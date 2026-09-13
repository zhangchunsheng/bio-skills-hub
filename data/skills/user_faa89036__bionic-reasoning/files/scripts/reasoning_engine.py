"""
推理引擎 - 整合科学方法论和物理推理
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from scientific_method import get_scientific_method, Hypothesis
from physics_reasoning import get_physics_reasoning, FirstPrinciple


@dataclass
class ReasoningReport:
    """推理报告"""
    observation: str
    hypotheses: List[Hypothesis]
    best_hypothesis: Optional[Hypothesis]
    first_principles: Optional[FirstPrinciple]
    bias_checks: List[dict]
    conservation_checks: List[dict]
    dimensional_analysis: Optional[dict]
    sanity_check: tuple
    recommendations: List[str]
    confidence: float


class ReasoningEngine:
    """推理引擎 - 整合两层推理"""
    
    def __init__(self):
        self.scientific = get_scientific_method()
        self.physics = get_physics_reasoning()
    
    def reason(self, observation: str, 
               analogy_solutions: Optional[List[str]] = None) -> ReasoningReport:
        """
        执行完整推理流程
        
        Args:
            observation: 观察/问题
            analogy_solutions: 基于类比的解决方案（可选）
            
        Returns:
            推理报告
        """
        recommendations = []
        
        # L1: 科学方法论
        # 1. 构建假设
        hypotheses = self.scientific.build_hypotheses(observation)
        best_h = self.scientific.get_best_hypothesis(observation)
        
        # 2. 偏误检查
        bias_checks = self.scientific.check_bias(observation)
        bias_dicts = [
            {
                "type": b.bias_type,
                "detected": b.detected,
                "severity": b.severity,
                "suggestion": b.suggestion
            }
            for b in bias_checks
        ]
        
        for bias in bias_checks:
            if bias.detected:
                recommendations.append(f"[偏误警告] {bias.bias_type}: {bias.suggestion}")
        
        # L2: 物理推理
        # 3. 第一性原理分析
        first_principles = None
        if analogy_solutions:
            first_principles = self.physics.first_principles_analysis(
                observation, analogy_solutions
            )
            recommendations.append(
                f"[第一性原理] {first_principles.conclusion}"
            )
        
        # 4. 守恒约束检查
        conservation = self.physics.check_conservation(observation)
        conservation_dicts = [
            {"name": c.name, "type": c.type, "description": c.description}
            for c in conservation
        ]
        
        for cons in conservation:
            recommendations.append(
                f"[约束检查] {cons.name}: {cons.description}"
            )
        
        # 5. 量纲分析
        dim_analysis = self.physics.dimensional_analysis(observation)
        dim_dict = None
        if dim_analysis.dimensions:
            dim_dict = {
                "expression": dim_analysis.expression,
                "dimensions": dim_analysis.dimensions,
                "consistent": dim_analysis.consistent,
                "issues": dim_analysis.issues
            }
            if not dim_analysis.consistent:
                recommendations.append(
                    f"[量纲错误] {'; '.join(dim_analysis.issues)}"
                )
        
        # 6. 合理性检查
        sanity = self.physics.sanity_check(observation)
        if not sanity[0]:
            recommendations.append(f"[合理性警告] {sanity[1]}")
        
        # 计算整体置信度
        if best_h:
            confidence = best_h.posterior_probability
            # 根据偏误和约束调整
            if any(b.detected and b.severity == "high" for b in bias_checks):
                confidence *= 0.7
            if not sanity[0]:
                confidence *= 0.5
        else:
            confidence = 0.5
        
        return ReasoningReport(
            observation=observation,
            hypotheses=hypotheses,
            best_hypothesis=best_h,
            first_principles=first_principles,
            bias_checks=bias_dicts,
            conservation_checks=conservation_dicts,
            dimensional_analysis=dim_dict,
            sanity_check=sanity,
            recommendations=recommendations,
            confidence=round(confidence, 2)
        )
    
    def update_with_evidence(self, hypothesis_id: str, 
                            evidence: str, 
                            likelihood: float) -> Dict[str, Any]:
        """
        用新证据更新假设置信度
        
        Args:
            hypothesis_id: 假设ID
            evidence: 证据描述
            likelihood: 似然 P(E|H)
            
        Returns:
            更新结果
        """
        old_prob, new_prob = self.scientific.bayesian_update(
            hypothesis_id, evidence, likelihood
        )
        
        return {
            "hypothesis_id": hypothesis_id,
            "evidence": evidence,
            "prior_probability": round(old_prob, 4),
            "posterior_probability": round(new_prob, 4),
            "change": round(new_prob - old_prob, 4),
            "significant": abs(new_prob - old_prob) > 0.1
        }


# 单例模式
_reasoning_engine_instance: Optional[ReasoningEngine] = None


def get_reasoning_engine() -> ReasoningEngine:
    """获取推理引擎单例"""
    global _reasoning_engine_instance
    if _reasoning_engine_instance is None:
        _reasoning_engine_instance = ReasoningEngine()
    return _reasoning_engine_instance
