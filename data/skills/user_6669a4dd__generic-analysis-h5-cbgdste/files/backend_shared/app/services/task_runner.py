"""
后台任务管理 - PPT 解析 + AI 分析
使用独立数据库 session，避免与请求生命周期冲突
"""
import json
import logging
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session
from app.models.analysis import Analysis
from app.models.config import Config
from app.services.ppt_parser import parse_ppt
from app.services.md_parser import parse_markdown
from app.services.ai_service import analyze_single_page, analyze_overall, analyze_transcript, analyze_document, analyze_document_with_chapters
from app.services.prompt_loader import (
    load_page_analysis_prompt,
    load_chapter_analysis_prompt,
    load_overall_analysis_prompt,
    load_transcript_analysis_prompt,
    get_active_mode
)

logger = logging.getLogger(__name__)


async def run_parse_only(analysis_id: int):
    """仅解析文件，不调用 AI 分析 - 支持 PPT/MD"""
    async with async_session() as db:
        result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
        analysis = result.scalar_one_or_none()
        if not analysis:
            logger.error(f"分析记录 {analysis_id} 不存在")
            return

        try:
            await _update_status(db, analysis, "parsing")

            # 根据文件类型选择解析器
            if analysis.file_type == "md":
                # MD文档解析
                parse_result = await parse_markdown(analysis.ppt_path, analysis_id)
                analysis.outline = json.dumps(parse_result.outline, ensure_ascii=False)
                raw_texts = [{"text": parse_result.markdown_content, "table": ""}]
                analysis.raw_texts = json.dumps(raw_texts, ensure_ascii=False)
                analysis.total_pages = 1  # MD文档统一为1页
            else:
                # PPT解析
                parse_result = await parse_ppt(analysis.ppt_path, analysis_id)
                analysis.outline = json.dumps(parse_result.outline, ensure_ascii=False)
                raw_texts = [
                    {"text": parse_result.page_texts[i], "table": parse_result.page_tables[i]}
                    for i in range(parse_result.total_pages)
                ]
                analysis.raw_texts = json.dumps(raw_texts, ensure_ascii=False)
                analysis.total_pages = parse_result.total_pages

            analysis.current_analyzing_page = 0
            await _update_status(db, analysis, "parsed")

        except Exception as e:
            logger.exception(f"文件解析失败: {e}")
            analysis.status = "error"
            analysis.error_message = str(e)[:500]
            await db.commit()


