#!/usr/bin/env python3
"""Build a deterministic HyperFrames composition from approved comic-drama assets."""

from __future__ import annotations

import argparse
from array import array
import html
import json
from pathlib import Path
import shutil
import sys
from typing import Any
import wave

from validate_story import load_story, validate_story


def asset_url(path: str) -> str:
    return Path(path).as_posix()


def script_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def resolve_bgm(
    story: dict[str, Any], audio_manifest: dict[str, Any], project_dir: Path
) -> dict[str, Any] | None:
    if not story["audio"]["bgm"]["enabled"]:
        return None
    bgm = audio_manifest.get("bgm")
    if not isinstance(bgm, dict):
        raise ValueError("generate background music before composition")
    bgm_file = project_dir / bgm["file"]
    if not bgm_file.exists():
        raise ValueError(f"missing background music: {bgm_file}")
    return bgm


def copy_runtime_assets(project_dir: Path) -> Path:
    source = Path(__file__).resolve().parents[1] / "assets/vendor/gsap.min.js"
    if not source.exists():
        raise ValueError(f"missing bundled GSAP runtime: {source}")
    target = project_dir / "assets/vendor/gsap.min.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return target


def mix_narration_track(
    audio_manifest: dict[str, Any], project_dir: Path, duration: float
) -> Path:
    sample_rate = 24000
    total_samples = int(round(duration * sample_rate))
    mixed = array("i", [0]) * total_samples
    for scene in audio_manifest.get("scenes", []):
        for line in scene.get("lines", []):
            source = project_dir / line["file"]
            with wave.open(str(source), "rb") as input_wav:
                audio_format = (
                    input_wav.getnchannels(),
                    input_wav.getsampwidth(),
                    input_wav.getframerate(),
                    input_wav.getcomptype(),
                )
                if audio_format != (1, 2, sample_rate, "NONE"):
                    raise ValueError(
                        f"narration WAV must be 24 kHz mono 16-bit PCM: {source}"
                    )
                samples = array("h")
                samples.frombytes(input_wav.readframes(input_wav.getnframes()))
                if sys.byteorder != "little":
                    samples.byteswap()
            offset = int(round(float(line["start"]) * sample_rate))
            available = max(0, total_samples - offset)
            for index, sample in enumerate(samples[:available]):
                mixed[offset + index] += sample

    output_samples = array(
        "h", (max(-32768, min(32767, value)) for value in mixed)
    )
    if sys.byteorder != "little":
        output_samples.byteswap()
    output = project_dir / "assets/audio/narration-timeline.wav"
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as output_wav:
        output_wav.setnchannels(1)
        output_wav.setsampwidth(2)
        output_wav.setframerate(sample_rate)
        output_wav.writeframes(output_samples.tobytes())
    return output


