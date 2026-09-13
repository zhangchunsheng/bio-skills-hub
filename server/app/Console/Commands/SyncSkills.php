<?php

namespace App\Console\Commands;

use App\Models\Skill;
use App\Models\SkillFile;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

/**
 * 从 skillhub.cn 抓取生物分析相关技能到本地 SQLite + 磁盘。
 * 部署后运行时不访问外网；此命令仅在需要更新技能库时手动/后台执行。
 */
class SyncSkills extends Command
{
    protected $signature = 'skills:sync {--refresh : 全量重下所有文件} {--max-pages=5 : 每个关键词最多抓取的页数}';

    protected $description = '从 skillhub.cn 同步生物分析相关技能到本地';

    private string $base;
    private bool $refresh;
    private string $logFile;

    public function handle(): int
    {
        $this->base = rtrim(config('skills.upstream'), '/');
        $this->refresh = (bool)$this->option('refresh');
        $maxPages = max(1, (int)$this->option('max-pages'));
        $this->logFile = storage_path('logs/sync.log');
        @mkdir(dirname($this->logFile), 0777, true);
        @mkdir(Skill::storageRoot(), 0777, true);

        $this->markStatus(['running' => true, 'started_at' => time()]);

        try {
            $this->runSync($maxPages);
            $this->markStatus([
                'running' => false,
                'finished_at' => time(),
                'skills' => Skill::count(),
                'files' => SkillFile::count(),
            ]);
        } catch (\Throwable $e) {
            $this->log('ERROR: ' . $e->getMessage());
            $this->markStatus(['running' => false, 'finished_at' => time(), 'error' => $e->getMessage()]);
            return self::FAILURE;
        }

        return self::SUCCESS;
    }

