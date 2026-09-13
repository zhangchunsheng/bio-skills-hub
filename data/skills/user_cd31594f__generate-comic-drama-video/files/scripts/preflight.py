#!/usr/bin/env python3
"""Check required comic-drama runtime tools and provider configuration."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


def command_version(command: str, args: list[str]) -> tuple[bool, str]:
    path = shutil.which(command)
    if not path:
        return False, "not found"
    completed = subprocess.run(
        [path, *args], text=True, capture_output=True, check=False, timeout=15
    )
    output = (completed.stdout or completed.stderr).strip().splitlines()
    return completed.returncode == 0, output[0] if output else path


def env_is_set(*names: str) -> bool:
    return any(bool(os.getenv(name)) for name in names)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check comic-drama runtime readiness")
    parser.add_argument(
        "--image-provider", choices=("external", "none"), default="external"
    )
    parser.add_argument(
        "--tts-provider",
        choices=("xiaomi_mimo", "local_kokoro", "none"),
        default="xiaomi_mimo",
    )
    parser.add_argument("--bgm", action="store_true", help="Require local MusicGen")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []

    def add(name: str, required: bool, ok: bool, detail: str) -> None:
        checks.append({"name": name, "required": required, "ok": ok, "detail": detail})

    for command, version_args in (
        ("python3", ["--version"]),
        ("node", ["--version"]),
        ("npx", ["--version"]),
        ("ffmpeg", ["-version"]),
        ("ffprobe", ["-version"]),
    ):
        ok, detail = command_version(command, version_args)
        if command == "node" and ok:
            match = re.search(r"v?(\d+)", detail)
            ok = bool(match and int(match.group(1)) >= 22)
            if not ok:
                detail = f"Node.js 22+ required; found {detail}"
        add(command, True, ok, detail)

    skill_root = Path(__file__).resolve().parents[1]
    image_cli = (
        Path(os.getenv("CODEX_HOME", str(Path.home() / ".codex")))
        / "skills/.system/imagegen/scripts/image_gen.py"
    )
    if args.image_provider == "external":
        add("imagegen_cli", True, image_cli.exists(), str(image_cli))
        add(
            "image_api_key",
            True,
            env_is_set("COMIC_IMAGE_API_KEY", "OPENAI_API_KEY"),
            "COMIC_IMAGE_API_KEY or OPENAI_API_KEY",
        )
        add(
            "image_base_url",
            True,
            env_is_set("COMIC_IMAGE_BASE_URL", "OPENAI_BASE_URL"),
            "COMIC_IMAGE_BASE_URL or OPENAI_BASE_URL",
        )
        model = os.getenv("COMIC_IMAGE_MODEL", "gpt-image-2")
        add("image_model", True, model == "gpt-image-2", model)

    if args.tts_provider == "xiaomi_mimo":
        add(
            "mimo_api_key",
            True,
            env_is_set("COMIC_TTS_API_KEY", "MIMO_API_KEY"),
            "COMIC_TTS_API_KEY or MIMO_API_KEY",
        )
        add(
            "mimo_base_url",
            False,
            True,
            os.getenv("COMIC_TTS_BASE_URL")
            or os.getenv("MIMO_BASE_URL")
            or "https://api.xiaomimimo.com/v1",
        )
    elif args.tts_provider == "local_kokoro":
        for package in ("kokoro_onnx", "soundfile"):
            add(package, True, importlib.util.find_spec(package) is not None, package)

    if args.bgm:
        for package in ("transformers", "torch", "soundfile", "numpy"):
            add(package, True, importlib.util.find_spec(package) is not None, package)
    else:
        add("local_musicgen", False, True, "disabled; no Torch/model download required")

    add("skill_root", True, skill_root.exists(), str(skill_root))
    failures = [item for item in checks if item["required"] and not item["ok"]]
    report = {
        "ready": not failures,
        "checks": checks,
        "next": "run `npx hyperframes doctor` after project scaffolding",
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in checks:
            marker = "OK" if item["ok"] else "MISSING"
            requirement = "required" if item["required"] else "optional"
            print(f"[{marker}] {item['name']} ({requirement}): {item['detail']}")
        print(report["next"])
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
