#!/usr/bin/env python3
"""
chapter-pacing-report.py - 章节节拍五要素打分

v2.0.0 新增。基于规则引擎对"目标-阻力-变化-反馈-钩子"五要素打分。

使用：
    python3 chapter-pacing-report.py --chapter chapter-008.md --memory memory/novels/{slug}.md
"""

import argparse
import json
import re
import sys
from pathlib import Path


FIVE_ELEMENTS = {
    'goal': {'name': '目标', 'weight': 0.2},
    'obstacle': {'name': '阻力', 'weight': 0.2},
    'change': {'name': '变化', 'weight': 0.2},
    'feedback': {'name': '反馈', 'weight': 0.2},
    'hook': {'name': '钩子', 'weight': 0.2},
}


def analyze_goal(content: str) -> dict:
    """分析目标要素：识别主角目标。"""
    patterns = [
        r'主角.{0,10}(想要|希望|打算|计划|决心)',
        r'(他|她|我|主角).{0,15}(必须|要|想|决定)',
        r'本章.{0,5}(目标|任务)',
    ]
    score = 0
    for pattern in patterns:
        if re.search(pattern, content):
            score += 3
    return {
        'name': FIVE_ELEMENTS['goal']['name'],
        'score': min(score, 10),
        'comment': '目标' + ('明确' if score >= 6 else '不够明确'),
    }


def analyze_obstacle(content: str) -> dict:
    """分析阻力要素：识别冲突来源。"""
    patterns = [
        r'(却|但|然而|但是)',
        r'(阻止|阻挡|反对|阻碍|拒绝)',
        r'(困难|难题|危机)',
        r'(无法|不能|不可能)',
    ]
    score = 0
    for pattern in patterns:
        matches = re.findall(pattern, content)
        score += min(len(matches), 3)
    return {
        'name': FIVE_ELEMENTS['obstacle']['name'],
        'score': min(score, 10),
        'comment': '阻力' + ('充分' if score >= 6 else '不够强'),
    }


def analyze_change(content: str) -> dict:
    """分析变化要素：识别状态变化。"""
    patterns = [
        r'(终于|最终|终于明白)',
        r'(明白|发现|意识到|领悟)',
        r'(决定|选择|决心)',
        r'(改变|变了|变化)',
    ]
    score = 0
    for pattern in patterns:
        matches = re.findall(pattern, content)
        score += min(len(matches), 3)
    return {
        'name': FIVE_ELEMENTS['change']['name'],
        'score': min(score, 10),
        'comment': '变化' + ('明显' if score >= 6 else '不够明显'),
    }


def analyze_feedback(content: str) -> dict:
    """分析反馈要素：识别主角反应。"""
    patterns = [
        r'(她|他|我|主角).{0,8}(想|感觉|觉得|明白|知道)',
        r'(内心|心中|脑海里)',
        r'(沉默|眼泪|愤怒|苦笑)',
    ]
    score = 0
    for pattern in patterns:
        matches = re.findall(pattern, content)
        score += min(len(matches), 3)
    return {
        'name': FIVE_ELEMENTS['feedback']['name'],
        'score': min(score, 10),
        'comment': '反馈' + ('充分' if score >= 6 else '可加强'),
    }


def analyze_hook(content: str) -> dict:
    """分析钩子要素：检查章末是否有钩子。"""
    # 取最后 500 字
    last_500 = content[-500:] if len(content) > 500 else content
    patterns = [
        r'(突然|忽然)',
        r'(原来|发现)',
        r'(她|他).{0,8}(看见|听到|意识到)',
        r'[？\?]$|[！!]$',
        r'(门|手机|电话|敲门)',
    ]
    score = 0
    for pattern in patterns:
        if re.search(pattern, last_500):
            score += 2
    return {
        'name': FIVE_ELEMENTS['hook']['name'],
        'score': min(score, 10),
        'comment': '钩子' + ('强烈' if score >= 6 else '偏弱'),
    }


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 章节节拍五要素打分（v2.0.0）'
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

    analyses = [
        analyze_goal(content),
        analyze_obstacle(content),
        analyze_change(content),
        analyze_feedback(content),
        analyze_hook(content),
    ]

    total_score = sum(a['score'] for a in analyses) / 5

    print(f'=== 章节节拍诊断（第 {chapter_path.stem} 章）===')
    print(f'\n五要素检查：')
    for a in analyses:
        mark = '✓' if a['score'] >= 6 else '✗' if a['score'] <= 3 else '-'
        print(f"  {mark} {a['name']}：{a['score']}/10 - {a['comment']}")

    print(f'\n节拍分：{total_score:.1f}/10')
    if total_score >= 7:
        print('判定：合格')
    elif total_score >= 5:
        print('判定：基本合格，建议优化')
    else:
        print('判定：需改进')

    if args.output:
        report = {
            'chapter': str(chapter_path),
            'total_score': total_score,
            'elements': analyses,
        }
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\n报告已保存：{args.output}')


if __name__ == '__main__':
    main()
