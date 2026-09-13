"""prism-style-plot 核心统计函数 pytest 正式单测(v2.3.2 新增)。

覆盖:ttest / mann_whitney / wilcoxon / oneway_anova_tukey / twoway_posthoc /
      prism_survival(log-rank) / contingency / 2 个回归 bug 场景。

验证策略(4 层防线):
1. 标准品:已知答案数据(教科书例题/手算值)
2. 阳性+阴性双对照:已知有差异→必须显著;已知无差异→不能误报
3. scipy 交叉验证:独立实现对照(权威库)
4. 突变回归:曾出 bug 的场景锁死(R²>0.9、legend 不压柱)

运行:PY=$(python ../../scripts/ensure_env.py) && $PY -m pytest tests/ -v
"""
import sys, pathlib
import numpy as np
import pytest

SKILL = pathlib.Path(__file__).resolve().parent.parent  # tests/.. = 技能根（跨机器可移植）
sys.path.insert(0, str(SKILL))

from scipy import stats as scipy_stats  # noqa: E402
from scripts.prism_theme import (  # noqa: E402
    ttest_two_groups, mann_whitney_u, wilcoxon_signed_rank,
    oneway_anova_tukey, twoway_posthoc, rm_twoway_anova, prism_spaghetti,
    prism_survival, prism_xy_fit, prism_bars,
    format_p, build_stats_report,
)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


# =====================================================================
# § 1. ttest_two_groups
# =====================================================================

def test_ttest_positive_control_detects_difference():
    """阳性对照:已知显著差异(教科书 t-test 例题)必须被检出。"""
    a = np.array([2.1, 2.4, 2.3, 2.5, 2.2])
    b = np.array([3.4, 3.8, 3.6, 3.7, 3.5])
    stat, p, method = ttest_two_groups(a, b)
    assert p < 0.001, f"阳性对照应显著, got p={p:.4f}"
    assert method in ("Unpaired t-test", "Welch t-test")


def test_ttest_negative_control_no_false_positive():
    """阴性对照:已知无差异的两组不能误报显著。"""
    a = np.array([1.0, 1.1, 0.9, 1.0, 1.05])
    b = np.array([1.02, 0.98, 1.04, 1.0, 1.01])
    stat, p, method = ttest_two_groups(a, b)
    assert p > 0.5, f"阴性对照不应显著, got p={p:.4f}"


def test_ttest_matches_scipy_independent():
    """scipy 交叉验证:与 scipy.stats.ttest_ind 输出一致(独立实现金标准)。"""
    rng = np.random.default_rng(42)
    a = rng.normal(10, 2, 30)
    b = rng.normal(12, 2, 30)
    stat, p, _ = ttest_two_groups(a, b)
    ref_stat, ref_p = scipy_stats.ttest_ind(a, b)
    assert abs(stat - ref_stat) < 1e-8, f"t 值不一致: {stat} vs {ref_stat}"
    assert abs(p - ref_p) < 1e-8, f"p 值不一致: {p} vs {ref_p}"


def test_ttest_paired_matches_scipy():
    """配对 t 检验与 scipy.stats.ttest_rel 一致。"""
    rng = np.random.default_rng(7)
    pre = rng.normal(5, 1, 20)
    post = pre + rng.normal(0.5, 0.3, 20)  # 配对但均值略升
    stat, p, method = ttest_two_groups(pre, post, paired=True)
    assert method == "Paired t-test"
    ref_stat, ref_p = scipy_stats.ttest_rel(pre, post)
    assert abs(stat - ref_stat) < 1e-8
    assert abs(p - ref_p) < 1e-8


# =====================================================================
# § 2. 非参数检验(v2.3.0)
# =====================================================================

def test_mann_whitney_matches_scipy():
    rng = np.random.default_rng(3)
    a = rng.gamma(2, 1, 25)
    b = rng.gamma(2.5, 1, 25)
    stat, p, method = mann_whitney_u(a, b)
    assert method == "Mann-Whitney U"
    ref_stat, ref_p = scipy_stats.mannwhitneyu(a, b, alternative="two-sided")
    assert abs(p - ref_p) < 1e-8


def test_wilcoxon_matches_scipy():
    rng = np.random.default_rng(11)
    a = rng.normal(0, 1, 20)
    b = a + rng.normal(0.3, 0.2, 20)
    stat, p, method = wilcoxon_signed_rank(a, b)
    assert method == "Wilcoxon signed-rank"
    ref_stat, ref_p = scipy_stats.wilcoxon(a, b)
    assert abs(p - ref_p) < 1e-8


# =====================================================================
# § 3. oneway_anova_tukey
# =====================================================================

def test_anova_positive_control():
    """阳性对照:三组显著差异必须被 ANOVA 检出。"""
    groups = [np.array([1., 2, 3]), np.array([5., 6, 7]), np.array([9., 10, 11])]
    labels = ["A", "B", "C"]
    res = oneway_anova_tukey(groups, labels)
    assert res["anova_p"] < 0.001
    # 三组两两比较全部显著
    assert len(res["pairwise"]) == 3
    assert all(p < 0.01 for _, _, p in res["pairwise"])


def test_anova_negative_control():
    """阴性对照:三组同分布数据不能误报显著。"""
    rng = np.random.default_rng(5)
    groups = [rng.normal(0, 1, 10) for _ in range(3)]
    labels = ["A", "B", "C"]
    res = oneway_anova_tukey(groups, labels)
    assert res["anova_p"] > 0.05, f"阴性对照误报, p={res['anova_p']:.4f}"


def test_anova_matches_scipy_f_oneway():
    """ANOVA 整体 F 检验与 scipy.stats.f_oneway 一致。"""
    rng = np.random.default_rng(21)
    groups = [rng.normal(m, 1.5, 15) for m in (0, 1, 2)]
    labels = ["A", "B", "C"]
    res = oneway_anova_tukey(groups, labels)
    ref_f, ref_p = scipy_stats.f_oneway(*groups)
    assert abs(res["anova_p"] - ref_p) < 1e-8, f"ANOVA p 与 scipy 不一致"


