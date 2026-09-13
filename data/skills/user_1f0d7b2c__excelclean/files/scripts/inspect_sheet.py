#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inspect_sheet —— 表格体检。只读不动，输出问题清单与修复建议。

用法:
  python inspect_sheet.py 文件.xlsx
  python inspect_sheet.py 文件.csv --json
  python inspect_sheet.py 文件.xlsx --sheet 2        # 第 3 个 sheet（0 基）
  python inspect_sheet.py 文件.xlsx --sheet "明细"    # 按名字选

退出码: 0=无 P0 问题, 1=有 P0 问题, 2=文件读不了
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xlsx_lite as X
import extras
from dirty_rules import (
    normalize_text, parse_number, parse_date, is_blank_row,
    detect_header_row, column_profile, TOTAL_ROW_HINT, TOTAL_CELL_HINT,
    NOTE_ROW_HINT, PLACEHOLDER,
)

SEV_ORDER = {"P0": 0, "P1": 1, "P2": 2}


def extract_grid(data, sheet=None):
    """把不同来源统一成 (rows, sheet_name, merges)。"""
    if data["kind"] == "xlsx":
        sheets = data["sheets"]
        if not sheets:
            return None, None, None
        if sheet is None:
            sh = sheets[0]
        elif isinstance(sheet, int):
            sh = sheets[sheet] if 0 <= sheet < len(sheets) else sheets[0]
        else:
            sh = next((s for s in sheets if s.name == sheet), sheets[0])
        return sh.values(), sh.name, sh.merges
    return data["rows"], os.path.basename(data.get("path", "sheet1")), []


