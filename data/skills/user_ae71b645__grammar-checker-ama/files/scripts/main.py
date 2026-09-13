#!/usr/bin/env python3
"""
AMA 语法检查工具 (Grammar Checker - AMA)
按照《AMA 风格手册》(AMA Manual of Style) 检查医学英语写作中的语法问题。

注意：本工具检查的是英文文本的语法（被动语态等），
因为 AMA 风格手册是面向英文医学写作的规范，检测逻辑保持英文不变。
"""

import argparse


class AMAChecker:
    """按照 AMA 风格检查语法。"""

    def check_passive_voice(self, text):
        """检测被动语态结构（基于英文常见被动语态短语）。"""
        passive_indicators = ["was performed", "were analyzed", "is shown", "are demonstrated"]
        issues = []
        for indicator in passive_indicators:
            if indicator in text.lower():
                issues.append(f"检测到被动语态: '{indicator}'")
        return issues

    def check(self, text):
        """运行所有语法检查项。"""
        results = {
            "passive_voice": self.check_passive_voice(text),
            "suggestions": []
        }
        return results


def main():
    parser = argparse.ArgumentParser(description="AMA 语法检查工具 (Grammar Checker - AMA)")
    parser.add_argument("--text", "-t", required=True, help="需要检查的英文文本")
    args = parser.parse_args()

    checker = AMAChecker()
    results = checker.check(args.text)

    print("AMA 语法检查结果：")
    print("-" * 50)
    if results["passive_voice"]:
        print("\n发现的被动语态问题：")
        for issue in results["passive_voice"]:
            print(f"  - {issue}")
    else:
        print("\n未发现被动语态问题。")


if __name__ == "__main__":
    main()
