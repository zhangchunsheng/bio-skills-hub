#!/usr/bin/env python3
"""Render one of seven responsive 3:4 real-estate cover template families."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


CANVAS = (1200, 1600)
NAVY = (9, 24, 43, 255)
DEEP_BLUE = (4, 16, 33, 255)
WHITE = (252, 251, 247, 255)
CREAM = (245, 240, 230, 255)
PAPER = (250, 247, 239, 255)
INK = (13, 31, 52, 255)
DEFAULT_GOLD = (218, 178, 88, 255)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render responsive A-G real-estate cover templates as a 1200x1600 PNG."
    )
    parser.add_argument("input", type=Path, help="Current project's primary image")
    parser.add_argument("output", type=Path, help="Destination PNG")
    parser.add_argument("--template", required=True, choices=tuple("ABCDEFG"))
    parser.add_argument("--secondary", type=Path, help="Current project's presenter or second evidence image")
    parser.add_argument(
        "--line",
        action="append",
        required=True,
        help="Exact title or semantic chunk; repeat as needed. Line breaks are adaptive by default.",
    )
    parser.add_argument(
        "--keep-lines",
        action="store_true",
        help="Lock the supplied --line breaks while still fitting size and leading responsively.",
    )
    parser.add_argument("--highlight", action="append", default=[], help="Exact title substring to accent")
    parser.add_argument("--focus-x", type=float, default=0.5)
    parser.add_argument("--focus-y", type=float, default=0.5)
    parser.add_argument("--secondary-focus-x", type=float, default=0.5)
    parser.add_argument("--secondary-focus-y", type=float, default=0.5)
    parser.add_argument("--accent", default="#DAB258")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def available_font(*names: str) -> str:
    root = Path(r"C:\Windows\Fonts")
    for name in names:
        candidate = root / name
        if candidate.is_file():
            return str(candidate)
    raise SystemExit("No supported Chinese font found in C:\\Windows\\Fonts")


FONT_MEDIUM = available_font("msyh.ttc", "Noto Sans SC Medium (TrueType).otf", "simhei.ttf")
FONT_BOLD = available_font("msyhbd.ttc", "Noto Sans SC Bold (TrueType).otf", "simhei.ttf")
FONT_SERIF = available_font("Source Han Serif SC Heavy (TrueType).ttf", "simsun.ttc")
FONT_SYMBOL = available_font("msyhbd.ttc", "msyh.ttc", "simhei.ttf")


def open_image(path: Path) -> Image.Image:
    if not path.is_file():
        raise SystemExit(f"input image does not exist: {path}")
    with Image.open(path) as opened:
        return ImageOps.exif_transpose(opened).convert("RGB")


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def fitted(image: Image.Image, size: tuple[int, int], focus=(0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(
        image,
        size,
        method=Image.Resampling.LANCZOS,
        centering=(clamp(focus[0]), clamp(focus[1])),
    ).convert("RGBA")


def rounded_photo(image: Image.Image, size, radius, focus=(0.5, 0.5)) -> Image.Image:
    photo = fitted(image, size, focus)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    photo.putalpha(mask)
    return photo


def gradient(size, start, end, horizontal=False):
    width, height = size
    strip = Image.new("RGBA", (width if horizontal else 1, 1 if horizontal else height))
    pixels = strip.load()
    count = width if horizontal else height
    for index in range(count):
        ratio = index / max(1, count - 1)
        rgba = tuple(round(start[i] * (1 - ratio) + end[i] * ratio) for i in range(4))
        if horizontal:
            pixels[index, 0] = rgba
        else:
            pixels[0, index] = rgba
    return strip.resize(size)


def add_shadow(canvas: Image.Image, box, radius=28, opacity=75, blur=24, offset=(0, 14)):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shifted = tuple(v + offset[i % 2] for i, v in enumerate(box))
    ImageDraw.Draw(layer).rounded_rectangle(shifted, radius=radius, fill=(0, 0, 0, opacity))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


@lru_cache(maxsize=4096)
def font_for_char(char: str, primary: str, size: int):
    path = FONT_SYMBOL if char in "㎡，。！？；：、%+—–" else primary
    return ImageFont.truetype(path, size)


def highlighted_indices(value: str, highlights: list[str]) -> set[int]:
    indices: set[int] = set()
    for term in highlights:
        start = 0
        while term and (match := value.find(term, start)) >= 0:
            indices.update(range(match, match + len(term)))
            start = match + len(term)
    return indices


def measure(draw: ImageDraw.ImageDraw, value: str, primary: str, size: int) -> float:
    return sum(draw.textlength(char, font=font_for_char(char, primary, size)) for char in value)


def draw_line(draw, xy, value, primary, size, normal, accent, highlights, shadow=False):
    x, y = xy
    marked = highlighted_indices(value, highlights)
    for index, char in enumerate(value):
        typeface = font_for_char(char, primary, size)
        color = accent if index in marked else normal
        if shadow:
            draw.text((x + 3, y + 4), char, font=typeface, fill=(0, 0, 0, 90))
        draw.text((x, y), char, font=typeface, fill=color)
        x += draw.textlength(char, font=typeface)
    return x


OPEN_PUNCTUATION = set("（《【“‘「『")
CLOSE_PUNCTUATION = set("，。！？；：、）》】”’」』")
NUMBER_TOKEN = re.compile(r"\d+(?:\.\d+)?(?:㎡|m²|m2|万|亿|%|年|层|套|元|公里|分钟|秒)?", re.I)


@dataclass(frozen=True)
class Atom:
    value: str
    start: int
    end: int


@dataclass
class TextPlan:
    zone: str
    box: tuple[int, int, int, int]
    lines: list[str]
    sizes: list[int]
    fonts: list[str]
    hero_index: int
    leading: float
    score: float
    container_box: tuple[int, int, int, int] | None = None
    evidence_box: tuple[int, int, int, int] | None = None

    @property
    def height(self) -> float:
        return sum(size * self.leading for size in self.sizes)


@dataclass(frozen=True)
class TextZone:
    name: str
    box: tuple[int, int, int, int]
    max_lines: int
    max_size: int
    min_hero_size: int
    body_font: str
    hero_font: str
    leading: float = 1.12


def canonical(value: str) -> str:
    return "".join(value.split())


def visible_length(value: str) -> int:
    return len(canonical(value))


def title_text(chunks: list[str]) -> str:
    return "".join(chunk.strip() for chunk in chunks if chunk.strip())


def build_atoms(chunks: list[str], highlights: list[str]) -> tuple[list[Atom], set[int]]:
    clean_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    value = "".join(clean_chunks)
    semantic_breaks: set[int] = set()
    cursor = 0
    for chunk in clean_chunks[:-1]:
        cursor += len(chunk)
        semantic_breaks.add(cursor)

    protected = sorted(
        {term for term in highlights if term and 1 < len(term) <= 8 and term in value},
        key=len,
        reverse=True,
    )
    atoms: list[Atom] = []
    index = 0
    while index < len(value):
        matched = next((term for term in protected if value.startswith(term, index)), None)
        if matched:
            atoms.append(Atom(matched, index, index + len(matched)))
            index += len(matched)
            continue
        number = NUMBER_TOKEN.match(value, index)
        if number:
            atoms.append(Atom(number.group(0), index, number.end()))
            index = number.end()
            continue
        char = value[index]
        if char.isascii() and (char.isalpha() or char in "_#"):
            end = index + 1
            while end < len(value) and value[end].isascii() and (value[end].isalnum() or value[end] in "_#-/"):
                end += 1
            atoms.append(Atom(value[index:end], index, end))
            index = end
            continue
        atoms.append(Atom(char, index, index + 1))
        index += 1
    return atoms, semantic_breaks


def preferred_line_count(length: int, maximum: int) -> int:
    if length <= 5:
        target = 1
    elif length <= 10:
        target = 2
    elif length <= 16:
        target = 3
    elif length <= 23:
        target = 4
    else:
        target = 5
    return max(1, min(maximum, target))


def partition_atoms(
    draw: ImageDraw.ImageDraw,
    atoms: list[Atom],
    line_count: int,
    font_path: str,
    semantic_breaks: set[int],
) -> tuple[list[str], float] | None:
    if line_count < 1 or line_count > len(atoms):
        return None
    segment_cache: dict[tuple[int, int], tuple[str, float]] = {}

    def segment(start: int, end: int) -> tuple[str, float]:
        key = (start, end)
        if key not in segment_cache:
            value = "".join(atom.value for atom in atoms[start:end]).strip()
            segment_cache[key] = (value, measure(draw, value, font_path, 100))
        return segment_cache[key]

    total_width = sum(measure(draw, atom.value, font_path, 100) for atom in atoms)
    target_width = total_width / line_count
    states: dict[tuple[int, int], tuple[float, list[str]]] = {(0, 0): (0.0, [])}
    for used in range(line_count):
        for start in range(len(atoms)):
            state = states.get((used, start))
            if state is None:
                continue
            max_end = len(atoms) - (line_count - used - 1)
            for end in range(start + 1, max_end + 1):
                value, width = segment(start, end)
                if not value:
                    continue
                cost = ((width - target_width) / max(1.0, target_width)) ** 2 * 100.0
                if visible_length(value) <= 1 and line_count > 1:
                    cost += 280.0
                if value[0] in CLOSE_PUNCTUATION:
                    cost += 220.0
                if value[-1] in OPEN_PUNCTUATION:
                    cost += 220.0
                if atoms[end - 1].end in semantic_breaks and end < len(atoms):
                    cost -= 32.0
                if used == line_count - 1 and width < target_width * 0.42:
                    cost += 45.0
                new_cost = state[0] + cost
                key = (used + 1, end)
                if key not in states or new_cost < states[key][0]:
                    states[key] = (new_cost, state[1] + [value])
    return states.get((line_count, len(atoms)))


def choose_hero(lines: list[str], highlights: list[str]) -> int:
    for term in sorted((term for term in highlights if term), key=len, reverse=True):
        for index, line in enumerate(lines):
            if term in line:
                return index
    if len(lines) == 1:
        return 0
    last_length = visible_length(lines[-1])
    average = sum(visible_length(line) for line in lines) / len(lines)
    if last_length <= max(8, average * 1.25):
        return len(lines) - 1
    return min(range(len(lines)), key=lambda index: visible_length(lines[index]))


def evaluate_plan(
    draw: ImageDraw.ImageDraw,
    zone: TextZone,
    lines: list[str],
    partition_cost: float,
    highlights: list[str],
) -> TextPlan | None:
    if not lines:
        return None
    hero_index = choose_hero(lines, highlights)
    multipliers: list[float] = []
    for index, line in enumerate(lines):
        if index == hero_index:
            multiplier = 1.0
        elif len(lines) == 2:
            multiplier = 0.76
        elif visible_length(line) <= 4:
            multiplier = 0.66
        else:
            multiplier = 0.74
        multipliers.append(multiplier)
    fonts = [zone.hero_font if index == hero_index else zone.body_font for index in range(len(lines))]
    desired = [max(24, round(zone.max_size * multiplier)) for multiplier in multipliers]
    width = zone.box[2] - zone.box[0]
    height = zone.box[3] - zone.box[1]
    width_scales = [
        width / max(1.0, measure(draw, line, fonts[index], desired[index]))
        for index, line in enumerate(lines)
    ]
    height_scale = height / max(1.0, sum(size * zone.leading for size in desired))
    scale = min(1.0, height_scale, *width_scales)
    sizes = [max(1, int(size * scale)) for size in desired]
    minimum_body = max(28, round(zone.min_hero_size * 0.64))
    if sizes[hero_index] < zone.min_hero_size or any(size < minimum_body for size in sizes):
        return None
    widths = [measure(draw, line, fonts[index], sizes[index]) / max(1.0, width) for index, line in enumerate(lines)]
    raggedness = sum((line_width - sum(widths) / len(widths)) ** 2 for line_width in widths)
    preferred = preferred_line_count(visible_length("".join(lines)), zone.max_lines)
    score = (
        sizes[hero_index] * 1.35
        + sum(sizes) / len(sizes)
        - partition_cost * 0.12
        - abs(len(lines) - preferred) * 7.0
        - raggedness * 28.0
    )
    return TextPlan(zone.name, zone.box, lines, sizes, fonts, hero_index, zone.leading, score)


def plan_text(
    draw: ImageDraw.ImageDraw,
    chunks: list[str],
    zone: TextZone,
    highlights: list[str],
    keep_lines: bool,
) -> TextPlan:
    atoms, semantic_breaks = build_atoms(chunks, highlights)
    if not atoms:
        raise SystemExit("Title is empty after normalization")
    candidates: list[TextPlan] = []
    if keep_lines:
        locked = [chunk.strip() for chunk in chunks if chunk.strip()]
        if len(locked) > zone.max_lines:
            raise SystemExit(
                f"{zone.name} supports at most {zone.max_lines} locked lines; remove --keep-lines or use fewer --line values"
            )
        plan = evaluate_plan(draw, zone, locked, 0.0, highlights)
        if plan:
            candidates.append(plan)
    else:
        for count in range(1, min(zone.max_lines, len(atoms)) + 1):
            partition = partition_atoms(draw, atoms, count, zone.body_font, semantic_breaks)
            if partition is None:
                continue
            cost, lines = partition
            plan = evaluate_plan(draw, zone, lines, cost, highlights)
            if plan:
                candidates.append(plan)
    if not candidates:
        raise SystemExit(
            f"Title cannot fit {zone.name} legibly. Keep the exact wording but choose a roomier core template or an open layout."
        )
    return max(candidates, key=lambda candidate: candidate.score)


def draw_plan(
    draw: ImageDraw.ImageDraw,
    zone: TextZone,
    plan: TextPlan,
    normal,
    accent,
    highlights,
    shadow=False,
    vertical="top",
):
    left, top, right, bottom = zone.box
    if vertical == "bottom":
        y = bottom - plan.height
    elif vertical == "center":
        y = top + ((bottom - top) - plan.height) / 2
    else:
        y = top
    start_y = y
    for index, value in enumerate(plan.lines):
        draw_line(
            draw,
            (left, round(y)),
            value,
            plan.fonts[index],
            plan.sizes[index],
            normal,
            accent,
            highlights,
            shadow,
        )
        y += plan.sizes[index] * plan.leading
    return (left, round(start_y), right, round(y))


def split_title_plans(
    draw: ImageDraw.ImageDraw,
    chunks: list[str],
    top_zone: TextZone,
    bottom_zone: TextZone,
    highlights: list[str],
    keep_lines: bool,
) -> tuple[TextPlan | None, TextPlan]:
    clean = [chunk.strip() for chunk in chunks if chunk.strip()]
    full = title_text(clean)

    def sliced(start: int, end: int) -> list[str]:
        selected: list[str] = []
        cursor = 0
        for chunk in clean:
            chunk_end = cursor + len(chunk)
            local_start = max(start, cursor) - cursor
            local_end = min(end, chunk_end) - cursor
            if local_start < local_end:
                selected.append(chunk[local_start:local_end])
            cursor = chunk_end
        return selected

    if keep_lines:
        if len(clean) > 1:
            splits: list[tuple[list[str], list[str], bool]] = [
                (clean[:index], clean[index:], True) for index in range(1, len(clean))
            ]
        else:
            splits = [([], clean, False)]
    else:
        atoms, semantic_breaks = build_atoms(chunks, highlights)
        splits = []
        if visible_length(full) <= 8:
            splits.append(([], clean, False))
        else:
            for index in range(1, len(atoms)):
                split_at = atoms[index - 1].end
                top_chunks = sliced(0, split_at)
                bottom_chunks = sliced(split_at, len(full))
                ratio = visible_length(title_text(top_chunks)) / max(1, visible_length(full))
                if (
                    visible_length(title_text(top_chunks)) < 2
                    or visible_length(title_text(bottom_chunks)) < 2
                    or not 0.22 <= ratio <= 0.58
                ):
                    continue
                semantic = split_at in semantic_breaks
                splits.append((top_chunks, bottom_chunks, semantic))

    best: tuple[float, TextPlan | None, TextPlan] | None = None
    for top_chunks, bottom_chunks, semantic in splits:
        try:
            top_plan = plan_text(draw, top_chunks, top_zone, highlights, keep_lines) if top_chunks else None
            bottom_plan = plan_text(draw, bottom_chunks, bottom_zone, highlights, keep_lines)
        except SystemExit:
            continue
        ratio = visible_length(title_text(top_chunks)) / max(1, visible_length(full))
        score = bottom_plan.score + (top_plan.score if top_plan else 0.0)
        if semantic:
            score += 22.0
        if top_plan:
            score -= abs(ratio - 0.42) * 34.0
        elif visible_length(full) > 8:
            score -= 80.0
        if best is None or score > best[0]:
            best = (score, top_plan, bottom_plan)
    if best is None:
        return None, plan_text(draw, clean, bottom_zone, highlights, keep_lines)
    return best[1], best[2]


def template_a(primary, lines, accent, highlights, focus, keep_lines):
    canvas = fitted(primary, CANVAS, focus)
    draw = ImageDraw.Draw(canvas)
    top_zone = TextZone("A-top", (68, 62, 1100, 520), 3, 126, 50, FONT_MEDIUM, FONT_BOLD, 1.08)
    bottom_zone = TextZone("A-bottom", (66, 1035, 1125, 1535), 4, 148, 54, FONT_SERIF, FONT_BOLD, 1.08)
    top, bottom = split_title_plans(draw, lines, top_zone, bottom_zone, highlights, keep_lines)
    top_support_height = round(max(260, min(620, (top.height if top else 0) + 150)))
    bottom_support_top = round(max(800, min(1160, 1600 - bottom.height - 210)))
    canvas = Image.alpha_composite(canvas, gradient(CANVAS, (5, 16, 31, 180), (5, 16, 31, 0), True))
    canvas.alpha_composite(
        gradient((1200, top_support_height), (5, 14, 28, 115), (5, 14, 28, 0)),
        (0, 0),
    )
    canvas.alpha_composite(
        gradient((1200, 1600 - bottom_support_top), (5, 14, 28, 0), (5, 14, 28, 205)),
        (0, bottom_support_top),
    )
    draw = ImageDraw.Draw(canvas)
    bottom.container_box = (0, bottom_support_top, 1200, 1600)
    if top:
        top.container_box = (0, 0, 1200, top_support_height)
    plans = []
    if top:
        bounds = draw_plan(draw, top_zone, top, WHITE, accent, highlights, True)
        rule_y = min(top_zone.box[3] - 10, bounds[3] + 18)
        plans.append(top)
    else:
        rule_y = 102
    draw.rounded_rectangle((70, rule_y, 410, rule_y + 11), radius=5, fill=accent)
    draw_plan(draw, bottom_zone, bottom, WHITE, accent, highlights, True, "bottom")
    plans.append(bottom)
    return canvas, plans


def template_b(primary, secondary, lines, accent, highlights, focus, second_focus, keep_lines):
    canvas = fitted(primary, CANVAS, focus)
    length = visible_length(title_text(lines))
    draw = ImageDraw.Draw(canvas)
    choices: list[tuple[float, int, TextZone, TextPlan]] = []
    for panel_bottom in (370, 430, 520, 610, 700, 790, 880, 970):
        zone = TextZone(
            "B-title",
            (90, 88, 1100, panel_bottom - 70),
            5,
            150 if length <= 10 else 132,
            46,
            FONT_BOLD,
            FONT_SERIF,
            1.10,
        )
        try:
            candidate = plan_text(draw, lines, zone, highlights, keep_lines)
        except SystemExit:
            continue
        container_penalty = (panel_bottom - 370) * 0.045
        empty_ratio = max(0.0, ((zone.box[3] - zone.box[1]) - candidate.height) / max(1.0, zone.box[3] - zone.box[1]))
        score = candidate.score - container_penalty - empty_ratio * 8.0
        choices.append((score, panel_bottom, zone, candidate))
    if not choices:
        raise SystemExit("Title cannot fit B with a readable text-card relationship; use F or an open layout")
    _, panel_bottom, zone, plan = max(choices, key=lambda item: item[0])
    panel_box = (48, 52, 1152, panel_bottom)
    panel = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle(panel_box, radius=34, fill=(249, 247, 241, 232))
    canvas = Image.alpha_composite(canvas, panel)
    draw = ImageDraw.Draw(canvas)
    draw_plan(draw, zone, plan, INK, accent, highlights, False, "center")
    draw.line((92, panel_bottom - 52, 650, panel_bottom - 52), fill=accent, width=9)
    inset_y = max(panel_bottom + 65, 860)
    inset_height = min(480, 1530 - inset_y)
    inset_box = (820, inset_y, 1135, inset_y + inset_height)
    add_shadow(canvas, inset_box, radius=25, opacity=90)
    canvas.alpha_composite(rounded_photo(secondary, (315, inset_height), 25, second_focus), (820, inset_y))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(inset_box, radius=25, outline=accent, width=4)
    plan.container_box = panel_box
    plan.evidence_box = inset_box
    return canvas, [plan]


def template_c(primary, lines, accent, highlights, focus, keep_lines):
    canvas = fitted(primary, CANVAS, focus)
    draw = ImageDraw.Draw(canvas)
    top_zone = TextZone("C-top", (68, 70, 1100, 510), 3, 120, 48, FONT_MEDIUM, FONT_BOLD, 1.08)
    bottom_zone = TextZone("C-bottom", (66, 1045, 1120, 1535), 4, 144, 52, FONT_SERIF, FONT_BOLD, 1.08)
    top, bottom = split_title_plans(draw, lines, top_zone, bottom_zone, highlights, keep_lines)
    top_support_height = round(max(270, min(620, (top.height if top else 0) + 155)))
    bottom_support_top = round(max(790, min(1160, 1600 - bottom.height - 220)))
    canvas = Image.alpha_composite(canvas, gradient(CANVAS, (3, 15, 33, 215), (3, 15, 33, 5), True))
    canvas.alpha_composite(
        gradient((1200, top_support_height), (2, 10, 24, 125), (2, 10, 24, 0)),
        (0, 0),
    )
    canvas.alpha_composite(
        gradient((1200, 1600 - bottom_support_top), (2, 10, 24, 0), (2, 10, 24, 200)),
        (0, bottom_support_top),
    )
    draw = ImageDraw.Draw(canvas)
    bottom.container_box = (0, bottom_support_top, 1200, 1600)
    if top:
        top.container_box = (0, 0, 1200, top_support_height)
    plans = []
    if top:
        bounds = draw_plan(draw, top_zone, top, WHITE, accent, highlights, True)
        rule_y = min(top_zone.box[3] - 10, bounds[3] + 18)
        plans.append(top)
    else:
        rule_y = 108
    draw.rounded_rectangle((70, rule_y, 430, rule_y + 11), radius=5, fill=accent)
    draw_plan(draw, bottom_zone, bottom, WHITE, accent, highlights, True, "bottom")
    plans.append(bottom)
    return canvas, plans


def template_d(primary, secondary, lines, accent, highlights, focus, second_focus, keep_lines):
    canvas = fitted(primary, CANVAS, focus)
    draw = ImageDraw.Draw(canvas)
    choices = []
    for panel_top in (1100, 1040, 980, 920, 860):
        top_zone = TextZone(
            "D-top",
            (68, 65, 1080, min(520, panel_top - 115)),
            3,
            116,
            46,
            FONT_MEDIUM,
            FONT_BOLD,
            1.08,
        )
        for mode in ("overlap", "lifted"):
            if mode == "overlap":
                inset_box = (800, panel_top - 185, 1135, panel_top + 305)
                bottom_box = (62, panel_top + 55, 750, 1535)
                mode_bonus = 18.0
            else:
                inset_top = max(560, panel_top - 390)
                inset_box = (875, inset_top, 1135, inset_top + 360)
                bottom_box = (62, panel_top + 54, 1138, 1535)
                mode_bonus = 0.0
            bottom_zone = TextZone("D-bottom", bottom_box, 4, 138, 48, FONT_SERIF, FONT_BOLD, 1.08)
            try:
                top, bottom = split_title_plans(
                    draw,
                    lines,
                    top_zone,
                    bottom_zone,
                    highlights,
                    keep_lines,
                )
            except SystemExit:
                continue
            text_score = bottom.score + (top.score if top else 0.0)
            image_reward = panel_top * 0.04
            bottom_fill = bottom.height / max(1.0, bottom_zone.box[3] - bottom_zone.box[1])
            density_penalty = abs(bottom_fill - 0.68) * 45.0
            total_lines = len(bottom.lines) + (len(top.lines) if top else 0)
            overlap_penalty = 35.0 if mode == "overlap" and total_lines >= 5 else 0.0
            score = text_score + image_reward + mode_bonus - density_penalty - overlap_penalty
            choices.append(
                (score, panel_top, inset_box, top_zone, bottom_zone, top, bottom)
            )
    if not choices:
        raise SystemExit("Title cannot fit D with a readable card-and-evidence relationship; use F or an open layout")
    _, panel_top, inset_box, top_zone, bottom_zone, top, bottom = max(choices, key=lambda item: item[0])
    panel_box = (0, panel_top, 1200, 1600)
    ImageDraw.Draw(canvas).rectangle(panel_box, fill=CREAM)
    draw = ImageDraw.Draw(canvas)
    plans = []
    if top:
        draw_plan(draw, top_zone, top, WHITE, accent, highlights, True)
        plans.append(top)
    add_shadow(canvas, inset_box, radius=24, opacity=90)
    canvas.alpha_composite(
        rounded_photo(secondary, (inset_box[2] - inset_box[0], inset_box[3] - inset_box[1]), 24, second_focus),
        (inset_box[0], inset_box[1]),
    )
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(inset_box, radius=24, outline=accent, width=5)
    draw_plan(draw, bottom_zone, bottom, INK, accent, highlights, False, "bottom")
    plans.append(bottom)
    draw.rounded_rectangle((64, 1560, 550, 1571), radius=5, fill=accent)
    bottom.container_box = panel_box
    bottom.evidence_box = inset_box
    return canvas, plans


def template_e(primary, lines, accent, highlights, focus, keep_lines):
    canvas = ImageEnhance.Color(fitted(primary, CANVAS, focus).convert("RGB")).enhance(0.9).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    choices: list[tuple[float, int, TextZone, TextPlan]] = []
    for panel_right in (460, 510, 560, 610, 660):
        zone = TextZone("E-sidebar", (62, 92, panel_right - 100, 1240), 7, 118, 43, FONT_SERIF, FONT_BOLD, 1.14)
        try:
            candidate = plan_text(draw, lines, zone, highlights, keep_lines)
        except SystemExit:
            continue
        subject_space_penalty = (panel_right - 460) * 0.35
        preferred = preferred_line_count(visible_length(title_text(lines)), zone.max_lines)
        fragmentation_penalty = max(0, len(candidate.lines) - preferred) * 18.0
        score = candidate.score - subject_space_penalty - fragmentation_penalty
        choices.append((score, panel_right, zone, candidate))
    if not choices:
        raise SystemExit("Title cannot fit E while preserving the image subject; use F or an open layout")
    _, panel_right, zone, plan = max(choices, key=lambda item: item[0])
    panel = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.polygon(((0, 0), (panel_right, 0), (panel_right - 80, 1600), (0, 1600)), fill=(7, 22, 40, 245))
    pd.polygon(
        ((panel_right - 20, 0), (panel_right + 7, 0), (panel_right - 73, 1600), (panel_right - 100, 1600)),
        fill=accent,
    )
    canvas = Image.alpha_composite(canvas, panel)
    draw = ImageDraw.Draw(canvas)
    draw_plan(draw, zone, plan, WHITE, accent, highlights, False, "center")
    draw.rounded_rectangle((64, 1490, 275, 1501), radius=5, fill=accent)
    plan.container_box = (0, 0, panel_right, 1600)
    return canvas, [plan]


def template_f(primary, lines, accent, highlights, focus, keep_lines):
    canvas = Image.new("RGBA", CANVAS, PAPER)
    length = visible_length(title_text(lines))
    draw = ImageDraw.Draw(canvas)
    choices: list[tuple[float, int, int, TextZone, TextPlan]] = []
    for image_bottom in (1180, 1140, 1080, 1020, 950, 880, 810):
        text_top = image_bottom + 45
        zone = TextZone(
            "F-caption",
            (116, text_top, 1120, 1535),
            6,
            142 if length <= 10 else 126,
            43,
            FONT_BOLD,
            FONT_SERIF,
            1.08,
        )
        try:
            candidate = plan_text(draw, lines, zone, highlights, keep_lines)
        except SystemExit:
            continue
        text_fill = candidate.height / max(1.0, zone.box[3] - zone.box[1])
        image_reward = image_bottom * 0.09
        density_penalty = abs(text_fill - 0.58) * 50.0
        score = candidate.score + image_reward - density_penalty
        choices.append((score, image_bottom, text_top, zone, candidate))
    if not choices:
        raise SystemExit("Title cannot fit F without making the image or text illegible; use an open layout")
    _, image_bottom, text_top, zone, plan = max(choices, key=lambda item: item[0])
    image_box = (62, 62, 1138, image_bottom)
    add_shadow(canvas, image_box, radius=34, opacity=55, blur=28, offset=(0, 16))
    canvas.alpha_composite(rounded_photo(primary, (1076, image_bottom - 62), 34, focus), (62, 62))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(image_box, radius=34, outline=(195, 177, 140, 200), width=3)
    draw.rectangle((62, text_top, 82, 1520), fill=accent)
    draw_plan(draw, zone, plan, INK, accent, highlights, False, "center")
    plan.container_box = (0, image_bottom, 1200, 1600)
    plan.evidence_box = image_box
    return canvas, [plan]


def template_g(primary, secondary, lines, accent, highlights, focus, second_focus, keep_lines):
    canvas = Image.new("RGBA", CANVAS, NAVY)
    length = visible_length(title_text(lines))
    image_box = (54, 54, 1146, 990)
    draw = ImageDraw.Draw(canvas)
    variants = (
        ((825, 845, 1137, 1325), (68, 1045, 760, 1535), "compact"),
        ((850, 620, 1137, 980), (68, 1045, 1132, 1535), "wide"),
    )
    choices = []
    for inset_box, text_box, mode in variants:
        zone = TextZone("G-evidence", text_box, 5, 134 if length <= 10 else 118, 44, FONT_BOLD, FONT_SERIF, 1.09)
        try:
            candidate = plan_text(draw, lines, zone, highlights, keep_lines)
        except SystemExit:
            continue
        if mode == "compact":
            mode_adjustment = 12.0 if len(candidate.lines) <= 3 else -18.0
        else:
            mode_adjustment = 0.0
        score = candidate.score + mode_adjustment
        choices.append((score, inset_box, zone, candidate))
    if not choices:
        raise SystemExit("Title cannot fit G without colliding with the evidence card; use F or an open layout")
    _, inset_box, zone, plan = max(choices, key=lambda item: item[0])
    add_shadow(canvas, image_box, radius=30, opacity=90)
    canvas.alpha_composite(rounded_photo(primary, (1092, 936), 30, focus), (54, 54))
    add_shadow(canvas, inset_box, radius=26, opacity=120, blur=22)
    canvas.alpha_composite(
        rounded_photo(secondary, (inset_box[2] - inset_box[0], inset_box[3] - inset_box[1]), 26, second_focus),
        (inset_box[0], inset_box[1]),
    )
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(inset_box, radius=26, outline=accent, width=5)
    draw_plan(draw, zone, plan, WHITE, accent, highlights, False, "bottom")
    plan.container_box = (0, 990, 1200, 1600)
    plan.evidence_box = inset_box
    return canvas, [plan]


def render(args: argparse.Namespace) -> tuple[Image.Image, list[TextPlan]]:
    primary = open_image(args.input)
    secondary = open_image(args.secondary) if args.secondary else primary.copy()
    lines = [line.strip() for line in args.line if line.strip()]
    if not 1 <= len(lines) <= 8:
        raise SystemExit("Provide between 1 and 8 non-empty --line values")
    accent = ImageColor.getrgb(args.accent) + (255,)
    focus = (args.focus_x, args.focus_y)
    second_focus = (args.secondary_focus_x, args.secondary_focus_y)
    if args.template == "A":
        result = template_a(primary, lines, accent, args.highlight, focus, args.keep_lines)
    elif args.template == "B":
        result = template_b(primary, secondary, lines, accent, args.highlight, focus, second_focus, args.keep_lines)
    elif args.template == "C":
        result = template_c(primary, lines, accent, args.highlight, focus, args.keep_lines)
    elif args.template == "D":
        result = template_d(primary, secondary, lines, accent, args.highlight, focus, second_focus, args.keep_lines)
    elif args.template == "E":
        result = template_e(primary, lines, accent, args.highlight, focus, args.keep_lines)
    elif args.template == "F":
        result = template_f(primary, lines, accent, args.highlight, focus, args.keep_lines)
    elif args.template == "G":
        result = template_g(primary, secondary, lines, accent, args.highlight, focus, second_focus, args.keep_lines)
    rendered = "".join("".join(plan.lines) for plan in result[1])
    if canonical(rendered) != canonical(title_text(lines)):
        raise SystemExit("Responsive layout changed or duplicated title text; output was not saved")
    return result


def main() -> None:
    args = parse_args()
    if args.output.exists() and not args.overwrite:
        raise SystemExit(f"output already exists: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image, plans = render(args)
    image.convert("RGB").save(args.output, "PNG", optimize=True)
    print(f"saved={args.output.resolve()}")
    print(f"template={args.template}")
    print("size=1200x1600")
    print("identity=source-pixels-only")
    print(f"line_mode={'locked' if args.keep_lines else 'adaptive'}")
    for plan in plans:
        pairs = " | ".join(f"{line} ({size}px)" for line, size in zip(plan.lines, plan.sizes))
        print(f"layout[{plan.zone}]={pairs}")
        print(f"text_box[{plan.zone}]={plan.box}")
        if plan.container_box:
            print(f"container_box[{plan.zone}]={plan.container_box}")
        if plan.evidence_box:
            print(f"evidence_box[{plan.zone}]={plan.evidence_box}")


if __name__ == "__main__":
    main()
