#!/usr/bin/env python3
"""Validate a comic-drama story plan with no third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


MAX_SCENES = 600
MAX_DURATION_SECONDS = 900.0
DRAFT_WARNING_SECONDS = 840.0
TRANSITION_SECONDS = 0.5
SCENE_PADDING_SECONDS = 0.8

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_SCENE_RE = re.compile(r"^scene_[0-9]{3,4}$")
_SIZE_RE = re.compile(r"^([1-9][0-9]*)x([1-9][0-9]*)$")
_CJK_RE = re.compile(r"[\u3400-\u9fff]")
_LATIN_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")
_NARRATOR_MODELS = {
    "local_kokoro": "kokoro-82m",
    "xiaomi_mimo": "mimo-v2.5-tts",
}
_MIMO_MODELS = {"mimo-v2.5-tts", "mimo-v2.5-tts-voicedesign"}
_MIMO_PRESET_VOICES = {"mimo_default", "冰糖", "茉莉", "苏打", "白桦", "Mia", "Chloe", "Milo", "Dean"}


def load_story(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"story file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError("story root must be an object")
    return data


def estimate_text_seconds(text: str, speed: float) -> float:
    cjk_count = len(_CJK_RE.findall(text))
    latin_words = len(_LATIN_WORD_RE.findall(_CJK_RE.sub(" ", text)))
    punctuation = len(re.findall(r"[，。！？；：,.!?;:]", text))
    spoken = (cjk_count / 4.2) + (latin_words / 2.5)
    pause = min(2.5, punctuation * 0.14)
    return max(0.8, (spoken + pause) / speed)


def validate_story(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    def require_object(parent: dict[str, Any], key: str) -> dict[str, Any]:
        value = parent.get(key)
        if not isinstance(value, dict):
            errors.append(f"{key} must be an object")
            return {}
        return value

    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")

    valid_stages = {
        "story_review",
        "visual_review",
        "style_and_character_review",
        "scene_image_review",
        "audio_generation",
        "composition",
        "complete",
    }
    stage = data.get("stage")
    if stage not in valid_stages:
        errors.append(f"stage must be one of {sorted(valid_stages)}")

    project = require_object(data, "project")
    for key in ("title", "theme", "language"):
        if not isinstance(project.get(key), str) or not project[key].strip():
            errors.append(f"project.{key} must be a non-empty string")
    expected_project = {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "max_duration_seconds": 900,
        "max_scenes": 600,
    }
    for key, expected in expected_project.items():
        if project.get(key) != expected:
            errors.append(f"project.{key} must be {expected}")
    caption_max = project.get("caption_max_characters", 80)
    if not isinstance(caption_max, int) or not 8 <= caption_max <= 80:
        errors.append("project.caption_max_characters must be an integer between 8 and 80")
        caption_max = 80

    size = project.get("image_size")
    match = _SIZE_RE.match(size) if isinstance(size, str) else None
    if not match:
        errors.append("project.image_size must use WIDTHxHEIGHT syntax")
    else:
        width, height = int(match.group(1)), int(match.group(2))
        pixels = width * height
        if width % 16 or height % 16:
            errors.append("project.image_size edges must be multiples of 16 for gpt-image-2")
        if max(width, height) > 3840 or max(width, height) / min(width, height) > 3:
            errors.append("project.image_size exceeds gpt-image-2 edge or aspect-ratio limits")
        if pixels < 655_360 or pixels > 8_294_400:
            errors.append("project.image_size exceeds gpt-image-2 pixel-count limits")

    style = require_object(data, "visual_style")
    if style.get("mode") not in {"user_reference", "generated_anchor"}:
        errors.append("visual_style.mode must be user_reference or generated_anchor")
    for key in ("style_prompt", "composition_prompt", "palette_prompt", "avoid"):
        if not isinstance(style.get(key), str) or not style[key].strip():
            errors.append(f"visual_style.{key} must be a non-empty string")
    if style.get("mode") == "user_reference" and not style.get("reference_image"):
        errors.append("visual_style.reference_image is required for user_reference mode")
    if style.get("mode") == "generated_anchor" and not style.get("anchor_prompt"):
        errors.append("visual_style.anchor_prompt is required for generated_anchor mode")

    narrator = require_object(data, "narrator")
    for key in ("voice", "tone", "language"):
        if not isinstance(narrator.get(key), str) or not narrator[key].strip():
            errors.append(f"narrator.{key} must be specified for each run")
    provider = narrator.get("provider", "local_kokoro")
    if provider not in _NARRATOR_MODELS:
        errors.append(f"narrator.provider must be one of {sorted(_NARRATOR_MODELS)}")
    else:
        model = narrator.get("model", _NARRATOR_MODELS[provider])
        if provider == "xiaomi_mimo" and model not in _MIMO_MODELS:
            errors.append(f"narrator.model must be one of {sorted(_MIMO_MODELS)} for xiaomi_mimo")
        elif provider != "xiaomi_mimo" and model != _NARRATOR_MODELS[provider]:
            errors.append(f"narrator.model must be {_NARRATOR_MODELS[provider]} for {provider}")
        if (
            provider == "xiaomi_mimo"
            and model == "mimo-v2.5-tts"
            and narrator.get("voice") not in _MIMO_PRESET_VOICES
        ):
            errors.append("narrator.voice must be a documented MiMo v2.5 preset voice")
        if provider == "xiaomi_mimo" and model == "mimo-v2.5-tts-voicedesign":
            voice_design = narrator.get("voice_design")
            if not isinstance(voice_design, str) or not voice_design.strip():
                errors.append("narrator.voice_design is required for MiMo voice design")
    speed = narrator.get("speed")
    if not isinstance(speed, (int, float)) or not 0.7 <= float(speed) <= 2.0:
        errors.append("narrator.speed must be between 0.7 and 2.0")
        speed = 1.0
    speed = float(speed)

    characters = data.get("characters")
    if not isinstance(characters, list) or not characters:
        errors.append("characters must be a non-empty array")
        characters = []
    if len(characters) > 30:
        errors.append("characters cannot contain more than 30 entries")
    character_ids: set[str] = set()
    for index, character in enumerate(characters):
        prefix = f"characters[{index}]"
        if not isinstance(character, dict):
            errors.append(f"{prefix} must be an object")
            continue
        character_id = character.get("id")
        if not isinstance(character_id, str) or not _ID_RE.match(character_id):
            errors.append(f"{prefix}.id must use lowercase letters, numbers, _ or -")
        elif character_id in character_ids:
            errors.append(f"duplicate character id: {character_id}")
        else:
            character_ids.add(character_id)
        for key in ("name", "appearance", "wardrobe", "personality", "sheet_prompt"):
            if not isinstance(character.get(key), str) or not character[key].strip():
                errors.append(f"{prefix}.{key} must be a non-empty string")

    audio = require_object(data, "audio")
    if audio.get("sfx_enabled") is not False:
        errors.append("audio.sfx_enabled must be false")
    gap = audio.get("sentence_gap_seconds")
    if not isinstance(gap, (int, float)) or not 0 <= float(gap) <= 2:
        errors.append("audio.sentence_gap_seconds must be between 0 and 2")
        gap = 0.25
    gap = float(gap)
    scene_gap = audio.get("scene_gap_seconds", 0.35)
    if not isinstance(scene_gap, (int, float)) or not 0 <= float(scene_gap) <= 2:
        errors.append("audio.scene_gap_seconds must be between 0 and 2 when provided")
    bgm = audio.get("bgm")
    if not isinstance(bgm, dict):
        errors.append("audio.bgm must be an object")
    else:
        enabled = bgm.get("enabled")
        if not isinstance(enabled, bool):
            errors.append("audio.bgm.enabled must be true or false")
        elif enabled:
            if bgm.get("mode") != "local_musicgen":
                errors.append("audio.bgm.mode must be local_musicgen when enabled")
            prompts = bgm.get("prompts")
            if not isinstance(prompts, list) or not 1 <= len(prompts) <= 6:
                errors.append("audio.bgm.prompts must contain 1-6 prompts")
            elif any(not isinstance(item, str) or not item.strip() for item in prompts):
                errors.append("audio.bgm.prompts entries must be non-empty strings")
            volume = bgm.get("volume")
            if not isinstance(volume, (int, float)) or not 0.01 <= float(volume) <= 0.35:
                errors.append("audio.bgm.volume must be between 0.01 and 0.35")

    approvals = require_object(data, "approvals")
    approval_values = {"pending", "approved", "rejected"}
    for key in ("story", "style_and_characters", "scene_images"):
        if approvals.get(key) not in approval_values:
            errors.append(f"approvals.{key} must be pending, approved, or rejected")

    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("scenes must be a non-empty array")
        scenes = []
    if len(scenes) > MAX_SCENES:
        errors.append(f"scenes contains {len(scenes)} items; maximum is {MAX_SCENES}")

    scene_ids: set[str] = set()
    scene_estimates: list[dict[str, Any]] = []
    for index, scene in enumerate(scenes):
        prefix = f"scenes[{index}]"
        if not isinstance(scene, dict):
            errors.append(f"{prefix} must be an object")
            continue
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not _SCENE_RE.match(scene_id):
            errors.append(f"{prefix}.id must match scene_001 through scene_9999")
        elif scene_id in scene_ids:
            errors.append(f"duplicate scene id: {scene_id}")
        else:
            scene_ids.add(scene_id)
        for key in ("name", "image_prompt"):
            if not isinstance(scene.get(key), str) or not scene[key].strip():
                errors.append(f"{prefix}.{key} must be a non-empty string")
        refs = scene.get("character_ids")
        if not isinstance(refs, list) or len(refs) > 12:
            errors.append(f"{prefix}.character_ids must be an array with at most 12 entries")
            refs = []
        for character_id in refs:
            if character_id not in character_ids:
                errors.append(f"{prefix} references unknown character id: {character_id}")

        narrations = scene.get("narrations")
        if not isinstance(narrations, list) or not narrations:
            errors.append(f"{prefix}.narrations must be a non-empty array")
            narrations = []
        if len(narrations) > 30:
            errors.append(f"{prefix}.narrations cannot contain more than 30 sentences")
        durations: list[float] = []
        for line_index, narration in enumerate(narrations):
            line_prefix = f"{prefix}.narrations[{line_index}]"
            if not isinstance(narration, dict):
                errors.append(f"{line_prefix} must be an object")
                continue
            text = narration.get("text")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{line_prefix}.text must be a non-empty sentence")
                continue
            if len(text) > caption_max:
                errors.append(
                    f"{line_prefix}.text exceeds project.caption_max_characters={caption_max}"
                )
            elif len(text) > 60:
                warnings.append(f"{line_prefix}.text may require a smaller caption font")
            if not isinstance(narration.get("emotion"), str) or not narration["emotion"].strip():
                errors.append(f"{line_prefix}.emotion must be a non-empty string")
            durations.append(estimate_text_seconds(text, speed))

        focus = scene.get("focus")
        if not isinstance(focus, dict):
            errors.append(f"{prefix}.focus must be an object")
        else:
            for key in ("x_percent", "y_percent"):
                value = focus.get(key)
                if not isinstance(value, (int, float)) or not 0 <= float(value) <= 100:
                    errors.append(f"{prefix}.focus.{key} must be between 0 and 100")
        motion = scene.get("motion")
        if not isinstance(motion, dict) or motion.get("type") not in {"slow_zoom_in", "slow_zoom_out"}:
            errors.append(f"{prefix}.motion must define slow_zoom_in or slow_zoom_out")
        else:
            start_scale = motion.get("scale_from")
            end_scale = motion.get("scale_to")
            if not all(isinstance(v, (int, float)) and 1 <= float(v) <= 1.2 for v in (start_scale, end_scale)):
                errors.append(f"{prefix}.motion scales must be between 1 and 1.2")
            elif motion["type"] == "slow_zoom_in" and float(end_scale) <= float(start_scale):
                errors.append(f"{prefix}.motion slow_zoom_in must increase scale")
            elif motion["type"] == "slow_zoom_out" and float(end_scale) >= float(start_scale):
                errors.append(f"{prefix}.motion slow_zoom_out must decrease scale")

        scene_duration = SCENE_PADDING_SECONDS + sum(durations) + max(0, len(durations) - 1) * gap
        scene_estimates.append({"id": scene_id or f"scene_{index + 1:03d}", "seconds": round(scene_duration, 3)})

    estimated_duration = sum(item["seconds"] for item in scene_estimates)
    estimated_duration -= max(0, len(scene_estimates) - 1) * TRANSITION_SECONDS
    estimated_duration = max(0.0, estimated_duration)
    if estimated_duration > MAX_DURATION_SECONDS:
        errors.append(
            f"estimated timeline is {estimated_duration:.1f}s; maximum is {MAX_DURATION_SECONDS:.0f}s"
        )
    elif estimated_duration > DRAFT_WARNING_SECONDS:
        warnings.append(
            f"estimated timeline is {estimated_duration:.1f}s; leave more TTS variance below 900s"
        )

    stage_requirements = {
        "visual_review": ("story",),
        "style_and_character_review": ("story",),
        "scene_image_review": ("story", "style_and_characters"),
        "audio_generation": ("story", "style_and_characters", "scene_images"),
        "composition": ("story", "style_and_characters", "scene_images"),
        "complete": ("story", "style_and_characters", "scene_images"),
    }
    for key in stage_requirements.get(stage, ()):
        if approvals.get(key) != "approved":
            errors.append(f"stage {stage} requires approvals.{key}=approved")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "scene_count": len(scenes),
        "estimated_duration_seconds": round(estimated_duration, 3),
        "scene_estimates": scene_estimates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a comic-drama story JSON file")
    parser.add_argument("story", type=Path)
    parser.add_argument("--json", action="store_true", help="Print a machine-readable report")
    args = parser.parse_args()

    try:
        report = validate_story(load_story(args.story.resolve()))
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "valid" if report["valid"] else "invalid"
        print(
            f"Story is {status}: {report['scene_count']} scenes, "
            f"estimated {report['estimated_duration_seconds']:.1f}s"
        )
        for warning in report["warnings"]:
            print(f"Warning: {warning}", file=sys.stderr)
        for error in report["errors"]:
            print(f"Error: {error}", file=sys.stderr)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
