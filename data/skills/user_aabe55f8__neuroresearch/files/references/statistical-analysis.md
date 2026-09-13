# 实验数据统计分析指南

本指南用于神经科学实验数据的统计分析与投稿级图表制作。融合 nature-statistics（nature-skills 的统计模块）的严谨规范与 BioClaw 的可视化工具。

> **运行环境说明（重要）**：本 WorkBuddy 环境已验证预装 **Python 3.13**（可用 `pip install` 装入 matplotlib / seaborn / scipy / statsmodels / lifelines / pandas；scanpy 用于单细胞）。**R / GraphPad Prism 需用户本地安装**——生信差异表达与富集推荐本地 R / RStudio 运行 `scripts/bioinfo_rna_seq.R`（详见 `bioinformatics.md`）。本文件统计实现以 **Python 优先**（§三、§四-B、§六），原 R 代码保留为有 R 环境时的备选。所有脚本须实际跑通、出结果后再交付，禁止"声称跑通"。
>
> **数据入口约定**：优先接收 `.xlsx` / `.csv`（首行表头，行为样本、列为指标；分组列如 `group`、观测列如 `value`）。用 `pandas.read_excel / read_csv` 读取，缺失值先 `dropna` 或明确说明处理方式。原始凝胶/图像另存文件夹，不混入数据表。
>
> **依赖**：scipy / statsmodels / lifelines / matplotlib / seaborn；缺失按 `references/python-runtime.md` 自动安装，确保开箱即跑。

## 一、统计分析决策流程

```
拿到数据
  ↓
数据形态确认：连续/分类/计数？正态性检验？
  ↓
两组比较？
  ├── 正态+方差齐 → Student t-test
  ├── 正态+方差不齐 → Welch's t-test
  └── 非正态 → Mann-Whitney U
  ↓
多组比较？
  ├── 单因素 → one-way ANOVA + 事后检验
  ├── 双因素 → two-way ANOVA + 交互作用分析
  └── 非参数 → Kruskal-Wallis + Dunn's
  ↓
数据是否配对 / 重复测量？
  ├── 是 → 配对 t / Wilcoxon signed-rank（先判正态，见 §二）
  │        重复测量 → RM-ANOVA / 线性混合效应模型（见 §4.B.3）
  └── 否 → 进入独立组检验
  ↓
嵌套设计（同一动物/培养皿内多个观测值）？
  ├── 是 → 先按单元（动物/皿）聚合为均值，再做独立组检验（防伪重复，见 §4.B.6）
  └── 否 → 继续
  ↓
生存数据？→ Kaplan-Meier + log-rank（多因素用 Cox 回归，见 §4.B.7）
相关性？→ Pearson / Spearman
```

## 二、统计检验选择表

| 数据类型 | 比较类型 | 参数检验 | 非参数检验 |
|---------|---------|---------|-----------|
| 连续变量 | 两组独立 | Student t-test | Mann-Whitney U |
| 连续变量 | 两组配对 | Paired t-test | Wilcoxon signed-rank |
| 连续变量 | 多组独立 | One-way ANOVA | Kruskal-Wallis |
| 连续变量 | 多因素 | Two-way ANOVA | - |
| 连续变量 | 重复测量 | RM-ANOVA | Friedman |
| 分类变量 | 关联 | Chi-square | Fisher's exact |
| 生存数据 | 组间生存 | - | log-rank test |
| 两连续变量 | 相关 | Pearson | Spearman |
| 嵌套设计 | 层级嵌套 | 按亚组均值聚合后 t/ANOVA | （防伪重复） |

### 配对还是非配对？（最常出错的判定）

- **配对**：同一批样本/个体测两次或多次（病人服药前 vs 后、同一培养皿加药前后、同一动物左右侧）
- **非配对**：两组样本完全独立（两笼不同的鼠、两批不同的细胞）
- 判据：**数据行之间是否存在一一对应关系**。存在 → 配对；不存在 → 非配对
- 重复测量（同一受试者跨时间多次测量）也是配对的一种，用重复测量 ANOVA
- **不要为了"显著"而反复切换检验方法**——先定方法再算 p 值，先算再选等于 p-hacking

