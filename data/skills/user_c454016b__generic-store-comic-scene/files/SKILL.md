---
name: generic-store-comic-scene
version: 1.0.2
description: "Use this skill when generating OFFLINE RETAIL STORE comic scenes that place a STAFF MEMBER and a CUSTOMER in one frame — service storyboards, objection-handling panels, training comics, onboarding illustrations — for ANY brand and ANY retail category. Enforces four anti-drift mechanisms: ASYMMETRY LOCK (one-sided appearance features get symmetrized by the model; lock them with an EXACTLY ONE counter plus a viewer-side position description plus triple negative constraints plus a reference anchor — NEVER use abstract phrasing like 'the same hand as in the reference image', which was measured to produce the feature on BOTH sides), SLOT ASSIGNMENT (which character occupies which image slot, and how to stop opposite constraints from contaminating each other), REFERENCE ANCHORING (characters and store background pinned to reference images), and MINIMAL-DELTA regeneration for 'change only X, keep the rest' requests. Load before any ImageGen call for in-store two-person comics. Brand-specific assets live in profiles/; no brand is hardcoded."
agent_created: true
---

# 零售门店漫画场景生成（通用版）

## Overview

生成线下零售门店「**员工 + 顾客**」同框漫画场景（服务标准分镜、业务讲解、培训漫画、新人手册插图等）。
不限品牌、不限零售品类。品牌专属资产（角色参考图、锁定背景图、品类材质规则、角色形象规格）全部外置在 `profiles/` 目录，本技能主体只承载方法论。

本技能的机制来自**多轮实战迭代的经验提炼**，只保留与品牌无关的通用模式；品牌专属内容一律外置到 `profiles/`。

### 四条核心机制

| 机制 | 解决什么 | 失败代价 |
|------|----------|----------|
| **① 非对称锁定（ASYMMETRY LOCK）** | 模型会把「仅单侧」的外观特征对称化 | 最高频翻车点，多轮迭代反复出现 |
| **② 参考图锚定（REFERENCE ANCHORING）** | 人物形象、门店背景被模型自由发挥 | 背景漂移到"另一家店"、角色头部/发型漂移 |
| **③ 多角色槽位分配（SLOT ASSIGNMENT）** | 同框时谁占哪个图槽；两角色约束相反时互相污染 | 槽位错配、一侧的约束污染到另一角色 |
| **④ 最小修改原则（MINIMAL-DELTA）** | 说"其他不变"却改了构图 | 需整轮重做，迭代成本翻倍 |

> **最高频失败点 = 非对称特征漂移。** 只要同时做到「**EXACTLY ONE 计数词 + 视角侧位置描述 + 三重负面约束 + 角色参考图锚定 image1**」四要素组合，就能稳定通过（2026-09-10 A/B 实测结论）。

---

## When to use

- 用户要求生成任意品牌、任意零售品类的**线下门店内、员工与顾客同框**漫画/分镜/场景图。
- 任何调用 ImageGen 产出「店员 / 导购 / 顾问 + 顾客 / 客户」人物场景的任务（含 16:9 / 9:16 双比例）。
- 涉及以下任一约束时：**单侧非对称特征**（单只手套 / 单侧长袖 / 单侧配饰）、**品类或材质锁定**（仅某类商品 / 仅某材质）、**复用锁定门店背景**。

**不触发**：

- 纯产品详情图 → 属于产品详情图类技能的职责，不在本技能范围内。
- 纯空间图（无人物） → 用门店空间图工作流。
- 单人物、非门店场景 → 直接调 ImageGen 即可，无需本技能。

---

## Step 0：加载品牌档案（前置）

**先检查 `profiles/` 下是否存在目标品牌档案。**

```
profiles/
├── _TEMPLATE.md          # 空白模板 + 字段说明
├── <brand-a>.md          # 已填档案
└── <brand-b>.md
```

### 分两种情况处理

