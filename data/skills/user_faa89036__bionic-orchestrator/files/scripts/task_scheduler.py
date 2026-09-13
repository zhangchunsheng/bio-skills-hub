"""
任务调度 - L2 编排层
实现复杂度评估、策略选择、异常处理
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Callable
from datetime import datetime
from enum import Enum


class ComplexityLevel(Enum):
    """复杂度等级"""
    C1 = 1  # 简单 - 仅 Orchestrator
    C2 = 2  # 中等 - + Guard + Cognition
    C3 = 3  # 复杂 - + Reasoning
    C4 = 4  # 极复杂 - + Swarm + 其他


@dataclass
class TaskStep:
    """任务步骤"""
    step_id: str
    name: str
    skill: str
    action: str
    status: str  # pending, running, completed, failed
    result: Optional[dict]
    started_at: Optional[str]
    completed_at: Optional[str]
    error: Optional[str]


@dataclass
class Workflow:
    """工作流"""
    workflow_id: str
    task_title: str
    complexity: ComplexityLevel
    steps: List[TaskStep]
    current_step: int
    status: str
    created_at: str
    updated_at: str


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".workbuddy" / "dreams" / "bionic-orchestrator"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.workflow_log_file = self.data_dir / "workflow-log.json"
        self.workflows: Dict[str, Workflow] = {}
        self._load_workflows()
    
    def _load_workflows(self):
        """加载工作流历史"""
        if self.workflow_log_file.exists():
            try:
                with open(self.workflow_log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for wf_data in data.get("workflows", []):
                        wf = self._dict_to_workflow(wf_data)
                        self.workflows[wf.workflow_id] = wf
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    
    def _save_workflows(self):
        """保存工作流"""
        with open(self.workflow_log_file, 'w', encoding='utf-8') as f:
            json.dump({
                "workflows": [self._workflow_to_dict(wf) for wf in self.workflows.values()],
                "updated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def _workflow_to_dict(self, wf: Workflow) -> dict:
        return {
            "workflow_id": wf.workflow_id,
            "task_title": wf.task_title,
            "complexity": wf.complexity.value,
            "steps": [asdict(s) for s in wf.steps],
            "current_step": wf.current_step,
            "status": wf.status,
            "created_at": wf.created_at,
            "updated_at": wf.updated_at
        }
    
    def _dict_to_workflow(self, data: dict) -> Workflow:
        steps = [TaskStep(**s) for s in data.get("steps", [])]
        return Workflow(
            workflow_id=data["workflow_id"],
            task_title=data["task_title"],
            complexity=ComplexityLevel(data.get("complexity", 2)),
            steps=steps,
            current_step=data.get("current_step", 0),
            status=data["status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
    
    def assess_complexity(self, task_description: str) -> ComplexityLevel:
        """
        评估任务复杂度
        
        Args:
            task_description: 任务描述
            
        Returns:
            复杂度等级
        """
        # 复杂度指标
        c4_keywords = ["系统", "架构", "重构", "迁移", "整合", "全流程"]
        c3_keywords = ["分析", "推理", "验证", "因果", "预测", "优化"]
        c2_keywords = ["检查", "修改", "更新", "添加", "删除"]
        
        task_lower = task_description.lower()
        
        # 检查 C4 关键词
        if any(kw in task_lower for kw in c4_keywords):
            return ComplexityLevel.C4
        
        # 检查 C3 关键词
        if any(kw in task_lower for kw in c3_keywords):
            return ComplexityLevel.C3
        
        # 检查 C2 关键词
        if any(kw in task_lower for kw in c2_keywords):
            return ComplexityLevel.C2
        
        # 默认 C3（保守处理）
        return ComplexityLevel.C3
    
    def create_workflow(self, task_title: str, 
                       task_description: str) -> Workflow:
        """
        创建工作流
        
        Args:
            task_title: 任务标题
            task_description: 任务描述
            
        Returns:
            工作流对象
        """
        complexity = self.assess_complexity(task_description)
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        timestamp = datetime.now().isoformat()
        
        # 根据复杂度生成步骤
        steps = self._generate_steps(complexity, task_description)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            task_title=task_title,
            complexity=complexity,
            steps=steps,
            current_step=0,
            status="pending",
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.workflows[workflow_id] = workflow
        self._save_workflows()
        
        return workflow
    
    def _generate_steps(self, complexity: ComplexityLevel, 
                       task_description: str) -> List[TaskStep]:
        """根据复杂度生成执行步骤"""
        steps = []
        timestamp = datetime.now().isoformat()
        
        # 所有复杂度都有的基础步骤
        steps.append(TaskStep(
            step_id="s1",
            name="意图理解",
            skill="bionic-cognition",
            action="decode_intent",
            status="pending",
            result=None,
            started_at=None,
            completed_at=None,
            error=None
        ))
        
        if complexity.value >= ComplexityLevel.C2.value:
            steps.append(TaskStep(
                step_id="s2",
                name="安全检查",
                skill="bionic-guard",
                action="risk_check",
                status="pending",
                result=None,
                started_at=None,
                completed_at=None,
                error=None
            ))
        
        if complexity.value >= ComplexityLevel.C3.value:
            steps.append(TaskStep(
                step_id="s3",
                name="推理验证",
                skill="bionic-reasoning",
                action="reason",
                status="pending",
                result=None,
                started_at=None,
                completed_at=None,
                error=None
            ))
        
        if complexity.value >= ComplexityLevel.C4.value:
            steps.append(TaskStep(
                step_id="s4",
                name="多路径探索",
                skill="swarm-intelligence",
                action="explore",
                status="pending",
                result=None,
                started_at=None,
                completed_at=None,
                error=None
            ))
        
        # 执行步骤
        steps.append(TaskStep(
            step_id=f"s{len(steps)+1}",
            name="任务执行",
            skill="executor",
            action="execute",
            status="pending",
            result=None,
            started_at=None,
            completed_at=None,
            error=None
        ))
        
        # 复盘步骤
        steps.append(TaskStep(
            step_id=f"s{len(steps)+1}",
            name="复盘反思",
            skill="bionic-orchestrator",
            action="self_talk",
            status="pending",
            result=None,
            started_at=None,
            completed_at=None,
            error=None
        ))
        
        return steps
    
    def execute_step(self, workflow_id: str, 
                    step_executor: Callable[[TaskStep], dict]) -> TaskStep:
        """
        执行工作流步骤
        
        Args:
            workflow_id: 工作流ID
            step_executor: 步骤执行函数
            
        Returns:
            执行后的步骤
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"工作流 {workflow_id} 不存在")
        
        workflow = self.workflows[workflow_id]
        
        if workflow.current_step >= len(workflow.steps):
            raise ValueError("所有步骤已执行完毕")
        
        step = workflow.steps[workflow.current_step]
        step.status = "running"
        step.started_at = datetime.now().isoformat()
        
        try:
            # 执行步骤
            result = step_executor(step)
            step.result = result
            step.status = "completed"
            step.completed_at = datetime.now().isoformat()
            
            # 推进到下一步
            workflow.current_step += 1
            
            # 检查是否完成
            if workflow.current_step >= len(workflow.steps):
                workflow.status = "completed"
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            workflow.status = "failed"
        
        workflow.updated_at = datetime.now().isoformat()
        self._save_workflows()
        
        return step
    
    def get_next_step(self, workflow_id: str) -> Optional[TaskStep]:
        """获取下一个待执行步骤"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        if workflow.current_step >= len(workflow.steps):
            return None
        
        return workflow.steps[workflow.current_step]
    
    def get_workflow_status(self, workflow_id: str) -> dict:
        """获取工作流状态"""
        if workflow_id not in self.workflows:
            return {"error": "工作流不存在"}
        
        wf = self.workflows[workflow_id]
        return {
            "workflow_id": wf.workflow_id,
            "task_title": wf.task_title,
            "complexity": wf.complexity.name,
            "status": wf.status,
            "progress": f"{wf.current_step}/{len(wf.steps)}",
            "current_step": wf.steps[wf.current_step].name if wf.current_step < len(wf.steps) else None
        }


# 单例模式
_task_scheduler_instance: Optional[TaskScheduler] = None


def get_task_scheduler() -> TaskScheduler:
    """获取任务调度器单例"""
    global _task_scheduler_instance
    if _task_scheduler_instance is None:
        _task_scheduler_instance = TaskScheduler()
    return _task_scheduler_instance
