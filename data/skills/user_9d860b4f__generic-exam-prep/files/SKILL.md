---
name: generic-exam-prep
description: |
  Use this skill when building, scaffolding, or refactoring ANY pure-frontend H5 quiz /
  exam-prep system (考研, 公考, 医师资格, 法律职业, language certs, corporate training, etc.)
  from scratch or adapting an existing one. It provides a reusable architecture template
  with single-file loading (questions.json, fetch with retry, no shard/IndexedDB dependency), standard module
  breakdown (daily / chapter / mock / real-exam / mistakes / favorites / knowledge cards),
  a GLOBAL SUBJECT SELECTOR in the sidebar (below brand, above nav; lockable per-module; single-subject auto-hide),
  mistake "conquer" semantics (mark-conquered not delete; idempotent by questionId),
  rail + 3D flip knowledge cards with pure-click interaction (no keyboard/ARIA),
  LocalStorage progress model with silent resume, responsive left-folding nav with chapter-filter
  drawers (left-slide), exam-mode answer-hiding (submit auto-advance, no reveal until 交卷), exam question-number palette on the left, exam-result with stats + single-question review browse (per-question: question+options+user-answer+correct-answer, back-to-result button on last), two-level collapsible sidebar nav with subject selector in sidebar, practice-mode last-question stop (no next/jump), knowledge single-card with localStorage progress tracking, mistake/favorite single-question paged review (no chapter filter), exam exit guard
  (SHA-256 hashed) with auto nickname mapping, jsdom smoke-test workflow, a HARDENED pitfall set
  (built-in SHA-256 template with >>> mod-32 fix, fetch `no-store` with 3-tier retry,
  global error listeners, stopTimer null-guard, and 10 others), and CloudStudio / COS deploy flows.
  Trigger when the user asks
  or wants a generic, exam-agnostic version of a subject-specific prep tool.
agent_created: true
---

# 通用备考系统（跨考试可复用框架）

## Overview
A reusable blueprint for zero-build, zero-backend, pure-frontend H5 exam-prep apps. Use it to
stand up a new prep system for any exam, or to generalize a subject-specific one. It favors
silent progress resume (no popups), mobile-friendly folding navigation, a structured
exam-result page, and a simple single-file loading architecture (questions.json with 3-tier retry fetch). Concrete subject rules (question bank, whitelist) live in the consuming project.

## When to use
- Scaffolding a new quiz/exam-prep H5 for any subject.
- Porting a prep tool to a new exam domain.
- Refactoring an existing prep app toward the conventions below.
- Wiring whitelist-based login with auto nickname display.

## ⛔ 前置问题（intake）= 强制第一步（每次生成新系统必问，不可跳过）

> **硬性规则**：本 skill 被调用来「从零搭建 / 生成」一个新的备考系统时，**agent 的第一条回复 MUST 是前置问题**，用 `AskUserQuestion` 呈现下方 Q1–Q10。问询确认前，禁止读取模板、禁止写文件、禁止部署。
> ⚠️ **反模式教训**：曾跳过这步直接开工，导致多处凭默认猜（白名单示例账号、科目划分、模块范围都是 agent 自作主张）。**无论用户多急，都必须先问**；用户说「直接按默认搭」等同默认确认全部「默认值」项，但仍需先把问题列出来、拿到确认再开工。
> 这是本 skill 的「前置问题」约定——每次新系统都必须走一遍，不是一次性文档。

## Mandatory pre-build intake (run BEFORE coding)

Before scaffolding or refactoring, collect the following. **Do not start development/deployment
until all required params for the chosen branch are confirmed.** Use `AskUserQuestion` (one or
several calls). Reasonable defaults may be proposed but must be marked「默认值」.

### Base params (required)
| # | Question | Why it matters |
|---|----------|----------------|
| Q1 | 目标考试类型与名称？(考研 / 公考 / 医师资格 / 法律职业 / 语言证书 / 企业培训 / 其他) | 决定科目划分、题型枚举、考点结构 |
| Q2 | 需要构建多少个考试科目？各科目名称？ | 数据按科目组织；单科目时全局自动隐藏科目筛选框 |
| Q3 | 题型清单？(单选 / 多选 / 判断 / 填空 / 简答 / 论述 / 作文 等) | 客观题系统判分；主观题只展示采分点 + 参考答案，不判分 |
| Q4 | 启用哪些功能模块？逐项勾选 | 动态隐藏未启用模块入口；关闭模块保留历史数据，仅隐藏入口 |

**模块清单（逐项确认启用 / 关闭）：**
- [ ] 备考中心 dashboard — **默认落地页**（欢迎语 + 模块入口卡）
- [ ] 知识卡 knowledge
- [ ] 每日一练 daily
- [ ] 章节刷题 chapter
- [ ] 模拟题 mock
- [ ] 真题模考 real-exam
- [ ] 错题本 mistakes — 建议默认启用（其他模块依赖）
- [ ] 收藏夹 favorites — 建议默认启用（其他模块依赖）

