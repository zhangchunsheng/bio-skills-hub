#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


DEFAULT_PATSEEK_URL = "https://patseek.cn"
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
SEARCH_ID = re.compile(r"^pls_[0-9a-f]{24}$")
PLAN_ID = re.compile(r"^pep_[0-9a-f]{24}$")
PUBLICATION_ID = re.compile(r"^[A-Z]{2}\d{6,}[A-Z]?\d?$")


class EnrichmentError(RuntimeError):
    def __init__(self, message: str, *, code: str, user_action: str):
        super().__init__(message)
        self.code = code
        self.user_action = user_action


class PatSeekHttpError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def state_dir_from_env() -> Path:
    value = os.getenv("PATENT_SEQUENCE_STATE_DIR", "").strip()
    return Path(value).expanduser() if value else Path.home() / ".cache" / "patent-sequence-local"


def ensure_dirs(root: Path) -> None:
    for name in ("searches", "enrichment-plans", "enrichments"):
        (root / name).mkdir(parents=True, exist_ok=True)


def read_json(path: Path, *, missing_message: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EnrichmentError(
            missing_message,
            code="LOCAL_STATE_NOT_FOUND",
            user_action="请先完成本机序列检索，再创建 PatSeek 增强计划。",
        ) from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EnrichmentError(
            f"无法读取本地状态：{path}",
            code="LOCAL_STATE_INVALID",
            user_action="请检查本地状态文件是否完整且为 UTF-8 JSON。",
        ) from exc
    if not isinstance(value, dict):
        raise EnrichmentError(
            f"无效的本地状态：{path}",
            code="LOCAL_STATE_INVALID",
            user_action="请重新生成该本地任务状态。",
        )
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def normalize_publication(value: Any) -> str | None:
    normalized = re.sub(r"[^A-Za-z0-9]", "", str(value or "")).upper()
    return normalized if PUBLICATION_ID.fullmatch(normalized) else None


def ranked_hits(search: dict[str, Any]) -> list[dict[str, Any]]:
    hits = [
        hit
        for database in search.get("databases") or []
        for hit in database.get("hits") or []
        if isinstance(hit, dict)
    ]

    def metric(value: Any, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    hits.sort(
        key=lambda hit: (
            metric(hit.get("evalue"), float("inf")),
            -metric(hit.get("identity"), 0.0),
            -metric(hit.get("query_coverage"), 0.0),
        )
    )
    return hits


def collect_publications(search: dict[str, Any], *, top: int) -> tuple[list[str], dict[str, list[str]]]:
    publications: list[str] = []
    source_hits: dict[str, list[str]] = {}
    for hit in ranked_hits(search):
        target_id = str(hit.get("target_id") or "Unresolved target")
        for raw in hit.get("patent_publications") or []:
            publication = normalize_publication(raw)
            if not publication:
                continue
            if publication not in publications:
                if len(publications) >= top:
                    continue
                publications.append(publication)
            targets = source_hits.setdefault(publication, [])
            if target_id not in targets:
                targets.append(target_id)
    return publications, source_hits


def discover_patseek_skill(
    *,
    configured: str | None = None,
    home: Path | None = None,
) -> Path | None:
    candidates: list[Path] = []
    explicit = configured if configured is not None else os.getenv("PATSEEK_SKILL_DIR", "").strip()
    if explicit:
        candidates = [Path(explicit).expanduser()]
    else:
        base_home = home or Path.home()
        for root in (base_home / ".codex" / "skills", base_home / ".agents" / "skills"):
            if root.is_dir():
                candidates.extend(sorted(root.glob("patseek-patent-search*"), reverse=True))
    for candidate in candidates:
        skill_file = candidate / "SKILL.md"
        client_file = candidate / "scripts" / "patseek_client.py"
        if not skill_file.is_file() or not client_file.is_file():
            continue
        try:
            frontmatter = skill_file.read_text(encoding="utf-8")[:4096]
        except (OSError, UnicodeDecodeError):
            continue
        if re.search(r"(?m)^name:\s*patseek-patent-search\s*$", frontmatter):
            return candidate.resolve()
    return None


def local_availability(*, configured_skill: str | None = None, home: Path | None = None) -> dict[str, Any]:
    skill_dir = discover_patseek_skill(configured=configured_skill, home=home)
    key = os.getenv("PATSEEK_API_KEY", "").strip()
    if skill_dir is None:
        return {
            "ready": False,
            "status": "skill_missing",
            "skill_installed": False,
            "api_key_configured": bool(key),
            "user_action": "未检测到 patseek-patent-search Skill；请先安装该 Skill，或仅使用本机序列报告。",
        }
    if not key:
        return {
            "ready": False,
            "status": "api_key_missing",
            "skill_installed": True,
            "skill_dir": str(skill_dir),
            "api_key_configured": False,
            "user_action": "已检测到 PatSeek Skill，但未配置 PATSEEK_API_KEY；请使用当前用户自己的 Key 后重试。",
        }
    return {
        "ready": True,
        "status": "configured_not_validated",
        "skill_installed": True,
        "skill_dir": str(skill_dir),
        "api_key_configured": True,
        "api_validation_required": True,
        "user_action": "PatSeek 已配置；执行前仍需验证 Key，并确认可能产生积分消耗的详情调用。",
    }


def patseek_base_url() -> str:
    value = os.getenv("PATSEEK_API_URL", DEFAULT_PATSEEK_URL).strip().rstrip("/")
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise EnrichmentError(
            "PATSEEK_API_URL 必须是绝对 HTTP(S) URL",
            code="PATSEEK_URL_INVALID",
            user_action="请删除无效覆盖值，使用 PatSeek Skill 配置的官方服务地址。",
        )
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise EnrichmentError(
            "PATSEEK_API_URL 不能包含凭据、查询或片段",
            code="PATSEEK_URL_INVALID",
            user_action="请只配置 PatSeek 服务根地址。",
        )
    if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise EnrichmentError(
            "PatSeek 外部服务必须使用 HTTPS",
            code="PATSEEK_URL_INVALID",
            user_action="请改用 HTTPS；HTTP 仅用于隔离的本地测试。",
        )
    return value


def api_request(
    method: str,
    path: str,
    *,
    api_key: str,
    timeout: float,
    base_url: str | None = None,
) -> dict[str, Any]:
    if not path.startswith("/") or "://" in path:
        raise ValueError("PatSeek request path must be relative")
    request = urllib.request.Request(
        f"{base_url or patseek_base_url()}{path}",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
        method=method,
    )
    opener = urllib.request.build_opener(NoRedirectHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raw = exc.read(4096)
        try:
            body = json.loads(raw.decode("utf-8"))
            message = str(body.get("detail") or body.get("message") or body.get("code") or exc.reason)
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            message = str(exc.reason)
        raise PatSeekHttpError(exc.code, message) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise EnrichmentError(
            "PatSeek 请求结果不确定；为避免重复扣费，未自动重试",
            code="PATSEEK_OUTCOME_UNCERTAIN",
            user_action="请先检查 PatSeek 任务/账户记录；确认没有成功调用后，再创建新的增强计划。",
        ) from exc
    if len(raw) > MAX_RESPONSE_BYTES:
        raise EnrichmentError(
            "PatSeek 响应超过安全大小限制",
            code="PATSEEK_RESPONSE_TOO_LARGE",
            user_action="请保留当前结果并联系 PatSeek 支持。",
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EnrichmentError(
            "PatSeek 返回了无效 JSON",
            code="PATSEEK_RESPONSE_INVALID",
            user_action="请稍后重试；若持续发生，请联系 PatSeek 支持。",
        ) from exc
    if not isinstance(value, dict):
        raise EnrichmentError(
            "PatSeek 返回结构无效",
            code="PATSEEK_RESPONSE_INVALID",
            user_action="请稍后重试；若持续发生，请联系 PatSeek 支持。",
        )
    return value


def skill_client_request(
    method: str,
    path: str,
    *,
    api_key: str,
    timeout: float,
    base_url: str | None = None,
) -> dict[str, Any]:
    """Use the installed PatSeek Skill's requests runtime without automatic retries.

    The optional integration remains isolated from the standard-library-only sequence
    client.  A detail request is attempted exactly once so an uncertain response cannot
    silently consume a second paid call.
    """
    if not path.startswith("/") or "://" in path:
        raise ValueError("PatSeek request path must be relative")
    skill_dir = discover_patseek_skill()
    if skill_dir is None:
        raise EnrichmentError(
            "未检测到可用的 PatSeek Skill 客户端",
            code="PATSEEK_SKILL_MISSING",
            user_action="请先安装 patseek-patent-search Skill，或改用标准库传输方式。",
        )
    client_file = skill_dir / "scripts" / "patseek_client.py"
    spec = importlib.util.spec_from_file_location("_patseek_optional_client", client_file)
    if spec is None or spec.loader is None:
        raise EnrichmentError(
            "无法加载 PatSeek Skill 客户端",
            code="PATSEEK_CLIENT_UNAVAILABLE",
            user_action="请重新安装 patseek-patent-search Skill。",
        )
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, SystemExit) as exc:
        raise EnrichmentError(
            "PatSeek Skill 客户端依赖不可用",
            code="PATSEEK_CLIENT_UNAVAILABLE",
            user_action="请按 PatSeek Skill 说明安装 requests 依赖后重试。",
        ) from exc

    url = f"{base_url or patseek_base_url()}{path}"
    try:
        response = module.requests.request(
            method,
            url,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            timeout=timeout,
            allow_redirects=False,
        )
    except module.requests.exceptions.RequestException as exc:
        raise EnrichmentError(
            "PatSeek 请求结果不确定；为避免重复扣费，未自动重试",
            code="PATSEEK_OUTCOME_UNCERTAIN",
            user_action="请先检查 PatSeek 任务/账户记录；确认没有成功调用后，再创建新的增强计划。",
        ) from exc
    if 300 <= response.status_code < 400:
        raise EnrichmentError(
            "PatSeek 返回了未跟随的重定向",
            code="PATSEEK_REDIRECT_REJECTED",
            user_action="请检查 PATSEEK_API_URL，确保直接指向官方 HTTPS 服务。",
        )
    raw = response.content
    if response.status_code >= 400:
        try:
            body = response.json()
            message = str(body.get("detail") or body.get("message") or body.get("code") or response.reason)
        except (ValueError, AttributeError):
            message = str(response.reason)
        raise PatSeekHttpError(response.status_code, message)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise EnrichmentError(
            "PatSeek 响应超过安全大小限制",
            code="PATSEEK_RESPONSE_TOO_LARGE",
            user_action="请保留当前结果并联系 PatSeek 支持。",
        )
    try:
        value = response.json()
    except ValueError as exc:
        raise EnrichmentError(
            "PatSeek 返回了无效 JSON",
            code="PATSEEK_RESPONSE_INVALID",
            user_action="请稍后重试；若持续发生，请联系 PatSeek 支持。",
        ) from exc
    if not isinstance(value, dict):
        raise EnrichmentError(
            "PatSeek 返回结构无效",
            code="PATSEEK_RESPONSE_INVALID",
            user_action="请稍后重试；若持续发生，请联系 PatSeek 支持。",
        )
    return value


def http_failure(status: int, message: str) -> tuple[str, str]:
    if status == 401:
        return "api_invalid", "PatSeek API Key 无效或已过期；请登录 patseek.cn 重新创建或更换 Key。"
    if status == 402:
        return "credits_insufficient", "PatSeek 积分不足；请检查账户余额后再创建新的增强计划。"
    if status == 403:
        return "api_disabled", "PatSeek API Key 已被禁用；请检查账户状态或联系平台管理员。"
    if status == 429:
        return "failed", "PatSeek 当前限流；请稍后创建新的增强计划，不要立即重复提交。"
    return "failed", f"PatSeek 返回 HTTP {status}；请检查服务状态后重试。"


def sanitize_key_info(value: dict[str, Any]) -> dict[str, Any]:
    allowed = (
        "status",
        "key_type",
        "plan",
        "scopes",
        "expires_at",
        "credits_remaining",
        "rate_limits",
    )
    return {key: value.get(key) for key in allowed if key in value}


def key_info_failure(value: dict[str, Any]) -> tuple[str, str] | None:
    status = str(value.get("status") or "").strip().lower()
    if status in {"disabled", "revoked", "blocked"}:
        return "api_disabled", "PatSeek API Key 已被禁用；请检查账户状态或联系平台管理员。"
    if status in {"invalid", "expired", "inactive"}:
        return "api_invalid", "PatSeek API Key 无效或已过期；请登录 patseek.cn 重新创建或更换 Key。"
    expires_at = value.get("expires_at")
    if isinstance(expires_at, str) and expires_at:
        try:
            if datetime.fromisoformat(expires_at.replace("Z", "+00:00")) <= utc_now():
                return "api_invalid", "PatSeek API Key 已过期；请登录 patseek.cn 重新创建或更换 Key。"
        except ValueError:
            pass
    remaining = value.get("credits_remaining")
    try:
        if remaining is not None and float(remaining) <= 0:
            return "credits_insufficient", "PatSeek 当前可用积分不足；请检查账户余额后再创建新的增强计划。"
    except (TypeError, ValueError):
        pass
    return None


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "\n".join(as_text(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def sequence_ids(value: str) -> list[str]:
    found = re.findall(
        r"(?i)\bSEQ(?:UENCE)?(?:\s+ID)?(?:\s+NO\.?)?\s*[:#]?\s*(\d+)\b",
        value,
    )
    return list(dict.fromkeys(found))


def identity_thresholds(value: str) -> list[str]:
    found = re.findall(
        r"(?i)(?:at\s+least(?:\s+about)?|至少|不低于|不少于)\s*(\d{1,3}(?:\.\d+)?)\s*%"
        r"(?:\s+sequence)?\s*(?:identity|identical|同一性|一致性)?",
        value,
    )
    return list(dict.fromkeys(found))


def evidence_snippets(value: str, patterns: list[str], *, limit: int = 3) -> list[str]:
    normalized = re.sub(r"\s+", " ", value).strip()
    snippets: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, normalized, re.IGNORECASE):
            left = max(0, match.start() - 90)
            right = min(len(normalized), match.end() + 130)
            snippet = normalized[left:right].strip()
            if left:
                snippet = "…" + snippet
            if right < len(normalized):
                snippet += "…"
            if snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) >= limit:
                return snippets
    return snippets


def normalize_patent(
    publication: str,
    response: dict[str, Any],
    *,
    source_targets: list[str],
) -> dict[str, Any]:
    patents = response.get("patent_list") or []
    if not patents or not isinstance(patents[0], dict):
        return {
            "publication": publication,
            "status": "unresolved",
            "source_targets": source_targets,
            "message": "PatSeek 未返回该公开号的详情。",
            "credits_charged": response.get("credits_charged", 0) or 0,
        }
    patent = patents[0]
    claims = as_text(patent.get("claims"))
    description = as_text(patent.get("description"))
    claim_sequence_ids = sequence_ids(claims)
    disclosed_sequence_ids = sequence_ids(description)
    target_sequence_ids = sequence_ids(" ".join(source_targets))
    matched_ids = sorted(set(claim_sequence_ids) & set(target_sequence_ids), key=int)
    thresholds = identity_thresholds(claims)
    if matched_ids:
        claim_class = "C2_specific_seq_claim"
        claim_label = "权利要求明确引用命中序列编号"
    elif claim_sequence_ids or thresholds:
        claim_class = "C1_claim_signal"
        claim_label = "权利要求存在序列范围信号，尚未与命中序列逐项确认"
    elif set(disclosed_sequence_ids) & set(target_sequence_ids):
        claim_class = "C1_disclosed_only"
        claim_label = "命中序列编号仅在说明书中定位，权利要求未确认"
    else:
        claim_class = "C0_not_verified"
        claim_label = "未建立权利要求与命中序列的明确联系"
    enrichment = patent.get("enrichment") if isinstance(patent.get("enrichment"), dict) else {}
    aggregation = patent.get("aggregation") if isinstance(patent.get("aggregation"), dict) else {}
    snippets = evidence_snippets(
        claims,
        [r"\bSEQ(?:UENCE)?(?:\s+ID)?(?:\s+NO\.?)?\s*[:#]?\s*\d+\b", r"(?:at\s+least|至少|不低于|不少于)\s*\d+(?:\.\d+)?\s*%"],
    )
    canonical_url = as_text(enrichment.get("canonical_url"))
    if not canonical_url.startswith("https://"):
        canonical_url = f"https://patents.google.com/patent/{urllib.parse.quote(publication, safe='')}/en"
    return {
        "publication": publication,
        "status": "enriched",
        "pid": as_text(patent.get("pid")) or publication,
        "application_number": as_text(patent.get("appnum")),
        "title": as_text(patent.get("title")),
        "applicant": as_text(patent.get("applicant")),
        "inventors": enrichment.get("inventors") or [],
        "ipc": patent.get("ipcs") or [],
        "application_date": as_text(patent.get("appdate")),
        "publication_date": as_text(patent.get("pubdate")),
        "priority_date": as_text(enrichment.get("priority_date")),
        "legal_status": as_text(enrichment.get("legal_status")),
        "latest_legal_event": enrichment.get("latest_legal_event"),
        "family_count": enrichment.get("family_count"),
        "citation_count": enrichment.get("citation_count"),
        "cited_by_count": enrichment.get("cited_by_count"),
        "aggregation_status": as_text(aggregation.get("status")) or "unknown",
        "canonical_url": canonical_url,
        "source_targets": source_targets,
        "claim_evidence": {
            "class": claim_class,
            "label": claim_label,
            "target_sequence_ids": target_sequence_ids,
            "claim_sequence_ids": claim_sequence_ids,
            "matching_sequence_ids": matched_ids,
            "identity_thresholds": thresholds,
            "snippets": snippets,
            "claims_source": "PatSeek detail text; source location must be verified",
        },
        "credits_charged": response.get("credits_charged", 0) or 0,
        "credits_remaining": response.get("credits_remaining"),
    }


def create_plan(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    if not SEARCH_ID.fullmatch(args.search_id):
        raise EnrichmentError(
            "无效的本机序列检索 ID",
            code="SEARCH_ID_INVALID",
            user_action="请使用序列 Skill 返回的 pls_... ID。",
        )
    if not 1 <= args.top <= 20:
        raise EnrichmentError(
            "PatSeek 增强数量必须在 1 到 20 之间",
            code="TOP_INVALID",
            user_action="建议默认只增强去重后的前 5 个公开号。",
        )
    search = read_json(
        root / "searches" / f"{args.search_id}.json",
        missing_message="本机序列检索不存在",
    )
    publications, source_hits = collect_publications(search, top=args.top)
    availability = local_availability()
    base = {
        "operation": "patseek_enrichment_plan",
        "search_id": args.search_id,
        "query_digest": search.get("query_digest"),
        "candidate_publications": publications,
        "source_hits": source_hits,
        "planned_detail_calls": len(publications),
        "credits_unknown_until_response": True,
        "query_sequence_sent_to_patseek": False,
        "local_sequence_state_sent_to_patseek": False,
        "requires_confirmation": True,
        "availability": availability,
    }
    if not publications:
        return {
            **base,
            "ready": False,
            "status": "no_publication_mapping",
            "user_action": "当前候选没有可核验的 P1 公开号；请保留 P0 未解析状态，不要猜测专利号。",
        }
    if not availability.get("ready"):
        return {
            **base,
            "ready": False,
            "status": availability.get("status"),
            "user_action": availability.get("user_action"),
        }
    now = utc_now()
    plan = {
        **base,
        "ready": True,
        "status": "planned",
        "plan_id": f"pep_{uuid.uuid4().hex[:24]}",
        "created_at": iso(now),
        "expires_at": iso(now + timedelta(minutes=args.plan_ttl_minutes)),
    }
    write_json(root / "enrichment-plans" / f"{plan['plan_id']}.json", plan)
    return plan


def execute_plan(
    args: argparse.Namespace,
    root: Path,
    *,
    request_fn: Callable[..., dict[str, Any]] = api_request,
) -> dict[str, Any]:
    if not args.confirm_patseek_use:
        raise EnrichmentError(
            "执行 PatSeek 增强需要明确确认",
            code="PATSEEK_CONFIRMATION_REQUIRED",
            user_action="请先展示公开号数量、可能的详情调用和积分不确定性；用户确认后再加 --confirm-patseek-use。",
        )
    if not PLAN_ID.fullmatch(args.plan_id):
        raise EnrichmentError(
            "无效的 PatSeek 增强计划 ID",
            code="PLAN_ID_INVALID",
            user_action="请重新运行 patseek-plan。",
        )
    plan = read_json(
        root / "enrichment-plans" / f"{args.plan_id}.json",
        missing_message="PatSeek 增强计划不存在",
    )
    if datetime.fromisoformat(str(plan["expires_at"]).replace("Z", "+00:00")) < utc_now():
        raise EnrichmentError(
            "PatSeek 增强计划已过期",
            code="PLAN_EXPIRED",
            user_action="请重新生成零调用计划并再次确认。",
        )
    search = read_json(
        root / "searches" / f"{plan['search_id']}.json",
        missing_message="本机序列检索不存在",
    )
    if search.get("query_digest") != plan.get("query_digest"):
        raise EnrichmentError(
            "序列检索状态已变化",
            code="SEARCH_STATE_CHANGED",
            user_action="请重新生成 PatSeek 增强计划。",
        )
    output_path = root / "enrichments" / f"{plan['search_id']}.json"
    if output_path.exists():
        existing = read_json(output_path, missing_message="")
        if existing.get("plan_id") == args.plan_id:
            return {**existing, "idempotent_reuse": True}
    availability = local_availability()
    if not availability.get("ready"):
        return {
            "operation": "patseek_enrichment",
            "search_id": plan["search_id"],
            "plan_id": args.plan_id,
            "status": availability.get("status"),
            "user_action": availability.get("user_action"),
            "query_sequence_sent_to_patseek": False,
            "publications": [],
        }
    api_key = os.getenv("PATSEEK_API_KEY", "").strip()
    try:
        key_info = request_fn(
            "GET",
            "/v1/key-info",
            api_key=api_key,
            timeout=args.request_timeout,
        )
    except PatSeekHttpError as exc:
        status, action = http_failure(exc.status, str(exc))
        result = {
            "operation": "patseek_enrichment",
            "search_id": plan["search_id"],
            "plan_id": args.plan_id,
            "status": status,
            "message": str(exc),
            "user_action": action,
            "query_sequence_sent_to_patseek": False,
            "publications": [],
            "checked_at": iso(utc_now()),
        }
        write_json(output_path, result)
        return result
    except EnrichmentError as exc:
        result = {
            "operation": "patseek_enrichment",
            "search_id": plan["search_id"],
            "plan_id": args.plan_id,
            "status": "uncertain",
            "message": str(exc),
            "user_action": exc.user_action,
            "query_sequence_sent_to_patseek": False,
            "publications": [],
            "checked_at": iso(utc_now()),
        }
        write_json(output_path, result)
        return result
    key_failure = key_info_failure(key_info)
    if key_failure:
        status, action = key_failure
        result = {
            "operation": "patseek_enrichment",
            "search_id": plan["search_id"],
            "plan_id": args.plan_id,
            "status": status,
            "user_action": action,
            "query_sequence_sent_to_patseek": False,
            "publications": [],
            "key_info": sanitize_key_info(key_info),
            "checked_at": iso(utc_now()),
        }
        write_json(output_path, result)
        return result
    result: dict[str, Any] = {
        "operation": "patseek_enrichment",
        "search_id": plan["search_id"],
        "plan_id": args.plan_id,
        "status": "running",
        "checked_at": iso(utc_now()),
        "key_info": sanitize_key_info(key_info),
        "query_sequence_sent_to_patseek": False,
        "local_sequence_state_sent_to_patseek": False,
        "candidate_publications": plan.get("candidate_publications") or [],
        "publications": [],
        "not_attempted": list(plan.get("candidate_publications") or []),
        "credits_charged": 0,
        "credits_remaining": key_info.get("credits_remaining"),
        "legal_status_notice": "法律状态仅用于候选筛查，须以目标法域官方登记簿复核。",
    }
    write_json(output_path, result)
    for publication in plan.get("candidate_publications") or []:
        item = {
            "publication": publication,
            "status": "submitting",
            "source_targets": (plan.get("source_hits") or {}).get(publication) or [],
        }
        result["publications"].append(item)
        result["not_attempted"].remove(publication)
        write_json(output_path, result)
        market = "cn" if publication.startswith("CN") else "world"
        path = (
            f"/v1/patent/{urllib.parse.quote(publication, safe='.-')}"
            f"?market={market}&include_enrichment=true"
        )
        try:
            response = request_fn(
                "GET",
                path,
                api_key=api_key,
                timeout=args.request_timeout,
            )
        except PatSeekHttpError as exc:
            status, action = http_failure(exc.status, str(exc))
            item.update(status=status, message=str(exc))
            result.update(status=status, user_action=action)
            write_json(output_path, result)
            break
        except EnrichmentError as exc:
            item.update(status="uncertain", message=str(exc))
            result.update(status="uncertain", user_action=exc.user_action)
            write_json(output_path, result)
            break
        normalized = normalize_patent(
            publication,
            response,
            source_targets=item["source_targets"],
        )
        result["publications"][-1] = normalized
        result["credits_charged"] += int(response.get("credits_charged", 0) or 0)
        if response.get("credits_remaining") is not None:
            result["credits_remaining"] = response.get("credits_remaining")
        write_json(output_path, result)
        time.sleep(0.05)
    else:
        statuses = {item.get("status") for item in result["publications"]}
        result["status"] = "finished" if statuses <= {"enriched", "unresolved"} else "partial"
    result["completed_at"] = iso(utc_now())
    write_json(output_path, result)
    return result


def check_patseek(
    args: argparse.Namespace,
    *,
    request_fn: Callable[..., dict[str, Any]] = api_request,
) -> dict[str, Any]:
    result = local_availability()
    if not result.get("ready") or not args.validate_api_key:
        return result
    api_key = os.getenv("PATSEEK_API_KEY", "").strip()
    try:
        key_info = request_fn(
            "GET",
            "/v1/key-info",
            api_key=api_key,
            timeout=args.request_timeout,
        )
    except PatSeekHttpError as exc:
        status, action = http_failure(exc.status, str(exc))
        return {**result, "ready": False, "status": status, "user_action": action}
    key_failure = key_info_failure(key_info)
    if key_failure:
        status, action = key_failure
        return {
            **result,
            "ready": False,
            "status": status,
            "api_validation_required": False,
            "key_info": sanitize_key_info(key_info),
            "user_action": action,
        }
    return {
        **result,
        "ready": True,
        "status": "valid",
        "api_validation_required": False,
        "key_info": sanitize_key_info(key_info),
        "user_action": "PatSeek Skill 与 API Key 均有效；付费详情调用前仍需用户确认。",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Optional PatSeek enrichment for local sequence results")
    parser.add_argument("--state-dir")
    parser.add_argument("--request-timeout", type=float, default=30.0)
    parser.add_argument(
        "--transport",
        choices=("stdlib", "skill-client"),
        default="stdlib",
        help="HTTPS transport for optional PatSeek calls",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="Detect optional PatSeek capability")
    check.add_argument("--validate-api-key", action="store_true")
    plan = subparsers.add_parser("plan", help="Create a zero-call patent enrichment plan")
    plan.add_argument("search_id")
    plan.add_argument("--top", type=int, default=5)
    plan.add_argument("--plan-ttl-minutes", type=int, default=30)
    execute = subparsers.add_parser("execute", help="Run a confirmed PatSeek detail enrichment plan")
    execute.add_argument("--plan-id", required=True)
    execute.add_argument("--confirm-patseek-use", action="store_true")
    return parser


def print_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.state_dir).expanduser() if args.state_dir else state_dir_from_env()
    request_fn = skill_client_request if args.transport == "skill-client" else api_request
    try:
        if args.command == "check":
            result = check_patseek(args, request_fn=request_fn)
        else:
            ensure_dirs(root)
        if args.command == "plan":
            if args.plan_ttl_minutes < 1:
                raise EnrichmentError(
                    "计划有效期必须为正数",
                    code="PLAN_TTL_INVALID",
                    user_action="请使用大于 0 的分钟数。",
                )
            result = create_plan(args, root)
        elif args.command == "execute":
            result = execute_plan(args, root, request_fn=request_fn)
        print_json(result)
        return 0
    except EnrichmentError as exc:
        print_json({"error": str(exc), "code": exc.code, "user_action": exc.user_action})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
