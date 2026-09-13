#!/usr/bin/env python3
"""
Bionic Brain Executor - 真正可执行的全脑系统
自动注入到任务执行流程
"""

import re
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict

# ========== 数据模型 ==========

@dataclass
class TaskContext:
    """任务上下文"""
    query: str
    command: Optional[str] = None
    complexity: str = "C1"
    risk_level: str = "P2"
    risk_desc: Optional[str] = None
    confidence: float = 1.0
    blocked: bool = False
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    output: Any = None
    errors: List[str] = None
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.metrics is None:
            self.metrics = {}

# ========== 核心检测器 ==========

class ACCMonitor:
    """ACC错误监测器"""
    OVERCONFIDENCE_PATTERNS = [
        r"绝对.*没问题", r"100%.*保证", r"肯定.*正确",
        r"绝对.*可靠", r"绝对.*安全", r"绝对不会.*错"
    ]
    LOGIC_CONTRADICTIONS = ["但是", "然而", "不过", "然而", "可是"]
    
    def check_text(self, text: str) -> Tuple[float, List[str]]:
        confidence = 1.0
        flags = []
        
        for p in self.OVERCONFIDENCE_PATTERNS:
            if re.search(p, text):
                flags.append(f"过度自信: {p}")
                confidence *= 0.8
        
        for c in self.LOGIC_CONTRADICTIONS:
            if text.count(c) > 1:
                flags.append(f"逻辑矛盾风险: 多次出现'{c}'")
                confidence *= 0.9
        
        return confidence, flags
    
    def check_memory_conflict(self, current: str, memory_path: Path) -> bool:
        """检查与记忆的冲突"""
        if not memory_path.exists():
            return False
        
        try:
            with open(memory_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单关键词冲突检测
                for line in content.split('\n'):
                    if ':' in line and len(line) < 100:
                        key = line.split(':')[0].strip()
                        if key in current:
                            return True
        except:
            pass
        return False


class AmygdalaGuard:
    """杏仁核风险守卫"""
    P0_PATTERNS = [
        (r"rm\s+-rf", "递归删除文件"),
        (r"del\s+/[sS]", "Windows递归删除"),
        (r"shutil\.rmtree", "Python递归删除"),
        (r"format\s+[a-zA-Z]:", "磁盘格式化"),
        (r"DROP\s+TABLE", "删除数据库表"),
        (r"DROP\s+DATABASE", "删除数据库"),
        (r"os\.remove.*\*", "通配符删除"),
        (r"Remove-Item.*-Recurse", "PowerShell递归删除"),
    ]
    
    P1_PATTERNS = [
        (r"open\(.*['\"]w['\"]", "覆写文件"),
        (r"move|rename.*\[\d{2,}", "批量重命名"),
        (r"requests\.post", "外部HTTP请求"),
        (r"subprocess.*install", "安装软件"),
        (r"pip\s+install", "pip安装"),
        (r"npm\s+install.*-g", "全局npm安装"),
    ]
    
    PROTECTED_PATHS = [
        "C:\\Windows", "C:\\System32",
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\Downloads"),
    ]
    
    def scan_command(self, cmd: str) -> Tuple[str, str, List[str]]:
        level = "P2"
        desc = "无风险"
        warnings = []
        
        # P0 检测
        for pattern, d in self.P0_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                level = "P0"
                desc = d
                warnings.append(f"⛔ P0风险: {d}")
        
        # P1 检测
        if level == "P2":
            for pattern, d in self.P1_PATTERNS:
                if re.search(pattern, cmd, re.IGNORECASE):
                    level = "P1"
                    desc = d
                    warnings.append(f"⚠️ P1风险: {d}")
        
        # 保护路径检测
        for path in self.PROTECTED_PATHS:
            if path in cmd:
                level = "P0"
                desc = f"保护路径: {path}"
                warnings.append(f"⛔ 触及保护路径: {path}")
        
        return level, desc, warnings


class ComplexityClassifier:
    """复杂度分类器"""
    C1_KEYWORDS = ["你好", "hi", "hello", "天气", "问候", "在吗"]
    C2_KEYWORDS = ["写", "读", "查", "生成", "create", "read", "搜索", "找一下"]
    C3_KEYWORDS = ["分析", "推理", "代码", "debug", "analyze", "比较", "优化", "修复"]
    C4_KEYWORDS = ["架构", "设计", "决策", "architecture", "strategy", "规划", "方案"]
    
    def classify(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in self.C4_KEYWORDS):
            return "C4"
        if any(k in q for k in self.C3_KEYWORDS):
            return "C3"
        if any(k in q for k in self.C2_KEYWORDS):
            return "C2"
        return "C1"


class ImmuneSystem:
    """免疫系统 - 异常模式识别"""
    def __init__(self, data_dir: Path):
        self.threat_file = data_dir / "threat-memory.json"
        self.anomaly_count = 0
        self._load_threats()
    
    def _load_threats(self):
        if self.threat_file.exists():
            try:
                with open(self.threat_file, 'r') as f:
                    data = json.load(f)
                    self.anomaly_count = data.get("total_anomalies", 0)
            except:
                self.anomaly_count = 0
    
    def record_anomaly(self, pattern: str, severity: str = "low"):
        self.anomaly_count += 1
        try:
            data = {"total_anomalies": self.anomaly_count, "last_update": datetime.now().isoformat()}
            with open(self.threat_file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def check_pattern(self, query: str) -> Tuple[bool, Optional[str]]:
        """检测异常模式"""
        # 简单检测：连续大写、异常字符等
        if sum(1 for c in query if c.isupper()) > len(query) * 0.5:
            return True, "异常大写模式"
        if re.search(r"[^\w\s\u4e00-\u9fff]", query) and len(query) > 50:
            return True, "异常字符模式"
        return False, None


class HabitTracker:
    """习惯追踪器"""
    def __init__(self, data_dir: Path):
        self.habit_file = data_dir / "habit-store.json"
        self.frequency_file = data_dir / "task-frequency-tracker.json"
        self.habits = self._load()
    
    def _load(self) -> Dict:
        if self.habit_file.exists():
            try:
                with open(self.habit_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"habits": [], "frequency": {}}
    
    def check_habit(self, query: str) -> Optional[Dict]:
        """检查是否有匹配的习惯"""
        query_lower = query.lower()
        for h in self.habits.get("habits", []):
            for trigger in h.get("triggers", []):
                if trigger.lower() in query_lower:
                    return h
        return None
    
    def record_task(self, query: str):
        """记录任务频率"""
        freq = self.habits.get("frequency", {})
        
        # 简化提取关键词
        key = query[:20].lower()
        freq[key] = freq.get(key, 0) + 1
        
        self.habits["frequency"] = freq
        
        # 检查是否达到习惯阈值
        if freq[key] >= 3:
            self._create_habit(key, query)
        
        self._save()
    
    def _create_habit(self, key: str, full_query: str):
        """创建习惯"""
        habits = self.habits.get("habits", [])
        for h in habits:
            if key in h.get("name", ""):
                return  # 已存在
        
        habits.append({
            "name": key,
            "trigger": key,
            "trigger_count": freq[key],
            "action": full_query,
            "created": datetime.now().isoformat()
        })
        self.habits["habits"] = habits
    
    def _save(self):
        try:
            with open(self.habit_file, 'w', encoding='utf-8') as f:
                json.dump(self.habits, f, ensure_ascii=False, indent=2)
        except:
            pass


# ========== Bionic Brain Executor ==========

class BionicBrainExecutor:
    """仿生全脑执行器"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".workbuddy" / "dreams"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化各模块
        self.acc = ACCMonitor()
        self.amygdala = AmygdalaGuard()
        self.classifier = ComplexityClassifier()
        self.immune = ImmuneSystem(data_dir)
        self.habit = HabitTracker(data_dir)
        
        # 记忆文件
        self.memory_file = Path.home() / ".workbuddy" / "MEMORY.md"
        
        # 执行日志
        self.log_file = data_dir / "bionic-brain-executions.json"
    
    def preflight(self, query: str, command: Optional[str] = None) -> TaskContext:
        """执行前检查"""
        ctx = TaskContext(query=query, command=command)
        
        # 1. 复杂度分类
        ctx.complexity = self.classifier.classify(query)
        
        # 2. 风险扫描
        if command:
            level, desc, warnings = self.amygdala.scan_command(command)
            ctx.risk_level = level
            ctx.risk_desc = desc
            ctx.warnings = warnings
            ctx.blocked = (level == "P0")
        
        # 3. 置信度检查
        ctx.confidence, conf_flags = self.acc.check_text(query)
        
        # 4. 记忆冲突检查
        if self.acc.check_memory_conflict(query, self.memory_file):
            ctx.warnings.append("⚠️ 与记忆存在潜在冲突")
        
        # 5. 异常模式检查
        is_anomaly, anomaly_desc = self.immune.check_pattern(query)
        if is_anomaly:
            ctx.warnings.append(f"🔍 异常模式: {anomaly_desc}")
            self.immune.record_anomaly(anomaly_desc)
        
        # 6. 习惯检查
        habit = self.habit.check_habit(query)
        if habit:
            ctx.warnings.append(f"🔄 习惯触发: {habit.get('name')}")
        
        return ctx
    
    def postflight(self, query: str, result: ExecutionResult):
        """执行后记录"""
        # 1. 记录任务频率
        self.habit.record_task(query)
        
        # 2. 记录执行日志
        self._log_execution(query, result)
    
    def _log_execution(self, query: str, result: ExecutionResult):
        """记录执行"""
        try:
            logs = []
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            logs.append({
                "ts": datetime.now().isoformat(),
                "query": query[:50],
                "success": result.success,
                "errors": result.errors
            })
            logs = logs[-1000:]  # 保留最近1000条
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_risk_alert(self, ctx: TaskContext) -> Optional[str]:
        """生成风险警报"""
        if ctx.risk_level == "P0":
            return f"""⛔ P0风险操作检测到！

操作：{ctx.risk_desc}
触发命令：{ctx.command[:100] if ctx.command else 'N/A'}...

⚠️ 此操作非常危险，可能导致不可逆的数据丢失！

请明确回复「确认执行」才会继续。"""
        
        if ctx.risk_level == "P1":
            return f"""⚠️ P1风险操作

操作：{ctx.risk_desc}
影响：{ctx.command[:100] if ctx.command else 'N/A'}...

建议：先备份再执行
[继续执行] 还是 [先备份]？（默认：先备份）"""
        
        return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "habits_count": len(self.habit.habits.get("habits", [])),
            "anomalies_count": self.immune.anomaly_count,
            "log_entries": 0,
            "data_dir": str(self.data_dir)
        }


# ========== 全局实例 ==========

_executor = None

def get_executor() -> BionicBrainExecutor:
    global _executor
    if _executor is None:
        _executor = BionicBrainExecutor()
    return _executor

def run_preflight(query: str, command: Optional[str] = None) -> TaskContext:
    """快捷预检"""
    return get_executor().preflight(query, command)


if __name__ == "__main__":
    executor = get_executor()
    
    print("=" * 50)
    print("Bionic Brain Executor - 系统测试")
    print("=" * 50)
    
    # 测试用例
    tests = [
        ("你好", None),
        ("帮我写一个PPT", None),
        ("删除所有桌面文件", "rm -rf ~/Desktop/*"),
        ("分析这段代码", None),
        ("架构设计文档", None),
    ]
    
    for query, cmd in tests:
        print(f"\n📋 任务: {query}")
        if cmd:
            print(f"   命令: {cmd}")
        
        ctx = executor.preflight(query, cmd)
        
        print(f"   复杂度: {ctx.complexity}")
        print(f"   风险: {ctx.risk_level} - {ctx.risk_desc}")
        print(f"   置信度: {ctx.confidence:.2f}")
        
        if ctx.warnings:
            for w in ctx.warnings:
                print(f"   {w}")
        
        if ctx.blocked:
            print(f"   🚫 已拦截!")
    
    print("\n" + "=" * 50)
    print("系统状态:", executor.get_system_status())
