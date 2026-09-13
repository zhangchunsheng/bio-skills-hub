#!/usr/bin/env python3
"""
style-dna-extract.py - 风格 DNA 提取

v2.0.0 新增。从开篇 1000 字提取风格指纹，输出 JSON。

使用：
    python3 style-dna-extract.py --chapter chapter-001.md --output style-dna.json
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


# 常见停用词
STOPWORDS = set([
    '的', '了', '是', '在', '和', '与', '或', '但', '而', '及', '等',
    '我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们',
    '这', '那', '这个', '那个', '这些', '那些',
    '有', '没有', '没', '会', '可以', '能够', '要', '应该',
    '一', '一个', '一些', '一种',
    '不', '也', '都', '就', '还', '才', '只',
    '把', '被', '从', '到', '为', '为了',
])


def split_sentences(text: str) -> list:
    """分割句子。"""
    text = re.sub(r'\s+', '', text)
    sentences = re.split(r'[。！？!?]', text)
    return [s for s in sentences if s.strip()]


def avg_sentence_length(sentences: list) -> float:
    """平均句长（字）。"""
    if not sentences:
        return 0
    return sum(len(s) for s in sentences) / len(sentences)


def sentence_length_distribution(sentences: list) -> dict:
    """句长分布。"""
    if not sentences:
        return {'short': 0, 'medium': 0, 'long': 0}

    short_count = sum(1 for s in sentences if len(s) <= 10)
    medium_count = sum(1 for s in sentences if 10 < len(s) <= 25)
    long_count = sum(1 for s in sentences if len(s) > 25)

    total = len(sentences)
    return {
        'short': round(short_count / total, 3),
        'medium': round(medium_count / total, 3),
        'long': round(long_count / total, 3),
    }


def top_words(text: str, top_n: int = 50) -> list:
    """词频 Top N（中文按字符统计）。"""
    chars = [c for c in text if c not in STOPWORDS and not re.match(r'[\s\p{P}]', c)]
    counter = Counter(chars)
    return [{'word': w, 'count': c} for w, c in counter.most_common(top_n)]


def count_dialogue(text: str) -> tuple:
    """统计对话比例。"""
    # 中文对话：「」"" 或者 —— 前缀
    dialogue_pattern = r'「[^」]+」|""[^""]+""'
    dialogues = re.findall(dialogue_pattern, text)
    dialogue_chars = sum(len(d) for d in dialogues)
    total_chars = len(text)
    ratio = dialogue_chars / total_chars if total_chars > 0 else 0
    return ratio, len(dialogues)


def detect_metaphor(text: str) -> int:
    """检测比喻（粗略估算）。"""
    patterns = [
        r'像.{1,8}(的|地)',
        r'如.{1,8}(一般|一样)',
        r'仿佛',
        r'好似',
        r'如同',
        r'犹如',
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text))
    return count


def detect_passive(text: str) -> int:
    """检测被动句。"""
    return len(re.findall(r'被.{2,8}', text))


def detect_dash(text: str) -> int:
    """检测破折号。"""
    return len(re.findall(r'——', text))


def detect_parallelism(text: str) -> int:
    """检测排比（连续三句相同结构）。"""
    sentences = split_sentences(text)
    pattern = re.compile(r'(.{2,8}?。)[\s]*(.{2,8}?。)[\s]*(.{2,8}?。)')
    matches = pattern.findall(text)
    return len(matches)


def detect_emotional_label(text: str) -> int:
    """检测情绪标签直白化。"""
    patterns = [
        r'非常.{1,4}',
        r'十分.{1,4}',
        r'极其.{1,4}',
        r'深深地',
        r'陷入了?',
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text))
    return count


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 风格 DNA 提取（v2.0.0）'
    )
    parser.add_argument('--chapter', required=True, help='章节文件路径')
    parser.add_argument('--output', help='输出 JSON 路径')
    parser.add_argument('--limit', type=int, default=1000, help='提取字数（默认 1000）')

    args = parser.parse_args()
    chapter_path = Path(args.chapter)
    if not chapter_path.exists():
        print(f'错误：章节文件不存在：{args.chapter}', file=sys.stderr)
        sys.exit(1)

    content = chapter_path.read_text(encoding='utf-8')
    sample = content[:args.limit]

    sentences = split_sentences(sample)
    avg_len = avg_sentence_length(sentences)
    dist = sentence_length_distribution(sentences)
    words = top_words(sample, top_n=50)
    dialogue_ratio, dialogue_count = count_dialogue(sample)

    rhetoric_density = {
        'metaphor': detect_metaphor(sample),
        'passive': detect_passive(sample),
        'dash': detect_dash(sample),
        'parallelism': detect_parallelism(sample),
        'emotional_label': detect_emotional_label(sample),
    }

    dna = {
        'chapter': str(chapter_path),
        'sample_length': len(sample),
        'stats': {
            'avg_sentence_length': round(avg_len, 2),
            'sentence_length_distribution': dist,
            'top_50_words': words,
            'dialogue_ratio': round(dialogue_ratio, 3),
            'dialogue_count': dialogue_count,
            'rhetoric_density': rhetoric_density,
        },
    }

    print(f'=== 风格 DNA 提取 ===')
    print(f'采样长度：{len(sample)} 字')
    print(f'平均句长：{avg_len:.2f} 字')
    print(f'句长分布：短 {dist["short"]:.1%} / 中 {dist["medium"]:.1%} / 长 {dist["long"]:.1%}')
    print(f'对话比例：{dialogue_ratio:.1%}（{dialogue_count} 处）')
    print(f'\n修辞密度：')
    for k, v in rhetoric_density.items():
        print(f'  {k}: {v}')

    if args.output:
        Path(args.output).write_text(
            json.dumps(dna, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\nDNA 已保存：{args.output}')


if __name__ == '__main__':
    main()
