"""
AI 分析服务 - 三阶段分析
"""
import base64
import json
import logging
from pathlib import Path
from typing import Optional

import httpx
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

# 全局客户端
client: Optional[AsyncOpenAI] = None


def get_client() -> AsyncOpenAI:
    global client
    if client is None:
        client = AsyncOpenAI(
            base_url=settings.base_url,
            api_key=settings.api_key,
            timeout=300.0,  # 设置超时为5分钟
            # trust_env=False: 忽略系统/WinINET代理设置，直连AI端点。
            # 某些机器配置了系统代理会导致 httpx 报 "All connection attempts failed"（curl 直连正常）。
            http_client=httpx.AsyncClient(trust_env=False, timeout=300.0),
        )
    return client


def encode_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_image_type(image_path: str) -> str:
    ext = Path(image_path).suffix.lower()
    return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")


def _build_image_content(image_path: str, detail: str = "auto") -> dict:
    b64 = encode_image_base64(image_path)
    img_type = _get_image_type(image_path)
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{img_type};base64,{b64}", "detail": detail},
    }


def _encode_image_scaled(path: str, max_px: int, quality: int):
    """下采样+转JPEG以控制请求体积。返回 (data_uri, 字节数)。失败则回退原图。"""
    try:
        import io
        from PIL import Image
        im = Image.open(path)
        im.load()
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        w, h = im.size
        scale = min(1.0, max_px / max(w, h))
        if scale < 1.0:
            im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality)
        data = buf.getvalue()
        return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}", len(data)
    except Exception as e:
        logger.warning(f"图片压缩失败,用原图: {path} - {e}")
        raw = open(path, "rb").read()
        return f"data:{_get_image_type(path)};base64,{base64.b64encode(raw).decode()}", len(raw)


# 请求体积预算(base64前的原始字节)。API上限约10MB,留余量给文本/JSON
_IMG_BUDGET_BYTES = 6_500_000
_SCALE_TIERS = [(1600, 85), (1400, 80), (1200, 75), (1024, 70), (900, 62), (768, 55)]


def _build_image_blocks_budgeted(paths: list, detail: str = "high", budget: int = _IMG_BUDGET_BYTES):
    """按总字节预算把一组图片编码为content块，逐级降分辨率/画质；仍超则按预算截断。
    返回与paths等长的列表(每项为content块或None表示被丢弃)。"""
    paths = [p for p in paths]
    for max_px, q in _SCALE_TIERS:
        enc = [_encode_image_scaled(p, max_px, q) for p in paths]
        total = sum(n for _, n in enc)
        if total <= budget:
            logger.info(f"图片预算: {len(paths)}张 @ {max_px}px/q{q} = {round(total/1e6,1)}MB")
            return [{"type": "image_url", "image_url": {"url": uri, "detail": detail}} for uri, _ in enc]
    # 最激进档位仍超预算：按预算截断（保留靠前的图）
    enc = [_encode_image_scaled(p, 768, 50) for p in paths]
    blocks, total, kept = [], 0, 0
    for uri, n in enc:
        if total + n > budget:
            blocks.append(None)
            continue
        blocks.append({"type": "image_url", "image_url": {"url": uri, "detail": detail}})
        total += n
        kept += 1
    logger.warning(f"图片超预算,截断保留 {kept}/{len(paths)} 张 = {round(total/1e6,1)}MB")
    return blocks


async def call_ai(messages: list, model: str, response_format: Optional[dict] = None, max_tokens: int = 8192) -> str:
    """调用 AI 接口，支持 JSON 格式约束"""
    kwargs = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if response_format:
        kwargs["response_format"] = response_format

    logger.info(f"调用 AI 模型: {model}, messages 数: {len(messages)}, max_tokens: {max_tokens}")
    try:
        resp = await get_client().chat.completions.create(**kwargs)
    except Exception as e:
        logger.error(f"AI 调用异常: {e}")
        return "{}"
    if resp.choices is None or len(resp.choices) == 0:
        logger.error(f"AI 返回 choices 为空: {resp}")
        return "{}"
    content = resp.choices[0].message.content
    if content is None:
        logger.error(f"AI 返回 content 为 None: {resp}")
        return "{}"
    # 清理可能的 markdown 代码块包裹
    content = content.strip()
    if content.startswith("```"):
        # 移除 ```json ... ``` 包裹
        content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    logger.info(f"AI 返回完成, 长度: {len(content)}")
    return content


