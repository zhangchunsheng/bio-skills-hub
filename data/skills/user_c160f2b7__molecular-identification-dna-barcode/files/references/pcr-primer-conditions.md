# PCR扩增与引物设计：条形码引物总表、体系条件与失败排查

## 1. 常用植物DNA条形码引物总表

### 1.1 核基因组

| 条形码 | 引物名 | 序列（5'→3'） | 片段长度（约） | 退火温度建议 | 参考文献 |
|---|---|---|---|---|---|
| ITS（完整） | ITS5 | GGAAGTAAAAGTCGTAACAAGG | 650–750 bp | 55–58℃ | White et al. 1990 |
| | ITS4 | TCCTCCGCTTATTGATATGC | | | |
| ITS（常用组合） | ITS1 | TCCGTAGGTGAACCTGCGG | 600–700 bp | 55–58℃ | White et al. 1990 |
| | ITS4 | TCCTCCGCTTATTGATATGC | | | |
| **ITS2（药典核心条形码）** | ITS2F（S2F） | ATGCGATACTTGGTGTGAAT | 220–250 bp | 55–58℃ | Chen et al. 2010（药典9107） |
| | ITS2R（S3R） | GACGCTTCTCCAGACTACAAT | | | |
| 5.8S rDNA | 5.8S_F | TGCGTTCA AAGACTCGATG（扩增ITS1时用） | — | — | 辅助鉴定 |

> **说明**：药典9107 ITS2 通用引物为 S2F/S3R（即 ITS2F/ITS2R），产物约 220–250 bp，适合药材粉末与饮片。部分类群 ITS 存在假基因或拷贝间差异，需结合峰图判断（见测序处理文件）。

### 1.2 叶绿体基因组

| 条形码 | 引物名 | 序列（5'→3'） | 片段长度（约） | 退火温度建议 | 参考文献 |
|---|---|---|---|---|---|
| **psbA-trnH（药典辅助条形码）** | psbAF | GTTATGCATGAACGTAATGCTC | 400–800 bp（种间差异大） | 55–58℃ | Kress et al. 2005 |
| | trnHR | CGCGCATGGTGGATTCACAATCC | | | |
| matK | 3F_KIM | CGTACAGTACTTTTGTGTTTACGAG | 约 850 bp | 50–52℃ | Ki-Joong Kim 等 |
| | 1R_KIM | ACCCAGTCCATCTGGAAATCTTGGTTC | | | |
| matK（备选） | matK390F | CGATCTATTCATTCAATATTTC | 约 950 bp | 52–55℃ | Cuenoud et al. 2002 |
| | matK1326R | TCTAGCACACGAAAGTCGAAGT | | | |
| rbcL | rbcLaF | ATGTCACCACAAACAGAGACTAAAGC | 约 550 bp | 55℃ | Levin et al. 2003 |
| | rbcLaR | GTAAAATCAAGTCCACCRCG | | | |
| rbcL（完整） | rbcL1F | ATGTCACCACAAACAGAGACTAAAGC | 约 1400 bp | 55℃ | 通用 |
| | rbcL1460R | TCCTTTTAGTAAAAGATTGGGCCGAG | | | |
| trnL-trnF | trnL-c | CGAAATCGGTAGACGCTACG | 350–400 bp（含内含子） | 55℃ | Taberlet et al. 1991 |
| | trnL-d | GGGGATAGAGGGACTTGAAC | | | |
| | trnL-e | GGTTCAAGTCCCTCTATCCC | | | |
| | trnL-f | ATTTGAACTGGTGACACGAG | | | |

### 1.3 条形码选择决策（药典9107与通用场景）

| 目的 | 首选 | 备选/辅助 | 理由 |
|---|---|---|---|
| 中药材基原鉴定（9107体系） | ITS2 | psbA-trnH | 药典推荐组合；ITS2 变异高、片段短 |
| 属内/近缘种区分 | ITS（含ITS2） | psbA-trnH、matK | ITS 分辨率最高，但注意假基因 |
| 科级以上系统发育 | rbcL | matK、trnL-trnF | 保守区通用性好 |
| 疑难属（如石斛、贝母） | **多条形码组合**（ITS2+psbA-trnH+matK） | 叶绿体全基因组 | 单一标记常不足 |
| 混伪品鉴别（粉末） | ITS2 | mini-barcode | 片段短、降解样本也能扩 |

