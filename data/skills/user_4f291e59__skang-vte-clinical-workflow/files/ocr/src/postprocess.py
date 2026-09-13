import re

# OCR整词纠错映射（误识别→正确词）
OCR_WORD_CORRECTIONS = {
    # 医学术语
    "医瞩": "医嘱",
    "医嚼": "医嘱",
    "医啊": "医嘱",
    "密置": "留置",
    "捡查": "检查",
    "单核胞": "单核细胞",
    "殖入": "植入",
    "迁曲": "迂曲",
    "遵医瞩": "遵医嘱",
    "馒性": "慢性",
    "静咏": "静脉",
    "国静脉": "腘静脉",
    "胭静脉": "腘静脉",
    "胆静脉": "腘静脉",
    "国动脉": "腘动脉",
    "胭动脉": "腘动脉",
    "国窝": "腘窝",
    "胭窝": "腘窝",
    "径后静脉": "胫后静脉",
    "轻后静脉": "胫后静脉",
    "经后静脉": "胫后静脉",
    "腔后静脉": "胫后静脉",
    "径前静脉": "胫前静脉",
    "轻前静脉": "胫前静脉",
    "经前静脉": "胫前静脉",
    "腔前动脉": "胫前动脉",
    "腔后动脉": "胫后动脉",
    "胚前动脉": "胫前动脉",
    "胚后动脉": "胫后动脉",
    "胚腓干": "胫腓干",
    "径腓干": "胫腓干",
    "轻腓干": "胫腓干",
    "腔排干": "胫腓干",
    "骼总动脉": "髂总动脉",
    "骼内动脉": "髂内动脉",
    "骼外动脉": "髂外动脉",
    "骼动脉": "髂动脉",
    "肌问静脉": "肌间静脉",
    "机间静脉": "肌间静脉",
    "左小肌间静脉": "左小腿肌间静脉",
    "右小肌间静脉": "右小腿肌间静脉",
    "啡骨骨折": "腓骨骨折",
    "口愿": "口服",
    "过最史": "过敏史",
    "休格检查": "体格检查",
    "范圈": "范围",
    "航侵犯": "膀胱侵犯",
    "未子手术": "未予手术",
    "右胸重输液港": "右胸壁输液港",
    "手术整痕": "手术瘢痕",
    "偏摊": "偏瘫",
    "肿服": "肿胀",
    "乎均": "平均",
    "首列腺": "前列腺",
    "水胖": "水肿",
    "无可回性水肿": "可凹性水肿",
    "无明是肿胀": "无明显肿胀",
    "外院趣胸椎退行性变": "外院MR胸椎退行性变",
    "惠者": "患者",
    "利伐沙斑": "利伐沙班",
    "液静脉": "腋静脉",
    "肌酥": "肌酐",
    "感外血管旁": "髂外血管旁",
    "低前神经节": "骶前神经节",
    "驱干部": "躯干部",
    "D二聚体": "D-二聚体",
    "利代沙班": "利伐沙班",
    "艾多沙沙": "艾多沙班",
    "间歇性跋行": "间歇性跛行",
    "跋行距离": "跛行距离",
    "坏痕": "坏疽",
    "大隐静咏": "大隐静脉",
    "小隐静咏": "小隐静脉",
    "骼外静脉": "髂外静脉",
    "骼总静脉": "髂总静脉",
    "骼内静脉": "髂内静脉",
    "骼静脉": "髂静脉",
    "骼血管": "髂血管",
    "外静脉血栓": "髂外静脉血栓",
    "股静脉静脉": "股静脉",
    "血流滞": "血流瘀滞",
    "压追": "压迫",
    "排静脉": "腓静脉",
    "雕静脉": "腓静脉",
    "群静脉": "腓静脉",
    "烧动脉": "桡动脉",
    "右顶术后": "右顶部术后",
    "肺瘤": "肺癌",
    "肺痴": "肺癌",
    "疵痒": "瘙痒",
    "间欧性": "间歇性",
    "短皙": "短暂",
    "闷激酶": "尿激酶",
    "女多沙班": "艾多沙班",
    "骨软骨痫": "骨软骨瘤",
    "瓯诊医师": "就诊医师",
    "焚别": "费别",
    "住别": "性别",
    "姓别": "性别",
    "喘2周": "喘憋2周",
    "责门代谢增高": "贲门代谢增高",
    "腔腓静脉": "胫腓静脉",
    "内课明显": "内踝明显",
    # 常见词
    "精况": "情况",
    "倩况": "情况",
    "自前": "目前",
    # 基本信息字段
    "灿名": "姓名",
    "纳码": "编码",
    # 段落标题（与SECTION_NORMALIZE保持一致）
    "过敛史": "过敏史",
    "过级史": "过敏史",
    "加助检查": "辅助检查",
    "翻助检查": "辅助检查",
    "和助检查": "辅助检查",
    "辑助检查": "辅助检查",
    "轴助检查": "辅助检查",
}