## 三、正态性检验

```r
shapiro.test(data$value)                     # 正态性（小样本首选）
car::leveneTest(value ~ group, data = data) # 方差齐性
```

```python
from scipy import stats
stats.shapiro(data)           # 正态性
stats.levene(*groups)         # 方差齐性
```

### 异常值检测与处理（防"删点不交代"红线）
> 与 `experiment-report.md §8.1`"删除失败/离群点不交代"红线配套：**检测规则须预先设定**，处理必须记录，禁止事后为凑显著性删点（p-hacking）。

1. **预先声明规则**（分析前定一个，写进方法）：
   - **Grubbs 检验**（小样本、单侧离群）：`pip install outlier_utils`；`from outlier_utils import Grubbs; Grubbs.test(values)`——**不建议自动删除**，仅标记。
   - **1.5×IQR 规则**（箱线图外点）：`Q1, Q3 = np.percentile(v, [25, 75]); lo, hi = Q1-1.5*(Q3-Q1), Q3+1.5*(Q3-Q1)`
   - **稳健 z 分数**（大样本）：`z = 0.6745*(v - np.median(v)) / np.median(np.abs(v - np.median(v)))`；|z|>3.5 视为可疑。
2. **处理决策**（默认保守）：
   - 可疑点先查**原始记录/实验笔记**：技术错误（移液失误/记录错）→ 剔除并记录原因；
   - 非技术错误 → **保留**，报告时用稳健统计（中位数/IQR）或注明敏感度分析；
   - 任何剔除都在 `_report.md` 与图注中注明"n=8（1 个离群值剔除，Grubbs p=0.02）"。
3. **禁止**：不预设规则、事后逐个删点试到显著。

## 四、常见检验 R 代码模板（R 备选，语法骨架）

> **定位（重要）**：本技能统计**默认走 Python 引擎**（§四-B 及 §三、§六）；本节 R 模板**仅当用户坚持用 R 或本地无 Python 时参考**，非主路径。自 v2.x 起 R 已退居「生信专用」（RNA-seq 差异表达 / 富集，见 `bioinformatics.md`），绘图也统一走 Python 引擎（`prism-style-plot.md`），不再用 R/ggplot2 出图。

```r
# 4.1 两组：独立/Welch + 非参数
t.test(value ~ group, data = df, var.equal = FALSE)
wilcox.test(value ~ group, data = df)
# 4.2 单因素 ANOVA + 事后（方差齐 Tukey；与对照比较用 Dunnett【multcomp】）
fit <- aov(value ~ group, data = df); summary(fit); TukeyHSD(fit)
# 4.3 双因素 ANOVA（重点看 group:time 交互项）
aov(value ~ group * time, data = df)
# 4.4 重复测量：线性混合效应【nlme】
lme(value ~ time * group, random = ~1|subject, data = df)
# 4.5 生存分析【survival, survminer】
survdiff(Surv(time, status) ~ group, data = df); ggsurvplot(survfit(Surv(time,status)~group,data=df), pval=TRUE)
```

## 四-B、常见检验 Python 实现（本环境优先）

> 运行：用当前环境 Python；依赖 `pip install scipy statsmodels lifelines pandas`（缺失按 `python-runtime.md` 自动安装）。

### 4.B.1 两组比较
```python
import pandas as pd, numpy as np
from scipy import stats

# 独立样本：scipy 默认 equal_var=True（Student t）；建议显式声明——
# 方差不齐/保守 → Welch's（equal_var=False）；方差齐 → Student（equal_var=True）
t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=False)
# 非参数
u_stat, p_mw = stats.mannwhitneyu(g1, g2, alternative='two-sided')
# 配对
t_p, p_p = stats.ttest_rel(before, after)
w_stat, p_w = stats.wilcoxon(before, after)
```

