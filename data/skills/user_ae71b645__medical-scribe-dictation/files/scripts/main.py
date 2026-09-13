#!/usr/bin/env python3
"""
医疗听写录音转录助手 —— 将医生口述内容转换为结构化的 SOAP 病历。

本模块提供以下功能：
- 处理已转录的医疗口述文本
- 生成结构化的 SOAP 病历
- 处理医学术语标准化
- 校验临床记录的完整性
"""

import re
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import warnings

# 可选依赖，若未安装则自动降级为规则解析
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class VitalSigns:
    """患者生命体征。"""
    temperature: Optional[str] = None
    heart_rate: Optional[str] = None
    blood_pressure: Optional[str] = None
    respiratory_rate: Optional[str] = None
    oxygen_saturation: Optional[str] = None
    weight: Optional[str] = None
    height: Optional[str] = None
    bmi: Optional[str] = None


@dataclass
class SOAPNote:
    """结构化 SOAP 病历数据类。"""
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    # Subjective（主观资料）
    chief_complaint: str = ""
    history_present_illness: str = ""
    review_of_systems: str = ""
    past_medical_history: str = ""
    medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    social_history: str = ""
    family_history: str = ""

    # Objective（客观资料）
    vital_signs: VitalSigns = field(default_factory=VitalSigns)
    physical_examination: str = ""
    diagnostic_studies: str = ""

    # Assessment（评估）
    primary_diagnosis: str = ""
    differential_diagnoses: List[str] = field(default_factory=list)
    clinical_reasoning: str = ""

    # Plan（计划）
    diagnostic_plan: str = ""
    therapeutic_plan: str = ""
    patient_education: str = ""
    follow_up: str = ""

    # 元数据
    specialty: str = "general"
    confidence_score: float = 0.0
    warnings: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """将 SOAP 病历转换为 Markdown 格式。"""
        sections = [
            f"# 临床记录 - {self.date}",
            "",
            "## 主观资料 (Subjective)",
            "",
            f"**主诉：** {self.chief_complaint or '未记录'}",
            "",
            f"**现病史：** {self.history_present_illness or '未记录'}",
            "",
        ]

        if self.review_of_systems:
            sections.extend([
                "**系统回顾：**",
                self.review_of_systems,
                ""
            ])

        if self.past_medical_history:
            sections.extend([
                "**既往病史：**",
                self.past_medical_history,
                ""
            ])

        if self.medications:
            sections.extend([
                "**目前用药：**",
                "\n".join(f"- {med}" for med in self.medications),
                ""
            ])

        if self.allergies:
            sections.extend([
                "**过敏史：**",
                "\n".join(f"- {allergy}" for allergy in self.allergies),
                ""
            ])

        if self.social_history:
            sections.extend([
                "**社会史：**",
                self.social_history,
                ""
            ])

        if self.family_history:
            sections.extend([
                "**家族史：**",
                self.family_history,
                ""
            ])

        # Objective
        sections.extend([
            "## 客观资料 (Objective)",
            ""
        ])

        vital_signs_text = self._format_vital_signs()
        if vital_signs_text:
            sections.extend([
                "**生命体征：**",
                vital_signs_text,
                ""
            ])

        if self.physical_examination:
            sections.extend([
                "**体格检查：**",
                self.physical_examination,
                ""
            ])

        if self.diagnostic_studies:
            sections.extend([
                "**辅助检查：**",
                self.diagnostic_studies,
                ""
            ])

        # Assessment
        sections.extend([
            "## 评估 (Assessment)",
            ""
        ])

        if self.primary_diagnosis:
            sections.extend([
                f"**主要诊断：** {self.primary_diagnosis}",
                ""
            ])

        if self.differential_diagnoses:
            sections.extend([
                "**鉴别诊断：**",
                "\n".join(f"- {dx}" for dx in self.differential_diagnoses),
                ""
            ])

        if self.clinical_reasoning:
            sections.extend([
                "**临床推理：**",
                self.clinical_reasoning,
                ""
            ])

        # Plan
        sections.extend([
            "## 计划 (Plan)",
            ""
        ])

        if self.diagnostic_plan:
            sections.extend([
                "**辅助检查计划：**",
                self.diagnostic_plan,
                ""
            ])

        if self.therapeutic_plan:
            sections.extend([
                "**治疗计划：**",
                self.therapeutic_plan,
                ""
            ])

        if self.patient_education:
            sections.extend([
                "**患者教育：**",
                self.patient_education,
                ""
            ])

        if self.follow_up:
            sections.extend([
                "**随访：**",
                self.follow_up,
                ""
            ])

        # Metadata
        if self.warnings:
            sections.extend([
                "---",
                "",
                "**⚠️ 校验警告：**",
                "\n".join(f"- {w}" for w in self.warnings),
                ""
            ])

        sections.extend([
            "---",
            "",
            f"*本病历生成置信度评分：{self.confidence_score:.2f}*",
            "",
            "*本病历由 AI 生成，正式记录前必须经主诊医师审核确认。*"
        ])

        return "\n".join(sections)

    def _format_vital_signs(self) -> str:
        """格式化生命体征用于展示。"""
        vs = self.vital_signs
        parts = []
        if vs.temperature:
            parts.append(f"体温：{vs.temperature}")
        if vs.heart_rate:
            parts.append(f"心率：{vs.heart_rate}")
        if vs.blood_pressure:
            parts.append(f"血压：{vs.blood_pressure}")
        if vs.respiratory_rate:
            parts.append(f"呼吸频率：{vs.respiratory_rate}")
        if vs.oxygen_saturation:
            parts.append(f"血氧饱和度：{vs.oxygen_saturation}")
        if vs.weight:
            parts.append(f"体重：{vs.weight}")
        if vs.height:
            parts.append(f"身高：{vs.height}")
        if vs.bmi:
            parts.append(f"BMI：{vs.bmi}")
        return " | ".join(parts) if parts else ""


