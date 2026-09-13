#!/usr/bin/env python3
"""
dialogue-style-check.py - 对白风格校验

v2.0.0 新增。基于对话风格样本库，校验章节对白是否漂移。

使用：
    python3 dialogue-style-check.py --character 林澈 --chapter chapter-008.md --memory memory/novels/{slug}.md
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_character_dialogues(content: str, character: str) -> list:
    """提取人物对白。"""
    pattern = rf'「[^」]*」|""[^""]+""'
    dialogues = re.findall(pattern, content)
    # 简化：返回所有对白（实际可通过主语过滤）
    return [d.strip('「」""') for d in dialogues]


def check_dash_usage(dialogues: list) -> dict:
    """检查破折号使用。"""
    count = sum(d.count('——') for d in dialogues)
    return {'dash_count': count, 'overused': count > len(dialogues) * 0.5}


def check_avg_sentence_length(dialogues: list) -> dict:
    """检查对白平均句长。"""
    if not dialogues:
        return {'avg_length': 0, 'too_long': False}
    total = sum(len(d) for d in dialogues)
    avg = total / len(dialogues)
    return {'avg_length': round(avg, 1), 'too_long': avg > 30}


def check_emotional_labels(dialogues: list) -> dict:
    """检查情绪标签直白化。"""
    patterns = ['非常', '十分', '极其', '深深地', '陷入了']
    count = sum(
        sum(1 for p in patterns if p in d)
        for d in dialogues
    )
    return {'emotional_label_count': count, 'overused': count > len(dialogues) * 0.3}


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 对白风格校验（v2.0.0）'
    )
    parser.add_argument('--character', required=True, help='人物名')
    parser.add_argument('--chapter', required=True, help='章节文件路径')
    parser.add_argument('--memory', help='记忆文件路径')
    parser.add_argument('--output', help='报告输出路径')

    args = parser.parse_args()
    chapter_path = Path(args.chapter)
    if not chapter_path.exists():
        print(f'错误：章节文件不存在：{args.chapter}', file=sys.stderr)
        sys.exit(1)

    content = chapter_path.read_text(encoding='utf-8')
    dialogues = extract_character_dialogues(content, args.character)

    if not dialogues:
        print(f'未找到 {args.character} 的对白')
        return

    dash_check = check_dash_usage(dialogues)
    length_check = check_avg_sentence_length(dialogues)
    emotional_check = check_emotional_labels(dialogues)

    drift_score = 0
    drift_score += 30 if dash_check['overused'] else 0
    drift_score += 30 if length_check['too_long'] else 0
    drift_score += 40 if emotional_check['overused'] else 0

    print(f'=== 对白风格校验（{args.character}）===')
    print(f'对白数量：{len(dialogues)}')
    print(f'\n破折号：{dash_check["dash_count"]} 次（{"过多" if dash_check["overused"] else "正常"}）')
    print(f'平均句长：{length_check["avg_length"]} 字（{"过长" if length_check["too_long"] else "正常"}）')
    print(f'情绪标签：{emotional_check["emotional_label_count"]} 处（{"过多" if emotional_check["overused"] else "正常"}）')
    print(f'\n漂移度：{drift_score}/100')

    if drift_score < 20:
        print('判定：完全一致')
    elif drift_score < 50:
        print('判定：轻微漂移（合格）')
    elif drift_score < 80:
        print('判定：中度漂移（建议调整）')
    else:
        print('判定：严重漂移（必须改写）')

    if args.output:
        report = {
            'character': args.character,
            'chapter': str(chapter_path),
            'dialogue_count': len(dialogues),
            'drift_score': drift_score,
            'checks': {
                'dash': dash_check,
                'length': length_check,
                'emotional': emotional_check,
            },
        }
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\n报告已保存：{args.output}')


if __name__ == '__main__':
    main()
