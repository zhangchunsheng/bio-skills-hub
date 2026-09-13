# SITE_SPEC and teardown artifact contract

## Authority boundaries

- `.gcw/SITE_SPEC.md` is the single human-readable implementation specification.
- `.gcw/teardown-manifest.json` is the machine-readable teardown gate.
- `.gcw/evidence/evidence-index.json` indexes artifacts and checksums.
- Companion Skill artifacts remain authoritative for their native schemas. SITE_SPEC summarizes and links them; it never reproduces them wholesale.

Initialize SITE_SPEC as a draft and finalize it only after the complete teardown sequence. Standard and deep teardown keep all 12 numbered sections. The opt-in minimal profile is limited to simple non-GPU pages and keeps sections 1, 5, 9, and 12. Remove every `REQUIRED` placeholder and write `N/A` only with supporting evidence.

## Delivery-contract state

`run-state.json` schema version 5 persists two required preflight fields:

- `finalDeliverable`: `RESEARCH_OR_RUNNABLE_REPLAY`, `EDITABLE_FAITHFUL_CLONE`, or `EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE`.
- `editabilityTarget`: `RUNNABLE_REPLAY` for choice A or `MAINTAINABLE_SOURCE` for choices B/C.

New build initialization requires `--final-deliverable A|B|C`. Teardown-only initialization records the current research/replay result as choice A but sets `deliveryContractConfirmedForBuild: false`, so a later transition into `FAITHFUL_CLONE` must still record an explicit user choice. A schema-v4 state without these fields migrates to `UNCONFIRMED` and the same unconfirmed flag. Pass `--final-deliverable A|B|C` to `advance_workflow.py` before `REVIEW_GATE` to confirm or update a migrated contract. The legacy recovery strategy `EDITABLE_REBUILD` migrates to `MAINTAINABLE_REBUILD` with a timestamped `stateMigrations` entry.

SITE_SPEC section 1 must state both delivery fields. Section 10 must turn `MAINTAINABLE_SOURCE` into acceptance criteria rather than deferring editability to `CREATIVE_REBUILD`.

Choice B remains an accepted, reusable checkpoint. A decision C at `REVIEW_GATE`, or an explicit C resume from a completed B delivery, updates `finalDeliverable` and `outcome`, appends `deliveryContractHistory`, and records the transition in `reviewDecisions`. Resuming from `COMPLETE` requires the earlier accepted B decision and revalidates the editability evidence; choice A is not eligible.

## Fixed evidence

Every task preserves:

```text
.gcw/evidence/
├─ evidence-index.json
├─ site-inventory.json
├─ route-map.json
├─ source-maps.json
├─ interaction-states.json
├─ screenshots/desktop/
├─ screenshots/mobile/
├─ network/
├─ design-dna/design-dna.json
└─ web-shader-extractor/gpu-decision.json
```

Run `design-dna` during standard and deep teardown and keep its complete three-dimension JSON. It is recommended but non-blocking for minimal teardown. SITE_SPEC section 4 summarizes only implementation-critical Design System, Design Style, and Visual Effects findings.

When a Canvas/WebGL/WebGPU/shader target exists, set `gpu-decision.json.decision` to `required`, run `web-shader-extractor`, and preserve its native `scout-card.json`, `replay-manifest.json`, `run-state.json`, and evidence tree in the same namespace. Before finalizing teardown, `scout-card.json` must be `TARGET_LOCKED`, `replay-manifest.json` must be `REPLAY_READY`, and no blocking replay unknown may remain. Raw Replay and QA belong to the faithful baseline phase.

When reconnaissance confirms no qualifying GPU surface, set the decision to `not-applicable` and record checked surfaces plus detection-evidence paths. Do not create fake Shader artifacts.

## Interaction-state schema

`interaction-states.json` uses schema version 1 and requires at least one observed state. Every state records the route, trigger, expected result, and evidence paths:

```json
{
  "schemaVersion": 1,
  "reviewStatus": "confirmed",
  "states": [
    {
      "id": "menu-open",
      "route": "/",
      "trigger": "click header menu button",
      "triggerType": "aria-expanded",
      "elementSelector": "#menu-button",
      "expected": "navigation overlay is visible",
      "before": {"ariaExpanded": "false"},
      "after": {"ariaExpanded": "true"},
      "evidence": ["screenshots/mobile/menu.before.png", "screenshots/mobile/menu.after.png"]
    }
  ]
}
```

`detect_interaction_states.mjs` writes `reviewStatus: pending`. Generated evidence must be reviewed, false positives removed, missing script-driven states added, and the status changed to `confirmed` before teardown finalization. Legacy manually authored schema-v1 files without `reviewStatus` remain valid.

## Editability evidence schema

For `MAINTAINABLE_SOURCE`, `.gcw/editability-evidence.json` schema version 1 is a formal `FAITHFUL_CLONE` gate. Before entering `REVIEW_GATE`, set `reviewStatus` to `confirmed` and provide:

- a workspace-relative maintainable source entrypoint outside production output directories;
- a completed `.gcw/REPLACE_GUIDE.md` content replacement map;
- a controlled content change with source file, field, distinct before/after values, build command, proof paths, and `productionBundlesModified: false`;
- `runtimeIndependence.status: passed` with evidence paths;
- `artifactReplayRole` set to `not-used` or `oracle-only`.

All referenced files must exist inside the workspace. `ARTIFACT_REPLAY` in `run-state.json.recoveryStrategy` blocks this gate. Under `PRODUCTION_RECOVERY`, the final strategy must be `MAINTAINABLE_REBUILD`.

## SITE_SPEC synthesis rules

- Design DNA answers what the design looks and feels like.
- Web Shader Extractor answers how the target rendering system actually runs.
- For implementation facts, target-bound Shader evidence outranks qualitative Design DNA inference.
- Record conflicts; never average them.
- Represent every implementation-critical conclusion in the subsystem table. Record both fidelity (`Exact`, `Approximate`, `Unknown`, `Excluded`) and truth (`SOURCE`, `PARTIAL`, `GUESS`).
- Classify unknowns as blocking, important, deferred, or external.

Add full route maps, motion state timelines, asset manifests, provenance/hashes, and recovery strategy only when their documented conditions apply.
