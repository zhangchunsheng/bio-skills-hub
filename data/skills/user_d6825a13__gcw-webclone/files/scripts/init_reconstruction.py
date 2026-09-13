#!/usr/bin/env python3
"""Create non-destructive GCW evidence scaffolding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from url_safety import validate_public_url, validate_relative_route


EVIDENCE_DIRS = (
    "screenshots/desktop",
    "screenshots/mobile",
    "network",
    "design-dna",
    "web-shader-extractor/evidence",
)

DELIVERY_CONTRACTS = {
    "A": ("RESEARCH_OR_RUNNABLE_REPLAY", "RUNNABLE_REPLAY"),
    "B": ("EDITABLE_FAITHFUL_CLONE", "MAINTAINABLE_SOURCE"),
    "C": ("EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE", "MAINTAINABLE_SOURCE"),
}


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--url", required=True)
    parser.add_argument("--route", action="append", default=[])
    parser.add_argument("--authorization", choices=("unconfirmed", "owned", "licensed", "authorized"), default="unconfirmed")
    parser.add_argument("--outcome", choices=("teardown", "faithful-clone", "creative-rebuild"), default="teardown")
    parser.add_argument("--final-deliverable", choices=tuple(DELIVERY_CONTRACTS))
    parser.add_argument("--site-type", default="unknown")
    parser.add_argument("--source-availability", choices=("unknown", "available", "unavailable", "damaged"), default="unknown")
    parser.add_argument("--baseline-scope", default="to-confirm")
    parser.add_argument("--implementation-path", choices=("", "SOURCE_ADAPT", "CLEAN_REBUILD", "PRODUCTION_RECOVERY"), default="")
    parser.add_argument("--teardown-depth", choices=("minimal", "standard", "deep"), default="standard")
    args = parser.parse_args()

    try:
        validate_public_url(args.url, "--url")
        for route in args.route:
            validate_relative_route(route, "--route")
    except ValueError as error:
        parser.error(str(error))
    if args.implementation_path == "PRODUCTION_RECOVERY" and (
        args.authorization == "unconfirmed" or args.source_availability not in {"unavailable", "damaged"}
    ):
        parser.error("PRODUCTION_RECOVERY requires confirmed authorization and unavailable or damaged source")
    build_requested = args.outcome != "teardown" or bool(args.implementation_path)
    if build_requested and args.final_deliverable is None:
        parser.error("build work requires --final-deliverable A, B, or C after asking the user")
    delivery_choice = args.final_deliverable or "A"
    if delivery_choice == "B" and args.outcome != "faithful-clone":
        parser.error("final deliverable B requires --outcome faithful-clone")
    if delivery_choice == "C" and args.outcome != "creative-rebuild":
        parser.error("final deliverable C requires --outcome creative-rebuild")
    if delivery_choice == "A" and args.outcome == "creative-rebuild":
        parser.error("creative-rebuild requires final deliverable C")
    final_deliverable, editability_target = DELIVERY_CONTRACTS[delivery_choice]
    parsed = urlparse(args.url)

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        parser.error(f"workspace does not exist: {workspace}")

    root = workspace / ".gcw"
    evidence = root / "evidence"
    for name in EVIDENCE_DIRS:
        (evidence / name).mkdir(parents=True, exist_ok=True)
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "config").mkdir(parents=True, exist_ok=True)

    routes = args.route or [parsed.path or "/"]
    state = {
        "schemaVersion": 5,
        "skill": "gcw",
        "sourceUrl": args.url,
        "permissionBoundary": args.authorization,
        "routes": routes,
        "outcome": args.outcome,
        "finalDeliverable": final_deliverable,
        "editabilityTarget": editability_target,
        "deliveryContractConfirmedForBuild": args.final_deliverable is not None,
        "currentPhase": "TEARDOWN_PHASE",
        "siteType": args.site_type,
        "ownershipAuthorization": args.authorization,
        "sourceAvailability": args.source_availability,
        "baselineScope": args.baseline_scope,
        "implementationPath": args.implementation_path,
        "teardownDepth": args.teardown_depth,
        "approximateOrExcludedScope": [],
        "conditionalGates": {
            "designDna": args.teardown_depth != "minimal",
            "gpuForensics": "required-when-canvas-webgl-webgpu-or-shaders-detected",
            "runtimeIndependence": editability_target == "MAINTAINABLE_SOURCE" or args.implementation_path == "CLEAN_REBUILD",
            "assetProvenance": "enable-when-asset-heavy-offline-or-maintained",
            "recovery": args.implementation_path == "PRODUCTION_RECOVERY",
        },
        "analysisGates": {
            "designDna": "pending",
            "gpuForensics": "pending-detection",
        },
        "reviewDecisions": [],
        "state": "TEARDOWN_PHASE",
        "gates": {
            "scope": False,
            "discovery": False,
            "targetLock": False,
            "replayReady": False,
            "baselineVerified": False,
            "projectVerified": False,
            "automationReady": False,
        },
        "cloneMode": "",  # v1.1 readers may still expect this key.
        "recoveryStrategy": "",
        "blockingUnknowns": [],
        "evidence": [],
    }

    skill_root = Path(__file__).resolve().parent.parent
    scenarios = json.loads((skill_root / "assets" / "capture-scenarios.example.json").read_text(encoding="utf-8"))
    scenarios["sourceUrl"] = args.url.rstrip("/")
    for scenario in scenarios["scenarios"]:
        scenario["route"] = routes[0]

    created = []
    files = {
        root / "run-state.json": json.dumps(state, indent=2) + "\n",
        root / "SITE_SPEC.md": (skill_root / "assets" / ("site-spec-minimal-template.md" if args.teardown_depth == "minimal" else "site-spec-template.md")).read_text(encoding="utf-8"),
        root / "CLONE_REPORT.md": (skill_root / "assets" / "clone-report-template.md").read_text(encoding="utf-8"),
        root / "REPLACE_GUIDE.md": (skill_root / "assets" / "replacement-map-template.md").read_text(encoding="utf-8"),
        root / "editability-evidence.json": (skill_root / "assets" / "editability-evidence.template.json").read_text(encoding="utf-8"),
        root / "teardown-manifest.json": (Path(__file__).resolve().parent.parent / "assets" / "teardown-manifest.template.json").read_text(encoding="utf-8"),
        evidence / "evidence-index.json": (Path(__file__).resolve().parent.parent / "assets" / "evidence-index.template.json").read_text(encoding="utf-8"),
        evidence / "web-shader-extractor" / "gpu-decision.json": (Path(__file__).resolve().parent.parent / "assets" / "gpu-decision.template.json").read_text(encoding="utf-8"),
        evidence / "site-inventory.json": "{}\n",
        evidence / "route-map.json": "{}\n",
        evidence / "interaction-states.json": json.dumps({"schemaVersion": 1, "states": []}, indent=2) + "\n",
        root / "known-gaps.md": "# Known gaps\n\n| Gap | Severity | Evidence | Impact | Next step |\n|---|---|---|---|---|\n",
        root / "qa-matrix.md": "# QA matrix\n\n| Scenario | Source | Candidate | Conditions | Result |\n|---|---|---|---|---|\n",
        root / "config" / "capture-scenarios.json": json.dumps(scenarios, indent=2) + "\n",
    }
    for path, content in files.items():
        if write_if_missing(path, content):
            created.append(str(path.relative_to(root)))

    print(json.dumps({"root": str(root), "created": created}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
