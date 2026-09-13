# 云端部署与「本地刷新→云端同步」闭环

看板是单文件 HTML（`assets/dashboard-template/medical-ai-intel.html`），数据内联，无需后端。发布用 CloudStudio 静态站点部署。

## 架构：单一数据源 + 重建
- 权威数据：`archive/entries.json`（entries 数组）+ `archive/graph.json`（nodes/edges）。
- `build.js`（Node）读取这两个 JSON，重建看板内嵌 `DEMO_ENTRIES` / `DEMO_GRAPH`，同时写回 `medical-ai-intel.html`（本地）与 `deploy/index.html`（云端部署目录）。
- 部署目录必须含 `index.html`：`cp medical-ai-intel.html deploy/index.html` 或让 build.js 直接写 `deploy/index.html`。

## 部署步骤
1. 准备部署目录：`mkdir -p deploy && cp medical-ai-intel.html deploy/index.html`（或 build.js 直接产出）。
2. 调用内置工具 `workbuddy_cloudstudio_deploy`，参数：
   - `action`: `"deploy"`
   - `directory`: 部署目录绝对路径（需含 `index.html`）
   - `port`: `3000`
3. 返回 `shareLink`（公开可访问）。重部署为**幂等更新**：sandboxId 与分享链接保持不变。

## 推荐自动化：采集驱动同步（轮询 + 守卫 + 当日标记）

核心规则：**只有当日采集已产出，且产出满 5 分钟后，才执行云端同步；没有采集就绝不同步。** 这样既保证「本地刷新即云端同步」，又彻底杜绝了「采集还没跑、同步先跑导致漏数据」的问题。

> 配套关系：自动化 A「每日入库」（如 `FREQ=DAILY;BYHOUR=9`）：只写 `archive/*.json`，不碰 HTML。本自动化（B）只负责把**已产出**的档案上云，本身不采集。

### ❌ 反模式：固定时间同步（已废弃，会漏数据）
把 B 设成「A 之后 10 分钟」的固定时间（如 `BYHOUR=9;BYMINUTE=10`）**不可靠**：A 实际完成时间会漂移（实测出现过 14:03、20:11 才写完档案）。B 到点跑时档案还是昨天的数据，当天就"跑过了"，新数据滞留本地不上云 → 用户报「今天没同步」。

### ✅ 正解：把 B 改成「采集驱动」（高频轮询 + 条件守卫）
WorkBuddy 自动化只支持 RRULE 固定调度，没有事件触发，用「高频轮询 + 条件守卫」等价实现「采集后才同步」：

1. **调度（5 分钟粒度）**：`FREQ=HOURLY;INTERVAL=1;BYMINUTE=0,5,10,15,20,25,30,35,40,45,50,55;BYHOUR=8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23`
   - `MINUTELY` **不被支持**（仅 DAILY/HOURLY/WEEKLY/MONTHLY/YEARLY），要 5 分钟粒度必须用 `HOURLY` + 枚举 `BYMINUTE`；`BYHOUR=8..23` 覆盖采集可能产出的全部时段。
2. **守卫写进 B 的 prompt 开头**，顺序很重要（先做最便宜的短路）：
   - ① 读当日标记 `.workbuddy/automations/<id>/last_sync_date.txt`，内容 = 今天 → 一句话「今日已同步」跳过，立即结束（避免重复部署）。
   - ② 读 `archive/entries.json` 的 `updatedAt`：日期 ≠ 今天 → 「今日采集未产出」跳过，**不重建、不部署**（核心：**没采集就不同步**）。
   - ③ 日期 = 今天但距今 < 5 分钟 → 「采集刚产出，未满 5 分钟，等下次轮询」跳过（**缓冲意义**：防 entries.json 已写、graph.json 还没落盘时读到半成品，产生悬挂边）。
   - ④ 全部通过 → 才执行下面的同步步骤；部署成功后把今天日期写回标记文件。
3. **务必要求守卫未通过时只回 1–2 句、不罗列数据、不调部署工具**，否则一天上百次轮询会产生大量噪音与开销。
4. 强制当日重同步：删掉 `last_sync_date.txt`，下次轮询即触发。
5. 已知现象：`automation_update` 返回的 `nextRunAt` 可能未按新 rrule 即时重算（仍显示旧时间），用 `mode:"view"` 确认 rrule 已落库即可。
6. **同步步骤（守卫通过后）**见下方「同步步骤清单」。

