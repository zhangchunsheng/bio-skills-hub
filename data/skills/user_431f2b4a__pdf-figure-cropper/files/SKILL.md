---
name: pdf-figure-cropper
title: 论文PDF图片自动切割
description: 论文PDF图片自动切割：把论文里的所有Figure一键切成独立高清PNG（300 DPI），子图字母、轴标签一个不丢，不混入正文、不残留图注。三种模式任选——只切整张大图、只切Figure内部的A/B/C小图、或整图+子图都切；图注跨页自动兜底；同一页多个figure自动按条带精准分离，互不污染；子图按标签/墨迹定位后自动合并标题、图例等附属块，避免"一个子图切成两半"。切完自动核对数量并输出报告，明确提示自动切割不保证100%准确、尤其子图可能出错需人工复核。Nature/Cell/ACS/NEJM等主流期刊版式开箱即用。当用户提供论文PDF，要求提取、切割、导出其中的图片、figure、插图、图表，或需要把Figure内部的A/B/C小图单独切出时，使用此技能。
agent_created: true
---

# 论文PDF图片自动切割（pdf-figure-cropper）

将学术论文 PDF 中的每个 figure（含所有子图、矢量图、位图、子图标签、轴标签）切割为独立高清 PNG，不混入正文文字、不残留图注、不切丢子图。

**v3.0 三模式**：
- `--mode whole`：只切整张大图，输出 `Fig_1.png`（`whole/` 目录）。
- `--mode subfig`：只把 figure 内部的 A/B/C 子图单独切出，输出 `Fig_1_a.png`、`Fig_1_b.png`…；无法识别标签时自动退化为墨迹间隙分割，输出 `Fig_1_p1.png`、`Fig_1_p2.png`…并标记低置信度（`subfig/` 目录）。
- `--mode both`（默认）：整图+子图都输出。

**v3.0 相比 v2.1 的主要改进**：

1. **一页多图精准分离**：同页有多个 figure 时（如 Elsevier 页10 同时有 Figure 8/9/10），按页分组、按图注把页面切成不重叠条带，每个 figure 只在自己条带内定界，彻底避免互相污染、整图把整页内容都装进去。
2. **子图防切半**：墨迹分割后新增合并规则 `merge_ink_regions`——把**高度显著矮且与主体紧邻**的标题/图例/被切断块并入最近主体（实测对比：Fig_3 饼图+图例从 10 块合并为 5 块完整饼图），同时对间距较大的真实子图（两个分子结构）保持不合并。
3. **输出精简**：CSV 报告改为简洁英文表头（`name,type,confidence,label_page,cut_page,pixel_size,file_path`），去掉参考价值低的 score 列；不再生成 report.json 与 contact_sheet 拼图。
4. **提速**：整页一次 300dpi 渲染 + PIL 按 bbox 裁剪（替代每子图单独 clip 渲染），一页多图时显著减少重复渲染。
5. **边界诚实**：完成时明确提示"自动切割不保证 100% 准确，尤其是子图可能切割错误，请人工核对确认"。

核心架构：**按页分组 + 锚点/条带定界 + 子图检测（标签/Voronoi + 墨迹分割+合并）**：

- **整图定界（锚点法）**：图注标签锚点 + 视觉元素并集定界（主流期刊，高置信度，含跨页兜底）；定界时自动排除页眉/页脚细分割线、两端对齐的正文段落块、「Table N」表格区（从表格标题洪水填充连通框线），只保留与图形核心区相交/邻近的文本。
- **一页多图（条带化）**：同页多个图注标签按 y 切条带，上一图注下边界 ~ 本图注上边界；图注跨页时（仅单图页）去下一页兜底。
- **子图检测**：
  1. 字体/字号聚类（按 `(字体名, 字号, 是否粗体)` 聚类单字母，取连续 `a/A` 前缀）识别子图标签；
  2. k-means Voronoi 分区：以标签中心为种子划分各子图区域；
  3. 并集定界：分区内对矢量/位图/文本取 bbox 并集；
  4. 兜底：无可靠标签时用墨迹投影间隙分割，再做 `merge_ink_regions` 合并附属块（低置信度）。

## 何时使用

- 用户给出学术论文 PDF，要求把其中的 figure/图片/插图提取或切割为独立图片文件。
- **必须是有文本层的生成版 PDF**（非扫描版）。v3 不再支持扫描版兜底。
- 期刊标签格式无需用户关心：内置 nature / generic / springer 三组正则自动探测；特殊格式用 `--label-regex` 定制。

## 环境准备

依赖 pymupdf 与 pillow（Python >= 3.9），首次使用前安装：

```bash
python3 -m pip install pymupdf pillow
```

若在 WorkBuddy 沙箱内执行，优先使用托管 Python：
`~/.workbuddy/binaries/python/envs/default/bin/python -m pip install pymupdf pillow`

