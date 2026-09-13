#!/usr/bin/env python3
"""Audit viral-structure-decoder package format."""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

VERSION = "1.4.0"
NAME = "viral-structure-decoder"
root = Path(__file__).resolve().parent.parent
zip_path = root.parent / f"{NAME}-{VERSION}.zip"
errors: list[str] = []
warns: list[str] = []

required = [
    "SKILL.md",
    "README.md",
    "examples/test-run.md",
    "examples/closed-loop-demo.md",
    "examples/closed-loop-quick.md",
    "examples/closed-loop-train.md",
    "examples/live-run-full.md",
    "examples/gold-run-review.md",
    "examples/review-checklist.md",
    "references/frameworks.md",
    "references/analysis-rules.md",
    "references/platform-playbooks.md",
    "references/failure-patterns.md",
    "references/table-field-safety.md",
    "templates/report.md",
    "scripts/validate_report.py",
    "scripts/build_zip.py",
    "scripts/audit_format.py",
    "assets/skill-meta.json",
]
for rel in required:
    if not (root / rel).is_file():
        errors.append(f"missing: {rel}")

for p in root.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in {".md", ".json", ".py"}:
        continue
    data = p.read_bytes()
    rel = p.relative_to(root).as_posix()
    if data.startswith(b"\xef\xbb\xbf"):
        errors.append(f"BOM: {rel}")
    if b"\r" in data:
        warns.append(f"CR: {rel}")
    if p.suffix.lower() == ".md":
        text = data.decode("utf-8", errors="replace")
        if re.search(r"评审|专家榜", text):
            errors.append(f"forbidden review text: {rel}")

skill_bytes = (root / "SKILL.md").read_bytes()
print("SKILL starts:", skill_bytes[:20])
if not skill_bytes.startswith(b"---\n"):
    errors.append("SKILL.md bad start")

text = skill_bytes.decode("utf-8")
m = re.match(r"---\n(.*?)\n---\n", text, re.S)
if not m:
    errors.append("frontmatter broken")
else:
    fm = m.group(1)
    if f"name: {NAME}" not in fm:
        errors.append("bad name")
    if "description:" not in fm:
        errors.append("no description")
    if f"version: {VERSION}" not in fm:
        warns.append("version mismatch fm")
    for line in fm.splitlines():
        if line.startswith("name:") and re.search(r"[\u4e00-\u9fff]", line):
            errors.append("Chinese in name")

for rel in ["SKILL.md", "README.md", "examples/test-run.md", "templates/report.md"]:
    p = root / rel
    if not p.exists():
        continue
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            inner = s.strip("|")
            if re.fullmatch(r"[\s\-:|]+", inner):
                continue
            for cell in inner.split("|"):
                if "<" in cell and "&lt;" not in cell and "＜" not in cell:
                    if "{{" in cell:
                        continue
                    warns.append(f"raw<:{rel}:{i}")

meta_path = root / "assets" / "skill-meta.json"
if meta_path.is_file():
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("name") != NAME or meta.get("entry") != "SKILL.md":
        errors.append("meta mismatch")
    if str(meta.get("version")) != VERSION:
        warns.append(f"meta ver {meta.get('version')}")
    if "judgingAligned" in meta:
        errors.append("skill-meta.json should not contain judgingAligned")

if not zip_path.is_file():
    errors.append(f"missing zip {zip_path.name}")
else:
    with zipfile.ZipFile(zip_path) as z:
        if z.testzip() is not None:
            errors.append("testzip fail")
        names = z.namelist()
        if any(not n.startswith(f"{NAME}/") for n in names):
            errors.append("zip root wrong")
        raw = z.read(f"{NAME}/SKILL.md")
        if raw.startswith(b"\xef\xbb\xbf") or not raw.startswith(b"---\n"):
            errors.append("zip SKILL bad")
        if f"version: {VERSION}".encode() not in raw:
            errors.append("zip version bad")

print("---")
print("ERRORS", len(errors))
for e in errors:
    print(" E:", e)
print("WARNS", len(warns))
for w in warns:
    print(" W:", w)
print("RESULT:", "OK" if not errors else "FAIL")
raise SystemExit(0 if not errors else 1)
