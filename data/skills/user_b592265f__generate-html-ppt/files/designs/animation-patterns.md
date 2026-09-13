# Animation Patterns Reference

Use this reference when generating presentations. Match animations to the intended feeling.

> **Canonical source.** The classes and timing tokens in this file are the same ones used by
> `templates/beautiful-modern/design.md` and the same ones `scripts/validate-fluid-deck.mjs`
> expects. If a future template introduces a new animation vocabulary, add it there first and
> cross-link from here — do not invent a parallel system.

## Effect-to-Feeling Guide

| Feeling | Animations | Visual Cues |
|---------|-----------|-------------|
| **Dramatic / Cinematic** | Slow fade-ins (1-1.5s), large scale transitions (0.9 to 1), parallax scrolling | Dark backgrounds, spotlight effects, full-bleed images |
| **Techy / Futuristic** | Neon glow (box-shadow), glitch/scramble text, grid reveals | Particle systems (canvas), grid patterns, monospace accents, cyan/magenta/electric blue |
| **Playful / Friendly** | Bouncy easing (spring physics), floating/bobbing | Rounded corners, pastel/bright colors, hand-drawn elements |
| **Professional / Corporate** | Subtle fast animations (200-300ms), clean slides | Navy/slate/charcoal, precise spacing, data visualization focus |
| **Calm / Minimal** | Very slow subtle motion, gentle fades | High whitespace, muted palette, serif typography, generous padding |
| **Editorial / Magazine** | Staggered text reveals, image-text interplay | Strong type hierarchy, pull quotes, grid-breaking layouts, serif headlines + sans body |

## Presenter-paced builds (逐步呈现)

Use a presenter-paced build only when the audience should focus on one argument, card,
or diagram node at a time. It is opt-in: ordinary slides must not be marked and keep
their normal page-to-page navigation.

`deck-stage.js` owns the interaction. It reveals each `[data-fragment]` in DOM order;
use `data-fragment-order` only to override that order. `Space`, `→`, PageDown, the next
button, and the mobile forward zone reveal the next item before advancing the page. `←`,
PageUp, and the previous button undo a shown item before returning to the prior page.

```html
<section data-label="Three levers">
  <h1>聚焦一个决策，再给出一个依据</h1>
  <article class="card" data-fragment data-fragment-effect="fade-up">先说明问题</article>
  <article class="card" data-fragment data-fragment-effect="scale">再对比选择</article>
  <article class="card" data-fragment data-fragment-effect="wipe">最后给出结论</article>
</section>
```

Supported effects are `fade` (default), `fade-up`, `scale`, and `wipe`. Fragments retain
their layout space while hidden so a reveal does not make the slide jump. With reduced
motion enabled, the item still appears step-by-step without movement. When a slide is
entered normally it starts with no fragments shown; returning with `←` lands on the
previous slide with its completed build, matching presenter expectations.

## Entrance Animations (`.anim*` + `.d1`–`.d8`)

The entrance vocabulary is a single base class plus four directional variants, paired with
delay classes for staggered reveals. All variants are spring-physics: opacity fades in while
transform overshoots its resting position, then settles.

```css
:root {
    --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes springUp    { 0% { opacity: 0; transform: translateY(45px) scale(0.94); } 60% { opacity: 1; transform: translateY(-6px) scale(1.015); } 100% { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes springLeft  { 0% { opacity: 0; transform: translateX(-60px); } 60% { opacity: 1; transform: translateX(8px); } 100% { opacity: 1; transform: translateX(0); } }
@keyframes springRight { 0% { opacity: 0; transform: translateX(60px); } 60% { opacity: 1; transform: translateX(-8px); } 100% { opacity: 1; transform: translateX(0); } }
@keyframes springScale { 0% { opacity: 0; transform: scale(0.85); } 60% { opacity: 1; transform: scale(1.03); } 100% { opacity: 1; transform: scale(1); } }
@keyframes float       { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }

.anim              { opacity: 0; }
.slide.active .anim        { animation: springUp 0.85s var(--ease-spring) forwards; }
.slide.active .anim-left   { animation-name: springLeft; }
.slide.active .anim-right  { animation-name: springRight; }
.slide.active .anim-scale  { animation-name: springScale; }
.slide.active .anim-float  { animation: float 4s ease-in-out infinite; opacity: 1; }

/* Staggered delays — apply to children in DOM order */
.slide.active .d1 { animation-delay: 0.08s; }
.slide.active .d2 { animation-delay: 0.18s; }
.slide.active .d3 { animation-delay: 0.30s; }
.slide.active .d4 { animation-delay: 0.42s; }
.slide.active .d5 { animation-delay: 0.54s; }
.slide.active .d6 { animation-delay: 0.66s; }
.slide.active .d7 { animation-delay: 0.78s; }
.slide.active .d8 { animation-delay: 0.90s; }
```

