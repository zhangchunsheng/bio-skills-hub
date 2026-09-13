# Legal Baseline

最后复核日期：2026-08-27。

本文件只记录生成和导出前必须遵守的法律底线。具体合同文本仍以 `template.md` 为主，确定性校验以 `scripts/validate_contract.py` 为准。

本 skill 生成和校验不等同于律师出具法律意见或完整合规审核；导出前校验只阻断确定性错误和高风险固定表达。

## 主要依据

- 《中华人民共和国劳动法》：1995-01-01 施行，现行修正版本；重点参考第四十四条加班工资。
- 《中华人民共和国劳动合同法》：2008-01-01 施行，2013-07-01 修正施行；重点参考第十七条、十九条、二十条、三十八条、三十九条、四十条、四十一条、四十二条、四十三条、四十五条、四十六条、四十七条、五十条、二十三条、二十四条。
- 《住房公积金管理条例》：1999-04-03 发布，2019-03-24 修订；重点参考单位办理缴存登记、按时足额缴存等规则。
- 《最高人民法院关于审理劳动争议案件适用法律问题的解释（二）》：2025-09-01 施行；重点参考竞业限制关于劳动者是否知悉、接触商业秘密和竞业限制范围、地域、期限与商业秘密相适应的裁判规则。

参考链接：

- https://www.gov.cn/banshi/2005-05/25/content_905.htm
- https://www.gjxfj.gov.cn/gjxfj/xxgk/fgwj/flfg/webinfo/2016/03/1460585589931971.htm
- https://www.gov.cn/gongbao/content/2019/content_5468867.htm
- https://www.court.gov.cn/fabu/xiangqing/472691.html

## 加班工资

- 工作日延长工作时间：支付不低于工资 150% 的工资报酬。
- 休息日安排工作且不能安排补休：支付不低于工资 200% 的工资报酬。
- 法定休假日安排工作：支付不低于工资 300% 的工资报酬，不得以补休替代该项法定加班工资。

## 试用期

- 以完成一定工作任务为期限的劳动合同不得约定试用期。
- 劳动合同期限不满三个月的，不得约定试用期。
- 同一用人单位与同一劳动者只能约定一次试用期。
- 试用期工资不得低于本单位相同岗位最低档工资或者劳动合同约定工资的 80%，且不得低于用人单位所在地最低工资标准。

## 竞业限制

- 竞业限制人员限于高级管理人员、高级技术人员和其他负有保密义务的人员。
- 完整竞业限制条款还必须有劳动者实际知悉或接触商业秘密、与知识产权相关保密事项的事实基础。
- 竞业限制范围、地域、期限应与劳动者知悉或接触的商业秘密及相关保密事项相适应。
- 未确认秘密接触事实时，只保留专项协议承接，不直接生成完整竞业限制义务。
- 竞业限制期限不得超过二年，并应约定经济补偿。

## 解除终止

- “提供虚假录用资料”不能被泛化写成当然即时解除；应限于重要、与录用直接相关、足以影响录用决定并有证据支持的资料，并衔接欺诈致合同无效、试用期不符合录用条件或严重违反依法有效规章制度等法定依据。
- 解除终止条款应同时保留劳动者依法解除、用人单位限制解除、工会通知、法定顺延、经济补偿和违法解除责任边界。

## 文书送达

- 内部管理文件、解除终止通知、劳动争议仲裁/诉讼送达不得混同。
- 电子或邮寄送达不应简单写成“已发送即视为送达”；应以签收、到达、系统可验证读达、可证明实际收悉，或依法有效的拒收/退回规则为依据。

## 住房公积金

- 按照国家及用工所在地现行规定办理和缴存住房公积金。
- 不写成“可依法缴存”这一容易被理解为任意可选的表达。

## 个人信息

- 劳动合同必备主体信息以用人单位名称/住所/法定代表人或主要负责人，以及劳动者姓名/住址/居民身份证或其他有效身份证件号码为基础。
- 紧急联系人、紧急联系人关系、紧急联系人电话不是劳动合同必备字段；如需收集，应作为可选员工信息表字段，并说明用途和最小必要原则。

## 规则追踪表

