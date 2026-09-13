# 质量检查清单（Checklist）

这个清单来自"一人公司"分享 PPT 的真实迭代过程。每一条都是踩过坑之后总结的，按重要性排序。

生成 PPT 前，先通读一遍；生成后，逐项自检。

---


## 🟣 Design System Specification (`design.md`) 架构自检

以下检查适用于使用 `design.md` 设计规范体系生成的 HTML 演示文稿。

### B-0. 设计系统与渐进式加载（Progressive Disclosure）
- 生成前先读取 `designs/bold-template-pack/selection-index.json` 索引进行风格匹配。
- 选定风格后，只单点读取该风格对应的单份 `design.md`（如 `designs/bold-template-pack/templates/<slug>/design.md` 或 `designs/STYLE_PRESETS.md`）。
- 严格遵循 `design.md` 中定义的 Design Tokens（Google Fonts / Fontshare 字体导入、色盘、阴影堆栈、字号 `clamp` 规范）。

### B-1. 页面必须带主题/色彩规范
每个 `<div class="slide">` 应遵循 `design.md` 中的主题规范。Hero 页与过渡页应与正文页形成视觉对比与律动。

### B-2. 全局色彩基调统一与防频闪规范 ⭐
- **现象**：整套 PPT 一页深色一页浅色黑白交替，导致观众眼睛在强光与暗光之间反复适应，产生强烈的频闪眩光（Visual Whiplash）与视觉疲劳。
- **做法**：整套演示文稿必须保持全局色彩世界观的高度纯净与一致，默认采用 **100% 全套统一纯深色（Unified Dark Mode）或 100% 全套统一纯浅色（Unified Light Mode）**。严禁逐页黑白无故交替闪烁。唯一豁免：大型长篇演说中仅允许封面/封底/章节过渡大幕页采用深色反差聚焦，而正文内容页（90%+）必须保持绝对统一的底色基调。

### B-3. 动画标记
每页至少给 kicker、主标题、lead、卡片/图表等 3 个以上元素加 `.anim` 与 `.d1`~`.d8` 延迟类。Hero 页核心块必须全部加动画。

### B-4. 智能图表与数字动画
- `.smart-chart` 必须包含合法的 `data-chart` JSON。
- `.count-up` 必须包含 `data-value`。

### B-5. 图片与图标
- 图片路径使用相对路径 `images/xxx.png`。
- 不使用 emoji 作图标；使用 Lucide 图标。
- 不给图片加厚重阴影或边框；使用 `.frame-img` 容器。

### B-6. 双轨间距规范自检（首页舒展大气 ↔ 正文紧凑空间让渡）⭐
- **现象**：
  - 正文页：Badge（分类标签）、主标题（h1/h2）、副标题（tagline/lead/金句）层层堆叠 20~30px 大外边距，导致页眉区域占据 35%~45% 画布高度，下方核心卡片或架构图被严重压缩下挤。
  - 首页 PPT：错误套用了正文的 6~8px 紧凑压缩，导致 Badge、主标题、副标题挤在一起，缺乏大气开阔的视觉冲击力。
- **做法（场景双轨分流）**：
  - **🟢 仅首页 PPT / 封面页（Cover Slide / Hero Slide）—— 开阔舒展宽纵向间距**：
    - 豁免紧凑压缩，为门面标题与金句赋予充裕留白与视觉呼吸感；
    - **Badge 与主标题间距**：`16px ~ 28px`（如 `DESIGN CANVAS` 与主标题）；
    - **主标题与副标题/金句间距**：`20px ~ 32px`（如 `写 Skill 前先回答四个问题` 与金句引导语）；
    - **副标题与下方元素间距**：`36px ~ 56px`（如与 Stats/Divider/作者信息）；
    - 推荐使用 `.cover-frame` 或 `.slide.hero` 舒展居中/左对齐容器。
  - **🔵 正文内容页（Content Slides）—— 严格执行页眉三要素紧凑压缩**：
    - 严格压缩页眉总高度至 **<= 200px（约占 1080p 画布的 18%~22%）**；
    - Badge 与主标题间距：`6px ~ 8px`；
    - 主标题与副标题间距：`8px ~ 12px`；
    - 副标题与主内容区间距：`16px ~ 24px`；
    - 推荐使用 `.header-compact` 容器、`.header-split`（左标题 + 右副标题左右水平分栏）、或主标题前缀行内徽章；
    - 严禁用带有厚重 padding 的独立 Card 容器包裹副标题从而挤占主内容空间；
    - 确保下方核心内容区（卡片网格、流水线、数据图表）拥有 **78%~82% 充足纵向展开空间**。

### B-7. 底部导航控制台四件套（上一页、下一页、全览、全屏）与全景缩略自检 ⭐
- **现象**：
  - 生成的 PPT 缺少控制按钮，或者仅有简单的小圆点/箭头，无法直观跳页与全览。
  - **全览标题/摘要大面积空白或卡片坍塌**：在全览模态框中，除首页外其余卡片（P02~P15）标题与描述全部空白、卡片高度被压成细扁条。**根因**：代码错误使用了 `innerText`（非激活幻灯片带有 `visibility: hidden`，浏览器 DOM `innerText` 会直接返回空字符串 `""`），且 `.overview-card` 缺少 `min-height`。
- **做法**：
  - 必须包含标准毛玻璃悬浮控制栏 `.controls-bar`，配备完整的四大操作按键：
    - `◀ 上一页` (`prevSlide()`)
    - `01 / 15` 页码与动态进度条
    - `下一页 ▶` (`nextSlide()`)
    - `🗂 全览` (`toggleOverview()`)
    - `⛶ 全屏` (`toggleFullScreen()`)
  - 必须包含 `#overviewModal` 全景缩略图网格容器与 JS 构建逻辑，支持点击任意卡片瞬间跳转并关闭全览。
  - **全览构建提取硬规则 (buildOverview)**：
    - **必须优先使用 `textContent` 而非 `innerText`**（如 `titleEl ? (titleEl.textContent || titleEl.innerText || '').trim() : ''`），确保即使幻灯片处于 `visibility: hidden` 也能完整提取标题与副标题。
    - `.overview-card` 必须设置 `min-height: 130px; box-sizing: border-box;`，确保卡片在各种内容长度下高度整齐统一，杜绝高度坍塌。
    - 标题选择器必须覆盖全：`h1, h2, h3, .slide-title, .h-hero, .h-xl, .h-lg, .h-md, .display-hero, .display-chapter, .cover-title, [data-title]`，并提供 `第 N 页` fallback。
  - 必须支持全套快捷键：`←`/`→`/`Space` 翻页，`O` 打开全览，`F` 全屏，`Esc` 退出全览/全屏。

