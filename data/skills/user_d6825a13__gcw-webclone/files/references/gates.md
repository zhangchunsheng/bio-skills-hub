# Workflow gates

| Gate | Required proof | Blocking failure |
|---|---|---|
| Teardown complete | Passed `teardown-manifest.json`, final `SITE_SPEC.md`, complete Design DNA, and Shader `TARGET_LOCKED` + `REPLAY_READY` or evidence-backed GPU `N/A` | Missing artifact, placeholder, blocking unknown, companion gate, or critical evidence |
| Baseline verified | Build, routes, desktop/mobile/key-state comparison, subsystem fidelity table; for `MAINTAINABLE_SOURCE`, confirmed `editability-evidence.json`, maintainable source entrypoint, completed `REPLACE_GUIDE.md`, controlled content-change proof without production-bundle edits, and runtime-independence proof | Open P0/P1/P2, unreported approximation, incomplete editability proof, or artifact-only final candidate |
| Review | Preview, screenshots, Diff, completed `CLONE_REPORT.md`, Known Gaps, and the persisted Final deliverable/Editability target | User has not chosen A, B, or C, or the selected delivery contract is not met |
| Creative brief | Keep/remove/change/new direction and final acceptance target | Missing explicit user decision |
| Resume Creative | Completed choice-B review decision, still-valid editability proof, explicit decision C, and completed `CREATIVE_BRIEF.md` | Choice A, missing accepted B baseline, stale/invalid editability proof, or incomplete brief |
| Runtime independence | No source-origin requests except explicit legal allowlist | Undeclared source runtime dependency |
| Closeout | Handoff, known gaps, Git status, deploy notes | Skipped work not reported |

Recovery configuration additionally requires provenance/hashes, replay strategy, complete routes, deployment continuity, and long-term regression CI. `ARTIFACT_REPLAY` may complete choice A, but is oracle-only for choices B/C. A recovered `MAINTAINABLE_SOURCE` delivery must use final strategy `MAINTAINABLE_REBUILD`. Do not impose recovery-only paperwork on ordinary reconstruction.

Severity: `P0` cannot run; `P1` wrong target or primary behavior; `P2` visible layout/timing/responsive/input drift; `P3` non-blocking polish. Record facts as `SOURCE`, `PARTIAL`, or `GUESS`.
