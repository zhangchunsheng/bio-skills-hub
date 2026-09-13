# 页面布局库（Layouts）

本文档收录 10 种最常用的页面布局骨架。每种都是一个完整可粘贴的 `<section class="slide ...">...</section>` 代码块，直接替换文案/图片即可使用。

---

## ⚠️ 生成前必读（Pre-flight）

### A. 类名必须来自 template.html

layouts.md 使用的所有类（`h-hero` / `h-xl` / `h-sub` / `h-md` / `lead` / `meta-row` / `stat-card` / `stat-label` / `stat-nb` / `stat-unit` / `stat-note` / `pipeline-section` / `pipeline-label` / `pipeline` / `step` / `step-nb` / `step-title` / `step-desc` / `grid-2-7-5` / `grid-2-6-6` / `grid-2-8-4` / `grid-3-3` / `grid-6` / `grid-3` / `grid-4` / `frame` / `frame-img` / `img-cap` / `callout` / `callout-src` / `kicker`）都在 `assets/template.html` 的 `<style>` 块里预定义。

**不要发明新类名**。如果必须自定义，用 `style="..."` inline 写。生成前若不确定某个类是否存在，grep template.html 确认。

### B. 图片比例规范（非常重要）

**永远用标准比例**，不要用原图 `aspect-ratio: 2592/1798` 这种奇葩比例：

| 场景 | 推荐比例 | 写法(范式 + 比例) |
|------|---------|------|
| 左文右图 主图 | 16:10 或 4:3 | `.t-float.r-16x10` 或 `.t-float.r-4x3`(T2 Float 默认) |
| 图片网格（多图对比） | 统一 | `.t-quiet` + `style="height:22vh\|26vh"`,同组必须同高(T6) |
| 小型面板组 | 统一 | `.t-quiet` + `style="height:16vh\|18vh"`,同组必须同高(T6) |
| 左小图 + 右文字 | 1:1 或 3:2 | `.t-float.r-1x1` 或 `.t-float.r-3x2`(T2) |
| 全屏主视觉 | 16:9 | `.t-bleed`(T1) 或 `.t-float.r-16x9`(T2) |
| 信息图 / 截图再设计 | 16:9 或 16:10 | `.t-inset.r-16x9` 或 `.t-inset.r-16x10`(T3,默认截图处理) |
| 图文混排小插图 | 3:2 或 3:4 | `.t-float.r-3x2` 或 `.t-float.r-3x4`(T2) |

图片必须包在 `<figure class="t-XXX">` 里(按 [`image-treatments.md`](image-treatments.md) 选范式),并写 `data-treatment="t-XXX"` 自检。比例类(`.r-*` / `.h-*`)全局通用,不再限定在 `.frame-img` 上。默认照片会 `object-fit:cover + object-position:top center`,只裁底部,不裁顶/左/右。信息图和截图再设计必须加 `.fit-contain`,避免文字或标注被裁切。

**禁用**: 旧版 `figure.frame-img` + `figcaption.img-cap` 写"产品截图/原始截图" 的组合已废止,本文件下面的所有 layout 示例都已改用 T2 / T6 范式。如果生成时仍写出这种组合,说明 LLM 回退到旧范式,需要手动改写。

### B2. 图片与内容的垂直对齐

图片应该跟正文内容区对齐,不要默认贴到大标题顶端。特别是左文右图和图文混排页:

- 如果左列是 kicker + 大标题 + 正文 + callout,右列图片通常从正文高度开始,可给图片加 `style="margin-top:7vh"` 到 `9vh`
- 如果图片是信息图或 UI 情景图,优先对齐正文首行或说明文字,不要和超大标题顶端齐平
- 如果一张截图/UI 情景图在横向页面里变成很长的条,不要硬拉满宽;改成极宽横图素材,或拆成 2-3 个局部面板拼排
- 多图面板必须使用同一个高度类,不要混用 `h-16` / `h-22` 或手写不同 `height`

### B3. 双轨间距规范（首页舒展大气 ↔ 正文紧凑空间让渡）

- **🟢 仅首页 PPT / 封面页 (Cover Slide / Hero Cover)**：
  - 豁免紧凑压缩，采用开阔舒展的纵向呼吸排版，赋予主标题与副标题/金句引导语极强的大格局留白。
  - **Badge 与主标题间距**：`16px ~ 28px`（如 `DESIGN CANVAS` 与大标题）
  - **主标题与副标题/金句间距**：`20px ~ 32px`（如 `写 Skill 前先回答四个问题` 与金句引导语）
  - **副标题与下方元素间距**：`36px ~ 56px`（与 Stats/Divider/作者信息/芯片桥接行）
