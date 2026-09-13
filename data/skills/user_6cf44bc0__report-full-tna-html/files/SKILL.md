---
name: Report-Full-TNA-html
title: "PDF 全文翻译 → 单文件 HTML（保留原图）"
version: "1.0.0"
created: "2026-08-31"
updated: "2026-08-31"
agent_created: true
description: 【PDF 全文翻译 → 单文件 HTML】长篇 PDF（研报/论文/白皮书/临床方案，50–300 页）全文翻译为「中文译本 + 原文件原图」的单文件 HTML。当用户要求把 PDF 全文翻译成中文且不省略任何章节/段落/表格/脚注/附录、要求严格保留原文件结构与格式（标题层级、编号、列表、加粗斜体、表格行列）、要求图片直接沿用原文件原图且位置与图注不变、要求术语全文统一且英文缩写首次出现标注为「中文全称（English, 缩写）」、要求输出可打印/可存 PDF 的中文报告时触发。同样适用于临床试验方案／研究者手册／药政文件 PDF（Profile B：表格译中文、结尾附「保留未译与存疑术语清单」、涂黑脱敏内容需先恢复再翻译）。核心解决：FOP/矢量生成型 PDF 中图表被切成上万碎片无法直接导出图片（整页光栅化 + 连通域聚类定位图区再按区裁剪渲染）；`_redacted` PDF 的「视觉脱敏 vs 真脱敏」判别与内容恢复；用线条画的跨页网格大表（如 SoA 评估时间表）的列结构与合并格还原。**若要输出可编辑的 .docx 而非 HTML，改用 Report-Full-TNA-docx（两者共用本 skill 的提取/翻译前端，仅渲染器不同）。**当用户要求把 PDF 全文翻译成中文且不省略任何章节/段落/表格/脚注/附录、要求严格保留原文件结构与格式（标题层级、编号、列表、加粗斜体、表格行列）、要求图片直接沿用原文件原图且位置与图注不变、要求术语全文统一且英文缩写首次出现标注为「中文全称（English, 缩写）」、要求输出可打印/可存 PDF 的中文报告时触发。同样适用于临床试验方案／研究者手册／药政文件 PDF（Profile B：表格译中文、结尾附「保留未译与存疑术语清单」、涂黑脱敏内容需先恢复再翻译）。核心解决：FOP/矢量生成型 PDF 中图表被切成上万碎片无法直接导出图片（整页光栅化 + 连通域聚类定位图区再按区裁剪渲染）；`_redacted` PDF 的「视觉脱敏 vs 真脱敏」判别与内容恢复；用线条画的跨页网格大表（如 SoA 评估时间表）的列结构与合并格还原。
---

# PDF 全文翻译 → 单文件 HTML（Report-Full-TNA-html）

> 姊妹 skill：**Report-Full-TNA-docx**（同一前端，输出 .docx）。两者共用本 skill 的
> 「提取 → 脱敏判别 → 表格重建 → 分段翻译」前端，只在**最后一步渲染**分叉：HTML vs Word。

## 何时使用

- 用户给出一个 PDF，要求「全文翻译成中文」
- 要求**保留原文件结构**：标题层级、编号、列表、加粗/斜体、表格行列、章节编号
- 要求**图片沿用原文件原图**，位置与图注不变
- 要求**术语统一**，英文缩写首次出现标注「中文全称（English, 缩写）」
- 要求译后另加「要点总结与分析」独立章节
- 交付形态：单个 HTML 文件、内联样式与脚本、无外部依赖、可直接打印为 PDF

已验证规模：
- 208 页 TD Cowen 白血病研报 → 14.4 MB HTML、159 张原图、251 张表格、239 条目录
- 49 页 TD Cowen 结直肠癌研报 → 2.03 MB HTML、23 张原图、7 张表格、86 条目录
- 127 页 APG-2575（GLORA-4）临床方案 → 0.35 MB HTML、2 张原图、TOC 100 条、页锚 128/128

## 文档类型 Profile（先判型，再开工）

同一条管线，不同文档类型的收尾与约定不同。**开工前先判型**：

| | **Profile A：卖方研报** | **Profile B：临床试验方案 / 药政文件** |
|---|---|---|
| 典型输入 | Cowen/瑞银/高盛类研报 | Protocol、Investigator's Brochure、批件 |
| 图 | 多（几十到上百张），是交付重点 | 极少（通常只有几张流程图），表格才是重点 |
| 表格 | 有底纹的多，可走图或 Markdown | **用线条画的网格大表**多，需坐标重建；**表格译中文** |
| 收尾章节 | 追加「要点总结与分析」 | 追加「保留未译与存疑的术语清单」 |
| 特殊步骤 | Step 3.5 删除收件人身份标识 | Step P1 脱敏判别与恢复 + Step P2 网格表重建 |
| 篇幅 | 50–300 页 | 80–200 页 |

判定后按对应 Profile 的附加步骤走；**六步主干流程两者通用**。Profile B 详见下方「临床方案 Profile B」专节。

## 路由与边界（先判「该不该用」，再判「怎么用」）

| 用户诉求 | 归属 |
|---|---|
| 单文件 HTML、保留原图、目录 + 可打印/存 PDF | **本 skill** |
| 要 `.docx`（可编辑、走审批/递交） | **`Report-Full-TNA-docx`**（共用本 skill 前端，只换渲染器） |
| 两种都要 | 译文 md 只做一份，**渲染两次**，绝不翻译两遍 |
| 只要摘要/要点，不要全文 | 直接读 PDF 作答，不必走管线 |
| 扫描件（无文字层） | 先 OCR，否则提取出来是空白 |
| 加密不可提取 | 向用户要解密版 |
| 非 PDF 源（docx/html/txt） | 不走本 skill，直接分段翻译 |
| **从零撰写**长篇 HTML（投研/rNPV/看板，非翻译） | **`long-html-report-pipeline`**（分段 Write + 合并 + 数字自洽性审计） |
| 译文 HTML 打开卡顿 | `report-perf-optimize` |

