#!/usr/bin/env python3
"""Validate 药店 AI lead-generation video prompt markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


INDUSTRY = '药店'
FORBIDDEN = ['全网第一', '行业第一', '最好', '最强', '顶级', '百分之百', '100%', '保证成交', '保证获客', '必爆', '稳赚', '零风险', '永久有效', '一次见效', '包治、药到病除或无副作用', '公开推广处方药或诱导超说明书用药', '替代医生诊断、擅自停药换药或给出个体处方', '虚构稀缺、疗效案例和专家推荐']
REQUIRED_FIELDS = ["景别：", "运镜：", "光影：", "构图：", "氛围：", "情绪："]
CTA_WORDS = ["评论", "私信", "预约", "咨询", "到店", "团购", "报名", "试用", "领取", "下单", "查看"]


def units(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^##\s+示例\d+[^\n]*", text))
    if not matches:
        return [("成品提示词", text)]
    output = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        output.append((match.group(0).lstrip("# ").strip(), text[match.start():end]))
    return output


def spoken_count(text: str) -> int:
    pieces = re.findall(r"口播：([^\n]+)", text)
    joined = "".join(piece for piece in pieces if "无口播" not in piece)
    chinese = re.findall(r"[\u4e00-\u9fff]", joined)
    alnum = re.findall(r"[A-Za-z0-9]+", joined)
    return len(chinese) + len(alnum)


def validate_unit(label: str, text: str, duration: float | None) -> dict:
    errors = []
    warnings = []
    pattern = re.compile(r"【\s*(\d+(?:\.\d+)?)\s*[-—至]\s*(\d+(?:\.\d+)?)\s*秒")
    segments = [(float(a), float(b)) for a, b in pattern.findall(text)]
    if not segments:
        errors.append("未找到【0-3秒】格式的时间轴")
        inferred = duration
    else:
        inferred = duration if duration is not None else segments[-1][1]
        if abs(segments[0][0]) > 1e-6:
            errors.append("时间轴必须从0秒开始")
        for index, (start, end) in enumerate(segments):
            if end <= start:
                errors.append(f"第{index + 1}段结束时间必须大于开始时间")
            if index and abs(start - segments[index - 1][1]) > 1e-6:
                errors.append(
                    f"第{index}段结束{segments[index - 1][1]:g}秒与"
                    f"第{index + 1}段开始{start:g}秒不连续"
                )
        if inferred is not None and abs(segments[-1][1] - inferred) > 1e-6:
            errors.append(
                f"时间轴结束于{segments[-1][1]:g}秒，不等于指定{inferred:g}秒"
            )
    shot_chunks = re.split(r"(?=【\s*\d+(?:\.\d+)?\s*[-—至])", text)
    shot_chunks = [chunk for chunk in shot_chunks if pattern.search(chunk)]
    for index, chunk in enumerate(shot_chunks):
        missing = [field for field in REQUIRED_FIELDS if field not in chunk]
        if missing:
            errors.append(f"第{index + 1}镜缺少：{'、'.join(missing)}")
        if "光比" not in chunk:
            errors.append(f"第{index + 1}镜光影缺少光比")
        if not re.search(r"(m/s|秒/圈|每秒|固定机位|三脚架|斯坦尼康|稳定器|滑轨|手持)", chunk):
            warnings.append(f"第{index + 1}镜运镜可能缺少设备或量化参数")
    count = spoken_count(text)
    if inferred is not None:
        limit = 50 if inferred <= 15 else 70 if inferred <= 30 else round(inferred / 60 * 140)
        if count > limit:
            errors.append(f"口播约{count}字，超过{inferred:g}秒建议上限{limit}字")
    for word in FORBIDDEN:
        if word and word in text:
            errors.append(f"命中行业禁用承诺：{word}")
    if not any(word in text for word in CTA_WORDS):
        errors.append("缺少评论、私信、预约、咨询或其他可执行承接动作")
    if "BPM" not in text.upper():
        warnings.append("没有明确BGM的BPM")
    if not re.search(r"@图片\d+", text):
        warnings.append("没有找到@图片N素材映射")
    return {
        "label": label,
        "duration": inferred,
        "spoken_count": count,
        "errors": list(dict.fromkeys(errors)),
        "warnings": list(dict.fromkeys(warnings)),
        "passed": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt_file", type=Path)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    text = args.prompt_file.read_text(encoding="utf-8")
    results = [
        validate_unit(label, value, args.duration)
        for label, value in units(text)
    ]
    payload = {
        "industry": INDUSTRY,
        "file": str(args.prompt_file),
        "passed": all(item["passed"] for item in results),
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"[{'PASS' if payload['passed'] else 'FAIL'}] {INDUSTRY}视频提示词")
        for item in results:
            print(f"- {item['label']}：口播约{item['spoken_count']}字")
            for error in item["errors"]:
                print(f"  错误：{error}")
            for warning in item["warnings"]:
                print(f"  提醒：{warning}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
