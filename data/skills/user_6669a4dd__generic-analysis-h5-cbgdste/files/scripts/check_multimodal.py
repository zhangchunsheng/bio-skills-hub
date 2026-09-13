# -*- coding: utf-8 -*-
"""多模态模型前置检测 — 通用分析H5报告 (generic-analysis-h5)

为什么必须检测：本 skill 的 AI 分析强依赖「读图」——PPT 页图、文档内嵌图里的
表格与图表是最高优先级证据（提示词原文：图片中的数据表格和图表是最准确的，如果
文本与图片不一致，以图片为准）。纯文本模型看不到图：轻则漏关键数字、重则瞎编，
产出的 H5 "看起来完整、实则虚构"。因此**在调用 AI 分析之前必须先确认所用模型
支持图像输入**；确认不了或确认不支持 → 停下，让用户切换到多模态模型，不许硬跑。

本脚本检测「外部模型」（backend/.env 里 BASE_URL/API_KEY/DEFAULT_MODEL 配置的模型，
即 generic_run.py 一条命令 / cloud_doc_run.py 全自动路径要用的模型）。
WorkBuddy 会话模型（--no-ai 路径）的多模态自检在会话内完成：助手用 Read 工具读一张
报告图，能描述出内容即视为多模态——脚本无法代测，SKILL.md 有专门流程。

检测分两级：
  ① 模型名启发式（免费、秒回）：模型名含视觉关键词（vl/vision/4o/omni/gemini 等）→ 直接判可用。
  ② 运行时探测（一次极小调用，几乎不花钱）：名字判断不了时，发一张 64x64 红色测试图问
     "什么颜色"，能正确回答红色 → 判可用；报"不支持图像输入"或答"看不到图" → 判不可用。

用法:
    python check_multimodal.py                        # 检测 backend/.env 的 DEFAULT_MODEL
    python check_multimodal.py --model gpt-4o         # 检测指定模型(不读 .env 的模型名)
    python check_multimodal.py --probe                # 跳过名字判断，强制发测试图探测
    python check_multimodal.py --json                 # 机器可读 JSON 输出
    python check_multimodal.py --backend <目录>       # 指定 backend 目录(自动探测失败时)

退出码:
    0 = 确认支持多模态(可继续)
    1 = 确认不支持 / 无法确认(应停下，让用户换多模态模型)
    2 = 配置缺失(backend/.env 不存在或没配模型)
"""
import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent

# 64x64 纯红色 PNG（运行时探测用，不依赖外部文件）。
# 注意不能用 1x1：部分网关限制图片宽高必须 >10（实测阿里云 MaaS 400 拒绝），64x64 兼容性最好。
RED_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAAfElEQVR4nNXOQREAMAjAsK7+PTMR"
    "PLhGQd7QJnESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ES"
    "J3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ES53Vg6wNShQF/fRSLfgAAAABJ"
    "RU5ErkJggg=="
)

# 视觉/多模态模型名字关键词（小写匹配）。命中即判可用；未命中不代表不可用，
# 会继续走运行时探测。新出的多模态模型加在这里可免去探测调用。
VISION_NAME_HINTS = [
    "vl", "vision", "visual", "omni", "gemini", "llava", "cogvlm", "internvl",
    "minicpm-v", "qwen-vl", "qwen2-vl", "qwen2.5-vl", "qwen3-vl", "qwen2.5-omni",
    "glm-4v", "glm-4.1v", "glm-4.5v", "step-1v", "step-2", "step-3", "deepseek-vl",
    "gpt-4o", "gpt-4.1", "gpt-4.5", "gpt-4-turbo", "claude-3-5", "claude-3.5",
    "claude-3-7", "claude-4", "claude-4-", "grok-4", "kimi-latest", "moonshot-v1-8k-vision",
    "doubao-1.5-vision", "doubao-vision", "doubao-seed-1.6", "hunyuan-vision",
    "hunyuan-turbos", "ernie-4", "ernie-4.5", "minimax-vl", "glm-4v-plus", "glm-4.5",
    "gpt-5", "o1", "o3", "o4",
]
# 明确纯文本、不能传图的模型（命中直接判不可用，省一次探测）
TEXT_ONLY_HINTS = [
    "deepseek-chat", "deepseek-reasoner", "deepseek-r1", "deepseek-v3", "deepseek-v2",
    "qwen-turbo", "qwen-plus", "qwen-max", "qwen3-turbo", "qwen3-plus", "qwen3-max",
    "gpt-3.5", "gpt-4", "claude-2", "claude-3-haiku", "glm-4-flash", "glm-4-air",
    "kimi-moonshot-v1-8k", "doubao-lite", "hunyuan-lite", "ernie-3.5", "llama-3",
    "llama-2", "mistral", "mixtral", "command-r",
]


