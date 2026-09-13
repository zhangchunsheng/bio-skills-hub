#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按 task_id 从服务器取回已生成的图片（用于服务端已生成、客户端被切断丢的任务）。
用法: python fetch_task.py <task_id> [task_id2 ...]
协议：经网关 POST /app/ai/query {taskId} → status SUCCESS/FAILED + results[].url
版权：奎可智能体出品 https://quakowork.com/
"""
import json
import os
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

KEY_FILE = Path(__file__).resolve().parent.parent / "key.txt"
KEY_HELP_URL = "https://quakowork.com/console/api-key?source=workbuddy"
GATEWAY_BASE_URL = "http://cwapi.xiemoai.com/v1/gateway/proxy"
QUERY_URL = f"{GATEWAY_BASE_URL}/app/ai/query"
# 输出目录平台自适应：Windows 有 D 盘用 D:\generate_images，否则(macOS/Linux) ~/generate_images
OUT_DIR = r"D:\generate_images" if os.path.exists("D:\\") else os.path.join(os.path.expanduser("~"), "generate_images")


def load_key() -> str:
    """读技能根 key.txt 首个非空行，去引号/空白。"""
    try:
        with open(KEY_FILE, "r", encoding="utf-8-sig") as f:
            for line in f:
                s = line.strip().strip('"').strip("'").strip()
                if s:
                    return s
    except FileNotFoundError:
        pass
    print(f"未配置 API Key：请访问 {KEY_HELP_URL} 注册并订阅/充值点数获取，交给助手写入 {KEY_FILE}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("用法: python fetch_task.py <task_id> [task_id2 ...]", file=sys.stderr)
        sys.exit(1)
    key = load_key()
    headers = {"jh-api-key": key, "Authorization": "Bearer {{apiKey}}", "Content-Type": "application/json"}
    os.makedirs(OUT_DIR, exist_ok=True)
    for tid in sys.argv[1:]:
        try:
            r = requests.post(QUERY_URL, headers=headers, json={"taskId": tid}, timeout=30)
            j = r.json()
        except Exception as e:
            print(f"[{tid}] 查询异常: {e}", file=sys.stderr)
            continue
        status = j.get("status", "UNKNOWN")
        results = j.get("results") or []
        print(f"[{tid}] status={status} results={len(results)}", file=sys.stderr)
        if status != "SUCCESS":
            print(f"[{tid}] 未成功: errorCode={j.get('errorCode')} {j.get('errorMessage','')}", file=sys.stderr)
            continue
        for i, it in enumerate(results, 1):
            url = it.get("url") or it.get("outputUrl")
            if not url:
                print(f"[{tid}] item{i} 无 url: {list(it.keys())}", file=sys.stderr)
                continue
            try:
                ir = requests.get(url, timeout=300)
                out = os.path.join(OUT_DIR, f"fetched_{tid}_{i}.png")
                with open(out, "wb") as f:
                    f.write(ir.content)
                print(f"[{tid}] OK 已取回 -> {out} ({len(ir.content)//1024} KB)", file=sys.stderr)
            except Exception as e:
                print(f"[{tid}] item{i} 下载失败: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
