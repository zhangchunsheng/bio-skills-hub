#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pubmed_search.py — 基于 NCBI E-utilities 的 PubMed 检索与结构化解析。

仅依赖 Python 标准库（urllib / xml），无需 pip 安装，可在隔离环境中直接运行。
用于 pharmacy-research-intel skill 的"追踪第一线"与"文献检索"任务。

用法示例：
  python pubmed_search.py --query "pharmacogenomics AND anticancer" --days 90 --max 20
  python pubmed_search.py --query "drug-induced liver injury" --mindate 2024/01 --maxdate 2024/12 --max 50 --out md
  python pubmed_search.py --query "..." --sort date --out json > result.json

输出：
  - 默认 markdown（每条文献一段，含 PMID/DOI/作者/Mesh/摘要）
  - --out json：结构化 JSON 数组（便于进一步处理或绘图）
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "workbuddy-pharmacy-research-intel"


def _get(url, params, timeout=30):
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": TOOL})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def esearch(query, mindate, maxdate, retmax, sort, api_key):
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": str(retmax),
        "sort": sort,
        "tool": TOOL,
    }
    if api_key:
        params["api_key"] = api_key
    if mindate:
        params["datetype"] = "pdat"
        params["mindate"] = mindate
        params["maxdate"] = maxdate or date.today().strftime("%Y/%m/%d")
    data = json.loads(_get(EUTILS + "/esearch.fcgi", params))
    return data.get("esearchresult", {}).get("idlist", [])


def efetch(pmids, api_key):
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "xml",
        "tool": TOOL,
    }
    if api_key:
        params["api_key"] = api_key
    return _get(EUTILS + "/efetch.fcgi", params)


def _text(el, path):
    node = el.find(path)
    return node.text.strip() if node is not None and node.text else ""


def parse_article(art):
    mc = art.find("MedlineCitation")
    if mc is None:
        return None
    article = mc.find("Article")
    if article is None:
        return None

    pmid = _text(mc, "PMID")
    title = _text(article, "ArticleTitle")

    # 作者
    authors = []
    al = article.find("AuthorList")
    if al is not None:
        for a in al.findall("Author"):
            last = _text(a, "LastName")
            fore = _text(a, "ForeName")
            coll = _text(a, "CollectiveName")
            if last or fore:
                authors.append(f"{last} {fore}".strip())
            elif coll:
                authors.append(coll)

    # 期刊
    journal = ""
    j = article.find("Journal")
    if j is not None:
        journal = _text(j, "ISOAbbreviation") or _text(j, "Title")

    # 日期：优先 Article/ArticleDate，回退 Journal/JournalIssue/PubDate
    year = ""
    date_str = ""
    ad = article.find("ArticleDate")
    if ad is not None and _text(ad, "Year"):
        year = _text(ad, "Year")
        date_str = "/".join([_text(ad, "Year"), _text(ad, "Month"), _text(ad, "Day")]).strip("/")
    else:
        jp = article.find("Journal/JournalIssue/PubDate")
        if jp is not None:
            year = _text(jp, "Year")
            date_str = "/".join([_text(jp, "Year"), _text(jp, "Month"), _text(jp, "Day")]).strip("/")

    # 摘要（合并含 NlmCategory 的分段）
    abstract_parts = []
    ab = article.find("Abstract")
    if ab is not None:
        for at in ab.findall("AbstractText"):
            cat = at.attrib.get("NlmCategory", "")
            txt = (at.text or "").strip()
            if cat and txt:
                abstract_parts.append(f"[{cat}] {txt}")
            elif txt:
                abstract_parts.append(txt)
    abstract = " ".join(abstract_parts)

    # 文献类型
    pubtypes = []
    ptl = article.find("PublicationTypeList")
    if ptl is not None:
        for pt in ptl.findall("PublicationType"):
            if pt.text:
                pubtypes.append(pt.text.strip())

    # MeSH
    mesh = []
    mhl = mc.find("MeshHeadingList")
    if mhl is not None:
        for mh in mhl.findall("MeshHeading"):
            d = mh.find("DescriptorName")
            if d is not None and d.text:
                mesh.append(d.text.strip())

    # DOI
    doi = ""
    pd = art.find("PubmedData")
    if pd is not None:
        for aid in pd.findall("ArticleIdList/ArticleId"):
            if aid.attrib.get("IdType") == "doi":
                doi = aid.text.strip()
                break

    return {
        "pmid": pmid,
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "date": date_str,
        "abstract": abstract,
        "pubtypes": pubtypes,
        "mesh": mesh,
        "doi": doi,
    }


def parse_xml(xml_text):
    root = ET.fromstring(xml_text)
    results = []
    for art in root.iter("PubmedArticle"):
        rec = parse_article(art)
        if rec:
            results.append(rec)
    return results


def to_markdown(records):
    lines = []
    for i, r in enumerate(records, 1):
        lines.append(f"## {i}. {r['title']} ({r['journal']}, {r['year']}) {'[' + ', '.join(r['pubtypes']) + ']' if r['pubtypes'] else ''}")
        meta = []
        if r["pmid"]:
            meta.append(f"**PMID**: {r['pmid']}")
        if r["doi"]:
            meta.append(f"**DOI**: {r['doi']}")
        if meta:
            lines.append("- " + " | ".join(meta))
        if r["authors"]:
            shown = ", ".join(r["authors"][:8])
            if len(r["authors"]) > 8:
                shown += f" 等 {len(r['authors'])}人"
            lines.append(f"- **作者**: {shown}")
        if r["mesh"]:
            lines.append(f"- **MeSH**: {', '.join(r['mesh'][:10])}")
        if r["abstract"]:
            lines.append(f"- **摘要**: {r['abstract']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="PubMed 检索与结构化解析（E-utilities）")
    ap.add_argument("--query", required=True, help="检索式，建议含 MeSH 与字段标签")
    ap.add_argument("--mindate", help="起始日期 YYYY/MM/DD 或 YYYY/MM")
    ap.add_argument("--maxdate", help="结束日期 YYYY/MM/DD 或 YYYY/MM")
    ap.add_argument("--days", type=int, help="近 N 天（与 mindate 二选一）")
    ap.add_argument("--max", type=int, default=20, help="最大返回条数（默认20，上限500）")
    ap.add_argument("--sort", default="date", choices=["date", "relevance"], help="排序方式")
    ap.add_argument("--out", default="md", choices=["md", "json"], help="输出格式")
    ap.add_argument("--api-key", help="NCBI E-utilities API key（提升速率）")
    args = ap.parse_args()

    retmax = min(max(args.max, 1), 500)
    mindate = args.mindate
    if args.days:
        mindate = (date.today() - timedelta(days=args.days)).strftime("%Y/%m/%d")

    try:
        pmids = esearch(args.query, mindate, args.maxdate, retmax, args.sort, args.api_key)
    except Exception as e:
        sys.stderr.write(f"[esearch 失败] {e}\n")
        sys.exit(1)

    if not pmids:
        sys.stderr.write("[提示] 未检索到文献，请放宽检索式或日期范围。\n")
        if args.out == "json":
            print("[]")
        else:
            print("（未检索到文献）")
        return

    try:
        xml_text = efetch(pmids, args.api_key)
    except Exception as e:
        sys.stderr.write(f"[efetch 失败] {e}\n")
        sys.exit(1)

    records = parse_xml(xml_text)
    if args.out == "json":
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(records))
        sys.stderr.write(f"[完成] 共解析 {len(records)} 篇（命中 {len(pmids)} 条）。\n")


if __name__ == "__main__":
    main()
