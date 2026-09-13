<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Skill extends Model
{
    public $timestamps = false;

    protected $fillable = [
        'handle', 'slug', 'name', 'description', 'description_zh',
        'category', 'category_name', 'version', 'icon_url',
        'source', 'source_url', 'downloads', 'stars', 'installs',
        'keywords', 'synced_at',
    ];

    protected $casts = [
        'downloads' => 'integer',
        'stars' => 'integer',
        'installs' => 'integer',
        'synced_at' => 'integer',
    ];

    public function files(): HasMany
    {
        return $this->hasMany(SkillFile::class);
    }

    /** 技能文件在磁盘上的目录：data/skills/<handle>__<slug> */
    public function diskDir(): string
    {
        $key = preg_replace('/[^\w@.-]/', '_', ($this->handle ?: '_') . '__' . $this->slug);

        return self::storageRoot() . '/' . $key;
    }

    public static function storageRoot(): string
    {
        return rtrim(config('skills.storage_path'), '/');
    }
}
