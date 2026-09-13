---
name: wmqe-pharma-rd-docs
slug: wmqe-pharma-rd-docs
displayName: 医药企鹅-文档与汇报
version: 1.0.3
description: "当研发用户需要周期性研发报告、结构化周报/项目总结，或申报资料清单整理时使用本技能。涵盖：研发报告撰写、周报/项目总结、申报资料整理。"
summary: "药物研发文档与汇报：周期性研发报告、结构化周报/项目总结与申报资料清单整理。"
tags: [医药, 制药, 研发, 文档, 周报]
license: MIT
agent_created: true
---

# 文档与汇报（药物研发/质量管理 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **药物研发/质量管理** role, specifically the **文档与汇报** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when an R&D user needs periodic R&D reports, structured weekly/project summaries, or submission material checklists. Covers: 研发报告撰写, 周报/项目总结, 申报资料整理.

## 触发示例
- "研发报告撰写：描述研发进展，自动生成阶段性研发报告"
- "周报/项目总结：汇总本周实验进展，自动生成结构化研发周报"
- "申报资料整理：提供申报要求，自动生成资料清单和整理建议"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 研发报告撰写 | 描述研发进展，自动生成阶段性研发报告 | 模板化输出 | 研发报告(.docx) |
| 周报/项目总结 | 汇总本周实验进展，自动生成结构化研发周报 | 减少重复 | 研发周报(.docx) |
| 申报资料整理 | 提供申报要求，自动生成资料清单和整理建议 | 有序高效 | 申报清单(.md) |

## 工作流
1. **明确场景与输入**：根据用户诉求定位上表中的目标场景，并收集所需输入（文本描述、CSV/Excel 数据、参考文件等）。
2. **组织内容**：基于场景要点与领域知识，撰写/归纳结构化内容（章节、要点、表格）。
3. **产出 spec**：将内容组织为 render.py 所需的 spec JSON（结构见 references/templates.md）。
4. **渲染交付物**：执行 `python scripts/render.py <spec.json> --format <md|html|docx|json> --output <交付文件路径>`。
5. **交付与复核**：返回交付物，并提示医药行业合规与人工复核要求（见下）。

## 脚本
- `scripts/render.py`：通用文档渲染器（支持 md / html / docx / json）。


## 输入 spec 说明（render.py）
spec 为 JSON，结构：
```json
{
  "title": "报告标题",
  "subtitle": "可选副标题",
  "meta": [["字段", "值"]],
  "sections": [
    {"heading": "章节标题", "paragraphs": ["段落"], "bullets": ["要点"], "table": {"headers": ["列1","列2"], "rows": [["a","b"]]}, "note": "提示"}
  ],
  "footer": "页脚"
}
```
完整字段与示例见 `references/templates.md`。

## 合规提示
医药行业涉及患者隐私、商业合规（反商业贿赂、GSP/GMP、数据合规）与广告宣传限制。所有 AI 产出仅供内部决策参考；对外材料（推广、招投标、注册、合同）须经相应资质人员复核并走合规审批流程，且不得含有未经证实的疗效或合规承诺。
