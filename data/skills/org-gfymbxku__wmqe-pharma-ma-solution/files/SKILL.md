---
name: wmqe-pharma-ma-solution
slug: wmqe-pharma-ma-solution
displayName: 医药企鹅-医学解决方案设计
version: 1.0.3
description: "当医学事务用户需要撰写医学教育/临床项目方案、在临床/安全/经济数据维度对比己方产品与竞品，或制作含讲者备注的学术演讲素材时使用本技能。涵盖：医学方案编写、竞品医学对比、学术演讲素材PPT和讲者备注。"
summary: "医学解决方案设计：医学教育/临床项目方案、竞品多维对比与含讲者备注的学术演讲素材。"
tags: [医药, 制药, 医学事务, 方案, 竞品]
license: MIT
agent_created: true
---

# 医学解决方案设计（医学事务/技术支持 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **医学事务/技术支持** role, specifically the **医学解决方案设计** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a medical affairs user needs to draft medical education/clinical project plans, compare own product vs competitors on clinical/safety/economic data, or build academic speech decks with speaker notes. Covers: 医学方案编写, 竞品医学对比, 学术演讲素材PPT和讲者备注.

## 触发示例
- "医学方案编写：提供临床需求、适应症、患者人群，自动生成医学教育方案或临床项目方案"
- "竞品医学对比：输入自家产品与竞品名称，深度对比临床试验数据、安全性数据、经济学评价"
- "学术演讲素材PPT和讲者备注：描述学术会议需求，自动生成演讲PPT和讲者备注"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 医学方案编写 | 提供临床需求、适应症、患者人群，自动生成医学教育方案或临床项目方案 | 快速响应学术需求 | 医学方案(.docx) |
| 竞品医学对比 | 输入自家产品与竞品名称，深度对比临床试验数据、安全性数据、经济学评价 | 专业度提升 | 医学对比矩阵(.md) |
| 学术演讲素材PPT和讲者备注 | 描述学术会议需求，自动生成演讲PPT和讲者备注 | 准备时间大幅缩短 | 演讲PPT+讲者备注(.md) |

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
