#!/usr/bin/env python3
"""Validate core content and common methodological errors in a Chinese risk report."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED: list[tuple[str, tuple[str, ...]]] = [
    ("评估对象或范围", ("评估对象", "评估范围", "对象与范围")),
    ("基准日或数据截止日", ("基准日", "数据截止", "截止日期")),
    ("评估依据", ("评估依据", "依据、标准", "适用标准")),
    ("评估方法与分级", ("评估方法", "分级标准", "可能性", "影响程度")),
    ("管理层摘要或总体结论", ("管理层摘要", "总体结论", "评估结论")),
    ("风险清单", ("风险清单", "风险台账", "风险登记")),
    ("固有风险", ("固有风险",)),
    ("控制评价", ("控制有效", "设计有效", "运行有效")),
    ("剩余风险", ("剩余风险", "残余风险")),
    ("处置计划", ("处置计划", "整改计划", "风险处置")),
    ("责任人与日期", ("责任人", "责任主体")),
    ("监测与触发", ("KRI", "关键风险指标", "触发条件", "监测")),
    ("证据", ("证据台账", "证据状态", "来源与定位")),
    ("假设或限制", ("假设", "限制", "局限")),
]

FORBIDDEN = (
    "零风险",
    "绝对安全",
    "完全消除风险",
    "保证不发生",
    "所有风险均可控",
    "所有风险完全可控",
    "所有风险可接受",
)


def contains_any(text: str, options: tuple[str, ...]) -> bool:
    return any(option.lower() in text.lower() for option in options)


def has_affirmative_evidence(text: str) -> bool:
    """Return True only when an evidence term is not immediately negated."""
    terms = ("抽样", "日志", "演练", "测试记录", "审批记录", "审计记录", "运行样本")
    negation = re.compile(r"(无|没有|未|缺少|不含|未提供|未见|无法提供).{0,8}$")
    for term in terms:
        for match in re.finditer(re.escape(term), text):
            prefix = text[max(0, match.start() - 12) : match.start()]
            if not negation.search(prefix):
                return True
    return False


def validate(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for label, terms in REQUIRED:
        if not contains_any(text, terms):
            errors.append(f"缺少：{label}")

    for phrase in FORBIDDEN:
        if phrase in text:
            errors.append(f"不当保证性表述：{phrase}")

    if re.search(
        r"(风险总分|总体风险得分|平均风险分|风险平均分|"
        r"(风险|评分|得分).{0,30}平均\s*\d|平均\s*\d+(?:\.\d+)?)",
        text,
    ):
        warnings.append("发现风险总分/平均分；不得用聚合分数掩盖单项重大风险或红线")

    if re.search(r"(剩余|残余)风险.{0,40}(低|降低|可接受)", text, re.S):
        if not has_affirmative_evidence(text):
            errors.append("剩余风险被降低或接受，但未发现控制运行有效性证据")

    if re.search(r"(控制后.{0,20}风险|风险.{0,20})(降至|降为|降低到)\s*\d", text):
        if not has_affirmative_evidence(text):
            errors.append("发现控制后风险数值降级，但未发现肯定性的运行证据")

    if contains_any(text, ("接受风险", "风险接受", "可接受")):
        if not contains_any(text, ("风险偏好", "容忍度", "红线", "批准主体", "批准人")):
            errors.append("风险接受结论未对照偏好/容忍度或未说明批准权限")

    percentage_matches = re.findall(r"\b\d+(?:\.\d+)?\s*%", text)
    if percentage_matches and not contains_any(
        text, ("数据来源", "模型参数", "历史频率", "样本", "来源与定位")
    ):
        warnings.append("发现百分比概率或比例，但未发现数据/模型来源说明")

    if re.search(r"(预计损失|期望损失|最大(?:可能)?损失|压力损失).{0,12}\d+(?:\.\d+)?\s*(万|亿)?元", text):
        if not contains_any(
            text, ("数据来源", "模型参数", "历史损失", "损失口径", "来源与定位", "敏感性")
        ):
            warnings.append("发现精确损失金额，但未发现数据来源、模型参数或损失口径")

    if contains_any(text, ("重大风险", "极高风险", "高风险")) or re.search(
        r"重大.{0,10}(事件|网络|安全|事故)", text
    ):
        if not contains_any(text, ("情景", "压力测试", "应急预案", "合理不利")):
            warnings.append("存在重大/高风险，但未发现情景、压力测试或应急安排")

    if contains_any(text, ("加强管理", "持续关注", "持续改进")):
        if not (
            contains_any(text, ("责任人", "责任主体"))
            and contains_any(text, ("最迟日期", "完成日期", "截止日期"))
            and contains_any(text, ("验证证据", "关闭条件", "验收标准"))
        ):
            warnings.append("存在泛化措施，但责任、日期或验证关闭条件可能不完整")

    if re.search(r"(近期|尽快|适时|后续完成)", text) and not re.search(
        r"\b20\d{2}[-年/.]\d{1,2}[-月/.]\d{1,2}", text
    ):
        warnings.append("行动日期只有相对表述；应使用绝对日期")

    if re.search(
        r"(制度.{0,20}(建立|制定)|通过.{0,12}认证|取得.{0,12}认证)"
        r".{0,24}(因此|所以|表明|证明).{0,20}(控制.{0,4}有效|运行有效|风险.{0,4}(低|降低))",
        text,
    ):
        warnings.append("可能把认证或制度存在直接推导为控制运行有效")
    elif contains_any(text, ("认证", "制度已建立", "已制定制度")) and contains_any(
        text, ("控制有效", "风险较低", "风险降低")
    ) and not has_affirmative_evidence(text):
        warnings.append("可能把认证或制度存在等同于控制运行有效")

    if not re.search(r"\bR[-_]?\d+\b", text, re.I):
        warnings.append("未发现唯一风险编号，追踪和整改闭环可能困难")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--strict", action="store_true", help="将警告视为错误")
    args = parser.parse_args()

    try:
        text = args.report.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate(text)
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")

    effective_errors = len(errors) + (len(warnings) if args.strict else 0)
    print(
        f"SUMMARY: {len(errors)} error(s), {len(warnings)} warning(s), "
        f"strict={'on' if args.strict else 'off'}"
    )
    return 1 if effective_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
