#!/usr/bin/env python3
"""Validate the structured brief used by wechat-cover-design."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED = {
    "input_quality", "article_thesis", "reader_takeaway", "content_class", "theme",
    "visual_metaphor", "elements", "forbidden_substitutions", "title", "prompt_elements",
    "image_prompt",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["brief must be a JSON object"]

    missing = sorted(REQUIRED - data.keys())
    if missing:
        return ["missing required fields: " + ", ".join(missing)]

    quality = data["input_quality"]
    if quality not in {"final", "provisional"}:
        fail(errors, "input_quality must be final or provisional")
    if quality == "provisional":
        fail(errors, "provisional briefs cannot generate a final image; request clarification or deliver prompt-only")

    for key, minimum in (("article_thesis", 20), ("reader_takeaway", 12), ("image_prompt", 300)):
        value = data.get(key)
        if not isinstance(value, str) or len(value.strip()) < minimum:
            fail(errors, f"{key} must be at least {minimum} characters")

    if data["content_class"] not in {
        "personal_showcase", "opinion", "method", "mechanism", "trend", "transaction",
        "controversy", "evidence", "industry_landscape",
    }:
        fail(errors, "content_class is not recognized")

    theme = data.get("theme")
    if not isinstance(theme, dict):
        fail(errors, "theme must be an object")
    else:
        # Theme IDs are defined by the current 13-theme registry.
        if theme.get("id") not in {f"theme{i}" for i in range(1, 14)}:
            fail(errors, "theme.id is not registered")
        if not isinstance(theme.get("rationale"), str) or len(theme["rationale"].strip()) < 20:
            fail(errors, "theme.rationale must explain the thesis-to-theme fit")
        if theme.get("compatibility") not in {"compatible", "user_override"}:
            fail(errors, "theme.compatibility must be compatible or user_override")

    metaphor = data.get("visual_metaphor")
    if not isinstance(metaphor, dict) or not all(isinstance(metaphor.get(k), str) and len(metaphor[k].strip()) >= 20 for k in ("relationship", "thesis_explanation")):
        fail(errors, "visual_metaphor must explain the relationship and why it communicates the thesis")

    elements = data.get("elements")
    ids: set[str] = set()
    if not isinstance(elements, list) or not elements:
        fail(errors, "elements must contain at least one sourced focal or supporting element")
    else:
        for index, element in enumerate(elements, 1):
            if not isinstance(element, dict):
                fail(errors, f"elements[{index}] must be an object")
                continue
            element_id = element.get("id")
            if not isinstance(element_id, str) or not element_id:
                fail(errors, f"elements[{index}].id is required")
            elif element_id in ids:
                fail(errors, f"duplicate element id: {element_id}")
            else:
                ids.add(element_id)
            if element.get("role") not in {"focal", "supporting"}:
                fail(errors, f"elements[{index}].role must be focal or supporting")
            for key in ("description", "source"):
                if not isinstance(element.get(key), str) or len(element[key].strip()) < 8:
                    fail(errors, f"elements[{index}].{key} is too vague")
        if ids and not any(item.get("role") == "focal" for item in elements if isinstance(item, dict)):
            fail(errors, "at least one focal element is required")

    forbidden = data.get("forbidden_substitutions")
    if not isinstance(forbidden, list) or not all(isinstance(item, str) and len(item.strip()) >= 3 for item in forbidden):
        fail(errors, "forbidden_substitutions must list keyword-driven but irrelevant visual shortcuts")

    prompt_elements = data.get("prompt_elements")
    if not isinstance(prompt_elements, list) or not prompt_elements:
        fail(errors, "prompt_elements must map every visual prompt object to an element id")
    else:
        mapped_ids = set()
        for index, item in enumerate(prompt_elements, 1):
            if not isinstance(item, dict) or item.get("element_id") not in ids:
                fail(errors, f"prompt_elements[{index}] references an unknown element id")
                continue
            mapped_ids.add(item["element_id"])
            if not isinstance(item.get("prompt_description"), str) or len(item["prompt_description"].strip()) < 8:
                fail(errors, f"prompt_elements[{index}].prompt_description is too vague")
        missing_mappings = ids - mapped_ids
        if missing_mappings:
            fail(errors, "elements missing from prompt_elements: " + ", ".join(sorted(missing_mappings)))

    title = data.get("title")
    title_fields = ("exact_text", "subtitle", "zone", "type_mood", "type_palette", "integration_device")
    if not isinstance(title, dict) or not all(isinstance(title.get(k), str) and len(title[k].strip()) >= 1 for k in title_fields if k != "subtitle"):
        fail(errors, "title must contain exact_text, subtitle, zone, type_mood, type_palette, and integration_device")

    prompt = data.get("image_prompt", "")
    prompt_body = prompt.split("Negative prompt:", 1)[0]
    # The Alignment Record documents forbidden substitutions for reviewers. It is not an
    # instruction to render them, so exclude that metadata line from artwork checks.
    prompt_body = re.sub(r"(?im)^\s*Forbidden substitutions\s*:\s*.*$", "", prompt_body).casefold()
    if isinstance(forbidden, list):
        matched = [item for item in forbidden if isinstance(item, str) and item.casefold() in prompt_body]
        if matched:
            fail(errors, "image_prompt body contains forbidden substitutions: " + ", ".join(matched))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a structured WeChat cover brief JSON file.")
    parser.add_argument("brief", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.brief.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: could not read brief: {exc}")
        return 1
    errors = validate(data)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print("PASS: structured brief is complete and internally aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
