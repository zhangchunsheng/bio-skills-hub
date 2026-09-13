"""通用分析H5报告 - 一条命令驱动脚本 (generic-analysis-h5)

把「上传 → 快速分析(仅整体) → 导出H5 → 复制到根目录」四步合成一条命令，
任何工具(Claude Code / Codex / workbuddy / 纯命令行)执行结果完全一致。

落位：backend/generic_run.py   （必须放在 backend 根目录，脚本靠自身位置定位 backend）

用法:
    python generic_run.py "<报告文件路径>"                 # 全流程
    python generic_run.py "<路径>" --out "我的报告.html"    # 指定输出文件名
    python generic_run.py --id 92 --h5-only                # 复用已分析记录，只重出H5
    python generic_run.py --id 92 --check                  # 只体检某条记录
    python generic_run.py --id 92 --title "正确的标题.pptx" # 修标题(改 ppt_path)后重出H5

支持格式: .ppt / .pptx / .md / .zip(MD+图片，推荐)
"""
import argparse
import asyncio
import json
import os
import re
import shutil
import sqlite3
import sys
import zipfile
from pathlib import Path

# --- 统一工作目录：database_url 是相对路径 ./data/analysis.db，必须切到 backend ---
BACKEND_DIR = Path(__file__).resolve().parent
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from app.core.config import settings  # noqa: E402

# H5 模板真正读取的 10 个维度 key，用于产出后体检
OVERALL_KEYS = [
    ("executive_summary", "执行摘要"),
    ("data_quality_check", "数据质量检查"),
    ("critical_business_issues", "核心经营问题"),
    ("root_cause_synthesis", "根因综合分析"),
    ("logic_chain_review", "逻辑链审查"),
    ("strategy_effectiveness", "策略有效性评估"),
    ("replicable_highlights", "可复制亮点"),
    ("recommendations", "改进建议"),
    ("information_gaps", "信息缺口"),
    ("final_assessment", "最终评估"),
]
IMAGE_DIR_NAMES = ["图片和附件", "images", "assets", "media"]

# ---------------------------------------------------------------- 多模态检测
# 分析强依赖读图（图片里的表格/图表是最准确的数据源），纯文本模型会漏数据甚至瞎编。
# 因此跑 AI 分析前必须先确认所用模型支持图像输入；确认不了 → 停下让用户换多模态模型。
# 逻辑与 scripts/check_multimodal.py 保持一致，但内联在这里保证脚本复制到 backend 后可自包含运行。

# 64x64 纯红色 PNG（运行时探测用，不依赖外部文件）。
# 注意不能用 1x1：部分网关限制图片宽高必须 >10（实测阿里云 MaaS 400 拒绝），64x64 兼容性最好。
RED_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAAfElEQVR4nNXOQREAMAjAsK7+PTMR"
    "PLhGQd7QJnESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ES"
    "J3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ESJ3ES53Vg6wNShQF/fRSLfgAAAABJ"
    "RU5ErkJggg=="
)
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
TEXT_ONLY_HINTS = [
    "deepseek-chat", "deepseek-reasoner", "deepseek-r1", "deepseek-v3", "deepseek-v2",
    "qwen-turbo", "qwen-plus", "qwen-max", "qwen3-turbo", "qwen3-plus", "qwen3-max",
    "gpt-3.5", "gpt-4", "claude-2", "claude-3-haiku", "glm-4-flash", "glm-4-air",
    "kimi-moonshot-v1-8k", "doubao-lite", "hunyuan-lite", "ernie-3.5", "llama-3",
    "llama-2", "mistral", "mixtral", "command-r",
]


