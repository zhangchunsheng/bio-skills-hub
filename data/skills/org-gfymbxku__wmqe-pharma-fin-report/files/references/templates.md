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
  "footer": "页脚",
  "watermark": "本交付物由 医药企鹅 专有 AI skill（pharma-fin-report / YYQ-E8EA774D）生成；未经书面授权禁止复制、转发或再分发。"
}
```

> **强制水印**：所有交付物必须在 spec 中带 `watermark` 字段（见上），渲染器会将其写入 md/html/docx 末尾，用于溯源。请勿删除。

> 本 skill 溯源标识（trace id）：`YYQ-E8EA774D`

## 二、各场景产出模板
### 财务分析报告（交付物：财务分析报告(.docx)）
- 操作方式：上传财务报表，自动生成同比环比、成本结构、盈利能力分析
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

### 研发成本分析（交付物：研发成本分析(.html)）
- 操作方式：输入各项目研发支出，自动分析投入产出比和预算偏差
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

### 两票制影响分析（交付物：两票制影响分析(.docx)）
- 操作方式：上传销售数据，AI分析两票制对利润和现金流的影响
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

## 三、analyze.py 配置示例
### type=summary
```json
{
  "title": "报表与分析-summary分析",
  "type": "summary",
  "dimension": "维度列名",
  "measure": "数值列名"
}
```

### type=ratio
```json
{
  "title": "报表与分析-ratio分析",
  "type": "ratio",
  "dimension": "维度列名",
  "measure": "数值列名",
  "measure2": "数值列名2",
  "ratio_mode": "share"
}
```

### type=comparison
```json
{
  "title": "报表与分析-comparison分析",
  "type": "comparison",
  "dimension": "维度列名",
  "measure": "数值列名",
  "measure2": "数值列名2"
}
```

