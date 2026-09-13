---
name: wmqe-pharma-ma-comms
slug: wmqe-pharma-ma-comms
displayName: 医药企鹅-医学沟通支撑
version: 1.0.4
description: "当医学事务用户需要基于说明书与文献构建医学FAQ库、分析临床需求，或以准确术语翻译英文医学文献时使用本技能。涵盖：医学FAQ库构建、临床需求分析、医学文献翻译。"
summary: "医学事务沟通支撑：基于说明书与文献构建医学FAQ库、临床需求分析与英文医学文献翻译。"
tags: [医药, 制药, 医学事务, FAQ, 文献翻译]
license: MIT
agent_created: true
---

# 医学沟通支撑（医学事务/技术支持 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **医学事务/技术支持** role, specifically the **医学沟通支撑** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a medical affairs user needs to build a medical FAQ library from labeling and literature, analyze clinical needs, or translate English medical literature with accurate terminology. Covers: 医学FAQ库构建, 临床需求分析, 医学文献翻译.

## 触发示例
- "医学FAQ库构建：上传产品说明书和临床文献，AI整理常见医学问题解答"
- "临床需求分析：描述临床痛点场景，AI分析并给出医学解决思路"
- "医学文献翻译：上传英文医学文献，快速翻译并保持医学术语准确性"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 医学FAQ库构建 | 上传产品说明书和临床文献，AI整理常见医学问题解答 | 知识沉淀 | 医学FAQ库(.md) |
| 临床需求分析 | 描述临床痛点场景，AI分析并给出医学解决思路 | 结构化思维 | 临床需求分析(.md) |
| 医学文献翻译 | 上传英文医学文献，快速翻译并保持医学术语准确性 | 消除语言障碍 | 中英对照译文(.md) |

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
