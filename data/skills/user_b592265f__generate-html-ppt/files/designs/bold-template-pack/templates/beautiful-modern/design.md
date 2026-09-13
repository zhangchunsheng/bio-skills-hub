---
version: 1.0.0
name: Beautiful Modern
description: A state-of-the-art presentation system inspired by Beautiful.ai with glassmorphism, spring-physics animations, fluid layout controls, and seamless viewport background synchronization. Built on Outfit (Display) and Plus Jakarta Sans (Body), with saturated HSL accents, gradient glowing orbs, dynamic stats count-up, and smart layout density strategies (Scheme 1 vs Scheme 2) to eliminate awkward empty gaps.

colors:
  bg-light: "#f8fafc"
  bg-dark: "#0f172a"
  surface-light: "rgba(255, 255, 255, 0.85)"
  surface-dark: "rgba(30, 41, 59, 0.75)"
  text-dark: "#0f172a"
  text-light: "#f8fafc"
  text-muted: "#64748b"
  border-light: "rgba(15, 23, 42, 0.08)"
  border-dark: "rgba(255, 255, 255, 0.12)"
  accent: "#4f46e5"
  accent-600: "#4338ca"
  accent-cyan: "#06b6d4"
  accent-light: "#e0e7ff"
  accent-soft: "rgba(79, 70, 229, 0.12)"
  teal: "#0d9488"
  rose: "#e11d48"
  amber: "#d97706"
  violet: "#7c3aed"

typography:
  display-hero:
    fontFamily: "'Outfit', sans-serif"
    fontWeight: 800
    fontSize: "clamp(72px, 7vw, 120px)"
    lineHeight: 1.05
    letterSpacing: "-0.03em"
  display-chapter:
    fontFamily: "'Outfit', sans-serif"
    fontWeight: 700
    fontSize: "clamp(48px, 4.5vw, 64px)"
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  eyebrow-pill:
    fontFamily: "'Outfit', sans-serif"
    fontWeight: 800
    fontSize: "16px"
    letterSpacing: "0.12em"
    textTransform: "uppercase"
  body:
    fontFamily: "'Plus Jakarta Sans', 'Noto Sans SC', sans-serif"
    fontWeight: 400
    fontSize: "22px"
    lineHeight: 1.6
---

## Tone Policy (Default: Dark)

**Canonical tone: `dark`.** Every Beautiful Modern deck MUST default to `class="slide dark"` on every slide unless the user explicitly requests light or specifies a context where light is the established convention (e.g. healthcare education, print-first deliverables, accessibility for low-vision viewers in bright rooms).

Why dark is the default:
- The :root token set (`--slide-bg: #0f172a`, `--viewport-bg: #0f172a`, `--b-grad-dark`) is the design system's foundation; orbs, glassmorphism, and gradient text are all tuned for dark.
- The Beautiful.ai inspiration and the spring-physics motion language both read as premium-dark.
- Inconsistent alternation produces a deck that feels like two different decks stitched together; users almost always want one consistent mood.

When light is appropriate (use sparingly, NEVER as the default):
- The user explicitly asks for "light / clean / 学术 / 印刷风 / 医疗 / 教育".
- The presentation will be printed in B&W or projected on a very bright screen and readability of small text on dark glass becomes a concern.
- Light is a per-slide emphasis-divider tool, NOT a deck-wide pattern. If you do mix, treat dark as the structural canvas and use light only for short pause/divider slides (≤20% of the deck, never the cover or the closing).

Reference: see `preview.md` for the canonical dark title slide; see the Beautiful Modern sections in `demo/beautiful-demo.html` for end-to-end dark-toned usage.

---

# Beautiful Modern Design System Specification

This document defines the complete visual design recipe, CSS system tokens, animation physics, component specifications, and layout density rules for the **Beautiful Modern** style.

---

## 1. Design Principles & Core Architecture

