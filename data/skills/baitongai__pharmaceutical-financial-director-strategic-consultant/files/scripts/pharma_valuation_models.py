#!/usr/bin/env python3
"""
医药估值模型（Pharma Valuation Models）
=======================================
包含4个医药行业专用估值模型：
1. rNPV管线估值模型（风险调整净现值）
2. 可比药物分析法（同靶点/同适应症对标）
3. 成熟产品销售折现模型
4. 峰值销售估计模型（患者流模型）

基于 Finance Director Enhanced v4.0.0 框架改造
原 DCF → rNPV, 可比公司 → 可比药物, DDM → 成熟产品销售折现, 剩余收益 → 峰值销售
"""

import math
import json
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# 数据类型定义
# =============================================================================

class ClinicalPhase(Enum):
    """临床阶段枚举"""
    PRECLINICAL = "preclinical"
    PHASE_I = "phase_i"
    PHASE_II = "phase_ii"
    PHASE_III = "phase_iii"
    NDA = "nda"
    APPROVED = "approved"
    LAUNCHED = "launched"


class TherapeuticArea(Enum):
    """治疗领域枚举"""
    ONCOLOGY = "oncology"
    CARDIOVASCULAR = "cardiovascular"
    CNS = "cns"
    IMMUNOLOGY = "immunology"
    INFECTIOUS = "infectious"
    METABOLIC = "metabolic"
    RARE_DISEASE = "rare_disease"
    RESPIRATORY = "respiratory"
    OTHER = "other"


# 各治疗领域各阶段成功率参考（来源：Nature Reviews Drug Discovery 2025）
# 格式：{TherapeuticArea: {ClinicalPhase: success_probability}}
CLINICAL_SUCCESS_RATES = {
    TherapeuticArea.ONCOLOGY: {
        ClinicalPhase.PHASE_I: 0.62,
        ClinicalPhase.PHASE_II: 0.35,
        ClinicalPhase.PHASE_III: 0.52,
        ClinicalPhase.NDA: 0.87,
    },
    TherapeuticArea.CARDIOVASCULAR: {
        ClinicalPhase.PHASE_I: 0.65,
        ClinicalPhase.PHASE_II: 0.42,
        ClinicalPhase.PHASE_III: 0.58,
        ClinicalPhase.NDA: 0.89,
    },
    TherapeuticArea.CNS: {
        ClinicalPhase.PHASE_I: 0.58,
        ClinicalPhase.PHASE_II: 0.30,
        ClinicalPhase.PHASE_III: 0.48,
        ClinicalPhase.NDA: 0.85,
    },
    TherapeuticArea.IMMUNOLOGY: {
        ClinicalPhase.PHASE_I: 0.68,
        ClinicalPhase.PHASE_II: 0.45,
        ClinicalPhase.PHASE_III: 0.62,
        ClinicalPhase.NDA: 0.90,
    },
    TherapeuticArea.INFECTIOUS: {
        ClinicalPhase.PHASE_I: 0.70,
        ClinicalPhase.PHASE_II: 0.48,
        ClinicalPhase.PHASE_III: 0.65,
        ClinicalPhase.NDA: 0.92,
    },
    TherapeuticArea.METABOLIC: {
        ClinicalPhase.PHASE_I: 0.66,
        ClinicalPhase.PHASE_II: 0.44,
        ClinicalPhase.PHASE_III: 0.60,
        ClinicalPhase.NDA: 0.89,
    },
    TherapeuticArea.RARE_DISEASE: {
        ClinicalPhase.PHASE_I: 0.72,
        ClinicalPhase.PHASE_II: 0.50,
        ClinicalPhase.PHASE_III: 0.68,
        ClinicalPhase.NDA: 0.93,
    },
}

# 默认折现率（按阶段）
DEFAULT_DISCOUNT_RATES = {
    ClinicalPhase.PRECLINICAL: 0.18,
    ClinicalPhase.PHASE_I: 0.16,
    ClinicalPhase.PHASE_II: 0.14,
    ClinicalPhase.PHASE_III: 0.12,
    ClinicalPhase.NDA: 0.10,
    ClinicalPhase.APPROVED: 0.09,
    ClinicalPhase.LAUNCHED: 0.08,
}

# 默认各阶段持续年数
DEFAULT_PHASE_DURATIONS = {
    ClinicalPhase.PRECLINICAL: 2.5,
    ClinicalPhase.PHASE_I: 1.5,
    ClinicalPhase.PHASE_II: 2.0,
    ClinicalPhase.PHASE_III: 3.0,
    ClinicalPhase.NDA: 1.0,
}


@dataclass
class RnpvInput:
    """rNPV估值输入参数"""
    drug_name: str
    current_phase: ClinicalPhase
    therapeutic_area: TherapeuticArea
    years_to_launch: float  # 从当前阶段到上市的年数
    peak_sales_cny: float  # 峰值年销售额（人民币元）

    # 时间参数（可选）
    commercial_years: int = 15  # 商业化的总年数（到专利到期）

    # 销售参数（可选）
    ramp_up_years: int = 4  # 从上市到峰值的年数
    peak_years: int = 5  # 维持峰值的年数

    # 成本参数（可选）
    launch_costs_cny: float = 0  # 上市准备成本
    annual_commercial_costs_cny: float = 0  # 年度商业化成本

    # 折现率（可选，不提供则使用默认）
    discount_rate: Optional[float] = None

    # 成功率（可选，不提供则根据治疗领域查表）
    custom_success_rates: Optional[Dict[ClinicalPhase, float]] = None

    # 专利到期后仿制药侵蚀
    generic_erosion_rate: float = 0.80  # 专利到期后销售额保留比例（即损失80%）


