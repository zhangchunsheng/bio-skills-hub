# -*- coding: utf-8 -*-
"""剧荒推荐 · 动漫作品池（反馈循环可运行版的数据底座）

本 skill 仅推荐【动画】（TV 番 + 动画电影），不推荐真人电视剧 / 电影。
作品库由 anime_pool.py 提供（600 部，12 人格 × 50 均衡，纯文字无封面）。

每部作品字段：
  name, year, direction, region, cat(类型标签),
  persona(主匹配人格), tier(相对该人格的分层 like/expand/try/niche),
  synopsis(简介), reason(一句话匹配理由)

pool_query() 支持：按 人格 + 区域 过滤，并在候选不足时自动从
"相邻人格"（六维余弦最近的 2 个）补位 —— 即第九章的"跨人格相邻补位"。
"""

import math
from domain_config import DOMAINS, get_domain
from anime_pool import ANIME_POOL
from curation import is_blocked  # 争议作品黑名单（中国用户合规护栏）

# ---------- 推荐去重 / 同系列限流（避免「细微差异同名」与「同系列扎堆」）----------
import re as _re

_PUNCT = _re.compile(r'[\s:：\-~!?！?。、，,.!?\'\"()\[\]【】（）／/`·]+')

def name_key(s):
    """归一化作品名：去空白 / 标点 / 大小写，用于「近名重复」判定。"""
    return _PUNCT.sub('', (s or '')).lower()

# 系列基名：在 name_key 基础上剥离「季 / 期 / 媒体 / 续作 / 分章」等多语种标记，
# 使同一系列的不同季 / 剧场版 / 外传在推荐限流时视为同一系列（默认每系列各留 1 部）。
# 覆盖：中文(第N季/剧场版/续集)、日文(セカンドシーズン/映画/外伝)、英文(Season 2/2nd Season/OVA)。
_SERIES_RE = _re.compile(
    r'第[一二三四五六七八九十百零\d]+\s*(?:季|期|シーズン|season)'   # 第2季/第二期/第2シーズン
    r'|(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+season'  # second season
    r'|\b\d+(?:st|nd|rd|th)\s+season'        # 2nd season
    r'|season\s*\d+'                          # Season 2
    r'|セカンドシーズン|サードシーズン|ファーストシーズン|フォースシーズン|フィフスシーズン'  # 日文季数
    r'|[二三五六七八九十]+期'                     # 二期/三期…
    r'|映画|劇場版|剧场版|电影版|动画电影|真人版|実写版'  # 电影版
    r'|\bova\b|\boad\b'                        # OVA / OAD
    r'|外伝|外传|番外編|番外篇|特別編|特别篇|総集編|总集篇|前編|前篇|後編|后篇|完結編|完结篇'  # 外传/总集
    r'|序章|終章|终章|前传|后传|続編|续集|後日譚|後日談'   # 章回 / 续作
    r'|part\s*\d+'                            # Part 2
    r'|第?\d+\s*部'                           # 第二部 / 第2部
    r'|episode\s*\d+|chapter\s*\d+|vol\.?\s*\d+|book\s*\d+'  # 分集 / 卷
    r'|\b(?:ii|iii|iv|vi|vii|viii|ix|x)\b'    # 罗马数字续作
    r'|[：:・·\-～~]+'                         # 残留分隔符
    r'|(?<![\d])\d{1,2}\s*$'                  # 结尾 1-2 位数字（续作编号，如 命运石之门0）
, _re.I)

# 「主标题 + 副标题」型续作的前缀归属索引（惰性构建，见 series_key）。
_NAME_SET = None
_MIN_BASE = 3


def _ensure_name_set():
    """构建系列基名集合 = 作品名 ∪ 剥离续作标记后的基名。

    用于归并「主标题 + 副标题」型续作——这类续作不带季数 / OVA / 剧场版等
    正则可识别的标记（如「排球少年!! 乌野高中 VS 白鸟泽学园高中」），
    仅靠 _SERIES_RE 会和主标题算出不同的 series_key，导致同系列重复推荐。
    """
    global _NAME_SET
    if _NAME_SET is None:
        names = {name_key(w.get("name", "")) for w in WORKS_POOL if w.get("name")}
        bases = set()
        for nm in names:
            b = _SERIES_RE.sub('', nm).strip()
            if len(b) >= _MIN_BASE:
                bases.add(b)
        _NAME_SET = {n for n in (names | bases) if len(n) >= _MIN_BASE}
    return _NAME_SET