    private function runSync(int $maxPages): void
    {
        $keywords = config('skills.sync_keywords');
        $now = time();

        // 分类 key → 中文名
        $catNames = [];
        try {
            foreach (Http::timeout(20)->get($this->base . '/api/v1/categories')->json('items') ?? [] as $c) {
                $catNames[$c['key']] = $c['name'];
            }
        } catch (\Throwable $e) {
            $this->log('警告：获取分类失败：' . $e->getMessage());
        }

        // ---- 检索技能列表 ----
        $this->log('== 检索技能列表（' . count($keywords) . ' 个关键词）');
        $found = []; // "handle/slug" => row
        foreach ($keywords as $kw) {
            for ($page = 1; $page <= $maxPages; $page++) {
                try {
                    $resp = Http::timeout(20)->get($this->base . '/api/skills', [
                        'page' => $page, 'pageSize' => 100, 'keyword' => $kw,
                    ])->throw()->json();
                } catch (\Throwable $e) {
                    $this->log("  [$kw] 第 $page 页失败：" . $e->getMessage());
                    break;
                }
                $data = $resp['data'] ?? [];
                $skills = $data['skills'] ?? [];
                if (!$skills) break;
                foreach ($skills as $s) {
                    $handle = $s['namespace']['handle'] ?? $s['ownerName'] ?? '_';
                    $key = "$handle/{$s['slug']}";
                    if (isset($found[$key])) {
                        if (!in_array($kw, $found[$key]['_kw'], true)) $found[$key]['_kw'][] = $kw;
                        continue;
                    }
                    $s['_handle'] = $handle;
                    $s['_kw'] = [$kw];
                    $found[$key] = $s;
                }
                $total = $data['total'] ?? 0;
                $this->log("  [$kw] 第 $page 页：" . count($skills) . " 条（共 $total 条）");
                if ($page * 100 >= $total) break;
            }
        }
        $this->log('== 去重后共 ' . count($found) . ' 个技能');

        // ---- 写入元数据 ----
        foreach (array_values($found) as $i => $s) {
            Skill::updateOrCreate(
                ['handle' => $s['_handle'], 'slug' => $s['slug']],
                [
                    'name' => $s['name'] ?? $s['slug'],
                    'description' => $s['description'] ?? '',
                    'description_zh' => $s['description_zh'] ?? '',
                    'category' => $s['category'] ?? '',
                    'category_name' => $catNames[$s['category'] ?? ''] ?? '',
                    'version' => $s['version'] ?? '',
                    'icon_url' => $s['iconUrl'] ?? '',
                    'source' => $s['source'] ?? '',
                    'source_url' => $s['upstream_url'] ?? '',
                    'downloads' => (int)($s['downloads'] ?? 0),
                    'stars' => (int)($s['stars'] ?? 0),
                    'installs' => (int)($s['installs'] ?? 0),
                    'keywords' => json_encode($s['_kw'], JSON_UNESCAPED_UNICODE),
                    'synced_at' => $now,
                ]
            );
            if (($i + 1) % 300 === 0) $this->log("  元数据 " . ($i + 1) . '/' . count($found));
        }

        $idMap = Skill::pluck('id', DB::raw("handle || '/' || slug"))->all();

        // ---- 文件清单 ----
        $this->log('== 获取文件清单');
        $allFiles = [];
        $keys = array_keys($found);
        foreach (array_chunk($keys, 20) as $chunk) {
            $responses = Http::pool(fn($pool) => array_map(
                fn($key) => $pool->as($key)->timeout(30)->get(
                    $this->base . '/api/v1/skills/' . rawurlencode($found[$key]['slug']) . '/files',
                    ['namespace' => $found[$key]['_handle']]
                ),
                $chunk
            ));
            foreach ($responses as $key => $resp) {
                if ($resp->ok()) {
                    $files = array_filter($resp->json('files') ?? [], fn($f) => SkillFile::isSafeRelPath($f['path'] ?? ''));
                    $allFiles[$key] = array_values($files);
                }
            }
            $this->log('  文件清单 ' . count($allFiles) . '/' . count($keys));
        }

        // ---- 已有文件哈希（跳过未变更） ----
        $existing = SkillFile::select('skill_id', 'path', 'sha256')->get()
            ->mapWithKeys(fn($f) => [$f->skill_id . ':' . $f->path => $f->sha256])->all();

        // ---- 下载文件内容 ----
        $jobs = []; // "skillKey|path" => [url, dest, skillId, path]
        foreach ($allFiles as $key => $files) {
            $skillId = $idMap[$key] ?? null;
            if (!$skillId) continue;
            $skill = $found[$key];
            $dir = Skill::storageRoot() . '/' . preg_replace('/[^\w@.-]/', '_', ($skill['_handle'] ?: '_') . '__' . $skill['slug']);
            foreach ($files as $f) {
                $dest = $dir . '/files/' . $f['path'];
                if (!$this->refresh
                    && ($existing[$skillId . ':' . $f['path']] ?? null) === ($f['sha256'] ?? '')
                    && is_file($dest)) {
                    continue;
                }
                $jobs[$key . '|' . $f['path']] = [
                    'url' => $this->base . '/api/v1/skills/' . rawurlencode($skill['slug']) . '/file?'
                        . http_build_query(['path' => $f['path'], 'namespace' => $skill['_handle']]),
                    'dest' => $dest,
                    'skill_id' => $skillId,
                    'path' => $f['path'],
                    'sha256' => $f['sha256'] ?? '',
                    'size' => (int)($f['size'] ?? 0),
                ];
            }
        }
        $this->log('== 需要下载 ' . count($jobs) . ' 个文件');

        $done = 0;
        $failed = 0;
        foreach (array_chunk($jobs, 20, true) as $chunk) {
            $responses = Http::pool(fn($pool) => array_map(
                fn($job) => $pool->timeout(60)->get($job['url']),
                $chunk
            ));
            foreach (array_values($chunk) as $i => $job) {
                $resp = array_values($responses)[$i];
                if ($resp->ok()) {
                    @mkdir(dirname($job['dest']), 0777, true);
                    file_put_contents($job['dest'], $resp->body());
                    SkillFile::updateOrCreate(
                        ['skill_id' => $job['skill_id'], 'path' => $job['path']],
                        ['sha256' => $job['sha256'], 'size' => $job['size']]
                    );
                } else {
                    $failed++;
                }
            }
            $done += count($chunk);
            $this->log("  文件 $done/" . count($jobs) . "（失败 {$failed}）");
        }

        // ---- 移除已不在上游文件清单中的 DB 记录 ----
        foreach ($allFiles as $key => $files) {
            $skillId = $idMap[$key] ?? null;
            if (!$skillId) continue;
            $valid = array_column($files, 'path');
            SkillFile::where('skill_id', $skillId)->whereNotIn('path', $valid)->delete();
        }

        DB::table('meta')->updateOrInsert(['key' => 'last_sync'], ['value' => (string)$now]);
        DB::table('meta')->updateOrInsert(['key' => 'keywords'], ['value' => json_encode($keywords, JSON_UNESCAPED_UNICODE)]);

        $this->log('== 完成：' . Skill::count() . ' 个技能，' . SkillFile::count() . ' 个文件');
    }

    private function log(string $message): void
    {
        $line = '[' . date('H:i:s') . '] ' . $message;
        $this->line($line);
        file_put_contents($this->logFile, $line . "\n", FILE_APPEND);
    }

    private function markStatus(array $status): void
    {
        file_put_contents(storage_path('app/sync-status.json'), json_encode($status, JSON_UNESCAPED_UNICODE));
    }
}