规模边界：50–300 页为已验证区间；**>300 页**建议把分块再切细（每块 6–8 页）并把图 DPI 降到 120 控体积。

## 环境

需要一个装了 `pymupdf` / `pdfplumber` / `pypdf` 的 Python 环境（推荐独立 venv，**不要**污染系统 Python）。下面两种方式任选其一：

```bash
# 方式 1（推荐，最稳）：显式指定你的 venv 解释器
export PY="<你的 venv 路径>/Scripts/python"     # Windows
# export PY="<你的 venv 路径>/bin/python"       # macOS / Linux
# 建议把这一行写进 ~/.bashrc 或 ~/.zshrc，之后每次开箱即用，不用再改 SKILL.md

# 建 venv（只需一次）
python -m venv .venv
.venv/Scripts/pip install pymupdf pdfplumber pypdf    # Windows
# source .venv/bin/activate && pip install pymupdf pdfplumber pypdf   # macOS / Linux

# 方式 2：不指定则用当前 python，并在下面自检依赖是否齐全
PY="${PY:-$(command -v python3 || command -v python)}"
"$PY" -c "import fitz, pdfplumber" 2>/dev/null || {
  echo "缺少依赖，请先安装：  $PY -m pip install pymupdf pdfplumber pypdf"; exit 1; }
```

> **为什么不再写死路径**：技能会分发到不同机器，写死的绝对路径在别人那里必然失效。把路径交给 `PY` 环境变量，既能在你本机零改动运行，也能让使用者各自填自己的路径。

Windows bash 下**必须**带 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`，且**脚本一律写成 .py 文件再执行**——`python -c "..."` 在 Git Bash 里经常静默无输出。

**路径坑**：Git Bash 的 `/c/Personal/...` 形式 pymupdf **不认**，会报 `no such file`。传给 pymupdf 的路径一律用 Windows 形式 `C:/Personal/...`（正斜杠可以，但盘符形式必须是 `C:`）。

**PDF 位置别写死**：用户常在任务中途移动源文件。脚本里用 `os.walk` 从任务根目录/常用目录动态查找，比硬编码路径稳。

## 目录约定（固定，便于脚本复用）

```
<workspace>/
├─ out/full_raw.txt        # 原文全文，===== PAGE N ===== 分隔（事实源）
├─ out/figs_meta.json      # 图表元数据
├─ out/figs/pNNN_N.jpg     # 渲染出的图表
├─ out/zh/part_01.md …     # 分段译文（含标记）
├─ out/style.css, out/shell.html
└─ <产物>.html
```

## 六步流程

### Step 1 — 提取原文（事实源）

```bash
PYTHONUTF8=1 $PY scripts/extract_text.py "<src.pdf>" out/full_raw.txt
```

产出 `===== PAGE N =====` 分隔的纯文本。**这份文件是后续一切的事实源**：翻译时以它为准，校验时以它为准（比对页码、比对数字）。

Read 工具读不了十几 MB 的 PDF，必须走脚本。

### Step 2 — 图表定位与渲染（核心难点）

**绝对不要**用 `page.get_images()` / `extract_image()`。FOP 2.x、iText、以及多数矢量排版引擎生成的 PDF，会把一张柱状图切成几千个矢量笔画 + 位图碎片。实测 208 页 PDF 会导出 **39,936 个碎片、2.4 GB**——全是色块和线条残片，拼不出图。

正确做法：**整页光栅化 + 连通域分析定位图区 + 按区裁剪渲染**。

```bash
PYTHONUTF8=1 $PY scripts/figs_extract.py "<src.pdf>" 150
```

脚本算法（`scripts/figs_extract.py`）：
1. `gra_rects()`：收集 `get_drawings()` 的 rect（≥5×5pt）+ `get_image_info()` 的 bbox（≥40×25pt）
2. `clusters()`：gap=24pt 的容差合并，把邻近碎片聚成图块；过滤掉 <45×28pt 的噪声
3. `figure_regions()`：把图块按 y 重叠归行（并排的两张图分属同一行，在中点切分左右边界）
4. `y_expand()`：把裁剪框的上下边界**扩展到相邻的标题/来源文本块的外缘**（见下方「标题截断」坑）
5. `page.get_pixmap(dpi=150, clip=rect)` 渲染，存 JPEG q88

参数经验值：
- **150 DPI / JPEG q88** 是甜点。PNG 同样内容体积是 JPEG 的 2.2 倍（20.6 MB vs 9.9 MB），base64 后差距更夸张。
- 页面正文区常数：`BODY_TOP=100, BODY_BOT=744, X0=12, X1=600`（Letter 612×792）。换开本要重新量。

### Step 2b — 图表提取后审计（必做，否则漏图无法发现）

`figs_extract.py` 跑完后，**必须**用以下脚本做三轮审计，不要靠肉眼翻图：

```bash
# 1) 逐页体检：有视觉内容但 meta 里图数偏少的页
PYTHONUTF8=1 $PY scripts/scan_pages.py "<src.pdf>" out/figs_meta.json

# 2) 全量审计：反向查漏图 + 正向查槽位 + 产物查图
PYTHONUTF8=1 $PY scripts/audit_figs.py "<src.pdf>" out/figs_meta.json out/zh "<产物>.html"

# 3) 标题是否被裁在图外
PYTHONUTF8=1 $PY scripts/audit_title_outside.py "<src.pdf>" out/figs_meta.json

