# 输出格式规范与展示模板

## 用户偏好

- **默认数量**：5 篇
- **摘要语言**：英文原标题 + 中文概括摘要要点
- **必含字段**：PMID、DOI、MeSH 主题词、文献类型标签
- **展示结构**：先表格概览，再逐篇详情展开

---

## PubMed 文献检索输出格式

### 第一步：概览表格

先以表格展示所有检索结果的概览，表格字段固定为：

| # | PMID | 英文标题 | 第一作者 | 期刊 | 年份 | DOI | 文献类型 |
|---|------|----------|----------|------|------|------|----------|
| 1 | 38123456 | Pembrolizumab plus chemotherapy for metastatic... | Smith J | J Clin Oncol | 2024 | 10.1200/JCO.2024.001 | Clinical Trial |
| 2 | 38098765 | Efficacy of osimertinib in EGFR-mutated NSCLC... | Lee K | Lancet Oncol | 2024 | 10.1016/S1470-2045(24)00123 | Clinical Trial |
| 3 | 38054321 | Combined immunotherapy in melanoma: a phase III... | Chen L | N Engl J Med | 2024 | 10.1056/NEJMoa2401234 | Clinical Trial |

**表格规则**：
- 标题过长时截断并加 `...`（表格仅展示概览，完整标题在详情中）
- DOI 显示完整编号（方便直接复制使用）
- 文献类型取主要类型：Clinical Trial / Review / Systematic Review / Meta-Analysis / Case Reports / Clinical Trial Protocol / Guideline
- 如果一篇文献有多个类型，用 `/` 分隔（如 `Clinical Trial/Review`）
- **注意**：MeSH 主题词仅在 abstract 模式（默认）下可用；summary 模式不返回 MeSH 词

### 第二步：逐篇详情展开

在表格下方，逐篇展开详细信息。每篇文献格式如下：

---

**1. Pembrolizumab plus chemotherapy for metastatic non-small cell lung cancer: 5-year outcomes**

- **PMID**: 38123456
- **作者**: Smith J, Doe A, Lee K, et al.
- **期刊**: Journal of Clinical Oncology, 2024 Jan 15
- **DOI**: 10.1200/JCO.2024.001
- **文献类型**: Clinical Trial
- **MeSH 主题词**: Lung Neoplasms/drug therapy; Carcinoma, Non-Small-Cell Lung; Pembrolizumab; Chemotherapy, Adjuvant
- **链接**: https://pubmed.ncbi.nlm.nih.gov/38123456/

**中文摘要**：

该研究评估了帕博利珠单抗联合化疗在转移性非小细胞肺癌中的疗效。这是一项随机双盲 III 期临床试验，共入组 616 例患者。结果显示，联合治疗组的中位无进展生存期显著优于单纯化疗组（15.2 个月 vs 9.8 个月，HR=0.62，P<0.001）。5 年随访数据显示，联合治疗组总生存率达 32.5%。安全性方面，3-4 级不良事件发生率为 35%，与既往报道一致。结论：帕博利珠单抗联合化疗可作为转移性非小细胞肺癌的一线标准治疗方案。

---

### 详情展开规则

1. **标题**：保留英文原文，完整不截断
2. **中文摘要**：
   - 不是逐句翻译，而是用中文概括核心要点
   - 包含：研究目的 → 方法学（试验类型、入组人数）→ 主要结果（关键数据、P值、HR等）→ 结论
   - 长度控制在 100-200 字，信息密度高
   - 关键数据保留原始数字（不翻译）
3. **MeSH 主题词**：用分号 `;` 分隔，`/` 后为限定词
4. **文献类型**：标注完整类型列表

---

## 会议摘要输出格式

### 按会议分组展示

按会议名称分组，组内按专场 / 摘要编号排序：

### ASCO 2024

**概览表格**：

| 摘要编号 | 英文标题 | 第一作者 | 专场 | 年份 |
|----------|----------|----------|------|------|
| LBA8500 | KEYNOTE-671: Adjuvant pembrolizumab... | Wakelee H | Plenary | 2024 |
| 8501 | Neoadjuvant nivolumab in resectable NSCLC... | Smith J | Oral | 2024 |
| 8520 | Circulating tumor DNA dynamics in... | Chen L | Poster | 2024 |

**详情展开**：

---

**LBA8500. KEYNOTE-671: Adjuvant pembrolizumab after neoadjuvant chemotherapy and resection in early-stage NSCLC**

- **会议**: ASCO 2024
- **专场**: Plenary Session
- **摘要编号**: LBA8500
- **作者**: Wakelee H, Liberman M, Kato T, et al.
- **链接**: meetinglibrary.asco.org/record/...

**中文摘要**：

该研究为 KEYNOTE-671 III 期临床试验，评估了新辅助化疗联合帕博利珠单抗后辅助治疗在可切除早期 NSCLC 中的疗效。共入组 797 例患者，结果显示联合治疗组 EFS 显著改善（HR=0.58，P<0.001），3 年 EFS 率为 62% vs 40.6%。OS 数据也显示出显著获益。安全性可管理，未发现新的安全信号。该方案有望成为可切除 NSCLC 的新标准治疗。

---

### ESMO 2024

**概览表格**：

| 摘要编号 | 英文标题 | 第一作者 | 专场 | 年份 |
|----------|----------|----------|------|------|
| LBA1 | CheckMate 9LA: 5-year follow-up... | Paz-Ares L | LBA | 2024 |

### CSCO 2024

CSCO 摘要以中文为主，格式略有不同：

