---
name: neil-monochrome-night-v0-1
slug: neil-monochrome-night
displayName: Neil Monochrome Night
version: 0.1.0
summary: "把普通夜景或低光环境照片重构为具有工业雾霾、城市光污染、补色冲突和场景内霓虹短句的 9:16 摄影夜景。"
tags: [image-generation, photo-editing, night-photography, atmospheric-reconstruction]
license: MIT
homepage: https://github.com/Nealsun1993/neil-night-skill
description: "Transform a supplied environment-led night or low-light photograph into the Neil Monochrome Night look: a controlled 9:16 scene reconstruction with a broad cyan, teal, or green field shaped by industrial haze and urban light pollution; concentrated amber, warm-white, red, or magenta practical emitters; deep readable darkness; a scene-appropriate dry-haze, post-rain, active-rain, water, or condensation mode; and a default two-word uppercase English neon phrase embedded in the place. Preserve recognizable location DNA and photographic materials, but allow reframing, simplification, weather conversion, and limited scene rebuilding. Use when the user explicitly names this skill or clearly asks for this exact stylized night treatment. Do not use for ordinary source-faithful grading, generic cyberpunk art, simple exposure correction, text-free documentary edits, or close portraits and product shots whose subject must remain primary."
---

# Neil Monochrome Night

Create a stylized photographic night scene from a supplied environment photograph. The source is a **spatial and semantic scaffold**, not a fidelity lock. Preserve enough location DNA to recognize the place while rebuilding the frame around the style signature. Do not use this workflow for a close portrait or product shot whose person or object must remain primary.

Read [references/style-kernel.md](references/style-kernel.md) and [references/typography.md](references/typography.md) for every task.

## Decision priority

Resolve conflicts in this order:

1. Follow the user's explicit request.
2. Preserve two to four location-identity anchors from the source.
3. Establish the 9:16 environment-led composition.
4. Make the complementary light relationship, industrial haze, and light pollution unmistakable at thumbnail size.
5. Choose a scene-appropriate surface state and color bridge. Separate falling rain from residual wetness: prefer post-rain wet ground for paved outdoor scenes that need a stronger low-frame bridge, while keeping active rain optional.
6. Add the short in-scene neon phrase.
7. Keep ordinary materials and scale photographic.

Do not sacrifice the style merely to preserve incidental source detail. Do not sacrifice the identity anchors merely to make a generic night fantasy.

Numeric ranges in this skill are overlapping visual checks, not additive shares of one frame. Evaluate each range against its named object and denominator. If soft numeric ranges conflict, preserve the counter-field's 25%–35% readable core and the brightest-single-emitting-region limit below 15% first, then relax only the other soft ranges by the smallest amount needed. Never relax identity anchors, 9:16 geometry, the registered-neutral-reference lock, or exact requested text. Explicit user numbers override these defaults.

## Build a Reconstruction Card

View every local target before editing it. Record a compact internal card:

