---
name: writing-style-profiler
description: 从你自己的文字样本（聊天记录、笔记、文章、发给 AI 的提示词）中提取「写作风格 DNA」，训练 AI 模仿你的声音。采用多轮深挖工作流：跨场景收集样本 → 追问隐藏习惯 → 输出结构化多维画像 + 模仿示例。样本不足或材料不对时自动补位并标注置信度，不轻易失败。画像的终极检验：交给任何 AI 都能写出被你认出「像我」的文字。适用：写作润色、风格统一、克隆人画像、AI 协作前的自我认知、训练分身/客服语气。触发词：「画出写作风格DNA」「训练AI模仿我的表达」「克隆人画像」「提取我的表达DNA」「让AI用我的语气写」。
agent_created: true
---

# Writing Style Profiler

## Purpose
Turn a user's own writing samples into a reusable, structured "writing-style DNA" profile that any AI can use to mimic their voice. The profile's ultimate test: hand it to any AI, and that AI produces text the user recognizes as their own.

## When to use
**直接触发（命中即走全流程）：**
- 用户要求分析 / 画像 / 克隆自己的写作风格
- 用户想让 AI「写像我」「用我的语气」「sound like me」
- 隐藏任务式提示：「画出你的写作风格DNA」「训练AI模仿我的表达」「克隆人画像」「提取我的表达DNA」
- 用户投喂 RIA 便签、聊天记录、文章、朋友圈草稿，要求提取风格

**需判断再触发（避免误用，见「复杂场景用法速查」）：**
- 「让 AI 以后写周报像我写的」→ 先用本 skill 出画像（模式 C），再把画像当后续写作的上下文
- 「训练客服/分身用我的语气」→ 出画像 + 隐蔽特征清单，喂给那个 AI
- 「帮团队统一话术/模板」→ 出画像 → 提取可迁移句式 → 生成模板
- **不该用本 skill**：需求是「把这段改通顺 / 翻译 / 总结」——那是模式 B 的润色，不是画像。判断口诀：**需求落脚在「让 AI 产出更像我的文字」或「搞清我到底怎么写」，就用它；否则用润色。**

## Workflow

### Step 0 — 样本自检与自动补位（可靠性保障）
正式分析前，先对用户给的样本做自检。**本 skill 不轻易失败**：样本不足或材料不对时，按规则自动补位，而不是卡住或空转。

**自检三规则**
1. **数量**：少于 3 段 / 只有 1 种语境 → 进「补位模式」，不报错。
2. **归属**：文本疑似 AI 代写（无个人口语痕迹、结构过工整、无括号 / 破折号 / 方言自注）→ 主动提示「这段更像 AI 生成稿，不计入你的 DNA」，请其补一段真实手写。
3. **长度**：单段 < 50 字难以分析 → 先出「迷你画像」并标「置信度：低」，列出还缺哪类样本。

**补位动作（按场景自动选一种）**
- **补位A（缺语境）**：用 1–2 个具体问题重建缺失语境。例：只给了公众号文，就问「发这条前你在微信里怎么跟人聊这事？贴一段」。
- **补位B（只有 1 段）**：降野心，先跑「单样本速写」给初步特征，明示「这只是基于 1 段的推测，建议再投 2–3 段」。
- **补位C（材料明显不对）**：直接说明本 skill 不适用此类输入，给替代建议（如「你要的是翻译 / 润色，用模式 B 而非画像」）。

**置信度评级（必须写进最终画像顶部）**
每版画像标明：🔴 低 / 🟡 中 / 🟢 高，并附「当前缺哪类样本、补完可升到哪级」。用户据此知道画像能信到什么程度，而不是拿到一份看似完整实则单薄的稿子。

### Step 1 — Collect samples across 5 contexts
Request real, unedited user text from as many of these as possible (minimum 3, ideal 5):
1. Casual / argumentative chat (most raw voice)
2. Structured reflection (notes, RIA 便签, journals)
3. Formal design / doc writing
4. Task-style prompts to AI (background-then-instruction)
5. Real-time replies under questioning (closest to daily voice)

Do NOT treat AI-ghostwritten published articles as the user's DNA — they reflect tone the user *approved*, not the user's own phrasing. Note this distinction in the profile.

