---
name: novel-hit-writer
description: 零基础按流程写小说必出爆款。This skill should be used when the user wants to write a web novel (网文/番茄小说/起点/晋江风格) following a structured, quality-gated pipeline — from locking the "hit gene" via 6 questions, to planning (outline / character files / emotion curve / golden opening), to chapter-by-chapter drafting with hard standards, de-AI rewriting, 18-item quality check, and 5-chapter rhythm feedback. Trigger when the user mentions 写小说、爆款小说、番茄小说、网文创作、爽文、追妻火葬场、系统流、扮猪吃虎、黄金开篇、情绪曲线 or asks for a novel-writing workflow.
agent_created: true
---

# 零基础按流程写小说必出爆款

把"从创意到完本"的网文创作流程拆成三段，按步骤卡住质量。不是让 AI 随便写一章，而是用流程把最容易翻车的地方提前锁死：开局基因漂移、前后人设打架、节奏平淡、AI 味重、写完才发现方向错。

## 适用边界（先读）

- 平台无关：默认按番茄小说节奏（快钩子、高留存）设计，但可通过 `references/rules_chapter_standards.md` 的变量适配起点/晋江/抖音等。
- 不承诺必爆：技能提高流程稳定性，作品数据仍取决于题材判断、作者审阅、平台推荐与读者反馈（见结尾风险说明）。
- 作者负责判断：AI 是协作与提速，不是枪手。凡有人设、节奏、钩子判断处，必须交回用户确认。

## 触发条件

满足任一即触发：

1. 用户表达写小说/网文/爽文/言情/悬疑等创作意图。
2. 用户提供一段灵感、设定、角色或大纲，希望发展成完整小说。
3. 用户已有半成品小说，出现写崩、写散、断节奏、人设打架。
4. 用户明确要求"黄金开篇 / 情绪曲线 / 逐章检查 / 去 AI 味 / 质量自查"。

## 输入

- **必填**：创作灵感或题材方向（一句话也可，越清晰越好）。
- **可选**：已有设定（作品名、题材、角色、前文、大纲、情绪标签）——若有，先读取再补缺失，严禁另起炉灶。
- **可选**：目标平台、目标字数/章数、风格偏好。

## 输出（交付五件套）

1. **爆款基因表**：情绪标签、题材、主角设定、反差点、核心冲突、章节数。
2. **整本规划**：大纲 + 人物档案 + 情绪曲线 + 黄金开篇。
3. **章节正文**：每章 2200-2800 字，前 50 字合规，结尾钩子轮换。
4. **质量报告**：字数/开头/对话/钩子/金句/去 AI 味/18 项自查结果。
5. **节奏反馈**：每 5 章一次节奏报告与后续调整建议。

全部以 Markdown 文件落盘到用户工作目录（默认 `./novel/<作品名>/`），每份交付对应一个模板（见 `references/templates.md`）。

## 工作流（三段 + 检查 + 反馈）

> 全流程遵循"先确认、再生产"原则。每个阶段结束都需用户确认后再进入下一阶段，避免方向漂移。

### 阶段一：6 问锁定爆款基因

1. 调用 `prompt.md` 的【需求提取 prompt】解析用户输入，提取 6 个字段初值。
2. 用 `prompt.md` 的【确认话术 prompt】生成选择题/追问，引导用户补全或确认。
3. 字段不全或模糊时，只追问缺失项，不自行脑补关键设定。
4. 生成 **爆款基因表**（模板见 `references/templates.md` 的 `gene_table`），6 项必须一次填清。
5. 参考 `references/rules_six_questions.md` 校验：主情绪只能一个；反差必须成立；核心冲突可贯穿全本。

### 阶段二：规划（大纲 / 人物档案 / 情绪曲线 / 黄金开篇）

