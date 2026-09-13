#!/usr/bin/env python3
"""
小说记忆文件压缩脚本 v2.0.0

功能：
1. 合并早期章节概要为早期概要块
2. 清理已解决的伏笔
3. 精简人物描述
4. 控制文件总字数

兼容：
- ## 章节概要 / ## 剧情概要 / ## 章节大纲
- ## 人物关系 / ## 人物关系图
- 表格式伏笔追踪 / 列表式伏笔追踪

使用：
    python3 compress_novel_memory.py <memory_file.md> [--keep-chapters N]
    python3 compress_novel_memory.py <memory_file.md> --dry-run
    python3 compress_novel_memory.py <memory_file.md> --report report.json
    python3 compress_novel_memory.py <memory_file.md> --keep-backups 5
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


SECTION_ALIASES = {
    'basic': ['## 基本信息', '## 基础信息', '## Basic Info'],
    'world': ['## 世界观', '## 世界观规则', '## World'],
    'characters': ['## 主要人物', '## 人物设定', '## Characters'],
    'relations': ['## 人物关系', '## 人物关系图', '## 关系', '## Relations'],
    'chapters': ['## 章节概要', '## 剧情概要', '## 章节大纲', '## Chapters'],
    'foreshadowing': ['## 伏笔追踪', '## 未解决伏笔', '## Foreshadowing'],
    'timeline': ['## 时间线', '## Timeline'],
}


def find_section(content: str, name: str) -> str:
    """按别名表匹配并截取第一个匹配的章节。"""
    aliases = SECTION_ALIASES.get(name, [])
    for alias in aliases:
        pattern = re.escape(alias) + r'\n(.*?)(?=\n## |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
    return ''


def parse_memory_file(content: str) -> dict:
    """解析记忆文件为结构化数据。"""
    sections = {key: find_section(content, key) for key in SECTION_ALIASES.keys()}
    chapters_text = sections['chapters']
    if chapters_text:
        chapter_pattern = r'### 第(\d+)章[：:\s](.*?)(?=### 第|\Z)'
        sections['chapters_list'] = [
            {'num': int(m.group(1)), 'content': m.group(2).strip()[:200]}
            for m in re.finditer(chapter_pattern, chapters_text, re.DOTALL)
        ]
    else:
        sections['chapters_list'] = []
    return sections


def compress_chapters(chapters: list, keep_recent: int) -> tuple:
    """压缩章节：保留近期章节，早期章节合并为概要。"""
    if len(chapters) <= keep_recent:
        return chapters, None

    early_chapters = chapters[:-keep_recent]
    recent_chapters = chapters[-keep_recent:]

    early_summary_lines = [f"### 早期章节概要（第 1-{early_chapters[-1]['num']} 章）", ""]
    for ch in early_chapters[:10]:
        first_sentence = ch['content'].split('。')[0][:50]
        if first_sentence:
            early_summary_lines.append(f"- 第 {ch['num']} 章：{first_sentence}")
    if len(early_chapters) > 10:
        early_summary_lines.append(f"- ……共 {len(early_chapters)} 章早期内容已合并")
    early_summary = '\n'.join(early_summary_lines)

    return recent_chapters, early_summary


def compress_foreshadowing(foreshadowing: str) -> tuple:
    """清理已解决的伏笔（兼容表格与列表两种写法）。"""
    if not foreshadowing:
        return '', 0

    lines = foreshadowing.split('\n')
    unresolved = []
    resolved_count = 0

    for line in lines:
        stripped = line.strip()
        # 表格式：| F001 | ... | 已回收 | ... |
        if '| F0' in line or '| F1' in line or '| F2' in line:
            if '已回收' in line or '已解决' in line or '废弃' in line:
                resolved_count += 1
            else:
                unresolved.append(line)
        # 列表式：- [x] 已解决 / - [ ] 未解决
        elif stripped.startswith('- [x]') or stripped.startswith('* [x]'):
            resolved_count += 1
        elif stripped.startswith('- [ ]') or stripped.startswith('* [ ]'):
            unresolved.append(line)
        else:
            unresolved.append(line)

    return '\n'.join(unresolved), resolved_count


def rebuild_memory_file(title: str, sections: dict, early_summary: str = None) -> str:
    """重建记忆文件。"""
    output_lines = [f"# 《{title}》记忆文件", ""]

    if sections.get('basic'):
        output_lines += ["## 基本信息", sections['basic'], ""]

    if sections.get('world'):
        output_lines += ["## 世界观", sections['world'], ""]

    if sections.get('characters'):
        output_lines += ["## 主要人物", sections['characters'], ""]

    if sections.get('relations'):
        output_lines += ["## 人物关系", sections['relations'], ""]

    output_lines.append("## 章节概要")
    output_lines.append("")
    if early_summary:
        output_lines += [early_summary, ""]
    for ch in sections.get('chapters_list', []):
        output_lines.append(f"### 第 {ch['num']} 章")
        output_lines.append(ch['content'])
        output_lines.append("")

    if sections.get('foreshadowing'):
        compressed, _ = compress_foreshadowing(sections['foreshadowing'])
        if compressed:
            output_lines += ["## 伏笔追踪", compressed, ""]

    if sections.get('timeline'):
        output_lines += ["## 时间线", sections['timeline']]

    return '\n'.join(output_lines).rstrip() + '\n'


def extract_title(content: str) -> str:
    """从文件中提取小说名。兼容多种标题写法。

    优先策略：
    1. # 《书名》记忆文件 / # 《书名》
    2. # 书名 记忆文件
    3. # 书名 + 换行（取首行第一个非空词组）
    4. 回退到 "未知小说"
    """
    lines = [ln.strip() for ln in content.split('\n') if ln.strip()]
    if not lines:
        return "未知小说"

    first_line = lines[0]

    # 策略 1：含《》的书名直接取《》内
    bracket_match = re.search(r'《(.+?)》', first_line)
    if bracket_match:
        title = bracket_match.group(1).strip()
        if title and not title.endswith('记忆文件'):
            return title

    # 策略 2：# 书名 记忆文件
    m = re.match(r'^#\s*(.+?)\s*记忆文件\s*$', first_line)
    if m:
        return m.group(1).strip()

    # 策略 3：# 书名（取首行去掉 # 与尾部"记忆文件："等修饰）
    m = re.match(r'^#\s*(.+?)$', first_line)
    if m:
        raw = m.group(1).strip()
        # 移除"记忆文件"等修饰词
        for suffix in ['记忆文件', '记忆', 'MEMO', 'memo']:
            if raw.endswith(suffix):
                raw = raw[:-len(suffix)].strip()
        if raw:
            return raw

    return "未知小说"


def create_timestamp_backup(path: Path, keep_backups: int) -> Path:
    """创建时间戳备份，并清理旧备份。"""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = path.with_suffix(f'.md.backup-{timestamp}')
    backup_path.write_text(path.read_text(encoding='utf-8'), encoding='utf-8')

    # 清理超过保留数量的旧备份
    backups = sorted(path.parent.glob(f'{path.stem}.md.backup-*'))
    if keep_backups > 0:
        for old_backup in backups[:-keep_backups]:
            if old_backup != backup_path:
                old_backup.unlink()
    else:
        for old_backup in backups:
            old_backup.unlink()

    return backup_path


def compress_memory_file(file_path: str, keep_chapters: int = 15,
                         keep_backups: int = 5, dry_run: bool = False) -> dict:
    """主压缩函数。返回结构化报告。"""
    path = Path(file_path)
    report = {
        'file': str(path),
        'success': False,
        'dry_run': dry_run,
        'original_size': 0,
        'new_size': 0,
        'compression_ratio': 0.0,
        'chapter_count': 0,
        'merged_early_chapters': 0,
        'cleaned_resolved_foreshadowing': 0,
        'backup_path': None,
        'error': None,
    }

    if not path.exists():
        report['error'] = f'文件不存在：{file_path}'
        return report

    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        report['error'] = f'读取失败：{e}'
        return report

    report['original_size'] = len(content)
    title = extract_title(content)
    sections = parse_memory_file(content)
    chapter_count = len(sections.get('chapters_list', []))
    report['chapter_count'] = chapter_count

    recent_chapters, early_summary = compress_chapters(sections.get('chapters_list', []), keep_chapters)
    sections['chapters_list'] = recent_chapters
    if early_summary:
        report['merged_early_chapters'] = chapter_count - keep_chapters

    new_content = rebuild_memory_file(title, sections, early_summary)
    report['new_size'] = len(new_content)
    if report['original_size'] > 0:
        report['compression_ratio'] = round((1 - report['new_size'] / report['original_size']) * 100, 1)

    if dry_run:
        report['success'] = True
        report['note'] = 'dry-run 模式，未实际写入'
        return report

    try:
        backup_path = create_timestamp_backup(path, keep_backups)
        report['backup_path'] = str(backup_path)
        path.write_text(new_content, encoding='utf-8')
        report['success'] = True
    except Exception as e:
        report['error'] = f'写入失败：{e}'
        # 回滚：从备份恢复
        if report['backup_path']:
            try:
                Path(report['backup_path']).rename(path)
                report['error'] += f'（已从备份 {report["backup_path"]} 回滚）'
            except Exception as rollback_error:
                report['error'] += f'（回滚失败：{rollback_error}）'

    return report


def main():
    parser = argparse.ArgumentParser(
        description='小说记忆文件压缩脚本（v2.0.0）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 compress_novel_memory.py memory/novels/my-novel.md
  python3 compress_novel_memory.py memory/novels/my-novel.md --keep-chapters 20
  python3 compress_novel_memory.py memory/novels/my-novel.md --dry-run
  python3 compress_novel_memory.py memory/novels/my-novel.md --report report.json
        """,
    )
    parser.add_argument('memory_file', help='记忆文件路径')
    parser.add_argument('--keep-chapters', type=int, default=15, help='保留最近 N 章（默认 15）')
    parser.add_argument('--keep-backups', type=int, default=5, help='保留 N 个时间戳备份（默认 5，0 表示不保留）')
    parser.add_argument('--dry-run', action='store_true', help='仅预览压缩效果，不实际写入')
    parser.add_argument('--report', type=str, default=None, help='输出 JSON 报告到指定文件')

    args = parser.parse_args()
    report = compress_memory_file(
        args.memory_file,
        keep_chapters=args.keep_chapters,
        keep_backups=args.keep_backups,
        dry_run=args.dry_run,
    )

    # 控制台输出
    print(f"正在压缩《{extract_title(Path(args.memory_file).read_text(encoding='utf-8'))}》记忆文件...")
    print(f"  原始大小：{report['original_size']} 字节")
    print(f"  章节数：{report['chapter_count']}")
    print(f"  压缩后大小：{report['new_size']} 字节")
    print(f"  压缩率：{report['compression_ratio']}%")
    if report['merged_early_chapters']:
        print(f"  合并了前 {report['merged_early_chapters']} 章为概要")
    if report['backup_path']:
        print(f"  原文件备份：{report['backup_path']}")
    if report['dry_run']:
        print("  [dry-run 模式，未实际写入]")
    if report['error']:
        print(f"  错误：{report['error']}", file=sys.stderr)
        sys.exit(1)

    # JSON 报告
    if args.report:
        report_path = Path(args.report)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  报告已保存：{args.report}")


if __name__ == '__main__':
    main()
