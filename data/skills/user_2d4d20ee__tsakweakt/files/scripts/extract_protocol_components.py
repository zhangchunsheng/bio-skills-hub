#!/usr/bin/env python3
"""Extract protocol text and map likely components from DOCX/MD/TXT/JSON.

PDF requires pypdf; missing or failed extraction is returned as EXTRACTION_UNCERTAIN.
The mapper produces candidates with evidence and never makes the final pass decision.
"""

from __future__ import annotations

import json
import os
import re
import sys
import zipfile
from typing import Any
from xml.etree import ElementTree

SECTION_HINTS = {
    "background_and_objective": ("研究背景", "研究目的", "背景与目的", "background", "objective"),
    "study_design": ("研究设计", "study design"),
    "eligibility.inclusion": ("纳入标准", "入选标准", "inclusion criteria"),
    "eligibility.exclusion": ("排除标准", "exclusion criteria"),
    "sample_size.basis": ("样本量计算", "样本量估算", "sample size"),
    "outcomes.primary": ("主要终点", "主要结局", "primary outcome", "primary endpoint"),
    "outcomes.secondary": ("次要终点", "次要结局", "secondary outcome", "secondary endpoint"),
    "statistical_analysis": ("统计分析", "statistical analysis"),
    "references": ("参考文献", "references"),
    "picos.population": ("研究对象", "研究人群", "population"),
    "picos.intervention": ("干预措施", "暴露因素", "intervention", "exposure"),
    "picos.comparison": ("对照", "comparison", "comparator"),
    "picos.outcome": ("结局指标", "终点指标", "outcome"),
    "picos.study_design": ("研究设计", "study design"),
}


def extract_docx(path: str) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("word/document.xml"))
    paragraphs = []
    for paragraph in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        text = "".join(node.text or "" for node in paragraph.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")).strip()
        if text:
            paragraphs.append(text)
    return paragraphs


def extract_pdf(path: str) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF_PARSER_UNAVAILABLE") from exc
    return [(page.extract_text() or "").strip() for page in PdfReader(path).pages if (page.extract_text() or "").strip()]


def extract_blocks(path: str) -> tuple[list[str], list[dict[str, str]]]:
    if not os.path.isfile(path):
        return [], [{"code": "EXTRACTION_UNCERTAIN", "reason": "DOCUMENT_NOT_ACCESSIBLE"}]
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".docx":
            blocks = extract_docx(path)
        elif ext == ".pdf":
            blocks = extract_pdf(path)
        elif ext in {".md", ".txt"}:
            with open(path, encoding="utf-8-sig") as source:
                blocks = [line.strip() for line in source if line.strip()]
        elif ext == ".json":
            with open(path, encoding="utf-8-sig") as source:
                data = json.load(source)
            return [], [] if isinstance(data, dict) else [{"code": "EXTRACTION_UNCERTAIN", "reason": "JSON_NOT_OBJECT"}]
        else:
            return [], [{"code": "EXTRACTION_UNCERTAIN", "reason": "UNSUPPORTED_DOCUMENT_TYPE"}]
    except Exception as exc:
        return [], [{"code": "EXTRACTION_UNCERTAIN", "reason": str(exc)}]
    if not blocks:
        return [], [{"code": "EXTRACTION_UNCERTAIN", "reason": "NO_TEXT_EXTRACTED"}]
    return blocks, []


def set_path(target: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    current = target
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value


def map_components(blocks: list[str]) -> dict[str, Any]:
    components: dict[str, Any] = {}
    lowered = [block.lower() for block in blocks]
    for field, hints in SECTION_HINTS.items():
        matches = []
        for index, text in enumerate(lowered):
            if any(hint.lower() in text for hint in hints):
                evidence = blocks[index:index + 3]
                meaningful = "\n".join(evidence).strip()
                if meaningful:
                    matches.append({"text": meaningful, "evidence_locations": [{"block": index + 1}]})
        if matches:
            set_path(components, field, matches if field in {"references", "outcomes.primary", "outcomes.secondary"} else matches[0])
    return components


def extract(payload: dict[str, Any]) -> dict[str, Any]:
    path = payload.get("document_path")
    if not path:
        return {"components": {}, "extraction_warnings": [{"code": "EXTRACTION_UNCERTAIN", "reason": "DOCUMENT_PATH_MISSING"}]}
    if str(path).lower().endswith(".json") and os.path.isfile(path):
        try:
            with open(path, encoding="utf-8-sig") as source:
                data = json.load(source)
            return {"components": data.get("components", data), "extraction_warnings": []}
        except Exception as exc:
            return {"components": {}, "extraction_warnings": [{"code": "EXTRACTION_UNCERTAIN", "reason": str(exc)}]}
    blocks, warnings = extract_blocks(path)
    return {"components": map_components(blocks), "blocks": [{"block_id": i + 1, "text": text} for i, text in enumerate(blocks)], "extraction_warnings": warnings}


if __name__ == "__main__":
    raw = open(sys.argv[1], encoding="utf-8") if len(sys.argv) > 1 else sys.stdin
    print(json.dumps(extract(json.load(raw)), ensure_ascii=False, indent=2))
