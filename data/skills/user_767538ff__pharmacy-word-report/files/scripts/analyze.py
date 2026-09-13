# -*- coding: utf-8 -*-
"""
药品使用分析聚合脚本（药库出库 Excel -> analysis_results.json + figs/）

用法:
    python analyze.py <input.xlsx> [workdir]

参数:
    input.xlsx   源 Excel（列见 COLMAP）
    workdir       输出目录，默认取 input.xlsx 所在目录；figs/ 与 analysis_results.json 写于此

输出:
    <workdir>/analysis_results.json
    <workdir>/figs/top15_drug.png, atc1.png, top15_dept.png, pareto.png
"""
import pandas as pd, numpy as np, json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---------- 列名映射（如用户文件列名不同，在此修改） ----------
COLMAP = {
    "dept": "科室",
    "unit": "入库单位",
    "qty": "数量",
    "price": "单价",
    "amount": "金额",
    "insurance": "医保编码",
    "generic": "通用名",
    "atc1": "最终ATC分类1级",
    "atc2": "最终ATC分类2级",
    "atc3": "最终ATC分类3级",
    "atc4": "最终ATC分类4级",
}
NUMERIC = ["qty", "price", "amount"]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    SRC = sys.argv[1]
    OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(SRC))
    FIG = os.path.join(OUT, "figs")
    os.makedirs(FIG, exist_ok=True)

    print("Loading:", SRC)
    raw = pd.read_excel(SRC, dtype=str)
    df = pd.DataFrame()
    for k, col in COLMAP.items():
        if col not in raw.columns:
            raise SystemExit(f"缺失列: {col}（请在 COLMAP 中校正列名）")
        df[k] = raw[col]
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    R = {}
    R["meta"] = {
        "source": "药库出库",
        "period": "参见文件名(YYYYMM)",
        "rows": int(len(df)),
        "depts": int(df["dept"].nunique()),
        "drugs": int(df["generic"].nunique()),
        "total_amount": float(df["amount"].sum()),
        "total_qty": float(df["qty"].sum()),
    }

    # ---------- 1) 总体：按通用名汇总 ----------
    g = df.groupby("generic", as_index=False).agg(
        金额=("amount", "sum"), 数量=("qty", "sum"), 记录数=("amount", "size"))
    def safe_mode(s):
        s2 = s.dropna()
        return s2.value_counts().index[0] if len(s2) else np.nan
    for atc in ["atc1", "atc2", "atc3", "atc4"]:
        g[atc] = g["generic"].map(df.groupby("generic")[atc].agg(safe_mode))
    def safe_unit(n):
        u = df[df["generic"] == n].groupby("unit")["amount"].sum().sort_values(ascending=False)
        return u.index[0] if len(u) else ""
    g["主要入库单位"] = g["generic"].map(safe_unit)
    g = g.sort_values("金额", ascending=False).reset_index(drop=True)
    tot = g["金额"].sum()
    g["占比"] = g["金额"] / tot * 100
    g["累计占比"] = g["占比"].cumsum()
    R["top50"] = g.head(50).to_dict(orient="records")
    R["top50_total_share"] = float(g.head(50)["占比"].sum())

    # ---------- 2) ATC 分类 ----------
    def atc_summary(col):
        a = df.groupby(col, as_index=False).agg(
            金额=("amount", "sum"), 品种数=("generic", "nunique"),
            科室数=("dept", "nunique"), 记录数=("amount", "size"))
        a = a.sort_values("金额", ascending=False).reset_index(drop=True)
        a["占比"] = a["金额"] / tot * 100
        a["累计占比"] = a["占比"].cumsum()
        return a
    atc1 = atc_summary("atc1"); atc2 = atc_summary("atc2")
    atc3 = atc_summary("atc3"); atc4 = atc_summary("atc4")
    R["atc1"] = atc1.to_dict(orient="records")
    R["atc2"] = atc2.to_dict(orient="records")
    R["atc3_top"] = atc3.head(30).to_dict(orient="records")
    R["atc4_top"] = atc4.head(30).to_dict(orient="records")
    top_in_atc1 = {}
    for cat in atc1["atc1"]:
        sub = g[g["atc1"] == cat].head(3)
        top_in_atc1[cat] = sub[["generic", "金额", "占比"]].rename(columns={"generic": "通用名"}).to_dict(orient="records")
    R["top_in_atc1"] = top_in_atc1

    # ---------- 3) 科室 ----------
    d = df.groupby("dept", as_index=False).agg(
        金额=("amount", "sum"), 品种数=("generic", "nunique"),
        记录数=("amount", "size"), 数量=("qty", "sum"))
    d = d.sort_values("金额", ascending=False).reset_index(drop=True)
    d["占比"] = d["金额"] / tot * 100
    d["累计占比"] = d["占比"].cumsum()
    R["dept_top"] = d.head(30).to_dict(orient="records")
    R["dept_total_share_top30"] = float(d.head(30)["占比"].sum())

    dept_dom = {}
    for dep in d["dept"]:
        sub = df[df["dept"] == dep].groupby("generic")["amount"].sum().sort_values(ascending=False)
        dn = sub.index[0]; da = sub.iloc[0]; depa = sub.sum()
        datc1 = df[df["generic"] == dn]["atc1"].value_counts().index[0]
        dept_dom[dep] = {"主导药品": dn, "主导金额": float(da),
                         "主导占比": float(da / depa * 100), "主导ATC1": datc1, "科室金额": float(depa)}
    R["dept_dom"] = dept_dom

    NON_ONCO_KW = ["康复", "理疗", "中医", "针灸", "皮肤", "眼科", "口腔", "耳鼻喉", "整形", "美容",
                   "妇产", "生殖", "计划生育", "保健", "营养", "心理", "精神", "康复医学", "体检", "健康管理"]
    susp_mismatch = [{"科室": dep, **info} for dep, info in dept_dom.items()
                     if info["主导ATC1"] == "抗肿瘤药及免疫调节剂" and any(k in dep for k in NON_ONCO_KW)]
    R["susp_mismatch"] = sorted(susp_mismatch, key=lambda x: -x["科室金额"])
    susp_conc = [{"科室": dep, **info} for dep, info in dept_dom.items() if info["主导占比"] > 30]
    R["susp_concentration"] = sorted(susp_conc, key=lambda x: -x["主导占比"])

    zero_amt = int((df["amount"] == 0).sum()); zero_price = int((df["price"] == 0).sum())
    # 金额=数量×单价 校验
    mismatch = int(((df["qty"] * df["price"] - df["amount"]).abs() > 0.01).sum())
    R["quality"] = {"zero_amount_rows": zero_amt, "zero_price_rows": zero_price,
                    "atc1_count": int(atc1.shape[0]), "amount_eq_qty_x_price_mismatch": mismatch}

    with open(os.path.join(OUT, "analysis_results.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)

    # ---------- 图表 ----------
    for cand in ["Microsoft YaHei", "SimHei", "SimSun", "PingFang SC", "Source Han Sans CN"]:
        try:
            font_manager.findfont(cand, fallback_to_default=False)
            plt.rcParams["font.sans-serif"] = [cand]; break
        except Exception:
            continue
    plt.rcParams["axes.unicode_minus"] = False
    yiy = lambda x: f"{x/1e8:.1f}"

    t15 = g.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.barh(t15["generic"], t15["金额"], color="#C0392B")
    ax.set_xlabel("金额（亿元）"); ax.set_title("药品使用金额 Top15（按通用名）")
    ax.set_xticklabels([yiy(v) for v in ax.get_xticks()])
    for i, (v, p) in enumerate(zip(t15["金额"], t15["占比"])):
        ax.text(v, i, f" {v/1e8:.2f}亿 ({p:.1f}%)", va="center", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "top15_drug.png"), dpi=150); plt.close(fig)

    a1 = atc1.iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.barh(a1["atc1"], a1["金额"], color="#2C3E50")
    ax.set_xlabel("金额（亿元）"); ax.set_title("ATC 1级分类 药品使用金额分布")
    ax.set_xticklabels([yiy(v) for v in ax.get_xticks()])
    for i, (v, p) in enumerate(zip(a1["金额"], a1["占比"])):
        ax.text(v, i, f" {v/1e8:.2f}亿 ({p:.1f}%)", va="center", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "atc1.png"), dpi=150); plt.close(fig)

    d15 = d.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.barh(d15["dept"], d15["金额"], color="#2471A3")
    ax.set_xlabel("金额（亿元）"); ax.set_title("科室药品使用金额 Top15")
    ax.set_xticklabels([yiy(v) for v in ax.get_xticks()])
    for i, (v, p) in enumerate(zip(d15["金额"], d15["占比"])):
        ax.text(v, i, f" {v/1e8:.2f}亿 ({p:.1f}%)", va="center", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "top15_dept.png"), dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(1, len(g) + 1)
    ax.bar(x, g["金额"] / 1e8, color="#AAB7B8", width=1.0)
    ax2 = ax.twinx(); ax2.plot(x, g["累计占比"], color="#C0392B", linewidth=1.5)
    ax2.axhline(80, color="grey", ls="--", lw=0.8)
    ax.set_xlabel(f"药品品种排序（共{len(g)}种）"); ax.set_ylabel("单品种金额（亿元）")
    ax2.set_ylabel("累计金额占比（%）"); ax.set_title("全院药品金额帕累托分布")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "pareto.png"), dpi=150); plt.close(fig)

    print("=== SUMMARY ===")
    print(f"记录={R['meta']['rows']:,} 科室={R['meta']['depts']} 品种={R['meta']['drugs']}")
    print(f"总金额={tot:,.2f}元 ({tot/1e4:,.2f}万元, {tot/1e8:.2f}亿元)")
    print(f"Top50占比={R['top50_total_share']:.2f}%  ATC1类={R['quality']['atc1_count']}")
    print(f"金额=数量×单价不一致={mismatch}  金额=0:{zero_amt} 单价=0:{zero_price}")
    print(f"专科-药品匹配存疑={len(R['susp_mismatch'])}  单药>30%科室={len(R['susp_concentration'])}")
    print("DONE ->", os.path.join(OUT, "analysis_results.json"))


if __name__ == "__main__":
    main()
