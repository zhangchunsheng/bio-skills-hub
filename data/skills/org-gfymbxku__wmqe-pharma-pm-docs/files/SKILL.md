---
name: wmqe-pharma-pm-docs
slug: wmqe-pharma-pm-docs
displayName: 医药企鹅-需求与文档
version: 1.0.4
description: "当产品经理需要产品定位文档、跨市场/技术/专利维度的研发管线优先级排序，或竞品功能对比矩阵时使用本技能。涵盖：产品定位文档、研发管线优先级、竞品功能对比。"
summary: "产品需求与文档：产品定位文档、研发管线优先级排序与竞品功能对比矩阵。"
tags: [医药, 制药, 产品, 文档, 管线]
license: MIT
agent_created: true
---

# 需求与文档（产品管理/新药研发 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **产品管理/新药研发** role, specifically the **需求与文档** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a product manager needs product positioning documents, R&D pipeline prioritization across market/technical/patent dimensions, or competitor feature comparison matrices. Covers: 产品定位文档, 研发管线优先级, 竞品功能对比.

## 触发示例
- "产品定位文档：描述产品特点和目标患者，自动生成产品定位策略文档"
- "研发管线优先级：列出在研项目清单，AI结合市场潜力、技术难度、专利期多维度分析优先级"
- "竞品功能对比：输入竞品列表，自动调研并生成适应症、剂型、价格对比矩阵"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 产品定位文档 | 描述产品特点和目标患者，自动生成产品定位策略文档 | 从想法到文档 | 产品定位文档(.docx) |
| 研发管线优先级 | 列出在研项目清单，AI结合市场潜力、技术难度、专利期多维度分析优先级 | 科学决策 | 管线优先级矩阵(.md) |
| 竞品功能对比 | 输入竞品列表，自动调研并生成适应症、剂型、价格对比矩阵 | 市场洞察 | 竞品对比矩阵(.md) |

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