### 4.B.2 单因素 ANOVA + 事后检验
> **推荐直接调用绘图引擎封装** `prism_theme.oneway_anova_tukey(groups, labels, var_equal=...)`——返回含 `anova_p`/`pairwise`/`f_stat`/`df1`/`df2`/`welch`/`posthoc` 的 dict，可直接喂 `add_pairwise_brackets`；方差不齐用 `var_equal="welch"`（事后 `posthoc="games_howell"`/`"dunnett_t3"`/`"welch_t"`）或 `var_equal="auto"`（Levene 自动切换）。下方为纯 scipy 手动版：

```python
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

f_stat, p_anova = stats.f_oneway(*groups)               # 多组独立
# 事后 Tukey HSD（自动校正多重比较，推荐）
tukey = pairwise_tukeyhsd(endog=df['value'], groups=df['group'], alpha=0.05)
print(tukey)                                            # 看 reject / p-adj
```

### 4.B.3 双因素 ANOVA / 重复测量
```python
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
import statsmodels.api as sm

# 双因素（含交互）
model = smf.ols('value ~ C(group) * C(time)', data=df).fit()
print(anova_lm(model, typ=2))        # 重点看 group:time 交互项
# 重复测量（线性混合效应）
mixed = sm.mixedlm('value ~ time * group', df, groups=df['subject']).fit()
```

### 4.B.4 生存分析
```python
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

kmf = KaplanMeierFitter()
kmf.fit(durations=t, event_observed=status, label='Group')
lr = logrank_test(t[group == 0], t[group == 1],
                  event_observed_A=status[group == 0], event_observed_B=status[group == 1])
print(lr.p_value)
```

### 4.B.5 功效 / 样本量
```python
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower

# 两样本 t：d=0.8, alpha=0.05, power=0.8 → 约 26/组（solve_power 返回每组 n）
n = TTestIndPower().solve_power(effect_size=0.8, alpha=0.05, power=0.8, alternative='two-sided')
# one-way ANOVA：f=0.4, 4 组 → solve_power 返回【总样本量】约 72，即每组约 18
# ⚠️ 注意：FTestAnovaPower 与 t 检验不同，solve_power 返回的是总 nobs，需再 ÷k_groups 得每组 n
k = FTestAnovaPower().solve_power(effect_size=0.4, k_groups=4, alpha=0.05, power=0.8)
print(round(n), round(k), round(k / 4))   # 26 72 18
```

> 效应量参考：小 d=0.2 / 中 d=0.5 / 大 d=0.8；ANOVA 小 f=0.1 / 中 f=0.25 / 大 f=0.4。

### 4.B.6 嵌套设计：先按单元聚合再统计（防假重复）
> 场景：每只动物/每个培养皿取多个视野/孔，同一单元内观测不独立——**不能直接按观测数当 n**（假重复）。必须先按单元聚合为均值，再以"单元数"为 n 做组间比较。

```python
# unit = 动物ID / 培养皿ID；每 unit 多个观测值
agg = df.groupby("unit")["value"].mean()          # 单元级均值
# 之后用聚合后的均值按组别走 4.B.1（两组）或 4.B.2（多组 ANOVA+Tukey）
# 报告时注明："n = 每组的动物/培养皿数（单元级），每个单元为多次观测的均值"
```

### 4.B.7 多因素生存分析：Cox 比例风险回归（lifelines）
> 单因素组间生存比较用 log-rank（§4.B.4）；需**校正协变量/多因素**时用 Cox 回归。

```python
from lifelines import CoxPHFitter
cph = CoxPHFitter()
surv_df = df[["time", "event", "group", "age", "sex"]]   # 协变量按需增减
cph.fit(surv_df, duration_col="time", event_col="event")
cph.print_summary()          # HR、95% CI、p；HR>1 提示风险↑
# 关键前提：比例风险（PH）假设检验
cph.check_assumptions(surv_df, show_plots=False)
```

