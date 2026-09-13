"""
2025-2026 知名基金经理种子库导入器
从 data/famous_managers_2025_2026.json 读取知名经理种子列表，
按需导入到 roster.json（受100人上限约束）。
支持：列出/一键导入/按分类导入/单经理导入/导入并抓取。

种子库覆盖4分类共80位知名经理：
  - 公募明星（30位）：张坤、萧楠、刘彦春、葛兰、蔡嵩松等长青公募
  - 私募百亿（20位）：邓晓峰、冯柳、赵军、但斌等百亿私募
  - QDII海外（15位）：李彦、张金涛、许之彦等QDII/海外
  - 当红经理（15位）：张城阳、韩创、冯明远等2025-2026当红

使用：
  python famous_manager_importer.py list                       # 列出全部种子经理(按分类)
  python famous_manager_importer.py list <分类>                # 列出某分类
  python famous_manager_importer.py import_all                 # 一键导入全部(受100人上限)
  python famous_manager_importer.py import_category <分类>     # 按分类导入
  python famous_manager_importer.py import_one <姓名>          # 导入单位经理
  python famous_manager_importer.py import_and_fetch <姓名>    # 导入并立即抓取+蒸馏
"""

import os
import sys

# 确保能 import 同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _common
from _common import read_json, write_json, log, DATA_DIR
import roster_manager
import manager_search

# 种子库路径
FAMOUS_MANAGERS_PATH = os.path.join(DATA_DIR, "famous_managers_2025_2026.json")

# 分类标签
CATEGORY_EMOJI = {
    "公募明星": "🏆",
    "私募百亿": "📈",
    "QDII海外": "🌍",
    "当红经理": "🔥",
}
MANAGER_TYPE_EMOJI = {"公募": "🏆", "私募": "📈", "QDII": "🌍"}


def load_famous_managers():
    """加载种子库"""
    data = read_json(FAMOUS_MANAGERS_PATH, default=None)
    if not data:
        log.error(f"种子库文件不存在或为空：{FAMOUS_MANAGERS_PATH}")
        return {"meta": {"total": 0}, "managers": []}
    return data


def _resolve_manager_id(seed):
    """
    解析种子条目的经理ID。
    若 id 已填，直接返回。
    若 id 为空，通过 manager_search 按姓名+公司搜索补全。
    返回: (manager_id, fund_count, tenure_return, scale, fund_codes, matched_company) 或 None
    """
    manager_id = seed.get("id", "").strip()
    if manager_id:
        # 已知ID，直接返回（用种子库的元信息，不再次抓取）
        return {
            "id": manager_id,
            "fund_count": 0,
            "tenure_return": "",
            "scale": "",
            "fund_codes": [],
            "matched_company": seed.get("company", ""),
        }

    name = seed.get("name", "").strip()
    company = seed.get("company", "").strip()
    manager_type = seed.get("manager_type", "公募")

    # 私募经理：通过 AMAC 搜索管理人
    if manager_type == "私募":
        try:
            # AMAC 搜索用的是管理人名称（公司名），私募基金经理个人名通常搜不到
            keyword = company if company else name
            candidates = manager_search.search_private_managers(keyword)
            if candidates:
                # 取匹配度最高的
                best = candidates[0]
                return {
                    "id": best["id"],
                    "fund_count": best.get("fund_count", 0),
                    "tenure_return": "",
                    "scale": "",
                    "fund_codes": [],
                    "matched_company": best.get("company", company),
                }
        except Exception as e:
            log.warning(f"私募经理 {name}（{company}）AMAC搜索失败：{e}")
        return None

    # 公募/QDII 经理：通过东方财富搜索
    try:
        candidates = manager_search.search_managers(
            name, search_type="name", company_filter=company if company else None
        )
        if not candidates:
            # 退化为不带公司过滤
            candidates = manager_search.search_managers(name, search_type="name")
        if not candidates:
            log.warning(f"未找到公募经理「{name}」（{company}）")
            return None

        # 优先取公司匹配的最高分候选
        best = candidates[0]
        if company:
            for c in candidates:
                if company in c.get("company", "") or c.get("company", "") in company:
                    best = c
                    break
        return {
            "id": best["id"],
            "fund_count": best.get("fund_count", 0),
            "tenure_return": best.get("tenure_return", ""),
            "scale": best.get("scale", ""),
            "fund_codes": best.get("fund_codes", []),
            "matched_company": best.get("company", company),
        }
    except Exception as e:
        log.warning(f"公募经理 {name}（{company}）搜索失败：{e}")
        return None


