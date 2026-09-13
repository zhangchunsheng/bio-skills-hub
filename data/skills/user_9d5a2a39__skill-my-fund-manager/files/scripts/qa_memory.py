"""
基金经理多轮对话记忆（v2.0.0 新增）。

每次"经理问答"自动记录到 data/qa_history/{id}.jsonl，
下次提问时检索相关历史，避免重复回答。

用法：
    from qa_memory import record_qa, search_similar, get_context_for_prompt
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


def _qa_dir() -> str:
    """动态计算 JSONL 目录（避免 import 时绑定旧 DATA_DIR）。"""
    return os.path.join(_common.DATA_DIR, "qa_history")


def _ensure_dir() -> None:
    os.makedirs(_qa_dir(), exist_ok=True)


def _path(manager_id: str) -> str:
    return os.path.join(_qa_dir(), f"{manager_id}.jsonl")


def _tokens(text: str) -> set:
    """中文 2-gram + 英文 word，简单分词。"""
    if not text:
        return set()
    tokens = set()
    # 中文 2-gram
    text_clean = re.sub(r"[^一-龥A-Za-z0-9]", " ", text)
    for word in text_clean.split():
        if re.match(r"^[A-Za-z0-9]+$", word):
            tokens.add(word.lower())
        else:
            for i in range(len(word) - 1):
                tokens.add(word[i:i + 2])
    return tokens


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _similarity(a: set, b: set) -> float:
    """混合相似度 = 0.6×Jaccard + 0.4×包含度。
    v2.1 升级：纯 Jaccard 对"后缀追加/重述"型相似问题不敏感，
    包含度（交集/较小集）能捕捉短问题被长问题包含的场景。"""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    jaccard = inter / len(a | b)
    containment = inter / min(len(a), len(b))
    return 0.6 * jaccard + 0.4 * containment


def record_qa(
    manager_id: str,
    question: str,
    answer: str,
    topic: str = "",
) -> Dict:
    """追加一条问答记录。"""
    _ensure_dir()
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "question": question[:500],
        "answer": answer[:1000],
        "topic": topic or _guess_topic(question),
    }
    path = _path(manager_id)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log.info(f"经理 {manager_id} 问答已记录：topic={entry['topic']}")
    return entry


def _guess_topic(text: str) -> str:
    """简单猜测主题（板块/问题类型）。"""
    topics = {
        "消费": ["消费", "白酒", "茅台", "食品"],
        "科技": ["科技", "半导体", "AI", "互联网"],
        "医药": ["医药", "医疗", "创新药"],
        "金融": ["金融", "银行", "保险"],
        "新能源": ["新能源", "锂电", "光伏"],
        "港股": ["港股", "港股通"],
        "宏观": ["宏观", "利率", "汇率"],
        "风格": ["风格", "持仓", "仓位", "调仓"],
        "业绩": ["业绩", "收益", "回撤", "夏普"],
    }
    for label, kws in topics.items():
        if any(kw in text for kw in kws):
            return label
    return "其他"


def _read_all(manager_id: str) -> List[Dict]:
    path = _path(manager_id)
    if not os.path.exists(path):
        return []
    entries = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except (OSError, UnicodeDecodeError):
        return []
    return entries


def search_similar(manager_id: str, question: str, top_k: int = 3) -> List[Dict]:
    """检索与当前问题最相关的历史问答（Jaccard×包含度混合相似度）。"""
    all_entries = _read_all(manager_id)
    if not all_entries:
        return []
    q_tokens = _tokens(question)
    scored = []
    for e in all_entries:
        score = _similarity(q_tokens, _tokens(e.get("question", "")))
        if score > 0:
            scored.append((score, e))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:top_k]]


def summarize(manager_id: str, since_date: str = "") -> List[Dict]:
    """汇总某段时间的问答（按 topic 分组）。"""
    entries = _read_all(manager_id)
    if since_date:
        entries = [e for e in entries if e.get("ts", "") >= since_date]
    by_topic: Dict[str, List[Dict]] = {}
    for e in entries:
        topic = e.get("topic", "其他")
        by_topic.setdefault(topic, []).append(e)
    summary = []
    for topic, items in by_topic.items():
        summary.append({
            "topic": topic,
            "count": len(items),
            "first_ts": min(e["ts"] for e in items),
            "last_ts": max(e["ts"] for e in items),
            "sample_question": items[-1].get("question", "")[:80],
        })
    summary.sort(key=lambda x: -x["count"])
    return summary


def get_context_for_prompt(manager_id: str, question: str, top_k: int = 2) -> str:
    """给 distill_manager 提供历史上下文，避免重复回答。"""
    similar = search_similar(manager_id, question, top_k)
    if not similar:
        return ""
    lines = ["\n[历史问答参考]"]
    for i, e in enumerate(similar, 1):
        lines.append(f"  {i}. Q: {e.get('question','')[:100]}")
        lines.append(f"     A: {e.get('answer','')[:200]}")
    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="经理多轮对话记忆")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_rec = sub.add_parser("record", help="追加一条问答")
    p_rec.add_argument("manager_id")
    p_rec.add_argument("--question", required=True)
    p_rec.add_argument("--answer", required=True)
    p_rec.add_argument("--topic", default="")

    p_search = sub.add_parser("search", help="检索相关历史问答")
    p_search.add_argument("manager_id")
    p_search.add_argument("--question", required=True)
    p_search.add_argument("--top-k", type=int, default=3)

    p_sum = sub.add_parser("summarize", help="按主题汇总")
    p_sum.add_argument("manager_id")
    p_sum.add_argument("--since", default="")

    args = parser.parse_args()

    if args.cmd == "record":
        e = record_qa(args.manager_id, args.question, args.answer, args.topic)
        print(f"✅ 记录：topic={e['topic']}")
    elif args.cmd == "search":
        for e in search_similar(args.manager_id, args.question, args.top_k):
            print(f"  [{e['ts']}] Q: {e['question'][:80]}")
    elif args.cmd == "summarize":
        for s in summarize(args.manager_id, args.since):
            print(f"  {s['topic']:　<8} ×{s['count']}  最近: {s['last_ts']}")