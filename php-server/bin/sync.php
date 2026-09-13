<?php
// Fetch bio-analysis related skills from skillhub.cn into the local SQLite
// database and data/skills/ directory. Run once (or to refresh):
//
//   php php-server/bin/sync.php                # incremental (skip unchanged files)
//   php php-server/bin/sync.php --refresh      # re-download everything
//   php php-server/bin/sync.php --max-pages=1  # limit pages per keyword (testing)
//
// Requires: PHP curl + pdo_sqlite extensions.

declare(strict_types=1);

require __DIR__ . '/../src/db.php';

const API_BASE = 'https://api.skillhub.cn';
const UA = 'bio-skills-hub-sync/1.0';
const CONCURRENCY = 10;

// Search keywords used to harvest bio-related skills from the community.
const KEYWORDS = [
    'bio', 'bioinformatics', 'genomics', 'protein', 'gene', 'dna', 'rna',
    'single-cell', 'sequencing', 'drug discovery', 'clinical', 'medical',
    'pharma', 'molecular', 'cell', 'cancer',
];

$opts = getopt('', ['refresh', 'max-pages:', 'help']);
if (isset($opts['help'])) {
    echo "Usage: php php-server/bin/sync.php [--refresh] [--max-pages=N]\n";
    return; // 顶层 return，正常结束（本机 PHP 构建对 exit(0) 有 bug，避免使用）
}
$refresh = isset($opts['refresh']);
$maxPages = max(1, (int)($opts['max-pages'] ?? 5));

if (!extension_loaded('curl')) {
    fwrite(STDERR, "需要 PHP curl 扩展\n");
    exit(1); // exit(非零) 正常；勿用 exit(0)，见 index.php 注释
}

function httpGet(string $url): string
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_USERAGENT => UA,
    ]);
    $body = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    if ($body === false || $code >= 400) {
        throw new RuntimeException("HTTP $code for $url");
    }
    return $body;
}

function getJson(string $url): array
{
    return json_decode(httpGet($url), true, 512, JSON_THROW_ON_ERROR);
}

/**
 * Download many URLs concurrently. $jobs: [id => url].
 * Returns [id => string body] (only successful ones).
 */
function httpGetMulti(array $jobs): array
{
    $results = [];
    $queue = $jobs;
    $mh = curl_multi_init();
    $active = [];

    $start = function (string $id, string $url) use ($mh, &$active) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_TIMEOUT => 60,
            CURLOPT_USERAGENT => UA,
        ]);
        curl_multi_add_handle($mh, $ch);
        $active[(int)$ch] = [$id, $ch];
    };

    foreach (array_slice($queue, 0, CONCURRENCY, true) as $id => $url) {
        $start($id, $url);
    }
    $queue = array_slice($queue, CONCURRENCY, null, true);

    do {
        curl_multi_exec($mh, $running);
        curl_multi_select($mh);
        while ($info = curl_multi_info_read($mh)) {
            $ch = $info['handle'];
            [$id, ] = $active[(int)$ch];
            unset($active[(int)$ch]);
            $code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
            $body = curl_multi_getcontent($ch);
            if ($info['result'] === CURLE_OK && $code < 400 && $body !== false) {
                $results[$id] = $body;
            }
            curl_multi_remove_handle($mh, $ch);
            curl_close($ch);
            if ($queue) {
                $nextId = array_key_first($queue);
                $start($nextId, $queue[$nextId]);
                unset($queue[$nextId]);
            }
        }
    } while ($running || $active);

    curl_multi_close($mh);
    return $results;
}

// ---------------------------------------------------------------------------

echo "== 初始化数据库\n";
@mkdir(dirname(DB_PATH), 0777, true);
@mkdir(SKILLS_DIR, 0777, true);
$pdo = new PDO('sqlite:' . DB_PATH);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
initSchema($pdo);

// Category key -> Chinese name map
$catNames = [];
try {
    foreach (getJson(API_BASE . '/api/v1/categories')['items'] ?? [] as $c) {
        $catNames[$c['key']] = $c['name'];
    }
} catch (Throwable $e) {
    echo "警告：获取分类失败（{$e->getMessage()}），继续\n";
}

