#!/usr/bin/env python3
"""Install the self-contained GCW visual-regression harness into a project."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from url_safety import validate_public_url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    try:
        validate_public_url(args.source_url, "--source-url")
    except ValueError as error:
        parser.error(str(error))

    project = args.project.resolve()
    if not project.is_dir():
        parser.error(f"project directory does not exist: {project}")

    skill = Path(__file__).resolve().parent.parent
    files = {
        skill / "scripts" / "capture_compare.mjs": project / ".gcw" / "tools" / "capture_compare.mjs",
        skill / "scripts" / "url_safety.mjs": project / ".gcw" / "tools" / "url_safety.mjs",
        skill / "scripts" / "batch_image_diff.py": project / ".gcw" / "tools" / "batch_image_diff.py",
        skill / "scripts" / "route_smoke.py": project / ".gcw" / "tools" / "route_smoke.py",
        skill / "scripts" / "url_safety.py": project / ".gcw" / "tools" / "url_safety.py",
        skill / "scripts" / "check_runtime_independence.py": project / ".gcw" / "tools" / "check_runtime_independence.py",
        skill / "assets" / "gcw-package.json": project / ".gcw" / "package.json",
        skill / "assets" / "gcw-package-lock.json": project / ".gcw" / "package-lock.json",
        skill / "assets" / "gcw-requirements.txt": project / ".gcw" / "requirements.txt",
        skill / "assets" / "gcw-gitignore": project / ".gcw" / ".gitignore",
        skill / "assets" / "capture-scenarios.example.json": project / ".gcw" / "capture-scenarios.json",
        skill / "assets" / "github-workflows" / "gcw-visual-regression.yml": project / ".github" / "workflows" / "gcw-visual-regression.yml",
    }
    results = {}
    for source, target in files.items():
        if not source.exists():
            raise FileNotFoundError(source)
        existed = target.exists()
        if existed and not args.force:
            results[str(target.relative_to(project))] = "skipped"
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        results[str(target.relative_to(project))] = "updated" if existed else "created"

    scenario_path = project / ".gcw" / "capture-scenarios.json"
    if not scenario_path.exists() or results.get(str(scenario_path.relative_to(project))) != "skipped":
        config = json.loads(scenario_path.read_text(encoding="utf-8"))
        config["sourceUrl"] = args.source_url
        scenario_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "project": str(project),
        "files": results,
        "notes": ["The generated workflow assumes npm run build and npm run preview; adapt those steps for non-Vite projects."],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
