# 故障与修复清单（Hard-won fixes）

本文件记录了在真实项目中踩过、并已修复的坑。**每次用本 skill 构建/重构系统时，先读本文**，
把对应的规范实现直接复制到新项目，避免重复踩坑。每个条目都给出：现象 → 根因 → 规范修复
（可直接复制的代码片段见 `../templates/`）。

---

## P1 · 白名单登录失败（file:// 拦截 + 竞态）

**现象**：输入白名单手机号总提示「不在授权范围」；或每日一练偶发抽不到题。
**根因（三层）**：
1. 用户直接 `file://` 打开页面时，`fetch('data/whitelist.json')` 被浏览器拦截/CORS 失败，
   白名单永远为空 → 任何手机号都判不在范围内。
2. 登录弹窗打开时白名单还没加载完（`Auth.loadWhitelist()` 是异步的），用户点「登录」时
   `whitelistCache` 仍为 `null` → `Auth.login` 直接返回「白名单未加载，请稍候再试」或误判不在范围。
3. `DataStore.loadIndex()` 被多个模块并发调用，多个 Promise 各自 `fetch` 后覆盖已水合的
   `Data.subjects`，导致某个章节题目被清空（每日一练抽不到题）。

**规范修复**：
- auth.js：内置 `BUILTIN_WHITELIST` 兜底 + `loadWhitelist().catch(兜底)`，文件读不到也能登录；
  提供 `isWhitelistReady()` 守卫；`login()` 在 `whitelistCache` 为空时返回友好提示而非误判。
- app.js `openLogin()`：白名单未就绪时**禁用**提交按钮并提示「加载中」，就绪后再启用（见 templates/app-global-subject.js）。
- idb.js `loadIndex()`：用 `_indexPromise` 单例，整库只加载/赋值一次（见 templates/idb-loadindex-singleton.js）。

> 关键：白名单文件是「可选增强」，本地直开必须能跑。兜底清单只用于离线/直开场景，
> 正式 `whitelist.json` 存在时以文件为准（便于管理员增删，见 whitelist-nickname.md）。

---

## P2 · 登录/解析弹窗关闭后仍显示、点击无反应（浏览器缓存旧 JS）

**现象**：登录成功后遮罩层仍在、点别的区域没反应；或改了 JS 但页面表现不变。
**根因**：
1. 隐藏遮罩依赖 `.hidden { display:none }`，但某些浏览器对 `hidden` 属性 + `display` 覆盖顺序
   处理不一致，旧样式没生效，遮罩层其实是「半透明但仍挡住点击」。
2. 部署后浏览器缓存了旧 `app.js`/`auth.js`，新逻辑没生效。

**规范修复**：
- CSS 顶层加一条强制规则，确保 `hidden` 永远隐藏遮罩/弹窗：
  ```css
  .hidden, [hidden] { display: none !important; }
  ```
- `index.html` 所有 `<script>`/`<link>` 加版本号查询串 `?v=N`（每次发版 +1）。
  注意：仅 CloudStudio 部署用 `?v=`；若走 COS 见 cos-pitfalls.md（要用文件名哈希而非查询串，CDN 忽略 `?v=`）。

---

## P3 · `loadIndex` 并发覆盖（每日一练偶发抽不到题）

见 P1 根因 3。修复见 templates/idb-loadindex-singleton.js：用模块级 `_indexPromise`
缓存首次调用返回的 Promise，后续调用直接复用，杜绝并发赋值覆盖。

---

## P4 · 裸 `App` 全局引用（jsdom 冒烟捕获）

**现象**：`xxx.js` 里写 `App.refreshBadges()` / `App.showAnalysis()`，本地偶发 `App is not defined`，
冒烟测试直接挂。
**根因**：skill 约定所有模块挂在 `QuizApp` 命名空间下（`QuizApp.App`、`QuizApp.Storage`…），
但个别模块误用裸 `App`（依赖 app.js 里的局部变量泄露到全局，不可靠）。
**规范修复**：任何模块一律用 `QuizApp.App`、`QuizApp.Storage`、`QuizApp.DataStore`、…，
**绝不用裸 `App`/`Storage`**。jsdom 冒烟测试（见 SKILL.md Testing workflow）能稳定抓到这类问题。