class MedicalTerminologyProcessor:
    """处理和标准化医学术语。"""

    # 常见医学缩写及其展开形式
    ABBREVIATIONS = {
        "c/o": "complaining of",
        "w/": "with",
        "w/o": "without",
        "s/p": "status post",
        "r/o": "rule out",
        "h/o": "history of",
        "b/l": "bilateral",
        "u/l": "unilateral",
        "d/t": "due to",
        "secondary to": "secondary to",
        "c-section": "cesarean section",
        "bmi": "body mass index",
        "bp": "blood pressure",
        "hr": "heart rate",
        "rr": "respiratory rate",
        "o2sat": "oxygen saturation",
        "spo2": "oxygen saturation",
        "temp": "temperature",
        "htn": "hypertension",
        "dm": "diabetes mellitus",
        "cad": "coronary artery disease",
        "chf": "congestive heart failure",
        "copd": "chronic obstructive pulmonary disease",
        "uti": "urinary tract infection",
        "aki": "acute kidney injury",
        "ckd": "chronic kidney disease",
        "mi": "myocardial infarction",
        "cva": "cerebrovascular accident",
        "tia": "transient ischemic attack",
        "pe": "pulmonary embolism",
        "dvt": "deep vein thrombosis",
        "afib": "atrial fibrillation",
        "hf": "heart failure",
        "aki": "acute kidney injury",
        "ards": "acute respiratory distress syndrome",
        "ards": "acute respiratory distress syndrome",
    }

    # 药物名称后缀模式（简化版）
    DRUG_SUFFIXES = [
        "mycin", "cillin", "xaban", "nib", "mab", "zolam", "pram", "sartan",
        "statin", "pril", "sone", "nide", "micin", "cycline", "azole"
    ]

    def normalize_text(self, text: str) -> str:
        """标准化文本中的医学缩写。"""
        text_lower = text.lower()

        # 展开常见缩写
        for abbr, expansion in self.ABBREVIATIONS.items():
            # 大小写不敏感替换
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            text = pattern.sub(expansion, text)

        return text

    def extract_medications(self, text: str) -> List[str]:
        """从文本中提取药物名称。"""
        medications = []

        # 常见药物格式的匹配模式
        # 匹配示例："Lisinopril 10mg"、"metformin"、"Amoxicillin-Clavulanate"
        med_patterns = [
            r'\b([A-Z][a-z]+(?:-[A-Z]?[a-z]+)?\s+\d+\s*(?:mg|mcg|g|ml|units?))\b',
            r'\b([a-z]+(?:mycin|cillin|zolam|sartan|statin|pril|sone|nide))\b',
            r'\b(aspirin|ibuprofen|acetaminophen|lisinopril|metformin|atorvastatin)\b',
        ]

        for pattern in med_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            medications.extend(matches)

        return list(set(medications))

    def extract_vital_signs(self, text: str) -> VitalSigns:
        """使用正则表达式从文本中提取生命体征。"""
        vs = VitalSigns()

        # 体温模式
        temp_match = re.search(r'(\d+\.?\d*)\s*(?:degrees?|°)?\s*[Ff]', text)
        if temp_match:
            vs.temperature = f"{temp_match.group(1)}°F"
        else:
            temp_match = re.search(r'(\d+\.?\d*)\s*(?:degrees?|°)?\s*[Cc]', text)
            if temp_match:
                vs.temperature = f"{temp_match.group(1)}°C"

        # 血压
        bp_match = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})\s*(?:mm\s*Hg)?', text)
        if bp_match:
            vs.blood_pressure = f"{bp_match.group(1)}/{bp_match.group(2)} mmHg"

        # 心率
        hr_match = re.search(r'(?:heart rate|hr|pulse)\s*(?:of|is|was)?\s*(\d+)', text, re.IGNORECASE)
        if hr_match:
            vs.heart_rate = f"{hr_match.group(1)} bpm"

        # 呼吸频率
        rr_match = re.search(r'(?:respiratory rate|rr|respirations?)\s*(?:of|is|was)?\s*(\d+)', text, re.IGNORECASE)
        if rr_match:
            vs.respiratory_rate = f"{rr_match.group(1)} /min"

        # 血氧饱和度
        o2_match = re.search(r'(?:o2\s*sat|spo2|oxygen)\s*(?:of|is|was)?\s*(\d+)%?', text, re.IGNORECASE)
        if o2_match:
            vs.oxygen_saturation = f"{o2_match.group(1)}%"

        return vs


