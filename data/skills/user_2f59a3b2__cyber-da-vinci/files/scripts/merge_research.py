#!/usr/bin/env python3
"""
merge_research.py - 汇总6个调研Agent的输出，生成Phase 1.5检查点摘要
用法: python3 merge_research.py <skill目录路径>

功能:
- 自动扫描 references/research/01-06.md 文件
- 统计每个文件的来源数量、一手/二手占比
- 提取关键发现（标题和首要观点）
- 识别文件间的矛盾点
- 输出Phase 1.5所需的Markdown格式摘要表格
"""

import re
import sys
from pathlib import Path
from datetime import datetime


# 调研文件配置
RESEARCH_FILES = {
    '01-writings.md': '著作',
    '02-conversations.md': '对话',
    '03-expression-dna.md': '表达DNA',
    '04-external-views.md': '他者视角',
    '05-decisions.md': '决策记录',
    '06-timeline.md': '时间线',
}


def count_sources(content: str) -> dict:
    """统计来源数量和一手/二手比例"""
    # 统计URL数量（粗略估计来源数量）
    urls = re.findall(r'https?://\S+', content)
    
    # 统计一手来源标记（常见标注方式）
    first_hand_patterns = [
        r'一手', r'first.hand', r'primary',
        r'\[著作\]', r'\[演讲\]', r'\[采访\]', r'\[本人\]',
        r'此人(?:写|说|表示|认为)',
        r'原文[:：]',
    ]
    second_hand_patterns = [
        r'二手', r'second.hand', r'secondary',
        r'\[转述\]', r'\[总结\]', r'\[分析\]',
        r'(?:他人|外部|评论)(?:说|认为|分析)',
        r'据(?:报道|称|说)',
    ]
    
    first_hand_count = sum(
        len(re.findall(p, content, re.IGNORECASE))
        for p in first_hand_patterns
    )
    second_hand_count = sum(
        len(re.findall(p, content, re.IGNORECASE))
        for p in second_hand_patterns
    )
    
    total_refs = len(urls)
    
    return {
        'urls': total_refs,
        'first_hand': first_hand_count,
        'second_hand': second_hand_count,
    }


def extract_key_findings(content: str, max_findings: int = 2) -> list[str]:
    """提取关键发现（取前几个一级或二级标题下的首句）"""
    findings = []
    
    # 查找标题后的第一个实质性句子
    heading_pattern = re.compile(r'^#{1,3}\s+(.+)$', re.MULTILINE)
    headings = list(heading_pattern.finditer(content))
    
    for i, match in enumerate(headings[:max_findings + 2]):
        heading_text = match.group(1).strip()
        
        # 跳过元信息类标题
        skip_headings = ['来源', '参考', '信息源', '注意', '调研目标', '概述']
        if any(skip in heading_text for skip in skip_headings):
            continue
        
        # 找标题后的第一个非空行
        pos = match.end()
        remaining = content[pos:]
        lines = remaining.split('\n')
        
        for line in lines[:10]:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-') and len(line) > 15:
                # 截取前50字
                finding = line[:50] + ('...' if len(line) > 50 else '')
                findings.append(f"**{heading_text}**: {finding}")
                break
        
        if len(findings) >= max_findings:
            break
    
    # 如果没找到，尝试提取前N个bullet points
    if not findings:
        bullets = re.findall(r'^[-*]\s+(.{20,80})', content, re.MULTILINE)
        findings = [b[:60] + '...' if len(b) > 60 else b for b in bullets[:max_findings]]
    
    return findings if findings else ['（未提取到关键发现，请手动检查文件）']


def check_timeline_recency(content: str) -> str:
    """检查时间线文件是否包含近12个月的信息"""
    current_year = datetime.now().year
    
    # 查找最近年份的提及
    years_found = re.findall(r'20\d{2}', content)
    if not years_found:
        return '无年份信息'
    
    max_year = max(int(y) for y in years_found)
    
    if max_year >= current_year:
        return f'✓ 含{current_year}年动态'
    elif max_year >= current_year - 1:
        return f'含{max_year}年动态（较新）'
    else:
        return f'⚠️ 最新仅至{max_year}年（可能过时）'


def detect_contradictions(research_dir: Path, files_content: dict) -> list[str]:
    """简单检测文件间可能的矛盾点（基于关键词对比）"""
    contradictions = []
    
    # 提取各文件的核心主张（标题列表）
    file_claims = {}
    for filename, content in files_content.items():
        headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        file_claims[filename] = headings
    
    # 简单检测：查找含有"但"、"然而"、"矛盾"等转折词的段落
    contradiction_keywords = ['矛盾', '争议', '批评', '反对', '不一致', '然而', '但事实上', '与...相反']
    
    for filename, content in files_content.items():
        display_name = RESEARCH_FILES.get(filename, filename)
        for keyword in contradiction_keywords:
            matches = re.findall(r'[^。\n]{0,30}' + keyword + r'[^。\n]{0,50}', content)
            for match in matches[:1]:  # 每文件最多1条
                if len(match) > 20:
                    contradictions.append(f"{display_name}: 「{match.strip()[:60]}」")
    
    return contradictions[:3]  # 最多3条


