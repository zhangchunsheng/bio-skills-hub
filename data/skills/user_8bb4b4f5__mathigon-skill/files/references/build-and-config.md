# Build, Config & Translations

Source: @mathigon/studio `build/index.js`, `server/serve.ts`, `server/interfaces.ts`, `docs/setup.md`; repo `package.json`, `config.yaml`, `.github/workflows/`.

## Prerequisites

- **Node.js >= 16** (CI uses 16; README says 14+ but 16 is the real floor). @mathigon/studio itself declares `node >=18` for its own dev, but the textbooks repo runs on 16.
- `npm install` brings in `mgon-build` and `mgon-serve` (binaries from `@mathigon/studio`).
- `node_modules` is frequently absent in this checkout — most edits (content.md, functions.ts authoring) don't require it; you only need it to actually run/build.

## Commands (from package.json)

```bash
npm install            # install deps (provides mgon-build / mgon-serve)

npm start              # DEV: watch + serve in parallel → http://localhost:5000
                       #   (first run is SLOW — compiles all courses; later runs use cache)

npm run server         # mgon-serve only (the dev server, port 5000, no flags)
npm run watch          # mgon-build --assets --watch --locales en  (recompile on change)
npm run assets         # mgon-build --assets --locales en           (one-shot build; used in CI)

npm run lint           # eslint content --ext .ts
npm run lint-fix       # eslint content --ext .ts --fix   (RUN BEFORE SUBMITTING)

npm run translate      # mgon-build --translate --key google-service-account.json  (key is gitignored!)
```

### `mgon-build` flags (authoritative, from source)
| Flag | Effect |
|------|--------|
| `--assets` | Build all courses (md→HTML/JSON), SCSS→CSS, TS→JS, SVG icons. |
| `--minify` | (with --assets) Minify (cssnano + html-minifier + esbuild). |
| `--watch` | (with --assets) Recompile on file change via chokidar. |
| `--locales aa,bb` | Comma-separated locales to build; defaults to `config.yaml` `locales`. |
| `--search` | Build search index (only if `config.yaml` `search.enabled: true`). |
| `--thumbnails` | Generate social-media preview thumbnails for every course. |
| `--translate` | Auto-translate UI strings via Google Translate (needs `--key`). |
| `--key <file>` | Path to a Google Cloud service-account JSON for `--translate`. |
| `--all` | (with --translate) Translate all locales in locales.yaml; else only config.yaml ones. |
| `--licenses` | Emit list of OSS dependency licenses. |

### `mgon-serve`
Fixed dev server on **port 5000** (overridable via `PORT` env). Takes no flags. For a custom server, write your own `server/app.ts` and run with `ts-node`/`nodemon` (see @mathigon/studio `docs/example/`).

## What `npm start` / `mgon-build --assets` actually does

1. Parses every `content/*/content.md` with the custom Markdown dialect → cached JSON + HTML.
2. Bundles each course's `functions.ts` → `.js` (esbuild, with a Pug-import plugin).
3. Compiles `content/*/styles.scss` → CSS (sass + autoprefixer + rtlcss + optional cssnano).
4. Inlines SVG icons into `/icons.svg`.
5. (If `--search` and enabled) builds a search index.
6. Caches results — subsequent builds reuse the cache (hence "first run is slow").

The watch mode recompiles the affected course when you save a file. **A few exceptions don't hot-reload** (shared files, YAML config) — restart `npm start` for those.

## config.yaml reference

Loaded by `build/utilities.js`: the studio package's defaults are deep-merged with the project's root `config.yaml` (project wins). Authoritative schema: `server/interfaces.ts` `Config`.

Current project `config.yaml`:
```yaml
siteName: Mathigon
description: A interactive textbook
domain: mathigon.org
privacyURL: https://amplify.com/customer-privacy
banner: (c) Mathigon
locales: [en, ar, cn, de, es, fr, hi, hr, it, ja, pt, ro, ru, sv, tr, vi]
search:
  enabled: false
footer:
  rows:
    - links:
        - {title: GitHub, url: https://github.com/mathigon/textbooks}
        - {title: Live Website, url: https://mathigon.org/courses}
  copyright: © Mathigon, 2022
social:
  facebook: {}
  twitter: {}
courses:
  showLocked: true
  revealAll: false
  audio: false
tutor:
  enabled: true
```