### Branch params

**Q6 — 白名单数据源（三选一，手机号 SHA-256 哈希比对，白名单不存明文）：**
- **A. 直接提供手机号清单（推荐，零运维）** → 确认格式（纯文本手机号 / 含姓名）；用 `gen-hash.html` 或 `crypto.js` 生成 SHA-256 哈希后写入 `whitelist.json`
- **B. 本地 Excel 文件** → 确认模板字段（手机号列、姓名列）；人工解析后生成哈希写入 `whitelist.json`
- **C. 飞书在线文档** → 追问：同步周期、飞书文档链接、变更通知接收人/群；需配套定时脚本（云函数/cron），运维成本高

> 无论选哪种，最终生成 `data/whitelist.json` = `{ "entries": [{ "hash": "sha256hex", "name": "昵称" }] }`（兼容旧格式 `{ "hashes": [...] }`）。用户登录时手机号经 SHA-256 哈希后与白名单哈希比对，昵称自动从白名单读取，**无需用户手填昵称**。登录弹窗副标题统一为「输入手机号（仅本地记录，不上传），系统生成你的专属学习档案」。白名单仅存哈希值，不存明文手机号（合规要求）。

**Q7 — 是否需要 AI 离线预生成题目？**
- 若需要：确认各章节题量配比；交付前用 AI 工具按大纲批量生成 → 人工审核 → 导入 `questions.json`；**运行时无 AI 调用**
- 若不需要：用户提供题库 JSON

> **部署方式：默认 CloudStudio sandbox（无需询问）。** 用 `workbuddy_cloudstudio_deploy` 部署干净 `dist/`（只含 `index.html` + `css/` + `js/` + `data/`）。
> 仅当用户主动要求自定义域名 / 长期稳定链接时才考虑腾讯云 COS，且**必须先读 `references/cos-pitfalls.md`**（5 层 bug 链：createReadStream 空文件、CDN 忽略查询参数、裸路径死循环等）。

### Optional params (sensible defaults if user skips)
| # | Question | Default |
|---|----------|---------|
| Q8 | 主题色色值 / 色系？ | `--c-primary` 蓝紫渐变（可改绿/橙等）|
| Q9 | 是否提供配套材料（大纲 / 教材 / 真题 / 讲义）？ | 无 |
| Q10 | 登录后落地页？ | **备考中心 dashboard**（欢迎语 + 日期 + 模块入口卡）；dashboard 未登录也可访问，其他模块需登录 |

### Intake execution rules
1. **按序逐项询问**：可用 `AskUserQuestion` 一次性或分批问，但当前分支所需参数必须全部确认。
2. **用户未明确的项**：可给合理默认值并标注「默认值」。
3. **信息收集完成后**：输出分层 PRD + 完整前端模板 + 配套运维说明（依 Q6 选择提供对应白名单方案）。
4. **不得跳过问询直接开发**；每次使用本 skill 必须先完成前置问询。

## Hard-won pitfalls (must read before coding)

15 real bugs were found and fixed in production. **Read `references/pitfalls.md`** for full
root-cause + fix. Each has a copy-paste template in `references/templates/`. Summary:

| # | Bug | Template / Fix |
|---|-----|----------------|
| P1 | Whitelist login fails on `file://` + race | `auth-whitelist-guard.js` + app `openLogin` guard |
| P2 | Modal won't close (stale JS cache) | CSS `.hidden,[hidden]{display:none!important}` + `?v=N` on assets |
| ~~P3~~ | ~~`loadIndex` 并发覆盖~~ | **已移除** — 无分片/IDB 即无此问题 |
| P4 | Bare `App` global (jsdom crash) | Always `QuizApp.App`; never bare `App` |
| P5 | `knowledge.json` written broken (un-escaped quotes) | Generate JSON via script (`json.dump`), never LLM-stream |
| P6 | Mistakes delete-not-conquer; subjective/blank leak in | `storage-mistake-conquer.js` + `quiz-submit-conquer.js` |
| P7 | Per-page subject dropdowns ≠ global selector | `app-global-subject.js` |
| ~~P8~~ | ~~IDB 空分片毒缓存~~ | **已移除** — 无 IndexedDB 缓存 |
| P9 | HTTP 缓存毒化 `data/*.json` → 硬刷新仍空 | `fetchJSON`：`{cache:'no-store'}` + URL `?_=Date.now()` |
| P10 | 真机错误全丢失（无 `unhandledrejection` 监听） | `app.js init` 首行加全局 error/unhandledrejection 监听 |
| ~~P11~~ | ~~健康自检假阴性~~ | **已移除** — 数据一次全量加载，无需 prefetch |
| P12 | 空题静默无恢复入口 | `render()` 空态改 `state-box` 含「刷新页面」「重置缓存并刷新」 |