**A. 有档案** → 直接加载，按其填写内容组装 prompt。

**B. 没有档案（首次使用 / 新品牌）** → **不要停下，更不要自行编造参考图路径**。改用「**零素材模式**」：

1. 告知用户：无参考图也能生成，但**人物形象每次会变化**，适合先试效果；
2. 请用户提供场景描述（谁、在哪、做什么），据此组装**纯文字 prompt**；
3. 若用户要求形象固定，指向 `GETTING-STARTED.md` 第三节，引导其按 `profiles/_TEMPLATE.md` 建立档案；
4. 生成时**仍须执行下方全部 Hard constraints**，只把「参考图锚定」降级为「强文字约束」——**不要因为缺参考图就跳过非对称锁定与品类锁定**。

> 面向使用者的完整上手路径写在 `GETTING-STARTED.md`（该文件给用户看，非模型读）。

一个完整的品牌档案需要提供 7 组信息：

| # | 字段 | 说明 | 缺失后果 |
|---|------|------|----------|
| 1 | **主角色参考图** | 本地绝对路径，优先占 image1 | 形象无锚定，非对称特征必漂移 |
| 2 | **角色清单与槽位映射** | 本品牌有哪些角色、谁有参考图、谁有非对称特征、同框场景如何分槽位 | 双角色槽位错配、形象互相污染 |
| 3 | **锁定场景背景图** | 每类场景映射一张 | 背景被模型自由发挥 |
| 4 | **场景 → 背景映射表** | 场景类型 ↔ 背景图路径 | 每次生成临时找图，易错配 |
| 5 | **主角色形象规格** | 非对称特征的准确表述（哪一侧、什么颜色、什么材质） | 锁定规则写不准 |
| 6 | **对手方角色形象规格** | 文字约束用；若有参考图另注路径 | 头部 / 发型 / 服装漂移 |
| 7 | **品类或材质锁定** | 画面内商品允许/禁止的材质范围、禁忌视觉元素 | 混入非目标品类商品 |

若用户只给了品牌名、没给参考图：**只做文字约束版**，并明确告知「无参考图锚定，非对称特征稳定性下降，建议生成后逐张核验」。

---

## Hard constraints（每次生成必守）

> 以下 6 段模板中，`{{...}}` 为占位符，从品牌档案填充。**未填充的占位符不得进入 prompt。**

### 1. 输入图锚定（REFERENCE ANCHORING）

**槽位分配规则**（ImageGen 最多 3 个槽位）——按「谁最需要锚定」排序：

| 场景 | image1 | image2 | image3 |
|------|--------|--------|--------|
| **单角色**（默认） | 主角色参考图 | 锁定背景图 | — |
| **双角色** | 有非对称特征的角色（通常员工） | 第二角色参考图 | 锁定背景图 |
| **双角色 · 一方无参考图** | 有参考图的角色 | 锁定背景图 | — |

**分配优先级**：

1. **有非对称特征的角色 → image1**。非对称特征最难约束，必须优先锚定。
2. **第二个有参考图的角色 → image2**。
3. **锁定背景 → 最后可用槽位**（image2 或 image3）。
4. **无参考图的角色 → 仅文字约束**，不占槽位。

**铁律**：

- ⚠️ **绝不用「对手方角色」作 image1**——会让有非对称特征的角色失去锚定，直接引发漂移（已实测复现）。
- ✅ **背景放 image3 锚定有效**（实测通过）：双角色场景 image1=有非对称特征者、image2=第二角色、image3=锁定背景，生成结果的**场景布局与配色**均与锁定背景一致。仍建议生成后核验一次。
- ✅ **相反约束可共存**（2026-09-10 实测通过）：一方「仅单侧佩戴某配饰」与另一方「完全禁戴该配饰」同时约束时未发生互相污染——前提是**各自段落写清约束对象 + 加防污染声明**。
- ⚠️ **两角色的约束方向可能相反**（一方仅单侧佩戴某配饰 vs 另一方完全禁戴）。必须**分别写清**，并在各自段落里加上「不得误加」的负面项，否则极易互相污染。这是双角色场景**最易出错处**。

