---
name: wmqe-pharma-exec-decision
slug: wmqe-pharma-exec-decision
displayName: 医药企鹅-经营决策支撑
version: 1.0.3
description: "当高管需要整合生产/销售/研发数据生成经营看板、进行行业对标分析（如某药企、某药企），或获得战略规划辅助时使用本技能。涵盖：经营数据看板、行业对标分析、战略规划辅助。"
summary: "面向医药企业高管的经营决策支撑：整合生产/销售/研发数据生成经营看板、行业对标与战略规划建议。"
tags: [医药, 制药, 高管, 经营决策, 数据看板, AI工作流]
license: MIT
agent_created: true
---

# 经营决策支撑（企业高管/管理层 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **企业高管/管理层** role, specifically the **经营决策支撑** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when an executive needs a consolidated business dashboard from production/sales/R&D data, industry benchmarking (e.g. Hengrui, CSPC), or strategic planning assistance. Covers: 经营数据看板, 行业对标分析, 战略规划辅助.

## 触发示例
- "经营数据看板：上传生产、销售、研发数据，AI自动汇总生成经营全景分析"
- "行业对标分析：输入关注指标，AI调研某药企、某药企等同行标杆数据"
- "战略规划辅助：描述战略目标（如进入新适应症领域），AI分析可行路径"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 经营数据看板 | 上传生产、销售、研发数据，AI自动汇总生成经营全景分析 | 全局视野 | 经营看板(.html) |
| 行业对标分析 | 输入关注指标，AI调研某药企、某药企等同行标杆数据 | 知己知彼 | 对标分析报告(.docx) |
| 战略规划辅助 | 描述战略目标（如进入新适应症领域），AI分析可行路径 | 决策质量 | 战略规划建议(.md) |

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
支持的分析类型：`summary、comparison`。配置示例见 references/templates.md。

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
