# Style Presets Reference

Curated visual styles for Frontend Slides. Each preset is inspired by real design references — no generic "AI slop" aesthetics. **Abstract shapes only — no illustrations.**

**Viewport CSS:** For mandatory base styles, see [viewport-base.css](viewport-base.css). Include in every presentation.

**Core Presentation Rules**:
1. **Dual-Track Header & Cover Spacing Standard (双轨间距规范：首页舒展大气 ↔ 正文紧凑空间让渡)**:
   - **仅首页 PPT / 封面页 (Cover Slide / Hero Slide)**: 豁免紧凑压缩，采用开阔舒展的纵向呼吸排版。Badge-to-Title: `16px ~ 28px`，Title-to-Subtitle: `20px ~ 32px`，Subtitle-to-Bottom: `36px ~ 56px`，营造大气大格局的门面视觉。
   - **正文内容页 (Content Slides)**: 严格执行页眉三要素紧凑压缩，Badge (`.eyebrow-pill` / `.kicker`)、主标题 (`.slide-title` / `.h-xl`) 和副标题 (`.slide-subtitle` / `.lead`) 紧凑编排，总高度 `<= 200px` (18%~22% 画布高)，Badge-to-Title `6~8px`，Title-to-Subtitle `8~12px`，Subtitle-to-Body `16~24px`，确保 78%+ 黄金垂直空间留给卡片与图表内容。
2. **Mandatory 4 Controls Bar & Overview Modal (底栏四件套与全景模式)**: Every presentation must include `.controls-bar` (`◀ 上一页`, `01 / N`, `下一页 ▶`, `🗂 全览`, `⛶ 全屏`) and `#overviewModal` with full keyboard shortcuts (`←`/`→`/`Space` 翻页, `O` 全览, `F` 全屏, `Esc` 退出).
3. **High-Legibility Large Font Standard (主要内容大字号高可读性规范 · NON-NEGOTIABLE)**: 杜绝 12px~14px 细碎小字感。在 1920×1080 舞台下，所有生成页面必须遵循大字号标准阶梯：
   - **分类徽章/Pill** (`.eyebrow-pill` / `.kicker`): `16px ~ 18px` (font-weight: 800)
   - **主标题** (`.slide-title` / `.h-xl`): `48px ~ 54px` (font-weight: 800/900, line-height: 1.15)
   - **副标题/金句** (`.slide-subtitle` / `.lead`): `22px ~ 26px` (font-weight: 600, line-height: 1.5)
   - **卡片/分栏标题** (`.b-card h3` / `.card-title`): `26px ~ 28px` (font-weight: 800)
   - **卡片正文/段落** (`.b-card p` / `.card-text` / `p`): `20px ~ 22px` (line-height: 1.62)
   - **列表项/Bullet Items** (`.b-card li` / `.feature-desc`): `19px ~ 21px` (line-height: 1.6)
   - **数据大数字** (`.stat-nb`): `56px ~ 72px`, **数据标签** (`.stat-label`): `16px ~ 18px` (font-weight: 700)
   - **表格** (`.data-table`): `th: 21px` (font-weight: 800) / `td: 20px` (line-height: 1.5)
   - **代码块** (`.code-block`): `19px ~ 21px` (line-height: 1.65)
   - **底栏控制台** (`.ctrl-btn` / `.slide-counter`): `16px` (font-weight: 700/800)
4. **Inline Icon, Badge & Title Standard (图片/图标/序号徽章与文字单行同行并排规范 · NON-NEGOTIABLE)**:
   - 在卡片（`.card` / `.b-card` / `.feat-card`）、架构层级（`.stack-row` / `.tier-card`）、流水线步骤（`.pipeline-step` / `.step`）等组件中，**图标、Emoji、图片或序号徽章必须与对应的标题文字处于同一行展示**（水平弹性盒 `display: flex; align-items: center; gap: 10px~14px;` 或在 `<h3>` 内前置 `<span class="badge">` / `<span class="icon-box">`），严禁无故分两行上下堆叠。
   - **豁免与折行例外 (Exemption Rule)**：除非在极限窄栏或超长标题文字场景下，图片/图标与文字在一行内确实放不下导致溢出，才可酌情折行拆为两行展示。
5. **Unified Global Color Tone Standard (全局色彩基调统一与防频闪规范 · NON-NEGOTIABLE)**:
   - 整套演示文稿必须保持全局色彩世界观的高度纯净与一致，**默认全套采用 100% 统一纯深色（Unified Dark Mode）或 100% 统一纯浅色（Unified Light Mode）**。
   - **严禁逐页黑白无故交替闪烁（Anti-Pattern: 严禁一页深一页浅交替）**。唯一豁免结构：长篇大型演说中允许仅对封面/封底/章节过渡大幕页采用深色聚焦，而正文内容页（90%+）必须保持绝对统一的底色基调。

