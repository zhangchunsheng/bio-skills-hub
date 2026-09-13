#!/usr/bin/env python3
"""
quality_check.py - 赛博达芬奇·Skill质量自检工具
用法: python3 quality_check.py <SKILL.md路径>

自动检查Phase 4通过标准的6项：
1. 心智模型数量（3-7个，每个含来源证据）
2. 每个模型的局限性（明确写出失效条件）
3. 表达DNA辨识度（有独特表达特征）
4. 诚实边界（至少3条具体局限）
5. 内在张力（至少2对矛盾）
6. 一手来源占比（>50%）
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass
class CheckResult:
    name: str
    passed: bool
    score: str
    standard: str
    evidence: str
    suggestion: str = ''


def check_mental_models(content: str) -> CheckResult:
    """检查1: 心智模型数量（3-7个，每个含来源证据）"""
    
    # 查找心智模型section
    mental_model_section = re.search(
        r'##\s*核心心智模型[^#]*?((?:###.+?\n[\s\S]*?)+?)(?=\n##(?!#)|\Z)',
        content, re.DOTALL
    )
    
    if not mental_model_section:
        return CheckResult(
            name='心智模型数量',
            passed=False,
            score='0个',
            standard='3-7个，每个有≥2条来源证据',
            evidence='未找到「核心心智模型」section',
            suggestion='添加 ## 核心心智模型 section，包含3-7个子section'
        )
    
    section_content = mental_model_section.group(1)
    
    # 统计心智模型数量（三级标题）
    models = re.findall(r'^###\s+(.+)$', section_content, re.MULTILINE)
    model_count = len(models)
    
    # 检查每个模型是否有来源证据
    models_with_evidence = 0
    for model in models:
        # 找到这个模型的内容块
        pattern = rf'###\s+{re.escape(model)}[\s\S]*?(?=###|\Z)'
        model_block = re.search(pattern, section_content)
        if model_block:
            block_content = model_block.group(0)
            # 检查是否有来源证据（URL、引号、来源标注）
            has_evidence = bool(
                re.search(r'https?://', block_content) or
                re.search(r'「.{10,}」', block_content) or
                re.search(r'来源[:：]', block_content) or
                re.search(r'\(\d{4}\)', block_content) or
                re.search(r'场景\d', block_content)
            )
            if has_evidence:
                models_with_evidence += 1
    
    passed = 3 <= model_count <= 7
    
    return CheckResult(
        name='心智模型数量',
        passed=passed,
        score=f'{model_count}个（{models_with_evidence}个含来源证据）',
        standard='3-7个，每个有≥2条来源证据',
        evidence=f'找到心智模型: {", ".join(models[:5])}{"..." if len(models) > 5 else ""}',
        suggestion='' if passed else (
            f'当前{model_count}个，{"需要减少到7个以内" if model_count > 7 else "需要增加到至少3个"}'
        )
    )


def check_model_limitations(content: str) -> CheckResult:
    """检查2: 每个心智模型是否写出局限性"""
    
    # 查找心智模型section
    mental_model_section = re.search(
        r'##\s*核心心智模型[^#]*?((?:###.+?\n[\s\S]*?)+?)(?=\n##(?!#)|\Z)',
        content, re.DOTALL
    )
    
    if not mental_model_section:
        return CheckResult(
            name='局限性完整性',
            passed=False,
            score='无法检测',
            standard='每个模型明确写出失效条件',
            evidence='未找到心智模型section',
        )
    
    section_content = mental_model_section.group(1)
    models = re.findall(r'^###\s+(.+)$', section_content, re.MULTILINE)
    
    limitation_keywords = ['局限', '失效', '不适用', '例外', '但当', '然而当', '前提', '边界']
    
    models_with_limitations = 0
    models_without = []
    
    for model in models:
        pattern = rf'###\s+{re.escape(model)}[\s\S]*?(?=###|\Z)'
        model_block = re.search(pattern, section_content)
        if model_block:
            block_content = model_block.group(0)
            has_limitation = any(kw in block_content for kw in limitation_keywords)
            if has_limitation:
                models_with_limitations += 1
            else:
                models_without.append(model)
    
    passed = len(models_without) == 0 and len(models) > 0
    
    return CheckResult(
        name='局限性完整性',
        passed=passed,
        score=f'{models_with_limitations}/{len(models)} 个模型含局限性',
        standard='每个模型明确写出失效条件，不只写优点',
        evidence=f'缺少局限性的模型: {", ".join(models_without[:3])}' if models_without else '所有模型均含局限性',
        suggestion=f'为以下模型补充「**局限性**」段落: {", ".join(models_without)}' if models_without else ''
    )


def check_expression_dna(content: str) -> CheckResult:
    """检查3: 表达DNA辨识度"""
    
    dna_section = re.search(r'##\s*表达DNA[\s\S]*?(?=\n##(?!#)|\Z)', content)
    
    if not dna_section:
        return CheckResult(
            name='表达DNA辨识度',
            passed=False,
            score='缺失',
            standard='读100字能认出是谁，不像通用AI',
            evidence='未找到「表达DNA」section',
            suggestion='添加 ## 表达DNA section，包含句式特征、高频词、幽默风格'
        )
    
    dna_content = dna_section.group(0)
    
    # 检查关键维度
    dimensions = {
        '句式特征': bool(re.search(r'句式|长句|短句|疑问|陈述', dna_content)),
        '高频词/术语': bool(re.search(r'高频|爱用|术语|词汇|专属', dna_content)),
        '幽默风格': bool(re.search(r'幽默|讽刺|自嘲|冷幽默|不幽默', dna_content)),
        '确定性表达': bool(re.search(r'确定性|不确定|很明显|我认为', dna_content)),
        '引用示例': bool(re.search(r'「.{10,}」|".{10,}"', dna_content)),
    }
    
    covered = sum(dimensions.values())
    passed = covered >= 3
    
    missing_dims = [k for k, v in dimensions.items() if not v]
    
    return CheckResult(
        name='表达DNA辨识度',
        passed=passed,
        score=f'{covered}/5 个维度已覆盖',
        standard='读100字能认出是谁，不像通用AI',
        evidence=f'已覆盖: {", ".join(k for k, v in dimensions.items() if v)}',
        suggestion=f'建议补充: {", ".join(missing_dims)}' if missing_dims else ''
    )


def check_honest_boundaries(content: str) -> CheckResult:
    """检查4: 诚实边界（至少3条具体局限）"""
    
    boundary_section = re.search(r'##\s*诚实边界[\s\S]*?(?=\n##(?!#)|\Z)', content)
    
    if not boundary_section:
        return CheckResult(
            name='诚实边界',
            passed=False,
            score='缺失',
            standard='至少3条具体局限',
            evidence='未找到「诚实边界」section',
            suggestion='添加 ## 诚实边界 section，列出至少3条具体局限'
        )
    
    boundary_content = boundary_section.group(0)
    
    # 统计列表项数量
    list_items = re.findall(r'^\d+\.\s+.{10,}', boundary_content, re.MULTILINE)
    bullet_items = re.findall(r'^[-*]\s+.{10,}', boundary_content, re.MULTILINE)
    
    total_items = len(list_items) + len(bullet_items)
    
    # 检查是否只有「不能替代本人」这种废话
    generic_only = (
        total_items <= 1 and
        bool(re.search(r'不能替代本人', boundary_content)) and
        not bool(re.search(r'截止|信息不足|缺少|薄弱|不确定', boundary_content))
    )
    
    passed = total_items >= 3 and not generic_only
    
    return CheckResult(
        name='诚实边界',
        passed=passed,
        score=f'{total_items}条',
        standard='至少3条具体局限，不只是「不能替代本人」',
        evidence=f'找到{total_items}条限制说明' + ('（但过于通用）' if generic_only else ''),
        suggestion='增加具体局限，如：信息截止日期、某领域信息不足、公开表达vs真实想法的差距等' if not passed else ''
    )


def check_inner_tensions(content: str) -> CheckResult:
    """检查5: 内在张力（至少2对矛盾）"""
    
    # 查找包含矛盾/张力的section
    tension_patterns = [
        r'##\s*(?:内在张力|矛盾|价值观与反模式)[\s\S]*?(?=\n##(?!#)|\Z)',
        r'###\s*(?:内在张力|矛盾与冲突)[\s\S]*?(?=\n###(?!#)|\n##(?!#)|\Z)',
    ]
    
    tension_content = ''
    for pattern in tension_patterns:
        match = re.search(pattern, content)
        if match:
            tension_content += match.group(0)
    
    if not tension_content:
        # 在全文中搜索张力关键词
        tension_keywords = ['张力', '矛盾', '冲突', '另一方面', '但同时', '悖论']
        has_tension = any(kw in content for kw in tension_keywords)
        
        return CheckResult(
            name='内在张力',
            passed=False,
            score='0对（未找到专门section）',
            standard='至少2对矛盾，不允许观点高度一致',
            evidence='未找到「内在张力」或「矛盾」section' + ('（全文有提及张力词汇）' if has_tension else ''),
            suggestion='在「价值观与反模式」section中添加「内在张力」子section，列出至少2对矛盾'
        )
    
    # 统计张力对数
    tension_pairs = re.findall(r'(?:张力|矛盾)\d+|【.+?vs.+?】|\*\*.+?\*\*\s*vs\s*\*\*.+?\*\*', tension_content)
    
    # 粗略计算：包含 "vs" 或 "矛盾N" 的项
    vs_count = len(re.findall(r'\bvs\b|与.{2,10}矛盾|和.{2,10}冲突', tension_content, re.IGNORECASE))
    explicit_tensions = len(re.findall(r'张力\d+|矛盾\d+', tension_content))
    
    total_tensions = max(vs_count, explicit_tensions, len(tension_pairs))
    
    # 如果有内容但没有明确标记，估算
    if total_tensions == 0 and len(tension_content) > 100:
        total_tensions = 1  # 至少有一些内容
    
    passed = total_tensions >= 2
    
    return CheckResult(
        name='内在张力',
        passed=passed,
        score=f'≈{total_tensions}对',
        standard='至少2对矛盾，不允许观点高度一致（太假）',
        evidence=tension_content[:100].replace('\n', ' ') + '...',
        suggestion='增加更多内在矛盾描述，展示此人思想的复杂性' if not passed else ''
    )


def check_primary_sources(content: str) -> CheckResult:
    """检查6: 一手来源占比（>50%）"""
    
    # 查找来源section
    source_section = re.search(r'##\s*(?:调研来源|参考来源|来源)[\s\S]*?(?=\n##(?!#)|\Z)', content)
    
    if not source_section:
        # 在全文中统计来源指标
        first_hand_signals = len(re.findall(
            r'著作|本人|演讲|亲口|原著|采访本人|一手|此人说|此人写',
            content
        ))
        second_hand_signals = len(re.findall(
            r'转述|二手|据称|报道|评价|他人说|分析文章',
            content
        ))
        
        total = first_hand_signals + second_hand_signals
        ratio = first_hand_signals / total if total > 0 else 0
        
        passed = ratio > 0.5
        return CheckResult(
            name='一手来源占比',
            passed=passed,
            score=f'估算约{ratio:.0%}（基于关键词）',
            standard='>50% 来自此人本人的著作/演讲/社媒',
            evidence=f'未找到专门来源section，基于关键词粗略估计',
            suggestion='添加「## 调研来源」section，区分一手和二手来源' if not passed else '建议添加「## 调研来源」section明确区分来源类型'
        )
    
    source_content = source_section.group(0)
    
    # 统计一手/二手来源数量
    first_hand_section = re.search(r'###\s*一手来源[\s\S]*?(?=###|\Z)', source_content)
    second_hand_section = re.search(r'###\s*二手来源[\s\S]*?(?=###|\Z)', source_content)
    
    first_count = 0
    second_count = 0
    
    if first_hand_section:
        first_count = len(re.findall(r'^[-*]\s+.+', first_hand_section.group(0), re.MULTILINE))
    
    if second_hand_section:
        second_count = len(re.findall(r'^[-*]\s+.+', second_hand_section.group(0), re.MULTILINE))
    
    total = first_count + second_count
    ratio = first_count / total if total > 0 else 0
    
    passed = ratio > 0.5 or (total == 0)  # 如果总数为0，暂时视为待填写
    
    return CheckResult(
        name='一手来源占比',
        passed=passed if total > 0 else False,
        score=f'{first_count}一手 / {second_count}二手 = {ratio:.0%}' if total > 0 else '待填写',
        standard='>50% 来自此人本人的著作/演讲/社媒',
        evidence=f'一手来源区包含{first_count}条，二手来源区包含{second_count}条',
        suggestion='增加一手来源比例，确保超过二手来源' if ratio <= 0.5 and total > 0 else ''
    )


def check_refusal_boundary(content: str) -> CheckResult:
    """检查8: 拒答边界是否被编码（此人公开回避的话题类型）"""

    refusal_keywords = [
        '拒绝回答', '拒答', '不公开谈', '回避', '不评论', '不讨论',
        '不谈', '从不评价', '明确不讨论', '这是他不会',
        '不代替', '不替他', '切换到第三人称',
    ]

    # 优先在诚实边界、反模式、角色扮演规则 section 中检索
    target_sections = []
    for section_name in ['诚实边界', '反模式', '角色扮演规则', '绝对不会']:
        m = re.search(
            r'#{1,3}\s*' + section_name + r'[\s\S]{0,800}',
            content
        )
        if m:
            target_sections.append(m.group(0))

    search_scope = '\n'.join(target_sections) if target_sections else content[:3000]
    has_refusal = any(kw in search_scope for kw in refusal_keywords)

    passed = has_refusal

    return CheckResult(
        name='拒答边界编码',
        passed=passed,
        score='已编码' if passed else '未检测到',
        standard='Skill中体现此人会拒绝/回避的话题类型（人格边界也是人格）',
        evidence='在诚实边界/反模式/角色规则中找到拒答约束' if passed
                 else '未在关键section中找到拒答边界描述',
        suggestion=(
            '在「诚实边界」或「反模式」中补充：此人公开回避的话题类型'
            '（如政治立场、竞争对手评价等），并说明Skill遇到此类问题时如何响应'
        ) if not passed else ''
    )


def check_attribution(content: str) -> CheckResult:
    """检查7: 创建者归属信息"""
    
    has_cyber = '赛博达芬奇' in content or 'Cyber Da Vinci' in content
    
    passed = has_cyber
    
    return CheckResult(
        name='创建者归属',
        passed=passed,
        score='完整' if passed else '缺失',
        standard='末尾含赛博达芬奇归属信息',
        evidence='已找到归属信息' if passed else '未找到「赛博达芬奇」或「Cyber Da Vinci」',
        suggestion='在SKILL.md末尾添加:\n  > 本Skill由 赛博达芬奇（Cyber Da Vinci）制作出品' if not passed else ''
    )


def run_quality_check(skill_path: str) -> None:
    """运行完整质量检查"""
    
    skill_file = Path(skill_path)
    
    if not skill_file.exists():
        print(f"[ERROR] 文件不存在: {skill_path}")
        sys.exit(1)
    
    content = skill_file.read_text(encoding='utf-8', errors='ignore')
    
    print(f"\n{'='*65}")
    print(f"赛博达芬奇·Phase 4 Skill质量自检报告")
    print(f"文件: {skill_path}")
    print(f"{'='*65}\n")
    
    # 运行所有检查
    checks = [
        check_mental_models(content),
        check_model_limitations(content),
        check_expression_dna(content),
        check_honest_boundaries(content),
        check_inner_tensions(content),
        check_primary_sources(content),
        check_refusal_boundary(content),
        check_attribution(content),
    ]
    
    passed_count = sum(1 for c in checks if c.passed)
    total_count = len(checks)
    
    # 输出逐项结果
    for check in checks:
        status = '✅ PASS' if check.passed else '❌ FAIL'
        print(f"{status} │ {check.name:<12} │ {check.score}")
        print(f"       │ 标准: {check.standard}")
        print(f"       │ 依据: {check.evidence[:80]}")
        if check.suggestion:
            print(f"       │ 建议: {check.suggestion[:80]}")
        print()
    
    # 总结
    print(f"{'='*65}")
    print(f"总计: {passed_count}/{total_count} 项通过")
    
    if passed_count == total_count:
        print("🎉 全部通过！Skill可以交付。")
    elif passed_count >= 5:
        print("⚡ 基本合格，修复上述FAIL项后可交付。")
    elif passed_count >= 3:
        print("⚠️  多项不通过，建议回到Phase 2进行迭代。")
    else:
        print("❌ 质量不达标，需要重新调研和提炼。")
    
    print(f"\n迭代上限提醒：Phase 2→4最多循环2次。")
    print(f"拒答边界提示：调研阶段请在 02-conversations.md 的「拒答记录」子节专门记录此人回避的话题类型。")
    print(f"2轮后仍有不通过项，在诚实边界中标注薄弱维度，交付当前最优版本。")
    print(f"{'='*65}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 quality_check.py <SKILL.md路径>")
        print("")
        print("示例:")
        print("  python3 quality_check.py .claude/skills/charlie-munger-perspective/SKILL.md")
        sys.exit(1)
    
    run_quality_check(sys.argv[1])
