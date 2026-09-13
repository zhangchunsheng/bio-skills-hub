# 长文配图 SKU · v1.0 核心

> **v1.0 核心 SKU**——给公众号/知乎/微信文章每篇配 1-30+ 张插图。
> **复用文哥 v6 主 IP + 极简手绘风**，完全解锁内容范围。
>
> **为什么不叫"长文配图 SKU"就叫"长文配图"？** 因为本 skill **只有两个 SKU**：长文配图 + PPT 演讲页（IP2）。
> 9:16 竖图漫画四格已拆分到 `文哥漫画-贱萌` skill。

---

## 1. 长文配图 vs 漫画四格 · 对比

| 维度 | 漫画四格（`文哥漫画-贱萌`） | **长文配图（`文哥漫画-手绘` v1.0）** |
|---|---|---|
| **画幅** | 9:16 竖图 | 16:9 横图 / 21:9 超宽（卷首） |
| **节奏** | 8-30 集连载 | 1-30+ 张单图（按内容弹性） |
| **风格** | 贱萌 Q 版（B+ 套 6 色） | **极简手绘（IP1 三色）** |
| **主 IP** | 文哥 chibi 化 | **文哥 v6（主 IP 锁）** |
| **文字量** | 0-1 块 primary_block | 0 文字块（仅图内标注） |
| **目的** | 微信/小红书连载 | **公众号/知乎/微信文章内嵌** |
| **单图时长** | 30-60s | 30-60s |
| **总产出** | 1 篇 8-30 集 = 2-4 小时 | 1 篇 1-30+ 张配图 = 5-60 分钟 |

---

## 2. 长文配图 5 步流程

```
[Step 1] 拿文章（用户上传 / URL / 已有文件）
   ↓
[Step 2] 读文章 + 列主题候选（每篇 3-5 个核心概念候选）
   ↓
[Step 3] 调性适配评估（5 维评分 + tone_match 字段）
   ↓
[Step 4] 写 shot list（按弹性图数 · 14 字段全填）
   ↓
[Step 5] 用户审核 shot list
   ↓
[Step 6] 调 matrix 出图（每张 ~30s） + QA + 交付
```

**总耗时**：5 分钟读 + 5 分钟 shot list + 1 分钟审核 + 5 分钟出图 = **15-20 分钟完成一篇文章配图**。

---

## 3. 文哥 v6 主 IP · 长文配图版

### 3.1 视觉 DNA 锁（IP1 极简手绘）

| 项 | 规定 |
|---|---|
| **底色** | 纯白 #FFFFFF |
| **主体线稿** | 极简手绘黑线（slightly wobbly but clean） |
| **留白** | 主体占画面 40-60% |
| **主色** | 黑 #000000（主体线 + 文字） |
| **辅色** | 橙 #FF7A45（流程/路径/箭头）+ 红 #D9304F（关键短语/警示）+ 蓝 #4A90E2（补充说明） |
| **字体** | 手写体中文（楷体/思源宋体），禁艺术字 |
| **禁项** | 3D / 商业 vector / 模板 PPT / 儿童 Q 版 / 萌系表情包 / 写实摄影 / 复杂 HUD 背景 |

### 3.2 文哥 v6 必带锚点（5 项）

1. **黑短发**（略刺猬头）
2. **方框眼镜**（黑/深色细框，**必带**）
3. **干净无胡**（无小胡子/山羊胡/络腮胡/胡茬）
4. **白长袖上衣**（基础，可换衬衫/T 恤）
5. **成人比例**（不幼态）

### 3.3 文哥动作 6 选 1

| 动作 | 适用场景 | 图示意 |
|---|---|---|
| **思考**（手托下巴） | 概念引入 / 反思 | 概念图 |
| **讲解**（手指向某物） | 知识传递 | 知识图 / 流程图 |
| **记录**（手拿笔记） | 步骤拆解 | 工作流图 |
| **举手**（手举起） | 提问互动 | 概念卡 |
| **微笑**（抱臂/不抱臂） | 收尾 / 金句 | 收尾图 |
| **看白板**（手撑白板） | 总结 / 类比 | 总结图 |

