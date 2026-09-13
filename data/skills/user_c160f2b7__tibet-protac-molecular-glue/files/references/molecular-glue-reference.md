# 分子胶水设计参考

## 分子胶水 vs PROTAC 核心差异速查表

| 维度 | PROTAC | 分子胶水 |
|------|--------|----------|
| 分子量 | 700-1100 Da | 300-500 Da |
| 结构 | 双功能（warhead-Linker-E3配体） | 单功能小分子 |
| 作用模式 | 诱导E3和靶蛋白同时结合 | 诱导或稳定E3-靶蛋白PPI |
| 设计逻辑 | 理性设计（基于结构） | 偏向性筛选+偶然发现 |
| Hook效应 | 明显存在 | 不典型 |
| 选择性 | 通常高（双结合决定） | 可宽可窄（依赖新PPI界面） |
| Lipinski规则 | 通常违反（大分子量） | 通常符合 |
| 口服生物利用度 | 挑战大 | 较可行 |
| 脱靶降解 | 可能（非特异性Linker暴露） | 显著（IMiD典型特性） |
| 代表药物 | ARV-110, ARV-471 | Lenalidomide, Mezigdomide |

## 已知分子胶水系统

### CRBN 依赖性胶水

| 分子 | 诱导降解的靶点 | 关键数据 |
|------|---------------|----------|
| Thalidomide | IKZF1/3（弱） | — |
| Lenalidomide | IKZF1/3, CK1α | DC50 ~50 nM (IKZF1) |
| Pomalidomide | IKZF1/3 | DC50 ~1 nM |
| CC-220 (iberdomide) | IKZF1/3, IKaros/Aiolos | DC50 <1 nM |
| CC-92480 (mezigdomide) | IKZF1/3 | 纳摩尔至皮摩尔 |
| CC-885 | GSPT1 | 强效（与lenalidomide结构差异小但完全不同的靶点谱） |
| CC-90009 | GSPT1 | 临床评估中 |
| dEpoD (dBET1类似物) | BRD4 | PROTAC/胶水边界案例 |

### 非CRBN依赖性胶水

| 系统 | E3连接酶 | 代表分子 | 靶点 |
|------|----------|----------|------|
| 芳基磺酰胺 | DCAF15 | E7820, indisulam, tasisulam | RBM39, RBM23 |
| CDK胶水 | (非E3依赖) | Roscovitine变体 | CDK12-Cyclin K界面 |
| SJ6986 | CRBN | — | GSPT1 (MMS) |
| CPD-1 | DCAF16 | — | 核蛋白泛降解 |

### 天然产物来源的分子胶水启示

| 天然产物 | 来源 | 机制 | 启发 |
|----------|------|------|------|
| Rapamycin | 链霉菌 | FKBP12-mTOR PPI稳定 | 经典天然胶水启发 |
| Cyclosporin A | 真菌 | Cyclophilin-Calcineurin PPI | 免疫抑制胶水 |
| FK506 | 链霉菌 | FKBP12-Calcineurin PPI | 与rapamycin共享FKBP12 |
| 雷公藤红素 (celastrol) | 雷公藤 | HSP90-CDC37 PPI | 天然来源PPI调节剂 |
| 姜黄素 (curcumin) | 姜黄 | 多种PPI调节 | 多靶点胶水候选 |

## 分子胶水理性设计策略

### 策略1: 已知胶水骨架的侧链发散
- 以 pomalidomide/lenalidomide 为起点
- 通过 C4/C5 位引入芳香/脂肪取代基
- 偏置靶点谱从IKZF转向GSPT1等新靶点
- 典型成功: CC-885 (lenalidomide + 芳氨取代 → GSPT1降解)

### 策略2: 藏药片段嵌入
- 将藏药活性分子的关键片段（如没食子酸的酚羟基团、绿绒蒿生物碱的芳环）接入已知胶水骨架的非关键位点
- 目的: 获得新的降解靶点选择性或降低已有脱靶效应

### 策略3: 表型筛选+靶点ID
- 使用藏药天然产物库进行细胞表型筛选（增殖抑制、分化诱导等）
- 通过CRISPR/Cas9敲除筛选+蛋白质组学鉴定被降解的靶点

### 策略4: 基于片段的从头设计
- 确定目标E3连接酶的表面口袋
- 从藏药片段库（多酚、黄酮、生物碱片段）筛选结合片段
- 通过结构生物学迭代优化
