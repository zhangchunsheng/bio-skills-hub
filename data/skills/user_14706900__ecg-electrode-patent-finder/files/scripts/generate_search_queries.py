#!/usr/bin/env python3
"""
Generate optimized patent search queries and ready-to-use URLs for
ECG electrode manufacturing process patents across multiple databases.

Usage:
    python generate_search_queries.py [--custom-keyword "KEYWORD"] [--output-format text|markdown|json]

Without arguments, generates a full set of bilingual search queries for
ECG electrode manufacturing process patents using the built-in keyword matrix.

With --custom-keyword, adds the specified keyword to the search set.
"""

import argparse
import json
import sys
import urllib.parse
from datetime import datetime, timedelta


# ============================================================
# Bilingual Keyword Matrix
# ============================================================

ELECTRODE_TYPES_CN = [
    "心电电极",
    "心电图电极",
    "心脏电极",
    "电极模块",
    "电极贴片",
    "电极扣",
    "湿电极",
    "干电极",
    "固态电极",
    "柔性电极",
]

ELECTRODE_TYPES_EN = [
    "ECG electrode",
    "EKG electrode",
    "cardiac electrode",
    "electrode module",
    "electrode pad",
    "electrode patch",
    "wet electrode",
    "dry electrode",
    "solid-state electrode",
    "flexible electrode",
]

PROCESS_TERMS_CN = [
    "制作工艺",
    "生产工艺",
    "制造方法",
    "加工流程",
    "制备方法",
    "工艺流程",
]

PROCESS_TERMS_EN = [
    "manufacturing process",
    "fabrication method",
    "production method",
    "preparation method",
    "process flow",
]

MATERIAL_KEYWORDS_CN = [
    "银氯化银",
    "导电凝胶",
    "水凝胶",
    "导电聚合物",
    "碳纳米管",
    "石墨烯",
]

MATERIAL_KEYWORDS_EN = [
    "Ag/AgCl",
    "conductive gel",
    "hydrogel",
    "conductive polymer",
    "carbon nanotube",
    "graphene",
]

IPC_CODES = [
    "A61B5/0408",
    "A61N1/04",
    "A61B5/024",
    "H01B13/00",
]

CPC_CODES = [
    "A61B5/0408",
    "A61N1/045",
    "A61B5/0205",
]


# ============================================================
# Query Generation Functions
# ============================================================

def generate_cn_keyword_queries():
    """Generate Chinese keyword combination queries."""
    queries = []
    for et in ELECTRODE_TYPES_CN:
        for pt in PROCESS_TERMS_CN:
            queries.append({
                "query": f'({et}) AND ({pt})',
                "language": "Chinese",
                "type": "keyword_combination",
            })
    return queries


def generate_en_keyword_queries():
    """Generate English keyword combination queries."""
    queries = []
    for et in ELECTRODE_TYPES_EN:
        for pt in PROCESS_TERMS_EN:
            queries.append({
                "query": f'({et}) AND ({pt})',
                "language": "English",
                "type": "keyword_combination",
            })
    return queries


def generate_material_queries():
    """Generate material-specific queries (bilingual)."""
    queries = []
    for i, mk in enumerate(MATERIAL_KEYWORDS_CN):
        queries.append({
            "query": f'({mk}) AND (电极) AND (制作 OR 制造 OR 生产)',
            "language": "Chinese",
            "type": "material_focused",
        })
        queries.append({
            "query": f'({MATERIAL_KEYWORDS_EN[i]}) AND (electrode) AND (manufactur* OR fabricat* OR produc*)',
            "language": "English",
            "type": "material_focused",
        })
    return queries


def generate_classification_queries():
    """Generate IPC/CPC classification-based queries."""
    queries = []
    for ipc in IPC_CODES:
        queries.append({
            "query": f'IPC={ipc}',
            "language": "Classification",
            "type": "ipc_filter",
        })
    for cpc in CPC_CODES:
        queries.append({
            "query": f'CPC={cpc}',
            "language": "Classification",
            "type": "cpc_filter",
        })
    return queries


def generate_combined_queries():
    """Generate combined keyword + classification queries."""
    queries = []
    # CN + IPC
    for ipc in IPC_CODES:
        queries.append({
            "query": f'IPC={ipc} AND (心电电极 OR 心电图电极) AND (制作 OR 制造 OR 工艺)',
            "language": "Chinese+IPC",
            "type": "combined",
        })
        queries.append({
            "query": f'IPC={ipc} AND (ECG electrode OR EKG electrode) AND (manufactur* OR fabricat*)',
            "language": "English+IPC",
            "type": "combined",
        })
    return queries


# ============================================================
# URL Generation Functions
# ============================================================

def build_google_patents_url(query, country="", after="", before=""):
    """Build a Google Patents search URL."""
    base = "https://patents.google.com/"
    params = {"q": query}
    if country:
        params["country"] = country
    if after:
        params["after"] = after
    if before:
        params["before"] = before
    param_str = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    return f"{base}?{param_str}"


def build_soopat_url(query):
    """Build a SooPAT search URL."""
    return f"https://www.soopat.com/Home/Result/IndexSearch?searchWord={urllib.parse.quote(query)}"


