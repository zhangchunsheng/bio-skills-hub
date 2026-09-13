#!/usr/bin/env python3
"""
Prefrontal Intent Decoder
前额叶意图解码器

职责：
- 解析用户输入的意图
- 提取关键实体和参数
- 匹配最佳执行策略
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

class IntentType(Enum):
    """意图类型"""
    CREATE = "create"           # 创建
    READ = "read"               # 读取
    UPDATE = "update"           # 更新
    DELETE = "delete"           # 删除
    ANALYZE = "analyze"         # 分析
    OPTIMIZE = "optimize"       # 优化
    TRANSFORM = "transform"     # 转换
    EXECUTE = "execute"         # 执行
    QUERY = "query"             # 查询
    UNKNOWN = "unknown"         # 未知

@dataclass
class Intent:
    """意图对象"""
    raw_input: str
    intent_type: str
    confidence: float  # 0-1
    entities: Dict[str, Any]
    target: Optional[str]
    parameters: Dict[str, Any]
    timestamp: str
    
    def to_dict(self):
        return asdict(self)

class IntentDecoder:
    """意图解码器"""
    
    # 意图模式库
    INTENT_PATTERNS = {
        IntentType.CREATE: {
            "keywords": ["创建", "新建", "生成", "建立", "制作", "写", "make", "create", "generate", "build"],
            "patterns": [
                r"(?:创建|新建|生成)\s*([^.]+)",
                r"(?:帮我|请)?\s*(?:写|制作)\s*([^.]+)",
            ]
        },
        IntentType.READ: {
            "keywords": ["读取", "查看", "打开", "显示", "获取", "read", "open", "show", "get", "view"],
            "patterns": [
                r"(?:查看|打开|显示)\s*([^.]+)",
                r"(?:获取|读取)\s*([^.]+)",
            ]
        },
        IntentType.UPDATE: {
            "keywords": ["更新", "修改", "编辑", "更改", "调整", "update", "modify", "edit", "change"],
            "patterns": [
                r"(?:更新|修改|编辑)\s*([^.]+)",
                r"(?:把|将)\s*([^.]+?)\s*(?:改成|改为)",
            ]
        },
        IntentType.DELETE: {
            "keywords": ["删除", "移除", "清除", "清理", "delete", "remove", "clear", "clean"],
            "patterns": [
                r"(?:删除|移除|清除)\s*([^.]+)",
                r"(?:清理|清空)\s*([^.]+)",
            ]
        },
        IntentType.ANALYZE: {
            "keywords": ["分析", "检查", "评估", "诊断", "analyze", "check", "evaluate", "diagnose"],
            "patterns": [
                r"(?:分析|检查|评估)\s*([^.]+)",
                r"([^.]+?)\s*(?:怎么样|如何|分析)",
            ]
        },
        IntentType.OPTIMIZE: {
            "keywords": ["优化", "改进", "提升", "完善", "optimize", "improve", "enhance", "refine"],
            "patterns": [
                r"(?:优化|改进|提升|完善)\s*([^.]+)",
                r"(?:帮我|请)?\s*(?:优化|改进)\s*([^.]+)",
            ]
        },
        IntentType.TRANSFORM: {
            "keywords": ["转换", "转变", "变成", "转为", "transform", "convert", "turn"],
            "patterns": [
                r"(?:转换|转变|转为)\s*([^.]+)",
                r"(?:把|将)\s*([^.]+?)\s*(?:转为|转换成)",
            ]
        },
        IntentType.EXECUTE: {
            "keywords": ["执行", "运行", "启动", "调用", "execute", "run", "start", "call"],
            "patterns": [
                r"(?:执行|运行|启动)\s*([^.]+)",
                r"(?:调用|使用)\s*([^.]+)",
            ]
        },
        IntentType.QUERY: {
            "keywords": ["查询", "搜索", "查找", "问", "query", "search", "find", "ask"],
            "patterns": [
                r"(?:查询|搜索|查找)\s*([^.]+)",
                r"(?:什么是|怎么|如何)\s*([^.]+)",
            ]
        }
    }
    
    # 文件类型实体
    FILE_TYPES = ["文件", "文档", "表格", "代码", "脚本", "配置", "图片", "视频", 
                  "file", "doc", "spreadsheet", "code", "script", "config", "image", "video"]
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".workbuddy" / "dreams" / "bionic-cognition"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.data_dir / "intent-cache.json"
        
        self._load_cache()
    
    def _load_cache(self):
        """加载意图缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8-sig') as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.cache = {"version": "1.0.0", "intents": []}
        else:
            self.cache = {"version": "1.0.0", "intents": []}
    
    def _save_cache(self):
        """保存意图缓存"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def decode(self, user_input: str) -> Intent:
        """
        解码用户意图
        
        Args:
            user_input: 用户输入
        
        Returns:
            Intent 对象
        """
        # 检查缓存
        cache_key = hash(user_input) % 1000000
        for cached in self.cache.get("intents", []):
            if cached.get("hash") == cache_key:
                return Intent(**cached["intent"])
        
        # 意图识别
        intent_type, confidence = self._classify_intent(user_input)
        
        # 实体提取
        entities = self._extract_entities(user_input)
        
        # 目标识别
        target = self._extract_target(user_input, intent_type)
        
        # 参数提取
        parameters = self._extract_parameters(user_input)
        
        intent = Intent(
            raw_input=user_input,
            intent_type=intent_type.value,
            confidence=confidence,
            entities=entities,
            target=target,
            parameters=parameters,
            timestamp=datetime.now().isoformat()
        )
        
        # 缓存
        self.cache["intents"].append({
            "hash": cache_key,
            "intent": intent.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
        self.cache["intents"] = self.cache["intents"][-100:]  # 保留最近100条
        self._save_cache()
        
        return intent
    
    def _classify_intent(self, text: str) -> Tuple[IntentType, float]:
        """分类意图"""
        text_lower = text.lower()
        scores = {}
        
        for intent_type, config in self.INTENT_PATTERNS.items():
            score = 0
            # 关键词匹配
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += 1
            
            # 模式匹配
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 2
            
            scores[intent_type] = score
        
        if not scores or max(scores.values()) == 0:
            return IntentType.UNKNOWN, 0.0
        
        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] / 5, 1.0)  # 归一化到0-1
        
        return best_intent, confidence
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """提取实体"""
        entities = {
            "file_types": [],
            "formats": [],
            "numbers": []
        }
        
        # 文件类型
        for ft in self.FILE_TYPES:
            if ft in text:
                entities["file_types"].append(ft)
        
        # 格式识别 (.xxx)
        formats = re.findall(r'\.([a-zA-Z0-9]+)', text)
        entities["formats"] = formats
        
        # 数字
        numbers = re.findall(r'\d+', text)
        entities["numbers"] = [int(n) for n in numbers]
        
        return entities
    
    def _extract_target(self, text: str, intent_type: IntentType) -> Optional[str]:
        """提取目标"""
        patterns = self.INTENT_PATTERNS.get(intent_type, {}).get("patterns", [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.groups():
                return match.group(1).strip()
        
        return None
    
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """提取参数"""
        params = {}
        
        # 路径参数
        paths = re.findall(r'[\w\\/]+(?:\.[\w]+)?', text)
        if paths:
            params["paths"] = paths
        
        # 布尔参数
        if any(word in text for word in ["强制", "force", "强制覆盖"]):
            params["force"] = True
        
        if any(word in text for word in ["递归", "recursive", "全部"]):
            params["recursive"] = True
        
        return params
    
    def get_intent_stats(self) -> Dict:
        """获取意图统计"""
        intents = self.cache.get("intents", [])
        type_counts = {}
        
        for item in intents:
            intent_type = item.get("intent", {}).get("intent_type", "unknown")
            type_counts[intent_type] = type_counts.get(intent_type, 0) + 1
        
        return {
            "total_decoded": len(intents),
            "by_type": type_counts,
            "recent": intents[-5:]
        }


# 单例
_decoder = None

def get_intent_decoder() -> IntentDecoder:
    global _decoder
    if _decoder is None:
        _decoder = IntentDecoder()
    return _decoder


if __name__ == "__main__":
    decoder = get_intent_decoder()
    
    # 测试
    test_inputs = [
        "帮我创建一个 Python 脚本",
        "分析一下这个文件的性能",
        "把文档转换成 PDF",
        "查询今天的天气",
    ]
    
    for text in test_inputs:
        intent = decoder.decode(text)
        print(f"\n输入: {text}")
        print(f"意图: {intent.intent_type} (置信度: {intent.confidence:.2f})")
        print(f"目标: {intent.target}")
        print(f"实体: {intent.entities}")
    
    print("\n统计:", json.dumps(decoder.get_intent_stats(), indent=2))