### 3.4 image-to-image 锁形

- **主锚图必传** `input_files`
- prompt 写 `MUST use the same character as in reference image, preserve identity anchors`
- 中文细描：`BLACK SHORT MESSY HAIR (slightly spiky) + BLACK SQUARE FRAME GLASSES (mandatory) + clean-shaven (NO facial hair) + white long-sleeve top`

---

## 4. 长文配图 6 种结构类型（决策指南）

| 类型 | 适用 | 隐喻 | 示例 |
|---|---|---|---|
| **卷首**（21:9） | 文章封面 | 物理隐喻 | S1 战壕复盘会 |
| **概念隐喻** | 抽象概念具象化 | USB-C / 战壕 / 洋葱 / 压机 | Test 1 USB-C / S3 根因洋葱 |
| **前后对比** | 旧 vs 新 / 错 vs 对 | 镜像 / 双格 | 战壕 vs 总部 / 乱线 vs USB-C |
| **方法分层** | 5 Whys / 4 件套 | 同心圆 / 洋葱剖面 | S3 5 Whys 洋葱 |
| **工作流** | 步骤/方法/流程 | 流水线 / 接力赛 | S4 三议题流程 |
| **角色状态** | 3 个错误/3 个价值 | 3 个角色各演一种 | S2 三大错误 |

**v1.0 规则**：每篇文章图数弹性 1-30+，**类型多样化**（不要 6 张都是概念隐喻），按文章结构选。

---

## 5. 出图 Prompt 模板（v1.0 长文配图版）

> 来自 ip-diagram-creator 内容图解通用 prompt，**适配文哥 v6 极简手绘**。

```text
Generate one standalone {aspect_ratio} Chinese explanatory diagram
using the confirmed creator persona (Wenge v6).

Character reference assets for this generation:
- Primary reference: assets/main_anchor.png

Confirmed creator persona:
- BLACK SHORT MESSY HAIR (slightly spiky on top)
- BLACK SQUARE FRAME GLASSES (mandatory, core identity anchor)
- Clean-shaven face (NO facial hair at all)
- White long-sleeve top
- Adult creator proportions, not chibi
- Confident slight smile

Content brief:
- Core idea: {核心观点}
- Main title: {顶部钩子句}
- Required text: {必保留词}

Structure type:
{workflow / 概念隐喻 / 前后对比 / 角色状态 / 方法分层 / 路线地图}

Main visual metaphor:
{主画面隐喻}

Wenge action:
{动作}

Supporting roles:
{按需角色 0-2 个 / 火柴人 1-3 个}

Visual DNA:
Pure white background. Beautiful minimalist black hand-drawn line art.
Slightly wobbly but clean pen lines. Lots of clean empty space.
Sparse red/orange/blue handwritten Chinese annotations.
Refined creator IP plus clean absurd product-sketch feeling.
NO 3D, NO realistic photo, NO cute mascot, NO PPT look, NO complex background.

Color use:
- Black for main line art and text
- Orange #FF7A45 for main flow / path / arrows
- Red #D9304F for key warnings / problems / results
- Blue #4A90E2 for secondary notes / system state

Constraints:
- One image explains the selected core idea
- Keep text readable
- The Wenge persona must be doing the action, not standing as decoration
- Do not make it a formal PPT slide or dense corporate infographic
- Do not write the structure type on the image
- Chinese text must be short, clean, and readable
- NO watermark, NO fake characters
```

---

## 6. 出图示例（v1.0 验证 · 2026-07-12 华为文章测试）

### Test 1 · MCP = USB-C 接口