### B-8. 主要内容大字号高可读性自检 (High-Legibility Large Font Standard) ⭐
- **现象**：生成的 PPT 在 1920×1080 舞台下文字字号过小（如正文 13px~16px、副标题 16px），缩放至笔记本或移动屏幕时字号收缩到 7px~10px，造成文字拥挤、像密密麻麻的 Word 文档，严重损害演说可读性。
- **做法**：
  - 严格遵循大字号标准阶梯：
    - **分类微标签/徽章** (`.eyebrow-pill` / `.kicker` / `.slide-label`): `16px ~ 18px` (`font-weight: 800`)
    - **主标题** (`.slide-title` / `.h-xl`): `48px ~ 54px` (`font-weight: 800/900`)
    - **副标题/金句引导语** (`.slide-subtitle` / `.lead` / `.tagline`): `22px ~ 26px` (`font-weight: 600`)
    - **卡片/分栏标题** (`.b-card h3` / `.card-title`): `26px ~ 28px` (`font-weight: 800`)
    - **卡片正文/主要段落** (`.b-card p` / `.card-text` / `p`): `20px ~ 22px` (`line-height: 1.62`)
    - **列表项/Bullet Items** (`.b-card li` / `.feature-desc`): `19px ~ 21px` (`line-height: 1.6`)
    - **数据大数字** (`.stat-nb`): `56px ~ 72px`，**数据标签** (`.stat-label`): `16px ~ 18px` (`font-weight: 700`)
    - **流水线/Pipeline** (`.step-nb: 19px~20px`, `h3: 24px`, `p: 19px`)
    - **表格** (`.data-table`): `th: 21px (w:800)` / `td: 20px (line-height: 1.5)`
    - **代码块** (`.code-block`): `19px ~ 21px` (`line-height: 1.65`)
    - **金句/引用与 Callout** (`.quote-text: 34px`, `.callout: 23px`)
    - **底栏控制按钮** (`.ctrl-btn` / `.slide-counter`): `16px` (`font-weight: 700/800`)

### B-9. 默认支持鼠标双击图片放大自检 (Default Double-Click Image Zoom & Lightbox) ⭐
- **现象**：幻灯片中的图片展示尺寸有限，演讲者或观众双击图片时无法查看大图细节。
- **做法**：
  - 页面原生内置 Lightbox 交互脚本，所有幻灯片中的 `<img>` **默认支持鼠标双击（dblclick）全屏毛玻璃放大**。
  - 支持再次双击、点击背景、点击右上角关闭按钮或按 `Esc` 键退出大图。
  - 同页多张图片支持键盘 `←` / `→` 键及悬浮翻页按钮自由切换查看。全屏图片专注纯净大图视觉，旁边及下方不展示多余文字或描述。

### B-10. 图片/图标/序号徽章与标题单行同行并排自检 (Inline Icon, Badge & Title Standard) ⭐
- **现象**：
  - 卡片（`.card` / `.b-card` / `.feat-card`）、架构层级（`.stack-row` / `.tier-card`）、流水线步骤（`.pipeline-step` / `.step`）中，序号徽标（如 `01` / `1`）、图标/Emoji（如 `💳` / `📄` / `✦`）作为独立 block 元素放置在标题上方，强制拆为上下两行展示，导致卡片纵向空间被无谓挤占、标题与图标产生视觉割裂。
- **做法**：
  - **单行同行并排原则**：图片、图标、Emoji 或序号徽标必须与对应的标题文字在同一行水平并排展示。
  - **标准写法**：
    - 方案 A（水平弹性容器）：使用 `.card-header` / `.card-title-row` / `.step-header` 配合 `display: flex; align-items: center; gap: 10px~14px;`；
    - 方案 B（标题内前置）：直接在 `<h3>` / `<h4>` 内前置 `<span class="card-num-badge">01</span>` 或 `<span class="icon-box">💳</span>`。
  - **豁免与折行例外 (Exemption Rule)**：除非在极端窄栏宽度或超长标题文字场景下，图片/图标与文字在一行内确实无法完整容纳导致文字溢出折断，才允许酌情拆分为两行展示。

## 🔴 P0 · 一定不能犯的错

### 0-S. Swiss locked mode:正文页必须来自原始 22P

**现象**:颜色、字体看起来像 Swiss,但标题跑到中间、图片不在网格上、页面结构和原始 22P 完全不是一套东西。

**根因**:生成时把 Swiss 当成风格包,自由组合了新的 P23/P24/自绘 SVG 页面,没有从原始参考 PPT 的 22 个登记版式里选。

**做法**:
- 先读 `references/swiss-layout-lock.md`
- 正文页只能使用 `S01-S22`;新增首页/尾页只能使用 `SWISS-COVER-ASCII` / `SWISS-CLOSING-ASCII`
- 每个 `<section class="slide">` 必须写 `data-layout="Sxx"`
- 生成后必须运行:

```bash
node <SKILL_ROOT>/scripts/validate-swiss-deck.mjs path/to/index.html
```

**校验会拦截**:
- 未登记版式 / 缺少 `data-layout`
- P23/P24 实验结构
- SVG 里写可见文字
- S22 图片未绑定 `s22-hero-21x9`
- S22 照片使用 `object-position:top center`

### 0-S-2. Swiss 顶部标题默认左上,不是居中

**现象**:最顶上的中文标题在页面中间,像一页自制海报,不再像原始 PPT。

**做法**:
- 除 `S03/S09/S10` 这类 statement/split 版式外,顶部标题必须贴原始模板的左上内容轴。
- 不要把小标题放左列、大标题放右侧大列,这会导致标题视觉居中。
- 如果需要标题 + 说明两列,必须复制原始 `S11` 或 `S17` 的骨架,不要自写 `4fr 8fr`。

### 0-S-3. Swiss 地图页必须用 S08 Map Component

**现象**:地点/历史内容只画了简易 SVG 地图,没有真实点位、关系卡片、缩放/拖动控制,或滚轮触发了 PPT 翻页。

**做法**:
- 使用 `data-layout="S08"`。
- 先读 `references/swiss-map-component.md`。
- 右侧地图组件必须包含 marker 点、连接线、地点卡片、`+` / `-` / `DRAG` 控制。
- 默认禁用 scroll zoom 和 drag pan;用户点击 `DRAG` 后才允许拖动。
- 必须保留静态 fallback,地图 CDN 或瓦片失败时仍可读。

**检查**:
- `grep -n "data-map-ctrl" index.html`
- `grep -n "maplibregl.Map" index.html`
- 浏览器实测 `+` 可放大,`DRAG` 可切换为 `DRAG ON`

### 0-S-4. Swiss 演示字号不能小到看不清 + 字重阶梯必须遵守

**现象**:瑞士风页面整体结构没问题,但图注、说明、时间线、KPI note、卡片小字在投屏时看不清;或者 16px 小字用了 weight 300 导致又小又细。

