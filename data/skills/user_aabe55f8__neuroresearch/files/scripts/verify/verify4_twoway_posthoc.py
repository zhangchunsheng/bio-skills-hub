"""验证 4:Two-way ANOVA 事后比较(twoway_posthoc) — v2.0.35 新增"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd

from prism_theme import (twoway_posthoc, build_stats_report, write_report,
                         format_p)
from verify_common import report, SEED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
fails = []

# ---------- 4.1 交互显著 → 简单效应 ----------
try:
    r = np.random.default_rng(SEED + 100)
    rows = []
    # 构造交互:Drug 只在 48h 起效(其他时间点无效)
    for t in ["0h", "24h", "48h"]:
        for drug in ["Ctrl", "Drug"]:
            base = {"0h": 10, "24h": 10, "48h": 10}[t]
            eff = 6.0 if (t == "48h" and drug == "Drug") else 0.0
            for _ in range(6):
                rows.append({"time": t, "drug": drug,
                             "value": base + eff + r.normal(0, 1.2)})
    df = pd.DataFrame(rows)
    ph = twoway_posthoc(df, "value ~ C(time)*C(drug)")
    assert ph["type"] == "simple_effects", f"交互显著应走简单效应,实际 {ph['type']}"
    assert ph["interaction_p"] < 0.05
    comps = ph["comparisons"]
    assert len(comps) > 0
    # 检查关键对比存在:48h 内 Ctrl vs Drug
    keys = [d for d, p, s in comps]
    assert any("time=48h" in k and "Ctrl vs Drug" in k for k in keys), \
        f"缺少 time=48h 的 Ctrl vs Drug 对比: {keys}"
    # 每个 time 内都应有 Ctrl vs Drug
    for t in ["0h", "24h", "48h"]:
        assert any(f"time={t}" in k and "Ctrl vs Drug" in k for k in keys), \
            f"time={t} 缺少 Ctrl vs Drug"
    # 报告
    rep = build_stats_report("twoway", df=df,
                             formula="value ~ C(time)*C(drug)",
                             description="Interaction design (simple effects)")
    assert "## 3. 事后比较" in rep, "报告缺少事后比较章节"
    assert "simple effects" in rep
    write_report("verify4_twoway_posthoc_interact", rep, OUT)
    sig = [f"{d} {format_p(p)} ({s})" for d, p, s in comps if "48h" in d]
    report("4.1 interaction -> simple effects", True,
           f"p_inter={format_p(ph['interaction_p'])}, 48h comparisons: {sig}")
except Exception as e:
    fails.append(("4.1 simple effects", e))
    report("4.1 interaction -> simple effects", False, str(e))

# ---------- 4.2 交互不显著 → 主效应事后 ----------
try:
    r = np.random.default_rng(SEED + 101)
    rows = []
    # 纯加性设计:无交互,time 主效应显著,drug 主效应显著
    for t in ["0h", "24h", "48h"]:
        for drug in ["Ctrl", "Drug"]:
            base = {"0h": 10, "24h": 15, "48h": 20}[t] + (3 if drug == "Drug" else 0)
            for _ in range(6):
                rows.append({"time": t, "drug": drug,
                             "value": base + r.normal(0, 1.5)})
    df = pd.DataFrame(rows)
    ph = twoway_posthoc(df, "value ~ C(time)*C(drug)")
    assert ph["type"] == "main_effects", f"交互不显著应走主效应,实际 {ph['type']}"
    assert ph["interaction_p"] >= 0.05
    comps = ph["comparisons"]
    keys = [d for d, p, s in comps]
    # time 3 水平应有 3 对比较
    time_comps = [k for k in keys if k.startswith("time:")]
    assert len(time_comps) == 3, f"time 主效应应有 3 对比较,实际 {time_comps}"
    drug_comps = [k for k in keys if k.startswith("drug:")]
    assert len(drug_comps) == 1, f"drug 2 水平应有 1 对比较,实际 {drug_comps}"
    # 报告
    rep = build_stats_report("twoway", df=df,
                             formula="value ~ C(time)*C(drug)",
                             description="Additive design (main effects)")
    assert "## 3. 事后比较" in rep
    assert "main effects" in rep
    write_report("verify4_twoway_posthoc_additive", rep, OUT)
    report("4.2 no interaction -> main effects", True,
           f"p_inter={format_p(ph['interaction_p'])}, "
           f"time_pairs={len(time_comps)}, drug_pairs={len(drug_comps)}")
except Exception as e:
    fails.append(("4.2 main effects", e))
    report("4.2 no interaction -> main effects", False, str(e))

# ---------- 4.3 posthoc=False 向后兼容(报告不含事后章节) ----------
try:
    r = np.random.default_rng(SEED + 102)
    rows = []
    for t in ["A", "B"]:
        for drug in ["Ctrl", "Drug"]:
            for _ in range(4):
                rows.append({"time": t, "drug": drug,
                             "value": r.normal(10, 1.5)})
    df = pd.DataFrame(rows)
    rep_off = build_stats_report("twoway", df=df,
                                 formula="value ~ C(time)*C(drug)",
                                 description="Posthoc disabled", posthoc=False)
    assert "## 3. 事后比较" not in rep_off, "posthoc=False 不应有事后章节"
    assert "## 4. Figure Legend" in rep_off, "章节编号应保持 Figure Legend 为 4"
    rep_on = build_stats_report("twoway", df=df,
                                formula="value ~ C(time)*C(drug)",
                                description="Posthoc enabled")
    assert "## 3. 事后比较" in rep_on, "posthoc=True 应有事后章节"
    report("4.3 posthoc=False backward compat", True,
           "False 无事后章节,True 有事后章节")
except Exception as e:
    fails.append(("4.3 posthoc flag", e))
    report("4.3 posthoc=False backward compat", False, str(e))

# ---------- 4.4 旧用法回归(不传 posthoc,默认 True) ----------
try:
    r = np.random.default_rng(SEED + 103)
    rows = []
    for t in ["0h", "24h"]:
        for drug in ["Ctrl", "Drug"]:
            for _ in range(5):
                rows.append({"time": t, "drug": drug,
                             "value": r.normal(10, 1.5)})
    df = pd.DataFrame(rows)
    rep = build_stats_report("twoway", df=df,
                             formula="value ~ C(time)*C(drug)",
                             description="Default posthoc")
    assert "## 3. 事后比较" in rep, "默认应开事后比较"
    # Figure Legend 应含 Post hoc 文本
    assert "Post hoc" in rep
    report("4.4 default posthoc=True", True, "默认开启事后比较且 Legend 含 Post hoc")
except Exception as e:
    fails.append(("4.4 default", e))
    report("4.4 default posthoc=True", False, str(e))

print("\n===== Two-way 事后比较验证完成,失败数:", len(fails), "=====")
for name, e in fails:
    print(f"  FAIL {name}: {type(e).__name__}: {e}")
sys.exit(1 if fails else 0)
