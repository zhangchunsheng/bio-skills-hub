# 神经科学领域生信数据分析指南

本指南融合 BioClaw 的计算生信工具生态，覆盖神经科学研究中的常见生信分析需求。所有分析必须可复现（记录版本、参数、随机种子）。

> **运行环境说明（v2.0.10 更新）**：本技能绘图统一走 Python 引擎（`prism_theme.py`）；**R 定位为生信分析**——RNA-seq 差异表达（DESeq2 / edgeR / limma）与富集（clusterProfiler）**推荐在 R 环境运行**（推荐本地 R ≥ 4.4 + RStudio）。WorkBuddy 内置 Python 3.13 环境侧重：富集用 `gseapy`、单细胞用 `scanpy`、可视化用 `matplotlib/seaborn`。若在无 R 的环境中，则退回 Python 路径并**不要假装 Python 能直接跑 DESeq2**（无原生实现）。
>
> **依赖**：R 流程需 Bioconductor 包（DESeq2 / edgeR / limma / clusterProfiler），按 `BiocManager::install()` 安装；Python 流程用 scanpy / gseapy / matplotlib / seaborn，缺失按 `references/python-runtime.md` 自动安装，确保开箱即跑。

## 一、数据类型与对应流程

| 数据类型 | 适用场景 | 分析流程 |
|---------|---------|---------|
| 转录组 RNA-seq | 组织/细胞表达谱 | 质控→比对→定量→差异→富集 |
| 单细胞 RNA-seq | 细胞异质性（胶质细胞亚群） | 质控→降维→聚类→注释→差异 |
| 空间转录组 | 空间表达模式 | 质控→聚类→空间注释→配体受体 |
| 蛋白组 | 蛋白表达/翻译后修饰 | 定量→差异→通路 |
| 甲基化 | 表观遗传 | 差异甲基化→功能 |
| 影像数据 | MRI/CT 神经影像 | 影像组学→分割→分析 |
| 多组学集成 | 多组学 | 整合→关联→网络 |
| 遗传学/变异 | 遗传病/风险基因 | 变异注释→致病性→关联 |

## 二、RNA-seq 标准流程（最常用）

### Step 1: 质控
```
工具：FastQC → MultiQC 汇总
检查：碱基质量、接头、GC含量、重复率、overrepresented sequences
```
- FASTQ 质控：`fastqc *.fastq`
- 汇总报告：`multiqc .`
- 去接头/修剪：`fastp` 或 `trimmomatic`

### Step 2: 比对与定量
- 基因组比对：`STAR` / `HISAT2` / `bowtie2`
- 定量：`featureCounts` / `RSEM` / `Salmon`
- 质控指标：比对率（通常 >70%）、gene body coverage

### Step 3: 差异表达分析
**R 环境（推荐）**：
```r
library(DESeq2)  # 或 edgeR / limma
dds <- DESeqDataSetFromMatrix(countData, colData, design = ~group)
dds <- DESeq(dds)
res <- results(dds, contrast = c("group", "Treatment", "Control"))
# 阈值：|log2FC| > 1, padj < 0.05
```
> **直接可用的完整模板**：技能内置 `scripts/bioinfo_rna_seq.R`——含依赖守卫、合成演示数据端到端验证、DEG 表/MA/火山图/PCA 导出、GO/KEGG/GSEA 富集与 sessionInfo 可复现记录。RStudio 中打开逐段运行；接入真实数据时改 `demo=FALSE` 并准备 `counts.csv`/`colData.csv` 即可（纯本地运行，无联网上传）。

**Python 环境（本环境优先）**：
```python
import pandas as pd, numpy as np
# 富集分析：gseapy（纯 Python，可跑 GO/KEGG/GSEA）
import gseapy as gp
enr = gp.enrichr(gene_list=gene_list, gene_sets='GO_Biological_Process_2021')
# 差异表达：Python 无 DESeq2 原生实现；两组粗筛用 scipy（见 statistical-analysis.md §4.B.1）
# 若坚持 DESeq2，可 pip install pyDESeq2，或在 R 环境运行上方 R 代码
from scipy import stats
# stats.ttest_ind / mannwhitneyu 做候选基因粗筛
```

### Step 4: 富集分析
- **GO 富集**：`clusterProfiler` (R) / `gseapy` (Python)
- **KEGG 通路**：`clusterProfiler` / `ReactomePA`
- **GSEA 基因集富集**：`fgsea` / `clusterProfiler::gseGO`
- **细胞类型去卷积**：CibersortX / MuSiC / BisqueRNA

### Step 5: 可视化
- 火山图（volcano plot）
- 热图（heatmap）
- PCA 图 / UMAP
- GSEA 富集图
- 通路网络图

