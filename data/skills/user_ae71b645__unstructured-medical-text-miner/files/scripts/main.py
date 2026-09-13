#!/usr/bin/env python3
"""非结构化医疗文本挖掘器（Skill ID: 213）

挖掘MIMIC-IV医疗文本数据，提取非结构化诊断与治疗信息。
支持实体识别（NER）、关系抽取、时间线分析和诊断逻辑提取。"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import warnings

import pandas as pd

# 尝试导入可选依赖
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    warnings.warn("spacy 未安装，NER（命名实体识别）功能将受限。")

try:
    from negspacy.negation import Negex  # noqa: F401
    NEGSPACY_AVAILABLE = True
except ImportError:
    NEGSPACY_AVAILABLE = False


class MedicalTextMiner:
    """MIMIC-IV 非结构化医疗文本挖掘器

    主要功能：
    1. 加载并预处理 NOTEEVENTS 等文本数据
    2. 实体识别（NER）——疾病、症状、药物、手术等
    3. 否定检测（Negation Detection）——识别被否定的临床发现
    4. 关系抽取——药物-疾病关系等
    5. 时间线抽取——疾病进展顺序
    6. 诊断治疗逻辑分析"""

    # 医疗实体类型定义
    ENTITY_PATTERNS = {
        "MEDICATION": [
            r"\b(aspirin|warfarin|heparin|metformin|insulin|amoxicillin|"
            r"azithromycin|morphine|fentanyl|propofol|norepinephrine|"
            r"phenylephrine|dopamine|epinephrine)\b",
            r"\b\w+\s*(?:mg|mcg|g|units?)\b"  # 剂量模式
        ],
        "DISEASE": [
            r"\b(acute myocardial infarction|AMI|STEMI|NSTEMI|heart failure|"
            r"pneumonia|sepsis|ARDS|COPD|asthma|diabetes mellitus|"
            r"hypertension|atrial fibrillation|AFib|stroke|DVT|PE)\b",
            r"\b\w+(?:itis|osis|emia|oma|pathy| syndrome)\b"
        ],
        "SYMPTOM": [
            r"\b(chest pain|dyspnea|shortness of breath|fatigue|nausea|"
            r"vomiting|fever|chills|headache|dizziness|syncope|"
            r"palpitations|cough|hemoptysis)\b"
        ],
        "PROCEDURE": [
            r"\b(PCI|CABG|ECG|EKG|echocardiogram|CT|MRI|chest X-ray|"
            r"bronchoscopy|intubation|extubation|thoracentesis|"
            r"paracentesis|lumbar puncture)\b"
        ],
        "ANATOMY": [
            r"\b(left ventricle|right ventricle|left atrium|right atrium|"
            r"mitral valve|aortic valve|tricuspid valve|pulmonary valve|"
            r"coronary artery|LAD|LCx|RCA|lung|liver|kidney|spleen)\b"
        ],
        "LAB_VALUE": [
            r"\b(troponin|creatinine|BNP|NT-proBNP|WBC|hemoglobin|platelet|"
            r"INR|PTT|PT|glucose|HbA1c|lactate|pH|PCO2|PO2)\b"
        ]
    }

    # 否定词模式
    NEGATION_CUES = [
        r"\b(no|not|denies|denied|without|absent|negative for|"
        r"ruled out|no evidence of|non-)\b"
    ]

    # 时间模式
    TIME_PATTERNS = [
        r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b",          # MM/DD/YYYY
        r"\b(\d{4}-\d{2}-\d{2})\b",                  # YYYY-MM-DD
        r"\b(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\b",  # 时间
        r"\b(on admission|at presentation|post-operatively|"
        r"pre-operatively|on day \d+|POD \#?\d+)\b"
    ]

    def __init__(self, config: Optional[Dict] = None):
        """初始化 MedicalTextMiner

        Args:
            config: 配置字典，可包含模型路径、输出格式等设置"""
        self.config = config or {}
        self.notes_df: Optional[pd.DataFrame] = None
        self.nlp = None

        # 初始化 spaCy 模型（如可用）
        self._init_nlp()

    def _init_nlp(self):
        """初始化 NLP 模型

        修复说明：原始代码在 negspacy 可用时先调用 Negex(self.nlp, name="negex")
        再调用 self.nlp.add_pipe("negex", last=True)，导致组件被重复添加，
        触发 ValueError: [E007] 'negex' already exists in the pipeline。
        修复方式：仅使用 add_pipe 工厂方法注册组件，移除多余的手动实例化。"""
        if not SPACY_AVAILABLE:
            return

        model_name = self.config.get("ner_model", "en_core_web_sm")
        try:
            self.nlp = spacy.load(model_name)

            # 添加否定检测组件（仅使用 add_pipe，避免重复注册）
            if NEGSPACY_AVAILABLE:
                self.nlp.add_pipe("negex", last=True)

        except OSError:
            warnings.warn(f"模型 {model_name} 未找到，将以纯正则模式运行。")
            self.nlp = None

    def load_notes(self, notes_path: Union[str, Path],
                   note_types: Optional[List[str]] = None) -> pd.DataFrame:
        """加载 MIMIC-IV NOTEEVENTS 数据

        Args:
            notes_path: NOTEEVENTS 文件路径（CSV 或 Parquet）
            note_types: 过滤特定记录类型（如 ['DS', 'RR']）

        Returns:
            加载后的 DataFrame"""
        path = Path(notes_path)

        if path.suffix == '.csv':
            df = pd.read_csv(path)
        elif path.suffix in ['.parquet', '.pq']:
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"不支持的文件格式：{path.suffix}")

        # 标准化列名
        df.columns = df.columns.str.lower()

        # 过滤记录类型
        if note_types and 'note_type' in df.columns:
            df = df[df['note_type'].isin(note_types)]

        # 转换时间列
        if 'charttime' in df.columns:
            df['charttime'] = pd.to_datetime(df['charttime'], errors='coerce')

        self.notes_df = df
        print(f"已从 {path} 加载 {len(df)} 条记录")

        return df

    def get_patient_texts(self, subject_id: int,
                          hadm_id: Optional[int] = None) -> List[Dict]:
        """获取特定患者的所有文本记录

        Args:
            subject_id: 患者 ID
            hadm_id: 可选的住院记录 ID

        Returns:
            该患者的文本记录列表"""
        if self.notes_df is None:
            raise ValueError("未加载记录数据，请先调用 load_notes()。")

        mask = self.notes_df['subject_id'] == subject_id
        if hadm_id is not None:
            mask = mask & (self.notes_df['hadm_id'] == hadm_id)

        patient_notes = self.notes_df[mask].sort_values('charttime')

        return patient_notes.to_dict('records')

    def extract_entities_regex(self, text: str) -> List[Dict]:
        """使用正则表达式提取医疗实体（NER）

        Args:
            text: 输入文本

        Returns:
            实体列表"""
        entities = []

        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entity = {
                        "text": match.group(),
                        "type": entity_type,
                        "start": match.start(),
                        "end": match.end(),
                        "source": "regex"
                    }
                    entities.append(entity)

        # 检测否定
        entities = self._detect_negation(text, entities)

        return entities

    def extract_entities_spacy(self, text: str) -> List[Dict]:
        """使用 spaCy 提取医疗实体（NER）

        Args:
            text: 输入文本

        Returns:
            实体列表"""
        if self.nlp is None:
            return []

        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            entity = {
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "source": "spacy"
            }

            # 检查否定（使用 negspacy）
            if NEGSPACY_AVAILABLE and hasattr(ent._, "negex"):
                entity["negated"] = ent._.negex

            entities.append(entity)

        return entities

    def _detect_negation(self, text: str, entities: List[Dict]) -> List[Dict]:
        """检测实体是否被否定（Negation Detection）

        Args:
            text: 原始文本
            entities: 实体列表

        Returns:
            添加否定标记后的实体列表"""
        for entity in entities:
            # 获取实体前方的文本窗口（最多 50 个字符）
            start_pos = max(0, entity["start"] - 50)
            context = text[start_pos:entity["start"]]

            # 检查是否存在否定词
            is_negated = any(
                re.search(pattern, context, re.IGNORECASE)
                for pattern in self.NEGATION_CUES
            )
            entity["negated"] = is_negated

        return entities

    def extract_relations(self, text: str, entities: List[Dict]) -> List[Dict]:
        """从文本中提取实体间关系

        Args:
            text: 输入文本
            entities: 已识别的实体列表

        Returns:
            关系三元组列表"""
        relations = []

        # 简单基于模式的关系抽取
        # 药物-疾病治疗关系
        med_disease_pattern = r"(\w+)\s+(?:for|to treat|management of)\s+([\w\s]+?)(?:\.|,|;|$)"
        for match in re.finditer(med_disease_pattern, text, re.IGNORECASE):
            relations.append({
                "subject": match.group(1),
                "predicate": "TREATS",
                "object": match.group(2).strip(),
                "confidence": 0.7,
                "source": "pattern"
            })

        # 症状-疾病因果关系
        symptom_disease_pattern = r"(\w+)\s+(?:due to|caused by|secondary to)\s+([\w\s]+?)(?:\.|,|;|$)"
        for match in re.finditer(symptom_disease_pattern, text, re.IGNORECASE):
            relations.append({
                "subject": match.group(1),
                "predicate": "CAUSED_BY",
                "object": match.group(2).strip(),
                "confidence": 0.6,
                "source": "pattern"
            })

        return relations

    def extract_timeline(self, text: str) -> List[Dict]:
        """从文本中提取时序事件

        Args:
            text: 输入文本

        Returns:
            事件时间线"""
        events = []
        sentences = re.split(r'[.!?]\s+', text)

        event_indicators = [
            "admitted", "presented", "developed", "underwent",
            "started", "discontinued", "noted", "observed",
            "worsening", "improvement", "resolved"
        ]

        for sent in sentences:
            # 检测时间表达式
            time_match = None
            for pattern in self.TIME_PATTERNS:
                match = re.search(pattern, sent, re.IGNORECASE)
                if match:
                    time_match = match.group()
                    break

            # 检测事件动词
            for indicator in event_indicators:
                if re.search(rf"\b{indicator}\b", sent, re.IGNORECASE):
                    events.append({
                        "time_expression": time_match,
                        "event_verb": indicator,
                        "description": sent.strip(),
                        "raw_time": time_match
                    })
                    break

        return events

    def parse_clinical_logic(self, text: str) -> Dict:
        """解析诊断治疗逻辑链

        Args:
            text: 医疗文本

        Returns:
            诊断治疗的逻辑结构"""
        logic = {
            "presenting_complaint": None,
            "differential_diagnoses": [],
            "workup": [],
            "final_diagnosis": None,
            "treatment_plan": [],
            "clinical_course": []
        }

        # 提取主诉
        chief_complaint_patterns = [
            r"chief complaint[:\s]+([^.]+)",
            r"presented with[:\s]+([^.]+)",
            r"\bPC[:\s]+([^.]+)"
        ]
        for pattern in chief_complaint_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logic["presenting_complaint"] = match.group(1).strip()
                break

        # 提取鉴别诊断（DDx）
        dd_pattern = r"(?:differential diagnosis|DDx)[:\s]+([^.]+(?:,[^.]+)*)"
        match = re.search(dd_pattern, text, re.IGNORECASE)
        if match:
            logic["differential_diagnoses"] = [
                d.strip() for d in match.group(1).split(",")
            ]

        # 提取检查项目
        workup_indicators = ["obtained", "performed", "ordered", "showed"]
        for indicator in workup_indicators:
            pattern = rf"(\w+(?:\s\w+)?)\s+{indicator}"
            for match in re.finditer(pattern, text, re.IGNORECASE):
                procedure = match.group(1)
                if procedure.lower() in [
                    "ecg", "ekg", "ct", "mri", "x-ray", "echo",
                    "troponin", "bnp", "wbc"
                ]:
                    logic["workup"].append(procedure)

        # 去重
        logic["workup"] = list(set(logic["workup"]))

        return logic

    def extract_insights(self, text: str,
                         extract_entities: bool = True,
                         extract_relations: bool = True,
                         extract_timeline: bool = True,
                         extract_logic: bool = True) -> Dict:
        """执行完整的医疗文本洞察提取

        Args:
            text: 输入医疗文本
            extract_entities: 是否提取实体（NER）
            extract_relations: 是否提取关系
            extract_timeline: 是否提取时间线
            extract_logic: 是否解析诊断治疗逻辑

        Returns:
            综合洞察结果字典"""
        insights = {
            "raw_text_length": len(text),
            "extraction_timestamp": datetime.now().isoformat()
        }

        # 实体提取（NER）
        if extract_entities:
            entities_regex = self.extract_entities_regex(text)
            entities_spacy = self.extract_entities_spacy(text)

            # 合并结果（去重）
            all_entities = entities_regex + [
                e for e in entities_spacy
                if not any(e["start"] == ex["start"] for ex in entities_regex)
            ]

            # 按类型分组
            entities_by_type: Dict[str, List] = {}
            for e in all_entities:
                etype = e["type"]
                if etype not in entities_by_type:
                    entities_by_type[etype] = []
                entities_by_type[etype].append(e)

            insights["entities"] = all_entities
            insights["entities_by_type"] = entities_by_type
            insights["entity_count"] = len(all_entities)

        # 关系抽取
        if extract_relations and extract_entities:
            relations = self.extract_relations(text, insights.get("entities", []))
            insights["relations"] = relations
            insights["relation_count"] = len(relations)

        # 时间线提取
        if extract_timeline:
            timeline = self.extract_timeline(text)
            insights["timeline"] = timeline
            insights["event_count"] = len(timeline)

        # 诊断治疗逻辑分析
        if extract_logic:
            logic = self.parse_clinical_logic(text)
            insights["clinical_logic"] = logic

        return insights

    def process_patient(self, subject_id: int,
                        hadm_id: Optional[int] = None) -> Dict:
        """处理单个患者的所有文本记录

        Args:
            subject_id: 患者 ID
            hadm_id: 可选的住院记录 ID

        Returns:
            患者综合洞察结果"""
        notes = self.get_patient_texts(subject_id, hadm_id)

        patient_insights: Dict[str, Any] = {
            "subject_id": subject_id,
            "hadm_id": hadm_id,
            "note_count": len(notes),
            "notes": []
        }

        for note in notes:
            text = note.get('note_text', '')
            if not text:
                continue

            note_insights = self.extract_insights(text)
            note_insights.update({
                "note_id": note.get('note_id'),
                "note_type": note.get('note_type'),
                "charttime": note.get('charttime')
            })

            patient_insights["notes"].append(note_insights)

        # 汇总所有实体
        all_entities: List[Dict] = []
        for note in patient_insights["notes"]:
            all_entities.extend(note.get("entities", []))

        patient_insights["aggregated_entities"] = self._aggregate_entities(all_entities)

        return patient_insights

    def _aggregate_entities(self, entities: List[Dict]) -> Dict:
        """汇总实体（去重并计数）"""
        entity_map: Dict = {}

        for e in entities:
            key = (e["text"].lower(), e["type"])
            if key not in entity_map:
                entity_map[key] = {
                    "text": e["text"],
                    "type": e["type"],
                    "count": 0,
                    "negated_count": 0,
                    "instances": []
                }

            entity_map[key]["count"] += 1
            if e.get("negated"):
                entity_map[key]["negated_count"] += 1
            entity_map[key]["instances"].append({
                "start": e["start"],
                "end": e["end"]
            })

        return {
            "unique_count": len(entity_map),
            "entities": list(entity_map.values())
        }

    def export_to_json(self, insights: Dict, output_path: str):
        """将洞察结果导出为 JSON 文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
        print(f"已将洞察结果导出至 {output_path}")

    def generate_summary_report(self, insights: Dict) -> str:
        """生成文本摘要报告"""
        report = []
        report.append("=" * 60)
        report.append("医疗文本挖掘摘要报告")
        report.append("=" * 60)

        if "subject_id" in insights:
            report.append(f"\n患者 ID：{insights['subject_id']}")

        if "note_count" in insights:
            report.append(f"已处理记录总数：{insights['note_count']}")

        if "aggregated_entities" in insights:
            agg = insights["aggregated_entities"]
            report.append(f"\n发现唯一实体数：{agg['unique_count']}")

            # 按类型分组展示
            by_type: Dict[str, List] = {}
            for e in agg["entities"]:
                t = e["type"]
                if t not in by_type:
                    by_type[t] = []
                by_type[t].append(e)

            for etype, entities in sorted(by_type.items()):
                report.append(f"\n{etype}（{len(entities)} 个唯一实体）：")
                for e in sorted(entities, key=lambda x: -x["count"])[:5]:
                    neg_info = f"，否定 {e['negated_count']} 次" if e['negated_count'] > 0 else ""
                    report.append(f"  - {e['text']}（提及 {e['count']} 次{neg_info}）")

        return "\n".join(report)