async def analyze_single_page(
    page_image: str,
    page_text: str,
    page_table: Optional[str],
    outline: list[dict],
    prompt_template: str,
    model: str,
    slide_index: int,
) -> dict:
    """阶段一：单页分析"""
    outline_str = json.dumps(outline, ensure_ascii=False)

    user_content = [
        {"type": "text", "text": f"## 大纲骨架\n{outline_str}\n\n## 当前页文本\n{page_text}\n"},
        _build_image_content(page_image),
    ]
    if page_table:
        user_content.insert(1, {"type": "text", "text": f"## 当前页表格\n{page_table}\n"})

    system_msg = prompt_template.replace("{slide_index}", str(slide_index))
    system_msg = system_msg.replace("{outline}", outline_str)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_content},
    ]

    result = await call_ai(messages, model, response_format={"type": "json_object"})
    try:
        parsed = json.loads(result)
        parsed["slide_index"] = slide_index
        return parsed
    except (json.JSONDecodeError, TypeError):
        logger.error(f"单页分析 JSON 解析失败, slide_index={slide_index}, raw={result[:200]}")
        return {"slide_index": slide_index, "raw": result, "error": "JSON 解析失败"}


async def analyze_overall(
    page_summaries: list[dict],
    outline: list[dict],
    prompt_template: str,
    model: str,
) -> dict:
    """阶段二：整体分析（基于逐页分析结果）"""
    outline_str = json.dumps(outline, ensure_ascii=False)
    summaries_str = json.dumps(page_summaries, ensure_ascii=False)

    system_msg = prompt_template.replace("{stage1_results}", json.dumps(page_summaries, ensure_ascii=False))
    system_msg = system_msg.replace("{outline}", outline_str)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"## 大纲骨架\n{outline_str}\n\n## 各页分析摘要\n{summaries_str}"},
    ]

    result = await call_ai(messages, model, response_format={"type": "json_object"})
    try:
        return json.loads(result)
    except (json.JSONDecodeError, TypeError):
        logger.error(f"整体分析 JSON 解析失败, raw={result[:200]}")
        return {"raw": result, "error": "JSON 解析失败"}


async def analyze_overall_with_images(
    page_images: list[str],
    page_texts: list[str],
    page_tables: list[str],
    outline: list[dict],
    prompt_template: str,
    model: str,
) -> dict:
    """快速整体分析：直接用所有页面的图片+文本进行一次性分析（多模态）"""
    outline_str = json.dumps(outline, ensure_ascii=False)

    system_msg = prompt_template.replace("{outline}", outline_str)

    # 构建多模态消息：交替插入图片和文本
    user_content = []

    # 添加说明文本
    user_content.append({
        "type": "text",
        "text": f"## 报告大纲\n{outline_str}\n\n## 完整PPT内容（共{len(page_images)}页）\n请基于以下所有页面的图片和文本进行整体分析。\n\n"
    })

    # 统一按体积预算压缩所有页面图片(避免413)
    page_blocks = _build_image_blocks_budgeted(page_images, detail="high")

    # 遍历每一页，添加图片和文本
    for i in range(len(page_images)):
        # 页面标题
        user_content.append({
            "type": "text",
            "text": f"### 第 {i+1} 页\n"
        })

        # 页面图片（高清截图，包含所有数据表格和图表）
        if page_blocks[i] is not None:
            user_content.append(page_blocks[i])

        # 页面文本（LibreOffice提取的纯文本）
        text_content = f"**文本内容：**\n{page_texts[i]}\n"
        if page_tables[i]:
            text_content += f"\n**表格数据：**\n{page_tables[i]}\n"

        user_content.append({
            "type": "text",
            "text": text_content + "\n---\n\n"
        })

    # 添加分析指令
    user_content.append({
        "type": "text",
        "text": "请基于以上所有页面的**图片**（优先）和文本内容，进行深度整体分析。注意：图片中的数据表格和图表是最准确的，如果文本与图片不一致，以图片为准。"
    })

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_content},
    ]

    logger.info(f"快速多模态整体分析: {len(page_images)}页图片, model={model}")
    result = await call_ai(messages, model, response_format={"type": "json_object"}, max_tokens=16384)

    # 尝试解析JSON，如果失败则尝试修复
    try:
        return json.loads(result)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"整体分析 JSON 解析失败: {e}, 尝试修复...")

        # 尝试修复：补全未闭合的大括号
        try:
            # 统计大括号平衡
            open_count = result.count('{')
            close_count = result.count('}')

            if open_count > close_count:
                # 缺少闭合括号，尝试补全
                fixed = result + '}' * (open_count - close_count)
                parsed = json.loads(fixed)
                logger.info("JSON修复成功（补全括号）")
                return parsed
        except:
            pass

        # 修复失败，返回错误格式
        logger.error(f"整体分析 JSON 无法修复, raw前200字符={result[:200]}, 后200字符={result[-200:]}")
        return {"raw": result, "error": "JSON 解析失败且无法修复"}


