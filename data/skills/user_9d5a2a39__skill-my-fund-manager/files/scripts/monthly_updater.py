"""
基金经理数据定期更新与自我迭代模块
遍历名单中所有经理，重新抓取数据并蒸馏。
更新 SKILL.md 版本号和数据统计区块。
适配任意 agent 环境（不依赖特定调度工具）。
"""

import os
import re
import sys
from datetime import datetime

# 确保能 import 同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _common
from _common import log, read_json, write_json, ROSTER_PATH, SKILL_ROOT, load_manager, save_manager
import roster_manager
from roster_manager import MAX_MANAGERS
import fetch_holdings
import fetch_reports
import fetch_performance
import distill_manager
import manager_search

SKILL_MD_PATH = os.path.join(SKILL_ROOT, "SKILL.md")
CHANGE_LOG_DIR = os.path.join(SKILL_ROOT, "data", "change_log")


def _post_update_hooks(manager_id):
    """
    v2.0.0 新增：每次 update_one 后自动执行：
    1. 持仓快照到 track_records/{id}.jsonl（便于下次对比换手率）
    2. 观点记录到 viewpoints_history/{id}.jsonl
    3. style_radar 计算+记录到 style_history/{id}.jsonl
    4. 能力评分 / 业绩归因 / 风险指标 计算并写回 manager.json
    每个 hook 失败都不影响其他 hook。
    """
    mgr = load_manager(manager_id)
    if not mgr:
        return

    # 1. 持仓快照
    try:
        import turnover_tracker as tt
        tt.snapshot(manager_id)
    except Exception as e:
        log.warning(f"持仓快照失败：{e}")

    # 2. 观点时序
    try:
        import viewpoint_tracker as vt
        report_date = mgr.get("holdings_report_date") or datetime.now().strftime("%Y-%m-%d")
        viewpoint = mgr.get("viewpoint_human", "")
        if viewpoint and viewpoint != "暂无足够数据生成投资观点。":
            vt.record_viewpoint(manager_id, report_date, viewpoint, "季报")
    except Exception as e:
        log.warning(f"观点记录失败：{e}")

    # 3. 风格雷达 + 时序
    try:
        import style_radar as sr
        import style_drift as sd
        radar = sr.compute_radar(mgr)
        sd.record_style(manager_id, radar)
    except Exception as e:
        log.warning(f"风格雷达记录失败：{e}")

    # 4. 能力评分 / 业绩归因 / 风险指标 / 言论指纹（写回 manager.json）
    try:
        import capability_score as cap
        scores = cap.compute_scores(mgr)
        mgr["capability_scores"] = scores
    except Exception as e:
        log.warning(f"能力评分失败：{e}")

    try:
        import performance_attribution as pa
        attr = pa.attribute_performance(mgr)
        mgr["attribution"] = attr
    except Exception as e:
        log.warning(f"业绩归因失败：{e}")

    try:
        import risk_metrics as rm
        risk = rm.compute_risk_metrics(mgr)
        mgr["risk_metrics"] = risk
    except Exception as e:
        log.warning(f"风险指标失败：{e}")

    try:
        import speech_fingerprint as sf
        fp = sf.build_fingerprint(manager_id)
        if not fp.get("error"):
            mgr["speech_fingerprint"] = fp
    except Exception as e:
        log.warning(f"言论指纹失败：{e}")

    # 一次性写回所有新字段
    save_manager(manager_id, mgr)


