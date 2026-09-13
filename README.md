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
# SQLite 默认使用仓库根目录 data/skills.db（已随仓库提交），无需额外配置；
# 如需换路径，在 server/.env 中设置 DB_DATABASE 绝对路径

# 抓取技能数据（一次性，可随时重跑更新）
npm run sync

# 创建默认管理员（admin@bio-skills.local / admin123456，可用 ADMIN_EMAIL/ADMIN_PASSWORD 覆盖）
cd server && php artisan db:seed --force && cd ..

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

# 重要：PHP 进程（php-fpm/Apache，通常 www-data）需要对 data/ 与
# server/storage 有写权限，否则登录/上传会报 "attempt to write a readonly database"
sudo chown -R www-data:www-data data/ server/storage server/bootstrap/cache
```

生产环境通常用 Nginx/Apache 将域名指向 `server/public/`。注意 SQLite 写入要求
数据库文件**及其所在目录**都可写（会创建 `-journal`/`-wal` 临时文件）。

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
排序、分页、技能详情、文件在线预览与下载；**注册登录后可上传自己的技能**
（multipart，必须包含 SKILL.md），并可管理（删除）自己的上传。

**管理端**（需管理员登录）：收录统计仪表盘、增量/全量同步触发（后台执行）、
技能检索表格、元数据编辑、删除（同时清理磁盘文件）、**用户管理**（列表/新建/
编辑角色/重置密码/删除，删除用户时连带清理其上传的技能）。
默认管理员：`admin@bio-skills.local / admin123456`（`php artisan db:seed` 创建，
可用 `ADMIN_EMAIL`/`ADMIN_PASSWORD` 环境变量覆盖；登录后请通过
`POST /api/auth/password` 修改密码）。

详见 [CLAUDE.md](./CLAUDE.md)。