### 2. 非对称锁定铁律（ASYMMETRY LOCK）— CRITICAL

**通用规律**：模型会把非对称特征对称化。只写 "ONLY her LEFT hand wears X" **不够**（实测仍生成对称）。

**🚫 禁止写法（2026-09-10 A/B 实测失败）**：不要用「与参考图同一只手」这类**抽象指代**代替具体方位描述。

```
❌ CRITICAL GLOVE RULE: ... a single black glove on the SAME single hand as in
   image1 (the reference image) ...
```
实测结果：**该单侧特征被对称化到双手**，完全复现最高频漂移模式。

**原因**：「视角侧位置描述」的作用不是"告诉模型哪只手"，而是**给出一个具体可定位的空间锚点**。锚点越具体，模型越难在两侧同时满足约束。去掉锚点后，三重负面约束失去落点，压制力大幅下降。

复制以下模板，把 `{{feature}}` 换成任意单侧特征（black glove / single long sleeve / one-side shoulder bag / asymmetric hair accessory），`{{LEFT|RIGHT}}` 按**基准图实际方位**填写：

```
CRITICAL ASYMMETRY RULE: the {{员工角色}} wears EXACTLY ONE {{feature}}
on {{her|his}} {{LEFT}} hand only (the hand on the viewer's {{RIGHT}} side of the body);
the other hand (on the viewer's {{LEFT}} side of the body) is completely
BARE with visible skin and is NOT holding anything.
NO {{feature}} on the other hand. NO {{feature}} on both sides.
NO second {{feature}} anywhere. NO symmetric pose.
```

**四个不可省略的要素**（缺一即失效）：

1. **视角侧参照系** — 必须写 `her LEFT hand (on the viewer's RIGHT side of the body)`。纯 left/right 会被模型镜像理解。
2. **EXACTLY ONE 计数词** — 明确"恰好一只 / 恰好一个"。
3. **三重负面约束** — `NO X on the other hand` + `NO X on both sides` + `NO second X anywhere`。只写一句无效。
4. **image1 锚定员工** — 无参考图锚定时，非对称约束的通过率显著下降。

> **职责分离**（2026-09-10 实测结论）：
> - **方位正确性**由 image1 参考图锚定保证——文字方位写反**不会**导致生成方位错误（实测：文字写「观众右侧」，生成「观众左侧」，与基准图一致）。
> - **单侧唯一性**由「EXACTLY ONE + 视角侧具体描述 + 三重负面约束」保证。
> - 尽管如此，**方位描述仍应与基准图实际对齐**，避免文字与图形冲突带来的潜在不稳定。填档案前先放大基准图确认是哪一侧，再填 `{{LEFT|RIGHT}}`。

> 仅当某只手需持产品时：那只手（仍仅限被锁定的一侧）戴手套持物，另一只手裸露、仅做讲解/指示手势。同时追加 `NO praying-hands pose`。

### 3. 对手方角色形象（参考图 + 文字双重约束）

**若该角色有参考图**（占 image2 或 image3）：文字约束仍需写全，并在 prompt 里声明 `EXACTLY as in image{{N}}`。

**若该角色无参考图**：仅文字约束，必须写到"只靠文字也能还原"的程度。

```
{{对手方角色形象规格 — 脸型、发型（含否定项）、上装、下装、鞋、包、配饰，
  每一项都写具体，并带上禁止变化项}}
```

务必附上**禁止发型变化**类负面约束：`NO bangs, NO ponytail, NO bun, NO hairclip`（按档案实际规格）。
发型与头部是最容易出现"看着像另一个人"的区域。只描述"要什么"不够，必须同时写"不要什么"。

