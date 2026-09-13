#!/usr/bin/env node

import { mkdir, readFile, unlink, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { assertSameOriginRedirects, joinSameOrigin, parsePublicHttpUrl, sanitizeText, sanitizeUrl } from "./url_safety.mjs";

const DEFAULT_CLOCK_START = "2026-06-30T00:00:00.000Z";

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--config") args.config = argv[++i];
    else if (argv[i] === "--output") args.output = argv[++i];
    else if (argv[i] === "--record-har") args.recordHar = argv[++i];
    else if (argv[i] === "--replay-har") args.replayHar = argv[++i];
    else throw new Error(`Unknown argument: ${argv[i]}`);
  }
  if (!args.config || !args.output) throw new Error("Usage: capture_compare.mjs --config <json> --output <dir> [--record-har <dir> | --replay-har <dir>]");
  if (args.recordHar && args.replayHar) throw new Error("--record-har and --replay-har are mutually exclusive");
  return args;
}

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (error) {
    throw new Error(`Playwright is required. Run 'npm install playwright'. Original error: ${error.message}`);
  }
}

function safeId(value) {
  return value.replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^-|-$/g, "") || "scenario";
}

const SENSITIVE_FIELD = /(?:^|[-_])(?:access[-_]?token|api[-_]?key|auth|authorization|client[-_]?secret|cookie|credential|jwt|key|password|passwd|refresh[-_]?token|secret|session|sig|signature|token)$/i;

function redactText(value) {
  return String(value)
    .replace(/\bBearer\s+[^\s,;]+/gi, "Bearer REDACTED")
    .replace(/\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g, "REDACTED");
}

function sanitizeString(value, sourceOrigins, candidateOrigin) {
  const redacted = redactText(value);
  if (!redacted.startsWith("http://") && !redacted.startsWith("https://")) return redacted;
  try {
    return rebaseAndSanitizeUrl(redacted, sourceOrigins, candidateOrigin);
  } catch {
    return redacted;
  }
}

function redactValue(value, key = "", sourceOrigins = new Set(), candidateOrigin = "") {
  if (SENSITIVE_FIELD.test(key)) return "REDACTED";
  if (Array.isArray(value)) return value.map((item) => redactValue(item, "", sourceOrigins, candidateOrigin));
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([childKey, child]) => [childKey, redactValue(child, childKey, sourceOrigins, candidateOrigin)]));
  }
  return typeof value === "string" ? sanitizeString(value, sourceOrigins, candidateOrigin) : value;
}

function redactJsonText(value, sourceOrigins, candidateOrigin) {
  try {
    return JSON.stringify(redactValue(JSON.parse(value), "", sourceOrigins, candidateOrigin));
  } catch {
    return sanitizeString(value, sourceOrigins, candidateOrigin);
  }
}

function sanitizeHeaders(headers = [], sourceOrigins, candidateOrigin) {
  return headers
    .filter((header) => !SENSITIVE_FIELD.test(header.name))
    .map((header) => ({ ...header, value: sanitizeString(header.value, sourceOrigins, candidateOrigin) }));
}

function rebaseAndSanitizeUrl(value, sourceOrigins, candidateOrigin) {
  const url = new URL(value);
  if (sourceOrigins.has(url.origin)) {
    const rebased = new URL(`${url.pathname}${url.search}${url.hash}`, candidateOrigin);
    return sanitizeUrl(rebased.href);
  }
  return sanitizeUrl(url.href);
}

function sanitizeContent(content = {}, sourceOrigins, candidateOrigin) {
  if (typeof content.text !== "string") return content;
  const encoding = content.encoding;
  if (encoding === "base64" && !/(?:json|javascript|text|xml|svg|x-www-form-urlencoded)/i.test(content.mimeType || "")) return content;
  const decoded = encoding === "base64" ? Buffer.from(content.text, "base64").toString("utf8") : content.text;
  const redacted = redactJsonText(decoded, sourceOrigins, candidateOrigin);
  return { ...content, text: encoding === "base64" ? Buffer.from(redacted).toString("base64") : redacted };
}

