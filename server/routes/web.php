<?php

use Illuminate\Support\Facades\Route;

/*
 * 生产模式静态托管：public/ 下由 deploy 脚本拷入构建产物
 *   public/          ← web/dist（用户端）
 *   public/admin/    ← admin/dist（管理端，vite base=/admin/）
 * Laravel 会自动提供 public/ 内真实存在的文件；以下路由仅做 SPA 回退。
 */

Route::fallback(function () {
    $path = request()->path();

    if (str_starts_with($path, 'admin')) {
        $index = public_path('admin/index.html');
        if (is_file($index)) {
            return response()->file($index, ['Content-Type' => 'text/html; charset=utf-8']);
        }
    }

    $index = public_path('index.html');
    if (is_file($index)) {
        return response()->file($index, ['Content-Type' => 'text/html; charset=utf-8']);
    }

    return response('前端尚未部署：请先构建 web/ 与 admin/ 并执行 deploy/deploy.sh', 404);
});
