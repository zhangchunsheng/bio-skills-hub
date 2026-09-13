# Production Lessons

Use this checklist for provider recovery, late narration changes, MiMo voice design, and final delivery.

## Intake and preflight

- Ask only for a theme as the required creative input. Present defaults for reference image, narrator, caption length, BGM, and ending instead of blocking on optional answers.
- Run preflight before scaffolding. Report missing command or environment-variable names without printing secrets.
- Do not install optional local TTS, MusicGen, Whisper, or Docker dependencies unless the chosen workflow needs them.

## Image provider completion

- Trust a validated local PNG with a complete `IEND` chunk over a lingering HTTP connection.
- Checkpoint `queued`, `submitted`, `waiting_response`, `file_ready`, and `complete` states with timestamps.
- Use `--adopt-existing` after interruption when complete PNG files exist without manifest entries.
- Accept provider-returned dimensions, record the mismatch, and rely on focal-point-aware `object-fit: cover` unless the user requires an exact aspect ratio.
- Strip proxy variables from image and local-music subprocesses. Do not silently route those providers through an inherited local proxy.

## Narration and approved images

- Treat every narration entry as one displayed caption, but synthesize all entries attached to one approved scene image as one continuous MiMo spoken unit.
- Set `project.caption_max_characters`; use 20-24 for short social captions unless the user requests otherwise.
- After images are approved, wording, perspective, and caption splitting are low-risk. A changed location, occupation, action, visible prop, character, age, or time is a semantic image change and must return to image review.
- Keep story drafts separate until approval. Apply approved narration to `story.json` only at the audio stage.
- Generate anchor, character sheets, and all scene images before one combined visual review. Do not make the user approve character sheets and scene images in separate stops unless explicitly requested.

## MiMo voice design

- Audition preset and designed voices on identical text and speed before generating a long story.
- Use `audio.optimize_text_preview=true` only for audition samples.
- Use `audio.optimize_text_preview=false` for production. When true on short production lines, MiMo may expand the preview text and produce durations several times longer than expected.
- Keep the exact `voice_design` plus delivery prompt stable across every scene. Do not append per-caption emotion instructions that cause the model to redesign cadence.
- Tell the model to enter sentences directly and keep phrase speed even. Do not request each 20-character caption independently; repeated short requests cause slow openings and abrupt fast continuations.
- Normalize raw scene WAVs at speed 1.0, join them, then apply numeric `atempo` once to the complete master. Never apply separate speed filters to each caption.
- Do not use `silenceremove` on this path. Preserve natural internal pauses; detect them only to derive caption timing.
- Review proportional fallbacks in `build/audio-alignment.json`. They are acceptable only after confirming the affected caption timing.
- Compare actual duration against the draft estimate. Large expansion is a request-format failure until proven otherwise.

## Optional music

- Default BGM to disabled. Do not install Torch, download MusicGen, or generate music unless the user explicitly requests it.
- When disabled, narration generation, composition, and finalization must not require a BGM file or manifest entry.

## Final render

- HyperFrames may emit a video-only MP4 even when the composition contains `<audio>` elements.
- Render to a `video-only` filename, then use `scripts/finalize_video.py` to mux narration and optional BGM.
- Run lint, validate, and inspect before rendering; use at least 30 inspect samples for dense caption timelines.
- Probe the final MP4 for 1920x1080, 30 fps, exactly one video stream, exactly one audio stream, and duration agreement with the audio manifest.
- Extract several frames across opening, conflict, climax, and ending to verify images and captions visually.

## Credentials

- Keep API keys in environment variables only. Never write them into story JSON, manifests, logs, commands, or source files.
- If a key was pasted into a conversation or log, rotate it even when project files remain clean.
