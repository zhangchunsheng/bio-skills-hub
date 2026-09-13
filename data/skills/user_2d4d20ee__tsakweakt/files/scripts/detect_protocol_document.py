#!/usr/bin/env python3
"""Detect a protocol artifact in a project manifest or artifact list."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

PROTOCOL_TYPES = {"study_protocol", "protocol", "research_protocol"}
SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".md", ".txt", ".json"}
NAME_HINTS = ("研究方案", "试验方案", "study protocol", "research protocol", "protocol")
INACTIVE_STATUSES = {"deleted", "archived", "superseded"}


def load_input() -> dict[str, Any]:
    raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    return json.loads(raw)


def score(artifact: dict[str, Any]) -> int:
    artifact_type = str(artifact.get("type", "")).lower()
    name = str(artifact.get("name") or artifact.get("path") or "").lower()
    extension = os.path.splitext(name)[1]
    value = 0
    if artifact_type in PROTOCOL_TYPES:
        value += 100
    if any(hint in name for hint in NAME_HINTS):
        value += 30
    if extension in SUPPORTED_EXTENSIONS:
        value += 10
    return value


def is_active(artifact: dict[str, Any]) -> bool:
    return str(artifact.get("status", "")).lower() not in INACTIVE_STATUSES


def detect(payload: dict[str, Any]) -> dict[str, Any]:
    artifacts = payload.get("artifacts") or payload.get("manifest", {}).get("artifacts") or []
    candidates = sorted(
        (a for a in artifacts if is_active(a) and score(a) >= 40),
        key=lambda a: (score(a), str(a.get("version", "")), str(a.get("updated_at", ""))),
        reverse=True,
    )
    if not candidates:
        return {"exists": False, "branch": "NO_PROTOCOL", "protocol_artifact_id": None, "document_path": None}
    selected = candidates[0]
    return {
        "exists": True,
        "branch": "HAS_PROTOCOL",
        "protocol_artifact_id": selected.get("id"),
        "document_path": selected.get("path"),
        "candidate_count": len(candidates),
        "selected_version": selected.get("version"),
        "selection_reason": "HIGHEST_SCORE_LATEST_ACTIVE_VERSION",
    }


if __name__ == "__main__":
    print(json.dumps(detect(load_input()), ensure_ascii=False, indent=2))
