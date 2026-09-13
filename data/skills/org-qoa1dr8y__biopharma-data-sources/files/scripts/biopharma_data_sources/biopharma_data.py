#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生物医药数据源模块 — ClinicalTrials.gov + FDA openFDA

用于港股/美股生物医药公司投资分析：管线 / 临床 / 审批 / 专利。
数据源（官方公开免费接口，无需向数据源申请 Key）：
  - ClinicalTrials.gov API v2 (NIH/NLM) — 全球临床试验注册库
  - openFDA (FDA) — Drugs@FDA 审批 + Orange Book 专利/独占期

（注：FINTRUST_API_KEY 是 Skill Hub 平台使用授权，与数据源 Key 无关）

登记：source_universe.json（维度：biopharma_clinical / biopharma_fda）

用法：
    from biopharma_data_sources.biopharma_data import get_clinical_trials, get_fda_drug
    trials = get_clinical_trials("zanubrutinib")
    drugs = get_fda_drug("BRUKINSA")
"""
import sys
from pathlib import Path

from .task_guard import retry_with_backoff  # noqa: E402
from . import fintrust_onboard as _fintrust  # noqa: E402

_fintrust.require_api_key()  # 模块级硬校验：CLI 运行与 import 调用均需 Key

CLINICALTRIALS_BASE = "https://clinicaltrials.gov/api/v2/studies"
OPENFDA_BASE = "https://api.fda.gov"
UA = {"User-Agent": "BiopharmaDataSources/1.1 (research contact: your-research@example.com)"}


@retry_with_backoff(max_retries=3, base_delay=2)
def _get_json(url, params=None, timeout=30):
    import requests
    r = requests.get(url, params=params, timeout=timeout, headers=UA)
    r.raise_for_status()
    return r.json()


# ── 本地缓存兜底（官方唯一源 → 最近成功缓存兜底） ────────────────────────────
import json as _json
CACHE_DIR = Path(__file__).parent / "data" / "biopharma_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_TTL = 3 * 86400  # 缓存 3 天（临床/审批/专利数据变化慢）


def _cached_call(name, fetch_fn, ttl=CACHE_TTL):
    """成功写缓存；失败读缓存（TTL内）兜底；无缓存则抛原始异常。

    生物医药数据源（ClinicalTrials/FDA/PubMed/Patents）均为官方唯一源，
    无第二免费源，本地缓存是唯一兜底。数据一旦收录变化极慢，缓存兜底 ≫ 完全缺失。
    """
    import time
    cache_file = CACHE_DIR / f"{name}.json"
    try:
        result = fetch_fn()
        try:
            cache_file.write_text(
                _json.dumps(result, ensure_ascii=False, default=str), encoding="utf-8")
        except Exception:
            pass
        return result
    except Exception:
        if cache_file.exists() and (time.time() - cache_file.stat().st_mtime) < ttl:
            try:
                return _json.loads(cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        raise


def get_clinical_trials(keyword, max_results=20):
    """搜索临床试验（按药物名 / 适应症 / 公司名 / NCT编号）。

    返回 list[dict]：nct_id / title / overall_status / phases /
    start_date / completion_date / sponsor
    """
    def _fetch():
        data = _get_json(CLINICALTRIALS_BASE, params={
            "query.term": keyword,
            "pageSize": max_results,
            "format": "json",
        })
        out = []
        for s in data.get("studies", []):
            ps = s.get("protocolSection", {})
            ident = ps.get("identificationModule", {})
            status = ps.get("statusModule", {})
            design = ps.get("designModule", {})
            sponsor = ps.get("sponsorCollaboratorsModule", {})
            out.append({
                "nct_id": ident.get("nctId"),
                "title": ident.get("briefTitle"),
                "overall_status": status.get("overallStatus"),
                "phases": design.get("phases", []),
                "start_date": (status.get("startDateStruct") or {}).get("date"),
                "completion_date": (status.get("completionDateStruct") or {}).get("date"),
                "sponsor": (sponsor.get("leadSponsor") or {}).get("name"),
            })
        return out
    return _cached_call(f"clinical_{keyword}_{max_results}", _fetch)


def get_trial_detail(nct_id):
    """单条临床试验完整详情（含入组标准、结局指标、干预组等）。"""
    return _get_json(f"{CLINICALTRIALS_BASE}/{nct_id}", params={"format": "json"})


def get_fda_drug(brand_name, limit=5):
    """查 FDA 药品审批信息（Drugs@FDA，按商品名）。

    返回 list[dict]：brand_name / active_ingredients / marketing_status /
    application_number / sponsor
    """
    def _fetch():
        data = _get_json(f"{OPENFDA_BASE}/drug/drugsfda.json", params={
            "search": f'products.brand_name:"{brand_name}"',
            "limit": limit,
        })
        out = []
        for r in data.get("results", []):
            for p in r.get("products", []):
                out.append({
                    "brand_name": p.get("brand_name"),
                    "active_ingredients": [ai.get("name") for ai in p.get("active_ingredients", [])],
                    "marketing_status": p.get("marketing_status"),
                    "application_number": p.get("application_number"),
                    "sponsor_name": (r.get("openfda") or {}).get("manufacturer_name"),
                })
        return out
    return _cached_call(f"fda_drug_{brand_name}_{limit}", _fetch)


def get_fda_orange_book(active_ingredient, limit=10):
    """查 Orange Book 橙皮书 — 药品批准 + 活性成分 + 市场状态。

    注意：openFDA Orange Book 端点不提供专利到期/独占期时间，
    专利到期需另从 FDA 橙皮书下载文件(ob.zip)或 USPTO/Google Patents 获取。
    返回 list[dict]：brand_name / active_ingredients / marketing_status /
    application_number / dosage_form / route
    """
    def _fetch():
        data = _get_json(f"{OPENFDA_BASE}/drug/orangebook.json", params={
            "search": f'products.active_ingredients.name:"{active_ingredient.upper()}"',
            "limit": limit,
        })
        out = []
        for r in data.get("results", []):
            for p in r.get("products", []):
                out.append({
                    "brand_name": p.get("brand_name"),
                    "active_ingredients": [ai.get("name") for ai in p.get("active_ingredients", [])],
                    "marketing_status": p.get("marketing_status"),
                    "application_number": p.get("application_number"),
                    "dosage_form": p.get("dosage_form"),
                    "route": p.get("route"),
                })
        return out
    return _cached_call(f"fda_orangebook_{active_ingredient}_{limit}", _fetch)


EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_pubmed(keyword, max_results=20):
    """搜索 PubMed 文献（NCBI E-utilities esearch），返回 PMID 列表。

    用途：生物医药最新临床数据/研究常首发于 PubMed，是 ASCO/ASH 之外的关键线索。
    """
    data = _get_json(f"{EUTILS_BASE}/esearch.fcgi", params={
        "db": "pubmed",
        "term": keyword,
        "retmode": "json",
        "retmax": max_results,
    })
    return data.get("esearchresult", {}).get("idlist", [])


def get_pubmed_summaries(pmids):
    """获取文献摘要（esummary），返回 list[dict]：pmid/title/journal/pubdate/authors。"""
    if not pmids:
        return []
    ids = ",".join(str(p) for p in pmids)
    data = _get_json(f"{EUTILS_BASE}/esummary.fcgi", params={
        "db": "pubmed",
        "id": ids,
        "retmode": "json",
    })
    result = data.get("result", {})
    out = []
    for pid in pmids:
        r = result.get(str(pid))
        if r and isinstance(r, dict):
            out.append({
                "pmid": str(pid),
                "title": r.get("title"),
                "journal": r.get("fulljournalname"),
                "pubdate": r.get("pubdate"),
                "authors": [a.get("name") for a in r.get("authors", [])[:3]],
            })
    return out


GPATENTS_BASE = "https://patents.google.com/xhr/query"


def get_patents(query, max_results=20):
    """查专利（Google Patents，免费无 key，覆盖全球专利族）。

    返回 list[dict]：patent_number / title / assignee / priority_date /
    grant_date / active_countries（专利在哪些国家仍有效，判断护城河/仿制风险）。
    """
    def _fetch():
        data = _get_json(GPATENTS_BASE, params={"url": f"q={query}"})
        out = []
        for cluster in data.get("results", {}).get("cluster", []):
            for r in cluster.get("result", []):
                p = r.get("patent", {})
                fm = (p.get("family_metadata", {}).get("aggregated", {})
                      .get("country_status", []))
                active = [c.get("country_code") for c in fm
                          if (c.get("best_patent_stage") or {}).get("state") == "ACTIVE"]
                out.append({
                    "patent_number": p.get("publication_number"),
                    "title": p.get("title"),
                    "assignee": p.get("assignee"),
                    "priority_date": p.get("priority_date"),
                    "grant_date": p.get("grant_date"),
                    "active_countries": active,
                })
                if len(out) >= max_results:
                    return out
        return out
    return _cached_call(f"patents_{query}_{max_results}", _fetch)


EMA_XLSX_URL = ("https://www.ema.europa.eu/en/documents/report/"
                "medicines-output-medicines-report_en.xlsx")
EMA_CACHE = Path.home() / ".cache" / "biopharma_data_sources" / "ema_medicines.xlsx"
EMA_CACHE_TTL = 7 * 86400  # 缓存 7 天


def _load_ema_df():
    """下载或读缓存 EMA 药品数据（EPAR Excel，官方，约 2700 条）。"""
    import time
    import pandas as pd
    if EMA_CACHE.exists() and (time.time() - EMA_CACHE.stat().st_mtime) < EMA_CACHE_TTL:
        return pd.read_excel(EMA_CACHE, header=8)
    import requests
    r = requests.get(EMA_XLSX_URL, headers=UA, timeout=90)
    r.raise_for_status()
    EMA_CACHE.parent.mkdir(parents=True, exist_ok=True)
    EMA_CACHE.write_bytes(r.content)
    return pd.read_excel(EMA_CACHE, header=8)


def get_ema_drugs(active_substance, limit=20):
    """查 EMA 批准药品（欧洲公共评估报告 EPAR，按活性成分模糊匹配）。

    返回 list[dict]：name / active_substance / inn / status /
    therapeutic_area / ema_number
    """
    df = _load_ema_df()
    mask = df["Active substance"].str.contains(
        active_substance, case=False, na=False)
    sub = df[mask].head(limit)
    out = []
    for _, row in sub.iterrows():
        out.append({
            "name": row.get("Name of medicine"),
            "active_substance": row.get("Active substance"),
            "inn": row.get("International non-proprietary name (INN) / common name"),
            "status": row.get("Medicine status"),
            "therapeutic_area": row.get("Therapeutic area (MeSH)"),
            "ema_number": row.get("EMA product number"),
        })
    return out


if __name__ == "__main__":
    from .fintrust_onboard import require_api_key
    require_api_key()
    import json
    kw = sys.argv[1] if len(sys.argv) > 1 else "zanubrutinib"
    print(f"=== 临床试验: {kw} ===")
    for t in get_clinical_trials(kw, max_results=5):
        print(json.dumps(t, ensure_ascii=False))
