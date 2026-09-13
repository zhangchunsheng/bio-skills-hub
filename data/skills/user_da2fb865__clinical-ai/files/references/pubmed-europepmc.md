# 文献检索：PubMed E-utilities 与 Europe PMC fallback

## 目标
每日从 PubMed 选取 AI 相关、高质量的医学文献（按 IF / 引用数筛选），以及从官网公布的 AI 产品公告中选取条目。

## 1. PubMed E-utilities（首选，取候选 + 元数据）
- 检索：`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<QUERY>&retmode=json&retmax=15&datetype=pdat&dfrom=YYYY/MM/DD&dto=YYYY/MM/DD`
  - 例：`(("deep learning" OR "machine learning" OR "artificial intelligence") AND ("diagnosis" OR "medical imaging" OR "clinical"))`
- 取摘要元数据：`efetch.fcgi?db=pubmed&id=<PMID1,PMID2>&retmode=xml`
- **坑**：NCBI 对高频/批量 efetch 会临时限流（返回 Access Denied / 403）。遇到时立即走下方 fallback，不要重试 efetch。

## 2. Europe PMC（fallback，且可一次返回摘要+引用数）
- 主题+日期检索（推荐，对极新文献也可用）：
  `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=(<AI词>) AND (<诊断/影像/临床>) AND FIRST_PDATE:[YYYY-MM-DD TO YYYY-MM-DD] AND SRC:MED&format=json&resultType=core&pageSize=12&sort=P_PDATE_D desc`
  - 返回字段：`pmid`、`title`、`journalInfo.journal.title`、`journalInfo.dateOfPublication`、`doi`、`abstractText`、`citationCount`。
- 按单篇取引用数：`query=EXT_ID:<PMID> AND SRC:MED&format=json&resultType=core`（注意：对**极新**的 ahead-of-print 文章 Europe PMC 尚未建索引，会返回空；此时必须用主题+日期检索）。
- iCite 旧端点已停用（404），不要再调用。

## 3. 质量筛选建议
- IF：PubMed 不返回，用内置「期刊→IF 映射表」近似（摘要里注明「IF 为近似值」）。
- 引用数：Europe PMC `citationCount`（新文多为 0，不作为唯一门槛）。
- 最终按「相关性 + IF + 引用数」综合挑 1 条作为「今日项目」，其余可入库为历史。

## 4. 商业产品条目
- 来自官网 / FDA / NMPA / 厂商新闻稿；`type: "product"`，`pmid` 留空，`clinicalStatus.commercial` 填公司/融资/销售/营收等公开可查证信息。
