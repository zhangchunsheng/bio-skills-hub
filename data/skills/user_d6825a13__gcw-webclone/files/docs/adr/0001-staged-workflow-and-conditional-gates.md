# ADR 0001: Staged workflow and conditional gates

Status: Accepted  
Date: 2026-07-02

## Context

GCW previously presented teardown, faithful cloning, creative rebuilding, and production recovery as parallel modes. That mixed workflow phases, desired outcomes, and source-availability conditions. It also left evidence depth and phase transitions too dependent on agent judgment.

## Decision

Use one visible staged workflow:

```text
TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD
```

- Teardown is mandatory but may be the final outcome.
- Production recovery is an implementation path enabled only for authorized work with unavailable or damaged maintainable source.
- The review gate requires baseline evidence and an explicit A/B/C user decision.
- Design evidence is required for standard and deep teardown; GPU forensics is conditional on detected Canvas, WebGL, WebGPU, or shader surfaces.
- Evidence remains in native companion schemas and is summarized, not duplicated, in SITE_SPEC.
- Runtime independence applies to final clean and creative rebuilds, not teardown itself.

Amendment, 2026-07-05:

- Every build records an explicit A/B/C final-deliverable contract before implementation.
- Choices B/C make maintainable-source editability a `FAITHFUL_CLONE` gate; it cannot be deferred to `CREATIVE_REBUILD`.
- `ARTIFACT_REPLAY` is oracle-only for B/C. Authorized recovery uses `MAINTAINABLE_REBUILD` as the final editable strategy; schema-v4 `EDITABLE_REBUILD` is a migrated legacy name.
- Runtime independence applies to every final `MAINTAINABLE_SOURCE` delivery, including an editable faithful clone that stops before Creative.
- Choice B is a durable accepted checkpoint. An explicit later decision C may resume `CREATIVE_REBUILD` from completed B after revalidating the B review record, editability evidence, and Creative Brief; choice A cannot resume this way.

## Consequences

The workflow has one source of truth, phase changes are auditable, and expensive gates apply only when target complexity warrants them. Simple non-GPU pages may opt into the minimal teardown profile while preserving the evidence tree, subsystem fidelity table, and finalization gate.
