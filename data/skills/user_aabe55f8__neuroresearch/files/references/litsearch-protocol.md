# 文献检索自包含协议（内置，无需外部技能）

本文件使本技能在**不依赖 `nature-academic-search` 等外部技能**的情况下，也能完成可复现的文献检索。若环境已安装 `nature-academic-search`，可优先调用它作加速器；否则严格按本协议执行。

## 一、检索源（按优先级）

| 源 | 用途 | 直接访问方式 |
|----|------|--------------|
| **PubMed** | 生物医学核心，首选 | WebSearch / WebFetch 直搜；或 E-utilities API（见下） |
| **Europe PMC** | 含 PubMed + PMC + 预印本，可 API | `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=...&format=json` |
| **bioRxiv / medRxiv** | 预印本，抢先获取 | 站点检索；Europe PMC 亦可覆盖 |
| **Google Scholar** | 补充、引文追踪 | WebSearch |
| **arXiv** | 计算/数学建模/理论神经科学 | `https://arxiv.org/search/` |
| **CNKI / 万方 / 维普** | 中文文献（如需中文产出） | 站点检索（机构权限） |

> 核心原则：**PubMed 为主源**，其余作补充与去重。所有检索必须可复现（保存检索式与日期）。

## 二、构造检索式

1. 从 `domain-lexicon.md` 取「疾病 × 机制 × 模型 × 方法」四维检索词。
2. 组合策略：
   - **MeSH + 自由词**：`"Alzheimer Disease"[MeSH] AND ("microglia"[Title/Abstract] OR "microglial"[Title/Abstract])`
   - **字段限定**：`[Title/Abstract]`、`[MeSH Terms]`、`[Author]`、`[Journal]`、`[Publication Date]`。
   - **布尔**：`AND` / `OR` / `NOT`；短语用双引号；截词用 `*`（`inflammat*`）。
3. 多源并行：同一概念换用不同源的检索语法（PubMed 用 MeSH，Europe PMC 用通用关键词）。

## 三、直接用 API 检索（无外部技能时的标准做法）

### PubMed E-utilities（最可靠，无需 key，限流 3 req/s）
```text
# 1) 按关键词搜索，返回 PMID 列表
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=50&term=Alzheimer+AND+microglia+AND+2018:2026[Publication+Date]

# 2) 用 PMID 拉取摘要/元数据（换 <PMID>）
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=<PMID>&rettype=abstract&retmode=text

# 3) 用 PMID 拉结构化摘要（换 <PMID>）
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<PMID>&retmode=json
```

### Europe PMC REST
```text
# 按 DOI 查
https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41593-024-01600-0&format=json

# 按 PMID 查
https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:35140389&format=json

# 关键词搜索
https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=microglia%20Alzheimer&format=json&pageSize=50
```

> 可用 WebFetch 直接请求上述 URL 获取 JSON/文本；WebFetch 会处理并提取结构化信息。（若环境有联网工具更佳，但 WebFetch 已足够。）

## 四、筛选与 PRISMA 流程

1. **记录每个检索式**（含源、日期、返回数）——满足 PRISMA 可复现。
2. **去重**：合并多源结果，按 PMID/DOI 去重。
3. **一轮筛选**：标题 + 摘要，排除明显无关。
4. **二轮筛选**：全文，按纳入/排除标准。
5. **流程图**：检索数 → 去重 → 初筛排除 → 全文排除 → 最终纳入。
6. 用 PRISMA 2020 流程图呈现（可用 Python matplotlib 或手动绘制）。

## 五、获取并保存 PMID / DOI

- 每条纳入文献必须记录：**作者 / 年 / 期刊 / 卷(期) / 页码 / PMID / DOI**。
- PMID 来自 PubMed 记录；DOI 来自 Crossref 或期刊页。
- Crossref 按 DOI 取元数据（可选校验）：`https://api.crossref.org/works/<doi>`。

## 六、知识卡片（每篇纳入文献）

```
# 文献卡片
- 标题：
- 作者/年份/期刊：
- PMID/DOI：
- 研究类型：动物/临床/体外/生信/综述
- 模型/方法：
- 主要发现：
- 机制关键词：
- 证据等级：高/中/低
- 与我的研究的相关性：
    - 可借鉴的方法：
```

## 七、常见检索盲区与排错（重要）

- **盲区1：工具名锚定漏检。** 若检索式硬性要求出现某药物名（如 PLX5622、PLX3397），会系统性漏掉“使用该工具但不在标题/摘要提名药”的顶刊论文（PubMed esearch 默认只搜 Title/Abstract/MeSH，不搜全文）。对策：除工具名检索外，必须追加**不绑药名的概念基线检索**，例如 `microglia AND (TBI OR neurotrauma) AND (repopulation OR turnover OR rejuvenation OR replacement)`、`IL-6 trans-signaling AND microglia AND (brain injury OR repair)`。
- **盲区2：机制词单一。** 仅用“depletion（耗竭）”会漏掉“repopulation / turnover / replacement / rejuvenation / renewal”等相邻但用词不同的范式。对策：机制维度同时覆盖“清除”与“重编程/再殖”两套词表。
- **盲区3：先入为主早停。** 找到看似匹配的候选（如误把 Nat Commun 当 Cell）后便停止检索，会错过真正目标。对策：当候选与用户描述（期刊/年份/模型）不完全吻合时，放宽关键词重试，必要时用 Europe PMC 全字段检索兜底。
- **核对清单：** 每篇纳入文献须逐条用 esummary/efetch 核验 PMID/DOI/作者/卷页，禁止凭记忆填入。

## 八、对抗式检索视角（落到检索式，配合 literature-review.md §七）

> 把"主流视角"之外的 4 个对抗视角转成可执行检索式，避免综述确认偏误。每个视角独立跑、宽→窄；合并后查盲区（见 §七 7.2）。

| 视角 | 检索式要点（PubMed/Europe PMC 语法） |
|------|--------------------------------------|
| **主流学派** | 标准 `疾病[MeSH] AND 机制 AND 模型`（见 §二） |
| **批评者（反驳/阴性）** | 主流式 `NOT (limitation OR controversy OR failed OR negative OR null)`；并单独搜 `"分子X" AND (controversy OR contradictory OR no effect OR failed)` |
| **相邻学科** | 跨疾病借词：`(microglia OR astrocyte) AND (TBI OR stroke OR Alzheimer) AND (pyroptosis OR lysosome)` |
| **方法学（测量争议）** | `(分子X OR 通路Y) AND (meta-analysis OR systematic review OR bias OR heterogeneity OR reproducibility)` |
| **转化与政策** | `(分子X OR 通路Y) AND (clinical trial OR guideline OR FDA OR NMPA OR translational)` |

> 提示：阴性/反驳性结果常未被 MeSH 标引，须用自由词 + Europe PMC 全字段检索兜底；不要因"首轮像样候选"早停（盲区3）。

## 九、生物医学证据标准（检索时即标注，配合 literature-review.md §七 7.3）

纳入文献卡片（§六）的"证据等级：高/中/低"细化为**证据类型**字段，便于综述按权重引用：

- **人 RCT / 队列** > **非人灵长/大动物** > **啮齿/小动物体内** > **体外** > **纯生信关联（假说生成级）**
- 写入卡片时追加一行：`证据类型：<上表一类>；n=；物种=；设计=`
- 生信（RNA-seq/scRNA-seq/GO-KEGG 富集）一律标 `假说生成级`，禁止在综述中当机制验证引用。
