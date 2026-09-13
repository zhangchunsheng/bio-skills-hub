#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用医药数据分析器 (pharma skill 共享脚本)
读取 CSV/Excel 数据，按 config 执行分析，输出可直接由 render.py 渲染的 spec JSON。

用法:
    python analyze.py <input.csv> <config.json> [--output <result.json>]

config.json 结构:
{
  "title": "销售报表解读",
  "subtitle": "...",
  "type": "trend" | "ranking" | "warning" | "ratio" | "comparison" | "summary",
  "dimension": "月份",        # 分组/时间维度列名
  "measure": "销售额",         # 数值度量列名
  "measure2": "成本",          # 可选(用于比率/对比)
  "threshold": 100,            # warning 用
  "top_n": 5,
  "ratio_mode": "share" | "margin"
}
"""

import sys
import csv
import json
import argparse
from pathlib import Path
from collections import OrderedDict


def clean_num(v):
    if v is None:
        return 0.0
    s = str(v).strip().replace(",", "").replace("，", "")
    s = s.replace("元", "").replace("%", "").replace("万", "").replace("￥", "").replace("$", "")
    s = s.replace("（", "").replace("）", "")
    if s in ("", "-", "—", "NA", "N/A", "null", "None"):
        return 0.0
    try:
        return float(s)
    except Exception:
        return 0.0


def load_rows(path):
    p = Path(path)
    if p.suffix.lower() in (".xlsx", ".xls"):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
            ws = wb.active
            rows = list(ws.values)
            wb.close()
            if not rows:
                return [], []
            headers = [str(h) for h in rows[0]]
            data = [dict(zip(headers, r)) for r in rows[1:]]
            return headers, data
        except Exception as e:
            raise RuntimeError(f"Excel 读取失败(需 openpyxl): {e}")
    # CSV
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        data = [dict(r) for r in reader]
    return headers, data


def group_sum(rows, dim, meas):
    agg = OrderedDict()
    for r in rows:
        k = str(r.get(dim, "")).strip()
        if k == "":
            continue
        agg.setdefault(k, 0.0)
        agg[k] += clean_num(r.get(meas, 0))
    return agg


def fmt(x):
    if abs(x) >= 10000:
        return f"{x:,.0f}"
    return f"{x:,.1f}"


def analyze(cfg, headers, rows):
    atype = cfg.get("type", "summary")
    dim = cfg.get("dimension")
    meas = cfg.get("measure")
    title = cfg.get("title", "数据分析报告")

    if atype == "trend":
        agg = group_sum(rows, dim, meas)
        items = list(agg.items())
        table_rows = [[k, fmt(v)] for k, v in items]
        total = sum(agg.values())
        bullets = []
        if items:
            mx = max(agg.items(), key=lambda kv: kv[1])
            mn = min(agg.items(), key=lambda kv: kv[1])
            bullets.append(f"峰值出现在「{mx[0]}」，数值 {fmt(mx[1])}；谷值在「{mn[0]}」，数值 {fmt(mn[1])}。")
            if len(items) >= 2:
                first, last = items[0][1], items[-1][1]
                chg = ((last - first) / first * 100) if first else 0
                direction = "上升" if chg >= 0 else "下降"
                bullets.append(f"首期 {fmt(first)} → 末期 {fmt(last)}，整体{direction} {abs(chg):.1f}%。")
        bullets.append(f"区间内「{meas}」合计 {fmt(total)}。")
        return {
            "title": title, "subtitle": cfg.get("subtitle", ""),
            "meta": [["样本量", len(rows)], ["分析类型", "趋势分析"], ["维度", dim], ["度量", meas]],
            "sections": [
                {"heading": f"{dim} 维度「{meas}」趋势", "table": {"headers": [dim, meas], "rows": table_rows},
                 "bullets": bullets, "note": "数据来源于上传文件，已按维度聚合。"}
            ],
            "footer": "本报告由 pharma 数据分析脚本生成。"
        }

    if atype == "ranking":
        agg = group_sum(rows, dim, meas)
        ranked = sorted(agg.items(), key=lambda kv: kv[1], reverse=True)
        top_n = int(cfg.get("top_n", 5))
        top = ranked[:top_n]
        bottom = ranked[-top_n:][::-1]
        total = sum(agg.values()) or 1
        table_rows = [[k, fmt(v), f"{v/total*100:.1f}%"] for k, v in top]
        bullets = [f"Top{top_n} 合计占总体 {sum(v for _,v in top)/total*100:.1f}%。"]
        if bottom:
            bullets.append("尾部(贡献最低)：" + "、".join(f"{k}({fmt(v)})" for k, v in bottom))
        return {
            "title": title, "subtitle": cfg.get("subtitle", ""),
            "meta": [["样本量", len(rows)], ["分析类型", "分组排名"], ["维度", dim], ["度量", meas]],
            "sections": [
                {"heading": f"「{dim}」按「{meas}」排名(Top{top_n})",
                 "table": {"headers": [dim, meas, "占比"], "rows": table_rows},
                 "bullets": bullets}
            ],
            "footer": "本报告由 pharma 数据分析脚本生成。"
        }

    if atype == "warning":
        thr = float(cfg.get("threshold", 0))
        meas2 = cfg.get("measure2")
        flag_dim = dim or "项目"
        flagged = []
        for r in rows:
            val = clean_num(r.get(meas, 0))
            if val < thr:
                extra = f"（{meas2}：{r.get(meas2,'')}）" if meas2 else ""
                flagged.append([str(r.get(flag_dim, "")), fmt(val), extra])
        bullets = [f"共识别出 {len(flagged)} 条低于阈值 {fmt(thr)} 的记录，建议重点关注。"]
        if flagged:
            bullets.append("高风险项：" + "、".join(f"{r[0]}" for r in flagged[:5]))
        return {
            "title": title, "subtitle": cfg.get("subtitle", ""),
            "meta": [["样本量", len(rows)], ["分析类型", "风险预警"], ["阈值", fmt(thr)], ["命中", len(flagged)]],
            "sections": [
                {"heading": "预警清单", "note": "以下记录触发预警条件，请结合业务判断。",
                 "table": {"headers": [flag_dim, meas, "备注"], "rows": flagged} if flagged
                          else {"headers": ["提示"], "rows": [["无预警记录"]]},
                 "bullets": bullets}
            ],
            "footer": "本报告由 pharma 数据分析脚本生成。"
        }

    if atype == "ratio":
        mode = cfg.get("ratio_mode", "share")
        if mode == "margin" and meas and cfg.get("measure2"):
            agg_a = group_sum(rows, dim, meas)
            agg_b = group_sum(rows, dim, cfg["measure2"])
            table_rows = []
            for k in agg_a:
                a = agg_a[k]
                b = agg_b.get(k, 0.0)
                margin = (a - b) / a * 100 if a else 0
                table_rows.append([k, fmt(a), fmt(b), f"{margin:.1f}%"])
            return {
                "title": title, "subtitle": cfg.get("subtitle", ""),
                "meta": [["样本量", len(rows)], ["分析类型", "比率分析(差额率)"], ["维度", dim]],
                "sections": [{"heading": f"「{dim}」差额率（({meas}-{cfg['measure2']})/{meas}）",
                              "table": {"headers": [dim, meas, cfg["measure2"], "差额率"], "rows": table_rows}}],
                "footer": "本报告由 pharma 数据分析脚本生成。"
            }
        else:  # share
            agg = group_sum(rows, dim, meas)
            total = sum(agg.values()) or 1
            table_rows = [[k, fmt(v), f"{v/total*100:.1f}%"] for k, v in agg.items()]
            return {
                "title": title, "subtitle": cfg.get("subtitle", ""),
                "meta": [["样本量", len(rows)], ["分析类型", "占比分析"], ["维度", dim], ["度量", meas]],
                "sections": [{"heading": f"「{dim}」在「{meas}」中的占比",
                              "table": {"headers": [dim, meas, "占比"], "rows": table_rows}}],
                "footer": "本报告由 pharma 数据分析脚本生成。"
            }

    if atype == "comparison":
        agg_a = group_sum(rows, dim, meas)
        agg_b = group_sum(rows, dim, cfg["measure2"]) if cfg.get("measure2") else None
        table_rows = []
        for k in agg_a:
            row = [k, fmt(agg_a[k])]
            if agg_b is not None:
                row.append(fmt(agg_b.get(k, 0.0)))
            table_rows.append(row)
        headers_tbl = [dim, meas] + ([cfg["measure2"]] if agg_b is not None else [])
        bullets = []
        if agg_a:
            mx = max(agg_a.items(), key=lambda kv: kv[1])
            bullets.append(f"「{meas}」最高为 {mx[0]}（{fmt(mx[1])}）。")
        return {
            "title": title, "subtitle": cfg.get("subtitle", ""),
            "meta": [["样本量", len(rows)], ["分析类型", "对比分析"], ["维度", dim]],
            "sections": [{"heading": f"「{dim}」对比（{meas}）",
                          "table": {"headers": headers_tbl, "rows": table_rows}, "bullets": bullets}],
            "footer": "本报告由 pharma 数据分析脚本生成。"
        }

    # summary (default)
    numeric_cols = [h for h in headers if any(clean_num(r.get(h)) != 0.0 for r in rows[:min(20, len(rows))])]
    totals = {h: sum(clean_num(r.get(h)) for r in rows) for h in numeric_cols[:6]}
    table_rows = [[h, fmt(v)] for h, v in totals.items()]
    dist_col = dim
    dist = OrderedDict()
    if dist_col:
        for r in rows:
            k = str(r.get(dist_col, "")).strip()
            if k:
                dist[k] = dist.get(k, 0) + 1
    dist_rows = [[k, str(v)] for k, v in list(dist.items())[:10]]
    sections = [{"heading": "关键指标汇总", "table": {"headers": ["指标", "合计"], "rows": table_rows}}]
    if dist_rows:
        sections.append({"heading": f"按「{dist_col}」分布", "table": {"headers": [dist_col, "数量"], "rows": dist_rows}})
    return {
        "title": title, "subtitle": cfg.get("subtitle", ""),
        "meta": [["样本量", len(rows)], ["分析类型", "汇总分析"], ["维度", dim or "-"]],
        "sections": sections,
        "footer": "本报告由 pharma 数据分析脚本生成。"
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="输入 CSV/Excel")
    ap.add_argument("config", help="分析配置 JSON")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    headers, rows = load_rows(args.input)
    result = analyze(cfg, headers, rows)
    out = args.output or "analysis_result.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK analysis({cfg.get('type')}) -> {out} ({len(rows)} rows, {len(result['sections'])} sections)")


if __name__ == "__main__":
    main()