class MedicalScribe:
    """处理口述内容的主类。"""

    def __init__(self, specialty: str = "general", llm_provider: Optional[str] = None):
        self.specialty = specialty
        self.terminology_processor = MedicalTerminologyProcessor()
        self.llm_provider = llm_provider

        # 若相应依赖可用，则初始化 LLM 客户端
        self.llm_client = None
        if llm_provider == "openai" and OPENAI_AVAILABLE:
            self.llm_client = openai.OpenAI()
        elif llm_provider == "anthropic" and ANTHROPIC_AVAILABLE:
            self.llm_client = Anthropic()

    def process_dictation(self, text: str) -> SOAPNote:
        """
        处理医疗口述内容并生成 SOAP 病历。

        参数：
            text: 原始转录口述文本

        返回：
            SOAPNote: 结构化 SOAP 病历对象
        """
        # 标准化术语
        normalized_text = self.terminology_processor.normalize_text(text)

        # 若 LLM 可用，则使用其进行智能解析
        if self.llm_client and self.llm_provider:
            return self._process_with_llm(normalized_text)
        else:
            # 降级为基于规则的解析
            return self._process_rule_based(normalized_text)

    def _process_with_llm(self, text: str) -> SOAPNote:
        """使用 LLM 进行智能信息提取。"""
        prompt = self._build_extraction_prompt(text)

        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a medical scribe AI. Extract clinical information and format as structured JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
            elif self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4096,
                    system="You are a medical scribe AI. Extract clinical information and format as structured JSON.",
                    messages=[{"role": "user", "content": prompt}]
                )
                # 从响应中提取 JSON
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("LLM 响应中未找到有效的 JSON 内容")
            else:
                return self._process_rule_based(text)

            return self._build_soap_from_dict(result)

        except Exception as e:
            warnings.warn(f"LLM 处理失败：{e}。已回退为基于规则的解析。")
            return self._process_rule_based(text)

    def _build_extraction_prompt(self, text: str) -> str:
        """构造用于 LLM 提取的提示词。"""
        return f"""Extract clinical information from the following medical dictation and format as JSON with this structure:

{{
    "chief_complaint": "...",
    "history_present_illness": "...",
    "review_of_systems": "...",
    "past_medical_history": "...",
    "medications": ["..."],
    "allergies": ["..."],
    "social_history": "...",
    "family_history": "...",
    "vital_signs": {{
        "temperature": "...",
        "heart_rate": "...",
        "blood_pressure": "...",
        "respiratory_rate": "...",
        "oxygen_saturation": "..."
    }},
    "physical_examination": "...",
    "diagnostic_studies": "...",
    "primary_diagnosis": "...",
    "differential_diagnoses": ["..."],
    "clinical_reasoning": "...",
    "diagnostic_plan": "...",
    "therapeutic_plan": "...",
    "patient_education": "...",
    "follow_up": "..."
}}

Dictation text:
{text}

Respond ONLY with valid JSON."""

    def _build_soap_from_dict(self, data: Dict) -> SOAPNote:
        """从字典构造 SOAPNote。"""
        note = SOAPNote(specialty=self.specialty)

        # Subjective
        note.chief_complaint = data.get("chief_complaint", "")
        note.history_present_illness = data.get("history_present_illness", "")
        note.review_of_systems = data.get("review_of_systems", "")
        note.past_medical_history = data.get("past_medical_history", "")
        note.medications = data.get("medications", [])
        note.allergies = data.get("allergies", [])
        note.social_history = data.get("social_history", "")
        note.family_history = data.get("family_history", "")

        # Objective - 生命体征
        vs_data = data.get("vital_signs", {})
        note.vital_signs = VitalSigns(
            temperature=vs_data.get("temperature"),
            heart_rate=vs_data.get("heart_rate"),
            blood_pressure=vs_data.get("blood_pressure"),
            respiratory_rate=vs_data.get("respiratory_rate"),
            oxygen_saturation=vs_data.get("oxygen_saturation")
        )
        note.physical_examination = data.get("physical_examination", "")
        note.diagnostic_studies = data.get("diagnostic_studies", "")

        # Assessment
        note.primary_diagnosis = data.get("primary_diagnosis", "")
        note.differential_diagnoses = data.get("differential_diagnoses", [])
        note.clinical_reasoning = data.get("clinical_reasoning", "")

        # Plan
        note.diagnostic_plan = data.get("diagnostic_plan", "")
        note.therapeutic_plan = data.get("therapeutic_plan", "")
        note.patient_education = data.get("patient_education", "")
        note.follow_up = data.get("follow_up", "")

        # 校验并生成警告
        note.warnings = self._validate_note(note)
        note.confidence_score = self._calculate_confidence(note)

        return note

    def _process_rule_based(self, text: str) -> SOAPNote:
        """使用基于规则的方式解析口述内容。"""
        note = SOAPNote(specialty=self.specialty)

        # 提取生命体征
        note.vital_signs = self.terminology_processor.extract_vital_signs(text)

        # 提取药物
        note.medications = self.terminology_processor.extract_medications(text)

        # 基于关键词的简单分段识别
        text_lower = text.lower()

        # 主诉 —— 查找常见模式
        cc_patterns = [
            r'chief complaint[:\s]+([^\.]+)',
            r'cc[:\s]+([^\.]+)',
            r'patient (?:presents|comes) (?:with|for) ([^\.]+)',
        ]
        for pattern in cc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                note.chief_complaint = match.group(1).strip()
                break

        # 评估/诊断
        dx_patterns = [
            r'assessment[:\s]+([^.]+)',
            r'impression[:\s]+([^.]+)',
            r'diagnosis[:\s]+([^.]+)',
        ]
        for pattern in dx_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                note.primary_diagnosis = match.group(1).strip()
                break

        # 计划
        plan_patterns = [
            r'plan[:\s]+(.+?)(?=\n\n|$)',
            r'treatment plan[:\s]+(.+?)(?=\n\n|$)',
        ]
        for pattern in plan_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                note.therapeutic_plan = match.group(1).strip()
                break

        # 若未识别到结构化分段，则整体归入现病史
        if not note.chief_complaint and not note.primary_diagnosis:
            note.history_present_illness = text

        # 校验并计算置信度
        note.warnings = self._validate_note(note)
        note.confidence_score = self._calculate_confidence(note)

        return note

    def _validate_note(self, note: SOAPNote) -> List[str]:
        """校验 SOAP 病历完整性并标记问题。"""
        warnings = []

        # 检查必需要素
        if not note.chief_complaint:
            warnings.append("Chief complaint not identified")
        if not note.history_present_illness and not note.chief_complaint:
            warnings.append("Limited clinical history documented")
        if not note.primary_diagnosis:
            warnings.append("No assessment/diagnosis identified")
        if not note.therapeutic_plan and not note.diagnostic_plan:
            warnings.append("No plan documented")

        # 检查生命体征完整性
        vs = note.vital_signs
        if not any([vs.temperature, vs.heart_rate, vs.blood_pressure]):
            warnings.append("Vital signs incomplete or missing")

        return warnings

    def _calculate_confidence(self, note: SOAPNote) -> float:
        """根据完整性计算置信度评分。"""
        score = 0.0

        # 主观资料完整性（30%）
        if note.chief_complaint:
            score += 0.10
        if note.history_present_illness:
            score += 0.10
        if note.medications or note.allergies:
            score += 0.10

        # 客观资料完整性（20%）
        vs_fields = [note.vital_signs.temperature, note.vital_signs.heart_rate,
                     note.vital_signs.blood_pressure]
        score += sum(0.07 for f in vs_fields if f) * 0.2
        if note.physical_examination:
            score += 0.05

        # 评估完整性（25%）
        if note.primary_diagnosis:
            score += 0.15
        if note.differential_diagnoses:
            score += 0.05
        if note.clinical_reasoning:
            score += 0.05

        # 计划完整性（25%）
        if note.therapeutic_plan:
            score += 0.15
        if note.follow_up:
            score += 0.10

        return min(score, 1.0)