**Usage pattern** — every animated element on a slide gets `.anim` (or one of the directional
variants) plus a delay class for staggering:

```html
<h2 class="anim d1">Spring entrance</h2>
<p  class="anim d2">The second element lands 100ms after the first.</p>
<div class="card anim d3">Cards stagger into the layout.</div>
<div class="cover-orb anim-float">Background orbs loop forever.</div>
```

**Rule of thumb.** `validate-fluid-deck.mjs` warns if a non-hero slide has fewer than 3
`.anim*` elements. Aim for `.anim d1` on the kicker, `.anim d2` on the title, `.anim d3` on
the lead paragraph, and `.anim d4`–`.d6` on cards. Hero slides may use only `.anim-float` for
orbs because the static layout speaks for itself.

## Background Effects

```css
/* Gradient Mesh — layered radial gradients for depth */
.gradient-bg {
    background:
        radial-gradient(ellipse at 20% 80%, rgba(120, 0, 255, 0.3) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.2) 0%, transparent 50%),
        var(--bg-primary);
}

/* Noise Texture — inline SVG for grain */
.noise-bg {
    background-image: url("data:image/svg+xml,..."); /* Inline SVG noise */
}

/* Grid Pattern — subtle structural lines */
.grid-bg {
    background-image:
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
}
```

## Interactive Effects

```javascript
/* 3D Tilt on Hover — adds depth to cards/panels */
class TiltEffect {
    constructor(element) {
        this.element = element;
        this.element.style.transformStyle = 'preserve-3d';
        this.element.style.perspective = '1000px';

        this.element.addEventListener('mousemove', (e) => {
            const rect = this.element.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            this.element.style.transform = `rotateY(${x * 10}deg) rotateX(${-y * 10}deg)`;
        });

        this.element.addEventListener('mouseleave', () => {
            this.element.style.transform = 'rotateY(0) rotateX(0)';
        });
    }
}
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Fonts not loading | Check Fontshare/Google Fonts URL; ensure font names match in CSS |
| Animations not triggering | Confirm the slide has `.active` (Beautiful) or `[data-deck-active]` (deck-stage web component). The `.anim` rule is a no-op until the parent slide is active. |
| Animations fire on first paint instead of on slide change | `.anim` only animates when its parent gains `.active` / `[data-deck-active]`. Do **not** set `.anim` on elements that should be visible on slide 1 before activation — gate with `opacity: 0` only inside `.slide.active` rules. |
| Scroll snap not working | Ensure `scroll-snap-type: y mandatory` on html; each slide needs `scroll-snap-align: start` |
| Mobile issues | Disable heavy effects at 768px breakpoint; test touch events; reduce particle count |
| Performance issues | Use `will-change` sparingly; prefer `transform`/`opacity` animations; throttle scroll handlers |

## Migration Note (legacy `.reveal*` classes)

The old `.reveal` / `.reveal-scale` / `.reveal-left` / `.reveal-blur` vocabulary that this file
used to document is no longer used by any template in `bold-template-pack/`. It was an
Intersection-Observer-driven system, not a parent-class-driven one, and it conflicted with the
spring-physics vocabulary that the Beautiful / Cyberpunk templates ship. Do not generate new
slides with `.reveal*` classes — `validate-fluid-deck.mjs` will count them as 0 animated
elements and the deck will fail the "≥3 anims per slide" quality bar.
