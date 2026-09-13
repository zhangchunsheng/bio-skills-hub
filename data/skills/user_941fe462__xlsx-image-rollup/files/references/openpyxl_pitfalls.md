# openpyxl Image-Embedding Pitfalls

Catalog of non-obvious failures encountered when embedding hundreds of images into a single `.xlsx` with `openpyxl`. Each entry includes the symptom, the root cause, and a working fix.

## 1. `load_workbook` crashes on certain drawing-relationship XML

**Symptom:** `openpyxl.load_workbook(path)` raises `AttributeError`, `KeyError`, or hangs on a workbook with several hundred embedded images.

**Root cause:** openpyxl's drawing parser chokes on certain `xl/drawings/_rels/drawing*.xml.rels` shapes (e.g. unusual `Id` values, missing `TargetMode`, or `Target` paths that contain a leading slash with a non-`xl/media` scheme).

**Fix:** Don't load the workbook with openpyxl just to extract images. Use a pure ZIP/XML extractor. See `scripts/extract_images.py` for a working implementation:

```python
with zipfile.ZipFile(path) as zf:
    for name in zf.namelist():
        if name.startswith("xl/media/"):
            # extract + record media path
```

Combine this with `xml.etree.ElementTree` parsing of `xl/workbook.xml`, `xl/_rels/workbook.xml.rels`, each `xl/worksheets/_rels/sheetN.xml.rels`, and each `xl/drawings/_rels/drawingN.xml.rels` to map (sheet, row, col) → image filename.

## 2. `KeyError: '.mpo'` when saving a workbook with MPO images

**Symptom:** `wb.save(out)` raises `KeyError: '.mpo'` deep inside `openpyxl/packaging/manifest.py`.

**Root cause:** openpyxl uses `Pillow.Image.format` as the embedded file extension. Some JPEG files are actually **MPO** (multi-frame 3D photos) — Pillow detects `format='MPO'`, openpyxl embeds with extension `.mpo`, then `mimetypes.types_map[True]['.mpo']` is missing.

**Fix:** Detect MPO at extract/preparation time and transcode to JPEG (first frame only is fine):

```python
im = Image.open(p)
fmt = (im.format or "").upper()
if fmt not in {"PNG", "JPEG", "JPG", "GIF", "BMP"}:
    im.seek(0)
    im.convert("RGB").save(dst, "JPEG", quality=95)
```

The same approach handles other exotic formats (HEIC, AVIF, TIFF) that openpyxl can't embed directly.

## 3. `OneCellAnchor.ext` must be a `XDRPositiveSize2D`, not a tuple

**Symptom:** `wb.save(out)` raises:
```
OneCellAnchor.ext should be <class 'openpyxl.drawing.xdr.XDRPositiveSize2D'>
but value is <class 'tuple'>
```

**Root cause:** `XDRPositiveSize2D(cx=..., cy=...)` is the correct type for the `ext` attribute. Passing a plain tuple gives the wrong runtime type.

**Fix:**
```python
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.utils.units import pixels_to_EMU

ext = XDRPositiveSize2D(cx=pixels_to_EMU(disp_w), cy=pixels_to_EMU(disp_h))
anchor = OneCellAnchor(_from=marker, ext=ext)
img.anchor = anchor
```

## 4. `AnchorMarker` is 0-indexed; `pixels_to_EMU` is your friend

**Symptom:** Images are anchored to the wrong cell or offset by one row/column.

**Root cause:** `AnchorMarker(col, colOff, row, rowOff)` uses **0-based** column and row indices, but `xl/worksheets/sheet1.xml` cells are also 0-based, while openpyxl's `ws.cell(row=1, column=1)` is **1-based**.

**Fix:** Subtract 1 when building markers from openpyxl row numbers, and remember `pixels_to_EMU(px)` returns `int(px * 9525)` (1px = 9525 EMU at 96 DPI).

```python
marker = AnchorMarker(
    col=ws_col - 1,            # 0-based
    colOff=pixels_to_EMU(x_offset_px),
    row=ws_row - 1,            # 0-based
    rowOff=pixels_to_EMU(y_offset_px),
)
```

## 5. Centering an image inside its cell

To center an image inside a fixed-size cell, compute the offset from the cell's top-left to the image's top-left:

```python
cell_w_px = 327   # H column width in pixels
cell_h_px = 273   # row height in pixels
disp_w, disp_h = image.display_width, image.display_height  # already scaled
col_off = pixels_to_EMU((cell_w_px - disp_w) / 2)
row_off = pixels_to_EMU((cell_h_px - disp_h) / 2)
```

Where `cell_w_px` is approximated as `column_width_chars * 7 + 5` (Calibri 11 default), and `cell_h_px` is `row_height_pt / 0.75`.

## 6. Column width and row height units

| Setting | Unit | To pixels (approx) |
|---|---|---|
| `ws.column_dimensions[X].width` | characters (Excel) | `width * 7 + 5` |
| `ws.row_dimensions[r].height` | points (1pt = 1/72 inch) | `height / 0.75` |

For a 96-DPI image, 1px = 0.75pt and 1px = 9525 EMU. To make an image display at exactly N pixels inside a fixed cell, set the column width to `N/7` characters and the row height to `N*0.75` points (with a small safety margin).

## 7. Mismatched `img.width` vs `anchor.ext`

If you set `img.width = disp_w` but `OneCellAnchor.ext = XDRPositiveSize2D(cx=..., cy=...)` does not match, openpyxl may save the file but Excel will display the image at the original (unscaled) size. Always keep `img.width/height` in sync with `XDRPositiveSize2D.cx/cy`.

## 8. `wb.save` silently uses the wrong file path

When the source workbook was opened by WPS/Excel, saving back to the same path can fail with `PermissionError` because the file is locked. `shutil.copyfile` from a freshly saved file in a different directory works; do that as a separate step after `wb.save`.

## 9. The `freeze_panes` magic string

Set `ws.freeze_panes = "A2"` to freeze the first row. Any cell address works — the column to the left and row above the cell are frozen.

## 10. Merge cells + image anchors

`ws.merge_cells` clears values in non-top-left cells. Always write the text value **before** merging, and apply alignment (e.g. `vertical="center"`) on the top-left cell of the merge.