---

## Dark Themes

### 1. Bold Signal

**Vibe:** Confident, bold, modern, high-impact

**Layout:** Colored card on dark gradient. Number top-left, navigation top-right, title bottom-left.

**Typography:**
- Display: `Archivo Black` (900)
- Body: `Space Grotesk` (400/500)

**Colors:**
```css
:root {
    --bg-primary: #1a1a1a;
    --bg-gradient: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
    --card-bg: #FF5722;
    --text-primary: #ffffff;
    --text-on-card: #1a1a1a;
}
```

**Signature Elements:**
- Bold colored card as focal point (orange, coral, or vibrant accent)
- Large section numbers (01, 02, etc.)
- Navigation breadcrumbs with active/inactive opacity states
- Grid-based layout for precise alignment

---

### 2. Electric Studio

**Vibe:** Bold, clean, professional, high contrast

**Layout:** Split panel—white top, blue bottom. Brand marks in corners.

**Typography:**
- Display: `Manrope` (800)
- Body: `Manrope` (400/500)

**Colors:**
```css
:root {
    --bg-dark: #0a0a0a;
    --bg-white: #ffffff;
    --accent-blue: #4361ee;
    --text-dark: #0a0a0a;
    --text-light: #ffffff;
}
```

**Signature Elements:**
- Two-panel vertical split
- Accent bar on panel edge
- Quote typography as hero element
- Minimal, confident spacing

---

### 3. Creative Voltage

**Vibe:** Bold, creative, energetic, retro-modern

**Layout:** Split panels—electric blue left, dark right. Script accents.

**Typography:**
- Display: `Syne` (700/800)
- Mono: `Space Mono` (400/700)

**Colors:**
```css
:root {
    --bg-primary: #0066ff;
    --bg-dark: #1a1a2e;
    --accent-neon: #d4ff00;
    --text-light: #ffffff;
}
```

**Signature Elements:**
- Electric blue + neon yellow contrast
- Halftone texture patterns
- Neon badges/callouts
- Script typography for creative flair

---

### 4. Dark Botanical

**Vibe:** Elegant, sophisticated, artistic, premium

**Layout:** Centered content on dark. Abstract soft shapes in corner.

**Typography:**
- Display: `Cormorant` (400/600) — elegant serif
- Body: `IBM Plex Sans` (300/400)

**Colors:**
```css
:root {
    --bg-primary: #0f0f0f;
    --text-primary: #e8e4df;
    --text-secondary: #9a9590;
    --accent-warm: #d4a574;
    --accent-pink: #e8b4b8;
    --accent-gold: #c9b896;
}
```

**Signature Elements:**
- Abstract soft gradient circles (blurred, overlapping)
- Warm color accents (pink, gold, terracotta)
- Thin vertical accent lines
- Italic signature typography
- **No illustrations—only abstract CSS shapes**

---

## Light Themes

### 5. Notebook Tabs

**Vibe:** Editorial, organized, elegant, tactile

**Layout:** Cream paper card on dark background. Colorful tabs on right edge.

**Typography:**
- Display: `Bodoni Moda` (400/700) — classic editorial
- Body: `DM Sans` (400/500)

**Colors:**
```css
:root {
    --bg-outer: #2d2d2d;
    --bg-page: #f8f6f1;
    --text-primary: #1a1a1a;
    --tab-1: #98d4bb; /* Mint */
    --tab-2: #c7b8ea; /* Lavender */
    --tab-3: #f4b8c5; /* Pink */
    --tab-4: #a8d8ea; /* Sky */
    --tab-5: #ffe6a7; /* Cream */
}
```

**Signature Elements:**
- Paper container with subtle shadow
- Colorful section tabs on right edge (vertical text)
- Binder hole decorations on left
- Tab text must scale with viewport: `font-size: clamp(0.5rem, 1vh, 0.7rem)`

---

### 6. Pastel Geometry

**Vibe:** Friendly, organized, modern, approachable

**Layout:** White card on pastel background. Vertical pills on right edge.

**Typography:**
- Display: `Plus Jakarta Sans` (700/800)
- Body: `Plus Jakarta Sans` (400/500)

**Colors:**
```css
:root {
    --bg-primary: #c8d9e6;
    --card-bg: #faf9f7;
    --pill-pink: #f0b4d4;
    --pill-mint: #a8d4c4;
    --pill-sage: #5a7c6a;
    --pill-lavender: #9b8dc4;
    --pill-violet: #7c6aad;
}
```

