#!/usr/bin/env node

import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { assertSameOriginRedirects, joinSameOrigin, parsePublicHttpUrl, sanitizeText, sanitizeUrl } from "./url_safety.mjs";

function parseArgs(argv) {
  const args = {
    routes: [],
    timeout: 20000,
    settleMs: 100,
    maxPerTrigger: 10,
    viewport: { width: 1280, height: 720 },
    executablePath: "",
  };
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    const value = argv[index + 1];
    if (key === "--url") args.url = value, index += 1;
    else if (key === "--out") args.out = value, index += 1;
    else if (key === "--route") args.routes.push(value), index += 1;
    else if (key === "--timeout") args.timeout = Number(value), index += 1;
    else if (key === "--settle-ms") args.settleMs = Number(value), index += 1;
    else if (key === "--max-per-trigger") args.maxPerTrigger = Number(value), index += 1;
    else if (key === "--executable-path") args.executablePath = value, index += 1;
    else if (key === "--viewport") {
      const match = /^(\d+)x(\d+)$/.exec(value || "");
      if (!match) throw new Error("--viewport must use WIDTHxHEIGHT, for example 390x844");
      args.viewport = { width: Number(match[1]), height: Number(match[2]) };
      index += 1;
    } else throw new Error(`Unknown argument: ${key}`);
  }
  if (!args.url || !args.out) {
    throw new Error("Usage: detect_interaction_states.mjs --url <url> --out <interaction-states.json> [--route /path]");
  }
  if (!Number.isFinite(args.timeout) || args.timeout <= 0) throw new Error("--timeout must be a positive number");
  if (!Number.isFinite(args.settleMs) || args.settleMs < 0) throw new Error("--settle-ms must be zero or greater");
  if (!Number.isInteger(args.maxPerTrigger) || args.maxPerTrigger <= 0) throw new Error("--max-per-trigger must be a positive integer");
  return args;
}

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (error) {
    throw new Error(`Playwright is required. Run 'npm install playwright'. Original error: ${error.message}`);
  }
}

async function installNavigationGuard(context, allowedOrigin) {
  await context.route("**/*", async (route) => {
    const request = route.request();
    if (request.resourceType() === "document" && new URL(request.url()).origin !== allowedOrigin) {
      await route.abort("blockedbyclient");
      return;
    }
    await route.continue();
  });
}

