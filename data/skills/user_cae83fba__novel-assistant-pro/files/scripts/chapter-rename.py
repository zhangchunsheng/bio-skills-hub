#!/usr/bin/env python3
"""
chapter-rename.py - 章节命名互转

v2.0.0 新增。在 `chapter-NNN.md` 与 `第N章-标题.docx` 之间互转。

使用：
    # 单个文件
    python3 chapter-rename.py --input chapter-001.md --output "第1章-港口爆炸.docx" --direction md-to-docx
    python3 chapter-rename.py --input "第1章-港口爆炸.docx" --output chapter-001.md --direction docx-to-md

    # 批量
    python3 chapter-rename.py --batch novels/{slug}/chapters/ --direction md-to-docx --output-dir novels/{slug}/docx/
"""

import argparse
import re
import shutil
import sys
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """清理文件名非法字符。"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def extract_chapter_info(filename: str) -> tuple:
    """从文件名提取章节信息。"""
    # chapter-001.md
    m = re.match(r'chapter-(\d+)\.md$', filename)
    if m:
        return int(m.group(1)), None

    # 第1章-标题.docx
    m = re.match(r'第(\d+)章-(.+?)\.docx$', filename)
    if m:
        return int(m.group(1)), m.group(2)

    return None, None


def md_to_docx_name(chapter_num: int, title: str = None) -> str:
    """转换为 docx 命名。"""
    if title:
        return f'第{chapter_num}章-{sanitize_filename(title)}.docx'
    return f'第{chapter_num}章.docx'


def docx_to_md_name(chapter_num: int) -> str:
    """转换为 md 命名。"""
    return f'chapter-{chapter_num:03d}.md'


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 章节命名互转（v2.0.0）'
    )
    parser.add_argument('--input', help='输入文件')
    parser.add_argument('--output', help='输出文件')
    parser.add_argument('--batch', help='批量输入目录')
    parser.add_argument('--output-dir', help='批量输出目录')
    parser.add_argument('--direction', choices=['md-to-docx', 'docx-to-md'], required=True)
    parser.add_argument('--dry-run', action='store_true')

    args = parser.parse_args()

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f'错误：输入文件不存在：{args.input}', file=sys.stderr)
            sys.exit(1)

        chapter_num, title = extract_chapter_info(input_path.name)
        if chapter_num is None:
            print(f'错误：无法识别章节编号：{input_path.name}', file=sys.stderr)
            sys.exit(1)

        if args.direction == 'md-to-docx':
            output_name = md_to_docx_name(chapter_num, title)
        else:
            output_name = docx_to_md_name(chapter_num)

        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.parent / output_name

        if args.dry_run:
            print(f'[dry-run] {input_path.name} → {output_path.name}')
        else:
            shutil.copy2(input_path, output_path)
            print(f'✓ {input_path.name} → {output_path.name}')

    elif args.batch:
        batch_dir = Path(args.batch)
        if not batch_dir.exists():
            print(f'错误：批量目录不存在：{args.batch}', file=sys.stderr)
            sys.exit(1)

        output_dir = Path(args.output_dir) if args.output_dir else batch_dir.parent / ('docx' if args.direction == 'md-to-docx' else 'chapters')
        if not args.dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        for input_path in sorted(batch_dir.iterdir()):
            chapter_num, title = extract_chapter_info(input_path.name)
            if chapter_num is None:
                continue

            if args.direction == 'md-to-docx':
                output_name = md_to_docx_name(chapter_num, title)
            else:
                output_name = docx_to_md_name(chapter_num)

            output_path = output_dir / output_name
            if args.dry_run:
                print(f'[dry-run] {input_path.name} → {output_name}')
            else:
                shutil.copy2(input_path, output_path)
                print(f'✓ {input_path.name} → {output_name}')
                success_count += 1

        print(f'\n完成：{success_count} 个文件')
    else:
        print('错误：请提供 --input 或 --batch', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