# OCR正则纠错映射（编译后的正则模式→替换文本）
OCR_REGEX_CORRECTIONS = [
    # 化验单数量级、角标和常见单位归一化。Markdown 使用 ^n 保留指数语义。
    (re.compile(r"\*\s*10\s*12\s*/\s*L", re.IGNORECASE), "×10^12/L"),
    (re.compile(r"\*\s*10\s*9\s*/?\s*L?", re.IGNORECASE), "×10^9/L"),
    (re.compile(r"\*\s*10\s*%\s*/\s*L", re.IGNORECASE), "×10^9/L"),
    (re.compile(r"f1\b", re.IGNORECASE), "fL"),
    (re.compile(r"CREA\s*(\d+)\s+(\d+)mo1/L", re.IGNORECASE), r"CREA \1.\2 μmol/L"),
    (re.compile(r"umo1/L", re.IGNORECASE), "μmol/L"),
    (re.compile(r"mg/儿"), "mg/L"),
    (re.compile(r"g/比"), "g/L"),
    # 血管名按有限解剖词典和常用序列校正。
    (re.compile(r"胫腓静脉[、,，]\s*静脉[、,，]\s*腓静脉"), "胫腓静脉、腘静脉、腓静脉"),
    (re.compile(r"胫腓静脉[、,，]\s*静脉[、,，]\s*胫后静脉"), "胫腓静脉、腘静脉、胫后静脉"),
    (re.compile(r"(外院行左)静脉支架植入术"), r"\1髂静脉支架植入术"),
    (re.compile(r"\bR示(?=腰椎)"), "MR示"),
    (re.compile(r"因走路右偏于住院治疗"), "因走路右偏住院治疗"),
    (re.compile(r"伴左下肢轻度肿[。；;]"), "伴左下肢轻度肿胀。"),
    (re.compile(r"左[；;]\s*3\s*侧"), "左侧"),
    (re.compile(r"(\d(?:\.\d+)?)\*(?=\d(?:\.\d+)?(?:\*\d|cm))"), r"\1×"),
    # 将院内检验套餐简称转换成可读标题。
    (re.compile(r"肾1[：:]"), "肾功能："),
    # 脑梗病史漏识别：仅在同句紧邻偏瘫语境时补回，避免把普通“死因”误改。
    (re.compile(r"((?:19|20)\d{2})死(?=[，,]\s*[左右]侧偏瘫)"), r"\1年脑梗死"),
    # 肌酐单位漏识别微摩尔前缀。
    (re.compile(r"(CREA\s*\d+(?:\.\d+)?)\s+mol/L", re.IGNORECASE), r"\1 μmol/L"),
    # 处置意见序号1被识别成字母L。
    (re.compile(r"^L\.(?=交代)"), "1."),
    # 无法组成诊疗语义的页尾OCR残片。
    (re.compile(r"\s+13[.。]牌\s*$"), ""),
    # 下肢动脉按解剖序列纠错，避免把末端腓动脉误改成第二个腘动脉。
    (re.compile(r"(股深动脉[、,，]\s*)胖动脉"), r"\1腘动脉"),
    (re.compile(r"(胫后动脉[、,，]\s*)胖动脉"), r"\1腓动脉"),
    (re.compile(r"(胫腓干[、,，]\s*)前动脉"), r"\1胫前动脉"),
    # 常见检查标题、体征和句间OCR碎片。
    (re.compile(r"(?<!超)彩[：:]"), "彩超："),
    (re.compile(r"Homans症"), "Homans征"),
    (re.compile(r"Honans(?:症|征)"), "Homans征"),
    (re.compile(r"拔出\s*PIC6"), "拔出PICC"),
    (re.compile(r"(利伐沙班\s*\d+(?:\.\d+)?)ng(?=Qd|Bid|bid|qd|\b)"), r"\1mg"),
    (
        re.compile(r"(肌酐\s*CREA\s*\d+(?:\.\d+)?)\s*mo1/L", re.IGNORECASE),
        r"\1 μmol/L",
    ),
    (
        re.compile(r"D-二聚体1[、,]748mg/L，无局部红无拉肢肿胀(?:明显)?"),
        "D-二聚体1.748mg/L，无局部红肿，无上肢明显肿胀",
    ),
    (re.compile(r"。总(?=左侧小腿肌间)"), "。"),
    # 小数点、数字1和cm被混识，例如“最大宽度约1：Ie益”应为“1.1cm”。
    (
        re.compile(r"(最大宽度约\s*)(\d+)\s*[：:]\s*[Il1]\s*[eEcC]\s*(?:益|m)?"),
        r"\1\2.1cm",
    ),
    # 单位中数字1误为字母l
    (re.compile(r"mmo1(?![\dA-Za-z])"), "mmol"),
    # fL单位误识别
    (re.compile(r"1f1"), "fL"),
    # mg误为"邮"
    (re.compile(r"邮/L"), "mg/L"),
    # mg误为"mB"
    (re.compile(r"mB/L"), "mg/L"),
    # g/L缺L（g/后不是L或行末）
    (re.compile(r"g/(?!L)(?=\s|$)"), "g/L"),
    # "否认过史"→"否认过敏史"（过敏史截断）
    (re.compile(r"否认过史"), "否认过敏史"),
    # "过敛情况"→"过敏情况"
    (re.compile(r"过敛情况"), "过敏情况"),
    # "过敛源"→"过敏源"
    (re.compile(r"过敛源"), "过敏源"),
    (re.compile(r"过级情况"), "过敏情况"),
    (re.compile(r"过级史"), "过敏史"),
    (re.compile(r"记\s+录日期"), "记录日期"),
    # "过情况"→"过敏情况"（过敏情况截断）
    (re.compile(r"过情况"), "过敏情况"),
]

