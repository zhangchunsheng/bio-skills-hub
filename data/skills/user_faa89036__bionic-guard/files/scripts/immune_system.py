#!/usr/bin/env python3
"""
Immune System Threat Recognition
免疫系统威胁识别 - 长期威胁学习和识别

职责：
- 维护威胁签名库
- 学习新的威胁模式
- 提供主动防御建议
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict

@dataclass
class ThreatSignature:
    """威胁签名"""
    id: str
    pattern: str
    threat_type: str
    severity: int  # 1-5
    first_seen: str
    last_seen: str
    occurrence_count: int
    source: str
    description: str
    mitigation: str
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ThreatSignature":
        return cls(**data)

class ImmuneSystem:
    """免疫系统"""
    
    # 内置威胁签名
    BUILTIN_THREATS = [
        {
            "pattern": "eval\\s*\\(",
            "threat_type": "code_injection",
            "severity": 4,
            "description": "动态代码执行可能导致代码注入攻击",
            "mitigation": "使用ast.literal_eval替代eval，或验证输入白名单"
        },
        {
            "pattern": "pickle\\.loads",
            "threat_type": "deserialization",
            "severity": 5,
            "description": "不安全的反序列化可导致远程代码执行",
            "mitigation": "使用json替代pickle，或验证pickle数据来源"
        },
        {
            "pattern": "subprocess\\.call.*shell=True",
            "threat_type": "command_injection",
            "severity": 4,
            "description": "shell=True 结合用户输入可导致命令注入",
            "mitigation": "使用shell=False并传递参数列表，避免字符串拼接"
        },
        {
            "pattern": "SELECT.*FROM.*WHERE.*=.*\\$",
            "threat_type": "sql_injection",
            "severity": 5,
            "description": "SQL字符串拼接存在注入风险",
            "mitigation": "使用参数化查询或ORM"
        }
    ]
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".workbuddy" / "dreams" / "bionic-guard"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.signatures_file = self.data_dir / "threat-signatures.json"
        
        self.signatures: Dict[str, ThreatSignature] = {}
        self._load_signatures()
        
        # 如果没有数据，初始化内置签名
        if not self.signatures:
            self._init_builtin_signatures()
    
    def _load_signatures(self):
        """加载签名库"""
        if self.signatures_file.exists():
            try:
                with open(self.signatures_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    for sig_data in data.get("signatures", []):
                        sig = ThreatSignature.from_dict(sig_data)
                        self.signatures[sig.id] = sig
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.signatures = {}
    
    def _save_signatures(self):
        """保存签名库"""
        data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "total_signatures": len(self.signatures),
            "signatures": [sig.to_dict() for sig in self.signatures.values()]
        }
        with open(self.signatures_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _init_builtin_signatures(self):
        """初始化内置签名"""
        for threat in self.BUILTIN_THREATS:
            sig_id = hashlib.md5(threat["pattern"].encode()).hexdigest()[:8]
            now = datetime.now().isoformat()
            sig = ThreatSignature(
                id=sig_id,
                pattern=threat["pattern"],
                threat_type=threat["threat_type"],
                severity=threat["severity"],
                first_seen=now,
                last_seen=now,
                occurrence_count=0,
                source="builtin",
                description=threat["description"],
                mitigation=threat["mitigation"]
            )
            self.signatures[sig_id] = sig
        self._save_signatures()
    
    def scan(self, content: str, source: str = "") -> List[ThreatSignature]:
        """
        扫描威胁
        
        Args:
            content: 要扫描的内容
            source: 内容来源标识
        
        Returns:
            匹配的威胁签名列表
        """
        import re
        matched = []
        
        for sig in self.signatures.values():
            if re.search(sig.pattern, content, re.IGNORECASE):
                # 更新统计
                sig.last_seen = datetime.now().isoformat()
                sig.occurrence_count += 1
                matched.append(sig)
        
        if matched:
            self._save_signatures()
        
        return matched
    
    def learn(self, pattern: str, threat_type: str, severity: int, 
              description: str, mitigation: str, source: str = "user") -> str:
        """
        学习新的威胁模式
        
        Returns:
            新签名的ID
        """
        sig_id = hashlib.md5(pattern.encode()).hexdigest()[:8]
        now = datetime.now().isoformat()
        
        if sig_id in self.signatures:
            # 更新现有签名
            self.signatures[sig_id].last_seen = now
            self.signatures[sig_id].occurrence_count += 1
        else:
            # 创建新签名
            sig = ThreatSignature(
                id=sig_id,
                pattern=pattern,
                threat_type=threat_type,
                severity=severity,
                first_seen=now,
                last_seen=now,
                occurrence_count=1,
                source=source,
                description=description,
                mitigation=mitigation
            )
            self.signatures[sig_id] = sig
        
        self._save_signatures()
        return sig_id
    
    def forget(self, sig_id: str) -> bool:
        """遗忘指定签名"""
        if sig_id in self.signatures:
            del self.signatures[sig_id]
            self._save_signatures()
            return True
        return False
    
    def get_threat_report(self) -> Dict:
        """获取威胁报告"""
        by_type = {}
        by_severity = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        active_threats = []
        
        for sig in self.signatures.values():
            by_type[sig.threat_type] = by_type.get(sig.threat_type, 0) + 1
            by_severity[sig.severity] = by_severity.get(sig.severity, 0) + 1
            
            # 最近7天内出现过的视为活跃
            last_seen = datetime.fromisoformat(sig.last_seen)
            if datetime.now() - last_seen < timedelta(days=7):
                active_threats.append(sig.to_dict())
        
        return {
            "total_signatures": len(self.signatures),
            "by_type": by_type,
            "by_severity": by_severity,
            "active_threats": active_threats[:10],
            "top_threats": sorted(
                [s.to_dict() for s in self.signatures.values()],
                key=lambda x: x["occurrence_count"],
                reverse=True
            )[:5]
        }


# 单例
_immune = None

def get_immune_system() -> ImmuneSystem:
    global _immune
    if _immune is None:
        _immune = ImmuneSystem()
    return _immune


if __name__ == "__main__":
    immune = get_immune_system()
    
    # 测试扫描
    test_code = """
    user_input = request.args.get('code')
    result = eval(user_input)
    """
    
    threats = immune.scan(test_code, "test.py")
    for t in threats:
        print(f"[Threat-{t.severity}] {t.threat_type}: {t.description}")
        print(f"  缓解措施: {t.mitigation}")
    
    print("\n威胁报告:", json.dumps(immune.get_threat_report(), indent=2))
