#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
method_metrics.py - 分析方法验证统计辅助（纯 Python，无第三方依赖）

功能：
  1) 线性：输入 (浓度, 响应) 点，输出 相关系数 r、斜率、截距、回算残差，
     并判定 r 是否达到可接受（含量 r>=0.999 / 杂质 r>=0.990）。
  2) 准确度：输入 (理论值, 测得值) 加标回收点，输出平均回收% 与 RSD%，
     并判定回收是否在 98-102%(含量)/80-120%(杂质) 区间。
  3) 精密度：输入重复测定值列表，输出 均值、SD、RSD%，并判定 RSD 是否<=2.0%(含量)。

用法示例（JSON 通过命令行 -j 传入，或从 stdin 读）：
  python method_metrics.py -j '{"linear":[[0.4,120],[0.8,245],[1.0,310],[1.2,372],[1.6,498]],
                              "accuracy":[[100,99.2],[100,101.1],[100,98.8]],
                              "precision":[99.5,100.3,99.8,100.1,99.6,100.0]}'

也可只传其中一项。
"""
import sys, json, math


def _linreg(xs, ys):
    n = len(xs)
    sx = sum(xs); sy = sum(ys)
    sxx = sum(x * x for x in xs); sxy = sum(x * y for x, y in zip(xs, ys))
    syy = sum(y * y for y in ys)
    denom = (n * sxx - sx * sx)
    if denom == 0:
        return None
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    # 相关系数
    num = (n * sxy - sx * sy)
    den = math.sqrt((n * sxx - sx * sx) * (n * syy - sy * sy))
    r = (num / den) if den != 0 else 0.0
    return slope, intercept, r


def lin_report(pts, mode="assay"):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    res = _linreg(xs, ys)
    if not res:
        return {"error": "线性数据无效（分母为0）"}
    slope, intercept, r = res
    resid = []
    for x, y in pts:
        pred = slope * x + intercept
        resid.append((y - pred) / pred * 100 if pred != 0 else 0)
    r_min = 0.999 if mode == "assay" else 0.990
    return {
        "n": len(pts),
        "slope": round(slope, 6),
        "intercept": round(intercept, 6),
        "r": round(r, 5),
        "r_accept": "PASS" if r >= r_min else "FAIL",
        "r_min_req": r_min,
        "max_residual_%": round(max(abs(v) for v in resid), 3),
    }


def acc_report(pts):
    recs = []
    for theo, meas in pts:
        recs.append(meas / theo * 100 if theo != 0 else 0)
    mean = sum(recs) / len(recs)
    sd = math.sqrt(sum((v - mean) ** 2 for v in recs) / (len(recs) - 1)) if len(recs) > 1 else 0
    rsd = sd / mean * 100 if mean != 0 else 0
    ok = all(80 <= v <= 120 for v in recs) and 80 <= mean <= 120
    return {
        "n": len(recs),
        "mean_recovery_%": round(mean, 2),
        "sd": round(sd, 3),
        "rsd_%": round(rsd, 3),
        "accept": "PASS" if ok else "FAIL",
    }


def prec_report(vals):
    n = len(vals)
    mean = sum(vals) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1)) if n > 1 else 0
    rsd = sd / mean * 100 if mean != 0 else 0
    return {
        "n": n,
        "mean": round(mean, 4),
        "sd": round(sd, 4),
        "rsd_%": round(rsd, 3),
        "accept_2pct": "PASS" if rsd <= 2.0 else "FAIL",
    }


def main():
    raw = None
    if "-j" in sys.argv:
        idx = sys.argv.index("-j") + 1
        raw = sys.argv[idx]
    else:
        data = sys.stdin.read().strip()
        if data:
            raw = data
    if not raw:
        print(__doc__)
        return
    try:
        d = json.loads(raw)
    except Exception as e:
        print("JSON 解析失败:", e)
        return
    out = {}
    if "linear" in d:
        out["linear"] = lin_report(d["linear"], d.get("linear_mode", "assay"))
    if "accuracy" in d:
        out["accuracy"] = acc_report(d["accuracy"])
    if "precision" in d:
        out["precision"] = prec_report(d["precision"])
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
