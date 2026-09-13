---
name: Posture Break Desk Card
description: Build a brief, non-medical desk break routine that resets posture, movement, eyes, and breathing while stopping on pain, numbness, or concerning symptoms.
version: "1.0.0"
type: prompt-flow
tags:
  - desk-break
  - posture
  - ergonomics
  - wellness-routine
  - movement-break
author: Bell (design)
---

# Posture Break Desk Card

## Overview

Posture Break Desk Card helps users create a short desk break routine for ordinary workday stiffness and posture reset. It focuses on gentle movement, visual rest, breathing, and workspace cues.

This skill is not medical advice, physical therapy, diagnosis, or treatment. The routine must stop immediately if the user feels pain, numbness, tingling, weakness, dizziness, chest pain, shortness of breath, severe headache, sudden loss of coordination, or any other concerning symptom. For concerning, persistent, worsening, or unusual symptoms, advise the user to seek care from a qualified professional or local urgent/emergency services as appropriate.

## When to Use

Use this skill when the user asks for:

- A quick desk posture break
- A gentle stretch routine during computer work
- A reminder-friendly movement break
- Eye, neck, shoulder, wrist, or back reset ideas for office work
- A non-medical ergonomic micro-routine

**Trigger phrases:** "posture break", "desk stretch", "my shoulders are tight at work", "quick computer break", "ergonomic reset", "movement break at my desk".

## Inputs to Ask For

Ask only what improves fit without turning it into diagnosis:

- Available time: 1, 3, 5, or 10 minutes
- Space: seated only, standing allowed, or private room
- Constraints: headset, camera on, shared office, limited mobility
- Area that feels tired: eyes, neck, shoulders, wrists, back, hips, or general

If the user reports pain, numbness, tingling, weakness, injury, recent surgery, or a medical condition, do not prescribe movements. Give a conservative safety response and suggest professional care.

## Workflow

### Step 1 - Start With a Safety Check

Before giving movements, include a simple safety note:

- This is a gentle desk break, not medical advice.
- Stop immediately if anything hurts, feels sharp, causes numbness, tingling, weakness, dizziness, chest pain, shortness of breath, or other concerning symptoms.
- Use a smaller range of motion than you think you need.

### Step 2 - Choose the Break Length

Pick a routine length based on the user's time. If they do not specify, default to three minutes.

- **1 minute:** Reset posture, breathe, look away from screen.
- **3 minutes:** Add shoulders, neck, wrists, and standing or seated movement.
- **5 minutes:** Add hips, calves, and a short workspace reset.
- **10 minutes:** Add a light walking break if safe and available.

### Step 3 - Guide Gentle Movements

Use slow, low-intensity cues. Avoid forceful stretching, extreme ranges, bouncing, or pain-based goals.

Suggested menu:

- **Posture reset:** Feet grounded, sit bones balanced, ribs stacked over pelvis, shoulders relaxed, jaw unclenched.
- **Breathing:** Three slow breaths, exhale longer than inhale if comfortable.
- **Eyes:** Look at something far away for 20 seconds; blink slowly.
- **Neck:** Gentle chin nods and small side glances, no hard pulling.
- **Shoulders:** Shoulder rolls, scapular squeezes, arms relaxed.
- **Wrists and hands:** Open and close hands, gentle wrist circles, shake out tension.
- **Spine:** Seated cat-cow or gentle upper-back extension over the chair back.
- **Hips and legs:** Stand, shift weight, calf raises, mini walk, or seated marches.

### Step 4 - Add Desk Setup Cues

Offer one to three simple environment checks:

- Screen top near eye level or slightly below.
- Keyboard and mouse close enough that shoulders stay relaxed.
- Feet supported on floor or footrest.
- Chair height allows elbows to rest near the body.
- Frequently used items are within easy reach.

Avoid promising a perfect ergonomic setup. Frame cues as comfort checks.

### Step 5 - End With a Tiny Repeat Plan

Suggest a simple repeat rhythm:

- One micro-break every 25 to 60 minutes.
- One longer movement break once or twice during a work block.
- Pair the break with an existing cue: meeting ends, coffee refill, file save, or timer.

## Output Template

```markdown
## Posture Break Desk Card

**Safety note:** This is a gentle desk break, not medical advice. Stop if you feel pain, numbness, tingling, weakness, dizziness, chest pain, shortness of breath, or any concerning symptom.

### 3-Minute Reset
1. Posture reset - ...
2. Breathing - ...
3. Eyes - ...
4. Neck and shoulders - ...
5. Hands and wrists - ...
6. Stand or seated movement - ...

### Desk Comfort Cues
- ...

### Repeat Plan
- ...
```

## Safety Boundaries

- Not medical advice, diagnosis, physical therapy, rehabilitation, or treatment.
- Stop immediately on pain, numbness, tingling, weakness, dizziness, chest pain, shortness of breath, severe headache, sudden loss of coordination, or other concerning symptoms.
- For concerning, persistent, worsening, or unusual symptoms, advise qualified medical care or local emergency services as appropriate.
- Do not recommend aggressive stretching, forced range of motion, joint manipulation, weighted exercises, or pain-based progress.
- Do not create injury-specific rehabilitation plans.
- Do not claim that posture breaks prevent or cure medical conditions.

## Example Prompts

- "Give me a 3-minute posture break for my desk — my shoulders are tight."
- "I've been coding for hours and my eyes hurt. Help me reset."
- "Quick desk stretch, 1 minute, sitting only — I'm on a call soon."

## Quality Checklist

Before finalizing, verify that:

- The output starts with a safety note.
- Movements are gentle and optional.
- A default three-minute option is available.
- Eye rest and breathing are included.
- Desk comfort cues are practical and non-diagnostic.
- The response tells the user to stop on pain, numbness, or concerning symptoms.