def analyze_research_quality(skill_dir: Path) -> None:
    """主函数：分析调研质量并输出Phase 1.5摘要"""
    
    research_dir = skill_dir / 'references' / 'research'
    
    if not research_dir.exists():
        print(f"[ERROR] 调研目录不存在: {research_dir}")
        print(f"请先确认 {skill_dir}/references/research/ 目录已创建并包含调研文件")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"赛博达芬奇·Phase 1.5 调研质量检查点")
    print(f"Skill目录: {skill_dir}")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    files_content = {}
    missing_files = []
    weak_files = []  # 内容不足的文件
    
    # 读取所有调研文件
    for filename in RESEARCH_FILES:
        filepath = research_dir / filename
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            files_content[filename] = content
            
            if len(content) < 200:
                weak_files.append(filename)
        else:
            missing_files.append(filename)
    
    # 输出摘要表格
    print("┌──────────────────┬──────────┬──────────────────────────────┐")
    print("│ Agent            │ 来源数量  │ 关键发现                      │")
    print("├──────────────────┼──────────┼──────────────────────────────┤")
    
    total_sources = 0
    
    for filename, display_name in RESEARCH_FILES.items():
        if filename in files_content:
            content = files_content[filename]
            stats = count_sources(content)
            
            if filename == '06-timeline.md':
                source_str = check_timeline_recency(content)
            else:
                source_count = max(stats['urls'], stats['first_hand'] + stats['second_hand'])
                if source_count == 0:
                    source_count = max(1, len(content) // 500)  # 粗略估计
                source_str = f"{source_count}条"
                total_sources += source_count
            
            findings = extract_key_findings(content, max_findings=1)
            finding_str = findings[0][:35] if findings else '（空文件）'
            
            status = '⚠️' if filename in weak_files else ''
            print(f"│ {status}{display_name:<14} │ {source_str:<8} │ {finding_str:<30} │")
        else:
            print(f"│ ✗{display_name:<14} │ 未找到   │ 文件缺失，需补充调研         │")
    
    print("├──────────────────┼──────────┼──────────────────────────────┤")
    
    # 检测矛盾点
    contradictions = detect_contradictions(research_dir, files_content)
    contradiction_str = f"{len(contradictions)}处" if contradictions else "暂无"
    
    info_gap_str = '、'.join(RESEARCH_FILES[f] for f in missing_files) if missing_files else '无'
    info_gap_str = info_gap_str if info_gap_str else '无'
    
    print(f"│ 矛盾点           │ {contradiction_str:<8} │ {(contradictions[0][:30] if contradictions else '见下方详情'):<30} │")
    print(f"│ 信息不足维度      │ {len(missing_files) + len(weak_files)}个     │ {info_gap_str:<30} │")
    print("└──────────────────┴──────────┴──────────────────────────────┘")
    
    # 矛盾点详情
    if contradictions:
        print(f"\n📌 矛盾点详情：")
        for i, c in enumerate(contradictions, 1):
            print(f"  {i}. {c}")
    
    # 缺失/薄弱文件提示
    if missing_files:
        print(f"\n⚠️  缺失文件（需补充调研）：")
        for f in missing_files:
            print(f"  - {RESEARCH_FILES[f]} ({f})")
    
    if weak_files:
        print(f"\n⚠️  内容薄弱文件（建议补充）：")
        for f in weak_files:
            print(f"  - {RESEARCH_FILES[f]} ({f})")
    
    # 质量评估
    completeness = len(files_content) / len(RESEARCH_FILES)
    print(f"\n📊 调研完整度: {len(files_content)}/{len(RESEARCH_FILES)} 个文件 ({completeness:.0%})")
    
    if completeness >= 0.8 and not weak_files:
        print("✅ 调研质量达标，可进入Phase 2提炼阶段")
    elif completeness >= 0.6:
        print("⚡ 调研基本完整，但建议先补充薄弱维度再进入Phase 2")
    else:
        print("❌ 调研严重不足，建议先完善调研再推进")
    
    print(f"\n{'='*60}")
    print("确认调研质量OK → 回复「进入Phase 2」")
    print("需要补充某维度 → 回复「补充[维度名]调研」")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 merge_research.py <skill目录路径>")
        print("")
        print("示例:")
        print("  python3 merge_research.py .claude/skills/charlie-munger-perspective/")
        sys.exit(1)
    
    skill_dir = Path(sys.argv[1])
    
    if not skill_dir.exists():
        print(f"[ERROR] 目录不存在: {skill_dir}")
        sys.exit(1)
    
    analyze_research_quality(skill_dir)
