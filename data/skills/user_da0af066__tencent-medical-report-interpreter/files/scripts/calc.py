#!/usr/bin/env python3
"""
医疗报告深度解读 · 定量风险计算工具

支持的计算：
  egfr   肾小球滤过率（CKD-EPI 2021 去种族系数 + 2009 版对照）
  ascvd  10 年 ASCVD 风险（China-PAR 为主结论 + ACC/AHA PCE 参考对照）
  fib4   肝纤维化无创评分
  bmi    体质指数 + 腰高比 + 腰围分级（中国标准）
  aip    致动脉粥样硬化指数
  homa   胰岛素抵抗指数
  unit   单位换算

数据来源：
  China-PAR : Yang X, et al. Circulation 2016;134(19):1430-1440
              《中国心血管病风险评估和管理指南》中国循环杂志 2019;34(1):4-28
  PCE       : Goff DC, et al. 2013 ACC/AHA Guideline. Circulation 2013
  CKD-EPI   : Inker LA, et al. NEJM 2021（2021版）/ Levey AS, et al. 2009
  FIB-4     : Sterling RK, et al. Hepatology 2006
  分级标准  : 《中国血脂管理指南 2023》《肥胖症诊疗指南 2024》KDIGO CKD 指南

用法：
  python3 calc.py egfr  --cr 88 --age 45 --sex male
  python3 calc.py ascvd --age 55 --sex male --sbp 135 --tc 5.6 --hdl 1.1 --wc 92 \
                        --smoker 1 --diabetes 0 --north 1 --urban 1 --family 0
  python3 calc.py fib4  --age 45 --ast 40 --alt 62 --plt 180
  python3 calc.py bmi   --height 172 --weight 82 --wc 92
  python3 calc.py aip   --tg 2.1 --hdl 1.1
  python3 calc.py homa  --glucose 5.8 --insulin 12.5
  python3 calc.py unit  --item ldl --value 3.2 --to mgdl

免责：本工具仅做数值计算与风险分层提示，不构成诊断。
"""

import argparse
import math
import sys


# ============================================================
# 单位换算
# ============================================================

# 系数定义：mmol/L * factor = mg/dL
UNIT_FACTORS = {
    "tc":       (38.6, "mmol/L", "mg/dL", "总胆固醇"),
    "ldl":      (38.6, "mmol/L", "mg/dL", "LDL-C"),
    "hdl":      (38.6, "mmol/L", "mg/dL", "HDL-C"),
    "nonhdl":   (38.6, "mmol/L", "mg/dL", "非HDL-C"),
    "tg":       (88.5, "mmol/L", "mg/dL", "甘油三酯"),
    "glucose":  (18.0, "mmol/L", "mg/dL", "血糖"),
    "cr":       (1 / 88.4, "umol/L", "mg/dL", "肌酐"),
    "bun":      (2.8, "mmol/L", "mg/dL", "尿素氮"),
    "ua":       (1 / 59.5, "umol/L", "mg/dL", "尿酸"),
    "tbil":     (1 / 17.1, "umol/L", "mg/dL", "总胆红素"),
    "ca":       (4.0, "mmol/L", "mg/dL", "血钙"),
    "vitd":     (1 / 2.5, "nmol/L", "ng/mL", "维生素D"),
}


def convert_unit(item, value, to):
    if item not in UNIT_FACTORS:
        return {"error": f"不支持的项目：{item}。支持：{', '.join(UNIT_FACTORS)}"}
    factor, si_unit, us_unit, name = UNIT_FACTORS[item]
    if to in ("mgdl", "us"):
        result, unit_from, unit_to = value * factor, si_unit, us_unit
    else:
        result, unit_from, unit_to = value / factor, us_unit, si_unit
    return {
        "项目": name,
        "输入": f"{value} {unit_from}",
        "输出": f"{round(result, 3)} {unit_to}",
        "换算系数": round(factor, 5),
    }


# ============================================================
# eGFR
# ============================================================

