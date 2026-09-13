# General-skill-reviewer 参考资料

## 关键研究发现速查（R1-R11）

以下研究发现是评审打分的科学基础，在评审中以 `[R编号]` 格式引用。

| 编号 | 研究发现 | 来源/年份 |
|:---:|---|---|
| R1 | LLM 存在 U 型注意力曲线，中段信息准确率下降约30% | Lost in the Middle (2023-2025) |
| R2 | 系统提示超过800 tokens 开始稀释指令遵从度 | Prompt Engineering Patterns 2026 |
| R3 | 推理性能在约3000 tokens 后开始退化 | Prompt Optimization Research 2025 |
| R4 | 87.5%的负向约束违规源于启动效应（提及禁止词反而激活其生成概率） | Semantic Gravity Wells (2025) |
| R5 | 正向指令优先+推理在后的结构，违规率仅7%（约束优先结构为31%） | Instruction Polarity Research (2025) |
| R6 | 3个Few-shot示例将结构化输出可靠性从71%提升到94% | Prompt Engineering Patterns 2026 |
| R7 | 结构化输出（XML标签）比JSON格式平均遵从率高11% | Prompt Engineering Patterns 2026 |
| R8 | 简洁提示可减少35%-81%的token消耗且不降低输出质量 | Token Optimization Research 2025 |
| R9 | 生产级结构化提示可达91%必须项遵从率和94%禁止项遵从率 | SCHEMA Production Study 2025 |
| R10 | 无 LLM 在10条约束测试中开箱即达100%遵从，但提示策略显著影响结果 | 18-Model Benchmark 2025 |
| R11 | 多 Skill 协作体系中，强制每步加载子 Skill 会在长对话中因重复加载导致 token 挤压，使核心输出（如报告）无法在单轮中完成 | 崩溃分析 Skills 实战发现 2026-04 |
