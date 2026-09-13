---
name: wmqe-pharma-sales-docs
slug: wmqe-pharma-sales-docs
displayName: 医药企鹅-文档与邮件
version: 1.0.4
description: "当医药销售用户需要制作符合GSP规范的报价单、学术推广邮件或完整的商务提案PPT时使用本技能。涵盖：报价单生成、学术推广邮件、客户提案PPT。"
summary: "医药销售文档与邮件：符合GSP规范的报价单、学术推广邮件与商务提案PPT。"
tags: [医药, 制药, 销售, 文档, GSP]
license: MIT
agent_created: true
---

# 文档与邮件（医药销售/商务拓展 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **医药销售/商务拓展** role, specifically the **文档与邮件** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a pharmaceutical sales user needs to produce GSP-compliant quotations, academic promotion emails, or complete business proposal PPTs. Covers: 报价单生成, 学术推广邮件, 客户提案PPT.

## 触发示例
- "报价单生成：提供药品信息和采购需求，自动生成符合GSP规范的专业报价单"
- "学术推广邮件：描述邮件目的和关键信息，一键生成专业学术推广邮件"
- "客户提案PPT：提供合作背景，AI生成完整商务合作提案PPT（含产品优势、临床数据、合作模式）"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 报价单生成 | 提供药品信息和采购需求，自动生成符合GSP规范的专业报价单 | 排版规范、时间节省 | GSP报价单(.docx/.md) |
| 学术推广邮件 | 描述邮件目的和关键信息，一键生成专业学术推广邮件 | 消除写作障碍 | 邮件正文(.md) |
| 客户提案PPT | 提供合作背景，AI生成完整商务合作提案PPT（含产品优势、临床数据、合作模式） | 从零到完整提案 | 提案PPT大纲(.md) |

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
