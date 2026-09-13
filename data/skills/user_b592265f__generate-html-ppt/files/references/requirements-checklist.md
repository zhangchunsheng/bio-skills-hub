# Requirements Checklist (7-Question Style Alignment)

This is the canonical 7-question requirements list that drives Phase 1: Outline & Style
Alignment in `SKILL.md`. The questions live here as a standalone reference so any agent or
reviewer can link to a stable anchor (`references/requirements-checklist.md`) instead of
quoting an inline block in `SKILL.md`.

Use this checklist before any template is selected. Aim to resolve the first 3 questions
in one round of conversation; the remaining 4 can be filled in opportunistically.

---

## The 7 Questions

### 1. Style Preference & First-Time Guidance (风格偏好与初用指南)
Match the user's request against the available design recipes. The default is **Beautiful
Modern**; common alternatives are **Swiss Minimalist**, **Cyberpunk Dark**, **8-Bit Orbit**,
**Emerald Editorial**, etc.

For first-time or undecided users, proactively offer to generate a quick **Visual Style
Preview (风格视觉预览)** before building the full presentation — saves tokens if the
aesthetic is wrong.

### 2. Audience & Scenario
What is this deck for? Pick one:
- **Pitch deck** (investors / clients)
- **Conference talk** (public speaking, technical)
- **Internal report** (team / leadership review)
- **Teaching / Tutorial** (educational, walkthrough)

### 3. Presentation Length
How many slides?
- **Short**: 5–10
- **Medium**: 10–20
- **Long**: 20+

### 4. Raw Materials
What source material does the user have? (documents, notes, topic outline, prior deck,
nothing yet, etc.)

### 5. Visual Assets
What assets can be embedded? (logos, screenshots, diagrams, brand photos, custom
illustrations, none yet.)

### 6. Theme & Density Mode
Pick the right density:
- **Low density / Speaker-led** — large headings, minimal text, generous negative space,
  1–3 bullets max per slide. The deck is a backdrop for the talk.
- **High density / Reading-first** — detailed grids, comparisons, tables, 4–8 bullets per
  slide. The deck must stand alone without narration.

### 7. Hard Constraints
Any non-negotiables: brand colors, required typography, regulatory disclaimers, fixed
deadline, must-include content, etc.

---

## How to Apply

- **First pass**: ask questions 1–3 explicitly; record answers before doing anything.
- **Second pass**: confirm questions 4–7 with a single combined prompt (e.g. "Any source
  docs, logos, or brand constraints I should know about? If not, I'll proceed with the
  default.").
- **Re-anchor anytime**: if the user's later asks contradict the original answers, re-open
  the relevant question instead of silently overriding.
