"""Shared URL boundary checks for GCW Python tools."""

from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlparse


SENSITIVE_QUERY_KEY = re.compile(
    r"(?:^|[-_])(?:key|api[-_]?key|access[-_]?token|token|auth|authorization|signature|sig|secret|password|passwd|credential|code|session|jwt)$",
    re.I,
)


def validate_public_url(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        raise ValueError(f"{label} must be an absolute http(s) URL")
    if parsed.username or parsed.password:
        raise ValueError(f"{label} must not contain embedded credentials")
    if any(SENSITIVE_QUERY_KEY.search(key) for key, _ in parse_qsl(parsed.query, keep_blank_values=True)):
        raise ValueError(f"{label} must not contain credential-like query parameters")


def validate_relative_route(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        raise ValueError(f"{label} must stay on the configured origin")
    if any(SENSITIVE_QUERY_KEY.search(key) for key, _ in parse_qsl(parsed.query, keep_blank_values=True)):
        raise ValueError(f"{label} must not contain credential-like query parameters")
