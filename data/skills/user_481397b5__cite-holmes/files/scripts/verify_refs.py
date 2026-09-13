#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_refs.py — cite-holmes skill 的引用机械验证器。

对研究引用清单做机器可判定的检查（可达性 / 域名权威度 / 字段完整性 / 去重），
输出五态判定报告（Markdown + JSON）。语义验证（来源是否真的支持论断）由模型
在研究流程中完成，本脚本不做语义判断。

五态：
  verified     可达 + 权威层(official/journal/preprint/media) + 字段完整
  partial      可达，但社区/博客层来源，或必填字段缺失
  unreachable  404/超时/反爬（needs_human_check，≠ 不存在）
  invalid      无 URL/DOI 或格式错误
  unverified   --offline 或跳过检查

纯标准库，跨平台（win32/linux/darwin），控频访问。
用法：
  python verify_refs.py --refs research_refs.json --out verify_report.md
  python verify_refs.py --claims '[{"title":"...","url":"https://...","source":"X","year":2026}]'
  python verify_refs.py --refs refs.json --offline        # 不联网，仅结构检查
  python verify_refs.py --refs refs.json --strict         # unreachable/invalid 视为失败(CI 用)
  python verify_refs.py --refs refs.json --profile medical # 医学信源预设(期刊层域名扩展+社区层降级警示)
  python verify_refs.py --refs refs.json --export bibtex,csv # 导出verified-only参考文献(bibtex)+全量台账(csv)

引用字段支持 url / doi / pmid 三选一（pmid 自动解析为 PubMed 页面），去重覆盖 URL+DOI+PMID。
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse, urlunparse

VERSION = "1.3.0"

# ---------------- CiteScore 置信度评分（v1.3.0） ----------------
# 五态加权：verified +10 / partial +4 / unreachable 0 / unverified -2 / invalid -8
# 归一化到 0-100，等级 A(>=85) B(70-84) C(50-69) D(<50)
SCORE_WEIGHTS = {"verified": 10, "partial": 4, "unreachable": 0,
                 "unverified": -2, "invalid": -8}


def compute_scorecard(results: list) -> dict:
    counts = {v: sum(1 for r in results if r["verdict"] == v)
              for v in SCORE_WEIGHTS}
    n = len(results)
    raw = sum(SCORE_WEIGHTS[v] * c for v, c in counts.items())
    score = round(100 * max(raw, 0) / (10 * n)) if n else 0
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D"
    return {"score": score, "grade": grade, "total": n,
            "counts": counts, "weights": SCORE_WEIGHTS}

# ---------------- 输出编码（Windows GBK 控制台兜底） ----------------
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

# ---------------- 域名权威度分层 ----------------
# 自上而下首个命中者生效；未命中默认 blog。
TIER_RULES = [
    ("official", [
        r"\.gov(\.[a-z]{2})?$", r"\.edu(\.[a-z]{2})?$", r"\.gov\.cn$", r"\.edu\.cn$",
        r"^docs\.", r"^developer\.", r"^documentation\.", r"^support\.",
        r"^www\.anthropic\.com$", r"^openai\.com$", r"^www\.nature\.com$",
        r"^www\.nejm\.org$", r"^www\.who\.int$", r"^www\.fda\.gov$",
        r"^www\.ema\.europa\.eu$", r"^arxiv\.org$", r"^www\.thelancet\.com$",
        r"^jamanetwork\.com$", r"^pubmed\.ncbi\.nlm\.nih\.gov$", r"^doi\.org$",
        r"^www\.sciencedirect\.com$", r"^link\.springer\.com$", r"^ieeexplore\.ieee\.org$",
        r"^www\.stats\.gov\.cn$", r"^www\.nhc\.gov\.cn$",
    ]),
    ("journal", [
        r"^pubmed\.ncbi\.nlm\.nih\.gov$", r"^doi\.org$", r"^journals?\.",
        r"^academic\.", r"^scholar\.", r"^kns\.", r"^oa\.cqvip\.com$", r"^yiigle\.com$",
    ]),
    ("preprint", [r"^arxiv\.org$", r"^biorxiv\.org$", r"^medrxiv\.org$", r"^ssrn\.com$", r"^chemrxiv\.org$"]),
    ("media", [
        r"^www\.reuters\.com$", r"^apnews\.com$", r"^www\.bbc\.", r"^www\.nytimes\.com$",
        r"^www\.bloomberg\.com$", r"^www\.ft\.com$", r"^www\.economist\.com$",
        r"^news\.yahoo\.com$", r"^www\.thepaper\.cn$", r"^www\.caixin\.com$",
        r"^www\.jiemian\.com$", r"^36kr\.com$", r"^www\.infoq\.cn$", r"^techcrunch\.com$",
        r"^www\.theverge\.com$", r"^arstechnica\.com$", r"^www\.wired\.com$",
    ]),
    ("community", [
        r"^github\.com$", r"^stackoverflow\.com$", r"^en\.wikipedia\.org$",
        r"^zh\.wikipedia\.org$", r"^www\.zhihu\.com$", r"^zhuanlan\.zhihu\.com$",
        r"^stackexchange\.com$", r"^www\.reddit\.com$", r"^news\.ycombinator\.com$",
        r"^www\.v2ex\.com$", r"^segmentfault\.com$", r"^juejin\.cn$",
    ]),
    ("social", [
        r"(^|\.)x\.com$", r"(^|\.)twitter\.com$", r"(^|\.)weibo\.com$", r"(^|\.)t\.me$",
        r"(^|\.)facebook\.com$", r"(^|\.)youtube\.com$", r"(^|\.)bilibili\.com$",
        r"(^|\.)douyin\.com$", r"(^|\.)xiaohongshu\.com$", r"(^|\.)medium\.com$",
    ]),
]
TRUSTED_TIERS = {"official", "journal", "preprint", "media"}