### Step 2 — Multi-round digging
For each sample, read closely and surface observations on: word preference, sentence rhythm, opening angle, argument style, emotional tone, punctuation. After each sample, ask 1–2 confirming/deepening questions. Loop until the user stops adding samples or the hidden-feature list stabilizes.
- 若某条隐蔽特征与样本矛盾，主动回问复核，不硬下结论。
- 若用户连续两轮未新增样本，主动给「当前置信度 + 还差什么」小结，让用户决定是否收口。

### Step 3 — Output the structured profile
Write a markdown profile with these sections:
- **置信度评级** (🔴/🟡/🟢 + 缺哪类样本，补完升到哪级) — 置顶
- Sample sources (table: context → style)
- 用词特征 (high-freq / banned / preferred word classes)
- 句式节奏 (long-short ratio, parenthesis / 破折号 habits, 分号 stacking)
- 切入角度 (how they open, never drop conclusions from nowhere)
- 论证方式 (per-context table)
- 情绪调性 (calm / sharp / humorous / restrained)
- 隐蔽特征 (the core — 8–12 hidden habits other AIs must replicate)
- 跨态 DNA (one-sentence summary for any AI to reproduce the voice)
- 模仿示例 (random topic, written in the user's style)

Reference `references/example-profile.md` for a complete worked example derived from a real session.

### Step 4 — Mimicry example + user reflection
Write one short piece on a random topic in the user's style. Ask the user: which hidden features surprised them, does the DNA hold, does the example "sound like me / like me but not me". Record their reflection into the profile's final section. The "像我又不是我" fuzzy feeling is the success signal.

## 复杂场景用法速查（适用性增强）
用户常不知「这种需求算不算本 skill 的活」。以下对照直接给可复制的触发语：

| 你想做的事 | 该说（直接复制） | 本 skill 怎么接 |
|---|---|---|
| 让 AI 以后写周报像我写的 | 「分析我的写作风格，之后帮我写的周报都用这个声纹」 | 先出画像（模式 C），再把画像作为后续写作的系统上下文 |
| 训练客服 / 分身用我的语气 | 「提取我的表达 DNA，我要让 AI 客服模仿」 | 出画像 + 隐蔽特征清单，直接喂给那个 AI |
| 统一多个平台的文风 | 「我公众号 / 朋友圈 / 笔记腔调不一样，帮我找出统一的那条线」 | 跨语境样本 → 找跨态 DNA → 给出「最小公约数」 |
| 投稿前自检「像不像我」 | 「用我的风格写一段 XX，我看看像不像」 | 走 Step 4 模仿示例，让用户判「像我又不是我」 |
| 帮团队统一话术 | 「我们组要一套对外邮件模板，基于我的风格」 | 出画像 → 提取可迁移句式 / 切入 → 生成模板 |
| 不懂技术也能用 | 「在 WorkBuddy 里说『安装写作风格 DNA 画像师』这个 skill」 | 触发即走流程，无需懂命令行 |

**判断口诀**：需求落脚在「让 AI 产出更像我的文字」或「搞清我到底怎么写」→ 用它；需求是「改通顺 / 翻译 / 总结」→ 那是模式 B 润色，不是画像。

## Hidden-feature detection checklist
Watch for these commonly-missed habits:
- Parenthetical real-time asides (边写边注)
- 破折号 sentence-extension density
- 分号 information-stacking in replies
- Terms wrapped in quotes for meta-distance ("做" "设计")
- High-frequency negative-constraint sentences (不 X / 绝不 X)
- Timestamp / number obsession on key actions
- Dialect / colloquial bursts inside formal text
- Role-assignment habit when prompting AI ("你是三级拆书家")
- Real-experience anchoring (AI may assist, never fabricate the user's truth)

## 常见问题 FAQ
- **Q：我只有一段文字，能分析吗？** 能，但标「置信度：低」。建议再投 2–3 段不同语境的，升到中 / 高级再正式用。
- **Q：AI 代写的文章能当样本吗？** 不能计入 DNA（那是你认可的调性，不是你的措辞）。本 skill 会区分标注，不混入。
- **Q：画像不准 / 模仿不像怎么办？** 回到 Step 2 多投一类样本，或指出哪条特征错，我会修正并重训；画像是可迭代的活文档。
- **Q：只有方言 / 口语、没有正式文，行吗？** 行，但画像偏「日常声纹」，缺正式场景特征——补一段工作文档即可补全。
- **Q：风格会变，画像是一次性的吗？** 不是。你反馈「这段不像我」即在重训；建议每季度或重大写作习惯变化后重跑一次。
- **Q：样本会泄露吗？** 样本只在本次会话处理，不联网、不留存外部服务；敏感内容建议脱敏后投喂。

## Pitfalls
- Do not count AI-ghostwritten published text as user DNA
- Do not flatter — dig for漏洞 like a 杠精 auditor
- Keep the profile a living document; user may say "this may iterate"
- Final reflection must be ≥100 words for the hidden-task submission format
- 样本不足时严禁硬出「高级画像」——必须走 Step 0 补位并标低置信度

## Resources
- `references/example-profile.md` — full worked profile from a real user session (5 sample contexts, 12 hidden features, mimicry example, user reflection). Use as the output template and quality bar.

## 延伸：拿到画像后，如何用 AI 协作（三种互动模式与适用边界）

本 skill 产出风格画像后，用户常接着要"用 AI 把事办成"。画像解决"像不像"，"怎么协作"是另一回事。以下三类互动模式来自真实会话，可与画像配合——知道了自己的声音，更要知道该让 AI 扮演什么角色。

### 三种互动模式
- **模式A · 对抗式压力测试（杠精审计员）**：用户出方案 → AI 连发致命追问 → 用户实时补洞 → 直到"无死角"。价值：逼出盲区。触发语："你当杠精，连问 3 轮"。
- **模式B · 共创式迭代打磨**：用户给原料 → AI 出初稿 → 用户评"不足" → AI 改 → 再评再改。价值：快速逼近好版本。
- **模式C · 反向画像 / 自我认知**：用户投喂样本 → AI 多轮深挖 → 出画像 → 用户反馈。价值：把隐性习惯变显性（即本 skill 本身）。

### 场景映射
| 场景 | 模式 | 能做到 | 做不到 |
| 时间管理 | A | 模糊意愿 → 无死角方案（触发器/物理墙/兜底） | 替你执行，落地归你 |
| 项目管理 | A+B | 排期风险预演、混乱需求 → SOP/看板 | 跨团队政治、真实资源协调 |
| 软考/考试 | B+C | 教材 → 你风格笔记、拆书内化、记忆锚点 | 替你考、判断当年考点（知识有截止） |
| 写作 | A+B+C | 挑逻辑洞、转化打磨、统一风格 | 替你"真实依托"（真事 AI 没有，编即幻觉） |

### 六条适用边界（务必主动告知用户）
1. AI 无真实体验，A1 类个人经验只能用户自己喂
2. AI 不执行物理动作，所有"落地"环节归用户
3. AI 默认顺用户，对抗感须用户主动触发，否则变高级应声虫
4. "无死角" = 逻辑自洽 ≠ 现实可行（真实世界还有"就是不想动"这种逻辑外的事）
5. 时效领域（考试/法规/技术栈）AI 给的须用户先验真再信
6. 每轮消耗用户注意力，非免费午餐——用户投入的脑力才是真成本

### 决策框架
- 方案有盲区风险 → 开模式 A，明确"你当杠精"
- 内容要成型 / 要转化 → 开模式 B，"先出初稿我再评不足"
- 想搞清自己 / 保持一致 → 开模式 C，投样本让它挖
- 涉及真实事件 / 价值判断 / 执行 → AI 只当助手，用户掌舵

一句话收口：**AI 是杠杆，不是替身。它放大你想清楚的部分，但"想清楚"和"做下去"这两步永远是你自己的。**

---

## 更新日志
- v1.3（本次）：针对 TRACE 评测 R(3.9)/A(4.3) 短板强化——①新增 Step 0 样本自检与自动补位（数量/归属/长度三规则 + 三选一补位 + 强制置信度评级），治「材料少/不对时无补位」；②扩展 When to use 触发判断 + 新增「复杂场景用法速查」表（6 类可复制触发语 + 判断口诀），治「复杂场景描述不具体」；③Step 3 输出强制含置信度评级；④新增 FAQ 六问，顺带补 C 的「常见问答少」。description 同步扩充触发词与适用边界。
- v1.2：新增「AI 协作三种互动模式与适用边界」延伸章节；description 改为中文市场展示版。
- v1.1：首版发布。
