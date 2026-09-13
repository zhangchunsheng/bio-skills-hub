---
name: xlsx-image-rollup
description: This skill should be used when the user wants to aggregate, summarize, or "roll up" a multi-sheet Excel workbook that contains embedded images (drawings) into a single summary table that also embeds the relevant images grouped by category/series/issue/responsibility. Trigger phrases include "把登记表按 XX 分类整理", "问题汇总 + 附图", "按维度聚合并附图片", "生成图片汇总相册", "embedded-image xlsx rollup", "把每张问题图片单独放在单元格中", "按问题点汇总图片", and any request where the source `.xlsx` contains a few hundred to a few thousand embedded product/issue images and the deliverable is a single grouped album/summary sheet.
---

# xlsx-image-rollup

## Overview

Aggregate a multi-sheet `.xlsx` (each row may carry an embedded image) into a single grouped summary table that also embeds the relevant images. The source workbook is typically a quality-issue registration form, inspection log, or after-sales complaint table where every record has 1–N photos. The output is a single Excel file with one "rollup" sheet where rows are grouped by `category → series → responsibility → issue point`, with frequency, percentage, user-original-quote and grouped images side by side.

Four output layouts are supported (selectable via `--layout`):

- `thumbnail` – 180px thumbnails, multiple images per row arranged horizontally
- `original` – original image data embedded (no resampling), 400px display
- `detail` – one image per row, text columns vertically merged, image centered in a fixed cell
- `grid` – one row per issue, all images packed into a single "图片" cell in a 4-per-line grid

## Workflow

To produce a rollup from a source `.xlsx`, follow these steps:

1. **Inspect the source workbook** to find the data sheets, header row, image-bearing column(s), and any image variants (`.png`/`.jpeg`/`.mpo`).
2. **Extract embedded images** via `scripts/extract_images.py` (ZIP-level, NOT openpyxl). Save to a flat directory using a stable `image{N}.{ext}` naming scheme.
3. **Aggregate rows** by `(category, series, responsibility, issue)` dimensions. For each unique key, count frequency, compute `count / series_total` percentage, collect user-original-quotes, and collect the list of image filenames.
4. **Choose a layout** by asking the user which of the four layouts fits the use case (or default to `grid` for the most compact one-row-per-issue presentation).
5. **Build the output workbook** via `scripts/build_album.py` with `--layout` and the summary JSON.
6. **Deliver** the output `.xlsx` via `present_files` and offer to adjust layout/sizing.

## Key decisions to make with the user

- **Layout** – `thumbnail` (smallest file, fastest), `original` (largest, full resolution), `detail` (each image in its own cell), `grid` (one row per issue, images in a single cell, recommended default).
- **Display edge** – only relevant for `thumbnail`/`original`/`detail`. Default 320px gives a balance of clarity and row density.
- **Grid width** – only relevant for `grid`. Default 4 images per row; lower to 3 for larger images.

## Critical pitfalls to avoid

See `references/openpyxl_pitfalls.md` for the full list. The non-obvious ones are:

- **DO NOT use `openpyxl.load_workbook` to read drawings** on a large file with hundreds of embedded images — it can crash on certain drawing-relationship XML. Use the ZIP-level extractor in `scripts/extract_images.py` instead.
- **MPO images** (3D/multi-frame, extension may be `.jpeg`) trigger `KeyError: '.mpo'` in openpyxl because openpyxl uses `Pillow.Image.format` as the embedded extension. The scripts auto-detect MPO and convert to JPEG via `Pillow.Image.seek(0).convert('RGB').save('JPEG')`.
- **OneCellAnchor.ext must be `XDRPositiveSize2D(cx, cy)`**, NOT a `(w, h)` tuple. The error message says `value is <class 'tuple'>` but the real fix is to import from `openpyxl.drawing.xdr` and construct the proper class.
- **Cell-center an image** with `AnchorMarker(col=..., colOff=pixels_to_EMU(x), row=..., rowOff=pixels_to_EMU(y))` and `OneCellAnchor(_from=marker, ext=XDRPositiveSize2D(...))`. The `x`/`y` offsets are the distance from the cell's top-left in pixels.
- **Column width and row height units**: column width is in "characters" (≈ 7px each for Calibri 11); row height is in `pt` (1pt = 1/72 inch, ≈ 1.33px). Convert with `pixels_to_EMU(px)` from `openpyxl.utils.units` (1px = 9525 EMU).

## Resources

### scripts/

- `extract_images.py` – ZIP-level image extractor. Takes `<input.xlsx> <output_dir>` and writes every embedded image (across all sheets) to the output dir using `image{N}.{ext}` naming. Handles MPO and other exotic formats.
- `build_album.py` – Build a rollup workbook from a summary JSON + extracted image directory. Supports `--layout {thumbnail,original,detail,grid}`. Produces a styled xlsx with frozen header, blue header fill, bordered cells, and a "图片" column.

### references/

- `openpyxl_pitfalls.md` – Detailed catalog of openpyxl embedding pitfalls with reproductions and fixes.
- `layouts.md` – Visual decision guide for choosing the right layout, with example row/column counts and file size impact.