# 4) 图注与图是否错位（并排图合并导致槽位漂移）
PYTHONUTF8=1 $PY scripts/figmap_check.py "<src.pdf>" out/figs_meta.json out/zh
```

`scan_pages.py` 会列出每页的笔画/位图/候选图区/meta 图数。**`clust > meta` 的页大概率漏图**。

`audit_figs.py` 是综合审计：
- A. 反向查图：PDF 里所有矢量笔画聚成候选图区，检查 meta 是否覆盖；
- B. 正向查槽：每个 `@@FIG:p:n@@` 是否解析到真实文件、槽位编号是否连续、是否与阅读顺序一致；
- C. 产物查图：HTML 中 `<figure>` 数、base64 可解码性、孤儿图片。

`audit_title_outside.py` 专门抓「图标题整块留在裁剪框上方 20–75pt」的情况（`check_crop.py` 只查骑边，不查整块漏裁）。

`figmap_check.py` 抓「并排图被合并成一张宽图后，后一个 `@@FIG:p:n@@` 错误地映射到下一张真实图」导致的图注错位。

**提取后若发现漏图/错位**：不要直接改 md 硬补。先回到 `figs_extract.py` 调参或做人工精修（见坑 #11 与「图区精修」小节），再重建 `figs_meta.json`；md 里的 `@@FIG` 标记应始终与 meta 真实图数一致。

### Step 2c — 图区精修（封面/正文误检与跨页表格）

自动提取不会 100% 完美，以下三类需要人工后处理：

1. **封面被误检为整页图**（p1）：封面常有大幅装饰底纹，会被聚类为一张全页图。应删除，避免把收件人信息重新插回译本。
2. **正文区块被误检为图**：项目符号、小图标、下划线等细碎矢量会被聚成「假图」。通过看 `scan_pages.py` 的候选图区坐标与内容，或 Read 生成的图片，把明显是正文文本的条目从 `figs_meta.json` 删除。
3. **跨页表格**：一张表格跨两页时，提取器按页裁切会把它拆成两张图。当前解法：保持拆分，在 md 里分别写 `@@FIG:45:1@@` / `@@FIG:46:1@@`，图注用「（续）」区分。若要合并为单张图，需手动按 y 坐标跨页拼接（未来可脚本化）。

精修 workflow：

```bash
# 备份原始 meta
mv out/figs_meta.json out/figs_meta.json.auto
# 写 curate_figs.py（调用 pymupdf 重新渲染指定 bbox、删除误检、合并碎片）
# 运行后得到新的 out/figs_meta.json
```

参考实现见 CRC 项目里的 `crc/out/curate_figs.py`（**项目内脚本，不在本 skill 里**，按需照其思路现写）：
删除 p1 封面、p9/p10 正文误检，合并 p45 两张碎片为一张完整 R&D Pipeline 表，并重新裁剪 p5 避免收入正文段落。

### Step 3 — 分段翻译（标记系统是关键）

按页切成 25–40 个 `out/zh/part_XX.md`，每个文件约 6–10 页原文。**不要一次性翻完整篇**——上下文会爆，而且中途被限流中断后无法续。

译文 Markdown 里用两种标记占位：

```markdown
<!--PAGE:57-->                 ← 页锚，组装时渲染成「原文第 57 页」分隔条

**图：Gazyva + Venclexta 带来更高缓解率…**   ← 图注（组装时并入 <figcaption>）
@@FIG:6:1@@                    ← 图槽，= 第 6 页第 1 张图
```

**为什么用标记**：翻译是按段分批做的，此时图还没定位完；用占位符可以让「翻译」和「取图」两条线解耦，最后 `build.py` 统一解析。图注写在图槽**上一行**，组装时自动并入 `<figcaption>`。

补齐漏页：`part_17b.md` 这种带字母后缀的命名是合法的，`build.py` 的 `part_key()` 会按 `(主数字, 后缀)` 自然排序，插在 `part_17` 与 `part_18` 之间。

翻译质量要求（写进每一段的 system 约束里）：
- 专有名词（产品名、人名、机构名、试验编号、URL、代码块、公式）保留原文
- 英文缩写首次出现：`中文全称（English, 缩写）`
- 原文件的疑似笔误**不要静默修正**，用「译注：…」标出
- 原文重复章节也不要删，用「编者注：本节与第 X 页重复」标出

### Step 3.5 — 脱敏：删除收件人身份标识（卖方研报必做）

**卖方研报（TD Cowen 等）首页的「研究团队邮箱 + 收件人专属声明」属于收件人身份标识，一律删除，不译、不留。**——这是分发前的合规动作，不只是个人偏好。

原文固定长这样（只在第 1 页，全文仅此一处）：

```
TD Cowen 制药团队        pharmateam@tdsecurities.com
TD Cowen 生物技术团队    biotechteam@tdsecurities.com
TD Cowen 医疗技术团队    medtechteam@tdsecurities.com
This report is intended for <收件人邮箱>. Unauthorized distribution prohibited.
```

> 注：上面三行研究团队邮箱是出版社固定印制的**公共信息**，保留在此作为识别特征（`redact.py` 据此匹配）；`<收件人邮箱>` 是占位符，**不要把任何真实收件人地址写进技能或译文**——它指向具体自然人，属于应当抹除的身份标识。

处理顺序：**翻译时就不要产出这几行**（最干净）；全部 part 写完后跑一遍脚本兜底：

```bash
PYTHONUTF8=1 $PY scripts/redact.py out/zh            # 递归清 *.md
PYTHONUTF8=1 $PY scripts/redact.py --check out/zh    # 复核，应为 0
```

脚本幂等，可重复运行。`--check` 只报告不写盘。**一定要先 `--check` 看 diff 再落盘**，因为：

- **保留**法律免责声明里的功能性地址（`Privacy.EAP@tdsecurities.com`）与公司网址（`portal.tdsecurities.com` / `tdcowen.bluematrix.com`）——这些不是收件人标识
- **不能**用「下一个非空行是 `<!--PAGE:N-->`」判定水平线 `---` 是否孤立。正文里 `---` 后面紧跟分页标记是合法用法（分页前的分隔线），按这条判据会误删正文里真实的分隔线。正确判据是「越过空行后遇到的第一个非空行**本身是被删除的行**」

若产物 HTML 已生成又不想重跑 `build.py`（如 200+ 页重建耗时），可直接对 HTML 跑同一脚本：

```bash
PYTHONUTF8=1 $PY scripts/redact.py "<产物>.html"
```

它按 `<p>` / `<li>` / `<blockquote>` / `<div>` 元素级匹配删除，并清空因此变空的 `<ul>`。但**优先改 md 源再重建**，否则下次 build 会把内容又带回来。

### Step 4 — 组装

```bash
PYTHONUTF8=1 $PY scripts/build.py \
  out/figs_meta.json out/zh \
  assets/shell.html assets/style.css \
  "<产物名>.html" "<标题>"
