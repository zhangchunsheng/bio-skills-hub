# CLAUDE.md

## 项目概述

Bio Skills Hub —— 面向生物分析的 AI Agent Skills 离线库网站。技能内容从
[SkillHub.cn](https://www.skillhub.cn/) 社区一次性抓取（`php php-server/bin/sync.php`），
保存到 **SQLite 数据库 + 本地文件**。**部署后完全不依赖外网**，运行时所有数据来自本地。

## 技术栈

- 前端：Vue 3 + Vite + Tailwind CSS 3 + Vue Router（`<script setup>` 组合式 API）
- 后端：PHP 8（无框架，PDO + SQLite），使用 PHP 内置服务器
- 数据库：SQLite（`data/skills.db`）
- 需要 PHP 扩展：`curl`、`pdo_sqlite`（Debian/Ubuntu：`sudo apt install php8.3-sqlite3 php8.3-curl`）

## 常用命令

```bash
npm install                       # 安装前端依赖
npm run sync                      # 从 skillhub.cn 抓取生物相关技能到本地（可反复执行，增量更新）
npm run dev                       # 同时启动 PHP 后端(:8000)和 Vite 前端(:5173，/api 代理到 8000)
npm run build && npm start        # 生产模式：PHP 在 :8000 直接托管 dist/
```

## 架构与目录

```
├── php-server/
│   ├── public/index.php   # 唯一入口（路由器）：/api/* 返回 JSON，其余路径回退到 dist/ SPA
│   ├── src/db.php         # PDO/SQLite 数据访问层、schema、文件路径工具
│   └── bin/sync.php       # 抓取脚本：skillhub.cn → SQLite + data/skills/ 文件
├── src/                   # Vue 前端
│   ├── views/HomeView.vue        # 技能浏览：搜索/主题快捷词/分类/排序/分页
│   ├── views/SkillDetailView.vue # 技能详情：元信息 + 文件预览/下载
│   ├── components/SkillCard.vue
│   └── api.js                    # 前端 API 封装（只调本地 /api）
├── data/                  # 运行时数据（gitignore）
│   ├── skills.db          # SQLite：skills / files / meta 三张表
│   └── skills/<handle>__<slug>/files/…   # 技能文件（SKILL.md 等）
└── docs/README.md         # 原始需求记录
```

## 数据流

1. `sync.php` 用一组英文生物关键词（`bio`、`genomics`、`protein`、`single-cell` 等，
   见脚本内 `KEYWORDS` 常量）分页检索 skillhub.cn 公开 API，去重后 upsert 进 SQLite；
   再用 `curl_multi` 并发下载每个技能的文件清单与文件内容到 `data/skills/`。
   支持 `--refresh`（全量重下）与 `--max-pages=N`（限制每关键词页数，用于测试）。
   注意：skillhub.cn 的中文关键词搜索是模糊评分匹配，相关性差，故关键词全部用英文术语。
2. 运行时 PHP 只查 SQLite / 读本地文件，不访问外网。

## API（PHP 后端，全部本地数据）

| 接口 | 说明 |
|---|---|
| `GET /api/skills?keyword=&category=&page=&pageSize=&sort=` | 搜索技能；sort ∈ downloads/stars/installs/newest |
| `GET /api/categories` | 本地库中实际存在的分类及数量 |
| `GET /api/stats` | 收录统计（技能数、文件数、最近同步时间） |
| `GET /api/skills/{handle}/{slug}` | 技能详情 + 文件清单 |
| `GET /api/skills/{handle}/{slug}/file?path=` | 文件内容（text/plain） |

## 上游 skillhub.cn API（仅 sync.php 使用）

| 接口 | 说明 |
|---|---|
| `GET /api/skills?page&pageSize&keyword` | 搜索，`data.skills[]` / `data.total` |
| `GET /api/v1/categories` | 分类 key → 中文名映射 |
| `GET /api/v1/skills/{slug}/files?namespace={handle}` | 文件清单（path/sha256/size） |
| `GET /api/v1/skills/{slug}/file?path=&namespace=` | 文件内容，302 跳转腾讯 COS，需跟随重定向 |

## 约定

- **PHP 禁用裸 `exit;` / `exit(0);`**：本机 PHP 8.3.6 (Ubuntu noble) 构建把零状态码的
  exit 当作空操作继续执行（`exit(非零)` 正常）。所有提前结束用返回值/if-else 结构或顶层
  `return` 表达（见 `php-server/public/index.php` 的 `routeApi()`）。
- 安全：所有写入磁盘的相对路径必须经过 `isSafeRelPath()` 校验（禁止 `..` 与绝对路径）。
- 技能本地目录名为 `<handle>__<slug>`，非单词字符替换为 `_`（见 `skillDir()`）。
- 前端字段使用 snake_case（与 SQLite 列一致）：`icon_url`、`description_zh`、`category_name`。
- 界面文案为中文；代码注释可用中文。
- 提交前验证：`npm run build` 通过、`php -l` 检查 PHP 语法。