# ---------------- 医学信源预设（--profile medical 时并入 journal 层） ----------------
MEDICAL_JOURNAL_PATTERNS = [
    r"\.cochranelibrary\.com$", r"^bestpractice\.bmj\.com$", r"^www\.bmj\.com$",
    r"^www\.embase\.com$", r"^clinicaltrials\.gov$", r"^www\.chinacdc\.cn$",
    r"^www\.cdc\.gov$", r"^www\.nmpa\.gov\.cn$", r"^www\.nice\.org\.uk$",
    r"\.wanfangdata\.com\.cn$", r"^guide\.medlive\.cn$", r"^rs\.yiigle\.com$",
    r"^(www\.)?chictr\.org\.cn$",
]

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
PMID_RE = re.compile(r"^\d{6,9}$")
REQUIRED_FIELDS = ("title", "url", "source", "year")


def classify_tier(url: str, medical: bool = False) -> str:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return "unknown"
    for tier, patterns in TIER_RULES:
        for pat in patterns:
            if re.search(pat, host):
                return tier
    if medical:
        for pat in MEDICAL_JOURNAL_PATTERNS:
            if re.search(pat, host):
                return "journal"
    return "blog"


def normalize_url(url: str) -> str:
    p = urlparse(url.strip())
    return urlunparse((p.scheme.lower(), (p.netloc or "").lower(), p.path.rstrip("/"),
                       "", "", ""))


PUBMED_URL_RE = re.compile(r"^https?://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/?$")