async def run_analysis_pipeline(analysis_id: int):
    """完整分析流水线：解析 → AI分析 (根据文件类型选择流程)"""
    async with async_session() as db:
        result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
        analysis = result.scalar_one_or_none()
        if not analysis:
            logger.error(f"分析记录 {analysis_id} 不存在")
            return

        try:
            # === 阶段一：文件解析 ===
            await _update_status(db, analysis, "parsing")

            if analysis.file_type == "md":
                # MD文档解析
                parse_result = await parse_markdown(analysis.ppt_path, analysis_id)
                analysis.outline = json.dumps(parse_result.outline, ensure_ascii=False)
                raw_texts = [{"text": parse_result.markdown_content, "table": ""}]
                analysis.raw_texts = json.dumps(raw_texts, ensure_ascii=False)
                analysis.total_pages = 1
            else:
                # PPT解析
                parse_result = await parse_ppt(analysis.ppt_path, analysis_id)
                analysis.outline = json.dumps(parse_result.outline, ensure_ascii=False)
                raw_texts = [
                    {"text": parse_result.page_texts[i], "table": parse_result.page_tables[i]}
                    for i in range(parse_result.total_pages)
                ]
                analysis.raw_texts = json.dumps(raw_texts, ensure_ascii=False)
                analysis.total_pages = parse_result.total_pages

            analysis.current_analyzing_page = 0
            await db.commit()

            # === 阶段二：AI 分析 ===
            # 获取配置
            config = None
            if analysis.config_id:
                r = await db.execute(select(Config).where(Config.id == analysis.config_id))
                config = r.scalar_one_or_none()

            if config:
                # 如果有配置，使用配置中的提示词和模型
                model = config.model_name
                single_prompt = config.single_page_prompt
                overall_prompt = config.overall_prompt
            else:
                # 使用默认配置：根据 prompt_config.json 加载
                model = settings.default_model
                active_mode = get_active_mode()
                logger.info(f"使用默认提示词配置，当前模式: {active_mode}")

                single_prompt = load_page_analysis_prompt()
                overall_prompt = load_overall_analysis_prompt()

            if analysis.file_type == "md":
                # === MD文档分析流程：整体+分章节一次性分析 ===
                await _update_status(db, analysis, "analyzing_overall")

                # 使用云文档专用提示词
                if config:
                    # 配置中的提示词
                    doc_overall_prompt = overall_prompt
                    doc_chapter_prompt = single_prompt
                else:
                    # 使用 prompt_loader 加载
                    doc_overall_prompt = load_overall_analysis_prompt()
                    doc_chapter_prompt = load_chapter_analysis_prompt()

                # 调用完整文档分析（整体+章节）
                full_result = await analyze_document_with_chapters(
                    markdown_content=parse_result.markdown_content,
                    images=parse_result.images,
                    outline=parse_result.outline,
                    overall_prompt=doc_overall_prompt,
                    chapter_prompt=doc_chapter_prompt,
                    model=model,
                )

                # 分离结果
                analysis.overall_analysis = json.dumps(full_result.get('overall_analysis', {}), ensure_ascii=False)
                analysis.page_analyses = json.dumps(full_result.get('chapter_analyses', []), ensure_ascii=False)  # 复用page_analyses存储章节分析
                analysis.config_name = config.name if config else None
                await _update_status(db, analysis, "completed")
            else:
                # === PPT分析流程：逐页 + 整体 ===
                await _update_status(db, analysis, "analyzing_pages")

                page_analyses = []
                for i in range(parse_result.total_pages):
                    analysis.current_analyzing_page = i + 1
                    await db.commit()

                    page_image = parse_result.page_images[i]
                    page_text = parse_result.page_texts[i]
                    page_table = parse_result.page_tables[i]
                    result_json = await analyze_single_page(
                        page_image=page_image,
                        page_text=page_text,
                        page_table=page_table,
                        outline=parse_result.outline,
                        prompt_template=single_prompt,
                        model=model,
                        slide_index=i + 1,
                    )
                    page_analyses.append(result_json)

                analysis.page_analyses = json.dumps(page_analyses, ensure_ascii=False)
                await db.commit()

                # 整体分析
                await _update_status(db, analysis, "analyzing_overall")
                analysis.current_analyzing_page = None
                await db.commit()
                overall_result = await analyze_overall(
                    page_summaries=page_analyses,
                    outline=parse_result.outline,
                    prompt_template=overall_prompt,
                    model=model,
                )
                analysis.overall_analysis = json.dumps(overall_result, ensure_ascii=False)
                analysis.config_name = config.name if config else None
                await _update_status(db, analysis, "completed")

        except Exception as e:
            logger.exception(f"分析流水线失败: {e}")
            analysis.status = "error"
            analysis.error_message = str(e)[:500]
            await db.commit()