- **Scene class:** name the source's dominant spatial type in plain language; examples include intimate interior, street, retail exterior, residential landscape, and city/waterfront, but do not force an input into this list.
- **Identity anchors:** two to four shapes or relationships that make this place recognizable: skyline profile, road bend, storefront canopy, bar geometry, tower pair, harbor edge, distinctive tree line, or similar.
- **Disposable facts:** crowd count, minor vehicles, clutter, small signs, exact window occupancy, and peripheral objects that may be simplified.
- **Vertical plan:** what will occupy the upper atmospheric field, middle scene, and lower material or reflective field after rebuilding to 9:16.
- **Visual-weight direction:** choose `source-matched`, `lighter`, or `denser`; default to `source-matched`, and use `denser` only when the user explicitly requests it. This is a relative information-and-attention-density instruction after the required style rebuild, not exposure and not a frame-area quota. For `lighter` or `denser`, name the quiet field, disposable object group, light-source group, focal point, or material-detail zone that will change without weakening the identity anchors.
- **Color pair:** choose one emitted family and its broad ambient counter-field from the kernel. Plan the pair's visual weight and physical routes: the ambient family stays larger, while the **emitted-family footprint** reaches roughly 10% of the frame through compact source cores plus directly traceable material, atmospheric, or reflective response. Treat 8%–12% as a visual gate, not literal pixel segmentation or a demand for 10% hardware. For a refinement against an approved image, record the baseline upper-, middle-, and lower-field exposure separately so a brighter sky cannot hide a darkened scene or ground.
- **Light inventory:** set the scene scale, then record the **anchor-emitter budget**: the emphasized concentrated emitters selected into the light architecture. The active phrase counts as one. Structural windows and registered neutral exposure references stay outside this budget unless explicitly selected as emitters, so the total visible source-point count may exceed the budget range. During a chromatic-pair adjustment, lock the position, count, hue, and source-core intensity of existing neutral path or street lamps unless the user explicitly targets them; allow their halos and surface pools to adapt only as required by the selected haze and weather while preserving their relative hierarchy. In a warm-white/petrol-blue pair, count or alter only the specific warm-white practicals named as selected emitters; keep all other neutral lamps locked.
- **Atmosphere invariant:** industrial particulate haze or humid interior air, urban light pollution, reduced distant contrast, and a colored non-black outdoor sky or colored ceiling/glass/deep-interior field when no sky is visible.
- **Weather mode:** dry polluted haze, post-rain without falling rain, active rain, waterfront/water, or interior condensation. Treat precipitation and surface wetness as separate decisions. For an outdoor paved scene with a broad lower field and no stronger natural bridge, prefer post-rain without falling rain. Choose dry haze only when named low physical carriers can still sustain strong color opposition.
- **Color bridge:** in wet modes, name the broken reflective surface; in dry mode, name the haze, glass, matte facade, asphalt, concrete, foliage, or other material where both families overlap without invented wetness.
- **Phrase mode:** `default two-word`, `user-supplied exact text`, or `opt-out`. In default mode, author exactly two short uppercase English words.

If the input is daylight, the skill may convert it to night only when the user explicitly requests this style. Preserve the selected identity anchors during the conversion.

## Controlled reconstruction

Default to a near-9:16 portrait result; the six accepted references use 1600 x 2848. Treat 9:16 as composition geometry rather than a demand for that exact pixel count. Accept a generated width-to-height ratio within 1% of 9:16. If the tool returns a ratio outside that range, use a scene-aware crop or extension to reach 9:16, or regenerate when cropping would remove an identity anchor. Recompose rather than letterbox.

Allowed by default:

- crop, outpaint, or rebuild peripheral geometry for the vertical frame;
- enlarge sky, ceiling, glass, water, or foreground into a quiet atmospheric field;
- strengthen industrial haze and light pollution; introduce rain, condensation, puddles, or wetness only when the selected weather mode supports them;
- simplify clutter, reduce a crowd to a few silhouettes, remove non-anchor people or vehicles, and reorganize minor objects;
- add a plausible sign, light box, window sign, facade sign, or other physical carrier for the phrase;
- adjust nonessential windows and practical lights to support depth and the chosen pair; during a color-pair refinement, exclude the registered neutral path/street lamps unless the user explicitly targets them.

Still preserve:

- the source's scene class and ordinary scale;
- the selected identity anchors and their main spatial relationship;
- the camera direction and recognizable perspective logic, even when the framing is rebuilt;
- believable architecture, vegetation, road, water, glass, metal, and skin or clothing where visible.

Never replace the place with a different city, invent megastructures or futuristic vehicles, turn a person into the hero, or fill the frame with unrelated neon signage.

## Build the style

Apply relationships 1–4 and 6–7 on every task. Apply relationship 5 by default unless the user explicitly supplies different wording or opts out of text:

