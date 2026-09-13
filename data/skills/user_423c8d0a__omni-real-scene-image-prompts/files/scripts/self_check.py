#!/usr/bin/env python3
"""Deterministic package checks for omni-real-scene-image-prompts v3.0.2-wb (WorkBuddy edition)."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import tempfile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"

REQUIRED_FILES = (
    "VERSION",
    "CHANGELOG.md",
    "MANIFEST.sha256",
    "SKILL.md",
    "agents/openai.yaml",
    "assets/universal_scene_card_template.md",
    "assets/social_series_template.md",
    "assets/visual_fission_template.csv",
    "references/industry-scene-atlas.md",
    "references/output-contract.md",
    "references/routing-and-modes.md",
    "references/n10-visual-fission-engine.md",
    "references/visual-opportunity-scoring.md",
    "references/universal-scene-world-schema.md",
    "references/evidence-stack-and-provenance.md",
    "references/satellite-ground-evidence-protocol.md",
    "references/china-morphology-engine.md",
    "references/global-localization-policy.md",
    "references/physical-causality-and-affordance.md",
    "references/people-mobility-behavior-engine.md",
    "references/domain-process-atlas.md",
    "references/commerce-operation-engine.md",
    "references/store-world-schema.md",
    "references/social-media-content-engine.md",
    "references/xiaohongshu-visual-engine.md",
    "references/product-and-brand-scene-engine.md",
    "references/people-home-work-education-health-engine.md",
    "references/space-architecture-interior-engine.md",
    "references/industrial-agriculture-infrastructure-engine.md",
    "references/outdoor-travel-nature-engine.md",
    "references/events-documentary-engine.md",
    "references/knowledge-health-education-engine.md",
    "references/camera-and-visual-realism.md",
    "references/text-signage-policy.md",
    "references/continuity-series-and-multiratio.md",
    "references/reference-visual-dna.md",
    "references/batch-diversity-ledger.md",
    "references/prompt-composer.md",
    "references/model-adapters.md",
    "references/quality-gate-and-repair.md",
    "references/compliance-production-gate.md",
    "references/source-baseline.md",
    "references/example-prompts.md",
    "scripts/build_visual_fission_matrix.py",
    "scripts/score_visual_candidates.py",
    "scripts/audit_visual_plan.py",
    "scripts/validate_scene_world.py",
    "scripts/validate_evidence_manifest.py",
    "scripts/lint_prompt_output.py",
    "scripts/audit_store_scene_plan.py",
    "scripts/self_check.py",
    "schemas/universal_scene.schema.json",
    "schemas/visual_plan.schema.json",
    "schemas/visual_fission.schema.json",
    "tests/sample_scene_world.json",
    "tests/invalid_scene_world.json",
    "tests/sample_batch_plan.json",
    "tests/invalid_batch_plan.json",
    "tests/sample_series_plan.json",
    "tests/sample_multiratio_plan.json",
    "tests/sample_visual_fission.json",
    "tests/sample_visual_candidates.csv",
    "tests/sample_evidence_manifest.json",
    "tests/invalid_evidence_manifest.json",
    "tests/sample_prompt_output.txt",
    "tests/invalid_prompt_output.txt",
    "tests/golden_requests.md",
)

OLD_BEHAVIOR_PHRASES = (
    "若用户要成图，不要只交付提示词",
    "默认使用内置图像生成能力",
    "最终图片或成套图片",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def run_expect(script: str, args: list[str], expected_success: bool) -> None:
    command = [sys.executable, str(ROOT / script), *args]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    success = result.returncode == 0
    if success != expected_success:
        print(result.stdout)
        print(result.stderr)
        outcome = "succeed" if expected_success else "fail"
        fail(f"expected {' '.join(command)} to {outcome}, got exit={result.returncode}")


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != "3.0.2-wb":
        fail(f"VERSION must be 3.0.2-wb, got {version!r}")

    skill = SKILL.read_text(encoding="utf-8")
    parts = skill.split("---", 2)
    if len(parts) < 3:
        fail("SKILL.md frontmatter is malformed")
    keys = re.findall(r"^([a-zA-Z0-9_-]+):", parts[1], flags=re.MULTILINE)
    required_keys = {"name", "description", "agent_created"}
    found_keys = set(keys)
    if not required_keys.issubset(found_keys):
        fail(f"frontmatter must contain name, description, agent_created; got {keys}")
    if len(found_keys - required_keys) > 0:
        extra = found_keys - required_keys
        print(f"NOTE: extra frontmatter keys present (allowed): {extra}")
    if "name: omni-real-scene-image-prompts" not in skill:
        fail("SKILL.md has wrong skill name")
    if len(skill.splitlines()) > 500:
        fail(f"SKILL.md exceeds 500 lines: {len(skill.splitlines())}")
    if "唯一正式交付物是提示词" not in skill:
        fail("Prompt-Only contract missing")
    if "V10 视觉裂变引擎" not in skill or "R12 通用真实世界模型" not in skill:
        fail("dual-engine architecture missing")
    if "调用图像生成或编辑工具" not in skill:
        fail("direct image generation prohibition missing")
    if "agent_created" not in parts[1]:
        fail("agent_created: true is missing from frontmatter")
    for phrase in OLD_BEHAVIOR_PHRASES:
        if phrase in skill:
            fail(f"old direct-image behavior remains: {phrase}")

    referenced = set(re.findall(r"\((references/[^)]+\.md)\)", skill))
    missing_links = sorted(path for path in referenced if not (ROOT / path).is_file())
    if missing_links:
        fail("SKILL.md links missing: " + ", ".join(missing_links))
    unlinked_required_refs = sorted(
        path for path in REQUIRED_FILES if path.startswith("references/") and path not in referenced
    )
    if unlinked_required_refs:
        fail("required references not routed from SKILL.md: " + ", ".join(unlinked_required_refs))

    json_files = sorted(path for path in ROOT.rglob("*.json"))
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")

    script_files = sorted(path for path in (ROOT / "scripts").glob("*.py"))
    for path in script_files:
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, str(path), "exec")
        except SyntaxError as exc:
            fail(f"syntax error in {path.relative_to(ROOT)}: {exc}")

    with (ROOT / "tests/sample_visual_candidates.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or "candidate" not in rows[0] or "safety" not in rows[0]:
        fail("sample_visual_candidates.csv has invalid header or no rows")

    forbidden = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.name in {"__pycache__", ".DS_Store"} or path.suffix in {".pyc", ".pyo"}
    ]
    if forbidden:
        fail("forbidden build artifacts present: " + ", ".join(forbidden))

    # Valid fixtures.
    run_expect("scripts/audit_visual_plan.py", ["tests/sample_batch_plan.json", "--strict"], True)
    run_expect("scripts/audit_visual_plan.py", ["tests/sample_series_plan.json", "--strict"], True)
    run_expect("scripts/audit_visual_plan.py", ["tests/sample_multiratio_plan.json", "--strict"], True)
    run_expect("scripts/validate_scene_world.py", ["tests/sample_scene_world.json", "--strict"], True)
    run_expect("scripts/validate_evidence_manifest.py", ["tests/sample_evidence_manifest.json", "--strict"], True)
    run_expect("scripts/lint_prompt_output.py", ["tests/sample_prompt_output.txt", "--strict"], True)
    run_expect("scripts/score_visual_candidates.py", ["tests/sample_visual_candidates.csv"], True)
    run_expect(
        "scripts/build_visual_fission_matrix.py",
        ["--seed", "职场妈妈晚餐", "--audience", "城市家庭", "--platform", "小红书"],
        True,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "visual-fission.csv"
        run_expect(
            "scripts/build_visual_fission_matrix.py",
            [
                "--seed",
                "职场妈妈晚餐",
                "--audience",
                "城市家庭",
                "--platform",
                "小红书",
                "--out",
                str(output_path),
            ],
            True,
        )
        if not output_path.is_file():
            fail("build_visual_fission_matrix.py --out did not create a file")
        with output_path.open("r", encoding="utf-8-sig", newline="") as handle:
            matrix_rows = list(csv.DictReader(handle))
        if len(matrix_rows) != 10 or {row.get("dimension", "") for row in matrix_rows} != {
            "domain",
            "audience",
            "content_objective",
            "platform",
            "scene_moment",
            "subject",
            "action",
            "emotional_evidence",
            "visual_language",
            "delivery_variant",
        }:
            fail("build_visual_fission_matrix.py --out produced an invalid V10 matrix")

    # Invalid fixtures.
    run_expect("scripts/audit_visual_plan.py", ["tests/invalid_batch_plan.json", "--strict"], False)
    run_expect("scripts/validate_scene_world.py", ["tests/invalid_scene_world.json", "--strict"], False)
    run_expect("scripts/validate_evidence_manifest.py", ["tests/invalid_evidence_manifest.json", "--strict"], False)
    run_expect("scripts/lint_prompt_output.py", ["tests/invalid_prompt_output.txt", "--strict"], False)

    file_count = len([path for path in ROOT.rglob("*") if path.is_file()])
    print(
        "PASS: package self-check passed; "
        f"version={version} SKILL.md lines={len(skill.splitlines())} files={file_count} refs={len(referenced)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
