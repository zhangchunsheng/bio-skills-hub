#!/usr/bin/env node

import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { assertSameOriginRedirects, hasSensitiveQuery, parsePublicHttpUrl, sanitizeText, sanitizeUrl } from "./url_safety.mjs";

function sanitizeSurface(surface) {
  for (const field of ["iframes", "images", "scripts", "stylesheets", "anchors"]) {
    surface[field] = surface[field].map(sanitizeUrl);
  }
  surface.videos = surface.videos.map((video) => ({ ...video, src: sanitizeUrl(video.src) }));
  surface.performanceResources = surface.performanceResources.map((resource) => ({ ...resource, url: sanitizeUrl(resource.url) }));
  return surface;
}

function isSourceMappable(response) {
  const resourceType = response.request().resourceType();
  const contentType = response.headers()["content-type"] || "";
  return resourceType === "script" || resourceType === "stylesheet" || /(?:javascript|ecmascript|text\/css)/i.test(contentType);
}

function sourceMapReference(response, body) {
  const headers = response.headers();
  for (const name of ["sourcemap", "x-sourcemap"]) {
    if (headers[name]) return { directive: name === "sourcemap" ? "SourceMap" : "X-SourceMap", value: headers[name].trim() };
  }
  const matches = [...body.matchAll(/(?:\/\/[#@]|\/\*[#@])\s*sourceMappingURL\s*=\s*([^\s*]+)[^\n]*?/gi)];
  return matches.length ? { directive: "sourceMappingURL", value: matches.at(-1)[1].trim() } : null;
}

function conventionalSourceMapUrl(resourceUrl) {
  const url = new URL(resourceUrl);
  url.hash = "";
  url.search = "";
  url.pathname = `${url.pathname}.map`;
  return url.href;
}

function isSourceMapV3(value, depth = 0) {
  if (!value || typeof value !== "object" || value.version !== 3 || depth > 8) return false;
  if (Array.isArray(value.sources) && typeof value.mappings === "string") return true;
  if (!Array.isArray(value.sections)) return false;
  return value.sections.every((section) => {
    const offset = section?.offset;
    const validOffset = Number.isInteger(offset?.line) && offset.line >= 0 && Number.isInteger(offset?.column) && offset.column >= 0;
    return validOffset && (typeof section.url === "string" || isSourceMapV3(section.map, depth + 1));
  });
}

function validateSourceMapBody(body) {
  try {
    const value = JSON.parse(body.toString("utf8"));
    if (!isSourceMapV3(value)) {
      return { validSourceMap: false, validationError: "response is not a valid Source Map v3 object" };
    }
    return { validSourceMap: true, validationError: null };
  } catch {
    return { validSourceMap: false, validationError: "response is not valid Source Map JSON" };
  }
}

async function readBoundedBody(response, maxBytes) {
  const contentLength = Number(response.headers.get("content-length"));
  if (Number.isFinite(contentLength) && contentLength > maxBytes) {
    await response.body?.cancel();
    throw new Error(`source map body exceeds ${maxBytes} bytes`);
  }
  if (!response.body) return Buffer.alloc(0);
  const reader = response.body.getReader();
  const chunks = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > maxBytes) throw new Error(`source map body exceeds ${maxBytes} bytes`);
      chunks.push(Buffer.from(value));
    }
  } catch (error) {
    await reader.cancel().catch(() => {});
    throw error;
  }
  return Buffer.concat(chunks, total);
}

function decodeEmbeddedSourceMap(value, maxBytes) {
  const separator = value.indexOf(",");
  if (separator < 0) throw new Error("embedded source map data URL is malformed");
  const metadata = value.slice(5, separator);
  const encoded = value.slice(separator + 1);
  const body = metadata.split(";").includes("base64") ? Buffer.from(encoded, "base64") : Buffer.from(decodeURIComponent(encoded));
  if (body.byteLength > maxBytes) throw new Error(`source map body exceeds ${maxBytes} bytes`);
  return { body, contentType: metadata.split(";", 1)[0] || "application/json" };
}

async function probeSourceMap(value, resourceUrl, timeout, maxBytes) {
  if (value.startsWith("data:")) {
    try {
      const { body, contentType } = decodeEmbeddedSourceMap(value, maxBytes);
      const validation = validateSourceMapBody(body);
      return {
        mapUrl: "data:embedded", finalUrl: null, status: null, reachable: true,
        accessible: validation.validSourceMap, embedded: true, contentType, bodyBytes: body.byteLength, ...validation,
      };
    } catch (error) {
      return {
        mapUrl: "data:embedded", finalUrl: null, status: null, reachable: true,
        accessible: false, embedded: true, contentType: null, bodyBytes: null,
        validSourceMap: false, validationError: error.message,
      };
    }
  }
  let current = parsePublicHttpUrl(new URL(value, resourceUrl).href, "source map URL", { allowSensitiveQuery: true });
  for (let hop = 0; hop < 10; hop += 1) {
    const response = await fetch(current, { redirect: "manual", signal: AbortSignal.timeout(timeout) });
    const contentType = response.headers.get("content-type");
    if (response.status < 300 || response.status >= 400) {
      if (!response.ok) {
        await response.body?.cancel();
        return {
          mapUrl: sanitizeUrl(new URL(value, resourceUrl).href), finalUrl: sanitizeUrl(current.href),
          status: response.status, reachable: false, accessible: false, embedded: false,
          contentType, bodyBytes: 0, validSourceMap: false, validationError: `source map returned HTTP ${response.status}`,
        };
      }
      try {
        const body = await readBoundedBody(response, maxBytes);
        const validation = validateSourceMapBody(body);
        return {
          mapUrl: sanitizeUrl(new URL(value, resourceUrl).href),
          finalUrl: sanitizeUrl(current.href),
          status: response.status,
          reachable: true,
          accessible: validation.validSourceMap,
          embedded: false,
          contentType,
          bodyBytes: body.byteLength,
          ...validation,
        };
      } catch (error) {
        return {
          mapUrl: sanitizeUrl(new URL(value, resourceUrl).href), finalUrl: sanitizeUrl(current.href),
          status: response.status, reachable: true, accessible: false, embedded: false,
          contentType, bodyBytes: null, validSourceMap: false, validationError: error.message,
        };
      }
    }
    await response.body?.cancel();
    const location = response.headers.get("location");
    if (!location) {
      return {
        mapUrl: sanitizeUrl(new URL(value, resourceUrl).href),
        finalUrl: sanitizeUrl(current.href),
        status: response.status,
        reachable: false,
        accessible: false,
        embedded: false,
        contentType,
        bodyBytes: 0,
        validSourceMap: false,
        validationError: "source map redirect has no location",
      };
    }
    current = parsePublicHttpUrl(new URL(location, current).href, "source map redirect", { allowSensitiveQuery: true });
  }
  throw new Error("source map probe exceeded 10 redirects");
}

async function inspectSourceMap(response, timeout, maxBytes) {
  const resourceUrl = response.url();
  let reference = null;
  let candidate = conventionalSourceMapUrl(resourceUrl);
  try {
    reference = sourceMapReference(response, (await response.body()).toString("utf8"));
    candidate = reference?.value || candidate;
    const probe = await probeSourceMap(candidate, resourceUrl, timeout, maxBytes);
    return {
      resourceUrl: sanitizeUrl(resourceUrl),
      resourceType: response.request().resourceType(),
      directive: reference?.directive || null,
      ...probe,
      error: null,
    };
  } catch (error) {
    return {
      resourceUrl: sanitizeUrl(resourceUrl),
      resourceType: response.request().resourceType(),
      directive: reference?.directive || null,
      mapUrl: candidate.startsWith("data:") ? "data:embedded" : sanitizeUrl(new URL(candidate, resourceUrl).href),
      finalUrl: null,
      status: null,
      reachable: false,
      accessible: false,
      embedded: false,
      contentType: null,
      bodyBytes: null,
      validSourceMap: false,
      validationError: null,
      error: sanitizeText(error.message),
    };
  }
}

function parseArgs(argv) {
  const args = { maxRoutes: 25, timeout: 20000, settleMs: 700, sourceMapMaxBytes: 20 * 1024 * 1024, executablePath: "", viewport: { width: 1280, height: 720 } };
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === "--url") args.url = value, i += 1;
    else if (key === "--out") args.out = value, i += 1;
    else if (key === "--max-routes") args.maxRoutes = Number(value), i += 1;
    else if (key === "--timeout") args.timeout = Number(value), i += 1;
    else if (key === "--settle-ms") args.settleMs = Number(value), i += 1;
    else if (key === "--source-map-max-bytes") args.sourceMapMaxBytes = Number(value), i += 1;
    else if (key === "--executable-path") args.executablePath = value, i += 1;
    else if (key === "--viewport") {
      const match = /^(\d+)x(\d+)$/.exec(value || "");
      if (!match) throw new Error("--viewport must use WIDTHxHEIGHT, for example 390x844");
      args.viewport = { width: Number(match[1]), height: Number(match[2]) }, i += 1;
    }
    else throw new Error(`Unknown argument: ${key}`);
  }
  if (!args.url || !args.out) {
    throw new Error("Usage: site_inventory.mjs --url <url> --out <file> [--max-routes 25]");
  }
  if (!Number.isInteger(args.maxRoutes) || args.maxRoutes <= 0) throw new Error("--max-routes must be a positive integer");
  if (!Number.isFinite(args.timeout) || args.timeout <= 0) throw new Error("--timeout must be a positive number");
  if (!Number.isFinite(args.settleMs) || args.settleMs < 0) throw new Error("--settle-ms must be zero or greater");
  if (!Number.isInteger(args.sourceMapMaxBytes) || args.sourceMapMaxBytes <= 0) throw new Error("--source-map-max-bytes must be a positive integer");
  if (args.viewport.width < 1 || args.viewport.height < 1) throw new Error("--viewport dimensions must be positive");
  return args;
}

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (error) {
    throw new Error(`Playwright is required. Run 'npm install playwright'. Original error: ${error.message}`);
  }
}