**做法(字号下限)**:
- 正文段落 / 主要说明 ≥ `18px`
- 卡片描述 / 列表 / 时间线说明 / caption / 图注 ≥ `16px`
- meta / kicker / mono label / 图表标签 ≥ `14px`
- 内容超出时,先删减文案、拆页或换 Sxx 版式,不要用 10/11/12/13px 小字硬塞。

**做法(字重阶梯 ⭐)**:
瑞士风坚持"越大越细,越小越粗",字号与字重必须成反比阶梯:
- ≥ 8vw → weight **200**(ExtraLight)
- 4-7.9vw → weight **200-300**
- 1.8-3.9vw → weight **300-400**
- 1-1.7vw / 16-20px → weight **400-500**
- 13-15px → weight **500-600**
- 同一页内,字号小的元素字重必须 ≥ 字号大的元素。
- **16px 左右小字禁止使用 weight 300**(太细不可读),最低 400,推荐 500。
- 封面/IKB 反白大标题内强调字用 `italic + weight 300`,不要用 accent 色。

**检查**:
- `rg -n "font-size:(10px|11px|12px|13px)|max\\((9|10|11|12|13)px" index.html`
- `rg -n "font-weight:(300)" index.html | rg -v "min\(|h-xl|h-hero|h-statement|num-mega|kpi-thin|name-mega|8vw|9vw|1[1-9]vw|cover-|\.multi"` —— 检查 weight 300 是否落在了小字号上
- 浏览器以 100% 缩放查看,底部 note、caption、timeline label、卡片描述仍能一眼读清。

### 0-A. 瑞士风画布对齐法则(每一页必查 · 最常踩)

**现象**:页眉 chrome-min 和底部 footer 都靠在 5vw 的边线上,但中间区域往内缩了一截,左右对不齐。

**根因**:`.canvas-card` 已经自带 `padding:5.6vh 5vw 4.4vh`。如果在主体区再写 `padding:5vh 5vw 4vh`,水平方向就变成 `5vw + 5vw = 10vw`,主体比 chrome-min 多内缩 5vw。

**做法**:
- 主体那层 `padding:0`,只用 grid `gap` 控垂直间距
- chrome-min 与主体之间的间距由 `.chrome-min{margin-bottom:48px}` 提供,**不要**在主体顶部叠 `margin-top` / `padding-top`
- split 模式例外:`.slide.split .canvas-card{padding:0}`,两个 `.half` 自己定 `padding:5.6vh 3.6vw 4.4vh`

```html
<!-- ❌ 错:主体多缩了 5vw,左右对不齐 -->
<div class="canvas-card">
  <div class="chrome-min">...</div>
  <div style="flex:1;padding:5vh 5vw 4vh;...">主体</div>
</div>
<!-- ✅ 对 -->
<div class="canvas-card">
  <div class="chrome-min">...</div>
  <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:3vh">主体</div>
</div>
```

**自检命令**:`grep "padding:.*5vw" index.html`,如果命中 `padding:Xvh 5vw Yvh` 在 canvas-card 直系子元素里,就是错的(.half / 装饰层除外)。

### 0-B. 瑞士风 head 区:kicker 必须在大标题"上方"(不要左右排)

**现象**:小标题(`.t-meta` / `.t-cat`)和大标题被挤在同一行,左侧一坨小字、右侧一坨大字,头部失去层级。

**根因**:`grid-template-columns:auto 1fr` 把两个本该上下叠的元素压成左右两列。

**做法**:
```html
<!-- ❌ 错 -->
<div data-anim="head" style="display:grid;grid-template-columns:auto 1fr;gap:3vw;align-items:end">
  <div class="t-meta">METHODOLOGY · 03</div>
  <h2 class="h-xl-zh">为什么是 N+1</h2>
</div>
<!-- ✅ 对 -->
<div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
  <div class="t-meta">METHODOLOGY · 03</div>
  <h2 class="h-xl-zh">为什么是 N+1</h2>
</div>
```

例外:head 一行同时承载"左:kicker+大标题(自己上下叠)"和"右:小注脚",外层可以用 `display:grid;grid-template-columns:1fr auto`,但**内层**仍要保持 flex column。

### 0-B-2. 瑞士风封面 / 封底默认:IKB 满屏 + ASCII 呼吸场 + 白色 weight 200(强制)

**现象**:封面用 `slide light` 白底 + 黑字 + 一个大大的"01"——同时 chrome 角标已经写了 `01 / 07`,屏幕上出现两个"01",视觉重复;白底太普通,完全没有"开场打招呼"的仪式感。

**根因**:layouts-swiss.md 旧版默认推荐左 ink + 右 paper 对开,实操中容易写成"白底 + 黑大字 + 编号大字",失去 IKB 这个标志色的开场冲击。

**做法**(瑞士风必守):
- **封面强制 `<section class="slide accent">`**(满屏 IKB),不要 `slide.light`,也不要 `slide.dark`;在 `.canvas-card` 内**第一个子元素**插入 `<canvas class="ascii-bg">`(ASCII 字符呼吸场,模板自带 IIFE 自动激活)
- **不要再写"01"等编号大字**:`.chrome-min` 已经显示 `01 / N`,封面再放一个巨大的"01"=同义重复,直接删掉
- **强调字必须用斜体**:`font-style:italic;font-weight:300`,**禁止**用 `color:var(--accent)`——IKB 蓝压 IKB 蓝,人眼看不见任何强调
- **封底强制 `slide.split`** 双半屏,左半 `.half.b-accent` + ASCII canvas(与封面色彩闭环),右半 paper 白底放 3 条 takeaway;**第 03 条**用 `var(--accent)` 上色,完成"开场全 IKB ↔ 收尾半 IKB"的色彩闭环
- ASCII canvas 在模板的 `<style>` 里已经预设 `mix-blend-mode:screen;opacity:.92`,不要去动这个值
- 封面/封底主标题字号双约束:`min(11.6vw,19vh)` ~ `min(8vw,14vh)`(遵守 Y ≥ X × 1.6 规则)

**自检命令**:
- `grep -c "ascii-bg" index.html`——封面 + 封底应至少命中 ≥ 2(各一个 canvas)
- `grep -E '"slide accent"' index.html | head -1`——封面应是 `slide accent` 而非 `slide light`
- `grep "color:var(--accent)" index.html`——若命中行同时含 `font-style:italic` 即危险信号(蓝压蓝),改为只 italic 不 accent;只有封底"03 takeaway"那一处用 `var(--accent)` 是合法的(此时背景是白色)
- 目视:打开页面看封面有没有"01"等大编号——有就删

### 0-C. 瑞士风大字号双约束:`min(Xvw, Yvh)` 中 Y ≥ X × 1.6

**现象**:在 16:9 标准屏(MacBook 13/14/16,常见显示器)打开,标题字号比预期小一截,整页内容显得空旷或缩水。

