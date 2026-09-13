#!/usr/bin/env python3
"""
医药财务总监·战略顾问 — 技能测试套件
====================================
测试所有16个模型和5大核心职责
"""

import sys
import json
import traceback

# 添加脚本目录到路径
sys.path.insert(0, ".")

from scripts.pharma_valuation_models import (
    PharmaValuationModels,
    RnpvInput, PeakSalesInput, BDDealInput, MatureProductInput,
    ClinicalPhase, TherapeuticArea,
    quick_rnpv, quick_bd_deal,
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


def run_test(name, func):
    """运行单个测试并报告结果"""
    try:
        print(f"\n  [{name}] ... ", end="")
        result = func()
        if isinstance(result, dict) and "error" in str(result).lower():
            print(f"⚠️ 警告")
            return "warning", str(result)[:200]
        print("✅ 通过")
        return "pass", None
    except Exception as e:
        print(f"❌ 失败: {e}")
        return "fail", traceback.format_exc()


def main():
    print("=" * 70)
    print("  医药财务总监·战略顾问 — 完整测试套件")
    print("=" * 70)

    results = {}
    pvm = PharmaValuationModels()
    pfm = PharmaFinancialModels()
    pcm = PharmaCashModels()

    # ==============================
    # 估值模型测试（4个）
    # ==============================
    print("\n📊 估值模型测试 (4个)")

    def test_rnpv():
        r = pvm.rnpv_valuation(RnpvInput(
            drug_name="Test-PD1",
            current_phase=ClinicalPhase.PHASE_II,
            therapeutic_area=TherapeuticArea.ONCOLOGY,
            years_to_launch=5.0, peak_sales_cny=2_000_000_000,
        ))
        assert r.rnpv != 0, "rNPV不应为0"
        return r.to_dict()

    def test_peak_sales():
        r = pvm.peak_sales_estimation(PeakSalesInput(
            drug_name="Test", indication="NSCLC",
            target_population=1_400_000_000, incidence_rate=45.6,
            annual_treatment_cost_cny=80_000,
        ))
        assert r.peak_sales_cny > 0, "峰值销售应>0"
        return r.to_dict()

    def test_bd_deal():
        r = pvm.bd_deal_analysis(BDDealInput(
            drug_name="Test-BD", deal_type="license-in",
            upfront_cny=200_000_000,
            milestones=[{"stage": "phase_3", "amount": 100_000_000, "prob": 0.5}],
            royalty_rate=0.12, peak_sales_cny=3_000_000_000,
        ))
        assert r.total_deal_value > 0, "交易总对价应>0"
        return r.to_dict()

    def test_mature_product():
        r = pvm.mature_product_valuation(MatureProductInput(
            drug_name="Test-Mature", generic_name="test",
            current_annual_sales_cny=500_000_000, years_to_patent_expiry=2,
        ))
        assert "产品剩余价值NPV（万元）" in r
        return r

    results["rNPV估值"] = run_test("rNPV估值", test_rnpv)
    results["峰值销售预测"] = run_test("峰值销售预测", test_peak_sales)
    results["BD交易分析"] = run_test("BD交易分析", test_bd_deal)
    results["成熟产品估值"] = run_test("成熟产品估值", test_mature_product)

    # ==============================
    # 财务模型测试（7个）
    # ==============================
    print("\n📊 财务模型测试 (7个)")

    def test_pharma_ratio():
        r = pfm.pharma_ratio_analysis(PharmaRatioInput(
            company_name="TestCo", drug_type=DrugType.INNOVATIVE,
            revenue=3_000_000_000, cost_of_goods=600_000_000,
            rd_expense=800_000_000, selling_expense=1_000_000_000,
            admin_expense=300_000_000, operating_profit=300_000_000,
            net_profit=250_000_000, total_assets=7_000_000_000,
            total_equity=3_500_000_000, total_liabilities=3_500_000_000,
            rd_headcount=500, total_headcount=2000,
            n_pipeline_drugs=10, n_clinical_phase_drugs=4,
        ))
        assert "毛利率" in r
        return r

    def test_roe_decomp():
        r = pfm.pharma_roe_decomposition(
            "TestCo", DrugType.INNOVATIVE, 0.08, 0.40, 2.0,
            rd_leverage=2.5,
        )
        assert "ROE" in r
        return r

    def test_clinical_cf():
        r = pfm.clinical_cash_flow_analysis(CashFlowInput(
            company_name="TestBiotech", current_cash=500_000_000,
            monthly_burn_rate=20_000_000, monthly_rd_spend=14_000_000,
            monthly_admin_spend=6_000_000, next_milestone_payment=50_000_000,
        ))
        assert "现金跑道（月）" in r
        return r

    def test_lifecycle():
        r = pfm.drug_lifecycle_forecast(LifecycleInput(
            drug_name="Test-Drug", launch_year=2027, peak_sales_cny=2_500_000_000,
            compound_patent_expiry=2038,
        ))
        assert "全生命周期NPV（万元）" in r
        return r

    def test_pricing_sens():
        r = pfm.pricing_sensitivity_analysis(PricingSensitivityInput(
            drug_name="Test-Drug", base_price_cny=80_000, base_peak_patients=50000,
        ))
        assert "敏感性分析（龙卷风图数据）" in r
        return r

    def test_swot():
        r = pfm.market_access_swot(
            "Test-Drug", "NSCLC",
            strengths=["靶点创新性", "临床数据优效性"],
            weaknesses=["给药途径不便"],
            opportunities=["CDE加速审评", "NRDL谈判窗口"],
            threats=["集采扩面风险", "竞品专利到期"],
        )
        assert "SWOT矩阵" in r
        return r

    def test_patent_cliff():
        r = pfm.patent_cliff_alert(
            "Test-Drug", 300_000_000, 2029, revenue_contribution=0.45,
        )
        assert "预警状态" in r
        return r

    results["药企比率分析"] = run_test("药企比率分析", test_pharma_ratio)
    results["ROE分解"] = run_test("ROE分解", test_roe_decomp)
    results["临床现金流"] = run_test("临床现金流", test_clinical_cf)
    results["药物生命周期"] = run_test("药物生命周期", test_lifecycle)
    results["定价敏感性"] = run_test("定价敏感性", test_pricing_sens)
    results["SWOT分析"] = run_test("SWOT分析", test_swot)
    results["专利悬崖预警"] = run_test("专利悬崖预警", test_patent_cliff)

    # ==============================
    # 资金管理模型测试（5个）
    # ==============================
    print("\n📊 资金管理模型测试 (5个)")

    def test_drug_ccc():
        r = pcm.drug_cash_conversion_cycle(DrugInventoryInput(
            company_name="TestPharma",
            api_inventory_days=90, production_cycle_days=45,
            finished_goods_days=60, hospital_receivables_days=270,
        ))
        assert "净现金周转周期（CCC）" in r
        return r

    def test_rd_reserve():
        r = pcm.rd_cash_reserve(RDCashReserveInput(
            company_name="TestBiotech", monthly_burn_rate=20_000_000,
            next_milestone_payment=50_000_000, clinical_phase=DevelopmentPhase.PHASE_II,
        ))
        assert "现金储备建议" in r
        return r

    def test_gmp_inv():
        r = pcm.gmp_inventory_management(GMPInventoryInput(
            company_name="TestPharma",
            products=[
                {"name": "Test-Bio", "category": "A_冷链生物药", "value": 50_000_000,
                 "shelf_life_months": 18, "monthly_consumption": 3_000_000},
            ],
        ))
        assert "产品分类管理" in r
        return r

    def test_hospital_credit():
        r = pcm.hospital_credit_rating(HospitalCreditInput(
            customers=[
                {"name": "Test-Hospital", "grade": HospitalGrade.GRADE_3A,
                 "payment_history": "on_time", "annual_purchase": 50_000_000,
                 "province_gdp_rank": 1, "insurance_settlement_cycle_months": 3},
            ],
        ))
        assert "客户评级结果" in r
        return r

    def test_phase_gate():
        r = pcm.phase_gate_budget(PhaseGateBudgetInput(
            drug_name="Test-Drug", current_phase=DevelopmentPhase.PHASE_II,
            phases=[
                {"phase": "phase_ii", "duration_months": 12, "monthly_cost": 8_000_000},
            ],
            current_cash=300_000_000,
        ))
        assert "资金预警" in r
        return r

    results["药品CCC"] = run_test("药品CCC", test_drug_ccc)
    results["研发现金储备"] = run_test("研发现金储备", test_rd_reserve)
    results["GMP库存"] = run_test("GMP库存", test_gmp_inv)
    results["医院信用"] = run_test("医院信用", test_hospital_credit)
    results["Phase-Gate预算"] = run_test("Phase-Gate预算", test_phase_gate)

    # ==============================
    # 结果汇总
    # ==============================
    print("\n" + "=" * 70)
    print("  测试结果汇总")
    print("=" * 70)

    total = len(results)
    passes = sum(1 for v in results.values() if v[0] == "pass")
    warnings = sum(1 for v in results.values() if v[0] == "warning")
    fails = sum(1 for v in results.values() if v[0] == "fail")

    for name, (status, _) in results.items():
        icon = {"pass": "✅", "warning": "⚠️", "fail": "❌"}[status]
        print(f"  {icon} {name}")

    print(f"\n  总计: {total} 项测试")
    print(f"  通过: {passes} | 警告: {warnings} | 失败: {fails}")

    if fails == 0:
        print("\n  🎉 所有测试通过！医药财务总监·战略顾问技能包可用。")
    else:
        print(f"\n  ⚠️ {fails} 项测试失败，请检查相关模型代码。")

    print("=" * 70)

    return fails == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
