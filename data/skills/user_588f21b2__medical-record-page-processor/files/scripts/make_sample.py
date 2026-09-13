# -*- coding: utf-8 -*-
"""生成模拟病案首页数据，用于演示与自测。

刻意保留真实导出的「脏」特征，方便验证工具的各条能力：
- 表格前 3 行是报表标题 / 导出时间 / 单位（脏表头）
- 列名带尾随空格、同义异名（入院科室 / 出院科室名称）
- 编码不统一（性别 1/2、离院方式 1–9、日期混用 / 与 8 位紧凑格式）
- 病案号被 Excel 读成 "12345.0"
- 混入逻辑错误：日期倒挂、天数不符、编码格式错、抢救次数矛盾、重复记录
- 混入隐私字段（姓名 / 身份证 / 电话 / 住址）
所有数据均为程序随机生成，不对应任何真实患者。
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

DEPTS = ["呼吸与危重症医学科", "心血管内科", "神经内科", "普外科", "骨科", "儿科",
         "妇产科", "消化内科", "肿瘤科", "急诊医学科", "泌尿外科", "眼科"]
DIAGNOSES = [
    ("J18.900", "肺炎，未特指病原体"), ("J44.100", "慢性阻塞性肺疾病伴急性加重"),
    ("J45.900", "支气管哮喘"), ("I10.x00", "高血压病"), ("E11.900", "2型糖尿病"),
    ("I25.101", "冠状动脉粥样硬化性心脏病"), ("K35.900", "急性阑尾炎"),
    ("S72.001", "股骨颈骨折"), ("C34.900", "肺恶性肿瘤"), ("J15.900", "细菌性肺炎"),
    ("N20.000", "肾结石"), ("I63.900", "脑梗死"), ("K29.500", "慢性胃炎"),
    ("J06.900", "急性上呼吸道感染"), ("A16.200", "肺结核"),
]
OPS = [("31.1", "气管切开术", "三级"), ("47.09", "阑尾切除术", "二级"),
       ("81.51", "全髋关节置换术", "四级"), ("51.23", "腹腔镜胆囊切除术", "三级"),
       ("38.93", "静脉导管置入术", "二级"), ("96.72", "气管插管", "二级"),
       ("", "", ""), ("", "", ""), ("", "", "")]
PAY = ["城镇职工基本医疗保险", "城乡居民基本医疗保险", "全自费", "商业健康保险", "异地医保"]
MARRIAGE = ["未婚", "已婚", "离异", "丧偶"]

COLUMNS = ["病案号 ", "住院次数", "患者姓名", "性别", "年龄", "身份证号", "联系电话",
           "现住址", "入院日期", "入院科室名称", "出院日期", "出院科室名称 ",
           "实际住院天数", "婚姻状况", "医疗付费方式", "出院主要诊断", "主要诊断编码",
           "其他诊断编码", "手术及操作", "手术编码", "手术级别", "麻醉方式",
           "离院方式", "抢救次数", "抢救成功次数", "住院总费用", "西药费", "中药费",
           "化验费", "影像学诊断费", "手术治疗费", "护理费", "卫生材料费", "其他费",
           "主诊医师", "编码员"]


def generate(outdir: str, rows_per_file: int = 700, seed: int = 20240911) -> list[str]:
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(seed)
    files = []
    for year, fmt in [(2023, "xlsx"), (2024, "xlsx"), (2025, "csv")]:
        df = _one_year(rng, rows_per_file, year)
        path = os.path.join(outdir, f"模拟病案首页_{year}.{fmt}")
        if fmt == "xlsx":
            _write_messy_excel(df, path, year)
        else:
            df.to_csv(path, index=False, encoding="gb18030")
        files.append(path)
    return files


def _one_year(rng, n: int, year: int) -> pd.DataFrame:
    base = int(year) * 10000
    ids = rng.integers(1, 99999, size=n)
    # 3% 重复病案号（同一次住院重复上报）
    dup_idx = rng.choice(n, size=max(1, n // 30), replace=False)
    ids[dup_idx] = ids[rng.integers(0, n, size=len(dup_idx))]

    admit = pd.to_datetime(
        [f"{year}-{rng.integers(1, 13):02d}-{rng.integers(1, 29):02d}" for _ in range(n)])
    los = np.clip(rng.gamma(2.0, 3.4, size=n).round(), 0, 180).astype(int)
    discharge = admit + pd.to_timedelta(los, unit="D")

    dept_in = rng.choice(DEPTS, size=n)
    # 85% 患者入院科室=出院科室（转科较少）
    dept_out = np.where(rng.random(n) < 0.85, dept_in, rng.choice(DEPTS, size=n))
    diag_idx = rng.integers(0, len(DIAGNOSES), size=n)
    op_idx = rng.integers(0, len(OPS), size=n)

    total = np.round(rng.gamma(2.2, 4200, size=n) + 600, 2)
    # 费用构成用 Dirichlet 分配，保证分项合计 ≈ 总费用（真实数据的基本特征）
    shares = rng.dirichlet([3.2, 0.8, 2.2, 1.6, 1.8, 1.2, 2.0, 1.0], size=n)
    fee = total.reshape(-1, 1) * shares
    fee = np.round(fee, 2)
    drug, herb, lab, img, opfee, nurse, mat, other = [fee[:, i] for i in range(8)]
    # 无手术的病例不给手术治疗费（该份额并入其他费，保持分项合计=总费用）
    has_op_mask = np.array([OPS[i][0] != "" for i in op_idx])
    other = np.round(other + np.where(has_op_mask, 0.0, opfee), 2)
    opfee = np.where(has_op_mask, opfee, 0.0)

    out_way = rng.choice(["1", "2", "3", "4", "5", "9"], size=n,
                         p=[0.86, 0.03, 0.02, 0.06, 0.02, 0.01])
    rescue = np.where(rng.random(n) < 0.06, rng.integers(1, 4, size=n), 0)
    rescue_ok = np.where(rescue > 0, np.minimum(rescue, rng.integers(0, 3, size=n)), 0)

    gender = rng.choice(["1", "2"], size=n)
    age = np.clip(rng.normal(58, 20, size=n).round(), 0, 102).astype(int)
    birth = pd.to_datetime([f"{year - a}-{rng.integers(1, 13):02d}-{rng.integers(1, 29):02d}"
                            for a in age])
    phone = [f"1{rng.integers(3, 9)}{rng.integers(10**8, 10**9 - 1)}" for _ in range(n)]
    idcard = [f"3201{rng.integers(10**14, 10**15 - 1)}" for _ in range(n)]
    names = [f"患者{chr(65 + (i % 26))}{i % 100:02d}" for i in range(n)]

    df = pd.DataFrame({
        "病案号 ": [f"{x}.0" if rng.random() < 0.3 else str(x) for x in ids],
        "住院次数": [str(rng.integers(1, 4)) for _ in range(n)],
        "患者姓名": names,
        "性别": gender,
        "年龄": age.astype(object),
        "身份证号": idcard,
        "联系电话": phone,
        "现住址": [f"XX省XX市XX区XX路{rng.integers(1, 999)}号" for _ in range(n)],
        "入院日期": [_fmt_date(x, rng, year) for x in admit],
        "入院科室名称": dept_in,
        "出院日期": [_fmt_date(x, rng, year) for x in discharge],
        "出院科室名称 ": dept_out,
        "实际住院天数": los.astype(object),
        "婚姻状况": rng.choice(MARRIAGE, size=n),
        "医疗付费方式": rng.choice(PAY, size=n),
        "出院主要诊断": [DIAGNOSES[i][1] for i in diag_idx],
        "主要诊断编码": [DIAGNOSES[i][0] for i in diag_idx],
        "其他诊断编码": [DIAGNOSES[(i + 3) % len(DIAGNOSES)][0] for i in diag_idx],
        "手术及操作": [OPS[i][1] for i in op_idx],
        "手术编码": [OPS[i][0] for i in op_idx],
        "手术级别": [OPS[i][2] for i in op_idx],
        "麻醉方式": np.where([OPS[i][0] != "" for i in op_idx],
                             rng.choice(["全身麻醉", "椎管内麻醉", "局部麻醉"], size=n), ""),
        "离院方式": out_way,
        "抢救次数": rescue.astype(object),
        "抢救成功次数": rescue_ok.astype(object),
        "住院总费用": total,
        "西药费": drug,
        "中药费": herb,
        "化验费": lab,
        "影像学诊断费": img,
        "手术治疗费": opfee,
        "护理费": nurse,
        "卫生材料费": mat,
        "其他费": other,
        "主诊医师": [f"医师{chr(65 + (i % 20))}" for i in range(n)],
        "编码员": [f"编码{chr(65 + (i % 8))}" for i in range(n)],
    })
    df["出生日期"] = [b.strftime("%Y/%m/%d") for b in birth]
    _inject_dirt(df, rng, n)
    return df


def _fmt_date(ts, rng, year) -> str:
    r = rng.random()
    if r < 0.15:
        return ts.strftime("%Y%m%d")
    if r < 0.45:
        return ts.strftime("%Y/%m/%d")
    return ts.strftime("%Y-%m-%d 00:00:00" if r > 0.9 else "%Y-%m-%d")


def _inject_dirt(df: pd.DataFrame, rng, n: int) -> None:
    def pick(k, frac):
        m = max(1, int(n * frac))
        return rng.choice(n, size=m, replace=False)

    # 日期倒挂：出院日期早于入院日期
    for i in pick(0, 0.02):
        df.at[i, "出院日期"], df.at[i, "入院日期"] = df.at[i, "入院日期"], df.at[i, "出院日期"]
    # 住院天数与日期不符
    for i in pick(1, 0.05):
        df.at[i, "实际住院天数"] = int(rng.integers(0, 20)) + 100
    # 性别异常值
    for i in pick(2, 0.015):
        df.at[i, "性别"] = "3"
    # 年龄缺失
    for i in pick(3, 0.04):
        df.at[i, "年龄"] = None
    # 诊断编码格式错（混入中文名）
    for i in pick(4, 0.02):
        df.at[i, "主要诊断编码"] = df.at[i, "出院主要诊断"]
    # 离院方式非标值
    for i in pick(5, 0.02):
        df.at[i, "离院方式"] = "治愈"
    # 抢救成功次数 > 抢救次数
    for i in pick(6, 0.01):
        df.at[i, "抢救次数"] = 1
        df.at[i, "抢救成功次数"] = 3
    # 总费用为 0
    for i in pick(7, 0.01):
        df.at[i, "住院总费用"] = 0
    # 费用分项严重不平（漏记药品费）
    for i in pick(8, 0.03):
        df.at[i, "西药费"] = 0
    # 手术编码存在但手术级别为空
    for i in pick(9, 0.02):
        df.at[i, "手术级别"] = ""
    # 病案号缺失
    for i in pick(10, 0.005):
        df.at[i, "病案号 "] = None


def _write_messy_excel(df: pd.DataFrame, path: str, year: int) -> None:
    """写成带标题行、表头在第 4 行的 Excel（模拟系统报表导出）。"""
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="病案首页", index=False, startrow=3)
        ws = writer.sheets["病案首页"]
        ws["A1"] = f"XX市人民医院 {year} 年度住院病案首页数据导出表"
        ws["A2"] = "导出时间：2026-09-11  导出人：病案科  说明：本表仅用于内部质控，请勿外传"
        ws["A3"] = ""
        for col in ws.columns:
            width = max(len(str(c.value or "")) for c in col[:6]) + 2
            ws.column_dimensions[col[0].column_letter].width = min(max(width, 8), 22)
        ws.freeze_panes = "A5"


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print("已生成：")
    for f in generate(target):
        print(" -", f)
