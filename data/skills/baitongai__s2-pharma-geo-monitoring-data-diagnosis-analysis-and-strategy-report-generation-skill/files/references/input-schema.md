# 输入数据标准JSON Schema

## 概述

本文件定义百通GEO平台监测数据的标准输入格式，兼容三种接入方式：API对接、Excel导出、人工粘贴。

## 完整JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Pharma GEO Monitoring Data Package",
  "description": "百通GEO平台监测数据标准格式",
  "type": "object",
  "required": ["metadata", "semantic_groups"],
  "properties": {

    "metadata": {
      "type": "object",
      "required": ["brand_name", "monitoring_period", "platforms", "query_count"],
      "properties": {
        "brand_name": {
          "type": "string",
          "description": "目标药品通用名或商品名",
          "example": "美泰彤"
        },
        "brand_generic_name": {
          "type": "string",
          "description": "药品通用名",
          "example": "甲氨蝶呤皮下注射液"
        },
        "therapeutic_area": {
          "type": "string",
          "description": "治疗领域",
          "example": "风湿免疫"
        },
        "monitoring_period": {
          "type": "object",
          "properties": {
            "start": {"type": "string", "format": "date", "example": "2026-06-01"},
            "end": {"type": "string", "format": "date", "example": "2026-06-30"}
          }
        },
        "platforms": {
          "type": "array",
          "items": {"type": "string"},
          "description": "监测的AI平台列表",
          "example": ["豆包", "千问", "DeepSeek", "元宝", "Kimi", "文心"]
        },
        "query_count": {
          "type": "integer",
          "description": "提问总数",
          "example": 150
        },
        "node_count": {
          "type": "integer",
          "description": "采集节点数",
          "example": 1000
        },
        "collection_method": {
          "type": "string",
          "enum": ["web", "app", "web+app"],
          "description": "采集方式",
          "example": "web+app"
        },
        "export_timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "数据导出时间",
          "example": "2026-07-01T10:00:00Z"
        },
        "platform_version": {
          "type": "object",
          "description": "各AI平台版本信息",
          "additionalProperties": {"type": "string"}
        }
      }
    },

    "golden_truth": {
      "type": "object",
      "description": "药品核心事实（用于合规诊断的校验基准）",
      "properties": {
        "indication": {
          "type": "string",
          "description": "适应症原文（直接复制说明书）",
          "example": "用于成人中重度类风湿关节炎"
        },
        "dosage": {
          "type": "string",
          "description": "用法用量原文",
          "example": "皮下注射，每周一次，初始剂量7.5mg"
        },
        "contraindication": {
          "type": "string",
          "description": "禁忌原文",
          "example": "孕妇禁用，严重肝肾功能不全者禁用"
        },
        "adverse_reaction": {
          "type": "string",
          "description": "不良反应原文",
          "example": "常见恶心、口腔溃疡、肝酶升高"
        },
        "mechanism": {
          "type": "string",
          "description": "作用机制原文",
          "example": "叶酸代谢拮抗剂，抑制二氢叶酸还原酶"
        },
        "special_warnings": {
          "type": "string",
          "description": "特殊警告/黑框警告",
          "example": "用药期间需监测肝功能和血常规"
        }
      }
    },

    "competitors": {
      "type": "array",
      "description": "竞品列表",
      "items": {
        "type": "object",
        "properties": {
          "competitor_name": {"type": "string", "example": "来氟米特"},
          "competitor_generic_name": {"type": "string", "example": "来氟米特片"},
          "relation": {
            "type": "string",
            "enum": ["direct", "indirect", "substitute"],
            "description": "竞品关系类型：直接竞品/间接竞品/替代品"
          }
        }
      }
    },

    "semantic_groups": {
      "type": "array",
      "description": "语义群监测结果（核心数据）",
      "items": {
        "type": "object",
        "required": ["group_id", "query_text", "results"],
        "properties": {
          "group_id": {
            "type": "string",
            "description": "语义群ID",
            "example": "SG-001"
          },
          "query_text": {
            "type": "string",
            "description": "原始提问文本",
            "example": "甲氨蝶呤治疗类风湿关节炎效果怎么样？"
          },
          "query_variants": {
            "type": "array",
            "items": {"type": "string"},
            "description": "该语义群的长尾变体提问",
            "example": ["MTX治类风湿好吗", "甲氨蝶呤疗效如何", "美泰彤效果怎么样"]
          },
          "journey_stage": {
            "type": "string",
            "enum": ["风险暴露", "症状感知", "首次就诊", "确诊", "治疗决策", "处方选择", "用药启动", "剂量调整", "疗效评估", "不良反应处理", "长期管理", "停药/换药"],
            "description": "患者旅程12阶段定位"
          },
          "semantic_level": {
            "type": "string",
            "enum": ["L1", "L2", "L3", "L4", "L5"],
            "description": "五层语义模型层级"
          },
          "questioner_identity": {
            "type": "string",
            "enum": ["patient", "family", "hcp", "healthy", "unknown"],
            "description": "提问者身份"
          },
          "results": {
            "type": "array",
            "description": "各AI平台的回答结果",
            "items": {
              "type": "object",
              "required": ["platform", "raw_response"],
              "properties": {
                "platform": {
                  "type": "string",
                  "description": "AI平台名称",
                  "example": "豆包"
                },
                "collection_terminal": {
                  "type": "string",
                  "enum": ["web", "app"],
                  "description": "采集终端"
                },
                "collection_timestamp": {
                  "type": "string",
                  "format": "date-time",
                  "description": "采集时间"
                },
                "raw_response": {
                  "type": "string",
                  "description": "AI平台原始回答全文"
                },
                "brand_mentioned": {
                  "type": "boolean",
                  "description": "品牌是否被提及"
                },
                "mention_position": {
                  "type": "integer",
                  "description": "品牌在回答中的提及位置（字符偏移量）",
                  "minimum": 0
                },
                "mention_segment_rank": {
                  "type": "integer",
                  "description": "品牌在回答中的段落位置（1=第一段）",
                  "minimum": 1
                },
                "mention_context": {
                  "type": "string",
                  "enum": ["recommendation", "listing", "comparison", "caution", "negative"],
                  "description": "提及上下文类型：推荐/列举/对比/警示/负面"
                },
                "recommendation_rank": {
                  "type": "integer",
                  "description": "在推荐列表中的排名（0=未推荐）",
                  "minimum": 0
                },
                "recommendation_tone": {
                  "type": "string",
                  "enum": ["strong", "weak", "neutral", "cautious", "none"],
                  "description": "推荐语气：强推荐/弱推荐/中性提及/谨慎/未推荐"
                },
                "recommendation_condition": {
                  "type": "string",
                  "description": "推荐条件描述",
                  "example": "一线治疗，适用于中重度活动期"
                },
                "cited_sources": {
                  "type": "array",
                  "description": "AI回答中引用的信源",
                  "items": {
                    "type": "object",
                    "properties": {
                      "source_type": {
                        "type": "string",
                        "enum": ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "unknown"],
                        "description": "信源分类（S1-S8传统信源/A1-A10 AI平台信源）"
                      },
                      "source_name": {"type": "string", "example": "中华风湿病学杂志"},
                      "source_url": {"type": "string", "format": "uri"},
                      "credibility_tier": {
                        "type": "string",
                        "enum": ["A", "B", "C"],
                        "description": "可信度分级"
                      },
                      "controllability": {
                        "type": "string",
                        "enum": ["controllable", "semi-controllable", "uncontrollable"],
                        "description": "品牌可控性：可控/半可控/不可控"
                      }
                    }
                  }
                },
                "compliance_check": {
                  "type": "object",
                  "description": "合规诊断数据",
                  "properties": {
                    "indication_accuracy": {
                      "type": "boolean",
                      "description": "适应症描述是否准确"
                    },
                    "dosage_accuracy": {
                      "type": "boolean",
                      "description": "用法用量是否准确"
                    },
                    "contraindication_accuracy": {
                      "type": "boolean",
                      "description": "禁忌描述是否准确"
                    },
                    "adverse_reaction_accuracy": {
                      "type": "boolean",
                      "description": "不良反应描述是否准确"
                    },
                    "prohibited_terms": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "检出的禁用词汇",
                      "example": ["根治", "最好", "唯一"]
                    },
                    "off_label_hint": {
                      "type": "boolean",
                      "description": "是否暗示超适应症使用"
                    },
                    "risk_level": {
                      "type": "string",
                      "enum": ["green", "yellow", "red"],
                      "description": "合规风险等级"
                    },
                    "risk_details": {
                      "type": "string",
                      "description": "风险详情描述"
                    }
                  }
                },
                "core_message_delivery": {
                  "type": "object",
                  "description": "语义适配诊断数据",
                  "properties": {
                    "delivered": {
                      "type": "boolean",
                      "description": "核心信息是否被传达"
                    },
                    "accuracy": {
                      "type": "number",
                      "minimum": 0,
                      "maximum": 1,
                      "description": "传达准确度（0-1）"
                    },
                    "deviation_type": {
                      "type": "string",
                      "enum": ["omission", "distortion", "outdated", "confusion", "none"],
                      "description": "偏差类型：遗漏/扭曲/过时/混淆/无偏差"
                    },
                    "deviation_detail": {
                      "type": "string",
                      "description": "偏差详情"
                    }
                  }
                },
                "competitor_mentions": {
                  "type": "array",
                  "description": "回答中提及的竞品",
                  "items": {
                    "type": "object",
                    "properties": {
                      "competitor_name": {"type": "string"},
                      "mention_rank": {"type": "integer"},
                      "mention_tone": {"type": "string"}
                    }
                  }
                }
              }
            }
          }
        }
      }
    },

    "competitor_data": {
      "type": "array",
      "description": "竞品汇总数据（用于竞品对标诊断）",
      "items": {
        "type": "object",
        "properties": {
          "competitor_name": {"type": "string"},
          "mention_rate": {"type": "number", "description": "提及率"},
          "recommendation_rate": {"type": "number", "description": "推荐率"},
          "avg_rank": {"type": "number", "description": "平均推荐排名"},
          "top_sources": {
            "type": "array",
            "items": {"type": "object"},
            "description": "主要引用信源"
          },
          "platform_performance": {
            "type": "object",
            "description": "分平台表现",
            "additionalProperties": {"type": "number"}
          }
        }
      }
    },

    "previous_baseline": {
      "type": "object",
      "description": "上期基线数据（用于趋势对比，选填）",
      "properties": {
        "previous_period": {"type": "string"},
        "health_score": {"type": "number"},
        "dimension_scores": {
          "type": "object",
          "properties": {
            "visibility": {"type": "number"},
            "recommendation": {"type": "number"},
            "source": {"type": "number"},
            "competitor": {"type": "number"},
            "compliance": {"type": "number"},
            "semantic_fit": {"type": "number"}
          }
        }
      }
    }
  }
}
```

## Excel导入映射规则

当百通GEO平台以Excel导出时，按以下规则映射：

| Excel列名 | JSON字段 | 说明 |
|-----------|---------|------|
| 药品名称 | metadata.brand_name | |
| 监测开始日期 | metadata.monitoring_period.start | |
| 监测结束日期 | metadata.monitoring_period.end | |
| AI平台 | semantic_groups[].results[].platform | |
| 原始提问 | semantic_groups[].query_text | |
| AI回答原文 | semantic_groups[].results[].raw_response | |
| 品牌是否提及 | semantic_groups[].results[].brand_mentioned | 是/否 → true/false |
| 提及位置 | semantic_groups[].results[].mention_segment_rank | |
| 推荐排名 | semantic_groups[].results[].recommendation_rank | |
| 引用信源 | semantic_groups[].results[].cited_sources | 分号分隔 |
| 合规风险 | semantic_groups[].results[].compliance_check.risk_level | 红/黄/绿 → red/yellow/green |

## 人工粘贴引导流程

当用户无法提供结构化数据时，技能引导式采集以下最小信息集：

1. 药品名称 + 适应症
2. 监测的AI平台（至少3个）
3. 每个平台至少3条AI原始回答（粘贴文本）
4. Golden Truth（说明书核心信息）
5. 竞品名称（至少1个）

基于最小信息集，技能自动推断其余字段并标注「推断」标记。
