#!/usr/bin/env python3
"""
platform-validate.py - 平台调性校验

v2.0.0 新增。校验章节是否符合指定平台的字数、钩子、爽点等要求。

使用：
    python3 platform-validate.py --platform tomato --chapter chapter-008.md --memory memory/novels/{slug}.md
    python3 platform-validate.py --platform qidian --chapter chapter-008.md --memory memory/novels/{slug}.md
"""

import argparse
import json
import sys
from pathlib import Path


PLATFORM_RULES = {
    'tomato': {
        'name': '番茄小说',
        'word_count_range': (1500, 2500),
        'hook_position': ['end'],
        'hook_required': True,
        'ai_score_threshold': 7,
        'pacing_score_threshold': 7,
    },
    'qidian': {
        'name': '起点中文网',
        'word_count_range': (2000, 4000),
        'hook_position': ['end'],
        'hook_required': True,
        'ai_score_threshold': 8,
        'pacing_score_threshold': 7,
    },
    'jinjiang': {
        'name': '晋江文学城',
        'word_count_range': (1500, 3000),
        'hook_position': ['end'],
        'hook_required': True,
        'ai_score_threshold': 8,
        'pacing_score_threshold': 6,
    },
    'qimao': {
        'name': '七猫小说',
        'word_count_range': (1500, 2500),
        'hook_position': ['end'],
        'hook_required': True,
        'ai_score_threshold': 7,
        'pacing_score_threshold': 7,
    },
    'wechat': {
        'name': '微信公众号',
        'word_count_range': (1500, 3000),
        'hook_position': ['end'],
        'hook_required': True,
        'ai_score_threshold': 8,
        'pacing_score_threshold': 6,
    },
    'xhs': {
        'name': '小红书连载',
        'word_count_range': (800, 1500),
        'hook_position': ['end'],
        'hook_required': True,
        'ai_score_threshold': 8,
        'pacing_score_threshold': 7,
    },
}


def validate_platform(platform: str, chapter_path: Path, memory_path: Path = None) -> dict:
    """校验章节是否符合平台规则。"""
    if platform not in PLATFORM_RULES:
        return {'error': f'不支持的平台：{platform}'}

    rules = PLATFORM_RULES[platform]
    content = chapter_path.read_text(encoding='utf-8')
    word_count = len(content)

    issues = []

    # 字数校验
    min_w, max_w = rules['word_count_range']
    if word_count < min_w:
        issues.append({
            'level': 'WARNING',
            'type': 'word_count_low',
            'message': f'字数不足：{word_count}（要求 {min_w}-{max_w}）',
        })
    elif word_count > max_w:
        issues.append({
            'level': 'WARNING',
            'type': 'word_count_high',
            'message': f'字数过多：{word_count}（要求 {min_w}-{max_w}）',
        })

    # 钩子校验（章末）
    last_300 = content[-300:]
    hook_patterns = [r'(突然|忽然|原来|却)', r'[？\?]$|[！!]$', r'(门|手机|电话)']
    has_hook = any(
        __import__('re').search(p, last_300)
        for p in hook_patterns
    )
    if rules['hook_required'] and not has_hook:
        issues.append({
            'level': 'WARNING',
            'type': 'missing_hook',
            'message': '章末缺少钩子',
        })

    return {
        'platform': platform,
        'platform_name': rules['name'],
        'chapter': str(chapter_path),
        'word_count': word_count,
        'word_count_range': rules['word_count_range'],
        'issues': issues,
    }


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 平台调性校验（v2.0.0）'
    )
    parser.add_argument('--platform', required=True, choices=list(PLATFORM_RULES.keys()), help='平台')
    parser.add_argument('--chapter', required=True, help='章节文件路径')
    parser.add_argument('--memory', help='记忆文件路径')
    parser.add_argument('--output', help='报告输出路径')

    args = parser.parse_args()
    chapter_path = Path(args.chapter)
    memory_path = Path(args.memory) if args.memory else None

    if not chapter_path.exists():
        print(f'错误：章节文件不存在：{args.chapter}', file=sys.stderr)
        sys.exit(1)

    report = validate_platform(args.platform, chapter_path, memory_path)

    if 'error' in report:
        print(f'错误：{report["error"]}', file=sys.stderr)
        sys.exit(1)

    print(f'=== 平台调性校验（{report["platform_name"]}）===')
    print(f'章节：{chapter_path.name}')
    print(f'字数：{report["word_count"]}（要求 {report["word_count_range"][0]}-{report["word_count_range"][1]}）')

    if report['issues']:
        print(f'\n问题：')
        for issue in report['issues']:
            mark = '⚠' if issue['level'] == 'WARNING' else 'ℹ'
            print(f"  {mark} {issue['message']}")
    else:
        print('\n✓ 无问题')

    if args.output:
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\n报告已保存：{args.output}')


if __name__ == '__main__':
    main()
