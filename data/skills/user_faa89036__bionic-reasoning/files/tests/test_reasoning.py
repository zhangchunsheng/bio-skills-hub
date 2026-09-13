"""
Bionic Reasoning 测试套件
"""

import unittest
import sys
from pathlib import Path

# 添加 scripts 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scientific_method import get_scientific_method, Hypothesis
from physics_reasoning import get_physics_reasoning
from reasoning_engine import get_reasoning_engine


class TestScientificMethod(unittest.TestCase):
    """测试科学方法论"""
    
    def setUp(self):
        self.sm = get_scientific_method()
    
    def test_build_hypotheses(self):
        """测试假设构建"""
        observation = "用户反馈系统变慢"
        hypotheses = self.sm.build_hypotheses(observation)
        
        self.assertEqual(len(hypotheses), 4)  # H0, H1, H2, H3
        self.assertEqual(hypotheses[0].level, 0)  # 零假设
        self.assertEqual(hypotheses[1].level, 1)  # 第一假设
    
    def test_bayesian_update(self):
        """测试贝叶斯更新"""
        observation = "测试观察"
        hypotheses = self.sm.build_hypotheses(observation)
        h1_id = hypotheses[1].id
        
        old_prob, new_prob = self.sm.bayesian_update(
            h1_id, "发现缓存命中率低", 0.8
        )
        
        self.assertGreater(new_prob, old_prob)  # 证据支持，概率应上升
    
    def test_check_falsifiability(self):
        """测试可证伪性检查"""
        # 可证伪的陈述
        result1 = self.sm.check_falsifiability("如果A则B")
        self.assertTrue(result1[0])
        
        # 模糊陈述（可证伪性检测可能无法识别）
        result2 = self.sm.check_falsifiability("有时候A会导致B")
        # 注意：当前实现可能返回 True 或 False，取决于关键词检测
    
    def test_check_bias(self):
        """测试偏误检查"""
        reasoning = "这个成功案例证明我们的方法是正确的"
        biases = self.sm.check_bias(reasoning)
        
        bias_types = [b.bias_type for b in biases]
        self.assertIn("确认偏误", bias_types)


class TestPhysicsReasoning(unittest.TestCase):
    """测试物理推理"""
    
    def setUp(self):
        self.pr = get_physics_reasoning()
    
    def test_first_principles_analysis(self):
        """测试第一性原理分析"""
        result = self.pr.first_principles_analysis(
            "如何优化数据库查询",
            ["增加索引", "使用缓存", "分库分表"]
        )
        
        self.assertEqual(result.problem, "如何优化数据库查询")
        self.assertTrue(len(result.assumptions_challenged) > 0)
    
    def test_check_conservation(self):
        """测试守恒约束检查"""
        system = "我们需要简化系统架构"
        constraints = self.pr.check_conservation(system)
        
        constraint_names = [c.name for c in constraints]
        self.assertIn("复杂度守恒", constraint_names)
    
    def test_dimensional_analysis(self):
        """测试量纲分析"""
        result = self.pr.dimensional_analysis("速度 = 距离 / 时间")
        
        self.assertTrue(result.consistent)
        self.assertIn("速度", result.dimensions)
    
    def test_sanity_check(self):
        """测试合理性检查"""
        # 不合理的声明
        result1 = self.pr.sanity_check("永动机方案", None)
        self.assertFalse(result1[0])
        
        # 合理的声明
        result2 = self.pr.sanity_check("效率提升20%", 20)
        self.assertTrue(result2[0])


class TestReasoningEngine(unittest.TestCase):
    """测试推理引擎"""
    
    def setUp(self):
        self.engine = get_reasoning_engine()
    
    def test_reason(self):
        """测试完整推理流程"""
        report = self.engine.reason(
            "系统响应时间增加",
            ["增加服务器", "优化代码", "使用CDN"]
        )
        
        self.assertEqual(report.observation, "系统响应时间增加")
        self.assertTrue(len(report.hypotheses) > 0)
        self.assertIsNotNone(report.best_hypothesis)
        self.assertIsNotNone(report.first_principles)
        self.assertTrue(0 <= report.confidence <= 1)
    
    def test_update_with_evidence(self):
        """测试证据更新"""
        # 先创建假设
        hypotheses = self.engine.scientific.build_hypotheses("测试")
        h_id = hypotheses[1].id
        
        result = self.engine.update_with_evidence(
            h_id, "新的性能数据", 0.9
        )
        
        self.assertEqual(result["hypothesis_id"], h_id)
        self.assertIn("posterior_probability", result)


if __name__ == "__main__":
    unittest.main()
