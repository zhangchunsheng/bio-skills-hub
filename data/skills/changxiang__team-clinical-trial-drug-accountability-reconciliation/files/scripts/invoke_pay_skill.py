#!/usr/bin/env python3
"""Invoke the Pay Skill gateway with a privacy-preserving payment envelope."""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import ssl
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit


SERVICE_BASE_URL = "https://skill.wiffar.com"
SKILL_ID = "team-clinical-trial-drug-accountability-reconciliation"
SKILL_VERSION = "2.0.2"
MAX_REQUEST_BYTES = 2_000_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Invoke a production SkillHub Pay Skill")
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument("--request-id", default=None)
    parser.add_argument("--out-trade-no", default=None)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the minimal payment envelope without making a network request",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = args.input_json.read_bytes()
    if len(raw) > MAX_REQUEST_BYTES:
        raise SystemExit("Input JSON exceeds the 2 MB client limit")
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("Input JSON must contain an object")
    canonical_input = json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    envelope = {
        "schema_version": "pay-skill-invocation-v2",
        "skill_id": SKILL_ID,
        "skill_version": SKILL_VERSION,
        "input_sha256": hashlib.sha256(canonical_input).hexdigest(),
        "input_bytes": len(raw),
    }
    body = json.dumps(envelope, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if args.dry_run:
        print(body.decode("utf-8"))
        return 0
    request_id = args.request_id or str(uuid.uuid4())
    headers = {
        "Content-Type": "application/json",
        "X-Request-Id": request_id,
    }
    if args.out_trade_no:
        headers["X-Out-Trade-No"] = args.out_trade_no
    service = urlsplit(SERVICE_BASE_URL)
    if service.scheme != "https" or not service.hostname or service.username or service.password:
        raise SystemExit("The configured Pay Skill service must use a credential-free HTTPS URL")
    endpoint = service.path or "/"
    connection = http.client.HTTPSConnection(
        service.hostname,
        port=service.port or 443,
        timeout=args.timeout,
        context=ssl.create_default_context(),
    )
    try:
        connection.request("POST", endpoint, body=body, headers=headers)
        response = connection.getresponse()
        status = response.status
        response_headers = response.headers
        response_body = response.read()
    finally:
        connection.close()
    try:
        result = json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Gateway returned a non-JSON response with HTTP {status}") from exc
    output = {
        "http_status": status,
        "request_id": response_headers.get("X-Request-Id", request_id),
        "out_trade_no": response_headers.get("X-Out-Trade-No") or result.get("out_trade_no"),
        "WeixinPay-Required": response_headers.get("WeixinPay-Required"),
        "body": result,
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0 if status == 402 or 200 <= status < 300 else 1


if __name__ == "__main__":
    sys.exit(main())
