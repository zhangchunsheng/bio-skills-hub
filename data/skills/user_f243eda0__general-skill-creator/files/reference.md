# General-skill-creator 参考资料

## §1 多 Skill 协作体系的额外约束

当产出 Skill 涉及多个子 Skill 协作（如 orchestrator + 多个 worker Skill）时，必须遵守以下约束：

1. **单次运行时加载量**（orchestrator + 当前步骤的 worker Skill）≤ 800 行 / ~12,000 tokens
2. 当强制要求"每步 use_skill 加载子 Skill"时，增加**长对话豁免条件**：当对话上下文中已有该 Skill 内容且 token 紧张时，可跳过重复加载
3. 在 orchestrator 中增加**优先级声明**：当 token 紧张时，优先确保核心输出物（如报告文件）完整写入，摘要输出可精简
4. 避免在 orchestrator 和子 Skill 中重复定义同一个 checklist/模板 — 在一处定义，其他处通过引用声明

> 以上约束来源于崩溃分析 Skills 实战经验：一次长对话中因 orchestrator 强制重新加载子 Skill 导致 Token 耗尽，最终报告无法在单轮中完成。
