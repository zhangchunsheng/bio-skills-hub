#!/usr/bin/env python3
"""
Bionic Guard 测试套件
"""

import sys
import unittest
from pathlib import Path

# 添加脚本路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from acc_monitor import ACCMonitor, ConflictType, get_acc_monitor
from risk_sniffer import RiskSniffer, RiskLevel, get_risk_sniffer
from immune_system import ImmuneSystem, get_immune_system


class TestACCMonitor(unittest.TestCase):
    """测试 ACC 冲突监测器"""
    
    def setUp(self):
        self.acc = ACCMonitor()
    
    def test_detect_conflict(self):
        """测试冲突检测"""
        event = self.acc.detect_conflict(
            operation="test_op",
            expected="success",
            actual="error",
            context="test"
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.conflict_type, "unexpected_result")
    
    def test_no_conflict(self):
        """测试无冲突情况"""
        event = self.acc.detect_conflict(
            operation="test_op",
            expected="same",
            actual="same"
        )
        self.assertIsNone(event)
    
    def test_check_syntax(self):
        """测试语法检查"""
        bad_code = "def foo():\n    print('missing"
        event = self.acc.check_syntax(bad_code)
        self.assertIsNotNone(event)
        self.assertEqual(event.conflict_type, "syntax_error")
        
        good_code = "def foo():\n    print('ok')"
        event = self.acc.check_syntax(good_code)
        self.assertIsNone(event)
    
    def test_state_consistency(self):
        """测试状态一致性检查"""
        event = self.acc.check_state_consistency(
            current_state={"status": "error"},
            expected_state={"status": "ok"},
            operation="test"
        )
        self.assertIsNotNone(event)


class TestRiskSniffer(unittest.TestCase):
    """测试杏仁核风险嗅探器"""
    
    def setUp(self):
        self.sniffer = RiskSniffer()
    
    def test_sniff_destructive(self):
        """测试破坏性操作检测"""
        code = "rm -rf /important"
        risks = self.sniffer.sniff(code, "test")
        self.assertTrue(len(risks) > 0)
        
        risk_types = [r.category for r in risks]
        self.assertIn("destructive_operation", risk_types)
    
    def test_sniff_security(self):
        """测试安全凭证检测"""
        code = 'password = "secret123"'
        risks = self.sniffer.sniff(code, "test")
        
        risk_types = [r.category for r in risks]
        self.assertIn("credential_exposure", risk_types)
    
    def test_whitelist(self):
        """测试白名单功能"""
        pattern = "test_pattern"
        self.sniffer.add_to_whitelist(pattern)
        self.assertIn(pattern, self.sniffer.whitelist)


class TestImmuneSystem(unittest.TestCase):
    """测试免疫系统"""
    
    def setUp(self):
        self.immune = ImmuneSystem()
    
    def test_scan_threat(self):
        """测试威胁扫描"""
        code = "eval(user_input)"
        threats = self.immune.scan(code, "test.py")
        self.assertTrue(len(threats) > 0)
    
    def test_learn_threat(self):
        """测试学习新威胁"""
        sig_id = self.immune.learn(
            pattern="test_threat",
            threat_type="test",
            severity=3,
            description="Test threat",
            mitigation="Test mitigation"
        )
        self.assertIsNotNone(sig_id)
        self.assertIn(sig_id, self.immune.signatures)
    
    def test_threat_report(self):
        """测试威胁报告"""
        report = self.immune.get_threat_report()
        self.assertIn("total_signatures", report)
        self.assertIn("by_type", report)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestACCMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskSniffer))
    suite.addTests(loader.loadTestsFromTestCase(TestImmuneSystem))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
