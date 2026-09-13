"""
编排器 - 整合工作记忆、任务调度、内心独白
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from working_memory import get_working_memory, WorkingMemoryBuffer
from task_scheduler import get_task_scheduler, ComplexityLevel
from self_talk import get_self_talk


@dataclass
class ExecutionReport:
    """执行报告"""
    task_title: str
    workflow_id: str
    complexity: str
    status: str
    decisions_count: int
    self_talk_insights: List[str]
    recommendations: List[str]


class Orchestrator:
    """仿生编排器"""
    
    def __init__(self):
        self.wm = get_working_memory()
        self.scheduler = get_task_scheduler()
        self.self_talk = get_self_talk()
    
    def start_task(self, task_title: str, intent: str,
                   constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        启动新任务
        
        Args:
            task_title: 任务标题
            intent: 用户意图
            constraints: 约束列表
            
        Returns:
            任务启动信息
        """
        # L1: 初始化工作记忆
        buffer = self.wm.initialize(task_title, intent, constraints)
        
        # L2: 创建调度工作流
        workflow = self.scheduler.create_workflow(task_title, intent)
        
        # L3: 执行前独白
        monologue = self.self_talk.pre_execution(
            buffer.session_id, intent
        )
        
        return {
            "session_id": buffer.session_id,
            "workflow_id": workflow.workflow_id,
            "complexity": workflow.complexity.name,
            "steps_count": len(workflow.steps),
            "insights": monologue.insights
        }
    
    def execute_step(self, workflow_id: str,
                    step_executor: Callable[[Any], dict]) -> Dict[str, Any]:
        """
        执行工作流步骤
        
        Args:
            workflow_id: 工作流ID
            step_executor: 步骤执行函数
            
        Returns:
            执行结果
        """
        # 执行步骤
        step = self.scheduler.execute_step(workflow_id, step_executor)
        
        # L1: 记录决策到工作记忆
        if step.result:
            self.wm.record_decision(
                action=step.action,
                reason=f"执行 {step.skill} 的 {step.action}",
                alternative=""
            )
        
        # 获取下一步信息
        next_step = self.scheduler.get_next_step(workflow_id)
        
        return {
            "step_completed": step.name,
            "status": step.status,
            "next_step": next_step.name if next_step else None,
            "progress": self.scheduler.get_workflow_status(workflow_id)["progress"]
        }
    
    def decision_branch(self, workflow_id: str, 
                       options: List[str]) -> Dict[str, Any]:
        """
        决策分支处理
        
        Args:
            workflow_id: 工作流ID
            options: 可选方案
            
        Returns:
            决策建议
        """
        workflow = self.scheduler.workflows.get(workflow_id)
        if not workflow:
            return {"error": "工作流不存在"}
        
        # L3: 内心独白权衡
        monologue = self.self_talk.during_execution(
            workflow_id,
            workflow.steps[workflow.current_step].name if workflow.current_step < len(workflow.steps) else "未知",
            {"options": options}
        )
        
        # 基于独白生成建议
        recommendation = "基于当前分析，建议选择方案 1"
        
        return {
            "options": options,
            "recommendation": recommendation,
            "insights": monologue.insights
        }
    
    def complete_task(self, workflow_id: str, 
                     success: bool = True) -> ExecutionReport:
        """
        完成任务
        
        Args:
            workflow_id: 工作流ID
            success: 是否成功
            
        Returns:
            执行报告
        """
        workflow = self.scheduler.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流 {workflow_id} 不存在")
        
        # L3: 复盘独白
        monologue = self.self_talk.post_execution(
            workflow_id,
            {"success": success, "novelty": 0.5}
        )
        
        # L1: 归档工作记忆
        self.wm.archive()
        
        # 生成报告
        recommendations = []
        
        # 检查是否有高价值发现
        if self.self_talk.has_high_value_finding(workflow_id):
            recommendations.append("[推送] 高价值发现已标记，建议推送到 dream-memory")
        
        # 生成建议
        if success:
            recommendations.append("任务成功完成，执行模式已记录")
        else:
            recommendations.append("任务遇到问题，建议复盘失败原因")
        
        return ExecutionReport(
            task_title=workflow.task_title,
            workflow_id=workflow_id,
            complexity=workflow.complexity.name,
            status="completed" if success else "failed",
            decisions_count=len(workflow.steps),
            self_talk_insights=monologue.insights,
            recommendations=recommendations
        )
    
    def get_task_summary(self) -> Dict[str, Any]:
        """获取当前任务摘要"""
        wm_summary = self.wm.get_summary()
        
        if wm_summary.get("status") == "no_active_task":
            return {"status": "no_active_task"}
        
        # 查找对应的工作流
        workflow_status = None
        for wf_id, wf in self.scheduler.workflows.items():
            if wf.task_title == wm_summary.get("task_title"):
                workflow_status = self.scheduler.get_workflow_status(wf_id)
                break
        
        return {
            "working_memory": wm_summary,
            "workflow": workflow_status
        }
    
    def check_forgetfulness(self) -> Optional[str]:
        """检查是否需要防遗忘提醒"""
        # 增加轮次计数
        needs_reminder = self.wm.increment_turn()
        
        if needs_reminder:
            return self.wm.get_forgetfulness_reminder()
        
        return None


# 单例模式
_orchestrator_instance: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """获取编排器单例"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance
