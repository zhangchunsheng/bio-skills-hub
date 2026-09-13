# 输出格式规范

## 1. 摘要报告格式

### 1.1 Markdown格式（默认）

```markdown
# [论文标题]

## 📋 基本信息
- **作者**：[作者列表]
- **期刊**：[期刊名称]
- **发表日期**：[日期]
- **DOI**：[DOI]
- **研究设计**：[研究类型]

## 🎯 研究目的
[1-2句话概括]

## 🔬 主要发现
1. [发现1]
2. [发现2]
3. [发现3]

## 📊 关键数据
- [统计指标1]
- [统计指标2]

## 💡 创新点
- [创新点1]
- [创新点2]

## ⚠️ 研究局限性
- [局限性1]
- [局限性2]

## 🏥 临床意义
[简要说明]

## 🔗 知识图谱
[图谱可视化链接或内嵌图谱]

---
*分析时间：[时间戳]*
```

### 1.2 简洁格式

```
【论文标题】[标题]
【作者】[作者]
【期刊】[期刊] | [日期]
【研究设计】[类型]

【目的】[1句话]
【方法】[1句话]
【结果】[1-2句话]
【结论】[1句话]

【关键词】[关键词1], [关键词2], [关键词3]
```

## 2. 实体数据格式

### 2.1 JSON格式

```json
{
  "diseases": ["2型糖尿病", "心肌梗死"],
  "drugs": ["二甲双胍"],
  "genes": ["AMPK"],
  "symptoms": [],
  "procedures": [],
  "biomarkers": ["HbA1c", "CRP"],
  "anatomy": ["心脏"],
  "populations": [],
  "animal_models": [],
  "cell_lines": [],
  "pathways": ["AMPK通路", "NF-κB通路"],
  "metabolites": [],
  "devices": [],
  "outcomes": ["总生存期", "MACE发生率"],
  "relations": [
    {"source": "二甲双胍", "target": "2型糖尿病", "type": "治疗", "evidence": "二甲双胍显著降低HbA1c水平（P<0.001）"},
    {"source": "二甲双胍", "target": "AMPK通路", "type": "激活", "evidence": "二甲双胍通过激活AMPK通路发挥心血管保护作用"},
    {"source": "AMPK通路", "target": "NF-κB通路", "type": "抑制", "evidence": "AMPK激活后抑制NF-κB介导的炎症反应"},
    {"source": "2型糖尿病", "target": "心肌梗死", "type": "导致", "evidence": "糖尿病患者心肌梗死风险显著升高（HR 2.3）"}
  ]
}
```

> **注意**：`relations` 字段是图谱的核心，只填写论文中有文本依据的关系，不推断、不臆造。没有关系的实体不需要列出。

### 2.2 带上下文的实体格式

```json
{
  "entities": [
    {
      "name": "实体名称",
      "type": "实体类型",
      "confidence": 0.95,
      "context": "出现该实体的上下文文本",
      "position": 1234,
      "normalized_name": "标准化名称"
    }
  ]
}
```

## 3. 知识图谱格式

### 3.1 JSON格式（默认）

```json
{
  "metadata": {
    "created_at": "2026-05-24T10:30:00",
    "node_count": 15,
    "edge_count": 22,
    "node_types": ["Disease", "Drug", "Gene"],
    "relation_types": ["TREATS", "ASSOCIATED_WITH"]
  },
  "nodes": [
    {
      "id": "node_001",
      "label": "2型糖尿病",
      "node_type": "Disease",
      "properties": {},
      "sources": ["paper_001"]
    }
  ],
  "edges": [
    {
      "source": "node_001",
      "target": "node_002",
      "relation_type": "TREATS",
      "properties": {},
      "evidence": "论文中的证据文本",
      "confidence": 0.9
    }
  ]
}
```

### 3.2 Cypher格式（Neo4j）

```cypher
// 创建节点
CREATE (n:Disease {id: "node_001", name: "2型糖尿病"});
CREATE (n:Drug {id: "node_002", name: "二甲双胍"});

// 创建关系
MATCH (a {id: "node_002"}), (b {id: "node_001"})
CREATE (a)-[:TREATS {confidence: 0.9}]->(b);
```

