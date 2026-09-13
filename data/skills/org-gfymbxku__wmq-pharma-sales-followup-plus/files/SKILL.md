---
name: wmq-pharma-sales-followup-plus
slug: wmq-pharma-sales-followup-plus
displayName: 医药企鹅-客户跟进与商机管理
version: 1.0.3
description: "当医药销售或商务拓展用户需要调研医院/药企背景、生成竞品药品分析报告、撰写针对性销售话术，或解读招标信息时使本技能。涵盖：医院/药企背调、竞品药品分析报告、销售话术生成、招标信息解读。"
summary: "客户跟进与商机管理：医院/药企背景调研、竞品药品分析报告、销售话术与招标信息解读。"
tags: [医药, 制药, 销售, 客户, 招投标]
license: MIT
agent_created: true
---

# 客户跟进与商机管理（医药销售/商务拓展 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **医药销售/商务拓展** role, specifically the **客户跟进与商机管理** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a pharmaceutical sales or business-development user needs to research hospital/company background, build competitor drug analysis reports, generate targeted sales talking points, or interpret tender documents. Covers: 医院/药企背调, 竞品药品分析报告, 销售话术生成, 招标信息解读.

## 触发示例
- "医院/药企背调：一句话描述目标医院或药企名称，自动查询医疗机构资质、采购历史、科室结构、关键决策人信息"
- "竞品药品分析报告：提供竞品药品名称，AI深度调研市场份额、适应症覆盖、临床数据、医保准入情况"
- "销售话术生成：描述医生/采购痛点场景（如控费压力、疗效需求），自动生成针对性沟通话术"
- "招标信息解读：上传集采/招标文件，AI自动提取关键条款、评分标准、时间节点"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 医院/药企背调 | 一句话描述目标医院或药企名称，自动查询医疗机构资质、采购历史、科室结构、关键决策人信息 | 5分钟→30秒，快速掌握客户全貌 | 客户背调报告(.md/.docx) |
| 竞品药品分析报告 | 提供竞品药品名称，AI深度调研市场份额、适应症覆盖、临床数据、医保准入情况 | 从头调研→即时交付 | 竞品分析报告(.md) |
| 销售话术生成 | 描述医生/采购痛点场景（如控费压力、疗效需求），自动生成针对性沟通话术 | 快速响应客户需求 | 话术卡片(.md) |
| 招标信息解读 | 上传集采/招标文件，AI自动提取关键条款、评分标准、时间节点 | 快速把握投标要点 | 招标文件解读(.md) |

## 工作流
1. **明确场景与输入**：根据用户诉求定位上表中的目标场景，并收集所需输入（文本描述、CSV/Excel 数据、参考文件等）。
2. **组织内容**：基于场景要点与领域知识，撰写/归纳结构化内容（章节、要点、表格）。
3. **产出 spec**：将内容组织为 render.py 所需的 spec JSON（结构见 references/templates.md）。
4. **渲染交付物**：执行 `python scripts/render.py <spec.json> --format <md|html|docx|json> --output <交付文件路径>`。
5. **交付与复核**：返回交付物，并提示医药行业合规与人工复核要求（见下）。

## 溯源与授权（重要）
- 本 skill 为 医药企鹅 专有资产，版权与授权见同目录 `LICENSE` / `NOTICE`。
- 唯一溯源标识（trace id）：**YYQ-2AE163E2**
- **强制水印**：渲染任何对外/对内交付物时，必须在 spec 中设置 `watermark` 字段为：
  > 本交付物由 医药企鹅 专有 AI skill（pharma-sales-followup / YYQ-2AE163E2）生成；未经书面授权禁止复制、转发或再分发。
  该字段会进入 md/html/docx 交付物末尾，用于泄露溯源。请勿删除。

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
  "footer": "页脚",
  "watermark": "本交付物由 医药企鹅 专有 AI skill（pharma-sales-followup / YYQ-2AE163E2）生成；未经书面授权禁止复制、转发或再分发。"
}
```
完整字段与示例见 `references/templates.md`。

## 合规提示
医药行业涉及患者隐私、商业合规（反商业贿赂、GSP/GMP、数据合规）与广告宣传限制。所有 AI 产出仅供内部决策参考；对外材料（推广、招投标、注册、合同）须经相应资质人员复核并走合规审批流程，且不得含有未经证实的疗效或合规承诺。