def _prefix_base(s):
    """若 s 以某个已知系列基名开头，返回该基名（取最长匹配）；否则返回 None。

    取最长匹配可避免把「魔法少女小圆」误并入更短的「魔法少女」。
    """
    ns = _ensure_name_set()
    if not s or len(s) < _MIN_BASE:
        return None
    for i in range(len(s) - 1, _MIN_BASE - 1, -1):
        if s[:i] in ns:
            return s[:i]
    return None


def series_key(name):
    """提取系列基名：剥离多语种季 / 媒体 / 续作标记，同一系列不同作品得到相同 key。

    两阶段归并：
      ① 正则剥离季数 / 剧场版 / OVA / 外传等续作标记（如「…第二季」→ 主标题）；
      ② 前缀归属——把「主标题 + 副标题」型续作归并回主标题系列
         （如「排球少年!! 乌野高中 VS 白鸟泽学园高中」→「排球少年」）。
    """
    s = _PUNCT.sub('', (name or '')).lower()
    base = _SERIES_RE.sub('', s).strip()
    pb = _prefix_base(base)
    if pb and pb != base:
        base = pb
    return _SERIES_RE.sub('', base).strip()

def finalize_reco(cands, n, per_series=1):
    """从已按优先级排序的候选 cands 中选出最多 n 部推荐：
    - 同名 / 近名（name_key 相同）只保留第一条；
    - 同一系列（series_key 相同）最多保留 per_series 部（默认 1）；
    - 一旦凑满 n 即停止（调用方应传入足够长的候选列表以便回填）。
    返回 list[dict]，长度 <= n，且保持 cands 的相对优先级。
    """
    seen_name, seen_series, out = set(), {}, []
    for w in cands:
        nk = name_key(w.get('name'))
        sk = series_key(w.get('name'))
        if nk in seen_name:
            continue
        if seen_series.get(sk, 0) >= per_series:
            continue
        seen_name.add(nk)
        seen_series[sk] = seen_series.get(sk, 0) + 1
        out.append(w)
        if len(out) >= n:
            break
    return out

# ---------- 12 人格六维向量（沉浸/情感/智识/暗度/群像/冒险）----------
PERSONA_VECS = {
    "暗夜造梦师": (75, 55, 70, 75, 45, 55),
    "温暖治愈系": (35, 75, 35, 20, 55, 35),
    "智性探索者": (55, 35, 80, 45, 30, 70),
    "情感深渊潜行者": (50, 75, 40, 75, 45, 35),
    "冒险浪漫派": (55, 70, 50, 30, 55, 75),
    "世界观建筑师": (80, 50, 70, 30, 30, 50),
    "纯粹感受者": (35, 75, 25, 25, 55, 35),
    "暗黑实验家": (50, 35, 65, 75, 30, 75),
    "现实凝视者": (30, 55, 70, 65, 45, 50),
    "复杂共情者": (55, 65, 65, 60, 45, 50),
    "热忱群像派": (45, 70, 50, 25, 90, 55),
    "多元观影者": (50, 50, 50, 50, 50, 50),
}

# tier 排序权重（like 最优先展示）
TIER_RANK = {"like": 0, "expand": 1, "try": 2, "niche": 3, "neighbor": 4}


def _sort_by_tier(works):
    """把片单按档位顺序排列：like → expand → try → niche → neighbor。

    Python 排序稳定，因此同一 tier 内部的相似度/优先级顺序保持不变。
    """
    return sorted(works, key=lambda w: TIER_RANK.get(w.get("tier"), 99))


# 本 skill 仅推荐动画：作品池 = 动画库（TV 番 + 动画电影，1000 部），不含真人电视剧/电影。
WORKS_POOL = ANIME_POOL

# 作品名 -> 区域 反查表（用于根据用户作品名单推断地区偏好）
NAME_REGION = {w["name"]: w["region"] for w in WORKS_POOL}