### 3.3 Turtle格式（RDF）

```turtle
@prefix med: <http://medical-kg.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

med:node_001 rdf:type med:Disease ;
    rdfs:label "2型糖尿病" .

med:node_002 rdf:type med:Drug ;
    rdfs:label "二甲双胍" .

med:node_002 med:treats med:node_001 .
```

## 4. 统计数据格式

```json
{
  "primary_outcomes": [
    {
      "outcome": "主要结局指标名称",
      "effect_size": "0.77",
      "effect_type": "HR",
      "ci_lower": "0.65",
      "ci_upper": "0.91",
      "p_value": "0.002"
    }
  ],
  "secondary_outcomes": [
    {
      "outcome": "次要结局指标名称",
      "effect_size": "0.69",
      "effect_type": "HR",
      "ci_lower": "0.52",
      "ci_upper": "0.92",
      "p_value": "0.01"
    }
  ],
  "sample_size": 5200,
  "follow_up_duration": "4.5年",
  "dropout_rate": "5.2%"
}
```

## 5. 文件命名规范

### 5.1 摘要报告

```
summary_[论文标识]_[日期].md
```

示例：
```
summary_diabetes_metformin_20260524.md
```

### 5.2 实体数据

```
entities_[论文标识]_[日期].json
```

示例：
```
entities_diabetes_metformin_20260524.json
```

### 5.3 知识图谱

```
knowledge_graph_[论文标识]_[日期].json
```

示例：
```
knowledge_graph_diabetes_metformin_20260524.json
```

## 6. 输出目录结构

```
medical-analysis/
├── summaries/           # 摘要报告
│   ├── paper1_summary.md
│   └── paper2_summary.md
├── entities/            # 实体数据
│   ├── paper1_entities.json
│   └── paper2_entities.json
├── knowledge_graphs/    # 知识图谱
│   ├── paper1_graph.json
│   └── paper2_graph.json
├── combined/            # 合并结果
│   ├── combined_graph.json
│   └── literature_review.md
└── exports/             # 导出文件
    ├── graph.cypher
    └── graph.turtle
```

## 7. 可视化输出格式

### 7.1 HTML交互式图谱

使用D3.js或vis.js生成的交互式HTML文件，支持：
- 节点拖拽
- 缩放平移
- 节点详情查看
- 关系高亮
- 搜索过滤

### 7.2 图片格式

支持导出为：
- PNG（静态图片）
- SVG（矢量图）
- PDF（文档格式）

## 8. 批量处理输出

### 8.1 汇总报告

```markdown
# 文献分析汇总报告

## 分析概况
- 分析论文数量：[数量]
- 分析时间范围：[开始时间] - [结束时间]
- 总耗时：[时间]

## 论文列表
| 序号 | 标题 | 作者 | 期刊 | 研究设计 |
|------|------|------|------|----------|
| 1 | [标题] | [作者] | [期刊] | [类型] |

## 实体统计
| 实体类型 | 数量 | 示例 |
|----------|------|------|
| 疾病 | 15 | 糖尿病、高血压... |
| 药物 | 12 | 二甲双胍、胰岛素... |

## 知识图谱统计
- 节点总数：[数量]
- 边总数：[数量]
- 连通分量：[数量]
- 平均度：[数值]

## 主要发现
[汇总各论文的主要发现]

## 综合结论
[基于所有论文的综合分析]
```

## 9. 数据交换格式

### 9.1 通用元数据格式

```json
{
  "schema_version": "1.0",
  "created_at": "2026-05-24T10:30:00Z",
  "tool_version": "1.0.0",
  "source": "medical-literature-skill",
  "format": "medical-kg-v1"
}
```

### 9.2 兼容性说明

支持导出为以下工具兼容的格式：
- Neo4j（Cypher）
- GraphDB（Turtle/RDF）
- Gephi（GEXF）
- Cytoscape（JSON）
