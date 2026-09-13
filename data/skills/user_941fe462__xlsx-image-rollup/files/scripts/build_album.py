"""
Build a rollup workbook from a summary JSON + extracted image directory.

Summary JSON format (list of records):
    [
      {
        "category": "平衡车",
        "series": "S1",
        "responsibility": "生产类",
        "issue": "瑕疵",
        "count": 90,
        "pct": 25.4,                  # optional; will be recomputed if missing
        "user_quotes": ["原话1", "原话2", ...],
        "image_files": ["image12.png", "image45.jpeg", ...]
      },
      ...
    ]

Layouts (--layout):
    thumbnail  - 180px thumbnails, multiple images per row arranged horizontally
    original   - original image data embedded, 400px display
    detail     - one image per row, text columns vertically merged, fixed cells
    grid       - one row per issue, all images packed into a single "图片" cell

Usage:
    python build_album.py --summary summary.json --images ./extracted_images \
        --out rollup.xlsx --layout grid [--display-edge 320] [--grid-n 4]
"""
import argparse
import json
import math
import os
import sys

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.units import pixels_to_EMU
from PIL import Image

# openpyxl can natively embed these; everything else is transcoded to JPEG.
NATIVE_FMT = {"PNG", "JPEG", "JPG", "GIF", "BMP"}


def get_embed_path(images_dir: str, fn: str, conv_dir: str):
    """Return the on-disk path to embed; transcode exotic formats to JPEG.

    Pillow can open MPO (multi-frame 3D photos) but openpyxl crashes because it
    uses Pillow's `Image.format` ('MPO') as the embedded file extension, and
    mimetypes has no entry for '.mpo' -> KeyError. Workaround: take the first
    frame and save as JPEG.
    """
    src = os.path.join(images_dir, fn)
    if not os.path.exists(src):
        return None
    try:
        im = Image.open(src)
        fmt = (im.format or "").upper()
        if fmt in NATIVE_FMT:
            im.close()
            return src
        os.makedirs(conv_dir, exist_ok=True)
        stem = os.path.splitext(fn)[0]
        dst = os.path.join(conv_dir, stem + ".jpg")
        if not os.path.exists(dst):
            im.seek(0)
            im.convert("RGB").save(dst, "JPEG", quality=95)
        im.close()
        return dst
    except Exception as e:
        print(f"  [WARN] cannot prepare {fn}: {e}", file=sys.stderr)
        return None


def get_size(images_dir: str, fn: str):
    p = os.path.join(images_dir, fn)
    if not os.path.exists(p):
        return None
    try:
        with Image.open(p) as im:
            return im.size
    except Exception:
        return None


def make_image(p: str, w_target: int, h_target: int, mode: str):
    """Load an image, contain-scale to (w_target, h_target), return XLImage.

    mode='fill' returns a size-only object (caller uses anchor offsets for layout).
    """
    img = XLImage(p)
    with Image.open(p) as im:
        w, h = im.size
    scale = min(w_target / w, h_target / h)
    img.width = max(1, int(w * scale))
    img.height = max(1, int(h * scale))
    return img


def anchor_centered(col: int, row: int, disp_w: int, disp_h: int,
                    cell_w_px: int, cell_h_px: int) -> OneCellAnchor:
    """Build a OneCellAnchor that centers an image inside its target cell."""
    col_off = pixels_to_EMU(max(0, (cell_w_px - disp_w) / 2))
    row_off = pixels_to_EMU(max(0, (cell_h_px - disp_h) / 2))
    marker = AnchorMarker(col=col, colOff=col_off, row=row,
                          rowOff=row_off)
    return OneCellAnchor(_from=marker,
                         ext=XDRPositiveSize2D(cx=pixels_to_EMU(disp_w),
                                               cy=pixels_to_EMU(disp_h)))


# ----- Layout builders -----

HEADERS = ["品类", "系列", "责任归属", "问题点", "频次", "占该系列%", "用户原话", "图片"]


def _styles():
    header_fill = PatternFill("solid", fgColor="D9E1F2")
    header_font = Font(bold=True, color="1F4E79", size=11)
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    vcenter = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_vcenter = Alignment(horizontal="left", vertical="center", wrap_text=True)
    thin = Side(style="thin", color="D0D0D0")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    return dict(header_fill=header_fill, header_font=header_font,
                center=center, vcenter=vcenter,
                left_vcenter=left_vcenter, border=border)


def _write_header(ws, st):
    for c, h in enumerate(HEADERS, 1):
        cell = ws.cell(row=1, column=c, value=h)
        cell.fill = st["header_fill"]
        cell.font = st["header_font"]
        cell.alignment = st["center"]
        cell.border = st["border"]


def _set_col_widths(ws, widths):
    for c, w in widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w


