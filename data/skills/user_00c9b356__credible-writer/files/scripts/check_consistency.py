#!/usr/bin/env python3
"""
check_consistency.py — 逻辑一致性机械扫描脚本（零依赖）

检查内容：
  1. 判定规则句 vs 选项极性位置一致性
     - 提取含"选前者/选后者/选A/选B"等句式的判定规则
     - 检查选项标注的极性是否与规则一致
  2. 术语一致性
     - 检测同一概念的不同写法混用
     - 检测中英术语不统一
  3. 标题-正文数量一致性
     - 标题说"N个"但正文列了不同数量

输出：PASS / WARN / FAIL
退出码：0 = PASS，1 = WARN 或 FAIL

用法：
  python check_consistency.py <文件路径>
  python check_consistency.py <目录路径>   (递归扫描 .md/.txt/.html)
"""

import sys
import os
import re


# ============================================================
# 极性词表
# ============================================================

POSITIVE_WORDS = ['正面', '积极', '共生', '互利', '合作', '正确', '优', '高', '强', '好', '对']
NEGATIVE_WORDS = ['负面', '消极', '寄生', '损耗', '竞争', '错误', '劣', '低', '弱', '坏', '错']

ALL_POLARITY_WORDS = POSITIVE_WORDS + NEGATIVE_WORDS


def get_polarity(text):
    """从文本中提取极性：positive / negative / None"""
    has_pos = any(w in text for w in POSITIVE_WORDS)
    has_neg = any(w in text for w in NEGATIVE_WORDS)
    if has_pos and has_neg:
        return 'mixed'
    if has_pos:
        return 'positive'
    if has_neg:
        return 'negative'
    return None


# ============================================================
# 维度 1：判定规则 - 选项极性一致性
# ============================================================

# 判定规则句模式 — 逐行匹配
# 匹配 "选前者 = 正面" "选后者=共生" "选 A = X" 等
RULE_LINE_PATTERNS = [
    # 选前者/后者 = 极性（带等号或冒号）
    re.compile(r'选前者\s*[=＝:：]\s*(.+)'),
    re.compile(r'选后者\s*[=＝:：]\s*(.+)'),
    # 前者/后者 为/是/表示/代表 极性
    re.compile(r'前者\s*(?:为|是|表示|代表|意味着?)\s*(.+)'),
    re.compile(r'后者\s*(为|是|表示|代表|意味着?)\s*(.+)'),
    # 选 A/B = 极性
    re.compile(r'选\s*([A-Da-d])\s*[=＝:：]\s*(.+)'),
    # 分数 > N = 极性
    re.compile(r'分数?\s*[>＞≥]\s*(\d+)\s*[=＝:：为是]\s*(.+)'),
]


def extract_rules(text):
    """逐行提取判定规则，返回规则列表"""
    rules = []
    for line in text.split('\n'):
        line_stripped = line.strip()
        for pattern in RULE_LINE_PATTERNS:
            match = pattern.search(line_stripped)
            if match:
                # 获取规则的方向词（前者/后者/A/B/分数）和极性
                full = line_stripped
                polarity_text = match.group(match.lastindex)  # 最后一个捕获组

                direction = None
                if '前者' in full:
                    direction = '前者'
                elif '后者' in full:
                    direction = '后者'
                elif '选' in full and re.search(r'选\s*([A-Da-d])', full):
                    direction = re.search(r'选\s*([A-Da-d])', full).group(1).upper()

                polarity = get_polarity(polarity_text)
                if polarity and polarity != 'mixed':
                    rules.append({
                        'line': full,
                        'direction': direction,
                        'polarity': polarity,
                        'polarity_text': polarity_text.strip()[:30],
                    })
                break  # 一行只匹配一个模式
    return rules


def extract_option_polarities(text):
    """逐行提取选项的极性标注，返回选项列表"""
    options = []
    for line in text.split('\n'):
        line_stripped = line.strip()
        # 跳过空行和纯标题行
        if not line_stripped or line_stripped.startswith('#'):
            continue

        # 检查这一行是否包含"前者"或"后者"或"选A/B"
        has_direction = False
        direction = None
        if '前者' in line_stripped:
            direction = '前者'
            has_direction = True
        elif '后者' in line_stripped:
            direction = '后者'
            has_direction = True
        else:
            m = re.search(r'选?\s*([A-Da-d])\s*[:：.、]', line_stripped)
            if m:
                direction = m.group(1).upper()
                has_direction = True

        if not has_direction:
            continue

        # 跳过判定规则句本身（含等号/冒号赋值）
        if re.search(r'(?:选前者|选后者|选\s*[A-Da-d])\s*[=＝:：]', line_stripped):
            continue
        if re.search(r'(?:前者|后者)\s*(?:为|是|表示|代表)', line_stripped) and not re.search(r'[*\-•|]', line_stripped):
            continue

        # 提取这一行的极性
        polarity = get_polarity(line_stripped)
        if polarity and polarity != 'mixed':
            options.append({
                'line': line_stripped,
                'direction': direction,
                'polarity': polarity,
            })

    return options


