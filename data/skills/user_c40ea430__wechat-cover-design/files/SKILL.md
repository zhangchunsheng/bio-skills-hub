---
name: wechat-cover-design
description: Design stable WeChat Official Account covers for biopharma and biomedical articles. Use when the user asks for a 公众号封面、封面图、文章首图、cover image、cover prompt or banner art about drug discovery, delivery, clinical evidence, molecular design, CMC, biotech industry, or related science. Ask the user to choose direct-image-generation or prompt-only, then generate a text-free background, audit its left quiet field, and apply exact title typography only with deterministic layout or image editing.
license: MIT
metadata:
  author: rcrusoe88-bot
  version: 1.0.0
---

# WeChat Cover Design

Create one editorial WeChat cover from the article's actual claim. This skill is optimized for the biopharma workflow: mechanism explanation, delivery technology, clinical evidence, platform analysis, molecular design, industry landscape, and CMC/manufacturing.

## Execution rule

Before drafting the final answer, explicitly ask the user to choose an execution path. Do not infer the path from host capability.

| User selection | Required action |
| --- | --- |
| Direct image generation | Generate a text-free background, run `scripts/validate_cover.py --json`, then apply exact text with layout/editing or `scripts/compose_cover.py`. Only a returned JSON object with `"status": "PASS"` permits delivery. If layout/editing is unavailable, return the text-free background plus a deterministic overlay specification; do not claim it is a finished cover. |
| Prompt-only | Return one copy-ready English prompt for a text-free background plus a deterministic overlay specification. |

If the user has not selected a path, ask only which they want: direct image generation or prompt-only. Never claim an image was generated unless the host returned an image artifact.

## WorkBuddy runtime

- Prefer WorkBuddy's built-in image-generation tool for the direct-image-generation path. Do not request an external image API key or send the article, prompt, or generated assets to an independently configured image provider.
- Resolve every bundled path relative to this skill directory. Do not assume the user's workspace contains a clone of the source repository.
- Before running the Python compositor or image audit, verify that Python and Pillow are available. Do not install packages without the user's approval.
- If Pillow or local script execution is unavailable, use a deterministic host image editor when it can preserve the exact title and coordinates. Otherwise return the text-free background and overlay specification as an explicit handoff; do not present it as a finished cover.

## Input and visual brief

Extract only what is needed to make a cover specific to the article:

| Field | Requirement |
| --- | --- |
| Article thesis | One sentence stating the actual claim. |
| Reader takeaway | What a reader should grasp in three seconds. |
| Core object chain | Focal scientific object, supporting object, and outcome. |
| Evidence | At most two meaningful comparisons, measures, or stages. |
| Title inventory | Exact optional title prefix, one or two exact main-title lines, optional subtitle, and any text that must remain verbatim. A supplied title prefix is part of the title and cannot be omitted or demoted. |
| Constraints | Brand colors, exclusions, or required theme. |

If the article does not provide enough information for a factual visual, ask up to three focused questions. Do not invent experimental results, clinical claims, company facts, or medical efficacy.

## Select one of the 13 themes

Read `references/theme_registry.md`, `references/typography_layout.md`, and the matching section in `references/theme_specs.md` before composing the prompt. Theme IDs are fixed at 1-13; do not refer to or restore any retired themes.

| Article signal | Theme |
| --- | --- |
| Biological mechanism or delivery chain | Theme 1: biomedical clay cutaway |
| Major scientific breakthrough or platform launch | Theme 2: Nature scientific concept |
| Valuation, transactions, or evidence mismatch | Theme 3: Businessweek metaphor |
| Industry ecosystem or R&D-to-clinic panorama | Theme 4: Monocle industry observation |
| Microscopic binding, nanodelivery, tissue microenvironment | Theme 5: microscopic documentary |
| One core proposition or binary relationship | Theme 6: Swiss poster |
| Patents, technical history, engineering barriers | Theme 7: science archive |
| Pipelines, competing routes, milestones, company landscape | Theme 8: pipeline map |
| Clinical evidence, efficacy/safety, cohorts, dose escalation | Theme 9: clinical evidence brief |
| Cellular mechanism, delivery chain, signaling pathway | Theme 10: Cell mechanism atlas |
| Annual review, congress recap, translational milestone | Theme 11: medical congress key visual |
| Molecular design, conjugation, formulation, structural IP | Theme 12: molecular blueprint |
| CMC, scale-up, TFF, purification, QC, CDMO | Theme 13: bioprocess engineering |

Honor an explicit theme choice unless it contradicts a factual constraint. When two themes are genuinely equally suitable, present two one-sentence options and ask the user to choose.

## Fixed title composition

All covers use a `1584x672` canvas (about 2.35:1). The title field is always on the left: `x=76..620`, `y=88..585` (roughly the left 39% of the canvas). Keep the right 60% for the focal biomedical scene.

