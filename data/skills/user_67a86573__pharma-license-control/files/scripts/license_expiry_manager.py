#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医药流通ERP 证照到期扫描 + 预警 + 停用 批处理脚本
=================================================
配套 skill: pharma-license-control（医药流通ERP证照管控）

做什么
------
1. 扫描所有证照：
   - 已过期（valid_to < 今天）且状态仍为 NORMAL 的  -> 置为 EXPIRED（停用），记录到停用清单
   - 距到期 <= WARN_DAYS 天（含）且状态 NORMAL 的 -> 生成预警（不阻断）
2. 计算"可用性"：某主体能否经营某品种 = 该品种所需证照类型，是否都有一张
   【有效】的证照覆盖（覆盖方式：2.1经营范围 / 2.2品种集合 / 2.3具体品种）。
   证照过期 -> 该证失效 -> 其关联的范围/集合/品种被视为"无资质" -> 业务行被拦截。
   （这正是 skill 第 5 节"过期阻断"的落地。）

怎么跑
------
    python license_expiry_manager.py                 # 内存演示库 + 默认30天预警
    python license_expiry_manager.py --warn-days 60  # 自定义预警窗口
    python license_expiry_manager.py --db erp.db     # 接你们真实sqlite库
    python license_expiry_manager.py --json report.json

接真实 ERP（重点）
------------------
默认 LicenseRepository 用内存 SQLite + 演示数据。要接你们系统，二选一：
  A. 改 __init__ 里的 conn 指向真实 sqlite 文件（表结构见 SCHEMA，字段可改名映射）。
  B. 继承 LicenseRepository，重写 get_all_licenses() / update_status() / get_linked()，
     改成查你们 ORM 表或调 ERP 接口（见文件底部 ERPRepository 占位类）。
其余扫描/预警/可用性逻辑无需改动。

注意：具体证照类型与"某品种需要哪些证照"(required_types) 来自 skill 第 2 节 9 格矩阵，
      落地时把你们实际的证照类型枚举与品种→所需证照映射填进 CONFIG 即可。