# “脑动脉/脑静脉”在神经科文本中是合法词，只有同一行明确出现下肢血管
# 解剖锚点时，才按形近字纠正为“腘动脉/腘静脉”。
LOWER_LIMB_VASCULAR_CONTEXT_PATTERN = re.compile(
    r"(?:下肢|股总动脉|股浅动脉|股深动脉|胫前动脉|胫后动脉|"
    r"股总静脉|股浅静脉|股深静脉|胫后静脉|腓静脉|大隐静脉|小隐静脉)"
)
LOWER_LIMB_CONTEXT_CORRECTIONS = {
    "脑动脉": "腘动脉",
    "脑静脉": "腘静脉",
}

# 置信度阈值
CONFIDENCE_THRESHOLD = 0.5


def apply_ocr_corrections(lines: list[str]) -> list[str]:
    """应用OCR纠错映射，修正已知误识别模式。"""
    result = []
    for line in lines:
        corrected = line
        for wrong, right in OCR_WORD_CORRECTIONS.items():
            corrected = corrected.replace(wrong, right)
        if LOWER_LIMB_VASCULAR_CONTEXT_PATTERN.search(corrected):
            for wrong, right in LOWER_LIMB_CONTEXT_CORRECTIONS.items():
                corrected = corrected.replace(wrong, right)
        for pattern, replacement in OCR_REGEX_CORRECTIONS:
            corrected = pattern.sub(replacement, corrected)
        result.append(corrected)
    return result


