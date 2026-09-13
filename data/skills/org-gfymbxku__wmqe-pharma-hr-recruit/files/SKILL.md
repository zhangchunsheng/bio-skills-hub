---
name: wmqe-pharma-hr-recruit
slug: wmqe-pharma-hr-recruit
displayName: 医药企鹅-招聘管理
version: 1.0.3
description: "当HR用户需要医药行业专属职位描述（如CRA、药物警戒专员）、简历筛选、专业面试题库或候选人评估时使用本技能。涵盖：JD职位描述、简历筛选、面试题库、候选人评估。"
summary: "医药行业招聘管理：CRA/药物警戒等专属职位描述、简历筛选、专业面试题库与候选人评估。"
tags: [医药, 制药, HR, 招聘, JD]
license: MIT
agent_created: true
---

# 招聘管理（人力资源 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **人力资源** role, specifically the **招聘管理** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when an HR user needs pharmaceutical-specific job descriptions (e.g. CRA, PV specialist), resume screening, professional interview question banks, or candidate evaluation. Covers: JD职位描述, 简历筛选, 面试题库, 候选人评估.

## 触发示例
- "JD职位描述：输入岗位名称（如CRA、PV专员）和核心要求，自动生成医药行业专业JD"
- "简历筛选：上传简历，AI分析候选人医药背景与岗位匹配度"
- "面试题库：提供岗位能力模型，自动生成GMP、注册法规等专业面试题"
- "候选人评估：描述面试表现，自动生成标准化评估意见"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| JD职位描述 | 输入岗位名称（如CRA、PV专员）和核心要求，自动生成医药行业专业JD | 招聘效率提升 | 岗位JD(.docx) |
| 简历筛选 | 上传简历，AI分析候选人医药背景与岗位匹配度 | 初筛加速 | 匹配度评估(.md) |
| 面试题库 | 提供岗位能力模型，自动生成GMP、注册法规等专业面试题 | 专业化提升 | 面试题库(.md) |
| 候选人评估 | 描述面试表现，自动生成标准化评估意见 | 流程规范化 | 评估意见(.docx) |

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