def infer_region_priority(work_names, fallback=None, min_signal=3):
    """根据用户提供的作品名单推断【区域优先级】，地区不再写死日本第一。

    机制：在作品池里查到这些作品的区域，按出现频次降序排列；
    频率并列时保持 fallback 的相对顺序（结果稳定、可复现）。
    命中数量不足 min_signal 时，回退到 fallback（默认动漫域冷启动顺序）。

    效果：用户列了一堆国漫 -> 区域优先级变成「中国」在前；
          列了欧美番 -> 「欧美」在前；列了日番 -> 「日本」在前。
          地区完全由用户真实口味驱动，而非硬编码。

    参数
    ----
    work_names  用户提供的作品名列表（与作品池 name 越能对齐，信号越强）
    fallback    冷启动回退顺序；默认 None -> 动漫域配置的 region_priority
    min_signal  命中作品数下限，低于此值视为信号不足、回退 fallback
    """
    if fallback is None:
        try:
            fallback = list(get_domain("动漫")["region_priority"])
        except Exception:
            fallback = ["日本", "中国", "欧美"]
    counts = {}
    for name in work_names or []:
        r = NAME_REGION.get(name)
        if r:
            counts[r] = counts.get(r, 0) + 1
    if sum(counts.values()) < min_signal:
        # FIX-B: 命中不足时不再整体回退 fallback（会把用户明确偏好丢掉），
        # 而是把已命中的 region 提到最前，其余仍按 fallback 相对顺序补齐。
        if counts:
            partial = sorted(counts.keys(),
                             key=lambda r: (-counts[r],
                                            fallback.index(r) if r in fallback else 99))
            rest = [r for r in fallback if r not in partial]
            return partial + rest
        return list(fallback)
    # 按频次降序；同频次保持 fallback 相对顺序（让结果可复现）
    ordered = sorted(counts.keys(),
                     key=lambda r: (-counts[r], fallback.index(r) if r in fallback else 99))
    # 补上 fallback 里未被命中的区域（如用户只列了日/中，仍保留欧美在末位可选）
    for r in fallback:
        if r not in ordered:
            ordered.append(r)
    return ordered


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb) if na and nb else 0


def neighbor_personas(persona, top=2):
    """返回与 persona 六维余弦最近的 top 个其他人格。"""
    v = PERSONA_VECS[persona]
    scored = [(p, _cosine(v, PERSONA_VECS[p])) for p in PERSONA_VECS if p != persona]
    scored.sort(key=lambda x: -x[1])
    return [p for p, _ in scored[:top]]


# ---------- 作品 → 六维向量（由 cat 题材标签派生，用于个性化相似度）----------
# 题材标签词 → 六维贡献（沉浸/情感/智识/暗度/群像/冒险）；一个标签可贡献多维度。
TAG_DIM = {
    0: ["奇幻", "科幻", "异界", "蒸汽", "史诗", "世界", "魔幻", "神话", "架空"],
    1: ["治愈", "催泪", "青春", "恋爱", "情感", "温情", "羁绊", "日常", "成长",
        "纯爱", "友情", "亲情", "爱情", "校园", "音乐", "运动", "热血"],
    2: ["悬疑", "烧脑", "智斗", "哲学", "思辨", "推理", "心理", "超能力", "实验",
        "解谜", "社会", "现实", "权谋", "职场", "历史"],
    3: ["暗黑", "黑暗", "恐怖", "哥特", "复仇", "末日", "血腥", "暴力", "犯罪",
        "猎奇", "深渊"],
    4: ["群像"],
    5: ["冒险", "热血", "战斗", "动作", "武侠", "战争", "旅行", "运动", "异界"],
}

def work_vec(w):
    """把作品题材标签 cat 映射成六维方向向量（L2 归一化）。

    无标签命中时回退到该作品主人格向量，保证仍可参与相似度计算。
    """
    vec = [0] * 6
    cat = w.get("cat", "") or ""
    for dim, keys in TAG_DIM.items():
        for k in keys:
            if k in cat:
                vec[dim] += 1
    nrm = math.sqrt(sum(v * v for v in vec))
    if nrm == 0:
        return list(PERSONA_VECS.get(w.get("persona"), (50, 50, 50, 50, 50, 50)))
    return [v / nrm for v in vec]


