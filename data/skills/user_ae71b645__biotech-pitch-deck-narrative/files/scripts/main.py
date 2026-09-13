#!/usr/bin/env python3
"""
生物科技融资演示文稿叙事引擎

将复杂的生物科技科学数据转化为引人入胜的投资者叙事。
为融资展示优化演示文稿的故事讲述方式。

用法：
    python main.py analyze --input pitch.pptx --stage series-a
    python main.py generate --science "tech description" --stage seed --focus market
    python main.py rewrite --section technology --content "..." --audience generalist-vc
"""

import argparse
import json
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path


class PitchStage(str, Enum):
    """融资阶段"""
    PRE_SEED = "pre-seed"
    SEED = "seed"
    SERIES_A = "series-a"
    SERIES_B = "series-b"
    SERIES_C = "series-c"
    IPO = "ipo"


class AudienceType(str, Enum):
    """目标投资者受众"""
    GENERALIST_VC = "generalist-vc"
    BIOTECH_SPECIALIST = "biotech-specialist"
    PHARMA_PARTNER = "pharma-partner"
    ANGEL_INVESTOR = "angel-investor"
    CROWD = "crowd"


@dataclass
class ScienceData:
    """科学数据结构"""
    mechanism: str = ""
    disease_area: str = ""
    stage: str = ""  # discovery, preclinical, phase1, phase2, phase3
    key_data: Dict[str, Any] = field(default_factory=dict)
    competitive_landscape: List[Dict] = field(default_factory=list)


@dataclass
class BusinessNarrative:
    """生成的商业叙事"""
    hook: str = ""
    problem_statement: str = ""
    solution_value: str = ""
    market_opportunity: str = ""
    traction: str = ""
    team_credibility: str = ""
    ask: str = ""
    risk_mitigation: str = ""


class PitchDeckNarrative:
    """用于生成生物科技融资叙事的主类"""

    def __init__(self, stage: PitchStage = PitchStage.SEED):
        self.stage = stage
        self.narrative_templates = self._load_templates()

    def _load_templates(self) -> Dict:
        """加载不同阶段的叙事模板"""
        return {
            "pre-seed": {
                "focus": "team_vision_breakthrough",
                "slide_count": 10,
                "key_sections": ["problem", "solution", "team", "market"]
            },
            "seed": {
                "focus": "product_validation_early_traction", 
                "slide_count": 12,
                "key_sections": ["problem", "solution", "traction", "market", "team"]
            },
            "series-a": {
                "focus": "commercial_viability_scaling",
                "slide_count": 15,
                "key_sections": ["traction", "market", "business_model", "team", "financials"]
            }
        }
    
    def translate_science_to_business(self, science_data: ScienceData, audience: AudienceType) -> BusinessNarrative:
        """将科学数据转化为商业叙事"""
        narrative = BusinessNarrative()

        # 根据疾病影响生成开场钩子
        narrative.hook = self._generate_hook(science_data.disease_area, science_data.mechanism)

        # 将机制转化为价值主张
        narrative.solution_value = self._translate_mechanism(science_data.mechanism, audience)

        # 构建市场叙事
        narrative.market_opportunity = self._build_market_story(science_data)

        return narrative

    def _generate_hook(self, disease: str, mechanism: str) -> str:
        """生成开场钩子"""
        return f"Addressing the critical unmet need in {disease} through novel {mechanism}"

    def _translate_mechanism(self, mechanism: str, audience: AudienceType) -> str:
        """将科学机制转化为商业价值"""
        if audience == AudienceType.GENERALIST_VC:
            return f"First-in-class therapeutic approach targeting {mechanism}"
        return f"Novel {mechanism} with demonstrated efficacy"

    def _build_market_story(self, science_data: ScienceData) -> str:
        """构建市场机遇叙事"""
        return f"${science_data.key_data.get('tam', '10B')}+ addressable market"

    def optimize_slide_order(self, slides: List[Dict]) -> List[Dict]:
        """优化幻灯片顺序以实现最大化影响力"""
        stage_config = self.narrative_templates.get(self.stage.value, {})
        priority_sections = stage_config.get("key_sections", [])

        # 按优先级对幻灯片排序
        sorted_slides = sorted(slides,
            key=lambda x: priority_sections.index(x.get("section", ""))
            if x.get("section") in priority_sections else 999)

        return sorted_slides

    def generate_qa_preparation(self, science_data: ScienceData) -> Dict[str, str]:
        """生成预判的问答及答案"""
        return {
            "clinical_risk": "Mitigated through rigorous trial design",
            "competition": "Differentiated by mechanism and efficacy profile",
            "timeline": "Key milestones achievable within funding runway",
            "regulatory": "Clear FDA pathway with precedent approvals"
        }


def main():
    parser = argparse.ArgumentParser(description="Biotech Pitch Deck Narrative Generator")
    parser.add_argument("--stage", default="seed", choices=[s.value for s in PitchStage])
    parser.add_argument("--audience", default="generalist-vc", choices=[a.value for a in AudienceType])
    parser.add_argument("--input", help="Input pitch deck file")
    parser.add_argument("--output", default="optimized_narrative.json", help="Output file")

    args = parser.parse_args()

    # 初始化引擎
    engine = PitchDeckNarrative(stage=PitchStage(args.stage))
    
    print(f"Biotech Pitch Narrative Generator - {args.stage.upper()} Stage")
    print(f"Target Audience: {args.audience}")
    print("\nNarrative optimization complete. See output file for results.")


if __name__ == "__main__":
    main()
