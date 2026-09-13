---
name: medical-device-poster-from-pptx
description: Create source-grounded, compliance-gated A1 portrait medical-device academic posters from a product PPTX. Follows the medpostdesign workflow, extracts text/images from the source deck with bundled python-pptx scripts, runs required-input and claim-ledger gates, then generates an editable PPTX + PDF + PNG QA preview via bundled data-driven renderers.
agent_created: true
---

# Medical Device Poster From PPTX

## When to use

Use this skill when the user asks to create an academic-conference or exhibition poster for a medical device based on an existing product presentation (PPTX). Typical triggers:

- "根据这个产品资料，出一个 XXX 的学术会议海报"
- "把这份产品介绍做成海报"
- "Generate a medical-device poster from this deck"

## Prerequisites

1. The `medpostdesign` skill must be installed at `~/.workbuddy/skills/medpostdesign/` (it provides the compliance gate CSV templates + the two validator scripts).
2. A managed Python venv at `~/.workbuddy/binaries/python/envs/default/` with: `python-pptx`, `Pillow`, `reportlab`.
   - **Do NOT rely on `pymupdf`** — on this box `pip install pymupdf` is killed (OOM, exit 137) twice. Use system `pdftoppm` (poppler) for PDF→PNG QA instead.
   - **`markitdown` is NOT preinstalled** — use the bundled `scripts/extract_source.py` (python-pptx backend) to dump text + images.
3. System tool `pdftoppm` (poppler) for PDF→PNG QA.
4. **LibreOffice is usually NOT usable**: the `soffice` wrapper script exists at `/opt/homebrew/bin/soffice`, but `/Applications/LibreOffice.app` is absent, so `soffice --headless --convert-to pdf` fails. Go straight to the bundled `scripts/make_pdf.py` (reportlab) for PDF generation — do not waste a turn on soffice unless you first confirm the app is installed.

## Workflow

### Step 1 — Set up project directory

```
<workspace>/medpost_<product>/
├── source_pack/          # copy the source PPTX here
├── build/                # compliance CSVs
├── output/               # final PPTX / PDF / PNG
└── resources/
    ├── extracted/        # text dump
    └── images/           # extracted images (auto-filled)
```

### Step 2 — Extract source content and images

```bash
python scripts/extract_source.py "source_pack/<source.pptx>" <KEYWORD>
```

- Dumps all slide text to `resources/extracted/source_text.txt`.
- Saves every embedded picture to `resources/images/slideNN_imgNN.<ext>`.
- Prints which slides mention `<KEYWORD>` (default `sinus`) so you can locate the product-specific content.
- Principles: extract images only from the source deck; never generate fake clinical images. Prefer source angiograms/CTAs/device photos over generated graphics.

### Step 3 — Run compliance gates (medpostdesign)

Fill the two medpostdesign CSV templates in `build/`:

- `required-input-gate.csv` — one row per expected field (product_name, device_category, source_pack, audience, channel, poster_type, output_size, approved_intended_use, key_specifications, evidence, legal_boundary, product_image, brand_assets).
- `claim-ledger.csv` — one row per claim used in the poster. Allowed statuses: `VERIFIED`, `SOURCE-QUOTED / REVIEW`, `MISSING`, `DO NOT USE`. Allowed types: `feature`, `specification`, `intended-use`, `evidence`, `case-context`, `outcome`, `comparison`, `visual-asset`.

Run validators:

```bash
python ~/.workbuddy/skills/medpostdesign/scripts/validate_required_inputs.py build/required-input-gate.csv
python ~/.workbuddy/skills/medpostdesign/scripts/validate_claim_ledger.py build/claim-ledger.csv
```

Fix any ERROR before proceeding. Warnings are acceptable if disclosed in the poster.

### Step 4 — Author the poster data (the single source of truth)

Copy the bundled template and edit it:

```bash
cp scripts/poster_data.py.example poster_data.py
```

`poster_data.py` drives BOTH renderers. Fill in: `title`, `subtitle`, `author_line`, `top_sections[3]`, `cases[3]`, `bottom_sections[2]`, `footer_lines`, `notes` (the `[Sources]` / `[Claim Audit]` / `[Review Points]` block for speaker notes). Keep bullets ≤6 per card. Image fields are filenames resolved against `resources/images/`.

Optionally also write `STORY.md` / `DESIGN.md` for the narrative rationale, but `poster_data.py` is what gets rendered.

### Step 5 — Generate the poster

```bash
python scripts/make_poster.py   # -> output/<out_pptx>
python scripts/make_pdf.py      # -> output/<out_pdf>  (reportlab fallback; no LibreOffice needed)
```

Both read `poster_data.py` from the current dir. The PPTX is fully editable; the PDF uses `STSong-Light` (CID) so CJK always renders even without a system CJK TTF.

### Step 6 — Render PNG for QA

```bash
pdftoppm -png -r 100 output/<out_pdf> output/<product>_poster_preview
```

Visually check for overlaps, missing CJK glyphs, and image fit. Iterate on `poster_data.py` (content) or the renderer scripts (layout) until clean.

### Step 7 — Deliver

Present:

- `output/<product>_academic_poster.pptx`
- `output/<product>_academic_poster.pdf`
- `output/<product>_poster_preview-1.png`

Explicitly warn the user:

- This is a DRAFT for internal review.
- Case images require verified patient consent / IRB / publication rights.
- Medical Affairs and Regulatory must approve before any conference display.

## Tool mapping (WorkBuddy, verified on this box)

| medpostdesign original | WorkBuddy replacement actually used |
|---|---|
| `@oai/artifact-tool` / Presentations skill | Managed Python + `python-pptx` (bundled `make_poster.py`) |
| PDF skill | `reportlab` (`make_pdf.py`); `pymupdf` install fails → `pdftoppm` for QA |
| Documents/Spreadsheets skill | `python-pptx` extraction (bundled `extract_source.py`); `markitdown` absent |
| image generation | Source images only; no AI-generated clinical images |

## Bundled scripts

- `scripts/extract_source.py` — dump source text + images, locate keyword slides.
- `scripts/poster_common.py` — shared A1 layout constants/colours.
- `scripts/make_poster.py` — PPTX renderer (python-pptx).
- `scripts/make_pdf.py` — PDF renderer (reportlab, no LibreOffice dependency).
- `scripts/poster_data.py.example` — template data (Sinus XL worked example).

## References

- `references/workflow.md` — detailed notes, pitfalls, validation checklist, claim examples.
