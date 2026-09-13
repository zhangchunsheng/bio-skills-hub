# 全能绘图大师workbuddy版 提示词优化参考（自包含）

> 本文件是「全能绘图大师workbuddy版」技能**内置**的提示词优化方法论，供调用本技能时（agent 层）在出图前把用户的口语化意图 / 文章 / 参考图要求优化成结构化提示词。覆盖本技能三模型：**gpt-image-2 / nano-banana-pro / nano-banana-2**。
> **自包含声明**：本文件内容自洽，可直接据其优化提示词，**不依赖任何外部 skill**。方法论蒸馏自社区验证范式（出处见文末），但运行时无需调用外部资源。
> 配套：优化后的提示词仍由 `scripts/rh_image_api.py` 原样透传给服务器——优化只发生在 agent 层，CLI 与 API 链路不变。

---

## 0. 何时优化 / 何时跳过

```
用户提示词到达
  │
  ├─ 已是精修结构化提示词（JSON count+labels / 完整身份锁+相机+负面词）
  │     → 跳过优化，直接 rh_image_api.py 出图
  │
  ├─ 草稿、口语化、只有模糊风格词（"真实光影""高质量""好看"）
  │     → 必须优化：按 §1 路由到对应模型章节，重构
  │
  ├─ 多元素/多分区构图（多视角、多面板、信息图、参考表、UI mockup）
  │     → 必须优化：gpt-image-2 走 JSON 结构化（§2）
  │
  └─ i2i 带参考图（人像写真/换装/换背景/产品换场景）
        → 必须优化：加身份锁 + 参考图锚定语法（§2 或 §3）
```

优化后用一段话向用户说明改了什么（缺什么补什么），再把**优化版**提示词传给 `rh_image_api.py`。

---

## 1. 按模型路由

| `--model` | 旗舰范式 | 参考图语法 | 一句话路由 |
|---|---|---|---|
| **nano-banana-pro** | **身份锁 + raw 美学 + 材质物理** | `Image 1`（脚标从 1 起） | 人像写真/换装/换背景/产品保真 → 锁脸锁货 + 详尽负面词 |
| **gpt-image-2**（**默认**） | **JSON 结构化**（`count`+`labels[]`） | `REFERENCE_0`（脚标从 0 起） | 多元素/有布局/有文字/参考表/信息图/电商主图 → 用 JSON |
| **nano-banana-2** | 同 pro（gemini 同族，**低价批量**用） | `Image 1` | 走 pro 同套方法论；要批量和速度时选它 |

> ⚠️ **别把复杂多区域布局（信息图/爆炸图/多面板）丢给 nano-banana**——文字渲染与结构服从度弱，路由到 **gpt-image-2** 更合适。
> ⚠️ **人像写真别丢给 gpt-image-2**——它不是纯写实摄影模型，脸易飘，路由到 **nano-banana-pro**。

---

## 2. gpt-image-2 优化章

### 2.1 旗舰范式：JSON 结构化（最具区分度）

凡是要**多元素、有布局、有计数**的构图（爆炸图、信息图、角色表、九宫格、UI mockup、产品参考表、因果链图），一律用 JSON schema 写。gpt-image-2 对结构化数据服从度极高，JSON 能精确控制每个区域放什么、放几个、文字写啥——**这是自然语言做不到的**。

通用骨架：

```json
{
  "type": "{类型，如 product reference sheet / exploded view poster / 2x2 grid / illustrated map}",
  "subject": "{主体}",
  "style": "{技法 + 光照 + 材质，如 clean high-tech 3D render, studio lighting}",
  "background": "{背景}",
  "reference": "REFERENCE_0 = {参考图用途，如 用户产品图，结构/材质基准}",
  "identity_lock": "exact_color / exact_texture / modification_permission: NONE（产品）；consistent facial identity across all panels, pixel-perfect（角色）",
  "layout": {
    "sections": [
      { "title": "{区块名}", "count": 4, "labels": ["标签1","标签2","标签3","标签4"], "descriptions": ["可选：每个的视觉描述"] }
    ]
  },
  "camera": "50mm, f/8, ISO 100, 5500K, studio softbox, SHARP and in focus",
  "negative_prompt": ["invented features not in reference","scene mixing","altered logo or text","blurry","cluttered"]
}
```

