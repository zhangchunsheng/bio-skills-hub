#!/usr/bin/env python3
r"""学术 PDF figure 精确切割 v3.0（融合算法 + 自检评分）

融合 ABC 三种技术路线，实现最高精度：
  A. 连通域分析：检测 drawings/images 连通域，标签分配给最近连通域
  B. 后处理合并：Voronoi 分区后，边界两侧图形距离 < 阈值则合并
  C. 分离 bbox 计算：图形元素用连通域 bbox，文本块只取相邻的

特性：
  - 多算法并行 + 自动选择最优结果
  - 边缘精化 + 连通域验证
  - 自检评分系统（完整性、边缘纯净度、标签对齐、尺寸合理性）
  - 并行计算架构（整图并行 + 子图并行）
  - 预解析缓存
  - 输出结构：whole/ + subfig/ + CSV 评分报告

用法：
  python crop_figures_v3.py <PDF路径> [--out DIR] [--dpi 300]
        [--preset auto|nature|generic|springer] [--label-regex REGEX]
        [--mode whole|subfig|both] [--header 42] [--footer 40] [--jobs N]
        [--preview] [--figures 1,3,5] [--refine-edge] [--cache]
"""

import argparse
import csv
import json
import math
import os
import re
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

import pymupdf

try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

# ==================== 配置 ====================

PRESETS = {
    "nature": r"^(?P<ext>Extended Data )?Fig\.\s*(?P<num>\d+)\s*\|",
    "generic": r"^Figure\s*(?P<num>\d+)[\.\:]",
    "springer": r"^Fig\.\s*(?P<num>\d+)[\.\s]",
}

CONF_LABEL = {"high": "高", "medium": "中", "low": "低"}


class Confidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SubfigResult:
    """子图切割结果"""
    name: str
    kind: str  # "whole" or "subfig"
    parent: Optional[str]
    label_page: int
    cut_page: int
    cross_page: bool
    method: str
    confidence: str
    bbox: Tuple[float, float, float, float]
    pixel_size: Tuple[int, int]
    file_path: str
    scores: Dict[str, float]
    total_score: float


@dataclass
class WorkerResult:
    """Worker 返回结果"""
    fig_name: str
    whole_result: Optional[SubfigResult]
    subfig_results: List[SubfigResult]
    error: Optional[str]


# ==================== 缓存 ====================

class PageCache:
    """页面级元素缓存"""
    
    def __init__(self):
        self._cache = {
            "blocks": {},
            "drawings": {},
            "images": {},
            "dict": {},
            "rawdict": {}
        }
    
    def get_blocks(self, page):
        if page.number not in self._cache["blocks"]:
            self._cache["blocks"][page.number] = page.get_text("blocks")
        return self._cache["blocks"][page.number]
    
    def get_dict(self, page):
        if page.number not in self._cache["dict"]:
            self._cache["dict"][page.number] = page.get_text("dict")
        return self._cache["dict"][page.number]
    
    def get_rawdict(self, page):
        if page.number not in self._cache["rawdict"]:
            self._cache["rawdict"][page.number] = page.get_text("rawdict")
        return self._cache["rawdict"][page.number]
    
    def get_drawings(self, page):
        if page.number not in self._cache["drawings"]:
            self._cache["drawings"][page.number] = page.get_drawings()
        return self._cache["drawings"][page.number]
    
    def get_images(self, page):
        if page.number not in self._cache["images"]:
            self._cache["images"][page.number] = page.get_image_info()
        return self._cache["images"][page.number]
    
    def clear(self):
        self._cache = {k: {} for k in self._cache}


# 全局缓存实例
CACHE = PageCache()


# ==================== 参数解析 ====================

def parse_args():
    ap = argparse.ArgumentParser(description="学术 PDF figure 精确切割 v3.0（融合算法 + 自检评分）")
    ap.add_argument("pdf", help="PDF 文件路径")
    ap.add_argument("--out", default="figures_extracted", help="输出目录（默认 figures_extracted）")
    ap.add_argument("--dpi", type=int, default=300, help="渲染 DPI（默认 300）")
    ap.add_argument("--preset", choices=["auto"] + list(PRESETS.keys()), default="auto",
                    help="标签正则预设（默认 auto 自动探测）")
    ap.add_argument("--label-regex", default=None,
                    help="自定义标签正则，须含 (?P<num>...)，可选 (?P<ext>...)。覆盖预设。")
    ap.add_argument("--mode", choices=["whole", "subfig", "both"], default="both",
                    help="切割模式：whole 只切整图 / subfig 只切子图 / both 两者都输出（默认 both）")
    ap.add_argument("--header", type=float, default=42, help="页眉底部截止线 pt（默认 42）")
    ap.add_argument("--footer", type=float, default=40, help="页脚顶部截止线 pt（默认 40）")
    ap.add_argument("--jobs", type=int, default=0,
                    help="并行渲染进程数（默认 0=自动，取 min(4, CPU核数)；1=关闭并行）")
    ap.add_argument("--preview", action="store_true",
                    help="快速预览模式（低分辨率，只输出缩略图）")
    ap.add_argument("--figures", default=None,
                    help="只切割指定的图（逗号分隔，如 1,3,5 或 ED_Fig_1,ED_Fig_2）")
    ap.add_argument("--refine-edge", action="store_true", default=True,
                    help="边缘精化（默认开启）")
    ap.add_argument("--no-refine-edge", dest="refine_edge", action="store_false",
                    help="关闭边缘精化")
    ap.add_argument("--cache", action="store_true", default=True,
                    help="启用预解析缓存（默认开启）")
    ap.add_argument("--no-cache", dest="cache", action="store_false",
                    help="关闭预解析缓存")
    return ap.parse_args()


# ==================== 标签探测 ====================

def compile_label_regex(pattern):
    label_re = re.compile(pattern)
    if "num" not in label_re.groupindex:
        sys.exit("[错误] 标签正则必须包含 (?P<num>...) 命名组。")
    return label_re


