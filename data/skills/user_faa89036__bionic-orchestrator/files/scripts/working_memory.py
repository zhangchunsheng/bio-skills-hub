"""
工作记忆管理 - L1 编排层
实现任务上下文管理、防遗忘机制
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class Decision:
    """决策记录"""
    step: int
    action: str
    reason: str
    alternative: str
    timestamp: str


@dataclass
class WorkingMemoryBuffer:
    """工作记忆缓冲区"""
    session_id: str
    task_title: str
    status: str  # in_progress, completed, aborted
    intent: str
    constraints: List[str]
    decisions: List[Decision]
    artifacts: List[str]
    open_questions: List[str]
    created_at: str
    updated_at: str
    turn_count: int = 0
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['decisions'] = [asdict(d) for d in self.decisions]
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WorkingMemoryBuffer':
        decisions = [Decision(**d) for d in data.get('decisions', [])]
        return cls(
            session_id=data['session_id'],
            task_title=data['task_title'],
            status=data['status'],
            intent=data['intent'],
            constraints=data.get('constraints', []),
            decisions=decisions,
            artifacts=data.get('artifacts', []),
            open_questions=data.get('open_questions', []),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            turn_count=data.get('turn_count', 0)
        )


class WorkingMemory:
    """工作记忆管理器"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".workbuddy" / "dreams" / "bionic-orchestrator"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.buffer_file = self.data_dir / "wm-buffer.json"
        self.archive_dir = self.data_dir / "wm-archive"
        self.archive_dir.mkdir(exist_ok=True)
        
        self.current_buffer: Optional[WorkingMemoryBuffer] = None
        self._load_buffer()
    
    def _load_buffer(self):
        """加载当前工作记忆"""
        if self.buffer_file.exists():
            try:
                with open(self.buffer_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_buffer = WorkingMemoryBuffer.from_dict(data)
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.current_buffer = None
    
    def _save_buffer(self):
        """保存工作记忆"""
        if self.current_buffer:
            with open(self.buffer_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_buffer.to_dict(), f, ensure_ascii=False, indent=2)
    
    def initialize(self, task_title: str, intent: str, 
                   constraints: Optional[List[str]] = None) -> WorkingMemoryBuffer:
        """
        初始化新任务的工作记忆
        
        Args:
            task_title: 任务标题
            intent: 用户意图
            constraints: 约束列表
            
        Returns:
            工作记忆缓冲区
        """
        timestamp = datetime.now().isoformat()
        session_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hash(task_title) & 0xFFFF:04X}"
        
        self.current_buffer = WorkingMemoryBuffer(
            session_id=session_id,
            task_title=task_title,
            status="in_progress",
            intent=intent,
            constraints=constraints or [],
            decisions=[],
            artifacts=[],
            open_questions=[],
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self._save_buffer()
        return self.current_buffer
    
    def update_status(self, status: str):
        """更新任务状态"""
        if self.current_buffer:
            self.current_buffer.status = status
            self.current_buffer.updated_at = datetime.now().isoformat()
            self._save_buffer()
    
    def record_decision(self, action: str, reason: str, 
                       alternative: str = ""):
        """
        记录决策
        
        Args:
            action: 执行的动作
            reason: 决策原因
            alternative: 放弃的选项
        """
        if not self.current_buffer:
            return
        
        decision = Decision(
            step=len(self.current_buffer.decisions) + 1,
            action=action,
            reason=reason,
            alternative=alternative,
            timestamp=datetime.now().isoformat()
        )
        
        self.current_buffer.decisions.append(decision)
        self.current_buffer.updated_at = datetime.now().isoformat()
        self._save_buffer()
    
    def add_artifact(self, artifact_path: str):
        """添加产出物"""
        if self.current_buffer:
            self.current_buffer.artifacts.append(artifact_path)
            self.current_buffer.updated_at = datetime.now().isoformat()
            self._save_buffer()
    
    def add_open_question(self, question: str):
        """添加未解决问题"""
        if self.current_buffer:
            self.current_buffer.open_questions.append(question)
            self.current_buffer.updated_at = datetime.now().isoformat()
            self._save_buffer()
    
    def increment_turn(self) -> bool:
        """
        增加轮次计数
        
        Returns:
            是否超过20轮（需要防遗忘提示）
        """
        if not self.current_buffer:
            return False
        
        self.current_buffer.turn_count += 1
        self._save_buffer()
        
        return self.current_buffer.turn_count >= 20
    
    def get_forgetfulness_reminder(self) -> Optional[str]:
        """获取防遗忘提醒"""
        if not self.current_buffer:
            return None
        
        if self.current_buffer.turn_count < 20:
            return None
        
        top_constraints = self.current_buffer.constraints[:2]
        constraints_str = " | ".join(top_constraints) if top_constraints else "无"
        
        return (
            f"[WM] 当前任务: {self.current_buffer.task_title} | "
            f"状态: {self.current_buffer.status} | "
            f"关键约束: {constraints_str}"
        )
    
    def archive(self):
        """归档当前任务"""
        if not self.current_buffer:
            return
        
        self.current_buffer.status = "completed"
        self.current_buffer.updated_at = datetime.now().isoformat()
        
        # 保存到归档
        archive_file = self.archive_dir / f"{self.current_buffer.session_id}.json"
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_buffer.to_dict(), f, ensure_ascii=False, indent=2)
        
        # 清空当前缓冲区
        self.current_buffer = None
        if self.buffer_file.exists():
            self.buffer_file.unlink()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取工作记忆摘要"""
        if not self.current_buffer:
            return {"status": "no_active_task"}
        
        return {
            "session_id": self.current_buffer.session_id,
            "task_title": self.current_buffer.task_title,
            "status": self.current_buffer.status,
            "intent": self.current_buffer.intent,
            "decisions_count": len(self.current_buffer.decisions),
            "artifacts_count": len(self.current_buffer.artifacts),
            "turn_count": self.current_buffer.turn_count
        }


# 单例模式
_working_memory_instance: Optional[WorkingMemory] = None


def get_working_memory() -> WorkingMemory:
    """获取工作记忆单例"""
    global _working_memory_instance
    if _working_memory_instance is None:
        _working_memory_instance = WorkingMemory()
    return _working_memory_instance
