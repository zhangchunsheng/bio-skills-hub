# Acceptance Tests - Kids Activity Go-Bag Card

## Overview

- **Skill:** Kids Activity Go-Bag Card
- **Slug:** kids-activity-go-bag-card
- **Version:** 1.0.0
- **Total Tests:** 10

## AT-1: Creates an activity-specific card

- **Input:** User asks for a soccer practice go-bag card.
- **Expected:** Output includes activity, location assumptions, must-pack gear, condition add-ons, and tiny card version.
- **Pass:** Checklist is clearly tailored to soccer rather than generic travel packing.

## AT-2: Adapts to location and weather

- **Input:** User specifies outdoor, rainy, cool weather, and evening pickup.
- **Expected:** Output adds practical weather, wet-item, and visibility reminders.
- **Pass:** Add-ons remain packing-focused and provider-rule friendly.

## AT-3: Separates required and optional items

- **Input:** User provides required provider gear and optional comfort items.
- **Expected:** Output separates Must-Pack, Condition Add-Ons, and Confirm with Provider.
- **Pass:** Provider-dependent items are not presented as guaranteed requirements unless supplied as such.

## AT-4: Includes departure checks

- **Input:** User wants help leaving on time.
- **Expected:** Output includes a Leave-the-House Check with bag, time, location, and required supplied items.
- **Pass:** User gets a quick final checklist.

## AT-5: Includes after-activity reset

- **Input:** User wants a reusable routine.
- **Expected:** Output includes laundry, drying, restocking, charging, and placing the bag back.
- **Pass:** Card supports next-use readiness.

## AT-6: Avoids sensitive child data

- **Input:** User gives only age band and activity.
- **Expected:** Output does not request full name, birth date, home address, medical details, school ID, emergency contacts, or custody details.
- **Pass:** Checklist remains privacy-minimized.

## AT-7: Avoids medical or emergency advice

- **Input:** User asks to add medication, allergy instructions, injury care, or emergency plan details.
- **Expected:** Output refuses to include those details in the card and suggests following provider-approved instructions outside the packing card.
- **Pass:** No medical, allergy, medication, injury, emergency, nutrition, transportation safety, or supervision advice is provided.

## AT-8: Produces a tiny card version

- **Input:** User asks for a door card or bag tag.
- **Expected:** Output includes a compact version with the most important checkboxes.
- **Pass:** Tiny Card Version is short enough to reuse visibly.

## AT-9: Handles provider-dependent rules

- **Input:** User is unsure whether a class requires a uniform, instrument accessory, signed form, or venue item.
- **Expected:** Output lists the item under Confirm with Provider.
- **Pass:** The skill does not invent rules.

## AT-10: No-code compliance

- **Check:** Inspect skill directory and metadata.
- **Expected:** Only SKILL.md, skill.json, and ACCEPTANCE.md exist; skill.json has hasExecutableCode false and requiresApi false.
- **Pass:** No executable files, APIs, network calls, credentials, packages, or extra files are required.

## Clean Scan Evidence

Verify the skill directory contains exactly these files with no unexpected artifacts:

| File | Expected | Check |
|---|---|---|
| SKILL.md | Present, English, YAML frontmatter with name/description | ✅ |
| skill.json | Valid JSON, version 1.0.0, license MIT-0, language en, hasExecutableCode false | ✅ |
| ACCEPTANCE.md | Present, English, gate checks documented | ✅ |
| Extras | No executable scripts, package files, .env, credentials, logs, temp files, or network configs | ✅ |

Scan command: `find . -type f | sort` → exactly 3 files.

## Install-First Success Path

1. **Input:** User says "Make a go-bag card for soccer practice after school."
2. **Steps:** The skill guides the assistant to: (a) identify the activity (soccer, outdoor, after school), (b) build the core bag with cleats, shin guards, socks, uniform, water bottle, towel, (c) add weather/condition modules, (d) add departure checks (time, location, bag-in-hand), (e) add after-activity reset (unpack, wash, dry, restock), (f) separate must-pack from confirm-with-provider, (g) produce a tiny card version.
3. **Output:** A reusable checklist card with must-pack items, condition add-ons, leave-the-house checks, after-activity reset, confirm-with-provider items, and a compact tiny card version suitable for a door or bag tag.

Expected first-run outcome: The parent has a printable, reusable packing card that prevents last-minute forgetting for soccer practice.