echo "== 检索技能列表（" . count(KEYWORDS) . " 个关键词）\n";
$found = []; // "handle/slug" => skill row
foreach (KEYWORDS as $kw) {
    for ($page = 1; $page <= $maxPages; $page++) {
        $url = API_BASE . '/api/skills?' . http_build_query([
            'page' => $page, 'pageSize' => 100, 'keyword' => $kw,
        ]);
        try {
            $data = getJson($url)['data'] ?? [];
        } catch (Throwable $e) {
            echo "  [$kw] 第 $page 页失败：{$e->getMessage()}\n";
            break;
        }
        $skills = $data['skills'] ?? [];
        if (!$skills) break;
        foreach ($skills as $s) {
            $handle = $s['namespace']['handle'] ?? $s['ownerName'] ?? '_';
            $key = "$handle/{$s['slug']}";
            if (isset($found[$key])) {
                // record which keywords matched
                if (!in_array($kw, $found[$key]['_kw'], true)) $found[$key]['_kw'][] = $kw;
                continue;
            }
            $s['_handle'] = $handle;
            $s['_kw'] = [$kw];
            $found[$key] = $s;
        }
        $total = $data['total'] ?? 0;
        echo "  [$kw] 第 $page 页：" . count($skills) . " 条（该词共 $total 条）\n";
        if ($page * 100 >= $total) break;
    }
}
echo "== 去重后共 " . count($found) . " 个技能\n";

// Upsert metadata
$upsert = $pdo->prepare(
    'INSERT INTO skills (handle, slug, name, description, description_zh, category, category_name,
                         version, icon_url, source, source_url, downloads, stars, installs, keywords, synced_at)
     VALUES (:handle, :slug, :name, :description, :description_zh, :category, :category_name,
             :version, :icon_url, :source, :source_url, :downloads, :stars, :installs, :keywords, :synced_at)
     ON CONFLICT(handle, slug) DO UPDATE SET
        name=excluded.name, description=excluded.description, description_zh=excluded.description_zh,
        category=excluded.category, category_name=excluded.category_name, version=excluded.version,
        icon_url=excluded.icon_url, source=excluded.source, source_url=excluded.source_url,
        downloads=excluded.downloads, stars=excluded.stars, installs=excluded.installs,
        keywords=excluded.keywords, synced_at=excluded.synced_at'
);

$now = time();
foreach (array_values($found) as $i => $s) {
    $upsert->execute([
        ':handle' => $s['_handle'],
        ':slug' => $s['slug'],
        ':name' => $s['name'] ?? $s['slug'],
        ':description' => $s['description'] ?? '',
        ':description_zh' => $s['description_zh'] ?? '',
        ':category' => $s['category'] ?? '',
        ':category_name' => $catNames[$s['category'] ?? ''] ?? '',
        ':version' => $s['version'] ?? '',
        ':icon_url' => $s['iconUrl'] ?? '',
        ':source' => $s['source'] ?? '',
        ':source_url' => $s['upstream_url'] ?? '',
        ':downloads' => (int)($s['downloads'] ?? 0),
        ':stars' => (int)($s['stars'] ?? 0),
        ':installs' => (int)($s['installs'] ?? 0),
        ':keywords' => json_encode($s['_kw'], JSON_UNESCAPED_UNICODE),
        ':synced_at' => $now,
    ]);
    if (($i + 1) % 200 === 0) echo "  元数据 {$i}/" . count($found) . "\n";
}

// Map handle/slug -> id
$idMap = [];
foreach ($pdo->query('SELECT id, handle, slug FROM skills') as $row) {
    $idMap["{$row['handle']}/{$row['slug']}"] = (int)$row['id'];
}

// ---------------------------------------------------------------------------
echo "== 获取文件清单\n";
$fileListJobs = [];
foreach ($found as $key => $s) {
    $fileListJobs[$key] = API_BASE . '/api/v1/skills/' . rawurlencode($s['slug'])
        . '/files?namespace=' . rawurlencode($s['_handle']);
}

$allFiles = []; // skillKey => [ [path, sha256, size], ... ]
$done = 0;
foreach (array_chunk($fileListJobs, 200, true) as $chunk) {
    foreach (httpGetMulti($chunk) as $key => $body) {
        $data = json_decode($body, true);
        $files = $data['files'] ?? [];
        $allFiles[$key] = array_values(array_filter($files, fn($f) => isSafeRelPath($f['path'] ?? '')));
    }
    $done += count($chunk);
    echo "  文件清单 $done/" . count($fileListJobs) . "\n";
}