"""

import sqlite3
import datetime as dt
import json
import sys

# ========================= 可配置区 =========================
WARN_DAYS_DEFAULT = 30  # 到期前多少天开始预警

# 证照类型枚举（示例，按你们实际字典扩展）
LIC_SUPPLIER_BASE = "SUPPLIER_BASE"        # 供应商基础（药品经营/生产许可+GSP）
LIC_SPECIAL_NARC = "SPECIAL_NARC"          # 麻精定点经营许可
LIC_SPECIAL_TOXIC = "SPECIAL_TOXIC"        # 医疗用毒性
LIC_COLDCHAIN = "COLDCHAIN"                # 冷链储存运输条件
LIC_MED_DEVICE_3 = "MED_DEVICE_3"          # 三类医疗器械经营许可

# 品种 -> 所需证照类型（来自 skill 矩阵第 2 节，示例）
# 真实环境应来自商品主数据 + 9 格规则配置，这里用字典演示。
REQUIRED_LICENSE_TYPES = {
    "P_TRAD": [LIC_SUPPLIER_BASE],                 # 中成药：基础证照
    "P_NARC": [LIC_SUPPLIER_BASE, LIC_SPECIAL_NARC],  # 麻精品种：基础 + 麻精许可
    "P_COLD": [LIC_SUPPLIER_BASE, LIC_COLDCHAIN],  # 冷链品种：基础 + 冷链条件
}

STATUS_NORMAL = "NORMAL"
STATUS_EXPIRED = "EXPIRED"
STATUS_REVOKED = "REVOKED"

SCHEMA = """
CREATE TABLE IF NOT EXISTS holder (
    id TEXT PRIMARY KEY, type TEXT, name TEXT
);
CREATE TABLE IF NOT EXISTS license (
    id TEXT PRIMARY KEY, license_type TEXT, holder_type TEXT, holder_id TEXT,
    license_no TEXT, issuer TEXT, valid_from TEXT, valid_to TEXT, status TEXT
);
CREATE TABLE IF NOT EXISTS scope_item (id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE IF NOT EXISTS product (
    id TEXT PRIMARY KEY, name TEXT, scope_item_id TEXT
);
CREATE TABLE IF NOT EXISTS productset (id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE IF NOT EXISTS license_scope_rel (license_id TEXT, scope_item_id TEXT);
CREATE TABLE IF NOT EXISTS license_productset_rel (license_id TEXT, productset_id TEXT);
CREATE TABLE IF NOT EXISTS license_product_rel (license_id TEXT, product_id TEXT);
CREATE TABLE IF NOT EXISTS productset_item (productset_id TEXT, product_id TEXT);
"""


# ========================= 数据访问层 =========================
class LicenseRepository:
    """默认实现：内存/文件 SQLite + 演示数据。可继承重写接入真实ERP。"""

    def __init__(self, conn=None):
        self.conn = conn or sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        if not self._has_data():
            self.load_demo()

    def _init_schema(self):
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def _has_data(self):
        try:
            n = self.conn.execute("SELECT COUNT(*) FROM license").fetchone()[0]
            return n > 0
        except Exception:
            return False

    # ---- 读写接口（接真实ERP时仅需重写这几个）----
    def get_all_licenses(self):
        rows = self.conn.execute("SELECT * FROM license").fetchall()
        return [dict(r) for r in rows]

    def update_status(self, license_id, status):
        self.conn.execute(
            "UPDATE license SET status=? WHERE id=?", (status, license_id)
        )
        self.conn.commit()

    def get_linked(self, license_id):
        """返回该证照关联的范围/集合/品种 id 列表（2.1/2.2/2.3）"""
        scopes = [r[0] for r in self.conn.execute(
            "SELECT scope_item_id FROM license_scope_rel WHERE license_id=?",
            (license_id,))]
        sets = [r[0] for r in self.conn.execute(
            "SELECT productset_id FROM license_productset_rel WHERE license_id=?",
            (license_id,))]
        products = [r[0] for r in self.conn.execute(
            "SELECT product_id FROM license_product_rel WHERE license_id=?",
            (license_id,))]
        return scopes, sets, products

    # ---- 演示数据 ----
    def load_demo(self):
        cur = self.conn
        holders = [
            ("S1", "SUPPLIER", "华润医药(供应商)"),
            ("S2", "SUPPLIER", "康健药业(供应商)"),
        ]
        # valid_from/valid_to 以演示"今天=2026-08-17"为基准
        licenses = [
            # S1：基础证有效；麻精证 10 天后到期(预警)；冷链证有效
            ("L1", LIC_SUPPLIER_BASE, "SUPPLIER", "S1", "XZ-001", "省药监局",
             "2024-01-01", "2026-12-31", STATUS_NORMAL),
            ("L2", LIC_SPECIAL_NARC, "SUPPLIER", "S1", "MZ-001", "省药监局",
             "2024-01-01", "2026-08-27", STATUS_NORMAL),  # 距今天10天 -> 预警
            ("L3", LIC_COLDCHAIN, "SUPPLIER", "S1", "LC-001", "省药监局",
             "2024-01-01", "2027-06-30", STATUS_NORMAL),
            # S2：基础证昨天(2026-08-16)已过期 -> 停用，导致该供应商无法经营
            ("L4", LIC_SUPPLIER_BASE, "SUPPLIER", "S2", "XZ-002", "省药监局",
             "2024-01-01", "2026-08-16", STATUS_NORMAL),
        ]
        scopes = [("SC_TRAD", "中成药"), ("SC_NARC", "麻精药品"), ("SC_COLD", "冷链品种")]
        products = [
            ("P_TRAD", "感冒灵颗粒", "SC_TRAD"),
            ("P_NARC", "盐酸吗啡注射液", "SC_NARC"),
            ("P_COLD", "人胰岛素注射液", "SC_COLD"),
        ]
        sets = [("SET_NARC", "麻精品种集合")]
        rel_scope = [
            ("L1", "SC_TRAD"), ("L1", "SC_NARC"), ("L1", "SC_COLD"),
            ("L2", "SC_NARC"), ("L3", "SC_COLD"),
            ("L4", "SC_TRAD"), ("L4", "SC_NARC"), ("L4", "SC_COLD"),
        ]
        rel_set = [("L2", "SET_NARC")]
        rel_product = []  # 演示用：麻精品种走集合，不逐SKU挂；可在此加2.3示例
        set_items = [("SET_NARC", "P_NARC")]

        cur.executemany("INSERT INTO holder VALUES (?,?,?)", holders)
        cur.executemany(
            "INSERT INTO license VALUES (?,?,?,?,?,?,?,?,?)", licenses)
        cur.executemany("INSERT INTO scope_item VALUES (?,?)", scopes)
        cur.executemany("INSERT INTO product VALUES (?,?,?)", products)
        cur.executemany("INSERT INTO productset VALUES (?,?)", sets)
        cur.executemany(
            "INSERT INTO license_scope_rel VALUES (?,?)", rel_scope)
        cur.executemany(
            "INSERT INTO license_productset_rel VALUES (?,?)", rel_set)
        cur.executemany(
            "INSERT INTO license_product_rel VALUES (?,?)", rel_product)
        cur.executemany(
            "INSERT INTO productset_item VALUES (?,?)", set_items)
        cur.commit()


# ========================= 核心逻辑 =========================
def parse_date(s):
    return dt.date.fromisoformat(s)


def days_to(lic, today):
    return (parse_date(lic["valid_to"]) - today).days


def is_valid(lic, today):
    """有效 = 在有效期区间内 且 状态正常 且 未被吊销/注销"""
    if lic["status"] in (STATUS_EXPIRED, STATUS_REVOKED):
        return False
    vf, vt = parse_date(lic["valid_from"]), parse_date(lic["valid_to"])
    return vf <= today <= vt


def scan(repo, today, warn_days):
    """扫描：过期停用 + 临期预警。返回 (deactivated, warnings)"""
    deactivated, warnings = [], []
    for lic in repo.get_all_licenses():
        if lic["status"] != STATUS_NORMAL:
            continue
        d = days_to(lic, today)
        if d < 0:  # 已过期
            repo.update_status(lic["id"], STATUS_EXPIRED)
            scopes, sets, prods = repo.get_linked(lic["id"])
            deactivated.append({
                "license_id": lic["id"], "license_no": lic["license_no"],
                "type": lic["license_type"], "holder_id": lic["holder_id"],
                "holder_type": lic["holder_type"], "expired_on": lic["valid_to"],
                "linked_scopes": scopes, "linked_productsets": sets,
                "linked_products": prods,
            })
        elif d <= warn_days:  # 临期预警（不阻断）
            warnings.append({
                "license_id": lic["id"], "license_no": lic["license_no"],
                "type": lic["license_type"], "holder_id": lic["holder_id"],
                "expires_on": lic["valid_to"], "days_left": d,
            })
    return deactivated, warnings


def authorized_licenses(repo, holder_type, holder_id, product_id, today):
    """返回某主体经营某品种时，覆盖它的【有效】证照列表（2.1/2.2/2.3 任一即可）"""
    prod = repo.conn.execute(
        "SELECT scope_item_id FROM product WHERE id=?", (product_id,)
    ).fetchone()
    scope = prod["scope_item_id"] if prod else None
    sets_of_product = [r[0] for r in repo.conn.execute(
        "SELECT productset_id FROM productset_item WHERE product_id=?",
        (product_id,))]
    result = []
    for lic in repo.get_all_licenses():
        if not (lic["holder_type"] == holder_type and lic["holder_id"] == holder_id):
            continue
        if not is_valid(lic, today):
            continue
        s, st, p = repo.get_linked(lic["id"])
        if scope in s or any(x in st for x in sets_of_product) or product_id in p:
            result.append(lic)
    return result


def is_available(repo, holder_type, holder_id, product_id, today):
    """可用性 = 该品种所需证照类型，每种都至少有1张有效覆盖证照"""
    required = REQUIRED_LICENSE_TYPES.get(product_id, [LIC_SUPPLIER_BASE])
    authorized = authorized_licenses(repo, holder_type, holder_id, product_id, today)
    have_types = {l["license_type"] for l in authorized}
    missing = [t for t in required if t not in have_types]
    return (len(missing) == 0), missing


# ========================= 报告 =========================
def build_report(repo, today, warn_days):
    deactivated, warnings = scan(repo, today, warn_days)
    # 抽查可用性（演示过期阻断效果）
    checks = [
        ("SUPPLIER", "S1", "P_NARC"),   # 应可用（L1+L2有效）
        ("SUPPLIER", "S2", "P_TRAD"),   # 应被阻断（L4过期）
        ("SUPPLIER", "S2", "P_NARC"),   # 应被阻断
    ]
    availability = []
    for ht, hid, pid in checks:
        ok, missing = is_available(repo, ht, hid, pid, today)
        availability.append({
            "holder": hid, "product": pid,
            "available": ok, "missing_types": missing,
        })
    return {
        "scan_date": today.isoformat(),
        "warn_days": warn_days,
        "deactivated_count": len(deactivated),
        "warning_count": len(warnings),
        "deactivated": deactivated,
        "warnings": warnings,
        "availability_check": availability,
    }


def print_report(r):
    print("=" * 60)
    print(f"证照扫描报告  扫描日={r['scan_date']}  预警窗口={r['warn_days']}天")
    print("=" * 60)
    print(f"[停用] 过期证照 {r['deactivated_count']} 张：")
    for d in r["deactivated"]:
        print(f"  - {d['license_no']}({d['type']}) 主体={d['holder_id']} "
              f"到期={d['expired_on']} 关联范围={d['linked_scopes']} "
              f"集合={d['linked_productsets']} 品种={d['linked_products']}")
    print(f"[预警] 临期证照 {r['warning_count']} 张：")
    for w in r["warnings"]:
        print(f"  - {w['license_no']}({w['type']}) 主体={w['holder_id']} "
              f"到期={w['expires_on']} 剩余{w['days_left']}天")
    print("[可用性核查] 过期即阻断：")
    for a in r["availability_check"]:
        tag = "可用" if a["available"] else f"阻断(缺{a['missing_types']})"
        print(f"  - 主体={a['holder']} 品种={a['product']} -> {tag}")
    print("=" * 60)


# ========================= 入口 =========================
def main(argv):
    warn_days = WARN_DAYS_DEFAULT
    db_path = None
    json_out = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--warn-days":
            warn_days = int(argv[i + 1]); i += 2; continue
        if a == "--db":
            db_path = argv[i + 1]; i += 2; continue
        if a == "--json":
            json_out = argv[i + 1]; i += 2; continue
        i += 1
    conn = sqlite3.connect(db_path) if db_path else None
    repo = LicenseRepository(conn)
    today = dt.date.today()
    report = build_report(repo, today, warn_days)
    print_report(report)
    if json_out:
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"JSON 报告已写出: {json_out}")
    return report


if __name__ == "__main__":
    main(sys.argv[1:])


# ========================= 接真实 ERP 的占位类 =========================
# class ERPRepository(LicenseRepository):
#     """示例：重写以下方法，改为查你们 ORM/调接口。其余逻辑不动。"""
#     def get_all_licenses(self):
#         # return list of dict(license_id, license_type, holder_type, holder_id,
#         #                     license_no, valid_from, valid_to, status)
#         raise NotImplementedError("对接你们的证照表/接口")
#     def update_status(self, license_id, status):
#         # 调 ERP 接口或 UPDATE 你们的表
#         raise NotImplementedError
#     def get_linked(self, license_id):
#         # 返回 (scope_ids, productset_ids, product_ids)
#         raise NotImplementedError
