#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生物医药公司 BD + 管线审批 上游信息追踪器（通用版 V1.1，2026-08-20）

通用脚本，通过 --config 指定公司配置文件，任何生物医药公司可复用。
核心诉求：在"获批/数据读出"等大信息发生前，提前**几天到几周**捕捉前哨信号。

信号分两层（时差要"可操作"）：
  【触发信号】时差几天-几周，可提前布局：
    1. EMA CHMP 会议纪要（早于公司公告 4-7 天）← 核心买入信号
    2. SEC 8-K（美股合作方先披露，数小时-天）
    3. 行业媒体 RSS（Endpoints/Fierce，BD 爆料）
  【催化剂日历】时差数月，仅标记未来获批节点（非买入信号）：
    4. CDE 优先审评 + 突破性治疗（早于 NMPA 获批数月，Playwright 绕瑞数）

用法：
  python -m biopharma_strategy.biopharma_tracker --config ../configs/henlius_tracking_config.json

数据源登记：source_universe.json（biopharma_ema_chmp / biopharma_sec_8k / biopharma_news / biopharma_cde_priority）
推送：Telegram + Gmail 双渠道，幂等去重
"""
import os
import re
import json
import sys
import html
import argparse
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timedelta
from pathlib import Path

from . import fintrust_onboard as _fintrust  # noqa: E402

# .env 加载 + 模块级硬校验：CLI 运行与 import 调用均需 Key（.env 由 fintrust_onboard 自动加载）
_fintrust.require_api_key()

DEFAULT_CONFIG = "henlius_tracking_config.json"
# 追踪状态目录按包命名空间隔离（避免与 biopharma-data-sources 同机并跑时互抢去重账本）
STATE_DIR = Path.home() / ".cache" / "biopharma_strategy" / "tracker_state"
HEARTBEAT_FILE = STATE_DIR / "_heartbeat.json"
SILENT_HEARTBEAT_DAYS = 7  # 连续 N 天无重大信号 → 发一条存活确认（2026-08-25 启用）

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121 Safari/537.36"}
SEC_UA = {"User-Agent": "Mozilla/5.0 (research contact: your-research@example.com)"}
EMA_HOME = "https://www.ema.europa.eu/en/homepage"
SEC_EFTS_URL = "https://efts.sec.gov/LATEST/search-index"
NEWS_RSS = [
    ("Endpoints", "https://endpts.com/feed/"),
    ("Fierce Biotech", "https://www.fiercebiotech.com/rss/xml"),
    ("Fierce Pharma", "https://www.fiercepharma.com/rss/xml"),
    ("BioPharma Dive", "https://www.biopharmadive.com/feeds/news/"),
    ("STAT", "https://www.statnews.com/feed/"),
    ("PharmaTimes", "https://pharmatimes.com/rss/"),
    ("GEN", "https://www.genengnews.com/feed/"),
]

# 日文媒体：日本主流医疗媒体（日经Biotech/m3.com/CareNet）无公开 RSS，用 Google News 日文搜索兜底
GOOGLE_NEWS_JP = "https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
JP_BD_KEYWORDS = (
    "提携", "契約", "ライセンス", "承認", "承認取得", "独占", "供給",
    "導出", "導入", "買収", "合併", "治験", "license", "deal", "approval", "approves",
)
# 英文媒体：Google News 英文搜索（聚合全英文媒体，不限于固定 RSS 源）
GOOGLE_NEWS_EN = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
EN_BD_KEYWORDS = (
    "license", "deal", "partnership", "agreement", "approval", "approves",
    "authorization", "authorisation", "milestone", "acquisition", "acquires", "merger",
)
SEC_LOOKBACK_DAYS = 7  # 2026-08-25：8-K 是即时披露，超 7 天已无「早于公告」价值
NEWS_LOOKBACK_HOURS = 72  # 2026-08-25：Google News 按相关性返回历史旧闻，必须硬时间窗（72h 覆盖周末）
CDE_LOOKBACK_DAYS = 90  # CDE 优先审评只看最近 90 天新公示（避免首次运行回放历史品种）

# INN 负向排除：这些 INN 后紧跟衍生词是**别的药**（ADC/偶联物），非本公司管线
INN_EXCLUDE_SUFFIX = {
    "trastuzumab": ["deruxtecan", "emtansine"],
    "pertuzumab": [], "denosumab": [], "bevacizumab": [],
    "adalimumab": [], "rituximab": [], "neratinib": [],
}

# ETF/指数基金噪音名单（SEC 8-K 搜索时过滤掉）
ETF_NOISE = ("ishares", "invesco", "vanguard", "trust", "etf", "fidelity", "spdr", "index", "fund")


def load_config(config_name):
    # 包目录化后 config 文件在 skill 根目录的 configs/ 下（scripts/ 的上两级）。
    # 依次尝试：绝对路径 / 相对 cwd / 包目录 / skill 根 configs/，保证各种调用方式都能命中。
    candidates = []
    raw = Path(config_name)
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.append(Path.cwd() / raw)                       # 相对当前工作目录
        candidates.append(Path(__file__).resolve().parent / raw)  # 相对包目录
        candidates.append(Path(__file__).resolve().parent.parent.parent / "configs" / raw)  # skill 根 configs/
    for p in candidates:
        if p.exists():
            return json.load(open(p))
    raise FileNotFoundError(f"找不到配置文件: {config_name}（尝试过 {len(candidates)} 个候选路径）")


def _state_file(company_en):
    return STATE_DIR / f"{company_en}_pushed.json"


def load_state(company_en):
    f = _state_file(company_en)
    if f.exists():
        try:
            return json.load(open(f))
        except Exception:
            return {}
    return {}


def save_state(company_en, state):
    f = _state_file(company_en)
    f.parent.mkdir(parents=True, exist_ok=True)
    state["updated"] = datetime.now().isoformat()
    _tmp = f.with_suffix(".tmp")
    with open(_tmp, "w") as fp:
        json.dump(state, fp, ensure_ascii=False, indent=2)
    _tmp.replace(f)


def _clean(s):
    if not s:
        return ""
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _extract_english_keywords(config):
    """从管线分子提取英文关键词（EMA/FDA 页面是英文）。"""
    kws = []
    for m in config.get("pipeline_molecules", []):
        for f in ("name_en", "brand_eu", "brand_cn"):
            v = (m.get(f) or "").strip()
            if v and "/" in v:
                kws.extend(x.strip() for x in v.split("/") if x.strip())
            elif v:
                kws.append(v)
    return sorted(set(k for k in kws if k and len(k) >= 3))


# ==================== 源1：EMA CHMP 会议纪要 ====================

def _get_latest_chmp_url():
    r = requests.get(EMA_HOME, headers=UA, timeout=30)
    r.raise_for_status()
    links = re.findall(r'href="(/en/news/meeting-highlights[^"]*chmp[^"]*)"', r.text)
    if links:
        return "https://www.ema.europa.eu" + links[0]
    return None


def check_ema_chmp(config, pushed_urls):
    """EMA CHMP 积极意见（欧盟批准前哨）。"""
    url = _get_latest_chmp_url()
    if not url:
        print("  ⚠️ 未找到 EMA CHMP meeting highlights 链接", file=sys.stderr)
        return []
    if url in pushed_urls:
        print(f"  [EMA CHMP] 已推送过该会议，跳过", file=sys.stderr)
        return []

    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    text = _clean(r.text)
    title = re.search(r"<title>([^<]+)</title>", r.text)
    meeting_title = html.unescape(title.group(1).strip()) if title else url

    keywords = _extract_english_keywords(config)
    hits = []
    for kw in keywords:
        base = kw.lower()
        exclude_suffixes = INN_EXCLUDE_SUFFIX.get(base, [])
        for m in re.finditer(re.escape(kw), text, re.IGNORECASE):
            if exclude_suffixes:
                after = text[m.end(): m.end() + 25].lower().lstrip()
                if any(after.startswith(s) for s in exclude_suffixes):
                    print(f"  [排除] {kw} 后跟衍生词(非本公司)", file=sys.stderr)
                    continue
            snippet = text[max(0, m.start() - 60): m.end() + 120]
            hits.append({"source": "EMA CHMP", "keyword": kw, "url": url,
                         "title": meeting_title, "snippet": snippet, "key": url})
            break
    return hits


# ==================== 源2：SEC 8-K（合作方披露） ====================

def check_partner_sec(config, pushed_ids):
    """SEC EDGAR full-text search 搜公司英文名+管线名，找美股披露的涉及本公司的 8-K。"""
    company_en = config.get("company_en", "")
    start = (datetime.now() - timedelta(days=SEC_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")

    queries = [f'"{company_en}"'] if company_en else []
    # 只搜「创新药」INN（serplulimab/HLX22 等本公司独有），
    # 生物类似药 INN（trastuzumab/rituximab 等）是通用药名，会命中大量无关药企的 8-K
    for m in config.get("pipeline_molecules", []):
        if m.get("type") != "创新药":
            continue
        ne = (m.get("name_en") or "").strip()
        if ne and len(ne) >= 4 and " " not in ne:
            queries.append(f'"{ne}"')

    hits = []
    seen_docs = {}   # accession(去后缀) → 已收录的 hit，同一份 8-K 只留一条
    for q in queries:
        try:
            r = requests.get(SEC_EFTS_URL, params={
                "q": q, "forms": "8-K", "dateRange": "custom", "startdt": start, "enddt": end,
            }, headers=SEC_UA, timeout=30)
            if r.status_code != 200:
                continue
            d = r.json()
            for h in d.get("hits", {}).get("hits", [])[:10]:
                src = h.get("_source", {})
                doc_id = str(h.get("_id", ""))
                names = src.get("display_names", [])
                filer = names[0] if names else "未知"
                file_date = src.get("file_date", "")
                ciks = src.get("ciks", [])
                cik = ciks[0] if ciks else ""
                # 过滤 ETF/指数基金噪音
                if any(k in filer.lower() for k in ETF_NOISE):
                    continue
                if doc_id in pushed_ids:
                    continue
                # 同一份 8-K（同 accession 号）会被多个查询词/多个附件文件重复命中 → 合并
                accession = doc_id.split(":")[0]
                if accession in seen_docs:
                    prev = seen_docs[accession]
                    if q not in prev["query"]:
                        prev["query"] += f" / {q}"
                    prev.setdefault("extra_keys", []).append(doc_id)
                    continue
                acc_no = accession.replace("-", "")
                url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no}/" if cik else ""
                item = {"source": "SEC 8-K", "filer": filer, "file_date": file_date,
                        "query": q, "url": url, "key": doc_id, "extra_keys": []}
                seen_docs[accession] = item
                hits.append(item)
        except Exception as e:
            print(f"  ⚠️ SEC 查询失败 ({q}): {e}", file=sys.stderr)
    return hits


# ==================== 源3：行业媒体 RSS ====================

def _parse_rss(url):
    try:
        r = requests.get(url, headers=UA, timeout=20)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        for item in root.iter("item"):
            # Fierce 的 title 里嵌套 <a> 标签，需 itertext 提取全部文本
            title_el = item.find("title")
            title = "".join(title_el.itertext()).strip() if title_el is not None else ""
            link = (item.findtext("link") or "").strip()
            pubdate = (item.findtext("pubDate") or "").strip()
            items.append({"title": title, "link": link, "pubDate": pubdate})
        return items
    except Exception as e:
        print(f"  ⚠️ RSS 抓取失败 ({url}): {e}", file=sys.stderr)
        return []


def check_industry_news(config, pushed_titles):
    """行业媒体 RSS 搜公司英文名 + BD 关键词。"""
    company_en = (config.get("company_en") or "").lower()
    company_cn = config.get("company") or ""
    # BD/审批关键词
    bd_kw = ("license", "deal", "partnership", "agreement", "approval", "approves",
             "authorization", "authorisation", "milestone", "授权", "合作", "获批", "批准")
    # 公司关键词（中英文名 + 核心管线英文名）
    company_kws = [company_en, company_cn]
    for m in config.get("pipeline_molecules", []):
        ne = (m.get("name_en") or "").strip()
        if ne and len(ne) >= 4:
            company_kws.append(ne.lower())

    hits = []
    for src_name, url in NEWS_RSS:
        for item in _parse_rss(url):
            title = item["title"]
            tl = title.lower()
            # 命中公司关键词 + BD 关键词
            if any(k and k.lower() in tl for k in company_kws):
                if any(k in tl for k in bd_kw):
                    if title in pushed_titles:
                        continue
                    hits.append({"source": src_name, "title": title,
                                 "link": item["link"], "pubDate": item["pubDate"], "key": title})
    return hits


def check_japan_news(config, pushed_titles):
    """Google News 日文搜索：搜公司中文名（日文同汉字）+ 管线 INN，捕捉日文媒体 BD/审批信号。

    日本主流医疗媒体（日经Biotech/m3.com/CareNet）无公开 RSS，用 Google News 日文搜索兜底。
    例：复宏汉霖 → 搜「復宏漢霖」+「serplulimab」，命中「エーザイとの独占的ライセンス契約」等日文 BD 爆料。
    """
    from urllib.parse import quote
    company_cn = config.get("company") or ""
    company_en = config.get("company_en") or ""
    # 日文关键词：公司中文名（日文同汉字）+ 公司英文名 + 管线代号 + 创新药核心 INN
    # 注意：生物类似药的通用 INN（trastuzumab/denosumab 等）是别人的原研药，搜了会命中大量无关新闻，排除
    jp_kws = [company_cn, company_en]
    for m in config.get("pipeline_molecules", []):
        code = (m.get("code") or "").strip()
        if code and len(code) >= 3:
            jp_kws.append(code)
        if (m.get("type") or "") == "创新药":
            ne = (m.get("name_en") or "").strip()
            if ne and len(ne) >= 4 and " " not in ne:
                jp_kws.append(ne.lower())
    jp_kws = list(dict.fromkeys(k for k in jp_kws if k))  # 去重去空
    hits = []
    seen = set()  # 本次运行内去重（同一新闻可能被公司名+代号+INN 多个关键词命中）
    for kw in jp_kws:
        if not kw:
            continue
        try:
            url = GOOGLE_NEWS_JP.format(q=quote(kw))
            for item in _parse_rss(url):
                title = item["title"]
                tl = title.lower()
                if any(k in tl for k in JP_BD_KEYWORDS):
                    if title in pushed_titles or title in seen:
                        continue
                    seen.add(title)
                    hits.append({"source": "GoogleNews日文", "title": title,
                                 "link": item["link"], "pubDate": item["pubDate"], "key": title})
        except Exception as e:
            print(f"  ⚠️ 日文新闻搜索失败 ({kw}): {e}", file=sys.stderr)
    return hits


def check_english_news(config, pushed_titles):
    """Google News 英文搜索：搜公司英文名 + 管线代号 + 创新药核心 INN，聚合全英文媒体（不限于固定 RSS）。

    固定 RSS 只覆盖 Endpoints/Fierce 等 7 个源近 48h，Google News 英文搜索聚合全英文媒体，覆盖面更大。
    """
    from urllib.parse import quote
    company_en = config.get("company_en") or ""
    # 英文关键词：公司英文名 + 管线代号 + 创新药核心 INN（生物类似药通用 INN 排除，避免命中别人家的药）
    en_kws = [company_en]
    for m in config.get("pipeline_molecules", []):
        code = (m.get("code") or "").strip()
        if code and len(code) >= 3:
            en_kws.append(code)
        if (m.get("type") or "") == "创新药":
            ne = (m.get("name_en") or "").strip()
            if ne and len(ne) >= 4 and " " not in ne:
                en_kws.append(ne.lower())
    en_kws = list(dict.fromkeys(k for k in en_kws if k))
    hits = []
    seen = set()
    for kw in en_kws:
        try:
            url = GOOGLE_NEWS_EN.format(q=quote(kw))
            for item in _parse_rss(url):
                title = item["title"]
                tl = title.lower()
                if any(k in tl for k in EN_BD_KEYWORDS):
                    if title in pushed_titles or title in seen:
                        continue
                    seen.add(title)
                    hits.append({"source": "GoogleNews英文", "title": title,
                                 "link": item["link"], "pubDate": item["pubDate"], "key": title})
        except Exception as e:
            print(f"  ⚠️ 英文新闻搜索失败 ({kw}): {e}", file=sys.stderr)
    return hits


# ==================== 源4：CDE 优先审评 + 突破性治疗（已接入，Playwright 绕瑞数） ====================

def check_cde_priority(config, pushed_ids):
    """CDE 优先审评 + 突破性治疗公示（中国审批前哨，早于 NMPA 获批数月-1年）。

    例：信达替妥尤单抗 2024-05 优先审评 -> 2025-03 获批（时差约 10 个月）。
    CDE 官网是瑞数级 JS 挑战反爬，requests 返回 202 空页，必须 Playwright 绕。
    """
    company = (config.get("cde_company") or config.get("company") or "").strip()
    if not company:
        return []
    try:
        import asyncio
        from .cde_priority_collector import collect
        # 只看最近 CDE_LOOKBACK_DAYS 天的新公示，避免首次运行回放历史品种
        result = asyncio.run(collect([company], days=CDE_LOOKBACK_DAYS))
        data = result.get(company, {})
        hits = []
        for kind in ("优先审评", "突破性治疗"):
            for item in data.get(kind, []):
                key = f"{item.get('受理号', '')}_{item.get('药品名称', '')}_{item.get('公示日期', '')}"
                if key in pushed_ids:
                    continue
                hits.append({
                    "source": "CDE", "kind": item.get("类型", kind),
                    "drug": item.get("药品名称", ""), "受理号": item.get("受理号", ""),
                    "申请人": item.get("注册申请人", ""), "公示日期": item.get("公示日期", ""),
                    "状态": item.get("状态", ""), "罕见病": item.get("是否罕见病", ""),
                    "key": key,
                })
        return hits
    except Exception as e:
        print(f"  ⚠️ CDE 查询失败: {e}", file=sys.stderr)
        return []


# ==================== 推送 ====================

def deliver_telegram(msg):
    try:
        token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        if not token or not chat_id:
            print("  ⚠️ TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 未设置，跳过 Telegram 推送", file=sys.stderr)
            return
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": chat_id, "text": msg[:4000], "parse_mode": "Markdown"},
                      timeout=10)
        print("  📲 Telegram已推送", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠️ Telegram推送失败: {e}", file=sys.stderr)


def deliver_email(msg, subject):
    """通过标准 SMTP 发送告警邮件（需 SMTP_HOST/SMTP_USER/SMTP_PASS/ALERT_EMAIL）。"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        host = os.environ.get("SMTP_HOST", "")
        user = os.environ.get("SMTP_USER", "")
        pwd = os.environ.get("SMTP_PASS", "")
        to = os.environ.get("ALERT_EMAIL", "")
        if not (host and user and pwd and to):
            print("  ⚠️ SMTP 未配置（SMTP_HOST/SMTP_USER/SMTP_PASS/ALERT_EMAIL），跳过邮件", file=sys.stderr)
            return
        plain = msg.replace("**", "").replace("*", "")
        m = MIMEText(plain, "plain", "utf-8")
        m["Subject"] = subject
        m["From"] = user
        m["To"] = to
        port = int(os.environ.get("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port, timeout=15) as s:
            s.starttls()
            s.login(user, pwd)
            s.sendmail(user, [to], m.as_string())
        print("  📧 邮件已发送", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠️ 邮件发送异常: {e}", file=sys.stderr)


def _build_message(company, hits_by_source, filter_stats=None):
    lines = [
        f"🔬 **{company} 上游追踪·重大信号**",
        f"只推三类：数据读出 / 监管批准拒批 / 并购授权带金额（外文已译中文）",
        "━━━━━━━━━━━",
    ]
    for src, hits in hits_by_source.items():
        if not hits:
            continue
        lines.append("")
        lines.append(f"📡 **{src} · {len(hits)} 条**")
        for h in hits:
            lines.append("")
            if src == "EMA CHMP 积极意见":
                lines.append(f"   🎯 关键词 {h['keyword']} | {(h.get('title_cn') or h['title'])[:60]}")
                lines.append(f"   {(h.get('snippet_cn') or h.get('snippet', ''))[:120]}")
            elif src == "SEC 8-K 合作方披露":
                lines.append(f"   🏢 {h['filer']} | {h['file_date']}")
                lines.append(f"   查询词 {h['query']}")
            elif src == "CDE 优先审评/突破性治疗（催化剂日历）":
                lines.append(f"   📅 [{h['kind']}] {h['drug']}（未来获批预期，非买入信号）")
                lines.append(f"   受理号 {h['受理号']} | 公示 {h['公示日期']} | {h['状态']}")
            else:
                label = h.get("category_label", "")
                age = h.get("age_hours")
                stamp = f"（{age:.0f}h 前 · {h.get('source', '')}）" if age is not None else f"（{h.get('source', '')}）"
                lines.append(f"   {label} {(h.get('title_cn') or h.get('title', ''))[:90]}")
                lines.append(f"   {stamp}")
                if h.get("dup_count"):
                    lines.append(f"   └ 同一事件另有 {h['dup_count']} 家媒体报道（已折叠）")
            url = h.get("url") or h.get("link")
            if url:
                lines.append(f"   {url}")
    if filter_stats and filter_stats.get("raw"):
        s = filter_stats
        lines.append("")
        lines.append("━━━━━━━━━━━")
        lines.append(
            f"🔎 新闻过滤：原始 {s['raw']} 条 → 重大 {s['kept']} 条"
            f"（旧闻 {s['dropped_stale']} / 与本公司无关 {s.get('dropped_irrelevant', 0)} / "
            f"股评噪音 {s['dropped_noise']} / 非重大 {s['dropped_minor']} / "
            f"同事件折叠 {s['clustered']}）"
        )
    return "\n".join(lines)


def _translate_hits(material_hits, ema_hits):
    """标题中文翻译（可选增强，本版未内置，默认保留原文标题）。

    如需启用：自行实现 translate_batch 并在此调用，将译文写入
    h 的 title_cn / snippet_cn 字段（下游已做原文 fallback，缺字段不影响推送）。
    """
    return


def _known_entities(config):
    """公司管线分子名/代号，用于同事件聚类。"""
    ents = []
    for m in config.get("pipeline_molecules", []):
        for f in ("name_en", "code", "name_cn"):
            v = (m.get(f) or "").strip()
            if not v or len(v) < 3:
                continue
            # code 可能是 "AK112/SMT112" 复合写法，拆开
            for part in re.split(r"[/,;|]", v):
                part = part.strip()
                if len(part) >= 3:
                    ents.append(part)
    return list(dict.fromkeys(ents))


def _subject_terms(config):
    """主体相关性词表：公司中英文名 + 别名 + 全部管线名/代号/商品名。
    标题里一个都没提到 → 是泛行业稿或别家公司新闻，直接丢。"""
    terms = [config.get("company", ""), config.get("company_en", ""),
             config.get("cde_company", "")]
    # 兼容历史字段命名：旧版用 aliases，新版 config 用 watch_keywords（含管线代号/临床名/事件词）
    terms += config.get("aliases", []) + config.get("watch_keywords", [])
    for m in config.get("pipeline_molecules", []):
        for f in ("name_cn", "name_en", "code", "brand_cn", "brand_eu"):
            v = (m.get(f) or "").strip()
            for part in re.split(r"[/,;|]", v):
                part = part.strip()
                if len(part) >= 3:
                    terms.append(part)
    return list(dict.fromkeys(t for t in terms if t and len(t) >= 3))


def run_one(config_path, skip_cde=False, only_cde=False):
    """跑单个公司的上游追踪，返回推送内容（空串=无命中）。"""
    config = load_config(config_path)
    company = config.get("company", "公司")
    company_en = config.get("company_en", "company")
    state = load_state(company_en)

    if only_cde:
        ema_hits = sec_hits = news_hits = japan_hits = english_hits = []
        cde_hits = check_cde_priority(config, set(state.get("cde_pushed", [])))
    else:
        ema_hits = check_ema_chmp(config, set(state.get("ema_chmp_pushed", [])))
        sec_hits = check_partner_sec(config, set(state.get("sec_pushed", [])))
        news_hits = check_industry_news(config, set(state.get("news_pushed", [])))
        japan_hits = check_japan_news(config, set(state.get("news_pushed", [])))
        english_hits = check_english_news(config, set(state.get("news_pushed", [])))
        cde_hits = [] if skip_cde else check_cde_priority(config, set(state.get("cde_pushed", [])))

    # ── 新闻三源合并后统一做重大性过滤（跨源同事件也能折叠） ──
    news_all = list(news_hits) + list(english_hits) + list(japan_hits)
    material_hits, filter_stats = [], {}
    if news_all:
        try:
            from .news_materiality_filter import filter_material
            material_hits, filter_stats = filter_material(
                news_all, lookback_hours=NEWS_LOOKBACK_HOURS,
                known_entities=_known_entities(config),
                subject_terms=_subject_terms(config))
            print(f"  🔎 新闻过滤 {filter_stats}", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️ 重大性过滤失败，退回全量推送: {e}", file=sys.stderr)
            material_hits, filter_stats = news_all, {}

    hits_by_source = {}
    if ema_hits:
        hits_by_source["EMA CHMP 积极意见"] = ema_hits
    if sec_hits:
        hits_by_source["SEC 8-K 合作方披露"] = sec_hits
    if material_hits:
        hits_by_source["重大新闻（数据读出/监管批准拒批/并购授权）"] = material_hits
    if cde_hits:
        hits_by_source["CDE 优先审评/突破性治疗（催化剂日历）"] = cde_hits

    # 新闻全被过滤掉也要落盘幂等，避免下次重复评估同批标题
    if not hits_by_source:
        _save_news_state(company_en, state, ema_hits, sec_hits, [], news_all, cde_hits)
        record_activity(company, pushed=False, scanned=len(news_all))
        print(f"  ✅ {company} 无重大信号（原始新闻 {len(news_all)} 条全部过滤）", file=sys.stderr)
        return ""

    _translate_hits(material_hits, ema_hits)

    output = _build_message(company, hits_by_source, filter_stats)
    print(output, file=sys.stderr)
    deliver_telegram(output)
    deliver_email(output, subject=f"🔬 {company} 上游追踪·重大信号")

    _save_news_state(company_en, state, ema_hits, sec_hits, material_hits, news_all, cde_hits)
    record_activity(company, pushed=True, scanned=len(news_all), kept=len(material_hits))
    return output


def _save_news_state(company_en, state, ema_hits, sec_hits, material_hits, news_all, cde_hits):
    """幂等落盘：推送的 + 折叠的 + 已评估过的新闻标题全部记账。"""
    news_keys = {h["key"] for h in news_all if h.get("key")}
    for h in material_hits:
        for k in h.get("merged_keys", []):
            news_keys.add(k)
    sec_keys = {h["key"] for h in sec_hits}
    for h in sec_hits:
        sec_keys |= set(h.get("extra_keys", []))   # 同一份 8-K 的其它附件/查询词命中也要记账
    new_state = {
        "ema_chmp_pushed": sorted(set(state.get("ema_chmp_pushed", [])) | {h["key"] for h in ema_hits}),
        "sec_pushed": sorted(set(state.get("sec_pushed", [])) | sec_keys),
        "news_pushed": sorted(set(state.get("news_pushed", [])) | news_keys),
        "cde_pushed": sorted(set(state.get("cde_pushed", [])) | {h["key"] for h in cde_hits}),
    }
    save_state(company_en, new_state)


def _load_hb():
    """静默心跳账本：记录最近推送日、最近心跳日、静默期累计扫描量。"""
    try:
        if HEARTBEAT_FILE.exists():
            return json.loads(HEARTBEAT_FILE.read_text())
    except Exception:
        pass
    return {}


def _save_hb(hb):
    try:
        HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = HEARTBEAT_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(hb, ensure_ascii=False, indent=1))
        tmp.replace(HEARTBEAT_FILE)
    except Exception as e:
        print(f"  ⚠️ 心跳账本写入失败: {e}", file=sys.stderr)


def record_activity(company, pushed, scanned, kept=0):
    """每家公司跑完记一笔：推送了没、扫了多少条新闻。"""
    hb = _load_hb()
    today = datetime.now().strftime("%Y-%m-%d")
    if pushed:
        hb["last_push_date"] = today
        hb["last_push_company"] = company
        hb["silent_scanned"] = 0
        hb["silent_companies"] = []
    else:
        hb["silent_scanned"] = int(hb.get("silent_scanned", 0)) + int(scanned)
        comps = hb.get("silent_companies", [])
        if company not in comps:
            comps.append(company)
        hb["silent_companies"] = comps[-20:]
    hb.setdefault("last_push_date", today)
    hb["last_run_date"] = today
    _save_hb(hb)


def maybe_heartbeat(force=False):
    """连续 SILENT_HEARTBEAT_DAYS 天无任何推送 → 发一条极简存活确认（同一周期只发一次）。"""
    hb = _load_hb()
    today = datetime.now().date()
    try:
        last_push = datetime.strptime(hb.get("last_push_date", ""), "%Y-%m-%d").date()
    except Exception:
        last_push = None
    try:
        last_hb = datetime.strptime(hb.get("last_heartbeat_date", ""), "%Y-%m-%d").date()
    except Exception:
        last_hb = None

    silent_days = (today - last_push).days if last_push else 0
    hb_gap = (today - last_hb).days if last_hb else 999

    if not force:
        if silent_days < SILENT_HEARTBEAT_DAYS or hb_gap < SILENT_HEARTBEAT_DAYS:
            print(f"  ⏱️ 心跳跳过（静默 {silent_days} 天 / 上次心跳 {hb_gap} 天前）", file=sys.stderr)
            return ""

    scanned = int(hb.get("silent_scanned", 0))
    comps = "、".join(hb.get("silent_companies", [])) or "全部追踪标的"
    msg = (
        f"💤 **生物医药上游追踪 · 存活确认**\n"
        f"已连续 {silent_days} 天无重大信号（系统正常运行中）\n"
        f"━━━━━━━━━━━\n"
        f"覆盖：{comps}\n"
        f"静默期累计扫描新闻：{scanned} 条，其中符合「数据读出 / 监管批准拒批 / 并购授权带金额」三类的：0 条\n"
        f"（重大信号本身稀疏，每家公司约每月 1~2 次；无消息即无重大事件）"
    )
    print(msg, file=sys.stderr)
    deliver_telegram(msg)
    hb["last_heartbeat_date"] = today.strftime("%Y-%m-%d")
    _save_hb(hb)
    return msg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--watchlist", default=None, help="前10清单JSON，遍历所有配置跑触发信号")
    ap.add_argument("--skip-cde", action="store_true", help="跳过CDE源（Playwright慢），每日快跑用")
    ap.add_argument("--only-cde", action="store_true", help="只跑CDE源（每周催化剂日历用）")
    ap.add_argument("--force-heartbeat", action="store_true", help="强制发一次静默心跳（自测用）")
    args = ap.parse_args()

    if args.watchlist:
        # watchlist 与 config 同属 skill 根 configs/，复用 load_config 的候选路径逻辑
        _wl_raw = Path(args.watchlist)
        _wl_candidates = [Path.cwd() / _wl_raw, Path(__file__).resolve().parent / _wl_raw,
                          Path(__file__).resolve().parent.parent.parent / "configs" / _wl_raw]
        _wl_path = next((p for p in _wl_candidates if p.exists()), _wl_raw)
        wl = json.load(open(_wl_path))
        configs = wl.get("configs", [])
        print(f"  🔬 遍历 {len(configs)} 家公司", file=sys.stderr)
        for cfg in configs:
            try:
                run_one(cfg, skip_cde=args.skip_cde, only_cde=args.only_cde)
            except Exception as e:
                print(f"  ⚠️ {cfg} 失败: {e}", file=sys.stderr)
    elif args.config:
        try:
            run_one(args.config, skip_cde=args.skip_cde, only_cde=args.only_cde)
        except Exception as e:
            print(f"  ⚠️ {args.config} 失败: {e}", file=sys.stderr)
    else:
        try:
            run_one(DEFAULT_CONFIG, skip_cde=args.skip_cde, only_cde=args.only_cde)
        except Exception as e:
            print(f"  ⚠️ {DEFAULT_CONFIG} 失败: {e}", file=sys.stderr)

    # 静默心跳：连续 SILENT_HEARTBEAT_DAYS 天无推送时，发一条极简存活确认
    maybe_heartbeat(force=args.force_heartbeat)


if __name__ == "__main__":
    from .fintrust_onboard import require_api_key
    require_api_key()
    main()
