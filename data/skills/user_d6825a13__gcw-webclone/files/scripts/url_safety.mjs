const SENSITIVE_QUERY_KEYS = /(?:^|[-_])(?:key|api[-_]?key|access[-_]?token|token|auth|authorization|signature|sig|secret|password|passwd|credential|code|session|jwt)$/i;

export function hasSensitiveQuery(url) {
  return [...url.searchParams.keys()].some((key) => SENSITIVE_QUERY_KEYS.test(key));
}

export function parsePublicHttpUrl(value, label = "URL", { allowSensitiveQuery = false } = {}) {
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error(`${label} must be an absolute http(s) URL`);
  }
  if (!["http:", "https:"].includes(url.protocol) || !url.hostname) {
    throw new Error(`${label} must be an absolute http(s) URL`);
  }
  if (url.username || url.password) {
    throw new Error(`${label} must not contain embedded credentials`);
  }
  if (!allowSensitiveQuery && hasSensitiveQuery(url)) {
    throw new Error(`${label} must not contain credential-like query parameters`);
  }
  return url;
}

export function sanitizeUrl(value) {
  try {
    const url = new URL(value);
    url.username = url.username ? "REDACTED" : "";
    url.password = url.password ? "REDACTED" : "";
    for (const key of [...url.searchParams.keys()]) {
      if (SENSITIVE_QUERY_KEYS.test(key)) url.searchParams.set(key, "REDACTED");
    }
    url.hash = "";
    return url.href;
  } catch {
    return value;
  }
}

export function sanitizeText(value) {
  return String(value).replace(/https?:\/\/[^\s"'<>]+/gi, (match) => {
    const trailing = match.match(/[),.;:]+$/)?.[0] || "";
    const url = trailing ? match.slice(0, -trailing.length) : match;
    return `${sanitizeUrl(url)}${trailing}`;
  });
}

export function joinSameOrigin(baseValue, route, label = "route") {
  const base = parsePublicHttpUrl(baseValue, "base URL");
  if (typeof route !== "string" || !route.trim()) throw new Error(`${label} must be a non-empty string`);
  const target = new URL(route, base.href.endsWith("/") ? base.href : `${base.href}/`);
  if (target.origin !== base.origin) throw new Error(`${label} must stay on ${base.origin}`);
  return target.href;
}

export async function assertSameOriginRedirects(value, allowedOrigin, label = "URL", timeoutMs = 30000) {
  let current = parsePublicHttpUrl(value, label);
  for (let hop = 0; hop < 10; hop += 1) {
    const response = await fetch(current, { method: "GET", redirect: "manual", signal: AbortSignal.timeout(timeoutMs) });
    await response.body?.cancel();
    if (response.status < 300 || response.status >= 400) return current.href;
    const location = response.headers.get("location");
    if (!location) return current.href;
    const target = new URL(location, current);
    if (target.origin !== allowedOrigin) throw new Error(`${label} redirect left the allowed origin`);
    current = parsePublicHttpUrl(target.href, `${label} redirect`);
  }
  throw new Error(`${label} exceeded 10 redirects`);
}
