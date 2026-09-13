/**
 * <deck-stage> — reusable web component for HTML decks.
 *
 * Handles:
 *  (a) speaker notes — reads <script type="application/json" id="speaker-notes">
 *      and posts {slideIndexChanged: N} to the parent window on nav.
 *  (b) keyboard navigation — ←/→, PgUp/PgDn, Space, Home/End, number keys.
 *      Elements marked with data-fragment are revealed one at a time before
 *      advancing to the next slide, like a native presentation clicker.
 *  (c) press R to reset to slide 0 (with a tasteful keyboard hint).
 *  (d) bottom-center overlay showing slide count + hints, fades out on idle.
 *  (e) auto-scaling — inner canvas is a fixed design size (default 1920×1080)
 *      scaled with `transform: scale()` to fit the viewport, letterboxed.
 *      Set the `noscale` attribute to render at authored size (1:1) — the
 *      PPTX exporter sets this so its DOM capture sees unscaled geometry.
*  (f) print — `@media print` lays every slide out as its own page at the
*      design size, so the browser's Print → Save as PDF produces a clean
*      one-page-per-slide PDF with no extra setup.
 *  (g) speaker view — opens a separate window with a `speaker.html` companion
 *      file and keeps it in sync via a `BroadcastChannel('deck-speaker-sync')`.
 *      Press `S` to open the console; arrow keys inside the console navigate
 *      the main deck in real time. The console shows elapsed time, current
 *      slide title, next slide title, speaker notes, and a live next-slide
 *      preview iframe. Notes are read from the same `<script
 *      type="application/json" id="speaker-notes">` array (1 entry per slide,
 *      empty string when none), with a fallback to `<aside class="notes">`
 *      inside each slide for hosts that prefer inline HTML notes.
*
* Slides are HIDDEN, not unmounted. Non-active slides stay in the DOM with
 * `visibility: hidden` + `opacity: 0`, so their state (videos, iframes,
 * form inputs, React trees) is preserved across navigation.
 *
 * Lifecycle event — the component dispatches a `slidechange` CustomEvent on
 * itself whenever the active slide changes (including the initial mount).
 * The event bubbles and composes out of shadow DOM, so you can listen on
 * the <deck-stage> element or on document:
 *
 *   document.querySelector('deck-stage').addEventListener('slidechange', (e) => {
 *     e.detail.index         // new 0-based index
 *     e.detail.previousIndex // previous index, or -1 on init
 *     e.detail.total         // total slide count
 *     e.detail.slide         // the new active slide element
 *     e.detail.previousSlide // the prior slide element, or null on init
 *     e.detail.reason        // 'init' | 'keyboard' | 'click' | 'tap' | 'api'
 *   });
 *
 * Persistence: none at the deck level. The host app keeps the current slide
 * in its own URL (?slide=) and re-delivers it via location.hash on load, so a
 * bare load with no hash always starts at slide 1.
 *
 * Usage:
 *   <deck-stage width="1920" height="1080">
 *     <section data-label="Title">...</section>
 *     <section data-label="Agenda">...</section>
 *   </deck-stage>
 *
 * Slides are the direct element children of <deck-stage>. Each slide is
 * automatically tagged with:
 *   - data-screen-label="NN Label"   (1-indexed, for comment flow)
 *   - data-om-validate="no_overflowing_text,no_overlapping_text,slide_sized_text"
 */

