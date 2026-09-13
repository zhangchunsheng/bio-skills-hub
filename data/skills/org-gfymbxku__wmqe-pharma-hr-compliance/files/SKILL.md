---
name: wmqe-pharma-hr-compliance
slug: wmqe-pharma-hr-compliance
displayName: 医药企鹅-合规与制度
version: 1.0.5
description: "当HR用户需要医药行业员工手册、合规培训材料（如反商业贿赂），或绩效考核方案时使用本技能。涵盖：员工手册编写、合规培训材料、绩效考核方案。"
summary: "医药行业人力资源合规与制度：员工手册、反商业贿赂培训材料与绩效考核方案。"
tags: [医药, 制药, HR, 合规, 员工手册]
license: MIT
agent_created: true
---

# 合规与制度（人力资源 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **人力资源** role, specifically the **合规与制度** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when an HR user needs employee handbooks for pharma, compliance training materials (e.g. anti-bribery), or performance appraisal plans. Covers: 员工手册编写, 合规培训材料, 绩效考核方案.

## 触发示例
- "员工手册编写：提供公司政策和福利信息，自动生成医药行业员工手册"
- "合规培训材料：描述合规要求（如反商业贿赂），自动生成培训材料"
- "绩效考核方案：提供考核指标，自动生成医药销售/研发人员考核方案"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 员工手册编写 | 提供公司政策和福利信息，自动生成医药行业员工手册 | 文档规范化 | 员工手册(.docx) |
| 合规培训材料 | 描述合规要求（如反商业贿赂），自动生成培训材料 | 风险防范 | 合规培训材料(.md) |
| 绩效考核方案 | 提供考核指标，自动生成医药销售/研发人员考核方案 | 管理规范 | 考核方案(.docx) |

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