- **结构类型**：概念隐喻 + 前后对比
- **图尺寸**：16:9
- **主 IP**：文哥 v6（举 USB-C 接口）
- **按需角色**：无
- **火柴人**：无
- **核心隐喻**：左侧乱线团（旧世界）vs 右侧 USB-C（新世界）
- **实测结果**：✅ 一次过，IP 全守，中文正确

### S1 · 战壕复盘会

- **结构类型**：概念隐喻
- **图尺寸**：21:9 超宽
- **主 IP**：文哥 v6（沙袋战壕里举白板）
- **按需角色**：无
- **火柴人**：2 个（趴战壕观察 + 递报告）
- **核心隐喻**：战壕 = 经营分析会
- **实测结果**：✅ A- 评级

### S3 · 根因洋葱

- **结构类型**：方法分层（5 Whys 洋葱）
- **图尺寸**：16:9
- **主 IP**：文哥 v6（手指洋葱）
- **按需角色**：无
- **火柴人**：1 个（举红 X 标错）
- **核心隐喻**：5 层洋葱剖面
- **实测结果**：✅ A+ 评级

### S4 · 三议题流程

- **结构类型**：工作流（3 步流程）
- **图尺寸**：16:9
- **主 IP**：文哥 v6（中央 orchestrator）
- **按需角色**：无
- **火柴人**：3 个（放大镜/手术刀/望远镜）
- **核心隐喻**：3 议题接力赛
- **实测结果**：✅ A- 评级

---

## 7. 长文配图素材复用

| 资产 | 路径 | 复用方式 |
|---|---|---|
| 文哥 v6 主锚图 | `assets/main_anchor.png` | **必传** image-to-image |
| 文哥 v6 规范说明图 | `assets/规范说明图.png` | 返修 / 纠偏 |
| 文哥 v6 动作扩展图 | `assets/动作扩展图.png` | 复杂动作 / 小比例场景 |
| 文哥 v6 角色档案 | `{SKILL_DIR}/ip-diagram-creator/characters/主理人.md` | prompt 必带字段摘要 |

---

## 8. 出图 SOP（标准操作流程）

```bash
# Step 1: 写 shot list（手工或脚本）
# Step 2: 准备 JSON 请求文件
{
  "requests": [
    {
      "prompt": "{从 shot list 14 字段拼}",
      "input_files": ["{PROJECT_ROOT}/文哥漫画-手绘/assets/main_anchor.png"],
      "aspect_ratio": "16:9",  // 或 21:9
      "resolution": "2K"
    }
  ]
}

# Step 3: 调 matrix
mavis mcp call <image-generation-tool> --file {json_path}

# Step 4: 下载到本地
# CDN URL 在 success_items[0].output_url

# Step 5: 复制到工作目录
cp {下载图} {工作目录}/{图编号}_{主题}.png

# Step 6: QA
# Read tool 打开图，肉眼 + 8 项 checklist（含 tone_match）
```

**单图耗时**：写 prompt 2 分钟 + matrix 调用 30s + 下载 10s + QA 1 分钟 = **~4 分钟/张**。

---

## 9. 长文配图 SKU 的"避坑指南"

| 坑 | 避免 |
|---|---|
| 把长文配图当 PPT 流程图 | 长文配图 = 单图一认知，不是流程图堆叠 |
| 把长文配图当商业插画 | 长文配图 = 极简手绘，禁商业 vector |
| 把文哥 v6 画成 chibi Q 版 | 长文配图 = 成人比例，不是 Q 版 |
| 把 IP1 三色和 B+ 套 6 色混用 | 同 ep 内选一套 |
| 忽略 image-to-image 锁形 | 必传主锚图 + 强 negative prompt |
| 一图塞 3 个概念 | 一图一认知 |
| 用英文标注（除非必要） | 中文为主，USB-C/AI 等保留英文 |
| **图数写死 13 张** | **用图片数量弹性指南**（1-30+ 张按内容定） |
| **跨风格混用** | **不与贱萌风混用**（同 ep 风格统一） |
