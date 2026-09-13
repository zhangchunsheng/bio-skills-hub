---
name: generate-comic-drama-video
description: "Create landscape comic-drama videos through environment preflight, guided user intake, story approval, one combined visual review, scene-level narration, short synchronized captions, and verified HyperFrames MP4 finalization. Use for 漫剧、动态漫画、漫画故事视频、AI 漫画视频, voice comparison, narrated illustrated stories, or fixing unnatural short-line TTS cadence. Supports gpt-image-2, Xiaomi MiMo preset/designed voices, optional BGM, up to 600 scenes, and a hard 15-minute duration."
---

# Generate Comic Drama Video

Check the environment and guide the user first. Then create the story, obtain explicit story and combined visual approvals, generate audio, and render. Keep narrative decisions flexible; keep state transitions and media processing deterministic.

## Required references

Read [references/workflow.md](references/workflow.md) at the start of every new project. Read [references/runtime.md](references/runtime.md) before the first live image, TTS, BGM, or render command. Read [references/production-lessons.md](references/production-lessons.md) when resuming partial provider jobs, revising narration after image approval, diagnosing abnormal TTS duration, or finalizing a render. Use [references/story.schema.json](references/story.schema.json) as the canonical data contract.

## Stage 0: Preflight and user guidance

Run the environment check before scaffolding or provider calls. Select only the providers the run needs; omit `--bgm` unless the user explicitly requested local music:

```bash
export COMIC_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/generate-comic-drama-video"
python3 "$COMIC_SKILL/scripts/preflight.py" \
  --image-provider external --tts-provider xiaomi_mimo --json
```

Resolve every missing required item before generation. Report environment variable names, never secret values. Optional Kokoro, MusicGen, Whisper, and Docker failures do not block a Xiaomi-MiMo narration-only run.

Guide a new user with this concise intake, omitting questions already answered:

1. Required: story theme or one-sentence premise.
2. Optional: style/reference image; otherwise generate a visual anchor.
3. Optional: narrator gender, tone, perspective, speed, and language.
4. Optional: caption length; default to 24 characters.
5. Optional: BGM choice; default to no music.
6. Optional: audience, ending, and prohibited content.

State the defaults and proceed when optional inputs are absent. Do not ask for target duration or scene count. Never ask the user to paste an API key into chat; direct them to configure the named environment variable.

Use these defaults when the user does not override them:

- Visuals: generate an anchor from the story theme.
- Narration: one neutral narrator in the story language, third-person perspective, speed 1.0. Use MiMo `mimo_default` when Xiaomi is configured; otherwise use the documented local fallback.
- Captions: 24 characters per displayed narration unit.
- Audio: no BGM and no sound effects.
- Ending: resolve the narrative naturally without adding a moral or call to action.

## Initialize

Collect only inputs that affect the result:

- Story theme or premise.
- Optional user style/reference image.
- Narrator provider, model, voice, tone, speed, and language for this run.
- Caption length preference; default `project.caption_max_characters` to 24 when unspecified.
- Whether the user explicitly wants BGM. Default it to disabled.
- Any explicit content, audience, or ending constraints.

Do not ask for a target duration or scene count. Let the story determine both, while enforcing at most 600 scenes and 900 seconds.

Create a dedicated project directory, scaffold it with HyperFrames, then run its doctor:

```bash
export COMIC_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/generate-comic-drama-video"
npx hyperframes init comic-drama-project --non-interactive
cd comic-drama-project
npx hyperframes doctor
cd ..
```

Use `assets/example-story.json` as a structural example, not as story content.

## Stage 1: Write the story JSON

Write `story.json` before generating any media.

1. Build a complete narrative arc with setup, escalation, climax, and resolution.
2. Split on a real visual beat: location, time, dominant action, point of view, or emotional reveal.
3. Keep consecutive narration units in the same scene when one image can support them.
4. Give each scene exactly one differential `image_prompt` and one or more complete narration entries. Each entry is one displayed caption; split at natural spoken boundaries so it stays within `project.caption_max_characters`.
5. Define every recurring character once under `characters`; keep appearance and wardrobe concrete.
6. Set `visual_style.mode` to `user_reference` when an image is supplied, otherwise `generated_anchor`.
7. Set `audio.sfx_enabled` to `false`. Set `audio.scene_gap_seconds` to `0.35` for scene-level MiMo narration. Set `audio.bgm.enabled` to `false` unless the user explicitly asks for music. Only define and generate local MusicGen prompts when enabled.
8. Keep `approvals.story` as `pending` and `stage` as `story_review`.