(() => {
  const DESIGN_W_DEFAULT = 1920;
  const DESIGN_H_DEFAULT = 1080;
  const OVERLAY_HIDE_MS = 1800;
  const VALIDATE_ATTR = 'no_overflowing_text,no_overlapping_text,slide_sized_text';

  const pad2 = (n) => String(n).padStart(2, '0');

  const SPEAKER_CHANNEL_NAME = 'deck-speaker-sync';
  const FRAGMENT_HIDDEN_ATTR = 'data-deck-fragment-hidden';
  const FRAGMENT_ENTER_ATTR = 'data-deck-fragment-enter';

  const stylesheet = `
    :host {
      position: fixed;
      inset: 0;
      display: block;
      background: #000;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
      overflow: hidden;
    }

    .stage {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .canvas {
      position: relative;
      transform-origin: center center;
      flex-shrink: 0;
      background: #fff;
      will-change: transform;
    }

    /* Slides live in light DOM (via <slot>) so authored CSS still applies.
       We absolutely position each slotted child to stack them. */
    ::slotted(*) {
      position: absolute !important;
      inset: 0 !important;
      width: 100% !important;
      height: 100% !important;
      box-sizing: border-box !important;
      overflow: hidden;
      opacity: 0;
      pointer-events: none;
      visibility: hidden;
    }
    ::slotted([data-deck-active]) {
      opacity: 1;
      pointer-events: auto;
      visibility: visible;
    }

    /* Tap zones for mobile — back/forward thirds like Stories.
       Transparent, no visible UI, don't block the overlay. */
    .tapzones {
      position: fixed;
      inset: 0;
      display: flex;
      z-index: 2147482000;
      pointer-events: none;
    }
    .tapzone {
      flex: 1;
      pointer-events: auto;
      -webkit-tap-highlight-color: transparent;
    }
    /* Only activate tap zones on coarse pointers (touch devices). */
    @media (hover: hover) and (pointer: fine) {
      .tapzones { display: none; }
    }

    .overlay {
      position: fixed;
      left: 50%;
      bottom: 22px;
      transform: translate(-50%, 6px) scale(0.92);
      filter: blur(6px);
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      background: #000;
      color: #fff;
      border-radius: 999px;
      font-size: 14px;
      font-feature-settings: "tnum" 1;
      letter-spacing: 0.01em;
      opacity: 0;
      pointer-events: none;
      transition: opacity 260ms ease, transform 260ms cubic-bezier(.2,.8,.2,1), filter 260ms ease;
      transform-origin: center bottom;
      z-index: 2147483000;
      user-select: none;
    }
    .overlay[data-visible] {
      opacity: 1;
      pointer-events: auto;
      transform: translate(-50%, 0) scale(1);
      filter: blur(0);
    }

    .btn {
      appearance: none;
      -webkit-appearance: none;
      background: transparent;
      border: 0;
      margin: 0;
      padding: 0;
      color: inherit;
      font: inherit;
      cursor: default;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      height: 32px;
      min-width: 32px;
      border-radius: 999px;
      color: rgba(255,255,255,0.72);
      transition: background 140ms ease, color 140ms ease;
      -webkit-tap-highlight-color: transparent;
    }
    .btn:hover { background: rgba(255,255,255,0.12); color: #fff; }
    .btn:active { background: rgba(255,255,255,0.18); }
    .btn:focus { outline: none; }
    .btn:focus-visible { outline: none; }
    .btn::-moz-focus-inner { border: 0; }
    .btn svg { width: 16px; height: 16px; display: block; }
    .btn.reset {
      font-size: 13px;
      font-weight: 500;
      letter-spacing: 0.02em;
      padding: 0 10px 0 12px;
      gap: 6px;
      color: rgba(255,255,255,0.72);
    }
    .btn.reset .kbd {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 18px;
      height: 18px;
      padding: 0 4px;
      font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
      font-size: 11px;
      line-height: 1;
      color: rgba(255,255,255,0.88);
      background: rgba(255,255,255,0.12);
      border-radius: 4px;
    }

    .count {
      font-variant-numeric: tabular-nums;
      color: #fff;
      font-weight: 500;
      padding: 0 8px;
      min-width: 46px;
      text-align: center;
      font-size: 14px;
    }
    .count .sep { color: rgba(255,255,255,0.45); margin: 0 3px; font-weight: 400; }
    .count .total { color: rgba(255,255,255,0.55); }

    .divider {
      width: 1px;
      height: 16px;
      background: rgba(255,255,255,0.18);
      margin: 0 3px;
    }

    /* ── Print: one page per slide, no chrome ────────────────────────────
       The screen layout stacks every slide at inset:0 inside a scaled
       canvas; for print we want them in document flow at the authored
       design size so the browser paginates one slide per sheet. The
       @page size is set from the width/height attributes via the inline
       <style id="deck-stage-print-page"> that connectedCallback injects
       into <head> (the @page at-rule has no effect inside shadow DOM). */
    @media print {
      :host {
        position: static;
        inset: auto;
        background: none;
        overflow: visible;
        color: inherit;
      }
      .stage { position: static; display: block; }
      .canvas {
        transform: none !important;
        width: auto !important;
        height: auto !important;
        background: none;
        will-change: auto;
      }
      ::slotted(*) {
        position: relative !important;
        inset: auto !important;
        width: var(--deck-design-w) !important;
        height: var(--deck-design-h) !important;
        box-sizing: border-box !important;
        opacity: 1 !important;
        visibility: visible !important;
        pointer-events: auto;
        break-after: page;
        page-break-after: always;
        break-inside: avoid;
        overflow: hidden;
      }
      ::slotted(*:last-child) {
        break-after: auto;
        page-break-after: auto;
      }
      .overlay, .tapzones { display: none !important; }
    }
  `;

  class DeckStage extends HTMLElement {
    static get observedAttributes() { return ['width', 'height', 'noscale']; }

    constructor() {
      super();
      this._root = this.attachShadow({ mode: 'open' });
      this._index = 0;
      this._slides = [];
      this._notes = [];
      this._fragmentSteps = new WeakMap();
      this._hideTimer = null;
      this._mouseIdleTimer = null;

      this._onKey = this._onKey.bind(this);
      this._onResize = this._onResize.bind(this);
      this._onSlotChange = this._onSlotChange.bind(this);
      this._onMouseMove = this._onMouseMove.bind(this);
      this._onTapBack = this._onTapBack.bind(this);
      this._onTapForward = this._onTapForward.bind(this);
    }

    get designWidth() {
      return parseInt(this.getAttribute('width'), 10) || DESIGN_W_DEFAULT;
    }
    get designHeight() {
      return parseInt(this.getAttribute('height'), 10) || DESIGN_H_DEFAULT;
    }

    connectedCallback() {
      this._render();
      this._ensureFragmentStyles();
      this._loadNotes();
      this._syncPrintPageRule();
      this._initImageLightbox();
      window.addEventListener('keydown', this._onKey);
      window.addEventListener('resize', this._onResize);
      window.addEventListener('mousemove', this._onMouseMove, { passive: true });
      // Initial collection + layout happens via slotchange, which fires on mount.
    }

    disconnectedCallback() {
      window.removeEventListener('keydown', this._onKey);
      window.removeEventListener('resize', this._onResize);
      window.removeEventListener('mousemove', this._onMouseMove);
      if (this._hideTimer) clearTimeout(this._hideTimer);
      if (this._mouseIdleTimer) clearTimeout(this._mouseIdleTimer);
    }

    attributeChangedCallback() {
      if (this._canvas) {
        this._canvas.style.width = this.designWidth + 'px';
        this._canvas.style.height = this.designHeight + 'px';
        this._canvas.style.setProperty('--deck-design-w', this.designWidth + 'px');
        this._canvas.style.setProperty('--deck-design-h', this.designHeight + 'px');
        this._fit();
        this._syncPrintPageRule();
      }
    }

    _render() {
      const style = document.createElement('style');
      style.textContent = stylesheet;

      const stage = document.createElement('div');
      stage.className = 'stage';

      const canvas = document.createElement('div');
      canvas.className = 'canvas';
      canvas.style.width = this.designWidth + 'px';
      canvas.style.height = this.designHeight + 'px';
      canvas.style.setProperty('--deck-design-w', this.designWidth + 'px');
      canvas.style.setProperty('--deck-design-h', this.designHeight + 'px');

      const slot = document.createElement('slot');
      slot.addEventListener('slotchange', this._onSlotChange);
      canvas.appendChild(slot);
      stage.appendChild(canvas);

      // Tap zones (mobile): left third = back, right third = forward.
      const tapzones = document.createElement('div');
      tapzones.className = 'tapzones export-hidden';
      tapzones.setAttribute('aria-hidden', 'true');
      tapzones.setAttribute('data-noncommentable', '');
      const tzBack = document.createElement('div');
      tzBack.className = 'tapzone tapzone--back';
      const tzMid = document.createElement('div');
      tzMid.className = 'tapzone tapzone--mid';
      tzMid.style.pointerEvents = 'none';
      const tzFwd = document.createElement('div');
      tzFwd.className = 'tapzone tapzone--fwd';
      tzBack.addEventListener('click', this._onTapBack);
      tzFwd.addEventListener('click', this._onTapForward);
      tapzones.append(tzBack, tzMid, tzFwd);

      // Overlay: compact, solid black, with clickable controls (上一页/下一页/全览/全屏).
      const overlay = document.createElement('div');
      overlay.className = 'overlay export-hidden';
      overlay.setAttribute('role', 'toolbar');
      overlay.setAttribute('aria-label', 'Deck controls');
      overlay.setAttribute('data-noncommentable', '');
      overlay.innerHTML = `
        <button class="btn prev" type="button" aria-label="Previous slide" title="Previous (←)">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 3L5 8l5 5"/></svg>
        </button>
        <span class="count" aria-live="polite"><span class="current">1</span><span class="sep">/</span><span class="total">1</span></span>
        <span class="fragment-count" aria-live="polite" hidden></span>
        <button class="btn next" type="button" aria-label="Next slide" title="Next (→)">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3l5 5-5 5"/></svg>
        </button>
        <span class="divider"></span>
        <button class="btn overview" type="button" aria-label="Overview gallery" title="Overview (O)">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="2" width="5" height="5"/><rect x="9" y="2" width="5" height="5"/><rect x="9" y="9" width="5" height="5"/><rect x="2" y="9" width="5" height="5"/></svg>
        </button>
        <button class="btn fs" type="button" aria-label="Fullscreen" title="Fullscreen (F)">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 5V2h3m6 0h3v3m0 6v3h-3M5 14H2v-3"/></svg>
        </button>
        <span class="divider"></span>
        <button class="btn reset" type="button" aria-label="Reset to first slide" title="Reset (R)">Reset<span class="kbd">R</span></button>
      `;

      overlay.querySelector('.prev').addEventListener('click', () => this._retreat('click'));
      overlay.querySelector('.next').addEventListener('click', () => this._advance('click'));
      overlay.querySelector('.overview').addEventListener('click', () => this._toggleOverview());
      overlay.querySelector('.fs').addEventListener('click', () => this._toggleFs());
      overlay.querySelector('.reset').addEventListener('click', () => this._go(0, 'click'));

      this._root.append(style, stage, tapzones, overlay);
      this._canvas = canvas;
      this._slot = slot;
      this._overlay = overlay;
      this._countEl = overlay.querySelector('.current');
      this._totalEl = overlay.querySelector('.total');
      this._fragmentCountEl = overlay.querySelector('.fragment-count');
    }

    _ensureFragmentStyles() {
      const id = 'deck-stage-fragment-styles';
      if (document.getElementById(id)) return;
      const tag = document.createElement('style');
      tag.id = id;
      tag.textContent = `
        [${FRAGMENT_HIDDEN_ATTR}] { opacity: 0 !important; visibility: hidden !important; pointer-events: none !important; }
        [${FRAGMENT_ENTER_ATTR}] { animation: deck-stage-fragment-fade .32s ease-out both; }
        [${FRAGMENT_ENTER_ATTR}][data-fragment-effect="fade-up"] { animation-name: deck-stage-fragment-fade-up; }
        [${FRAGMENT_ENTER_ATTR}][data-fragment-effect="scale"] { animation-name: deck-stage-fragment-scale; }
        [${FRAGMENT_ENTER_ATTR}][data-fragment-effect="wipe"] { animation-name: deck-stage-fragment-wipe; transform-origin: left center; }
        @keyframes deck-stage-fragment-fade { from { opacity: 0; } to { opacity: 1; } }
        @keyframes deck-stage-fragment-fade-up { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes deck-stage-fragment-scale { from { opacity: 0; transform: scale(.94); } to { opacity: 1; transform: scale(1); } }
        @keyframes deck-stage-fragment-wipe { from { opacity: 0; clip-path: inset(0 100% 0 0); } to { opacity: 1; clip-path: inset(0 0 0 0); } }
        @media (prefers-reduced-motion: reduce) { [${FRAGMENT_ENTER_ATTR}] { animation: none !important; } }
        .deck-overview { position: fixed; inset: 0; z-index: 2147483000; display: none; flex-direction: column; gap: 28px; padding: clamp(28px, 5vw, 76px); overflow: auto; color: #eef4ff; background: rgba(4, 10, 24, .96); font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; backdrop-filter: blur(24px); }
        .deck-overview.active { display: flex; }
        .overview-header { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding-bottom: 22px; border-bottom: 1px solid rgba(174, 198, 255, .2); }
        .overview-title { display: flex; align-items: baseline; gap: 18px; font-size: clamp(23px, 2vw, 34px); font-weight: 800; letter-spacing: -.03em; }
        .overview-hint { color: #9fb1d7; font-size: 14px; font-weight: 600; letter-spacing: 0; }
        .overview-close-btn { padding: 11px 16px; border: 1px solid rgba(174, 198, 255, .3); border-radius: 10px; color: #eef4ff; background: rgba(104, 129, 194, .16); cursor: pointer; font: inherit; font-size: 15px; font-weight: 700; }
        .overview-close-btn:hover, .overview-close-btn:focus-visible { background: rgba(104, 129, 194, .34); outline: 2px solid #76d9ff; outline-offset: 2px; }
        .overview-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(235px, 1fr)); gap: 18px; align-content: start; }
        .overview-card { position: relative; min-height: 170px; padding: 27px 24px 22px; overflow: hidden; border: 1px solid rgba(174, 198, 255, .2); border-radius: 18px; color: #eff5ff; background: linear-gradient(145deg, rgba(38, 59, 112, .58), rgba(13, 23, 49, .9)); cursor: pointer; box-shadow: inset 0 1px rgba(255,255,255,.08); transition: transform .18s ease, border-color .18s ease, background .18s ease; }
        .overview-card::after { content: ""; position: absolute; width: 170px; height: 170px; right: -70px; bottom: -92px; border-radius: 50%; background: radial-gradient(circle, rgba(82, 221, 255, .2), transparent 66%); pointer-events: none; }
        .overview-card:hover, .overview-card:focus-visible, .overview-card.current { transform: translateY(-4px); border-color: #61dfff; background: linear-gradient(145deg, rgba(50, 83, 148, .8), rgba(15, 29, 65, .96)); outline: none; }
        .overview-card-badge { display: inline-grid; place-items: center; width: 34px; height: 26px; margin-bottom: 20px; border-radius: 7px; color: #071222; background: #61dfff; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; font-weight: 900; }
        .overview-card-title { position: relative; z-index: 1; font-size: 22px; font-weight: 800; line-height: 1.22; letter-spacing: -.025em; }
        .overview-card-desc { position: relative; z-index: 1; margin-top: 10px; color: #acbddf; font-size: 14px; line-height: 1.5; }
        @media (max-width: 640px) { .deck-overview { padding: 22px; } .overview-header { align-items: flex-start; } .overview-title { flex-direction: column; gap: 6px; } .overview-grid { grid-template-columns: 1fr; } }
      `;
      document.head.appendChild(tag);
    }

    /** @page must live in the document stylesheet — it's a no-op inside
     *  shadow DOM. Inject/update a single <head> style tag so the print
     *  sheet matches the design size and Save-as-PDF yields one slide per
     *  page with no margins. */
    _syncPrintPageRule() {
      const id = 'deck-stage-print-page';
      let tag = document.getElementById(id);
      if (!tag) {
        tag = document.createElement('style');
        tag.id = id;
        document.head.appendChild(tag);
      }
      tag.textContent =
        '@page { size: ' + this.designWidth + 'px ' + this.designHeight + 'px; margin: 0; } ' +
        '@media print { html, body { margin: 0 !important; padding: 0 !important; background: none !important; overflow: visible !important; height: auto !important; } ' +
        '* { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }';
    }

    _onSlotChange() {
      this._collectSlides();
      this._restoreIndex();
      this._applyIndex({ showOverlay: false, broadcast: true, reason: 'init' });
      this._fit();
    }

    _collectSlides() {
      const assigned = this._slot.assignedElements({ flatten: true });
      this._slides = assigned.filter((el) => {
        // Skip template/style/script nodes even if someone slots them.
        const tag = el.tagName;
        return tag !== 'TEMPLATE' && tag !== 'SCRIPT' && tag !== 'STYLE';
      });

      this._slides.forEach((slide, i) => {
        const n = i + 1;
        // Determine a label for comment flow: prefer explicit data-label,
        // then an existing data-screen-label, then first heading, else "Slide".
        let label = slide.getAttribute('data-label');
        if (!label) {
          const existing = slide.getAttribute('data-screen-label');
          if (existing) {
            // Strip any leading number the author may have included.
            label = existing.replace(/^\s*\d+\s*/, '').trim() || existing;
          }
        }
        if (!label) {
          const h = slide.querySelector('h1, h2, h3, [data-title]');
          if (h) label = (h.textContent || '').trim().slice(0, 40);
        }
        if (!label) label = 'Slide';
        slide.setAttribute('data-screen-label', `${pad2(n)} ${label}`);

        // Validation attribute for comment flow / auto-checks.
        if (!slide.hasAttribute('data-om-validate')) {
          slide.setAttribute('data-om-validate', VALIDATE_ATTR);
        }

        slide.setAttribute('data-deck-slide', String(i));
        this._fragmentSteps.set(slide, 0);
        this._applyFragmentState(slide, 0);
      });

      if (this._totalEl) this._totalEl.textContent = String(this._slides.length || 1);
      if (this._index >= this._slides.length) this._index = Math.max(0, this._slides.length - 1);
    }

    _loadNotes() {
      const tag = document.getElementById('speaker-notes');
      if (!tag) { this._notes = []; return; }
      try {
        const parsed = JSON.parse(tag.textContent || '[]');
        if (Array.isArray(parsed)) this._notes = parsed;
      } catch (e) {
        console.warn('[deck-stage] Failed to parse #speaker-notes JSON:', e);
        this._notes = [];
      }
    }

    _restoreIndex() {
      // The host's ?slide= param is delivered as a #<int> hash (1-indexed) on
      // the iframe src. No hash → slide 1; the deck itself keeps no position
      // state across loads.
      const h = (location.hash || '').match(/^#(\d+)$/);
      if (h) {
        const n = parseInt(h[1], 10) - 1;
        if (n >= 0 && n < this._slides.length) this._index = n;
      }
    }

    _applyIndex({ showOverlay = true, broadcast = true, reason = 'init' } = {}) {
      if (!this._slides.length) return;
      const prev = this._prevIndex == null ? -1 : this._prevIndex;
      const curr = this._index;
      // Keep the iframe's own hash in sync so an in-iframe location.reload()
      // (reload banner path in viewer-handle.ts) lands on the current slide,
      // not the stale deep-link hash from initial load.
      try { history.replaceState(null, '', '#' + (curr + 1)); } catch (e) {}
      this._slides.forEach((s, i) => {
        if (i === curr) s.setAttribute('data-deck-active', '');
        else s.removeAttribute('data-deck-active');
      });
      if (this._countEl) this._countEl.textContent = String(curr + 1);
      this._applyFragmentState(this._slides[curr], 0);
      this._updateFragmentCount(this._slides[curr]);

      if (broadcast) {
        // (1) Legacy: host-window postMessage for speaker-notes renderers.
        try { window.postMessage({ slideIndexChanged: curr }, '*'); } catch (e) {}

        // (2) In-page CustomEvent on the <deck-stage> element itself.
        //     Bubbles and composes out of shadow DOM so slide code can listen:
        //       document.querySelector('deck-stage').addEventListener('slidechange', e => {
        //         e.detail.index, e.detail.previousIndex, e.detail.total, e.detail.slide, e.detail.reason
        //       });
        const detail = {
          index: curr,
          previousIndex: prev,
          total: this._slides.length,
          slide: this._slides[curr] || null,
          previousSlide: prev >= 0 ? (this._slides[prev] || null) : null,
          reason: reason, // 'init' | 'keyboard' | 'click' | 'tap' | 'api'
        };
        this.dispatchEvent(new CustomEvent('slidechange', {
          detail,
          bubbles: true,
          composed: true,
        }));
      }

      this._prevIndex = curr;
      if (showOverlay) this._flashOverlay();
    }

    _flashOverlay() {
      if (!this._overlay) return;
      this._overlay.setAttribute('data-visible', '');
      if (this._hideTimer) clearTimeout(this._hideTimer);
      this._hideTimer = setTimeout(() => {
        this._overlay.removeAttribute('data-visible');
      }, OVERLAY_HIDE_MS);
    }

    _fit() {
      if (!this._canvas) return;
      // PPTX export sets noscale so the DOM capture sees authored-size
      // geometry — the scaled canvas is in shadow DOM, so the exporter's
      // resetTransformSelector can't reach .canvas.style.transform directly.
      if (this.hasAttribute('noscale')) {
        this._canvas.style.transform = 'none';
        return;
      }
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      const s = Math.min(vw / this.designWidth, vh / this.designHeight);
      this._canvas.style.transform = `scale(${s})`;
    }

    _onResize() { this._fit(); }

    _onMouseMove() {
      // Keep overlay visible while mouse moves; hide after idle.
      this._flashOverlay();
    }

    _onTapBack(e) {
      e.preventDefault();
      this._retreat('tap');
    }

    _onTapForward(e) {
      e.preventDefault();
      this._advance('tap');
    }

    _onKey(e) {
      // Ignore when the user is typing.
      const t = e.target;
      if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      const key = e.key;
      let handled = true;

      if (key === 'ArrowRight' || key === 'PageDown' || key === ' ' || key === 'Spacebar') {
        this._advance('keyboard');
      } else if (key === 'ArrowLeft' || key === 'PageUp') {
        this._retreat('keyboard');
      } else if (key === 'Home') {
        this._go(0, 'keyboard');
      } else if (key === 'End') {
        this._go(this._slides.length - 1, 'keyboard');
      } else if (key === 'r' || key === 'R') {
        this.reset();
      } else if (key === 'o' || key === 'O') {
        this._toggleOverview();
      } else if (key === 'f' || key === 'F') {
        this._toggleFs();
      } else if (key === 'Escape') {
        if (this._overviewEl && this._overviewEl.classList.contains('active')) {
          this._toggleOverview();
        } else {
          handled = false;
        }
      } else if (/^[0-9]$/.test(key)) {
        // 1..9 jump to that slide; 0 jumps to 10.
        const n = key === '0' ? 9 : parseInt(key, 10) - 1;
        if (n < this._slides.length) this._go(n, 'keyboard');
      } else {
        handled = false;
      }

      if (handled) {
        e.preventDefault();
        this._flashOverlay();
      }
    }

    _toggleFs() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }

    _toggleOverview() {
      let modal = document.getElementById('overviewModal') || document.querySelector('.deck-overview');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'overviewModal';
        modal.className = 'deck-overview';
        modal.innerHTML = `
          <div class="overview-header">
            <div class="overview-title"><span>🗂 幻灯片全览导航</span><span class="overview-hint">按 ESC 或 O 键快速退出</span></div>
            <button class="overview-close-btn" type="button">✕ 关闭全览</button>
          </div>
          <div class="overview-grid" id="overviewGrid"></div>
        `;
        modal.querySelector('.overview-close-btn').onclick = () => this._toggleOverview();
        document.body.appendChild(modal);
      }
      this._overviewEl = modal;
      const isOpening = !modal.classList.contains('active');
      if (isOpening) {
        const grid = modal.querySelector('.overview-grid') || modal.querySelector('#overviewGrid');
        if (grid) {
          grid.innerHTML = '';
          this._slides.forEach((s, idx) => {
            const card = document.createElement('div');
            card.className = `overview-card ${idx === this._index ? 'current' : ''}`;
            const titleEl = s.querySelector('h1, h2, h3, .slide-title, .h-hero, .h-xl, .h-lg, .h-md, .display-hero, .display-chapter, .cover-title, .section-title, .chapter-title, [data-title]');
            let title = titleEl ? (titleEl.textContent || titleEl.innerText || '').replace(/\s+/g, ' ').trim() : '';
            if (!title) {
              title = s.getAttribute('data-title') || s.getAttribute('data-label') || `第 ${idx + 1} 页`;
            }
            const descEl = s.querySelector('.slide-subtitle, .tagline, .lead, .cover-sub, .body-desc, .desc-compact, p, .card-text, .feature-desc');
            let desc = descEl ? (descEl.textContent || descEl.innerText || '').replace(/\s+/g, ' ').trim() : '';
            if (desc.length > 90) desc = desc.slice(0, 88) + '...';
            card.innerHTML = `
              <span class="overview-card-badge">${String(idx + 1).padStart(2, '0')}</span>
              <div class="overview-card-title">${title}</div>
              <div class="overview-card-desc">${desc}</div>
            `;
            card.onclick = () => { this._go(idx, 'click'); this._toggleOverview(); };
            grid.appendChild(card);
          });
        }
        modal.classList.add('active');
      } else {
        modal.classList.remove('active');
      }
    }

    _go(i, reason = 'api') {
      if (!this._slides.length) return;
      const clamped = Math.max(0, Math.min(this._slides.length - 1, i));
      if (clamped === this._index) {
        this._flashOverlay();
        return;
      }
      this._index = clamped;
      this._applyIndex({ showOverlay: true, broadcast: true, reason });
    }

    _fragments(slide) {
      if (!slide) return [];
      return [...slide.querySelectorAll('[data-fragment]')]
        .map((el, index) => ({ el, index, order: Number(el.getAttribute('data-fragment-order')) }))
        .sort((a, b) => {
          const aOrder = Number.isFinite(a.order) ? a.order : a.index;
          const bOrder = Number.isFinite(b.order) ? b.order : b.index;
          return aOrder - bOrder || a.index - b.index;
        })
        .map(({ el }) => el);
    }

    _applyFragmentState(slide, step, { animate = false } = {}) {
      const fragments = this._fragments(slide);
      const clamped = Math.max(0, Math.min(fragments.length, step));
      this._fragmentSteps.set(slide, clamped);
      fragments.forEach((el, index) => {
        const shown = index < clamped;
        const wasHidden = el.hasAttribute(FRAGMENT_HIDDEN_ATTR);
        if (shown) {
          el.removeAttribute(FRAGMENT_HIDDEN_ATTR);
          if (animate && wasHidden) {
            el.setAttribute(FRAGMENT_ENTER_ATTR, '');
            el.addEventListener('animationend', () => el.removeAttribute(FRAGMENT_ENTER_ATTR), { once: true });
          } else {
            el.removeAttribute(FRAGMENT_ENTER_ATTR);
          }
        } else {
          el.removeAttribute(FRAGMENT_ENTER_ATTR);
          el.setAttribute(FRAGMENT_HIDDEN_ATTR, '');
        }
      });
    }

    _updateFragmentCount(slide) {
      if (!this._fragmentCountEl) return;
      const total = this._fragments(slide).length;
      const step = this._fragmentSteps.get(slide) || 0;
      this._fragmentCountEl.hidden = total === 0;
      this._fragmentCountEl.textContent = total ? `· ${step} / ${total}` : '';
    }

    _advance(reason = 'api') {
      const slide = this._slides[this._index];
      const total = this._fragments(slide).length;
      const step = this._fragmentSteps.get(slide) || 0;
      if (step < total) {
        this._applyFragmentState(slide, step + 1, { animate: true });
        this._updateFragmentCount(slide);
        this._flashOverlay();
        return;
      }
      this._go(this._index + 1, reason);
    }

    _retreat(reason = 'api') {
      const slide = this._slides[this._index];
      const step = this._fragmentSteps.get(slide) || 0;
      if (step > 0) {
        this._applyFragmentState(slide, step - 1);
        this._updateFragmentCount(slide);
        this._flashOverlay();
        return;
      }
      if (this._index <= 0) return;
      this._go(this._index - 1, reason);
      const previous = this._slides[this._index];
      this._applyFragmentState(previous, this._fragments(previous).length);
      this._updateFragmentCount(previous);
    }

    // Public API ------------------------------------------------------------

    /** Current slide index (0-based). */
    get index() { return this._index; }
    /** Total slide count. */
    get length() { return this._slides.length; }
    /** Programmatically navigate. */
    goTo(i) { this._go(i, 'api'); }
    next() { this._advance('api'); }
    prev() { this._retreat('api'); }
    reset() {
      this._index = 0;
      this._applyIndex({ showOverlay: true, broadcast: true, reason: 'api' });
    }
    toggleFullscreen() { this._toggleFs(); }
    toggleOverview() { this._toggleOverview(); }

    _initImageLightbox() {
      let lb = document.getElementById('imgLightbox');
      if (!lb) {
        lb = document.createElement('div');
        lb.id = 'imgLightbox';
        lb.className = 'img-lightbox';
        lb.setAttribute('role', 'dialog');
        lb.setAttribute('aria-hidden', 'true');
        lb.setAttribute('aria-label', '图片放大预览');
        lb.innerHTML = `
          <button class="img-lightbox-close" type="button" aria-label="关闭">×</button>
          <button class="img-lightbox-prev" type="button" aria-label="上一张" hidden>‹</button>
          <button class="img-lightbox-next" type="button" aria-label="下一张" hidden>›</button>
          <div class="img-lightbox-counter" id="imgLightboxCounter" hidden></div>
          <div class="img-lightbox-frame">
            <img class="img-lightbox-img" id="imgLightboxImg" alt="放大预览" />
          </div>
          <div class="img-lightbox-hint">双击图片 · ESC · 任意位置关闭</div>
        `;
        document.body.appendChild(lb);
      }

      const lbImg = document.getElementById('imgLightboxImg') || lb.querySelector('.img-lightbox-img');
      const lbCounter = document.getElementById('imgLightboxCounter') || lb.querySelector('.img-lightbox-counter');
      const lbClose = lb.querySelector('.img-lightbox-close');
      const lbPrev = lb.querySelector('.img-lightbox-prev');
      const lbNext = lb.querySelector('.img-lightbox-next');
      let currentGroup = { items: [] };
      let currentIndex = -1;

      const collectGroups = () => {
        const groups = new Map();
        const allImgs = document.querySelectorAll('img, [data-zoomable] img');
        allImgs.forEach(img => {
          if (img.classList.contains('img-lightbox-img') || img.closest('.deck-overview') || img.closest('.img-lightbox')) return;
          const slide = img.closest('.slide, [data-slide], section') || document.body;
          const key = slide.id || ('__grp__' + groups.size);
          if (!groups.has(key)) groups.set(key, { slide, items: [] });
          groups.get(key).items.push({
            img,
            src: img.getAttribute('src') || img.currentSrc,
            alt: img.getAttribute('alt') || ''
          });
        });
        return groups;
      };

      const applyItem = (group, index) => {
        const item = group.items[index];
        if (!item) return;
        if (lbImg.src !== item.src) lbImg.src = item.src;
        lbImg.alt = item.alt;
        if (group.items.length > 1) {
          lbCounter.textContent = (index + 1) + ' / ' + group.items.length;
          lbCounter.hidden = false;
          lbPrev.hidden = false;
          lbNext.hidden = false;
        } else {
          lbCounter.hidden = true;
          lbPrev.hidden = true;
          lbNext.hidden = true;
        }
      };

      const openAt = (group, index) => {
        currentGroup = group;
        currentIndex = index;
        applyItem(group, index);
        lb.classList.add('open');
        lb.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
      };

      const close = () => {
        lb.classList.remove('open');
        lb.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
      };

      const nav = (delta) => {
        if (!currentGroup.items || !currentGroup.items.length) return;
        const n = currentGroup.items.length;
        if (n < 2) return;
        currentIndex = (currentIndex + delta + n) % n;
        applyItem(currentGroup, currentIndex);
      };

      lb.addEventListener('click', (e) => {
        if (e.target === lb || e.target.classList.contains('img-lightbox-frame')) close();
      });
      lb.addEventListener('dblclick', (e) => {
        e.stopPropagation();
        close();
      });
      if (lbClose) lbClose.addEventListener('click', (e) => { e.stopPropagation(); close(); });
      if (lbPrev) lbPrev.addEventListener('click', (e) => { e.stopPropagation(); nav(-1); });
      if (lbNext) lbNext.addEventListener('click', (e) => { e.stopPropagation(); nav(1); });

      const bindEvents = () => {
        const groups = collectGroups();
        groups.forEach(g => {
          g.items.forEach((item, i) => {
            item.img.addEventListener('dblclick', (e) => {
              e.preventDefault();
              e.stopPropagation();
              openAt(g, i);
            });
            const zoomableParent = item.img.closest('[data-zoomable]');
            if (zoomableParent) {
              zoomableParent.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openAt(g, i);
              });
            }
          });
        });
      };

      setTimeout(bindEvents, 100);

      document.addEventListener('keydown', (e) => {
        if (!lb.classList.contains('open')) return;
        if (e.key === 'Escape') { close(); e.stopPropagation(); e.preventDefault(); }
        else if (e.key === 'ArrowLeft') { nav(-1); e.stopPropagation(); e.preventDefault(); }
        else if (e.key === 'ArrowRight') { nav(1); e.stopPropagation(); e.preventDefault(); }
      }, true);
    }
  }

  if (!customElements.get('deck-stage')) {
    customElements.define('deck-stage', DeckStage);
  }
})();
