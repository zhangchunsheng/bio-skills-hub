---
name: web-inspiration-vault
description: 把收藏的网页拆出「视觉 DNA」（配色/字体/排版节奏）+ 文字内容，套进预设风格模板，生成统一风格的灵感卡片与单文件灵感库。当用户说"网页灵感库""收藏页转 HTML""提取网页配色/字体""网页风格模板""把这篇文章存成卡片""做灵感归档"，或提供一批网址/本地 SingleFile HTML 要求归档成作品集时使用。
agent_created: true
version: "1.4.0"
---

# 网页灵感风格模板库

> 一句话：网页收藏的终局不是存链接，是**拆出风格和内容、重组进自己的模板体系**。
> 跟财报拆结构再套披露模板，是同一件事。

## 核心立场（先读这三条，能省很多返工）

1. **是结构化理解，不是截图。** 全流程解析 HTML/CSS 得到数值化参数（HEX、字体栈、
   基准间距、字号比），产出可搜索、可 diff、可复现的 JSON。不截图、不 OCR。
2. **风格与骨架解耦。** 「风格」= 视觉 token + 该风格独有的排版手法（写在 `styles/<id>/`）；
   「骨架」= 信息结构（灵感卡 / 月度一页纸 / 项目展示页）。
   两者正交，N×M 组合。加骨架不用动风格模板，反之亦然。
3. **待建的风格必须如实标注。** 目前只有「极简风」有成品模板。命中其它风格时会用极简风模板
   兜底渲染，同时在卡片上明写"该风格模板待建，配色与字体参数仍是原页真实值" ——
   绝不假装已支持。

## 何时用 / 不用

- 用：攒了一批好看网页想提炼视觉规律；要把收藏变成可展示的灵感库；要给文章/周报做统一风格归档。
- 不用：只想存一份离线快照 -> 直接上 SingleFile；只想摘正文 -> Readability / Obsidian Web Clipper；
  只想长期归档整站 -> ArchiveBox。本技能是**在这三者之上做"风格提炼与重组"**那一层。

## 环境依赖

- Python：`requests` `beautifulsoup4` `lxml` `jinja2`（均已在本机 venv 中）。
  venv 路径：`~/.workbuddy/binaries/python/envs/default/Scripts/python.exe`
- **不需要**无头浏览器。字段按 computed style 语义命名，将来接 Playwright 只需替换
  `collect_declarations()` 的数据源，下游模板零改动。

## 标准工作流

```bash
PY="~/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
SK="~/.workbuddy/skills/web-inspiration-vault"

# 1) 抓取（可选，也可直接把 URL 交给第 2 步）
#    会评估"抓全了没有"，没抓全会明确让你改用 SingleFile
"$PY" "$SK/scripts/fetch_page.py" "<URL>" --dir raw/

# 2) 提取视觉 DNA -> dna.json
"$PY" "$SK/scripts/extract_dna.py" "<URL 或 本地.html>" -o out/dna_01.json

# 3) 单张卡渲染（可选，建库时会自动做）
"$PY" "$SK/scripts/render_card.py" out/dna_01.json -o out/card.html
"$PY" "$SK/scripts/render_card.py" out/dna_01.json -o out/card.html --style minimalist

# 4) 汇总成单文件灵感库（零外部请求，离线永久可看）
"$PY" "$SK/scripts/build_vault.py" out/ -o out/vault.html --emit-cards --title "我的灵感库"

# 5) 回归测试
"$PY" "$SK/tests/test_extract_dna.py"
```

批量：把多个 URL 各自跑一遍 `extract_dna.py`，文件名用 `dna_*.json`，再跑一次 `build_vault.py`。

## SingleFile 是首选入口（重要）

**SingleFile 的产物本身就是"已冻结的网页"**：样式、字体、图片全部内联进一个 HTML 文件。
解析它比爬线上页面**更准也更稳**（不依赖原站存活、不受反爬影响、字体可离线保真）。

- 抓取结论是 `js-shell` / `no-css` 时，就用 SingleFile 插件存一份再跑第 2 步。
- 检测到 SingleFile 标记时，脚本会自动跳过外链 CSS 抓取。
- SingleFile：https://github.com/gildas-lormeau/SingleFile

