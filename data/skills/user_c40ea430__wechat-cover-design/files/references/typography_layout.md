# Typography And Layout System

Use this deterministic layout for native-image post-production. Do not ask an image model to render the final Chinese title: it is not a deterministic typography engine.

## Canvas and fixed coordinates

- Output canvas: `1584x672` (approximately 2.35:1), crop-safe for WeChat.
- Default title field: `x=76..620`, `y=88..585`; keep all text left aligned.
- Eyebrow: one line only, 25 px, with an 18 px minimum. It contains content class and angle only; never place a title term on a second eyebrow line.
- Title prefix: optional but immutable when supplied, for example `Ab-mRNA-LNP`; 46 px, minimum 38 px, using the selected Latin display face.
- Main title: one or two semantic Chinese lines, default 62 px, minimum 52 px. It is deliberately one scale below the former 72 px title size so it retains a buffer from the right-side subject.
- Subtitle: up to two lines, 34 px, with a 26 px minimum. It explains the claim and must not repeat the main title.
- Footer: `抗体精准定位 · mRNA 递送 · 体内生成 CAR-T`, one line, 20 px, with a 16 px minimum.
- Do not add a box, underline, divider, shadow, gradient, or translucent panel behind text.
- Place text directly on the source image's natural quiet field. If no quiet field exists, regenerate the background first.
- The title group is eyebrow, optional title prefix, and one or two main-title lines. Preserve every supplied title term verbatim; do not move a title prefix into the eyebrow, subtitle, or footer.
- Effective text width is `500 px` within the fixed title field. The compositor measures eyebrow, main-title, subtitle, and footer lines and shrinks each group only to its documented minimum; if a line still does not fit, it rejects the layout and requires a semantic line break.
- Fixed baselines: eyebrow `y=96`; title prefix `y=140`; main title lines `y=210` and `y=288`; subtitle lines `y=398` and `y=445`; footer `y=548`.

## Generation-to-layout conversion

Use the same title field in two representations. Image prompts use percentages; post-production uses pixels on the canonical canvas.

| Canonical pixels (`1584x672`) | Prompt percentage |
| --- | --- |
| `x=76..620` | `x=4.8%..39.1%` |
| `y=88..585` | `y=13.1%..87.1%` |

For another 2.33-2.35:1 input image, `scripts/compose_cover.py` scales these coordinates and font sizes proportionally. When the provider supports only 16:9, generate the text-free background at 16:9, center-crop it to 2.35:1, then audit and overlay the title. Do not use a different title zone for generation and post-production.

## Background-only requirement

Every image-generation prompt must request a text-free background and reserve the left 39% as a quiet field. Exact Chinese and Latin typography is overlaid only after the background passes `scripts/validate_cover.py`. A host without compositing support must return the text-free background plus the exact overlay specification; it must not claim that model-rendered title text is production-ready.

## Font selection

The SkillHub package contains no font binaries. Prefer a host-available Chinese serif or editorial display face with complete CJK coverage, paired with a compatible Latin display face. Preserve supplied English lockups such as `in vivo CAR-T`, `LNP`, `mRNA`, and `CAR-T` exactly.

When using `scripts/compose_cover.py`, pass both local font paths explicitly with `--font <chinese-font.ttf>` and `--latin-font <latin-font.ttf>`. Confirm that the user has the right to use the selected fonts. If suitable fonts or deterministic host editing are unavailable, return the text-free background plus the overlay specification instead of claiming a finished cover.

## Theme title profiles

Theme IDs begin at 1 and correspond to former themes 4-16. Use the source-specific quiet field when one is defined by the background; otherwise use the default title field.

| ID | Style | Text palette |
| --- | --- | --- |
| 1 | Clay diorama | terracotta + deep brown |
| 2 | Nature science | ice white + coral |
| 3 | Businessweek | black + clinical red |
| 4 | Monocle | forest green + brick red |
| 5 | Micro documentary | silver white + fluorescence green |
| 6 | Swiss poster | black + cobalt blue |
| 7 | Science archive | charcoal + oxide red |
| 8 | Pipeline map | deep navy + teal |
| 9 | Clinical evidence | navy + safety orange |
| 10 | Cell mechanism | cold white + RNA gold on deep navy |
| 11 | Medical congress | cold white + magenta |
| 12 | Molecular blueprint | ice white + node gold on Prussian blue |
| 13 | Bioprocess | deep teal + amber |
