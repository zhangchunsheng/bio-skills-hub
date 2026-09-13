# -*- coding: utf-8 -*-
"""把「WorkBuddy 会话内模型」产出的 10 维度分析 JSON 写入分析库。

用途：配合 cloud_doc_run.py --no-ai 使用，让 AI 分析这一步由当前会话模型完成，
      完全不调用 backend/.env 里配置的外部模型（不产生外部 API 费用）。

用法：
    python write_session_analysis.py --id 101 --json analysis.json
    python write_session_analysis.py --id 101 --json analysis.json --db <自定义db路径>

analysis.json 必须是一个包含以下 10 个顶层 key 的对象（schema 见
backend_shared/app/services/prompts/generic_overall_analysis_prompt.txt）：
    executive_summary, data_quality_check, critical_business_issues,
    root_cause_analysis, logic_chain_review, strategy_effectiveness,
    replicable_highlights, recommendations, information_gaps, final_assessment

写入后执行：python generic_run.py --id <id> --h5-only --out "输出.html"
"""
import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_KEYS = [
    "executive_summary",
    "data_quality_check",
    "critical_business_issues",
    "root_cause_synthesis",
    "logic_chain_review",
    "strategy_effectiveness",
    "replicable_highlights",
    "recommendations",
    "information_gaps",
    "final_assessment",
]


def find_db(explicit: str = "") -> Path:
    """定位 analysis.db：显式参数 > 环境变量 > WB_BACKEND > 常见位置。"""
    cands = []
    if explicit:
        cands.append(Path(explicit))
    if os.environ.get("WB_ANALYSIS_DB"):
        cands.append(Path(os.environ["WB_ANALYSIS_DB"]))
    if os.environ.get("WB_BACKEND"):
        cands.append(Path(os.environ["WB_BACKEND"]) / "data" / "analysis.db")
    cands.append(Path(r"D:\Python代码源\报告分析系统\backend\data\analysis.db"))
    for p in cands:
        if p.exists():
            return p
    raise SystemExit("[✗] 找不到 analysis.db，请用 --db 指定或设置 WB_ANALYSIS_DB / WB_BACKEND")


def main():
    ap = argparse.ArgumentParser(description="写入会话内模型的 10 维度分析结果")
    ap.add_argument("--id", type=int, required=True, help="analyses 表记录 id")
    ap.add_argument("--json", required=True, help="10 维度分析 JSON 文件路径")
    ap.add_argument("--db", default="", help="analysis.db 路径（默认自动探测）")
    ap.add_argument("--model", default="",
                    help="实际做分析的模型名，会显示在 H5 头部（不填则 H5 显示 .env 的 DEFAULT_MODEL，"
                         "会与事实不符）。会话内分析请填当前 WorkBuddy 所选模型名")
    args = ap.parse_args()

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("[✗] JSON 顶层必须是对象")

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise SystemExit(f"[✗] 缺少维度: {missing}\n    H5 会出现空白区块，请补齐后重试")

    empty = [k for k in REQUIRED_KEYS if not data[k]]
    if empty:
        print(f"[!] 警告：以下维度内容为空，H5 对应区块将空白: {empty}")

    db = find_db(args.db)
    raw = json.dumps(data, ensure_ascii=False)
    conn = sqlite3.connect(str(db))
    cur = conn.execute("SELECT id FROM analyses WHERE id=?", (args.id,))
    if cur.fetchone() is None:
        raise SystemExit(f"[✗] analyses 表里没有 id={args.id} 的记录（先跑 cloud_doc_run.py --no-ai）")
    if args.model:
        # H5 头部的模型名取自 tags 里的 "model:xxx"，不标注会错显示成 .env 的 DEFAULT_MODEL
        conn.execute(
            "UPDATE analyses SET overall_analysis=?, status='completed', tags=? WHERE id=?",
            (raw, f"model:{args.model}", args.id),
        )
    else:
        conn.execute(
            "UPDATE analyses SET overall_analysis=?, status='completed' WHERE id=?",
            (raw, args.id),
        )
        print("[!] 未指定 --model，H5 头部会显示 .env 的 DEFAULT_MODEL（与实际分析模型不符）")
    conn.commit()
    conn.close()

    print(f"[✓] 已写入 id={args.id}，维度 {len(data)}/10，长度 {len(raw)} 字符"
          + (f"，模型标注={args.model}" if args.model else ""))
    print(f"    DB: {db}")
    print(f"    下一步: python generic_run.py --id {args.id} --h5-only --out \"输出.html\"")


if __name__ == "__main__":
    main()
