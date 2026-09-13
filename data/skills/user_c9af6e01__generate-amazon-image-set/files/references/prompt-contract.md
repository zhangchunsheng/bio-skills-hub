# Generation Brief Contract

## Purpose

Make each slot executable by an image model or another agent without hidden context.

## Required brief sections

Write every slot brief in this order:

1. **Slot objective** — state the customer question and narrative role.
2. **Canvas** — state delivery size, generation size, and target device.
3. **Product identity** — repeat exact variant, quantity, silhouette, color, finish, and structural landmarks.
4. **Product state** — state orientation, operating state, included accessories, and interaction.
5. **Composition** — define focal point, product occupancy, viewpoint, hierarchy, and safe areas.
6. **Environment** — define background, scene, props, people, and spatial context.
7. **Lighting and finish** — define the intended visible result rather than camera-brand jargon.
8. **Copy** — provide exact approved text or state `NO_TEXT`.
9. **Consistency anchors** — identify approved product and paired-story references when available.
10. **Exclusions** — list prohibited changes, unsupported claims, artifacts, and unwanted content.

## Brief rules

- Use complete sentences or a structured table; do not rely on another slot’s brief.
- Refer to evidence-backed features only.
- State exact copy rather than asking the image model to write persuasive text.
- If precise typography matters, prefer generating a clean image and adding text in a deterministic design step when available.
- Keep negative constraints specific to the slot; avoid a generic copied block that hides important exclusions.
- Describe people only when they clarify scale or usage, and prevent them from obscuring the product.
- Use reference images as identity evidence, not permission to copy a competitor’s protected creative expression.

## Pair brief rule

For paired A+ slots, repeat the shared semantic brief in both records, then add device-specific composition instructions.

Bad:

> Same as A2, cropped for mobile.

Good:

> Present the same confirmed adjustable-height benefit, product variant, warm neutral room, and two approved claims as A2. Recompose for the mobile canvas with the product centered and larger, headline above, two claims below, and no desktop crop.

## Output template

| Field | Value |
|---|---|
| Slot | |
| Objective | |
| Device | |
| A+ tier / module ID / module name | |
| Dimension source / minimum size | |
| Alternative text | |
| Delivery size | |
| Generation size | |
| Product identity | |
| Product state | |
| Composition | |
| Environment | |
| Lighting and finish | |
| Exact copy | |
| References | |
| Exclusions | |
| Missing evidence | |
| Status | READY / NEEDS_REVIEW / BLOCKED |