1. **Environment-led vertical frame:** a readable atmospheric or dark negative-space field on every task; make it large wherever the source topology permits, scale its area to the declared visual-weight direction, and keep clear depth with no poster border or letterboxing.
2. **Complementary opposition:** a broad cool environmental field against a smaller, brighter emitted family. This conflict—such as cold cyan-blue against signal red, or polluted cool green against magenta-pink—is foundational rather than optional. The two families must read at thumbnail size. At thumbnail scale, aim for the selected pair to own nearly all clearly chromatic visual weight while neutral structure remains intact; use 85% as a directional gate, not pixel segmentation. Keep a clearly identifiable counter-field core across roughly 25%–35% of the frame; lower-contrast contamination may extend farther. Keep the emitted-family footprint around 10% of the frame, normally 8%–12%, counting compact source cores plus only directly traceable bloom, atmospheric spill, facade or foliage response, and wet or glass reflection. The literal sign, lamp, or window hardware stays compact. Give the emitted family at least one spatially separated response beyond its main source, adding a second when the scene naturally supports it. Keep the counter-field darker, softer, and visually broader. Control the conflict through source distribution and physical response—not by recoloring practical lamps outside the selected pair, muting saturation, applying a global two-color wash, or darkening the environment.
3. **Industrial light-polluted air:** outdoors, the sky is colored rather than black, particulate haze catches urban glow, and the horizon carries light pollution. In a windowless interior, route the same dirty luminous depth through humid air, ceiling, glass, and distant dark planes without inventing a sky or horizon. In both cases distance loses contrast and bloom widens slightly with depth.
4. **Scene-appropriate color bridge:** in wet, water, or condensation modes, use broken reflections interrupted by ripples, seams, droplets, texture, or dry patches. When a paved foreground is the bridge, make the wet material visibly occupy the lower field rather than adding a faint clean sheen. In dry-haze mode, mix the two families through particulate air, glass, and named matte materials without adding puddles or mirror wetness.
5. **In-scene phrase:** in default mode, one readable two-word uppercase English neon phrase is physically attached to the place and participates in nearby air and material response. In user-supplied mode, use the exact wording instead. In opt-out mode, add no new text.
6. **Photographic world:** ordinary materials, restrained local bloom, imperfect exposure, soft atmospheric depth, and small irregularities remain believable.
7. **Scene-scaled anchor-emitter budget:** use 1–3 emphasized concentrated emitters at intimate scale and 3–8 at street or city scale. The active phrase counts as one. Structural windows and registered neutral exposure references remain outside the budget unless explicitly selected into the emitted family; total visible source-point count may therefore exceed the range. Structural windows stay small midtone rectangles with many dark gaps, no individual halo, and no broad cast light; they occupy about 10%–25% of a visible facade at street scale and up to 40% only at city scale. Keep the brightest single emitting region below 15% of the frame.

Avoid using the label `cyberpunk` in the generation prompt; describe the observable industrial haze, light pollution, color, material, and typography instead.

### Vary precipitation, not just wetness

- For a single outdoor image with a substantial paved lower field, default to post-rain without falling rain when residual water materially strengthens the color bridge. Use active rain only when visible precipitation improves the scene.
- For a batch of three or more, active rain may appear in at most half the results unless the user asks for a rain series. Include at least one result with no falling rain; that result may be post-rain rather than dry. Do not repeat the same precipitation medium mechanically across the batch.
- Treat dry polluted haze as a deliberate variant, not the automatic opposite of rain. Use it when the user or source calls for dryness, or when haze plus named low surfaces already creates forceful thumbnail-scale color opposition. `Dry` never means clean transparent air.

## Compile a compact reconstruction prompt

Use source-specific nouns and the following order. State the style relationships positively before the avoid list.