@dataclass
class RnpvOutput:
    """rNPV估值输出结果"""
    drug_name: str
    current_phase: str
    therapeutic_area: str

    # 成功率
    cumulative_success_prob: float  # 从当前阶段到获批的累积成功率
    phase_success_rates: Dict[str, float]  # 各阶段成功率

    # 估值结果
    unadjusted_npv: float  # 未调整的NPV（假设100%成功）
    rnpv: float  # 风险调整后的NPV
    rnpv_million_cny: float  # rNPV（百万人民币）

    # 分解
    commercial_value: float  # 商业化阶段的价值（上市后）
    development_costs: float  # 到上市前的开发成本

    # 峰值销售相关
    peak_sales_cny: float
    year_to_peak: int  # 到达峰值销售的年份

    # 解读
    interpretation: str
    risk_level: str  # "low", "medium", "high", "very_high"

    def to_dict(self) -> Dict:
        return {
            "药物名称": self.drug_name,
            "当前阶段": self.current_phase,
            "治疗领域": self.therapeutic_area,
            "累积成功率": f"{self.cumulative_success_prob:.1%}",
            "各阶段成功率": self.phase_success_rates,
            "风险调整前NPV（万元）": round(self.unadjusted_npv / 10000, 0),
            "风险调整后rNPV（万元）": round(self.rnpv / 10000, 0),
            "峰值销售额（万元）": round(self.peak_sales_cny / 10000, 0),
            "到达峰值年份": f"上市后第{self.year_to_peak}年",
            "风险等级": self.risk_level,
            "解读": self.interpretation,
        }


@dataclass
class PeakSalesInput:
    """峰值销售估计输入"""
    drug_name: str
    indication: str

    # 流行病学参数
    target_population: int  # 目标总人口
    incidence_rate: float  # 发病率（每10万人）
    prevalence_rate: Optional[float] = None  # 患病率（慢性病适用）

    # 治疗漏斗
    diagnosis_rate: float = 0.60  # 诊断率
    treatment_rate: float = 0.70  # 治疗率
    target_market_share: float = 0.20  # 目标市场份额

    # 定价
    annual_treatment_cost_cny: float = 0  # 年治疗费用

    # 竞争
    competitor_share: float = 0.50  # 已上市竞品市场份额
    years_to_peak: int = 5  # 到峰值销售的年数

    # 可选：直接给定患者数
    target_patients: Optional[int] = None


@dataclass
class PeakSalesOutput:
    """峰值销售估计输出"""
    drug_name: str
    indication: str

    # 患者流
    total_patients: int  # 总患者数
    diagnosed_patients: int  # 已诊断患者数
    treated_patients: int  # 接受治疗的患者数
    addressable_patients: int  # 可寻址患者数
    target_patients: int  # 目标患者数

    # 销售
    peak_sales_cny: float  # 峰值年销售额
    peak_sales_million_cny: float  # 峰值年销售额（百万元）

    # 竞争分析
    remaining_market_size: float  # 除去竞品后的市场规模

    def to_dict(self) -> Dict:
        return {
            "药物名称": self.drug_name,
            "适应症": self.indication,
            "总患者数": f"{self.total_patients:,}",
            "已诊断患者数": f"{self.diagnosed_patients:,}",
            "接受治疗患者数": f"{self.treated_patients:,}",
            "可寻址患者数": f"{self.addressable_patients:,}",
            "目标患者数": f"{self.target_patients:,}",
            "峰值年销售额（万元）": round(self.peak_sales_cny / 10000, 0),
            "剩余市场规模（百万元）": round(self.remaining_market_size / 1000000, 1),
        }


@dataclass
class BDDealInput:
    """BD交易分析输入"""
    drug_name: str
    deal_type: str  # "license-in" or "license-out"

    # 交易条款
    upfront_cny: float  # 首付款
    milestones: List[Dict]  # [{"stage": str, "amount": float, "prob": float}]
    royalty_rate: float  # 分成比例（小数，如0.12表示12%）

    # 销售预测
    peak_sales_cny: float

    # 以下为可选参数
    royalty_rate_tiers: Optional[List[Dict]] = None  # 分级分成率
    ramp_up_years: int = 4
    commercial_years: int = 12

    # 估值参数
    discount_rate: float = 0.12

    # 成本
    development_costs_cny: float = 0  # 买方的后续开发成本
    commercialization_costs_cny: float = 0  # 商业化成本


