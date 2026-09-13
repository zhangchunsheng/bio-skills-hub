# Acceptance Criteria - Home First Aid Kit Audit Card

## Gate Checks

- [x] `SKILL.md` exists and contains a prompt-only workflow.
- [x] `skill.json` is valid JSON and declares `version=1.0.0`, `license=MIT-0`, `language=en`, and `hasExecutableCode=false`.
- [x] File count is exactly 3: `SKILL.md`, `skill.json`, and `ACCEPTANCE.md`.
- [x] Public-facing documentation is English only.
- [x] No executable code, scripts, package files, network calls, APIs, credentials, secrets, or private data are included.
- [x] Trigger scenario, concrete deliverable, workflow, output format, and safety boundary are explicit.
- [x] The workflow supports emptying the kit, sorting categories, checking dates and condition, marking gaps, creating a restock card, and producing a visible kit label.
- [x] The output distinguishes ready, low, missing, expired, damaged, opened, unclear, and ask-a-professional states.
- [x] Medication-related content is limited to neutral tracking and explicitly avoids dosing, medication selection advice, and treatment instructions.
- [x] Serious injuries and dangerous symptoms are escalated to emergency care or urgent medical help.
- [x] No CJK characters are present.

## Scope

- Prompt-only MVP.
- Local implementation only.
- Not published to ClawHub in this phase.

## Clean Scan Evidence

- [x] Secrets scan: no API keys, tokens, passwords, or credentials found.
- [x] Executable scan: no scripts, binaries, or executable code present.
- [x] Network scan: no outbound calls, fetch, or API endpoints.
- [x] File audit: only SKILL.md, skill.json, and ACCEPTANCE.md; no temp, logs, or build artifacts.
- [x] Language audit: English only; no CJK or mixed-script content.
- [x] Claims audit: all gate check claims verifiable against file contents.

## Install-First Success Path

- **Input:** User says "Help me audit my home first aid kit."
- **Steps:**
  1. Agent reads SKILL.md and asks for kit location, who uses it, and current item list or photo of contents.
  2. Agent sorts contents into readiness categories, checks expiration dates and condition, and marks gaps.
  3. Agent produces the audit card with item audit table, restock list by priority, and a printable visible kit label.
- **Output:** A complete First Aid Kit Audit Card with kit snapshot, item audit table sorted by category, status markers (ready/replace/restock/ask-professional), restock list, and a printable kit label — all without medical treatment advice or medication dosing.

## Review Status

- Implemented by: Golden Bean / coder
- Date: 2026-05-11
- Status: Ready for cross-review and test.