## 输出物

| 文件 | 内容 |
|---|---|
| `dna_*.json` | 完整视觉 DNA：配色（含语义角色）/ 字体栈 / 排版节奏 / 效果信号 / 正文结构 / 风格评分 |
| `cards/*.html` | 每张卡的独立页面 |
| `vault.html` | 单文件灵感库，按风格分区 + 粘性筛选导航，零外部请求 |

## 风格评分口径

4 类风格各自按证据加权，归一化后取最高分：极简 / 杂志 / 科技 / 复古。
证据来自：彩色数、圆角、渐变、阴影、留白密度、底色亮度、强调色色相与饱和度、
衬线与否、等宽字体、字号比、**以及 HTML 痕迹**（`<font>`/`<center>`/`<marquee>`/`bgcolor`）。

三条已踩过的坑，已固化为测试：
- CSS 信号稀薄时（`style_signal_strength: weak`），基于 CSS 的结论自动减半；
  否则 1996 年的图片型站点会被判成"极简风"。
- `has_serif` 只看**标题字体/正文字体**是否为衬线，不看 CSS 里有没有出现过衬线族。
  否则带了个没用上的 `font-serif` 工具类的站点会被误判成杂志风。
- 字号比优先取 `html/body/h1-h6/p` 这些结构性选择器上的字号，避免被工具类字号阶梯拉爆。

## 已知限制（别踩，也别粉饰）

1. **CSS 变量定义了整站色板 ≠ 页面用了那么多色。** 已按"是否被 `var()` 真实引用"过滤，
   但复杂站点仍可能残留少量噪声色，`palette_size` 应视为量级参考而非精确值。
2. **远程字体只记录字体栈，不内嵌字体文件。** 卡片上的字体样例走系统回退，
   真正的字体保真请用 SingleFile 留档（字体已内联为 `data:font`）。
3. **风格边界模糊的站点会得到接近的分值**（例如奶油底极简站 vs 复古站）。
   卡片会同时列出 4 项分值，**不要只看冠军标签**，分值分布才是信息。
4. 需要 JS 渲染的关键样式（computed style）暂时拿不到 —— 这是接入 Playwright 的唯一动机。
5. 图片/封面暂不作为卡片视觉主体（用配色块表达）；如需要，next step 是 `--download-images`。

## 加新风格模板

```
styles/<id>/
  style.json          # 风格元数据：签名手法、禁忌、适用场景、判据出处
  card.css.txt        # 共享样式，强调色用 var(--card-accent)
  body.html.txt       # 卡片体（不含 <style>，供单卡与汇总库共用）
  card.html.txt       # 单卡外壳，include 上面两个
  # 后缀用 .txt 是发布要求：.css/.j2 不在平台扩展名白名单，而被代码
  # include 的模板又不能靠打包工具自动转 .md（转完功能即断）。
```
签名手法的意义：**风格区隔不能只靠换色**。杂志风要有首字下沉/多栏/pull quote，
科技风要有发光边框/等宽标签，复古风要有纹理/衬线大标题 —— 这些"排版动作"才是风格的身份证。

## v1.2 新增：设计体检 + 卡片网格 + 判据层

三件事，都是为了从"能跑"走到"可信"：

### 1. 设计体检（`dna["audit"]`）
把《Refactoring UI》《The Elements of Typographic Style》与 WCAG 的判据
转成可计算检查，每张卡都带等级（A–D）与逐条结论。判据清单见
`docs/design_criteria.md`。检查项包括：行宽（45–75 字符，66 理想）、行高（按角色取值）、
字号/间距阶梯相邻差（>=25%）、字重档位、对比度、灰阶色温、品牌色有效性、
阴影方向（光来自上方）、边框使用量。

**三条必须守住的诚实边界：**
- 判据读的是 **CSS 声明**，不是页面实际使用。设计系统完备的站点（如 RAND）会声明
  比页面用到的多得多的字号/字重/颜色，这类告警应按"站点可选范围偏宽"理解。
