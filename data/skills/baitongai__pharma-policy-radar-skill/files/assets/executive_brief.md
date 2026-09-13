# 医药政策雷达 · 高管简报

> **生成时间**：{{ generated_at }}
> **监测周期**：{{ date_start }} 至 {{ date_end }}
> **覆盖范围**：{{ provinces }}

---

## ⚠️ 红色预警（需立即决策）

{{#if red_policies}}
{{#each red_policies}}
### {{ title }}
- **发布机构**：{{ agency_name }} | **日期**：{{ date }}
- **风险等级**：🔴 {{ risk_score }}/25
- **战略影响**：{{ executive_impact }}
- **建议决策**：{{ executive_decision }}
- **时间窗口**：{{ time_window }}

{{/each}}
{{else}}
✅ 本期无红色预警政策，常规监控正常。
{{/if}}

---

## 📊 本期概览

| 指标 | 数值 |
|------|------|
| 新增政策 | {{ final_count }} 条 |
| 🔴 红色预警 | {{ red_count }} 条 |
| 🟡 黄色关注 | {{ yellow_count }} 条 |
| 🟢 绿色跟踪 | {{ green_count }} 条 |
| 涉及省份 | {{ affected_provinces_count }} 个 |

---

## 🔑 关键趋势

{{ key_trends }}

---

## 📋 需关注的TOP3

1. **{{ top_policy_1.title }}** — {{ top_policy_1.one_liner }}
2. **{{ top_policy_2.title }}** — {{ top_policy_2.one_liner }}
3. **{{ top_policy_3.title }}** — {{ top_policy_3.one_liner }}

---

*AI生成报告，仅供参考，非法律意见*
