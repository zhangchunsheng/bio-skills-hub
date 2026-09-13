"""
基金经理言论风格指纹（v2.0.0 新增）。

借鉴 wechat-analyzer.text_analyzer._analyze_big_five：用关键词字典 + 计数 +
比例计算多维评分，零 LLM 依赖。

用法：
    from speech_fingerprint import build_fingerprint, save_fingerprint
    fp = build_fingerprint(manager_id)
    save_fingerprint(manager_id, fp)
"""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from typing import Dict, List

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import _common
from _common import load_manager, save_manager, log


# ============================================================
# 关键词字典（参考 wechat-analyzer big_five 风格）
# ============================================================

# 第一人称密度（"我""我的""我认为"等）
FIRST_PERSON = {"我", "我的", "我认为", "我觉得", "我相信", "我们", "我们的", "我关注", "我看好"}

# 数据驱动（财务/估值/定量术语）
DATA_DRIVEN = {
    "ROE", "ROA", "PE", "PB", "EPS", "估值", "现金流", "盈利", "营收", "利润",
    "增速", "毛利率", "净利率", "分红", "股息", "收益率", "波动率", "夏普", "回撤",
    "市值", "规模", "成长性", "行业", "板块", "仓位", "占比", "基准", "指数",
}

# 直觉判断（定性/主观表达）
INTUITIVE = {
    "看好", "看空", "看多", "看好", "觉得", "相信", "判断", "认为", "预期",
    "故事", "逻辑", "常识", "直觉", "感受", "判断", "心动", "怀疑",
}

# 确定性表达（不留余地）
CERTAINTY = {"必然", "一定", "必定", "肯定", "毫无疑问", "坚信", "始终", "永远", "绝对"}

# 留余地表达（模糊/谨慎）
HEDGING = {"可能", "或许", "也许", "大概", "关注", "留意", "观察", "谨慎", "灵活", "视情况", "取决于"}


def _count_keywords(text: str, keywords: set) -> int:
    """统计关键词在文本中出现次数（不区分大小写）。"""
    if not text:
        return 0
    total = 0
    text_lower = text.lower()
    for kw in keywords:
        # 统一用子串匹配（避免 \b 在中文上下文失效）
        total += text_lower.count(kw.lower())
    return total