---

## P5 · knowledge.json 被写坏（LLM 流式写入未转义引号）

**现象**：`data/knowledge.json` 含未转义引号/`\n`，`JSON.parse` 报错，知识卡整页崩溃。
**根因**：用 LLM 流式「直接写文件」生成 JSON，正文含大量双引号与换行，代理中断或拼接时
漏转义，产出非法 JSON。
**规范修复**：**JSON 一律用脚本生成**，不要手写/流式拼接到 `.json` 文件：
- 用 Python `json.dump(obj, f, ensure_ascii=False, indent=2)` 输出；
- 或用 Node `fs.writeFileSync(path, JSON.stringify(obj, null, 2))`；
- 正文里的 HTML（含 `<mark>` 高亮）放在字符串字段里，由 `json.dump` 自动转义，绝不在模板里手拼引号。
- 生成后跑一次 `node -e "JSON.parse(require('fs').readFileSync('data/knowledge.json'))"` 校验。

---

## P6 · 错题「删除」而非「攻克」，且主观题/空白误入册

**现象**：重做对了的错题仍留在错题本；主观题、未作答的题也进了错题本。
**根因**：旧逻辑把错题当「待删集合」，答对就 `removeMistake`；主观题与空白也调了 `addMistake`。
**规范修复**（见 templates/storage-mistake-conquer.js + templates/quiz-submit-conquer.js）：
- 错题本用「攻克」语义：`addMistake` 幂等（重复答错只 `wrongCount++`），`markConquered` 标记
  `status:'conquered'` 但**保留记录**（历史可追溯）；标题 N 用 `activeMistakeCount()`（未攻克数）。
- quiz.js `submitAnswer`：客观题答对 → `markConqueredIfExists`；答错 → `addMistake`；
  **主观题永不入册**；**未作答（sel 为空）不入册**（先 `toast('请先选择答案')` 拦截）。
- 列表页提供「未攻克 / 已攻克」分段切换 +「清空全部」（带 `confirm`）。

---

## P7 · 每页各自科目下拉 → 改为全局科目选择器

**现象（需求纠正）**：用户在「备考中心上方」要一个**常驻科目下拉**，其它模块都按所选科目呈现数据；
而不是每个列表页各自放科目+章节两级下拉。
**根因**：最初把「统一筛选」做成每页两级下拉，偏离需求；且多模块各自维护科目下拉导致状态分散。
**规范修复**（见 templates/app-global-subject.js）：
- 顶部 `subjbar`（**必选、常驻**，放在主区顶部 `<div id="topwrap">` 内，系统标题下方、内容上方，桌面+移动端都可见）放一个**全局科目**下拉（仅多科目时显示，单科目自动隐藏）；**不要放进侧栏抽屉**（移动端默认隐藏，用户看不见）。
- `App.currentSubject` + `getSubject()/setSubject()` 是全局唯一科目来源；`setSubject` 时
  `renderGlobalSubject()` + `route()` 重渲染当前页。
- 列表页（错题本/收藏夹/知识卡/章节）**只做章节筛选**（章节是该科目的子集），数据用
  `Storage.mistakesForSubject(sid)` / `favoritesForSubject(sid)` 按全局科目限定。
- 单科目时：全局科目下拉隐藏，列表页章节下拉也仅在该科目多章节时显示。

---



---

## P8 · 旧 IndexedDB 分片毒缓存 → 部署后各模块空题（致命·高频）

**现象**：更新代码/题库后重新部署，旧链接硬刷新仍然所有模块显示"没有可练习的题目"。
**根因（两层联动）**：
1. `ensureChapter` 读取 IndexedDB 分片时，缓存守卫 `if(cached && cached.questions)`——
   **空数组 `[]` 在 JS 是 truthy**。历史版本写入的 Key 仍可命中，`cached.questions` 为空数组照样
   通过守卫，章节被标记为 `_hydrated`，永远不再回源网络。
2. `INDEX_VER` 升版只让 `shard_v<N>_*` 键失效——**但若上一层部署已把旧键种成了毒缓存（如空分片），
   `INDEX_VER` 加 1 只是给新键起了新名字，旧毒键落在 DB 里占空间（非 Bug，但事后排查易混淆）。
