<?php

namespace App\Http\Controllers;

use App\Models\Skill;
use App\Models\SkillFile;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class SkillController extends Controller
{
    /**
     * GET /api/skills?keyword=&category=&page=&pageSize=&sort=
     */
    public function index(Request $request): JsonResponse
    {
        $pageSize = min(100, max(1, (int)$request->query('pageSize', 24)));

        $query = Skill::query()
            ->select(['id', 'handle', 'slug', 'name', 'description', 'description_zh',
                      'category', 'category_name', 'version', 'icon_url', 'source',
                      'downloads', 'stars', 'installs', 'synced_at']);

        if ($kw = trim((string)$request->query('keyword', ''))) {
            $like = '%' . $kw . '%';
            $query->where(function ($q) use ($like) {
                $q->where('name', 'like', $like)
                  ->orWhere('description', 'like', $like)
                  ->orWhere('description_zh', 'like', $like)
                  ->orWhere('slug', 'like', $like);
            });
        }
        if ($cat = $request->query('category')) {
            $query->where('category', $cat);
        }

        match ($request->query('sort')) {
            'downloads' => $query->orderByDesc('downloads'),
            'stars' => $query->orderByDesc('stars'),
            'installs' => $query->orderByDesc('installs'),
            'newest' => $query->orderByDesc('synced_at'),
            default => $query->orderByRaw('(downloads * 2 + stars * 10 + installs) DESC'),
        };

        $paginator = $query->paginate($pageSize);

        return response()->json([
            'skills' => $paginator->items(),
            'total' => $paginator->total(),
            'page' => $paginator->currentPage(),
            'pageSize' => $pageSize,
        ]);
    }

    /**
     * GET /api/skills/{handle}/{slug}
     */
    public function show(string $handle, string $slug): JsonResponse
    {
        $skill = Skill::where('handle', $handle)->where('slug', $slug)->first();
        if (!$skill) {
            return response()->json(['error' => '技能不存在'], 404);
        }
        $skill->files = $skill->files()->orderBy('path')->get(['path', 'sha256', 'size']);

        return response()->json(['skill' => $skill]);
    }

    /**
     * GET /api/skills/{handle}/{slug}/file?path=
     */
    public function file(string $handle, string $slug, Request $request)
    {
        $path = (string)$request->query('path', '');
        if (!SkillFile::isSafeRelPath($path)) {
            return response()->json(['error' => '非法路径'], 400);
        }
        $skill = Skill::where('handle', $handle)->where('slug', $slug)->first();
        if (!$skill) {
            return response()->json(['error' => '技能不存在'], 404);
        }
        $file = $skill->diskDir() . '/files/' . $path;
        if (!is_file($file)) {
            return response()->json(['error' => '文件不存在'], 404);
        }

        return response(file_get_contents($file), 200, ['Content-Type' => 'text/plain; charset=utf-8']);
    }

    /**
     * GET /api/categories — 本地库中实际存在的分类
     */
    public function categories(): JsonResponse
    {
        $items = Skill::query()
            ->select('category as key', 'category_name as name', DB::raw('COUNT(*) as count'))
            ->where('category', '!=', '')
            ->groupBy('category', 'category_name')
            ->orderByDesc('count')
            ->get();

        return response()->json(['items' => $items]);
    }

    /**
     * GET /api/stats
     */
    public function stats(): JsonResponse
    {
        $meta = DB::table('meta')->pluck('value', 'key');

        return response()->json([
            'skills' => Skill::count(),
            'files' => SkillFile::count(),
            'categories' => Skill::where('category', '!=', '')->distinct()->count('category'),
            'lastSync' => isset($meta['last_sync']) ? (int)$meta['last_sync'] : null,
            'keywords' => isset($meta['keywords']) ? json_decode($meta['keywords'], true) : [],
        ]);
    }
}
