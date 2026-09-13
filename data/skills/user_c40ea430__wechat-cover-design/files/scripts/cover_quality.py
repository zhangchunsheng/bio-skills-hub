"""Quality gates shared by the cover compositor and the standalone auditor."""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageFilter, ImageStat


BASE_CANVAS = (1584, 672)
TITLE_ZONE = (76, 88, 620, 585)


@dataclass(frozen=True)
class ThemePalette:
    label: str
    main: str
    accent: str
    sub: str
    footer: str


THEMES = {
    1: ThemePalette("主题 1 · 生物医学黏土封面", "#57392D", "#964A3C", "#57392D", "#57392D"),
    2: ThemePalette("主题 2 · Nature 科学意象", "#EDF8FA", "#FF7E73", "#EDF8FA", "#BFEFF5"),
    3: ThemePalette("主题 3 · Businessweek 商业隐喻", "#090909", "#B53732", "#090909", "#090909"),
    4: ThemePalette("主题 4 · Monocle 产业观察", "#285541", "#A94F3C", "#285541", "#285541"),
    5: ThemePalette("主题 5 · 显微纪录摄影", "#E6EEEE", "#36E562", "#E6EEEE", "#CCD2D1"),
    6: ThemePalette("主题 6 · Swiss 极简海报", "#111111", "#1749C6", "#111111", "#111111"),
    7: ThemePalette("主题 7 · 复古科学档案", "#22201D", "#A33D2E", "#22201D", "#22201D"),
    8: ThemePalette("主题 8 · 药物管线地图", "#0A2948", "#147F7B", "#0A2948", "#0A2948"),
    9: ThemePalette("主题 9 · 临床证据蓝图", "#12375C", "#FF6B21", "#12375C", "#52616B"),
    10: ThemePalette("主题 10 · Cell 机制图谱", "#EDF8FA", "#F0C45B", "#C7EEF5", "#8FCBD8"),
    11: ThemePalette("主题 11 · 医学大会主视觉", "#F0F8FA", "#D94A98", "#F0F8FA", "#48CED0"),
    12: ThemePalette("主题 12 · 分子蓝图", "#EDF8FA", "#F0C45B", "#C7EEF5", "#8FCBD8"),
    13: ThemePalette("主题 13 · 生物工艺工程", "#164B68", "#B37A28", "#164B68", "#164B68"),
}


def parse_color(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def relative_luminance(color: tuple[int, int, int]) -> float:
    channels = []
    for channel in color:
        value = channel / 255
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(first: float, second: float) -> float:
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def _scaled_title_zone(image: Image.Image) -> tuple[int, int, int, int]:
    width, height = image.size
    return (
        round(TITLE_ZONE[0] * width / BASE_CANVAS[0]),
        round(TITLE_ZONE[1] * height / BASE_CANVAS[1]),
        round(TITLE_ZONE[2] * width / BASE_CANVAS[0]),
        round(TITLE_ZONE[3] * height / BASE_CANVAS[1]),
    )


def _edge_component_metrics(gray: Image.Image) -> tuple[float, float, float]:
    """Measure connected high-contrast marks that would intrude on the title area."""
    edges = gray.filter(ImageFilter.FIND_EDGES)
    width, height = edges.size
    pixels = edges.load()
    threshold = 60
    active = {
        (x, y)
        for y in range(2, height - 2)
        for x in range(2, width - 2)
        if pixels[x, y] >= threshold
    }
    edge_coverage = len(active) / max(1, width * height)
    largest_width = largest_height = 0

    while active:
        start = active.pop()
        stack = [start]
        count = 1
        min_x = max_x = start[0]
        min_y = max_y = start[1]
        while stack:
            x, y = stack.pop()
            for neighbour in (
                (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                (x - 1, y), (x + 1, y),
                (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
            ):
                if neighbour not in active:
                    continue
                active.remove(neighbour)
                stack.append(neighbour)
                count += 1
                min_x = min(min_x, neighbour[0])
                max_x = max(max_x, neighbour[0])
                min_y = min(min_y, neighbour[1])
                max_y = max(max_y, neighbour[1])
        if count >= 80:
            largest_width = max(largest_width, max_x - min_x + 1)
            largest_height = max(largest_height, max_y - min_y + 1)

    return edge_coverage, largest_width / width, largest_height / height


def audit_report(image: Image.Image, theme_id: int) -> dict[str, object]:
    """Build an inspectable pass/fail report for a text-free source image."""
    width, height = image.size
    ratio = width / height
    if not 2.25 <= ratio <= 2.45:
        return {
            "status": "FAIL",
            "theme": theme_id,
            "issues": [f"expected a roughly 2.35:1 input image, got {width}x{height}"],
            "metrics": {},
        }

    zone = image.convert("RGB").crop(_scaled_title_zone(image))
    gray = zone.convert("L")
    values = list(gray.getdata())
    values.sort()
    low = values[max(0, round((len(values) - 1) * 0.10))]
    high = values[round((len(values) - 1) * 0.90)]
    texture = ImageStat.Stat(gray).stddev[0]
    edges = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).mean[0]
    edge_coverage, component_width, component_height = _edge_component_metrics(gray)

    palette = THEMES[theme_id]
    color_luminance = relative_luminance(parse_color(palette.main))
    # The 10th/90th percentile avoids rejecting a clean field for one isolated pixel,
    # while still catching a field whose normal texture makes the title unreadable.
    background_gray = low if color_luminance < 0.5 else high
    background_luminance = relative_luminance((background_gray, background_gray, background_gray))
    contrast = contrast_ratio(color_luminance, background_luminance)

    issues: list[str] = []
    if texture > 54:
        issues.append(f"title field is too textured (grayscale deviation {texture:.1f}; maximum 54)")
    if edges > 48:
        issues.append(f"title field has too many edges (edge score {edges:.1f}; maximum 48)")
    if edge_coverage > 0.035:
        issues.append(f"title field has too many high-contrast marks (edge coverage {edge_coverage:.3f}; maximum 0.035)")
    if component_width > 0.22 or component_height > 0.22:
        issues.append(
            "title field contains a long structured mark "
            f"({component_width:.0%} width, {component_height:.0%} height); regenerate the background"
        )
    if contrast < 4.5:
        issues.append(f"main title contrast is {contrast:.2f}:1; require at least 4.5:1")
    return {
        "status": "PASS" if not issues else "FAIL",
        "theme": theme_id,
        "issues": issues,
        "metrics": {
            "texture": round(texture, 2),
            "edge_score": round(edges, 2),
            "edge_coverage": round(edge_coverage, 4),
            "largest_component_width": round(component_width, 4),
            "largest_component_height": round(component_height, 4),
            "contrast": round(contrast, 2),
        },
    }


def audit_background(image: Image.Image, theme_id: int) -> list[str]:
    """Return blocking issues for a text-free source image before typography is drawn."""
    return list(audit_report(image, theme_id)["issues"])
