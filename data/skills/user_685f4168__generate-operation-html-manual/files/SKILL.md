---
name: build-visual-html-manual
description: Create or revise polished Chinese or bilingual single-file HTML manuals, SOPs, implementation guides, operation handbooks, training guides, and solution documents with a fixed professional visual system. Use when an agent must turn source documents, notes, screenshots, or requirements into an easy-to-scan HTML deliverable with a cover, complete left navigation, cards, native HTML/CSS flowcharts, scenario playbooks, responsive screenshot placeholders, click-to-zoom images, print/PDF styling, and deterministic link/image QA.
---

# Build Visual HTML Manual

Create a self-contained, professional document rather than a generic webpage. Keep factual content specific to the user's materials while preserving the bundled visual language and QA discipline.

## Required resources

- Start from `assets/manual-template.html`; do not recreate the layout from memory.
- Read `references/design-system.md` before deciding the document structure or adding components.
- Run `scripts/validate_html.py` on every final HTML file.
- Use `scripts/new_manual.py` when creating a new manual; it copies the template, fills cover metadata, and creates the sibling image folder.

## Workflow

1. Inspect every user-provided source and the existing deliverable, if any.
2. Identify audience, operational goal, expected decisions, scenarios, prerequisites, and screenshot sequence.
3. Draft the information architecture before writing:
   - Put the implementation/category map first.
   - Explain each route with its own explicit steps and visual flow.
   - Expand each important scenario into trigger, inputs, procedure, settings, verification, failure handling, and output.
   - Put cross-scenario workflow wiring, acceptance, maintenance, and appendices after the scenario chapters.
4. Create the file with `new_manual.py` or copy the template manually when preserving an existing document.
5. Replace sample content with the user's content. Prefer visual components to dense tables or uninterrupted prose.
6. Add screenshots as `<figure class="shot">` blocks. Use relative paths beside the HTML and retain visible placeholders until image files exist.
7. Keep every screenshot keyboard-accessible and click-to-zoom through the template lightbox.
8. Build the navigation from the final section hierarchy. Every navigation target must exist exactly once.
9. Run validation, open the HTML in a browser, inspect desktop and narrow layouts, test image zoom, and test print preview.
10. Fix all reported errors and material visual defects before delivery.

## Content rules

- Lead each chapter with an outcome or decision, then show the steps.
- Use paragraphs for explanation, cards for parallel options, step cards for procedures, and flows for sequence or branching.
- Do not compress a requested scenario into one sentence. A usable scenario states who does what, in what order, with what input, using which settings, how success is checked, and what to do when it fails.
- Avoid large tables. Use a table only for exact repeated-field comparison; otherwise convert the relationship to cards, lanes, decision flows, or a timeline.
- Keep flow labels executable. Prefer `上传源文件 → 上传切片文件 → 建立关联 → 校验预览 → 发布` over abstract labels such as `资料处理 → 完成`.
- Do not fabricate UI labels, parameters, product behavior, or citations. Mark uncertain values as examples or verify them from primary sources when browsing is appropriate.
- Keep client names, product IDs, dataset IDs, tokens, URLs, and personal data out of reusable assets and screenshots unless the user explicitly requires them.

## Visual and interaction rules

- Preserve the navy/blue/cyan design tokens, white document canvas, sticky dark sidebar, generous section spacing, rounded cards, and restrained shadows.
- Use native HTML/CSS diagrams whenever the information can be expressed as nodes, arrows, lanes, cards, or branches. Do not depend on external diagram libraries.
- Keep all assets local or embedded. The final HTML must still work when opened with `file:///` and without internet access.
- Images must use `width: 100%`, bounded height, and `object-fit: contain`; never hardcode the screenshot's natural dimensions.
- Preserve responsive breakpoints and `@media print`. Do not hide document content on small screens.
- Preserve semantic headings, visible focus states, meaningful alt text, Escape-to-close, and Enter/Space image activation.

## Screenshot contract

Use stable ordered names such as `images/S01.png`, `images/S02.png`, or a descriptive subfolder. A standard block is:

```html
<figure class="shot">
  <div class="shot-head"><strong>S01 · 页面名称</strong><code>images/S01.png</code></div>
  <div class="shot-stage">
    <img class="shot-img" data-src="images/S01.png" alt="说明截图中需要观察的区域">
    <div class="shot-empty"><div class="slot">截图 S01</div><p>截图范围与需要隐藏的信息。</p></div>
  </div>
  <figcaption>操作结果、检查点或注意事项。</figcaption>
</figure>
```

When the file exists, JavaScript loads it and hides the placeholder. When it does not, the placeholder remains visible. Replacing a file with another aspect ratio must not require CSS changes.

## Verification command

```powershell
python "<skill-dir>\scripts\validate_html.py" "<output.html>"
```

Treat broken or duplicate navigation targets, missing local images without an intentional placeholder, missing alt text, absent responsive or print CSS, and broken lightbox structure as release blockers. After static validation, perform visual browser inspection; static checks do not prove layout quality.

## Delivery

Return the absolute clickable path to the HTML and, when useful, the image folder. Briefly report navigation-link count, missing targets, duplicate IDs, screenshot count, placeholder count, and visual QA status.
