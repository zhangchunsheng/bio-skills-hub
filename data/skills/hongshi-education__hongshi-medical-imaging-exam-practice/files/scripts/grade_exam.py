#!/usr/bin/env python3
"""医学影像技术专业科目刷题 - 判分脚本。

用法：
    python3 grade_exam.py --answers C,A,ACE,B --keys C,A,ACE,B --multi 3

说明：
    - answers / keys：逗号分隔的答案序列（多选答案用连续字母表示，如 ACE；判断题用 A/B）
    - multi：第几题（1-based）是多选题，可传多个，如 --multi 3 或 --multi 3,5
    - 单选/判断：答对得满分，答错得 0 分
    - 多选：错选/多选得 0 分；少选（且所选均正确）每个正确项得 0.3 分；全对得满分
"""
import argparse


def grade_one(user, key, is_multi, single_score=1.0, multi_full=2.0):
    u = set(user.strip().upper())
    k = set(key.strip().upper())
    if is_multi:
        if not u or not u <= k:
            return 0.0, "错选/多选，0 分"
        if u == k:
            return multi_full, "多选全对，满分"
        return round(len(u) * 0.3, 2), f"少选，{len(u)}×0.3={round(len(u)*0.3,2)} 分"
    return (single_score if u == k else 0.0), ("对" if u == k else "错")


def main():
    p = argparse.ArgumentParser(description="医学影像技术刷题判分")
    p.add_argument("--answers", required=True, help="逗号分隔的用户答案")
    p.add_argument("--keys", required=True, help="逗号分隔的标准答案")
    p.add_argument("--multi", default="", help="多选题号（1-based），逗号分隔")
    p.add_argument("--single-score", type=float, default=1.0, help="单选分值")
    p.add_argument("--multi-full", type=float, default=2.0, help="多选满分")
    args = p.parse_args()

    ans = [a.strip() for a in args.answers.split(",")]
    keys = [k.strip() for k in args.keys.split(",")]
    multi = {int(x) for x in args.multi.split(",") if x.strip() != ""}

    if len(ans) != len(keys):
        print("错误：答案数量与标准答案数量不一致")
        return

    total = 0.0
    correct = 0
    for i, (a, k) in enumerate(zip(ans, keys), 1):
        score, note = grade_one(a, k, i in multi, args.single_score, args.multi_full)
        total += score
        if note in ("对", "多选全对，满分"):
            correct += 1
        print(f"第{i}题: 你的答案={a.upper()} 标准答案={k.upper()} → {score}分（{note}）")

    print(f"\n答对 {correct}/{len(ans)} 题，总分 {round(total, 2)} 分")


if __name__ == "__main__":
    main()
