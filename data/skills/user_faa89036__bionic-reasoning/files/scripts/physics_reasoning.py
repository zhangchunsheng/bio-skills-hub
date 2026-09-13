"""
物理推理 - L2 推理层
实现第一性原理、约束守恒、量纲分析
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


@dataclass
class Constraint:
    """约束对象"""
    name: str
    type: str  # conservation, boundary, invariant
    description: str
    check_function: str  # 描述如何检查


@dataclass
class DimensionalAnalysis:
    """量纲分析结果"""
    expression: str
    dimensions: Dict[str, str]  # 变量 -> 量纲
    consistent: bool
    issues: List[str]


@dataclass
class FirstPrinciple:
    """第一性原理分析"""
    problem: str
    basic_facts: List[str]
    assumptions_challenged: List[str]
    conclusion: str


class PhysicsReasoning:
    """物理推理实现"""
    
    def __init__(self):
        # 常见量纲定义
        self.dimensions = {
            # 基本量纲
            '长度': 'L', '距离': 'L', '宽度': 'L', '高度': 'L',
            '质量': 'M', '重量': 'M',
            '时间': 'T', '时长': 'T', '周期': 'T',
            '电流': 'I',
            '温度': 'Θ',
            # 导出量纲
            '速度': 'L/T', '速率': 'L/T',
            '加速度': 'L/T²',
            '力': 'ML/T²',
            '能量': 'ML²/T²', '功': 'ML²/T²',
            '功率': 'ML²/T³',
            '密度': 'M/L³',
            '频率': '1/T',
            '压力': 'M/LT²',
        }
        
        # 守恒约束
        self.conservation_constraints = [
            Constraint("能量守恒", "conservation", "能量不会凭空产生或消失", "检查输入输出能量平衡"),
            Constraint("信息守恒", "conservation", "信息不会凭空产生", "检查信息来源和传递路径"),
            Constraint("复杂度守恒", "conservation", "简化一端必然复杂化另一端", "检查系统整体复杂度"),
        ]
    
    def first_principles_analysis(self, problem: str, 
                                   analogy_based_solutions: List[str]) -> FirstPrinciple:
        """
        第一性原理分析
        从最基本事实出发，不依赖类比
        
        Args:
            problem: 问题描述
            analogy_based_solutions: 基于类比的解决方案（需要质疑）
            
        Returns:
            第一性原理分析结果
        """
        # 提取基本事实（简化实现）
        basic_facts = [
            f"问题 '{problem}' 的核心需求是什么？",
            "必须满足的硬性约束有哪些？",
            "现有资源和技术能力的边界在哪里？"
        ]
        
        # 质疑类比
        assumptions_challenged = []
        for solution in analogy_based_solutions:
            assumptions_challenged.append(
                f"质疑: '{solution}' 是基于类比，其背后的第一性原理是什么？"
            )
            assumptions_challenged.append(
                f"验证: 该方案是否满足问题的核心约束？"
            )
        
        # 生成结论
        conclusion = (
            f"基于第一性原理，'{problem}' 应该从最基本约束出发重新分析，"
            f"而不是直接套用 {len(analogy_based_solutions)} 个类比方案。"
        )
        
        return FirstPrinciple(
            problem=problem,
            basic_facts=basic_facts,
            assumptions_challenged=assumptions_challenged,
            conclusion=conclusion
        )
    
    def check_conservation(self, system_description: str) -> List[Constraint]:
        """
        检查系统是否违反守恒约束
        
        Args:
            system_description: 系统描述
            
        Returns:
            被触发的约束列表
        """
        triggered = []
        
        # 能量相关检查
        if any(kw in system_description for kw in ["能量", "消耗", "产生", "转化"]):
            triggered.append(self.conservation_constraints[0])
        
        # 信息相关检查
        if any(kw in system_description for kw in ["信息", "数据", "知识", "生成"]):
            triggered.append(self.conservation_constraints[1])
        
        # 复杂度相关检查
        if any(kw in system_description for kw in ["简化", "复杂", "优化", "重构"]):
            triggered.append(self.conservation_constraints[2])
        
        return triggered
    
    def dimensional_analysis(self, expression: str) -> DimensionalAnalysis:
        """
        量纲分析
        检查表达式的量纲一致性
        
        Args:
            expression: 数学表达式或公式
            
        Returns:
            量纲分析结果
        """
        dimensions = {}
        issues = []
        
        # 提取表达式中的变量和数值
        # 简化实现：识别常见的物理量词汇
        for quantity, dim in self.dimensions.items():
            if quantity in expression:
                dimensions[quantity] = dim
        
        # 检查常见物理公式
        # 速度 = 距离 / 时间
        if "速度" in expression and ("距离" in expression or "时间" in expression):
            if "距离" in expression and "时间" in expression:
                pass  # 量纲正确 [L/T]
            else:
                issues.append("速度公式缺少距离或时间")
        
        # 密度 = 质量 / 体积
        if "密度" in expression:
            if "质量" not in expression or "体积" not in expression:
                issues.append("密度公式需要质量和体积")
        
        # 力 = 质量 × 加速度
        if "力" in expression:
            if "质量" not in expression:
                issues.append("力的计算需要质量")
        
        consistent = len(issues) == 0
        
        return DimensionalAnalysis(
            expression=expression,
            dimensions=dimensions,
            consistent=consistent,
            issues=issues
        )
    
    def estimate_order_of_magnitude(self, value: float, 
                                     context: str) -> Tuple[float, str]:
        """
        数量级估算（费米估算）
        
        Args:
            value: 数值
            context: 上下文
            
        Returns:
            (数量级, 评估说明)
        """
        if value <= 0:
            return 0, "数值必须为正"
        
        magnitude = math.floor(math.log10(value))
        
        assessments = {
            -12: "皮米级 - 原子核尺度",
            -9: "纳米级 - 分子尺度",
            -6: "微米级 - 细胞尺度",
            -3: "毫米级 - 昆虫尺度",
            0: "米级 - 人体尺度",
            3: "千米级 - 城市尺度",
            6: "百万级 - 国家尺度",
            9: "十亿级 - 全球尺度",
        }
        
        # 找到最接近的评估
        closest = min(assessments.keys(), key=lambda x: abs(x - magnitude))
        assessment = assessments.get(closest, f"10^{magnitude} 量级")
        
        return magnitude, f"{context}: {assessment} (实际: 10^{magnitude})"
    
    def sanity_check(self, claim: str, numerical_value: Optional[float] = None) -> Tuple[bool, str]:
        """
        合理性检查
        
        Args:
            claim: 声明
            numerical_value: 数值（如果有）
            
        Returns:
            (是否合理, 说明)
        """
        issues = []
        
        # 检查超光速
        if numerical_value and "速度" in claim and numerical_value > 3e8:
            issues.append("速度超过光速，违反物理定律")
        
        # 检查永动机
        if any(kw in claim for kw in ["永动", "无限能量", "无中生有"]):
            issues.append("违反能量守恒定律")
        
        # 检查效率 > 100%
        if numerical_value and "效率" in claim and numerical_value > 100:
            issues.append("效率超过100%，违反热力学定律")
        
        # 检查负概率
        if numerical_value and "概率" in claim and (numerical_value < 0 or numerical_value > 1):
            issues.append("概率必须在0-1之间")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, "声明通过基本物理合理性检查"


# 导入 math 用于数量级计算
import math

# 单例模式
_physics_reasoning_instance: Optional[PhysicsReasoning] = None


def get_physics_reasoning() -> PhysicsReasoning:
    """获取物理推理单例"""
    global _physics_reasoning_instance
    if _physics_reasoning_instance is None:
        _physics_reasoning_instance = PhysicsReasoning()
    return _physics_reasoning_instance