- **🔵 正文内容页 (Content Slides)**：
  - **页眉三要素组合**（分类 Badge、主标题 h1/h2、副标题/说明 lead/tagline）必须保持紧凑扁平，**总高度严格控制在 <= 200px（约占 1080p 画布的 18%~22%）**，杜绝层层堆叠 20~30px 大外边距，为下方主内容（卡片、图表、流程等）留出 78%+ 黄金纵向空间。
  - **具体间距标准**：
    - Badge 与主标题间距：`6px ~ 8px`
    - 主标题与副标题间距：`8px ~ 12px`
    - 副标题与下方主内容区间距：`16px ~ 24px`
  - **推荐排版方案**：
    - 使用 `.header-compact` 垂直紧凑编排
    - 使用 `.header-split` 左右水平分栏（左标题 + 右副标题，将 3 行压缩为 1 行）
    - 使用行内徽标前缀（如 `<h2><span class="eyebrow-pill">TAG</span> 主标题</h2>`）
- 居中大标题页必须让主标题在页面水平居中,使用 `.center` 或 `text-align:center; margin-inline:auto`

### B4. 主要内容大字号高可读性规范 (High-Legibility Large Font Standard · NON-NEGOTIABLE)

- **字号阶梯规范**：在 1920×1080 舞台下，所有文字必须遵循大字号标准，杜绝 12px~14px 密密麻麻的文档感：
  - **分类徽章/Pill** (`.eyebrow-pill` / `.kicker`): `16px ~ 18px` (`font-weight: 800`)
  - **主标题** (`.slide-title` / `.h-xl`): `48px ~ 54px` (`font-weight: 800/900`)
  - **副标题/金句引导语** (`.slide-subtitle` / `.lead`): `22px ~ 26px` (`font-weight: 600`)
  - **卡片/分栏标题** (`.b-card h3` / `.card-title`): `26px ~ 28px` (`font-weight: 800`)
  - **卡片正文/主要段落** (`.b-card p` / `.card-text` / `p`): `20px ~ 22px` (`line-height: 1.62`)
  - **列表项/Bullet Items** (`.b-card li` / `.feature-desc`): `19px ~ 21px` (`line-height: 1.6`)
  - **数据大数字** (`.stat-nb`): `56px ~ 72px`，**数据标签** (`.stat-label`): `16px ~ 18px` (`font-weight: 700`)
  - **流水线/Pipeline** (`.step-nb: 19px~20px`, `h3: 24px`, `p: 19px`)
  - **表格** (`.data-table`): `th: 21px (w:800)` / `td: 20px (line-height: 1.5)`
  - **代码块** (`.code-block`): `19px ~ 21px` (`line-height: 1.65`)
  - **底栏控制按钮** (`.ctrl-btn` / `.slide-counter`): `16px` (`font-weight: 700/800`)

### B5. 图片/图标/序号徽章与文字单行同行并排规范 (Inline Icon, Badge & Title Standard · NON-NEGOTIABLE)

- **排版原则**：在卡片（`.card` / `.b-card`）、步骤（`.step` / `.pipeline-step`）、架构层级（`.stack-row`）中，**图片、图标、Emoji 或序号徽章必须与对应的标题文字处于同一行展示**（使用 `.card-header` / `.step-header` 配合 `display: flex; align-items: center; gap: 10px~14px;` 或直接在 `<h3>` 内包含 `<span class="badge">`），严禁上下拆成两行展示。
- **豁免条件**：除非在极端窄栏或超长文字确实无法单排放下时，才可酌情折行两行展示。

### C. 图片定位准则（避免图片堆到页面最底部、被浏览器工具栏遮挡）

**错误做法**（已踩坑，不要再犯）：
- 在非 grid 容器里用 `align-self:end`：`align-self` 在 flex/grid 之外完全无效，图片会掉到文档流末尾堆底
- 用 `position:absolute + bottom:0` 把图"固定"到底：会被底部 `.foot` 和 `#nav` 圆点遮挡
- 单张图片只写 `height:N vh` 不限 `max-height`：在低分屏会撑出视口

