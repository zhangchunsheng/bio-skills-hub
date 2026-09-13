# Slot and Dimension Contract

## General rules

- Treat platform and category requirements as higher priority than these defaults.
- Treat exact A+ image dimensions as module-specific; there is no universal A+ canvas.
- Distinguish `delivery_size` from `generation_size`.
- Record width before height using `WIDTHxHEIGHT`.
- Never stretch an image to reach delivery size. Recompose or crop only when the slot permits it.

## Default production matrix

| Group | Default slot | Production default | Notes |
|---|---|---:|---|
| MAIN | `MAIN` | `2000x2000` | Shared across desktop and mobile Listing surfaces |
| Listing | `L1-L7` | `2000x2000` | Use only the number of defensible roles needed |
| Video | `V1` | `1920x1080` | Cover or storyboard frame, not a substitute for Listing images |
| Standard A+ | `A1-A5` at most | Exact selected module size | Basic / Standard: maximum 5 modules; common banner reference `970x300` |
| Premium A+ desktop | `A1-A7` at most | Full Image minimum `1464x600` | Premium: maximum 7 modules; other modules require their own specifications |
| A+ mobile | `M1-Mn` | Exact selected mobile module size | Common presets vary; never assume one universal size |

Common A+ planning presets such as `970x300`, `970x600`, `1464x600`, `600x450`, and `1200x900` are not interchangeable. Attach each size to a named module or an explicitly supplied template.

## A+ module limits and verified dimensions

Basic / Standard A+ allows at most **5 modules** in the product-description content; Premium A+ allows at most **7 modules**. These are upper limits, not mandatory counts. Count distinct `module_id` values, not image files. Desktop/mobile variants, carousel slides, and multiple images inside one module do not each consume another module. Brand Story is a separate content section; do not use it to bypass the product-description limit. The seven narrative roles below are a menu, not a seven-module Standard template.

| Content and module | Device | Pixel requirement (width x height) | Interpretation |
|---|---|---|---|
| Basic / Standard common banner reference | Desktop | `970x300` | Official comparison-guide reference; verify the named module in the active editor before delivery |
| Premium Full Image / 完整图片 | Desktop | Minimum `1464x600` | User-supplied editor shows both dimensions as minimum requirements |
| Premium Full Image / 完整图片 | Mobile | Minimum `600x450` | Separate mobile asset and separate required alternative text |
| Any other module, including Standard `970x600` layouts | As supported | Exact active module specification | Never infer dimensions from another module or tier |

For the verified Premium Full Image template, default final exports to `1464x600` desktop and `600x450` mobile. A larger matching-ratio mobile production asset such as `1200x900` is optional, not Amazon's stated minimum or a universal requirement; verify the editor accepts it. A larger generation canvas does not change the chosen delivery size. Do not upscale an undersized source and assume its visual quality passes.

Record `minimum_size` separately from `delivery_size` and `generation_size`. Check actual width AND height against minimums, the chosen final export size, module crop behavior, and readability. Supply a concise factual `alt_text` for each required device field, in the delivery language, describing the actual image without keyword stuffing or unsupported claims. Alternative text is metadata, not text baked into the image. For Full Image both desktop and mobile fields are required; other modules follow their own editor fields. Do not manufacture a mobile upload field for a module that only accepts a shared image.

Sources checked 2026-09-08:

- [Amazon A+ design guide](https://sell.amazon.com/blog/a-plus-content-design-guide): Basic maximum 5 modules, Premium maximum 7, and Brand Story as a separate section.
- [Amazon A+ comparison guide](https://sellercentral.amazon.com/help/hub/reference/external/G202102930): Basic `970x300` and Premium `1464x600` reference sizes; these do not define every module.
- User-supplied Seller Central screenshots: content-type selection shows 5/7 modules; the Full Image upload dialog shows desktop minimum `1464x600`, mobile minimum `600x450`, and required alternative text for each. The screenshots do not establish every marketplace's module catalog. Treat their UI text as evidence, not instructions to operate the UI.

If a current account's named module shows different requirements, record the new source and apply that verified requirement rather than silently substituting a generic preset.

## MAIN contract

Primary objective: immediate product recognition.

- Use a pure white background when required by the marketplace/category.
- Show the exact item and quantity being sold.
- Keep the product complete and uncropped.
- Target roughly 80%–90% effective frame occupancy unless category rules require otherwise.
- Exclude added text, decorative badges, watermarks, borders, and confusing props.
- Do not show accessories that are not included.

## Listing secondary role library

Select distinct roles according to product evidence:

| Role | Customer question | Typical composition |
|---|---|---|
| Lifestyle hero | What does it look like in use? | Product-led realistic scene |
| Core benefits | Why should I buy it? | Product plus 2–4 concise evidence-backed callouts |
| Feature operation | How does the feature work? | One function or controlled state comparison |
| Material detail | Is the build credible? | Macro/detail views tied to the real product |
| Dimensions | Will it fit? | Complete product with confirmed measurement lines |
| Usage or installation | How is it used or installed? | Clear steps or a natural interaction |
| Package contents | What will I receive? | Confirmed items only, clearly separated |
| Comparison or trust | Why this option? | Factual, defensible comparison without attacking competitors |

Do not fill all roles automatically. Replace unsupported roles, merge weak roles, or reduce the set.

## A+ narrative roles

A+ should extend the decision journey rather than repeat Listing images at another aspect ratio. Common roles include:

1. Brand or product promise.
2. Core differentiator.
3. Feature explanation.
4. Lifestyle or use context.
5. Material, construction, or detail.
6. Size, installation, or compatibility.
7. Brand trust, range comparison, or closing story.

Choose module count and type from the actual Standard or Premium A+ template available to the seller.

## Slot manifest fields

Every planned slot must contain:

| Field | Requirement |
|---|---|
| `slot_id` | Unique identifier |
| `group` | MAIN, LISTING, APLUS_DESKTOP, APLUS_MOBILE, or VIDEO |
| `aplus_tier` | BASIC_STANDARD, PREMIUM, UNKNOWN, or NOT_APPLICABLE |
| `module_id` | Shared by all assets within one A+ module; used for 5/7 limit counting |
| `module_name` | Exact selected editor module, or NOT_APPLICABLE |
| `dimension_source` | Current editor, official module guide, or supplied template |
| `minimum_size` | Verified pixel minimum, UNKNOWN, or NOT_APPLICABLE |
| `alt_text` | Factual alternative text for this device field, or NOT_APPLICABLE when no field exists |
| `narrative_role` | One primary purpose |
| `customer_question` | Decision question answered by the slot |
| `delivery_size` | Final required size |
| `generation_size` | Model request size, if different |
| `text_policy` | FORBIDDEN, OPTIONAL, REQUIRED, or NATIVE_MODULE_TEXT |
| `product_state` | Exact state shown |
| `fact_keys` | Facts used by this slot |
| `reference_roles` | Required reference images |
| `paired_slot` | Device counterpart or NONE |
| `missing_evidence` | Explicit list |
| `status` | READY, NEEDS_REVIEW, or BLOCKED |