| P13 | `startPaper` 前置操作 `S`（null → 白屏） | 不要提前设 `S.xxx`，全部走 `startItems` 的 `opts` |
| P14 | 错题本收藏按钮 `ReferenceError: q is not defined` | wireCard 不要引用外部局部变量 `q`，用 `rec.questionData` |
| P15 | 路由时未开始答题即调 `stopTimer()` → 崩 | `stopTimer()` 首行加 `if(S && S.timer)` 空守卫 |

## Architecture template

### Single namespace, IIFE modules
```js
(function (global) {
  var App = { /* router, dashboard, login, renderUser */ };
  global.QuizApp = global.QuizApp || {};
  global.QuizApp.App = App;
})(window);
```
Split feature code into one file per module to keep each under ~400 lines.

### Core modules
- `js/app.js` — router, **dashboard (备考中心, default landing page)**, login dialog, `renderUser` (top-right greeting).
- `js/idb.js` — `DataStore` manager (`loadData` / `getSubject` / `getChapter` / `findQuestion`). Single `questions.json` fetch with 3-tier retry.
- `js/quiz.js` — daily/chapter/mock/exam modes, `renderExamComplete` (result page), `gradeExamSilent` (exam exit guard).
- `js/knowledge.js` — single-card knowledge view with localStorage progress, sidebar chapter linkage, 3D flip (pure click).
- `js/review.js` — shared module for 错题本 + 收藏夹 (single-question paged view with prev/next; no chapter filter).
- `js/auth.js` — phone-number whitelist login (SHA-256 hashed compare), auto nickname from whitelist.
- `js/storage.js` — LocalStorage wrapper, per-user isolation prefix, progress persistence.
- `js/crypto.js` — pure-JS SHA-256 for whitelist compare + user isolation prefix (template: `references/templates/crypto-sha256.js`).

### Data model
```
Data.subjects[]            // e.g. one subject, or grouped by exam section
  └─ chapters[]            // chapters / units / topics
       └─ questions[]      // { id, type, question, options:[{label,text}], answer, analysis,
                            //   scoringPoints:[{score,point}], referenceAnswer }
```
Keep progress separate from content: persist progress to LocalStorage keyed by user + module + chapter.

### Layout pattern (PC: 侧栏常驻 + 主区; 移动端: 侧栏抽屉)
Desktop: `#sidebar` fixed left, `#main` flex right. Mobile: `#sidebar` is a fixed left drawer triggered by `#railToggle`,
with `#railOverlay` as backdrop. 章节筛选抽屉已移除——侧栏两级导航替代.

## Data loading (simple, single file)

All data lives in one file: `data/questions.json`. `DataStore.loadData()` fetches it once
(with 3-tier retry: cache-bust → clean URL → 800ms delayed retry) and populates
`Data.subjects` / `Data.mockPapers` / `Data.realPapers`. The promise is cached — subsequent
calls return the same result.

- **No IndexedDB, no shards, no `INDEX_VER`**. One file, one fetch.
- Chapters have `questions` arrays inline — read from `DataStore.getChapter()` directly.
- Module entry: `DataStore.loadData().then(...)` — fire-and-forget on first call, instant after.
- `js/idb.js` is ~60 lines (retry logic + query helpers). No `references/architecture.md` needed.
- Do NOT use `ensureSubject`, `ensureChapter`, `loadIndex`, or `INDEX_VER` — these are removed.

## 备考中心 Dashboard（默认落地页）

`DEFAULT_ROUTE = 'dashboard'` — 登录后（及未登录时）首先进入备考中心，结构如下：

1. **登录引导横幅**（未登录时顶部显示）—「登录后解锁全部学习功能」+「立即登录」按钮。
2. **Hero 区域** — `👋 你好，{昵称}` + 今日日期/星期 + 「开始每日一练 →」CTA（仅登录态）。
3. **学习模块入口卡** — 网格展示启用的模块（含错题/收藏 badge 计数），点击进入对应模块。

**关键点：**
- dashboard 未登录也可访问（展示登录引导横幅 + 模块入口）；其他模块需登录。
- 题数显示兼容骨架态：`count != null ? count : questions.length`（直接从 questions 数组计算）。

## 全局科目选择器（侧栏内，P7）

科目下拉放在 `#sidebar` 内（brand 下方、nav 上方），全站唯一入口。所有模块按所选科目呈现数据。

- `index.html`：`<nav id="sidebar">` 内 `<div class="brand">` 下方放 `<div id="subjbar" hidden></div>`。
  桌面端侧栏常驻，科目下拉始终可见；移动端侧栏是抽屉，科目下拉随抽屉出现。
