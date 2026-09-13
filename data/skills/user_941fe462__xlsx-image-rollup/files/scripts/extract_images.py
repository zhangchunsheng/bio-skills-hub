"""
Extract every embedded image from an .xlsx workbook to a flat directory.

ZIP-level extraction (not openpyxl) to avoid openpyxl crashing on certain
drawing-relationship XML. Also emits an image_index.json describing where
each image was anchored (sheet -> row -> col -> filename), so a downstream
aggregator can join cell text with image filenames by (sheet, row).

Usage:
    python extract_images.py <input.xlsx> <output_dir> [--map image_index.json]

Output:
    output_dir/image1.png, image2.jpeg, ...      (one file per embedded image)
    output_dir/image_index.json                 (anchor map)
"""
import argparse
import json
import os
import re
import shutil
import sys
import zipfile
from xml.etree import ElementTree as ET


NS = {
    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    "a":   "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r":   "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}

SHEET_RELS = re.compile(r"xl/worksheets/_rels/(sheet\d+)\.xml\.rels")
DRAWING_RELS = re.compile(r"xl/drawings/_rels/(drawing\d+)\.xml\.rels")


def q(name: str) -> str:
    """Return Clark-notation qualified name for a local name."""
    for prefix, uri in NS.items():
        if prefix in ("xdr", "a", "r", "main"):
            yield f"{{{uri}}}{name}"


def parse_sheet_drawing_map(zf: zipfile.ZipFile) -> dict:
    """Return {sheet_name: drawing_path} by joining workbook.xml + sheet rels."""
    wb_xml = zf.read("xl/workbook.xml")
    root = ET.fromstring(wb_xml)
    sheets = {}
    for sh in root.iter(f"{{{NS['main']}}}sheet"):
        # rid is in attribute r:id
        rid = sh.attrib.get(f"{{{NS['r']}}}id")
        name = sh.attrib.get("name")
        sheets[rid] = name
    # workbook rels: rid -> sheet path
    wb_rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {}
    for rel in wb_rels.iter(f"{{{NS['rel']}}}Relationship"):
        rid_to_target[rel.attrib["Id"]] = rel.attrib["Target"]
    sheet_to_drawing = {}
    for rid, name in sheets.items():
        sheet_path = rid_to_target.get(rid)
        if not sheet_path:
            continue
        # find sheet rels file
        rels_path = "xl/" + os.path.dirname(sheet_path) + "/_rels/" + os.path.basename(sheet_path) + ".rels"
        rels_path = rels_path.replace("xl/worksheets/_rels/worksheets/", "xl/worksheets/_rels/")
        if rels_path not in zf.namelist():
            # try direct
            alt = "xl/worksheets/_rels/" + os.path.basename(sheet_path) + ".rels"
            if alt in zf.namelist():
                rels_path = alt
        if rels_path not in zf.namelist():
            continue
        sheet_rels = ET.fromstring(zf.read(rels_path))
        for rel in sheet_rels.iter(f"{{{NS['rel']}}}Relationship"):
            if rel.attrib.get("Type", "").endswith("/drawing"):
                # Target is relative to xl/
                tgt = rel.attrib["Target"]
                if tgt.startswith("/"):
                    drawing_path = tgt.lstrip("/")
                else:
                    base = os.path.dirname("xl/" + sheet_path)
                    drawing_path = os.path.normpath(os.path.join(base, tgt)).replace("\\", "/")
                sheet_to_drawing[name] = drawing_path
    return sheet_to_drawing


def parse_drawing_anchors(zf: zipfile.ZipFile, drawing_path: str) -> list:
    """Return list of (row0, col0, rId) for each <xdr:twoCellAnchor>/<xdr:oneCellAnchor>."""
    if drawing_path not in zf.namelist():
        return []
    xml = zf.read(drawing_path)
    root = ET.fromstring(xml)
    anchors = []
    # The drawing element wraps anchors
    for anchor in list(root):
        tag = anchor.tag.split("}", 1)[-1]
        if tag not in ("twoCellAnchor", "oneCellAnchor"):
            continue
        from_marker = anchor.find("xdr:from", NS)
        if from_marker is None:
            continue
        col = int(from_marker.find("xdr:col", NS).text)
        row = int(from_marker.find("xdr:row", NS).text)
        # find blip r:embed
        blip = anchor.find(".//a:blip", NS)
        if blip is None:
            continue
        rid = blip.attrib.get(f"{{{NS['r']}}}embed")
        if not rid:
            continue
        anchors.append((row, col, rid))
    return anchors


def parse_drawing_rels(zf: zipfile.ZipFile, drawing_path: str) -> dict:
    """Return {rId: media_path} for a drawing's rels file."""
    base = os.path.dirname(drawing_path)
    rels_name = os.path.basename(drawing_path) + ".rels"
    rels_path = f"{base}/_rels/{rels_name}" if base else f"_rels/{rels_name}"
    rels_path = rels_path.replace("\\", "/")
    if rels_path not in zf.namelist():
        return {}
    rels = ET.fromstring(zf.read(rels_path))
    out = {}
    for rel in rels.iter(f"{{{NS['rel']}}}Relationship"):
        out[rel.attrib["Id"]] = rel.attrib["Target"]
    return out


def normalize_media_path(target: str, drawing_path: str) -> str:
    """Resolve a drawing rels Target to an xlsx-internal path."""
    if target.startswith("/"):
        return target.lstrip("/")
    base = os.path.dirname(drawing_path)
    return os.path.normpath(os.path.join(base, target)).replace("\\", "/")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="Path to source .xlsx")
    p.add_argument("output_dir", help="Directory to write extracted images")
    p.add_argument("--map", default="image_index.json",
                   help="Filename for the anchor map (default: image_index.json)")
    p.add_argument("--no-map", action="store_true",
                   help="Skip writing the anchor map (only extract images)")
    args = p.parse_args()

    if not os.path.isfile(args.input):
        print(f"[ERROR] input not found: {args.input}", file=sys.stderr)
        return 2

    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)

    with zipfile.ZipFile(args.input) as zf:
        # 1. Sheet -> drawing
        sheet_to_drawing = parse_sheet_drawing_map(zf)
        if not sheet_to_drawing:
            print("[WARN] No drawings found in any sheet.")

        # 2. For each sheet, parse anchors + rels, copy media, build anchor map
        anchor_map = {}     # sheet_name -> { "row_index": [{"col", "filename", "media_path"}] }
        written = {}        # media_path -> output filename (dedup identical media)
        next_id = [1]
        media_seen = {}     # (sheet_name, rId) -> filename, to dedupe

        for sheet_name, drawing_path in sheet_to_drawing.items():
            anchors = parse_drawing_anchors(zf, drawing_path)
            if not anchors:
                continue
            rels = parse_drawing_rels(zf, drawing_path)
            sheet_anchors = {}
            for row0, col0, rid in anchors:
                target = rels.get(rid)
                if not target:
                    continue
                media_path = normalize_media_path(target, drawing_path)
                if media_path not in zf.namelist():
                    continue
                if media_path not in written:
                    ext = os.path.splitext(media_path)[1].lstrip(".") or "png"
                    fname = f"image{next_id[0]}.{ext}"
                    next_id[0] += 1
                    with zf.open(media_path) as src, open(os.path.join(out_dir, fname), "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    written[media_path] = fname
                fname = written[media_path]
                # row0/col0 are 0-based; convert to 1-based for human friendliness
                sheet_anchors.setdefault(str(row0 + 1), []).append({
                    "col": col0 + 1,
                    "filename": fname,
                    "media_path": media_path,
                })
            if sheet_anchors:
                anchor_map[sheet_name] = sheet_anchors

    if not args.no_map:
        map_path = os.path.join(out_dir, args.map)
        with open(map_path, "w", encoding="utf-8") as f:
            json.dump(anchor_map, f, ensure_ascii=False, indent=2)
        print(f"[OK] Wrote anchor map: {map_path}")

    print(f"[OK] Extracted {len(written)} images to: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
