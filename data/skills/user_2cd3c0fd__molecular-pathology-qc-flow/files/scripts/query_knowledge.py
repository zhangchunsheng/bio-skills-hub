#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
离线检索分子病理技术、方法和检测项目知识索引。

说明：检索层只负责匹配和展示，不把知识条目中的通用内容转换为实验室阈值。
Author: WangYunL
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


DEFAULT_INDEX = Path(__file__).resolve().parent.parent / "references" / "技术项目索引.json"
TOKEN_SPLIT_PATTERN = re.compile(r"[^0-9a-zA-Z\u4e00-\u9fff]+")


class KnowledgeQueryError(ValueError):
    """表示知识索引无法读取或查询参数无效。"""


def configure_console_encoding() -> None:
    """在 Windows 命令行中统一使用 UTF-8 输出中文。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def normalize_text(value: Any) -> str:
    """统一全半角、大小写和标点，便于中英文别名匹配。"""
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(part for part in TOKEN_SPLIT_PATTERN.split(text) if part)


def tokenize(value: Any) -> list[str]:
    """拆分查询词并保持首次出现顺序。"""
    tokens: list[str] = []
    for token in normalize_text(value).split():
        if token not in tokens:
            tokens.append(token)
    return tokens


def load_index(path: Path = DEFAULT_INDEX) -> dict[str, Any]:
    """严格按 UTF-8 读取知识索引。"""
    raw = path.read_text(encoding="utf-8-sig")
    if "\ufffd" in raw:
        raise KnowledgeQueryError(f"知识索引包含中文替换字符：{path}")
    try:
        index = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise KnowledgeQueryError(
            f"知识索引 JSON 解析失败：第 {exc.lineno} 行，第 {exc.colno} 列。"
        ) from exc
    if not isinstance(index, dict) or not isinstance(index.get("entries"), list):
        raise KnowledgeQueryError("知识索引必须包含 entries 数组。")
    return index


def _flatten_search_values(entry: dict[str, Any]) -> list[str]:
    """提取允许参与全文检索的字段，来源 URL 不参与业务匹配。"""
    values: list[str] = []
    for field in (
        "id",
        "kind",
        "name",
        "technology",
        "summary",
        "principle",
        "scope_note",
    ):
        values.append(str(entry.get(field) or ""))
    for field in ("aliases", "methods", "qc_stages", "common_measurements", "keywords"):
        value = entry.get(field)
        if isinstance(value, list):
            values.extend(str(item) for item in value)
    return values


def _contains_filter(entry: dict[str, Any], field: str, expected: str | None) -> bool:
    """对技术、项目和阶段进行可读的包含式筛选。"""
    if not expected:
        return True
    expected_value = normalize_text(expected).replace(" ", "")
    value = entry.get(field)
    candidates = value if isinstance(value, list) else [value]
    return any(
        expected_value in normalize_text(candidate).replace(" ", "")
        for candidate in candidates
        if candidate is not None
    )


def _score_entry(entry: dict[str, Any], query: str) -> tuple[int, list[str]]:
    """计算别名、名称和全文字段的匹配分数。"""
    normalized_query = normalize_text(query)
    compact_query = normalized_query.replace(" ", "")
    query_tokens = tokenize(query)
    name = normalize_text(entry.get("name"))
    aliases = [normalize_text(item) for item in entry.get("aliases") or []]
    fields = [normalize_text(value) for value in _flatten_search_values(entry)]
    compact_fields = [value.replace(" ", "") for value in fields]

    score = 0
    reasons: list[str] = []
    if normalized_query == name or normalized_query in aliases:
        score += 120
        reasons.append("名称或别名精确匹配")
    elif compact_query and any(compact_query == value for value in compact_fields):
        score += 100
        reasons.append("去标点后精确匹配")
    elif compact_query and any(compact_query in value for value in compact_fields):
        score += 35
        reasons.append("完整查询匹配")

    matched_tokens = 0
    for token in query_tokens:
        compact_token = token.replace(" ", "")
        if any(compact_token in value for value in compact_fields):
            matched_tokens += 1
            score += 18
            if compact_token == name.replace(" ", ""):
                score += 12
    if matched_tokens:
        reasons.append(f"命中 {matched_tokens}/{len(query_tokens)} 个查询词")
    if query_tokens and matched_tokens == len(query_tokens):
        score += 30
    if str(entry.get("kind")) == "project" and matched_tokens == len(query_tokens):
        score += 8
    return score, reasons


def search_index(
    index: dict[str, Any],
    query: str,
    *,
    technology: str | None = None,
    project: str | None = None,
    qc_stage: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """搜索索引并返回带匹配分数和原因的条目副本。"""
    if not tokenize(query):
        raise KnowledgeQueryError("查询词不能为空。")
    results: list[dict[str, Any]] = []
    for entry in index["entries"]:
        if not isinstance(entry, dict):
            continue
        if not _contains_filter(entry, "technology", technology):
            continue
        if not _contains_filter(entry, "name", project):
            continue
        if not _contains_filter(entry, "qc_stages", qc_stage):
            continue
        score, reasons = _score_entry(entry, query)
        if score <= 0:
            continue
        result = dict(entry)
        result["match_score"] = score
        result["match_reasons"] = reasons
        results.append(result)
    results.sort(key=lambda item: (-int(item["match_score"]), str(item.get("name"))))
    return results[: max(1, limit)]


def format_markdown(results: list[dict[str, Any]], query: str) -> str:
    """把查询结果输出为便于直接引用的中文 Markdown。"""
    lines = [f"# 分子病理知识查询：{query}", ""]
    if not results:
        lines.extend(
            [
                "未找到匹配条目。请补充技术、方法、项目名称或常用别名。",
                "",
                "注意：缺少具体试剂、平台或 SOP 时，不应据此补写实验室阈值。",
            ]
        )
        return "\n".join(lines)

    for index, entry in enumerate(results, start=1):
        lines.extend(
            [
                f"## {index}. {entry.get('name')}（{entry.get('kind')}）",
                "",
                f"- 技术：{entry.get('technology')}",
                f"- 常见方法：{'、'.join(entry.get('methods') or ['未确定'])}",
                f"- 是什么：{entry.get('summary')}",
                f"- 原理：{entry.get('principle')}",
                f"- 常见质控阶段：{'、'.join(entry.get('qc_stages') or [])}",
                f"- 常见指标：{'、'.join(entry.get('common_measurements') or [])}",
                f"- 适用边界：{entry.get('scope_note')}",
                f"- 详细参考：{entry.get('reference_file')}",
                f"- 匹配依据：{'；'.join(entry.get('match_reasons') or [])}",
                "- 权威来源：",
            ]
        )
        for source in entry.get("sources") or []:
            lines.append(
                f"  - {source.get('title')}（核对日期 {source.get('last_verified')}）：{source.get('url')}"
            )
        lines.append("")
    lines.append("阈值提示：通用知识仅用于定位质控点；具体阈值必须回到匹配版本的 SOP、试剂说明书或验证报告。")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="检索分子病理技术与质控知识索引。")
    parser.add_argument("query", help="技术、方法、项目或别名，例如 PCR BRAF")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="知识索引路径")
    parser.add_argument("--technology", help="按技术筛选")
    parser.add_argument("--project", help="按项目名称筛选")
    parser.add_argument("--qc-stage", help="按质控阶段筛选")
    parser.add_argument("--limit", type=int, default=5, help="最多返回条目数")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args()


def main() -> int:
    """执行离线知识查询。"""
    args = parse_args()
    try:
        index = load_index(args.index)
        results = search_index(
            index,
            args.query,
            technology=args.technology,
            project=args.project,
            qc_stage=args.qc_stage,
            limit=args.limit,
        )
    except (OSError, KnowledgeQueryError) as exc:
        print(f"查询失败：{exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(results, args.query))
    return 0 if results else 2


if __name__ == "__main__":
    configure_console_encoding()
    raise SystemExit(main())

