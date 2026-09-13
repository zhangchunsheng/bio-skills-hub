# -*- coding: utf-8 -*-
"""病案首页数据质量控制规则引擎。

规则覆盖四类问题：
- 完整性（必填缺失、关键字段为空）
- 一致性（日期倒挂、天数与日期矛盾、费用分项不平、抢救次数矛盾）
- 规范性（值域越界、ICD 编码格式、病案号重复）
- 合规性（直接标识符是否残留）

每条规则输出：命中例数、发生率、最多 5 条样例明细、整改建议。
"""

from __future__ import annotations

import re

import pandas as pd

from loader import to_numeric

SEV_FATAL = "致命"
SEV_MAJOR = "严重"
SEV_INFO = "提示"

ICD10_RE = re.compile(r"^[A-Z]\d{2}(\.\w{1,4})?$")
ICD9_RE = re.compile(r"^\d{2}(\.\d{1,3})?$")

MAX_SAMPLES = 5


class _Ctx:
    """规则运行上下文：持有数据、列索引与惰性计算缓存。"""

    def __init__(self, df: pd.DataFrame, privacy_cols: list[str], cfg: dict | None = None):
        self.df = df
        self.privacy_cols = privacy_cols
        self.cfg = cfg or {}
        self.n = len(df)
        self._cache: dict[str, pd.Series] = {}

    def s(self, name: str) -> pd.Series | None:
        if name in self._cache:
            return self._cache[name]
        if name not in self.df.columns:
            return None
        self._cache[name] = self.df[name]
        return self._cache[name]

    def num(self, name: str) -> pd.Series | None:
        key = f"#num#{name}"
        if key in self._cache:
            return self._cache[key]
        raw = self.s(name)
        if raw is None:
            return None
        self._cache[key] = to_numeric(raw)
        return self._cache[key]

    def dt(self, name: str) -> pd.Series | None:
        key = f"#dt#{name}"
        if key in self._cache:
            return self._cache[key]
        if name in self.df.columns:
            self._cache[key] = pd.to_datetime(self.df[name], errors="coerce")
            return self._cache[key]
        return None

    def ids(self) -> pd.Series:
        s = self.s("病案号")
        if s is None:
            s = self.s("研究ID")
        if s is None:
            return pd.Series([f"第{i + 1}行" for i in range(self.n)], index=self.df.index)
        return s.astype(str).where(s.notna(), pd.Series([f"第{i + 1}行" for i in range(self.n)],
                                                       index=self.df.index))


SENSITIVE_KEY_PAT = re.compile(r"病案号|研究ID|住院号|病历号|身份证|姓名|联系电[话]|住址|电话")


def mask_id(v: str) -> str:
    """标识打码：保留尾 4 位，其余用 * 代替；空值不打码。"""
    v = str(v).strip()
    if not v or v.lower() in ("nan", "none", "nat"):
        return "缺失"
    if len(v) <= 4:
        return "****" + v[-2:] if len(v) > 2 else "****"
    return "*" * (len(v) - 4) + v[-4:]


def mask_samples(issues: list[dict]) -> None:
    """就地打码样例明细中的直接标识符（病案号等），供对外报告使用。"""
    for issue in issues:
        for s_ in issue.get("samples", []):
            rid = str(s_.get("记录标识", ""))
            # "第N行" 是无病案号时的行号回退标识，不是患者标识，原样保留
            if not re.fullmatch(r"第\d+行", rid):
                s_["记录标识"] = mask_id(rid)
            detail = s_.get("明细") or {}
            for k in list(detail):
                if SENSITIVE_KEY_PAT.search(str(k)):
                    detail[k] = mask_id(detail[k])


