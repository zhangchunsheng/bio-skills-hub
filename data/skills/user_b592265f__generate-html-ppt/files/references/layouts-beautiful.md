 # Beautiful.ai 风格布局库

 本文档配合 `resources/template-beautiful.html` 使用，提供 12 套可直接复制的版式骨架。

> **图片处理范式升级**：12 套版式里所有图片区都已切换到 [`image-treatments.md`](image-treatments.md) 的 8 套范式（T1-T8）。**默认走 T2 Float / T6 Quiet Frame**；其它范式（截图用 T3、设备用 T5、营销首图用 T8、章节背景用 T7）按场景选。所有图必须写 `data-treatment="t-XXX"` 自检属性，**禁止**给 figcaption 写"原始截图/产品截图/Screenshot"。

| Layout | 图片范式 | 适用 |
|---|---|---|
| L01 开场封面 | T7 Backdrop 或 T1 Bleed | 满屏背景 + 标题 |
| L02 章节幕封 | T7 Backdrop | 模糊背景大字标题 |
| L03 三列卡片 | (无图)或 T8 Edge Card | 卡片自带卡片感,营销可用 T8 |
| L04 数据大字报 | (无图)或 T7 Backdrop | 纯数据时可走 T7 烘托 |
| L05 左文右图 | T2 Float | 单图,纯留白;不加图注 |
| L06 图片网格 | T6 Quiet Frame | 多图分组,单图无 figcap |
| L07 流水线 | (无图) | 流程图为主 |
| L08 智能图表 | (无图) | 图表为主 |
| L09 对比页 | T6 Quiet Frame(双图) | 视觉等价,只靠位置/标题区分 |
| L10 大引用 | (无图) | 文字为主 |
| L11 四列小卡 | (无图) | 卡片为主 |
| L12 收尾页 | T7 Backdrop | 收尾背景图 |



 ## 设计原则

 1. **12 列网格**：所有内容在 1920×1080 的 12 列网格上排布。
 2. **大量留白**：页面四周留 80px/120px 边距，内容之间用 `--space-6` 以上间距。
 3. **全局色彩基调统一**：全套 PPT 统一采用纯深色（Dark）或纯浅色（Light），严禁逐页黑白交替闪烁，保障视觉沉浸与连贯性。
 4. **动画编排**：所有需要入场动画的元素加 `.anim` 和 `.d1`~`.d8`；方向动画加 `.anim-left` / `.anim-right` / `.anim-scale`。
 5. **智能图表**：用 `.smart-chart` + `data-chart` 自动渲染，支持 bar / line / donut / pie / radar。
 6. **数字动画**：大数字加 `.count-up` + `data-value`，进入页面时自动 count-up。
 7. **纵向布局自适应策略（杜绝巨幅中空）**：
    - **无中间扩展内容（如仅有标题+2列卡片）**：使用 **方案一** `.frame.vstack`，设置 `justify-content: flex-start; gap: 40px;`（或 `justify-content: center;`），使内容紧凑靠拢，留白集中在底部。
    - **含流程图/数据指标（3段式结构）**：使用 **方案二** `.frame.between`，配合 `justify-content: space-between`，并在中间插入 `.pipeline`（步骤流程）或 `.stat-card`（指标行）填补空白。
 8. **双轨间距规范（首页舒展大气 ↔ 正文紧凑空间让渡）**：
    - **🟢 仅首页 PPT / 封面页 (Cover Slide / Hero Slide)**：豁免紧凑压缩，采用开阔舒展的纵向呼吸排版。Badge-to-Title: `16px ~ 28px`，Title-to-Subtitle: `20px ~ 32px`，Subtitle-to-Bottom: `36px ~ 56px`，赋予门面标题与金句极强的视觉冲击力与留白。
    - **🔵 正文内容页 (Content Slides)**：Badge/Eyebrow (`.eyebrow-pill` / `.kicker`)、主标题 (`.h-xl` / `.slide-title`)、副标题 (`.lead` / `.slide-subtitle`) 必须紧凑编排，严格控制页眉总高度 <= 200px (18%~22% 画布高)。Badge-to-Title 6~8px，Title-to-Subtitle 8~12px，Subtitle-to-Content 16~24px，将 78%+ 纵向空间让渡给卡片、图表与正文。可采用 `.header-compact` 容器或 `.header-split` 左右分栏容器。
 9. **主要内容大字号高可读性规范 (High-Legibility Large Font Standard · NON-NEGOTIABLE)**：
    - 杜绝 12px~14px 细碎小字感。在 1920×1080 舞台下，卡片正文与段落不低于 `20px~22px`，副标题 `22px~26px`，卡片标题 `26px~28px`，分类徽章 `16px~18px`，数据大字 `56px~72px`，表格与代码 `19px~21px`，保证大屏演示与各种缩放比例下的极佳易读性。
 10. **图片/图标/序号与标题单行同行并排规范 (Inline Icon, Badge & Title Standard · NON-NEGOTIABLE)**：
    - 在卡片（`.b-card`）、流水线步骤（`.pipeline-step`）、架构层等组件中，**图标（`.icon-box`）、序号徽标（`.card-num-badge` / `.step-nb`）与标题文字必须处于同一行展示**（使用 `.card-header` / `.step-header` 或在 `<h3>` 内前置图标），严禁无故分两行上下堆叠。**唯一例外**：仅在文字与图标过宽一行放不下时才酌情折行。

 ## 基础结构

 ```html
 <div class="slide light" id="sN">
   <div class="chrome"><div>栏目名</div><div>页码</div></div>
   <div class="frame">...</div>
   <div class="foot"><div>左下角</div><div>右下角</div></div>
 </div>
 ```

 可用主题类：
 - `.light` — 浅底黑字
 - `.dark` — 深底白字
 - `.hero.light` — 浅底 + 渐变光晕
 - `.hero.dark` — 深底 + 渐变光晕

 ## L01 开场封面 (Hero Cover · 首页专属宽间距排版)

 ```html
 <div class="slide hero light active" id="s1">
   <div class="cover-orb one anim-float"></div>
   <div class="cover-orb two anim-float" style="animation-delay:-2s"></div>
   <div class="cover-frame">
     <div class="cover-badge anim d1">DESIGN CANVAS</div>
     <h1 class="cover-title anim d2"><span class="gradient-text">写 Skill 前先回答四个问题</span></h1>
     <p class="cover-sub anim d3">“想清楚问题，比直接写代码更重要” —— 四问设计画布与核心架构规范</p>
     <div class="cover-divider anim d3"></div>
     <div class="cover-stats anim d4">
       <div class="cover-stat"><div class="n">04</div><div class="l">核心问题</div></div>
       <div class="cover-stat"><div class="n">100%</div><div class="l">架构清晰</div></div>
       <div class="cover-stat"><div class="n">Zero</div><div class="l">冗余代码</div></div>
     </div>
   </div>
 </div>
 ```

 ## L02 章节幕封 (Act Divider)

 ```html
 <div class="slide hero dark" id="sN">
   <div class="cover-frame">
     <div class="header-compact">
       <div class="kicker anim d1">Act I</div>
       <div class="h-hero anim d2">章节标题</div>
       <div class="lead anim d3" style="max-width:800px">章节引言</div>
     </div>
   </div>
 </div>
 ```

 ## L03 三列卡片 (3-Column Cards)

 ```html
 <div class="slide light" id="sN">
   <div class="chrome"><div>章节</div><div>页码</div></div>
   <div class="frame vstack" style="justify-content:center">
     <div class="header-compact">
       <div class="kicker anim d1">小标题</div>
       <div class="h-xl anim d2">大标题带 <span class="em">强调</span></div>
       <div class="lead anim d3" style="max-width:900px">说明文字</div>
     </div>
     <div class="grid-3 anim d4">
       <div class="b-card"><div class="card-header"><span class="icon-box">✦</span><h3>卡片标题</h3></div><p>内容</p></div>
       <div class="b-card teal"><div class="card-header"><span class="icon-box teal">◎</span><h3>卡片标题</h3></div><p>内容</p></div>
       <div class="b-card violet"><div class="card-header"><span class="icon-box violet">◈</span><h3>卡片标题</h3></div><p>内容</p></div>
     </div>
   </div>
   <div class="foot"><div>左</div><div>右</div></div>
 </div>
 ```

 ## L04 数据大字报 (Big Numbers)

 ```html
 <div class="slide light" id="sN">
   <div class="chrome"><div>数据</div><div>页码</div></div>
   <div class="frame vstack" style="justify-content:center">
     <div>
       <div class="kicker anim d1">Metrics</div>
       <div class="h-xl anim d2">关键数据</div>
     </div>
     <div class="grid-6 anim d3">
       <div class="stat-card"><div class="stat-label">Label</div><div class="stat-nb count-up" data-value="64">0</div><div class="stat-note">注释</div></div>
       <div class="stat-card"><div class="stat-label">Label</div><div class="stat-nb count-up" data-value="110" data-suffix="K+">0</div><div class="stat-note">注释</div></div>
       <div class="stat-card"><div class="stat-label">Label</div><div class="stat-nb count-up" data-value="5166" data-suffix="">0</div><div class="stat-note">注释</div></div>
       <div class="stat-card"><div class="stat-label">Label</div><div class="stat-nb count-up" data-value="41" data-suffix="K+">0</div><div class="stat-note">注释</div></div>
       <div class="stat-card"><div class="stat-label">Label</div><div class="stat-nb count-up" data-value="19">0</div><div class="stat-note">注释</div></div>
       <div class="stat-card"><div class="stat-label">Label</div><div class="stat-nb count-up" data-value="608" data-suffix="+">0</div><div class="stat-note">注释</div></div>
     </div>
   </div>
 </div>
 ```

 ## L05 左文右图 (Text + Image)

 ```html
 <div class="slide light" id="sN">
   <div class="chrome"><div>章节</div><div>页码</div></div>
   <div class="frame grid-2-7-5" style="align-items:center">
     <div class="vstack">
       <div class="kicker anim d1">Kicker</div>
       <div class="h-xl anim d2">标题</div>
       <div class="lead anim d3">正文说明</div>
       <div class="quote-block anim d4">
         <div class="quote-text">引用内容</div>
         <div class="quote-src">— 来源</div>
       </div>
     </div>
     <!-- T2 Float 自由留白（默认范式,无圆角无阴影,无"产品截图"图注） -->
     <figure class="t-float r-16x10 anim-right d3" data-treatment="t-float">
       <img src="images/xxx.png" alt="描述">
     </figure>
   </div>
 </div>
 ```

 ## L06 图片网格 (Image Grid)

 ```html
 <div class="slide light" id="sN">
   <div class="chrome"><div>Gallery</div><div>页码</div></div>
   <div class="frame vstack" style="justify-content:center">
     <div>
       <div class="kicker anim d1">Proof</div>
       <div class="h-xl anim d2">图片网格标题</div>
     </div>
     <div class="t-quiet-grid anim d3" data-treatment="t-quiet">
       <!-- T6 Quiet Frame 多图分组,单图无 figcaption -->
       <figure class="t-quiet" style="height:24vh"><img src="images/1.png" alt="图1"></figure>
       <figure class="t-quiet" style="height:24vh"><img src="images/2.png" alt="图2"></figure>
       <figure class="t-quiet" style="height:24vh"><img src="images/3.png" alt="图3"></figure>
       <figure class="t-quiet" style="height:24vh"><img src="images/4.png" alt="图4"></figure>
       <figure class="t-quiet" style="height:24vh"><img src="images/5.png" alt="图5"></figure>
       <figure class="t-quiet" style="height:24vh"><img src="images/6.png" alt="图6"></figure>
     </div>
   </div>
 </div>
 ```

 ## L07 流水线 (Pipeline)

 ```html
 <div class="slide light" id="sN">
   <div class="chrome"><div>Workflow</div><div>页码</div></div>
   <div class="frame vstack" style="justify-content:center">
     <div>
       <div class="kicker anim d1">Pipeline</div>
       <div class="h-xl anim d2">流程标题</div>
     </div>
     <div class="pipeline anim d3">
       <div class="pipeline-step"><div class="step-header"><span class="step-nb">01</span><h3>步骤一</h3></div><p>说明</p></div>
       <div class="pipeline-step"><div class="step-header"><span class="step-nb">02</span><h3>步骤二</h3></div><p>说明</p></div>
       <div class="pipeline-step"><div class="step-header"><span class="step-nb">03</span><h3>步骤三</h3></div><p>说明</p></div>
       <div class="pipeline-step"><div class="step-header"><span class="step-nb">04</span><h3>步骤四</h3></div><p>说明</p></div>
     </div>
   </div>
 </div>
 ```

 ## L08 智能图表 (Smart Charts)

 ```html
 <div class="slide light" id="sN">
   <div class="chrome"><div>Data</div><div>页码</div></div>
   <div class="frame vstack" style="justify-content:center">
     <div>
       <div class="kicker anim d1">Insights</div>
       <div class="h-xl anim d2">数据洞察</div>
     </div>
     <div class="grid-2 anim d3" style="align-items:stretch;height:520px">
       <div class="smart-chart" data-chart='{"type":"donut","data":[{"name":"Direct","value":35},{"name":"Social","value":45},{"name":"Organic","value":20}]}'></div>
       <div class="smart-chart" data-chart='{"type":"bar","labels":["Mon","Tue","Wed","Thu","Fri"],"series":[{"name":"Visits","data":[120,190,150,220,280]}]}'></div>
     </div>
   </div>
 </div>
 ```

 ## L09 对比页 (Comparison)

 ```html
 <div class="slide light" id="sN">
   <div class="chrome"><div>Compare</div><div>页码</div></div>
   <div class="frame center">
     <div class="kicker anim d1">Before vs After</div>
     <div class="h-xl anim d2" style="margin-bottom:var(--space-8)">对比标题</div>
     <div class="compare anim d3">
       <div class="compare-card">
         <div class="label">Before</div>
         <div class="value">3x</div>
         <p class="caption">旧方案</p>
       </div>
       <div class="compare-vs anim-scale d4">VS</div>
       <div class="compare-card">
         <div class="label">After</div>
         <div class="value" style="color:var(--b-accent)">1x</div>
         <p class="caption">新方案</p>
       </div>
     </div>
   </div>
 </div>
 ```

 ## L10 大引用 (Big Quote)

 ```html
 <div class="slide dark" id="sN">
   <div class="chrome"><div>Quote</div><div>页码</div></div>
   <div class="frame center">
     <div class="quote-block anim d1" style="max-width:1100px">
       <div class="quote-text">一句话金句，放在页面中央，字号最大。</div>
       <div class="quote-src">— 作者</div>
     </div>
   </div>
 </div>
 ```

 ## L11 四列小卡 (4-Column)

 ```html
 <div class="slide light" id="sN">
   <div class="chrome"><div>Features</div><div>页码</div></div>
   <div class="frame vstack" style="justify-content:center">
     <div>
       <div class="kicker anim d1">Features</div>
       <div class="h-xl anim d2">四个特性</div>
     </div>
     <div class="grid-4 anim d3">
       <div class="b-card glass"><h3>特性 A</h3><p>说明</p></div>
       <div class="b-card glass"><h3>特性 B</h3><p>说明</p></div>
       <div class="b-card glass"><h3>特性 C</h3><p>说明</p></div>
       <div class="b-card glass"><h3>特性 D</h3><p>说明</p></div>
     </div>
   </div>
 </div>
 ```

 ## L12 收尾页 (Closing)

 ```html
 <div class="slide hero dark" id="sN">
   <div class="cover-frame">
     <div class="h-hero anim d1">Thank You</div>
     <div class="lead anim d2" style="max-width:800px">总结语或行动号召</div>
     <div class="cover-divider anim d3"></div>
     <div class="hstack anim d4" style="gap:var(--space-6)">
       <div class="tag accent">#hashtag</div>
       <div class="tag accent">@handle</div>
     </div>
   </div>
 </div>
 ```

