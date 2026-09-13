#!/usr/bin/env node
// 图像准备工具：DICOM / HEIC / TIFF 等 → PNG，可选缩放到指定尺寸（默认 896，与 MedGemma 图像规格一致）
// 用法: node scripts/prepare-image.js <input> [--size 896] [--output out.png]
// 依赖: macOS 自带 sips；DICOM 转换需要 ffmpeg（brew install ffmpeg）或 dcmtk（brew install dcmtk）
import fs from "node:fs/promises";
import path from "node:path";
import { execFileSync } from "node:child_process";

const DEFAULT_SIZE = 896;
const args = parseArgs(process.argv.slice(2));
const input = args._[0];
if (!input) fail("usage: node prepare-image.js <input> [--size 896] [--output out.png]");

const size = Number(args.size || DEFAULT_SIZE);
if (!Number.isInteger(size) || size <= 0) fail("invalid --size: must be a positive integer");

let stat;
try { stat = await fs.stat(input); } catch { fail("cannot read input file: " + input); }
if (!stat.isFile()) fail("input is not a file: " + input);

const ext = path.extname(input).toLowerCase();
const isDicom = ext === ".dcm" || ext === ".dicom";
const output = args.output || path.join(path.dirname(input), path.basename(input, ext) + ".png");

try {
  if (isDicom) convertDicom(input, output, size);
  else convertImage(input, output, size);
} catch (error) {
  fail(error.message);
}

console.log(JSON.stringify({ success: true, input, output, size, note: "use this output path with medgemma.js --image" }));

function convertDicom(input, output, size) {
  if (hasTool("ffmpeg")) {
    run("ffmpeg", ["-y", "-i", input, "-frames:v", "1", output]);
    if (size) run("sips", ["-Z", String(size), output, "--out", output]);
    return;
  }
  if (hasTool("dcmj2pnm")) {
    run("dcmj2pnm", ["--write-png", input, output]);
    if (size) run("sips", ["-Z", String(size), output, "--out", output]);
    return;
  }
  fail("no DICOM converter available; install one: brew install ffmpeg, or brew install dcmtk");
}

function convertImage(input, output, size) {
  if (hasTool("sips")) {
    const cmd = ["-s", "format", "png"];
    if (size) cmd.push("-Z", String(size));
    run("sips", [...cmd, input, "--out", output]);
    return;
  }
  if (hasTool("ffmpeg")) {
    const cmd = ["-y", "-i", input];
    if (size) cmd.push("-vf", "scale=" + size + ":-2");
    run("ffmpeg", [...cmd, output]);
    return;
  }
  fail("no image converter available; sips is built-in on macOS, or install ffmpeg");
}

function hasTool(name) {
  try { execFileSync("which", [name], { stdio: "ignore" }); return true; } catch { return false; }
}

function run(name, argsList) {
  try {
    execFileSync(name, argsList, { stdio: "ignore" });
  } catch (error) {
    throw new Error(name + " failed (exit " + error.status + "): " + argsList.join(" "));
  }
}

function parseArgs(values) {
  const output = {};
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (value.startsWith("--")) {
      const key = value.slice(2);
      output[key] = values[index + 1]?.startsWith("--") ? true : values[index + 1] ?? true;
      if (output[key] !== true) index += 1;
    } else {
      if (!output._) output._ = [];
      output._.push(value);
    }
  }
  return output;
}

function fail(message) { console.error(JSON.stringify({ success: false, error: message })); process.exit(1); }