### 4.B.8 非参数事后（Dunn's）与 Welch ANOVA + Games-Howell + 效应量
> **方差不齐的多组比较（Welch ANOVA + Games-Howell / Dunnett T3）已由绘图引擎内置**（`oneway_anova_tukey(var_equal="welch", posthoc="games_howell")`），无需额外依赖；两组非参数检验引擎也内置（`mann_whitney_u` / `wilcoxon_signed_rank`）。**非参数多组（Kruskal-Wallis）的事后 Dunn's 仍需 `scikit-posthocs`**（`pip install scikit-posthocs`，缺失按 `python-runtime.md` 安装）。

```python
from scipy import stats
import scikit_posthocs as sp

h, p_kw = stats.kruskal(*groups)                    # 整体 Kruskal-Wallis
print(sp.posthoc_dunn(groups, p_adjust="bonferroni"))  # 事后 Dunn's（或 "holm"/"fdr"）

# 方差不齐的多组比较：直接走引擎（内置 Welch ANOVA + Games-Howell/Dunnett T3）
# from prism_theme import oneway_anova_tukey
# res = oneway_anova_tukey(groups, labels, var_equal="welch", posthoc="games_howell")

# 效应量（§五 必填项）
def cohens_d(a, b):                                 # 两组 Cohen's d（合并 SD）
    na, nb = len(a), len(b)
    sp_ = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    return (np.mean(a) - np.mean(b)) / sp_
# ANOVA 效应量 η² = SS_between / SS_total（statsmodels anova_lm 输出可算）
# 非参数秩效应量：ε² = H / (N² - 1) * ...（Kruskal 后报 ε² 更规范）
```

## 五、统计报告规范（nature-statistics 要求）

每处统计必须报告：
1. **检验方法**：如"one-way ANOVA followed by Tukey's post hoc test"
2. **样本量**：每组 n（区分生物学重复与技术重复）
3. **检验统计量**：t、F、χ²、U、H 值
4. **自由度**：df
5. **精确 p 值**：如 p = 0.023（而非仅 p < 0.05）
6. **效应量**：Cohen's d、η²、95% CI
7. **多重比较校正**：Tukey / Bonferroni / FDR (BH)

### 规范报告示例
> Data are presented as mean ± SEM (n = 8 per group). Statistical significance was assessed by one-way ANOVA followed by Tukey's post hoc test (F(3,28) = 12.4, p < 0.001). Treatment significantly reduced lesion volume compared with vehicle (p = 0.008, Cohen's d = 1.2, 95% CI [0.4, 2.0]).

### 常见错误警示
- ❌ 只写 p < 0.05 不写具体值
- ❌ 忽略多重比较校正（多次比较后仍用 0.05 阈值）
- ❌ 用条状图隐藏数据分布（建议叠加散点）
- ❌ 技术重复当作生物学重复（n 膨胀）
- ❌ 未检验正态性就盲目用参数检验

## 六、投稿级图表制作

> **绘图标准流程（Prism 风格，自包含）**：绘图前**先识别数据表类型**（XY / Column / Grouped / Contingency / Survival / Parts of whole / Multiple variables / Nested，判别见 `table-mapping.md`），表类型决定图型与统计方法；统计完成后再出图；默认叠加个体散点、标注精确 p 值。**推荐路径：直接调用内建引擎 `scripts/prism_theme.py`**（入口 `references/prism-style-plot.md`，已封装配色/均衡抖动/显著性 bracket/紧凑 Y 轴/报告生成，勿手搓）；纯 matplotlib 兜底见 `references/plotting-protocol.md`（规则约束 + 等效 inline 参考）。