1. **Fixed 16:9 Canvas Stage (1920×1080)**: Every slide is constructed inside a `.deck-stage` canvas uniformly scaled to any viewport using JavaScript (`updateScale()`).
2. **Seamless Viewport Background**: Dynamic background sync (`updateViewportBg()`) ensures outer screen padding seamlessly matches the active slide's background gradient or tone.
3. **Glassmorphism & Spring Physics**: Light/dark surface layers with backdrop blurs (`backdrop-filter: blur(16px/20px)`), paired with spring-physics motion curves (`cubic-bezier(0.175, 0.885, 0.32, 1.275)`).
4. **Layout Density Strategy (防止中间尴尬中空与过度拉伸)**:
   - **Avoid Space-Between Stretching (space-between 滥用规避)**: Do NOT use `justify-content: space-between;` on slides where middle component heights are low (<200px). Otherwise, `space-between` pushes elements to top/bottom edges leaving 200px-400px empty voids in between.
   - **Scheme 1 (Tight Center/Top Grouping)**: Use `.slide-content.center-group` (`justify-content: center; gap: 40px;`) or `.slide-content` (`justify-content: flex-start; gap: 40px;`), tightly grouping title, middle bridges, and bottom cards.
   - **Scheme 2 (3-Section Bridge Layout)**: Use `.slide-content.between` ONLY when middle component has rich content height (e.g. detailed `.pipeline` steps with bullet lists, `.stat-card` rows, or `.hero-middle-bridge` feature chips).

---

## 2. CSS Design Tokens & Base CSS

Include these fonts and CSS declarations in the `<head>` of the presentation:

```html
<!-- Google Fonts: Outfit (Display) & Plus Jakarta Sans / Noto Sans SC (Body) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js" integrity="sha384-o5uz97et3bErHvpKfD4Jz4n0JfhJDWABFuF4NP+iEEDxE1VwMWJ19QGR0lqFZnr6" crossorigin="anonymous" defer></script>
```

