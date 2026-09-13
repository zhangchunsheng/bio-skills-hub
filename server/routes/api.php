<?php

use App\Http\Controllers\Admin\SkillController as AdminSkillController;
use App\Http\Controllers\Admin\SyncController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\SkillController;
use App\Http\Controllers\UploadController;
use Illuminate\Support\Facades\Route;

// ---- 认证 ----
Route::post('/auth/register', [AuthController::class, 'register']);
Route::post('/auth/login', [AuthController::class, 'login']);

Route::middleware('auth:sanctum')->group(function () {
    Route::post('/auth/logout', [AuthController::class, 'logout']);
    Route::get('/auth/me', [AuthController::class, 'me']);
    Route::post('/auth/password', [AuthController::class, 'changePassword']);

    // 用户上传技能
    Route::post('/skills', [UploadController::class, 'store']);
    Route::get('/my/skills', [UploadController::class, 'index']);
    Route::delete('/my/skills/{id}', [UploadController::class, 'destroy'])->whereNumber('id');
});

// ---- 公开 API（用户端） ----
Route::get('/skills', [SkillController::class, 'index']);
Route::get('/categories', [SkillController::class, 'categories']);
Route::get('/stats', [SkillController::class, 'stats']);
Route::get('/skills/{handle}/{slug}', [SkillController::class, 'show']);
Route::get('/skills/{handle}/{slug}/file', [SkillController::class, 'file']);

// ---- 管理端 API（需管理员） ----
Route::prefix('admin')->middleware(['auth:sanctum', 'admin'])->group(function () {
    Route::get('/skills', [AdminSkillController::class, 'index']);
    Route::get('/skills/{id}', [AdminSkillController::class, 'show'])->whereNumber('id');
    Route::put('/skills/{id}', [AdminSkillController::class, 'update'])->whereNumber('id');
    Route::delete('/skills/{id}', [AdminSkillController::class, 'destroy'])->whereNumber('id');
    Route::get('/sync-status', [SyncController::class, 'status']);
    Route::post('/sync', [SyncController::class, 'start']);
});