## 2. PCR反应体系（25 μL 体系为例，按比例放大至 50 μL）

| 组分 | 终浓度/用量 | 说明 |
|---|---|---|
| 10× PCR Buffer（含 Mg²⁺） | 1×（2.5 μL） | 若缓冲液不含Mg²⁺，另加MgCl₂至 1.5–2.5 mM |
| dNTP Mix | 0.2 mM each（0.5 μL of 10 mM） | 终浓度过高抑制聚合酶 |
| 正向引物 | 0.2–0.4 μM（0.5 μL of 10 μM） | 先做浓度梯度优化 |
| 反向引物 | 0.2–0.4 μM（0.5 μL of 10 μM） | |
| 模板 DNA | 10–100 ng（1–2 μL） | 药材DNA可加至100 ng；纯度高可少加 |
| Taq 聚合酶 | 0.5–1.25 U（0.1–0.25 μL of 5 U/μL） | 高保真酶（如Phusion）用于建树/克隆时 |
| 灭菌水 | 补至 25 μL | |

## 3. 标准PCR程序

```
95℃ 预变性 3–5 min
循环（30–35×）：
  94–95℃ 变性 30–45 s
  退火（引物Tm-3~-5℃） 30–45 s
  72℃ 延伸 30–60 s（约 1 kb/min）
72℃ 终延伸 5–10 min
4℃ 保存
```

**退火温度计算**：经典公式 Tm ≈ 4×(G+C) + 2×(A+T)℃（<20 bp 引物）；建议用引物合成单上的 Tm 减去 3–5℃ 起步，再以梯度 PCR（±5℃ 范围）优化。

**touchdown程序（推荐用于Tm差异大的引物对或低特异性扩增）**：

```
95℃ 3 min
前 10 个循环：94℃ 30s；退火 62℃（每循环降 0.5℃）30s；72℃ 45s
后 25 个循环：94℃ 30s；退火 57℃ 30s；72℃ 45s
72℃ 5 min
```

## 4. 扩增失败与异常结果排查表

| 现象 | 可能原因 | 排查/对策 |
|---|---|---|
| **完全无条带** | 模板量不足或抑制物；引物失效；退火温度过高；聚合酶失活 | 先确认DNA可扩（用通用引物或加对照）；稀释模板1:10再试；降低退火温度5℃；换新引物/酶 |
| **弥散smear** | 模板过多或降解；退火温度过低；循环过多 | 减少模板；提高退火温度2–5℃；减循环至25–30 |
| **非特异条带/多带** | 退火温度低；引物特异性差；Mg²⁺过高 | 提高退火温度；梯度PCR寻最适；降Mg²⁺至1.5 mM；切胶回收目标带 |
| **条带弱** | 模板少；延伸时间不足；引物浓度低 | 加模板至100 ng；延长时间；引物加到0.4 μM；增加循环至35 |
| **目标条带大小不符** | 引物结合位置特殊（内含子/假基因）；样本属ITS长度变异大的类群 | 电泳对照Marker核对大小；与NCBI比对；考虑换条形码 |
| **阴性对照出现条带** | 试剂或环境污染 | 换全套试剂；分区操作（配液区/加样区/扩增区）；UV照射超净台；重抽引物 |
| **空白提取对照PCR阳性** | 提取试剂污染 | 排查裂解缓冲液、磁珠/柱等耗材 |

## 5. 通用建议

- 每批PCR必须设**阳性对照**（已知可扩的DNA）与**阴性对照**（ddH₂O），阴性对照阳性则整批结果作废。
- 建树/克隆目的选用高保真聚合酶并加长延伸时间；仅做鉴定（Sanger测序）用普通Taq即可。
- 药材粉末样本建议 ITS2 短片段 + 提高模板量（50–100 ng）+ touchdown 程序，成功率最高。
- 多拷贝核标记（ITS）测序前先跑胶确认单一条带，防止异质拷贝混合信号。
