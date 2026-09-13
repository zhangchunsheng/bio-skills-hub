# 配图规范（Illustration Guide）

使用 ImageGen 工具为公众号文章生成配图。每篇文章 4 张：1 封面 + 3 正文插图。

## 硬性规格

- 尺寸：1536×1024（横版，正文插图与封面同规格，封面发布时按 2.35:1 裁剪）
- 数量：封面 1 张 + 正文插图 3 张（分别放在「痛点章」「方法章」「结果/CTA章」之后）
- 风格统一：同一篇文章所有配图必须同一风格族（flat modern corporate tech illustration）+ 同一色系（紫-蓝-青为主，金色点缀）

## Prompt 黄金法则

1. **画面里绝不出现文字**：每个 prompt 结尾必须加 "no text, no words, no letters"——生图模型的文字必然乱码/错拼，所有文案交给正文承担
2. **主题具象化**：把抽象概念翻译成一个可视场景。例：「流量入口变化」→「左侧商人面对杂乱搜索链接（灰暗沮丧），右侧商人问 AI、AI 投出全息推荐卡（明亮带绿勾金星）」
3. **封面留暗区**：封面 prompt 要求 "empty dark space at top for headline"，方便叠加标题
4. **强调叙事对比**：用左右分屏 / 上升路径 / 明暗对比讲故事，不用静态罗列图标

## 四张图的定位

| 图 | 位置 | 视觉策略 |
|---|---|---|
| 封面 | 素材库封面 | 单一强主体 + 高饱和发光 + 冲击力优先，让人在信息流里停住 |
| 插图1 | 痛点章节后 | 直观呈现"变化/反差"，让读者一图看懂问题 |
| 插图2 | 方法章节后 | 步骤递进可视化（阶梯 / 流程 / 串联路径） |
| 插图3 | 结果/CTA章节前 | "赢 vs 输"的对比感，制造行动冲动 |

## 可复用 Prompt 模板

- 封面：`Eye-catching cover illustration, premium tech style with strong visual impact. [主体场景描述]. Vibrant saturated colors, dramatic cinematic lighting, empty dark space at top for headline, no text, no words, no letters.`
- 对比图：`Flat vector illustration, split-screen comparison. LEFT half in muted desaturated tones: [旧场景]. RIGHT half in vibrant glowing purple-blue tones: [新场景]. Strong visual contrast, no text, no words, no letters.`
- 步骤图：`Flat modern infographic illustration, [N] ascending platforms/steps from bottom-left to top-right: Step1 [场景], Step2 [场景], Step3 [场景]. Dotted path connects upward, tiny figure climbing. Purple-blue-cyan glow, no text, no words, no letters.`

## 质检与归档

- 生成后必须逐张 Read 检查：文字乱码、元素跳戏（如出现品牌字样）、主题偏移 → 不合格立即用调整后的 prompt 重生成
- 命名归档：`01-cover.png`、`02-xxx.png`、`03-xxx.png`、`04-cta.png`，存放在文章目录 `images/` 下
- 替换旧图时旧版备份到 `images/v1/`，不要直接删除