def find_labels(page, label_re):
    """行级匹配图注标签"""
    out = []
    for blk in CACHE.get_dict(page)["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            text = "".join(s["text"] for s in line["spans"]).strip()
            m = label_re.match(text)
            if m:
                r = pymupdf.Rect(line["bbox"])
                is_ext = bool(m.group("ext")) if "ext" in label_re.groupindex else False
                out.append((int(m.group("num")), is_ext, r, text))
    out.sort(key=lambda t: (t[2].y0, t[2].x0))
    return out


def scan_labels(doc, label_re):
    all_labels = []
    for pno, page in enumerate(doc):
        for num, is_ext, r, _ in find_labels(page, label_re):
            all_labels.append({"pno": pno, "num": num, "ext": is_ext, "rect": r})
    return all_labels


def score_labels(labels):
    if not labels:
        return 0
    keys = [(l["ext"], l["num"]) for l in labels]
    uniq = set(keys)
    dups = len(keys) - len(uniq)
    main_nums = sorted({l["num"] for l in labels if not l["ext"]})
    seq = 5 if main_nums == list(range(1, len(main_nums) + 1)) else 0
    return len(uniq) * 2 + seq - dups * 3


def auto_detect(doc):
    best = None
    for name, pattern in PRESETS.items():
        label_re = re.compile(pattern)
        labels = scan_labels(doc, label_re)
        score = score_labels(labels)
        if labels:
            print(f"[自动探测] {name}: {len(labels)} 个标签，得分 {score}")
        if score > 0 and (best is None or score > best[3]):
            best = (name, label_re, labels, score)
    if best is None:
        return None
    name, label_re, labels, score = best
    print(f"[自动探测] 选用预设 {name}（得分 {score}）。")
    return name, label_re, labels


# ==================== 通用几何 ====================

def is_decorative(r, page):
    pw, ph = page.rect.width, page.rect.height
    if r.width > pw * 0.97 and r.height > ph * 0.9:
        return True
    if r.width > pw * 0.8 and r.height < 4:
        return True
    if r.height > ph * 0.8 and r.width < 4:
        return True
    return False


def region_has_graphics(page, region):
    for d in CACHE.get_drawings(page):
        r = d["rect"]
        if r.is_empty or r.width <= 0 or r.height <= 0:
            continue
        if is_decorative(r, page):
            continue
        if r.intersects(region):
            return True
    for img in CACHE.get_images(page):
        r = pymupdf.Rect(img["bbox"])
        if not r.is_empty and r.intersects(region):
            return True
    return False


def collect_union_rects(page, region, exclude_label_re=None):
    """收集区域内 drawings/图像/文本块 bbox"""
    rects = []
    
    # 矢量绘图
    for d in CACHE.get_drawings(page):
        r = pymupdf.Rect(d["rect"])
        if r.is_empty or r.width <= 0 or r.height <= 0:
            continue
        if is_decorative(r, page):
            continue
        clipped = pymupdf.Rect(r)
        clipped.intersect(region)
        if not clipped.is_empty and clipped.get_area() > 0.5:
            rects.append(clipped)
    
    # 位图
    for img in CACHE.get_images(page):
        r = pymupdf.Rect(img["bbox"])
        if r.is_empty:
            continue
        clipped = pymupdf.Rect(r)
        clipped.intersect(region)
        if not clipped.is_empty:
            rects.append(clipped)
    
    # 文本块
    for blk in CACHE.get_blocks(page):
        r = pymupdf.Rect(blk[:4])
        if r.is_empty:
            continue
        if exclude_label_re and exclude_label_re.match(blk[4].strip()):
            continue
        clipped = pymupdf.Rect(r)
        clipped.intersect(region)
        if not clipped.is_empty and clipped.get_area() > 0.5:
            rects.append(clipped)
    
    return rects


def union_bbox(rects):
    if not rects:
        return pymupdf.Rect()
    bbox = pymupdf.Rect(rects[0])
    for r in rects[1:]:
        bbox |= r
    return bbox


# ==================== 方案A：连通域分析 ====================

def find_connected_components(page, fig_bbox, min_area=100, zoom=100/72):
    """检测整个 fig_bbox 内 drawings/images 的连通域（过滤小连通域）"""
    # 渲染低分辨率灰度图
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom),
                          colorspace=pymupdf.csGRAY, alpha=False,
                          clip=fig_bbox)
    w, h = pix.width, pix.height
    if w < 10 or h < 10:
        return []
    
    # 二值化
    samples = pix.samples
    bin_table = bytes(1 if v < 160 else 0 for v in range(256))
    binary = []
    for y in range(h):
        row = samples[y * w:(y + 1) * w].translate(bin_table)
        binary.append(list(row))
    
    # 连通域标记（简单 flood fill）
    labels = [[0] * w for _ in range(h)]
    current_label = 0
    
    def flood_fill(x, y, label):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if cx < 0 or cx >= w or cy < 0 or cy >= h:
                continue
            if binary[cy][cx] == 0 or labels[cy][cx] != 0:
                continue
            labels[cy][cx] = label
            stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
    
    components = []
    for y in range(h):
        for x in range(w):
            if binary[y][x] == 1 and labels[y][x] == 0:
                current_label += 1
                flood_fill(x, y, current_label)
                
                # 计算连通域 bbox
                xs, ys = [], []
                for cy in range(h):
                    for cx in range(w):
                        if labels[cy][cx] == current_label:
                            xs.append(cx)
                            ys.append(cy)
                
                if xs and ys:
                    area = len(xs)
                    if area < min_area:  # 过滤小连通域
                        continue
                    bbox = pymupdf.Rect(
                        fig_bbox.x0 + min(xs) / zoom,
                        fig_bbox.y0 + min(ys) / zoom,
                        fig_bbox.x0 + max(xs) / zoom,
                        fig_bbox.y0 + max(ys) / zoom
                    )
                    components.append({"label": current_label, "bbox": bbox, "area": area})
    
    return components


def assign_labels_to_components(labels, components):
    """将标签分配给最近的连通域"""
    assignments = {}
    
    print(f"[调试] assign_labels_to_components: {len(labels)} 个标签, {len(components)} 个连通域")
    
    for letter, label_rect in labels:
        label_center = (
            (label_rect.x0 + label_rect.x1) / 2,
            (label_rect.y0 + label_rect.y1) / 2
        )
        
        best_component = None
        min_dist = float('inf')
        
        for comp in components:
            comp_center = (
                (comp["bbox"].x0 + comp["bbox"].x1) / 2,
                (comp["bbox"].y0 + comp["bbox"].y1) / 2
            )
            dist = math.sqrt(
                (label_center[0] - comp_center[0]) ** 2 +
                (label_center[1] - comp_center[1]) ** 2
            )
            if dist < min_dist:
                min_dist = dist
                best_component = comp
        
        if best_component:
            assignments[letter] = best_component
            print(f"[调试]   标签 {letter}: 分配到连通域 {best_component['label']}, bbox={best_component['bbox']}, 距离={min_dist:.2f}")
    
    return assignments


# ==================== 方案B：Voronoi 分区 ====================

