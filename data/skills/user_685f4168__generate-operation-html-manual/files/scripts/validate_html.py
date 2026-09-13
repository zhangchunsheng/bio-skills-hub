#!/usr/bin/env python3
"""Static release checks for a visual HTML manual."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


class ManualParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.nav_depth = 0
        self.nav_links: list[str] = []
        self.images: list[dict[str, str]] = []
        self.h1_count = 0
        self.title_depth = 0
        self.title_text: list[str] = []
        self.viewport = False
        self.classes: Counter[str] = Counter()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {k: (v or "") for k, v in attrs}
        if data.get("id"):
            self.ids.append(data["id"])
        for cls in data.get("class", "").split():
            self.classes[cls] += 1
        if tag == "nav":
            self.nav_depth += 1
        if tag == "a" and self.nav_depth and data.get("href", "").startswith("#"):
            self.nav_links.append(unquote(data["href"][1:]))
        if tag == "img":
            self.images.append(data)
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self.title_depth += 1
        if tag == "meta" and data.get("name", "").lower() == "viewport":
            self.viewport = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.nav_depth:
            self.nav_depth -= 1
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data.strip())


def is_remote(source: str) -> bool:
    scheme = urlparse(source).scheme.lower()
    return scheme in {"http", "https", "data", "blob"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    path = Path(args.html).expanduser().resolve()
    if not path.is_file():
        ap.error(f"File not found: {path}")
    source = path.read_text(encoding="utf-8")
    parser = ManualParser()
    parser.feed(source)

    id_counts = Counter(parser.ids)
    duplicate_ids = sorted(k for k, n in id_counts.items() if n > 1)
    missing_targets = sorted(set(parser.nav_links) - set(parser.ids))
    duplicate_nav = sorted(k for k, n in Counter(parser.nav_links).items() if n > 1)
    missing_alt = []
    missing_files = []
    intentional_placeholders = 0
    for idx, image in enumerate(parser.images, 1):
        image_classes = image.get("class", "").split()
        if "lightbox-image" in image_classes:
            continue
        if not image.get("alt", "").strip():
            missing_alt.append(idx)
        candidate = image.get("data-src") or image.get("src", "")
        if not candidate or candidate.startswith("SCREENSHOT_"):
            intentional_placeholders += 1
            continue
        if not is_remote(candidate):
            local = (path.parent / unquote(candidate.split("#", 1)[0].split("?", 1)[0])).resolve()
            if not local.is_file():
                if image.get("data-src"):
                    intentional_placeholders += 1
                else:
                    missing_files.append(candidate)

    errors = []
    warnings = []
    if parser.h1_count != 1:
        errors.append(f"Expected exactly one h1; found {parser.h1_count}")
    if not "".join(parser.title_text).strip():
        errors.append("Missing non-empty title element")
    if not parser.viewport:
        errors.append("Missing viewport meta tag")
    if duplicate_ids:
        errors.append("Duplicate IDs: " + ", ".join(duplicate_ids))
    if missing_targets:
        errors.append("Broken nav targets: " + ", ".join(missing_targets))
    if duplicate_nav:
        errors.append("Duplicate nav targets: " + ", ".join(duplicate_nav))
    if missing_alt:
        errors.append("Images missing alt text at positions: " + ", ".join(map(str, missing_alt)))
    if missing_files:
        errors.append("Missing local image files: " + ", ".join(sorted(set(missing_files))))
    for marker, message in [
        ("@media print", "Missing print stylesheet"),
        ("image-lightbox", "Missing image lightbox"),
        ("window.print", "Missing print/PDF control"),
    ]:
        if marker not in source:
            errors.append(message)
    if not re.search(r"@media\s*\(\s*max-width\s*:", source):
        errors.append("Missing responsive breakpoint")
    leftovers = sorted(set(re.findall(r"\{\{[A-Z][A-Z0-9_]*\}\}|\bTODO\b", source)))
    if leftovers:
        warnings.append("Template markers remain: " + ", ".join(leftovers))

    result = {
        "file": str(path),
        "nav_links": len(parser.nav_links),
        "unique_ids": len(id_counts),
        "screenshots": parser.classes["shot"],
        "images": len(parser.images),
        "intentional_placeholders": intentional_placeholders,
        "errors": errors,
        "warnings": warnings,
        "status": "PASS" if not errors else "FAIL",
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[{result['status']}] {path}")
        print(f"Navigation: {result['nav_links']} links | IDs: {result['unique_ids']} | Screenshots: {result['screenshots']} | Placeholders: {intentional_placeholders}")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARN:  {item}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