def mark_low_confidence_lines(lines_with_conf: list[tuple[str, float]]) -> list[str]:
    """标记低置信度行，返回纯文本行列表。

    低于CONFIDENCE_THRESHOLD的行在末尾标记[低置信]。
    """
    result = []
    for text, conf in lines_with_conf:
        if conf < CONFIDENCE_THRESHOLD:
            result.append(f"{text} [低置信]")
        else:
            result.append(text)
    return result


# 夸克扫描王水印文字
WATERMARK_PATTERNS = [
    r"夸克扫描王",
    r"套克扫描王",  # OCR误识别：夸克扫描王
    r"极速扫描[，,]就是高效",
]

# 需要删除的行内容模式（签名占位符等）
REMOVE_LINE_PATTERNS = [
    re.compile(r"^[（(]签字或盖章有效[）)]$"),
]

# 需要从行内删除的内容模式
INLINE_REMOVE_PATTERNS = [
    re.compile(r"[（(]签字或盖章有效[）)]"),
    re.compile(r"夸克扫描王"),
    re.compile(r"套克扫描王"),
    re.compile(r"费别[：:]?\s*.*?(?=(姓名|性别|年龄|身份|身份证|就诊时间|科别|主诉|现病史|既往史|过敏史|个人史|家族史|体格检查|辅助检查|诊断|处理|处置意见)[：:]?|$)"),
    re.compile(r"医疗保险就诊卡[：:]?\s*.*?(?=(姓名|性别|年龄|身份|身份证|就诊时间|科别|主诉|现病史|既往史|过敏史|个人史|家族史|体格检查|辅助检查|诊断|处理|处置意见)[：:]?|$)"),
    re.compile(r"就诊医师[：:]?\s*.*?(?=(主诉|现病史|既往史|过敏史|个人史|家族史|体格检查|辅助检查|诊断|处理|处置意见)[：:]?|$)"),
    re.compile(r"就诊医生签字[：:]?\s*.*?(?=(主诉|现病史|既往史|过敏史|个人史|家族史|体格检查|辅助检查|诊断|处理|处置意见)[：:]?|$)"),
]

# 页码模式（如"第1/2页"、"第1页"、"第2/共2页"、"共2页"、"/共2页"）
PAGE_NUMBER_PATTERN = re.compile(r"第\d+[/.／共]*\d*页|[/／]?共\d+页")

# 打印时间模式
PRINT_TIME_PATTERN = re.compile(r"打印时间[：:]?\s*\S+.*$")

# 病历页眉和机构页眉。机构名称也属于需要脱敏的信息，因此原始页眉不保留。
HEADER_PATTERN = re.compile(r"^.*(?:医院|门诊部|卫生院|社区卫生服务中心|医疗中心|诊所).*(?:病历|门诊).*$")

# 段落标题关键词（用于分段，按病历中出现的顺序）
# 包含OCR常见误识别变体
SECTION_KEYWORDS = [
    "主诉",
    "现病史",
    "既往史",
    "过敏史",
    "过敛史",  # OCR误识别：过敏史
    "过级史",  # OCR误识别：过敏史
    "个人史",
    "家族史",
    "体格检查",
    "辅助检查",
    "加助检查",  # OCR误识别：辅助检查
    "翻助检查",  # OCR误识别：辅助检查
    "和助检查",  # OCR误识别：辅助检查
    "辑助检查",  # OCR误识别：辅助检查
    "轴助检查",  # OCR误识别：辅助检查
    "诊断",
    "处理",
    "处置意见",
    "就诊医生签字",
]

# 段落标题规范化映射（OCR变体→标准关键词）
SECTION_NORMALIZE = {
    "过敛史": "过敏史",
    "过级史": "过敏史",
    "加助检查": "辅助检查",
    "翻助检查": "辅助检查",
    "和助检查": "辅助检查",
    "辑助检查": "辅助检查",
    "轴助检查": "辅助检查",
}

# 基本信息字段关键词（用于去重：只在开头保留一次）
BASIC_INFO_KEYWORDS = [
    "定点医疗机构",
    "医疗机构",
    "姓名",
    "性别",
    "年龄",
    "身份",
    "身份证",
    "就诊卡",
    "医疗保险就诊卡",
    "医保",
    "就诊时间",
    "科别",
    "打印时间",
    "联系电话",
    "手机号",
    "电话",
    "住址",
    "地址",
    "门诊号",
    "病历号",
    "病案号",
]

