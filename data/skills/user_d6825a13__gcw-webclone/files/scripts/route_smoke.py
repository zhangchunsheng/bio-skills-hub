#!/usr/bin/env python3
"""Smoke-test public routes on a GCW preview server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from url_safety import validate_public_url, validate_relative_route


class SameOriginRedirectHandler(HTTPRedirectHandler):
    def __init__(self, origin: tuple[str, str]) -> None:
        super().__init__()
        self.origin = origin

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        target = urlparse(newurl)
        if (target.scheme, target.netloc) != self.origin:
            raise HTTPError(req.full_url, code, "redirect left the base origin", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--route", action="append", default=[])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    try:
        validate_public_url(args.base_url, "--base-url")
    except ValueError as error:
        parser.error(str(error))
    base = urlparse(args.base_url)
    opener = build_opener(SameOriginRedirectHandler((base.scheme, base.netloc)))

    checks = [{"route": route} for route in args.route]
    if args.manifest:
        loaded = json.loads(args.manifest.read_text(encoding="utf-8"))
        checks.extend(loaded.get("routes", loaded if isinstance(loaded, list) else []))
    if not checks:
        checks = [{"route": "/"}]

    results = []
    for check in checks:
        route = check["route"] if isinstance(check, dict) else str(check)
        try:
            validate_relative_route(route, f"route '{route}'")
        except ValueError as error:
            parser.error(str(error))
        expected = check.get("contains") if isinstance(check, dict) else None
        url = urljoin(args.base_url.rstrip("/") + "/", route.lstrip("/"))
        result = {"route": route, "url": url, "status": None, "passed": False, "error": None}
        try:
            request = Request(url, headers={"User-Agent": "GCW route smoke/1.1"})
            with opener.open(request, timeout=args.timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                result["status"] = response.status
                result["passed"] = response.status < 400 and (not expected or expected in body)
                if expected and expected not in body:
                    result["error"] = f"expected text not found: {expected}"
        except HTTPError as error:
            result.update(status=error.code, error=str(error))
        except URLError as error:
            result["error"] = str(error)
        results.append(result)

    report = {"baseUrl": args.base_url, "passed": all(item["passed"] for item in results), "routes": results}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
