"""
科学方法论 - L1 推理层
实现假设构建、贝叶斯更新、可证伪性检验、偏误防御
"""

import json
import math
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime


@dataclass
class Hypothesis:
    """假设对象"""
    id: str
    level: int  # 0=零假设, 1=第一假设, 2=第二假设, 3=第三假设
    statement: str
    complexity: float  # 复杂度 = 参数数量 × 依赖假设数 / 解释力
    prior_probability: float  # 先验概率
    posterior_probability: float  # 后验概率
    evidence_count: int
    falsifiable: bool
    created_at: str
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Hypothesis':
        return cls(**data)


@dataclass
class Evidence:
    """证据对象"""
    id: str
    hypothesis_id: str
    description: str
    likelihood: float  # P(E|H)
    timestamp: str
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BiasCheck:
    """偏误检查结果"""
    bias_type: str
    detected: bool
    severity: str  # low, medium, high
    suggestion: str


class ScientificMethod:
    """科学方法论实现"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".workbuddy" / "dreams" / "bionic-reasoning"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.hypothesis_log_file = self.data_dir / "hypothesis-log.json"
        self.confidence_file = self.data_dir / "confidence-updates.json"
        
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.evidence: Dict[str, List[Evidence]] = {}
        self._load_data()
    
    def _load_data(self):
        """加载历史数据"""
        if self.hypothesis_log_file.exists():
            try:
                with open(self.hypothesis_log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for h_data in data.get("hypotheses", []):
                        h = Hypothesis.from_dict(h_data)
                        self.hypotheses[h.id] = h
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        if self.confidence_file.exists():
            try:
                with open(self.confidence_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.evidence = {
                        k: [Evidence(**e) for e in v]
                        for k, v in data.get("evidence", {}).items()
                    }
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.evidence = {}
    
    def _save_data(self):
        """保存数据"""
        with open(self.hypothesis_log_file, 'w', encoding='utf-8') as f:
            json.dump({
                "hypotheses": [h.to_dict() for h in self.hypotheses.values()],
                "updated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        with open(self.confidence_file, 'w', encoding='utf-8') as f:
            json.dump({
                "evidence": {
                    k: [e.to_dict() for e in v]
                    for k, v in self.evidence.items()
                },
                "updated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def build_hypotheses(self, observation: str) -> List[Hypothesis]:
        """
        基于观察构建假设层级
        
        Args:
            observation: 观察到的现象
            
        Returns:
            假设列表（H0, H1, H2, H3）
        """
        hypotheses = []
        timestamp = datetime.now().isoformat()
        
        # H0: 零假设（什么都不发生）
        h0 = Hypothesis(
            id=f"h0_{hash(observation) & 0xFFFFFFFF}",
            level=0,
            statement=f"观察到的现象 '{observation}' 是随机波动或测量误差",
            complexity=1.0,
            prior_probability=0.1,
            posterior_probability=0.1,
            evidence_count=0,
            falsifiable=True,
            created_at=timestamp
        )
        hypotheses.append(h0)
        self.hypotheses[h0.id] = h0
        
        # H1: 第一假设（最简单解释 - 奥卡姆剃刀）
        h1 = Hypothesis(
            id=f"h1_{hash(observation) & 0xFFFFFFFF}",
            level=1,
            statement=f"'{observation}' 有最直接、最简单的单一原因解释",
            complexity=2.0,
            prior_probability=0.5,
            posterior_probability=0.5,
            evidence_count=0,
            falsifiable=True,
            created_at=timestamp
        )
        hypotheses.append(h1)
        self.hypotheses[h1.id] = h1
        
        # H2: 第二假设（次要因素加入）
        h2 = Hypothesis(
            id=f"h2_{hash(observation) & 0xFFFFFFFF}",
            level=2,
            statement=f"'{observation}' 由多个因素共同作用导致",
            complexity=4.0,
            prior_probability=0.3,
            posterior_probability=0.3,
            evidence_count=0,
            falsifiable=True,
            created_at=timestamp
        )
        hypotheses.append(h2)
        self.hypotheses[h2.id] = h2
        
        # H3: 第三假设（复杂性增加）
        h3 = Hypothesis(
            id=f"h3_{hash(observation) & 0xFFFFFFFF}",
            level=3,
            statement=f"'{observation}' 涉及复杂系统交互和涌现效应",
            complexity=8.0,
            prior_probability=0.1,
            posterior_probability=0.1,
            evidence_count=0,
            falsifiable=True,
            created_at=timestamp
        )
        hypotheses.append(h3)
        self.hypotheses[h3.id] = h3
        
        self._save_data()
        return hypotheses
    
    def bayesian_update(self, hypothesis_id: str, evidence: str, 
                       likelihood: float) -> Tuple[float, float]:
        """
        贝叶斯置信更新
        P(H|E) = P(E|H) × P(H) / P(E)
        
        Args:
            hypothesis_id: 假设ID
            evidence: 证据描述
            likelihood: P(E|H) 似然
            
        Returns:
            (更新前概率, 更新后概率)
        """
        if hypothesis_id not in self.hypotheses:
            raise ValueError(f"假设 {hypothesis_id} 不存在")
        
        hypothesis = self.hypotheses[hypothesis_id]
        prior = hypothesis.posterior_probability
        
        # 简化的贝叶斯更新
        # P(H|E) ∝ P(E|H) × P(H)
        posterior = (likelihood * prior) / ((likelihood * prior) + (1 - likelihood) * (1 - prior))
        
        # 边界处理
        posterior = max(0.01, min(0.99, posterior))
        
        # 更新假设
        old_prob = hypothesis.posterior_probability
        hypothesis.posterior_probability = posterior
        hypothesis.prior_probability = prior
        hypothesis.evidence_count += 1
        
        # 记录证据
        ev = Evidence(
            id=f"e_{len(self.evidence.get(hypothesis_id, []))}",
            hypothesis_id=hypothesis_id,
            description=evidence,
            likelihood=likelihood,
            timestamp=datetime.now().isoformat()
        )
        if hypothesis_id not in self.evidence:
            self.evidence[hypothesis_id] = []
        self.evidence[hypothesis_id].append(ev)
        
        self._save_data()
        return old_prob, posterior
    
    def check_falsifiability(self, statement: str) -> Tuple[bool, str]:
        """
        检查结论是否可证伪
        
        Args:
            statement: 待检查的陈述
            
        Returns:
            (是否可证伪, 说明)
        """
        # 不可证伪的关键词
        unfalsifiable_patterns = [
            "有时候", "可能", "也许", "我相信", "我觉得",
            "总体上", "一般来说", "通常", "大概"
        ]
        
        # 可证伪的模式
        falsifiable_patterns = [
            "如果...则", "导致", "平均", "概率", "%",
            "增加", "减少", "等于", "大于", "小于"
        ]
        
        has_unfalsifiable = any(p in statement for p in unfalsifiable_patterns)
        has_falsifiable = any(p in statement for p in falsifiable_patterns)
        
        if has_unfalsifiable and not has_falsifiable:
            return False, f"陈述包含模糊词汇，难以证伪: {statement}"
        
        if has_falsifiable:
            return True, "陈述包含可观测、可测量的断言"
        
        # 如果包含不可证伪词汇但没有可证伪词汇，返回不可证伪
        if has_unfalsifiable:
            return False, f"陈述包含模糊词汇，难以证伪: {statement}"
        
        return True, "陈述可以被检验（默认假设可证伪）"
    
    def check_bias(self, reasoning: str) -> List[BiasCheck]:
        """
        检查推理中的认知偏误
        
        Args:
            reasoning: 推理文本
            
        Returns:
            偏误检查结果列表
        """
        results = []
        
        # 确认偏误检查
        confirm_patterns = ["证明", "证实", "支持", "正确"]
        disconfirm_patterns = ["反驳", "质疑", "反对", "错误"]
        confirm_count = sum(1 for p in confirm_patterns if p in reasoning)
        disconfirm_count = sum(1 for p in disconfirm_patterns if p in reasoning)
        
        if confirm_count > 0 and disconfirm_count == 0:
            results.append(BiasCheck(
                bias_type="确认偏误",
                detected=True,
                severity="medium",
                suggestion="同时考虑反驳证据，搜索'为什么这可能是错的'"
            ))
        
        # 幸存者偏误检查
        survivor_patterns = ["成功案例", "赢家", "顶尖", "最优秀"]
        if any(p in reasoning for p in survivor_patterns):
            results.append(BiasCheck(
                bias_type="幸存者偏误",
                detected=True,
                severity="high",
                suggestion="列出失败案例进行对比，计算基础概率"
            ))
        
        # 相关≠因果检查
        causal_patterns = ["导致", "因为", "所以", "引起"]
        if any(p in reasoning for p in causal_patterns):
            results.append(BiasCheck(
                bias_type="因果推断",
                detected=True,
                severity="low",
                suggestion="检查混杂变量、时序关系、反向因果可能性"
            ))
        
        if not results:
            results.append(BiasCheck(
                bias_type="无",
                detected=False,
                severity="low",
                suggestion="未发现明显偏误"
            ))
        
        return results
    
    def get_best_hypothesis(self, observation: str) -> Optional[Hypothesis]:
        """获取最佳假设（后验概率最高且复杂度最低）"""
        if not self.hypotheses:
            return None
        
        # 按后验概率排序
        sorted_h = sorted(
            self.hypotheses.values(),
            key=lambda h: (h.posterior_probability, -h.complexity),
            reverse=True
        )
        return sorted_h[0] if sorted_h else None


# 单例模式
_scientific_method_instance: Optional[ScientificMethod] = None


def get_scientific_method() -> ScientificMethod:
    """获取科学方法论单例"""
    global _scientific_method_instance
    if _scientific_method_instance is None:
        _scientific_method_instance = ScientificMethod()
    return _scientific_method_instance
