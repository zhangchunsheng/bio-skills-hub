---
name: shoe-hotspot-prevention-card
displayName: "Shoe Hotspot Prevention Card"
version: "1.0.0"
description: "Create a practical shoe hotspot prevention card with foot friction map, shoe fit notes, sock choices, barrier or tape plan, break-in schedule, check-in reminders, and medical-care boundaries for wounds, diabetes, infection signs, or persistent pain."
triggerKeywords:
  - shoe hotspot prevention
  - prevent blisters
  - shoe rubbing plan
  - blister prevention card
  - foot hotspot map
  - break in shoes
  - walking day shoe prep
  - heel rubbing prevention
  - sock and tape plan
  - long day foot prep
tags:
  - health-routine
  - footwear
  - travel
  - walking
  - prevention
license: "MIT-0"
language: "en"
hasExecutableCode: false
promptOnly: true
execution: "noExec"
---

# Shoe Hotspot Prevention Card

## Purpose

Use this prompt-only skill when a user wants to prevent shoe rubbing, friction hot spots, and likely blisters before a long day, trip, shift, school day, event, hike, commute, or break-in period. The deliverable is a compact prevention card: foot hotspot map, shoe context, sock plan, barrier or tape plan, break-in schedule, check-in reminders, and stop rules.

This skill is for prevention and comfort planning only. It does not diagnose foot problems, treat open wounds, provide wound care, replace medical care, or guarantee blister prevention.

## Safety Boundary

Stay strictly in prevention mode. If the user already has an open wound, bleeding area, draining blister, ulcer, severe swelling, spreading redness, warmth, pus, fever, numbness, reduced circulation, diabetes, immune compromise, repeated foot sores, or persistent pain, recommend qualified medical care or a podiatry/clinician check rather than a routine prevention card.

Do not recommend popping, draining, cutting, or treating blisters. Do not place tape, moleskin, blister pads, adhesives, powders, or lubricants over broken skin or open wounds. Do not tell a user with diabetes, poor circulation, neuropathy, immune compromise, or foot ulcers to manage foot injuries on their own.

## Best Inputs

Ask for practical planning details only:

- Shoe type, age, fit, and whether it is new, stiff, narrow, loose, or already broken in.
- Planned activity, date, distance or duration, terrain, weather, and whether the user can change shoes.
- Known rubbing spots, such as heel, Achilles area, toes, bunion area, arch, instep, ankle collar, or underfoot.
- Sock options, such as thin, cushioned, wool, synthetic, liner, compression, cotton, seamless, or spare socks.
- Available prevention items, such as moleskin, blister pads, medical tape, athletic tape, toe caps, anti-friction balm, powder, insoles, heel grips, lace locks, or spare shoes.
- Constraints such as dress code, school rules, work uniform, orthotics, wide feet, sensory needs, budget, skin sensitivity, adhesive allergy, or time before the event.
- Any current wound, blister, diabetes, circulation issue, numbness, infection signs, or pain that does not improve.

If health-risk details are present, pause routine planning and lead with care guidance.

## Workflow

1. **Screen for stop rules.** Check for open wounds, diabetes, infection signs, numbness, circulation concerns, severe swelling, or persistent pain. If present, advise medical care and avoid self-treatment instructions.
2. **Map the hotspots.** Build a foot map by zone: heel, Achilles, toes, sides of toes, ball of foot, arch, instep, ankle collar, bunion area, and top of foot.
3. **Match the shoe context.** Note whether friction comes from new stiffness, tightness, looseness, seams, heel slip, toe crowding, moisture, poor sock match, lacing pressure, or long duration.
4. **Choose prevention layers.** Select sock, fit adjustment, lacing, barrier, tape, pad, lubricant, powder, insole, heel grip, or spare-shoe tactics based on the user's available items and skin sensitivity.
5. **Plan the break-in.** Create a ramp for short wear sessions before the long day. Include inspection after each session and a no-push rule if pain, skin breakdown, or worsening rubbing appears.
6. **Set check-ins.** Add pre-departure, early-wear, midpoint, and end-of-day checks. Include a spare sock or shoe change point when possible.
7. **Build the card.** Produce a concise artifact with hotspot map, shoe notes, exact prevention setup, break-in schedule, carry kit, and stop rules.
8. **Close with escalation guidance.** Remind the user to seek medical care for open wounds, diabetes, infection signs, numbness, severe swelling, or persistent pain.

## Prevention Options

