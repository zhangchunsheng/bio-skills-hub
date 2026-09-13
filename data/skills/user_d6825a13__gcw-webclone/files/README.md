# GCW

This English README is canonical; update `README.zh-CN.md` in the same change whenever user-facing behavior changes.

<p align="center">
  <strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a>
</p>

<p align="center">GCW is an agent skill that tears down, clones, and rebuilds websites, with verifiable evidence at every phase.</p>

<img src="./assets/banner.webp" alt="GCW — evidence-driven website cloning" width="100%">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE) · [Changelog](./CHANGELOG.md)

> A screenshot is one frame. A live website is a million.
>
> Everything beyond that frame is guesswork. GCW doesn't guess.
>
> It verifies frame by frame, pixel by pixel.
>
> SOURCE means SOURCE. GUESS says GUESS.
>
> Evidence-driven teardown, faithful cloning, and creative reconstruction. Built on structured Design DNA and WebGL forensics, with a verifiable artifact at every step.
>
> Prove it. Specify it. Rebuild it.

GCW stands for Gao Copy Website. Yes, the name is that literal. The tooling is not:

feed it a website. It returns evidence, a spec, and a project that runs.

## What you can do

| Goal | Result |
|---|---|
| Learn how a site works | A technical teardown with evidence and transferable techniques |
| Clone an excellent site | A runnable replay or editable faithful project, with route, responsive, interaction and visual checks |
| Rebuild it as your own | An accepted editable faithful baseline followed by original content and brand work |
| Recover an owned deployed site | A verified replay or maintainable rebuild when source is unavailable |

GCW covers static pages, React/Vue/Next content sites, multi-page marketing sites, animation-heavy experiences, and Canvas/WebGL/WebGPU frontends. Authentication, private server logic, payment, permissions and proprietary APIs are outside the default boundary.

Ordinary websites are first-class use cases. GCW's distinctive strength is that the same workflow can continue into motion-heavy, interaction-heavy and GPU-rendered sites without abandoning evidence or browser verification.

## How it works

```text
TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD
```

Every task starts with teardown and `.gcw/SITE_SPEC.md`. A study can stop there. Build tasks establish a scoped faithful baseline, then stop at `REVIEW_GATE` so the user can request more fidelity, accept the clone, or approve a creative rebuild.

Before any build starts, GCW asks the ordinary user once and records both `Final deliverable` and `Editability target`. It never selects from a user-profile default:

| Choice | Final deliverable | Editability target |
|---|---|---|
| A | Research or runnable replay only | `RUNNABLE_REPLAY` |
| B | Editable faithful clone; stop after acceptance, with a later C upgrade still available | `MAINTAINABLE_SOURCE` |
| C | Editable faithful clone, then Creative after review | `MAINTAINABLE_SOURCE` |

For B/C, editability is part of `FAITHFUL_CLONE`. `ARTIFACT_REPLAY` may remain an oracle, but an artifact-only candidate cannot pass formal review. `CREATIVE_REBUILD` starts only after acceptance and owns content, brand, and approved innovation—not source maintainability. B is a durable checkpoint rather than a permanent fork: the user may upgrade it to C during review or resume Creative later from the completed B delivery with an explicit C decision and Creative Brief.

Teardown depth scales with the target: `minimal` is an explicit simple non-GPU page profile, `standard` is the default, and `deep` retains the full contract for complex rendering and recovery work.

| User outcome | Workflow | Implementation path |
|---|---|---|
| Study the site | Stop after `TEARDOWN_PHASE` | Evidence only |
| Editable faithful result | Continue through `FAITHFUL_CLONE`, prove editability, then review | `SOURCE_ADAPT`, `CLEAN_REBUILD`, or authorized `MAINTAINABLE_REBUILD` |
| Creative result | Accept an editable faithful baseline, then create a creative brief | Accepted baseline, then content/brand innovation |
| Recover an owned site with unusable source | Enable recovery inside the faithful phase | `PRODUCTION_RECOVERY` configuration |

<img src="./assets/features.webp" alt="GCW workflow: public evidence, local reconstruction, verification, and deployment" width="100%">

