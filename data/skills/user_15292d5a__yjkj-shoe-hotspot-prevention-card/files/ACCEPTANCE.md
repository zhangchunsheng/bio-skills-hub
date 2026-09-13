# Acceptance Checklist

- [x] SKILL.md has valid YAML frontmatter.
- [x] skill.json is present and valid JSON.
- [x] Version is 1.0.0 and license is MIT-0.
- [x] Language is English only.
- [x] Prompt-only metadata is present: promptOnly true, hasExecutableCode false, requires_api false, requiresApi false, no_code_execution true, execution noExec.
- [x] No executable code, scripts, package files, automation hooks, API requirements, credential needs, or network requirements.
- [x] Directory contains exactly SKILL.md, skill.json, and ACCEPTANCE.md.
- [x] Boundary is prevention routine only.
- [x] Boundary advises medical care for open wounds, diabetes, circulation or numbness concerns, infection signs, severe swelling, or persistent pain.
- [x] Boundary avoids blister popping, draining, wound treatment, and adhesive or powder use on broken skin.
- [x] Deliverable is a shoe hotspot prevention card with foot hotspot map, shoe context, sock plan, barrier or tape plan, break-in schedule, check-in reminders, carry kit, and stop rules.
- [x] Workflow covers screening for stop rules, mapping hotspots, matching shoe context, choosing prevention layers, planning break-in, setting check-ins, building the card, and closing with care guidance.
- [x] Official verification completed during development using current Mayo Clinic, American Academy of Dermatology, NHS, CDC, and MedlinePlus blister and foot-care guidance.
- [x] Slug matches the accepted design: shoe-hotspot-prevention-card.

## Clean Scan Evidence

Verify the skill directory contains exactly these files with no unexpected artifacts:

| File | Expected | Check |
|---|---|---|
| SKILL.md | Present, English, YAML frontmatter with name/description/version/type/tags/author | ✅ |
| skill.json | Valid JSON, version 1.0.0, license MIT-0, language en, hasExecutableCode false | ✅ |
| ACCEPTANCE.md | Present, English, gate checks documented | ✅ |
| Extras | No executable scripts, package files, .env, credentials, logs, temp files, or network configs | ✅ |

Scan command: `find . -type f | sort` → exactly 3 files.

## Install-First Success Path

1. **Input:** User says "I bought new leather boots and I have a full day of walking tomorrow. Help me prevent blisters before I leave."
2. **Steps:** The skill guides the assistant to: (a) screen for stop rules, (b) map the hotspots by foot zone, (c) match the shoe context, (d) choose prevention layers, (e) plan the break-in schedule, (f) set check-in reminders, (g) build the carry kit, (h) close with stop rules and care guidance.
3. **Output:** A shoe hotspot prevention card with safety-first note, shoe day snapshot, hotspot map, sock/fit/barrier plan, break-in schedule, check-in reminders, carry kit, and stop rules.

Expected first-run outcome: The user receives a practical prevention card they can review before leaving, with specific sock and barrier setup, a realistic check-in schedule, and clear medical-care boundaries.
