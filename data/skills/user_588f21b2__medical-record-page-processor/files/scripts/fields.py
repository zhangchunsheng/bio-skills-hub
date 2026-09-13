# -*- coding: utf-8 -*-
"""字段字典与自动识别。

本模块是「病案首页数据处理器」的领域核心：内置住院病案首页标准字段表
（参考国家卫健委 2011/2016 版住院病案首页及医保结算清单字段口径），
配合别名库把各 HIS / 病案系统千奇百怪的列名映射到统一标准名。

设计要点：
1. 各医院导出的列名差异极大（"出院科室 " 带尾随空格、"病案号码" vs "住院号"），
   因此匹配走「规范化后精确匹配 -> 长别名包含匹配」两级，再落到关键词启发式分类。
2. 每个映射带置信度（high/medium/low），low 的会进报告让用户人工确认。
3. 隐私字段（姓名、身份证、住址、电话等）单独打标，默认不进入任何输出。
"""

from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------------------
# 字段规格表
# dtype: id / date / datetime / code / category / number / text
# privacy: True 表示直接标识符，默认剔除
# required: True 表示质控必填
# ---------------------------------------------------------------------------
FIELD_SPECS: list[dict] = [
    # ---------------- 标识 ----------------
    {"name": "病案号", "category": "标识", "dtype": "id", "required": True,
     "aliases": ["病案号", "病案号码", "住院号", "住院号码", "病历号", "病历号码",
                 "病案流水号", "住院流水号", "就诊号", "就诊流水号", "档案号", "mrn",
                 "病案号 ", "住院登记号", "住院病历号"]},
    {"name": "住院次数", "category": "标识", "dtype": "number",
     "aliases": ["住院次数", "第几次住院", "本次住院次数", "住院次", "住院序号"]},
    {"name": "研究ID", "category": "标识", "dtype": "id",
     "aliases": ["研究id", "研究编号", "患者id", "patient_id", "pid", "hash_id",
                 "匿名id", "去标识id", "subject_id", "研究号"]},
    {"name": "医疗机构名称", "category": "标识", "dtype": "text",
     "aliases": ["医疗机构名称", "医院名称", "医疗机构", "单位名称", "院区"]},
    {"name": "组织机构代码", "category": "标识", "dtype": "text",
     "aliases": ["组织机构代码", "机构代码", "医院代码"]},

    # ---------------- 隐私（直接标识符） ----------------
    {"name": "姓名", "category": "隐私", "dtype": "text", "privacy": True,
     "aliases": ["姓名", "患者姓名", "病人姓名", "患者名字", "name"]},
    {"name": "身份证号", "category": "隐私", "dtype": "text", "privacy": True,
     "aliases": ["身份证号", "身份证号码", "身份证件号", "证件号码", "身份证", "idcard",
                 "市民卡号", "社会保障卡号", "医保卡号"]},
    {"name": "联系电话", "category": "隐私", "dtype": "text", "privacy": True,
     "aliases": ["联系电话", "电话", "电话号码", "手机号", "手机号码", "患者电话",
                 "联系号码", "tel", "phone"]},
    {"name": "现住址", "category": "隐私", "dtype": "text", "privacy": True,
     "aliases": ["现住址", "住址", "家庭住址", "户籍地址", "联系地址", "户口地址"]},
    {"name": "工作单位", "category": "隐私", "dtype": "text", "privacy": True,
     "aliases": ["工作单位", "单位名称", "工作单位及地址", "职业单位"]},
    {"name": "联系人姓名", "category": "隐私", "dtype": "text", "privacy": True,
     "aliases": ["联系人姓名", "联系人", "家属姓名", "亲属姓名", "监护人姓名"]},
    {"name": "联系人电话", "category": "隐私", "dtype": "text", "privacy": True,
     "aliases": ["联系人电话", "家属电话", "亲属电话", "监护人电话"]},

    # ---------------- 人口学 ----------------
    {"name": "性别", "category": "人口学", "dtype": "category", "required": True,
     "aliases": ["性别", "患者性别", "病人性别", "sex", "gender"]},
    {"name": "出生日期", "category": "人口学", "dtype": "date",
     "aliases": ["出生日期", "出生年月日", "出生年月", "出生日", "生日", "birth_date",
                 "birthday", "dob"]},
    {"name": "年龄", "category": "人口学", "dtype": "number", "required": True,
     "aliases": ["年龄", "患者年龄", "病人年龄", "age"]},
    {"name": "年龄单位", "category": "人口学", "dtype": "category",
     "aliases": ["年龄单位", "年龄类型", "年龄计算单位"]},
    {"name": "新生儿出生体重", "category": "人口学", "dtype": "number",
     "aliases": ["新生儿出生体重", "出生体重", "新生儿体重"]},
    {"name": "民族", "category": "人口学", "dtype": "category", "aliases": ["民族"]},
    {"name": "国籍", "category": "人口学", "dtype": "category", "aliases": ["国籍", "国家"]},
    {"name": "职业", "category": "人口学", "dtype": "category", "aliases": ["职业", "职业类别"]},
    {"name": "婚姻状况", "category": "人口学", "dtype": "category",
     "aliases": ["婚姻状况", "婚姻状态", "婚姻"]},
    {"name": "医疗付费方式", "category": "人口学", "dtype": "category",
     "aliases": ["医疗付费方式", "付费方式", "结算方式", "支付方式", "医保类型",
                 "费别", "医疗费用支付方式", "参保类型", "医保身份"]},
    {"name": "医保支付金额", "category": "费用", "dtype": "number",
     "aliases": ["医保支付金额", "基金支付金额", "统筹支付金额", "医保统筹支付"]},

    # ---------------- 住院过程 ----------------
    {"name": "入院日期", "category": "住院", "dtype": "datetime", "required": True,
     "aliases": ["入院日期", "入院时间", "入院日期时间", "入院日", "admission_date",
                 "入科时间", "入院年月日"]},
    {"name": "入院科别", "category": "住院", "dtype": "category",
     "aliases": ["入院科别", "入院科室", "入院科", "入科科室", "admission_dept"]},
    {"name": "出院日期", "category": "住院", "dtype": "datetime", "required": True,
     "aliases": ["出院日期", "出院时间", "出院日期时间", "出院日", "discharge_date",
                 "离院时间", "出院年月日"]},
    {"name": "出院科别", "category": "住院", "dtype": "category",
     "aliases": ["出院科别", "出院科室", "出院科", "科室", "dept", "discharge_dept",
                 "出院科室名称"]},
    {"name": "实际住院天数", "category": "住院", "dtype": "number",
     "aliases": ["实际住院天数", "住院天数", "住院日", "los", "住院时长", "住院总天数"]},
    {"name": "转科科别", "category": "住院", "dtype": "category",
     "aliases": ["转科科别", "转科科室", "转科"]},
    {"name": "病房", "category": "住院", "dtype": "text", "aliases": ["病房", "病区", "病室"]},
    {"name": "门急诊诊断", "category": "诊断", "dtype": "text",
     "aliases": ["门急诊诊断", "门诊诊断", "急诊诊断", "门急诊诊断名称"]},
    {"name": "入院诊断", "category": "诊断", "dtype": "text", "aliases": ["入院诊断", "入院诊断名称"]},
    {"name": "入院病情", "category": "诊断", "dtype": "category",
     "aliases": ["入院病情", "入院时病情", "入院情况"]},

    # ---------------- 诊断 ----------------
    {"name": "主要诊断名称", "category": "诊断", "dtype": "text", "required": True,
     "aliases": ["出院主要诊断", "主要诊断", "主要诊断名称", "出院诊断", "主诊断",
                 "主要诊断（出院）", "出院主要诊断名称", "主诊断名称"]},
    {"name": "主要诊断编码", "category": "诊断", "dtype": "code", "required": True,
     "aliases": ["主要诊断编码", "主诊断编码", "出院主要诊断编码", "主要诊断icd编码",
                 "疾病编码", "主要诊断icd", "出院主要诊断疾病编码", "主诊断icd编码"]},
    {"name": "其他诊断名称", "category": "诊断", "dtype": "text",
     "aliases": ["其他诊断", "其他诊断名称", "次要诊断", "其他诊断1"]},
    {"name": "其他诊断编码", "category": "诊断", "dtype": "text",
     "aliases": ["其他诊断编码", "其他诊断1编码", "次要诊断编码"]},
    {"name": "病理诊断名称", "category": "诊断", "dtype": "text",
     "aliases": ["病理诊断", "病理诊断名称", "病理结果"]},
    {"name": "病理诊断编码", "category": "诊断", "dtype": "text",
     "aliases": ["病理诊断编码", "病理编码"]},
    {"name": "病理号", "category": "诊断", "dtype": "text", "aliases": ["病理号"]},

    # ---------------- 手术操作 ----------------
    {"name": "手术操作名称", "category": "手术", "dtype": "text",
     "aliases": ["手术及操作", "手术操作名称", "手术名称", "主要手术", "手术",
                 "手术及操作名称", "手术操作"]},
    {"name": "手术操作编码", "category": "手术", "dtype": "code",
     "aliases": ["手术编码", "手术操作编码", "手术及操作编码", "icd-9-cm-3",
                 "手术操作代码", "手术代码"]},
    {"name": "手术日期", "category": "手术", "dtype": "date",
     "aliases": ["手术日期", "手术时间", "手术开始时间"]},
    {"name": "手术级别", "category": "手术", "dtype": "category",
     "aliases": ["手术级别", "手术分级", "手术等级"]},
    {"name": "麻醉方式", "category": "手术", "dtype": "category",
     "aliases": ["麻醉方式", "麻醉方法", "麻醉"]},
    {"name": "切口愈合等级", "category": "手术", "dtype": "category",
     "aliases": ["切口愈合等级", "愈合等级", "切口等级"]},
    {"name": "是否手术", "category": "手术", "dtype": "category",
     "aliases": ["是否手术", "手术标志", "有无手术"]},

    # ---------------- 费用 ----------------
    {"name": "总费用", "category": "费用", "dtype": "number", "required": True,
     "aliases": ["总费用", "住院总费用", "医疗总费用", "费用总额", "总金额",
                 "住院费用总额", "费用合计", "合计费用"]},
    {"name": "自付金额", "category": "费用", "dtype": "number",
     "aliases": ["自付金额", "个人自付", "个人支付金额", "自费金额"]},
    {"name": "综合医疗服务费", "category": "费用", "dtype": "number",
     "aliases": ["综合医疗服务类", "综合医疗服务费", "综合医疗服务费用"]},
    {"name": "一般医疗服务费", "category": "费用", "dtype": "number",
     "aliases": ["一般医疗服务费", "一般医疗服务费用"]},
    {"name": "一般治疗操作费", "category": "费用", "dtype": "number",
     "aliases": ["一般治疗操作费", "一般治疗操作费用"]},
    {"name": "护理费", "category": "费用", "dtype": "number",
     "aliases": ["护理费", "护理费用", "护理类"]},
    {"name": "病理诊断费", "category": "费用", "dtype": "number",
     "aliases": ["病理诊断费", "病理费", "病理诊断费用"]},
    {"name": "实验室诊断费", "category": "费用", "dtype": "number",
     "aliases": ["实验室诊断费", "化验费", "检验费", "实验室诊断费用"]},
    {"name": "影像学诊断费", "category": "费用", "dtype": "number",
     "aliases": ["影像学诊断费", "影像费", "影像学检查费", "影像诊断费"]},
    {"name": "临床诊断项目费", "category": "费用", "dtype": "number",
     "aliases": ["临床诊断项目费", "临床诊断费"]},
    {"name": "非手术治疗项目费", "category": "费用", "dtype": "number",
     "aliases": ["非手术治疗项目费", "非手术治疗费", "治疗费", "治疗费用"]},
    {"name": "手术治疗费", "category": "费用", "dtype": "number",
     "aliases": ["手术治疗费", "手术费", "手术治疗费用"]},
    {"name": "康复费", "category": "费用", "dtype": "number", "aliases": ["康复费", "康复费用"]},
    {"name": "中医治疗费", "category": "费用", "dtype": "number",
     "aliases": ["中医治疗费", "中医类", "中医费用"]},
    {"name": "西药费", "category": "费用", "dtype": "number",
     "aliases": ["西药费", "西药费用", "药品费", "药费", "药品费用"]},
    {"name": "中药费", "category": "费用", "dtype": "number",
     "aliases": ["中药费", "中成药费", "中草药费", "中药饮片费"]},
    {"name": "血液制品费", "category": "费用", "dtype": "number",
     "aliases": ["血液和血液制品费", "血液制品费", "输血费", "血液费"]},
    {"name": "白蛋白类制品费", "category": "费用", "dtype": "number",
     "aliases": ["白蛋白类制品费", "白蛋白费"]},
    {"name": "球蛋白类制品费", "category": "费用", "dtype": "number",
     "aliases": ["球蛋白类制品费", "球蛋白费"]},
    {"name": "凝血因子类制品费", "category": "费用", "dtype": "number",
     "aliases": ["凝血因子类制品费", "凝血因子费"]},
    {"name": "细胞因子类制品费", "category": "费用", "dtype": "number",
     "aliases": ["细胞因子类制品费", "细胞因子费"]},
    {"name": "检查用一次性材料费", "category": "费用", "dtype": "number",
     "aliases": ["检查用一次性医用材料费", "检查用材料费"]},
    {"name": "治疗用一次性材料费", "category": "费用", "dtype": "number",
     "aliases": ["治疗用一次性医用材料费", "治疗用材料费"]},
    {"name": "手术用一次性材料费", "category": "费用", "dtype": "number",
     "aliases": ["手术用一次性医用材料费", "手术用材料费"]},
    {"name": "耗材费", "category": "费用", "dtype": "number",
     "aliases": ["卫生材料费", "耗材费", "材料费", "医用材料费", "一次性材料费"]},
    {"name": "其他费", "category": "费用", "dtype": "number", "aliases": ["其他费", "其他费用"]},

    # ---------------- 结局与转归 ----------------
    {"name": "离院方式", "category": "结局", "dtype": "category", "required": True,
     "aliases": ["离院方式", "出院方式", "转归", "离院情况", "出院情况"]},
    {"name": "31日再住院计划", "category": "结局", "dtype": "category",
     "aliases": ["是否有出院31日内再住院计划", "31日内再住院计划", "31天再住院计划",
                 "再住院计划"]},
    {"name": "抢救次数", "category": "结局", "dtype": "number",
     "aliases": ["抢救次数", "抢救总次数"]},
    {"name": "抢救成功次数", "category": "结局", "dtype": "number",
     "aliases": ["抢救成功次数", "抢救成功例数"]},
    {"name": "颅脑损伤昏迷时间", "category": "结局", "dtype": "number",
     "aliases": ["颅脑损伤患者昏迷时间", "昏迷时间", "昏迷时长"]},

    # ---------------- DRG / 绩效 ----------------
    {"name": "DRG名称", "category": "DRG", "dtype": "category",
     "aliases": ["drg", "drg组", "drg名称", "drg分组", "drg组名称", "病种组合名称"]},
    {"name": "DRG代码", "category": "DRG", "dtype": "code",
     "aliases": ["drg代码", "drg编码", "drg组代码", "drg组编码"]},
    {"name": "DRG权重", "category": "DRG", "dtype": "number",
     "aliases": ["rw", "权重", "相对权重", "drg权重", "cmi权重"]},
    {"name": "CMI", "category": "DRG", "dtype": "number",
     "aliases": ["cmi", "病例组合指数"]},
    {"name": "数据来源文件", "category": "元数据", "dtype": "text",
     "aliases": ["source_file", "数据来源文件", "来源文件"]},
]

