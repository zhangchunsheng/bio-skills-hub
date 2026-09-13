# 截图美化语义规则

用于把用户提供的产品截图、网页截图、代码截图、设计稿截图处理成符合 [`image-treatments.md`](image-treatments.md) 范式规范的图片资产。本文件是 8 套范式(T1-T8)中**截图类**的子集说明:T3 Inset(默认截图处理)、T4 Browser Chrome(网页截图)、T5 Device Frame(移动/桌面 App 截图)。其它范式见主文档。

> **重大变更**: 旧文档里"CleanShot X 式截图居中 + 背景填充"现在统一收敛到 **T3 Inset** 这一档。**不再**用"圆角+阴影+1px 边框"作为所有截图的默认外观,那是被 [`image-treatments.md`](image-treatments.md) 显式禁止的卡片化旧行为。

## 优先级

1. **程序化适配优先**: 截图内容、文字、UI 细节需要保真时,不要重画;创建目标比例画布,把原截图等比缩放后放入画布(T3 Inset)。
2. **GPT-M 2.0 只做重构**: 只有原图过长、过窄、信息太乱、需要 UI 情景化或概念化表达时,才使用"截图再设计 / UI 情景图"。
3. **范式先行**: 先在 T3 / T4 / T5 里选一档,再决定截图适配参数。不要回退到"圆角+阴影+figcap 原始截图"的旧范式。

## 开始前询问

在主流程 Step 1 中,只要用户可能提供截图,就先问清楚:

- 截图在哪个文件夹?是否包含网页、App、代码、dashboard、设计稿或旧 PPT?
- 这批截图要**保真展示**、**统一美化**、**重新设计成 UI 情景图**,还是混合处理?
- 最终要放进哪些槽位:21:9 顶图、16:10 主图、4:3 侧图、1:1 方图、还是多图网格?
- 是否必须保留所有文字和数据?是否需要隐藏账号、头像、项目名等敏感信息?
- 构图希望居中、左上、右下,还是根据页面内容自动判断?

如果在 Claude Code 中,用 Ask Question / `ask_question` 做这些澄清;如果在 Codex 中,用普通对话询问,不要调用 Ask Question。

## 处理链路

1. **先匹配版式**:根据内容选择模板 layout,确定截图槽位尺寸和比例。
2. **再选处理方式**:
   - 要保真:程序化适配,不重画截图。
   - 要统一视觉但不改内容:程序化适配 + 主题背景。
   - 原图不可用或需要解释概念:再走 GPT-M 2.0 截图再设计。
3. **再选择背景**:优先使用内置背景资产,不应该每张截图临时生成一种风格。
4. **最后合成截图**:创建目标比例画布,背景 cover 铺满,截图等比缩放后按 `padding` 和 `alignment` 放入。

默认不要裁掉截图内容。只有截图已经按目标槽位重新生成,或者用户明确允许裁切时,才使用 cover 裁切。

## 语义参数

每次处理截图前,先确定这 7 个参数:

| 参数 | 可选值 | 判断方式 |
|---|---|---|
| `ratio` | `21:9` / `16:10` / `16:9` / `4:3` / `1:1` | 跟随模板图片槽位(`.r-16x10` 等),不要跟随原截图比例 |
| `background` | `plain` / `gradient` / `wallpaper` / `blurred` / `grid` / `paper` | T3 默认 `plain`(浅色基底);Style A 可 `paper`;Style B 用 `grid` |
| `padding` | `compact` / `standard` / `spacious` | 普通截图 standard;文字密集或高截图 spacious;小图组 compact |
| `inset` | `none` / `subtle` / `balanced` | **T3 默认 `subtle`**(仅靠浅色基底色阶分层);不靠阴影/边框 |
| `shadow` | `none` / `soft` / `editorial` | **T3 / T4 / T5 / T6 默认 `none`**;只有 T8 (Edge Card) 才允许 `soft` |
| `corners` | `square` / `small` / `medium` | **T3 / T4 / T5 / T6 默认 `square`**(无圆角);T8 可 `small`(6px) |
| `alignment` | `center` / `top-left` / `top-right` / `bottom-left` / `bottom-right` | 跟随页面构图,不是永远居中 |

