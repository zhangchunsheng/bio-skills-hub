#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DA 合规初筛（pharma skill 共享脚本）

对生成的医药推广材料做轻量合规初筛：
  - 违禁 / 高风险词（绝对化用语、疗效承诺等）
  - DA 必备要素缺失（批准文号、仅供医药专业人士、不良反应/禁忌）
仅提示、不修改文件；返回人类可读报告，退出码始终为 0（不阻塞流水线）。

用法:
    python compliance_check.py <file> [--json]
支持 .md / .txt（直接读）；.docx 在有 python-docx 时抽取正文，否则提示改用 .md 版本自检。
"""

import sys
import re
import argparse
import json
from pathlib import Path

# 违禁 / 高风险词（命中即警告，须人工复核或替换）
BANNED_TERMS = [
    "最佳", "首选", "唯一", "100%", "百分之百", "根治", "治愈率", "包治",
    "断根", "无副作用", "绝对安全", "保证", "特效", "王牌", "第一品牌",
    "最有效", "最安全", "国家级", "最高级", "顶级",
]

# 必备要素（缺任一项即提示）
REQUIRED_PATTERNS = {
    "仅供医药专业人士": re.compile(r"医药专业人士|医疗卫生专业人士|仅供.*专业"),
    "批准文号": re.compile(r"某药企准字|批准文号|H\d{8}|Z\d{8}|S\d{8}"),
    "不良反应/禁忌": re.compile(r"不良反应|禁忌|注意事项"),
}


def extract_text(path: Path):
    if path.suffix.lower() == ".docx":
        try:
            from docx import Document
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""  # 无法抽取；调用方会提示对 .md 版本自检
    return path.read_text(encoding="utf-8", errors="ignore")


def check(text):
    findings = []
    for term in BANNED_TERMS:
        if term in text:
            for i, line in enumerate(text.splitlines(), 1):
                if term in line:
                    findings.append({
                        "level": "warn",
                        "type": "banned_term",
                        "hit": term,
                        "line": i,
                        "context": line.strip()[:80],
                    })
                    break
    missing = [name for name, pat in REQUIRED_PATTERNS.items() if not pat.search(text)]
    return findings, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="待自检的文件 (.md/.txt/.docx)")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"文件不存在: {p}")
        return

    text = extract_text(p)
    if text == "" and p.suffix.lower() == ".docx":
        msg = "docx 正文抽取需 python-docx，请对渲染出的 .md 版本运行自检。"
        if args.json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"合规初筛：{p}\n  ⚠️ {msg}")
        return

    findings, missing = check(text)

    if args.json:
        print(json.dumps({"findings": findings, "missing_required": missing},
                         ensure_ascii=False, indent=2))
        return

    print(f"合规初筛：{p}")
    if not findings and not missing:
        print("  ✅ 未发现明显违禁词，必备要素齐全。仍须人工复核。")
    else:
        if findings:
            print(f"  ⚠️ 命中 {len(findings)} 处高风险词（须人工复核/替换）：")
            for f in findings:
                print(f"    L{f['line']} 「{f['hit']}」 {f['context']}")
        if missing:
            print(f"  ⚠️ 缺失必备要素：{', '.join(missing)}（DA 文案须包含）")
        print("  → 请修订后重新自检；本检查仅提示，不替代合规复核。")


if __name__ == "__main__":
    main()
