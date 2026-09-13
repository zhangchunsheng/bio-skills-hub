---
name: classic-western-mystery-all
title: classic-western-mystery · 全套聚合
description: classic-western-mystery-all：封闭环境连环杀人悬疑技法全套（style/genre/rhythm/structure）；情绪
  幽闭恐惧、猜疑博弈、绝望求生；样本 1 部。按需使用：适用「封闭环境连环杀人悬疑」向连载；不适合硬套时跳过 tropes 等强题材层，opening/hook/emotion/dialogue
  通用技法仍可用。不适合：依赖天才侦探现场破案的本格推理。装本包后先读错用告警、分层用法与 FAQ。
version: 0.1.0
priority: 50
enabled: true
family: classic-western-mystery
facets:
- style
- genre
- rhythm
- structure
replaces_facets:
- style
- genre
- rhythm
- structure
agents:
- writer
- planner
- editor
inject:
  slices:
  - id: contents
    file: references/pack-contents.md
    title: 本包内容
    facet: style
    priority: 10
    when:
      always: true
  - id: faq
    file: references/faq.md
    title: 常见问题与拒写闸门
    facet: genre
    priority: 15
    when:
      always: true
  - id: tropes
    file: references/tropes-dna.md
    title: 题材 DNA
    facet: genre
    priority: 60
    when:
      always: true
  - id: emotion
    file: references/emotion-curve.md
    title: 情绪曲线
    facet: rhythm
    priority: 80
    when:
      always: true
  - id: opening
    file: references/chapter-opening.md
    title: 开篇技法
    facet: structure
    priority: 90
    when:
      always: true
  - id: voice
    file: references/style-voice.md
    title: 叙事声口
    facet: style
    priority: 55
    when:
      always: true
  - id: dialogue
    file: references/dialogue.md
    title: 对话声口
    facet: dialogue
    priority: 70
    when:
      scene_types:
      - dialogue
  - id: hook
    file: references/hook-techniques.md
    title: 章末钩子
    facet: rhythm
    priority: 100
    when:
      always: true
source:
  tool: novel-skill-agent
  sample_count: 1
  compiled_at: '2026-08-06'
checks:
  hook_signals_file: hooks.yaml
---

# classic-western-mystery-all

本目录即 `classic-western-mystery-all`，说明仅覆盖本包。

## 一句话定位
**封闭环境连环杀人悬疑** 写作技法包（按需使用）（无侦探自证清白、童谣倒计时杀人、过往罪行清算）；主打情绪：幽闭恐惧、猜疑博弈、绝望求生、道德审判。样本部数：1。
适用：封闭岛屿/庄园/列车/雪山等物理隔绝场景的连环杀人谜题；不适合硬套：依赖天才侦探现场破案的本格推理。题材不匹配时跳过强题材层，通用技法可保留；完整边界与闸门见下文，勿在多处重复维护清单。

## ⚠ 错用告警（先读）

本包是 **「封闭环境连环杀人悬疑」技法指导配置包**，按需使用，不是万能写作模板。完整适合/不适合清单见 `references/tropes-dna.md`「本包边界」。

**适用题材（摘要 · 主类型「封闭环境连环杀人悬疑」）：**
- 封闭岛屿/庄园/列车/雪山等物理隔绝场景的连环杀人谜题
- 无专业侦探、全员嫌疑人的群像心理博弈
- 以童谣、塔罗牌、预言诗等公开剧本为杀人时间表的倒计时叙事
- 结局需通过事后文书/供词揭示全貌的‘完美犯罪’类推理

**立刻停用强题材层并换包 / 改方向（摘要）：**
- 依赖天才侦探现场破案的本格推理
- 开放城市背景下的连环案件侦破流程
- 以/科幻设定解释作案手法的异能悬疑
- 复述样书专名情节或原句的同人/改编创作

任务落在「不适合」时：跳过 tropes 等强题材切片；opening / hook / emotion / dialogue 等通用做法仍可按需保留。硬套强题材层常会腔调与冲突错位——这不是 Agent「坏了」，而是题材层不匹配。

## 按需使用（分层）

本包主类型是 **「封闭环境连环杀人悬疑」**，但不是「要么全用要么全弃」。
启用前先对照 `tropes-dna.md`；任务不完全匹配时，按层取舍：

**强题材层（错用或不匹配 → 跳过，勿硬套）：**
- tropes-dna（题材 DNA / trope_playbook）
- fit_for / unfit_for 中的题材专属槽位

**通用技法层（多数题材仍可按需用）：**
- emotion-curve（情绪拍与章长骨架）
- chapter-opening（开篇冲突配额与做法）
- hook-techniques / hooks.yaml（章末钩子类型）
- style-voice / dialogue（做法与验收骨架，勿硬套样书专属声口）

