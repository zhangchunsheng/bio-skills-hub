"""言论风格指纹测试（v2.0.0）— 8 个用例。"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class _DirIsolation:
    """复用 test_bug_fixes.py 的 _DirIsolation（同步拷贝以避免测试间依赖）。"""
    def __enter__(self):
        import _common
        self.original = {
            k: getattr(_common, k) for k in
            ("DATA_DIR", "MANAGERS_DIR", "PROGRESS_DIR", "EXPORTS_DIR", "ROSTER_PATH")
        }
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


# ============================================================
# 关键词计数 + 分类核心算法
# ============================================================

def test_count_keywords_chinese_substring():
    """中文字幕串匹配（无词边界）。"""
    import speech_fingerprint as sf
    text = "我看好ROE指标，我认为ROE高代表质量好"
    n = sf._count_keywords(text, {"我", "ROE"})
    assert n == 4  # 我 ×2 + ROE ×2


def test_count_keywords_english_word_boundary():
    """英文按词边界匹配。"""
    import speech_fingerprint as sf
    text = "ROE is good. The ROE is high. ROSE is different."
    n = sf._count_keywords(text, {"ROE"})
    assert n == 2  # ROSE 不算


def test_avg_sentence_len_basic():
    """平均句长（句号切分）。"""
    import speech_fingerprint as sf
    text = "我看好消费板块。配置以白酒为主。仓位适度集中。"
    avg = sf._avg_sentence_len(text)
    # 三个句子，长度 8/7/6 -> 平均 7.0
    assert 6 < avg < 8


def test_data_vs_intuition_extreme_data():
    """全数据驱动→1.0。"""
    import speech_fingerprint as sf
    text = "ROE 高 估值 低 PE 合理 现金流 充裕 盈利 增速 稳定"
    score = sf._data_vs_intuition(text)
    assert score >= 0.9


def test_data_vs_intuition_extreme_intuition():
    """全直觉→0.0。"""
    import speech_fingerprint as sf
    text = "看好 觉得 相信 故事 心动 怀疑"
    score = sf._data_vs_intuition(text)
    assert score <= 0.1


def test_classify_dominant_style_combinations():
    """主导风格归纳。"""
    import speech_fingerprint as sf
    assert sf._classify_dominant_style(0.8, 0.8) == "数据驱动+观点坚定"
    assert sf._classify_dominant_style(0.2, 0.2) == "直觉判断+留有余地"
    assert sf._classify_dominant_style(0.5, 0.5) == "数据+直觉平衡+态度中性"


# ============================================================
# build_fingerprint + save_fingerprint 集成
# ============================================================

def test_build_fingerprint_with_empty_text():
    """空文本应返回占位 dict 不崩溃。"""
    import speech_fingerprint as sf

    with _DirIsolation():
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试", "company": "X",
            "strategy_texts": [], "viewpoint_human": "", "bio": "",
        })
        fp = sf.build_fingerprint("m1")
    assert fp["avg_sentence_len"] == 0.0
    assert "无文本" in fp["dominant_style"]


def test_save_fingerprint_writes_to_manager():
    """save_fingerprint 应写到 managers/{id}.json 的 speech_fingerprint 字段。"""
    import speech_fingerprint as sf

    with _DirIsolation():
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试", "company": "X",
            "strategy_texts": ["我看好消费板块。ROE 较高。"],
        })
        fp = sf.build_fingerprint("m1")
        sf.save_fingerprint("m1", fp)
        saved = _common.load_manager("m1")
    assert "speech_fingerprint" in saved
    assert saved["speech_fingerprint"]["manager_id"] == "m1"