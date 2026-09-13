#!/usr/bin/env python3
"""
Bionic Cognition 测试套件
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from intent_decoder import IntentDecoder, IntentType, get_intent_decoder


class TestIntentDecoder(unittest.TestCase):
    """测试意图解码器"""
    
    def setUp(self):
        self.decoder = IntentDecoder()
    
    def test_decode_create(self):
        """测试创建意图"""
        intent = self.decoder.decode("创建一个 Python 文件")
        self.assertEqual(intent.intent_type, "create")
        self.assertGreater(intent.confidence, 0)
    
    def test_decode_analyze(self):
        """测试分析意图"""
        intent = self.decoder.decode("分析这个代码的性能")
        self.assertEqual(intent.intent_type, "analyze")
    
    def test_decode_transform(self):
        """测试转换意图"""
        intent = self.decoder.decode("把文档转换成 PDF")
        self.assertEqual(intent.intent_type, "transform")
    
    def test_extract_entities(self):
        """测试实体提取"""
        intent = self.decoder.decode("创建 test.py 文件")
        self.assertIn("py", intent.entities.get("formats", []))
    
    def test_extract_target(self):
        """测试目标提取"""
        intent = self.decoder.decode("帮我创建一个报告")
        self.assertIsNotNone(intent.target)


def run_tests():
    """运行测试"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIntentDecoder)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
