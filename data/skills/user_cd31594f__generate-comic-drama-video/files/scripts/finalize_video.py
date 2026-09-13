#!/usr/bin/env python3
"""Mux the rendered picture track with verified narration and optional BGM."""

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


def run_json(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "media probe failed")
    return json.loads(completed.stdout)


def probe_media(path: Path, ffprobe: list[str]) -> dict[str, Any]:
    return run_json(
        ffprobe
        + [
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ]
    )


def validate_final_media(media: dict[str, Any], expected_duration: float) -> list[str]:
    problems: list[str] = []
    streams = media.get("streams", [])
    videos = [item for item in streams if item.get("codec_type") == "video"]
    audios = [item for item in streams if item.get("codec_type") == "audio"]
    if len(videos) != 1:
        problems.append("final video must contain exactly one video stream")
    else:
        video = videos[0]
        if (video.get("width"), video.get("height")) != (1920, 1080):
            problems.append("final video must be 1920x1080")
        if video.get("r_frame_rate") != "30/1":
            problems.append("final video must be 30 fps")
    if len(audios) != 1:
        problems.append("final video must contain exactly one audio stream")
    duration = float(media.get("format", {}).get("duration", 0))
    if abs(duration - expected_duration) > 0.15:
        problems.append(
            f"final duration {duration:.3f}s differs from manifest {expected_duration:.3f}s"
        )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize a rendered comic-drama MP4")
    parser.add_argument("story", type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--video", type=Path, required=True, help="Rendered video-only MP4")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
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
    video = args.video.resolve()
    output = args.output.resolve()
    manifest_path = project_dir / "build/audio-manifest.json"
    narration = project_dir / "assets/audio/narration-timeline.wav"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("Error: valid build/audio-manifest.json not found", file=sys.stderr)
        return 1
    duration = float(manifest.get("timeline_duration", 0))
    if manifest.get("valid") is not True or not 0 < duration <= 900:
        print("Error: audio manifest is invalid", file=sys.stderr)
        return 1
    if not video.exists() or not narration.exists():
        print("Error: rendered video or narration timeline is missing", file=sys.stderr)
        return 1
    ffmpeg = shlex.split(os.getenv("FFMPEG_BIN", "ffmpeg"))
    ffprobe = shlex.split(os.getenv("FFPROBE_BIN", "ffprobe"))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f"{output.stem}.tmp{output.suffix}")

    command = ffmpeg + ["-y", "-v", "error", "-i", str(video), "-i", str(narration)]
    bgm = manifest.get("bgm") if story["audio"]["bgm"]["enabled"] else None
    if bgm:
        bgm_path = project_dir / bgm["file"]
        if not bgm_path.exists():
            print(f"Error: missing background music: {bgm_path}", file=sys.stderr)
            return 1
        volume = float(bgm["volume"])
        command += [
            "-i",
            str(bgm_path),
            "-filter_complex",
            f"[1:a]volume=1[n];[2:a]volume={volume:.6f}[b];[n][b]amix=inputs=2:duration=longest:normalize=0[a]",
            "-map",
            "0:v:0",
            "-map",
            "[a]",
        ]
    else:
        command += ["-map", "0:v:0", "-map", "1:a:0"]
    command += [
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-t",
        f"{duration:.6f}",
        "-movflags",
        "+faststart",
        str(temporary),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        temporary.unlink(missing_ok=True)
        print(f"Error: {completed.stderr.strip() or 'ffmpeg finalization failed'}", file=sys.stderr)
        return 1
    try:
        media = probe_media(temporary, ffprobe)
        problems = validate_final_media(media, duration)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        temporary.unlink(missing_ok=True)
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if problems:
        temporary.unlink(missing_ok=True)
        for problem in problems:
            print(f"Error: {problem}", file=sys.stderr)
        return 1
    temporary.replace(output)
    final_duration = float(media["format"]["duration"])
    print(f"Final video: {output} ({final_duration:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