**正确做法**：
- 图文混排**必须用 `.frame.grid-2-7-5`**（或 `.grid-2-6-6` / `.grid-2-8-4`）的 grid 结构
- grid 容器默认 `align-items:start`（已在 template 中设置），图片自然贴到 cell 顶端
- 如果需要"图片底对齐左列 callout"：**左列用 flex column + `justify-content:space-between`**（让 callout 自己贴左列底），**右列 figure 直接保持 align-items:start 即可**，不要加 `align-self:end`
- 所有 grid 父容器建议加 inline `style="padding-top:6vh"`，给标题区留呼吸空间

### D. 主题色与主题节奏

- 主题色与视觉 Spec 从对应模板的 `design.md` 或 `STYLE_PRESETS.md` 提取，遵循设计系统 Token 规范
- 主题节奏(每页用 light / dark / hero light / hero dark 哪一个)在下文"主题节奏规划"一节有硬规则,生成前必读
- 两件事都要在挑布局之前决定,避免返工

### E. 动效系统(默认开启 · Motion One 驱动)

**核心机制**:template.html 底部的 module script 会在翻页时触发入场动画。所有带 `data-anim` 的元素初始不可见,翻到当前页时由 Motion One 逐个淡入。

**动效策略**:在 `<section>` 上加 `data-animate="<recipe>"` 选择动画风格;每个需要入场动画的元素加 `data-anim`(可选附值,如 `left` / `right` / `line` / `step`)。

| recipe | 用法 | 适合布局 |
|---|---|---|
| 默认(cascade) | 什么也不加,自动级联淡入 | 大部分正文页(Layout 3 / 4 / 5 / 10) |
| `hero` | `.hero` 页自动启用,节奏更慢更仪式感 | Layout 1 / 2 / 7(所有 hero 页) |
| `quote` | 一句一句揭示,慢节奏(550ms stagger) | Layout 8 大引用 |
| `directional` | 左进 → 分割 → 右进,用于对比 | Layout 9 Before/After |
| `pipeline` | 手动推进,按 →/空格 一步步点亮 | Layout 6 流水线 |

**降级保底**:如果随演示文稿审核发布的本地 `motion.min.js` 不可用,脚本会强制把所有 `data-anim` 元素设为 `opacity:1`,内容永远可读；不会再从 CDN 动态导入可执行模块。

**不需要动效的页面**:如果某页想完全跳过动效,不加任何 `data-anim` 即可 —— Motion One 只对带标记的元素生效。

---

## 0. 基础结构（所有 slide 都一样）

```html
<section class="slide [light|dark|hero light|hero dark]">
  <div class="chrome">
    <div>上下文标签 · 子标签</div>
    <div>ACT · 页号 / 总页数</div>
  </div>
  <!-- 主内容 -->
  <div class="foot">
    <div>页码说明 · Page Description</div>
    <div>— · —</div>
  </div>
</section>
```

- 非 hero 页建议加 `light` 或 `dark` 主题；hero 页加 `hero light` 或 `hero dark`（参与 WebGL 主题插值）
- `chrome` 和 `foot` 是可选但推荐保留的上下左右四角元数据
- **hero 页用于章节封面/开场/收束/转场**，非 hero 页用于正文

### ⚠️ chrome 和 kicker 不要写同一句话

这是最常见的内容重复问题。两者在语义上完全不同的维度：

| 位置 | 角色 | 内容性质 | 例子 |
|------|------|---------|------|
| `.chrome` 左上 | **杂志页眉 / 导航元数据** | 稳定的"栏目名"或"章节分类"，跨多页可以相同 | "Act II · Workflow" / "Data · Result" / "lukew.com · 2026.04" |
| `.chrome` 右上 | **页号 + 幕号** | 固定格式 | "Act II · 15 / 25" |
| `.kicker` | **这一页独一份的引导句** | 是大标题的"小前缀"，像杂志大标题上方的一行话，每页都应不同 | "BUT" / "一个人,做了什么。" / "Phase 01 · 设计阶段" |

**反例**（已踩坑）：chrome 写"设计先行 · Design First"，kicker 又写"Phase 01 · 设计阶段"——意思重复，读者一眼就觉得 AI 生成的。

**正确做法**：chrome 是**栏目标签**（稳定、跨页可复用），kicker 是**本页钩子**（短句、有戏剧性），两者互为补充，不互相翻译。

