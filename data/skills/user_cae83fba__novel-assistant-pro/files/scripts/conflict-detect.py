#!/usr/bin/env python3
"""
conflict-detect.py - 剧情冲突自动检测

v2.0.0 新增。检测 7 项剧情冲突维度。

使用：
    python3 conflict-detect.py --memory memory/novels/{slug}.md --chapter chapter-008.md
"""

import argparse
import json
import re
import sys
from pathlib import Path


def check_hard_rules_violation(memory: str, chapter: str) -> list:
    """检查世界观硬规则违反。"""
    issues = []

    # 提取硬规则
    hard_rules_section = re.search(r'### 硬规则.*?\n(.*?)(?=\n### |\Z)', memory, re.DOTALL)
    if not hard_rules_section:
        return issues

    rules_text = hard_rules_section.group(1)
    # 简化：每条硬规则作为一个关键词列表检查
    rules = re.findall(r'^\d+\.\s*(.+)$', rules_text, re.MULTILINE)

    # 这里做简化处理：实际项目需结合规则内容智能判断
    for i, rule in enumerate(rules, 1):
        # 仅作为示例：检查常见违反模式
        if '不能' in rule or '不可' in rule:
            # 提取禁止行为的关键短语
            forbidden = re.search(r'(不能|不可)(.{2,15})', rule)
            if forbidden:
                phrase = forbidden.group(2).strip()
                if phrase in chapter:
                    # 检查上下文是否有反转（"破例""但是"等）
                    if not re.search(rf'破例|但是|然而.*{phrase}', chapter):
                        issues.append({
                            'id': f'C{i:03d}',
                            'level': 'ERROR',
                            'type': 'hard_rule_violation',
                            'message': f'可能违反硬规则 #{i}：{rule.strip()}',
                        })
    return issues


def check_passive_overuse(chapter: str) -> list:
    """检查被动句堆叠。"""
    passive_pattern = r'被.{2,8}'
    count = len(re.findall(passive_pattern, chapter))
    issues = []
    if count > 5:
        issues.append({
            'id': 'C101',
            'level': 'WARNING',
            'type': 'passive_overuse',
            'message': f'被动句过多：{count} 次 / 全章',
        })
    return issues


def check_chapter_meta_leak(chapter: str) -> list:
    """检查章节编号泄露（痕迹 9）。"""
    issues = []
    patterns = [
        r'本章结束',
        r'本章.{0,5}结尾',
        r'这是第.{1,3}章',
        r'\(第.{1,3}章\)',
    ]
    for pattern in patterns:
        if re.search(pattern, chapter):
            issues.append({
                'id': 'C201',
                'level': 'WARNING',
                'type': 'chapter_meta_leak',
                'message': '检测到章节元叙述泄露',
            })
            break
    return issues


def check_generic_ending(chapter: str) -> list:
    """检查通用化总结（痕迹 10）。"""
    issues = []
    last_300 = chapter[-300:]
    patterns = [
        r'从此.{2,10}',
        r'一切.{0,5}刚刚开始',
        r'一切.{0,5}结束',
    ]
    for pattern in patterns:
        if re.search(pattern, last_300):
            issues.append({
                'id': 'C301',
                'level': 'INFO',
                'type': 'generic_ending',
                'message': '章末出现通用化总结，建议改用具体场景',
            })
            break
    return issues


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 剧情冲突自动检测（v2.0.0）'
    )
    parser.add_argument('--memory', help='记忆文件路径')
    parser.add_argument('--chapter', required=True, help='章节文件路径')
    parser.add_argument('--output', help='报告输出路径')

    args = parser.parse_args()
    chapter_path = Path(args.chapter)
    if not chapter_path.exists():
        print(f'错误：章节文件不存在：{args.chapter}', file=sys.stderr)
        sys.exit(1)

    chapter = chapter_path.read_text(encoding='utf-8')
    memory = ''
    if args.memory and Path(args.memory).exists():
        memory = Path(args.memory).read_text(encoding='utf-8')

    issues = []
    if memory:
        issues.extend(check_hard_rules_violation(memory, chapter))
    issues.extend(check_passive_overuse(chapter))
    issues.extend(check_chapter_meta_leak(chapter))
    issues.extend(check_generic_ending(chapter))

    errors = [i for i in issues if i['level'] == 'ERROR']
    warnings = [i for i in issues if i['level'] == 'WARNING']
    infos = [i for i in issues if i['level'] == 'INFO']

    print(f'=== 剧情冲突检测（第 {chapter_path.stem} 章）===')
    print(f'\n严重冲突：{len(errors)} 个')
    for e in errors:
        print(f"  ✗ [{e['id']}] {e['message']}")

    print(f'\n中度疑点：{len(warnings)} 个')
    for w in warnings:
        print(f"  ⚠ [{w['id']}] {w['message']}")

    print(f'\n轻微可优化：{len(infos)} 个')
    for i in infos:
        print(f"  ℹ [{i['id']}] {i['message']}")

    print(f'\n阻塞状态：{"必须修复才能继续" if errors else "可以继续"}')

    if args.output:
        report = {
            'chapter': str(chapter_path),
            'error_count': len(errors),
            'warning_count': len(warnings),
            'info_count': len(infos),
            'issues': issues,
        }
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\n报告已保存：{args.output}')

    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
