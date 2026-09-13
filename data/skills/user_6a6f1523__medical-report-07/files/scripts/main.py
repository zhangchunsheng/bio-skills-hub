#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
思维导图生成器
基于LLM的思维导图生成技能
"""

import json
import sys

PROMPT_TEMPLATE = """请为我生成一个思维导图：

主题：{topic}
结构类型：{structure}
层级深度：{depth}
侧重方向：{focus}
已有要点：{existing_points}
其他要求：{extra}

请按照你的工作流程，生成完整的思维导图Markdown文本。"""


def build_prompt(params):
    defaults = {
        "topic": "",
        "structure": "总分式",
        "depth": 3,
        "focus": "全面",
        "existing_points": "",
        "extra": "",
    }
    defaults.update(params)
    return PROMPT_TEMPLATE.format(**defaults)


def call_llm(prompt):
    """调用大语言模型生成结果（在SkillHub环境中由平台调度LLM）"""
    return {
        "status": "success",
        "prompt": prompt,
        "message": "请将prompt发送给LLM获取最终结果",
    }


def validate_params(params):
    if not params.get("topic"):
        return False, "缺少必填参数：topic（主题）"
    return True, "参数验证通过"


def main():
    params = {}
    if len(sys.argv) > 1:
        try:
            params = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "message": "参数格式错误"}, ensure_ascii=False))
            return
    
    valid, msg = validate_params(params)
    if not valid:
        print(json.dumps({"status": "error", "message": msg}, ensure_ascii=False))
        return
    
    prompt = build_prompt(params)
    result = call_llm(prompt)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
