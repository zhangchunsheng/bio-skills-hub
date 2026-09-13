#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
log_learning.py — 技能自我优化学习日志辅助脚本

把每次使用后发现的坑 / 用户纠正 / 能力缺口,以结构化 JSON 行追加进技能根目录的
learnings.jsonl(append-only)。支持列出最近若干条,供复盘与瘦身使用。

用法:
  # 记录一条(自动改)
  python scripts/log_learning.py --type bug --trigger "boxplot 三箱体全蓝" \
      --issue "sns.boxplot 不显式传 palette= 时默认全蓝" \
      --resolution "新增 prism_boxplot() 内置 palette+hue" \
      --files "scripts/prism_theme.py" --status applied \
      --verified "verify_box_v2.py" --safe-auto

  # 记录一条(待确认,不改文件)
  python scripts/log_learning.py --type ambiguous --trigger "用户问小提琴图密度估计" \
      --issue "不确定用哪种 KDE" --resolution "待用户拍板" \
      --files "" --status pending_confirmation

  # 列出最近 10 条(人类可读)
  python scripts/log_learning.py --list 10

  # 全文件体检(报告坏行,不修改)
  python scripts/log_learning.py --check
"""
import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 技能根目录 = scripts/ 的上一级(本脚本位于 scripts/ 下)
SKILL_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = SKILL_ROOT / "learnings.jsonl"

VALID_TYPES = {"bug", "convention", "doc", "gap", "ambiguous"}
VALID_STATUS = {"applied", "pending_confirmation", "reverted"}


def now_iso():
    # 用本地时区(若可用),否则 UTC;保持 ISO-8601 带偏移
    try:
        local = datetime.now().astimezone()
    except Exception:
        local = datetime.now(timezone.utc)
    return local.isoformat()


def parse_files(raw):
    if not raw:
        return []
    return [f.strip() for f in raw.split(",") if f.strip()]


def _validate_line(line):
    """单行 JSON 合法性校验(防坏行入库:拒绝多行/截断/尾缀残留)。"""
    line = line.strip()
    if not line:
        return False
    try:
        json.loads(line)
        return True
    except json.JSONDecodeError:
        return False


def append_entry(entry):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False)
    # 写入前自检:json.dumps 应产出单行合法 JSON(内部换行已被转义为 \n)
    if not _validate_line(line):
        raise ValueError(f"待写入内容不是合法单行 JSON,已拒绝: {line[:120]!r}")
    before = LOG_PATH.stat().st_size if LOG_PATH.exists() else 0
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    # 写入后回读校验:最后一行必须可解析;失败则截断回滚,绝不把坏行留在库里
    try:
        with LOG_PATH.open("r", encoding="utf-8") as f:
            last = [ln for ln in f.read().splitlines() if ln.strip()][-1]
    except IndexError:
        last = ""
    if last != line or not _validate_line(last):
        with LOG_PATH.open("r+", encoding="utf-8") as f:
            f.truncate(before)
        raise IOError("追加后回读校验失败,已回滚截断,learnings.jsonl 未受损")
    return entry


def check_entries():
    """全文件体检:统计合法/坏行行数,报告坏行行号(只读,不修改)。"""
    if not LOG_PATH.exists():
        print("[log_learning] 暂无 learnings.jsonl 记录。")
        return 0
    lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
    nonempty = [ln for ln in lines if ln.strip()]
    bad = [(i, ln) for i, ln in enumerate(lines, 1)
           if ln.strip() and not _validate_line(ln)]
    if bad:
        print(f"[log_learning] 发现 {len(bad)} 条坏行(共 {len(nonempty)} 条):")
        for i, ln in bad:
            print(f"  line {i}: {ln[:100]!r}")
    else:
        print(f"[log_learning] 体检通过:共 {len(nonempty)} 条,全部为合法单行 JSON。")
    return len(bad)


def list_entries(n):
    if not LOG_PATH.exists():
        print("[log_learning] 暂无 learnings.jsonl 记录。")
        return
    lines = [ln for ln in LOG_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    total = len(lines)
    recent = lines[-n:]
    print(f"[log_learning] 共 {total} 条,显示最近 {len(recent)} 条:\n")
    for i, ln in enumerate(recent, 1):
        try:
            e = json.loads(ln)
        except json.JSONDecodeError:
            print(f"  {i}. (无法解析) {ln[:80]}")
            continue
        ts = e.get("ts", "?")
        typ = e.get("type", "?")
        st = e.get("status", "?")
        trig = e.get("trigger", "")
        iss = e.get("issue", "")
        res = e.get("resolution", "")
        fc = ", ".join(e.get("files_changed", [])) or "—"
        print(f"  {i}. [{ts}] {typ}/{st}")
        print(f"       触发: {trig}")
        print(f"       问题: {iss}")
        print(f"       处置: {res}")
        print(f"       文件: {fc}")
        print()


def main():
    p = argparse.ArgumentParser(description="prism-style-plot 学习日志工具")
    p.add_argument("--type", choices=sorted(VALID_TYPES), help="问题类型")
    p.add_argument("--trigger", default="", help="触发信号(报错/用户原话/补丁描述)")
    p.add_argument("--issue", default="", help="问题具体描述")
    p.add_argument("--resolution", default="", help="做了什么")
    p.add_argument("--files", default="", help="受影响文件,逗号分隔(相对技能根)")
    p.add_argument("--status", choices=sorted(VALID_STATUS), default="applied")
    p.add_argument("--verified", default="", help="回归验证手段")
    p.add_argument("--safe-auto", action="store_true",
                   help="是否走了'安全修复自动改'通道")
    p.add_argument("--task", default="", help="触发本轮复盘的任务简述")
    p.add_argument("--list", type=int, metavar="N",
                   help="列出最近 N 条(人类可读),不记录")
    p.add_argument("--check", action="store_true",
                   help="全文件体检:报告坏行(只读),不记录")
    args = p.parse_args()

    if args.check:
        sys.exit(1 if check_entries() else 0)

    if args.list is not None:
        list_entries(args.list)
        return

    # 记录模式:type 必填
    if not args.type:
        p.error("记录模式必须提供 --type")

    entry = {
        "ts": now_iso(),
        "task": args.task,
        "type": args.type,
        "trigger": args.trigger,
        "issue": args.issue,
        "resolution": args.resolution,
        "files_changed": parse_files(args.files),
        "status": args.status,
        "verified_by": args.verified,
        "safe_auto": bool(args.safe_auto),
    }
    append_entry(entry)
    print(f"[log_learning] 已记录 1 条 → {LOG_PATH}")
    print(f"  type={entry['type']} status={entry['status']} safe_auto={entry['safe_auto']}")


if __name__ == "__main__":
    main()