- **宁可说不知道，也不给假数字。** 拿不到正文栏宽时报告"行宽无法静态确定"，
  并说明"按容器估算会得到 N 字符，该数字不予采信"。
- **异常值先查来源，再改判据。** RAND 报"正文行高 1.0"时，真相是
  `:where(ul>li)::marker{line-height:1}` —— 伪元素不参与正文判据。

### 2. 卡片网格抽取 + 页面类型
`page_type` 分四类：`article` / `content_hub` / `listing` / `unknown`。
内容枢纽页（主题聚合页、索引页）正文段落极少但卡片有几十张，
纯文章抽取器会产出近乎空的 DNA。`dna["content"]["cards"]` 给出卡片原子：
标题 / 类型标签 / 日期 / 链接 / 是否带图。

**注意：`图片多 ≠ 杂志风`，必须绑定 `page_type`。** 第一版只按图片数量给杂志风加分，
结果 Tailwind 文档页（大量截图）被误判，造成回归。

### 3. 字体族系判定：`trusted_char()`
同一个坑出现三次，已根治：**品牌自定义字体的回退链不代表设计意图。**
- `fraktion, Lucida Console, Monaco, monospace` -> 曾被误读成"等宽"
- `suisse, Times New Roman, Georgia, serif` -> 曾被误读成"衬线"

第一族不在已知字体表里时，诚实的答案是 `unknown`（并在卡片上说明
"品牌自定义字体，族系未知"），而不是从兜底链里硬猜。

### 4. 新增风格模板：杂志风
签名手法（写在 `styles/magazine/style.json`）：双宽度版心、用 **`66ch`** 约束正文栏
（把 Bringhurst 的字符数判据直接写进 CSS）、衬线大标题 + 无衬线正文、
首字下沉、卡片网格、两层向下阴影、少用边框。

**多风格汇总的坑**：两套模板都定义 `.wrap`/`.rule`/`.label`，直接拼接会互相覆盖，
汇总库里所有卡片会变成同一种长相。`build_vault.py` 的 `scope_css()` 逐条选择器
加 `.style-<id>` 前缀隔离。

## 作者与联系方式

本技能由「七仔的AI工具箱」维护。公众号 / 抖音 / CSDN 同名。

## 版权与署名

本技能代码与模板为原创，可免费使用与二次分享；转载请注明出处。

`docs/design_criteria.md` 中的设计判据，方法论来源为 Adam Wathan & Steve Schoger 的
《Refactoring UI》、Robert Bringhurst 的《The Elements of Typographic Style》与 WCAG 无障碍标准。
本包内**只包含从这些来源提炼的规则与参数（思想与方法层面），不含任何原书原文摘录**；
作者名与书名仅作溯源署名。

## v1.3 新增：链接 -> 风格档案（资产留存与复用）

一条命令把任意页面变成一份**可检索、可 diff、可复用**的风格档案：

```bash
python scripts/extract_style_doc.py "<URL 或 本地.html>" --library <资产库目录>
python scripts/extract_style_doc.py "<URL>" --library <dir> --style-name 赛博风   # 手动指定风格名
python scripts/extract_style_doc.py --reindex --library <dir>                    # 从已有档案重建索引
```

### 资产库结构

```text
<library>/
  INDEX.md                     人读索引：按风格分区，含体检等级与修订次数
  assets.json                  机器读清单：URL 哈希 / 首次与最近提取 / 修订记录
  <风格>-<站点>.md              风格档案（front-matter + 七节正文），如 杂志风-rand.org.md
  dna/<风格>-<站点>.json        原始 DNA，供程序再消费
  _history/<名>.<时间戳>.md     同一 URL 重提取时旧版自动归档
```

### 档案七节

一、页面结构总览（含**真实抽取**的标题大纲，非推断）　二、设计语言量化提取
（配色 / 站点自报 token / 字体层级 / 栅格版心 / 效果信号）　三、内容卡片原子
　四、设计体检　五、可复用 CSS 变量（命名空间化，可直接复制）　
六、静态不可得的项　七、复用与复现命令

### 资产管理规则（设计意图）

