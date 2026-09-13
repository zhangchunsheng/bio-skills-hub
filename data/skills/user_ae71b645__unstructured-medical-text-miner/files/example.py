"""非结构化医疗文本挖掘器使用示例

演示如何使用医疗文本挖掘器处理 MIMIC-IV 数据"""

from scripts.main import MedicalTextMiner

# 示例出院摘要文本
sample_discharge_summary = """
DISCHARGE SUMMARY

Patient: [**Name**] (M, 67 y/o)
Admission Date: [**Date**]
Discharge Date: [**Date**]

CHIEF COMPLAINT:
Chest pain for 3 hours

HISTORY OF PRESENT ILLNESS:
Patient presented with acute onset chest pain radiating to left arm.
No prior history of coronary artery disease. Denies dyspnea, nausea, or diaphoresis.
Vital signs on admission: BP 140/90, HR 98, RR 18, SpO2 97% on room air.

HOSPITAL COURSE:
ECG showed ST elevation in V1-V4 consistent with anterior STEMI.
Troponin I peaked at 15.6 ng/mL.
Patient underwent emergent cardiac catheterization with PCI to LAD.
Started on aspirin 81mg daily, clopidogrel 75mg daily, atorvastatin 40mg daily.
No complications post-procedure. Chest pain resolved.

DISCHARGE DIAGNOSIS:
1. Acute anterior ST-elevation myocardial infarction (STEMI), successfully treated with PCI
2. Hypertension

DISCHARGE MEDICATIONS:
1. Aspirin 81mg PO daily
2. Clopidogrel 75mg PO daily
3. Atorvastatin 40mg PO daily
4. Lisinopril 10mg PO daily

FOLLOW UP:
Cardiology clinic in 1 week
"""


def demo_single_text():
    """演示对单段文本进行实体（NER）和关系抽取"""
    print("=" * 60)
    print("示例 1：单段文本提取")
    print("=" * 60)

    miner = MedicalTextMiner()

    # 执行完整洞察提取
    insights = miner.extract_insights(
        sample_discharge_summary,
        extract_entities=True,
        extract_relations=True,
        extract_timeline=True,
        extract_logic=True
    )

    print(f"\n共提取 {insights['entity_count']} 个实体：")
    for entity_type, entities in insights.get('entities_by_type', {}).items():
        print(f"\n  {entity_type}：")
        for e in entities[:3]:  # 仅展示前 3 个
            neg_mark = " [已否定]" if e.get('negated') else ""
            print(f"    - {e['text']}{neg_mark}")

    print(f"\n共提取 {insights.get('relation_count', 0)} 条关系：")
    for r in insights.get('relations', [])[:3]:
        print(f"  - {r['subject']} --{r['predicate']}--> {r['object']}")

    print("\n临床逻辑：")
    logic = insights.get('clinical_logic', {})
    if logic.get('presenting_complaint'):
        print(f"  主诉：{logic['presenting_complaint']}")
    if logic.get('workup'):
        print(f"  检查项目：{', '.join(logic['workup'])}")

    return insights


def demo_patient_processing():
    """演示患者级别处理（需要 MIMIC-IV 数据文件）"""
    print("\n" + "=" * 60)
    print("示例 2：患者级别处理（需要 MIMIC-IV 数据）")
    print("=" * 60)

    miner = MedicalTextMiner()

    # 注意：此示例需要实际的 MIMIC-IV 数据文件
    # 取消以下注释并提供正确的文件路径后即可运行

    # miner.load_notes("path/to/noteevents.csv", note_types=["DS", "RR"])
    # patient_insights = miner.process_patient(subject_id=10000032)
    #
    # print(miner.generate_summary_report(patient_insights))
    # miner.export_to_json(patient_insights, "patient_10000032_insights.json")

    print("""
    运行患者级别处理的步骤：

    1. 从 PhysioNet 下载 MIMIC-IV NOTEEVENTS 数据
    2. 执行以下代码：

       miner = MedicalTextMiner()
       miner.load_notes("noteevents.csv", note_types=["DS"])
       insights = miner.process_patient(subject_id=10000032)
       miner.export_to_json(insights, "output.json")
    """)


def demo_regex_patterns():
    """演示正则表达式模式匹配"""
    print("\n" + "=" * 60)
    print("示例 3：正则模式匹配")
    print("=" * 60)

    test_text = """
    The patient was diagnosed with acute myocardial infarction.
    Started on heparin drip and metformin 500mg twice daily.
    No evidence of pneumonia. Troponin elevated at 5.2 ng/mL.
    """

    miner = MedicalTextMiner()
    entities = miner.extract_entities_regex(test_text)

    print(f"\n共找到 {len(entities)} 个实体：")
    for e in entities:
        neg_mark = " [已否定]" if e.get('negated') else ""
        print(f"  - [{e['type']}] {e['text']}{neg_mark}")


if __name__ == "__main__":
    # 运行演示
    demo_single_text()
    demo_regex_patterns()
    demo_patient_processing()
