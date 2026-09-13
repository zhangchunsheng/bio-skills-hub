#!/usr/bin/env python3
"""
bionic-brain 安装初始化脚本
自动创建必要的数据目录和配置文件
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def get_data_dir():
    """获取数据目录"""
    home = Path.home()
    data_dir = home / ".workbuddy" / "dreams"
    return data_dir

def init_data_files():
    """初始化数据文件"""
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    files = {}

    # 1. 进化日志
    evo_file = data_dir / "evolution-log.json"
    if not evo_file.exists():
        files["evolution-log.json"] = {
            "generations": [],
            "fitness_history": [],
            "best_strategies": [],
            "strategy_usage": {},
            "updated_at": datetime.now().isoformat()
        }

    # 2. 习惯存储
    habit_file = data_dir / "habit-store.json"
    if not habit_file.exists():
        files["habit-store.json"] = {
            "habits": [],
            "frequency": {},
            "confidence_decay_days": 30,
            "auto_promote_threshold": 3,
            "updated_at": datetime.now().isoformat()
        }

    # 3. 威胁记忆
    threat_file = data_dir / "threat-memory.json"
    if not threat_file.exists():
        files["threat-memory.json"] = {
            "threats": [],
            "count": 0,
            "patterns": [
                {"type": "recursive_delete", "severity": "critical",
                 "patterns": ["rm -rf", "rm /", "del /s"]},
                {"type": "credential_leak", "severity": "high",
                 "patterns": ["password=", "api_key=", "secret="]},
                {"type": "unauthorized_network", "severity": "medium",
                 "patterns": ["requests.post", "http://"]},
            ],
            "updated_at": datetime.now().isoformat()
        }

    # 4. 工作记忆
    wm_file = data_dir / "wm-buffer.json"
    if not wm_file.exists():
        files["wm-buffer.json"] = {
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

    # 5. 风格库
    style_file = data_dir / "style-library.json"
    if not style_file.exists():
        files["style-library.json"] = {
            "preferences": {},
            "patterns": [],
            "domains": {},
            "global_preferences": {
                "response_language": "zh-CN",
                "no_filler": True,
                "no_emoji_unless_asked": True,
                "direct_action": True,
                "precheck_before_complex_task": True,
                "risk_warning_before_action": True
            },
            "updated_at": datetime.now().isoformat()
        }

    # 写入文件
    for filename, content in files.items():
        filepath = data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        print(f"  + {filename}")

    return len(files)

def check_dependencies():
    """检查依赖"""
    print("\n检查依赖...")

    # Python版本
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"  ! Python {version.major}.{version.minor} (需要 3.7+)")
        return False

    print(f"  OK Python {version.major}.{version.minor}.{version.micro}")

    # 标准库
    std_libs = ["json", "math", "pathlib", "datetime", "re"]
    for lib in std_libs:
        try:
            __import__(lib)
            print(f"  OK {lib}")
        except ImportError:
            print(f"  ! {lib}")
            return False

    return True

def verify_installation():
    """验证安装"""
    print("\n验证安装...")

    try:
        from bionic_brain import BionicBrain, analyze, get_brain

        brain = get_brain()
        result = brain.analyze("测试任务")

        print(f"  OK 导入成功")
        print(f"  OK 复杂度: {result['complexity']}")
        print(f"  OK 风险: {result['risk']['level']}")

        return True

    except Exception as e:
        print(f"  ! 验证失败: {e}")
        return False

def main():
    print("=" * 60)
    print("bionic-brain 安装程序 v2.1.0")
    print("仿生认知大脑")
    print("=" * 60)

    if not check_dependencies():
        print("\n依赖检查失败")
        sys.exit(1)

    print("\n初始化数据文件...")
    count = init_data_files()
    print(f"已创建 {count} 个数据文件")

    data_dir = get_data_dir()
    print(f"\n数据目录: {data_dir}")

    if verify_installation():
        print("\n" + "=" * 60)
        print("安装成功!")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 查看示例: python examples/quickstart.py")
        print("  2. 运行测试: python scripts/__init__.py")
        print("  3. 自我审计: python scripts/self_audit.py")
    else:
        print("\n安装验证失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
