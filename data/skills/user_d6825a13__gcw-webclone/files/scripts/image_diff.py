#!/usr/bin/env python3
"""Compare two same-size screenshots and emit deterministic JSON metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance


def percentile_from_histogram(histogram: list[int], percentile: float) -> int:
    target = sum(histogram) * percentile
    seen = 0
    for value, count in enumerate(histogram):
        seen += count
        if seen >= target:
            return value
    return len(histogram) - 1


def compare(source_path: Path, candidate_path: Path, threshold: int, diff_path: Path | None = None) -> dict:
    source = Image.open(source_path).convert("RGB")
    candidate = Image.open(candidate_path).convert("RGB")
    if source.size != candidate.size:
        raise ValueError(f"image sizes differ: {source.size} vs {candidate.size}")
    diff = ImageChops.difference(source, candidate)
    pixels = source.width * source.height
    red, green, blue = diff.split()
    maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    changed = maximum.point(lambda value: 255 if value > threshold else 0).histogram()[255]
    histogram = diff.histogram()
    combined = [histogram[i] + histogram[256 + i] + histogram[512 + i] for i in range(256)]
    if diff_path:
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        ImageEnhance.Contrast(diff).enhance(4).save(diff_path)
    return {
        "width": source.width,
        "height": source.height,
        "threshold": threshold,
        "meanAbs": round(sum(index * count for index, count in enumerate(combined)) / (pixels * 3), 6),
        "changedPct": round(changed * 100 / pixels, 6),
        "p95ChannelDifference": percentile_from_histogram(combined, 0.95),
        "maxChannelDifference": max((i for i, count in enumerate(combined) if count), default=0),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--threshold", type=int, default=4)
    parser.add_argument("--diff", type=Path)
    args = parser.parse_args()
    if not 0 <= args.threshold <= 255:
        parser.error("--threshold must be between 0 and 255")

    try:
        result = compare(args.source, args.candidate, args.threshold, args.diff)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
