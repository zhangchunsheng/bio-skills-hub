# -*- coding: utf-8 -*-
"""存疑科室单科室明细深挖：读取两个月原始出库 Excel，对"专科-主导药品匹配存疑"科室
输出逐月药品明细（Top药品、主导药占比、ATC1分类），供药师逐科核实。
输出 dept_dive.json。
"""
import json, os, sys
import pandas as pd

F606 = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/LM/Desktop/202606.xlsx"
F607 = sys.argv[2] if len(sys.argv) > 2 else "C:/Users/LM/Desktop/202607.xlsx"
J606 = sys.argv[3] if len(sys.argv) > 3 else "out_202606/analysis_results.json"
J607 = sys.argv[4] if len(sys.argv) > 4 else "out_202607/analysis_results.json"
OUT = sys.argv[5] if len(sys.argv) > 5 else "out_compare"
os.makedirs(OUT, exist_ok=True)

COLMAP = {
    "dept": "科室", "unit": "入库单位", "qty": "数量", "price": "单价",
    "amount": "金额", "insurance": "医保编码", "generic": "通用名",
    "atc1": "最终ATC分类1级", "atc2": "最终ATC分类2级",
    "atc3": "最终ATC分类3级", "atc4": "最终ATC分类4级",
}
NUMERIC = ["qty", "price", "amount"]


def load(fp):
    raw = pd.read_excel(fp, dtype=str)
    df = pd.DataFrame()
    for k, col in COLMAP.items():
        df[k] = raw[col]
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


df6, df7 = load(F606), load(F607)

R6 = json.load(open(J606, encoding="utf-8"))
R7 = json.load(open(J607, encoding="utf-8"))
depts = sorted(set(r["科室"] for r in R6["susp_mismatch"]) | set(r["科室"] for r in R7["susp_mismatch"]))

# 专科非肿瘤科室关键词（用于判定主导药是否明显不匹配）
NON_ONCO_KW = ["康复", "理疗", "中医", "皮肤", "眼科", "口腔", "耳鼻喉", "生殖", "妇产",
               "保健", "营养", "心理", "精神", "针灸", "风湿"]


def dept_detail(df, dept, period):
    sub = df[df["dept"] == dept]
    if sub.empty:
        return None
    total = sub["amount"].sum()
    top = sub.groupby("generic").agg(金额=("amount", "sum"), 数量=("qty", "sum")).sort_values("金额", ascending=False)
    top["占比"] = top["金额"] / total * 100
    # 主导药ATC1
    g0 = top.index[0]
    a0 = sub[sub["generic"] == g0]["atc1"].dropna()
    atc0 = a0.value_counts().index[0] if len(a0) else None
    top_rows = []
    for g, row in top.head(8).iterrows():
        gatc = sub[sub["generic"] == g]["atc1"].dropna()
        atc = gatc.value_counts().index[0] if len(gatc) else None
        top_rows.append({"generic": g, "金额": float(row["金额"]), "金额_万元": float(row["金额"]) / 1e4,
                         "数量": float(row["数量"]), "占比": float(row["占比"]), "atc1": atc})
    mismatch = (atc0 == "抗肿瘤药及免疫调节剂") and any(k in dept for k in NON_ONCO_KW)
    return {
        "period": period, "科室": dept, "科室金额": float(total), "科室金额_万元": float(total) / 1e4,
        "品种数": int(sub["generic"].nunique()), "记录数": int(len(sub)),
        "主导药品": g0, "主导占比": float(top.iloc[0]["占比"]), "主导ATC1": atc0,
        "匹配存疑": bool(mismatch), "top": top_rows,
    }


result = []
for d in depts:
    det6 = dept_detail(df6, d, "202606")
    det7 = dept_detail(df7, d, "202607")
    # 出现月数
    months = [x["period"] for x in (det6, det7) if x]
    result.append({"科室": d, "出现月份": months, "明细": [x for x in (det6, det7) if x]})

with open(os.path.join(OUT, "dept_dive.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("DONE ->", os.path.join(OUT, "dept_dive.json"))
print(f"深挖存疑科室数: {len(result)}")
for r in result:
    for m in r["明细"]:
        print(f"  {m['科室']:<16} {m['period']} 主导={m['主导药品']:<12} 占={m['主导占比']:.1f}% 存疑={m['匹配存疑']} 万元={m['科室金额_万元']:,.0f}")
