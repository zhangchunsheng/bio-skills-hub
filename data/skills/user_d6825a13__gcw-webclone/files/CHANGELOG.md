# Changelog

## Unreleased

## 1.4.0 - 2026-07-05

### Added

- Build preflight now persists an explicit A/B/C final-deliverable contract and gates maintainable-source delivery on source, replacement-map, controlled-change, and runtime-independence evidence.

### Changed

- Production recovery now names the maintainable strategy `MAINTAINABLE_REBUILD`; schema-v4 `EDITABLE_REBUILD` states migrate with an audit record, while `ARTIFACT_REPLAY` remains oracle-only for editable delivery.
- Choice B now remains upgradeable to C at review or after completion; resuming Creative revalidates the accepted editable baseline and requires an explicit decision C plus Creative Brief.

Full diff: `v1.3.0..v1.4.0`

## 1.3.0 - 2026-07-04

### Added

- Inventory now records redacted Source Map evidence from response headers, `sourceMappingURL` comments, and conventional `.map` probes, with bounded body reads and semantic v3 validation.
- Capture comparison now supports explicit per-scenario SPA HAR recording and offline replay with origin rebasing, credential/body redaction, Service Worker blocking, and network-fallback evidence.
- Interaction detection now drafts review-gated hover, focus, and common `aria-expanded` evidence with before/after screenshots and browser QA errors.
- Asset manifest generation now classifies and deduplicates inventory resources into deterministic local paths while gating downloads on explicit human review.

Full diff: `v1.2.1..v1.3.0`

## 1.2.1 - 2026-07-04

### Added

- Teardown depth profiles: `minimal`, `standard`, and `deep`.
- Machine-validated interaction-state schema, screenshot decoding, companion schema anchors, and review-decision history.
- Configurable inventory viewport plus generated route-map and network evidence.
- Public ADR for the staged workflow and conditional gates.

### Changed

- Image comparison now uses Pillow-native operations and one shared implementation.
- Capture scenarios use one canonical template and default to a light color scheme.
- Environment reporting separates base runtime readiness from teardown companion readiness.
- Skill commands resolve through `<skill-root>` and recognize both `AGENTS.md` and `CLAUDE.md` workspace instructions.

### Fixed

- Workflow transitions no longer fabricate a creative brief and now enforce `CLONE_REPORT.md` plus explicit A/B/C decisions.
- Teardown finalization validates all inputs before writing final state.
- Runtime-independence checks normalize default ports and inspect both network evidence and final build output.
- Asset downloads report per-item failures and reject every cross-origin redirect hop.
- Installed visual-regression CI invokes Playwright from `.gcw` and warns when non-Vite build commands need adaptation.

Full diff: `v1.2.0..1.2.1`