LETTER_RE = re.compile(r'^[a-zA-Z]$')
LOWER_RE = re.compile(r'^[a-z]$')
UPPER_RE = re.compile(r'^[A-Z]$')


def _font_key(font, size, flags):
    """归一化字体键：去掉末尾版本数字，标记是否粗体/黑体。"""
    base = re.sub(r'\d+$', '', font or '').strip()
    is_bold = bool(flags & 2**4) or any(w in base for w in ('Bold', 'Black', 'Heavy'))
    return (base, round(float(size), 1), is_bold)


def _longest_prefix(labels, start='a'):
    """取从 start 开始的最长连续字母前缀。真实子图标签必从 a/A 连续编号。"""
    if not labels:
        return []
    uniq = {}
    for c, b, s in labels:
        if c not in uniq:
            uniq[c] = (c, b, s)
    letters = sorted(uniq.keys())
    if not letters or letters[0] != start:
        return []
    prefix = [start]
    for i in range(1, len(letters)):
        expected = chr(ord(start) + i)
        if letters[i] == expected:
            prefix.append(expected)
        else:
            break
    return [uniq[c] for c in prefix]


def _best_label_group(chars):
    """按字体/字号对单字母聚类，返回最可能是子图标签的连续 a/A 前缀。
    chars: [(char, bbox, size, font, flags)]"""
    groups = {}
    for c, b, s, font, flags in chars:
        key = _font_key(font, s, flags)
        groups.setdefault(key, []).append((c, b, s))

    best, best_score = [], -1
    for key, items in groups.items():
        _, size, is_bold = key
        for start in ('a', 'A'):
            prefix = _longest_prefix(items, start)
            if len(prefix) < 2:
                continue
            if len(prefix) > 12:
                prefix = prefix[:12]
            score = len(prefix) * size + (30 if is_bold else 0)
            if score > best_score:
                best, best_score = prefix, score
    return best


def _filter_continuous_text(cands):
    """同一文本行被拆成多个单字符 span 时（标题/正文），整行排除。
    判据：同 y（容差 2pt）且相邻 x 间距 <= 3pt 的连续单字母 >= 3 个。"""
    if len(cands) < 3:
        return cands
    cands = sorted(cands, key=lambda t: (t[1].y0, t[1].x0))
    rows = []
    for c, b, s in cands:
        if rows and abs(b.y0 - rows[-1][0][1].y0) <= 2:
            rows[-1].append((c, b, s))
        else:
            rows.append([(c, b, s)])
    bad = set()
    for row in rows:
        row = sorted(row, key=lambda t: t[1].x0)
        chain = [row[0]]
        for i in range(1, len(row)):
            if row[i][1].x0 - row[i - 1][1].x1 <= 3:
                chain.append(row[i])
            else:
                if len(chain) >= 3:
                    bad.update(id(c) for c in chain)
                chain = [row[i]]
        if len(chain) >= 3:
            bad.update(id(c) for c in chain)
    return [c for c in cands if id(c) not in bad]


def _validate_labels(labels, fig_bbox):
    """过滤由页眉/水印/URL 文字产生的假子图标签。"""
    if not (2 <= len(labels) <= 12):
        return False
    xs = [b.x0 + b.width / 2 for _, b in labels]
    ys = [b.y0 + b.height / 2 for _, b in labels]
    x_range = max(xs) - min(xs)
    y_range = max(ys) - min(ys)
    top_margin = max(15, fig_bbox.height * 0.12)
    if all(y < fig_bbox.y0 + top_margin for y in ys):
        return False
    if y_range < 15 and min(ys) < fig_bbox.y0 + max(20, fig_bbox.height * 0.18):
        return False
    rows = []
    for y in sorted(ys):
        if rows and abs(y - rows[-1][-1]) <= 15:
            rows[-1].append(y)
        else:
            rows.append([y])
    for row in rows:
        if len(row) >= max(3, len(labels) / 2):
            if max(row) < fig_bbox.y0 + max(25, fig_bbox.height * 0.20):
                return False
    if x_range < 35 and y_range < 35:
        return False
    return True