- `js/app.js`：`App.currentSubject` + `getSubject()/setSubject()` 是全局唯一科目来源；
  `renderGlobalSubject()` 渲染 `#subjbar`（`<select>` + `<label>`），单科目时 `bar.hidden=true` 自动隐藏。
- 各页面**无独立的章节筛选**（章节下拉框已全部移除）。侧栏两级导航中点击章节子项即切换内容。
- 模块内科目锁定：进入模块后 `renderGlobalSubject(true)` → `select disabled` + `🔒 科目·锁定`，
  回备考中心才可切换。

## Standard module breakdown
| Module | Purpose | Resume behavior |
|--------|---------|-----------------|
| 每日一练 (daily) | deterministic seeded subset per day | silent resume by date key |
| 章节刷题 (chapter) | browse by chapter cards (direct entry) | no next-button; tap card → practice |
| 模拟题 (mock) | full timed paper | exam flow |
| 真题模考 (real-exam) | past papers | exam flow |
| 错题本 (mistakes) | wrong-question review (single-question paged) | prev/next buttons; no chapter filter |
| 收藏夹 (favorites) | bookmarked review (single-question paged) | prev/next buttons; no chapter filter |
| 知识卡 (knowledge) | single flashcard + localStorage progress | sidebar chapter click → switch chapter cards |

## 考试模式 · 关键行为
- **提交后不显示答案**：考试中提交只记录答案并自动跳到下一题；最后一题提交后停住，显示「已提交，等待交卷」。
- 实现要点：`renderBody` 对错着色 guard `!S.isExam`；`renderQuestion` 仅在 `!S.isExam` 时渲染 reveal（正确答案/解析）；`submit` 考试分支执行 `S.idx++; render()` 自动跳题。
- **答案仅在交卷后可见**：点击「交卷」→ 确认 → `renderExamComplete` 展示成绩单。

## 考试题号面板
- 考试页面左侧 `.exam-palette`（grid 排列题号按钮），点击可跳转任意题。
- 题号三态：当前 `.current`（蓝底白字）、已答 `.answered`（浅蓝）、未答（灰）。按钮 `data-pidx` 存索引。

## 两级可折叠侧栏导航
- `#sidebar` 中章节刷题、知识卡、模拟题、真题模考四个模块改为 `.has-sub > .nav-parent + .nav-sub` 结构。
- 点击父项展开/折叠（切换 `.open` class）；子项直接启动章节/试卷。`buildSidebar()` 在 `loadData()` 后构建。
- 各页面**不再有独立的章节筛选下拉框**（错题本、收藏夹、知识卡等均已移除 `chapterFilterHTML`/`wireChapterFilter`）。

## 答案回顾 · 单题浏览模式（结果页按钮）
- 结果页两个按钮：「逐题回顾」「错题回顾」（+「返回备考中心」）。
- 点击后进入 `Quiz.reviewBrowse(items, view, onBack)`——每页一道题，答题界面格式（q-card），
  选项已着色 disabled、reveal 直接展开（正确答案+解析+采分点），下一题翻页逐题查看。
- 最后一题显示「返回结果 →」按钮（`onBack` 回调），点后回到成绩报告页。
- 错题回顾若无错题 toasts「本次没有错题 🎉」。
- 实现：回顾按钮保存当前 `S.items`/`S.answers` 快照，传给 `reviewBrowse`；`onBack`→恢复快照→`renderExamComplete()`。

## 模块 UI 重设计模式（知识卡 / 收藏夹 / 错题本 / 章节刷题）

重设计这几个复习模块时沉淀的通用模式，复用即可避免返工。原型定稿后再实现（原型仅作确认，不在原型里写业务代码）。

### 通用原则（每次重设计必守）
- **配色对齐全局主色**：只用 App 的 `--c-primary / --c-success / --c-danger / --c-warn / --c-bg / --c-surface / --c-line` 等 token，**不要另起一套色板**（否则会出现"原型色调与主色调不一致"，需返工）。
- **模块内不做科目筛选**：科目选择唯一入口在侧栏 `#subjbar`（brand 下方）。桌面端常驻可见；移动端侧栏抽屉打开时可见。模块内锁定（`select disabled` + `🔒 科目·锁定`），回备考中心切。
- **解析用内联抽屉（`渐进披露`），不用 modal**：点「解析」就地展开 `.reveal`（`display:none` → `.show`），减少弹窗打断；`revealBody(rec)` 组装「正确答案 + 解析 + 采分点」。
- **纯点击交互（不做键盘/ARIA）**：用户明确要求去掉键盘 ← → / 空格、ARIA、`tabindex`、`focus-visible`、44px 强制触控。所有交互只保留点击（卡片翻面 = `onclick` 翻面；上一张/下一张 = 按钮 `onclick`）。动画仍用 `prefers-reduced-motion` 关闭 `.flashcard-inner` 等过渡。
- **性能**：收藏/错题记录已存 `questionData`（localStorage），重练直接用 `Quiz.startItems(items, {mode:'list'})` 成卷（items 形如 `{q, subjectId, chapterId}`）。
- **尺寸自适应（流体布局）**：容器 `max-width:min(1200px,100%)`；侧栏/rail 宽度 `clamp()`；环形图尺寸 `clamp()`；避免写死 `px` 值。闪卡用 `flex:1` 撑满整页——PC 上 `min-height:calc(100vh-170px)`、移动端 `min-height:max(320px,calc(100vh-200px))`。

