# General-skill-creator — 垂直领域 Skill 工程师

通过 **Builder-Evaluator 分离架构**和**最低三轮质量迭代**，为任意垂直领域打造生产级专业 Skill。

## 触发词

- 创建skill、设计skill、写一个skill
- 新建技能、skill creator
- 帮我做一个skill

## 文件结构

| 文件 | 说明 |
|---|---|
| `SKILL.md` | Skill 主体（v4.2），包含完整 8 阶段工作流 |
| `examples.md` | 3 个跨领域完成品 Skill 片段参考（写作类/分析类/对话类） |

## 工作流概览

```
PHASE 1: 需求解析与调研 → PHASE 2: 架构设计 → PHASE 3: 规则与示例工程
    → PHASE 4: 规则质量迭代（≥3轮）→ PHASE 5: Skill 组装
    → PHASE 6: 实效验证迭代（≥3轮）→ PHASE 7: 工程质量审计
    → PHASE 8: 交付
```

## 配套 Skill

- **General-skill-reviewer**：PHASE 7 工程质量审计阶段可通过 `use_skill` 加载 `General-skill-reviewer` 执行完整 8 维度审计。