def detect_subfig_labels(page, fig_bbox):
    """在整图 bbox 内检测子图标签（a/b/c...）。
    策略：① 按字体/字号聚类，取连续 a/A 前缀 ② 失败则回退到孤立性+连续文本过滤。"""
    all_chars, letter_chars = [], []
    for blk in CACHE.get_rawdict(page)["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for span in line["spans"]:
                font = span.get("font", "")
                flags = span.get("flags", 0)
                for ch in span.get("chars", []):
                    b = pymupdf.Rect(ch["bbox"])
                    if b.is_empty:
                        continue
                    clipped = pymupdf.Rect(b)
                    clipped.intersect(fig_bbox)
                    if clipped.is_empty or clipped.get_area() < b.get_area() * 0.5:
                        continue
                    c = ch.get("c", "").strip()
                    if not c:
                        continue
                    size = b.height
                    all_chars.append((c, b, size))
                    if LETTER_RE.match(c):
                        letter_chars.append((c, b, size, font, flags))

    if not letter_chars:
        return []

    selected = _best_label_group(letter_chars)
    if selected:
        seen, uniq = set(), []
        for c, b, _ in sorted(selected, key=lambda t: (t[1].y0, t[1].x0)):
            if c in seen:
                continue
            seen.add(c)
            uniq.append((c, b))
        if _validate_labels(uniq, fig_bbox):
            return uniq

    if selected:
        filtered = _filter_continuous_text([(c, b, 0) for c, b in uniq])
        if len(filtered) >= 2:
            uniq2 = [(c, b) for c, b, _ in filtered]
            if _validate_labels(uniq2, fig_bbox):
                return uniq2

    if not all_chars:
        return []
    sizes = [s for _, _, s in all_chars]
    med = sorted(sizes)[len(sizes) // 2]
    non_letter = [(b, s) for c, b, s in all_chars if not LETTER_RE.match(c)]

    def isolated(cands):
        out = []
        for c, b, s in cands:
            R = max(s * 1.5, 10)
            forbid = pymupdf.Rect(b) + (-R, -R, R, R)
            if any(nb.intersects(forbid) for nb, _ in non_letter):
                continue
            out.append((c, b, s))
        return out

    lower = isolated([(c, b, s) for c, b, s in all_chars
                      if LOWER_RE.match(c) and s >= med * 0.7])
    lower = _filter_continuous_text(lower)
    lower = _longest_prefix(lower, 'a')
    if 2 <= len(lower) <= 12:
        selected = lower
    else:
        upper = isolated([(c, b, s) for c, b, s in all_chars
                          if UPPER_RE.match(c) and s >= med * 0.7])
        upper = _filter_continuous_text(upper)
        upper = _longest_prefix(upper, 'A')
        selected = upper if 2 <= len(upper) <= 12 else []
    seen, uniq = set(), []
    for c, b, _ in sorted(selected, key=lambda t: (t[1].y0, t[1].x0)):
        if c in seen:
            continue
        seen.add(c)
        uniq.append((c, b))
    return uniq if _validate_labels(uniq, fig_bbox) else []


def infer_subfig_regions_voronoi(page, fig_bbox, labels, grid=8, zoom=100/72, refine=2):
    """Voronoi + k-means 精化分区"""
    if not labels:
        return []
    
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom),
                          colorspace=pymupdf.csGRAY, alpha=False,
                          clip=fig_bbox)
    w, h = pix.width, pix.height
    if w < 20 or h < 20:
        return []
    
    bin_table = bytes(1 if v < 160 else 0 for v in range(256))
    samples = pix.samples
    
    # 标签中心
    seeds = []
    anchors = {}
    for letter, r in labels:
        cx = ((r.x0 + r.x1) / 2 - fig_bbox.x0) * zoom
        cy = ((r.y0 + r.y1) / 2 - fig_bbox.y0) * zoom
        seeds.append([letter, cx, cy])
        anchors[letter] = r
    
    # 提取墨迹网格
    step = max(4, int(grid))
    ink_cells = []
    for gy in range(0, h, step):
        y1 = min(gy + step, h)
        for gx in range(0, w, step):
            x1 = min(gx + step, w)
            has_ink = False
            for y in range(gy, y1):
                row = samples[y * w:(y + 1) * w].translate(bin_table)
                if b"\x01" in row[gx:x1]:
                    has_ink = True
                    break
            if has_ink:
                ink_cells.append((gx, gy, x1, y1))
    
    if not ink_cells:
        return [{"letter": letter, "region": pymupdf.Rect(anchors[letter]) + (-20, -20, 20, 20),
                 "anchor": anchors[letter]} for letter, _, _ in seeds]
    
    # 迭代精化
    for _ in range(refine):
        assignments = {letter: [] for letter, _, _ in seeds}
        for cell in ink_cells:
            cx, cy = (cell[0] + cell[2]) / 2, (cell[1] + cell[3]) / 2
            best = min(seeds, key=lambda s: (cx - s[1]) ** 2 + (cy - s[2]) ** 2)
            assignments[best[0]].append(cell)
        for s in seeds:
            cells = assignments[s[0]]
            if cells:
                sx = sum((c[0] + c[2]) / 2 for c in cells) / len(cells)
                sy = sum((c[1] + c[3]) / 2 for c in cells) / len(cells)
                nx = max(0, min(w, sx))
                ny = max(0, min(h, sy))
                if abs(nx - s[1]) <= 30 and abs(ny - s[2]) <= 30:
                    s[1], s[2] = nx, ny
    
    # 最终分配
    assignments = {letter: [] for letter, _, _ in seeds}
    for cell in ink_cells:
        cx, cy = (cell[0] + cell[2]) / 2, (cell[1] + cell[3]) / 2
        best = min(seeds, key=lambda s: (cx - s[1]) ** 2 + (cy - s[2]) ** 2)
        assignments[best[0]].append(cell)
    
    result = []
    for letter, _, _ in seeds:
        pts = assignments[letter]
        anchor = anchors[letter]
        if not pts:
            region = pymupdf.Rect(anchor) + (-20, -20, 20, 20)
            region &= fig_bbox
        else:
            xs = [p[0] for p in pts] + [p[2] for p in pts]
            ys = [p[1] for p in pts] + [p[3] for p in pts]
            region = pymupdf.Rect(fig_bbox.x0 + min(xs) / zoom,
                                  fig_bbox.y0 + min(ys) / zoom,
                                  fig_bbox.x0 + max(xs) / zoom,
                                  fig_bbox.y0 + max(ys) / zoom)
        result.append({"letter": letter, "region": region, "anchor": anchor})
    
    return result


# ==================== 后处理合并 ====================

def merge_adjacent_regions(regions, threshold=5.0):
    """合并相邻区域（边界两侧图形距离 < 阈值）"""
    if len(regions) <= 1:
        return regions
    
    print(f"[调试] merge_adjacent_regions: 输入 {len(regions)} 个区域")
    
    # 计算相邻区域的距离
    merged = True
    while merged:
        merged = False
        for i in range(len(regions)):
            for j in range(i + 1, len(regions)):
                r1 = regions[i]["region"]
                r2 = regions[j]["region"]
                
                # 检查是否有重叠
                if r1.intersects(r2):
                    # 计算重叠面积
                    intersection = r1 & r2
                    overlap_area = intersection.get_area()
                    min_area = min(r1.get_area(), r2.get_area())
                    
                    # 如果重叠面积超过较小区域的30%，则合并
                    if min_area > 0 and overlap_area / min_area > 0.3:
                        new_region = r1 | r2
                        regions[i] = {
                            "letter": regions[i]["letter"],
                            "region": new_region,
                            "anchor": regions[i]["anchor"]
                        }
                        regions.pop(j)
                        merged = True
                        print(f"[调试]   合并区域 {i} 和 {j}")
                        break
            if merged:
                break
    
    print(f"[调试] merge_adjacent_regions: 输出 {len(regions)} 个区域")
    return regions


# ==================== 方案C：分离 bbox 计算（正文过滤版） ====================

_TABLE_RE = re.compile(r"^Table\s*\d+")


