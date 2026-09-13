# Bio Skills Hub 🧬

面向生物分析的 AI Agent Skills 离线库平台。技能内容预先从 [SkillHub.cn](https://www.skillhub.cn/)
社区抓取并保存到本地（SQLite + 文件），**部署后完全离线运行，不再访问外网**。

## 技术栈

| 模块 | 技术 |
|---|---|
| 用户端 `web/` | Vue 3 + Vite + Tailwind CSS |
| 管理端 `admin/` | Vue 3 + Vite + Element Plus |
| 后端 API `server/` | Laravel（目标 PHP 8.2，见 composer `platform`） |
| 数据库 | SQLite（`data/skills.db`） |

## 环境要求

- Node.js ≥ 18
- PHP ≥ 8.2（本地开发使用 8.3），扩展：`curl`、`pdo_sqlite`
- Composer

## 快速开始

```bash
# 安装依赖
npm install && npm --prefix web install && npm --prefix admin install
cd server && composer install && cp .env.example .env && php artisan key:generate && cd ..

# 抓取技能数据（一次性，可随时重跑更新）
npm run sync

# 开发（同时启动 Laravel :8000、用户端 :5173、管理端 :5174）
npm run dev
```

- 用户端：http://localhost:5173
- 管理端：http://localhost:5174
- API：http://localhost:8000/api/

## 生产部署

```bash
npm run deploy   # 构建两个前端并拷入 server/public/
npm start        # Laravel 在 :8000 提供 API + 用户端 / + 管理端 /admin/
```

生产环境通常用 Nginx/Apache 将域名指向 `server/public/`。

## 项目结构

```
├── web/               # 用户端（Vue 3 + Tailwind）：技能浏览/搜索/详情/文件预览
├── admin/             # 管理端（Vue 3 + Element Plus）：仪表盘、技能管理、同步触发
├── server/            # Laravel API
│   ├── app/Console/Commands/SyncSkills.php   # skills:sync 抓取命令
│   ├── app/Http/Controllers/                 # 公开 API + Admin API
│   └── routes/api.php
├── data/              # 运行时数据：skills.db 与技能文件（已随仓库提交，开箱即用）
└── deploy/deploy.sh   # 前端产物发布脚本
```

## 功能

**用户端**：关键词搜索（内置基因组学 / 蛋白质 / 单细胞等主题快捷词）、分类筛选、
排序、分页、技能详情、文件在线预览与下载。

**管理端**：收录统计仪表盘、增量/全量同步触发（后台执行）、技能检索表格、
元数据编辑、删除（同时清理磁盘文件）。

详见 [CLAUDE.md](./CLAUDE.md)。