```

`build.py` 做的事：
1. 按 `part_key()` 自然排序拼接所有 part
2. 解析 `@@FIG:p:n@@`：按页取 `figs_meta.json` 里第 n 张；若该页图数少于标记数，取最后一张兜底
3. **同图去重**：多个标记映射到同一张图时（并排图被合成一张宽图），只渲染一次，图注用 ` ｜ ` 合并
4. Markdown → HTML：标题（带 TOC 锚点）、表格（`div.tw` 包裹可横向滚动）、列表（嵌套）、引用块、行内 code/链接/加粗
5. 图片 base64 内联，同路径只编码一次
6. 注入 `assets/shell.html`（顶栏 + 可折叠目录抽屉 + 灯箱缩放 + 回到顶部 + 打印样式）

### Step 5 — 校验（必做，别跳过）

```bash
PYTHONUTF8=1 $PY scripts/verify.py "<产物>.html" 208
```

看这六项：
- `page anchors` == PDF 总页数（缺页 → 补 part）
- `@@FIG left` == 0（有残留 → 标记格式写错，检查是否独占一行）
- `stray caps` == 0（游离图注 → 说明图注没被并入 figcaption）
- `div / p imbal` == 0（标签不平衡）
- `missing pages` / `dup pages` == none

**还要反向查一遍**：`figs_meta.json` 里每个有图的页，译文里是否都有对应 `@@FIG` 标记；有图无标记 = 那一页漏翻了。这次就是靠这条查出第 81–85 页整段漏翻。

**Step 5b — 逐页覆盖率检查（推荐，能抓到「页码连续但内容被砍」）**

```bash
PYTHONUTF8=1 $PY scripts/coverage.py out/full_raw.txt out/zh
```

逐页算「中文字数 ÷ 英文词数」。研报健康区间约 **1.1–1.8**。某页显著低于中位数 = 段落被漏翻；显著高于 = 译文注水或版式串页。**注意**：最后一页通常会被标红，因为 `part_99_summary.md` 排在最后一个 `<!--PAGE:N-->` 之后、落进了那一页的区块，属于预期，不是缺陷。

**Step 5c — 图片截断自动检查（替代肉眼看图）**

```bash
PYTHONUTF8=1 $PY scripts/check_crop.py "<src.pdf>" out/figs_meta.json
```

对每个裁剪框，检查上下 22pt 内的文本块是否有「骑在裁剪边上」的（即该行被切了一半）。有则为 0 才算干净。当所用模型看不了图片时，这条脚本是唯一可靠的替代手段——不要靠猜。

### Step 6 — 交付

`present_files` 给出 HTML 路径。提醒用户：目录可折叠、点图可放大、右上角「打印 / 存为 PDF」可导出。

## 脱敏（redacted）PDF：先判别「视觉脱敏」还是「真脱敏」，再决定流程

拿到文件名带 `_redacted` 或页面上有黑框的 PDF，**不要**默认内容已删除、更不要把覆盖文本替换成 ■ 占位符直接前进——临床方案/合同类文件的「脱敏」常是画黑矩形盖在完整文字层上（视觉脱敏），文字层其实完好。

**Step R1 — 判别（已脚本化，全文档跑一次只要十几秒）**：

```bash
PYTHONUTF8=1 $PY scripts/check_redaction.py "C:/path/src_redacted.pdf" --samples 15
```

输出示例（127 页 APG-2575 方案实测）：

```
黑框（近黑填充矩形）: 2272
文本 span 总数      : 8366
被黑框覆盖的 span   : 2280
■/● 占位字形 span   : 0
→ 【视觉脱敏 → 可恢复】：黑框只是盖在完整文字层之上，无占位字形。
```

判别原理（`scripts/check_redaction.py`，不必重写）：

```python
for page in doc:
    boxes = [d["rect"] for d in page.get_drawings()
             if d.get("fill") and max(d["fill"]) < 0.15]          # 黑色填充矩形
    for blk in page.get_text("dict")["blocks"]:
        for line in blk.get("lines", []):
            for span in line["spans"]:
                covered = sum(fitz.Rect(span["bbox"]) & fitz.Rect(b)
                              for b in boxes if fitz.Rect(span["bbox"]).intersects(b))
                if covered.get_area() / max(fitz.Rect(span["bbox"]).get_area(), 1e-6) >= 0.6:
                    ...  # 被覆盖但可恢复
    # 另统计 span 文本含 ■ 的数量（真脱敏时文字层会出现 ■/● 替换字形）
