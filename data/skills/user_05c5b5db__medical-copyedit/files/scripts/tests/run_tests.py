#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回归测试 runner —— medical-journal-copyediting

对 scripts/tests/cases.json 中的回归用例逐条调用 check_manuscript.run()，
断言：
  - expect 中的 rule_id 必须出现（否则计为漏检 FN）
  - forbid 中的 rule_id 必须不出现（出现计为误报 FP）
  - 既不在 expect 也不在 forbid/allow 的命中，计为额外误报 FP

并汇总：用例通过率，以及规则级 精确率 / 召回率 / F1。

说明：本 runner 只验证「规则是否按设计触发」，不等同于真实稿件的
准确率评测。正式评测需独立金标准语料 + 双编辑标注（见审查报告第 6 项）。

用法:
  python run_tests.py
  python run_tests.py --scope national,professional
"""
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # scripts/
import check_manuscript as cm

CASES_PATH = os.path.join(HERE, "cases.json")

WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _make_min_docx(path, para_xml):
    """生成一个最小可用 .docx（含 1 张占位图片以测 image_count）。"""
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           f'<w:document xmlns:w="{WNS}"><w:body>{para_xml}</w:body></w:document>')
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
          'content-types"><Default Extension="rels" ContentType="application/'
          'vnd.openxmlformats-package.relationships+xml"/><Default Extension='
          '"xml" ContentType="application/xml"/><Default Extension="png" '
          'ContentType="image/png"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
            '2006/relationships"><Relationship Id="rId1" Type="http://'
            'schemas.openxmlformats.org/officeDocument/2006/relationships/'
            'officeDocument" Target="word/document.xml"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc)
        z.writestr("word/media/image1.png", b"\x89PNG\r\n\x1a\n")
    return path


def test_docx():
    """DOCX 解析 + 统计符号正斜体检查回归：斜体符号不报警、正体符号报警。"""
    import tempfile
    ok = True
    # 全斜体：t/F/r 符合规范 → 不应出现 STAT-ITALIC
    p1 = tempfile.mktemp(suffix=".docx")
    _make_min_docx(p1,
                   '<w:p><w:r><w:rPr><w:i/></w:rPr>'
                   '<w:t>t=2.34, F=3.1, r=0.5</w:t></w:r></w:p>')
    # 全正体：P/n 应斜体未斜体 → 应出现 STAT-ITALIC
    p2 = tempfile.mktemp(suffix=".docx")
    _make_min_docx(p2,
                   '<w:p><w:r><w:t>P=0.05, n=30</w:t></w:r></w:p>')
    try:
        from parse_docx import parse_docx
        lines1, img1 = parse_docx(p1)
        lines2, img2 = parse_docx(p2)
        if img1 != 1 or img2 != 1:
            ok = False
            print(f"  [docx] image_count 期望 1，实得 {img1}/{img2}")
        if not lines1 or not lines2:
            ok = False
            print("  [docx] 未提取到文本行")
            return ok
        # 斜体行：无 STAT-ITALIC
        iss1, _, _, _ = cm.run(lines1, cm.SCOPE_ORDER, [], {}, set(),
                               stats_italic=True)
        if any(it["rule_id"] == "STAT-ITALIC" for it in iss1):
            ok = False
            print("  [docx] 误报：斜体 t/F/r 被报 STAT-ITALIC")
        # 正体行：有 STAT-ITALIC
        iss2, _, _, _ = cm.run(lines2, cm.SCOPE_ORDER, [], {}, set(),
                               stats_italic=True)
        if not any(it["rule_id"] == "STAT-ITALIC" for it in iss2):
            ok = False
            print("  [docx] 漏检：正体 P/n 未报 STAT-ITALIC")
        # 表格行提取（source=表格）
        p3 = tempfile.mktemp(suffix=".docx")
        _make_min_docx(p3,
                       '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>P=0.05</w:t></w:r>'
                       '</w:p></w:tc></w:tr></w:tbl>')
        lines3, _ = parse_docx(p3)
        if not any(l.get("source") == "表格" for l in lines3):
            ok = False
            print("  [docx] 未提取表格行（source=表格）")
    finally:
        for p in (p1, p2, p3):
            if os.path.exists(p):
                os.remove(p)
    return ok


def test_rule_examples():
    """逐规则 example/counter_example 自洽校验（P2-1）。

    对每条 auto=true 且 pattern 非空的规则：其 example 应触发本规则自身，
    其 counter_example 不应触发本规则自身。auto=false 的清单规则（如
    EXP-AD）与空 pattern 的纯提示规则不参与——它们的 example 本就不自动扫描。
    """
    rules = cm.load_rules()
    ok = True
    for r in rules:
        rid = r.get("id", "")
        if not rid:
            continue
        if not r.get("_auto", True):
            continue
        if not r.get("pattern"):
            continue
        ex = r.get("example")
        ce = r.get("counter_example")
        if ex:
            issues, _, _, _ = cm.run([ex], cm.SCOPE_ORDER, [], {}, set())
            det = {it["rule_id"] for it in issues}
            if rid not in det:
                ok = False
                print(f"  [示例不触发] {rid}: example={ex!r} -> 命中 {sorted(det)}")
        if ce:
            issues, _, _, _ = cm.run([ce], cm.SCOPE_ORDER, [], {}, set())
            det = {it["rule_id"] for it in issues}
            if rid in det:
                ok = False
                print(f"  [反例仍触发] {rid}: counter_example={ce!r} -> 命中 {sorted(det)}")
    return ok


def test_dict_directionality():
    """自定义词典方向性校验回归（待办#1）。

    通过 cm.run() 直接传入 custom_terms 验证：
      - 正确方向（非规范→规范）应生成 CUSTOM- 规则；
      - 键为已知规范词（如「心肌梗死」）应被跳过，不误报规范文本；
      - 键==值（无替换意义）应被跳过。
    """
    ok = True
    # 正确方向：应生成 CUSTOM- 规则
    iss, _, _, _ = cm.run("患者患yy症。", cm.SCOPE_ORDER, [], {"yy症": "YY症"}, set())
    if not any(it["rule_id"].startswith("CUSTOM-") for it in iss):
        ok = False
        print("  [词典方向性] 正确方向词条未生成 CUSTOM- 规则")
    # 键为已知规范词：应跳过，不得误报规范文本
    iss2, _, _, _ = cm.run("患者发生急性心肌梗死。", cm.SCOPE_ORDER,
                           [], {"心肌梗死": "心梗"}, set())
    if any(it["rule_id"].startswith("CUSTOM-") for it in iss2):
        ok = False
        print("  [词典方向性] 键为规范词仍生成 CUSTOM-（应跳过）")
    # 键==值：应跳过
    iss3, _, _, _ = cm.run("这是测试词示例。", cm.SCOPE_ORDER,
                           [], {"测试词": "测试词"}, set())
    if any(it["rule_id"].startswith("CUSTOM-") for it in iss3):
        ok = False
        print("  [词典方向性] 键==值仍生成 CUSTOM-（应跳过）")
    return ok


def main():
    scopes = list(cm.SCOPE_ORDER)
    if len(sys.argv) > 2 and sys.argv[1] == "--scope":
        scopes = [s for s in sys.argv[2].split(",") if s in cm.SCOPE_ORDER]

    # 逐规则 example/counter_example 自洽校验（P2-1）：确保规则 JSON 的示例
    # 真能触发、反例真不触发，防止规则与文档漂移。auto=false 清单规则与空
    # pattern 纯提示规则不参与（其 example 本就不自动扫描）。
    if not test_rule_examples():
        print("\n规则 example/counter_example 自洽校验未通过")
        sys.exit(1)

    with open(CASES_PATH, encoding="utf-8") as f:
        cases = json.load(f)

    passed = 0
    tp = fp = fn = 0
    failures = []

    for c in cases:
        name = c.get("name", "?")
        text = c["text"]
        expect = set(c.get("expect", []))
        forbid = set(c.get("forbid", []))
        allow = set(c.get("allow", []))

        issues, _, _, _ = cm.run(text, scopes, [], {}, set())
        detected = {it["rule_id"] for it in issues}

        case_ok = True
        for eid in expect:
            if eid in detected:
                tp += 1
            else:
                fn += 1
                case_ok = False
                failures.append(f"  [漏检] {name}: 预期 {eid} 未命中")
        for fid in forbid:
            if fid in detected:
                fp += 1
                case_ok = False
                failures.append(f"  [误报] {name}: 禁止 {fid} 却命中")
        extra = detected - expect - forbid - allow
        if extra:
            fp += len(extra)
            case_ok = False
            failures.append(f"  [额外误报] {name}: 命中 {sorted(extra)}")
        if case_ok:
            passed += 1

    total = len(cases)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

    print(f"用例通过: {passed}/{total}  ({passed / total * 100:.1f}%)")
    print(f"规则级: TP={tp} FP={fp} FN={fn}  "
          f"精确率={prec:.3f} 召回率={rec:.3f} F1={f1:.3f}")
    if failures:
        print("\n未通过项:")
        print("\n".join(failures))
        sys.exit(1)

    # DOCX 解析与统计正斜体回归
    if not test_docx():
        print("\nDOCX 回归未通过")
        sys.exit(1)

    # 自定义词典方向性校验回归
    if not test_dict_directionality():
        print("\n自定义词典方向性回归未通过")
        sys.exit(1)

    print("\n全部通过 ✓")
    sys.exit(0)


if __name__ == "__main__":
    main()
