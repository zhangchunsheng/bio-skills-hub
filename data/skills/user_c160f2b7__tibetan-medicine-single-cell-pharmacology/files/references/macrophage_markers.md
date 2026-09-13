# 巨噬细胞M1/M2极化标志物参考

## 小鼠巨噬细胞标志物

### M1型（经典活化，促炎）

| 标志物 | 基因名 | 定位 | 功能 | 流式克隆号 |
|--------|-------|------|------|-----------|
| CD86 | Cd86 | 表面 | 共刺激分子，抗原呈递 | GL1 |
| CD80 | Cd80 | 表面 | 共刺激分子 | 16-10A1 |
| MHC-II (I-A/I-E) | H2-Aa/H2-Ea | 表面 | 抗原呈递 | M5/114.15.2 |
| iNOS/NOS2 | Nos2 | 胞质 | 一氧化氮合成，杀菌 | CXNFT |
| TNF-α | Tnf | 分泌/胞内 | 促炎因子 | MP6-XT22 |
| IL-6 | Il6 | 分泌/胞内 | 促炎因子 | MP5-20F3 |
| IL-1β | Il1b | 分泌/胞内 | 促炎因子 | NJTEN3 |
| CXCL9 | Cxcl9 | 分泌 | 趋化Th1细胞 | — |
| CXCL10 | Cxcl10 | 分泌 | 趋化Th1细胞 | — |
| CCL5 | Ccl5 | 分泌 | 招募T细胞/单核细胞 | — |
| IL-12 | Il12a/Il12b | 分泌 | 促进Th1分化 | C15.6 |

### M2型（替代活化，抗炎/组织修复）

| 标志物 | 基因名 | 定位 | 功能 | 流式克隆号 |
|--------|-------|------|------|-----------|
| CD206/MRC1 | Mrc1 | 表面 | 甘露糖受体，内吞 | C068C2 |
| CD163 | Cd163 | 表面 | 清道夫受体，血红蛋白清除 | TNKUPJ |
| CD209/DC-SIGN | Cd209a | 表面 | C型凝集素 | — |
| Arg-1 | Arg1 | 胞质 | 精氨酸酶，多胺合成 | — |
| IL-10 | Il10 | 分泌/胞内 | 抗炎因子 | JES5-16E3 |
| TGF-β | Tgfb1 | 分泌 | 免疫抑制，组织修复 | TW7-16B4 |
| CCL17 | Ccl17 | 分泌 | 趋化Th2细胞 | — |
| CCL22 | Ccl22 | 分泌 | 趋化Treg/Th2细胞 | — |
| Fizz1/RELMα | Retnla | 分泌 | M2标志，纤维化相关 | — |
| Ym1/Chi3l3 | Chil3 | 分泌 | 几丁质酶样蛋白，M2标志 | — |
| PPAR-γ | Pparg | 核内 | 脂代谢转录因子，M2检查点 | — |

### M1/M2转换相关转录因子

| 转录因子 | 促极化方向 | 机制 |
|---------|-----------|------|
| STAT1 | M1 | IFN-γ信号下游，激活Nos2/Cxcl9转录 |
| IRF5 | M1 | 促进IL-12/IL-23，抑制IL-10 |
| NF-κB (p65) | M1 | 促进TNF-α/IL-6/IL-1β |
| STAT6 | M2 | IL-4/IL-13信号下游，激活Arg1/Mrc1 |
| PPAR-γ | M2 | 代谢检查点，促进M2基因表达 |
| IRF4 | M2 | 促进M2极化抑制M1 |
| KLF4 | M2 | 与NF-κB竞争，抑制M1程序 |

---

## 人巨噬细胞标志物

### M1型

