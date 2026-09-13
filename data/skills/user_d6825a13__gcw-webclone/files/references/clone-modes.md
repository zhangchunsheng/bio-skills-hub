# Workflow phases and outcomes

GCW uses one staged workflow, not four parallel modes:

```text
TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD
```

`TEARDOWN_PHASE` is mandatory. A study-only task stops there and may be described externally as `TEARDOWN`. `FAITHFUL_CLONE` may be the final outcome or the baseline for later creative work. Never enter `CREATIVE_REBUILD` until the user accepts the baseline at `REVIEW_GATE`.

Before any build work, ask the ordinary user to choose one final-deliverable contract. Do not infer or default this choice from a user profile:

| Choice | Final deliverable | Editability target |
|---|---|---|
| A | `RESEARCH_OR_RUNNABLE_REPLAY` | `RUNNABLE_REPLAY` |
| B | `EDITABLE_FAITHFUL_CLONE` | `MAINTAINABLE_SOURCE` |
| C | `EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE` | `MAINTAINABLE_SOURCE` |

Choice A may stop after research or deliver an explicitly replay-only build. Choices B and C require editability inside `FAITHFUL_CLONE`; `CREATIVE_REBUILD` begins only after the editable faithful baseline passes review and is limited to content, brand, and approved innovation. Choice B is a durable checkpoint: it may be upgraded to C during review or resumed later from `COMPLETE` with a new Creative Brief and explicit decision C.

Every `TEARDOWN_PHASE` requires `design-dna` before its deliverables are finalized, including study-only work. Canvas/WebGL/WebGPU/shader surfaces additionally require `web-shader-extractor`; when inventory evidence confirms none exist, record GPU analysis as `N/A`. Integrate both decisions and all resulting evidence into `SITE_SPEC.md` before leaving teardown.

## Visible preflight

Show `Outcome`, `Final deliverable`, `Editability target`, `Current phase`, `Site type`, `Ownership/authorization`, `Source availability`, `Baseline scope`, `Implementation path`, and `Approximate or excluded scope`. Ask the A/B/C question for build work even when the remaining scope is clear. Ask one additional path-changing question when intent or authorization is ambiguous. Record scope changes.

## Faithful implementation paths

| Condition | Path |
|---|---|
| Reusable official source is legally available | `SOURCE_ADAPT` |
| Public evidence is sufficient for a clean implementation | `CLEAN_REBUILD` |
| User confirms ownership/authorization and maintainable source is unavailable | `PRODUCTION_RECOVERY` |

`PRODUCTION_RECOVERY` is a conditional recovery configuration, never a user-facing parallel mode. Read `recovery-tiers.md` and `gates.md` only when both recovery conditions are met.

For choices B and C, `ARTIFACT_REPLAY` may establish an oracle but cannot be the final recovery strategy. A recovered editable delivery records `MAINTAINABLE_REBUILD` and must pass the same editability gate as other maintainable-source paths.

## Review gate choices

- Fidelity insufficient: return to `FAITHFUL_CLONE`.
- Baseline accepted as final: stop at B; the accepted editable baseline remains eligible for a later C upgrade.
- Baseline accepted for innovation: create `.gcw/CREATIVE_BRIEF.md`, then enter `CREATIVE_REBUILD`.

Resuming from completed B revalidates the recorded B review decision, delivery contract, editability evidence, and Creative Brief. Choice A has no maintainable-source baseline and cannot resume Creative.