> **重要**: 上表中只有 T3 / T4 / T5 / T6 适用本文件的截图处理。T1 / T2 / T7 / T8 的范式不依赖这 7 个参数(分别是全屏出血、纯留白、背景虚化、营销卡片)。完整规范见 [`image-treatments.md`](image-treatments.md)。
## 风格映射

### 截图处理默认走 T3 (Inset)

**无论 Style A 还是 Style B,所有原始截图默认走 T3 Inset**,只在 `background` / `padding` 两个参数上有差异:

```text
# T3 Inset 通用默认
ratio:跟随槽位, background:plain, padding:standard, inset:subtle, shadow:none, corners:square, alignment:center
```

### Style A · 电子杂志风

- 背景: `paper` / `blurred` / 低饱和 `gradient`
- 质感:纸张、墨水、胶片颗粒、暖白、低对比
- 截图:**无圆角无阴影**,完全靠浅色色阶分层;不要像 SaaS 营销卡片
- 背景:优先用 CSS 生成 `paper` / `blurred` / 低饱和渐变；若完整源码中的可选背景资产已安装，也可按槽位裁切复用。
- 推荐语义:

```text
ratio:16:10, background:paper, padding:standard, inset:subtle, shadow:none, corners:square, alignment:center
```

### Style B · 瑞士国际主义

- 背景: `plain` / `grid` / `dot-matrix`
- 色彩:只允许当前锚点色作为极低占比强调;不要大面积亮色块
- 截图:直角、无阴影、无圆角、少量 hairline 或顶部 accent 线
- 背景:优先用 CSS 生成网格或点阵；若完整源码中的可选背景资产已安装，也可按槽位裁切复用，但只用当前 accent,不要混色。
- 推荐语义:

```text
ratio:21:9, background:grid, padding:standard, inset:subtle, shadow:none, corners:square, alignment:center
```

## 背景强度规则

截图背景是“托底”,不是主视觉。

- 如果 `alignment` 不确定,背景中心和四角都必须安静,不要放显眼色块。
- 如果截图要放在右下角,右下角不能有强色块;其他位置同理。
- 瑞士风锚点色只做 `5%-8%` 视觉占比的淡线、点阵或极浅几何场,不要生成高亮蓝条、大色块、霓虹渐变。
- 背景不能有文字、logo、图标、人物、设备、边框、明显主体或方向性构图。
- 背景必须 crop-safe:裁成 `21:9`、`16:10`、`4:3`、`1:1` 都不能暴露“被裁掉”的痕迹。

## 可选主题背景资产（源码图库）

完整源码仓库包含一组预生成背景，但为兼容仅允许文本文件的技能仓库，它们不属于核心安装包。处理截图时优先用 CSS 的渐变、纸张纹理、网格或点阵实现相同语义；仅当完整源码中的资产已安装时再复用它们。

背景图之后由程序复用到每张截图中。不要把背景当作单张 slide 来画,背景图内部不能有标题、页脚、边框、logo、人物或明显主体。

### Style A · 5 套主题背景

| 主题 | 内置资产 | 背景语义 |
|---|---|---|
| 墨水经典 | `resources/screenshot-backgrounds/style-a/monocle-classic.webp` | 黑白灰纸张纹理、柔和阴影、细颗粒 |
| 靛蓝瓷 | `resources/screenshot-backgrounds/style-a/indigo-porcelain.webp` | 靛蓝低饱和墨色、纸感渐变、轻微噪点 |
| 森林墨 | `resources/screenshot-backgrounds/style-a/forest-ink.webp` | 模糊植物阴影、低饱和绿色、纸张颗粒 |
| 牛皮纸 | `resources/screenshot-backgrounds/style-a/kraft-paper.webp` | 暖纸色、淡墨阴影、复古印刷颗粒 |
| 沙丘 | `resources/screenshot-backgrounds/style-a/dune.webp` | 沙色/灰调柔和渐变、低对比、留白安静 |

