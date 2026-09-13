# 文献数据源与访问方式

本文件列出药学科研常见文献源及其可程序化/可检索的访问方式，供 skill 在"追踪第一线"与"文献检索"两种任务中选用。

## 1. PubMed / MEDLINE（英文核心，首选）

- 覆盖范围： biomedical 与生命科学，含药学、临床药理、药物治疗、药物警戒。
- 免费、无需登录即可用 E-utilities 程序化检索（见 `scripts/pubmed_search.py`）。
- 关键能力：
  - **MeSH 主题词**检索（如 `"Drug-Related Side Effects and Adverse Reactions"[MeSH]`）。
  - **Filters**：文献类型（`Clinical Trial`, `Randomized Controlled Trial`, `Review`, `Meta-Analysis`）、出版日期（`pdat`）、物种（`"Humans"[MeSH]`）、年龄组、语种。
  - **PubMed Central (PMC)** 提供大量开放全文。
- 访问方式：优先调用 `scripts/pubmed_search.py` 获取结构化结果（标题/作者/期刊/年/摘要/DOI/Mesh/文献类型）。

## 2. Web of Science / Scopus（引文索引，影响力与演进）

- 强项：被引频次、期刊影响因子、课题演进脉络、高被引论文识别。
- 限制：多为机构订阅，通常无法程序化直连；用 **WebSearch / WebFetch** 辅助定位高被引与综述，并交叉验证。
- 用法：在给出"研究热点与趋势"或"立项依据"时，用 Web of Science 的被引/高被引信息补充影响力判断；注明"据 WoS 被引"而非凭空给影响因子。

## 3. CNKI 中国知网（中文核心、指南、中药、学位论文）

- 强项：中文临床指南、中药/天然药物、医院药学实践、学位论文、基金立项。
- 限制：反爬严格，无稳定公开 API；用 **WebSearch / WebFetch** 检索，检索式示例：`site:cnki.net "抗肿瘤药物" "个体化用药"` 或直接在 cnki.net 检索页查询。
- 注意：中文文献需区分"核心期刊/CSCD/科技核心"与普刊，标注来源质量。

## 4. bioRxiv / medRxiv 等预印本平台（前沿、未审稿）

- 强项：最早披露未发表成果，追踪"第一线"动态。
- 风险（务必提示用户）：**未经同行评议**，结论可能变更或被撤稿。
- 用法：在"前沿动态速递"中可纳入预印本，但必须明确标注 `[预印本·未评议]`，并提示"结论待同行评议确认"。

## 5. 其他有价值的源

- **ClinicalTrials.gov**：在研/已结临床试验方案与结果，支撑药物治疗与 RCT 证据。
- **Cochrane Library**：系统评价与 Meta 分析，循证总结的金标准来源。
- **FDA / EMA / NMPA 药品说明书与审评报告**：药物警戒、适应症、不良反应的权威依据。
- **指南库**：NICE、WHO、中华医学会/药典委员会指南。

## 访问方式决策树

1. 英文、需结构化批量 → `scripts/pubmed_search.py`。
2. 中文、指南、中药 → WebSearch/WebFetch + CNKI。
3. 前沿未发表 → bioRxiv/medRxiv（标注预印本）。
4. 影响力/被引/趋势 → Web of Science/Scopus（WebSearch/WebFetch 辅助）。
5. 系统评价金标准 → Cochrane Library（WebSearch/WebFetch）。

## 严谨性约束（贯穿所有源）

- 每条结论必须可回溯到具体文献（PMID / DOI / 标题+期刊+年）。
- 预印本与已发表文献必须区分呈现。
- 无法核实的数据（如影响因子具体数值）宁可说明"需以官方最新发布为准"，不得编造。