async function discoverCandidates(page) {
  return page.evaluate(() => {
    const result = { hover: new Set(), focus: new Set(), expanded: new Set() };
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
    };
    const selectorFor = (element) => {
      if (element.id) return `#${CSS.escape(element.id)}`;
      const parts = [];
      let current = element;
      while (current && current !== document.documentElement && parts.length < 5) {
        let part = current.localName;
        if (!part) break;
        const siblings = current.parentElement ? [...current.parentElement.children].filter((item) => item.localName === current.localName) : [];
        if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(current) + 1})`;
        parts.unshift(part);
        const selector = parts.join(" > ");
        try {
          if (document.querySelectorAll(selector).length === 1) return selector;
        } catch {}
        current = current.parentElement;
      }
      return parts.join(" > ");
    };
    const addMatches = (selectorText) => {
      for (const selector of selectorText.split(",")) {
        for (const [trigger, pattern] of [["hover", /:hover(?![\w-])/], ["focus", /:focus(?:-visible)?(?![\w-])/]]) {
          const match = pattern.exec(selector);
          if (!match) continue;
          const base = selector.slice(0, match.index).trim();
          if (!base || /[(:>+~]$/.test(base)) continue;
          try {
            for (const element of document.querySelectorAll(base)) {
              if (visible(element)) result[trigger].add(selectorFor(element));
            }
          } catch {}
        }
      }
    };
    const walkRules = (rules) => {
      for (const rule of rules || []) {
        if (rule.selectorText) addMatches(rule.selectorText);
        if (rule.cssRules) walkRules(rule.cssRules);
      }
    };
    for (const sheet of document.styleSheets) {
      try {
        walkRules(sheet.cssRules);
      } catch {}
    }
    for (const element of document.querySelectorAll("button[aria-expanded], [role='button'][aria-expanded], [aria-controls][aria-expanded]")) {
      if (visible(element)) result.expanded.add(selectorFor(element));
    }
    return Object.fromEntries(Object.entries(result).map(([key, values]) => [key, [...values]]));
  });
}

async function snapshot(locator) {
  return locator.evaluate((element) => {
    const style = getComputedStyle(element);
    const fields = [
      "backgroundColor", "borderColor", "boxShadow", "color", "display", "opacity",
      "outlineColor", "outlineStyle", "textDecorationLine", "transform", "visibility",
    ];
    return {
      ariaExpanded: element.getAttribute("aria-expanded"),
      styles: Object.fromEntries(fields.map((field) => [field, style[field]])),
    };
  });
}

function changedFields(before, after) {
  const changes = [];
  if (before.ariaExpanded !== after.ariaExpanded) changes.push("aria-expanded");
  for (const [field, value] of Object.entries(before.styles)) {
    if (after.styles[field] !== value) changes.push(field);
  }
  return changes;
}

function safeId(value) {
  return value.replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^-|-$/g, "").slice(0, 60) || "element";
}

async function observeState(page, triggerType, selector, args) {
  const locator = page.locator(selector).first();
  if (!await locator.isVisible().catch(() => false)) return null;
  await page.mouse.move(args.viewport.width - 1, args.viewport.height - 1);
  await page.evaluate(() => {
    if (typeof document.activeElement?.blur === "function") document.activeElement.blur();
  });
  await page.waitForTimeout(args.settleMs);
  const before = await snapshot(locator);
  const beforeImage = await page.screenshot({ animations: "disabled" });
  try {
    if (triggerType === "hover") await locator.hover({ timeout: args.timeout });
    else if (triggerType === "focus") await locator.focus({ timeout: args.timeout });
    else await locator.click({ timeout: args.timeout });
  } catch {
    return null;
  }
  await page.waitForTimeout(args.settleMs);
  if (!await locator.isVisible().catch(() => false)) return null;
  const after = await snapshot(locator);
  const afterImage = await page.screenshot({ animations: "disabled" });
  const changes = changedFields(before, after);
  if (triggerType === "aria-expanded" && !changes.includes("aria-expanded")) return null;
  if (!changes.length && beforeImage.equals(afterImage)) return null;
  if (triggerType === "aria-expanded") await locator.click({ timeout: args.timeout }).catch(() => {});
  return { before, after, beforeImage, afterImage, changes };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const canonical = parsePublicHttpUrl(args.url, "--url");
  const routes = args.routes.length ? args.routes : [`${canonical.pathname}${canonical.search}` || "/"];
  const { chromium } = await loadPlaywright();
  const executablePath = args.executablePath || process.env.GCW_BROWSER_EXECUTABLE || undefined;
  const browser = await chromium.launch({ headless: true, executablePath });
  const outPath = path.resolve(args.out);
  const evidenceRoot = path.dirname(outPath);
  const viewportKind = args.viewport.width <= 600 ? "mobile" : "desktop";
  const screenshotDir = path.join(evidenceRoot, "screenshots", viewportKind, "interactions");
  await mkdir(screenshotDir, { recursive: true });
  const states = [];
  const qa = { consoleErrors: [], httpErrors: [] };
  try {
    const context = await browser.newContext({ viewport: args.viewport, deviceScaleFactor: 1 });
    await installNavigationGuard(context, canonical.origin);
    const page = await context.newPage();
    page.setDefaultTimeout(args.timeout);
    page.on("console", (message) => {
      if (message.type() === "error") qa.consoleErrors.push(sanitizeText(message.text()));
    });
    page.on("response", (response) => {
      if (response.status() >= 400) qa.httpErrors.push({ status: response.status(), url: sanitizeUrl(response.url()) });
    });
    for (const route of routes) {
      const target = joinSameOrigin(canonical.origin, route, `Route '${route}'`);
      parsePublicHttpUrl(target, `Route '${route}'`);
      await assertSameOriginRedirects(target, canonical.origin, `Route '${route}'`, args.timeout);
      await page.goto(target, { waitUntil: "domcontentloaded", timeout: args.timeout });
      await page.waitForTimeout(args.settleMs);
      const candidates = await discoverCandidates(page);
      for (const [triggerType, selectors] of [
        ["hover", candidates.hover],
        ["focus", candidates.focus],
        ["aria-expanded", candidates.expanded],
      ]) {
        for (const selector of selectors.slice(0, args.maxPerTrigger)) {
          const observed = await observeState(page, triggerType, selector, args);
          if (!observed) continue;
          const stateId = `${triggerType}-${safeId(selector)}-${states.length + 1}`;
          const beforeName = `${stateId}.before.png`;
          const afterName = `${stateId}.after.png`;
          const beforePath = path.join(screenshotDir, beforeName);
          const afterPath = path.join(screenshotDir, afterName);
          await Promise.all([
            writeFile(beforePath, observed.beforeImage),
            writeFile(afterPath, observed.afterImage),
          ]);
          const evidence = [beforePath, afterPath].map((item) => path.relative(evidenceRoot, item).split(path.sep).join("/"));
          states.push({
            id: stateId,
            route,
            trigger: `${triggerType} ${selector}`,
            triggerType,
            elementSelector: selector,
            expected: `Observed ${triggerType} change: ${observed.changes.join(", ") || "viewport pixels"}`,
            before: observed.before,
            after: observed.after,
            viewport: args.viewport,
            evidence,
          });
        }
      }
    }
    await context.close();
  } finally {
    await browser.close();
  }
  const output = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    sourceUrl: sanitizeUrl(canonical.href),
    reviewStatus: "pending",
    states,
    qa,
  };
  await mkdir(path.dirname(outPath), { recursive: true });
  await writeFile(outPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
  console.log(JSON.stringify({ out: outPath, states: states.length, reviewStatus: output.reviewStatus, qa }, null, 2));
}

main().catch((error) => {
  console.error(sanitizeText(error.stack || error.message));
  process.exitCode = 1;
});
