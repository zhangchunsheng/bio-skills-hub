# 医学文献追踪 - 使用示例

## 示例 1：基础关键词检索（一次性）

**用户**：帮我查一下最近关于 GLP-1 受体激动剂对心血管结局影响的最新文献

**Skill 执行**：
1. 参数确认：关键词 "GLP-1 receptor agonist cardiovascular outcome"，期刊范围 Tier 1+2，仅本次，近30天
2. PubMed 检索 → 获取 8 篇
3. WoS 补充检索 → 获取 3 篇
4. 排序筛选 → 取前 12 篇
5. 抓取摘要 → 翻译 → 生成简报
6. 对话展示 + 保存 `GLP1_心血管_文献简报_2026-05-21.md`

---

## 示例 2：按专业领域 + 定期更新

**用户**：我是心内科医生，帮我追踪心衰方向的最新研究，每周一更新，只要顶刊

**Skill 执行**：
1. 参数确认：关键词 "heart failure"，期刊范围仅 Tier 1，每周更新
2. 首次检索生成简报
3. 创建定时任务：`cron "0 8 * * 1"`，prompt 包含完整检索参数
4. 此后每周一早 8 点自动检索 + 生成简报

---

## 示例 3：含国内核心期刊

**用户**：追踪肺癌免疫治疗的最新进展，要包括中华肿瘤杂志，每月更新

**Skill 执行**：
1. 参数确认：关键词 "lung cancer immunotherapy"，期刊范围 Tier 1+2 + 国内核心（中华肿瘤杂志）
2. PubMed 检索 Tier 1+2
3. 国内核心期刊检索（web_search 中华肿瘤杂志官网/知网）
4. 合并排序，取前 15 篇
5. 生成简报 + 创建每月定时任务

---

## 示例 4：紧急关注特定事件

**User**：Any new papers on long COVID treatment in the past week? Just NEJM and Lancet.

**Skill 执行**：
1. 参数确认：关键词 "long COVID treatment / post-COVID condition treatment"，仅 NEJM+Lancet，近7天
2. PubMed 检索：`site:pubmed.ncbi.nlm.nih.gov (long COVID OR post-COVID) AND (N Engl J Med[Journal] OR Lancet[Journal]) AND ("last 7 days"[PDAT])`
3. 筛选 → 翻译 → 输出简报

---

## 输出样例

```
## heart failure 文献简报 | 2026-05-21

> 检索范围：Tier 1 顶级期刊 | 时间：近30天 | 共筛选 12 篇

### 1. 恩格列净对射血分数保留心衰患者长期预后的影响：EMPEROR-Preserved 试验5年随访

- **原文标题**：Empagliflozin and Long-Term Outcomes in Heart Failure with Preserved Ejection Fraction: 5-Year Follow-up of the EMPEROR-Preserved Trial
- **作者**：Anker SD et al., Packer M (Corresponding)
- **期刊**：N Engl J Med | 2026-05-15
- **DOI**：10.1056/NEJMoa2400123
- **摘要原文**：BACKGROUND: Sodium-glucose cotransporter 2 (SGLT2) inhibitors ... METHODS: ... RESULTS: ... CONCLUSIONS: ...
- **中文摘要**：
  背景：SGLT2抑制剂已证实可改善射血分数保留心衰(HFpEF)患者的短期预后，但其长期疗效尚不明确。
  方法：EMPEROR-Preserved试验纳入5988例HFpEF患者，随机分配至恩格列净组或安慰剂组，中位随访5.2年。
  结果：恩格列净组主要复合终点（心血管死亡或心衰住院）风险降低21%（HR 0.79, 95% CI 0.72-0.87, p<0.001），全因死亡风险降低14%（HR 0.86, 95% CI 0.78-0.95, p=0.003）。两组严重不良事件发生率无显著差异。
  结论：恩格列净长期治疗可持续降低HFpEF患者的心血管死亡和心衰住院风险，安全性与短期观察一致。
- **关键结论**：恩格列净对HFpEF患者5年心血管获益持续，HR 0.79 | 证据等级：RCT（多中心双盲，n=5988）

---
```