# Layout Decision Guide

Four output layouts are supported by `scripts/build_album.py`. Each trades off file size, row density, image clarity, and the visual relationship between text and images.

## At a glance

| Layout | Rows | File size | Image clarity | When to use |
|---|---|---|---|---|
| `thumbnail` | one per issue | smallest (~16 MB / 500 images) | 180px previews | Quick visual scan; minimum file size |
| `original` | one per issue | largest (~140 MB / 500 images) | full resolution, 400px display | When pixel-perfect inspection matters |
| `detail` | one per image | very large | 320px centered in fixed cell | When each image is reviewed individually |
| `grid` | one per issue | large | 160px grid, 4 per row | **Recommended default.** Compact, every image visible |

## `thumbnail` — multiple images per row, horizontally

- 7 text columns (A–G) + 1 image column (H) extending rightward up to 19 slots
- All images for one issue share the same row
- Images uniformly scaled to 180px (longest edge), anchored top-left of each slot
- **File size:** ~32 KB per image after compression
- **Best for:** Email-friendly distribution, mobile viewing, low-bandwidth scenarios
- **Trade-off:** The text columns are narrow because the image area extends 19 columns; horizontal scrolling is heavy on small screens

## `original` — same as `thumbnail` but with full image data

- Identical layout to `thumbnail`, but images are embedded at original resolution (no resampling)
- Display size 400px (longest edge), double-click to view full-size in Excel
- **File size:** proportional to source images (~280 KB each on average, so 500 images ≈ 140 MB)
- **Best for:** Quality-control workflows where reviewers need to zoom in
- **Trade-off:** Opening and scrolling will feel sluggish; 100+ MB files may exceed some email attachment limits

## `detail` — one image per row, text columns vertically merged

- One row per image (an issue with 5 photos spans 5 rows)
- Text columns A–G are vertically merged across those rows and centered
- H column has a fixed 320×260 cell with the image centered (no resampling)
- **File size:** ≈ same as `original`
- **Best for:** When each image is reviewed individually with its context above
- **Trade-off:** Issues with many images take many rows; comparing across issues requires vertical scrolling

## `grid` — one row per issue, all images in a single cell

- One row per issue (375 rows for 375 unique issue points)
- A–G are text columns; H is a wide "图片" cell containing all images in a 4-per-row grid
- Images uniformly scaled to 160px, centered in 160px grid units with 8px gaps
- Row height auto-adjusts: 1 grid row (~126pt) for ≤4 images, 2 for 5–8, etc.
- **File size:** ≈ same as `original` (full image data embedded)
- **Best for:** Compact scanning, comparing many issues side-by-side, dashboard-style review
- **Trade-off:** With 19 images in one issue, the row becomes 5 grid rows tall (~630pt) — but only 1 issue is that extreme

## Choosing the right layout

Ask the user two questions:

1. **Will reviewers double-click images to see full detail, or are thumbnails enough?**
   - Thumbnails enough → `thumbnail` (smallest file, fastest)
   - Need detail → `original` or `grid`
2. **Compact one-row-per-issue or expanded one-image-per-row?**
   - Compact → `grid` (recommended)
   - Expanded → `detail`

If the user can't decide, default to `grid` — it gives the best balance of clarity, density, and reviewability.

## Tuning parameters

- `--display-edge N` (default 320) — controls the longest edge of the image in `thumbnail`/`original`/`detail`. Larger = clearer but bigger cells; smaller = more compact.
- `--grid-n N` (default 4) — controls images per row in `grid`. Lower (3) for larger cells and better clarity; higher (6) for more density.

## Performance notes

- The dominant cost is the final `wb.save`. For a 500-image workbook, expect 30–90 seconds on a typical machine.
- Building the summary and reading sizes happens in-memory; extraction is O(number of images) and is fast.
- If the source workbook is huge (>500 MB) consider running `extract_images.py` on a separate machine and copying only the output directory to where `build_album.py` runs.