> ⚠️ **双角色互斥声明**：若两角色的约束方向相反（一方戴配饰、另一方禁配饰；一方单手套、另一方无手套），**必须在各自段落内写互斥声明**，否则形象互相污染。例：
> - 员工段：`NO earrings, NO necklace, NO bag, NO waist bag`
> - 对手方段：`NO gloves, NO black glove, NO uniform, NO name badge`

### 4. 品类 / 材质锁定

```
ALL products displayed are {{允许品类}} ONLY — {{具体列举}}; plus
{{允许的辅助道具，如证书卡}}. NO {{禁止材质1}}, NO {{禁止材质2}},
NO {{禁止材质3}}.
```

模型默认会画混合形式，不主动限定材质。此段**每次必写**。

### 5. 通用负面约束（跨品牌通用，直接复用）

```
NOT a photograph, NO photorealistic rendering, NO English text on signage,
NO watermark, NO dark vignette, clean glass with thin outline and subtle
diagonal white highlights, NO photorealistic reflections, NO reflected people.
```

### 6. 风格（可覆盖）

```
Flat 2D comic book illustration, clean bright pastel manga aesthetic, bold black
ink outlines, cel-shaded flat colors, soft warm lighting, 16:9 (or 9:16) storyboard panel.
```

> 若用户指定其他画风（写实风、水彩风、国潮风等），替换本段，但**第 5 段负面约束不要删**——它是用来压水印和照片感的，与画风无关。

---

## Prompt 组装顺序（固定）

```
风格 → 背景强制复用 → 员工（含非对称铁律）→ 顾客（文字约束）→ 品类锁定 → 通用负面约束
```

**背景强制复用段**（配合 image2，防背景漂移）：

```
BACKGROUND MUST BE EXACTLY the store environment in image2, used as the literal
background plate. Reproduce image2's exact layout, furniture placement, and color
palette — do NOT invent a different store.
```

只写 "store environment" 会失败（实测背景被换成另一家店）。

---

## Generation workflow

1. **加载品牌档案**（Step 0），按槽位规则分配输入图：**主角色 → image1，第二角色 → image2，锁定背景 → 最后可用槽位**。
2. **组装 prompt**：按上方固定顺序，逐段填充占位符。
3. **调用 ImageGen**（`size` 1920x1080 或 1080x1920，`background: opaque`）。
4. **读图核验**：非对称特征是否仅锁定在一侧？顾客头部/发型对？背景是否锁定场景？商品材质是否合规？
5. **清除水印**：`python scripts/watermark.py <file.png>`（原地修改）。注意实际生成尺寸为 **1920x1072**（非 1080），脚本按实际尺寸计算。
6. **重命名为约定文件名**，保留 HTML 引用。
7. **若生成 HTML 讲解页**：编辑后跑 `python scripts/check_html_divs.py <file.html>` 校验 div 平衡，再 present。

> **运行环境**：
> - `watermark.py` 依赖 **Pillow + numpy** → 请使用**本机已安装这两个依赖的 Python 解释器**（Windows 上通常是单独安装的 Python，而非应用内置的运行时）。
> - `check_html_divs.py` 是纯标准库，任何 Python 解释器都能跑。
> - 若报 `ModuleNotFoundError`，说明当前解释器缺少依赖，换一个解释器或先安装依赖即可。

---

## 最小修改原则（收到「其他不变」时）

| 用户表述 | 正确做法 |
|----------|----------|
| 「只改 X，其他不变」 | 复用上一版**完全相同**的 prompt，仅替换目标项。**禁止重写 prompt** |
| 改动后仍报了构图变化 | 可把上一版成品作为 image1 传入保一致性；但需评估与员工锁定的冲突——**优先保员工非对称特征锁定** |
| 需要严格保构图 | 明确告知用户：当前模型不保证构图复现，需逐张核验，可能需人工挑选 |

