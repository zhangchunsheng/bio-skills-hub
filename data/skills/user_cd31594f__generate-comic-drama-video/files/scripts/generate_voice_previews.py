#!/usr/bin/env python3
"""Generate comparable Xiaomi MiMo preset and voice-design previews."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import sys
from typing import Any

from generate_audio import (
    normalize_api_base_url,
    normalize_mimo_wav,
    probe_duration,
    request_mimo_wav,
)


DEFAULT_MIMO_BASE_URL = "https://api.xiaomimimo.com/v1"
DEFAULT_SAMPLE_TEXT = (
    "二十五岁那年，你回到熟悉的县城。"
    "日子没有突然变好，却终于可以慢慢过了。"
)

DEFAULT_PROFILES: list[dict[str, str]] = [
    {
        "id": "01-preset-bingtang",
        "name": "预置-冰糖",
        "kind": "preset",
        "model": "mimo-v2.5-tts",
        "voice": "冰糖",
        "direction": "中文女性旁白，克制、自然、有故事感，不使用播音腔。",
    },
    {
        "id": "02-preset-moli",
        "name": "预置-茉莉",
        "kind": "preset",
        "model": "mimo-v2.5-tts",
        "voice": "茉莉",
        "direction": "中文女性旁白，克制、自然、有故事感，不使用播音腔。",
    },
    {
        "id": "03-preset-suda",
        "name": "预置-苏打",
        "kind": "preset",
        "model": "mimo-v2.5-tts",
        "voice": "苏打",
        "direction": "中文男性旁白，磁性、有故事感，克制而松弛，不说教。",
    },
    {
        "id": "04-preset-baihua",
        "name": "预置-白桦",
        "kind": "preset",
        "model": "mimo-v2.5-tts",
        "voice": "白桦",
        "direction": "中文男性旁白，磁性、有故事感，克制而松弛，不说教。",
    },
    {
        "id": "05-custom-deep-mature",
        "name": "自定义-低沉成熟",
        "kind": "voice_design",
        "model": "mimo-v2.5-tts-voicedesign",
        "direction": (
            "请设计一位40岁左右的中文男性声音。声线低沉、醇厚、磁性，带一点岁月感，"
            "像经历过生活后平静回望自己的人生。咬字自然，不使用播音腔，不刻意煽情，"
            "表达克制、沉稳、有故事感。"
        ),
    },
    {
        "id": "06-custom-magnetic-relaxed",
        "name": "自定义-磁性松弛",
        "kind": "voice_design",
        "model": "mimo-v2.5-tts-voicedesign",
        "direction": (
            "请设计一位35至45岁的中文男性声音。音色磁性、温暖、松弛，略带沙哑质感，"
            "像夜晚坐在老朋友身边讲自己的往事。语气轻松自然，有阅历但不沧桑，"
            "不要广告腔、主持腔或夸张表演。"
        ),
    },
    {
        "id": "07-custom-documentary",
        "name": "自定义-克制纪实",
        "kind": "voice_design",
        "model": "mimo-v2.5-tts-voicedesign",
        "direction": (
            "请设计一位38岁左右的中文男性纪实旁白声音。中低音，清晰耐听，声音真实、"
            "朴素、可信，像本人直接讲述生活经历。情绪内收，停顿自然，不说教、不煽情，"
            "不使用新闻播音腔。"
        ),
    },
]


def preview_payload(profile: dict[str, str], text: str) -> dict[str, Any]:
    audio: dict[str, Any] = {"format": "wav"}
    if profile["kind"] == "preset":
        audio["voice"] = profile["voice"]
    else:
        # Preview optimization is useful only while choosing a designed voice.
        audio["optimize_text_preview"] = True
    return {
        "model": profile["model"],
        "messages": [
            {"role": "user", "content": profile["direction"]},
            {"role": "assistant", "content": text},
        ],
        "audio": audio,
    }


def load_profiles(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return DEFAULT_PROFILES
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("profiles JSON must be a non-empty array")
    required = {"id", "name", "kind", "model", "direction"}
    for index, profile in enumerate(data):
        if not isinstance(profile, dict) or not required.issubset(profile):
            raise ValueError(f"profiles[{index}] is missing required fields")
        if profile["kind"] not in {"preset", "voice_design"}:
            raise ValueError(f"profiles[{index}].kind must be preset or voice_design")
        if profile["kind"] == "preset" and not profile.get("voice"):
            raise ValueError(f"profiles[{index}].voice is required for preset")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate MiMo voice comparison previews")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--text", default=DEFAULT_SAMPLE_TEXT)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--concurrency", type=int, default=7)
    parser.add_argument("--profiles", type=Path, help="Optional JSON profile array")
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not 0.7 <= args.speed <= 2.0:
        print("Error: speed must be between 0.7 and 2.0", file=sys.stderr)
        return 1
    if not 1 <= args.concurrency <= 10:
        print("Error: concurrency must be between 1 and 10", file=sys.stderr)
        return 1
    if not 1 <= args.attempts <= 3:
        print("Error: attempts must be between 1 and 3", file=sys.stderr)
        return 1
    try:
        profiles = load_profiles(args.profiles)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(
            json.dumps(
                {
                    "sample_text": args.text,
                    "speed": args.speed,
                    "concurrency": min(args.concurrency, len(profiles)),
                    "profiles": [
                        {
                            "id": profile["id"],
                            "name": profile["name"],
                            "model": profile["model"],
                            "audio": preview_payload(profile, args.text)["audio"],
                        }
                        for profile in profiles
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    api_key = os.getenv("COMIC_TTS_API_KEY") or os.getenv("MIMO_API_KEY") or ""
    if not api_key:
        print("Error: set COMIC_TTS_API_KEY or MIMO_API_KEY", file=sys.stderr)
        return 1
    raw_base_url = (
        os.getenv("COMIC_TTS_BASE_URL")
        or os.getenv("MIMO_BASE_URL")
        or DEFAULT_MIMO_BASE_URL
    )
    base_url = normalize_api_base_url(raw_base_url)
    output_dir = args.project_dir.resolve() / "assets/audio/voice-previews"
    output_dir.mkdir(parents=True, exist_ok=True)

    def generate(profile: dict[str, str]) -> dict[str, Any]:
        output = output_dir / f"{profile['id']}.wav"
        wav = request_mimo_wav(
            preview_payload(profile, args.text), base_url, api_key, args.attempts
        )
        normalize_mimo_wav(wav, output, args.speed, ["ffmpeg"])
        return {
            **profile,
            "file": output.name,
            "duration_seconds": round(probe_duration(output, ["ffprobe"]), 3),
            "speed": args.speed,
            "status": "complete",
        }

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(args.concurrency, len(profiles))) as executor:
        future_map = {executor.submit(generate, profile): profile for profile in profiles}
        for future in as_completed(future_map):
            profile = future_map[future]
            try:
                result = future.result()
                print(f"Complete: {result['name']} ({result['duration_seconds']}s)")
                results.append(result)
            except Exception as exc:  # noqa: BLE001
                detail = str(exc).replace(api_key, "[redacted]")
                print(f"Failed: {profile['name']}: {detail}", file=sys.stderr)
                results.append({**profile, "status": "failed", "error": detail})

    results.sort(key=lambda item: str(item["id"]))
    manifest = {"sample_text": args.text, "speed": args.speed, "previews": results}
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    failures = [item for item in results if item["status"] != "complete"]
    print(f"Generated {len(results) - len(failures)}/{len(results)} previews in {output_dir}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
