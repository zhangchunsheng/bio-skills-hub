#!/usr/bin/env python3
"""Crop an image to exact 3:4 and export a 1200x1600 PNG."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Center-crop an image to an exact portrait ratio and resize it."
    )
    parser.add_argument("input", type=Path, help="Source image path")
    parser.add_argument("output", type=Path, help="Destination PNG path")
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=1600)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacement of an existing destination file",
    )
    return parser.parse_args()


def crop_box(
    source_width: int, source_height: int, target_ratio: float
) -> tuple[int, int, int, int]:
    source_ratio = source_width / source_height
    if source_ratio > target_ratio:
        crop_width = round(source_height * target_ratio)
        left = (source_width - crop_width) // 2
        return left, 0, left + crop_width, source_height

    crop_height = round(source_width / target_ratio)
    top = (source_height - crop_height) // 2
    return 0, top, source_width, top + crop_height


def main() -> None:
    args = parse_args()
    if args.width <= 0 or args.height <= 0:
        raise SystemExit("width and height must be positive integers")
    if not args.input.is_file():
        raise SystemExit(f"input image does not exist: {args.input}")
    if args.output.exists() and not args.overwrite:
        raise SystemExit(f"output already exists: {args.output}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    target_ratio = args.width / args.height

    with Image.open(args.input) as opened:
        image = ImageOps.exif_transpose(opened)
        box = crop_box(image.width, image.height, target_ratio)
        cropped = image.crop(box)
        resized = cropped.resize((args.width, args.height), Image.Resampling.LANCZOS)

        if resized.mode not in {"RGB", "RGBA"}:
            resized = resized.convert("RGBA" if "A" in resized.getbands() else "RGB")

        resized.save(args.output, format="PNG", optimize=True)

    print(f"saved={args.output.resolve()}")
    print(f"size={args.width}x{args.height}")


if __name__ == "__main__":
    main()