```

**判别决策树**：

| 黑框数 | 被覆盖 span | ■ 字形 | 结论 | 处理 |
|---|---|---|---|---|
| 多 | 多 | **0** | **视觉脱敏 → 可恢复** | 用不带脱敏逻辑的提取器拿完整文本，被覆盖内容**照常翻译写入** |
| — | 0 | 多 | 真脱敏 → 不可恢复 | 保留 ■ 占位，术语清单注明「原文此处已脱敏」 |
| 多 | 多 | 多 | 混合脱敏 | 逐处判断，只对真删处留占位符 |
| 0 | 0 | 0 | 无脱敏 | 按普通 PDF 处理 |

⚠ **最贵的坑**：不要用「脱敏感知提取器」把覆盖文本替换成 ■ —— 那是自我阉割，会导致整轮译文作废重译（本次 11 个分块全部重译）。
⚠ **后悔药**：提取阶段永远留一份**未做任何替换**的完整文本备份（如 `out/full_raw_full.txt`），任何"顺手处理"都在备份之后。

**Step R2 — 难表格坐标重建**（SoA 评估时间表这类跨页网格大表；已脚本化）：

```bash
# 跨页大表（如 p68-70 的评估时间表）：前 2 行作表头，跨页重复表头自动跳过
PYTHONUTF8=1 $PY scripts/grid_table.py "C:/path/src.pdf" \
    --pages 68-70 --hrows 2 --out out/soa.md

# 跨页统计界值表（表 18 实际跨 p106-107）：**页区间要含表头所在页**
PYTHONUTF8=1 $PY scripts/grid_table.py "C:/path/src.pdf" \
    --pages 106-107 --hrows 2 --out out/table18.md

# 只想截取页面中部（排除页眉页脚与正文）
PYTHONUTF8=1 $PY scripts/grid_table.py "C:/path/src.pdf" \
    --pages 107 --hrows 0 --top 80 --bot 190 --out out/t18_cont.md