**根因**:1vw : 1vh ≈ 1.78,如果写 `min(7vw, 10vh)`,在 16:9 屏 7vw = 12.46vh,会被 10vh 上限截断到 10vh,字号缩水 20%。

**做法**:推荐数值速查
| 用途 | 推荐 |
|---|---|
| h-hero 巨字宣言 | `min(11.6vw, 19vh)` |
| h-xl 章节标题 | `min(7vw, 12vh)` ~ `min(7.4vw, 13vh)` |
| 大数字 KPI | `min(8.4vw, 14vh)` |
| 中数字 / 编号 | `min(4.6vw, 8.5vh)` ~ `min(5.6vw, 10vh)` |
| 副标 | `min(7.6vw, 13vh)` |

**自检命令**:`grep -E "font-size:min\([0-9.]+vw,\s*[0-9.]+vh\)" index.html`,把所有命中的 X/Y 看一眼,任何 Y/X < 1.6 都改大。

### 0-D. 图片处理范式:8 套范式 + 1 个 T8 例外(所有主题通用)

**现象**:图片像普通 PPT 插图,圆角+阴影+1px 边框当默认;多张截图高度不一;figcap 写"原始截图/产品截图/Screenshot"等空标签;LLM 把旧 `.frame-img` 卡片范式带回到新 deck。

**根因**:没有用 8 套图片处理范式(T1-T8),回退到"圆角+阴影+figcap"那套旧范式。完整规范见 [`image-treatments.md`](image-treatments.md)。

**适用范围**: 本节适用于**所有主题**(Beautiful Modern、Swiss、Cyberpunk 等),不限于瑞士风。瑞士风是"最严格"的子集(全部 8 套范式都禁止圆角和阴影);Beautiful Modern 允许 T8 Edge Card 是唯一例外。

**先判断图像角色**:
- 证据截图、UI、代码、dashboard:保真优先,关键文字和数据不能裁;需要统一比例时先做截图背景画布和 `.fit-contain`。
- 已按槽位生成的信息图/插图:按 S22/S15/S16 的目标比例铺满,不要再缩成短小图片。
- 照片/产品图/人物图:必须写清 `object-position`,主体不能被裁切、标题块或 caption 压住。
- 文字压图:必须先判断是否有足够 quiet zone;没有低细节留白就不要把标题压在图上。
- 多图组:统一比例、高度、容器样式和 caption 密度;视觉角色不同的图不要硬放同一组。

**做法**:
- 先选版式:单张大图 + KPI 用 `S22`;多图用 `S15/S16` 的原始网格骨架改造
- S22 生成图比例固定 `21:9`,并在 `<img>` 上写 `data-image-slot="s22-hero-21x9"`
- 照片默认 `object-position:center 35%` 或 `center center`,不要用 `top center` 截人脸
- 图片容器按场景选范式: 截图用 `.t-inset` (T3),网页用 `.t-browser` (T4),多图用 `.t-quiet` + `.t-quiet-grid` (T6),单图用 `.t-float` (T2)
- **唯一允许圆角+阴影的范式**: T8 Edge Card,仅限 Beautiful Modern 风格的营销首图,且**必须显式标** `class="t-edge-card"`
- Swiss 主题: 即使 T8 也不允许(Swiss 全局规则禁止圆角和阴影,优先级最高)
- 老 `.frame-img` 仍可作 fallback,但**不要再**给它加 `border-radius` / `box-shadow`(默认已是 `0 / none`)
- UI / 信息图 / 流程图若是用户原始截图或文字密集图,使用 `.t-inset` + `.fit-contain`(T3 Inset);若已按槽位重生成,必须用对应比例类铺满容器,例如 `.t-inset.r-21x9` 或 `.t-float.r-16x10`,不能再用固定短高度把图片缩小
- 多图同组必须统一槽位、比例、高度,不要混用
- 用户原始截图要先读 `references/screenshot-framing.md`:优先用 CSS 主题背景 + 程序化缩放/留边/对齐；如完整源码的可选背景已安装才复用，避免为了比例统一重画截图内容
- 截图背景必须跟随当前主题色,且可裁成 `21:9` / `16:10` / `4:3` / `1:1`;背景里不能有标题、页脚、边框、logo、人物或明显主体
- GPT-M 2.0 提示词必须写明:Swiss Style、单一 accent、直角、无渐变/阴影/圆角、无页眉页脚标题角标

- 文字压图 / 全屏主视觉必须先做 quiet-zone 判断:至少约 30% 低细节区域可承载标题;不通过就换图、换裁切或改成图文分栏,不要整页套黑色/白色遮罩

**自检命令**:
- `grep -nE "<img[^>]*>" index.html | grep -v "data-treatment"` ——每张 `<img>` 必须有 `data-treatment` 属性,0 命中才合规
- `grep -nE "frame-img.*border-radius|box-shadow" index.html` ——命中就删(老 frame-img 不应再带圆角阴影,默认已重置为 0)
- `grep -nE "figcap|img-cap" index.html` ——检查 figcap 内容,凡命中"原始截图/产品截图/Screenshot/Untitled/Sample"必须删
- `grep -nE "data-image-slot" index.html` ——Swiss 主题下每张本地图片都应有槽位声明
- `grep -nE "原始截图|产品截图|Untitled screenshot" index.html references/ designs/ resources/ demo/` ——必须 0 命中
- 目视:图片内部如果自带大标题、页码、页脚、角标,优先重生成,不要在页面里再裁切硬救
- 目视:截图外侧背景应该是安静托底,不能比截图本身更抢眼;Swiss 风截图不得出现圆角和投影
- 目视:每张图都有"图片会说话"的感觉,**不要**默认带 `.img-cap` 写"产品截图"这类占位符

### 0-D-2. 瑞士风底部分页安全区:最低处不要碰 nav

**现象**:图片 caption、脚注、timeline 下方 label、底部 KPI 被分页小方块挡住,或者视觉上贴得太近。

**根因**:`#nav` 固定在 `bottom:2vh`,如果主体内容用 `align-self:end` / `align-items:end` / `margin-top:auto` 贴到底,最低处会进入分页区域。

**做法**:
- 主内容最低边缘与分页组件之间至少留 `3vh` 呼吸空间
- 图文页需要底部对齐时,先控制图片高度,再给主体容器加 `.nav-safe-bottom` / `.nav-safe-bottom-tight`
- 其他页面需要贴底时,给主体容器加 `.nav-safe-bottom` 或 `.nav-safe-bottom-tight`
- 不要手写 `bottom:2vh` / `bottom:0` 放说明文字;这会和 nav 抢位置

**自检**:
- 视觉:翻到该页,看最后一行 caption/label 是否明显高于分页组件
- 代码:`grep -E "align-items:end|align-self:end|bottom:0|bottom:2vh|margin-top:auto" index.html`,命中后逐个确认是否有 nav safe zone

### 0-D-3. 后验测量:先量超出和空白,再改版式

