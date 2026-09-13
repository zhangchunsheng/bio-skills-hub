#!/usr/bin/env python3
"""
relationship-graph.py - 人物关系 mermaid 图生成

v2.0.0 新增。基于人物关系，生成 mermaid 图。

使用：
    python3 relationship-graph.py --memory memory/novels/{slug}.md --output relationships.md
"""

import argparse
import re
import sys
from pathlib import Path


def extract_relationships(memory: str) -> list:
    """提取人物关系。"""
    section = re.search(r'## 人物关系\n(.*?)(?=\n## |\Z)', memory, re.DOTALL)
    if not section:
        return []
    relationships = []
    for line in section.group(1).split('\n'):
        m = re.match(r'-\s*(.+?)\s*[与和]\s*(.+?)\s*[：:](.+)', line)
        if m:
            relationships.append({
                'from': m.group(1).strip(),
                'to': m.group(2).strip(),
                'relation': m.group(3).strip(),
            })
    return relationships


def generate_mermaid(relationships: list) -> str:
    """生成 mermaid 图。"""
    lines = ['```mermaid', 'graph LR']
    nodes = set()
    for r in relationships:
        a, b = r['from'], r['to']
        nodes.add(a)
        nodes.add(b)

    for node in nodes:
        lines.append(f'  {node}["{node}"]')

    for r in relationships:
        relation = r['relation'].replace('"', "'")
        lines.append(f'  {r["from"]} -->|{relation}| {r["to"]}')

    lines.append('```')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 人物关系图生成（v2.0.0）'
    )
    parser.add_argument('--memory', required=True, help='记忆文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')

    args = parser.parse_args()
    memory_path = Path(args.memory)
    if not memory_path.exists():
        print(f'错误：记忆文件不存在：{args.memory}', file=sys.stderr)
        sys.exit(1)

    memory = memory_path.read_text(encoding='utf-8')
    relationships = extract_relationships(memory)

    if not relationships:
        print('未找到人物关系（"## 人物关系" 章节为空）')
        return

    mermaid = generate_mermaid(relationships)
    Path(args.output).write_text(mermaid, encoding='utf-8')

    print(f'=== 人物关系图 ===')
    print(f'关系数：{len(relationships)}')
    print(f'节点数：{len(set(r["from"] for r in relationships) | set(r["to"] for r in relationships))}')
    print(f'\n已生成 mermaid 图：{args.output}')


if __name__ == '__main__':
    main()
