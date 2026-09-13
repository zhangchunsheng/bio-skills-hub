# -*- coding: utf-8 -*-
"""数据定型、指标派生与机构级 KPI 计算。

这是「病案首页数据处理器」的指标口径层。所有口径定义集中在
references/indicator_caliber.md，本模块实现与之一一对应，允许通过
配置覆盖（如住院天数 0 基/1 基、年龄段切点）。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fields import CANON_SPEC, VALUE_MAPS
from loader import clean_id_string, to_datetime, to_numeric

DEFAULT_CFG = {
    "los_offset": 0,            # 住院天数口径：0 = 出院-入院（同日入出院=0 天）
    "age_bins": [0, 18, 45, 60, 75, 200],
    "age_labels": ["0-17岁", "18-44岁", "45-59岁", "60-74岁", "75岁及以上"],
    "readmission_days": 31,
}

FEE_DRUG = ["西药费", "中药费"]
FEE_MATERIAL = ["检查用一次性材料费", "治疗用一次性材料费", "手术用一次性材料费", "耗材费"]
FEE_EXAM = ["实验室诊断费", "影像学诊断费", "病理诊断费", "临床诊断项目费"]
FEE_TREAT = ["手术治疗费", "非手术治疗项目费", "一般治疗操作费", "护理费", "一般医疗服务费",
             "综合医疗服务费", "康复费", "中医治疗费"]

LEVEL_MAP = {"1": "一级", "2": "二级", "3": "三级", "4": "四级",
             "一级": "一级", "二级": "二级", "三级": "三级", "四级": "四级",
             "0": "未分级", "一": "一级", "二": "二级", "三": "三级", "四": "四级"}


# ---------------------------------------------------------------------------
# 1. 定型：原始列名 -> 标准字段名 + 类型转换 + 隐私剔除
# ---------------------------------------------------------------------------
def canonicalize(df: pd.DataFrame, mapping: dict, drop_privacy: bool = True) -> dict:
    """按字段映射把原始表转成标准字段表。

    返回 {df, privacy_cols, kept_raw, dropped_raw, typed}
    """
    rename = {raw: canon for raw, canon in mapping.items() if raw in df.columns}
    work = df.rename(columns=rename)

    privacy_cols = [c for c in work.columns
                    if CANON_SPEC.get(c, {}).get("privacy")]
    dropped: list[str] = []
    if drop_privacy and privacy_cols:
        work = work.drop(columns=privacy_cols)
        dropped = list(privacy_cols)

    typed: list[str] = []
    for col in list(work.columns):
        spec = CANON_SPEC.get(col)
        if spec is None:
            continue
        dt = spec["dtype"]
        if dt == "id":
            work[col] = clean_id_string(work[col])
        elif dt in ("date", "datetime"):
            work[col] = to_datetime(work[col])
        elif dt == "number":
            work[col] = to_numeric(work[col])
        elif dt == "category":
            work[col] = _norm_category(work[col], col)
        else:
            work[col] = work[col].astype(str).str.strip().replace({"nan": None, "None": None})
        typed.append(col)

    return {"df": work, "privacy_cols": privacy_cols,
            "dropped_raw": dropped, "typed": typed,
            "kept_canon": [c for c in work.columns if c in CANON_SPEC]}


def _norm_category(s: pd.Series, col: str) -> pd.Series:
    txt = s.astype(str).str.strip()
    txt = txt.replace({"nan": None, "None": None, "": None})
    vmap = VALUE_MAPS.get(col)
    if not vmap:
        return txt
    out = txt.str.lower().map(vmap)
    # 已是标准值但大小写不一致的，回填原值（如"男"）
    return out.fillna(txt)


# ---------------------------------------------------------------------------
# 2. 派生指标
# ---------------------------------------------------------------------------
def derive(df: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """在标准字段表上派生分析所需的行级变量。"""
    c = {**DEFAULT_CFG, **(cfg or {})}
    d = df.copy()

    # 住院天数
    adm, dis = d.get("入院日期"), d.get("出院日期")
    if adm is not None and dis is not None:
        calc = (dis - adm).dt.days + int(c["los_offset"])
        d["住院天数_计算"] = calc.where(calc >= 0)
    if "实际住院天数" in d.columns:
        d["住院天数"] = d["实际住院天数"].where(
            d["实际住院天数"].notna() & (d["实际住院天数"] >= 0),
            d.get("住院天数_计算"))
    elif "住院天数_计算" in d.columns:
        d["住院天数"] = d["住院天数_计算"]

    # 年龄
    age = d.get("年龄")
    unit = d.get("年龄单位")
    age_calc = None
    if age is not None:
        age_calc = age.astype(float)
        if unit is not None:
            u = unit.astype(str)
            age_calc = age_calc.where(~u.str.contains("月"), age_calc / 12.0)
            age_calc = age_calc.where(~u.str.contains("天"), age_calc / 365.0)
    birth = d.get("出生日期")
    if birth is not None and adm is not None:
        from_birth = ((adm - birth).dt.days / 365.25).round(1)
        from_birth = from_birth.where(from_birth.between(0, 120))
        if age_calc is not None:
            mismatch = age_calc.notna() & from_birth.notna() & ((age_calc - from_birth).abs() > 2)
            d["年龄_生日推算"] = from_birth
            d["年龄_口径不一致"] = mismatch
            age_calc = age_calc.where(age_calc.notna(), from_birth)
        else:
            age_calc = from_birth
    d["年龄_计算"] = age_calc
    if age_calc is not None:
        d["年龄段"] = pd.cut(age_calc, bins=c["age_bins"], labels=c["age_labels"],
                             right=False, include_lowest=True).astype(object)

    # 时间维度
    key_date = dis if dis is not None else adm
    if key_date is not None:
        d["年份"] = key_date.dt.year
        d["月份"] = key_date.dt.month
        d["季度"] = key_date.dt.quarter
        d["年月"] = key_date.dt.strftime("%Y-%m")

    # 手术相关：优先用手术编码/名称判断；两者都缺时退回手术日期；再退回手术费
    has_op = pd.Series(False, index=d.index)
    op_src = [c for c in ("手术操作编码", "手术操作名称") if c in d.columns]
    if op_src:
        for col in op_src:
            txt = d[col].astype(str).str.strip()
            has_op |= (d[col].notna() & ~txt.isin(["", "nan", "None", "-", "无", "0"]))
    elif "手术日期" in d.columns:
        has_op = d["手术日期"].notna()
    else:
        fee_op = d.get("手术治疗费")
        if fee_op is not None:
            has_op = fee_op.fillna(0) > 0
    d["有无手术"] = np.where(has_op, "有手术", "无手术")
    d["是否三四级手术"] = np.where(
        d.get("手术级别_标准化", pd.Series(index=d.index, dtype=object)).isin(["三级", "四级"]),
        "是", "否") if "手术级别_标准化" in d else "否"
    lvl = d.get("手术级别")
    if lvl is not None:
        d["手术级别_标准化"] = (lvl.astype(str).str.strip().str.lower()
                              .map(LEVEL_MAP).fillna(lvl))
        d["是否三四级手术"] = np.where(d["手术级别_标准化"].isin(["三级", "四级"]), "是", "否")

    # 结局
    way = d.get("离院方式")
    if way is not None:
        w = way.astype(str).str.strip()
        d["是否死亡"] = np.where(w.isin(["死亡", "5"]), "是", "否")
        d["是否非医嘱离院"] = np.where(w.isin(["非医嘱离院", "4"]), "是", "否")
    rescue = d.get("抢救次数")
    if rescue is not None:
        d["是否抢救"] = np.where(rescue.fillna(0) > 0, "是", "否")
    oks = d.get("抢救成功次数")
    if oks is not None:
        d["是否抢救成功"] = np.where(oks.fillna(0) > 0, "是", "否")

    # 费用结构
    total = d.get("总费用")
    if total is not None:
        drug = _sum_cols(d, FEE_DRUG)
        mat = _sum_cols(d, FEE_MATERIAL)
        d["西药中药费合计"] = drug
        d["材料费合计"] = mat
        d["检查检验费合计"] = _sum_cols(d, FEE_EXAM)
        d["治疗手术费合计"] = _sum_cols(d, FEE_TREAT)
        safe = total.replace(0, np.nan)
        if drug.notna().any():
            d["药占比"] = (drug / safe * 100).round(2)
        if mat.notna().any():
            d["耗占比"] = (mat / safe * 100).round(2)
        los = d.get("住院天数")
        if los is not None:
            d["日均费用"] = (total / los.replace(0, np.nan)).round(2)
        items = [x for x in FEE_MATERIAL + FEE_EXAM + FEE_TREAT + FEE_DRUG + ["其他费"]
                 if x in d.columns]
        if len(items) >= 3:
            parts = _sum_cols(d, items)
            d["费用分项合计"] = parts
            d["费用分项偏差率"] = ((parts - total).abs() / safe * 100).round(2)

    # 31 天再入院
    pid = d.get("病案号") if d.get("病案号") is not None else d.get("研究ID")
    if pid is not None and adm is not None and dis is not None:
        tmp = pd.DataFrame({"pid": pid, "adm": adm, "dis": dis, "idx": d.index})
        tmp = tmp.dropna(subset=["pid", "adm", "dis"]).sort_values(["pid", "adm"])
        tmp["prev_dis"] = tmp.groupby("pid")["dis"].shift(1)
        gap = (tmp["adm"] - tmp["prev_dis"]).dt.days
        flag = (gap >= 0) & (gap <= int(c["readmission_days"]))
        d["是否31天再入院"] = "否"
        d.loc[tmp.loc[flag, "idx"], "是否31天再入院"] = "是"

    return d


def _sum_cols(d: pd.DataFrame, cols: list[str]) -> pd.Series:
    present = [c for c in cols if c in d.columns]
    if not present:
        return pd.Series(np.nan, index=d.index)
    out = d[present[0]].fillna(0)
    for c in present[1:]:
        out = out + d[c].fillna(0)
    if d[present].notna().sum(axis=1).eq(0).all():
        return pd.Series(np.nan, index=d.index)
    return out


# ---------------------------------------------------------------------------
# 3. 机构级 KPI
# ---------------------------------------------------------------------------
def kpis(d: pd.DataFrame) -> dict:
    """计算机构级核心指标；每项都带分子/分母，便于报告里溯源。"""
    n = len(d)
    k: dict[str, dict] = {}

    def put(name, value, unit="", num=None, den=None, caliber=""):
        k[name] = {"值": _round(value), "单位": unit,
                   "分子": _round(num) if num is not None else None,
                   "分母": _round(den) if den is not None else None,
                   "口径": caliber}

    put("出院人次", n, "人次", caliber="首页记录条数（未去重）")
    pid = d.get("病案号") if d.get("病案号") is not None else d.get("研究ID")
    if pid is not None:
        put("患者数（去重）", int(pid.nunique()), "人", caliber="病案号/研究ID 去重计数")
        if n:
            put("人均住院次数", round(n / max(1, pid.nunique()), 2), "次/人",
                caliber="出院人次 ÷ 患者数")

    los = d.get("住院天数")
    if los is not None and los.notna().any():
        put("平均住院日", float(los.mean()), "天", caliber="∑住院天数 ÷ 出院人次；住院天数=出院日期-入院日期")
        put("中位住院日", float(los.median()), "天", caliber="住院天数 P50")
        put("住院日 P90", float(los.quantile(0.9)), "天", caliber="住院天数 90 分位")
    total = d.get("总费用")
    if total is not None and total.notna().any():
        put("总费用", float(total.sum()), "元", caliber="∑总费用")
        put("次均费用", float(total.mean()), "元",
            caliber="∑总费用 ÷ 出院人次（含未产生费用记录）")
        put("次均费用（中位）", float(total.median()), "元", caliber="总费用 P50")
    day_fee = d.get("日均费用")
    if day_fee is not None and day_fee.notna().any():
        put("日均费用", float(day_fee.mean()), "元/天", caliber="总费用 ÷ 住院天数 的均值")

    for name, col, caliber in [
        ("药占比", "药占比", "（西药费+中药费）÷ 总费用，按例均值口径"),
        ("耗占比", "耗占比", "一次性医用材料费合计 ÷ 总费用"),
    ]:
        s = d.get(col)
        if s is not None and s.notna().any():
            drug_sum = d.get("西药中药费合计")
            mat_sum = d.get("材料费合计")
            base = total if total is not None else None
            if "药" in name and drug_sum is not None and base is not None:
                put(name, float(drug_sum.sum() / base.sum() * 100), "%",
                    num=float(drug_sum.sum()), den=float(base.sum()),
                    caliber="全院合计口径（分子分母分别求和），与按例均值口径略有差异")
            elif "耗" in name and mat_sum is not None and base is not None:
                put(name, float(mat_sum.sum() / base.sum() * 100), "%",
                    num=float(mat_sum.sum()), den=float(base.sum()), caliber=caliber)
            else:
                put(name, float(s.mean()), "%", caliber=caliber)

    dead = d.get("是否死亡")
    if dead is not None:
        cnt = int((dead == "是").sum())
        put("死亡率", cnt / n * 100 if n else 0, "%", num=cnt, den=n,
            caliber="离院方式=死亡 例数 ÷ 出院人次")
    nono = d.get("是否非医嘱离院")
    if nono is not None:
        cnt = int((nono == "是").sum())
        put("非医嘱离院率", cnt / n * 100 if n else 0, "%", num=cnt, den=n,
            caliber="离院方式=非医嘱离院 ÷ 出院人次")
    op = d.get("有无手术")
    if op is not None:
        cnt = int((op == "有手术").sum())
        put("手术率", cnt / n * 100 if n else 0, "%", num=cnt, den=n,
            caliber="有手术编码或手术费>0 的例数 ÷ 出院人次")
        lv34 = d.get("是否三四级手术")
        if lv34 is not None and cnt:
            c34 = int((lv34 == "是").sum())
            put("三四级手术占比", c34 / cnt * 100, "%", num=c34, den=cnt,
                caliber="手术级别为三/四级例数 ÷ 有手术例数")
    r = d.get("抢救次数")
    if r is not None and r.fillna(0).sum() > 0:
        oks = d.get("抢救成功次数", pd.Series(0, index=d.index)).fillna(0)
        put("抢救成功率", float(oks.sum() / r.sum() * 100), "%",
            num=float(oks.sum()), den=float(r.sum()),
            caliber="∑抢救成功次数 ÷ ∑抢救次数")
    re31 = d.get("是否31天再入院")
    if re31 is not None and (re31 == "是").any():
        cnt = int((re31 == "是").sum())
        put("31天再入院率", cnt / n * 100 if n else 0, "%", num=cnt, den=n,
            caliber="与上一次出院间隔≤31天的再入院 ÷ 出院人次（需同一患者纵向数据）")
    rw = d.get("DRG权重")
    if rw is not None and rw.notna().any():
        put("CMI（病例组合指数）", float(rw.mean()), "", caliber="DRG 权重的算术均值")
        grp = d.get("DRG代码") if d.get("DRG代码") is not None else d.get("DRG名称")
        if grp is not None:
            put("DRG 组数", int(grp.nunique()), "组", caliber="DRG 编码/名称去重数")
    age = d.get("年龄_计算")
    if age is not None and age.notna().any():
        put("平均年龄", float(age.mean()), "岁", caliber="年龄字段（缺失时按出生日期推算）均值")
    return k


def _round(v):
    if v is None:
        return None
    if isinstance(v, (int, np.integer)):
        return int(v)
    try:
        f = float(v)
    except (TypeError, ValueError):
        return v
    if not np.isfinite(f):
        return None
    return round(f, 2)