def check_rule_option_consistency(text):
    """检查判定规则句与选项极性是否一致"""
    warnings = []

    rules = extract_rules(text)
    if not rules:
        return []

    options = extract_option_polarities(text)
    if not options:
        return []

    # 对每个规则，检查对应方向的选项极性是否一致
    for rule in rules:
        if not rule['direction']:
            continue

        for opt in options:
            if opt['direction'] != rule['direction']:
                continue

            if opt['polarity'] == rule['polarity']:
                continue  # 一致，OK

            # 直接矛盾：规则说前者=正面，但选项把前者标为负面
            is_rule_line = any(r['line'] == opt['line'] for r in rules)
            if is_rule_line:
                continue  # 这行本身是规则行，跳过

            warnings.append(
                f"[FAIL] 维度1-判定规则选项一致性: "
                f"规则 '{rule['line'][:60]}' 声明 {rule['direction']}={rule['polarity']}，"
                f"但选项 '{opt['line'][:60]}' 把 {opt['direction']} 标为 {opt['polarity']}——直接矛盾。"
            )

    return warnings


# ============================================================
# 维度 2：术语一致性
# ============================================================

SYNONYM_GROUPS = [
    {
        'concept': '技能/Skill',
        'variants': ['Skill', 'skill', '技能包', '技能模块', '技能'],
        'warning_threshold': 3,
    },
    {
        'concept': '人工智能/AI',
        'variants': ['AI', 'ai', '人工智能技术', '人工智能'],
        'warning_threshold': 3,
    },
    {
        'concept': '提示词/Prompt',
        'variants': ['Prompt', 'prompt', '提示语', '提示词', '提示'],
        'warning_threshold': 3,
    },
    {
        'concept': '模型/Model',
        'variants': ['大语言模型', '大模型', 'LLM', '语言模型', '模型'],
        'warning_threshold': 3,
    },
]


def check_terminology_consistency(text):
    """检查术语是否全文统一"""
    warnings = []

    for group in SYNONYM_GROUPS:
        found_variants = {}
        for variant in group['variants']:
            count = text.count(variant)
            if count > 0:
                found_variants[variant] = count

        if len(found_variants) >= group['warning_threshold']:
            variant_str = ', '.join(f"'{v}'({c}次)" for v, c in found_variants.items())
            warnings.append(
                f"[WARN] 维度4-术语一致性: 概念'{group['concept']}'"
                f"出现 {len(found_variants)} 种写法: {variant_str}。建议统一。"
            )

    return warnings


# ============================================================
# 维度 3：标题-正文数量一致性
# ============================================================

def check_title_body_count(text):
    """检查标题中的数字与正文实际项数是否一致"""
    warnings = []

    title_patterns = [
        re.compile(r'^#+\s*.*?(\d+)\s*(?:个|种|大|项|条|步|个方面|个要点|个关键|个原因|个方法|个误区|个问题)', re.MULTILINE),
        re.compile(r'^#+\s*.*?(\d+)\s*(?:ways|steps|tips|reasons|mistakes|points)', re.MULTILINE | re.IGNORECASE),
    ]

    for pattern in title_patterns:
        for match in pattern.finditer(text):
            claimed_count = int(match.group(1))
            title_line = match.group(0).strip()

            title_end = match.end()
            next_header = re.search(r'^#+\s', text[title_end:], re.MULTILINE)
            if next_header:
                section_text = text[title_end:title_end + next_header.start()]
            else:
                section_text = text[title_end:]

            list_items = re.findall(r'^\s*[*\-•\d]+[.\)、]\s+', section_text, re.MULTILINE)

            if list_items and abs(len(list_items) - claimed_count) >= 1:
                warnings.append(
                    f"[WARN] 维度2-标题正文一致性: "
                    f"标题 '{title_line[:50]}' 承诺 {claimed_count} 项，"
                    f"但正文列出 {len(list_items)} 项。"
                )

    return warnings


# ============================================================
# 主流程
# ============================================================

def check_file(filepath):
    """检查单个文件，返回 warnings 列表"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        return [f"[ERROR] 无法读取文件 {filepath}: {e}"]

    warnings = []
    warnings.extend(check_rule_option_consistency(text))
    warnings.extend(check_terminology_consistency(text))
    warnings.extend(check_title_body_count(text))

    return warnings


def main():
    if len(sys.argv) < 2:
        print("用法: python check_consistency.py <文件路径或目录>")
        print("退出码: 0=PASS, 1=WARN/FAIL")
        sys.exit(1)

    target = sys.argv[1]
    all_warnings = []

    if os.path.isfile(target):
        all_warnings.extend(check_file(target))
    elif os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for fname in files:
                if fname.endswith(('.md', '.txt', '.html', '.htm')):
                    fpath = os.path.join(root, fname)
                    all_warnings.extend(check_file(fpath))
    else:
        print(f"错误: {target} 不是有效的文件或目录")
        sys.exit(1)

    has_fail = any('[FAIL]' in w for w in all_warnings)
    has_warn = any('[WARN]' in w for w in all_warnings)

    if not all_warnings:
        print("===== 一致性检查结果: PASS =====")
        print("未发现一致性问题。")
        sys.exit(0)
    elif has_fail:
        print("===== 一致性检查结果: FAIL =====")
        print(f"发现 {len(all_warnings)} 个问题（含确定性矛盾）:\n")
        for w in all_warnings:
            print(f"  {w}")
        sys.exit(1)
    else:
        print("===== 一致性检查结果: WARN =====")
        print(f"发现 {len(all_warnings)} 个潜在问题:\n")
        for w in all_warnings:
            print(f"  {w}")
        print("\n请人工复核以上警告后再交付。")
        sys.exit(1)


if __name__ == '__main__':
    main()