# 就诊医师信息需要删除，不保留在脱敏输出中。
DOCTOR_KEYWORDS = ["就诊医师", "就诊医生"]

FEE_KEYWORDS = ["费别", "医疗保险就诊卡", "医保"]

# OCR删除“就诊医师：”标签后，可能留下单个姓名碎片。
DOCTOR_NAME_RESIDUE_PATTERN = re.compile(r"^\s*(?:余康|佘康|全康|余律|康|涛)\s*|\s*(?:余康|佘康|全康|余律|康|涛)$")

# 日期模式（用于辅助检查等段落内按日期分小段）
# 要求日期前面是句末标点（。；：）、空格、或行首，避免在词中间误拆
DATE_PATTERN = re.compile(r"(?:^|(?<=[。；：:;\s]))(\d{4}\s*-\s*\d{1,2}\s*-\s*\d{1,2})(?!\d)")

# 检查项目标题模式（如"全血细胞分析:"、"D-二聚体定量："）
# 特征：以冒号结尾，前面是中文或字母数字，且不是基本信息字段
EXAM_TITLE_PATTERN = re.compile(r"(?:^|(?<=[。；，,\s]))([一-龥A-Za-z0-9\-\+·]+(?:分析|检查|定量|测定|检测|筛查|试验|培养|涂片|计数|扫描|造影|超声|病理|活检)[：:])")

INLINE_SECTION_PATTERN = re.compile(
    r"(?=(主诉|现病史|既往史|过敏史|个人史|家族史|体格检查|辅助检查|诊断|处理|处置意见)[：:])"
)

# 病史类段落中的日期常是病程、手术时间或过敏记录日期，不应按辅助检查逻辑拆段。
NO_DATE_SPLIT_PREFIXES = [
    "主诉",
    "现病史",
    "既往史",
    "过敏史",
    "个人史",
    "家族史",
    "体格检查",
    "诊断",
    "处理",
    "处置意见",
]

SYSTEM_DISPOSITION_MARKERS = [
    "药品：",
    "检查：",
    "检验：",
    "治疗：",
]


def remove_watermarks(lines: list[str]) -> list[str]:
    """删除水印文字行。"""
    result = []
    for line in lines:
        is_watermark = False
        for pattern in WATERMARK_PATTERNS:
            if re.search(pattern, line):
                is_watermark = True
                break
        if not is_watermark:
            result.append(line)
    return result


def remove_junk_lines(lines: list[str]) -> list[str]:
    """删除签名占位符等无意义行，并清理行内垃圾内容。"""
    result = []
    for line in lines:
        stripped = line.strip()
        # 整行匹配则跳过
        skip = False
        for pattern in REMOVE_LINE_PATTERNS:
            if pattern.search(stripped):
                skip = True
                break
        if skip:
            continue
        # 行内清理
        cleaned = stripped
        for pattern in INLINE_REMOVE_PATTERNS:
            cleaned = pattern.sub("", cleaned).strip()
        if cleaned:
            result.append(cleaned)
    return result


def remove_fee_and_doctor_info(lines: list[str]) -> list[str]:
    """删除费别/医保就诊卡和就诊医师信息。"""
    result = []
    for line in lines:
        cleaned = line.strip()
        for pattern in INLINE_REMOVE_PATTERNS:
            cleaned = pattern.sub("", cleaned).strip()
        if not cleaned:
            continue
        if any(keyword in cleaned for keyword in FEE_KEYWORDS + DOCTOR_KEYWORDS):
            # 如果整行只剩敏感字段或医生签名字段，直接丢弃；否则保守清理残余标签。
            for keyword in FEE_KEYWORDS + DOCTOR_KEYWORDS:
                cleaned = re.sub(rf"{keyword}[：:]?\s*\S*", "", cleaned).strip()
        cleaned = remove_doctor_name_residue(cleaned)
        if cleaned:
            result.append(cleaned)
    return result


