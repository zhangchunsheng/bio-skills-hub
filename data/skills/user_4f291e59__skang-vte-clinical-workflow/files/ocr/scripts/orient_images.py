"""图片方向自动校正（OCR 前置必做步骤）。

背景：RapidOCR/PaddleOCR 的检测+方向分类是「方向不变」的，横放、倒置的照片
OCR 文本量几乎一样，所以不能用识别文本长度或置信度来判方向。本脚本改用几何+
方向分类器两级判据：

1. EXIF Orientation 先做无损纠正（手机照片常见）。
2. 用文本检测框的中位宽高比判断竖横：正立/倒置时文字行是横向长条（AR>1），
   旋转 90/270 时为竖向长条（AR<1）。
3. 在选定的基准方向上裁出文本条，交给 PP-OCR 方向分类器（text_cls）判断
   0 / 180，按置信度加权投票决定是否再转 180 度。
4. 输出校正后的图片（原文件名）+ `_orientation_report.json` 报告。
   置信度不足的图片会标记 low_confidence，提示人工确认。

用法：
    python orient_images.py --input <图片或文件夹> --output <校正后目录> [--probe-size 1400]

全程本机运行，不上传任何图片。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def load_engine():
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


def _probe_array(pil_img: Image.Image, probe_size: int) -> np.ndarray:
    img = pil_img.copy()
    img.thumbnail((probe_size, probe_size), Image.LANCZOS)
    return np.array(img.convert("RGB"))


def _detect_boxes(engine, arr: np.ndarray):
    boxes, _ = engine.text_detector(arr)
    if boxes is None or len(boxes) == 0:
        return None
    return engine.sorted_boxes(boxes)


def _horizontal_score(boxes) -> tuple[float, int]:
    """返回 (中位宽高比, 横向长条数量)。"""
    ratios = []
    for b in boxes:
        b = np.asarray(b)
        w = float(b[:, 0].max() - b[:, 0].min())
        h = float(b[:, 1].max() - b[:, 1].min())
        ratios.append(w / max(h, 1.0))
    ratios = np.array(ratios)
    return float(np.median(ratios)), int((ratios > 2.0).sum())


def _upside_down_vote(engine, arr: np.ndarray, boxes) -> tuple[float, float]:
    """用方向分类器对文本条投票，返回 (正立票, 倒置票)，票值按置信度加权。"""
    crops = engine.get_crop_img_list(arr, boxes)
    if not crops:
        return 0.0, 0.0
    crops = crops[:60]
    _, cls_res, _ = engine.text_cls(crops)
    up = down = 0.0
    for label, score in cls_res:
        score = float(score)
        if score < 0.6:
            continue
        if str(label) == "180":
            down += score
        else:
            up += score
    return up, down


def process_one(engine, src: Path, out_dir: Path, probe_size: int) -> dict:
    img = ImageOps.exif_transpose(Image.open(src))

    stats = {}
    for angle in (0, 90):
        arr = _probe_array(img if angle == 0 else img.rotate(-angle, expand=True), probe_size)
        boxes = _detect_boxes(engine, arr)
        if boxes is None:
            stats[angle] = {"median_ar": 0.0, "wide": 0, "arr": arr, "boxes": None}
        else:
            med, wide = _horizontal_score(boxes)
            stats[angle] = {"median_ar": med, "wide": wide, "arr": arr, "boxes": boxes}

    base = 0 if stats[0]["wide"] >= stats[90]["wide"] else 90
    other = 90 if base == 0 else 0
    wide_margin = abs(stats[0]["wide"] - stats[90]["wide"])

    up = down = 0.0
    if stats[base]["boxes"] is not None:
        up, down = _upside_down_vote(engine, stats[base]["arr"], stats[base]["boxes"])
    final_angle = base if up >= down else (base + 180) % 360

    final = img if final_angle == 0 else img.rotate(-final_angle, expand=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / src.name
    final.convert("RGB").save(dst, quality=95, subsampling=0)

    total_vote = up + down
    low_conf = (
        stats[base]["boxes"] is None
        or wide_margin < 3
        or total_vote <= 0
        or abs(up - down) < 0.25 * total_vote
    )
    return {
        "file": src.name,
        "rotation_applied": final_angle,
        "base_from_geometry": base,
        "wide_boxes": {"0": stats[0]["wide"], "90": stats[90]["wide"]},
        "median_ar": {"0": round(stats[0]["median_ar"], 2), "90": round(stats[90]["median_ar"], 2)},
        "cls_vote": {"upright": round(up, 2), "upside_down": round(down, 2)},
        "low_confidence": bool(low_conf),
        "output": str(dst),
        "_unused_other": other,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--probe-size", type=int, default=1400)
    args = ap.parse_args()

    src = Path(args.input)
    out_dir = Path(args.output)
    if src.is_dir():
        files = sorted(p for p in src.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    elif src.suffix.lower() in IMAGE_EXTS:
        files = [src]
    else:
        files = []
    if not files:
        print(json.dumps({"error": "no image found", "input": str(src)}, ensure_ascii=False))
        return 1

    engine = load_engine()
    reports = []
    for f in files:
        rep = process_one(engine, f, out_dir, args.probe_size)
        rep.pop("_unused_other", None)
        reports.append(rep)
        print(
            f"[orient] {rep['file']} -> {rep['rotation_applied']}deg "
            f"wide={rep['wide_boxes']} cls={rep['cls_vote']} low_conf={rep['low_confidence']}",
            flush=True,
        )
    report_path = out_dir / "_orientation_report.json"
    report_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[orient] report -> {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
