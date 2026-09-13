#!/usr/bin/env python3
"""Validate companion artifacts and finalize the GCW teardown gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, UnidentifiedImageError


SITE_SPEC_SECTIONS = tuple(str(index) for index in range(1, 13))
ALLOWED_FIDELITY = {"Exact", "Approximate", "Unknown", "Excluded"}
ALLOWED_TRUTH = {"SOURCE", "PARTIAL", "GUESS"}


def ensure_safe_path(root: Path, path: Path) -> None:
    resolved = path.resolve()
    if root != resolved and root not in resolved.parents:
        raise ValueError(f"artifact path leaves .gcw: {path}")
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError(f"artifact path must not use symlinks: {path}")
        current = current.parent


def load_json(path: Path, root: Path) -> dict:
    ensure_safe_path(root, path)
    if not path.is_file():
        raise ValueError(f"missing required artifact: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid JSON artifact: {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return value


def validate_site_spec(path: Path, root: Path, teardown_depth: str) -> str:
    ensure_safe_path(root, path)
    if not path.is_file():
        raise ValueError(f"missing required artifact: {path}")
    text = path.read_text(encoding="utf-8")
    if "Status: DRAFT" not in text and "Status: FINAL" not in text:
        raise ValueError("SITE_SPEC.md status must be DRAFT or FINAL")
    if "<!-- REQUIRED" in text:
        raise ValueError("SITE_SPEC.md still contains REQUIRED placeholders")
    matches = list(re.finditer(r"^## (\d+)\. .+$", text, re.MULTILINE))
    expected = ("1", "5", "9", "12") if teardown_depth == "minimal" else SITE_SPEC_SECTIONS
    if tuple(match.group(1) for match in matches) != expected:
        raise ValueError(f"SITE_SPEC.md must contain the {len(expected)} required numbered sections in order for {teardown_depth} teardown")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        if not body:
            raise ValueError(f"SITE_SPEC.md section {match.group(1)} is empty")
    validate_subsystem_table(text)
    return text


def validate_subsystem_table(text: str) -> None:
    match = re.search(r"^## 9\. [^\n]+\n(.*?)(?=^## \d+\.|\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError("SITE_SPEC.md section 9 subsystem table is missing")
    rows = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
        if cells and cells[0] not in {"Subsystem", "---"} and not all(set(cell) <= {"-", ":"} for cell in cells):
            rows.append(cells)
    if not rows:
        raise ValueError("SITE_SPEC.md section 9 requires at least one subsystem row")
    for row_number, cells in enumerate(rows, 1):
        if len(cells) != 6:
            raise ValueError(f"SITE_SPEC.md section 9 row {row_number} must have 6 columns")
        subsystem, fidelity, truth, evidence, blocking, acceptance = cells
        if not subsystem:
            raise ValueError(f"SITE_SPEC.md section 9 row {row_number} has no subsystem")
        if fidelity not in ALLOWED_FIDELITY:
            raise ValueError(f"SITE_SPEC.md section 9 row {row_number} has invalid Fidelity: {fidelity}")
        if truth not in ALLOWED_TRUTH:
            raise ValueError(f"SITE_SPEC.md section 9 row {row_number} has invalid Truth: {truth}")
        if blocking.lower() not in {"yes", "no"}:
            raise ValueError(f"SITE_SPEC.md section 9 row {row_number} has invalid Blocking: {blocking}")
        if not evidence or not acceptance:
            raise ValueError(f"SITE_SPEC.md section 9 row {row_number} requires Evidence and Acceptance")


def artifact_entry(root: Path, path: Path, kind: str, source_skill: str) -> dict[str, str]:
    return {
        "id": f"artifact-{kind}",
        "kind": kind,
        "path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sourceSkill": source_skill,
    }


def require_nonempty_json(root: Path, path: Path) -> None:
    value = load_json(path, root)
    if not value:
        raise ValueError(f"required evidence is empty: {path}")


def validate_interaction_states(root: Path, path: Path) -> None:
    value = load_json(path, root)
    if value.get("schemaVersion") != 1:
        raise ValueError("interaction-states.json schemaVersion must be 1")
    if value.get("reviewStatus") not in (None, "confirmed"):
        raise ValueError("generated interaction-states.json reviewStatus must be confirmed before finalization")
    states = value.get("states")
    if not isinstance(states, list) or not states:
        raise ValueError("interaction-states.json requires at least one state")
    required = {"id", "route", "trigger", "expected", "evidence"}
    for index, state in enumerate(states, 1):
        if not isinstance(state, dict):
            raise ValueError(f"interaction-states.json state {index} must be an object")
        missing = sorted(key for key in required if not state.get(key))
        if missing:
            raise ValueError(f"interaction-states.json state {index} missing: {', '.join(missing)}")
        if not isinstance(state["evidence"], list) or not all(isinstance(item, str) and item for item in state["evidence"]):
            raise ValueError(f"interaction-states.json state {index} evidence must be a non-empty string array")


def require_object(value: dict, key: str, label: str) -> dict:
    child = value.get(key)
    if not isinstance(child, dict):
        raise ValueError(f"{label}.{key} must be an object")
    return child


def evidence_files(root: Path, path: Path, suffixes: set[str] | None = None) -> list[Path]:
    files = [item for item in path.rglob("*") if item.is_file() and item.stat().st_size > 0]
    if suffixes is not None:
        files = [item for item in files if item.suffix.lower() in suffixes]
    if not files:
        raise ValueError(f"missing required evidence files under: {path}")
    for item in files:
        ensure_safe_path(root, item)
    return sorted(files)


def verify_images(paths: list[Path]) -> None:
    for path in paths:
        try:
            with Image.open(path) as image:
                image.verify()
        except (OSError, UnidentifiedImageError) as error:
            raise ValueError(f"invalid screenshot image: {path}: {error}") from error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    root = args.workspace.resolve() / ".gcw"

    manifest_path = root / "teardown-manifest.json"
    manifest = load_json(manifest_path, root)
    state_path = root / "run-state.json"
    state = load_json(state_path, root)
    teardown_depth = state.get("teardownDepth", "standard")
    if teardown_depth not in {"minimal", "standard", "deep"}:
        raise ValueError(f"invalid teardownDepth: {teardown_depth}")
    site_spec_path = root / "SITE_SPEC.md"
    site_spec = validate_site_spec(site_spec_path, root, teardown_depth)

    evidence_root = root / "evidence"
    fixed_json = {
        "site-inventory": evidence_root / "site-inventory.json",
        "route-map": evidence_root / "route-map.json",
        "interaction-states": evidence_root / "interaction-states.json",
    }
    source_maps_path = evidence_root / "source-maps.json"
    if source_maps_path.is_file():
        fixed_json["source-maps"] = source_maps_path
    for name, path in fixed_json.items():
        if name == "interaction-states":
            continue
        require_nonempty_json(root, path)
    validate_interaction_states(root, fixed_json["interaction-states"])
    desktop_screenshots = evidence_files(root, evidence_root / "screenshots" / "desktop", {".png", ".jpg", ".jpeg", ".webp"})
    mobile_screenshots = evidence_files(root, evidence_root / "screenshots" / "mobile", {".png", ".jpg", ".jpeg", ".webp"})
    verify_images(desktop_screenshots + mobile_screenshots)
    network_evidence = evidence_files(root, evidence_root / "network")

    design_path = root / "evidence" / "design-dna" / "design-dna.json"
    required_design_keys = {"meta", "design_system", "design_style", "visual_effects"}
    design = load_json(design_path, root) if design_path.is_file() else None
    if teardown_depth != "minimal" and design is None:
        raise ValueError(f"missing required artifact: {design_path}")
    if design is not None and (not required_design_keys.issubset(design) or any(not design[key] for key in required_design_keys)):
        raise ValueError("design-dna.json contract three-dimension-v1 requires non-empty meta, design_system, design_style, and visual_effects")

    shader_root = root / "evidence" / "web-shader-extractor"
    decision_path = shader_root / "gpu-decision.json"
    decision = load_json(decision_path, root)
    gpu_decision = decision.get("decision")
    indexed = [
        *(artifact_entry(root, path, kind, "gcw") for kind, path in fixed_json.items()),
        *(artifact_entry(root, path, f"desktop-screenshot-{index}", "gcw") for index, path in enumerate(desktop_screenshots, 1)),
        *(artifact_entry(root, path, f"mobile-screenshot-{index}", "gcw") for index, path in enumerate(mobile_screenshots, 1)),
        *(artifact_entry(root, path, f"network-evidence-{index}", "gcw") for index, path in enumerate(network_evidence, 1)),
        artifact_entry(root, decision_path, "gpu-decision", "gcw"),
    ]
    if design is not None:
        design_entry = artifact_entry(root, design_path, "design-dna", "design-dna")
        design_entry["schemaContract"] = "three-dimension-v1"
        indexed.append(design_entry)
    if gpu_decision == "not-applicable":
        if not decision.get("checkedSurfaces") or not decision.get("detectionEvidence"):
            raise ValueError("GPU N/A requires checkedSurfaces and detectionEvidence")
        gpu_status = "not-applicable"
    elif gpu_decision == "required":
        if teardown_depth == "minimal":
            raise ValueError("minimal teardown requires evidence-backed GPU not-applicable; use standard or deep for GPU targets")
        scout_path = shader_root / "scout-card.json"
        replay_path = shader_root / "replay-manifest.json"
        scout = load_json(scout_path, root)
        replay = load_json(replay_path, root)
        if scout.get("schemaVersion") != 3 or replay.get("schemaVersion") != 3:
            raise ValueError("web-shader-extractor schema drift: expected scout-card and replay-manifest schemaVersion 3")
        if scout.get("lockStatus") != "locked" or scout.get("gateDecision", {}).get("targetLocked") is not True:
            raise ValueError("GPU teardown requires a TARGET_LOCKED scout-card.json")
        if replay.get("gateDecision", {}).get("replayReady") is not True:
            raise ValueError("GPU teardown requires a REPLAY_READY replay-manifest.json")
        if replay.get("unknowns", {}).get("blocking") or replay.get("gateDecision", {}).get("blockers"):
            raise ValueError("GPU teardown cannot finalize with blocking replay unknowns")
        for path, kind in ((scout_path, "shader-scout-card"), (replay_path, "shader-replay-manifest")):
            entry = artifact_entry(root, path, kind, "web-shader-extractor")
            entry["schemaVersion"] = 3
            indexed.append(entry)
        gpu_status = "replay-ready"
    else:
        raise ValueError("gpu-decision.json decision must be required or not-applicable")

    if manifest.get("blockingUnknowns"):
        raise ValueError("teardown-manifest.json has blockingUnknowns")

    site_spec_manifest = require_object(manifest, "siteSpec", "teardown-manifest.json")
    design_manifest = require_object(manifest, "designDna", "teardown-manifest.json")
    gpu_manifest = require_object(manifest, "gpuAnalysis", "teardown-manifest.json")
    index_path = root / "evidence" / "evidence-index.json"
    evidence_index = load_json(index_path, root)
    if not isinstance(evidence_index.get("entries"), list):
        raise ValueError("evidence-index.json entries must be an array")

    finalized_at = datetime.now(timezone.utc).isoformat()
    finalized_site_spec = site_spec.replace("Status: DRAFT", "Status: FINAL", 1)
    indexed.append({
        "id": "artifact-site-spec",
        "kind": "site-spec",
        "path": site_spec_path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(finalized_site_spec.encode("utf-8")).hexdigest(),
        "sourceSkill": "gcw",
    })
    existing = {
        entry.get("id"): entry
        for entry in evidence_index.get("entries", [])
        if isinstance(entry, dict) and not str(entry.get("id", "")).startswith("artifact-")
    }
    existing.update({entry["id"]: entry for entry in indexed})
    evidence_index["entries"] = list(existing.values())

    manifest.update({"status": "passed", "finalizedAt": finalized_at})
    site_spec_manifest.update({"status": "final"})
    design_manifest.update({"required": teardown_depth != "minimal", "status": "passed" if design is not None else "recommended-not-provided"})
    gpu_manifest.update({"decision": gpu_decision, "status": gpu_status})

    state["analysisGates"] = {"designDna": "complete", "gpuForensics": gpu_status, "teardown": "passed"}

    site_spec_path.write_text(finalized_site_spec, encoding="utf-8")
    index_path.write_text(json.dumps(evidence_index, indent=2) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "gpuAnalysis": gpu_status, "finalizedAt": finalized_at}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