| Rule ID | 规则 | 校验函数 | 正例测试 | 反例测试 |
| --- | --- | --- | --- | --- |
| FACTS_SCHEMA | facts 必须为 schema_version=1 的 JSON object，字段类型、枚举、范围合法 | validate_facts_schema | test_cli_accepts_structured_facts_file | test_rejects_non_dict_facts / test_rejects_unknown_enum_and_negative_term / test_rejects_string_months_without_type_error / test_rejects_required_facts_that_are_all_null |
| FACTS_CONDITIONAL | final/template、期限类型、试用期、竞业限制和合同 hash 必须满足条件约束 | validate_facts_schema | test_cli_accepts_structured_facts_file | test_fixed_term_requires_positive_term_months / test_probation_requires_wage_ratio_fact / test_probation_wage_ratio_without_probation_is_invalid / test_final_requires_contract_hash / test_rejects_nan_number_fact |
| FACTS_REQUIRED | 最终合同导出必须提供结构化 facts；空白模板用 document_mode=template | validate_facts_schema | test_allows_blank_template_with_term_options_and_probation_option | test_final_contract_requires_structured_facts / test_cli_requires_facts_for_export |
| FACTS_CONSISTENCY | facts 不能压制或背离正文中的期限、试用期、竞业限制和工资比例 | validate_text_facts_consistency / validate_probation / validate_noncompete | test_allows_noncompete_reference_only_clause / test_fixed_contract_renewal_clause_does_not_make_term_indefinite / test_allows_date_range_fixed_term_when_facts_term_months_is_duration | test_template_mode_cannot_pair_with_final_contract_body / test_plain_title_final_contract_cannot_be_marked_template / test_bold_title_final_contract_cannot_be_marked_template / test_final_facts_cannot_pair_with_blank_multiterm_template / test_term_type_must_match_contract_body / test_term_date_order_is_validated / test_term_dates_are_checked_against_facts_months / test_probation_months_must_match_contract_body / test_noncompete_none_cannot_hide_full_noncompete_text / test_noncompete_full_requires_body_clause |
| REQUIRED_001 | final 合同必备字段组和双方签署区缺失应阻断，不能靠关键词堆砌通过 | validate_required_sections | test_cli_accepts_structured_facts_file | test_blocks_final_contract_missing_required_sections_as_errors / test_subject_work_and_signature_require_all_parts / test_keyword_stuffing_does_not_satisfy_required_sections |
| OVERTIME_001 | 法定节假日加班工资不得低于 300%，不得以补休替代 | validate_overtime | test_allows_legal_holiday_300_percent_plus_extra_rest / test_allows_paid_300_percent_and_rest_without_legal_holiday_phrase | test_blocks_legal_holiday_comp_time_overtime_clause / test_blocks_cross_sentence_legal_holiday_comp_time / test_blocks_legal_holiday_paid_only_200_percent / test_blocks_legal_holiday_paid_only_250_percent / test_blocks_legal_holiday_no_overtime_pay / test_blocks_legal_holiday_no_overtime_fee_synonym / test_blocks_legal_holiday_two_times_pay / test_legal_holiday_200_percent_not_hidden_by_unrelated_500_percent |
| PROBATION_001 | 试用期按合同期限分档，且不得重复约定 | validate_probation | test_allows_blank_template_with_term_options_and_probation_option | test_blocks_excessive_probation_for_one_year_contract_from_facts / test_blocks_repeat_probation |
| PROBATION_002 | 试用期工资不得低于约定工资 80% | validate_probation | test_cli_accepts_structured_facts_file | test_blocks_probation_wage_under_80_percent / test_body_probation_wage_ratio_under_80_is_blocked_without_ratio_fact |
| NONCOMPETE_001 | 完整竞业限制须有适格人员、秘密接触事实、补偿、期限和范围比例性，且必须在竞业上下文内成立 | validate_noncompete | test_allows_noncompete_liquidated_damages | test_blocks_noncompete_without_secret_access_fact / test_rejects_string_boolean_secret_access / test_blocks_noncompete_without_literal_noncompete_keyword / test_noncompete_compensation_must_be_inside_noncompete_clause / test_noncompete_proportionality_must_be_inside_noncompete_clause |
| SOCIAL_001 | 社保依法缴纳，不得放弃、替代或全部转嫁劳动者；否定性禁止句不误报 | validate_facts_schema / validate_prohibited_patterns | test_cli_accepts_structured_facts_file / test_allows_negative_social_housing_and_delivery_sentences | test_blocks_social_insurance_waiver_paid_as_wages / test_blocks_employee_bears_all_social_insurance / test_blocks_voluntary_non_participation_in_social_insurance / test_blocks_employee_self_paid_social_insurance |
| HOUSING_001 | 住房公积金不得写成经营情况决定的可选事项 | validate_prohibited_patterns | test_cli_accepts_structured_facts_file | test_blocks_conditional_housing_fund_payment |
| DELIVERY_001 | 不得简单约定已发送即视为送达；到达或可证明收悉可作为依据；否定性禁止句不误报 | validate_delivery | test_allows_system_confirmed_delivery_arrival / test_allows_negative_social_housing_and_delivery_sentences | test_blocks_sent_equals_served_delivery_clause / test_later_bad_delivery_clause_is_not_hidden_by_earlier_valid_clause / test_blocks_delivery_even_when_system_confirms_not_arrived / test_blocks_unconfirmed_arrival_deemed_served_synonym |
| PENALTY_001 | 不得泛化劳动者固定违约金；培训服务期和有效竞业限制违约金可豁免 | validate_penalties | test_allows_noncompete_liquidated_damages | test_blocks_general_labor_penalty / test_blocks_generic_fixed_penalty_without_any_clause / test_blocks_general_penalty_even_when_service_period_is_mentioned_as_exception / test_blocks_general_penalty_without_any_word |
| ADJUST_001 | 不得约定任意调岗调薪或劳动者无条件服从；否定性禁止表述不应误报 | validate_job_adjustment | test_allows_negative_arbitrary_adjustment_sentence | test_blocks_unconditional_job_and_pay_adjustment |
| CLI_001 | CLI 文件、编码、JSON 错误应单行报错，不输出 traceback | read_utf8_text / read_json_file | test_cli_accepts_structured_facts_file | test_validate_cli_reports_bad_json_without_traceback / test_generate_cli_reports_missing_input_without_traceback |
