<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Skill;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;

class UserController extends Controller
{
    /**
     * GET /api/admin/users?keyword=&page=&pageSize=
     */
    public function index(Request $request): JsonResponse
    {
        $pageSize = min(100, max(1, (int)$request->query('pageSize', 20)));

        $query = User::query();

        if ($kw = trim((string)$request->query('keyword', ''))) {
            $like = '%' . $kw . '%';
            $query->where(function ($q) use ($like) {
                $q->where('name', 'like', $like)->orWhere('email', 'like', $like);
            });
        }
        if ($role = $request->query('role')) {
            $query->where('role', $role);
        }

        $paginator = $query->orderByDesc('id')->paginate($pageSize);

        // 每个用户的上传技能数（handle = u{id}）
        $users = collect($paginator->items());
        $counts = Skill::whereIn('handle', $users->map(fn ($u) => $u->handle()))
            ->selectRaw('handle, COUNT(*) as c')
            ->groupBy('handle')
            ->pluck('c', 'handle');
        $users->each(fn ($u) => $u->skills_count = (int)($counts[$u->handle()] ?? 0));

        return response()->json([
            'users' => $paginator->items(),
            'total' => $paginator->total(),
            'page' => $paginator->currentPage(),
            'pageSize' => $pageSize,
        ]);
    }

    /**
     * POST /api/admin/users — 创建用户（可指定角色）
     */
    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name' => 'required|string|max:64',
            'email' => 'required|email|max:255|unique:users,email',
            'password' => 'required|string|min:8',
            'role' => 'required|in:admin,user',
        ]);

        $user = User::create($data);

        return response()->json(['user' => $user], 201);
    }

    /**
     * PUT /api/admin/users/{id} — 编辑资料 / 角色 / 重置密码
     */
    public function update(Request $request, int $id): JsonResponse
    {
        $user = User::findOrFail($id);
        $data = $request->validate([
            'name' => 'sometimes|string|max:64',
            'email' => 'sometimes|email|max:255|unique:users,email,' . $user->id,
            'role' => 'sometimes|in:admin,user',
            'password' => 'sometimes|string|min:8',
        ]);

        // 防止把自己降级导致无人可管
        if (isset($data['role']) && $user->id === $request->user()->id && $data['role'] !== 'admin') {
            return response()->json(['error' => '不能取消自己的管理员角色'], 422);
        }

        $user->update($data);

        // 重置密码后吊销该用户全部令牌
        if (isset($data['password'])) {
            $user->tokens()->delete();
        }

        return response()->json(['user' => $user->fresh()]);
    }

    /**
     * DELETE /api/admin/users/{id} — 删除用户及其上传的技能（含磁盘文件）
     */
    public function destroy(Request $request, int $id): JsonResponse
    {
        $user = User::findOrFail($id);
        if ($user->id === $request->user()->id) {
            return response()->json(['error' => '不能删除当前登录的管理员账号'], 422);
        }

        // 清理该用户上传的技能
        $skills = Skill::where('handle', $user->handle())->get();
        foreach ($skills as $skill) {
            File::deleteDirectory($skill->diskDir());
            $skill->delete();
        }

        $user->tokens()->delete();
        $user->delete();

        return response()->json(['ok' => true, 'deleted_skills' => $skills->count()]);
    }
}
