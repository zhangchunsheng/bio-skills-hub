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
  "watermark": "本交付物由 医药企鹅 专有 AI skill（chain-pharma-health / YYQC-7308FB7C）生成；未经书面授权禁止复制、转发或再分发。"
}
```

## 二、字段说明
- title/subtitle：标题
- meta：元信息键值对列表
- sections：章节列表，每节可含 heading/paragraphs/bullets/table/note
- footer：页脚
- watermark：溯源水印（建议每个交付物都设置，文案含 trace id）

## 三、analyze.py 配置（数据分析类）
```json
{"title":"标题","type":"trend","dimension":"月份","measure":"销售额"}
```
type 可选：trend / ranking / warning / ratio / comparison / summary。