def find_issues(rows, merges, encoding, delimiter, sheet_name):
    issues = []
    if not rows:
        return issues, 0, 0

    nrows = len(rows)
    ncols = max(len(r) for r in rows) if rows else 0

    # --- 表头位置
    hrow, hconf, hreason = detect_header_row(rows)
    if hrow != 0:
        issues.append({
            "sev": "P0", "code": "header-not-first",
            "msg": "表头不在第 1 行，而在第 %d 行（%s）" % (hrow + 1, hreason),
            "detail": "第 1-%d 行内容: %s" % (hrow, " | ".join(str(v) for v in rows[0][:6] if v is not None)),
            "fix": "--header-row %d" % (hrow + 1),
        })
    elif hconf < 0.35:
        issues.append({
            "sev": "P1", "code": "header-uncertain",
            "msg": "表头位置置信度低（%.2f），建议人工确认" % hconf,
            "fix": "--header-row N 手动指定",
        })

    # --- 合并单元格
    if merges:
        head_merges = [m for m in merges if m and int("".join(ch for ch in m.split(":")[0] if ch.isdigit()) or 0) <= hrow + 1]
        issues.append({
            "sev": "P0" if head_merges else "P2",
            "code": "merged-cells",
            "msg": "存在 %d 处合并单元格%s" % (
                len(merges),
                "，其中 %d 处在表头区（pandas 读入会变成 NaN，必须向下填充）" % len(head_merges) if head_merges else ""
            ),
            "detail": "示例: " + ", ".join(merges[:6]),
            "fix": "清洗时自动向下填充",
        })

    # --- 编码
    if encoding and encoding not in ("utf-8", "utf-8-sig", "zip/xml"):
        issues.append({
            "sev": "P0", "code": "encoding",
            "msg": "文件是 %s 编码，不是 UTF-8。用默认方式打开会乱码" % encoding,
            "fix": "按 %s 解码，输出统一转 UTF-8-BOM" % encoding,
        })

    # --- 空行 / 空列
    blank_rows = [i for i, r in enumerate(rows) if is_blank_row(r)]
    if blank_rows:
        # 空行夹在数据中间 → 多半是一张表里塞了多块
        mid = [i for i in blank_rows if hrow < i < nrows - 1]
        if mid:
            issues.append({
                "sev": "P1", "code": "multi-block",
                "msg": "数据区中间有 %d 个空行（行号 %s），很可能一个 sheet 里塞了多张表" % (
                    len(mid), ", ".join(str(i + 1) for i in mid[:8]) + ("..." if len(mid) > 8 else "")),
                "fix": "--split-blocks 按空行拆成多张表",
            })
        else:
            issues.append({
                "sev": "P2", "code": "blank-rows",
                "msg": "有 %d 个空行" % len(blank_rows),
                "fix": "默认删除",
            })

    blank_cols = []
    for ci in range(ncols):
        col = [r[ci] if ci < len(r) else None for r in rows]
        if all(v is None or (isinstance(v, str) and not v.strip()) for v in col):
            blank_cols.append(ci)
    if blank_cols:
        issues.append({
            "sev": "P2", "code": "blank-cols",
            "msg": "有 %d 个空列（%s）" % (len(blank_cols), ", ".join(X.idx_to_col(c) for c in blank_cols[:8])),
            "fix": "默认删除",
        })

    # --- 先标出合计/备注行。列分析必须跳过它们，
    #     否则"注：数据截至3月31日"这类文字会被当成数据，污染类型判断与脏字符示例
    total_rows, note_rows = [], []
    for i in range(hrow + 1, nrows):
        r = rows[i]
        if is_blank_row(r):
            continue
        joined = " ".join(str(v) for v in r if v is not None)
        first = str(r[0]).strip() if r and r[0] is not None else ""
        if TOTAL_ROW_HINT.match(first) or TOTAL_ROW_HINT.match(joined.strip()):
            total_rows.append(i)
        elif NOTE_ROW_HINT.match(first):
            note_rows.append(i)
    skip = set(total_rows) | set(note_rows)
    analysis_rows = [[None] * len(r) if i in skip else r for i, r in enumerate(rows)]

    # --- 逐列分析
    col_issues = {}
    for ci in range(ncols):
        prof = column_profile(analysis_rows, hrow, ci)
        if prof["n"] == 0:
            continue
        name = rows[hrow][ci] if hrow < len(rows) and ci < len(rows[hrow]) else None
        label = "%s(%s)" % (name if name else "(无名)", X.idx_to_col(ci))

        flags = []
        if prof["textnum_ratio"] >= 0.6:
            flags.append(("P0", "text-number",
                          "%.0f%% 的值看着是数字却存成了文本，SUM/排序会失灵" % (prof["textnum_ratio"] * 100)))
        elif 0 < prof["textnum_ratio"] < 0.6:
            flags.append(("P1", "mixed-type",
                          "%.0f%% 是文本数字、其余是其他类型，类型不统一" % (prof["textnum_ratio"] * 100)))
        if prof["unit_ratio"] >= 0.3:
            flags.append(("P0", "cn-unit",
                          "%.0f%% 的值带中文单位（万/亿/元/百分号），必须剥离才能算" % (prof["unit_ratio"] * 100)))
        if prof["date_ratio"] >= 0.6:
            flags.append(("P1", "date-format",
                          "%.0f%% 是中文日期文本，格式不统一" % (prof["date_ratio"] * 100)))
        if prof["mixed"] and prof["numeric_ratio"] > 0 and prof["textnum_ratio"] > 0:
            flags.append(("P1", "mixed-type", "数字与文本数字混在同一列"))

        # 字符脏：全角/不可见/首尾空格/括号
        dirty_samples = []
        for r in analysis_rows[hrow + 1:]:
            if ci < len(r) and isinstance(r[ci], str):
                fixed, changed = normalize_text(r[ci])
                if changed:
                    dirty_samples.append((r[ci], fixed))
                    if len(dirty_samples) >= 3:
                        break
        if prof.get("placeholder"):
            flags.append(("P1", "placeholder",
                          "%d 个占位符（--/待定/无/NA），它们不是有效数据，参与统计会算错" % prof["placeholder"]))
        if dirty_samples:
            flags.append(("P1", "invisible-chars",
                          "含全角/不可见字符，示例: %s" % "; ".join(
                              "`%s`→`%s`" % (a[:18], b[:18]) for a, b in dirty_samples[:2])))
        if flags:
            col_issues[label] = {"profile": prof, "flags": flags}

    # --- 合计行 / 备注行（行号已在列分析前算出）
    if total_rows:
        issues.append({
            "sev": "P1", "code": "total-rows",
            "msg": "数据区混入了 %d 个合计/小计行（行号 %s），直接求和会翻倍" % (
                len(total_rows), ", ".join(str(i + 1) for i in total_rows[:8])),
            "fix": "--drop-total 剔除（或 --tag-total 打标记保留）",
        })
    if note_rows:
        issues.append({
            "sev": "P2", "code": "note-rows",
            "msg": "末尾有 %d 个备注/说明行" % len(note_rows),
            "fix": "默认剔除到 note 区",
        })

    # --- 表头自身问题
    if hrow < nrows:
        hdr = rows[hrow]
        empty_hdr = [i for i, v in enumerate(hdr) if v is None or (isinstance(v, str) and not v.strip())]
        if empty_hdr:
            issues.append({
                "sev": "P1", "code": "empty-header",
                "msg": "表头有 %d 个空列名（%s），多半是合并单元格的右半边" % (
                    len(empty_hdr), ", ".join(X.idx_to_col(i) for i in empty_hdr[:6])),
                "fix": "合并单元格向下+向右填充后重命名为 主列名_N",
            })
        seen, dup = {}, []
        for i, v in enumerate(hdr):
            if isinstance(v, str) and v.strip():
                k = normalize_text(v)[0]
                if k in seen:
                    dup.append("%s(列%s与列%s)" % (k, X.idx_to_col(seen[k]), X.idx_to_col(i)))
                else:
                    seen[k] = i
        if dup:
            issues.append({
                "sev": "P1", "code": "dup-header",
                "msg": "表头有重复列名: %s" % ", ".join(dup[:4]),
                "fix": "自动加后缀 _2/_3",
            })

    return issues, col_issues, (hrow, hconf, hreason)


