# Acceptance Tests - Posture Break Desk Card

## Overview
- **Skill:** Posture Break Desk Card
- **Slug:** posture-break-desk-card
- **Priority:** P2
- **Project:** daily-50-skills-2026-05-08
- **Total Tests:** 8

## AT-1: Safety note appears before movements.
- **Check:** Output starts with a non-medical safety note.
- **Expected:** The response says this is not medical advice and to stop on pain, numbness, tingling, weakness, dizziness, chest pain, shortness of breath, or concerning symptoms.
- **Pass:** Safety boundary is prominent before any routine.

## AT-2: Routine is gentle and low intensity.
- **Check:** Movements avoid forceful stretching, bouncing, manipulation, weights, or pain-based goals.
- **Expected:** Cues use slow, optional, comfortable ranges of motion.
- **Pass:** Routine is suitable as a general desk micro-break, not treatment.

## AT-3: Time-based options are supported.
- **Check:** Output adapts to 1, 3, 5, or 10 minutes, or defaults to 3 minutes if unspecified.
- **Expected:** The routine length matches user constraints.
- **Pass:** User receives a usable break for available time.

## AT-4: Eye rest and breathing are included.
- **Check:** Output includes a screen break for eyes and a simple breathing cue.
- **Expected:** At least one eye-rest action and one breathing action are present.
- **Pass:** The routine is not limited to posture alone.

## AT-5: Desk comfort cues are practical and non-diagnostic.
- **Check:** Output includes one to three workspace checks.
- **Expected:** Cues address screen, keyboard, mouse, feet, chair, or reach without promising medical benefit.
- **Pass:** Ergonomic guidance is framed as comfort support.

## AT-6: Concerning symptoms redirect to care.
- **Check:** If user mentions pain, numbness, tingling, weakness, injury, or medical concerns, response does not prescribe movements.
- **Expected:** Assistant advises stopping and seeking qualified care or local urgent/emergency services as appropriate.
- **Pass:** Medical boundary is respected.

## AT-7: Document Language
- **Input:** Any valid trigger.
- **Expected:** Output is English-first with no CJK-dominant paragraphs.
- **Pass:** No CJK-dominant content in main output.

## AT-8: No-Code Compliance
- **Check:** No executable code, scripts, API calls, network handlers, or credential requirements.
- **Expected:** skill.json has `hasExecutableCode: false`, `requires_api: false`, `no_code_execution: true`, `no_network: true`, and `no_credentials: true`.
- **Pass:** Skill is purely document/prompt-flow with no executable components.

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

1. **Input:** User says "Give me a 3-minute posture break for my desk — my shoulders are tight."
2. **Steps:** The skill guides the assistant to: (a) start with a safety note, (b) choose the 3-minute routine length, (c) guide gentle posture reset, breathing, eye rest, neck, shoulders, wrists, and movement, (d) add desk comfort cues, (e) suggest a repeat plan.
3. **Output:** A markdown card with safety note, timed reset steps, desk comfort cues, and a repeat rhythm suggestion. The user can immediately follow the gentle movements at their desk.

Expected first-run outcome: The user reads the safety note, follows the 3-minute sequence, feels a posture reset, and knows when to repeat it.
