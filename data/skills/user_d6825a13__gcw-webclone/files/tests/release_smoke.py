#!/usr/bin/env python3
"""Release smoke tests for GCW's public command-line workflows."""

from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
NODE = "node"


def run(*args: str, expect: int = 0, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=ROOT,
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        source_map_header = None
        if self.path == "/redirect-external":
            self.send_response(302)
            self.send_header("Location", "http://127.0.0.1:65530/outside")
            self.end_headers()
            return
        if self.path == "/asset.bin":
            body = b"gcw-asset"
            content_type = "application/octet-stream"
        elif self.path == "/api/data":
            body = b'{"message":"fixture-data","token":"response-secret"}'
            content_type = "application/json"
        elif self.path.startswith("/asset.js.map"):
            body = b'{"version":3,"sources":["asset.ts"],"names":[],"mappings":""}'
            content_type = "application/json"
        elif self.path.startswith("/asset.js"):
            body = b"window.fixtureLoaded = true;\n//# sourceMappingURL=/asset.js.map?token=mapsecret"
            content_type = "text/javascript"
        elif self.path == "/styles.css.map":
            body = b'{"version":3,"sources":["styles.scss"],"names":[],"mappings":""}'
            content_type = "application/json"
        elif self.path == "/styles.css":
            body = b"body { color: white; }"
            content_type = "text/css"
            source_map_header = "/styles.css.map"
        elif self.path == "/invalid.css.map":
            body = b'{"version":3,"sources":[]}'
            content_type = "application/json"
        elif self.path == "/invalid.css":
            body = b"aside { display: block; }"
            content_type = "text/css"
            source_map_header = "/invalid.css.map"
        elif self.path == "/plain.css.map":
            body = b'{"version":3,"sources":["plain.scss"],"names":[],"mappings":""}'
            content_type = "application/json"
        elif self.path == "/plain.css":
            body = b"html { background: black; }"
            content_type = "text/css"
        elif self.path == "/missing.css":
            body = b"main { display: block; }"
            content_type = "text/css"
        elif self.path == "/spa":
            body = b"""<!doctype html><title>SPA fixture</title>
<body><div id='api-value'>loading</div><script>
fetch('/api/data', {headers: {Authorization: 'Bearer request-secret'}})
  .then(response => response.json())
  .then(data => { document.querySelector('#api-value').textContent = data.message; });
</script></body>"""
            content_type = "text/html"
        elif self.path == "/interactions":
            body = b"""<!doctype html><title>Interaction fixture</title>
<style>
#hover:hover { background-color: rgb(0, 255, 0); }
#focus:focus { outline: 4px solid rgb(0, 0, 255); }
#within:focus-within { background-color: rgb(255, 0, 255); }
#panel { display: none; }
#expand[aria-expanded='true'] + #panel { display: block; }
</style>
<button id='hover'>Hover me</button>
<input id='focus' value='Focus me'>
<div id='within'><input value='Nested focus'></div>
<button id='expand' aria-expanded='false'>Expand</button><div id='panel'>Panel open</div>
<script>
document.querySelector('#expand').addEventListener('click', event => {
  const button = event.currentTarget;
  button.setAttribute('aria-expanded', button.getAttribute('aria-expanded') === 'true' ? 'false' : 'true');
});
</script>"""
            content_type = "text/html"
        elif self.path == "/child":
            body = b"<!doctype html><title>Child</title><h1>Child route</h1>"
            content_type = "text/html"
        elif self.path == "/missing":
            self.send_error(404)
            return
        else:
            body = b"""<!doctype html>
<html><head><title>GCW fixture</title><link rel='stylesheet' href='/styles.css'><link rel='stylesheet' href='/invalid.css'><link rel='stylesheet' href='/plain.css'><link rel='stylesheet' href='/missing.css'><script src='/asset.js?x-amz-signature=topsecret'></script></head>
<body style='margin:0;background:#ff0000;min-height:100vh'><a href='/child'>Child</a>
<canvas id='unused'></canvas><canvas id='used'></canvas>
<script>
document.querySelector('#used').getContext('2d');
setTimeout(() => { document.body.style.background = '#00ff00'; }, 1000);
</script>
</body></html>"""
            content_type = "text/html"
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        if source_map_header:
            self.send_header("X-SourceMap", source_map_header)
        if self.path == "/api/data":
            self.send_header("Set-Cookie", "session=response-cookie-secret")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


class OfflineCandidateHandler(BaseHTTPRequestHandler):
    api_hits = 0

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path == "/api/data":
            type(self).api_hits += 1
            self.send_error(503)
            return
        body = b"""<!doctype html><title>Offline candidate</title>
<body><div id='api-value'>loading</div><script>
fetch('/api/data', {headers: {Authorization: 'Bearer request-secret'}})
  .then(response => response.json())
  .then(data => { document.querySelector('#api-value').textContent = data.message; })
  .catch(() => { document.querySelector('#api-value').textContent = 'offline'; });
</script></body>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


@contextmanager
def fixture_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@contextmanager
def offline_candidate_server():
    OfflineCandidateHandler.api_hits = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), OfflineCandidateHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def complete_teardown_artifacts(workspace: Path, gpu_required: bool = False) -> None:
    root = workspace / ".gcw"
    spec = root / "SITE_SPEC.md"
    spec_text = re.sub(r"<!-- REQUIRED.*?-->", "Completed from persisted evidence.", spec.read_text(encoding="utf-8"))
    spec_text = spec_text.replace(
        "| Completed from persisted evidence. | Exact / Approximate / Unknown / Excluded | SOURCE / PARTIAL / GUESS |  | yes / no |  |",
        "| Layout | Exact | SOURCE | evidence/site-inventory.json | no | Matches measured grid and breakpoints |",
    )
    spec.write_text(spec_text, encoding="utf-8")
    design = {
        "meta": {"name": "fixture"},
        "design_system": {"color": {"primary": "#000000"}},
        "design_style": {"aesthetic": {"mood": ["neutral"]}},
        "visual_effects": {"overview": {"effect_intensity": "none"}},
    }
    design_path = root / "evidence" / "design-dna" / "design-dna.json"
    design_path.write_text(json.dumps(design), encoding="utf-8")
    (root / "evidence" / "site-inventory.json").write_text(json.dumps({"fixture": True}), encoding="utf-8")
    (root / "evidence" / "route-map.json").write_text(json.dumps({"routes": [{"route": "/"}]}), encoding="utf-8")
    (root / "evidence" / "source-maps.json").write_text(json.dumps({"schemaVersion": 1, "resources": []}), encoding="utf-8")
    interaction_states = {
        "schemaVersion": 1,
        "states": [{
            "id": "home-stable",
            "route": "/",
            "trigger": "initial load",
            "expected": "stable home view",
            "evidence": ["screenshots/desktop/home.png"],
        }],
    }
    (root / "evidence" / "interaction-states.json").write_text(json.dumps(interaction_states), encoding="utf-8")
    Image.new("RGB", (8, 8), "#ffffff").save(root / "evidence" / "screenshots" / "desktop" / "home.png")
    Image.new("RGB", (8, 8), "#ffffff").save(root / "evidence" / "screenshots" / "mobile" / "home.png")
    (root / "evidence" / "network" / "requests.json").write_text(json.dumps({"requests": []}), encoding="utf-8")
    shader = root / "evidence" / "web-shader-extractor"
    if gpu_required:
        decision = {"schemaVersion": 1, "decision": "required", "checkedSurfaces": ["canvas#hero"], "detectionEvidence": ["evidence/site-inventory.json"]}
        scout = {"schemaVersion": 3, "lockStatus": "locked", "gateDecision": {"targetLocked": True}}
        replay = {"schemaVersion": 3, "unknowns": {"blocking": []}, "gateDecision": {"replayReady": True, "blockers": []}}
        (shader / "scout-card.json").write_text(json.dumps(scout), encoding="utf-8")
        (shader / "replay-manifest.json").write_text(json.dumps(replay), encoding="utf-8")
    else:
        decision = {"schemaVersion": 1, "decision": "not-applicable", "checkedSurfaces": ["main document and iframes"], "detectionEvidence": ["evidence/site-inventory.json"]}
    (shader / "gpu-decision.json").write_text(json.dumps(decision), encoding="utf-8")


def complete_clone_report(workspace: Path) -> None:
    report = workspace / ".gcw" / "CLONE_REPORT.md"
    text = report.read_text(encoding="utf-8")
    report.write_text(text.replace("REQUIRED", "Verified"), encoding="utf-8")


def complete_editability_evidence(workspace: Path) -> None:
    source = workspace / "src"
    reports = workspace / ".gcw" / "reports"
    source.mkdir(exist_ok=True)
    reports.mkdir(exist_ok=True)
    (source / "main.js").write_text("import './content.js';\n", encoding="utf-8")
    (source / "content.js").write_text("export const title = 'Original';\n", encoding="utf-8")
    (reports / "content-change.md").write_text("Controlled source edit rebuilt successfully.\n", encoding="utf-8")
    (reports / "runtime-independence.md").write_text("Network and build scans passed.\n", encoding="utf-8")
    replacement_map = workspace / ".gcw" / "REPLACE_GUIDE.md"
    replacement_map.write_text(
        "# Content replacement map\n\n| Content | Source path | Field | Validation |\n"
        "|---|---|---|---|\n| Hero title | src/content.js | title | Rebuild and inspect home |\n",
        encoding="utf-8",
    )
    evidence_path = workspace / ".gcw" / "editability-evidence.json"
    evidence = {
        "schemaVersion": 1,
        "reviewStatus": "confirmed",
        "maintainableSourceEntrypoint": "src/main.js",
        "contentReplacementMap": ".gcw/REPLACE_GUIDE.md",
        "controlledContentChange": {
            "sourceFile": "src/content.js",
            "field": "title",
            "beforeValue": "Original",
            "afterValue": "Controlled test",
            "buildCommand": "npm run build",
            "productionBundlesModified": False,
            "evidence": [".gcw/reports/content-change.md"],
        },
        "runtimeIndependence": {
            "status": "passed",
            "evidence": [".gcw/reports/runtime-independence.md"],
        },
        "artifactReplayRole": "oracle-only",
    }
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def complete_creative_brief(workspace: Path) -> None:
    brief = """# Creative brief

## Keep
Layout.
## Remove
Original branding.
## Change
Content.
## New brand, content, and features
New identity.
## Innovation direction
Editorial motion.
## Final acceptance target
Approved screenshots.
"""
    (workspace / ".gcw" / "CREATIVE_BRIEF.md").write_text(brief, encoding="utf-8")


def prepare_editable_review(workspace: Path) -> None:
    run(
        PYTHON, "scripts/init_reconstruction.py", str(workspace),
        "--url", "https://example.com/", "--outcome", "faithful-clone",
        "--final-deliverable", "B",
    )
    complete_teardown_artifacts(workspace)
    run(PYTHON, "scripts/finalize_teardown.py", str(workspace))
    run(PYTHON, "scripts/advance_workflow.py", str(workspace), "--to", "FAITHFUL_CLONE")
    complete_clone_report(workspace)
    complete_editability_evidence(workspace)
    run(PYTHON, "scripts/advance_workflow.py", str(workspace), "--to", "REVIEW_GATE")


class ReleaseSmokeTests(unittest.TestCase):
    def test_skill_and_package_contract(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\nname: gcw\n"))
        for reference in re.findall(r"`references/([^`]+\.md)`", skill):
            self.assertTrue((ROOT / "references" / reference).is_file(), reference)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('$gcw', metadata)
        short = re.search(r'^  short_description: "([^"]+)"$', metadata, re.M)
        self.assertIsNotNone(short)
        self.assertGreaterEqual(len(short.group(1)), 25)
        self.assertLessEqual(len(short.group(1)), 64)

        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        harness = json.loads((ROOT / "assets" / "gcw-package.json").read_text(encoding="utf-8"))
        harness_lock = json.loads((ROOT / "assets" / "gcw-package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(package["version"], lock["version"])
        self.assertEqual(package["dependencies"]["playwright"], harness["dependencies"]["playwright"])
        self.assertEqual(harness["dependencies"]["playwright"], harness_lock["packages"]["node_modules/playwright"]["version"])
        self.assertEqual(package["version"], "1.4.0")

        flow = "TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD"
        self.assertIn(flow, (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn(flow, (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        self.assertIn("## Evidence orchestration: the GCW difference", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("## 证据编排：GCW 的核心差异", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        self.assertIn("A screenshot is one frame. A live website is a million.", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("截图只有一帧。活的网站有千万帧。", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        self.assertIn("GCW stands for Gao Copy Website. Yes, the name is that literal.", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("GCW 就是 Gao Copy Website。对，名字就这么直白。", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        self.assertIn("SITE_SPEC.md", skill)
        self.assertIn("Stop at REVIEW_GATE", skill)
        self.assertIn("During every standard or deep `TEARDOWN_PHASE`, invoke `design-dna`", skill)
        self.assertIn("also invoke `web-shader-extractor`", skill)
        self.assertIn("Only after these decisions and calls are complete", skill)
        self.assertIn("If required `design-dna` is unavailable, stop", skill)
        self.assertIn("never infer or default it from a user profile", skill)
        self.assertIn("Final deliverable:", skill)
        self.assertIn("Editability target:", skill)
        self.assertIn("MAINTAINABLE_REBUILD", skill)
        self.assertIn("resume Creative from a completed B delivery", skill)
        for readme in (ROOT / "README.md", ROOT / "README.zh-CN.md"):
            content = readme.read_text(encoding="utf-8")
            self.assertIn("Final deliverable", content)
            self.assertIn("Editability target", content)
            self.assertIn("MAINTAINABLE_REBUILD", content)
        self.assertIn("resume Creative later", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("以后仍可升级到 C", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        for asset in (
            "site-spec-template.md", "site-spec-minimal-template.md", "creative-brief-template.md", "asset-manifest.example.json",
            "clone-report-template.md", "replacement-map-template.md", "editability-evidence.template.json",
            "teardown-manifest.template.json", "evidence-index.template.json", "gpu-decision.template.json",
        ):
            self.assertTrue((ROOT / "assets" / asset).is_file(), asset)

        workflows = [ROOT / ".github" / "workflows" / "ci.yml", ROOT / "assets" / "github-workflows" / "gcw-visual-regression.yml"]
        for workflow in workflows:
            content = workflow.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"uses:\s+[^\s#]+@v\d+", content), workflow)
            self.assertIn("actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0", content)
            self.assertIn("actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e", content)
            self.assertIn("actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1", content)
        self.assertIn("actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a", workflows[1].read_text(encoding="utf-8"))
        installed_workflow = workflows[1].read_text(encoding="utf-8")
        self.assertIn("cd .gcw\n          npx playwright install", installed_workflow)
        self.assertNotIn("npx --prefix .gcw", installed_workflow)
        project_ci = workflows[0].read_text(encoding="utf-8")
        self.assertIn("os: [ubuntu-latest, windows-latest, macos-latest]", project_ci)
        self.assertIn("runner.os == 'macOS'", project_ci)

        environment = json.loads(run(NODE, "scripts/check_environment.mjs").stdout)
        self.assertIn("teardownReady", environment)
        self.assertIn("teardownRequirements", environment)
        self.assertNotIn("companionSkills", environment["optional"])

    def test_init_is_non_destructive_and_rejects_secret_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            state_path = Path(temp) / ".gcw" / "run-state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["schemaVersion"], 5)
            self.assertIn("cloneMode", state)
            self.assertEqual(state["permissionBoundary"], "unconfirmed")
            self.assertEqual(state["currentPhase"], "TEARDOWN_PHASE")
            self.assertEqual(state["outcome"], "teardown")
            self.assertEqual(state["finalDeliverable"], "RESEARCH_OR_RUNNABLE_REPLAY")
            self.assertEqual(state["editabilityTarget"], "RUNNABLE_REPLAY")
            self.assertFalse(state["deliveryContractConfirmedForBuild"])
            self.assertEqual(state["teardownDepth"], "standard")
            self.assertEqual(state["reviewDecisions"], [])
            self.assertEqual(state["conditionalGates"]["assetProvenance"], "enable-when-asset-heavy-offline-or-maintained")
            self.assertTrue(state["conditionalGates"]["designDna"])
            self.assertEqual(state["conditionalGates"]["gpuForensics"], "required-when-canvas-webgl-webgpu-or-shaders-detected")
            gcw = Path(temp) / ".gcw"
            self.assertTrue((gcw / "SITE_SPEC.md").is_file())
            self.assertTrue((gcw / "CLONE_REPORT.md").is_file())
            self.assertTrue((gcw / "REPLACE_GUIDE.md").is_file())
            self.assertTrue((gcw / "editability-evidence.json").is_file())
            self.assertTrue((gcw / "teardown-manifest.json").is_file())
            self.assertTrue((gcw / "evidence" / "evidence-index.json").is_file())
            self.assertTrue((gcw / "evidence" / "screenshots" / "desktop").is_dir())
            self.assertTrue((gcw / "evidence" / "design-dna").is_dir())
            self.assertTrue((gcw / "evidence" / "web-shader-extractor" / "gpu-decision.json").is_file())
            for name in ("site-inventory.json", "route-map.json", "interaction-states.json"):
                self.assertTrue((gcw / "evidence" / name).is_file())
            scenarios = json.loads((gcw / "config" / "capture-scenarios.json").read_text(encoding="utf-8"))
            self.assertEqual(len(scenarios["scenarios"]), 2)
            self.assertTrue(all(item["colorScheme"] == "light" for item in scenarios["scenarios"]))
            state_path.write_text('{"preserved": true}\n', encoding="utf-8")
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), {"preserved": True})
            rejected = run(
                PYTHON,
                "scripts/init_reconstruction.py",
                temp,
                "--url",
                "https://example.com/?token=secret",
                expect=2,
            )
            self.assertIn("credential-like", rejected.stderr)
            recovery = run(
                PYTHON, "scripts/init_reconstruction.py", temp,
                "--url", "https://example.com/", "--implementation-path", "PRODUCTION_RECOVERY",
                expect=2,
            )
            self.assertIn("requires confirmed authorization", recovery.stderr)

            missing_contract = run(
                PYTHON, "scripts/init_reconstruction.py", temp,
                "--url", "https://example.com/", "--outcome", "faithful-clone",
                expect=2,
            )
            self.assertIn("requires --final-deliverable A, B, or C", missing_contract.stderr)

        with tempfile.TemporaryDirectory() as temp:
            run(
                PYTHON, "scripts/init_reconstruction.py", temp,
                "--url", "https://example.com/", "--outcome", "faithful-clone",
                "--final-deliverable", "B",
            )
            state = json.loads((Path(temp) / ".gcw" / "run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["finalDeliverable"], "EDITABLE_FAITHFUL_CLONE")
            self.assertEqual(state["editabilityTarget"], "MAINTAINABLE_SOURCE")
            self.assertTrue(state["deliveryContractConfirmedForBuild"])
            self.assertTrue(state["conditionalGates"]["runtimeIndependence"])

    def test_build_transition_requires_explicit_delivery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace)
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            blocked = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "FAITHFUL_CLONE", expect=2)
            self.assertIn("explicitly confirmed final deliverable", blocked.stderr)
            run(
                PYTHON, "scripts/advance_workflow.py", temp,
                "--to", "FAITHFUL_CLONE", "--final-deliverable", "A",
            )
            state = json.loads((workspace / ".gcw" / "run-state.json").read_text(encoding="utf-8"))
            self.assertTrue(state["deliveryContractConfirmedForBuild"])
            self.assertEqual(state["deliveryContractHistory"][-1]["choice"], "A")

    def test_ci_installer_is_reproducible_and_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            installed = run(PYTHON, "scripts/install_ci.py", temp, "--source-url", "https://example.com/")
            self.assertIn("non-Vite projects", installed.stdout)
            package = json.loads((project / ".gcw" / "package.json").read_text(encoding="utf-8"))
            lock = json.loads((project / ".gcw" / "package-lock.json").read_text(encoding="utf-8"))
            self.assertEqual(package["dependencies"]["playwright"], "1.61.1")
            self.assertEqual(lock["packages"]["node_modules/playwright"]["version"], "1.61.1")
            self.assertTrue((project / ".gcw" / "tools" / "url_safety.mjs").exists())
            self.assertTrue((project / ".gcw" / "tools" / "url_safety.py").exists())
            self.assertTrue((project / ".gcw" / "tools" / "check_runtime_independence.py").exists())
            self.assertEqual((project / ".gcw" / "requirements.txt").read_text(encoding="utf-8").strip(), "Pillow==12.2.0")
            run(PYTHON, str(project / ".gcw" / "tools" / "route_smoke.py"), "--help")
            copied_capture = run(NODE, str(project / ".gcw" / "tools" / "capture_compare.mjs"), expect=1)
            self.assertIn("Usage: capture_compare.mjs", copied_capture.stderr)
            scenario = project / ".gcw" / "capture-scenarios.json"
            scenario.write_text('{"preserved": true}\n', encoding="utf-8")
            run(PYTHON, "scripts/install_ci.py", temp, "--source-url", "https://example.com/")
            self.assertEqual(json.loads(scenario.read_text(encoding="utf-8")), {"preserved": True})

    def test_route_smoke_stays_on_base_origin(self) -> None:
        with fixture_server() as base:
            run(PYTHON, "scripts/route_smoke.py", "--base-url", base, "--route", "/", "--route", "/child")
            rejected = run(
                PYTHON,
                "scripts/route_smoke.py",
                "--base-url",
                base,
                "--route",
                "https://example.com/",
                expect=2,
            )
            self.assertIn("stay on the configured origin", rejected.stderr)
            redirected = run(
                PYTHON,
                "scripts/route_smoke.py",
                "--base-url",
                base,
                "--route",
                "/redirect-external",
                expect=1,
            )
            self.assertIn("redirect left the base origin", redirected.stdout)

    def test_inventory_crawls_routes_and_redacts_resource_secrets(self) -> None:
        with fixture_server() as base, tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "inventory.json"
            run(NODE, "scripts/site_inventory.mjs", "--url", base, "--out", str(out), "--settle-ms", "0", "--viewport", "390x844")
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["limits"]["viewport"], {"width": 390, "height": 844})
            self.assertEqual({item["route"] for item in report["routes"]}, {"/", "/child"})
            serialized = json.dumps(report)
            self.assertNotIn("topsecret", serialized)
            self.assertIn("REDACTED", serialized)
            canvases = report["routes"][0]["surface"]["canvases"]
            self.assertEqual([canvas["context"] for canvas in canvases], ["unknown", "2d"])
            route_map = json.loads((Path(temp) / "route-map.json").read_text(encoding="utf-8"))
            self.assertEqual({item["route"] for item in route_map["routes"]}, {"/", "/child"})
            network = json.loads((Path(temp) / "network" / "requests.json").read_text(encoding="utf-8"))
            self.assertTrue(any(item["url"].endswith("/asset.js?x-amz-signature=REDACTED") for item in network["requests"]))
            source_maps = json.loads((Path(temp) / "source-maps.json").read_text(encoding="utf-8"))
            self.assertEqual(source_maps["schemaVersion"], 1)
            script = next(item for item in source_maps["resources"] if "/asset.js?" in item["resourceUrl"])
            self.assertEqual(script["directive"], "sourceMappingURL")
            self.assertEqual(script["mapUrl"], f"{base}/asset.js.map?token=REDACTED")
            self.assertEqual(script["status"], 200)
            self.assertTrue(script["validSourceMap"])
            stylesheet = next(item for item in source_maps["resources"] if item["resourceUrl"].endswith("/styles.css"))
            self.assertEqual(stylesheet["directive"], "X-SourceMap")
            self.assertEqual(stylesheet["mapUrl"], f"{base}/styles.css.map")
            self.assertEqual(stylesheet["status"], 200)
            self.assertTrue(stylesheet["validSourceMap"])
            conventional = next(item for item in source_maps["resources"] if item["resourceUrl"].endswith("/plain.css"))
            self.assertIsNone(conventional["directive"])
            self.assertEqual(conventional["mapUrl"], f"{base}/plain.css.map")
            self.assertTrue(conventional["accessible"])
            missing = next(item for item in source_maps["resources"] if item["resourceUrl"].endswith("/missing.css"))
            self.assertEqual(missing["status"], 200)
            self.assertTrue(missing["reachable"])
            self.assertFalse(missing["validSourceMap"])
            self.assertFalse(missing["accessible"])
            self.assertIn("valid Source Map", missing["validationError"])
            invalid = next(item for item in source_maps["resources"] if item["resourceUrl"].endswith("/invalid.css"))
            self.assertFalse(invalid["validSourceMap"])
            self.assertIn("valid Source Map v3 object", invalid["validationError"])
            self.assertNotIn("mapsecret", json.dumps(source_maps))

            bounded = Path(temp) / "bounded.json"
            run(
                NODE, "scripts/site_inventory.mjs", "--url", base, "--out", str(bounded),
                "--settle-ms", "0", "--source-map-max-bytes", "32",
            )
            bounded_maps = json.loads((Path(temp) / "source-maps.json").read_text(encoding="utf-8"))
            bounded_script = next(item for item in bounded_maps["resources"] if "/asset.js?" in item["resourceUrl"])
            self.assertFalse(bounded_script["validSourceMap"])
            self.assertIn("exceeds", bounded_script["validationError"])

            redirected = Path(temp) / "redirected.json"
            run(NODE, "scripts/site_inventory.mjs", "--url", f"{base}/redirect-external", "--out", str(redirected), "--settle-ms", "0")
            redirect_report = json.loads(redirected.read_text(encoding="utf-8"))
            self.assertIn("redirect left the allowed origin", redirect_report["routes"][0]["error"])

    def test_capture_applies_phase_and_rejects_filename_collisions(self) -> None:
        with fixture_server() as base, tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = {
                "sourceUrl": base,
                "candidateUrl": base,
                "seed": 7,
                "harFixture": {"urlFilter": "**/api/**"},
                "scenarios": [
                    {
                        "id": "phase",
                        "route": "/",
                        "viewport": {"width": 64, "height": 64},
                        "clockMode": "controlled",
                        "readyFunction": "document.readyState === 'complete'",
                        "readyDelayMs": 0,
                        "phaseMs": 1200,
                        "afterInputDelayMs": 0,
                    }
                ],
            }
            config_path = root / "capture.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            output = root / "results"
            run(NODE, "scripts/capture_compare.mjs", "--config", str(config_path), "--output", str(output))
            manifest = json.loads((output / "capture-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["captures"][0]["timing"]["phaseMs"], 1200)
            self.assertNotIn("harFixtures", manifest)
            pixel = Image.open(output / "phase.source.png").convert("RGB").getpixel((32, 32))
            self.assertGreater(pixel[1], 200)
            self.assertLess(pixel[0], 30)

            config["scenarios"] = [
                {"id": "same id", "route": "/", "readyFunction": "true"},
                {"id": "same-id", "route": "/", "readyFunction": "true"},
            ]
            config_path.write_text(json.dumps(config), encoding="utf-8")
            rejected = run(
                NODE,
                "scripts/capture_compare.mjs",
                "--config",
                str(config_path),
                "--output",
                str(root / "collision"),
                expect=1,
            )
            self.assertIn("id collision", rejected.stderr)

    def test_har_fixture_recording_is_opt_in_redacted_and_replays_offline(self) -> None:
        with offline_candidate_server() as candidate, tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            har_dir = root / "har"
            config_path = root / "capture.json"
            with fixture_server() as source:
                config = {
                    "sourceUrl": source,
                    "candidateUrl": candidate,
                    "harFixture": {"urlFilter": "**/api/**"},
                    "scenarios": [{"id": "spa", "route": "/spa", "readyFunction": "true", "afterInputDelayMs": 0}],
                }
                config_path.write_text(json.dumps(config), encoding="utf-8")
                run(
                    NODE, "scripts/capture_compare.mjs", "--config", str(config_path),
                    "--output", str(root / "record"), "--record-har", str(har_dir),
                )

            har_path = har_dir / "spa.har"
            self.assertTrue(har_path.is_file())
            self.assertFalse((har_dir / "spa.raw.har").exists())
            har_text = har_path.read_text(encoding="utf-8")
            self.assertNotIn("request-secret", har_text)
            self.assertNotIn("response-secret", har_text)
            self.assertNotIn("response-cookie-secret", har_text)
            self.assertNotIn(source, har_text)
            self.assertIn(candidate, har_text)
            self.assertIn("REDACTED", har_text)

            config.update({"sourceUrl": candidate, "candidateUrl": candidate})
            config["scenarios"][0]["readyFunction"] = "document.querySelector('#api-value')?.textContent === 'fixture-data'"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            OfflineCandidateHandler.api_hits = 0
            replay = run(
                NODE, "scripts/capture_compare.mjs", "--config", str(config_path),
                "--output", str(root / "replay"), "--replay-har", str(har_dir),
            )
            self.assertEqual(OfflineCandidateHandler.api_hits, 0)
            self.assertIn('"harMode": "replay"', replay.stdout)
            manifest = json.loads((root / "replay" / "capture-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["harFixtures"]["mode"], "replay")
            self.assertEqual(manifest["harFixtures"]["blockedRequests"], [])
            self.assertFalse(any("/api/data" in item["url"] for item in manifest["harFixtures"]["fallbacks"]))

            build = root / "dist"
            build.mkdir()
            (build / "index.js").write_text("const local = true;", encoding="utf-8")
            run(
                PYTHON, "scripts/check_runtime_independence.py", str(har_path),
                "--source-url", source, "--build-dir", str(build),
            )

    def test_har_fixture_flags_are_explicit_and_mutually_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "capture.json"
            config.write_text(json.dumps({"sourceUrl": "https://example.com", "candidateUrl": "https://example.com", "scenarios": [{"id": "one", "readyFunction": "true"}]}), encoding="utf-8")
            rejected = run(
                NODE, "scripts/capture_compare.mjs", "--config", str(config), "--output", str(Path(temp) / "out"),
                "--record-har", str(Path(temp) / "record"), "--replay-har", str(Path(temp) / "replay"), expect=1,
            )
            self.assertIn("mutually exclusive", rejected.stderr)

    def test_interaction_state_detection_records_reviewable_browser_evidence(self) -> None:
        with fixture_server() as base, tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp) / ".gcw" / "evidence"
            out = evidence / "interaction-states.json"
            run(
                NODE, "scripts/detect_interaction_states.mjs",
                "--url", f"{base}/interactions", "--out", str(out),
                "--settle-ms", "0", "--max-per-trigger", "2",
            )
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["schemaVersion"], 1)
            self.assertEqual(report["reviewStatus"], "pending")
            self.assertEqual({state["triggerType"] for state in report["states"]}, {"hover", "focus", "aria-expanded"})
            self.assertNotIn("#within", {state["elementSelector"] for state in report["states"]})
            self.assertEqual(report["qa"], {"consoleErrors": [], "httpErrors": []})
            for state in report["states"]:
                self.assertEqual(len(state["evidence"]), 2)
                self.assertTrue(state["before"])
                self.assertTrue(state["after"])
                for relative in state["evidence"]:
                    image_path = evidence / relative
                    self.assertTrue(image_path.is_file(), relative)
                    with Image.open(image_path) as image:
                        image.verify()

    def test_teardown_rejects_pending_generated_interaction_states(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace)
            states_path = workspace / ".gcw" / "evidence" / "interaction-states.json"
            states = json.loads(states_path.read_text(encoding="utf-8"))
            states["reviewStatus"] = "pending"
            states_path.write_text(json.dumps(states), encoding="utf-8")
            blocked = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
            self.assertIn("reviewStatus must be confirmed", blocked.stderr)
            states["reviewStatus"] = "confirmed"
            states_path.write_text(json.dumps(states), encoding="utf-8")
            run(PYTHON, "scripts/finalize_teardown.py", temp)

    def test_image_diff_threshold_validation_and_batch_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sample.source.png"
            candidate = root / "sample.candidate.png"
            Image.new("RGB", (8, 8), "#000000").save(source)
            Image.new("RGB", (8, 8), "#000000").save(candidate)
            run(PYTHON, "scripts/batch_image_diff.py", temp)
            report = json.loads((root / "visual-diff-report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["passed"])
            invalid = run(PYTHON, "scripts/image_diff.py", str(source), str(candidate), "--threshold", "256", expect=2)
            self.assertIn("between 0 and 255", invalid.stderr)

    def test_workflow_requires_review_gate_before_creative(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run(
                PYTHON, "scripts/init_reconstruction.py", temp,
                "--url", "https://example.com/", "--outcome", "creative-rebuild",
                "--final-deliverable", "C",
            )
            invalid = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "CREATIVE_REBUILD", expect=2)
            self.assertIn("invalid transition", invalid.stderr)
            incomplete_study = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "COMPLETE", expect=2)
            self.assertIn("finalize_teardown.py to pass", incomplete_study.stderr)
            missing_analysis = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "FAITHFUL_CLONE", expect=2)
            self.assertIn("finalize_teardown.py to pass", missing_analysis.stderr)
            complete_teardown_artifacts(Path(temp))
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "FAITHFUL_CLONE")
            missing_report = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "REVIEW_GATE", expect=2)
            self.assertIn("CLONE_REPORT.md", missing_report.stderr)
            complete_clone_report(Path(temp))
            incomplete_editability = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "REVIEW_GATE", expect=2)
            self.assertIn("editability-evidence.json reviewStatus must be confirmed", incomplete_editability.stderr)
            complete_editability_evidence(Path(temp))
            run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "REVIEW_GATE")
            mismatched_decision = run(
                PYTHON, "scripts/advance_workflow.py", temp,
                "--to", "CREATIVE_REBUILD", "--decision", "A", expect=2,
            )
            self.assertIn("requires --to FAITHFUL_CLONE", mismatched_decision.stderr)
            missing_decision = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "CREATIVE_REBUILD", expect=2)
            self.assertIn("--decision", missing_decision.stderr)
            missing_brief = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "CREATIVE_REBUILD", "--decision", "C", expect=2)
            self.assertIn("CREATIVE_BRIEF.md", missing_brief.stderr)
            complete_creative_brief(Path(temp))
            run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "CREATIVE_REBUILD", "--decision", "C")
            state = json.loads((Path(temp) / ".gcw" / "run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["reviewDecisions"][-1]["decision"], "C")
            self.assertEqual(state["analysisGates"], {"designDna": "complete", "gpuForensics": "not-applicable", "teardown": "passed"})
            manifest = json.loads((Path(temp) / ".gcw" / "teardown-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "passed")
            evidence_index = json.loads((Path(temp) / ".gcw" / "evidence" / "evidence-index.json").read_text(encoding="utf-8"))
            self.assertTrue({"design-dna", "gpu-decision", "site-spec", "site-inventory", "route-map", "source-maps", "interaction-states"}.issubset({entry["kind"] for entry in evidence_index["entries"]}))
            design_entry = next(entry for entry in evidence_index["entries"] if entry["kind"] == "design-dna")
            self.assertEqual(design_entry["schemaContract"], "three-dimension-v1")
            state_path = Path(temp) / ".gcw" / "run-state.json"
            state["recoveryStrategy"] = "ARTIFACT_REPLAY"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            blocked_closeout = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "COMPLETE", expect=2)
            self.assertIn("ARTIFACT_REPLAY is oracle-only", blocked_closeout.stderr)

    def test_editable_b_can_upgrade_to_c_at_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            prepare_editable_review(workspace)
            complete_creative_brief(workspace)
            run(
                PYTHON, "scripts/advance_workflow.py", temp,
                "--to", "CREATIVE_REBUILD", "--decision", "C",
            )
            state = json.loads((workspace / ".gcw" / "run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["currentPhase"], "CREATIVE_REBUILD")
            self.assertEqual(state["finalDeliverable"], "EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE")
            self.assertEqual(state["outcome"], "creative-rebuild")
            self.assertEqual(state["deliveryContractHistory"][-1]["choice"], "C")
            self.assertEqual(state["deliveryContractHistory"][-1]["previous"]["finalDeliverable"], "EDITABLE_FAITHFUL_CLONE")

    def test_completed_b_can_resume_creative_but_a_cannot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            prepare_editable_review(workspace)
            run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "COMPLETE", "--decision", "B")
            missing_brief = run(
                PYTHON, "scripts/advance_workflow.py", temp,
                "--to", "CREATIVE_REBUILD", "--decision", "C", expect=2,
            )
            self.assertIn("CREATIVE_BRIEF.md", missing_brief.stderr)
            complete_creative_brief(workspace)
            run(
                PYTHON, "scripts/advance_workflow.py", temp,
                "--to", "CREATIVE_REBUILD", "--decision", "C",
            )
            state = json.loads((workspace / ".gcw" / "run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["currentPhase"], "CREATIVE_REBUILD")
            self.assertEqual(state["reviewDecisions"][-1]["from"], "COMPLETE")
            self.assertEqual(state["reviewDecisions"][-1]["decision"], "C")

        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace)
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            run(
                PYTHON, "scripts/advance_workflow.py", temp,
                "--to", "COMPLETE", "--final-deliverable", "A",
            )
            complete_creative_brief(workspace)
            blocked = run(
                PYTHON, "scripts/advance_workflow.py", temp,
                "--to", "CREATIVE_REBUILD", "--decision", "C", expect=2,
            )
            self.assertIn("completed editable faithful clone", blocked.stderr)

    def test_editable_delivery_blocks_artifact_only_replay_and_migrates_legacy_strategy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(
                PYTHON, "scripts/init_reconstruction.py", temp,
                "--url", "https://example.com/", "--outcome", "faithful-clone",
                "--final-deliverable", "B",
            )
            complete_teardown_artifacts(workspace)
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            direct_complete = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "COMPLETE", expect=2)
            self.assertIn("must pass FAITHFUL_CLONE and REVIEW_GATE", direct_complete.stderr)
            run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "FAITHFUL_CLONE")
            complete_clone_report(workspace)
            complete_editability_evidence(workspace)

            state_path = workspace / ".gcw" / "run-state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["editabilityTarget"] = "RUNNABLE_REPLAY"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            mismatched = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "REVIEW_GATE", expect=2)
            self.assertIn("delivery contract mismatch", mismatched.stderr)

            state["editabilityTarget"] = "MAINTAINABLE_SOURCE"
            state["schemaVersion"] = 4
            state["recoveryStrategy"] = "ARTIFACT_REPLAY"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            blocked = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "REVIEW_GATE", expect=2)
            self.assertIn("ARTIFACT_REPLAY is oracle-only", blocked.stderr)

            state["recoveryStrategy"] = "EDITABLE_REBUILD"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            editability_path = workspace / ".gcw" / "editability-evidence.json"
            editability = json.loads(editability_path.read_text(encoding="utf-8"))
            editability["runtimeIndependence"]["status"] = "pending"
            editability_path.write_text(json.dumps(editability), encoding="utf-8")
            blocked_runtime = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "REVIEW_GATE", expect=2)
            self.assertIn("runtimeIndependence.status must be passed", blocked_runtime.stderr)

            editability["runtimeIndependence"]["status"] = "passed"
            editability_path.write_text(json.dumps(editability), encoding="utf-8")
            run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "REVIEW_GATE")
            migrated = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(migrated["schemaVersion"], 5)
            self.assertEqual(migrated["recoveryStrategy"], "MAINTAINABLE_REBUILD")
            self.assertEqual(migrated["stateMigrations"][-1]["from"], "EDITABLE_REBUILD")

            migrated["recoveryStrategy"] = "ARTIFACT_REPLAY"
            state_path.write_text(json.dumps(migrated), encoding="utf-8")
            blocked_closeout = run(
                PYTHON, "scripts/advance_workflow.py", temp,
                "--to", "COMPLETE", "--decision", "B", expect=2,
            )
            self.assertIn("ARTIFACT_REPLAY is oracle-only", blocked_closeout.stderr)

    def test_gpu_teardown_requires_target_lock_and_replay_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace, gpu_required=True)
            scout_path = workspace / ".gcw" / "evidence" / "web-shader-extractor" / "scout-card.json"
            scout = json.loads(scout_path.read_text(encoding="utf-8"))
            scout["lockStatus"] = "provisional"
            scout_path.write_text(json.dumps(scout), encoding="utf-8")
            blocked = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
            self.assertIn("TARGET_LOCKED", blocked.stderr)
            scout["lockStatus"] = "locked"
            scout["schemaVersion"] = 4
            scout_path.write_text(json.dumps(scout), encoding="utf-8")
            drifted = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
            self.assertIn("schema drift", drifted.stderr)
            scout["schemaVersion"] = 3
            scout_path.write_text(json.dumps(scout), encoding="utf-8")
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            manifest = json.loads((workspace / ".gcw" / "teardown-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["gpuAnalysis"]["status"], "replay-ready")
            index = json.loads((workspace / ".gcw" / "evidence" / "evidence-index.json").read_text(encoding="utf-8"))
            shader_entries = [entry for entry in index["entries"] if entry["sourceSkill"] == "web-shader-extractor"]
            self.assertTrue(shader_entries)
            self.assertTrue(all(entry["schemaVersion"] == 3 for entry in shader_entries))

    def test_teardown_rejects_invalid_truth_fidelity_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace)
            spec_path = workspace / ".gcw" / "SITE_SPEC.md"
            valid_spec = spec_path.read_text(encoding="utf-8")
            cases = (
                ("| Exact | SOURCE |", "| Similar | SOURCE |", "invalid Fidelity"),
                ("| Exact | SOURCE |", "| Exact | CERTAIN |", "invalid Truth"),
                ("| no | Matches measured", "| maybe | Matches measured", "invalid Blocking"),
                ("| evidence/site-inventory.json |", "|  |", "requires Evidence and Acceptance"),
                ("| Matches measured grid and breakpoints |", "|  |", "requires Evidence and Acceptance"),
            )
            for old, new, message in cases:
                spec_path.write_text(valid_spec.replace(old, new), encoding="utf-8")
                blocked = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
                self.assertIn(message, blocked.stderr)
            spec_path.write_text(valid_spec, encoding="utf-8")
            run(PYTHON, "scripts/finalize_teardown.py", temp)

    def test_teardown_validation_failure_does_not_finalize_site_spec(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace)
            index_path = workspace / ".gcw" / "evidence" / "evidence-index.json"
            index_path.write_text("not json", encoding="utf-8")
            blocked = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
            self.assertIn("invalid JSON artifact", blocked.stderr)
            spec = (workspace / ".gcw" / "SITE_SPEC.md").read_text(encoding="utf-8")
            self.assertIn("Status: DRAFT", spec)
            self.assertNotIn("Status: FINAL", spec)

    def test_teardown_rejects_invalid_screenshot_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace)
            (workspace / ".gcw" / "evidence" / "screenshots" / "desktop" / "home.png").write_bytes(b"not-an-image")
            blocked = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
            self.assertIn("invalid screenshot image", blocked.stderr)

    def test_minimal_teardown_uses_reduced_spec_and_optional_design_dna(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(
                PYTHON, "scripts/init_reconstruction.py", temp,
                "--url", "https://example.com/", "--teardown-depth", "minimal",
            )
            complete_teardown_artifacts(workspace)
            root = workspace / ".gcw"
            spec = root / "SITE_SPEC.md"
            text = re.sub(r"<!-- REQUIRED.*?-->", "Completed from persisted evidence.", spec.read_text(encoding="utf-8"))
            text = text.replace(
                "| Completed from persisted evidence. | Exact / Approximate / Unknown / Excluded | SOURCE / PARTIAL / GUESS |  | yes / no |  |",
                "| Layout | Exact | SOURCE | evidence/site-inventory.json | no | Matches the authorized page |",
            )
            spec.write_text(text, encoding="utf-8")
            (root / "evidence" / "design-dna" / "design-dna.json").unlink()
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            manifest = json.loads((root / "teardown-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["designDna"]["status"], "recommended-not-provided")

    def test_runtime_independence_blocks_source_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp) / "network.json"
            evidence.write_text(json.dumps({"requests": ["https://source.example/app.js", "https://cdn.example/a.js"]}), encoding="utf-8")
            build = Path(temp) / "dist"
            build.mkdir()
            (build / "index.js").write_text("const api = 'https://cdn.example/a.js';", encoding="utf-8")
            blocked = run(
                PYTHON, "scripts/check_runtime_independence.py", str(evidence),
                "--source-url", "https://source.example:443", "--build-dir", str(build), expect=1,
            )
            self.assertIn("source.example/app.js", blocked.stdout)
            evidence.write_text(json.dumps({"requests": ["https://cdn.example/a.js"]}), encoding="utf-8")
            (build / "index.js").write_text("const api = 'https://source.example/runtime';", encoding="utf-8")
            build_blocked = run(
                PYTHON, "scripts/check_runtime_independence.py", str(evidence),
                "--source-url", "https://source.example", "--build-dir", str(build), expect=1,
            )
            self.assertIn("index.js", build_blocked.stdout)
            (build / "index.js").write_text("const api = 'https://cdn.example/a.js';", encoding="utf-8")
            run(
                PYTHON, "scripts/check_runtime_independence.py", str(evidence),
                "--source-url", "https://source.example", "--build-dir", str(build),
            )

    def test_python_and_node_url_safety_agree(self) -> None:
        urls = [
            "https://example.com/path",
            "https://user:pass@example.com/",
            "https://example.com/?api_key=secret",
            "ftp://example.com/file",
            "not-a-url",
        ]
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            from url_safety import validate_public_url
            python_results = []
            for url in urls:
                try:
                    validate_public_url(url, "URL")
                    python_results.append(True)
                except ValueError:
                    python_results.append(False)
        finally:
            sys.path.pop(0)
        script = """import {parsePublicHttpUrl} from './scripts/url_safety.mjs';
const urls = JSON.parse(process.argv[1]);
console.log(JSON.stringify(urls.map((url) => { try { parsePublicHttpUrl(url); return true; } catch { return false; } })));
"""
        node_results = json.loads(run(NODE, "--input-type=module", "-e", script, json.dumps(urls)).stdout)
        self.assertEqual(python_results, node_results)

    def test_asset_manifest_generator_creates_safe_review_gated_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inventory = root / "site-inventory.json"
            inventory.write_text(json.dumps({
                "schemaVersion": 1,
                "resources": [
                    {"url": "https://cdn.example/media/hero.webp", "resourceType": "image", "mimeType": "image/webp"},
                    {"url": "https://cdn.example/render.php", "resourceType": "image", "mimeType": "image/png"},
                    {"url": "https://cdn.example/fonts/site.woff2", "resourceType": "font", "mimeType": "font/woff2"},
                    {"url": "https://cdn.example/assets/app.js", "resourceType": "script", "mimeType": "text/javascript"},
                    {"url": "https://api.example/data", "resourceType": "fetch", "mimeType": "application/json"},
                    {"url": "https://cdn.example/private.png?token=topsecret", "resourceType": "image", "mimeType": "image/png"},
                ],
                "routes": [{
                    "route": "/",
                    "surface": {
                        "images": ["https://cdn.example/media/hero.webp"],
                        "videos": [{"src": "https://cdn.example/media/intro.mp4"}],
                        "scripts": ["https://cdn.example/assets/app.js"],
                        "stylesheets": ["https://cdn.example/assets/site.css"],
                        "performanceResources": [],
                    },
                }],
            }), encoding="utf-8")
            manifest_path = root / "asset-manifest.json"
            run(PYTHON, "scripts/generate_asset_manifest.py", str(inventory), "--out", str(manifest_path))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schemaVersion"], 1)
            self.assertEqual(manifest["reviewStatus"], "pending")
            self.assertEqual(len(manifest["assets"]), 6)
            self.assertEqual(len({item["sourceUrl"] for item in manifest["assets"]}), 6)
            self.assertEqual(len({item["localPath"] for item in manifest["assets"]}), 6)
            hero = next(item for item in manifest["assets"] if item["sourceUrl"].endswith("hero.webp"))
            self.assertEqual(len(hero["discoveredFrom"]), 2)
            dynamic_image = next(item for item in manifest["assets"] if item["sourceUrl"].endswith("render.php"))
            self.assertTrue(dynamic_image["localPath"].endswith(".png"))
            self.assertTrue(all(item["localPath"].startswith("public/assets/") for item in manifest["assets"]))
            self.assertTrue(any(item["reason"] == "unsupported-resource-type" for item in manifest["excluded"]))
            self.assertTrue(any(item["reason"] == "sensitive-or-invalid-url" for item in manifest["excluded"]))
            self.assertNotIn("topsecret", json.dumps(manifest))

            blocked_download = run(
                PYTHON, "scripts/download_assets.py", str(manifest_path), "--output", str(root / "download"), expect=2,
            )
            self.assertIn("reviewStatus must be confirmed", blocked_download.stderr)
            preserved = run(
                PYTHON, "scripts/generate_asset_manifest.py", str(inventory), "--out", str(manifest_path), expect=2,
            )
            self.assertIn("output already exists", preserved.stderr)

    def test_asset_downloader_checks_type_checksum_and_is_idempotent(self) -> None:
        with fixture_server() as base, tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            digest = hashlib.sha256(b"gcw-asset").hexdigest()
            manifest = root / "assets.json"
            manifest.write_text(json.dumps({"assets": [{
                "sourceUrl": f"{base}/asset.bin",
                "localPath": "public/asset.bin",
                "contentType": "application/octet-stream",
                "checksumSha256": digest,
            }]}), encoding="utf-8")
            first = run(PYTHON, "scripts/download_assets.py", str(manifest), "--output", str(root / "out"))
            self.assertIn('"status": "downloaded"', first.stdout)
            second = run(PYTHON, "scripts/download_assets.py", str(manifest), "--output", str(root / "out"))
            self.assertIn('"status": "skipped"', second.stdout)
            manifest.write_text(json.dumps({"assets": [
                {
                    "sourceUrl": f"{base}/asset.bin",
                    "localPath": "../escape.bin",
                    "contentType": "application/octet-stream",
                },
                {
                    "sourceUrl": f"{base}/asset.bin",
                    "localPath": "public/second.bin",
                    "contentType": "application/octet-stream",
                },
                {
                    "sourceUrl": f"{base}/redirect-external",
                    "localPath": "public/external.bin",
                },
            ]}), encoding="utf-8")
            escaped = run(PYTHON, "scripts/download_assets.py", str(manifest), "--output", str(root / "out"), expect=1)
            report = json.loads(escaped.stdout)
            self.assertEqual([item["status"] for item in report["assets"]], ["failed", "downloaded", "failed"])
            self.assertIn("localPath must stay inside output", report["assets"][0]["error"])
            self.assertIn("redirect left source origin", report["assets"][2]["error"])
            self.assertNotIn("Traceback", escaped.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