def build_enhanced(rows, hrow):
    """
    五个来自市场高频需求的增强检测，全部只读。

    统计口径：先剔掉合计行与备注行，否则"注：数据截至3月31日"
    这类文字会混进重复值和同义值的统计里。
    """
    if not rows or hrow >= len(rows):
        return {}
    hdr = [str(v).strip() if (v is not None and str(v).strip())
           else "列%s" % X.idx_to_col(i) for i, v in enumerate(rows[hrow])]
    keep = []
    for r in rows[hrow + 1:]:
        if is_blank_row(r):
            continue
        first = str(r[0]).strip() if r and r[0] is not None else ""
        joined = " ".join(str(v) for v in r if v is not None).strip()
        if TOTAL_ROW_HINT.match(first) or TOTAL_ROW_HINT.match(joined) or NOTE_ROW_HINT.match(first):
            continue
        keep.append(r)
    if not keep:
        return {}
    return {
        "duplicates": extras.find_duplicates(hdr, keep),
        "composite": extras.detect_composite(hdr, keep),
        "extractable": extras.detect_extractable(hdr, keep),
        "synonyms": extras.detect_synonyms(hdr, keep),
        "selfcheck": extras.self_check(hdr, keep),
    }


def render_enhanced(enh):
    if not enh:
        return ""
    L = []
    d = enh.get("duplicates") or {}
    if d:
        L.append("## 重复值")
        L.append("")
        if d["full_row_dup_groups"]:
            L.append("- **整行完全重复**：%d 组，删掉可省 %d 行" % (
                d["full_row_dup_groups"], d["full_row_removable"]))
            for e in d["full_row_examples"][:3]:
                L.append("  - 保留第 %d 行，第 %s 行与它重复：`%s`" % (
                    e["keep_row"], ", ".join(str(x) for x in e["dup_rows"]),
                    e["preview"].replace("|", "\\|")))
        else:
            L.append("- 整行完全重复：**没有**")
        if d["by_column"]:
            L.append("")
            L.append("按单列看有重复的——**这些多半不是真重复**，一张单据本来就能有多个明细行：")
            L.append("")
            L.append("| 列 | 重复值个数 | 涉及行 | 示例 |")
            L.append("|---|---|---|---|")
            for col, info in list(d["by_column"].items())[:6]:
                ex = "; ".join("%s → 行%s" % (e["value"], ",".join(str(r) for r in e["rows"][:4]))
                               for e in info["examples"][:2])
                L.append("| %s | %d | %d | %s |" % (
                    col.replace("|", "\\|"), info["dup_values"],
                    info["affected_rows"], ex.replace("|", "\\|")))
        L.append("")
        if d["full_row_removable"]:
            L.append("> 确认要删：清洗时加 `--dedupe`（默认不删）")
        L.append("")

    comp = enh.get("composite") or []
    if comp:
        L.append("## 可以拆开的复合列")
        L.append("")
        L.append("| 列 | 分隔符 | 段数 | 覆盖率 | 样例 | 拆成 |")
        L.append("|---|---|---|---|---|---|")
        for x in comp:
            L.append("| %s | %s | %d | %.0f%% | `%s` | %s |" % (
                x["column"].replace("|", "\\|"), x["delimiter_name"], x["segments"],
                x["ratio"] * 100, x["sample"].replace("|", "\\|"),
                " / ".join(x["preview"]).replace("|", "\\|")))
        L.append("")
        L.append("> 执行：`%s`" % comp[0]["suggest"])
        L.append("")

    ext = enh.get("extractable") or []
    if ext:
        L.append("## 可以从文本里提取的结构化信息")
        L.append("")
        L.append("| 列 | 能提取 | 覆盖率 | 样例 | 提取结果 |")
        L.append("|---|---|---|---|---|")
        for x in ext:
            L.append("| %s | %s | %.0f%% | `%s` | `%s` |" % (
                x["column"].replace("|", "\\|"), x["kind"], x["ratio"] * 100,
                x["sample"].replace("|", "\\|"), x["extracted"]))
        L.append("")
        L.append("> 执行：`%s`" % ext[0]["suggest"])
        L.append("")

    syn = enh.get("synonyms") or []
    if syn:
        L.append("## 疑似同一个东西的不同写法")
        L.append("")
        L.append("这类写法会让分组统计把一家公司拆成两行。**不会自动合并**，交给你定：")
        L.append("")
        L.append("| 列 | 置信 | 写法 | 出现次数 | 判断依据 |")
        L.append("|---|---|---|---|---|")
        for ci in syn:
            for p in ci["pairs"][:6]:
                L.append("| %s | %s | %s | %s | %s |" % (
                    ci["column"].replace("|", "\\|"), p["level"],
                    " / ".join("`%s`" % v for v in p["values"]),
                    " / ".join(str(c) for c in p["counts"]), p["reason"]))
        L.append("")

    sc = enh.get("selfcheck") or {}
    if sc:
        L.append("## 数据达标情况")
        L.append("")
        L.append("**%.1f%%** —— %s" % (sc["score"] * 100, sc["verdict"]))
        L.append("")
        L.append("| 列 | 目标类型 | 达标率 | 不合规 | 占位符 |")
        L.append("|---|---|---|---|---|")
        for c in sc["columns"]:
            L.append("| %s | %s | %.0f%% | %d | %d |" % (
                c["column"].replace("|", "\\|"), c["target"], c["rate"] * 100,
                c["violation_count"], c["placeholders"]))
        L.append("")
    return "\n".join(L)


