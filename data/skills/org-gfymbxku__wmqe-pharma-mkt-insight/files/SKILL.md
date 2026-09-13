---
name: wmqe-pharma-mkt-insight
slug: wmqe-pharma-mkt-insight
displayName: 医药企鹅-市场洞察
version: 1.0.3
description: "当市场用户需要竞品动态监控、行业报告解读，或医生调研分析时使用本技能。涵盖：竞品动态监控、行业报告解读、医生调研分析。"
summary: "市场洞察：竞品动态监控、行业报告解读与医生调研分析。"
tags: [医药, 制药, 市场, 洞察, 竞品]
license: MIT
agent_created: true
---

# 市场洞察（市场推广/医学教育 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **市场推广/医学教育** role, specifically the **市场洞察** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a marketing user needs competitor dynamics monitoring, industry report digestion, or physician survey analysis. Covers: 竞品动态监控, 行业报告解读, 医生调研分析.

## 触发示例
- "竞品动态监控：设置关注竞品，AI定期汇总竞品学术活动、医保动态、新适应症获批"
- "行业报告解读：上传医药市场报告，AI提炼核心观点、市场规模、增长趋势"
- "医生调研分析：上传调研数据，AI自动生成处方行为分析报告和洞察建议"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 竞品动态监控 | 设置关注竞品，AI定期汇总竞品学术活动、医保动态、新适应症获批 | 情报自动化 | 竞品情报周报(.md) |
| 行业报告解读 | 上传医药市场报告，AI提炼核心观点、市场规模、增长趋势 | 快速吸收 | 报告解读(.md) |
| 医生调研分析 | 上传调研数据，AI自动生成处方行为分析报告和洞察建议 | 数据驱动 | 调研分析报告(.html) |

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
支持的分析类型：`summary、ranking`。配置示例见 references/templates.md。

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
