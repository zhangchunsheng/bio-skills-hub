"""
基金经理名单管理模块
维护已蒸馏基金经理名单（最多100名），支持新增、删除、查看、状态管理。
名单存储在 data/roster.json。
支持知名基金经理种子库一键导入（见 famous_manager_importer.py）。
"""

import os
from datetime import datetime

import _common
from _common import read_json, write_json, log

# v2.0 修复：不要 from X import Y 引入路径常量！
# from x import y 在模块加载时会把 y 的当前值绑定到本地命名空间，
# 之后若 _common 修改了常量（如测试时切换到临时目录），这里的本地变量不会跟随更新。
# 修复方法：所有代码统一走 _common.ROSTER_PATH，不保留本地常量。

MAX_MANAGERS = 100


def _display(name, company):
    """格式化显示名，私募管理人的 name 与 company 相同时避免重复"""
    if company and company != name:
        return f"{name}（{company}）"
    return name

def _load_roster():
    """加载名单"""
    return read_json(_common.ROSTER_PATH, default={"meta": {"version": 1, "last_update": "", "count": 0, "max": MAX_MANAGERS}, "managers": []})


def _save_roster(roster):
    """保存名单并更新元数据"""
    roster["meta"]["count"] = len(roster["managers"])
    roster["meta"]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    roster["meta"]["max"] = MAX_MANAGERS
    write_json(_common.ROSTER_PATH, roster)
    log.info(f"名单已保存：{roster['meta']['count']}/{MAX_MANAGERS} 人")


def get_roster():
    """获取完整名单"""
    return _load_roster()


def list_managers():
    """列出名单中所有经理，返回摘要列表"""
    roster = _load_roster()
    return [
        {
            "id": m["id"],
            "name": m["name"],
            "company": m.get("company", ""),
            "manager_type": m.get("manager_type", "公募"),
            "add_date": m.get("add_date", ""),
            "last_refresh": m.get("last_refresh", ""),
            "status": m.get("status", "active"),
        }
        for m in roster["managers"]
    ]


def is_full():
    """检查名单是否已满"""
    roster = _load_roster()
    return len(roster["managers"]) >= MAX_MANAGERS


def is_in_roster(manager_id):
    """检查经理是否已在名单中"""
    roster = _load_roster()
    return any(m["id"] == str(manager_id) for m in roster["managers"])


def add_manager(manager_id, name, company="", fund_count=0, tenure_return="", scale="", manager_type=None):
    """
    添加经理到名单。
    manager_type: 公募/私募（自动根据ID前缀判断：amac_=私募，其他=公募）
    返回:
        - 成功: {"success": True, "message": "..."}
        - 已存在: {"success": False, "message": "该经理已在名单中"}
        - 名单已满: {"success": False, "message": "名单已满（最多100名），请先删除一些经理"}
    """
    manager_id = str(manager_id)
    # 自动判断经理类型
    if manager_type is None:
        manager_type = "私募" if manager_id.startswith("amac_") else "公募"
    roster = _load_roster()

    # 去重检查
    if is_in_roster(manager_id):
        return {"success": False, "message": f"{_display(name, company)}已在名单中，无需重复添加"}
    # 上限检查
    if len(roster["managers"]) >= MAX_MANAGERS:
        return {
            "success": False,
            "message": f"名单已满（最多{MAX_MANAGERS}名），请先删除一些经理后再添加",
        }

    # 添加
    entry = {
        "id": manager_id,
        "name": name,
        "company": company,
        "manager_type": manager_type,
        "fund_count": fund_count,
        "tenure_return": tenure_return,
        "scale": scale,
        "add_date": datetime.now().strftime("%Y-%m-%d"),
        "last_refresh": "",
        "status": "active",  # active=已加入待蒸馏, distilled=已蒸馏, stale=数据过期
    }
    roster["managers"].append(entry)
    _save_roster(roster)

    log.info(f"已添加经理：{_display(name, company)}，名单共{len(roster['managers'])}人")
    return {
        "success": True,
        "message": f"✅ 已添加 {_display(name, company)}到名单。当前名单共{len(roster['managers'])}/{MAX_MANAGERS}人。",
        "manager": entry,
    }


def remove_manager(manager_id):
    """
    从名单中删除经理（忘记经理）。
    同时删除该经理的档案文件。
    返回: {"success": True/False, "message": "..."}
    """
    manager_id = str(manager_id)
    roster = _load_roster()

    # 查找
    target = None
    for i, m in enumerate(roster["managers"]):
        if m["id"] == manager_id:
            target = roster["managers"].pop(i)
            break

    if not target:
        return {"success": False, "message": f"名单中未找到ID为{manager_id}的经理"}

    _save_roster(roster)

    # 删除档案文件
    from _common import manager_path
    path = manager_path(manager_id)
    if os.path.exists(path):
        os.remove(path)
        log.info(f"已删除经理档案文件：{path}")

    log.info(f"已从名单删除：{_display(target['name'], target.get('company',''))}")
    return {
        "success": True,
        "message": f"✅ 已从名单删除 {_display(target['name'], target.get('company',''))}，同时清除其档案数据。"
                   f"当前名单共{len(roster['managers'])}/{MAX_MANAGERS}人。",
    }


def remove_manager_by_name(name):
    """按姓名删除经理（大小写不敏感，如果有同名，删除第一个匹配的）"""
    roster = _load_roster()
    name_lower = name.lower()
    for m in roster["managers"]:
        m_name_lower = m["name"].lower()
        if name_lower in m_name_lower or m_name_lower in name_lower:
            return remove_manager(m["id"])
    return {"success": False, "message": f"名单中未找到姓名包含「{name}」的经理"}


# v2.0 增加：合法状态白名单（防止静默写入非法值）
VALID_STATUSES = {"active", "distilled", "stale"}


