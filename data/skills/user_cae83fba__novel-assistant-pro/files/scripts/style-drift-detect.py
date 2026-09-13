#!/usr/bin/env python3
"""
style-drift-detect.py - 风格漂移检测

v2.0.0 新增。比对当前章节与风格 DNA 的差异，输出漂移度。

使用：
    python3 style-drift-detect.py --style-dna style-dna.json --chapter chapter-008.md
"""

import argparse
import json
import sys
from pathlib import Path


def load_dna(dna_path: Path) -> dict:
    """加载风格 DNA JSON。"""
    return json.loads(dna_path.read_text(encoding='utf-8'))


def compute_drift(dna: dict, chapter_content: str) -> dict:
    """计算漂移度。"""
    # 简化实现：直接复用 style-dna-extract 的统计逻辑
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from style_dna_extract import (
        split_sentences, avg_sentence_length, sentence_length_distribution,
        top_words, count_dialogue, detect_metaphor, detect_passive,
        detect_dash, detect_parallelism, detect_emotional_label
    )

    sample = chapter_content[:1000]
    sentences = split_sentences(sample)

    new_stats = {
        'avg_sentence_length': avg_sentence_length(sentences),
        'sentence_length_distribution': sentence_length_distribution(sentences),
        'top_50_words': [w['word'] for w in top_words(sample, 50)],
        'dialogue_ratio': count_dialogue(sample)[0],
        'rhetoric_density': {
            'metaphor': detect_metaphor(sample),
            'passive': detect_passive(sample),
            'dash': detect_dash(sample),
            'parallelism': detect_parallelism(sample),
            'emotional_label': detect_emotional_label(sample),
        },
    }

    base_stats = dna['stats']

    # 计算各维度漂移
    drift_components = {}

    # 句长漂移
    len_diff = abs(new_stats['avg_sentence_length'] - base_stats['avg_sentence_length'])
    drift_components['sentence_length'] = min(len_diff * 5, 100)

    # 词频重合率
    base_words = set(w['word'] for w in base_stats.get('top_50_words', []))
    new_words = set(new_stats['top_50_words'])
    if base_words:
        overlap = len(base_words & new_words) / len(base_words)
    else:
        overlap = 1.0
    drift_components['vocabulary'] = round((1 - overlap) * 100, 1)

    # 对话比例漂移
    dia_diff = abs(new_stats['dialogue_ratio'] - base_stats['dialogue_ratio'])
    drift_components['dialogue'] = round(dia_diff * 200, 1)

    # 修辞密度漂移
    base_rhetoric = base_stats.get('rhetoric_density', {})
    new_rhetoric = new_stats['rhetoric_density']
    rhetoric_diff = sum(
        abs(new_rhetoric.get(k, 0) - base_rhetoric.get(k, 0))
        for k in ['metaphor', 'passive', 'dash', 'parallelism', 'emotional_label']
    )
    drift_components['rhetoric'] = min(rhetoric_diff * 2, 100)

    # 加权总漂移度
    total_drift = (
        0.4 * drift_components['sentence_length'] +
        0.3 * drift_components['vocabulary'] +
        0.2 * drift_components['rhetoric'] +
        0.1 * drift_components['dialogue']
    )

    return {
        'total_drift': round(total_drift, 1),
        'components': drift_components,
        'new_stats': new_stats,
    }


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 风格漂移检测（v2.0.0）'
    )
    parser.add_argument('--style-dna', required=True, help='风格 DNA JSON 路径')
    parser.add_argument('--chapter', required=True, help='章节文件路径')
    parser.add_argument('--output', help='报告输出路径')

    args = parser.parse_args()
    dna_path = Path(args.style_dna)
    chapter_path = Path(args.chapter)

    if not dna_path.exists():
        print(f'错误：DNA 文件不存在：{args.style_dna}', file=sys.stderr)
        sys.exit(1)
    if not chapter_path.exists():
        print(f'错误：章节文件不存在：{args.chapter}', file=sys.stderr)
        sys.exit(1)

    dna = load_dna(dna_path)
    chapter_content = chapter_path.read_text(encoding='utf-8')

    report = compute_drift(dna, chapter_content)

    print(f'=== 风格漂移检测（第 {chapter_path.stem} 章）===')
    print(f'\n各维度漂移：')
    for k, v in report['components'].items():
        print(f'  {k}: {v}/100')

    print(f'\n总漂移度：{report["total_drift"]}/100')

    if report['total_drift'] < 10:
        print('判定：完全一致')
    elif report['total_drift'] < 20:
        print('判定：轻微漂移（合格）')
    elif report['total_drift'] < 40:
        print('判定：中度漂移（建议调整）')
    else:
        print('判定：严重漂移（必须改写）')

    if args.output:
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\n报告已保存：{args.output}')


if __name__ == '__main__':
    main()
