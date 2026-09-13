"""Compose deterministic bilingual cover typography on a 2.35:1 background."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from cover_quality import BASE_CANVAS, THEMES, audit_background, parse_color

LATIN_RUN = re.compile(r"[A-Za-z0-9+./-]+|\s+")
TITLE_MAX_WIDTH = 500


def load_font(path: Path, base_size: int, scale: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), max(8, round(base_size * scale)))


def draw_bilingual(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    chinese_font: ImageFont.FreeTypeFont,
    latin_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
) -> None:
    """Draw Chinese and Latin runs with explicit fonts instead of fallback glyphs."""
    cursor = position[0]
    for run in re.findall(r"[A-Za-z0-9+./-]+|\s+|[^A-Za-z0-9+./\-\s]+", text):
        face = latin_font if LATIN_RUN.fullmatch(run) else chinese_font
        draw.text((cursor, position[1]), run, font=face, fill=fill)
        cursor += round(draw.textlength(run, font=face))


def bilingual_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    chinese_font: ImageFont.FreeTypeFont,
    latin_font: ImageFont.FreeTypeFont,
) -> int:
    return sum(
        round(draw.textlength(run, font=latin_font if LATIN_RUN.fullmatch(run) else chinese_font))
        for run in re.findall(r"[A-Za-z0-9+./-]+|\s+|[^A-Za-z0-9+./\-\s]+", text)
    )


def fit_bilingual_fonts(
    draw: ImageDraw.ImageDraw,
    texts: list[str],
    chinese_path: Path,
    latin_path: Path,
    preferred_size: int,
    minimum_size: int,
    scale: float,
    maximum_width: int,
) -> tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
    """Keep a title group inside its safe field without changing its supplied text."""
    for size in range(preferred_size, minimum_size - 1, -1):
        chinese_font = load_font(chinese_path, size, scale)
        latin_font = load_font(latin_path, size, scale)
        if all(not text or bilingual_width(draw, text, chinese_font, latin_font) <= maximum_width for text in texts):
            return chinese_font, latin_font
    raise ValueError(
        "title line exceeds the left safe field at the minimum permitted type size; "
        "supply a semantic line break instead of overlapping the background"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--theme", required=True, type=int, choices=range(1, 14))
    parser.add_argument("--font", required=True, type=Path, help="Path to a local Chinese font")
    parser.add_argument("--latin-font", required=True, type=Path, help="Path to a local Latin/English font")
    parser.add_argument("--eyebrow", help="Optional eyebrow; defaults to the theme label")
    parser.add_argument("--title-prefix", default="", help="Exact title prefix, for example Ab-mRNA-LNP")
    parser.add_argument("--title", default="in vivo CAR-T", help="Exact main title line 1")
    parser.add_argument("--title-line2", default="", help="Exact main title line 2; use an empty string to omit")
    parser.add_argument("--subtitle-line1", default="抗体偶联 LNP", help="First subtitle line; use an empty string to omit")
    parser.add_argument("--subtitle-line2", default="技术路径深度研究", help="Second subtitle line; use an empty string to omit")
    parser.add_argument("--footer", default="抗体精准定位  ·  mRNA  ·  体内生成 CAR-T", help="Short footer; use an empty string to omit")
    parser.add_argument("--crop-16-9", action="store_true", help="Center-crop a 16:9 source to the canonical 2.35:1 cover before overlaying text")
    args = parser.parse_args()

    image = Image.open(args.input).convert("RGB")
    if args.crop_16_9:
        width, height = image.size
        target_height = round(width / (BASE_CANVAS[0] / BASE_CANVAS[1]))
        if height < target_height:
            raise ValueError(f"cannot crop {width}x{height} to 2.35:1 without upscaling")
        top = (height - target_height) // 2
        image = image.crop((0, top, width, top + target_height)).resize(BASE_CANVAS, Image.Resampling.LANCZOS)
    width, height = image.size
    scale_x = width / BASE_CANVAS[0]
    scale_y = height / BASE_CANVAS[1]
    scale_font = min(scale_x, scale_y)
    issues = audit_background(image, args.theme)
    if issues:
        raise ValueError("background failed title quality gate: " + "; ".join(issues))

    chinese_path = args.font.resolve()
    latin_path = args.latin_font.resolve()
    for label, font_path in (("Chinese", chinese_path), ("Latin/English", latin_path)):
        if not font_path.is_file():
            raise FileNotFoundError(f"{label} font not found: {font_path}")

    draw = ImageDraw.Draw(image)
    profile = THEMES[args.theme]
    eyebrow = args.eyebrow if args.eyebrow is not None else profile.label
    zh_small, latin_small = fit_bilingual_fonts(
        draw,
        [eyebrow],
        chinese_path,
        latin_path,
        25,
        18,
        scale_font,
        round(TITLE_MAX_WIDTH * scale_x),
    )
    zh_prefix, latin_prefix = fit_bilingual_fonts(
        draw, [args.title_prefix], chinese_path, latin_path, 46, 38, scale_font, round(TITLE_MAX_WIDTH * scale_x)
    )
    zh_main, latin_main = fit_bilingual_fonts(
        draw, [args.title, args.title_line2], chinese_path, latin_path, 62, 52, scale_font, round(TITLE_MAX_WIDTH * scale_x)
    )
    zh_sub, latin_sub = fit_bilingual_fonts(
        draw,
        [args.subtitle_line1, args.subtitle_line2],
        chinese_path,
        latin_path,
        34,
        26,
        scale_font,
        round(TITLE_MAX_WIDTH * scale_x),
    )
    zh_footer, latin_footer = fit_bilingual_fonts(
        draw,
        [args.footer],
        chinese_path,
        latin_path,
        20,
        16,
        scale_font,
        round(TITLE_MAX_WIDTH * scale_x),
    )
    x = round(76 * scale_x)
    y = lambda base: round(base * scale_y)

    if eyebrow:
        draw_bilingual(draw, (x, y(96)), eyebrow, zh_small, latin_small, parse_color(profile.accent))
    if args.title_prefix:
        draw_bilingual(draw, (x, y(140)), args.title_prefix, zh_prefix, latin_prefix, parse_color(profile.main))
    if args.title:
        draw_bilingual(draw, (x, y(210)), args.title, zh_main, latin_main, parse_color(profile.main))
    if args.title_line2:
        draw_bilingual(draw, (x, y(288)), args.title_line2, zh_main, latin_main, parse_color(profile.main))
    if args.subtitle_line1:
        draw_bilingual(draw, (x, y(398)), args.subtitle_line1, zh_sub, latin_sub, parse_color(profile.sub))
    if args.subtitle_line2:
        draw_bilingual(draw, (x, y(445)), args.subtitle_line2, zh_sub, latin_sub, parse_color(profile.sub))
    if args.footer:
        draw_bilingual(draw, (x, y(548)), args.footer, zh_footer, latin_footer, parse_color(profile.footer))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, quality=96)


if __name__ == "__main__":
    main()
