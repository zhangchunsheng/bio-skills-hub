#!/usr/bin/env python3
"""Generate resumable sentence-level narration and an exact timing manifest."""

from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from validate_story import TRANSITION_SECONDS, estimate_text_seconds, load_story, validate_story


DEFAULT_HYPERFRAMES_COMMAND = "npx --yes hyperframes@0.7.48"
DEFAULT_LOCAL_MODEL = "kokoro-82m"
DEFAULT_MIMO_BASE_URL = "https://api.xiaomimimo.com/v1"
DEFAULT_MIMO_MODEL = "mimo-v2.5-tts"
MIMO_VOICE_DESIGN_MODEL = "mimo-v2.5-tts-voicedesign"


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def prune_narration_jobs(manifest: dict[str, Any], scenes: list[dict[str, Any]]) -> None:
    expected = {
        f"{scene['id']}:{index:03d}"
        for scene in scenes
        for index, _ in enumerate(scene["narrations"], start=1)
    }
    jobs = manifest.get("jobs", {})
    manifest["jobs"] = {key: value for key, value in jobs.items() if key in expected}


def normalize_api_base_url(raw: str) -> str:
    value = raw.strip().rstrip("/")
    parsed = urllib_parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("TTS base URL must be an absolute http(s) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("TTS base URL cannot contain credentials, query parameters, or fragments")
    path = parsed.path.rstrip("/")
    if not path.endswith("/v1"):
        path += "/v1"
    return urllib_parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def narrator_runtime(narrator: dict[str, Any]) -> dict[str, str]:
    provider = narrator.get("provider", "local_kokoro")
    default_model = DEFAULT_MIMO_MODEL if provider == "xiaomi_mimo" else DEFAULT_LOCAL_MODEL
    runtime = {
        "provider": provider,
        "model": narrator.get("model", default_model),
        "voice": narrator["voice"],
    }
    if provider == "xiaomi_mimo":
        base_url = os.getenv("COMIC_TTS_BASE_URL") or os.getenv("MIMO_BASE_URL") or DEFAULT_MIMO_BASE_URL
        runtime["base_url"] = normalize_api_base_url(base_url)
    return runtime


def narration_fingerprint(
    narrator: dict[str, Any], runtime: dict[str, str], narration: dict[str, str]
) -> str:
    payload = {
        "provider": runtime["provider"],
        "model": runtime["model"],
        "voice": narrator["voice"],
        "voice_design": narrator.get("voice_design"),
        "tone": narrator["tone"],
        "speed": float(narrator["speed"]),
        "language": narrator["language"],
        "emotion": narration["emotion"],
        "text": narration["text"],
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_mimo_payload(
    narrator: dict[str, Any], runtime: dict[str, str], narration: dict[str, str]
) -> dict[str, Any]:
    if runtime["model"] == MIMO_VOICE_DESIGN_MODEL:
        # Keep the design prompt identical across every sentence. Adding per-line
        # direction here makes the model redesign both the voice and cadence.
        style_instruction = narrator["voice_design"]
        audio: dict[str, Any] = {"format": "wav", "optimize_text_preview": False}
    else:
        style_instruction = (
            f"请使用{narrator['language']}旁白。整体表达：{narrator['tone']}。"
            f"当前句情绪：{narration['emotion']}。以自然清晰的标准语速录制，"
            "不要添加、改写或省略目标文本。"
        )
        audio = {"format": "wav", "voice": narrator["voice"]}
    return {
        "model": runtime["model"],
        "messages": [
            {"role": "user", "content": style_instruction},
            {"role": "assistant", "content": narration["text"]},
        ],
        "audio": audio,
    }


def request_mimo_wav(
    payload: dict[str, Any], base_url: str, api_key: str, attempts: int
) -> bytes:
    endpoint = f"{base_url}/chat/completions"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error = "MiMo TTS request failed"
    for attempt in range(1, attempts + 1):
        request = urllib_request.Request(
            endpoint,
            data=body,
            headers={"api-key": api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib_request.urlopen(request, timeout=180) as response:
                response_data = json.loads(response.read().decode("utf-8"))
            audio_data = response_data["choices"][0]["message"]["audio"]["data"]
            if not isinstance(audio_data, str) or not audio_data:
                raise ValueError("MiMo response audio.data is empty")
            return base64.b64decode(audio_data, validate=True)
        except urllib_error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[-1500:]
            last_error = f"MiMo HTTP {exc.code}: {detail}"
            retryable = exc.code == 429 or 500 <= exc.code < 600
            if not retryable or attempt == attempts:
                break
        except (urllib_error.URLError, TimeoutError) as exc:
            last_error = f"MiMo network error: {exc}"
            if attempt == attempts:
                break
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            last_error = f"Invalid MiMo TTS response: {exc}"
            break
        time.sleep(min(8, 2 ** attempt))
    raise RuntimeError(last_error.replace(api_key, "[redacted]"))


def normalize_mimo_wav(
    audio_bytes: bytes,
    output: Path,
    speed: float,
    ffmpeg_command: list[str],
    compact_pauses: bool = False,
) -> None:
    source = output.with_name(f"{output.stem}.source.tmp.wav")
    temporary = output.with_name(f"{output.stem}.tmp.wav")
    source.write_bytes(audio_bytes)
    try:
        audio_filters = [f"atempo={speed:.6f}"]
        if compact_pauses:
            audio_filters.append(
                "silenceremove="
                "start_periods=1:start_duration=0.10:start_threshold=-50dB:start_silence=0.05:"
                "stop_periods=-1:stop_duration=0.45:stop_threshold=-50dB:stop_silence=0.18"
            )
        command = ffmpeg_command + [
            "-y",
            "-v",
            "error",
            "-i",
            str(source),
            "-filter:a",
            ",".join(audio_filters),
            "-ar",
            "24000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(temporary),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "ffmpeg failed to normalize MiMo audio")
        temporary.replace(output)
    finally:
        source.unlink(missing_ok=True)
        temporary.unlink(missing_ok=True)


def probe_duration(path: Path, ffprobe_command: list[str]) -> float:
    command = ffprobe_command + [
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"ffprobe failed for {path}")
    data = json.loads(completed.stdout)
    return float(data["format"]["duration"])


def generate_mimo_job(
    narrator: dict[str, Any],
    runtime: dict[str, str],
    narration: dict[str, str],
    output: Path,
    api_key: str,
    attempts: int,
    ffmpeg_command: list[str],
    ffprobe_command: list[str],
) -> float:
    payload = build_mimo_payload(narrator, runtime, narration)
    audio_bytes = request_mimo_wav(payload, runtime["base_url"], api_key, attempts)
    normalize_mimo_wav(
        audio_bytes,
        output,
        float(narrator["speed"]),
        ffmpeg_command,
        compact_pauses=runtime["model"] == MIMO_VOICE_DESIGN_MODEL,
    )
    return probe_duration(output, ffprobe_command)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate narration for a comic drama")
    parser.add_argument("story", type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, help="Process only the first N scenes")
    args = parser.parse_args()

    if not 1 <= args.attempts <= 3:
        print("Error: attempts must be between 1 and 3", file=sys.stderr)
        return 1
    if not 1 <= args.concurrency <= 10:
        print("Error: concurrency must be between 1 and 10", file=sys.stderr)
        return 1

    story_path = args.story.resolve()
    try:
        story = load_story(story_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    report = validate_story(story)
    if not report["valid"]:
        for error in report["errors"]:
            print(f"Error: {error}", file=sys.stderr)
        return 1
    if story["approvals"]["scene_images"] != "approved" and not args.dry_run:
        print("Error: approve all scene images before generating narration", file=sys.stderr)
        return 1

    project_dir = (args.project_dir or story_path.parent).resolve()
    audio_dir = project_dir / "assets/audio/narration"
    audio_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = project_dir / "build/audio-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        manifest = {"jobs": {}}
    if not isinstance(manifest.get("jobs"), dict):
        manifest["jobs"] = {}

    hyperframes = shlex.split(os.getenv("HYPERFRAMES_CMD", DEFAULT_HYPERFRAMES_COMMAND))
    ffmpeg = shlex.split(os.getenv("FFMPEG_BIN", "ffmpeg"))
    ffprobe = shlex.split(os.getenv("FFPROBE_BIN", "ffprobe"))
    narrator = story["narrator"]
    try:
        runtime = narrator_runtime(narrator)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    api_key = ""
    if runtime["provider"] == "xiaomi_mimo":
        api_key = os.getenv("COMIC_TTS_API_KEY") or os.getenv("MIMO_API_KEY") or ""
        if not api_key and not args.dry_run:
            print("Error: set COMIC_TTS_API_KEY or MIMO_API_KEY", file=sys.stderr)
            return 1

    scenes = story["scenes"]
    if args.limit is not None and not args.dry_run:
        print("Error: --limit is only available with --dry-run", file=sys.stderr)
        return 1
    if args.limit is not None:
        scenes = scenes[: max(0, args.limit)]
    if not args.dry_run and args.limit is None:
        prune_narration_jobs(manifest, scenes)

    failures = 0
    pending_mimo_jobs: list[dict[str, Any]] = []
    manifest["narration_backend"] = {
        key: value for key, value in runtime.items() if key in {"provider", "model", "base_url", "voice"}
    }
    for scene in scenes:
        for index, narration in enumerate(scene["narrations"], start=1):
            key = f"{scene['id']}:{index:03d}"
            output = audio_dir / f"{scene['id']}-{index:03d}.wav"
            fingerprint = narration_fingerprint(narrator, runtime, narration)
            previous_job = manifest["jobs"].get(key, {})
            cache_matches = previous_job.get("fingerprint") == fingerprint
            if output.exists() and cache_matches and not args.force and not args.dry_run:
                try:
                    duration = probe_duration(output, ffprobe)
                    manifest["jobs"][key].update(
                        {
                            "status": "complete",
                            "file": str(output.relative_to(project_dir)),
                            "duration": round(duration, 6),
                            "text": narration["text"],
                        }
                    )
                    atomic_write_json(manifest_path, manifest)
                    print(f"[{key}] skipped matching {output}")
                    continue
                except Exception as exc:
                    print(f"[{key}] existing file is invalid: {exc}", file=sys.stderr)

            local_command = hyperframes + [
                "tts",
                narration["text"],
                "--voice",
                narrator["voice"],
                "--speed",
                str(narrator["speed"]),
                "--lang",
                narrator["language"],
                "--output",
                str(output),
            ]
            if args.dry_run:
                if runtime["provider"] == "local_kokoro":
                    print(shlex.join(local_command))
                else:
                    print(
                        f"[{key}] xiaomi_mimo model={runtime['model']} "
                        f"voice={narrator['voice']} output={output}"
                    )
                continue

            if runtime["provider"] == "xiaomi_mimo":
                pending_mimo_jobs.append(
                    {
                        "key": key,
                        "narration": narration,
                        "output": output,
                        "fingerprint": fingerprint,
                    }
                )
                continue

            try:
                if runtime["provider"] == "local_kokoro":
                    completed = subprocess.run(
                        local_command, text=True, capture_output=True, check=False
                    )
                    if completed.returncode != 0:
                        detail = (completed.stdout + completed.stderr).strip()
                        raise RuntimeError(detail or "HyperFrames TTS failed")
                duration = probe_duration(output, ffprobe)
            except Exception as exc:
                failures += 1
                detail = str(exc).replace(api_key, "[redacted]") if api_key else str(exc)
                manifest["jobs"][key] = {
                    "status": "failed",
                    "fingerprint": fingerprint,
                    "error": detail[-2000:],
                }
                atomic_write_json(manifest_path, manifest)
                print(f"[{key}] failed: {detail}", file=sys.stderr)
                continue
            manifest["jobs"][key] = {
                "status": "complete",
                "file": str(output.relative_to(project_dir)),
                "duration": round(duration, 6),
                "text": narration["text"],
                "fingerprint": fingerprint,
            }
            atomic_write_json(manifest_path, manifest)
            print(f"[{key}] wrote {output} ({duration:.2f}s)")

    if pending_mimo_jobs and not args.dry_run:
        workers = min(args.concurrency, len(pending_mimo_jobs))
        print(f"Generating {len(pending_mimo_jobs)} MiMo narration job(s) with concurrency {workers}")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(
                    generate_mimo_job,
                    narrator,
                    runtime,
                    job["narration"],
                    job["output"],
                    api_key,
                    args.attempts,
                    ffmpeg,
                    ffprobe,
                ): job
                for job in pending_mimo_jobs
            }
            for future in as_completed(future_map):
                job = future_map[future]
                key = job["key"]
                try:
                    duration = future.result()
                except Exception as exc:
                    failures += 1
                    detail = str(exc).replace(api_key, "[redacted]")
                    manifest["jobs"][key] = {
                        "status": "failed",
                        "fingerprint": job["fingerprint"],
                        "error": detail[-2000:],
                    }
                    atomic_write_json(manifest_path, manifest)
                    print(f"[{key}] failed: {detail}", file=sys.stderr)
                    continue
                manifest["jobs"][key] = {
                    "status": "complete",
                    "file": str(job["output"].relative_to(project_dir)),
                    "duration": round(duration, 6),
                    "text": job["narration"]["text"],
                    "fingerprint": job["fingerprint"],
                }
                atomic_write_json(manifest_path, manifest)
                print(f"[{key}] wrote {job['output']} ({duration:.2f}s)")

    if args.dry_run:
        speed = float(narrator["speed"])
        estimated = sum(
            estimate_text_seconds(line["text"], speed)
            for scene in scenes
            for line in scene["narrations"]
        )
        print(
            f"Dry run: provider={runtime['provider']}, model={runtime['model']}, "
            f"{len(scenes)} scene(s), about {estimated:.1f}s of speech"
        )
        return 0
    if failures:
        print(f"Narration generation stopped with {failures} failure(s)", file=sys.stderr)
        return 1

    gap = float(story["audio"]["sentence_gap_seconds"])
    scene_start = 0.0
    timed_scenes: list[dict[str, Any]] = []
    for scene in story["scenes"]:
        cursor = 0.4
        lines: list[dict[str, Any]] = []
        for index, narration in enumerate(scene["narrations"], start=1):
            key = f"{scene['id']}:{index:03d}"
            job = manifest["jobs"].get(key)
            if not job or job.get("status") != "complete":
                print(f"Error: missing completed narration job {key}", file=sys.stderr)
                return 1
            duration = float(job["duration"])
            lines.append(
                {
                    "text": narration["text"],
                    "emotion": narration["emotion"],
                    "file": job["file"],
                    "start": round(scene_start + cursor, 6),
                    "duration": round(duration, 6),
                }
            )
            cursor += duration
            if index < len(scene["narrations"]):
                cursor += gap
        scene_duration = cursor + 0.4
        timed_scenes.append(
            {
                "id": scene["id"],
                "start": round(scene_start, 6),
                "duration": round(scene_duration, 6),
                "lines": lines,
            }
        )
        scene_start += scene_duration - TRANSITION_SECONDS

    timeline_duration = 0.0
    if timed_scenes:
        last = timed_scenes[-1]
        timeline_duration = float(last["start"]) + float(last["duration"])
    manifest.update(
        {
            "valid": timeline_duration <= 900,
            "transition_seconds": TRANSITION_SECONDS,
            "timeline_duration": round(timeline_duration, 6),
            "narrator": narrator,
            "scenes": timed_scenes,
        }
    )
    atomic_write_json(manifest_path, manifest)
    if timeline_duration > 900:
        print(
            f"Error: actual narration timeline is {timeline_duration:.1f}s; condense below 900s and re-approve",
            file=sys.stderr,
        )
        return 1
    print(f"Audio manifest: {manifest_path} ({timeline_duration:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
