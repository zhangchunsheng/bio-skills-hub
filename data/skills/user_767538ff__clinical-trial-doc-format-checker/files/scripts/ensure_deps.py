#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ensure_deps.py — 确保 generate_docx.py 所需依赖已安装到隔离 venv。

策略：
1. 检查默认 venv 是否存在；不存在则创建。
2. 检查 python-docx 是否已安装；未安装则安装到 venv。
3. 输出 venv 的 python 解释器绝对路径，供调用方使用。

退出码：
    0 成功
    1 创建 venv 失败
    2 安装 python-docx 失败
"""

import os
import subprocess
import sys

PY_BASE = r"C:\Users\qqq\.workbuddy\binaries\python\versions\3.13.12\python.exe"
VENV_DIR = r"C:\Users\qqq\.workbuddy\binaries\python\envs\default"
VENV_PY = os.path.join(VENV_DIR, "Scripts", "python.exe")
VENV_PIP = os.path.join(VENV_DIR, "Scripts", "pip.exe")


def run(cmd, check=True):
    print("[run]", " ".join(cmd))
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def main():
    # 1. 创建 venv
    if not os.path.exists(VENV_PY):
        if not os.path.exists(PY_BASE):
            sys.stderr.write(f"[ensure_deps] 找不到基础 Python：{PY_BASE}\n")
            sys.exit(1)
        try:
            run([PY_BASE, "-m", "venv", VENV_DIR])
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"[ensure_deps] 创建 venv 失败：{e.stderr}\n")
            sys.exit(1)

    # 2. 检查 python-docx
    check = subprocess.run(
        [VENV_PY, "-c", "import docx; print(docx.__version__)"],
        capture_output=True, text=True
    )
    if check.returncode != 0:
        try:
            run([VENV_PY, "-m", "pip", "install", "--upgrade", "python-docx"])
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"[ensure_deps] 安装 python-docx 失败：{e.stderr}\n")
            sys.exit(2)

    # 3. 复核
    verify = subprocess.run(
        [VENV_PY, "-c", "import docx; print(docx.__version__)"],
        capture_output=True, text=True
    )
    if verify.returncode != 0:
        sys.stderr.write("[ensure_deps] 安装后仍无法导入 python-docx\n")
        sys.exit(2)

    print(VENV_PY)


if __name__ == "__main__":
    main()
