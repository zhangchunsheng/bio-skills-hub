# Generate HTML PPT

An AI Coding-Agent Skill for creating stunning, interactive HTML presentations — built from scratch or converted from PowerPoint (`.pptx`) files. Designed for local AI coding assistants (such as Claude Code, Antigravity, Gemini CLI, Codex, etc.), it features a **Design System Specification (`design.md`) architecture**, **35+ distinct visual style presets (Bold Template Pack)**, a fixed 16:9 stage with Seamless Viewport background synchronization, dual-window presenter view, and rich interactive components.

---

![Generate HTML PPT Demo](https://github.com/helloyxs/generate-html-ppt/blob/main/demo/beautiful-demo.gif)

![Generate HTML PPT Demo](https://github.com/helloyxs/generate-html-ppt/blob/main/demo/风格选择.gif)

---

## 🌟 Key Features

**Generate HTML PPT** empowers AI agents to break free from generic templates and AI output bottlenecks. Without writing manual CSS/JS code, you can produce web-based presentations with premium design aesthetics, true WYSIWYG responsive scaling, and rich interactivity.

### 1. 🎨 35+ Aesthetic Design Recipes (Bold Template Pack)
* **Comprehensive Style Library**: Access over 35+ distinct visual design systems (`design.md`), including *Beautiful Modern*, *Swiss International*, *Cyberpunk Dark*, *8-Bit Orbit*, *Emerald Editorial*, *Retro Zine*, *Neo Grid Bold*, *Monochrome*, *Pastel Geometry*, and *Vintage Editorial*.
* **No Generic AI Aesthetic**: Each recipe defines curated Google/Fontshare typography stacks, color tokens, elevation shadows, fluid type scales, and micro-animations — avoiding plain blue/purple gradients and default system fonts.

### 2. 📺 Fixed 16:9 Stage & Seamless Viewport Protocol
* **Fixed 16:9 Stage**: Authored at a baseline resolution of `1920×1080` pixels. Dynamic JavaScript (`updateScale()`) and CSS `transform` scale the entire stage uniformly to fit any viewport size. Content never reflows or breaks across laptops, tablets, or 4K projectors.
* **Seamless Viewport Fusion**: Synchronizes the outer screen background with the active slide's background in real-time using CSS variables (`--viewport-bg`) and dynamic JavaScript (`updateViewportBg()`), eliminating awkward letterbox contrast.

### 3. 🎯 Progressive Disclosure Architecture
* **Token-Efficient Agent Workflow**: The AI agent avoids loading hundreds of KB of template files at once. It first reads `designs/bold-template-pack/selection-index.json` (lightweight metadata) to select a style, and only reads the specific template's single `design.md` file once confirmed by the user.

### 4. 🔀 Three Operating Modes
* **Mode A: Create Deck from Scratch** — Complete workflow covering requirements alignment, visual style previewing, brand asset sniffing, narrative arc outline, wireframe confirmation, and content batch filling.
* **Mode B: PowerPoint Conversion** — Includes a Python parser (`extract-pptx.py`) that extracts slide text, shapes, high-resolution images, and speaker notes from `.pptx` files, converting legacy decks to the web effortlessly.
* **Mode C: Multi-Platform Cover Generation** — Extracts core slide takeaways and generates social media cover prompts/visuals for WeChat (21:9), Xiaohongshu (3:4), X/Twitter, or newsletters.

### 5. 🚀 Zero Dependencies & Single-File Output
* Generates a single, self-contained HTML file with inline CSS and JavaScript logic (plus CDN fallbacks). No Node.js runtime, npm dependencies, or build step required. Works instantly offline and stays readable for decades.

### 6. 📊 Rich UI Component Kit & Data Visualization
* Built-in support for interactive **ECharts charts**, **Mermaid.js vector diagrams**, **syntax highlighting**, **number count-up animations (`.count-up`)**, and **spring physics entry animations (`.anim`)**.

### 7. 🎛️ Bottom Controls & Overview Gallery Mode
* Every presentation automatically comes equipped with a floating glassmorphism bottom bar containing **`◀ Previous`**, **`Slide Counter & Progress`**, **`Next ▶`**, **`🗂 Overview`**, and **`⛶ Fullscreen`** buttons. Includes instant slide thumbnail grid navigation (`O` for Overview, `F` for Fullscreen, `Esc` to close) paired with **Dual-Track Spacing Standards** (spacious breathing room on Cover Slides ↔ compact header compression on Content Slides) yielding 78%+ vertical canvas space for main content.

### 8. 🔤 High-Legibility Large Font Standard
* Eliminates tiny, illegible 12px~14px text. Under the 1920×1080 canvas stage, all typography is tuned for speech presentation clarity: Body Paragraphs `20px~22px`, Subtitles `22px~26px`, Card Titles `26px~28px`, Badges `16px~18px`, Big Stats `56px~72px`, Tables & Code `19px~21px` — ensuring effortless reading across both large projection screens and scaled laptop viewports.

### 9. 🔍 Default Double-Click Image Zoom & Lightbox
* Built-in interactive fullscreen image lightbox: Any image across the presentation **supports double-clicking (`dblclick`) to zoom and enlarge into a backdrop-blurred lightbox overlay**. Double-click again, click anywhere, or press `Esc` to close; multi-image slides support fluid keyboard `←` / `→` arrow navigation.

### 10. 🏷️ Inline Icon, Badge & Title Standard
* In cards, pipeline steps, architecture layers, and feature grids, icons, emojis, images, or numerical badges stay horizontally aligned on the same row with their paired title text by default, eliminating unnecessary two-line vertical stacking and wasted canvas height. Graceful two-line wrapping is reserved exclusively for narrow columns or exceptionally long text.

---

## 📂 Project Structure

Optimized for modular AI agent workflows:

```text
generate-html-ppt/
├── SKILL.md                  # Master workflow guide and instructions for AI agents
├── README.md                 # Chinese documentation
├── README_en.md              # English documentation
├── designs/                  # Design System Specification library
│   ├── bold-template-pack/   # Collection of 35+ design style presets
│   │   ├── selection-index.json # Lightweight index for style selection
│   │   ├── deck-stage.js     # Stage scaling & viewport sync engine
│   │   └── templates/        # 35+ template design recipes (design.md)
│   ├── viewport-base.css     # Base 16:9 stage & seamless viewport CSS
│   ├── STYLE_PRESETS.md      # Core visual theme reference
│   └── animation-patterns.md # Micro-interactions & animation guide
├── references/               # Agent reference handbooks
│   ├── checklist.md          # Presentation quality checklist
│   ├── screenshot-framing.md # Software screenshot framing & mockup guide
│   ├── image-prompts.md      # AI image prompt generation guide
│   └── covers.md             # Social media cover design guidelines
├── resources/                # Base HTML templates and high-res assets
│   ├── template.html         # Cyberpunk base template
│   ├── template-swiss.html   # Swiss International base template
│   ├── template-beautiful.html # Beautiful.ai base template
│   └── screenshot-backgrounds/
└── scripts/                  # Helper scripts
    ├── extract-pptx.py       # Python script to extract slides, images, and notes from PPTX
    ├── validate-swiss-deck.mjs # Strict Node.js validation script for Swiss layout
    └── validate-fluid-deck.mjs # Validation script for fluid layouts (Beautiful Modern / Cyberpunk Dark)
```

---

## 🛠️ Installation

### 1-Click Install via AI Assistant (Recommended)
Ask your AI coding assistant (Claude Code, Antigravity, Gemini CLI, Codex, etc.) to install the skill automatically:

```text
Install a specific release or reviewed commit of `helloyxs/generate-html-ppt` as a local skill. Verify the repository URL and commit SHA against this guide first, then install `python-pptx` only if Mode B is needed.
```

### Manual Install for Claude Code

```bash
# 1. Clone repository to your Claude skills directory
git clone https://github.com/helloyxs/generate-html-ppt.git ~/.claude/skills/generate-html-ppt
git -C ~/.claude/skills/generate-html-ppt checkout --detach 3167cd6a3cd2e9901e113c6e3ae728385e92f36d

# 2. Install Python dependency (required for PPTX conversion in Mode B)
pip install python-pptx
```

### Manual Install for Codex / Antigravity

```bash
# 1. Clone repository to your agent's skills directory
git clone https://github.com/helloyxs/generate-html-ppt.git ~/.codex/skills/generate-html-ppt
git -C ~/.codex/skills/generate-html-ppt checkout --detach 3167cd6a3cd2e9901e113c6e3ae728385e92f36d

# 2. Install Python dependency
pip install python-pptx
```

During chat, simply pass `SKILL.md` or instruct your agent: "Load and follow `~/.claude/skills/generate-html-ppt/SKILL.md`".

---

## 💡 Usage Guidelines

### 1. Create a New Presentation (Mode A)
Run the slash command or describe your topic:
```text
/generate-html-ppt "Create a pitch deck for an open-source cloud-native database project"
```

The AI agent executes a **4-Phase Workflow**:
1. **Requirements Alignment & Style Recommendation (with Visual Preview)**: Clarifies audience and length via 7 checklist questions, recommends 2–3 suitable design recipes from 35+ presets based on `selection-index.json` (*Beautiful Modern*, *Swiss Style*, *8-Bit Orbit*, etc.), offers lightweight 1-slide HTML comparison cards (`style-preview.html`) or preview images to preview aesthetics before building full slides, and triggers **Brand Asset Sniffing** to extract brand colors and fonts.
2. **Visual Assets Preparation**: Wraps software screenshots into device mockups (`screenshot-framing`) or generates AI illustrations (`image-prompts`).
3. **Design-System Wireframing**: Reads the single `design.md` recipe, constructs the `1920×1080` stage wireframe, applies layout density strategy (preventing empty center space using `center-group` vertical grouping and hero middle bridge blocks), and **pauses to request user approval**.
4. **Content Batch Filling & Verification**: Fills detailed paragraphs and interactive charts in batches after wireframe approval, verifies layout integrity, and opens the deck in your browser.

### 2. Convert a PowerPoint File (Mode B)
Provide a local `.pptx` file path:
```text
/generate-html-ppt "Convert ./docs/Q3_Roadmap.pptx into an HTML presentation"
```
The agent automatically runs `python scripts/extract-pptx.py` to extract text, vector shapes, images, and speaker notes, mapping them cleanly into the HTML stage.

### 3. Generate Social Media Covers (Mode C)
After generating a deck, request social media assets:
```text
"Design a 21:9 WeChat cover and a 3:4 Xiaohongshu cover image based on this presentation"
```
The agent extracts key takeaways and generates tailored cover designs per `references/covers.md`.

---

## 🎨 Visual Presets Overview

The skill includes **35+ unique design system specifications** covering tech, business, academic, fashion, and retro presentations. Here is a curated selection:

| Style Preset | Visual Preview | Vibe / Mood | Best For | Signature Elements |
| :--- | :--- | :--- | :--- | :--- |
| **Beautiful Modern** | <img src="demo/previews/beautiful-modern.png" width="200" alt="Beautiful Modern"> | Elegant, Modern, Premium | Pitch decks, product launches | Gradient orbs, hero numbers, `light`/`dark`/`hero` theme rhythm |
| **Swiss International** | <img src="demo/previews/swiss-international.png" width="200" alt="Swiss International"> | Rigorous, Minimalist, Bauhaus | System architecture, academic | 22 locked layouts (`S01-S22`), negative space, pure typography |
| **Cyberpunk Dark** | <img src="demo/previews/cyberpunk-dark.png" width="200" alt="Cyberpunk Dark"> | High-impact Neon, Geeky | Tech talks, developer decks | Glow cards (`.b-blue`, `.fill-teal`), staggered entry animations (`.a1`-`.a6`) |
| **8-Bit Orbit** | <img src="demo/previews/8-bit-orbit.png" width="200" alt="8-Bit Orbit"> | Retro Pixel, Nostalgic Game | Game dev, Web3 projects | Pixel borders, dot-matrix fonts, retro color contrast |
| **Emerald Editorial** | <img src="demo/previews/emerald-editorial.png" width="200" alt="Emerald Editorial"> | Deep Green, Magazine Quality | Sustainability, design exhibitions | Serif display headers, classic grids, deep emerald & gold accents |
| **Neo Grid Bold** | <img src="demo/previews/neo-grid-bold.png" width="200" alt="Neo Grid Bold"> | Neubrutalism, Energetic | Youth culture, creative meetups | Thick black borders, hard offset shadows, high saturation blocks |
| **Monochrome** | <img src="demo/previews/monochrome.png" width="200" alt="Monochrome"> | High Contrast, Hacker Aesthetic | Code walkthroughs, hackathons | Pure black & white contrast, monospace typography |

> 🖼️ **Explore Complete Gallery**: For all 37 style presets with 1:1 previews, full color tokens, typography pairings, and the decision matrix, see 📖 **[Full Style Presets Gallery (STYLE_GALLERY.md)](designs/STYLE_GALLERY_en.md)**.


---

## ⌨️ Shortcuts & Navigation

When viewing the generated HTML presentation in a browser:

* **Next Slide**: `ArrowRight (→)`, `ArrowDown (↓)`, `Space`, `PageDown`, or swipe left on mobile.
* **Previous Slide**: `ArrowLeft (←)`, `ArrowUp (↑)`, `PageUp`, or swipe right on mobile.
* **Jump to Start / End**: `Home` / `End`.
* **Overview Gallery**: `O` key.
* **Fullscreen**: `F` key.
* **Direct Slide Hash**: URL hash updates automatically (e.g., `#s3` directly links to slide 3).

---

## 🧠 Philosophy

1. **Zero-Dependency Lifespan**: Single-file HTML output runs everywhere without external server or build dependencies, ensuring the deck opens perfectly even 20 years later.
2. **Layout Stability**: Fixed 16:9 canvas with dynamic CSS scale transform eliminates layout reflow and text wrapping bugs across different screens.
3. **AI-Native Workflow**: Replaces fragile CSS tweaking with structured AI directives. Strict `design.md` schemas and validation scripts eliminate AI UI hallucinations.

---

## 🔒 Security & Subresource Integrity (SRI) Policy

To guarantee **supply-chain safety**, **integrity**, and **tamper resistance** in enterprise and production environments, this project follows strict third-party static asset security standards:

### 1. Supply Chain Security Baseline
* **Removal of Flagged Mirrors**: Untrusted third-party mirrors (such as `cdn.bootcdn.net` and `cdn.staticfile.org`) flagged by threat intelligence have been completely eliminated.
* **Verified Official CDNs**: Only official and highly trusted public CDN networks are used (`cdnjs.cloudflare.com`, `cdn.jsdelivr.net`, `unpkg.com`).
* **Strict Version Pinning**: All external dependencies are pinned to exact semantic versions. Floating versions like `@latest`, `@5`, `@10` are strictly forbidden.
* **Script integrity verification**: The optional-script loader in `template.html` applies fixed SHA-384 SRI hashes to both CDN and local `vendor/` fallbacks. Fonts and optional style resources that cannot use SRI are not covered by this claim and remain subject to the browser's origin/CSP policy.

### 2. External Dependencies & SRI Inventory

| Package | Pinned Version | Verified CDN Mirrors | SRI Hash (SHA-384) |
| :--- | :--- | :--- | :--- |
| **ECharts** (Charts) | `5.5.0` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-o5uz97et3bErHvpKfD4Jz4n0JfhJDWABFuF4NP+iEEDxE1VwMWJ19QGR0lqFZnr6` |
| **Mermaid** (Diagrams) | `10.9.1` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-WmdflGW9aGfoBdHc4rRyWzYuAjEmDwMdGdiPNacbwfGKxBW/SO6guzuQ76qjnSlr` |
| **Marked** (Markdown) | `12.0.2` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-/TQbtLCAerC3jgaim+N78RZSDYV7ryeoBCVqTuzRrFec2akfBkHS7ACQ3PQhvMVi` |
| **Highlight.js (JS)** | `11.9.0` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-F/bZzf7p3Joyp5psL90p/p89AZJsndkSoGwRpXcZhleCWhd8SnRuoYo4d0yirjJp` |
| **Highlight.js (CSS)** | `11.9.0` | `cdnjs` / `jsdelivr` / `unpkg` | `sha384-oaMLBGEzBOJx3UHwac0cVndtX5fxGQIfnAeFZ35RTgqPcYlbprH9o9PUV/F8Le07` |
| **Lucide Icons** | `0.344.0` | `jsdelivr` / `unpkg` | `sha384-tTkFttkBclaU1cloKwOi9xk3pbao3VZxTjLNBt8iFABWDBQibbAbWpVmO28zMuxq` |
| **Motion** (Animations) | `11.11.17` | Optional reviewed local copy in `./assets/` | Optional animations are disabled if absent |

### 3. Fully Offline / Air-Gapped Intranet Deployment
For air-gapped internal enterprise networks, create a `vendor/` directory beside the generated HTML and place the corresponding pinned `.min.js` files inside. The loader prioritizes those local files and verifies them with the fixed SRI hash before execution. The Swiss template never dynamically imports Motion from a CDN; its optional animations are enabled only when a reviewed `assets/motion.min.js` is explicitly shipped with the presentation, otherwise they safely disable.

---

## 📄 License

[MIT License](LICENSE) — Free to use, modify, and share!

## 👏 Credits

Inspired by [@zarazhangrui](https://github.com/zarazhangrui)'s [frontend-slides](https://github.com/zarazhangrui/frontend-slides) and [@op7418](https://github.com/op7418)'s [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill).
