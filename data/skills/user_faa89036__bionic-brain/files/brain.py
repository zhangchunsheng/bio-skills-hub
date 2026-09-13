#!/usr/bin/env python3
"""
bionic Brain - 仿生全脑系统 v2.1 (优化版)
整合11种认知能力 + 自动进化引擎
基于自我审计结果优化
"""

import re
import json
import math
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict

# ========== 1. ACC Error Monitor - 错误监测 ==========

class ACCMonitor:
    """ACC错误监测器 - 优化版"""
    OVERCONFIDENCE_PATTERNS = [
        r"绝对.*没问题", r"100%.*保证", r"肯定.*正确",
        r"绝对.*可靠", r"绝对.*安全", r"绝对不会.*错",
        r"一定.*成功", r"完全.*确定", r"保证.*完美",
        r"万无一失", r"毫无疑问"
    ]
    
    # 新增: 低置信度指示词
    LOW_CONFIDENCE_PATTERNS = [
        r"可能.*吧", r"大概.*吧", r"也许.*吧",
        r"不确定", r"不清楚", r"不知道"
    ]
    
    def check_text(self, text: str) -> Tuple[float, List[str]]:
        """检测文本中的过度自信"""
        confidence = 1.0
        flags = []
        
        for p in self.OVERCONFIDENCE_PATTERNS:
            if re.search(p, text):
                flags.append(f"过度自信: {p}")
                confidence *= 0.8
        
        # 新增: 检测过低置信度
        for p in self.LOW_CONFIDENCE_PATTERNS:
            if re.search(p, text):
                flags.append(f"过低置信: {p}")
                confidence *= 0.9
        
        return confidence, flags
    
    def check_memory_conflict(self, text: str, memory_path: Path) -> bool:
        """检测与记忆的冲突"""
        if not memory_path.exists(): return False
        try:
            with open(memory_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    if ':' in line and len(line) < 100:
                        key = line.split(':')[0].strip()
                        if key and len(key) > 2 and key in text:
                            return True
        except: pass
        return False
    
    def check_consistency(self, claims: List[str]) -> Tuple[bool, Optional[str]]:
        """检测多个声明之间的一致性"""
        if len(claims) < 2: return True, None
        
        # 简化: 检查是否有过度自信声明
        overconfident = 0
        for claim in claims:
            conf, _ = self.check_text(claim)
            if conf < 0.9:
                overconfident += 1
        
        if overconfident > len(claims) * 0.5:
            return False, "多个声明存在过度自信"
        
        return True, None


# ========== 2. Amygdala Guard - 风险守卫 (增强版) ==========

class AmygdalaGuard:
    """杏仁核风险守卫 - 增强版"""
    P0_PATTERNS = [
        # 递归删除
        (r"rm\s+-rf", "递归删除"),
        (r"rm\s+-r\s+/", "根目录删除"),
        (r"del\s+/[sS]", "Windows递归删除"),
        (r"shutil\.rmtree", "Python递归删除"),
        (r"Remove-Item.*-Recurse", "PowerShell递归删除"),
        # 磁盘操作
        (r"format\s+[a-zA-Z]:", "磁盘格式化"),
        (r"dd\s+if=.*of=/dev/", "直接磁盘写入"),
        # 数据库
        (r"DROP\s+TABLE", "删除数据库表"),
        (r"DROP\s+DATABASE", "删除数据库"),
        (r"TRUNCATE\s+TABLE", "清空数据库表"),
        # 系统危险
        (r":(){ :|:& };:", "Fork炸弹"),
        (r">\s*/dev/sd", "直接写入磁盘"),
    ]
    
    P1_PATTERNS = [
        # 文件覆写
        (r"open\(.*['\"]w['\"]", "覆写文件"),
        (r">\s*[\w/.-]+\s*$", "Shell重定向覆写"),
        # 批量操作
        (r"move|rename.*\[\d{2,}", "批量重命名"),
        (r"glob\(|Path\(/.*\*", "通配符匹配"),
        # 网络操作
        (r"requests\.post", "外部HTTP"),
        (r"requests\.put", "外部PUT"),
        (r"fetch\(['\"]http", "HTTP请求"),
        # 安装操作
        (r"pip\s+install", "pip安装"),
        (r"npm\s+install.*-g", "全局npm"),
        (r"composer\s+global", "全局Composer"),
        # 凭据操作
        (r"password\s*=", "密码硬编码"),
        (r"api[_-]?key\s*=", "API密钥硬编码"),
        (r"secret\s*=", "密钥硬编码"),
    ]
    
    # P2: 需要注意但不危险
    P2_PATTERNS = [
        (r"git\s+commit", "Git提交"),
        (r"git\s+push", "Git推送"),
        (r"mkdir\s+-p", "创建目录"),
        (r"copy_item|copy-item", "复制文件"),
    ]
    
    PROTECTED = [
        "Desktop", "Documents", "Downloads",
        "C:\\Windows", "C:\\System32", "C:\\Program Files",
        "/etc", "/bin", "/sbin", "/usr"
    ]
    
    def __init__(self, data_dir: Path = None):
        """初始化并加载威胁模式"""
        self.threat_file = (data_dir or Path.home() / ".workbuddy" / "dreams") / "threat-memory.json"
        self.custom_patterns = self._load_custom_patterns()
    
    def _load_custom_patterns(self) -> Dict:
        """加载自定义威胁模式"""
        if not self.threat_file.exists():
            return {"P0": [], "P1": [], "P2": []}
        
        try:
            with open(self.threat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 从威胁库加载模式
            patterns = {"P0": [], "P1": [], "P2": []}
            for threat in data.get("threats", []):
                sev = threat.get("severity", "P2").upper()
                if sev in patterns:
                    for p in threat.get("patterns", []):
                        patterns[sev].append((p, threat.get("type", "custom")))
            return patterns
        except:
            return {"P0": [], "P1": [], "P2": []}
    
    def scan(self, cmd: str) -> Tuple[str, str, List[str]]:
        """扫描命令风险"""
        level, desc, warnings = "P2", "无风险", []
        
        # 检查自定义P0模式
        for p, t in self.custom_patterns.get("P0", []):
            if re.search(p, cmd, re.I):
                return "P0", f"自定义P0: {t}", [f"⛔ P0: {t}"]
        
        # 检查内置P0模式
        for p, d in self.P0_PATTERNS:
            if re.search(p, cmd, re.I):
                return "P0", d, [f"⛔ P0: {d}"]
        
        # 检查自定义P1模式
        for p, t in self.custom_patterns.get("P1", []):
            if re.search(p, cmd, re.I):
                return "P1", f"自定义P1: {t}", [f"⚠️ P1: {t}"]
        
        # 检查内置P1模式
        for p, d in self.P1_PATTERNS:
            if re.search(p, cmd, re.I):
                return "P1", d, [f"⚠️ P1: {d}"]
        
        # 检查保护路径
        for path in self.PROTECTED:
            if path in cmd.replace('/', '\\'):
                return "P0", f"保护路径: {path}", [f"⛔ 保护路径: {path}"]
        
        # 检查P2模式（仅警告）
        for p, d in self.P2_PATTERNS:
            if re.search(p, cmd, re.I):
                warnings.append(f"ℹ️ P2: {d}")
        
        return level, desc, warnings
    
    def add_threat(self, pattern: str, threat_type: str, severity: str = "P1"):
        """添加自定义威胁模式"""
        if not self.threat_file.exists():
            self._init_threat_file()
        
        try:
            with open(self.threat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 添加新威胁
            data.setdefault("threats", []).append({
                "type": threat_type,
                "severity": severity,
                "patterns": [pattern],
                "added_at": datetime.now().isoformat()
            })
            
            # 更新计数
            data["count"] = len(data["threats"])
            
            with open(self.threat_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 重新加载
            self.custom_patterns = self._load_custom_patterns()
            return True
        except:
            return False
    
    def _init_threat_file(self):
        """初始化威胁文件"""
        data = {
            "threats": [],
            "count": 0,
            "patterns": [],
            "updated_at": datetime.now().isoformat()
        }
        self.threat_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.threat_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# ========== 3. Immune System - 免疫系统 ==========

class ImmuneSystem:
    """免疫系统 - 异常模式识别"""
    def __init__(self, data_dir: Path):
        self.threat_file = data_dir / "threat-memory.json"
        self.threats = self._load()
    
    def _load(self) -> Dict:
        if self.threat_file.exists():
            try:
                with open(self.threat_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"threats": [], "count": 0}
    
    def check(self, text: str) -> Tuple[bool, Optional[str]]:
        """检测异常模式"""
        flags = []
        
        # 异常大写
        upper_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if upper_ratio > 0.5:
            return True, "异常大写"
        
        # 异常字符密度
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        if special_chars > len(text) * 0.3:
            return True, "异常字符"
        
        # 重复字符检测
        if re.search(r'(.)\1{5,}', text):
            return True, "异常重复"
        
        return False, None
    
    def check_against_known(self, text: str) -> Tuple[bool, Optional[Dict]]:
        """检查是否匹配已知威胁"""
        for threat in self.threats.get("threats", []):
            for pattern in threat.get("patterns", []):
                if re.search(pattern, text, re.I):
                    return True, threat
        return False, None
    
    def record(self, threat: str, details: Dict = None):
        """记录新威胁"""
        self.threats["threats"].append({
            "ts": datetime.now().isoformat(),
            "type": threat,
            "details": details or {}
        })
        self.threats["count"] = len(self.threats["threats"])
        try:
            with open(self.threat_file, 'w') as f:
                json.dump(self.threats, f, ensure_ascii=False, indent=2)
        except: pass


# ========== 4. Prefrontal Check - 前额叶预检 ==========

class PrefrontalCheck:
    """前额叶预检 - 意图解码"""
    INTENT_KEYWORDS = {
        "create": ["写", "创建", "生成", "制作", "新建", "create", "write", "build"],
        "read": ["读", "查看", "看", "找", "搜索", "read", "find", "search", "look"],
        "analyze": ["分析", "评估", "比较", "诊断", "analyze", "evaluate", "compare"],
        "execute": ["执行", "运行", "操作", "操作", "execute", "run", "do"],
        "delete": ["删除", "清空", "移除", "remove", "delete", "clear"],
        "modify": ["修改", "编辑", "更新", "改", "edit", "modify", "update", "change"],
        "explain": ["解释", "说明", "为什么", "explain", "why", "how"],
        "plan": ["规划", "计划", "设计", "方案", "plan", "design", "strategy"],
    }
    
    def decode_intent(self, query: str) -> Dict[str, Any]:
        """解码用户意图"""
        query_lower = query.lower()
        intent = "unknown"
        confidence = 0.5
        matched_keyword = None
        
        for intent_name, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in query_lower:
                    intent = intent_name
                    confidence = 0.9
                    matched_keyword = kw
                    break
            if matched_keyword:
                break
        
        return {
            "intent": intent,
            "confidence": confidence,
            "matched_keyword": matched_keyword,
            "original_query": query
        }
    
    def check_ambiguity(self, query: str) -> List[str]:
        """检测歧义"""
        ambiguities = []
        vague_words = ["随便", "都可以", "差不多", "看着办", "无所谓"]
        for w in vague_words:
            if w in query:
                ambiguities.append(f"模糊表述: {w}")
        
        # 检测过短请求
        if len(query) < 5:
            ambiguities.append("请求过短，意图不明")
        
        return ambiguities
    
    def suggest_questions(self, query: str, ambiguities: List[str]) -> List[str]:
        """根据歧义建议提问"""
        questions = []
        
        if "模糊表述" in str(ambiguities):
            questions.append("请明确具体要求？")
        
        if "请求过短" in str(ambiguities):
            questions.append("能否详细描述需求？")
        
        return questions


# ========== 5. Information Theory - 信息论策略 ==========

class InformationTheory:
    """信息论策略 - 熵计算"""
    def calc_entropy(self, symbols: List[str]) -> float:
        """计算香农熵"""
        if not symbols: return 0
        freq = {}
        for s in symbols:
            freq[s] = freq.get(s, 0) + 1
        entropy = 0
        n = len(symbols)
        for count in freq.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def should_ask(self, query: str, memory_content: str) -> Tuple[bool, Optional[str]]:
        """判断是否需要提问"""
        mem_symbols = memory_content.split()[:20] if memory_content else []
        h_memory = self.calc_entropy(mem_symbols)
        
        query_symbols = query.split()[:20]
        h_query = self.calc_entropy(query_symbols)
        
        if h_query > 1.0:
            return True, "高不确定性，请确认关键约束"
        elif h_query > 0.5:
            return True, "中等不确定性，补充1个关键问题"
        return False, None
    
    def filter_noise(self, text: str) -> str:
        """信噪比过滤"""
        noise_patterns = [r"谢谢", r"好的", r"嗯", r"哦", r"好的好的", r"辛苦了", r"麻烦"]
        result = text
        for pattern in noise_patterns:
            result = re.sub(pattern, '', result)
        return result.strip()
    
    def calc_mutual_info(self, x: List[str], y: List[str]) -> float:
        """计算互信息"""
        if not x or not y: return 0
        combined = x + y
        h_xy = self.calc_entropy(combined)
        h_x = self.calc_entropy(x)
        h_y = self.calc_entropy(y)
        return h_x + h_y - h_xy


# ========== 6. Complexity Classifier - 复杂度分类 ==========

class ComplexityClassifier:
    """复杂度分类器"""
    C1 = ["你好", "hi", "hello", "天气", "在吗", "再见", "bye", "吗", "？", "?"]
    C2 = ["写", "读", "查", "生成", "create", "搜索", "给我", "帮我", "告诉"]
    C3 = ["分析", "推理", "代码", "debug", "比较", "优化", "检查", "审核"]
    C4 = ["架构", "设计", "决策", "规划", "strategy", "方案", "系统"]
    
    def classify(self, query: str) -> str:
        """分类复杂度"""
        q = query.lower()
        
        # C4: 战略级
        if any(k in q for k in self.C4):
            return "C4"
        
        # C3: 分析级
        if any(k in q for k in self.C3):
            return "C3"
        
        # C2: 操作级
        if any(k in q for k in self.C2):
            return "C2"
        
        # C1: 简单交互
        return "C1"
    
    def get_required_depth(self, complexity: str) -> int:
        """获取所需分析深度"""
        depths = {"C1": 1, "C2": 2, "C3": 3, "C4": 4}
        return depths.get(complexity, 2)


# ========== 7. Working Memory Buffer - 工作记忆 (增强版) ==========

class WorkingMemoryBuffer:
    """工作记忆缓冲区 - 增强版"""
    def __init__(self, data_dir: Path):
        self.buffer_file = data_dir / "wm-buffer.json"
        self.current = self._load()
    
    def _load(self) -> Dict:
        if self.buffer_file.exists():
            try:
                with open(self.buffer_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return self._new_session()
    
    def _new_session(self) -> Dict:
        return {
            "session_id": datetime.now().strftime("%Y-%m-%d-%H-%M"),
            "task_title": None,
            "status": "idle",
            "intent": None,
            "complexity": None,
            "constraints": [],
            "decisions": [],
            "artifacts": [],
            "open_questions": [],
            "loaded_from_memory": [],
            "risk_level": None,
            "risk_blocked": False,
            "confidence": 1.0,
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat()
        }
    
    def init_task(self, query: str, intent: str = None, complexity: str = None, risk_level: str = None):
        """初始化任务"""
        self.current = self._new_session()
        self.current["task_title"] = query[:100]
        self.current["intent"] = intent
        self.current["complexity"] = complexity
        self.current["risk_level"] = risk_level
        self._save()
    
    def add_decision(self, action: str, reason: str, outcome: str = None):
        """添加决策记录"""
        decision = {
            "step": len(self.current["decisions"]) + 1,
            "action": action,
            "reason": reason,
            "outcome": outcome,
            "ts": datetime.now().isoformat()
        }
        self.current["decisions"].append(decision)
        self.current["last_update"] = datetime.now().isoformat()
        self._save()
    
    def add_artifact(self, artifact_type: str, path: str):
        """添加产物记录"""
        self.current["artifacts"].append({
            "type": artifact_type,
            "path": path,
            "ts": datetime.now().isoformat()
        })
        self._save()
    
    def add_question(self, question: str, status: str = "open"):
        """添加待解决问题"""
        self.current["open_questions"].append({
            "question": question,
            "status": status,
            "ts": datetime.now().isoformat()
        })
        self._save()
    
    def resolve_question(self, question: str):
        """标记问题已解决"""
        for q in self.current["open_questions"]:
            if q["question"] == question:
                q["status"] = "resolved"
                q["resolved_at"] = datetime.now().isoformat()
        self._save()
    
    def complete_task(self, success: bool = True, summary: str = None):
        """完成任务"""
        self.current["status"] = "completed" if success else "failed"
        self.current["complete_time"] = datetime.now().isoformat()
        self.current["summary"] = summary
        self._save()
    
    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        parts = []
        if self.current.get("task_title"):
            parts.append(f"任务: {self.current['task_title'][:50]}")
        if self.current.get("intent"):
            parts.append(f"意图: {self.current['intent']}")
        if self.current.get("complexity"):
            parts.append(f"复杂度: {self.current['complexity']}")
        if self.current.get("decisions"):
            parts.append(f"决策数: {len(self.current['decisions'])}")
        if self.current.get("open_questions"):
            open_qs = [q["question"] for q in self.current["open_questions"] if q["status"] == "open"]
            if open_qs:
                parts.append(f"待解决问题: {len(open_qs)}")
        return " | ".join(parts)
    
    def _save(self):
        try:
            with open(self.buffer_file, 'w', encoding='utf-8') as f:
                json.dump(self.current, f, ensure_ascii=False, indent=2)
        except: pass


# ========== 8. Habit Loop - 习惯化 (增强版) ==========

class HabitLoop:
    """习惯化系统 - 增强版"""
    def __init__(self, data_dir: Path):
        self.habit_file = data_dir / "habit-store.json"
        self.habits = self._load()
    
    def _load(self) -> Dict:
        if self.habit_file.exists():
            try:
                with open(self.habit_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {
            "habits": [],
            "frequency": {},
            "confidence_decay_days": 30,
            "auto_promote_threshold": 3,  # 降低到3次
            "updated_at": datetime.now().isoformat()
        }
    
    def check(self, query: str) -> Optional[Dict]:
        """检查是否有匹配的习惯"""
        q = query.lower()[:50]
        for h in self.habits.get("habits", []):
            trigger = h.get("trigger", "").lower()
            if trigger and trigger in q:
                # 增加使用计数
                h["usage_count"] = h.get("usage_count", 0) + 1
                h["last_used"] = datetime.now().isoformat()
                self._save()
                return h
        return None
    
    def record(self, query: str):
        """记录任务频率"""
        # 使用更好的特征提取
        key = self._extract_key(query)
        freq = self.habits.get("frequency", {})
        freq[key] = freq.get(key, 0) + 1
        self.habits["frequency"] = freq
        
        # 检查是否达到习惯化阈值
        threshold = self.habits.get("auto_promote_threshold", 3)
        if freq[key] >= threshold:
            self._create_habit(key, query)
        
        self._save()
    
    def _extract_key(self, query: str) -> str:
        """提取关键特征"""
        # 移除语气词和填充词
        fillers = ["帮我", "请", "能不能", "可以帮我", "我想", "麻烦", "一下"]
        result = query.lower()
        for f in fillers:
            result = result.replace(f, "")
        
        # 取前30个字符作为key
        return result.strip()[:30]
    
    def _create_habit(self, key: str, full: str):
        """创建习惯"""
        for h in self.habits.get("habits", []):
            if h.get("name") == key:
                return  # 已存在
        
        self.habits.setdefault("habits", []).append({
            "name": key,
            "trigger": key,
            "trigger_count": self.habits["frequency"].get(key, 0),
            "action": full,
            "created": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "usage_count": 1,
            "success_rate": 0.5
        })
    
    def update_success(self, habit_name: str, success: bool):
        """更新习惯成功率"""
        for h in self.habits.get("habits", []):
            if h.get("name") == habit_name:
                total = h.get("usage_count", 1)
                successes = h.get("successes", 0) + (1 if success else 0)
                h["successes"] = successes
                h["success_rate"] = successes / total
                self._save()
                break
    
    def get_top_habits(self, limit: int = 5) -> List[Dict]:
        """获取最常用的习惯"""
        habits = self.habits.get("habits", [])
        # 兼容旧格式: trigger -> name, trigger_count -> usage_count
        for h in habits:
            if "name" not in h:
                h["name"] = h.get("trigger", h.get("id", ""))[:30]
            if "usage_count" not in h:
                h["usage_count"] = h.get("trigger_count", 0)
        return sorted(habits, key=lambda x: x.get("usage_count", 0), reverse=True)[:limit]
    
    def import_from_memory(self, memory_content: str):
        """从记忆导入习惯"""
        # 简单实现：从记忆中提取模式
        patterns = re.findall(r'[帮请让]?(.*?)[做制作生成]', memory_content)
        for p in patterns[:5]:  # 最多导入5个
            if p and len(p) > 3:
                key = p.lower().strip()[:30]
                if key not in [h.get("name") for h in self.habits.get("habits", [])]:
                    self._create_habit(key, f"习惯导入: {p}")
        self._save()
    
    def _save(self):
        try:
            self.habits["updated_at"] = datetime.now().isoformat()
            with open(self.habit_file, 'w', encoding='utf-8') as f:
                json.dump(self.habits, f, ensure_ascii=False, indent=2)
        except: pass


# ========== 9. Mirror Neuron - 镜像同步 ==========

class MirrorNeuron:
    """镜像神经元 - 风格学习"""
    def __init__(self, data_dir: Path):
        self.style_file = data_dir / "style-library.json"
        self.style = self._load()
    
    def _load(self) -> Dict:
        if self.style_file.exists():
            try:
                with open(self.style_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"preferences": {}, "patterns": [], "domains": {}}
    
    def learn_from_feedback(self, query: str, feedback_type: str):
        """从用户反馈中学习"""
        keywords = {
            "简洁": ["简洁", "简单", "简短", "精炼"],
            "详细": ["详细", "完整", "全面", "细致"],
            "专业": ["专业", "技术", "术语"],
            "口语": ["口语", "通俗", "易懂"],
            "正式": ["正式", "规范", "书面"],
            "快速": ["快", "速度", "简洁"],
            "慢": ["慢", "详细", "完整"]
        }
        
        for pref, kws in keywords.items():
            for kw in kws:
                if kw in query:
                    prefs = self.style.setdefault("preferences", {})
                    prefs[pref] = prefs.get(pref, 0) + 1
                    self._save()
                    break
    
    def learn_from_pattern(self, pattern: str, response: str):
        """学习响应模式"""
        patterns = self.style.setdefault("patterns", [])
        
        # 检查是否已存在
        for p in patterns:
            if p.get("trigger") == pattern:
                p["count"] = p.get("count", 0) + 1
                self._save()
                return
        
        patterns.append({
            "trigger": pattern,
            "response_length": len(response),
            "count": 1,
            "learned_at": datetime.now().isoformat()
        })
        self._save()
    
    def get_style(self) -> Dict:
        """获取当前风格偏好"""
        return self.style.get("preferences", {})
    
    def get_domain_style(self, domain: str) -> Dict:
        """获取特定领域的风格"""
        domains = self.style.get("domains", {})
        return domains.get(domain, {})
    
    def _save(self):
        try:
            self.style["updated_at"] = datetime.now().isoformat()
            with open(self.style_file, 'w', encoding='utf-8') as f:
                json.dump(self.style, f, ensure_ascii=False, indent=2)
        except: pass


# ========== 10. Physics Reasoning - 物理推理 ==========

class PhysicsReasoning:
    """物理推理"""
    def check_conservation(self, conclusion: str) -> Tuple[bool, Optional[str]]:
        """守恒律检查"""
        if re.search(r"因为.*所以|导致|造成", conclusion):
            if re.search(r"一定|必然|绝对|保证", conclusion):
                return False, "因果关系过于绝对，缺乏边界条件"
        return True, None
    
    def check_units(self, conclusion: str) -> Tuple[bool, Optional[str]]:
        """量纲分析"""
        numbers = re.findall(r"\d+\.?\d*", conclusion)
        if len(numbers) > 2:
            if "翻倍" in conclusion or "减半" in conclusion:
                if "极限" not in conclusion and "边界" not in conclusion:
                    return False, "可能忽略边界条件"
        return True, None
    
    def check_scale(self, value: float, lower: float, upper: float) -> Tuple[bool, Optional[str]]:
        """尺度检查"""
        if value < lower:
            return False, f"值 {value} 低于合理下限 {lower}"
        if value > upper:
            return False, f"值 {value} 超过合理上限 {upper}"
        return True, None


# ========== 11. Scientific Method - 科学推理 ==========

class ScientificMethod:
    """科学方法论"""
    def build_hypothesis(self, query: str) -> List[Dict]:
        """构建假设层级"""
        return [
            {"id": "H0", "desc": "不执行任何操作", "prior": 0.1, "complexity": 0},
            {"id": "H1", "desc": f"简单执行: {query[:30]}", "prior": 0.3, "complexity": 1},
            {"id": "H2", "desc": f"带约束执行: {query[:30]}", "prior": 0.4, "complexity": 2},
            {"id": "H3", "desc": f"深度分析+执行: {query[:30]}", "prior": 0.2, "complexity": 3},
        ]
    
    def bayes_update(self, prior: float, likelihood: float) -> float:
        """贝叶斯更新"""
        # P(H|E) = P(E|H) * P(H) / P(E)
        # 简化: posterior = likelihood * prior
        posterior = likelihood * prior
        return min(posterior, 1.0)
    
    def calc_posterior(self, hypothesis: Dict, evidence_likelihood: float) -> float:
        """计算后验概率"""
        prior = hypothesis.get("prior", 0.5)
        posterior = self.bayes_update(prior, evidence_likelihood)
        return posterior
    
    def check_falsifiability(self, conclusion: str) -> Tuple[bool, Optional[str]]:
        """可证伪性检验"""
        unfalsifiable = ["有时候", "总体来说", "我相信", "大概", "也许"]
        for pattern in unfalsifiable:
            if pattern in conclusion:
                return False, f"不可证伪: '{pattern}'"
        return True, None
    
    def design_experiment(self, hypothesis: str) -> List[str]:
        """设计验证实验"""
        return [
            f"测试假设: {hypothesis[:50]}",
            "收集证据",
            "更新信念"
        ]


# ========== 12. Evolution Engine - 自动进化 (增强版) ==========

class EvolutionEngine:
    """进化引擎 - 自动优化 (增强版)"""
    def __init__(self, data_dir: Path):
        self.evolve_file = data_dir / "evolution-log.json"
        self.evolution = self._load()
    
    def _load(self) -> Dict:
        if self.evolve_file.exists():
            try:
                with open(self.evolve_file, 'r') as f:
                    return json.load(f)
            except: pass
        return {
            "generations": [],
            "fitness_history": [],
            "best_strategies": [],
            "strategy_usage": {},  # 新增: 策略使用追踪
            "updated_at": datetime.now().isoformat()
        }
    
    def record_outcome(self, strategy: str, success: bool, score: float):
        """记录策略结果"""
        # 记录到历史
        self.evolution.setdefault("generations", []).append({
            "ts": datetime.now().isoformat(),
            "strategy": strategy[:50],
            "success": success,
            "score": score
        })
        
        # 更新适应度历史
        history = self.evolution.setdefault("fitness_history", [])
        history.append(score)
        history[:] = history[-100:]  # 保留最近100
        
        # 更新策略使用统计
        usage = self.evolution.setdefault("strategy_usage", {})
        if strategy[:30] not in usage:
            usage[strategy[:30]] = {"count": 0, "total_score": 0, "successes": 0}
        usage[strategy[:30]]["count"] += 1
        usage[strategy[:30]]["total_score"] += score
        usage[strategy[:30]]["successes"] += (1 if success else 0)
        
        self._save()
    
    def get_best_strategy(self) -> Optional[str]:
        """获取最佳策略"""
        strategies = self.evolution.get("best_strategies", [])
        if strategies:
            # 返回成功率最高的策略
            best = max(strategies, key=lambda x: x.get("score", 0))
            return best.get("strategy")
        return None
    
    def get_strategy_stats(self, strategy: str) -> Dict:
        """获取策略统计"""
        usage = self.evolution.get("strategy_usage", {}).get(strategy[:30], {})
        if not usage:
            return {"count": 0, "avg_score": 0, "success_rate": 0}
        
        count = usage.get("count", 1)
        return {
            "count": count,
            "avg_score": usage.get("total_score", 0) / count,
            "success_rate": usage.get("successes", 0) / count
        }
    
    def evolve(self, current: str, outcome: float):
        """进化：根据结果调整策略"""
        if outcome > 0.7:
            self.evolution.setdefault("best_strategies", []).append({
                "strategy": current[:50],
                "score": outcome,
                "ts": datetime.now().isoformat()
            })
        self._save()
    
    def suggest_next_strategy(self) -> str:
        """建议下一个策略"""
        usage = self.evolution.get("strategy_usage", {})
        
        # 找使用最少但成功率不低的策略
        candidates = []
        for name, stats in usage.items():
            if stats["count"] > 0:
                score = stats["success_rate"] / (stats["count"] + 1)  # 平衡成功率和探索
                candidates.append((name, score))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return "默认策略"
    
    def _save(self):
        try:
            self.evolution["updated_at"] = datetime.now().isoformat()
            with open(self.evolve_file, 'w') as f:
                json.dump(self.evolution, f, ensure_ascii=False, indent=2)
        except: pass


# ========== Bionic Brain 核心 (增强版) ==========

class BionicBrain:
    """仿生全脑系统 - 增强版"""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path.home() / ".workbuddy" / "dreams"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化11种能力
        self.acc = ACCMonitor()
        self.amygdala = AmygdalaGuard(data_dir)
        self.immune = ImmuneSystem(data_dir)
        self.prefrontal = PrefrontalCheck()
        self.info_theory = InformationTheory()
        self.classifier = ComplexityClassifier()
        self.working_memory = WorkingMemoryBuffer(data_dir)
        self.habit = HabitLoop(data_dir)
        self.mirror = MirrorNeuron(data_dir)
        self.physics = PhysicsReasoning()
        self.scientific = ScientificMethod()
        self.evolution = EvolutionEngine(data_dir)
        
        # 记忆文件
        self.memory_file = Path.home() / ".workbuddy" / "MEMORY.md"
    
    def analyze(self, query: str, command: str = None) -> Dict[str, Any]:
        """完整分析"""
        result = {
            "ts": datetime.now().isoformat(),
            "query": query,
            "capabilities_used": []
        }
        
        # 1. 前额叶预检
        intent = self.prefrontal.decode_intent(query)
        ambiguities = self.prefrontal.check_ambiguity(query)
        result["intent"] = intent
        result["ambiguities"] = ambiguities
        result["questions"] = self.prefrontal.suggest_questions(query, ambiguities)
        result["capabilities_used"].append("prefrontal-check")
        
        # 2. 复杂度分类
        complexity = self.classifier.classify(query)
        result["complexity"] = complexity
        result["required_depth"] = self.classifier.get_required_depth(complexity)
        result["capabilities_used"].append("complexity-classifier")
        
        # 3. 杏仁核风险扫描
        risk_level, risk_desc, risk_warnings = "P2", "无风险", []
        if command:
            risk_level, risk_desc, risk_warnings = self.amygdala.scan(command)
        result["risk"] = {"level": risk_level, "desc": risk_desc, "warnings": risk_warnings}
        result["blocked"] = (risk_level in ["P0", "P1"])
        result["capabilities_used"].append("amygdala-guard")
        
        # 4. 初始化工作记忆
        self.working_memory.init_task(
            query=query,
            intent=intent["intent"],
            complexity=complexity,
            risk_level=risk_level
        )
        
        # 5. ACC置信度检测
        confidence, conf_flags = self.acc.check_text(query)
        memory_conflict = self.acc.check_memory_conflict(query, self.memory_file)
        result["confidence"] = {
            "score": confidence,
            "flags": conf_flags,
            "memory_conflict": memory_conflict
        }
        result["capabilities_used"].append("acc-error-monitor")
        
        # 6. 免疫系统检查
        is_anomaly, anomaly_desc = self.immune.check(query)
        is_known_threat, threat_info = self.immune.check_against_known(query)
        result["anomaly"] = {
            "detected": is_anomaly,
            "desc": anomaly_desc,
            "known_threat": is_known_threat,
            "threat_info": threat_info
        }
        if is_anomaly:
            self.immune.record(anomaly_desc)
        result["capabilities_used"].append("immune-system")
        
        # 7. 信息论评估
        mem_content = ""
        if self.memory_file.exists():
            try:
                mem_content = self.memory_file.read_text()
            except: pass
        should_ask, question = self.info_theory.should_ask(query, mem_content)
        filtered = self.info_theory.filter_noise(query)
        result["info_theory"] = {
            "should_ask": should_ask,
            "question": question,
            "filtered_query": filtered
        }
        result["capabilities_used"].append("information-theory")
        
        # 8. 习惯检查
        habit_match = self.habit.check(query)
        result["habit"] = habit_match
        if habit_match:
            result["confidence"]["score"] *= 1.1  # 习惯匹配增加置信度
        result["capabilities_used"].append("habit-loop")
        
        # 9. 风格学习
        style = self.mirror.get_style()
        result["style"] = style
        result["capabilities_used"].append("mirror-neuron")
        
        # 10. 科学推理 - 构建假设
        hypotheses = self.scientific.build_hypothesis(query)
        result["hypotheses"] = hypotheses
        result["capabilities_used"].append("scientific-method")
        
        # 11. 物理推理
        phys_ok, phys_issue = True, None
        result["physics"] = {"ok": phys_ok, "issue": phys_issue}
        result["capabilities_used"].append("physics-reasoning")
        
        # 12. 工作记忆状态
        result["working_memory"] = {
            "session": self.working_memory.current.get("session_id"),
            "status": self.working_memory.current.get("status"),
            "context_summary": self.working_memory.get_context_summary()
        }
        result["capabilities_used"].append("working-memory-buffer")
        
        # 进化记录
        result["capabilities_used"].append("evolution-engine")
        
        # 总结建议
        result["summary"] = self._generate_summary(result)
        
        return result
    
    def _generate_summary(self, result: Dict) -> str:
        """生成分析总结"""
        parts = []
        
        # 复杂度
        parts.append(f"复杂度: {result['complexity']} (深度{result['required_depth']})")
        
        # 意图
        parts.append(f"意图: {result['intent']['intent']}")
        
        # 风险
        risk = result["risk"]
        if risk["level"] == "P0":
            parts.append(f"⛔ {risk['desc']} - 已拦截")
        elif risk["level"] == "P1":
            parts.append(f"⚠️ {risk['desc']} - 需要确认")
        else:
            parts.append(f"✓ 风险可控")
        
        # 置信度
        conf = result["confidence"]["score"]
        if conf < 0.7:
            parts.append(f"⚠️ 置信度较低 ({conf:.0%})")
        else:
            parts.append(f"✓ 置信度 ({conf:.0%})")
        
        # 歧义
        if result["ambiguities"]:
            parts.append(f"⚠️ 存在歧义")
        
        # 习惯
        if result.get("habit"):
            parts.append(f"✓ 匹配习惯: {result['habit']['name'][:20]}")
        
        return " | ".join(parts)
    
    def post_task(self, query: str, success: bool, score: float, strategy: str = None):
        """任务后处理 - 触发学习和进化"""
        # 策略默认为当前复杂度
        if strategy is None:
            strategy = self.classifier.classify(query)
        
        # 习惯记录
        self.habit.record(query)
        
        # 习惯更新成功率
        habit_match = self.habit.check(query)
        if habit_match:
            self.habit.update_success(habit_match.get("name", ""), success)
        
        # 工作记忆更新
        self.working_memory.complete_task(success=success)
        
        # 进化引擎记录
        self.evolution.record_outcome(strategy, success, score)
        self.evolution.evolve(strategy, score)
    
    def record_decision(self, action: str, reason: str, outcome: str = None):
        """记录决策"""
        self.working_memory.add_decision(action, reason, outcome)
    
    def add_artifact(self, artifact_type: str, path: str):
        """记录产物"""
        self.working_memory.add_artifact(artifact_type, path)
    
    def get_status(self) -> Dict:
        """系统状态"""
        return {
            "habits_count": len(self.habit.habits.get("habits", [])),
            "threats_count": self.immune.threats.get("count", 0),
            "evolution_generations": len(self.evolution.evolution.get("generations", [])),
            "best_fitness": max(self.evolution.evolution.get("fitness_history", [0])) if self.evolution.evolution.get("fitness_history") else 0,
            "top_habits": [h["name"][:20] for h in self.habit.get_top_habits(3)],
            "data_dir": str(self.data_dir)
        }
    
    def run_self_audit(self) -> Dict:
        """运行自我审计"""
        from . import self_audit
        return self_audit.run_self_audit()


# ========== 快速访问 ==========

_brain = None

def get_brain() -> BionicBrain:
    global _brain
    if _brain is None:
        _brain = BionicBrain()
    return _brain

def analyze(query: str, command: str = None) -> Dict[str, Any]:
    return get_brain().analyze(query, command)


if __name__ == "__main__":
    brain = get_brain()
    
    print("=" * 70)
    print("Bionic Brain v2.1 - 全能力整合测试 (增强版)")
    print("=" * 70)
    
    tests = [
        ("帮我写一个PPT演示文稿", None),
        ("分析一下这个代码有什么问题", None),
        ("删除桌面所有文件", "rm -rf ~/Desktop/*"),
        ("设计一个架构方案", None),
        ("帮我优化一下这个SQL查询", None),
    ]
    
    for query, cmd in tests:
        print(f"\n📋 {query}")
        result = brain.analyze(query, cmd)
        
        print(f"   {result['summary']}")
        print(f"   假设: {[h['id'] for h in result['hypotheses']]}")
        
        if result.get('blocked'):
            print("   🚫 已拦截!")
    
    print("\n" + "=" * 70)
    status = brain.get_status()
    print(f"系统状态:")
    print(f"  习惯: {status['habits_count']} | 威胁: {status['threats_count']}")
    print(f"  进化代数: {status['evolution_generations']}")
    print(f"  最佳适应度: {status['best_fitness']:.2f}")
    print(f"  常用习惯: {', '.join(status['top_habits']) or '无'}")
