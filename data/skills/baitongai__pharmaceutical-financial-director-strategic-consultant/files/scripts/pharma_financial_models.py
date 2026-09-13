#!/usr/bin/env python3
"""
医药财务模型（Pharma Financial Models）
=======================================
包含7个医药行业专用财务模型：
1. 药企财务比率分析模型
2. 药企ROE分解模型（仿制药/创新药双线）
3. 临床阶段现金流分析模型（Burn Rate / Cash Runway）
4. 药物生命周期财务预测模型
5. 药品定价敏感性分析模型
6. 医药市场准入SWOT分析模型
7. 专利悬崖财务预警模型

基于 Finance Director Enhanced v4.0.0 框架改造
"""

import math
import json
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# 数据类型定义
# =============================================================================

class DrugType(Enum):
    """药物类型"""
    INNOVATIVE = "innovative"  # 创新药（1类新药）
    BIOSIMILAR = "biosimilar"  # 生物类似药
    GENERIC = "generic"  # 仿制药
    ME_TOO = "me_too"  # me-too/me-better


class RevenueStream(Enum):
    """收入来源"""
    DRUG_SALES = "drug_sales"
    BD_INCOME = "bd_income"  # 授权收入
    CDMO = "cdmo"
    GRANT = "grant"  # 政府补助


@dataclass
class PharmaRatioInput:
    """药企财务比率输入"""
    company_name: str
    drug_type: DrugType

    # 损益表
    revenue: float  # 营业收入
    cost_of_goods: float  # 营业成本
    rd_expense: float  # 研发费用
    selling_expense: float  # 销售费用（学术推广费）
    admin_expense: float  # 管理费用
    operating_profit: float  # 营业利润
    net_profit: float  # 净利润

    # 资产负债表
    total_assets: float
    total_equity: float
    total_liabilities: float

    # 运营指标
    rd_headcount: int  # 研发人员数
    total_headcount: int  # 总员工数
    n_pipeline_drugs: int  # 在研管线数量
    n_clinical_phase_drugs: int  # 临床阶段管线数量

    # 产品维度（可选，用于单品分析）
    product_details: Optional[List[Dict]] = None  # [{"name": str, "revenue": float, "gross_margin": float}]


@dataclass
class CashFlowInput:
    """临床阶段现金流输入"""
    company_name: str
    current_cash: float  # 账面现金
    monthly_burn_rate: float  # 月现金消耗
    monthly_rd_spend: float  # 月研发支出
    monthly_admin_spend: float  # 月管理支出

    next_milestone_payment: float = 0  # 下一里程碑付款
    months_to_next_milestone: int = 12
    expected_revenue_monthly: float = 0  # 已有产品的月收入（如果有）

    financing_lead_time_months: int = 6  # 融资到账周期


@dataclass
class LifecycleInput:
    """药物生命周期输入"""
    drug_name: str
    launch_year: int
    peak_sales_cny: float
    compound_patent_expiry: int  # 化合物专利到期年份

    # 可选参数
    current_year: int = 2026
    ramp_years: int = 4  # 爬坡年数
    peak_years: int = 5  # 峰值维持年数

    # 专利
    formulation_patent_expiry: Optional[int] = None  # 制剂专利到期年份

    # 成本
    cog_percent: float = 0.25  # 营业成本占收入比
    sg_and_a_percent: float = 0.30  # 销售管理费用占收入比
    rd_maintenance_percent: float = 0.08  # 上市后维护型研发占收入比
    tax_rate: float = 0.15  # 高新技术企业优惠税率

    # 集采影响
    vbp_impact_year: Optional[int] = None  # 预期集采年份
    vbp_price_cut: float = 0.50  # 集采降价幅度

    # 折现率
    discount_rate: float = 0.10


@dataclass
class PricingSensitivityInput:
    """定价敏感性分析输入"""
    drug_name: str
    base_price_cny: float  # 基准年治疗费用
    base_peak_patients: int  # 基准峰值患者数
    launch_year: int = 2027
    commercial_years: int = 10
    discount_rate: float = 0.10

    # 变量范围
    price_range: Tuple[float, float] = (-0.50, +0.10)  # 价格变动范围（-50% ~ +10%）
    patient_range: Tuple[float, float] = (-0.30, +0.20)  # 患者数变动范围
    vbp_prob_range: Tuple[float, float] = (0.0, 1.0)  # 集采概率范围


# =============================================================================
# 核心财务模型
# =============================================================================

