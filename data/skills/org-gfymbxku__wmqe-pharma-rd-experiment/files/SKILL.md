---
name: wmqe-pharma-rd-experiment
slug: wmqe-pharma-rd-experiment
displayName: 医药企鹅-研发与实验
version: 1.0.4
description: "当研发用户需要实验方案审查、基于实验数据的统计分析报告、SOP检索，或CTD格式注册文件搭建时使用本技能。涵盖：实验方案审查、数据分析报告、SOP查询生成、注册文档生成。"
summary: "研发与实验支撑：实验方案审查、统计分析报告、SOP检索与CTD格式注册文件搭建。"
tags: [医药, 制药, 研发, 实验, SOP, CTD]
license: MIT
agent_created: true
---

# 研发与实验（药物研发/质量管理 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **药物研发/质量管理** role, specifically the **研发与实验** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when an R&D user needs experiment protocol review, statistical analysis reports from experimental data, SOP retrieval, or CTD-format registration document scaffolding. Covers: 实验方案审查, 数据分析报告, SOP查询生成, 注册文档生成.

## 触发示例
- "实验方案审查：上传实验方案，AI自动审查并提出优化建议（样本量、对照组设计等）"
- "数据分析报告：上传实验数据，自动生成统计分析和结果解读"
- "SOP查询生成：描述操作需求，AI自动检索相关SOP文件和操作规程"
- "注册文档生成：提供产品信息，自动生成CTD格式注册申报文档框架"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 实验方案审查 | 上传实验方案，AI自动审查并提出优化建议（样本量、对照组设计等） | 质量提升 | 审查意见(.md) |
| 数据分析报告 | 上传实验数据，自动生成统计分析和结果解读 | 技术传承 | 统计分析报告(.docx) |
| SOP查询生成 | 描述操作需求，AI自动检索相关SOP文件和操作规程 | 降低门槛 | SOP检索结果(.md) |
| 注册文档生成 | 提供产品信息，自动生成CTD格式注册申报文档框架 | 文档同步 | CTD框架(.docx) |

## 工作流
1. **明确场景与输入**：根据用户诉求定位上表中的目标场景，并收集所需输入（文本描述、CSV/Excel 数据、参考文件等）。
2. **组织内容**：基于场景要点与领域知识，撰写/归纳结构化内容（章节、要点、表格）。
3. **运行分析**：对量化数据场景，执行 `python scripts/analyze.py <数据文件> <config.json> --output result.json` 得到分析 spec。
4. **渲染交付物**：执行 `python scripts/render.py <spec.json> --format <md|html|docx|json> --output <交付文件路径>`。
5. **交付与复核**：返回交付物，并提示医药行业合规与人工复核要求（见下）。

## 溯源与授权（重要）
- 本 skill 为 医药企鹅 专有资产，版权与授权见同目录 `LICENSE` / `NOTICE`。
- 唯一溯源标识（trace id）：**YYQ-5545C2BA**
- **强制水印**：渲染任何对外/对内交付物时，必须在 spec 中设置 `watermark` 字段为：
  > 本交付物由 医药企鹅 专有 AI skill（pharma-rd-experiment / YYQ-5545C2BA）生成；未经书面授权禁止复制、转发或再分发。
  该字段会进入 md/html/docx 交付物末尾，用于泄露溯源。请勿删除。

## 脚本
- `scripts/render.py`：通用文档渲染器（支持 md / html / docx / json）。
- `scripts/analyze.py`：通用数据分析器（trend/ranking/warning/ratio/comparison/summary）。


## 数据分析（本类含）
涉及量化数据的场景，先运行 `scripts/analyze.py` 生成分析 spec JSON，再交给 render.py 出报告。
支持的分析类型：`summary、trend`。配置示例见 references/templates.md。

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
  "watermark": "本交付物由 医药企鹅 专有 AI skill（pharma-rd-experiment / YYQ-5545C2BA）生成；未经书面授权禁止复制、转发或再分发。"
}
```
完整字段与示例见 `references/templates.md`。

## 合规提示
医药行业涉及患者隐私、商业合规（反商业贿赂、GSP/GMP、数据合规）与广告宣传限制。所有 AI 产出仅供内部决策参考；对外材料（推广、招投标、注册、合同）须经相应资质人员复核并走合规审批流程，且不得含有未经证实的疗效或合规承诺。