| 标志物 | 基因名 | 定位 | 备注 |
|--------|-------|------|------|
| CD86 | CD86 | 表面 | 同小鼠，流式克隆 2331(FUN-1) |
| CD80 | CD80 | 表面 | 流式克隆 L307.4 |
| HLA-DR | HLA-DRA | 表面 | 人MHC-II |
| iNOS/NOS2 | NOS2 | 胞质 | 人巨噬细胞中表达低于小鼠 |
| TNF-α | TNF | 胞内/分泌 | 流式克隆 MAb11 |
| IL-6 | IL6 | 胞内/分泌 | 流式克隆 MQ2-13A5 |
| IL-1β | IL1B | 胞内/分泌 | 流式克隆 H1b-98 |
| CXCL9 | CXCL9 | 分泌 | MIG |
| CXCL10 | CXCL10 | 分泌 | IP-10 |
| IL-12p70 | IL12A/IL12B | 分泌 | 流式克隆 C11.5 |

### M2型

| 标志物 | 基因名 | 定位 | 备注 |
|--------|-------|------|------|
| CD206/MRC1 | MRC1 | 表面 | 流式克隆 15-2 |
| CD163 | CD163 | 表面 | 流式克隆 GHI/61 |
| CD209/DC-SIGN | CD209 | 表面 | 流式克隆 DCN46 |
| IL-10 | IL10 | 胞内/分泌 | 流式克隆 JES3-9D7 |
| TGF-β1 | TGFB1 | 分泌 | 流式克隆 2D8B8 |
| CCL17 | CCL17 | 分泌 | TARC |
| CCL22 | CCL22 | 分泌 | MDC |
| Arg-1 | ARG1 | 胞质 | 需要透膜 |

---

## M1/M2评分基因集

### 推荐用于AddModuleScore/AUCell的基因集

**小鼠M1评分基因集（20基因）：**
```
Nos2, Cd86, Cd80, Cxcl9, Cxcl10, Cxcl11, Tnf, Il6, Il1b, Il12a,
Ccl5, Ccl3, Ccl4, Icam1, Irf5, Stat1, Fcgr1, Fcgr4, Lgals3, Ptafr
```

**小鼠M2评分基因集（20基因）：**
```
Mrc1, Arg1, Cd163, Il10, Tgfb1, Ccl17, Ccl22, Retnla, Chil3, Ccl24,
Pparg, Irf4, Klf4, Cd209a, Msr1, Mertk, Tgm2, Socs2, Cxcr4, Cd274
```

**人M1评分基因集：**
```
CD86, CD80, CXCL9, CXCL10, CXCL11, TNF, IL6, IL1B, IL12A, CCL5,
CCL3, CCL4, ICAM1, IRF5, STAT1, FCGR1A, FCGR3A, CD40, TLR2, TLR4
```

**人M2评分基因集：**
```
MRC1, CD163, IL10, TGFB1, CCL17, CCL22, PPARG, IRF4, KLF4, CD209,
MSR1, MERTK, TGM2, SOCS2, CXCR4, CD274, SIGLEC1, STAB1, SEPP1, CCL13
```

---

## 常用诱导方案

### M1诱导

| 物种 | 诱导剂 | 浓度 | 时间 |
|------|--------|------|------|
| 小鼠 | LPS | 100 ng/mL | 24 h |
| 小鼠 | IFN-γ | 20 ng/mL | 24 h |
| 小鼠 | LPS + IFN-γ | 100 ng/mL + 20 ng/mL | 24 h（经典M1方案） |
| 人 | LPS | 100 ng/mL | 24 h |
| 人 | IFN-γ + LPS | 20 ng/mL + 10 ng/mL | 24 h |
| 人 | GM-CSF | 50 ng/mL | 7 d（分化M1） |

### M2诱导

| 物种 | 诱导剂 | 浓度 | 时间 |
|------|--------|------|------|
| 小鼠 | IL-4 | 20 ng/mL | 24 h |
| 小鼠 | IL-13 | 20 ng/mL | 24 h |
| 小鼠 | IL-4 + IL-13 | 20 ng/mL each | 24-48h（经典M2方案） |
| 人 | IL-4 | 20 ng/mL | 24 h |
| 人 | M-CSF | 50 ng/mL | 7 d（分化M2） |
| 人 | IL-10 | 20 ng/mL | 24 h |
| 人 | TGF-β + IL-4 | 10 ng/mL + 20 ng/mL | 48 h |
