#!/usr/bin/env python3
"""
anti-ai-scan.py - AI 痕迹扫描

v2.0.0 新增。扫描 10 条典型 AI 痕迹并打分。

使用：
    python3 anti-ai-scan.py --chapter chapter-008.md
    python3 anti-ai-scan.py --chapter chapter-008.md --locate
"""

import argparse
import json
import re
import sys
from pathlib import Path


TRACE_PATTERNS = {
    1: {'name': '破折号滥用', 'pattern': r'——', 'penalty': 0.5, 'threshold': 5},
    2: {'name': '对比结构', 'pattern': r'(不是|并非).{1,8}，(而是|是)', 'penalty': 1, 'threshold': 3},
    3: {'name': '拟人化用词', 'pattern': r'(沉默|时间|风|雨|光|黑暗|真相)\s*(在|从|向|往).{0,8}(蔓延|流淌|低语|呢喃|呼啸|倾泻)', 'penalty': 1, 'threshold': 3},
    4: {'name': '过度比喻', 'pattern': r'(如同|仿佛|好像|犹如).{2,12}(星辰|海洋|花朵|火焰|灵魂|生命)', 'penalty': 1, 'threshold': 4},
    5: {'name': '解释性补注', 'pattern': r'\(注[：:].{1,30}\)|（注[：:].{1,30}）', 'penalty': 1.5, 'threshold': 1},
    6: {'name': '列表化排比', 'pattern': r'她.{0,5}(想要|想知道|想知道|要明白).{0,8}。\s*她.{0,5}\1.{0,8}。\s*她.{0,5}\1', 'penalty': 1, 'threshold': 1},
    7: {'name': '被动句堆叠', 'pattern': r'被.{2,8}', 'penalty': 0.5, 'threshold': 5},
    8: {'name': '情绪标签直白化', 'pattern': r'(非常|十分|极其|深深地|彻彻底底)', 'penalty': 1, 'threshold': 5},
    9: {'name': '章节编号泄露', 'pattern': r'(本章结束|本章.{0,5}结尾|这是第.{1,3}章)', 'penalty': 2, 'threshold': 1},
    10: {'name': '通用化总结', 'pattern': r'(从此.{2,10}|一切.{0,5}刚刚开始|一切.{0,5}结束)', 'penalty': 1.5, 'threshold': 1},
}


def scan_trace(content: str, trace_id: int, locate: bool = False) -> dict:
    """扫描单个痕迹。"""
    trace = TRACE_PATTERNS[trace_id]
    matches = list(re.finditer(trace['pattern'], content))
    count = len(matches)
    overused = count > trace['threshold']
    penalty = trace['penalty'] * count if overused else 0

    result = {
        'id': trace_id,
        'name': trace['name'],
        'count': count,
        'threshold': trace['threshold'],
        'overused': overused,
        'penalty': penalty,
    }

    if locate and matches:
        locations = []
        for m in matches[:10]:
            line_no = content[:m.start()].count('\n') + 1
            locations.append({'line': line_no, 'text': m.group()[:50]})
        result['locations'] = locations

    return result


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · AI 痕迹扫描（v2.0.0）'
    )
    parser.add_argument('--chapter', required=True, help='章节文件路径')
    parser.add_argument('--locate', action='store_true', help='显示痕迹位置')
    parser.add_argument('--output', help='报告输出路径')

    args = parser.parse_args()
    chapter_path = Path(args.chapter)
    if not chapter_path.exists():
        print(f'错误：章节文件不存在：{args.chapter}', file=sys.stderr)
        sys.exit(1)

    content = chapter_path.read_text(encoding='utf-8')
    word_count = len(content)

    results = []
    total_penalty = 0
    for trace_id in TRACE_PATTERNS.keys():
        result = scan_trace(content, trace_id, locate=args.locate)
        results.append(result)
        total_penalty += result['penalty']

    final_score = max(0, 10 - total_penalty)

    print(f'=== AI 痕迹扫描（第 {chapter_path.stem} 章）===')
    print(f'章节字数：{word_count}')
    print(f'\n痕迹检查：')
    for r in results:
        mark = '✗' if r['overused'] else '✓'
        print(f"  {mark} 痕迹 {r['id']}（{r['name']}）：{r['count']} 次 → {'扣 ' + str(r['penalty']) + ' 分' if r['penalty'] else '合格'}")

        if args.locate and 'locations' in r:
            for loc in r['locations']:
                print(f"      L{loc['line']}: {loc['text']}")

    print(f'\n合计扣分：{total_penalty:.1f}')
    print(f'最终得分：{final_score:.1f}/10')

    if final_score >= 8:
        print('判定：人味充足')
    elif final_score >= 6:
        print('判定：合格')
    elif final_score >= 4:
        print('判定：需改进')
    else:
        print('判定：必须改写')

    if args.output:
        report = {
            'chapter': str(chapter_path),
            'word_count': word_count,
            'total_penalty': total_penalty,
            'final_score': final_score,
            'traces': results,
        }
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\n报告已保存：{args.output}')


if __name__ == '__main__':
    main()
