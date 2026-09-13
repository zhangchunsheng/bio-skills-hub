#!/usr/bin/env node

import fs from "node:fs";

const EXPLICIT_ZONE_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,3})?)?(?:Z|[+-]\d{2}:\d{2})$/;

function fail(message) {
  throw new Error(message);
}

function readInput() {
  const raw = fs.readFileSync(0, "utf8").trim();
  if (!raw) fail("stdin 需要一个 JSON 对象");
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
      fail("输入必须是 JSON 对象");
    }
    return parsed;
  } catch (error) {
    if (error.message === "输入必须是 JSON 对象") throw error;
    fail("输入不是合法 JSON");
  }
}

function parseIso(value, field) {
  if (typeof value !== "string" || !EXPLICIT_ZONE_RE.test(value)) {
    fail(`${field} 必须是带 Z 或 +/-HH:MM 时区的 ISO 8601 时间`);
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) fail(`${field} 不是合法时间`);
  return date;
}

function positiveNumber(value, field) {
  const number = Number(value);
  if (!Number.isFinite(number) || number <= 0) fail(`${field} 必须是正数`);
  return number;
}

function localHour(iso) {
  const match = iso.match(/T(\d{2}):(\d{2})/);
  return Number(match[1]) + Number(match[2]) / 60;
}

function hoursBetween(start, end) {
  return (end.getTime() - start.getTime()) / 36e5;
}

function remainingMg(caffeineMg, elapsedHours, halfLifeHours) {
  return caffeineMg * 0.5 ** (elapsedHours / halfLifeHours);
}

function band(residualMg) {
  if (residualMg > 80) return "high";
  if (residualMg >= 30) return "medium";
  return "low";
}

function round(value) {
  return Number(value.toFixed(1));
}

function normalizeDose(item, field, fallbackIso) {
  if (!item || Array.isArray(item) || typeof item !== "object") {
    fail(`${field} 必须是对象`);
  }
  const drankAtIso = item.drankAt ?? fallbackIso;
  const drankAt = parseIso(drankAtIso, `${field}.drankAt`);
  const caffeineMg = positiveNumber(item.caffeineMg, `${field}.caffeineMg`);
  return {
    label: typeof item.label === "string" && item.label.trim() ? item.label.trim() : field,
    drankAtIso,
    drankAt,
    caffeineMg
  };
}

function calculate() {
  const input = readInput();
  const now = parseIso(input.nowIso, "nowIso");
  const bedtime = parseIso(input.bedtimeIso, "bedtimeIso");
  const hoursToBedtime = hoursBetween(now, bedtime);
  if (hoursToBedtime <= 0) fail("bedtimeIso 必须晚于 nowIso");

  const halfLifeHours = input.halfLifeHours === undefined
    ? 5
    : positiveNumber(input.halfLifeHours, "halfLifeHours");
  if (halfLifeHours < 1.5 || halfLifeHours > 12) {
    fail("halfLifeHours 必须在 1.5 到 12 小时之间");
  }

  const rawIntakes = input.intakes ?? [];
  if (!Array.isArray(rawIntakes)) fail("intakes 必须是数组");
  if (rawIntakes.length > 100) fail("intakes 最多接受 100 条记录");

  const warnings = [];
  const intakes = [];
  for (let index = 0; index < rawIntakes.length; index += 1) {
    try {
      const intake = normalizeDose(rawIntakes[index], `intakes[${index}]`);
      if (intake.drankAt.getTime() > now.getTime()) {
        warnings.push(`跳过 ${intake.label}：已摄入记录晚于 nowIso`);
        continue;
      }
      intakes.push(intake);
    } catch (error) {
      warnings.push(`跳过 intakes[${index}]：${error.message}`);
    }
  }

  let baselineTotalMg = 0;
  let baselineResidualMg = 0;
  let lateIntakeMg = 0;
  for (const intake of intakes) {
    baselineTotalMg += intake.caffeineMg;
    baselineResidualMg += remainingMg(
      intake.caffeineMg,
      hoursBetween(intake.drankAt, bedtime),
      halfLifeHours
    );
    if (localHour(intake.drankAtIso) >= 14) lateIntakeMg += intake.caffeineMg;
  }

  let candidate = null;
  let candidateResidualMg = 0;
  if (input.candidate !== undefined && input.candidate !== null) {
    candidate = normalizeDose(input.candidate, "candidate", input.nowIso);
    if (candidate.drankAt.getTime() < now.getTime()) {
      fail("candidate.drankAt 不能早于 nowIso");
    }
    if (candidate.drankAt.getTime() >= bedtime.getTime()) {
      fail("candidate.drankAt 必须早于 bedtimeIso");
    }
    candidateResidualMg = remainingMg(
      candidate.caffeineMg,
      hoursBetween(candidate.drankAt, bedtime),
      halfLifeHours
    );
    if (localHour(candidate.drankAtIso) >= 14) lateIntakeMg += candidate.caffeineMg;
  }

  const projectedResidualMg = baselineResidualMg + candidateResidualMg;
  const projectedTotalMg = baselineTotalMg + (candidate?.caffeineMg ?? 0);

  return {
    nowIso: input.nowIso,
    bedtimeIso: input.bedtimeIso,
    hoursToBedtime: round(hoursToBedtime),
    halfLifeHours,
    baselineTotalMg: round(baselineTotalMg),
    baselineResidualMg: round(baselineResidualMg),
    candidateCaffeineMg: candidate ? round(candidate.caffeineMg) : null,
    candidateResidualMg: candidate ? round(candidateResidualMg) : null,
    projectedTotalMg: round(projectedTotalMg),
    projectedResidualMg: round(projectedResidualMg),
    lateIntakeMg: round(lateIntakeMg),
    heuristicBand: band(projectedResidualMg),
    warnings,
    disclaimer: "简化估算，不是人体测量、医学诊断或个体安全剂量。"
  };
}

try {
  process.stdout.write(`${JSON.stringify(calculate(), null, 2)}\n`);
} catch (error) {
  process.stderr.write(`calculate-caffeine 失败：${error.message}\n`);
  process.exit(1);
}