### ⚠️ 全局色彩基调规划（必读 · 防频闪规范)

**核心机制**: 每页 `<section class="slide">` 必须带 `light` 或 `dark` 主题类名，并设置 `data-bg` 属性。JS 依据此类名自动同步外部视口底色 (`updateViewportBg()`)。

#### 色彩统一硬规则

- ✅ **推荐范式 A（纯粹统一基调 · 默认推荐）**：整套 PPT 100% 保持全套纯深色（`Unified Dark`）或全套纯浅色（`Unified Light`），全篇视觉世界观高度一致，彻底消除页面切换时的黑白频闪与视觉眩光。
- ✅ **推荐范式 B（结构化章节对比）**：仅在封面页、封底或大型章节大幕过渡页采用深色聚焦，正文内容页（90%+）统一采用浅色，绝不逐页频繁跳跃。
- ❌ **严禁逐页黑白交替**：严禁在相邻正文页之间一页深一页浅交替，这会导致观众眼睛在强弱光线间反复适应，产生强烈视觉疲劳。
- 节奏感应来自**排版拓扑（如分栏、网格、流水线、数据大字报）与内容编排**，而非底色乱跳。

#### 8 页节奏模板(可直接套用)

| 页 | 主题 | 布局 | 备注 |
|---|---|---|---|
| 1 | `hero dark` | 封面 | 开场 |
| 2 | `light` | 大字报 | 数据抛出 |
| 3 | `dark` | 左文右图 | 对比/故事 |
| 4 | `light` | Pipeline | 流程 |
| 5 | `hero light` | 章节幕封 | 呼吸 |
| 6 | `dark` | 左文右图 or 大引用 | |
| 7 | `hero dark` | 问题页 | 悬念收束 |
| 8 | `light` | 大引用/结尾 | 收尾 |

**先画这张表对齐,再动手写 slide**。跳过规划直接粘骨架 = 全是 light。

---

## Layout 1: 开场封面（Hero Cover）

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>A Talk · 2026.04.22</div>
    <div>Vol.01</div>
  </div>
  <div class="frame" style="display:grid; gap:4vh; align-content:center; min-height:80vh">
    <div class="kicker" data-anim>私享会 · 李继刚</div>
    <h1 class="h-hero" data-anim>一人公司</h1>
    <h2 class="h-sub" data-anim>被 AI 折叠的组织</h2>
    <p class="lead" style="max-width:60vw" data-anim>
      一个 AI 创作者 —— 在 64 天里做了 11 万行代码、在 9 个平台上持续输出，生活节奏几乎没有被改变。
    </p>
    <div class="meta-row" data-anim>
      <span>歸藏 Guizang</span><span>·</span><span>独立创作者 / CodePilot 作者</span>
    </div>
  </div>
  <div class="foot">
    <div>一场关于 AI · 组织 · 个体的分享</div>
    <div>— 2026 —</div>
  </div>
</section>
```

**要点**：
- 用 `hero dark` 让 WebGL 背景在大部分区域透出
- `h-hero` 是最大字号（10vw），这里作标题主视觉
- 采用开阔纵向呼吸间距（Badge-to-Title `16px ~ 28px`，Title-to-Subtitle `20px ~ 32px`，Subtitle-to-Bottom `36px ~ 56px`），严禁按正文页 `6~8px` 紧凑挤压
- 用 `min-height:80vh + align-content:center` 让内容整体垂直居中
- 不需要 `.chrome` 里写页码，封面页自成一体

---

## Layout 2: 章节幕封（Act Divider）

```html
<section class="slide hero light">
  <div class="chrome">
    <div>第一幕 · 硬数据</div>
    <div>Act I · 01 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:6vh; align-content:center; min-height:80vh">
    <div class="kicker" data-anim>Act I</div>
    <h1 class="h-hero" style="font-size:8.5vw" data-anim>硬数据</h1>
    <p class="lead" style="max-width:55vw" data-anim>
      先看数字，再谈方法。
    </p>
  </div>
  <div class="foot">
    <div>第一幕引子</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：
- 极简，只需要 kicker + 大标题 + 一行引语
- 两个幕的封面可以交替 `hero light` / `hero dark`，制造节奏
- `h-hero` 字号可以从 10vw 调到 8.5vw 适配长短

---

## Layout 3: 数据大字报（Big Numbers Grid）