def pool_query(persona, direction=None, region=None, region_priority=None,
               domain=None, exclude=None, n=20, neighbor_top=2, user_vec=None):
    """从作品池挑选推荐候选。

    参数
    ----
    persona         目标人格名
    direction / region / region_priority / domain / exclude / n / neighbor_top
                    见旧逻辑说明。
    user_vec        用户的六维 DNA 向量（沉浸/情感/智识/暗度/群像/冒险，0-100）。
                    - 不传：按人格 + 区域 + tier 排序（旧行为，向后兼容，demo 用）。
                    - 传入：在同一人格池内按"与用户口味的余弦相似度"重排，
                      使**同一人格、不同分数画像的用户拿到不同的 20 部**，且仍保持
                      五档结构、每用户恰好 20 部。
    region_priority 区域优先级（高优先级在前），应由用户作品名单推断得到
                    （见 infer_region_priority），而非写死「日本第一」。
                    跨区（非最高优先级区域）的同人格作品自动降级到 neighbor；
                    因此"主档（本命/上头…）"始终贴合用户偏好的地区。

    设计要点（个性化分支）
    ----------------------
    - 每个 tier 内按相似度取 top-k（配额 like6/expand5/try4/niche3/neighbor2=20），
      因此同人格不同用户在各档里看到的具体作品不同。
    - 跨区（非最高优先级区域）同人格作品降级到 neighbor；相邻人格作品归入 neighbor，
      自然成为"意外惊喜/突破"档。
    - 结果确定性：相同 user_vec → 相同 20 部（便于复现，非随机）。
    """
    if persona not in PERSONA_VECS:
        raise ValueError(
            f"未知人格：{persona!r}。可用人格：{list(PERSONA_VECS.keys())}")

    if domain is not None:
        cfg = get_domain(domain)
        if direction is None:
            direction = cfg["direction"]
        if region is None and region_priority is None:
            region_priority = cfg["region_priority"]

    exclude = set(exclude or [])

    # 规范化 direction 为多值集合（支持「动漫 + 动画电影」），None 表示不限方向
    dirs = (tuple(direction) if isinstance(direction, (list, tuple, set))
            else (direction,) if direction is not None else None)

    def region_idx(region_name):
        if region_priority:
            try:
                return region_priority.index(region_name)
            except ValueError:
                return len(region_priority)
        return 0

    top_region = region_priority[0] if region_priority else None

    if user_vec is None:
        # ---------- 旧逻辑（向后兼容：demo / 未传 DNA 时）----------
        def match(w):
            if w["name"] in exclude or is_blocked(w["name"]):
                return False
            if w["persona"] != persona:
                return False
            if dirs is not None and w["direction"] not in dirs:
                return False
            if region is not None and w["region"] != region:
                return False
            return True

        def sort_key(w):
            return (region_idx(w["region"]), TIER_RANK[w["tier"]])

        def collect(pool_personas):
            cands = [w for w in WORKS_POOL if match(w) and w["persona"] in pool_personas]
            cands.sort(key=sort_key)
            out = []
            for w in cands:
                w2 = dict(w)
                if top_region and w["region"] != top_region:
                    w2["tier"] = "neighbor"
                out.append(w2)
            return out

        result = collect({persona})
        if len(result) < n:
            seen = {name_key(r["name"]) for r in result}
            for w in collect(set(neighbor_personas(persona, top=neighbor_top))):
                if name_key(w["name"]) in seen:
                    continue
                result.append(w)
                seen.add(name_key(w["name"]))
        # 近名去重 + 同系列限流（每个系列默认各留 1 部），collect 已含足量候选
        return _sort_by_tier(finalize_reco(result, n, per_series=1))

    # ---------- 个性化逻辑：按用户六维 DNA 在人格池内做相似度重排 ----------
    pool_personas = {persona} | set(neighbor_personas(persona, top=neighbor_top))
    by_tier = {t: [] for t in TIER_RANK}
    for w in WORKS_POOL:
        if w["name"] in exclude or is_blocked(w["name"]):
            continue
        if dirs is not None and w["direction"] not in dirs:
            continue
        if region is not None and w["region"] != region:
            continue
        if w["persona"] == persona:
            # FIX-A: 跨区同人格作品原本「一律降级到 neighbor」，导致 top_region 一旦
            # 被冷启动错设（如日本），整个国漫池都被塞进 neighbor，主档被日漫占满。
            # 改为：只有 try（本就是拓展档）降级为 neighbor 当「跨区惊喜」，
            # like/expand 保留原 tier，让偏好地区的标杆作仍能进入主档。
            # FIX-E: niche 不再跟随降级——实测当偏好地区非日本时，niche 候选会被
            # 抽干到 0（48 组场景里 5 组），该档直接消失。niche 仅 3 部且属「挖宝」
            # 性质，留在冷门档不影响主档（like/expand）贴合偏好地区。
            if top_region and w["region"] != top_region:
                t = "neighbor" if w["tier"] == "try" else w["tier"]
            else:
                t = w["tier"]
            by_tier[t].append(w)
        elif w["persona"] in pool_personas:
            by_tier["neighbor"].append(w)   # 相邻人格 → 突破/惊喜

    def score_key(w):
        return (region_idx(w["region"]), -_cosine(user_vec, work_vec(w)))

    for t in by_tier:
        by_tier[t].sort(key=score_key)

    quota = {"like": 6, "expand": 5, "try": 4, "niche": 3, "neighbor": 2}
    OVERFLOW = 3
    # FIX-D: 原实现把每档 quota*OVERFLOW 全部串成一条长候选，finalize_reco 一旦
    # 在前两档凑满 n 就 break，try/niche/neighbor 永远选不进来（五档塌成两档）。
    # 改为两阶段：① 先每档只取配额量（quota 合计 = 20 = n），保证五档都有席位；
    # ② 因近名/同系列去重导致不足 n 时，再从各档 OVERFLOW 余量按档优先补齐。
    tier_order = ["like", "expand", "try", "niche", "neighbor"]
    MIN_PER_TIER = 1   # 方案 A 兜底：每个「有候选」的档位至少保留 1 部（见文件末尾保底段）
    # 轮转交织（而非按档铺开）：先各档第 1 部、再各档第 2 部……
    # 这样 finalize_reco 去重时会优先保住每个档位的第一个席位，
    # 避免稀缺档位被排在前面的大档（like/expand）挤空。
    cands = []
    max_len = max((min(quota[t], len(by_tier[t])) for t in tier_order), default=0)
    for i in range(max_len):
        for t in tier_order:
            if i < min(quota[t], len(by_tier[t])):
                w2 = dict(by_tier[t][i])
                w2["tier"] = t
                cands.append(w2)

    out = finalize_reco(cands, n, per_series=1)

    # ② 不足 n：先从「已有席位但被去重挤掉」的档内 OVERFLOW 余量补，保持档结构
    if len(out) < n:
        used_name = {name_key(w["name"]) for w in out}
        used_series = {series_key(w["name"]) for w in out}
        extra = []
        for t in tier_order:
            for w in by_tier[t][quota[t]: quota[t] * OVERFLOW]:
                w2 = dict(w)
                w2["tier"] = t
                extra.append(w2)
        for w in extra:
            if len(out) >= n:
                break
            nk, sk = name_key(w["name"]), series_key(w["name"])
            if nk in used_name or sk in used_series:
                continue
            used_name.add(nk)
            used_series.add(sk)
            out.append(w)

    # 仍不足 n：从「同人格 + 相邻人格」剩余池按相似度补足（保持近名 / 同系列护栏）
    if len(out) < n:
        used_name = {name_key(w["name"]) for w in out}
        used_series = {series_key(w["name"]) for w in out}
        rest = [w for w in WORKS_POOL
                if name_key(w["name"]) not in used_name
                and series_key(w["name"]) not in used_series
                and w["name"] not in exclude
                and not is_blocked(w["name"])
                and (dirs is None or w["direction"] in dirs)
                and (region is None or w["region"] == region)
                and w["persona"] in pool_personas]
        rest.sort(key=score_key)
        for w in rest:
            if len(out) >= n:
                break
            out.append(dict(w))

    # ④ 档位保底（方案 A 兜底）：确保每个「有候选」的档位至少 MIN_PER_TIER 部。
    #    防御两类情况：近名 / 同系列去重把整个档位剔空；未来数据分布变化导致某档稀缺。
    #    若该档确实一部候选都没有，则跳过——不凭空凑数，也不把别的作品改档冒名顶替。
    if MIN_PER_TIER > 0:
        from collections import Counter as _Cnt
        used_name = {name_key(w["name"]) for w in out}
        used_series = {series_key(w["name"]) for w in out}
        cur = _Cnt(w["tier"] for w in out)
        for t in tier_order:
            if cur.get(t, 0) >= MIN_PER_TIER:
                continue
            for cand in by_tier[t]:
                nk, sk = name_key(cand["name"]), series_key(cand["name"])
                if nk in used_name or sk in used_series:
                    continue
                if len(out) >= n:
                    # 已满员：挤掉一部「所属档位数量 > MIN_PER_TIER」的末尾作品
                    victim = None
                    for j in range(len(out) - 1, -1, -1):
                        if cur.get(out[j]["tier"], 0) > MIN_PER_TIER:
                            victim = j
                            break
                    if victim is None:
                        break
                    removed = out.pop(victim)
                    cur[removed["tier"]] -= 1
                    used_name.discard(name_key(removed["name"]))
                    used_series.discard(series_key(removed["name"]))
                w2 = dict(cand)
                w2["tier"] = t
                out.append(w2)
                cur[t] = cur.get(t, 0) + 1
                used_name.add(nk)
                used_series.add(sk)
                break
    return _sort_by_tier(out[:n])