// Existing file hashes (to skip unchanged files)
$existing = [];
foreach ($pdo->query('SELECT skill_id, path, sha256 FROM files') as $row) {
    $existing[$row['skill_id'] . ':' . $row['path']] = $row['sha256'];
}

$insFile = $pdo->prepare(
    'INSERT INTO files (skill_id, path, sha256, size) VALUES (?, ?, ?, ?)
     ON CONFLICT(skill_id, path) DO UPDATE SET sha256=excluded.sha256, size=excluded.size'
);

// ---------------------------------------------------------------------------
echo "== 下载文件内容\n";
$downloadJobs = []; // "skillKey|path" => url
foreach ($allFiles as $key => $files) {
    $skillId = $idMap[$key] ?? null;
    if (!$skillId) continue;
    [$handle, $slug] = explode('/', $key, 2);
    foreach ($files as $f) {
        if (!$refresh && ($existing[$skillId . ':' . $f['path']] ?? null) === ($f['sha256'] ?? '')) {
            $dir = skillDir($handle, $slug) . '/files/' . $f['path'];
            if (is_file($dir)) continue; // already downloaded & unchanged
        }
        $downloadJobs[$key . '|' . $f['path']] =
            API_BASE . '/api/v1/skills/' . rawurlencode($slug) . '/file?' . http_build_query([
                'path' => $f['path'], 'namespace' => $handle,
            ]);
    }
}
echo "  需要下载 " . count($downloadJobs) . " 个文件\n";

$done = 0;
$failed = 0;
foreach (array_chunk($downloadJobs, 200, true) as $chunk) {
    $bodies = httpGetMulti($chunk);
    foreach ($chunk as $jobKey => $url) {
        [$key, $path] = explode('|', $jobKey, 2);
        [$handle, $slug] = explode('/', $key, 2);
        if (!isset($bodies[$jobKey])) {
            $failed++;
            continue;
        }
        $dest = skillDir($handle, $slug) . '/files/' . $path;
        @mkdir(dirname($dest), 0777, true);
        file_put_contents($dest, $bodies[$jobKey]);
    }
    $done += count($chunk);
    echo "  文件 $done/" . count($downloadJobs) . "（失败 {$failed}）\n";
}

// Persist file records
foreach ($allFiles as $key => $files) {
    $skillId = $idMap[$key] ?? null;
    if (!$skillId) continue;
    [$handle, $slug] = explode('/', $key, 2);
    $valid = [];
    foreach ($files as $f) {
        $local = skillDir($handle, $slug) . '/files/' . $f['path'];
        if (is_file($local)) {
            $insFile->execute([$skillId, $f['path'], $f['sha256'] ?? '', (int)($f['size'] ?? 0)]);
            $valid[] = $f['path'];
        }
    }
    // drop DB records for files that no longer exist upstream
    $stmt = $pdo->prepare('SELECT id, path FROM files WHERE skill_id = ?');
    $stmt->execute([$skillId]);
    foreach ($stmt->fetchAll() as $row) {
        if (!in_array($row['path'], $valid, true)) {
            $pdo->prepare('DELETE FROM files WHERE id = ?')->execute([$row['id']]);
        }
    }
}

// Remove skills that were previously synced but no longer matched (only on full run)
$del = $pdo->prepare('DELETE FROM skills WHERE id = ?');
$removed = 0;
foreach ($idMap as $key => $id) {
    if (!isset($found[$key])) {
        $del->execute([$id]);
        $removed++;
    }
}
if ($removed) echo "== 移除已不再匹配的 $removed 个技能（文件保留在磁盘）\n";

$pdo->prepare('INSERT INTO meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value')
    ->execute(['last_sync', (string)$now]);
$pdo->prepare('INSERT INTO meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value')
    ->execute(['keywords', json_encode(KEYWORDS, JSON_UNESCAPED_UNICODE)]);

$stats = getStats();
echo "== 完成：{$stats['skills']} 个技能，{$stats['files']} 个文件\n";
