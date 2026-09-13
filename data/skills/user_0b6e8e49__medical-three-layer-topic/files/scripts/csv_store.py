#!/usr/bin/env python3
"""Write local keyword libraries and doctor-IP topic CSV files safely."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
import time
import unicodedata
from datetime import date
from pathlib import Path
from typing import Iterable


TOPIC_HEADERS = [
    "序号",
    "科室/专业方向",
    "选题标题",
    "第一层关键词",
    "第二层关键词",
    "第三层关键词",
    "生成模式",
    "生成日期",
]
LIBRARY_HEADERS = ["层级", "关键词", "分类", "权重", "状态"]
ALLOWED_MODES = {"mixed", "newbie", "pitfall", "compare", "live", "burst"}

TOPIC_INPUT_FIELDS = ["title", "layer1", "layer2", "layer3", "mode"]
LIBRARY_INPUT_FIELDS = ["layer", "keyword", "category", "weight", "status"]


class CsvStoreError(ValueError):
    """Raised when runtime data cannot be validated or safely written."""


def sanitize_specialty(value: str) -> str:
    """Return a filesystem-safe specialty label without changing user-visible data."""
    if not isinstance(value, str) or not value.strip():
        raise CsvStoreError("科室/专业方向不能为空")
    normalized = unicodedata.normalize("NFKC", value).strip()
    normalized = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", normalized)
    normalized = re.sub(r"\s+", "_", normalized)
    while ".." in normalized:
        normalized = normalized.replace("..", "_")
    normalized = normalized.strip(" ._")[:80]
    if not normalized:
        raise CsvStoreError("科室/专业方向无法转换为安全文件名")
    return normalized


def _required_text(row: dict, field: str, row_number: int) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise CsvStoreError(f"第 {row_number} 行缺少字段或内容为空：{field}")
    return value.strip()


def _validate_topics(payload: dict) -> list[dict[str, str]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("topics"), list):
        raise CsvStoreError("输入必须包含 topics 数组")
    if not payload["topics"]:
        raise CsvStoreError("topics 数组不能为空")

    validated = []
    for index, item in enumerate(payload["topics"], start=1):
        if not isinstance(item, dict):
            raise CsvStoreError(f"第 {index} 行必须是对象")
        row = {field: _required_text(item, field, index) for field in TOPIC_INPUT_FIELDS}
        if row["mode"] not in ALLOWED_MODES:
            raise CsvStoreError(f"第 {index} 行生成模式无效：{row['mode']}")
        validated.append(row)
    return validated


def _validate_library(payload: dict) -> list[dict[str, object]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("keywords"), list):
        raise CsvStoreError("输入必须包含 keywords 数组")
    if not payload["keywords"]:
        raise CsvStoreError("keywords 数组不能为空")

    validated = []
    for index, item in enumerate(payload["keywords"], start=1):
        if not isinstance(item, dict):
            raise CsvStoreError(f"第 {index} 行必须是对象")
        row = {
            "layer": _required_text(item, "layer", index),
            "keyword": _required_text(item, "keyword", index),
            "category": _required_text(item, "category", index),
            "status": _required_text(item, "status", index),
        }
        weight = item.get("weight")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise CsvStoreError(f"第 {index} 行权重必须是数字")
        row["weight"] = weight
        validated.append(row)
    return validated


def _normalize_title(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value)).casefold()


def _ensure_inside(output_dir: Path, filename: str) -> Path:
    root = output_dir.resolve()
    candidate = (root / filename).resolve()
    if candidate.parent != root:
        raise CsvStoreError("输出路径超出指定目录")
    return candidate


_WRITE_RETRIES = 3
_WRITE_BACKOFF_BASE = 1


def _atomic_write_csv(path: Path, headers: list[str], rows: Iterable[dict]) -> None:
    """原子写入 CSV：先写临时文件再替换，支持自动重试。

    重试策略：最多 3 次，指数退避 1s → 2s → 4s。
    覆盖的临时故障：磁盘瞬时写满、云同步目录瞬时锁冲突、系统句柄不足。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for attempt in range(1, _WRITE_RETRIES + 1):
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8-sig",
                newline="",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temp_path = Path(handle.name)
                writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="raise")
                writer.writeheader()
                writer.writerows(rows)
            os.replace(temp_path, path)
            return  # 成功
        except PermissionError as exc:
            last_error = exc
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            if attempt < _WRITE_RETRIES:
                time.sleep(_WRITE_BACKOFF_BASE * (2 ** (attempt - 1)))
                continue
            raise CsvStoreError(
                f"无法写入文件 {path.name}：目录权限不足，请检查是否有写入权限。\n"
                f"如果输出目录在 iCloud/OneDrive 中，请换到本地目录后重试。"
            ) from exc
        except OSError as exc:
            last_error = exc
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            if attempt < _WRITE_RETRIES:
                time.sleep(_WRITE_BACKOFF_BASE * (2 ** (attempt - 1)))
                continue
            raise CsvStoreError(
                f"无法写入文件 {path.name}：系统 IO 错误（可能磁盘已满或文件系统异常），"
                f"已重试 {_WRITE_RETRIES} 次仍失败。请检查磁盘空间后重试。"
            ) from exc
        except Exception:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            raise