**关键技巧**：
- **`count` 驱动数量**：写 `"count": 8` 就画 8 个，不写模型自由发挥。
- **`labels[]` 驱动文案**：标签/标题逐字列进数组，模型照搬（文字渲染才准）。
- **数组长度与 count 一致**（或不写 count 让数组长度说话），否则模型困惑。
- **网格类**用 `"layout": {"grid": "3x3", "panels": [{"position":"top-left","label":"..."}, ...]}`。

### 2.2 参考图：`REFERENCE_0` 图生图

gpt-image-2 用 `REFERENCE_0`（**脚标从 0 起**）锚定参考图，说清"保留什么 / 改什么"：

```
Using REFERENCE_0 as a structural base, preserve the exact product appearance, color and material. Transform only the background to {新场景}.
```

保姿势/结构换外观：
```
Using REFERENCE_0, transform the subject's appearance to {style} while preserving the exact pose, clothing structure, and proportions.
```

> 不写"用我传的图"这种自然语言——用 `REFERENCE_0` 脚标更稳。

### 2.3 身份锁（放第一句）

- **产品保真**（换场景不改货）：`exact_color / exact_texture / exact_stitching / modification_permission: NONE`
- **角色跨面板一致**（多视角/九宫格）：`consistent facial identity across all panels, pixel-perfect, no drift`
- 锁定语**放第一句**（模型权重靠前），别堆末尾。

### 2.4 相机布光（具体到机身镜头）

禁"真实光影""高质量"虚词。参考表/产品图用深景深全清晰：
```
50mm, f/8, ISO 100, 5500K, studio softbox + rim light, SHARP and in focus, NO ARTIFICIAL BOKEH
```
（要电影感虚化：`85mm, f/1.8, shallow depth of field, creamy bokeh`。更多预设见 §4.1）

### 2.5 负面词（防串扰）

gpt-image-2 参考表/信息图至少带：
```
inconsistent faces across panels, drift in face/outfit, scene mixing, extra or duplicate products,
invented features not in reference, altered logo or text, cluttered, illegible, overlapping labels,
wrong counts, blurry, extra fingers
```

### 2.6 反模式（必避）

- 🚫 **用自然语言描述复杂多区域布局**（"左边放三个标签右边放五个下面放一段话"）→ 错位、漏字。**改用 JSON**。
- 🚫 让模型"自己想标语/文案"→ 文字渲染强但内容胡编。**逐字写明**。
- 🚫 不指定 aspect ratio → 默认比例可能不合用（用 `--aspect` 指定）。
- 🚫 把多分区糊成一条自然语言长 prompt → 一图同渲必乱。**每区 count+labels**。

### 2.7 gpt-image-2 示例：产品一致性参考表

弱草稿：`画个护肤品的产品图，多角度，带品牌感觉`
优化版：
```json
{
  "type": "product visual consistency reference sheet",
  "style": "photorealistic commercial studio, controlled softbox + rim light",
  "reference": "REFERENCE_0 = 用户产品图（结构与材质基准）",
  "identity_lock": "exact_color / exact_texture / modification_permission: NONE",
  "layout": { "sections": [
    { "title": "产品设定区", "count": 4, "labels": ["正面","侧面","45°","细节特写"], "descriptions": ["忠于参考图真实外观与材质，不得添加参考图没有的部件"] },
    { "title": "品牌调性区", "count": 1, "labels": ["mood board"], "descriptions": ["主色/光影/材质/氛围/字体调性"] }
  ]},
  "camera": "50mm, f/8, ISO 100, 5500K, studio softbox + rim light, SHARP and in focus",
  "negative_prompt": ["invented features not in reference","extra or duplicate products","scene mixing","altered logo or text","fake bokeh","cluttered","blurry"]
}
```

---

## 3. nano-banana-pro / nano-banana-2 优化章

> nano-banana-2（gemini-3.1-flash）与 pro（gemini-3-pro）同族，**同一套方法论**；nano-banana-2 更便宜更快，适合批量。两者**不支持**蒙版、透明底（那是 gpt-image-2 专属），传了会被拒。

### 3.1 旗舰范式：身份锁 + raw 美学 + 材质物理

凡用参考图（人物/产品），**第一句就写锁定**。

**最高级（写真/换装，脸必须一模一样）**：
```
Identity: Strictly preserve the exact face and unique features of the subject in Image 1.
Bio-Fidelity: high-fidelity skin physics: visible micro-pores, satin-finish glow, fine peach fuzz along the jawline.
identity_lock_strength: 0.995
preserve_original: true, reference_match: true, no_identity_drift: true, no_face_morphing: true, no_beautification: true
```