def import_one(seed, fetch=False, distill_engine="auto"):
    """
    导入单个种子经理到 roster。
    参数:
        seed: 种子条目 dict
        fetch: 导入后是否立即抓取+蒸馏
        distill_engine: 蒸馏引擎 auto/llm/rules
    返回: {"success": bool, "message": str, "skipped": bool}
    """
    name = seed.get("name", "")
    company = seed.get("company", "")
    manager_type = seed.get("manager_type", "公募")
    category = seed.get("category", "")
    emoji = CATEGORY_EMOJI.get(category, "")

    # 1. 解析ID
    resolved = _resolve_manager_id(seed)
    if not resolved:
        return {
            "success": False,
            "message": f"{emoji} {name}（{company}）- ❌ 无法解析经理ID（搜索无匹配）",
            "skipped": True,
        }

    manager_id = resolved["id"]

    # 2. 检查是否已在名单
    if roster_manager.is_in_roster(manager_id):
        return {
            "success": False,
            "message": f"{emoji} {name}（{company}）- ⏭️ 已在名单中，跳过",
            "skipped": True,
        }

    # 3. 检查名单是否已满
    if roster_manager.is_full():
        return {
            "success": False,
            "message": f"{emoji} {name}（{company}）- ❌ 名单已满（最多{roster_manager.MAX_MANAGERS}人）",
            "skipped": True,
        }

    # 4. 添加到名单
    result = roster_manager.add_manager(
        manager_id,
        name,
        company=resolved["matched_company"] or company,
        fund_count=resolved["fund_count"],
        tenure_return=resolved["tenure_return"],
        scale=resolved["scale"],
        manager_type=manager_type,
    )

    if not result.get("success"):
        return {
            "success": False,
            "message": f"{emoji} {name}（{company}）- ❌ {result.get('message', '添加失败')}",
            "skipped": True,
        }

    # 5. 抓取+蒸馏（可选）
    fetch_msg = ""
    if fetch:
        try:
            import monthly_updater
            monthly_updater.update_single_manager(manager_id, distill_engine=distill_engine)
            fetch_msg = "（已抓取+蒸馏）"
        except Exception as e:
            fetch_msg = f"（抓取失败：{e}）"

    return {
        "success": True,
        "message": f"{emoji} {name}（{company}）- ✅ 已导入{fetch_msg}",
        "skipped": False,
        "manager_id": manager_id,
    }


def import_batch(seeds, fetch=False, distill_engine="auto"):
    """
    批量导入种子经理。
    返回汇总 dict。
    """
    results = {"total": len(seeds), "success": 0, "skipped": 0, "failed": 0, "details": []}
    for i, seed in enumerate(seeds, 1):
        log.info(f"[{i}/{len(seeds)}] 导入：{seed.get('name','')}（{seed.get('company','')}）")
        r = import_one(seed, fetch=fetch, distill_engine=distill_engine)
        results["details"].append(r["message"])
        if r["skipped"]:
            results["skipped"] += 1
        elif r["success"]:
            results["success"] += 1
        else:
            results["failed"] += 1
    return results


