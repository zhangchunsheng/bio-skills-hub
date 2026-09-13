#!/usr/bin/env python3
"""
医药财务总监·战略顾问 — 主入口（Pharma CFO Strategic Advisor）
============================================================
整合所有医药财务模型的统一入口，提供便捷的分析接口。

基于 Finance Director Enhanced v4.0.0 框架改造
"""

import json
from typing import Dict, List, Optional

from scripts.pharma_valuation_models import (
    PharmaValuationModels,
    RnpvInput, PeakSalesInput, BDDealInput, MatureProductInput,
    ClinicalPhase, TherapeuticArea,
)
from scripts.pharma_financial_models import (
    PharmaFinancialModels,
    PharmaRatioInput, CashFlowInput, LifecycleInput,
    PricingSensitivityInput, DrugType,
)
from scripts.pharma_cash_models import (
    PharmaCashModels,
    DrugInventoryInput, RDCashReserveInput, GMPInventoryInput,
    HospitalCreditInput, PhaseGateBudgetInput,
    HospitalGrade, DevelopmentPhase,
)


class PharmaCFO:
    """
    医药财务总监·战略顾问

    五大核心职责：
    1. 管线预算健康管理者 → pipeline_health_check()
    2. 药政与市场准入风险控制者 → policy_risk_assessment()
    3. 药品商业化战略保障者 → commercialization_strategy()
    4. GMP合规与研发保密权限设计者 → compliance_permission_design()
    5. 医药行业持续学习者 → 集成自主学习评估系统
    """

    def __init__(self, discount_rate: float = 0.12):
        self.discount_rate = discount_rate
        self.valuation = PharmaValuationModels(discount_rate=discount_rate)
        self.financial = PharmaFinancialModels(discount_rate=discount_rate)
        self.cash = PharmaCashModels()

    # =========================================================================
    # 职责1：管线预算健康管理者
    # =========================================================================

    def pipeline_health_check(
        self,
        pipelines: List[Dict],
        current_cash: float,
        monthly_burn_rate: float,
    ) -> Dict:
        """
        管线健康检查

        Args:
            pipelines: [{"drug_name": str, "phase": str, "therapeutic_area": str,
                         "peak_sales_cny": float, "years_to_launch": float}]
            current_cash: 账面现金
            monthly_burn_rate: 月现金消耗
        """
        # 管线估值
        rnpv_inputs = []
        for p in pipelines:
            phase_map = {
                "preclinical": ClinicalPhase.PRECLINICAL, "phase_i": ClinicalPhase.PHASE_I,
                "phase_ii": ClinicalPhase.PHASE_II, "phase_iii": ClinicalPhase.PHASE_III,
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

            rnpv_inputs.append(RnpvInput(
                drug_name=p["drug_name"],
                current_phase=phase_map.get(p["phase"], ClinicalPhase.PHASE_II),
                therapeutic_area=ta_map.get(p["therapeutic_area"], TherapeuticArea.ONCOLOGY),
                years_to_launch=p.get("years_to_launch", 5.0),
                peak_sales_cny=p["peak_sales_cny"],
            ))

        portfolio = self.valuation.portfolio_analysis(rnpv_inputs)

        # 现金流
        cash_analysis = self.financial.clinical_cash_flow_analysis(CashFlowInput(
            company_name="管线组合",
            current_cash=current_cash,
            monthly_burn_rate=monthly_burn_rate,
            monthly_rd_spend=monthly_burn_rate * 0.70,
            monthly_admin_spend=monthly_burn_rate * 0.30,
        ))

        return {
            "报告类型": "管线健康报告",
            "管线组合估值": portfolio,
            "现金流状况": cash_analysis,
            "建议": self._pipeline_health_recommendations(portfolio, cash_analysis),
        }

    def _pipeline_health_recommendations(self, portfolio: Dict, cash: Dict) -> List[str]:
        """管线健康建议"""
        recommendations = []
        ranking = portfolio.get("管线优先级排序", [])
        if ranking:
            top = ranking[0]
            recommendations.append(f"优先级最高管线：{top['管线']}（rNPV={top['rNPV（万元）']}万元，成功率={top['累积成功率']}）")

        runway = cash.get("现金跑道（月）", "∞")
        alert = cash.get("预警级别", "")
        if "🔴" in alert or "🟠" in alert:
            recommendations.append(f"⚠️ 现金流预警：{alert}，建议启动融资或BD")

        top3_conc = portfolio.get("前3大管线价值占比", "")
        if "过度集中" in top3_conc:
            recommendations.append(f"管线集中度风险：{top3_conc}，建议补充新管线或BD引进")

        return recommendations

    # =========================================================================
    # 职责2：药政与市场准入风险控制者
    # =========================================================================

    def policy_risk_assessment(
        self,
        drug_name: str,
        indication: str,
        vbp_risk_level: str = "medium",  # low/medium/high
        nrdl_probability: float = 0.5,
        patent_expiry: int = 2035,
        competitor_clinical_phase: Dict[str, int] = None,
    ) -> Dict:
        """
        药政与市场准入风险评估

        四维风险矩阵：
        1. 集采风险
        2. 医保谈判不确定性
        3. 专利悬崖
        4. 替代疗法威胁
        """
        # 1. 集采风险评估
        vbp_risks = {
            "low": {"降价幅度": "10-30%", "影响年份": "3-5年后", "说明": "品种不在集采目录或为创新药，短期内不受集采影响"},
            "medium": {"降价幅度": "30-50%", "影响年份": "1-3年内", "说明": "品种可能纳入下一批集采，需提前准备应对策略"},
            "high": {"降价幅度": "50-70%", "影响年份": "当年或明年", "说明": "品种过评企业数≥3家，集采概率高，需立即启动应对"},
        }

        # 2. 医保谈判风险评估
        if nrdl_probability > 0.7:
            nrdl_risk = "低风险：大概率进入医保，可加速放量"
        elif nrdl_probability > 0.3:
            nrdl_risk = "中等风险：谈判结果不确定，准备两组财务模型"
        else:
            nrdl_risk = "高风险：可能不进医保，需评估全自费市场的可行性"

        # 3. 专利悬崖
        patent_alert = self.financial.patent_cliff_alert(
            drug_name=drug_name,
            current_annual_sales=0,  # 此处假设在研管线，可替换
            compound_patent_expiry=patent_expiry,
        )

        # 4. 竞品威胁
        competitor_threat = "无竞品数据" if not competitor_clinical_phase else \
            f"竞品临床阶段分布：{json.dumps(competitor_clinical_phase, ensure_ascii=False)}"

        # 综合风险评分
        risk_scores = []
        if vbp_risk_level == "high":
            risk_scores.append(("集采风险", "高", 8))
        elif vbp_risk_level == "medium":
            risk_scores.append(("集采风险", "中", 5))
        else:
            risk_scores.append(("集采风险", "低", 2))

        if nrdl_probability < 0.3:
            risk_scores.append(("医保准入风险", "高", 7))
        elif nrdl_probability < 0.7:
            risk_scores.append(("医保准入风险", "中", 4))
        else:
            risk_scores.append(("医保准入风险", "低", 1))

        total_risk = sum(s[2] for s in risk_scores)

        if total_risk >= 12:
            overall_risk = "🔴 高风险：多项政策风险叠加，建议重新评估商业化策略"
        elif total_risk >= 7:
            overall_risk = "🟠 中等风险：存在显著政策不确定性，需制定风险缓解计划"
        else:
            overall_risk = "🟢 低风险：政策环境有利，可按计划推进"

        return {
            "药物名称": drug_name,
            "适应症": indication,
            "集采风险评估": vbp_risks.get(vbp_risk_level, {}),
            "医保谈判风险评估": nrdl_risk,
            "专利悬崖评估": patent_alert,
            "竞品威胁": competitor_threat,
            "综合风险评分": f"{total_risk}/22",
            "综合评估": overall_risk,
        }

    # =========================================================================
    # 职责3：药品商业化战略保障者
    # =========================================================================

    def commercialization_strategy(
        self,
        drug_name: str,
        indication: str,
        target_population: int,
        incidence_rate: float,
        annual_treatment_cost: float,
        target_market_share: float = 0.20,
    ) -> Dict:
        """
        药品商业化战略

        回答：适应症→市场→准入→定价 四个核心问题
        """
        # 1. 市场规模（患者流模型）
        peak_input = PeakSalesInput(
            drug_name=drug_name,
            indication=indication,
            target_population=target_population,
            incidence_rate=incidence_rate,
            annual_treatment_cost_cny=annual_treatment_cost,
            target_market_share=target_market_share,
        )
        peak = self.valuation.peak_sales_estimation(peak_input)

        # 2. 定价策略建议
        pricing_input = PricingSensitivityInput(
            drug_name=drug_name,
            base_price_cny=annual_treatment_cost,
            base_peak_patients=peak.target_patients,
        )
        pricing_sensitivity = self.financial.pricing_sensitivity_analysis(pricing_input)

        # 3. 准入路径建议
        if annual_treatment_cost > 150_000:
            access_path = "高值创新药：推荐国谈路径（NRDL），争取进入医保目录"
        elif annual_treatment_cost > 50_000:
            access_path = "中等价位：推荐挂网+医院准入路径，辅以患者援助计划（PAP）"
        else:
            access_path = "低价药：可考虑集采路径或基层市场覆盖"

        return {
            "药物名称": drug_name,
            "适应症": indication,
            "市场规模分析": peak.to_dict(),
            "定价敏感性": pricing_sensitivity,
            "准入路径建议": access_path,
        }

    # =========================================================================
    # 职责4：GMP合规与研发保密权限设计者
    # =========================================================================

    def compliance_permission_design(self) -> Dict:
        """
        GMP合规与研发保密权限分层设计

        输出权限矩阵
        """
        return {
            "权限分层体系": {
                "L0 - 完全隔离": {
                    "数据类型": ["盲态临床数据（随机分组方案）", "揭盲后个体患者数据（仅DMC）"],
                    "可访问角色": ["独立数据监查委员会（DMC）", "独立统计师"],
                    "药监审计要求": "盲态维护记录须可追溯",
                },
                "L1 - 核心机密": {
                    "数据类型": ["BD交易底价", "rNPV估值模型参数", "核心工艺参数（CMC关键步骤）",
                               "严重不良反应个例报告（SAE）"],
                    "可访问角色": ["CEO", "CFO", "BD Head", "生产负责人", "药物警戒负责人"],
                    "药监审计要求": "SAE须在24小时内上报CDE",
                },
                "L2 - 项目机密": {
                    "数据类型": ["临床试验方案", "期中分析汇总数据", "质量标准（QC）",
                               "BD交易条款框架（不含底价）", "专利策略"],
                    "可访问角色": ["项目组核心成员", "临床运营团队", "QA/QC", "IP律师"],
                    "药监审计要求": "方案修订须经CDE备案",
                },
                "L3 - 部门共享": {
                    "数据类型": ["已获批产品毛利率", "学术推广预算", "市场准入进度",
                               "通用CMC信息（给CDMO的）"],
                    "可访问角色": ["市场部", "销售部", "准入团队", "CDMO合作伙伴"],
                    "药监审计要求": "CDMO协议须包含数据安全条款",
                },
                "L4 - 公开信息": {
                    "数据类型": ["已上市产品说明书", "年报披露管线进度", "新闻稿数据"],
                    "可访问角色": ["全员", "投资者", "公众"],
                    "药监审计要求": "广告宣传须符合药品广告审查标准",
                },
            },
            "GMP审计数据完整性要求": [
                "ALCOA+原则：Attributable（可归属）、Legible（清晰可读）、Contemporaneous（实时记录）、Original（原始）、Accurate（准确）",
                "补充原则：Complete（完整）、Consistent（一致）、Enduring（持久）、Available（可获取）",
                "飞行检查应对：所有数据实时可查，不留死角",
            ],
        }

    # =========================================================================
    # 综合报告
    # =========================================================================

    def comprehensive_report(
        self,
        pipelines: List[Dict],
        current_cash: float,
        monthly_burn_rate: float,
        drug_name: str = "",
        indication: str = "",
        vbp_risk_level: str = "medium",
        nrdl_probability: float = 0.5,
        patent_expiry: int = 2035,
    ) -> Dict:
        """
        生成医药财务总监综合报告

        一站式输出所有关键分析

        Args:
            pipelines: 管线列表
            current_cash: 账面现金
            monthly_burn_rate: 月现金消耗
            drug_name: 药物名称（用于政策风险评估）
            indication: 适应症
            vbp_risk_level: 集采风险等级，可选 "low"/"medium"/"high"
            nrdl_probability: 预计进入NRDL的概率（0.0-1.0）
            patent_expiry: 专利到期年份
        """
        report = {
            "报告标题": "医药财务总监·战略顾问综合报告",
            "生成时间": __import__("datetime").datetime.now().strftime("%Y-%m-%d"),
            # 职责1
            "管线健康检查": self.pipeline_health_check(pipelines, current_cash, monthly_burn_rate),
        }

        # 职责2（如果提供了药物信息，透传所有参数）
        if drug_name and indication:
            report["政策风险评估"] = self.policy_risk_assessment(
                drug_name=drug_name,
                indication=indication,
                vbp_risk_level=vbp_risk_level,
                nrdl_probability=nrdl_probability,
                patent_expiry=patent_expiry,
            )

        # 职责4
        report["合规权限设计"] = self.compliance_permission_design()

        return report


# =============================================================================
# 便捷函数
# =============================================================================

def quick_analysis():
    """快速分析示例"""
    cfo = PharmaCFO()

    pipelines = [
        {"drug_name": "PD-L1单抗", "phase": "phase_iii", "therapeutic_area": "oncology",
         "peak_sales_cny": 2_500_000_000, "years_to_launch": 3.0},
        {"drug_name": "HER2 ADC", "phase": "phase_ii", "therapeutic_area": "oncology",
         "peak_sales_cny": 1_800_000_000, "years_to_launch": 5.0},
        {"drug_name": "GLP-1口服", "phase": "phase_i", "therapeutic_area": "metabolic",
         "peak_sales_cny": 4_000_000_000, "years_to_launch": 7.0},
    ]

    report = cfo.pipeline_health_check(
        pipelines=pipelines,
        current_cash=500_000_000,
        monthly_burn_rate=20_000_000,
    )

    return report


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  医药财务总监·战略顾问 — 主入口测试")
    print("=" * 70)

    cfo = PharmaCFO(discount_rate=0.12)

    # 测试1：管线健康检查
    print("\n【测试1】管线健康检查")
    print("-" * 50)
    pipelines = [
        {"drug_name": "PD-L1单抗", "phase": "phase_iii", "therapeutic_area": "oncology",
         "peak_sales_cny": 2_500_000_000, "years_to_launch": 3.0},
        {"drug_name": "HER2 ADC", "phase": "phase_ii", "therapeutic_area": "oncology",
         "peak_sales_cny": 1_800_000_000, "years_to_launch": 5.0},
        {"drug_name": "GLP-1口服", "phase": "phase_i", "therapeutic_area": "metabolic",
         "peak_sales_cny": 4_000_000_000, "years_to_launch": 7.0},
    ]
    health = cfo.pipeline_health_check(pipelines, 500_000_000, 20_000_000)
    print(json.dumps(health, ensure_ascii=False, indent=2))

    # 测试2：政策风险评估
    print("\n【测试2】政策风险评估")
    print("-" * 50)
    policy = cfo.policy_risk_assessment(
        drug_name="PD-L1单抗",
        indication="非小细胞肺癌",
        vbp_risk_level="low",
        nrdl_probability=0.6,
        patent_expiry=2038,
        competitor_clinical_phase={"phase_iii": 2, "phase_ii": 3, "phase_i": 5},
    )
    print(json.dumps(policy, ensure_ascii=False, indent=2))

    # 测试3：合规权限设计
    print("\n【测试3】合规权限设计")
    print("-" * 50)
    permissions = cfo.compliance_permission_design()
    # 只输出层级结构
    layers = {k: list(v.keys()) for k, v in permissions["权限分层体系"].items()}
    print(json.dumps(layers, ensure_ascii=False, indent=2))

    print("\n" + "=" * 70)
    print("  所有测试完成！")
    print("=" * 70)
