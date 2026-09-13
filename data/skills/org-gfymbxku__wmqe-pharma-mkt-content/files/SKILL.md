---
name: wmqe-pharma-mkt-content
slug: wmqe-pharma-mkt-content
displayName: 医药企鹅-内容创作
version: 1.0.3
description: "当市场/医学教育用户需要深度医学文章、多渠道内容适配、学术活动策划，或患者教育材料时使用本技能。涵盖：学术文章撰写、多渠道内容适配、学术活动策划、患者教育文案。"
summary: "市场与医学教育内容创作：深度医学文章、多渠道内容适配、学术活动策划与患者教育材料。"
tags: [医药, 制药, 市场, 内容, 医学教育]
license: MIT
agent_created: true
---

# 内容创作（市场推广/医学教育 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **市场推广/医学教育** role, specifically the **内容创作** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a marketing/medical-education user needs deep medical articles, multi-channel content adaptation, academic event planning, or patient education materials. Covers: 学术文章撰写, 多渠道内容适配, 学术活动策划, 患者教育文案.

## 触发示例
- "学术文章撰写：提供主题和关键数据，一键生成专业医学深度文章"
- "多渠道内容适配：一份学术素材，自动改写成科室会、线上会、患教等多版本"
- "学术活动策划：描述活动目标和预算，自动生成完整学术会议策划文档"
- "患者教育文案：输入疾病知识和治疗要点，自动生成患者教育材料"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 学术文章撰写 | 提供主题和关键数据，一键生成专业医学深度文章 | 内容产能提升 | 医学文章(.md) |
| 多渠道内容适配 | 一份学术素材，自动改写成科室会、线上会、患教等多版本 | 一鱼多吃 | 多版本内容包(.md) |
| 学术活动策划 | 描述活动目标和预算，自动生成完整学术会议策划文档 | 从零到方案 | 活动策划案(.docx) |
| 患者教育文案 | 输入疾病知识和治疗要点，自动生成患者教育材料 | 创意效率 | 患教材料(.md) |

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
