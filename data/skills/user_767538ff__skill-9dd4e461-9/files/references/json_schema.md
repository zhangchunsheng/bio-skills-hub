# build_report.py 的 JSON 规格说明

将点评分析结果整理为该 JSON，再调用 `scripts/build_report.py --json <file> --out <report.docx>` 生成报告。

## 字段
| 字段 | 必填 | 说明 |
|---|---|---|
| `title` | 否 | 报告标题，默认「医嘱点评报告（用药合理性评价）」 |
| `review_objects` | 否 | 点评对象字符串（如"蔡XX、高X 等共6份病例"），显示在封面 |
| `review_basis` | 否 | 点评依据（引用真实指南名称），显示在封面 |
| `template_note` | 否 | 模板学习要点段落文本（若用户给了模板病例） |
| `cases` | 是 | 病例数组，每例一个章节 |
| `summary_rows` | 否 | 汇总表数据，4 列：病例 / 主要诊断 / 点评结论 / 主要改进或关注点 |
| `note` | 否 | 文末说明（免责/审慎声明） |

### cases 数组元素
| 字段 | 必填 | 说明 |
|---|---|---|
| `heading` | 是 | 章节标题，如「二、蔡XX（女，45岁，高级别B细胞淋巴瘤，双打击）」 |
| `summary` | 是 | 病例摘要文本 |
| `medications` | 否 | 用药情况字符串数组，每项一条 bullet |
| `reasonable` | 否 | 合理点数组，自动加「（一）合理：」前缀 |
| `concerns` | 否 | 需关注/需纠正点数组，自动加「（二）需关注/需纠正：」前缀 |
| `conclusion` | 是 | 点评结论文本 |

## 示例（单病例最小可用）
```json
{
  "title": "医嘱点评报告（用药合理性评价）",
  "review_objects": "示例病例 共1份",
  "review_basis": "参照《NCCN》《IDSA 粒缺伴发热指南》《ASCO/COSO 肿瘤VTE预防指南》及药品说明书。",
  "template_note": "模板写法：时间线 + 指征 + 剂量 + 监测。",
  "cases": [
    {
      "heading": "二、示例XX（诊断）",
      "summary": "因\"xxx\"于2026-xx-xx入院，xx-xx出院。出院诊断：……",
      "medications": [
        "2026-xx-xx 方案：药物 剂量 d1-3，辅以……",
        "抗感染：……"
      ],
      "reasonable": [
        "方案选择符合 NCCN 推荐；剂量与疗程规范。"
      ],
      "concerns": [
        "某预防用药指征/时限需明确，建议……"
      ],
      "conclusion": "基本合理。主要改进点为……"
    }
  ],
  "summary_rows": [
    ["示例XX", "诊断", "基本合理", "改进点……"]
  ],
  "note": "以上点评基于所提供病历文本，临床决策须结合患者实时体征、检验动态及本院处方集。"
}
```