### 6.1 常用图表类型
| 图表 | 用途 | 工具 |
|------|------|------|
| 柱状图+散点 | 组间比较 | **Python: matplotlib/seaborn**（优先）；R: ggplot2 / Prism |
| 箱线图 | 分布展示 | **Python: seaborn**（优先）；R: ggplot2 |
| 火山图 | 差异表达 | **Python: matplotlib**（优先）；R: EnhancedVolcano |
| 热图 | 表达模式 | **Python: seaborn/matplotlib**（优先）；R: pheatmap |
| PCA/UMAP | 样本聚类 | **Python: matplotlib/scanpy**（优先）；R: ggplot2 |
| KM 生存曲线 | 生存分析 | **Python: lifelines + matplotlib**（优先）；R: survminer |
| 森林图 | Meta/多指标 | Python: matplotlib；R: forestplot |
| 通路图 | 机制示意 | 手绘 / BioRender / matplotlib |

### 6.2 ggplot2 模板（投稿级，R 备选）
```r
library(ggplot2)
ggplot(df, aes(x = group, y = value, fill = group)) +
  geom_boxplot(outlier.shape = NA, width = 0.5) + geom_jitter(width = 0.15, size = 1.5) +
  theme_classic(base_size = 14) + labs(x = "Group", y = "Expression (relative)")
```
> **R 用户**：本技能自 v2.x 起已移除 R/ggplot2 绘图引擎（统一走 Python 引擎 `prism-style-plot.md`）；R 定位于生信分析（RNA-seq 差异表达 / 富集，见 `bioinformatics.md`）。若确实需要在 R 内出图，用上方 ggplot2 原生模板 + 本文件的规范（均衡抖动、组色+黑描边、0.75pt 线宽、精确 p 值）自行实现。

### 6.2b Python 箱线图+散点（matplotlib / seaborn，本环境优先）

**散点布局强制规则（所有叠加样本散点的图通用）**：镜像均衡抖动 `jitter_offsets`——每点 x = 箱/柱中心 + 抖动，要求左右对称均匀、**左右侧点数均衡**（左 n//2 点 = 右 n//2 点，n 奇数时 1 点居中）、颜色跟随组别 + 黑色描边。**禁止 `sns.stripplot`**（`jitter=True` 无法保证左右点数均衡）；投稿级一律手动 `scatter`。

**完整实现直接调用内建引擎**：`prism_theme.prism_boxplot(ax, groups, labels)` 已内置配色、均衡抖动、黑描边与 0.75pt 线宽（入口 `prism-style-plot.md` §一）；纯 matplotlib 兜底代码见 `plotting-protocol.md` Phase 3「箱线图标准画法」（仅 bundled 库不可用时手写）。

### 6.2c Python 分组柱状图+散点（Grouped 表，Prism 风格）

Grouped 表（两个分组变量，如 时间×药物）默认**分组柱状图（Mean±SEM）+ 散点**，三条强制规则（细节与完整代码见 `plotting-protocol.md` Phase 3「分组柱状图标准画法」）：

1. **柱间距 25%**：同组内相邻柱间距 = 0.25 × 柱宽（柱宽 w≈0.20–0.25，中心距 = 1.25w），用 matplotlib 手动布局，不用 seaborn `dodge`（无法精确控制）。
2. **散点柱内左右均匀分布且左右点数均衡**：每点 x = 柱中心 + 抖动，抖动用统一 `jitter_offsets(...)`（左右各 n//2 点镜像对称、n 奇数时 1 点居中，见 §6.2b），颜色跟随组别、黑色描边。
3. **errorbar 线宽与柱描边一致**：`elinewidth`/`capthick` = 柱 `edgecolor='black'` 的 `linewidth`（默认均取 `LW = 0.75` pt）。

> **实现**：引擎路径直接调用 `prism_theme.prism_bars(...)`（三条规则已内置）；纯 matplotlib 兜底见 `plotting-protocol.md` Phase 3「分组柱状图标准画法」。

两因素统计（Two-way ANOVA + 简单效应）见 §四-B；图注精确 p 值、报告同名规范见 `plotting-protocol.md` Phase 4。

### 6.3 火山图模板（R 备选）
```r
library(EnhancedVolcano)
EnhancedVolcano(res, lab = rownames(res), x = "log2FoldChange", y = "padj", pCutoff = 0.05, FCcutoff = 1)
```