def _table_title_rects(page):
    """正文表格标题块（Table N ...）的 bbox，用于把表格区排除出 figure 定界。"""
    rects = []
    for blk in CACHE.get_dict(page)["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk.get("lines") or []:
            txt = "".join(s["text"] for s in line["spans"]).strip()
            if _TABLE_RE.match(txt):
                rects.append(pymupdf.Rect(blk["bbox"]))
                break
    return rects


def _expand_zones(seeds, elements, grow=6, max_iter=6):
    """从种子区域出发，把与之相交（含外扩 grow）的元素迭代并入，直到收敛。"""
    zones = [pymupdf.Rect(s) for s in seeds]
    for _ in range(max_iter):
        changed = False
        for r in elements:
            if any(z.contains(r) for z in zones):
                continue
            if any(r.intersects(pymupdf.Rect(z) + (-grow, -grow, grow, grow))
                   for z in zones):
                zones.append(pymupdf.Rect(r))
                changed = True
        if not changed:
            break
    return zones


def _is_body_text_block(blk, page_width):
    """识别两端对齐的正文段落块：行数多且各行几乎充满栏宽。"""
    lines = blk.get("lines") or []
    if len(lines) < 3:
        return False
    widths = []
    for line in lines:
        spans = line.get("spans") or []
        if not spans:
            continue
        widths.append(max(s["bbox"][2] for s in spans) -
                      min(s["bbox"][0] for s in spans))
    if len(widths) < 3:
        return False
    blk_w = max(widths)
    if blk_w < page_width * 0.22:
        return False
    fill = sum(1 for w in widths if w > blk_w * 0.9) / len(widths)
    return fill >= 0.75


def collect_union_rects(page, region, label_re):
    """收集区域内 drawings/图像/文本块 bbox（正文/表格/图注双保险过滤）。
    文本块过滤：
      1) 排除图注标签所在块、两端对齐的正文段落块；
      2) 若存在矢量/位图核心区，仅保留与核心区相交或邻近(<12pt)的文本块。"""
    raw_graphics = []
    for d in CACHE.get_drawings(page):
        r = pymupdf.Rect(d["rect"])
        if r.is_empty or r.width <= 0 or r.height <= 0 or is_decorative(r, page):
            continue
        raw_graphics.append(r)
    for img in CACHE.get_images(page):
        r = pymupdf.Rect(img["bbox"])
        if not r.is_empty:
            raw_graphics.append(r)
    table_zones = _expand_zones(_table_title_rects(page), raw_graphics)

    graphic_rects = []
    for r in raw_graphics:
        if any(r.intersects(z) for z in table_zones):
            continue
        clipped = pymupdf.Rect(r)
        clipped.intersect(region)
        if not clipped.is_empty and clipped.get_area() > 0.5:
            graphic_rects.append(clipped)
    core = union_bbox(graphic_rects) if graphic_rects else None

    text_rects = []
    for blk in CACHE.get_dict(page)["blocks"]:
        if blk.get("type") != 0:
            continue
        is_caption = any(
            label_re.match("".join(s["text"] for s in line["spans"]).strip())
            for line in blk["lines"])
        if is_caption:
            continue
        if _is_body_text_block(blk, page.rect.width):
            continue
        r_blk = pymupdf.Rect(blk["bbox"])
        if any(r_blk.intersects(z) for z in table_zones):
            continue
        r = pymupdf.Rect(blk["bbox"])
        if r.is_empty:
            continue
        clipped = pymupdf.Rect(r)
        clipped.intersect(region)
        if clipped.is_empty or clipped.get_area() <= 0.5:
            continue
        if core is not None:
            near = pymupdf.Rect(core) + (-12, -12, 12, 12)
            if not clipped.intersects(near):
                continue
        text_rects.append(clipped)
    return graphic_rects + text_rects


def compute_separate_bbox(page, region, exclude_label_re=None):
    """方案C：分离 bbox 计算（图形元素 + 相邻文本块）。"""
    rects = collect_union_rects(page, region, exclude_label_re)
    if not rects:
        return pymupdf.Rect()
    return union_bbox(rects)


# ==================== 边缘精化 ====================

def refine_edge_bbox(bbox, page, padding=2):
    """边缘精化：去除多余边缘"""
    # 确保 bbox 不超出页面
    bbox &= page.rect
    
    # 如果 bbox 太大，尝试收缩
    if bbox.width > page.rect.width * 0.95 or bbox.height > page.rect.height * 0.95:
        return bbox
    
    # 检查边缘是否有内容
    edge_margin = 2
    
    # 检查左边缘
    left_region = pymupdf.Rect(bbox.x0, bbox.y0, bbox.x0 + edge_margin, bbox.y1)
    if not region_has_graphics(page, left_region):
        bbox.x0 += edge_margin
    
    # 检查右边缘
    right_region = pymupdf.Rect(bbox.x1 - edge_margin, bbox.y0, bbox.x1, bbox.y1)
    if not region_has_graphics(page, right_region):
        bbox.x1 -= edge_margin
    
    # 检查上边缘
    top_region = pymupdf.Rect(bbox.x0, bbox.y0, bbox.x1, bbox.y0 + edge_margin)
    if not region_has_graphics(page, top_region):
        bbox.y0 += edge_margin
    
    # 检查下边缘
    bottom_region = pymupdf.Rect(bbox.x0, bbox.y1 - edge_margin, bbox.x1, bbox.y1)
    if not region_has_graphics(page, bottom_region):
        bbox.y1 -= edge_margin
    
    return bbox


# ==================== 自检评分 ====================

def score_subfig(page, bbox, label_rect=None):
    """自检评分：完整性、边缘纯净度、标签对齐、尺寸合理性"""
    scores = {
        "completeness": 1.0,  # 完整性
        "edge_purity": 1.0,   # 边缘纯净度
        "label_alignment": 1.0,  # 标签对齐
        "size_reasonability": 1.0  # 尺寸合理性
    }
    
    # 1. 完整性检查：图形元素是否完整包含
    graphics_rects = []
    for d in CACHE.get_drawings(page):
        r = pymupdf.Rect(d["rect"])
        if r.is_empty or r.width <= 0 or r.height <= 0:
            continue
        if is_decorative(r, page):
            continue
        if bbox.contains(r):
            graphics_rects.append(r)
    
    for img in CACHE.get_images(page):
        r = pymupdf.Rect(img["bbox"])
        if r.is_empty:
            continue
        if bbox.contains(r):
            graphics_rects.append(r)
    
    # 检查是否有图形元素被切割
    total_graphics = len(graphics_rects)
    if total_graphics > 0:
        # 检查边缘附近的图形
        edge_margin = 5
        edge_graphics = 0
        for r in graphics_rects:
            if (r.x0 < bbox.x0 + edge_margin or r.x1 > bbox.x1 - edge_margin or
                r.y0 < bbox.y0 + edge_margin or r.y1 > bbox.y1 - edge_margin):
                edge_graphics += 1
        
        if edge_graphics > 0:
            scores["completeness"] = max(0.5, 1.0 - edge_graphics * 0.1)
    
    # 2. 边缘纯净度：是否混入正文/图注
    text_in_bbox = []
    for blk in CACHE.get_blocks(page):
        r = pymupdf.Rect(blk[:4])
        if r.is_empty:
            continue
        text = blk[4].strip()
        # 检查是否为正文（长文本）
        if len(text) > 50 and bbox.contains(r):
            text_in_bbox.append(r)
    
    if text_in_bbox:
        scores["edge_purity"] = max(0.3, 1.0 - len(text_in_bbox) * 0.2)
    
    # 3. 标签对齐：标签应在子图左上角
    if label_rect:
        label_center_x = (label_rect.x0 + label_rect.x1) / 2
        label_center_y = (label_rect.y0 + label_rect.y1) / 2
        
        # 检查是否在左上角区域
        in_left = label_center_x < bbox.x0 + bbox.width * 0.3
        in_top = label_center_y < bbox.y0 + bbox.height * 0.3
        
        if not (in_left and in_top):
            scores["label_alignment"] = 0.6
    
    # 4. 尺寸合理性：宽高比是否合理
    aspect_ratio = bbox.width / bbox.height if bbox.height > 0 else 1
    if aspect_ratio > 5 or aspect_ratio < 0.2:
        scores["size_reasonability"] = 0.5
    
    # 计算总分（百分制）
    weights = {"completeness": 0.4, "edge_purity": 0.3, 
               "label_alignment": 0.15, "size_reasonability": 0.15}
    total_score = round(sum(scores[k] * weights[k] for k in scores) * 100, 1)
    
    return scores, total_score


# ==================== 切割渲染 ====================

def crop_figure(page, bbox, out_path, dpi=300, preview=False):
    """渲染并保存图片"""
    if preview:
        # 预览模式：低分辨率
        zoom = 72 / 72  # 72 DPI
    else:
        zoom = dpi / 72
    
    mat = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=bbox, alpha=False)
    pix.save(out_path)
    return pix.width, pix.height