| 摘要编号 | 中文标题 | 讲者 | 专场 | 年份 |
|----------|----------|------|------|------|
| N/A | 肺癌免疫治疗新进展 | 张三 | 专题报告 | 2024 |
| N/A | 胃癌靶向治疗最新数据 | 李四 | 专题报告 | 2024 |

---

## 无结果时的提示格式

### PubMed 无结果

```
未在 PubMed 中找到相关结果。建议：

1. 尝试更宽泛的关键词（如用 "lung cancer" 替代 "non-small cell lung cancer"）
2. 检查拼写（如药物名、作者名）
3. 扩大日期范围或移除日期限制
4. 使用 MeSH 词替代自由词（如 "Lung Neoplasms"[MeSH] 替代 lung cancer[Title/Abstract]）
5. 尝试英文关键词（PubMed 以英文文献为主）
6. 移除部分筛选条件（如 Publication Type 限制）
```

### 会议摘要无结果

```
未找到相关会议摘要。建议：

1. 尝试不同的关键词组合
2. 中英文交替搜索（ASCO/ESMO 用英文，CSCO 用中文）
3. 检查年份是否正确——该年份会议可能尚未举行
4. 尝试用药物通用名或试验代号搜索
5. 扩大搜索范围（如同时搜索 ASCO 和 ESMO）
```

---

## 大量结果时的分页提示

```
共找到 1,234 条结果，当前显示第 1-5 条。

如需查看更多结果：
- 告诉我"继续"或"下一页"，获取第 6-10 条
- 缩小查询范围（增加 AND 条件、限定日期范围、指定文献类型）
- 按最新发表日期排序
```

---

## 多源综合检索结果格式

当同时检索 PubMed 和会议摘要时，按来源分区展示：

### PubMed 检索结果

**共找到 45 条，当前显示前 5 条**

[PubMed 概览表格 + 详情]

### 会议摘要检索结果

**ASCO 2024**

[ASCO 摘要列表]

**ESMO 2024**

[ESMO 摘要列表]

**CSCO 2024**

[CSCO 摘要列表]

### 跨来源重复提示

如发现同一研究在多个来源出现：

> 注：KEYNOTE-671 研究同时在 PubMed（PMID: 38123456）和 ASCO 2024（摘要 #LBA8500）中有报告。

---

## 药物/靶点专题综合汇总表

当用户要求全面检索某靶点或某药物的临床进展时，在报告开头展示此汇总表。仅收录有临床结果的品种（I 期及以后），按临床阶段降序排列。

### 小分子药物汇总表

| 品种 | 开发企业 | 最新进展 | 瘤种 | 主要有效性结果 | 主要安全性结果 |
|------|----------|----------|------|----------------|----------------|
| 示例药A | 示例公司 | III 期启动（2026.06） | PDAC一线 | ORR 63.3%, DCR 93.3%, 6mo-PFS 89.3% | ≥3级TRAE 87.1%（血液学），无停药/死亡 |
| 示例药B | 示例公司 | 注册性临床（FDA BTD） | NSCLC | ORR 61%, DCR 89% | ≥3级TRAE 2%，无4-5级 |

### 非小分子模态汇总表（如有）

| 品种/疗法 | 开发企业 | 最新进展 | 瘤种 | 主要有效性结果 | 主要安全性结果 |
|-----------|----------|----------|------|----------------|----------------|
| 示例疫苗 | 示例公司 | I 期 | PDAC辅助 | T细胞应答率84%, RFS显著延长 | grade 1-2注射部位反应 |

### 表格规则

1. **"最新进展"列**：标注最高临床阶段 + 关键监管里程碑（如 FDA BTD / 快速通道 / NMPA IND）+ 日期
2. **"主要有效性结果"列**：ORR / DCR / mPFS / mOS 等核心指标，保留原始数字
3. **"主要安全性结果"列**：≥3级TRAE发生率 + 主要AE类型 + 是否有停药/死亡
4. **排序规则**：III期 > 注册性临床 > II期 > I期（大规模）> I期 > IND
5. 数据来源不同试验、基线不同，不可直接横比，需在表后注明

---

## Word 文档导出格式

当用户要求导出 Word 时，按以下结构生成 `.docx` 文件。

### 封面页

```
检索报告：<主题标题>

检索时间：YYYY-MM-DD
检索范围：<列出所有来源，如 PubMed / ASCO 2026 / AACR 2026 / ESMO 2025 / CSCO 2025 / WebSearch>
检索关键词：<列出所有查询关键词>
时间范围：<如 2023-01-01 至 2026-07-17>
文献数量：PubMed X 篇 / 会议摘要 X 条
检索工具：PubMed E-utilities API / WebSearch / WebFetch
```

### 正文章节结构

1. **综合汇总表**（药物/靶点专题时）— 上述汇总表格式
2. **重点药物/文献详情** — 按重要性排序，每条含：机制、临床数据、关键里程碑、要点概括
3. **会议数据汇总** — 按会议分组，表格含摘要号、药物、瘤种、关键数据、专场
4. **耐药机制与新策略**（如有） — 按机制类型列表
5. **PubMed 核心文献列表** — PMID | DOI | 文献类型 | 英文标题 | 第一作者 | 期刊 | 年份
6. **总结与趋势判断** — 竞争格局、进度排序、疗效对比、关键趋势、中国市场

### 技术要点

- 使用 `python-docx` 库生成
- 表格使用 `doc.add_table()` 创建，设置样式为 'Table Grid'
- 标题用 Heading 样式（Heading 1 / Heading 2）
- 正文用 11pt 宋体（中文）/ Calibri（英文）
- 文件命名：`<主题>_检索报告_YYYYMMDD.docx`
- 保存到项目根目录
