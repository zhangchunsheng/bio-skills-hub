#!/usr/bin/env python3
"""Fail when final runtime evidence still requests the source origin."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from url_safety import validate_public_url


def walk_urls(value: object):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_urls(child)
    elif isinstance(value, str) and value.startswith(("http://", "https://")):
        yield value


def origin(url: str) -> tuple[str, str, int | None]:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    port = parsed.port
    if port is None:
        port = {"http": 80, "https": 443}.get(scheme)
    return scheme, (parsed.hostname or "").lower(), port


URL_PATTERN = re.compile(r"https?://[^\s\"'<>)}\]]+")


def scan_build(build_dir: Path, source: tuple[str, str, int | None]) -> list[dict[str, str]]:
    if not build_dir.is_dir():
        raise ValueError(f"build directory does not exist: {build_dir}")
    matches = []
    for path in sorted(item for item in build_dir.rglob("*") if item.is_file()):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        urls = sorted({match.group(0).rstrip(".,;") for match in URL_PATTERN.finditer(text)})
        for url in urls:
            if origin(url) == source:
                matches.append({"path": path.relative_to(build_dir).as_posix(), "url": url})
    return matches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        validate_public_url(args.source_url, "--source-url")
    except ValueError as error:
        parser.error(str(error))
    source = origin(args.source_url)
    try:
        data = json.loads(args.evidence.read_text(encoding="utf-8"))
        build_matches = scan_build(args.build_dir, source)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    blocked = sorted({url for url in walk_urls(data) if origin(url) == source})
    report = {
        "passed": not blocked and not build_matches,
        "sourceOrigin": source,
        "blocked": blocked,
        "buildMatches": build_matches,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
