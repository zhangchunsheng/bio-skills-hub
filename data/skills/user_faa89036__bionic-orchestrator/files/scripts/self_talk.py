"""
内心独白 - L3 编排层
实现自我反思、复盘、场景预演
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Monologue:
    """独白记录"""
    monologue_id: str
    task_id: str
    monologue_type: str  # pre_execution, during_execution, post_execution
    questions: Dict[str, str]  # 问题 -> 回答
    insights: List[str]
    timestamp: str


class SelfTalk:
    """内心独白系统"""
    
    # 标准独白问题
    STANDARD_QUESTIONS = [
        "任务是什么？最核心要解决的是什么？",
        "我对这个问题的置信度是多少？",
        "有哪些可能的路径？各有什么风险？",
        "我遗漏了什么信息？",
        "如果我错了，最可能错在哪里？",
        "最简洁的方案是什么？",
        "用户会如何评估这个结果？"
    ]
    
    # 复盘问题
    REVIEW_QUESTIONS = [
        "刚才的输出有什么可以改进？",
        "发现了什么通用规律？",
        "下次可以做得更好的地方？",
        "有什么应该记录到长期记忆？"
    ]
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".workbuddy" / "dreams" / "bionic-orchestrator"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.data_dir / "self-talk-log.json"
        self.monologues: List[Monologue] = []
        self._load_data()
    
    def _load_data(self):
        """加载独白历史"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for m_data in data.get("monologues", []):
                        m = Monologue(**m_data)
                        self.monologues.append(m)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    
    def _save_data(self):
        """保存独白记录"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump({
                "monologues": [asdict(m) for m in self.monologues],
                "updated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def pre_execution(self, task_id: str, task_description: str) -> Monologue:
        """
        执行前独白
        
        Args:
            task_id: 任务ID
            task_description: 任务描述
            
        Returns:
            独白记录
        """
        questions = {}
        insights = []
        
        # 回答标准问题
        questions[self.STANDARD_QUESTIONS[0]] = f"核心任务是: {task_description[:50]}..."
        questions[self.STANDARD_QUESTIONS[1]] = "置信度: 70%（需要更多信息）"
        questions[self.STANDARD_QUESTIONS[2]] = "可能路径: 1)直接执行 2)先分析再执行 3)多方案对比"
        questions[self.STANDARD_QUESTIONS[3]] = "可能遗漏: 用户的隐含需求、边界约束"
        questions[self.STANDARD_QUESTIONS[4]] = "可能错误: 误解用户意图、忽略边界情况"
        questions[self.STANDARD_QUESTIONS[5]] = "最简洁方案: 先理解意图，再执行，最后验证"
        questions[self.STANDARD_QUESTIONS[6]] = "用户评估: 结果是否符合预期、是否超出期望"
        
        insights.append("执行前已进行充分思考")
        
        monologue = Monologue(
            monologue_id=f"m_{len(self.monologues)}_{task_id}",
            task_id=task_id,
            monologue_type="pre_execution",
            questions=questions,
            insights=insights,
            timestamp=datetime.now().isoformat()
        )
        
        self.monologues.append(monologue)
        self._save_data()
        
        return monologue
    
    def during_execution(self, task_id: str, current_step: str,
                        context: dict) -> Monologue:
        """
        执行中独白（决策分支时）
        
        Args:
            task_id: 任务ID
            current_step: 当前步骤
            context: 上下文信息
            
        Returns:
            独白记录
        """
        questions = {}
        insights = []
        
        questions["当前步骤是什么？"] = current_step
        questions["有哪些选择？"] = "1)继续当前路径 2)调整策略 3)回退重来"
        questions["每个选择的风险？"] = "继续:可能陷入死胡同;调整:需要额外时间;回退:已做工作浪费"
        questions["推荐的选择？"] = "基于当前信息，建议微调策略继续"
        
        insights.append(f"在步骤 '{current_step}' 进行了决策权衡")
        
        monologue = Monologue(
            monologue_id=f"m_{len(self.monologues)}_{task_id}",
            task_id=task_id,
            monologue_type="during_execution",
            questions=questions,
            insights=insights,
            timestamp=datetime.now().isoformat()
        )
        
        self.monologues.append(monologue)
        self._save_data()
        
        return monologue
    
    def post_execution(self, task_id: str, task_result: dict) -> Monologue:
        """
        执行后复盘独白
        
        Args:
            task_id: 任务ID
            task_result: 任务结果
            
        Returns:
            独白记录
        """
        questions = {}
        insights = []
        
        # 复盘问题
        questions[self.REVIEW_QUESTIONS[0]] = "可以改进: 更充分的预分析、更好的错误处理"
        questions[self.REVIEW_QUESTIONS[1]] = "通用规律: 复杂任务需要先分解再执行"
        questions[self.REVIEW_QUESTIONS[2]] = "下次更好: 提前识别风险、准备备选方案"
        
        # 判断是否有高价值发现
        high_value = task_result.get("success", False) and task_result.get("novelty", 0) > 0.7
        
        if high_value:
            questions[self.REVIEW_QUESTIONS[3]] = "高价值发现: 新的解决模式值得记录"
            insights.append("[高价值] 此任务的解决模式值得固化到长期记忆")
        else:
            questions[self.REVIEW_QUESTIONS[3]] = "常规执行，无需特别记录"
        
        insights.append("任务已完成复盘")
        
        monologue = Monologue(
            monologue_id=f"m_{len(self.monologues)}_{task_id}",
            task_id=task_id,
            monologue_type="post_execution",
            questions=questions,
            insights=insights,
            timestamp=datetime.now().isoformat()
        )
        
        self.monologues.append(monologue)
        self._save_data()
        
        return monologue
    
    def get_insights_for_task(self, task_id: str) -> List[str]:
        """获取任务的所有洞察"""
        insights = []
        for m in self.monologues:
            if m.task_id == task_id:
                insights.extend(m.insights)
        return insights
    
    def has_high_value_finding(self, task_id: str) -> bool:
        """检查任务是否有高价值发现"""
        for m in self.monologues:
            if m.task_id == task_id:
                for insight in m.insights:
                    if "[高价值]" in insight:
                        return True
        return False


# 单例模式
_self_talk_instance: Optional[SelfTalk] = None


def get_self_talk() -> SelfTalk:
    """获取内心独白单例"""
    global _self_talk_instance
    if _self_talk_instance is None:
        _self_talk_instance = SelfTalk()
    return _self_talk_instance
