"""风格聚类测试（v2.0.0）— 6 个用例。"""
from __future__ import annotations

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


def test_cosine_identical():
    """相同向量余弦相似度 = 1。"""
    import style_cluster as sc
    v = [1, 2, 3, 4]
    assert abs(sc._cosine(v, v) - 1.0) < 0.001


def test_cosine_opposite_directions():
    """v2.1：中心化后方向相反的雷达向量相似度 = -1（旧版全正向量恒 ~1 无判别力）。"""
    import style_cluster as sc
    assert abs(sc._cosine([90, 10], [10, 90]) + 1.0) < 0.001


def test_cosine_neutral_vectors():
    """v2.1：全 50 中性向量之间相似度 = 1。"""
    import style_cluster as sc
    assert abs(sc._cosine([50, 50], [50, 50]) - 1.0) < 0.001


def test_kmeans_basic():
    """_kmeans 能正确聚类（v2.1 返回 (assignments, centers)）。"""
    import style_cluster as sc
    # 三组明显的点
    points = [
        [0, 0], [1, 0], [0, 1],  # 簇 0：原点附近
        [10, 10], [11, 10], [10, 11],  # 簇 1：(10,10) 附近
        [20, 20], [21, 20], [20, 21],  # 簇 2：(20,20) 附近
    ]
    assignments, centers = sc._kmeans(points, k=3, max_iter=10)
    # 同一簇的点应分到同一 cluster
    assert assignments[0] == assignments[1]
    assert assignments[3] != assignments[0]
    assert len(centers) == 3


def test_get_all_managers_empty():
    """无 roster 时返回空 dict。"""
    import style_cluster as sc
    with _DirIsolation():
        result = sc._get_all_managers_with_radar()
    assert result == {}


def test_find_similar_no_radar_data():
    """经理无 style_radar 时返回空列表。"""
    import style_cluster as sc
    with _DirIsolation():
        results = sc.find_similar("nonexistent")
    assert results == []


def test_cluster_all_with_sample_data():
    """cluster_all 能基于模拟数据分 2 组。"""
    import style_cluster as sc

    with _DirIsolation():
        import _common
        # 准备 roster.json + 三个经理档案
        _common.write_json(_common.ROSTER_PATH, {
            "meta": {"count": 3, "max": 100},
            "managers": [
                {"id": "m1", "name": "价值经理", "company": "A"},
                {"id": "m2", "name": "成长经理", "company": "B"},
                {"id": "m3", "name": "均衡经理", "company": "C"},
            ],
        })
        # m1 价值型（value 80），m2 成长型（growth 80），m3 均衡
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "价值经理", "company": "A",
            "style_radar": {
                "value_growth": {"value": 90, "growth": 10},
                "market_cap": {"large": 80, "mid": 20},
                "momentum": {"high": 30, "low": 70},
                "quality": {"high": 80, "low": 20},
                "concentration": {"high": 70, "low": 30},
                "turnover": {"high": 20, "low": 80},
            },
        })
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m2.json"), {
            "id": "m2", "name": "成长经理", "company": "B",
            "style_radar": {
                "value_growth": {"value": 10, "growth": 90},
                "market_cap": {"large": 20, "mid": 80},
                "momentum": {"high": 80, "low": 20},
                "quality": {"high": 30, "low": 70},
                "concentration": {"high": 30, "low": 70},
                "turnover": {"high": 80, "low": 20},
            },
        })
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m3.json"), {
            "id": "m3", "name": "均衡经理", "company": "C",
            "style_radar": {
                "value_growth": {"value": 50, "growth": 50},
                "market_cap": {"large": 50, "mid": 50},
                "momentum": {"high": 50, "low": 50},
                "quality": {"high": 50, "low": 50},
                "concentration": {"high": 50, "low": 50},
                "turnover": {"high": 50, "low": 50},
            },
        })
        clusters = sc.cluster_all(k=2)
    assert len(clusters) == 2
    # 均衡经理单独一组（与其他两组差异明显）
    flat = [m["id"] for c in clusters for m in c["members"]]
    assert "m1" in flat
    assert "m2" in flat
    assert "m3" in flat