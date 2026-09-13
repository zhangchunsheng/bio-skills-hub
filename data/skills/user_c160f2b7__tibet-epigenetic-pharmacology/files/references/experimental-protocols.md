# 藏药表观遗传药理学实验方案参考

## 一、细胞活性成分处理标准方案

### 药品配制

1. 精密称量活性成分粉末（纯度 ≥95%）
2. 溶解于 DMSO，配制 10-100mM 储备液（根据溶解度）
3. 分装，-20℃或-80℃避光保存（避免反复冻融）
4. 使用前用完全培养基稀释至工作浓度，确保 DMSO 终浓度 <0.1%

### 剂量-效应预实验（确定实验浓度）

```text
Day 1: 接种细胞于 96 孔板（~5000 cells/well，根据细胞类型调整）
Day 2: 配制 6-8 个浓度的活性成分（例如 0.1, 1, 5, 10, 25, 50, 100, 200μM）
         含 DMSO 对照孔（0.1%），每个浓度 6 复孔
         处理 24h 和 48h 两个时间点
Day 3: 24h 组：CCK-8 法（10μL/well，1-4h 孵育）或 MTT 法
         OD 值检测 (CCK-8: 450nm; MTT: 570nm)
Day 4: 48h 组：同上

数据分析：GraphPad Prism 计算 IC₂₀ 和 IC₅₀
         选择亚毒性浓度（IC₂₀附近）进行后续表观实验
```

### 阳性对照药物

| 实验类型 | 阳性对照药物 | 浓度参考 | 作用 |
|---------|------------|---------|------|
| DNMT抑制 | 5-Aza-2'-deoxycytidine (5-Aza-dC) | 1-10μM (72h) | DNA甲基化整体降低 |
| HDAC抑制 | Trichostatin A (TSA) | 0.1-1μM (24h) | 组蛋白过度乙酰化 |
| HDAC抑制 | Vorinostat (SAHA) | 1-5μM (24h) | Class I/II HDAC抑制 |
| HAT抑制 | C646 (p300选择性) | 10-25μM (24h) | p300/CBP活性抑制 |
| SIRT1激活 | Resveratrol | 10-50μM (24h) | SIRT1激活兼有其他靶点 |
| EZH2抑制 | GSK126 (选择性) | 1-5μM (72h) | H3K27me3降低 |
| LSD1抑制 | Tranylcypromine (2-PCPA) | 1-5μM (48h) | H3K4me1/me2水平升高 |

## 二、DNA 甲基化检测详细方案

### 方案A：焦磷酸测序（目标基因验证型）

#### 第1步：基因组DNA提取与质控
- **推荐试剂盒**：DNeasy Blood & Tissue Kit (Qiagen) 或 Quick-DNA Miniprep Kit (Zymo)
- **质控标准**：OD260/280 1.8-2.0；浓度 >50ng/μL；总量 ≥2μg
- **完整性检查**：1%琼脂糖凝胶电泳，主带 >10kb

#### 第2步：亚硫酸盐转化
- **试剂盒**：EZ DNA Methylation-Gold™ Kit (Zymo D5005)
- **操作**：500ng DNA / 反应，按说明书设置热循环程序
- **质控**：同时转化商业对照 DNA (0% 和 100%甲基化对照)
- **回收**：M-Elution Buffer 10-20μL，-20℃保存

#### 第3步：PCR扩增
- **模板**：2μL 转化后DNA / 25μL 反应体系
- **聚合酶**：使用 bisulfite 专用酶（如 ZymoTaq Premix）
- **引物**：设计在非CpG区域（见引物设计原则）
- **PCR程序**：
  ```
  95°C 10min
  [95°C 30s → 50-56°C 40s → 72°C 40s] × 40 cycles
  72°C 7min
  4°C hold
  ```
- **质控**：2%琼脂糖凝胶确认单一条带

#### 第4步：焦磷酸测序
- **系统**：PyroMark Q24 (Qiagen)
- **测序引物**：设计在PCR引物对内部，使用链霉素亲和素珠纯化单链模板
- **CpG位点分析**：每个CpG位点输出甲基化百分比
- **质控**：bisulfite 转化效率（通过非CpG胞嘧啶的T转换率评估，应 >98%）

### 方案B：MeDIP-qPCR（全基因组级筛查性）

