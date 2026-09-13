<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Process;

class SyncController extends Controller
{
    private function statusFile(): string
    {
        return storage_path('app/sync-status.json');
    }

    /**
     * GET /api/admin/sync-status — 最近同步状态与日志尾部
     */
    public function status(): JsonResponse
    {
        $status = is_file($this->statusFile())
            ? json_decode(file_get_contents($this->statusFile()), true)
            : ['running' => false];

        $meta = DB::table('meta')->pluck('value', 'key');
        $status['last_sync'] = isset($meta['last_sync']) ? (int)$meta['last_sync'] : null;

        return response()->json($status);
    }

    /**
     * POST /api/admin/sync — 后台触发同步（skills:sync）
     */
    public function start(Request $request): JsonResponse
    {
        $status = is_file($this->statusFile())
            ? json_decode(file_get_contents($this->statusFile()), true)
            : [];
        if (!empty($status['running'])) {
            return response()->json(['error' => '同步正在进行中'], 409);
        }

        $args = [];
        if ($request->boolean('refresh')) $args[] = '--refresh';
        if ($pages = $request->input('max_pages')) $args[] = '--max-pages=' . (int)$pages;

        $log = storage_path('logs/sync.log');
        $cmd = array_merge([PHP_BINARY, base_path('artisan'), 'skills:sync'], $args);
        Process::start(implode(' ', array_map('escapeshellarg', $cmd)) . ' >> ' . escapeshellarg($log) . ' 2>&1 &');

        file_put_contents($this->statusFile(), json_encode([
            'running' => true,
            'started_at' => time(),
            'args' => $args,
        ]));

        return response()->json(['ok' => true]);
    }
}