def calc_egfr(cr_umol, age, sex):
    """CKD-EPI 2021（无种族系数，推荐）+ 2009 版对照。cr 输入 μmol/L。"""
    cr = cr_umol / 88.4  # 转 mg/dL
    female = sex.lower() in ("f", "female", "女")

    # --- CKD-EPI 2021 ---
    if female:
        kappa, alpha, sex_coef = 0.7, -0.241, 1.012
    else:
        kappa, alpha, sex_coef = 0.9, -0.302, 1.0
    ratio = cr / kappa
    egfr_2021 = (142
                 * (min(ratio, 1) ** alpha)
                 * (max(ratio, 1) ** -1.200)
                 * (0.9938 ** age)
                 * sex_coef)

    # --- CKD-EPI 2009（对照）---
    if female:
        k9, a9, s9 = 0.7, -0.329, 1.018
    else:
        k9, a9, s9 = 0.9, -0.411, 1.0
    r9 = cr / k9
    egfr_2009 = (141
                 * (min(r9, 1) ** a9)
                 * (max(r9, 1) ** -1.209)
                 * (0.993 ** age)
                 * s9)

    egfr = round(egfr_2021, 1)
    if egfr >= 90:
        stage, note = "G1", "eGFR 正常或升高。需结合尿白蛋白（UACR）判断有无肾损伤，单看 eGFR 不能排除 CKD"
        level = "L4"
    elif egfr >= 60:
        stage, note = "G2", "轻度下降。有肾损伤标志（UACR≥30、尿沉渣异常、影像异常）才诊断 CKD"
        level = "L3"
    elif egfr >= 45:
        stage, note = "G3a", "轻至中度下降，需肾内科随访"
        level = "L2"
    elif egfr >= 30:
        stage, note = "G3b", "中至重度下降，需肾内科规律随访，评估贫血/钙磷/PTH"
        level = "L2"
    elif egfr >= 15:
        stage, note = "G4", "重度下降，需准备肾脏替代治疗评估"
        level = "L2"
    else:
        stage, note = "G5", "肾衰竭，需即刻肾内科处置"
        level = "L1"

    return {
        "eGFR (CKD-EPI 2021)": f"{egfr} mL/min/1.73m²",
        "eGFR (CKD-EPI 2009 对照)": f"{round(egfr_2009, 1)} mL/min/1.73m²",
        "CKD 分期": stage,
        "随访档位": level,
        "解读": note,
        "输入": f"肌酐 {cr_umol} μmol/L ({round(cr, 2)} mg/dL), 年龄 {age}, 性别 {'女' if female else '男'}",
        "重要提示": [
            "肌酐受肌肉量影响大：健身人群 eGFR 可被低估，老年/消瘦者可被高估",
            "若与临床不符，建议加做胱抑素 C 计算 eGFR",
            "CKD 诊断需 eGFR 异常或肾损伤标志持续超过 3 个月",
        ],
    }


# ============================================================
# ASCVD · China-PAR
# ============================================================

# 系数来源：《中国心血管病风险评估和管理指南》(2019) / China-PAR 原始研究
CHINA_PAR = {
    "male": {
        "ln_age": 31.97,
        "ln_sbp_treated": 27.39,
        "ln_sbp_untreated": 26.15,
        "ln_tc": 0.62,
        "ln_hdl": -0.69,
        "ln_wc": -0.71,
        "smoker": 3.96,
        "diabetes": 0.36,
        "north": 0.48,
        "urban": -0.16,
        "family": 6.22,
        "ln_age_x_smoker": -0.94,
        "ln_age_x_ln_sbp_treated": -6.02,
        "ln_age_x_ln_sbp_untreated": -5.73,
        "ln_age_x_family": -1.53,
        "mean": 140.68,
        "s10": 0.9707,
    },
    "female": {
        "ln_age": 24.87,
        "ln_sbp_treated": 20.71,
        "ln_sbp_untreated": 19.98,
        "ln_tc": 0.16,
        "ln_hdl": -0.22,
        "ln_wc": 1.48,
        "smoker": 0.49,
        "diabetes": 0.57,
        "north": 0.54,
        "urban": None,
        "family": None,
        "ln_age_x_smoker": None,
        "ln_age_x_ln_sbp_treated": -4.53,
        "ln_age_x_ln_sbp_untreated": -4.36,
        "ln_age_x_family": None,
        "mean": 117.26,
        "s10": 0.9851,
    },
}