#### 步骤概述
1. 超声片段化：3-5μg 基因组DNA超声至 200-600bp（Covaris 或 Bioruptor）
2. 末端修复 + A-加尾 + 接头连接（如需要测序）
3. 变性（95°C 10min，冰上5min）
4. 5mC 抗体免疫沉淀（2-4μg 抗-5-甲基胞嘧啶抗体，4°C 过夜）
5. Protein A/G 琼脂糖珠捕获（2h, 4°C）
6. 洗涤 × 3（低盐 → 高盐 → TE）
7. Proteinase K 消化，酚氯仿抽提纯化
8. Input 对照：取 10% 超声后DNA 做 input
9. qPCR 定量富集倍数（Fold enrichment = 2^(Ct_input - Ct_IP) × 10%

## 三、组蛋白修饰ChIP-qPCR详细方案

### 第1步：交联与细胞收集

```
培养细胞（10⁷ 细胞 / ChIP）→ 药物处理（建议24-72h）
→ 1%甲醛室温交联10min（轻柔摇晃）
→ 甘氨酸（125mM）终止5min
→ PBS洗涤×2 → 刮取细胞 → 液氮速冻 → -80℃保存
```

> **注意**：对于组蛋白修饰，可考虑 Native ChIP（不交联），保留天然染色质结构。Native ChIP 适合 H3K4me3、H3K27me3 等高度稳定的修饰标记。

### 第2步：染色质制备与片段化

1. 细胞沉淀 → 重悬于 1mL 裂解缓冲液（含蛋白酶抑制剂 cocktail，以及 HDAC 抑制剂 TSA 100nM 保护乙酰化信号）
2. 冰上裂解 10min
3. 超声片段化（推荐参数，以实际优化为准）：
   - 超声仪：Bioruptor Pico / Diagenode
   - 条件：30s ON / 30s OFF × 10-15 cycles
   - 目标大小：200-600bp（约 80% 的片段在此范围）
4. 验证：取 5μL 逆转交联 + RNase A → 蛋白酶K → 酚氯仿抽提 → 1.5% 琼脂糖凝胶电泳
5. 每个 ChIP 取 25-50μg 染色质（约相当于 1-2×10⁶ 细胞）

### 第3步：免疫沉淀

```
染色质 25-50μg → Pre-clear (Protein A/G beads, 30min, 4°C)
→ 加入 5μg 目标抗体（或对照IgG），4°C 过夜
→ 加入 30μL Protein A/G磁珠，2h, 4°C
→ 磁力架回收 → 洗涤：
  1. 低盐洗涤缓冲液 × 1
  2. 高盐洗涤缓冲液 × 1
  3. LiCl 洗涤缓冲液 × 1
  4. TE 洗涤缓冲液 × 2
→ Elution缓冲液（1% SDS/0.1M NaHCO₃）室温洗脱 30min × 2
→ 逆转交联：65°C 4-6h（或过夜）
→ RNase A (30min, 37°C) → 蛋白酶K (2h, 55°C)
→ 酚氯仿抽提 → 乙醇沉淀 → 重悬于 30μL TE
```

### 第4步：qPCR 分析

```
反应体系（20μL）：
  SYBR Green Master Mix     10μL
  前引物 (10μM)             0.5μL
  后引物 (10μM)             0.5μL
  DNA模板                    2μL (ChIP DNA / Input DNA 1:10稀释)
  ddH₂O                     up to 20μL

qPCR程序：
  95°C 10min
  [95°C 10s → 60°C 30s → 72°C 30s + plate read] × 40 cycles
  溶解曲线 65°C→95°C (step 0.5°C/5s)

数据分析方法：
  Method 1 - %Input:      %Input = 2^(Ct_Input - Ct_ChIP) × 稀释因子 × 100%
  Method 2 - Fold Enrichment:  2^(Ct_IgG - Ct_ChIP)
  Method 3 - ΔΔCt (对比给药组 vs 对照组):
  Relative enrichment = 2 ^ [Ct_chip_sample - Ct_input_sample) - (Ct_chip_ctrl - Ct_input_ctrl)]
```

### 质量控制标准

| 指标 | 合格标准 |
|------|---------|
| IgG 信号 | %Input < 1% |
| 阳性对照基因富集 | Fold enrichment > 5 |
| 生物学重复 CV | < 15% |
| 技术重复 Ct SD | < 0.5 |
| 超声片段化 | 200-600bp 为主区域 |
| 抗体特异性 | 有文献报道的 ChIP-grade 验证 |