@dataclass
class BDDealOutput:
    """BD交易分析输出"""
    drug_name: str
    deal_type: str

    # 对价分解
    upfront_value: float  # 首付款现值
    expected_milestones_value: float  # 期望里程碑付款现值
    expected_royalties_value: float  # 期望分成现值
    total_deal_value: float  # 交易总对价NPV

    # 卖方/买方视角
    seller_proceeds: float  # 卖方实收（不含买方后续成本）
    buyer_net_value: float  # 买方净价值（总药品价值-总对价-买方成本）

    # 倍数
    upfront_to_peak_sales: float  # 首付款/峰值销售倍数
    total_to_peak_sales: float  # 总对价/峰值销售倍数

    # 建议
    fair_value_range: Tuple[float, float]  # 公允对价区间
    recommendation: str

    def to_dict(self) -> Dict:
        return {
            "药物名称": self.drug_name,
            "交易类型": "引进（License-in）" if self.deal_type == "license-in" else "对外授权（License-out）",
            "首付款（万元）": round(self.upfront_value / 10000, 0),
            "期望里程碑（万元）": round(self.expected_milestones_value / 10000, 0),
            "期望分成现值（万元）": round(self.expected_royalties_value / 10000, 0),
            "交易总对价NPV（万元）": round(self.total_deal_value / 10000, 0),
            "卖出方实收（万元）": round(self.seller_proceeds / 10000, 0),
            "买入方净价值（万元）": round(self.buyer_net_value / 10000, 0),
            "首付款/峰值销售倍数": f"{self.upfront_to_peak_sales:.2f}x",
            "总对价/峰值销售倍数": f"{self.total_to_peak_sales:.2f}x",
            "公允对价区间（万元）": f"{round(self.fair_value_range[0]/10000, 0)} ~ {round(self.fair_value_range[1]/10000, 0)}",
            "建议": self.recommendation,
        }


@dataclass
class MatureProductInput:
    """成熟产品销售折现输入"""
    drug_name: str
    generic_name: str
    current_annual_sales_cny: float  # 当前年销售额
    years_to_patent_expiry: int  # 到专利到期的年数
    post_patent_years: int = 5  # 专利到期后分析年数

    # 侵蚀参数
    generic_erosion_schedule: Optional[List[float]] = None  # 逐年侵蚀率（0-1）
    vbp_discount_impact: float = 0  # 集采额外降价影响（百分比）

    discount_rate: float = 0.10

    # 增长
    pre_expiry_growth_rate: float = 0.05  # 专利期内年增长率


# =============================================================================
# 核心估值模型
# =============================================================================

