#!/usr/bin/env python3
"""Generate scene-level MiMo narration, then align short captions to one master track."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any
import wave

from generate_audio import (
    MIMO_VOICE_DESIGN_MODEL,
    atomic_write_json,
    narrator_runtime,
    normalize_mimo_wav,
    probe_duration,
    request_mimo_wav,
)
from validate_story import TRANSITION_SECONDS, estimate_text_seconds, load_story, validate_story


SAMPLE_RATE = 24000
DEFAULT_SCENE_GAP_SECONDS = 0.35
PUNCTUATION = set("，。！？；：、,.!?;:\"'“”‘’（）()《》〈〉—-…")
SCENE_DELIVERY_DIRECTION = (
    "整体语速自然偏快，但不要机械赶字。句首直接进入，不拖长开头一两个字；"
    "短语间只作自然短停顿，同一句内语速均匀。保持用户指定的整体表达和情绪基调。"
    "严格朗读目标文本，不添加、改写或省略内容。"
)


def build_scene_text(scene: dict[str, Any]) -> str:
    return "".join(line["text"].strip() for line in scene["narrations"])


def build_scene_mimo_payload(
    narrator: dict[str, Any], runtime: dict[str, str], text: str
) -> dict[str, Any]:
    if runtime["model"] == MIMO_VOICE_DESIGN_MODEL:
        style_instruction = (
            narrator["voice_design"].rstrip()
            + f"\n整体表达：{narrator['tone']}。"
            + SCENE_DELIVERY_DIRECTION
        )
        audio: dict[str, Any] = {"format": "wav", "optimize_text_preview": False}
    else:
        style_instruction = (
            f"请使用{narrator['language']}旁白。整体表达：{narrator['tone']}。"
            + SCENE_DELIVERY_DIRECTION
        )
        audio = {"format": "wav", "voice": narrator["voice"]}
    return {
        "model": runtime["model"],
        "messages": [
            {"role": "user", "content": style_instruction},
            {"role": "assistant", "content": text},
        ],
        "audio": audio,
    }


def scene_fingerprint(
    narrator: dict[str, Any], runtime: dict[str, str], scene_id: str, text: str
) -> str:
    payload = {
        "scene_id": scene_id,
        "text": text,
        "provider": runtime["provider"],
        "model": runtime["model"],
        "voice": narrator["voice"],
        "voice_design": narrator.get("voice_design"),
        "tone": narrator["tone"],
        "language": narrator["language"],
        "delivery_direction": SCENE_DELIVERY_DIRECTION,
        "normalize_speed": 1.0,
        "compact_pauses": False,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def generate_scene_job(
    narrator: dict[str, Any],
    runtime: dict[str, str],
    text: str,
    output: Path,
    api_key: str,
    attempts: int,
    ffmpeg: list[str],
    ffprobe: list[str],
) -> float:
    payload = build_scene_mimo_payload(narrator, runtime, text)
    audio_bytes = request_mimo_wav(payload, runtime["base_url"], api_key, attempts)
    normalize_mimo_wav(
        audio_bytes,
        output,
        speed=1.0,
        ffmpeg_command=ffmpeg,
        compact_pauses=False,
    )
    return probe_duration(output, ffprobe)


def wav_frames(path: Path) -> int:
    with wave.open(str(path), "rb") as source:
        audio_format = (
            source.getnchannels(),
            source.getsampwidth(),
            source.getframerate(),
            source.getcomptype(),
        )
        if audio_format != (1, 2, SAMPLE_RATE, "NONE"):
            raise ValueError(f"expected 24 kHz mono 16-bit PCM WAV: {path}")
        return source.getnframes()


def join_wav_files(inputs: list[Path], output: Path, gap_seconds: float) -> int:
    if not inputs:
        raise ValueError("at least one scene WAV is required")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f"{output.stem}.tmp.wav")
    expected: tuple[int, int, int, str] | None = None
    total_frames = 0
    with wave.open(str(temporary), "wb") as joined:
        for index, path in enumerate(inputs):
            with wave.open(str(path), "rb") as source:
                current = (
                    source.getnchannels(),
                    source.getsampwidth(),
                    source.getframerate(),
                    source.getcomptype(),
                )
                if expected is None:
                    expected = current
                    if expected != (1, 2, SAMPLE_RATE, "NONE"):
                        raise ValueError(f"expected 24 kHz mono 16-bit PCM WAV: {path}")
                    joined.setnchannels(expected[0])
                    joined.setsampwidth(expected[1])
                    joined.setframerate(expected[2])
                elif current != expected:
                    raise ValueError(f"incompatible scene WAV format: {path}")
                if index:
                    gap_frames = round(gap_seconds * SAMPLE_RATE)
                    joined.writeframes(b"\0" * gap_frames * 2)
                    total_frames += gap_frames
                frames = source.getnframes()
                joined.writeframes(source.readframes(frames))
                total_frames += frames
    temporary.replace(output)
    return total_frames


def apply_global_speed(
    source: Path, output: Path, speed: float, ffmpeg: list[str]
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f"{output.stem}.tmp.wav")
    command = ffmpeg + [
        "-y",
        "-v",
        "error",
        "-i",
        str(source),
        "-filter:a",
        f"atempo={speed:.6f}",
        "-ar",
        str(SAMPLE_RATE),
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(temporary),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(completed.stderr.strip() or "ffmpeg failed to apply global speed")
    temporary.replace(output)


def detect_silences(path: Path, ffmpeg: list[str]) -> list[dict[str, float]]:
    command = ffmpeg + [
        "-v",
        "info",
        "-i",
        str(path),
        "-af",
        "silencedetect=noise=-42dB:d=0.12",
        "-f",
        "null",
        "-",
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"silence detection failed: {path}")
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", completed.stderr)]
    ends = [
        (float(end), float(duration))
        for end, duration in re.findall(
            r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", completed.stderr
        )
    ]
    return [
        {"start": start, "end": end, "duration": duration, "mid": (start + end) / 2}
        for start, (end, duration) in zip(starts, ends)
    ]


def text_weight(text: str) -> int:
    return max(1, sum(1 for char in text if not char.isspace() and char not in PUNCTUATION))


def select_boundaries(
    texts: list[str], duration: float, silences: list[dict[str, float]]
) -> tuple[list[float], list[float], list[dict[str, float]]]:
    if len(texts) == 1:
        return [], [], []
    weights = [text_weight(text) for text in texts]
    expected = [
        duration * sum(weights[:index]) / sum(weights)
        for index in range(1, len(weights))
    ]
    candidates = [
        item for item in silences if 0.45 <= item["mid"] <= duration - 0.45
    ]
    needed = len(texts) - 1
    best: tuple[float, tuple[dict[str, float], ...]] | None = None
    for chosen in combinations(candidates, needed):
        points = [0.0, *[item["mid"] for item in chosen], duration]
        if min(end - start for start, end in zip(points, points[1:])) < 0.55:
            continue
        score = 0.0
        for target, item in zip(expected, chosen):
            normalized_error = (item["mid"] - target) / max(duration, 1.0)
            score += normalized_error * normalized_error * 120
            score -= min(item["duration"], 0.9) * 0.9
        if best is None or score < best[0]:
            best = (score, chosen)
    if best is None:
        fallback = [
            {"start": value, "end": value, "duration": 0.0, "mid": value}
            for value in expected
        ]
        return expected, expected, fallback
    chosen_items = list(best[1])
    return [item["mid"] for item in chosen_items], expected, chosen_items


def write_caption_wav(
    output: Path,
    params: tuple[int, int, int, int, str, str],
    audio: bytes,
    start_frame: int,
    end_frame: int,
) -> None:
    channels, sample_width, sample_rate, _frame_count, compression, compression_name = params
    frame_width = channels * sample_width
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f"{output.stem}.tmp.wav")
    with wave.open(str(temporary), "wb") as target:
        target.setparams((channels, sample_width, sample_rate, 0, compression, compression_name))
        target.writeframes(audio[start_frame * frame_width : end_frame * frame_width])
    temporary.replace(output)


def build_timing_manifest(
    story: dict[str, Any],
    project_dir: Path,
    scene_files: list[Path],
    source_master: Path,
    final_master: Path,
    scene_gap_seconds: float,
    ffmpeg: list[str],
    runtime: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    scenes = story["scenes"]
    source_frames = [wav_frames(path) for path in scene_files]
    source_total_frames = wav_frames(source_master)
    with wave.open(str(final_master), "rb") as master:
        master_params = master.getparams()
        if (
            master.getnchannels(),
            master.getsampwidth(),
            master.getframerate(),
            master.getcomptype(),
        ) != (1, 2, SAMPLE_RATE, "NONE"):
            raise ValueError(f"expected 24 kHz mono 16-bit PCM WAV: {final_master}")
        output_frames = master.getnframes()
        master_audio = master.readframes(output_frames)
    ratio = output_frames / source_total_frames
    caption_dir = project_dir / "assets/audio/narration-captions"
    gap_frames = round(scene_gap_seconds * SAMPLE_RATE)
    jobs: dict[str, Any] = {}
    timed_scenes: list[dict[str, Any]] = []
    report_scenes: list[dict[str, Any]] = []
    source_cursor = 0
    for scene, scene_file, scene_frames in zip(scenes, scene_files, source_frames):
        scene_id = scene["id"]
        texts = [line["text"] for line in scene["narrations"]]
        raw_duration = scene_frames / SAMPLE_RATE
        silences = detect_silences(scene_file, ffmpeg)
        boundaries, expected, chosen = select_boundaries(texts, raw_duration, silences)
        local_frames = [0, *[round(value * SAMPLE_RATE) for value in boundaries], scene_frames]
        global_frames = [round((source_cursor + value) * ratio) for value in local_frames]
        lines: list[dict[str, Any]] = []
        for index, (narration, start_frame, end_frame) in enumerate(
            zip(scene["narrations"], global_frames, global_frames[1:]), start=1
        ):
            if end_frame <= start_frame:
                raise ValueError(f"non-positive caption duration: {scene_id}:{index:03d}")
            key = f"{scene_id}:{index:03d}"
            output = caption_dir / f"{scene_id}-{index:03d}.wav"
            write_caption_wav(output, master_params, master_audio, start_frame, end_frame)
            relative_file = str(output.relative_to(project_dir))
            duration = (end_frame - start_frame) / SAMPLE_RATE
            lines.append(
                {
                    "text": narration["text"],
                    "emotion": narration["emotion"],
                    "file": relative_file,
                    "start": round(start_frame / SAMPLE_RATE, 6),
                    "duration": round(duration, 6),
                }
            )
            jobs[key] = {
                "status": "complete",
                "file": relative_file,
                "duration": round(duration, 6),
                "text": narration["text"],
                "timing_method": "scene_silence_alignment",
            }
        timed_scenes.append(
            {
                "id": scene_id,
                "start": round(global_frames[0] / SAMPLE_RATE, 6),
                "duration": 0.0,
                "lines": lines,
            }
        )
        report_scenes.append(
            {
                "id": scene_id,
                "source_duration": round(raw_duration, 6),
                "expected_boundaries": [round(value, 6) for value in expected],
                "selected_boundaries": [round(value, 6) for value in boundaries],
                "selected_silence_durations": [round(item["duration"], 6) for item in chosen],
                "used_proportional_fallback": any(item["duration"] == 0 for item in chosen),
            }
        )
        source_cursor += scene_frames + gap_frames

    timeline_duration = output_frames / SAMPLE_RATE
    for index, scene in enumerate(timed_scenes):
        start = float(scene["start"])
        if index + 1 < len(timed_scenes):
            next_start = float(timed_scenes[index + 1]["start"])
            scene["duration"] = round(next_start - start + TRANSITION_SECONDS, 6)
        else:
            scene["duration"] = round(timeline_duration - start, 6)

    manifest = {
        "jobs": jobs,
        "narration_backend": {
            "provider": runtime["provider"],
            "model": runtime["model"],
            "voice": story["narrator"]["voice"],
            "processing": "scene_level_tts_then_global_atempo",
            "speed": float(story["narrator"]["speed"]),
            "compact_pauses": False,
        },
        "valid": timeline_duration <= 900,
        "transition_seconds": TRANSITION_SECONDS,
        "timeline_duration": round(timeline_duration, 6),
        "narrator": story["narrator"],
        "master_audio": str(final_master.relative_to(project_dir)),
        "scenes": timed_scenes,
    }
    report = {
        "source_scene_count": len(scenes),
        "caption_count": sum(len(scene["narrations"]) for scene in scenes),
        "source_total_frames": source_total_frames,
        "output_total_frames": output_frames,
        "global_time_ratio": ratio,
        "scene_gap_source_seconds": scene_gap_seconds,
        "speed": float(story["narrator"]["speed"]),
        "compact_pauses": False,
        "scenes": report_scenes,
    }
    return manifest, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("story", type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, help="Process only the first N scenes in dry-run")
    args = parser.parse_args()

    if not 1 <= args.attempts <= 3:
        print("Error: attempts must be between 1 and 3", file=sys.stderr)
        return 1
    if not 1 <= args.concurrency <= 10:
        print("Error: concurrency must be between 1 and 10", file=sys.stderr)
        return 1
    if args.limit is not None and not args.dry_run:
        print("Error: --limit is only available with --dry-run", file=sys.stderr)
        return 1

    story_path = args.story.resolve()
    try:
        story = load_story(story_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    validation = validate_story(story)
    if not validation["valid"]:
        for error in validation["errors"]:
            print(f"Error: {error}", file=sys.stderr)
        return 1
    if story["approvals"]["scene_images"] != "approved" and not args.dry_run:
        print("Error: approve all scene images before generating narration", file=sys.stderr)
        return 1

    project_dir = (args.project_dir or story_path.parent).resolve()
    narrator = story["narrator"]
    try:
        runtime = narrator_runtime(narrator)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if runtime["provider"] != "xiaomi_mimo":
        print("Error: scene-level narration requires narrator.provider=xiaomi_mimo", file=sys.stderr)
        return 1

    scenes = story["scenes"]
    if args.limit is not None:
        scenes = scenes[: max(0, args.limit)]
    speed = float(narrator["speed"])
    if args.dry_run:
        for scene in scenes:
            print(
                f"[{scene['id']}] xiaomi_mimo scene request model={runtime['model']} "
                f"voice={narrator['voice']} captions={len(scene['narrations'])}"
            )
        estimated = sum(
            estimate_text_seconds(build_scene_text(scene), speed) for scene in scenes
        )
        print(
            f"Dry run: {len(scenes)} scene request(s), global atempo={speed:.3f}, "
            f"compact_pauses=false, about {estimated:.1f}s"
        )
        return 0

    api_key = os.getenv("COMIC_TTS_API_KEY") or os.getenv("MIMO_API_KEY") or ""
    if not api_key:
        print("Error: set COMIC_TTS_API_KEY or MIMO_API_KEY", file=sys.stderr)
        return 1
    ffmpeg = shlex.split(os.getenv("FFMPEG_BIN", "ffmpeg"))
    ffprobe = shlex.split(os.getenv("FFPROBE_BIN", "ffprobe"))
    audio_dir = project_dir / "assets/audio/narration-scenes"
    audio_dir.mkdir(parents=True, exist_ok=True)
    jobs_path = project_dir / "build/audio-scene-jobs.json"
    try:
        scene_state = json.loads(jobs_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        scene_state = {"jobs": {}}
    if not isinstance(scene_state.get("jobs"), dict):
        scene_state["jobs"] = {}

    expected_ids = {scene["id"] for scene in story["scenes"]}
    scene_state["jobs"] = {
        key: value for key, value in scene_state["jobs"].items() if key in expected_ids
    }
    pending: list[dict[str, Any]] = []
    for scene in story["scenes"]:
        scene_id = scene["id"]
        text = build_scene_text(scene)
        output = audio_dir / f"{scene_id}.wav"
        fingerprint = scene_fingerprint(narrator, runtime, scene_id, text)
        previous = scene_state["jobs"].get(scene_id, {})
        if output.exists() and previous.get("fingerprint") == fingerprint and not args.force:
            try:
                duration = probe_duration(output, ffprobe)
                previous.update({"status": "complete", "duration": round(duration, 6)})
                print(f"[{scene_id}] skipped matching output ({duration:.2f}s)")
                continue
            except Exception:
                pass
        scene_state["jobs"][scene_id] = {
            "status": "submitted",
            "file": str(output.relative_to(project_dir)),
            "text": text,
            "caption_count": len(scene["narrations"]),
            "fingerprint": fingerprint,
        }
        pending.append(
            {
                "scene_id": scene_id,
                "text": text,
                "output": output,
                "fingerprint": fingerprint,
            }
        )
    scene_state["configuration"] = {
        "unit": "scene",
        "model": runtime["model"],
        "voice": narrator["voice"],
        "normalize_speed": 1.0,
        "compact_pauses": False,
    }
    atomic_write_json(jobs_path, scene_state)

    failures = 0
    if pending:
        workers = min(args.concurrency, len(pending))
        print(f"Generating {len(pending)} scene-level MiMo job(s) with concurrency {workers}")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(
                    generate_scene_job,
                    narrator,
                    runtime,
                    job["text"],
                    job["output"],
                    api_key,
                    args.attempts,
                    ffmpeg,
                    ffprobe,
                ): job
                for job in pending
            }
            for future in as_completed(future_map):
                job = future_map[future]
                scene_id = job["scene_id"]
                try:
                    duration = future.result()
                except Exception as exc:
                    failures += 1
                    detail = str(exc).replace(api_key, "[redacted]")
                    scene_state["jobs"][scene_id].update(
                        {"status": "failed", "error": detail[-2000:]}
                    )
                    print(f"[{scene_id}] failed: {detail}", file=sys.stderr)
                else:
                    scene_state["jobs"][scene_id].update(
                        {"status": "complete", "duration": round(duration, 6)}
                    )
                    print(f"[{scene_id}] complete ({duration:.2f}s)")
                atomic_write_json(jobs_path, scene_state)
    if failures:
        print(f"Scene narration stopped with {failures} failure(s)", file=sys.stderr)
        return 1

    scene_files = [audio_dir / f"{scene['id']}.wav" for scene in story["scenes"]]
    if any(not path.exists() for path in scene_files):
        print("Error: one or more completed scene WAV files are missing", file=sys.stderr)
        return 1
    scene_gap = float(story["audio"].get("scene_gap_seconds", DEFAULT_SCENE_GAP_SECONDS))
    source_master = project_dir / "assets/audio/narration-scene-source.wav"
    final_master = project_dir / "assets/audio/narration-timeline.wav"
    join_wav_files(scene_files, source_master, scene_gap)
    apply_global_speed(source_master, final_master, speed, ffmpeg)
    try:
        manifest, alignment = build_timing_manifest(
            story,
            project_dir,
            scene_files,
            source_master,
            final_master,
            scene_gap,
            ffmpeg,
            runtime,
        )
    except (OSError, RuntimeError, ValueError, wave.Error) as exc:
        print(f"Error: failed to align scene narration: {exc}", file=sys.stderr)
        return 1
    manifest_path = project_dir / "build/audio-manifest.json"
    alignment_path = project_dir / "build/audio-alignment.json"
    atomic_write_json(manifest_path, manifest)
    atomic_write_json(alignment_path, alignment)
    if not manifest["valid"]:
        print(
            f"Error: actual narration timeline is {manifest['timeline_duration']:.1f}s; "
            "condense below 900s and re-approve",
            file=sys.stderr,
        )
        return 1
    fallback_count = sum(
        scene["used_proportional_fallback"] for scene in alignment["scenes"]
    )
    print(
        f"Audio manifest: {manifest_path} ({manifest['timeline_duration']:.1f}s, "
        f"{len(story['scenes'])} scene requests, {alignment['caption_count']} captions, "
        f"{fallback_count} proportional fallback scene(s))"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
