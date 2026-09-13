# Acceptance Criteria - Hearing Protection Day Kit

## Gate Checks

- [x] `SKILL.md` exists and contains a prompt-only workflow.
- [x] `skill.json` is valid JSON and declares `version=1.0.0`, `license=MIT-0`, `language=en`, and `hasExecutableCode=false`.
- [x] File count is exactly 3: `SKILL.md`, `skill.json`, and `ACCEPTANCE.md`.
- [x] Public-facing documentation is English only.
- [x] No executable code, scripts, package files, network calls, APIs, credentials, secrets, or private data are included.
- [x] Trigger scenario, concrete deliverable, workflow, output format, and safety boundary are explicit.
- [x] The workflow produces a noisy day snapshot, noise block plan, carry-kit checklist, break and recovery plan, fit and comfort notes, discomfort log, and follow-up guidance.
- [x] The skill stays within everyday readiness and does not provide medical, audiology, or workplace compliance advice.
- [x] The safety boundary recommends qualified professional help for pain, sudden hearing changes, persistent ringing, muffled hearing after noise, injury, or urgent symptoms.
- [x] The safety boundary routes regulated work noise questions to employer procedures, product instructions, and qualified occupational safety guidance.
- [x] No CJK characters are present.

## Clean Scan Evidence

- [x] No secrets, tokens, passwords, API keys, or private keys.
- [x] No executable code, scripts, package.json, or build artifacts.
- [x] No network calls, outbound requests, or external API dependencies.
- [x] No credential handling or environment-variable leakage.
- [x] No binary files, compiled code, or platform-specific executables.
- [x] No temp files, logs, .DS_Store, or editor artifacts.
- [x] Document-only, prompt-only, no execution required.
- [x] Language content is English with no CJK-dominant paragraphs.

## Install-First Success Path

**Input:** User describes a noisy day (concert, commute, tools, class, event) with expected loud blocks, duration, available protection, communication needs, and comfort constraints.

**Steps:**
1. Read the skill metadata and verify document-only, prompt-only safety.
2. Review the workflow: safety check, map the day, match protection to context, add break points, build the carry kit, plan use moments, track discomfort, close with follow-up guidance.
3. Ask for any missing inputs (expected loud blocks, protection available, communication needs, comfort constraints).
4. Produce the Hearing Protection Day Kit with all 8 required sections.

**Output:** A complete noisy-day readiness plan with safety note, day snapshot, noise block plan, carry-kit checklist, break and recovery plan, fit/comfort/communication notes, discomfort log, and follow-up guidance — ready for immediate use with no additional tools, files, or network access.

## Scope

- Prompt-only MVP.
- Local implementation only.
- Not published to ClawHub in this phase.

## Review Status

- Implemented by: Golden Bean / coder
- Date: 2026-05-11
- Status: Ready for cross-review and test.
- V2 remediated: 2026-05-14 09:40 (Clean Scan Evidence, Install-First Success Path)