class PharmaValuationModels:
    """医药估值模型主类"""

    def __init__(self, discount_rate: float = 0.12):
        """
        初始化估值模型

        Args:
            discount_rate: 默认折现率
        """
        self.discount_rate = discount_rate

    # -------------------------------------------------------------------------
    # 1. rNPV管线估值模型
    # -------------------------------------------------------------------------

    def rnpv_valuation(self, input_data: RnpvInput) -> RnpvOutput:
        """
        风险调整净现值（rNPV）管线估值

        核心公式：
        rNPV = 累积成功率 × 商业化NPV - 到上市前的开发成本
        """
        drug = input_data.drug_name
        phase = input_data.current_phase

        # 1.1 获取成功率
        if input_data.custom_success_rates:
            success_rates = input_data.custom_success_rates
        else:
            success_rates = CLINICAL_SUCCESS_RATES.get(
                input_data.therapeutic_area,
                CLINICAL_SUCCESS_RATES[TherapeuticArea.ONCOLOGY]
            )

        # 1.2 计算从当前阶段到获批的累积成功率
        phase_order = [
            ClinicalPhase.PRECLINICAL, ClinicalPhase.PHASE_I,
            ClinicalPhase.PHASE_II, ClinicalPhase.PHASE_III, ClinicalPhase.NDA
        ]
        try:
            current_idx = phase_order.index(phase)
        except ValueError:
            current_idx = len(phase_order)  # 已获批

        cumulative_success = 1.0
        phase_details = {}
        for i in range(current_idx, len(phase_order)):
            p = phase_order[i]
            if p in success_rates:
                rate = success_rates[p]
                cumulative_success *= rate
                phase_details[p.value] = {
                    "成功率": f"{rate:.1%}",
                    "阶段说明": self._get_phase_description(p)
                }

        # 1.3 确定折现率
        if input_data.discount_rate:
            discount_rate = input_data.discount_rate
        else:
            discount_rate = DEFAULT_DISCOUNT_RATES.get(phase, 0.12)

        # 1.4 计算商业化阶段的现金流（上市后）
        commercial_npv = self._calculate_commercial_cashflows(
            peak_sales=input_data.peak_sales_cny,
            ramp_up_years=input_data.ramp_up_years,
            peak_years=input_data.peak_years,
            commercial_years=input_data.commercial_years,
            launch_costs=input_data.launch_costs_cny,
            annual_commercial_costs=input_data.annual_commercial_costs_cny,
            discount_rate=discount_rate,
            generic_erosion_rate=input_data.generic_erosion_rate,
            years_to_launch=input_data.years_to_launch,
        )

        # 1.5 开发成本（到上市前）
        development_costs = self._estimate_development_costs(phase)

        # 1.6 计算rNPV
        unadjusted_npv = commercial_npv - development_costs
        rnpv = cumulative_success * commercial_npv - development_costs

        # 1.7 风险等级判断
        risk_level = self._assess_risk_level(cumulative_success)

        # 1.8 解读
        interpretation = self._generate_rnpv_interpretation(
            drug, phase, cumulative_success, rnpv, unadjusted_npv
        )

        return RnpvOutput(
            drug_name=drug,
            current_phase=phase.value,
            therapeutic_area=input_data.therapeutic_area.value,
            cumulative_success_prob=cumulative_success,
            phase_success_rates=phase_details,
            unadjusted_npv=unadjusted_npv,
            rnpv=rnpv,
            rnpv_million_cny=rnpv / 1000000,
            commercial_value=commercial_npv,
            development_costs=development_costs,
            peak_sales_cny=input_data.peak_sales_cny,
            year_to_peak=input_data.ramp_up_years,
            interpretation=interpretation,
            risk_level=risk_level,
        )

    def _calculate_commercial_cashflows(
        self,
        peak_sales: float,
        ramp_up_years: int,
        peak_years: int,
        commercial_years: int,
        launch_costs: float,
        annual_commercial_costs: float,
        discount_rate: float,
        generic_erosion_rate: float,
        years_to_launch: float,
    ) -> float:
        """计算商业化阶段的现金流现值"""
        npv = -launch_costs / ((1 + discount_rate) ** years_to_launch)

        for year in range(1, commercial_years + 1):
            t = years_to_launch + year

            # 销售曲线：爬坡期 → 平台期 → 下降期（专利到期后）
            if year <= ramp_up_years:
                # 线性爬坡
                sales = peak_sales * (year / ramp_up_years)
            elif year <= ramp_up_years + peak_years:
                sales = peak_sales
            else:
                # 专利到期后的侵蚀
                years_post_peak = year - ramp_up_years - peak_years
                erosion = min(0.85, years_post_peak * 0.20)  # 每年侵蚀20%，最多85%
                sales = peak_sales * (1 - erosion)

            # 净利润简化为销售额的25%（扣除COGS、SGA、税费后的典型净利率）
            net_profit = sales * 0.25

            # 扣除商业化成本
            net_cashflow = net_profit - annual_commercial_costs
            present_value = net_cashflow / ((1 + discount_rate) ** t)
            npv += present_value

        return npv

    def _estimate_development_costs(self, phase: ClinicalPhase) -> float:
        """估算到上市前的开发成本（人民币元）"""
        cost_estimates = {
            ClinicalPhase.PRECLINICAL: 500000000,  # 5亿
            ClinicalPhase.PHASE_I: 350000000,       # 3.5亿
            ClinicalPhase.PHASE_II: 200000000,      # 2亿
            ClinicalPhase.PHASE_III: 50000000,      # 0.5亿（仅NDA费用）
            ClinicalPhase.NDA: 10000000,            # 0.1亿
        }
        return cost_estimates.get(phase, 0)

    def _assess_risk_level(self, cumulative_success: float) -> str:
        """评估风险等级"""
        if cumulative_success >= 0.70:
            return "低"
        elif cumulative_success >= 0.40:
            return "中等"
        elif cumulative_success >= 0.15:
            return "高"
        else:
            return "极高"

    def _get_phase_description(self, phase: ClinicalPhase) -> str:
        """获取阶段说明"""
        descriptions = {
            ClinicalPhase.PRECLINICAL: "临床前研究（药效、药代、毒理）",
            ClinicalPhase.PHASE_I: "临床I期（安全性和耐受性，20-80人）",
            ClinicalPhase.PHASE_II: "临床II期（初步疗效和剂量探索，100-300人）",
            ClinicalPhase.PHASE_III: "临床III期（确证性试验，300-3000+人）",
            ClinicalPhase.NDA: "新药上市申请审评",
        }
        return descriptions.get(phase, "")

    def _generate_rnpv_interpretation(
        self,
        drug: str,
        phase: ClinicalPhase,
        cum_prob: float,
        rnpv: float,
        unadjusted_npv: float,
    ) -> str:
        """生成rNPV估值解读"""
        rnpv_m = rnpv / 1000000

        if rnpv > 0:
            if cum_prob >= 0.40:
                return (
                    f"{drug}当前处于{phase.value}阶段，"
                    f"累积成功率{cum_prob:.1%}，"
                    f"风险调整后估值约{rnpv_m:.0f}百万元人民币。"
                    f"该管线估值合理，建议继续推进。"
                )
            else:
                return (
                    f"{drug}当前处于{phase.value}阶段，"
                    f"累积成功率仅{cum_prob:.1%}（风险较高），"
                    f"风险调整后估值约{rnpv_m:.0f}百万元。"
                    f"虽然rNPV为正，但需密切关注临床数据读出。"
                )
        else:
            return (
                f"{drug}当前处于{phase.value}阶段，"
                f"累积成功率{cum_prob:.1%}，"
                f"风险调整后rNPV为负（{rnpv_m:.0f}百万元）。"
                f"从纯财务角度，该管线当前估值不支持继续投入，"
                f"建议评估是否调整策略或寻找合作伙伴分担风险。"
            )

    # -------------------------------------------------------------------------
    # 2. 峰值销售估计模型（患者流模型）
    # -------------------------------------------------------------------------

    def peak_sales_estimation(self, input_data: PeakSalesInput) -> PeakSalesOutput:
        """
        峰值销售估计 — 患者流模型

        核心逻辑：
        目标总人口 × 发病率 → 总患者数
        → × 诊断率 → 已诊断患者
        → × 治疗率 → 治疗患者
        → × (1-竞品份额) → 可寻址患者
        → × 目标市场份额 → 目标患者
        → × 年治疗费用 → 峰值年销售额
        """
        drug = input_data.drug_name
        indication = input_data.indication

        # 2.1 总患者数
        if input_data.prevalence_rate:
            # 慢性病：使用患病率
            total_patients = int(input_data.target_population * input_data.prevalence_rate)
        else:
            # 急性病/肿瘤：使用发病率
            total_patients = int(input_data.target_population * input_data.incidence_rate / 100000)

        # 2.2 治疗漏斗
        diagnosed = int(total_patients * input_data.diagnosis_rate)
        treated = int(diagnosed * input_data.treatment_rate)
        addressable = int(treated * (1 - input_data.competitor_share))
        target = int(addressable * input_data.target_market_share)

        # 2.3 峰值销售（竞争后）
        peak_sales = target * input_data.annual_treatment_cost_cny

        # 2.4 剩余市场规模
        remaining_market = treated * input_data.annual_treatment_cost_cny

        return PeakSalesOutput(
            drug_name=drug,
            indication=indication,
            total_patients=total_patients,
            diagnosed_patients=diagnosed,
            treated_patients=treated,
            addressable_patients=addressable,
            target_patients=target,
            peak_sales_cny=peak_sales,
            peak_sales_million_cny=peak_sales / 1000000,
            remaining_market_size=remaining_market,
        )

    # -------------------------------------------------------------------------
    # 3. BD交易分析模型
    # -------------------------------------------------------------------------

    def bd_deal_analysis(self, input_data: BDDealInput) -> BDDealOutput:
        """
        BD交易分析（License-in/License-out）

        分析交易结构，计算买卖双方的净值
        """
        drug = input_data.drug_name
        rate = input_data.discount_rate

        # 3.1 首付款现值
        upfront_pv = input_data.upfront_cny  # 首付通常在签约时支付，不做折现

        # 3.2 里程碑付款期望现值
        total_milestone_pv = 0
        for i, ms in enumerate(input_data.milestones):
            prob = ms.get("prob", 1.0)
            amount = ms["amount"]
            # 假设里程碑发生在各阶段结束时间点
            # 按阶段粗略估算：Phase III start ≈ 2年后, NDA ≈ 5年后
            stage_years = {"preclinical": 2.5, "phase_1": 1.5, "phase_2": 3.0,
                          "phase_3": 5.0, "nda": 6.0, "approval": 7.0}
            t = stage_years.get(ms.get("stage", "").lower().replace(" ", "_"), 3.0)
            expected_amount = amount * prob
            pv = expected_amount / ((1 + rate) ** t)
            total_milestone_pv += pv

        # 3.3 销售分成期望现值
        total_royalty_pv = 0
        for year in range(1, input_data.commercial_years + 1):
            # 销售曲线
            if year <= input_data.ramp_up_years:
                sales = input_data.peak_sales_cny * (year / input_data.ramp_up_years)
            else:
                # 平台期后每年递减
                years_post_peak = year - input_data.ramp_up_years
                decay = min(0.5, years_post_peak * 0.08)
                sales = input_data.peak_sales_cny * (1 - decay)

            # 分级分成
            if input_data.royalty_rate_tiers:
                royalty = self._calculate_tiered_royalty(sales, input_data.royalty_rate_tiers)
            else:
                royalty = sales * input_data.royalty_rate

            pv = royalty / ((1 + rate) ** (year + 0.5))  # +0.5 年中折现
            total_royalty_pv += pv

        # 3.4 总对价
        total_deal_value = upfront_pv + total_milestone_pv + total_royalty_pv

        # 3.5 买方净价值
        # 买方：投入=对价+后续开发成本+商业化成本，产出=药物商业化价值
        drug_commercial_value = sum(
            input_data.peak_sales_cny * (1 - max(0, (year - input_data.ramp_up_years) * 0.08))
            * 0.25 / ((1 + rate) ** (year + 0.5))
            for year in range(1, input_data.commercial_years + 1)
        )
        buyer_net = drug_commercial_value - total_deal_value - input_data.development_costs_cny - input_data.commercialization_costs_cny

        # 卖方实收
        seller_proceeds = total_deal_value

        # 3.6 倍数
        upfront_multiple = input_data.upfront_cny / input_data.peak_sales_cny
        total_multiple = total_deal_value / input_data.peak_sales_cny

        # 3.7 公允对价区间和推荐
        fair_low = input_data.peak_sales_cny * 0.25  # 峰值销售的25%
        fair_high = input_data.peak_sales_cny * 0.50  # 峰值销售的50%
        fair_value_range = (fair_low, fair_high)

        if total_multiple < 0.25:
            recommendation = "对价偏低，建议卖家重新谈判或寻找其他买家"
        elif total_multiple < 0.50:
            recommendation = "对价在合理区间内，交易结构可行"
        else:
            recommendation = "对价偏高，建议买家仔细评估药物商业潜力"

        return BDDealOutput(
            drug_name=drug,
            deal_type=input_data.deal_type,
            upfront_value=upfront_pv,
            expected_milestones_value=total_milestone_pv,
            expected_royalties_value=total_royalty_pv,
            total_deal_value=total_deal_value,
            seller_proceeds=seller_proceeds,
            buyer_net_value=buyer_net,
            upfront_to_peak_sales=upfront_multiple,
            total_to_peak_sales=total_multiple,
            fair_value_range=fair_value_range,
            recommendation=recommendation,
        )

    def _calculate_tiered_royalty(
        self, sales: float, tiers: List[Dict]
    ) -> float:
        """计算分级分成"""
        total = 0.0
        remaining = sales
        prev_threshold = 0

        for tier in tiers:
            threshold = tier.get("threshold", float("inf"))
            rate = tier.get("rate", 0)
            tier_sales = min(remaining, threshold - prev_threshold)
            total += tier_sales * rate
            remaining -= tier_sales
            prev_threshold = threshold
            if remaining <= 0:
                break

        return total

    # -------------------------------------------------------------------------
    # 4. 成熟产品销售折现模型
    # -------------------------------------------------------------------------

    def mature_product_valuation(self, input_data: MatureProductInput) -> Dict:
        """
        成熟产品销售折现模型

        适用于已过/将过专利期的品种
        """
        drug = input_data.drug_name
        rate = input_data.discount_rate

        # 默认仿制药侵蚀曲线
        if input_data.generic_erosion_schedule is None:
            erosion_schedule = [0.40, 0.65, 0.80, 0.85, 0.85]  # 专利到期后逐年侵蚀率
        else:
            erosion_schedule = input_data.generic_erosion_schedule

        total_npv = 0.0
        yearly_details = []

        total_years = input_data.years_to_patent_expiry + len(erosion_schedule)

        for year in range(1, total_years + 1):
            if year <= input_data.years_to_patent_expiry:
                # 专利期内
                growth_factor = (1 + input_data.pre_expiry_growth_rate) ** (year - 1)
                sales = input_data.current_annual_sales_cny * growth_factor
                erosion = 0
            else:
                # 专利到期后
                post_expiry_year = year - input_data.years_to_patent_expiry - 1
                if post_expiry_year < len(erosion_schedule):
                    erosion = erosion_schedule[post_expiry_year]
                else:
                    erosion = erosion_schedule[-1]
                sales = input_data.current_annual_sales_cny * (1 - erosion)

            # 集采叠加效应
            if input_data.vbp_discount_impact > 0:
                sales = sales * (1 - input_data.vbp_discount_impact)

            pv = sales / ((1 + rate) ** year)
            total_npv += pv

            yearly_details.append({
                "年份": year,
                "阶段": "专利期内" if year <= input_data.years_to_patent_expiry else f"专利到期后第{year - input_data.years_to_patent_expiry}年",
                "销售额（万元）": round(sales / 10000, 0),
                "仿制药侵蚀率": f"{erosion:.0%}",
                "现值（万元）": round(pv / 10000, 0),
            })

        return {
            "药物名称": drug,
            "当前年销售额（万元）": round(input_data.current_annual_sales_cny / 10000, 0),
            "专利剩余年数": input_data.years_to_patent_expiry,
            "产品剩余价值NPV（万元）": round(total_npv / 10000, 0),
            "年度明细": yearly_details,
        }

    # -------------------------------------------------------------------------
    # 5. 可比药物分析法
    # -------------------------------------------------------------------------

    def comparable_drug_analysis(
        self,
        target_drug: str,
        target_indication: str,
        target_moa: str,  # Mechanism of Action
        comparable_drugs: List[Dict],
    ) -> Dict:
        """
        可比药物分析法

        对标同靶点/同适应症药物的关键指标

        Args:
            target_drug: 目标药物名称
            target_indication: 目标适应症
            target_moa: 作用机制
            comparable_drugs: [
                {"name": str, "moa": str, "indication": str, "peak_sales_cny": float,
                 "annual_cost_cny": float, "launch_year": int, "market_share": float, ...}
            ]
        """
        if not comparable_drugs:
            return {"error": "无可比药物数据"}

        # 提取可比药物的关键指标
        peak_sales_list = [d.get("peak_sales_cny", 0) for d in comparable_drugs if d.get("peak_sales_cny")]
        annual_costs = [d.get("annual_cost_cny", 0) for d in comparable_drugs if d.get("annual_cost_cny")]
        market_shares = [d.get("market_share", 0) for d in comparable_drugs if d.get("market_share")]

        # 中位数和范围
        def median(lst):
            if not lst:
                return 0
            s = sorted(lst)
            mid = len(s) // 2
            return s[mid] if len(s) % 2 else (s[mid-1] + s[mid]) / 2

        median_peak = median(peak_sales_list)
        avg_annual_cost = sum(annual_costs) / len(annual_costs) if annual_costs else 0
        avg_market_share = sum(market_shares) / len(market_shares) if market_shares else 0

        # 生成对比表
        comparison = []
        for d in comparable_drugs:
            comparison.append({
                "药物名称": d.get("name", ""),
                "靶点/MOA": d.get("moa", ""),
                "适应症": d.get("indication", ""),
                "峰值销售（万元）": round(d.get("peak_sales_cny", 0) / 10000, 0) if d.get("peak_sales_cny") else "N/A",
                "年治疗费用（元）": d.get("annual_cost_cny", "N/A"),
                "上市年份": d.get("launch_year", "N/A"),
                "市场份额": f"{d.get('market_share', 0):.1%}" if d.get("market_share") else "N/A",
                "临床优势": d.get("clinical_advantage", ""),
            })

        return {
            "目标药物": target_drug,
            "目标适应症": target_indication,
            "作用机制": target_moa,
            "可比药物数量": len(comparable_drugs),
            "可比药物中位峰值销售（万元）": round(median_peak / 10000, 0),
            "可比药物平均年治疗费用（元）": round(avg_annual_cost, 0),
            "可比药物平均市场份额": f"{avg_market_share:.1%}",
            "估值参考": {
                "乐观估值（×1.2）": round(median_peak * 1.2 / 10000, 0) if median_peak > 0 else "N/A",
                "基准估值": round(median_peak / 10000, 0) if median_peak > 0 else "N/A",
                "保守估值（×0.7）": round(median_peak * 0.7 / 10000, 0) if median_peak > 0 else "N/A",
            },
            "定价参考区间（元）": f"{round(avg_annual_cost * 0.8, 0)} ~ {round(avg_annual_cost * 1.2, 0)}",
            "可比药物列表": comparison,
        }

    # -------------------------------------------------------------------------
    # 6. 管线组合（Portfolio）分析
    # -------------------------------------------------------------------------

    def portfolio_analysis(self, pipelines: List[RnpvInput]) -> Dict:
        """
        管线组合分析

        对多个管线进行批量rNPV估值，输出组合总估值和优先级排序
        """
        results = []
        total_rnpv = 0
        total_cost = 0

        for p in pipelines:
            try:
                result = self.rnpv_valuation(p)
                results.append(result)
                total_rnpv += result.rnpv
                total_cost += result.development_costs
            except Exception as e:
                results.append({"error": str(e), "drug": p.drug_name})

        # 按rNPV/成本排序
        valid_results = [r for r in results if isinstance(r, RnpvOutput)]
        ranked = sorted(
            valid_results,
            key=lambda x: (x.rnpv / max(x.development_costs, 1)) if x.development_costs > 0 else 0,
            reverse=True,
        )

        ranking = []
        for i, r in enumerate(ranked, 1):
            rnpv_cost_ratio = r.rnpv / max(r.development_costs, 1) if r.development_costs > 0 else float("inf")
            ranking.append({
                "排名": i,
                "管线": r.drug_name,
                "阶段": r.current_phase,
                "治疗领域": r.therapeutic_area,
                "rNPV（万元）": round(r.rnpv / 10000, 0),
                "累积成功率": f"{r.cumulative_success_prob:.1%}",
                "风险等级": r.risk_level,
                "rNPV/成本比": f"{rnpv_cost_ratio:.1f}x",
            })

        return {
            "管线总数": len(pipelines),
            "估值有效管线数": len(valid_results),
            "管线组合总rNPV（万元）": round(total_rnpv / 10000, 0),
            "管线优先级排序": ranking,
            "前3大管线价值占比": self._top3_concentration(ranked, total_rnpv),
        }

    def _top3_concentration(self, ranked: List[RnpvOutput], total_rnpv: float) -> str:
        """计算前3管线价值集中度"""
        if len(ranked) == 0:
            return "N/A"

        # 仅统计rNPV为正的管线
        positive_pipelines = [r for r in ranked if r.rnpv > 0]
        n_positive = len(positive_pipelines)

        if n_positive == 0:
            return "无正价值管线：所有管线当前rNPV均为负，建议重新评估管线策略或寻找BD合作伙伴分担成本"

        if n_positive == 1:
            r = positive_pipelines[0]
            return f"⚠️ 仅1条管线贡献正价值（{r.drug_name}，rNPV={r.rnpv/10000:.0f}万元），其余管线均为负值。单一管线依赖风险极高，管线多元化严重不足"

        if total_rnpv <= 0:
            return f"组合总rNPV为负，但{n_positive}条管线为正值。负值管线拖累严重，建议评估是否终止/BD部分管线"

        top3_rnpv = sum(r.rnpv for r in ranked[:3])
        positive_total = sum(r.rnpv for r in positive_pipelines)
        concentration = top3_rnpv / positive_total  # 用正值之和做分母

        if n_positive <= len(ranked) * 0.5:
            extra_note = f"（共{len(ranked)}条管线，仅{n_positive}条正价值）"
        else:
            extra_note = ""

        if concentration > 0.85:
            return f"{concentration:.0%}{extra_note} — 过度集中风险！管线多元化不足"
        elif concentration > 0.60:
            return f"{concentration:.0%}{extra_note} — 集中度较高，建议关注后续管线补充"
        else:
            return f"{concentration:.0%}{extra_note} — 分散度合理"