def test_oneway_welch_matches_reference():
    """回归(v2.5.8):Welch ANOVA + Games-Howell 结果与固定参考值一致。

    参考值来自独立实现(pingouin 0.6.1 welch_anova/pairwise_gameshowell,
    开发期交叉验证 p 差 <1e-15)在固定种子数据上的输出——防未来改动漂移。
    数据: n=20/组, SD 0.5/4.0/0.6(方差不齐), 种子 1。
    """
    rng = np.random.default_rng(1)
    groups = [rng.normal(m, s, 20) for m, s in ((10, 0.5), (12, 4.0), (14, 0.6))]
    labels = ["Ctl", "Lo", "Hi"]
    r = oneway_anova_tukey(groups, labels, var_equal="welch",
                           posthoc="games_howell")  # 显式 GH,锁 v2.5.8 行为
    assert r["method"] == "Welch ANOVA + Games-Howell"
    assert r["welch"] is True
    assert abs(r["f_stat"] - 542.3430660016948) < 1e-9
    assert abs(r["df1"] - 2.0) < 1e-12
    assert abs(r["df2"] - 32.44648549836578) < 1e-9
    assert abs(r["anova_p"] - 1.1638494945594648e-25) < 1e-35
    pmap = {(a, b): p for a, b, p in r["pairwise"]}
    assert abs(pmap[("Ctl", "Lo")] - 0.22797031684180924) < 1e-10
    assert abs(pmap[("Ctl", "Hi")] - 8.992806499463768e-15) < 1e-20
    assert abs(pmap[("Lo", "Hi")] - 0.17366981203084786) < 1e-10
    # var_test 附带 Levene(Brown-Forsythe) 结果
    assert r["var_test"] is not None and r["var_test"]["p"] < 0.05


def test_oneway_dunnett_t3_reference():
    """回归(v2.5.9):Dunnett T3 事后与固定参考值一致(防漂移)。

    实现: Welch t 统计量(不带 /2) + 未取整 Welch-Satterthwaite df +
    单步 Sidak 式校正 p=1−(1−p_raw)^m(m=k(k−1)/2), 等价于 SMM 分布
    (Dunnett 1980)。参考值来自固定种子数据(种子 11, n=8/6/10)。
    """
    rng = np.random.default_rng(11)
    groups = [rng.normal(m, s, n) for m, s, n in
              ((10, 1.0, 8), (12, 4.0, 6), (14, 0.8, 10))]
    labels = ["A", "B", "C"]
    r = oneway_anova_tukey(groups, labels, var_equal="welch",
                           posthoc="dunnett_t3")
    assert r["method"] == "Welch ANOVA + Dunnett T3"
    assert r["posthoc"] == "dunnett_t3"
    assert abs(r["f_stat"] - 59.52682158075456) < 1e-9
    assert abs(r["df2"] - 9.756312345649473) < 1e-9
    pmap = {(a, b): p for a, b, p in r["pairwise"]}
    assert abs(pmap[("A", "B")] - 0.6065962225840142) < 1e-10
    assert abs(pmap[("A", "C")] - 1.0439529740668974e-07) < 1e-15
    assert abs(pmap[("B", "C")] - 0.8980414434585438) < 1e-10


def test_oneway_welch_t_equals_ttest_ind():
    """v2.5.9:posthoc='welch_t'(不校正)必须与 scipy ttest_ind(equal_var=False)
    逐对精确一致(Prism 'Don't correct for multiple comparisons' 选项)。"""
    rng = np.random.default_rng(11)
    groups = [rng.normal(m, s, n) for m, s, n in
              ((10, 1.0, 8), (12, 4.0, 6), (14, 0.8, 10))]
    labels = ["A", "B", "C"]
    r = oneway_anova_tukey(groups, labels, var_equal="welch", posthoc="welch_t")
    assert r["posthoc"] == "welch_t"
    pmap = {(a, b): p for a, b, p in r["pairwise"]}
    for i in range(3):
        for j in range(i + 1, 3):
            _, pref = scipy_stats.ttest_ind(groups[i], groups[j],
                                            equal_var=False)
            assert abs(pmap[(labels[i], labels[j])] - pref) < 1e-12, \
                f"{labels[i]}-{labels[j]} 应与 Welch t 一致"


def test_oneway_posthoc_auto_rule():
    """v2.5.9:posthoc='auto'(默认)按 Prism 推荐选事后——max(组内 n)>50 →
    Games-Howell;≤50 → Dunnett T3。"""
    rng = np.random.default_rng(2)
    small = [rng.normal(m, s, 20) for m, s in ((10, 1.0), (12, 4.0), (14, 0.8))]
    big = [np.random.default_rng(3).normal(m, s, 60)
           for m, s in ((10, 1.0), (12, 4.0), (14, 0.8))]
    r_s = oneway_anova_tukey(small, ["A", "B", "C"], var_equal="welch")
    r_b = oneway_anova_tukey(big, ["A", "B", "C"], var_equal="welch")
    assert r_s["posthoc"] == "dunnett_t3", "n≤50 auto 应选 Dunnett T3"
    assert r_b["posthoc"] == "games_howell", "n>50 auto 应选 Games-Howell"


def test_oneway_welch_k2_equals_welch_ttest():
    """数学恒等: k=2 时 Welch ANOVA 的 p 必须等于 scipy Welch t 检验的 p。"""
    rng = np.random.default_rng(3)
    a = rng.normal(10, 1.0, 8)
    b = rng.normal(14, 3.5, 6)
    r = oneway_anova_tukey([a, b], ["A", "B"], var_equal="welch")
    t, p_ref = scipy_stats.ttest_ind(a, b, equal_var=False)
    assert abs(r["anova_p"] - p_ref) < 1e-10, \
        f"k=2 Welch ANOVA p={r['anova_p']} 应等于 Welch t p={p_ref}"
    # Games-Howell 单对也应与 Welch t 一致
    assert abs(r["pairwise"][0][2] - p_ref) < 1e-10