def calc_china_par(age, sex, sbp, tc_mmol, hdl_mmol, wc,
                   smoker, diabetes, treated, north, urban, family):
    """China-PAR 10 年 ASCVD 风险。TC/HDL 输入 mmol/L，内部按 1 mmol/L = 38.6 mg/dL 转换。"""
    female = sex.lower() in ("f", "female", "女")
    c = CHINA_PAR["female" if female else "male"]

    tc = tc_mmol * 38.6
    hdl = hdl_mmol * 38.6
    ln_age = math.log(age)

    x = 0.0
    x += c["ln_age"] * ln_age
    x += c["ln_tc"] * math.log(tc)
    x += c["ln_hdl"] * math.log(hdl)
    x += c["ln_wc"] * math.log(wc)

    if treated:
        x += c["ln_sbp_treated"] * math.log(sbp)
        x += c["ln_age_x_ln_sbp_treated"] * ln_age * math.log(sbp)
    else:
        x += c["ln_sbp_untreated"] * math.log(sbp)
        x += c["ln_age_x_ln_sbp_untreated"] * ln_age * math.log(sbp)

    x += c["smoker"] * smoker
    if c["ln_age_x_smoker"] is not None:
        x += c["ln_age_x_smoker"] * ln_age * smoker

    x += c["diabetes"] * diabetes
    x += c["north"] * north

    if c["urban"] is not None:
        x += c["urban"] * urban
    if c["family"] is not None:
        x += c["family"] * family
    if c["ln_age_x_family"] is not None:
        x += c["ln_age_x_family"] * ln_age * family

    y = math.exp(x - c["mean"])
    risk = 1 - (c["s10"] ** y)
    return max(0.0, min(1.0, risk)) * 100


# ============================================================
# ASCVD · ACC/AHA PCE（参考对照）
# ============================================================

PCE = {
    "male": {
        "ln_age": 12.344, "ln_age_sq": 0.0,
        "ln_tc": 11.853, "ln_age_x_ln_tc": -2.664,
        "ln_hdl": -7.990, "ln_age_x_ln_hdl": 1.769,
        "ln_sbp_treated": 1.797, "ln_age_x_ln_sbp_treated": 0.0,
        "ln_sbp_untreated": 1.764, "ln_age_x_ln_sbp_untreated": 0.0,
        "smoker": 7.837, "ln_age_x_smoker": -1.795,
        "diabetes": 0.658,
        "mean": 61.18, "s10": 0.9144,
    },
    "female": {
        "ln_age": -29.799, "ln_age_sq": 4.884,
        "ln_tc": 13.540, "ln_age_x_ln_tc": -3.114,
        "ln_hdl": -13.578, "ln_age_x_ln_hdl": 3.149,
        "ln_sbp_treated": 2.019, "ln_age_x_ln_sbp_treated": 0.0,
        "ln_sbp_untreated": 1.957, "ln_age_x_ln_sbp_untreated": 0.0,
        "smoker": 7.574, "ln_age_x_smoker": -1.665,
        "diabetes": 0.661,
        "mean": -29.18, "s10": 0.9665,
    },
}


def calc_pce(age, sex, sbp, tc_mmol, hdl_mmol, smoker, diabetes, treated):
    """ACC/AHA PCE（白人/其他种族系数）。仅作参考对照，对中国人群倾向高估。"""
    female = sex.lower() in ("f", "female", "女")
    c = PCE["female" if female else "male"]

    tc = tc_mmol * 38.6
    hdl = hdl_mmol * 38.6
    ln_age, ln_tc, ln_hdl, ln_sbp = math.log(age), math.log(tc), math.log(hdl), math.log(sbp)

    x = 0.0
    x += c["ln_age"] * ln_age
    x += c["ln_age_sq"] * (ln_age ** 2)
    x += c["ln_tc"] * ln_tc
    x += c["ln_age_x_ln_tc"] * ln_age * ln_tc
    x += c["ln_hdl"] * ln_hdl
    x += c["ln_age_x_ln_hdl"] * ln_age * ln_hdl

    if treated:
        x += c["ln_sbp_treated"] * ln_sbp
        x += c["ln_age_x_ln_sbp_treated"] * ln_age * ln_sbp
    else:
        x += c["ln_sbp_untreated"] * ln_sbp
        x += c["ln_age_x_ln_sbp_untreated"] * ln_age * ln_sbp

    x += c["smoker"] * smoker
    x += c["ln_age_x_smoker"] * ln_age * smoker
    x += c["diabetes"] * diabetes

    risk = 1 - (c["s10"] ** math.exp(x - c["mean"]))
    return max(0.0, min(1.0, risk)) * 100


