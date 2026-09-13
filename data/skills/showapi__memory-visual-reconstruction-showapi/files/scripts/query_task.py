#!/usr/bin/env python3
"""
大记忆恢复术 - 异步任务查询接口（真实调用时使用）
调用方式: python scripts/query_task.py --task-id "任务ID"

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


def query_task(task_id: str) -> dict:
    """
    查询异步任务结果

    Args:
        task_id: 异步任务ID

    Returns:
        dict: 任务查询结果
    """
    # 1. 获取凭证：优先环境变量，无则运行时交互式询问
    # appKey 获取地址：https://www.showapi.com/console#/myApp
    app_key = os.environ.get("SHOWAPI_APP_KEY")
    if not app_key:
        print("未检测到环境变量 SHOWAPI_APP_KEY，请输入 AppKey：")
        print("（获取地址：https://www.showapi.com/console#/myApp）")
        app_key = getpass.getpass(prompt="AppKey: ")

    if not app_key.strip():
        raise ValueError("AppKey 不能为空，请重新运行并输入有效凭证。获取地址：https://www.showapi.com/console#/myApp")

    # 2. 构建请求
    url = f"https://route.showapi.com/flow/task/query/{task_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {app_key}"
    }

    # 3. 发起请求
    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status >= 400:
                raise Exception(f"HTTP请求失败: {response.status}")

            data = json.loads(response.read().decode("utf-8"))

            # 4. 业务错误处理
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
    parser = argparse.ArgumentParser(description="大记忆恢复术 - 异步任务查询")
    parser.add_argument("--task-id", "-t", required=True, help="异步任务ID")

    args = parser.parse_args()

    result = query_task(args.task_id)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()