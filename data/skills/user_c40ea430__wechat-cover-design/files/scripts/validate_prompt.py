#!/usr/bin/env python3
"""Portable prompt checks for wechat-cover-design.

Read UTF-8 prompt text from stdin and return 0 only when every selected check passes.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable

Check = Callable[[str], tuple[bool, str]]


def check_no_placeholders(text: str) -> tuple[bool, str]:
    found = re.findall(
        r"\{[^{}\n]+\}|\[(?:selected|focal|insert|replace|your|article|company|theme|scene)[^\[\]\n]*\]|"
        r"\b(?:TBD|TODO|FIXME|XXX)\b",
        text,
        re.I,
    )
    if found:
        return False, f"unresolved placeholders: {', '.join(found[:5])}"
    return True, "no unresolved placeholders"


def check_negative(text: str) -> tuple[bool, str]:
    match = re.search(
        r"(?is)(?:negative\s+prompt|avoid)\s*:\s*(.+?)(?=\n\s*[A-Z][^\n:]{1,40}:|\Z)",
        text,
    )
    ok = bool(match and len(match.group(1).strip()) >= 20)
    message = "contains a non-empty negative/avoid section" if ok else "missing or empty Negative prompt/Avoid section"
    return ok, message


def check_ratio(text: str) -> tuple[bool, str]:
    exact_canvas = re.search(r"\b1584\s*[x×]\s*672\b", text, re.I)
    target_ratio = re.search(r"\b(?:21\s*:\s*9|2\.3[3-5]\s*:\s*1)\b", text, re.I)
    ok = bool(exact_canvas or target_ratio)
    message = (
        "contains the 1584x672 canvas or 2.33-2.35:1 ratio"
        if ok
        else "missing the required 1584x672 canvas or 2.33-2.35:1 ratio"
    )
    return ok, message


def check_length(text: str) -> tuple[bool, str]:
    count = len(text)
    ok = 300 <= count <= 8000
    return ok, f"length {count} characters" if ok else f"length {count} outside 300-8000 characters"


def check_text_free_strategy(text: str) -> tuple[bool, str]:
    text_free = re.search(r"text[- ]free|no\s+(?:readable\s+)?text", text, re.I)
    overlay = re.search(r"post[- ]?process|overlay|后期|叠字", text, re.I)
    ok = bool(text_free and overlay)
    message = (
        "contains both a text-free requirement and overlay strategy"
        if ok
        else "requires both a text-free background and an explicit overlay strategy"
    )
    return ok, message


def check_handoff(text: str) -> tuple[bool, str]:
    left_field = re.search(
        r"(?:left(?:-side)?[^\n.]{0,100}(?:title\s+field|title\s+zone|title\s+area|title\s+block))|"
        r"(?:x\s*=\s*4\.8%?\s*(?:\.\.|-|to)\s*39\.1%?)",
        text,
        re.I,
    )
    text_free = re.search(r"text[- ]free|no\s+(?:readable\s+)?text", text, re.I)
    overlay = re.search(r"post[- ]?process|overlay|叠字", text, re.I)
    exclusions = all(
        re.search(pattern, text, re.I)
        for pattern in (r"(?:no\s+)?(?:readable\s+)?text", r"labels?", r"logos?", r"watermarks?")
    )
    if left_field and text_free and overlay and exclusions:
        return True, "contains a text-free background handoff with an explicit title field and overlay strategy"
    return False, "handoff needs a text-free background, explicit left title field, overlay strategy, and text/label/logo/watermark exclusions"


def check_content_alignment(text: str) -> tuple[bool, str]:
    """Require a minimal, inspectable record tying the prompt to the article."""
    required_fields = [
        "Article thesis",
        "Reader takeaway",
        "Content class",
        "Theme rationale",
        "Visual metaphor",
        "Element provenance",
        "Forbidden substitutions",
    ]
    missing = [field for field in required_fields if not re.search(rf"(?im)^\s*{re.escape(field)}\s*:\s*\S", text)]
    if missing:
        return False, "missing or empty Alignment Record fields: " + ", ".join(missing)

    provenance_match = re.search(
        r"(?ims)^\s*Element provenance\s*:\s*(.+?)(?=^\s*(?:Forbidden substitutions|English image prompt|Negative prompt)\s*:|\Z)",
        text,
    )
    if not provenance_match or len(provenance_match.group(1).strip()) < 25:
        return False, "Element provenance is empty or too vague"

    forbidden_match = re.search(
        r"(?ims)^\s*Forbidden substitutions\s*:\s*(.+?)(?=^\s*(?:English image prompt|Negative prompt)\s*:|\Z)",
        text,
    )
    if not forbidden_match or len(forbidden_match.group(1).strip()) < 10:
        return False, "Forbidden substitutions is empty or too vague"
    return True, "contains a complete Alignment Record"


def selected_checks(args: argparse.Namespace) -> list[Check]:
    all_checks = [
        check_no_placeholders,
        check_negative,
        check_ratio,
        check_length,
        check_text_free_strategy,
        check_content_alignment,
        check_handoff,
    ]
    if args.all or args.prompt_only:
        return all_checks
    mapping = {
        "no_placeholders": check_no_placeholders,
        "has_negative": check_negative,
        "has_ratio": check_ratio,
        "length": check_length,
        "text_strategy": check_text_free_strategy,
        "content_alignment": check_content_alignment,
    }
    return [check for name, check in mapping.items() if getattr(args, name)]


def run(text: str, args: argparse.Namespace) -> int:
    failed = False
    for check in selected_checks(args):
        ok, message = check(text)
        print(("PASS" if ok else "FAIL") + ": " + message)
        failed = failed or not ok
    if args.all:
        print("\n" + ("All checks passed." if not failed else "One or more checks failed."))
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a wechat-cover-design prompt from stdin.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--no-placeholders", dest="no_placeholders", action="store_true")
    group.add_argument("--has-negative", dest="has_negative", action="store_true")
    group.add_argument("--has-ratio", dest="has_ratio", action="store_true")
    group.add_argument("--length", action="store_true")
    group.add_argument("--text-strategy", dest="text_strategy", action="store_true")
    group.add_argument("--content-alignment", dest="content_alignment", action="store_true")
    group.add_argument("--prompt-only", dest="prompt_only", action="store_true")
    args = parser.parse_args()
    return run(sys.stdin.read(), args)


if __name__ == "__main__":
    raise SystemExit(main())
