import unittest
from hashlib import sha256


def valid_contract_text(**overrides):
    values = {
        "term": "固定期限，合同期限一年。",
        "probation": "试用期二个月，试用期工资为转正工资的80%。",
        "noncompete": "如乙方符合竞业限制适用条件，双方可另行签署竞业限制协议。",
        "social": "甲方和乙方依法参加社会保险，甲方按照国家及用工所在地现行规定办理和缴存住房公积金。",
    }
    values.update(overrides)
    return (
        "# 劳动合同\n"
        "甲方（用人单位）名称：__________\n"
        "乙方（劳动者）姓名：__________\n"
        f"{values['term']}\n"
        f"{values['probation']}\n"
        "工作内容：__________。工作地点：__________。\n"
        "工作时间和休息休假：标准工时制，依法休息休假。"
        "加班工资按工作日150%、休息日不能补休则200%、法定节假日300%执行。\n"
        "劳动报酬：工资人民币____元/月。\n"
        f"{values['social']}\n"
        "劳动保护和劳动条件：甲方依法提供劳动保护和劳动条件。\n"
        "解除终止：双方依法解除或终止。\n"
        f"{values['noncompete']}\n"
        "劳动争议：依法申请劳动仲裁。\n"
        "甲方（盖章）：__________\n"
        "乙方（签字）：__________\n"
    )


def full_noncompete_text(extra: str = ""):
    return (
        "乙方属于高级技术人员并实际接触商业秘密，承担竞业限制义务，"
        "竞业限制期限十二个月，范围、地域、期限与商业秘密相适应，"
        "甲方按月支付经济补偿。"
        f"{extra}"
    )


def final_facts(**overrides):
    text = overrides.pop("text", None) or valid_contract_text()
    facts = {
        "schema_version": 1,
        "document_mode": "final",
        "term_type": "fixed",
        "term_months": 12,
        "probation_months": 2,
        "probation_wage_ratio": 0.8,
        "prior_probation_used": False,
        "noncompete_mode": "reference_only",
        "noncompete_person_eligible": False,
        "secret_access_confirmed": False,
        "noncompete_months": None,
        "noncompete_compensation_confirmed": False,
        "social_insurance": "statutory",
        "contract_sha256": sha256(text.encode("utf-8")).hexdigest(),
    }
    facts.update(overrides)
    return facts


def template_facts(**overrides):
    facts = {
        "schema_version": 1,
        "document_mode": "template",
        "term_type": "template_options",
        "term_months": None,
        "probation_months": None,
        "probation_wage_ratio": None,
        "prior_probation_used": False,
        "noncompete_mode": "reference_only",
        "noncompete_person_eligible": False,
        "secret_access_confirmed": False,
        "noncompete_months": None,
        "noncompete_compensation_confirmed": False,
        "social_insurance": "statutory",
    }
    facts.update(overrides)
    return facts


