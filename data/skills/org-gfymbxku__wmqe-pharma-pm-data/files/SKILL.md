---
name: wmqe-pharma-pm-data
slug: wmqe-pharma-pm-data
displayName: 医药企鹅-数据驱动决策
version: 1.0.4
description: "当产品经理需要分类/整合KOL访谈反馈、搭建市场数据看板，或设计临床试验方案（样本量、终点指标）时使用本技能。涵盖：医生反馈分析、市场数据看板、临床试验设计。"
summary: "产品数据驱动决策：KOL访谈反馈分类整合、市场数据看板与临床试验方案设计。"
tags: [医药, 制药, 产品, 数据, KOL, 临床试验]
license: MIT
agent_created: true
---

# 数据驱动决策（产品管理/新药研发 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **产品管理/新药研发** role, specifically the **数据驱动决策** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a product manager needs to classify/synthesize KOL interview feedback, build market data dashboards, or design clinical trial protocols (sample size, endpoints). Covers: 医生反馈分析, 市场数据看板, 临床试验设计.

## 触发示例
- "医生反馈分析：上传KOL访谈记录，AI自动分类、归纳、提炼临床需求"
- "市场数据看板：上传销售和市场数据，自动生成可视化图表和竞争分析报告"
- "临床试验设计：输入研究目的，AI协助设计试验方案、样本量计算、终点选择"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 医生反馈分析 | 上传KOL访谈记录，AI自动分类、归纳、提炼临床需求 | 从噪音到洞察 | 反馈洞察报告(.md) |
| 市场数据看板 | 上传销售和市场数据，自动生成可视化图表和竞争分析报告 | 数据叙事 | 市场看板(.html) |
| 临床试验设计 | 输入研究目的，AI协助设计试验方案、样本量计算、终点选择 | 快速验证 | 试验设计方案(.docx) |

## 工作流
1. **明确场景与输入**：根据用户诉求定位上表中的目标场景，并收集所需输入（文本描述、CSV/Excel 数据、参考文件等）。
2. **组织内容**：基于场景要点与领域知识，撰写/归纳结构化内容（章节、要点、表格）。
3. **运行分析**：对量化数据场景，执行 `python scripts/analyze.py <数据文件> <config.json> --output result.json` 得到分析 spec。
4. **渲染交付物**：执行 `python scripts/render.py <spec.json> --format <md|html|docx|json> --output <交付文件路径>`。
5. **交付与复核**：返回交付物，并提示医药行业合规与人工复核要求（见下）。

## 脚本
- `scripts/render.py`：通用文档渲染器（支持 md / html / docx / json）。
- `scripts/analyze.py`：通用数据分析器（trend/ranking/warning/ratio/comparison/summary）。


## 数据分析（本类含）
涉及量化数据的场景，先运行 `scripts/analyze.py` 生成分析 spec JSON，再交给 render.py 出报告。
支持的分析类型：`summary、trend`。配置示例见 references/templates.md。

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
