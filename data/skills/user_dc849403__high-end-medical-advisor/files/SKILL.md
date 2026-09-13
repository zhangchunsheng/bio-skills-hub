---
name: high-end-medical-advisor
description: 中国中高端医疗险沟通顾问。当输入客户的年龄、性别、家庭情况、对医疗险的看法、需求、异议问题等资料，需要分析中高端医疗险相对社保/惠民保/百万医疗险的优势、做 DRG 政策解读、逐条处理异议并给出投保建议时使用。会结合 ima-mcp 检索用户 IMA 资料库中的中高端医疗险资料，从医疗资源区别、条款优势、DRG 政策、保险公司服务四个维度论证，并输出纯文本结构化分析。
version: 1.0.0
display_name: 中高端医疗险沟通顾问
display_name_en: High-End Medical Insurance Advisor
description_zh: 面向保险代理人的中国中高端医疗险沟通顾问。输入客户年龄、性别、家庭情况、对医疗险的看法、需求与异议后，结合 IMA 资料库中的中高端医疗险资料，从医疗资源区别、条款优势、DRG 政策解读、保险公司服务四个维度论证中高端医疗险相对社保/惠民保/百万医疗险的优势，逐条处理客户异议并给出量身投保建议，输出纯文本结构化分析。
description_en: A communication advisor for China's high-end medical insurance, built for insurance agents. Given a client's age, gender, family situation, views on medical insurance, needs, and objections, it draws on the user's IMA knowledge base to demonstrate why high-end medical insurance beats social insurance, Huiminbao, and million medical plans across four dimensions—medical resources, clause benefits, DRG policy, and insurer services—answers objections point by point, and delivers tailored recommendations as structured plain-text analysis.
agent_created: true
---

# 中高端医疗险沟通顾问 (High-End Medical Insurance Advisor)

## Overview

本 skill 将 WorkBuddy 变成一名"中高端医疗险沟通专家"，面向保险代理人/顾问场景：输入客户资料后，结合 IMA 资料库中的中高端医疗险资料，从**医疗资源区别、条款优势、DRG 政策解读、保险公司服务**四个维度，论证中高端医疗险为什么比社保、惠民保、百万医疗险更适合该客户，逐条处理客户异议，并生成量身投保建议。

核心交付物为**纯文本结构化分析**（用于代理人直接用于沟通或二次加工），不生成文件。

## When to Use

- 用户提交客户资料（年龄/性别/家庭/对医疗险看法/需求/异议），要求分析中高端医疗险优势。
- 用户需要 DRG 政策对就医与医疗险影响的讲解话术。
- 用户需要针对具体客户异议（"太贵""有社保就够了""等老了再买"等）的回应脚本。
- 用户要对比中高端医疗险 vs 社保/惠民保/百万医疗险，并给出投保建议。
- 触发词示例："中高端医疗险怎么跟客户讲""客户说百万医疗就够了怎么回""DRG 后为什么还要买中高端""帮我分析这个客户的医疗险方案"。

## Workflow

### Step 1 — 接收并梳理客户资料
从用户输入中提取并结构化以下字段（缺失项标记"未知"，不要凭空编造）：
- 年龄、性别
- 家庭情况（婚育、子女、父母赡养、配偶）
- 职业/城市
- 既往病史/体况/已购保险
- 对医疗险的看法与已有认知（偏差点）
- 真实需求与恐惧
- 具体异议问题（逐条列出）
- 预算区间

### Step 2 — 检索 IMA 资料库（关键步骤）
调用 ima-mcp 检索用户 IMA 资料库中的中高端医疗险资料，用于核对与充实论据：
1. 用 `mcp__ima-mcp__get_knowledge_base_list` 查看有哪些知识库。
2. 用 `mcp__ima-mcp__search_knowledge` 或 `mcp__ima-mcp__search_knowledge_base` 检索如"中高端医疗险 产品 条款 直付 特需 保证续保 保费"等关键词，提取最新产品、保额、免赔、网络医院、续保条件、真实案例。
3. 若 IMA 无相关库/检索为空，则以本 skill 的 references 基线输出，并在结尾提示代理人补充最新产品资料。