def _text_cell(ws, row, col, value, st, align_left=False):
    cell = ws.cell(row=row, column=col, value=value)
    cell.alignment = st["left_vcenter"] if align_left else st["vcenter"]
    cell.font = Font(size=11)
    cell.border = st["border"]


def _img_cell_border(ws, row, col, st):
    cell = ws.cell(row=row, column=col)
    cell.border = st["border"]


def _values(rec):
    quotes = rec.get("user_quotes") or []
    joined = " | ".join(q for q in quotes if q)
    return [
        rec.get("category", ""),
        rec.get("series", ""),
        rec.get("responsibility", ""),
        rec.get("issue", ""),
        rec.get("count", 0),
        f"{rec.get('pct', 0):.1f}",
        joined,
    ]


def build_thumbnail(ws, summary, st, images_dir, conv_dir, edge=180):
    """thumbnails laid out horizontally (one row per issue, multiple images)."""
    col_widths = {1: 12, 2: 12, 3: 11, 4: 22, 5: 7, 6: 11, 7: 42}
    for c in range(8, 8 + 19):
        col_widths[c] = 26
    _set_col_widths(ws, col_widths)
    ws.row_dimensions[1].height = 30
    row_h = int(edge * 0.75)
    row_idx = 2
    for r in summary:
        for c, v in enumerate(_values(r), 1):
            align_left = c in (4, 7)
            _text_cell(ws, row_idx, c, v, st, align_left=align_left)
        ws.row_dimensions[row_idx].height = row_h
        # Image header cell across all image slots
        for k, fn in enumerate(r.get("image_files") or []):
            anchor_col = 8 + k
            p = get_embed_path(images_dir, fn, conv_dir)
            if not p:
                continue
            img = make_image(p, edge, edge, "fill")
            ws.add_image(img, f"{get_column_letter(anchor_col)}{row_idx}")
        row_idx += 1
    return row_idx - 2


def build_original(ws, summary, st, images_dir, conv_dir, edge=400):
    """Same horizontal layout as thumbnail but with original image data and a
    larger display size."""
    col_widths = {1: 12, 2: 12, 3: 11, 4: 22, 5: 7, 6: 11, 7: 42}
    for c in range(8, 8 + 19):
        col_widths[c] = 57
    _set_col_widths(ws, col_widths)
    ws.row_dimensions[1].height = 30
    row_h = int(edge * 0.75)
    # Pre-load sizes
    size_cache = {}
    for r in summary:
        for fn in r.get("image_files") or []:
            if fn not in size_cache:
                size_cache[fn] = get_size(images_dir, fn)
    row_idx = 2
    for r in summary:
        for c, v in enumerate(_values(r), 1):
            align_left = c in (4, 7)
            _text_cell(ws, row_idx, c, v, st, align_left=align_left)
        ws.row_dimensions[row_idx].height = row_h
        for k, fn in enumerate(r.get("image_files") or []):
            anchor_col = 8 + k
            p = get_embed_path(images_dir, fn, conv_dir)
            if not p:
                continue
            img = XLImage(p)
            w, h = size_cache.get(fn) or (edge, edge)
            scale = edge / max(w, h)
            img.width = max(1, int(w * scale))
            img.height = max(1, int(h * scale))
            ws.add_image(img, f"{get_column_letter(anchor_col)}{row_idx}")
        row_idx += 1
    return row_idx - 2


def build_detail(ws, summary, st, images_dir, conv_dir, box_w=320, box_h=260,
                 cell_w=327, cell_h=273, row_pt=205):
    """One image per row, text columns vertically merged, image centered."""
    col_widths = {1: 12, 2: 12, 3: 11, 4: 22, 5: 7, 6: 11, 7: 42, 8: 46}
    _set_col_widths(ws, col_widths)
    size_cache = {}
    for r in summary:
        for fn in r.get("image_files") or []:
            if fn not in size_cache:
                size_cache[fn] = get_size(images_dir, fn)
    row_idx = 2
    for r in summary:
        images = r.get("image_files") or []
        n = max(1, len(images))
        # Vertical merge text columns
        for c, v in enumerate(_values(r), 1):
            if n > 1:
                ws.merge_cells(start_row=row_idx, start_column=c,
                               end_row=row_idx + n - 1, end_column=c)
            align_left = c in (4, 7)
            _text_cell(ws, row_idx, c, v, st, align_left=align_left)
        # Image column borders for every row
        for k in range(n):
            _img_cell_border(ws, row_idx + k, 8, st)
        for k, fn in enumerate(images):
            p = get_embed_path(images_dir, fn, conv_dir)
            r_row = row_idx + k
            ws.row_dimensions[r_row].height = row_pt
            if not p:
                continue
            img = XLImage(p)
            w, h = size_cache.get(fn) or (box_w, box_h)
            scale = min(box_w / w, box_h / h)
            disp_w = max(1, int(w * scale))
            disp_h = max(1, int(h * scale))
            img.width = disp_w
            img.height = disp_h
            img.anchor = anchor_centered(7, r_row - 1, disp_w, disp_h, cell_w, cell_h)
            ws.add_image(img)
        if not images:
            ws.row_dimensions[row_idx].height = row_pt
        row_idx += n
    return row_idx - 2