```html
<section class="slide light">
  <div class="chrome">
    <div>过去 64 天 · 开发篇</div>
    <div>Act I / Dev · 02 / 25</div>
  </div>
  <div class="frame" style="padding-top:3vh">
    <div class="kicker" data-anim>一个人，做了什么。</div>
    <h2 class="h-xl" data-anim>过去 64 天</h2>
    <p class="lead" style="margin-bottom:2vh" data-anim>从 0 到开源 CodePilot。</p>

    <div class="grid-6" style="margin-top:2vh">
      <div class="stat-card" data-anim>
        <div class="stat-label">Duration</div>
        <div class="stat-nb">64 <span class="stat-unit">天</span></div>
        <div class="stat-note">从 0 到现在</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">Lines of Code</div>
        <div class="stat-nb">110K+</div>
        <div class="stat-note">一行行写到 11 万+</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">GitHub Stars</div>
        <div class="stat-nb">5,166</div>
        <div class="stat-note">一个开源仓库</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">Downloads</div>
        <div class="stat-nb">41K+</div>
        <div class="stat-note">装到了几万台电脑里</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">AI Providers</div>
        <div class="stat-nb">19</div>
        <div class="stat-note">跨平台接入</div>
      </div>
      <div class="stat-card" data-anim>
        <div class="stat-label">Commits</div>
        <div class="stat-nb">608+</div>
        <div class="stat-note">没有协作者</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>项目 · CodePilot　|　github.com/codepilot</div>
    <div>Act I · Dev Numbers</div>
  </div>
</section>
```

**要点**：
- 3×2 或 4×2 网格最稳（见 `.grid-6`）
- 每个 `stat-card` 结构固定：label（英文小字）→ nb（大字数字）→ note（注释）
- 数字建议 2-3 位字符（太长会溢出），用 K / M 简写
- **间距不要再加大**：骨架默认 `padding-top:3vh` + lead `margin-bottom:2vh` + grid `margin-top:2vh` 是 3×2 网格在 16:9 屏不压 foot 的实测上限;内容更多时先删卡片,不要压缩 foot 空间

---

## Layout 4: 左文右图（Quote + Image）

```html
<section class="slide light">
  <div class="chrome">
    <div>身份反差 · The Twist</div>
    <div>03 / 25</div>
  </div>
  <div class="frame grid-2-7-5" style="padding-top:6vh">
    <!-- 左列：标题 + 正文 + callout，flex column 让 callout 贴列底 -->
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:3vh">
      <div>
        <div class="kicker" data-anim>BUT</div>
        <h2 class="h-xl" style="white-space:nowrap; font-size:7.2vw" data-anim>
          我不是程序员。
        </h2>
        <p class="lead" style="margin-top:3vh" data-anim>
          大学毕业之后再也没写过一行代码。过去十年做的是 UI 设计和 AI 特效。
        </p>
      </div>
      <div class="callout" data-anim>
        "这东西在三年前，<br>
        需要一个十人团队做一年。"
        <div class="callout-src">— 一个观察者的判断</div>
      </div>
    </div>
    <!-- 右列：T2 Float 自由留白（默认范式,无圆角无阴影,无产品截图图注） -->
    <figure class="t-float r-16x10" data-treatment="t-float" data-anim>
      <img src="images/codepilot.png" alt="CodePilot 主界面">
    </figure>
  </div>
  <div class="foot">
    <div>Page 03 · 我不是程序员</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：
- 用 `grid-2-7-5`（左 7 份、右 5 份），`align-items:start` 已在 template 预设
- **左列**用 flex column + `justify-content:space-between`：标题贴顶，callout 自然贴底
- **右列图片** **不要加 `align-self:end`**。会让图片滑到 cell 底部，低分屏下被浏览器工具栏遮挡
- 图片必须用 **标准比例类 `.r-16x10` 或 `.r-4x3`**，不要用原图奇葩比例（`2592/1798` 这种）

---

## Layout 5: 图片网格（多图对比）

```html
<section class="slide light">
  <div class="chrome">
    <div>平台粉丝实证</div>
    <div>Act I / Ops · 05 / 27</div>
  </div>
  <div class="frame" style="padding-top:3vh">
    <div class="kicker" data-anim>Proof · 粉丝实证</div>
    <h2 class="h-xl" data-anim>10 个平台 · 6 张截图</h2>

    <!-- T6 Quiet Frame 多图分组,单图无 figcaption,组标题在顶部 .h-xl -->
    <div class="t-quiet-grid" data-treatment="t-quiet" style="margin-top:3vh">
      <figure class="t-quiet" style="height:26vh" data-anim><img src="images/weibo.png" alt="微博"></figure>
      <figure class="t-quiet" style="height:26vh" data-anim><img src="images/twitter.png" alt="推特"></figure>
      <figure class="t-quiet" style="height:26vh" data-anim><img src="images/wechat.png" alt="公众号"></figure>
      <figure class="t-quiet" style="height:26vh" data-anim><img src="images/jike.png" alt="即刻"></figure>
      <figure class="t-quiet" style="height:26vh" data-anim><img src="images/xhs.png" alt="小红书"></figure>
      <figure class="t-quiet" style="height:26vh" data-anim><img src="images/douyin.png" alt="抖音"></figure>
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>Page 05 · 粉丝实证</div>
  </div>