def run_checks(df: pd.DataFrame, privacy_cols: list[str], cfg: dict | None = None) -> dict:
    """跑全部质控规则，返回问题清单与质量分。"""
    ctx = _Ctx(df, privacy_cols, cfg)
    issues: list[dict] = []

    def add(rule, name, severity, mask, detail_fn=None, advice=""):
        if mask is None:
            return
        mask = mask.fillna(False).astype(bool)
        cnt = int(mask.sum())
        if cnt == 0:
            return
        idx = df.index[mask][:MAX_SAMPLES]
        samples = []
        for i in idx:
            rid = str(ctx.ids().loc[i])
            row = df.loc[i]
            vals = {}
            if detail_fn is not None:
                vals = detail_fn(row)
            samples.append({"记录标识": rid, "明细": vals})
        issues.append({
            "rule": rule, "name": name, "severity": severity,
            "count": cnt, "rate": round(cnt / ctx.n, 4) if ctx.n else 0.0,
            "samples": samples, "advice": advice,
        })

    # ---- 完整性 ----
    for f, sev in [("病案号", SEV_FATAL), ("性别", SEV_MAJOR), ("年龄", SEV_MAJOR),
                   ("入院日期", SEV_FATAL), ("出院日期", SEV_FATAL),
                   ("主要诊断名称", SEV_MAJOR), ("主要诊断编码", SEV_MAJOR),
                   ("总费用", SEV_MAJOR), ("离院方式", SEV_MAJOR)]:
        raw = ctx.s(f)
        if raw is None:
            continue
        txt = raw.astype(str).str.strip()
        mask = raw.isna() | txt.isin(["", "nan", "None", "-", "无", "0"])
        if f in ("总费用",):
            mask = raw.isna() | (ctx.num(f) == 0)
        add(f"Q001-{f}", f"{f}缺失或为空", sev, mask,
            lambda r, f=f: {f: str(r.get(f))},
            f"补录 {f} 后重新导出；缺失率过高时该字段相关指标不可用。")

    # ---- 病案号重复 ----
    key = ctx.s("病案号")
    if key is not None:
        sub = [key.astype(str)]
        for extra in ("住院次数", "入院日期"):
            if extra in df.columns:
                sub.append(df[extra].astype(str))
                break
        dup = pd.concat(sub, axis=1).duplicated(keep=False) & key.notna()
        add("Q002", "病案号（+住院次数）重复记录", SEV_MAJOR, dup,
            lambda r: {"病案号": str(r.get("病案号")), "住院次数": str(r.get("住院次数"))},
            "去重或核对病案号/住院次数赋值，避免人次与人头统计口径混淆。")

    # ---- 日期逻辑 ----
    adm, dis = ctx.dt("入院日期"), ctx.dt("出院日期")
    if adm is not None and dis is not None:
        add("Q003", "出院日期早于入院日期", SEV_FATAL, (dis < adm).fillna(False),
            lambda r: {"入院": str(r.get("入院日期")), "出院": str(r.get("出院日期"))},
            "核对两个日期字段是否填反，这是最常见的首页录入错误。")
        today = pd.Timestamp.today().normalize()
        add("Q004", "入院/出院日期超出合理范围（1980 年前或未来）", SEV_MAJOR,
            (adm < pd.Timestamp("1980-01-01")) | (adm > today + pd.Timedelta(days=1)),
            lambda r: {"入院": str(r.get("入院日期"))}, "核对日期格式解析是否正确（如 Excel 序列号）。")
        los_calc = (dis - adm).dt.days
        reals = ctx.num("实际住院天数")
        if reals is not None:
            diff = (reals - los_calc).abs()
            add("Q005", "实际住院天数与出入院日期推算值不一致（差>1天）", SEV_MAJOR,
                ((diff > 1) & reals.notna() & los_calc.notna()).fillna(False),
                lambda r: {"填报天数": str(r.get("实际住院天数")),
                           "推算天数": str((pd.to_datetime(r.get("出院日期"), errors="coerce")
                                          - pd.to_datetime(r.get("入院日期"), errors="coerce")).days)},
                "统一住院天数口径（出院日期-入院日期，同日入出院记 1 天或 0 天需全院一致）。")
        add("Q006", "实际住院天数为负或超过 365 天", SEV_FATAL,
            ((reals < 0) | (reals > 365)).fillna(False) if reals is not None else None,
            lambda r: {"实际住院天数": str(r.get("实际住院天数"))}, "核对是否为跨年长期住院或录入错误。")
        op = ctx.dt("手术日期")
        if op is not None:
            add("Q007", "手术日期不在住院区间内", SEV_MAJOR,
                ((op < adm) | (op > dis + pd.Timedelta(days=1))).fillna(False),
                lambda r: {"入院": str(r.get("入院日期")), "手术": str(r.get("手术日期")),
                           "出院": str(r.get("出院日期"))},
                "核对手术日期填报，或确认是否为入院前已实施的手术。")

    # ---- 值域 ----
    sex = ctx.s("性别")
    if sex is not None:
        txt = sex.astype(str).str.strip()
        add("Q008", "性别取值异常（非男/女/未知）", SEV_MAJOR,
            (~txt.isin(["男", "女", "未知", "1", "2", "M", "F", "m", "f"])).fillna(False),
            lambda r: {"性别": str(r.get("性别"))}, "规范性别取值，避免影响性别分层统计。")

    age = ctx.num("年龄")
    if age is not None:
        add("Q009", "年龄超出合理区间（<0 或 >120）", SEV_MAJOR,
            ((age < 0) | (age > 120)).fillna(False),
            lambda r: {"年龄": str(r.get("年龄")), "年龄单位": str(r.get("年龄单位"))},
            "核对年龄单位（岁/月/天），婴幼儿须以月龄折算或标注单位。")

    way = ctx.s("离院方式")
    if way is not None:
        txt = way.astype(str).str.strip()
        legal = ["医嘱离院", "医嘱转院", "医嘱转社区", "非医嘱离院", "死亡", "其他",
                 "1", "2", "3", "4", "5", "9"]
        add("Q010", "离院方式取值不在标准值域内", SEV_MAJOR,
            (~txt.isin(legal)).fillna(False),
            lambda r: {"离院方式": str(r.get("离院方式"))},
            "按国标取值：1医嘱离院 2医嘱转院 3医嘱转社区 4非医嘱离院 5死亡 9其他。")

    # ---- 编码规范 ----
    for f, pat, rule, sev in [("主要诊断编码", ICD10_RE, "Q011", SEV_MAJOR),
                              ("手术操作编码", ICD9_RE, "Q012", SEV_INFO)]:
        raw = ctx.s(f)
        if raw is None:
            continue
        txt = raw.astype(str).str.strip().str.upper()
        # 空值/缺失不算"格式不规范"，否则会把"无手术"的记录全部误报
        miss = raw.isna() | txt.isin(["", "NAN", "NONE", "-", "无", "NULL"])
        bad = (~txt.str.match(pat.pattern, na=False)) & (~miss)
        add(f"{rule}-格式", f"{f}格式不规范", sev, bad.fillna(False),
            lambda r, f=f: {f: str(r.get(f))},
            "ICD-10 形如 J18.9；ICD-9-CM-3 形如 31.1。格式异常多因混入中文名或系统内码。")

    # ---- 费用 ----
    total = ctx.num("总费用")
    if total is not None:
        add("Q013", "总费用为负值", SEV_FATAL, (total < 0).fillna(False),
            lambda r: {"总费用": str(r.get("总费用"))}, "核对退费/冲账记录是否误入出院费用。")
        items = [c for c in df.columns if c in FEE_ITEM_NAMES]
        if len(items) >= 3:
            parts = sum((ctx.num(c).fillna(0) for c in items[1:]), pd.Series(0.0, index=df.index))
            dev = (parts - total).abs() / total.abs().replace(0, pd.NA)
            add("Q014", "费用分项合计与总费用偏差超过 5%", SEV_MAJOR,
                (dev > 0.05).fillna(False),
                lambda r: {"总费用": str(r.get("总费用"))},
                "费用分项口径不一致（如是否含自费、是否含院外购药），会影响药占比等派生指标。")

    # ---- 临床逻辑 ----
    rescue = ctx.num("抢救次数")
    ok = ctx.num("抢救成功次数")
    if rescue is not None and ok is not None:
        add("Q015", "抢救成功次数大于抢救次数", SEV_FATAL, (ok > rescue).fillna(False),
            lambda r: {"抢救次数": str(r.get("抢救次数")),
                       "抢救成功次数": str(r.get("抢救成功次数"))}, "核对抢救数据填报来源。")
    if way is not None:
        dead = ctx.s("是否死亡")
        dmask = (way.astype(str).str.strip().isin(["5", "死亡"])) if dead is None else dead.astype(str).isin(["是", "True", "1"])
        if rescue is not None:
            add("Q016", "死亡病例抢救次数为 0", SEV_INFO,
                (dmask & (rescue.fillna(0) == 0)).fillna(False),
                lambda r: {"离院方式": str(r.get("离院方式")),
                           "抢救次数": str(r.get("抢救次数"))},
                "死亡病例通常应记录抢救过程，缺失会低估抢救成功率分母。")
        add("Q017", "死亡病例未填写离院方式=死亡", SEV_INFO, None)

    opcode = ctx.s("手术操作编码")
    opfee = ctx.num("手术治疗费")
    if opcode is not None and opfee is not None:
        has_code = opcode.astype(str).str.strip().replace({"nan": ""}).str.len() > 0
        add("Q018", "有手术编码但手术治疗费为 0", SEV_INFO,
            (has_code & (opfee.fillna(0) == 0)).fillna(False),
            lambda r: {"手术编码": str(r.get("手术操作编码"))},
            "核对手术费是否计入其他费用项，否则手术相关费用分析会失真。")

    # ---- 合规 ----
    if privacy_cols:
        add("Q019", "存在患者直接标识符字段（合规告警，工具已自动剔除）", SEV_INFO,
            pd.Series(True, index=df.index),
            lambda r=None: {"字段": "、".join(privacy_cols)},
            "本工具已默认剔除这些字段且不写入任何输出；外发或分析前请先做去标识化。")

    # 兜底：Q017 的占位（无数据依赖）已跳过
    issues = [i for i in issues if i["count"] > 0]

    return {"issues": issues, "summary": _summary(issues), "score": _score(issues, ctx.n)}


