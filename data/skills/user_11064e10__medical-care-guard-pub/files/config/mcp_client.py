# -*- coding: utf-8 -*-
# Copyright (c) Joyxj2devs Team. All rights reserved.
"""个人业务全能知识库 - 统一知识服务客户端（云端 MCP）。

调用方式：仅调用云端 MCP 服务（JSON-RPC /mcp 端点）。
  - 云端为权威数据源，内容随服务端实时更新；
  - 用户端技能包不含本地服务，无法本地直连；离线场景请使用
    offline_workflows/ 下的离线流程手册。

云端端点默认：https://mcp.aitaxs.top/api/services/personal-life-knowledge/mcp
可用环境变量 PLK_MCP_URL 覆盖。
云端 /mcp 端点面向客户端开放 tools/call，无需本地注册即可调用已暴露的服务工具。
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

_CLIENT_ID = "medical-care-guard"
_SERVICE = "personal-life-knowledge"
_REMOTE_MCP = os.environ.get(
    "PLK_MCP_URL",
    "https://mcp.aitaxs.top/api/services/personal-life-knowledge/mcp",
)
_TIMEOUT = 25
_RPC_ID = 1


# --------------------------------------------------------------------------- #
# 云端通道（MCP JSON-RPC，端点 .../mcp）
# --------------------------------------------------------------------------- #
def _rpc(tool: str, args: dict) -> dict | None:
    """向云端 /mcp 端点发起 tools/call，返回工具结果字典；失败返回 None。"""
    payload = {
        "jsonrpc": "2.0",
        "id": _RPC_ID,
        "method": "tools/call",
        "params": {"name": tool, "arguments": args or {}},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(_REMOTE_MCP, data=data, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("X-Client-Id", _CLIENT_ID)
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None
    if isinstance(body, dict) and "error" in body:
        return None
    result = body.get("result") if isinstance(body, dict) else None
    return result if isinstance(result, dict) else None


# --------------------------------------------------------------------------- #
# 对外 API
# --------------------------------------------------------------------------- #
def call(tool: str, **args):
    """调用云端知识服务工具。失败返回统一错误字典。"""
    res = _rpc(tool, args)
    if res is not None:
        return res
    return {
        "ok": False,
        "error": "云端知识服务暂不可用或该工具未开放，请稍后重试或使用 offline_workflows/ 下的离线流程手册。",
    }


def life_policy_ask(question: str, board: str = "unemployment", city: str = "", top_k: int = 3):
    return call("life_policy_ask", question=question, board=board, city=city, top_k=top_k)


def benefit_check(profile: dict, board: str = "unemployment"):
    return call("benefit_check", board=board, profile=profile)


def rights_calculate(scene: str, params: dict):
    return call("rights_calculate", scene=scene, params=params)


def risk_check(profile: dict, board: str = "unemployment"):
    return call("risk_check", board=board, profile=profile)


def timeline_plan(event: str, start_date: str, city: str = ""):
    return call("timeline_plan", event=event, start_date=start_date, city=city)


def city_params(city: str, fields: list | None = None):
    return call("city_params", city=city, fields=fields or [])


def contract_scan(contract_text: str, mask: bool = True):
    return call("contract_scan", contract_text=contract_text, mask=mask)


def route_query(query: str, top_n: int = 3):
    return call("route_query", query=query, top_n=top_n)


def kb_list(board: str = ""):
    # kb_list 为服务端内部工具，云端未暴露；保留 API 以返回明确错误而非崩溃。
    return call("kb_list", board=board)


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "公司让我签自愿离职书能签吗"
    print(json.dumps(life_policy_ask(q), ensure_ascii=False, indent=2))