def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(
        description="MIMIC-IV 非结构化医疗文本挖掘器"
    )
    parser.add_argument(
        "--input", "-i",
        help="NOTEEVENTS CSV/Parquet 文件路径"
    )
    parser.add_argument(
        "--subject-id", "-s", type=int,
        help="按 subject_id 处理特定患者"
    )
    parser.add_argument(
        "--hadm-id", type=int,
        help="按住院记录 ID 过滤"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出 JSON 文件路径"
    )
    parser.add_argument(
        "--extract", choices=["entities", "relations", "timeline", "logic", "all"],
        default="all",
        help="指定要提取的内容（entities/relations/timeline/logic/all）"
    )
    parser.add_argument(
        "--note-types", nargs="+",
        help="按记录类型过滤（如 DS RR ECG）"
    )
    parser.add_argument(
        "--sample-text",
        help="直接处理单个文本片段"
    )

    args = parser.parse_args()

    miner = MedicalTextMiner()

    # 处理单个文本片段
    if args.sample_text:
        insights = miner.extract_insights(args.sample_text)
        print(json.dumps(insights, indent=2, default=str))
        return

    # 需要输入文件
    if not args.input:
        parser.error("必须提供 --input（或使用 --sample-text）")

    # 加载数据
    miner.load_notes(args.input, args.note_types)

    # 处理特定患者或批量处理
    if args.subject_id:
        insights = miner.process_patient(args.subject_id, args.hadm_id)
    else:
        # 处理所有患者（简化版本）
        print("正在处理所有患者...")
        all_insights = []
        for sid in miner.notes_df['subject_id'].unique()[:10]:  # 限制前 10 名患者
            patient_insights = miner.process_patient(sid)
            all_insights.append(patient_insights)
        insights = {
            "patient_count": len(all_insights),
            "patients": all_insights
        }

    # 生成摘要
    print("\n" + miner.generate_summary_report(insights))

    # 导出结果
    if args.output:
        miner.export_to_json(insights, args.output)
    else:
        default_output = "medical_text_insights.json"
        miner.export_to_json(insights, default_output)


if __name__ == "__main__":
    main()