def remove_doctor_name_residue(line: str) -> str:
    """删除已知就诊医师姓名残片。"""
    return DOCTOR_NAME_RESIDUE_PATTERN.sub("", line).strip()


def deduplicate_headers(pages_lines: list[list[str]]) -> list[list[str]]:
    """删除病历页眉行。"""
    if not pages_lines:
        return pages_lines

    result = []
    for page_lines in pages_lines:
        filtered = []
        for line in page_lines:
            if HEADER_PATTERN.search(line.strip()):
                continue
            filtered.append(line)
        result.append(filtered)

    return result


def remove_page_numbers(lines: list[str]) -> list[str]:
    """删除页码文字（如'第1/2页'、'共2页'）。"""
    result = []
    for line in lines:
        cleaned = PAGE_NUMBER_PATTERN.sub("", line).strip()
        if cleaned:
            result.append(cleaned)
    return result


def extract_print_times(lines: list[str]) -> list[tuple[int, str]]:
    """提取所有打印时间及其所在行索引。"""
    times = []
    for i, line in enumerate(lines):
        match = re.search(r"打印时间[：:]?\s*(.+)", line)
        if match:
            times.append((i, match.group(1).strip()))
    return times


def remove_print_times(lines: list[str]) -> list[str]:
    """删除打印时间。打印时间属于页面元数据，不保留在脱敏病历中。"""
    result = []
    for line in lines:
        cleaned = PRINT_TIME_PATTERN.sub("", line).strip()
        if cleaned:
            result.append(cleaned)
    return result


def is_basic_info_line(line: str) -> bool:
    """判断一行是否是基本信息字段。"""
    for keyword in BASIC_INFO_KEYWORDS:
        if re.search(rf"{keyword}[：:]?", line):
            return True
    return False


def is_doctor_line(line: str) -> bool:
    """判断一行是否包含就诊医师信息。"""
    for keyword in DOCTOR_KEYWORDS:
        if keyword in line:
            return True
    return False


def is_fee_line(line: str) -> bool:
    """判断一行是否包含费别/医保就诊卡信息。"""
    return any(keyword in line for keyword in FEE_KEYWORDS)


def deduplicate_basic_info(pages_lines: list[list[str]]) -> list[list[str]]:
    """基本信息去重：每页都有相同的基本信息字段，只在第一页保留。

    后续页中，如果某行包含与第一页相同的基本信息关键词，则删除该行。

    Args:
        pages_lines: 每页的文本行列表

    Returns:
        处理后的每页文本行列表
    """
    if not pages_lines:
        return pages_lines

    # 从第一页提取基本信息关键词
    first_page_keywords = set()
    for line in pages_lines[0]:
        for keyword in BASIC_INFO_KEYWORDS:
            if re.search(rf"{keyword}[：:]?", line):
                first_page_keywords.add(keyword)

    # 从后续页中删除包含这些关键词的行，以及紧跟其后的时间碎片行
    TIME_FRAGMENT_PATTERN = re.compile(r"^\d{1,2}:\d{2}$")
    result = [pages_lines[0]]
    for page_lines in pages_lines[1:]:
        filtered = []
        skip_next = False
        for i, line in enumerate(page_lines):
            if skip_next:
                skip_next = False
                continue
            should_remove = False
            for keyword in first_page_keywords:
                if re.search(rf"{keyword}[：:]?", line):
                    should_remove = True
                    break
            if should_remove:
                # 如果下一行是时间碎片（如"09:02"），也一并删除
                if i + 1 < len(page_lines) and TIME_FRAGMENT_PATTERN.match(page_lines[i + 1].strip()):
                    skip_next = True
                continue
            filtered.append(line)
        result.append(filtered)

    return result


def deduplicate_basic_info_lines(lines: list[str]) -> list[str]:
    """合并后再次去重基本信息，处理单张图片内多次识别到页眉信息的情况。"""
    seen_keywords = set()
    result = []

    for line in lines:
        if is_fee_line(line) or is_doctor_line(line):
            continue

        matched_keyword = None
        for keyword in BASIC_INFO_KEYWORDS:
            if re.search(rf"{keyword}[：:]?", line):
                matched_keyword = keyword
                break

        if matched_keyword:
            if matched_keyword in seen_keywords:
                continue
            seen_keywords.add(matched_keyword)

        result.append(line)

    return result


