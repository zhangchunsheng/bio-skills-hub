# Bio Skills Hub 🧬

面向生物分析的 AI Agent Skills 离线库网站。技能内容预先从 [SkillHub.cn](https://www.skillhub.cn/)
社区抓取并保存到本地（SQLite + 文件），**部署后完全离线运行，不再访问外网**。

## 技术栈

- **前端**：Vue 3 + Vite + Tailwind CSS + Vue Router
- **后端**：PHP 8（PDO + SQLite，无框架，内置服务器即可运行）
- **数据库**：SQLite（`data/skills.db`）

## 环境要求

- Node.js ≥ 18
- PHP ≥ 8.1，扩展：`curl`、`pdo_sqlite`
  - Debian/Ubuntu：`sudo apt install php-cli php-sqlite3 php-curl`

## 快速开始

```bash
npm install
npm run sync     # 从 skillhub.cn 抓取生物分析相关技能到本地（一次性，可随时重跑更新）
npm run dev      # 前端 http://localhost:5173（/api 自动代理到 PHP :8000）
```

## 生产部署

```bash
npm run build
npm start        # PHP 在 :8000 同时提供 API 和前端静态页面
```

也可以把 `dist/` 交给 Nginx/Apache 托管，将 `/api` 反代到 PHP。

## 功能

- **技能库浏览**：关键词搜索（内置基因组学 / 蛋白质 / 单细胞 / 测序 / 药物研发等主题快捷词）、分类筛选、排序、分页
- **技能详情**：元信息、文件列表、`SKILL.md` 等内容在线预览、单文件下载
- **离线数据**：所有技能元数据存于 SQLite，技能文件存于 `data/skills/`，运行时零外网依赖
- **增量同步**：`npm run sync` 可随时重跑以更新技能库（`--refresh` 强制全量重下）

## 项目结构

```
├── php-server/
│   ├── public/index.php   # PHP 入口：/api/* JSON 接口 + dist/ 静态托管
│   ├── src/db.php         # SQLite 数据访问层
│   └── bin/sync.php       # 抓取脚本：skillhub.cn → SQLite + 本地文件
├── src/                   # Vue 前端源码
├── data/                  # 运行时生成：skills.db 与技能文件（已 gitignore）
└── CLAUDE.md              # 面向 AI 协作者的项目说明
```

详见 [CLAUDE.md](./CLAUDE.md)。