async def analyze_transcript(
    page_analyses: list[dict],
    overall_analysis: dict,
    transcript_text: str,
    prompt_template: str,
    model: str,
) -> dict:
    """阶段三：转写对照分析"""
    content = (
        f"## 逐页分析结果\n{json.dumps(page_analyses, ensure_ascii=False)}\n\n"
        f"## 整体分析结果\n{json.dumps(overall_analysis, ensure_ascii=False)}\n\n"
        f"## 现场汇报转写文本\n{transcript_text}\n\n"
        "注意：转写文本来自 ASR 语音识别，可能存在错字、数字识别误差，请综合判断。"
    )

    system_msg = prompt_template.replace("{stage1_results}", json.dumps(page_analyses, ensure_ascii=False))
    system_msg = system_msg.replace("{stage2_results}", json.dumps(overall_analysis, ensure_ascii=False))
    system_msg = system_msg.replace("{transcript}", transcript_text)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": content},
    ]

    result = await call_ai(messages, model, response_format={"type": "json_object"})
    try:
        return json.loads(result)
    except (json.JSONDecodeError, TypeError):
        logger.error(f"转写分析 JSON 解析失败, raw={result[:200]}")
        return {"raw": result, "error": "JSON 解析失败"}


async def analyze_document_with_chapters(
    markdown_content: str,
    images: list[dict],
    outline: list[dict],
    overall_prompt: str,
    chapter_prompt: str,
    model: str,
) -> dict:
    """云文档完整分析 - 一次性输出整体分析和分章节分析"""
    outline_str = json.dumps(outline, ensure_ascii=False)

    # 提取一级标题作为章节
    chapters = []
    lines = markdown_content.split('\n')
    current_chapter = None
    current_content = []

    for line in lines:
        # 检测一级标题
        if line.strip().startswith('# ') and not line.strip().startswith('## '):
            # 保存上一章节
            if current_chapter:
                chapters.append({
                    'title': current_chapter,
                    'content': '\n'.join(current_content).strip()
                })
            # 开始新章节
            current_chapter = line.strip()[2:].strip()  # 去掉 '# '
            current_content = []
        else:
            if current_chapter is not None:
                current_content.append(line)

    # 保存最后一章
    if current_chapter:
        chapters.append({
            'title': current_chapter,
            'content': '\n'.join(current_content).strip()
        })

    logger.info(f"提取到 {len(chapters)} 个一级章节")

    # 构建完整的system prompt（包含整体分析和分章节分析指令）
    system_msg = f"""你是中国营销本部述职报告的资深检视专家。请完成两项任务：

【任务一：整体分析】
{overall_prompt}

【任务二：分章节分析】
针对以下每个章节，逐一进行深度分析：
{json.dumps([{'id': f'chapter-{i+1}', 'title': ch['title']} for i, ch in enumerate(chapters)], ensure_ascii=False)}

每个章节分析使用以下标准：
{chapter_prompt}

【输出格式】
严格按照以下JSON格式输出：
{{
  "overall_analysis": {{
    // 整体分析结果（按任务一的格式）
  }},
  "chapter_analyses": [
    {{
      "chapter_id": "chapter-1",
      "chapter_title": "...",
      // 其他章节分析字段
    }},
    ...
  ]
}}
"""

    # 构建user content（文档内容 + 图片）
    user_content = []
    user_content.append({
        "type": "text",
        "text": f"## 文档大纲\n{outline_str}\n\n## 文档完整内容\n{markdown_content}\n\n"
    })

    # 添加章节内容说明
    chapters_text = "\n\n## 章节详细内容\n"
    for i, ch in enumerate(chapters):
        chapters_text += f"\n### 章节 {i+1}: {ch['title']}\n{ch['content'][:500]}...\n"  # 每章取前500字作为示例

    user_content.append({
        "type": "text",
        "text": chapters_text
    })

    # 添加图片
    if images and len(images) > 0:
        user_content.append({
            "type": "text",
            "text": "\n\n## 文档中的图片（按顺序）\n"
        })
        for img_info in images:
            if Path(img_info['actual_path']).exists():
                user_content.append(_build_image_content(img_info['actual_path']))
                user_content.append({
                    "type": "text",
                    "text": f"图片引用: {img_info['relative_path']}\n"
                })

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_content},
    ]

    result = await call_ai(messages, model, response_format={"type": "json_object"})
    try:
        parsed = json.loads(result)
        # 确保返回结构完整
        if 'overall_analysis' not in parsed:
            parsed['overall_analysis'] = {}
        if 'chapter_analyses' not in parsed:
            parsed['chapter_analyses'] = []
        return parsed
    except (json.JSONDecodeError, TypeError):
        logger.error(f"文档完整分析 JSON 解析失败, raw={result[:200]}")
        return {
            "overall_analysis": {"raw": result, "error": "JSON 解析失败"},
            "chapter_analyses": []
        }


