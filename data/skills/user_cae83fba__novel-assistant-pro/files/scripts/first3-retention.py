#!/usr/bin/env python3
"""
first3-retention.py - 开篇留存诊断（4 维评分）

v2.0.0 新增。评估钩子强度、主角处境、欲望与异常、信息密度。

使用：
    python3 first3-retention.py --chapter chapter-001.md --memory memory/novels/{slug}.md
"""

import argparse
import json
import re
import sys
from pathlib import Path


def score_hook(content: str) -> dict:
    """评估钩子强度（章首 200 字）。"""
    first_200 = content[:200]
    patterns = [
        (r'(却|突然|忽然)', 3),
        (r'(「|"|")[^」""]+', 2),
        (r'(看见|发现|意识到)', 2),
        (r'(不可能|怎么会)', 2),
        (r'第.{0,3}秒', 1),
    ]
    score = 0
    for pattern, weight in patterns:
        score += len(re.findall(pattern, first_200)) * weight
    return {
        'name': '钩子强度',
        'score': min(score, 10),
        'sample_text': first_200,
    }


def score_protagonist_situation(content: str) -> dict:
    """评估主角处境。"""
    # 简化：检查是否有身份、压力、欲望的描述
    patterns = [
        (r'(调查员|医生|律师|警察|侦探|学生|农民|工人|老板)', 2),
        (r'(任务|目标|必须|应该|想要)', 2),
        (r'(压力|危机|困境|难题|威胁)', 2),
        (r'(我.{0,3}(叫|是)|她.{0,3}(叫|是)|他.{0,3}(叫|是))', 1),
    ]
    score = 0
    for pattern, weight in patterns:
        score += len(re.findall(pattern, content)) * weight
    return {
        'name': '主角处境',
        'score': min(score, 10),
    }


def score_desire_and_anomaly(content: str) -> dict:
    """评估欲望与异常。"""
    patterns = [
        (r'(发现.{0,8}(不|没).{0,5}(正常|对|可能))', 3),
        (r'(奇怪|异常|不可思议|神秘)', 2),
        (r'(系统|穿越|重生|金手指)', 3),
        (r'(身份|血脉|秘密).{0,5}(发现|揭露)', 2),
    ]
    score = 0
    for pattern, weight in patterns:
        score += len(re.findall(pattern, content)) * weight
    return {
        'name': '欲望与异常',
        'score': min(score, 10),
    }


def score_info_density(content: str) -> dict:
    """评估信息密度。"""
    # 信息密度高 = 设定融入情节；密度低 = 大段说明
    paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
    long_paragraphs = sum(1 for p in content.split('\n\n') if len(p) > 200)

    # 设定说明比例（粗略估算）
    bracket_count = len(re.findall(r'（[^）]{5,30}）|\([^)]{5,30}\)', content))

    if paragraph_count == 0:
        score = 5
    else:
        ratio = long_paragraphs / paragraph_count
        score = 10 - int(ratio * 10)
        score = max(3, score)

    if bracket_count > 3:
        score -= 2

    return {
        'name': '信息密度',
        'score': min(max(score, 0), 10),
    }


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 开篇留存诊断（v2.0.0）'
    )
    parser.add_argument('--chapter', required=True, help='章节文件路径')
    parser.add_argument('--memory', help='记忆文件路径')
    parser.add_argument('--output', help='报告输出路径')

    args = parser.parse_args()
    chapter_path = Path(args.chapter)
    if not chapter_path.exists():
        print(f'错误：章节文件不存在：{args.chapter}', file=sys.stderr)
        sys.exit(1)

    content = chapter_path.read_text(encoding='utf-8')

    dimensions = [
        score_hook(content),
        score_protagonist_situation(content),
        score_desire_and_anomaly(content),
        score_info_density(content),
    ]

    total = sum(d['score'] for d in dimensions)

    print(f'=== 开篇留存诊断（第 {chapter_path.stem} 章）===')
    print(f'\n4 维评分：')
    for d in dimensions:
        mark = '✓' if d['score'] >= 7 else '✗' if d['score'] <= 4 else '-'
        print(f"  {mark} {d['name']}：{d['score']}/10")

    print(f'\n总分：{total}/40')

    if total >= 32:
        verdict = '优秀'
    elif total >= 24:
        verdict = '合格'
    elif total >= 16:
        verdict = '需改进'
    else:
        verdict = '不合格'

    print(f'判定：{verdict}')

    if args.output:
        report = {
            'chapter': str(chapter_path),
            'total': total,
            'verdict': verdict,
            'dimensions': dimensions,
        }
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\n报告已保存：{args.output}')


if __name__ == '__main__':
    main()