### 6.3b Python 火山图
```python
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.dpi': 300})
up = (res['log2FC'] > 1) & (res['padj'] < 0.05)
dn = (res['log2FC'] < -1) & (res['padj'] < 0.05)
plt.scatter(res['log2FC'], -np.log10(res['padj']), s=8, c='grey', label='ns')
plt.scatter(res.loc[up, 'log2FC'], -np.log10(res.loc[up, 'padj']), s=8, c='red', label='up')
plt.scatter(res.loc[dn, 'log2FC'], -np.log10(res.loc[dn, 'padj']), s=8, c='blue', label='down')
plt.axhline(-np.log10(0.05), ls='--', c='k')
plt.xlabel('log2 FC'); plt.ylabel('-log10 padj'); plt.legend()
plt.tight_layout(); plt.savefig('volcano.png', dpi=300, bbox_inches='tight', pad_inches=0.15); plt.close()
```

### 6.4 出图规范

> **规则权威源**：本小节列出的 p 值格式铁律 / `0.75 pt` 线宽 / Y 轴顶部留白 `≤0.26×span` / 镜像均衡抖动等，其**权威定义以 `prism-style-plot.md`「核心规则（权威源）」为准**；本处为应用要点，规则变更只改权威源再同步此处。

**基础规范**
- 分辨率：≥300 dpi（PNG + PDF 矢量双格式，`bbox_inches='tight', pad_inches=0.15`）
- **Y 轴顶端刻度（强制，紧凑方案）**：显著性 bracket 会抬高 Y 轴顶部的留白，**老方案（`ymax*1.06/1.10 + 粗步长取整`）易留 40–50% 跨度空白、图面不协调**。新方案以**数据跨度 `span = y_max − y_min` 为基准**（bracket 高度与留白均按 span 比例），三道保险（详见 `plotting-protocol.md` Phase 3「y 轴收尾」）：
  1. bracket 紧凑布局：`y_base = y_max + 0.03*span`，`H_LAYER = 0.05*span`，竖线 0.015*span，星号 `va='bottom'` 于 `y + 0.018*span`
  2. 步长三阶段选择（从粗到细 50/20/10/5/2/1）：优先第一个同时满足**「4–9 个刻度」且「取整损失 ≤ 20% 跨度」**的步长；全不满足则在同密度候选中取损失最小者；`y_top = ceil(top_raw/step)*step` + 显式 `set_yticks`
  3. **顶部留白量化**：(ylim_top − max(bracket_tops)) / span **≤ 0.26**（设计余量 0.08 + 取整损失 ≤ 0.18）——程序化验证强制项
  ⚠️ 已知坑：**预置过高 ylim 会让 `set_nice_ylim` 早退（不重设刻度）→ 顶端无刻度**；凡预先设过 ylim 的图最后必须显式 `set_yticks` 收尾，完整对策见 `plotting-protocol.md`「y 轴收尾已知坑」。
- 字号：≥6 pt（Figure 内文字），轴标题 12–14pt、刻度 10–12pt，无衬线字体（Arial/Helvetica 类）
- **线条粗细（默认 0.75 pt，强制）**：所有线条统一默认 `LW = 0.75` pt（Nature 系投稿可接受细线，印刷/投影下清晰）——柱/箱描边、errorbar（`elinewidth`/`capthick`）、显著性 bracket、折线、散点描边；用户指定线宽时以用户为准（详见 `plotting-protocol.md` Phase 3「线条粗细总则」）
- 颜色：色盲安全色板（默认 Okabe-Ito 8 色），见 `plotting-protocol.md` Phase 3「配色」
- 比例尺/图例：完整标注；单栏图宽 90mm，双栏 180mm

