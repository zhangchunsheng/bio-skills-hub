#!/usr/bin/env python3
"""
ACC (Anterior Cingulate Cortex) Conflict Monitor
前额叶皮层前扣带 - 实时冲突与错误检测

职责：
- 监测操作中的冲突信号
- 检测执行错误
- 触发错误相关负波 (ERN)
"""

import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class ConflictType(Enum):
    """冲突类型"""
    SYNTAX_ERROR = "syntax_error"          # 语法错误
    LOGIC_CONFLICT = "logic_conflict"      # 逻辑冲突
    RESOURCE_RACE = "resource_race"        # 资源竞争
    STATE_MISMATCH = "state_mismatch"      # 状态不匹配
    PERMISSION_DENIED = "permission_denied" # 权限拒绝
    TIMEOUT = "timeout"                     # 超时
    UNEXPECTED_RESULT = "unexpected_result" # 意外结果

@dataclass
class ConflictEvent:
    """冲突事件"""
    timestamp: str
    conflict_type: str
    severity: int  # 1-5, 5最严重
    context: str
    operation: str
    expected: str
    actual: str
    resolution: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

class ACCMonitor:
    """ACC 冲突监测器"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".workbuddy" / "dreams" / "bionic-guard"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "acc-log.json"
        
        # 冲突阈值配置
        self.thresholds = {
            "syntax_error": 1,      # 立即报告
            "logic_conflict": 2,    # 轻微延迟
            "resource_race": 3,     # 中等延迟
            "state_mismatch": 2,
            "permission_denied": 1,
            "timeout": 3,
            "unexpected_result": 2
        }
        
        # 回调函数注册
        self._handlers: List[Callable[[ConflictEvent], None]] = []
        
        # 加载历史
        self._load_log()
    
    def _load_log(self) -> List[Dict]:
        """加载历史日志"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8-sig') as f:
                    return json.load(f).get("entries", [])
            except (json.JSONDecodeError, UnicodeDecodeError):
                return []
        return []
    
    def _save_log(self, entries: List[Dict]):
        """保存日志"""
        data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "total_conflicts": len(entries),
            "entries": entries[-1000:]  # 保留最近1000条
        }
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def register_handler(self, handler: Callable[[ConflictEvent], None]):
        """注册冲突处理器"""
        self._handlers.append(handler)
    
    def detect_conflict(self, 
                       operation: str,
                       expected: str,
                       actual: str,
                       context: str = "",
                       conflict_type: ConflictType = ConflictType.UNEXPECTED_RESULT) -> Optional[ConflictEvent]:
        """
        检测冲突
        
        Args:
            operation: 执行的操作
            expected: 预期结果
            actual: 实际结果
            context: 上下文信息
            conflict_type: 冲突类型
        
        Returns:
            ConflictEvent if conflict detected, None otherwise
        """
        # 比较预期与实际
        if expected == actual:
            return None
        
        # 创建冲突事件
        event = ConflictEvent(
            timestamp=datetime.now().isoformat(),
            conflict_type=conflict_type.value,
            severity=self.thresholds.get(conflict_type.value, 2),
            context=context,
            operation=operation,
            expected=expected,
            actual=actual,
            resolution=None
        )
        
        # 记录日志
        self._record_event(event)
        
        # 触发回调
        for handler in self._handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[ACC] Handler error: {e}")
        
        return event
    
    def _record_event(self, event: ConflictEvent):
        """记录事件到日志"""
        entries = self._load_log()
        entries.append(event.to_dict())
        self._save_log(entries)
    
    def check_syntax(self, code: str, language: str = "python") -> Optional[ConflictEvent]:
        """检查语法错误"""
        import ast
        
        if language == "python":
            try:
                ast.parse(code)
                return None
            except SyntaxError as e:
                return self.detect_conflict(
                    operation=f"parse_{language}",
                    expected="valid syntax",
                    actual=f"SyntaxError: {e.msg} at line {e.lineno}",
                    context=code[:200],
                    conflict_type=ConflictType.SYNTAX_ERROR
                )
        return None
    
    def check_state_consistency(self, 
                                current_state: Dict,
                                expected_state: Dict,
                                operation: str) -> Optional[ConflictEvent]:
        """检查状态一致性"""
        mismatches = []
        for key in set(current_state.keys()) | set(expected_state.keys()):
            if current_state.get(key) != expected_state.get(key):
                mismatches.append(f"{key}: expected={expected_state.get(key)}, actual={current_state.get(key)}")
        
        if mismatches:
            return self.detect_conflict(
                operation=operation,
                expected=str(expected_state),
                actual=str(current_state),
                context="; ".join(mismatches),
                conflict_type=ConflictType.STATE_MISMATCH
            )
        return None
    
    def get_conflict_stats(self) -> Dict:
        """获取冲突统计"""
        entries = self._load_log()
        stats = {
            "total": len(entries),
            "by_type": {},
            "by_severity": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "recent": entries[-10:]
        }
        
        for entry in entries:
            conflict_type = entry.get("conflict_type", "unknown")
            severity = entry.get("severity", 2)
            stats["by_type"][conflict_type] = stats["by_type"].get(conflict_type, 0) + 1
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
        
        return stats
    
    def generate_ern_signal(self, event: ConflictEvent) -> str:
        """
        生成错误相关负波 (Error-Related Negativity) 信号
        用于触发上层响应
        """
        signal_strength = "🔴" * event.severity
        return f"[ERN-{event.severity}] {signal_strength} {event.conflict_type}: {event.operation}"


# 单例实例
_acc_monitor = None

def get_acc_monitor() -> ACCMonitor:
    """获取 ACC 监测器单例"""
    global _acc_monitor
    if _acc_monitor is None:
        _acc_monitor = ACCMonitor()
    return _acc_monitor


if __name__ == "__main__":
    # 测试
    acc = get_acc_monitor()
    
    # 测试语法检查
    bad_code = "def foo():\n    print('missing parenthesis"
    conflict = acc.check_syntax(bad_code)
    if conflict:
        print(acc.generate_ern_signal(conflict))
    
    # 测试状态检查
    conflict2 = acc.check_state_consistency(
        current_state={"status": "error", "code": 500},
        expected_state={"status": "success", "code": 200},
        operation="api_call"
    )
    if conflict2:
        print(acc.generate_ern_signal(conflict2))
    
    # 打印统计
    print("\n冲突统计:", json.dumps(acc.get_conflict_stats(), indent=2))