### 知识卡 · 单卡视图 + 进度记忆
- 每页只显示一张闪卡（`.kb-single`），上一张/下一张按钮翻页，不跳转。
- 浏览位置存入 localStorage（`kb_prog_{sid}`），退出再进恢复上次章节和卡片索引。
- 侧栏知识卡章节子项点击 → `Knowledge.setChapter(cid)` → 切到对应章节第一张卡。
- 3D 翻转纯点击（`card.onclick → inner.classList.add('flipped')`），不做键盘/ARIA。
- 实现：`Knowledge.render` → `loadData()` → 读 localStorage 恢复进度 → 按 `_selChapter` 过滤知识点列表 → 渲染单卡 + 上下页按钮。

### 章节刷题 · 全宽章节卡片 + 点击直接入答题
- 去掉中间"章节概览卡"那一步，改成**点击卡片直接调 `launchChapter(sid, cid)` 进入答题页**。
- PC 桌面：`.rail-wide` 网格容器（`display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr))`），每张卡片纵向展示章节名 + x/y 题 + 进度条 + CTA 按钮；hover 上浮 + 变色。
- 移动端：`.rail-wide` 的 grid 被媒体查询覆盖（`.rail` 走固定左抽屉），卡片在移动端左抽屉内纵向堆叠，选完**自动折叠**（`classList.remove('open')` + 遮罩隐藏）。
- 卡片结构：`<button class="rail-ch chapter-card" data-cid> <div class="cc-name"> <div class="cc-meta"> <div class="cc-progress"><i> <div class="cc-cta"> </button>`。
- 关键词：不要 `.ch-overview` 概览卡；不要 `data-go` 按钮两步操作；不要 `activeCid` 跟踪（每次进入都是列表），`launchChapterList` 直接调 `renderChapterNav(view, sid)` 无第三个参数。

### 考试离开守卫 + 静默交卷（防误触退出）
- `App.route()` 守卫：`Quiz.getState()` 判 `isExam && !completed && examRoute` → 弹 `App.confirm({title:'考试进行中', msg:'退出将视为交卷，确定离开吗？'})`。
- **确认** → `Quiz.gradeExamSilent()`（静默判分：记错题 + 标 completed + 停计时，**不渲染成绩单**）+ 清 `App.examRoute` + `App._doRoute()` 跳到目标页。
- **取消** → `history.replaceState(null, '', '#/' + examRoute)` 回退 URL（**不触发 hashchange**，不重渲染，答题进度完好）。
- `Quiz.gradeExamSilent()` 与 `renderExamComplete` 共用判分循环但跳过渲染；`S.completed=true` 标记在 `renderExamComplete` 顶部。
- `App.examRoute` 在 `launchPaperList` 入口置为 `'mock'` 或 `'real'`；确认后或成绩单渲染后清空。
- 需暴露 `Quiz.getState()` 供守卫读取当前会话；`Quiz.gradeExamSilent()` 暴露供守卫调用。

### 侧栏布局（已简化）
章节筛选抽屉已移除——所有章节切换通过侧栏两级导航完成。
桌面端 `#sidebar` 常驻；移动端通过 `#railToggle` 打开左侧抽屉，`#railOverlay` 为遮罩。
各页面不设独立章节下拉框。

### 收藏夹 · 单题翻页
- 使用 `Review.renderPaged(view, recs, 'favorite')`，每页只显示一道收藏题。
- 上/下一题按钮翻页；删除后自动调整到合理的相邻位置。
- 操作：⭐/☆ 收藏切换、取消收藏。无章节筛选下拉框。
- 顶部空态：「还没有收藏的题目 ⭐...」

### 错题本 · 单题翻页
- 使用 `Review.renderPaged(view, recs, 'mistake')`，每页只显示一道错题。
- 上/下一题按钮翻页；移除后自动调整位置。
- 显示：题型标签、章节名、错题次数、待巩固/已攻克状态、题目、已着色选项、正确答案+解析。
- 操作：⭐/☆ 收藏、移除错题。无章节筛选下拉框。
- 顶部空态：「还没有错题记录 🛠️...」

