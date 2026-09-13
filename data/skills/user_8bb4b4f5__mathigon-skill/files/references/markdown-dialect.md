# Mathigon Custom Markdown Dialect (`content.md`)

A superset of Markdown with: YAML-like `>` metadata, `:::` fenced layout blocks, Pug-style 4-space-indented components, and special inline link/aside syntax. Source: distilled from all 35 course `content.md` files + official `docs/markdown.md` in @mathigon/studio.

## File structure

```
# Course Title                    ← single H1, the course title

> color: "#5A49C9"               ┐
> description: ...               │  course-level metadata (before first section)
> section: introduction          │
> id: intro                      │
> trailer: tBJUNvCBkLo           │
> level: Intermediate            │
> next: graph-theory             ┘

## First Section                 ← H2 starts a section (sidebar entry)

Body text...

---                              ← three dashes = new step within section
> id: radius                     ← each step gets its own metadata block
> goals: compass

Body of step "radius"...
```

- **`---`** (three dashes) separates steps within a section.
- **A long run of dashes** (`--------…`) marks a heavier new-section boundary.
- `# H1` once per file; `## H2` per section; `### H3` for subsections.

## Metadata directive keys (lines starting with `>`)

| Key | Example | Meaning |
|------|---------|---------|
| `id:` | `> id: radius` | Unique DOM id for the step. **Must match** the exported function name in functions.ts (kebab→camelCase). Used for progress tracking in DB. |
| `goals:` | `> goals: circle-0 circle-1` | Space-separated goal ids; step completes when all scored. Singular `> goal:` also valid. |
| `section:` | `> section: radians` | Section slug (sidebar grouping, URL `/course/<course>/<section>`). |
| `color:` | `> color: "#5A49C9"` | Hex theme color for the section/course (quoted). |
| `level:` | `> level: Intermediate` | One of `Foundations`, `Intermediate`, `Advanced`. |
| `next:` | `> next: graph-theory` | Next course to recommend. |
| `title:` | `> title: Rolling Dice` | Display title (overrides heading). |
| `description:` | `> description: ...` | Free-text description for cards/SEO. |
| `trailer:` | `> trailer: tBJUNvCBkLo` | YouTube id for course trailer video. |
| `sectionBackground:` | `> sectionBackground: dark casino` | Visual background theme. |
| `sectionStatus:` | `> sectionStatus: dev` | Dev status; `dev` hides from non-dev. |
| `url:` | `> url: /world/Logic` | Legacy/canonical URL. |

> goals: A step with **no** `> goals:` line completes as soon as it's viewed (pure info content).

## Math notation — backticks, NOT `$`

Math is **AsciiMath inside backticks**, rendered to MathML by MathJax:

```
`C = π × d`            inline math
`x^2`                  superscript
`x_n`, `x_(n-1)`       subscript (parenthesise multi-char)
`\frac{a}{b}`          LaTeX fraction also works
`"circumference"`      quoted text inside math
`K_"3,3"`              subscripted text
`6800\ km`             backslash-space = non-breaking space (also `12\ m`)
```

**Do NOT use `$...$`** — single `$` is reserved for variable interpolation (see below). Display equations are just centered paragraphs: `{.text-center} `V = π r^2 h``.

## Blanks (fill-in-the-interactive) — the `blank-N` goal source

| Syntax | Type | Example |
|--------|------|---------|
| `[[42]]` | numeric free input | `[[169]]` |
| `[[correct\|wrong\|wrong]]` | multiple choice (1st = correct, shuffled) | `[[twice\|half\|same]]` |
| `[[\`pi/180\`\|180pi]]` | math in options | `[[`pi`\|`2 pi`\|3]]` |
| `[[100 ± 5]]` | accept range 95–105 | `[[100 ± 5]]` |
| `[[100 (hint text)]]` | hint on mistake | `[[100 (Double it.)]]` |
| `[[100 (hint1 \| hint2)]]` | progressive hints | |
| `[[100 (50: msg \| 100: msg)]]` | error-specific hints | |

Blanks are **auto-indexed `blank-0`, `blank-1`, …** in document order → these become auto-scored goals. Reference them in `when="blank-0"` reveals and `$step.onScore('blank-0', ...)`.

