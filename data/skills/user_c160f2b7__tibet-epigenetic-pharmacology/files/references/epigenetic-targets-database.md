# 表观遗传调控靶点数据库（藏药研究参考）

## DNA 甲基化机器

### 甲基转移酶（DNMTs）

| 靶点 | 全称 | 功能 | 已知天然抑制剂 | 检测方法 |
|------|------|------|--------------|---------|
| DNMT1 | DNA Methyltransferase 1 | 维持甲基化，复制后甲基化模式继承 | 没食子酸、EGCG、姜黄素、槲皮素 | WB、RT-qPCR、活性试剂盒 |
| DNMT3A | DNA Methyltransferase 3A | 从头甲基化，胚胎发育与分化 | 漆黄素、白藜芦醇 | WB、RT-qPCR、活性试剂盒 |
| DNMT3B | DNA Methyltransferase 3B | 从头甲基化，肿瘤特异性甲基化 | 萝卜硫素、帕立骨化醇 | WB、RT-qPCR、活性试剂盒 |
| DNMT3L | DNMT3-like | DNMT3A/3B辅助因子，无催化活性 | — | RT-qPCR |

### 去甲基化酶（TETs）

| 靶点 | 全称 | 功能 | 已知调控机制 | 检测方法 |
|------|------|------|-------------|---------|
| TET1 | Ten-Eleven Translocation 1 | 5mC→5hmC氧化，去甲基化起始 | 维生素C增强活性，某些天然黄酮可诱导表达 | WB、5hmC dot blot、活性试剂盒 |
| TET2 | Ten-Eleven Translocation 2 | 造血系统主要TET | α-酮戊二酸依赖，异柠檬酸脱氢酶突变影响 | WB、RT-qPCR |
| TET3 | Ten-Eleven Translocation 3 | 受精卵表观重编程 | — | WB、RT-qPCR |

### 甲基化阅读蛋白（MBDs）

| 靶点 | 全称 | 功能 | 检测方法 |
|------|------|------|---------|
| MeCP2 | Methyl-CpG Binding Protein 2 | 结合甲基化CpG，招募HDAC复合物形成抑制性染色质 | WB、ChIP (抗MeCP2抗体) |
| MBD1 | Methyl-CpG Binding Domain 1 | 结合甲基化DNA，与SETDB1互作介导H3K9me3 | WB、ChIP |
| MBD2 | Methyl-CpG Binding Domain 2 | 结合甲基化DNA，MeCP1复合物核心组分 | WB、ChIP |
| MBD3 | Methyl-CpG Binding Domain 3 | NuRD复合物组分，结合5hmC偏好 | WB、ChIP |
| MBD4 | Methyl-CpG Binding Domain 4 | DNA糖苷酶活性，修复T:G错配 | WB、活性试剂盒 |

## 组蛋白乙酰化机器

### 乙酰转移酶（HATs/KATs）

| 靶点 | 全称 | 修饰位点 | 功能 | 已知天然调控 |
|------|------|---------|------|-------------|
| p300 | E1A Binding Protein p300 | H3K18ac, H3K27ac, H4K5ac, H4K8ac | 转录共激活，细胞增殖分化 | 姜黄素抑制；白藜芦醇间接调控 |
| CBP | CREB Binding Protein | 同上 | 与p300高度同源，cAMP应答 | 同上；漆黄素活化 |
| PCAF | p300/CBP-Associated Factor | H3K9ac, H4K8ac | 细胞周期，DNA损伤修复 | 没食子酸抑制 |
| GCN5 | General Control of Amino Acid Synthesis 5 | H3K9ac, H3K14ac | 氨基酸代谢，细胞生长 | 蒜素调控 |
| Tip60 | Tat Interactive Protein 60kDa | H4K5ac, H4K8ac, H4K12ac, H4K16ac | DNA损伤应答，凋亡 | 白藜芦醇间接 |
| MOF | Males absent On the First | H4K16ac | 剂量补偿，DNA修复 | — |
| MOZ/MYST3 | Monocytic Leukemia Zinc Finger | H3K9ac, H4K16ac | 造血发育，HOX基因表达 | — |

### 去乙酰化酶（HDACs）

**Class I HDACs（细胞核，广泛表达）**

| 靶点 | 定位 | 功能 | 已知天然抑制剂 | 检测方法 |
|------|------|------|--------------|---------|
| HDAC1 | 核 | 转录抑制，与Sin3/NuRD/COREST复合物 | 丁酸、萝卜硫素、姜黄素 | WB、HDAC-Glo™ |
| HDAC2 | 核 | 与HDAC1高度同源，突触可塑性 | 同上 | WB |
| HDAC3 | 核 | 与NCOR/SMRT复合物，代谢调控 | 白藜芦醇（间接） | WB、活性试剂盒 |
| HDAC8 | 核/质 | 平滑肌收缩，X染色体失活 | HDDAC-8选择性抑制剂 | WB、活性试剂盒 |

