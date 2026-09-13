# Troubleshooting (排错指南)

30-second localization for the four most common runtime faults. Each section
follows the same shape: symptom, quick check, fix, fallback. If a fault is not
here, see [`faq.md`](faq.md) for design-time questions.

The P0 reliability runtime in `template.html` already wires a yellow banner to
every fault below. If you can see the banner, read its `.degrade-reason` first -
it usually names the failing subsystem.

---

## 1. White Page / Slides Not Visible

Symptom: Page loads but the entire stage is blank or shows the body
background only.

Quick check:

```js
// Paste in DevTools console
document.querySelectorAll('.slide').length
document.querySelector('.slide.active')
getComputedStyle(document.querySelector('.deck-stage')).transform
```

- If `slides.length === 0`: the agent forgot to drop slide markup in. Re-run
  Phase 2.
- If `slides.length > 0` but `.slide.active` is `null`: the `currentSlide`
  variable is out of bounds. Reload the page; the URL hash handler at the
  bottom of `template.html` will reset it.
- If `transform` is `none` or empty: the `updateScale()` script did not run.
  Check for a JS syntax error in your custom block.

Fallback: press `R` (planned shortcut, currently `Cmd + R` reload) to
re-init the stage.

---

## 2. Fonts Invisible / Layout Shift on Load

Symptom: Headings are missing on first paint, then pop in. Cards move up
or down by 5-10px.

Quick check:

```js
document.fonts.status           // 'loaded' | 'unloaded' | 'loading' | 'error'
document.fonts.size             // number of font faces
```

If `status === 'error'`, the network blocked the CDN. The yellow banner should
already be visible. If it is not, your `template.html` was edited and the P0
runtime block was removed - re-apply it from
[`../designs/font-stack-fallback.md`](../designs/font-stack-fallback.md) section 5.

Fix:

- Add `&display=swap` to the Google Fonts URL if missing.
- Make sure the body stack chains a Chinese family (see Q8 in FAQ).
- For layout shift, declare `min-height` on the slide title block so the swap
  does not move surrounding cards.

Fallback: manually add the `.font-fallback` class to `<html>` in DevTools
to see what the page looks like in fallback mode.

---

## 3. Chart Area Blank (ECharts / Mermaid)

Symptom: Card with `.echarts` or `.mermaid` class is sized correctly but
empty.

Quick check:

```js
typeof echarts                  // 'undefined' if CDN failed
typeof mermaid                  // same
document.querySelectorAll('.echart-box, .echarts').length
document.querySelector('.echarts').clientWidth   // 0 means parent has 0 width
```

Fix:

- If `typeof echarts === 'undefined'`: the loader gave up. Re-trigger by
  calling `initECharts()` from the console. If that still fails, vendorize the
  library (see FAQ Q6).
- If `clientWidth === 0`: the parent container is hidden. ECharts needs a
  non-zero width to initialize. Fix the parent layout first.
- If Mermaid shows "Syntax error": paste the `data-source` / `.mermaid` text
  into [mermaid.live](https://mermaid.live) to find the broken arrow.

Fallback: replace the chart card with a styled table; the design system
already supports this via `.data-table`.

---

## 4. Keyboard Shortcuts Not Working

Symptom: Pressing arrow keys, `F`, `O`, or `S` does nothing.

Quick check:

```js
document.querySelector('.deck-overview')   // null if overview HTML missing
document.querySelector('.controls-bar')    // null if bar missing
```

Fix:

- The keydown handler in `template.html` is global. If shortcuts are dead,
  the entire `<script>` block at the bottom was probably removed. Re-apply
  from the canonical template.
- Overview (`O`) and fullscreen (`F`) need focus on the page. Click anywhere
  on the page first to give the body focus.
- The `F` key is intentionally ignored when `Ctrl` or `Cmd` is held, so
  browser shortcuts (Cmd+F find) still work.

Fallback: use the bottom controls bar buttons. They are wired to the same
functions and never depend on keyboard events.

---

## 5. Lightbox (Double-Click Image Zoom) Broken

Symptom: Double-clicking a slide image does not open the lightbox.

Quick check:

```js
document.getElementById('imgLightbox')   // null if HTML missing
```

Fix:

- The lightbox is initialized by `initImageLightbox()` near the end of
  `template.html`. If `imgLightbox` is null, the wrapper HTML was removed.
- Make sure the image has a `src` (not `data-src` for lazy load). Lazy loaders
  may not trigger the dblclick listener until the image is in viewport.

Fallback: see the `<a href="..." target="_blank">` wrapper pattern. Wrap
the image in an anchor and the browser will open it in a new tab on click.

---

## 6. Performance: Laggy Slide Switching

Symptom: Pressing an arrow key takes 200ms+ before the next slide appears.

Quick check (Chrome DevTools -> Performance):

- Open the Performance panel, click Record, press an arrow key, stop.
- Look for long "Recalculate Style" or "Layout" tasks.

Fix:

- `.anim` keyframes can be expensive on slides with many cards. The default
  template reduces them to `transform` only; if you added custom `width` /
  `height` animations, convert to `transform`.
- ECharts animations: pass `{ animation: false }` to the chart's `setOption`
  call. Mermaid: `mermaid.initialize({ startOnLoad: false })` and call
  `mermaid.render()` manually after the slide is shown.
- For decks with 20+ slides, consider replacing all `<img>` with WebP and
  using `loading="lazy"`.

Fallback: switch to the Swiss style, which is the most performant template
in the pack (no glassmorphism, no blur, no animation physics).

---

## Reporting a Bug

If none of the above matches, capture the following and send it to the
maintainer:

1. URL or local file path of the generated HTML.
2. The exact text of the yellow `.degrade-banner` (if visible).
3. Output of the relevant Quick check snippet from this file.
4. The first 5 lines of DevTools -> Console.
5. Output of `node scripts/diagnose-deck.mjs <file>.html` (planned, see
   module plan P2 module 2).
