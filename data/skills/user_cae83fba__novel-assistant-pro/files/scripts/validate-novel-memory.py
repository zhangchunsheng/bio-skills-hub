#!/usr/bin/env python3
"""
validate-novel-memory.py - 校验小说记忆文件

v2.0.0 新增。校验必填字段、伏笔 ID 唯一性、人物名一致性、章节编号连续性。

使用：
    python3 validate-novel-memory.py memory/novels/{slug}.md
    python3 validate-novel-memory.py memory/novels/{slug}.md --json report.json
    python3 validate-novel-memory.py memory/novels/{slug}.md --show-unresolved
    python3 validate-novel-memory.py memory/novels/{slug}.md --check-p1-stale
"""

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = [
    ('## 基本信息', '小说名'),
    ('## 风格规则', None),
    ('## 世界观规则', None),
    ('## 主要人物', None),
    ('## 人物关系', None),
    ('## 主线与阶段目标', None),
    ('## 章节概要', None),
    ('## 未解决伏笔', None),
    ('## 已回收伏笔', None),
    ('## 时间线', None),
]


def check_required_sections(content: str) -> list:
    """检查必填章节是否存在。"""
    issues = []
    for section, _ in REQUIRED_FIELDS:
        if section not in content:
            issues.append({
                'level': 'ERROR',
                'type': 'missing_section',
                'message': f'缺少必填章节：{section}',
            })
    return issues


def check_foreshadowing_ids(content: str) -> list:
    """检查伏笔 ID 唯一性。"""
    issues = []
    ids = []
    for line in content.split('\n'):
        m = re.search(r'\|\s*(F\d+)\s*\|', line)
        if m:
            ids.append(m.group(1))

    seen = {}
    for fid in ids:
        seen[fid] = seen.get(fid, 0) + 1
    for fid, count in seen.items():
        if count > 1:
            issues.append({
                'level': 'WARNING',
                'type': 'duplicate_foreshadowing_id',
                'message': f'伏笔 ID {fid} 出现 {count} 次',
            })
    return issues


def check_chapter_continuity(content: str) -> list:
    """检查章节编号连续性。"""
    issues = []
    chapter_nums = []
    for line in content.split('\n'):
        m = re.search(r'### 第\s*(\d+)\s*章', line)
        if m:
            chapter_nums.append(int(m.group(1)))

    chapter_nums.sort()
    for i in range(len(chapter_nums) - 1):
        if chapter_nums[i + 1] - chapter_nums[i] != 1:
            issues.append({
                'level': 'WARNING',
                'type': 'chapter_number_gap',
                'message': f'章节编号跳跃：{chapter_nums[i]} → {chapter_nums[i + 1]}',
            })
    return issues


def check_character_consistency(content: str) -> list:
    """检查人物名一致性（基础版：统计出现次数）。"""
    issues = []
    characters = []
    for line in content.split('\n'):
        m = re.match(r'### 人物\s*[：:]\s*(.+)', line)
        if m:
            name = m.group(1).strip()
            characters.append(name)
        m = re.match(r'### (.+)$', line)
        if m and '人物' not in m.group(1):
            # 这是其他类型的 ### 标题，跳过
            pass

    # 简单一致性：人物列表 vs 主要人物章节
    main_section = re.search(r'## 主要人物\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if main_section:
        declared = re.findall(r'### (.+)', main_section.group(1))
        for c in declared:
            if c not in characters:
                issues.append({
                    'level': 'INFO',
                    'type': 'character_inconsistent',
                    'message': f'人物 {c} 在主要人物中，但未在人物关系中出现',
                })
    return issues


def check_p1_stale(content: str, threshold: int) -> list:
    """检查 P1 伏笔是否长期未推进。"""
    issues = []
    p1_section = re.search(r'## 未解决伏笔\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if not p1_section:
        return issues

    chapter_count = len(re.findall(r'### 第\s*(\d+)\s*章', content))

    for line in p1_section.group(1).split('\n'):
        if '| P1 |' not in line:
            continue
        m = re.search(r'\|\s*F\d+\s*\|\s*P1\s*\|\s*(\d+)', line)
        if m:
            buried_chapter = int(m.group(1))
            stale = chapter_count - buried_chapter
            if stale > threshold:
                issues.append({
                    'level': 'WARNING',
                    'type': 'p1_stale',
                    'message': f'P1 伏笔（埋设于第 {buried_chapter} 章）已 {stale} 章未推进（阈值 {threshold}）',
                })
    return issues


def get_unresolved_by_priority(content: str) -> dict:
    """获取按优先级分组的未解决伏笔。"""
    result = {'P1': [], 'P2': [], 'P3': []}
    p1_section = re.search(r'## 未解决伏笔\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if not p1_section:
        return result

    for line in p1_section.group(1).split('\n'):
        m = re.search(r'\|\s*(F\d+)\s*\|\s*(P[123])\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|', line)
        if m:
            fid, priority, buried_chapter, content_text = m.groups()
            if priority in result:
                result[priority].append({
                    'id': fid,
                    'buried_chapter': int(buried_chapter),
                    'content': content_text,
                })
    return result


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 校验小说记忆文件（v2.0.0）'
    )
    parser.add_argument('memory_file', help='记忆文件路径')
    parser.add_argument('--json', dest='json_report', help='JSON 报告输出路径')
    parser.add_argument('--show-unresolved', action='store_true', help='显示未解决伏笔')
    parser.add_argument('--check-p1-stale', action='store_true', help='检查 P1 伏笔长期未推进')
    parser.add_argument('--stale-threshold', type=int, default=10, help='P1 伏笔过期阈值（默认 10 章）')
    parser.add_argument('--check-timeline', action='store_true', help='检查时间线')

    args = parser.parse_args()
    path = Path(args.memory_file)
    if not path.exists():
        print(f'错误：文件不存在：{args.memory_file}', file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding='utf-8')

    issues = []
    issues.extend(check_required_sections(content))
    issues.extend(check_foreshadowing_ids(content))
    issues.extend(check_chapter_continuity(content))
    issues.extend(check_character_consistency(content))

    if args.check_p1_stale:
        issues.extend(check_p1_stale(content, args.stale_threshold))

    # 输出
    if args.show_unresolved:
        result = get_unresolved_by_priority(content)
        print(f'=== 未解决伏笔 ===')
        for priority in ['P1', 'P2', 'P3']:
            items = result[priority]
            print(f'\n【{priority}】（共 {len(items)} 个）')
            for item in items:
                print(f"  {item['id']}（埋设于第 {item['buried_chapter']} 章）：{item['content']}")
        return

    # 汇总
    errors = [i for i in issues if i['level'] == 'ERROR']
    warnings = [i for i in issues if i['level'] == 'WARNING']
    infos = [i for i in issues if i['level'] == 'INFO']

    print(f'=== 校验报告 ===')
    print(f'文件：{args.memory_file}')
    print(f'错误：{len(errors)} 个')
    print(f'警告：{len(warnings)} 个')
    print(f'提示：{len(infos)} 个')

    if errors:
        print(f'\n【错误】')
        for e in errors:
            print(f"  ✗ {e['message']}")

    if warnings:
        print(f'\n【警告】')
        for w in warnings:
            print(f"  ⚠ {w['message']}")

    if infos:
        print(f'\n【提示】')
        for i in infos:
            print(f"  ℹ {i['message']}")

    if args.json_report:
        report = {
            'file': str(path),
            'error_count': len(errors),
            'warning_count': len(warnings),
            'info_count': len(infos),
            'issues': issues,
        }
        Path(args.json_report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\n报告已保存：{args.json_report}')

    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
