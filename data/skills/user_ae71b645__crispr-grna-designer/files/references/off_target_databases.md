# 脱靶数据库

## 已验证的脱靶数据集

### 1. GUIDE-seq

**方法**：通过测序实现的全基因组无偏差双链断裂（DSB）识别

**发表文献**：Tsai 等人，"GUIDE-seq enables genome-wide profiling of off-target cleavage by CRISPR-Cas nucleases"，Nature Biotechnology 2014

**关键特点**：
- 在 DSB 位点整合 dsODN
- 可检测频率 >0.1% 的 DSB
- 脱靶验证的金标准

**数据集**：
- `guide_seq_human_hg38.bed`：50+ 细胞系，1,200+ 向导
- `guide_seq_mouse_mm10.bed`：mESC、MEF 数据集

**访问方式**：https://github.com/tsailabSJ/guideseq

### 2. Digenome-seq

**方法**：体外 Cas9 消化 + 全基因组测序

**发表文献**：Kim 等人，"Digenome-seq: genome-wide profiling of CRISPR-Cas9 off-target effects in human cells"，Nature Methods 2015

**优势**：
- 无细胞系统（无克隆偏差）
- 可检测低频脱靶
- 预筛选成本效益高

**局限性**：
- 可能遗漏受染色质保护的位点
- 体外结果可能无法反映体内活性

### 3. CIRCLE-seq

**方法**：通过测序进行的环化体外切割效应报告

**发表文献**：Tsai 等人，"CIRCLE-seq: a highly sensitive in vitro method for genome-wide identification of CRISPR-Cas9 off-targets"，Nature Protocols 2018

**相较于 Digenome-seq 的改进**：
- 更高的灵敏度（可检测 0.01% 频率）
- 降低了背景噪音
- 验证率 >90%

### 4. SITE-seq

**方法**：通过测序进行的靶点边缘选择性富集与分析

**发表文献**：Cameron 等人，"Mapping the genomic landscape of CRISPR-Cas9 cleavage"，Nature Methods 2017

## 计算数据库

### 1. Cas-OFFinder

**发表文献**：Bae 等人，"Cas-OFFinder: a fast and versatile algorithm that searches for potential off-target sites of Cas9 RNA-guided endonucleases"

**特征**：
- 支持凸起序列（DNA/RNA 凸起）
- 支持多种 PAM 序列
- 支持 GPU 加速

**网址**：http://www.rgenome.net/cas-offinder/

### 2. CHOPCHOP 数据库

**网址**：https://chopchop.cbu.uib.no/

**预计算内容**：
- 人类（hg19/hg38）
- 小鼠（mm9/mm10）
- 斑马鱼（danRer10/11）

### 3. GT-Scan

**特征**：
- 全基因组脱靶分析
- GPU 加速搜索
- 可视化基因组浏览器集成

## 脱靶注释

### 基因组背景分类

| 类别 | 定义 | 风险等级 |
|----------|------------|------------|
| 外显子区 | 位于蛋白编码外显子内 | 高 |
| 内含子区 | 位于基因内含子内 | 中 |
| UTR | 5' 或 3' 非翻译区 | 中 |
| 启动子 | 距转录起始位点 <2kb | 高 |
| 基因间区 | 无已知基因特征 | 低 |
| 重复序列 | 位于转座元件内 | 低 |

### 群体变异

**gnomAD 整合**：
- 过滤靶点附近的常见 SNP
- 标记针对多态区域的向导
- 群体特异性等位基因频率

**ClinVar 重叠**：
- 位于致病性变异区域的脱靶
- 疾病相关基因

## 基准结果

### 脱靶检测灵敏度

| 方法 | 检测下限 | 假阳性率 | 成本 |
|--------|-----------------|---------------------|------|
| GUIDE-seq | 0.1% | <5% | $$$$ |
| Digenome-seq | 0.01% | ~15% | $$$ |
| CIRCLE-seq | 0.001% | <10% | $$$ |
| SITE-seq | 0.05% | ~8% | $$$ |
| WGS | 0.5% | ~20% | $$$$$ |

### 计算预测准确性

| 工具 | 精确率 | 召回率 | F1 分数 |
|------|-----------|--------|----------|
| CFD | 0.45 | 0.72 | 0.55 |
| MIT | 0.38 | 0.65 | 0.48 |
| CCTop | 0.52 | 0.68 | 0.59 |
| CRISPOR | 0.55 | 0.70 | 0.62 |

## 本目录中的数据文件

```
references/off_target_databases/
├── guide_seq/
│   ├── human_hg38_guides.bed
│   ├── mouse_mm10_guides.bed
│   └── metadata.json
├── digenome_seq/
│   └── digenome_benchmarks.tsv
├── cfd_scores/
│   ├── mismatch_penalties.csv
│   └── pam_scores.csv
└── gnomad/
    └── common_variants_flanking_sgrnas.vcf
```

## 推荐工作流程

1. **计算筛选**：使用 CFD/CCTop 过滤高风险向导
2. **体外验证**：对候选靠前的向导使用 Digenome-seq 或 CIRCLE-seq
3. **体内确认**：在目标细胞类型中使用 GUIDE-seq
4. **功能测试**：对预测的脱靶位点进行扩增子测序

## 关键发现

1. **种子区至关重要**：第 12-20 位的错配通常可被容忍
2. **PAM 邻近性**：第 20 位（NGG）对错配最敏感
3. **染色质效应**：开放染色质中的脱靶更可能具有活性
4. **细胞类型影响**：同一向导在不同细胞中脱靶效应可能不同

## 参考文献

1. Tsai SQ et al. (2014) Nature Biotechnology 32:687-697
2. Kim D et al. (2015) Nature Methods 12:237-243
3. Tsai SQ et al. (2017) Nature Protocols 12:551-567
4. Bae S et al. (2014) Bioinformatics 30:1473-1475
5. Cameron P et al. (2017) Nature Methods 14:600-606
