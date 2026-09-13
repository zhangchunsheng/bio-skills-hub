---
name: Home First Aid Kit Audit Card
description: Use when a user wants to audit a home, car, dorm, travel, or workplace first aid kit for supply readiness, expired items, missing categories, storage labels, and restock actions. Produces a printable audit card and replenishment list while avoiding medical treatment advice, medication dosing, or diagnosis.
---

# Home First Aid Kit Audit Card

## Purpose

Create a practical audit card that helps the user inspect a first aid kit, identify missing or expired supplies, and make the kit easier to find and restock. Keep the work about readiness, storage, labels, and replacement planning.

## Boundaries

- This is not medical advice and must not diagnose, triage, or tell the user how to treat an injury.
- Do not provide medication dosing, medication selection advice, or instructions for using medicines.
- If the user mentions a serious injury, severe bleeding, trouble breathing, suspected poisoning, loss of consciousness, head/neck/spine injury, major burn, chest pain, stroke symptoms, anaphylaxis, or any situation that feels dangerous, tell them to contact local emergency services or urgent medical help immediately.
- For household-specific medical needs, tell the user to follow guidance from qualified clinicians, product labels, and local emergency preparedness authorities.
- If asked to include medications, limit the output to a neutral tracking row for item name, owner, expiration date, storage note, and who to ask before replacing it. Do not advise whether, when, or how to use it.

## Inputs To Request

Ask only for details that improve the audit card:

- Kit location and use case: home, car, travel, dorm, workshop, office, sports bag, or other.
- Household context that affects supplies: adults, children, older adults, pets, allergies, known clinician-directed emergency items, outdoor work, tools, kitchen, or travel.
- Current item list or a photo/text dump if available.
- Climate and storage concerns: heat, humidity, freezing, car trunk, bathroom cabinet, garage, or shared building.
- Restock preferences: local store, online order, budget cap, compact kit, or printable checklist only.

If the user lacks an inventory, guide them to empty the kit onto a clean surface and group items by category.

## Workflow

1. Define the kit mission.
   - Name where the kit lives, who may use it, and what situations it is meant to support.
   - Separate home kit, travel kit, car kit, and workplace kit needs when relevant.

2. Sort the contents into readiness categories.
   - Wound covering: adhesive bandages, sterile gauze, dressings, tape.
   - Cleaning and barrier items: antiseptic wipes, gloves, hand sanitizer, CPR face shield if present.
   - Tools: scissors, tweezers, thermometer, instant cold pack, flashlight, notepad, marker.
   - Wraps and support supplies: elastic bandage, triangular bandage, finger splint, safety pins.
   - Personal or clinician-directed items: track only presence, owner, expiration, and replacement source.
   - Documents: emergency contacts, allergy list, kit inventory, local emergency numbers.

3. Check readiness.
   - Mark each item as ready, low, missing, expired, damaged, opened, unclear, or not appropriate for this kit.
   - Flag items with damaged packaging, unreadable labels, moisture exposure, heat damage, or missing instructions.
   - Record expiration dates without recommending medical use.

4. Build the restock card.
   - List missing and expired items by priority: replace now, restock soon, optional upgrade, ask a professional.
   - Convert vague gaps into shopping quantities only when the user supplied a preferred kit size or existing checklist.
   - Keep medicine-related rows as "confirm with clinician/pharmacist or product label" rather than advice.

5. Make the visible kit label.
   - Include kit location, last audit date, next audit date, emergency number reminder, owner, and restock contact.
   - Add a short "return borrowed items here" line for shared households.

6. Close with a maintenance rhythm.
   - Suggest a recurring audit after expiration-heavy seasons, trips, moves, car storage changes, or every 6 to 12 months.
   - Recommend checking official preparedness resources or local emergency guidance for baseline kit lists.

## Output Format

Use this structure by default:

```markdown
# First Aid Kit Audit Card

## Kit Snapshot
- Kit location:
- Kit mission:
- People or context considered:
- Audit date:
- Next check:

## Quick Status
- Ready now:
- Replace now:
- Restock soon:
- Unclear or ask a professional:

## Item Audit
| Category | Item | Status | Expiration or condition | Action |
|---|---|---|---|---|
| Wound covering |  |  |  |  |
| Cleaning and barrier |  |  |  |  |
| Tools |  |  |  |  |
| Wraps and support |  |  |  |  |
| Personal/clinician-directed |  |  |  | Confirm with clinician, pharmacist, product label, or household plan. |
| Documents |  |  |  |  |

## Restock List
| Priority | Item | Why | Replacement note |
|---|---|---|---|
| Replace now |  |  |  |
| Restock soon |  |  |  |
| Optional upgrade |  |  |  |
| Ask a professional |  |  |  |

## Visible Kit Label
- Kit lives at:
- Emergency reminder: call local emergency services for serious or dangerous injuries.
- Last checked:
- Next check:
- Restock owner:

## Safety Boundary
This audit covers supply readiness only. It does not provide medical treatment instructions, diagnosis, or medication dosing. For serious injuries or dangerous symptoms, seek emergency care immediately.
```

## Quality Checks

Before finishing, verify that the output:

- Produces a concrete audit card, restock list, and kit label.
- Separates missing, expired, damaged, low, and unclear items.
- Keeps medications to tracking only and contains no dosing or treatment instructions.
- Escalates serious injuries to emergency care.
- Uses plain language suitable for printing or sharing with a household.

## Example Prompts

Copy and paste one of these to get started:

- "Audit my home first aid kit. I have bandages, antiseptic wipes, expired pain relief, and scattered supplies in a bathroom drawer."
- "Check my car first aid kit for summer readiness — it's been baking in the trunk for a year."
- "We're restocking the office first aid cabinet. Make an audit card and restock list from scratch."