# =============================================================================
# 便捷函数
# =============================================================================

def quick_rnpv(
    drug_name: str,
    phase: str = "phase_ii",
    therapeutic_area: str = "oncology",
    peak_sales_cny: float = 2_000_000_000,  # 20亿元
    years_to_launch: float = 5.0,
) -> RnpvOutput:
    """快速rNPV估值"""
    phase_map = {
        "preclinical": ClinicalPhase.PRECLINICAL,
        "phase_i": ClinicalPhase.PHASE_I,
        "phase_ii": ClinicalPhase.PHASE_II,
        "phase_iii": ClinicalPhase.PHASE_III,
        "nda": ClinicalPhase.NDA,
    }
    ta_map = {
        "oncology": TherapeuticArea.ONCOLOGY,
        "cardiovascular": TherapeuticArea.CARDIOVASCULAR,
        "cns": TherapeuticArea.CNS,
        "immunology": TherapeuticArea.IMMUNOLOGY,
        "infectious": TherapeuticArea.INFECTIOUS,
        "metabolic": TherapeuticArea.METABOLIC,
        "rare_disease": TherapeuticArea.RARE_DISEASE,
    }

    model = PharmaValuationModels()
    return model.rnpv_valuation(RnpvInput(
        drug_name=drug_name,
        current_phase=phase_map.get(phase, ClinicalPhase.PHASE_II),
        therapeutic_area=ta_map.get(therapeutic_area, TherapeuticArea.ONCOLOGY),
        years_to_launch=years_to_launch,
        peak_sales_cny=peak_sales_cny,
    ))


