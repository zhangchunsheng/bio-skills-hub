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
  "watermark": "本交付物由 医药企鹅 专有 AI skill（pharma-rd-qa / YYQ-2DC24B2C）生成；未经书面授权禁止复制、转发或再分发。"
}
```

> **强制水印**：所有交付物必须在 spec 中带 `watermark` 字段（见上），渲染器会将其写入 md/html/docx 末尾，用于溯源。请勿删除。

> 本 skill 溯源标识（trace id）：`YYQ-2DC24B2C`

## 二、各场景产出模板
### 偏差原因分析（交付物：偏差/CAPA报告(.md)）
- 操作方式：描述偏差现象，AI推理可能根本原因和CAPA方案
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

### GMP法规查询（交付物：GMP条款检索(.md)）
- 操作方式：描述检查场景，AI检索GMP相关条款和检查要点
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

### 供应商审计报告（交付物：供应商评估报告(.docx)）
- 操作方式：上传审计记录，自动生成供应商评估报告
- 建议章节：
  1. 背景/目标
  2. 核心内容（按操作方式展开，可用表格/要点）
  3. 结论与下一步/风险提示

## 三、analyze.py 配置示例
### type=summary
```json
{
  "title": "质量管理与合规-summary分析",
  "type": "summary",
  "dimension": "维度列名",
  "measure": "数值列名"
}
```

### type=ranking
```json
{
  "title": "质量管理与合规-ranking分析",
  "type": "ranking",
  "dimension": "维度列名",
  "measure": "数值列名",
  "top_n": 5
}
```

