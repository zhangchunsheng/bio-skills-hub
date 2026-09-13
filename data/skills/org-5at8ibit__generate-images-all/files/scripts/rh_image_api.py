#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全能绘图大师workbuddy版 - 经网关调用服务器出图脚本（key 存技能根 key.txt）

三模型 × 文生图/图生图 = 6 条网关路由：
  nano-banana-pro  t2i /model/t2i-pro  i2i /model/i2i-pro   (算力 7/张，支持 2K/4K)
  nano-banana-2    t2i /model/t2i-v2   i2i /model/i2i-v2    (算力 3/张，固定 2K)
  gpt-image-2      t2i /model/t2i-g2   i2i /model/i2i-g2    (算力 3/张，固定 2K)

协议（经网关 cwapi.xiemoai.com）：
  POST {GATEWAY}/model/<路由>    提交（jh-api-key 头 + Bearer {{apiKey}} 占位；body: prompt/aspectRatio/resolution/imageUrls/quality）→ taskId
  POST {GATEWAY}/app/ai/query    轮询 {taskId} → status SUCCESS/FAILED + results[0].url
  POST {GATEWAY}/app/upload      上传本地图（multipart file）→ data.download_url

版权：奎可智能体出品 https://quakowork.com/
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ============================================================================
# 网关配置
# ============================================================================
GATEWAY_BASE_URL = "http://cwapi.xiemoai.com/v1/gateway/proxy"
QUERY_PATH = "/app/ai/query"
UPLOAD_PATH = "/app/upload"

# ============================================================================
# 模型 ↔ 网关路由映射
# ============================================================================
WORKFLOWS = {
    "nano-banana-pro": {
        "name_cn": "香蕉PRO",
        "t2i": "/model/t2i-pro",
        "i2i": "/model/i2i-pro",
        "resolutions": ["2K", "4K"],   # 2K/4K 可选
        "credits": 7,
    },
    "nano-banana-2": {
        "name_cn": "香蕉V2",
        "t2i": "/model/t2i-v2",
        "i2i": "/model/i2i-v2",
        "resolutions": ["2K"],          # 固定 2K
        "credits": 3,
    },
    "gpt-image-2": {
        "name_cn": "GPT-image-2",
        "t2i": "/model/t2i-g2",
        "i2i": "/model/i2i-g2",
        "resolutions": ["2K"],          # 固定 2K
        "credits": 3,
    },
}
MODEL_ALIASES = {
    "nano-banana-pro": "nano-banana-pro", "banana-pro": "nano-banana-pro", "香蕉pro": "nano-banana-pro",
    "pro": "nano-banana-pro", "gemini-3-pro-image-preview": "nano-banana-pro",
    "nano-banana-2": "nano-banana-2", "nano-banana": "nano-banana-2", "banana-v2": "nano-banana-2",
    "香蕉v2": "nano-banana-2", "v2": "nano-banana-2", "gemini-3.1-flash-image-preview": "nano-banana-2",
    "gpt-image-2": "gpt-image-2", "gptimage2": "gpt-image-2", "gpt-image": "gpt-image-2",
}
ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
MAX_IMAGES = 10
POLL_INTERVAL = 5
MAX_POLL_SECONDS = 900

DEFAULT_MODEL = "gpt-image-2"  # 与 SKILL.md 声明的默认对齐（文字/多元素意图出图最强且 3 算力）
DEFAULT_RESOLUTION = "2K"
DEFAULT_ASPECT = "1:1"

# 输出目录平台自适应：Windows 有 D 盘用 D:\generate_images，否则(macOS/Linux) ~/generate_images
DEFAULT_OUTPUT_DIR = r"D:\generate_images" if os.path.exists("D:\\") else os.path.join(os.path.expanduser("~"), "generate_images")
# 独立 tasklog（避免与其他工具的 taskId 格式互相污染）
TASKLOG = os.path.join(DEFAULT_OUTPUT_DIR, "_tasklog_pro.jsonl")

# ============================================================================
# Key 管理（网关密钥，存本技能根目录 key.txt；缺失时指引注册链接）
# ============================================================================
KEY_FILE = Path(__file__).resolve().parent.parent / "key.txt"
KEY_HELP_URL = "https://quakowork.com/console/api-key?source=workbuddy"


def load_api_key() -> str | None:
    """读 key.txt 首个非空行，去引号/空白；无文件或全空返回 None。"""
    try:
        with open(KEY_FILE, "r", encoding="utf-8-sig") as f:
            for line in f:
                s = line.strip().strip('"').strip("'").strip()
                if s:
                    return s
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return None


