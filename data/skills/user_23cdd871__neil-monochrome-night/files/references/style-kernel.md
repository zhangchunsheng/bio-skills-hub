# Style Kernel

Use this reference to make scene-specific decisions. Do not paste every line into the generation prompt.

## Contents

- Identity sentence and stable signature
- Color architecture, physical carriers, and scene-scaled anchor-emitter budget
- Air, weather-variation, composition, and visual-weight engines
- Reconstruction limits and color-bridge engine
- Failure directions and visual acceptance

## Identity sentence

**A concentrated artificial light burns inside broad industrial haze; urban light pollution colors the sky and distance. Residual wetness can stir the two colors together even when no rain is falling; visible rain is a variation rather than a template. A short neon phrase belongs to the place.**

The output is a photographic reconstruction of the source location, not a faithful retouch and not a new science-fiction location.

## Stable signature

Every complete result needs:

- a full-bleed 9:16 environment-led composition;
- two to four recognizable location-identity anchors;
- broad colored industrial haze, light-polluted sky, or unlit environmental material;
- a smaller family of concentrated practical emitters;
- deep but structured darkness;
- a declared relative visual-weight direction, with `source-matched` as the default;
- a scene-appropriate color bridge through haze/material overlap or broken wet reflection;
- one two-word uppercase English phrase as the default in-scene emitter, unless the user supplies exact wording or opts out;
- believable ordinary materials and scale.

These may vary: exact pair, dry haze versus post-rain versus active rain, camera height, scene scale, people, phrase position, sign form, reflection coverage, and anchor-emitter selection.

## Color architecture

Choose one relationship per image:

| Emitted family | Ambient counter-field | Good scene fit |
|---|---|---|
| sodium amber or warm yellow | deep teal-green | harbor, retail exterior, calm water, warm storefront |
| signal red | cold cyan-blue | street, intersection, residential exterior |
| warm white | petrol blue | mixed practical lighting, road, architectural exterior |
| magenta-pink | polluted cool green or blue-green | bar, wet glass, interior night |

The relationship matters more than the exact hue.

- The **ambient counter-field is broad**: it should occupy sky, haze, distant space, and named unlit materials. It must be visible at thumbnail size.
- The **emitted family is concentrated and brighter**: signs, lamps, storefronts, windows, traffic lights, or a few plausible added practicals.
- Preserve identifiable chroma in both families. Restrain the emitted family through small area, limited count, and surrounding darkness—not through words such as muted, pale, pastel, or desaturated.
- Keep a clearly readable counter-field core across roughly 25%–35% of the frame; lower-contrast color contamination may extend beyond that core. The counter-field stays darker and softer than the emitted family. Opposition comes from hue distance and source distribution, not equal brightness or a darker global exposure.
- At thumbnail scale, aim for the selected pair to own nearly all clearly chromatic visual weight. Use 85% as a directional composition gate, not literal pixel segmentation; neutral charcoal, gray, black, and small warm-white neutral exposure references do not need recoloring.
- Keep the ambient family visually broader than the emitted family. The **emitted-family footprint** should read across roughly 10% of the frame, with 8%–12% as the normal visual acceptance range. Count compact source cores plus only directly traceable local bloom, atmospheric spill, facade or foliage response, water, glass, or broken reflection. This is a visual estimate, not pixel segmentation and not a demand that literal sign, lamp, or window hardware occupy 10%. The same spatial rule applies to warm-white/petrol-blue pairs; judge luminous salience rather than demanding saturation from warm white.
- Give the emitted family a compact source cluster and at least one spatially separated, physically traceable response. When the scene offers two natural carriers or depth zones, use both. A source-aligned wet reflection, atmospheric spill, facade response, or sparse structural window cluster may count; an unrelated colored patch may not.
- Existing low-chroma path and street lamps are **neutral exposure references**, not members of a red, magenta, or amber emitted-family footprint. During a chromatic-pair adjustment, preserve their baseline position, count, hue, and source-core intensity unless the user explicitly targets them. Their halos and reflection pools may adapt only as required by the selected haze and surface state, while preserving the original relative light hierarchy. For a warm-white/petrol-blue pair, name the specific warm-white practicals that belong to the emitted family; keep all other neutral lamps locked. Do not recolor or brighten unrelated practicals to manufacture conflict.
- Build stronger primary-color conflict through the smallest plausible extension of source-linked spill, reflection, atmospheric scatter, or structural light until the emitted-family footprint reaches the roughly 10% visual target. Preserve environmental exposure and black point in the upper, middle, and lower fields separately; a brighter sky may not compensate for a darkened scene or ground. Stop before the response becomes a continuous wash. Do not substitute a global saturation increase.
- Keep charcoal, black, gray, and truthful material color between them. Do not make an equal-area two-color split or recolor every object.
- One or two small truthful off-hue lights may survive, but keep them below 5% of the frame so they never become a third field.
- The phrase uses the emitted family, not the counter-field hue.