**规范修复（双重）**：
- `INDEX_VER` 每次部署时 +1（两处同步：`idb.js` + `build-shards.js`），直接使所有旧键失效。
- 分片缓存守卫改为 **`cached && Array.isArray(cached.questions) && cached.questions.length`**（必须 >0 条题目才算有效）。
- Index 缓存守卫同步加强：`cached.subjects.every(s => Array.isArray(s.chapters) && s.chapters.length > 0)`——防「subjects 数组在但各章题数为 0」的结构化毒缓存。
> 预定义 guards 模板：见 `templates/idb-cache-guards.js`（提供可复制的 loadIndex + ensureChapter 守卫代码）。

---

## P9 · HTTP 缓存毒化 `data/*.json` → CDN/浏览器返回旧空文件（致命·隐蔽）

**现象**：硬刷新 + 清 IndexedDB 后仍空题；线上 `data/index.json` 可达却无法在真机加载。
**根因**：
1. 某次部署中 `data/*.json` 返回 404/空响应，浏览器 HTTP 缓存了该响应（ETag/304）。
2. `INDEX_VER` 只能清 IndexedDB，**不能**清 HTTP 缓存。
3. `fetch(url)` 不设 `cache` 模式时，浏览器可返回内存/磁盘缓存的旧值。
**规范修复**：
- `fetchJSON(url)` 里加 **`Object.assign({cache:'no-store'}, opts)`**（不允许浏览器/代理缓存）。
- 仍担心 → 再加 URL 时间戳：`url + '?_=' + Date.now()`，物理层面绕过所有缓存层。
```js
function fetchJSON(url) {
  var ctrl = new AbortController();
  var to = setTimeout(function(){ctrl.abort();},8000);
  var u = url + '?_=' + Date.now();
  return fetch(u, Object.assign({cache:'no-store'},{signal:ctrl.signal}))
    .then(function(r){...});
}
```
> 注意：加 `?_=` 后 jsdom 测试里的 fetch mock 必须 `url.split('?')[0]` 或 `replace(/\?.*$/,'')`。

---

## P10 · 真机 fetch/IDB 错误全丢失 —— 零全局错误监听（隐蔽）

**现象**：代码逻辑在 jsdom 测试全绿，真机 Chrome 加载分片时静默失败（页面无任何报错），"无题" 排查无任何线索，只能盲猜缓存/网络。
**根因**：生产代码**无任何全局错误监听**（无 `unhandledrejection` / `window.onerror`）。`prefetch` 用 `.catch(()=>{})` 吞掉 ensureSubject 失败；`startPaper` 无 `.catch`；真机的 fetch 失败/IDB 异常/分片 parse 错误全部静默消失。
**规范修复**：`app.js` `init()` 首行添加：
```js
window.addEventListener('unhandledrejection', function(e) {
  console.error('[exam-prep] ', e.reason && (e.reason.stack || e.reason));
});
window.addEventListener('error', function(e) {
  if (e && e.error) console.error('[exam-prep] ', e.error && e.error.stack);
});
```
从此任何真机失败都会在控制台暴露完整堆栈，一招终结「bug 只出现在真机但定位不了」的困局。

---

## P11 · 健康自检假阴性 —— prefetch 异步未完成就统计题目数

**现象**：页面加载后 console 打印 `questions(已 hydrate)=0`，误以为题库加载失败，实际题库是好的。
**根因**：在 `prefetch()` 触发后**立即**遍历 `Data.subjects[i].chapters[j].questions` 统计——但 `prefetch` 通过 `requestIdleCallback` / `setTimeout` 异步调用 `ensureSubject`，此时章节尚未 hydrate，`c.questions` 全空（假阴性）。
**规范修复**：自检必须等 `ensureSubject` 完成后再统计：
```js
DataStore.ensureSubject(App.getSubject()).then(function() {
  var questions = 0;
  (Data.subjects || []).forEach(function(s) {
    (s.chapters || []).forEach(function(c) { questions += (c.questions || []).length; });
  });
  console.log('[exam-prep] questions=' + questions);
  if (questions === 0) console.error('[exam-prep] hydrate 失败！');
});
```