### 考试模式新特性（倒计时 / 常驻交卷 / 退出拦截 / 结束停留）
- **倒计时 + 交卷右上**：`.exambar`（顶部 bar）+ `.exam-timer` 每秒刷新；交卷按钮在右侧，`startTimer()` 在 `startItems` 里 `opts.isExam` 时启动，归零自动交卷。
- **常驻交卷按钮**：每道题底部都有「交卷」按钮，非仅末题；点击先 `confirm` 再 `submitExam`。
- **退出拦截**：侧栏跳转/浏览器后退时 `App.confirm({msg:'退出将视为交卷'})` → 确认交卷 / 取消停留；`beforeunload` 关页提醒。
- **结束行为**：练习（每日一练/章节刷题）末题提交后**停留当前题**（答案可见，无下一题按钮，无页面跳转）。考试交卷后停留成绩单（含逐题/错题回顾按钮）。

## 响应式布局模板（三档，复用即可）

所有页面遵循同一套断点，不另起布局：

| 端 | 断点 | 布局 | 要点 |
|-----|------|------|------|
| 桌面 Desktop | >1024px | 侧栏固定 + 主区两栏（`.nav-rail` / `.practice-main`） | 侧栏常驻可见，主区 `max-width` 居中 |
| 平板 Tablet | ≤1024px | 侧栏抽屉 + 主区单栏 | 侧栏通过 ☰ 按钮滑入（`.open`），`.rail-overlay` 遮罩 |
| 手机 Mobile | ≤640px | 全宽紧凑 | 按钮 `width:100%`，字号缩小，卡片 `padding` 减半 |

**实现**：三档通过 CSS `@media` 统一管理；`body{overflow-x:hidden}`；全局 `box-sizing:border-box`；`#view{margin:0 auto}` 居中。

**侧栏移动端**：
- `#railToggle` 按钮固定在顶栏（`display:none` on desktop，`display:block` on ≤1024px）。
- `#sidebar.open` + `#railOverlay.show` 双态。点 overlay 或侧栏链接 → `closeRail()` 自动收起。

## 错误态恢复 UI（双按钮模式）

当题目加载失败或数据为空时，不显示无操作的「空态」，而是展示可操作的 `state-box`：

```html
<div class="state-box">
  <span class="ico">📭</span>
  <div class="msg">题目数据未成功加载</div>
  <div class="sub">缓存或网络异常，请尝试重置后重试</div>
  <div class="state-actions">
    <button class="btn" onclick="location.reload()">刷新页面</button>
    <button class="btn ghost" onclick="indexedDB.deleteDatabase('exam_prep_db');location.reload()">重置缓存并刷新</button>
  </div>
</div>
```

**两处复用**：
1. `quiz.js render()` — items 为空时直接渲染 state-box（`__freshReload` / `__wipeReload`）
2. `app.js App.showError()` — 加载失败时加「重置缓存并重试」按钮（`__retry` / `__wipe`）

**`App.confirm` 通用弹窗**：标题 + 消息 + 确认/取消按钮，考试退出拦截 + 交卷确认共用。

## 全局错误监听（init 首行必加）

```js
window.addEventListener('unhandledrejection', function(e) {
  console.error('[exam-prep] ', e.reason);
});
window.addEventListener('error', function(e) {
  if (e && e.error) console.error('[exam-prep] ', e.error.stack);
});
```

## 关键 CSS class 清单（复用需引对应样式）

### 考试模式
| class | 用途 |
|-------|------|
| `.exambar` | 考试顶部条（计时 + 交卷，flex 两端对齐，交卷按钮在右上）|
| `.exam-timer` | 倒计时数字（大号等宽字体，变红预警）|
| `.exam-timer-wrap` | 计时区域容器 |

### 完成页
| class | 用途 |
|-------|------|
| `.action-group` | 完成页操作按钮行（「返回备考中心」+ 重做等）|

### 错题本底部行
| class | 用途 |
|-------|------|
| `.mb-actions` | 错题/收藏底部操作行（收藏 + 移除/取消 + 上/下一题），水平 flex 布局 |
| `.mb-page` | 错题/收藏翻页计数（第 n/m 题）|
| `.kb-single` | 知识卡单卡容器（`.flashcard` + `.stage-nav`）|

### 错误 / 加载态
| class | 用途 |
|-------|------|
| `.state-box` | 错误/空态容器（居中 + padding + 图标 + 消息）|
| `.state-actions` | 错误态按钮行（flex + gap + 居中）|
| `.loading-box` | 加载态（spinner + 文案居中）|
| `#__retry` | 「重新加载」按钮 |
| `#__wipe` | 「重置缓存并重试」按钮 |
| `#__freshReload` | render 空态「刷新页面」按钮 |
| `#__wipeReload` | render 空态「重置缓存并刷新」按钮 |


> 回归：重设计后务必 `node --check` 三个模块 + 跑 smoke；确认无裸 `App.`/`Storage.`（必须 `QuizApp.*`）。

## 错题 / 收藏全模式联动（关键约定）

