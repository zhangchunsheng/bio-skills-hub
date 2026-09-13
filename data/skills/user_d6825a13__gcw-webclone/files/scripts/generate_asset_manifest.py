#!/usr/bin/env python3
"""Generate a review-gated asset manifest draft from GCW inventory evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qsl, unquote, urlencode, urlparse, urlunparse

from url_safety import SENSITIVE_QUERY_KEY, validate_public_url


TYPE_CATEGORIES = {
    "image": "images",
    "font": "fonts",
    "media": "media",
    "stylesheet": "styles",
    "script": "scripts",
}
EXTENSION_CATEGORIES = {
    ".avif": "images", ".gif": "images", ".jpeg": "images", ".jpg": "images",
    ".png": "images", ".svg": "images", ".webp": "images",
    ".eot": "fonts", ".otf": "fonts", ".ttf": "fonts", ".woff": "fonts", ".woff2": "fonts",
    ".aac": "media", ".m4a": "media", ".mp3": "media", ".mp4": "media",
    ".ogg": "media", ".wav": "media", ".webm": "media",
    ".bin": "models", ".glb": "models", ".gltf": "models", ".ktx2": "models",
    ".wasm": "runtime",
    ".css": "styles", ".js": "scripts", ".mjs": "scripts",
}
MIME_EXTENSIONS = {
    "image/avif": ".avif", "image/jpeg": ".jpg", "image/png": ".png", "image/svg+xml": ".svg",
    "image/webp": ".webp", "font/woff": ".woff", "font/woff2": ".woff2",
    "model/gltf-binary": ".glb", "model/gltf+json": ".gltf",
}
UNSUPPORTED_TYPES = {"document", "eventsource", "fetch", "websocket", "xhr"}


def redact_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return "REDACTED"
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    try:
        port = parsed.port
    except ValueError:
        return "REDACTED"
    if port:
        host = f"{host}:{port}"
    if parsed.username or parsed.password:
        host = f"REDACTED@{host}"
    query = urlencode([
        (key, "REDACTED" if SENSITIVE_QUERY_KEY.search(key) else item)
        for key, item in parse_qsl(parsed.query, keep_blank_values=True)
    ])
    return urlunparse((parsed.scheme, host, parsed.path, parsed.params, query, ""))


def add_candidate(candidates: dict[str, dict], url: object, source: str, resource_type: str = "", mime_type: str = "") -> None:
    if not isinstance(url, str) or not url:
        return
    item = candidates.setdefault(url, {"types": set(), "mimeTypes": set(), "sources": set()})
    if resource_type:
        item["types"].add(resource_type.lower())
    if mime_type:
        item["mimeTypes"].add(mime_type.split(";", 1)[0].strip().lower())
    item["sources"].add(source)


def collect_candidates(inventory: dict) -> dict[str, dict]:
    candidates: dict[str, dict] = {}
    for resource in inventory.get("resources", []):
        if isinstance(resource, dict):
            add_candidate(candidates, resource.get("url"), "resources", resource.get("resourceType", ""), resource.get("mimeType", ""))
    for route in inventory.get("routes", []):
        if not isinstance(route, dict) or not isinstance(route.get("surface"), dict):
            continue
        surface = route["surface"]
        route_name = str(route.get("route", "/"))
        for url in surface.get("images", []):
            add_candidate(candidates, url, f"route:{route_name}:images", "image")
        for video in surface.get("videos", []):
            if isinstance(video, dict):
                add_candidate(candidates, video.get("src"), f"route:{route_name}:videos", "media")
        for url in surface.get("scripts", []):
            add_candidate(candidates, url, f"route:{route_name}:scripts", "script")
        for url in surface.get("stylesheets", []):
            add_candidate(candidates, url, f"route:{route_name}:stylesheets", "stylesheet")
        for resource in surface.get("performanceResources", []):
            if isinstance(resource, dict):
                add_candidate(candidates, resource.get("url"), f"route:{route_name}:performance", resource.get("initiatorType", ""))
    return candidates


def classify(url: str, types: set[str], mime_types: set[str]) -> str | None:
    suffix = PurePosixPath(urlparse(url).path).suffix.lower()
    if suffix in EXTENSION_CATEGORIES:
        return EXTENSION_CATEGORIES[suffix]
    for resource_type in sorted(types):
        if resource_type in TYPE_CATEGORIES:
            return TYPE_CATEGORIES[resource_type]
    for mime_type in sorted(mime_types):
        if mime_type.startswith("image/"):
            return "images"
        if mime_type.startswith("font/"):
            return "fonts"
        if mime_type.startswith(("audio/", "video/")):
            return "media"
    if types and types.issubset(UNSUPPORTED_TYPES):
        return None
    return None


def extension_for(url: str, mime_type: str) -> str:
    suffix = PurePosixPath(urlparse(url).path).suffix.lower()
    if suffix in EXTENSION_CATEGORIES:
        return suffix
    return MIME_EXTENSIONS.get(mime_type) or mimetypes.guess_extension(mime_type, strict=False) or ".bin"


def local_path(url: str, category: str, mime_type: str) -> str:
    name = unquote(PurePosixPath(urlparse(url).path).name)
    extension = extension_for(url, mime_type)
    stem = name[:-len(extension)] if extension and name.lower().endswith(extension.lower()) else Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-._") or "asset"
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
    return f"public/assets/{category}/{stem}-{digest}{extension}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists() or args.out.is_symlink():
        parser.error(f"output already exists; review or choose another path: {args.out}")
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        parser.error(f"cannot read inventory: {error}")
    if not isinstance(inventory, dict):
        parser.error("inventory must be a JSON object")

    assets = []
    excluded = []
    for url, candidate in sorted(collect_candidates(inventory).items()):
        try:
            validate_public_url(url, "asset URL")
        except ValueError:
            excluded.append({
                "sourceUrl": redact_url(url),
                "reason": "sensitive-or-invalid-url",
                "discoveredFrom": sorted(candidate["sources"]),
            })
            continue
        category = classify(url, candidate["types"], candidate["mimeTypes"])
        if not category:
            excluded.append({
                "sourceUrl": url,
                "reason": "unsupported-resource-type",
                "resourceTypes": sorted(candidate["types"]),
                "discoveredFrom": sorted(candidate["sources"]),
            })
            continue
        mime_type = sorted(candidate["mimeTypes"])[0] if candidate["mimeTypes"] else ""
        assets.append({
            "sourceUrl": url,
            "localPath": local_path(url, category, mime_type),
            "purpose": "REVIEW REQUIRED",
            "licenseOrAttribution": "REVIEW REQUIRED before download or reuse",
            "contentType": mime_type,
            "checksumSha256": "",
            "category": category,
            "discoveredFrom": sorted(candidate["sources"]),
        })

    output = {
        "schemaVersion": 1,
        "reviewStatus": "pending",
        "sourceInventory": args.inventory.name,
        "assets": assets,
        "excluded": excluded,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out.resolve()), "assets": len(assets), "excluded": len(excluded), "reviewStatus": "pending"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
