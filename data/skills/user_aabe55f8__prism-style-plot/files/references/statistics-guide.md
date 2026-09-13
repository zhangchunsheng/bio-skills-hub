# 统计方法选择指南（Phase 2 依据）

本文件回答两个问题：**该用哪个检验**、**显著性怎么标注**。核心原则：统计方法由数据结构决定，不是由用户的偏好决定——方法选错，再小的 p 值也没有意义。

## 一、方法选择决策树

```
第一步：数据是什么表？
│
├── Survival 表 → log-rank 检验（两组或多组）
├── Contingency 表 → 卡方检验（期望频数≥5）；2×2 小样本 → Fisher 精确检验
├── Parts of whole 表 → 通常不做检验
├── XY 表 → 线性/非线性回归（检验斜率≠0、比较两组拟合）
├── Multiple variables 表 → 按假设选择回归/多元方法
├── Nested 表 → 按亚组均值聚合后做 t 检验/ANOVA（防伪重复）
│
└── Column / Grouped 表（最常见，重点）：
    │
    ├── 1 个分组变量（Column 表）
    │   ├── 只有 2 组
    │   │   ├── 独立样本 → 正态？→ 是：非配对 t 检验
    │   │   │                             → 否/小样本：Mann-Whitney U
    │   │   └── 配对设计（同一批样本前后测）→ 差值正态？→ 是：配对 t 检验
    │   │                                                        → 否：Wilcoxon 符号秩检验
    │   └── ≥3 组
    │       ├── 方差齐 → One-way ANOVA + Tukey 事后检验
    │       └── 方差不齐 → Welch ANOVA + Games-Howell 事后检验
    │
    └── 2 个分组变量（Grouped 表）→ Two-way ANOVA
        ├── 独立样本 → 常规 Two-way ANOVA（主效应×2 + 交互效应）
        └── 重复测量 → 重复测量 Two-way ANOVA
```

## 二、关键判定规则

### 配对还是非配对？（最常出错的判定）

- **配对**：同一批样本/个体测两次或多次（病人服药前 vs 后、同一培养皿加药前后、同一动物左右侧）
- **非配对**：两组样本完全独立（两笼不同的鼠、两批不同的细胞）
- 判据：**数据行之间是否存在一一对应关系**。存在 → 配对；不存在 → 非配对
- 重复测量（同一受试者跨时间多次测量）也是配对的一种，用重复测量 ANOVA

### 正态性与方差齐性

- 小样本（每组 n<30）用 Shapiro-Wilk 检验正态性，Levene 检验方差齐性
- 正态性不满足时：两组 → 非参数检验；多组 → Kruskal-Wallis + Dunn 事后检验（这是 One-way ANOVA 的非参数替代）
- **不要为了"显著"而反复切换检验方法**——先定方法再算 p 值，先算再选等于 p-hacking

### 多重比较的硬性规则

- **≥3 组比较严禁两两 t 检验**（A-B、A-C、B-C 各做一次 t 检验会把假阳性率放大到约 1-(0.95)³≈14%）
- 正确做法：ANOVA 显著后再做事后检验（Tukey 控制整体错误率）
- 图上标注的事后比较组数应明确告知用户；若用户只关心"每个处理 vs Control"，可用 Dunnett 检验（更敏感）

## 三、显著性星号规范

**v2.0.17-21 混合标注规则**（本技能出图默认，见 Phase 3）：

| p 值范围 | 图上标注 | 说明 |
|---|---|---|
| p < 0.0001 | \*\*\*\* | 极显著（星号） |
| 0.0001 ≤ p < 0.001 | \*\*\* | 极显著（星号） |
| 0.001 ≤ p < 0.01 | \*\* | 高度显著（星号） |
| 0.01 ≤ p < 0.05 | \* | 显著（星号） |
| **0.05 ≤ p < 0.1** | **精确 p 值**（如 `p=0.073`）| **边缘显著/趋势：直接标 p 值**（v2.0.17 起），让读者自行判断 |
| **p ≥ 0.1** | **不标注** | v2.0.16 起默认不标 ns；`include_ns=True` 可恢复 "ns" 文本 |

