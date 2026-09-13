"""
季度调仓追踪（v2.0.0 新增）。

跨期对比重仓股：
- track_changes(id): 当前持仓 vs 上一期快照
- compute_turnover_rate(id): 换手率 = (新增+退出)/2
- list_added_removed(id): 列出新增/退出个股
- snapshot(id): 把当前 top_holdings 追加到 data/track_records/{id}.jsonl

零 LLM 依赖。
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import _common
from _common import load_manager, log


def _track_dir() -> str:
    return os.path.join(_common.DATA_DIR, "track_records")


def _path(manager_id: str) -> str:
    return os.path.join(_track_dir(), f"{manager_id}.jsonl")


def snapshot(manager_id: str) -> None:
    """把当前 top_holdings 快照到 JSONL（在 update_one 抓取后调用）。"""
    mgr = load_manager(manager_id)
    if not mgr:
        return
    os.makedirs(_track_dir(), exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "report_date": mgr.get("holdings_report_date", ""),
        "holdings": mgr.get("top_holdings", []) or [],
    }
    with open(_path(manager_id), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log.info(f"经理 {manager_id} 持仓快照已记录")


def get_history(manager_id: str, limit: int = 4) -> List[Dict]:
    path = _path(manager_id)
    if not os.path.exists(path):
        return []
    lines = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []
    recent = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            recent.append(json.loads(line))
        except json.JSONDecodeError:
            continue
        if len(recent) >= limit:
            break
    return list(reversed(recent))


def _holdings_dict(holdings: List[Dict]) -> Dict[str, float]:
    """{code: total_ratio}。"""
    return {h.get("code", ""): h.get("total_ratio", 0) for h in holdings if h.get("code")}


def track_changes(manager_id: str) -> Dict:
    """对比当前持仓 vs 上一期快照，返回变化。

    用法：先 snapshot() 备份旧持仓，再更新 manager.json 的 top_holdings，
    然后调 track_changes() 看新增/退出。
    """
    mgr = load_manager(manager_id)
    if not mgr:
        return {"error": f"经理档案 {manager_id} 不存在"}
    current_holdings = mgr.get("top_holdings", []) or []
    history = get_history(manager_id, limit=1)
    if not history:
        return {
            "manager_id": manager_id,
            "added": [],
            "removed": [],
            "ratio_changes": [],
            "note": "无上一期快照，请先 snapshot() 后再调用",
        }
    current_dict = _holdings_dict(current_holdings)
    previous_dict = _holdings_dict(history[-1]["holdings"])

    added = [c for c in current_dict if c not in previous_dict]
    removed = [c for c in previous_dict if c not in current_dict]
    ratio_changes = []
    for c in set(current_dict) & set(previous_dict):
        delta = current_dict[c] - previous_dict[c]
        if abs(delta) >= 0.5:  # 变动 ≥0.5% 才记录
            ratio_changes.append({"code": c, "delta": round(delta, 2)})

    return {
        "manager_id": manager_id,
        "added": added,
        "removed": removed,
        "ratio_changes": sorted(ratio_changes, key=lambda x: abs(x["delta"]), reverse=True)[:10],
    }


def compute_turnover_rate(manager_id: str) -> Optional[float]:
    """换手率 = (新增权重 + 退出权重) / 2。返回百分比。"""
    mgr = load_manager(manager_id)
    if not mgr:
        return None
    current_holdings = mgr.get("top_holdings", []) or []
    history = get_history(manager_id, limit=1)
    if not history:
        return None
    current_dict = _holdings_dict(current_holdings)
    previous_dict = _holdings_dict(history[-1]["holdings"])
    # 新增权重
    added_weight = sum(current_dict[c] for c in current_dict if c not in previous_dict)
    # 退出权重
    removed_weight = sum(previous_dict[c] for c in previous_dict if c not in current_dict)
    turnover = (added_weight + removed_weight) / 2.0
    return round(turnover, 2)


def list_added_removed(manager_id: str) -> Dict:
    """列出本季新增/退出个股（带名字）。"""
    changes = track_changes(manager_id)
    if "error" in changes:
        return changes
    mgr = load_manager(manager_id)
    code_to_name = {h.get("code", ""): h.get("name", "") for h in (mgr.get("top_holdings", []) or [])}
    # 上期 name 也要查
    history = get_history(manager_id, limit=1)
    if history:
        for h in history[-1]["holdings"]:
            c = h.get("code", "")
            if c and c not in code_to_name:
                code_to_name[c] = h.get("name", "")

    return {
        "added": [{"code": c, "name": code_to_name.get(c, "")} for c in changes.get("added", [])],
        "removed": [{"code": c, "name": code_to_name.get(c, "")} for c in changes.get("removed", [])],
    }


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="季度调仓追踪")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_snap = sub.add_parser("snapshot", help="快照当前持仓")
    p_snap.add_argument("manager_id")

    p_changes = sub.add_parser("changes", help="对比当前 vs 上一期")
    p_changes.add_argument("manager_id")

    p_turnover = sub.add_parser("turnover", help="算换手率")
    p_turnover.add_argument("manager_id")

    args = parser.parse_args()

    if args.cmd == "snapshot":
        snapshot(args.manager_id)
        print(f"✅ 快照已记录到 track_records/{args.manager_id}.jsonl")
    elif args.cmd == "changes":
        changes = track_changes(args.manager_id)
        if "error" in changes:
            print(changes["error"])
            sys.exit(1)
        if changes.get("note"):
            print(f"ℹ️  {changes['note']}")
        else:
            added_removed = list_added_removed(args.manager_id)
            print(f"📊 {args.manager_id} 调仓变化：")
            print(f"  新增 {len(added_removed['added'])} 只：{', '.join(a['name'] for a in added_removed['added'][:5])}")
            print(f"  退出 {len(added_removed['removed'])} 只：{', '.join(r['name'] for r in added_removed['removed'][:5])}")
            ratio = compute_turnover_rate(args.manager_id)
            if ratio is not None:
                print(f"  换手率：{ratio:.2f}%")
    elif args.cmd == "turnover":
        ratio = compute_turnover_rate(args.manager_id)
        if ratio is None:
            print("无上一期快照，无法计算换手率")
        else:
            print(f"换手率：{ratio:.2f}%")