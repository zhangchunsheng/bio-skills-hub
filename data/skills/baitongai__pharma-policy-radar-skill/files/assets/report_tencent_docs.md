# 医药政策雷达 · 监测报告（腾讯文档版）

> 本模板适配腾讯文档在线协作场景。通过腾讯文档MCP连接器自动创建在线文档。

## 一、执行摘要

- **生成时间**：{{ generated_at }}
- **监测周期**：{{ date_start }} 至 {{ date_end }}
- **覆盖范围**：{{ provinces }}（{{ sources }}）
- **检索统计**：原始 {{ total_raw }} → 有效 {{ final_count }} 条

### 高风险预警

<!-- 红色预警政策在此以表格呈现，便于移动端阅读 -->

| 优先级 | 政策标题 | 发布机构 | 风险分 | 建议动作 |
|--------|---------|---------|--------|---------|
{{#each red_policies}}
| 🔴 高 | {{ title }} | {{ agency_name }} | {{ risk_score }}/25 | {{ risk_action }} |
{{/each}}

### 本期核心发现

{{ executive_summary }}

---

## 二、政策概览

{{#each policies}}

### {{ index }}. {{ title }}

**发布信息**
- 机构：{{ agency_name }}
- 日期：{{ date }}
- 链接：[查看原文]({{ url }})
- 类型：{{ policy_type }} | 紧急度：{{ urgency }}
- 风险：{{ risk_label }}（{{ risk_score }}/25）

**政策要点**
> {{ snippet }}

**四维度影响**

| 维度 | 影响评估 |
|------|---------|
| 药监 | {{ drug_impact }} |
| 医保 | {{ insurance_impact }} |
| 中医药 | {{ tcm_impact }} |
| 卫健委 | {{ health_impact }} |

**行动建议**

| 岗位 | 影响 | 动作 |
|------|------|------|
| 合规 | {{ compliance.what }} → {{ compliance.so_what }} | {{ compliance.now_what }} |
| GA | {{ ga.what }} → {{ ga.so_what }} | {{ ga.now_what }} |
| MA | {{ ma.what }} → {{ ma.so_what }} | {{ ma.now_what }} |
| Mkt | {{ mkt.what }} → {{ mkt.so_what }} | {{ mkt.now_what }} |
| 高管 | {{ exec.what }} → {{ exec.so_what }} | {{ exec.now_what }} |

---

{{/each}}

## 三、趋势研判

| 维度 | 内容 |
|------|------|
| 政策热词 | {{ hot_keywords }} |
| 跨省信号 | {{ cross_province_signals }} |
| 持续跟踪 | {{ tracking_windows }} |

## 四、检索日志

| 检索时间 | 范围 | 原始 | 有效 |
|---------|------|------|------|
| {{ search_time }} | {{ coverage }} | {{ total_raw }} | {{ final_count }} |

---

*本报告由医药政策雷达AI自动生成，仅供参考，不作为法律意见。*
*生成于：{{ generated_at }}*
