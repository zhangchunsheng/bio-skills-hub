#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新闻重大性过滤器（最严口径）

问题背景：上游追踪把"公司名 + 任意BD词"命中的新闻全推，康方一次刷 22 条，
其中实际只有 3~4 个事件，其余全是二次解读/股评/榜单噪音。

口径（最严）：只推三类对股价有重大影响的新闻，其余一律丢弃：
  1. data_readout  数据读出 —— 注册/关键临床数据、主要终点达成或失败、揭盲、OS/PFS
  2. regulatory    监管批准或拒批 —— NMPA/FDA/EMA 批准、拒批、CRL、临床暂停、撤回
  3. deal_amount   并购/授权带金额 —— license-out / 收购 / 合并，且标题含明确金额

配套三道处理：
  · 噪音名单前置拦截（股评/榜单/复盘/评级/"why shares moved"）
  · 48 小时硬时间窗（Google News 会返回旧闻）
  · 事件聚类去重（同一事件多家媒体转载 → 只留首发，其余计数折叠）

用法：
    from biopharma_data_sources.news_materiality_filter import filter_material
    kept, stats = filter_material(hits, lookback_hours=48, subject_terms=[...])
"""
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

# ── 噪音：命中即丢（股评/榜单/复盘/行情解读） ──
NOISE_PATTERNS = (
    "stocks to watch", "stock to watch", "stocks to buy", "stock to buy", "best stocks",
    "top stocks", "penny stock", "should you buy", "buy or sell", "is it time to buy",
    "price target", "analyst", "analysts", "rating", "upgrade", "downgrade",
    "here's why", "heres why", "here is why", "why shares", "why is", "what to know",
    "shares jump", "shares surge", "shares fall", "shares slide", "shares rise",
    "stock jumps", "stock falls", "stock surges", "stock drops", "stock soars",
    "premarket", "pre-market", "market close", "closing bell", "recap", "week in review",
    "weekly wrap", "roundup", "round-up", "digest", "newsletter", "podcast", "webinar",
    "opinion", "commentary", "editorial", "interview", "outlook for", "forecast to 20",
    "market size", "market report", "research report", "cagr", "market share analysis",
    "simply wall st", "motley fool", "zacks", "seeking alpha", "investing.com",
    "jim cramer", "insider monkey", "hedge fund", "13f",
    # 估值/观点/科普类（不带新增事实，纯二次加工）
    "undervalued", "overvalued", "fair value", "intrinsic value", "valuation",
    "mean for investor", "what does", "what it means", "could be", "here's what",
    "5 things", "3 things", "things to know", "explained", "deep dive", "primer",
    "watch:", "odds", "confident of", "bull case", "bear case", "worth watching",
    "vs ", " versus ", "compared", "peer comparison", "years of growth",
    "株価", "値上がり", "値下がり", "見通し", "銘柄", "投資判断",
    "股价", "涨幅", "跌幅", "研报", "评级", "点评", "解读", "复盘", "看点",
)

# ── 类别1：数据读出 ──
READOUT_STAGE = (
    "phase 3", "phase iii", "phase 2/3", "phase iib", "pivotal", "registrational",
    "confirmatory", "第3相", "第iii相", "第ii/iii相", "三期", "iii期", "ⅲ期", "关键注册",
)
READOUT_SIGNAL = (
    "topline", "top-line", "top line", "primary endpoint", "primary endpoints",
    "met the primary", "missed the primary", "failed to meet", "did not meet",
    "statistically significant", "interim analysis", "final analysis", "data readout",
    "readout", "overall survival", "progression-free survival", "pfs", "os benefit",
    "survival benefit", "efficacy results", "trial results", "study results",
    "unblinded", "data cutoff", "hazard ratio",
    "主要評価項目", "中間解析", "全生存", "無増悪生存", "有効性",
    "主要终点", "总生存", "无进展生存", "揭盲", "期中分析", "统计学显著",
)

# ── 类别2：监管批准/拒批 ──
REG_BODY = (
    "fda", "nmpa", "ema", "chmp", "pmda", "mhra", "cde", "ec approval",
    "european commission", "european medicines agency", "健康保険", "厚生労働省",
    "国家药监局", "药监局", "欧盟", "欧洲药品管理局", "美国fda",
)
REG_ACTION = (
    "approve", "approves", "approved", "approval", "authorisation", "authorization",
    "authorised", "authorized", "clearance", "cleared", "green light", "greenlight",
    "reject", "rejects", "rejected", "rejection", "declines to approve",
    "complete response letter", " crl", "crl ", "clinical hold", "partial hold",
    "suspends trial", "halts trial", "trial halted", "withdraw", "withdrawn",
    "recall", "safety signal", "black box", "label expansion", "sbla", "bla accepted",
    "nda accepted", "accepted for review", "priority review", "breakthrough therapy",
    "orphan drug", "fast track", "pdufa",
    "承認", "承認取得", "承認申請", "審査", "優先審査", "希少疾病",
    "获批", "批准", "拒批", "受理", "优先审评", "突破性疗法", "附条件批准", "上市许可",
)

# ── 类别3：并购/授权（必须带金额） ──
DEAL_WORD = (
    "license", "licence", "licensing", "out-licensing", "licensing deal", "licensing agreement",
    "acquire", "acquires", "acquisition", "acquired", "merger", "merges", "buyout",
    "takeover", "to buy", "stake", "collaboration", "partnership", "exclusive rights",
    "option agreement", "asset purchase", "tender offer",
    "ライセンス", "契約", "買収", "合併", "提携", "導出", "導入",
    "授权", "许可", "收购", "并购", "合并", "独家权益", "对外授权", "license-out",
)
AMOUNT_RE = re.compile(
    r"(?:"
    r"[\$€£¥]\s?\d[\d,.]*\s?(?:k|m|mn|bn|b|million|billion|亿|万)?"       # $500 million / $1.2bn
    r"|\d[\d,.]*\s?(?:million|billion|mn|bn)\s?(?:dollar|usd|euro|eur|pound)?"
    r"|\d[\d,.]*\s?(?:亿|万)\s?(?:美元|美金|港元|港币|人民币|元|ドル|円)"
    r"|\d[\d,.]*\s?(?:億|万)\s?(?:ドル|円)"
    r"|upfront\s+payment"
    r"|首付款|首付|里程碑付款|总金额|交易总额"
    r")",
    re.IGNORECASE,
)

CATEGORY_LABEL = {
    "data_readout": "📊 数据读出",
    "regulatory": "🏛️ 监管批准/拒批",
    "deal_amount": "💰 并购授权（带金额）",
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "with", "from", "into", "after", "before",
    "of", "in", "on", "to", "as", "at", "by", "its", "it", "is", "are", "was", "were",
    "be", "been", "new", "says", "said", "will", "has", "have", "had", "that", "this",
    "more", "than", "over", "amid", "but", "not", "no", "up", "down", "out", "first",
    "news", "report", "reports", "update", "updates", "co", "ltd", "inc", "corp",
}


def _norm(text: str) -> str:
    return (text or "").lower()


def is_noise(title: str) -> bool:
    t = _norm(title)
    return any(p in t for p in NOISE_PATTERNS)


def classify(title: str) -> str:
    """返回 'data_readout' / 'regulatory' / 'deal_amount'，非重大返回 ''。"""
    t = _norm(title)
    if not t or is_noise(t):
        return ""

    # 1. 数据读出：需「临床阶段」或「读出信号」中的硬信号
    if any(k in t for k in READOUT_SIGNAL) and (
        any(k in t for k in READOUT_STAGE)
        or any(k in t for k in ("primary endpoint", "topline", "top-line", "readout",
                               "overall survival", "progression-free survival",
                               "survival benefit", "主要终点", "主要評価項目",
                               "总生存", "全生存", "揭盲"))
    ):
        return "data_readout"

    # 2. 监管批准/拒批：需「监管机构」+「监管动作」同时命中
    if any(k in t for k in REG_BODY) and any(k in t for k in REG_ACTION):
        return "regulatory"
    # 无机构名但动作极强（获批/拒批/临床暂停）也算
    if any(k in t for k in ("approval", "approves", "approved", "rejected", "rejection",
                            "complete response letter", "clinical hold",
                            "获批", "批准", "拒批", "承認取得")):
        return "regulatory"

    # 3. 并购/授权：必须交易词 + 明确金额
    if any(k in t for k in DEAL_WORD) and AMOUNT_RE.search(title or ""):
        return "deal_amount"

    return ""


def _fingerprint(title: str) -> set:
    """标题指纹：去停用词后的显著 token 集合，用于同事件聚类。"""
    t = re.sub(r"[^a-z0-9\u4e00-\u9fff\s]", " ", _norm(title))
    toks = {w for w in t.split() if len(w) >= 4 and w not in STOPWORDS}
    # 中文标题按 2-gram 补充
    for seg in re.findall(r"[\u4e00-\u9fff]{2,}", title or ""):
        for i in range(len(seg) - 1):
            toks.add(seg[i:i + 2])
    return toks


# 生物药通用后缀（自动识别药名实体）+ 管线代号形态（AK112 / HLX10 / SHR-1210）
DRUG_SUFFIX = ("mab", "nib", "tinib", "cept", "sen", "stat", "ciclib", "parib", "zumab", "limab")
CODE_RE = re.compile(r"\b([A-Z]{2,4}[-\s]?\d{2,5}[A-Za-z]?)\b")


def extract_entities(title: str, known_entities=None) -> set:
    """抽取标题中的药物实体（已知分子名/代号优先，其次按生物药后缀+代号形态自动识别）。"""
    ents = set()
    t = _norm(title)
    for e in (known_entities or []):
        e = (e or "").strip().lower()
        if e and len(e) >= 3 and e in t:
            ents.add(e)
    for w in re.findall(r"[a-z]{6,}", t):
        if w in STOPWORDS:
            continue
        if any(w.endswith(s) for s in DRUG_SUFFIX):
            ents.add(w)
    for m in CODE_RE.findall(title or ""):
        ents.add(m.replace(" ", "").replace("-", "").lower())
    return ents


def _same_event(a, b) -> bool:
    """(category, entities, tokens) 三元组判定是否同一事件。

    · 双方都有药物实体 → 实体有交集才算同事件（不同药 = 不同事件）
    · 一方无实体（多为二次转载的概述稿）→ 同类别 + 少量共同关键词即合并
    · 双方都无实体 → 同类别 + 关键词重叠 ≥ 0.3
    """
    cat_a, ent_a, tok_a = a
    cat_b, ent_b, tok_b = b
    if cat_a != cat_b:
        return False
    if ent_a and ent_b:
        return bool(ent_a & ent_b)
    if ent_a or ent_b:
        # 一方无药名（典型的二次转载概述稿）→ 同类别且有共同关键词即视为同事件
        return bool(tok_a & tok_b)
    return _similar(tok_a, tok_b, 0.30)


def _similar(a: set, b: set, threshold: float = 0.5) -> bool:
    if not a or not b:
        return False
    inter = len(a & b)
    union = len(a | b)
    if not union:
        return False
    return (inter / union) >= threshold


def _parse_dt(s: str):
    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def is_relevant(title: str, subject_terms) -> bool:
    """主体相关性门控：标题必须提到本公司或本公司管线，否则是泛行业稿/别家新闻。"""
    if not subject_terms:
        return True
    t = _norm(title)
    for s in subject_terms:
        s = (s or "").strip().lower()
        if len(s) >= 3 and s in t:
            return True
    return False


def filter_material(hits, lookback_hours: int = 48, known_entities=None, subject_terms=None):
    """四道过滤：时间窗 → 主体相关性 → 重大性分级 → 事件聚类去重。

    known_entities: 公司管线分子名/代号列表（提升同事件聚类准确度）
    subject_terms:  公司名/别名/管线名列表（标题未提到本公司主体 → 丢弃）
    返回 (kept_hits, stats)
    """
    stats = {"raw": len(hits), "dropped_stale": 0, "dropped_irrelevant": 0,
             "dropped_noise": 0, "dropped_minor": 0, "clustered": 0, "kept": 0}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    staged = []
    for h in hits:
        title = h.get("title", "")
        dt = _parse_dt(h.get("pubDate", ""))
        if dt and dt < cutoff:
            stats["dropped_stale"] += 1
            continue
        if not is_relevant(title, subject_terms):
            stats["dropped_irrelevant"] += 1
            continue
        if is_noise(title):
            stats["dropped_noise"] += 1
            continue
        cat = classify(title)
        if not cat:
            stats["dropped_minor"] += 1
            continue
        staged.append((dt, cat, h, extract_entities(title, known_entities)))

    # 排序：带药名实体的首发稿优先占位（信息量高），其次时间升序，无时间排最后
    _far = datetime.max.replace(tzinfo=timezone.utc)
    staged.sort(key=lambda x: (not x[3], x[0] is None, x[0] or _far))

    kept = []
    keys = []
    for dt, cat, h, ents in staged:
        title = h.get("title", "")
        key = (cat, ents, _fingerprint(title))
        merged = False
        for i, prev in enumerate(keys):
            if _same_event(prev, key):
                kept[i]["dup_count"] = kept[i].get("dup_count", 0) + 1
                src = h.get("source", "")
                if src and src not in kept[i]["dup_sources"]:
                    kept[i]["dup_sources"].append(src)
                kept[i].setdefault("merged_keys", []).append(h.get("key") or title)
                stats["clustered"] += 1
                merged = True
                break
        if merged:
            continue
        item = dict(h)
        item["category"] = cat
        item["category_label"] = CATEGORY_LABEL[cat]
        item["dup_count"] = 0
        item["dup_sources"] = []
        item["merged_keys"] = []
        item["age_hours"] = ((datetime.now(timezone.utc) - dt).total_seconds() / 3600) if dt else None
        kept.append(item)
        keys.append(key)

    stats["kept"] = len(kept)
    return kept, stats


if __name__ == "__main__":
    from . import fintrust_onboard as _fintrust
    _fintrust.require_api_key()  # 硬校验：保持全包口径一致（本演示不发起网络请求）
    samples = [
        ("Akeso secures China NMPA authorisation for ivonescimab combo", "Mon, 25 Aug 2026 02:00:00 GMT"),
        ("Akeso (SEHK:9926) Wins China Lung Cancer Approval As Breast Cancer Trial Begins", "Mon, 25 Aug 2026 03:00:00 GMT"),
        ("Summit, Akeso's China approval celebration cut short as survival benefit degrades", "Mon, 25 Aug 2026 04:00:00 GMT"),
        ("China's NMPA approves Akeso's gumokimab for plaque psoriasis", "Mon, 25 Aug 2026 05:00:00 GMT"),
        ("Why Akeso shares jumped 8% today - Simply Wall St", "Mon, 25 Aug 2026 05:30:00 GMT"),
        ("Akeso licenses out ivonescimab rights for $500 million upfront", "Mon, 25 Aug 2026 06:00:00 GMT"),
        ("Phase 3 HARMONi-2 topline: ivonescimab met primary endpoint on PFS", "Mon, 25 Aug 2026 06:30:00 GMT"),
        ("Analyst raises Akeso price target to HK$120", "Mon, 25 Aug 2026 07:00:00 GMT"),
        ("Old news from last week about approval", "Mon, 10 Aug 2026 07:00:00 GMT"),
    ]
    hits = [{"title": t, "pubDate": d, "source": "test", "link": ""} for t, d in samples]
    kept, stats = filter_material(hits)
    print("stats:", stats)
    for k in kept:
        print(f"[{k['category_label']}] {k['title']} (折叠 {k['dup_count']} 条)")