**Class IIa HDACs（组织特异性，核质穿梭）**

| 靶点 | 功能 | 备注 |
|------|------|------|
| HDAC4 | 软骨发育，神经元保护 | 通过14-3-3调控核质穿梭 |
| HDAC5 | 心脏发育，骨骼肌分化 | 氧化应激响应 |
| HDAC7 | 胸腺发育，血管生成 | T细胞选择 |
| HDAC9 | 心脏功能，免疫调节 | 选择性剪接多样 |

**Class IIb HDACs**

| 靶点 | 功能 | 检测要点 |
|------|------|---------|
| HDAC6 | 细胞质微管蛋白去乙酰化，细胞运动 | 底物为α-微管蛋白（K40）和HSP90 |
| HDAC10 | 自噬调控 | — |

**Class III HDACs（Sirtuins, NAD+依赖）**

| 靶点 | 定位 | 功能 | 天然调控 | 检测试剂盒 |
|------|------|------|---------|----------|
| SIRT1 | 核/质 | 代谢调控，线粒体生物发生，寿命调控 | 白藜芦醇↑；没食子酸↑；烟酰胺↓ | SIRT1 Activity Assay Kit (荧光底物) |
| SIRT2 | 细胞质 | α-微管蛋白K40去乙酰化，细胞周期 | — | SIRT2 Activity Assay |
| SIRT3 | 线粒体 | 线粒体蛋白去乙酰化，脂肪酸氧化 | — | SIRT3 Activity Assay |
| SIRT6 | 核 | DNA修复，端粒维护，H3K9ac/H3K56ac去乙酰化 | — | SIRT6 Activity Assay |

**Class IV HDAC**

| 靶点 | 功能 |
|------|------|
| HDAC11 | 免疫调控（IL-10表达），最新发现成员 |

## 组蛋白甲基化机器

### 甲基转移酶（HMTs/KMTs）

**赖氨酸甲基转移酶（PKMTs）**

| 靶点 | 修饰位点 | 功能 | 天然调控 | 检测方法 |
|------|---------|------|---------|---------|
| EZH2 | H3K27me3 | PRC2复合物催化亚基，基因沉默 | 姜黄素↓；EGCG↓ | WB、EZH2 Methyltransferase Kit |
| G9a/EHMT2 | H3K9me1/me2 | 真染色质H3K9甲基化，基因沉默 | BIX-01294（合成抑制剂参考） | WB、 Activity Assay |
| SUV39H1 | H3K9me3 | 异染色质形成，端粒维持 | — | WB、ChIP |
| SETD1A | H3K4me3 | COMPASS复合物，HOX基因表达 | — | WB、ChIP |
| SETD2 | H3K36me3 | 转录延伸，RNA剪接，DNA错配修复 | — | WB |
| SETD7 | H3K4me1 | 非组蛋白底物（p53, TAF10, ERα） | — | WB、Activity Assay |
| DOT1L | H3K79me | 端粒沉默，DNA损伤应答 | — | DOT1L抑制剂筛选 |
| NSD1/2 | H3K36me1/me2 | Sotos综合征相关 | — | — |

**精氨酸甲基转移酶（PRMTs）**

| 靶点 | 修饰类型 | 功能 | 天然调控 |
|------|---------|------|---------|
| PRMT1 | H4R3me2a | 转录激活，转录本选择性剪接 | — |
| PRMT5 | H3R8me2s, H4R3me2s | 转录抑制，snRNP组装 | — |
| CARM1/PRMT4 | H3R17me2a, H3R26me2a | 核激素受体共激活 | — |

### 去甲基化酶（HDMs/KDMs）

**赖氨酸去甲基化酶**

| 靶点 | 底物 | 类型 | 功能 |
|------|------|------|------|
| LSD1/KDM1A | H3K4me1/me2, H3K9me1/me2 | FAD依赖 | 分化调控，上皮-间充质转化 |
| JMJD3/KDM6B | H3K27me2/me3 | JmjC (Fe2+/α-KG依赖) | 炎症响应，神经分化 |
| UTX/KDM6A | H3K27me2/me3 | JmjC | 发育调控，与MLL复合物互作 |
| JMJD2A/KDM4A | H3K9me2/me3, H3K36me2/me3 | JmjC | 激素受体共激活 |
| PHF8/KDM7B | H3K9me1/me2, H4K20me1 | JmjC | 细胞周期调控，神经发育 |
| JARID1A/KDM5A | H3K4me2/me3 | JmjC | 转录抑制，与PRC2交叉 |

## 关键试剂与公司参考

### 推荐抗体信息（ChIP-grade）