## Variable sliders & interpolation — `${...}`

```
${n}{n|5|2,20,1}        slider: var n, default 5, range 2–20, step 1
${n}                    interpolate current value of n
${n*n}                  interpolate an expression
${round(2*p,1)}π        expression with function call
```

- The `${name}{name|default|min,max,step}` form **defines** a slider bound to `name`.
- Bare `${expr}` interpolates the value (used alongside a slider definition or a model var set in functions.ts).

**MUST: a slider must be INLINE inside a sentence, never on its own line.** `${n}{n|6|6,96,2}` placed alone on a line renders as a literal `<n>` tag with raw text (NOT an interactive slider) — the parser only recognises the slider syntax when it's embedded in prose. Every existing course puts it mid-sentence:
```markdown
✓ 如果边数 _n_ = ${n}{n|5|2,20,1}，那么……      ← 嵌在句中，渲染成 <x-var>
✗ ${n}{n|5|2,20,1}                              ← 单独成行，渲染成错误的 <n> 标签
```
Verified failure: a standalone slider line produced `<n>{n|6|6,96,2}</n>` instead of `<x-var bind="n|6|6,96,2">`.

**functions.ts must draw the initial state itself.** A slider's default value populates `$step.model` asynchronously, so `$step.model.watch` may fire before `m.n` is set. Always call your `redraw(defaultValue)` once immediately after registering the watcher, and guard against `undefined`:
```ts
redraw(6);                          // draw the default state immediately
$step.model.watch((m) => {          // then react to slider changes
  redraw(m.n);                      // redraw() must tolerate n being undefined
});
```

## Reveals — show content after a goal

```
{.reveal(when="blank-0")} This appears after blank-0 is solved.
{.reveal(when="compass" delay="1000")} Appears 1s after compass.
{.reveal(when="blank-0 blank-1")} Multiple goals (all required).
```

- `when=` = goal name(s), space-separated.
- `delay=` = ms (e.g. `1000`) or seconds (e.g. `"1s"`).
- `animation=` = e.g. `pop`.
- Can prefix a paragraph: `{.reveal(when="g")} text`
- Or wrap a block: `::: .reveal(when="g") ... :::`
- Or as an attribute on Pug elements/components: `path.red.reveal(when="blank-0")`.

## Layout — `:::` fenced blocks

Multiple consecutive `::: column(...)` blocks form a **row**; a lone `:::` closes the group.

```
::: column.grow                       grow to fill (most common)
::: column.fit                        shrink to fit
::: column(width=320)                 fixed pixel width
::: column(width=220 parent="padded-thin")   join a named row across blocks
::: column.frame.blue.text-center(width=212)  bordered colored box
::: column.reveal(when="eqn-0")       column that reveals on goal
```

Other containers:
```
::: .theorem  /  ::: .theorem.s-red        definition/theorem callout
::: .box.blue / .box.red / .box.green      highlighted exercise box (often wraps #### Exercises)
::: figure  /  ::: blockquote  /  ::: .overflow-wrap.overflow-table
::: tab                                     one tab pane inside an x-tabbox
::: x-slideshow  /  ::: x-equation-system   component-as-block
```

**No** `::: problem`, `::: solution`, `::: warning`, `::: definition` — use `.theorem`/`.box`/`#### Heading` instead.

## Inline class/aside syntax

Prefix a paragraph: `{.caption} text` · `{.text-center} text` · `{.todo} Coming Soon!` · `{.fixme} needs work` · `{.r} right-aligned`.

Wrap inline spans: `_{.n}3_` · `_{span.reveal(when="blank-1")} ... _` · `_{x-equation.small(...)}_` (wrap a component inline) · `__{.red}RR__` (bold + class).

Chained classes: `{.text-center.s-orange.no-voice}`.

## Links — special URI schemes