**Signature Elements:**
- Rounded card with soft shadow
- **Vertical pills on right edge** with varying heights (like tabs)
- Consistent pill width, heights: short → medium → tall → medium → short
- Download/action icon in corner

---

### 7. Split Pastel

**Vibe:** Playful, modern, friendly, creative

**Layout:** Two-color vertical split (peach left, lavender right).

**Typography:**
- Display: `Outfit` (700/800)
- Body: `Outfit` (400/500)

**Colors:**
```css
:root {
    --bg-peach: #f5e6dc;
    --bg-lavender: #e4dff0;
    --text-dark: #1a1a1a;
    --badge-mint: #c8f0d8;
    --badge-yellow: #f0f0c8;
    --badge-pink: #f0d4e0;
}
```

**Signature Elements:**
- Split background colors
- Playful badge pills with icons
- Grid pattern overlay on right panel
- Rounded CTA buttons

---

### 8. Vintage Editorial

**Vibe:** Witty, confident, editorial, personality-driven

**Layout:** Centered content on cream. Abstract geometric shapes as accent.

**Typography:**
- Display: `Fraunces` (700/900) — distinctive serif
- Body: `Work Sans` (400/500)

**Colors:**
```css
:root {
    --bg-cream: #f5f3ee;
    --text-primary: #1a1a1a;
    --text-secondary: #555;
    --accent-warm: #e8d4c0;
}
```

**Signature Elements:**
- Abstract geometric shapes (circle outline + line + dot)
- Bold bordered CTA boxes
- Witty, conversational copy style
- **No illustrations—only geometric CSS shapes**

---

## Specialty Themes

### 9. Neon Cyber

**Vibe:** Futuristic, techy, confident

**Typography:** `Clash Display` + `Satoshi` (Fontshare)

**Colors:** Deep navy (#0a0f1c), cyan accent (#00ffcc), magenta (#ff00aa)

**Signature:** Particle backgrounds, neon glow, grid patterns

---

### 10. Terminal Green

**Vibe:** Developer-focused, hacker aesthetic

**Typography:** `JetBrains Mono` (monospace only)

**Colors:** GitHub dark (#0d1117), terminal green (#39d353)

**Signature:** Scan lines, blinking cursor, code syntax styling

---

### 11. Swiss Modern

**Vibe:** Clean, precise, Bauhaus-inspired

**Typography:** `Archivo` (800) + `Nunito` (400)

**Colors:** Pure white, pure black, red accent (#ff3300)

**Signature:** Visible grid, asymmetric layouts, geometric shapes

---

### 12. Paper & Ink

**Vibe:** Editorial, literary, thoughtful

**Typography:** `Cormorant Garamond` + `Source Serif 4`

**Colors:** Warm cream (#faf9f7), charcoal (#1a1a1a), crimson accent (#c41e3a)

**Signature:** Drop caps, pull quotes, elegant horizontal rules

---

## Font Pairing Quick Reference

| Preset | Display Font | Body Font | Source |
|--------|--------------|-----------|--------|
| Bold Signal | Archivo Black | Space Grotesk | Google |
| Electric Studio | Manrope | Manrope | Google |
| Creative Voltage | Syne | Space Mono | Google |
| Dark Botanical | Cormorant | IBM Plex Sans | Google |
| Notebook Tabs | Bodoni Moda | DM Sans | Google |
| Pastel Geometry | Plus Jakarta Sans | Plus Jakarta Sans | Google |
| Split Pastel | Outfit | Outfit | Google |
| Vintage Editorial | Fraunces | Work Sans | Google |
| Neon Cyber | Clash Display | Satoshi | Fontshare |
| Terminal Green | JetBrains Mono | JetBrains Mono | JetBrains |

---

## DO NOT USE (Generic AI Patterns)

**Fonts:** Inter, Roboto, Arial, system fonts as display

**Colors:** `#6366f1` (generic indigo), purple gradients on white

**Layouts:** Everything centered, generic hero sections, identical card grids

**Decorations:** Realistic illustrations, gratuitous glassmorphism, drop shadows without purpose

---

## CSS Gotchas

### Negating CSS Functions

**WRONG — silently ignored by browsers (no console error):**
```css
right: -clamp(28px, 3.5vw, 44px);   /* Browser ignores this */
margin-left: -min(10vw, 100px);      /* Browser ignores this */
```

**CORRECT — wrap in `calc()`:**
```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));  /* Works */
margin-left: calc(-1 * min(10vw, 100px));     /* Works */
```

CSS does not allow a leading `-` before function names. The browser silently discards the entire declaration — no error, the element just appears in the wrong position. **Always use `calc(-1 * ...)` to negate CSS function values.**
