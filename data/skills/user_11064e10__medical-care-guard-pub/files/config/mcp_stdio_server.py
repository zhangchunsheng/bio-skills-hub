# -*- coding: utf-8 -*-
# Copyright (c) Joyxj2devs Team. All rights reserved.
"""stdio 形态的 MCP 服务器：把统一知识服务工具暴露给宿主 Agent。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mcp_client  # noqa: E402

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "medical-care-guard", "version": "1.0.0"}

TOOLS = [
    {
        "name": "life_policy_ask",
        "description": "失业/劳动政策问答检索，返回带出处的知识片段",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "board": {"type": "string", "default": "unemployment"},
                "city": {"type": "string"},
                "top_k": {"type": "integer", "default": 3},
            },
            "required": ["question"],
        },
    },
    {
        "name": "benefit_check",
        "description": "失业金/失业补助金等待遇资格达标判定",
        "inputSchema": {
            "type": "object",
            "properties": {
                "board": {"type": "string", "default": "unemployment"},
                "profile": {"type": "object"},
            },
            "required": ["profile"],
        },
    },
    {
        "name": "rights_calculate",
        "description": "经济补偿N/N+1/2N、未签合同二倍工资、失业金月数测算",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scene": {
                    "type": "string",
                    "enum": ["severance", "double_wage", "ui_months"],
                },
                "params": {"type": "object"},
            },
            "required": ["scene", "params"],
        },
    },
    {
        "name": "risk_check",
        "description": "三级风险闸门体检，返回 L0/L1/L2 风险码与处置建议",
        "inputSchema": {
            "type": "object",
            "properties": {
                "board": {"type": "string", "default": "unemployment"},
                "profile": {"type": "object"},
            },
            "required": ["profile"],
        },
    },
    {
        "name": "timeline_plan",
        "description": "人生事件时间轴规划，输出各节点截止日期与动作",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event": {"type": "string"},
                "start_date": {"type": "string"},
                "city": {"type": "string"},
            },
            "required": ["event", "start_date"],
        },
    },
    {
        "name": "kb_list",
        "description": "列出知识库条目清单",
        "inputSchema": {
            "type": "object",
            "properties": {"board": {"type": "string"}},
        },
    },
    {
        "name": "route_query",
        "description": "按问题路由到最合适的技能包",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_n": {"type": "integer", "default": 3},
            },
            "required": ["query"],
        },
    },
]


def _reply(rid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": rid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _handle(req: dict) -> None:
    method = req.get("method")
    rid = req.get("id")
    params = req.get("params") or {}

    if method == "initialize":
        _reply(rid, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })
    elif method == "tools/list":
        _reply(rid, {"tools": TOOLS})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        if name not in {t["name"] for t in TOOLS}:
            _reply(rid, error={"code": -32601, "message": f"未知工具: {name}"})
            return
        try:
            data = mcp_client.call(name, **args)
        except Exception as exc:  # noqa: BLE001
            _reply(rid, error={"code": -32000, "message": str(exc)})
            return
        _reply(rid, {
            "content": [
                {"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}
            ]
        })
    elif rid is not None:
        _reply(rid, error={"code": -32601, "message": f"未知方法: {method}"})


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        _handle(req)


if __name__ == "__main__":
    main()
