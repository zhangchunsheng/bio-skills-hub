"""多轮对话记忆测试（v2.0.0）— 6 个用例。"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class _DirIsolation:
    def __enter__(self):
        import _common
        self.original = {k: getattr(_common, k) for k in
                         ("DATA_DIR", "MANAGERS_DIR", "PROGRESS_DIR", "EXPORTS_DIR", "ROSTER_PATH")}
        self.tmp = tempfile.mkdtemp()
        _common.DATA_DIR = os.path.join(self.tmp, "data")
        _common.MANAGERS_DIR = os.path.join(_common.DATA_DIR, "managers")
        _common.PROGRESS_DIR = os.path.join(_common.DATA_DIR, "progress")
        _common.EXPORTS_DIR = os.path.join(_common.DATA_DIR, "exports")
        _common.ROSTER_PATH = os.path.join(_common.DATA_DIR, "roster.json")
        for p in (_common.MANAGERS_DIR, _common.PROGRESS_DIR, _common.EXPORTS_DIR):
            os.makedirs(p, exist_ok=True)
        return self

    def __exit__(self, *args):
        import _common
        for k, v in self.original.items():
            setattr(_common, k, v)
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


def test_tokens_chinese_bigram():
    """中文 2-gram 分词。"""
    import qa_memory as qm
    toks = qm._tokens("我看好消费板块")
    assert "看好" in toks
    assert "好消" in toks
    assert "消费" in toks


def test_jaccard_basic():
    """Jaccard 相似度基本公式。"""
    import qa_memory as qm
    a = {"a", "b", "c"}
    b = {"b", "c", "d"}
    assert qm._jaccard(a, b) == 0.5  # 交集2 / 并集4


def test_record_qa_appends_to_jsonl():
    """record_qa 应追加一行到 JSONL。"""
    import qa_memory as qm

    captured = {}
    with _DirIsolation():
        qm.record_qa("m1", "你怎么看消费板块？", "我看好高端白酒", "消费")
        import _common
        path = os.path.join(_common.DATA_DIR, "qa_history", "m1.jsonl")
        captured["lines"] = open(path, "r", encoding="utf-8").readlines()
    lines = captured["lines"]
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["question"] == "你怎么看消费板块？"
    assert entry["topic"] == "消费"


def test_search_similar_finds_relevant_history():
    """search_similar 应按 Jaccard 排序返回 top-k。"""
    import qa_memory as qm

    with _DirIsolation():
        qm.record_qa("m1", "你怎么看消费板块？", "看好白酒", "消费")
        qm.record_qa("m1", "科技股怎么看？", "谨慎", "科技")
        qm.record_qa("m1", "消费板块什么时候建仓？", "现在就可以", "消费")
        results = qm.search_similar("m1", "消费板块现在能买吗？", top_k=2)
    # 两个结果都是消费相关
    assert len(results) == 2
    topics = [r["topic"] for r in results]
    assert topics == ["消费", "消费"]


def test_summarize_groups_by_topic():
    """summarize 应按 topic 分组计数。"""
    import qa_memory as qm

    with _DirIsolation():
        qm.record_qa("m1", "白酒怎么看", "a1", "消费")
        qm.record_qa("m1", "消费配置思路", "a2", "消费")
        qm.record_qa("m1", "半导体怎么看", "a3", "科技")
        summary = qm.summarize("m1")
    topics = {s["topic"]: s["count"] for s in summary}
    assert topics["消费"] == 2
    assert topics["科技"] == 1


def test_get_context_for_prompt_returns_related_qa():
    """get_context_for_prompt 应返回相关历史问答文本。"""
    import qa_memory as qm

    with _DirIsolation():
        qm.record_qa("m1", "消费板块怎么看？", "看好白酒", "消费")
        qm.record_qa("m1", "科技股呢？", "谨慎", "科技")
        ctx = qm.get_context_for_prompt("m1", "消费板块什么时候加仓？")
    assert "历史问答参考" in ctx
    assert "看好白酒" in ctx