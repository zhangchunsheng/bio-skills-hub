# Frequently Asked Questions (FAQ)

Ten questions real users ask. Each answer points at the actual fix, not a doc
wall to re-read. If a question is not here, check
[`references/troubleshooting.md`](troubleshooting.md) for runtime faults.

---

## Q1 · 字体隐形 / 加载慢 / 中文渲染奇怪

**Most common cause**: Google Fonts (`fonts.gstatic.com`) is blocked or slow on
the user's network, so the browser falls back to a generic font after a long
blank period.

**Fix**:
- The default `template.html` already ships a 4-mirror CDN chain and a
  `font-fallback` class. Open the file and check whether a yellow
  "字体加载超时" banner is visible at the top.
- For a permanent fix, see [`../designs/font-stack-fallback.md`](../designs/font-stack-fallback.md).
  Section 6 documents a `vendor/fonts/` local fallback for fully air-gapped
  networks.
- On Windows machines, do not declare `font-weight: 500` or `600` — Microsoft
  YaHei silently drops to Regular. Use 400 / 700 / 900 only.

---

## Q2 · 图表区域空白（ECharts / Mermaid）

**Most common cause**: The CDN mirror was blocked; the loader silently fell
through and the consumer code's `typeof echarts === 'undefined'` check passed,
so the chart div stayed empty.

**Fix**:
- Open DevTools Console. If you see `cdn:degraded` events or the yellow
  "ECharts 库未加载" banner, the loader gave up.
- The default `template.html` tries local `./vendor/` → cdnjs → jsDelivr →
  unpkg with Subresource Integrity (SRI) verification. Untrusted mirrors
  (BootCDN, Staticfile) have been completely removed. For air-gapped offline
  networks, place the `.min.js` files into a local `vendor/` folder next to your
  HTML presentation.
- For Mermaid, the first `mermaid.initialize()` call has a `startOnLoad: true`
  flag — if Mermaid loaded but did not render, the source likely had a syntax
  error. Check the browser console for "Syntax error in graph definition".

---

## Q3 · 双击图片放大没反应

**Most common cause**: The image is inside a slide that is not yet `active`, so
the lightbox initialization ran but the event listener was attached to a
`display: none` element. Or the image's parent has `pointer-events: none`.

**Fix**:
- Make sure you are on the slide where the image is visible. Overview mode
  (`O` key) thumbnails are not zoomable.
- The lightbox is wired by `initImageLightbox` near the end of `template.html`.
  Check that the script tag was not removed during your edits.
- If the parent is a card with custom `transform`, set `pointer-events: auto`
  on the `<img>`.

---

## Q4 · 翻页时上一张的动画残留

**Most common cause**: `.anim` / `.a1` / `.a2` keyframes are still running on a
slide that was set to `display: none`. They keep painting the layout off-screen,
which is harmless but visible in DevTools' Performance tab.

**Fix**:
- The default template has `animation: none !important;` on
  `.slide:not(.active) *`. If you removed this rule, add it back.
- For ECharts animations, the chart's `notMerge: true` flag in `setOption` can
  cause flicker between slides. Set it to `false` if you do not need the
  "data change" animation.

---

## Q5 · PPTX 转换后图片 / 矢量形状丢失

**Most common cause**: `extract-pptx.py` (Mode B) only extracts raster images
and a subset of vector shapes (rectangles, ellipses, lines, basic text). It does
not extract SmartArt, charts, or grouped shapes.

**Fix**:
- Open the .pptx in PowerPoint, right-click the missing element, "Save as
  Picture" (PNG), and drop the resulting image into the slide via
  `T3 (Inset)` or `T4 (Browser)` per
  [`screenshot-framing.md`](screenshot-framing.md).
- For embedded charts, see Q2 — they typically render as ECharts blocks in the
  HTML version, not as a 1:1 copy.

---

## Q6 · 离线 / 公司内网怎么用

Three levels of offline support, pick what matches your network:

1. **Read-only offline**: Disable JavaScript on the page. The static layout will
   still render because all CSS is inline. Animations and the controls bar will
   not work, but the slides are visible.
2. **Partly offline** (one blocked domain): The default `template.html` already
   tries 4 mirrors. If they all fail, edit the `CHAINS` map to put your
   internal mirror first.
3. **Fully air-gapped**: Use [`../designs/font-stack-fallback.md`](../designs/font-stack-fallback.md)
   §6 — vendorize the fonts into `vendor/fonts/`. For ECharts / Mermaid, copy
   the minified JS into `vendor/js/` and reference it as a relative path in
   the loader.

---

## Q7 · 风格选错了能不能中途换

**Yes, with one caveat**: only swap **before Phase 2.5 (Content Batch Filling)**.
After the slides are filled with copy in the wrong style, swapping means a full
re-render of every slide.

If you catch it early:
- Tell the agent: "Actually, let's switch to [new style slug]". The agent
  re-reads the new `design.md` and regenerates the wireframe.
- If the layouts differ, the wireframe is regenerated; if the layouts are
  shared, only the CSS tokens swap.

If you catch it late:
- Cheaper to re-generate from scratch than to hand-patch. The agent will do
  this in a few minutes.

---

## Q8 · 中文用 Outfit 显示很丑怎么办

**Most common cause**: The HTML did not include a Chinese family in the font
stack. Outfit only ships Latin glyphs, so the browser picks a default Chinese
font that does not match Outfit's metrics.

**Fix**:
- The body stack defined in
  [`../designs/font-stack-fallback.md`](../designs/font-stack-fallback.md) §2.2
  already chains `PingFang SC`, `Microsoft YaHei`, `Source Han Sans SC`,
  `Noto Sans SC` after `Plus Jakarta Sans`. Use that exact stack.
- Avoid giving headings the same `letter-spacing` as Latin display fonts. The
  `.font-fallback` class automatically strips `-0.02em` and tighter.

---

## Q9 · 怎么嵌入自己的 logo / 字体文件

**Logo**: drop the SVG / PNG into the slide as a regular `<img>` and use
`T2 (Float)` per [`image-treatments.md`](image-treatments.md). Do not wrap it
in `.frame-img` with a `figcaption` — that is the deprecated pattern from the
old `template.html`.

**Custom font**:
1. Drop the `.woff2` into a `vendor/fonts/` directory next to the HTML.
2. Add a `@font-face` block to the top of the `<style>` section, above all
   other styles, so it wins over the system fallback.
3. Append the family name to the `--font-display` / `--font-body` CSS variable.

For per-template customization, copy the template's `design.md` into your
local overrides file and edit there — do not edit the canonical one.

---

## Q10 · 怎么导出 PDF / 图片

**PDF**: open the HTML in Chrome, `Cmd + P`, choose "Save as PDF", and in
`More settings` set margins to "None" and enable "Background graphics". The
fixed 16:9 stage scales to the page width automatically.

**Image**: in Chrome, open DevTools, `Cmd + Shift + P`, type "screenshot",
choose "Capture node screenshot" for a single slide or "Capture full size
screenshot" for the entire deck. For a per-slide batch export, use a headless
tool like `puppeteer` with `page.goto(url)` + a wait of 500ms before
`page.screenshot({ clip: ... })`.

**Speaker view PDF**: print only the notes panel of the speaker view window,
not the slide panel.