**现象**:一页只超出 20-30px,但修的时候删掉大块内容,结果下方多出一大片空白;或者标题与正文贴在一起,肉眼检查时容易漏。

**做法**:
- 生成后运行 `node <SKILL_ROOT>/scripts/validate-swiss-deck.mjs path/to/index.html`
- 如果环境里能解析到 Playwright,校验器会额外执行真实渲染测量:
  - `M1 DOM/visual overflow`:量出超出多少 px,并指出最低/最高的问题元素
  - `M1 bottom whitespace`:量出底部空白和 active content height,防止从"超出"修成"巨空"
  - `M1 nav-safe`:量出最低内容是否进入底部分页安全线
  - `M2 title gap`:量出标题到下一块内容的距离,防止标题和正文贴住

**Overflow 修正阶梯**:
- `1-40px` over:只做微调,上移内容组或收紧一个 gap/padding;不要删内容。
- `40-90px` over:局部压缩 gap/padding 或降低一个模块高度;仍然优先保留内容。
- `90-160px` over:轻微压标题或压缩一段正文,再考虑拆页。
- `160px+` over:才考虑换更高容量版式、合并模块或删内容。

**修完反查**:
- 如果 `M1 bottom whitespace` 变大,说明修过头了;恢复部分间距、放大最后一块或把内容组向下回调。
- 每轮只做一个档位的调整,重渲染后再跑 validator。
- 不要靠多模态肉眼先猜;超出、底部空白和标题间距先看测量值。

### 0-D-4. 发布闸门:正文页内容占用率与“伪填充”

**发布门槛**（1920×1080）:
- 正文页的真实内容组必须覆盖可用舞台高度的 **72%+**，或其最低边缘距导航安全线不超过 **170px**；背景、舞台边框、控制栏、光球和装饰线均不计入。
- 覆盖率不足时，不能把低内容卡片强行拉高，也不能用空白设备框、渐变块或重复标签凑数。补入真实的图表、流程、示例、对比、图片或结构化说明；否则收紧为平衡的居中构图。
- 仅封面、结尾和单句章节转场可以留出大面积负空间，且必须在 slide 上写 `data-density-exempt="cover|closing|divider"`。能力页、流程页、对比页、产品页和数据页不得豁免。

**验收动作**:
- 每页切换后等待入场动效稳定，再在 1920×1080 下检查稳定画面。
- `validate-fluid-deck.mjs` 或 `validate-swiss-deck.mjs` 报出的底部空白/内容高度问题均为返工项；不能仅凭代码静态检查写“已验证”。
- 单个容器中空高度超过其真实内容高度的 40% 时，删减容器或补入有信息价值的内容。

### 0-D-5. 首页主题必须落在视觉中心

**现象**:封面上半页大面积空白，主标题、说明和数据卡整体被挤到下半页；或者一个 `height:100%` 的空包装器居中了，但真实标题仍然偏下。

**做法**:
- 用 `data-cover-subject` 标记主标题、说明与关键数据/主视觉的共同外层；顶部品牌栏、日期和底部页脚不放进来。
- 以该外层中的真实文字、数据、图片和图表的组合包围盒验收。其纵向中心必须落在导航安全区中心上下 8% 范围内。
- 左文右数据的分栏封面按两列整体居中，文字本身可以左对齐；不要把“主题居中”误解为所有文字必须 `text-align:center`。
- 删除用于把内容向下推的大额 `padding-top` / `margin-top`、空占位层和 `justify-content:flex-end`。

**检查**:
- `validate-fluid-deck.mjs` 必须识别 `data-cover-subject`，并报告真实主题组相对安全区中心的偏移。
- 目视检查时先忽略背景装饰，只看标题、说明、数据/主视觉组成的黑白剪影是否在页面中心稳定落座。

### 0-D-6. 正文卡片禁止镂空

**现象**:卡片只有顶部标题与底部说明/列表，中间保留 200~400px 空白；整页看似被卡片“铺满”，实际信息仍然断裂。

**做法**:
- 带背景、边框或阴影的内容面板，内部最大连续空带不得同时超过 180px 和面板高度的 28%。
- 自定义面板添加 `data-panel`；模板中的 `card` / `panel` / `metric` 类会由流式校验器自动识别。
- 删除不必要的固定高度、`height:100%`、过大的 `min-height` 和 `space-between`。内容少时让卡片随内容收缩，再把卡片组整体垂直居中。
- 需要占据较大空间时，必须加入有信息价值的图表、流程、对比、图片或结构化说明；装饰底色、边框和空框不算内容。

**检查**:
- 在稳定渲染帧上检查面板顶部、内容块之间和底部的连续空带。
- 发现“标题在顶、列表在底、中间空一大片”的结构，直接判定返工，不能以整体占用率达标放行。

### 0-D-7. 正文页禁止区块间镂空

**现象**:页眉在顶部、卡片或图表在下方，两者之间横跨页面留出 180~300px 空白；或者页面底部另有流程条，使整体内容占用率看似达标，但中间阅读动线已经断裂。

**做法**:
- 合并普通正文页中可见文字、图片、图表、表格、代码和信息图的纵向范围，检查相邻真实内容组之间的连续空带。
- 内部空带同时超过 **160px** 和 1080p 画布高度的 **14%** 时，直接判定为区块间镂空。
- 优先删除被拉高的 grid/flex 空行、过大的 `margin` / `padding`、空占位层和 `justify-content:space-between`；需要承接信息时加入真实图表、流程、对比或图片，不能用装饰矩形填空。
- 仅 `data-density-exempt="cover|closing|divider"` 可保留有意负空间；能力页、流程页、对比页、产品页和数据页不得豁免。

**检查**:
- `validate-fluid-deck.mjs` 必须同时检查底部空白、面板内部空带和全页区块间空带；任一项失败都不能宣称已验证。
- 目视检查时忽略底色、边框和装饰，只看真实内容的黑白剪影是否形成连续、平衡的阅读节奏。

---

### 0-E. Swiss 模板还原度守卫:原始 PPT 是 golden source

**现象**:生成页看起来像瑞士风,但和原始参考 PPT 的实际字重、间距、时间线、卡片密度不一致;越迭代越偏离参考。

**根因**:把新增图片版式或实验结构写成了全局样式修改,或无意改动了原始基座类,例如 `.h-hero` / `.h-xl` 字重、`.tl-node` 列宽、`.duo-compare` 间距。

**做法**:
- 仓库内的 `assets/template-swiss.html` 是 Swiss 主题的 golden source 快照,但要以**实际页面用法**为准,不要只看未使用的 CSS helper
- 原始页面的大标题大量使用 `font-weight:200`,强调词/数字用 `300`;`.h-hero` / `.h-xl` / `.h-hero-zh` / `.h-xl-zh` 在本模板里必须保持轻字重,不要恢复成 800/900
- 除新增封面/封底 ASCII 机制、S22 图片槽位修复、横向时间线 label 居中修复、以及把标题 helper 校正为实际轻字重外,不要改动原始基座 CSS/JS recipe
- 新增图片能力必须绑定到 S22/S15/S16 原始槽位,不要发明新正文结构
- 如果要修改 `assets/template-swiss.html`,先做原始参考对比;可接受差异只应是 ASCII 类、S22 图片定位类、轻字重标题 helper 和已知动效修复