- **风格名进文件名**，便于按风格检索与归档。
- **同一 URL 重复建档 = 修订，不新建重复文件**：旧版进 `_history/`，`assets.json` 记修订次数。
  同一份资产永远只有一个当前版本，不会滚成一堆 `_v2_final`。
- **置信度低于 0.40 标为 `未定风(某风)` 而不硬贴标签**，避免资产库里堆满"看似确定"的错误归类。
  也可用 `--style-name` 手动指定（例如分类器还没有的风格：赛博风）。
- `dna/` 里的 json 可以直接喂给 `build_vault.py` 生成统一风格的灵感库，
  即「档案 -> 卡片 -> 展厅」三段式复用。
- `docs/design_criteria.md` 是判据层：把《Refactoring UI》《The Elements of Typographic Style》
  与 WCAG 的规则转成可计算检查，并明确标注哪些项静态解析拿不到。

### 发布状态（SkillHub 免费发布）

- 扩展名已全部走白名单：模板文件用 `.txt` 后缀（`.css` / `.j2` 不在平台白名单里，
  而被代码 include/open 的文本文件不能靠打包工具自动转 `.md`，否则功能即断），
  加载路径集中在 `render_card.TPL_CARD / TPL_BODY / TPL_CSS` 与 `card_css_path()`。
- 已清除全部本机绝对路径（统一写 `~/`）与 Unicode 装饰符号（箭头、emoji、制表符会被平台渲染成 SKIP）。
- `_meta.json` 含 SkillHub 必需字段：`slug`（与目录名一致）/ `display_name` / `version`（三段式 SemVer）/ `author`。
- 已知未处理项：`styles/<风格>/<文件>` 是三级目录，**仅开放平台**会报「目录层级超限」；
  SkillHub 免费发布不受此限。若日后要上开放平台，把 `styles/<id>/x` 拍平为 `styles/<id>.x`
  并同步改 `render_card` 里的路径常量即可。

## v1.4：四套风格模板全部就绪

| 风格 | 签名手法（风格身份证，不是换色） | 实测表现（8 站资产库） |
|---|---|---|
| 极简风 minimalist | 发丝线 / 大留白 / 三档字重 / 强调色极省 | 科技爱好者周刊 11.8KB |
| 杂志风 magazine | 双宽度版心 / **66ch 正文栏** / 首字下沉 / 卡片矩阵 | RAND、Steph Ango |
| 科技赛博风 tech | 细网格底纹 / **霓虹发光线（零偏移带色阴影）** / 等宽终端标签 / 方形角标 | Tailwind、Stripe、Craig Mod、leerob |
| 复古 Vintage 风 retro | 纸感底 / **双线分隔** / 菱形装饰（纯 CSS）/ 点线引导 / 旧式数字 | Space Jam 1996 |

### 关于"赛博风"的一个设计取舍（重要）

赛博/科技风天然想用暗底，但交付物的**可读性红线要求浅底深字**。
本模板的解法是：**赛博感不靠暗底，靠纹理 + 单色霓虹 + 终端排版**：

- 26px 细网格底纹（透明度 4.5%）：蓝图 / 终端纸质感
- 2px 霓虹强调线，零偏移 + 带色阴影（这正是判据库里"发光 = 零偏移 + 带色阴影"的正解）
- 等宽字体承担全部标签与数据，方括号包裹小节名
- 状态灯、评分条端点一律用**方形**（非圆形），维持终端几何感

真需要暗色版时，`styles/tech/card.css.txt` 末尾留了注释块，覆盖三行即可切。
**这是刻意的默认值选择，不是没做。**

### 验证方式（控制变量法）

一次只加一套模板，加完立刻：① 跑 14 项单元测试；
② 用该风格对应的真实站点渲染，检查产物**有无未解析模板残留 / None / 空值**；
③ 跑 8 站全量分类回归，确认其它风格判定未被影响（本次四风格判定与加模板前完全一致）。
汇总库里四套风格靠 `scope_css()` 逐条加 `.style-<id>` 前缀隔离 —— 否则同名 `.wrap` / `.rule`
会互相覆盖，所有卡片会长成一个样。
