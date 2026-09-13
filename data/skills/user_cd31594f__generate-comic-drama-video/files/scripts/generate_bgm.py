#!/usr/bin/env python3
"""Generate a local MusicGen bed and extend it to the narration timeline."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any

from validate_story import load_story, validate_story


PROXY_ENV_VARS = {
    "ALL_PROXY",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
    "all_proxy",
    "http_proxy",
    "https_proxy",
    "no_proxy",
}


def clear_proxy_environment() -> None:
    for key in PROXY_ENV_VARS:
        os.environ.pop(key, None)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def probe_duration(path: Path) -> float:
    ffprobe = shlex.split(os.getenv("FFPROBE_BIN", "ffprobe"))
    completed = subprocess.run(
        ffprobe
        + ["-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"ffprobe failed for {path}")
    return float(json.loads(completed.stdout)["format"]["duration"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate local background music with MusicGen")
    parser.add_argument("story", type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda", "mps"), default="auto")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    clear_proxy_environment()

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
    project_dir = (args.project_dir or story_path.parent).resolve()
    manifest_path = project_dir / "build/audio-manifest.json"
    try:
        audio_manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        if args.dry_run:
            audio_manifest = {"timeline_duration": report["estimated_duration_seconds"]}
        else:
            print("Error: generate narration before background music", file=sys.stderr)
            return 1
    timeline_duration = float(audio_manifest.get("timeline_duration", 0))
    if timeline_duration <= 0 or timeline_duration > 900:
        print("Error: audio manifest must contain a timeline duration between 0 and 900 seconds", file=sys.stderr)
        return 1

    bgm = story["audio"]["bgm"]
    prompts = bgm["prompts"]
    model_name = os.getenv("MUSICGEN_MODEL", bgm.get("model", "facebook/musicgen-small"))
    seed_seconds = float(bgm.get("seed_seconds", 20))
    output_dir = project_dir / "assets/audio/bgm"
    output = output_dir / "background-music.wav"
    if output.exists() and not args.force:
        try:
            existing_duration = probe_duration(output)
        except Exception as exc:
            print(f"Error: existing BGM is invalid: {exc}", file=sys.stderr)
            return 1
        if existing_duration + 0.05 < timeline_duration:
            print("Error: existing BGM is shorter than the narration timeline; use --force", file=sys.stderr)
            return 1
        audio_manifest["bgm"] = {
            "file": str(output.relative_to(project_dir)),
            "duration": round(timeline_duration, 6),
            "volume": float(bgm["volume"]),
            "model": model_name,
        }
        atomic_write_json(manifest_path, audio_manifest)
        print(f"Skipped existing {output}; refreshed audio manifest")
        return 0

    if args.dry_run:
        print(
            json.dumps(
                {
                    "model": model_name,
                    "device": args.device,
                    "prompts": prompts,
                    "seed_seconds": seed_seconds,
                    "timeline_duration": timeline_duration,
                    "output": str(output),
                    "dependencies": ["transformers", "torch", "soundfile", "numpy", "ffmpeg"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    try:
        import numpy as np
        import soundfile as sf
        import torch
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
    except ImportError:
        print(
            "Error: install local BGM dependencies with "
            "`uv pip install transformers torch soundfile numpy`",
            file=sys.stderr,
        )
        return 1

    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device

    output_dir.mkdir(parents=True, exist_ok=True)
    processor = AutoProcessor.from_pretrained(model_name)
    model = MusicgenForConditionalGeneration.from_pretrained(model_name).to(device)
    inputs = processor(text=prompts, padding=True, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    max_new_tokens = min(1500, max(256, int(round(seed_seconds * 50))))
    with torch.inference_mode():
        generated = model.generate(**inputs, max_new_tokens=max_new_tokens)
    sample_rate = int(model.config.audio_encoder.sampling_rate)

    seed_paths: list[Path] = []
    for index in range(len(prompts)):
        values = generated[index, 0].detach().cpu().float().numpy()
        peak = float(np.max(np.abs(values))) or 1.0
        values = values / max(1.0, peak)
        seed_path = output_dir / f"seed-{index + 1:02d}.wav"
        sf.write(seed_path, values, sample_rate)
        seed_paths.append(seed_path)

    concat_path = project_dir / "build/bgm-concat.txt"
    concat_path.parent.mkdir(parents=True, exist_ok=True)
    concat_path.write_text(
        "".join(f"file '{str(path).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'\n" for path in seed_paths),
        encoding="utf-8",
    )
    combined = output_dir / "combined-seeds.wav"
    ffmpeg = shlex.split(os.getenv("FFMPEG_BIN", "ffmpeg"))
    concat_command = ffmpeg + [
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
        "-c:a",
        "pcm_s16le",
        str(combined),
    ]
    completed = subprocess.run(concat_command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        print(f"Error: {completed.stderr.strip()}", file=sys.stderr)
        return 1

    fade_out_start = max(0.0, timeline_duration - 3.0)
    loop_command = ffmpeg + [
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(combined),
        "-t",
        f"{timeline_duration:.6f}",
        "-af",
        f"afade=t=in:st=0:d=2,afade=t=out:st={fade_out_start:.6f}:d=3",
        "-c:a",
        "pcm_s16le",
        str(output),
    ]
    completed = subprocess.run(loop_command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        print(f"Error: {completed.stderr.strip()}", file=sys.stderr)
        return 1

    audio_manifest["bgm"] = {
        "file": str(output.relative_to(project_dir)),
        "duration": round(timeline_duration, 6),
        "volume": float(bgm["volume"]),
        "model": model_name,
    }
    atomic_write_json(manifest_path, audio_manifest)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
