#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学论文结构化分析工具
功能：识别研究类型、计算临床指标、生成结构化数据提取模板
"""

import re
import json
from typing import Dict, List


def identify_study_type(text: str) -> Dict:
    """
    根据论文文本识别研究类型
    
    Args:
        text: 论文文本内容
    
    Returns:
        研究类型信息
    """
    text_lower = text.lower()
    
    study_types = [
        {
            "type": "随机对照试验(RCT)",
            "level": "I级",
            "keywords": ["随机对照", "randomized controlled", "rct", "随机分组", "双盲", "安慰剂对照"],
            "weight": 5
        },
        {
            "type": "Meta分析/系统综述",
            "level": "I级",
            "keywords": ["meta分析", "meta-analysis", "系统综述", "systematic review", "荟萃分析", "合并分析"],
            "weight": 5
        },
        {
            "type": "队列研究",
            "level": "II级",
            "keywords": ["队列研究", "cohort study", "前瞻性研究", "retrospective cohort", "随访研究", "纵向研究"],
            "weight": 4
        },
        {
            "type": "病例对照研究",
            "level": "III级",
            "keywords": ["病例对照", "case-control", "回顾性研究", "对照研究", "匹配"],
            "weight": 4
        },
        {
            "type": "横断面研究",
            "level": "IV级",
            "keywords": ["横断面", "cross-sectional", "现况调查", "现患率", "患病率调查"],
            "weight": 3
        },
        {
            "type": "诊断试验研究",
            "level": "-",
            "keywords": ["诊断试验", "diagnostic", "灵敏度", "特异度", "sensitivity", "specificity", "auc", "roc"],
            "weight": 4
        },
        {
            "type": "病例报告/系列",
            "level": "V级",
            "keywords": ["病例报告", "case report", "case series", "个案报告"],
            "weight": 2
        },
    ]
    
    scores = []
    for st in study_types:
        score = 0
        for kw in st["keywords"]:
            if kw in text_lower:
                score += st["weight"]
        if score > 0:
            scores.append({
                "type": st["type"],
                "level": st["level"],
                "score": score
            })
    
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    if not scores:
        return {"type": "未知研究类型", "level": "未知", "confidence": 0, "all_matches": []}
    
    return {
        "type": scores[0]["type"],
        "level": scores[0]["level"],
        "confidence": min(scores[0]["score"] / 20, 1.0),
        "all_matches": scores
    }


def extract_sample_size(text: str) -> Dict:
    """
    提取样本量信息
    
    Args:
        text: 论文文本
    
    Returns:
        样本量信息
    """
    patterns = [
        r'(\d+)\s*例',
        r'n\s*=\s*(\d+)',
        r'(\d+)\s*名患者',
        r'(\d+)\s*名受试者',
        r'纳入\s*(\d+)\s*例',
        r'共\s*(\d+)\s*例',
        r'(\d+)\s*名参与者',
    ]
    
    numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        numbers.extend([int(n) for n in matches])
    
    if not numbers:
        return {"total_sample": "未提取到", "groups": {}, "all_numbers": []}
    
    numbers = sorted(list(set(numbers)), reverse=True)
    
    groups = {}
    group_patterns = [
        r'(试验组|实验组|治疗组|观察组|研究组)[^0-9]*(\d+)\s*例',
        r'(对照组|安慰剂组)[^0-9]*(\d+)\s*例',
        r'(病例组)[^0-9]*(\d+)\s*例',
    ]
    
    for pattern in group_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            groups[match[0]] = int(match[1])
    
    return {
        "total_sample": numbers[0] if numbers else "未提取到",
        "groups": groups,
        "all_numbers": numbers[:10]
    }


def calculate_diagnostic_metrics(sensitivity: float, specificity: float, prevalence: float = 0.1) -> Dict:
    """
    计算诊断试验的各项指标
    
    Args:
        sensitivity: 灵敏度（0-1）
        specificity: 特异度（0-1）
        prevalence: 患病率（默认0.1）
    
    Returns:
        诊断试验指标字典
    """
    youden_index = sensitivity + specificity - 1
    positive_lr = sensitivity / (1 - specificity) if (1 - specificity) > 0 else float('inf')
    negative_lr = (1 - sensitivity) / specificity if specificity > 0 else float('inf')
    ppv = (sensitivity * prevalence) / (sensitivity * prevalence + (1 - specificity) * (1 - prevalence))
    npv = (specificity * (1 - prevalence)) / ((1 - sensitivity) * prevalence + specificity * (1 - prevalence))
    dor = (sensitivity * specificity) / ((1 - sensitivity) * (1 - specificity)) if ((1 - sensitivity) * (1 - specificity)) > 0 else float('inf')
    
    quality = ""
    if youden_index > 0.8:
        quality = "极高准确性"
    elif youden_index > 0.6:
        quality = "较高准确性"
    elif youden_index > 0.4:
        quality = "中等准确性"
    elif youden_index > 0.2:
        quality = "较低准确性"
    else:
        quality = "准确性较低"
    
    if positive_lr > 10:
        plr_interp = "阳性似然比很高，对确诊有重要价值"
    elif positive_lr > 5:
        plr_interp = "阳性似然比较高，对确诊有较好价值"
    elif positive_lr > 2:
        plr_interp = "阳性似然比中等，对确诊有一定价值"
    else:
        plr_interp = "阳性似然比较低，确诊价值有限"
    
    interpretation = f"{quality}；{plr_interp}"
    
    return {
        "sensitivity_pct": round(sensitivity * 100, 2),
        "specificity_pct": round(specificity * 100, 2),
        "youden_index": round(youden_index, 4),
        "positive_likelihood_ratio": round(positive_lr, 2) if positive_lr != float('inf') else "无穷大",
        "negative_likelihood_ratio": round(negative_lr, 4),
        "ppv_pct": round(ppv * 100, 2),
        "npv_pct": round(npv * 100, 2),
        "diagnostic_odds_ratio": round(dor, 2) if dor != float('inf') else "无穷大",
        "prevalence_assumed_pct": prevalence * 100,
        "interpretation": interpretation
    }


def calculate_nnt(risk_treatment: float, risk_control: float) -> Dict:
    """
    计算NNT（需治疗人数）等指标
    
    Args:
        risk_treatment: 治疗组事件发生率
        risk_control: 对照组事件发生率
    
    Returns:
        NNT等指标
    """
    arr = abs(risk_control - risk_treatment)
    rrr = arr / risk_control if risk_control > 0 else 0
    nnt = 1 / arr if arr > 0 else float('inf')
    rr = risk_treatment / risk_control if risk_control > 0 else 0
    benefit = risk_control > risk_treatment
    
    interpretation = ""
    if benefit and nnt != float('inf'):
        interpretation = f"每治疗{round(nnt)}例患者可预防1例不良事件"
    elif not benefit and nnt != float('inf'):
        interpretation = f"治疗有害，每治疗{round(nnt)}例患者增加1例不良事件"
    else:
        interpretation = "两组无显著差异"
    
    return {
        "treatment_risk_pct": round(risk_treatment * 100, 2),
        "control_risk_pct": round(risk_control * 100, 2),
        "arr_pct": round(arr * 100, 2),
        "rrr_pct": round(rrr * 100, 2),
        "nnt": round(nnt, 1) if nnt != float('inf') else "无穷大",
        "rr": round(rr, 3),
        "is_beneficial": benefit,
        "interpretation": interpretation
    }


def assess_meta_heterogeneity(i_squared: float) -> Dict:
    """
    评估Meta分析异质性
    
    Args:
        i_squared: I²值（百分比，0-100）
    
    Returns:
        异质性评估
    """
    if i_squared < 25:
        level = "低异质性"
        suggestion = "可使用固定效应模型"
        concern = "较低"
    elif i_squared < 50:
        level = "中等异质性"
        suggestion = "可考虑固定效应或随机效应模型"
        concern = "中等"
    elif i_squared < 75:
        level = "较高异质性"
        suggestion = "建议使用随机效应模型，需探讨异质性来源"
        concern = "较高"
    else:
        level = "高异质性"
        suggestion = "必须使用随机效应模型，强烈建议亚组分析/敏感性分析"
        concern = "很高"
    
    return {
        "i_squared": i_squared,
        "heterogeneity_level": level,
        "concern_level": concern,
        "suggestion": suggestion
    }


def generate_extraction_template(study_type: str) -> Dict:
    """
    根据研究类型生成数据提取模板
    
    Args:
        study_type: 研究类型
    
    Returns:
        数据提取模板
    """
    templates = {
        "随机对照试验(RCT)": {
            "基本信息": ["题目", "作者", "期刊", "发表年份", "研究中心数"],
            "研究对象": ["纳入标准", "排除标准", "年龄范围", "样本量", "随机化方法", "分配隐藏"],
            "干预措施": ["试验组干预", "对照组干预", "治疗时长", "随访时间"],
            "结局指标": ["主要终点", "次要终点", "安全性指标"],
            "结果数据": ["试验组结果", "对照组结果", "P值", "效应量(OR/RR/MD)", "95%CI"],
            "质量评价": ["随机序列产生", "分配隐藏", "盲法实施", "不完整数据", "选择性报告", "其他偏倚"],
        },
        "Meta分析/系统综述": {
            "基本信息": ["题目", "作者", "期刊", "发表年份", "PROSPERO注册号"],
            "研究方法": ["纳入标准", "排除标准", "检索数据库", "检索时间范围", "文献筛选流程"],
            "纳入研究": ["纳入研究数", "总样本量", "研究类型", "研究质量"],
            "统计方法": ["效应模型", "异质性检验(I²)", "亚组分析", "敏感性分析", "发表偏倚"],
            "主要结果": ["合并效应量", "95%CI", "P值", "异质性", "结论"],
        },
        "诊断试验研究": {
            "基本信息": ["题目", "疾病名称", "金标准", "待评价试验"],
            "研究对象": ["病例组来源", "对照组来源", "样本量", "纳入排除标准"],
            "诊断指标": ["灵敏度", "特异度", "阳性预测值", "阴性预测值", "AUC", "约登指数"],
            "结果数据": ["真阳性", "假阳性", "真阴性", "假阴性", "似然比"],
        },
        "队列研究": {
            "基本信息": ["题目", "暴露因素", "研究类型（前瞻性/回顾性）"],
            "研究对象": ["暴露组", "非暴露组", "样本量", "随访时间", "失访率"],
            "结局指标": ["主要结局", "次要结局", "混杂因素控制方法"],
            "结果数据": ["暴露组发病率", "非暴露组发病率", "RR", "95%CI", "P值", "HR"],
        },
    }
    
    return templates.get(study_type, {"通用信息": ["题目", "作者", "目的", "方法", "结果", "结论"]})


def grade_evidence_quality(study_type: str, sample_size: int, limitations: List[str] = None) -> Dict:
    """
    简化的GRADE证据质量评估
    
    Args:
        study_type: 研究类型
        sample_size: 样本量
        limitations: 局限性列表
    
    Returns:
        证据质量评级
    """
    # 初始等级
    if study_type in ["随机对照试验(RCT)", "Meta分析/系统综述"]:
        base_grade = "高"
        base_score = 4
    elif study_type == "队列研究":
        base_grade = "中"
        base_score = 3
    elif study_type == "病例对照研究":
        base_grade = "低"
        base_score = 2
    else:
        base_grade = "极低"
        base_score = 1
    
    # 样本量降级因素
    if sample_size < 100:
        base_score -= 1
    elif sample_size < 50:
        base_score -= 2
    
    # 局限性降级
    if limitations:
        base_score -= min(len(limitations), 2)
    
    base_score = max(1, min(4, base_score))
    
    grade_map = {4: "高", 3: "中", 2: "低", 1: "极低"}
    grade = grade_map.get(base_score, "低")
    
    return {
        "study_type": study_type,
        "sample_size": sample_size,
        "evidence_grade": grade,
        "score": base_score,
        "explanation": f"{study_type}初始等级为{grade_map.get(base_score + min(len(limitations or []), 2), '低')}，"
                       f"样本量{sample_size}，局限性{len(limitations or [])}项，最终评级{grade}级"
    }


# ===== 示例运行 =====
if __name__ == "__main__":
    # 测试：研究类型识别
    test_text = """
    本研究为一项多中心、随机、双盲、安慰剂对照试验，
    纳入420例中重度溃疡性结肠炎患者，1:1随机分组，
    试验组210例接受XX单抗治疗，对照组210例接受安慰剂，
    主要终点为第8周临床缓解率。结果显示，试验组缓解率38.6%，
    对照组12.4%，差异有统计学意义（P<0.001）。
    """
    
    print("=" * 50)
    print("研究类型识别测试")
    print("=" * 50)
    study_type = identify_study_type(test_text)
    print(json.dumps(study_type, ensure_ascii=False, indent=2))
    
    # 测试：样本量提取
    print()
    print("=" * 50)
    print("样本量提取测试")
    print("=" * 50)
    sample_size = extract_sample_size(test_text)
    print(json.dumps(sample_size, ensure_ascii=False, indent=2))
    
    # 测试：诊断试验计算
    print()
    print("=" * 50)
    print("诊断试验指标计算示例")
    print("=" * 50)
    diag_result = calculate_diagnostic_metrics(0.78, 0.85, 0.05)
    print(json.dumps(diag_result, ensure_ascii=False, indent=2))
    
    # 测试：NNT计算
    print()
    print("=" * 50)
    print("NNT计算示例")
    print("=" * 50)
    nnt_result = calculate_nnt(0.386, 0.124)
    print(json.dumps(nnt_result, ensure_ascii=False, indent=2))
    
    # 测试：异质性评估
    print()
    print("=" * 50)
    print("Meta分析异质性评估示例")
    print("=" * 50)
    het_result = assess_meta_heterogeneity(56)
    print(json.dumps(het_result, ensure_ascii=False, indent=2))
    
    # 测试：证据质量评级
    print()
    print("=" * 50)
    print("GRADE证据质量评估示例")
    print("=" * 50)
    grade_result = grade_evidence_quality("随机对照试验(RCT)", 420, ["随访时间短", "亚组分析不足"])
    print(json.dumps(grade_result, ensure_ascii=False, indent=2))
    
    # 测试：生成提取模板
    print()
    print("=" * 50)
    print("RCT数据提取模板（部分）")
    print("=" * 50)
    template = generate_extraction_template("随机对照试验(RCT)")
    for section, fields in list(template.items())[:3]:
        print(f"\n【{section}】")
        for f in fields:
            print(f"  - {f}: ______")
