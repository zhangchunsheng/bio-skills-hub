---
name: sunscreen-reapply-outdoor-card
description: "Create a pocket sunscreen reapply card for outdoor days, with start time, product-label reminders, water or sweat resets, shade breaks, gear checklist, and severe sunburn care escalation without making medical claims."
---

# Sunscreen Reapply Outdoor Card

## Purpose

Help the user turn an outdoor window into a simple, visible reapply plan. The deliverable is a pocket card or printable note with sunscreen start time, reminder times, shade breaks, gear, and after-outdoor cleanup.

This is a prompt-only planning workflow. It does not provide medical advice, does not claim sunscreen prevents all harm, and does not replace the directions on the sunscreen product label. The user should read and follow the product label, especially for water resistance, swimming, sweating, towel drying, spray warnings, children, and sensitive skin.

## Use This Skill When

Use this skill when the user wants to:

- Plan sunscreen reminders for a beach day, pool day, sports sidelines, hiking, gardening, outdoor work, festival, commute, school event, or travel day.
- Convert an outdoor start and end time into reapply alarms.
- Pack sun-protection gear such as sunscreen, hat, sunglasses, clothing, shade, lip balm, and water.
- Account for swimming, sweating, towel drying, or changing activities.
- Make a pocket card for a group, child, team, family, guest, or caregiver to follow.

Do not use this skill to diagnose or treat sunburn, recommend medical products, evaluate skin lesions, decide whether someone can safely stay in the sun, or override a clinician, product label, school, workplace, event, or local safety rule.

## Best Inputs

Ask only for details that make the card practical. If details are missing, proceed with clear assumptions.

- Date, location, outdoor start time, end time, and time zone.
- Activities: beach, pool, hiking, sports, work, gardening, driving, event, travel, or school.
- Whether swimming, heavy sweating, towel drying, water play, or changing clothes is expected.
- Sunscreen product details the user can read from the label: SPF, broad spectrum, water resistance duration, directions, warnings, and age guidance.
- People included, using names or initials if useful.
- Gear available: hat, sunglasses, protective clothing, shade, umbrella, canopy, lip balm, water, bag, or cooler.
- Reminder preference: phone alarms, watch timers, printed card, caregiver handoff, or group checklist.

If the product label is unknown, avoid inventing it. Use a conservative placeholder: "Follow the product label; many labels call for reapplying at least every 2 hours and after swimming, sweating, or towel drying."

## Workflow

1. **Set the scope.** State that this is a planning card and that the user should follow the sunscreen product label.
2. **Map the outdoor window.** Capture arrival, first application, outdoor blocks, water or sweat blocks, shade breaks, meals, travel, and departure.
3. **Read label-dependent rules.** Ask the user to check SPF, broad spectrum, water resistance duration, warnings, child guidance, spray safety, and reapply instructions. Do not guess product-specific claims.
4. **Build reminder times.** Create alarms from the first application time, then add resets after swimming, sweating, or towel drying according to the label.
5. **Add shade and gear.** Include shade breaks, protective clothing, hat, sunglasses, lip balm, extra sunscreen, water, and storage notes.
6. **Assign owners.** For groups, assign who carries sunscreen, who sets alarms, who checks children or guests, and who confirms reapply moments.
7. **Add a severe-burn escalation note.** If the user reports severe burns, blistering over a large area, fever, chills, confusion, fainting, dehydration concerns, severe pain, eye involvement, infection signs, or a burn involving an infant or medically vulnerable person, advise seeking urgent care or local medical help.
8. **Produce the card.** Keep it compact enough to screenshot, print, or copy into a note.

## Output Format

Return the card in this order:

1. **Outdoor Snapshot**

| Field | Detail |
|---|---|
| Date and location | |
| Outdoor window | |
| First sunscreen application | |
| Activities | |
| Swimming, sweating, or towel drying expected | |
| Product-label details known | |
| People included | |
| Assumptions | |

2. **Pocket Reapply Card**

```text
SUNSCREEN REAPPLY CARD
Outdoor window:
First apply:
Follow label:
Alarm 1:
Alarm 2:
Water/sweat/towel reset:
Shade break:
Gear check:
Owner:
```

3. **Reminder Schedule**

| Time | Action | Reason | Owner |
|---|---|---|---|
| | Apply before outdoor exposure | Product-label direction | |
| | Reapply | Label or 2-hour reminder | |
| | Reset reminder | Swimming, sweating, or towel drying | |
| | Shade or clothing break | Reduce exposure | |

4. **Gear Checklist**

Use checkboxes:

```text
[ ] Sunscreen product and label checked
[ ] Enough sunscreen for the group
[ ] SPF lip balm, if used
[ ] Hat or visor
[ ] Sunglasses
[ ] Protective clothing or cover-up
[ ] Shade option
[ ] Water and snacks
[ ] Phone/watch alarms set
[ ] Bag note: keep sunscreen out of excessive heat when practical
```

5. **Label and Safety Notes**

Include concise notes:

- Read and follow the sunscreen product label.
- Use the label for water resistance, swimming, sweating, towel drying, spray warnings, children, and sensitive skin.
- Sunscreen is one part of sun protection; shade, clothing, hats, and sunglasses can reduce exposure.
- Seek care for severe burns or concerning symptoms instead of relying on this card.

6. **Open Questions**

List missing details such as exact product label, water resistance duration, first application time, outdoor schedule, child or group handoff, shade availability, or reminder preference.

## Message Style

- Keep the card practical, compact, and time-based.
- Use plain English, tables, and checkboxes.
- Prefer "follow the label" over product-specific claims when the label is not supplied.
- Make reminders easy to copy into alarms.
- Avoid medical certainty, diagnosis, treatment plans, claims that sunscreen prevents all burns, or advice to stay outdoors despite symptoms.

## Safety Boundary

- This skill provides general planning only and is not medical advice.
- Do not diagnose or treat sunburn, skin conditions, allergic reactions, heat illness, eye injury, or medication-related sun sensitivity.
- Do not recommend medicines, supplements, topical treatments, clinical cooling, or individualized medical care.
- Do not claim that any sunscreen product prevents all sunburn, skin damage, skin cancer, aging, or heat illness.
- Follow product labels and official guidance. For infants, sensitive skin, allergies, photosensitizing medications, pregnancy, immune suppression, prior skin cancer, or other medical concerns, suggest asking a qualified clinician or pharmacist.
- If severe burns or concerning symptoms are reported, recommend urgent local medical care or emergency services as appropriate.

## Example Prompts

- "Make me a sunscreen reapply card for 10 a.m. to 4 p.m. at the beach."
- "We have a soccer tournament all afternoon. Help me set sunscreen alarms."
- "Create a pocket card for my kids' pool day, with shade breaks and gear."
- "I will be gardening for four hours. Build a reapply checklist."