**自检命令**:
- 运行本次测试目录里的 `compare-swiss-base.mjs`,确认输出里 `missing in template: 0`
- 目视对比原始 PPT 的同类页面:大标题字重、chrome-min 位置、timeline dot/label、卡片密度必须一致

### 0-F. 视觉 + 代码双核对:不要只看 HTML

**现象**:代码看起来类名正确,但实际页面拥挤、图文关系不对、可选组件堆太多,或者用了不适合内容的版式。

**做法**:
- 同时打开原始参考 PPT、当前模板或生成页、测试 PPT,先做视觉并排判断
- 等入场动效稳定后再截图或下判断,不要把动画中间态当成内容缺失
- 先打开网页逐页看视觉:标题字重、头部间距、正文密度、图片对齐、nav 安全区
- 再回代码看结构:该页是否用了正确版式,必选组件是否齐,可选组件是否过度
- 对照原始 PPT 时以实际画面为准;raw CSS helper 只能辅助,不能替代视觉判断
- 判断问题来源:版式选错 / 必选组件缺失 / 可选组件滥用 / 间距和安全区问题
- 通用版式(S03/S08/S11/S19)可多用;数据专用(S06/S07/S20/S21/S22)必须有真实数据或案例;结构专用(S14/S15/S17)必须有闭环、矩阵或层级关系
---

### 0. 生成前必须通过的类名校验(最重要)

**现象**：直接把 layouts.md 的骨架粘到新 HTML,结果样式全部丢失——大标题变成非衬线、数据大字报字体小得像正文、pipeline 多页糊成一坨、图片堆到浏览器底部。

**根因**：如果当前模板的 `<style>` 里没有这些类的定义,浏览器就 fallback 到默认样式。

**做法**：
- **生成 PPT 前,必须先 `Read` 当前风格对应模板**:风格 A 读 `assets/template.html`,风格 B 读 `assets/template-swiss.html`,确认 layouts 里用到的类都已定义
- 最常见遗漏的类:`h-hero / h-xl / h-sub / h-md / lead / meta-row / stat-card / stat-label / stat-nb / stat-unit / stat-note / pipeline-section / pipeline-label / pipeline / step / step-nb / step-title / step-desc / grid-2-7-5 / grid-2-6-6 / grid-2-8-4 / grid-3-3 / frame / img-cap / callout-src`
- 如果某个类确实缺了,**在模板的 `<style>` 里补上**,不要在每页 inline 重写
- 生成后打开浏览器,如果看到"大标题是非衬线"或"pipeline 步骤挤在一行",几乎 100% 是这个问题

### 1. 不要用 emoji 作图标

**现象**：在中式杂志风格里用 emoji（🎯 💡 ✅）会立刻破坏格调。

**做法**：用 Lucide 图标库，CDN 方式引用：

```html
<script src="https://cdn.jsdelivr.net/npm/lucide@0.344.0/dist/umd/lucide.min.js" integrity="sha384-tTkFttkBclaU1cloKwOi9xk3pbao3VZxTjLNBt8iFABWDBQibbAbWpVmO28zMuxq" crossorigin="anonymous"></script>
...
<i data-lucide="target" class="ico-md"></i>
...
<script>lucide.createIcons();</script>
```

常用图标名：`target / palette / search-check / compass / share-2 / crown / check-circle / x-circle / plus / arrow-right / grid-2x2 / network`

### 2. 图片只允许裁底部，左右和顶部绝对不能切

**现象**：用 `aspect-ratio` 撑图，网格会在父容器不足时堆叠或切掉图片关键信息（比如截图上部的标题栏）。

**做法**：图片容器用**固定 height + overflow hidden**，图片走 `object-fit:cover + object-position:top`：

```html
<figure class="frame-img" style="height:26vh">
  <img src="screenshot.png">
</figure>
```

CSS 里 `.frame-img img` 已经预设 `object-position:top`，只裁底。

**绝不用这种写法**（会在网格中撑破容器）：

```html
<!-- 坏例 -->
<figure class="frame-img" style="aspect-ratio: 16/9">...</figure>
```

**例外**：单张主视觉（非网格内）可以用 `aspect-ratio + max-height`，因为父容器会兜底。

### 2b. 亮页面配暗 WebGL = 灰蒙蒙(主题切换没生效)

**现象**:所有 light 页面背景都像蒙了一层灰,甚至 hero light 也灰。

**根因**:JS 根据 slide 的主题切换两张 canvas 的 opacity。如果整个 deck 开场是 hero dark,而没有任何机制能把 bg 切到 light,body 永远不加 `light-bg` 类,`canvas#bg-dark` 一直在上面。

**做法**:
- 模板里 `go()` 函数已改为从 `classList` 推断主题(`light` / `dark`),所以 **slide 必须明确带 `light` 或 `dark` 类**。不要漏写,更不要用其他自定义主题名
- hero 页用 `hero light` / `hero dark`,正文页用 `light` / `dark`。只写 `hero` 不带主题色是坏的
- 一个 deck 里必须至少有一个 **非 hero 的 light 页**,确保 body 有机会加 `light-bg`

### 2b-2. 全局色彩基调统一与防频闪规范（严禁逐页黑白乱跳）

**现象**: 一套演示文稿中一页白底、一页黑底黑白交替，放映时屏幕忽明忽暗，观众产生严重视觉眩光与疲劳感。

**根因**: 机械理解了"视觉节奏"，误把黑白底色交替当成节奏，破坏了整套 PPT 的色彩世界观与品牌统一性。

**做法**:
- **全套纯深色（Unified Dark Mode）** 或 **全套纯浅色（Unified Light Mode）** 二选一并贯穿全篇。
- 视觉节奏应该通过**版式拓扑（左右分栏 vs 3卡片网格 vs Pipeline 流水线 vs 大数据指标）与字阶层级**来创造，而不是靠底色黑白乱跳。
- **结构化例外**：仅允许封面/封底/章节过渡大幕页采用深色反差，正文内容页（90%+）必须保持绝对统一的底色基调。
- **自检**：检查所有幻灯片背景类名与 `data-bg`，确认全局底色高度统一。

### 2c. chrome 和 kicker 不要写同一句话

**现象**:左上角 `.chrome` 写"Design First · 设计先行",同一页里 `.kicker` 又写"Phase 01 · 设计阶段"——同义翻译,AI 味浓。

