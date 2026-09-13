<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class SkillFile extends Model
{
    public $timestamps = false;

    protected $table = 'files';

    protected $fillable = ['skill_id', 'path', 'sha256', 'size'];

    protected $casts = ['size' => 'integer'];

    public function skill(): BelongsTo
    {
        return $this->belongsTo(Skill::class);
    }

    /** 相对路径安全校验：禁止绝对路径与 .. 穿越 */
    public static function isSafeRelPath(string $path): bool
    {
        return $path !== ''
            && !str_starts_with($path, '/')
            && !in_array('..', explode('/', $path), true);
    }
}