### Give the ambient color a body

Do not leave the counter-field only in airborne haze. Name at least two physical carriers: unlit facade, foliage, dry or wet paving outside lamp pools, water, glass, distant building, metal, or dark interior surface. When both air and surfaces are available, route at least half of the clearly readable counter-field core through physical carriers, and keep some in the air/deep field. At least one carrier should route the ambient hue into the lower half.

Do not solve a missing low carrier by inventing a cool LED strip or outlining architecture. Instead, extend the ambient hue through an existing unlit surface, dry or wet material, glass, water, foliage, or distance haze; if none exists, rebuild a plausible matte or reflective surface within the source topology and selected weather mode.

### Scene-scaled anchor-emitter budget

Set scene scale before selecting the emphasized concentrated emitters that define the light architecture. This **anchor-emitter budget** is a hierarchy tool, not a total-light count and not a frame-area target.

| Scene scale | Anchor-emitter budget | Structural window field |
|---|---:|---|
| intimate interior or close exterior | 1–3 | omit unless windows are already defining selected emitters |
| street or residential landscape | 3–8 | sparse or half-lit, about 10%–25% of visible facade area |
| city or skyline | 3–8 | sparse to dense with dark gaps, about 15%–40% of visible facade area |

- Count only emphasized concentrated emitters selected into the light architecture. The active phrase counts as one.
- Structural windows and registered neutral exposure references remain outside the budget unless explicitly selected as emitters. Total visible source-point count may therefore exceed the budget range without failing it.
- Keep the brightest single emitting region below 15% of the frame.
- Structural windows are midtone building texture, not anchor emitters: crisp small rectangles, many dark gaps, no individual halo, no beam, and no broad cast light. Near windows may read slightly warmer; distant windows become smaller, softer, and closer to the counter-field hue.

## Air engine

Industrial particulate haze and urban light pollution are the stable world-building signature. The air is luminous, dirty, and depth-bearing rather than clinically clean and transparent, even when surfaces are dry. In windowless interiors, interpret this as humid or particulate interior air plus contaminated ceiling, glass, and distant dark planes; never invent an outdoor sky.

- Where sky is visible, allow no pure black: let the upper field be darkest and coolest, with stronger city glow and pollution scatter toward the horizon or practical-light cluster. In windowless interiors, apply the same gradient to ceiling, glass, and deep space instead.
- Lift the deepest black slightly while keeping broad darkness. Preserve low-contrast structure in buildings, trees, counters, boats, and roads.
- Reduce contrast and saturation detail with distance while retaining the chosen ambient hue.
- Keep haze as a permeating particulate film, not a discrete smoke plume, visible exhaust cloud, or opaque fog wall.
- Use tight bloom near foreground lights and slightly wider, softer halos deeper in the frame.
- Keep individual windows as irregular midtone rectangles. They give buildings mass; they are not all primary emitters.

### Weather variation

Choose one compatible mode after establishing industrial haze and light pollution:

