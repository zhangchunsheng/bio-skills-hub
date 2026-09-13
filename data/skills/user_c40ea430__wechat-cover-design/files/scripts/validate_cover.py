#!/usr/bin/env python3
"""Reject a generated background that cannot safely receive the fixed title."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from cover_quality import audit_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--theme", required=True, type=int, choices=range(1, 14))
    parser.add_argument("--json", action="store_true", help="Print a machine-readable audit report")
    args = parser.parse_args()

    image = Image.open(args.input).convert("RGB")
    report = audit_report(image, args.theme)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    if report["status"] != "PASS":
        if not args.json:
            for issue in report["issues"]:
                print("FAIL: " + issue)
            print("Regenerate a text-free background; do not place title text over this image.")
        return 1
    if not args.json:
        print("PASS: title field is quiet enough, unoccupied, and has sufficient contrast for deterministic typography")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
