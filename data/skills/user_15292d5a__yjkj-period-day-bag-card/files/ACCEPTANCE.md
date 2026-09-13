# Acceptance Criteria - Period Day Bag Card

## Gate Checks

- [x] `SKILL.md` exists and contains a prompt-only workflow.
- [x] `skill.json` is valid JSON and declares `version=1.0.0`, `license=MIT-0`, `language=en`, and `hasExecutableCode=false`.
- [x] File count is exactly 3: `SKILL.md`, `skill.json`, and `ACCEPTANCE.md`.
- [x] Public-facing documentation is English only.
- [x] No executable code, scripts, package files, network calls, APIs, credentials, secrets, or private data are included.
- [x] Trigger scenario, concrete deliverable, workflow, output format, and safety boundary are explicit.
- [x] The workflow produces a compact bag checklist, comfort plan, leak response plan, refill reminder, seek-care note, and open questions.
- [x] The skill avoids medical diagnosis, medication dosing, treatment changes, and product superiority claims.
- [x] The safety boundary flags severe pain, very heavy bleeding, fainting, fever, unusual discharge or odor, new or worsening symptoms, pregnancy concerns, and alarming symptoms for medical care.
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
- **Safety scan:** Clean — no medical diagnosis or treatment; no medication advice; no product superiority claims; seek-care flags for severe symptoms; body-neutral and discreet language; privacy-respecting intake

## Install-First Success Path

- **Input:** User says "I need a small period bag for school. I use pads and sometimes liners for backup. I have a locker and a backpack. Periods are usually 5 days, medium flow. Can you make me a checklist?"
- **Steps:** Skill identifies context: school, backpack/locker, 5-day coverage → builds core supplies: pads (enough for school day plus one extra), liners for backup → adds cleanup and privacy items: resealable bags for disposal, wipes, hand sanitizer, spare underwear, dark cloth pouch → adds comfort support: small heat patch if safe, water, snack → creates leak response plan: calm mini-script for changing, rinsing, storing items → sets refill cue: check pouch after each period or monthly → adds seek-care flags for severe pain, very heavy bleeding, or alarming symptoms → produces compact pocket card.
- **Output:** A discreet period day bag card with pack list (products, backup, cleanup, comfort, clothing), pocket-sized checklist, leak response plan, refill reminder, seek-care note, and open questions — all practical, body-neutral, and privacy-respecting with no medical diagnosis or product superiority claims.

## Scope

- Prompt-only MVP.
- Local implementation only.
- Not published to ClawHub in this phase.

## Review Status

- Implemented by: Golden Bean / coder
- Date: 2026-05-11
- Status: Ready for cross-review and test.
