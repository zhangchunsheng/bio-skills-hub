# Font Stack Fallback Contract (字体回退契约)

This document is the canonical fallback policy for every `design.md` in this skill.
Any template that ignores it is considered non-compliant and will be flagged by
`scripts/diagnose-deck.mjs` (planned, see module plan).

The goal: when Google Fonts is blocked, slow, or partially loaded (very common
on Chinese mainland / corporate intranets), the page MUST still display all text
using a chain of locally available system fonts, without invisible glyphs, FOUT
flashes longer than 500ms, or layout shifts larger than one line.

---

## 1. Mandatory Web-Font Loading Directives

Every `design.md` that imports Google Fonts / Fontshare MUST ship the link tag
with these three attributes verbatim:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link
  href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap"
  rel="stylesheet">
```

Key rules:

- `display=swap` is **non-negotiable**. The browser must use the fallback font
  immediately and swap in the web font when ready. `display=block` is forbidden
  because it leaves a 3-second blank-text period on slow networks.
- The `preconnect` to `fonts.gstatic.com` is required so the actual font files
  start downloading in parallel with the CSS parse.
- `crossorigin` on the second `preconnect` is required; without it the browser
  cannot reuse the connection.

If the user is in a known-blocked network, the agent SHOULD swap the URL to
the mirror documented in `designs/cdn-mirrors.md` before generating the HTML.

---

## 2. Canonical Font Stacks (字体回退栈)

Use these stacks verbatim in the `:root` CSS variable definitions. The order is
load-bearing: the first match wins, and the order must put a web font first only
if it has been preloaded or has `display=swap`.

### 2.1 Display / Heading Stacks

| Use case | Stack (paste verbatim) |
| :--- | :--- |
| Latin display (Outfit, Inter, Manrope) | `'Outfit', 'Inter', 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', 'Source Han Sans SC', 'Noto Sans SC', sans-serif` |
| Editorial serif (for Emerald / Vintage) | `'Fraunces', 'Playfair Display', 'Source Han Serif SC', 'Songti SC', 'SimSun', serif` |
| Mono / code (for Monochrome / 8-Bit) | `'JetBrains Mono', 'Fira Code', 'SF Mono', 'Consolas', 'PingFang SC', monospace` |

### 2.2 Body Stack (single canonical chain)