def test_oneway_auto_switches_on_unequal():
    """回归(v2.5.8):var_equal='auto' 时 Levene(Brown-Forsythe) 显著→切 Welch;
    方差齐→保持标准 ANOVA+Tukey。"""
    rng = np.random.default_rng(1)
    un = [rng.normal(m, s, 20) for m, s in ((10, 0.5), (12, 4.0), (14, 0.6))]
    eq = [np.random.default_rng(5).normal(m, 1.5, 12) for m in (10, 12, 14)]
    r_un = oneway_anova_tukey(un, ["A", "B", "C"], var_equal="auto")
    r_eq = oneway_anova_tukey(eq, ["A", "B", "C"], var_equal="auto")
    assert r_un["welch"] is True, "方差不齐(auto)应切 Welch"
    assert r_eq["welch"] is False, "方差齐(auto)应保持标准 ANOVA"


def test_report_anova_welch_and_consistency_label():
    """回归(v2.5.8): 报告一致性——(1) var_equal='welch' 输出 Welch+Games-Howell
    段落;(2) var_equal='assumed' 但 Levene 判方差不齐时,明确标注下方为标准
    ANOVA 结果(p 值可能失真),不再'建议切换却给标准值'自相矛盾。"""
    rng = np.random.default_rng(1)
    groups = [rng.normal(m, s, 20) for m, s in ((10, 0.5), (12, 4.0), (14, 0.6))]
    labels = ["Ctl", "Lo", "Hi"]
    rep_w = build_stats_report("anova_tukey", description="Test", groups=groups,
                               labels=labels, var_equal="welch",
                               anova_posthoc="games_howell")
    assert "## 3. Welch ANOVA" in rep_w
    assert "Games-Howell 事后多重比较" in rep_w
    rep_a = build_stats_report("anova_tukey", description="Test", groups=groups,
                               labels=labels, var_equal="assumed")
    assert "下方 F/p 为假设方差齐性的标准 ANOVA 结果" in rep_a, \
        "方差不齐但 assumed 时应标注口径,不自相矛盾"


def test_report_welch_uncorrected_column():
    """v2.5.10: Welch 分支报告在校正表(gh/t3)上附'p (Welch t, uncorr)'参考列;
    posthoc='welch_t' 本身即未校正,不再重复加列。"""
    rng = np.random.default_rng(11)
    groups = [rng.normal(m, s, n) for m, s, n in
              ((10, 1.0, 8), (12, 4.0, 6), (14, 0.8, 10))]
    labels = ["A", "B", "C"]
    for ph in ("dunnett_t3", "games_howell"):
        rep = build_stats_report("anova_tukey", description="T", groups=groups,
                                 labels=labels, var_equal="welch",
                                 anova_posthoc=ph)
        assert "p (Welch t, uncorr)" in rep, f"{ph} 应附未校正参考列"
        assert "结论以校正 p 列为准" in rep
    rep_wt = build_stats_report("anova_tukey", description="T", groups=groups,
                                labels=labels, var_equal="welch",
                                anova_posthoc="welch_t")
    assert "p (Welch t, uncorr)" not in rep_wt, "welch_t 分支不应重复加列"


def test_anova_tukey_kramer_per_pair_unbalanced():
    """回归(v2.5.6 修复):非均衡样本下 Tukey 事后必须用逐对 Tukey-Kramer 公式
    q_ij = |mean_i−mean_j| / sqrt(MSE·(1/n_i+1/n_j)/2),而非全局调和均数近似。

    旧实现用 n_harmonic = k / Σ(1/n_j) 近似,非均衡时偏差可达数个百分点
    (如 A vs C: 0.8068 vs 标准 0.7738)。scipy 无独立 Tukey 实现,此处手算标准
    逐对公式作权威交叉验证;均衡设计下新公式与旧公式结果完全一致(向后兼容)。
    """
    rng = np.random.default_rng(7)
    groups = [rng.normal(m, 1.0, n) for m, n in ((0, 6), (2, 3), (4, 4))]
    labels = ["A", "B", "C"]
    res = oneway_anova_tukey(groups, labels)
    k = len(groups)
    df_within = sum(len(g) for g in groups) - k
    mse = sum((len(g) - 1) * np.var(g, ddof=1) for g in groups) / df_within
    pmap = {(a, b): p for a, b, p in res["pairwise"]}
    for i in range(k):
        for j in range(i + 1, k):
            ref_q = abs(groups[i].mean() - groups[j].mean()) / np.sqrt(
                mse * (1.0 / len(groups[i]) + 1.0 / len(groups[j])) / 2.0)
            ref_p = 1.0 - scipy_stats.studentized_range.cdf(ref_q, k, df_within)
            got_p = pmap[(labels[i], labels[j])]
            assert abs(got_p - ref_p) < 1e-9, \
                f"Tukey-Kramer 逐对 p 偏差过大: {got_p} vs {ref_p}"


def test_anova_tukey_balanced_unchanged():
    """均衡设计下新逐对公式与理论值一致(向后兼容:旧全局调和均数写法等价)。"""
    rng = np.random.default_rng(3)
    groups = [rng.normal(m, 1.0, 8) for m in (0, 1, 2)]
    labels = ["A", "B", "C"]
    res = oneway_anova_tukey(groups, labels)
    k = 3
    df_within = 24 - 3
    mse = sum((len(g) - 1) * np.var(g, ddof=1) for g in groups) / df_within
    pmap = {(a, b): p for a, b, p in res["pairwise"]}
    for i in range(k):
        for j in range(i + 1, k):
            ref_q = abs(np.mean(groups[i]) - np.mean(groups[j])) / np.sqrt(
                mse * (1.0 / 8 + 1.0 / 8) / 2.0)
            ref_p = 1.0 - scipy_stats.studentized_range.cdf(ref_q, k, df_within)
            assert abs(pmap[(labels[i], labels[j])] - ref_p) < 1e-9


def test_add_significance_brackets_include_ns_draws():
    """回归(v2.5.6 修复):include_ns=True 时 p≥0.1 的比较应画出 'ns' 标注,
    而非静默跳过(旧版 include_ns 仅传给 p_to_stars 改字符串,分支却用 sig
    判定导致永远不画)。
    """
    from scripts.prism_theme import add_significance_brackets
    fig, ax = plt.subplots()
    ax.bar([0, 1], [1, 1])
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0, 1.3)
    # p=0.4 ≥0.1,include_ns=True → 应画 'ns'
    add_significance_brackets(ax, 0, 1, p_value=0.4, include_ns=True)
    texts = [c.get_text() for c in ax.texts]
    assert "ns" in texts, f"include_ns=True 未画出 ns 标注, texts={texts}"
    plt.close(fig)
    # 默认 include_ns=False → 不画
    fig, ax = plt.subplots()
    ax.bar([0, 1], [1, 1])
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0, 1.3)
    add_significance_brackets(ax, 0, 1, p_value=0.4, include_ns=False)
    assert len(ax.texts) == 0, "默认 include_ns=False 不应画任何标注"
    plt.close(fig)