## 三、单细胞 RNA-seq 分析（胶质细胞亚群研究）

适合研究**疾病状态下小胶质细胞/星形胶质细胞异质性**、**细胞状态转变**等。

### 流程（Seurat / Scanpy）
1. **质控**：过滤低质量细胞（基因数、线粒体比例）
2. **标准化**：LogNormalize / SCTransform
3. **降维聚类**：PCA → UMAP/tSNE → FindClusters
4. **细胞类型注释**：marker 基因
5. **差异分析**：FindMarkers（疾病状态 vs 对照状态）
6. **拟时序**：Monocle3 / Slingshot（细胞状态转变）
7. **细胞通讯**：CellChat / CellPhoneDB（胶质-神经元-内皮互作）
8. **轨迹/RNA速度**：scVelo（分化方向）

### Scanpy 实操模板（Python，本环境优先）
```python
import scanpy as sc
adata = sc.read_h5ad('counts.h5ad')
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
adata = adata[adata.obs.pct_counts_mt < 20].copy()
sc.pp.normalize_total(adata); sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata); sc.tl.pca(adata)   # scanpy ≥1.9 用 sc.tl.pca（sc.pp.pca 已废弃）
sc.pp.neighbors(adata); sc.tl.umap(adata); sc.tl.leiden(adata)
sc.pl.umap(adata, color=['leiden', 'Cx3cr1', 'Gfap'])
# 差异：sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
```

### 神经细胞 marker 基因参考
| 细胞类型 | Marker |
|---------|--------|
| 神经元 | Rbfox3/NeuN, Snap25, Tubb3, Map2, Syn1 |
| 兴奋性神经元 | Slc17a7/Vglut1, Camk2a |
| 抑制性神经元 | Gad1, Gad2, Slc32a1/Vgat |
| 小胶质细胞 | Cx3cr1, P2ry12, Tmem119, Hexb |
| 星形胶质细胞 | Gfap, Aldh1l1, Slc1a3, Aqp4 |
| 少突胶质细胞 | Olig2, Mbp, Mog, Plp1 |
| 少突前体细胞 OPC | Pdgfra, Cspg4/NG2 |
| 内皮细胞 | Cldn5, Pecam1, Flt1 |
| 周细胞 | Pdgfrb, Des, Rgs5 |
| 血管平滑肌细胞 | Acta2, Myh11, Tagln |

### 小胶质细胞状态 marker 参考
| 状态 | Marker |
|------|--------|
| 稳态小胶质细胞 | Cx3cr1, P2ry12, Tmem119, Siglech, Hexb |
| 促炎活化 (M1样) | CD86, iNOS/Nos2, TNF, IL1b, Ccl2 |
| 抗炎 (M2样) | Arg1, Ym1/Chil3, CD206/Mrc1, IL10 |
| 疾病相关小胶质细胞 (DAM) | Clec7a, Itgax, Apoe, Trem2, Cst7 |
| 衰老小胶质细胞 | Cdkn2a, Serpine1, IL1b |

## 四、蛋白组学分析
- 定量软件：MaxQuant / Proteome Discoverer
- 差异蛋白：limma / DEP
- 修饰组（磷酸化/泛素化）：个性化分析
- 蛋白互作网络：STRING + Cytoscape

## 五、变异分析（遗传病/风险基因）

### 变异注释流程
1. 获取变异（ClinVar / 文献 / gnomAD）
2. 变异注释：ANNOVAR / VEP
3. 保守性评估：GERP / PhyloP
4. 致病性预测：SIFT / PolyPhen / REVEL / CADD
5. 结构域定位：蛋白结构域（跨膜、激酶、配体结合域等）
6. 人群频率过滤：gnomAD 频率 <0.1%（致病性候选）

### 分析代码示例（Python）
```python
# 检查变异是否位于蛋白功能结构域
def in_domain(position, domain_ranges):
    return any(start <= position <= end for start, end in domain_ranges)
```

## 六、神经影像数据分析

- 结构 MRI 分割：FreeSurfer / SPM / FSL
- 白质高信号（WMH）分割：FreeSurfer / SPM / 深度学习 (nnU-Net)
- 弥散张量成像（DTI）：FA/MD 值分析（FSL / DTI-TK）
- 功能连接：fMRI 静息态（CONN / DPARSF）
- 影像组学特征提取：PyRadiomics

