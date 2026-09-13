"""
基金经理观点时序追踪（v2.0.0 新增）。

每次 smart_update 自动追加一行到 data/viewpoints_history/{id}.jsonl，
记录该期 viewpoint_human + sentiment + stance，支持立场漂移检测。

用法：
    from viewpoint_tracker import record_viewpoint, get_history, detect_drift, render_timeline
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import _common
from _common import log


def _viewpoints_dir() -> str:
    """动态计算 JSONL 目录（避免 import 时绑定旧 DATA_DIR）。"""
    return os.path.join(_common.DATA_DIR, "viewpoints_history")


# ============================================================
# 情感+立场关键词字典
# ============================================================

POSITIVE = {
    "看好", "看多", "机会", "增长", "提升", "改善", "受益", "优势", "强劲",
    "稳定", "复苏", "拐点", "向上", "增持", "超配", "推荐",
}

NEGATIVE = {
    "看空", "谨慎", "风险", "下行", "回落", "下滑", "承压", "恶化", "亏损",
    "减仓", "低配", "回避", "不确定性", "挑战", "压力",
}

SECTOR_BULLISH = {
    "消费": "看多消费", "科技": "看多科技", "医药": "看多医药", "金融": "看多金融",
    "新能源": "看多新能源", "半导体": "看多半导体", "制造": "看多制造",
    "港股": "看多港股", "海外": "看多海外",
}

SECTOR_BEARISH = {
    "消费": "谨慎消费", "科技": "谨慎科技", "医药": "谨慎医药", "金融": "谨慎金融",
    "新能源": "谨慎新能源", "港股": "谨慎港股",
}


def _ensure_dir() -> None:
    os.makedirs(_viewpoints_dir(), exist_ok=True)


def _path(manager_id: str) -> str:
    return os.path.join(_viewpoints_dir(), f"{manager_id}.jsonl")


def _score_sentiment(text: str) -> float:
    """
    算 sentiment_score (-1 ~ +1)。
    +1=极乐观，0=中性，-1=极悲观。
    """
    if not text:
        return 0.0
    pos = sum(text.count(kw) for kw in POSITIVE)
    neg = sum(text.count(kw) for kw in NEGATIVE)
    total = pos + neg
    if total == 0:
        return 0.0
    score = (pos - neg) / total
    # 归一化到 [-1, 1]（保守起见，因为 pos+neg 通常较大）
    return round(max(-1.0, min(1.0, score)), 3)


def _detect_stance(text: str) -> str:
    """
    立场分类。看板块 vs 谨慎板块的优先级最高，其次是总体多空。
    """
    if not text:
        return "中性"
    # 先看是否有具体板块表态
    for sector, label in SECTOR_BULLISH.items():
        if sector in text and ("看好" in text or "机会" in text or "增持" in text or "超配" in text):
            return label
    for sector, label in SECTOR_BEARISH.items():
        if sector in text and ("谨慎" in text or "回避" in text or "减仓" in text or "风险" in text):
            return label
    # 总览
    pos = sum(text.count(kw) for kw in POSITIVE)
    neg = sum(text.count(kw) for kw in NEGATIVE)
    if pos > neg * 1.3:
        return "整体看多"
    if neg > pos * 1.3:
        return "整体谨慎"
    return "中性"


def _detect_key_changes(text: str) -> List[str]:
    """简单提取关键变化（新增加/退出/调整等动作）。"""
    changes = []
    if not text:
        return changes
    patterns = [
        (r"(新增|加仓|增持|买入)[一-龥A-Za-z]{0,8}", "新增/加仓"),
        (r"(退出|清仓|减仓|减持|卖出)[一-龥A-Za-z]{0,8}", "退出/减仓"),
        (r"(调整|切换|转向|转向到|转向于)[一-龥A-Za-z]{0,12}", "结构调整"),
    ]
    for pat, label in patterns:
        matches = re.findall(pat, text)
        if matches:
            # 去重
            unique = list(dict.fromkeys(matches))[:2]
            for m in unique:
                changes.append(f"{label}：{m}")
    return changes[:3]


def record_viewpoint(
    manager_id: str,
    date: str,
    viewpoint_text: str,
    report_type: str = "季报",
) -> Dict:
    """
    追加一期观点到 JSONL。

    参数：
        manager_id: 经理ID
        date: 报告期日期（YYYY-MM-DD）
        viewpoint_text: 观点正文（通常是 viewpoint_human 或季报摘要）
        report_type: 报告类型（季报/中报/年报/临时）

    返回：写入的 dict
    """
    _ensure_dir()
    entry = {
        "date": date,
        "report_type": report_type,
        "viewpoint_human": viewpoint_text[:300] if viewpoint_text else "",
        "sentiment_score": _score_sentiment(viewpoint_text),
        "stance": _detect_stance(viewpoint_text),
        "key_changes": _detect_key_changes(viewpoint_text),
        "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    path = _path(manager_id)
    line = json.dumps(entry, ensure_ascii=False)
    # 追加写（不读旧文件，避免锁问题）
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    log.info(f"经理 {manager_id} 观点已记录：{date} stance={entry['stance']}")
    return entry


def get_history(manager_id: str, limit: int = 8) -> List[Dict]:
    """读最近 N 期观点。"""
    path = _path(manager_id)
    if not os.path.exists(path):
        return []
    lines = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []
    # 倒序取最近 N 期，再正序返回
    recent = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        recent.append(entry)
        if len(recent) >= limit:
            break
    return list(reversed(recent))


def detect_drift(manager_id: str, threshold: float = 0.5) -> Optional[Dict]:
    """
    立场漂移检测。对比最近 2 期。

    返回：
        None 表示无漂移或历史不足
        Dict 含 drift_type / magnitude / details
    """
    history = get_history(manager_id, limit=2)
    if len(history) < 2:
        return None
    latest, previous = history[-1], history[-2]
    sent_delta = abs(latest["sentiment_score"] - previous["sentiment_score"])
    stance_changed = latest["stance"] != previous["stance"]

    if sent_delta >= threshold or stance_changed:
        return {
            "manager_id": manager_id,
            "drift_detected": True,
            "from_date": previous["date"],
            "to_date": latest["date"],
            "sentiment_delta": round(latest["sentiment_score"] - previous["sentiment_score"], 3),
            "stance_from": previous["stance"],
            "stance_to": latest["stance"],
            "stance_changed": stance_changed,
            "magnitude": "high" if sent_delta >= threshold * 1.5 else "medium",
            "details": f"立场从「{previous['stance']}」转向「{latest['stance']}」",
        }
    return None


def render_timeline(manager_id: str, limit: int = 8) -> str:
    """生成时间线文本。"""
    history = get_history(manager_id, limit=limit)
    if not history:
        return "（无观点历史）"
    lines = [f"📜 {manager_id} 观点时间线（最近 {len(history)} 期）："]
    for h in history:
        arrow = "→"
        score = h.get("sentiment_score", 0)
        bar = "▓" * int(abs(score) * 5)
        sign = "+" if score >= 0 else "-"
        snippet = h.get("viewpoint_human", "")
        # v2.1 修复：仅在真正截断时加省略号
        snippet = snippet[:50] + "..." if len(snippet) > 50 else snippet
        lines.append(
            f"  {h['date']} {arrow} {h['stance']:　<8} [{sign}{bar:<5}] {snippet}"
        )
    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="基金经理观点时序追踪")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_record = sub.add_parser("record", help="追加一期观点")
    p_record.add_argument("manager_id")
    p_record.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    p_record.add_argument("--text", required=True)
    p_record.add_argument("--type", default="季报")

    p_history = sub.add_parser("history", help="查看历史")
    p_history.add_argument("manager_id")
    p_history.add_argument("--limit", type=int, default=8)

    p_drift = sub.add_parser("drift", help="立场漂移检测")
    p_drift.add_argument("manager_id")

    p_timeline = sub.add_parser("timeline", help="渲染时间线")
    p_timeline.add_argument("manager_id")
    p_timeline.add_argument("--limit", type=int, default=8)

    args = parser.parse_args()

    if args.cmd == "record":
        entry = record_viewpoint(args.manager_id, args.date, args.text, args.type)
        print(f"✅ 已记录：{entry['stance']} | sentiment={entry['sentiment_score']}")
    elif args.cmd == "history":
        for h in get_history(args.manager_id, args.limit):
            print(f"  {h['date']} {h['stance']:　<8} [{h['sentiment_score']:+.2f}] {h['viewpoint_human'][:60]}")
    elif args.cmd == "drift":
        d = detect_drift(args.manager_id)
        if d:
            print(f"⚠️  漂移检测：{d['details']}（幅度={d['magnitude']}）")
        else:
            print("✅ 无显著立场漂移")
    elif args.cmd == "timeline":
        print(render_timeline(args.manager_id, args.limit))