Validate immediately:

```bash
python3 "$COMIC_SKILL/scripts/validate_story.py" comic-drama-project/story.json
```

Fix every error. Then present the complete script for user review, not only an outline, summary, or scene list. The review must include the full story content and, for every scene in order, the scene ID/title, complete visual beat or `image_prompt`, and every narration entry verbatim as the corresponding spoken paragraph. Do not truncate, collapse, paraphrase, or replace narration with counts or excerpts. If the script is too long for one message, split it into clearly numbered review parts and present every part before requesting approval. After revisions, re-present the complete revised script, or the complete revised scenes together with an explicit list of unchanged scenes when the user requested a narrowly scoped change. Stop until the user explicitly approves the displayed script. Record `approvals.story: approved`, set `stage: visual_review`, and never infer approval from silence.

## Stage 2: Generate and review all visuals

Use the fixed reference strategy. Never chain one scene image into the next scene. Generate the visual anchor when needed, all character sheets, and all scene images before requesting one combined visual approval.

Configure the external OpenAI-compatible endpoint without exposing credentials:

```bash
export COMIC_IMAGE_BASE_URL="https://provider.example/v1"
export COMIC_IMAGE_API_KEY="..."
export COMIC_IMAGE_MODEL="gpt-image-2"
```

Generate the full visual package in order. The wrapper skips anchor generation when the user supplied a reference image:

```bash
python3 "$COMIC_SKILL/scripts/generate_visuals.py" comic-drama-project/story.json \
  --project-dir comic-drama-project --concurrency 3 --attempts 3
```

Never ask the user to paste a key into chat. Never store a key in `story.json`, manifests, command output, or source files.

The dispatcher must:

- Call the installed imagegen CLI rather than a custom OpenAI SDK runner.
- Use `gpt-image-2` only.
- Use the edits endpoint for every scene because references are present.
- Put the style reference first and relevant character sheets after it.
- Omit `input_fidelity`; `gpt-image-2` already uses high fidelity for image inputs.
- Use one request per distinct scene and retry each failed scene at most three times.
- Preserve `build/image-manifest.json` and skip completed outputs on resume.
- Keep text, subtitles, speech bubbles, watermarks, panels, borders, and collages out of generated images.

Do not send 600 scenes as one API job. Keep concurrency conservative and lower it when the provider rate-limits.

Show the style reference/anchor, every character sheet, and all scene images or review sheets together. Stop once for explicit visual approval. On approval, set both legacy-compatible fields `approvals.style_and_characters: approved` and `approvals.scene_images: approved`, then set `stage: audio_generation`. These are one user-facing approval gate, not two separate stops.

If narration changes after scene-image approval, compare every revised scene against its approved image. Perspective, wording, and caption splitting may change without regeneration; location, job, action, visible object, character, age, or time changes require a new image review and may require regeneration.

## Stage 3: Generate narration and optional music

Set MiMo credentials only when `narrator.provider` is `xiaomi_mimo`. The story records the provider, model, and voice; the key remains environment-only:

```bash
export COMIC_TTS_BASE_URL="https://api.xiaomimimo.com/v1"
export COMIC_TTS_API_KEY="..."
```

Never pass or print the key in a command argument, manifest, or source file. MiMo uses `POST /v1/chat/completions`: place stable voice and delivery direction in the `user` message and the exact scene narration in the `assistant` message. Use a documented preset voice with `mimo-v2.5-tts`, or a stored `voice_design` description with `mimo-v2.5-tts-voicedesign`.

When the user wants to choose a voice, generate comparable samples before full narration. Use the same text and speed for every candidate:

```bash
python3 "$COMIC_SKILL/scripts/generate_voice_previews.py" \
  --project-dir comic-drama-project --speed 1.5 --concurrency 7
```

Stop for explicit voice approval. Record the selected preset or the exact designed-voice description in `story.json`.

For Xiaomi MiMo, generate one continuous WAV per approved visual scene. Do not send each short caption as a separate TTS request. The scene-level helper keeps sentence openings direct, disables pause compaction, joins scenes with `audio.scene_gap_seconds`, applies the numeric speed once to the complete master track, then aligns the short captions to detected sentence pauses:

```bash
python3 "$COMIC_SKILL/scripts/generate_scene_audio.py" comic-drama-project/story.json \
  --project-dir comic-drama-project --concurrency 10
```