def update_single_manager(manager_id, distill_engine="auto"):
    """
    更新单个经理的完整数据：重仓 -> 投资策略 -> 业绩 -> 蒸馏。
    返回更新摘要。
    """
    entry = None
    roster = roster_manager.get_roster()
    for m in roster["managers"]:
        if m["id"] == str(manager_id):
            entry = m
            break

    if not entry:
        return {"error": f"经理 {manager_id} 不在名单中"}

    name = entry.get("name", "")
    log.info(f"--- 更新经理：{name}（{entry.get('company','')}）---")

    # 判断经理类型（私募经理ID以amac_开头）
    is_private = str(manager_id).startswith("amac_")

    # 确保经理档案存在
    mgr = load_manager(manager_id) or {"id": manager_id, "name": name, "company": entry.get("company", "")}
    if is_private:
        mgr["manager_type"] = "私募"

    if is_private:
        # 私募经理：通过AMAC获取基金产品列表，不抓取东方财富数据（私募不公开持仓/季报/净值）
        log.info("私募基金管理人，通过AMAC获取产品列表（私募不公开持仓/季报/净值）")
        try:
            funds = manager_search.search_amac_funds(name if len(name) <= 20 else name[:20], page_size=20)
            mgr["fund_names"] = list(set(f.get("fund_name", "") for f in funds if f.get("fund_name")))[:10]
            mgr["fund_count"] = len(funds)
            mgr["manager_type"] = "私募"
            save_manager(manager_id, mgr)
            log.info(f"  AMAC获取到 {len(funds)} 只私募基金产品")
        except Exception as e:
            log.warning(f"AMAC产品列表获取失败：{e}")
            save_manager(manager_id, mgr)
    else:
        # 公募经理：正常通过东方财富抓取数据
        # 0. 刷新经理基本信息（获取最新基金代码）
        try:
            candidates = manager_search.search_managers(name, search_type="name")
            for c in candidates:
                if c["id"] == str(manager_id):
                    mgr["fund_codes"] = c.get("fund_codes", [])
                    mgr["fund_names"] = c.get("fund_names", [])
                    mgr["tenure_return"] = c.get("tenure_return", "")
                    mgr["scale"] = c.get("scale", "")
                    mgr["manager_type"] = "公募"
                    # 同步更新名单条目中的元数据
                    roster_manager.refresh_entry_meta(
                        manager_id,
                        fund_count=len(c.get("fund_codes", [])),
                        tenure_return=c.get("tenure_return", ""),
                        scale=c.get("scale", ""),
                        manager_type="公募",
                    )
                    break
        except Exception as e:
            log.warning(f"刷新经理基本信息失败：{e}")

        save_manager(manager_id, mgr)

        # 1. 抓取重仓
        try:
            log.info(f"[1/4] 抓取十大重仓...")
            fetch_holdings.update_manager_holdings(manager_id)
        except Exception as e:
            log.warning(f"重仓抓取失败：{e}")

        # 2. 抓取投资策略
        try:
            log.info(f"[2/4] 抓取投资策略和季报...")
            fetch_reports.update_manager_reports(manager_id)
        except Exception as e:
            log.warning(f"投资策略抓取失败：{e}")

        # 3. 抓取业绩数据
        try:
            log.info(f"[3/4] 抓取业绩数据...")
            fetch_performance.update_manager_performance(manager_id)
        except Exception as e:
            log.warning(f"业绩抓取失败：{e}")

    # 4. 蒸馏
    distill_success = False
    try:
        log.info(f"[4/4] 蒸馏投资风格（引擎: {distill_engine}）...")
        result = distill_manager.distill_manager(manager_id, engine=distill_engine)
        if result.get("task_type"):
            log.info("已生成蒸馏任务，待对话 LLM 执行（engine=llm）")
        elif result.get("success"):
            log.info(result["message"])
            distill_success = True
        elif result.get("error"):
            log.warning(result["error"])
    except Exception as e:
        log.warning(f"蒸馏失败：{e}")

    # 5. v2.0.0 新增：自动快照+能力评分+风格雷达（即使蒸馏失败也尝试）
    _post_update_hooks(manager_id)

    # 更新名单刷新时间（apply_distill_result成功时已更新状态，避免重复保存）
    if not distill_success:
        roster_manager.update_last_refresh(manager_id)
        roster_manager.update_status(manager_id, "active")

    return {"success": True, "manager_id": manager_id, "name": name}


def update_all(distill_engine="auto", stale_only=False, days_threshold=30):
    """
    更新名单中所有经理的数据。
    参数:
        distill_engine: auto/llm/rules
        stale_only: 只更新过期数据
        days_threshold: 过期阈值（天）
    """
    roster = roster_manager.get_roster()
    managers = roster["managers"]

    if not managers:
        log.warning("名单为空，无需更新")
        return {"message": "名单为空，请先添加基金经理"}

    # 筛选需要更新的经理
    if stale_only:
        targets = roster_manager.get_stale_managers(days_threshold)
        log.info(f"名单共{len(managers)}人，其中{len(targets)}人数据过期（>{days_threshold}天）")
    else:
        targets = managers
        log.info(f"开始更新全部{len(managers)}名经理...")

    results = {"total": len(targets), "success": 0, "failed": 0, "details": []}

    for i, m in enumerate(targets):
        log.info(f"\n[{i+1}/{len(targets)}] 处理经理：{m['name']}")
        try:
            result = update_single_manager(m["id"], distill_engine)
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
            results["details"].append({"name": m["name"], "result": result})
        except Exception as e:
            log.error(f"经理 {m['name']} 更新失败：{e}")
            results["failed"] += 1
            results["details"].append({"name": m["name"], "error": str(e)})

    # 自我迭代：bump SKILL.md 版本和统计
    bump_skill_version(results)

    log.info(f"\n更新完成：成功{results['success']}，失败{results['failed']}")
    return results