def _avg_sentence_len(text: str) -> float:
    """平均句长（句号/问号/感叹号切分）。"""
    if not text:
        return 0.0
    # 中文标点 + 英文标点
    sentences = re.split(r"[。！？!?\.]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 0.0
    avg = sum(len(s) for s in sentences) / len(sentences)
    return round(avg, 1)


def _first_person_density(text: str) -> float:
    """第一人称密度（第一人称关键词数 / 总字数）。"""
    if not text:
        return 0.0
    fp_count = sum(text.count(kw) for kw in FIRST_PERSON)
    return round(fp_count / max(len(text), 1), 4)


def _data_vs_intuition(text: str) -> float:
    """
    数据驱动 vs 直觉判断倾向（0-1）。
    0=完全直觉，1=完全数据驱动。0.5=中性。
    """
    data_count = _count_keywords(text, DATA_DRIVEN)
    int_count = _count_keywords(text, INTUITIVE)
    total = data_count + int_count
    if total == 0:
        return 0.5
    return round(data_count / total, 3)


def _certainty_score(text: str) -> float:
    """
    确定性 vs 留余地倾向（0-1）。
    0=完全留余地，1=完全确定。0.5=中性。
    """
    cert_count = _count_keywords(text, CERTAINTY)
    hedge_count = _count_keywords(text, HEDGING)
    total = cert_count + hedge_count
    if total == 0:
        return 0.5
    return round(cert_count / total, 3)


def _extract_sample_quotes(text: str, max_quotes: int = 3) -> List[str]:
    """提取样本金句（最长 3 个完整句子，去重）。"""
    if not text:
        return []
    sentences = re.split(r"[。！？!?\.]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) >= 12]
    sentences = list(dict.fromkeys(sentences))  # 去重保持顺序
    return sentences[:max_quotes]


def _classify_dominant_style(data_score: float, cert_score: float) -> str:
    """根据数据驱动+确定性两个维度，归纳经理主导风格。"""
    parts = []
    if data_score >= 0.65:
        parts.append("数据驱动")
    elif data_score <= 0.35:
        parts.append("直觉判断")
    else:
        parts.append("数据+直觉平衡")

    if cert_score >= 0.65:
        parts.append("观点坚定")
    elif cert_score <= 0.35:
        parts.append("留有余地")
    else:
        parts.append("态度中性")

    return "+".join(parts) if parts else "风格未明"


def build_fingerprint(manager_id: str) -> Dict:
    """
    构建经理言论风格指纹。

    输入：从 managers/{id}.json 读 strategy_texts / viewpoint_human / bio
    输出：6 维指纹 dict（avg_sentence_len / first_person_density /
          data_driven_score / certainty_score / dominant_style / sample_quotes）
    """
    mgr = load_manager(manager_id)
    if not mgr:
        return {"error": f"经理档案 {manager_id} 不存在"}

    # 拼接所有可用文本（strategy_texts 是 list[str]，bio/viewpoint 是单条）
    parts: List[str] = []
    for s in mgr.get("strategy_texts", []) or []:
        if s and s != "暂无数据":
            parts.append(s)
    if mgr.get("viewpoint_human"):
        parts.append(mgr["viewpoint_human"])
    if mgr.get("bio"):
        parts.append(mgr["bio"])

    text = "\n".join(parts).strip()
    if not text:
        return {
            "manager_id": manager_id,
            "name": mgr.get("name", ""),
            "computed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "avg_sentence_len": 0.0,
            "first_person_density": 0.0,
            "data_driven_score": 0.5,
            "certainty_score": 0.5,
            "dominant_style": "无文本可分析",
            "sample_quotes": [],
            "note": "无策略文本/观点/bio，跳过指纹构建",
        }

    fp = {
        "manager_id": manager_id,
        "name": mgr.get("name", ""),
        "computed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "avg_sentence_len": _avg_sentence_len(text),
        "first_person_density": _first_person_density(text),
        "data_driven_score": _data_vs_intuition(text),
        "certainty_score": _certainty_score(text),
        "dominant_style": "",
        "sample_quotes": _extract_sample_quotes(text),
        "text_chars": len(text),
    }
    fp["dominant_style"] = _classify_dominant_style(fp["data_driven_score"], fp["certainty_score"])
    return fp


def save_fingerprint(manager_id: str, fp: Dict) -> None:
    """把指纹写回 managers/{id}.json 的 speech_fingerprint 字段。"""
    mgr = load_manager(manager_id) or {"id": manager_id}
    mgr["speech_fingerprint"] = fp
    save_manager(manager_id, mgr)
    log.info(f"经理 {manager_id} 言论指纹已写入档案")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="基金经理言论风格指纹")
    parser.add_argument("manager_id", help="经理ID（如 30189744）")
    parser.add_argument("--save", action="store_true", help="写入 manager.json")
    args = parser.parse_args()

    fp = build_fingerprint(args.manager_id)
    if fp.get("error"):
        print(fp["error"])
        sys.exit(1)

    print(f"📝 {fp.get('name', args.manager_id)} 言论风格指纹")
    print("=" * 50)
    print(f"  平均句长：{fp['avg_sentence_len']} 字")
    print(f"  第一人称密度：{fp['first_person_density']:.4f}")
    print(f"  数据驱动倾向：{fp['data_driven_score']:.3f} (0=直觉, 1=数据)")
    print(f"  确定性倾向：{fp['certainty_score']:.3f} (0=留余地, 1=坚定)")
    print(f"  主导风格：{fp['dominant_style']}")
    if fp.get("sample_quotes"):
        print("\n  样本金句：")
        for q in fp["sample_quotes"]:
            print(f"    - {q}")

    if args.save:
        save_fingerprint(args.manager_id, fp)
        print(f"\n✅ 已写入 managers/{args.manager_id}.json")