---

## P12 · 空题静默 —— 无恢复入口，用户卡死

**现象**：当所有加载通道都失败时，页面仅显示「📭 没有可练习的题目」，无任何恢复入口。
**规范修复**：`render()` 空题态改为可操作的 `state-box`（含「刷新页面」+「重置缓存并刷新」两个按钮：`location.reload()` 和 `indexedDB.deleteDatabase() + location.reload()`）。同时 `App.showError` 补一个「重置缓存并重试」按钮。

---

## P13 · 考试模式页面白屏 —— startPaper 前置 `S.isExam` 崩

**现象**：点击模拟/真题试卷后页面白屏，控制台 `Cannot set properties of null (setting 'isExam')`。
**根因**：`S`（会话对象）在 `startItems` 内部才初始化，在 `Quiz.startPaper` 顶部调 `S.isExam = true` 时 `S` 为 `null`。
**规范修复**：不要在 `startPaper`/`startDaily` 顶部提前操作 `S`——考试态标志通过 `startItems` 的 `opts.mode==='exam'` 传入，在 `startItems` 内部设 `S.isExam` + `S.deadline`。

---

## P15 · 路由未开始答题时调用 `stopTimer()` 崩（P13 同类）

**现象**：未进入任何答题页（`S` 为 `null`），点击侧栏切换路由时页面崩溃，控制台 `Cannot read properties of null (reading 'timer')`。
**根因**：`App.route()` 或 `closeRail()` 等路由切换路径中无守卫调了 `Quiz.stopTimer()`，而该函数内部直接读 `S.timer`——`S` 未初始化时为 `null` → 空指针崩溃。
**规范修复**：`stopTimer()` 内部加守卫：
```js
function stopTimer() { if (S && S.timer) { clearInterval(S.timer); S.timer = null; } }
```
**口诀**：所有操作 `S` 内部属性的函数（`stopTimer` / `cache` / `submitAnswer` 等）首行必判 `if(!S) return;`。与 P13（`startPaper` 前置操作 `S`）同源——不要在 `S` 未就绪时访问其属性。

> 关联 P13：二者本质是同一类——「在 S 初始化前或不使用 opts 方式操作 S」。规范做法：所有 S 的初始化都走 `startItems(opts)`；对外暴露的函数在访问 S 内部属性前必须判 null。

---
## P14 · 错题本收藏按钮报错 `ReferenceError: q is not defined`

**现象**：错题本里点收藏（☆/⭐）按钮无反应，控制台 `ReferenceError: q is not defined`。
**根因**：`mistake-book.js` 里 `q` 是 `Mistakes.render` 函数的**局部变量**（`var rec = list[st.idx], q = rec.questionData`），但 `wireCard` 是**模块级函数**，闭包无法访问 `q`。`wireCard` 里写 `Storage.toggleFavorite({questionData: q})`——`q` 在此作用域下为 `undefined`。
**对比**：`favorites.js` 使用 `rec.questionData` 而非局部变量 `q`，所以无此 bug。
**规范修复**：所有 `wireCard` / `wireButtons` 等事件绑定函数，**不要引用外部模块函数的局部变量**。改用已传入的对象属性（如 `rec.questionData`）：
```js
// ❌ 错误：q 是外部函数的局部变量
function wireCard(view, rec, list) {
  el.onclick = function() { Storage.toggleFavorite({questionData: q}); }; // q = undefined!
}
// ✅ 正确：用已传入的对象属性
function wireCard(view, rec, list) {
  el.onclick = function() { Storage.toggleFavorite({questionData: rec.questionData}); };
}
```
> **检测建议**：jsdom 烟雾测试无法捕获此 bug（`wireCard` 绑定时不会立即触发 onclick），需用 `el.dispatchEvent(new MouseEvent('click'))` 并断言按钮状态变化（参考 tests/probe_fav.js）。

## P16 · 纯 JS SHA-256 长度字段大端编码错误 → 白名单登录全失败（隐蔽·致命）

**现象**：`Crypto.sha256(手机号)` 与标准 SHA-256 不一致（如 `sha256('abc')` 得到 `3859a4ec…` 而非 `ba7816bf…`）。后果：手机号哈希与白名单 `entries[].hash` 永远对不上，登录在**所有环境**（含浏览器，非仅测试）全部失败；且 `Storage` 用户隔离前缀 `hashPrefix()` 也跟着错。

