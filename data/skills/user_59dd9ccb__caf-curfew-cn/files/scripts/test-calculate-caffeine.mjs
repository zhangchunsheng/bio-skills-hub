#!/usr/bin/env node

import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const script = path.join(here, "calculate-caffeine.mjs");

function run(input, env = {}) {
  return spawnSync(process.execPath, [script], {
    input: typeof input === "string" ? input : JSON.stringify(input),
    encoding: "utf8",
    env: { ...process.env, ...env }
  });
}

const normal = run({
  nowIso: "2026-07-19T15:00:00+08:00",
  bedtimeIso: "2026-07-19T23:00:00+08:00",
  halfLifeHours: 5,
  intakes: [
    { label: "latte", drankAt: "2026-07-19T10:00:00+08:00", caffeineMg: 150 }
  ],
  candidate: { label: "small coffee", caffeineMg: 120 }
});
assert.equal(normal.status, 0, normal.stderr);
const normalResult = JSON.parse(normal.stdout);
assert.equal(normalResult.baselineResidualMg, 24.7);
assert.equal(normalResult.candidateResidualMg, 39.6);
assert.equal(normalResult.projectedResidualMg, 64.3);
assert.equal(normalResult.heuristicBand, "medium");
assert.equal(normalResult.lateIntakeMg, 120);

const timezone = run({
  nowIso: "2026-07-19T14:30:00+08:00",
  bedtimeIso: "2026-07-19T23:00:00+08:00",
  intakes: [
    { drankAt: "2026-07-19T14:15:00+08:00", caffeineMg: 80 }
  ]
}, { TZ: "UTC" });
assert.equal(timezone.status, 0, timezone.stderr);
assert.equal(JSON.parse(timezone.stdout).lateIntakeMg, 80);

const invalidRecord = run({
  nowIso: "2026-07-19T15:00:00+08:00",
  bedtimeIso: "2026-07-19T23:00:00+08:00",
  intakes: [
    { label: "bad time", drankAt: "not-a-time", caffeineMg: 80 },
    { label: "valid", drankAt: "2026-07-19T09:00:00+08:00", caffeineMg: 100 }
  ]
});
assert.equal(invalidRecord.status, 0, invalidRecord.stderr);
const invalidRecordResult = JSON.parse(invalidRecord.stdout);
assert.equal(invalidRecordResult.warnings.length, 1);
assert.equal(invalidRecordResult.baselineTotalMg, 100);

const missingZone = run({
  nowIso: "2026-07-19T15:00:00",
  bedtimeIso: "2026-07-19T23:00:00+08:00",
  intakes: []
});
assert.equal(missingZone.status, 1);
assert.match(missingZone.stderr, /时区/);

const pastBedtime = run({
  nowIso: "2026-07-19T23:30:00+08:00",
  bedtimeIso: "2026-07-19T23:00:00+08:00",
  intakes: []
});
assert.equal(pastBedtime.status, 1);
assert.match(pastBedtime.stderr, /晚于/);

const malformed = run("{not json");
assert.equal(malformed.status, 1);
assert.match(malformed.stderr, /合法 JSON/);

process.stdout.write("6 calculate-caffeine cases passed\n");