CANON_SPEC: dict[str, dict] = {s["name"]: s for s in FIELD_SPECS}

# 全部别名 -> 标准名（规范化后）
ALIAS2CANON: dict[str, str] = {}
STRICT_ALIASES: set[str] = set()  # 只允许精确匹配的短别名
for _spec in FIELD_SPECS:
    for _a in [_spec["name"]] + list(_spec.get("aliases", [])):
        key = re.sub(r"[\s_\-（）()\[\]【】/\\]", "", str(_a)).lower()
        ALIAS2CANON.setdefault(key, _spec["name"])
        if len(key) <= 3:
            STRICT_ALIASES.add(key)

# 关键词启发式：未识别列按此猜类型（不猜具体字段名，只猜语义类别）
KEYWORD_CLASSES: list[tuple[str, str]] = [
    ("费", "费用"), ("金额", "费用"), ("成本", "费用"),
    ("日期", "日期"), ("时间", "日期"),
    ("编码", "编码"), ("代码", "编码"), ("icd", "编码"),
    ("天数", "数值"), ("次数", "数值"), ("数量", "数值"),
    ("科室", "分类"), ("科别", "分类"), ("病区", "分类"),
]

# 值的规范化映射
VALUE_MAPS: dict[str, dict[str, str]] = {
    "性别": {"1": "男", "2": "女", "m": "男", "f": "女", "male": "男", "female": "女",
             "男": "男", "女": "女", "未知": "未知", "9": "未知", "0": "未知"},
    "离院方式": {"1": "医嘱离院", "2": "医嘱转院", "3": "医嘱转社区",
                 "4": "非医嘱离院", "5": "死亡", "9": "其他",
                 "医嘱离院": "医嘱离院", "医嘱转院": "医嘱转院", "医嘱转社区": "医嘱转社区",
                 "非医嘱离院": "非医嘱离院", "死亡": "死亡", "其他": "其他",
                 "转院": "医嘱转院", "自动出院": "非医嘱离院"},
    "入院病情": {"1": "有", "2": "临床未确定", "3": "情况不明", "4": "无",
                 "有": "有", "临床未确定": "临床未确定", "情况不明": "情况不明", "无": "无"},
    "31日再住院计划": {"1": "有", "2": "无", "有": "有", "无": "无"},
    "是否手术": {"1": "是", "2": "否", "是": "是", "否": "否", "y": "是", "n": "否",
                 "有": "是", "无": "否"},
    "年龄单位": {"岁": "岁", "月": "月", "天": "天", "年": "岁", "岁(月)": "岁"},
}