def ascvd_report(age, sex, sbp, tc, hdl, wc, smoker, diabetes,
                 treated, north, urban, family):
    par = calc_china_par(age, sex, sbp, tc, hdl, wc, smoker,
                         diabetes, treated, north, urban, family)
    pce = calc_pce(age, sex, sbp, tc, hdl, smoker, diabetes, treated)

    def stratify(r):
        if r < 5:
            return "低危"
        if r < 10:
            return "中危"
        return "高危"

    par_level, pce_level = stratify(par), stratify(pce)

    # LDL-C 目标（《中国血脂管理指南 2023》，按 China-PAR 分层）
    if par_level == "高危":
        ldl_target, nonhdl_target = "< 2.6 mmol/L", "< 3.4 mmol/L"
    elif par_level == "中危":
        ldl_target, nonhdl_target = "< 3.4 mmol/L", "< 4.2 mmol/L"
    else:
        ldl_target, nonhdl_target = "< 3.4 mmol/L", "< 4.2 mmol/L"

    out = {
        "China-PAR 10年风险（主要结论）": f"{round(par, 2)}%",
        "China-PAR 风险分层": par_level,
        "ACC/AHA PCE 10年风险（参考对照）": f"{round(pce, 2)}%",
        "PCE 风险分层": pce_level,
        "LDL-C 目标值": ldl_target,
        "非HDL-C 目标值": nonhdl_target,
        "分层标准": "低危 <5% / 中危 5~10% / 高危 ≥10%（China-PAR）",
        "模型选用说明": (
            "以 China-PAR 为主要结论。China-PAR 原始研究已证实 ACC/AHA PCE "
            "不适用于中国人群，对中国人群倾向高估风险，故 PCE 仅作对照参考。"
        ),
    }

    if par_level != pce_level:
        out["⚠ 两模型分层不一致"] = (
            f"China-PAR 判为{par_level}（{round(par, 2)}%），"
            f"PCE 判为{pce_level}（{round(pce, 2)}%）。"
            f"按 China-PAR 定档为{par_level}。差异主要源于两模型建模人群不同。"
        )

    out["重要限定"] = [
        "本模型适用于 20 岁及以上、无 ASCVD 病史的一级预防人群",
        "已确诊 ASCVD（心梗/卒中/外周动脉疾病）者不适用本模型，直接归极高危，LDL-C 目标 <1.8",
        "有颈动脉斑块等亚临床动脉粥样硬化证据者，危险分层应上调",
        "LDL-C ≥4.9 mmol/L 未治疗者疑家族性高胆固醇血症，直接归超高危，目标 <1.4",
        "10 年风险中低危且年龄 20~59 岁者，建议加做终生风险评估",
    ]
    return out


# ============================================================
# FIB-4
# ============================================================

def calc_fib4(age, ast, alt, plt):
    if alt <= 0 or plt <= 0:
        return {"error": "ALT 与 PLT 必须大于 0"}
    fib4 = (age * ast) / (plt * math.sqrt(alt))
    fib4 = round(fib4, 2)
    if fib4 < 1.30:
        interp, level = "低风险，可基本排除进展性肝纤维化", "L4"
    elif fib4 <= 2.67:
        interp, level = "中间区（灰区），需进一步评估", "L3"
    else:
        interp, level = "高风险，提示可能存在进展性肝纤维化", "L2"
    return {
        "FIB-4": fib4,
        "风险判定": interp,
        "随访档位": level,
        "阈值": "<1.30 低风险 / 1.30~2.67 中间区 / >2.67 高风险",
        "输入": f"年龄 {age}, AST {ast} U/L, ALT {alt} U/L, PLT {plt} ×10⁹/L",
        "后续建议": {
            "L4": "常规随访，结合生活方式管理",
            "L3": "建议肝脏弹性成像（FibroScan）或超声，3~6 月复查",
            "L2": "建议肝病专科评估，行弹性成像/肝脏 MR，必要时肝活检",
        }[level],
        "适用限定": "FIB-4 主要用于 NAFLD/慢性肝炎人群纤维化筛查，35 岁以下与 65 岁以上准确性下降",
    }


# ============================================================
# BMI / 腰高比
# ============================================================

