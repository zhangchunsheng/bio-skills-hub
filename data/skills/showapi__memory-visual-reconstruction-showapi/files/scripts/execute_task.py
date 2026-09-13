#!/usr/bin/env python3
"""
大记忆恢复术 - 执行任务接口（真实调用时使用）
调用方式: python scripts/execute_task.py --prompt "记忆碎片描述"

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
    prompt: str,
    aspect_ratio: str = "1:1",
    reference_image: list = None,
    mode: str = "sync"
) -> dict:
    """
    执行大记忆恢复术任务，异步提交记忆重构与生图请求

    Args:
        prompt: 用户记忆碎片描述，可包含人物、地点、时代、事件片段、感官体验、情绪感受等自然语言描述（必填）
        aspect_ratio: 图片宽高比例，可选值：1:1、3:4、4:3、16:9、9:16
        reference_image: 用户提供的旧照片、老物件照片、家庭图片URL列表，用于辅助理解记忆环境和视觉特征
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
    url = "https://route.showapi.com/flow/execute/6a72ded53c51f2ec2101b557"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {app_key}"
    }

    # 构建请求体
    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio
    }

    # 可选参数
    if reference_image:
        payload["reference_image"] = reference_image

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
    parser = argparse.ArgumentParser(description="大记忆恢复术 - 执行任务")
    parser.add_argument("--prompt", "-p", required=True, help="用户记忆碎片描述，可包含人物、地点、时代、感官体验等")
    parser.add_argument("--aspect-ratio", "-a", default="1:1", choices=["1:1", "3:4", "4:3", "16:9", "9:16"], help="图片宽高比例，默认1:1")
    parser.add_argument("--reference-image", "-r", nargs="*", default=[], help="参考图片URL列表，用于辅助理解记忆环境和视觉特征")
    parser.add_argument("--async", dest="mode", action="store_const", const="async", default="sync", help="使用异步模式")

    args = parser.parse_args()

    result = execute_task(
        prompt=args.prompt,
        aspect_ratio=args.aspect_ratio,
        reference_image=args.reference_image if args.reference_image else None,
        mode=args.mode
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()