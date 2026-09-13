# -*- coding: utf-8 -*-
# find_similar.py —— 扫描历史同类公告
# 读取用户提供的全量文件名索引 CSV，按关键词筛历史公告目录下的同类公告，按日期降序返回路径。
# 用途：announcement-drafter 技能第 2 步"扫描历史同类"，优先取最近一份做结构参考。
#
# 用法：
#   python find_similar.py "担保" --limit 10
#   python find_similar.py "减持" --year 2025
#   python find_similar.py "权益分派" --csv "其他索引.csv"
import argparse
import csv
import os


def main():
    ap = argparse.ArgumentParser(description="扫描公告目录历史同类公告")
    ap.add_argument("keyword", help="公告类型关键词，如 担保 / 减持 / 权益分派 / 换届")
    ap.add_argument("--csv", required=True, help="文件名索引 CSV 路径（必传，含 相对路径/文件名/扩展名/修改日期 列）")
    ap.add_argument("--limit", type=int, default=15, help="返回条数上限")
    ap.add_argument("--year", default=None, help="限定年份，如 2025")
    ap.add_argument("--all", action="store_true", help="包含非文档类（默认只返回 .doc/.docx 公告）")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        print(f"[错误] 索引文件不存在: {args.csv}")
        return 1

    kw = args.keyword.lower()
    hits = []
    with open(args.csv, encoding="utf-8-sig", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            path = row.get("相对路径", "") or ""
            name = row.get("文件名", "") or ""
            if "02-公告" not in path:
                continue
            if args.year and args.year not in (row.get("修改日期", "") or ""):
                continue
            if name.lower().find(kw) >= 0:
                ext = (row.get("扩展名", "") or "").lower()
                if not args.all and ext not in ("doc", "docx"):
                    continue
                hits.append((row.get("修改日期", ""), path, name))

    hits.sort(key=lambda x: x[0], reverse=True)
    shown = hits[: args.limit]
    if not shown:
        print(f"[无命中] 关键词='{args.keyword}' 在 02-公告 下未找到匹配。可换关键词或放宽 --year。")
        return 0
    print(f"# 命中 {len(hits)} 条，显示前 {len(shown)} 条（按修改日期降序）")
    for d, p, n in shown:
        print(f"{d}\t{p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