def calc_bmi(height_cm, weight_kg, wc_cm=None, sex=None):
    h = height_cm / 100
    bmi = round(weight_kg / (h * h), 1)
    if bmi < 18.5:
        bmi_cls, bmi_level = "体重不足", "L3"
    elif bmi < 24:
        bmi_cls, bmi_level = "正常", "L4"
    elif bmi < 28:
        bmi_cls, bmi_level = "超重", "L3"
    else:
        bmi_cls, bmi_level = "肥胖", "L3"

    res = {
        "BMI": bmi,
        "BMI 分级（中国标准）": bmi_cls,
        "分级标准": "<18.5 不足 / 18.5~23.9 正常 / 24~27.9 超重 / ≥28 肥胖",
        "随访档位": bmi_level,
    }

    if wc_cm:
        whtr = round(wc_cm / height_cm, 3)
        if whtr < 0.5:
            whtr_cls = "正常"
        elif whtr < 0.55:
            whtr_cls = "腹型肥胖风险增加"
        else:
            whtr_cls = "腹型肥胖"
        res["腰围"] = f"{wc_cm} cm"
        res["腰高比 WHtR"] = whtr
        res["腰高比分级"] = whtr_cls
        res["腰高比标准"] = "<0.5 正常 / 0.5~0.55 风险增加 / ≥0.55 腹型肥胖"

        if sex:
            female = sex.lower() in ("f", "female", "女")
            cut_over, cut_obese = (80, 85) if female else (85, 90)
            if wc_cm < cut_over:
                wc_cls = "正常"
            elif wc_cm < cut_obese:
                wc_cls = "腹型肥胖前期"
            else:
                wc_cls = "腹型肥胖"
            res["腰围分级"] = wc_cls
            res["腰围标准"] = (f"{'女' if female else '男'}性："
                               f"<{cut_over} 正常 / {cut_over}~{cut_obese} 前期 / ≥{cut_obese} 腹型肥胖")

        res["重要提示"] = (
            "腰围/腰高比对心血管事件的预测优于 BMI（China-PAR 模型采用腰围而非 BMI）。"
            "BMI 正常但腰高比 ≥0.5 属「隐性中心性肥胖」，仍需干预。"
        )
    return res


# ============================================================
# AIP / HOMA-IR
# ============================================================

def calc_aip(tg_mmol, hdl_mmol):
    if tg_mmol <= 0 or hdl_mmol <= 0:
        return {"error": "TG 与 HDL-C 必须大于 0"}
    aip = round(math.log10(tg_mmol / hdl_mmol), 3)
    if aip < 0.11:
        risk, level = "低风险", "L4"
    elif aip <= 0.24:
        risk, level = "中等风险", "L3"
    else:
        risk, level = "高风险", "L3"
    return {
        "AIP": aip,
        "致动脉粥样硬化风险": risk,
        "随访档位": level,
        "阈值": "<0.11 低 / 0.11~0.24 中 / >0.24 高",
        "计算式": "AIP = log10(TG / HDL-C)，单位均为 mmol/L",
        "说明": "AIP 反映小而密 LDL 颗粒比例，对残余心血管风险有补充价值，可用于 LDL-C 已达标但仍有风险者",
    }


def calc_homa(glucose_mmol, insulin_uiu):
    if glucose_mmol <= 0 or insulin_uiu <= 0:
        return {"error": "血糖与胰岛素必须大于 0"}
    homa_ir = round(glucose_mmol * insulin_uiu / 22.5, 2)
    homa_beta = round(20 * insulin_uiu / (glucose_mmol - 3.5), 2) if glucose_mmol > 3.5 else None
    if homa_ir < 1.4:
        interp, level = "胰岛素敏感性良好", "L4"
    elif homa_ir < 2.7:
        interp, level = "轻度胰岛素抵抗", "L3"
    else:
        interp, level = "明显胰岛素抵抗", "L3"
    res = {
        "HOMA-IR": homa_ir,
        "判定": interp,
        "随访档位": level,
        "参考阈值": "<1.4 敏感 / 1.4~2.7 轻度抵抗 / >2.7 明显抵抗（各实验室略有差异）",
        "计算式": "HOMA-IR = 空腹血糖(mmol/L) × 空腹胰岛素(μIU/mL) / 22.5",
    }
    if homa_beta:
        res["HOMA-β（胰岛功能）"] = homa_beta
    res["注意"] = "需空腹采血；已用胰岛素治疗者不适用；阈值存在实验室间差异，趋势比绝对值更有价值"
    return res


# ============================================================
# CLI
# ============================================================