```css
--font-body: 'Plus Jakarta Sans', 'Inter', 'PingFang SC', 'Microsoft YaHei',
             'Source Han Sans SC', 'Noto Sans SC', system-ui, -apple-system,
             'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

This stack is the only acceptable body font declaration. Reasons:

- `Plus Jakarta Sans` and `Inter` carry the modern look and degrade cleanly
  to each other.
- `PingFang SC` (macOS) to `Microsoft YaHei` (Windows) to `Source Han Sans SC`
  (Linux) guarantees a Chinese-readable face on any mainstream OS.
- `system-ui` and `-apple-system` give the OS-native face as a last resort so
  the page is never typeset in a serif default.
- `Noto Sans SC` is included as a final safe harbor for Linux servers and
  CI-rendered screenshots.

### 2.3 Forbidden Substitutions

The following are explicitly **NOT** allowed in the font stack because they
visibly break the design:

- `'Times New Roman'` or generic `serif` for body text (looks like a Word doc)
- Pure `'sans-serif'` without any Chinese family (Chinese text falls back to
  the OS default which is inconsistent)
- `'Helvetica'` without a Chinese family (the Chinese text on Windows becomes
  `SimSun`, which clashes with Helvetica)
- Any `font-family` shorter than 4 entries in the body stack

---

## 3. Weight Mapping (字重映射)

Outfit / Plus Jakarta Sans ship weights 400-800. Local Chinese fonts do not. The
agent MUST keep weights honest so the fallback face does not suddenly become
bolder or lighter:

| Declared weight | PingFang SC | Microsoft YaHei | Source Han Sans SC |
| :--- | :--- | :--- | :--- |
| 400 | Regular | Regular | Regular |
| 500 | Medium | - (fallback to Regular) | Medium |
| 600 | Semibold | - (fallback to Regular) | Semibold |
| 700 | Semibold | Bold | Bold |
| 800 | Heavy | Bold | Heavy |
| 900 | Heavy | Black | Heavy |

In practice this means: **do not use weight 500 or 600 on Microsoft YaHei
machines**. The visual will look like a font drop. When the agent is confident
the audience is on Windows, declare weights in 400/700/900 only.

---

## 4. Failure Mode & User-Visible Fallback

### 4.1 Initial degradation

If `document.fonts.ready` does not resolve within **2500ms**, the agent-injected
runtime (see `template.html` P0 patch) MUST:

1. Show a small dismissible banner: **"字体加载超时，正在重试…"**
2. Force re-apply the local stack by adding a class `font-fallback` to `<html>`.
   This class strips any `letter-spacing` heavier than `-0.02em` and forces
   `font-feature-settings: normal` so Chinese punctuation does not look squished.
3. Keep the page fully readable. **Never** hide text while waiting for a web
   font.

### 4.2 Auto-retry ladder (recovery before giving up)

A flaky network must not lock the page into the system-font fallback. After
the initial 2.5s timeout, the runtime MUST attempt recovery on this ladder:

- **+5s** — Timer 1: re-attach a fresh `<link rel="stylesheet" href="…?retry=…">`
  with a cache-buster, race `document.fonts.ready` against a 4s timeout.
- **+12s** — Timer 2: same probe.
- **+25s** — Timer 3: same probe. If still failing, transition to **failed**
  state (see §4.3).
- **`window.online` event** — Immediate: same probe; fires the moment the
  browser regains connectivity without waiting for the next scheduled timer.

On the first successful probe:

- Remove the `font-fallback` class from `<html>`.
- Cancel all remaining retry timers.
- Update the banner to **"字体已恢复加载"** and auto-hide it after 2.5s.

### 4.3 Terminal state

After Timer 3 fails (or the page has been in fallback for ~30s with no
`online` event), the runtime transitions to a **failed** state and shows:

**"字体加载失败，已使用本地系统字体"**

This state is terminal: no further retries are attempted. The banner stays
until the user dismisses it. The local system stack remains in effect.

### 4.4 Detection contract

The runtime is only armed when the template includes a link tag with
`data-fonts-css="…"` in `<head>`. If no such link is present, the runtime is
a no-op. This is what lets `template.html` (system-fonts-only) coexist with
`template-beautiful.html` / `template-swiss.html` (web fonts) using the same
shared runtime.

```css
.font-fallback body,
.font-fallback .slide,
.font-fallback .b-card,
.font-fallback .card,
.font-fallback p,
.font-fallback h1,
.font-fallback h2,
.font-fallback h3 {
  letter-spacing: 0 !important;
  font-feature-settings: normal !important;
  font-family: var(--font-body) !important;
}
```

---

## 5. Self-Test in Template

The `template.html` P0 patch includes a self-test snippet (appended near the
end of `<body>`) that runs once on `DOMContentLoaded`. The auto-retry ladder
from §4.2 is wired in here:

```js
// P0 reliability runtime - font auto-retry. See §4.1-4.3 for the policy.
(function () {
  var banner = document.getElementById('degrade-banner');
  // ... banner state machine ...
  function guardFonts() {
    var link = document.querySelector('link[data-fonts-css]');
    if (!link || !document.fonts) return;
    // FONT_RETRY_DELAYS = [5000, 12000, 25000]; FONT_LOAD_TIMEOUT_MS = 4000
    // On 2.5s timeout: setState('fallback') -> pushReason('正在重试…')
    //   + schedule FONT_RETRY_DELAYS timers + listen for 'online'.
    // On successful probe: setState('recovered') -> remove .font-fallback,
    //   clear timers, show '字体已恢复加载' for 2.5s, then auto-hide.
    // On all retries exhausted: setState('failed') -> '字体加载失败，已使用本地系统字体'.
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', guardFonts);
  } else {
    guardFonts();
  }
})();
```

If a future template chooses to skip Google Fonts entirely (e.g. a
"chinese-native" template that just uses `Source Han Sans SC`), it MUST still
ship this snippet with `result === 'timeout'` unreachable, so the banner code
path is always wired up.

---

## 6. Local Vendor Fallback (Last Resort)

For users on fully air-gapped networks, the agent SHOULD copy the following
files into a `vendor/fonts/` sibling directory next to the generated HTML and
update the `font-family` declaration to use local `url()` first:

```
vendor/fonts/Outfit-Regular.woff2
vendor/fonts/Outfit-Bold.woff2
vendor/fonts/PlusJakartaSans-Regular.woff2
vendor/fonts/PlusJakartaSans-Bold.woff2
vendor/fonts/NotoSansSC-Regular.woff2
vendor/fonts/NotoSansSC-Bold.woff2
```

`@font-face` declarations SHOULD sit in the generated HTML's `<style>` block
above all other styles, so they win over any system fallback.

This path is documented here but not yet automated by the skill; a future
iteration of `scripts/diagnose-deck.mjs` will offer to vendorize fonts when it
detects the user is on a fully air-gapped network.
