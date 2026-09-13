# Medical Device Poster From PPTX — Workflow Notes

## Environment facts (verified on this macOS box, 2026-07-28)

1. **LibreOffice is NOT reliably available.** `/opt/homebrew/bin/soffice` is a wrapper, but `/Applications/LibreOffice.app` is absent → `soffice --headless --convert-to pdf` fails immediately. Use the bundled `make_pdf.py` (reportlab) instead of fighting soffice. Only try soffice if you confirmed `test -e /Applications/LibreOffice.app` first.
2. **`pymupdf` cannot be installed** here — `pip install pymupdf` is killed (OOM, exit 137) repeatedly. Do NOT depend on it. For PDF→PNG QA use system `pdftoppm` (poppler) or `gs`.
3. **`markitdown` is not preinstalled.** Use `scripts/extract_source.py` (python-pptx backend) — it dumps text + every embedded image and reports which slides mention the product keyword.
4. **Packages that DO work** in the managed venv: `python-pptx`, `Pillow`, `reportlab`, `openpyxl`, `python-docx`.

## Layout model (A1 portrait, 594 × 841 mm)

- 3-column top section (Background / Design+Specs / Intended Use) + optional per-card source image.
- Full-width "Representative Cases" band with 3 case cards (image + ≤3 bullets each).
- 2-column bottom band (Evidence & Limitations / Conclusions).
- Dark-blue top banner (DRAFT warning) and footer (Sources + Claim ledger + review note).
- All content is data-driven via `poster_data.py`; the two renderers share `poster_common.py` constants.

## Common pitfalls

1. **EMU conversion**: 1 mm = 36000 EMU. A wrong multiplier (e.g. 360000) overflows the slide. The bundled scripts use `MM = 36000`.
2. **PDF CJK font**: reportlab TTFont may fail to load `.ttc` collections. Fallback chain in `make_pdf.py`: PingFang → STHeiti Light → **STSong-Light** (built-in CID, always renders CJK). Always render PNG and verify glyphs.
3. **Image aspect fit**: neither engine auto-fits. Both use `scale = min(max_w/iw, max_h/ih)` and center the image.
4. **Text overflow**: A1 holds a lot, but text boxes overflow silently. Keep ≤6 bullets per card and verify with the rendered PNG.
5. **Compliance terms**: the medpostdesign claim ledger blocks `唯一`, `第一`, `最佳`, `顶级`, `领先`, `彻底`, `保证`, `零风险`, `100%有效`, `显著改善`. Use source wording literally; never escalate (e.g. write "内漏减少", not "内漏消失").
6. **Case images**: academic posters need de-identified images + documented consent/IRB. Always flag the poster as DRAFT pending review.

## Validation checklist

- [ ] `required-input-gate.csv` has all 13 expected fields; validator returns `READY*` (0 errors).
- [ ] `claim-ledger.csv` has valid statuses/types; reviewer/footnote present for intended-use / evidence / case-context / outcome claims; validator returns 0 errors.
- [ ] `poster_data.py` exists in the project dir and imports without error.
- [ ] PDF rendered to PNG shows no overlaps; CJK readable; case images fit their cards.
- [ ] Speaker notes contain `[Sources]` and `[Claim Audit]`.
- [ ] Footer marks DRAFT + review requirements.

## Example claim types

| Claim | Type | Status | Reviewer required |
|---|---|---|---|
| "Nitinol (Ni/Ti 50/50)" | specification | VERIFIED | no |
| "Indicated for abdominal aorta..." | intended-use | VERIFIED | yes |
| "Branch perfusion restored" | outcome | SOURCE-QUOTED / REVIEW | yes |
| "Published study showed 96.8% technical success" | evidence | SOURCE-QUOTED / REVIEW | yes |
| "Case angiogram from X Hospital" | visual-asset | SOURCE-QUOTED / REVIEW | yes |

## Output files

```
output/
├── <product>_academic_poster.pptx
├── <product>_academic_poster.pdf
└── <product>_poster_preview-1.png
```
