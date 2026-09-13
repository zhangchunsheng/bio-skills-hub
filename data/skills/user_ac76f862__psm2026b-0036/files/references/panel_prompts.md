# ImageGen Panel Prompt Templates — Old Master Q (老夫子) Style

Use these as starting points. **Every prompt MUST begin with a different opening
phrase** so parallel calls don't overwrite each other (ImageGen timestamps files
by the second; identical opening + same second = collision = missing panels).

## Shared style anchor

Append this block to every prompt (adjust the character description per story):

> black-and-white ink line art, hand-drawn pen cartoon in the style of Old Master
> Q (Lao Fu Zi), bold simple outlines, flat minimal background, humorous, no color.
> A blank white speech bubble is drawn near [CHARACTER]. No text, no words, no
> letters anywhere in the image.

## Recurring character (keep consistent across a story)

> A short plump balding middle-aged Chinese man with a few hairs on top, small
> mustache, light-grey changshan gown (or casual shirt), round wire-frame glasses.

> A slender young Chinese woman pharmacist with glasses wearing a white lab coat.
> (use for 转/合 reveal beats)

## Distinct opening phrases (rotate these so files never collide)

1. `Old Master Q gag comic, ...`
2. `Monochrome pen cartoon like Lao Fu Zi, ...`
3. `Hong Kong humor comic strip, ...`
4. `Black-and-white hand-drawn comic in the Old Master Q manner, ...`
5. `Lao Fu Zi monochrome comic, ...`
6. `Humorous ink drawing in the Old Master Q style, ...`
7. `Classic Hong Kong gag panel, ...`
8. `Pen-and-ink Lao Fu Zi style scene, ...`

## Per-beat prompt skeletons

**起 (错误认知):** `[Opening 1] the balding mustached man at home holding a
digital blood pressure monitor showing a normal reading, happily tossing a small
pill bottle into the air, triumphant grin.`

**承 (埋雷/延续):** `[Opening 2] the same man outdoors, spiral eyes, holding his
head, stumbling and leaning against a wall, wobbly legs, comic motion lines.`

**转 (冲突/真相):** `[Opening 3] hospital emergency room: the same man pale on an
examination bed with a blood pressure cuff, weak. A doctor in a white coat with a
stethoscope holds a chart showing a very high number, pointing dramatically.`

**合 (改正):** `[Opening 4] the same man meekly taking a small pill with a glass
of water, obedient. The young woman pharmacist beside him smiles and gives a
thumbs-up.`

## Food/drug-interaction variant (西柚刺客 style)

- 起: `... the man holding a small medicine bottle, chest out, confident smile.`
- 承: `... the man happily biting into a large grapefruit wedge, juice dripping,
  eyes closed in delight.`
- 转: `... the man bent over clutching his leg and arm in pain, sweat drops,
  miserable. The pharmacist stands nearby shocked, pointing at a whole grapefruit.`
- 合: `... the man throwing a grapefruit into a trash bin and holding up a red
  apple, enlightened. The pharmacist gives a thumbs-up.`

## Parameters

- `size`: `1024x1024`
- `quality`: `medium`
- `style`: `black and white ink comic` (or `realistic illustration` if the user
  later wants the screenshot's realistic look — see workflow_pitfalls.md)
- `output_dir`: a dedicated `comic_panels/` folder in the working directory.