# ============================================================
# 智能增量更新（变化检测）
# ============================================================
def _parse_scale(scale_str):
    """把规模字符串解析为 float（统一单位：亿元）。失败返回 None。"""
    if not scale_str:
        return None
    text = str(scale_str).strip().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(万亿|亿元|亿|万元|万)?", text)
    if not m:
        return None
    try:
        value = float(m.group(1))
    except ValueError:
        return None
    unit = m.group(2) or "亿"
    if unit == "万亿":
        return value * 10000
    if unit == "万元":
        return value / 10000
    if unit == "万":
        return value / 10000
    return value


def _detect_changes(fresh_data, archived_data):
    """
    对比新抓取数据 vs 已存档数据，判断是否有变化（四维度）。
    返回: {"changed": bool, "reasons": [str, ...], "details": dict}
    """
    reasons = []
    details = {}

    # 1. 规模变化（±10%）
    new_scale = _parse_scale(fresh_data.get("scale", ""))
    old_scale = _parse_scale(archived_data.get("scale", ""))
    if new_scale and old_scale and old_scale > 0:
        change_pct = abs(new_scale - old_scale) / old_scale * 100
        if change_pct >= 10:
            reasons.append(f"规模变化{change_pct:.1f}%（{old_scale}→{new_scale}亿元）")
            details["scale_change"] = {"old": old_scale, "new": new_scale, "pct": round(change_pct, 2)}

    # 2. 重仓变化（新增/退出≥1 或 占比变动≥3%）
    new_holdings = fresh_data.get("top_holdings", []) or []
    old_holdings = archived_data.get("top_holdings", []) or []
    if new_holdings and old_holdings:
        new_codes = {h.get("code", "") for h in new_holdings[:10]}
        old_codes = {h.get("code", "") for h in old_holdings[:10]}
        added = new_codes - old_codes
        removed = old_codes - new_codes
        if added or removed:
            reasons.append(f"重仓变动：新增{len(added)}只/退出{len(removed)}只")
            details["holdings_change"] = {"added": list(added), "removed": list(removed)}
        else:
            new_ratio = {h.get("code", ""): h.get("total_ratio", 0) or 0 for h in new_holdings[:10]}
            old_ratio = {h.get("code", ""): h.get("total_ratio", 0) or 0 for h in old_holdings[:10]}
            big_changes = []
            for code in new_codes & old_codes:
                diff = abs(new_ratio.get(code, 0) - old_ratio.get(code, 0))
                if diff >= 3:
                    big_changes.append({"code": code, "old": old_ratio.get(code, 0), "new": new_ratio.get(code, 0), "diff": round(diff, 2)})
            if big_changes:
                reasons.append(f"重仓占比变动≥3%：{len(big_changes)}只")
                details["holdings_ratio_change"] = big_changes

    # 3. 新季报（报告期日期变化）
    new_report_date = fresh_data.get("holdings_report_date", "")
    old_report_date = archived_data.get("holdings_report_date", "")
    if new_report_date and new_report_date != old_report_date:
        reasons.append(f"新季报：{old_report_date or '无'} → {new_report_date}")
        details["report_date_change"] = {"old": old_report_date, "new": new_report_date}

    # 4. 业绩变化（近1年收益率 ±5%）
    new_perf = (fresh_data.get("performance") or {}).get("summary", {}).get("avg_returns", {}) or {}
    old_perf = (archived_data.get("performance") or {}).get("summary", {}).get("avg_returns", {}) or {}
    new_1y = new_perf.get("近1年")
    old_1y = old_perf.get("近1年")
    if new_1y is not None and old_1y is not None:
        try:
            diff = abs(float(new_1y) - float(old_1y))
            if diff >= 5:
                reasons.append(f"近1年业绩变化{diff:.1f}个百分点（{old_1y}%→{new_1y}%）")
                details["perf_change"] = {"old": old_1y, "new": new_1y, "diff": round(diff, 2)}
        except (ValueError, TypeError):
            pass

    return {"changed": len(reasons) > 0, "reasons": reasons, "details": details}


