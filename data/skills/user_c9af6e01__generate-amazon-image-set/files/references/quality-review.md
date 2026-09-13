# Quality Review Protocol

## Status vocabulary

| Status | Meaning |
|---|---|
| `PASS` | Verified with available evidence or inspection capability |
| `FAIL` | A specific rule is violated |
| `BLOCKED` | The check cannot be completed with available evidence or capability |

Never convert `BLOCKED` into `PASS` to finish the task.

## Stage 1: plan review

Check every item and name affected slots.

| Gate | Requirement |
|---|---|
| Scope | Requested deliverables and A+ eligibility are explicit |
| Module count | Distinct A+ module IDs do not exceed 5 for Basic / Standard or 7 for Premium; paired assets count once |
| Module specification | Named module and dimension source recorded; Full Image desktop minimum 1464x600 and mobile minimum 600x450 checked independently |
| Alternative text | Every required device field has factual alternative text; Premium Full Image requires both desktop and mobile |
| Facts | Every exact claim maps to an allowed evidence label |
| Roles | Every slot has one primary decision role |
| Coverage | Important purchase questions are covered without padding |
| Dimensions | Every slot has a single delivery size tied to a valid template |
| MAIN | No added text, confusing props, or unsupported accessories |
| References | Required product views and states are available |
| Copy | Exact wording is supplied and claims are defensible |
| Pairing | Every device-specific A+ slot has the required counterpart |
| Pair semantics | Paired slots lock the same story, facts, and product state |
| Self-containment | Every brief is independently executable |
| Repetition | Later slots add evidence rather than restating earlier slots |

Any failure involving product truth, MAIN compliance, unsupported claims, or unresolved delivery dimensions is a hard failure.

## Stage 2: final-image review

Perform only checks supported by the agent’s capabilities.

### Technical

- File is present, readable, and associated with the correct slot.
- Actual pixel dimensions match delivery requirements.
- Image is sharp enough at intended display size.
- No unintended borders, watermarks, corrupted regions, or generation artifacts appear.

### Product fidelity

- Variant, quantity, color, finish, silhouette, controls, and accessories match the fact lock.
- Product is not deformed, duplicated, merged, or partially replaced.
- Operating state is physically plausible and supported.
- The approved MAIN or product reference remains the identity anchor.

### Slot compliance

- Image answers its assigned customer question.
- MAIN uses the required clean background and contains no prohibited additions.
- Measurements and package contents are confirmed.
- People, props, and scenes do not obscure or misrepresent the product.

### Text and claims

- Copy matches the approved wording and language.
- Spelling, numbers, units, punctuation, and capitalization are correct.
- Text remains readable at intended device size and inside safe areas.
- No fabricated badge, certification, rating, testimonial format, or competitor claim appears.

### Set coherence

- Visual identity, product appearance, and brand system remain coherent.
- Each image adds a distinct role.
- Later images do not show quality decay or generic repetition.
- Desktop/mobile pairs retain the same narrative, product state, and claims while using independent layouts.

## Hard-fail conditions

Mark the set `NEEDS_REVISION` regardless of score when any required image has:

- Wrong product, variant, quantity, or included item.
- Unsupported measurable claim or certification.
- MAIN compliance violation.
- Wrong delivery dimensions.
- A+ module count exceeds the tier limit, or an export falls below either required pixel dimension.
- Missing required mobile asset or alternative-text field.
- Unreadable or incorrect required copy.
- Missing required slot.
- Desktop/mobile semantic mismatch.
- Material deformation that changes the product.

## Quality score

Use this score only after hard gates pass:

| Dimension | Weight |
|---|---:|
| Product fidelity and factual accuracy | 30 |
| Platform and slot compliance | 20 |
| Composition and visual hierarchy | 15 |
| Text, claims, and readability | 15 |
| Set coherence and device pairing | 10 |
| Technical quality | 10 |

Qualification threshold: at least `85/100`, no hard failure, and no required check marked `BLOCKED`.

## Review output

Return:

1. Per-slot status with evidence.
2. Hard failures.
3. Blocked checks.
4. Weighted score.
5. Required revisions in priority order.
6. Overall status: `QUALIFIED`, `NEEDS_REVISION`, or `BLOCKED`.