Use `generate_audio.py` only for the local Kokoro fallback or when the user explicitly requests legacy caption-level TTS. MiMo concurrency accepts 1-10; use 10 only when the provider account supports it. Treat `assets/audio/narration-timeline.wav` and its probed duration as authoritative. Review `build/audio-alignment.json`; proportional fallback means no usable pause was detected for at least one scene and should be audited before render. Designed-voice production requests must keep `optimize_text_preview` false. If the timeline exceeds 900 seconds, do not render.

When `audio.bgm.enabled` is `true`, generate local instrumental background music after narration establishes the final duration:

```bash
python3 "$COMIC_SKILL/scripts/generate_bgm.py" comic-drama-project/story.json \
  --project-dir comic-drama-project
```

Generate no sound effects. Keep the BGM volume below the narrator; the schema caps it at 0.35 and defaults to 0.14.
When the user disables BGM, skip MusicGen entirely. The composition builder must produce a narration-only timeline without requiring a BGM manifest entry or file.

## Stage 4: Build and render

Build the HyperFrames composition:

```bash
python3 "$COMIC_SKILL/scripts/build_hyperframes.py" comic-drama-project/story.json \
  --project-dir comic-drama-project
```

The builder must preserve `audio-manifest.json.master_audio` when scene-level narration is present; do not reconstruct or overwrite the approved globally accelerated master. Legacy sentence-level projects may still be pre-mixed. Use one narration audio clip in HyperFrames.

The visible frame must contain only:

- One full-bleed 16:9 scene image using `object-fit: cover`.
- One whole-sentence caption at the bottom when narration is active.

Use the scene focal point for crop protection, a slow scale move, and a 0.5-second crossfade. Do not add visible titles, cards, UI, logos, borders, decorations, or sound-effect elements.

Run all quality gates before preview or render:

```bash
cd comic-drama-project
npm run check
npm run dev
```

Use the Studio URL printed by HyperFrames for review. For dense captions, also run `npx hyperframes inspect --samples 30`. Render a picture track to a distinct path, then finalize it with verified narration and optional BGM:

```bash
npx hyperframes render --output renders/comic-drama-video-only.mp4
python3 "$COMIC_SKILL/scripts/finalize_video.py" story.json \
  --project-dir . \
  --video renders/comic-drama-video-only.mp4 \
  --output renders/comic-drama-final.mp4
```

Do not assume the HyperFrames renderer embedded audio. The finalizer requires exactly one 1920x1080 30 fps video stream and one audio stream, and rejects duration drift from `build/audio-manifest.json`.

Report the final `story.json`, approval state, image/audio manifests, Studio URL, and MP4 path.

## Failure rules

- Stop on JSON validation errors, missing approvals, missing reference assets, or a timeline over 900 seconds.
- Preserve completed files and manifests after partial image or TTS failure.
- Treat a complete, structurally valid local PNG as success even when an upstream connection does not close; adopt it into the manifest instead of paying for a duplicate request.
- Retry image generation at most three times; then report exact failed scene IDs.
- Do not silently change model, style reference, narrator, or approved story content.
- Do not render with placeholder images, silent missing narration, or absent BGM when BGM is enabled.
- Never trade story coherence for a target scene count. The 600-scene value is a capacity limit only.
- Never use voice-preview optimization for production narration.
- Never apply `atempo` independently to short captions. Apply it once to the complete scene-joined master.
- Never use `silenceremove` or other internal pause compaction on the scene-level path.
- Never claim a final MP4 is complete until `ffprobe` confirms both video and audio streams.

## Offline checks

Use dry runs before a live provider call:

```bash
python3 "$COMIC_SKILL/scripts/generate_images.py" comic-drama-project/story.json \
  --project-dir comic-drama-project --phase scenes --dry-run --limit 2
python3 "$COMIC_SKILL/scripts/generate_visuals.py" comic-drama-project/story.json \
  --project-dir comic-drama-project --dry-run
python3 "$COMIC_SKILL/scripts/generate_audio.py" comic-drama-project/story.json \
  --project-dir comic-drama-project --dry-run --limit 2
python3 "$COMIC_SKILL/scripts/generate_scene_audio.py" comic-drama-project/story.json \
  --project-dir comic-drama-project --dry-run --limit 2 --concurrency 10
python3 "$COMIC_SKILL/scripts/generate_bgm.py" comic-drama-project/story.json \
  --project-dir comic-drama-project --dry-run
python3 "$COMIC_SKILL/scripts/generate_voice_previews.py" \
  --project-dir comic-drama-project --dry-run
```