- 星号 + 连接线（bracket）标注被比较的两组；**bracket 自动分层防重叠**，层高 0.055 span（`add_pairwise_brackets`）
- **标注底部按类型分偏移**（v2.0.25）：星号底在横线下 0.03 span（骑线，由 -0.02 加深）、精确 p 值底在横线上（'p' descender 自然垂下）
- 精确 p 值展示：正文/图注中可写 p=0.023（`format_legend` 自动包含全部精确 p 值）；图上仅在边缘显著区间 [0.05,0.1) 直接标 p 值
- 期刊对星号阈值的定义有差异（有些期刊用 p<0.05/\*、p<0.01/\*\*、p<0.001/\*\*\*），画图前若用户有目标期刊，按期刊要求调整；没有则用上表

## 四、描述统计与误差线规范

| 场景 | 默认误差线 | 说明 |
|---|---|---|
| 柱状图 + 散点 | Mean ± SEM | SEM 展示"均值估计的精度"，生物医学论文最常见 |
| 柱状图（无散点） | Mean ± SD | SD 展示数据离散度；无散点时用 SD 更诚实 |
| 箱线图 | 中位数 ± IQR（须注明） | 展示分布；须在图注说明 whisker 定义 |
| 小提琴图 | 核密度 + 中位数/均值 | 展示完整分布形态 |
| 时间进程/量效曲线 | Mean ± SEM | 沿曲线加误差棒或阴影 |

**无论选哪种，图注（Figure Legend）必须注明误差线类型和 n 值**，这是审稿人的标准检查项。

## 五、结果展示规则

- 每次统计输出应包含：检验方法、检验统计量（t、F、U、χ² 等）、自由度（如适用）、精确 p 值、显著性星号
- p 值格式：**一律输出实际精确值，绝不使用 `<` 阈值写法**（禁用 p<1e-6、p<0.001 等）。p≥0.001 保留 3 位小数（p=0.034）；p<0.001 用科学计数法保留 3 位有效数字（p=2.04e-4、p=3.71e-9，指数去前导零）。不写 p=0.000 这类假精度
- 唯一例外：**数值下溢**（scipy 返回 0.0 / 非有限，低于双精度可表示范围）时输出 `p=<1e-300`（Prism 同显示 <0.0001，v2.0.4 铁律），绝不写 p=0.000
- 效应量（Cohen's d、η²）按用户要求或期刊要求补充
- 用户自带统计结果时：跳过计算，但必须核对星号阈值与本文档一致，并在图注注明统计来源

## 六、常用实现速查（Python）

> 注：以下为通用参考片段；本技能的内置实现（`prism_theme.py` 的 `oneway_anova_tukey`、
> `build_stats_report`、`prism_survival` 等）仅依赖 scipy / statsmodels，**无需 lifelines**，
> 出图时直接调用对应封装函数即可。

```python
# 非配对 t 检验
from scipy import stats
t, p = stats.ttest_ind(group_a, group_b, equal_var=True)

# 配对 t 检验
t, p = stats.ttest_rel(before, after)

# 非参数
u, p = stats.mannwhitneyu(a, b)            # 两组独立
w, p = stats.wilcoxon(before, after)       # 两组配对
h, p = stats.kruskal(a, b, c)              # 多组非参数

# One-way ANOVA + Tukey（推荐 statsmodels，直接给出逐对比较与星号）
from statsmodels.stats.multicomp import pairwise_tukeyhsd
res = pairwise_tukeyhsd(all_values, group_labels, alpha=0.05)
print(res.summary())                        # 每对比较的 p 值

# 卡方 / Fisher
chi2, p, dof, expected = stats.chi2_contingency(table)
odds, p = stats.fisher_exact(table_2x2)

# Two-way ANOVA（statsmodels）
import statsmodels.api as sm
from statsmodels.formula.api import ols
model = ols("value ~ C(time) * C(drug)", data=df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

# 生存分析（lifelines）
from lifelines import KaplanMeierFitter, statistics as lifelines_stats
kmf = KaplanMeierFitter(); kmf.fit(durations, event_observed)
result = lifelines_stats.logrank_test(durations_a, durations_b,
                                      event_observed_a, event_observed_b)
```

注意：`pairwise_tukeyhsd` 的 p 值已做多重比较校正，可直接用于星号标注；不要对校正后的 p 再乘比较次数。