**根因**：`crypto-sha256.js` 模板里 64 位长度字段的编码同时犯了两个错：
1. **字节序写反**：把低 32 位(bitLen)塞进字节 8..11、高 32 位(lenHi)塞进字节 12..15——而 SHA-256 要求先高后低的大端序。
2. **半内也小端**：每个 32 位内部又按 `>>>((3-j)*8)` 反向取字节，变成小端。

双重错误使 `w[14]/w[15]` 被污染，非空串哈希必错。**空串长度=0 恰好全 0 自愈**，所以只测 `sha256('')` 会被完全蒙蔽，极易漏检。

**规范修复**（`references/templates/crypto-sha256.js` 已修正）：
```js
var lenHi = Math.floor(bitLen / 0x100000000); // 高 32 位
var lenLo = bitLen >>> 0;                       // 低 32 位（>>>0 关到无符号 32 位，避开 mod-32）
// 高 32 位 → 字节 8..11（大端）
for (var j = 3; j >= 0; j--) bytes.push((lenHi >>> (j * 8)) & 0xff);
// 低 32 位 → 字节 12..15（大端）
for (var j = 3; j >= 0; j--) bytes.push((lenLo >>> (j * 8)) & 0xff);
```
> ⚠️ 若部署目标浏览器支持 `crypto.subtle`，应优先用原生 `SubtleCrypto.digest`（模板当前为纯 JS 兜底路径）；但纯 JS 路径必须保证与标准一致。

**检测建议**：jsdom 烟雾测试必须断言 `Crypto.sha256('abc') === 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'`（标准向量），并用多用例（含非空串、长串、中文）与 Node `crypto.createHash('sha256')` 对齐；同时断言 `Auth.login('13800138000').ok === true`（白名单哈希由标准 SHA-256 生成）。

## P17 · 业务模块在 IIFE 顶部 `var App = QuizApp.App` 捕获到 undefined（章节题直接崩 + 昵称错乱）

**现象**：点击章节卡片进入刷题时 `Quiz.startChapter` 抛 `TypeError: Cannot read properties of undefined (reading 'showLoading')`；知识卡 `Knowledge.render`、错题本收藏 `Review` 同样在 `App.xxx` 上崩。若仅在登录态下观察，还会看到「登录成功却右上角昵称变『备考学员』」的割裂（见 P18）。

**根因**：脚本加载顺序固定为 `crypto → storage → auth → idb → quiz → knowledge → review → app`（app.js 是路由/入口，必须最后加载，因为它在末尾才 `QuizApp.App = App`）。于是 quiz/knowledge/review 在各自 IIFE 顶部执行 `var App = QuizApp.App` 时，捕获到的 `App` 是 `undefined`。等到用户点击触发 `Quiz.startChapter`，函数体内 `App.showLoading(...)` 才执行 → 崩。`Storage`/`Auth`/`DataStore` 因为加载更早（storage/auth/idb 都在 quiz 之前），捕获有效，所以不崩——**只有 `App` 因 app.js 垫后而必崩**。

**规范修复**：业务模块内一律用 `QuizApp.App.*` 直接引用（这与 skill 模板 `references/templates/quiz-submit-conquer.js` 的写法完全一致：`QuizApp.App.toast(...)` / `QuizApp.App.refreshBadges()`），**禁止** `var App = QuizApp.App` 这类加载期捕获。`Storage`/`Auth`/`DataStore` 因为加载顺序在其前，可继续按加载顺序捕获（或同样统一改 `QuizApp.*` 以求一致）。

> ⚠️ P4 的 grep 只能抓到「裸 `App.`」，抓不到 `var App = QuizApp.App`（此处 `App` 后接空格）。必须额外 grep `var App = QuizApp\.App` 或直接运行时断言 `!!(QuizApp.App && QuizApp.App.toast)`。

**检测建议**：jsdom 烟雾测试里真实驱动登录弹窗（点 `loginOk` → `doLogin` → `renderUser`），并断言 `userBox` 含「你好！<昵称>」；再进入章节卡片断言 `.opt` 渲染、提交后 `qNext`/`.reveal` 出现；进入知识卡断言 `.flashcard` 存在。

