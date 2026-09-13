# -*- coding: utf-8 -*-
"""观影DNA分析器（实验版 / 后续可蒸馏进 skill 的核心逻辑）

输入：用户最喜欢的 N 部作品，每部打 6 维分（沉浸/情感/智识/暗度/群像/冒险，0-100）
输出：
  1. 六维 DNA 向量（均值）
  2. 12 人格匹配分排序 + 最终人格裁决（含框架 §4.4 兜底规则）
  3. 推荐片单（来自 works_pool.pool_query，支持多方向/多区域/跨人格补位）
"""
import sys
sys.path.insert(0, ".")
from works_pool import PERSONA_VECS, pool_query, neighbor_personas, infer_region_priority

DIMS = ["沉浸度", "情感度", "智识度", "暗度", "群像度", "冒险度"]

# ---------------------------------------------------------------
# 用户输入：12 部最爱的动漫（JOJO 三部曲拆成 3 个数据点 → 共 14 个）
# 每部 6 维打分依据框架 §4.1 的定义来源（题材主轴/群像/暗度等权重更高）
# ---------------------------------------------------------------
USER_WORKS = {
    "全职猎人":                          (80, 60, 55, 45, 80, 50),
    "棋魂":                              (45, 60, 65, 20, 70, 40),
    "钻石王牌":                          (45, 65, 50, 20, 85, 35),
    "JOJO的奇妙冒险 星尘斗士(3部)":       (55, 50, 60, 60, 75, 70),
    "JOJO的奇妙冒险 不灭钻石(4部)":       (50, 55, 55, 50, 80, 65),
    "JOJO的奇妙冒险 黄金之风(5部)":       (55, 50, 60, 65, 80, 70),
    "宝可梦 日月":                        (40, 55, 30, 10, 65, 40),
    "交响情人梦":                        (40, 65, 50, 20, 70, 35),
    "超常技能开启奇幻世界美食之旅":        (60, 50, 35, 25, 60, 55),
    "超智游戏":                          (60, 45, 80, 45, 60, 60),
    "十二国记":                          (80, 60, 65, 45, 75, 60),
    "月刊少女野崎君":                     (30, 55, 45, 10, 75, 30),
    "碧蓝之海":                          (35, 60, 35, 10, 80, 35),
    "某科学的超电磁炮":                   (60, 55, 55, 45, 70, 55),
}


def compute_dna(works):
    n = len(works)
    return tuple(round(sum(v[i] for v in works.values()) / n, 1) for i in range(6))


def match_personas(dna):
    """返回按匹配分降序的 (人格, 分数) 列表。Score = 100 - mean(|u-t|)。"""
    scored = []
    for name, vec in PERSONA_VECS.items():
        mean_diff = sum(abs(dna[i] - vec[i]) for i in range(6)) / 6
        scored.append((name, round(100 - mean_diff, 2)))
    scored.sort(key=lambda x: -x[1])
    return scored


def resolve_persona(dna, scored):
    """框架 §4.4 裁决：多元观影者是兜底，仅当最高分即为其自身、
    且所有特征型人格匹配分都明显偏低时才生效。"""
    best_name, best_score = scored[0]
    if best_name != "多元观影者":
        return best_name, best_score, "argmax 直接命中特征型人格"
    # 最高分是多元 → 检查是否有特征型人格分数足够高（接近多元，差距<2分视为平手）
    feature_scores = [(n, s) for n, s in scored if n != "多元观影者"]
    runner_name, runner_score = feature_scores[0]
    gap = round(best_score - runner_score, 2)
    if gap <= 2.0:
        return runner_name, runner_score, (
            f"原始 argmax 为『多元观影者』({best_score})，但特征型人格"
            f"『{runner_name}』({runner_score}) 仅低 {gap} 分，"
            f"且用户存在单一强峰维度 → 按 §4.4 兜底规则判为『{runner_name}』")
    return best_name, best_score, "所有特征型人格匹配分均偏低，确认为多元观影者"


def recommend(persona, direction="动漫", region=None, region_priority=None, exclude=None, n=14, user_vec=None):
    return pool_query(persona, direction=direction, region=region, region_priority=region_priority,
                     exclude=exclude, n=n, user_vec=user_vec)


def fmt_dna(dna):
    return " / ".join(f"{dims}:{v}" for dims, v in zip(DIMS, dna))


def run():
    dna = compute_dna(USER_WORKS)
    print("=" * 60)
    print("【1】用户六维 DNA（14 个样本均值）")
    print("=" * 60)
    print(fmt_dna(dna))
    peaks = sorted(range(6), key=lambda i: -dna[i])
    print(f"最高维度：{DIMS[peaks[0]]}({dna[peaks[0]]})  "
          f"次高：{DIMS[peaks[1]]}({dna[peaks[1]]})  "
          f"最低：{DIMS[peaks[5]]}({dna[peaks[5]]})")
    span = round(max(dna) - min(dna), 1)
    print(f"维度极差：{span}（>25 表示有强偏好峰，<15 表示非常均衡）")

    print("\n" + "=" * 60)
    print("【2】12 人格匹配分排序")
    print("=" * 60)
    scored = match_personas(dna)
    for i, (name, s) in enumerate(scored, 1):
        tag = "  ← 最高分" if i == 1 else ""
        print(f"{i:>2}. {name:<8} {s}{tag}")

    persona, score, reason = resolve_persona(dna, scored)
    print("\n>>> 裁决：", persona, f"({score} 分)")
    print(">>> 理由：", reason)

    # 根据用户提供的作品名单推断地区偏好（不再写死日本优先）
    region_priority = infer_region_priority(list(USER_WORKS.keys()))
    print("\n>>> 地区优先级（由你的作品名单推断）：", " > ".join(region_priority))

    print("\n" + "=" * 60)
    print(f"【3】推荐片单（人格={persona}，方向=动漫，地区优先级由你的口味驱动，排除已看）")
    print("=" * 60)
    recs = recommend(persona, direction="动漫", region_priority=region_priority,
                     exclude=list(USER_WORKS.keys()), n=16, user_vec=dna)
    # 按区域分组展示
    by_region = {}
    for w in recs:
        by_region.setdefault(w["region"], []).append(w)
    for region in ["日本", "中国", "欧美"]:
        items = by_region.get(region, [])
        if not items:
            continue
        print(f"\n— {region}动漫（{len(items)} 部）—")
        for w in items:
            print(f"  [{w['tier']:>7}] {w['name']} ({w['year']}) "
                  f"{w['cat']} — {w['reason']}")

    print("\n>>> 相邻人格（六维最近的 2 个，可用于『相邻/突破』推荐）：",
          neighbor_personas(persona, top=2))
    return dna, persona, score, recs


if __name__ == "__main__":
    run()
