<?php

return [
    /*
     * 技能文件在磁盘上的根目录（由 skills:sync 命令写入）。
     */
    'storage_path' => env('SKILLS_STORAGE', base_path('../data/skills')),

    /*
     * skillhub.cn 上游 API（仅同步时使用，运行时不访问外网）。
     */
    'upstream' => env('SKILLS_UPSTREAM', 'https://api.skillhub.cn'),

    /*
     * 同步时使用的生物分析相关检索关键词。
     */
    'sync_keywords' => [
        'bio', 'bioinformatics', 'genomics', 'protein', 'gene', 'dna', 'rna',
        'single-cell', 'sequencing', 'drug discovery', 'clinical', 'medical',
        'pharma', 'molecular', 'cell', 'cancer',
    ],
];
