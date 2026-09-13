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
  "watermark": "本交付物由 医药企鹅 专有 AI skill（pharma-fin-cost / YYQ-3DB6A235）生成；未经书面授权禁止复制、转发或再分发。"
}
```

> **强制水印**：所有交付物必须在 spec 中带 `watermark` 字段（见上），渲染器会将其写入 md/html/docx 末尾，用于溯源。请勿删除。

> 本 skill 溯源标识（trace id）：`YYQ-3DB6A235`

## 二、各场景产出模板
### 生产成本分析（交付物：成本结构分析(.html)）
- 操作方式：输入成本构成数据，自动分析原料药、人工、制造费用结构
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

### 供应商比价（交付物：比价分析表(.md)）
- 操作方式：上传多家供应商报价，AI自动生成原料药比价分析表
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

### 应收账款管理（交付物：应收预警清单(.md)）
- 操作方式：输入客户账期数据，自动生成逾期预警和催收建议
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

## 三、analyze.py 配置示例
### type=ratio
```json
{
  "title": "成本与资金管理-ratio分析",
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
  "title": "成本与资金管理-comparison分析",
  "type": "comparison",
  "dimension": "维度列名",
  "measure": "数值列名",
  "measure2": "数值列名2"
}
```

### type=warning
```json
{
  "title": "成本与资金管理-warning分析",
  "type": "warning",
  "dimension": "维度列名",
  "measure": "数值列名",
  "threshold": 100
}
```

