#!/usr/bin/env python3
"""Build the labeled A-G case overview used for customer template selection."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


SKILL_DIR = Path(__file__).resolve().parent.parent
CASE_DIR = SKILL_DIR / "assets" / "cases"
OUTPUT = SKILL_DIR / "assets" / "template-catalog.jpg"
ITEMS = [
    ("A｜香槟金编辑感", "A-香槟金编辑感.png"),
    ("B｜江景画册感", "B-江景画册感.png"),
    ("C｜深蓝电影感", "C-深蓝电影感.png"),
    ("D｜米白楼书感", "D-米白楼书感.png"),
    ("E｜侧栏分割", "E-侧栏分割.png"),
    ("F｜画册窗景", "F-画册窗景.png"),
    ("G｜证据卡片", "G-证据卡片.png"),
]


def font_path() -> str:
    for name in ("msyhbd.ttc", "msyh.ttc", "simhei.ttf"):
        candidate = Path(r"C:\Windows\Fonts") / name
        if candidate.is_file():
            return str(candidate)
    raise SystemExit("No supported Chinese font found")


def main():
    width, height = 1800, 2310
    sheet = Image.new("RGB", (width, height), (235, 231, 222))
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.truetype(font_path(), 52)
    label_font = ImageFont.truetype(font_path(), 34)
    draw.text((70, 42), "房产封面固定模板 A–G", font=title_font, fill=(13, 31, 52))

    tile_size = (500, 667)
    x_positions = (70, 650, 1230)
    y_positions = (150, 870, 1590)
    for index, (label, filename) in enumerate(ITEMS):
        row, col = divmod(index, 3)
        x, y = x_positions[col], y_positions[row]
        path = CASE_DIR / filename
        if not path.is_file():
            raise SystemExit(f"Missing case image: {path}")
        with Image.open(path) as opened:
            case = ImageOps.exif_transpose(opened).convert("RGB")
        case = ImageOps.fit(case, tile_size, method=Image.Resampling.LANCZOS)
        sheet.paste(case, (x, y + 54))
        draw.text((x, y), label, font=label_font, fill=(13, 31, 52))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT, "JPEG", quality=93, subsampling=0)
    print(OUTPUT)


if __name__ == "__main__":
    main()
