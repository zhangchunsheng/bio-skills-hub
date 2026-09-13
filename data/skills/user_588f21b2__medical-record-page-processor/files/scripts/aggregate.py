# -*- coding: utf-8 -*-
"""汇总聚合：把派生后的明细表压成图表数据结构。

每个图表对象自带 facts（事实卡）—— 这些数字是写报告解读时唯一可引用的来源，
全部由本模块从数据实算得出，不允许手写编造。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MAX_CATS = 15


def build_charts(d: pd.DataFrame, cfg: dict | None = None) -> list[dict]:
    charts: list[dict] = []
    add = charts.append

    # 1. 年度趋势：出院人次 + 平均住院日
    if "年份" in d.columns and d["年份"].notna().any():
        g = d.groupby("年份", dropna=True)
        cnt = g.size()
        cats = [str(int(x)) for x in cnt.index]
        series = [{"name": "出院人次", "data": [int(v) for v in cnt.values], "unit": "人次"}]
        los = g["住院天数"].mean() if "住院天数" in d.columns else None
        if los is not None and los.notna().any():
            series.append({"name": "平均住院日", "data": [_r(v) for v in los.values], "unit": "天"})
        top = cnt.idxmax()
        partial = _partial_last_year(cnt)
        full = cnt.iloc[:-1] if partial else cnt
        facts = [
            f"共 {len(cats)} 个年度，出院人次合计 {int(cnt.sum())} 人次",
            f"峰值年份 {int(top)} 年：{int(cnt.loc[top])} 人次，占全部 {cnt.loc[top] / cnt.sum() * 100:.1f}%",
            f"{'完整年度' if partial else ''}首年 {int(full.index[0])} 年 {int(full.iloc[0])} 人次 → "
            f"末年 {int(full.index[-1])} 年 {int(full.iloc[-1])} 人次"
            + (f"（增幅 {(full.iloc[-1] / full.iloc[0] - 1) * 100:+.1f}%）" if full.iloc[0] else ""),
        ]
        if partial:
            facts.append(f"⚠ {int(cnt.index[-1])} 年仅 {int(cnt.iloc[-1])} 人次，明显低于其他年度，"
                         "极可能是数据导出截止造成的不完整年度；上面的增幅对比已剔除该年")
        add({
            "id": "trend_year", "type": "line", "title": _title_year(cnt),
            "subtitle": f"按出院日期归年（{cats[0]}–{cats[-1]}），共 {int(cnt.sum())} 条记录"
                        + ("；末年数据不完整，趋势解读请以完整年度为准" if partial else ""),
            "categories": cats, "series": series, "x_name": "年份", "y_name": "数值",
            "facts": facts,
        })

    # 2. 月度趋势（按 年月）
    if "年月" in d.columns and d["年月"].notna().any():
        cnt = d.groupby("年月", dropna=True).size().sort_index()
        if len(cnt) >= 3:
            add({
                "id": "trend_month", "type": "line",
                "title": f"月度出院人次波动（最高 {int(cnt.max())} 人次）",
                "subtitle": f"按出院日期归月，覆盖 {len(cnt)} 个月",
                "categories": [str(x) for x in cnt.index],
                "series": [{"name": "出院人次", "data": [int(v) for v in cnt.values], "unit": "人次"}],
                "x_name": "年月", "y_name": "出院人次",
                "facts": [
                    f"月度出院人次中位 {cnt.median():.0f} 人次，最高 {int(cnt.max())}（{cnt.idxmax()}），"
                    f"最低 {int(cnt.min())}（{cnt.idxmin()}）",
                    f"极差 {int(cnt.max() - cnt.min())} 人次，峰谷比 {cnt.max() / max(1, cnt.min()):.2f}",
                ],
            })

    # 3. 科室对比（人次 + 平均住院日）
    dept = _pick(d, ["出院科别", "入院科别"])
    if dept is not None:
        vc = d[dept].astype(str).str.strip().replace({"nan": None}).dropna().value_counts()
        vc = vc[vc.index.isin(["", "None"]) == False]
        if len(vc):
            top = vc.head(MAX_CATS)
            other = int(vc.iloc[MAX_CATS:].sum())
            cats = list(top.index) + (["其他"] if other else [])
            data = [int(v) for v in top.values] + ([other] if other else [])
            add({
                "id": "dept_volume", "type": "bar",
                "title": f"出院人次最多科室：{cats[0]}（{data[0]} 人次）",
                "subtitle": f"按{dept}统计，覆盖 {int(vc.shape[0])} 个科室，展示前 {MAX_CATS}"
                            + ("，其余合并为「其他」" if other else ""),
                "categories": cats, "series": [{"name": "出院人次", "data": data, "unit": "人次"}],
                "x_name": dept, "y_name": "出院人次",
                "facts": [
                    f"共 {int(vc.shape[0])} 个科室，出院人次前 3 位："
                    + "、".join(f"{k} {int(v)} 人次" for k, v in vc.head(3).items()),
                    f"首位科室占比 {vc.iloc[0] / vc.sum() * 100:.1f}%，"
                    f"前 5 位累计 {vc.head(5).sum() / vc.sum() * 100:.1f}%",
                ],
            })
            if "住院天数" in d.columns:
                m = (d[d[dept].astype(str).isin(top.index)]
                     .groupby(d[dept].astype(str))["住院天数"].mean().reindex(top.index).dropna())
                if len(m):
                    m = m.sort_values(ascending=False)
                    add({
                        "id": "dept_los", "type": "bar",
                        "title": f"平均住院日最长科室：{m.index[0]}（{m.iloc[0]:.1f} 天）",
                        "subtitle": f"仅统计出院人次前 {MAX_CATS} 的科室，核对样本量后再解读",
                        "categories": [str(x) for x in m.index],
                        "series": [{"name": "平均住院日", "data": [_r(v) for v in m.values],
                                    "unit": "天"}],
                        "x_name": dept, "y_name": "平均住院日（天）",
                        "facts": [
                            f"平均住院日最高 {m.index[0]} {m.iloc[0]:.1f} 天，"
                            f"最低 {m.index[-1]} {m.iloc[-1]:.1f} 天，极差 {m.iloc[0] - m.iloc[-1]:.1f} 天",
                            f"全部样本平均 {d['住院天数'].mean():.1f} 天",
                        ],
                    })

    # 4. 年龄段构成
    if "年龄段" in d.columns and d["年龄段"].notna().any():
        vc = d["年龄段"].value_counts()
        add({
            "id": "age_pie", "type": "pie",
            "title": f"{vc.index[0]}患者占比最高（{vc.iloc[0] / vc.sum() * 100:.1f}%）",
            "subtitle": "按年龄段统计出院人次，年龄段由年龄字段（缺失按出生日期推算）分段",
            "data": [{"name": str(k), "value": int(v)} for k, v in vc.items()],
            "facts": [f"{k}：{int(v)} 人次（{v / vc.sum() * 100:.1f}%）" for k, v in vc.items()],
        })

    # 5. 性别构成
    sex = _pick(d, ["性别"])
    if sex is not None:
        vc = d[sex].astype(str).str.strip().value_counts()
        if len(vc):
            add({
                "id": "sex_pie", "type": "pie",
                "title": f"{vc.index[0]}性占 {vc.iloc[0] / vc.sum() * 100:.1f}%",
                "subtitle": "按性别统计出院人次（已把 1/2、M/F 归一到男/女）",
                "data": [{"name": str(k), "value": int(v)} for k, v in vc.items()],
                "facts": [f"{k}：{int(v)} 人次（{v / vc.sum() * 100:.1f}%）" for k, v in vc.items()],
            })

    # 6. 主要诊断 TOP10
    diag = _pick(d, ["主要诊断名称", "主要诊断编码"])
    if diag is not None:
        vc = (d[diag].astype(str).str.strip()
              .replace({"nan": None, "": None}).dropna().value_counts())
        if len(vc):
            top = vc.head(10)
            add({
                "id": "diag_top", "type": "bar",
                "title": f"首位出院诊断：{str(top.index[0])[:20]}（{int(top.iloc[0])} 例）",
                "subtitle": f"按{diag}统计，共 {int(vc.shape[0])} 个不同取值，展示前 10",
                "categories": [str(x) for x in top.index],
                "series": [{"name": "例数", "data": [int(v) for v in top.values], "unit": "例"}],
                "x_name": diag, "y_name": "例数",
                "facts": [
                    f"首位 {top.index[0]}：{int(top.iloc[0])} 例（{top.iloc[0] / vc.sum() * 100:.1f}%）",
                    f"前 5 位累计 {vc.head(5).sum() / vc.sum() * 100:.1f}%，"
                    f"前 10 位累计 {top.sum() / vc.sum() * 100:.1f}%",
                    f"首位与第 10 位相差 {int(top.iloc[0] - top.iloc[-1])} 例",
                ],
            })

    # 7. 费用构成
    fee_cols = _fee_columns(d)
    if len(fee_cols) >= 3:
        sums = {c: float(d[c].fillna(0).sum()) for c in fee_cols}
        total = sums.get("总费用", sum(v for k, v in sums.items() if k != "总费用"))
        items = sorted(((k, v) for k, v in sums.items() if k != "总费用" and v > 0),
                       key=lambda x: -x[1])
        if items and total > 0:
            keep = items[:9]
            rest = sum(v for _, v in items[9:])
            data = [{"name": k, "value": _r(v)} for k, v in keep]
            if rest > 0:
                data.append({"name": "其他分项", "value": _r(rest)})
            add({
                "id": "fee_pie", "type": "pie",
                "title": f"费用占比最高项：{keep[0][0]}（{keep[0][1] / total * 100:.1f}%）",
                "subtitle": f"按费用分项汇总，总计 {total:,.0f} 元；分母为分项合计",
                "data": data,
                "facts": [f"{k}：{v:,.0f} 元（{v / total * 100:.1f}%）" for k, v in keep[:5]]
                         + [f"分项合计 {total:,.0f} 元"],
            })

    # 8. 离院方式构成
    way = _pick(d, ["离院方式"])
    if way is not None:
        vc = d[way].astype(str).str.strip().value_counts()
        if len(vc):
            add({
                "id": "outcome_pie", "type": "pie",
                "title": f"{vc.index[0]}占 {vc.iloc[0] / vc.sum() * 100:.1f}%",
                "subtitle": "按离院方式统计出院人次（国标值域：医嘱离院/转院/转社区/非医嘱离院/死亡/其他）",
                "data": [{"name": str(k), "value": int(v)} for k, v in vc.items()],
                "facts": [f"{k}：{int(v)} 人次（{v / vc.sum() * 100:.2f}%）" for k, v in vc.items()],
            })

    # 9. 费用与结构年度趋势
    if "年份" in d.columns and d["年份"].notna().any() and "总费用" in d.columns:
        g = d.groupby("年份", dropna=True)
        cnt_all = g.size()
        partial = _partial_last_year(cnt_all)
        cats = [str(int(x)) for x in g.size().index]
        series = []
        fee_mean = g["总费用"].mean()
        if fee_mean.notna().any():
            series.append({"name": "次均费用", "data": [_r(v) for v in fee_mean.values], "unit": "元"})
        if "药占比" in d.columns and g["药占比"].mean().notna().any():
            series.append({"name": "药占比", "data": [_r(v) for v in g["药占比"].mean().values],
                           "unit": "%"})
        if series:
            fee_full = fee_mean.iloc[:-1] if partial else fee_mean
            facts = []
            if fee_mean.notna().any() and len(fee_full) >= 2:
                facts.append(f"次均费用 {int(fee_full.index[0])} 年 {fee_full.iloc[0]:,.0f} 元 → "
                             f"{int(fee_full.index[-1])} 年 {fee_full.iloc[-1]:,.0f} 元"
                             + (f"（{(fee_full.iloc[-1] / fee_full.iloc[0] - 1) * 100:+.1f}%）"
                                if fee_full.iloc[0] else ""))
            if "药占比" in d.columns and g["药占比"].mean().notna().any():
                y = g["药占比"].mean()
                y = y.iloc[:-1] if partial else y
                if len(y) >= 2:
                    facts.append(f"药占比（按例均值）{y.iloc[0]:.1f}% → {y.iloc[-1]:.1f}%")
            add({
                "id": "trend_fee", "type": "line",
                "title": f"次均费用年度变化（{cats[0]}–{cats[-1]}）",
                "subtitle": "次均费用=∑总费用÷出院人次；药占比=（西药费+中药费）÷总费用，按例均值"
                            + ("；末年数据不完整，趋势解读请以完整年度为准" if partial else ""),
                "categories": cats, "series": series, "x_name": "年份", "y_name": "数值",
                "facts": facts,
            })

    # 10. 手术情况
    if "有无手术" in d.columns and (d["有无手术"] == "有手术").any():
        vc = d["有无手术"].value_counts()
        add({
            "id": "op_pie", "type": "pie",
            "title": f"手术患者占 {vc.get('有手术', 0) / vc.sum() * 100:.1f}%",
            "subtitle": "有手术 = 手术编码/名称/日期任一非空或手术治疗费>0",
            "data": [{"name": str(k), "value": int(v)} for k, v in vc.items()],
            "facts": [f"{k}：{int(v)} 例（{v / vc.sum() * 100:.1f}%）" for k, v in vc.items()],
        })
        lv = d.get("手术级别_标准化")
        if lv is not None:
            vc2 = lv.astype(str).replace({"nan": None}).dropna().value_counts()
            if len(vc2) > 1:
                add({
                    "id": "op_level", "type": "bar",
                    "title": f"手术以{vc2.index[0]}为主（{vc2.iloc[0]} 例）",
                    "subtitle": "按手术级别统计（未填级别的记录不计入）",
                    "categories": [str(x) for x in vc2.index],
                    "series": [{"name": "例数", "data": [int(v) for v in vc2.values], "unit": "例"}],
                    "x_name": "手术级别", "y_name": "例数",
                    "facts": [f"{k}：{int(v)} 例（{v / vc2.sum() * 100:.1f}%）" for k, v in vc2.items()],
                })

    # 11. 付费方式构成
    pay = _pick(d, ["医疗付费方式"])
    if pay is not None:
        vc = d[pay].astype(str).str.strip().replace({"nan": None}).dropna().value_counts()
        if len(vc) and vc.sum() > 0 and len(vc) <= 12:
            add({
                "id": "pay_pie", "type": "pie",
                "title": f"{vc.index[0]}结算占 {vc.iloc[0] / vc.sum() * 100:.1f}%",
                "subtitle": f"按{pay}统计出院人次",
                "data": [{"name": str(k), "value": int(v)} for k, v in vc.items()],
                "facts": [f"{k}：{int(v)} 人次（{v / vc.sum() * 100:.1f}%）" for k, v in vc.items()],
            })

    return charts


def _title_year(cnt: pd.Series) -> str:
    peak = cnt.idxmax()
    return f"{int(peak)} 年出院人次最多（{int(cnt.loc[peak])} 人次）"


def _partial_last_year(cnt: pd.Series) -> bool:
    """末年记录数明显低于其他年度时，判定为"数据导出截止造成的不完整年度"。

    这类年份必须从同比/增幅类结论里剔除，否则会得出"业务量腰斩"的错误结论。
    """
    if len(cnt) < 3:
        return False
    return bool(cnt.iloc[-1] < cnt.iloc[:-1].median() * 0.5)


def _pick(d: pd.DataFrame, names: list[str]) -> str | None:
    for n in names:
        if n in d.columns and d[n].notna().any():
            return n
    return None


def _fee_columns(d: pd.DataFrame) -> list[str]:
    from quality import FEE_ITEM_NAMES
    return [c for c in FEE_ITEM_NAMES if c in d.columns]


def _r(v):
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return None
    try:
        return round(float(v), 2)
    except (TypeError, ValueError):
        return v
