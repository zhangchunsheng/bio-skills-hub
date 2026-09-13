# Product Input and Fact Lock

## Purpose

Prevent visual drift, fabricated claims, and inconsistent product states across an image set.

## Evidence labels

| Label | Meaning | Allowed for exact claims |
|---|---|---|
| `USER_CONFIRMED` | Explicitly supplied or approved by the user | Yes |
| `DOCUMENT_CONFIRMED` | Found in an authoritative product document | Yes |
| `IMAGE_OBSERVED` | Unambiguously visible in supplied product images | Yes, for visible attributes only |
| `INFERRED` | Plausible but not confirmed | No |
| `UNKNOWN` | Missing or contradictory | No |

An image observation cannot establish invisible material composition, performance, certification, dimensions, package contents, or internal structure.

## Minimum fact table

Record the value, source label, source location, and confidence for:

- Product name and category.
- Exact product variant, color, finish, and sales quantity.
- Shape, components, controls, connectors, and adjustable parts.
- Dimensions, weight, capacity, or compatibility.
- Materials and construction.
- Confirmed functions and operating states.
- Package contents and optional accessories.
- Installation or usage method.
- Certifications, warranty, and measurable performance claims.
- Target market, target user, and realistic environments.
- Brand name, logo, colors, typography, and prohibited expressions.

## Contradictions

When sources conflict:

1. Do not choose silently.
2. Record both values and their sources.
3. Mark affected slots `BLOCKED` or remove the disputed claim.
4. Ask for confirmation only when the decision materially changes the deliverable.

## Product identity anchor

Define a reusable identity anchor containing:

- Exact variant and quantity.
- Overall silhouette and proportions.
- Color and material appearance.
- Key structural landmarks.
- Allowed operating states.
- Included and excluded accessories.
- Primary reference image or approved MAIN result, when available.

Apply the anchor to every slot. A lifestyle or A+ image may change viewpoint, lighting, scale, and environment, but must not change product identity.

## Missing-evidence behavior

| Missing information | Required response |
|---|---|
| Exact measurement | Omit the number or mark the dimension slot `BLOCKED` |
| Included accessory | Do not render it as included |
| Functional state | Do not depict the state as working |
| Material composition | Describe only visible finish, not composition |
| Certification or performance | Remove the badge, number, or claim |
| Brand asset | Use neutral brand-safe composition; do not invent a logo |

