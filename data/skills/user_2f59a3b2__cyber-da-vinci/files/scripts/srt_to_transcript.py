#!/usr/bin/env python3
"""
srt_to_transcript.py - 将SRT/VTT字幕文件清洗为可阅读的纯文本transcript
用法: python3 srt_to_transcript.py <input.srt> [output.txt]

功能:
- 去除时间戳（00:00:00,000 --> 00:00:03,500）
- 去除字幕序号
- 去除HTML标签（<i>, <b>, <font>等）
- 合并连续重复行（字幕常见的逐字显示重叠）
- 智能分段（根据停顿重新分段，而非每行换行）
- 输出可直接阅读的干净文本
"""

import re
import sys
from pathlib import Path


def remove_html_tags(text: str) -> str:
    """去除HTML/XML标签"""
    return re.sub(r'<[^>]+>', '', text)


def is_timestamp_line(line: str) -> bool:
    """判断是否为时间戳行（SRT: 00:00:00,000 --> 00:00:03,500 或 VTT: 00:00:00.000 --> 00:00:03.500）"""
    return bool(re.match(r'^\d{1,2}:\d{2}:\d{2}[,\.]\d{3}\s*-->\s*\d{1,2}:\d{2}:\d{2}[,\.]\d{3}', line.strip()))


def is_sequence_number(line: str) -> bool:
    """判断是否为纯数字序号行"""
    return bool(re.match(r'^\d+\s*$', line.strip()))


def is_webvtt_header(line: str) -> bool:
    """判断是否为VTT文件头"""
    return line.strip().startswith('WEBVTT') or line.strip().startswith('NOTE')


def parse_srt_vtt(content: str) -> list[str]:
    """解析SRT/VTT文件，提取所有文本行"""
    lines = content.split('\n')
    text_lines = []
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行
        if not line:
            continue
        
        # 跳过VTT文件头
        if is_webvtt_header(line):
            continue
        
        # 跳过时间戳行
        if is_timestamp_line(line):
            continue
        
        # 跳过序号行
        if is_sequence_number(line):
            continue
        
        # 清理HTML标签
        line = remove_html_tags(line)
        
        # 清理特殊字符
        line = line.replace('\u200b', '')  # 零宽空格
        line = line.replace('\ufeff', '')  # BOM
        line = re.sub(r'\s+', ' ', line).strip()  # 规范化空白
        
        if line:
            text_lines.append(line)
    
    return text_lines


def remove_consecutive_duplicates(lines: list[str]) -> list[str]:
    """
    去除连续重复行（字幕逐字显示时常见）
    例如: ["你好", "你好，世界", "你好，世界！"] → ["你好，世界！"]
    策略：如果当前行是前一行的前缀，保留更长的那行
    """
    if not lines:
        return lines
    
    result = []
    i = 0
    
    while i < len(lines):
        current = lines[i]
        
        # 向前看，找到不再是当前行前缀关系的行
        j = i + 1
        while j < len(lines) and (
            lines[j].startswith(current) or 
            current.startswith(lines[j]) or
            lines[j] == current
        ):
            # 保留更长的那个
            if len(lines[j]) > len(current):
                current = lines[j]
            j += 1
        
        result.append(current)
        i = j
    
    return result


def merge_into_paragraphs(lines: list[str], min_sentence_len: int = 20) -> str:
    """
    将字幕行合并为自然段落
    
    策略：
    - 以句号/问号/感叹号结尾 → 段落结束，换行
    - 短行（<min_sentence_len字符）通常是不完整句子 → 与下一行合并
    - 长行 → 可能是完整句子，视情况处理
    """
    if not lines:
        return ""
    
    paragraphs = []
    current_para = []
    
    for line in lines:
        current_para.append(line)
        
        # 判断是否应该在此处结束段落
        # 以句子终止符结尾，且当前段落累积内容足够长
        combined = ' '.join(current_para)
        ends_with_punctuation = bool(re.search(r'[。！？.!?…]$', line))
        
        if ends_with_punctuation and len(combined) >= min_sentence_len:
            paragraphs.append(combined)
            current_para = []
        elif len(combined) > 200:  # 防止段落过长
            paragraphs.append(combined)
            current_para = []
    
    # 处理剩余内容
    if current_para:
        paragraphs.append(' '.join(current_para))
    
    return '\n\n'.join(paragraphs)


def convert_subtitle_to_transcript(input_path: str, output_path: str = None) -> str:
    """
    主函数：将字幕文件转换为transcript
    
    Returns:
        输出文件路径
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"[ERROR] 文件不存在: {input_path}")
        sys.exit(1)
    
    # 确定输出路径
    if output_path is None:
        output_path = str(input_file.with_suffix('.txt'))
    
    # 读取文件（尝试多种编码）
    content = None
    for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'latin-1']:
        try:
            content = input_file.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print(f"[ERROR] 无法读取文件（编码问题）: {input_path}")
        sys.exit(1)
    
    print(f"[INFO] 读取文件: {input_path} ({len(content)} 字符)")
    
    # Step 1: 解析字幕，提取文本行
    lines = parse_srt_vtt(content)
    print(f"[INFO] 提取文本行: {len(lines)} 行")
    
    # Step 2: 去除连续重复
    lines_deduped = remove_consecutive_duplicates(lines)
    removed = len(lines) - len(lines_deduped)
    print(f"[INFO] 去除重复行: {removed} 行 → 剩余 {len(lines_deduped)} 行")
    
    # Step 3: 合并为段落
    transcript = merge_into_paragraphs(lines_deduped)
    
    # Step 4: 写出
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(transcript, encoding='utf-8')
    
    print(f"[✓] 清洗完成: {output_path}")
    print(f"[INFO] 输出字符数: {len(transcript)}")
    print(f"[INFO] 输出段落数: {transcript.count(chr(10)*2) + 1}")
    
    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 srt_to_transcript.py <input.srt> [output.txt]")
        print("")
        print("示例:")
        print("  python3 srt_to_transcript.py video.srt")
        print("  python3 srt_to_transcript.py video.srt ./sources/transcripts/charlie_munger_talk.txt")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = convert_subtitle_to_transcript(input_path, output_path)
    print(f"\n完成！可阅读的transcript已保存至: {result}")
