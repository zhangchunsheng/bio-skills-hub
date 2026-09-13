#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医疗科普文案生成器
基于LLM的医疗科普文案生成技能
"""

import json
import sys

PROMPT_TEMPLATE = """请生成一篇医疗科普文章：

科普主题：{topic}
目标平台：{platform}
目标读者：{target_audience}
字数要求：{word_count}
其他要求：{extra_requirements}

请按照你的工作流程，生成完整的科普文章。"""


def build_prompt(params):
    defaults = {
        "topic": "",
        "platform": "公众号",
        "target_audience": "普通大众",
        "word_count": "适中",
        "extra_requirements": "",
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
        return False, "缺少必填参数：topic（科普主题）"
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