def find_backend(explicit: str = "") -> Path:
    """定位 backend 目录（含 generic_run.py）。显式参数 > WB_BACKEND > 探测。"""
    cands = []
    if explicit:
        cands.append(Path(explicit))
    if os.environ.get("WB_BACKEND"):
        cands.append(Path(os.environ["WB_BACKEND"]))
    cands += [HERE.parent / "backend", Path(r"D:\Python代码源\报告分析系统\backend")]
    for p in cands:
        if p and (p / "generic_run.py").exists():
            return p
    raise SystemExit("[✗] 找不到 backend 目录（需含 generic_run.py）。"
                     "请用 --backend 指定或设置环境变量 WB_BACKEND")


def load_env(backend: Path) -> dict:
    """读取 backend/.env 的 BASE_URL / API_KEY / DEFAULT_MODEL（键名大小写不敏感）。
    返回缺失字段为 None 的 dict。"""
    env = {}
    env_file = backend / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip().upper()] = v.strip().strip('"').strip("'")
    return {
        "base_url": env.get("BASE_URL"),
        "api_key": env.get("API_KEY"),
        "default_model": env.get("DEFAULT_MODEL"),
    }


def name_check(model: str):
    """按模型名启发式判断。返回 True=多模态 / False=纯文本 / None=无法判断。
    注意先查视觉关键词再查纯文本关键词：TEXT_ONLY 里的短词(如 gpt-4)会子串命中
    多模态长名(如 gpt-4o)，先查 VISION 可避免误判。"""
    name = (model or "").lower()
    if not name:
        return None
    for hint in VISION_NAME_HINTS:
        if hint in name:
            return True
    for hint in TEXT_ONLY_HINTS:
        if hint in name:
            return False
    return None


def _judge_400(text: str):
    """解析 400/422 错误消息：返回 'size'(图太小需放大) / 'no-image'(不支持图像) / 'other'。"""
    low = text.lower()
    if re.search(r"size|dimension|height|width|too small|larger than|resolution|min.*pixel|必须|宽高|长和宽|至少", low):
        return "size"
    if re.search(r"not support|unsupported|does not (support|accept)|only (accept|support) text|text[- ]only|"
                 r"no vision|vision.*(not|no)|不支持|无法处理图像|不能.*图像|图片.*不支持", low):
        return "no-image"
    return "other"


def _make_red_png(size: int):
    """用 PIL 动态生成纯红 PNG（backend 环境装有 Pillow）。失败返回 None。"""
    try:
        import base64 as _b64
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (size, size), (255, 0, 0)).save(buf, format="PNG")
        return _b64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def _probe_once(base_url: str, api_key: str, model: str, png_b64: str) -> tuple:
    """单次运行时探测，返回 (ok, detail)，ok 为 True/False/None(无法确认)。"""
    url = base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        url += "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "这张图片里是什么颜色？只回答颜色名称。"},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{png_b64}"}},
                ],
            }
        ],
        "max_tokens": 16,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        import httpx
        r = httpx.post(url, json=payload, headers=headers, timeout=30.0)
    except Exception as e:
        return None, f"探测请求失败(网络/代理?): {type(e).__name__}: {str(e)[:120]}"

    if r.status_code == 200:
        try:
            content = (r.json()["choices"][0]["message"]["content"] or "").strip()
        except Exception:
            return None, f"探测返回 200 但结构异常: {r.text[:150]}"
        if re.search(r"红|red", content, re.IGNORECASE):
            return True, f"测试图识别为: {content[:40]}"
        if re.search(r"无法|不能|不支持|看不到|没有图片|不包含图片|no image|can'?t|cannot|not (see|support)",
                     content, re.IGNORECASE):
            return False, f"模型答复: {content[:80]}"
        return None, f"探测返回了内容但无法确认是否看图: {content[:60]}"

    err = r.text[:250].replace("\n", " ")
    if r.status_code in (400, 422):
        kind = _judge_400(err)
        if kind == "size":
            return "size", err
        if kind == "no-image":
            return False, f"API 明确拒绝图像输入(HTTP {r.status_code}): {err}"
        return None, f"API 返回 400 但无法判断原因(疑似配置问题): {err}"
    if r.status_code == 401:
        return None, f"API Key 无效(HTTP 401): {err}"
    if r.status_code == 404:
        return None, f"模型或端点不存在(HTTP 404): {err}"
    return None, f"HTTP {r.status_code}: {err}"