def transcribe_audio(audio_path: str) -> str:
    """
    使用 Whisper（若可用）将音频文件转录为文本。

    参数：
        audio_path: 音频文件路径

    返回：
        转录后的文本
    """
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except ImportError:
        raise RuntimeError(
            "音频转录功能需要安装 'openai-whisper' 包。"
            "安装方式：pip install openai-whisper"
        )


def main():
    """CLI 主入口。"""
    parser = argparse.ArgumentParser(
        description="医疗听写录音转录助手 —— 将医生口述内容转换为 SOAP 病历"
    )
    parser.add_argument("--input", "-i", help="输入文本，或指向文本文件的路径")
    parser.add_argument("--audio", "-a", help="音频文件路径（需要安装 whisper）")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--specialty", "-s", default="general",
                        help="医学专科（默认：general）")
    parser.add_argument("--llm", choices=["openai", "anthropic"],
                        help="用于高级解析的 LLM 提供方")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                        help="输出格式")

    args = parser.parse_args()

    # 获取输入文本
    if args.audio:
        print(f"正在转录音频：{args.audio}")
        text = transcribe_audio(args.audio)
    elif args.input:
        if Path(args.input).exists():
            text = Path(args.input).read_text()
        else:
            text = args.input
    else:
        # 从标准输入读取
        import sys
        text = sys.stdin.read()

    if not text.strip():
        print("错误：未提供任何输入内容", file=sys.stderr)
        sys.exit(1)

    # 处理口述内容
    print("正在处理口述内容……")
    scribe = MedicalScribe(specialty=args.specialty, llm_provider=args.llm)
    note = scribe.process_dictation(text)

    # 生成输出
    if args.format == "json":
        import json
        output = json.dumps({
            "chief_complaint": note.chief_complaint,
            "history_present_illness": note.history_present_illness,
            "medications": note.medications,
            "vital_signs": {
                "temperature": note.vital_signs.temperature,
                "heart_rate": note.vital_signs.heart_rate,
                "blood_pressure": note.vital_signs.blood_pressure,
                "respiratory_rate": note.vital_signs.respiratory_rate,
                "oxygen_saturation": note.vital_signs.oxygen_saturation,
            },
            "assessment": note.primary_diagnosis,
            "plan": note.therapeutic_plan,
            "confidence": note.confidence_score,
            "warnings": note.warnings,
        }, indent=2, ensure_ascii=False)
    else:
        output = note.to_markdown()

    # 输出结果
    if args.output:
        Path(args.output).write_text(output)
        print(f"结果已写入：{args.output}")
    else:
        print(output)

    print(f"\n置信度评分：{note.confidence_score:.2%}")
    if note.warnings:
        print(f"⚠️  发现 {len(note.warnings)} 项校验警告 —— 需要医师审核")


if __name__ == "__main__":
    import sys
    main()