class PharmaFinancialModels:
    """医药财务模型主类"""

    def __init__(self, discount_rate: float = 0.10):
        self.discount_rate = discount_rate

    # -------------------------------------------------------------------------
    # 1. 药企财务比率分析模型
    # -------------------------------------------------------------------------

    def pharma_ratio_analysis(self, input_data: PharmaRatioInput) -> Dict:
        """
        药企财务比率分析（医药行业专用指标）

        新增指标：
        - R&D Intensity（研发强度）
        - 单品毛利率
        - 学术推广费用率
        - 人均创收
        - 人均管线价值
        """
        # 通用财务比率
        gross_margin = (input_data.revenue - input_data.cost_of_goods) / input_data.revenue if input_data.revenue > 0 else 0
        net_margin = input_data.net_profit / input_data.revenue if input_data.revenue > 0 else 0
        roe = input_data.net_profit / input_data.total_equity if input_data.total_equity > 0 else 0
        roa = input_data.net_profit / input_data.total_assets if input_data.total_assets > 0 else 0
        debt_ratio = input_data.total_liabilities / input_data.total_assets if input_data.total_assets > 0 else 0

        # 医药专用指标
        rd_intensity = input_data.rd_expense / input_data.revenue if input_data.revenue > 0 else float("inf")
        selling_ratio = input_data.selling_expense / input_data.revenue if input_data.revenue > 0 else 0

        # 人均指标
        revenue_per_head = input_data.revenue / input_data.total_headcount if input_data.total_headcount > 0 else 0
        rd_per_head = input_data.rd_expense / input_data.rd_headcount if input_data.rd_headcount > 0 else 0

        # 管线效率
        pipeline_value_per_rd_head = input_data.n_pipeline_drugs / input_data.rd_headcount if input_data.rd_headcount > 0 else 0

        # 单品分析
        product_analysis = []
        if input_data.product_details:
            for prod in input_data.product_details:
                contribution = prod["revenue"] / input_data.revenue if input_data.revenue > 0 else 0
                product_analysis.append({
                    "产品": prod["name"],
                    "收入（万元）": round(prod["revenue"] / 10000, 0),
                    "收入占比": f"{contribution:.1%}",
                    "毛利率": f"{prod.get('gross_margin', 0):.1%}",
                })

        # 行业对标判断
        assessments = self._generate_pharma_ratio_assessments(
            input_data.drug_type, rd_intensity, gross_margin, roe
        )

        return {
            "公司名称": input_data.company_name,
            "药物类型": input_data.drug_type.value,
            # 盈利能力
            "毛利率": f"{gross_margin:.1%}",
            "净利率": f"{net_margin:.1%}",
            "ROE": f"{roe:.1%}",
            "ROA": f"{roa:.1%}",
            # 医药专用
            "研发强度（R&D Intensity）": f"{rd_intensity:.1%}",
            "学术推广费用率": f"{selling_ratio:.1%}",
            "负债率": f"{debt_ratio:.1%}",
            # 人均/管线效率
            "人均创收（万元）": round(revenue_per_head / 10000, 0),
            "人均研发支出（万元）": round(rd_per_head / 10000, 0),
            "管线数/研发人员": f"{pipeline_value_per_rd_head:.2f}",
            "在研管线总数": input_data.n_pipeline_drugs,
            "临床阶段管线数": input_data.n_clinical_phase_drugs,
            # 单品分析
            "单品贡献分析": product_analysis,
            # 行业对标
            "行业对标评估": assessments,
        }

    def _generate_pharma_ratio_assessments(
        self, drug_type: DrugType, rd_intensity: float,
        gross_margin: float, roe: float
    ) -> List[str]:
        """生成行业对标评估"""
        assessments = []

        # 研发强度对标
        if drug_type == DrugType.INNOVATIVE or drug_type == DrugType.BIOSIMILAR:
            if rd_intensity > 0.15:
                assessments.append(f"✅ 研发强度{rd_intensity:.1%}，符合创新药企标准（>15%）")
            elif rd_intensity > 0.08:
                assessments.append(f"⚠️ 研发强度{rd_intensity:.1%}，偏低，可能影响管线可持续性")
            else:
                assessments.append(f"❌ 研发强度{rd_intensity:.1%}，显著低于创新药企行业水平")
        else:
            if rd_intensity > 0.08:
                assessments.append(f"✅ 仿制药企研发投入偏高，可能向创新转型")
            elif rd_intensity > 0.03:
                assessments.append(f"✅ 研发强度{rd_intensity:.1%}，符合仿制药企特征")
            else:
                assessments.append(f"⚠️ 研发强度{rd_intensity:.1%}，持续低研发投入可能影响品种储备")

        # 毛利率对标
        if gross_margin > 0.80:
            assessments.append(f"✅ 毛利率{gross_margin:.1%}，处于行业优秀水平")
        elif gross_margin > 0.60:
            assessments.append(f"✅ 毛利率{gross_margin:.1%}，行业正常水平")
        else:
            assessments.append(f"⚠️ 毛利率{gross_margin:.1%}，偏低（集采影响？成本控制不足？）")

        # ROE对标
        if roe > 0.15:
            assessments.append(f"✅ ROE{roe:.1%}，股东回报良好")
        elif roe > 0.08:
            assessments.append(f"⚠️ ROE{roe:.1%}，一般水平（研发期roE偏低是正常的）")
        else:
            assessments.append(f"ℹ️ ROE{roe:.1%}，创新药企研发期低roe属正常现象")

        return assessments

    # -------------------------------------------------------------------------
    # 2. 药企ROE分解模型
    # -------------------------------------------------------------------------

    def pharma_roe_decomposition(
        self,
        company_name: str,
        drug_type: DrugType,
        net_margin: float,
        asset_turnover: float,
        equity_multiplier: float,
        rd_leverage: Optional[float] = None,  # 研发杠杆系数（管线价值/研发投入）
        pipeline_value_estimate: Optional[float] = None,
        rd_expense: Optional[float] = None,
    ) -> Dict:
        """
        药企ROE分解 — 仿制药/创新药双线分解

        仿制药：ROE = 净利率 × 资产周转率 × 权益乘数
        创新药：ROE = 净利率 × 研发杠杆系数 × 权益乘数
        """
        if drug_type == DrugType.INNOVATIVE or drug_type == DrugType.BIOSIMILAR:
            # 创新药线：用研发杠杆系数替代资产周转率
            if rd_leverage is None and pipeline_value_estimate and rd_expense and rd_expense > 0:
                rd_leverage = pipeline_value_estimate / rd_expense
            elif rd_leverage is None:
                rd_leverage = 1.0  # 默认

            roe = net_margin * rd_leverage * equity_multiplier

            return {
                "公司名称": company_name,
                "药物类型": drug_type.value,
                "分解方法": "创新药线（净利率 × 研发杠杆系数 × 权益乘数）",
                "ROE": f"{roe:.1%}",
                "净利率": f"{net_margin:.1%}",
                "研发杠杆系数": f"{rd_leverage:.2f}x" + ("（管线价值/研发投入）" if pipeline_value_estimate else ""),
                "权益乘数": f"{equity_multiplier:.2f}x",
                "解读": self._interpret_innovative_roe(net_margin, rd_leverage, equity_multiplier),
            }
        else:
            # 仿制药线：传统杜邦分析
            roe = net_margin * asset_turnover * equity_multiplier

            return {
                "公司名称": company_name,
                "药物类型": drug_type.value,
                "分解方法": "仿制药线（净利率 × 资产周转率 × 权益乘数）",
                "ROE": f"{roe:.1%}",
                "净利率": f"{net_margin:.1%}",
                "资产周转率": f"{asset_turnover:.2f}x",
                "权益乘数": f"{equity_multiplier:.2f}x",
                "解读": self._interpret_generic_roe(net_margin, asset_turnover, equity_multiplier),
            }

    def _interpret_innovative_roe(
        self, net_margin: float, rd_leverage: float, equity_multiplier: float
    ) -> str:
        """解读创新药ROE"""
        parts = []
        if net_margin > 0.20:
            parts.append(f"净利率{net_margin:.1%}较高（定价权强或成本控制好）")
        elif net_margin > 0:
            parts.append(f"净利率{net_margin:.1%}一般（可能处于放量初期）")
        else:
            parts.append(f"净利率为负（研发期无收入或收入有限，属正常现象）")

        if rd_leverage > 3.0:
            parts.append(f"研发杠杆系数{rd_leverage:.1f}x优秀（管线价值远高于研发投入）")
        elif rd_leverage > 1.0:
            parts.append(f"研发杠杆系数{rd_leverage:.1f}x合理（管线价值超过研发投入）")
        else:
            parts.append(f"研发杠杆系数{rd_leverage:.1f}x警示（管线价值可能低于投入，需重新评估）")

        if equity_multiplier > 3.0:
            parts.append(f"权益乘数{equity_multiplier:.1f}x偏高（负债较重，biotech典型特征）")
        else:
            parts.append(f"权益乘数{equity_multiplier:.1f}x健康（负债适中）")

        return "；".join(parts)

    def _interpret_generic_roe(
        self, net_margin: float, asset_turnover: float, equity_multiplier: float
    ) -> str:
        """解读仿制药ROE"""
        parts = []
        if net_margin > 0.15:
            parts.append(f"净利率{net_margin:.1%}良好（成本控制有效）")
        elif net_margin > 0.05:
            parts.append(f"净利率{net_margin:.1%}一般（集采压力？）")
        else:
            parts.append(f"净利率{net_margin:.1%}偏低（集采重创或成本失控）")

        if asset_turnover > 1.0:
            parts.append(f"资产周转率{asset_turnover:.2f}优秀（渠道效率高）")
        elif asset_turnover > 0.5:
            parts.append(f"资产周转率{asset_turnover:.2f}正常")
        else:
            parts.append(f"资产周转率{asset_turnover:.2f}偏低（库存积压或产能利用率不足）")

        return "；".join(parts)

    # -------------------------------------------------------------------------
    # 3. 临床阶段现金流分析模型
    # -------------------------------------------------------------------------

    def clinical_cash_flow_analysis(self, input_data: CashFlowInput) -> Dict:
        """
        临床阶段现金流分析（Burn Rate / Cash Runway）

        核心指标：
        - Gross Burn Rate：总月度现金消耗
        - Net Burn Rate：扣除收入后的净现金消耗
        - Cash Runway：现金余额可维持月数
        - Cash Zero Date：预估现金耗尽日期
        """
        company = input_data.company_name

        # 计算
        gross_burn = input_data.monthly_rd_spend + input_data.monthly_admin_spend
        net_burn = gross_burn - input_data.expected_revenue_monthly

        # Cash Runway
        if net_burn > 0:
            cash_runway_months = input_data.current_cash / net_burn
        else:
            cash_runway_months = float("inf")  # 正现金流，永不断流

        # 需要在下一次里程碑前补足的资金
        if input_data.next_milestone_payment > 0:
            cash_at_milestone = input_data.current_cash - net_burn * input_data.months_to_next_milestone
            cash_gap = input_data.next_milestone_payment - cash_at_milestone if cash_at_milestone < input_data.next_milestone_payment else 0
        else:
            cash_at_milestone = input_data.current_cash
            cash_gap = 0

        # 预警级别
        if cash_runway_months == float("inf"):
            alert_level = "🟢 安全（正现金流）"
            alert_color = "green"
        elif cash_runway_months > 24:
            alert_level = "🟢 充裕（>24个月）"
            alert_color = "green"
        elif cash_runway_months > 18:
            alert_level = "🟡 注意（18-24个月，可正常运营）"
            alert_color = "yellow"
        elif cash_runway_months > 12:
            alert_level = "🟡 关注（12-18个月，建议启动融资准备）"
            alert_color = "yellow"
        elif cash_runway_months > 6:
            alert_level = "🟠 预警（6-12个月，需加速融资或BD）"
            alert_color = "orange"
        else:
            alert_level = "🔴 紧急（<6个月，立即启动紧急融资/缩减管线）"
            alert_color = "red"

        # 融资建议（与预警级别和研发现金储备模型保持一致）
        if cash_runway_months <= 12:
            financing_advice = (
                f"🔴 紧急：现金仅能维持{cash_runway_months:.0f}个月！"
                f"立即启动紧急融资（预留{input_data.financing_lead_time_months}个月到账周期），"
                f"同时评估管线缩减方案。"
            )
        elif cash_runway_months <= 18:
            financing_advice = (
                f"🟡 建议在{cash_runway_months - input_data.financing_lead_time_months:.0f}个月内启动融资准备，"
                f"预留{input_data.financing_lead_time_months}个月融资到账时间。"
                f"关注下一里程碑前后的融资窗口。"
            )
        elif cash_runway_months <= 24:
            financing_advice = "现金可维持正常运营，但建议开始关注融资市场动态，为可能的数据读出窗口做准备。"
        else:
            financing_advice = "现金充裕（>24个月），可正常运营。超额资金可考虑短期理财（确保T+3可赎回）。"

        return {
            "公司名称": company,
            "账面现金（万元）": round(input_data.current_cash / 10000, 0),
            "月总消耗（Gross Burn, 万元）": round(gross_burn / 10000, 0),
            "月净消耗（Net Burn, 万元）": round(net_burn / 10000, 0),
            "月研发支出（万元）": round(input_data.monthly_rd_spend / 10000, 0),
            "月管理支出（万元）": round(input_data.monthly_admin_spend / 10000, 0),
            "现金跑道（月）": f"{cash_runway_months:.1f}" if cash_runway_months != float("inf") else "∞（正现金流）",
            "现金跑道（年）": f"{cash_runway_months/12:.1f}" if cash_runway_months != float("inf") else "∞",
            "预警级别": alert_level,
            "下一里程碑付款（万元）": round(input_data.next_milestone_payment / 10000, 0),
            "到达里程碑时现金（万元）": round(cash_at_milestone / 10000, 0),
            "资金缺口（万元）": round(cash_gap / 10000, 0),
            "融资建议": financing_advice,
        }

    # -------------------------------------------------------------------------
    # 4. 药物生命周期财务预测模型
    # -------------------------------------------------------------------------

    def drug_lifecycle_forecast(self, input_data: LifecycleInput) -> Dict:
        """
        药物生命周期财务预测

        从上市到专利到期的全周期损益表和现金流预测
        """
        drug = input_data.drug_name
        rate = input_data.discount_rate

        # 计算总商业化年数
        total_years = input_data.compound_patent_expiry - input_data.launch_year + 5  # 专利后+5年

        yearly_data = []
        total_npv = 0
        cumulative_cf = 0

        for year in range(1, total_years + 1):
            yr = input_data.launch_year + year - 1

            # 销售曲线
            if year <= input_data.ramp_years:
                sales = input_data.peak_sales_cny * (year / input_data.ramp_years)
            elif year <= input_data.ramp_years + input_data.peak_years:
                sales = input_data.peak_sales_cny
            else:
                # 专利到期后的侵蚀
                post_peak = year - input_data.ramp_years - input_data.peak_years
                erosion = min(0.85, post_peak * 0.25)
                sales = input_data.peak_sales_cny * (1 - erosion)

            # 集采叠加影响
            vbp_flag = ""
            if input_data.vbp_impact_year and yr >= input_data.vbp_impact_year:
                sales = sales * (1 - input_data.vbp_price_cut)
                vbp_flag = "（集采影响）"

            # 损益表
            cogs = sales * input_data.cog_percent
            gross_profit = sales - cogs
            sga = sales * input_data.sg_and_a_percent
            rd_maintenance = sales * input_data.rd_maintenance_percent
            operating_profit = gross_profit - sga - rd_maintenance
            tax = max(0, operating_profit * input_data.tax_rate)
            net_income = operating_profit - tax

            # 简化现金流 = 净利润（不考虑折旧摊销）
            cashflow = net_income
            cumulative_cf += cashflow

            # NPV
            discount_factor = 1 / ((1 + rate) ** year)
            pv = cashflow * discount_factor
            total_npv += pv

            yearly_data.append({
                "年份": yr,
                "商业年第": year,
                "阶段": self._get_lifecycle_stage(year, input_data.ramp_years, input_data.peak_years),
                "销售额（万元）": round(sales / 10000, 0),
                "集采标注": vbp_flag,
                "毛利（万元）": round(gross_profit / 10000, 0),
                "营业利润（万元）": round(operating_profit / 10000, 0),
                "净利润（万元）": round(net_income / 10000, 0),
                "现金流（万元）": round(cashflow / 10000, 0),
                "现值（万元）": round(pv / 10000, 0),
            })

        return {
            "药物名称": drug,
            "上市年份": input_data.launch_year,
            "化合物专利到期": input_data.compound_patent_expiry,
            "预测总年数": total_years,
            "峰值年销售额（万元）": round(input_data.peak_sales_cny / 10000, 0),
            "全生命周期累计现金流（万元）": round(cumulative_cf / 10000, 0),
            "全生命周期NPV（万元）": round(total_npv / 10000, 0),
            "折现率": f"{rate:.0%}",
            "年度明细": yearly_data,
        }

    def _get_lifecycle_stage(self, year: int, ramp: int, peak: int) -> str:
        """获取生命周期阶段"""
        if year <= ramp:
            return "放量期"
        elif year <= ramp + peak:
            return "峰值期"
        else:
            return "衰退期"

    # -------------------------------------------------------------------------
    # 5. 药品定价敏感性分析模型
    # -------------------------------------------------------------------------

    def pricing_sensitivity_analysis(self, input_data: PricingSensitivityInput) -> Dict:
        """
        药品定价敏感性分析（龙卷风图数据）

        分析各变量对NPV的影响弹性
        """
        drug = input_data.drug_name
        rate = input_data.discount_rate

        # 基准NPV
        base_npv = self._calc_simple_npv(
            input_data.base_price_cny,
            input_data.base_peak_patients,
            input_data.commercial_years,
            rate,
        )

        # 各变量敏感性
        sensitivities = []

        # 1. 定价敏感性
        price_steps = [input_data.base_price_cny * (1 + input_data.price_range[0]),
                      input_data.base_price_cny * (1 + input_data.price_range[1])]
        for price in price_steps:
            npv = self._calc_simple_npv(price, input_data.base_peak_patients,
                                       input_data.commercial_years, rate)
            change = (npv - base_npv) / base_npv if base_npv != 0 else 0
            sensitivities.append({
                "变量": f"年治疗费用（¥{price/10000:.0f}万）",
                "类别": "定价",
                "NPV变动": f"{change:.1%}",
                "变动值（万元）": round((npv - base_npv) / 10000, 0),
            })

        # 2. 患者数敏感性
        patient_steps = [input_data.base_peak_patients * (1 + input_data.patient_range[0]),
                        input_data.base_peak_patients * (1 + input_data.patient_range[1])]
        for patients in patient_steps:
            npv = self._calc_simple_npv(input_data.base_price_cny, patients,
                                       input_data.commercial_years, rate)
            change = (npv - base_npv) / base_npv if base_npv != 0 else 0
            sensitivities.append({
                "变量": f"峰值患者数（{patients}人）",
                "类别": "患者数",
                "NPV变动": f"{change:.1%}",
                "变动值（万元）": round((npv - base_npv) / 10000, 0),
            })

        # 3. 集采概率敏感性
        for prob in input_data.vbp_prob_range:
            expected_price = (input_data.base_price_cny * (1 - prob * 0.50) +
                            input_data.base_price_cny * (1 - prob)) / 2  # 简化的期望价格
            npv = self._calc_simple_npv(expected_price, input_data.base_peak_patients,
                                       input_data.commercial_years, rate)
            change = (npv - base_npv) / base_npv if base_npv != 0 else 0
            sensitivities.append({
                "变量": f"集采概率（{prob:.0%}）",
                "类别": "集采风险",
                "NPV变动": f"{change:.1%}",
                "变动值（万元）": round((npv - base_npv) / 10000, 0),
            })

        # 排序（按NPV变动的绝对值）
        sensitivities.sort(key=lambda x: abs(float(x["NPV变动"].rstrip("%")) / 100), reverse=True)

        return {
            "药物名称": drug,
            "基准年治疗费用（万元）": round(input_data.base_price_cny / 10000, 1),
            "基准峰值患者数": f"{input_data.base_peak_patients:,}",
            "基准NPV（万元）": round(base_npv / 10000, 0),
            "敏感性分析（龙卷风图数据）": sensitivities,
            "启示": self._interpret_pricing_sensitivity(sensitivities),
        }

    def _calc_simple_npv(
        self, price: float, patients: int, years: int, rate: float
    ) -> float:
        """简化NPV计算"""
        revenue = price * patients
        net = revenue * 0.25  # 简化净利率
        npv = sum(net / ((1 + rate) ** y) for y in range(1, years + 1))
        return npv

    def _interpret_pricing_sensitivity(self, sensitivities: List[Dict]) -> str:
        """解释敏感性分析结果"""
        if not sensitivities:
            return ""
        top = sensitivities[0]
        return (
            f"对NPV影响最大的因素是「{top['变量']}」（{top['NPV变动']}变动）。"
            f"定价策略和医保准入路径的选择至关重要。"
        )

    # -------------------------------------------------------------------------
    # 6. 医药市场准入SWOT分析
    # -------------------------------------------------------------------------

    def market_access_swot(
        self,
        drug_name: str,
        indication: str,
        strengths: List[str],
        weaknesses: List[str],
        opportunities: List[str],
        threats: List[str],
        financial_impacts: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """
        医药市场准入SWOT分析

        为每个S/W/O/T要素附加财务影响量化评估
        """
        default_impacts = {
            "靶点创新性": "峰值销售溢价+15~25%",
            "临床数据优效性（OS HR<0.8）": "市场份额+10%，rNPV+20%",
            "生产工艺壁垒": "仿制药威胁延迟2-3年，NPV+15%",
            "专利保护强度": "独家期延长=峰值期延长，NPV+10~20%",
            "给药途径不便": "患者依从性低→市场份额-10%",
            "不良反应谱不佳": "安全性风险→市场份额-15%，FDA/EMA审评风险增加",
            "适应症窄": "市场空间受限→峰值销售上限-30%",
            "缺乏中国人群数据": "CDE可能要求桥接试验→上市延迟6-12月，NPV-10%",
            "竞品专利到期": "仿制药压力→NPV-20~50%",
            "CDE加速审评": "上市提前6-12月→NPV+15%",
            "NRDL谈判窗口": "快速进医保→放量加速，NPV+10~20%",
            "集采扩面风险": "降价50~70%→NPV-30~60%",
            "DRG/DIP改革": "住院用药受控→销售额-10~20%",
        }

        impacts = financial_impacts or default_impacts

        swot_matrix = {
            "优势（S）": [
                {"要素": s, "财务影响": impacts.get(s, "待评估")}
                for s in strengths
            ],
            "劣势（W）": [
                {"要素": w, "财务影响": impacts.get(w, "待评估")}
                for w in weaknesses
            ],
            "机会（O）": [
                {"要素": o, "财务影响": impacts.get(o, "待评估")}
                for o in opportunities
            ],
            "威胁（T）": [
                {"要素": t, "财务影响": impacts.get(t, "待评估")}
                for t in threats
            ],
        }

        # 综合评估
        s_score = len(strengths)
        w_score = len(weaknesses)
        o_score = len(opportunities)
        t_score = len(threats)

        net_score = s_score + o_score - w_score - t_score
        if net_score > 3:
            overall = "积极：优势+机会显著超过劣势+威胁，建议积极推进入市"
        elif net_score > 0:
            overall = "中性偏积极：优势略大于劣势，需关注关键威胁的应对"
        elif net_score > -3:
            overall = "中性偏谨慎：劣势和威胁较多，建议先补短板再全面推广"
        else:
            overall = "谨慎：劣势和威胁显著，需重新评估商业化策略"

        return {
            "药物名称": drug_name,
            "适应症": indication,
            "SWOT矩阵": swot_matrix,
            "综合评分（S+O-W-T）": net_score,
            "综合评估": overall,
        }

    # -------------------------------------------------------------------------
    # 7. 专利悬崖财务预警模型
    # -------------------------------------------------------------------------

    def patent_cliff_alert(
        self,
        drug_name: str,
        current_annual_sales: float,
        compound_patent_expiry: int,
        current_year: int = 2026,
        revenue_contribution: float = 1.0,  # 该品种占公司总收入比
    ) -> Dict:
        """
        专利悬崖财务预警

        评估专利到期对公司财务的冲击
        """
        years_remaining = compound_patent_expiry - current_year

        # 专利到期后销售额预测
        # 参考行业数据：化合物专利到期后1-3年销售额下降到峰值的20-35%
        year1_sales = current_annual_sales * 0.60  # 第一年保留60%
        year2_sales = current_annual_sales * 0.30  # 第二年保留30%
        year3_sales = current_annual_sales * 0.15  # 第三年保留15%

        # 冲击评估
        if years_remaining <= 0:
            status = "已过专利期"
            urgency = "🔴 已发生"
        elif years_remaining <= 2:
            status = "迫在眉睫"
            urgency = "🔴 紧急：2年内到期，立即启动应对计划"
        elif years_remaining <= 5:
            status = "中期关注"
            urgency = "🟠 预警：5年内到期，需制定应对策略"
        elif years_remaining <= 8:
            status = "远期规划"
            urgency = "🟡 关注：8年内到期，纳入战略规划"
        else:
            status = "安全区"
            urgency = "🟢 安全：8年以上保护期"

        # 如果该品种占收入比重大，叠加公司级别风险
        concentration_risk = ""
        if revenue_contribution > 0.50 and years_remaining <= 5:
            concentration_risk = f"⚠️ 高度集中风险：该品种占收入{revenue_contribution:.0%}，专利到期将严重影响公司整体业绩"
        elif revenue_contribution > 0.30 and years_remaining <= 5:
            concentration_risk = f"⚡ 中度集中风险：该品种占收入{revenue_contribution:.0%}，需关注收入替代"
        else:
            concentration_risk = "✅ 收入分散度可接受"

        return {
            "药物名称": drug_name,
            "当前年销售额（万元）": round(current_annual_sales / 10000, 0),
            "占公司收入比": f"{revenue_contribution:.1%}",
            "化合物专利到期年份": compound_patent_expiry,
            "剩余保护年限": years_remaining,
            "预警状态": status,
            "紧急程度": urgency,
            "集中度风险": concentration_risk,
            "到期后销售预测": {
                "到期后第1年（万元）": round(year1_sales / 10000, 0),
                "到期后第2年（万元）": round(year2_sales / 10000, 0),
                "到期后第3年（万元）": round(year3_sales / 10000, 0),
            },
            "建议应对策略": self._patent_cliff_strategies(years_remaining, revenue_contribution),
        }

    def _patent_cliff_strategies(self, years: int, contribution: float) -> List[str]:
        """专利悬崖应对策略"""
        strategies = []
        if years <= 2:
            strategies.append("加速新一代产品上市（如果已布局）")
            strategies.append("考虑专利延长策略（儿科用药延长期/PTE）")
            strategies.append("评估License-out剩余市场的BD机会")
        if contribution > 0.30:
            strategies.append("加速非相关品种管线补充（M&A或BD）")
            strategies.append("控制该品种相关成本支出，为收入下降做准备")
        if years <= 5:
            strategies.append("制剂/用途/晶型等外围专利布局，拉长保护期")
            strategies.append("品牌仿制药策略（授权仿制药，争夺首仿市场）")
        strategies.append("开始布局下一代产品或新适应症，确保收入替代")
        return strategies


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  医药财务模型（Pharma Financial Models）测试")
    print("=" * 70)

    pfm = PharmaFinancialModels()

    # 测试1：药企财务比率分析
    print("\n【测试1】药企财务比率分析")
    print("-" * 50)
    ratio_input = PharmaRatioInput(
        company_name="XX创新药企",
        drug_type=DrugType.INNOVATIVE,
        revenue=3_500_000_000,
        cost_of_goods=700_000_000,
        rd_expense=800_000_000,
        selling_expense=1_200_000_000,
        admin_expense=300_000_000,
        operating_profit=500_000_000,
        net_profit=420_000_000,
        total_assets=8_000_000_000,
        total_equity=4_000_000_000,
        total_liabilities=4_000_000_000,
        rd_headcount=600,
        total_headcount=2500,
        n_pipeline_drugs=12,
        n_clinical_phase_drugs=5,
        product_details=[
            {"name": "PD-1单抗", "revenue": 1_500_000_000, "gross_margin": 0.85},
            {"name": "HER2 ADC", "revenue": 800_000_000, "gross_margin": 0.88},
            {"name": "BTK抑制剂", "revenue": 500_000_000, "gross_margin": 0.90},
        ],
    )
    print(json.dumps(pfm.pharma_ratio_analysis(ratio_input), ensure_ascii=False, indent=2))

    # 测试2：临床阶段现金流
    print("\n【测试2】临床阶段现金流分析")
    print("-" * 50)
    cf_input = CashFlowInput(
        company_name="XX Biotech（临床阶段）",
        current_cash=500_000_000,
        monthly_burn_rate=25_000_000,
        monthly_rd_spend=18_000_000,
        monthly_admin_spend=7_000_000,
        next_milestone_payment=100_000_000,
        months_to_next_milestone=8,
        expected_revenue_monthly=2_000_000,
    )
    print(json.dumps(pfm.clinical_cash_flow_analysis(cf_input), ensure_ascii=False, indent=2))

    # 测试3：药物生命周期
    print("\n【测试3】药物生命周期财务预测")
    print("-" * 50)
    lifecycle_input = LifecycleInput(
        drug_name="PD-L1单抗",
        launch_year=2027,
        peak_sales_cny=2_500_000_000,
        ramp_years=4,
        peak_years=5,
        compound_patent_expiry=2038,
        vbp_impact_year=2029,
        vbp_price_cut=0.45,
    )
    result = pfm.drug_lifecycle_forecast(lifecycle_input)
    # 只打印摘要（年度明细太长）
    summary = {k: v for k, v in result.items() if k != "年度明细"}
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # 测试4：定价敏感性
    print("\n【测试4】药品定价敏感性分析")
    print("-" * 50)
    sensitivity_input = PricingSensitivityInput(
        drug_name="PD-L1单抗",
        base_price_cny=80_000,
        base_peak_patients=50000,
    )
    print(json.dumps(pfm.pricing_sensitivity_analysis(sensitivity_input), ensure_ascii=False, indent=2))

    # 测试5：专利悬崖预警
    print("\n【测试5】专利悬崖预警")
    print("-" * 50)
    print(json.dumps(pfm.patent_cliff_alert(
        drug_name="阿托伐他汀钙片",
        current_annual_sales=300_000_000,
        compound_patent_expiry=2028,
        revenue_contribution=0.45,
    ), ensure_ascii=False, indent=2))

    print("\n" + "=" * 70)
    print("  所有测试完成！")
    print("=" * 70)