### Step 3 — 四维优势论证
参考 `references/comparison_matrix.md` 与 `references/drg_policy.md`，紧扣客户关注点，从四维度论证：
1. **医疗资源区别**：机构覆盖（特需/国际/VIP/私立/全球）、好医生好床位好药的优先获取权。
2. **条款优势**：0 免赔可选、不限医保目录、直付网络、门诊可保、保证续保。
3. **DRG 政策解读**：控费导致普通部受限，中高端提供绕开路径（用大白话+切身场景）。
4. **保险公司服务**：绿通、二次诊疗、海外就医、护工等增值服务价值。

### Step 4 — 异议逐条回应
参考 `references/objection_handling.md` 的结构，对客户提出的每条异议按「客户心理 → 共情+转折+论证+收口」回应。
**关键：先查 `references/materials_index.md` 的「场景→素材映射」，用 Grep/Read 调取 `references/source/` 中对应的用户真实话术文件**（如"太贵"→`客户嫌中高端医疗险太贵怎么回.md`），优先引用用户一线沉淀的话术与案例，再结合本 skill 基线论证。
客户未提异议时，预判其最可能担心的 1–2 条并主动提示，同时预载对应素材。

### Step 5 — 生成量身建议
参考 `references/communication_logic.md` 的"量身建议生成逻辑"，按年龄/家庭/需求/预算给出：
- 推荐产品层级与机构范围（国内特需 / 大中华 / 全球）
- 免赔额与门诊责任建议（调节旋钮以适配预算）
- 保证续保要求
- 下一步动作（试算/出方案/锁资格/转介绍）

### Step 6 — 输出纯文本结构化分析
按 `references/communication_logic.md` 的"输出结构"组织成纯文本：

```
1. 客户画像小结
2. 核心结论（为什么中高端更适合该客户）
3. 四维优势论证（医疗资源 / 条款 / DRG / 服务）
4. 异议逐条回应
5. 量身建议（层级/机构/免赔/门诊/预算/续保）
6. 下一步动作
```

## Resources

### references/
- `comparison_matrix.md` — 社保/惠民保/百万医疗/中高端 四层定位、核心维度对比表、关键差异点与沟通要点。
- `drg_policy.md` — DRG/DIP 大白话解读、对医院与病人的实际影响、中高端如何绕开限制、讲解注意事项与误区澄清。
- `objection_handling.md` — 10 条常见异议的「客户心理→回应策略」逐条脚本（基线框架）。
- `communication_logic.md` — 沟通总原则、倾听清单、四维分析框架、量身建议生成逻辑、输出结构、IMA 联动说明。
- `materials_index.md` — **用户真实展业素材索引**：19 份文档/课件的抽取清单 + 「场景→素材」映射表，处理具体异议时按需调取。
- `source/` — 从用户提供的 19 份资料（话术 docx ×15、展业工具/讲座 pptx ×4）抽取出的纯文本素材，文件名即主题，可直接 Grep/Read。

### scripts/
- `extract_sources.py` — 将用户的 docx/pptx 源文件重新抽取为 `references/source/*.md` 的脚本（依赖 python-docx / python-pptx）。源文件路径见脚本顶部，新增资料时更新列表后重跑即可。

## Notes
- 本 skill 不直接对比具体产品条款细节（时效性强），涉及具体产品保额/保费/网络医院时务必先走 Step 2 检索 IMA 资料库核对。
- **素材优先级**：用户真实展业话术（`references/source/` + `materials_index.md`）高于 skill 内置基线 references；遇到具体异议先查索引、调取对应素材，再叠加基线论证，不要凭空编造话术。
- 沟通基调：路径差异而非贬低他品；先共情再转折；用"就医自由度"替代"保额数字"。
- 不编造客户未提供的体况或需求；缺失信息明确标注"未知"并给出需补充项。
