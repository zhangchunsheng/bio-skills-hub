# -*- coding: utf-8 -*-
"""对话驱动的反馈重推入口（剧荒推荐 Skill · 第九章反馈循环的可运行落地）

用法（在对话里拿到用户反馈后，由我/助手运行）：
  # 场景 B：用户说"这几部我看过了"
  python apply_feedback.py --seen "排球少年!!" "灌篮高手" "齐木楠雄的灾难"

  # 场景 A：用户说"这几部我不喜欢"（可带要避开的属性标签）
  python apply_feedback.py --dislike "排球少年!!" "灌篮高手" --tags "运动题材" "喜剧"

输出：重新生成的片单图（share_list_feedback.png 或自定义 --out），
      并在控制台打印保留/剔除的作品清单，方便核对。
"""
import argparse
import sys

sys.path.insert(0, ".")
import build_share as bs


def main():
    ap = argparse.ArgumentParser(description="剧荒推荐 · 反馈重推")
    ap.add_argument("--seen", nargs="*", default=[],
                    help="用户已看过的作品名（场景 B：冷门下钻）")
    ap.add_argument("--dislike", nargs="*", default=[],
                    help="用户不喜欢的作品名（场景 A：剔除+避开属性）")
    ap.add_argument("--tags", nargs="*", default=[],
                    help="不喜欢作品对应的属性标签，如 运动题材 / 喜剧")
    ap.add_argument("--out", default="share_list_feedback.png",
                    help="输出图片路径")
    args = ap.parse_args()

    if args.dislike:
        print(f"[场景 A · 不喜欢] 剔除 {len(args.dislike)} 部，避开标签：{args.tags or '（自动）'}")
        kept = bs.regenerate(
            {"mode": "dislike", "items": args.dislike, "reject_tags": args.tags},
            args.out)
    elif args.seen:
        print(f"[场景 B · 看过了] 排除 {len(args.seen)} 部，触发冷门下钻")
        kept = bs.regenerate(
            {"mode": "seen", "items": args.seen}, args.out)
    else:
        print("未提供反馈（--seen / --dislike）。退出。")
        return

    print(f"剩余推荐 {len(kept)} 部：")
    for w in kept:
        print(f"  [{w['tier']:>6}] {w['name']}")


if __name__ == "__main__":
    main()