**失败根因**：未固定构图时，模型会自由布局，人物左右位置可能整体翻转（实测出现过角色从画面一侧换到另一侧的情况）。若用户对构图有硬要求，建议改为局部修补（PIL 改色/改配饰）而非重新生成。

---

## Pre-generation checklist（调用前逐项勾选）

- [ ] 已加载目标品牌档案（`profiles/<brand>.md`），**7 组字段齐全**
- [ ] 槽位按「有非对称特征者 → image1」规则分配；image1 **非**对手方角色
- [ ] 锁定背景已分配到最后一个可用槽位
- [ ] **双角色同框时**：各段约束已显式限定对象（`applies to ... ONLY`）
- [ ] **双角色同框时**：已写入**双向**防污染声明（两句都要，缺一句仍可能反向污染）
- [ ] prompt 含非对称锁定铁律（**EXACTLY ONE + 视角侧位置描述 + 三重负面约束**，三要素都在）
- [ ] 该角色**无非对称特征**时，改用「对称强制 + 绝对禁止」表述，**不套用单侧模板**
- [ ] 手套段**未使用**「与参考图同一只手」类抽象表述（实测导致双手漂移，见 ERROR-LOG 错误 8）
- [ ] 方位描述已**放大基准图目视确认**，并与基准图实际对齐
- [ ] prompt 含对手方角色文字约束 + 禁止发型变化项
- [ ] prompt 含品类/材质锁定 + 负面约束
- [ ] prompt 含通用负面约束（NOT photograph / NO English / NO watermark）
- [ ] 已确认本次为**串行生成**（并行会撞时间戳文件名互相覆盖，见错误 9）
- [ ] 生成后读图核验 → 清除水印（复杂图案区注意接缝）→ 重命名
- [ ] 改 HTML 后跑 `check_html_divs.py`
- [ ] 旧版按迭代归档到 `vN-raw/` / `vN-backup/`，不删

---

## 迭代归档约定

每轮旧版入对应版本文件夹，便于回溯、不删：
`vN-raw/`（原始生成）· `vN-backup/`（修改前备份）· `vN-drift/`（已知有漂移问题的版本）。

版本名尽量带上问题标签（如 `v1-<问题名>`），回溯时能一眼看出该版为什么被淘汰。

---

## 如何把一次失败提炼为防错规则（元方法）

本技能的方法论来自一次迭代，后续遇到新失败点按此流程沉淀，**规则库能自己长大**：

1. **定位现象** — 具体到什么位置错了（哪张、哪个人物、哪个部位），不要写"效果不好"。
2. **归因根因** — 区分「约束写得不够明确」与「模型能力边界」。前者加约束可解，后者要换策略（如改用局部修补）。
3. **记录失败尝试** — 写清楚"试过 X 但没用"，避免下次重复试错。这是最有价值的一栏。
4. **给出有效修复** — 标注验证通过的版本号，让规则可信。
5. **写成可直接复制的模板** — 把修复方案固化成 prompt 片段，不要只写"要写清楚左右手"。
6. **进 checklist** — 只有进了生成前清单的规则才会被真正执行。

---

## Resources

- `GETTING-STARTED.md` — **初次使用指引**（面向使用者）：零素材跑通第一张图、建立品牌档案、常见问题。首次使用者遇到困难时指引其阅读。
- `references/ERROR-LOG.md` — 通用化错误记录与防错手册（10 类错误的根因 / 失败尝试 / 有效修复 / 防错规则 + 提炼方法）。**每次生成前建议先读。**
- `profiles/_TEMPLATE.md` — 品牌档案空白模板（含 7 组字段填写说明与范例格式）。
- `profiles/<brand>.md` — 按模板建立的目标品牌档案。**本技能不预置任何具体品牌的档案**，以保持完全通用。
- `scripts/watermark.py` — 清除 ImageGen 右下角水印（PIL 同色调块修补 + 边缘羽化，v2）。
- `scripts/check_html_divs.py` — 校验 HTML `<div>` 平衡，防结构破裂。