FEE_ITEM_NAMES = [
    "总费用", "综合医疗服务费", "一般医疗服务费", "一般治疗操作费", "护理费", "病理诊断费",
    "实验室诊断费", "影像学诊断费", "临床诊断项目费", "非手术治疗项目费", "手术治疗费",
    "康复费", "中医治疗费", "西药费", "中药费", "血液制品费", "白蛋白类制品费",
    "球蛋白类制品费", "凝血因子类制品费", "细胞因子类制品费", "检查用一次性材料费",
    "治疗用一次性材料费", "手术用一次性材料费", "耗材费", "其他费",
]


def _summary(issues: list[dict]) -> dict:
    out = {SEV_FATAL: 0, SEV_MAJOR: 0, SEV_INFO: 0}
    for i in issues:
        out[i["severity"]] = out.get(i["severity"], 0) + 1
    return {"规则命中数": len(issues), **out}


def _score(issues: list[dict], n: int) -> float:
    """质量分：按致命/严重/提示加权扣分，最低 0 分。"""
    if n == 0:
        return 0.0
    penalty = 0.0
    weights = {SEV_FATAL: 12.0, SEV_MAJOR: 5.0, SEV_INFO: 1.5}
    for i in issues:
        if i["rule"] == "Q019":
            continue
        penalty += weights.get(i["severity"], 1.0) * min(1.0, max(0.1, i["rate"] * 10))
    return round(max(0.0, 100.0 - penalty), 1)