### Style B · 4 套主题背景

| 主题色 | 内置资产 | 背景语义 |
|---|---|---|
| IKB 蓝 | `resources/screenshot-backgrounds/style-b/ikb-dot-gradient.webp` | 点阵 + 低对比蓝色渐变,避免亮蓝大色块 |
| 柠檬黄 | `resources/screenshot-backgrounds/style-b/lemon-grid.webp` | 纯网格 + 稀疏点阵,黄色只做低透明细线/点 |
| 柠檬绿 | `resources/screenshot-backgrounds/style-b/lemon-green-dot-shadow.webp` | 点阵 + 阴影场,绿色只做轻微光感 |
| 安全橙 | `resources/screenshot-backgrounds/style-b/safety-orange-halftone.webp` | 模块化半调点阵 + 暗部阴影,橙色低占比 |

可选背景都是 1920×1080 级别的 16:9 WebP。若它们已安装，程序化合成时先把背景 cover 到目标画布，再裁成 `21:9` / `16:10` / `4:3` / `1:1` 等截图槽位；否则按同一构图规则用 CSS 背景实现。背景必须四角安静，因为截图可能居中、左上、右下或被裁成不同尺寸。

## 截图类型决策

| 原始素材 | 推荐处理(范式 + 做法) |
|---|---|---|
| 普通网页 / App / 桌面截图 | T3 Inset,程序化适配到目标比例 |
| 网页应用 / dashboard 截图 | **T4 Browser Chrome** 增强"在浏览器里"语境 |
| 移动端 App 截图 | **T5 Device Frame** (iPhone) |
| 桌面端原生 App 截图 | **T5 Device Frame** (Mac) 或 T3 Inset |
| 产品 UI 细节很重要 | T3 Inset + `fit-contain`,不重画 |
| 多张同气质证据截图 | **T6 Quiet Frame**,单图不加 figcaption |
| 改版前后对比 | T6 Quiet Frame 双图,只靠位置/标题区分 |
| 长网页截图 | T3 Inset;过长则拆成 2-3 张同尺寸面板 |
| 极窄 / 极高截图 | T3 Inset + `spacious` padding;仍太小再走 GPT-M 2.0 重构 |
| 代码截图 | T3 Inset + 暗底主题;Style A 用纸感背景;Style B 用浅网格背景 |
| 概念解释用的 UI 情景图 | GPT-M 2.0 重新设计,生成后用 T3 Inset 嵌入 |
| 营销首图 / 产品摄影 | T8 Edge Card(仅限 Beautiful Modern 风格) |
| 封面 / 章节主视觉 | T1 Bleed 或 T7 Backdrop(由 [`image-treatments.md`](image-treatments.md) 决定) |

## 生成背景图提示词

只有需要新增背景资产时才使用本节。常规截图美化不要实时生成背景,直接使用上方内置资产。

### Style A 背景

```text
16:9 crop-safe screenshot background for an editorial magazine / e-ink PPT system. Warm off-white paper texture, subtle ink wash, fine film grain, low contrast, quiet center and quiet corners, no text, no logo, no objects, no border, no focal subject. Suitable for cropping to 21:9, 16:10, 4:3, or 1:1.
```

### Style B 背景

```text
16:9 crop-safe screenshot background for a Swiss International Style PPT system. Pure off-white base, ultra-subtle 16-column grid and sparse dot matrix, one accent color only: [theme color], used at very low opacity as thin lines or tiny dots, no large bright color blocks. Quiet center and quiet corners, no text, no logo, no objects, no border, no focal subject. Suitable for cropping to 21:9, 16:10, 4:3, or 1:1.
```
