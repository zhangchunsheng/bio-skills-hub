#!/usr/bin/env python3
"""Generate resumable style, character, and scene images through imagegen CLI."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Optional
from urllib import parse as urllib_parse

from validate_story import load_story, validate_story


DEFAULT_MODEL = "gpt-image-2"
DEFAULT_QUALITY = "high"
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


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def resolve_project_path(story_path: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = story_path.parent / path
    return path.resolve()


def normalize_openai_base_url(raw: str) -> str:
    value = raw.strip().rstrip("/")
    parsed = urllib_parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("image base URL must be an absolute http(s) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("image base URL cannot contain credentials, query parameters, or fragments")
    path = parsed.path.rstrip("/")
    if not path.endswith("/v1"):
        path += "/v1"
    return urllib_parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def clear_proxy_environment(env: dict[str, str]) -> None:
    for key in PROXY_ENV_VARS:
        env.pop(key, None)


def inspect_png_output(path: Path, requested_size: str) -> tuple[str, Optional[str]]:
    if not path.exists() or path.stat().st_size <= 24:
        raise ValueError("image output is missing or empty")
    with path.open("rb") as handle:
        header = handle.read(24)
        handle.seek(-12, os.SEEK_END)
        trailer = handle.read(12)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("image output is not a valid PNG")
    if trailer[:8] != b"\x00\x00\x00\x00IEND":
        raise ValueError("image output is incomplete; PNG IEND chunk is missing")
    width, height = struct.unpack(">II", header[16:24])
    requested_width, requested_height = (int(value) for value in requested_size.split("x", 1))
    actual_ratio = width / height
    requested_ratio = requested_width / requested_height
    actual_size = f"{width}x{height}"
    warning = None
    if abs(actual_ratio - requested_ratio) / requested_ratio > 0.01:
        warning = (
            f"provider returned {actual_size}; requested {requested_size}; "
            "aspect ratio differs and will be cover-cropped during composition"
        )
    elif actual_size != requested_size:
        warning = f"provider returned {actual_size}; requested {requested_size}"
    return actual_size, warning


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def file_signature(path: Optional[Path]) -> Optional[tuple[int, int]]:
    if path is None or not path.exists():
        return None
    stat = path.stat()
    return stat.st_mtime_ns, stat.st_size


def job_fingerprint(job: dict[str, Any], model: str, size: str, quality: str) -> str:
    references = []
    for reference in job["references"]:
        path = Path(reference)
        references.append(
            {
                "path": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    payload = {
        "model": model,
        "size": size,
        "quality": quality,
        "prompt": job["prompt"],
        "references": references,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def image_cli_path() -> Path:
    codex_home = Path(os.getenv("CODEX_HOME", Path.home() / ".codex"))
    path = codex_home / "skills/.system/imagegen/scripts/image_gen.py"
    if not path.exists():
        raise RuntimeError(f"imagegen CLI not found: {path}")
    return path


def build_prompt(story: dict[str, Any], primary: str, references: list[str]) -> str:
    style = story["visual_style"]
    reference_text = "; ".join(references) if references else "none"
    return "\n".join(
        [
            "Use case: illustration-story",
            "Asset type: 16:9 full-screen comic-drama frame",
            f"Primary request: {primary}",
            f"Input images: {reference_text}",
            f"Style/medium: {style['style_prompt']}",
            f"Composition/framing: {style['composition_prompt']}",
            f"Color palette: {style['palette_prompt']}",
            "Constraints: preserve recurring character identity, face, hair, body proportions, and wardrobe; keep the focal subject safe for 16:9 cover cropping",
            f"Avoid: {style['avoid']}; no text, subtitles, speech bubbles, watermark, comic panels, borders, or collage",
        ]
    )


def run_cli(
    command: list[str],
    env: dict[str, str],
    attempts: int,
    dry_run: bool,
    output_path: Optional[Path] = None,
    requested_size: Optional[str] = None,
    status_callback: Optional[Callable[[str, int, float], None]] = None,
    request_timeout_seconds: float = 600.0,
) -> tuple[bool, str]:
    max_attempts = 1 if dry_run else attempts
    output = ""
    for attempt in range(1, max_attempts + 1):
        if dry_run:
            completed = subprocess.run(command, env=env, text=True, capture_output=True, check=False)
            output = (completed.stdout + completed.stderr).strip()
            return completed.returncode == 0, output

        initial_signature = file_signature(output_path)
        started = time.monotonic()
        if status_callback:
            status_callback("submitted", attempt, 0.0)
        process = subprocess.Popen(
            command,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        next_heartbeat = 0.0
        file_ready = False
        timed_out = False
        while process.poll() is None:
            elapsed = time.monotonic() - started
            if elapsed >= request_timeout_seconds:
                timed_out = True
                if status_callback:
                    status_callback("timed_out", attempt, elapsed)
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
                break
            if elapsed >= next_heartbeat:
                if status_callback:
                    status_callback("waiting_response", attempt, elapsed)
                next_heartbeat = elapsed + 5.0
            current_signature = file_signature(output_path)
            if (
                output_path is not None
                and requested_size is not None
                and current_signature is not None
                and current_signature != initial_signature
            ):
                try:
                    inspect_png_output(output_path, requested_size)
                    file_ready = True
                except ValueError:
                    file_ready = False
            if file_ready:
                if status_callback:
                    status_callback("file_ready", attempt, elapsed)
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=2)
                break
            time.sleep(0.5)

        stdout, _ = process.communicate()
        output = (stdout or "").strip()
        validation_error = ""
        valid_file = file_ready
        if output_path is not None and requested_size is not None and not valid_file:
            try:
                inspect_png_output(output_path, requested_size)
                valid_file = True
            except ValueError as exc:
                validation_error = str(exc)
        elif output_path is None or requested_size is None:
            valid_file = process.returncode == 0
        if valid_file:
            return True, output
        if validation_error:
            output = f"{output}\n{validation_error}".strip()
            try:
                output_path.unlink(missing_ok=True)
            except OSError as exc:
                output = f"{output}\nfailed to remove invalid output: {exc}".strip()
        if timed_out:
            timeout_detail = (
                f"image request timed out after {request_timeout_seconds:.0f}s "
                "without a complete local PNG"
            )
            output = f"{output}\n{timeout_detail}".strip()
        if attempt < max_attempts:
            if status_callback:
                status_callback("retrying", attempt, time.monotonic() - started)
            time.sleep(min(30, 2 ** attempt))
    return False, output


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate comic-drama images with checkpoints")
    parser.add_argument("story", type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--phase", required=True, choices=("anchor", "characters", "scenes"))
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--request-timeout-seconds", type=float, default=600.0)
    parser.add_argument("--quality", choices=("low", "medium", "high", "auto"), default=DEFAULT_QUALITY)
    parser.add_argument(
        "--adopt-existing",
        action="store_true",
        help="Validate and checkpoint existing PNG outputs that predate their manifest entries",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--combined-visual-review",
        action="store_true",
        help="Allow scene generation before the single combined visual approval",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
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
    if story["approvals"]["story"] != "approved" and not args.dry_run:
        print("Error: approve the story before generating images", file=sys.stderr)
        return 1
    if (
        args.phase == "scenes"
        and story["approvals"]["style_and_characters"] != "approved"
        and not args.combined_visual_review
        and not args.dry_run
    ):
        print("Error: approve style and character sheets before generating scene images", file=sys.stderr)
        return 1
    if not 1 <= args.concurrency <= 10:
        print("Error: concurrency must be between 1 and 10", file=sys.stderr)
        return 1
    if not 1 <= args.attempts <= 3:
        print("Error: attempts must be between 1 and 3", file=sys.stderr)
        return 1
    if not 60 <= args.request_timeout_seconds <= 3600:
        print("Error: request timeout must be between 60 and 3600 seconds", file=sys.stderr)
        return 1

    project_dir = (args.project_dir or story_path.parent).resolve()
    model = os.getenv("COMIC_IMAGE_MODEL", DEFAULT_MODEL)
    if model != DEFAULT_MODEL:
        print("Error: this skill is locked to gpt-image-2", file=sys.stderr)
        return 1
    env = os.environ.copy()
    clear_proxy_environment(env)
    if os.getenv("COMIC_IMAGE_API_KEY"):
        env["OPENAI_API_KEY"] = os.environ["COMIC_IMAGE_API_KEY"]
    raw_base_url = os.getenv("COMIC_IMAGE_BASE_URL") or env.get("OPENAI_BASE_URL")
    if raw_base_url:
        try:
            env["OPENAI_BASE_URL"] = normalize_openai_base_url(raw_base_url)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    if not args.dry_run:
        if not env.get("OPENAI_API_KEY"):
            print("Error: set COMIC_IMAGE_API_KEY or OPENAI_API_KEY", file=sys.stderr)
            return 1
        if not env.get("OPENAI_BASE_URL"):
            print("Error: set COMIC_IMAGE_BASE_URL or OPENAI_BASE_URL", file=sys.stderr)
            return 1

    cli = image_cli_path()
    size = story["project"]["image_size"]
    style = story["visual_style"]
    anchor_output = project_dir / "assets/references/style-anchor.png"
    if style["mode"] == "user_reference":
        style_reference = resolve_project_path(story_path, style["reference_image"])
    else:
        style_reference = anchor_output

    python = sys.executable
    jobs: list[dict[str, Any]] = []
    if args.phase == "anchor":
        if style["mode"] != "generated_anchor":
            print("Error: anchor phase is only valid for generated_anchor mode", file=sys.stderr)
            return 1
        prompt = build_prompt(story, style["anchor_prompt"], [])
        jobs.append({"key": "anchor", "output": anchor_output, "prompt": prompt, "references": []})
    elif args.phase == "characters":
        if not style_reference.exists():
            print(f"Error: style reference not found: {style_reference}", file=sys.stderr)
            return 1
        for character in story["characters"]:
            primary = (
                f"Character reference sheet for {character['name']}. "
                f"Appearance: {character['appearance']}. Wardrobe: {character['wardrobe']}. "
                f"Personality cues: {character['personality']}. {character['sheet_prompt']}"
            )
            jobs.append(
                {
                    "key": f"character:{character['id']}",
                    "output": project_dir / f"assets/characters/{character['id']}.png",
                    "prompt": build_prompt(story, primary, ["Image 1: fixed style, composition, and palette reference"]),
                    "references": [style_reference],
                }
            )
    else:
        character_map = {item["id"]: item for item in story["characters"]}
        for scene in story["scenes"]:
            references = [style_reference]
            labels = ["Image 1: fixed style, composition, and palette reference"]
            for index, character_id in enumerate(scene["character_ids"], start=2):
                character_path = project_dir / f"assets/characters/{character_id}.png"
                if not character_path.exists():
                    print(f"Error: character sheet not found: {character_path}", file=sys.stderr)
                    return 1
                references.append(character_path)
                labels.append(f"Image {index}: identity reference for {character_map[character_id]['name']}")
            if not style_reference.exists():
                print(f"Error: style reference not found: {style_reference}", file=sys.stderr)
                return 1
            jobs.append(
                {
                    "key": f"scene:{scene['id']}",
                    "output": project_dir / f"assets/scenes/{scene['id']}.png",
                    "prompt": build_prompt(story, scene["image_prompt"], labels),
                    "references": references,
                }
            )

    if args.limit is not None:
        jobs = jobs[: max(0, args.limit)]

    manifest_path = project_dir / "build/image-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        manifest = {"jobs": {}}
    if not isinstance(manifest.get("jobs"), dict):
        manifest["jobs"] = {}
    manifest["model"] = model
    manifest["base_url"] = env.get("OPENAI_BASE_URL")
    lock = threading.Lock()

    def checkpoint(
        job: dict[str, Any], status: str, attempt: int = 0, elapsed: float = 0.0
    ) -> None:
        with lock:
            entry = manifest["jobs"].setdefault(job["key"], {})
            entry.update(
                {
                    "status": status,
                    "output": str(job["output"].relative_to(project_dir)),
                    "attempt": attempt,
                    "elapsed_seconds": round(elapsed, 1),
                    "updated_at": utc_timestamp(),
                    "fingerprint": job_fingerprint(job, model, size, args.quality),
                }
            )
            atomic_write_json(manifest_path, manifest)

    def execute(job: dict[str, Any]) -> tuple[str, bool, str]:
        output_path: Path = job["output"]
        fingerprint = job_fingerprint(job, model, size, args.quality)
        previous_job = manifest["jobs"].get(job["key"], {})
        cache_matches = previous_job.get("fingerprint") == fingerprint
        if (
            output_path.exists()
            and output_path.stat().st_size > 0
            and (cache_matches or args.adopt_existing)
            and not args.force
            and not args.dry_run
        ):
            try:
                _, warning = inspect_png_output(output_path, size)
                detail = f"skipped existing {output_path}"
                if warning:
                    detail += f"; warning: {warning}"
                return job["key"], True, detail
            except ValueError:
                cache_matches = False
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mode = "edit" if job["references"] else "generate"
        command = [
            python,
            str(cli),
            mode,
            "--model",
            model,
            "--prompt",
            job["prompt"],
            "--size",
            size,
            "--quality",
            args.quality,
            "--output-format",
            "png",
            "--out",
            str(output_path),
            "--no-augment",
        ]
        for reference in job["references"]:
            command.extend(["--image", str(reference)])
        if args.force or (output_path.exists() and not cache_matches):
            command.append("--force")
        if args.dry_run:
            command.append("--dry-run")
        ok, detail = run_cli(
            command,
            env,
            args.attempts,
            args.dry_run,
            output_path=output_path,
            requested_size=size,
            status_callback=lambda status, attempt, elapsed: checkpoint(
                job, status, attempt, elapsed
            ),
            request_timeout_seconds=args.request_timeout_seconds,
        )
        api_key = env.get("OPENAI_API_KEY", "")
        if api_key:
            detail = detail.replace(api_key, "[redacted]")
        if ok and not args.dry_run:
            try:
                _, warning = inspect_png_output(output_path, size)
                if warning:
                    detail = f"{detail}\nWarning: {warning}".strip()
            except ValueError as exc:
                ok = False
                detail = str(exc)
        return job["key"], ok, detail

    failures = 0
    if not args.dry_run:
        for job in jobs:
            previous = manifest["jobs"].get(job["key"], {})
            if previous.get("status") != "complete" or not job["output"].exists():
                checkpoint(job, "queued")
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(execute, job): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                key, ok, detail = future.result()
            except Exception as exc:
                key, ok, detail = job["key"], False, str(exc)
            print(f"[{key}] {'ok' if ok else 'failed'}")
            if args.dry_run and detail:
                print(detail)
            if not ok:
                failures += 1
                print(detail, file=sys.stderr)
            if not args.dry_run:
                with lock:
                    actual_size = None
                    size_warning = None
                    if ok:
                        actual_size, size_warning = inspect_png_output(job["output"], size)
                    manifest["jobs"][key] = {
                        "status": "complete" if ok else "failed",
                        "output": str(job["output"].relative_to(project_dir)),
                        "requested_size": size,
                        "actual_size": actual_size,
                        "warning": size_warning,
                        "attempt_limit": args.attempts,
                        "attempt": manifest["jobs"].get(key, {}).get("attempt"),
                        "elapsed_seconds": manifest["jobs"].get(key, {}).get("elapsed_seconds"),
                        "updated_at": utc_timestamp(),
                        "error": None if ok else detail[-2000:],
                        "fingerprint": job_fingerprint(job, model, size, args.quality),
                    }
                    atomic_write_json(manifest_path, manifest)

    print(f"Processed {len(jobs)} image job(s); failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