**Prism 风格强制项**（详见 `references/plotting-protocol.md` Phase 3–4）
- **L 形坐标轴**：隐藏上、右边框，仅留左、下
- **个体散点叠加（强制，所有叠加样本散点的图）**：柱/箱内**左右均匀分布且左右侧点数均衡**——统一 `jitter_offsets(...)`（左右各 n//2 点镜像对称、n 奇数 1 点居中），颜色跟随组别 + 黑色描边；**禁止 `sns.stripplot` / 默认 jitter / `color='black'`**（无法保证左右点数均衡与组色）；点密集/审稿敏感时切 beeswarm（永不重叠）
- **Grouped 分组柱状图三条强制规则**：① 同组柱间**留 25% 间距**（柱宽 w≈0.20–0.25，相邻柱中心距 1.25w，手动布局勿用 seaborn dodge）；② 散点柱内镜像均衡抖动（`jitter_offsets`）；③ errorbar 线宽与柱描边一致（`elinewidth`/`capthick` = 柱 `linewidth`）（详见 `plotting-protocol.md` Phase 3）
- **形态预设（单位 cm，引擎 `get_figsize` 自动换算 inch）**：默认 tall (3×5)；square (5×5)；wide (7×5)
- **误差线类型声明（图注必须注明误差线类型和 n 值）**：柱状图 + 散点 → Mean±SEM（生物医学最常见）；柱状图无散点 → Mean±SD（更诚实）；箱线图 → 中位数/四分位距（须注明 whisker 定义，勿误报为 Mean±SEM）；小提琴图 → 核密度 + 中位数/均值；时间进程/量效曲线 → Mean±SEM
- **显著性标注**：星号 + bracket（线高 ≤ 图区 95%），多组两两比较按跨度分层堆叠防重叠。星号分级必须从最严阈值往下判断（p<0.0001→\*\*\*\*、p<0.001→\*\*\*、p<0.01→\*\*、p<0.05→\*）；**边缘显著 [0.05, 0.1) 直接标精确 p 值**（如 `p=0.073`，不标星号/ns，让读者自行判断）；**p≥0.1 默认不标注**（引擎 `p_to_stars(include_ns=False)` 行为；确需时可恢复 "ns"）
- **图注精确 p 值（铁律）**：除星号外给出 scipy 实际精确值，禁用 `<` 阈值写法（如 `p<1e-6` 禁止）；p≥0.001 写 3 位小数，p<0.001 用科学计数法保留 3 位有效数字；**下溢边界**（软件返回 `0.0`，低于双精度可表示范围）唯一诚实表示是 `p<1e-300`（Prism 同显示 `<0.0001`），`fmt_p` 开头判 `if p <= 0 or p < 1e-300: return '<1e-300'`
- **图与报告同名**：统计图 `.png/.pdf` 与统计报告 `{图名}_report.md` 同名对应，报告含描述统计、前提检验、检验统计量+自由度、事后比较、效应量、Figure Legend（对齐 §五 七要素）

## 七、样本量/功效分析（投稿必备）

```r
library(pwr)
pwr.t.test(d = 0.8, sig.level = 0.05, power = 0.8, type = "two.sample")  # two-sample t
pwr.anova.test(k = 4, f = 0.4, sig.level = 0.05, power = 0.8)            # one-way ANOVA
```

效应量参考：
- 小 d=0.2 / 中 d=0.5 / 大 d=0.8
- ANOVA: 小 f=0.1 / 中 f=0.25 / 大 f=0.4

## 八、可复现性要求

1. 记录软件版本（`python -V` / `pip freeze`；若用 R 则记 R version、ggplot2、Prism 版本）
2. 固定随机种子（`set.seed(42)`）
3. 原始数据 + 分析脚本一并归档
4. 数据文件命名规范：`2026-08-08_WB_quantification.xlsx`

## 九、统计常见术语速查

| 术语 | 含义 |
|------|------|
| padj / FDR | 多重比较校正后 p 值（BH 法） |
| SEM vs SD | 标准误 vs 标准差（SEM=SD/√n） |
| 95% CI | 95% 置信区间 |
| Cohen's d | 标准化效应量 |
| η² (eta-squared) | ANOVA 效应量 |
| Power | 检验功效（1-β） |
| Type I/II error | α（假阳性）/ β（假阴性） |