- Use a natural quiet field, not a translucent card, underline, divider, shadow, or gradient panel.
- Reserve the left field before generating the background. Keep it low-detail, clear of focal objects, high-contrast edges, labels, and data marks.
- Use the selected theme's palette. Prefer a host-available Chinese serif or editorial display face and a compatible Latin display face. When using `scripts/compose_cover.py`, the user must provide local font paths explicitly.
- Keep the hierarchy to eyebrow, main title, optional subtitle, and one short footer at most.
- Use the fixed title group: one-line eyebrow; optional title prefix; one or two semantic main-title lines; up to two subtitle lines; one-line footer. A title prefix such as `Ab-mRNA-LNP` stays in the title group, never in the eyebrow or footer.
- Main title default is 62 px, with a 52 px minimum. The compositor measures each line against the 500 px effective width and rejects overflow; it never moves title text toward the scientific subject.
- If the source artwork has no usable left quiet field, regenerate the background. Do not move the title toward the scientific subject.

### Direct image-generation path

Use this path only after the user selects direct image generation. Write a text-free image prompt that explicitly reserves the fixed left title field. Generate the artwork with the host's native image tool. If the provider only supports `16:9`, generate at `16:9`, center-crop to `2.35:1`, then audit the cropped result. Run `scripts/validate_cover.py --input <background.png> --theme <1-13> --json` before any type is applied. A failed audit means regenerate the background. The audit rejects high-contrast long lines, charts, process paths, labels, or any large structured mark in the title field. Do not describe the image as audited unless the command returned `"status": "PASS"`; phrases such as “审计一次过” are not validation evidence. Only then render the supplied exact title in the field using host layout/editing or `scripts/compose_cover.py`.

### Handoff path

Use this path only after the user selects prompt-only. Provide one self-contained English prompt that contains all of the following:

1. Target dimensions: `1584x672` or `2.35:1`.
2. The selected theme's visual scene, palette, materials, focal object, and right-side placement.
3. A left-side low-detail title field occupying 39% of the width.
4. An explicit `text-free background` instruction, with `no readable text, labels, logo, or watermark anywhere in the generated image`.
5. A negative prompt preventing objects, high-contrast edges, labels, and data marks from entering the title field.

Then append a separate `Overlay specification` containing the exact title, subtitle, coordinates, fonts, and colors. Never ask the image model to render these strings.

## Deliverables

### When an image was generated

Return:

1. The image artifact.
2. Theme and one-sentence rationale.
3. A concise Chinese production note: title treatment, crop safety, and any text-rendering limitation.
4. The validation result.
5. The raw JSON result from `scripts/validate_cover.py --json`.

### When a handoff is required

Return:

1. Theme and one-sentence rationale.
2. A complete, copy-ready English prompt for a text-free background.
3. `Overlay specification`: title, subtitle, `x=76..620, y=88..585`, Chinese font, English font, palette, and left alignment.
4. A concise Chinese production note and the validation result.

## Prompt package format

Use this package structure for both paths. It is also the required input to `scripts/validate_prompt.py --all`; replace every quoted value with article-specific content.

```text
Cover plan:
Theme: Theme 6 - Swiss poster
Generation path: user-confirmed direct-image-generation / prompt-only

Alignment Record:
Article thesis: "..."
Reader takeaway: "..."
Content class: mechanism / evidence / transaction / industry_landscape / other registered class
Theme rationale: "..."
Visual metaphor: "..."
Element provenance: "focal object: article section ...; supporting object: reader takeaway ..."
Forbidden substitutions: "article-irrelevant visual shortcuts only; do not repeat image-quality negative terms"

English image prompt:
Create a text-free 16:9 or 1584x672 (2.35:1) WeChat cover in [selected theme] style. Place [focal scientific scene] in the right 60% of the canvas. Reserve left x=4.8%-39.1%, y=13.1%-87.1% as a low-detail, theme-native title field. Do not render readable text, labels, logos, or watermarks anywhere in the image.
Text-rendering strategy: audit the background, then overlay exact supplied text with deterministic layout.
Negative prompt: watermark, logo, readable text, gibberish, crowded composition, focal objects, high-contrast edges, labels, or data marks in the title field.

Chinese production note:
...
```

## Validation

Before delivery, confirm that the final prompt has no unresolved placeholders, states the 2.35:1 format, includes a negative prompt, names the theme's visual language, and preserves the left title field.

- Run `scripts/validate_prompt.py --all` for every text-free background prompt.
- Run `scripts/validate_cover.py --input <background.png> --theme <1-13> --json` after generation and before title overlay. If it fails, regenerate the background. There is no bypass flag.
- If scripts cannot run, apply the equivalent checklist manually and state that fact.

## References

- `references/theme_registry.md`: theme names and article-signal mapping.
- `references/theme_specs.md`: detailed visual prompt skeletons.
- `references/typography_layout.md`: fixed coordinates, palette, and font-selection rules.
- `references/title_overlay_policy.md`: native-image and prompt-only title rules.
- `scripts/compose_cover.py`: deterministic title compositor.
- `scripts/validate_cover.py`: image-level quiet-field and contrast quality gate.
- `scripts/validate_prompt.py`: prompt validator.