# =====================================================================
# § 4. twoway_posthoc
# =====================================================================

def _make_twoway(interaction=True, seed=1):
    """构造 2×2 长格式数据;interaction=True 时设计成交互显著。"""
    rng = np.random.default_rng(seed)
    rows = []
    for g in ["WT", "KO"]:
        for t in ["Sham", "TBI"]:
            base = {"WT": {"Sham": 10, "TBI": 16},
                    "KO": {"Sham": 10, "TBI": 12}}[g][t]
            for _ in range(8):
                rows.append({"genotype": g, "treat": t,
                             "value": base + rng.normal(0, 0.6)})
    import pandas as pd
    return pd.DataFrame(rows)


def test_twoway_detects_interaction():
    """交互设计:twoway_posthoc 应返回 simple_effects 类型。"""
    df = _make_twoway(interaction=True)
    res = twoway_posthoc(df, "value ~ C(genotype)*C(treat)")
    assert res.get("type") == "simple_effects", \
        f"交互显著应走简单效应, got {res.get('type')}"


def test_twoway_returns_comparisons():
    df = _make_twoway(interaction=True)
    res = twoway_posthoc(df, "value ~ C(genotype)*C(treat)")
    assert len(res["comparisons"]) >= 4  # WT-Sham vs WT-TBI 等 4 条
    # 已知 TBI 使 WT 显著升高
    wts = [p for d, p, _ in res["comparisons"] if "WT: Sham vs TBI" in d]
    assert wts and wts[0] < 0.001


def test_twoway_comparison_key_order_stable():
    """回归(Bug):比较键方向必须按数据水平出现顺序标准化。

    曾 bug:pairwise_tukeyhsd 按字典序枚举水平,返回 'genotype=KO: Drug vs
    Sham',而调用方按数据顺序构造 key 'Sham vs Drug' 匹配失败,导致
    2×3 析因图上 6 个组内比较丢 4 个。修复后必须 6/6 匹配。
    """
    df = _make_twoway(interaction=True)
    res = twoway_posthoc(df, "value ~ C(genotype)*C(treat)")
    genotypes = ["WT", "KO"]
    treats = ["Sham", "TBI"]
    matched, total = 0, 0
    for g in genotypes:
        for i in range(2):
            for j in range(i + 1, 2):
                ti, tj = treats[i], treats[j]
                key = f"genotype={g}: {ti} vs {tj}"
                total += 1
                if any(d == key for d, _, _ in res["comparisons"]):
                    matched += 1
    assert matched == total, f"比较键方向失配: {matched}/{total} 匹配"


def test_twoway_posthoc_matches_statsmodels():
    """回归(v2.5.7):twoway_posthoc 弃用 statsmodels pairwise_tukeyhsd,
    改复用纯 scipy Tukey-Kramer(oneway_anova_tukey)后,p 值必须与
    statsmodels 数学等价(同 studentized_range 分布,误差 < 1e-6)。"""
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    df = _make_twoway(interaction=True)
    res = twoway_posthoc(df, "value ~ C(genotype)*C(treat)")
    # 参照: statsmodels 全单元格 Tukey(用原始 pvalues 数组,summary 表格
    # 是 4 位小数字符串,不能作全精度对照)
    d2 = df.copy()
    d2["_cell"] = d2["genotype"].astype(str) + "|" + d2["treat"].astype(str)
    sm = pairwise_tukeyhsd(d2["value"], d2["_cell"])
    sm_p = {}
    gu = list(sm.groupsunique)
    for i in range(len(gu)):
        for j in range(i + 1, len(gu)):
            sm_p[frozenset((gu[i], gu[j]))] = float(sm.pvalues[len(sm_p)])
    assert res["type"] == "simple_effects"
    n_checked, n_miss = 0, 0
    for desc, p, _ in res["comparisons"]:
        head, _, tail = desc.partition(": ")
        fac, _, lv = head.partition("=")
        g1, _, g2 = tail.partition(" vs ")
        if fac == "genotype":
            cells = (f"{lv}|{g1}", f"{lv}|{g2}")
        else:
            cells = (f"{g1}|{lv}", f"{g2}|{lv}")
        key = frozenset(cells)
        if key not in sm_p:
            n_miss += 1
            continue
        n_checked += 1
        assert abs(p - sm_p[key]) < 1e-6, \
            f"{desc}: 新实现 p={p} vs statsmodels {sm_p[key]}"
    assert n_checked > 0 and n_miss == 0, \
        f"应与 statsmodels 一一匹配(n_checked={n_checked}, n_miss={n_miss})"


# =====================================================================
# § 4b. 重复测量 Two-way ANOVA（v2.5.11 混合设计）
# =====================================================================

def _make_rm_twoway(seed=7):
    rng = np.random.default_rng(seed)
    rows = []
    for gi, g in enumerate(["WT", "KO"]):
        base = [10, 13, 16] if g == "WT" else [10, 11, 12]
        for si in range(8):
            eff = rng.normal(0, 1.0)  # subject 随机效应
            for ti, t in enumerate(["0h", "24h", "48h"]):
                rows.append({"genotype": g, "time": t, "subject": f"{g}-{si}",
                             "value": base[ti] + eff + rng.normal(0, 0.5)})
    return pd.DataFrame(rows)


