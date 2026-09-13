#!/usr/bin/env node
//
// Validates decks built from fluid-layout templates that use the
// `<div class="slide …">` + light/dark theme convention. Today this covers
// Beautiful Modern and Cyberpunk Dark, and any future template that adopts
// the same vocabulary. Swiss / 8-Bit / Emerald / Neo-Grid etc. have their
// own layout grammars and should use `validate-swiss-deck.mjs` or a
// style-specific validator instead.
//
// If you only have a `validate-beautiful-deck.mjs` path in your workflow
// (older docs, cached shells), it is an old alias for this file.
//
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const file = process.argv[2];
if (!file) {
  console.error('Usage: node scripts/validate-fluid-deck.mjs <index.html>');
  process.exit(2);
}

const html = readFileSync(file, 'utf8');
const errors = [];
const warnings = [];

async function loadPlaywright() {
  const candidates = [
    createRequire(import.meta.url),
    createRequire(pathToFileURL(path.join(process.cwd(), 'package.json')).href),
  ];
  for (const req of candidates) {
    try {
      const resolved = req.resolve('playwright');
      const mod = await import(pathToFileURL(resolved).href);
      return mod.default || mod;
    } catch {
      // Try the next resolution root.
    }
  }
  return null;
}

// Extract slide containers with depth-aware parsing. Existing fluid decks use
// either <div>, <section>, or <article> as the slide root; the class contract
// is the stable part.
function extractSlides() {
  const slides = [];
  const openRe = /<(div|section|article)\b[^>]*class="[^"]*\bslide\b(?!-)[^"]*"[^>]*>/gi;
  let match;
  while ((match = openRe.exec(html)) !== null) {
    const start = match.index;
    const tagName = match[1].toLowerCase();
    const tagEnd = html.indexOf('>', start);
    if (tagEnd === -1) continue;
    let depth = 1;
    let i = tagEnd + 1;
    while (i < html.length && depth > 0) {
      const nextOpenMatch = new RegExp(`<${tagName}\\b`, 'ig');
      nextOpenMatch.lastIndex = i;
      const nextOpen = nextOpenMatch.exec(html)?.index ?? -1;
      const nextClose = html.toLowerCase().indexOf(`</${tagName}>`, i);
      if (nextClose === -1) break;
      if (nextOpen !== -1 && nextOpen < nextClose) {
        depth++;
        i = nextOpen + tagName.length + 1;
      } else {
        depth--;
        if (depth === 0) {
          const closeLength = tagName.length + 3;
          slides.push({ idx: slides.length + 1, html: html.slice(start, nextClose + closeLength), tag: match[0] });
          i = nextClose + closeLength;
          openRe.lastIndex = i;
        } else {
          i = nextClose + 6;
        }
      }
    }
  }
  return slides;
}

const slides = extractSlides();

if (!slides.length) {
  errors.push('No <div class="slide"> pages found. This validator targets fluid-layout templates (Beautiful Modern, Cyberpunk Dark). If your deck uses a Swiss / 8-Bit / Emerald / Neo-Grid layout, run its style-specific validator instead.');
}

const firstSlideClasses = slides[0]?.tag.match(/\bclass="([^"]*)"/)?.[1]?.split(/\s+/) || [];
const firstSlideIsCover = firstSlideClasses.includes('hero') || firstSlideClasses.includes('cover') || /\bdata-density-exempt="cover"/.test(slides[0]?.tag || '');
const firstSlideHasCoverSubject = /\bdata-cover-subject(?:\s|=|>)/.test(slides[0]?.html || '');
if (firstSlideIsCover && !firstSlideHasCoverSubject) {
  errors.push('Slide 1: cover/hero slide is missing data-cover-subject. Mark the wrapper around the real title, narrative copy, and supporting data/visuals so visual centering can be verified.');
}

const ids = [];
const themes = [];
slides.forEach((slide) => {
  const clsMatch = slide.tag.match(/\bclass="([^"]*)"/);
  const classes = clsMatch ? clsMatch[1].split(/\s+/) : [];
  const idMatch = slide.tag.match(/\bid="([^"]*)"/);
  const id = idMatch ? idMatch[1] : null;

  // ID
  if (!id) {
    errors.push(`Slide ${slide.idx}: missing id. Use id="s{N}".`);
  } else if (!/^s\d+$/.test(id)) {
    errors.push(`Slide ${slide.idx}: id "${id}" does not match s{N} pattern.`);
  } else {
    ids.push(parseInt(id.slice(1), 10));
  }

  // Theme class
  const hasLight = classes.includes('light');
  const hasDark = classes.includes('dark');
  const isHero = classes.includes('hero');
  if (!hasLight && !hasDark) {
    errors.push(`Slide ${slide.idx}: missing theme class. Every slide must include either "light" or "dark".`);
  }
  if (isHero && !hasLight && !hasDark) {
    errors.push(`Slide ${slide.idx}: hero slide must also include "light" or "dark".`);
  }
  themes.push(hasDark ? 'dark' : 'light');

  // Animation density (cover/closing slides are allowed to be lighter)
  const animCount = (slide.html.match(/\banim(?:-left|-right|-scale|-float)?\b/g) || []).length;
  if (animCount < 3 && !classes.includes('hero')) {
    warnings.push(`Slide ${slide.idx}: only ${animCount} animated elements. Consider adding .anim to kicker, title, lead, and cards.`);
  }
});

