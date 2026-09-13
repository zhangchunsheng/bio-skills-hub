#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_sheet —— 中文脏表格清洗。输出干净 CSV + 可追溯的变更日志。

用法:
  python clean_sheet.py 脏表.xlsx
  python clean_sheet.py 脏表.csv --header-row 3 --drop-total
  python clean_sheet.py 脏表.xlsx --split-blocks --out 输出目录/
  python clean_sheet.py 脏表.xlsx --percent decimal    # 35% -> 0.35

产出（不覆盖原文件）:
  <原名>_clean.csv        干净数据，UTF-8-BOM，Excel/WPS 双击不乱码
  <原名>_clean.report.md  人看的变更报告
  <原名>_clean.changes.json  机器可读的逐处改动

安全原则:
  - 不覆盖源文件
  - 不把空值填成 0（不制造假数据）
  - "100-200" 这类范围只取下限并标记，不猜中值
  - 低置信度转换一律标记出来交给人判断
"""

import argparse
import json
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xlsx_lite as X
import extras
from inspect_sheet import render_enhanced
from dirty_rules import (
    normalize_text, normalize_brackets, parse_number, parse_date,
    is_blank_row, detect_header_row, detect_blocks,
    TOTAL_ROW_HINT, NOTE_ROW_HINT, PLACEHOLDER,
)

MAX_CHANGES = 800  # 变更日志上限，超出只汇总，避免日志比数据还大
ISO_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")


def find_suspects(header, rows):
    """
    清洗之后仍然可疑的值。原则是**不猜、不改，只列出来交给人判断**。

    两类最常坑人的残留：
      1. 数字列里混进文本——"含退货""待定"，求和时会直接报错或静默跳过
      2. 日期列里没认出来的——"1/12" 缺年份，且 1月12日 / 12月1日 两种解读都说得通
    """
    suspects = []
    for ci, name in enumerate(header):
        vals = [(i, r[ci]) for i, r in enumerate(rows)
                if ci < len(r) and r[ci] is not None and r[ci] != ""]
        if not vals:
            continue
        nums = [v for _, v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
        isos = [v for _, v in vals if isinstance(v, str) and ISO_RE.match(v)]

        if len(nums) >= max(2, len(vals) * 0.5):
            for i, v in vals:
                if isinstance(v, str) and v.strip():
                    suspects.append({
                        "column": name, "row": i + 2, "value": v,
                        "issue": "数字列里混了文本",
                        "hint": "像占位符，建议置空" if PLACEHOLDER.match(v) else "需人工判断是否改数或置空",
                    })
        elif len(isos) >= max(2, len(vals) * 0.5):
            for i, v in vals:
                if not (isinstance(v, str) and ISO_RE.match(v)):
                    suspects.append({
                        "column": name, "row": i + 2, "value": v,
                        "issue": "日期列里有没认出来的格式",
                        "hint": "缺年份或分隔符有歧义（如 1/12 可能是1月12日或12月1日），请人工核对",
                    })
    return suspects[:200]


def parse_merge(ref):
    """'A1:C1' -> (r1, c1, r2, c2) 0 基闭区间。"""
    try:
        a, b = ref.split(":") if ":" in ref else (ref, ref)
    except ValueError:
        return None
    def split(cell):
        m = __import__("re").match(r"([A-Za-z]+)(\d+)", cell)
        if not m:
            return None
        return int(m.group(2)) - 1, X.col_to_idx(m.group(1))
    p1, p2 = split(a), split(b)
    if not p1 or not p2:
        return None
    return (min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1]))


def fill_merges(rows, merges, changes):
    """合并单元格只有左上角有值，把值铺满整个区域。"""
    count = 0
    for ref in merges or []:
        box = parse_merge(ref)
        if not box:
            continue
        r1, c1, r2, c2 = box
        if r1 >= len(rows):
            continue
        if c1 >= len(rows[r1]):
            continue
        src = rows[r1][c1]
        if src is None or (isinstance(src, str) and not src.strip()):
            continue
        for r in range(r1, min(r2 + 1, len(rows))):
            for c in range(c1, min(c2 + 1, len(rows[r]))):
                if r == r1 and c == c1:
                    continue
                if rows[r][c] is None:
                    rows[r][c] = src
                    count += 1
    if count:
        changes["summary"]["merged_fill"] = count
    return rows


def build_header(hdr_row, ci_count):
    """生成干净的列名：空列名补 上级名_N，重复列名加 _2/_3。"""
    names = []
    last = None
    seen = OrderedDict()
    for ci in range(ci_count):
        raw = hdr_row[ci] if ci < len(hdr_row) else None
        nm, _ = normalize_text(raw if isinstance(raw, str) else ("" if raw is None else str(raw)))
        if not nm:
            nm = "%s_%d" % (last or "列", ci + 1) if last else "列%s" % X.idx_to_col(ci)
        base = nm
        if nm in seen:
            seen[nm] += 1
            nm = "%s_%d" % (base, seen[nm] + 1)
        else:
            seen[nm] = 0
        names.append(nm)
        if nm != (raw if isinstance(raw, str) else None):
            last = base
        else:
            last = base
    return names


def clean_cell(v, ci_name, rownum, percent, do_number, do_date, default_year, changes):
    """清洗单个单元格，返回 (新值, 规则名 or None)。"""
    if v is None:
        return None, None
    if isinstance(v, bool):
        return v, None
    if isinstance(v, (int, float)):
        return v, None
    if not isinstance(v, str):
        return v, None

    orig = v
    v, ch1 = normalize_text(v)
    v, ch2 = normalize_brackets(v)
    rule = None
    if ch1 or ch2:
        rule = "normalize-text"
        if ch1:
            changes["summary"]["invisible_chars"] = changes["summary"].get("invisible_chars", 0) + 1

    if v == "":
        return None, rule

    if do_date:
        d = parse_date(v, default_year=default_year)
        if d and d != v:
            changes["summary"]["date_norm"] = changes["summary"].get("date_norm", 0) + 1
            return d, "date-normalize"

    if do_number:
        nv, unit, note = parse_number(v, percent=percent)
        if nv is not None and note not in ("numeric",):
            key = {"text-number": "text_to_number", "percent": "percent",
                   "paren-negative": "paren_negative", "range-take-lower": "range_lower"}.get(note)
            if key is None:
                key = "cn_unit" if unit else "text_to_number"
            changes["summary"][key] = changes["summary"].get(key, 0) + 1
            return nv, ("unit:%s" % unit if unit else note)

    if rule:
        changes["summary"]["normalize_text"] = changes["summary"].get("normalize_text", 0) + 1
    return v, rule


def add_change(changes, row, col, name, before, after, rule):
    if len(changes["items"]) < MAX_CHANGES:
        changes["items"].append({
            "row": row, "col": col, "column": name,
            "before": before if not isinstance(before, (int, float)) else before,
            "after": after, "rule": rule,
        })


def process(data, args, src_path):
    sheet = args.sheet
    if sheet is not None and str(sheet).lstrip("-").isdigit():
        sheet = int(sheet)

    if data["kind"] == "xlsx":
        sheets = data["sheets"]
        if not sheets:
            raise ValueError("没有可读取的工作表")
        if sheet is None:
            sh = sheets[0]
        elif isinstance(sheet, int):
            sh = sheets[min(sheet, len(sheets) - 1)]
        else:
            sh = next((s for s in sheets if s.name == sheet), sheets[0])
        rows = sh.values()
        merges = sh.merges
        sheet_name = sh.name
    else:
        rows = [list(r) for r in data["rows"]]
        merges = []
        sheet_name = "sheet1"

    changes = {"items": [], "summary": {}, "meta": {
        "source": os.path.abspath(src_path),
        "sheet": sheet_name,
        "encoding": data.get("encoding"),
        "delimiter": data.get("delimiter"),
        "shape_before": [len(rows), max(len(r) for r in rows) if rows else 0],
    }}

    # 1. 合并单元格填充
    if merges:
        rows = fill_merges(rows, merges, changes)

    # 2. 定位表头
    if args.header_row:
        hrow = int(args.header_row) - 1
        hconf, hreason = 1.0, "用户指定"
    else:
        hrow, hconf, hreason = detect_header_row(rows, scan=args.scan)
    hrow = max(0, min(hrow, len(rows) - 1)) if rows else 0
    changes["meta"]["header_row"] = hrow + 1
    changes["meta"]["header_confidence"] = round(hconf, 3)

    # 3. 切分标题区 / 表头 / 数据区
    titles = [[str(v) for v in r if v is not None] for r in rows[:hrow] if not is_blank_row(r)]
    hdr_raw = rows[hrow] if rows else []
    body = rows[hrow + 1:]

    # 4. 数据区：剔空行、合计行、备注行
    kept, dropped = [], []
    for off, r in enumerate(body):
        rownum = hrow + off + 2  # 1 基，对应原文件行号
        if is_blank_row(r):
            dropped.append((rownum, "blank", " | ".join("" if v is None else str(v) for v in r)[:40]))
            continue
        first = str(r[0]).strip() if r and r[0] is not None else ""
        joined = " ".join(str(v) for v in r if v is not None).strip()
        if TOTAL_ROW_HINT.match(first) or TOTAL_ROW_HINT.match(joined):
            if args.drop_total:
                dropped.append((rownum, "total", joined[:40]))
                continue
            if args.tag_total:
                r = list(r) + ["__合计行__"]
                while len(r) < len(hdr_raw) + 1:
                    r.append(None)
        elif NOTE_ROW_HINT.match(first):
            dropped.append((rownum, "note", joined[:40]))
            continue
        kept.append((rownum, r))

    ncols_body = max([len(r) for _, r in kept] + [len(hdr_raw)]) if kept else len(hdr_raw)

    # 5. 删全空列
    cols_keep = []
    for ci in range(ncols_body):
        col = []
        if ci < len(hdr_raw):
            col.append(hdr_raw[ci])
        col += [r[ci] if ci < len(r) else None for _, r in kept]
        if any(v is not None and (not isinstance(v, str) or v.strip()) for v in col):
            cols_keep.append(ci)
    dropped_cols = [ci for ci in range(ncols_body) if ci not in cols_keep]
    if dropped_cols:
        changes["summary"]["blank_cols_removed"] = len(dropped_cols)

    hdr = [hdr_raw[ci] if ci < len(hdr_raw) else None for ci in cols_keep]
    names = build_header(hdr, len(cols_keep))
    if any(nm != raw for nm, raw in zip(names, hdr)):
        changes["summary"]["header_fixed"] = sum(1 for nm, raw in zip(names, hdr) if nm != raw)

    # 6. 逐格清洗
    default_year = args.default_year
    out_rows = []
    for rownum, r in kept:
        new = []
        for k, ci in enumerate(cols_keep):
            v = r[ci] if ci < len(r) else None
            nv, rule = clean_cell(v, names[k], rownum, args.percent,
                                  not args.no_number, not args.no_date,
                                  default_year, changes)
            if rule and nv != v:
                add_change(changes, rownum, X.idx_to_col(ci), names[k], v, nv, rule)
            new.append(nv)
        out_rows.append(new)

    changes["summary"]["rows_dropped"] = len(dropped)
    changes["summary"]["rows_out"] = len(out_rows)
    changes["meta"]["suspects"] = find_suspects(names, out_rows)
    changes["meta"]["dropped_rows"] = [{"row": rn, "kind": k, "preview": p} for rn, k, p in dropped[:200]]
    changes["meta"]["titles"] = titles[:5]
    # 8. 增强处理。全部只在用户显式要求时才动数据，默认一条都不执行
    if args.dedupe or args.dedupe_by:
        subset = [c.strip() for c in args.dedupe_by.split(",")] if args.dedupe_by else None
        out_rows, dup_removed = extras.dedupe_rows(names, out_rows, subset)
        if dup_removed:
            changes["summary"]["dedupe_removed"] = len(dup_removed)
            changes["meta"]["dedupe_removed_rows"] = dup_removed[:500]

    if args.split_col:
        delim = args.delim if args.delim is not None else " "
        try:
            names, out_rows = extras.split_column(names, out_rows, args.split_col, delim)
            changes["summary"]["split_columns"] = 1
        except ValueError as e:
            print("警告: 拆分跳过（%s）" % e, file=sys.stderr)

    for spec in (args.extract or []):
        if ":" not in spec:
            print("警告: --extract 格式应为 \"列名:类型\"，跳过 %r" % spec, file=sys.stderr)
            continue
        col, kind = spec.split(":", 1)
        col, kind = col.strip(), kind.strip()
        if col not in names:
            print("警告: 没有这一列 %r，跳过提取" % col, file=sys.stderr)
            continue
        ci = names.index(col)
        names = names + ["%s_%s" % (col, kind)]
        hit = 0
        for r in out_rows:
            v = r[ci] if ci < len(r) else None
            ev, _ = extras.extract_pattern(v, kind)
            if ev is not None:
                hit += 1
            while len(r) < len(names) - 1:
                r.append(None)
            r.append(ev)
        changes["summary"]["extracted"] = changes["summary"].get("extracted", 0) + hit

    # 9. 清洗后自检 —— 证明它真的洗干净了，而不是看起来干净
    changes["meta"]["selfcheck"] = extras.self_check(names, out_rows)
    changes["meta"]["enhanced"] = {
        "duplicates": extras.find_duplicates(names, out_rows),
        "composite": extras.detect_composite(names, out_rows),
        "extractable": extras.detect_extractable(names, out_rows),
        "synonyms": extras.detect_synonyms(names, out_rows),
    }

    changes["meta"]["shape_after"] = [len(out_rows) + 1, len(names)]
    changes["meta"]["columns"] = names

    result = {
        "header": names,
        "rows": out_rows,
        "changes": changes,
        "sheet_name": sheet_name,
        "blocks": [],
    }

    # 7. 可选：按空行拆多表
    if args.split_blocks:
        blocks = detect_blocks([hdr_raw] + [r for _, r in kept], 0)
        if len(blocks) > 1:
            result["blocks"] = [
                {"index": i + 1, "start": s + hrow + 2, "end": e + hrow + 1}
                for i, (s, e, _t) in enumerate(blocks)
            ]
    return result


def render_report(res, src_path, out_csv):
    ch = res["changes"]
    s = ch["summary"]
    m = ch["meta"]
    L = []
    L.append("# 清洗报告")
    L.append("")
    L.append("- **源文件**: `%s`%s" % (src_path, ("（sheet: %s）" % res["sheet_name"]) if m.get("sheet") else ""))
    L.append("- **原编码**: %s%s" % (m.get("encoding"), ("（分隔符: %s）" % m.get("delimiter")) if m.get("delimiter") else ""))
    L.append("- **规模变化**: %d 行 × %d 列 → **%d 行 × %d 列**" % (
        m["shape_before"][0], m["shape_before"][1], m["shape_after"][0], m["shape_after"][1]))
    L.append("- **表头行**: 第 %d 行（置信度 %.2f）" % (m["header_row"], m.get("header_confidence", 0)))
    L.append("- **输出**: `%s`" % out_csv)
    L.append("")

    if not s:
        L.append("## 未做任何改动，原表已经是干净的。")
        return "\n".join(L)

    L.append("## 改了什么")
    L.append("")
    L.append("| 项目 | 数量 |")
    L.append("|---|---|")
    label = {
        "merged_fill": "合并单元格向下/向右填充",
        "normalize_text": "全角/不可见字符规范化",
        "invisible_chars": "含不可见字符的单元格",
        "text_to_number": "文本数字 → 真数字",
        "cn_unit": "剥离中文单位（万/亿/元）",
        "percent": "百分号转数值",
        "paren_negative": "(100) → -100",
        "range_lower": "范围值取下限（未猜中值）",
        "date_norm": "中文日期 → ISO",
        "blank_cols_removed": "删除空列",
        "rows_dropped": "删除行（空行/合计/备注）",
        "header_fixed": "修复空/重复列名",
        "rows_out": "最终数据行数",
    }
    for k, v in sorted(s.items(), key=lambda kv: -kv[1] if isinstance(kv[1], int) else 0):
        L.append("| %s | %s |" % (label.get(k, k), "{:,}".format(v) if isinstance(v, int) else v))
    L.append("")

    if m.get("dropped_rows"):
        L.append("## 被剔除的行")
        L.append("")
        L.append("| 原行号 | 类型 | 内容预览 |")
        L.append("|---|---|---|")
        for d in m["dropped_rows"][:20]:
            L.append("| %d | %s | %s |" % (d["row"], d["kind"], str(d["preview"]).replace("|", "\\|")))
        if len(m["dropped_rows"]) > 20:
            L.append("| ... | | 共 %d 行，详见 changes.json |" % len(m["dropped_rows"]))
        L.append("")

    if ch["items"]:
        L.append("## 改动明细（前 30 条）")
        L.append("")
        L.append("| 原行 | 列 | 列名 | 原值 | 新值 | 规则 |")
        L.append("|---|---|---|---|---|---|")
        for it in ch["items"][:30]:
            L.append("| %s | %s | %s | `%s` | `%s` | %s |" % (
                it["row"], it["col"], it["column"],
                str(it["before"])[:28].replace("|", "\\|"),
                str(it["after"])[:28].replace("|", "\\|"),
                it["rule"]))
        if len(ch["items"]) >= MAX_CHANGES:
            L.append("")
            L.append("> 改动超过 %d 条，日志已截断，完整清单见 changes.json" % MAX_CHANGES)
        L.append("")

    suspects = ch["meta"].get("suspects") or []
    if suspects:
        L.append("## 需要你确认的值")
        L.append("")
        L.append("这些值**没有自动改**——改了可能就是错的，交给你判断：")
        L.append("")
        L.append("| 行 | 列名 | 原样保留的值 | 问题 | 建议 |")
        L.append("|---|---|---|---|---|")
        for s2 in suspects[:30]:
            L.append("| %d | %s | `%s` | %s | %s |" % (
                s2["row"], s2["column"], str(s2["value"])[:24].replace("|", "\\|"),
                s2["issue"], s2["hint"]))
        if len(suspects) > 30:
            L.append("| ... | | | 共 %d 处，见 changes.json | |" % len(suspects))
        L.append("")

    sc = ch["meta"].get("selfcheck") or {}
    if sc:
        L.append("## 清洗后自检")
        L.append("")
        L.append("**%.1f%%** —— %s" % (sc["score"] * 100, sc["verdict"]))
        L.append("")
        L.append("| 列 | 目标类型 | 达标率 | 不合规 |")
        L.append("|---|---|---|---|")
        for c in sc["columns"]:
            L.append("| %s | %s | %.0f%% | %d |" % (
                c["column"].replace("|", "\\|"), c["target"],
                c["rate"] * 100, c["violation_count"]))
        L.append("")

    enh = ch["meta"].get("enhanced") or {}
    if enh:
        L.append(render_enhanced(enh))

    if res["blocks"]:
        L.append("## 检测到多个数据块")
        L.append("")
        for b in res["blocks"]:
            L.append("- 第 %d 块：原表第 %d–%d 行" % (b["index"], b["start"], b["end"]))
        L.append("")
        L.append("> 已按连续数据输出，若需拆成独立文件请对每块单独运行。")
        L.append("")

    L.append("## 清洗后预览")
    L.append("")
    L.append("| " + " | ".join(str(h) for h in res["header"][:12]) + " |")
    L.append("|" + "---|" * min(12, len(res["header"])))
    for r in res["rows"][:8]:
        L.append("| " + " | ".join(("" if v is None else str(v))[:20] for v in r[:12]) + " |")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="中文脏表格清洗")
    ap.add_argument("path")
    ap.add_argument("--sheet", default=None, help="sheet 序号(0基)或名字")
    ap.add_argument("--header-row", type=int, default=None, help="表头在原始文件的第几行（1 基）")
    ap.add_argument("--scan", type=int, default=15, help="表头搜索范围")
    ap.add_argument("--out", default=None, help="输出目录，默认与源文件同目录")
    ap.add_argument("--percent", choices=["keep", "decimal"], default="keep",
                    help="百分号处理：keep=35%%→35（默认），decimal=35%%→0.35")
    ap.add_argument("--drop-total", action="store_true", help="剔除合计/小计行")
    ap.add_argument("--tag-total", action="store_true", help="保留合计行但加 __合计行__ 标记")
    ap.add_argument("--split-blocks", action="store_true", help="检测一个 sheet 内的多个数据块")
    ap.add_argument("--default-year", type=int, default=None, help="无年份日期（如 3月5日）的默认年份")
    ap.add_argument("--no-number", action="store_true", help="不做数值转换")
    ap.add_argument("--no-date", action="store_true", help="不做日期转换")
    ap.add_argument("--dedupe", action="store_true",
                    help="删除整行完全重复的行。默认只报告不删，因为一张单据常有多个明细行")
    ap.add_argument("--dedupe-by", default=None,
                    help="按指定列去重（逗号分隔列名），比整行去重激进，慎用")
    ap.add_argument("--split-col", default=None, help="拆分复合列的列名，配合 --delim")
    ap.add_argument("--delim", default=None, help="拆分的分隔符，默认空格")
    ap.add_argument("--extract", action="append", default=None,
                    help='从文本里提取结构化信息，格式 "列名:类型"，'
                         '类型可选 手机号/邮箱/身份证/URL/日期串')
    ap.add_argument("--xlsx", action="store_true", help="若环境有 openpyxl，额外导出 .xlsx")
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
        print("错误: 读不了（%s: %s）" % (type(e).__name__, e), file=sys.stderr)
        return 2

    try:
        res = process(data, args, args.path)
    except Exception as e:
        print("错误: 清洗失败（%s: %s）" % (type(e).__name__, e), file=sys.stderr)
        return 2

    outdir = args.out or os.path.dirname(os.path.abspath(args.path))
    os.makedirs(outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(args.path))[0]

    csv_path = os.path.join(outdir, base + "_clean.csv")
    X.write_csv(csv_path, [res["header"]] + res["rows"])

    md_path = os.path.join(outdir, base + "_clean.report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_report(res, args.path, csv_path))

    js_path = os.path.join(outdir, base + "_clean.changes.json")
    with open(js_path, "w", encoding="utf-8") as f:
        json.dump(res["changes"], f, ensure_ascii=False, indent=2)

    xlsx_note = ""
    if args.xlsx:
        xp = os.path.join(outdir, base + "_clean.xlsx")
        if X.try_write_xlsx(xp, [res["header"]] + res["rows"], res["sheet_name"]):
            xlsx_note = "\n  xlsx:      %s" % xp
        else:
            xlsx_note = "\n  xlsx:      跳过（环境无 openpyxl，CSV 已足够）"

    s = res["changes"]["summary"]
    print("清洗完成")
    print("  规模:      %d行×%d列 → %d行×%d列" % (
        res["changes"]["meta"]["shape_before"][0], res["changes"]["meta"]["shape_before"][1],
        res["changes"]["meta"]["shape_after"][0], res["changes"]["meta"]["shape_after"][1]))
    if s:
        print("  改动:      " + ", ".join("%s×%s" % (k, v) for k, v in sorted(s.items(), key=lambda kv: -kv[1] if isinstance(kv[1], int) else 0)[:6]))
    print("  干净数据:  %s" % csv_path)
    print("  变更报告:  %s" % md_path)
    print("  改动明细:  %s" % js_path + xlsx_note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
