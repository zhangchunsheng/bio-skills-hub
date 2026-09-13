---
name: wmqe-pharma-hr-training
slug: wmqe-pharma-hr-training
displayName: 医药企鹅-培训与发展
version: 1.0.3
description: "当HR用户需要新员工培训材料（GMP/合规/文化）、岗位技能差距矩阵，或培训效果分析时使用本技能。涵盖：新员工培训、岗位技能矩阵、培训效果评估。"
summary: "医药行业培训与发展：新员工GMP/合规/文化培训、岗位技能差距矩阵与培训效果分析。"
tags: [医药, 制药, HR, 培训, GMP]
license: MIT
agent_created: true
---

# 培训与发展（人力资源 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **人力资源** role, specifically the **培训与发展** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when an HR user needs new-employee training decks (GMP/compliance/culture), skill-gap matrices, or training-effectiveness analysis. Covers: 新员工培训, 岗位技能矩阵, 培训效果评估.

## 触发示例
- "新员工培训：提供培训目标，自动生成GMP、合规、企业文化培训PPT"
- "岗位技能矩阵：上传岗位要求，自动生成技能差距分析和发展计划"
- "培训效果评估：输入培训数据，自动生成培训效果分析报告"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 新员工培训 | 提供培训目标，自动生成GMP、合规、企业文化培训PPT | 内容生产 | 培训PPT(.md) |
| 岗位技能矩阵 | 上传岗位要求，自动生成技能差距分析和发展计划 | 人才发展 | 技能矩阵(.md) |
| 培训效果评估 | 输入培训数据，自动生成培训效果分析报告 | 持续改进 | 培训效果报告(.docx) |

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
支持的分析类型：`summary`。配置示例见 references/templates.md。

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
