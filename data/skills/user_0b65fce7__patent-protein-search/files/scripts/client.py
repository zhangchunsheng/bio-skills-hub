#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_EBI_URL = "https://www.ebi.ac.uk/Tools/services/rest/fasta"
DEFAULT_DATABASES = ("epo", "jpo", "kipo", "uspto", "nrpl1", "nrpl2")
SUPPORTED_DATABASES = DEFAULT_DATABASES
TERMINAL_STATUSES = {"finished", "partial", "failed"}
PROTEIN_ALPHABET = frozenset("ACDEFGHIKLMNPQRSTVWYBXZJUO")
MAX_SEQUENCE_LENGTH = 100_000
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
PLAN_ID = re.compile(r"^plp_[0-9a-f]{24}$")
SEARCH_ID = re.compile(r"^pls_[0-9a-f]{24}$")
JOB_ID = re.compile(r"^[A-Za-z0-9._-]{8,160}$")
IDEMPOTENCY_KEY = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
PATENT_REFERENCE = re.compile(
    r"\b((?:WO|W0|US|EP|JP|KR|CN|CA|AU|GB|DE|FR)\s*[/.-]?\s*\d{6,}(?:\s*[A-Z]\d?)?)\b",
    re.IGNORECASE,
)


class ClientError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None, code: str | None = None):
        super().__init__(message)
        self.status = status
        self.code = code


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def state_dir_from_env() -> Path:
    configured = os.getenv("PATENT_SEQUENCE_STATE_DIR", "").strip()
    return Path(configured).expanduser() if configured else Path.home() / ".cache" / "patent-sequence-local"


AUTO_EMAIL_DOMAIN = "github.com"
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def auto_email_domain() -> str:
    """EMBL-EBI rejects addresses whose domain has no MX record, so the
    fallback domain must be a real routable domain. Override with
    PATENT_SEQUENCE_AUTO_EMAIL_DOMAIN (e.g. your own domain)."""
    value = os.getenv("PATENT_SEQUENCE_AUTO_EMAIL_DOMAIN", "").strip().lstrip("@").rstrip(".")
    if value and EMAIL_PATTERN.fullmatch(f"x@{value}"):
        return value
    return AUTO_EMAIL_DOMAIN


def contact_email_from_env(*, required: bool) -> str | None:
    value = os.getenv("EBI_CONTACT_EMAIL", "").strip()
    if value and EMAIL_PATTERN.fullmatch(value):
        return value
    if required:
        raise ClientError(
            "No usable contact email: set EBI_CONTACT_EMAIL or allow writing to the state directory"
        )
    return None


def resolve_contact_email(root: Path, *, required: bool) -> tuple[str | None, str]:
    """Resolve the EMBL-EBI contact address.

    Priority: EBI_CONTACT_EMAIL env > persisted auto address > newly generated
    address (only when required, i.e. right before an external submission).
    The address value is never written into plan/search/cache/report files;
    it lives only in the dedicated state config and the provider request.
    """
    env_value = contact_email_from_env(required=False)
    if env_value:
        return env_value, "env"
    config_path = root / "contact-email.json"
    try:
        stored = json.loads(config_path.read_text(encoding="utf-8"))
        email = str(stored.get("email", "")).strip()
        if email and EMAIL_PATTERN.fullmatch(email):
            return email, "auto-persisted"
    except (OSError, ValueError, AttributeError):
        pass
    if not required:
        return None, "none"
    email = f"patent-seq-{uuid.uuid4().hex[:8]}@{auto_email_domain()}"
    write_json(config_path, {"email": email, "source": "auto", "created_at": iso(utc_now())})
    return email, "auto-generated"