**做法**:
- **chrome = 杂志页眉 / 导航标签**:跨多页可相同(如 "Act II · Workflow"、"Data · Result"、"lukew.com · 2026.04")
- **kicker = 本页独一份的引导句**:短、有钩子、是大标题的"小前缀"(如 "BUT"、"一个人,做了什么。"、"The Question")
- 一个描述栏目,一个描述这一页——绝不互相翻译

### 3. 大标题字号不能超过屏宽 / 单字数

**现象**：中文大标题字号设太大（比如 13vw），结果每行只容 1 个字，强制换行非常难看。

**做法**：
- `h-hero`（最大）：10vw，**且标题长度 ≤ 5 字**
- `h-xl`（次大）：6vw-7vw
- 长标题用 `<br>` 手工断行，不要依赖自动换行
- 必要时加 `white-space:nowrap`

**示例**：`我不是程序员。`（6 字）用 `h-xl` 7.2vw + nowrap，一行排完。

### 4. 字体分工：标题衬线、正文非衬线

**做法**：
- 大标题、重点 quote、数字大字 → **衬线字体**（Noto Serif SC + Playfair Display + Source Serif）
- 正文、描述、pipeline 步骤名 → **非衬线字体**（Noto Sans SC + Inter）
- 元数据、代码、标签 → **等宽字体**（IBM Plex Mono + JetBrains Mono）

所有字体用 Google Fonts CDN 引入，模板里已预设。

### 4b. 图片不要用 `align-self:end` 贴底

**现象**：左文右图布局里,为了让右列图片和左列 callout 底部对齐,在 `<figure>` 上加 `align-self:end`。结果:
- 如果父容器不是 grid(比如类名没定义),`align-self` 完全失效,图片掉到文档流最下面被浏览器底栏遮挡
- 即使是 grid,图片会在 cell 里贴底,低分屏上仍然被 `.foot` 和 `#nav` 圆点遮挡

**做法**:
- 图文混排**必须用 `.frame.grid-2-7-5`**(或 `.grid-2-6-6`/`.grid-2-8-4`)
- 右列 `<figure class="frame-img r-16x10">` 或 `<figure class="frame-img r-4x3">` 自然贴顶即可
- 要让左列 callout 看起来"贴底",给**左列**加 flex column + `justify-content:space-between`,不要动右列
- 如果图片与大标题顶端齐平但正文从标题下方开始,给图片加 `margin-top:7vh` 到 `9vh`,让图片跟正文内容区对齐

### 4c. 图片不要用原图奇葩比例

**现象**:`aspect-ratio: 2592/1798` 这种从原图复制的比例,在不同屏幕下撑出奇怪的空白或溢出。

**做法**:无论原图什么比例,占位器固定用标准比例 **16/10 / 4/3 / 3/2 / 1/1 / 16/9**。图片自动 `object-fit:cover + object-position:top`,顶部不裁,底部裁掉一点无伤大雅。

### 5. 不要给图片加厚边框 / 阴影

**现象**：为了"高级感"加了强阴影或黑框，瞬间变成商务 PPT。

**做法**：最多 1-4px 的微圆角 + **极淡的底噪**（已在模板里）。不要加 `box-shadow`，不要加 `border`（除非 1px 极淡的灰）。

---

## 🟡 P1 · 排版节奏

### 6. Hero 页和非 hero 页要交替

**推荐节奏**（25-30 页）：
```
Hero Cover → Act Divider (hero) → 3-4 pages non-hero → Act Divider (hero)
→ 4-5 pages non-hero → Hero Question → ... → Hero Close
```

连续 2 页以上 hero 会让人疲劳，连续 4 页以上 non-hero 会让节奏死。

### 7. 大字报页和密集页要交替

大字报（big numbers / hero question）和密集页（pipeline / image grid）交替出现，听众眼睛才不累。

### 8. 同一概念的英文/中文用法要统一

**现象**：一会儿写 "Skills"，一会儿写 "技能"，一会儿写 "薄承载厚技能"，全篇不一致。

**做法**：
- 术语优先用**英文单词**（Skills / Harness / Pipeline / Workflow），这些都是圈内熟悉词
- **别硬翻译**，硬翻译反而生硬
- 整个 deck 里同一个词 1 个写法

### 9. 底部 chrome 的页码要一致

用 `XX / 总页数` 的格式（比如 `05 / 27`）。**不要在右上角加动态页码**（会和 `.chrome` 重复）。

### 9b. 动效系统:每一页都要有 data-anim 标记

**现象**:生成后打开浏览器,翻页时内容直接"啪"地出来,没有任何节奏感——杂志风完全靠排版硬撑,少了层级展开的仪式感。

**根因**:完全没给任何元素加 `data-anim`,Motion One 脚本找不到可播的元素,整页静态出现。

**做法**:
- 所有正文页,**至少给 kicker / 主标题 / lead / callout / stat-card / figure 这些叶子元素加 `data-anim`**
- **Hero 页**(开场/幕封/问题/结尾):所有核心块(kicker + 大标题 + lead + meta-row)都要加
- **不需要特殊 recipe 的页**:什么也不用写,默认 cascade 就好看
- **需要特殊 recipe 的 4 类页**:必须在 `<section>` 上加对应 `data-animate`
  - 大引用 → `data-animate="quote"` + 每行 `<span data-anim="line" style="display:block">`
  - Before/After 对比 → `data-animate="directional"` + 左列 `data-anim="left"` + 右列 `data-anim="right"`
  - Pipeline 流水线 → `data-animate="pipeline"` + 每 step 加 `data-anim="step"`
  - Hero 页(自动用 hero recipe,但仍需给元素加 `data-anim`)

**自检**:生成后 `grep -c 'data-anim' index.html`,应该数十条以上。如果只有个位数,一定漏标了。

### 9c. Pipeline 页必须加 data-animate="pipeline"

**现象**:流水线页直接全部淡入,失去"一步步讲"的节奏,但切到下一页时又只能往前翻,没法回到上一个 step。

**做法**:Layout 6 的 `<section>` 必须加 `data-animate="pipeline"`。演示时按 →/空格/滚轮下滑可以**逐个点亮 step**,全部点亮之后再按 → 才会翻到下一页。这个节奏是刻意的,不是 bug。

---

## 🟢 P2 · 视觉打磨

### 10. WebGL 背景的遮罩透明度

**dark hero**：遮罩 12-15%（WebGL 明显透出）
**light hero**：遮罩 16-20%（WebGL 隐约可见，不抢字）
**普通 light/dark 页**：遮罩 92-95%（几乎不透）

如果页面文字非常少（hero question），遮罩可以再薄些；如果正文密集，必须加厚遮罩确保可读。

### 11. Light hero 的 shader 不能有强中心点

**现象**：Spiral Vortex、径向涟漪在 light 主题下太显眼，像 Windows 98 屏保。

