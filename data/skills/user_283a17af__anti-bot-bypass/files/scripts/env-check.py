#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境自检脚本 —— 安装本 skill 后先跑一次，确认你的机器能跑通各层级。

用法:
    python scripts/env-check.py
    python scripts/env-check.py --verbose

输出: 红/黄/绿 三色中文报告，逐项告诉你「通过了什么 / 缺什么 / 怎么装」。
依赖: 仅标准库即可运行；curl_cffi 等可选依赖会自动探测，不影响自检本身。

为什么需要它: 评测反馈「没有自动化工具帮你验证配置是否正确」。本脚本就是那个工具——
装完 skill 第一步跑它，看到全绿再开始抓，避免中途因环境缺依赖而报错。
"""

import sys
import os
import json
import shutil
import socket
import importlib.util
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Windows 终端启用 ANSI 颜色（Win10+ 支持虚拟终端）
if os.name == "nt":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

G = "\033[32m"; Y = "\033[33m"; R = "\033[31m"; B = "\033[1m"; E = "\033[0m"


def ok(msg):
    print(f"  {G}✓{E} {msg}")


def warn(msg):
    print(f"  {Y}!{E} {msg}")


def bad(msg):
    print(f"  {R}×{E} {msg}")


def section(title):
    print(f"\n{B}== {title} =={E}")


def check_py():
    section("1. Python 版本")
    v = sys.version_info
    ver = f"{v.major}.{v.minor}.{v.micro}"
    if v.major == 3 and v.minor >= 8:
        ok(f"Python {ver}（满足 ≥ 3.8 要求）")
        return True
    bad(f"Python {ver} 太旧，建议升级到 3.8+")
    return False


def check_net():
    section("2. 网络连通性（能否联网发请求）")
    targets = [
        ("百度", "https://www.baidu.com"),
        ("B站 API", "https://api.bilibili.com/x/web-interface/wbi/index/top/feed/rcmd?web_location=333.1007"),
    ]
    all_ok = True
    for name, url in targets:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                if r.status == 200:
                    ok(f"{name} 可达（HTTP 200）")
                else:
                    warn(f"{name} 返回 {r.status}（状态码非 200，但网络通）")
        except Exception as e:
            msg = str(e).lower()
            if "certificate" in msg:
                bad(f"{name} 证书校验失败（若用抓包代理，可在探针加 --insecure）")
            elif "timed out" in msg or "timeout" in msg:
                bad(f"{name} 超时（网络慢或代理不稳）")
            else:
                bad(f"{name} 不可达：{e}")
            all_ok = False
    return all_ok


def check_opt(name, pipname, hint):
    section(f"3. 可选依赖：{name}")
    spec = importlib.util.find_spec(name)
    if spec:
        ok(f"{name} 已安装（可直接用对应层级能力）")
        return True
    warn(f"{name} 未安装 —— {hint}")
    print(f"      安装: python -m pip install {pipname} -i https://pypi.tuna.tsinghua.edu.cn/simple")
    return False


def find_browsers():
    found = []
    candidates = []
    if os.name == "nt":
        pf = os.environ.get("ProgramFiles", "C:\\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        candidates = [
            os.path.join(pf, "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(pf86, "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(pf, "Microsoft\\Edge\\Application\\msedge.exe"),
            os.path.join(pf86, "Microsoft\\Edge\\Application\\msedge.exe"),
        ]
    for b in ("chrome", "msedge", "chromium", "google-chrome", "chromium-browser"):
        p = shutil.which(b)
        if p:
            candidates.append(p)
    seen = set()
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        if os.path.isfile(c):
            found.append(c)
    return found


def check_browser():
    section("4. 本机浏览器（L5 CDP 复用需要）")
    found = find_browsers()
    if found:
        for f in found:
            ok(f"找到: {f}")
        print("      L5 可直接用 web-access skill，或按 cdp-reuse.md 启动 CDP")
        return True
    warn("未发现 Chrome/Edge（L5 本机接管需要）。可选：装 Chrome，或用 L3 的 patchright 自带 chromium")
    return False


def check_cdp_port():
    section("5. CDP 远程调试端口（若已开调试模式）")
    up = []
    for port in (9222, 9223):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", port))
            up.append(port)
        except Exception:
            pass
        finally:
            s.close()
    if up:
        ok(f"检测到 CDP 端口开放: {up}（可直接连接复用）")
    else:
        warn("未检测到开放的 CDP 端口（正常，未启动调试模式时）。需要时按 cdp-reuse.md 开启")


def main():
    print(f"\n{B}==== 反爬 skill 环境自检 ===={E}\n")
    py_ok = check_py()
    net_ok = check_net()
    curl_ok = check_opt("curl_cffi", "curl_cffi", "L1 TLS 伪装核心，强烈建议装")
    check_opt("patchright", "patchright", "L3 浏览器伪装（Playwright 去自动化）")
    check_opt("camoufox", "camoufox", "L4 火狐指纹伪装")
    check_opt("nodriver", "nodriver", "L3 无驱动 Chrome 控制")
    check_opt("fonttools", "fonttools", "L7 字体反爬建映射表")
    browser_ok = check_browser()
    check_cdp_port()

    print(f"\n{B}==== 结论 ===={E}\n")
    if py_ok and net_ok:
        ok("基础环境就绪：探针 + 网络可用，最低成本方案（L0/L1）立即可用")
    else:
        bad("基础环境有问题，先解决上面标 × 的项再继续")
    if not curl_ok:
        print("  → 想跑 L1 伪装：装 curl_cffi（装好后探针会自动启用 TLS 对照实验）")
    if not browser_ok:
        print("  → 想跑 L5 接管：装 Chrome，或用 patchright 自带 chromium")
    print("\n  下一步：python scripts/probe.py https://目标站   （开始判层）\n")


if __name__ == "__main__":
    main()