def format_list(seeds, category_filter=None):
    """格式化种子经理列表"""
    if category_filter:
        seeds = [s for s in seeds if s.get("category") == category_filter]
        if not seeds:
            return f"分类「{category_filter}」下无种子经理。可用分类：{', '.join(CATEGORY_EMOJI.keys())}"

    lines = [
        f"📋 2025-2026 知名基金经理种子库（共 {len(seeds)} 位）",
        f"   数据来源：东方财富（公募/QDII）+ AMAC（私募）",
        f"   导入命令：python scripts/famous_manager_importer.py import_all\n",
    ]

    # 按分类分组
    by_cat = {}
    for s in seeds:
        cat = s.get("category", "其他")
        by_cat.setdefault(cat, []).append(s)

    for cat in ["公募明星", "私募百亿", "QDII海外", "当红经理"]:
        if cat not in by_cat:
            continue
        emoji = CATEGORY_EMOJI.get(cat, "")
        lines.append(f"\n{emoji} {cat}（{len(by_cat[cat])}位）")
        lines.append("-" * 80)
        for i, s in enumerate(by_cat[cat], 1):
            name = s.get("name", "")
            company = s.get("company", "")
            mtype = s.get("manager_type", "")
            tags = "/".join(s.get("tags", []))
            note = s.get("note", "")[:40]
            id_status = "✓" if s.get("id") else "？"
            lines.append(f"  [{i:>2}] {name:<6} | {company:<14} | {mtype:<4} | {tags:<14} | ID{id_status} | {note}")

    lines.append("\n" + "=" * 80)
    lines.append("图例：ID✓=已预填ID可直接导入  ID？=需搜索补全ID")
    lines.append("导入选项：")
    lines.append("  import_all                 # 一键导入全部（受100人上限）")
    lines.append("  import_category <分类>     # 按分类导入")
    lines.append("  import_one <姓名>          # 导入单位经理")
    lines.append("  import_and_fetch <姓名>    # 导入并立即抓取+蒸馏")
    return "\n".join(lines)


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python famous_manager_importer.py list                       # 列出全部种子经理")
        print("  python famous_manager_importer.py list <分类>                # 列出某分类")
        print("  python famous_manager_importer.py import_all                 # 一键导入全部")
        print("  python famous_manager_importer.py import_category <分类>     # 按分类导入")
        print("  python famous_manager_importer.py import_one <姓名>          # 导入单位经理")
        print("  python famous_manager_importer.py import_and_fetch <姓名>    # 导入并立即抓取+蒸馏")
        print(f"\n可用分类：{', '.join(CATEGORY_EMOJI.keys())}")
        sys.exit(1)

    cmd = sys.argv[1]
    famous = load_famous_managers()
    seeds = famous.get("managers", [])

    if cmd == "list":
        cat = sys.argv[2] if len(sys.argv) > 2 else None
        print(format_list(seeds, category_filter=cat))

    elif cmd == "import_all":
        print(f"开始一键导入全部 {len(seeds)} 位种子经理（上限 {roster_manager.MAX_MANAGERS} 人）...\n")
        results = import_batch(seeds, fetch=False)
        print("\n" + "=" * 80)
        print(f"导入完成：成功 {results['success']}，跳过 {results['skipped']}，失败 {results['failed']}")
        print("\n明细：")
        for d in results["details"]:
            print(f"  {d}")
        # 同步 SKILL.md 版本
        try:
            import monthly_updater
            monthly_updater.bump_skill_version()
        except Exception:
            pass

    elif cmd == "import_category":
        if len(sys.argv) < 3:
            print(f"用法: python famous_manager_importer.py import_category <分类>")
            print(f"可用分类：{', '.join(CATEGORY_EMOJI.keys())}")
            sys.exit(1)
        cat = sys.argv[2]
        cat_seeds = [s for s in seeds if s.get("category") == cat]
        if not cat_seeds:
            print(f"分类「{cat}」下无种子经理。可用分类：{', '.join(CATEGORY_EMOJI.keys())}")
            sys.exit(1)
        print(f"开始导入分类「{cat}」下 {len(cat_seeds)} 位种子经理...\n")
        results = import_batch(cat_seeds, fetch=False)
        print("\n" + "=" * 80)
        print(f"导入完成：成功 {results['success']}，跳过 {results['skipped']}，失败 {results['failed']}")
        for d in results["details"]:
            print(f"  {d}")

    elif cmd == "import_one":
        if len(sys.argv) < 3:
            print("用法: python famous_manager_importer.py import_one <姓名>")
            sys.exit(1)
        name = sys.argv[2]
        seed = next((s for s in seeds if s.get("name") == name), None)
        if not seed:
            print(f"种子库中未找到姓名为「{name}」的经理。执行 list 查看全部种子经理。")
            sys.exit(1)
        r = import_one(seed, fetch=False)
        print(r["message"])

    elif cmd == "import_and_fetch":
        if len(sys.argv) < 3:
            print("用法: python famous_manager_importer.py import_and_fetch <姓名>")
            sys.exit(1)
        name = sys.argv[2]
        seed = next((s for s in seeds if s.get("name") == name), None)
        if not seed:
            print(f"种子库中未找到姓名为「{name}」的经理。执行 list 查看全部种子经理。")
            sys.exit(1)
        print(f"开始导入并抓取「{name}」的完整数据（重仓/策略/业绩/蒸馏）...")
        r = import_one(seed, fetch=True)
        print(r["message"])

    else:
        print(f"未知命令: {cmd}")
        print(f"可用命令: list, list <分类>, import_all, import_category <分类>, import_one <姓名>, import_and_fetch <姓名>")
        sys.exit(1)