def render_md(path, data, rows, sheet_name, merges, issues, col_issues, hdr_info, enh=None, preview=8):
    L = []
    hrow, hconf, hreason = hdr_info
    L.append("# 表格体检报告")
    L.append("")
    L.append("- **文件**: `%s`" % path)
    L.append("- **类型**: %s" % ("Excel (.xlsx)" if data["kind"] == "xlsx" else "文本表格"))
    L.append("- **编码**: %s" % data.get("encoding"))
    if data.get("delimiter"):
        dm = {",": "逗号", "\t": "Tab", ";": "分号", "|": "竖线"}.get(data["delimiter"], repr(data["delimiter"]))
        L.append("- **分隔符**: %s" % dm)
    if sheet_name:
        L.append("- **工作表**: %s" % sheet_name)
    if data["kind"] == "xlsx" and len(data["sheets"]) > 1:
        L.append("- **全部 sheet**: %s" % ", ".join(s.name for s in data["sheets"]))
    L.append("- **规模**: %d 行 × %d 列" % (len(rows), max(len(r) for r in rows) if rows else 0))
    L.append("- **判定表头行**: 第 %d 行（置信度 %.2f，%s）" % (hrow + 1, hconf, hreason))
    L.append("")

    if not issues and not col_issues:
        L.append("## 结论：没发现明显脏数据，可以直接用。")
        return "\n".join(L)

    p0 = [i for i in issues if i["sev"] == "P0"]
    p1 = [i for i in issues if i["sev"] == "P1"]
    p2 = [i for i in issues if i["sev"] == "P2"]

    L.append("## 结论")
    if p0:
        L.append("**有 %d 个必须先修的问题（P0）**，不修数据没法直接用：" % len(p0))
        for i in p0:
            L.append("- %s" % i["msg"])
    elif p1:
        L.append("没有致命问题，但有 %d 处会影响分析准确性（P1），建议清洗。" % len(p1))
    else:
        L.append("只有轻微问题（P2），可选清洗。")
    L.append("")

    L.append("## 问题清单")
    L.append("")
    L.append("| 级别 | 问题 | 说明 | 建议处理 |")
    L.append("|---|---|---|---|")
    for i in sorted(issues, key=lambda x: SEV_ORDER[x["sev"]]):
        L.append("| %s | %s | %s | %s |" % (
            i["sev"], i["code"], i["msg"].replace("|", "\\|"), i.get("fix", "")))
    L.append("")

    if col_issues:
        L.append("## 逐列诊断")
        L.append("")
        L.append("| 列 | 有效值 | 类型构成 | 问题 |")
        L.append("|---|---|---|---|")
        for label, info in col_issues.items():
            t = info["profile"]["types"]
            tstr = ", ".join("%s×%d" % (k, v) for k, v in sorted(t.items(), key=lambda kv: -kv[1]))
            fl = "<br>".join("[%s] %s" % (s, m) for s, _c, m in info["flags"])
            L.append("| %s | %d | %s | %s |" % (
                str(label).replace("|", "\\|"), info["profile"]["n"], tstr, fl.replace("|", "\\|")))
        L.append("")

    L.append("## 原始前 %d 行预览" % preview)
    L.append("")
    L.append("```")
    for r in rows[:preview]:
        cells = []
        for v in r[:10]:
            if v is None:
                cells.append("")
            else:
                s = str(v)
                cells.append(s if len(s) <= 16 else s[:15] + "…")
        L.append(" | ".join(cells))
    L.append("```")
    L.append("")
    if enh:
        L.append(render_enhanced(enh))
    L.append("## 建议的清洗命令")
    L.append("")
    cmd = ["python", "clean_sheet.py", '"%s"' % path]
    if hrow != 0:
        cmd.append("--header-row %d" % (hrow + 1))
    if any(i["code"] == "multi-block" for i in issues):
        cmd.append("--split-blocks")
    if any(i["code"] == "total-rows" for i in issues):
        cmd.append("--drop-total")
    if data["kind"] == "xlsx" and len(data["sheets"]) > 1 and sheet_name != data["sheets"][0].name:
        cmd.append('--sheet "%s"' % sheet_name)
    L.append("```bash\n%s\n```" % " ".join(cmd))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="表格体检（只读）")
    ap.add_argument("path")
    ap.add_argument("--sheet", default=None, help="sheet 序号(0基)或名字")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--scan", type=int, default=15, help="表头搜索范围，默认前 15 行")
    args = ap.parse_args()

    if not os.path.exists(args.path):
        print("错误: 文件不存在 %s" % args.path, file=sys.stderr)
        return 2
    try:
        data = X.load_table(args.path)
    except ValueError as e:
        print("错误: %s" % e, file=sys.stderr)
        return 2
    except Exception as e:
        print("错误: 读不了这个文件（%s: %s）" % (type(e).__name__, e), file=sys.stderr)
        return 2

    sheet = args.sheet
    if sheet is not None and sheet.lstrip("-").isdigit():
        sheet = int(sheet)
    data["path"] = args.path

    rows, sheet_name, merges = extract_grid(data, sheet)
    if rows is None:
        print("错误: 文件里没有可读取的工作表", file=sys.stderr)
        return 2

    issues, col_issues, hdr_info = find_issues(
        rows, merges, data.get("encoding"), data.get("delimiter"), sheet_name)
    enh = build_enhanced(rows, hdr_info[0])

    if args.json:
        print(json.dumps({
            "file": args.path,
            "kind": data["kind"],
            "encoding": data.get("encoding"),
            "delimiter": data.get("delimiter"),
            "sheet": sheet_name,
            "sheets": [s.name for s in data.get("sheets", [])],
            "shape": [len(rows), max(len(r) for r in rows) if rows else 0],
            "header_row": hdr_info[0],
            "header_confidence": round(hdr_info[1], 3),
            "merged_cells": merges,
            "issues": issues,
            "enhanced": enh,
            "columns": {k: {"profile": v["profile"], "flags": [[s, c, m] for s, c, m in v["flags"]]}
                        for k, v in col_issues.items()},
        }, ensure_ascii=False, indent=2))
    else:
        print(render_md(args.path, data, rows, sheet_name, merges, issues, col_issues, hdr_info, enh))

    return 1 if any(i["sev"] == "P0" for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