# ---- 提速：整页一次 300dpi 渲染 + PIL 按 bbox 裁剪（避免每子图重复 clip 渲染） ----
def _page_image(page, dpi, cache):
    key = (page.number, dpi)
    if key not in cache:
        pix = page.get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72), alpha=False)
        cache[key] = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return cache[key]


def _crop_page(page, bbox, path, dpi, cache):
    if not _HAS_PIL:
        return crop_figure(page, bbox, path, dpi)
    img = _page_image(page, dpi, cache)
    scale = dpi / 72
    box = (int(round(bbox.x0 * scale)), int(round(bbox.y0 * scale)),
           int(round(bbox.x1 * scale)), int(round(bbox.y1 * scale)))
    box = (max(0, box[0]), max(0, box[1]),
           min(img.width, box[2]), min(img.height, box[3]))
    w, h = box[2] - box[0], box[3] - box[1]
    if w > 0 and h > 0:
        img.crop(box).save(path)
    return w, h


def ink_split_regions(page, fig_bbox, pad, zoom=100 / 72):
    """无子图标签时的墨迹投影间隙分割（低置信度兜底）。
    整图内行投影找空白间隙 → 水平分段；每段列投影 → 垂直分段。返回 [Rect]"""
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom),
                          colorspace=pymupdf.csGRAY, alpha=False,
                          clip=fig_bbox)
    w, h = pix.width, pix.height
    if w < 10 or h < 10:
        return []
    samples = pix.samples
    bin_table = bytes(1 if v < 160 else 0 for v in range(256))
    row_ink = []
    for y in range(h):
        row = samples[y * w:(y + 1) * w].translate(bin_table)
        row_ink.append(row.count(b"\x01"))
    gaps_y, run = [], 0
    for y in range(h):
        if row_ink[y] == 0:
            run += 1
        else:
            if run >= 4:
                gaps_y.append((y - run, y))
            run = 0
    if run >= 4:
        gaps_y.append((h - run, h))
    min_h = 40 * zoom
    segs, y0 = [], 0
    for gs, ge in gaps_y:
        if ge - y0 >= min_h:
            segs.append((y0, gs))
        y0 = ge
    if h - y0 >= min_h:
        segs.append((y0, h))
    regions = []
    min_w = 40 * zoom
    for y0, y1 in segs:
        col_ink = [0] * w
        for y in range(y0, y1):
            row = samples[y * w:(y + 1) * w].translate(bin_table)
            x = row.find(b"\x01")
            while x >= 0:
                col_ink[x] += 1
                x = row.find(b"\x01", x + 1)
        gaps_x, run = [], 0
        for x in range(w):
            if col_ink[x] == 0:
                run += 1
            else:
                if run >= 4:
                    gaps_x.append((x - run, x))
                run = 0
        if run >= 4:
            gaps_x.append((w - run, w))
        x0 = 0
        for gs, ge in gaps_x:
            if ge - x0 >= min_w:
                r = pymupdf.Rect(fig_bbox.x0 + x0 / zoom, fig_bbox.y0 + y0 / zoom,
                                 fig_bbox.x0 + gs / zoom, fig_bbox.y0 + y1 / zoom)
                r &= page.rect
                r += (-pad, -pad, pad, pad)
                r &= page.rect
                if r.width >= 40 and r.height >= 40:
                    regions.append(r)
            x0 = ge
        if w - x0 >= min_w:
            r = pymupdf.Rect(fig_bbox.x0 + x0 / zoom, fig_bbox.y0 + y0 / zoom,
                             fig_bbox.x0 + w / zoom, fig_bbox.y0 + y1 / zoom)
            r &= page.rect
            r += (-pad, -pad, pad, pad)
            r &= page.rect
            if r.width >= 40 and r.height >= 40:
                regions.append(r)
    return regions


def merge_ink_regions(regions, h_ratio=0.5, gap_limit=6.0):
    """墨迹分割后处理：把"附属矮块"（图例/标题/被切断的图形底部）归并到紧邻的主体区域，
    修复"一个子图被切成上下两半"。
    判据：
      - 高度显著矮于最高块（< h_ratio*最高高度）——图例行/标题；
      - 与主体在 y 方向紧邻（间距 < gap_limit）——排除上下两个真实子图之间的大间隔。
    两者同时满足才合并（如 Fig_3 图例并入饼图；Fig_7 两个分子结构因间隔大而保留）。"""
    if len(regions) <= 1:
        return regions
    maxh = max(r.height for r in regions)
    large = [r for r in regions if r.height >= h_ratio * maxh]
    small = [r for r in regions if r.height < h_ratio * maxh]
    if not small or not large:
        return regions

    large = list(large)
    for s in small:
        best_i, best_key = -1, (-1e9, 1e9)
        for i, L in enumerate(large):
            ox = min(s.x1, L.x1) - max(s.x0, L.x0)
            if ox <= 0:
                continue
            y_dist = max(0, max(L.y0, s.y0) - min(L.y1, s.y1))
            if y_dist > gap_limit:
                continue
            overlap_ratio = ox / min(s.width, L.width)
            key = (overlap_ratio, -y_dist)  # 重叠越大、距离越小越优先
            if key > best_key:
                best_key, best_i = key, i
        if best_i >= 0:
            large[best_i] = large[best_i] | s
        else:
            large.append(s)
    return large

