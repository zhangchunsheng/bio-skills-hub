═══════════════════════════════════════
# 医药政策雷达 · 监测报告
═══════════════════════════════════════

**生成时间**：{{ generated_at }}
**监测周期**：{{ date_start }} 至 {{ date_end }}
**覆盖范围**：{{ provinces }}（{{ sources }}）
**检索统计**：检索 {{ total_raw }} 条 → 去重过滤后 {{ deduped }} 条 → 有效政策 {{ final_count }} 条

---

## 一、执行摘要

### {{#if red_policies}}
### ⚠️ 本期高风险预警

{{#each red_policies}}
- **{{ title }}** — {{ agency_name }} ({{ risk_score }}/25)
{{/each}}
{{else}}
✅ 本期无红色预警政策。
{{/if}}

### 本期核心发现

{{ executive_summary }}

---

## 二、政策清单概览

| # | 发布机构 | 政策标题 | 日期 | 机构类别 | 紧急度 | 风险 |
|---|---------|---------|------|---------|-------|------|
{{#each policies}}
| {{ index }} | {{ agency_name }} | {{ title }} | {{ date }} | {{ agency_type }} | {{ urgency }} | {{ risk_label }} |
{{/each}}

---

## 三、逐条深度分析

{{#each policies}}

### 政策 #{{ index }}：{{ title }}

- **来源**：{{ agency_name }} | **发布日期**：{{ date }}
- **原文链接**：{{ url }}
- **政策类型**：{{ policy_type }}
- **生效时间**：{{ effective_date }}
- **时限分级**：{{ time_classification }}

#### 3.1 政策要点摘要
> {{ snippet }}

#### 3.2 分维度影响分析

**（A）药监维度**
{{ drug_impact }}

**（B）医保维度**
{{ insurance_impact }}

**（C）中医药维度**
{{ tcm_impact }}

**（D）卫健委维度**
{{ health_impact }}

#### 3.3 分岗位行动建议

| 岗位 | What（影响什么） | So What（影响多大） | Now What（现在做什么） |
|------|-----------------|--------------------|----------------------|
| 合规 | {{ compliance.what }} | {{ compliance.so_what }} | {{ compliance.now_what }} |
| GA | {{ ga.what }} | {{ ga.so_what }} | {{ ga.now_what }} |
| MA | {{ ma.what }} | {{ ma.so_what }} | {{ ma.now_what }} |
| Mkt/PM | {{ mkt.what }} | {{ mkt.so_what }} | {{ mkt.now_what }} |
| 高管 | {{ exec.what }} | {{ exec.so_what }} | {{ exec.now_what }} |

#### 3.4 风险评级
- 影响程度：{{ risk_impact }}/5
- 发生概率：{{ risk_probability }}/5
- 风险等级：**{{ risk_label }}**（{{ risk_score }}/25）
- 建议动作：{{ risk_action }}

---
{{/each}}

## 四、综合趋势研判

- **本周政策热词**：{{ hot_keywords }}
- **跨省政策趋同/差异信号**：{{ cross_province_signals }}
- **需持续跟踪的政策窗口**：{{ tracking_windows }}

---

## 五、检索日志

| 时间 | 覆盖范围 | 原始命中 | 去重移除 | 噪音过滤 | 最终有效 |
|------|---------|---------|---------|---------|---------|
| {{ search_time }} | {{ coverage }} | {{ total_raw }} | -{{ dup_removed }} | -{{ noise_removed }} | {{ final_count }} |

---

**免责声明**

本报告由医药政策雷达AI系统自动生成，信息来源为各政府机构官网公开发布内容。
报告中的影响分析和行动建议仅供参考，不构成法律意见或商业建议。
用户在执行任何商业决策前，应核实原始政策文本并咨询企业内部法务/合规部门。
