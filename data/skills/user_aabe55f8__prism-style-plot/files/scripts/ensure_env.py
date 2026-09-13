#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
ensure_env.py — 可移植、幂等的 Python 绘图环境引导器（prism-style-plot 技能用）。

为什么需要它（踩坑记录，分享时务必保留）：
  受管理 Python 的绘图依赖（matplotlib/scipy/numpy/pandas/seaborn）装在**受管理 venv**
  里，而不在基础解释器上。如果用基础解释器去 `import matplotlib` 做"装没装"的判定，
  会报 ModuleNotFoundError，从而**误判为未安装、每次都重装**。本脚本只检查 venv 自己的
  解释器；首次装好后在 venv 内写入标记文件，之后运行仅做文件系统检查（秒回，不再全量
  import），并返回 venv 解释器绝对路径，供后续统一调用。传递 --force 可强制重新探针
  （用于 venv 被手动破坏后的恢复）。

可移植性：
  - venv 路径**不硬编码用户名**，而是从当前解释器 `sys.executable` 向上推导受管理结构
    `<root>/binaries/python/versions/<ver>/python[.exe]` → venv 落在
    `<root>/binaries/python/envs/default`。换机器/换用户名都适用。
  - 跨平台：Windows 用 `Scripts\python.exe`，POSIX 用 `bin/python`。
  - 若当前解释器已经能 import 全部依赖，直接返回它自己（无需 venv）。
  - 若不在受管理结构内，兜底放到用户级 `~/.workbuddy/python_envs/prism_plot`。

用法（在任何绘图脚本之前运行一次）：
  PY=$(python scripts/ensure_env.py)   # 打印 venv 解释器路径
  $PY your_plot.py                     # 之后一律用 $PY 运行
"""
import os
import subprocess
import sys

# 注意：lifelines 硬依赖 pandas<3.0，故把 pandas 一并钉在 <3.0，
# 避免全新 bootstrap 时 pip 拉到 pandas 3.x 与 lifelines 冲突、整批安装中止。
REQUIRED = ["matplotlib", "scipy", "numpy", "pandas<3.0", "seaborn",
            "statsmodels", "lifelines"]
# statsmodels 供 build_stats_report("twoway") 的 Two-way ANOVA；
# lifelines 供 Cox 比例风险回归（cox_regression / build_stats_report("survival", add_cox=True)），
# 与 REQUIRED 一同在 bootstrap 安装；另 prism_theme 在 Cox 路径按需惰性补装，兼容旧 venv。


def _target_venv_python():
    """从当前解释器推导受管理 venv 解释器路径（跨平台、跨用户名）。"""
    exe = sys.executable
    parts = exe.split(os.sep)
    # 寻找受管理结构：.../binaries/python/versions/<ver>/python[.exe]
    for i in range(len(parts) - 2):
        if parts[i] == "binaries" and parts[i + 1] == "python" and parts[i + 2] == "versions":
            base = os.sep.join(parts[: i + 2])  # <root>/binaries/python
            venv_dir = os.path.join(base, "envs", "default")
            sub = "Scripts" if os.name == "nt" else "bin"
            name = "python.exe" if os.name == "nt" else "python"
            return os.path.join(venv_dir, sub, name)
    # 兜底：不在受管理结构内时，放到用户级目录（跨机器可移植）
    venv_dir = os.path.expanduser(os.path.join("~", ".workbuddy", "python_envs", "prism_plot"))
    sub = "Scripts" if os.name == "nt" else "bin"
    name = "python.exe" if os.name == "nt" else "python"
    return os.path.join(venv_dir, sub, name)


def _can_import_all(py):
    code = (
        "import importlib;mods=" + repr(REQUIRED) + ";"
        "[importlib.import_module(m) for m in mods];print('OK')"
    )
    try:
        r = subprocess.run([py, "-c", code], capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and "OK" in r.stdout
    except Exception:
        return False


def _venv_root(py):
    # Windows: py=.../envs/default/Scripts/python.exe -> root=.../envs/default
    # POSIX:   py=.../envs/default/bin/python       -> root=.../envs/default
    if os.name == "nt":
        return os.path.dirname(os.path.dirname(py))
    return os.path.dirname(py)


def _marker_path(py):
    """标记文件写在 venv 根目录内（技能目录之外，不随技能上传，跨机器不串味）。"""
    return os.path.join(_venv_root(py), "_prism_deps_ok")


def _marker_valid(py):
    """venv 解释器存在且标记内容与路径一致 → 视为依赖就绪（跳过全量探针）。"""
    mp = _marker_path(py)
    if not os.path.exists(mp) or not os.path.exists(py):
        return False
    try:
        with open(mp, "r", encoding="utf-8") as f:
            return f.read().strip() == py
    except Exception:
        return False


def _write_marker(py):
    """记下已验证可用的 venv 解释器路径；写入失败不影响主流程。"""
    try:
        mp = _marker_path(py)
        os.makedirs(_venv_root(py), exist_ok=True)
        with open(mp, "w", encoding="utf-8") as f:
            f.write(py)
    except Exception:
        pass


def main():
    force = "--force" in sys.argv[1:]

    # 0) 标记缓存：venv 已就绪且标记有效则跳过昂贵的全量 import 探针（秒回）。
    #    标记写在 venv 目录内（技能目录之外，不随技能上传，跨机器不串味）。
    #    --force 可强制重新探针（用于 venv 被手动破坏后的恢复）。
    py = _target_venv_python()
    if not force and _marker_valid(py):
        print(py)
        return 0

    # 1) 当前解释器已经能 import 全部依赖？直接返回它自己（含"已在正确 venv 内"的情况）
    if _can_import_all(sys.executable):
        print(sys.executable)
        return 0

    # 2) 推导 venv 解释器，已就位则秒退（关键：用 venv 自己的解释器判定，避免误装）
    if _can_import_all(py):
        _write_marker(py)
        print(py)
        return 0

    # 3) 需要创建或补全 venv
    venv_root = _venv_root(py)
    if not os.path.exists(py):
        print(f"[ensure_env] 创建 venv: {venv_root}", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "venv", venv_root], check=True)
    else:
        print("[ensure_env] venv 已存在但缺包，执行补全安装…", file=sys.stderr)

    sub = "Scripts" if os.name == "nt" else "bin"
    pip = os.path.join(venv_root, sub, "pip.exe" if os.name == "nt" else "pip")
    subprocess.run([pip, "install", "--quiet", *REQUIRED], check=True)

    # 4) 再次确认，给出明确状态
    if _can_import_all(py):
        print(f"[ensure_env] 依赖就绪", file=sys.stderr)
        _write_marker(py)
    else:
        print("[ensure_env] 警告：安装后检测仍失败，请检查网络/镜像源", file=sys.stderr)
    print(py)
    return 0


if __name__ == "__main__":
    sys.exit(main())
