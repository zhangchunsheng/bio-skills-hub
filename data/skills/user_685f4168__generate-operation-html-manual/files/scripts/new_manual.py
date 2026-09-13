#!/usr/bin/env python3
"""Instantiate the bundled visual manual template."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Output .html path")
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="操作说明与实施指南")
    parser.add_argument("--audience", default="业务、实施与运维人员")
    parser.add_argument("--version", default="V1.0")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--eyebrow", default="PROFESSIONAL OPERATIONS MANUAL")
    args = parser.parse_args()

    output = Path(args.output).expanduser().resolve()
    if output.suffix.lower() != ".html":
        parser.error("--output must end in .html")
    template = Path(__file__).resolve().parent.parent / "assets" / "manual-template.html"
    html = template.read_text(encoding="utf-8")
    replacements = {
        "{{TITLE}}": args.title,
        "{{SUBTITLE}}": args.subtitle,
        "{{AUDIENCE}}": args.audience,
        "{{VERSION}}": args.version,
        "{{DATE}}": args.date,
        "{{EYEBROW}}": args.eyebrow,
        "{{IMAGE_DIR}}": f"{output.stem}-images",
    }
    for token, value in replacements.items():
        html = html.replace(token, value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    image_dir = output.with_name(f"{output.stem}-images")
    image_dir.mkdir(exist_ok=True)
    print(f"Created: {output}")
    print(f"Images:  {image_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