| Syntax | Meaning |
|--------|---------|
| `[text](gloss:term)` | Glossary tooltip (term in content/shared/glossary.yaml) |
| `[Name](bio:slug)` | Biography popup (slug in content/shared/bios.yaml) |
| `[text](target:r)` | Highlight the element(s) with `target="r"` when hovered |
| `[text](action:fn())` | Call JS function `fn` on click (e.g. `action:setState(0)`) |
| `[text](->selector)` | Target pointer — highlight/scroll to a DOM selector. **Replace spaces in the selector with `_`**. |
| `[text](pill:red)` | Colored pill highlight in an equation (colors: red, purple, blue, teal, green, lime, yellow, orange) |
| `[text](https://…)` | Normal link |

Link text can carry classes: `[{.red.b}radius](target:r)`, `the [{.pill.green}data bits](target:data)`.

## Inline Pug tag in prose

`#[span.check.incorrect(when="bridge-0")]` · `#[em actual]` · `#[br]` (line break) — embeds a Pug element mid-sentence.

## Pug blocks (4-space indented)

4-space-indented content is **Pug** (no angle brackets; attrs unquoted or `key=value`):

```
.roulette-wheel
  .layer-2.wheel
  .ball

figure: x-img(src="images/x.jpg" width=320)        chained tag: syntax

x-geopad(width=320 height=300)
  svg
    circle.move(name="a" cx=160 cy=150 target="r")
    path.red(x="segment(a,b)" target="r")

include svg/wheel.svg                  inline an SVG file
include mixins                         +barchart([[...]])
```

Pug comments: `//` (ignored) and `//-` (unbuffered).

## Math inside equations — special functions

Inside backtick math, use these instead of Markdown blanks/pills:

| Markdown | Inside equation |
|----------|-----------------|
| `[[choice]]` | `` `blank(x, "choice")` `` |
| `[[10]]` | `` `input(10)` `` |
| `[pill](pill:red)` | `` `pill(x, "red")` `` |
| `[{.green}t](target:p)` | `` `pill(x, "green", "p")` `` |
| `${y*2}` | `` `var("y * 2")` `` |

## Tables

Standard GFM pipe tables; cells can contain blanks, math, components, class spans:

```
| degrees | 0 | 60 | _{x-equation.small(solution="360/π" keys="π frac" numeric)}_ |
| radians | 0 | _{x-equation.small(solution="π/3" keys="π frac" numeric)}_ | 2 |
{.table-small.grid}          ← attribute line attaches to the table
```

## Emphasis & typography (MUST follow these — verified failures)

`__bold__`, `_italic_`, `**bold**`, `*italic*` all work. `&nbsp;` for non-breaking space; `° × ÷ − π θ …` Unicode used directly.

**Critical typography rules (each was a real rendering bug):**

- **Use curly quotes `'` (U+2019) for ALL apostrophes/possessives in prose and headings, NEVER ASCII `'`.** ASCII apostrophes get HTML-escaped to `&#39;` and render as literal `&#39;` in `<title>`/`<h1>`/meta tags — visible garbage like `A President&#39;s Proof`. Mathigon's own courses use `'` everywhere (e.g. `## Pythagoras’ Theorem`). When writing or editing prose, replace every `'` in English words (`Garfield's`, `President's`, `That's`) with `'`. Do NOT touch apostrophes inside backtick math expressions (e.g. derivative notation) — only prose.
- **Use en dash `–` (U+2013) for ranges/pauses, em dash `—` (U+2014) for breaks**, matching existing courses. Don't use `--` or `---` inline in prose (those are section separators, see above).
- **AsciiMath inside backticks rejects Unicode fraction glyphs**: `½` → "Unknown symbol" build error. Write `1/2`. But `×`, `÷`, `°`, `π`, `θ`, `²`(superscript-two) etc. are fine; only fractional Unicode (`½ ¼ ¾`) and superscript-via-Unicode must be plain ASCII (`1/2`, `^2`).
- **`gloss:` / `bio:` links need exact keys** in `content/shared/glossary.yaml` / `bios.yaml` or they warn + render as dead links. Note Mathigon uses **British** spelling in the glossary: it's `gloss:trapezium` (not `trapezoid`), `gloss:colour` (not `color`). When in doubt, grep the yaml before linking, or fall back to plain `__bold__` text.

## Audio narration (auto-generated)

`_{.no-voice} silent text_` suppresses TTS. `_{span(voice="a squared")} `a^2`_` overrides spoken text.