## P18 · `Auth.getDisplayName` 只按 `phone` 查昵称 → 白名单仅存 `hash` 时永远查不到（昵称退化「备考学员」）

**现象**：登录成功（isLoggedIn 为 true、显示「退出」按钮），但右上角/备考中心问候语是「你好！备考学员」而非「你好！张三」。

**根因**：`getDisplayName()` 仅 `getNameByPhone(p)` 遍历 `whitelistCache.entries` 匹配 `e.phone === phone`；而 `gen_whitelist.js` 输出只含 `{hash, name}`（遵循「不存明文手机号」），**无 `phone` 字段** → 永远 `null` → 兜底「备考学员」。与此同时 `login()` 用 `getNameFromHash(sha256(phone))` 能查到昵称，于是出现「`login` 成功返回张三，但 `getDisplayName` 拿不到」的割裂。

**规范修复**：`getDisplayName` 与 `login` 解析路径一致——先 `getNameByPhone`，再回退 `getNameFromHash(QuizApp.Crypto.sha256(p))`：
```js
Auth.getDisplayName = function () {
  var p = Auth.getCurrentPhone();
  if (!p) return '备考学员';
  var name = Auth.getNameByPhone(p) || Auth.getNameFromHash(QuizApp.Crypto.sha256(p));
  return name || '备考学员';
};
```
（白名单只存 `hash+name` 是符合隐私设计的，不要为修这个 bug 而往白名单塞明文 `phone`。）

**检测建议**：jsdom 断言白名单就绪后 `Auth.getDisplayName()` 返回正确昵称；登录驱动后 `userBox` 文本匹配 `/你好！张三/`。

## 冒烟测试须覆盖的回归点

每次发版前用 jsdom 跑（参考 SKILL.md Testing workflow）：
1. `loadIndex` 并发 3 次调用后 `Data.subjects` 仍完整（P1/P3）。
2. 白名单未就绪时登录被拦截；就绪后可登录（P1）。
3. `hidden` 遮罩 `display==='none'`（P2）。
4. 裸 `App` 引用为 0（P4，grep 校验）；额外 grep `var App = QuizApp\.App` 必须为 0（这种写法 `App` 后接空格，P4 的 `App.` grep 抓不到，却是 P17 崩因）；业务模块改统一用 `QuizApp.App.*`。
5. `knowledge.json` 可 `JSON.parse`（P5）。
6. 答对 → `activeMistakeCount` 不增且该题 `status==='conquered'`；答错 → 幂等累加（P6）。
7. 多科目时 `subjbar` 可见、切换后列表数据随之变化；单科目时隐藏（P7）。
8. IndexedDB 空分片守卫生效（P8）：`ensureChapter` 返回空 questions 时自动回源网络。
9. `fetchJSON` 含 `cache:'no-store'`（P9）：抓包确认无 304 缓存命中。
10. `window` 有 `unhandledrejection` + `error` 全局监听（P10）。
11. 分片加载完成后 `questions(已 hydrate) > 0`（P11：不可在 prefetch 未完成时统计）。
12. 空 items 时渲染「刷新页面」+「重置缓存并刷新」按钮，不显示无操作的「没有可练习的题目」（P12）。
13. 错题本收藏按钮点击后 `isFavorite` 正确切换，无 `ReferenceError`（P14）。
14. `Quiz.stopTimer()` 在 S 为 null 时不崩溃（P15）。
15. `Crypto.sha256('abc')` 等于标准向量 `ba7816bf…f20015ad`（P16）；`Auth.login('13800138000').ok === true`（白名单哈希由标准 SHA-256 生成，纯 JS 路径必须正确）。

16. `fetchJSON` 主请求带 `?_=` 缓存爆破，对带 `?_=` 返回非 ok 时自动回退无查询串原 URL（P19）：否则 CloudStudio 这类托管对查询串偶发 404，会让 `index.json`/分片整包失败、`subjects` 变空、所有按科目查数据的功能全挂。
17. 主观题判定统一用 `isSubjective(q)`（short/essay），禁止 `q.type === 'subjective'`（P20）：数据里主观题类型是 `short`/`essay`，无 `subjective` 值，旧写法使主观题被当客观题判分、错进错题本、结果页不显示采分点/参考答案。
18. 实机点击选项应出现 `.opt.sel` 高亮；考试答题时应可正常点选；提交后练习应显示 reveal、考试应自动跳下一题无 reveal（P21）。

