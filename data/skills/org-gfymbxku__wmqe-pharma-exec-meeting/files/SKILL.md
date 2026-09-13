---
name: wmqe-pharma-exec-meeting
slug: wmqe-pharma-exec-meeting
displayName: 医药企鹅-会议与汇报
version: 1.0.3
description: "当高管需要含行动项的纪要、董事会材料，或投资者路演材料时使用本技能。涵盖：会议纪要生成、董事会材料、投资者汇报。"
summary: "面向高管的会议与汇报支撑：生成含行动项的会议纪要、董事会材料与投资者路演材料。"
tags: [医药, 制药, 高管, 会议纪要, 董事会, 路演]
license: MIT
agent_created: true
---

# 会议与汇报（企业高管/管理层 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **企业高管/管理层** role, specifically the **会议与汇报** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when an executive needs structured meeting minutes with action items, board materials, or investor roadshow decks. Covers: 会议纪要生成, 董事会材料, 投资者汇报.

## 触发示例
- "会议纪要生成：提供会议内容，自动生成结构化会议纪要（含行动项）"
- "董事会材料：输入核心数据和要点，AI生成专业董事会汇报材料"
- "投资者汇报：提供财务和管线数据，自动生成面向投资人的路演材料"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 会议纪要生成 | 提供会议内容，自动生成结构化会议纪要（含行动项） | 高效闭环 | 会议纪要(.docx) |
| 董事会材料 | 输入核心数据和要点，AI生成专业董事会汇报材料 | 准备时间大幅减少 | 董事会材料(.docx) |
| 投资者汇报 | 提供财务和管线数据，自动生成面向投资人的路演材料 | 流程化输出 | 路演材料(.md) |

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
