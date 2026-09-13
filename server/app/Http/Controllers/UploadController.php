<?php

namespace App\Http\Controllers;

use App\Models\Skill;
use App\Models\SkillFile;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Str;

class UploadController extends Controller
{
    /**
     * GET /api/my/skills — 我上传的技能
     */
    public function index(Request $request): JsonResponse
    {
        $skills = Skill::where('handle', $request->user()->handle())
            ->withCount('files')
            ->orderByDesc('id')
            ->get();

        return response()->json(['skills' => $skills]);
    }

    /**
     * POST /api/skills — 上传新技能（multipart）
     *
     * 字段：name, slug?, description?, description_zh?, category?, version?
     * 文件：files[]（至少一个，文件名即技能内相对路径，必须包含 SKILL.md）
     */
    public function store(Request $request): JsonResponse
    {
        $user = $request->user();
        $data = $request->validate([
            'name' => 'required|string|max:128',
            'slug' => 'nullable|regex:/^[a-z0-9][a-z0-9-]*$/|max:64',
            'description' => 'nullable|string|max:5000',
            'description_zh' => 'nullable|string|max:5000',
            'category' => 'nullable|string|max:64',
            'category_name' => 'nullable|string|max:64',
            'version' => 'nullable|string|max:32',
            'files' => 'required|array|min:1|max:50',
            'files.*' => 'file|max:2048', // 单文件 ≤ 2MB
        ]);

        $slug = $data['slug'] ?? Str::slug($data['name']);
        if ($slug === '') {
            return response()->json(['error' => '无法从名称生成 slug，请显式填写'], 422);
        }
        if (Skill::where('handle', $user->handle())->where('slug', $slug)->exists()) {
            return response()->json(['error' => "你已上传过 slug 为 {$slug} 的技能"], 422);
        }

        $uploaded = $request->file('files');
        $paths = array_map(fn($f) => $f->getClientOriginalName(), $uploaded);
        foreach ($paths as $p) {
            if (!SkillFile::isSafeRelPath($p)) {
                return response()->json(['error' => "非法文件名：{$p}"], 422);
            }
        }
        if (!in_array('SKILL.md', $paths, true)) {
            return response()->json(['error' => '必须包含 SKILL.md 文件'], 422);
        }

        $skill = Skill::create([
            'handle' => $user->handle(),
            'slug' => $slug,
            'name' => $data['name'],
            'description' => $data['description'] ?? '',
            'description_zh' => $data['description_zh'] ?? '',
            'category' => $data['category'] ?? '',
            'category_name' => $data['category_name'] ?? '',
            'version' => $data['version'] ?? '1.0.0',
            'source' => 'user-upload',
            'keywords' => json_encode(['upload']),
            'synced_at' => time(),
        ]);

        $dir = $skill->diskDir() . '/files';
        foreach ($uploaded as $file) {
            $path = $file->getClientOriginalName();
            @mkdir(dirname($dir . '/' . $path), 0777, true);
            $file->move(dirname($dir . '/' . $path), basename($path));
            SkillFile::create([
                'skill_id' => $skill->id,
                'path' => $path,
                'sha256' => hash_file('sha256', $dir . '/' . $path),
                'size' => filesize($dir . '/' . $path) ?: 0,
            ]);
        }

        return response()->json(['skill' => $skill->load('files:id,skill_id,path,size')], 201);
    }

    /**
     * DELETE /api/my/skills/{id} — 删除自己上传的技能
     */
    public function destroy(Request $request, int $id): JsonResponse
    {
        $skill = Skill::where('handle', $request->user()->handle())->findOrFail($id);
        File::deleteDirectory($skill->diskDir());
        $skill->delete();

        return response()->json(['ok' => true]);
    }
}
