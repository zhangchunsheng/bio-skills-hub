#!/usr/bin/env python3
"""
export-to-docx.py - 导出 Markdown 章节为 docx

v2.0.0 新增。封装中文出版排版规范（宋体/黑体/首行缩进/1.5 倍行距）。

依赖：
    pip install python-docx

使用：
    python3 export-to-docx.py --chapter chapter-008.md --output "第8章-标题.docx"
    python3 export-to-docx.py --chapter-dir novels/{slug}/chapters/ --output-dir novels/{slug}/docx/
"""

import argparse
import re
import sys
from pathlib import Path


def extract_title(content: str) -> tuple:
    """从 Markdown 提取章节标题与编号。"""
    m = re.search(r'^#\s*第\s*(\d+)\s*章[：:\s]*(.+)$', content, re.MULTILINE)
    if m:
        return int(m.group(1)), m.group(2).strip()
    m = re.search(r'^#\s*第\s*(\d+)\s*章\s*$', content, re.MULTILINE)
    if m:
        return int(m.group(1)), f'第{m.group(1)}章'
    return 0, '未命名章节'


def sanitize_filename(name: str) -> str:
    """清理文件名非法字符。"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def export_to_docx(chapter_path: Path, output_path: Path) -> dict:
    """导出单个章节为 docx。"""
    report = {'success': False, 'output': None, 'error': None}

    try:
        from docx import Document
        from docx.shared import Pt, Cm
        from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    except ImportError:
        report['error'] = '缺少依赖：python-docx。请运行 pip install python-docx'
        return report

    content = chapter_path.read_text(encoding='utf-8')
    chapter_num, title = extract_title(content)

    doc = Document()

    # 默认样式：宋体 12pt
    style = doc.styles['Normal']
    style.font.name = '宋体'
    style.font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.first_line_indent = Cm(0.74)

    # 一级标题：黑体 22pt 居中
    h1 = doc.styles['Heading 1']
    h1.font.name = '黑体'
    h1.font.size = Pt(22)
    h1.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # 写入标题
    doc.add_heading(f'第 {chapter_num} 章 {title}', level=1)

    # 写入正文（去除原 Markdown 标题行）
    lines = content.split('\n')
    in_title = True
    for line in lines:
        if in_title and re.match(r'^#\s*第\s*\d+\s*章', line):
            in_title = False
            continue
        if not in_title and line.strip():
            # 处理 Markdown 标记
            line = re.sub(r'^\s*#{1,6}\s*', '', line)
            line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            line = re.sub(r'\*(.+?)\*', r'\1', line)
            doc.add_paragraph(line)

    # 保存
    if not output_path.suffix:
        output_path = output_path.with_suffix('.docx')
    doc.save(str(output_path))
    report['success'] = True
    report['output'] = str(output_path)
    return report


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 导出 docx（v2.0.0）'
    )
    parser.add_argument('--chapter', help='章节文件路径（单个）')
    parser.add_argument('--chapter-dir', help='章节目录（批量）')
    parser.add_argument('--output', help='输出文件路径（单个）')
    parser.add_argument('--output-dir', help='输出目录（批量）')
    parser.add_argument('--title', help='章节标题（可选）')

    args = parser.parse_args()

    if args.chapter:
        chapter_path = Path(args.chapter)
        if not chapter_path.exists():
            print(f'错误：章节文件不存在：{args.chapter}', file=sys.stderr)
            sys.exit(1)

        if args.output:
            output_path = Path(args.output)
        else:
            content = chapter_path.read_text(encoding='utf-8')
            chapter_num, title = extract_title(content)
            safe_title = sanitize_filename(title)
            output_path = chapter_path.parent / f'第{chapter_num}章-{safe_title}.docx'

        report = export_to_docx(chapter_path, output_path)
        if report['success']:
            print(f'✓ 已导出：{report["output"]}')
        else:
            print(f'✗ 失败：{report["error"]}', file=sys.stderr)
            sys.exit(1)

    elif args.chapter_dir:
        chapter_dir = Path(args.chapter_dir)
        output_dir = Path(args.output_dir) if args.output_dir else chapter_dir.parent / 'docx'
        output_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        for chapter_path in sorted(chapter_dir.glob('chapter-*.md')):
            content = chapter_path.read_text(encoding='utf-8')
            chapter_num, title = extract_title(content)
            safe_title = sanitize_filename(title)
            output_path = output_dir / f'第{chapter_num}章-{safe_title}.docx'
            report = export_to_docx(chapter_path, output_path)
            if report['success']:
                print(f'✓ {output_path.name}')
                success_count += 1
            else:
                print(f'✗ {chapter_path.name}：{report["error"]}')

        print(f'\n完成：{success_count} 个文件已导出到 {output_dir}')

    else:
        print('错误：请提供 --chapter 或 --chapter-dir', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
