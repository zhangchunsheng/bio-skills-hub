# 药讯内容JSON Schema

定义 `scripts/generate_newsletter.py` 的输入JSON结构。所有字段为字符串除非另有说明。

## 顶层结构

```json
{
  "issue": { "year": 2026, "month": 8, "topic": "可选专题标题" },
  "sections": {
    "preface": "...",
    "guideline_updates": [...],
    "safety_alerts": [...],
    "literature": [...],
    "new_drugs": [...]
  }
}
```

## 各栏目字段

### preface（卷首语）

字符串，100-200字。

### guideline_updates（指南更新）

```json
[
  {
    "title": "指南全称（含版本号）",
    "source": "发布机构 + URL",
    "publish_date": "2026-07-15",
    "changes": "关键变更点（2-4条）",
    "impact": "临床影响（与本科室实践相关性）",
    "evidence_level": "A/B/C/D（GRADE或OCEBM）",
    "translation_note": "若为翻译内容，标注'机翻待药师校对'"
  }
]
```

### safety_alerts（药物安全警示）

```json
[
  {
    "title": "警示标题",
    "type": "院内案例/国家通报/FDA警示/EMA警示",
    "drug": "涉及药品（通用名）",
    "case": "案例描述（已脱敏，含年龄性别诊断用药史ADR表现转归）",
    "national_alert": "国家/监管机构通报要点（如有）",
    "risk": "风险机制与高危人群",
    "suggestion": "临床建议（监测/替代/剂量调整）",
    "report_deadline": "上报时限：24h/15d/30d/无需上报"
  }
]
```

### literature（文献速递）

```json
[
  {
    "title": "文献标题",
    "journal": "期刊名",
    "publish_date": "2026-07-20",
    "pmid": "12345678",
    "doi": "10.xxx/xxx",
    "study_type": "RCT/Meta-analysis/队列/病例对照",
    "summary": "研究目的+方法+主要结局+结论（200-300字）",
    "clinical_implication": "对本科室实践的启示",
    "evidence_level": "A/B/C"
  }
]
```

### new_drugs（新药速览）

```json
[
  {
    "name": "通用名（商品名）",
    "class": "药品分类",
    "indication": "适应症",
    "dosage": "用法用量",
    "cautions": "禁忌/注意事项/主要不良反应",
    "insurance": "医保属性（甲类/乙类/自费）",
    "formulary_status": "本院药事会审议状态",
    "key_interaction": "重要相互作用（如有）"
  }
]
```

## 字段约束

- 所有日期格式：YYYY-MM-DD
- 数值字段：纯数字（不加千分位）
- 脱敏字段：case中不得出现真实姓名/住院号/床号/电话
- 可选字段：未提供时省略键，脚本自动跳过该栏目
- 编码：UTF-8（中文参数严禁key=value通过命令行传递）