错用强题材层时，Agent 应明确说明「已跳过题材专属切片，仅保留通用做法/验收」；不要把主类型专名、世界观槽位偷渡进不匹配的正文。

## Agent 拒写闸门（写前必过）

每次启用本包写/改文前，Agent **必须先做边界核对**；不要等用户自己发现题材不对。

1. 用一句话概括用户任务的主类型与情绪目标。
2. 对照 `tropes-dna.md`「不适合」；若命中（例如：依赖天才侦探现场破案的本格推理；开放城市背景下的连环案件侦破流程；以/科幻设定解释作案手法的异能悬疑）：
   - **跳过**强题材层（tropes-dna / 题材专属槽位），明确回复：「当前任务与 `封闭环境连环杀人悬疑` 强题材层不匹配，原因：…；已跳过题材专属切片。」
   - **仍可按需**使用通用技法层（emotion-curve、chapter-opening、hook-techniques、style-voice/dialogue 的做法与验收）。
   - 若用户只要「该主类型完整包」且任务完全相反，则停用本包并建议换对应题材包。
3. 仅当任务落在「适合」内，才注入 tropes 等强题材切片。
4. 写中若发现用户中途改成明显不匹配体裁，再次触发本闸门：先撤强题材层，再问是否只保留通用技法。

## 推荐阅读顺序（与文件组织一致）

按编号读，避免先扎进细节再发现题材不对：

1. `references/tropes-dna.md` — 本包边界（先确认适不适合）
2. `references/faq.md` — 常见问题与拒写闸门
3. `references/emotion-curve.md` — 本章情绪拍与章长
4. `references/chapter-opening.md` — 开篇玩法
5. `references/style-voice.md` — 叙事声口
6. `references/dialogue.md` — 对话声口（对白场）
7. `references/hook-techniques.md` — 章末钩子
8. `references/pack-contents.md` — 全包摘要（可选）

## 调用示例（怎么触发本包）

### 安装（一次）
1. 把本目录 `classic-western-mystery-all` 放进 Agent 的 skills 路径（Cursor Skills / SkillHub / readerAgent `skills/` 均可）。
2. 确认能读到本包 `SKILL.md` 与 `references/`。

### 触发口令（短口令，任选其一）
- 「启用 `classic-western-mystery-all`，按边界写封闭环境连环杀人悬疑。」
- 「@`classic-western-mystery-all` 写第 N 回；先过闸门再开篇。」
- 「用 `classic-western-mystery-all`（封闭环境连环杀人悬疑 / 幽闭恐惧、猜疑博弈、绝望求生）：先核对 tropes-dna。」
- 「只用 `classic-western-mystery-all` 的 hook + opening（跳过题材 DNA）。」
- 「按 `classic-western-mystery-all` 的 style-voice / dialogue 改对白；只执行做法与验收。」

### 写一回的最小流程
1. **闸门**：核对题材 → 不匹配则跳过强题材层（或换包）。
2. **写前**：emotion-curve 定情绪拍；chapter-opening 定开篇冲突。
3. **写中**：style-voice 管叙述；dialogue 管对白（匹配时再加 tropes）。
4. **写末**：hook-techniques 选钩；对照「验收」自检；勿照搬示例声口。

### 自检口令
- 「对照本包 playbook：做法是否落地？避雷是否踩中？验收能否勾选？有无模仿样书句式节奏？有无误用强题材词？」

## 本包是什么
- 一次启用维度：style, genre, rhythm, structure
- 样本部数：1
- 技法配置 IR：仅存于分析项目 `projects/<name>/craft_profile.yaml`（本包不附带）
- playbook 质量：first_class=42，degraded=0，upgrade_ratio=0%
- 语域 register_mode：auto
- 分层：强题材（tropes）可跳过；通用（opening/hook/emotion/dialogue）按需保留

## 本包文件
- `SKILL.md`：入口、分层用法、拒写闸门、触发口令与 inject（本文件）
- `hooks.yaml`：章末钩子信号（不得为空）
- `references/`：边界（tropes-dna）+ FAQ + 各维 playbook

## 本包约束摘要
- 文风 POV：第三人称全知视角，频繁切换焦点人物（自由间接引语），单场景通常锁定 1-2 视角；硬禁用 1 条 / 弱建议类别 5 条
- 题材：封闭环境连环杀人悬疑；tropes 9 条
- 节奏：章长 2800–3800（stats）；情绪 平静好奇 → 震惊质疑 → 紧张搜索 → 恐惧蔓延 → 绝望对峙 → 释然揭秘
- 结构：开篇冲突前 15%
