#!/usr/bin/env python3
"""
world-rules-lint.py - 世界观硬规则自洽校验

v2.0.0 新增。检测硬规则是否被章节违反，并检查规则间是否冲突。

使用：
    python3 world-rules-lint.py --memory memory/novels/{slug}.md --chapter chapter-008.md
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_hard_rules(memory: str) -> list:
    """提取硬规则。"""
    section = re.search(r'### 硬规则.*?\n(.*?)(?=\n### |\Z)', memory, re.DOTALL)
    if not section:
        return []
    text = section.group(1)
    return [line.strip() for line in text.split('\n') if re.match(r'^\d+\.', line)]


def check_rule_consistency(rules: list) -> list:
    """检查规则间一致性。"""
    issues = []

    # 简化：检查常见冲突模式
    keywords_per_rule = []
    for rule in rules:
        keywords_per_rule.append(set(re.findall(r'[一-鿿]{2,4}', rule)))

    # 检查同一关键词是否在不同规则中有矛盾描述
    for i, kw_i in enumerate(keywords_per_rule):
        for j, kw_j in enumerate(keywords_per_rule):
            if i >= j:
                continue
            common = kw_i & kw_j
            if common and ('不能' in rules[i] and '可以' in rules[j]):
                issues.append({
                    'level': 'WARNING',
                    'type': 'rule_conflict',
                    'message': f'硬规则 #{i+1} 与 #{j+1} 可能冲突（共享关键词 {common}）',
                })
    return issues


def check_rule_in_chapter(rules: list, chapter: str) -> list:
    """检查硬规则是否被章节违反。"""
    issues = []
    for i, rule in enumerate(rules, 1):
        # 提取禁止行为
        forbidden = re.search(r'(不能|不可|禁止|不允许)(.{2,20})', rule)
        if forbidden:
            phrase = forbidden.group(2).strip()
            # 检查章节中是否有相反行为
            if phrase in chapter:
                # 检查是否有反转描述
                if not re.search(rf'(破例|但是.{0,5}这次|然而.{0,5}后|改变.{0,5}规则)', chapter):
                    issues.append({
                        'level': 'ERROR',
                        'type': 'rule_violation',
                        'rule_num': i,
                        'message': f'硬规则 #{i} 可能被违反：{rule}',
                    })
    return issues


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 世界观硬规则自洽校验（v2.0.0）'
    )
    parser.add_argument('--memory', required=True, help='记忆文件路径')
    parser.add_argument('--chapter', help='章节文件路径')
    parser.add_argument('--genre', help='流派（用于流派特定校验）')
    parser.add_argument('--output', help='报告输出路径')

    args = parser.parse_args()
    memory_path = Path(args.memory)
    if not memory_path.exists():
        print(f'错误：记忆文件不存在：{args.memory}', file=sys.stderr)
        sys.exit(1)

    memory = memory_path.read_text(encoding='utf-8')
    rules = extract_hard_rules(memory)

    if not rules:
        print('未找到硬规则（"### 硬规则" 章节为空）')
        return

    print(f'=== 世界观硬规则校验 ===')
    print(f'规则数：{len(rules)}')

    issues = []
    issues.extend(check_rule_consistency(rules))

    if args.chapter:
        chapter_path = Path(args.chapter)
        if not chapter_path.exists():
            print(f'错误：章节文件不存在：{args.chapter}', file=sys.stderr)
            sys.exit(1)
        chapter = chapter_path.read_text(encoding='utf-8')
        issues.extend(check_rule_in_chapter(rules, chapter))
    else:
        print('（未指定 --chapter，跳过章节检查）')

    errors = [i for i in issues if i['level'] == 'ERROR']
    warnings = [i for i in issues if i['level'] == 'WARNING']

    if errors:
        print(f'\n【严重】')
        for e in errors:
            print(f"  ✗ {e['message']}")
    if warnings:
        print(f'\n【警告】')
        for w in warnings:
            print(f"  ⚠ {w['message']}")

    if not issues:
        print('\n✓ 无冲突')

    if args.output:
        report = {
            'memory': str(memory_path),
            'rules_count': len(rules),
            'error_count': len(errors),
            'warning_count': len(warnings),
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