## 七、分析工具清单（CLI 见此；R/Python 库见 references/statistical-analysis.md §六，避免重复）
| 工具 | 用途 |
|------|------|
| FastQC / MultiQC | 测序质控 |
| fastp | 数据修剪 |
| STAR / HISAT2 / bowtie2 | 比对 |
| featureCounts / RSEM / Salmon | 定量计数 |
| SAMtools / BCFtools | 比对/变异处理 |
| BLAST+ | 序列相似性 |
| PyMOL | 蛋白结构可视化 |

## 八、可复现性要求

每次分析必须记录：
1. 软件版本（`pip freeze` / `sessionInfo()`）
2. 参数设置（比对参数、DESeq2 参数）
3. 随机种子（`set.seed(42)` / `np.random.seed(42)`）
4. 参考基因组版本（GRCh38/mm10 等）
5. 数据版本与来源

## 九、常见陷阱

- ⚠️ **批次效应**：多批次数据需校正（ComBat / limma removeBatchEffect）
- ⚠️ **假阳性**：差异基因需多重比较校正（BH/FDR）
- ⚠️ **过度解读**：相关不等于因果，通路富集≠机制验证
- ⚠️ **小样本**：n<3 时谨慎下结论，考虑功效分析
- ⚠️ **注释版本**：确认基因/转录本注释版本一致
- ⚠️ **双端配对错误**：确认 read1/read2 配对与链特异性方向

## 十、进阶可执行流水线（scVI 批次校正 / PyDESeq2 / GRN 推断）

> 借鉴 K-Dense-AI/claude-scientific-skills 的可执行建模范式（scvi-tools / pydeseq2 / arboreto）。以下为**脚本骨架 + 标准参数**，接入真实数据前先跑通合成数据。包安装统一走 `references/python-runtime.md` 的 managed venv（`python -m venv` + `pip install`），不污染系统环境。

### 10.1 scVI 概率批次校正（scanpy + scvi-tools）
- 适用：多批次/多供体单细胞数据整合，优于简单 harmony/ComBat 的线性假设。
- 标准流程骨架：
```python
import scanpy as sc
import scvi
adata = sc.read_h5ad("merged.h5ad")
scvi.model.SCVI.setup_anndata(adata, batch_key="batch", labels_key="cell_type")
model = scvi.model.SCVI(adata, n_layers=2, n_latent=30, gene_likelihood="nb")
model.train(max_epochs=400, early_stopping=True)        # 早停防过拟合
adata.obsm["X_scVI"] = model.get_latent_representation()
# 用 scVI 潜空间做邻居图/UMAP/差异（替代原始 PCA）
sc.pp.neighbors(adata, use_rep="X_scVI"); sc.tl.umap(adata); sc.tl.leiden(adata)
```
- 不确定批次效应是否显著时，先 `scvi.model.SCVI` 与原始 PCA 各跑一遍 UMAP 对比。

### 10.2 PyDESeq2 差异表达（Python 端，无 R 环境备选）
- 适用：希望在 Python 内完成差异表达（与 §二 R 路径等价）。
- 骨架：
```python
from pydeseq2.ds import DeseqDataSet, DefaultInference
dds = DeseqDataSet(
    counts=counts_df,           # 行=基因, 列=样本
    metadata=metadata_df,       # 含 group 列
    design_factors="group",
)
dds.deseq2()
res = dds.results(contrast=("group", "Treatment", "Control"))
res = res.sort_values("padj").query("padj < 0.05 and abs(log2FoldChange) > 1")
```
- 阈值同 §二：`|log2FC| > 1, padj < 0.05`。

### 10.3 基因调控网络推断（arboreto）
- 适用：从表达矩阵推断转录因子 → 靶基因调控（如小胶质激活中 TF 驱动机理）。
- 骨架：
```python
from arboreto.algo import grnboost2
from arboreto.utils import load_tf
tf_names = load_tf("resources/TF_mm.txt")     # 物种 TF 列表
net = grnboost2(expression_matrix.values, tf_names=tf_names,
                gene_names=expression_matrix.index.tolist())
# net: [TF, target, importance]
```
- 大数据可选 `dask_grnboost2`（分布式）。

### 10.4 公共数据整合（cellxgene Census，可选）
- 适用：用公开单细胞 census 做同组织对照（如正常脑 vs 疾病脑胶质细胞基线）。
- `pip install cellxgene-census`；按 tissue/species 切片取 AnnData，与本地数据合并后走 §10.1。

### 10.5 进阶工具清单
| 工具 | 用途 | 安装 |
|------|------|------|
| scvi-tools | 概率批次校正/整合 | `pip install scvi-tools` |
| pydeseq2 | Python 端差异表达 | `pip install pydeseq2` |
| arboreto | GRN 推断 | `pip install arboreto` |
| cellxgene-census | 公共单细胞数据 | `pip install cellxgene-census` |