def _resolve_region_priority(args_region):
    """把 CLI 的 --region 参数转成 region_priority 列表（该 region 置顶）。"""
    if not args_region:
        return None
    fallback = ["日本", "中国", "欧美"]
    try:
        fallback = list(get_domain("动漫")["region_priority"])
    except Exception:
        pass
    rest = [r for r in fallback if r != args_region]
    return [args_region] + rest


if __name__ == "__main__":
    import argparse, json
    from collections import Counter

    ap = argparse.ArgumentParser(
        description="剧荒推荐 · 作品检索（仅标准库，无需 Pillow / opencc）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python works_pool.py --persona \"热忱群像派\"\n"
            "  python works_pool.py --persona \"热忱群像派\" --region 中国 --json\n"
            "  python works_pool.py --stats\n"
        ),
    )
    ap.add_argument("--persona", help="观影人格名（如：热忱群像派）")
    ap.add_argument("--region", help="区域置顶（中国/日本/欧美），用于推断地区偏好")
    ap.add_argument("--domain", default="动漫", help="域（默认：动漫）")
    ap.add_argument("--n", type=int, default=20, help="返回部数（默认 20）")
    ap.add_argument("--user-vec", help="用户六维 DNA，逗号分隔 6 个 0-100 的数"
                    "（沉浸,情感,智识,暗度,群像,冒险），如 60,70,55,40,75,55")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出（便于模型解析）")
    ap.add_argument("--stats", action="store_true", help="打印作品池统计而非检索")
    args = ap.parse_args()

    if args.stats:
        print(f"作品池总量: {len(WORKS_POOL)} 部")
        print("方向分布:", dict(Counter(w["direction"] for w in WORKS_POOL)))
        print("动漫各人格分布:",
              dict(Counter(w["persona"] for w in WORKS_POOL if w["direction"] == "动漫")))
        raise SystemExit(0)

    if not args.persona:
        ap.error("必须指定 --persona（或改用 --stats 查看作品池统计）")

    if args.persona not in PERSONA_VECS:
        available = "、".join(PERSONA_VECS.keys())
        raise SystemExit(
            f"[错误] 未知人格「{args.persona}」。\n可用人格：{available}")

    user_vec = None
    if args.user_vec:
        try:
            parts = [float(x) for x in args.user_vec.split(",")]
            if len(parts) != 6:
                raise ValueError("需要 6 个数")
            user_vec = tuple(parts)
        except Exception as e:
            raise SystemExit(f"[错误] --user-vec 解析失败：{e}（应为 6 个 0-100 逗号分隔数）")

    recs = pool_query(
        args.persona,
        domain=args.domain,
        n=args.n,
        user_vec=user_vec,
        region_priority=_resolve_region_priority(args.region),
    )

    if args.json:
        print(json.dumps(recs, ensure_ascii=False, indent=2))
    else:
        print(f"# 人格：{args.persona}（共 {len(recs)} 部）")
        for i, w in enumerate(recs, 1):
            print(f"{i:>2}. [{w['tier']}] {w['name']} "
                  f"（{w.get('year','')}·{w.get('region','')}·{w.get('direction','')}）")
            print(f"    标签：{w.get('cat','')}")
            print(f"    简介：{w.get('synopsis','')}")
            print(f"    理由：{w.get('reason','')}")
