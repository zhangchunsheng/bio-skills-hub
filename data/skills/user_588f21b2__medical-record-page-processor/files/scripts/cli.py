# -*- coding: utf-8 -*-
"""病案首页数据处理器 —— 命令行入口。

用法（三种模式）：
    python scripts/cli.py report  <文件/目录> [--outdir DIR]   # 全套：清洗+校验+指标+HTML 报告（默认）
    python scripts/cli.py profile <文件/目录>                  # 只摸底：字段识别 + 数据概览
    python scripts/cli.py check   <文件/目录>                  # 只质控：问题清单
    python scripts/cli.py sample  [目录]                       # 生成演示用模拟病案首页数据
    python scripts/cli.py --doctor                             # 环境与资产自检

成功时 stdout 输出单行 JSON（含 kpi / facts / 质量摘要），供上层写解读；
报告与附表落在 --outdir。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001 - 老终端可能不支持
    pass

import pandas as pd  # noqa: E402

from fields import CANON_SPEC, DERIVED_FIELDS, guess_class, match_columns  # noqa: E402
from loader import LoaderError, load  # noqa: E402
from quality import run_checks  # noqa: E402
import aggregate  # noqa: E402
import indicators  # noqa: E402
import report as report_mod  # noqa: E402

DEFAULT_OUTDIR = "病案首页分析输出"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--doctor" in argv:
        return doctor()
    p = _build_parser()
    args = p.parse_args(argv)
    try:
        if args.mode == "sample":
            return _run_sample(args)
        if args.mode in ("report", "profile", "check"):
            return _run(args)
        p.print_help()
        return 0
    except LoaderError as exc:
        return _fail(exc.code_name, exc.message, exc.suggestion)
    except Exception as exc:  # noqa: BLE001 - 兜底给可读错误
        tb = traceback.format_exc(limit=3)
        return _fail("internal_error", f"{type(exc).__name__}: {exc}",
                     "这是工具内部错误，请把以下堆栈反馈给维护者：\n" + tb)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="medrec", description="病案首页结构化数据表格处理器")
    p.add_argument("mode", nargs="?", default="report",
                   choices=["report", "profile", "check", "sample"],
                   help="report=全套报告（默认）；profile=字段与数据摸底；check=仅质控；sample=生成模拟数据")
    p.add_argument("input", nargs="?", help="输入文件、目录或通配符")
    p.add_argument("--outdir", default=None, help=f"输出目录（默认 ./{DEFAULT_OUTDIR}）")
    p.add_argument("--sheet", default=None, help="Excel 工作表名或序号")
    p.add_argument("--header-row", type=int, default=None,
                   help="表头所在行（0 基）。留空自动探测")
    p.add_argument("--encoding", default=None, help="CSV 编码，如 gb18030")
    p.add_argument("--sep", default=None, help="CSV 分隔符")
    p.add_argument("--keep-identifiers", action="store_true",
                   help="保留姓名/身份证等直接标识符（默认剔除，且不写入任何输出）")
    p.add_argument("--los-offset", type=int, choices=[0, 1], default=0,
                   help="住院天数口径：0=出院-入院（默认）；1=首尾日均计")
    p.add_argument("--age-bins", default=None,
                   help="年龄段切点，逗号分隔，如 0,18,45,60,75,200")
    p.add_argument("--theme", default="light", choices=["light", "dark"])
    p.add_argument("--title", default=None, help="报告主标题（默认按结论自动生成）")
    p.add_argument("--subtitle", default=None, help="报告副标题（口径说明）")
    p.add_argument("--annotation", default=None, help="解读文字（写入报告「解读」区块）")
    p.add_argument("--annotation-file", default=None, help="从文件读解读文字")
    p.add_argument("--max-rows", type=int, default=None, help="只处理前 N 行（试跑用）")
    p.add_argument("--export-clean", action="store_true", help="导出清洗后的数据 CSV")
    p.add_argument("--show-ids", action="store_true",
                   help="质控样例中显示完整病案号（默认打码，仅科内核对时使用）")
    p.add_argument("--no-facts-file", action="store_true", help="不写事实卡 JSON")
    return p


# ---------------------------------------------------------------------------
def _run(args) -> int:
    if not args.input:
        return _fail("missing_input", "缺少输入路径",
                     "用法：python scripts/cli.py report <文件或目录> --outdir ./out")
    outdir = os.path.abspath(args.outdir or DEFAULT_OUTDIR)
    os.makedirs(outdir, exist_ok=True)

    loaded = load(args.input, sheet=_sheet(args.sheet), encoding=args.encoding,
                  sep=args.sep, header_row=args.header_row)
    raw = loaded["df"]
    if args.max_rows:
        raw = raw.head(args.max_rows)
    warnings = list(loaded["warnings"])

    # 字段识别
    cols = [c for c in raw.columns if c != "__source_file__"]
    match = match_columns(cols)
    match["mapping"]["__source_file__"] = "数据来源文件"

    # 定型 + 隐私剔除
    can = indicators.canonicalize(raw, match["mapping"],
                                  drop_privacy=not args.keep_identifiers)
    d = can["df"]
    if args.keep_identifiers and can["privacy_cols"]:
        warnings.append("已按 --keep-identifiers 保留直接标识符，请注意数据安全与合规风险。")
    elif can["privacy_cols"]:
        warnings.append(
            f"检测到 {len(can['privacy_cols'])} 个直接标识符字段，已自动剔除且未写入任何输出。")

    # 派生指标
    cfg = {"los_offset": args.los_offset}
    if args.age_bins:
        bins = [float(x) for x in str(args.age_bins).split(",")]
        labels = [f"{int(bins[i])}-{int(bins[i + 1]) - 1}岁" for i in range(len(bins) - 1)]
        labels[-1] = f"{int(bins[-2])}岁及以上"
        cfg["age_bins"] = bins
        cfg["age_labels"] = labels
    d = indicators.derive(d, cfg)

    # 质控
    qual = run_checks(d, can["privacy_cols"], cfg)
    if not args.show_ids:
        from quality import mask_samples
        mask_samples(qual["issues"])
        qual["ids_masked"] = True
    kpi = indicators.kpis(d)
    charts = aggregate.build_charts(d, cfg)

    meta = _build_meta(args, loaded, raw, d, match, can, warnings)

    result = {
        "success": True, "mode": args.mode, "outdir": outdir,
        "source_rows": int(len(raw)), "plotted_rows": int(len(d)),
        "columns": int(len(cols)),
        "mapped_fields": len(_mapping_rows(match)),
        "unmapped_fields": len(match["unmapped"]),
        "privacy_dropped": can["privacy_cols"],
        "quality": {"score": qual["score"], "summary": qual["summary"]},
        "kpi": kpi,
        "charts": [{"id": c["id"], "type": c["type"], "title": c["title"],
                    "facts": c["facts"], "data_rows": len(c.get("categories", c.get("data", [])))}
                   for c in charts],
        "warnings": warnings,
        "outputs": [],
    }

    # 附表输出
    _export_tables(outdir, result, match, can, d, qual, args)

    if args.mode == "profile":
        _write_json(os.path.join(outdir, "字段识别与数据概览.json"),
                    {"meta": meta, "mapping": _mapping_rows(match),
                     "unmapped": _unmapped_rows(match, raw)})
        result["outputs"].append("字段识别与数据概览.json")
        _emit(result)
        return 0

    if args.mode == "check":
        result.pop("charts", None)
        _emit(result)
        return 0

    # report 模式
    ann, src = _annotation(args)
    if src == "default":
        ann = _default_annotation(meta, kpi, qual, charts)
    payload = {"meta": meta, "kpis": kpi, "charts": charts, "quality": qual,
               "mapping": {"pairs": _mapping_rows(match)}, "annotation": ann}
    html = report_mod.render(payload, theme=args.theme)
    html_path = os.path.join(outdir, "病案首页分析报告.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    result["html_path"] = html_path
    result["annotation_source"] = src
    result["outputs"].append("病案首页分析报告.html")
    if src == "default":
        result["advisory"] = ("当前报告的「解读」区块由模板生成。请读取本 JSON 的 kpi / "
                              "charts[].facts 后撰写解读，用 --annotation 重新生成一次。")
    if not args.no_facts_file:
        facts_path = os.path.join(outdir, "事实卡.json")
        _write_json(facts_path, {"meta": meta, "kpi": kpi, "quality": qual["summary"],
                                 "score": qual["score"],
                                 "charts": [{"id": c["id"], "title": c["title"],
                                             "subtitle": c["subtitle"], "facts": c["facts"]}
                                            for c in charts]})
        result["facts_path"] = facts_path
        result["outputs"].append("事实卡.json")
    _emit(result)
    return 0


def _sheet(raw):
    if raw is None:
        return None
    return int(raw) if str(raw).isdigit() else raw


def _annotation(args) -> tuple[str | None, str]:
    if args.annotation_file:
        with open(args.annotation_file, "r", encoding="utf-8") as fh:
            return fh.read(), "user"
    if args.annotation:
        return args.annotation, "user"
    return None, "default"


def _build_meta(args, loaded, raw, d, match, can, warnings) -> dict:
    files = loaded["files"]
    key_date = None
    for col in ("出院日期", "入院日期"):
        if col in d.columns and d[col].notna().any():
            key_date = d[col]
            break
    span = "—"
    if key_date is not None:
        span = (f"{key_date.min():%Y-%m-%d} ~ {key_date.max():%Y-%m-%d}")
    source = os.path.basename(os.path.abspath(args.input.rstrip("/\\")))
    if len(files) > 1:
        source = f"{source}/（{len(files)} 个文件）"
    return {
        "title": args.title or "病案首页数据分析报告",
        "subtitle": args.subtitle or (
            f"数据源：{source}；共 {len(raw):,} 条记录；出院/入院日期跨度 {span}；"
            f"字段识别 {len(_mapping_rows(match))}/{len(raw.columns) - 1} 列"),
        "source": source, "rows": int(len(d)), "file_count": len(files),
        "span": span, "mapped_count": len(_mapping_rows(match)),
        "column_count": max(0, len(raw.columns) - 1),
        "unmapped": match["unmapped"],
        "privacy_cols": can["privacy_cols"],
        "header_rows": {f["file_name"]: f["header_row"] for f in files},
        "warnings": warnings,
        "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": [{"name": f["file_name"], "rows": f["rows"],
                   "header_row": f["header_row"] + 1,
                   "header_confidence": f["header_confidence"]} for f in files],
    }


def _default_annotation(meta, kpi, qual, charts) -> str:
    """模板解读（仅在调用方未提供解读时兜底使用）。"""
    lines = [f"本报告基于 {meta['rows']:,} 条病案首页记录（{meta['span']}）生成，"
             f"数据质量评分 {qual['score']} / 100。"]
    if kpi:
        picks = list(kpi.items())[:4]
        lines.append("核心指标：" + "；".join(f"{k} {v['值']}{v['单位']}" for k, v in picks) + "。")
    if charts:
        lines.append("主要发现：" + charts[0]["facts"][0] + "。")
    if qual["summary"].get("致命"):
        lines.append(f"注意：存在 {qual['summary']['致命']} 类致命质量问题，"
                     "相关指标在整改前不宜直接对外引用。")
    return "\n".join(lines)


def _mapping_rows(match) -> list[dict]:
    return [{"原始列名": raw, "标准字段": canon, "置信度": match["confidence"][raw]}
            for raw, canon in match["mapping"].items() if raw != "__source_file__"]


def _unmapped_rows(match, raw) -> list[dict]:
    return [{"原始列名": c, "语义猜测": guess_class(c),
             "示例值": str(raw[c].dropna().iloc[0])[:40] if raw[c].notna().any() else ""}
            for c in match["unmapped"]]


def _export_tables(outdir, result, match, can, d, qual, args) -> None:
    mp = os.path.join(outdir, "字段映射表.csv")
    pd.DataFrame(_mapping_rows(match)).to_csv(mp, index=False, encoding="utf-8-sig")
    result["outputs"].append("字段映射表.csv")

    rows = []
    for i in qual["issues"]:
        rows.append({"规则编号": i["rule"], "问题类型": i["severity"], "问题描述": i["name"],
                     "命中条数": i["count"], "占比": f"{i['rate'] * 100:.2f}%",
                     "样例": " | ".join(
                         f"{s['记录标识']} " + "，".join(
                             f"{k}={v}" for k, v in (s.get('明细') or {}).items())
                         for s in i.get("samples", [])),
                     "整改建议": i.get("advice", "")})
    qp = os.path.join(outdir, "质控问题清单.csv")
    pd.DataFrame(rows or [{"规则编号": "—", "问题类型": "—", "问题描述": "未发现质控问题",
                           "命中条数": 0, "占比": "", "样例": "", "整改建议": ""}]
                 ).to_csv(qp, index=False, encoding="utf-8-sig")
    result["outputs"].append("质控问题清单.csv")

    if args.export_clean:
        cols = [c for c in d.columns if c not in DERIVED_FIELDS or c in
                ("住院天数", "年龄段", "年份", "年月", "有无手术", "是否死亡", "药占比", "耗占比")]
        out = d[cols].copy()
        for c in out.columns:
            if pd.api.types.is_datetime64_any_dtype(out[c]):
                out[c] = out[c].dt.strftime("%Y-%m-%d")
        cp = os.path.join(outdir, "清洗后数据.csv")
        out.to_csv(cp, index=False, encoding="utf-8-sig")
        result["outputs"].append("清洗后数据.csv")


def _run_sample(args) -> int:
    import make_sample
    outdir = os.path.abspath(args.outdir or args.input or ".")
    paths = make_sample.generate(outdir)
    _emit({"success": True, "mode": "sample", "outdir": outdir,
           "files": paths, "note": "模拟数据仅用于演示与自测，非真实患者数据。"})
    return 0


def doctor() -> int:
    import platform
    info = {"python": sys.version.split()[0], "platform": platform.platform()}
    for mod in ("pandas", "numpy", "openpyxl", "xlrd"):
        try:
            m = __import__(mod)
            info[mod] = getattr(m, "__version__", "unknown")
        except Exception as exc:  # noqa: BLE001
            info[mod] = f"缺失（{exc}）"
    assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "echarts.min.js")
    info["echarts_asset"] = (f"OK ({os.path.getsize(assets) // 1024} KB)"
                             if os.path.exists(assets) else "缺失：图表无法离线渲染")
    _emit({"success": True, "mode": "doctor", **info})
    return 0


def _write_json(path: str, obj) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, default=str)


def _emit(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, default=str))


def _fail(code_name: str, message: str, suggestion: str = "") -> int:
    print(json.dumps({"success": False,
                      "error": {"code_name": code_name, "message": message,
                                "suggestion": suggestion}}, ensure_ascii=False, default=str))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