def require_api_key() -> str:
    key = load_api_key()
    if not key:
        print(json.dumps({"success": False, "needKey": True, "keyFile": str(KEY_FILE),
                          "error": f"未配置 API Key：请访问 {KEY_HELP_URL} 注册并订阅/充值点数，创建 API Key 后把它交给助手写入 key.txt（或自行粘贴到该文件，单行）"},
                         ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    return key


def mask_key(k: str) -> str:
    return f"{k[:8]}…(len={len(k)})"


def resolve_model(name: str) -> str:
    key = (name or "").strip().lower()
    if key in WORKFLOWS:
        return key
    if key in MODEL_ALIASES:
        return MODEL_ALIASES[key]
    print(json.dumps({"success": False, "error": f"未知模型: {name}，可选: {list(WORKFLOWS)}"}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def auth_headers(api_key: str) -> dict:
    # 网关双头：jh-api-key 带真值；Authorization 为字面量占位，网关侧替换
    return {"jh-api-key": api_key, "Authorization": "Bearer {{apiKey}}", "Content-Type": "application/json"}


# ============================================================================
# 上传 / 提交 / 轮询 / 下载
# ============================================================================
def upload_image(api_key: str, file_path: str) -> str:
    url = f"{GATEWAY_BASE_URL}{UPLOAD_PATH}"
    t0 = time.time()
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        # multipart 不带 Content-Type（由 requests 生成 boundary）；网关双头
        resp = requests.post(url, headers={"jh-api-key": api_key, "Authorization": "Bearer {{apiKey}}"}, files=files, timeout=120)
    j = resp.json()
    if j.get("code") != 0:
        raise RuntimeError(f"上传失败 {file_path}: {j.get('msg', j)}")
    dl = j.get("data", {}).get("download_url")
    if not dl:
        raise RuntimeError(f"上传成功但无 download_url: {j}")
    print(f"[upload] {os.path.basename(file_path)} ({time.time()-t0:.1f}s)", file=sys.stderr)
    return dl


def resolve_image_ref(api_key: str, ref: str) -> str:
    """本地图→上传拿 download_url；http(s) URL→透传。"""
    if ref.startswith(("http://", "https://")):
        return ref
    if not os.path.exists(ref):
        raise RuntimeError(f"图片不存在: {ref}")
    return upload_image(api_key, ref)


def submit(api_key: str, endpoint: str, payload: dict) -> dict:
    url = f"{GATEWAY_BASE_URL}{endpoint}"  # endpoint 已含前导 /，如 /model/t2i-pro
    t0 = time.time()
    resp = requests.post(url, headers=auth_headers(api_key), json=payload, timeout=120)
    try:
        j = resp.json()
    except Exception:
        raise RuntimeError(f"提交非 JSON 响应 HTTP {resp.status_code}: {resp.text[:300]}")
    # 立即成功（少数端点同步返回结果）
    if j.get("status") == "SUCCESS" and j.get("results"):
        print(f"[submit] 同步成功 ({time.time()-t0:.1f}s)", file=sys.stderr)
        return j
    tid = j.get("taskId")
    if not tid:
        ec = j.get("errorCode")
        em = j.get("errorMessage")
        raise RuntimeError(f"提交失败 无 taskId: HTTP {resp.status_code} code={ec} {em}")
    print(f"[submit] 已提交 task={tid} ({time.time()-t0:.1f}s)", file=sys.stderr)
    return {"taskId": tid}


def query_once(api_key: str, task_id: str) -> dict:
    url = f"{GATEWAY_BASE_URL}{QUERY_PATH}"
    resp = requests.post(url, headers=auth_headers(api_key), json={"taskId": task_id}, timeout=30)
    return resp.json()


def poll_until_done(api_key: str, task_id: str) -> dict:
    elapsed = 0
    last_status = None
    last_beat = 0
    while elapsed <= MAX_POLL_SECONDS:
        try:
            j = query_once(api_key, task_id)
        except Exception as e:
            print(f"[poll {elapsed}s] 查询异常: {e}", file=sys.stderr)
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
            continue
        status = j.get("status", "UNKNOWN")
        if status != last_status:
            print(f"[poll {elapsed}s] {status}", file=sys.stderr)
            last_status = status
            last_beat = elapsed
        elif elapsed - last_beat >= 30:
            print(f"[poll {elapsed}s] 仍 {status}…", file=sys.stderr)
            last_beat = elapsed
        if status == "SUCCESS":
            return j
        if status in ("FAILED", "ERROR"):
            em = j.get("errorMessage", "")
            ec = j.get("errorCode", "")
            raise RuntimeError(f"任务失败 [{ec}] {em}")
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
    raise RuntimeError(f"轮询超时 {MAX_POLL_SECONDS}s (task={task_id})")


def download_file(url: str, out_path: str) -> str:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    print(f"[download] {len(r.content)//1024} KB ({time.time()-t0:.1f}s)", file=sys.stderr)
    return out_path


def get_output_dir() -> str:
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    return DEFAULT_OUTPUT_DIR


def sanitize_filename(text: str, max_length: int = 30) -> str:
    s = re.sub(r'[\\/*?:"<>|]', "", text)
    s = " ".join(s.split())
    return (s[:max_length].strip() or "image")


def log_task(task_id: str, model: str, endpoint: str, prompt: str) -> None:
    os.makedirs(os.path.dirname(TASKLOG), exist_ok=True)
    rec = {"ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "task_id": task_id,
           "model": model, "endpoint": endpoint, "prompt": prompt[:200]}
    with open(TASKLOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ============================================================================
# payload 构造
# ============================================================================
def validate_resolution(model: str, resolution: str) -> str:
    allowed = WORKFLOWS[model]["resolutions"]
    if resolution not in allowed:
        print(json.dumps({"success": False, "error": f"{WORKFLOWS[model]['name_cn']} 仅支持分辨率 {allowed}，收到 {resolution}"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    return resolution.lower()  # API 用小写 2k/4k


def build_payload(model: str, mode: str, prompt: str, aspect: str, resolution: str, image_urls: list[str]) -> tuple[str, dict]:
    endpoint = WORKFLOWS[model][mode]
    res_low = validate_resolution(model, resolution)
    payload: dict = {"prompt": prompt, "resolution": res_low}
    # gpt-image-2 额外必填 quality（与 banana 不同），固定 high；三模型均传 aspectRatio
    if model == "gpt-image-2":
        payload["quality"] = "high"
    payload["aspectRatio"] = aspect
    if mode == "i2i":
        if not image_urls:
            raise RuntimeError("图生图需要至少 1 张图片")
        payload["imageUrls"] = image_urls
    return endpoint, payload


# ============================================================================
# 一次完整出图（提交→落盘 task_id→轮询→下载）
# ============================================================================
def run_one(api_key: str, model: str, mode: str, prompt: str, aspect: str, resolution: str, image_refs: list[str], idx: int, total: int) -> dict:
    # i2i：先把本地图全部上传
    image_urls: list[str] = []
    if mode == "i2i":
        for r in image_refs:
            image_urls.append(resolve_image_ref(api_key, r))

    endpoint, payload = build_payload(model, mode, prompt, aspect, resolution, image_urls)
    print(f"[尝试] {model}/{mode} {WORKFLOWS[model]['name_cn']} res={resolution} aspect={aspect} ({idx}/{total})", file=sys.stderr)

    submitted = submit(api_key, endpoint, payload)
    # 同步成功
    if "results" in submitted and submitted.get("status") == "SUCCESS":
        return _finalize(submitted, model, endpoint, prompt, resolution, aspect, idx)

    task_id = submitted["taskId"]
    log_task(task_id, model, endpoint, prompt)
    print(f"[SUBMITTED] task_id={task_id} 已入队，开始轮询（{resolution} 约 30-180s）。若中断/超时取回：python scripts/fetch_task.py {task_id}", file=sys.stderr)

    final = poll_until_done(api_key, task_id)
    return _finalize(final, model, endpoint, prompt, resolution, aspect, idx)


def _finalize(final: dict, model: str, endpoint: str, prompt: str, resolution: str, aspect: str, idx: int) -> dict:
    results = final.get("results") or []
    if not results:
        raise RuntimeError(f"任务完成但无 results: {json.dumps(final, ensure_ascii=False)[:300]}")
    out_dir = get_output_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved = []
    for i, it in enumerate(results, 1):
        url = it.get("url") or it.get("outputUrl")
        if not url:
            continue
        fname = f"{model}_{sanitize_filename(prompt)}_{ts}_{idx}_{i}.png"
        out_path = os.path.join(out_dir, fname)
        download_file(url, out_path)
        saved.append(out_path)
    usage = final.get("usage") or {}
    return {
        "success": True,
        "model": model,
        "endpoint": endpoint,
        "resolution": resolution,
        "aspect": aspect,
        "saved_count": len(saved),
        "saved_paths": saved,
        "credits": WORKFLOWS[model]["credits"],
        "consume_money": final.get("consumeCoins") or usage.get("consumeMoney") or usage.get("thirdPartyConsumeMoney"),
        "task_cost_time": usage.get("taskCostTime"),
    }


# ============================================================================
# check / discover
# ============================================================================
def cmd_check(args):
    api_key = require_api_key()
    print(f"[key] {mask_key(api_key)}", file=sys.stderr)
    routes = {m: {"t2i": wf["t2i"], "i2i": wf["i2i"], "credits": wf["credits"]} for m, wf in WORKFLOWS.items()}
    print(json.dumps({"success": True, "key": mask_key(api_key), "gateway": GATEWAY_BASE_URL,
                      "query": f"{GATEWAY_BASE_URL}{QUERY_PATH}", "routes": routes}, ensure_ascii=False))


def cmd_discover(args):
    """打印路由表 + 对每条路由发空 body 探测首个必填字段（排错用）。"""
    api_key = require_api_key()
    print(f"[key] {mask_key(api_key)} | gateway={GATEWAY_BASE_URL}", file=sys.stderr)
    print(json.dumps({"WORKFLOWS": WORKFLOWS, "ASPECT_RATIOS": ASPECT_RATIOS}, ensure_ascii=False, indent=2), file=sys.stderr)
    print("--- 探测每条路由首个必填字段 ---", file=sys.stderr)
    for model, wf in WORKFLOWS.items():
        for mode in ("t2i", "i2i"):
            ep = wf[mode]
            try:
                resp = requests.post(f"{GATEWAY_BASE_URL}{ep}", headers=auth_headers(api_key), json={}, timeout=20)
                j = resp.json()
                print(f"{model}/{mode} {ep}: code={j.get('errorCode')} {str(j.get('errorMessage',''))[:60]}", file=sys.stderr)
            except Exception as e:
                print(f"{model}/{mode} {ep}: EXC {e}", file=sys.stderr)
            time.sleep(1)


# ============================================================================
# t2i / i2i / auto
# ============================================================================
def cmd_t2i(args):
    api_key = require_api_key()
    model = resolve_model(args.model)
    results = [run_one(api_key, model, "t2i", args.prompt, args.aspect, args.resolution, [], i, args.n)
               for i in range(1, args.n + 1)]
    _emit(results)


def cmd_i2i(args):
    api_key = require_api_key()
    model = resolve_model(args.model)
    refs = [p.strip() for p in args.images.split("|") if p.strip()]
    if not refs:
        print(json.dumps({"success": False, "error": "图生图需要至少 1 张图片，用 | 分隔"}, ensure_ascii=False))
        sys.exit(1)
    if len(refs) > MAX_IMAGES:
        print(json.dumps({"success": False, "error": f"最多 {MAX_IMAGES} 张图片"}, ensure_ascii=False))
        sys.exit(1)
    results = [run_one(api_key, model, "i2i", args.prompt, args.aspect, args.resolution, refs, i, args.n)
               for i in range(1, args.n + 1)]
    _emit(results)


def _emit(results: list[dict]):
    ok = sum(1 for r in results if r.get("success"))
    summary = {"success": ok == len(results), "total": len(results), "ok": ok,
               "saved_count": sum(r.get("saved_count", 0) for r in results),
               "saved_paths": [p for r in results for p in r.get("saved_paths", [])],
               "results": results}
    print(json.dumps(summary, ensure_ascii=False))
    sys.stdout.flush()


# ============================================================================
# CLI
# ============================================================================
def add_common(p):
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--resolution", default=DEFAULT_RESOLUTION)
    p.add_argument("--aspect", default=DEFAULT_ASPECT, choices=ASPECT_RATIOS)
    p.add_argument("-n", type=int, default=1)


def main():
    ap = argparse.ArgumentParser(description="全能绘图大师workbuddy版 - 经网关调用服务器出图")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="校验 key + 账户")
    sub.add_parser("discover", help="打印端点表 + 探测必填字段")
    p_t2i = sub.add_parser("t2i", help="文生图")
    p_t2i.add_argument("prompt")
    add_common(p_t2i)
    p_i2i = sub.add_parser("i2i", help="图生图")
    p_i2i.add_argument("prompt")
    p_i2i.add_argument("--images", required=True, help="参考图，| 分隔，最多 10")
    add_common(p_i2i)
    p_auto = sub.add_parser("auto", help="自动判断（给图走 i2i）")
    p_auto.add_argument("prompt")
    p_auto.add_argument("--images", default="")
    add_common(p_auto)

    args = ap.parse_args()
    if args.cmd == "check":
        cmd_check(args)
    elif args.cmd == "discover":
        cmd_discover(args)
    elif args.cmd == "t2i":
        cmd_t2i(args)
    elif args.cmd == "i2i":
        cmd_i2i(args)
    elif args.cmd == "auto":
        if args.images:
            cmd_i2i(args)
        else:
            cmd_t2i(args)


if __name__ == "__main__":
    main()