// Sequential IDs
if (ids.length) {
  ids.sort((a, b) => a - b);
  for (let i = 0; i < ids.length; i++) {
    if (ids[i] !== i + 1) {
      errors.push(`Slide IDs are not sequential: expected s${i + 1}, found s${ids[i]}.`);
      break;
    }
  }
}

// Unified light or dark is valid. Reject repeated light/dark flipping instead.
let themeTransitions = 0;
for (let i = 1; i < themes.length; i++) {
  if (themes[i] !== themes[i - 1]) themeTransitions++;
}
if (themes.length >= 4 && themeTransitions >= 3) {
  errors.push(`Theme consistency: detected ${themeTransitions} light/dark switches across ${themes.length} slides. Use a unified global tone; reserve contrast changes for intentional section boundaries.`);
}

// Whole-deck checks (ignore comments)
const stripped = html.replace(/<!--[\s\S]*?-->/g, '');

// Images
const imgTags = [...stripped.matchAll(/<img\b[^>]*>/gi)];
imgTags.forEach((m) => {
  const tag = m[0];
  if (/src="https?:\/\//i.test(tag)) {
    warnings.push('Found external image URL. Prefer local images/ folder and relative paths.');
  }
});

// Data-chart JSON
const chartMatches = [...stripped.matchAll(/data-chart="([^"]*)"/gi)];
chartMatches.forEach((m, idx) => {
  try {
    JSON.parse(m[1]);
  } catch (e) {
    errors.push(`Smart chart #${idx + 1} has invalid JSON: ${e.message}`);
  }
});

// Count-up data-value
const countUpTags = [...stripped.matchAll(/<[^>]*class="[^"]*\bcount-up\b[^"]*"[^>]*>/gi)];
countUpTags.forEach((m, idx) => {
  if (!/\bdata-value="/.test(m[0])) {
    errors.push(`Count-up element #${idx + 1} is missing data-value.`);
  }
});

// Inline bad practices
if (/height\s*:\s*100vh/i.test(stripped)) {
  errors.push('Avoid height:100vh on slide elements; use the template stage sizing.');
}
if (/box-shadow\s*:/i.test(stripped) && /frame-img/i.test(stripped)) {
  warnings.push('Images should not use inline shadows. The template handles card shadows.');
}
if (/border-radius\s*:\s*\d+px/i.test(stripped) && /frame-img/i.test(stripped)) {
  warnings.push('Images should not use inline border-radius. Use the template frame classes.');
}