def ebi_url_from_env() -> str:
    value = os.getenv("PATENT_SEQUENCE_EBI_URL", DEFAULT_EBI_URL).strip().rstrip("/")
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ClientError("PATENT_SEQUENCE_EBI_URL must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ClientError("EMBL-EBI URL cannot contain credentials, a query, or a fragment")
    if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ClientError("The external provider must use HTTPS; HTTP is reserved for local tests")
    return value


def normalize_protein(value: str, *, max_length: int = MAX_SEQUENCE_LENGTH) -> str:
    lines = value.strip().splitlines()
    if not lines:
        raise ClientError("Protein sequence is empty")
    headers = [index for index, line in enumerate(lines) if line.lstrip().startswith(">")]
    if headers and headers != [0]:
        raise ClientError("Only one FASTA record is supported")
    if headers == [0]:
        lines = lines[1:]
    sequence = re.sub(r"[\s\d]+", "", "".join(lines)).upper()
    if sequence.endswith("*"):
        sequence = sequence[:-1]
    if len(sequence) < 10:
        raise ClientError("Protein sequence must contain at least 10 amino acids")
    if len(sequence) > max_length:
        raise ClientError(f"Protein sequence exceeds {max_length} amino acids")
    invalid = sorted(set(sequence) - PROTEIN_ALPHABET)
    if invalid:
        raise ClientError("Protein sequence contains invalid characters: " + ", ".join(invalid))
    return sequence


def load_sequence(args: argparse.Namespace) -> str:
    if getattr(args, "sequence", None):
        value = args.sequence
    else:
        path = Path(args.sequence_file)
        try:
            value = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ClientError(f"Cannot read sequence file: {path}") from exc
    return normalize_protein(value)


def sequence_digest(sequence: str) -> str:
    return hashlib.sha256(sequence.encode("ascii")).hexdigest()[:16]


def ensure_state_dirs(root: Path) -> None:
    for name in ("plans", "searches", "cache", "enrichment-plans", "enrichments"):
        (root / name).mkdir(parents=True, exist_ok=True)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def read_json(path: Path, *, missing_message: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ClientError(missing_message) from exc
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ClientError(f"Cannot read local state: {path}") from exc
    if not isinstance(value, dict):
        raise ClientError(f"Invalid local state: {path}")
    return value


def criteria_from_args(args: argparse.Namespace) -> dict[str, Any]:
    if not 0 <= args.min_identity <= 100:
        raise ClientError("min_identity must be between 0 and 100")
    if not 0 <= args.min_query_coverage <= 100:
        raise ClientError("min_query_coverage must be between 0 and 100")
    if not 0 < args.max_evalue <= 1000:
        raise ClientError("max_evalue must be greater than 0 and no more than 1000")
    if not 1 <= args.max_hits <= 100:
        raise ClientError("max_hits must be between 1 and 100")
    return {
        "min_identity": args.min_identity,
        "min_query_coverage": args.min_query_coverage,
        "max_evalue": args.max_evalue,
        "max_hits": args.max_hits,
        "include_alignment": args.include_alignment,
    }


def cache_key(query_digest: str, database: str, criteria: dict[str, Any]) -> str:
    canonical = json.dumps(
        {"query_digest": query_digest, "database": database, "criteria": criteria},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def cache_path(root: Path, query_digest: str, database: str, criteria: dict[str, Any]) -> Path:
    return root / "cache" / f"{cache_key(query_digest, database, criteria)}.json"


def cache_is_valid(path: Path, *, ttl_seconds: int) -> bool:
    if not path.exists():
        return False
    return time.time() - path.stat().st_mtime <= ttl_seconds


class EbiClient:
    def __init__(self, *, base_url: str, email: str, timeout_seconds: float):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.timeout_seconds = timeout_seconds
        self.opener = urllib.request.build_opener(NoRedirectHandler())

    def request(self, method: str, path: str, *, form: dict[str, str] | None = None) -> bytes:
        if not path or "://" in path or path.startswith("//"):
            raise ClientError("Only EMBL-EBI relative paths are allowed")
        data = urllib.parse.urlencode(form).encode("utf-8") if form else None
        headers = {
            "Accept": "application/json, application/xml, text/plain",
            "User-Agent": "Patent-Sequence-Local-Skill/0.2",
        }
        if form:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        request = urllib.request.Request(
            f"{self.base_url}/{path.lstrip('/')}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with self.opener.open(request, timeout=self.timeout_seconds) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except urllib.error.HTTPError as exc:
            if 300 <= exc.code < 400:
                raise ClientError("EMBL-EBI redirects are not allowed", status=exc.code) from exc
            if exc.code == 429:
                raise ClientError("EMBL-EBI rate limited the request", status=429, code="RATE_LIMITED") from exc
            if exc.code == 400:
                try:
                    body = exc.read().decode("utf-8", errors="replace").lower()
                except Exception:
                    body = ""
                if "valid email" in body:
                    raise ClientError(
                        "EMBL-EBI rejected the contact email; set EBI_CONTACT_EMAIL to a real address, then retry with a NEW idempotency key",
                        status=400,
                        code="INVALID_CONTACT_EMAIL",
                    ) from exc
            raise ClientError(f"EMBL-EBI returned HTTP {exc.code}", status=exc.code) from exc
        except urllib.error.URLError as exc:
            raise ClientError("Cannot reach EMBL-EBI") from exc
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ClientError("EMBL-EBI response exceeded 16 MiB")
        return raw

    def submit(
        self,
        *,
        sequence: str,
        database: str,
        max_hits: int,
        max_evalue: float,
    ) -> str:
        raw = self.request(
            "POST",
            "run/",
            form={
                "email": self.email,
                "title": "patent-sequence-local-search",
                "program": "fasta",
                "stype": "protein",
                "database": database,
                "sequence": f">query\n{sequence}\n",
                "scores": str(max(10, max_hits)),
                "alignments": str(max(10, max_hits)),
                "expupperlim": f"{max_evalue:g}",
            },
        )
        job_id = raw.decode("utf-8", errors="replace").strip()
        if not JOB_ID.fullmatch(job_id):
            raise ClientError("EMBL-EBI returned an invalid job ID")
        return job_id

    def status(self, job_id: str) -> str:
        if not JOB_ID.fullmatch(job_id):
            raise ClientError("Invalid EMBL-EBI job ID")
        return self.request("GET", f"status/{job_id}").decode("utf-8", errors="replace").strip().upper()

    def result_types(self, job_id: str) -> list[str]:
        raw = self.request("GET", f"resulttypes/{job_id}")
        text = raw.decode("utf-8", errors="replace").strip()
        if text.startswith("{"):
            try:
                payload = json.loads(text)
                identifiers = [
                    str(node.get("identifier") or "").strip()
                    for node in payload.get("types") or []
                ]
            except (ValueError, AttributeError) as exc:
                raise ClientError("Cannot parse EMBL-EBI result types") from exc
            return [name for name in identifiers if name]
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise ClientError("Cannot parse EMBL-EBI result types") from exc
        return [node.text.strip() for node in root.findall(".//identifier") if node.text and node.text.strip()]

    def result(self, job_id: str, result_type: str) -> bytes:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", result_type):
            raise ClientError("Invalid EMBL-EBI result type")
        return self.request("GET", f"result/{job_id}/{result_type}")


def number(value: Any, *, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def integer(value: Any, *, default: int | None = None) -> int | None:
    parsed = number(value)
    return default if parsed is None else int(parsed)


def percentage(value: Any) -> float:
    parsed = number(value, default=0.0) or 0.0
    if 0 <= parsed <= 1:
        parsed *= 100
    return round(max(0.0, min(parsed, 100.0)), 3)


def coverage(start: Any, end: Any, total: int | None, fallback: int | None) -> float | None:
    first, last = integer(start), integer(end)
    span = abs(last - first) + 1 if first is not None and last is not None else fallback
    if not span or not total or total <= 0:
        return None
    return round(min(100.0, 100.0 * span / total), 3)


def patent_publications(*values: Any) -> list[str]:
    found: list[str] = []
    for value in values:
        for match in PATENT_REFERENCE.findall(str(value or "")):
            normalized = re.sub(r"[\s/.-]+", "", match.upper())
            if normalized.startswith("W0"):
                normalized = "WO" + normalized[2:]
            if normalized not in found:
                found.append(normalized)
    return found


def parse_ebi_json(raw: bytes, *, database: str, criteria: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ClientError("EMBL-EBI JSON result is invalid") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("hits") or [], list):
        raise ClientError("EMBL-EBI JSON result has an unexpected shape")
    query_length = integer(payload.get("query_len"))
    normalized: list[dict[str, Any]] = []
    for hit in payload.get("hits") or []:
        if not isinstance(hit, dict):
            continue
        hsps = [item for item in (hit.get("hit_hsps") or []) if isinstance(item, dict)]
        if not hsps:
            continue
        best = min(
            hsps,
            key=lambda item: (
                number(item.get("hsp_expect"), default=float("inf")),
                -(number(item.get("hsp_bit_score"), default=0.0) or 0.0),
            ),
        )
        align_length = integer(best.get("hsp_align_len"))
        identity = percentage(best.get("hsp_identity"))
        query_coverage = coverage(
            best.get("hsp_query_from"), best.get("hsp_query_to"), query_length, align_length
        ) or 0.0
        target_length = integer(hit.get("hit_len"))
        target_coverage = coverage(
            best.get("hsp_hit_from"), best.get("hsp_hit_to"), target_length, align_length
        )
        evalue = number(best.get("hsp_expect"), default=float("inf")) or 0.0
        if identity < criteria["min_identity"] or query_coverage < criteria["min_query_coverage"]:
            continue
        if evalue > criteria["max_evalue"]:
            continue
        target_id = str(hit.get("hit_id") or hit.get("hit_acc") or "").strip()
        if not target_id:
            continue
        definition = str(hit.get("hit_def") or hit.get("hit_desc") or "")[:2000]
        item: dict[str, Any] = {
            "rank": 0,
            "source_database": str(hit.get("hit_db") or database),
            "target_id": target_id,
            "target_accession": str(hit.get("hit_acc") or "") or None,
            "target_definition": definition,
            "target_length": target_length,
            "patent_publications": patent_publications(
                hit.get("hit_def"), hit.get("hit_desc"), hit.get("hit_id")
            ),
            "identity": identity,
            "query_coverage": query_coverage,
            "target_coverage": target_coverage,
            "evalue": evalue,
            "score": number(best.get("hsp_score") or best.get("hsp_sw_score")),
            "bit_score": number(best.get("hsp_bit_score")),
            "evidence_url": str(
                hit.get("hit_url") or hit.get("hit_dbfetch_url") or hit.get("hit_xref_url") or ""
            ) or None,
            "evidence_scope": "sequence_similarity_only",
        }
        if criteria["include_alignment"]:
            item["alignment"] = {
                "query_from": integer(best.get("hsp_query_from")),
                "query_to": integer(best.get("hsp_query_to")),
                "target_from": integer(best.get("hsp_hit_from")),
                "target_to": integer(best.get("hsp_hit_to")),
                "query_sequence": None,
                "match_sequence": str(best.get("hsp_mseq") or "") or None,
                "target_sequence": str(best.get("hsp_hseq") or "") or None,
            }
        normalized.append(item)
    normalized.sort(key=lambda item: (item["evalue"], -item["identity"], -item["query_coverage"]))
    normalized = normalized[: criteria["max_hits"]]
    for rank, item in enumerate(normalized, 1):
        item["rank"] = rank
    return normalized


def match_class(hit: dict[str, Any]) -> str:
    if hit.get("identity") == 100 and hit.get("query_coverage") == 100:
        return "QX_exact_query"
    if (hit.get("identity") or 0) >= 90 and (hit.get("query_coverage") or 0) >= 90:
        return "QH_high_full"
    return "QS_similarity_candidate"


def summarize_search(search: dict[str, Any], *, top: int) -> dict[str, Any]:
    databases = []
    for db in search.get("databases") or []:
        candidates = []
        for hit in (db.get("hits") or [])[:top]:
            candidates.append(
                {
                    "target_id": hit.get("target_id"),
                    "target_accession": hit.get("target_accession"),
                    "patent_publications": hit.get("patent_publications") or [],
                    "identity": hit.get("identity"),
                    "query_coverage": hit.get("query_coverage"),
                    "target_coverage": hit.get("target_coverage"),
                    "evalue": hit.get("evalue"),
                    "sequence_match_class": match_class(hit),
                    "patent_mapping_class": (
                        "P1_publication_parsed"
                        if hit.get("patent_publications")
                        else "P0_accession_only"
                    ),
                    "claim_link_class": "C0_not_verified",
                    "evidence_scope": "sequence_similarity_only",
                }
            )
        databases.append(
            {
                "database": db.get("database"),
                "status": db.get("status"),
                "cache_hit": db.get("cache_hit"),
                "external_submission": db.get("external_submission"),
                "hit_count": db.get("hit_count"),
                "error_code": db.get("error_code"),
                "message": db.get("message"),
                "top_candidates": candidates,
            }
        )
    return {
        "search_id": search.get("search_id"),
        "status": search.get("status"),
        "provider": "embl_ebi_fasta",
        "query_length": search.get("query_length"),
        "query_digest": search.get("query_digest"),
        "criteria": search.get("criteria"),
        "external_submissions": search.get("external_submissions", 0),
        "hit_count": sum(item.get("hit_count") or 0 for item in search.get("databases") or []),
        "databases": databases,
        "coverage": search.get("coverage"),
        "patseek_used": False,
        "message": search.get("message"),
    }


def recalculate_search(search: dict[str, Any]) -> None:
    databases = search.get("databases") or []
    pending = [item for item in databases if item.get("status") in {"queued", "running", "submitting"}]
    failed = [item for item in databases if item.get("status") == "failed"]
    finished = [item for item in databases if item.get("status") == "finished"]
    if pending:
        status = "running"
    elif failed and finished:
        status = "partial"
    elif failed:
        status = "failed"
    else:
        status = "finished"
    searched = [item["database"] for item in finished]
    failed_names = [item["database"] for item in failed]
    empty = [item["database"] for item in finished if not item.get("hit_count")]
    search["status"] = status
    search["coverage"] = {
        "searched": searched,
        "failed": failed_names,
        "empty": empty,
        "not_searched": [
            item["database"] for item in pending if item.get("status") == "submitting"
        ],
        "limitations": [
            "Sequence similarity does not establish claim scope, validity, FTO, or infringement.",
            "Database content and update timing are controlled by EMBL-EBI.",
            "Empty results do not prove absence; cross-database hits are not family-deduplicated.",
        ],
    }
    search["updated_at"] = iso(utc_now())
    search["message"] = {
        "running": "Local agent is waiting for EMBL-EBI jobs.",
        "finished": "All selected databases completed.",
        "partial": "Some selected databases failed.",
        "failed": "All selected databases failed.",
    }[status]


def create_plan(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    sequence = load_sequence(args)
    digest = sequence_digest(sequence)
    criteria = criteria_from_args(args)
    databases = args.database or list(DEFAULT_DATABASES)
    ttl_seconds = args.cache_ttl_hours * 3600
    items = []
    for database in databases:
        hit = cache_is_valid(cache_path(root, digest, database, criteria), ttl_seconds=ttl_seconds)
        items.append(
            {
                "database": database,
                "cache_hit": hit,
                "estimated_external_submissions": 0 if hit else 1,
            }
        )
    now = utc_now()
    plan = {
        "schema_version": 1,
        "plan_id": f"plp_{uuid.uuid4().hex[:24]}",
        "query_length": len(sequence),
        "query_digest": digest,
        "criteria": criteria,
        "databases": items,
        "estimated_external_submissions": sum(
            item["estimated_external_submissions"] for item in items
        ),
        "external_destination": ebi_url_from_env(),
        "external_submission_required_on_cache_miss": True,
        "monetary_cost": 0,
        "contact_email_configured": bool(contact_email_from_env(required=False)),
        "contact_email_source": resolve_contact_email(root, required=False)[1],
        "sequence_persistence": "raw query sequence is not stored; only length and digest are retained",
        "created_at": iso(now),
        "expires_at": iso(now + timedelta(minutes=args.plan_ttl_minutes)),
        "cache_ttl_hours": args.cache_ttl_hours,
    }
    write_json(root / "plans" / f"{plan['plan_id']}.json", plan)
    return plan


def execute_plan(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    if not PLAN_ID.fullmatch(args.plan_id):
        raise ClientError("Invalid local plan ID")
    if not IDEMPOTENCY_KEY.fullmatch(args.idempotency_key):
        raise ClientError("Idempotency key must be 8-128 characters: A-Z a-z 0-9 . _ : -")
    plan = read_json(root / "plans" / f"{args.plan_id}.json", missing_message="Local plan not found")
    if parse_time(plan["expires_at"]) <= utc_now():
        raise ClientError("Local plan expired; create a new plan")
    sequence = load_sequence(args)
    if sequence_digest(sequence) != plan.get("query_digest") or len(sequence) != plan.get("query_length"):
        raise ClientError("Execution sequence does not match the local plan")
    stable = hashlib.sha256(f"{args.plan_id}\0{args.idempotency_key}".encode("utf-8")).hexdigest()[:24]
    search_id = f"pls_{stable}"
    search_path = root / "searches" / f"{search_id}.json"
    if search_path.exists():
        return read_json(search_path, missing_message="Local search not found")

    ttl_seconds = int(plan.get("cache_ttl_hours", 24)) * 3600
    databases = []
    misses = []
    for planned in plan["databases"]:
        database = planned["database"]
        path = cache_path(root, plan["query_digest"], database, plan["criteria"])
        if cache_is_valid(path, ttl_seconds=ttl_seconds):
            cached = read_json(path, missing_message="Local cache disappeared")
            databases.append(
                {
                    "database": database,
                    "status": "finished",
                    "cache_hit": True,
                    "external_submission": False,
                    "external_job_id": None,
                    "hit_count": len(cached.get("hits") or []),
                    "hits": cached.get("hits") or [],
                    "message": "Loaded from local cache.",
                    "error_code": None,
                }
            )
        else:
            misses.append(database)
            databases.append(
                {
                    "database": database,
                    "status": "submitting",
                    "cache_hit": False,
                    "external_submission": True,
                    "external_job_id": None,
                    "hit_count": 0,
                    "hits": [],
                    "message": "Not submitted yet.",
                    "error_code": None,
                }
            )
    if misses and not args.confirm_external_submission:
        raise ClientError(
            "External submission confirmation is required for: " + ", ".join(misses)
        )
    email, email_source = resolve_contact_email(root, required=bool(misses))
    now = utc_now()
    search = {
        "schema_version": 1,
        "search_id": search_id,
        "plan_id": args.plan_id,
        "idempotency_key_digest": hashlib.sha256(args.idempotency_key.encode()).hexdigest()[:12],
        "status": "running" if misses else "finished",
        "query_length": plan["query_length"],
        "query_digest": plan["query_digest"],
        "criteria": plan["criteria"],
        "external_destination": plan["external_destination"],
        "external_submissions": 0,
        "contact_email_source": email_source,
        "databases": databases,
        "created_at": iso(now),
        "updated_at": iso(now),
        "coverage": {},
        "message": "Preparing external submissions." if misses else "Loaded entirely from cache.",
    }
    write_json(search_path, search)
    if not misses:
        recalculate_search(search)
        write_json(search_path, search)
        return search

    provider = EbiClient(
        base_url=plan["external_destination"],
        email=email or "",
        timeout_seconds=args.request_timeout,
    )
    for item in search["databases"]:
        if item["database"] not in misses:
            continue
        write_json(search_path, search)
        try:
            job_id = provider.submit(
                sequence=sequence,
                database=item["database"],
                max_hits=plan["criteria"]["max_hits"],
                max_evalue=plan["criteria"]["max_evalue"],
            )
        except ClientError as exc:
            item.update(
                status="failed",
                error_code=exc.code or "SUBMISSION_FAILED",
                message=str(exc),
            )
        else:
            item.update(
                status="queued",
                external_job_id=job_id,
                message="Submitted to EMBL-EBI.",
            )
            search["external_submissions"] += 1
        write_json(search_path, search)
    recalculate_search(search)
    write_json(search_path, search)
    return search


def poll_search(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    if not SEARCH_ID.fullmatch(args.search_id):
        raise ClientError("Invalid local search ID")
    path = root / "searches" / f"{args.search_id}.json"
    search = read_json(path, missing_message="Local search not found")
    if search.get("status") in TERMINAL_STATUSES:
        return search
    provider = EbiClient(
        base_url=search["external_destination"],
        email=resolve_contact_email(root, required=True)[0] or "",
        timeout_seconds=args.request_timeout,
    )
    for item in search.get("databases") or []:
        if item.get("status") not in {"queued", "running"}:
            continue
        job_id = item.get("external_job_id")
        try:
            status = provider.status(job_id)
            if status == "FINISHED":
                result_types = provider.result_types(job_id)
                if "json" not in result_types:
                    raise ClientError("EMBL-EBI did not provide a JSON result")
                hits = parse_ebi_json(
                    provider.result(job_id, "json"),
                    database=item["database"],
                    criteria=search["criteria"],
                )
                item.update(
                    status="finished",
                    hit_count=len(hits),
                    hits=hits,
                    message="EMBL-EBI search completed.",
                    error_code=None,
                )
                write_json(
                    cache_path(root, search["query_digest"], item["database"], search["criteria"]),
                    {
                        "query_digest": search["query_digest"],
                        "database": item["database"],
                        "criteria": search["criteria"],
                        "hits": hits,
                        "cached_at": iso(utc_now()),
                    },
                )
            elif status in {"ERROR", "FAILURE", "NOT_FOUND"}:
                item.update(
                    status="failed",
                    error_code=f"UPSTREAM_{status}",
                    message=f"EMBL-EBI job ended with {status}.",
                )
            else:
                item.update(status="running", message=f"EMBL-EBI status: {status}.")
        except ClientError as exc:
            item.update(
                status="running",
                error_code=exc.code or "POLL_RETRYABLE",
                message=str(exc),
            )
    recalculate_search(search)
    write_json(path, search)
    return search


def format_metric(value: Any, *, suffix: str = "") -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        rendered = f"{value:.3g}" if abs(value) < 0.001 else f"{value:.3f}".rstrip("0").rstrip(".")
    else:
        rendered = str(value)
    return html.escape(rendered + suffix)


def alignment_cell_classes(index: int, position: int) -> list[str]:
    return ["group-start"] if index > 0 and (position - 1) % 5 == 0 else []


def residue_row(
    sequence: str,
    peer: str | None = None,
    *,
    start_position: int = 1,
) -> str:
    cells = []
    width = max(len(sequence), len(peer or ""))
    for index in range(width):
        position = start_position + index
        residue = sequence[index] if index < len(sequence) else "-"
        other = peer[index] if peer is not None and index < len(peer) else None
        if residue == "-":
            class_name = "gap"
        elif other is None:
            class_name = "neutral"
        elif residue == other:
            class_name = "match"
        else:
            class_name = "substitution"
        classes = ["residue", class_name, *alignment_cell_classes(index, position)]
        tooltip = f"位置 {position}: {residue}"
        if other is not None and residue != other:
            tooltip += f"（对比 {other}）"
        cells.append(
            f'<span class="{" ".join(classes)}" title="{html.escape(tooltip)}">'
            f'{html.escape(residue)}</span>'
        )
    return "".join(cells)


def consensus_row(query: str, target: str, *, start_position: int = 1) -> str:
    cells = []
    for index in range(max(len(query), len(target))):
        position = start_position + index
        query_residue = query[index] if index < len(query) else "-"
        target_residue = target[index] if index < len(target) else "-"
        if query_residue == target_residue and query_residue != "-":
            character, class_name = "│", "match"
        elif "-" in {query_residue, target_residue}:
            character, class_name = "–", "gap"
        else:
            character, class_name = "●", "substitution"
        classes = [
            "residue",
            "consensus-symbol",
            class_name,
            *alignment_cell_classes(index, position),
        ]
        cells.append(
            f'<span class="{" ".join(classes)}" title="位置 {position}: '
            f'{html.escape(query_residue)}→{html.escape(target_residue)}">{character}</span>'
        )
    return "".join(cells)


def position_ruler(query: str, target: str, *, start_position: int = 1) -> str:
    cells = []
    for index in range(max(len(query), len(target))):
        position = start_position + index
        query_residue = query[index] if index < len(query) else "-"
        target_residue = target[index] if index < len(target) else "-"
        is_difference = query_residue != target_residue
        classes = ["ruler-cell", *alignment_cell_classes(index, position)]
        if is_difference:
            classes.append("difference-position")
        label = f"<b>{position}</b>" if position % 10 == 0 else ""
        marker = '<i aria-hidden="true"></i>' if is_difference else ""
        tooltip = f"位置 {position}: {query_residue}→{target_residue}"
        cells.append(
            f'<span class="{" ".join(classes)}" title="{html.escape(tooltip)}" '
            f'aria-label="{html.escape(tooltip)}">{label}{marker}</span>'
        )
    return "".join(cells)


def identity_analysis(query: str, target: str, *, target_label: str) -> str:
    width = max(len(query), len(target))
    matches = 0
    substitutions = 0
    gaps = 0
    for index in range(width):
        query_residue = query[index] if index < len(query) else "-"
        target_residue = target[index] if index < len(target) else "-"
        if query_residue == target_residue and query_residue != "-":
            matches += 1
        elif "-" in {query_residue, target_residue}:
            gaps += 1
        else:
            substitutions += 1
    identity = matches / width * 100 if width else 0.0
    identity_text = f"{identity:.2f}".rstrip("0").rstrip(".") + "%"
    escaped_target_label = html.escape(target_label)
    return (
        '<div class="identity-analysis">'
        '<div class="identity-head"><div><strong>一致性分析</strong>'
        '<span>按当前显示的比对列计算</span></div>'
        f'<span class="identity-score">{identity_text}</span></div>'
        '<div class="identity-body">'
        '<div class="identity-facts">'
        f'<div><b>{matches}/{width}</b><span>相同位点</span></div>'
        f'<div><b>{substitutions}</b><span>氨基酸替换</span></div>'
        f'<div><b>{gaps}</b><span>缺口列</span></div>'
        f'<div><b>{identity_text}</b><span>序列一致率</span></div>'
        '</div>'
        '<div class="identity-matrix-wrap"><table class="identity-matrix" '
        'aria-label="序列一致性矩阵">'
        '<thead><tr><th></th><th>Query</th>'
        f'<th title="{escaped_target_label}">Target</th></tr></thead>'
        '<tbody><tr><th>Query</th><td class="matrix-diagonal">100%</td>'
        f'<td class="matrix-pair">{identity_text}</td></tr>'
        f'<tr><th title="{escaped_target_label}">Target</th>'
        f'<td class="matrix-pair">{identity_text}</td>'
        '<td class="matrix-diagonal">100%</td></tr></tbody>'
        '</table>'
        f'<div class="matrix-caption">Target：{escaped_target_label}</div></div>'
        '</div></div>'
    )


def alignment_block(hit: dict[str, Any], query_sequence: str | None) -> str:
    alignment = hit.get("alignment") or {}
    target = str(alignment.get("target_sequence") or "")
    if not target:
        return '<p class="muted">该结果没有可显示的比对片段。</p>'
    query_from = int(alignment.get("query_from") or 1)
    query_to = int(alignment.get("query_to") or query_from + len(target) - 1)
    query_segment = None
    if query_sequence is not None:
        query_segment = query_sequence[max(0, query_from - 1) : max(query_from, query_to)]
    overview = ""
    if query_segment is not None:
        comparison_length = max(len(query_segment), len(target))
        differences: list[tuple[int, str, str]] = []
        substitution_count = 0
        gap_count = 0
        overview_cells = []
        for index in range(comparison_length):
            query_residue = query_segment[index] if index < len(query_segment) else "-"
            target_residue = target[index] if index < len(target) else "-"
            is_match = query_residue == target_residue
            if not is_match:
                differences.append((query_from + index, query_residue, target_residue))
                if "-" in {query_residue, target_residue}:
                    gap_count += 1
                else:
                    substitution_count += 1
            class_name = "overview-match" if is_match else "overview-diff"
            overview_cells.append(
                f'<span class="{class_name}" title="位置 {query_from + index}: '
                f'{html.escape(query_residue)}→{html.escape(target_residue)}"></span>'
            )
        first_tick = ((query_from + 9) // 10) * 10
        tick_values = list(range(first_tick, query_to + 1, 10))
        ticks = "".join(
            f'<span style="left:{((value - query_from) / max(1, comparison_length - 1)) * 100:.4f}%">'
            f"{value}</span>"
            for value in tick_values
        )
        if differences:
            detail = "".join(
                '<span class="difference-chip">'
                f'<b>{position}</b> {html.escape(query_residue)}→{html.escape(target_residue)}'
                "</span>"
                for position, query_residue, target_residue in differences
            )
        else:
            detail = '<span class="no-difference">全长一致</span>'
        identity = identity_analysis(
            query_segment,
            target,
            target_label=str(hit.get("target_id") or "Target"),
        )
        overview = (
            '<div class="alignment-overview">'
            '<div class="overview-head"><strong>全长差异概览</strong>'
            f'<span>替换 {substitution_count} · 缺口 {gap_count}</span></div>'
            f'{identity}'
            f'<div class="overview-track" style="--sequence-length:{comparison_length}">'
            f'{"".join(overview_cells)}</div>'
            f'<div class="overview-ticks">{ticks}</div>'
            f'<div class="difference-list">{detail}</div>'
            '</div>'
        )
    chunks = []
    width = max(len(target), len(query_segment or ""))
    for offset in range(0, width, 60):
        target_chunk = target[offset : offset + 60]
        query_chunk = query_segment[offset : offset + 60] if query_segment is not None else None
        left = query_from + offset
        right = min(query_to, query_from + offset + max(len(target_chunk), len(query_chunk or "")) - 1)
        if query_chunk is not None:
            query_line = (
                '<div class="alignment-line position-line"><span class="alignment-label">Position</span>'
                f'<span class="alignment-seq">{position_ruler(query_chunk, target_chunk, start_position=left)}</span></div>'
                '<div class="alignment-line"><span class="alignment-label">Query</span>'
                f'<span class="alignment-seq">{residue_row(query_chunk, target_chunk, start_position=left)}</span></div>'
                '<div class="alignment-line"><span class="alignment-label">Consensus</span>'
                f'<span class="alignment-seq">{consensus_row(query_chunk, target_chunk, start_position=left)}</span></div>'
            )
        else:
            query_line = (
                '<div class="alignment-note">为保护查询序列，HTML 默认不写入 Query 残基。'
                '使用 <code>--include-query-sequence</code> 可为公开序列生成双行比对。</div>'
            )
        chunks.append(
            '<div class="alignment-chunk">'
            f'<div class="alignment-range">Query {left}–{right}</div>'
            f'{query_line}'
            '<div class="alignment-line"><span class="alignment-label">Target</span>'
            f'<span class="alignment-seq">{residue_row(target_chunk, query_chunk, start_position=left)}</span></div>'
            '</div>'
        )
    return overview + "".join(chunks)


def display_values(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, (list, tuple, set)):
        rendered = ", ".join(str(item) for item in value if item not in (None, ""))
        return rendered or "—"
    if isinstance(value, dict):
        rendered = value.get("description") or value.get("event") or value.get("title")
        return str(rendered or "—")
    return str(value)


def legal_event_text(value: Any) -> str:
    if not isinstance(value, dict):
        return display_values(value)
    parts = [value.get("date"), value.get("code"), value.get("title") or value.get("description")]
    rendered = " · ".join(str(part) for part in parts if part not in (None, ""))
    return rendered or "—"


def patseek_publication_index(enrichment: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not enrichment:
        return {}
    return {
        str(item.get("publication") or "").upper(): item
        for item in enrichment.get("publications") or []
        if isinstance(item, dict) and item.get("publication")
    }


def patseek_claim_code(publications: list[Any], index: dict[str, dict[str, Any]]) -> str:
    codes = []
    for publication in publications:
        item = index.get(str(publication).upper()) or {}
        claim_class = str((item.get("claim_evidence") or {}).get("class") or "")
        codes.append(claim_class.split("_", 1)[0] if claim_class else "C0")
    return max(codes, key=lambda code: int(code[1:]) if code[1:].isdigit() else 0) if codes else "C0"


def render_patseek_hit(publications: list[Any], index: dict[str, dict[str, Any]]) -> str:
    cards = []
    for raw_publication in publications:
        publication = str(raw_publication).upper()
        item = index.get(publication)
        if not item or item.get("status") != "enriched":
            continue
        claim = item.get("claim_evidence") if isinstance(item.get("claim_evidence"), dict) else {}
        claim_class = str(claim.get("class") or "C0_not_verified")
        claim_code = claim_class.split("_", 1)[0]
        thresholds = [f"≥ {value}% identity" for value in claim.get("identity_thresholds") or []]
        matching_ids = claim.get("matching_sequence_ids") or []
        claim_signals = []
        if matching_ids:
            claim_signals.append("对应序列编号：" + ", ".join(f"SEQ ID NO: {value}" for value in matching_ids))
        if thresholds:
            claim_signals.append("范围表达：" + ", ".join(thresholds))
        if not claim_signals:
            claim_signals.append("尚未定位到与当前命中直接对应的权利要求序列信号")
        snippets = "".join(
            f"<blockquote>{html.escape(str(snippet))}</blockquote>"
            for snippet in claim.get("snippets") or []
        )
        legal_status = display_values(item.get("legal_status"))
        latest_legal_event = legal_event_text(item.get("latest_legal_event"))
        canonical_url = str(item.get("canonical_url") or "")
        source_link = (
            '<a class="patseek-source" target="_blank" rel="noopener noreferrer" '
            f'href="{html.escape(canonical_url, quote=True)}">核对来源 ↗</a>'
            if canonical_url.startswith("https://")
            else ""
        )
        cards.append(
            '<div class="patseek-card">'
            '<div class="patseek-card-head"><div>'
            f'<span class="patseek-kicker">PatSeek · {html.escape(publication)}</span>'
            f'<h4>{html.escape(display_values(item.get("title")))}</h4>'
            f'<p>{html.escape(display_values(item.get("applicant")))}</p></div>'
            f'<span class="claim-code claim-{html.escape(claim_code.lower())}">{html.escape(claim_code)}</span></div>'
            '<div class="patent-intel-grid">'
            f'<div><span>公开号</span><b>{html.escape(display_values(item.get("pid")))}</b></div>'
            f'<div><span>申请号</span><b>{html.escape(display_values(item.get("application_number")))}</b></div>'
            f'<div><span>申请日</span><b>{html.escape(display_values(item.get("application_date")))}</b></div>'
            f'<div><span>公开日</span><b>{html.escape(display_values(item.get("publication_date")))}</b></div>'
            f'<div><span>最早优先权</span><b>{html.escape(display_values(item.get("priority_date")))}</b></div>'
            f'<div><span>法律状态</span><b>{html.escape(legal_status)}</b></div>'
            f'<div class="wide"><span>最新法律事件</span><b>{html.escape(latest_legal_event)}</b></div>'
            f'<div><span>同族数量</span><b>{html.escape(display_values(item.get("family_count")))}</b></div>'
            f'<div><span>引用 / 被引</span><b>{html.escape(display_values(item.get("citation_count")))} / {html.escape(display_values(item.get("cited_by_count")))}</b></div>'
            f'<div><span>聚合状态</span><b>{html.escape(display_values(item.get("aggregation_status")))}</b></div>'
            f'<div class="wide"><span>发明人</span><b>{html.escape(display_values(item.get("inventors")))}</b></div>'
            '</div>'
            '<div class="claim-evidence">'
            f'<strong>{html.escape(display_values(claim.get("label")))}</strong>'
            f'<ul>{"".join(f"<li>{html.escape(signal)}</li>" for signal in claim_signals)}</ul>'
            f'{snippets}'
            '<p>权利要求文本来自详情聚合；SEQ ID 对应关系、范围解释及法律效力仍需核对原始专利与官方登记簿。</p>'
            f'{source_link}</div></div>'
        )
    return "".join(cards)


def render_patseek_summary(enrichment: dict[str, Any] | None) -> str:
    if not enrichment:
        return (
            '<section class="section patseek-summary patseek-optional"><div>'
            '<span class="section-kicker">Optional enrichment</span><h2>PatSeek 专利增强未启用</h2>'
            '<p>序列检索结果不受影响。需要申请人、优先权、法律状态、同族和权利要求信号时，'
            '先运行零调用增强计划；若 PatSeek Skill 未安装或 API Key 不可用，命令会提示当前用户处理。</p>'
            '</div><span class="optional-badge">可选</span></section>'
        )
    status = str(enrichment.get("status") or "unknown")
    publications = enrichment.get("publications") or []
    enriched = sum(1 for item in publications if item.get("status") == "enriched")
    unresolved = sum(1 for item in publications if item.get("status") == "unresolved")
    if status not in {"finished", "partial"}:
        action = str(enrichment.get("user_action") or "请检查 PatSeek Skill 与 API Key 状态后重新生成增强计划。")
        return (
            '<section class="section patseek-summary patseek-warning"><div>'
            '<span class="section-kicker">Optional enrichment</span><h2>PatSeek 专利增强不可用</h2>'
            f'<p><strong>状态：{html.escape(status)}</strong></p><p>{html.escape(action)}</p>'
            '<p class="muted">原有序列检索与比对结果仍然有效；没有把蛋白序列发送给 PatSeek。</p>'
            '</div><span class="warning-badge">需要处理</span></section>'
        )
    return (
        '<section class="section patseek-summary patseek-complete">'
        '<div class="patseek-summary-head"><div><span class="section-kicker">Optional enrichment</span>'
        '<h2>PatSeek 专利增强</h2></div><span class="complete-badge">已增强</span></div>'
        '<div class="patseek-metrics">'
        f'<div><b>{enriched}</b><span>已补充公开号</span></div>'
        f'<div><b>{unresolved}</b><span>未解析</span></div>'
        f'<div><b>{html.escape(display_values(enrichment.get("credits_charged")))}</b><span>本次积分</span></div>'
        f'<div><b>{html.escape(display_values(enrichment.get("credits_remaining")))}</b><span>剩余积分</span></div>'
        '</div>'
        f'<p class="muted">核验时间：{html.escape(display_values(enrichment.get("checked_at")))}。'
        'PatSeek 只接收标准化公开号，没有接收 Query 序列或本机任务状态。法律状态为候选筛查信号，非法律意见。</p>'
        '</section>'
    )


def render_static_html(
    search: dict[str, Any],
    *,
    title: str,
    case_label: str,
    top: int,
    query_sequence: str | None,
    patseek_enrichment: dict[str, Any] | None = None,
) -> str:
    status = str(search.get("status") or "unknown")
    criteria = search.get("criteria") or {}
    coverage_data = search.get("coverage") or {}
    databases = search.get("databases") or []
    all_hits: list[tuple[str, dict[str, Any]]] = []
    for database in databases:
        for hit in database.get("hits") or []:
            all_hits.append((str(database.get("database") or "unknown"), hit))
    all_hits.sort(
        key=lambda pair: (
            number(pair[1].get("evalue"), default=float("inf")),
            -(number(pair[1].get("identity"), default=0.0) or 0.0),
            -(number(pair[1].get("query_coverage"), default=0.0) or 0.0),
        )
    )
    all_hits = all_hits[:top]
    hit_count = sum(int(item.get("hit_count") or 0) for item in databases)
    patseek_index = patseek_publication_index(patseek_enrichment)

    db_rows = []
    for item in databases:
        db_status = str(item.get("status") or "unknown")
        db_rows.append(
            "<tr>"
            f'<td><span class="db-name">{html.escape(str(item.get("database") or "—").upper())}</span></td>'
            f'<td><span class="status status-{html.escape(db_status)}">{html.escape(db_status)}</span></td>'
            f'<td>{"是" if item.get("cache_hit") else "否"}</td>'
            f'<td>{format_metric(item.get("hit_count"))}</td>'
            f'<td>{html.escape(str(item.get("message") or ""))}</td>'
            "</tr>"
        )

    hit_cards = []
    for rank, (database, hit) in enumerate(all_hits, 1):
        publications = hit.get("patent_publications") or []
        patent_links = "".join(
            '<a class="patent" target="_blank" rel="noopener noreferrer" '
            f'href="https://patents.google.com/patent/{urllib.parse.quote(str(item), safe="")}/en">'
            f'{html.escape(str(item))}</a>'
            for item in publications
        ) or '<span class="muted">未解析到公开号</span>'
        evidence_url = str(hit.get("evidence_url") or "")
        evidence_link = (
            '<a class="evidence" target="_blank" rel="noopener noreferrer" '
            f'href="{html.escape(evidence_url, quote=True)}">查看来源记录 ↗</a>'
            if evidence_url.startswith("https://")
            else ""
        )
        sequence_class = match_class(hit)
        sequence_code = sequence_class.split("_", 1)[0]
        mapping_code = "P1" if publications else "P0"
        claim_code = patseek_claim_code(publications, patseek_index)
        patseek_hit = render_patseek_hit(publications, patseek_index)
        legal_code = "L1" if any(
            display_values((patseek_index.get(str(item).upper()) or {}).get("legal_status")) != "—"
            for item in publications
        ) else "L0"
        hit_cards.append(
            '<article class="hit-card">'
            '<div class="hit-head">'
            f'<div><span class="rank">#{rank}</span><span class="db-pill">{html.escape(database.upper())}</span>'
            f'<h3>{html.escape(str(hit.get("target_id") or "Unnamed target"))}</h3>'
            f'<p class="definition">{html.escape(str(hit.get("target_definition") or ""))}</p></div>'
            f'<div class="evidence-codes"><span title="序列匹配等级">{sequence_code}</span>'
            f'<span title="专利映射等级">{mapping_code}</span><span title="权利要求证据等级">{claim_code}</span>'
            f'<span title="法律状态数据等级">{legal_code}</span></div>'
            '</div>'
            '<div class="metric-grid compact">'
            f'<div><strong>{format_metric(hit.get("identity"), suffix="%")}</strong><span>Identity</span></div>'
            f'<div><strong>{format_metric(hit.get("query_coverage"), suffix="%")}</strong><span>Query coverage</span></div>'
            f'<div><strong>{format_metric(hit.get("target_coverage"), suffix="%")}</strong><span>Target coverage</span></div>'
            f'<div><strong>{format_metric(hit.get("evalue"))}</strong><span>E-value</span></div>'
            '</div>'
            f'<div class="patent-row"><span class="label">专利标识</span>{patent_links}{evidence_link}</div>'
            f'{patseek_hit}'
            '<details class="alignment" open>'
            '<summary>序列比对视图</summary>'
            f'{alignment_block(hit, query_sequence)}'
            '</details>'
            '</article>'
        )
    if not hit_cards:
        hit_cards.append('<div class="empty-state">当前阈值下没有可展示的候选。空结果不证明相关序列不存在。</div>')

    coverage_parts = []
    for key, label in (
        ("searched", "已检索"),
        ("failed", "失败"),
        ("empty", "空结果"),
        ("not_searched", "未检索"),
    ):
        values = coverage_data.get(key) or []
        coverage_parts.append(
            f'<div class="coverage-item"><span>{label}</span><strong>{html.escape(", ".join(values) or "—")}</strong></div>'
        )
    limitations = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in coverage_data.get("limitations") or []
    )
    query_mode = "已包含（公开序列）" if query_sequence else "未写入 HTML"
    generated_at = iso(utc_now())
    patseek_summary = render_patseek_summary(patseek_enrichment)
    patseek_footer = (
        "PatSeek 仅参与公开号增强，未参与序列检索"
        if patseek_enrichment
        else "PatSeek 未参与序列检索"
    )
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ --ink:#172033; --muted:#657089; --line:#dfe5ee; --paper:#fff; --wash:#f4f7fb; --navy:#14243b; --teal:#0c7c78; --green:#138a55; --amber:#b96b12; --red:#b83a42; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; color:var(--ink); background:var(--wash); font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
    .page {{ max-width:1240px; margin:0 auto; padding:34px 24px 72px; }}
    .hero {{ color:#fff; background:linear-gradient(135deg,var(--navy),#1e4962 72%,#176f71); border-radius:18px; padding:32px; box-shadow:0 18px 45px rgba(20,36,59,.18); }}
    .eyebrow {{ color:#9fe6dc; font-weight:700; letter-spacing:.09em; text-transform:uppercase; }}
    h1 {{ margin:8px 0 6px; font-size:30px; line-height:1.2; }}
    .subtitle {{ color:#dceaf0; margin:0; }}
    .hero-meta {{ display:flex; flex-wrap:wrap; gap:9px; margin-top:22px; }}
    .hero-meta span {{ background:rgba(255,255,255,.11); border:1px solid rgba(255,255,255,.18); border-radius:999px; padding:6px 11px; }}
    .section {{ margin-top:22px; background:var(--paper); border:1px solid var(--line); border-radius:15px; padding:24px; box-shadow:0 6px 18px rgba(30,50,75,.05); }}
    .section h2 {{ margin:0 0 17px; font-size:19px; }}
    .metric-grid {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:12px; }}
    .metric-grid>div {{ background:#f7f9fc; border:1px solid #e7ebf2; border-radius:12px; padding:15px; }}
    .metric-grid strong {{ display:block; font-size:22px; color:var(--navy); }}
    .metric-grid span {{ display:block; color:var(--muted); margin-top:3px; font-size:12px; }}
    .metric-grid.compact {{ grid-template-columns:repeat(4,minmax(0,1fr)); margin:18px 0; }}
    .metric-grid.compact>div {{ padding:12px; }} .metric-grid.compact strong {{ font-size:17px; }}
    .coverage {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }}
    .coverage-item {{ border-left:3px solid var(--teal); background:#f7fbfb; padding:10px 12px; border-radius:6px; }}
    .coverage-item span {{ display:block; color:var(--muted); font-size:12px; }}
    table {{ width:100%; border-collapse:collapse; }} th,td {{ text-align:left; border-bottom:1px solid var(--line); padding:11px 10px; vertical-align:top; }} th {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }}
    .db-name,.db-pill {{ font-weight:750; color:var(--teal); }} .db-pill {{ margin-left:8px; padding:3px 7px; background:#e8f6f4; border-radius:6px; font-size:11px; }}
    .status {{ display:inline-block; border-radius:999px; padding:3px 8px; background:#eef1f5; }} .status-finished {{ color:var(--green); background:#e7f6ee; }} .status-failed {{ color:var(--red); background:#fdecee; }} .status-partial {{ color:var(--amber); background:#fff3df; }}
    .hits {{ display:grid; gap:15px; }} .hit-card {{ border:1px solid var(--line); border-radius:14px; padding:20px; background:#fff; }}
    .hit-head {{ display:flex; justify-content:space-between; gap:18px; }} .rank {{ color:var(--muted); font-weight:800; }} .hit-head h3 {{ margin:7px 0 2px; font-size:17px; }}
    .definition {{ color:var(--muted); margin:0; max-width:880px; }} .evidence-codes {{ display:flex; gap:5px; align-items:flex-start; }} .evidence-codes span {{ min-width:32px; text-align:center; padding:5px 7px; border-radius:7px; color:#fff; background:var(--navy); font-weight:800; font-size:11px; }}
    .patent-row {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; }} .label {{ color:var(--muted); margin-right:3px; }} .patent {{ color:#086a77; background:#eaf7f8; border-radius:6px; padding:4px 8px; text-decoration:none; font-weight:650; }} .evidence {{ margin-left:auto; color:var(--teal); text-decoration:none; }}
    .patseek-summary {{ display:flex; justify-content:space-between; gap:20px; align-items:flex-start; }} .patseek-summary h2 {{ margin:2px 0 7px; }} .section-kicker,.patseek-kicker {{ color:var(--teal); font-size:11px; font-weight:800; letter-spacing:.06em; text-transform:uppercase; }} .optional-badge,.warning-badge,.complete-badge {{ white-space:nowrap; border-radius:999px; padding:5px 10px; font-size:11px; font-weight:800; }} .optional-badge {{ color:#596579; background:#edf1f5; }} .warning-badge {{ color:#8a541e; background:#fff0d9; }} .complete-badge {{ color:#0b7048; background:#dff3e9; }} .patseek-warning {{ border-color:#edcf98; background:#fffdf8; }} .patseek-complete {{ display:block; border-color:#b9ded7; }} .patseek-summary-head {{ display:flex; justify-content:space-between; gap:20px; }} .patseek-metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:14px 0; }} .patseek-metrics div {{ padding:11px 13px; background:#f2f8f7; border-radius:9px; }} .patseek-metrics b {{ display:block; color:var(--teal); font-size:17px; }} .patseek-metrics span {{ color:var(--muted); font-size:11px; }}
    .patseek-card {{ margin-top:15px; padding:15px; border:1px solid #bddfd9; background:#f8fcfb; border-radius:11px; }} .patseek-card-head {{ display:flex; justify-content:space-between; gap:15px; }} .patseek-card h4 {{ margin:3px 0 2px; font-size:15px; }} .patseek-card-head p {{ margin:0; color:var(--muted); }} .claim-code {{ align-self:flex-start; min-width:38px; text-align:center; padding:5px 8px; border-radius:7px; color:#fff; background:#58677c; font-weight:850; }} .claim-c1 {{ background:#a86c13; }} .claim-c2 {{ background:#087b70; }} .patent-intel-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; margin-top:12px; }} .patent-intel-grid div {{ min-width:0; padding:9px 10px; background:#fff; border:1px solid #e1ebe9; border-radius:8px; }} .patent-intel-grid div.wide {{ grid-column:span 2; }} .patent-intel-grid span {{ display:block; color:var(--muted); font-size:10px; }} .patent-intel-grid b {{ display:block; overflow:hidden; text-overflow:ellipsis; color:#26384a; font-size:12px; white-space:nowrap; }} .patent-intel-grid .wide b {{ white-space:normal; line-height:1.45; }} .claim-evidence {{ position:relative; margin-top:10px; padding:12px; background:#fff; border-left:3px solid var(--teal); border-radius:6px; }} .claim-evidence ul {{ margin:7px 0; padding-left:18px; }} .claim-evidence blockquote {{ margin:7px 0; padding:8px 10px; color:#4e5a6e; background:#f6f8fb; border-radius:6px; font-size:11px; }} .claim-evidence p {{ color:var(--muted); font-size:10px; margin:8px 0 0; }} .patseek-source {{ display:inline-block; margin-top:8px; color:var(--teal); font-weight:700; text-decoration:none; }}
    .alignment {{ margin-top:17px; border-top:1px solid var(--line); padding-top:14px; }} .alignment summary {{ cursor:pointer; font-weight:750; color:var(--navy); }}
    .alignment-overview {{ margin-top:14px; padding:14px; background:#f6f8fc; border:1px solid var(--line); border-radius:10px; }} .overview-head {{ display:flex; justify-content:space-between; gap:12px; margin-bottom:9px; }} .overview-head span {{ color:var(--muted); font-size:12px; }}
    .identity-analysis {{ margin:10px 0 15px; padding:15px; background:#fff; border:1px solid #dce3ec; border-radius:10px; }} .identity-head {{ display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:12px; }} .identity-head strong {{ display:block; color:var(--navy); font-size:14px; }} .identity-head span:not(.identity-score) {{ display:block; color:var(--muted); font-size:11px; margin-top:1px; }} .identity-score {{ color:#fff; background:var(--teal); border-radius:999px; padding:4px 10px; font-weight:800; font-size:13px; }}
    .identity-body {{ display:grid; grid-template-columns:minmax(0,1fr) auto; gap:18px; align-items:center; }} .identity-facts {{ display:grid; grid-template-columns:repeat(4,minmax(92px,1fr)); gap:8px; }} .identity-facts div {{ padding:9px 10px; background:#f6f8fb; border-radius:8px; }} .identity-facts b {{ display:block; color:var(--navy); font-size:15px; }} .identity-facts span {{ color:var(--muted); font-size:11px; }}
    .identity-matrix-wrap {{ overflow-x:auto; }} .identity-matrix {{ width:auto; min-width:250px; border-collapse:separate; border-spacing:2px; font:11px/1.25 ui-monospace,SFMono-Regular,Menlo,monospace; }} .identity-matrix th,.identity-matrix td {{ min-width:68px; padding:7px 9px; border:0; text-align:center; }} .identity-matrix th {{ color:#536177; background:#eef2f7; text-transform:none; letter-spacing:0; }} .identity-matrix td {{ font-weight:800; }} .matrix-diagonal {{ color:#546175; background:#f1f3f7; }} .matrix-pair {{ color:#096c68; background:#dff3ef; box-shadow:inset 0 0 0 1px #a9dcd4; }} .matrix-caption {{ max-width:250px; color:var(--muted); font-size:10px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:4px; }}
    .overview-track {{ display:grid; grid-template-columns:repeat(var(--sequence-length),minmax(2px,1fr)); height:18px; overflow:hidden; border-radius:5px; background:#dce2ea; }} .overview-track span {{ min-width:2px; }} .overview-match {{ background:#32a852; }} .overview-diff {{ background:#f08a24; box-shadow:inset 0 0 0 1px #b7540d; }}
    .overview-ticks {{ position:relative; height:16px; color:#7b8698; font:10px/1.3 ui-monospace,SFMono-Regular,Menlo,monospace; margin-top:5px; }} .overview-ticks span {{ position:absolute; transform:translateX(-50%); }}
    .difference-list {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:9px; color:#8a541e; font:11px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; }} .difference-chip {{ display:inline-flex; align-items:center; gap:4px; padding:3px 7px; color:#7c4313; background:#fff0da; border:1px solid #efc187; border-radius:999px; }} .difference-chip b {{ color:#b84e0a; }} .no-difference {{ color:var(--green); }}
    .alignment-chunk {{ overflow-x:auto; margin-top:12px; padding:12px; background:#101827; color:#dfe9ef; border-radius:10px; }} .alignment-range {{ color:#8da4b7; margin-bottom:7px; font:11px/1.3 ui-monospace,SFMono-Regular,Menlo,monospace; }}
    .alignment-line {{ display:flex; min-width:max-content; }} .alignment-label {{ width:76px; flex:0 0 76px; color:#91a8b9; font:12px/20px ui-monospace,SFMono-Regular,Menlo,monospace; }} .alignment-seq {{ white-space:nowrap; }}
    .position-line {{ min-height:27px; margin-bottom:2px; }} .position-line .alignment-label {{ color:#b6c5d0; font-weight:700; line-height:25px; }}
    .residue,.ruler-cell {{ display:inline-block; width:12px; text-align:center; font:12px/20px ui-monospace,SFMono-Regular,Menlo,monospace; border-radius:2px; vertical-align:top; }} .residue.group-start,.ruler-cell.group-start {{ margin-left:7px; }}
    .ruler-cell {{ position:relative; height:25px; color:#aebdc8; overflow:visible; }} .ruler-cell b {{ position:absolute; top:0; left:50%; transform:translateX(-50%); color:#d9e3ea; font-size:10px; line-height:15px; font-weight:650; }} .ruler-cell i {{ position:absolute; left:50%; bottom:1px; width:4px; height:4px; transform:translateX(-50%); border-radius:50%; background:#ff9f3d; }} .ruler-cell.difference-position b {{ color:#ffb85c; font-weight:850; }}
    .residue.match {{ color:#d9ffe5; background:rgba(41,180,104,.24); }} .residue.substitution {{ color:#ffe2a8; background:rgba(225,142,30,.34); font-weight:800; outline:1px solid rgba(255,184,92,.45); }} .residue.gap {{ color:#9ba8b2; }} .residue.neutral {{ color:#e2e9ef; }} .consensus-symbol.match {{ color:#68ed91; background:transparent; }} .consensus-symbol.substitution {{ color:#ffb85c; background:rgba(225,142,30,.24); }}
    .alignment-note {{ color:#aebdc8; font-size:12px; margin-bottom:8px; }} code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
    .muted {{ color:var(--muted); }} .empty-state {{ text-align:center; color:var(--muted); padding:35px; border:1px dashed #c8d0dc; border-radius:12px; }}
    .notice {{ background:#fff8e8; border:1px solid #f0d69b; border-radius:10px; padding:14px 16px; color:#6b4c16; }} .limitations {{ color:var(--muted); padding-left:20px; }}
    .footer {{ color:var(--muted); font-size:12px; margin-top:20px; text-align:center; }}
    @media (max-width:850px) {{ .metric-grid,.metric-grid.compact,.coverage,.patseek-metrics {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .patent-intel-grid {{ grid-template-columns:1fr; }} .patent-intel-grid div.wide {{ grid-column:span 1; }} .identity-body {{ grid-template-columns:1fr; }} .identity-facts {{ grid-template-columns:repeat(2,minmax(92px,1fr)); }} .hit-head {{ display:block; }} .evidence-codes {{ margin-top:12px; }} .page {{ padding:18px 12px 50px; }} .section,.hero {{ padding:18px; }} }}
    @media print {{ body {{ background:#fff; }} .page {{ max-width:none; padding:0; }} .hero,.section {{ box-shadow:none; break-inside:avoid; }} details {{ display:block; }} }}
  </style>
</head>
<body>
<main class="page">
  <header class="hero">
    <div class="eyebrow">Patent protein sequence evidence</div>
    <h1>{html.escape(title)}</h1>
    <p class="subtitle">{html.escape(case_label)}</p>
    <div class="hero-meta">
      <span>状态：{html.escape(status)}</span><span>任务：{html.escape(str(search.get("search_id") or "—"))}</span>
      <span>Provider：EMBL-EBI FASTA</span><span>生成：{html.escape(generated_at)}</span>
    </div>
  </header>
  <section class="section">
    <h2>检索概览</h2>
    <div class="metric-grid">
      <div><strong>{format_metric(search.get("query_length"))}</strong><span>Query length</span></div>
      <div><strong>{format_metric(hit_count)}</strong><span>Total candidates</span></div>
      <div><strong>{format_metric(search.get("external_submissions", 0))}</strong><span>External submissions</span></div>
      <div><strong>{html.escape(str(search.get("query_digest") or "—"))}</strong><span>Query digest</span></div>
      <div><strong>{html.escape(query_mode)}</strong><span>Query residues in HTML</span></div>
    </div>
    <p class="notice">序列相似性用于候选召回，不等于权利要求覆盖、专利有效性、FTO 或侵权结论。</p>
  </section>
  <section class="section">
    <h2>阈值与覆盖</h2>
    <div class="coverage">{''.join(coverage_parts)}</div>
    <p class="muted">Identity ≥ {format_metric(criteria.get("min_identity"), suffix="%")} · Query coverage ≥ {format_metric(criteria.get("min_query_coverage"), suffix="%")} · E-value ≤ {format_metric(criteria.get("max_evalue"))}</p>
  </section>
  <section class="section">
    <h2>数据库执行状态</h2>
    <div style="overflow-x:auto"><table><thead><tr><th>数据库</th><th>状态</th><th>缓存</th><th>命中</th><th>说明</th></tr></thead><tbody>{''.join(db_rows)}</tbody></table></div>
  </section>
  {patseek_summary}
  <section class="section">
    <h2>代表性候选（前 {len(all_hits)} 条）</h2>
    <div class="hits">{''.join(hit_cards)}</div>
  </section>
  <section class="section">
    <h2>证据限制</h2>
    <ul class="limitations">{limitations}</ul>
  </section>
  <div class="footer">静态单文件报告 · 无外部脚本、无跟踪器 · {html.escape(patseek_footer)}</div>
</main>
</body>
</html>'''


def generate_html_report(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    if not SEARCH_ID.fullmatch(args.search_id):
        raise ClientError("Invalid local search ID")
    search = read_json(
        root / "searches" / f"{args.search_id}.json",
        missing_message="Local search not found",
    )
    query_sequence = None
    if args.include_query_sequence:
        if not args.sequence_file:
            raise ClientError("--include-query-sequence requires --sequence-file")
        query_sequence = normalize_protein(Path(args.sequence_file).read_text(encoding="utf-8"))
        if sequence_digest(query_sequence) != search.get("query_digest"):
            raise ClientError("HTML query sequence does not match the search")
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    enrichment_path = root / "enrichments" / f"{args.search_id}.json"
    patseek_enrichment = None
    if enrichment_path.exists():
        patseek_enrichment = read_json(
            enrichment_path,
            missing_message="PatSeek enrichment state not found",
        )
    document = render_static_html(
        search,
        title=args.title,
        case_label=args.case_label,
        top=args.top,
        query_sequence=query_sequence,
        patseek_enrichment=patseek_enrichment,
    )
    output.write_text(document, encoding="utf-8")
    return {
        "output": str(output),
        "search_id": args.search_id,
        "status": search.get("status"),
        "displayed_hits": min(
            args.top,
            sum(len(item.get("hits") or []) for item in search.get("databases") or []),
        ),
        "query_sequence_included": query_sequence is not None,
        "patseek_enrichment_status": (
            patseek_enrichment.get("status") if patseek_enrichment else "not_enabled"
        ),
        "static_single_file": True,
        "web_server_required": False,
    }


def capabilities(root: Path | None = None) -> dict[str, Any]:
    return {
        "skill_runtime": "local-agent-cli",
        "backend_service_required": False,
        "web_page_required": False,
        "static_html_report": True,
        "python_dependencies": "standard-library-only",
        "provider": "EMBL-EBI JDispatcher FASTA",
        "provider_url": ebi_url_from_env(),
        "supported_databases": list(SUPPORTED_DATABASES),
        "default_databases": list(DEFAULT_DATABASES),
        "sequence_type": "protein",
        "external_submission_on_cache_miss": True,
        "monetary_cost": 0,
        "local_state": str(root or state_dir_from_env()),
        "sequence_persistence": "raw query sequence is not stored locally",
        "patseek_api_required": False,
    }


def doctor(root: Path) -> dict[str, Any]:
    ensure_state_dirs(root)
    probe = root / ".write-test"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        writable = True
    except OSError:
        writable = False
    result = capabilities(root)
    result.update(
        {
            "ok": writable,
            "state_writable": writable,
            "contact_email_configured": bool(contact_email_from_env(required=False)),
            "contact_email_resolved": bool(resolve_contact_email(root, required=False)[0]),
            "contact_email_source": resolve_contact_email(root, required=False)[1],
            "network_checked": False,
        }
    )
    return result


def print_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False))


def add_sequence_input(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sequence", help="Public protein sequence or FASTA text")
    group.add_argument("--sequence-file", help="UTF-8 protein sequence or FASTA file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local patent-protein search client for agents")
    parser.add_argument("--state-dir", default=None)
    parser.add_argument("--request-timeout", type=float, default=30.0)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="Check the local runtime without network access")
    subparsers.add_parser("capabilities", help="Show local runtime capabilities")

    plan = subparsers.add_parser("plan", help="Create a local zero-submission plan")
    add_sequence_input(plan)
    plan.add_argument("--database", action="append", choices=SUPPORTED_DATABASES)
    plan.add_argument("--min-identity", type=float, default=70.0)
    plan.add_argument("--min-query-coverage", type=float, default=70.0)
    plan.add_argument("--max-evalue", type=float, default=1e-5)
    plan.add_argument("--max-hits", type=int, default=20)
    plan.add_argument("--include-alignment", action=argparse.BooleanOptionalAction, default=True)
    plan.add_argument("--plan-ttl-minutes", type=int, default=30)
    plan.add_argument("--cache-ttl-hours", type=int, default=24)

    execute = subparsers.add_parser("execute", help="Execute a reviewed local plan")
    add_sequence_input(execute)
    execute.add_argument("--plan-id", required=True)
    execute.add_argument("--idempotency-key", required=True)
    execute.add_argument("--confirm-external-submission", action="store_true")
    execute.add_argument("--top", type=int, default=5)
    execute.add_argument("--full", action="store_true")

    poll = subparsers.add_parser("poll", help="Poll local search state once")
    poll.add_argument("search_id")
    poll.add_argument("--summary", action="store_true")
    poll.add_argument("--top", type=int, default=5)

    watch = subparsers.add_parser("watch", help="Poll until a terminal state")
    watch.add_argument("search_id")
    watch.add_argument("--poll-seconds", type=float, default=5.0)
    watch.add_argument("--timeout-seconds", type=float, default=1800.0)
    watch.add_argument("--summary", action="store_true")
    watch.add_argument("--top", type=int, default=5)

    report = subparsers.add_parser("render-html", help="Generate a standalone static HTML report")
    report.add_argument("search_id")
    report.add_argument("--output", required=True)
    report.add_argument("--title", default="专利蛋白序列检索报告")
    report.add_argument("--case-label", default="Agent 本机生成的静态证据页面")
    report.add_argument("--top", type=int, default=20)
    report.add_argument("--sequence-file")
    report.add_argument(
        "--include-query-sequence",
        action="store_true",
        help="Embed public query residues in HTML for a two-row comparison",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        root = Path(args.state_dir).expanduser() if args.state_dir else state_dir_from_env()
        ensure_state_dirs(root)
        if args.command == "doctor":
            result = doctor(root)
        elif args.command == "capabilities":
            result = capabilities(root)
        elif args.command == "plan":
            if args.plan_ttl_minutes < 1 or args.cache_ttl_hours < 1:
                raise ClientError("Plan and cache TTL values must be positive")
            result = create_plan(args, root)
        elif args.command == "execute":
            result = execute_plan(args, root)
            if not args.full:
                result = summarize_search(result, top=args.top)
        elif args.command == "poll":
            result = poll_search(args, root)
            if args.summary:
                result = summarize_search(result, top=args.top)
        elif args.command == "render-html":
            if args.top < 1 or args.top > 100:
                raise ClientError("HTML top must be between 1 and 100")
            result = generate_html_report(args, root)
        else:
            deadline = time.monotonic() + args.timeout_seconds
            previous = None
            while True:
                result = poll_search(args, root)
                state = (
                    result.get("status"),
                    tuple(
                        (item.get("database"), item.get("status"))
                        for item in result.get("databases") or []
                    ),
                )
                if state != previous:
                    print(f"status: {state}", file=sys.stderr, flush=True)
                    previous = state
                if result.get("status") in TERMINAL_STATUSES:
                    break
                if time.monotonic() >= deadline:
                    raise ClientError("Timed out while EMBL-EBI jobs were incomplete")
                time.sleep(args.poll_seconds)
            if args.summary:
                result = summarize_search(result, top=args.top)
        print_json(result)
        return 0
    except ClientError as exc:
        print(
            json.dumps(
                {"error": str(exc), "code": exc.code, "http_status": exc.status},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
