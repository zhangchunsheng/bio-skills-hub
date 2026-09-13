# CLAUDE.md

## 项目概述

Bio Skills Hub —— 面向生物分析的 AI Agent Skills 离线库平台。技能内容从
[SkillHub.cn](https://www.skillhub.cn/) 社区抓取（`php artisan skills:sync`），
保存到 **SQLite 数据库 + 本地文件**。**部署后完全不依赖外网**，运行时所有数据来自本地。

## 技术栈与模块

| 模块 | 技术 | 说明 |
|---|---|---|
| `web/` | Vue 3 + Vite + Tailwind CSS 3 + Vue Router | 用户端（技能浏览/搜索/详情） |
| `admin/` | Vue 3 + Vite + Element Plus | 管理端（仪表盘/技能管理/同步） |
| `server/` | Laravel 12（PHP ≥ 8.2，本地用 8.3 开发） | 后端 API |
| `data/` | SQLite `skills.db` + `skills/` 文件目录 | 技能数据（已随仓库提交，开箱即用） |

需要 PHP 扩展：`curl`、`pdo_sqlite`（Ubuntu：`sudo apt install php-sqlite3 php-curl`）。
SQLite 默认路径为仓库根目录 `data/skills.db`（`config/database.php` 中用
`base_path('../data/skills.db')` 解析，与部署机器无关）；可用 `DB_DATABASE` 环境变量覆盖。

## 常用命令（在仓库根目录执行）

```bash
npm run dev        # 同时启动 Laravel(:8000)、用户端 Vite(:5173)、管理端 Vite(:5174)
npm run sync       # = php server/artisan skills:sync，增量抓取技能（--refresh 全量）
npm run build      # 构建 web/ 与 admin/
npm run deploy     # 构建并拷入 server/public/（管理端 base=/admin/）
npm start          # Laravel 托管 API + 用户端 / + 管理端 /admin/
```

## 架构与目录

```
├── web/                  # 用户端 Vue（Tailwind，暗色主题，bio 绿）
├── admin/                # 管理端 Vue（Element Plus）
│   └── vite.config.js    # build 时 base=/admin/
├── server/               # Laravel
│   ├── app/Console/Commands/SyncSkills.php   # 抓取命令（Http::pool 并发）
│   ├── app/Http/Controllers/SkillController.php        # 公开 API
│   ├── app/Http/Controllers/Admin/…                    # 管理 API（无鉴权，内网工具）
│   ├── app/Models/Skill.php / SkillFile.php            # diskDir()/isSafeRelPath()
│   ├── config/skills.php # 存储路径、上游地址、同步关键词
│   └── routes/api.php
├── data/                 # skills.db（skills/files/meta 三表）+ skills/<handle>__<slug>/files/
├── deploy/deploy.sh      # 前端产物拷入 server/public/
└── docs/README.md        # 原始需求记录
```

## 数据流

1. `skills:sync` 用 `config/skills.php` 中的英文生物关键词分页检索 skillhub.cn
   公开 API，去重后 `updateOrCreate` 进 SQLite；再用 `Http::pool` 并发下载文件清单
   与文件内容（按 sha256 跳过未变更文件）。`--refresh` 全量重下，`--max-pages=N` 限页测试。
   注意：skillhub.cn 的中文关键词搜索是模糊评分匹配，相关性差，关键词全部用英文术语。
2. 运行时 Laravel 只查 SQLite / 读本地文件，不访问外网。
3. 管理端"同步"按钮通过 `Process` 后台执行 artisan 命令，状态写在
   `server/storage/app/sync-status.json`，日志在 `server/storage/logs/sync.log`。

## API（全部本地数据）

认证（Sanctum Bearer token；前端把 token 存 localStorage，请求带 `Authorization: Bearer`）：
| 接口 | 说明 |
|---|---|
| `POST /api/auth/register` · `POST /api/auth/login` | 注册（role=user）/ 登录，返回 `{token, user}` |
| `POST /api/auth/logout` · `GET /api/auth/me`（需登录） | 注销 / 当前用户 |
| `POST /api/auth/password`（需登录） | 修改密码，吊销其它令牌 |

默认管理员：`admin@bio-skills.local / admin123456`，由 `php artisan db:seed` 创建
（`ADMIN_EMAIL`/`ADMIN_PASSWORD` 环境变量可覆盖）。

公开：
| 接口 | 说明 |
|---|---|
| `GET /api/skills?keyword=&category=&page=&pageSize=&sort=` | 搜索；sort ∈ downloads/stars/installs/newest |
| `GET /api/categories` | 本地库分类及数量 |
| `GET /api/stats` | 收录统计与最近同步时间 |
| `GET /api/skills/{handle}/{slug}` | 详情 + 文件清单 |
| `GET /api/skills/{handle}/{slug}/file?path=` | 文件内容（text/plain） |

用户（需登录）：
| 接口 | 说明 |
|---|---|
| `POST /api/skills` | 上传技能（multipart：元数据字段 + `files[]`，必须含 SKILL.md，单文件 ≤2MB；handle=`u{user_id}`） |
| `GET /api/my/skills` · `DELETE /api/my/skills/{id}` | 我的上传 / 删除（连带磁盘文件） |

管理（`/api/admin/`，需 admin 角色）：
| 接口 | 说明 |
|---|---|
| `GET /api/admin/skills?keyword=&category=&page=` | 管理列表（含 files_count） |
| `GET/PUT/DELETE /api/admin/skills/{id}` | 详情 / 编辑元数据 / 删除（含磁盘文件） |
| `GET /api/admin/sync-status` · `POST /api/admin/sync` | 同步状态 / 触发同步 |
| `GET/POST /api/admin/users` · `PUT/DELETE /api/admin/users/{id}` | 用户管理：列表/创建/编辑角色与邮箱/重置密码（PUT 带 password）/删除（连带清理其上传技能）；不可删除或降级自己 |

## 上游 skillhub.cn API（仅同步命令使用）

| 接口 | 说明 |
|---|---|
| `GET /api/skills?page&pageSize&keyword` | 搜索，`data.skills[]` / `data.total` |
| `GET /api/v1/categories` | 分类 key → 中文名 |
| `GET /api/v1/skills/{slug}/files?namespace={handle}` | 文件清单（path/sha256/size） |
| `GET /api/v1/skills/{slug}/file?path=&namespace=` | 文件内容，302 跳腾讯 COS，需跟随重定向 |

## 约定

- **PHP 禁用裸 `exit;` / `exit(0);`**：本机 PHP 8.3.6 (Ubuntu noble) 构建把零状态码
  exit 当作空操作继续执行（`exit(非零)` 正常）。提前结束用返回值/if-else/顶层 `return`。
- **composer 镜像用腾讯（`mirrors.cloud.tencent.com/composer/`）**：阿里云 composer
  镜像已停止维护（元数据过期、安全公告误报全量版本）。GitHub codeload 直连在本网络下会超时。
- **字符串内插变量后紧跟全角字符（如 `）`）时必须用花括号**:`"（失败 {$failed}）"`，
  否则 PHP 把全角字符并进变量名（历史上踩过两次）。
- 安全：所有磁盘相对路径必须过 `SkillFile::isSafeRelPath()`（禁 `..` 与绝对路径）；
  技能目录名 `<handle>__<slug>`，非单词字符替换为 `_`（见 `Skill::diskDir()`）。
- 用户端字段 snake_case（与 SQLite 列一致）：`icon_url`、`description_zh`、`category_name`。
- 界面文案为中文；代码注释可用中文。
- **SEO**:`SeoController` 在 fallback 路由里按路径向 index.html 注入 meta
  （技能页查库生成 title/OG/JSON-LD/canonical）；新增公开页面时记得同步
  `sitemap()`；管理端必须保持 noindex。Nginx 部署用
  `try_files $uri $uri/ /index.php?$query_string;`，技能页不是真实文件才会
  走进 Laravel 注入逻辑。
- 提交前验证：`npm run build`（两个前端）、`php artisan route:list` 正常。