```css
:root {
  --b-bg-light: #f8fafc;
  --b-bg-dark: #0f172a;
  --b-surface-light: rgba(255, 255, 255, 0.85);
  --b-surface-dark: rgba(30, 41, 59, 0.75);
  --b-text-dark: #0f172a;
  --b-text-light: #f8fafc;
  --b-text-muted: #64748b;
  --b-border-light: rgba(15, 23, 42, 0.08);
  --b-border-dark: rgba(255, 255, 255, 0.12);

  --b-accent: #4f46e5;
  --b-accent-600: #4338ca;
  --b-accent-cyan: #06b6d4;
  --b-accent-light: #e0e7ff;
  --b-accent-soft: rgba(79, 70, 229, 0.12);

  --b-teal: #0d9488;
  --b-rose: #e11d48;
  --b-amber: #d97706;
  --b-violet: #7c3aed;

  --b-grad-accent: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
  --b-grad-dark: radial-gradient(ellipse 80% 60% at 20% 30%, rgba(99,102,241,0.25), transparent),
                 radial-gradient(ellipse 60% 50% at 80% 80%, rgba(6,182,212,0.20), transparent),
                 linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
  --b-grad-light: radial-gradient(ellipse 80% 60% at 20% 30%, rgba(79,70,229,0.08), transparent),
                  radial-gradient(ellipse 60% 50% at 80% 80%, rgba(6,182,212,0.08), transparent),
                  linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);

  --viewport-bg: #0f172a;
  --slide-bg: #0f172a;

  --font-display: 'Outfit', sans-serif;
  --font-body: 'Plus Jakarta Sans', 'Noto Sans SC', sans-serif;

  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
  --ease-smooth: cubic-bezier(0.22, 1, 0.36, 1);
  --radius-md: 24px;
}

/* Stage Setup */
html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; background: var(--viewport-bg); font-family: var(--font-body); }
.deck-viewport { position: fixed; inset: 0; overflow: hidden; background: var(--viewport-bg); transition: background 0.5s ease; display: flex; align-items: center; justify-content: center; }
.deck-stage { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: hidden; transform-origin: 0 0; background: var(--slide-bg); box-shadow: 0 25px 60px -15px rgba(0,0,0,0.4); }
.slide { position: absolute; inset: 0; width: 1920px; height: 1080px; overflow: hidden; visibility: hidden; opacity: 0; pointer-events: none; transition: opacity 0.4s ease, visibility 0.4s ease; padding: 90px 110px; box-sizing: border-box; }
.slide.active { visibility: visible; opacity: 1; pointer-events: auto; z-index: 1; }

.slide.dark { background: var(--b-grad-dark); color: var(--b-text-light); --card-bg: var(--b-surface-dark); --card-border: var(--b-border-dark); --text-color: var(--b-text-light); --text-sub: #94a3b8; }
.slide.light { background: var(--b-grad-light); color: var(--b-text-dark); --card-bg: var(--b-surface-light); --card-border: var(--b-border-light); --text-color: var(--b-text-dark); --text-sub: var(--b-text-muted); }

/* Layout Rules (Scheme 1 vs Scheme 2) */
.slide-content, .frame { position: relative; z-index: 2; height: 100%; display: flex; flex-direction: column; justify-content: flex-start; gap: 40px; }
.slide-content.between, .frame.between { justify-content: space-between; gap: 0; }
.slide-content.center, .frame.center { justify-content: center; align-items: center; text-align: center; }
.slide-content.center-group, .frame.center-group { justify-content: center; gap: 40px; }

/* Middle Bridge Feature Chips (Hero Cover Component) */
.hero-middle-bridge { display: flex; gap: 16px; flex-wrap: wrap; margin-top: -8px; margin-bottom: 4px; }
.hero-chip { padding: 10px 22px; border-radius: 30px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.12); backdrop-filter: blur(12px); font-size: 19px; font-weight: 600; color: #cbd5e1; display: flex; align-items: center; gap: 8px; transition: all 0.3s ease; }
.hero-chip:hover { background: rgba(79, 70, 229, 0.15); border-color: rgba(6, 182, 212, 0.4); color: #fff; transform: translateY(-2px); }
.chip-dot { color: var(--b-accent-cyan); font-size: 18px; }

/* Grid Helper Classes */
.grid-2col, .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
.grid-3col, .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 32px; }
.grid-4col, .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }

/* Glass Cards */
.b-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--radius-md); padding: 36px; backdrop-filter: blur(16px); box-shadow: 0 20px 40px -15px rgba(0,0,0,0.08); transition: transform 0.3s var(--ease-spring), box-shadow 0.3s ease; display: flex; flex-direction: column; justify-content: space-between; }
.b-card:hover { transform: translateY(-6px); box-shadow: 0 25px 50px -12px rgba(79, 70, 229, 0.18); }
.b-card.teal { --b-accent: var(--b-teal); }
.b-card.rose { --b-accent: var(--b-rose); }
.b-card.amber { --b-accent: var(--b-amber); }
.b-card.violet { --b-accent: var(--b-violet); }

/* Card Header & Components (单行同行并排标准) */
.card-header, .b-card-header, .card-title-row, .step-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; width: 100%; }
.card-header h3, .b-card-header h3, .card-title-row h3, .step-header h3 { margin: 0 !important; display: inline-flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.card-num-badge { width: 44px; height: 44px; border-radius: 12px; background: var(--b-grad-accent); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-family: var(--font-display); font-size: 20px; font-weight: 800; flex-shrink: 0; }
.icon-box { width: 48px; height: 48px; border-radius: 12px; background: var(--b-accent-soft); color: var(--b-accent); display: inline-flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.icon-box.teal { background: rgba(13,148,136,0.12); color: var(--b-teal); }
.icon-box.rose { background: rgba(225,29,72,0.12); color: var(--b-rose); }
.icon-box.amber { background: rgba(217,119,6,0.12); color: var(--b-amber); }
.icon-box.violet { background: rgba(124,58,237,0.12); color: var(--b-violet); }

/* Pipeline Steps (Scheme 2 Component) */
.pipeline { display: flex; gap: 24px; width: 100%; margin: 10px 0; }
.pipeline-step { flex: 1; background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--radius-md); padding: 24px; position: relative; backdrop-filter: blur(16px); }
.pipeline-step::after { content: ''; position: absolute; top: 50%; right: -20px; width: 14px; height: 14px; border-top: 3px solid var(--b-accent-cyan); border-right: 3px solid var(--b-accent-cyan); transform: translateY(-50%) rotate(45deg); opacity: 0.8; }
.pipeline-step:last-child::after { display: none; }
.step-nb { width: 38px; height: 38px; border-radius: 50%; background: var(--b-grad-accent); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-family: var(--font-display); font-weight: 800; font-size: 18px; flex-shrink: 0; }

/* Stat Cards */
.stat-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--radius-md); padding: 24px; backdrop-filter: blur(16px); }
.stat-label { font-size: 16px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: var(--text-sub); margin-bottom: 8px; }
.stat-nb { font-family: var(--font-display); font-size: 56px; font-weight: 800; background: var(--b-grad-accent); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1; }

/* Code Box & Blueprint Tree (Engineering / Architecture Component) */
.code-box { background: rgba(11, 17, 33, 0.88); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 20px; padding: 28px 34px; backdrop-filter: blur(20px); box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6); display: flex; flex-direction: column; justify-content: center; }
.code-box-header { color: #38bdf8; font-weight: 800; font-size: 20px; font-family: var(--font-mono, monospace); margin-bottom: 16px; }
.code-tree { margin: 0; font-family: var(--font-mono, monospace); font-size: 20px; line-height: 1.8; color: #cbd5e1; }
.cards-column { display: flex; flex-direction: column; gap: 16px; justify-content: space-between; }

/* Animations */
@keyframes springUp { 0% { opacity: 0; transform: translateY(45px) scale(0.94); } 60% { opacity: 1; transform: translateY(-6px) scale(1.015); } 100% { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes springLeft { 0% { opacity: 0; transform: translateX(-60px); } 60% { opacity: 1; transform: translateX(8px); } 100% { opacity: 1; transform: translateX(0); } }
@keyframes springRight { 0% { opacity: 0; transform: translateX(60px); } 60% { opacity: 1; transform: translateX(-8px); } 100% { opacity: 1; transform: translateX(0); } }
@keyframes springScale { 0% { opacity: 0; transform: scale(0.85); } 60% { opacity: 1; transform: scale(1.03); } 100% { opacity: 1; transform: scale(1); } }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }

.anim { opacity: 0; }
.slide.active .anim { animation: springUp 0.85s var(--ease-spring) forwards; }
.slide.active .anim-left { animation-name: springLeft; }
.slide.active .anim-right { animation-name: springRight; }
.slide.active .anim-scale { animation-name: springScale; }
.slide.active .anim-float { animation: float 4s ease-in-out infinite; opacity: 1; }

.slide.active .d1 { animation-delay: 0.08s; }
.slide.active .d2 { animation-delay: 0.18s; }
.slide.active .d3 { animation-delay: 0.30s; }
.slide.active .d4 { animation-delay: 0.42s; }
```