def _write_change_log(change_log):
    """写入变化日志到 data/change_log/YYYY-MM-DD.json（同日追加）"""
    os.makedirs(CHANGE_LOG_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(CHANGE_LOG_DIR, f"{today}.json")

    # 若当天已有日志，合并
    existing = read_json(path, default=None) or {"date": today, "runs": []}
    existing.setdefault("runs", []).append(change_log)
    write_json(path, existing)
    log.info(f"变化日志已写入：{path}")


def smart_update(distill_engine="auto", days_threshold=7):
    """
    智能增量更新：对名单中每位经理，抓取最新数据并与存档对比，
    只对有变化的经理执行完整更新（含蒸馏），无变化的仅刷新时间戳。

    四维度变化检测：
      1. 规模变化 ±10%
      2. 重仓变动（新增/退出≥1 或 占比变动≥3%）
      3. 新季报发布（报告期日期变化）
      4. 业绩变化（近1年收益率 ±5%）

    参数:
        distill_engine: 蒸馏引擎 auto/llm/rules
        days_threshold: 在该天数内已刷新的经理跳过抓取（数据已新鲜）
    返回: 汇总 dict
    """
    roster = roster_manager.get_roster()
    managers = roster["managers"]

    if not managers:
        log.warning("名单为空，无需更新")
        return {
            "message": (
                "名单为空，请先添加基金经理。\n"
                "💡 提示：执行 `python scripts/famous_manager_importer.py import_all` "
                "可一键导入 2025-2026 知名基金经理种子库。"
            )
        }

    log.info(f"智能增量更新开始：名单共 {len(managers)} 人（新鲜阈值 {days_threshold} 天）")

    results = {"total": len(managers), "changed": 0, "skipped": 0, "failed": 0, "details": []}
    change_log = {
        "run_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "engine": distill_engine,
        "managers": [],
    }

    for i, m in enumerate(managers):
        manager_id = m["id"]
        name = m["name"]
        log.info(f"\n[{i+1}/{len(managers)}] 智能检测：{name}（{m.get('company','')}）")

        # 1. 跳过：在 days_threshold 内已刷新
        last_refresh = m.get("last_refresh", "")
        if last_refresh:
            try:
                last_dt = datetime.strptime(last_refresh[:10], "%Y-%m-%d")
                days_since = (datetime.now() - last_dt).days
                if days_since < days_threshold:
                    log.info(f"  ⏭ 数据在 {days_since} 天内已刷新（<{days_threshold}天），跳过")
                    results["skipped"] += 1
                    results["details"].append({"name": name, "action": "skipped_fresh", "reason": f"在{days_since}天内已刷新"})
                    continue
            except ValueError:
                pass

        # 私募经理无东方财富数据，跳过变化检测（保留抓取逻辑在 update_single_manager 中）
        is_private = str(manager_id).startswith("amac_")
        if is_private:
            log.info(f"  私募经理，跳过智能检测，直接执行完整更新")
            try:
                update_single_manager(manager_id, distill_engine)
                results["changed"] += 1
                results["details"].append({"name": name, "action": "updated", "reasons": ["私募经理直接更新"]})
                change_log["managers"].append({"name": name, "manager_id": manager_id, "changed": True, "reasons": ["私募经理直接更新"]})
            except Exception as e:
                log.error(f"  更新失败：{e}")
                results["failed"] += 1
                results["details"].append({"name": name, "action": "failed", "error": str(e)})
            continue

        # 2. 加载已存档数据
        archived = load_manager(manager_id) or {}

        # 3. 轻量抓取最新数据（重仓+业绩+规模，不蒸馏、不抓策略）
        fresh = {"scale": archived.get("scale", "")}
        try:
            log.info(f"  [1/3] 抓取最新重仓...")
            fetch_holdings.update_manager_holdings(manager_id)
            fresh_mgr = load_manager(manager_id) or {}
            fresh["top_holdings"] = fresh_mgr.get("top_holdings", [])
            fresh["holdings_report_date"] = fresh_mgr.get("holdings_report_date", "")
        except Exception as e:
            log.warning(f"  重仓抓取失败：{e}")
            fresh["top_holdings"] = archived.get("top_holdings", [])
            fresh["holdings_report_date"] = archived.get("holdings_report_date", "")

        try:
            log.info(f"  [2/3] 抓取最新业绩...")
            fetch_performance.update_manager_performance(manager_id)
            fresh_mgr = load_manager(manager_id) or {}
            fresh["performance"] = fresh_mgr.get("performance", {})
        except Exception as e:
            log.warning(f"  业绩抓取失败：{e}")
            fresh["performance"] = archived.get("performance", {})

        try:
            log.info(f"  [3/3] 抓取最新规模...")
            candidates = manager_search.search_managers(name, search_type="name")
            for c in candidates:
                if c["id"] == str(manager_id):
                    fresh["scale"] = c.get("scale", "") or fresh["scale"]
                    break
        except Exception as e:
            log.warning(f"  规模刷新失败：{e}")

        # 4. 变化检测
        change_result = _detect_changes(fresh, archived)

        if change_result["changed"]:
            log.info(f"  🔔 检测到变化：{'; '.join(change_result['reasons'])}")
            results["changed"] += 1
            change_log["managers"].append({
                "name": name,
                "manager_id": manager_id,
                "changed": True,
                "reasons": change_result["reasons"],
                "details": change_result["details"],
            })

            # 5. 有变化：补抓投资策略 + 蒸馏
            try:
                log.info(f"  抓取投资策略 + 蒸馏...")
                fetch_reports.update_manager_reports(manager_id)
                distill_result = distill_manager.distill_manager(manager_id, engine=distill_engine)
                if distill_result.get("error") or (
                    not distill_result.get("success") and not distill_result.get("task_type")
                ):
                    error = distill_result.get("error") or "蒸馏未返回成功结果"
                    raise RuntimeError(error)
                results["details"].append({"name": name, "action": "updated", "reasons": change_result["reasons"]})
            except Exception as e:
                log.error(f"  完整更新失败：{e}")
                results["failed"] += 1
                results["details"].append({"name": name, "action": "failed", "error": str(e)})
        else:
            log.info(f"  ✅ 无变化，仅刷新时间戳")
            results["skipped"] += 1
            roster_manager.update_last_refresh(manager_id)
            change_log["managers"].append({
                "name": name,
                "manager_id": manager_id,
                "changed": False,
                "reasons": [],
            })

    # 写入变化日志
    _write_change_log(change_log)

    # 自我迭代
    bump_skill_version(results)

    log.info(f"\n智能更新完成：变化 {results['changed']}，跳过 {results['skipped']}，失败 {results['failed']}")
    return results


def bump_skill_version(update_results=None):
    """
    自我迭代：更新 SKILL.md 的版本号和数据统计区块。
    """
    if not os.path.exists(SKILL_MD_PATH):
        log.warning("SKILL.md 不存在，跳过版本更新")
        return

    with open(SKILL_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    now = datetime.now()
    updated = False

    # 更新 version（小版本号 +1）
    version_m = re.search(r'^version:\s*(\d+)\.(\d+)\.(\d+)', content, re.MULTILINE)
    if version_m:
        major, minor, patch = int(version_m.group(1)), int(version_m.group(2)), int(version_m.group(3))
        new_version = f"{major}.{minor}.{patch + 1}"
        content = re.sub(r'^version:\s*\d+\.\d+\.\d+', f'version: {new_version}', content, count=1, flags=re.MULTILINE)
        updated = True
        log.info(f"SKILL.md 版本更新：{version_m.group(0)} -> version: {new_version}")

    # 更新 updated 日期
    if re.search(r'^updated:\s*\S+', content, re.MULTILINE):
        content = re.sub(r'^updated:\s*\S+', f'updated: {now.strftime("%Y-%m-%d")}', content, count=1, flags=re.MULTILINE)
        updated = True

    # 更新数据统计区块（如果存在）
    roster = roster_manager.get_roster()
    count = roster["meta"]["count"]
    stats_pattern = r'(<!-- DATA_STATS_START -->.*?<!-- DATA_STATS_END -->)'
    if re.search(stats_pattern, content, re.DOTALL):
        stats_text = (
            f"<!-- DATA_STATS_START -->\n"
            f"- 已蒸馏基金经理：{count}/{MAX_MANAGERS} 人\n"
            f"- 最后更新：{now.strftime('%Y-%m-%d %H:%M')}\n"
            f"- 数据来源：东方财富/天天基金\n"
            f"<!-- DATA_STATS_END -->"
        )
        content = re.sub(stats_pattern, stats_text, content, count=1, flags=re.DOTALL)
        updated = True

    if updated:
        # v2.1 修复：原子写入（临时文件 + replace），避免写一半崩溃损坏 SKILL.md
        tmp_path = SKILL_MD_PATH + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, SKILL_MD_PATH)
        log.info(f"SKILL.md 已自我更新（{now.strftime('%Y-%m-%d %H:%M')}）")
    else:
        log.info("SKILL.md 无需更新")

    return updated


def schedule_hint():
    """
    提示用户如何设置定时更新。
    适配任意 agent 环境：
    - ZCode 环境：可用 CronCreate 工具
    - 其他环境：可用系统 crontab 或手动运行
    """
    hint = """
📋 定期更新设置说明（支持全量/增量/智能三种模式）：

【更新模式选择】
  - update_all     全量更新：对所有经理重新抓取+蒸馏（最彻底，耗时最长）
  - stale [天数]   过期更新：只更新超过N天未刷新的经理（默认30天）
  - smart_update   智能增量：基于变化检测（规模/重仓/季报/业绩四维度），
                    只对有变化的经理执行蒸馏，无变化的仅刷新时间戳（推荐，最高效）

方式1 - ZCode 定时任务（推荐）：
  在对话中说「帮我设置每月定时更新基金经理数据」，
  我会用 CronCreate 创建每月第1个工作日 09:00 的定时任务，默认执行 smart_update。

方式2 - 手动触发：
  在对话中说「智能更新数据」或「刷新所有经理」，
  我会立即运行 smart_update 脚本（变化检测+增量蒸馏）。

方式3 - 命令行手动运行：
  python scripts/monthly_updater.py smart_update          # 智能增量更新（推荐）
  python scripts/monthly_updater.py update_all            # 全量更新
  python scripts/monthly_updater.py stale 30              # 只更新30天前的数据

方式4 - 系统定时任务（Linux/Mac crontab）：
  0 9 1 * * cd /path/to/skill-my-fund-manager && python scripts/monthly_updater.py smart_update

方式5 - Windows 任务计划程序：
  设置每月1日 09:00 运行 monthly_updater.py smart_update

【新增维护 vs 增量维护】
  - 新增维护：导入新经理到名单 -> 抓取+蒸馏
      python scripts/famous_manager_importer.py import_and_fetch <姓名>
  - 增量维护：对名单中已有经理定期刷新
      python scripts/monthly_updater.py smart_update
"""
    return hint


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python monthly_updater.py update_all [auto/llm/rules]   # 全量更新所有经理")
        print("  python monthly_updater.py update_one <经理ID> [引擎]          # 更新单个经理")
        print("  python monthly_updater.py stale [天数]                         # 只更新过期数据(>N天)")
        print("  python monthly_updater.py smart_update [新鲜天数]              # 智能增量更新(变化检测)")
        print("  python monthly_updater.py bump                                 # 仅更新SKILL.md版本")
        print("  python monthly_updater.py schedule                             # 查看定时设置说明")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "update_all":
        engine = sys.argv[2] if len(sys.argv) > 2 else "auto"
        result = update_all(distill_engine=engine)
        print(f"\n更新完成：成功{result['success']}，失败{result['failed']}")

    elif cmd == "update_one":
        if len(sys.argv) < 3:
            print("用法: python monthly_updater.py update_one <经理ID> [引擎]")
            sys.exit(1)
        mgr_id = sys.argv[2]
        engine = sys.argv[3] if len(sys.argv) > 3 else "auto"
        result = update_single_manager(mgr_id, engine)
        print(f"\n结果: {result}")

    elif cmd == "stale":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        result = update_all(distill_engine="auto", stale_only=True, days_threshold=days)
        print(f"\n过期数据更新完成：成功{result['success']}，失败{result['failed']}")

    elif cmd == "smart_update":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        result = smart_update(distill_engine="auto", days_threshold=days)
        if "message" in result:
            print(result["message"])
        else:
            print(f"\n智能增量更新完成：变化{result['changed']}，跳过{result['skipped']}，失败{result['failed']}")
            print(f"变化日志：data/change_log/{datetime.now().strftime('%Y-%m-%d')}.json")

    elif cmd == "bump":
        updated = bump_skill_version()
        print(f"SKILL.md {'已更新' if updated else '无需更新'}")

    elif cmd == "schedule":
        print(schedule_hint())
