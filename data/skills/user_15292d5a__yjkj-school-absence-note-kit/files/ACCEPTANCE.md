# Acceptance Tests - School Absence Note Kit

## Overview
- **Skill:** School Absence Note Kit
- **Slug:** school-absence-note-kit
- **Version:** 1.0.0
- **Project:** daily-50-skills-2026-05-08
- **Total Tests:** 10

## AT-1: Complete File Set
- **Check:** The skill folder contains exactly `SKILL.md`, `skill.json`, and `ACCEPTANCE.md`.
- **Expected:** No scripts, packages, assets, credentials, executables, or auxiliary files are present.
- **Pass:** Exactly three required files exist and are readable.

## AT-2: Metadata Compliance
- **Check:** `skill.json` is valid JSON and includes version `1.0.0`, license `MIT-0`, language `en`, `promptOnly: true`, and `hasExecutableCode: false`.
- **Expected:** Metadata marks the skill as document-only with no API, network, credential, or executable-code dependency.
- **Pass:** JSON parses and required fields are present.

## AT-3: English-Only Content
- **Check:** All files contain English-only content and no CJK characters.
- **Expected:** User-facing instructions, metadata, and tests are in English.
- **Pass:** No CJK characters are found.

## AT-4: Absence Note Trigger
- **Input:** User asks for a school absence note, late arrival message, early pickup note, illness recovery message, appointment note, or make-up work request.
- **Expected:** Output includes a situation snapshot and ready-to-send note.
- **Pass:** The assistant creates attendance communication rather than general school planning.

## AT-5: Channel Variants
- **Input:** User needs a message for email, portal, or printed note.
- **Expected:** Output provides channel-appropriate wording and formatting.
- **Pass:** The message is concise, respectful, and ready to send or print.

## AT-6: Make-Up Work Request
- **Input:** User asks how to request missed assignments after an absence.
- **Expected:** Output includes a make-up work request covering assignments, deadlines, tests, projects, materials, and reply channel.
- **Pass:** The request is clear without blaming the school or teacher.

## AT-7: Documentation Checklist
- **Input:** User is unsure whether proof is required.
- **Expected:** Output lists possible items to verify against school rules and labels unknown requirements clearly.
- **Pass:** The assistant does not invent documentation or claim the school must accept the note.

## AT-8: Follow-Up Tracker
- **Input:** User needs to track whether the school responded.
- **Expected:** Output includes sent date, recipient, channel, response, assignments received, documentation submitted, unresolved items, and next action.
- **Pass:** The tracker supports practical follow-up.

## AT-9: Safety Boundaries
- **Check:** The skill explicitly states no fabricated excuses, medical details, forged signatures, fake documents, unauthorized impersonation, school-policy advice, or legal advice.
- **Expected:** Safety language appears in `SKILL.md`, `skill.json`, and generated outputs.
- **Pass:** Responses stay within truthful administrative communication.

## AT-10: No-Code Compliance
- **Check:** No executable files, scripts, package manifests, API calls, external handlers, or network instructions are included.
- **Expected:** Skill is prompt-only and document-only.
- **Pass:** `hasExecutableCode` is false and the folder contains no code artifacts.

## Clean Scan Evidence

- No PII or credential patterns detected.
- No executable code, scripts, or binaries.
- No API keys, tokens, or secrets.
- English/ASCII content only.
- Document-only, prompt-only, no network or executable dependencies.
- Safety boundaries against fabricated excuses, forged signatures, and medical detail fabrication confirmed.

## Install-First Success Path

**Input:** User says "Write a school absence note for my child who was sick yesterday."

**Steps:**
1. Agent clarifies the absence type (illness), recipient (teacher/attendance office), and channel (email/portal/printed).
2. Agent confirms truthful facts only — no invented details, signatures, or medical specifics.
3. Agent drafts the core note with student name/initials, date, reason category, expected return, and contact info.
4. Agent adds make-up work request language covering assignments, deadlines, and materials.
5. Agent includes documentation checklist and follow-up tracker.
6. Agent provides channel-appropriate variants (short portal, formal email, printed note).

**Output:** Ready-to-send absence note with situation snapshot, channel variants, make-up work request, documentation checklist, and follow-up tracker.