**所有练习模式（每日一练 / 章节刷题 / 模拟题 / 真题模考）共用同一套答题与收藏逻辑，错题和收藏全模式联动，不存在「每日一练答错不进错题本」之类的孤岛。**

实现要点：
- **共用 `submitAnswer(q)`**：所有模式走同一个提交函数。客观题答错时（`!isCorrect`）立即调 `Storage.addMistake({ questionId, subjectId, chapterId, userAnswer, correctAnswer, questionData })`，**幂等 by questionId**（重复答错不重复入库）。每日一练答错 → 自动进错题本。
- **共用 `renderQuestion(q)`**：所有模式走同一个题目渲染函数，收藏按钮 `onclick` 调 `Storage.toggleFavorite(q)`，切换收藏态 + 刷新 badge + toast 提示。每日一练点收藏 → 加入收藏夹。
- **考试模式（mock/exam）交卷时**：`submitExam` / `renderExamComplete` 批量把客观题错题写入错题本（同样幂等 by questionId），保证「重做错题」可用。
- **主观题永不进错题本**：主观题（简答/论述/作文）只展示采分点 + 参考答案，不判分、不入错题。
- **badge 实时刷新**：每次 addMistake / toggleFavorite 后调 `App.refreshBadges()`，侧栏/底部栏的错题、收藏角标即时更新。

> 规则：任何新增练习模式必须复用 `submitAnswer` + `renderQuestion`，不得另起一套答题逻辑，否则会破坏错题/收藏联动。

**错题「攻克」语义（P6，必做）**：错题本是「待巩固集合」而非「待删集合」。
- 客观题答对 → `Storage.markConqueredIfExists(qid)`（标记 `status:'conquered'`，**保留记录**便于追溯）；标题 N 用 `Storage.activeMistakeCount()`（未攻克数）。
- 客观题答错 → `Storage.addMistake(rec)`（**幂等 by questionId**，重复答错只 `wrongCount++`，已攻克再错退回 `active`）。
- **主观题永不入册**；**未作答（sel 为空）先 `toast` 拦截，不入册**。
- 列表页提供「未攻克 / 已攻克」分段 +「清空全部」(`confirm` 保护)。模板见 `storage-mistake-conquer.js` 与 `quiz-submit-conquer.js`。

## Progress & silent resume
- Store per `(userHash, module, chapter)`: `{ currentIndex, answeredQuestions, isCompleted, savedAt }`.
- On re-entry: resume silently (set `currentIndex`, re-render) + `toast('已恢复进度 …')`. Never block with a confirm dialog.
- Add `savedAt: Date.now()` on every save; resume the max-`savedAt` item, never "first incomplete".
- For review modules, switching content is handled by the two-level sidebar nav (no per-page filter).

> 成绩单结构详见「考试模式新特性」与「考试离开守卫」章节；知识卡交互详见「知识卡 · 左筛选 + 右翻转闪卡（纯点击）」。

## Auth: whitelist with auto nickname (SHA-256 hashed phone)

Phone → SHA-256 hash → whitelist hash compare. Whitelist stores only phone hashes + nickname mapping
(never plaintext phones) so users never type a nickname. Full spec: see `references/whitelist-nickname.md`.

- Whitelist format: `{ "entries": [{ "hash": "sha256hex", "name": "昵称" }] }` (compat: `{ "hashes": [...] }`).
- `Auth.login(phone)` → `Crypto.sha256(phone)` → `isWhitelisted(phoneHash)` → `getNameFromHash(phoneHash)` auto-reads nickname; no manual nickname input.
- Login dialog subtitle (standard copy):「输入手机号（仅本地记录，不上传），系统生成你的专属学习档案」. Only a phone input field, no nickname field.
- `Auth.getDisplayName()` returns nickname or default (e.g. 备考学员); **never show raw/masked phone in UI**.
- 用户区（`你好！{昵称}` + 退出 / `登录` 按钮）统一放在主区顶部栏**右上角**（`#topbar` 内的 `#userBox`，`margin-left:auto`）。**禁止在侧栏底部放用户卡**——曾把 `#userBox` 塞进 `.side-foot` 导致出现「左下角登录按钮」，已纠正。☰ 菜单按钮放在顶部栏左侧，移动端内联显示（不要做成左下角浮窗）。
- Per-user data isolation: `Storage` prefix `qb_{hash8}_` (first 8 chars of phone SHA-256 hash).
- `js/crypto.js` provides `sha256(msg)` + `hashPrefix(msg)`; `tools/gen-hash.html` is a browser tool for admins to generate hashes from phone lists.

## First-screen init (critical)
- NEVER put nav binding, route (hashchange) listeners, or first paint inside an async data `fetch().then()`. On slow mobile networks this makes the whole page unclickable until a manual refresh (cache hit).
- Do: render the nav skeleton + bind events + paint a dashboard shell **synchronously**, set an `_initDone` flag up front, then backfill data async and re-render the current route.
- Use `DataStore.loadData()` (fetches `questions.json` once, caches the promise).
- Add an 8s timeout (AbortController) to fetches and degrade to empty data on failure so the UI never hangs blank.