def resolve_narration_track(
    audio_manifest: dict[str, Any], project_dir: Path, duration: float
) -> Path:
    master_file = audio_manifest.get("master_audio")
    if not master_file:
        return mix_narration_track(audio_manifest, project_dir, duration)
    source = project_dir / master_file
    if not source.exists():
        raise ValueError(f"missing narration master audio: {source}")
    with wave.open(str(source), "rb") as input_wav:
        audio_format = (
            input_wav.getnchannels(),
            input_wav.getsampwidth(),
            input_wav.getframerate(),
            input_wav.getcomptype(),
        )
        actual_duration = input_wav.getnframes() / input_wav.getframerate()
    if audio_format != (1, 2, 24000, "NONE"):
        raise ValueError(f"narration master must be 24 kHz mono 16-bit PCM: {source}")
    if abs(actual_duration - duration) > 0.02:
        raise ValueError(
            f"narration master duration {actual_duration:.3f}s differs from manifest {duration:.3f}s"
        )
    output = project_dir / "assets/audio/narration-timeline.wav"
    if source.resolve() != output.resolve():
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a HyperFrames comic-drama composition")
    parser.add_argument("story", type=Path)
    parser.add_argument("--project-dir", type=Path)
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
    for key in ("story", "style_and_characters", "scene_images"):
        if story["approvals"][key] != "approved":
            print(f"Error: approvals.{key} must be approved before composition", file=sys.stderr)
            return 1

    project_dir = (args.project_dir or story_path.parent).resolve()
    if not (project_dir / "package.json").exists() or not (project_dir / "hyperframes.json").exists():
        print(
            "Error: scaffold the project first with `npx hyperframes init <project> --non-interactive`",
            file=sys.stderr,
        )
        return 1
    try:
        copy_runtime_assets(project_dir)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    manifest_path = project_dir / "build/audio-manifest.json"
    try:
        audio_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: valid build/audio-manifest.json not found", file=sys.stderr)
        return 1
    if audio_manifest.get("valid") is not True:
        print("Error: audio manifest is not valid", file=sys.stderr)
        return 1
    duration = float(audio_manifest.get("timeline_duration", 0))
    if duration <= 0 or duration > 900:
        print("Error: final timeline duration must be between 0 and 900 seconds", file=sys.stderr)
        return 1
    try:
        bgm = resolve_bgm(story, audio_manifest, project_dir)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    timing_map = {item["id"]: item for item in audio_manifest.get("scenes", [])}
    if len(timing_map) != len(story["scenes"]):
        print("Error: audio manifest scene count does not match story", file=sys.stderr)
        return 1

    scene_markup: list[str] = []
    audio_markup: list[str] = []
    timeline_scenes: list[dict[str, Any]] = []
    for scene_index, scene in enumerate(story["scenes"]):
        timing = timing_map.get(scene["id"])
        if not timing:
            print(f"Error: missing audio timing for {scene['id']}", file=sys.stderr)
            return 1
        image_file = project_dir / f"assets/scenes/{scene['id']}.png"
        if not image_file.exists():
            print(f"Error: missing scene image: {image_file}", file=sys.stderr)
            return 1

        captions: list[str] = []
        timeline_lines: list[dict[str, Any]] = []
        for line_index, line in enumerate(timing["lines"], start=1):
            audio_file = project_dir / line["file"]
            if not audio_file.exists():
                print(f"Error: missing narration audio: {audio_file}", file=sys.stderr)
                return 1
            caption_id = f"caption-{scene['id']}-{line_index:03d}"
            captions.append(
                f'<div id="{caption_id}" class="caption">{html.escape(line["text"])}</div>'
            )
            timeline_lines.append(
                {
                    "id": caption_id,
                    "start": float(line["start"]),
                    "end": float(line["start"]) + float(line["duration"]),
                    "text": line["text"],
                }
            )

        opacity = "1" if scene_index == 0 else "0"
        scene_markup.append(
            "\n".join(
                [
                    f'<div id="scene-{scene["id"]}" class="scene" style="opacity:{opacity};z-index:{scene_index + 1}">',
                    f'  <img id="image-{scene["id"]}" class="scene-image" data-layout-allow-overflow src="assets/scenes/{scene["id"]}.png"',
                    f'    alt="" crossorigin="anonymous" style="object-position:{float(scene["focus"]["x_percent"]):.2f}% {float(scene["focus"]["y_percent"]):.2f}%;transform-origin:{float(scene["focus"]["x_percent"]):.2f}% {float(scene["focus"]["y_percent"]):.2f}%" />',
                    '  <div class="caption-layer" data-layout-allow-occlusion data-layout-allow-overlap>',
                    *[f"    {item}" for item in captions],
                    "  </div>",
                    "</div>",
                ]
            )
        )
        timeline_scenes.append(
            {
                "id": scene["id"],
                "start": float(timing["start"]),
                "duration": float(timing["duration"]),
                "scaleFrom": float(scene["motion"]["scale_from"]),
                "scaleTo": float(scene["motion"]["scale_to"]),
                "lines": timeline_lines,
            }
        )

    try:
        narration_track = resolve_narration_track(audio_manifest, project_dir, duration)
    except (OSError, ValueError, wave.Error) as exc:
        print(f"Error: failed to mix narration timeline: {exc}", file=sys.stderr)
        return 1
    audio_markup.append(
        "\n".join(
            [
                '<audio id="narration-timeline" class="clip"',
                '  data-start="0"',
                f'  data-duration="{duration:.6f}"',
                '  data-track-index="2"',
                f'  src="{html.escape(asset_url(str(narration_track.relative_to(project_dir))))}"',
                '  data-volume="1"></audio>',
            ]
        )
    )

    if bgm is not None:
        audio_markup.append(
            "\n".join(
                [
                    '<audio id="background-music" class="clip"',
                    '  data-start="0"',
                    f'  data-duration="{duration:.6f}"',
                    '  data-track-index="3"',
                    f'  src="{html.escape(asset_url(bgm["file"]))}"',
                    f'  data-volume="{float(bgm["volume"]):.3f}"></audio>',
                ]
            )
        )

    title = html.escape(story["project"]["title"])
    scenes_json = script_json(timeline_scenes)
    html_output = f'''<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {{
        font-family: "PingFang SC";
        src: local("PingFang SC");
      }}
      @font-face {{
        font-family: "Microsoft YaHei";
        src: local("Microsoft YaHei");
      }}
      html, body {{
        margin: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #000000;
        font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
      }}
      #root {{
        position: relative;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #000000;
      }}
      .scene {{
        position: absolute;
        inset: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #000000;
      }}
      .scene-image {{
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        z-index: 1;
        will-change: transform;
      }}
      .caption-layer {{
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 10;
      }}
      .caption {{
        position: absolute;
        left: 0;
        right: 0;
        bottom: 96px;
        width: calc(100% - 240px);
        max-width: 1680px;
        min-height: 72px;
        margin: 0 auto;
        color: #f7f4ec;
        font-size: 54px;
        font-weight: 700;
        line-height: 1.28;
        letter-spacing: 0;
        text-align: center;
        overflow: visible;
        opacity: 0;
        visibility: hidden;
        -webkit-text-stroke: 2px rgba(0, 0, 0, 0.72);
        text-shadow: 0 3px 12px rgba(0, 0, 0, 0.95);
        will-change: transform, opacity;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{duration:.6f}" data-width="1920" data-height="1080">
      {chr(10).join(scene_markup)}
      {chr(10).join(audio_markup)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      var SCENES = {scenes_json};
      document.querySelectorAll(".caption").forEach(function (element) {{
        if (window.__hyperframes && window.__hyperframes.fitTextFontSize) {{
          var result = window.__hyperframes.fitTextFontSize(element.textContent, {{
            maxWidth: 1680,
            baseFontSize: 54,
            minFontSize: 32,
            fontWeight: 700,
            fontFamily: "PingFang SC",
            step: 2
          }});
          element.style.fontSize = result.fontSize + "px";
        }}
      }});

      var tl = gsap.timeline({{ paused: true }});
      SCENES.forEach(function (scene, index) {{
        var sceneElement = document.getElementById("scene-" + scene.id);
        var imageElement = document.getElementById("image-" + scene.id);
        if (index === 0) {{
          tl.from(sceneElement, {{ opacity: 0, duration: 0.45, ease: "power2.out", overwrite: "auto" }}, 0.1);
        }} else {{
          var previous = document.getElementById("scene-" + SCENES[index - 1].id);
          tl.to(previous, {{ opacity: 0, duration: 0.5, ease: "power2.inOut", overwrite: "auto" }}, scene.start);
          tl.fromTo(
            sceneElement,
            {{ opacity: 0 }},
            {{ opacity: 1, duration: 0.5, ease: "power2.inOut", immediateRender: false, overwrite: "auto" }},
            scene.start
          );
        }}
        tl.fromTo(
          imageElement,
          {{ scale: scene.scaleFrom }},
          {{ scale: scene.scaleTo, duration: scene.duration, ease: "none", immediateRender: false }},
          scene.start
        );
        scene.lines.forEach(function (line) {{
          var caption = document.getElementById(line.id);
          tl.set(caption, {{ visibility: "visible", opacity: 0, y: 14 }}, line.start);
          tl.to(caption, {{ opacity: 1, y: 0, duration: 0.25, ease: "power2.out" }}, line.start + 0.02);
          tl.to(caption, {{ opacity: 0, y: -8, duration: 0.12, ease: "power2.in" }}, Math.max(line.start + 0.27, line.end - 0.12));
          tl.set(caption, {{ opacity: 0, visibility: "hidden" }}, line.end);
        }});
      }});

      SCENES.forEach(function (scene) {{
        scene.lines.forEach(function (line) {{
          var caption = document.getElementById(line.id);
          tl.seek(line.end + 0.01);
          var computed = window.getComputedStyle(caption);
          if (computed.opacity !== "0" && computed.visibility !== "hidden") {{
            console.warn("[caption-lint] " + line.id + " remains visible after its sentence");
          }}
        }});
      }});
      tl.seek(0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
    output = project_dir / "index.html"
    output.write_text(html_output, encoding="utf-8")
    print(f"Wrote {output} ({len(story['scenes'])} scenes, {duration:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
