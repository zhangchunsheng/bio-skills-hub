# Generate HTML PPT (网页版 PPT 生成工具)

一个专为 AI 编程助手（如 Claude Code, Antigravity, Gemini CLI, Codex 等）打造的高质感 HTML 演示文稿（PPT）生成技能。基于 **Design System Specification (`design.md`) 规范架构**，内置 **35+ 套独立视觉设计 Preset（Bold Template Pack）**，结合固定 16:9 舞台与视口无缝融合规范，支持从零生成（Mode A）、PowerPoint (`.pptx`) 文件转换（Mode B）以及自媒体封面设计（Mode C）。

---

![Generate HTML PPT Demo](https://github.com/helloyxs/generate-html-ppt/blob/main/demo/beautiful-demo.gif)

在创建新PPT时支持直观的风格选择，避免Token浪费

![Generate HTML PPT Demo](https://github.com/helloyxs/generate-html-ppt/blob/main/demo/风格选择.gif)

---

## 🌟 核心亮点

**Generate HTML PPT** 让 AI 助手摆脱传统“AI 瓶颈”与简陋模板，无需手动编写复杂的 CSS/JS 代码，即可在浏览器中输出具备顶级设计质感、支持响应式缩放与富交互的网页版演示文稿。

### 1. 🎨 35+ 套视觉设计系统 (Design Recipe Pack)
* **丰富的风格库**：拥有包含 Beautiful Modern, Swiss International, Cyberpunk Dark, 8-Bit Orbit, Emerald Editorial, Retro Zine, Neo Grid Bold, Monochrome, Pastel Geometry, Vintage Editorial 等 35+ 种精心打造的视觉设计规范 (`design.md`)。
* **拒绝无脑 AI 风格**：每套 Presets 均包含独立且严谨的字体栈（Google Fonts / Fontshare）、颜色 Token、阴影阶梯、排版 Scale 与微动效规范，拒绝泛滥的浅蓝/紫渐变与通用系统字体。

### 2. 📺 固定 16:9 舞台与视口无缝融合 (Fixed Stage & Seamless Viewport)
* **16:9 绝对防错位舞台**：以 `1920×1080` 像素为标准分辨率设计，采用动态 JavaScript（`updateScale()`）与 CSS `transform` 进行全视口等比缩放。在手机、平板、4K 投影仪上均能保持完美的排版比例，杜绝响应式折行导致的“排版坍塌”。
* **视口无缝融合 (Seamless Viewport)**：通过 CSS 变量（`--viewport-bg`）与动态脚本（`updateViewportBg()`），自动将浏览器舞台外围背景色与当前幻灯片的切面背景色实时无缝同步，告别尴尬的硬切黑边。

### 3. 🎯 渐进式上下文加载 (Progressive Disclosure)
* **极高的 Token 效率**：大模型无需一次性读取数百 K 的模板代码。AI 助手首先读取 `designs/bold-template-pack/selection-index.json` 轻量元数据匹配风格，待用户选定后再**单点精准读取**对应模板的 `design.md` 进行构建，显著提升响应速度并降低消耗。

### 4. 🔀 灵活的三大工作模式 (Operational Modes)
* **Mode A: 从零创作演示文稿** — 包含需求对齐、风格视觉预览前置（Visual Style Preview）、品牌嗅探（Brand Asset Sniffing）、叙事弧线大纲（Narrative Arc）、灰度骨架确认（Wireframing）与分批填充内容。
* **Mode B: PPTX 文件一键转换** — 内置 Python 解析脚本（`extract-pptx.py`），自动提取 PowerPoint 中的文本、图片、矢量形状与演讲者备注（Speaker Notes），轻松将传统 PPT 升级为网页版。
* **Mode C: 多平台自媒体封面设计** — 自动提炼 PPT/文章核心要点，根据内置排版规范生成微信公众号 (21:9)、小红书 (3:4)、X/Twitter 等社交平台的封面 Prompt 及视觉产出。

### 5. 🚀 零依赖与单文件交付 (Zero Dependencies)
* 输出单个自包含 HTML 文件，内联全量 CSS 与 JS 逻辑（包含 CDN 备用链接）。无需 Node.js 运行时、npm 依赖或复杂的打包构建流程，支持离线即开即用，长久保存不出错。

### 6. 📊 富交互组件与数据可视化 (Rich UI Component Kit)
* 原生内置 **ECharts 交互图表**、**Mermaid.js 矢量流程图**、**代码高亮**、**数字递增动画 (`.count-up`)** 以及 **弹簧物理入场动画 (`.anim`)**。

### 7. 🎛️ 底部交互控制台与全景缩略图 (Controls Bar & Overview Gallery)
* 每次生成均自动内置底部毛玻璃悬浮控制栏，标配 **`◀ 上一页`**、**`01 / 15 进度条`**、**`下一页 ▶`**、**`🗂 全览`** 与 **`⛶ 全屏`** 交互按钮；支持一键开启全景卡片网格直达跳转（`O` 键全览、`F` 键全屏、`Esc` 退出），配合**双轨间距规范**（首页开阔大气呼吸感 ↔ 正文页眉三要素紧凑压缩），将 78%+ 黄金纵向空间留给核心内容。

### 8. 🔤 主要内容大字号高可读性标准 (High-Legibility Large Font Standard)
* 杜绝传统 12px~14px 细碎小字感。在 1920×1080 舞台下，所有文字阶梯经过专门的演说可读性校准：正文 `20px~22px`、副标题 `22px~26px`、卡片标题 `26px~28px`、分类徽章 `16px~18px`、数据大数字 `56px~72px`、表格与代码 `19px~21px`，无论在投影大屏还是笔记本缩放视口中均能清晰秒读。

### 9. 🔍 默认支持鼠标双击图片放大 (Default Double-Click Image Zoom & Lightbox)
* 原生标配图片全屏 Lightbox 交互：幻灯片中的任何图片**默认支持鼠标双击（dblclick）居中全屏放大**，再次双击、点击背景或按 `Esc` 退出；同页多张图片支持键盘 `←` / `→` 键与左右箭头流畅翻页浏览。

### 10. 🏷️ 图片/图标/序号徽章与文字单行同行并排规范 (Inline Icon, Badge & Title Standard)
* 在卡片、流水线步骤、架构层级等组件中，图标、Emoji、图片或序号徽章与对应的标题文字默认保持在同一行水平并排展示，杜绝无故分两行上下堆叠带来的空间浪费与视觉松散；仅在极限窄栏或超长文字放不下时才酌情折行。

---

## 📂 项目结构

项目针对 AI Agent 工作流进行了高度模块化设计：

```text
generate-html-ppt/
├── SKILL.md                  # AI 编程助手的工作流地图与生成规则
├── README.md                 # 中文说明文档
├── README_en.md              # 英文说明文档
├── designs/                  # 设计系统规范库
│   ├── bold-template-pack/   # 35+ 种设计 Preset 集合
│   │   ├── selection-index.json # 风格选择轻量索引
│   │   ├── deck-stage.js     # 舞台缩放与视口同步核心脚本
│   │   └── templates/        # 包含 8-bit-orbit, beautiful-modern, swiss 等 35+ 套 design.md
│   ├── viewport-base.css     # 16:9 舞台与视口基线 CSS
│   ├── STYLE_PRESETS.md      # 核心视觉主题参考
│   └── animation-patterns.md # 动画与微交互指南
├── references/               # AI 助手的排版、组件与配图指导手册
│   ├── checklist.md          # 幻灯片质量校验清单
│   ├── screenshot-framing.md # 截图带壳美化与排版规范
│   ├── image-prompts.md      # AI 文生图 Prompt 生成指南
│   └── covers.md             # 自媒体封面排版规范
├── resources/                # 基础模版与高清截图底图
│   ├── template.html         # Cyberpunk 主模版
│   ├── template-swiss.html   # Swiss International 主模版
│   ├── template-beautiful.html # Beautiful.ai 主模版
│   └── screenshot-backgrounds/
└── scripts/                  # 辅助工具脚本
    ├── extract-pptx.py       # Python 脚本：提取 PPTX 文本、图片与讲稿
    ├── validate-swiss-deck.mjs # Swiss 风格合规性 Node.js 校验脚本
    └── validate-fluid-deck.mjs # Fluid 主题 (Beautiful Modern / Cyberpunk Dark) 合规性校验脚本
```

---

## 🛠️ 安装说明

### 1. 使用 AI 助手一键安装（推荐）
向您的 AI 编程助手（如 Claude Code, Antigravity, Gemini CLI, Codex 等）发送以下指令：

```text
请将 `helloyxs/generate-html-ppt` 的指定发布版本或已审核 commit 安装为本地技能；安装前核对仓库地址、commit SHA 与本说明，再按需安装 `python-pptx`（仅 Mode B 需要）。
```

### 2. 在 Claude Code 中手动安装

```bash
# 1. 克隆仓库到本地技能目录
git clone https://github.com/helloyxs/generate-html-ppt.git ~/.claude/skills/generate-html-ppt
git -C ~/.claude/skills/generate-html-ppt checkout --detach 3167cd6a3cd2e9901e113c6e3ae728385e92f36d

# 2. 安装 Python 依赖（用于解析 .pptx，仅在使用 Mode B 时需要）
pip install python-pptx
```

### 3. 在 Codex / Antigravity 中手动安装

```bash
# 1. 克隆仓库到对应的技能目录
git clone https://github.com/helloyxs/generate-html-ppt.git ~/.codex/skills/generate-html-ppt
git -C ~/.codex/skills/generate-html-ppt checkout --detach 3167cd6a3cd2e9901e113c6e3ae728385e92f36d

# 2. 安装 Python 依赖
pip install python-pptx
```

在对话中，只需给 AI 传入 `SKILL.md`，或者告诉 AI 助手：“加载并遵循 `~/.claude/skills/generate-html-ppt/SKILL.md`”。

---

## 💡 使用指南

### 1. 从零开始生成演示文稿 (Mode A)
通过斜杠命令或直接描述您的需求：
```text
/generate-html-ppt "我想为一个开源云原生数据库项目制作一份商业路演 PPT"
```

AI 助手将严格遵循 **四阶段工作流**：
1. **需求对齐与风格推荐（含视觉预览）**：通过 7 个检查问题确认受众与时长，基于 `selection-index.json` 从 35+ 种 Preset 中推荐 2-3 个符合调性的设计方向（如 *Beautiful Modern*, *Swiss Style*, *8-Bit Orbit* 等），并支持生成轻量 1 Slide 风格对比卡（`style-preview.html`）或示例图供用户提前确认，消除试错不确定性；同时自动触发**品牌嗅探（Brand Asset Sniffing）**提取品牌主色与字体。
2. **视觉资产准备**：针对项目截图应用带壳美化（`screenshot-framing`），或根据 `image-prompts` 生成配套 AI 插画。
3. **设计系统灰度骨架确认 (Wireframing)**：根据选定的 `design.md` 单点规范，构建 `1920×1080` 舞台骨架，应用布局密度策略（防止中间尴尬中空，使用 `center-group` 垂直集中分组与 Hero 中间连通桥），生成 HTML 骨架文件并**暂停等待用户确认**。
4. **分批内容填充与交付**：骨架确认后分批填入精细文案与可视化图表，自动校验后在浏览器中打开 PPT。

### 2. 转换现有的 PPTX 文件 (Mode B)
提供本地 PowerPoint 文件路径：
```text
/generate-html-ppt "帮我把路径为 ./docs/Q3_Roadmap.pptx 的文件转换为 HTML 演示文稿"
```
AI 将自动运行 `python scripts/extract-pptx.py` 提取文字、矢量元素、高分辨率图片与演讲者备注，并将其精准映射到 HTML PPT 模板中。

### 3. 生成多平台社交封面 (Mode C)
生成 PPT 后可直接要求：
```text
"根据这份 PPT 的核心内容，帮我设计一张微信公众号 (21:9) 和一张小红书 (3:4) 的封面图"
```
AI 将依据 `references/covers.md` 规范生成适配不同社交平台的视觉封面。

---

## 🎨 视觉风格与 Presets 一览

系统内置了 **35+ 种独立设计规范**，覆盖商业、技术、学术、时尚、复古等各类演讲场景。以下为部分代表性风格展示：

| 风格 Preset | 视觉效果 (Preview) | 视觉基调 (Vibe) | 适合场景 | 核心设计元素 |
| :--- | :--- | :--- | :--- | :--- |
| **Beautiful Modern** | <img src="demo/previews/beautiful-modern.png" width="200" alt="Beautiful Modern"> | 优雅、现代、高端 | 商业路演、产品发布会 | 渐变光晕 Orb、大字报数字、`light`/`dark`/`hero` 主题交替 |
| **Swiss International** | <img src="demo/previews/swiss-international.png" width="200" alt="Swiss International"> | 严谨、极简、包豪斯 | 架构设计、学术汇报 | 22 种严格锁定的网格版式 (`S01-S22`)、大负空间、极简文字排版 |
| **Cyberpunk Dark** | <img src="demo/previews/cyberpunk-dark.png" width="200" alt="Cyberpunk Dark"> | 霓虹发光、极客感 | 技术分享、开源项目 | 卡片发光边框 (`.b-blue`, `.fill-teal`)、渐显入场动画 (`.a1`-`.a6`) |
| **8-Bit Orbit** | <img src="demo/previews/8-bit-orbit.png" width="200" alt="8-Bit Orbit"> | 像素怀旧、复古游戏 | 游戏开发、创意 Web3 | 像素边框、点阵字体、复古色彩对比 |
| **Emerald Editorial** | <img src="demo/previews/emerald-editorial.png" width="200" alt="Emerald Editorial"> | 深邃绿调、杂志质感 | 环保可持续、设计展 | 衬线标题、典雅网格、深绿色调与金色微发光 |
| **Neo Grid Bold** | <img src="demo/previews/neo-grid-bold.png" width="200" alt="Neo Grid Bold"> | 粗矿新丑风 (Neubrutalism) | 潮流品牌、青年沙龙 | 粗黑边框、硬投影、高饱和度对比块 |
| **Monochrome** | <img src="demo/previews/monochrome.png" width="200" alt="Monochrome"> | 黑白极简、黑客风格 | 代码演练、黑客松 | 纯黑纯白高对比、monospace 等宽字体 |

> 🖼️ **查看完整风格图鉴**：全部 37 款设计风格的高清预览图、色板 Token、字体搭配与选型决策矩阵，请参阅 📖 **[全量设计风格与 Presets 图鉴 (STYLE_GALLERY.md)](designs/STYLE_GALLERY.md)**。


---

## ⌨️ 快捷键与播放控制

在浏览器中打开生成的 HTML 幻灯片时，可使用以下快捷键：

* **下一页**：`右方向键 (→)`、`下方向键 (↓)`、`空格键 (Space)`、`PageDown`，或移动端向左轻扫。
* **上一页**：`左方向键 (←)`、`上方向键 (↑)`、`PageUp`，或移动端向右轻扫。
* **跳转首页 / 末页**：`Home` / `End` 键。
* **全览视图 (Overview)**：`O` 键。
* **全屏模式**：`F` 键。
* **页面锚点定位**：支持 URL Hash 实时同步（如直接访问 `#s3` 跳转第 3 页）。

---

## 🧠 项目哲学

1. **零依赖长寿生命周期 (Zero-Dependency Lifespan)**：生成的 HTML 文件不依赖任何外部后端或构建系统，在任何设备随时运行，且在 20 年后依然能够被浏览器完美打开。
2. **排版稳定性 (Layout Stability)**：固定 16:9 舞台结合 CSS transform 等比缩放，彻底解决屏幕比例变动导致“格式错乱”的行业难题。
3. **AI 原生工作流 (AI-Native Workflow)**：将复杂的代码调试转化为给 AI 的逻辑指令。借助 `design.md` 规则约束与校验脚本，大幅降低大模型的幻觉概率。

---

## 🔒 安全策略与远程资源披露 (Security & Subresource Integrity)

为了保障演示文稿在任何网络与企业环境下的**供应链安全**与**防篡改完整性**，本项目实施了严格的第三方静态资源治理策略：

### 1. 供应链安全基线
* **彻底排除风险镜像**：已全面移除被威胁情报标记的第三方镜像源（如 `cdn.bootcdn.net` 和 `cdn.staticfile.org`），杜绝供应链投毒与中间人劫持风险。
* **官方/高信誉 CDN 托管**：仅采用官方制品库与高信誉公共 CDN 源（`cdnjs.cloudflare.com`、`cdn.jsdelivr.net`、`unpkg.com`）。
* **版本完全固化**：所有外部资源严格锁定精确语义版本号，严禁使用 `@latest`、`@5`、`@10` 等不可控的浮动版本。
* **脚本完整性校验**：`template.html` 的可选脚本加载器对 CDN 和 `vendor/` 本地回退均使用固定 SHA-384 SRI 指纹；无法校验的字体和可选样式资源不作 SRI 覆盖，按浏览器的同源/CSP 策略处理。

### 2. 生成文件引用的远程资源与 SRI 指纹清单

| 依赖库 (Package) | 固化版本 (Version) | 受信官方源 (Verified CDN Mirrors) | SRI 完整性哈希 (SHA-384 Hash) |
| :--- | :--- | :--- | :--- |
| **ECharts** (图表引擎) | `5.5.0` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-o5uz97et3bErHvpKfD4Jz4n0JfhJDWABFuF4NP+iEEDxE1VwMWJ19QGR0lqFZnr6` |
| **Mermaid** (矢量图引擎) | `10.9.1` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-WmdflGW9aGfoBdHc4rRyWzYuAjEmDwMdGdiPNacbwfGKxBW/SO6guzuQ76qjnSlr` |
| **Marked** (Markdown 渲染) | `12.0.2` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-/TQbtLCAerC3jgaim+N78RZSDYV7ryeoBCVqTuzRrFec2akfBkHS7ACQ3PQhvMVi` |
| **Highlight.js** (代码高亮 JS) | `11.9.0` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-F/bZzf7p3Joyp5psL90p/p89AZJsndkSoGwRpXcZhleCWhd8SnRuoYo4d0yirjJp` |
| **Highlight.js** (暗色主题 CSS) | `11.9.0` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-oaMLBGEzBOJx3UHwac0cVndtX5fxGQIfnAeFZ35RTgqPcYlbprH9o9PUV/F8Le07` |
| **Lucide Icons** (图标库) | `0.344.0` | `jsdelivr` / `unpkg` | `sha384-tTkFttkBclaU1cloKwOi9xk3pbao3VZxTjLNBt8iFABWDBQibbAbWpVmO28zMuxq` |
| **Motion** (动效引擎) | `11.11.17` | 可选的、审核后的本地 `./assets/` 副本 | 缺失时禁用可选动效 |

### 3. 企业专有云 / 纯内网 / 离线部署 (Local Vendor Fallback)
在无法访问外网的物理隔离网络或严苛企业合规环境中，可在 HTML 文件同级目录下创建 `vendor/` 文件夹，并放入上表对应版本的 `.min.js` 文件。`template.html` 会优先加载这些本地文件，并以固定 SRI 哈希校验；校验失败时不会执行。Swiss 模板不会从 CDN 动态导入 Motion；只有在生成/分发时显式随演示文稿提供审核后的 `assets/motion.min.js` 才启用该可选动效，缺失时安全降级为无动效。

---

## 📄 开源协议

[MIT License](LICENSE) — 欢迎自由地使用、定制、修改并分享！

## 👏 致谢

感谢 [@zarazhangrui](https://github.com/zarazhangrui) 的 [frontend-slides](https://github.com/zarazhangrui/frontend-slides) 以及 [@op7418](https://github.com/op7418) 的 [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) 开源项目。