## Evidence orchestration: the GCW difference

GCW does not merely call companion skills. It preserves their native evidence, converts the results into one implementation specification, and blocks phase transitions until the evidence contract passes.

### Companion analysis

Every `TEARDOWN_PHASE`, including study-only work, runs `design-dna` before `SITE_SPEC.md` is finalized:

- [design-dna](https://github.com/zanwei/design-dna) is required for typography, spacing, palette, layout, responsive rules, motion and visual language.
- [web-shader-extractor](https://github.com/lixiaolin94/skills/tree/main/web-shader-extractor) is required when Canvas, WebGL, WebGPU or shaders are present; otherwise GPU analysis is recorded as `N/A` with detection evidence.

Install both in the same singular `.agent/skills` root. Study-only work stops after teardown but does not bypass its required analysis.

### One authority per layer

| Layer | Authority |
|---|---|
| Companion artifacts | Complete native Design DNA and Shader evidence |
| `SITE_SPEC.md` | The single human-readable implementation specification |
| `teardown-manifest.json` | Machine-readable completion gate |
| `evidence-index.json` | Artifact paths, ownership and SHA-256 checksums |

```text
.gcw/
├─ SITE_SPEC.md
├─ teardown-manifest.json
├─ run-state.json
├─ CLONE_REPORT.md
├─ REPLACE_GUIDE.md
├─ editability-evidence.json
└─ evidence/
   ├─ evidence-index.json
   ├─ site-inventory.json
   ├─ route-map.json
   ├─ source-maps.json
   ├─ interaction-states.json
   ├─ screenshots/{desktop,mobile}/
   ├─ network/
   ├─ design-dna/design-dna.json
   └─ web-shader-extractor/
      ├─ gpu-decision.json
      ├─ scout-card.json          # GPU targets only
      └─ replay-manifest.json     # GPU targets only
```

`finalize_teardown.py` refuses to finalize when fixed evidence is empty, Design DNA is missing, GPU `N/A` lacks detection evidence, or a detected GPU target has not reached `TARGET_LOCKED` and `REPLAY_READY`. GCW summarizes these artifacts in SITE_SPEC but never copies or rewrites their native schemas.

## Quick start

### 1. Install GCW

Clone this repository as the canonical source:

```bash
git clone https://github.com/idonafraid-create/GCW.git /path/to/GCW
```

Link it into the singular `.agent/skills` directory used by this workspace.

Windows PowerShell:

```powershell
New-Item -ItemType Junction `
  -Path "D:\your-workspace\.agent\skills\gcw" `
  -Target "D:\path\to\GCW"
```

macOS or Linux:

```bash
ln -s /path/to/GCW /path/to/your-workspace/.agent/skills/gcw
```

### 2. Verify the toolkit

```bash
cd /path/to/GCW
npm install
npm run install:browser
python -m pip install -r requirements.txt
npm run check
```

`npm run check` verifies runtime dependencies and companion-skill discovery. A passing environment check does not prove that a particular clone is complete.

Before publishing changes to GCW itself, run the complete release suite:

```bash
npm run verify
```

This runs syntax checks, local HTTP/Chromium workflow tests, URL and credential-boundary tests, image-diff gates, CI-installer tests, and the environment check.

### 3. Ask for the outcome you want

```text
Use $gcw to study this site, explain its real implementation, and produce a technical teardown: https://example.com/
```

```text
Use $gcw to create a faithful local clone of this authorized public site: https://example.com/
```

```text
Use $gcw to extract the design DNA and rebuild this reference with my own content: https://example.com/
```

The skill performs a short preflight before choosing the tools and scope.

For a build, initialize the recorded contract explicitly. For example, choice B:

```bash
python /path/to/GCW/scripts/init_reconstruction.py /project \
  --url https://example.com \
  --authorization authorized \
  --outcome faithful-clone \
  --final-deliverable B
```

## What GCW can leave behind

- `.gcw/SITE_SPEC.md` and fixed route, interaction, network and screenshot evidence
- `teardown-manifest.json` and a checksummed evidence index
- Native Design DNA and conditional Shader Target Lock/Replay Ready artifacts
- Route and resource inventory
- A runnable local project and production build command
- `CLONE_REPORT.md` with the delivery contract, source-versus-local differences and known gaps
- `REPLACE_GUIDE.md` for text, media, color, font, model and data changes
- `editability-evidence.json` for maintainable source, controlled content-change, and runtime-independence proof
- Matched desktop/mobile screenshots, numeric diffs and visual reports
- Optional GitHub Actions screenshot regression

Recovery provenance and replay paperwork applies only when ownership/authorization is confirmed and maintainable source is unavailable. New recovered editable work uses strategy `MAINTAINABLE_REBUILD`; schema-v4 `EDITABLE_REBUILD` is a migrated legacy alias.

## Toolkit

| Script | Purpose |
|---|---|
| `init_reconstruction.py` | Create a non-destructive `.gcw/` project record with the final-delivery contract |
| `finalize_teardown.py` | Validate companion artifacts and finalize SITE_SPEC |
| `site_inventory.mjs` | Inventory routes and emit site, route-map, network, and source-map evidence |
| `detect_interaction_states.mjs` | Draft reviewed hover, focus, and expanded-state evidence with screenshots |
| `capture_compare.mjs` | Capture matched states plus opt-in redacted SPA HAR record/replay |
| `batch_image_diff.py` | Generate metrics, diff images and Markdown/JSON reports |
| `route_smoke.py` | Check preview routes and representative text |
| `generate_asset_manifest.py` | Draft a safe, review-gated asset manifest from inventory |
| `install_ci.py` | Install the GCW visual-regression runner and workflow |
| `advance_workflow.py` | Record transitions, migrate schema-v4 strategy names, and enforce review/editability gates |
| `download_assets.py` | Reproducibly download authorized manifest assets |
| `check_runtime_independence.py` | Gate source-origin requests and URLs embedded in final builds |
| `blender_replace_text.py` | Optional playbook for text baked into GLTF/GLB geometry |

Read [SKILL.md](./SKILL.md) for the agent workflow. The [references](./references/) directory defines phases, SITE_SPEC, provenance, runtime independence, recovery, QA, tooling and special cases.

## Visual verification

Define source and candidate scenarios, then capture and compare matched states:

```bash
node scripts/capture_compare.mjs \
  --config /project/.gcw/capture-scenarios.json \
  --output /project/.gcw/results

python scripts/batch_image_diff.py \
  /project/.gcw/results \
  --diff-dir /project/.gcw/results/diff
```

GCW can align random seed, JavaScript time, viewport, DPR, route, pointer, scroll and readiness. GPU drivers, video, cross-origin frames, workers and compositor timing can still introduce noise; record those regions instead of weakening every threshold.

## Requirements

- Python 3.10+
- Node.js 20+
- Pillow
- Playwright and Chromium
- Blender 4.x only for the optional baked-3D-text playbook

## Safety and reuse

Use GCW only when the target is owned by the user, licensed for the intended reuse, or explicitly authorized.

- Do not bypass authentication, passcodes, paywalls or other access controls.
- Use the final canonical URL; credential-bearing URLs and cross-origin document redirects are rejected before browser capture.
- Check code and asset licenses separately before publishing a clone or adaptation.
- Remove tracking and original brand residue from creative rebuilds.
- Do not commit credentials found in public bundles or configuration.
- Represent every implementation-critical conclusion in SITE_SPEC section 9 and mark it `SOURCE`, `PARTIAL` or `GUESS`; teardown cannot finalize with an invalid subsystem truth/fidelity row.

## Acknowledgments

GCW's first reconstruction benchmark and production-recovery case used [haoqi.design](https://haoqi.design/) as its public reference. Thanks to its creator, Haoqi Wen, whose site provided a real-world test bed for route recovery, WebGL forensics, deterministic visual comparison, and the baked 3D-text workflow. GCW is an independent project; this acknowledgment credits the reference work, not authorship of this repository.

GCW coordinates the independently maintained `web-shader-extractor` and `design-dna` workflows; it does not vendor their source. See the upstream repositories for current licenses and updates.

## License

GCW is available under the [MIT License](./LICENSE).