| 靶点 | 推荐克隆号 | 推荐厂家 | 货号参考 | ChIP用量 |
|------|-----------|---------|---------|---------|
| H3K4me3 | C42D8 | CST | #9751 | 5µg/ChIP |
| H3K27ac | D5E4 | CST | #8173 | 5µg/ChIP |
| H3K27me3 | C36B11 | CST | #9733 | 5µg/ChIP |
| H3K9me3 | D4W1U | CST | #13969 | 5µg/ChIP |
| H3K9ac | C5B11 | CST | #9649 | 5µg/ChIP |
| H4K16ac | EPR1000(B) | Abcam | ab109463 | 3-5µg/ChIP |
| RNA Pol II | 8WG16 | BioLegend | MMS-126R | 5µg/ChIP |
| DNMT1 | — | Abcam | ab13537 (H-300) | 适合WB(1:500) |
| HDAC1 | — | CST | #5356 (D5C6U) | 适合WB(1:1000) |
| EZH2 | — | CST | #5246 (D2C9) | 适合WB(1:1000) |
| MeCP2 | — | CST | #3456 (D10F2) | 适合WB(1:1000) |
| Normal Rabbit IgG | — | CST | #2729 | 同型对照 |
| Normal Mouse IgG | — | CST | #5415 | 同型对照 |

### 推荐试剂盒

| 用途 | 试剂盒名称 | 厂家 |
|------|-----------|------|
| DNA bisulfite conversion | EZ DNA Methylation-Gold™ Kit | Zymo Research #D5005 |
| Pyrosequencing | PyroMark Q24 System | Qiagen |
| MeDIP | Methylated DNA IP Kit | Zymo Research #D5101 |
| ChIP | SimpleChIP® Plus Kit | CST #9005 |
| Native ChIP | Native ChIP Kit | Active Motif #53016 |
| DNMT Activity | EpiQuik™ DNMT Activity/Inhibition Assay Kit | Epigentek |
| HDAC Activity | HDAC-Glo™ I/II Assay | Promega |
| SIRT1 Activity | SIRT1 Activity Assay Kit (Fluorometric) | Abcam |
| Total Histone Extraction | EpiQuik™ Total Histone Extraction Kit | Epigentek |
| Nuclear/Cytoplasmic Extraction | NE-PER™ Kit | Thermo Fisher |

## 常用 qPCR 引物设计原则

### 甲基化特异性引物（MSP）

- **原则**：在CpG岛区域设计两对引物（甲基化特异性M + 非甲基化特异性U）
- **目标差异**：M引物的CpG位点设C（保留），U引物对应位点设T（转换后）
- **Tm范围**：52-58℃
- **产物长度**：100-300bp
- **阴性对照**：使用M.SssI处理的DNA（完全甲基化）和WGA扩增DNA（非甲基化）
- **推荐工具**：MethPrimer 2.0、BiSearch

### Bisulfite 测序 PCR (BSP) 引物

- **关键原则**：引物中不包含CpG位点（避免甲基化偏倚）
- **Tm范围**：50-56℃（因为模板序列复杂性降低）
- **产物长度**：200-500bp（含10-20个CpG位点时为佳）
- **推荐工具**：MethPrimer、Bisulfite Primer Seeker (Zymo)

### ChIP-qPCR 引物

- **产物长度**：80-200bp（超声片段化后最佳扩增长度）
- **Tm范围**：58-62℃
- **GC含量**：40-60%
- **靶区域选择**：启动子区域（TSS上下游-2kb至+500bp）、已知增强子区域
- **阴性对照区域**：基因间非编码区域（如GAPDH上游5kb处）
- **推荐工具**：Primer3、NCBI Primer-BLAST

## 藏药常见疾病的关联表观靶点参考

| 疾病 | 相关的表观靶点 | 藏药提示 | 验证方法 |
|------|--------------|---------|---------|
| 肝癌 | DNMT1↑, EZH2↑, H3K27me3↑, miR-122↓ | 藏茵陈、波棱瓜、榜嘎群 | ChIP-seq/WGBS + RNA-seq |
| 胃癌 | HDAC1/2↑, H3K9me3↑, MLH1启动子甲基化 | 寒水石、石榴子、荜茇、香旱芹 | MSP/BSP + HDAC Activity |
| 结肠炎→癌 | TET2↓, NF-κBp65乙酰化↑, HDACs↑ | 诃子、木香、波棱瓜子 | HDAC-Glo + TET Activity |
| 糖尿病 | SIRT1↓, PGC-1α启动子甲基化↑, H3K9ac↓ | 红景天、沙棘、枸杞、白茅根 | SIRT1活性 + 甲基化分析 |
| 缺氧/高原病 | HIF-1α乙酰化↑, miR-210, DNA甲基化重编程 | 红景天、蕨麻、雪莲 | ChIP (anti-Ac-HIF-1α) |
| 类风湿关节炎 | HDACs活性↑↓双相, 滑膜H3K27me3改变 | 藏药浴常用组方、文冠木、秦艽花 | HDAC Activity + H3K27me3 ChIP |
| 阿尔茨海默病 | SIRT1↓, HDAC2↑, H4K12ac↓, 记忆基因启动子甲基化 | 红景天、兔耳草、河子、余甘子 | ChIP-qPCR + 焦磷酸测序 |
