#!/usr/bin/env python3
"""
制药资金管理模型（Pharma Cash Management Models）
=================================================
包含5个医药行业专用资金管理模型：
1. 药品库存与回款周转模型
2. 研发现金储备模型
3. API/制剂GMP库存模型
4. 医院/经销商信用评级模型
5. 药物开发现金流滚动预算模型（Phase-Gate）

基于 Finance Director Enhanced v4.0.0 资金管理五大模型改造
"""

import math
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


# =============================================================================
# 数据类型定义
# =============================================================================

class HospitalGrade(Enum):
    """医院等级"""
    GRADE_3A = "三甲"
    GRADE_3B = "三乙"
    GRADE_2A = "二甲"
    GRADE_2B = "二乙"
    GRADE_1 = "一级"
    COMMUNITY = "社区/基层"


class InventoryCategory(Enum):
    """GMP库存分类"""
    COLD_CHAIN_BIOLOGIC = "A_冷链生物药"  # A类：效期<12个月，严格效期管理
    REGULAR_CHEMICAL = "B_常规化学药"     # B类：常规库存管理
    EXCIPIENT_PACKAGING = "C_辅料包材"    # C类：批量采购


class DevelopmentPhase(Enum):
    """开发阶段（Phase-Gate）"""
    PRECLINICAL = "preclinical"
    PHASE_I = "phase_i"
    PHASE_II = "phase_ii"
    PHASE_III = "phase_iii"
    NDA = "nda"
    LAUNCHED = "launched"


# =============================================================================
# 输入数据类型
# =============================================================================

@dataclass
class DrugInventoryInput:
    """药品库存与回款周转输入"""
    company_name: str

    # 库存周转
    api_inventory_days: float  # API库存天数
    production_cycle_days: float  # 制剂生产周期（天）
    finished_goods_days: float  # 成品库存天数

    # 回款周期
    hospital_receivables_days: float  # 医院回款天数
    distributor_receivables_days: float = 30  # 经销商回款天数

    # 应付
    supplier_payables_days: float = 60  # 供应商账期
    cro_payment_terms_days: float = 30  # CRO付款条款

    # 生物药特有
    is_biologic: bool = False
    cold_chain_shelf_life_months: float = 18  # 冷链效期（月）


@dataclass
class RDCashReserveInput:
    """研发现金储备输入"""
    company_name: str
    monthly_burn_rate: float  # 月Burn Rate

    # 里程碑
    next_milestone_payment: float = 0
    months_to_milestone: int = 12

    # 管线
    n_active_clinical_programs: int = 1
    clinical_phase: DevelopmentPhase = DevelopmentPhase.PHASE_II

    # 融资
    financing_lead_time_months: int = 6
    monthly_overhead: float = 0  # 固定月度管理费（即使管线暂停也要付）


@dataclass
class GMPInventoryInput:
    """GMP库存管理输入"""
    company_name: str

    # 库存数据
    products: List[Dict]  # [{"name": str, "category": str, "value": float,
                          #   "shelf_life_months": float, "monthly_consumption": float}]

    # GMP合规
    gmp_sample_retention_pct: float = 0.02  # 留样比例
    temperature_excursion_risk: str = "low"  # 温度偏移风险：low/medium/high


@dataclass
class HospitalCreditInput:
    """医院信用评级输入"""
    customers: List[Dict]  # [{"name": str, "grade": HospitalGrade, "payment_history": str,
                          #   "annual_purchase": float, "province_gdp_rank": int,
                          #   "insurance_settlement_cycle_months": float}]

    drug_type: str = "innovative"  # innovative/generic


@dataclass
class PhaseGateBudgetInput:
    """Phase-Gate预算输入"""
    drug_name: str
    current_phase: DevelopmentPhase
    phases: List[Dict]  # [{"phase": str, "duration_months": int, "monthly_cost": float,
                        #   "one_time_costs": [{"item": str, "amount": float, "month": int}]}]

    current_cash: float
    monthly_revenue: float = 0  # 已有产品收入
    discount_rate: float = 0.10


# =============================================================================
# 核心模型
# =============================================================================

