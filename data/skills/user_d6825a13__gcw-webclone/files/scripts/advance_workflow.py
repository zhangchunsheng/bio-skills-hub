#!/usr/bin/env python3
"""Advance a GCW project through explicit workflow gates."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


TRANSITIONS = {
    "TEARDOWN_PHASE": {"FAITHFUL_CLONE", "COMPLETE"},
    "FAITHFUL_CLONE": {"REVIEW_GATE"},
    "REVIEW_GATE": {"FAITHFUL_CLONE", "COMPLETE", "CREATIVE_REBUILD"},
    "CREATIVE_REBUILD": {"COMPLETE"},
    "COMPLETE": {"CREATIVE_REBUILD"},
}

REVIEW_DESTINATIONS = {"A": "FAITHFUL_CLONE", "B": "COMPLETE", "C": "CREATIVE_REBUILD"}
DELIVERY_CONTRACTS = {
    "A": ("RESEARCH_OR_RUNNABLE_REPLAY", "RUNNABLE_REPLAY"),
    "B": ("EDITABLE_FAITHFUL_CLONE", "MAINTAINABLE_SOURCE"),
    "C": ("EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE", "MAINTAINABLE_SOURCE"),
}
CURRENT_SCHEMA_VERSION = 5
CREATIVE_BRIEF_SECTIONS = (
    "Keep",
    "Remove",
    "Change",
    "New brand, content, and features",
    "Innovation direction",
    "Final acceptance target",
)


def require_nonempty_file(path: Path, label: str) -> str:
    if not path.is_file():
        raise ValueError(f"{label} is required: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"{label} must not be empty: {path}")
    return text


def require_completed_file(path: Path, label: str) -> str:
    text = require_nonempty_file(path, label)
    if "REQUIRED" in text:
        raise ValueError(f"{label} contains REQUIRED placeholders: {path}")
    return text


def migrate_state(state: dict) -> None:
    schema_version = state.get("schemaVersion", 0)
    if not isinstance(schema_version, int) or schema_version > CURRENT_SCHEMA_VERSION:
        raise ValueError(f"unsupported run-state.json schemaVersion: {schema_version}")
    if state.get("recoveryStrategy") == "EDITABLE_REBUILD":
        state["recoveryStrategy"] = "MAINTAINABLE_REBUILD"
        state.setdefault("stateMigrations", []).append({
            "field": "recoveryStrategy",
            "from": "EDITABLE_REBUILD",
            "to": "MAINTAINABLE_REBUILD",
            "recordedAt": datetime.now(timezone.utc).isoformat(),
        })
    state.setdefault("finalDeliverable", "UNCONFIRMED")
    state.setdefault("editabilityTarget", "UNCONFIRMED")
    state.setdefault("deliveryContractConfirmedForBuild", False)
    state["schemaVersion"] = CURRENT_SCHEMA_VERSION


def apply_delivery_contract(state: dict, choice: str, *, building: bool) -> None:
    previous = {
        "finalDeliverable": state.get("finalDeliverable"),
        "editabilityTarget": state.get("editabilityTarget"),
    }
    final_deliverable, editability_target = DELIVERY_CONTRACTS[choice]
    state["finalDeliverable"] = final_deliverable
    state["editabilityTarget"] = editability_target
    state["deliveryContractConfirmedForBuild"] = True
    if choice == "A":
        state["outcome"] = "faithful-clone" if building else "teardown"
    elif choice == "B":
        state["outcome"] = "faithful-clone"
    elif choice == "C":
        state["outcome"] = "creative-rebuild"
    state.setdefault("deliveryContractHistory", []).append({
        "choice": choice,
        "previous": previous,
        "finalDeliverable": final_deliverable,
        "editabilityTarget": editability_target,
        "recordedAt": datetime.now(timezone.utc).isoformat(),
    })


def validate_delivery_contract(state: dict, *, require_build_confirmation: bool) -> None:
    expected_targets = {final: target for final, target in DELIVERY_CONTRACTS.values()}
    final_deliverable = state.get("finalDeliverable")
    editability_target = state.get("editabilityTarget")
    if final_deliverable not in expected_targets:
        raise ValueError(f"invalid or unconfirmed finalDeliverable: {final_deliverable}")
    if editability_target != expected_targets[final_deliverable]:
        raise ValueError(
            f"delivery contract mismatch: {final_deliverable} requires editabilityTarget "
            f"{expected_targets[final_deliverable]}"
        )
    outcome = state.get("outcome")
    if final_deliverable == "EDITABLE_FAITHFUL_CLONE" and outcome != "faithful-clone":
        raise ValueError("EDITABLE_FAITHFUL_CLONE requires outcome faithful-clone")
    if final_deliverable == "EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE" and outcome != "creative-rebuild":
        raise ValueError("EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE requires outcome creative-rebuild")
    if final_deliverable == "RESEARCH_OR_RUNNABLE_REPLAY" and outcome == "creative-rebuild":
        raise ValueError("RESEARCH_OR_RUNNABLE_REPLAY cannot use outcome creative-rebuild")
    if require_build_confirmation and not state.get("deliveryContractConfirmedForBuild"):
        raise ValueError("build work requires an explicitly confirmed final deliverable A, B, or C")


def require_project_file(workspace: Path, value: object, label: str, *, source: bool = False) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty workspace-relative path")
    relative = Path(value)
    if relative.is_absolute():
        raise ValueError(f"{label} must be workspace-relative: {value}")
    resolved = (workspace / relative).resolve()
    if workspace != resolved and workspace not in resolved.parents:
        raise ValueError(f"{label} leaves the workspace: {value}")
    if not resolved.is_file():
        raise ValueError(f"{label} is required: {resolved}")
    if source:
        parts = {part.lower() for part in relative.parts}
        if parts.intersection({"dist", "build", ".next", "_next", "chunks"}) or resolved.name.endswith(".min.js"):
            raise ValueError(f"{label} must point to maintainable source, not a production artifact: {value}")
    return resolved


def require_evidence_files(workspace: Path, value: object, label: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must contain at least one evidence path")
    for index, item in enumerate(value):
        require_project_file(workspace, item, f"{label}[{index}]")


def validate_editability_contract(workspace: Path, root: Path, state: dict) -> None:
    if state.get("editabilityTarget") != "MAINTAINABLE_SOURCE":
        return
    if state.get("finalDeliverable") not in {
        "EDITABLE_FAITHFUL_CLONE",
        "EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE",
    }:
        raise ValueError("MAINTAINABLE_SOURCE requires an editable final deliverable")
    recovery_strategy = state.get("recoveryStrategy", "")
    if recovery_strategy == "ARTIFACT_REPLAY":
        raise ValueError("ARTIFACT_REPLAY is oracle-only for MAINTAINABLE_SOURCE and cannot pass the formal delivery gate")
    if state.get("implementationPath") == "PRODUCTION_RECOVERY" and recovery_strategy != "MAINTAINABLE_REBUILD":
        raise ValueError("PRODUCTION_RECOVERY with MAINTAINABLE_SOURCE requires recoveryStrategy MAINTAINABLE_REBUILD")

    evidence_path = root / "editability-evidence.json"
    try:
        evidence = json.loads(require_nonempty_file(evidence_path, "editability-evidence.json"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid editability-evidence.json: {error}") from error
    if evidence.get("schemaVersion") != 1:
        raise ValueError("editability-evidence.json schemaVersion must be 1")
    if evidence.get("reviewStatus") != "confirmed":
        raise ValueError("editability-evidence.json reviewStatus must be confirmed")
    if evidence.get("artifactReplayRole") not in {"not-used", "oracle-only"}:
        raise ValueError("editability-evidence.json artifactReplayRole must be not-used or oracle-only")

    require_project_file(
        workspace,
        evidence.get("maintainableSourceEntrypoint"),
        "maintainableSourceEntrypoint",
        source=True,
    )
    replacement_map = require_project_file(
        workspace,
        evidence.get("contentReplacementMap"),
        "contentReplacementMap",
    )
    require_completed_file(replacement_map, "content replacement map")

    change = evidence.get("controlledContentChange")
    if not isinstance(change, dict):
        raise ValueError("editability-evidence.json controlledContentChange must be an object")
    require_project_file(workspace, change.get("sourceFile"), "controlledContentChange.sourceFile", source=True)
    for field in ("field", "beforeValue", "afterValue", "buildCommand"):
        if not isinstance(change.get(field), str) or not change[field].strip():
            raise ValueError(f"controlledContentChange.{field} must not be empty")
    if change["beforeValue"] == change["afterValue"]:
        raise ValueError("controlledContentChange beforeValue and afterValue must differ")
    if change.get("productionBundlesModified") is not False:
        raise ValueError("controlledContentChange.productionBundlesModified must be false")
    require_evidence_files(workspace, change.get("evidence"), "controlledContentChange.evidence")

    runtime = evidence.get("runtimeIndependence")
    if not isinstance(runtime, dict) or runtime.get("status") != "passed":
        raise ValueError("editability-evidence.json runtimeIndependence.status must be passed")
    require_evidence_files(workspace, runtime.get("evidence"), "runtimeIndependence.evidence")


def validate_completed_b_resume(workspace: Path, root: Path, state: dict) -> None:
    validate_delivery_contract(state, require_build_confirmation=True)
    if state.get("finalDeliverable") != "EDITABLE_FAITHFUL_CLONE":
        raise ValueError("resuming Creative requires a completed editable faithful clone from choice B")
    decisions = state.get("reviewDecisions")
    if not isinstance(decisions, list) or not any(
        item.get("decision") == "B"
        and item.get("from") == "REVIEW_GATE"
        and item.get("to") == "COMPLETE"
        for item in decisions
        if isinstance(item, dict)
    ):
        raise ValueError("resuming Creative requires an accepted choice-B REVIEW_GATE decision")
    validate_editability_contract(workspace, root, state)


def validate_creative_brief(path: Path) -> None:
    text = require_nonempty_file(path, "CREATIVE_BRIEF.md")
    matches = list(re.finditer(r"^## (.+?)\s*$", text, re.MULTILINE))
    sections = {match.group(1): match for match in matches}
    missing = [name for name in CREATIVE_BRIEF_SECTIONS if name not in sections]
    if missing:
        raise ValueError(f"CREATIVE_BRIEF.md is missing sections: {', '.join(missing)}")
    for name in CREATIVE_BRIEF_SECTIONS:
        match = sections[name]
        next_start = min((item.start() for item in matches if item.start() > match.start()), default=len(text))
        if not text[match.end():next_start].strip():
            raise ValueError(f"CREATIVE_BRIEF.md section is empty: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--to", required=True, choices=sorted({phase for values in TRANSITIONS.values() for phase in values}))
    parser.add_argument("--decision", choices=sorted(REVIEW_DESTINATIONS))
    parser.add_argument("--final-deliverable", choices=tuple(DELIVERY_CONTRACTS))
    args = parser.parse_args()
    root = args.workspace.resolve() / ".gcw"
    state_path = root / "run-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    try:
        migrate_state(state)
    except ValueError as error:
        parser.error(str(error))
    current = state.get("currentPhase", state.get("state"))
    if args.final_deliverable is not None:
        if current not in {"TEARDOWN_PHASE", "FAITHFUL_CLONE"}:
            parser.error("--final-deliverable can only change the contract before REVIEW_GATE")
        apply_delivery_contract(
            state,
            args.final_deliverable,
            building=current == "FAITHFUL_CLONE" or args.to == "FAITHFUL_CLONE",
        )
    if args.to not in TRANSITIONS.get(current, set()):
        parser.error(f"invalid transition: {current} -> {args.to}")
    if current == "REVIEW_GATE":
        if args.decision is None:
            parser.error("leaving REVIEW_GATE requires --decision A, B, or C")
        expected = REVIEW_DESTINATIONS[args.decision]
        if args.to != expected:
            parser.error(f"review decision {args.decision} requires --to {expected}")
        if args.decision == "C":
            if state.get("finalDeliverable") == "EDITABLE_FAITHFUL_CLONE":
                apply_delivery_contract(state, "C", building=True)
            elif state.get("finalDeliverable") != "EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE":
                parser.error("review decision C requires an editable faithful choice B or C baseline")
    elif current == "COMPLETE" and args.to == "CREATIVE_REBUILD":
        if args.decision != "C":
            parser.error("resuming Creative from COMPLETE requires --decision C")
        try:
            validate_completed_b_resume(args.workspace.resolve(), root, state)
        except ValueError as error:
            parser.error(str(error))
        apply_delivery_contract(state, "C", building=True)
    elif args.decision is not None:
        parser.error("--decision is only valid when leaving REVIEW_GATE or resuming Creative from COMPLETE")
    if current == "TEARDOWN_PHASE":
        manifest_path = root / "teardown-manifest.json"
        if not manifest_path.is_file():
            parser.error("leaving TEARDOWN_PHASE requires teardown-manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "passed" or manifest.get("siteSpec", {}).get("status") != "final":
            parser.error("leaving TEARDOWN_PHASE requires scripts/finalize_teardown.py to pass")
        if args.to == "COMPLETE" and (
            state.get("finalDeliverable") in {
                "EDITABLE_FAITHFUL_CLONE",
                "EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE",
            }
            or state.get("editabilityTarget") == "MAINTAINABLE_SOURCE"
        ):
            parser.error("editable final deliverables must pass FAITHFUL_CLONE and REVIEW_GATE before COMPLETE")
        if args.to == "FAITHFUL_CLONE":
            try:
                validate_delivery_contract(state, require_build_confirmation=True)
            except ValueError as error:
                parser.error(str(error))
    if args.to == "REVIEW_GATE":
        try:
            validate_delivery_contract(state, require_build_confirmation=True)
            require_completed_file(root / "CLONE_REPORT.md", "CLONE_REPORT.md")
            validate_editability_contract(args.workspace.resolve(), root, state)
        except ValueError as error:
            parser.error(str(error))
    if current == "REVIEW_GATE" and args.decision in {"B", "C"}:
        try:
            validate_delivery_contract(state, require_build_confirmation=True)
            validate_editability_contract(args.workspace.resolve(), root, state)
        except ValueError as error:
            parser.error(str(error))
    if current == "CREATIVE_REBUILD" and args.to == "COMPLETE":
        try:
            validate_delivery_contract(state, require_build_confirmation=True)
            validate_editability_contract(args.workspace.resolve(), root, state)
        except ValueError as error:
            parser.error(str(error))
    if args.to == "CREATIVE_REBUILD":
        try:
            validate_creative_brief(root / "CREATIVE_BRIEF.md")
        except ValueError as error:
            parser.error(str(error))
    if current in {"REVIEW_GATE", "COMPLETE"}:
        decisions = state.setdefault("reviewDecisions", [])
        if not isinstance(decisions, list):
            parser.error("run-state.json reviewDecisions must be an array")
        decisions.append({
            "decision": args.decision,
            "from": current,
            "to": args.to,
            "recordedAt": datetime.now(timezone.utc).isoformat(),
        })
    state["currentPhase"] = args.to
    state["state"] = args.to
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"from": current, "to": args.to}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
