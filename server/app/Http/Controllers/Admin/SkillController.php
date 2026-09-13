<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Skill;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;

class SkillController extends Controller
{
    /**
     * GET /api/admin/skills?keyword=&category=&page=&pageSize=
     */
    public function index(Request $request): JsonResponse
    {
        $pageSize = min(100, max(1, (int)$request->query('pageSize', 20)));

        $query = Skill::query()->withCount('files');

        if ($kw = trim((string)$request->query('keyword', ''))) {
            $like = '%' . $kw . '%';
            $query->where(function ($q) use ($like) {
                $q->where('name', 'like', $like)
                  ->orWhere('slug', 'like', $like)
                  ->orWhere('handle', 'like', $like)
                  ->orWhere('description', 'like', $like)
                  ->orWhere('description_zh', 'like', $like);
            });
        }
        if ($cat = $request->query('category')) {
            $query->where('category', $cat);
        }

        $paginator = $query->orderByDesc('id')->paginate($pageSize);

        return response()->json([
            'skills' => $paginator->items(),
            'total' => $paginator->total(),
            'page' => $paginator->currentPage(),
            'pageSize' => $pageSize,
        ]);
    }

    /**
     * GET /api/admin/skills/{id}
     */
    public function show(int $id): JsonResponse
    {
        $skill = Skill::with('files:id,skill_id,path,size')->findOrFail($id);

        return response()->json(['skill' => $skill]);
    }

    /**
     * PUT /api/admin/skills/{id} — 编辑元数据
     */
    public function update(int $id, Request $request): JsonResponse
    {
        $skill = Skill::findOrFail($id);
        $data = $request->validate([
            'name' => 'sometimes|string|max:255',
            'description' => 'sometimes|nullable|string',
            'description_zh' => 'sometimes|nullable|string',
            'category' => 'sometimes|string|max:64',
            'category_name' => 'sometimes|string|max:64',
            'version' => 'sometimes|string|max:32',
            'icon_url' => 'sometimes|nullable|string|max:512',
            'source_url' => 'sometimes|nullable|string|max:512',
        ]);
        $skill->update($data);

        return response()->json(['skill' => $skill->fresh()]);
    }

    /**
     * DELETE /api/admin/skills/{id} — 删除记录并清理磁盘文件
     */
    public function destroy(int $id): JsonResponse
    {
        $skill = Skill::findOrFail($id);
        File::deleteDirectory($skill->diskDir());
        $skill->delete();

        return response()->json(['ok' => true]);
    }
}
