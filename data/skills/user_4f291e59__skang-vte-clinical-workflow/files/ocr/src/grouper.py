import re


def extract_patient_id(lines: list[str]) -> tuple[str, str | None] | None:
    """从文本行中提取患者标识（姓名+就诊卡号）。

    Args:
        lines: OCR识别出的文本行列表

    Returns:
        (姓名, 就诊卡号) 元组。就诊卡号可能为None。
        若姓名缺失则返回None
    """
    name = None
    card = None

    for line in lines:
        # 匹配 "姓名 张三" 或 "姓名：张三" 格式
        name_match = re.match(r"姓名[：:]?\s*(.+)", line)
        if name_match:
            name = name_match.group(1).strip()
            continue

        card_match = re.match(r"就诊卡[：:]?\s*(.+)", line)
        if card_match:
            card = card_match.group(1).strip()
            continue

    if name:
        return (name, card)
    return None


def extract_page_number(lines: list[str]) -> int | None:
    """从文本行中提取页码信息。

    支持格式：'第1/3页'、'第2页'

    Returns:
        页码数字，未找到则返回None
    """
    for line in lines:
        match = re.search(r"第(\d+)[/页]", line)
        if match:
            return int(match.group(1))
    return None


def group_pages_by_patient(pages: list[dict]) -> tuple[list[dict], list[dict]]:
    """将页面按患者标识分组，组内按页码排序。

    分组策略：
    1. 有姓名+就诊卡的页面：以姓名+就诊卡为唯一键
    2. 仅有姓名的页面：先尝试匹配已有同姓名+就诊卡的组，否则以姓名为键单独分组
    3. 无姓名的页面：归入unclassified

    Args:
        pages: 每个元素为 {"pdf_page": int, "lines": [str]}

    Returns:
        (groups, unclassified)
        groups: [{"patient_id": (name, card), "pages": [...]}, ...]
        unclassified: 无法提取患者标识的页面列表
    """
    patient_map = {}  # key -> [pages]
    unclassified = []

    # 先处理有就诊卡的页面，建立完整标识
    pages_with_card = []
    pages_name_only = []
    pages_no_name = []

    for page in pages:
        patient_id = extract_patient_id(page["lines"])
        if patient_id is None:
            pages_no_name.append(page)
        elif patient_id[1] is not None:
            pages_with_card.append((page, patient_id))
        else:
            pages_name_only.append((page, patient_id))

    # 处理有姓名+就诊卡的页面
    for page, patient_id in pages_with_card:
        if patient_id not in patient_map:
            patient_map[patient_id] = []
        patient_map[patient_id].append(page)

    # 处理仅有姓名的页面：尝试匹配同姓名的组
    for page, patient_id in pages_name_only:
        name = patient_id[0]
        matched_key = None
        for key in patient_map:
            if key[0] == name and key[1] is not None:
                matched_key = key
                break
        if matched_key:
            patient_map[matched_key].append(page)
        else:
            if patient_id not in patient_map:
                patient_map[patient_id] = []
            patient_map[patient_id].append(page)

    # 无姓名的页面归入未分类
    unclassified = pages_no_name

    # 对每个患者的页面按页码排序，无页码则按pdf_page排序
    groups = []
    for patient_id, patient_pages in patient_map.items():
        patient_pages.sort(
            key=lambda p: extract_page_number(p["lines"]) or p["pdf_page"]
        )
        groups.append({"patient_id": patient_id, "pages": patient_pages})

    return groups, unclassified
