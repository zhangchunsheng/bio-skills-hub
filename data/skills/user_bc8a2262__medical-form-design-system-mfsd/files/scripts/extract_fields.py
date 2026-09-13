#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医疗文档信息提取与字段推断辅助脚本
用于 STEP2-3：从文本中识别字段候选、关键词和表单目录信息
用法：python extract_fields.py <document.txt> [--btype CLN|MGT|RES]
"""

import re
import sys
import argparse
import json
from collections import Counter


# ─────────────────────────────────────────────────────────────
# 医学常用停用词
# ─────────────────────────────────────────────────────────────
STOP_WORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "那", "但", "与", "及", "或", "并",
    "以", "为", "由", "其", "对", "等", "该", "本", "各", "可", "应",
    "时", "后", "前", "中", "内", "外", "如", "当", "于", "至", "按",
    "进行", "情况", "相关", "必须", "需要", "包括", "具有", "通过",
])

# ─────────────────────────────────────────────────────────────
# 临床/管理/研究类关键字段词典
# ─────────────────────────────────────────────────────────────
FIELD_PATTERNS = {
    "CLN": {
        "基本信息": ["患者姓名", "姓名", "住院号", "门诊号", "病历号", "性别", "年龄", "出生日期",
                    "联系电话", "家庭住址", "入院日期", "出院日期", "科室", "床号", "主治医师"],
        "诊断信息": ["主诊断", "诊断", "ICD", "分期", "分级", "诊断依据", "诊断日期",
                    "病理诊断", "临床诊断", "主诉", "现病史", "既往史"],
        "治疗信息": ["治疗方案", "用药", "药品名称", "剂量", "给药途径", "手术", "手术名称",
                    "治疗日期", "疗程", "治疗效果", "不良反应", "化疗方案", "放疗"],
        "检验检查信息": ["检验", "检查", "检测", "血常规", "尿常规", "生化", "CT", "MRI",
                       "超声", "心电图", "检查项目", "检查结果", "参考范围", "检查日期"],
    },
    "MGT": {
        "科室信息": ["科室", "病区", "部门", "归属", "二级科室"],
        "工作内容": ["工作项目", "工作内容", "执行人", "完成时间", "工作量", "完成情况"],
        "规则要求": ["规范", "标准", "要求", "依据", "违规", "合规", "执行标准"],
        "统计指标": ["指标", "目标值", "实际值", "完成率", "统计周期", "考核", "达标"],
        "人员信息": ["负责人", "姓名", "职务", "职称", "联系方式", "签字", "工号"],
    },
    "RES": {
        "研究方法": ["研究设计", "随机", "盲法", "对照", "统计方法", "样本量", "检验水准"],
        "技术路线": ["实验步骤", "技术路线", "流程", "时间节点", "操作要点"],
        "研究对象": ["入组标准", "排除标准", "纳入标准", "年龄", "病例数", "知情同意", "研究对象"],
        "研究条件": ["实验设备", "试剂", "仪器型号", "环境温度", "储存条件", "规格"],
        "验证方法及要求": ["验证指标", "阈值", "合格标准", "重复次数", "验证方法", "精密度", "准确度"],
    }
}

# 控件类型推断规则
CONTROL_TYPE_RULES = [
    (re.compile(r"(姓名|名称|编号|号码|地址|说明|描述|备注|主诉|病史|方案|内容|步骤|要点|情况)"), "text"),
    (re.compile(r"(日期|时间|出生|就诊|入院|出院|手术日|检查日|开始|结束)"), "date"),
    (re.compile(r"(年龄|次数|剂量|数量|值|率|分数|评分|次|个|mg|ml|kg|cm|mmHg|次/天)"), "number"),
    (re.compile(r"(性别|男|女|是否|状态|阳性|阴性|分期|分级|程度|类型|科室|部门|途径|方式|设计类型)"), "select"),
    (re.compile(r"(并发症|药物|合并症|并存病|多选|勾选|项目)"), "checkbox"),
    (re.compile(r"(报告|附件|单据|图片|文件|影像|扫描)"), "file"),
    (re.compile(r"(矩阵|批量|多项|列表|明细|汇总表)"), "matrix"),
    (re.compile(r"(现病史|既往史|主诉|描述|备注|说明|意见|总结|处置)"), "textarea"),
]


def infer_control_type(label):
    """根据字段名推断控件类型"""
    for pattern, ctype in CONTROL_TYPE_RULES:
        if pattern.search(label):
            return ctype
    return "text"


def extract_keywords(text, top_n=30):
    """提取高频词"""
    # 简单分词（按标点和空格切割，过滤短词和停用词）
    tokens = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]{2,8}', text)
    tokens = [t for t in tokens if t not in STOP_WORDS and not t.isdigit()]
    freq = Counter(tokens)
    return freq.most_common(top_n)


def extract_table_headers(text):
    """识别文档中已有表格的表头（简单启发式：连续的「、」分隔词组）"""
    # 匹配像"姓名、性别、年龄、诊断"这样的连续字段列表
    pattern = re.compile(r'([\u4e00-\u9fa5]{1,10}[（）()A-Za-z0-9]*(?:[、，,]\s*[\u4e00-\u9fa5]{1,10}[（）()A-Za-z0-9]*){2,})')
    matches = pattern.findall(text)
    results = []
    for m in matches:
        items = re.split(r'[、，,]\s*', m.strip())
        if len(items) >= 3:
            results.append(items)
    return results


def match_fields_from_text(text, btype):
    """从文本中匹配已知字段关键词，返回候选字段列表"""
    found = {}
    patterns_dict = FIELD_PATTERNS.get(btype, FIELD_PATTERNS["CLN"])
    for group, keywords in patterns_dict.items():
        for kw in keywords:
            if kw in text:
                if group not in found:
                    found[group] = []
                found[group].append(kw)
    return found


def build_field_schema(form_name, btype, matched_groups, source_doc=""):
    """根据匹配到的字段构建 JSON Schema"""
    fields = []
    fid_counter = 1
    for group, labels in matched_groups.items():
        seen = set()
        for label in labels:
            if label in seen:
                continue
            seen.add(label)
            ctype = infer_control_type(label)
            field = {
                "id": f"field_{fid_counter:03d}",
                "group": group,
                "label": label,
                "type": ctype,
                "required": label in ["患者姓名", "姓名", "住院号", "性别", "年龄", "就诊日期", "主诊断", "科室", "负责人", "研究设计"],
                "placeholder": f"请输入{label}" if ctype in ("text", "number", "textarea") else "",
                "options": [],
                "validation": "",
            }
            # 为部分select字段补充默认选项
            if ctype == "select" and "性别" in label:
                field["options"] = [{"value": "男", "label": "男"}, {"value": "女", "label": "女"}]
            elif ctype == "select" and "科室" in label:
                field["options"] = [{"value": "", "label": "（从系统获取）"}]
            fields.append(field)
            fid_counter += 1

    return {
        "form_name": form_name,
        "business_type": btype,
        "source_document": source_doc,
        "version": "1.0",
        "fields": fields
    }


def main():
    parser = argparse.ArgumentParser(description="医疗文档字段提取工具")
    parser.add_argument("doc_file", help="文档文本文件路径")
    parser.add_argument("--btype", default="CLN", choices=["CLN", "MGT", "RES"],
                        help="业务类型：CLN临床 MGT管理 RES研究")
    parser.add_argument("--name", default="医疗表单", help="表单名称")
    parser.add_argument("--out", default="extracted_schema.json", help="输出JSON文件路径")
    args = parser.parse_args()

    with open(args.doc_file, "r", encoding="utf-8") as fh:
        text = fh.read()

    print(f"\n📄 文档长度：{len(text)} 字符")
    print(f"   业务类型：{args.btype}\n")

    # 关键词提取
    keywords = extract_keywords(text, top_n=20)
    print("🔑 高频关键词 Top 20：")
    for kw, freq in keywords:
        print(f"   {kw}（{freq}次）")

    # 表头识别
    headers = extract_table_headers(text)
    if headers:
        print(f"\n📊 识别到的表格字段列表：")
        for h in headers[:5]:
            print(f"   {' | '.join(h)}")

    # 字段匹配
    matched = match_fields_from_text(text, args.btype)
    print(f"\n🏷️  字段匹配结果：")
    total = 0
    for g, fs in matched.items():
        print(f"   [{g}] {', '.join(fs)}")
        total += len(fs)
    print(f"   共 {total} 个字段候选")

    # 构建schema
    schema = build_field_schema(args.name, args.btype, matched, args.doc_file)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(schema, fh, ensure_ascii=False, indent=2)
    print(f"\n✅ Schema 已保存至：{args.out}")
    print(f"   下一步：python generate_form.py {args.out}")


if __name__ == "__main__":
    main()