class PharmaCashModels:
    """制药资金管理模型主类"""

    def __init__(self):
        pass

    # -------------------------------------------------------------------------
    # 1. 药品库存与回款周转模型
    # -------------------------------------------------------------------------

    def drug_cash_conversion_cycle(self, input_data: DrugInventoryInput) -> Dict:
        """
        药品现金周转周期模型

        制药特化公式：
        制药CCC = API库存天数 + 生产周期 + 成品库存天数 + 医院回款天数 - 供应商账期
        """
        # 上游：采购周期
        upstream_days = input_data.api_inventory_days + input_data.supplier_payables_days

        # 内部：生产和库存
        internal_days = input_data.production_cycle_days + input_data.finished_goods_days

        # 下游：回款周期
        downstream_days = input_data.hospital_receivables_days

        # 净现金周转周期
        ccc = (input_data.api_inventory_days +
               input_data.production_cycle_days +
               input_data.finished_goods_days +
               input_data.hospital_receivables_days -
               input_data.supplier_payables_days)

        # 行业对标
        industry_ccc_reference = {
            "innovative": 365,    # 创新药：约12个月（研发+回款长）
            "biosimilar": 300,    # 生物类似药：约10个月
            "generic": 180,      # 仿制药：约6个月（周转快）
        }

        # 评估
        if input_data.is_biologic:
            target_ccc = 300
            drug_label = "生物药"
        else:
            target_ccc = 180
            drug_label = "化学药"

        if ccc < target_ccc:
            assessment = f"✅ CCC={ccc:.0f}天，优于{drug_label}行业平均（{target_ccc}天）"
        elif ccc < target_ccc * 1.3:
            assessment = f"⚠️ CCC={ccc:.0f}天，略高于行业平均（{target_ccc}天），关注回款周期"
        else:
            assessment = f"❌ CCC={ccc:.0f}天，显著高于行业平均（{target_ccc}天），需优化库存和回款"

        # 生物药特有：效期压力
        if input_data.is_biologic:
            shelf_life_days = input_data.cold_chain_shelf_life_months * 30
            if input_data.api_inventory_days + input_data.finished_goods_days > shelf_life_days * 0.5:
                assessment += f"\n⚠️ 冷链效期风险：库存天数已超过效期的50%，存在过期报废风险"

        return {
            "公司名称": input_data.company_name,
            "API库存天数": f"{input_data.api_inventory_days:.0f}天",
            "制剂生产周期": f"{input_data.production_cycle_days:.0f}天",
            "成品库存天数": f"{input_data.finished_goods_days:.0f}天",
            "医院回款天数": f"{input_data.hospital_receivables_days:.0f}天",
            "供应商账期": f"-{input_data.supplier_payables_days:.0f}天",
            "净现金周转周期（CCC）": f"{ccc:.0f}天（{ccc/30:.1f}个月）",
            "上游占用（采购+应付）": f"{upstream_days:.0f}天",
            "内部占用（生产+库存）": f"{internal_days:.0f}天",
            "下游占用（回款）": f"{downstream_days:.0f}天",
            "药物类型": "生物药（冷链）" if input_data.is_biologic else "化学药",
            "评估": assessment,
        }

    # -------------------------------------------------------------------------
    # 2. 研发现金储备模型
    # -------------------------------------------------------------------------

    def rd_cash_reserve(self, input_data: RDCashReserveInput) -> Dict:
        """
        研发现金储备模型

        基于Burn Rate计算安全现金储备
        """
        company = input_data.company_name
        monthly_overhead = input_data.monthly_overhead or input_data.monthly_burn_rate * 0.15

        # 下限：6个月Burn Rate + 紧急融资周期
        reserve_lower = input_data.monthly_burn_rate * 6

        # 上限：18个月Burn Rate（但不超过2年）
        reserve_upper = input_data.monthly_burn_rate * 18

        # 最优：12个月Burn Rate + 下一里程碑付款 + 融资周期缓冲
        reserve_optimal = (input_data.monthly_burn_rate * 12 +
                          input_data.next_milestone_payment +
                          input_data.monthly_burn_rate * input_data.financing_lead_time_months)

        # 最低生存线（仅覆盖固定费用，暂停所有管线）
        survival_minimum = (monthly_overhead * 12 +
                           input_data.next_milestone_payment)

        # 当前现金状态
        current = input_data.monthly_burn_rate * (input_data.months_to_milestone + 3)

        return {
            "公司名称": company,
            "月Burn Rate（万元）": round(input_data.monthly_burn_rate / 10000, 0),
            "活跃临床项目数": input_data.n_active_clinical_programs,
            "当前临床阶段": input_data.clinical_phase.value,
            "现金储备建议": {
                "资金下限（6个月Burn，万元）": round(reserve_lower / 10000, 0),
                "最优储备（12个月Burn+里程碑，万元）": round(reserve_optimal / 10000, 0),
                "资金上限（18个月Burn，可投资，万元）": round(reserve_upper / 10000, 0),
                "最低生存线（仅固定费用，万元）": round(survival_minimum / 10000, 0),
            },
            "储备率（储备/最优）": f"{current / reserve_optimal:.0%}" if reserve_optimal > 0 else "N/A",
            "超额资金（万元）": f"{max(0, current - reserve_upper) / 10000:.0f}" if current > reserve_upper else "0",
            "建议": self._generate_reserve_advice(
                current, reserve_lower, reserve_optimal, reserve_upper
            ),
        }

    def _generate_reserve_advice(
        self, current: float, lower: float, optimal: float, upper: float
    ) -> str:
        """生成现金储备建议"""
        if current < lower:
            return "🔴 紧急：现金低于安全下限！立即启动融资或暂停非核心管线"
        elif current < optimal:
            shortfall = (optimal - current) / 10000
            return f"🟠 不足：现金低于最优储备，缺口约{shortfall:.0f}万元。建议在1-2个月内启动融资"
        elif current < upper:
            return "🟡 合理：现金在安全范围内，可维持正常运营。关注下一里程碑需求"
        else:
            excess = (current - upper) / 10000
            return f"🟢 充裕：现金超出资金上限约{excess:.0f}万元。超额部分可考虑短期理财（确保T+3赎回）"

    # -------------------------------------------------------------------------
    # 3. API/制剂GMP库存模型
    # -------------------------------------------------------------------------

    def gmp_inventory_management(self, input_data: GMPInventoryInput) -> Dict:
        """
        API/制剂GMP库存管理模型

        ABC分类依据：效期敏感性（而非货值）
        - A类：冷链生物药，严格效期管理，过期即报废
        - B类：常规化学药制剂，常规库存管理
        - C类：辅料/包材/试剂，批量采购
        """
        products = input_data.products
        total_value = sum(p["value"] for p in products)

        classified = []
        total_expiry_risk = 0

        for p in products:
            cat = p.get("category", "B_常规化学药")
            value = p["value"]
            shelf_life = p.get("shelf_life_months", 36)
            monthly_cons = p.get("monthly_consumption", 0)

            # 库存覆盖月数
            if monthly_cons > 0:
                months_covered = value / (monthly_cons * value / shelf_life if shelf_life > 0 else 1)
                stock_coverage = value / (monthly_cons * (value / 12))  # 近似计算
                stock_coverage_months = (value / max(monthly_cons, 1)) if monthly_cons > 0 else float("inf")
            else:
                stock_coverage_months = float("inf")

            # 效期风险
            if cat.startswith("A_"):
                if stock_coverage_months > shelf_life * 0.5:
                    expiry_risk = "🔴 高风险（库存超过效期50%）"
                    total_expiry_risk += value * 0.10  # 假设10%面临报废
                elif stock_coverage_months > shelf_life * 0.33:
                    expiry_risk = "🟡 中等风险（库存超过效期33%）"
                    total_expiry_risk += value * 0.03
                else:
                    expiry_risk = "🟢 低风险"
            else:
                expiry_risk = "N/A（常规效期）"

            # 管理建议
            if cat.startswith("A_"):
                advice = "少批量多频次采购，目标库存<效期的40%。启用效期预警（到期前6月/3月/1月三级预警）"
            elif cat.startswith("B_"):
                advice = "按销售预测备货，安全库存=2-4周销量。定期盘点，关注近效期（<6个月）品种"
            else:
                advice = "批量采购以降低单价，定期审核供应商资质。关注包材变更对GMP的影响"

            classified.append({
                "产品名称": p["name"],
                "分类": cat.replace("A_", "").replace("B_", "").replace("C_", ""),
                "库存价值（万元）": round(value / 10000, 0),
                "效期（月）": f"{shelf_life:.0f}",
                "库存覆盖（月）": f"{stock_coverage_months:.1f}" if stock_coverage_months != float("inf") else "∞",
                "效期风险": expiry_risk,
                "管理建议": advice,
            })

        # GMP合规要求
        gmp_requirements = [
            "✅ 留样管理：每批至少保留检验量的2倍，留样至有效期后1年",
            "✅ 温湿度监控：冷链品种须24小时温度记录，偏差>2°C启动偏差调查",
            "✅ 供应商资质：辅料/包材供应商变更须重新评估和验证",
            "✅ 不合格品隔离：物理隔离+标识+QA审批销毁",
        ]
        if input_data.temperature_excursion_risk in ("medium", "high"):
            gmp_requirements.append(
                "⚠️ 冷链品种温度偏移风险较高，建议增加备用制冷设备和断电应急预案"
            )

        return {
            "公司名称": input_data.company_name,
            "库存总价值（万元）": round(total_value / 10000, 0),
            "预计效期报废风险（万元）": round(total_expiry_risk / 10000, 0),
            "报废风险率": f"{total_expiry_risk / total_value:.1%}" if total_value > 0 else "0%",
            "产品分类管理": classified,
            "GMP合规要求": gmp_requirements,
        }

    # -------------------------------------------------------------------------
    # 4. 医院/经销商信用评级模型
    # -------------------------------------------------------------------------

    def hospital_credit_rating(self, input_data: HospitalCreditInput) -> Dict:
        """
        医院/经销商信用评级（两票制约束版）

        评级维度：
        - 医院等级（20%）
        - 回款历史（30%）
        - 医保结算周期（25%）
        - 区域经济水平（15%）
        - 历史坏账率（10%）
        """
        customers = input_data.customers
        rated = []

        for c in customers:
            # 评分
            scores = {}

            # 1. 医院等级评分
            grade = c["grade"]
            if isinstance(grade, str):
                grade = HospitalGrade(grade)
            grade_scores = {
                HospitalGrade.GRADE_3A: 5,
                HospitalGrade.GRADE_3B: 4,
                HospitalGrade.GRADE_2A: 3,
                HospitalGrade.GRADE_2B: 2,
                HospitalGrade.GRADE_1: 1,
                HospitalGrade.COMMUNITY: 0.5,
            }
            scores["医院等级"] = grade_scores.get(grade, 1) * 0.20

            # 2. 回款历史评分
            payment = c.get("payment_history", "on_time")
            payment_scores = {
                "on_time": 5,
                "late_1_3_months": 3,
                "late_3_6_months": 1,
                "late_6_plus_months": 0,
            }
            scores["回款历史"] = payment_scores.get(payment, 2) * 0.30

            # 3. 医保结算周期
            insurance_cycle = c.get("insurance_settlement_cycle_months", 6)
            if insurance_cycle <= 3:
                insurance_score = 5
            elif insurance_cycle <= 6:
                insurance_score = 3
            else:
                insurance_score = 1
            scores["医保结算"] = insurance_score * 0.25

            # 4. 区域经济
            gdp_rank = c.get("province_gdp_rank", 15)
            if gdp_rank <= 5:
                econ_score = 5
            elif gdp_rank <= 15:
                econ_score = 3
            else:
                econ_score = 1
            scores["区域经济"] = econ_score * 0.15

            # 5. 历史坏账率
            bad_debt = c.get("historical_bad_debt_rate", 0)
            if bad_debt == 0:
                bad_score = 5
            elif bad_debt < 0.01:
                bad_score = 4
            elif bad_debt < 0.03:
                bad_score = 2
            else:
                bad_score = 0
            scores["坏账率"] = bad_score * 0.10

            total_score = sum(scores.values())

            # 授信策略
            if total_score >= 4.0:
                credit_strategy = "✅ 优质客户：账期90天，额度不限"
                credit_days = 90
            elif total_score >= 3.0:
                credit_strategy = "✅ 良好客户：账期60天，额度=月采购额×1.5"
                credit_days = 60
            elif total_score >= 2.0:
                credit_strategy = "⚠️ 一般客户：账期30天，额度=月采购额×1.0"
                credit_days = 30
            else:
                credit_strategy = "❌ 高风险客户：款到发货，不设账期"
                credit_days = 0

            rated.append({
                "客户名称": c["name"],
                "医院等级": grade.value if hasattr(grade, 'value') else grade,
                "综合评分": f"{total_score:.1f}/5.0",
                "评分明细": {k: f"{v:.2f}" for k, v in scores.items()},
                "年采购额（万元）": round(c.get("annual_purchase", 0) / 10000, 0),
                "授信策略": credit_strategy,
                "建议账期": f"{credit_days}天",
            })

        # 汇总
        avg_score = sum(float(r["综合评分"].split("/")[0]) for r in rated) / len(rated) if rated else 0

        return {
            "药物类型": input_data.drug_type,
            "客户评级结果": rated,
            "客户数": len(rated),
            "平均信用评分": f"{avg_score:.1f}/5.0",
            "高信用客户占比": f"{sum(1 for r in rated if float(r['综合评分'].split('/')[0]) >= 4.0) / len(rated):.0%}" if rated else "0%",
            "关键提示": "两票制下，医院回款周期取决于医保局拨款节奏，而非医院自身意愿。评级为'一般'的客户中，相当部分是因为所在省份医保结算周期长。",
        }

    # -------------------------------------------------------------------------
    # 5. Phase-Gate现金流滚动预算模型
    # -------------------------------------------------------------------------

    def phase_gate_budget(self, input_data: PhaseGateBudgetInput) -> Dict:
        """
        药物开发Phase-Gate滚动现金流预算

        按临床阶段编制，每个Gate触发Go/No-Go决策
        """
        drug = input_data.drug_name
        current_phase = input_data.current_phase.value

        # 构建完整开发时间线
        timeline = []
        cumulative_cost = 0
        current_month = 0
        phase_order = ["preclinical", "phase_i", "phase_ii", "phase_iii", "nda"]

        # 找到当前阶段的起始索引
        try:
            start_idx = phase_order.index(current_phase)
        except ValueError:
            start_idx = len(phase_order)

        for phase_data in input_data.phases:
            phase = phase_data["phase"]
            duration = phase_data["duration_months"]
            monthly_cost = phase_data["monthly_cost"]
            one_time_costs = phase_data.get("one_time_costs", [])

            # 构建一次性成本的时间表
            one_time_schedule = {}
            for otc in one_time_costs:
                one_time_schedule[otc["month"]] = one_time_schedule.get(otc["month"], 0) + otc["amount"]

            for m in range(duration):
                current_month += 1
                monthly_total = monthly_cost + one_time_schedule.get(m + 1, 0)
                cumulative_cost += monthly_total

                is_gate = (m == duration - 1)  # 每个阶段的最后一个月是Gate

                timeline.append({
                    "月": current_month,
                    "阶段": phase,
                    "当月支出（万元）": round(monthly_total / 10000, 0),
                    "累计支出（万元）": round(cumulative_cost / 10000, 0),
                    "Gate": "🚪 Go/No-Go决策点" if is_gate else "",
                })

        # 现金预测
        cash = input_data.current_cash
        monthly_net_outflow = 0
        cash_warning_months = []
        lowest_cash = cash

        for entry in timeline:
            monthly_outflow = float(entry["当月支出（万元）"]) * 10000
            cash = cash - monthly_outflow + input_data.monthly_revenue
            if cash < lowest_cash:
                lowest_cash = cash

            if cash < 0:
                cash_warning_months.append({
                    "月份": entry["月"],
                    "阶段": entry["阶段"],
                    "资金缺口（万元）": round(abs(cash) / 10000, 0),
                })

        # 预警
        if cash < 0:
            shortage_month = cash_warning_months[0]["月份"] if cash_warning_months else "N/A"
            warning = f"🔴 资金将在第{shortage_month}个月耗尽！需提前{input_data.current_cash / (monthly_outflow or 1) / 12:.1f}年启动融资"
        else:
            runway_months = input_data.current_cash / (monthly_outflow or 1) if monthly_outflow > 0 else float("inf")
            if runway_months == float("inf"):
                warning = "🟢 资金充足（无净流出）"
            elif runway_months > 36:
                warning = f"🟢 资金可覆盖{runway_months:.0f}个月，远超开发周期"
            elif runway_months > 24:
                warning = f"🟡 资金可覆盖{runway_months:.0f}个月，建议在18个月左右启动融资准备"
            elif runway_months > 12:
                warning = f"🟠 资金可覆盖{runway_months:.0f}个月，建议立即启动融资或BD"
            else:
                warning = f"🔴 资金仅可覆盖{runway_months:.0f}个月，紧急启动融资或缩减管线"

        return {
            "药物名称": drug,
            "当前阶段": current_phase,
            "开发总月数": current_month,
            "总开发成本（万元）": round(cumulative_cost / 10000, 0),
            "当前现金（万元）": round(input_data.current_cash / 10000, 0),
            "月度产品收入（万元）": round(input_data.monthly_revenue / 10000, 0),
            "最低现金点（万元）": round(lowest_cash / 10000, 0),
            "资金预警": warning,
            "资金缺口详情": cash_warning_months if cash_warning_months else "无缺口",
            "开发时间线（前12个月）": timeline[:12],
            "总月份数": current_month,
        }


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  制药资金管理模型（Pharma Cash Models）测试")
    print("=" * 70)

    pcm = PharmaCashModels()

    # 测试1：药品库存与回款周转
    print("\n【测试1】药品现金周转周期")
    print("-" * 50)
    inventory_input = DrugInventoryInput(
        company_name="XX生物制药",
        api_inventory_days=90,
        production_cycle_days=45,
        finished_goods_days=60,
        hospital_receivables_days=270,  # 9个月（两票制下典型周期）
        supplier_payables_days=45,
        is_biologic=True,
        cold_chain_shelf_life_months=18,
    )
    print(json.dumps(pcm.drug_cash_conversion_cycle(inventory_input), ensure_ascii=False, indent=2))

    # 测试2：研发现金储备
    print("\n【测试2】研发现金储备")
    print("-" * 50)
    reserve_input = RDCashReserveInput(
        company_name="XX Biotech",
        monthly_burn_rate=20_000_000,
        next_milestone_payment=50_000_000,
        months_to_milestone=9,
        n_active_clinical_programs=2,
        clinical_phase=DevelopmentPhase.PHASE_II,
    )
    print(json.dumps(pcm.rd_cash_reserve(reserve_input), ensure_ascii=False, indent=2))

    # 测试3：GMP库存管理
    print("\n【测试3】GMP库存管理")
    print("-" * 50)
    gmp_input = GMPInventoryInput(
        company_name="XX制药",
        products=[
            {"name": "PD-1单抗（冷链）", "category": "A_冷链生物药",
             "value": 50_000_000, "shelf_life_months": 18, "monthly_consumption": 3_000_000},
            {"name": "阿托伐他汀", "category": "B_常规化学药",
             "value": 20_000_000, "shelf_life_months": 36, "monthly_consumption": 2_000_000},
            {"name": "注射用辅料", "category": "C_辅料包材",
             "value": 5_000_000, "shelf_life_months": 24, "monthly_consumption": 400_000},
        ],
        temperature_excursion_risk="medium",
    )
    print(json.dumps(pcm.gmp_inventory_management(gmp_input), ensure_ascii=False, indent=2))

    # 测试4：医院信用评级
    print("\n【测试4】医院信用评级")
    print("-" * 50)
    credit_input = HospitalCreditInput(
        customers=[
            {"name": "北京协和医院", "grade": HospitalGrade.GRADE_3A,
             "payment_history": "on_time", "annual_purchase": 50_000_000,
             "province_gdp_rank": 1, "insurance_settlement_cycle_months": 3},
            {"name": "XX省人民医院", "grade": HospitalGrade.GRADE_3A,
             "payment_history": "late_1_3_months", "annual_purchase": 30_000_000,
             "province_gdp_rank": 10, "insurance_settlement_cycle_months": 6},
            {"name": "XX县级医院", "grade": HospitalGrade.GRADE_2A,
             "payment_history": "late_3_6_months", "annual_purchase": 10_000_000,
             "province_gdp_rank": 22, "insurance_settlement_cycle_months": 12},
        ],
        drug_type="innovative",
    )
    print(json.dumps(pcm.hospital_credit_rating(credit_input), ensure_ascii=False, indent=2))

    # 测试5：Phase-Gate预算
    print("\n【测试5】Phase-Gate预算")
    print("-" * 50)
    phase_input = PhaseGateBudgetInput(
        drug_name="XX-001（PD-L1单抗）",
        current_phase=DevelopmentPhase.PHASE_II,
        phases=[
            {"phase": "phase_ii", "duration_months": 18, "monthly_cost": 8_000_000,
             "one_time_costs": [{"item": "期中分析", "amount": 5_000_000, "month": 12}]},
            {"phase": "phase_iii", "duration_months": 30, "monthly_cost": 15_000_000,
             "one_time_costs": [{"item": "III期启动费", "amount": 20_000_000, "month": 1},
                              {"item": "期中分析", "amount": 10_000_000, "month": 18}]},
            {"phase": "nda", "duration_months": 12, "monthly_cost": 3_000_000,
             "one_time_costs": [{"item": "NDA申报费", "amount": 5_000_000, "month": 1}]},
        ],
        current_cash=300_000_000,
        monthly_revenue=2_000_000,
    )
    result = pcm.phase_gate_budget(phase_input)
    # 只输出摘要
    summary = {k: v for k, v in result.items() if k != "开发时间线（前12个月）"}
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    print("\n" + "=" * 70)
    print("  所有测试完成！")
    print("=" * 70)
