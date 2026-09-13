"""Shared text normalization for labor contract scripts."""

from __future__ import annotations

import re


MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
MARKDOWN_BOLD_RE = re.compile(r"\*\*(.*?)\*\*")
MARKDOWN_ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)")
MARKDOWN_CODE_RE = re.compile(r"`([^`]*)`")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
CONTRACT_TITLE_RE = re.compile(r"^劳动合同(?:（.*?）)?$")


def normalize_input(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return [line.rstrip() for line in normalized.split("\n")]


def clean_markdown_inline(text: str) -> str:
    cleaned = text.strip()
    previous = None
    while cleaned != previous:
        previous = cleaned
        cleaned = MARKDOWN_LINK_RE.sub(r"\1", cleaned)
        cleaned = MARKDOWN_CODE_RE.sub(r"\1", cleaned)
        cleaned = MARKDOWN_BOLD_RE.sub(r"\1", cleaned)
        cleaned = MARKDOWN_ITALIC_RE.sub(r"\1", cleaned)
    return cleaned


def normalize_control_line(text: str) -> str:
    line = text.strip()
    markdown_heading = MARKDOWN_HEADING_RE.match(line)
    if markdown_heading:
        line = markdown_heading.group(2)
    return clean_markdown_inline(line)


def is_contract_title(text: str) -> bool:
    return bool(CONTRACT_TITLE_RE.match(normalize_control_line(text)))
