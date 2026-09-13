#!/usr/bin/env python3
"""Compare every GCW source/candidate screenshot pair and emit reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from image_diff import compare


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("--diff-dir", type=Path)
    parser.add_argument("--threshold", type=int, default=4)
    parser.add_argument("--max-changed-pct", type=float, default=1.0)
    parser.add_argument("--max-mean-abs", type=float, default=2.0)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-md", type=Path)
    args = parser.parse_args()
    if not 0 <= args.threshold <= 255:
        parser.error("--threshold must be between 0 and 255")
    if args.max_changed_pct < 0 or args.max_mean_abs < 0:
        parser.error("diff thresholds must be zero or greater")

    root = args.results_dir.resolve()
    diff_dir = (args.diff_dir or root / "diff").resolve()
    report_json = (args.report_json or root / "visual-diff-report.json").resolve()
    report_md = (args.report_md or root / "visual-diff-report.md").resolve()
    pairs = []
    failed = False

    for source_path in sorted(root.glob("*.source.png")):
        scenario = source_path.name.removesuffix(".source.png")
        candidate_path = root / f"{scenario}.candidate.png"
        if not candidate_path.exists():
            pairs.append({"scenario": scenario, "status": "failed", "error": "candidate image missing"})
            failed = True
            continue
        try:
            metrics = {"status": "measured", **compare(source_path, candidate_path, args.threshold, diff_dir / f"{scenario}.diff.png")}
        except (OSError, ValueError) as error:
            metrics = {"status": "failed", "error": str(error)}
        passed = (
            metrics.get("status") == "measured"
            and metrics["changedPct"] <= args.max_changed_pct
            and metrics["meanAbs"] <= args.max_mean_abs
        )
        metrics.update({
            "scenario": scenario,
            "source": source_path.name,
            "candidate": candidate_path.name,
            "diff": str((diff_dir / f"{scenario}.diff.png").relative_to(root)) if diff_dir.is_relative_to(root) else str(diff_dir / f"{scenario}.diff.png"),
            "passed": passed,
        })
        pairs.append(metrics)
        failed = failed or not passed

    if not pairs:
        parser.error(f"no *.source.png files found in {root}")

    report = {
        "schemaVersion": 1,
        "thresholds": {
            "pixelChannel": args.threshold,
            "maxChangedPct": args.max_changed_pct,
            "maxMeanAbs": args.max_mean_abs,
        },
        "passed": not failed,
        "scenarios": pairs,
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GCW visual diff report",
        "",
        f"Overall: **{'PASS' if not failed else 'FAIL'}**",
        "",
        "| Scenario | Changed > threshold | Mean abs | P95 | Result |",
        "|---|---:|---:|---:|---|",
    ]
    for item in pairs:
        if item.get("status") == "measured":
            lines.append(f"| {item['scenario']} | {item['changedPct']:.6f}% | {item['meanAbs']:.6f} | {item['p95ChannelDifference']} | {'PASS' if item['passed'] else 'FAIL'} |")
        else:
            lines.append(f"| {item['scenario']} | — | — | — | FAIL: {item.get('error', 'unknown')} |")
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"passed": not failed, "json": str(report_json), "markdown": str(report_md)}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
