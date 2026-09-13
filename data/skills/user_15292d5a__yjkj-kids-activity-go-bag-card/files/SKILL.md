---
name: kids-activity-go-bag-card
description: Create reusable kids activity go-bag checklist cards for practice, class, lessons, playdates, and outings using activity, weather, location, and timing details while avoiding medical or sensitive child information.
---

# Kids Activity Go-Bag Card

## Overview

Use this skill when a parent, guardian, caregiver, coach, or older child wants a simple packing card for a recurring activity. The goal is to reduce last-minute forgetting by creating a reusable checklist by activity type.

This is a packing readiness skill only. It does not provide medical, emergency, allergy, injury, medication, nutrition, transportation safety, or supervision advice. It should avoid sensitive child details and focus on ordinary gear, clothing, weather, timing, and return-home reset steps.

## Trigger

Use this skill when the user asks to:

- Build a packing checklist for a child's sport, class, lesson, club, practice, rehearsal, camp day, or outing.
- Make a reusable go-bag card for a recurring activity.
- Adapt a bag checklist for indoor, outdoor, hot, cold, rainy, or evening conditions.
- Create a door checklist for leaving on time.
- Make a reset checklist for after practice or class.

Do not use this skill for emergency kits, medical plans, allergy plans, medication management, injury care, or supervision rules.

## Intake

Ask only for practical packing context:

- Activity type, such as soccer, dance, swim, art class, music lesson, scouts, robotics, theater, tutoring, or playground outing.
- Age band only if it changes gear size or independence level; avoid full birth date or identifying details.
- Indoor, outdoor, pool, field, studio, classroom, or mixed location.
- Weather or season, if relevant.
- Duration and whether there is a snack or water break, if the user wants ordinary packing reminders.
- Required gear supplied by the activity provider.
- Optional comfort items or cleanup items.
- Preferred card size: tiny door card, bag tag, full checklist, or reset card.

If medical, allergy, medication, or emergency details come up, do not process them. Suggest keeping those with the appropriate provider-approved plan outside this packing card.

## Workflow

1. **Identify the activity.** Capture activity type, location, duration, weather, and required provider gear.
2. **Build the core bag.** List activity-specific gear, clothing, shoes, ordinary water bottle, towel, notebook, instrument, costume, or supplies as relevant.
3. **Add condition modules.** Include weather, indoor/outdoor, evening visibility, wet items, messy items, or uniform modules when applicable.
4. **Add departure checks.** Include quick reminders for time, location, required form or ticket if user supplied it, and bag-in-hand check.
5. **Add return reset.** Include unpack, wash, dry, restock, recharge, and place-back tasks.
6. **Separate optional from required.** Mark must-have, nice-to-have, and confirm-with-provider items.
7. **Minimize personal data.** Do not include child full name, medical information, emergency contacts, home address, school ID, or caregiver schedule unless the user specifically requests a non-sensitive label.
8. **Produce reusable card.** Make the output printable or copyable with checkboxes.
9. **End with scope notes.** State that the card is for packing readiness only and not medical or emergency guidance.

## Output Format

Return these sections:

1. **Card Setup**: activity, location, weather or season, duration, and assumptions.
2. **Must-Pack**: essential gear and clothing.
3. **Condition Add-Ons**: weather, wet, messy, evening, competition, recital, or provider-specific add-ons.
4. **Leave-the-House Check**: fast final checks before departure.
5. **After-Activity Reset**: laundry, drying, restocking, charging, and putting gear back.
6. **Confirm with Provider**: items that depend on coach, teacher, venue, camp, or class rules.
7. **Tiny Card Version**: compact version suitable for a door, bag tag, or note app.
8. **Privacy and Scope Notes**: no sensitive child data; no medical or emergency advice.

For a rushed request, provide Must-Pack, Leave-the-House Check, and Tiny Card Version first.

## Common Modules

Use these modules when relevant:

- **Sports field:** shoes, socks, uniform, protective gear required by the activity provider, water bottle, towel, change of clothes, ball or equipment if assigned.
- **Dance or gymnastics:** outfit, shoes, hair supplies, water bottle, cover-up, small towel, class card if needed.
- **Swim:** swimsuit, goggles, towel, dry clothes, wet bag, sandals, cap if required.
- **Art or messy class:** smock, washable clothes, folder, labeled supplies, cleanup bag.
- **Music lesson:** instrument, music book, notebook, pencil, tuner or accessory if used.
- **Outdoor weather:** layer, hat, rain layer, extra socks, sun or shade item if user normally uses it.
- **Evening visibility:** reflective item or small light if the user already uses one and it fits the venue rules.
- **Return reset:** empty trash, dry wet items, wash uniform, restock basics, place bag by door.

Keep modules practical and non-medical.

## Safety and Privacy Boundaries

- Packing readiness only; no emergency, medical, allergy, medication, injury, nutrition, transportation safety, or supervision advice.
- Avoid sensitive child data such as full identifying profiles, birth date, home address, medical details, medications, diagnoses, emergency contacts, school ID, or custody details.
- Do not create emergency plans, first-aid instructions, medication schedules, allergy instructions, or supervision ratios.
- If the user needs medical, allergy, medication, emergency, or safety planning, suggest following provider-approved instructions from a qualified professional or the activity organizer.
- Mark provider-dependent gear and rules as confirm with provider.

## Acceptance Criteria

1. Produces a reusable kids activity go-bag checklist card for the specified activity.
2. Separates must-pack, condition add-ons, leave-the-house checks, after-activity reset, and provider-dependent items.
3. Adapts to location, weather, duration, and activity type without collecting sensitive child data.
4. Avoids emergency, medical, allergy, medication, injury, nutrition, transportation safety, and supervision advice.
5. Includes a compact tiny card version suitable for visible reuse.
6. Requires no code execution, credentials, API access, network access, packages, or extra files.

## Example Prompts

- "Make a go-bag card for soccer practice after school."
- "We always forget dance shoes. Create a tiny checklist."
- "Build a swim lesson bag card with after-class reset."
- "Make an art class packing card for a messy project day."
- "Create an outdoor activity bag checklist for cool weather, no medical items."