def quick_bd_deal(
    drug_name: str,
    upfront: float = 100_000_000,
    peak_sales: float = 2_000_000_000,
    royalty_rate: float = 0.12,
) -> BDDealOutput:
    """快速BD交易分析"""
    model = PharmaValuationModels()
    return model.bd_deal_analysis(BDDealInput(
        drug_name=drug_name,
        deal_type="license-in",
        upfront_cny=upfront,
        milestones=[
            {"stage": "phase_3_start", "amount": 100_000_000, "prob": 0.60},
            {"stage": "nda_approval", "amount": 200_000_000, "prob": 0.30},
        ],
        royalty_rate=royalty_rate,
        peak_sales_cny=peak_sales,
    ))


# =============================================================================
# 测试和使用示例
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  医药估值模型（Pharma Valuation Models）测试")
    print("=" * 70)

    pvm = PharmaValuationModels(discount_rate=0.12)

    # ---- 测试1：rNPV估值 ----
    print("\n【测试1】rNPV管线估值 — PD-L1单抗（Phase II）")
    print("-" * 50)
    rnpv_input = RnpvInput(
        drug_name="XX-001（PD-L1单抗）",
        current_phase=ClinicalPhase.PHASE_II,
        therapeutic_area=TherapeuticArea.ONCOLOGY,
        years_to_launch=5.0,
        commercial_years=12,
        peak_sales_cny=2_500_000_000,  # 25亿
        ramp_up_years=4,
        peak_years=5,
        launch_costs_cny=500_000_000,
        annual_commercial_costs_cny=100_000_000,
    )
    rnpv_result = pvm.rnpv_valuation(rnpv_input)
    print(json.dumps(rnpv_result.to_dict(), ensure_ascii=False, indent=2))

    # ---- 测试2：峰值销售估计 ----
    print("\n【测试2】峰值销售估计 — 非小细胞肺癌（NSCLC）")
    print("-" * 50)
    peak_input = PeakSalesInput(
        drug_name="XX-001（PD-L1单抗）",
        indication="非小细胞肺癌（NSCLC）一线治疗",
        target_population=1_400_000_000,  # 中国14亿人口
        incidence_rate=45.6,  # NSCLC发病率约45.6/10万
        diagnosis_rate=0.65,
        treatment_rate=0.75,
        target_market_share=0.20,
        annual_treatment_cost_cny=80_000,  # 年治疗费用8万元
        competitor_share=0.55,
    )
    peak_result = pvm.peak_sales_estimation(peak_input)
    print(json.dumps(peak_result.to_dict(), ensure_ascii=False, indent=2))

    # ---- 测试3：BD交易分析 ----
    print("\n【测试3】BD交易分析 — License-in PD-1双抗")
    print("-" * 50)
    bd_input = BDDealInput(
        drug_name="PD-1/VEGF双抗",
        deal_type="license-in",
        upfront_cny=200_000_000,  # 2亿首付
        milestones=[
            {"stage": "phase_3_start", "amount": 100_000_000, "prob": 0.60},
            {"stage": "nda_approval", "amount": 200_000_000, "prob": 0.30},
            {"stage": "sales_1billion", "amount": 150_000_000, "prob": 0.25},
        ],
        royalty_rate=0.12,
        royalty_rate_tiers=[
            {"threshold": 500_000_000, "rate": 0.10},
            {"threshold": 1_000_000_000, "rate": 0.12},
            {"threshold": float("inf"), "rate": 0.15},
        ],
        peak_sales_cny=3_000_000_000,
        discount_rate=0.12,
        development_costs_cny=300_000_000,
        commercialization_costs_cny=200_000_000,
    )
    bd_result = pvm.bd_deal_analysis(bd_input)
    print(json.dumps(bd_result.to_dict(), ensure_ascii=False, indent=2))

    # ---- 测试4：成熟产品销售折现 ----
    print("\n【测试4】成熟产品销售折现 — 阿托伐他汀（专利即将到期）")
    print("-" * 50)
    mature_input = MatureProductInput(
        drug_name="阿托伐他汀钙片",
        generic_name="阿托伐他汀",
        current_annual_sales_cny=500_000_000,  # 5亿
        years_to_patent_expiry=2,
        discount_rate=0.10,
        pre_expiry_growth_rate=0.03,
    )
    mature_result = pvm.mature_product_valuation(mature_input)
    print(json.dumps(mature_result, ensure_ascii=False, indent=2))

    # ---- 测试5：管线组合分析 ----
    print("\n【测试5】管线组合分析")
    print("-" * 50)
    pipelines = [
        RnpvInput("PD-L1单抗", ClinicalPhase.PHASE_III, TherapeuticArea.ONCOLOGY, 3.0, 12, 3_000_000_000),
        RnpvInput("HER2 ADC", ClinicalPhase.PHASE_II, TherapeuticArea.ONCOLOGY, 5.0, 12, 2_000_000_000),
        RnpvInput("GLP-1口服", ClinicalPhase.PHASE_I, TherapeuticArea.METABOLIC, 7.0, 12, 5_000_000_000),
        RnpvInput("CD19 CAR-T", ClinicalPhase.PHASE_I, TherapeuticArea.ONCOLOGY, 6.0, 10, 800_000_000),
    ]
    portfolio = pvm.portfolio_analysis(pipelines)
    print(json.dumps(portfolio, ensure_ascii=False, indent=2))

    print("\n" + "=" * 70)
    print("  所有测试完成！")
    print("=" * 70)
