<?php

use App\Http\Controllers\SeoController;
use Illuminate\Support\Facades\Route;

/*
 * SEO 路由 + SPA 静态托管：public/ 下由 deploy 脚本拷入构建产物
 *   public/          ← web/dist（用户端）
 *   public/admin/    ← admin/dist（管理端，vite base=/admin/）
 * Laravel 自动提供 public/ 内真实存在的文件；fallback 负责 SPA 回退并注入 meta。
 */

Route::get('/sitemap.xml', [SeoController::class, 'sitemap']);
Route::get('/robots.txt', [SeoController::class, 'robots']);

Route::fallback([SeoController::class, 'spa']);