```

常用参数：`--pages`（必填）/ `--hrows` 前几行作表头（后续页相同行自动跳过，**续页用 `--hrows 0`**）/ `--top --bot` 上下边界 / `--coltol` 列聚类容差（默认 8）/ `--rowtol` 带内分行容差（默认 3）/ `--mincol` 伪列合并阈值（默认 8pt）/ `--title` 表题 / `--out` 输出。

**实测基准（127 页 APG-2575 方案，可与你的结果对照）**：

| 表 | 命令 | 结果 |
|---|---|---|
| 表 10 SoA | `--pages 68-70 --hrows 2` | 自动合并 2 个伪列 → **15 列 / 41 行**，列边界 55.2 / 166.2 / 216.1 / 264.3 / 327.0 / 349.4 / 382.3 / 428.7 / 468.4 / 509.5 / 561.9 / 608.5 / 652.2 / 702.1 / 741.9 / 789.7 |
| 表 18 | `--pages 106-107 --hrows 2` | 自动合并 1 个伪列 → **10 列（末列为空）/ 9 行**，5 行数据 + 2 行表头 + 页眉页脚噪声行 |

输出中的合并格形如 `Objective response assessment X7.1〔合并格：列5–列9〕`，
即「周期 1 全部访视列合并」；`Bone marrow MRD X19〔合并格：列2–列12〕` 即「筛选期至周期 2 D22 大合并格」。
**这些标注必须与脚注/正文交叉验证后再译**（如脚注 16 可印证周期 2 只有 D1/D15/D22 三列）。

脚本算法（`scripts/grid_table.py`）：

1. 横线：`get_drawings()` 中 `width>=40, height<=2.5` 的矩形 → 按中心 y 聚成「行带」；
2. 竖线：`width<=2.5, height>=4` 的矩形 → 按中心 x 聚类（tol 默认 8pt）成「列边界」；
3. 单元格：`get_text("words")` 按中心点落入 (行带, 列区间)，带内按 y 容差分行、行内按 x 拼接；
4. **合并格检测**：某条列边界在该行带内**没有竖线覆盖** → 判定左右两格合并，文本后自动追加 `〔合并格：列A–列B〕`；
5. 跨页：后续页中与首页表头文本相同的行自动跳过。

产物写成独立 `*_insert.md`，由主任务在对应页锚处替换骨架 / 插入。

⚠ **列归属必须坐标验证，不能靠语义猜**。本次表 18 第一版把「累积 α 消耗」误放进「无效性边界」组，
坐标核对才发现它是独立顶层列（`Cumulative@484` vs `Futility@302` / `Efficacy@401`），整表重写。
⚠ **合并格会让单元格数变少**，回填到 ncol 列时要按跨度展开补空串，否则整行错位（本次 SoA 的 MRD 行就多出 1 格）。
⚠ **单元格为空不等于缺内容**：给药细节、访视窗口常写在脚注里（如 4.1–4.3），原文单元格本就只有标记 → 忠实留空，用脚注编号（X⁷·¹、X¹⁹）与正文交叉验证列数。
⚠ **双线边框会产生极窄伪列**（外框与内框之间只有 2–4pt），把 15 列撑成 17 列 → 用 `--mincol`（默认 8pt）自动合并；若仍多列则手工核对列边界。
⚠ **表头去重的坑（已修复，勿回退）**：早期版本写成
`if 首页 and len(rows_out) < hrows: header_keys.add(key)` 后紧跟 `if key in header_keys and rows_out: continue`，
结果「刚加进 header_keys 的行又被自己跳过」，**首页第 2 行起被全部吞掉**——单页表只剩 1 行、跨页表丢掉首页大部分行。
正确写法是 `elif key in header_keys: continue`。排查信号：输出行数远少于 PDF 上肉眼可见的行数。

**其余注意**：
- 用户可能移动过 PDF——脚本里用 `os.walk` 从任务根目录动态定位。
- 后台翻译 Agent 被手动中断时会一并终止：恢复时先核对落盘状态，再分批（每批 4–5 个）重派。
- Agent 可能把相邻页块合并导致 `<!--PAGE:N-->` 锚缺失：先核对内容是否已译，已译则只需补锚，勿重译。

## 临床方案 Profile B（Protocol / IB / 药政文件）

### 触发条件

用户给出临床试验方案、研究者手册（IB）、药政批件/回复等**药政类英文 PDF**，并要求全文译为中文、保留结构编号、结尾列术语清单时，走本 Profile。

### 主干流程之上新增的步骤

| 步骤 | 内容 | 说明 |
|---|---|---|
| **Step P1** | 脱敏判别与恢复 | 见上文「脱敏 PDF」章节。**先判别，再决定提取方式**，不要默认内容已删 |
| **Step P2** | 网格表坐标重建 | SoA 评估时间表、统计界值表等跨页/多层表头表，走 `grid_table.py`，**不让翻译 Agent 猜列** |
| **Step P3** | 写 `translation_guide.md` 再派发 | 术语表 + 格式约定 + 恢复文本政策；多 Agent 并行时这是唯一的一致性保障 |
| **Step P4** | 收尾术语清单 | 见下；**不写**「要点总结与分析」 |

主干的 Step 1–6（提取 → 图区 → 分段翻译 → 组装 → 校验 → 交付）照常执行。
图片通常只有几张流程图；若流程图内部标签在文件层面被真删除，保留图槽 + 中文图题并在术语清单注明。

### 术语处理规范

> ⚠ **本表是 `Report-Full-TNA-html` 与 `Report-Full-TNA-docx` 的术语唯一真源**，
> 改动时两边同时生效；docx 侧不要再另写一份术语表。

| 类别 | 规则 | 示例 |
|---|---|---|
| 药物名 | 首次出现中英对照，后续从简 | lisaftoclax（APG-2575）；阿扎胞苷（Azacitidine, AZA） |
| 研究代码 / 方案编号 | **保留英文** | APG-2575、GLORA-4、APG2575MG301 |
| 访视与周期代码 | **保留英文** | C1D1、C1D8、C2+D15、EOT、Day -3 to Day -1 |
| 缩略语 | 首现标注「中文全称（English, 缩写）」，后续用中文或缩写 | OS 总生存期、CR 完全缓解、MRD 微小残留病、PK 药代动力学、EOT 治疗结束 |
| 统计方法名 | 保留方法原名 | Lan-DeMets α 消耗函数、O'Brien-Fleming 型界值、分层 log-rank、Cochran-Mantel-Haenszel、Clopper–Pearson、Kaplan-Meier |
| 参考文献 | **保留英文原文**（作者/期刊/卷期/DOI/URL） | — |
| 数字·剂量·单位·实验室值·受试者编号·日期·时间窗 | **原样不换算** | 400 mg、QD、28 天周期、±1 天、±7 天 |

### 结构与格式要求

- 章节编号、入选/排除标准编号、表号（表 1…表 18）、图号**保持原文编号，不重排**
- **表格译为中文**（Profile B 与 docx 版 skill 的关键差异）
- 脚注按原文位置保留，不并入正文；给药细节、访视窗口常只在脚注里出现
- 标题层级跨分块保持一致（否则 TOC 错位）
- 原文笔误（如期刊名连写 `Am J ClinOncol`、引用编号 `refer to 23.2`）**照录**，写入存疑清单，不擅自修正

### 收尾：术语清单（`part_12.md` 形式，`<!--PAGE:N+1-->` 起）

三段式，缺一不可：

1. **保留未译（保留英文）的术语**：药物代号与研究代码、访视/周期代码、参考文献、URL、公式符号
2. **使用存疑或需说明的术语**：重建产物标注（合并格）、原文如此的特殊结构（如 C2 周期只有 D1/D15/D22）、真脱敏不可恢复的位置、原文笔误、译名选择（如 WM / venetoclax）
3. **脱敏恢复范围说明**：哪些内容从黑框下恢复并已译出、哪些真不可恢复

## 关键坑（按踩坑代价排序）

1. **图表碎片化**：别碰 `get_images()`。走整页光栅化 + 连通域聚类。
2. **图表标题/来源行被截断**：`y_expand()` 早期版本把裁剪框上边界设为「上方文本带的**下缘**」，等于把标题整块排除在外，用户看到「标题上半截被切掉」。正确做法是**把相邻标题/来源文本块整体纳入裁剪框**（取 `block.y0` 而非 `block.y1`），并留 8pt padding。
   - 判定「是不是标题/来源块」必须用**独立文本块**（`get_text('dict')` 的单个 block），**不能**用合并后的文本带——否则来源行会和下方正文段合并成一个高块，把整段正文也框进图里。
   - 判据：块高 ≤42pt、与图块水平有重叠、垂直距离 <45pt（上方）/ <28pt（下方，含 `Source:`/`Note:` 等关键词时放宽到 70pt）。
   - 保险丝：裁剪框总高 >650pt 时回退到「图块 ±10pt」。
3. **PNG 体积失控**：一律 JPEG。150 DPI + q88。
4. **图注重复渲染**：并排图被合成一张宽图后，两个标记指向同一文件 → 会渲染两遍、图注出现两次。必须按 `(page, path)` 分组，只发组长的 `<figure>`，其余标记行 + 其图注行进 `drop_lines`。
5. **标题层级不统一**：前段用 `###`/`####`、后段用 `##`/`###`，TOC 会错位。组装前统一降/升一级；TOC 默认只收 h1–h3（`.t1/.t2/.t3`）。
6. **漏页静默发生**：分批翻译最容易整页跳过。靠 Step 5 的「有图无标记」反向查 + 页码连续性查。
7. **Windows Git Bash 下 `python -c` 无输出**：脚本写成文件执行；带 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`。
8. **无底纹/无矢量的纯文本表格才可能不被图表提取器识别**。`figs_extract.py` 依赖 `get_drawings()` 与 `get_image_info()`，所以只用文字和细线画出的大表格在 `figs_meta.json` 里**完全不存在**。它的内容只存在于文本层，而且 `extract_text.py` 按阅读顺序拉平后，列位置会全部丢失。
   - 但注意：**很多「看起来像纯文本」的表格其实有行底纹（shading）**，修复坑 #11 的聚类 bug 后，这些底纹会被合并成大图区，表格就会以图片形式被正确提取（CRC 的 R&D Pipeline 表即如此）。因此先跑 `figs_extract.py`，再用 `scan_pages.py` / `audit_figs.py` 确认是否真的缺失。
   - 若确实只有文字+细线，解法：对该页单独跑一次 `page.get_text('dict')`，按 `span['bbox']` 的 `x0` 把单元格还原回列。实操要点：
     - 先打印表头的列坐标定出各列 x 区间（例：PC≈281–293、I≈305–310、II≈324–331、III/NDA/MKT 均分 343–398）
     - 再把落点符号（⚫/●/✓）按 x 归入对应列
     - **用页面自带的合计行交叉验证**：如管线表末尾「Total Drugs in Development: PC 0 / I 9 / II 6 / III 4 / NDA 0 / MKT 17」，逐列数完必须能对上（有跨两列的药会重复计数，总数会比行数多 1）
     - 还原后在译文里写成 Markdown 表格，`build.py` 会自动渲染成可横向滚动的 HTML 表
9. **宽表在窄屏会被挤成细条**。样式里用 `table{width:max-content;min-width:100%}` 配合 `.tw{overflow-x:auto}`：窄表照常撑满，9 列的管线表保持自然宽度并横向滚动。写成 `width:100%` 会把长文本单元格压成竖排，完全没法读。
10. **`build.py` 的 `render()` 返回 list，不是 str**。引用块分支若写成 `'<blockquote>%s</blockquote>' % render(...)`，`%s` 会把 list 格式化成 **Python repr**，页面上直接出现 `['<p>译注：…</p>']` 这种方括号+引号的字面量（208 页那份报告里漏了 16 处）。必须 `''.join(render(...))`。
    排查：`grep -c "\['" 产物.html`，应为 0。
11. **`pymupdf.Rect` 没有实现 `__ior__`**，`hit |= r` 只是把新对象重新绑定给局部变量 `hit`，**列表里的 `Rect` 从未被真正更新**。这会让 `figs_extract.py` 的聚类合并**静默失效**：由大量细碎笔画组成的图表会被拆成无数小矩形，因尺寸不足被整体丢弃，造成「图片缺失/不全」。**所有聚类合并必须用 `include_rect()`**。
    - 排查：`python -c "import pymupdf; print('__ior__' in dir(pymupdf.Rect))"` 应输出 `False`。
    - 修复：把 `hit |= r` / `new[-1] |= c` 全部改成 `hit.include_rect(r)` / `last.include_rect(c)`。
    - 注意：这个 bug 影响所有基于列表存储 Rect 的脚本（`audit_figs.py`、`scan_pages.py` 等），必须一并修正。
12. **把「视觉脱敏」误判成「真脱敏」——代价最高的一次返工**（判别与恢复流程见上文「脱敏 PDF」章节，此处不再重复）。
    一句话：**先跑 `check_redaction.py`，再决定提取方式**；提取阶段永远留一份未做任何替换的完整文本备份（`full_raw_full.txt`），那是唯一的后悔药。
13. **后台翻译 Agent 会被用户中断一起杀掉**。用户手动中断任务时，正在跑的并行 Agent 全部终止，只有部分 `part_XX.md` 落盘。
    - 恢复动作：**先盘 `out/zh/` 落盘状态**（不要盲重发），再按缺的分块补派。
    - 派发节奏：**每批 4–5 个**，别一次全派；一次性全派容易限流，出现过 `502 ENOTFOUND`。
    - 偶发的「Agent 空返回 / 网络 502」，直接重派该分块即可，不必整批重来。
14. **`<!--PAGE:N-->` 锚缺失 ≠ 漏译**。翻译 Agent 常把相邻页块合并成一个段落块，导致某个页锚不存在。
    - 先拿原文逐页核对内容在不在（**大概率已译，只是合并了**），确认已译就只在块边界补插锚点，**不要重译**。
    - 本次 part_04 缺 `PAGE:32`、part_11 缺 `PAGE:119`，均属此类。
15. **表格列归属靠语义推断必错**。统计界值表常有「无效性边界 / 有效性边界 / 累积 α 消耗」等多组顶层列，按语义分组会把列塞错组。
    - 必须回到**坐标**：打印各顶层表头文字的 x 中心，按 x 区间归属。本次表 18 靠 `Cumulative@484` vs `Futility@302` / `Efficacy@401` 才发现归错。
    - 同理，合并格会自动减少单元格数，回填时要按跨度展开补空串，否则整行错位。
16. **Git Bash 下传给 pymupdf 的路径必须是 Windows 形式**。`pymupdf.open("/c/Personal/...")` 报 `no such file`，要写成 `C:/Personal/...`。另外用户可能在任务中途移动源文件，脚本里用 `os.walk` 动态查找比硬编码稳。

## 遇到看不了图片的模型时

若当前模型无法查看图片，不要反复尝试 Read 图片（会一直返回 "does not support images"）。改用数值化验证：

- `scripts/scan_pages.py` 快速定位「有视觉内容但提取为空/偏少」的页
- `scripts/audit_figs.py` 做反向查漏图 + 正向查槽位 + 产物查图
- `scripts/audit_title_outside.py` 抓「标题整块留在框外」
- `scripts/figmap_check.py` 抓「并排图合并导致图注错位」
- `scripts/check_crop.py` 判断裁剪是否截断文字
- 直接 dump `figs_meta.json` 的 bbox 与 `get_text('dict')` 的文本块坐标，用坐标算术确认标题/来源行落在裁剪框内
- 打印 `clusters()` 的中间输出，确认碎片合并是否符合预期（如底纹表格是否被拆成两张）

## 译文之后：要点总结与分析

用户通常还会要求「译后独立成章」的总结。三段式，简明不复述译文：

1. **核心主题与主要结论**（3–5 条）
2. **关键数据、时间节点、约束条件、决策依据**（用表格，标数字 + 来源 + 时间）
3. **值得关注的判断、风险提示、待确认事项**（含原文笔误、重复章节、数据矛盾）

写成 `out/zh/part_99_summary.md`，`build.py` 会自动排到最后。总结里的数字必须回 `out/full_raw.txt` 核对，不要凭记忆写——研报里同一指标在不同章节常有出入。

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `scripts/extract_text.py` | PDF → 带页码分隔的纯文本 |
| `scripts/figs_extract.py` | 连通域定位图区 → 裁剪渲染 JPEG + meta json |
| `scripts/scan_pages.py` | 逐页体检：定位「有视觉内容但提取图数偏少」的页 |
| `scripts/audit_figs.py` | 全量审计：反向查漏图 + 正向查槽位 + 产物查图 |
| `scripts/audit_title_outside.py` | 审计图框上方 20–75pt 是否漏裁标题 |
| `scripts/figmap_check.py` | 核对 `@@FIG` 槽位映射：图注与图是否错位 |
| `scripts/build.py` | Markdown 分段 + 图 → 单文件 HTML |
| `scripts/verify.py` | 结构完整性校验（页锚 / 图槽 / 标签平衡） |
| `scripts/coverage.py` | 逐页覆盖率：中文字数 ÷ 英文词数，抓漏翻页 |
| `scripts/check_crop.py` | 图片裁剪是否截断标题/来源行的自动检查 |
| `scripts/redact.py` | 删除收件人身份标识（Cowen 团队邮箱 + 「仅供 X 使用」声明）；支持 md 与 html，幂等 |
| `scripts/check_redaction.py` | 判别「视觉脱敏（可恢复）」还是「真脱敏（不可恢复）」：统计黑框数 / 被覆盖 span / ■ 占位字形，输出结论 |
| `scripts/grid_table.py` | 难表格坐标重建：横线分带 + 竖线分列 + 合并格检测 → Markdown 表，支持跨页与多层表头 |
| `assets/shell.html` | 页面骨架（含 `__TITLE__` / `__CSS__` / `__TOC__` / `__BODY__` 占位） |
| `assets/style.css` | 深灰 + 翠绿终端风样式，含打印样式 |

> **共用约定**：`extract_text.py` / `check_redaction.py` / `grid_table.py` / `redact.py` / `coverage.py`
> 属「前端」，被 `Report-Full-TNA-docx` 以 `$SHARED` 路径直接调用；改这些脚本时**两边同时受益/受影响**。
> 只有 `build.py` / `verify.py` / `figs_extract.py` 与图相关脚本是 HTML 侧独有。

## 交付清单（每次收尾前自检）

- [ ] `figs_extract.py` 已跑，且 `scan_pages.py` / `audit_figs.py` / `audit_title_outside.py` / `figmap_check.py` 无异常
- [ ] 已处理封面误检、正文误检、跨页表格等需人工精修的情况
- [ ] `verify.py` 六项全绿
- [ ] **通用 HTML 校验补查**（**可选**：`verify.py` 不覆盖锚点解析/外部依赖/占位符这三项；需已安装 `long-html-report-pipeline` 技能，未安装可跳过本条）：
      `python ../long-html-report-pipeline/scripts/merge_and_validate.py --frags <产物>.html --out /tmp/_check.html`
      → 需 PASS；`}}` 若来自 CSS `@media{…{…}}` 属正常（脚本已剔除 style，不应再报）
- [ ] **收件人身份标识已删除**：`grep -c "pharmateam@\|biotechteam@\|medtechteam@\|Unauthorized distribution prohibited" 产物.html` 为 0；且免责声明里的功能性邮箱（如 `Privacy.EAP@tdsecurities.com`，属机构公开联系方式而非收件人标识）仍在
- [ ] **无 repr 残留**：`grep -c "\['" 产物.html` 为 0（见第 10 条坑）
- [ ] **无聚类 bug 残留**：`grep -n "|= r\|= c" scripts/*.py` 应为空（见第 11 条坑）
- [ ] **脱敏 PDF 已按判别流程处理**：■ 残留计数 = 0（视觉脱敏文件）或占位符均有注明（真脱敏内容）；结尾术语清单已列
- [ ] 抽查 3–5 张图，确认标题与来源行未被截断、未被多余正文污染
- [ ] TOC 层级正确、锚点可跳转
- [ ] 「要点总结与分析」章节已追加（**Profile A 研报**）
- [ ] `present_files` 已调用

**Profile B（临床方案）额外自检**

- [ ] 已跑 `check_redaction.py` 判别脱敏类型；若为视觉脱敏，■ 残留 = 0 且涂黑内容已译出
- [ ] 未做任何替换的完整文本备份仍在（`full_raw_full.txt`）
- [ ] 网格大表（SoA 等）用 `grid_table.py` 重建，**输出行数/列数与 PDF 肉眼可见的行列数一致**（行数骤减 = 踩了表头去重坑或 `--pages` 漏了表头所在页）
- [ ] 统计界值表的列归属经**坐标**验证，非语义推断
- [ ] 表格已译为中文；参考文献保留英文
- [ ] 结尾「保留未译与存疑术语清单」三段齐全（保留英文 / 存疑说明 / 脱敏恢复范围）
- [ ] 页数校验：原文 N 页 + 术语清单附页 → `verify.py` 传 **N+1**