def build_espacenet_url(query):
    """Build an Espacenet search URL."""
    return f"https://worldwide.espacenet.com/patent/search?q={urllib.parse.quote(query)}"


def build_patentscope_url(query):
    """Build a WIPO Patentscope search URL."""
    return f"https://patentscope.wipo.int/search/en/result.jsf?query={urllib.parse.quote(query)}"


def build_uspto_url(query):
    """Build a USPTO Patent Public Search URL."""
    return f"https://ppubs.uspto.gov/dirsearch-public/users/search/advancedsearch?query={urllib.parse.quote(query)}"


# ============================================================
# Main Generation
# ============================================================

def generate_all(custom_keyword=""):
    """Generate all queries and URLs."""
    cn_queries = generate_cn_keyword_queries()
    en_queries = generate_en_keyword_queries()
    mat_queries = generate_material_queries()
    cls_queries = generate_classification_queries()
    com_queries = generate_combined_queries()

    if custom_keyword:
        cn_queries.append({
            "query": f'({custom_keyword}) AND (电极) AND (制作 OR 制造 OR 工艺)',
            "language": "Chinese",
            "type": "custom",
        })
        en_queries.append({
            "query": f'({custom_keyword}) AND (electrode) AND (manufactur* OR fabricat*)',
            "language": "English",
            "type": "custom",
        })

    all_queries = cn_queries + en_queries + mat_queries + cls_queries + com_queries

    # Generate URLs for top queries (limit to avoid excessive output)
    top_queries = all_queries[:20]

    results = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_queries": len(all_queries),
            "description": "ECG electrode manufacturing process patent search queries",
        },
        "queries": all_queries,
        "urls": [],
    }

    # Generate URLs for top queries across databases
    databases = [
        ("Google Patents (CN)", build_google_patents_url, {"country": "CN"}),
        ("Google Patents (Global)", build_google_patents_url, {}),
        ("SooPAT", build_soopat_url, {}),
        ("Espacenet", build_espacenet_url, {}),
        ("WIPO Patentscope", build_patentscope_url, {}),
        ("USPTO PPUBS", build_uspto_url, {}),
    ]

    for q in top_queries:
        url_entries = []
        for db_name, builder, extra_params in databases:
            url = builder(q["query"], **extra_params)
            url_entries.append({"database": db_name, "url": url})
        results["urls"].append({
            "query": q["query"],
            "language": q["language"],
            "type": q["type"],
            "urls": url_entries,
        })

    return results


def format_text_output(results):
    """Format results as plain text."""
    lines = []
    lines.append("=" * 70)
    lines.append("ECG Electrode Patent Search Queries")
    lines.append(f"Generated: {results['metadata']['generated_at']}")
    lines.append(f"Total queries: {results['metadata']['total_queries']}")
    lines.append("=" * 70)
    lines.append("")

    # Group by language/type
    by_type = {}
    for q in results["queries"]:
        key = f"[{q['language']}] {q['type']}"
        by_type.setdefault(key, []).append(q["query"])

    for key, queries in sorted(by_type.items()):
        lines.append(f"\n{'─' * 50}")
        lines.append(f"  {key} ({len(queries)} queries)")
        lines.append(f"{'─' * 50}")
        for i, q in enumerate(queries, 1):
            lines.append(f"  {i}. {q}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("Ready-to-Use Search URLs (Top 20 Queries)")
    lines.append("=" * 70)

    for entry in results["urls"]:
        lines.append(f"\nQuery: {entry['query']} [{entry['language']}]")
        for u in entry["urls"]:
            lines.append(f"  {u['database']}: {u['url']}")

    return "\n".join(lines)


def format_markdown_output(results):
    """Format results as Markdown."""
    md = []
    md.append("# ECG Electrode Patent Search Queries\n")
    md.append(f"**Generated**: {results['metadata']['generated_at']}  ")
    md.append(f"**Total queries**: {results['metadata']['total_queries']}\n")
    md.append("---\n")

    by_type = {}
    for q in results["queries"]:
        key = f"{q['language']} - {q['type']}"
        by_type.setdefault(key, []).append(q["query"])

    for key, queries in sorted(by_type.items()):
        md.append(f"## {key}\n")
        for i, q in enumerate(queries, 1):
            md.append(f"{i}. `{q}`")
        md.append("")

    md.append("---\n")
    md.append("## Ready-to-Use Search URLs\n")

    for entry in results["urls"]:
        md.append(f"### Query: `{entry['query']}` [{entry['language']}]\n")
        for u in entry["urls"]:
            md.append(f"- **{u['database']}**: [{u['url']}]({u['url']})")
        md.append("")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(
        description="Generate ECG electrode patent search queries and URLs"
    )
    parser.add_argument(
        "--custom-keyword",
        type=str,
        default="",
        help="Custom keyword to add to the search set",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["text", "markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    args = parser.parse_args()

    results = generate_all(args.custom_keyword)

    if args.output_format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.output_format == "text":
        print(format_text_output(results))
    else:
        print(format_markdown_output(results))


if __name__ == "__main__":
    main()
