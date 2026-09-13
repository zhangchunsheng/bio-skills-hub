#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FinTrust Skill Hub API 引导与校验模块。

本 skill 由星财富（复星财富）发布，使用需 FinTrust Skill Hub 的 API Key。

- 本模块被 import 时自动加载 ~/.biopharma/.env（密钥不落盘进仓库）
- 数据模块（biopharma_data / biopharma_tracker / cde_priority_collector /
  nmpa_clinical_trials）在模块级调用 require_api_key()：
  未配置 Key 时，无论 CLI 运行还是 import 调用一律拒绝（exit code 2）
"""

import os
import sys

REGISTER_URL = "https://fintrustskill.com/landing"
API_KEY_ENV = "FINTRUST_API_KEY"


def _load_env_file() -> None:
    """加载 ~/.biopharma/.env（已存在的环境变量不覆盖）。"""
    env_file = os.path.join(os.path.expanduser("~"), ".biopharma", ".env")
    if not os.path.isfile(env_file):
        return
    try:
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass  # .env 读取失败不阻断，环境变量仍可直接注入


_load_env_file()


def has_api_key() -> bool:
    return bool(os.environ.get(API_KEY_ENV, "").strip())


def print_onboard_hint() -> None:
    """未配置 API Key 时，在 stderr 打印申请引导。"""
    if has_api_key():
        return
    print(
        "\n" + "=" * 62
        + "\n[FinTrust Skill Hub] 尚未配置 API Key，已拒绝执行"
        + "\n  本 skill 需配合 FinTrust Skill Hub 的 API Key 使用："
        + f"\n    1. 前往 {REGISTER_URL} 注册账号"
        + "\n    2. 申请 API Key"
        + f"\n    3. 配置环境变量：export {API_KEY_ENV}=你的Key"
        + "\n       （或写入 ~/.biopharma/.env，本 skill 会自动加载）"
        + "\n  配置后此提示不再出现。"
        + "\n" + "=" * 62 + "\n",
        file=sys.stderr,
    )


def require_api_key() -> None:
    """硬校验：未配置 API Key 时打印申请引导并拒绝运行（exit code 2）。

    数据模块在模块级调用本函数——CLI 运行与 import 库式调用均被拦截。
    """
    if has_api_key():
        return
    print_onboard_hint()
    sys.exit(2)
