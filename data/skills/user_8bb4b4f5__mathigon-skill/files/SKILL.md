---
name: mathigon-skill
description: How to author and edit interactive Mathigon course content in the textbooks repo — the custom Markdown dialect in content.md, the functions.ts interactive model (Step lifecycle, scoring, goals), the x-* custom components, the @mathigon/* library APIs, and the build/config pipeline. Use whenever the user wants to add, modify, fix, or translate Mathigon course content, build interactives, write functions.ts handlers, use x-geopad/x-slider/x-equation/x-coordinate-system components, edit styles.scss, run the dev server, configure config.yaml, or otherwise work inside D:\textbooks-master\content or translations/. Trigger on any mention of Mathigon, content.md, functions.ts, mgon-build, mgon-serve, x-step, x-geopad, gloss/bio links, goal/score, or Mathigon courses generally — even if the user doesn't say "skill".
---

# Mathigon Course Authoring

This skill guides edits to interactive Mathigon courses in this repo. Courses live in `content/<course>/`; each course is three paired files plus assets:

```
content/<course>/
├── content.md      ← course source (custom Markdown dialect)
├── functions.ts    ← TypeScript for interactive steps
├── styles.scss     ← course-specific styles
├── hints.yaml      ← (optional) tutor hint strings
├── components/     ← course-local custom elements + helpers
├── images/ svg/ audio/  ← static assets
```

Shared cross-course resources: `content/shared/` (types.d.ts, constants.ts with the color palette, bios.yaml, glossary.yaml, reusable components under components/).

The server, Markdown parser, and core component library live in the **external** npm package `@mathigon/studio` (pinned 0.1.43) — not in this repo. `node_modules` is often absent; treat this repo as content + thin interactives.

## The one mental model that matters most

Every course is a sequence of **steps**. A step is declared in `content.md` with YAML metadata, and *optionally* backed by a TypeScript function in `functions.ts`. The linkage is mechanical:

```
content.md                          functions.ts
──────────                          ────────────
---                                 
> id: my-step-2          ◄────────► export function myStep2($step: Step) { ... }
> goals: click reveal
```

The step's `> id:` (kebab-case) is converted to camelCase and used as the **lookup key** into the table of functions exported by the course's `functions.ts`. That function runs **once, the first time the step is revealed**, receiving the `$step` (the `<x-step>` element view). `toCamelCase("my-step-2")` → `myStep2`.

**A step is "complete" (unlocks the Next button) when ALL its declared goals are scored.** Goals come from two sources:
1. **You score them** from JS: `$step.score('click')` fulfils the `click` token in `> goals: click reveal`.
2. **The framework auto-scores fill-in blanks**: every `[[...]]` in the step auto-generates goals `blank-0`, `blank-1`, … in document order, scored automatically when the student answers correctly. You don't score these — you *listen* with `$step.onScore('blank-0', ...)` to drive animations.

Most steps have **no** function at all — they're pure content (prose + blanks the framework manages). Only add a function when you need custom JS.

## When the user asks you to do X, read Y first

| Task | Read this reference before editing |
|------|------------------------------------|
| Write/edit `content.md` (prose, layout, blanks, math, links, reveals) | `references/markdown-dialect.md` |
| Write a `functions.ts` step handler, score goals, react to blanks, animate | `references/functions-model.md` |
| Use `x-geopad`, `x-slider`, `x-equation`, `x-coordinate-system`, `x-video`, etc. | `references/components.md` (for the tag/attrs) **and** `references/functions-model.md` (for driving them from TS) |
| Call @mathigon utilities (Point, Random, animate, slide, $, $N, list, clamp, …) | `references/libraries.md` |
| Run the dev server, build, lint, or change `config.yaml` | `references/build-and-config.md` |
| Translate content | `references/build-and-config.md` (Translations section) |
| **Write/edit a Chinese (中文) course** — for Chinese students | `references/chinese-localization.md` **(MUST read — CJK has non-obvious rules)** |

**Always read the reference that matches the task before writing code** — these are distilled from the real source. Do not rely on memory of the @mathigon/* APIs.

## How to edit safely (recipe)

1. **Find a reference course.** Before writing anything new, open an existing course that does something similar (`circles`, `graph-theory`, `sequences`, `probability` are the richest). Copy its patterns verbatim — import blocks, header comments, section structure.
2. **Pair content.md with functions.ts.** Keep a section's `> id:` and its `export function` in sync. If you rename an id, rename the function (camelCase).
3. **Match imports to what you use.** Standard import order (enforced by `sort-imports`): `@mathigon/core` → `fermat` → `euclid` → `boost` → `studio` → `../shared/...` → `./components/...` → bare side-effect `import './components/x'` lines. See `references/libraries.md` for what each package exports.
4. **Start every .ts file with the header banner** (else lint/style breaks):
   ```ts
   // =============================================================================
   // <Section Name>
   // (c) Mathigon
   // =============================================================================
   ```
5. **Lint before done.** Lint scope is `content/**/*.ts` only. Run `npm run lint-fix` (auto-fixes) then `npm run lint`. Key rules: 2-space indent, LF line endings, `prefer-const`, unused vars/args prefixed `_`, `comma-dangle: never`, no spaces inside parens, sorted imports.
6. **Register custom elements via side-effect import.** If you use a course-local `<x-foo>` in content.md, add `import './components/foo'` (or `import '../shared/components/foo/foo'`) at the top of functions.ts. The `@register('x-foo')` decorator runs on import and defines the element. See `references/components.md`.
7. **Reuse shared colors.** Import from `../shared/constants` (`RED`, `BLUE`, `GREEN`, `YELLOW`, `ORANGE`, `PURPLE`, `TEAL`, `LIME`, `GREY`) instead of hardcoding hex.

## Common gotchas

- **For Chinese (中文) courses: every section MUST have an explicit `> section: <english-slug>`.** Chinese H2 headings (e.g. `## 构造梯形`) cannot be slugified into a URL — without `> section:`, only the first section appears and all others return 404. Also: `> id:` stays English (matches functions.ts exports); backtick math must contain NO Chinese characters (AsciiMath errors on them); prose/blanks/hints use Chinese; `gloss:`/`bio:` keys stay English. Full rules in `references/chinese-localization.md`.
- **NEVER trust memory for math/geometry.** When a course involves geometric figures, coordinates, or proofs, you MUST verify every length, angle, and coordinate with an actual computation (Python `math.hypot`/dot-product) before writing `content.md`. Visual diagrams that "look right" but have wrong coordinates are the #1 failure mode — a figure with three sides all labelled `c` that aren't actually equal in length is worse than no figure. Compute, don't guess. Example verification pattern: pick concrete values (e.g. a=3,b=4,c=5), compute each vertex, then assert `abs(length_a - expected) < 1e-9` for every labelled edge and `dot(v1,v2)==0` for every claimed right angle.
- **README's `docs/*.md` and `utilities/audio.js` links don't exist in this checkout.** Use existing courses as reference instead. (Official docs are at github.com/mathigon/studio/tree/main/docs — markdown.md, interactives.md, setup.md.)
- **No test suite.** CI runs only `npm run lint` + `npm run assets`. Verify interactives by running `npm start` and clicking through at localhost:5000.
- **`npm start` first run is slow** (compiles all courses); later runs use cache.
- **Node >= 16 required** (CI uses 16). `mgon-build`/`mgon-serve` come from @mathigon/studio after `npm install`.
- **`google-service-account.json`** (for `npm run translate`) is gitignored and absent — translate will fail without it.
- **The `$` prefix is a project convention for "view/DOM object"**, unrelated to jQuery. `$step`, `$svg`, `$circle` are ElementView wrappers.
- **`x-geopad`, `x-coordinate-system`, `Equation`, `EquationSystem`, `Geopad`, `CoordinateSystem`** types come from `../shared/types` (a .d.ts); their implementations come from `@mathigon/euclid`/`@mathigon/studio`/shared components. See `references/components.md` for where each lives.
- **`x-select` and `x-icon` live in `@mathigon/boost`**, not studio. The tabbed container is `x-tabbox` (not `x-tabs`).

