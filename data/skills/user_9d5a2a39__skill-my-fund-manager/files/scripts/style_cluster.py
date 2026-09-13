"""
同风格经理聚类（v2.0.0 新增）。

基于 style_radar 6 维向量：
- find_similar(id): 和某经理最相似的 top-k
- cluster_all(k=4): 把全部经理分 k 组（KMeans 纯 Python 实现）
- render_cluster_summary(): 输出每组代表+风格画像

零 LLM 依赖，无第三方包。
"""
from __future__ import annotations

import math
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import _common
from _common import load_manager, log

import style_radar as sr


def _flatten_radar(radar: Dict) -> List[float]:
    """同 style_drift._flatten_radar。"""
    vec = []
    for dim in ("value_growth", "market_cap", "momentum", "quality", "concentration", "turnover"):
        v = radar.get(dim, {})
        keys = list(v.keys())[:2]
        for k in keys:
            vec.append(float(v.get(k, 50)))
    return vec


def _cosine(a: List[float], b: List[float]) -> float:
    """中心化余弦相似度（-1~1）。
    v2.1 修复：雷达分均为 0-100 正值，原始余弦恒 ~0.99+ 无判别力；
    先减 50 中心化，使"双高/双低"差异能体现。"""
    if len(a) != len(b):
        return 0.0
    ca = [x - 50.0 for x in a]
    cb = [x - 50.0 for x in b]
    dot = sum(x * y for x, y in zip(ca, cb))
    na = math.sqrt(sum(x * x for x in ca))
    nb = math.sqrt(sum(y * y for y in cb))
    if na == 0 or nb == 0:
        # 全 50 的中性向量：与自身相似、与其他中性向量也视为相似
        return 1.0 if na == nb == 0 else 0.0
    return dot / (na * nb)


def _get_all_managers_with_radar() -> Dict[str, Dict]:
    """加载全部有 style_radar 的经理。"""
    roster_path = _common.ROSTER_PATH
    if not os.path.exists(roster_path):
        return {}
    roster = _common.read_json(roster_path, default={})
    result = {}
    for m in roster.get("managers", []):
        mid = m.get("id")
        if not mid:
            continue
        mgr = load_manager(mid)
        if mgr and mgr.get("style_radar"):
            result[mid] = {
                "name": mgr.get("name", ""),
                "company": mgr.get("company", ""),
                "radar": mgr["style_radar"],
            }
    return result


def find_similar(manager_id: str, top_k: int = 5) -> List[Dict]:
    """找和某经理最相似的 top_k。"""
    all_managers = _get_all_managers_with_radar()
    target = all_managers.get(manager_id)
    if not target:
        return []
    target_vec = _flatten_radar(target["radar"])
    scored = []
    for mid, info in all_managers.items():
        if mid == manager_id:
            continue
        vec = _flatten_radar(info["radar"])
        sim = _cosine(target_vec, vec)
        scored.append({"manager_id": mid, "name": info["name"], "company": info["company"], "similarity": round(sim, 3)})
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]


# ============================================================
# 极简 KMeans（无 sklearn，纯 stdlib）
# ============================================================

def _euclidean(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        return 0.0
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _kmeans(points: List[List[float]], k: int, max_iter: int = 30) -> Tuple[List[int], List[List[float]]]:
    """返回 (每个点的 cluster 索引, 最终中心点)。
    v2.1 修复：初始化从"前 k 点"改为 kmeans++ lite（确定性）：
    首个中心取第 0 点，后续中心逐次选离已有中心最远的点，
    避免重复中心/坏局部解。"""
    if len(points) < k:
        return list(range(len(points))), [list(p) for p in points]
    # 初始化：kmeans++ lite（确定性，无随机）
    centers = [list(points[0])]
    while len(centers) < k:
        farthest_idx, farthest_dist = -1, -1.0
        for i, p in enumerate(points):
            d = min(_euclidean(p, c) for c in centers)
            if d > farthest_dist:
                farthest_dist, farthest_idx = d, i
        if farthest_dist <= 0:  # 剩余点全重复，防死循环
            break
        centers.append(list(points[farthest_idx]))
    assignments = [-1] * len(points)
    for _ in range(max_iter):
        new_assignments = []
        for p in points:
            best = min(range(len(centers)), key=lambda i: _euclidean(p, centers[i]))
            new_assignments.append(best)
        if new_assignments == assignments:
            break
        assignments = new_assignments
        # 更新中心
        for ci in range(len(centers)):
            members = [points[i] for i in range(len(points)) if assignments[i] == ci]
            if members:
                dim = len(centers[ci])
                centers[ci] = [sum(m[d] for m in members) / len(members) for d in range(dim)]
    return assignments, centers


def cluster_all(k: int = 4) -> List[Dict]:
    """把全部经理分 k 组，返回每组代表 + 成员。"""
    all_managers = _get_all_managers_with_radar()
    if not all_managers:
        return []

    ids = list(all_managers.keys())
    vectors = [_flatten_radar(all_managers[mid]["radar"]) for mid in ids]
    assignments, centers = _kmeans(vectors, k)

    # 按 cluster 聚合（同时记录组内向量索引）
    clusters = {}
    for idx, mid in enumerate(ids):
        ci = assignments[idx]
        clusters.setdefault(ci, []).append((idx, mid))

    result = []
    for ci, members in clusters.items():
        # v2.1 修复：代表选组内最接近中心的成员（旧版用名单第一人近似）
        center = centers[ci] if ci < len(centers) else None
        if center is not None:
            rep_idx, rep_id = min(
                members, key=lambda im: _euclidean(vectors[im[0]], center)
            )
        else:
            rep_idx, rep_id = members[0]
        result.append({
            "cluster_id": ci,
            "member_count": len(members),
            "representative_id": rep_id,
            "representative_name": all_managers[rep_id]["name"],
            "members": [{"id": mid, "name": all_managers[mid]["name"]} for _, mid in members],
        })
    result.sort(key=lambda x: -x["member_count"])
    return result


def render_cluster_summary() -> str:
    """渲染聚类摘要。"""
    clusters = cluster_all(k=4)
    if not clusters:
        return "（无 style_radar 数据，请先对经理运行 style_radar.py）"
    lines = [f"🧩 经理风格聚类（共 {sum(c['member_count'] for c in clusters)} 人，{len(clusters)} 组）："]
    for c in clusters:
        lines.append(f"\n  【组 {c['cluster_id']}】 代表：{c['representative_name']}（{c['member_count']} 人）")
        for m in c["members"][:5]:
            lines.append(f"    - {m['name']} ({m['id']})")
        if len(c["members"]) > 5:
            lines.append(f"    ...还有 {len(c['members']) - 5} 人")
    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="同风格经理聚类")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sim = sub.add_parser("similar", help="找相似经理")
    p_sim.add_argument("manager_id")
    p_sim.add_argument("--top-k", type=int, default=5)

    p_cluster = sub.add_parser("cluster_all", help="聚类全部经理")
    p_cluster.add_argument("--k", type=int, default=4)

    args = parser.parse_args()

    if args.cmd == "similar":
        results = find_similar(args.manager_id, args.top_k)
        if not results:
            print(f"经理 {args.manager_id} 无 style_radar 数据")
            sys.exit(1)
        print(f"🎯 和 {args.manager_id} 风格最相似的 {len(results)} 位：")
        for r in results:
            print(f"  {r['name']:　<6} ({r['company']})  相似度={r['similarity']:.3f}")

    elif args.cmd == "cluster_all":
        print(render_cluster_summary())