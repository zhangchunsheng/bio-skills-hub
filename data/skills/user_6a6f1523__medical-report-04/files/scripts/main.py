#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健身计划定制助手
基于LLM的个性化健身计划生成技能
"""

import json
import sys

PROMPT_TEMPLATE = """请为我制定一份个性化健身计划：

身高：{height}cm
体重：{weight}kg
年龄：{age}
性别：{gender}
健身目标：{goal}
健身基础：{level}
每周可训练次数：{frequency}次
每次训练时间：{duration}分钟
训练场地：{location}
有无器械：{equipment}
其他需求：{extra}

请按照你的工作流程，生成完整的健身计划。"""


def build_prompt(params):
    defaults = {
        "height": "",
        "weight": "",
        "gender": "",
        "age": "",
        "goal": "减脂",
        "level": "零基础",
        "frequency": 3,
        "duration": 45,
        "location": "家",
        "equipment": "无",
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
    if not params.get("height"):
        return False, "缺少必填参数：height（身高）"
    if not params.get("weight"):
        return False, "缺少必填参数：weight（体重）"
    if not params.get("gender"):
        return False, "缺少必填参数：gender（性别）"
    if not params.get("age"):
        return False, "缺少必填参数：age（年龄）"
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