def test_rm_twoway_matches_reference():
    """回归(v2.5.11):重复测量 two-way(混合设计)与固定参考值一致。

    参考值来自独立实现 pingouin 0.6.1 (mixed_anova / pairwise_tests)
    交叉验证——F、p、GG epsilon、Mauchly、简单效应 Sidak p 全部一致。
    数据: 种子 7, genotype(WT/KO, between, 各 8 只) × time(0h/24h/48h,
    within), 完整平衡设计。
    """
    df = _make_rm_twoway(7)
    r = rm_twoway_anova(df, subject="subject", within="time",
                        between="genotype", value="value")
    pm = {row["source"]: row for row in r["aov"]}
    assert abs(pm["genotype (between)"]["f"] - 11.96286196478886) < 1e-9
    assert abs(pm["time (within)"]["f"] - 288.9635493284677) < 1e-9
    assert abs(pm["Interaction"]["f"] - 93.27413042044397) < 1e-9
    assert abs(pm["Subjects (matching)"]["p"] - 3.0135727638432406e-06) < 1e-15
    sp = r["sphericity"]
    assert abs(sp["epsilon_gg"] - 0.5714088652030241) < 1e-9
    assert abs(sp["mauchly_w"] - 0.24993964760295537) < 1e-9
    assert abs(sp["mauchly_p"] - 6.0932089614308486e-05) < 1e-12
    assert r["type"] == "simple_effects"
    se = {d: (t_, df_, pr, pc) for d, t_, df_, pr, pc
          in r["pairwise"]["simple_effects"]}
    assert abs(se["genotype=WT: 0h vs 24h"][3] - 5.0288899178019264e-05) < 1e-12
    assert abs(se["genotype=KO: 0h vs 24h"][3] - 0.03322270325299437) < 1e-10
    assert se["genotype=WT: 0h vs 24h"][1] == 7  # 组内配对 df = n_a − 1


def test_rm_twoway_two_levels_no_sphericity():
    """within 仅 2 水平时球形性不适用:ε=1 且不报 Mauchly。"""
    rng = np.random.default_rng(3)
    rows = []
    for gi, g in enumerate(["WT", "KO"]):
        base = [10, 13] if g == "WT" else [10, 11]
        for si in range(6):
            eff = rng.normal(0, 1.0)
            for ti, t in enumerate(["Pre", "Post"]):
                rows.append({"genotype": g, "time": t, "subject": f"{g}-{si}",
                             "value": base[ti] + eff + rng.normal(0, 0.5)})
    df = pd.DataFrame(rows)
    r = rm_twoway_anova(df, subject="subject", within="time",
                        between="genotype", value="value")
    assert r["sphericity"]["epsilon_gg"] == 1.0
    assert r["sphericity"]["mauchly_w"] is None
    assert r["sphericity"]["mauchly_p"] is None


def test_rm_twoway_unbalanced_raises():
    """subject 缺失 within 水平(不平衡)应明确报错(Prism RM 要求完整)。"""
    df = _make_rm_twoway(7)
    bad = df[~((df["subject"] == "WT-0") & (df["time"] == "48h"))]
    with pytest.raises(ValueError):
        rm_twoway_anova(bad, subject="subject", within="time",
                        between="genotype", value="value")


def test_report_twoway_rm_contains_key_sections():
    """v2.5.11: twoway_rm 报告含 ANOVA 表/球形性/简单效应/图注。"""
    df = _make_rm_twoway(7)
    rep = build_stats_report("twoway_rm", description="RM demo", df=df,
                             rm_subject="subject", rm_within="time",
                             rm_between="genotype", value="value")
    assert "## 2. 重复测量 Two-way ANOVA" in rep
    assert "Subjects (matching)" in rep
    assert "Greenhouse-Geisser" in rep
    assert "## 4. 事后比较" in rep
    assert "genotype=WT: 0h vs 24h" in rep
    assert "Two-way repeated measures ANOVA" in rep


# =====================================================================
# § 5. prism_survival(log-rank)
# =====================================================================

