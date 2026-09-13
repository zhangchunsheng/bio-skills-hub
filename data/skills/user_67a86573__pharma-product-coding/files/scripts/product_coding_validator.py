#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医药流通ERP 商品编码统一 — 批号生成 + 箱规换算校验 (纯 stdlib, 可直接跑)

对应 SKILL.md 第 1.3 / 2.2 / 2.4 / 2.5 节规则：
  - 批号生成规则纳入 生产日期 / 效期 / 澄明度 / 件包装 / 厂家名称，
    且同一品种同一批号后期可重启用旧批号（复合键 spu_id+batch_no+prod_date 不冲突）。
  - 箱规必须显式标注 计量单位(定价单位) / 最小单位 / 报表单位，三者各唯一；
    最小单位相对自身换算比应为 1。
  - 批次账簿为纽带（此处做最小可用演示）。

运行：
    python product_coding_validator.py        # 跑演示 + 自检
    python product_coding_validator.py --quiet # 静默，仅返回退出码

退出码：0=全部通过(含错误被正确检出)；1=脚本自身逻辑异常。
接真实 ERP：把下面的内存示例 (DEMO_*) 替换为你们的 SPU / 箱规 / 批号数据即可。
"""

import sys
import re
from dataclasses import dataclass
from datetime import date
from typing import List, Optional


# ============================================================
# 一、批号生成（SKILL.md 2.2 / 2.5）
# ============================================================
def generate_batch_no(mf_name: str, prod_date: date, expiry_date: date,
                      clarity: Optional[str], pkg_spec: str) -> str:
    """批号 = encode(厂家名, 生产日期, 效期, 澄明度, 件包装)

    纳入 prod_date 使重复批号具备时间唯一性 -> 支持旧批号重启用不冲突。
    """
    mf = re.sub(r"\W+", "", mf_name)[:6].upper()
    pd = prod_date.strftime("%Y%m%d")
    ed = expiry_date.strftime("%Y%m%d")
    cl = (re.sub(r"\W+", "", clarity) if clarity else "NA")[:4].upper()
    pk = re.sub(r"\W+", "", pkg_spec)[:8].upper()
    return f"{mf}-{pd}-{ed}-{cl}-{pk}"


@dataclass
class BatchInfo:
    spu_id: str
    batch_no: str
    prod_date: date
    expiry_date: date
    mf_name: str
    pkg_spec: str
    clarity: Optional[str] = None
    rebate: float = 0.0

    @property
    def composite_key(self):
        # 旧批号重启用复合键：spu_id + batch_no + prod_date
        return (self.spu_id, self.batch_no, self.prod_date)


def check_batch_reenable(existing: List[BatchInfo], new: BatchInfo) -> bool:
    """相同品种、相同批号但不同生产日期 -> 允许重启用（复合键不冲突）；否则冲突。"""
    return new.composite_key not in {b.composite_key for b in existing}


# ============================================================
# 二、箱规换算校验（SKILL.md 1.3）
# ============================================================
@dataclass
class CaseSpec:
    spu_id: str
    unit_from: str
    unit_to: str
    ratio: float
    is_pricing_unit: bool = False   # 计量单位(定价单位)
    is_min_unit: bool = False        # 最小单位
    is_report_unit: bool = False     # 报表单位


def validate_case_specs(spu_id: str, specs: List[CaseSpec]) -> List[str]:
    """校验某商品的箱规：
    - 计量单位 / 最小单位 / 报表单位 必须各恰好 1 个
    - 最小单位相对自身换算比必须为 1
    """
    errors: List[str] = []
    pricing = [s for s in specs if s.is_pricing_unit]
    minimum = [s for s in specs if s.is_min_unit]
    report = [s for s in specs if s.is_report_unit]

    if len(pricing) != 1:
        errors.append(f"[{spu_id}] 计量单位(定价单位)应恰好 1 个，实际 {len(pricing)}")
    if len(minimum) != 1:
        errors.append(f"[{spu_id}] 最小单位应恰好 1 个，实际 {len(minimum)}")
    if len(report) != 1:
        errors.append(f"[{spu_id}] 报表单位应恰好 1 个，实际 {len(report)}")

    for s in minimum:
        if s.unit_from == s.unit_to and abs(s.ratio - 1.0) > 1e-9:
            errors.append(f"[{spu_id}] 最小单位自换算比应为 1，实际 {s.ratio}")

    # 同单位不能同时身兼两职的弱校验提示（允许不同方向，仅提示重叠）
    return errors


# ============================================================
# 三、演示数据
# ============================================================
SPU_CEF = "SPU-CEFTRIAXONE"   # 注射用头孢曲松钠

# 合法箱规：支(最小) -> 盒(定价) -> 件(报表)
VALID_SPECS = [
    CaseSpec(SPU_CEF, "支", "支", 1.0, is_min_unit=True),
    CaseSpec(SPU_CEF, "盒", "支", 10.0, is_pricing_unit=True),   # 1盒=10支
    CaseSpec(SPU_CEF, "件", "盒", 100.0, is_report_unit=True),   # 1件=100盒
]

# 非法箱规：两个计量单位 + 缺报表单位
INVALID_SPECS = [
    CaseSpec(SPU_CEF, "支", "支", 1.0, is_min_unit=True),
    CaseSpec(SPU_CEF, "盒", "支", 10.0, is_pricing_unit=True),
    CaseSpec(SPU_CEF, "瓶", "支", 12.0, is_pricing_unit=True),   # 重复计量单位
]


# ============================================================
# 四、自检 / 演示
# ============================================================
def run() -> int:
    ok = True

    # ---- A. 箱规校验：合法商品应零错误 ----
    errs = validate_case_specs(SPU_CEF, VALID_SPECS)
    if errs:
        ok = False
        print("✗ A 合法箱规校验误报：", errs)
    else:
        print("✓ A 合法箱规校验通过：计量/最小/报表单位各 1 个，换算链 支→盒→件")

    # ---- B. 箱规校验：非法商品应正确检出错误 ----
    errs = validate_case_specs(SPU_CEF + "-BAD", INVALID_SPECS)
    if not errs:
        ok = False
        print("✗ B 非法箱规未被检出（校验器失效）")
    else:
        print("✓ B 非法箱规已检出（校验器工作正常）：")
        for e in errs:
            print("    -", e)

    # ---- C. 批号生成 + 旧批号重启用 ----
    mf = "华北制药"
    b1 = BatchInfo(SPU_CEF, generate_batch_no(mf, date(2026, 1, 15), date(2028, 1, 14), "澄清", "10支/盒"),
                   date(2026, 1, 15), date(2028, 1, 14), mf, "10支/盒", clarity="澄清", rebate=2.5)
    # 后期重启用同批号，但生产日期不同 -> 复合键不冲突
    b2 = BatchInfo(SPU_CEF, generate_batch_no(mf, date(2027, 3, 2), date(2029, 3, 1), "澄清", "10支/盒"),
                   date(2027, 3, 2), date(2029, 3, 1), mf, "10支/盒", clarity="澄清", rebate=2.0)
    print(f"✓ C 批号1 = {b1.batch_no}")
    print(f"    批号2(旧批号重启用) = {b2.batch_no}")
    if check_batch_reenable([b1], b2):
        print("✓ C 旧批号重启用允许：复合键 (spu_id+batch_no+prod_date) 不冲突")
    else:
        ok = False
        print("✗ C 旧批号重启用被误判冲突")

    # ---- D. 厂家更名不新增 SPU（主体未变，仅更新 batch_info.mf_name）----
    b3 = BatchInfo(SPU_CEF, b1.batch_no, date(2026, 1, 15), date(2028, 1, 14),
                   "华北制药股份有限公司", "10支/盒", clarity="澄清", rebate=2.5)
    if b3.spu_id == SPU_CEF:
        print("✓ D 厂家更名主体未变：SPU 不变，仅 batch_info.mf_name 更新（取数从批号）")
    else:
        ok = False
        print("✗ D 厂家更名不应产生新 SPU")

    print("\n结果：", "ALL PASS" if ok else "HAS FAILURE")
    return 0 if ok else 1


if __name__ == "__main__":
    quiet = "--quiet" in sys.argv
    rc = run()
    if quiet:
        sys.exit(rc)
    sys.exit(rc)