1. 读取 `references/rules_golden_opening.md`，选定开篇类型（冲突前置 / 悬念钩子 / 人设立体），并规避 5 类低效开头。
2. 生成 **整本大纲**：按 `references/rules_emotion_units.md` 的"压→小扬→爆"3 章循环排布；前 3 章高强度；每 10 章一大高潮；结尾段提密度。
3. 用 `scripts/emotion_curve.py` 生成并校验情绪曲线：输入总章数，输出每章情绪定位（压/扬/爆）与 10 章大高潮标记，校验循环是否断裂。
4. 生成 **人物档案**：主角+关键配角，含设定、反差、说话方式标签（供去 AI 味用）。
5. 生成 **黄金开篇**：前 50 字+前 200 字样本，明确落在合规区。

### 阶段三：逐章创作 + 检查 + 反馈

对每一章执行闭环：

1. **起草**：按规划写 2200-2800 字，落 `references/templates.md` 的 `chapter` 模板。
2. **硬标准自检**：运行 `scripts/validate_chapter.py`，检查字数、前 50 字、前 20% 即时冲突、对话占比、结尾钩子与轮换。
3. **去 AI 味**：按 `references/rules_deai.md` 改写——删过度修饰、减抽象陈述、用动作对话表情绪、角色说话方式差异化、情绪高潮加金句。
4. **18 项自查**：运行 `scripts/quality_check.py`，任 3 项以上不通过 → 退回润色，不硬交付。
5. **交付本章**：输出章节正文 + 质量报告（五件套第 3、4 项）。
6. **每 5 章反馈**：运行节奏复核（逻辑见 `references/rules_data_feedback.md`），产出节奏报告（五件套第 5 项）；若连续 3 章完读下降信号，回退大纲阶段调整后续。

## 资源索引

- `prompt.md`：需求提取逻辑、确认话术逻辑的**可复用 prompt 模板**（本 Skill 的核心引擎）。
- `references/rules_six_questions.md`：6 问详解与判定规则。
- `references/rules_golden_opening.md`：黄金开篇 3 类型 + 5 类低效开头黑名单。
- `references/rules_emotion_units.md`：3 章情绪单元循环规则。
- `references/rules_chapter_standards.md`：逐章硬标准（字数/开头/对话/钩子及平台变量）。
- `references/rules_deai.md`：去 AI 味改写规则。
- `references/rules_quality_checklist.md`：18 项质量自查清单（与脚本对应）。
- `references/rules_data_feedback.md`：每 5 章数据反馈规则。
- `references/templates.md`：4 类 Markdown 模板，含字段定义（gene_table / plan / chapter / feedback）。
- `references/examples.md`：3 个真实案例（打脸爽文 / 追妻火葬场 / 系统流）。
- `scripts/validate_chapter.py`：逐章硬标准检查（CLI，输出 JSON 报告）。
- `scripts/quality_check.py`：18 项质量自查（CLI，输出通过/不通过 + 是否退回）。
- `scripts/emotion_curve.py`：情绪曲线生成与 3 章循环校验（CLI）。

## 边界处理

- **信息不全**：只问缺失的关键 6 问项；非关键细节可给默认值并标注"建议"，不得替用户定主情绪。
- **人设打架**：凡检测到与已有设定冲突（如"怕水→游泳冠军"），立即冻结该章，提示用户裁决，不自动覆盖。
- **质量不达标**：validate 或 quality_check 不通过 → 退回润色并给出具体修改点，绝不"写完即交付"。
- **数据预警**：连续 3 章节奏下滑信号 → 暂停生产，回大纲阶段复盘，不硬写扩大损失。
- **平台差异**：非番茄场景，先询问目标平台，再调 `rules_chapter_standards.md` 的变量（如字数、钩子密度）。
- **合规红线**：禁止生成色情、血腥暴力、违法违规或侵犯他人著作权的内容；涉及真实人物需提示风险。
- **用户意图变更**：用户中途改题材/主情绪，视为新基因，回到阶段一重走，不半成品拼接。