**做法**：light hero 用 FBM 域扭曲驱动的无中心流动，底色保持银/纸色（接近 #F0F0F0 / #FBF8F3），彩虹偏色 subtle（0.05 以下）。

### 12. Dark hero 允许更多视觉冲击

Dark hero 可以用 Holographic Dispersion（钛金色散）等带中心结构的 shader，因为黑底能容纳更多视觉信息。

### 13. 左文右图的对齐

- 左列的文字组 `justify-content:space-between`：标题贴顶，引用框贴底
- 右列图片保持自然顶对齐,不要加 `align-self:end`
- 右列图片通常要跟正文内容区对齐,不是跟大标题顶端对齐;必要时加 `margin-top:7vh` 到 `9vh`
- 网格整体 `align-items:start`（不是 `center` / `end`）

### 13b. 标题与正文间距

- 顶部标题 + 下方长文章/引用/图表的两段式布局,中间必须有明显间距,推荐 `margin-top:6vh` 到 `8vh`
- 居中大标题页必须整体水平居中,不要只让文字块左对齐居中摆放
- 复杂内容页用大标题定调,下方内容用 grid / rowline 两端对齐,不要把大标题、小标题、正文挤成一坨

### 13c. UI 情景图不要拉成巨长条

- 单张 UI 截图如果放满宽后变成长条,优先拆成 2-3 个局部面板
- 多面板拼排时每个 `.frame-img` 用同一个固定高度类,如 `.h-16` / `.h-18` / `.h-22`,不要用同一个超宽容器硬塞
- 同一组图片的视觉大小必须一致,不要混用不同高度、不同缩放和不同边距密度
- 如果确实需要全宽,必须生成比例足够长的横向图片,并在 prompt 里明确"ultra-wide horizontal strip"

### 13d. 生成配图不要自带 slide 元素

- GPT-M 2.0 生成的配图只是嵌入素材,不要让图片自带页眉、页脚、标题、页码、角标、署名或装饰边框
- 流程图/信息图只保留核心图形和必要短标签,PPT 自己负责标题、页脚和 chrome
- 如果生成图已经带了这些元素,优先重生成;不要在 PPT 里再叠一层 chrome 造成干扰

### 13e. Swiss 图文混排不能只用一种

- 7-8 页 Swiss 测试 deck 至少使用 6 个不同 S 编号版式
- 有 2-3 张配图时,至少使用两种图片承载方式:S22 主视觉 / S15 矩阵 / S16 小报 / S08 对照图文 / S19 四卡证据
- 左文右图或右文左图需要底对齐时,先控制图片高度和主体安全区,不要把整块内容推到分页组件附近
- 白底信息图容器必须白底、无描边;不要用灰框包白图

### 13f. Swiss 中文大标题要降级

- 中文 2 行标题默认从 `min(5.8vw,10.2vh)` 起步,不要直接用英文页的 `6.8vw-7vw`
- 任一行 9-12 个中文字符时降到 `min(5.2vw,9.2vh)`
- 3 行标题优先改写,不能为了标题大而挤掉下方图文内容

### 14. 图片的微弱圆角

风格 A 可以有轻微圆角。风格 B Swiss 必须直角: `.frame-img` 和图片本身都不要圆角、阴影或消费 app 式卡片感。
---

## 🔵 P3 · 操作细节

### 15. 图片路径用相对路径

图片放在 `images/` 文件夹下，HTML 里用相对路径 `images/xxx.png`，不要用绝对路径。

### 16. 页码在 `.chrome` 里写死

JS 会动态算总页数并扩展底部翻页圆点，但 `.chrome` 里的 `XX / N` 是写死的。加页/删页时要手工改 N。

### 17. 翻页导航要保留

模板默认支持：← → / 滚轮 / 触屏滑动 / 底部圆点 / Home·End。不要删 JS 里的导航逻辑。

### 18. 不要用 `height:100vh` 硬设，用 `min-height:80vh`

`100vh` 会让内容刚好卡满屏幕，但浏览器工具栏、标签栏会吃掉一部分高度，导致内容溢出。用 `min-height:80vh + align-content:center` 更稳。

---

## 🧪 最终自检清单

生成完 PPT 后，逐项对照这个清单（勾一下）：

```
预检(生成前)
  □ 全局色彩基调已统一: 全套保持纯深色(Dark)或纯浅色(Light),无逐页黑白交替闪烁
  □ `<title>` 已改为实际 deck 标题(grep "[必填]" 应无结果)
  □ 瑞士风:封面是 `slide accent` 满屏 IKB + `<canvas class="ascii-bg">`(不是 `slide light` 白底)
  □ 瑞士风:封底是 `slide split` + 左 `b-accent` + ASCII canvas / 右 paper 3 条 takeaway,第 03 条用 var(--accent)
  □ 瑞士风:`grep -c "ascii-bg" index.html` ≥ 2(封面 + 封底各一)
  □ 瑞士风:封面没有"01"等大编号(chrome 已显示 01/N,不要重复)
  □ 瑞士风:IKB 背景上的强调字用 `font-style:italic`,禁止用 `color:var(--accent)`(蓝压蓝)

内容
  □ 每一幕的页数比例合理(不会头重脚轻)
  □ 没有使用 emoji 作图标
  □ Skills / Harness 等术语用法统一
  □ 每页的 kicker + 标题 + 正文 三级信息清晰

排版
  □ 所有大标题没有出现 1 字 1 行的换行
  □ 图片网格用 height:Nvh 而非 aspect-ratio
  □ 图片只裁底部，顶部和左右完整
  □ 衬线/非衬线字体分工符合模板
  □ Pipeline 多组之间有明显分隔

视觉
  □ hero 页和 non-hero 页交替
  □ WebGL 背景在 hero 页可见
  □ 图片有微弱圆角
  □ 没有沉重的阴影和边框

交互
  □ ← → 翻页正常
  □ 底部圆点数量与总页数匹配
  □ chrome 里的页码和实际页号一致
  □ ESC 键触发索引视图（如果保留）
  □ B 键触发静态/低功耗模式,右下角提示在 `B 静态` / `B 动态` 之间切换

动效
  □ 如使用 Motion 动效，`assets/motion.min.js` 已随演示文稿审核发布；缺失时所有动画元素仍保持可见
  □ 低功耗模式下 WebGL/ASCII canvas 不再挂 RAF 循环,当前页内容仍全部可见
  □ 翻页时内容逐个淡入,不是"啪"一下全出
  □ 大引用页 `<section>` 带 `data-animate="quote"`,每行 `<span data-anim="line">`
  □ Before/After 对比页 `<section>` 带 `data-animate="directional"`,左右列标 left/right
  □ Pipeline 页 `<section>` 带 `data-animate="pipeline"`,每 step 标 data-anim="step"
  □ `grep -c 'data-anim' index.html` 数量 ≥ 页数 × 3(平均每页 3 个以上标记)
```

全勾完，才是合格的 PPT。