---

## 3. Core JavaScript Scaling, 4-Button Controls & Overview

Include this HTML & script at the end of the presentation file:

```html
<!-- 标准底部悬浮控制台 (Controls Bar) -->
<div class="controls-bar" id="controlsBar">
    <button class="ctrl-btn" onclick="prevSlide()" title="上一页 (← / PageUp)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 18l-6-6 6-6"/></svg> 上一页
    </button>
    <div class="slide-counter">
        <span id="counter">01 / 12</span>
        <div class="slide-progress-track"><div class="slide-progress-fill" id="progressFill" style="width: 8.3%;"></div></div>
    </div>
    <button class="ctrl-btn" onclick="nextSlide()" title="下一页 (→ / Space / PageDown)">
        下一页 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18l6-6-6-6"/></svg>
    </button>
    <button class="ctrl-btn" onclick="toggleOverview()" title="全览缩略图 (O / Esc)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg> 全览
    </button>
    <button class="ctrl-btn" onclick="toggleFullScreen()" title="全屏演示 (F)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg> 全屏
    </button>
</div>

<!-- 标准全览缩略图模态框 (Overview Modal) -->
<div class="deck-overview" id="overviewModal">
    <div class="overview-header">
        <div class="overview-title">
            <span>🗂 幻灯片全览导航</span>
            <span class="overview-hint">按 ESC 或 O 键快速退出</span>
        </div>
        <button class="overview-close-btn" onclick="toggleOverview()">✕ 关闭全览</button>
    </div>
    <div class="overview-grid" id="overviewGrid"></div>
</div>

<script>
    let currentSlide = 1;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;

    function updateScale() {
        const stage = document.getElementById('stage') || document.querySelector('.deck-stage');
        if (!stage) return;
        const scaleX = window.innerWidth / 1920;
        const scaleY = window.innerHeight / 1080;
        const scale = Math.min(scaleX, scaleY);
        const left = (window.innerWidth - 1920 * scale) / 2;
        const top = (window.innerHeight - 1080 * scale) / 2;
        stage.style.transform = `translate(${left}px, ${top}px) scale(${scale})`;
    }

    function updateViewportBg(slideIndex) {
        const slide = document.getElementById(`s${slideIndex}`) || slides[slideIndex - 1];
        if (slide) {
            const bg = slide.getAttribute('data-bg') || (slide.classList.contains('dark') ? '#0f172a' : '#f8fafc');
            document.documentElement.style.setProperty('--viewport-bg', bg);
        }
    }

    function showSlide(index) {
        if (index < 1) index = 1;
        if (index > totalSlides) index = totalSlides;
        currentSlide = index;
        slides.forEach((slide, i) => {
            slide.classList.toggle('active', i + 1 === currentSlide);
        });
        const counter = document.getElementById('counter');
        if (counter) counter.innerText = `${String(currentSlide).padStart(2, '0')} / ${String(totalSlides).padStart(2, '0')}`;
        const progressFill = document.getElementById('progressFill');
        if (progressFill) progressFill.style.width = `${(currentSlide / totalSlides) * 100}%`;
        updateViewportBg(currentSlide);
    }

    function nextSlide() { if (currentSlide < totalSlides) showSlide(currentSlide + 1); }
    function prevSlide() { if (currentSlide > 1) showSlide(currentSlide - 1); }

    function toggleFullScreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => {});
        } else {
            if (document.exitFullscreen) document.exitFullscreen();
        }
    }

    function buildOverview() {
        const grid = document.getElementById('overviewGrid');
        if (!grid) return;
        grid.innerHTML = '';
        slides.forEach((s, idx) => {
            const card = document.createElement('div');
            card.className = `overview-card ${idx + 1 === currentSlide ? 'current' : ''}`;
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
            card.onclick = () => { showSlide(idx + 1); toggleOverview(); };
            grid.appendChild(card);
        });
    }

    function toggleOverview() {
        const modal = document.getElementById('overviewModal');
        if (!modal) return;
        const isOpening = !modal.classList.contains('active');
        if (isOpening) {
            buildOverview();
            modal.classList.add('active');
        } else {
            modal.classList.remove('active');
        }
    }

    document.addEventListener('keydown', (e) => {
        const modal = document.getElementById('overviewModal');
        const isOverviewActive = modal && modal.classList.contains('active');
        if (e.key === 'Escape') {
            if (isOverviewActive) { toggleOverview(); return; }
        }
        if (e.key === 'o' || e.key === 'O') { toggleOverview(); return; }
        if (e.key === 'f' || e.key === 'F') { if (!e.metaKey && !e.ctrlKey) toggleFullScreen(); return; }
        if (isOverviewActive) return;
        if (e.key === 'ArrowRight' || e.key === 'Space' || e.key === 'PageDown') { e.preventDefault(); nextSlide(); }
        if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prevSlide(); }
        if (e.key === 'Home') { e.preventDefault(); showSlide(1); }
        if (e.key === 'End') { e.preventDefault(); showSlide(totalSlides); }
    });

    window.addEventListener('resize', updateScale);
    updateScale();
    updateViewportBg(1);
</script>
```
