# GCW tooling

Use automation for deterministic collection and transformation. Use browser inspection and judgment for target attribution, animation semantics and visual acceptance.

| Tool | Purpose | Main output |
|---|---|---|
| `init_reconstruction.py` | Create non-destructive `.gcw/` evidence scaffolding | run state, known gaps, QA matrix, scenario config |
| `site_inventory.mjs` | Crawl public same-origin routes and validate bounded Source Map evidence | `site-inventory.json`, `route-map.json`, `network/requests.json`, `source-maps.json` |
| `detect_interaction_states.mjs` | Detect reviewable hover, focus, and common expanded-state evidence | `interaction-states.json` + before/after PNGs |
| `capture_compare.mjs` | Capture source/candidate pairs; explicitly record or replay redacted per-scenario SPA HAR fixtures | PNG pairs + capture manifest + optional HAR files |
| `image_diff.py` | Compare one same-size screenshot pair | JSON metric and optional diff image |
| `batch_image_diff.py` | Compare every `*.source.png`/`*.candidate.png` pair | JSON, Markdown and diff images |
| `route_smoke.py` | Verify public preview routes respond and optionally contain text | JSON route report |
| `generate_asset_manifest.py` | Draft a review-gated static asset manifest from inventory | `.gcw/asset-manifest.json` |
| `blender_replace_text.py` | Create replacement 3D text matching reference bounds | GLB/GLTF model |
| `install_ci.py` | Install a self-contained GitHub visual-regression harness | `.gcw/` tools and workflow |
| `check_runtime_independence.py` | Reject source-origin URLs in network evidence and final text build artifacts | JSON gate report |

## Dependencies

- Python 3.10+
- Pillow for image diff: `python -m pip install Pillow`
- Node.js 20+
- Playwright for crawling/capture: `npm install playwright`
- A Playwright Chromium browser, or set `browserExecutable`/`GCW_BROWSER_EXECUTABLE` to an installed Chrome/Edge executable
- Blender 4.x only for 3D word replacement

Run `npm install`, `npm run install:browser` and `npm run check` from the GCW repository to verify the shared runtime before a recovery. If Blender is installed outside `PATH`, set `GCW_BLENDER_EXECUTABLE` to its full executable path.

The environment report separates base runtime `passed` from companion `teardownReady` and `teardownRequirements`. Standard and deep work requires teardown readiness; a green base-runtime result does not override it.

The installed CI workflow assumes Vite-style `npm run build` and `npm run preview` scripts. Adapt those two steps when the target project uses another build or preview command.

## Determinism model

Every capture scenario must define `readySelector` or `readyFunction`. Replace the example `document.readyState === 'complete'` condition with an application-specific observable condition for animated sites, such as the final shell being visible or a loading canvas being removed.

Interaction detection is a bounded reconnaissance pass, not a general crawler. It reads accessible CSSOM rules for direct `:hover`, `:focus`, and `:focus-visible` candidates, exercises common `aria-expanded` controls, and keeps only candidates with an observed style, attribute, or viewport-pixel change. It records console and HTTP errors for review. Run it separately for desktop/mobile viewports when both matter; cross-origin CSS and multi-step application states require manual evidence.

`capture_compare.mjs` launches source and candidate in separate browser processes so heavy WebGL contexts do not starve each other. It injects the same seeded `Math.random`, installs the same virtual clock before navigation, advances both pages in equal 16 ms steps until both satisfy readiness, then advances the same settling and input delay. CSS/compositor animations are disabled during screenshot capture.

The controlled clock uses Playwright's official Clock API: <https://playwright.dev/docs/clock>. If an application cannot initialize while the clock is controlled, set `clockMode` to `realtime` and label the resulting temporal comparison `PARTIAL`.

## SPA HAR fixtures

HAR recording never runs by default. Pass exactly one of `--record-har <dir>` or `--replay-har <dir>` and configure a narrow `harFixture.urlFilter`; use `rebaseOrigins` only for additional API origins that must become candidate-local fixture routes. Recording uses embedded minimal HAR data, removes credential headers and cookies, redacts sensitive URL/query/body fields, rebases configured origins to the candidate origin, and deletes the raw HAR before returning.

Replay disables Service Workers. HAR matches are fulfilled before the network guard; misses may reach only the configured page origin, while non-local misses are aborted. The capture manifest records both fallback and blocked requests. A fixture is offline-ready only when candidate-side API paths do not appear in `harFixtures.fallbacks` and candidate-side `harFixtures.blockedRequests` is empty.

This greatly reduces dynamic noise but cannot guarantee a zero diff for GPU drivers, video, cross-origin iframes, server timestamps, nondeterministic workers or compositor state created before readiness. Label such regions explicitly instead of loosening every threshold.

## Safety

- Crawl only routes inside the authorized origin unless the user expands scope.
- Use the final canonical URL. GCW performs a manual redirect-chain preflight and rejects document redirects that leave the configured origin.
- Do not submit forms, guess passcodes or bypass access controls.
- Inventory scripts collect URLs and metadata; they do not archive private responses.
- Source Map probes distinguish HTTP reachability from a valid v3 map and read at most 20 MiB per candidate by default; use `--source-map-max-bytes` to set a different explicit limit.
- Review manifests for query strings or secrets before committing.
- Treat capture configuration as executable code because `readyFunction` runs in the page; review third-party configs before use.
- Inventory and route checks do not consult `robots.txt` because GCW requires ownership or explicit authorization before collection.

Set `GCW_SKILLS_ROOT` when companion skills are not installed beside the GCW checkout or under a supported user skill directory.