def update_status(manager_id, status):
    """更新经理状态（active/distilled/stale）

    Args:
        manager_id: 经理 ID
        status: 必须是 active / distilled / stale 之一

    v2.0 增加：非法 status 返回错误而非静默写入。
    """
    manager_id = str(manager_id)
    if status not in VALID_STATUSES:
        return {
            "success": False,
            "message": f"非法状态值 '{status}'。合法值：{', '.join(sorted(VALID_STATUSES))}",
        }
    roster = _load_roster()
    for m in roster["managers"]:
        if m["id"] == manager_id:
            m["status"] = status
            _save_roster(roster)
            return {"success": True, "message": f"{m['name']} 状态已更新为 {status}"}
    return {"success": False, "message": f"未找到ID为{manager_id}的经理"}


def mark_distilled(manager_id):
    """标记经理为已蒸馏状态，同时更新最后刷新时间（一次保存，避免双重写入）"""
    manager_id = str(manager_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    roster = _load_roster()
    for m in roster["managers"]:
        if m["id"] == manager_id:
            m["status"] = "distilled"
            m["last_refresh"] = now
            _save_roster(roster)
            return True
    return False


def refresh_entry_meta(manager_id, **kwargs):
    """
    刷新名单条目中的元数据字段（不覆盖未提供的字段）。
    支持的字段: fund_count, tenure_return, scale, manager_type, name, company
    """
    manager_id = str(manager_id)
    roster = _load_roster()
    for m in roster["managers"]:
        if m["id"] == manager_id:
            for key in ("fund_count", "tenure_return", "scale", "manager_type", "name", "company"):
                if key in kwargs and kwargs[key]:
                    m[key] = kwargs[key]
            _save_roster(roster)
            return True
    return False


def update_last_refresh(manager_id):
    """更新经理的最后刷新时间"""
    manager_id = str(manager_id)
    roster = _load_roster()
    for m in roster["managers"]:
        if m["id"] == manager_id:
            m["last_refresh"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save_roster(roster)
            return True
    return False


def get_stale_managers(days_threshold=30):
    """获取数据过期的经理（超过days_threshold天未刷新）"""
    roster = _load_roster()
    stale = []
    now = datetime.now()
    for m in roster["managers"]:
        last = m.get("last_refresh", "")
        if not last:
            # 从未刷新过，用添加日期判断
            last = m.get("add_date", "")
        if last:
            try:
                dt = datetime.strptime(last[:10], "%Y-%m-%d")
                if (now - dt).days > days_threshold:
                    stale.append(m)
            except ValueError:
                pass
        else:
            stale.append(m)
    return stale


def format_roster():
    """格式化名单为可读文本"""
    roster = _load_roster()
    managers = roster["managers"]
    meta = roster["meta"]

    if not managers:
        return (
            "📋 我的基金经理名单（0/100人）\n"
            "名单为空。请告诉我要跟踪哪位基金经理（提供姓名/基金代码/产品名/公司名），"
            "我会帮您搜索并添加到名单。\n"
            "💡 提示：可执行 `python scripts/famous_manager_importer.py list` "
            "查看 2025-2026 知名基金经理种子库，一键导入。"
        )

    lines = [
        f"📋 我的基金经理名单（{len(managers)}/{MAX_MANAGERS}人）",
        f"   最后更新：{meta.get('last_update', 'N/A')}\n",
        f"{'序号':<4} {'类型':<6} {'姓名':<10} {'基金公司':<14} {'状态':<10} {'添加日期':<12} {'最后刷新':<12}",
        "-" * 90,
    ]

    status_emoji = {"active": "🆕待蒸馏", "distilled": "✅已蒸馏", "stale": "⚠️需更新"}
    type_emoji = {"公募": "🏆公募", "私募": "📈私募"}

    for i, m in enumerate(managers):
        status = status_emoji.get(m.get("status", "active"), m.get("status", ""))
        mtype = type_emoji.get(m.get("manager_type", "公募"), m.get("manager_type", "🏆公募"))
        name = m['name'][:8]  # 截断过长的名字
        company = m.get('company','')[:12]  # 截断过长的公司名
        lines.append(
            f"{i+1:<4} {mtype:<6} {name:<10} {company:<14} {status:<10} "
            f"{m.get('add_date',''):<12} {m.get('last_refresh','未刷新'):<12}"
        )

    return "\n".join(lines)


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python roster_manager.py list              # 查看名单")
        print("  python roster_manager.py add <id> <name> [company]  # 添加经理")
        print("  python roster_manager.py remove <id|name>   # 删除经理")
        print("  python roster_manager.py stale [天数]       # 查看过期经理")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        print(format_roster())
    elif cmd == "add":
        if len(sys.argv) < 4:
            print("用法: python roster_manager.py add <id> <name> [company]")
            sys.exit(1)
        result = add_manager(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
        print(result["message"])
    elif cmd == "remove":
        if len(sys.argv) < 3:
            print("用法: python roster_manager.py remove <id|name>")
            sys.exit(1)
        arg = sys.argv[2]
        # 支持纯数字ID（公募）和 amac_ 前缀ID（私募）
        if arg.isdigit() or arg.startswith("amac_"):
            result = remove_manager(arg)
        else:
            result = remove_manager_by_name(arg)
        print(result["message"])
    elif cmd == "stale":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        stale = get_stale_managers(days)
        if stale:
            print(f"以下 {len(stale)} 位经理的数据已超过{days}天未更新：")
            for m in stale:
                print(f"  {m['name']}（{m.get('company','')}）- 最后刷新: {m.get('last_refresh','从未')}")
        else:
            print(f"所有经理的数据都在{days}天内更新过")
    else:
        print(f"未知命令: {cmd}")
