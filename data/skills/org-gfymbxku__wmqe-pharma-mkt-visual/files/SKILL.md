---
name: wmqe-pharma-mkt-visual
slug: wmqe-pharma-mkt-visual
displayName: 医药企鹅-视觉素材
version: 1.0.3
description: "当市场用户需要学术海报设计建议、科室会封面，或疾病知识图谱信息图时使用本技能。涵盖：学术海报设计、科室会封面、疾病知识图谱。"
summary: "市场视觉素材：学术海报设计建议、科室会封面与疾病知识图谱信息图。"
tags: [医药, 制药, 市场, 视觉, 海报]
license: MIT
agent_created: true
---

# 视觉素材（市场推广/医学教育 · pharma skill）

## 用途
This skill equips WorkBuddy to act as a specialized assistant for the **市场推广/医学教育** role, specifically the **视觉素材** sub-scenario set from the 医药企鹅 WorkBuddy 医药企业AI工作场景案例白皮书. This skill should be used when a marketing user needs academic poster design suggestions, department-meeting covers, or disease knowledge-graph infographics. Covers: 学术海报设计, 科室会封面, 疾病知识图谱.

## 触发示例
- "学术海报设计：提供研究数据，AI生成学术会议海报设计建议"
- "科室会封面：提供会议主题，自动生成各平台适配封面"
- "疾病知识图谱：提供疾病信息，自动生成疾病机制信息图"

## 适用场景明细
| 场景 | 操作方式 | 提效价值 | 典型交付物 |
|------|----------|----------|------------|
| 学术海报设计 | 提供研究数据，AI生成学术会议海报设计建议 | 降低设计成本 | 海报设计建议(.md) |
| 科室会封面 | 提供会议主题，自动生成各平台适配封面 | 品牌一致性 | 封面方案(.md) |
| 疾病知识图谱 | 提供疾病信息，自动生成疾病机制信息图 | 数据可视化 | 知识图谱大纲(.md) |

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
