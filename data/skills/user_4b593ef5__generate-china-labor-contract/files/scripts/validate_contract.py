#!/usr/bin/env python3
"""Validate labor contract text before DOCX export.

The validator uses structured facts as the source of truth for fragile legal
rules, then scans contract text for deterministic prohibited expressions. Final
contracts must provide facts; blank templates should use document_mode=template.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import date
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from contract_text import is_contract_title, normalize_control_line, normalize_input
except ImportError:  # pragma: no cover - package import during tests
    from scripts.contract_text import is_contract_title, normalize_control_line, normalize_input


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


REQUIRED_SECTION_RULES = (
    ("REQUIRED_SUBJECTS", "合同主体信息", (r"^甲方（用人单位）.*[：:]", r"^乙方（劳动者）.*[：:]")),
    ("REQUIRED_TERM", "劳动合同期限", (r"合同期限[：:为]|固定期限|无固定期限|以完成一定工作任务为期限",)),
    ("REQUIRED_WORK", "工作内容和工作地点", (r"工作内容[：:]", r"工作地点[：:]")),
    ("REQUIRED_HOURS", "工作时间和休息休假", (r"工作时间", r"休息休假")),
    ("REQUIRED_PAY", "劳动报酬", (r"劳动报酬[：:]|工资(?:为|人民币|标准|按)",)),
    ("REQUIRED_SOCIAL_INSURANCE", "社会保险和福利待遇", (r"社会保险[：:]|参加社会保险|缴纳社会保险",)),
    ("REQUIRED_PROTECTION", "劳动保护", (r"劳动保护", r"劳动条件")),
    ("REQUIRED_TERMINATION", "解除终止", (r"解除", r"终止")),
    ("REQUIRED_DISPUTE", "劳动争议处理", (r"劳动争议", r"仲裁")),
    ("REQUIRED_SIGNATURE", "签署区", (r"^甲方（盖章）", r"^乙方（签字）")),
)

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "facts-schema.json"
FACTS_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

PROHIBITED_PATTERNS = (
    (
        "SOCIAL_INSURANCE_WAIVER",
        re.compile(r"(不缴纳社会保险|无需缴纳社会保险|放弃缴纳社保|放弃缴纳社会保险|自愿不参加社保|自愿不参加社会保险|自行缴纳社保|自行缴纳社会保险|现金补贴替代社保|现金补贴替代社会保险|社保.{0,12}随工资发放|社会保险.{0,12}随工资发放|单位承担部分随工资发放|社会保险费用全部由劳动者承担|社保费用全部由劳动者承担)"),
        "不得生成放弃社保或以现金补贴替代社保的条款。",
    ),
    (
        "ARBITRARY_JOB_ADJUSTMENT",
        re.compile(r"甲方.{0,12}(随时|任意|无条件).{0,30}(调整|变更).{0,30}(岗位|地点|薪酬|工时|工作时间)|甲方.{0,12}(调整|变更).{0,20}(岗位|地点|薪酬|工时|工作时间).{0,20}乙方应无条件(服从|接受)"),
        "不得约定甲方可随时、任意或无条件调整岗位、地点、薪酬或工时。",
    ),
    (
        "HOUSING_FUND_CONDITIONAL",
        re.compile(r"(根据经营情况|视经营情况|有条件|可).{0,12}缴存住房公积金|住房公积金.{0,12}(根据经营情况|视经营情况|有条件|可).{0,12}缴存"),
        "住房公积金不得写成由甲方经营情况决定的可选缴存事项。",
    ),
)

TERM_TYPES = set(FACTS_SCHEMA["enums"]["term_type"])
DOCUMENT_MODES = set(FACTS_SCHEMA["enums"]["document_mode"])
NONCOMPETE_MODES = set(FACTS_SCHEMA["enums"]["noncompete_mode"])
SOCIAL_INSURANCE_MODES = set(FACTS_SCHEMA["enums"]["social_insurance"])
REQUIRED_FACT_FIELDS = tuple(FACTS_SCHEMA["required_fields"])
FINAL_REQUIRED_FACT_FIELDS = tuple(FACTS_SCHEMA["final_required_fields"])
NUMBER_OR_NULL_FIELDS = tuple(FACTS_SCHEMA["number_or_null_fields"])
BOOLEAN_FIELDS = tuple(FACTS_SCHEMA["boolean_fields"])
DATE_OR_NULL_FIELDS = tuple(FACTS_SCHEMA["date_or_null_fields"])


def add_finding(findings: list[Finding], severity: str, code: str, message: str) -> None:
    findings.append(Finding(severity=severity, code=code, message=message))


def has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


CHINESE_DIGITS = {
    "零": 0,
    "〇": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}


def parse_number(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    if value.isdigit():
        return int(value)
    if "百" in value:
        before, after = value.split("百", 1)
        hundreds = parse_number(before) if before else 1
        rest = parse_number(after) if after else 0
        if hundreds is None or rest is None:
            return None
        return hundreds * 100 + rest
    if "十" in value:
        before, after = value.split("十", 1)
        tens = parse_number(before) if before else 1
        rest = parse_number(after) if after else 0
        if tens is None or rest is None:
            return None
        return tens * 10 + rest
    if len(value) == 1:
        return CHINESE_DIGITS.get(value)
    if all(char in CHINESE_DIGITS for char in value):
        result = 0
        for char in value:
            result = result * 10 + CHINESE_DIGITS[char]
        return result
    return None


def split_clauses(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[。；;\n]+", text) if part.strip()]


def searchable_units(text: str) -> list[str]:
    return [normalize_control_line(line) for line in normalize_input(text) if line.strip()] + split_clauses(text)


def unit_matches(text: str, pattern: str) -> bool:
    return any(re.search(pattern, unit) for unit in searchable_units(text))


def has_title(text: str) -> bool:
    return any(is_contract_title(line) for line in normalize_input(text))


def term_clauses(text: str) -> list[str]:
    clauses = split_clauses(text)
    selected: list[str] = []
    for clause in clauses:
        normalized = normalize_control_line(clause)
        if (
            "合同期限" in normalized
            or normalized.startswith(("固定期限", "无固定期限", "以完成一定工作任务为期限"))
        ):
            selected.append(normalized)
    return selected


def noncompete_clauses(text: str) -> list[str]:
    clauses = split_clauses(text)
    selected: list[str] = []
    for index, clause in enumerate(clauses):
        if infer_noncompete_mode(clause) == "full" or "竞业限制" in clause:
            selected.append(clause)
            for lookahead in range(index + 1, min(index + 3, len(clauses))):
                next_clause = clauses[lookahead]
                if re.search(r"(劳动报酬|社会保险|劳动保护|解除终止|劳动争议|甲方（盖章）|乙方（签字）)", next_clause):
                    break
                selected.append(next_clause)
    return selected


def extract_percentages(text: str) -> list[int]:
    percentages = [int(match) for match in re.findall(r"(\d{1,3})\s*%", text)]
    for match in re.findall(r"百分之([零〇一二两三四五六七八九十百\d]+)", text):
        parsed = parse_number(match)
        if parsed is not None:
            percentages.append(parsed)
    return percentages


def first_match_number(patterns: tuple[str, ...], text: str) -> int | None:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return parse_number(match.group(1))
    return None


def placeholder_count(text: str) -> int:
    return len(re.findall(r"_{2,}|____年__月__日|人民币____元", text))


def term_option_count(text: str) -> int:
    options = 0
    if "固定期限" in text:
        options += 1
    if "无固定期限" in text:
        options += 1
    if "以完成一定工作任务为期限" in text:
        options += 1
    return options


def looks_like_blank_template(text: str) -> bool:
    term_context = "\n".join(term_clauses(text)) or text
    has_multiple_term_options = term_option_count(term_context) >= 2
    has_many_placeholders = placeholder_count(text) >= 5 and placeholder_count(term_context) >= 2
    has_no_concrete_pay = not re.search(r"人民币\s*[1-9]\d*(?:\.\d+)?\s*元", text)
    return has_multiple_term_options and has_many_placeholders and has_no_concrete_pay


def infer_term_type(text: str) -> str | None:
    if looks_like_blank_template(text) or re.search(r"可选择固定期限、无固定期限或以完成一定工作任务为期限", text):
        return "template_options"
    context = "\n".join(term_clauses(text)) or text
    if "以完成一定工作任务为期限" in context:
        return "task"
    fixed_in_term = any("固定期限" in clause and "无固定期限" not in clause for clause in term_clauses(text))
    if fixed_in_term:
        return "fixed"
    if "无固定期限" in context:
        return "indefinite"
    if "固定期限" in context or re.search(r"合同期限[^。；\n]{0,20}[零〇一二两三四五六七八九十百\d]+\s*(年|个?月)", context):
        return "fixed"
    return None


def extract_term_months(text: str) -> int | None:
    context = "\n".join(term_clauses(text)) or text
    months = first_match_number(
        (
            r"(?:劳动合同期限|合同期限|期限)(?:为|是|共|合计|总计)?\s*([零〇一二两三四五六七八九十百\d]+)\s*个?月",
        ),
        context,
    )
    if months is not None:
        return months
    years = first_match_number(
        (
            r"(?:劳动合同期限|合同期限|期限)(?:为|是|共|合计|总计)?\s*([零〇一二两三四五六七八九十百\d]+)\s*年",
        ),
        context,
    )
    return years * 12 if years is not None else None


def parse_chinese_date(year: str, month: str, day: str) -> date | None:
    try:
        return date(int(year), int(month), int(day))
    except ValueError:
        return None


def extract_term_date_range(text: str) -> tuple[date, date] | None:
    context = "\n".join(term_clauses(text)) or text
    match = re.search(
        r"自\s*(\d{4})年(\d{1,2})月(\d{1,2})日(?:起)?\s*至\s*(\d{4})年(\d{1,2})月(\d{1,2})日(?:止)?",
        context,
    )
    if not match:
        return None
    start = parse_chinese_date(match.group(1), match.group(2), match.group(3))
    end = parse_chinese_date(match.group(4), match.group(5), match.group(6))
    if start is None or end is None:
        return None
    return start, end


def contract_months_between(start: date, end: date) -> int | None:
    if end < start:
        return None
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day >= start.day - 1:
        months += 1
    return months


def parse_iso_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def extract_probation_months(text: str) -> int | None:
    return first_match_number((r"试用期(?:为|是|：|:)?\s*([零〇一二两三四五六七八九十百\d]+)\s*个?月",), text)


def extract_probation_wage_ratio(text: str) -> float | None:
    for clause in split_clauses(text):
        if "试用期工资" not in clause:
            continue
        percentages = extract_percentages(clause)
        if percentages:
            return percentages[0] / 100
    return None


def extract_noncompete_months(text: str) -> int | None:
    months = first_match_number(
        (
            r"竞业限制期限(?:为|是|：|:)?\s*([零〇一二两三四五六七八九十百\d]+)\s*个?月",
            r"离职后\s*([零〇一二两三四五六七八九十百\d]+)\s*个?月内",
        ),
        text,
    )
    if months is not None:
        return months
    years = first_match_number(
        (
            r"竞业限制期限(?:为|是|：|:)?\s*([零〇一二两三四五六七八九十百\d]+)\s*年",
            r"离职后\s*([零〇一二两三四五六七八九十百\d]+)\s*年内",
        ),
        text,
    )
    return years * 12 if years is not None else None


def legal_holiday_pay_percentages(clause: str) -> list[int]:
    direct = re.search(r"(法定节假日|法定休假日).{0,20}(加班工资|工资报酬|工资)(?:为|按|按照|不低于|标准为)?\s*(\d{2,3})\s*%", clause)
    if direct:
        return [int(direct.group(3))]
    direct_cn = re.search(r"(法定节假日|法定休假日).{0,20}(加班工资|工资报酬|工资)(?:为|按|按照|不低于|标准为)?\s*百分之([零〇一二两三四五六七八九十百\d]+)", clause)
    if direct_cn:
        parsed = parse_number(direct_cn.group(3))
        return [parsed] if parsed is not None else []
    direct_times = re.search(r"(法定节假日|法定休假日).{0,30}(?:支付|发放|计发).{0,6}([零〇一二两三四五六七八九十百\d]+)\s*倍\s*(?:工资|加班工资|加班费)", clause)
    if direct_times:
        parsed = parse_number(direct_times.group(2))
        return [parsed * 100] if parsed is not None else []
    tail = re.search(r"(法定节假日|法定休假日)[^。；\n]*", clause)
    if tail:
        tail_text = tail.group(0)
        percentages = extract_percentages(tail_text)
        times = re.findall(r"(?:支付|发放|计发).{0,6}([零〇一二两三四五六七八九十百\d]+)\s*倍\s*(?:工资|加班工资|加班费)", tail_text)
        for item in times:
            parsed = parse_number(item)
            if parsed is not None:
                percentages.append(parsed * 100)
        return percentages
    return []


def infer_noncompete_mode(text: str) -> str:
    if re.search(r"(未约定|不约定|无).{0,8}竞业限制", text):
        return "none"
    full_patterns = (
        r"竞业限制.{0,20}(义务|期限|补偿|违约|范围|地域)",
        r"离职后.{0,30}不得.{0,30}(竞争单位|竞争关系|同业单位|竞争对手|竞争性业务)",
        r"不得.{0,20}(去|到|加入|任职于).{0,20}(竞争单位|同业单位|竞争对手)",
    )
    if any(re.search(pattern, text) for pattern in full_patterns):
        return "full"
    if re.search(r"(另行签署|另行签订|可另行签署|可另行签订).{0,8}竞业限制协议", text):
        return "reference_only"
    return "none"


def validate_facts_schema(text: str, raw_facts: Any, findings: list[Finding]) -> dict[str, Any]:
    if raw_facts is None:
        add_finding(findings, "error", "FACTS_REQUIRED", "最终合同导出必须提供结构化 facts；空白模板使用 document_mode: template。")
        return {}
    if not isinstance(raw_facts, dict):
        add_finding(findings, "error", "FACTS_NOT_OBJECT", "facts 必须是 JSON object。")
        return {}

    for field in REQUIRED_FACT_FIELDS:
        if field not in raw_facts:
            add_finding(findings, "error", "FACTS_MISSING_FIELD", f"facts 缺少必填字段：{field}。")

    schema_version = raw_facts.get("schema_version")
    if not isinstance(schema_version, int) or isinstance(schema_version, bool) or schema_version != 1:
        add_finding(findings, "error", "FACTS_INVALID_SCHEMA_VERSION", "facts.schema_version 必须为整数 1。")

    for field, allowed in (
        ("document_mode", DOCUMENT_MODES),
        ("term_type", TERM_TYPES),
        ("noncompete_mode", NONCOMPETE_MODES),
        ("social_insurance", SOCIAL_INSURANCE_MODES),
    ):
        value = raw_facts.get(field)
        if not isinstance(value, str):
            add_finding(findings, "error", "FACTS_INVALID_TYPE", f"facts.{field} 必须是字符串枚举值。")
        elif value not in allowed:
            code = "SOCIAL_INSURANCE_FACT_INVALID" if field == "social_insurance" else "FACTS_INVALID_ENUM"
            add_finding(findings, "error", code, f"facts.{field} 取值无效：{value!r}。")

    for field in NUMBER_OR_NULL_FIELDS:
        if field not in raw_facts or raw_facts.get(field) is None:
            continue
        value = raw_facts.get(field)
        if not is_number(value):
            add_finding(findings, "error", "FACTS_INVALID_TYPE", f"facts.{field} 必须是数字或 null。")
        elif not math.isfinite(value) or value < 0:
            add_finding(findings, "error", "FACTS_INVALID_NUMBER", f"facts.{field} 不得为负数。")

    for field in BOOLEAN_FIELDS:
        value = raw_facts.get(field)
        if not isinstance(value, bool):
            add_finding(findings, "error", "FACTS_INVALID_TYPE", f"facts.{field} 必须是布尔值。")

    for field in DATE_OR_NULL_FIELDS:
        value = raw_facts.get(field)
        if value is None:
            continue
        if not isinstance(value, str):
            add_finding(findings, "error", "FACTS_INVALID_TYPE", f"facts.{field} 必须是 ISO 日期字符串或 null。")
            continue
        try:
            date.fromisoformat(value)
        except ValueError:
            add_finding(findings, "error", "FACTS_INVALID_TYPE", f"facts.{field} 必须是有效 ISO 日期字符串。")

    document_mode = raw_facts.get("document_mode")
    term_type = raw_facts.get("term_type")
    probation_months = raw_facts.get("probation_months")
    probation_wage_ratio = raw_facts.get("probation_wage_ratio")
    noncompete_mode = raw_facts.get("noncompete_mode")
    term_months = raw_facts.get("term_months")
    noncompete_months = raw_facts.get("noncompete_months")

    if document_mode == "final" and raw_facts.get("term_type") == "template_options":
        add_finding(findings, "error", "FACTS_INVALID_ENUM", "最终合同不得使用 term_type: template_options。")
    if document_mode == "final":
        for field in FINAL_REQUIRED_FACT_FIELDS:
            if field not in raw_facts:
                add_finding(findings, "error", "FACTS_MISSING_FIELD", f"最终合同 facts 必须包含 {field}。")
        if "contract_sha256" not in raw_facts:
            pass
        elif not isinstance(raw_facts.get("contract_sha256"), str):
            add_finding(findings, "error", "FACTS_INVALID_TYPE", "facts.contract_sha256 必须是当前正式合同正文的 sha256 字符串。")
        if term_type == "fixed" and (not is_number(term_months) or term_months <= 0):
            add_finding(findings, "error", "FACTS_CONDITIONAL_REQUIRED", "final + fixed 时 facts.term_months 必须为正数。")
        if term_type in {"indefinite", "task"} and term_months is not None:
            add_finding(findings, "error", "FACTS_CONDITIONAL_REQUIRED", "final + indefinite/task 时 facts.term_months 应为 null。")
        if probation_months is None:
            add_finding(findings, "error", "FACTS_CONDITIONAL_REQUIRED", "final 合同必须明确 facts.probation_months，未约定时填 0。")
        if is_number(probation_months) and probation_months > 0 and not is_number(probation_wage_ratio):
            add_finding(findings, "error", "FACTS_CONDITIONAL_REQUIRED", "约定试用期时必须提供 facts.probation_wage_ratio。")
        if is_number(probation_months) and probation_months == 0 and probation_wage_ratio is not None:
            add_finding(findings, "error", "FACTS_CONDITIONAL_REQUIRED", "未约定试用期时 facts.probation_wage_ratio 应为 null。")
        if noncompete_mode == "full":
            if raw_facts.get("noncompete_person_eligible") is not True:
                add_finding(findings, "error", "NONCOMPETE_PERSON_NOT_ELIGIBLE", "完整竞业限制必须确认劳动者属于法定适用人员。")
            if raw_facts.get("secret_access_confirmed") is not True:
                add_finding(findings, "error", "NONCOMPETE_MISSING_SECRET_ACCESS", "完整竞业限制必须确认劳动者实际知悉或接触商业秘密。")
            if not is_number(noncompete_months) or noncompete_months <= 0:
                add_finding(findings, "error", "FACTS_CONDITIONAL_REQUIRED", "完整竞业限制必须提供正数 facts.noncompete_months。")
            if raw_facts.get("noncompete_compensation_confirmed") is not True:
                add_finding(findings, "error", "NONCOMPETE_MISSING_COMPENSATION", "完整竞业限制必须确认经济补偿。")
        elif noncompete_months is not None:
            add_finding(findings, "error", "FACTS_CONDITIONAL_REQUIRED", "非完整竞业限制模式下 facts.noncompete_months 应为 null。")
    if document_mode == "template":
        if term_type != "template_options":
            add_finding(findings, "error", "FACTS_CONDITIONAL_REQUIRED", "template 模式必须使用 term_type: template_options。")
        for field in ("term_months", "probation_months", "probation_wage_ratio", "noncompete_months"):
            if raw_facts.get(field) is not None:
                add_finding(findings, "error", "FACTS_CONDITIONAL_REQUIRED", f"template 模式下 facts.{field} 应为 null。")

    if "contract_sha256" in raw_facts:
        expected = raw_facts.get("contract_sha256")
        actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if not isinstance(expected, str) or expected != actual:
            add_finding(findings, "error", "FACTS_CONTRACT_HASH_MISMATCH", "facts.contract_sha256 与当前合同正文不匹配。")

    return raw_facts


def validate_required_sections(text: str, facts: dict[str, Any], findings: list[Finding]) -> None:
    severity = "warning" if facts.get("document_mode") == "template" else "error"
    for code, label, patterns in REQUIRED_SECTION_RULES:
        if not all(unit_matches(text, pattern) for pattern in patterns):
            add_finding(findings, severity, code, f"可能缺少{label}模块。")


def validate_overtime(text: str, findings: list[Finding]) -> None:
    clauses = split_clauses(text)
    for index, clause in enumerate(clauses):
        if re.search(r"(法定节假日|法定休假日).{0,30}(加班|安排工作).{0,30}(不另行支付|不支付|无需支付|不计发).{0,12}(加班工资|加班费)", clause):
            add_finding(
                findings,
                "error",
                "OVERTIME_LEGAL_HOLIDAY_NO_PAY",
                "法定节假日安排加班不得约定不支付或不另行支付加班工资。",
            )
            break
        direct_comp_time = re.search(r"(法定节假日|法定休假日).{0,30}(加班|安排工作).{0,30}(补休|调休|安排休息)", clause)
        next_clause_comp_time = (
            re.search(r"(法定节假日|法定休假日).{0,30}(加班|安排工作)", clause)
            and index + 1 < len(clauses)
            and re.search(r"(甲方|用人单位)?.{0,12}(可以|可|安排).{0,12}(补休|调休|安排休息)", clauses[index + 1])
        )
        if not direct_comp_time and not next_clause_comp_time:
            continue
        context = clause if direct_comp_time else f"{clause}。{clauses[index + 1]}"
        if re.search(r"(300%|百分之三百)", context) and re.search(r"(额外|另行|同时|并).{0,12}(补休|调休|安排休息)", context):
            continue
        if re.search(r"(不得|不能|不可).{0,6}(补休|调休|安排休息).{0,12}替代", context):
            continue
        add_finding(
            findings,
            "error",
            "OVERTIME_LEGAL_HOLIDAY_COMP_TIME",
            "法定节假日加班不得以补休替代法定加班工资，应按不低于工资的300%支付。",
        )
        break
    for clause in clauses:
        if not re.search(r"(法定节假日|法定休假日).{0,30}(加班|安排工作)", clause):
            continue
        percentages = legal_holiday_pay_percentages(clause)
        if percentages and max(percentages) < 300:
            add_finding(
                findings,
                "error",
                "OVERTIME_LEGAL_HOLIDAY_UNDERPAID",
                "法定节假日加班工资不得低于工资的300%。",
            )
            break
    if "加班" in text and not all(term in text for term in ("150%", "200%", "300%")):
        add_finding(
            findings,
            "warning",
            "OVERTIME_RATE_DETAIL_MISSING",
            "加班条款建议明确工作日150%、休息日不能补休则200%、法定节假日300%。",
        )


def legal_probation_max_months(term_months: int | float | None) -> int | None:
    if term_months is None:
        return None
    if term_months < 3:
        return 0
    if term_months < 12:
        return 1
    if term_months < 36:
        return 2
    return 6


def validate_probation(text: str, facts: dict[str, Any], findings: list[Finding]) -> None:
    term_type = facts.get("term_type")
    probation_months = facts.get("probation_months")
    term_months = facts.get("term_months")
    valid_probation_months = probation_months if is_number(probation_months) else None
    valid_term_months = term_months if is_number(term_months) else None

    if term_type == "task" and valid_probation_months:
        add_finding(
            findings,
            "error",
            "PROBATION_TASK_CONTRACT",
            "以完成一定工作任务为期限的劳动合同不得约定试用期。",
        )
    max_months = legal_probation_max_months(valid_term_months)
    if valid_probation_months is not None and max_months is not None and valid_probation_months > max_months:
        add_finding(
            findings,
            "error",
            "PROBATION_EXCEEDS_LEGAL_MAX",
            f"合同期限对应试用期上限为{max_months}个月，当前事实为{valid_probation_months}个月。",
        )

    text_probation_months = extract_probation_months(text)
    if valid_probation_months is not None and text_probation_months is not None and valid_probation_months != text_probation_months:
        add_finding(findings, "error", "PROBATION_FACTS_TEXT_CONFLICT", "facts.probation_months 与正文试用期月数不一致。")
    if is_number(facts.get("probation_wage_ratio")) and facts["probation_wage_ratio"] < 0.8:
        add_finding(findings, "error", "PROBATION_WAGE_RATIO_LOW", "试用期工资不得低于劳动合同约定工资的80%。")
    if valid_probation_months and facts.get("prior_probation_used") is True:
        add_finding(findings, "error", "PROBATION_REPEAT", "同一用人单位与同一劳动者只能约定一次试用期。")

    text_wage_ratio = extract_probation_wage_ratio(text)
    if text_wage_ratio is not None:
        if text_wage_ratio < 0.8:
            add_finding(findings, "error", "PROBATION_WAGE_RATIO_LOW", "试用期工资不得低于劳动合同约定工资的80%。")
        fact_wage_ratio = facts.get("probation_wage_ratio")
        if is_number(fact_wage_ratio) and abs(fact_wage_ratio - text_wage_ratio) > 0.001:
            add_finding(findings, "error", "PROBATION_WAGE_FACTS_TEXT_CONFLICT", "facts.probation_wage_ratio 与正文试用期工资比例不一致。")

    if re.search(r"以完成一定工作任务为期限的劳动合同[，,。；;、 ]*试用期(?:为|是|：)", text):
        add_finding(
            findings,
            "error",
            "PROBATION_TASK_CONTRACT",
            "以完成一定工作任务为期限的劳动合同不得约定试用期。",
        )
    if re.search(r"(不满三个月|不足三个月|少于三个月).{0,30}(约定|设置|设定).{0,8}试用期", text):
        add_finding(
            findings,
            "error",
            "PROBATION_UNDER_THREE_MONTHS",
            "期限不满三个月的劳动合同不得约定试用期。",
        )
    if re.search(r"(同一用人单位|同一单位).{0,12}(再次|重复|二次|重新).{0,12}约定试用期", text):
        add_finding(findings, "error", "PROBATION_REPEAT", "同一用人单位与同一劳动者只能约定一次试用期。")
    if re.search(r"试用期工资[^。；\n]*(50%|百分之五十|60%|百分之六十|70%|百分之七十)", text):
        add_finding(findings, "error", "PROBATION_WAGE_RATIO_LOW", "试用期工资不得低于劳动合同约定工资的80%。")


def validate_noncompete(text: str, facts: dict[str, Any], findings: list[Finding]) -> None:
    noncompete_mode = facts.get("noncompete_mode")
    text_noncompete_mode = infer_noncompete_mode(text)
    context = "。".join(noncompete_clauses(text))

    if noncompete_mode in {"none", "reference_only"} and text_noncompete_mode == "full":
        add_finding(findings, "error", "NONCOMPETE_FACTS_TEXT_CONFLICT", "facts 显示未设置完整竞业限制，但正文写入了完整竞业限制义务。")
    if noncompete_mode == "full" and text_noncompete_mode != "full":
        add_finding(findings, "error", "NONCOMPETE_FACTS_TEXT_CONFLICT", "facts 显示完整竞业限制，但正文未写入完整竞业限制条款。")

    has_full_noncompete = noncompete_mode == "full" or text_noncompete_mode == "full"
    if not has_full_noncompete:
        return

    secret_access_fact = facts.get("secret_access_confirmed") if isinstance(facts.get("secret_access_confirmed"), bool) else False
    secret_access = secret_access_fact or has_any(
        context,
        ("知悉商业秘密", "接触商业秘密", "掌握商业秘密", "实际接触", "实际知悉"),
    )
    person_eligible = facts.get("noncompete_person_eligible") is True or has_any(context, ("高级管理人员", "高级技术人员", "负有保密义务"))
    proportionality = has_any(context, ("相适应", "必要范围", "合理范围", "比例"))
    compensation = has_any(context, ("经济补偿", "竞业补偿", "补偿金"))
    compensation_detail = compensation and has_any(context, ("按月", "每月", "人民币", "工资", "标准", "计算方式", "支付周期"))

    if not person_eligible:
        add_finding(findings, "error", "NONCOMPETE_PERSON_NOT_ELIGIBLE", "完整竞业限制必须限于高级管理人员、高级技术人员或其他负有保密义务的人员。")
    if not secret_access:
        add_finding(
            findings,
            "error",
            "NONCOMPETE_MISSING_SECRET_ACCESS",
            "完整竞业限制条款应有劳动者实际知悉或接触商业秘密的事实基础；否则只保留专项协议承接。",
        )
    if not proportionality:
        add_finding(
            findings,
            "error",
            "NONCOMPETE_MISSING_PROPORTIONALITY",
            "竞业限制范围、地域、期限应与劳动者知悉或接触的商业秘密相适应。",
        )
    text_months = extract_noncompete_months(context)
    if text_months is None:
        add_finding(findings, "error", "NONCOMPETE_MISSING_TERM", "完整竞业限制正文必须写明竞业限制期限。")
    if not compensation_detail:
        add_finding(findings, "error", "NONCOMPETE_MISSING_COMPENSATION", "完整竞业限制正文必须写明经济补偿标准、计算方式或支付周期。")
    fact_months = facts.get("noncompete_months")
    if is_number(fact_months) and text_months is not None and fact_months != text_months:
        add_finding(findings, "error", "NONCOMPETE_FACTS_TEXT_CONFLICT", "facts.noncompete_months 与正文竞业限制期限不一致。")
    if (is_number(fact_months) and fact_months > 24) or (text_months is not None and text_months > 24):
        add_finding(findings, "error", "NONCOMPETE_OVER_24_MONTHS", "竞业限制期限不得超过二年。")


def validate_delivery(text: str, findings: list[Finding]) -> None:
    for clause in split_clauses(text):
        if is_negative_rule_clause(clause):
            continue
        if re.search(r"(未经|未).{0,8}(系统)?确认到达.{0,8}(也|亦)?视[为作]送达", clause):
            add_finding(
                findings,
                "error",
                "DELIVERY_SENT_EQUALS_SERVED",
                "文书送达不得在未确认到达或未可证明收悉时约定视为送达。",
            )
            break
        if not re.search(r"(发送|发出|寄出|发出即).{0,30}视[为作]送达", clause):
            continue
        if "未经" not in clause and re.search(r"(发送|发出|寄出).{0,30}(确认到达|系统确认到达|签收|实际收悉).{0,20}视[为作]送达", clause):
            continue
        add_finding(
            findings,
            "error",
            "DELIVERY_SENT_EQUALS_SERVED",
            "文书送达不得简单约定已发送即视为送达，应区分内部管理文件、解除终止通知和仲裁诉讼送达，并以到达、签收或可证明收悉为依据。",
        )
        break


def validate_text_facts_consistency(text: str, facts: dict[str, Any], findings: list[Finding]) -> None:
    document_mode = facts.get("document_mode")
    term_type = facts.get("term_type")
    text_term_type = infer_term_type(text)
    blank_template = looks_like_blank_template(text)

    if document_mode == "template":
        looks_like_final = has_title(text) and not blank_template and text_term_type != "template_options"
        if looks_like_final:
            add_finding(findings, "error", "DOCUMENT_MODE_TEXT_CONFLICT", "facts.document_mode 为 template，但正文看起来是最终合同。")
        return

    if document_mode != "final":
        return

    if blank_template or text_term_type == "template_options":
        add_finding(findings, "error", "DOCUMENT_MODE_TEXT_CONFLICT", "facts.document_mode 为 final，但正文看起来是空白多选模板。")
        return

    if text_term_type and text_term_type != "template_options" and term_type in TERM_TYPES and text_term_type != term_type:
        add_finding(findings, "error", "TERM_FACTS_TEXT_CONFLICT", "facts.term_type 与正文合同期限类型不一致。")

    text_term_months = extract_term_months(text)
    fact_term_months = facts.get("term_months")
    if term_type == "fixed" and is_number(fact_term_months) and text_term_months is not None and fact_term_months != text_term_months:
        add_finding(findings, "error", "TERM_FACTS_TEXT_CONFLICT", "facts.term_months 与正文固定期限月数不一致。")

    text_dates = extract_term_date_range(text)
    fact_start_raw = facts.get("term_start_date")
    fact_end_raw = facts.get("term_end_date")
    fact_start = parse_iso_date(fact_start_raw)
    fact_end = parse_iso_date(fact_end_raw)
    start = fact_start or (text_dates[0] if text_dates else None)
    end = fact_end or (text_dates[1] if text_dates else None)
    if start and end:
        months_from_dates = contract_months_between(start, end)
        if months_from_dates is None:
            add_finding(findings, "error", "TERM_DATE_ORDER_INVALID", "固定期限起止日期先后顺序不合法。")
        elif term_type == "fixed" and is_number(fact_term_months) and fact_term_months != months_from_dates:
            add_finding(findings, "error", "TERM_FACTS_TEXT_CONFLICT", "facts.term_months 与合同起止日期计算结果不一致。")
    if text_dates and fact_start and fact_end and (text_dates[0] != fact_start or text_dates[1] != fact_end):
        add_finding(findings, "error", "TERM_FACTS_TEXT_CONFLICT", "facts 起止日期与正文合同期限日期不一致。")


def validate_penalties(text: str, findings: list[Finding]) -> None:
    for clause in split_clauses(text):
        if "违约金" not in clause and "固定赔偿" not in clause:
            continue
        if re.search(r"(违反|违反.*义务|不履行|违反约定).{0,12}(竞业限制|服务期|专项培训|专业技术培训).{0,30}(违约金|固定赔偿)", clause):
            continue
        if re.search(r"(竞业限制|服务期|专项培训|专业技术培训).{0,20}(违约责任|违约金|固定赔偿)", clause) and not re.search(r"(任何违约|任一违约|一切违约|所有违约|违反本合同任何约定)", clause):
            continue
        if re.search(r"(违反本合同任何约定|任何违约|任一违约|一切违约|所有违约).{0,30}(违约金|固定赔偿)", clause):
            add_finding(findings, "error", "GENERAL_LABOR_PENALTY", "培训服务期和竞业限制以外不得泛化约定劳动者违约金。")
            break
        if re.search(r"(违反本合同约定|违约).{0,12}(应|须)?\s*(支付|承担).{0,6}违约金(?:人民币)?\s*[0-9零〇一二两三四五六七八九十百千万]+", clause):
            add_finding(findings, "error", "GENERAL_LABOR_PENALTY", "培训服务期和竞业限制以外不得泛化约定劳动者违约金。")
            break
        if re.search(r"(应|须)?\s*支付违约金(?:人民币)?\s*[0-9零〇一二两三四五六七八九十百千万]+", clause):
            add_finding(findings, "error", "GENERAL_LABOR_PENALTY", "培训服务期和竞业限制以外不得泛化约定劳动者违约金。")
            break


def validate_job_adjustment(text: str, findings: list[Finding]) -> None:
    for clause in split_clauses(text):
        if re.search(r"(不得|不能|不可).{0,8}(随时|任意|无条件).{0,20}(调整|变更)", clause):
            continue
        if re.search(r"甲方.{0,12}(随时|任意|无条件).{0,30}(调整|变更).{0,30}(岗位|地点|薪酬|工时|工作时间)", clause):
            add_finding(findings, "error", "ARBITRARY_JOB_ADJUSTMENT", "不得约定甲方可随时、任意或无条件调整岗位、地点、薪酬或工时。")
            break
        if re.search(r"甲方.{0,12}(调整|变更).{0,20}(岗位|地点|薪酬|工时|工作时间).{0,20}乙方应无条件(服从|接受)", clause):
            add_finding(findings, "error", "ARBITRARY_JOB_ADJUSTMENT", "不得约定甲方可随时、任意或无条件调整岗位、地点、薪酬或工时。")
            break


def validate_false_materials(text: str, findings: list[Finding]) -> None:
    for clause in split_clauses(text):
        if re.search(r"(提供虚假|提交.{0,6}不实).{0,12}(资料|材料|信息)?.{0,30}(立即解除|即时解除|解除本合同|单方解除|即可解除|可以解除)", clause):
            if all(term in clause for term in ("与录用直接相关", "影响录用决定")):
                continue
            add_finding(
                findings,
                "error",
                "FALSE_MATERIALS_OVERBROAD_TERMINATION",
                "虚假录用资料作为解除依据时，应限于重要、与录用直接相关且足以影响录用决定的资料，并衔接欺诈致合同无效或严重违反有效规章制度等法定依据。",
            )
            break


def validate_guidance_leakage(text: str, findings: list[Finding]) -> None:
    if has_any(text, ("策略判断卡", "【已重点处理以下用工风险相关条款】", "待补充字段", "请选择导出方式")):
        add_finding(findings, "error", "GUIDANCE_TEXT_IN_CONTRACT", "正式合同正文中不得混入策略卡、风险说明、待补充字段或导出动作。")


def validate_placeholders(text: str, findings: list[Finding]) -> None:
    if re.search(r"[：:]\s*[，。；]", text):
        add_finding(findings, "warning", "EMPTY_FIELD_VALUE", "仍存在冒号后为空的字段，导出前应补占位符或具体内容。")


def is_negative_rule_clause(clause: str) -> bool:
    return bool(re.search(r"(不得|不能|不可|禁止|不应).{0,20}(自行缴纳|根据经营情况|视经营情况|仅以发送|发送视为送达|发出即视为送达|选择是否缴存)", clause))


def validate_prohibited_patterns(text: str, findings: list[Finding]) -> None:
    for code, pattern, message in PROHIBITED_PATTERNS:
        if code == "ARBITRARY_JOB_ADJUSTMENT":
            continue
        for clause in split_clauses(text):
            if is_negative_rule_clause(clause):
                continue
            if pattern.search(clause):
                add_finding(findings, "error", code, message)
                break


def validate_contract(text: str, facts: dict[str, Any] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    parsed_facts = validate_facts_schema(text, facts, findings)
    validate_required_sections(text, parsed_facts, findings)
    validate_text_facts_consistency(text, parsed_facts, findings)
    validate_overtime(text, findings)
    validate_probation(text, parsed_facts, findings)
    validate_noncompete(text, parsed_facts, findings)
    validate_delivery(text, findings)
    validate_penalties(text, findings)
    validate_job_adjustment(text, findings)
    validate_false_materials(text, findings)
    validate_guidance_leakage(text, findings)
    validate_placeholders(text, findings)
    validate_prohibited_patterns(text, findings)
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate China labor contract text.")
    parser.add_argument("--input", "-i", type=Path, help="Path to a UTF-8 text or Markdown contract file.")
    parser.add_argument("--facts", type=Path, help="Path to structured contract facts JSON.")
    parser.add_argument("--json", action="store_true", help="Emit JSON findings.")
    parser.add_argument("--warnings-as-errors", action="store_true", help="Exit nonzero when warnings exist.")
    return parser.parse_args()


def read_utf8_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR cannot read input file: {exc}") from None
    except UnicodeDecodeError as exc:
        raise SystemExit(f"ERROR input file must be UTF-8: {exc}") from None


def read_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"ERROR cannot read facts file: {exc}") from None
    except UnicodeDecodeError as exc:
        raise SystemExit(f"ERROR facts file must be UTF-8: {exc}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR invalid facts JSON: {exc.msg} at line {exc.lineno} column {exc.colno}") from None


def main() -> None:
    args = parse_args()
    text = read_utf8_text(args.input) if args.input else sys.stdin.read()
    facts = read_json_file(args.facts) if args.facts else None
    findings = validate_contract(text, facts=facts)

    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    else:
        for finding in findings:
            print(f"{finding.severity.upper()} {finding.code}: {finding.message}")

    has_errors = any(finding.severity == "error" for finding in findings)
    has_warnings = any(finding.severity == "warning" for finding in findings)
    if has_errors or (args.warnings_as_errors and has_warnings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
