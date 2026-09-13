# 现代数据库检索策略

本文件提供中英文数据库、植物分类资源、标准数据库的检索式模板与跨库策略，供设计检索方案时直接套用。

## 一、核心关键词构建（通用步骤）

1. **药材名系列**：中文药名（黄连）、拉丁药材名（Coptidis Rhizoma）、植物学名（Coptis chinensis Franch.）、英文俗名（goldthread / golden thread）
2. **别名系列**：历代别名（王连、支连）、地方名、商品名
3. **民族药名系列**：藏文（ཀེ་རྐེ་མེར་）、威利转写、藏汉音译（如"吉合那保"）
4. **主题维度**：基原（origin/botanical source）、鉴定（identification/authentication）、成分（chemical constituent/berberine）、药理（pharmacology/anti-inflammatory）、质量（quality control）
5. **构建检索词矩阵**：`药物维度 × 主题维度` 交叉，每格为一个检索单元

```
检索词矩阵示例（黄连）:
        基原      鉴定        成分          药理
药名    origin   identification  berberine   pharmacology
黄连    考证      显微鉴别      小檗碱      抗炎
```

## 二、中文学术数据库

### CNKI（中国知网）
- 检索式（专业检索语法）：`(SU='黄连' OR SU='Coptis chinensis') AND (SU='基原' OR SU='考证')`
- 技巧：先用"主题"字段宽检，再用"关键词"精检；利用"引文网络"找核心文献；学位论文库（博硕士）常有详尽综述
- 分类号：中图法 R282（药材学）/ R284（中药化学）/ R285（中药药理学）

### 万方数据
- 检索式：`主题:(黄连 基原 考证)`，支持字段：题名/关键词/摘要/分类号
- 特色：万方学位论文与标准库较全

### 维普期刊
- 检索式：`M=(黄连)*M=(基原)`，M 为主题词
- 特色：回溯年代久，适合查老文献

## 三、英文学术数据库

### PubMed（生物医学）
- 核心语法：`("Coptis chinensis"[MeSH] OR "Coptidis Rhizoma"[Supplementary Concept] OR "Huanglian"[tiab]) AND (pharmacology[sh] OR anti-inflammatory[tiab])`
- 技巧：MeSH 词自动扩展下位词；"Similar articles"功能找相关；filter 限定综述（review）与年限
- 常用 MeSH：`Coptis`、`Berberine`（有效成分）、`Drugs, Chinese Herbal`

### Web of Science（SCI核心合集）
- 检索式：`TS=(("Coptis chinensis" OR "Coptidis Rhizoma") AND (authentication OR identification OR DNA barcoding))`
- 技巧：字段 TS=主题 / TI=标题 / AU=作者；利用"引文报告"（Citation Report）看高被引与趋势；检索结果精炼至 Q1/Q2 分区
- 注意：药材拉丁名拼写变体（Rhizoma Coptidis / Coptidis Rhizoma）须用 OR 并列

### Scopus
- 检索式：`TITLE-ABS-KEY("Coptis chinensis" OR "Rhizoma Coptidis") AND TITLE-ABS-KEY(pharmacolog*)`
- 技巧：通配符 `*` 扩展词干（pharmacolog* 覆盖 pharmacology/pharmacological）；CiteScore 分区筛选

## 四、植物与分类学资源

| 资源 | 网址 | 用途 | 关键操作 |
|------|------|------|----------|
| 中国植物志在线 | frps.iplant.cn | 权威中文分类记载 | 输学名/中文名，查看形态描述、产地分布、图版 |
| Flora of China (FOC) | www.efloras.org | 英文权威分类修订 | 查学名变更（异名、接受名）与英文形态描述 |
| GBIF | www.gbif.org | 全球分布数据 | 下载 occurrence 数据做产地考证、分布图 |
| Plants of the World Online | powo.science.kew.org | 全球接受名判定 | 判定"接受名/异名"，追踪分类沿革 |
| iPlant 植物智 | www.iplant.cn | 中国植物智能检索 | 图片识别、地方植物志检索 |
| 中国植物图像库 | ppbc.iplant.cn | 活体/标本照片 | 形态核对、产地照片佐证 |

### 学名变更追踪方法
1. POWO 查当前接受名 → 2. FOC 查《中国植物志》处理意见 → 3. 反查相关修订论文（如 *Taxon*、*Phytotaxa* 上的分类修订）→ 4. 在 CNKI 搜"学名订正/新组合"类文献

## 五、标准与专论数据库

| 资源 | 内容 | 使用场景 |
|------|------|----------|
| 中药材标准数据库 | 中国药典、部颁标准、各省地方药材标准 | 核实法定基原、质量标准项目（性状/检查/含量测定） |
| 国家药品标准物质数据库 | 对照品/对照药材目录 | 查含量测定用对照品信息（如小檗碱对照品） |
| 国家药典委员会官网 | 药典勘误、公示稿 | 最新标准动态 |
| TCMSP（中药系统药理学数据库） | 成分-靶点-疾病关系 | 网络药理学、成分筛选（查 OB≥30%、DL≥0.18 的类药成分） |
| ETCM / SymMap / HERB | 中药成分与靶点补充库 | 多库交叉验证成分-靶点数据 |
| PubChem / ChemSpider | 化合物结构、性质 | 验证成分结构、CAS号、分子式 |

## 六、民族药特色数据库

- **中国民族药数据库**（中国中医科学院）——藏、蒙、维、傣、壮等民族药条目
- **藏药相关**：《晶珠本草》数字资源、藏药标准（2020年版藏药标准）查询
- **蒙药/维药**：《蒙药标准》《维吾尔药标准》地方标准库
- 检索提示：民族药名多语检索（藏文/威利/汉译），标准名称常含"藏药X"前缀（如"藏药吉合那保"）

## 七、跨库检索策略（一次任务完整流程）

```
第1轮 典籍层：古籍库/辑佚本 → 确认历史基原与别名（中华医典、中医古籍知识库）
第2轮 分类层：POWO+FOC+植物志 → 锁定当代学名与接受名
第3轮 标准层：药材标准数据库 → 确认现行法定基原与质控指标
第4轮 文献层：CNKI+PubMed 平行检索 → 基原/鉴定/成分/药理四个主题
第5轮 数据层：TCMSP+PubChem+GBIF → 成分、靶点、分布数据支撑
第6轮 交叉验证：引文追踪 + 高被引筛选 → 确定核心文献清单
```

## 八、检索式质量自检清单

- [ ] 药名维度覆盖：中文名/拉丁学名/英文俗名/民族名是否齐全？
- [ ] 异名与拼写变体是否用 OR 并入？
- [ ] 主题维度是否与用户侧重点匹配（基原/鉴定/化学/药理）？
- [ ] MeSH 词是否可自动扩展下位词（如 Coptis 下含多种黄连）？
- [ ] 是否建议了年限、文献类型、期刊分区筛选条件？
- [ ] 是否提供了 1-2 个"免费直达"路径（植物志/标准库）？
