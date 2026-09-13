#!/usr/bin/env python3
"""
Amygdala Risk Sniffer
杏仁核风险嗅探器 - 预判潜在风险

职责：
- 基于模式识别预判风险
- 评估风险等级
- 触发预警机制
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class RiskLevel(Enum):
    """风险等级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class RiskEvent:
    """风险事件"""
    timestamp: str
    risk_level: str
    category: str
    pattern: str
    context: str
    recommendation: str
    triggered: bool = False
    
    def to_dict(self):
        return asdict(self)

class RiskSniffer:
    """杏仁核风险嗅探器"""
    
    # 风险模式库
    RISK_PATTERNS = {
        "destructive": {
            "patterns": [
                r"rm\s+-rf",
                r"del\s+/[sfq]",
                r"format\s+",
                r"drop\s+database",
                r"truncate\s+table",
                r"DELETE\s+FROM\s+\w+\s+WHERE\s+1\s*=\s*1",
            ],
            "level": RiskLevel.CRITICAL,
            "category": "destructive_operation"
        },
        "security": {
            "patterns": [
                r"password\s*=\s*['\"]\w+",
                r"api[_-]?key\s*=\s*['\"]\w+",
                r"token\s*=\s*['\"]\w+",
                r"secret\s*=\s*['\"]\w+",
                r"BEGIN\s+(RSA\s+)?PRIVATE\s+KEY",
            ],
            "level": RiskLevel.HIGH,
            "category": "credential_exposure"
        },
        "performance": {
            "patterns": [
                r"for\s+\w+\s+in\s+range\([^)]+\):\s*\n\s+for\s+\w+",  # 嵌套循环
                r"SELECT\s+\*\s+FROM",
                r"while\s*\(\s*true\s*\)",
            ],
            "level": RiskLevel.MEDIUM,
            "category": "performance_issue"
        },
        "external": {
            "patterns": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"subprocess\.call\s*\(",
                r"os\.system\s*\(",
            ],
            "level": RiskLevel.HIGH,
            "category": "external_execution"
        }
    }
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".workbuddy" / "dreams" / "bionic-guard"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "risk-events.json"
        self.whitelist_file = self.data_dir / "whitelist.json"
        
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    self.events = data.get("events", [])
                    self.risk_levels = data.get("risk_levels", {"low": 0, "medium": 0, "high": 0, "critical": 0})
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.events = []
                self.risk_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        else:
            self.events = []
            self.risk_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        if self.whitelist_file.exists():
            try:
                with open(self.whitelist_file, 'r', encoding='utf-8-sig') as f:
                    self.whitelist = set(json.load(f).get("patterns", []))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.whitelist = set()
        else:
            self.whitelist = set()
    
    def _save_data(self):
        """保存数据"""
        log_data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "risk_levels": self.risk_levels,
            "events": self.events[-500:]  # 保留最近500条
        }
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def sniff(self, content: str, context: str = "") -> List[RiskEvent]:
        """
        嗅探风险
        
        Args:
            content: 要检查的内容
            context: 上下文描述
        
        Returns:
            发现的风险事件列表
        """
        detected = []
        
        for risk_type, config in self.RISK_PATTERNS.items():
            for pattern in config["patterns"]:
                if pattern in self.whitelist:
                    continue
                    
                if re.search(pattern, content, re.IGNORECASE):
                    event = RiskEvent(
                        timestamp=datetime.now().isoformat(),
                        risk_level=config["level"].name.lower(),
                        category=config["category"],
                        pattern=pattern,
                        context=context[:200],
                        recommendation=self._get_recommendation(config["category"]),
                        triggered=True
                    )
                    detected.append(event)
                    self._record_event(event)
        
        return detected
    
    def _record_event(self, event: RiskEvent):
        """记录事件"""
        self.events.append(event.to_dict())
        self.risk_levels[event.risk_level] = self.risk_levels.get(event.risk_level, 0) + 1
        self._save_data()
    
    def _get_recommendation(self, category: str) -> str:
        """获取建议"""
        recommendations = {
            "destructive_operation": "⚠️ 检测到破坏性操作，请确认目标路径和数据备份",
            "credential_exposure": "🔒 检测到敏感信息，请使用环境变量或密钥管理服务",
            "performance_issue": "⚡ 检测到潜在性能问题，建议使用索引或优化算法",
            "external_execution": "🔐 检测到外部命令执行，请验证输入并限制执行范围"
        }
        return recommendations.get(category, "请人工复核")
    
    def add_to_whitelist(self, pattern: str):
        """添加白名单"""
        self.whitelist.add(pattern)
        with open(self.whitelist_file, 'w', encoding='utf-8') as f:
            json.dump({"patterns": list(self.whitelist)}, f, indent=2)
    
    def get_risk_summary(self) -> Dict:
        """获取风险摘要"""
        return {
            "total_events": len(self.events),
            "by_level": self.risk_levels,
            "recent_events": self.events[-5:],
            "whitelist_count": len(self.whitelist)
        }


# 单例
_sniffer = None

def get_risk_sniffer() -> RiskSniffer:
    global _sniffer
    if _sniffer is None:
        _sniffer = RiskSniffer()
    return _sniffer


if __name__ == "__main__":
    sniffer = get_risk_sniffer()
    
    # 测试
    test_code = """
    import os
    os.system("rm -rf /important/data")
    password = "secret123"
    """
    
    risks = sniffer.sniff(test_code, "测试代码检查")
    for risk in risks:
        print(f"[{risk.risk_level.upper()}] {risk.category}: {risk.recommendation}")
    
    print("\n风险摘要:", json.dumps(sniffer.get_risk_summary(), indent=2))
