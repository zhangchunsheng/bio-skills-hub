#!/usr/bin/env python3
"""
科室会PPT内容脚本质量检查工具
检查生成的PPT内容脚本是否满足STEPS框架的所有质量要求。
用法：python3 quality_check.py <脚本文件路径>
"""

import re
import sys


def check_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    results = []
    errors = []
    warnings = []

    # 1. 检查页面数量
    page_count = len(re.findall(r'###\s*(?:第\s*(\d+)\s*页|Slide\s*(\d+)|第\d+页)', content))
    slides_found = len(re.findall(r'(?:第\s*\d+\s*页|Slide\s+\d+)', content))
    results.append(("📄 页面数量检查", f"找到 {slides_found} 页幻灯片", slides_found >= 13 and slides_found <= 17))

    # 2. 检查AIDA关键阶段存在性
    has_attention = any(kw in content for kw in ['临床挑战', '未满足', '问题', '痛点', '负担', '现状'])
    has_interest = any(kw in content for kw in ['解决方案', '作用机制', '药理', '机制', '优势'])
    has_desire = any(kw in content for kw in ['循证', '证据', '研究', 'RCT', 'Meta', '试验'])
    has_action = any(kw in content for kw in ['患者识别', '治疗路径', '处方', '总结', '行动', '路径'])

    results.append(("🎯 AIDA-Attention（引起注意）", "包含临床挑战/问题描述", has_attention))
    results.append(("🎯 AIDA-Interest（激发兴趣）", "包含解决方案/机制描述", has_interest))
    results.append(("🎯 AIDA-Desire（建立欲望）", "包含循证证据引用", has_desire))
    results.append(("🎯 AIDA-Action（促进行动）", "包含患者路径/行动号召", has_action))

    # 3. 检查GRADE分级存在性
    grade_pattern = re.findall(r'GRADE[：:]\s*(高|中|低|极低)', content)
    grade_all = re.findall(r'(?:GRADE|grade|Grade)\s*[：:：]?\s*(高|中|低|极低|High|Moderate|Low|Very\s*Low)', content)
    results.append(("📊 GRADE证据分级检查", f"找到 {len(grade_all)} 处GRADE分级标注", len(grade_all) >= 2))

    # 4. 检查演讲者备注（Notes）
    notes_count = len(re.findall(r'(?:📝|演讲者备注|备注|Notes|notes)', content))
    results.append(("📝 演讲者备注检查", f"找到 {notes_count} 处备注标记", notes_count >= 14))

    # 5. 合规检查：禁止性用语
    forbidden_words = ['首选', '最佳', '金标准', '特效', '独一无二', '万能', '根治', '治愈',
                       '第一', '领先（作为最高级）', '绝对安全', '无毒副作用', '零风险']
    found_forbidden = []
    for word in ['首选', '最佳', '金标准', '特效', '独一无二', '万能', '绝对安全', '无毒副', '零风险']:
        if word in content:
            found_forbidden.append(word)

    if found_forbidden:
        errors.append(f"⚠️ 发现疑似违规词：{', '.join(found_forbidden)}")
    results.append(("🚫 合规检查-禁止用语", f"发现 {len(found_forbidden)} 个疑似违规词", len(found_forbidden) == 0))

    # 6. 检查页间过渡
    transition_count = len(re.findall(r'(接下来|下面|刚才谈到|过渡|下一页|来看|前面提到|另一方面|此外|不仅如此)', content))
    results.append(("🔗 页间过渡检查", f"找到 {transition_count} 处过渡语", transition_count >= 5))

    # 7. 总篇幅检查
    char_count = len(content)
    results.append(("📏 总篇幅检查", f"共 {char_count} 字符", char_count >= 3000))

    # 输出结果
    print("=" * 60)
    print("  科室会PPT内容脚本 - 质量检查报告")
    print("=" * 60)
    print()

    all_pass = True
    for name, detail, passed in results:
        status = "✅" if passed else "❌"
        if not passed:
            all_pass = False
        print(f"  {status} {name}")
        print(f"     {detail}")
        print()

    if errors:
        print("⚠️  合规风险警告：")
        for e in errors:
            print(f"  🔴 {e}")
        print()

    print("-" * 60)
    if all_pass and not errors:
        print("  🏆 所有质量检查通过！内容脚本可以交付。")
    else:
        print(f"  {'⚠️ 部分检查未通过，建议修改后重新检查' if not all_pass else '✅ 基础检查通过'}")
        if errors:
            print(f"  ⚠️ 存在 {len(errors)} 项合规风险，必须修改")
    print("=" * 60)

    return all_pass and len(errors) == 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python3 quality_check.py <脚本文件路径>")
        sys.exit(1)
    success = check_file(sys.argv[1])
    sys.exit(0 if success else 1)