class ValidateContractTest(unittest.TestCase):
    def test_allows_blank_template_with_term_options_and_probation_option(self):
        from scripts.validate_contract import validate_contract

        findings = validate_contract(
            "合同期限可选择固定期限、无固定期限或以完成一定工作任务为期限。"
            "如双方依法约定试用期，试用期自____年__月__日起至____年__月__日止。",
            facts=template_facts(),
        )

        self.assert_no_error(findings, "PROBATION_TASK_CONTRACT")

    def test_allows_full_blank_template_with_multiline_term_options_and_signature_area(self):
        from scripts.validate_contract import validate_contract

        text = (
            "# 劳动合同\n"
            "甲方（用人单位）名称：__________\n"
            "乙方（劳动者）姓名：__________\n"
            "合同期限：\n"
            "固定期限：自____年__月__日起至____年__月__日止。\n"
            "无固定期限：自____年__月__日起。\n"
            "以完成一定工作任务为期限：以__________任务完成为止。\n"
            "工作内容：__________。工作地点：__________。\n"
            "劳动报酬：人民币____元/月。\n"
            "甲方（盖章）：__________\n"
            "乙方（签字）：__________\n"
        )
        findings = validate_contract(text, facts=template_facts())

        self.assert_no_errors(findings)

    def test_allows_date_range_fixed_term_when_facts_term_months_is_duration(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(term="合同期限：固定期限，自2026年9月1日起至2027年8月31日止。")
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                term_months=12,
                term_start_date="2026-09-01",
                term_end_date="2027-08-31",
            ),
        )

        self.assert_no_errors(findings)

    def test_fixed_contract_renewal_clause_does_not_make_term_indefinite(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            term="合同期限：固定期限，合同期限一年。续订时符合条件的，双方依法签订无固定期限劳动合同。"
        )
        findings = validate_contract(text, facts=final_facts(text=text, term_type="fixed", term_months=12))

        self.assert_no_errors(findings)

    def test_plain_title_final_contract_cannot_be_marked_template(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text().replace("# 劳动合同", "劳动合同")
        findings = validate_contract(text, facts=template_facts())

        self.assert_has_error(findings, "DOCUMENT_MODE_TEXT_CONFLICT")

    def test_bold_title_final_contract_cannot_be_marked_template(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text().replace("# 劳动合同", "**劳动合同**")
        findings = validate_contract(text, facts=template_facts())

        self.assert_has_error(findings, "DOCUMENT_MODE_TEXT_CONFLICT")

    def test_final_facts_cannot_pair_with_blank_multiterm_template(self):
        from scripts.validate_contract import validate_contract

        text = (
            "# 劳动合同\n"
            "甲方（用人单位）名称：__________\n"
            "乙方（劳动者）姓名：__________\n"
            "合同期限：\n"
            "固定期限：自____年__月__日起至____年__月__日止。\n"
            "无固定期限：自____年__月__日起。\n"
            "以完成一定工作任务为期限：以__________任务完成为止。\n"
            "工作内容：__________。工作地点：__________。\n"
            "劳动报酬：人民币____元/月。\n"
            "社会保险：__________。\n"
            "劳动保护和劳动条件：__________。\n"
            "解除终止：__________。\n"
            "劳动争议：依法申请劳动仲裁。\n"
            "甲方（盖章）：__________\n"
            "乙方（签字）：__________\n"
        )
        findings = validate_contract(text, facts=final_facts(text=text, term_type="fixed", term_months=12))

        self.assert_has_error(findings, "DOCUMENT_MODE_TEXT_CONFLICT")

    def test_term_date_order_is_validated(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(term="合同期限：固定期限，自2027年8月31日起至2026年9月1日止。")
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                term_start_date="2027-08-31",
                term_end_date="2026-09-01",
            ),
        )

        self.assert_has_error(findings, "TERM_DATE_ORDER_INVALID")

    def test_term_dates_are_checked_against_facts_months(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(term="合同期限：固定期限，自2026年9月1日起至2027年8月31日止。")
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                term_months=24,
                term_start_date="2026-09-01",
                term_end_date="2027-08-31",
            ),
        )

        self.assert_has_error(findings, "TERM_FACTS_TEXT_CONFLICT")

    def test_allows_noncompete_reference_only_clause(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="如乙方符合竞业限制适用条件，双方可另行签署竞业限制协议。")
        findings = validate_contract(text, facts=final_facts(text=text, noncompete_mode="reference_only"))

        self.assert_no_errors(findings)

    def test_blocks_legal_holiday_comp_time_overtime_clause(self):
        from scripts.validate_contract import validate_contract

        findings = validate_contract("法定节假日安排加班的，甲方可以安排补休或支付加班工资。")

        self.assert_has_error(findings, "OVERTIME_LEGAL_HOLIDAY_COMP_TIME")

    def test_blocks_noncompete_without_secret_access_fact(self):
        from scripts.validate_contract import validate_contract

        findings = validate_contract(
            "乙方承担竞业限制义务，竞业限制期限为二年，地域范围为中国境内，"
            "甲方每月支付经济补偿人民币____元。",
            facts=final_facts(
                text="乙方承担竞业限制义务，竞业限制期限为二年，地域范围为中国境内，甲方每月支付经济补偿人民币____元。",
                noncompete_mode="full",
                noncompete_person_eligible=True,
                noncompete_months=24,
                noncompete_compensation_confirmed=True,
            ),
        )

        self.assert_has_error(findings, "NONCOMPETE_MISSING_SECRET_ACCESS")

    def test_blocks_sent_equals_served_delivery_clause(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="甲方通过电子邮件发送至乙方确认邮箱的，视为送达。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "DELIVERY_SENT_EQUALS_SERVED")

    def test_blocks_probation_for_task_based_contract(self):
        from scripts.validate_contract import validate_contract

        findings = validate_contract(
            "以完成一定工作任务为期限的劳动合同，试用期为一个月。",
            facts=final_facts(term_type="task", term_months=None, probation_months=1),
        )

        self.assert_has_error(findings, "PROBATION_TASK_CONTRACT")

    def test_blocks_general_labor_penalty(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="乙方违反本合同任何约定，应支付违约金5万元。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "GENERAL_LABOR_PENALTY")

    def test_blocks_social_insurance_waiver_paid_as_wages(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(social="乙方自愿放弃缴纳社保，单位承担部分随工资发放。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "SOCIAL_INSURANCE_WAIVER")

    def test_blocks_excessive_probation_for_one_year_contract_from_facts(self):
        from scripts.validate_contract import validate_contract

        findings = validate_contract(
            "合同期限一年，试用期三个月。",
            facts=final_facts(term_months=12, probation_months=3),
        )

        self.assert_has_error(findings, "PROBATION_EXCEEDS_LEGAL_MAX")

    def test_blocks_legal_holiday_comp_time_even_when_rates_present(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            probation="试用期二个月，试用期工资为转正工资的80%。",
            noncompete="法定节假日加班安排补休。加班工资标准为150%、200%、300%。",
        )
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "OVERTIME_LEGAL_HOLIDAY_COMP_TIME")

    def test_allows_correct_overtime_rates_with_rest_day_comp_time_clause(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text()
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_no_errors(findings)

    def test_final_contract_requires_structured_facts(self):
        from scripts.validate_contract import validate_contract

        findings = validate_contract("合同期限一年，试用期三个月。")

        self.assert_has_error(findings, "FACTS_REQUIRED")

    def test_rejects_non_dict_facts(self):
        from scripts.validate_contract import validate_contract

        findings = validate_contract("劳动合同", facts=[])

        self.assert_has_error(findings, "FACTS_NOT_OBJECT")

    def test_rejects_unknown_enum_and_negative_term(self):
        from scripts.validate_contract import validate_contract

        findings = validate_contract(
            "劳动合同",
            facts=final_facts(term_type="seasonal", term_months=-1),
        )

        self.assert_has_error(findings, "FACTS_INVALID_ENUM")
        self.assert_has_error(findings, "FACTS_INVALID_NUMBER")

    def test_rejects_string_months_without_type_error(self):
        from scripts.validate_contract import validate_contract

        findings = validate_contract(
            "劳动合同",
            facts=final_facts(term_months="12", probation_months="2"),
        )

        self.assert_has_error(findings, "FACTS_INVALID_TYPE")

    def test_rejects_string_boolean_secret_access(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            noncompete="乙方承担竞业限制义务，竞业限制期限为二年，范围与商业秘密相适应，甲方支付经济补偿。"
        )
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                noncompete_mode="full",
                noncompete_person_eligible=True,
                noncompete_months=24,
                noncompete_compensation_confirmed=True,
                secret_access_confirmed="false",
            ),
        )

        self.assert_has_error(findings, "FACTS_INVALID_TYPE")
        self.assert_has_error(findings, "NONCOMPETE_MISSING_SECRET_ACCESS")

    def test_rejects_non_statutory_social_insurance_fact(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text()
        findings = validate_contract(text, facts=final_facts(text=text, social_insurance="cash_allowance"))

        self.assert_has_error(findings, "SOCIAL_INSURANCE_FACT_INVALID")

    def test_facts_reference_only_cannot_hide_full_noncompete_text(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            noncompete="乙方承担竞业限制义务，竞业限制期限为二年，甲方每月支付经济补偿人民币____元。"
        )
        findings = validate_contract(text, facts=final_facts(text=text, noncompete_mode="reference_only"))

        self.assert_has_error(findings, "NONCOMPETE_FACTS_TEXT_CONFLICT")

    def test_facts_without_probation_cannot_hide_probation_text(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(probation="试用期三个月。")
        findings = validate_contract(text, facts=final_facts(text=text, probation_months=0))

        self.assert_has_error(findings, "PROBATION_FACTS_TEXT_CONFLICT")

    def test_blocks_legal_holiday_paid_only_200_percent(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="法定节假日加班支付200%工资。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "OVERTIME_LEGAL_HOLIDAY_UNDERPAID")

    def test_allows_legal_holiday_300_percent_plus_extra_rest(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="法定节假日加班支付300%工资，并额外安排调休。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_no_errors(findings)

    def test_allows_system_confirmed_delivery_arrival(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="邮件发出并经系统确认到达后视为送达。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_no_errors(findings)

    def test_blocks_repeat_probation(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(probation="同一用人单位与同一劳动者再次约定试用期。")
        findings = validate_contract(text, facts=final_facts(text=text, prior_probation_used=True))

        self.assert_has_error(findings, "PROBATION_REPEAT")

    def test_blocks_probation_wage_under_80_percent(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(probation="试用期工资为转正工资的50%。")
        findings = validate_contract(text, facts=final_facts(text=text, probation_wage_ratio=0.5))

        self.assert_has_error(findings, "PROBATION_WAGE_RATIO_LOW")

    def test_blocks_conditional_housing_fund_payment(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(social="甲方可根据经营情况缴存住房公积金。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "HOUSING_FUND_CONDITIONAL")

    def test_blocks_employee_bears_all_social_insurance(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(social="社会保险费用全部由劳动者承担。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "SOCIAL_INSURANCE_WAIVER")

    def test_blocks_generic_fixed_penalty_without_any_clause(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="乙方须支付违约金人民币50000元。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "GENERAL_LABOR_PENALTY")

    def test_blocks_unconditional_job_and_pay_adjustment(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="甲方调整岗位及薪酬，乙方应无条件服从。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "ARBITRARY_JOB_ADJUSTMENT")

    def test_rejects_required_facts_that_are_all_null(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text()
        findings = validate_contract(
            text,
            facts={field: None for field in (
                "schema_version",
                "document_mode",
                "term_type",
                "term_months",
                "probation_months",
                "probation_wage_ratio",
                "prior_probation_used",
                "noncompete_mode",
                "noncompete_person_eligible",
                "secret_access_confirmed",
                "noncompete_months",
                "noncompete_compensation_confirmed",
                "social_insurance",
                "contract_sha256",
            )},
        )

        self.assert_has_error(findings, "FACTS_INVALID_TYPE")

    def test_template_mode_cannot_pair_with_final_contract_body(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text()
        findings = validate_contract(text, facts=template_facts())

        self.assert_has_error(findings, "DOCUMENT_MODE_TEXT_CONFLICT")

    def test_probation_months_must_match_contract_body(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(probation="试用期三个月，试用期工资为转正工资的80%。")
        findings = validate_contract(text, facts=final_facts(text=text, probation_months=2))

        self.assert_has_error(findings, "PROBATION_FACTS_TEXT_CONFLICT")

    def test_term_type_must_match_contract_body(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(term="固定期限，合同期限一年。")
        findings = validate_contract(text, facts=final_facts(text=text, term_type="indefinite", term_months=None))

        self.assert_has_error(findings, "TERM_FACTS_TEXT_CONFLICT")

    def test_noncompete_none_cannot_hide_full_noncompete_text(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            noncompete="乙方离职后二年内不得到与甲方有竞争关系的单位任职，甲方支付经济补偿。"
        )
        findings = validate_contract(text, facts=final_facts(text=text, noncompete_mode="none"))

        self.assert_has_error(findings, "NONCOMPETE_FACTS_TEXT_CONFLICT")

    def test_noncompete_full_requires_body_clause(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="双方未约定竞业限制义务。")
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                noncompete_mode="full",
                noncompete_person_eligible=True,
                secret_access_confirmed=True,
                noncompete_months=12,
                noncompete_compensation_confirmed=True,
            ),
        )

        self.assert_has_error(findings, "NONCOMPETE_FACTS_TEXT_CONFLICT")

    def test_fixed_term_requires_positive_term_months(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text()
        findings = validate_contract(text, facts=final_facts(text=text, term_months=None))

        self.assert_has_error(findings, "FACTS_CONDITIONAL_REQUIRED")

    def test_body_probation_wage_ratio_under_80_is_blocked_without_ratio_fact(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(probation="试用期工资为转正工资的75%。")
        findings = validate_contract(text, facts=final_facts(text=text, probation_wage_ratio=None))

        self.assert_has_error(findings, "PROBATION_WAGE_RATIO_LOW")

    def test_probation_requires_wage_ratio_fact(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text()
        findings = validate_contract(text, facts=final_facts(text=text, probation_wage_ratio=None))

        self.assert_has_error(findings, "FACTS_CONDITIONAL_REQUIRED")

    def test_final_requires_contract_hash(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text()
        facts = final_facts(text=text)
        facts.pop("contract_sha256")
        findings = validate_contract(text, facts=facts)

        self.assert_has_error(findings, "FACTS_MISSING_FIELD")

    def test_blocks_cross_sentence_legal_holiday_comp_time(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="法定节假日安排加班。甲方可以安排调休。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "OVERTIME_LEGAL_HOLIDAY_COMP_TIME")

    def test_blocks_legal_holiday_paid_only_250_percent(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="法定节假日加班支付250%工资。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "OVERTIME_LEGAL_HOLIDAY_UNDERPAID")

    def test_blocks_final_contract_missing_required_sections_as_errors(self):
        from scripts.validate_contract import validate_contract

        text = "# 劳动合同\n甲方（用人单位）名称：__________\n合同期限一年。\n"
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "REQUIRED_PAY")
        self.assert_has_error(findings, "REQUIRED_SOCIAL_INSURANCE")
        self.assert_has_error(findings, "REQUIRED_PROTECTION")
        self.assert_has_error(findings, "REQUIRED_DISPUTE")
        self.assert_has_error(findings, "REQUIRED_SIGNATURE")

    def test_subject_work_and_signature_require_all_parts(self):
        from scripts.validate_contract import validate_contract

        text = (
            "# 劳动合同\n"
            "甲方（用人单位）名称：__________\n"
            "合同期限一年。\n"
            "工作内容：__________。\n"
            "工作时间和休息休假：标准工时制，依法休息休假。\n"
            "劳动报酬：工资人民币____元/月。\n"
            "社会保险：甲方依法缴纳社会保险。\n"
            "劳动保护和劳动条件：甲方依法提供劳动保护和劳动条件。\n"
            "解除终止：双方依法解除或终止。\n"
            "劳动争议：依法申请劳动仲裁。\n"
            "甲方（盖章）：__________\n"
        )
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "REQUIRED_SUBJECTS")
        self.assert_has_error(findings, "REQUIRED_WORK")
        self.assert_has_error(findings, "REQUIRED_SIGNATURE")

    def test_noncompete_body_must_include_compensation_even_when_facts_confirm_it(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            noncompete=(
                "乙方属于高级技术人员并实际接触商业秘密，承担竞业限制义务，"
                "竞业限制期限十二个月，范围、地域、期限与商业秘密相适应。"
            )
        )
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                noncompete_mode="full",
                noncompete_person_eligible=True,
                secret_access_confirmed=True,
                noncompete_months=12,
                noncompete_compensation_confirmed=True,
            ),
        )

        self.assert_has_error(findings, "NONCOMPETE_MISSING_COMPENSATION")

    def test_noncompete_body_must_include_term_even_when_facts_has_months(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            noncompete=(
                "乙方属于高级技术人员并实际接触商业秘密，承担竞业限制义务，"
                "范围、地域、期限与商业秘密相适应，甲方按月支付经济补偿。"
            )
        )
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                noncompete_mode="full",
                noncompete_person_eligible=True,
                secret_access_confirmed=True,
                noncompete_months=12,
                noncompete_compensation_confirmed=True,
            ),
        )

        self.assert_has_error(findings, "NONCOMPETE_MISSING_TERM")

    def test_blocks_general_penalty_even_when_service_period_is_mentioned_as_exception(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="除培训服务期外，任何违约均支付5万元违约金。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "GENERAL_LABOR_PENALTY")

    def test_allows_paid_300_percent_and_rest_without_legal_holiday_phrase(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="法定节假日安排工作的，已支付300%工资并安排调休。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_no_errors(findings)

    def test_blocks_legal_holiday_no_overtime_pay(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="法定节假日安排加班的，不另行支付加班工资。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "OVERTIME_LEGAL_HOLIDAY_NO_PAY")

    def test_legal_holiday_200_percent_not_hidden_by_unrelated_500_percent(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="法定节假日加班工资为200%，绩效考核系数最高500%。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "OVERTIME_LEGAL_HOLIDAY_UNDERPAID")

    def test_blocks_delivery_even_when_system_confirms_not_arrived(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="未经系统确认到达也视为送达。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "DELIVERY_SENT_EQUALS_SERVED")

    def test_blocks_employee_self_paid_social_insurance(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(social="乙方自行缴纳社会保险。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "SOCIAL_INSURANCE_WAIVER")

    def test_false_materials_conditions_must_be_in_same_clause(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            noncompete=(
                "录用资料应与录用直接相关并影响录用决定。"
                "乙方提供虚假资料的，甲方可以立即解除本合同。"
            )
        )
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "FALSE_MATERIALS_OVERBROAD_TERMINATION")

    def test_blocks_voluntary_non_participation_in_social_insurance(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(social="乙方自愿不参加社会保险。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "SOCIAL_INSURANCE_WAIVER")

    def test_blocks_noncompete_without_literal_noncompete_keyword(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="乙方离职后二十五个月内不得去竞争单位任职，甲方支付经济补偿。")
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                noncompete_mode="full",
                noncompete_person_eligible=True,
                secret_access_confirmed=True,
                noncompete_months=25,
                noncompete_compensation_confirmed=True,
            ),
        )

        self.assert_has_error(findings, "NONCOMPETE_OVER_24_MONTHS")

    def test_later_bad_delivery_clause_is_not_hidden_by_earlier_valid_clause(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="邮件发出并经系统确认到达后视为送达。短信发出即视为送达。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "DELIVERY_SENT_EQUALS_SERVED")

    def test_allows_noncompete_liquidated_damages(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            noncompete=(
                full_noncompete_text("乙方违反竞业限制义务的，应支付违约金人民币50000元。")
            )
        )
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                noncompete_mode="full",
                noncompete_person_eligible=True,
                secret_access_confirmed=True,
                noncompete_months=12,
                noncompete_compensation_confirmed=True,
            ),
        )

        self.assert_no_errors(findings)

    def test_allows_negative_arbitrary_adjustment_sentence(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="甲方不得随时调整乙方岗位。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_no_errors(findings)

    def test_allows_negative_social_housing_and_delivery_sentences(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            social="乙方不得自行缴纳社会保险。甲方不得根据经营情况选择是否缴存住房公积金。",
            noncompete="甲方不得仅以发送视为送达。",
        )
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_no_errors(findings)

    def test_blocks_legal_holiday_no_overtime_fee_synonym(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="法定节假日安排工作的，不计发加班费。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "OVERTIME_LEGAL_HOLIDAY_NO_PAY")

    def test_blocks_legal_holiday_two_times_pay(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="法定节假日安排加班的，支付二倍工资。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "OVERTIME_LEGAL_HOLIDAY_UNDERPAID")

    def test_noncompete_compensation_must_be_inside_noncompete_clause(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            noncompete="乙方属于高级技术人员并实际接触商业秘密，承担竞业限制义务，竞业限制期限十二个月，范围、地域、期限与商业秘密相适应。",
        ).replace("解除终止：双方依法解除或终止。", "解除终止：双方依法解除或终止，甲方依法支付经济补偿。").replace(
            "劳动报酬：工资人民币____元/月。", "劳动报酬：每月工资人民币____元。"
        )
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                noncompete_mode="full",
                noncompete_person_eligible=True,
                secret_access_confirmed=True,
                noncompete_months=12,
                noncompete_compensation_confirmed=True,
            ),
        )

        self.assert_has_error(findings, "NONCOMPETE_MISSING_COMPENSATION")

    def test_noncompete_proportionality_must_be_inside_noncompete_clause(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(
            noncompete="乙方属于高级技术人员并实际接触商业秘密，承担竞业限制义务，竞业限制期限十二个月，甲方按月支付经济补偿。",
        ).replace("解除终止：双方依法解除或终止。", "解除终止：双方应在合理范围内依法解除或终止。")
        findings = validate_contract(
            text,
            facts=final_facts(
                text=text,
                noncompete_mode="full",
                noncompete_person_eligible=True,
                secret_access_confirmed=True,
                noncompete_months=12,
                noncompete_compensation_confirmed=True,
            ),
        )

        self.assert_has_error(findings, "NONCOMPETE_MISSING_PROPORTIONALITY")

    def test_keyword_stuffing_does_not_satisfy_required_sections(self):
        from scripts.validate_contract import validate_contract

        text = (
            "# 劳动合同\n"
            "甲方乙方合同期限工作内容工作地点工作时间休息休假劳动报酬工资社会保险劳动保护劳动条件解除终止劳动争议仲裁甲方（盖章）乙方（签字）。\n"
        )
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "REQUIRED_SUBJECTS")
        self.assert_has_error(findings, "REQUIRED_WORK")
        self.assert_has_error(findings, "REQUIRED_PAY")

    def test_blocks_general_penalty_without_any_word(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="乙方违反本合同约定，支付违约金五万元。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "GENERAL_LABOR_PENALTY")

    def test_blocks_untrue_materials_unilateral_termination_synonym(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="乙方提交材料不实即可单方解除。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "FALSE_MATERIALS_OVERBROAD_TERMINATION")

    def test_blocks_unconfirmed_arrival_deemed_served_synonym(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(noncompete="未确认到达亦视作送达。")
        findings = validate_contract(text, facts=final_facts(text=text))

        self.assert_has_error(findings, "DELIVERY_SENT_EQUALS_SERVED")

    def test_probation_wage_ratio_without_probation_is_invalid(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text(probation="双方不约定试用期。")
        findings = validate_contract(text, facts=final_facts(text=text, probation_months=0, probation_wage_ratio=0.8))

        self.assert_has_error(findings, "FACTS_CONDITIONAL_REQUIRED")

    def test_rejects_nan_number_fact(self):
        from scripts.validate_contract import validate_contract

        text = valid_contract_text()
        findings = validate_contract(text, facts=final_facts(text=text, term_months=float("nan")))

        self.assert_has_error(findings, "FACTS_INVALID_NUMBER")

    def test_contract_hash_must_match_text_when_provided(self):
        from scripts.validate_contract import validate_contract

        text = "劳动合同"
        findings = validate_contract(text, facts=final_facts(contract_sha256=sha256(b"other").hexdigest()))

        self.assert_has_error(findings, "FACTS_CONTRACT_HASH_MISMATCH")

    def assert_has_error(self, findings, code):
        matching = [
            finding for finding in findings
            if finding.code == code and finding.severity == "error"
        ]
        self.assertTrue(matching, f"Expected error {code}, got {findings!r}")

    def assert_no_error(self, findings, code):
        matching = [
            finding for finding in findings
            if finding.code == code and finding.severity == "error"
        ]
        self.assertFalse(matching, f"Unexpected error {code}: {findings!r}")

    def assert_no_errors(self, findings):
        errors = [finding for finding in findings if finding.severity == "error"]
        self.assertFalse(errors, f"Unexpected errors: {errors!r}")


if __name__ == "__main__":
    unittest.main()