**中级（保持一致性，不需像素级）**：
```
maintaining their exact facial features and likeness, consistent facial identity across all panels, same face throughout
```

**产品保真（换场景不改货）**：
```
reference_logic: STRICT_PRODUCT_PRESERVATION
preservation_rules: [exact_color, exact_fabric_texture, exact_stitching, exact_hemline_and_fit]
modification_permission: NONE
```

### 3.2 参考图：`Image 1`（脚标从 1 起）

```
Use the attached image as the strict character reference.
Image 1 (Selfie) — preserve identity.
Image 2 (outfit) — preserve garment.
```

### 3.3 raw / 未修美学（nano-banana 招牌）

要"真实感、社交直出味"，显式关掉 AI 味：
```
NO ARTIFICIAL BOKEH. Everything is SHARP and in focus.
Raw unedited social-media dump aesthetic, visible digital grain, visible ISO noise, chroma noise.
Authentic selfie vibe, not polished or professional.
```
主动要"瑕疵"：`imperfect autofocus, uneven exposure, slight motion blur, mild wide-angle distortion`。
（极致低画质风：把"高质量"写进负面 → `NEGATIVE WARNINGS: high resolution, sharp focus, DSLR, beauty filter, HDR`）

### 3.4 材质物理描写（让写实度飙升）

别只写"穿黑色裙子"，写面料的物理行为：
```
A skin-tight jet-black jersey-knit dress. Extreme elastic tension, vacuum-tight fit, realistic micro-folds and tension lines.
Realistic skin-to-surface compression (thigh squish) visible where legs meet the surface.
```

### 3.5 相机布光（机身级，nano-banana 服从度最高）

```
Camera: iPhone 17 Pro rear camera (no portrait/bokeh mode)
Focal length: 26mm (广角自拍) / 85mm (人像虚化)
Aperture: f/1.8
ISO: 100
Shutter: 1/200s
White balance: 5200K
EV: -0.3
Focus: sharp on eyes / torso in mirror
```

### 3.6 负面词（nano-banana 很吃负面，写实人像 ≥8-10 条）

```
cartoon, anime, illustration, 3d render, CGI look, plastic skin, airbrushed, beauty filter,
over-smoothed skin, poreless, doll face, perfect symmetry, unnatural proportions, HDR,
overprocessed, distorted face, bad anatomy, extra fingers, nsfw
```

### 3.7 反模式（必避）

- 🚫 写"超高清 8K 美女"却不给身份锁 → 脸会飘。**先写锁定语**。
- 🚫 滥用"bokeh / 浅景深 / 美颜" → 毁 raw 味。要 raw 就 `NO ARTIFICIAL BOKEH`。
- 🚫 摄影参数只写"专业摄影" → 质感不可控。**写到机身/焦段/光圈级**。
- 🚫 负面词太短 → nano-banana 很吃负面，写实人像至少 8-10 条。
- 🚫 复杂多元素布局丢给 nano-banana → 路由到 **gpt-image-2**。

### 3.8 nano-banana-pro 示例：身份锁定镜面自拍

弱草稿：`把我这张自拍变得真实点，穿黑裙子，浴室镜子前`
优化版：
```
Identity: Strictly preserve the exact face of the woman in Image 1 (Selfie). identity_lock_strength: 0.995, no_identity_drift: true, no_beautification: true.
Bio-Fidelity: TrueLens skin physics, visible micro-pores, satin-finish glow, fine peach fuzz along jawline.
Clothing: skin-tight jet-black jersey-knit dress; extreme elastic tension, vacuum-tight fit, realistic micro-folds and tension lines.
NO ARTIFICIAL BOKEH. Everything SHARP and in focus. Raw unedited social-media dump aesthetic, visible ISO noise.
Mirror: faint water spots, dust, minor smudges catching light.
Camera: iPhone 17 Pro rear camera, 26mm, f/1.8, ISO 100, 1/200s, 5200K, EV -0.3, focus on torso in mirror.
NEGATIVE: cartoon, anime, plastic skin, airbrushed, beauty filter, over-smoothed, poreless, doll face, HDR, overprocessed, distorted face, bad anatomy, extra fingers.
```

---

## 4. 通用速查

### 4.1 相机 / 焦段 / 光照预设

