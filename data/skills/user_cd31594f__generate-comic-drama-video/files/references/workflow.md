# Workflow Contract

## State machine

Run environment preflight and user intake before entering the stored state machine. Then advance only through these current states:

1. `story_review`: create and validate `story.json`; present the complete script with every scene's visual content and verbatim narration; stop for approval.
2. `visual_review`: generate the anchor when needed, character sheets, and scene images; stop once for combined visual approval.
3. `audio_generation`: audition and approve a voice when needed, then generate scene-level narration, align short captions, and optionally generate BGM.
4. `composition`: build, check, preview, render a picture track, and finalize the MP4 with verified audio.
5. `complete`: report the JSON, approved assets, manifests, Studio URL, and probed final MP4.

`style_and_character_review` and `scene_image_review` remain valid only for older projects. New projects use `visual_review`. Never infer approval. The user explicitly approves the story and the combined visual package. For compatibility, one visual approval updates both `approvals.style_and_characters` and `approvals.scene_images`. Voice choice is also explicit when the user requests auditions.

At story approval, never show only an outline, summary, or scene list. Show the full story content and every scene in order with its scene ID/title, complete visual beat or `image_prompt`, and all corresponding narration entries verbatim as spoken paragraphs. Do not truncate, paraphrase, or collapse narration. Split a long review into numbered parts when necessary, but wait until all parts have been presented before asking for approval. After revisions, re-present the complete revised script, or all fully revised scenes plus an explicit list of unchanged scenes for a narrowly scoped user-requested edit.

## Story-driven scene splitting

Do not target a scene count. Split when the location, time, dominant action, point of view, or narrative beat needs a new image. Keep multiple narration sentences in one scene when the same image can support them. Stop if the plan exceeds 600 scenes.

Estimate duration before TTS from language-aware reading speed and punctuation. Keep the draft under 840 seconds when practical. After TTS, use probed audio durations as the source of truth. If the final timeline exceeds 900 seconds, do not render; condense narration or merge visually redundant scenes, then return to story approval.

Set `project.caption_max_characters` for each project. Treat every narration entry as one displayed caption, but combine all entries under one scene into one MiMo TTS request. Split copy at natural spoken boundaries without changing meaning. The audio helper detects sentence pauses and derives caption WAV slices only for timing; the scene-level master remains authoritative. When narration changes after images are approved, re-check semantic image alignment before retaining `approvals.scene_images=approved`.

## Prompt resolution

Resolve every scene prompt from four layers:

1. Global style, palette, and composition guidance.
2. The fixed style reference or approved generated anchor.
3. Approved character sheets for characters in the scene.
4. The scene's differential `image_prompt`.

Do not chain scene N as the reference for scene N+1. Always return to the same approved master references to prevent accumulated drift. Use the Image API edits endpoint when reference images are present. For `gpt-image-2`, do not send `input_fidelity`; image inputs already use high fidelity.

## Runtime directory

Use this project layout:

```text
comic-drama-project/
├── story.json
├── build/
│   ├── image-manifest.json
│   ├── audio-scene-jobs.json
│   ├── audio-alignment.json
│   └── audio-manifest.json
├── assets/
│   ├── references/
│   ├── characters/
│   ├── scenes/
│   └── audio/
│       ├── voice-previews/
│       ├── narration-scenes/
│       ├── narration-captions/
│       ├── narration-scene-source.wav
│       └── narration-timeline.wav
├── index.html
├── package.json
├── hyperframes.json
└── meta.json
```

The manifests are resumable execution state. Keep the approved narrative plan in `story.json`; do not insert API keys or large base64 image data into it.

## HyperFrames contract

- Render at 1920x1080, 30 fps, MP4.
- Show only one full-bleed image and whole-sentence captions as visible content.
- Use `object-fit: cover` and the per-scene focal point to protect faces during crop.
- Use a slow 1.0-1.2 scale move and a 0.5-second crossfade.
- Preserve the globally accelerated scene-level narration master. Treat BGM as optional.
- Keep background music under the narrator; default volume is 0.14.
- Use no sound effects, cards, titles, logos, panels, or visible decorative DOM.
- Run `hyperframes lint`, `validate`, and `inspect` before render.
- Render to a video-only path and run `finalize_video.py`; never assume the renderer embedded composition audio.
