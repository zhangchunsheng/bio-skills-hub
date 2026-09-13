<?php

namespace App\Http\Controllers;

use App\Models\Skill;
use Illuminate\Http\Request;
use Illuminate\Http\Response;

/**
 * SEO：为爬虫在服务端注入页面 meta（title/description/OG/JSON-LD），
 * 并提供 sitemap.xml 与 robots.txt。SPA 本身的交互不受影响。
 */
class SeoController extends Controller
{
    private const SITE_NAME = 'Bio Skills Hub';
    private const SITE_DESC = '面向生物分析的 AI Agent Skills 离线库：收录基因组学、蛋白质、单细胞测序、药物研发、临床医疗等方向的生物信息技能，支持在线预览与本地下载。';
    private const SITE_KEYWORDS = '生物信息,生物分析,生信技能,genomics,bioinformatics,AI skills,Agent Skills,单细胞测序,蛋白质,药物研发,Claude skills';

    /**
     * SPA 入口（fallback 路由调用）：按路径注入对应 meta 后返回 index.html。
     */
    public function spa(Request $request)
    {
        $path = $request->path();

        // 管理端：禁止索引
        if (str_starts_with($path, 'admin')) {
            $index = public_path('admin/index.html');
            if (is_file($index)) {
                return response($this->inject(file_get_contents($index), [
                    'title' => '管理后台 - ' . self::SITE_NAME,
                    'extra' => '<meta name="robots" content="noindex,nofollow">',
                ]))->header('Content-Type', 'text/html; charset=utf-8');
            }
            return response('管理端尚未部署', 404);
        }

        $index = public_path('index.html');
        if (!is_file($index)) {
            return response('前端尚未部署：请先构建 web/ 并执行 deploy/deploy.sh', 404);
        }
        $html = file_get_contents($index);

        // 技能详情页：用技能信息生成 meta
        if (preg_match('#^skill/([^/]+)/([^/]+)$#', $path, $m)) {
            $skill = Skill::where('handle', urldecode($m[1]))->where('slug', urldecode($m[2]))->first();
            if ($skill) {
                return $this->skillPage($request, $html, $skill);
            }
        }

        // 首页/其它页面：站点级 meta
        return response($this->inject($html, $this->siteMeta($request)))
            ->header('Content-Type', 'text/html; charset=utf-8');
    }

    private function skillPage(Request $request, string $html, Skill $skill)
    {
        $base = rtrim($request->getSchemeAndHttpHost(), '/');
        $url = $base . '/skill/' . $skill->handle . '/' . $skill->slug;
        $desc = trim($skill->description_zh ?: $skill->description) ?: self::SITE_DESC;
        $desc = mb_substr($desc, 0, 160);
        $title = $skill->name . ' - ' . self::SITE_NAME;

        $jsonLd = [
            '@context' => 'https://schema.org',
            '@type' => 'TechArticle',
            'headline' => $skill->name,
            'description' => $desc,
            'url' => $url,
            'version' => $skill->version ?: null,
            'author' => ['@type' => 'Person', 'name' => $skill->handle],
            'isPartOf' => ['@type' => 'WebSite', 'name' => self::SITE_NAME, 'url' => $base],
            'keywords' => '生物信息,' . ($skill->category_name ?: $skill->category),
        ];

        $extra = implode("\n    ", array_filter([
            '<meta name="description" content="' . e($desc) . '">',
            '<meta name="keywords" content="' . e('生物信息,' . ($skill->category_name ?: '') . ',' . $skill->name) . '">',
            '<link rel="canonical" href="' . e($url) . '">',
            '<meta property="og:type" content="article">',
            '<meta property="og:site_name" content="' . e(self::SITE_NAME) . '">',
            '<meta property="og:title" content="' . e($title) . '">',
            '<meta property="og:description" content="' . e($desc) . '">',
            '<meta property="og:url" content="' . e($url) . '">',
            $skill->icon_url ? '<meta property="og:image" content="' . e($skill->icon_url) . '">' : null,
            '<meta name="twitter:card" content="summary">',
            '<meta name="twitter:title" content="' . e($title) . '">',
            '<meta name="twitter:description" content="' . e($desc) . '">',
            '<script type="application/ld+json">' . json_encode($jsonLd, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>',
        ]));

        return response($this->inject($html, ['title' => $title, 'extra' => $extra]))
            ->header('Content-Type', 'text/html; charset=utf-8');
    }

    private function siteMeta(Request $request): array
    {
        $base = rtrim($request->getSchemeAndHttpHost(), '/');

        return [
            'title' => self::SITE_NAME . ' - 生物分析 AI 技能库',
            'extra' => implode("\n    ", [
                '<meta name="description" content="' . e(self::SITE_DESC) . '">',
                '<meta name="keywords" content="' . e(self::SITE_KEYWORDS) . '">',
                '<link rel="canonical" href="' . e($base . '/') . '">',
                '<meta property="og:type" content="website">',
                '<meta property="og:site_name" content="' . e(self::SITE_NAME) . '">',
                '<meta property="og:title" content="' . e(self::SITE_NAME . ' - 生物分析 AI 技能库') . '">',
                '<meta property="og:description" content="' . e(self::SITE_DESC) . '">',
                '<meta property="og:url" content="' . e($base . '/') . '">',
                '<meta name="twitter:card" content="summary">',
            ]),
        ];
    }

    /** 替换 <title> 并在 </head> 前注入额外标签 */
    private function inject(string $html, array $meta): string
    {
        $html = preg_replace('/<title>.*?<\/title>/s', '<title>' . e($meta['title']) . '</title>', $html, 1);
        if (!empty($meta['extra'])) {
            $html = str_replace('</head>', "    {$meta['extra']}\n  </head>", $html);
        }

        return $html;
    }

    /**
     * GET /sitemap.xml — 首页 + 全部技能详情页
     */
    public function sitemap(Request $request)
    {
        $base = rtrim($request->getSchemeAndHttpHost(), '/');
        $urls = [
            ['loc' => $base . '/', 'priority' => '1.0', 'changefreq' => 'daily'],
        ];
        foreach (Skill::select('handle', 'slug', 'synced_at')->orderBy('id')->cursor() as $s) {
            $urls[] = [
                'loc' => $base . '/skill/' . $s->handle . '/' . $s->slug,
                'lastmod' => $s->synced_at ? date('Y-m-d', $s->synced_at) : null,
                'priority' => '0.7',
                'changefreq' => 'weekly',
            ];
        }

        $xml = '<?xml version="1.0" encoding="UTF-8"?>' . "\n"
            . '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
        foreach ($urls as $u) {
            $xml .= "  <url>\n    <loc>" . e($u['loc']) . "</loc>\n";
            if (!empty($u['lastmod'])) $xml .= "    <lastmod>{$u['lastmod']}</lastmod>\n";
            $xml .= "    <changefreq>{$u['changefreq']}</changefreq>\n    <priority>{$u['priority']}</priority>\n  </url>\n";
        }
        $xml .= '</urlset>';

        return response($xml)->header('Content-Type', 'application/xml; charset=utf-8');
    }

    /**
     * GET /robots.txt
     */
    public function robots(Request $request)
    {
        $base = rtrim($request->getSchemeAndHttpHost(), '/');
        $txt = "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: {$base}/sitemap.xml\n";

        return response($txt)->header('Content-Type', 'text/plain; charset=utf-8');
    }
}