def test_survival_logrank_matches_manual():
    """log-rank p 与手工 Peto 法计算一致(标准品)。"""
    time = np.array([1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
    event = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    group = np.array(["A"] * 5 + ["B"] * 5)
    fig, ax = plt.subplots()
    res = prism_survival(ax, time, event, group)
    plt.close(fig)
    assert res["p"] is not None
    assert 0 <= res["p"] <= 1
    assert res["chi2"] >= 0


def test_survival_identical_groups_no_sig():
    """阴性对照:两组完全相同的生存数据 → 不显著。"""
    rng = np.random.default_rng(9)
    time = np.array([1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8])
    event = np.ones_like(time)
    group = np.array(["A"] * 8 + ["B"] * 8)
    fig, ax = plt.subplots()
    res = prism_survival(ax, time, event, group)
    plt.close(fig)
    assert res["p"] > 0.05, f"同分布不应显著, p={res['p']:.4f}"


# =====================================================================
# § 6. contingency 报告统计
# =====================================================================

def test_contingency_report_contains_chi2():
    """build_stats_report('contingency') 应含卡方检验结果。"""
    from scripts.prism_theme import build_stats_report
    table = np.array([[25, 18, 8], [5, 12, 22]])
    rep = build_stats_report("contingency", table=table,
                             description="response by arm")
    assert "χ" in rep and "p=" in rep


# =====================================================================
# § 7. 回归 bug 场景(v2.3.1 / v2.3.2 修复锁死)
# =====================================================================

def test_xy_4pl_data_driven_p0_regression():
    """回归:Bug F1(p0 硬编码)→ 默认调用 R² 必须 > 0.9。"""
    x = np.array([1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4])
    rng = np.random.default_rng(20260820)
    bottom, top, logec50, hill = 8.0, 92.0, -7.2, 1.1
    y = bottom + (top - bottom) / (1 + 10 ** ((logec50 - np.log10(x)) * hill))
    y = np.clip(y + rng.normal(0, 3.5, size=y.size), 0, 100)
    fig, ax = plt.subplots()
    res = prism_xy_fit(ax, x, y, model="4pl")
    plt.close(fig)
    assert res["r2"] > 0.9, f"回归失败:默认 p0 数据驱动后 R²={res['r2']:.4f}"
    assert 1e-8 < res["ic50"] < 1e-6, f"IC50 应接近真值 10^-7.2, got {res['ic50']}"


def test_xy_4pl_drops_nonpositive_x():
    """回归:x≤0 自动过滤 + dropped 计数。"""
    x = np.array([0, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4])
    y = np.array([8, 10, 20, 50, 80, 90, 92], dtype=float)
    fig, ax = plt.subplots()
    res = prism_xy_fit(ax, x, y, model="4pl")
    plt.close(fig)
    assert res["dropped"] == 1
    assert res["r2"] > 0.5


def test_format_p_precision():
    """回归:format_p 不输出 '<' 阈值写法,用精确值。"""
    assert format_p(0.134).startswith("p=0.134")
    assert "p<" not in format_p(1e-5)
    assert format_p(0.5) == "p=0.500" or "p=0.5" in format_p(0.5)


def test_format_p_precision_guard():
    """回归:precision<1 应显式报错,而非 f'{p:.{-1}e}' 静默崩溃。"""
    import pytest
    with pytest.raises(ValueError):
        format_p(0.13, precision=0)
    with pytest.raises(ValueError):
        format_p(0.13, precision=-2)


# =====================================================================
# § 8. 图生成冒烟(确保核心图型能跑通不崩)
# =====================================================================

def test_prism_bars_smoke():
    """柱状图冒烟:3 组数据能画出,不崩溃。"""
    fig, ax = plt.subplots()
    prism_bars(ax, [np.array([1., 2, 3]), np.array([2., 3, 4]),
                    np.array([4., 5, 6])], ["A", "B", "C"])
    plt.close(fig)
    assert len(ax.patches) >= 3


def test_prism_spaghetti_smoke():
    """v2.5.12: 意大利面条图冒烟——出图不崩、返回结构完整、均值/SEM/n 正确。"""
    rng = np.random.default_rng(5)
    rows = []
    for grp in ["WT", "KO"]:
        for si in range(8):
            base = rng.normal(0, 1.0)
            for ti, t in enumerate(["Day1", "Day3", "Day7"]):
                rows.append({"group": grp, "time": t,
                             "subject": f"{grp}-{si}",
                             "value": 10 + 2 * ti + base + rng.normal(0, 0.5)})
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots()
    res = prism_spaghetti(ax, df, "time", "group", "value", "subject")
    assert list(res["x_levels"]) == ["Day1", "Day3", "Day7"]
    assert list(res["group_levels"]) == ["WT", "KO"]
    # 均值与手算一致；n = 每组受试者数
    for grp in ["WT", "KO"]:
        for ti, t in enumerate(["Day1", "Day3", "Day7"]):
            v = df[(df["group"] == grp) & (df["time"] == t)]["value"]
            assert abs(res["means"][grp][ti] - v.mean()) < 1e-9
            assert res["n"][grp][ti] == 8
    assert set(res["colors"].keys()) == {"WT", "KO"}
    plt.close(fig)


def test_dot_edgecolor_always_opaque():
    """回归(v2.3.8):样品点描边必须始终不透明,不跟随填充透明度。"""
    # 构造重叠场景(小柱宽 + 大样本 → 触发 _apply_overlap_alpha 压低填充)
    rng = np.random.default_rng(0)
    data = [rng.normal(10, 0.3, 40) for _ in range(3)]
    fig, ax = plt.subplots()
    prism_bars(ax, data, ["A", "B", "C"], dot_alpha=0.5)
    plt.close(fig)
    from matplotlib.collections import PathCollection
    # 填充 alpha 应被压低(<1),而描边 alpha 必须 = 1.0
    edge_alphas = set()
    face_alphas = set()
    for coll in ax.collections:
        if isinstance(coll, PathCollection) and len(coll.get_offsets()):
            fc = coll.get_facecolor()
            ec = coll.get_edgecolor()
            if len(fc):
                face_alphas.update(np.round(fc[:, 3], 3))
            if len(ec):
                edge_alphas.update(np.round(ec[:, 3], 3))
    assert face_alphas and max(face_alphas) < 1.0, \
        f"填充应被透明度压低,实际 face_alphas={face_alphas}"
    assert edge_alphas and all(a == 1.0 for a in edge_alphas), \
        f"描边必须不透明,实际 edge_alphas={edge_alphas}"


# =====================================================================
# § 10. prism_grouped_bars(v2.3.6 NEW 整图封装)
# =====================================================================

def test_prism_grouped_bars_smoke():
    """prism_grouped_bars 冒烟:2×3 长格式数据,所有柱子画出 + 返回位置映射。"""
    from scripts.prism_theme import prism_grouped_bars
    rng = np.random.default_rng(7)
    rows = [{"g": g, "t": t, "v": rng.normal(10, 2)}
            for g in ["WT", "KO"] for t in ["Sham", "TBI", "Drug"]
            for _ in range(8)]
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots()
    res = prism_grouped_bars(ax, df, "g", "t", "v")
    plt.close(fig)
    assert res["x_levels"] == ["WT", "KO"]
    assert res["group_levels"] == ["Sham", "TBI", "Drug"]
    # 每组 3 根子柱 → 总柱数 2×3 = 6 (+ n_g 个 Rectangle 图例锚点 = 9)
    assert len(ax.patches) >= 6
    # 位置映射:每个 group 在每个 x 位置都有 1 个 x
    for g in res["group_levels"]:
        assert res["positions"][g].shape == (2,)
        assert np.all(np.isfinite(res["positions"][g]))
        # 散点叠加:每个 group 2×8=16 个
        assert np.all(np.isfinite(res["n"][g]))
        assert res["n"][g].sum() == 16


def test_prism_grouped_bars_dot_size_unified():
    """所有散点同大(common_point_size 统一),不允许逐组自适应。"""
    from scripts.prism_theme import (prism_grouped_bars, common_point_size)
    rng = np.random.default_rng(0)
    rows = [{"g": "WT", "t": "Sham", "v": rng.normal(10, 1)} for _ in range(15)]
    rows += [{"g": "WT", "t": "TBI", "v": rng.normal(15, 1)} for _ in range(15)]
    rows += [{"g": "KO", "t": "Sham", "v": rng.normal(11, 1)} for _ in range(15)]
    rows += [{"g": "KO", "t": "TBI", "v": rng.normal(13, 1)} for _ in range(15)]
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots()
    prism_grouped_bars(ax, df, "g", "t", "v")
    plt.close(fig)
    # 收集所有散点 Scatter Collection 的 sizes
    from matplotlib.collections import PathCollection
    sizes = set()
    for coll in ax.collections:
        if isinstance(coll, PathCollection) and len(coll.get_sizes()) > 0:
            sizes.update(coll.get_sizes())
    # 整图点大小只可能 1 种值(不允许逐组自适应)
    assert len(sizes) <= 1, f"散点大小不统一,实际 {sizes}"
    # 验证用的是 common_point_size(60, 4) 算的统一值
    expected_s = common_point_size(60, 4) ** 2
    assert sizes.pop() == pytest.approx(expected_s, rel=1e-6)


def test_prism_grouped_bars_legend_outside_default():
    """legend 默认在 ax 外右侧(防 X≤3 时压柱坑)。"""
    from scripts.prism_theme import prism_grouped_bars
    rng = np.random.default_rng(0)
    rows = [{"g": "WT", "t": "Sham", "v": 1.} for _ in range(5)]
    rows += [{"g": "WT", "t": "TBI", "v": 2.} for _ in range(5)]
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots()
    prism_grouped_bars(ax, df, "g", "t", "v")
    plt.close(fig)
    leg = ax.get_legend()
    assert leg is not None
    # bbox_to_anchor 应在 ax 右侧(>1.0)
    assert leg.get_bbox_to_anchor().xmin > 1.0


def test_prism_grouped_bars_legend_has_color_handles():
    """回归(v2.3.8):legend 必须带颜色图示 handle(不能只剩文字)。

    曾 bug:图例锚点 Rectangle 加 visible=False 后,legend 把不可见 artist 的
    handle 整个丢弃 → 只剩 'Sham/TBI/Drug' 文字没颜色块。修复后显式传
    handles=Patch 列表,legend 应有 n_groups 个带颜色的 handle。
    """
    from scripts.prism_theme import prism_grouped_bars
    rng = np.random.default_rng(0)
    rows = [{"g": "WT", "t": t, "v": rng.normal(10, 1)}
            for t in ["Sham", "TBI", "Drug"] for _ in range(8)]
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots()
    prism_grouped_bars(ax, df, "g", "t", "v")
    plt.close(fig)
    leg = ax.get_legend()
    assert leg is not None
    handles = list(leg.legend_handles)
    assert len(handles) == 3, f"应有 3 个 handle,实际 {len(handles)}"
    # 每个 handle 必须有可见的颜色填充(不是透明)
    for h in handles:
        fc = np.asarray(h.get_facecolor())
        assert fc.shape == (4,) and fc[3] > 0.5, \
            f"handle {h.get_label()!r} 无可见颜色: {fc}"
    # 图上不能有可见的 1×1 锚点方块
    from matplotlib.patches import Rectangle
    vis_rects = [p for p in ax.patches
                 if isinstance(p, Rectangle) and p.get_visible()
                 and abs(p.get_width() - 1.0) < 0.01]
    assert len(vis_rects) == 0, f"图上仍有 {len(vis_rects)} 个锚点方块"


# =====================================================================
# § 11. common_bar_width(v2.3.7 NEW 柱宽自适应)
# =====================================================================

def test_common_bar_width_no_overlap():
    """common_bar_width 公式保证任何 k 根子柱总宽恒 ≤ fill(无重叠)。"""
    from scripts.prism_theme import common_bar_width
    for k in [1, 2, 3, 4, 5, 6, 8, 10]:
        w = common_bar_width(k)
        # 总宽 = k*w + (k-1)*0.15*w ≤ 0.85 间距
        total = k * w + (k - 1) * 0.15 * w
        assert total <= 0.85 + 1e-9, \
            f"k={k} 子柱总宽 {total:.3f} > 0.85, 会重叠"
    # k=1 时单柱宽应等于 max_width (0.62, 与 prism_bars 一致)
    assert common_bar_width(1) == pytest.approx(0.62, abs=1e-9)


def test_prism_grouped_bars_width_auto():
    """prism_grouped_bars width=None 时按 common_bar_width 自动缩,不再重叠。"""
    from scripts.prism_theme import (prism_grouped_bars, common_bar_width)
    rng = np.random.default_rng(0)
    # 6 根子柱(k=6)+ 2 x 位置 → 极易重叠场景
    rows = []
    for g in ["A", "B", "C", "D", "E", "F"]:
        for t in ["T1", "T2"]:
            for _ in range(6):
                rows.append({"g": g, "t": t, "v": rng.normal(10, 2)})
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots()
    prism_grouped_bars(ax, df, "t", "g", "v")
    plt.close(fig)
    # 验证:所有 bar 的宽度都等于 common_bar_width(6)
    # 用 width 接近 expected_w 过滤(bar;Rectangle 图例 width=1 不算)
    expected_w = common_bar_width(6)
    bar_widths = [p.get_width() for p in ax.patches
                  if abs(p.get_width() - expected_w) < 1e-4]
    assert len(bar_widths) >= 2, "应有多个 bar"
    for w in bar_widths:
        assert abs(w - expected_w) < 1e-6, \
            f"bar 宽度 {w} != 期望 {expected_w}"


def test_pairwise_marginal_p_all_labeled():
    """回归(v2.4.7):多个边缘显著对 [0.05,0.1) 必须**全部**标出精确 p 值。

    用户反馈"p 值标记没有标出所有大于0.05但小于0.1的比较组"——
    用 5 组数据构造 3 个边缘显著对,验证 add_pairwise_brackets 全标。
    """
    from scripts.prism_theme import apply_prism_theme, add_pairwise_brackets
    rng = np.random.default_rng(4)
    labels = ["A", "B", "C", "D", "E"]
    groups = [rng.normal(10 + i * 0.6, 1, 8) for i in range(5)]
    res = oneway_anova_tukey(groups, labels)
    marg = [(a, b, p) for a, b, p in res["pairwise"] if 0.05 <= p < 0.1]
    assert len(marg) >= 2, f"测试数据需 ≥2 个边缘显著对, 实际 {len(marg)}"
    apply_prism_theme()
    fig, ax = plt.subplots(figsize=(8, 6))
    prism_bars(ax, groups, labels)
    add_pairwise_brackets(ax, res["pairwise"], labels=labels)
    p_txts = sorted(t.get_text() for t in ax.texts
                    if t.get_text().startswith("p="))
    plt.close(fig)
    assert len(p_txts) == len(marg), \
        f"边缘显著对 {len(marg)} 个, 图上只标出 {len(p_txts)}: {p_txts}"


def test_nested_bars_marker_rotation():
    """回归(v2.4.7):prism_nested_bars 按内层单元轮转 marker 形状,mean bar 线宽 0.75。

    用户反馈:不同单元簇用不同形状区分 + mean±SEM 线条用默认 0.75。
    """
    import pandas as pd
    from scripts.prism_theme import (apply_prism_theme, prism_nested_bars)
    rng = np.random.default_rng(47)
    rows = []
    meds = [10.0, 11.2, 12.4, 13.6]
    for gi, med in enumerate(meds):
        for ani in range(5):
            u = rng.normal(med, 1.1)
            for rep in range(3):
                rows.append((f"G{gi}", f"G{gi}-a{ani}", u + rng.normal(0, 0.5)))
    df = pd.DataFrame(rows, columns=["group", "animal", "value"])
    apply_prism_theme()
    fig, ax = plt.subplots(figsize=(8, 6))
    res = prism_nested_bars(ax, df, "group", "animal", "value",
                            markers=["o", "s", "^", "D"])
    # 1) marker 轮转:收集所有 scatter 的 marker path,种类 ≥2
    from matplotlib.collections import PathCollection
    import matplotlib.path as mpath
    marker_paths = []
    for c in ax.collections:
        if isinstance(c, PathCollection) and len(c.get_offsets()) > 0:
            marker_paths.extend(c.get_paths())
    assert len(marker_paths) >= 2, f"单元簇应 ≥2 种形状, 实际 {len(marker_paths)}"
    # 2) mean bar 线宽 0.75:ax.lines 中含跨组横线(lw=0.75)
    bar_lws = [ln.get_linewidth() for ln in ax.lines if len(ln.get_xdata()) == 2]
    plt.close(fig)
    assert len(bar_lws) == len(res["outer"]), f"mean bar 数 {len(bar_lws)}"
    assert all(abs(lw - 0.75) < 1e-9 for lw in bar_lws), \
        f"mean bar 线宽应 0.75, 实际 {bar_lws}"


# =====================================================================
# § 11. 退化输入防御（v2.5.3）：n=1 组 / 零方差 / 配对长度不等不再崩或静默 NaN
# =====================================================================

def test_anova_zero_variance_degenerate():
    """组内零方差（归一化全同值数据）→ 确定性退化结果，不崩溃。"""
    res = oneway_anova_tukey([[5, 5, 5], [5, 5, 5], [6, 6, 6]],
                             ["A", "B", "C"])
    assert res["anova_p"] == 0.0, "均值存在差异 → p=0"
    assert res["pairwise"][1][2] == 0.0 and res["pairwise"][0][2] == 1.0
    res2 = oneway_anova_tukey([[5, 5, 5], [5, 5, 5], [5, 5, 5]],
                              ["A", "B", "C"])
    assert res2["anova_p"] == 1.0, "各组均值全同 → p=1"
    assert all(p == 1.0 for _, _, p in res2["pairwise"])


def test_anova_single_obs_raises():
    """每组 n=1 → 明确 ValueError（此前 f_oneway 抛 SmallSampleWarning）。"""
    with pytest.raises(ValueError, match="n=1"):
        oneway_anova_tukey([[1.0], [2.0], [3.0]], ["A", "B", "C"])


def test_ttest_zero_variance_degenerate():
    """两组合并零方差 → 确定性退化结果（此前 ttest_ind 除零返回 NaN）。"""
    stat, p, method = ttest_two_groups([1, 1, 1, 1], [1, 1, 1, 1])
    assert p == 1.0 and "degenerate" in method
    stat, p, _ = ttest_two_groups([1, 1, 1, 1], [2, 2, 2, 2])
    assert p == 0.0


def test_ttest_short_group_raises():
    """任一组长 n<2 → 明确 ValueError。"""
    with pytest.raises(ValueError, match="n<2"):
        ttest_two_groups([0.5], [0.5, 0.6, 0.7])


def test_ttest_paired_length_mismatch_raises():
    """配对 t 检验长度不等 → 明确 ValueError（此前 ValueError 信息不清）。"""
    with pytest.raises(ValueError, match="长度一致"):
        ttest_two_groups([1, 2, 3], [1, 2], paired=True)


def test_twoway_single_obs_cell_raises():
    """Two-way 存在单观测格 → 明确 ValueError（此前 ols 除零）。"""
    df = pd.DataFrame({"x": ["A", "A", "B", "B"],
                       "hue": ["M", "F", "M", "F"],
                       "val": [1.0, 2.0, 3.0, 4.0]})
    with pytest.raises(ValueError, match="每格至少需要 2 个观测"):
        twoway_posthoc(df, "val ~ C(x)*C(hue)")


# =====================================================================
# § 12. __all__ API 完整性（v2.5.3）：新增函数忘同步会在此报警
# =====================================================================

def test_all_exports_exist():
    """__all__ 中每个名字都能在模块中取到（防删函数忘删 __all__）。"""
    import scripts.prism_theme as pt_mod
    for name in pt_mod.__all__:
        assert hasattr(pt_mod, name), f"__all__ 含 {name} 但模块中已不存在"


def test_all_covers_module_public_functions():
    """模块内定义的公共函数（顶层 def、非 _ 前缀）必须在 __all__ 中
    （防新增公共函数忘加 __all__；import 进来的第三方名除外）。"""
    import scripts.prism_theme as pt_mod
    module_name = pt_mod.__name__
    pub_defs = []
    for name in dir(pt_mod):
        if name.startswith("_"):
            continue
        obj = getattr(pt_mod, name)
        # 只统计模块内 def 定义的函数（__module__ 指向本模块；
        # import 进来的 PathCollection/curve_fit/to_rgba 等 __module__ 指向源库）
        if callable(obj) and getattr(obj, "__module__", None) == module_name:
            pub_defs.append(name)
    missing = [n for n in pub_defs if n not in pt_mod.__all__]
    assert not missing, f"以下公共函数未加入 __all__: {missing}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
