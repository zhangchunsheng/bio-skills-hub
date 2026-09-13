---
name: pet-sitter-fridge-card
description: "Create a printable pet sitter fridge card with pet basics, feeding, walks or litter, quirks, supplies, home notes, emergency contacts, and vet information without giving medical dosing guidance."
---
# Pet Sitter Fridge Card

## Purpose

Use this skill when someone else will care for a pet for a day, evening, weekend, trip, emergency, or trial visit. The output is a fridge-ready care card that a sitter can print, save, or keep on their phone.

This is a prompt-only household handoff workflow. It organizes user-provided care instructions, routines, supplies, home notes, and contact information. It does not prescribe medication, change doses, diagnose symptoms, or replace veterinary guidance.

## Use This Skill When

Use this skill when the user asks to:

- Prepare instructions for a pet sitter, neighbor, family member, friend, dog walker, or house sitter.
- Make a short printable card instead of a long chat thread.
- Capture feeding, walking, litter, crate, bedtime, play, and cleanup routines.
- List pet quirks, escape risks, anxiety triggers, favorite rewards, or house rules.
- Include vet contact, emergency contact, supply locations, and basic home notes.

Do not use it to invent medical instructions, calculate medication doses, diagnose symptoms, or replace a vet's written plan.

## Best Inputs

Ask for only the details needed to make a usable card. If the user does not know an item, leave a blank field.

- Pet name, species, breed or type, age, size, photo note if useful, and temperament.
- Sitter dates, arrival and departure times, and whether overnight care is needed.
- Feeding schedule, food type, portions as provided by the user, treats, water, and forbidden foods.
- Walk, yard, litter, crate, cage, tank, bedding, play, grooming, and cleanup routines.
- Quirks, fears, hiding spots, door-dashing risks, bite or scratch risks, leash behavior, and other safety notes.
- Supply locations: food, treats, leash, harness, bags, litter, cleaning supplies, towels, carrier, toys, bedding, and spare keys.
- Vet clinic name, vet phone, emergency vet, owner's emergency contact, backup local contact, and preferred action if the sitter is worried.
- Home notes: entry instructions, alarm note, parking, Wi-Fi label, trash, thermostat, lights, plants, mail, and areas off-limits to pet or sitter.

Do not request passwords, alarm codes, lockbox codes, payment details, full addresses, or private personal data unless the user clearly chooses to include a safe shareable version for the sitter.

## Workflow

1. **Enter pet basics.** Capture each pet's name, species, temperament, care dates, and sitter role.
2. **Add daily care.** Record food, water, walks, litter or cleanup, play, rest, bedtime, and morning/evening routine.
3. **List quirks and safety notes.** Include escape risks, fears, triggers, handling preferences, prohibited foods, off-limit areas, and what not to do.
4. **Add supplies and home notes.** Create a fast map of where things are kept and what household instructions matter.
5. **Add contact fields.** Include owner, backup person, vet clinic, emergency vet, and permission note for the sitter to call if concerned.
6. **Create the fridge card.** Format a concise one-page version first, then add an optional detailed notes section if needed.
7. **Review gaps.** List missing information that should be filled in before the sitter arrives.

## Output Format

Return the card in this order:

1. **Fridge Card Header**

| Field | Detail |
|---|---|
| Pet name or pets | |
| Care dates | |
| Sitter name | |
| Owner contact | |
| Backup contact | |
| Vet clinic | |
| Emergency vet | |

2. **Daily Routine**

| Time | Task | Details |
|---|---|---|
| Morning | | |
| Midday | | |
| Evening | | |
| Bedtime | | |

3. **Food and Water**

| Item | Instruction |
|---|---|
| Food | |
| Portion | Use only the owner's stated portion. |
| Treats | |
| Water | |
| Foods to avoid | |

4. **Walk, Litter, Cleanup, or Habitat Care**

A practical checklist for the pet type.

5. **Quirks and Safety Notes**

| Situation | What to know | What to do |
|---|---|---|

6. **Supplies Map**

| Supply | Location |
|---|---|
| Food | |
| Leash or carrier | |
| Bags, litter, or cleaning supplies | |
| Towels or bedding | |
| Toys or comfort items | |

7. **House Notes**

Entry, parking, off-limit rooms, lights, trash, thermostat, mail, plants, and anything else the sitter needs.

8. **If Something Seems Wrong**

A calm escalation ladder: contact owner, backup contact, vet clinic, emergency vet, or local emergency services if immediate danger exists.

9. **Before You Leave Checklist**

Food secured, water filled, doors/windows checked, pet accounted for, litter or yard cleaned, lights/thermostat set, photo update sent if desired, key returned or locked up.

10. **Missing Details to Fill In**

A short list of blanks that should be completed before printing or sharing.

## Style Rules

- Make it printable and scannable.
- Use short sentences and clear labels.
- Put urgent contacts near the top.
- Separate pet-specific notes when there is more than one pet.
- Mark uncertain details as blanks instead of guessing.
- Keep medical notes limited to owner-provided instructions and vet contact information.

## Safety Boundary

- Do not provide medical dosing guidance, diagnose symptoms, suggest medication changes, or recommend treatment plans.
- Do not convert or calculate medication amounts. If the user mentions medication, record only the owner's exact written instruction or direct them to the vet's written instructions.
- Include vet and emergency vet fields, plus a clear instruction to call the owner or vet if concerned.
- Do not guarantee pet behavior, sitter performance, or emergency outcomes.
- Do not encourage unsafe handling of aggressive, highly fearful, sick, injured, exotic, or high-risk animals; suggest professional or veterinary support where appropriate.
- Do not ask for unnecessary sensitive home information. Use safe shareable placeholders for entry and security details.

## Example Prompts

- "Make a fridge card for my cat sitter this weekend."
- "I need simple dog care instructions for my neighbor."
- "Turn these pet care notes into a printable one-page card."
- "Help me write instructions for two cats with different feeding routines."
- "Create a sitter handoff card with vet info and house notes."
