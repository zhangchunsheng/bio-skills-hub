<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * 技能库表结构。兼容已有数据：若表已由旧版 sync 工具创建则跳过。
 */
return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable('skills')) {
            Schema::create('skills', function (Blueprint $table) {
                $table->id();
                $table->string('handle');
                $table->string('slug');
                $table->string('name')->default('');
                $table->text('description')->nullable();
                $table->text('description_zh')->nullable();
                $table->string('category')->default('');
                $table->string('category_name')->default('');
                $table->string('version')->default('');
                $table->string('icon_url')->default('');
                $table->string('source')->default('');
                $table->string('source_url')->default('');
                $table->unsignedInteger('downloads')->default(0);
                $table->unsignedInteger('stars')->default(0);
                $table->unsignedInteger('installs')->default(0);
                $table->string('keywords')->default(''); // 命中同步关键词 JSON
                $table->unsignedBigInteger('synced_at')->default(0);
                $table->unique(['handle', 'slug']);
                $table->index('category');
                $table->index('downloads');
            });
        }

        if (!Schema::hasTable('files')) {
            Schema::create('files', function (Blueprint $table) {
                $table->id();
                $table->foreignId('skill_id')->constrained('skills')->cascadeOnDelete();
                $table->string('path');
                $table->string('sha256')->default('');
                $table->unsignedBigInteger('size')->default(0);
                $table->unique(['skill_id', 'path']);
            });
        }

        if (!Schema::hasTable('meta')) {
            Schema::create('meta', function (Blueprint $table) {
                $table->string('key')->primary();
                $table->text('value')->nullable();
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('files');
        Schema::dropIfExists('skills');
        Schema::dropIfExists('meta');
    }
};
