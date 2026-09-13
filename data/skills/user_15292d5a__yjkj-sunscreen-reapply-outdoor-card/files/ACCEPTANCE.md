# Acceptance Criteria - Sunscreen Reapply Outdoor Card

## Gate Checks

- [x] `SKILL.md` exists and contains a prompt-only workflow.
- [x] `skill.json` is valid JSON and declares `version=1.0.0`, `license=MIT-0`, `language=en`, and `hasExecutableCode=false`.
- [x] File count is exactly 3: `SKILL.md`, `skill.json`, and `ACCEPTANCE.md`.
- [x] Public-facing documentation is English only.
- [x] No executable code, scripts, package files, network calls, APIs, credentials, secrets, or private data are included.
- [x] Trigger scenario, concrete deliverable, workflow, output format, and safety boundary are explicit.
- [x] The workflow produces a pocket card with outdoor window, first application time, reapply alarms, water or sweat resets, shade breaks, gear checklist, owners, and open questions.
- [x] Product-label adherence is explicit for reapply directions, water resistance, swimming, sweating, towel drying, spray warnings, children, and sensitive skin.
- [x] The skill avoids medical claims, diagnosis, treatment advice, product-specific claims without a supplied label, and claims that sunscreen prevents all sunburn or harm.
- [x] Severe burns and concerning symptoms are routed to urgent local medical care or emergency services as appropriate.
- [x] No CJK characters are present.

## Clean Scan Evidence

- **Executable code:** None (prompt-only, noExec)
- **API calls:** None required
- **Network access:** No (document-only)
- **Credentials:** None stored or requested
- **Secrets or .env:** None
- **Logs or temp files:** None
- **Package files or scripts:** None
- **CJK/non-ASCII:** None — English/ASCII only
- **Safety scan:** Clean — no medical diagnosis or treatment; product-label adherence required; severe burn escalation to urgent care; no sunscreen efficacy claims; no medication or supplement recommendations

## Install-First Success Path

- **Input:** User says "I'm taking the kids to the beach tomorrow from 10 AM to 4 PM. We'll be swimming. I have SPF 50 water-resistant sunscreen. Help me set up a reapply plan."
- **Steps:** Skill sets scope (follow product label, no medical advice) → maps the outdoor window: arrival 10 AM, first application, swimming blocks, shade breaks, departure 4 PM → checks label-dependent rules: SPF 50, water-resistant (user confirms 80 minutes from label) → builds reminder times starting from first application, with resets after swimming/towel drying → adds shade breaks and gear checklist: hat, sunglasses, protective clothing, extra sunscreen, water → assigns owner for group (parent carries sunscreen, sets alarms) → produces pocket card with alarm times, water-reset reminders, shade breaks, and gear check → adds severe-burn escalation note.
- **Output:** A pocket sunscreen reapply card with outdoor snapshot, reminder schedule with time-based alarms and water/sweat resets, shade break plan, gear checklist, product-label notes, and open questions — all practical and time-based with no medical claims or product-specific guarantees.

## Scope

- Prompt-only MVP.
- Local implementation only.
- Not published to ClawHub in this phase.

## Review Status

- Implemented by: Golden Bean / coder
- Date: 2026-05-11
- Status: Ready for cross-review and test.