## L13 架构/代码树与多卡片左右对比布局 (Directory Blueprint / Code + Cards Grid · 垂直左对齐标准版式)

 ```html
 <div class="slide dark" id="sN">
   <div class="grid-overlay"></div>
   <div class="orb orb-1"></div>
   <div class="orb orb-3"></div>
   <div class="page-num">05 / 15</div>
   <div class="slide-content center-group">
     <!-- 垂直左对齐经典紧凑页眉 -->
     <div class="header-compact">
       <div class="eyebrow anim d1"><span class="eyebrow-dot"></span> DIRECTORY BLUEPRINT</div>
       <h1 class="hero-title anim d2">Skill 标准工程目录结构</h1>
       <p class="hero-subtitle anim d3">遵循标准化组织规范，兼顾极简主义与扩展能力</p>
     </div>
     <!-- 2列网格：左侧代码树 + 右侧3卡片 -->
     <div class="grid-2 anim d4" style="width: 100%; align-items: stretch;">
       <div class="code-box">
         <div class="code-box-header">📂 my-skill/ 目录树</div>
         <pre class="code-tree">
 <span class="kw">my-skill/</span>
 ├── <span class="str">SKILL.md</span>               <span class="cmt"># 唯一必需（技能大脑）</span>
 ├── <span class="prop">scripts/</span>               <span class="cmt"># 确定性可执行代码</span>
 │   ├── <span class="fn">classify_intent.py</span> <span class="cmt"># 意图分类</span>
 │   └── <span class="fn">generate_ticket.py</span>  <span class="cmt"># 工单生成</span>
 ├── <span class="hl">references/</span>            <span class="cmt"># 领域参考文档</span>
 │   ├── <span class="str">policies.md</span>        <span class="cmt"># 售后政策</span>
 │   └── <span class="str">templates.md</span>       <span class="cmt"># 话术库</span>
 └── <span class="prop">assets/</span>                <span class="cmt"># 输出模板素材</span>
     └── <span class="str">report_schema.json</span></pre>
       </div>
       <div class="cards-column">
         <div class="b-card accent-indigo">
           <div class="card-title-row"><span>📑 SKILL.md</span> <span class="badge-tag badge-success">唯一必需</span></div>
           <p class="card-text">YAML 元数据 + 核心分步工作流指令。调度 scripts 与 references，是指挥官角色。</p>
         </div>
         <div class="b-card accent-amber">
           <div class="card-title-row"><span>⚙️ scripts/</span> <span class="badge-tag badge-info">确定性计算</span></div>
           <p class="card-text">数据解析、分类算法、格式校验等确定性代码，直接由环境执行，节省 Token。</p>
         </div>
         <div class="b-card accent-violet">
           <div class="card-title-row"><span>📚 references/ & assets/</span> <span class="badge-tag badge-info">知识与资产</span></div>
           <p class="card-text">references 存行业政策、API 规范；assets 存报表样例与模板，按需引用。</p>
         </div>
       </div>
     </div>
   </div>
 </div>
 ```

 ## 动画类速查

 | 类名 | 效果 |
 |------|------|
 | `.anim` | 默认从下方弹簧入场 |
 | `.anim-left` | 从左侧弹簧入场 |
 | `.anim-right` | 从右侧弹簧入场 |
 | `.anim-scale` | 缩放弹簧入场 |
 | `.anim-float` | 持续上下漂浮 |
 | `.d1` ~ `.d8` | 延迟触发顺序 |

 ## 智能图表类型

 | type | 必需字段 |
 |------|---------|
 | `bar` | `labels`, `series[].name`, `series[].data` |
 | `line` | `labels`, `series[].name`, `series[].data` |
 | `donut` / `pie` | `data[].name`, `data[].value` |
 | `radar` | `indicators[].name`, `indicators[].max`, `series[].name`, `series[].data` |