def build_grid(ws, summary, st, images_dir, conv_dir, grid_n=4, cell=160,
               gap=8, step=168, col_w=95, row_pt=126):
    """One row per issue, all images packed into a single 图片 cell, grid layout."""
    col_widths = {1: 12, 2: 12, 3: 11, 4: 22, 5: 7, 6: 11, 7: 42, 8: col_w}
    _set_col_widths(ws, col_widths)
    size_cache = {}
    for r in summary:
        for fn in r.get("image_files") or []:
            if fn not in size_cache:
                size_cache[fn] = get_size(images_dir, fn)
    row_idx = 2
    for r in summary:
        images = r.get("image_files") or []
        n = len(images)
        rows = math.ceil(n / grid_n) if n else 0
        for c, v in enumerate(_values(r), 1):
            align_left = c in (4, 7)
            _text_cell(ws, row_idx, c, v, st, align_left=align_left)
        _img_cell_border(ws, row_idx, 8, st)
        ws.row_dimensions[row_idx].height = max(30, rows * row_pt) if rows else 30
        for k, fn in enumerate(images):
            p = get_embed_path(images_dir, fn, conv_dir)
            if not p:
                continue
            img = XLImage(p)
            w, h = size_cache.get(fn) or (cell, cell)
            scale = min(cell / w, cell / h)
            disp_w = max(1, int(w * scale))
            disp_h = max(1, int(h * scale))
            img.width = disp_w
            img.height = disp_h
            gx = k % grid_n
            gy = k // grid_n
            cell_x = gx * step + (cell - disp_w) / 2
            cell_y = gy * step + (cell - disp_h) / 2
            marker = AnchorMarker(col=7, colOff=pixels_to_EMU(cell_x),
                                  row=row_idx - 1, rowOff=pixels_to_EMU(cell_y))
            img.anchor = OneCellAnchor(_from=marker,
                                       ext=XDRPositiveSize2D(cx=pixels_to_EMU(disp_w),
                                                             cy=pixels_to_EMU(disp_h)))
            ws.add_image(img)
        row_idx += 1
    return row_idx - 2


LAYOUTS = {
    "thumbnail": ("缩略图横向排列（每行多图、跨多列）", build_thumbnail),
    "original":  ("原图横向排列（每行多图、跨多列、文件最大）", build_original),
    "detail":    ("明细行（每图一行，文字列纵向合并）", build_detail),
    "grid":      ("网格汇总（一行一问题，图片集中于 H 列单元格）", build_grid),
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--summary", required=True, help="Path to summary JSON")
    p.add_argument("--images", required=True, help="Directory with extracted images")
    p.add_argument("--out", required=True, help="Output .xlsx path")
    p.add_argument("--layout", choices=list(LAYOUTS), default="grid",
                   help="Output layout (default: grid)")
    p.add_argument("--display-edge", type=int, default=320,
                   help="Display edge in px for thumbnail/original/detail (default: 320)")
    p.add_argument("--grid-n", type=int, default=4,
                   help="Images per row in grid layout (default: 4)")
    p.add_argument("--conv-dir", default=None,
                   help="Where to write transcoded (e.g. MPO -> JPEG) images")
    args = p.parse_args()

    with open(args.summary, encoding="utf-8") as f:
        summary = json.load(f)
    if not isinstance(summary, list):
        print("[ERROR] summary must be a JSON list of records", file=sys.stderr)
        return 2

    conv_dir = args.conv_dir or os.path.join(os.path.dirname(args.out) or ".", "converted_images")

    wb = Workbook()
    ws = wb.active
    ws.title = "问题图片相册"
    st = _styles()
    _write_header(ws, st)
    ws.freeze_panes = "A2"

    note, builder = LAYOUTS[args.layout]
    n_rows = builder(ws, summary, st, args.images, conv_dir,
                     edge=args.display_edge) if args.layout in ("thumbnail", "original") \
        else builder(ws, summary, st, args.images, conv_dir) if args.layout == "detail" \
        else builder(ws, summary, st, args.images, conv_dir, grid_n=args.grid_n)

    out_abs = os.path.abspath(args.out)
    wb.save(out_abs)
    print(f"[OK] Wrote {out_abs}")
    print(f"     Layout: {args.layout} ({note})")
    print(f"     Records: {len(summary)}  Data rows: {n_rows}  Size: {os.path.getsize(out_abs)/1024/1024:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
