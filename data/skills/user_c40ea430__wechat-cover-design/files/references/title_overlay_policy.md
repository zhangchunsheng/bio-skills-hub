# Title Policy

All themes reserve the same natural left title field: `x=76..620`, `y=88..585` on a `1584x672` canvas. It is part of the background composition, not a floating UI panel.

## Native-image mode

Generate the background without text. Keep the left title field low-detail and free of focal objects. After generation, render exact typography with the host layout tool or `scripts/compose_cover.py`:

- Chinese: a host-available serif or editorial display face with complete CJK coverage.
- Latin/English: a compatible host-available display face.
- No underline, divider, card, shadow, or translucent panel.

If the host can generate images but cannot perform layout or image editing, return a text-free background and the overlay specification. Do not generate the final Chinese title inside the image model; this mode is a handoff, not a finished cover.

## Handoff mode

The final English prompt must request a text-free background. Include all of the following in the prompt:

- `left 39% of the canvas reserved for a left-aligned title block`;
- `no text, labels, watermark, or logo anywhere in the generated image`;
- no objects, high-contrast edges, or data marks in the title field;
- `no other text, labels, watermark, logo, or object in the title field`.

Return the exact title, subtitle, font style, colors, and coordinates as an overlay specification. The destination system must run `scripts/validate_cover.py` before `scripts/compose_cover.py`; a failed audit requires background regeneration. The compositor requires explicit `--font` and `--latin-font` paths because SkillHub packages cannot contain font binaries.
