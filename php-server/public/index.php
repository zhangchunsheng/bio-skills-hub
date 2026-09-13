<?php
// Single entry point: JSON API under /api/*, static frontend (dist/) otherwise.
// Dev:  php -S localhost:8000 php-server/public/index.php
// Prod: same — the router serves dist/ when it exists.
//
// NOTE: this code intentionally avoids bare `exit;` / `exit(0);` — the target
// PHP 8.3.6 (Ubuntu noble) build treats zero-status exit as a no-op and keeps
// executing. All routing is expressed as return values instead.

declare(strict_types=1);

require __DIR__ . '/../src/db.php';

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

/**
 * @return array{0: string, 1: int, 2: string} [body, status, content-type]
 */
function routeApi(string $uri, string $method, array $query): array
{
    $respond = fn(mixed $data, int $code = 200): array => [
        json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE),
        $code,
        'application/json; charset=utf-8',
    ];

    if ($method !== 'GET') {
        return $respond(['error' => '仅支持 GET'], 405);
    }

    // GET /api/skills?keyword=&category=&page=&pageSize=&sort=
    if ($uri === '/api/skills') {
        return $respond(searchSkills($query));
    }

    // GET /api/categories
    if ($uri === '/api/categories') {
        return $respond(['items' => getCategories()]);
    }

    // GET /api/stats
    if ($uri === '/api/stats') {
        return $respond(getStats());
    }

    // GET /api/skills/{handle}/{slug}
    if (preg_match('#^/api/skills/([^/]+)/([^/]+)$#', $uri, $m)) {
        $skill = getSkill(urldecode($m[1]), urldecode($m[2]));
        return $skill ? $respond(['skill' => $skill]) : $respond(['error' => '技能不存在'], 404);
    }

    // GET /api/skills/{handle}/{slug}/file?path=
    if (preg_match('#^/api/skills/([^/]+)/([^/]+)/file$#', $uri, $m)) {
        $path = $query['path'] ?? '';
        if (!isSafeRelPath($path)) return $respond(['error' => '非法路径'], 400);
        $skill = getSkill(urldecode($m[1]), urldecode($m[2]));
        if (!$skill) return $respond(['error' => '技能不存在'], 404);
        $file = skillDir($skill['handle'], $skill['slug']) . '/files/' . $path;
        if (!is_file($file)) return $respond(['error' => '文件不存在'], 404);
        return [file_get_contents($file), 200, 'text/plain; charset=utf-8'];
    }

    return $respond(['error' => '接口不存在'], 404);
}

if (str_starts_with($uri, '/api/')) {
    try {
        [$body, $code, $contentType] = routeApi($uri, $method, $_GET);
    } catch (Throwable $e) {
        $body = json_encode(['error' => $e->getMessage()], JSON_UNESCAPED_UNICODE);
        $code = 500;
        $contentType = 'application/json; charset=utf-8';
    }
    http_response_code($code);
    header('Content-Type: ' . $contentType);
    echo $body;
} else {
    // ---- Static files (production build) ----
    $dist = realpath(__DIR__ . '/../../dist');
    $served = false;
    if ($dist && $uri !== '/') {
        $file = realpath($dist . $uri);
        if ($file && str_starts_with($file, $dist) && is_file($file)) {
            $mimes = [
                'html' => 'text/html', 'js' => 'text/javascript', 'css' => 'text/css',
                'json' => 'application/json', 'png' => 'image/png', 'jpg' => 'image/jpeg',
                'svg' => 'image/svg+xml', 'ico' => 'image/x-icon', 'woff2' => 'font/woff2',
            ];
            header('Content-Type: ' . ($mimes[pathinfo($file, PATHINFO_EXTENSION)] ?? 'application/octet-stream'));
            readfile($file);
            $served = true;
        }
    }
    if (!$served && $dist && file_exists($dist . '/index.html')) {
        // SPA fallback
        header('Content-Type: text/html; charset=utf-8');
        readfile($dist . '/index.html');
        $served = true;
    }
    if (!$served) {
        http_response_code(404);
        header('Content-Type: text/plain; charset=utf-8');
        echo "前端尚未构建。开发模式请使用 npm run dev (Vite)，或先执行 npm run build。\n";
    }
}