</section>
```

**要点**：
- **范式：T6 Quiet Frame**（多图分组,单图无 figcaption,组标题在顶部 `.h-xl`）
- 关键：每个 `.t-quiet` 必须写死 `height:NNvh`（不要用 `aspect-ratio`），否则网格会撑破
- 图片会自动 `object-fit:cover + object-position:top`，只裁底部
- 容器用 `.t-quiet-grid`（auto-fit minmax 220px 1fr, gap 14px），不要用 `.grid-3-3`（旧 grid 不带 T6 的极轻发丝线）
- 3×2 双行时,`height:26vh` 是不压 foot 的上限;标题更长或加说明行时降到 `22vh`
- **不要**给单图加 `figcap` 写"微博 · 289K" —— 这种标签属于旧 `frame-img` + `.img-cap` 范式,新规则是组标题在 slide 顶部,单图本身保持干净
- 完整规范见 [`image-treatments.md`](image-treatments.md) T6 段

---

## Layout 6: 两列流水线（Pipeline）

```html
<section class="slide light" data-animate="pipeline">
  <div class="chrome">
    <div>我的工作流 · Workflow</div>
    <div>Act II · 15 / 27</div>
  </div>
  <div class="frame">
    <div class="kicker">Pipeline · 流水线</div>
    <h2 class="h-xl">两条流水线</h2>

    <!-- 第一组：文本侧 -->
    <div class="pipeline-section">
      <div class="pipeline-label">文本侧 · Text Pipeline</div>
      <div class="pipeline">
        <div class="step" data-anim="step">
          <div class="step-header"><span class="step-nb">01</span><div class="step-title">Draft</div></div>
          <div class="step-desc">AI 帮我起草初稿</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-header"><span class="step-nb">02</span><div class="step-title">Polish</div></div>
          <div class="step-desc">AI 润色去 AI 味</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-header"><span class="step-nb">03</span><div class="step-title">Morph</div></div>
          <div class="step-desc">AI 变形成推特 / 小红书</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-header"><span class="step-nb">04</span><div class="step-title">Illustrate</div></div>
          <div class="step-desc">AI 生成信息图</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-header"><span class="step-nb">05</span><div class="step-title">Distribute</div></div>
          <div class="step-desc">一键分发 9 平台</div>
        </div>
      </div>
    </div>

    <!-- 第二组：视频侧 -->
    <div class="pipeline-section">
      <div class="pipeline-label">视觉 · 视频侧 · Video Pipeline</div>
      <div class="pipeline">
        <div class="step" data-anim="step">
          <div class="step-header"><span class="step-nb">06</span><div class="step-title">Cut</div></div>
          <div class="step-desc">AI 帮我剪辑</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-header"><span class="step-nb">07</span><div class="step-title">Wrap</div></div>
          <div class="step-desc">AI 帮我包装</div>
        </div>
        <div class="step" data-anim="step">
          <div class="step-header"><span class="step-nb">08</span><div class="step-title">Cover</div></div>
          <div class="step-desc">AI 生成封面</div>
        </div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 15 · 我的内容工厂</div>
    <div>Workflow</div>
  </div>
