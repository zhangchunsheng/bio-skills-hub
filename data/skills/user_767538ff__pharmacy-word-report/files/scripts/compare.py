# -*- coding: utf-8 -*-
"""两月药品使用环比对比：202606 vs 202607。
读取两个月的 analysis_results.json，输出 comparison_results.json。
字段说明：
  m606 / m607  两个月的 meta、top50、atc1、susp_mismatch
  totals        总体环比（总额、科室数、品种数、记录数、Top50占比）
  top_drug_mom  Top药品（取两月并集的前N名）金额与排名环比
  atc1_mom      ATC1级分类金额与占比环比
  susp_mom      存疑科室两月对照（出现月份、主导药、主导占比）
"""
import json, os, sys

A = sys.argv[1] if len(sys.argv) > 1 else "out_202606/analysis_results.json"
B = sys.argv[2] if len(sys.argv) > 2 else "out_202607/analysis_results.json"
OUT = sys.argv[3] if len(sys.argv) > 3 else "out_compare"
os.makedirs(OUT, exist_ok=True)

R6 = json.load(open(A, encoding="utf-8"))
R7 = json.load(open(B, encoding="utf-8"))


def pct(new, old):
    if old in (0, 0.0, None) or old is None:
        return None
    return (new - old) / old * 100


# ---- 总体环比 ----
m6, m7 = R6["meta"], R7["meta"]
totals = {
    "m606": {"rows": m6["rows"], "depts": m6["depts"], "drugs": m6["drugs"],
             "total_amount": m6["total_amount"], "total_amount_wan": m6["total_amount"] / 1e4,
             "top50_share": R6["top50_total_share"]},
    "m607": {"rows": m7["rows"], "depts": m7["depts"], "drugs": m7["drugs"],
             "total_amount": m7["total_amount"], "total_amount_wan": m7["total_amount"] / 1e4,
             "top50_share": R7["top50_total_share"]},
    "delta": {
        "amount_wan": m7["total_amount"] / 1e4 - m6["total_amount"] / 1e4,
        "amount_pct": pct(m7["total_amount"], m6["total_amount"]),
        "depts": m7["depts"] - m6["depts"],
        "drugs": m7["drugs"] - m6["drugs"],
        "rows": m7["rows"] - m6["rows"],
        "top50_share_delta": R7["top50_total_share"] - R6["top50_total_share"],
    },
}

# ---- Top药品环比 ----
idx6 = {r["generic"]: r for r in R6["top50"]}
idx7 = {r["generic"]: r for r in R7["top50"]}
all_gen = list(idx6.keys()) + [g for g in idx7 if g not in idx6]
# 取两月并集金额降序前 40 做对比（覆盖核心品种）
union = []
for g in all_gen:
    a6 = idx6.get(g, {}).get("金额", 0.0)
    a7 = idx7.get(g, {}).get("金额", 0.0)
    union.append((g, a6, a7))
union.sort(key=lambda x: (x[1] + x[2]), reverse=True)
rank6 = {g: i + 1 for i, g in enumerate(idx6)}
rank7 = {g: i + 1 for i, g in enumerate(idx7)}
top_drug_mom = []
for g, a6, a7 in union[:40]:
    top_drug_mom.append({
        "generic": g,
        "amt_606": a6, "amt_607": a7,
        "delta_wan": (a7 - a6) / 1e4,
        "pct": pct(a7, a6),
        "rank_606": rank6.get(g),
        "rank_607": rank7.get(g),
        "in_top50_606": g in idx6,
        "in_top50_607": g in idx7,
    })
# 仅两月均在Top50的品种（稳定性）
both_top50 = [g for g in idx6 if g in idx7]

# ---- ATC1环比 ----
a1_6 = {a["atc1"]: a for a in R6["atc1"]}
a1_7 = {a["atc1"]: a for a in R7["atc1"]}
atc1_names = list(a1_7.keys()) + [k for k in a1_6 if k not in a1_7]
atc1_mom = []
for k in atc1_names:
    v6 = a1_6.get(k, {})
    v7 = a1_7.get(k, {})
    atc1_mom.append({
        "atc1": k,
        "amt_606_wan": v6.get("金额", 0) / 1e4,
        "amt_607_wan": v7.get("金额", 0) / 1e4,
        "share_606": v6.get("占比", 0.0),
        "share_607": v7.get("占比", 0.0),
        "delta_wan": (v7.get("金额", 0) - v6.get("金额", 0)) / 1e4,
        "share_delta": v7.get("占比", 0.0) - v6.get("占比", 0.0),
    })
atc1_mom.sort(key=lambda x: x["amt_607_wan"], reverse=True)

# ---- 存疑科室两月对照 ----
s6 = {r["科室"]: r for r in R6["susp_mismatch"]}
s7 = {r["科室"]: r for r in R7["susp_mismatch"]}
susp_depts = sorted(set(s6) | set(s7))
susp_mom = []
for d in susp_depts:
    r6 = s6.get(d)
    r7 = s7.get(d)
    susp_mom.append({
        "科室": d,
        "in_606": d in s6, "in_607": d in s7,
        "主导药品_606": r6["主导药品"] if r6 else "",
        "主导占比_606": r6["主导占比"] if r6 else None,
        "主导药品_607": r7["主导药品"] if r7 else "",
        "主导占比_607": r7["主导占比"] if r7 else None,
        "科室金额_606_wan": (r6["科室金额"] / 1e4) if r6 else None,
        "科室金额_607_wan": (r7["科室金额"] / 1e4) if r7 else None,
    })

# ---- 单药高度集中科室数环比 ----
conc = {
    "n_606": len(R6["susp_concentration"]),
    "n_607": len(R7["susp_concentration"]),
}

R = {
    "totals": totals,
    "top_drug_mom": top_drug_mom,
    "both_top50_count": len(both_top50),
    "atc1_mom": atc1_mom,
    "susp_mom": susp_mom,
    "conc": conc,
}

with open(os.path.join(OUT, "comparison_results.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)

print("DONE ->", os.path.join(OUT, "comparison_results.json"))
print(f"总额环比: {totals['delta']['amount_pct']:+.2f}%  ({totals['delta']['amount_wan']:+,.0f}万元)")
print(f"科室数: {m6['depts']}->{m7['depts']} ({totals['delta']['depts']:+d})  品种数: {m6['drugs']}->{m7['drugs']} ({totals['delta']['drugs']:+d})")
print(f"两月同在Top50品种: {len(both_top50)}")
print(f"存疑科室: 606={len(s6)} 607={len(s7)} 并集={len(susp_depts)}")
print(f"单药>30%科室: 606={conc['n_606']} 607={conc['n_607']}")