def print_result(d):
    if "error" in d:
        print(f"错误：{d['error']}")
        sys.exit(1)
    width = max(len(str(k)) for k in d)
    for k, v in d.items():
        if isinstance(v, list):
            print(f"{str(k):<{width}} :")
            for i in v:
                print(f"{'':<{width}}   - {i}")
        elif isinstance(v, dict):
            print(f"{str(k):<{width}} :")
            for kk, vv in v.items():
                print(f"{'':<{width}}   {kk}: {vv}")
        else:
            print(f"{str(k):<{width}} : {v}")


def main():
    p = argparse.ArgumentParser(
        description="医疗报告深度解读 · 定量风险计算",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("egfr", help="eGFR 与 CKD 分期")
    s.add_argument("--cr", type=float, required=True, help="肌酐 μmol/L")
    s.add_argument("--age", type=float, required=True)
    s.add_argument("--sex", required=True, help="male/female")

    s = sub.add_parser("ascvd", help="10 年 ASCVD 风险（China-PAR + PCE）")
    s.add_argument("--age", type=float, required=True)
    s.add_argument("--sex", required=True, help="male/female")
    s.add_argument("--sbp", type=float, required=True, help="收缩压 mmHg")
    s.add_argument("--tc", type=float, required=True, help="总胆固醇 mmol/L")
    s.add_argument("--hdl", type=float, required=True, help="HDL-C mmol/L")
    s.add_argument("--wc", type=float, required=True, help="腰围 cm")
    s.add_argument("--smoker", type=int, default=0, help="当前吸烟 1/0")
    s.add_argument("--diabetes", type=int, default=0, help="糖尿病 1/0")
    s.add_argument("--treated", type=int, default=0, help="正在服降压药 1/0")
    s.add_argument("--north", type=int, default=0, help="居住北方（长江以北）1/0")
    s.add_argument("--urban", type=int, default=1, help="城市 1 / 农村 0（仅男性模型使用）")
    s.add_argument("--family", type=int, default=0, help="ASCVD 家族史 1/0（仅男性模型使用）")

    s = sub.add_parser("fib4", help="肝纤维化 FIB-4")
    s.add_argument("--age", type=float, required=True)
    s.add_argument("--ast", type=float, required=True, help="AST U/L")
    s.add_argument("--alt", type=float, required=True, help="ALT U/L")
    s.add_argument("--plt", type=float, required=True, help="血小板 ×10⁹/L")

    s = sub.add_parser("bmi", help="BMI 与腰高比")
    s.add_argument("--height", type=float, required=True, help="身高 cm")
    s.add_argument("--weight", type=float, required=True, help="体重 kg")
    s.add_argument("--wc", type=float, help="腰围 cm（可选）")
    s.add_argument("--sex", help="male/female（提供腰围时建议填写）")

    s = sub.add_parser("aip", help="致动脉粥样硬化指数")
    s.add_argument("--tg", type=float, required=True, help="TG mmol/L")
    s.add_argument("--hdl", type=float, required=True, help="HDL-C mmol/L")

    s = sub.add_parser("homa", help="胰岛素抵抗指数")
    s.add_argument("--glucose", type=float, required=True, help="空腹血糖 mmol/L")
    s.add_argument("--insulin", type=float, required=True, help="空腹胰岛素 μIU/mL")

    s = sub.add_parser("unit", help="单位换算")
    s.add_argument("--item", required=True, help=f"项目：{', '.join(UNIT_FACTORS)}")
    s.add_argument("--value", type=float, required=True)
    s.add_argument("--to", default="mgdl", help="mgdl 或 si")

    a = p.parse_args()

    if a.cmd == "egfr":
        r = calc_egfr(a.cr, a.age, a.sex)
    elif a.cmd == "ascvd":
        r = ascvd_report(a.age, a.sex, a.sbp, a.tc, a.hdl, a.wc,
                         a.smoker, a.diabetes, a.treated, a.north, a.urban, a.family)
    elif a.cmd == "fib4":
        r = calc_fib4(a.age, a.ast, a.alt, a.plt)
    elif a.cmd == "bmi":
        r = calc_bmi(a.height, a.weight, a.wc, a.sex)
    elif a.cmd == "aip":
        r = calc_aip(a.tg, a.hdl)
    elif a.cmd == "homa":
        r = calc_homa(a.glucose, a.insulin)
    elif a.cmd == "unit":
        r = convert_unit(a.item, a.value, a.to)
    else:
        p.print_help()
        sys.exit(1)

    print_result(r)
    print("\n" + "-" * 60)
    print("本工具仅做数值计算与风险分层提示，不构成医疗诊断。")


if __name__ == "__main__":
    main()
