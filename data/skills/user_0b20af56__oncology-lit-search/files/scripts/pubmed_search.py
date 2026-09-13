#!/usr/bin/env python3
"""PubMed 文献检索脚本 — 基于 NCBI E-utilities API

Usage:
    python pubmed_search.py --query "lung cancer AND immunotherapy"
    python pubmed_search.py -q "breast cancer[MeSH] AND trastuzumab" -m 20 --year-from 2023 --year-to 2024
    python pubmed_search.py -q "CAR-T AND lymphoma" --mode summary -m 15
    python pubmed_search.py -q "colorectal cancer" --sort pub_date -m 10 --start 10

无第三方依赖，仅使用 Python 标准库。无 API Key 时限速 3 req/sec。
"""

import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET

# Windows UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TOOL_NAME = "oncology-lit-search"
BATCH_SIZE = 200  # max PMIDs per efetch/esummary call


def rate_limit_wait(api_key):
    """Sleep to respect NCBI rate limits: 3 req/s without key, 10 req/s with key."""
    interval = 0.10 if api_key else 0.34
    time.sleep(interval)


def build_params(params, api_key):
    """Add tool name and optional api_key to request parameters."""
    params["tool"] = TOOL_NAME
    if api_key:
        params["api_key"] = api_key
    return params


def make_request(url, params, api_key, retries=1):
    """Make an HTTP GET request with retry logic.

    Returns the response body as a string.
    Raises URLError on persistent failure.
    """
    full_url = url + "?" + urllib.parse.urlencode(params)
    last_error = None

    for attempt in range(retries + 1):
        try:
            rate_limit_wait(api_key)
            req = urllib.request.Request(full_url, headers={"User-Agent": TOOL_NAME})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                # Rate limited — wait and retry
                time.sleep(2)
                continue
            if e.code == 400:
                # Bad request — likely query syntax error
                body = e.read().decode("utf-8", errors="replace")
                raise ValueError(f"PubMed query syntax error (HTTP 400): {body[:500]}")
            # Other HTTP errors
            last_error = e
            if attempt < retries:
                time.sleep(1)
                continue
            raise
        except urllib.error.URLError as e:
            last_error = e
            if attempt < retries:
                time.sleep(1)
                continue
            raise

    raise last_error  # Should not reach here


def append_date_filter(query, year_from, year_to):
    """Append a date range filter to the PubMed query string."""
    if not year_from and not year_to:
        return query

    yf = year_from or "1900"
    yt = year_to or "2100"
    date_filter = f' AND ("{yf}/01/01"[Date - Publication] : "{yt}/12/31"[Date - Publication])'
    return query + date_filter


def esearch(query, max_results, start, sort, api_key):
    """Search PubMed and return (pmid_list, total_count).

    Raises on error.
    """
    params = build_params({
        "db": "pubmed",
        "term": query,
        "retmax": str(max_results),
        "retstart": str(start),
        "retmode": "json",
        "sort": sort,
    }, api_key)

    body = make_request(BASE_URL + "esearch.fcgi", params, api_key)
    data = json.loads(body)
    result = data.get("esearchresult", {})

    id_list = result.get("idlist", [])
    count_str = result.get("count", "0")

    try:
        total = int(count_str)
    except (ValueError, TypeError):
        total = 0

    return id_list, total


def parse_efetch_xml(xml_text):
    """Parse efetch XML response and return a list of article dicts.

    Extracts: pmid, title, authors, journal, pub_date, abstract, doi, url
    """
    articles = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return articles

    for article_elem in root.findall(".//PubmedArticle"):
        article = parse_pubmed_article(article_elem)
        if article:
            articles.append(article)

    # Also handle PubmedBookArticle (rare, but possible)
    for book_elem in root.findall(".//PubmedBookArticle"):
        article = parse_pubmed_book(book_elem)
        if article:
            articles.append(article)

    return articles