def extract_and_move_doctor_info(lines: list[str]) -> list[str]:
    """删除就诊医师信息。"""
    return [line for line in lines if not is_doctor_line(line)]


def segment_by_sections(lines: list[str]) -> list[str]:
    """按段落标题关键词分段。

    每遇到一个段落标题关键词开头的行，就开始新段落。
    段落标题包括：主诉、现病史、个人史、家族史、体格检查、
    辅助检查、诊断、处理、处置意见、就诊医生签字。

    非段落标题的连续行合并到当前段落中。
    """
    if not lines:
        return []

    paragraphs = []
    current_title = None
    current_content = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        for stripped in split_inline_sections(stripped):
            if not stripped:
                continue

            # 检查是否是段落标题行
            matched_section = None
            for keyword in SECTION_KEYWORDS:
                if stripped.startswith(keyword):
                    matched_section = keyword
                    break

            if matched_section:
                # 保存上一个段落
                if current_title is not None or current_content:
                    para_text = " ".join(current_content)
                    if para_text:
                        paragraphs.append(para_text)
                # 开始新段落（规范化OCR变体）
                normalized = SECTION_NORMALIZE.get(matched_section, matched_section)
                current_title = matched_section
                current_content = [normalized + stripped[len(matched_section):]]
            else:
                # 基本信息行：单独成段
                if is_basic_info_line(stripped):
                    if current_content:
                        para_text = " ".join(current_content)
                        if para_text:
                            paragraphs.append(para_text)
                        current_title = None
                        current_content = []
                    paragraphs.append(stripped)
                else:
                    # 普通行：追加到当前段落
                    current_content.append(stripped)

    # 保存最后一个段落
    if current_content:
        para_text = " ".join(current_content)
        if para_text:
            paragraphs.append(para_text)

    return paragraphs


def split_inline_sections(line: str) -> list[str]:
    """把同一OCR行里挤在一起的多个段落标题拆开。"""
    starts = [match.start() for match in INLINE_SECTION_PATTERN.finditer(line)]
    starts = sorted(set(starts))
    if not starts or starts == [0]:
        return [line]
    if starts[0] != 0:
        starts.insert(0, 0)
    parts = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(line)
        part = line[start:end].strip()
        if part:
            parts.append(part)
    return parts


def split_by_dates(paragraphs: list[str]) -> list[str]:
    """对包含日期的段落按日期和检查项目标题拆分为多个小段。

    辅助检查等段落中常包含多个日期开头的检查报告，
    按日期和检查项目标题拆分使每个检查报告独立成段。
    只在日期前面是句末标点或空格时拆分，避免在词中间误拆。
    检查项目标题（如"全血细胞分析:"）只有不在日期紧邻之后时才作为拆分点。
    只在段落中有2个及以上拆分点时才拆分。
    """
    result = []
    for para in paragraphs:
        if _is_no_date_split_paragraph(para):
            result.append(normalize_paragraph_text(para))
            continue

        # 收集日期拆分点
        date_points = set()
        for m in DATE_PATTERN.finditer(para):
            date_points.add(m.start())

        # 收集检查项目标题拆分点（排除紧跟日期后的）
        exam_points = set()
        for m in EXAM_TITLE_PATTERN.finditer(para):
            # 如果此位置紧邻前一个日期（日期结尾到标题开头<=2字符），不作为拆分点
            is_after_date = False
            for dp in date_points:
                # 日期大约10-14字符长
                if dp < m.start() <= dp + 15:
                    is_after_date = True
                    break
            if not is_after_date:
                exam_points.add(m.start())

        split_points = sorted(date_points | exam_points)

        if len(split_points) < 2:
            result.append(normalize_paragraph_text(para))
            continue

        # 第一个拆分点之前的内容作为首段（如果非空）
        first_pos = split_points[0]
        if first_pos > 0:
            prefix = para[:first_pos].strip()
            if prefix:
                result.append(normalize_paragraph_text(prefix))

        # 每个拆分点到下一个拆分点之前的内容作为一段
        for i, start in enumerate(split_points):
            end = split_points[i + 1] if i + 1 < len(split_points) else len(para)
            segment = para[start:end].strip()
            if segment:
                result.append(normalize_paragraph_text(segment))

    return result


