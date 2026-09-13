# Bio Skills Hub 🧬

面向生物分析的 AI Skills 聚合站。从 [SkillHub.cn](https://www.skillhub.cn/) 社区检索生物信息、基因组学、药物研发等方向的 Agent Skills，并可一键下载到本地。

## 技术栈

- **前端**：Vue 3 + Vite + Tailwind CSS + Vue Router
- **后端**：Node.js + Express（代理 SkillHub API、下载技能到本地磁盘）
- **数据源**：`https://api.skillhub.cn`（公开 API，无需鉴权）

## 快速开始

```bash
npm install
npm run dev
```

- 前端：http://localhost:5173
- 后端：http://localhost:3001

## 功能

- **技能市场**：关键词搜索（内置生物医药 / 基因组学 / 蛋白质 / 单细胞测序等主题快捷词）、分类筛选、排序、分页
- **技能详情**：查看技能元信息与文件内容（如 `SKILL.md`）
- **下载到本地**：点击"下载到本地"，后端将技能全部文件保存到 `data/downloads/<handle>__<slug>/`
- **本地技能库**：查看、预览、删除已下载的技能

## 生产模式

```bash
npm run build
npm start   # 后端直接托管 dist/，访问 http://localhost:3001
```

## 项目结构

```
├── server/
│   ├── index.js      # Express 入口，API 路由
│   ├── skillhub.js   # SkillHub.cn 上游 API 客户端
│   └── storage.js    # 本地下载存储（data/downloads/）
├── src/
│   ├── views/        # HomeView / SkillDetailView / LibraryView
│   ├── components/   # SkillCard
│   ├── api.js        # 前端 API 封装
│   └── ...
└── data/             # 运行时生成：下载的技能与索引（已 gitignore）
```

## 使用的上游 API

| 接口 | 说明 |
|---|---|
| `GET /api/skills?page&pageSize&keyword&category&sortBy&order` | 技能搜索 |
| `GET /api/v1/categories` | 分类列表 |
| `GET /api/v1/skills/{slug}?namespace=` | 技能详情 |
| `GET /api/v1/skills/{slug}/files?namespace=` | 文件清单 |
| `GET /api/v1/skills/{slug}/file?path=&namespace=` | 文件内容（302 → COS） |
