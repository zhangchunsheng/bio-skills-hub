# 渲染 spec 与场景模板

## 一、render.py spec 结构
```json
{
  "title": "示例报告",
  "subtitle": "可选",
  "meta": [
    [
      "字段",
      "值"
    ]
  ],
  "sections": [
    {
      "heading": "章节",
      "paragraphs": [
        "段落"
      ],
      "bullets": [
        "要点"
      ],
      "table": {
        "headers": [
          "列1",
          "列2"
        ],
        "rows": [
          [
            "a",
            "b"
          ]
        ]
      },
      "note": "提示"
    }
  ],
  "footer": "页脚"
}
```

## 二、各场景产出模板
### 销售报表解读（交付物：销售分析看板(.html/.docx)）
- 操作方式：上传销售数据，自动分析区域销售趋势、品种贡献度、客户分布
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

### 周报/月报生成（交付物：销售周/月报(.docx)）
- 操作方式：汇总本周客户拜访情况，自动生成结构化销售周报
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

### 库存预警分析（交付物：库存预警清单(.md)）
- 操作方式：上传库存数据，自动识别滞销品种和缺货风险
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

## 三、analyze.py 配置示例
### type=trend
```json
{
  "title": "数据分析-trend分析",
  "type": "trend",
  "dimension": "维度列名",
  "measure": "数值列名"
}
```

### type=ranking
```json
{
  "title": "数据分析-ranking分析",
  "type": "ranking",
  "dimension": "维度列名",
  "measure": "数值列名",
  "top_n": 5
}
```

### type=warning
```json
{
  "title": "数据分析-warning分析",
  "type": "warning",
  "dimension": "维度列名",
  "measure": "数值列名",
  "threshold": 100
}
```