</section>
```

**要点**：
- 用 `.pipeline-section` 分组 + `.pipeline-label` 作组标题
- 两组之间用 3.6vh 的间距 + 顶部细分隔线（已在 CSS 中预设）
- 每个 step 是固定的 nb → title → desc 结构
- 步骤数不限但单行最好 ≤5 个，否则换到第二 pipeline
- **动效**:`<section>` 加 `data-animate="pipeline"`,每个 `.step` 加 `data-anim="step"`。翻到此页时步骤默认 `opacity:.15`,按 →/空格/滚轮下滑时一次点亮一个 step;**所有 step 点亮完才会翻到下一页**,可制造演讲互动感

---

## Layout 7: 悬念收束 / 问题页（Hero Question）

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>留给你的问题</div>
    <div>24 / 27</div>
  </div>
  <div class="frame" style="display:grid; gap:8vh; align-content:center; min-height:80vh">
    <div class="kicker" data-anim>The Question</div>
    <h1 class="h-hero" style="font-size:7vw; line-height:1.15">
      <span data-anim style="display:block">你的公司里，</span>
      <span data-anim style="display:block">哪些岗位本来就</span>
      <span data-anim style="display:block">不该由人来做？</span>
    </h1>
    <p class="lead" style="max-width:50vw" data-anim>
      这个问题，不是技术问题，是架构问题。
    </p>
  </div>
  <div class="foot">
    <div>Page 24 · The Question</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：
- Hero 页留白越多越好，只放一个问题
- `h-hero` 字号视长度调整（7vw 适合 3 行，10vw 适合 1 行）
- 用 `<br>` 手工断行，确保断点在语义处
- 尾巴可以再给一行 `lead` 作为点破

---

## Layout 8: 大引用页（Big Quote · 衬线金句）

```html
<section class="slide light" data-animate="quote">
  <div class="chrome">
    <div>The Takeaway · 核心金句</div>
    <div>18 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:5vh; align-content:center; min-height:80vh">
    <div class="kicker" data-anim>Quote · 金句</div>
    <blockquote style="font-family:var(--serif-zh); font-weight:700; font-size:5.8vw; line-height:1.2; letter-spacing:-.01em; max-width:72vw">
      <span data-anim="line" style="display:block">"没有交接,</span>
      <span data-anim="line" style="display:block">所有人都在构建。"</span>
    </blockquote>
    <p class="lead" style="max-width:55vw; opacity:.65" data-anim>
      Without the handoff, everyone builds.<br>
      And that makes all the difference.
    </p>
    <div class="meta-row" data-anim>
      <span>— Luke Wroblewski</span><span>·</span><span>2026.04.16</span>
    </div>
  </div>
  <div class="foot">
    <div>Page 18 · 金句</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：
- 整页留白,只放一个大引用 + 出处
- `<blockquote>` 用 inline style 单独放大（5-6vw）,不要用 `h-hero`（那是页面主标题的命名）
- 下面跟随英文原文（lead · opacity:.65）制造层级
- 配 `meta-row` 写出处 · 日期

---

## Layout 9: 并列对比（A vs B · 旧 vs 新）

```html
<section class="slide light" data-animate="directional">
  <div class="chrome">
    <div>旧 vs 新 · The Shift</div>
    <div>12 / 25</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker" data-anim>Before / After · 范式转变</div>
    <h2 class="h-xl" style="margin-bottom:4vh" data-anim>从交接到共建</h2>

    <div class="grid-2-6-6" style="gap:5vw 4vh">
      <!-- 左列：旧 -->
      <div data-anim="left" style="padding:3vh 2vw; border-left:3px solid currentColor; opacity:.55">
        <div class="kicker" style="opacity:.9">Before · 旧模式</div>
        <h3 class="h-md" style="margin-top:2vh">设计 → 开发 → 交接</h3>
        <ul style="margin-top:3vh; padding-left:1.2em; display:flex; flex-direction:column; gap:1.4vh; font-family:var(--sans-zh); font-size:max(14px,1.1vw); line-height:1.55">
          <li>设计师在 Figma 做稿</li>
          <li>开发者盯着文件翻译像素</li>
          <li>反复 PR 沟通对齐</li>
          <li>非技术人员无法触碰代码</li>
        </ul>
      </div>
      <!-- 右列:新 -->
      <div data-anim="right" style="padding:3vh 2vw; border-left:3px solid currentColor">
        <div class="kicker" style="opacity:.9">After · 新模式</div>
        <h3 class="h-md" style="margin-top:2vh">同工具 · 并行 · 共建</h3>
        <ul style="margin-top:3vh; padding-left:1.2em; display:flex; flex-direction:column; gap:1.4vh; font-family:var(--sans-zh); font-size:max(14px,1.1vw); line-height:1.55">
          <li>三个角色同时在 Intent 工作</li>
          <li>agents.md 作为共享上下文</li>
          <li>代理处理对齐 / 冲突 / 动画</li>
          <li>任何人都能安全贡献代码</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 12 · 范式转变</div>
    <div>Before / After</div>
  </div>
</section>
```

