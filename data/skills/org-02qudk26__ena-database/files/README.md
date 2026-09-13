# ENA 序列数据检索

- 唯一标识：`hub-ena-database`
- 显示名称：ENA 序列数据检索
- 能力摘要：通过 European Nucleotide Archive 的 REST API 与 FTP 检索 DNA/RNA 序列、FASTQ 原始读段、组装、样本、研究和注释元数据，并支持可追溯批量下载。

## 案例素材

1. 生信人员按研究编号下载公开 RNA-seq 数据。该 skill 会先查询样本与 run 元数据，筛选平台和物种，再以受控并发下载 FASTQ 并记录 accession。
2. 研究项目要比较多个菌株组装。该 skill 会按分类和组装质量检索基因组，保留版本、发布日期和注释来源，避免混用不同参考版本。
3. 数据管道需处理大规模公共数据。该 skill 会处理 API 分页、限速和失败重试，校验文件校验和，并把来源链写入分析元数据。