| Mode | Falling rain | Surface and color bridge |
|---|---|---|
| dry polluted haze | none | dry asphalt, concrete, facade, foliage, glass, and airborne scatter overlap the two families; no puddles or mirror wetness |
| post-rain | none | broken residual water, damp paving, and shallow puddles carry reflections |
| active rain | visible | rain catches emitter light; wet surfaces and ripples break the reflections |
| waterfront/water | optional | existing water is the main reflective bridge; low polluted haze carries depth |
| interior condensation | outside rain optional | condensation, glass, a polished counter, or humid interior air carries the color; never rain from the ceiling |

Separate precipitation from surface state. For outdoor hardscape with a broad lower field and no stronger natural bridge, post-rain is the preferred non-raining mode: residual water carries color while the air contains no rain streaks. Active rain remains a variation, not the default. Choose dry haze only when the source or user calls for dryness, or when named low physical carriers can preserve forceful thumbnail-scale opposition without reflection.

In batches of three or more, active rain appears in at most half the results unless the user asks for a rain series; include at least one result with no falling rain, which may be post-rain. Do not use falling rain as a shortcut for atmosphere—the haze and light pollution must work without it.

## Composition engine

Rebuild the source into 9:16 using three depth layers:

1. **Near field:** dry or wet texture, water, counter, road markings, paving, boats, foliage, or another leading surface.
2. **Scene field:** the recognizable buildings, bar, storefront, road bend, or skyline anchors.
3. **Atmospheric field:** sky, ceiling, glass, fog, distant towers, or deep interior darkness.

Reserve a readable quiet atmospheric or dark field on every image, above, below, or within the scene. Make it large whenever the source geometry supports it, then scale its area to the declared visual-weight direction. There is no minimum frame-area quota. Empty space still carries hue, haze, rain, grain, or a gentle gradient; it is not a featureless black void.

Scene tendencies:

- **City/waterfront:** skyline sits low or mid-frame; sky and water create the scale.
- **Street/intersection:** road or curb lines pull through a dry, damp, or wet foreground into a haze-softened middle distance.
- **Retail exterior:** canopy/store anchors the lower middle; a large light-polluted sky and material-rich apron keep the frame open.
- **Residential landscape:** tree masses and towers frame a path; a distant sign may become the emitter.
- **Intimate interior:** foreground counter and ceiling/glass form large dark planes; reduce people to a few silhouettes.

## Visual-weight engine

Visual weight is the relative density of information and equal-strength attention demands. It is not exposure, contrast, darkness, or a mandatory empty-space percentage.

Choose one direction on the Reconstruction Card:

- **`source-matched` — default:** after the required 9:16 style rebuild, preserve the source's overall balance of quiet field, object density, focal hierarchy, light-source hierarchy, and material detail without preserving exact inventory.
- **`lighter`:** reduce that relative density while retaining the place and the foundational color impact.
- **`denser`:** add coherent, scene-supported information only when the user explicitly requests it; do not turn density into clutter.

Lighter results come from more breathing room relative to the source, fewer disposable objects, fewer equal-emphasis focal points, a more concentrated source hierarchy, selective material detail, and broken traceable light responses. Heavier results come from filling the frame with objects or detail, dispersing equal-strength lights, making spill and reflection continuous, rendering every material exhaustively, or creating several equal focal points.

When a result is too heavy for its declared direction, subtract in this order:

1. Remove disposable objects.
2. Enlarge an existing or source-plausible quiet field.
3. Reduce nonessential emphasized emitters.
4. Demote non-identity equal focal points.
5. Break continuous spill or reflection into sparse source-linked response.
6. Simplify distributed microdetail.

During that correction, preserve the identity anchors, complementary pair and low bridge, at least one separated emitted response, industrial haze and light pollution, registered neutral exposure references, upper/middle/lower exposure, and exact phrase. Never darken the scene or add extra rules to simulate lower visual weight.

When a result is too light for its declared direction, restore only source-supported scene mass, primary-versus-secondary focal structure, and selective material information. Do not fill every quiet field, scatter new lights, or darken the environment to manufacture weight.

## Reconstruction limits

Preserve location DNA, not incidental inventory.