def parse_pubmed_article(elem):
    """Parse a single <PubmedArticle> element."""
    article = {}

    # PMID
    pmid_elem = elem.find(".//MedlineCitation/PMID")
    if pmid_elem is not None and pmid_elem.text:
        article["pmid"] = pmid_elem.text.strip()
    else:
        return None  # No PMID = skip

    # Title
    title_elem = elem.find(".//Article/ArticleTitle")
    article["title"] = get_element_text(title_elem) if title_elem is not None else ""

    # Authors
    authors = []
    for author_elem in elem.findall(".//Article/AuthorList/Author"):
        last_name = author_elem.find("LastName")
        initials = author_elem.find("Initials")
        collective = author_elem.find("CollectiveName")

        if collective is not None and collective.text:
            authors.append(collective.text.strip())
        elif last_name is not None and last_name.text:
            name = last_name.text.strip()
            if initials is not None and initials.text:
                name += " " + initials.text.strip()
            authors.append(name)

    article["authors"] = authors

    # Journal
    journal_elem = elem.find(".//Article/Journal/Title")
    article["journal"] = journal_elem.text.strip() if journal_elem is not None and journal_elem.text else ""

    # Publication date
    pub_date = format_pub_date(elem)
    article["pub_date"] = pub_date

    # Abstract (may have multiple labeled sections)
    abstract_parts = []
    for abs_elem in elem.findall(".//Article/Abstract/AbstractText"):
        label = abs_elem.get("Label", "")
        text = get_element_text(abs_elem)
        if label:
            abstract_parts.append(f"{label}: {text}")
        else:
            abstract_parts.append(text)
    article["abstract"] = "\n".join(abstract_parts) if abstract_parts else None

    # DOI
    doi = ""
    for eloc in elem.findall(".//Article/ELocationID"):
        if eloc.get("EIdType", "").lower() == "doi" and eloc.text:
            doi = eloc.text.strip()
            break
    article["doi"] = doi if doi else None

    # MeSH terms
    mesh_terms = []
    for mesh_heading in elem.findall(".//MeshHeadingList/MeshHeading"):
        descriptor = mesh_heading.find("DescriptorName")
        if descriptor is not None and descriptor.text:
            term = descriptor.text.strip()
            # Append qualifiers if present
            for qualifier in mesh_heading.findall("QualifierName"):
                if qualifier.text:
                    term += f"/{qualifier.text.strip()}"
            mesh_terms.append(term)
    article["mesh_terms"] = mesh_terms if mesh_terms else None

    # Publication types
    pub_types = []
    for pt_elem in elem.findall(".//Article/PublicationTypeList/PublicationType"):
        if pt_elem.text:
            pub_types.append(pt_elem.text.strip())
    article["publication_types"] = pub_types if pub_types else None

    # URL
    article["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/"

    return article


def parse_pubmed_book(elem):
    """Parse a <PubmedBookArticle> element (rare)."""
    article = {}

    pmid_elem = elem.find(".//PMID")
    if pmid_elem is not None and pmid_elem.text:
        article["pmid"] = pmid_elem.text.strip()
    else:
        return None

    title_elem = elem.find(".//ArticleTitle")
    article["title"] = get_element_text(title_elem) if title_elem is not None else ""

    authors = []
    for author_elem in elem.findall(".//AuthorList/Author"):
        last_name = author_elem.find("LastName")
        initials = author_elem.find("Initials")
        if last_name is not None and last_name.text:
            name = last_name.text.strip()
            if initials is not None and initials.text:
                name += " " + initials.text.strip()
            authors.append(name)
    article["authors"] = authors

    article["journal"] = ""
    article["pub_date"] = ""
    article["abstract"] = None
    article["doi"] = None
    article["mesh_terms"] = None
    article["publication_types"] = None
    article["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/"

    return article


def format_pub_date(elem):
    """Extract and format publication date from article element."""
    pub_date_elem = elem.find(".//Article/Journal/JournalIssue/PubDate")
    if pub_date_elem is not None:
        year = pub_date_elem.find("Year")
        month = pub_date_elem.find("Month")
        day = pub_date_elem.find("Day")

        parts = []
        if year is not None and year.text:
            parts.append(year.text.strip())
        if month is not None and month.text:
            parts.append(month.text.strip())
        if day is not None and day.text:
            parts.append(day.text.strip())

        if parts:
            return " ".join(parts)

        # MedlineDate fallback (e.g., "2024 Spring")
        medline_date = pub_date_elem.find("MedlineDate")
        if medline_date is not None and medline_date.text:
            return medline_date.text.strip()

    return ""


def get_element_text(elem):
    """Get all text content from an element, including tail text of children."""
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def efetch(pmids, api_key):
    """Fetch full article data (with abstracts) via efetch.

    Returns list of article dicts.
    """
    all_articles = []

    for i in range(0, len(pmids), BATCH_SIZE):
        batch = pmids[i:i + BATCH_SIZE]
        params = build_params({
            "db": "pubmed",
            "id": ",".join(batch),
            "rettype": "abstract",
            "retmode": "xml",
        }, api_key)

        body = make_request(BASE_URL + "efetch.fcgi", params, api_key)
        articles = parse_efetch_xml(body)
        all_articles.extend(articles)

    return all_articles


def esummary(pmids, api_key):
    """Fetch article summaries (metadata only, no abstracts) via esummary.

    Returns list of article dicts.
    """
    all_articles = []

    for i in range(0, len(pmids), BATCH_SIZE):
        batch = pmids[i:i + BATCH_SIZE]
        params = build_params({
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "json",
        }, api_key)

        body = make_request(BASE_URL + "esummary.fcgi", params, api_key)
        data = json.loads(body)
        result = data.get("result", {})

        for pmid in batch:
            entry = result.get(pmid)
            if not entry or not isinstance(entry, dict):
                continue

            # Authors
            authors = []
            for au in entry.get("authors", []):
                name = au.get("name", "")
                if name:
                    authors.append(name)

            # DOI from elocationid (format: "doi: 10.xxx/yyy")
            doi = None
            eloc = entry.get("elocationid", "")
            if eloc and "doi:" in eloc.lower():
                doi = eloc.split("doi:", 1)[-1].strip()

            article = {
                "pmid": pmid,
                "title": entry.get("title", "").strip(),
                "authors": authors,
                "journal": entry.get("fulljournalname", "").strip(),
                "pub_date": entry.get("pubdate", "").strip(),
                "abstract": None,
                "doi": doi,
                "mesh_terms": entry.get("meshheadinglist", None),
                "publication_types": entry.get("pubtype", None),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }
            all_articles.append(article)

    return all_articles


def main():
    parser = argparse.ArgumentParser(
        description="PubMed literature search via NCBI E-utilities API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python pubmed_search.py -q "lung cancer AND immunotherapy"
  python pubmed_search.py -q "breast cancer[MeSH] AND trastuzumab" -m 20 --year-from 2023 --year-to 2024
  python pubmed_search.py -q "CAR-T AND lymphoma" --mode summary -m 15
  python pubmed_search.py -q "colorectal cancer" --sort pub_date -m 10 --start 10
""",
    )
    parser.add_argument("-q", "--query", required=True, help="PubMed query string (supports full PubMed syntax)")
    parser.add_argument("-m", "--max-results", type=int, default=5, help="Max results to return (1-200, default: 5)")
    parser.add_argument("-s", "--start", type=int, default=0, help="Pagination start offset (default: 0)")
    parser.add_argument("--mode", choices=["abstract", "summary"], default="abstract",
                        help="abstract: fetch full abstracts (slower); summary: metadata only (faster)")
    parser.add_argument("--sort", choices=["relevance", "pub_date", "author", "journal"], default="relevance",
                        help="Sort order (default: relevance)")
    parser.add_argument("--year-from", type=int, default=None, help="Start year for date filter")
    parser.add_argument("--year-to", type=int, default=None, help="End year for date filter")
    parser.add_argument("--api-key", default=None, help="NCBI API key (optional, raises rate limit to 10 req/s)")
    parser.add_argument("--raw", action="store_true", help="Output raw API response (debug)")

    args = parser.parse_args()

    # Validate max_results
    if args.max_results < 1 or args.max_results > 200:
        print(json.dumps({"error": "--max-results must be between 1 and 200"}, ensure_ascii=False))
        sys.exit(1)

    # Build full query with optional date filter
    full_query = append_date_filter(args.query, args.year_from, args.year_to)

    try:
        # Step 1: esearch to get PMIDs
        pmids, total = esearch(full_query, args.max_results, args.start, args.sort, args.api_key)

        if args.raw:
            print(json.dumps({"pmids": pmids, "total": total, "query": full_query}, ensure_ascii=False, indent=2))
            return

        # Handle no results
        if not pmids:
            output = {
                "query": args.query,
                "total_results": total,
                "returned": 0,
                "start": args.start,
                "mode": args.mode,
                "articles": [],
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return

        # Step 2: fetch article details
        if args.mode == "abstract":
            articles = efetch(pmids, args.api_key)
        else:
            articles = esummary(pmids, args.api_key)

        # Preserve esearch order (efetch/esummary may reorder)
        pmid_order = {pmid: i for i, pmid in enumerate(pmids)}
        articles.sort(key=lambda a: pmid_order.get(a.get("pmid", ""), 999))

        output = {
            "query": args.query,
            "total_results": total,
            "returned": len(articles),
            "start": args.start,
            "mode": args.mode,
            "articles": articles,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    except ValueError as e:
        # Query syntax error
        print(json.dumps({"error": str(e), "query": args.query}, ensure_ascii=False, indent=2))
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Network error: {e.reason}", "query": args.query}, ensure_ascii=False, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}", "query": args.query}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