def norm_key(text: object) -> str:
    """列名/值规范化：全角转半角、去空白与常见标点、转小写。"""
    if text is None:
        return ""
    s = unicodedata.normalize("NFKC", str(text))
    s = re.sub(r"[\s_\-（）()\[\]【】/\\:：,，.。]", "", s)
    return s.strip().lower()


def guess_class(col: object) -> str:
    """未识别列的语义类别猜测。"""
    key = str(col).lower()
    for kw, cls in KEYWORD_CLASSES:
        if kw in key:
            return cls
    return "未知"


def match_columns(columns) -> dict:
    """把原始列名映射到标准字段名。

    返回 dict：
      mapping      {原始列名: 标准字段名}
      confidence   {原始列名: high|medium|low}
      unmapped     [原始列名]
      duplicates   {标准字段名: [被挤掉的原始列名]}
    """
    mapping: dict[str, str] = {}
    confidence: dict[str, str] = {}
    used: dict[str, str] = {}
    duplicates: dict[str, list[str]] = {}

    # 第一轮：规范化精确匹配
    for col in columns:
        key = norm_key(col)
        if not key:
            continue
        canon = ALIAS2CANON.get(key)
        if canon:
            _assign(mapping, confidence, used, duplicates, col, canon, "high")

    # 第二轮：长别名包含匹配（别名长度 >= 4 才允许，避免「科室」这类泛词误命中）
    candidates = [c for c in columns if c not in mapping]
    for col in candidates:
        key = norm_key(col)
        if not key:
            continue
        best_alias, best_canon = "", None
        for alias, canon in ALIAS2CANON.items():
            if len(alias) < 4 or alias in STRICT_ALIASES:
                continue
            if alias in key or key in alias:
                if len(alias) > len(best_alias):
                    best_alias, best_canon = alias, canon
        if best_canon:
            _assign(mapping, confidence, used, duplicates, col, best_canon, "medium")

    unmapped = [c for c in columns if c not in mapping]
    return {"mapping": mapping, "confidence": confidence,
            "unmapped": unmapped, "duplicates": duplicates}


def _assign(mapping, confidence, used, duplicates, col, canon, level) -> None:
    if canon in used:
        duplicates.setdefault(canon, []).append(col)
        return
    mapping[col] = canon
    confidence[col] = level
    used[canon] = col


# 派生指标字段（由 scripts/indicators.py 计算生成，不参与原始列匹配）
DERIVED_FIELDS = [
    "住院天数_计算", "年龄_计算", "年龄段", "年份", "季度", "月份", "年月",
    "有无手术", "手术级别_标准化", "是否死亡", "是否非医嘱离院", "是否抢救",
    "是否抢救成功", "是否三四级手术", "药占比", "耗占比", "西药中药费合计",
    "材料费合计", "检查检验费合计", "治疗手术费合计", "日均费用", "费用分项合计",
    "费用分项偏差率", "是否31天再入院",
]