async function sanitizeRecordedHar(rawPath, finalPath, sourceOrigins, candidateOrigin) {
  try {
    const har = JSON.parse(await readFile(rawPath, "utf8"));
    const entries = har?.log?.entries;
    if (!Array.isArray(entries)) throw new Error(`Recorded HAR has no log.entries array: ${rawPath}`);
    for (const entry of entries) {
      const request = entry.request || {};
      request.url = rebaseAndSanitizeUrl(request.url, sourceOrigins, candidateOrigin);
      request.headers = sanitizeHeaders(request.headers, sourceOrigins, candidateOrigin);
      request.cookies = [];
      request.queryString = (request.queryString || []).map((item) => ({
        ...item,
        value: SENSITIVE_FIELD.test(item.name) ? "REDACTED" : redactText(item.value),
      }));
      if (request.postData) {
        request.postData = { ...request.postData };
        if (typeof request.postData.text === "string") request.postData.text = redactJsonText(request.postData.text, sourceOrigins, candidateOrigin);
        request.postData.params = (request.postData.params || []).map((item) => ({
          ...item,
          value: SENSITIVE_FIELD.test(item.name) ? "REDACTED" : redactText(item.value),
        }));
      }
      const response = entry.response || {};
      response.headers = sanitizeHeaders(response.headers, sourceOrigins, candidateOrigin);
      response.cookies = [];
      response.redirectURL = response.redirectURL ? rebaseAndSanitizeUrl(response.redirectURL, sourceOrigins, candidateOrigin) : "";
      response.content = sanitizeContent(response.content, sourceOrigins, candidateOrigin);
    }
    await writeFile(finalPath, `${JSON.stringify(har, null, 2)}\n`, "utf8");
    return entries.length;
  } finally {
    await unlink(rawPath).catch((error) => {
      if (error.code !== "ENOENT") throw error;
    });
  }
}

async function installHarReplay(context, harPath, allowedOrigin, side, fallbacks, blocked) {
  await context.route("**/*", async (route) => {
    const url = route.request().url();
    const sameOrigin = new URL(url).origin === allowedOrigin;
    fallbacks.push({ side, url: sanitizeUrl(url), allowed: sameOrigin });
    if (sameOrigin) await route.continue();
    else {
      blocked.push({ side, url: sanitizeUrl(url) });
      await route.abort("blockedbyclient");
    }
  });
  await context.routeFromHAR(harPath, { notFound: "fallback" });
}

async function installSeededRandom(context, seed) {
  await context.addInitScript(({ runtimeSeed }) => {
    let state = Number(runtimeSeed) >>> 0;
    Math.random = () => {
      state += 0x6D2B79F5;
      let value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }, { runtimeSeed: seed });
}

async function installNavigationGuard(context, allowedOrigin) {
  await context.route("**/*", async (route) => {
    const request = route.request();
    if (request.resourceType() === "document") {
      const target = new URL(request.url());
      if (target.origin !== allowedOrigin) {
        await route.abort("blockedbyclient");
        return;
      }
    }
    await route.fallback();
  });
}

async function initializePage(page, url, scenario) {
  await page.emulateMedia({
    colorScheme: scenario.colorScheme || "light",
    reducedMotion: scenario.reducedMotion || "no-preference",
  });
  if ((scenario.clockMode || "controlled") === "controlled") {
    const clockStart = new Date(scenario.clockStart || DEFAULT_CLOCK_START);
    await page.clock.install({ time: clockStart });
    await page.clock.pauseAt(clockStart);
  }
  const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: scenario.timeoutMs || 30000 });
  return { status: response?.status() ?? null, finalUrl: page.url(), title: await page.title() };
}

async function isReady(page, scenario) {
  if (scenario.readySelector) {
    return page.locator(scenario.readySelector).first().isVisible().catch(() => false);
  }
  return Boolean(await page.evaluate(scenario.readyFunction));
}

