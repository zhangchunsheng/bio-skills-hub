# In-Scene Neon Phrase

The phrase is part of the default style, not an optional poster overlay. Omit it only when the user explicitly asks for no text.

## Copy rule

- If the user gives wording, render it verbatim in the supplied language, capitalization, and word count; explicit wording overrides every default copy restriction below.
- Otherwise author **exactly two short English words**, uppercase.
- In default mode, prefer a total of 7–18 letters excluding the space.
- Use one phrase once. Do not add a subtitle, logo, date, extra slogan, or decorative pseudo-writing. If the user opts out, add no phrase or replacement text.
- Make the words readable at ordinary viewing size and verify spelling at full size.

Choose language that feels like a found message about place, time, weather, waiting, closure, or interior state. The desired cadence is terse and slightly uncanny, not a literal business name or generic `NIGHT CITY` label. Examples of cadence only—not fixed defaults—include `HARBOR STATIC`, `NO DEPARTURE`, `STAY LATE`, `LAST AISLE`, `INNER WEATHER`, and `AFTER HOURS`.

In default mode, avoid copyrighted slogans, brand imitation, gibberish, CJK glyph generation, sentences, and more than two lines. In user-supplied mode, do not rewrite or reject the requested wording merely because it is CJK, a sentence, or longer than two words; instead fit it to one plausible carrier and keep all characters exact.

## Physical carrier

Bind the phrase to exactly one plausible object:

- facade-mounted outline sign;
- projecting street sign;
- canopy fascia;
- window-interior neon;
- freestanding light box already plausible for the site;
- bar-front light box;
- distant rooftop or upper-facade sign.

It must obey the scene perspective and construction. The carrier may be added or adapted from a non-identity part of the source, but it must not float as a graphic overlay.

## Letterform and light

- Use condensed or geometric uppercase sans-serif lettering.
- Prefer monolinear strokes, squared or slightly chamfered terminals, tight tracking, and clean counters.
- Outline-tube letters or a simple illuminated light box both work; avoid script, rounded bubble type, ornamental serif, or glitch typography.
- Use the selected emitted family: amber/warm-white, signal red, or magenta-pink.
- Keep the tube or letter edge legible with a tight bright core and local bloom. Do not bury the words in a huge soft halo.
- Let nearby haze, glass, wall, counter, water, or wet ground receive the sign's light where physically plausible.

The phrase is an important anchor but not a floating headline. Its apparent size may vary with scene scale: large on a waterfront facade, medium on a storefront, small but bright on a distant residential tower.

## Prompt clause

Use the clause for the active mode:

```text
Default two-word: render "[TWO WORDS]" once and only once, uppercase and correctly spelled, as [carrier] in [emitted hue]; condensed geometric monolinear lettering with squared terminals, a sharp bright core and tight local bloom; obey the carrier perspective and illuminate nearby haze/material; create a broken reflection only in wet, water, or condensation modes, and in dry-haze mode do not invent wetness; no other new readable text.
User-supplied exact text: render "[EXACT USER STRING]" once and only once, preserving every character, language, capitalization, spacing, and word count, as [carrier] in [emitted hue]; obey the carrier perspective and illuminate nearby haze/material; no paraphrase, translation, deletion, addition, or other new readable text.
Opt-out: add no new text, letters, pseudo-writing, sign copy, subtitle, logo, or replacement phrase.
```

## Validation and correction

At full size verify:

- in default mode, exactly two authored uppercase English words are present and correctly spelled;
- in user-supplied mode, the full requested string is present verbatim;
- in opt-out mode, no new readable or pseudo-readable text is present;
- when text is active, the phrase appears once, attaches to a physical carrier, follows perspective, uses the emitter family, and creates a plausible local air/material response;
- no extra generated pseudo-text competes with it.

If active text fails, use the one permitted regeneration to restate the exact wording, carrier, position, and `once and only once`. If opt-out fails, restate that no new text or substitute mark may appear. Keep the successful identity anchors, composition, color relationship, medium, and blend zone unchanged.
