# Runtime Requirements

## Preflight

Run `scripts/preflight.py` before scaffolding or live requests. It checks Python, Node.js 22+, npx, FFmpeg, FFprobe, the bundled imagegen CLI, selected provider variables, and only the optional local packages requested for the run. It prints variable names and readiness, never credential values.

After scaffolding, run `npx hyperframes doctor`. Treat missing dependencies according to the selected path: Chrome, FFmpeg, FFprobe, Node, and npx are required for rendering; Kokoro is optional when using MiMo; MusicGen/Torch are optional when BGM is disabled; Whisper and Docker are not required for pause-aligned scene narration and standard local rendering.

## Image API

Use `gpt-image-2` through the installed imagegen fallback CLI. Configure the OpenAI-compatible service with environment variables; never pass a key as a command argument or write it into project files.

```bash
export COMIC_IMAGE_BASE_URL="https://example.com/v1"
export COMIC_IMAGE_API_KEY="..."
export COMIC_IMAGE_MODEL="gpt-image-2"
```

The dispatcher maps these variables to `OPENAI_BASE_URL` and `OPENAI_API_KEY` only for child processes. The service must implement `POST /v1/images/generations` and `POST /v1/images/edits`, return `data[].b64_json`, and accept multiple edit input images. Scene generation uses the edits endpoint with the style reference first and character sheets after it.

The dispatcher accepts either an API root or a `/v1` base URL and normalizes it to a single trailing `/v1`. It rejects credentials, query strings, and fragments in the URL. It never records the key; manifests record only the normalized endpoint and locked model.

Image API child processes remove `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`, and lowercase equivalents before connecting. Do not route image generation through a local or inherited proxy.

The image dispatcher accepts concurrency from 1 through 10. Keep normal production concurrency conservative and use the upper limit only when the provider account and rate limits support it. After an interrupted parent process leaves valid PNG files without manifest entries, use `--adopt-existing` once to validate and checkpoint them without repeating paid requests.

Each image job checkpoints `queued`, `submitted`, `waiting_response`, `file_ready`, and `complete` states with timestamps and five-second heartbeats. Treat a PNG as ready after its complete `IEND` chunk is present. Accept provider-returned dimensions and aspect ratios, record the actual size and any mismatch warning, and rely on the focal-point-aware `object-fit: cover` composition crop. Once a complete target file is ready, the dispatcher may terminate a lingering SDK child after a short grace period and record success instead of waiting for the HTTP connection to close.

Each attempt also has a 600-second local-file timeout by default. If the provider reports success but no complete PNG reaches disk, the dispatcher records `timed_out`, terminates the stuck connection, and retries within the configured three-attempt limit. Override with `--request-timeout-seconds` only within 60-3600 seconds.

Install the Python SDK in the active environment when needed:

```bash
uv pip install openai
```

## Narration providers

Each run records provider, model, voice, tone, speed, and language in `story.json`. Existing stories without provider/model remain compatible and default to `local_kokoro` with `kokoro-82m`.

### Xiaomi MiMo v2.5 TTS

Set `narrator.provider` to `xiaomi_mimo`. Use `mimo-v2.5-tts` with a documented preset voice, or use `mimo-v2.5-tts-voicedesign` with a stable logical `voice` name and a non-empty `voice_design` description. Chinese male presets include `苏打` and `白桦`. Configure secrets only through the environment:

```bash
export COMIC_TTS_BASE_URL="https://api.xiaomimimo.com/v1"
export COMIC_TTS_API_KEY="..."
```

`MIMO_BASE_URL` and `MIMO_API_KEY` are accepted aliases. `generate_scene_audio.py` calls `POST /v1/chat/completions` once per visual scene, puts a stable voice/delivery description in the `user` message, puts the exact combined scene narration in the `assistant` message, and requests Base64 WAV. Voice-design requests omit `audio.voice` and set `audio.optimize_text_preview=false`. Raw scene files normalize to 24 kHz mono PCM at speed 1.0 with no `silenceremove`. The helper joins scenes with a 0.35-second default gap, applies the story's numeric `atempo` once to the whole master, detects pauses in each raw scene, and maps short captions onto the accelerated master. Requests retry HTTP 429, 5xx, and network failures at most three times. Concurrency accepts 1-10. Credentials are redacted from errors and never enter manifests.

`build/audio-scene-jobs.json` caches paid scene requests independently of the numeric global speed, so changing only `narrator.speed` can reuse raw scene audio. `build/audio-alignment.json` records expected and selected pause boundaries plus proportional fallbacks. `build/audio-manifest.json.master_audio` points to the authoritative final WAV; the composition builder must preserve it.

Generate auditions with `scripts/generate_voice_previews.py`. It intentionally sets preview optimization to `true` only for designed-voice samples. Use identical text and speed across candidates, then copy the approved profile's logical voice name and exact design description into `story.json`.

### Local Kokoro

HyperFrames TTS uses Kokoro-82M. Mandarin uses the `zf_xiaobei` voice and `zh` language unless the user specifies another available voice.

```bash
uv pip install kokoro-onnx soundfile
npx hyperframes tts --list
```

Non-English phonemization also requires `espeak-ng`. Run `npx hyperframes doctor` before generating audio.

## Optional local background music

The bundled BGM helper uses `facebook/musicgen-small` by default and loops the generated seed bed to the final duration with FFmpeg.
Run it only when `audio.bgm.enabled` is `true`. When disabled, do not install MusicGen dependencies, download a model, or require a BGM file during composition.

```bash
uv pip install transformers torch soundfile numpy
```

Set `MUSICGEN_MODEL` to override the local model. Model downloads are large and occur on first use. No sound effects are generated.

The MusicGen helper removes all standard proxy environment variables before model download and inference. Fetch model assets directly.

## HyperFrames

Require Node.js 22+, Chrome, FFmpeg, and FFprobe. Scaffold each output project through HyperFrames before composition:

```bash
npx hyperframes init comic-drama-project --non-interactive
npx hyperframes doctor
```

Use the project's pinned HyperFrames command when available. Otherwise the helper scripts default to `npx --yes hyperframes@0.7.48`.

HyperFrames can render a picture-only MP4 even when composition audio exists. Always keep the render output distinct, then run `scripts/finalize_video.py` to mux `assets/audio/narration-timeline.wav` and optional manifest BGM. The finalizer probes stream count, resolution, frame rate, and duration before accepting the output.