def probe_model(base_url: str, api_key: str, model: str) -> dict:
    """运行时探测：先用 64x64 红色测试图；若网关报图太小，动态放大到 128/256 重试。
    返回 {"ok": True/False/None, "detail": str}；None=无法确认(网络/网关/其他问题)。"""
    ok, detail = _probe_once(base_url, api_key, model, RED_PNG_B64)
    if ok != "size":
        return {"ok": ok, "detail": detail}
    for size in (128, 256):
        b64 = _make_red_png(size)
        if not b64:
            break
        ok, detail = _probe_once(base_url, api_key, model, b64)
        if ok != "size":
            return {"ok": ok, "detail": f"[放大到{size}x{size}后] {detail}"}
    return {"ok": None, "detail": f"网关持续报图片尺寸限制: {detail}"}


def check(model: str, base_url: str, api_key: str, force_probe: bool = False) -> dict:
    """完整检测流程。返回 {"ok": bool, "method": str, "detail": str}。"""
    if force_probe:
        return probe_model(base_url, api_key, model) | {"method": "probe"}
    judged = name_check(model)
    if judged is True:
        return {"ok": True, "method": "name", "detail": f"模型名含视觉关键词，判定支持多模态"}
    if judged is False:
        return {"ok": False, "method": "name", "detail": f"模型名命中纯文本关键词，判定不支持多模态"}
    if not base_url or not api_key:
        return {"ok": None, "method": "name",
                "detail": "模型名无法判断且缺少 BASE_URL/API_KEY，无法做运行时探测"}
    probe = probe_model(base_url, api_key, model)
    return {**probe, "method": "probe"}


def main():
    ap = argparse.ArgumentParser(description="检测模型是否支持多模态(图像输入) — 通用分析H5报告前置检测")
    ap.add_argument("--model", default="", help="要检测的模型名(默认读 backend/.env 的 DEFAULT_MODEL)")
    ap.add_argument("--probe", action="store_true", help="跳过模型名判断，强制发测试图探测")
    ap.add_argument("--json", action="store_true", help="机器可读 JSON 输出")
    ap.add_argument("--backend", default="", help="backend 目录(默认自动探测)")
    args = ap.parse_args()

    backend = find_backend(args.backend)
    env = load_env(backend)
    model = args.model or env["default_model"]
    if not model:
        msg = f"未配置模型：请用 --model 指定，或检查 {backend}/.env 的 DEFAULT_MODEL"
        print(json.dumps({"ok": False, "method": "config", "detail": msg}, ensure_ascii=False)
              if args.json else f"[✗] {msg}")
        sys.exit(2)

    result = check(model, env["base_url"] or "", env["api_key"] or "", force_probe=args.probe)
    ok = result["ok"]
    method = result["method"]
    detail = result["detail"]

    if args.json:
        print(json.dumps({"ok": ok, "model": model, "method": method, "detail": detail,
                          "backend": str(backend)}, ensure_ascii=False))
    else:
        if ok is True:
            print(f"[✓] 模型 {model} 支持多模态（{detail}）→ 可以继续分析")
        elif ok is False:
            print(f"[✗] 模型 {model} 不支持多模态（{detail}）")
            print("    分析强依赖读图(图片里的表格/图表是最准确的数据源)，纯文本模型会漏数据甚至瞎编。")
            print("    请任选其一后重试：")
            print(f"      1) 本次覆盖:  python generic_run.py \"<报告>\" --model \"<多模态模型名>\"")
            print(f"      2) 永久生效:  修改 {backend}/.env 的 DEFAULT_MODEL 为多模态模型")
            print(f"      3) 确知支持但检测误报: 加 --skip-multimodal-check 强制继续")
        else:
            print(f"[?] 无法确认模型 {model} 是否支持多模态（{detail}）")
            print("    为安全起见按『不支持』处理，请人工确认该模型能否看图，或换多模态模型后重试；")
            print("    确知支持时可加 --skip-multimodal-check 强制继续。")
    sys.exit(0 if ok is True else 1)


if __name__ == "__main__":
    main()
