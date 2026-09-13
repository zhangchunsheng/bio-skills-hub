#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旅游攻略生成器
基于LLM的旅游攻略生成技能
"""

import json
import sys

PROMPT_TEMPLATE = """请为我生成一份旅游攻略：

目的地：{destination}
出行天数：{days}天
预算范围：{budget}元/人
出行人数：{people}
旅行风格：{travel_style}
旅行偏好：{preferences}
出行季节：{season}
其他需求：{extra}

请按照你的工作流程，生成完整的旅游攻略。"""


def build_prompt(params):
    defaults = {
        "destination": "",
        "days": 3,
        "budget": "中等",
        "people": "2人",
        "travel_style": "自由行",
        "preferences": "综合",
        "season": "",
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
    if not params.get("destination"):
        return False, "缺少必填参数：destination（目的地）"
    if not params.get("days"):
        return False, "缺少必填参数：days（出行天数）"
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
