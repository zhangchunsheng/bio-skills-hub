#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
registry_cli.py — 仿制药调研「自我成长」本地知识库引擎
=====================================================
维护 data/registry.json（持久累积）。每次查询自动沉淀条目、超期自动标 STALE，
随使用自我成长。所有判定确定性、无第三方依赖。

桶（--type 取值，动态取自 registry.json 顶层键，除 meta）：
  products      品种档案：原研/参比RLD/国内上市申报/规格剂型/PLD
  patents       专利：化合物/制剂/工艺/用途、到期、PIV挑战、规避、首访首仿
  be_registry   一致性评价/参比制剂目录/BE（局部制剂BE豁免与质量一致替代证据）
  market        市场格局/销量/集采/份额/价格
  ocular_otic   眼科/耳科仿制专项（滴眼剂无防腐单剂量、眼用混悬/凝胶BE替代、耳科局部仿制）

命令：
  init                      创建空库（若缺失）
  query --name X --type T   查条目；输出 JSON：{status:"FRESH|STALE|NOT_FOUND", entry:{...}}
  add  --json '{...}'       新增/覆盖条目（必须含 type 与 name；last_checked 自动置今天）
  list --type T             列出某类所有 key + last_checked + 新鲜度
  stale                     列出所有超期(>freshness_months)条目
  stats                     输出条目计数与总体新鲜度
"""
import argparse
import json
import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "registry.json")
FRESH_DAYS = 180  # 6 个月


def _today():
    return date.today().isoformat()


def _load():
    if not os.path.exists(DB):
        return {"meta": {"last_full_refresh": _today(), "version": 1,
                         "freshness_months": 6}}
    with open(DB, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(db):
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def _buckets(db):
    return [k for k in db.keys() if k != "meta"]


def _age_days(s):
    try:
        d = date.fromisoformat(s)
        return (date.today() - d).days
    except Exception:
        return 99999


def cmd_init():
    if os.path.exists(DB):
        print("EXISTS")
        return
    _save(_load())
    print("INIT_OK")


def cmd_query(name, t):
    db = _load()
    b = db.setdefault(t, {})
    if name not in b:
        print(json.dumps({"status": "NOT_FOUND", "entry": None}, ensure_ascii=False))
        return
    e = b[name]
    age = _age_days(e.get("last_checked", ""))
    status = "FRESH" if age <= FRESH_DAYS else "STALE"
    print(json.dumps({"status": status, "entry": e}, ensure_ascii=False))


def cmd_add(payload):
    db = _load()
    t = payload.get("type")
    name = payload.get("name")
    if not t or not name:
        print("ERROR: payload 必须含 type 与 name")
        sys.exit(2)
    if t not in _buckets(db):
        print("ERROR: type 必须是", _buckets(db))
        sys.exit(2)
    b = db.setdefault(t, {})
    payload["last_checked"] = _today()
    b[name] = payload
    _save(db)
    print("ADDED_OK", t, name, _today())


def cmd_list(t):
    db = _load()
    b = db.setdefault(t, {})
    for k, v in sorted(b.items()):
        age = _age_days(v.get("last_checked", ""))
        flag = "OK" if age <= FRESH_DAYS else "STALE"
        print(f"[{flag}] {k}  last_checked={v.get('last_checked','-')}")


def cmd_stale():
    db = _load()
    for t in _buckets(db):
        b = db.get(t, {})
        for k, v in b.items():
            if _age_days(v.get("last_checked", "")) > FRESH_DAYS:
                print(f"[{t}] {k}  last_checked={v.get('last_checked','-')}")


def cmd_stats():
    db = _load()
    out = {"last_full_refresh": db.get("meta", {}).get("last_full_refresh")}
    for t in _buckets(db):
        b = db.get(t, {})
        stale = sum(1 for v in b.values() if _age_days(v.get("last_checked", "")) > FRESH_DAYS)
        out[t] = len(b)
        out["stale_" + t] = stale
    print(json.dumps(out, ensure_ascii=False))


def main():
    db = _load()
    buckets = _buckets(db) or ["products", "patents", "be_registry", "market", "ocular_otic"]
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    q = sub.add_parser("query"); q.add_argument("--name", required=True); q.add_argument("--type", required=True, choices=buckets)
    a = sub.add_parser("add"); a.add_argument("--json", required=True)
    l = sub.add_parser("list"); l.add_argument("--type", required=True, choices=buckets)
    sub.add_parser("stale")
    sub.add_parser("stats")
    args = ap.parse_args()
    if args.cmd == "init": cmd_init()
    elif args.cmd == "query": cmd_query(args.name, args.type)
    elif args.cmd == "add": cmd_add(json.loads(args.json))
    elif args.cmd == "list": cmd_list(args.type)
    elif args.cmd == "stale": cmd_stale()
    elif args.cmd == "stats": cmd_stats()


if __name__ == "__main__":
    main()
