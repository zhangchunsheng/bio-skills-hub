---
name: wmqe-pharma-ma-evidence
slug: wmqe-pharma-ma-evidence
displayName: 医药企鹅-医学证据与演示
version: 1.0.4
description: "当医学事务用户需要药物经济学分析（ICER/成本效果）、临床路径图绘制，或基于药物警戒数据的不良反应信号检测时使用本技能。涵盖：卫生经济学分析、临床路径图绘制、不良反应信号分析。"
summary: "医学证据与演示：药物经济学(ICER/成本效果)、临床路径图绘制与不良反应信号检测。"
tags: [医药, 制药, 医学事务, 药物经济学, 临床路径]
license: MIT
agent_created: true
---

# 医学证据与演示（医学事务/技术支持 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **医学事务/技术支持** role, specifically the **医学证据与演示** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a medical affairs user needs pharmacoeconomic analysis (ICER/cost-effectiveness), clinical pathway diagrams, or adverse-event signal detection from pharmacovigilance data. Covers: 卫生经济学分析, 临床路径图绘制, 不良反应信号分析.

## 触发示例
- "卫生经济学分析：输入治疗方案和成本数据，自动计算ICER、成本效果比"
- "临床路径图绘制：描述诊疗流程，AI生成可视化临床路径图"
- "不良反应信号分析：上传药物警戒数据，AI识别潜在安全风险信号"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 卫生经济学分析 | 输入治疗方案和成本数据，自动计算ICER、成本效果比 | 数据支撑说服 | 卫生经济学报告(.docx) |
| 临床路径图绘制 | 描述诊疗流程，AI生成可视化临床路径图 | 直观展示 | 临床路径图大纲(.md) |
| 不良反应信号分析 | 上传药物警戒数据，AI识别潜在安全风险信号 | 风险预警 | 信号分析清单(.md) |

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
支持的分析类型：`ratio、warning`。配置示例见 references/templates.md。

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
