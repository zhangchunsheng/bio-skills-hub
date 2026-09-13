# 藏药基因组学与天然多样性成分库构建 完整使用指南

> **版本**：v1.0 | **适用对象**：具有分子生物学或天然药物化学基础的研究人员
>
> 本指南可作为实验方案设计、团队培训或项目立项的技术参考文档。

---

## 目录

1. [技能概述与科学意义](#1-技能概述与科学意义)
2. [适用对象与前置知识](#2-适用对象与前置知识)
3. [输入数据与资源准备](#3-输入数据与资源准备)
4. [详细工作流程（GBCLV 五步法）](#4-详细工作流程gbclv-五步法)
   - 4.1 基因组测序策略与组装注释
   - 4.2 生物合成基因簇预测与挖掘
   - 4.3 天然产物结构预测与多样性评估
   - 4.4 多样性成分库构建
   - 4.5 结果验证与应用
5. [输出结果示例](#5-输出结果示例)
6. [常见问题与故障排除](#6-常见问题与故障排除)
7. [推荐工具链与参考脚本](#7-推荐工具链与参考脚本)
8. [扩展阅读与引用](#8-扩展阅读与引用)

---

## 1. 技能概述与科学意义

### 1.1 本技能解决的核心问题

藏药植物蕴含丰富的次生代谢产物资源，但由于以下瓶颈，其化学多样性尚未被系统性发掘：

- **基因组资源极度匮乏**：绝大多数藏药植物（如红景天 *Rhodiola rosea*、诃子 *Terminalia chebula*、波棱瓜 *Herpetospermum pedunculosum*、翼首草 *Pterocephalus hookeri* 等）缺乏参考基因组序列
- **传统分离效率低**：活性导向分离（bioassay-guided fractionation）重复发现率高，新颖化合物发现效率持续下降
- **结构与活性空间未被探索**：大量生物合成基因簇（Biosynthetic Gene Cluster, BGC）因异源表达条件缺失而"沉默"，其所编码的潜在新颖天然产物未被发现

**本技能通过基因组学驱动（Genome-Driven）的策略，系统性地解决上述问题。**

### 1.2 科学意义与应用价值

| 维度 | 具体价值 |
|------|---------|
| **药物先导发现** | 预测的新颖骨架可直接进入虚拟筛选或 HTS，缩短先导发现周期 60%–80% |
| **资源保护** | 为濒危藏药植物（如雪莲、红景天）建立"数字基因库"，减少盲目采挖；通过 BGC 异源表达替代天然提取 |
| **质量控制** | 基因组数据辅助 Q-marker 筛选（与 `tibet-qmarker-discovery` 技能联动），从基因层面验证特征代谢物的存在性 |
| **可持续利用** | 通过合成生物学（与 `tibet-cm-synbio` 技能联动）实现活性成分的异源生产，不依赖野生资源 |
| **分类与进化** | 比较基因组学分析藏药植物的 BGC 进化和化学多样性演化规律 |

### 1.3 藏药植物基因组学特殊挑战

与模式植物（拟南芥、水稻）相比，藏药植物基因组分析面临以下特殊挑战：

- **高海拔适应性导致基因组复杂**：高 GC 含量、大量重复序列（60%+）、高杂合度
- **缺乏近缘参考基因组**：需要 de novo 组装，无法依赖参考引导
- **次生代谢通路多属于种属特异性**：BGC 在不同科属间保守性低，通用数据库覆盖率有限
- **样本采集困难**：部分藏药植物分布于海拔 3000 m+ 地区，新鲜样本冷链运输是关键制约

---

## 2. 适用对象与前置知识

### 2.1 目标用户

- 天然产物化学研究者（需具备基础的生物信息学概念）
- 植物基因组学 / 生信分析师
- 藏药资源学研究生
- 药物发现项目 PI

### 2.2 建议前置知识

| 领域 | 具体要求 |
|------|---------|
| **基因组学基础** | 理解 NGS 测序原理、基因组组装指标（N50, L50, BUSCO 完整性）、基因结构注释流程 |
| **代谢通路分析** | 理解植物次生代谢分类（萜类、生物碱、黄酮、苯丙素）、P450 酶与糖基转移酶的作用 |
| **天然产物化学** | 理解 NMR/MS 结构解析原理、化合物的类药性五规则（Lipinski's Ro5） |
| **基础编程** | 能够运行 Linux 命令行（bash）、基础的 Python 脚本执行（conda 环境管理） |
| **资源准备** | 拥有或可申请 Linux 服务器（建议 CPU ≥ 16 核, RAM ≥ 64 GB, 存储 ≥ 2 TB） |

### 2.3 建议的软硬件环境

**硬件最低配置**（可运行核心分析）：

| 组件 | 最低要求 | 建议配置 |
|------|---------|---------|
| CPU | 8 核 | 32 核+ |
| RAM | 32 GB | 128 GB+ |
| 存储 | 500 GB SSD | 2 TB NVMe + 4 TB HDD |
| GPU | 非必需 | 1× NVIDIA A100 (用于 DeepBGC / 深度学习) |

**软件环境**（建议通过 Conda/Mamba 管理）：

```bash
# 创建统一环境
mamba create -n tibet-genomics python=3.10
mamba activate tibet-genomics

# 核心软件安装示例
mamba install -c bioconda -c conda-forge hifiasm flye canu busco braker3
mamba install -c bioconda hmmer interproscan diamond blast
mamba install -c conda-forge rdkit openbabel biopython pandas numpy
pip install antiSMASH[all]  # 或通过独立安装包
```

---

## 3. 输入数据与资源准备

### 3.1 需要的原始数据类型

| 数据类型 | 格式 | 关键作用 | 建议最低量 |
|---------|------|---------|-----------|
| **基因组测序数据** | FASTQ (.fq.gz) | 基因组组装 | HiFi: 30×; ONT: 60×; Illumina: 100× |
| **Hi-C 数据** | FASTQ | 染色体级别挂载 | 50× |
| **RNA-seq 数据** | FASTQ | 基因结构注释证据 + 共表达分析 | 3+ 组织/条件; 3× 生物学重复 |
| **代谢物谱 (LC-MS/MS)** | .mzML/.mzXML | 分子网络 + BGC 活性关联 | >100 特征 / 样本 |
| **已有参考基因组** | FASTA + GFF | 比较分析（如近缘种） | 1+ 近缘种 |

### 3.2 公共数据库资源

以下数据库是基因组挖掘和天然产物发现的核心数据源：

| 数据库 | URL | 用途 |
|--------|-----|------|
| **NCBI GenBank / SRA** | https://www.ncbi.nlm.nih.gov/ | 参考基因组下载、原始测序数据存档 |
| **UniProt (Swiss-Prot/TrEMBL)** | https://www.uniprot.org/ | 蛋白功能注释 |
| **antiSMASH database** | https://antismash.secondarymetabolites.org/ | BGC 已知簇比对 |
| **MIBiG** | https://mibig.secondarymetabolites.org/ | 已知 BGC 参考库（v4.0: >3,000 簇） |
| **NPAtlas** | https://www.npatlas.org/ | 已验证的微生物天然产物结构库 |
| **COCONUT** | https://coconut.naturalproducts.net/ | 天然产物开放数据库（>40 万） |
| **SuperNatural III** | https://bioinf-applied.charite.de/supernatural_3/ | >76 万天然产物，含 ADMET 信息 |
| **GNPS** | https://gnps.ucsd.edu/ | 质谱分子网络平台 |
| **MetaboLights** | https://www.ebi.ac.uk/metabolights/ | 代谢组学数据存储库 |
| **PlantCyc** | https://plantcyc.org/ | 植物代谢通路数据库 |
| **KEGG GENES** | https://www.kegg.jp/kegg/genes.html | 代谢通路功能注释 |
| **BUSCO** (植物库) | https://busco.ezlab.org/ | 基因组完整性评估 |

### 3.3 样本采集与核酸提取质控要点

**采样阶段**：

1. **组织选择**：优先使用幼嫩叶片或花蕾（细胞分裂旺盛，DNA 完整性好，RNA 含量高）；根茎次之
2. **速冻保存**：采集后立即投入液氮或 RNAlater 稳定液中；避免室温超过 30 分钟
3. **高海拔注意事项**：
   - 藏药植物常含有大量多糖/多酚（如诃子鞣质可达干重 30%+），常规 CTAB 法快速法会产生大量褐色胶状物
   - **改良提取方案**：CTAB + 2% PVP + 0.1 M 抗坏血酸 + 氯仿/异戊醇 (24:1) 抽提 2–3 次

**核酸质控（QC）接受标准**：

| 指标 | DNA | RNA |
|------|-----|-----|
| 浓度 (Nanodrop) | ≥ 50 ng/µL | ≥ 100 ng/µL |
| 纯度 A260/A280 | 1.8–2.0 | 1.9–2.1 |
| 纯度 A260/A230 | ≥ 1.8 | ≥ 2.0 |
| 完整性 | 主带 > 20 kb (凝胶电泳) | RIN ≥ 7 (Agilent Bioanalyzer) |
| 总量 | ≥ 5 µg (PacBio HiFi 建库) | ≥ 2 µg (RNA-seq 建库) |

---

## 4. 详细工作流程（GBCLV 五步法）

### 4.1 Step 1: 基因组测序策略与组装注释

#### 4.1.1 测序平台选择决策树

```
基因组大小预估（流式细胞术 / k-mer 分析）
    │
    ├── < 1 Gb ─────────────────────────────→ PacBio HiFi (CCS, 15–20 kb) → Hifiasm
    │
    ├── 1–5 Gb ─────────────────────────────→ PacBio HiFi + ONT Ultra-long → Hifiasm + TGS-GapCloser
    │
    └── > 5 Gb 或预算有限 ─────────────────→ ONT (Q20+, ~60×) → Flye + Medaka + Polypolish
                                                      │
                                                      └─ 补充 Illumina (PCR-free, 50×) 用于纠错
```

**推荐策略**：对于大多数藏药植物（基因组 ≤ 2 Gb），**PacBio HiFi + Hifiasm** 是当前最优方案，可达到 contig N50 20–50 Mb 水平。

#### 4.1.2 基因组组装（推荐工具）

| 工具 | 输入数据 | 适用场景 | 关键参数 | 版本建议 |
|------|---------|---------|----------|---------|
| **Hifiasm** | PacBio HiFi (CCS) | 高杂合度植物基因组 | `-l 0` (无hashing) / `--h1/h2` (Hi-C) | v0.19+ |
| **Flye** | ONT / PacBio CLR | 长读长通用 | `--genome-size 1g --nano-hq` | v2.9+ |
| **Canu** | 任意长读长 | 高错误率数据 | `correctedErrorRate=0.045` | v2.2+ |
| **NextDenovo** | ONT / PacBio | 大型基因组 | `genome_size=1g` | v2.5+ |

**组装质控指标**：

| 指标 | 优秀 | 可接受 | 需改进 |
|------|------|--------|--------|
| Contig N50 | ≥ 10 Mb | ≥ 1 Mb | < 1 Mb |
| 完整基因数 (BUSCO, eudicots_odb10) | ≥ 95% | ≥ 85% | < 85% |
| 重复序列占比 | > 50% (植物正常) | — | < 30% (过度压缩) |
| 总组装大小 | 基因组预期 ± 10% | ± 20% | > ± 30% |

#### 4.1.3 基因组注释

**重复序列注释**（必须在结构注释前完成）：

```bash
# 1. 从头构建重复序列库
RepeatModeler -pa 32 -database tibet_plant -LTRStruct
# 2. 基因组屏蔽
RepeatMasker -pa 32 -lib tibet_plant-families.fa -xsmall tibet_plant_genome.fa
```

**结构注释**：

```bash
# BRAKER3（推荐方法，整合 RNA-seq 和蛋白证据）
braker.pl --genome=tibet_plant_genome.fa.masked \
          --bam=merged_rnaseq.bam \
          --prot_seq=viridiplantae_odb10.fa \
          --species=tibet_plant \
          --threads=32
```

**功能注释**：

```bash
# InterProScan（pfam, PANTHER, SUPERFAMILY 等联合注释）
interproscan.sh -i proteins.faa -f TSV -goterms -pa -iprlookup -cpu 32

# KEGG 映射（使用 KofamKOALA web 服务或本地 kofamscan）
kofam_scan/exec_annotation -f detail -o annotation.tsv proteins.faa
```

### 4.2 Step 2: 生物合成基因簇（BGC）预测与挖掘

#### 4.2.1 BGC 预测工具选型

| 工具 | 算法 | 覆盖范围 | 适合场景 | 输出格式 |
|------|------|---------|---------|---------|
| **antiSMASH 7** | HMM + rule-based | 植物/细菌/真菌全部 BGC 类型 | **通用首选** | GBK + HTML + JSON |
| **PRISM 4** | HMM + substrate-based | 细菌为主 | 跨物种比较 | GBK + CSV |
| **DeepBGC** | 深度学习 (RNN) | 通用 | 发现新奇 BGC | GFF + JSON |
| **GECCO** | 深度学习 (CNN) | 细菌基因组 | 假阳性率低 | GFF + JSON |
| **plantiSMASH** | antiSMASH 定制版 | **植物特异性 BGC** | 藏药植物首选 | GBK + HTML |

> **推荐工作流**：**plant-iSMASH → antiSMASH (tsv模式) → DeepBGC 交叉验证**
>
> 对于藏药植物，plant-iSMASH 比通用 antiSMASH 更能识别植物特异性萜类合酶通路。

#### 4.2.2 antiSMASH 批量运行

```bash
#!/bin/bash
# batch_antismash.sh — 批量运行 antiSMASH
# 用法: bash batch_antismash.sh /path/to/genbank/files/ output_dir

GBK_DIR=$1
OUT_DIR=$2
THREADS=32

mkdir -p $OUT_DIR

for gbk in $GBK_DIR/*.gbk; do
    sample=$(basename $gbk .gbk)
    echo "[$(date)] Processing $sample ..."
    
    antismash $gbk \
        --output-dir $OUT_DIR/$sample \
        --genefinding-tool prodigal \
        --taxon plants \
        --enable-html \
        --clusterhmmer \
        --pfam2go \
        --cb-knownclusters \
        --cb-subclusters \
        --cb-general \
        --asf \
        --full-hmmer \
        --smcogs \
        --tta-threshold 0.6 \
        --cpus $THREADS
done

echo "[$(date)] All samples completed."
```

#### 4.2.3 转录组辅助挖掘（WGCNA 共表达网络）

当同时拥有 RNA-seq 和 LC-MS/MS 数据时，WGCNA 可以锁定与目标代谢物共表达的 BGC。

**分析框架**：

```
RNA-seq TPM matrix (n 样本 × m 基因)
    │
    └── WGCNA 共表达模块识别
            │
            ├── 模块-代谢物关联（LC-MS/MS 特征峰强度）
            │       └── Pearson |cor| > 0.8, p < 0.01 → 候选模块
            │
            └── 模块-功能富集
                    └── KEGG / GO → 确认是否为次生代谢通路
```

**核心 R 代码框架**（假设已安装 WGCNA 包）：

```r
# Step 1: 导出 BGC 基因的 TPM 值
bgc_genes <- read.csv("antismash_bgc_gene_list.csv")  # antiSMASH 输出的 BGC 基因 ID
tpm_matrix <- read.csv("rnaseq_tpm_matrix.csv", row.names = 1)
bgc_tpm <- tpm_matrix[rownames(tpm_matrix) %in% bgc_genes$gene_id, ]

# Step 2: WGCNA
library(WGCNA)
powers <- pickSoftThreshold(t(bgc_tpm), powerVector = 1:20, verbose = 0)
softPower <- 6  # 根据 R² > 0.85 选择
net <- blockwiseModules(t(bgc_tpm), power = softPower,
                        TOMType = "unsigned", minModuleSize = 5,
                        reassignThreshold = 0, mergeCutHeight = 0.25,
                        numericLabels = TRUE, verbose = 0)

# Step 3: 模块-代谢物关联
metabolite_data <- read.csv("lcms_peak_intensity.csv")  # 同一批样本的代谢组数据
module_eigengenes <- net$MEs
cor_results <- corAndPvalue(module_eigengenes, metabolite_data)
```

### 4.3 Step 3: 天然产物结构预测与多样性评估

#### 4.3.1 基于酶的产物骨架预测

**策略解读**：

BGC 中编码的酶决定了产物骨架的类型。以下是根据关键酶家族预测产物骨架的简化规则：

| 关键酶家族 | 预测的产物类型 | 示例工具 |
|------------|--------------|---------|
| **Terpene Synthase (TPS)** | 单萜/倍半萜/二萜骨架 | antiSMASH TPS 检测 |
| **Polyketide Synthase (PKS)** | 聚酮类（多环芳香族/大环内酯） | PRISM 延伸预测 |
| **Non-ribosomal Peptide Synthetase (NRPS)** | 非核糖体肽（环肽/糖肽） | NRPSPredictor2 |
| **Cytochrome P450** | 氧化后修饰（羟化/环氧化/骨架重排） | — |
| **UGT (UDP-glycosyltransferase)** | 糖苷化（提高水溶性和稳定性） | — |
| **SAM-dependent Methyltransferase** | 甲基化（影响活性和膜通透性） | — |

**BGC 结构新奇度的定量评估**：

```python
# bgc_novelty_score.py 片段
def calculate_novelty_score(bgc_protein_seqs, bgc_type):
    """
    计算 BGC 的新奇度分数 (0–1)
    - 高 (0.7–1.0): 无已知同源 BGC，酶组合为新组合
    - 中 (0.3–0.7): 与已知 BGC 有部分同源性，但核心酶不同
    - 低 (0–0.3): 与 MIBiG 已知 BGC 高度同源
    """
    # 对每个核心酶进行 BLAST 比对 → 记录与已知 BGC 的最大相似度
    # 根据相似度和酶组合的新颖性综合打分
    novelty = 1.0 - max_similarity  # 简化的分数
    return max(0.0, min(1.0, novelty))
```

#### 4.3.2 分子网络分析（GNPS 工作流）

GNPS（Global Natural Products Social Molecular Networking）通过 MS/MS 谱图相似性构建化合物关联网络，与 BGC 预测互补：

1. **数据准备**：LC-MS/MS 数据从原始格式（.raw/.d）通过 MSConvert 转换为 .mzML
2. **上传至 GNPS**：通过 Web 界面或 `gnps_dashboard` Python 客户端
3. **参数建议**：
   - 前体离子质量容差：0.02 Da
   - 碎片离子容差：0.05 Da
   - 最小峰强度：100 counts
   - 网络连接得分阈值：≥ 0.7 (cosine score)
4. **结果解读**：连接密集的子网络 → 相似结构系列；孤立节点 → 潜在新颖骨架

**替代方案——基于本地的代谢组学分析**：

```bash
# SIRIUS 5 + CSI:FingerID — 从头鉴定分子结构
sirius --input sample.mzML --output sirius_output \
       --maxmz 1500 --profile qtof \
       --compound "unknown" --processors 32

# 读取鉴定结果的分子结构
canopus --input sirius_output --output canopus_out
```

### 4.4 Step 4: 多样性成分库构建

#### 4.4.1 虚拟库构建（计算驱动）

基于 BGC 预测信息，构建虚拟化合物数据库：

```bash
# 使用 RDKit 生成化合物库的完整流程
python scripts/bgc_pipeline.py build_library \
    --bgc-csv antismash_summary.csv \
    --output-sdf virtual_library.sdf \
    --max-conformers 50 \
    --compute-descriptors
```

**虚拟库的化合物结构来源**：

| 来源 | 详细方法 | 规模预估 |
|------|---------|---------|
| **BGC 预测骨架 + 衍生化** | antiSMASH 输出的已知簇同源产物骨架 → RDKit `AllChem.ReplaceCore` 衍生 | 10–50/簇 |
| **分子网络节点** | GNPS 分子网络中的未鉴定特征 → SIRIUS/CSI:FingerID 预测结构 | 50–200/项目 |
| **同源建模产物** | 基于同源已知 BGC 的产物差异推断（如 PKS 延伸单元不同） | 20–100/项目 |
| **虚拟组合库** | 骨架枚举 + R 基团替换（REAL Space 策略） | 500–5,000/项目 |

**虚拟库的关键属性元数据**：

| 字段 | 格式 | 示例 |
|------|------|------|
| Compound_ID | `TGP_XXXXX` | TGP_00123 |
| Source_BGC_ID | antiSMASH cluster number | Cluster_5.3 |
| Source_Plant | 拉丁学名 | *Rhodiola rosea* |
| Predicted_Class | 化合物分类 | 倍半萜 (Sesquiterpene) |
| SMILES | 标准 SMILES | `CC1=CCC2C(C)(C)OC2C1` |
| MW | 分子量 (g/mol) | 236.35 |
| logP | 脂水分配系数 | 3.21 |
| HBA | 氢键受体数 | 1 |
| HBD | 氢键供体数 | 0 |
| TPSA | 拓扑极性表面积 (Å²) | 21.87 |
| Ro5_Violations | 类药性五规则违反数 | 0 |
| Synthetic_Accessibility | 合成难易度 (1–10, 1=易) | 4.2 |
| Novelty_Score | 新奇度 (0–1) | 0.78 |

**生成 3D 构象库**：

```python
from rdkit import Chem
from rdkit.Chem import AllChem

def generate_3d_conformers(sdf_in, sdf_out, max_confs=50):
    suppl = Chem.SDMolSupplier(sdf_in)
    writer = Chem.SDWriter(sdf_out)
    
    for mol in suppl:
        if mol is None:
            continue
        mol = Chem.AddHs(mol)
        params = AllChem.EmbedMultipleConfs(
            mol, numConfs=max_confs,
            pruneRmsThresh=0.5,
            randomSeed=42
        )
        if params == 0:
            # 无失败则生成单个构象
            AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        writer.write(mol)
    writer.close()
```

#### 4.4.2 实体库构建策略

**活性导向分离 (Bioassay-Guided Fractionation, BGF)**：

1. 基于虚拟库的预测，优先分离新奇度分数 > 0.7 的候选成分
2. 提取流程：95% EtOH 粗提 → 液-液萃取分段（石油醚/EtOAc/BuOH/水）
3. 分离手段：正相 silica gel + ODS + Sephadex LH-20 + Prep-HPLC
4. 每步收集馏分进行 LC-MS 跟踪 → 与虚拟库中预测的 [M+H]⁺ 和 RT 范围匹配

**质谱导向分离 (MS-Guided Fractionation, MSGF)**：

- 基于 GNPS 分子网络中的未归属节点（孤立节点或低相似度子网络）
- 设定 MS 特征阈值：
  - m/z 偏差 < 5 ppm
  - 同位素分布匹配
  - 碰撞截面 (CCS if TIMS) 偏差 < 2%
- 目标馏分直接进入结构鉴定（NMR + HR-ESI-MS/MS）

#### 4.4.3 库管理

**推荐数据库结构**（PostgreSQL 模式）：

```sql
CREATE TABLE compounds (
    compound_id VARCHAR(20) PRIMARY KEY,
    smiles TEXT NOT NULL,
    source_plant VARCHAR(100),
    source_bgc_id VARCHAR(50),
    predicted_class VARCHAR(50),
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 5),
    -- 1 = 仅预测; 2 = 虚拟验证; 3 = MS证据; 4 = 部分NMR; 5 = 完全鉴定
    status VARCHAR(20) DEFAULT 'predicted',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE descriptors (
    compound_id VARCHAR(20) REFERENCES compounds(compound_id),
    mw DECIMAL(8,2),
    logp DECIMAL(5,2),
    hba INTEGER,
    hbd INTEGER,
    tpsa DECIMAL(6,2),
    ro5_violations INTEGER,
    synthetic_access DECIMAL(3,1)
);

CREATE TABLE activity_scores (
    compound_id VARCHAR(20) REFERENCES compounds(compound_id),
    target VARCHAR(100),
    docking_score DECIMAL(6,2),
    assay_ic50 DECIMAL(10,4),
    assay_type VARCHAR(50)
);
```

**关于 DataWarrior**：推荐使用 DataWarrior（免费）进行库的可视化探索：
- 散点图矩阵（MW vs logP vs TPSA）
- 化学空间覆盖（t-SNE 或 PCA 投影）
- 子结构搜索和相似性筛选

### 4.5 Step 5: 结果验证与应用

#### 4.5.1 关键预测的验证策略

| 验证方法 | 适用场景 | 时间成本 | 资金成本 | 成功率 |
|---------|---------|---------|---------|--------|
| **标准品比对** | 预测的化合物有商业标准品 | 1–2 天 | 低 | ≥ 95% |
| **定向分离 + NMR** | 预测化合物可通过 LC-MS/MS 锁定 | 2–4 周 | 中 | 60%–80% |
| **异源表达** | BGC 完整，宿主可操作 | 3–6 月 | 高 | 30%–50% |
| **全化学合成** | 骨架明确，合成路线可行 | 1–3 月 | 中高 | 40%–60% |
| **半合成** | 天然类似物 + 选择性修饰 | 2–4 周 | 中 | 50%–70% |

#### 4.5.2 虚拟筛选应用

构建好的成分库可直接用于分子对接虚拟筛选：

```bash
# AutoDock Vina 批量对接框架
# 准备：受体结构 (PDB) + 化合物库 (SDF)
obabel rec.pdb -O rec.pdbqt -xr
obabel lib.sdf -O lib.pdbqt -m  # 将 SDF 拆分为单体

# 批量对接脚本骨架
for pdbqt in lib_*.pdbqt; do
    vina --receptor rec.pdbqt \
         --ligand $pdbqt \
         --center_x 0 --center_y 0 --center_z 0 \
         --size_x 20 --size_y 20 --size_z 20 \
         --exhaustiveness 8 \
         --out results/${pdbqt%.pdbqt}_out.pdbqt
done

# 结果汇总
grep "REMARK VINA RESULT:" results/*.pdbqt | \
    awk '{print $1, $4}' > docking_scores.csv
```

---

## 5. 输出结果示例

以下以假设的藏药植物 **"藏雪莲"** (取 *Saussurea involucrata* 为原型，基因组大小 ~2.5 Gb, 杂合度 ~1.8%)为例，展示完整输出。

### 5.1 基因组组装报告（摘要）

```
═══════════════════════════════════════════
  藏雪莲 (Saussurea involucrata) 基因组组装报告
═══════════════════════════════════════════

测序平台: PacBio Revio (HiFi) × 2 SMRT Cells
数据量: 89 Gb (≈ 35× 覆盖度)

组装工具: Hifiasm v0.24.0 (Hi-C 辅助)
───────────────────────────────────
统计指标              数值
───────────────────────────────────
Contig数              1,892
Contig N50            18.7 Mb
Longest contig        89.2 Mb
Total size            2.48 Gb
BUSCO 完整性 (eudicots_odb10)
  完整单拷贝          89.2%
  完整多拷贝          6.7%
  缺失                4.1%
GC 含量              38.2%
重复序列占比          62.5%
───────────────────────────────────

组装质量判定: ★★★★☆ (优秀，可直接用于 BGC 挖掘)
```

### 5.2 antiSMASH BGC 挖掘结果

```
═══ antiSMASH 7.0 结果摘要 ═══
基因组: Saussurea_involucrata.fna
发现的 BGC 总数: 89
--------------------------------
BGC 类型分布:
  萜烯 (Terpene)             31  (34.8%)
  PKS (I型)                   8  (9.0%)
  PKS (III型)                12  (13.5%)
  NRPS-like                  14  (15.7%)
  萜烯 + PKS 混合型           5  (5.6%)
  Alkaloid                    6  (6.7%)
  Saccharide                  3  (3.4%)
  Other / 未分类             10  (11.2%)

与 MIBiG 已知 BGC 相似性分析:
  > 70% 相似度 (已知簇)      8
  30%–70% (部分相似)        24
  < 30% (潜在新簇)          57  ← 高价值目标候选

新奇度评估:
  高新奇度 (≥ 0.7):         32 BGC
  中新奇度 (0.3–0.7):      41 BGC
  低新奇度 (< 0.3):        16 BGC
```

### 5.3 预测的新颖天然产物示例

```
化合物: TGP_00089
来源 BGC: Cluster_12.4 (Terpene, 新奇度 0.82)
预测类别: 倍半萜内酯 (Sesquiterpene lactone)
SMILES: CC1=C2C(=CC=C1)C(=O)OC3C2C(C)(C)OC3
分子式: C₁₅H₁₈O₃
MW: 246.30 g/mol
logP: 2.89
衍生化预测:
  - P450 羟化位点: C-6, C-8 → 3 种潜在类似物
  - 糖基化位点: C-3 (O-Glc) → 提高水溶性
  - 骨架重排: 非典型 germacrene → guaiane 骨架重排 → 2 种重排产物
```

### 5.4 多样性成分库统计

```
═══════════════════════════════════════════════
  藏雪莲天然多样性成分库 — 统计概览
═══════════════════════════════════════════════

库类型: 虚拟多样性成分库
总化合物数: 2,847

─────────────────────────────────
属性                  范围          中位数
─────────────────────────────────
MW (g/mol)          180–890       412
logP                –1.5–7.8      3.1
HBA                 0–8           3
HBD                 0–5           1
TPSA (Å²)           0–180         68.3
Rotatable Bonds     0–12          4
Ring Count          1–8           3
─────────────────────────────────

类药性评估:
  满足 Lipinski Ro5:  2,362 (83.0%)
  违反 1 项规则:       335 (11.8%)
  违反 ≥ 2 项规则:     150 (5.3%)

化学空间分布（t-SNE + Morgan fingerprints）:
  聚类数 (DBSCAN):    12 个主要簇
  片段多样度:         0.78 (范围 0–1, > 0.7 = 高多样度)

新颖化合物评估:
  与 NPAtlas 无匹配:   2,403 (84.4%)
  与 COCONUT 无匹配:   1,856 (65.2%)
  与两者均无匹配:     1,672 (58.7%) ← 潜在全新化合物

虚拟筛选亮点（以 COX-2 为靶点示例）:
  Top 5 对接分数: –11.2, –10.8, –10.5, –10.3, –10.1 kcal/mol
  与阳性对照 (Celecoxib, –9.8 kcal/mol) 相比更具优势
```

---

## 6. 常见问题与故障排除

### 6.1 基因组组装连续性差怎么办？

| 可能原因 | 诊断方法 | 解决方案 |
|---------|---------|---------|
| 测序覆盖度不足 | 检查 k-mer 分布；Hifiasm 日志中的 coverage 统计 | 补充测序至 30×+ (HiFi) 或 60×+ (ONT) |
| 杂合度太高 | 运行 `genomescope2` 评估杂合度；检查 Hifiasm dual 模式输出 | 使用 Hifiasm `-l 0` (purge_dups 模式) 或加 Hi-C 辅助 |
| 重复序列比例高 | RepeatMasker 分析重复占比 | 更换长读长平台（ONT > 100 kb ultra-long）跨过重复区 |
| GC 极端偏差 | 检查 GC 分布直方图 | 修改组装参数：Hifiasm `--n-hap 2 --hom-cov 40` |

### 6.2 BGC 预测工具给出大量假阳性如何处理？

```
假阳性率估计（植物基因组经验值）:
  antiSMASH (通用模式):   ~40%–60% 假阳性
  plant-iSMASH:           ~20%–35% 假阳性
  DeepBGC (默认阈值):     ~30%–50% 假阳性

降低假阳性的 4 条策略:
1. 转录组证据过滤: 只保留 RNA-seq 验证表达的 BGC (FPKM > 5)
2. 保守域完整性: 检查核心合成酶是否包含完整功能域
3. 跨工具交叉验证: 取 antiSMASH + DeepBGC + GECCO 的交集
4. 系统发育过滤: 仅保留在近缘物种中保守或在目标种内 unique 的 BGC
```

### 6.3 如何提高预测产物结构的可信度？

**可信度等级系统**（参考 NPAtlas 的五级系统）：

| 等级 | 标准 | 所需证据 |
|------|------|---------|
| Level 1: 确认 | 与 NMR 全谱数据一致 | 标准品比对或完整 NMR 归属 |
| Level 2: 高可信 | MS/MS + RT + 同位素模式一致 | SIRIUS 结构得分 > 0.8 + RT 预测匹配 |
| Level 3: 推测 | BGC 同源 + 酶逻辑合理 | 核心酶与已知 BGC 相似度 > 60% |
| Level 4: 假设 | 基于酶类型的骨架预测 | antiSMASH 产物预测输出 |
| Level 5: 未验证 | 仅计算预测 | 本技能虚拟库的默认等级 |

### 6.4 成分库更新与版本控制建议

```yaml
# 版本控制最佳实践
策略: Git LFS 追踪化合物库文件
目录结构:
  library/
    v1.0/           ← 初始版本（对应发表或项目里程碑）
    v1.1/           ← 小更新：新增 5 个经 NMR 确认的结构
    v2.0/           ← 大更新：新增 20+ BGC 数据，库规模翻倍

每次版本发布附带 CHANGELOG:
  ## v2.0 (2026-07-29)
  ### Added
  - 新增反相色谱保留时间预测模型
  - 集成 300 个化合物 MS/MS 真实谱图
  
  ### Changed
  - 更新 antiSMASH 输出解析器至 v7.1 格式
  
  ### Fixed
  - 修复 logP 计算在高脂溶性区域 (logP > 6) 的系统偏差

元数据版本化: 使用 DVC (Data Version Control) 跟踪大文件的变化
```

---

## 7. 推荐工具链与参考脚本

### 7.1 完整软件栈一览

#### 基因组学工具

| 类别 | 工具 | 安装方式 | 建议版本 |
|------|------|---------|---------|
| 组装 | Hifiasm | conda install -c bioconda hifiasm | ≥ 0.24.0 |
| 组装 | Flye | conda install -c bioconda flye | ≥ 2.9.5 |
| 组装纠错 | Polypolish | conda install -c bioconda polypolish | ≥ 0.6.0 |
| 组装纠错 | NextPolish | conda install -c bioconda nextpolish | ≥ 1.4.1 |
| 重复注释 | RepeatModeler | conda install -c bioconda repeatmodeler | ≥ 2.0.5 |
| 重复屏蔽 | RepeatMasker | conda install -c bioconda repeatmasker | ≥ 4.1.7 |
| 结构注释 | BRAKER3 | conda install -c bioconda braker3 | ≥ 3.0.8 |
| 结构注释 | Funannotate | pip install funannotate | ≥ 1.8.17 |
| 功能注释 | InterProScan | 本地安装（需 ftp 下载） | ≥ 5.69 |
| 功能注释 | eggNOG-mapper | conda install -c bioconda eggnog-mapper | ≥ 2.1.12 |
| 完整性评估 | BUSCO | conda install -c bioconda busco | ≥ 5.7.0 |

#### BGC 挖掘工具

| 工具 | 安装方式 | 建议版本 | 备注 |
|------|---------|---------|------|
| antiSMASH | pip install antismash[all] | ≥ 7.0 | 需单独下载数据库 |
| plantiSMASH | antiSMASH 内的植物模块 | — | antiSMASH 7 中集成 |
| DeepBGC | pip install deepbgc | ≥ 0.1.3 | 依赖 TensorFlow |
| GECCO | pip install gecco | ≥ 0.9.9 | |
| BiG-SLiCE | pip install bigslice | ≥ 1.1.0 | BGC 聚类分析 |

#### 天然产物与计算化学工具

| 工具 | 安装方式 | 用途 |
|------|---------|------|
| RDKit | conda install -c conda-forge rdkit | 化学信息学核心库 |
| Open Babel | conda install -c conda-forge openbabel | 分子格式转换 |
| DataWarrior | 官网下载 (免费) | 化合物库可视化 |
| KNIME | 官网下载 (免费) | 分析管道构建 |
| AutoDock Vina | conda install -c bioconda vina | 分子对接 |
| GNINA | conda install -c gnina gnina | 深度学习对接 |
| SIRIUS | 官网下载 | MS/MS 结构解析 |
| MZmine 4 | 官网下载 (免费) | LC-MS 数据处理 |

#### Python 库推荐

```text
biopython>=1.83        # 序列处理 (GenBank/FASTA 解析)
pandas>=2.1            # 数据框操作
numpy>=1.26            # 数值计算
rdkit>=2024.03         # 化学信息学核心
openbabel>=3.1         # 分子文件格式转换
scikit-learn>=1.5      # 聚类与降维 (t-SNE, DBSCAN)
matplotlib>=3.8        # 可视化
seaborn>=0.13          # 统计图表
requests>=2.31         # API 网络请求
tqdm>=4.66             # 进度条
```

### 7.2 核心脚本框架：`scripts/bgc_pipeline.py`

**函数 1：解析 antiSMASH 输出**

```python
#!/usr/bin/env python3
"""
bgc_pipeline.py — 藏药基因组学成分库构建辅助工具
"""
import os, sys, re, csv
from pathlib import Path
from Bio import SeqIO
import pandas as pd

def parse_antismash_output(gbk_dir: str, output_csv: str = None):
    """
    批量解析 antiSMASH 输出的 GBK 文件，提取 BGC 元数据。
    
    Parameters
    ----------
    gbk_dir : str
        antiSMASH 输出目录 (包含各样本子目录)
    output_csv : str, optional
        输出 CSV 路径
        
    Returns
    -------
    pd.DataFrame
        包含以下列的表格:
        - sample_id, cluster_number, cluster_type
        - contig, start, end, length
        - mibig_hit, similarity, core_genes
    """
    records = []
    gbk_dir = Path(gbk_dir)
    
    for gbk_file in sorted(gbk_dir.rglob("*.gbk")):
        sample = gbk_file.parent.parent.name  # 假设目录名即样本名
        try:
            for record in SeqIO.parse(gbk_file, "genbank"):
                for feat in record.features:
                    if feat.type == "cluster":
                        cluster_num = feat.qualifiers.get("cluster_number", [""])[0]
                        cluster_type = feat.qualifiers.get("product", [""])[0]
                        mibig = feat.qualifiers.get("most_similar_mibig", [""])[0]
                        sim = feat.qualifiers.get("similarity", [""])[0]
                        
                        records.append({
                            "sample_id": sample,
                            "cluster_number": cluster_num,
                            "cluster_type": cluster_type,
                            "contig": record.id,
                            "start": int(feat.location.start),
                            "end": int(feat.location.end),
                            "length": len(feat.location),
                            "mibig_hit": mibig,
                            "similarity": sim
                        })
        except Exception as e:
            print(f"⚠️  解析 {gbk_file.name} 失败: {e}", file=sys.stderr)
    
    df = pd.DataFrame(records)
    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"✅ 已保存 BGC 摘要至 {output_csv}")
    return df
```

**函数 2：提取 BGC 核心蛋白序列**

```python
def extract_bgc_sequences(gbk_dir: str, output_fasta: str = None):
    """
    从 BGC GBK 文件中提取核心生物合成酶的蛋白序列。
    
    筛选条件：只保留 CDS 特征中的关键酶基因
    (PKS / NRPS / TPS / P450 / UGT 等)
    """
    KEY_ENZYMES = {
        "polyketide_synthase", "non-ribosomal peptide synthetase",
        "terpene_synthase", "terpene_cyclase",
        "cytochrome_P450", "UDP-glycosyltransferase",
        "methyltransferase", "acyltransferase"
    }
    
    records = []
    gbk_dir = Path(gbk_dir)
    
    for gbk_file in sorted(gbk_dir.rglob("*.gbk")):
        for record in SeqIO.parse(gbk_file, "genbank"):
            for feat in record.features:
                if feat.type == "CDS":
                    gene_func = feat.qualifiers.get("function", [""])[0].lower()
                    product = feat.qualifiers.get("product", [""])[0].lower()
                    desc = gene_func + " " + product
                    
                    if any(kw in desc for kw in KEY_ENZYMES):
                        if "translation" in feat.qualifiers:
                            seq = feat.qualifiers["translation"][0]
                            locus = feat.qualifiers.get("locus_tag", [f"gene_{len(records)}"])[0]
                            records.append(f">{locus}|{gene_func[:60]}\n{seq}")
    
    if output_fasta:
        with open(output_fasta, "w") as f:
            f.write("\n".join(records))
        print(f"✅ 已保存 {len(records)} 条核心酶序列至 {output_fasta}")
    return records
```

**函数 3：构建虚拟化合物库**

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem, Lipinski

def build_virtual_library(bgc_csv: str, output_sdf: str = "virtual_library.sdf",
                          max_compounds_per_cluster: int = 10):
    """
    基于 BGC 预测结果生成虚拟化合物库。
    本版本使用规则模板映射，在完整版中可替换为 ML 预测模型。
    """
    df = pd.read_csv(bgc_csv)
    writer = Chem.SDWriter(output_sdf)
    compound_count = 0
    
    # 简化模板映射规则（生产版应使用更精确的 mapping）
    SKELETON_TEMPLATES = {
        "terpene": "CC(=C)C",           # 异戊二烯单元
        "type_i_pks": "CC(=O)CC(=O)",   # 聚酮链
        "nrps": "NC(=O)CNC(=O)",        # 多肽骨架
        "alkaloid": "c1ccncc1",         # 吡啶碱
    }
    
    for _, row in df.iterrows():
        bcg_type = row["cluster_type"].lower()
        template = None
        for key, smarts in SKELETON_TEMPLATES.items():
            if key in bcg_type:
                template = smarts
                break
        
        if template is None:
            continue
        
        # 生成一个基础骨架分子
        mol = Chem.MolFromSmiles(template)
        if mol is None:
            continue
        
        # 添加氢，生成 3D 构象
        mol = Chem.AddHs(mol)
        params = AllChem.EmbedMultipleConfs(
            mol, numConfs=3, randomSeed=42
        )
        if params == 0:
            AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        mol = Chem.RemoveHs(mol)
        
        # 写入属性
        mol.SetIntProp("cluster_number", int(row["cluster_number"]))
        mol.SetProp("cluster_type", row["cluster_type"])
        mol.SetProp("sample_id", row["sample_id"])
        writer.write(mol)
        compound_count += 1
    
    writer.close()
    print(f"✅ 虚拟库已保存至 {output_sdf}，共 {compound_count} 个化合物")
```

**函数 4：计算分子描述符**

```python
def compute_descriptors(sdf_file: str, output_csv: str = "descriptors.csv"):
    """
    计算化合物库的分子描述符和类药性评估。
    """
    suppl = Chem.SDMolSupplier(sdf_file)
    descriptors = []
    
    for mol in suppl:
        if mol is None:
            continue
        desc = {
            "compound_id": mol.GetProp("_Name") if mol.HasProp("_Name") else "unknown",
            "MW": Descriptors.MolWt(mol),
            "logP": Descriptors.MolLogP(mol),
            "HBA": Descriptors.NumHAcceptors(mol),
            "HBD": Descriptors.NumHDonors(mol),
            "TPSA": Descriptors.TPSA(mol),
            "RotBonds": Descriptors.NumRotatableBonds(mol),
            "RingCount": Descriptors.RingCount(mol),
            "AromaticRings": Descriptors.NumAromaticRings(mol),
        }
        # Lipinski 五规则
        ro5_violations = 0
        if desc["MW"] > 500: ro5_violations += 1
        if desc["logP"] > 5: ro5_violations += 1
        if desc["HBA"] > 10: ro5_violations += 1
        if desc["HBD"] > 5: ro5_violations += 1
        desc["Ro5_Violations"] = ro5_violations
        desc["Passes_Ro5"] = ro5_violations <= 1
        
        descriptors.append(desc)
    
    df = pd.DataFrame(descriptors)
    df.to_csv(output_csv, index=False)
    print(f"✅ 描述符表已保存至 {output_csv}")
    print(f"   Ro5 通过率: {df['Passes_Ro5'].mean():.1%}")
    return df


# ---- CLI 入口 ----
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="藏药基因组学成分库构建工具")
    parser.add_argument("mode", choices=["parse", "extract", "build_library", "descriptors"],
                        help="运行模式")
    parser.add_argument("--bgc-csv", help="BGC 摘要 CSV (build_library / descriptors 使用)")
    parser.add_argument("--gbk-dir", help="antiSMASH GBK 目录 (parse / extract 使用)")
    parser.add_argument("--output-csv", help="输出 CSV 路径")
    parser.add_argument("--output-sdf", default="virtual_library.sdf",
                        help="输出 SDF 路径")
    
    args = parser.parse_args()
    
    if args.mode == "parse":
        if not args.gbk_dir:
            parser.error("parse 模式需要 --gbk-dir")
        parse_antismash_output(args.gbk_dir, args.output_csv)
    elif args.mode == "extract":
        if not args.gbk_dir:
            parser.error("extract 模式需要 --gbk-dir")
        extract_bgc_sequences(args.gbk_dir, args.output_csv)
    elif args.mode == "build_library":
        if not args.bgc_csv:
            parser.error("build_library 模式需要 --bgc-csv")
        build_virtual_library(args.bgc_csv, args.output_sdf)
    elif args.mode == "descriptors":
        compute_descriptors(args.output_sdf, args.output_csv)
```

### 7.3 工作流自动化建议

**使用 Snakemake 或 Nextflow 构建可重现管道**：

```python
# Snakefile 片段 — BGC 挖掘自动化管道
rule antismash_plant:
    input:
        gbk = "genome/{sample}.gbk"
    output:
        "antismash/{sample}/index.html"
    params:
        cpus = 32
    shell:
        "antismash {input.gbk} --output-dir antismash/{wildcards.sample} "
        "--taxon plants --cpus {params.cpus}"

rule parse_bgc:
    input:
        expand("antismash/{sample}/index.html", sample=SAMPLES)
    output:
        "results/bgc_summary.csv"
    run:
        parse_antismash_output("antismash", "results/bgc_summary.csv")

rule build_library:
    input:
        "results/bgc_summary.csv"
    output:
        "results/virtual_library.sdf"
    run:
        build_virtual_library("results/bgc_summary.csv",
                              "results/virtual_library.sdf")
```

---

## 8. 扩展阅读与引用

### 8.1 代表性综述与方法学论文

**基因组挖掘与天然产物发现综述**：

1. Medema, M. H., & Fischbach, M. A. (2015). Computational approaches to natural product discovery. *Nature Chemical Biology*, 11(9), 639–648. https://doi.org/10.1038/nchembio.1884
   - 基因组挖掘发现天然产物的综述性介绍，适合入门阅读

2. van der Hooft, J. J., et al. (2020). Linking genomics and metabolomics to chart specialized metabolic diversity. *Chemical Society Reviews*, 49(10), 3297–3314. https://doi.org/10.1039/D0CS00162G
   - 基因组-代谢组关联分析的方法学综述

3. Ren, H., et al. (2024). Plant genome mining for novel natural products. *Natural Product Reports*, 41(1), 5–21. https://doi.org/10.1039/D3NP00037A
   - 植物基因组挖掘的最新综述，尤其关注植物特异性 BGC 类型

**关键工具发表论文**：

4. Blin, K., et al. (2023). antiSMASH 7.0: new and improved for detection, regulation and chemical structure prediction. *Nucleic Acids Research*, 51(W1), W46–W50. https://doi.org/10.1093/nar/gkad344
   - antiSMASH 7 的官方方法论文

5. Cheng, H., et al. (2021). Haplotype-resolved de novo assembly using phased assembly graphs with Hifiasm. *Nature Methods*, 18(2), 170–175. https://doi.org/10.1038/s41592-020-01056-5
   - Hifiasm 组装方法的原始论文

6. Hannigan, G. D., et al. (2019). A deep learning genome-mining strategy for biosynthetic gene cluster prediction. *Nucleic Acids Research*, 47(18), e110. https://doi.org/10.1093/nar/gkz654
   - DeepBGC 方法论文

7. Brügger, R., et al. (2021). PRISM 4: prediction of natural product chemical structures from microbial genomes. *Nucleic Acids Research*, 49(W1), W529–W535.
   - PRISM 结构预测工具

**代谢组学与分子网络**：

8. Wang, M., et al. (2016). Sharing and community curation of mass spectrometry data with Global Natural Products Social Molecular Networking. *Nature Biotechnology*, 34(8), 828–837. https://doi.org/10.1038/nbt.3597
   - GNPS 平台原始论文

9. Dührkop, K., et al. (2019). SIRIUS 4: a rapid tool for turning tandem mass spectra into metabolite structure information. *Nature Methods*, 16(4), 299–302. https://doi.org/10.1038/s41592-019-0344-8
   - SIRIUS 结构解析方法

**化合物库与虚拟筛选**：

10. Sorokina, M., et al. (2021). COCONUT online: collection of open natural products database. *Journal of Cheminformatics*, 13(1), 57. https://doi.org/10.1186/s13321-021-00537-3
    - COCONUT 天然产物数据库

11. Eberhardt, J., et al. (2021). AutoDock Vina 1.2.0: New docking methods, expanded force field, and Python bindings. *Journal of Chemical Information and Modeling*, 61(8), 3891–3898. https://doi.org/10.1021/acs.jcim.1c00203
    - AutoDock Vina 1.2 方法论文

**藏药基因组学（代表性应用案例）**：

12. Chen, S., et al. (2022). Chromosome-level genome assembly of *Rhodiola crenulata* provides insights into salidroside biosynthesis. *Communications Biology*, 5, 534. https://doi.org/10.1038/s42003-022-03443-6
    - 红景天基因组与红景天苷生物合成

13. Ma, Y., et al. (2023). A chromosome-level genome of *Saussurea involucrata* reveals adaptive evolution and flavonoid biosynthesis. *Plant Communications*, 4(4), 100585.
    - 雪莲基因组组装与黄酮代谢

14. Xu, Z., et al. (2024). Genome assembly of *Terminalia chebula* and identification of ellagitannin biosynthetic gene clusters. *Horticulture Research*, 11, uhad283.
    - 诃子基因组与鞣花鞣质 BGC 发现

### 8.2 推荐网络资源

- **antiSMASH 官方教程**：https://docs.antismash.secondarymetabolites.org/
- **GNPS 教程库**：https://gnps.ucsd.edu/ProtectoSAFe/static/gnps-tutorial.pdf
- **RDKit Cookbook**：https://www.rdkit.org/docs/Cookbook.html
- **WGCNA 官方教程**：https://horvath.genetics.ucla.edu/html/CoexpressionNetwork/Rpackages/
- **Busco 植物谱系数据库下载**：https://busco-data.ezlab.org/v5/data/lineages/
- **Bioconda 软件包搜索**：https://bioconda.github.io/
- **MIBiG 数据库**：https://mibig.secondarymetabolites.org/

### 8.3 数据集与资源

- **植物基因组重复序列库 (植物版 RepeatMasker)**:
  - RepBase (https://www.girinst.org/repbase/) — 需机构订阅
  - DANTE (https://dante.plant.tools/) — 免费植物重复序列注释工具
- **植物蛋白参考库 (BRAKER 注释用)**:
  - Viridiplantae OrthoDB: https://bioinf.evop.org/orthodb/
  - PLAZA 植物基因组平台: https://bioinformatics.psb.ugent.be/plaza/
- **天然产物活性数据库**:
  - ChEMBL: https://www.ebi.ac.uk/chembl/
  - DrugBank: https://go.drugbank.com/
  - TCMSP (中药系统药理学): https://tcmsp-e.com/

---

> **文件结束** — 本文档由 `tibet-genomics-complib` 技能随附，版本 v1.0。
>
> 建议定期检查工具和数据库更新（每 6 个月），以确保分析方法保持最新。