> ⚠️ 注意：`automation_update` 的字段校验失败会**整体回滚本次调用**。若同时改 rrule 和 prompt 而 rrule 非法，prompt 也不会保存——报错后用 `mode:"view"` 确认，再单独重提失败的字段。

## 同步步骤清单（守卫通过后依次执行）

1. **校验数据源**：读 `archive/entries.json` 与 `archive/graph.json`，确认 JSON 合法、entries 数组非空、图谱无悬挂边。文件缺失/非法 → 停止汇报，绝不新建空数据。
2. **重建看板（archive 为唯一数据源）**：在工作目录执行 `node build.js`（Node 用托管版绝对路径 `C:/Users/50268136/.workbuddy/binaries/node/versions/22.22.2/node.exe`）。该脚本重建 `medical-ai-intel.html`（本地）与 `deploy/index.html`（云端部署目录）的内嵌 `DEMO_ENTRIES`/`DEMO_GRAPH`。
   - 报错（如正则未匹配到块）→ 停止汇报，**切勿用空数据覆盖**。
   - build.js 不存在 → 退而用 Read+Write 把最新 entry 与新节点/边手动同步进 HTML，并复制为 `deploy/index.html`。
3. **重建后自检（任一不过则停止）**：① `const DEMO_ENTRIES` 与 `const DEMO_GRAPH` 在两份 HTML 中各只出现 1 次（防重复声明导致页面空白）；② 两份 HTML `cmp` 逐字节一致；③ 从 `deploy/index.html` 反解 JSON，校验 entries 条数、graph 节点/边数、悬挂边 = 0。
4. **重新部署云端**：调用 `workbuddy_cloudstudio_deploy`（action 默认 `"deploy"`），`directory` 传部署目录绝对路径（需含 `index.html`），`port` 默认 3000。遇 504/409 → 重试，若 409 等 5–10 秒再试，最多 3 次。
5. **写标记**：部署成功后把今天日期写入 `.workbuddy/automations/<id>/last_sync_date.txt`（覆盖），当天后续轮询全部跳过。
6. **线上回验**：curl 拉取分享链接，反解 entries/节点/边数并与本地 `deploy/index.html` 逐字节比对；临时文件用完 `rm -f` 清理。
7. **汇报**：entries 条数、graph 节点/边数、最新条目日期与 PMID、部署是否成功、分享链接是否仍可用。部署失败 → 明确「本地已更新，云端需手动重新部署」并给出 deploy 目录路径。

约束：只同步，**绝不修改 `archive/*.json` 的业务数据**；保持 JSON 合法；所有路径以工作目录为准。

## ⚠️ build.js 致命坑（务必遵守）
- 用正则重写内嵌 JS 数据块时，**替换串严禁拼接下一个声明名**。错误写法：
  `html.replace(reEntries, entriesBlock + '\nconst DEMO_GRAPH = ')` ← 会产生 `const DEMO_GRAPH = const DEMO_GRAPH = ...` 重复声明。
  `html.replace(reGraph, graphBlock + '\nlet DATA = ')` ← 会产生 `let DATA = let DATA = ...` 重复声明。
  这两个重复声明会让**整段 `<script>` 语法错误、页面空白**（表现为「内容为空」）。
- 正确写法：每个块只替换自身声明，不拼接任何后续关键字：
  ```js
  const entriesBlock = 'const DEMO_ENTRIES = ' + JSON.stringify(entries, null, 2) + ';';
  const graphBlock   = 'const DEMO_GRAPH = '   + JSON.stringify(graph, null, 2)   + ';';
  html = html.replace(/const DEMO_ENTRIES = \[[\s\S]*?\];/, entriesBlock);
  html = html.replace(/const DEMO_GRAPH = \{[\s\S]*?\};/, graphBlock);
  ```
- **校验必须用 `node --check` 跑整段脚本语法**，不能只 `JSON.parse` 抽取的数据——后者会漏掉重复声明类语法错误。
- 若模板 HTML 已被污染（多重声明），用 `archive` 两 JSON 作干净源、以 `const DEMO_ENTRIES =` 到 `let DATA = { entries:` 为区间整体重写为干净声明修复。
