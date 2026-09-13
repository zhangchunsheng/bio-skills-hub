#!/usr/bin/env python3
"""Download authorized manifest assets to deterministic local paths."""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from url_safety import validate_public_url


def origin(url: str) -> tuple[str, str, int | None]:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    return scheme, (parsed.hostname or "").lower(), parsed.port or {"http": 80, "https": 443}.get(scheme)


class SameOriginRedirectHandler(HTTPRedirectHandler):
    def __init__(self, source_url: str):
        self.source_origin = origin(source_url)

    def redirect_request(self, request, fp, code, message, headers, new_url):
        validate_public_url(new_url, "redirect URL")
        if origin(new_url) != self.source_origin:
            raise ValueError(f"redirect left source origin: {new_url}")
        return super().redirect_request(request, fp, code, message, headers, new_url)


def download(item: dict[str, str], root: Path, refresh: bool, max_bytes: int) -> dict[str, str]:
    url = item["sourceUrl"]
    validate_public_url(url, "sourceUrl")
    relative = Path(item["localPath"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"localPath must stay inside output: {relative}")
    candidate = root / relative
    target = candidate.resolve()
    if root not in target.parents or candidate.is_symlink():
        raise ValueError(f"localPath must stay inside output: {relative}")
    expected = item.get("checksumSha256", "").lower()
    if target.exists() and not refresh:
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if not expected or digest == expected:
            return {"localPath": str(relative), "status": "skipped", "checksumSha256": digest}
    request = Request(url, headers={"User-Agent": "GCW asset downloader/1.2"})
    with build_opener(SameOriginRedirectHandler(url)).open(request, timeout=30) as response:
        final_url = response.geturl()
        validate_public_url(final_url, "redirect URL")
        if origin(final_url) != origin(url):
            raise ValueError(f"redirect left source origin: {url}")
        content_type = response.headers.get_content_type()
        configured_type = item.get("contentType", "")
        if configured_type and content_type != configured_type:
            raise ValueError(f"content type mismatch for {url}: {content_type}")
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > max_bytes:
            raise ValueError(f"asset exceeds --max-bytes: {url}")
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError(f"asset exceeds --max-bytes: {url}")
    digest = hashlib.sha256(body).hexdigest()
    if expected and digest != expected:
        raise ValueError(f"checksum mismatch for {url}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    return {"localPath": str(relative), "status": "downloaded", "checksumSha256": digest}


def download_report(item: dict[str, str], root: Path, refresh: bool, max_bytes: int) -> dict[str, str]:
    try:
        return download(item, root, refresh, max_bytes)
    except Exception as error:
        return {
            "sourceUrl": str(item.get("sourceUrl", "")),
            "localPath": str(item.get("localPath", "")),
            "status": "failed",
            "error": str(error),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--max-bytes", type=int, default=100 * 1024 * 1024)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.concurrency <= 16:
        parser.error("--concurrency must be between 1 and 16")
    if args.max_bytes < 1:
        parser.error("--max-bytes must be positive")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("reviewStatus") not in (None, "confirmed"):
        parser.error("generated asset manifest reviewStatus must be confirmed before download")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        results = list(executor.map(lambda item: download_report(item, output, args.refresh, args.max_bytes), manifest.get("assets", [])))
    print(json.dumps({"output": str(output), "assets": results}, indent=2))
    return 1 if any(item["status"] == "failed" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