def resolve_disposition_conflicts(paragraphs: list[str]) -> list[str]:
    """处置意见优先于系统处置/处理。

    门诊病历中“处理”常为开药系统自动复制记录；“处置意见”是医生手写或特别交代。
    当两者同时存在时，保留处置意见，删除形如“处理：药品/检查/检验...”的系统记录，
    避免系统开药剂量与医生实际嘱咐冲突。
    """
    has_doctor_disposition = any(_has_nonempty_doctor_disposition(p) for p in paragraphs)
    if not has_doctor_disposition:
        return paragraphs

    result = []
    for paragraph in paragraphs:
        stripped = paragraph.lstrip()
        if stripped.startswith(("处理：", "处理:")) and any(
            marker in stripped for marker in SYSTEM_DISPOSITION_MARKERS
        ):
            continue
        result.append(paragraph)
    return result


def _has_nonempty_doctor_disposition(paragraph: str) -> bool:
    stripped = paragraph.lstrip()
    if not stripped.startswith(("处置意见：", "处置意见:")):
        return False
    content = re.sub(r"^处置意见[：:]\s*", "", stripped).strip()
    return bool(content)


def normalize_paragraph_text(paragraph: str) -> str:
    """段落级纠错，处理行合并后才出现的OCR碎片。"""
    paragraph = re.sub(r"记\s+录日期", "记录日期", paragraph)
    return remove_doctor_name_residue(paragraph)


def _is_no_date_split_paragraph(paragraph: str) -> bool:
    """判断段落是否不应按日期拆分。"""
    stripped = paragraph.lstrip()
    return any(stripped.startswith(prefix) for prefix in NO_DATE_SPLIT_PREFIXES)


def postprocess_patient(pages_lines: list[list[str]]) -> list[str]:
    """对一个患者的所有页面进行后处理。

    处理顺序：
    1. 删除水印
    2. 删除页码
    3. 删除签名占位符等垃圾行
    4. 删除后续页重复的病历页眉
    5. 基本信息去重
    6. 合并所有页面
    7. 删除打印时间、费别、就诊医师并再次去重基本信息
    8. 删除就诊医师信息
    9. 按段落标题分段

    Args:
        pages_lines: 每页的文本行列表

    Returns:
        后处理后的段落列表
    """
    # 0. 应用OCR纠错映射
    processed_pages = [apply_ocr_corrections(page) for page in pages_lines]

    # 1. 删除水印
    processed_pages = [remove_watermarks(page) for page in processed_pages]

    # 2. 删除页码
    processed_pages = [remove_page_numbers(page) for page in processed_pages]

    # 3. 删除签名占位符等垃圾行
    processed_pages = [remove_junk_lines(page) for page in processed_pages]

    # 4. 删除后续页重复的病历页眉
    processed_pages = deduplicate_headers(processed_pages)

    # 5. 基本信息去重
    processed_pages = deduplicate_basic_info(processed_pages)

    # 6. 合并所有页面
    all_lines = []
    for page_lines in processed_pages:
        all_lines.extend(page_lines)

    # 7. 删除打印时间并再次去重基本信息
    all_lines = remove_print_times(all_lines)
    all_lines = remove_fee_and_doctor_info(all_lines)
    all_lines = deduplicate_basic_info_lines(all_lines)

    # 8. 删除就诊医师信息
    all_lines = extract_and_move_doctor_info(all_lines)

    # 9. 按段落标题分段
    paragraphs = segment_by_sections(all_lines)

    # 10. 按日期拆分段落（辅助检查等段落内按日期分小段）
    paragraphs = split_by_dates(paragraphs)

    # 11. 若医生处置意见与系统处置并存，以处置意见为准
    paragraphs = resolve_disposition_conflicts(paragraphs)

    return paragraphs