（无 pillow 时脚本自动回退到 pymupdf 逐图渲染，速度略慢但功能不受影响。）

## 执行流程

### 1. 运行切割脚本（一体化：探测 + 切割 + 报告）

```bash
python3 <skill-dir>/scripts/crop_figures.py <PDF路径> --out figures_auto
```

默认 `--mode both`（整图+子图都输出）。如需只切整图或只切子图：

```bash
python3 <skill-dir>/scripts/crop_figures.py <PDF路径> --out figures_auto --mode whole
python3 <skill-dir>/scripts/crop_figures.py <PDF路径> --out figures_auto --mode subfig
```

默认即全自动：预检文本层 → 标签正则自动探测 → 锚点/条带定界（含一页多图、跨页兜底）→ 子图检测（标签 Voronoi / 墨迹分割+合并）→ 并行 300dpi 渲染 → 输出 CSV 报告。

### 2. 按输出处置异常

| 输出 | 含义 | 处置 |
|---|---|---|
| `疑似扫描版` | 文本字符 < 1000 | v3 不支持扫描版，任务失败；需改用 OCR 或人工 |
| `所有内置预设均未匹配到图注标签` | 期刊格式陌生 | 用 `--label-regex` 定制 |
| 检出标签数远少于实际 figure 数（如 11 图只检出 1 个） | 期刊用 `Figure N`（无点号，Elsevier 常见）等非内置格式 | 先用 pymupdf 确认该标签在 PDF 中独占成行，再用 `--label-regex '^Figure\s+(?P<num>\d+)\s*$'` 重跑 |
| `未检测到图注标签` | 无匹配 | 换 `--preset` 或 `--label-regex`；或确认 PDF 有文本层 |

### 3. 验证（不可跳过）

脚本自动完成数量核对并输出 CSV 报告。**执行者须人工核对**：打开 `whole/`、`subfig/` 目录浏览切出的图片，重点检查：子图是否完整、有无正文混入、有无图注残留。低置信度子图（`low`，来自墨迹分割）必须重点核对。

> 自动切割不保证 100% 准确，尤其是子图可能切割错误（过度合并或切碎），请人工复核确认。

## 参数速查

| 参数 | 默认 | 说明 |
|---|---|---|
| `--out` | figures_extracted | 输出目录（内有 whole/ 与 subfig/） |
| `--dpi` | 300 | 渲染 DPI |
| `--preset` | auto | 标签正则：auto 自动探测 / nature / generic / springer |
| `--label-regex` | - | 自定义正则，须含 `(?P<num>...)`，可选 `(?P<ext>...)` |
| `--mode` | both | 切割模式：whole（整图）/ subfig（只子图）/ both（整图+子图） |
| `--header` / `--footer` | 42 / 40 | 页眉底/页脚上截止线（pt） |
| `--jobs` | 0 | 并行进程数（0=自动 min(4,核数)，1=关闭） |
| `--figures` | - | 只切指定图（如 `1,3,5` 或 `Fig_2,ED_Fig_1`） |
| `--preview` | - | 快速预览（72 DPI 低分辨率） |
| `--refine-edge`（`--no-refine-edge` 关闭） | 开启 | 边缘精化 |
| `--cache`（`--no-cache` 关闭） | 开启 | 预解析缓存 |

## 性能基准（实测，M1 Pro，4 进程，`--mode both`）

| 论文 | 输出 | 耗时 |
|---|---|---|
| 27 页 Nature（13 figure） | 13 张整图 + 113 张子图 | ~14.5 s |
| 14 页 Science Advances（7 figure） | 7 张整图 + 39 张子图 | ~4.4 s |
| 13 页 Elsevier（11 figure，`--label-regex` 定制 Figure N） | 11 张整图 + 39 张子图 | ~1.1 s |

主要耗时在 300dpi 渲染，已按页并行 + 整页预渲染裁剪优化。同页多图（如 Elsevier 一页 3 张 figure）提速明显。

## 已知局限

- **必须是有文本层的 PDF**；扫描版不支持（v3 已移除扫描版/模型兜底）。
- 依赖图注与图形在同一页或相邻页；图注跨页时仅单图页支持；图注与图形间隔超过一页不支持。
- 子图模式优先检测文本层中的 A/B/C 标签（Nature/Wiley 等）。若标签被烤进位图/矢量图（Science Advances、Elsevier 常见），会诚实退化为墨迹分割，标记低置信度。
- 墨迹分割 + 合并为启发式，对"标题/图例与被切主体"或"相邻真实子图高度悬殊"等情况可能过度合并或不足，需人工核对（CSV 的 confidence=low 即此类）。
- 一页多图要求各图注标签在同一页；若图注跨页，最多跨页兜底到下一页。