async def run_overall_only_pipeline(analysis_id: int):
    """快速分析流水线：解析 → 仅整体分析（跳过逐页分析）"""
    async with async_session() as db:
        result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
        analysis = result.scalar_one_or_none()
        if not analysis:
            logger.error(f"分析记录 {analysis_id} 不存在")
            return

        try:
            # === 阶段一：文件解析 ===
            await _update_status(db, analysis, "parsing")

            if analysis.file_type == "md":
                # MD文档解析
                parse_result = await parse_markdown(analysis.ppt_path, analysis_id)
                analysis.outline = json.dumps(parse_result.outline, ensure_ascii=False)
                raw_texts = [{"text": parse_result.markdown_content, "table": ""}]
                analysis.raw_texts = json.dumps(raw_texts, ensure_ascii=False)
                analysis.total_pages = 1
            else:
                # PPT解析
                parse_result = await parse_ppt(analysis.ppt_path, analysis_id)
                analysis.outline = json.dumps(parse_result.outline, ensure_ascii=False)
                raw_texts = [
                    {"text": parse_result.page_texts[i], "table": parse_result.page_tables[i]}
                    for i in range(parse_result.total_pages)
                ]
                analysis.raw_texts = json.dumps(raw_texts, ensure_ascii=False)
                analysis.total_pages = parse_result.total_pages

            analysis.current_analyzing_page = 0
            await db.commit()

            # === 阶段二：仅整体分析（跳过逐页） ===
            config = None
            if analysis.config_id:
                r = await db.execute(select(Config).where(Config.id == analysis.config_id))
                config = r.scalar_one_or_none()

            if config:
                model = config.model_name
                overall_prompt = config.overall_prompt
            else:
                model = settings.default_model
                active_mode = get_active_mode()
                logger.info(f"使用默认提示词配置，当前模式: {active_mode}")
                overall_prompt = load_overall_analysis_prompt()

            await _update_status(db, analysis, "analyzing_overall")

            # 对于PPT，直接用所有页面的图片+文本做整体分析
            if analysis.file_type == "ppt":
                # 导入新的多模态整体分析函数
                from app.services.ai_service import analyze_overall_with_images

                overall_result = await analyze_overall_with_images(
                    page_images=parse_result.page_images,
                    page_texts=parse_result.page_texts,
                    page_tables=parse_result.page_tables,
                    outline=parse_result.outline,
                    prompt_template=overall_prompt,
                    model=model,
                )
                analysis.overall_analysis = json.dumps(overall_result, ensure_ascii=False)
                analysis.page_analyses = json.dumps([], ensure_ascii=False)  # 空的逐页分析
            else:
                # MD文档分析 - 也使用多模态整体分析
                from app.services.ai_service import analyze_document

                overall_result = await analyze_document(
                    markdown_content=parse_result.markdown_content,
                    images=parse_result.images,
                    outline=parse_result.outline,
                    prompt_template=overall_prompt,
                    model=model,
                )
                analysis.overall_analysis = json.dumps(overall_result, ensure_ascii=False)
                analysis.page_analyses = json.dumps([], ensure_ascii=False)  # 空的章节分析

            analysis.config_name = config.name if config else None
            await _update_status(db, analysis, "completed")

        except Exception as e:
            logger.exception(f"快速分析流水线失败: {e}")
            analysis.status = "error"
            analysis.error_message = str(e)[:500]
            await db.commit()


async def run_transcript_analysis(analysis_id: int):
    """阶段三：转写对照分析"""
    async with async_session() as db:
        result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
        analysis = result.scalar_one_or_none()
        if not analysis:
            logger.error(f"分析记录 {analysis_id} 不存在")
            return

        if not analysis.transcript_text:
            logger.warning(f"分析记录 {analysis_id} 没有转写文本")
            return

        try:
            await _update_status(db, analysis, "analyzing_transcript")

            page_analyses = json.loads(analysis.page_analyses) if analysis.page_analyses else []
            overall_analysis = json.loads(analysis.overall_analysis) if analysis.overall_analysis else {}

            config = None
            if analysis.config_id:
                r = await db.execute(select(Config).where(Config.id == analysis.config_id))
                config = r.scalar_one_or_none()

            if config and config.transcript_prompt:
                prompt = config.transcript_prompt
                model = config.model_name
            else:
                prompt = load_transcript_analysis_prompt()
                model = settings.default_model

            transcript_result = await analyze_transcript(
                page_analyses=page_analyses,
                overall_analysis=overall_analysis,
                transcript_text=analysis.transcript_text,
                prompt_template=prompt,
                model=model,
            )
            analysis.transcript_analysis = json.dumps(transcript_result, ensure_ascii=False)
            await _update_status(db, analysis, "completed")

        except Exception as e:
            logger.exception(f"转写分析失败: {e}")
            analysis.status = "error"
            analysis.error_message = str(e)[:500]
            await db.commit()


async def _update_status(db, analysis: Analysis, status: str):
    analysis.status = status
    await db.commit()
