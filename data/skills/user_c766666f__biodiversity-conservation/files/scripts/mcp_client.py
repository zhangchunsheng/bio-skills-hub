#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物多样性保护助手 - MCP 直调客户端（无需连接器配置）

通过标准 MCP streamable-http 协议直接调用山水自然保护中心
「生物多样性风险助手」服务。仅依赖 Python 标准库，无需 pip 安装。

凭证采用两级模式：
  - 公共 Key（内置，开箱即用）：基础功能兜底，由服务端限流控制
  - 私有 Key（联系山水自然保护中心申请）：更强功能与更高配额

用法:
  python mcp_client.py list
      # 列出全部可用工具

  python mcp_client.py call check_project_compliance --name "XX项目" --lng 116.4 --lat 39.9
  python mcp_client.py call check_project_compliance --name "XX项目" --address "北京市XX区XX路"
  python mcp_client.py call nature_disclosure_advice --name "XX项目" --lng 116.4 --lat 39.9
  python mcp_client.py call biodiversity_increment_suggestions --context "项目情况描述..."
  python mcp_client.py call get_biodiversity_expert_skill

API Key 来源（按优先级从高到低）:
  1. --token 命令行参数
  2. 环境变量 BIODIVERSITY_MCP_TOKEN
  3. 技能目录下 state/api_key.txt（私有 Key，首次使用后自动复用）
  4. 内置公共 Key（默认兜底，无需任何配置）

示例:
  python mcp_client.py call check_project_compliance --name "某化工厂" --token <你的私有Key>
"""

import json
import os
import sys
import urllib.error
import urllib.request

MCP_URL = "https://mid.shanshui.org/biodiversity-mcp/mcp"
PROTOCOL_VERSION = "2025-03-26"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 内置公共 Key：基础功能兜底（服务端已限流），零配置可用。
# 私有 Key 请联系山水自然保护中心申请。
PUBLIC_KEY = "W6WhOb0bWp8ArwESaolO4ho_fF7Hcc1-d7yP3koEAb0"

_rpc_id = 0
_using_public_key = False


def _key_file_path():
    """state/api_key.txt 位于技能目录的上一级（skills/<skill>/state/）。"""
    return os.path.normpath(os.path.join(SCRIPT_DIR, "..", "state", "api_key.txt"))


def get_token(cli_token=None):
    """按优先级取 API Key：参数 > 环境变量 > state/api_key.txt > 内置公共 Key。

    返回 (token, is_public)。is_public=True 表示当前使用内置公共 Key（基础功能模式）。
    """
    if cli_token:
        return cli_token.strip(), False
    env = os.environ.get("BIODIVERSITY_MCP_TOKEN", "").strip()
    if env:
        return env, False
    key_file = _key_file_path()
    if os.path.exists(key_file):
        tok = open(key_file, encoding="utf-8").read().strip()
        if tok:
            return tok, False
    return PUBLIC_KEY, True


def _fail_hint(status):
    """根据 HTTP 状态与当前 Key 类型给出可行动的提示。"""
    if status != 401:
        return ""
    if _using_public_key:
        return ("\nHINT: 当前使用内置公共 Key（基础功能模式）。认证失败可能是公共 Key 已被服务端"
                "更新、吊销或触发限流。请联系山水自然保护中心申请私有 Key。")
    return "\nHINT: 当前使用私有 Key。认证失败说明 Key 无效或已过期，请检查 state/api_key.txt 或重新申请。"


def _rpc(method, params, token, session_id=None):
    global _rpc_id
    _rpc_id += 1
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer %s" % token,
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    body = json.dumps({"jsonrpc": "2.0", "id": _rpc_id, "method": method, "params": params}).encode()
    req = urllib.request.Request(MCP_URL, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.headers.get("Mcp-Session-Id"), resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return None, e.code, e.read().decode(errors="replace")
    except Exception as e:  # 网络错误等
        return None, 0, "network error: %s" % e


def _parse(data):
    """兼容 SSE（text/event-stream）与纯 JSON 两种响应。"""
    text = data.lstrip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except Exception:
            return {"error": "json parse failed", "raw": data[:500]}
    last = None
    for line in text.splitlines():
        if line.startswith("data:"):
            try:
                last = json.loads(line[5:].strip())
            except Exception:
                pass
    return last


def _session(token):
    sid, status, data = _rpc("initialize",
                             {"protocolVersion": PROTOCOL_VERSION,
                              "capabilities": {},
                              "clientInfo": {"name": "biodiversity-skill", "version": "1.2.0"}},
                             token)
    if status != 200:
        msg = _parse(data)
        detail = json.dumps(msg, ensure_ascii=False)[:300] if msg else data[:300]
        print("ERROR: 服务初始化失败 (HTTP %s): %s%s" % (status, detail, _fail_hint(status)))
        sys.exit(1)
    _rpc("notifications/initialized", {}, token, sid)
    return sid


def cmd_list(token):
    sid = _session(token)
    sid, status, data = _rpc("tools/list", {}, token, sid)
    if status != 200:
        print("ERROR: 获取工具列表失败 (HTTP %s)%s" % (status, _fail_hint(status)))
        sys.exit(1)
    tl = _parse(data)
    tools = ((tl or {}).get("result") or {}).get("tools", [])
    print("可用工具（%d 个）：" % len(tools))
    for t in tools:
        name = t.get("name", "?")
        desc = (t.get("description") or "").replace("\n", " ")[:150]
        print("  - %s: %s" % (name, desc))
    if _using_public_key:
        print("\n[当前模式] 公共 Key（基础功能，已内置，无需配置）。")
        print("[功能受限] 如需更强功能与更高配额，请联系山水自然保护中心申请私有 Key，")
        print("           并告知 AI 保存到 state/api_key.txt 即可自动升级。")


def cmd_call(token, tool, params):
    sid = _session(token)
    sid, status, data = _rpc("tools/call", {"name": tool, "arguments": params}, token, sid)
    if status != 200:
        print("ERROR: 工具调用失败 (HTTP %s)%s" % (status, _fail_hint(status)))
        sys.exit(1)
    res = _parse(data)
    result = ((res or {}).get("result") or {})
    if result.get("isError"):
        print("TOOL_ERROR: %s" % json.dumps(result, ensure_ascii=False)[:800])
        sys.exit(1)
    for c in result.get("content", []):
        if c.get("type") == "text":
            print(c.get("text", ""))
        else:
            print(json.dumps(c, ensure_ascii=False))


def main():
    global _using_public_key
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0 if args else 2)

    cmd = args[0]
    token = None
    tool = None
    params = {}
    i = 1
    while i < len(args):
        a = args[i]
        if a == "--token" and i + 1 < len(args):
            token = args[i + 1]
            i += 2
        elif a.startswith("--") and i + 1 < len(args):
            params[a[2:]] = args[i + 1]
            i += 2
        elif tool is None:
            tool = a
            i += 1
        else:
            i += 1

    if cmd == "list":
        token, is_public = get_token(token)
        _using_public_key = is_public
        cmd_list(token)
    elif cmd == "call":
        if not tool:
            print("用法: python mcp_client.py call <tool> [--name X] [--lng X] [--lat X] [--address X] [--context X] [--token KEY]")
            sys.exit(2)
        token, is_public = get_token(token)
        _using_public_key = is_public
        cmd_call(token, tool, params)
    else:
        print("未知命令: %s（支持 list / call）" % cmd)
        sys.exit(2)


if __name__ == "__main__":
    main()