### Key options
| Key | Meaning |
|-----|---------|
| `siteName`, `description`, `domain` | Site identity (SEO, sitemap, templates). |
| `contentDir` | Path to courses; default `content`. Rarely changed. |
| `banner` | Comment header prepended to every generated JS/CSS file. |
| `locales` | Locale codes served; default for `--locales`/`--translate`. |
| `search.enabled` | Master switch for `--search` (no-op unless true). `search.popular` for popular terms. |
| `header.{logo,title,links}`, `footer.{rows,copyright}` | Header/footer branding & nav. |
| `accounts.enabled` | User accounts + progress saving (needs MongoDB `mongoServer` + SendGrid `sendgridKey` + optional `oAuth`). Plus `minAge`, `privacyPolicy`, `termsOfUse`, `address`, `supportEmail`. |
| `social` | Facebook `{page,appId}`, Twitter `{handle}` (no @), Instagram/Youtube handles; `pinterest`/`reddit`/`googleClassroom` booleans for share buttons. |
| `courses.revealAll` | `true` = reveal all steps immediately (disables goal-gating; read-only mode). |
| `courses.showLocked` | `true` = show dev-locked sections greyed out (rather than hide). |
| `courses.biosPath`, `courses.feedback` | Custom bios path; feedback toggle. |
| `tutor.enabled` | Enable the `<x-tutor>` virtual tutor. `tutor.name`/`icon` customise it. |

> **Note:** `courses.audio` appears in this repo's config but is **not** in @mathigon/studio 0.1.43's `Config` interface. Audio narration is generated by a separate textbooks-repo script (`utilities/audio.js`, using Google Cloud TTS + FFmpeg) — and that script + `docs/` are **not present in this checkout** despite README references.

## Translations

Two parallel systems:

### 1. UI strings (`translations/strings.yaml` + `__()` in Pug templates)
- In Pug templates, wrap strings: `__("hello")`, `__("hello, $0", name)`.
- Running the dev server auto-collects these into `translations/strings.yaml` (commit it).
- `npm run translate` auto-translates `strings.yaml` keys into each `translations/<locale>/strings.yaml` via Google Translate. **Needs the gitignored `google-service-account.json`** — will fail without it. Existing human translations are preserved; only missing keys get machine-translated.

### 2. Course content (`translations/<locale>/`)
- Translated copies of course markdown, mirroring the `content/` layout.
- Managed via **GitLocalize** (https://gitlocalize.com/repo/5711) — human translators work there; PRs come back to this repo.
- Locales served via subdomain (`fr.domain.com`) or `?hl=fr` query param.
- Master locale list: `@mathigon/studio` `server/data/locales.yaml` (each entry may carry a `google` code for translation).

**When editing translations:** prefer minimal, typo-fix-only hand edits; structural translation work goes through GitLocalize. Always edit the **English source** in `content/` as the canonical version.

## Lint scope & rules (what CI checks)

- Scope: **`content/**/*.ts` only**. `frontend/` and `translations/` are NOT linted by `npm run lint`.
- CI (`.github/workflows/test.yml`, Node 16): `npm ci --no-optional` → `npm run lint` → `npm run assets`. (Unit/screendiff tests are commented out — `TODO`.)
- CodeQL runs on `.js`/`.ts` for master/PRs.
- **There is no test suite.** Verify interactives manually via `npm start` at localhost:5000.

### Enforced rules (from .eslintrc.js + .editorconfig)
- 2-space indent, UTF-8, **LF** line endings, trim trailing whitespace, final newline for .ts/.js.
- `prefer-const` error; unused vars/args must be `_`-prefixed.
- `comma-dangle: never`; no spaces inside parens; sorted imports (case-insensitive, external before relative).
- `@typescript-eslint/no-explicit-any` is a **warning** (tolerated but avoid).
- `spaced-comment` requires a space after `//`.
- Every `.ts` file starts with the `(c) Mathigon` header banner (convention, not linted but expected).

## Verifying a content change end-to-end

```bash
npm install                       # only if node_modules absent
npm run lint-fix && npm run lint  # TS style in content/
npm start                         # → open localhost:5000 → navigate to your course/step
# Click through the step; confirm goals fire, reveals appear, no console errors.
# functions.ts runtime errors usually = id↔function-name mismatch, bad import, or wrong goal name.
```

## Official docs (when this skill isn't enough)

The README references `docs/markdown.md`, `docs/interactives.md`, `docs/translations.md`, `utilities/audio.js` — **these do NOT exist in this checkout**. The real docs live in the @mathigon/studio repo:
- https://github.com/mathigon/studio/tree/main/docs → `markdown.md`, `interactives.md`, `setup.md`
- Component sources: `github.com/mathigon/studio/tree/main/frontend/components/`
- Library APIs: `github.com/mathigon/{core,fermat,euclid,boost,hilbert}.js/tree/master/src/`
