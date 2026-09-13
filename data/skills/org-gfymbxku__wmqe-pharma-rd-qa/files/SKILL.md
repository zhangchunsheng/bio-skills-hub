---
name: wmqe-pharma-rd-qa
slug: wmqe-pharma-rd-qa
displayName: 医药企鹅-质量管理与合规
version: 1.0.4
description: "当质量用户需要偏差根本原因与CAPA分析、检查用GMP条款查询，或供应商审计评估报告时使用本技能。涵盖：偏差原因分析、GMP法规查询、供应商审计报告。"
summary: "质量管理与合规：偏差根本原因与CAPA分析、GMP条款查询与供应商审计评估。"
tags: [医药, 制药, 研发, 质量, GMP, CAPA]
license: MIT
agent_created: true
---

# 质量管理与合规（药物研发/质量管理 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **药物研发/质量管理** role, specifically the **质量管理与合规** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a quality user needs deviation root-cause & CAPA analysis, GMP clause lookup for inspections, or supplier audit evaluation reports. Covers: 偏差原因分析, GMP法规查询, 供应商审计报告.

## 触发示例
- "偏差原因分析：描述偏差现象，AI推理可能根本原因和CAPA方案"
- "GMP法规查询：描述检查场景，AI检索GMP相关条款和检查要点"
- "供应商审计报告：上传审计记录，自动生成供应商评估报告"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 偏差原因分析 | 描述偏差现象，AI推理可能根本原因和CAPA方案 | 快速定位 | 偏差/CAPA报告(.md) |
| GMP法规查询 | 描述检查场景，AI检索GMP相关条款和检查要点 | 合规保障 | GMP条款检索(.md) |
| 供应商审计报告 | 上传审计记录，自动生成供应商评估报告 | 决策支撑 | 供应商评估报告(.docx) |

## 工作流
1. **明确场景与输入**：根据用户诉求定位上表中的目标场景，并收集所需输入（文本描述、CSV/Excel 数据、参考文件等）。
2. **组织内容**：基于场景要点与领域知识，撰写/归纳结构化内容（章节、要点、表格）。
3. **运行分析**：对量化数据场景，执行 `python scripts/analyze.py <数据文件> <config.json> --output result.json` 得到分析 spec。
4. **渲染交付物**：执行 `python scripts/render.py <spec.json> --format <md|html|docx|json> --output <交付文件路径>`。
5. **交付与复核**：返回交付物，并提示医药行业合规与人工复核要求（见下）。

## 溯源与授权（重要）
- 本 skill 为 医药企鹅 专有资产，版权与授权见同目录 `LICENSE` / `NOTICE`。
- 唯一溯源标识（trace id）：**YYQ-2DC24B2C**
- **强制水印**：渲染任何对外/对内交付物时，必须在 spec 中设置 `watermark` 字段为：
  > 本交付物由 医药企鹅 专有 AI skill（pharma-rd-qa / YYQ-2DC24B2C）生成；未经书面授权禁止复制、转发或再分发。
  该字段会进入 md/html/docx 交付物末尾，用于泄露溯源。请勿删除。

## 脚本
- `scripts/render.py`：通用文档渲染器（支持 md / html / docx / json）。
- `scripts/analyze.py`：通用数据分析器（trend/ranking/warning/ratio/comparison/summary）。


## 数据分析（本类含）
涉及量化数据的场景，先运行 `scripts/analyze.py` 生成分析 spec JSON，再交给 render.py 出报告。
支持的分析类型：`summary、ranking`。配置示例见 references/templates.md。

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
  "watermark": "本交付物由 医药企鹅 专有 AI skill（pharma-rd-qa / YYQ-2DC24B2C）生成；未经书面授权禁止复制、转发或再分发。"
}
```
完整字段与示例见 `references/templates.md`。

## 合规提示
医药行业涉及患者隐私、商业合规（反商业贿赂、GSP/GMP、数据合规）与广告宣传限制。所有 AI 产出仅供内部决策参考；对外材料（推广、招投标、注册、合同）须经相应资质人员复核并走合规审批流程，且不得含有未经证实的疗效或合规承诺。