**要点**：
- 用 `.grid-2-6-6`（1:1）左右分半
- 左列 `opacity:.55` 做"旧"的视觉弱化,右列满亮度做"新"的突出
- 两列都用 `border-left:3px solid` + `padding-left` 做引用块感
- 每列结构统一:`kicker` → `h-md` → `<ul>` 要点,节奏一致

---

## Layout 10: 图文混排（Lead Image + Side Text）

```html
<section class="slide light">
  <div class="chrome">
    <div>Design First · 设计先行</div>
    <div>08 / 16</div>
  </div>
  <div class="frame grid-2-8-4" style="padding-top:6vh">
    <!-- 左列:大段正文 + 引用 -->
    <div>
      <div class="kicker" data-anim>Phase 01 · 设计阶段</div>
      <h2 class="h-xl" style="margin-top:1vh; margin-bottom:3vh" data-anim>设计先行 · 2 周</h2>

      <p class="lead" style="margin-bottom:3vh" data-anim>
        在 Figma 中完成视觉探索与设计系统,网格 / 排版 / 颜色变量 / 可复用组件,桌面和移动端稿件几轮反馈迭代。
      </p>

      <p data-anim style="font-family:var(--sans-zh); font-size:max(14px,1.15vw); line-height:1.75; opacity:.78; margin-bottom:2.4vh">
        两周之内,视觉风格、粗略结构、方向性内容全部稳定。这是扎实的传统设计流程——在这里还没什么新鲜事。
      </p>

      <div class="callout" style="margin-top:3vh" data-anim>
        "This phase was pretty standard.<br>Just a solid Web design process."
        <div class="callout-src">— Luke Wroblewski</div>
      </div>
    </div>
    <!-- 右列:T2 Float 自由留白 · 竖版或方形 · 不加"产品截图"类图注 -->
    <figure class="t-float r-3x4" data-treatment="t-float" data-anim>
      <img src="images/figma.png" alt="Figma design system">
    </figure>
  </div>
  <div class="foot">
    <div>Page 08 · Design First</div>
    <div>约 2 周</div>
  </div>
</section>
```

**要点**：
- `.grid-2-8-4`(8:4) 让正文占主导,图片作辅助
- 左列包含多种信息层级:kicker → 大标题 → lead → 正文段落 → callout(引用)
- 右列图片用 **竖版 3:4** 或方形 1:1,避免和左列文本竞争注意力
- 这种布局适合**页面信息量偏大**的场景(不像 Layout 4 只有一句金句)

---

## 附录：常用网格模板

| 类名 | 配比 | 用途 |
|---|---|---|
| `.grid-2-6-6` | 6:6（1:1） | 对半分 |
| `.grid-2-7-5` | 7:5 | 文字为主 + 辅助图 |
| `.grid-2-8-4` | 8:4（2:1） | 大段文字 + 小图/数据 |
| `.grid-3` | 1:1:1 | 3 项并列（案例/截图） |
| `.grid-3-3` | 3×2 | 6 图矩阵 |
| `.grid-6` | 3×2 | 6 个数据卡片 |

所有网格都预留 `gap: 3vw 4vh`（水平 3vw、竖直 4vh），可以单独覆写。

---

## 页面节奏建议

一场 25-30 页的分享，推荐以下节奏：

1. **Hero Cover**（第 1 页）
2. **Act Divider**（第一幕开场，hero light 或 hero dark）
3. **Big Numbers**（抛硬数据制造冲击）
4. **Quote + Image**（讲身份反差/挂钩）
5. **Image Grid**（证据支撑）
6. **Hero Question**（幕收束，留悬念）
7. ... 第二幕、第三幕同样节奏 ...
8. **Hero Close**（最后一页，问题或致谢）

hero 页与 non-hero 页应该 **2-3 : 1 比例交错**，不要连续超过 3 页 non-hero，也不要连续超过 2 页 hero。