async def analyze_document(
    markdown_content: str,
    images: list[dict],
    outline: list[dict],
    prompt_template: str,
    model: str,
) -> dict:
    """云文档整体分析 - 支持多模态(MD文本+图片)"""
    outline_str = json.dumps(outline, ensure_ascii=False)

    # 构建多模态消息: 文本 + 图片穿插
    user_content = []

    # 先添加大纲和文档开头说明
    user_content.append({
        "type": "text",
        "text": f"## 文档大纲\n{outline_str}\n\n## 文档完整内容\n"
    })

    # 如果有图片，按图片在正文中的引用位置"就地"高清注入，保证每张图与其上下文对齐
    # （很多关键数据只存在于图片表格里，如H2各品类/战区目标拆解；必须 detail="high" 才能读清密集小字）
    valid_imgs = [img for img in (images or []) if Path(img.get("actual_path", "")).exists()]
    if valid_imgs:
        import re as _re
        ref_to_path = {img.get("relative_path"): img.get("actual_path") for img in valid_imgs}
        # 统一按体积预算压缩(避免413请求过大)，再按正文引用位置就地注入
        paths = [img["actual_path"] for img in valid_imgs]
        blocks = _build_image_blocks_budgeted(paths, detail="high")
        block_by_path = {p: b for p, b in zip(paths, blocks)}
        img_ref_re = _re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
        parts = _re.split(r'(!\[[^\]]*\]\([^)]+\))', markdown_content)
        injected = set()
        for part in parts:
            if not part:
                continue
            m = img_ref_re.fullmatch(part)
            if m:
                ref = m.group(1)
                actual = ref_to_path.get(ref)
                user_content.append({"type": "text", "text": part})  # 保留图片标记提供上下文
                blk = block_by_path.get(actual)
                if blk is not None:
                    user_content.append(blk)
                    injected.add(actual)
            else:
                user_content.append({"type": "text", "text": part})
        # 兜底：正文未定位到的图片附末尾
        leftover = [(img["relative_path"], img["actual_path"]) for img in valid_imgs
                    if img["actual_path"] not in injected and block_by_path.get(img["actual_path"]) is not None]
        if leftover:
            user_content.append({"type": "text", "text": "\n\n## 其余未定位图片\n"})
            for ref, actual in leftover:
                user_content.append(block_by_path[actual])
                user_content.append({"type": "text", "text": f"图片引用: {ref}\n"})
    else:
        # 无图片，直接放文本
        user_content.append({
            "type": "text",
            "text": markdown_content
        })

    system_msg = prompt_template

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_content},
    ]

    logger.info(f"MD文档多模态整体分析: {len(images)}张图片, model={model}")
    result = await call_ai(messages, model, response_format={"type": "json_object"}, max_tokens=16384)
    try:
        return json.loads(result)
    except (json.JSONDecodeError, TypeError):
        logger.error(f"文档分析 JSON 解析失败, raw前200={result[:200]}, 后200={result[-200:]}")
        return {"raw": result, "error": "JSON 解析失败"}