async function advancePair(sourcePage, candidatePage, milliseconds) {
  if (milliseconds <= 0) return;
  await Promise.all([sourcePage.clock.runFor(milliseconds), candidatePage.clock.runFor(milliseconds)]);
}

async function waitPair(sourcePage, candidatePage, milliseconds) {
  if (milliseconds <= 0) return;
  await Promise.all([sourcePage.waitForTimeout(milliseconds), candidatePage.waitForTimeout(milliseconds)]);
}

async function waitForPairedReadiness(sourcePage, candidatePage, scenario) {
  const clockMode = scenario.clockMode || "controlled";
  const timeoutMs = scenario.readyTimeoutMs || 30000;
  if (clockMode === "realtime") {
    const waitOne = async (page) => {
      if (scenario.readySelector) await page.waitForSelector(scenario.readySelector, { state: "visible", timeout: timeoutMs });
      else await page.waitForFunction(scenario.readyFunction, undefined, { timeout: timeoutMs });
      await page.waitForTimeout(scenario.readyDelayMs || 0);
    };
    await Promise.all([waitOne(sourcePage), waitOne(candidatePage)]);
    return { clockMode, advancedMs: null };
  }

  const stepMs = scenario.clockStepMs || 16;
  let advancedMs = 0;
  while (advancedMs <= timeoutMs) {
    const [sourceReady, candidateReady] = await Promise.all([
      isReady(sourcePage, scenario),
      isReady(candidatePage, scenario),
    ]);
    if (sourceReady && candidateReady) break;
    await advancePair(sourcePage, candidatePage, stepMs);
    advancedMs += stepMs;
  }
  const [sourceReady, candidateReady] = await Promise.all([
    isReady(sourcePage, scenario),
    isReady(candidatePage, scenario),
  ]);
  if (!sourceReady || !candidateReady) {
    throw new Error(`Scenario '${scenario.id || scenario.route}' did not reach paired readiness within ${timeoutMs} virtual ms`);
  }
  await advancePair(sourcePage, candidatePage, scenario.readyDelayMs || 0);
  return { clockMode, advancedMs: advancedMs + (scenario.readyDelayMs || 0) };
}