- Retain the main camera direction, scene scale, and two to four identity anchors.
- It is acceptable to simplify crowd count, cars, carts, chairs, minor signs, windows, boats, plants, or other clutter.
- People, when kept, are small silhouettes or environmental scale cues. Do not create a central hero.
- Added text carriers and practical lights must fit existing architecture and ordinary construction.
- Do not add towers, tunnels, cables, holograms, flying vehicles, futuristic machinery, fantasy weather, or a different landmark.

## Color-bridge engine

The bridge between color families is structural, not decorative.

- In wet, water, or condensation modes, name the surface and both colors entering it. When a paved foreground is selected, make roughly 35%–50% of the lower frame visibly damp through irregular water film, shallow puddles, wet-asphalt diffusion, and dry interruptions. Align reflections with plausible emitters and viewing angle; break them with ripples, seams, droplets, roughness, objects, or dry patches. Prefer irregular traces over a perfect mirror.
- In dry polluted-haze mode, name two or more non-emissive carriers. Let the cool field occupy haze, dry asphalt/concrete, unlit facade, foliage, glass, or metal while warm/red light pools fade into it through airborne scatter. Do not invent puddles.
- In every mode, route the counter-field into the lower half so the image does not collapse to one hue.

## Failure directions

Reject these outcomes:

1. A subtle source-faithful grade with the original aspect ratio.
2. Clean transparent air, a pure-black visible sky, a featureless black interior depth, or no visible industrial haze/light pollution.
3. Cool color restricted to sky while the ground and architecture remain single-hued.
4. A full-frame red/cyan filter with no physical carriers or neutral structure, or an emitted family trapped in one isolated corner with no traceable response elsewhere.
5. Pure-black visible sky, featureless black interior depth, crushed shadows, or identical halo sizes at every depth.
6. Dense neon signage, invented technology, a hero character, or a different location.
7. Falling rain applied mechanically to every scene, a post-rain mode that still looks clean and dry, mirror-wet surfaces, forced puddles in dry mode, or reflections that do not correspond to a light source.
8. Missing, floating, illegible, or non-emissive phrase when text is active, or any new phrase when the user opted out.
9. A muted low-chroma pair whose two families cannot be distinguished at thumbnail size, even if their nominal hues are present.
10. Flat low-impact lighting caused by too few plausible sources, or an attempted fix that darkens any major upper, middle, or lower field, boosts existing lamp intensity, raises global saturation, clips lights, or crushes the atmospheric shadow field instead of extending restrained source-linked light and material response.
11. Structural windows that become highlight emitters, bloom individually, cast broad light, form a uniform full grid, or exceed the scene-scale facade range.
12. Confusing the anchor-emitter budget with the emitted-family footprint, forcing every visible source point into the budget, or recruiting structural windows and neutral exposure references merely to satisfy the selected pair.
13. Visual weight that contradicts the declared direction: disposable clutter, dispersed equal-strength lights, continuous spill, several equal focal points, or exhaustive microdetail on the heavy side; generic emptiness, stripped source-supported scene mass, or missing focal and material structure on the light side; or an attempted correction that simply darkens the scene or scatters more lights.
14. Painted concept-art texture, plastic 3D materials, synthetic HDR, or over-sharpened game-scene finish.

## Visual acceptance

At thumbnail size, read: vertical environment, broad light-polluted outdoor haze or humid interior depth, a chromatically distinct concentrated warm/red light with at least one separate physical echo, a strong lower-field color bridge, and—when active—one short phrase. The selected pair should own nearly all obvious chromatic visual weight while neutral structure remains intact; the emitted-family footprint should visually approach 10% of the frame through compact sources plus traceable response, remaining more than a single colored corner but less than a second broad environmental wash. Practical lamps outside the selected pair must retain their baseline identity and relative hierarchy rather than being recruited into the conflict. The balance of quiet field, object density, focal hierarchy, light-source hierarchy, and material detail must follow the declared visual-weight direction relative to the source, with no fixed empty-space quota. At full size, recognize the chosen location-identity anchors and trace important glows to plausible carriers. In wet, water, or condensation modes, also trace broken reflections and distinguish residual wetness from falling rain; in dry mode, verify the named non-reflective carriers instead. Confirm the selected weather and text modes and photographic material irregularity.
