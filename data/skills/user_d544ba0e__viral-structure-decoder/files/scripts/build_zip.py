#!/usr/bin/env python3
"""Build viral-structure-decoder zip."""
from __future__ import annotations

import zipfile
from pathlib import Path

VERSION = "1.4.0"
NAME = "viral-structure-decoder"
root = Path(__file__).resolve().parent.parent
dst = root.parent / f"{NAME}-{VERSION}.zip"

for p in root.rglob("*"):
    if p.is_file() and p.suffix.lower() in {".md", ".json", ".py"}:
        data = p.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            data = data[3:]
        text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        p.write_bytes(text.encode("utf-8"))

skill = (root / "SKILL.md").read_bytes()
assert skill.startswith(b"---\n"), skill[:12]
assert f"version: {VERSION}".encode() in skill

if dst.exists():
    dst.unlink()

with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name.startswith("."):
            continue
        arc = f"{NAME}/" + p.relative_to(root).as_posix()
        info = zipfile.ZipInfo(filename=arc)
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, p.read_bytes())

with zipfile.ZipFile(dst) as zf:
    assert zf.testzip() is None
    assert all(n.startswith(f"{NAME}/") for n in zf.namelist())
    assert zf.read(f"{NAME}/SKILL.md").startswith(b"---\n")
    print("OK", dst, dst.stat().st_size)
    for n in zf.namelist():
        print(" ", n)
