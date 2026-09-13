# -*- coding: utf-8 -*-
"""剧荒推荐 · 动漫作品库（最终合并版，2975 部）

构成（由 merge_final_pool.py 生成 anime_pool_merged.py）：
- 手工策展库 1000 部（PART_A~G，含 135 部手工策展非日漫：欧美/法/加/俄/英/韩国，
  原样保留，质量最高）
- AniList 扩充标注（非日漫 627 + 日漫热门层 1500）按 name 去重后并入新作品

冷门日漫（pop<20000，约 5233 部，persona 空）暂未纳入：pool_query 按 persona
精确匹配，空 persona 无法召回；后续可通过 genre→persona 推导或继续标注接入。

字段：name/year/direction/region/cat/persona/tier/synopsis/reason
"""
from collections import Counter

from anime_pool_merged import ANIME_POOL

# ---------- 繁简/日文异体字归一化（在数据加载层做一次，全局简体） ----------
try:
    import opencc
    _OPENCC = opencc.OpenCC('t2s')
except Exception:
    _OPENCC = None

# OpenCC t2s 不覆盖日文新字体（如 壊→坏、帰→归），用补充表兜底
_EXTRA_SIMPLIFY = {
    "崩壊3rd 帰还": "崩坏3rd 归还",
    # 可继续追加其他 OpenCC 漏转的日文异体标题
}


def _to_simple(text):
    if not isinstance(text, str):
        return text
    # 1) 先命中兜底表（全标题匹配，优先处理日文新字体标题）
    if text in _EXTRA_SIMPLIFY:
        return _EXTRA_SIMPLIFY[text]
    # 2) OpenCC 标准繁体转简体
    if _OPENCC is not None:
        text = _OPENCC.convert(text)
    return text


# 对作品池中所有面向用户的文本字段做归一化
for _w in ANIME_POOL:
    for _k in ("name", "cat", "synopsis", "reason"):
        if _k in _w:
            _w[_k] = _to_simple(_w[_k])
    if "aliases" in _w and isinstance(_w["aliases"], list):
        _w["aliases"] = [_to_simple(a) for a in _w["aliases"]]

# 释放临时变量
_del = object()
for _name in ("_OPENCC", "_EXTRA_SIMPLIFY", "_to_simple", "_w", "_k"):
    if _name in dir():
        exec(f"del {_name}")

PERSONAS = [
    "暗夜造梦师", "温暖治愈系", "智性探索者", "情感深渊潜行者",
    "冒险浪漫派", "世界观建筑师", "纯粹感受者", "暗黑实验家",
    "现实凝视者", "复杂共情者", "热忱群像派", "多元观影者",
]


if __name__ == "__main__":
    pool = ANIME_POOL
    n = len(pool)
    pc = Counter(w["persona"] for w in pool)
    rc = Counter(w["region"] for w in pool)
    dc = Counter(w["direction"] for w in pool)
    tc = Counter(w["tier"] for w in pool)
    names = [w["name"] for w in pool]
    dup = [k for k, c in Counter(names).items() if c > 1]
    empty = sum(1 for w in pool if not w.get("persona"))
    print(f"作品库总量: {n} 部")
    print(f"重复名: {len(dup)} | 空persona: {empty}")
    print("方向:", dict(dc))
    print("区域:", dict(rc))
    print("tier:", dict(tc))
    print("人格:", dict(pc))
