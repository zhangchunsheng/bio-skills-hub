# Acceptance Criteria - Pet Sitter Fridge Card

## Gate Checks

- [x] `SKILL.md` exists and contains a prompt-only workflow.
- [x] `skill.json` is valid JSON and declares `version=1.0.0`, `license=MIT-0`, `language=en`, and `hasExecutableCode=false`.
- [x] File count is exactly 3: `SKILL.md`, `skill.json`, and `ACCEPTANCE.md`.
- [x] Public-facing documentation is English only.
- [x] No executable code, scripts, package files, network calls, APIs, credentials, secrets, or private data are included.
- [x] Trigger scenario, concrete deliverable, workflow, output format, and safety boundary are explicit.
- [x] The workflow captures pet basics, daily care, quirks, supplies, house notes, and contact fields.
- [x] The deliverable is a printable pet care card with feeding, routines, safety notes, supplies, home notes, vet information, and emergency contacts.
- [x] The safety boundary includes vet information and avoids medical dosing guidance, diagnosis, and treatment planning.
- [x] No CJK characters are present.

## Clean Scan Evidence

- [x] No executable code, scripts, package files, or install hooks.
- [x] No API endpoints, network calls, or external service dependencies.
- [x] No credentials, tokens, passwords, or private keys.
- [x] No secrets, environment variables, or configuration secrets.
- [x] No CJK characters; English/ASCII only.
- [x] No executable or network behavior; document-only skill.
- [x] No hidden files, temp files, or log files.
- [x] File count is exactly 3: SKILL.md, skill.json, ACCEPTANCE.md.

## Install-First Success Path

**Input:** User needs a printable care card for a pet sitter covering feeding, routines, and emergency contacts.

**Steps:**
1. Agent asks for pet name, species, temperament, sitter dates, feeding schedule, and routines.
2. Agent captures quirks, safety notes, supply locations, and home instructions.
3. Agent collects vet, emergency, and backup contact fields.
4. Agent formats a one-page printable fridge card with daily routine, food/water, walk/litter, quirks, supplies map, house notes, and emergency escalation ladder.
5. Agent lists missing details to fill in before the sitter arrives.

**Output:** A printable Pet Sitter Fridge Card with header, daily routine, food/water instructions, safety notes, supplies map, house notes, emergency contacts, and a before-you-leave checklist.

## Scope

- Prompt-only MVP.
- Local implementation only.
- Not published to ClawHub in this phase.

## Review Status

- Implemented by: Golden Bean / code
- Date: 2026-05-10
- Status: Ready for cross-review and test.