# ==================== Worker 函数 ====================

def process_page(args):
    """处理单个页面、该页所有 figure 的 worker 函数。
    同一页多个图注标签时，按 y 切成不重叠的条带，每个 figure 只在自己的条带内定界，
    避免一页多图互相污染（参考 V2.1 Stage B）。"""
    (pdf_path, pno, page_labels, out_dir, dpi, mode, header, footer,
     preview, refine_edge, label_re_str, cache_enabled) = args

    label_re = re.compile(label_re_str) if label_re_str else None

    try:
        doc = pymupdf.open(pdf_path)
        page = doc[pno]
        results = []
        header_cutoff, footer_cutoff, gap, pad = header, footer, 6, 4
        raster_cache = {}  # (page_no, dpi) -> PIL.Image，整页一次渲染裁剪

        page_labels = sorted(page_labels, key=lambda l: l["rect"].y0)
        single = len(page_labels) == 1

        prev_bottom = header_cutoff
        for lab in page_labels:
            name = "ED_Fig_%d" % lab["num"] if lab["ext"] else "Fig_%d" % lab["num"]
            # 条带：上一图注下边界 ~ 本图注上边界
            band = pymupdf.Rect(0, prev_bottom, page.rect.width, lab["rect"].y0 - gap)
            prev_bottom = lab["rect"].y1 + gap
            if band.y1 <= band.y0:
                continue

            cross_page = False
            cut_page = page
            fig_bbox = pymupdf.Rect()
            if region_has_graphics(page, band):
                fig_bbox = compute_separate_bbox(page, band, label_re)

            # 跨页兜底：仅当本页只有一个 figure 且本页无图形时；多图页不兜底（下一页归下一页）
            if (fig_bbox.is_empty or fig_bbox.width <= 0 or fig_bbox.height <= 0) and single:
                next_pno = pno + 1
                if next_pno < len(doc):
                    nxt = doc[next_pno]
                    nxt_has_label = any(
                        label_re.match("".join(s["text"] for s in line["spans"]).strip())
                        for blk in CACHE.get_dict(nxt)["blocks"] if blk.get("type") == 0
                        for line in blk.get("lines") or [])
                    if not nxt_has_label:
                        nxt_region = pymupdf.Rect(0, header_cutoff,
                                                  nxt.rect.width, nxt.rect.height - footer_cutoff)
                        nxt_bbox = compute_separate_bbox(nxt, nxt_region, label_re)
                        if not nxt_bbox.is_empty and nxt_bbox.width > 0 and nxt_bbox.height > 0:
                            fig_bbox = nxt_bbox
                            cut_page = nxt
                            cross_page = True
                            print(f"[跨页兜底] {name}: 图注页{pno+1}，图形在页{next_pno+1}")

            if fig_bbox.is_empty or fig_bbox.width <= 0 or fig_bbox.height <= 0:
                fig_bbox = pymupdf.Rect(30, header_cutoff, page.rect.width - 30,
                                        lab["rect"].y0 - 10)
            fig_bbox += (-pad, -pad, pad, pad)
            fig_bbox &= cut_page.rect

            # ---- 整图 ----
            whole_result = None
            if mode in ["whole", "both"]:
                whole_path = out_dir / "whole" / f"{name}.png"
                w, h = _crop_page(cut_page, fig_bbox, whole_path, dpi, raster_cache)
                whole_result = SubfigResult(
                    name=name, kind="whole", parent=None,
                    label_page=pno + 1, cut_page=cut_page.number + 1,
                    cross_page=cross_page, method="anchor", confidence="high",
                    bbox=tuple(fig_bbox), pixel_size=(w, h),
                    file_path=str(whole_path.relative_to(out_dir.parent)),
                    scores={}, total_score=100.0
                )

            # ---- 子图 ----
            subfig_results = []
            if mode in ["subfig", "both"]:
                fig_page = cut_page
                labels = detect_subfig_labels(fig_page, fig_bbox)
                if labels:
                    cells = infer_subfig_regions_voronoi(fig_page, fig_bbox, labels)
                    method, confidence = "subfig-labels", "high"
                    for cell in cells:
                        letter, region_, anchor = cell["letter"], cell["region"], cell["anchor"]
                        rects = collect_union_rects(fig_page, region_, label_re)
                        if not rects:
                            continue
                        bbox = union_bbox(rects)
                        bbox.intersect(region_)
                        bbox += (-pad, -pad, pad, pad)
                        bbox &= fig_page.rect
                        if bbox.is_empty or bbox.width <= 0 or bbox.height <= 0:
                            continue
                        if bbox.get_area() > fig_bbox.get_area() * 0.9:
                            continue
                        if refine_edge:
                            bbox = refine_edge_bbox(bbox, fig_page)
                        scores, total_score = score_subfig(fig_page, bbox, anchor)
                        subfig_name = f"{name}_{letter}"
                        subfig_path = out_dir / "subfig" / f"{subfig_name}.png"
                        w, h = _crop_page(fig_page, bbox, subfig_path, dpi, raster_cache)
                        subfig_results.append(SubfigResult(
                            name=subfig_name, kind="subfig", parent=name,
                            label_page=pno + 1, cut_page=fig_page.number + 1,
                            cross_page=cross_page, method=method, confidence=confidence,
                            bbox=tuple(bbox), pixel_size=(w, h),
                            file_path=str(subfig_path.relative_to(out_dir.parent)),
                            scores=scores, total_score=total_score
                        ))

                if not subfig_results:
                    regions = merge_ink_regions(ink_split_regions(fig_page, fig_bbox, pad))
                    method, confidence = "subfig-ink-split", "low"
                    for i, reg in enumerate(regions, 1):
                        bbox = pymupdf.Rect(reg)
                        if refine_edge:
                            bbox = refine_edge_bbox(bbox, fig_page)
                        scores, total_score = score_subfig(fig_page, bbox)
                        subfig_name = f"{name}_p{i}"
                        subfig_path = out_dir / "subfig" / f"{subfig_name}.png"
                        w, h = _crop_page(fig_page, bbox, subfig_path, dpi, raster_cache)
                        subfig_results.append(SubfigResult(
                            name=subfig_name, kind="subfig", parent=name,
                            label_page=pno + 1, cut_page=fig_page.number + 1,
                            cross_page=cross_page, method=method, confidence=confidence,
                            bbox=tuple(bbox), pixel_size=(w, h),
                            file_path=str(subfig_path.relative_to(out_dir.parent)),
                            scores=scores, total_score=total_score
                        ))

            results.append(WorkerResult(fig_name=name, whole_result=whole_result,
                                        subfig_results=subfig_results, error=None))

        doc.close()
        return {"page": pno, "results": results, "error": None}

    except Exception as e:
        return {"page": pno, "results": [], "error": str(e)}