async function applyInput(page, scenario) {
  const scroll = scenario.scroll || { x: 0, y: 0 };
  if (scenario.innerScrollSelector) {
    await page.locator(scenario.innerScrollSelector).evaluate((node, value) => node.scrollTo(value.x || 0, value.y || 0), scroll);
  } else {
    await page.evaluate((value) => window.scrollTo(value.x || 0, value.y || 0), scroll);
  }
  if (scenario.pointer) await page.mouse.move(scenario.pointer.x, scenario.pointer.y);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const config = JSON.parse(await readFile(path.resolve(args.config), "utf8"));
  const sourceUrl = process.env.GCW_SOURCE_URL || config.sourceUrl;
  const candidateUrl = process.env.GCW_CANDIDATE_URL || config.candidateUrl;
  if (!sourceUrl || !candidateUrl || !Array.isArray(config.scenarios) || !config.scenarios.length) {
    throw new Error("Config requires sourceUrl, candidateUrl and a non-empty scenarios array");
  }
  const sourceCanonical = parsePublicHttpUrl(sourceUrl, "sourceUrl");
  const candidateCanonical = parsePublicHttpUrl(candidateUrl, "candidateUrl");
  const harMode = args.recordHar ? "record" : args.replayHar ? "replay" : null;
  if (harMode && (typeof config.harFixture?.urlFilter !== "string" || !config.harFixture.urlFilter.trim())) {
    throw new Error("HAR recording/replay requires harFixture.urlFilter in the capture config");
  }
  if (harMode && config.harFixture.rebaseOrigins !== undefined && !Array.isArray(config.harFixture.rebaseOrigins)) {
    throw new Error("harFixture.rebaseOrigins must be an array of public origins");
  }
  const harRebaseOrigins = new Set(harMode ? [
    sourceCanonical.origin,
    ...(config.harFixture.rebaseOrigins || []).map((value) => parsePublicHttpUrl(value, "harFixture.rebaseOrigins entry").origin),
  ] : []);
  const ids = new Set();
  for (const scenario of config.scenarios) {
    if (!scenario.readySelector && !scenario.readyFunction) {
      throw new Error(`Scenario '${scenario.id || scenario.route || "unnamed"}' requires readySelector or readyFunction`);
    }
    const id = safeId(scenario.id || scenario.route || "scenario");
    if (ids.has(id)) throw new Error(`Scenario id collision after filename sanitization: '${id}'`);
    ids.add(id);
    joinSameOrigin(sourceUrl, scenario.route || "/", `Scenario '${id}' route`);
  }

  const { chromium } = await loadPlaywright();
  const executablePath = process.env.GCW_BROWSER_EXECUTABLE || config.browserExecutable || undefined;
  const [sourceBrowser, candidateBrowser] = await Promise.all([
    chromium.launch({ headless: true, executablePath }),
    chromium.launch({ headless: true, executablePath }),
  ]);
  const outputDir = path.resolve(args.output);
  await mkdir(outputDir, { recursive: true });
  const harDir = harMode ? path.resolve(args.recordHar || args.replayHar) : null;
  if (harDir) await mkdir(harDir, { recursive: true });
  const harFallbacks = [];
  const blockedRequests = [];
  const manifest = {
    schemaVersion: 3,
    generatedAt: new Date().toISOString(),
    sourceUrl: sanitizeUrl(sourceUrl),
    candidateUrl: sanitizeUrl(candidateUrl),
    seed: config.seed ?? 1,
    captures: [],
  };
  if (harMode) {
    manifest.harFixtures = { mode: harMode, urlFilter: config.harFixture.urlFilter, files: [], fallbacks: harFallbacks, blockedRequests };
  }

  try {
    for (const scenario of config.scenarios) {
      const id = safeId(scenario.id || scenario.route || "scenario");
      const contextOptions = {
        viewport: scenario.viewport || { width: 1280, height: 720 },
        deviceScaleFactor: scenario.deviceScaleFactor || 1,
        locale: scenario.locale || "en-US",
        timezoneId: scenario.timezoneId || "UTC",
        ...(harMode ? { serviceWorkers: "block" } : {}),
      };
      const harPath = harMode ? path.join(harDir, `${id}.har`) : null;
      const rawHarPath = args.recordHar ? path.join(harDir, `${id}.raw.har`) : null;
      const [sourceContext, candidateContext] = await Promise.all([
        sourceBrowser.newContext(rawHarPath ? {
          ...contextOptions,
          recordHar: { path: rawHarPath, content: "embed", mode: "minimal", urlFilter: config.harFixture.urlFilter },
        } : contextOptions),
        candidateBrowser.newContext(contextOptions),
      ]);
      let recordedEntries = null;
      try {
        if (args.replayHar) {
          await Promise.all([
            installHarReplay(sourceContext, harPath, sourceCanonical.origin, "source", harFallbacks, blockedRequests),
            installHarReplay(candidateContext, harPath, candidateCanonical.origin, "candidate", harFallbacks, blockedRequests),
          ]);
        }
        await Promise.all([
          installSeededRandom(sourceContext, config.seed ?? 1),
          installSeededRandom(candidateContext, config.seed ?? 1),
          ...(args.replayHar ? [] : [
            installNavigationGuard(sourceContext, sourceCanonical.origin),
            installNavigationGuard(candidateContext, candidateCanonical.origin),
          ]),
        ]);
        const route = scenario.route || "/";
        const sourceTarget = joinSameOrigin(sourceUrl, route, `Scenario '${id}' source route`);
        const candidateTarget = joinSameOrigin(candidateUrl, route, `Scenario '${id}' candidate route`);
        await Promise.all([
          assertSameOriginRedirects(sourceTarget, sourceCanonical.origin, `Scenario '${id}' source`, scenario.timeoutMs || 30000),
          assertSameOriginRedirects(candidateTarget, candidateCanonical.origin, `Scenario '${id}' candidate`, scenario.timeoutMs || 30000),
        ]);
        const [sourcePage, candidatePage] = await Promise.all([sourceContext.newPage(), candidateContext.newPage()]);
        const [sourceMeta, candidateMeta] = await Promise.all([
          initializePage(sourcePage, sourceTarget, scenario),
          initializePage(candidatePage, candidateTarget, scenario),
        ]);
        const timing = await waitForPairedReadiness(sourcePage, candidatePage, scenario);
        const phaseMs = scenario.phaseMs ?? 0;
        if (!Number.isFinite(phaseMs) || phaseMs < 0) throw new Error(`Scenario '${id}' phaseMs must be zero or greater`);
        if (timing.clockMode === "controlled") await advancePair(sourcePage, candidatePage, phaseMs);
        else await waitPair(sourcePage, candidatePage, phaseMs);
        await Promise.all([applyInput(sourcePage, scenario), applyInput(candidatePage, scenario)]);
        const afterInputDelayMs = scenario.afterInputDelayMs ?? 100;
        if (!Number.isFinite(afterInputDelayMs) || afterInputDelayMs < 0) throw new Error(`Scenario '${id}' afterInputDelayMs must be zero or greater`);
        if (timing.clockMode === "controlled") {
          await advancePair(sourcePage, candidatePage, afterInputDelayMs);
        } else {
          await waitPair(sourcePage, candidatePage, afterInputDelayMs);
        }

        const sourcePath = path.join(outputDir, `${id}.source.png`);
        const candidatePath = path.join(outputDir, `${id}.candidate.png`);
        const screenshotOptions = { animations: "disabled", fullPage: Boolean(scenario.fullPage) };
        await Promise.all([
          sourcePage.screenshot({ ...screenshotOptions, path: sourcePath }),
          candidatePage.screenshot({ ...screenshotOptions, path: candidatePath }),
        ]);
        manifest.captures.push({
          id,
          route,
          viewport: scenario.viewport || { width: 1280, height: 720 },
          deviceScaleFactor: scenario.deviceScaleFactor || 1,
          timing: { ...timing, phaseMs, afterInputDelayMs },
          scroll: scenario.scroll || { x: 0, y: 0 },
          pointer: scenario.pointer || null,
          source: { ...sourceMeta, finalUrl: sanitizeUrl(sourceMeta.finalUrl), image: path.basename(sourcePath) },
          candidate: { ...candidateMeta, finalUrl: sanitizeUrl(candidateMeta.finalUrl), image: path.basename(candidatePath) },
        });
      } finally {
        let closeError = null;
        try {
          await Promise.all([sourceContext.close(), candidateContext.close()]);
        } catch (error) {
          closeError = error;
        }
        if (rawHarPath) {
          recordedEntries = await sanitizeRecordedHar(rawHarPath, harPath, harRebaseOrigins, candidateCanonical.origin);
        }
        if (closeError) throw closeError;
      }
      if (rawHarPath) {
        manifest.harFixtures.files.push({ id, path: path.basename(harPath), entries: recordedEntries });
      } else if (harPath) {
        manifest.harFixtures.files.push({ id, path: path.basename(harPath) });
      }
    }
  } finally {
    await Promise.all([sourceBrowser.close(), candidateBrowser.close()]);
  }

  const manifestPath = path.join(outputDir, "capture-manifest.json");
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  console.log(JSON.stringify({ output: outputDir, scenarios: manifest.captures.length, manifest: manifestPath, harMode }, null, 2));
}

main().catch((error) => {
  console.error(sanitizeText(error.stack || error.message));
  process.exitCode = 1;
});
