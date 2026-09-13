#!/usr/bin/env python3
"""Generate anchor, characters, and scenes for one combined visual review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate all comic-drama visual assets")
    parser.add_argument("story", type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--request-timeout-seconds", type=float, default=600.0)
    parser.add_argument("--quality", choices=("low", "medium", "high", "auto"), default="high")
    parser.add_argument("--adopt-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.concurrency <= 10:
        print("Error: concurrency must be between 1 and 10", file=sys.stderr)
        return 1
    story_path = args.story.resolve()
    try:
        story = json.loads(story_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    project_dir = (args.project_dir or story_path.parent).resolve()
    generator = Path(__file__).with_name("generate_images.py")
    phases = [] if story.get("visual_style", {}).get("mode") == "user_reference" else ["anchor"]
    phases += ["characters", "scenes"]
    if args.dry_run:
        print(
            json.dumps(
                {
                    "story": str(story_path),
                    "project_dir": str(project_dir),
                    "phases": phases,
                    "concurrency": args.concurrency,
                    "attempts": args.attempts,
                    "request_timeout_seconds": args.request_timeout_seconds,
                    "quality": args.quality,
                    "note": "Run phases in order; later phases consume outputs from earlier phases.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    for phase in phases:
        command = [
            sys.executable,
            str(generator),
            str(story_path),
            "--project-dir",
            str(project_dir),
            "--phase",
            phase,
            "--concurrency",
            str(args.concurrency),
            "--attempts",
            str(args.attempts),
            "--request-timeout-seconds",
            str(args.request_timeout_seconds),
            "--quality",
            args.quality,
        ]
        if phase == "scenes":
            command.append("--combined-visual-review")
        if args.adopt_existing:
            command.append("--adopt-existing")
        print(f"Visual phase: {phase}: {shlex.join(command)}")
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return completed.returncode
    print("Visual assets are ready for one combined style, character, and scene review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