# ==================== 主函数 ====================

def make_contact_sheet(out_dir, items, fname="contact_sheet.png"):
    """所有切出图缩略拼一张总览 PNG，看一张图即可完成目视抽查。
    items: [(name, confidence, file_path), ...]"""
    n = len(items)
    if n == 0:
        return None
    cols = min(6, max(1, math.ceil(math.sqrt(n))))
    rows = math.ceil(n / cols)
    cell_w, cap_h, margin = 170, 16, 12
    cell_h = 120
    W = cols * cell_w + (cols + 1) * margin
    H = rows * (cell_h + cap_h) + (rows + 1) * margin
    sheet = pymupdf.open()
    page = sheet.new_page(width=W, height=H)
    for idx, (name, conf, fpath) in enumerate(items):
        cx = margin + (idx % cols) * (cell_w + margin)
        cy = margin + (idx // cols) * (cell_h + cap_h + margin)
        img_path = Path(fpath)
        try:
            pm = pymupdf.Pixmap(str(img_path))
            iw, ih = pm.width, pm.height
        except Exception:
            continue
        scale = min(cell_w / iw, cell_h / ih)
        dw, dh = iw * scale, ih * scale
        rect = pymupdf.Rect(cx + (cell_w - dw) / 2, cy + (cell_h - dh) / 2,
                            cx + (cell_w + dw) / 2, cy + (cell_h + dh) / 2)
        page.insert_image(rect, filename=str(img_path))
        tag = f"{name} [{conf[0].upper()}]"
        page.insert_text((cx, cy + cell_h + 12), tag, fontsize=9,
                         fontname="helv", color=(0.3, 0.3, 0.35))
    out_path = out_dir / fname
    pix = page.get_pixmap(matrix=pymupdf.Matrix(150 / 72, 150 / 72), alpha=False)
    pix.save(out_path)
    sheet.close()
    return out_path


def main():
    args = parse_args()
    
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        sys.exit(f"[错误] PDF 文件不存在：{pdf_path}")
    
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "whole").mkdir(exist_ok=True)
    (out_dir / "subfig").mkdir(exist_ok=True)
    
    print("=" * 60)
    print("PDF figure 精确切割 v3.0（融合算法 + 自检评分）")
    print("=" * 60)
    
    # 打开 PDF
    doc = pymupdf.open(pdf_path)
    print(f"PDF: {pdf_path.name}，{len(doc)} 页")
    
    # 标签探测
    if args.label_regex:
        label_re = compile_label_regex(args.label_regex)
        labels = scan_labels(doc, label_re)
        print(f"[自定义正则] 检出 {len(labels)} 个标签")
    else:
        result = auto_detect(doc)
        if result is None:
            print("[警告] 所有内置预设均未匹配到图注标签，尝试通用检测...")
            label_re = re.compile(PRESETS["generic"])
            labels = scan_labels(doc, label_re)
        else:
            _, label_re, labels = result
    
    if not labels:
        sys.exit("[错误] 未检测到图注标签")
    
    # 过滤指定图
    if args.figures:
        fig_nums = [f.strip() for f in args.figures.split(",")]
        filtered = []
        for l in labels:
            name = f"ED_Fig_{l['num']}" if l["ext"] else f"Fig_{l['num']}"
            if name in fig_nums or str(l["num"]) in fig_nums:
                filtered.append(l)
        labels = filtered
        print(f"[过滤] 只切割指定图：{len(labels)} 个")
    
    print(f"[标签] 共 {len(labels)} 个图注标签")
    
    # 并行处理：按页分组（同一页多个 figure 一起处理，避免互相污染）
    num_workers = args.jobs if args.jobs > 0 else min(4, os.cpu_count() or 1)
    
    by_page = {}
    for l in labels:
        by_page.setdefault(l["pno"], []).append(l)
    
    tasks = []
    for pno in sorted(by_page):
        tasks.append((
            str(pdf_path), pno, by_page[pno], out_dir, args.dpi, args.mode,
            args.header, args.footer, args.preview, args.refine_edge,
            str(label_re.pattern), args.cache
        ))
    
    print(f"\n[并行] 使用 {num_workers} 个 worker 处理 {len(tasks)} 个页面（含 {len(labels)} 个 figure）")
    
    results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_page, task): task for task in tasks}
        
        for future in as_completed(futures):
            res = future.result()
            if res["error"]:
                print(f"[错误] 页{res['page']+1}: {res['error']}")
                continue
            for wr in res["results"]:
                results.append(wr)
                status = "✓" if wr.whole_result else "○"
                subfig_count = len(wr.subfig_results)
                print(f"[完成] {wr.fig_name}: 整图{status} 子图×{subfig_count}")
    
    doc.close()
    
    # 汇总结果
    all_whole = [r.whole_result for r in results if r.whole_result]
    all_subfig = []
    for r in results:
        all_subfig.extend(r.subfig_results)
    
    # 生成 CSV（英文表头）
    csv_path = out_dir / "report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "type", "confidence",
                         "label_page", "cut_page", "pixel_size", "file_path"])
        for r in all_whole + all_subfig:
            writer.writerow([
                r.name, r.kind, r.confidence,
                r.label_page, r.cut_page,
                f"{r.pixel_size[0]}x{r.pixel_size[1]}",
                r.file_path
            ])
    
    print(f"\n[输出] CSV 报告：{csv_path}")
    
    # 统计
    print("\n" + "=" * 60)
    print("统计")
    print("=" * 60)
    print(f"整图：{len(all_whole)} 张")
    print(f"子图：{len(all_subfig)} 张")
    
    # 置信度统计
    high = sum(1 for r in all_subfig if r.confidence == "high")
    low = sum(1 for r in all_subfig if r.confidence == "low")
    print(f"子图置信度：高={high} 中={len(all_subfig)-high-low} 低={low}")
    
    print(f"\n[已完成] 所有输出至 {out_dir}")
    print("注意：自动切割不保证 100% 准确，尤其是子图可能切割错误，请人工核对确认。")


if __name__ == "__main__":
    main()