### Gotchas discovered building a real course (verified against this repo)

- **Import members must be alphabetically sorted** within each `import {...}` block (`sort-imports` rule, case-insensitive). E.g. `import {confetti, Slider, Step}` — not `{Slider, Step, confetti}`. Lint errors on this; run `npm run lint-fix`.
- **SCSS variable names**: the only font var is `$fonts` (NOT `$font-ui`), and color/theme vars (`$red`, `$blue`, `$grey-background`, `$dark-mode`, `$shadow`, …) only exist after `@import "@mathigon/studio/frontend/styles/variables";`. Full list in `node_modules/@mathigon/studio/frontend/styles/variables.scss`.
- **AsciiMath rejects Unicode math glyphs** inside backticks. `½` → "Unknown symbol" build error. Write `1/2`; `×`/`÷`/`°`/`π` are fine, but fractional Unicode like `½`/`¼`/`²` must be plain ASCII (`1/2`, `^2`).
- **`gloss:` and `bio:` links require matching keys.** `[x](gloss:foo)` needs `foo:` in `content/shared/glossary.yaml`; `[x](bio:bar)` needs `bar:` in `content/shared/bios.yaml`. Missing keys produce build warnings (non-fatal) and render as dead links. Either add the entry or rewrite as plain text / `->#anchor`.
- **Course page URL format is `/course/<course-id>/<section-slug>`** (note the `/course/` prefix). The `<section-slug>` comes from **either** an explicit `> section: foo` directive **or** (if absent) the slugified `## H2 Heading` that introduces the section — NOT from `> id:`. So a heading `## The Hidden Right Angle` with `> id: hidden-angle` is reached at `.../the-hidden-right-angle`, not `.../hidden-angle`. When testing, always get the real slugs from the homepage (`curl http://localhost:5000/` and grep for `href="/course/<your-course>/..."`) rather than guessing from `> id:` values. Bare `/garfield-theorem` (no section) returns 404.
- **A new course is auto-discovered** from its `content/<course>/` folder — no registration needed. Just `content.md` + `functions.ts` + (optional) `hero.jpg`/`icon.png`/`styles.scss`/`hints.yaml`.
- **`$step.isShown` is a public boolean** (true once `show()` runs) — safe to read. `$step.delayedHint(callback, t=10000)` shows a hint after a delay unless the student scores in the meantime. `$step.onScore(...)` also returns a Promise.

## Verifying your work

```bash
npm install           # if node_modules absent (note: see .npmrc note below)
npm run lint-fix      # auto-fix TS style in content/
npm run lint          # verify  (0 errors expected; pre-existing `any` warnings are fine)
npm run assets        # CI's build — compiles md/ts/scss. WATCH for warnings about
                      #   "Maths parsing error", "Missing bios keys", "Missing glossary keys"
npm run server        # dev server on port 5000 (in another terminal)
# Browse to http://localhost:5000/ to find your course's URL (listed on the homepage),
#   then http://localhost:5000/course/<your-course>/<section>
# If functions.ts throws at runtime, check: id↔function name match, imports, goal names
```

**npm registry note:** the user's global `~/.npmrc` may point at `registry.npmmirror.com`, which is missing `@mathigon/studio` (404 → install rolls back). If `npm install` fails with E404 on `@mathigon/studio`, create a project-local `.npmrc` with `registry=https://registry.npmjs.org/` to override, then retry.