def _read_history(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != TOPIC_HEADERS:
                raise CsvStoreError("选题历史表头不符合预期，已停止写入并保留原文件")
            rows = list(reader)
    except UnicodeError as exc:
        raise CsvStoreError("选题历史编码无效，已停止写入并保留原文件") from exc

    for index, row in enumerate(rows, start=2):
        if any(row.get(header) is None for header in TOPIC_HEADERS):
            raise CsvStoreError(f"选题历史第 {index} 行损坏，已停止写入并保留原文件")
        if not row["选题标题"].strip():
            raise CsvStoreError(f"选题历史第 {index} 行标题为空，已停止写入并保留原文件")
    return rows


def write_topics(
    payload: dict,
    specialty: str,
    output_dir: Path,
    generated_date: date,
) -> Path:
    """Write deduplicated topic results and atomically update local history."""
    topics = _validate_topics(payload)
    display_specialty = specialty.strip()
    safe_specialty = sanitize_specialty(specialty)
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    history_path = _ensure_inside(root, "选题历史.csv")
    history_rows = _read_history(history_path)

    seen = {_normalize_title(row["选题标题"]) for row in history_rows}
    result_rows = []
    for topic in topics:
        normalized_title = _normalize_title(topic["title"])
        if normalized_title in seen:
            continue
        seen.add(normalized_title)
        result_rows.append(
            {
                "序号": len(result_rows) + 1,
                "科室/专业方向": display_specialty,
                "选题标题": topic["title"],
                "第一层关键词": topic["layer1"],
                "第二层关键词": topic["layer2"],
                "第三层关键词": topic["layer3"],
                "生成模式": topic["mode"],
                "生成日期": generated_date.isoformat(),
            }
        )
    if not result_rows:
        raise CsvStoreError("没有可写入的新选题：候选标题均与历史或当前批次重复")

    result_path = _ensure_inside(
        root,
        f"医生IP选题_{safe_specialty}_{generated_date.strftime('%Y%m%d')}.csv",
    )
    _atomic_write_csv(result_path, TOPIC_HEADERS, result_rows)

    combined_history = [*history_rows]
    for row in result_rows:
        history_row = dict(row)
        history_row["序号"] = len(combined_history) + 1
        combined_history.append(history_row)
    _atomic_write_csv(history_path, TOPIC_HEADERS, combined_history)
    return result_path


def write_library(payload: dict, specialty: str, output_dir: Path) -> Path:
    """Write a validated three-layer keyword library as UTF-8 BOM CSV."""
    keywords = _validate_library(payload)
    safe_specialty = sanitize_specialty(specialty)
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    output_path = _ensure_inside(root, f"关键词库_{safe_specialty}.csv")
    rows = [
        {
            "层级": item["layer"],
            "关键词": item["keyword"],
            "分类": item["category"],
            "权重": item["weight"],
            "状态": item["status"],
        }
        for item in keywords
    ]
    _atomic_write_csv(output_path, LIBRARY_HEADERS, rows)
    return output_path


def _load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CsvStoreError(f"无法读取 JSON 输入：{exc}") from exc
    if not isinstance(payload, dict):
        raise CsvStoreError("JSON 顶层必须是对象")
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write local doctor-IP topic and keyword CSV files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("topics", "library"):
        child = subparsers.add_parser(command)
        child.add_argument("--input", required=True, type=Path, help="UTF-8 JSON input file")
        child.add_argument("--specialty", required=True, help="Medical specialty or professional direction")
        child.add_argument("--output-dir", required=True, type=Path, help="Local output directory")
        if command == "topics":
            child.add_argument("--date", default=date.today().isoformat(), help="Generation date: YYYY-MM-DD")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        payload = _load_json(args.input)
        if args.command == "topics":
            generated_date = date.fromisoformat(args.date)
            output = write_topics(payload, args.specialty, args.output_dir, generated_date)
        else:
            output = write_library(payload, args.specialty, args.output_dir)
    except (CsvStoreError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
