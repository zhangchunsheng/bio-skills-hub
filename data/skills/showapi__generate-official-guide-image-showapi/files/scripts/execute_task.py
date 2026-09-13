#!/usr/bin/env python3
"""
基于办事目标生成导引图 - 执行任务接口（真实调用时使用）
调用方式: python scripts/execute_task.py --user-goal "新生儿医保参保登记"

仅使用 Python 标准库，无需安装第三方依赖。
appKey 获取：访问 https://www.showapi.com 注册账号，
登录后进入 https://www.showapi.com/console#/myApp 获取 appKey。
"""

import argparse
import json
import os
import getpass
import urllib.request
import urllib.error
import urllib.parse


def execute_task(
    user_goal: str,
    visual_style: str = "莫兰迪扁平插画",
    aspect_ratio: str = "1:1",
    mode: str = "sync"
) -> dict:
    """
    执行导引图生成任务

    Args:
        user_goal: 用户具体的办事目标或事项名称（必填）
        visual_style: 导引图视觉风格，默认莫兰迪扁平插画
        aspect_ratio: 创作图片比例，可选 1:1, 3:4, 4:3, 16:9, 9:16
        mode: 调用模式 async 或 sync

    Returns:
        dict: 包含 showapi_res_body、showapi_res_code 等字段的响应
    """
    # 1. 获取凭证：优先环境变量，无则交互式输入
    # appKey 获取地址：https://www.showapi.com/console#/myApp
    app_key = os.environ.get("SHOWAPI_APP_KEY")
    if not app_key:
        print("未检测到环境变量 SHOWAPI_APP_KEY，请输入 AppKey：")
        print("（获取地址：https://www.showapi.com/console#/myApp）")
        app_key = getpass.getpass(prompt="AppKey: ")

    if not app_key.strip():
        raise ValueError("AppKey 不能为空，请重新运行并输入有效凭证。获取地址：https://www.showapi.com/console#/myApp")

    # 2. 构建请求
    url = "https://route.showapi.com/flow/execute/6a85628e3c51f2e31100e0a2"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {app_key}"
    }

    # 构建请求体
    payload = {
        "user_goal": user_goal,
        "visual_style": visual_style,
        "aspect_ratio": aspect_ratio
    }

    # 3. 构建查询参数
    query_params = urllib.parse.urlencode({"mode": mode})
    full_url = f"{url}?{query_params}"

    # 4. 发起请求
    req = urllib.request.Request(
        full_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status >= 400:
                raise Exception(f"HTTP请求失败: {response.status}")

            data = json.loads(response.read().decode("utf-8"))

            # 5. 业务错误处理
            if data.get("showapi_res_code", -1) != 0:
                error_msg = data.get("showapi_res_error", "未知错误")
                raise Exception(f"API错误: {error_msg}")

            return data

    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP请求失败: {e.code}, {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"请求失败: {str(e.reason)}")
    except Exception as e:
        raise Exception(f"请求异常: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="基于办事目标生成导引图 - 执行任务")
    parser.add_argument("--user-goal", "-g", required=True, help="用户具体的办事目标或事项名称")
    parser.add_argument("--visual-style", "-s", default="莫兰迪扁平插画", help="导引图视觉风格")
    parser.add_argument("--aspect-ratio", "-a", default="1:1", choices=["1:1", "3:4", "4:3", "16:9", "9:16"], help="创作图片比例")
    parser.add_argument("--async", dest="mode", action="store_const", const="async", default="sync", help="使用异步模式")

    args = parser.parse_args()

    result = execute_task(
        user_goal=args.user_goal,
        visual_style=args.visual_style,
        aspect_ratio=args.aspect_ratio,
        mode=args.mode
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()