## 四、HDAC/DNMT 酶活性检测方案

### HDAC 总活性检测（荧光法，以 HDAC-Glo™ I/II为例）

**原理**：HDAC去乙酰化 → 底物被开发荧光素酶 → 发光信号

**步骤**：
1. 提取核蛋白（NE-PER Kit, Thermo Fisher）
2. 蛋白定量（BCA法），调整至 1-2μg/μL
3. 每孔加 25μg 核蛋白（96孔板）
4. 加入 25μL HDAC-Glo™ 试剂
5. 室温避光孵育 10-30min
6. 读板（发光模式，integration time 0.5-1s）
7. 对照设置：
   - 阳性抑制对照：TSA (1μM)
   - 阴性对照：仅缓冲液
   - 空白对照：无蛋白提取物

**结果计算**：
```
HDAC活性(%) = (RLU_sample - RLU_blank) / (RLU_ctrl - RLU_blank) × 100%
```

## 五、蛋白质免疫印迹（WB）关键参数

### 表观修饰检测的特殊考虑

| 注意事项 | 说明 |
|---------|------|
| 组蛋白提取专用缓冲液 | 含 HDAC 抑制剂 cocktail（TSA + NaButyrate） |
| 分离胶浓度 | 15% SDS-PAGE（组蛋白 ~15kDa） |
| 转膜时间 | 半干转 15min / 湿转 30min (PVDF膜, 0.22μm) |
| 封闭液 | 5% BSA（不用脱脂奶粉，因磷酸化抗体可能交叉反应） |
| 一抗稀释液 | 5% BSA/TBST，4°C 过夜 |
| 内参选择 | H3（总组蛋白水平）或 β-actin / GAPDH |
| 关键条带 | 应标注分子量 marker 确认特异性 |

### 组蛋白修饰常见条带位置

| 修饰标记 | 分子量 (kDa) | 备注 |
|---------|-------------|------|
| H3 (总) | ~17 | 内参 |
| H3K4me3 | ~17 | 剪切H3，很可能出现双条带 |
| H3K9ac | ~17 | 与 H3K14ac 交叉反应可能 |
| H3K27me3 | ~17 | 大修饰可导致慢迁移 |
| H4K16ac | ~14 | H4迁移通常快于H3 |
| pan-Acetyl H3 | ~17 | 全局H3乙酰化 |
| pan-Acetyl H4 | ~14 | 全局H4乙酰化 |

## 六、统计分析决策树

```text
实验数据
    │
    ├── 是否符合正态分布（Shapiro-Wilk 检验）？
    │   ├── 是 → 方差齐性（Levene检验）？
    │   │   ├── 是 → 两组比较 → 非配对 t检验
    │   │   │   └── 多组比较 → One-way ANOVA + Tukey HSD
    │   │   └── 否 → Welch's t检验 / Welch's ANOVA
    │   └── 否 → 两组比较 → Mann-Whitney U检验
    │       └── 多组比较 → Kruskal-Wallis + Dunn事后检验
    │
    ├── 剂量-效应关系 → 非线性回归（四参数logistic曲线）
    │
    ├── 相关性分析 → Pearson（正态）/ Spearman（非正态）
    │   └── 甲基化-表达相关性 → 线性回归 + 95%CI
    │
    └── 多重比较校正 → BH法 / Bonferroni
```

## 七、实验方案时间表范例

### 完整机制研究（细胞水平，约 4-6 周）

| 周次 | 实验内容 |
|------|---------|
| 第1周 | 细胞培养建立；活性成分IC₂₀/IC₅₀测定；阳性和阴性对照组设定 |
| 第2周 | 活性成分处理细胞（选定浓度 × 多个时间点）；RNA提取 + RT-qPCR筛选 |
| 第3周 | 剂量依赖实验（含阳性对照）；核蛋白提取 + HDAC/DNMT活性检测；WB验证蛋白表达 |
| 第4周 | ChIP-qPCR（靶基因组蛋白修饰分析）；DNA提取 + 亚硫酸盐转化 + BSP/焦磷酸测序 |
| 第5周 | 补充实验（抑制剂组合、siRNA敲减验证、回复实验）；重复验证关键结果 |
| 第6周 | 数据整合分析；统计分析和图表制作；结果讨论与论文撰写 |