## P19 · `fetchJSON` 缓存爆破 `?_=` 在部分静态托管（CloudStudio）对带查询串 URL 偶发 404
**现象**：部署到 CloudStudio 后每日/章节/模考/真题全部「加载失败」「该科目暂无边卷」，科目下拉消失；本地 jsdom 与 IDB 复现均正常。
**根因**：P9 规范要求 `fetchJSON` 给 URL 拼 `?_=时间戳` 绕过 HTTP 缓存，但 CloudStudio 网关对带查询串的静态文件偶发返回 404（冷边缘节点尤甚），`index.json?_=`/`shards?_=` 抽风失败。
**修法**：`fetchJSON` 主请求带 `?_=`；`response.ok` 为 false 或抛错时，回退请求**无查询串**原 URL（`cache:'no-store'` 已保证不读浏览器缓存，P9 意图不丢）。正常主机仍走爆破，不认查询串的托管自愈。
**检测建议**：jsdom 用「带 `?_=` 必 404、干净 URL 才 200」的仿真 fetch 垫片，断言 `loadIndex` 仍能取到 `subjects`、`ensureChapter` 能取到分片；或冒烟测试里强制 `?_=` 永 404 验证回退。

## P20 · 主观题类型误判：`q.type === 'subjective'` 永远为假
**现象**：主观题（简答/论述/作文）在练习/考试/错题本/收藏夹里被当客观题处理——`isCorrect` 拿 `undefined` 答案比永远判错、被错塞进错题本（违反「主观题永不进错题本」）、结果页不显示采分点/参考答案、答对率统计异常。
**根因**：数据里主观题类型是 `short` / `essay`，**不存在 `subjective` 这个值**；代码却到处用 `q.type === 'subjective'` 判断主观题，条件恒假。
**修法**：新增 `function isSubjective(q){ return !!q && (q.type === 'short' || q.type === 'essay'); }`，`quiz.js`（`submit`/`gradeSilent`/`rateText`/`renderExamComplete`/`fillReview`/`renderReveal`）与 `review.js`（`renderRevealRO`）所有 `q.type === 'subjective'` / `!== 'subjective'` 全部替换为 `isSubjective(q)` / `!isSubjective(q)`。
**检测建议**：jsdom 跑一套含 short/essay 的试卷交卷，断言 `S.answers[主观题id].correct === true`、结果页该卡显示「不判分」+采分点+参考答案、且未被写入错题本。

## P21 · 选中态读错字段：`renderBody` 用 `S.answers` 判选中而非 `S.sel`

**现象**：点击选项后按钮无任何高亮变化，用户反馈"点不动""选项没反应"——实则 `onclick` 正常触发了 `S.sel = label` + `render()`，但 `renderBody` 判定"哪个选项当前选中"时只读了 `S.answers[q.id].userAnswer`（此值提交后才写入），导致重渲染后 `.sel` class 永不出现。

**根因**：`renderBody` 的原始写法：
```
var ans = S.answers[q.id], ua = ans ? ans.userAnswer : null;
```
提交前 `ans` 恒为 `undefined`，`ua` 恒为 `null`，`isSel` 恒为 `false`——无论用户怎么点，视觉上毫不变色。考试和练习共用这段逻辑，所以两边都"点不上"。

**修法**：选中态在提交前读实时选择 `S.sel`，提交后读答案 `userAnswer` 用于对错着色：
```
var ans = S.answers[q.id], ua = (answered && ans) ? ans.userAnswer : S.sel;
```
同时考试模式下对错着色需 guard `!S.isExam`（考试中不暴露答案，等交卷后回顾页才着色）。

**回归点 #18**：实机点击选项应出现 `.opt.sel` 高亮；考试答题时应可正常点选；提交后练习应显示 reveal、考试应自动跳下一题无 reveal。