```text
Use case: controlled photographic night-scene reconstruction
Input: Image 1 is the sole spatial and semantic scaffold, not a pixel-fidelity lock
Primary request: rebuild Image 1 into the Neil Monochrome Night look in a full-bleed 9:16 portrait frame
Must retain: [scene class, camera direction, two to four identity anchors and their spatial relationship]
Vertical composition: [upper atmospheric field, middle scene, lower material/reflective field; named leading lines and negative space]
Visual-weight direction: [source-matched / lighter / denser; default source-matched; denser only by explicit request], judged after the required 9:16 style rebuild and disposable simplification through [quiet field, object density, source hierarchy, focal hierarchy, and material-detail density]; preserve overall source weight rather than exact inventory, and preserve upper-, middle-, and lower-field exposure rather than using darkness to simulate lower weight
Allowed reconstruction: simplify [disposable facts]; establish industrial haze and light pollution; apply [selected weather mode and its permitted surface state]; when text is active, add one plausible physical text carrier; rebuild only peripheral or non-identity geometry needed for 9:16
Light architecture: [emitted family] from [named sources] against broad [ambient counter-field], with a 25%-35% readable core across [air plus named physical carriers including one low carrier]; keep neutral structure, truthful saturated off-hue points below 5%, the brightest single emitting region below 15%, and the counter-field darker and softer than emitters
Color conflict: at thumbnail scale [selected pair] owns nearly all obvious chromatic weight; [emitted family] forms an 8%-12% emitted-family footprint through [compact source cluster] plus [one or two directly traceable responses], while the ambient family stays broader; registered neutral exposure references keep baseline position/count/hue/core intensity and do not count toward this target, though their halos and pools may adapt physically to [weather mode]; preserve upper-, middle-, and lower-field exposure and black point separately
Anchor-emitter budget: use [1-3 / 3-8] emphasized concentrated emitters for [scene scale]; count the active phrase as one; keep structural windows and registered neutral exposure references outside the budget unless explicitly selected as emitters, while allowing total visible source-point count to exceed the budget range
Atmosphere and weather: industrial particulate haze or humid interior air, urban light pollution, reduced distant contrast, depth-scaled local halos; outdoors use a colored non-black sky and horizon glow, while windowless interiors use colored ceiling/glass/deep-air fields with no invented sky; selected mode is [dry haze / post-rain / active rain / water / condensation], with falling-rain state and surface-wetness state specified separately
Color bridge: [wet/water mode: named lower surface is visibly wet and mixes both families in broken physically plausible reflections; dry mode: named haze, glass, or matte materials overlap both families with no invented wetness]
Exact text: [default: render "TWO WORDS" once, uppercase; user-supplied: render the exact supplied wording once; opt-out: add no new text]; when active, place it on [physical carrier] in [emitted hue], with sharp condensed lettering and tight local bloom; light nearby air/material and reflect only where plausible
Photographic finish: believable ordinary materials and scale, deep but readable shadows, natural lens response, slight grain, no illustration or 3D sheen
Avoid: source-faithful-only color grade, clean transparent air, black empty visible sky or featureless interior depth, falling rain on every image, forced puddles in dry mode, weak color opposition, floating overlay title, long or garbled text, dense neon clutter, hero character, sci-fi props, new landmark, perfect mirror reflection, global HDR glow
```

Do not ask the model to preserve every object, every person, exact signage, or the original aspect ratio. Those instructions suppress the intended reconstruction.

## Generate

- Use the available image-generation tool in edit mode with the target photograph as the only reference image.
- Process multiple targets one at a time and build a fresh Reconstruction Card for each.
- Vary the scene-specific phrase, color pair, weather mode, carrier, and composition while keeping industrial haze and light pollution stable. In a batch of three or more, enforce the weather-diversity guard above.
- Do not overwrite a source file.

## Validate and correct

Inspect at thumbnail and full size. Accept only when all gates pass:

