#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_chapter.py —— 逐章硬标准检查

检查项：
  1. 字数（默认 2200-2800，可调）
  2. 前 50 字含 动作/冲突/悬念 至少一项
  3. 前 20% 内容出现即时冲突
  4. 对话占比（引号内字数 / 总字数，默认 35%-45%）
  5. 结尾钩子存在
  6. 钩子类型轮换（不与上一章同类型）

用法：
  python validate_chapter.py <chapter.md> [--min 2200] [--max 2800]
        [--dialog-min 0.35] [--dialog-max 0.45]
        [--prev-hook TYPE] [--json]

输出：JSON 报告到 stdout；人类可读摘要同时打印。
"""
import argparse
import json
import re
import sys
import os

# ---- 词库 ----
ACTION_WORDS = set("冲跑打抓踢撕砸甩扑躲挡推掐抽踩撞翻跳刺砍劈摔咬吼夺掀踹勒斩擒扑夺扼扼拽拂拂")
CONFLICT_WORDS = set("死杀毁败辱逼叛抛离破抓审曝围羞巴耳泼踩赶滚愁恨敌战斗骂撕驱陷坑骗诈欺夺劫崩塌坍塌覆灭")
SUSPENSE_MARKS = set("？?！")  # 强悬念标点
SUSPENSE_WORDS = ["难道", "究竟", "为什么", "忽然", "竟", "偏偏", "原来", "秘密", "真相", "不料", "诡异", "异常", "却", "但", "可是", "不过", "谁知"]

HOOK_KEYWORDS = {
    "信息揭示": ["原来", "真相", "秘密", "揭晓", "暴露", "身份", "竟是", "实则"],
    "危境预警": ["危险", "逼近", "围攻", "陷阱", "危机", "倒计时", "杀机", "逼退", "逼近"],
    "反差展示": ["竟", "居然", "没想到", "表面", "实则", "不过", "殊不知", "伪装"],
    "倒计时": ["三天后", "倒计时", "期限", "还有", "凌晨", "午夜", "钟声", "倒计时"],
    "人物登场": ["他来了", "门开了", "出现", "走来", "身影", "新来的", "推门", "脚步声"],
    "悬念断点": ["就在这时", "就在此刻", "话音未落", "此刻", "突然"],
}

CJK = re.compile(r"[\u4e00-\u9fff]")


def count_cjk(text: str) -> int:
    return len(CJK.findall(text))


def first_n_chars(text: str, n: int) -> str:
    # 取正文前 n 个字符（含标点），用于"前 50 字/前 200 字"语义
    clean = text.strip()
    return clean[:n]


def detect_open_type(head: str):
    """返回 ('action'|'conflict'|'suspense'|None, 命中词)"""
    for w in SUSPENSE_WORDS:
        if w in head:
            return "suspense", w
    for ch in head:
        if ch in ACTION_WORDS:
            return "action", ch
    for w in ["离婚", "羞辱", "甩", "泼", "踩", "赶", "滚", "骂", "逼", "杀", "死", "撕", "摔", "砸"]:
        if w in head:
            return "conflict", w
    if any(m in head for m in SUSPENSE_MARKS):
        return "suspense", "？"
    return None, ""


def has_early_conflict(text: str, ratio: float = 0.20) -> bool:
    total = len(text)
    window = text[: max(1, int(total * ratio))]
    for w in SUSPENSE_WORDS:
        if w in window:
            return True
    for w in ["离婚", "羞辱", "甩", "泼", "踩", "赶", "滚", "骂", "逼", "杀", "死", "撕", "摔", "砸", "战", "斗", "冲突", "翻脸", "背叛"]:
        if w in window:
            return True
    if any(m in window for m in SUSPENSE_MARKS):
        return True
    return False


def dialog_ratio(text: str):
    """返回 (引号内CJK数, 总CJK数, 占比)"""
    total = count_cjk(text)
    opening = {'"': '"', '\u201c': '\u201d', '\u2018': '\u2019',
               '「': '」', '『': '』'}
    in_quote = False
    cur_close = None
    quoted = 0
    for ch in text:
        if not in_quote and ch in opening:
            in_quote = True
            cur_close = opening[ch]
            continue
        if in_quote and ch == cur_close:
            in_quote = False
            cur_close = None
            continue
        if in_quote and CJK.match(ch):
            quoted += 1
    ratio = (quoted / total) if total else 0.0
    return quoted, total, ratio


def detect_hook(text: str):
    """返回 (钩子类型|None, 命中词)"""
    tail = text.strip()[-120:]
    best_type, best_word = None, ""
    for htype, kws in HOOK_KEYWORDS.items():
        for w in kws:
            if w in tail:
                return htype, w  # 命中即返回优先级最高类型
    # 兜底：句末有问号也算悬念断点
    if tail.strip().endswith(("？", "?", "！")):
        return "悬念断点", "？"
    return None, ""


def rotation_ok(cur_type, prev_type):
    if prev_type is None:
        return True, "首章无前置钩子"
    return cur_type != prev_type, f"上章钩子={prev_type}"


def validate(path, min_len=2200, max_len=2800, dmin=0.35, dmax=0.45, prev_hook=None):
    if not os.path.exists(path):
        return {"error": f"文件不存在: {path}"}
    with open(path, encoding="utf-8") as f:
        text = f.read()

    total = count_cjk(text)
    head50 = first_n_chars(text, 50)
    open_type, open_hit = detect_open_type(head50)
    early_conflict = has_early_conflict(text)
    q, tot, ratio = dialog_ratio(text)
    hook_type, hook_hit = detect_hook(text)
    rot_ok, rot_msg = rotation_ok(hook_type, prev_hook)

    results = {
        "file": path,
        "word_count": total,
        "word_count_pass": min_len <= total <= max_len,
        "open50_type": open_type or "none",
        "open50_pass": open_type is not None,
        "early_conflict_pass": early_conflict,
        "dialog_chars": q,
        "dialog_ratio": round(ratio, 3),
        "dialog_pass": dmin <= ratio <= dmax,
        "hook_type": hook_type or "none",
        "hook_pass": hook_type is not None,
        "hook_rotation_pass": rot_ok,
        "hook_rotation_msg": rot_msg,
    }
    all_pass = all([
        results["word_count_pass"], results["open50_pass"],
        results["early_conflict_pass"], results["dialog_pass"],
        results["hook_pass"], results["hook_rotation_pass"],
    ])
    results["all_pass"] = all_pass
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chapter")
    ap.add_argument("--min", type=int, default=2200)
    ap.add_argument("--max", type=int, default=2800)
    ap.add_argument("--dialog-min", type=float, default=0.35)
    ap.add_argument("--dialog-max", type=float, default=0.45)
    ap.add_argument("--prev-hook", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    r = validate(args.chapter, args.min, args.max, args.dialog_min, args.dialog_max, args.prev_hook)
    if "error" in r:
        print(json.dumps(r, ensure_ascii=False))
        sys.exit(1)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"文件: {r['file']}")
        print(f"字数: {r['word_count']}  {'✅' if r['word_count_pass'] else '❌'}({args.min}-{args.max})")
        print(f"前50字: {r['open50_type']}  {'✅' if r['open50_pass'] else '❌'}")
        print(f"前20%冲突: {'✅' if r['early_conflict_pass'] else '❌'}")
        print(f"对话占比: {r['dialog_ratio']}  {'✅' if r['dialog_pass'] else '❌'}({args.dialog_min}-{args.dialog_max})")
        print(f"结尾钩子: {r['hook_type']}  {'✅' if r['hook_pass'] else '❌'}")
        print(f"钩子轮换: {'✅' if r['hook_rotation_pass'] else '❌'} ({r['hook_rotation_msg']})")
        print(f"综合: {'全部通过 ✅' if r['all_pass'] else '存在不通过项 ❌'}")


if __name__ == "__main__":
    main()