def pubmed_pmid_exists(pmid: str, timeout: float) -> tuple:
    """经 NCBI E-utilities 核实 PMID 真实存在。

    PubMed 网页对不存在的 PMID 也返回 2xx/203（且带反爬壳页），HTTP 状态码
    无法区分真假——AI 编造的 PMID 必须靠 API 核实才能抓住。
    返回 (exists, note)。
    """
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
         f"?db=pubmed&id={pmid}&retmode=json")
    try:
        req = urllib.request.Request(
            u, headers={"User-Agent": "cite-holmes/1.1; +verified-deep-research"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            j = json.loads(resp.read().decode("utf-8", "ignore"))
        res = j.get("result") or {}
        item = res.get(str(pmid)) or {}
        if item.get("error") or str(pmid) not in (res.get("uids") or []):
            return False, "PMID 在 PubMed 不存在（E-utilities 核实）→ 疑似编造引用"
        return True, "PMID 经 E-utilities 核实存在"
    except Exception as e:
        return True, f"E-utilities 校验失败（{type(e).__name__}），按可达处理"


def check_url(url: str, timeout: float) -> tuple:
    """返回 (reachable, status, note)。reachable 以 2xx/3xx/429(反爬) 计。"""
    req = urllib.request.Request(url, method="HEAD", headers={
        "User-Agent": "Mozilla/5.0 (compatible; cite-holmes/1.0; +verified-deep-research)",
        "Accept": "*/*",
    })
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
    for method in ("HEAD", "GET"):
        try:
            req.method = method
            with opener.open(req, timeout=timeout) as resp:
                return True, resp.status, f"{method} {resp.status}"
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue  # 站点拒绝 HEAD，降级 GET 重试
            if e.code == 429:
                return True, 429, "HTTP 429（反爬限流，站点实际存在）"
            return False, e.code, f"HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            if method == "HEAD":
                continue
            return False, None, f"{type(e).__name__}: {e}"[:120]
    return False, None, "HEAD/GET 均失败"


def missing_fields(ref: dict) -> list:
    miss = [f for f in REQUIRED_FIELDS if not ref.get(f)]
    if "url" in miss and (
            (ref.get("doi") and DOI_RE.match(str(ref["doi"]).strip())) or
            (ref.get("pmid") and PMID_RE.match(str(ref["pmid"]).strip()))):
        miss.remove("url")
    return miss


def ref_to_url(ref: dict) -> str:
    """url → doi → pmid 三级解析，返回最终可检查的 URL。"""
    url = (ref.get("url") or "").strip()
    if url:
        return url
    doi = (ref.get("doi") or "").strip()
    if doi and DOI_RE.match(doi):
        return f"https://doi.org/{doi}"
    pmid = str(ref.get("pmid") or "").strip()
    if pmid and PMID_RE.match(pmid):
        return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    return ""


def verify_one(ref: dict, idx: int, offline: bool, timeout: float, medical: bool = False) -> dict:
    out = {"index": idx, "title": ref.get("title") or "(无标题)", "url": ref.get("url") or "",
           "doi": str(ref.get("doi") or "").strip(), "pmid": str(ref.get("pmid") or "").strip(),
           "source": ref.get("source") or "", "year": ref.get("year"),
           "tier": ref.get("tier") or "", "semantic": ref.get("semantic", ""),
           "verdict": "unverified", "http_status": None, "note": "", "needs_human_check": False}

    pmid = out["pmid"]
    url = ref_to_url(ref)
    if not url:
        out.update(verdict="invalid",
                   note="缺少 url 且无可解析的 doi/pmid" +
                        ("（pmid 须为 6-9 位数字）" if pmid else ""))
        return out
    if not re.match(r"^https?://", url):
        out.update(verdict="invalid", note=f"url 非 http(s) 格式: {url[:60]}")
        return out

    if not out["tier"]:
        out["tier"] = classify_tier(url, medical)
    out["url"] = url
    if medical and out["tier"] in ("community", "social", "blog"):
        out["note"] = "医学模式：社区/社交/博客层来源不得支撑医学结论（仅作线索）"

    if offline:
        out["note"] = (out["note"] + "；" if out["note"] else "") + "offline 模式未做可达性检查"
    else:
        reachable, status, note = check_url(url, timeout)
        out["http_status"] = status
        out["note"] = (out["note"] + "；" if out["note"] else "") + note
        if not reachable:
            out.update(verdict="unreachable", needs_human_check=True,
                       note=(out["note"] + "；" if out["note"] else "") + "可能反爬/临时故障，不等于不存在")
            return out
        m = PUBMED_URL_RE.match(url)
        if m:
            pmid_ok, pmid_note = pubmed_pmid_exists(m.group(1), timeout)
            if not pmid_ok:
                out.update(verdict="invalid", needs_human_check=True,
                           note=(out["note"] + "；" if out["note"] else "") + pmid_note)
                return out
            out["note"] = (out["note"] + "；" if out["note"] else "") + pmid_note

    miss = missing_fields(ref)
    if out["tier"] in TRUSTED_TIERS and not miss:
        out["verdict"] = "verified"
    else:
        why = []
        if out["tier"] not in TRUSTED_TIERS:
            why.append(f"来源层级为 {out['tier']}（非权威层）")
        if miss:
            why.append(f"缺字段 {','.join(miss)}")
        out["verdict"] = "partial"
        out["note"] = (out["note"] + "；" if out["note"] else "") + "；".join(why)
    return out


def mark_duplicates(results: list) -> None:
    seen = {}
    kind_zh = {"url": "URL", "doi": "DOI", "pmid": "PMID"}
    for r in results:
        keys = []
        if r.get("url"):
            keys.append(("url", normalize_url(r["url"])))
        if r.get("doi"):
            keys.append(("doi", r["doi"].lower()))
        if r.get("pmid"):
            keys.append(("pmid", r["pmid"]))
        hit = next(((k, seen[v]) for k, v in keys if v in seen), None)
        if hit:
            kind, first = hit
            r["note"] = (r["note"] + "；" if r["note"] else "") + f"与 #{first} 重复（同{kind_zh[kind]}）"
            if r["verdict"] == "verified":
                r["verdict"] = "partial"
        else:
            for _, v in keys:
                seen[v] = r["index"]


VERDICT_ZH = {"verified": "✅ verified", "partial": "🟡 partial", "unreachable": "⚠️ unreachable",
              "invalid": "❌ invalid", "unverified": "⏸ unverified"}


def export_bibtex(results: list, path: str) -> int:
    """仅导出 verified 条目为 BibTeX（可直接导入论文参考文献管理器）。返回条数。"""
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for r in results:
            if r["verdict"] != "verified":
                continue
            n += 1
            title = str(r.get("title") or "untitled").strip()
            year = r.get("year") or "n.d."
            words = re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", title)[:3]
            key = ("holmes" + str(year) + "".join(words))[:42] or f"ref{r['index']}"
            fields = [f"  title = {{{title}}}"]
            if r.get("source"):
                fields.append(f"  journal = {{{r['source']}}}")
            if r.get("year"):
                fields.append(f"  year = {{{r['year']}}}")
            if r.get("url"):
                fields.append(f"  url = {{{r['url']}}}")
            if r.get("doi"):
                fields.append(f"  doi = {{{r['doi']}}}")
            notes = ["cite-holmes verified"]
            if r.get("pmid"):
                notes.append(f"PMID: {r['pmid']}")
            fields.append("  note = {{{}}}".format("; ".join(notes)))
            f.write("@misc{" + key + ",\n" + ",\n".join(fields) + "}\n\n")
    return n


def export_csv(results: list, path: str) -> None:
    """全量审计台账 CSV（utf-8-sig，Excel 直接打开不乱码）。"""
    cols = ["index", "title", "verdict", "tier", "http_status", "needs_human_check",
            "year", "source", "url", "doi", "pmid", "note"]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow({c: r.get(c, "") for c in cols})


def render_md(results: list, offline: bool) -> str:
    sc = compute_scorecard(results)
    c = sc["counts"]
    lines = [
        "# 引用机械验证报告",
        f"- 验证器：verify_refs.py v{VERSION} · 模式：{'offline（未联网）' if offline else 'online'}",
        "",
        "## CiteScore 置信度评分",
        f"### **{sc['score']} / 100 · {sc['grade']} 级**",
        "",
        f"- 总计 {sc['total']} 条：✅verified {c['verified']} · 🟡partial {c['partial']} · "
        f"⚠️unreachable {c['unreachable']} · ❌invalid {c['invalid']} · ⏸unverified {c['unverified']}",
        "- 计分：verified +10 / partial +4 / unreachable 0 / unverified −2 / invalid −8，"
        "满分 = 10 × 条数，归一化 0-100",
        "",
        "| # | 标题 | 层级 | HTTP | 判定 | 说明 |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        title = str(r["title"]).replace("|", "\\|")[:48]
        lines.append(f"| {r['index']} | {title} | {r['tier']} | "
                     f"{r['http_status'] or '-'} | {VERDICT_ZH[r['verdict']]} | {r['note'] or '-'} |")
    flagged = [r for r in results if r["needs_human_check"] or r["verdict"] in ("invalid", "unverified")]
    if flagged:
        lines += ["", "## 待人工复核", ""]
        for r in flagged:
            lines.append(f"- #{r['index']} {r['title']} → {r['verdict']}：{r['note']}")
    lines += ["", "## 判定说明", "",
              "- `verified`：可达 + 权威层(official/journal/preprint/media) + 字段完整 —— 可支撑正文结论",
              "- `partial`：可达但社区/博客层来源，或字段缺失 —— 降级使用，结论需注明",
              "- `unreachable`：抓取失败（404/超时/反爬）—— 不等于不存在，需人工打开复核",
              "- `invalid`：无 URL/DOI 或格式错误 —— 不得进入报告",
              "- 语义验证（来源是否支持论断）由模型完成，本报告只覆盖机械层", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="deep-research 引用机械验证器（五态判定）")
    ap.add_argument("--refs", help="research_refs.json 路径")
    ap.add_argument("--claims", help="内联 JSON 引用数组（同 --refs 的 schema）")
    ap.add_argument("--out", default="verify_report.md", help="Markdown 报告输出路径")
    ap.add_argument("--json-out", help="JSON 报告输出路径（默认 <out>.json）")
    ap.add_argument("--offline", action="store_true", help="不联网，仅结构/字段检查")
    ap.add_argument("--strict", action="store_true", help="unreachable/invalid 计为失败（exit 1）")
    ap.add_argument("--timeout", type=float, default=10.0, help="单 URL 超时秒数（默认 10）")
    ap.add_argument("--interval", type=float, default=1.0, help="请求间隔秒数（默认 1.0）")
    ap.add_argument("--profile", choices=["general", "medical"], default="general",
                    help="信源预设：medical=医学期刊层域名扩展(Cochrane/CTS/NMPA/CDC/万方等)+社区层降级警示")
    ap.add_argument("--export", help="附加导出，逗号分隔：bibtex（仅verified，可直接进论文）/ csv（全量审计台账）")
    args = ap.parse_args()
    medical = args.profile == "medical"

    if not args.refs and not args.claims:
        ap.error("需要 --refs 或 --claims 之一")
    try:
        refs = (json.loads(args.claims) if args.claims
                else json.load(open(args.refs, encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as e:
        print(f"❌ 读取引用清单失败：{e}", file=sys.stderr)
        return 2
    if not isinstance(refs, list) or not refs:
        print("❌ 引用清单须为非空 JSON 数组", file=sys.stderr)
        return 2

    results = []
    for i, ref in enumerate(refs, 1):
        if not isinstance(ref, dict):
            results.append({"index": i, "title": str(ref)[:48], "url": "", "doi": "", "pmid": "",
                            "source": "", "year": None, "tier": "-", "semantic": "", "verdict": "invalid",
                            "http_status": None, "note": "条目不是对象", "needs_human_check": False})
            continue
        r = verify_one(ref, i, args.offline, args.timeout, medical)
        results.append(r)
        print(f"[{i}/{len(refs)}] {VERDICT_ZH[r['verdict']]} {r['title'][:40]}")
        if not args.offline and i < len(refs) and args.interval > 0:
            time.sleep(args.interval)

    mark_duplicates(results)
    scorecard = compute_scorecard(results)
    md = render_md(results, args.offline)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)
    json_path = args.json_out or (args.out.rsplit(".", 1)[0] + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"version": VERSION, "profile": args.profile, "offline": args.offline,
                   "scorecard": scorecard, "results": results},
                  f, ensure_ascii=False, indent=2)
    print(f"CiteScore: {scorecard['score']}/100 ({scorecard['grade']} 级，{scorecard['total']} 条)")

    if args.export:
        base = args.out.rsplit(".", 1)[0] if "." in args.out else args.out
        for fmt in [x.strip().lower() for x in args.export.split(",") if x.strip()]:
            if fmt == "bibtex":
                p = base + ".bib"
                n = export_bibtex(results, p)
                print(f"导出：{p}（{n} 条 verified，可直接进论文）")
            elif fmt == "csv":
                p = base + ".csv"
                export_csv(results, p)
                print(f"导出：{p}（{len(results)} 条全量审计台账）")
            else:
                print(f"⚠️ 未知导出格式 {fmt}（支持 bibtex,csv）", file=sys.stderr)

    bad = [r for r in results if r["verdict"] in ("unreachable", "invalid")]
    print(f"\n报告：{args.out}\nJSON：{json_path}")
    if bad:
        print(f"⚠️ {len(bad)} 条 unreachable/invalid" + ("（strict 模式 → exit 1）" if args.strict else ""))
    return 1 if (args.strict and bad) else 0


def main_with_args(argv: list) -> int:
    """程序化调用入口（测试/其他脚本用）。argv 不含脚本名。"""
    old = sys.argv
    sys.argv = [sys.argv[0]] + list(argv)
    try:
        return main()
    finally:
        sys.argv = old


if __name__ == "__main__":
    sys.exit(main())