- **Recognizable DNA:** the scene class and selected identity anchors still identify the source place.
- **Vertical rebuild:** the result is a deliberate near-9:16 composition within 1% of the 9:16 ratio, with atmospheric negative space—not the original frame padded or lightly cropped.
- **Visual-weight direction:** the result follows the declared relative direction after the required 9:16 style rebuild. `Source-matched` preserves the source's overall balance of quiet field, object density, focal hierarchy, light-source hierarchy, and material detail without preserving exact inventory; `lighter` visibly subtracts from that balance; `denser` adds only coherent, scene-supported information and appears only by explicit request. None is simulated by darkening exposure.
- **Color opposition — thumbnail separation:** a large cool ambient field and smaller bright emitted family are both unmistakable at thumbnail size.
- **Color opposition — pair dominance:** the selected pair owns nearly all clearly chromatic visual weight—use 85% as a directional thumbnail gate, not pixel segmentation—while neutral structure remains intact.
- **Color opposition — counter-field core:** the counter-field has a clearly readable 25%–35% core and remains darker and softer than the emitters.
- **Color opposition — physical routing:** when air and surfaces are both available, at least half of that readable core sits on named physical carriers, including one low carrier.
- **Color opposition — emitted-family footprint:** the emitted family reaches roughly 10%, normally 8%–12%, through compact hardware plus directly traceable response; it neither collapses into one tiny corner nor spreads into a second environmental wash.
- **Color opposition — neutral practicals:** practical lamps outside the selected pair retain baseline position, count, hue, and source-core intensity and do not count toward the emitted-family footprint; their halos and pools adapt only to selected haze/weather without changing the hierarchy. In a warm-white/petrol-blue pair, only specifically named warm-white emitters count; all other neutral lamps remain locked.
- **Color opposition — chroma control:** neither family collapses to gray, low-chroma neutrality, or a single wash. The emitter stays saturated and is restrained by source count and response area rather than desaturation, global saturation, or environmental darkening.
- **Color opposition — exposure continuity:** for an edit against an approved baseline, compare upper, middle, and lower fields separately; a brighter sky does not excuse a darkened scene or ground.
- **Anchor-emitter budget:** the selected emphasized-emitter count matches the scene-scale range and the brightest single emitting region remains below 15%. The active phrase counts as one. Structural windows remain irregular midtone texture with many dark gaps, stay within the scene-scale facade range, and do not bloom or cast broad light. Registered neutral exposure references and unselected structural windows remain outside the budget even when total visible source-point count exceeds its range.
- **Polluted atmosphere:** outdoors, industrial haze and light pollution create a colored non-black sky, horizon glow, airborne scatter, and distance falloff. Windowless interiors instead use humid/particulate air, colored ceiling or glass, and softened deep planes without inventing a sky. Falling rain is not required.
- **Weather logic:** the result follows the selected mode. Dry haze has no forced puddles or falling rain; post-rain has tactile residual water without falling rain; active rain visibly affects air and surfaces.
- **Color bridge:** wet modes use a named, visibly substantial broken reflection that routes both families through the lower field; dry mode visibly overlaps the two families through haze, glass, or named low matte materials.
- **Text object:** in default mode, exactly one readable two-word uppercase English phrase is embedded in perspective and emits light; in user-supplied mode, the exact requested wording appears once; in opt-out mode, no new text appears.
- **Photographic world:** ordinary scene scale and material behavior survive; no generic futuristic set dressing.

Reject a result that merely looks like a restrained night grade, preserves a non-portrait source ratio, has clean transparent air, uses faint clean-looking sheen for a post-rain mode, applies falling rain to every batch item, mutes the complementary pair until it lacks impact, strands the emitted family in one isolated corner, turns its spill into an untraceable second environmental wash, omits the phrase when text is active, lacks a low material route for the ambient color, or replaces the place with unrelated spectacle.

If correction is needed, regenerate at most once. Fix the largest style collapse first—usually composition, counter-field, polluted atmosphere, weather logic/color bridge, or typography—while restating the identity anchors. If the result is too heavy for the declared visual-weight direction, subtract in this order: disposable objects; enlarge an existing or source-plausible quiet field; nonessential emphasized emitters; non-identity equal focal points; continuous spill or reflection, broken back into sparse source-linked response; distributed microdetail. If it is too light, restore only source-supported scene mass, primary-versus-secondary focal structure, and selective material detail; do not fill the frame, scatter new lights, or darken the environment. In either direction preserve the identity anchors, complementary pair and low bridge, at least one separated emitted response, industrial haze/light pollution, registered neutral exposure references, upper/middle/lower exposure, and exact phrase. Do not add more rules to simulate visual weight. Do not revert to source-fidelity instructions as the correction strategy.

If the corrected result still fails any gate, stop. Do not label or publish it as an accepted final. Report the failed gates, keep the best attempt clearly marked as diagnostic only when useful, and return the Reconstruction Card plus compiled prompt so the user can decide whether to continue.

## Return

Return the final image and a short Chinese note naming the preserved identity anchors, the chosen complementary pair, the haze/light-pollution treatment, and the weather mode and color bridge. When text is active, name the phrase; when the user opted out, state that no new text was added. Include the full compiled prompt only when the user asks.

If image editing is unavailable, return the Reconstruction Card and compiled prompt instead.