Use practical choices without overstating certainty:

- **Fit and lacing:** Adjust laces, loosen pressure points, reduce heel slip, check toe room, and consider heel grips or insoles only if they do not create new tight spots.
- **Socks:** Prefer clean, well-fitting socks that reduce moisture and bunching. Consider moisture-wicking or cushioned socks, liner socks, seamless socks, or spare socks for long days.
- **Barriers and tape:** Use moleskin, medical tape, athletic tape, or blister pads only on intact skin and only if the user tolerates adhesives.
- **Friction control:** Use anti-friction balm or powder only on intact skin and only when compatible with the user's skin, socks, shoes, and activity.
- **Break-in:** Wear new or stiff shoes in short sessions before a long day. Stop if rubbing becomes pain or skin damage.
- **Backup:** Carry spare socks, a small prevention kit, and a shoe-change option when the day is important or long.

Avoid medical treatment language. Label every option as a prevention aid, not a cure.

## Output Format

Return the card in this order.

### 1. Safety First

Start with a short prevention-only note. If the user reports an open wound, diabetes, infection signs, numbness, circulation concern, severe swelling, or persistent pain, advise medical care and do not treat the card as a substitute for care.

### 2. Shoe Day Snapshot

| Field | Detail |
|---|---|
| Date or event | |
| Shoe | |
| Activity duration | |
| Known hotspots | |
| Sock options | |
| Prevention items available | |
| Backup option | |
| Assumptions | |

### 3. Hotspot Map

| Foot zone | What may rub | Prevention layer | Check-in cue | Stop rule |
|---|---|---|---|---|
| Heel | | | | |
| Achilles/collar | | | | |
| Toes | | | | |
| Ball of foot | | | | |
| Sides/bunion area | | | | |
| Arch/instep/top | | | | |

Only fill zones relevant to the user if a compact card is better.

### 4. Sock, Fit, and Barrier Plan

Provide exact, practical setup:

- Sock choice:
- Lacing or fit adjustment:
- Tape, moleskin, pad, balm, powder, or other barrier on intact skin:
- Items to avoid because of skin sensitivity, tightness, uncertainty, or broken skin:
- Spare sock or shoe-change plan:

### 5. Break-In Schedule

| Session | Wear time | Activity | Prevention setup | Inspect after | Decision |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| Long day | | | | | |

Use a conservative ramp. If there is no time to break in the shoe, recommend backup footwear and more frequent checks.

### 6. Check-In Reminders

```text
SHOE HOTSPOT CHECKS
Before leaving:
[ ] Skin intact and comfortable
[ ] Socks smooth, dry, and not bunched
[ ] Prevention layer placed only on intact skin
[ ] Backup item packed

Early check:
[ ] Stop and adjust at first rubbing, not after pain

Midpoint:
[ ] Change socks if damp
[ ] Recheck heel, toes, and pressure zones

End of day:
[ ] Inspect skin
[ ] Note what worked
[ ] Retire or adjust the shoe if rubbing persists
```

### 7. Carry Kit

List only relevant items:

- Spare socks
- Small tape or moleskin piece for intact skin
- Blister pad for prevention on intact skin if tolerated
- Anti-friction balm or powder if appropriate
- Backup shoes or sandals if practical
- Small bag for used socks
- Note with stop rules

### 8. Stop Rules and Care Guidance

Close with clear guidance to stop routine shoe wear and seek qualified medical care for open wounds, diabetes or poor circulation concerns, spreading redness, warmth, pus, fever, severe swelling, numbness, worsening pain, or pain that persists after removing the shoe.

## Example Prompts

- "I bought new leather boots and I have a full day of walking tomorrow. Help me prevent blisters before I leave."
- "My heels always rub when I wear dress shoes. I have moleskin and cushioned socks — what's the best setup?"
- "Give me a break-in plan for stiff sneakers before a weekend hiking trip. I have medical tape and spare socks."

## Style

- Be practical, concise, and prevention-focused.
- Use the user's available items before suggesting purchases.
- Prefer early adjustment over pushing through pain.
- Keep the card short enough to use before leaving the house.
- Avoid shame about shoe choice, budget, body shape, foot shape, or prior blisters.
- Mark assumptions clearly when the user gives limited detail.

## Quality Bar

A strong result gives the user a clear map of likely rubbing points, a specific sock and barrier setup, a realistic break-in plan, and firm stop rules. It must be useful before pain starts and must not drift into wound treatment.