## Testing workflow
- jsdom smoke tests in a TEMP dir (not the project). Run with managed Node, `NODE_PATH=node_modules`.
- Divs aren't buttons: fire `dispatchEvent(new Event('click'))` or assert element presence.
- `node --check` every edited file before deploy. Aim for a baseline regression suite (e.g. 20+ cases) kept passing.

## Deployment

### Preferred: CloudStudio sandbox (zero-config)
Deploy a clean static dir (only `index.html` + `css/` + `js/` + `data/`) via `workbuddy_cloudstudio_deploy`.
- Gateway auto-sets correct Content-Type for all files — no MIME issues.
- Fresh sandbox URL has no cache history — users see full styles on first open.
- URL stable across redeploys (same sandbox) or changes (new sandbox).

### Alternative: Tencent COS anonymous bucket
For custom domain / long-term stable link. **Read `references/cos-pitfalls.md` first** — it documents
a 5-layer bug chain (createReadStream empty file on Windows Chinese paths, CDN ignoring query params,
bare-path empty-file deadlock, etc.). Key rules if using COS:
- Use `fs.readFileSync` (NOT `createReadStream`) + explicit `ContentType`.
- Use filename-hash cache-busting (`style.<hash>.css`), NOT query-param `?v=` (CDN ignores it).
- Upload both hash path (immutable 1y) AND bare path (no-cache) to break empty-file cache deadlock.

## Reusable scripts (bundled)

> Note: `js/crypto.js` (SHA-256) and `tools/gen-hash.html` (admin hash generator) are required —
> the whitelist stores phone SHA-256 hashes (never plaintext) and compares hashes on login.
> **crypto.js 未随包附带**——完整实现（含 `>>>` mod-32 修复的注释）见 `references/templates/crypto-sha256.js`，
> 直接复制到消费项目的 `js/crypto.js`。核心陷阱：JS 位运算位移量按 mod 32 取模，64 位长度必须
> 高低 32 位分开编码（`Math.floor(l/0x100000000)` + `l>>>0`），否则"空串正确，非空串错误"。

## Reuse checklist for a new exam
0. **先跑前置问题（见上方 ⛔ 一节）**：用 `AskUserQuestion` 确认 Q1–Q10，拿到确认后再开始下面 1–12 步。跳过问询直接搭 = 违反强制规则。
1. Define `Data` shape (subjects/chapters/questions) + `type` enum (incl. subjective types).
2. Define `Data` shape in `data/questions.json`. Use `DataStore.loadData()` (single fetch, cached promise). All modules call `DataStore.loadData().then(...)` at entry.
3. Wire the dashboard (备考中心, default landing page) + learning modules; implement silent resume + `savedAt`.
4. **Ensure mistake/favorite cross-mode linkage**: all practice modes share `submitAnswer` (wrong → `addMistake`, idempotent by questionId) + `renderQuestion` (fav btn → `toggleFavorite`); call `App.refreshBadges()` after each. No mode-specific answer logic.
5. Build the two-level sidebar nav (`.has-sub > .nav-parent + .nav-sub`) + `buildSidebar()` after `loadData()`. Mobile folding sidebar (`#sidebar` / `#railToggle` / `#railOverlay`). No per-page chapter filter dropdowns.
6. Wire exam exit guard + 考试模式（提交自动跳题不显示答案）+ 结果页（正确率环 + 薄弱章节 + 逐题/错题回顾按钮进入单题浏览模式，末题返回结果页）。
7. Add whitelist login with auto nickname (`references/whitelist-nickname.md`); generate SHA-256 hash per phone and write `{hash, name}` into `data/whitelist.json` (never store plaintext phones). Copy `crypto-sha256.js` template.
8. Add jsdom smoke tests; deploy (CloudStudio preferred); record the URL in project memory.
9. **Hardening pass**: read `references/pitfalls.md`; copy the templates from `references/templates/` (auth-whitelist-guard, idb-loadindex-singleton, idb-cache-guards, crypto-sha256, storage-mistake-conquer, quiz-submit-conquer, app-global-subject); grep for bare `App.`/`Storage.` (must be `QuizApp.*`); run jsdom smoke suite covering the 14 regression points in pitfalls.md.
10. **JSON safety (P5)**: any generated data file (`questions.json` / `knowledge.json` / `whitelist.json`) MUST be produced by a script (`json.dump` / `JSON.stringify`), never hand-written or LLM-streamed into a `.json`; validate with `JSON.parse` after writing.
11. **Global subject (P7)**: add `#subjbar` to `index.html` and wire `App.getSubject/setSubject`; ensure every list page scopes by the global subject and only filters by chapter.
