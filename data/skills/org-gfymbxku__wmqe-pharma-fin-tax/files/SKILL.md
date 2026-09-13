---
name: wmqe-pharma-fin-tax
slug: wmqe-pharma-fin-tax
displayName: 医药企鹅-税务与合规
version: 1.0.4
description: "当财务用户需要医药税务筹划、财税政策查询，或合同财税合规审查（付款条件、开票、返利条款）时使用本技能。涵盖：税务筹划、财税政策查询、合同财税审查。"
summary: "医药企业税务与合规：税务筹划、财税政策查询与合同财税合规审查。"
tags: [医药, 制药, 财务, 税务, 合规]
license: MIT
agent_created: true
---

# 税务与合规（财务/成本管理 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **财务/成本管理** role, specifically the **税务与合规** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a finance user needs pharmaceutical tax planning, fiscal policy lookup, or contract fiscal/compliance review (payment terms, invoicing, rebate clauses). Covers: 税务筹划, 财税政策查询, 合同财税审查.

## 触发示例
- "税务筹划：描述业务场景，AI分析医药企业税收优惠和筹划空间"
- "财税政策查询：描述业务类型，自动检索医药行业税收政策和申报要求"
- "合同财税审查：上传商业合同，AI检查付款节点、发票条款、返利条款合规性"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 税务筹划 | 描述业务场景，AI分析医药企业税收优惠和筹划空间 | 合规节税 | 税务筹划建议(.md) |
| 财税政策查询 | 描述业务类型，自动检索医药行业税收政策和申报要求 | 政策追踪 | 政策检索结果(.md) |
| 合同财税审查 | 上传商业合同，AI检查付款节点、发票条款、返利条款合规性 | 风险前置 | 合同审查意见(.md) |

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