def _name_check(model: str):
    """按模型名启发式判断。True=多模态 / False=纯文本 / None=无法判断。
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
    import re as _re
    import httpx

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
        r = httpx.post(url, json=payload, headers=headers, timeout=30.0)
    except Exception as e:
        return None, f"探测请求失败(网络/代理?): {type(e).__name__}: {str(e)[:120]}"

    if r.status_code == 200:
        try:
            content = (r.json()["choices"][0]["message"]["content"] or "").strip()
        except Exception:
            return None, f"探测返回 200 但结构异常: {r.text[:150]}"
        if _re.search(r"红|red", content, _re.IGNORECASE):
            return True, f"测试图识别为: {content[:40]}"
        if _re.search(r"无法|不能|不支持|看不到|没有图片|不包含图片|no image|can'?t|cannot|not (see|support)",
                      content, _re.IGNORECASE):
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


def _probe_model(base_url: str, api_key: str, model: str) -> tuple:
    """运行时探测：先用 64x64 红色测试图；若网关报图太小，动态放大到 128/256 重试。
    返回 (ok, detail)，ok 为 True/False/None(无法确认)。"""
    ok, detail = _probe_once(base_url, api_key, model, RED_PNG_B64)
    if ok != "size":
        return ok, detail
    for size in (128, 256):
        b64 = _make_red_png(size)
        if not b64:
            break
        ok, detail = _probe_once(base_url, api_key, model, b64)
        if ok != "size":
            return ok, f"[放大到{size}x{size}后] {detail}"
    return None, f"网关持续报图片尺寸限制: {detail}"


def check_multimodal(model: str, base_url: str, api_key: str, force_probe: bool = False) -> tuple:
    """完整检测：模型名启发式 → 必要时运行时探测。
    返回 (ok, detail)，ok 为 True/False/None(无法确认)。"""
    if force_probe:
        return _probe_model(base_url, api_key, model)
    judged = _name_check(model)
    if judged is True:
        return True, "模型名含视觉关键词，判定支持多模态"
    if judged is False:
        return False, "模型名命中纯文本关键词，判定不支持多模态"
    if not base_url or not api_key:
        return None, "模型名无法判断且缺少 BASE_URL/API_KEY，无法做运行时探测"
    return _probe_model(base_url, api_key, model)


def require_multimodal(model: str, backend: Path):
    """多模态前置检查。不通过/无法确认 → 打印指引并 SystemExit(1)，绝不硬跑 AI。"""
    ok, detail = check_multimodal(model, settings.base_url, settings.api_key)
    if ok is True:
        log(f"[前置✓] 模型 {model} 支持多模态（{detail}）")
        return
    head = "[✗] 模型 {m} 未确认支持多模态（{d}）".format(m=model, d=detail)
    log(head)
    log("    分析强依赖读图(图片里的表格/图表是最准确的数据源)，纯文本模型会漏数据甚至瞎编。")
    log("    请任选其一后重试：")
    log(f"      1) 本次覆盖:  python generic_run.py \"<报告>\" --model \"<多模态模型名>\"")
    log(f"      2) 永久生效:  修改 {backend / '.env'} 的 DEFAULT_MODEL 为多模态模型")
    log(f"      3) 确知支持但检测误报: 加 --skip-multimodal-check 强制继续")
    raise SystemExit(1)


def log(msg: str):
    print(msg, flush=True)


def detect_file_type(filename: str) -> str:
    """与 /api/analyses/upload 完全一致的类型判定：zip 视为云文档"""
    lower = filename.lower()
    if lower.endswith((".ppt", ".pptx")):
        return "ppt"
    if lower.endswith((".md", ".zip")):
        return "md"
    raise SystemExit(f"[✗] 仅支持 PPT/PPTX/MD/ZIP 文件，收到: {filename}")


# ---------------------------------------------------------------- 步骤1 建记录
async def create_record(file_path: Path, config_id: int = 0) -> tuple[int, str]:
    """等价于 POST /api/analyses/upload，但不需要启动 uvicorn 服务"""
    from app.core.database import async_session, init_db
    from app.models.analysis import Analysis

    await init_db()  # 表不存在时自动建表，幂等

    name = file_path.name
    file_type = detect_file_type(name)

    async with async_session() as db:
        analysis = Analysis(
            config_id=config_id if config_id > 0 else None,
            original_filename=name,
            file_type=file_type,
            ppt_path="",
            status="uploaded",
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        analysis_id = analysis.id

        upload_dir = Path(settings.upload_dir) / str(analysis_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        dest = upload_dir / name
        shutil.copyfile(file_path, dest)

        analysis.ppt_path = str(dest)
        analysis.status = "ready"
        await db.commit()

    log(f"[1/4] 已建记录  分析ID={analysis_id}  类型={file_type}  存至 {dest}")
    return analysis_id, file_type


# ------------------------------------------------- ZIP 预解压 + 图片目录扁平化
def preflatten_zip(analysis_id: int, zip_path: Path):
    """把 ZIP 预解压到 uploads/{id}/{id}/ 并把图片目录提到该层。

    踩坑点：解析器和 H5 生成器都只在 uploads/{id}/{id}/{图片和附件|images|...}
    这一层找图。若 ZIP 里多包了一层「报告名/」文件夹，图片就会全部丢失。
    这里提前解压并把图片目录上移一层，等价于操作文档里的手工修复。
    """
    out_dir = Path(settings.upload_dir) / str(analysis_id) / str(analysis_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)

    if any((out_dir / n).is_dir() for n in IMAGE_DIR_NAMES):
        return  # 结构已正确

    for name in IMAGE_DIR_NAMES:
        for nested in sorted(out_dir.rglob(name)):
            if nested.is_dir():
                shutil.move(str(nested), str(out_dir / name))
                log(f"      ↳ 图片目录已上移: {nested.name} → uploads/{analysis_id}/{analysis_id}/{name}")
                return
    log("      ↳ 提示: ZIP 内未找到图片目录(图片和附件/images/assets/media)，H5 将无图")


# ------------------------------------------------------------ 步骤2 快速分析
async def run_analysis(analysis_id: int):
    from app.services.task_runner import run_overall_only_pipeline

    log(f"[2/4] 快速分析中(仅整体分析，多模态传图+文本，约3-5分钟)… id={analysis_id}")
    await run_overall_only_pipeline(analysis_id)


# ------------------------------------------------------------ 读库 / 体检
def fetch_row(analysis_id: int) -> dict:
    conn = sqlite3.connect("data/analysis.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    conn.close()
    if row is None:
        raise SystemExit(f"[✗] 数据库中不存在分析记录 id={analysis_id}")
    return dict(row)


def check_result(row: dict) -> bool:
    """体检：状态 / JSON是否被截断 / 10个维度覆盖情况"""
    status = row.get("status")
    if status == "error":
        log(f"[✗] 分析失败: {row.get('error_message')}")
        return False

    raw = row.get("overall_analysis") or ""
    try:
        overall = json.loads(raw) if isinstance(raw, str) else (raw or {})
    except json.JSONDecodeError:
        log(f"[✗] overall_analysis 不是合法JSON(长度{len(raw)})，多半是 max_tokens 截断，请重跑分析")
        return False

    if not isinstance(overall, dict) or not overall:
        log("[✗] overall_analysis 为空 {}，AI 返回被截断或解析失败，请重跑分析")
        return False

    # ai_service 解析不了 AI 返回时会存成 {"raw": ..., "error": ...}，
    # 这种记录长度看着很大但 H5 会整片空白，必须拦下来
    if "error" in overall and "raw" in overall:
        log(f"[✗] AI 返回的不是合法JSON，已被存成 raw/error: {str(overall.get('error'))[:120]}")
        log("     多为 JSON 截断，请重跑分析(max_tokens 已设 16384)")
        return False

    hit = [zh for k, zh in OVERALL_KEYS if overall.get(k)]
    miss = [zh for k, zh in OVERALL_KEYS if not overall.get(k)]
    log(f"      状态={status}  JSON长度={len(raw)}  维度命中 {len(hit)}/10")
    if miss:
        log(f"      ⚠ 缺失维度: {', '.join(miss)}")
    return True


# ------------------------------------------------------------ 步骤3/4 导出H5
def export_h5(analysis_id: int, out_path: Path | None) -> Path:
    row = fetch_row(analysis_id)

    from app.services.h5_export_generic import generate_generic_h5  # ★只用这个生成器

    generate_generic_h5(row)
    src = Path(settings.h5_export_dir) / f"{analysis_id}.html"
    if not src.exists():
        raise SystemExit(f"[✗] H5 未生成: {src}")
    size_mb = src.stat().st_size / 1024 / 1024
    log(f"[3/4] H5 已生成: {src}  ({size_mb:.2f} MB)")

    if out_path is None:
        stem = Path(row.get("original_filename") or f"分析报告-{analysis_id}").stem
        out_path = BACKEND_DIR.parent / f"{stem}-通用分析.html"
    out_path = out_path if out_path.is_absolute() else (BACKEND_DIR.parent / out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out_path)
    log(f"[4/4] 已复制到: {out_path}")
    return out_path


def set_title(analysis_id: int, title: str):
    """H5 标题取自 ppt_path 的文件名，按操作文档的方式直接改库"""
    conn = sqlite3.connect("data/analysis.db")
    conn.execute(
        "UPDATE analyses SET ppt_path = ? WHERE id = ?",
        (f"uploads/{analysis_id}/{title}", analysis_id),
    )
    conn.commit()
    conn.close()
    log(f"      ↳ 标题已改为: {title}")


# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="通用分析H5报告 - 快速模式(仅整体分析)一键跑通")
    ap.add_argument("file", nargs="?", help="报告文件路径 (.ppt/.pptx/.md/.zip)")
    ap.add_argument("--id", type=int, help="复用已有分析ID")
    ap.add_argument("--out", help="输出HTML路径/文件名(默认项目根目录/<原名>-通用分析.html)")
    ap.add_argument("--title", help="覆盖H5标题(改数据库 ppt_path)")
    ap.add_argument("--model", default="",
                    help="覆盖分析模型(默认 backend/.env 的 DEFAULT_MODEL)。覆盖时也会参与多模态检测")
    ap.add_argument("--check-multimodal", action="store_true",
                    help="只做多模态模型检测，不分析不出H5(退出码 0=可用 1=不可用)")
    ap.add_argument("--skip-multimodal-check", action="store_true",
                    help="跳过多模态检测(确知所用模型支持看图时用，否则不推荐)")
    ap.add_argument("--config-id", type=int, default=0, help="提示词配置ID，0=用 prompt_config.json 的 generic 模式")
    ap.add_argument("--h5-only", action="store_true", help="跳过分析，只重出H5")
    ap.add_argument("--check", action="store_true", help="只体检，不做别的")
    ap.add_argument("--upload-only", action="store_true",
                    help="只建记录+落盘ZIP(不跑AI)，供 WorkBuddy 会话内模型分析后 --h5-only")
    args = ap.parse_args()

    # --model 覆盖 .env 的 DEFAULT_MODEL（运行时改 settings，task_runner 会读到）
    if args.model:
        settings.default_model = args.model

    if args.check_multimodal:
        model = args.model or settings.default_model
        ok, detail = check_multimodal(model, settings.base_url, settings.api_key)
        log(f"[{'✓' if ok is True else '✗'}] 模型 {model} 多模态检测: {detail}")
        sys.exit(0 if ok is True else 1)

    if args.upload_only:
        if not args.file:
            raise SystemExit("[✗] --upload-only 需要配合报告文件路径")
        src = Path(args.file).expanduser()
        if not src.exists():
            raise SystemExit(f"[✗] 文件不存在: {src}")
        analysis_id, file_type = asyncio.run(create_record(src, args.config_id))
        if src.suffix.lower() == ".zip":
            preflatten_zip(analysis_id, Path(settings.upload_dir) / str(analysis_id) / src.name)
        # 必须解析：H5 左侧原文依赖 outline / raw_texts / total_pages，
        # 只建记录不解析会导致 H5 左侧全空（表格与图片都丢）
        from app.services.task_runner import run_parse_only
        asyncio.run(run_parse_only(analysis_id))
        row = fetch_row(analysis_id)
        log(f"\n[✓] 已建记录并解析 ID={analysis_id} 类型={file_type}（未做AI分析）")
        log(f"    原文长度={len(row.get('raw_texts') or '')} outline={'有' if row.get('outline') else '无'}")
        log(f"    素材目录: {Path(settings.upload_dir) / str(analysis_id) / str(analysis_id)}")
        log("\n    ⚠ 下一步由 WorkBuddy 会话模型读图分析，先做多模态自检：")
        log("      Read 一张「图片和附件/」里的图，能描述出内容 → 会话模型是多模态，继续；")
        log("      Read 失败/看不到图 → 先让用户切换到多模态模型再继续分析。")
        log(f"    → 会话内模型分析后: python write_session_analysis.py --id {analysis_id} --json analysis.json")
        log(f"    → 然后出H5:        python generic_run.py --id {analysis_id} --h5-only")
        return

    if args.check:
        if not args.id:
            raise SystemExit("[✗] --check 需要配合 --id")
        check_result(fetch_row(args.id))
        return

    if args.h5_only:
        if not args.id:
            raise SystemExit("[✗] --h5-only 需要配合 --id")
        if args.title:
            set_title(args.id, args.title)
        check_result(fetch_row(args.id))
        export_h5(args.id, Path(args.out) if args.out else None)
        return

    if args.id:
        analysis_id = args.id
        file_type = fetch_row(analysis_id).get("file_type", "ppt")
    else:
        if not args.file:
            raise SystemExit("[✗] 请给出报告文件路径，或用 --id 复用已有记录")
        src = Path(args.file).expanduser()
        if not src.exists():
            raise SystemExit(f"[✗] 文件不存在: {src}")
        analysis_id, file_type = asyncio.run(create_record(src, args.config_id))
        if src.suffix.lower() == ".zip":
            preflatten_zip(analysis_id, Path(settings.upload_dir) / str(analysis_id) / src.name)

    # ★ 多模态前置检测：确认所用模型支持看图，否则立即停下让用户换模型，不硬跑 AI
    if not args.skip_multimodal_check:
        require_multimodal(args.model or settings.default_model, BACKEND_DIR)

    asyncio.run(run_analysis(analysis_id))

    row = fetch_row(analysis_id)
    if not check_result(row):
        raise SystemExit(f"[✗] 分析未通过体检，未导出H5。可修复后执行: python generic_run.py --id {analysis_id} --h5-only")

    if args.title:
        set_title(analysis_id, args.title)

    out = export_h5(analysis_id, Path(args.out) if args.out else None)
    log(f"\n[✓] 完成  分析ID={analysis_id}  类型={file_type}\n    {out}")


if __name__ == "__main__":
    main()