| 想要的效果 | 写法 |
|---|---|
| 手机自拍味（广角微变形） | iPhone 17 Pro, 0.5x wide-angle (24mm), handheld |
| 手机日常味（自然深景深） | iPhone rear camera, 26mm, no portrait/bokeh mode |
| 人像虚化 | 85mm, f/1.8, shallow depth of field, creamy bokeh |
| 环境交代 | 35mm, wider view, environmental storytelling |
| 压缩感 | 200mm telephoto, compressed perspective |
| 微距 | macro lens, extreme close-up, razor-sharp |
| 电影宽幕 | anamorphic lens, 16:9, lens flare |
| 工作室（产品/参考表） | studio softbox key + controlled fill + rim, f/8 全清晰 |
| 黄金时刻 | golden hour sunlight, warm long shadows |
| 蓝调时刻 | blue hour twilight, moody |
| 侧光雕刻 | chiaroscuro, hard side light, dramatic split |
| 轮廓光 | rim light / backlight separating from background |

曝光三角：`Aperture: f/1.8`(大光圈浅景深) / `f/8-f/11`(全清晰) · `ISO: 100`(净；要 raw 颗粒写 ISO 800+) · `Shutter: 1/200s`(慢门=运动模糊) · `WB: 5200K`(低 K 暖 / 高 K 冷) · `EV: -0.3`(欠曝浓郁)。

### 4.2 负面词库（按场景拼装）

**通用质量类（几乎都加 5-8 条）**：`low quality, blurry, distorted, deformed, bad anatomy, extra limbs, extra fingers, mutated, disfigured, artifact, watermark, jpeg artifacts, overexposed, oversaturated, flat lighting`

**写实人像（nano-banana 必加 8-10 条）**：`cartoon, anime, illustration, 3d render, CGI look, plastic skin, airbrushed, beauty filter, over-smoothed skin, poreless, doll face, perfect symmetry, unnatural proportions, HDR, overprocessed`

**商业/编辑摄影**：`cluttered composition, busy background, text errors, misspellings, warped text, distorted logos, fake bokeh, cheap plastic feel, cropped body, garment distortion`

**信息图 / 海报 / 多面板（gpt-image-2）**：`cluttered, illegible, overlapping labels, misaligned callouts, wrong counts, misspelled labels, inconsistent faces across panels, inconsistent character design, messy piling, information overload`

**拼装建议**：① 必加通用质量类 5-8 条；② 按场景加 4-6 条；③ 明确不想要的风格（写实人像加 `cartoon, anime`）；④ raw 反向用法见 §3.3。

### 4.3 三模型参考图语法对照

| 模型 | 图生图/变换 | 多图赋值 | 蒙版 | 透明底 |
|---|---|---|---|---|
| **gpt-image-2** | `Using REFERENCE_0, …`（脚标从 0） | `REFERENCE_0` 主 + 文字描述次图 | ✅ `--mask` | ✅ `--transparent` |
| **nano-banana-pro** | `Use the attached image as reference` / `Image 1`（脚标从 1） | `Image 1`/`Image 2`/`Image 3` | ❌ | ❌ |
| **nano-banana-2** | 同 pro | 同 pro | ❌ | ❌ |

> **i2i 通道说明**：i2i 由脚本自动处理图片上传与传图（本地图先经网关 `/app/upload` 上传拿 URL 再填入 `imageUrls`），不影响 `REFERENCE_0`/`Image 1` 的提示词写法；用户提示词按本表语法写即可。

---

## 5. 优化输出约定

优化完提示词后，向用户**简述改了什么**（一行：缺身份锁/缺相机参数/改为 JSON/补负面词 等），然后调用：
```bash
python rh_image_api.py t2i "<优化后的提示词>" --model <模型> --resolution 2K --aspect <比例>
# 或 i2i（带参考图）
python rh_image_api.py i2i "<优化后的提示词>" --images "<参考图路径>"
```
**铁律**：优化只在 agent 层进行；`rh_image_api.py` 永远原样透传，不引入 LLM 调用，守住"脚本原样透传"。

---

## 出处

本文件方法论蒸馏自社区验证范式，原始出处为 YouMind-OpenLab 三个 awesome-* 社区提示词仓库（~8300 条）沉淀的 `models/{gpt-image-2,nano-banana-pro}.md`、`patterns/{structured-json,identity-lock,camera-lighting,negative-prompts,reference-image}.md` 与 `examples/*-featured.md`。本文件已自洽，**运行时不依赖任何外部 skill 或仓库**。
