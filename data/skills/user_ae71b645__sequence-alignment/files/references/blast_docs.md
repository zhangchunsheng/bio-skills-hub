# BLAST 文档

## 概述

BLAST（Basic Local Alignment Search Tool，基本局部比对搜索工具）是一种用于比较生物序列基本信息的算法，例如蛋白质的氨基酸序列或 DNA 序列的核苷酸序列。

## BLAST 程序

### blastn
- **查询序列**：核酸
- **数据库**：核酸
- **使用场景**：用核酸查询序列检索核酸数据库

### blastp
- **查询序列**：蛋白
- **数据库**：蛋白
- **使用场景**：用蛋白查询序列检索蛋白数据库

### blastx
- **查询序列**：核酸（翻译后）
- **数据库**：蛋白
- **使用场景**：用翻译后的核酸查询序列检索蛋白数据库

### tblastn
- **查询序列**：蛋白
- **数据库**：核酸（翻译后）
- **使用场景**：用蛋白查询序列检索翻译后的核酸数据库

### tblastx
- **查询序列**：核酸（翻译后）
- **数据库**：核酸（翻译后）
- **使用场景**：用翻译后的核酸查询序列检索翻译后的核酸数据库

## 关键指标

### E-value（期望值）
- 统计显著性阈值
- 数值越低越好
- E-value < 0.01 通常被视为具有显著性
- 默认值：10

### Bit Score（比特得分）
- 跨检索结果可比较的标准化得分
- 数值越高越好
- 由原始比对得分推导而来

### Identity（一致性）
- 比对中完全相同匹配所占的百分比
- 计算方式：（相同位点数 / 比对长度）× 100

### Positives（相似位点数）
- 针对蛋白比对，指相似的氨基酸（保守替换）
- 包含相同残基与相似残基

## 常用数据库

| 数据库 | 类型 | 说明 |
|----------|------|-------------|
| nr | 蛋白 | 非冗余蛋白序列 |
| nt | 核酸 | 核酸序列集合 |
| swissprot | 蛋白 | Swiss-Prot 蛋白序列 |
| pdb | 蛋白 | 蛋白质数据库（Protein Data Bank）序列 |
| refseq_protein | 蛋白 | NCBI 参考序列（RefSeq）蛋白 |
| refseq_rna | 核酸 | NCBI 参考序列（RefSeq）RNA |
| est | 核酸 | 表达序列标签（Expressed Sequence Tags） |
| gss | 核酸 | 基因组勘测序列（Genome Survey Sequences） |

## 最佳实践

1. **选择合适的程序**：正确匹配查询序列与数据库的类型
2. **设置 E-value 阈值**：高置信度命中建议从 0.001 起
3. **过滤低复杂度区域**：使用合适的过滤器避免误报命中
4. **检查比对长度**：过短的比对可靠性可能较低
5. **核实一致性百分比**：一致性越高，说明进化关系越接近

## 参考文献

- Altschul SF, Gish W, Miller W, Myers EW, Lipman DJ. Basic local alignment search tool. J Mol Biol. 1990;215(3):403-410.
- NCBI BLAST 帮助文档：https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs
