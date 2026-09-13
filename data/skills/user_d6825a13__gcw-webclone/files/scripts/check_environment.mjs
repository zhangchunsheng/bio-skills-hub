#!/usr/bin/env node

import { accessSync, constants, existsSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..");
const requiredCompanions = ["web-shader-extractor", "design-dna"];
const optionalCompanions = ["browser-qa"];

function executableExists(file) {
  if (!file || !existsSync(file)) return false;
  try {
    accessSync(file, constants.X_OK);
    return true;
  } catch {
    return process.platform === "win32";
  }
}

function command(command, args) {
  const result = spawnSync(command, args, { encoding: "utf8", windowsHide: true });
  return {
    ok: result.status === 0,
    output: (result.stdout || result.stderr || "").trim(),
  };
}

function findBlender() {
  const candidates = [process.env.GCW_BLENDER_EXECUTABLE];
  const where = process.platform === "win32" ? command("where.exe", ["blender"]) : command("which", ["blender"]);
  if (where.ok) candidates.unshift(where.output.split(/\r?\n/)[0]);
  return candidates.find(executableExists) || null;
}

function inspectSkillRoot(root) {
  if (!root || !existsSync(root)) return null;
  const skills = requiredCompanions.filter((name) => existsSync(path.join(root, name, "SKILL.md")));
  const optionalSkills = optionalCompanions.filter((name) => existsSync(path.join(root, name, "SKILL.md")));
  return {
    root,
    complete: skills.length === requiredCompanions.length,
    found: skills,
    missing: requiredCompanions.filter((name) => !skills.includes(name)),
    optional: {
      found: optionalSkills,
      missing: optionalCompanions.filter((name) => !optionalSkills.includes(name)),
    },
  };
}

const nodeMajor = Number(process.versions.node.split(".")[0]);
const python = command(process.platform === "win32" ? "python" : "python3", ["--version"]);
const pillow = command(process.platform === "win32" ? "python" : "python3", ["-c", "from PIL import Image; print(Image.__version__)"]);

let playwright = { ok: false, version: null, chromium: null };
try {
  const module = await import("playwright");
  const packageJson = JSON.parse(await (await import("node:fs/promises")).readFile(path.join(repoRoot, "node_modules", "playwright", "package.json"), "utf8"));
  const chromium = module.chromium.executablePath();
  playwright = { ok: executableExists(chromium), version: packageJson.version, chromium };
} catch (error) {
  playwright.error = error.message;
}

const skillRootCandidates = [
  process.env.GCW_SKILLS_ROOT,
  path.resolve(repoRoot, "..", ".agent", "skills"),
  path.join(homedir(), ".claude", "skills"),
  path.join(homedir(), ".codex", "skills"),
];
const skillRoots = [...new Set(skillRootCandidates.filter(Boolean))].map(inspectSkillRoot).filter(Boolean);
const blender = findBlender();

const report = {
  passed: nodeMajor >= 20 && python.ok && pillow.ok && playwright.ok,
  teardownReady: skillRoots.some((item) => item.complete),
  required: {
    node: { ok: nodeMajor >= 20, version: process.versions.node },
    python,
    pillow,
    playwright,
  },
  teardownRequirements: {
    companionSkills: { ok: skillRoots.some((item) => item.complete), roots: skillRoots, requiredFor: "standard and deep teardown" },
  },
  optional: {
    blender: { ok: Boolean(blender), executable: blender, requiredFor: "GLTF or GLB text replacement only" },
  },
};

process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
process.exitCode = report.passed ? 0 : 1;
