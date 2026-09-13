import re


# Fields that must be removed completely, including the label.
REMOVE_FIELD_KEYWORDS = [
    "费别",
    "医疗保险就诊卡",
    "医保",
    "就诊卡",
    "就诊医师",
    "就诊医生签字",
    "就诊医生",
    # 科别可能携带院区/区县等可定位地理信息，整字段删除。
    "科别",
]

# Fields whose labels can remain, but whose values must be anonymized.
SENSITIVE_VALUE_FIELD_KEYWORDS = [
    "姓名",
    # 手写/低清扫描中“姓名”的常见 OCR 变体。
    "生名",
    "姓各",
    "身份",
    "身份证号",
    "身份证",
    "定点医疗机构编码",
    "定点医疗机构名称",
    "医疗机构编码",
    "医疗机构名称",
    "就诊时间",
    "打印时间",
    "出生日期",
    "出生年月",
    "联系电话",
    "手机号",
    "电话",
    "住址",
    "地址",
    "门诊号",
    "病历号",
    "病案号",
]

FIELD_BOUNDARY_KEYWORDS = [
    *REMOVE_FIELD_KEYWORDS,
    *SENSITIVE_VALUE_FIELD_KEYWORDS,
    "性别",
    "年龄",
    "科别",
    "主诉",
    "现病史",
    "既往史",
    "过敏史",
    "个人史",
    "家族史",
    "体格检查",
    "辅助检查",
    "诊断",
    "处理",
    "处置意见",
]

FIELD_BOUNDARY = "|".join(re.escape(keyword) for keyword in FIELD_BOUNDARY_KEYWORDS)
ALL_REMOVED_FIELD_KEYWORDS = sorted(
    set(REMOVE_FIELD_KEYWORDS + SENSITIVE_VALUE_FIELD_KEYWORDS),
    key=len,
    reverse=True,
)

KNOWN_ORGANIZATION_PATTERNS = [
    re.compile(r"北京大学第一医院"),
    # 本批门诊记录中的医院简称；简称同样具有机构可识别性。
    re.compile(r"东肿"),
    # OCR 可能漏掉“医院”后缀，仍按可定位机构名称处理。
    re.compile(r"大兴人民"),
]

GENERIC_ORGANIZATION_PATTERN = re.compile(
    r"[\u4e00-\u9fffA-Za-z0-9·（）()]{1,30}"
    r"(?:医院|门诊部|卫生院|社区卫生服务中心|医疗中心|医学中心|诊所)"
    r"(?:\s*[（(][^（）()]{0,20}[）)])?\s*[：:]?"
)

ID_NUMBER_PATTERN = re.compile(r"\d{17}[\dXx]")
PHONE_PATTERN = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
KNOWN_DOCTOR_NAME_PATTERN = re.compile(r"(?:余康|佘康|全康|余律|念律|杨敏|闫子光|孙浩林)")
TRAILING_DOCTOR_SIGNATURE_FRAGMENT_PATTERN = re.compile(
    r"(?<=[。；;，,])(?:念律|余律|律|念)$"
)
SURGEON_AFTER_SURGERY_PATTERN = re.compile(
    r"((?:手术方式[：:]?\s*|手术治疗|[\u4e00-\u9fffA-Za-z0-9]+术))"
    r"\s*[（(][\u4e00-\u9fff]{2,8}(?:医生|医师|主任|教授|大夫|先生)?[）)]"
)
SURGEON_AFTER_SURGERY_METHOD_PATTERN = re.compile(
    r"(手术方式[：:]?\s*)[（(][\u4e00-\u9fff]{2,4}(?:医生|医师|主任|教授|大夫|先生)?[）)]"
)


def desensitize_lines(lines: list[str]) -> list[str]:
    """Desensitize OCR text lines before writing patient markdown."""
    result = []
    for line in lines:
        new_line = line.strip()
        if not new_line:
            continue

        new_line = _remove_organizations(new_line)
        new_line = _remove_sensitive_fields(new_line)
        new_line = _desensitize_by_regex(new_line)
        new_line = _normalize_anonymized_blanks(new_line)

        if _should_keep_line(new_line):
            result.append(new_line)
    return result


def _remove_sensitive_fields(line: str) -> str:
    for field in ALL_REMOVED_FIELD_KEYWORDS:
        pattern = re.compile(rf"{re.escape(field)}[：:]?\s*.*?(?=(?:{FIELD_BOUNDARY})[：:]?|$)")
        line = pattern.sub("", line).strip()
    return line


def _remove_organizations(line: str) -> str:
    for pattern in KNOWN_ORGANIZATION_PATTERNS:
        line = pattern.sub("", line)
    return GENERIC_ORGANIZATION_PATTERN.sub("", line)


def _desensitize_by_regex(line: str) -> str:
    line = SURGEON_AFTER_SURGERY_PATTERN.sub(r"\1", line)
    line = SURGEON_AFTER_SURGERY_METHOD_PATTERN.sub(r"\1", line)
    line = ID_NUMBER_PATTERN.sub("", line)
    line = PHONE_PATTERN.sub("", line)
    line = KNOWN_DOCTOR_NAME_PATTERN.sub("", line)
    return TRAILING_DOCTOR_SIGNATURE_FRAGMENT_PATTERN.sub("", line)


def _normalize_anonymized_blanks(line: str) -> str:
    line = re.sub(r"\s+", " ", line).strip()
    line = _remove_irrelevant_chinese_spaces(line)
    line = re.sub(r"\s+([，,；;。])", r"\1", line)
    line = re.sub(r"([：:])\s*(?=([，,；;。]|$))", r"\1", line)
    line = re.sub(r"^[，,；;。]+", "", line).strip()
    return line


def _remove_irrelevant_chinese_spaces(line: str) -> str:
    # OCR often inserts visual-layout spaces inside Chinese text. Keep spaces
    # around Latin abbreviations/units and Markdown formatting intact.
    cjk = r"\u4e00-\u9fff"
    cn_punct = r"，。；：、？！）】》"
    left_punct = r"（【《"
    line = re.sub(rf"(?<=[{cjk}])\s+(?=[{cjk}])", "", line)
    line = re.sub(rf"(?<=[{cjk}])\s+(?=[{cn_punct}])", "", line)
    line = re.sub(rf"(?<=[{cn_punct}])\s+(?=[{cjk}])", "", line)
    line = re.sub(rf"(?<=[{left_punct}])\s+(?=[{cjk}])", "", line)
    return line


def _should_keep_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped in {"门诊病历", "病历记录"}:
        return False
    if re.fullmatch(r"[_*\-\s，,；;。:：]+", stripped):
        return False
    return True
