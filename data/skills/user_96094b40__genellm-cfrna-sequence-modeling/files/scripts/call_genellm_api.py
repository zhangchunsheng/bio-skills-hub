"""调用 GeneLLM 付费推理端点。

用法：
    python call_genellm_api.py --reads ACGT... TTTT... --n-kmers 1000

环境变量：
    SKILL_API_BASE   计费 API 地址（默认 http://127.0.0.1:8899）
    SKILL_API_KEY    用户的 API Key（sk_live_ 前缀）
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE = os.environ.get("SKILL_API_BASE", "http://127.0.0.1:8899")
KEY = os.environ.get("SKILL_API_KEY", "")


def call_genellm(reads, n_kmers=1000, api_key=None):
    key = api_key or KEY
    if not key:
        print("错误：未设置 SKILL_API_KEY。请先获取 API Key 并设置环境变量。", file=sys.stderr)
        sys.exit(1)
    body = {"reads": reads, "n_kmers": n_kmers}
    req = urllib.request.Request(
        f"{BASE}/infer/genellm",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Api-Key": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        if e.code == 402:
            print("余额不足，请先充值（联系服务提供方）。", file=sys.stderr)
        elif e.code == 401:
            print("API Key 无效或已禁用。", file=sys.stderr)
        elif e.code == 429:
            print("调用过于频繁，请稍后再试。", file=sys.stderr)
        else:
            print(f"HTTP {e.code}: {detail}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="GeneLLM 付费推理")
    p.add_argument("--reads", nargs="+", required=True, help="测序 reads 序列列表")
    p.add_argument("--n-kmers", type=int, default=1000)
    args = p.parse_args()
    result = call_genellm(args.reads, args.n_kmers)
    print(json.dumps(result, ensure_ascii=False, indent=2))