async function installCanvasProbe(context) {
  await context.addInitScript(() => {
    const observedContexts = new WeakMap();
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function getContext(type, ...args) {
      const result = Reflect.apply(originalGetContext, this, [type, ...args]);
      if (result) {
        observedContexts.set(this, {
          type: String(type),
          attributes: typeof result.getContextAttributes === "function" ? result.getContextAttributes() : null,
        });
      }
      return result;
    };
    Object.defineProperty(window, "__gcwCanvasContexts", { value: observedContexts });
  });
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
    await route.continue();
  });
}

function normalizeRoute(href, origin) {
  try {
    const url = new URL(href, origin);
    if (url.origin !== origin || !["http:", "https:"].includes(url.protocol)) return null;
    url.hash = "";
    if (hasSensitiveQuery(url)) return null;
    return `${url.pathname}${url.search}` || "/";
  } catch {
    return null;
  }
}

async function inspectPage(page) {
  return page.evaluate(() => {
    const canvases = [...document.querySelectorAll("canvas")].map((canvas, index) => {
      const observed = window.__gcwCanvasContexts?.get(canvas);
      const rect = canvas.getBoundingClientRect();
      return {
        index,
        context: observed?.type || "unknown",
        attributes: observed?.attributes || null,
        width: canvas.width,
        height: canvas.height,
        clientRect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        className: String(canvas.className || ""),
      };
    });

    const resources = performance.getEntriesByType("resource").map((entry) => ({
      url: entry.name,
      initiatorType: entry.initiatorType,
      duration: Number(entry.duration.toFixed(3)),
      transferSize: entry.transferSize || 0,
      decodedBodySize: entry.decodedBodySize || 0,
    }));

    return {
      title: document.title,
      readyState: document.readyState,
      scrollSize: { width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight },
      canvases,
      iframes: [...document.querySelectorAll("iframe")].map((node) => node.src),
      videos: [...document.querySelectorAll("video")].map((node) => ({ src: node.currentSrc || node.src, autoplay: node.autoplay, loop: node.loop })),
      images: [...document.images].map((node) => node.currentSrc || node.src).filter(Boolean),
      scripts: [...document.scripts].map((node) => node.src).filter(Boolean),
      stylesheets: [...document.querySelectorAll('link[rel="stylesheet"]')].map((node) => node.href),
      fonts: document.fonts ? [...document.fonts].map((font) => ({ family: font.family, style: font.style, weight: font.weight, status: font.status })) : [],
      anchors: [...document.querySelectorAll("a[href]")].map((node) => node.href),
      performanceResources: resources,
    };
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const canonical = parsePublicHttpUrl(args.url, "--url");
  const { chromium } = await loadPlaywright();
  const executablePath = args.executablePath || process.env.GCW_BROWSER_EXECUTABLE || undefined;
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const context = await browser.newContext({ viewport: args.viewport, deviceScaleFactor: 1 });
    await installCanvasProbe(context);
    await installNavigationGuard(context, canonical.origin);
    const page = await context.newPage();
    page.setDefaultTimeout(args.timeout);

    const resources = new Map();
    const sourceMapTasks = new Map();
    context.on("request", (request) => {
      const url = request.url();
      if (!resources.has(url)) {
        resources.set(url, { url: sanitizeUrl(url), method: request.method(), resourceType: request.resourceType(), status: null, mimeType: null });
      }
    });
    context.on("response", (response) => {
      const request = response.request();
      const current = resources.get(response.url()) || { url: sanitizeUrl(response.url()), method: request.method(), resourceType: request.resourceType() };
      current.status = response.status();
      current.mimeType = response.headers()["content-type"] || null;
      resources.set(response.url(), current);
      if (isSourceMappable(response) && !sourceMapTasks.has(response.url())) {
        sourceMapTasks.set(response.url(), inspectSourceMap(response, args.timeout, args.sourceMapMaxBytes));
      }
    });

    const queue = [normalizeRoute(canonical.href, canonical.origin) || "/"];
    const queued = new Set(queue);
    const visited = new Set();
    const routes = [];

    while (queue.length && routes.length < args.maxRoutes) {
      const route = queue.shift();
      if (visited.has(route)) continue;
      visited.add(route);
      const url = new URL(route, canonical.origin).href;
      const record = { route, url: sanitizeUrl(url), status: null, error: null, surface: null };
      try {
        await assertSameOriginRedirects(url, canonical.origin, `Route '${route}'`, args.timeout);
        const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: args.timeout });
        record.status = response?.status() ?? null;
        await page.waitForTimeout(args.settleMs);
        record.surface = sanitizeSurface(await inspectPage(page));
        for (const href of record.surface.anchors) {
          const candidate = normalizeRoute(href, canonical.origin);
          if (candidate && !queued.has(candidate) && !visited.has(candidate)) {
            queued.add(candidate);
            queue.push(candidate);
          }
        }
      } catch (error) {
        record.error = sanitizeText(error.message);
      }
      routes.push(record);
    }

    const sourceMaps = {
      schemaVersion: 1,
      generatedAt: new Date().toISOString(),
      limits: { maxBodyBytes: args.sourceMapMaxBytes },
      resources: (await Promise.all(sourceMapTasks.values())).sort((a, b) => a.resourceUrl.localeCompare(b.resourceUrl)),
    };
    const output = {
      schemaVersion: 1,
      generatedAt: new Date().toISOString(),
      canonicalUrl: sanitizeUrl(canonical.href),
      origin: canonical.origin,
      limits: { maxRoutes: args.maxRoutes, timeout: args.timeout, settleMs: args.settleMs, sourceMapMaxBytes: args.sourceMapMaxBytes, viewport: args.viewport },
      routes,
      resources: [...resources.values()].sort((a, b) => a.url.localeCompare(b.url)),
    };
    const inventoryPath = path.resolve(args.out);
    const evidenceDir = path.dirname(inventoryPath);
    const routeMapPath = path.join(evidenceDir, "route-map.json");
    const networkPath = path.join(evidenceDir, "network", "requests.json");
    const sourceMapsPath = path.join(evidenceDir, "source-maps.json");
    const routeMap = {
      schemaVersion: 1,
      generatedAt: output.generatedAt,
      routes: routes.map(({ route, url, status, error }) => ({ route, url, status, error })),
    };
    const network = {
      schemaVersion: 1,
      generatedAt: output.generatedAt,
      requests: output.resources,
    };
    await mkdir(evidenceDir, { recursive: true });
    await mkdir(path.dirname(networkPath), { recursive: true });
    await Promise.all([
      writeFile(inventoryPath, `${JSON.stringify(output, null, 2)}\n`, "utf8"),
      writeFile(routeMapPath, `${JSON.stringify(routeMap, null, 2)}\n`, "utf8"),
      writeFile(networkPath, `${JSON.stringify(network, null, 2)}\n`, "utf8"),
      writeFile(sourceMapsPath, `${JSON.stringify(sourceMaps, null, 2)}\n`, "utf8"),
    ]);
    console.log(JSON.stringify({
      out: inventoryPath,
      routeMap: routeMapPath,
      network: networkPath,
      sourceMaps: sourceMapsPath,
      routes: routes.length,
      resources: output.resources.length,
      sourceMapCandidates: sourceMaps.resources.length,
    }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(sanitizeText(error.stack || error.message));
  process.exitCode = 1;
});