// Emoji detection
const emojiRe = /[\u{1F300}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;
if (emojiRe.test(stripped)) {
  warnings.push('Detected emoji characters. Prefer Lucide icons for icons.');
}

async function runRenderedDensityGate() {
  const playwright = await loadPlaywright();
  if (!playwright?.chromium) {
    warnings.push('Rendered density gate skipped: Playwright is not resolvable. Perform and record a stable 1920×1080 browser visual review before claiming the deck is verified.');
    return;
  }

  const browser = await playwright.chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    const page = await context.newPage();
    await page.goto(pathToFileURL(path.resolve(file)).href, { waitUntil: 'domcontentloaded' });
    await Promise.race([page.evaluate(() => document.fonts?.ready), page.waitForTimeout(1800)]);
    await page.waitForTimeout(700);

    const measured = await page.evaluate(async () => {
      const slides = [...document.querySelectorAll('.slide')];
      const hidden = (el) => {
        const s = getComputedStyle(el);
        return s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) === 0;
      };
      const semanticIntervals = (container, excludeSlideChrome = false) => {
        const rect = container.getBoundingClientRect();
        const intervals = [];
        const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          const node = walker.currentNode;
          if (!node.textContent.trim()) continue;
          const parent = node.parentElement;
          if (!parent || hidden(parent) || parent.closest('.controls-bar,.deck-overview,.lightbox')) continue;
          if (excludeSlideChrome && parent.closest('.footer,.slide-footer,.page-footer,.page-number,.chrome-min,.deck-chrome')) continue;
          const range = document.createRange();
          range.selectNodeContents(node);
          for (const r of range.getClientRects()) {
            if (r.width > 3 && r.height > 3) intervals.push([Math.max(rect.top, r.top), Math.min(rect.bottom, r.bottom)]);
          }
        }
        for (const el of container.querySelectorAll('img,figure,table,pre,canvas,svg,.chart,.diagram,.flow,.visual,.media,.image,.illustration')) {
          if (hidden(el)) continue;
          if (excludeSlideChrome && el.closest('.footer,.slide-footer,.page-footer,.page-number,.chrome-min,.deck-chrome')) continue;
          const r = el.getBoundingClientRect();
          if (r.width > 3 && r.height > 3) intervals.push([Math.max(rect.top, r.top), Math.min(rect.bottom, r.bottom)]);
        }
        return intervals.filter(([a, b]) => b > a).sort((a, b) => a[0] - b[0]);
      };
      const mergeIntervals = (intervals) => {
        const merged = [];
        for (const interval of intervals) {
          const last = merged[merged.length - 1];
          if (!last || interval[0] > last[1] + 2) merged.push([...interval]);
          else last[1] = Math.max(last[1], interval[1]);
        }
        return merged;
      };
      const panelCandidates = (slide) => [...slide.querySelectorAll('[data-panel],div,section,article,aside')].filter((el) => {
        if (el === slide || el.closest('.controls-bar,.deck-overview,.lightbox')) return false;
        const cls = typeof el.className === 'string' ? el.className : '';
        const named = el.hasAttribute('data-panel') || /(?:^|[-_\s])(card|panel|metric|deliverable|insight)(?:$|[-_\s])/.test(cls);
        if (!named || el.hasAttribute('data-panel-gap-ok')) return false;
        const r = el.getBoundingClientRect();
        if (r.width < 220 || r.height < 220) return false;
        const s = getComputedStyle(el);
        const hasSurface = s.backgroundImage !== 'none' || !['rgba(0, 0, 0, 0)', 'transparent'].includes(s.backgroundColor) ||
          ['Top', 'Right', 'Bottom', 'Left'].some((side) => parseFloat(s[`border${side}Width`]) > 0 && s[`border${side}Style`] !== 'none') || s.boxShadow !== 'none';
        return hasSurface && !hidden(el);
      });
      const out = [];
      const hollowPanels = [];
      const interSectionGaps = [];
      let cover = null;
      for (let index = 0; index < slides.length; index++) {
        const slide = slides[index];
        slides.forEach((s, i) => {
          s.classList.toggle('active', i === index);
          s.style.visibility = i === index ? 'visible' : 'hidden';
          s.style.opacity = i === index ? '1' : '0';
        });
        await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        await new Promise((resolve) => setTimeout(resolve, 700));
        const root = slide.getBoundingClientRect();
        const slideIntervals = mergeIntervals(semanticIntervals(slide, true));
        const top = slideIntervals.length ? Math.max(root.top, slideIntervals[0][0]) : root.top;
        const bottom = slideIntervals.length ? Math.min(root.bottom, slideIntervals[slideIntervals.length - 1][1]) : root.top;
        const ratio = root.height ? (bottom - top) / root.height : 0;
        const bottomGap = Math.max(0, root.bottom - bottom);
        const exempt = slide.dataset.densityExempt || '';
        out.push({ index: index + 1, ratio, bottomGap, exempt, count: slideIntervals.length });

        if (!exempt && slideIntervals.length > 1) {
          let largestGap = null;
          for (let i = 1; i < slideIntervals.length; i++) {
            const from = slideIntervals[i - 1][1];
            const to = slideIntervals[i][0];
            const gap = to - from;
            if (!largestGap || gap > largestGap.gap) largestGap = { gap, from, to };
          }
          if (largestGap && largestGap.gap > 160 && largestGap.gap / root.height > 0.14) {
            interSectionGaps.push({
              slide: index + 1,
              gap: largestGap.gap,
              ratio: largestGap.gap / root.height,
              from: largestGap.from - root.top,
              to: largestGap.to - root.top,
            });
          }
        }

        if (index === 0 && (slide.classList.contains('hero') || slide.classList.contains('cover') || slide.dataset.densityExempt === 'cover')) {
          const subject = slide.querySelector('[data-cover-subject]');
          if (subject) {
            const intervals = mergeIntervals(semanticIntervals(subject));
            if (intervals.length) {
              const subjectTop = intervals[0][0];
              const subjectBottom = intervals[intervals.length - 1][1];
              const safeTop = root.top + 80;
              const safeBottom = root.bottom - 130;
              const safeCenter = (safeTop + safeBottom) / 2;
              const offsetRatio = Math.abs((subjectTop + subjectBottom) / 2 - safeCenter) / (safeBottom - safeTop);
              cover = { offsetRatio, subjectTop: subjectTop - root.top, subjectBottom: subjectBottom - root.top };
            } else {
              cover = { offsetRatio: null, subjectTop: null, subjectBottom: null };
            }
          }
        }

        for (const panel of panelCandidates(slide)) {
          const r = panel.getBoundingClientRect();
          const s = getComputedStyle(panel);
          const top = r.top + parseFloat(s.paddingTop || 0);
          const bottom = r.bottom - parseFloat(s.paddingBottom || 0);
          const intervals = mergeIntervals(semanticIntervals(panel).map(([a, b]) => [Math.max(top, a), Math.min(bottom, b)]).filter(([a, b]) => b > a));
          let maxGap = intervals.length ? Math.max(0, intervals[0][0] - top, bottom - intervals[intervals.length - 1][1]) : bottom - top;
          for (let i = 1; i < intervals.length; i++) maxGap = Math.max(maxGap, intervals[i][0] - intervals[i - 1][1]);
          const innerHeight = Math.max(1, bottom - top);
          if (maxGap > 180 && maxGap / innerHeight > 0.28) {
            const label = panel.getAttribute('data-panel') || (typeof panel.className === 'string' ? panel.className.trim().replace(/\s+/g, '.') : panel.tagName.toLowerCase());
            hollowPanels.push({ slide: index + 1, label: label || panel.tagName.toLowerCase(), maxGap, ratio: maxGap / innerHeight });
          }
        }
      }
      slides.forEach((s, i) => {
        s.style.visibility = '';
        s.style.opacity = '';
        s.classList.toggle('active', i === 0);
      });
      return { density: out, cover, hollowPanels, interSectionGaps };
    });

    for (const m of measured.density) {
      if (m.exempt && !['cover', 'closing', 'divider'].includes(m.exempt)) {
        errors.push(`Slide ${m.index}: invalid data-density-exempt="${m.exempt}". Only cover, closing, or divider are permitted.`);
      }
      if (!m.exempt && m.count === 0) {
        errors.push(`Slide ${m.index}: density gate found no meaningful visible content.`);
      }
      if (!m.exempt && m.ratio < 0.72 && m.bottomGap > 170) {
        errors.push(`Slide ${m.index}: density gate failed — meaningful content occupies ${Math.round(m.ratio * 100)}% of stage height with ${Math.round(m.bottomGap)}px lower blank space. Add meaningful visual content or redesign the composition; do not stretch empty panels.`);
      }
    }
    if (firstSlideIsCover && firstSlideHasCoverSubject) {
      if (!measured.cover || measured.cover.offsetRatio === null) {
        errors.push('Slide 1: data-cover-subject contains no measurable semantic content. Put the real title, narrative copy, and supporting data/visuals inside it.');
      } else if (measured.cover.offsetRatio > 0.08) {
        errors.push(`Slide 1: cover subject is not visually centered — semantic group spans y=${Math.round(measured.cover.subjectTop)}..${Math.round(measured.cover.subjectBottom)} and its center is ${Math.round(measured.cover.offsetRatio * 100)}% of the safe-area height away from center (maximum 8%). Remove top/bottom spacer pressure and center the combined subject group.`);
      }
    }
    for (const panel of measured.hollowPanels) {
      errors.push(`Slide ${panel.slide}: hollow panel "${panel.label}" has a ${Math.round(panel.maxGap)}px continuous blank band (${Math.round(panel.ratio * 100)}% of its inner height). Remove stretched height/space-between, regroup the content, or add meaningful visual information.`);
    }
    for (const gap of measured.interSectionGaps) {
      errors.push(`Slide ${gap.slide}: inter-section dead zone spans y=${Math.round(gap.from)}..${Math.round(gap.to)} — ${Math.round(gap.gap)}px (${Math.round(gap.ratio * 100)}% of stage height). Tighten header-to-content/grid spacing, remove empty rows/spacers, or add meaningful connecting content; bottom-aligned panels do not compensate for a hollow middle.`);
    }
    await context.close();
  } finally {
    await browser.close();
  }
}

await runRenderedDensityGate();

// Print results
if (errors.length) {
  console.error(`\n❌ ${errors.length} error(s) found in ${file}:\n`);
  errors.forEach((e) => console.error('  • ' + e));
}
if (warnings.length) {
  console.warn(`\n⚠️ ${warnings.length} warning(s) in ${file}:\n`);
  warnings.forEach((w) => console.warn('  • ' + w));
}
if (!errors.length && !warnings.length) {
  console.log(`\n✅ Fluid-layout deck validation passed for ${file}.`);
  process.exit(0);
}
process.exit(errors.length ? 1 : 0);
