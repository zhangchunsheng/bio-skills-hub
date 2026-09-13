#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商详情页文案生成器
基于LLM的电商详情页文案生成技能
"""

import json
import sys

PROMPT_TEMPLATE = """请为以下产品生成电商详情页文案：

产品名称：{product_name}
产品特点：{features}
目标人群：{target_audience}
价格区间：{price_range}
其他信息：{extra_info}

请按照你的工作流程，生成完整的详情页文案。"""


def build_prompt(params):
    defaults = {
        "product_name": "",
        "features": "",
        "target_audience": "通用",
        "price_range": "",
        "extra_info": "",
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
    if not params.get("product_name"):
        return False, "缺少必填参数：product_name（产品名称）"
    if not params.get("features"):
        return False, "缺少必填参数：features（产品特点/卖点）"
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
