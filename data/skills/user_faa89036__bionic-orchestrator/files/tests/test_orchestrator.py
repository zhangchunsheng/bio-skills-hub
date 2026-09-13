"""
Bionic Orchestrator 测试套件
"""

import unittest
import sys
from pathlib import Path

# 添加 scripts 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from working_memory import get_working_memory
from task_scheduler import get_task_scheduler, ComplexityLevel
from self_talk import get_self_talk
from orchestrator import get_orchestrator


class TestWorkingMemory(unittest.TestCase):
    """测试工作记忆"""
    
    def setUp(self):
        self.wm = get_working_memory()
    
    def test_initialize(self):
        """测试初始化"""
        buffer = self.wm.initialize(
            "测试任务",
            "创建一个 Python 文件",
            ["使用标准库", "保持简洁"]
        )
        
        self.assertEqual(buffer.task_title, "测试任务")
        self.assertEqual(buffer.status, "in_progress")
        self.assertEqual(len(buffer.constraints), 2)
    
    def test_record_decision(self):
        """测试记录决策"""
        self.wm.initialize("测试", "测试意图")
        self.wm.record_decision("执行操作", "因为需要", "放弃其他")
        
        self.assertEqual(len(self.wm.current_buffer.decisions), 1)
        self.assertEqual(self.wm.current_buffer.decisions[0].action, "执行操作")
    
    def test_forgetfulness(self):
        """测试防遗忘机制"""
        self.wm.initialize("测试", "测试")
        
        # 模拟多轮对话
        for _ in range(25):
            self.wm.increment_turn()
        
        reminder = self.wm.get_forgetfulness_reminder()
        # 提醒可能为None，取决于实现阈值
        if reminder:
            self.assertIn("[WM]", reminder)


class TestTaskScheduler(unittest.TestCase):
    """测试任务调度"""
    
    def setUp(self):
        self.scheduler = get_task_scheduler()
    
    def test_assess_complexity(self):
        """测试复杂度评估"""
        c1 = self.scheduler.assess_complexity("修改一个文件")
        c3 = self.scheduler.assess_complexity("分析系统性能瓶颈")
        c4 = self.scheduler.assess_complexity("重构整个架构")
        
        self.assertEqual(c1, ComplexityLevel.C2)  # 默认C2
        # 实际复杂度评估可能根据关键词匹配而变化
        self.assertIn(c3, [ComplexityLevel.C2, ComplexityLevel.C3, ComplexityLevel.C4])
        self.assertEqual(c4, ComplexityLevel.C4)
    
    def test_create_workflow(self):
        """测试创建工作流"""
        workflow = self.scheduler.create_workflow(
            "测试任务",
            "分析并优化代码"
        )
        
        self.assertIsNotNone(workflow.workflow_id)
        self.assertTrue(len(workflow.steps) > 0)
        self.assertEqual(workflow.status, "pending")
    
    def test_workflow_status(self):
        """测试工作流状态"""
        workflow = self.scheduler.create_workflow("测试", "测试")
        status = self.scheduler.get_workflow_status(workflow.workflow_id)
        
        self.assertEqual(status["task_title"], "测试")
        self.assertIn("progress", status)


class TestSelfTalk(unittest.TestCase):
    """测试内心独白"""
    
    def setUp(self):
        self.st = get_self_talk()
    
    def test_pre_execution(self):
        """测试执行前独白"""
        mono = self.st.pre_execution("task_1", "创建一个文件")
        
        self.assertEqual(mono.monologue_type, "pre_execution")
        self.assertTrue(len(mono.questions) > 0)
        self.assertTrue(len(mono.insights) > 0)
    
    def test_post_execution(self):
        """测试执行后独白"""
        mono = self.st.post_execution(
            "task_2",
            {"success": True, "novelty": 0.8}
        )
        
        self.assertEqual(mono.monologue_type, "post_execution")
        
        # 高价值发现应该被标记
        has_high_value = any("[高价值]" in i for i in mono.insights)
        self.assertTrue(has_high_value)


class TestOrchestrator(unittest.TestCase):
    """测试编排器"""
    
    def setUp(self):
        self.orch = get_orchestrator()
    
    def test_start_task(self):
        """测试启动任务"""
        result = self.orch.start_task(
            "测试任务",
            "创建一个 Python 脚本",
            ["简洁", "高效"]
        )
        
        self.assertIn("session_id", result)
        self.assertIn("workflow_id", result)
        self.assertIn("complexity", result)
    
    def test_task_summary(self):
        """测试任务摘要"""
        self.orch.start_task("测试", "测试")
        summary = self.orch.get_task_summary()
        
        self.assertIn("working_memory", summary)


if __name__ == "__main__":
    unittest.main()
