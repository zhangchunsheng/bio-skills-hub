<?php

use App\Http\Controllers\Admin\SkillController as AdminSkillController;
use App\Http\Controllers\Admin\SyncController;
use App\Http\Controllers\SkillController;
use Illuminate\Support\Facades\Route;

// ---- 公开 API（用户端） ----
Route::get('/skills', [SkillController::class, 'index']);
Route::get('/categories', [SkillController::class, 'categories']);
Route::get('/stats', [SkillController::class, 'stats']);
Route::get('/skills/{handle}/{slug}', [SkillController::class, 'show']);
Route::get('/skills/{handle}/{slug}/file', [SkillController::class, 'file']);

// ---- 管理端 API ----
Route::prefix('admin')->group(function () {
    Route::get('/skills', [AdminSkillController::class, 'index']);
    Route::get('/skills/{id}', [AdminSkillController::class, 'show'])->whereNumber('id');
    Route::put('/skills/{id}', [AdminSkillController::class, 'update'])->whereNumber('id');
    Route::delete('/skills/{id}', [AdminSkillController::class, 'destroy'])->whereNumber('id');
    Route::get('/sync-status', [SyncController::class, 'status']);
    Route::post('/sync', [SyncController::class, 'start']);
});
