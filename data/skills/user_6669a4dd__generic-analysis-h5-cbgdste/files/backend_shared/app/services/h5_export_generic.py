"""通用分析H5报告导出 - 适配generic模式的JSON结构"""
import base64
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


def _image_to_base64(image_path: str) -> str:
    """将图片文件转为 base64 data URI"""
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        ext = Path(image_path).suffix.lower()
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext.replace(".", ""), "image/png")
        return f"data:{mime};base64,{base64.b64encode(data).decode()}"
    except Exception as e:
        logger.warning(f"图片转 base64 失败: {image_path} - {e}")
        return ""


def _markdown_to_html(md_text: str, images: list = None) -> str:
    """将Markdown转换为HTML，支持标题、表格、图片、样式

    Args:
        md_text: Markdown文本
        images: 图片映射列表 [{'relative_path': '...', 'actual_path': '...'}]
    """
    if not md_text:
        return ""

    import re

    html = md_text

    # 0. 预处理：直接删除所有反斜杠
    html = html.replace('\\', '')

    # 1. 图片处理（先处理，避免被其他规则干扰）
    if images:
        # 构建图片路径映射
        image_map = {}
        for img_info in images:
            rel_path = img_info.get('relative_path', '')
            actual_path = img_info.get('actual_path', '')
            if rel_path and actual_path and Path(actual_path).exists():
                # 转换为base64
                try:
                    img_base64 = _image_to_base64(actual_path)
                    image_map[rel_path] = img_base64
                except Exception as e:
                    logger.warning(f"图片转base64失败: {actual_path} - {e}")

        # 替换图片引用
        def replace_image(match):
            alt = match.group(1)
            src = match.group(2)
            if src in image_map:
                return f'<img src="{image_map[src]}" alt="{alt}" style="max-width:100%;height:auto;margin:12px 0;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.1);cursor:pointer;" onclick="openImageModal(this.src)">'
            else:
                return f'<span style="color:#ef4444;">[图片缺失: {src}]</span>'

        html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, html)

    # 2. 表格处理（必须在其他规则之前）
    lines = html.split('\n')
    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # 检测表格（至少两行，第二行是分隔符 |---|---|）
        if '|' in line and i + 1 < len(lines) and re.match(r'^\s*\|[\s:-]+\|', lines[i + 1]):
            # 表格开始
            table_lines = [line]
            j = i + 1
            while j < len(lines) and '|' in lines[j]:
                table_lines.append(lines[j])
                j += 1
            i = j

            # 构建HTML表格
            if len(table_lines) >= 2:
                table_html = '<div class="table-wrap" onclick="openTableModal(this)">'
                table_html += '<table style="border-collapse:collapse;width:100%;border:1px solid #e2e8f0;">'
                # 表头（第一行）
                header_cells = [c.strip() for c in table_lines[0].split('|')[1:-1]]
                table_html += '<thead style="background:#f8fafc;"><tr>'
                for cell in header_cells:
                    table_html += f'<th style="border:1px solid #e2e8f0;padding:10px 12px;text-align:left;font-weight:600;color:#1e293b;">{cell}</th>'
                table_html += '</tr></thead>'

                # 表格内容（从第三行开始）
                table_html += '<tbody>'
                for row_line in table_lines[2:]:
                    cells = [c.strip() for c in row_line.split('|')[1:-1]]
                    table_html += '<tr>'
                    for cell in cells:
                        # 处理单元格内的样式
                        cell_html = cell
                        cell_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', cell_html)
                        table_html += f'<td style="border:1px solid #e2e8f0;padding:10px 12px;">{cell_html}</td>'
                    table_html += '</tr>'
                table_html += '</tbody></table></div>'

                processed_lines.append(table_html)
        else:
            processed_lines.append(lines[i])
            i += 1

    html = '\n'.join(processed_lines)

    # 3. 标题（添加ID用于锚点跳转）
    heading_counter = [0]

    def replace_heading(match):
        level = len(match.group(1))
        text = match.group(2)
        heading_counter[0] += 1
        heading_id = f"heading-{heading_counter[0]}"
        sizes = {1: '24px', 2: '20px', 3: '18px', 4: '16px', 5: '15px', 6: '14px'}
        margins = {1: '24px 0 14px', 2: '20px 0 12px', 3: '18px 0 10px', 4: '16px 0 10px', 5: '14px 0 8px', 6: '12px 0 8px'}
        colors = {1: '#dc2626', 2: '#7c3aed', 3: '#1e293b', 4: '#1e293b', 5: '#1e293b', 6: '#1e293b'}

        return f'<h{level} id="{heading_id}" style="font-size:{sizes[level]};font-weight:700;color:{colors.get(level, "#1e293b")};margin:{margins[level]};scroll-margin-top:20px;">{text}</h{level}>'

    html = re.sub(r'^(#{1,6})\s+(.+)$', replace_heading, html, flags=re.MULTILINE)

    # 4. 粗体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong style="font-weight:600;color:#1e293b;">\1</strong>', html)
    html = re.sub(r'__(.+?)__', r'<strong style="font-weight:600;color:#1e293b;">\1</strong>', html)

    # 5. 斜体
    html = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', html)
    html = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'<em>\1</em>', html)

    # 6. 行内代码
    html = re.sub(r'`([^`]+)`', r'<code style="background:#f1f5f9;padding:2px 6px;border-radius:3px;font-size:0.9em;color:#e11d48;">\1</code>', html)

    # 7. 链接
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#2563eb;text-decoration:underline;" target="_blank">\1</a>', html)

    # 8. 列表项
    html = re.sub(r'^\s*-\s+(.+)$', r'<li style="margin:4px 0;">\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\s*\*\s+(.+)$', r'<li style="margin:4px 0;">\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\s*\d+\.\s+(.+)$', r'<li style="margin:4px 0;">\1</li>', html, flags=re.MULTILINE)

    # 包裹连续的列表项
    html = re.sub(r'(<li[^>]*>.*?</li>(?:\n<li[^>]*>.*?</li>)*)', r'<ul style="margin:12px 0;padding-left:24px;line-height:1.8;">\1</ul>', html, flags=re.DOTALL)

    # 9. 段落处理
    lines = html.split('\n')
    final_lines = []
    in_para = False
    para_content = []

    for line in lines:
        stripped = line.strip()

        # 如果是HTML标签或空行，结束段落
        if not stripped or stripped.startswith('<'):
            if in_para and para_content:
                final_lines.append('<p style="margin:8px 0;line-height:1.8;color:#334155;">' + ' '.join(para_content) + '</p>')
                para_content = []
                in_para = False

            if stripped:
                final_lines.append(line)
        else:
            # 普通文本行
            in_para = True
            para_content.append(stripped)

    # 处理最后的段落
    if para_content:
        final_lines.append('<p style="margin:8px 0;line-height:1.8;color:#334155;">' + ' '.join(para_content) + '</p>')

    return '\n'.join(final_lines)


def generate_generic_h5(analysis_data: dict) -> str:
    """生成通用分析模式的H5报告"""
    analysis_id = analysis_data["id"]

    # 修复文件名编码问题 - 使用多种方法尝试
    filename = "未命名报告"
    ppt_path = analysis_data.get("ppt_path", "")

    # 方法1: 从路径提取（可能有编码问题）
    if ppt_path:
        try:
            import os
            filename = os.path.basename(ppt_path)
            logger.info(f"从ppt_path提取文件名: {filename}")
            # 检查是否有乱码（非ASCII且非中文字符过多）
            if filename and not any(c in filename for c in ['�', '\x00']):
                # 看起来OK
                logger.info(f"文件名OK，使用: {filename}")
                pass
            else:
                logger.warning(f"文件名有乱码: {filename}")
                raise ValueError("filename has encoding issues")
        except Exception as e:
            logger.warning(f"文件名提取异常: {e}")
            # 方法2: 尝试从原始文件名字段获取
            orig = analysis_data.get("original_filename", "")
            if orig and isinstance(orig, str):
                filename = orig
                logger.info(f"使用original_filename: {filename}")
            else:
                # 方法3: 使用ID作为标识
                filename = f"分析报告-{analysis_id}"
                logger.info(f"使用默认名称: {filename}")

    # 最后检查：如果文件名看起来还是有问题，使用备用名称
    if not filename or len(filename) < 3 or '�' in filename:
        filename = f"分析报告-{analysis_id}"
        logger.info(f"最终使用备用名称: {filename}")

    logger.info(f"最终确定的文件名: {filename}")
    total_pages = analysis_data.get("total_pages", 0)

    # 获取模型和时间（转换为北京时间 UTC+8）
    # 优先用记录里标注的实际分析模型（tags 字段存 "model:xxx"），
    # 只有没标注时才回退到 .env 的 DEFAULT_MODEL——
    # 否则会出现「会话内模型分析、H5 却显示 .env 里外部模型」的错标。
    model_name = settings.default_model
    _tags = analysis_data.get("tags") or ""
    if isinstance(_tags, str) and "model:" in _tags:
        for _seg in _tags.split(","):
            _seg = _seg.strip()
            if _seg.startswith("model:"):
                _v = _seg[len("model:"):].strip()
                if _v:
                    model_name = _v
                break
    analysis_time = analysis_data.get("updated_at", "") or analysis_data.get("created_at", "")
    if isinstance(analysis_time, str) and analysis_time:
        try:
            # 解析UTC时间并转换为北京时间
            from datetime import datetime, timedelta
            dt = datetime.fromisoformat(analysis_time.replace('Z', '+00:00'))
            # 加8小时转为北京时间
            dt_beijing = dt + timedelta(hours=8)
            analysis_time = dt_beijing.strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass
    elif isinstance(analysis_time, datetime):
        # 如果是datetime对象，加8小时
        from datetime import timedelta
        analysis_time = (analysis_time + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

    # 解析整体分析
    overall = analysis_data.get("overall_analysis")
    if isinstance(overall, str):
        overall = json.loads(overall)
    if not isinstance(overall, dict):
        overall = {}

    # 获取文件类型
    file_type = analysis_data.get("file_type", "ppt")

    # 获取页面图片（PPT）或Markdown内容（MD）
    upload_dir = Path(settings.upload_dir) / str(analysis_id)
    page_images = []
    md_html = ""
    images_info = []

    if file_type == "md":
        # MD文件：获取Markdown原文并转换为HTML
        raw_texts = analysis_data.get("raw_texts")
        if raw_texts:
            try:
                import re
                import urllib.parse

                texts_data = json.loads(raw_texts) if isinstance(raw_texts, str) else raw_texts
                if texts_data and len(texts_data) > 0:
                    md_content = texts_data[0].get("text", "")

                    # 查找图片文件
                    images_info = []
                    # 图片目录：uploads/{id}/{id}/图片和附件
                    img_search_dir = upload_dir / str(analysis_id)
                    if img_search_dir.exists():
                        possible_dirs = ["图片和附件", "images", "assets", "media"]
                        for dir_name in possible_dirs:
                            img_dir = img_search_dir / dir_name
                            if img_dir.exists():
                                logger.info(f"找到图片目录: {img_dir}")

                                # 提取MD中的图片引用
                                img_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', md_content)

                                for alt, src in img_refs:
                                    # URL解码图片路径
                                    src_decoded = urllib.parse.unquote(src)
                                    img_name = Path(src_decoded).name

                                    # 在图片目录中查找匹配的文件
                                    for img_file in img_dir.iterdir():
                                        if img_file.is_file() and (
                                            img_file.name == img_name or
                                            img_file.stem == Path(img_name).stem
                                        ):
                                            images_info.append({
                                                'relative_path': src,
                                                'actual_path': str(img_file)
                                            })
                                            logger.info(f"匹配图片: {src} -> {img_file.name}")
                                            break
                                break

                    # 转换Markdown为HTML
                    md_html = _markdown_to_html(md_content, images_info)
            except Exception as e:
                logger.warning(f"MD内容解析失败: {e}")
                md_html = "<p>Markdown内容加载失败</p>"
    else:
        # PPT文件：加载页面图片
        if upload_dir.exists():
            images = sorted(upload_dir.glob("page_*.png"))
            for img in images:
                page_images.append(_image_to_base64(str(img)))

    # 生成HTML
    html = _render_generic_template(
        filename=filename,
        total_pages=total_pages,
        analysis_time=analysis_time,
        model_name=model_name,
        overall=overall,
        page_images=page_images,
        md_html=md_html,
        file_type=file_type
    )

    # 保存文件
    output_dir = Path(settings.h5_export_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{analysis_id}.html"

    # 确保使用UTF-8编码写入，不使用BOM
    with open(output_path, "w", encoding="utf-8", errors="xmlcharrefreplace") as f:
        f.write(html)

    logger.info(f"通用分析H5报告已生成: {output_path}")
    return str(output_path)


def _render_left_content(file_type: str, page_images: list, md_html: str) -> str:
    """根据文件类型渲染左侧内容"""
    if file_type == "md":
        # MD文件：显示格式化的Markdown HTML
        return md_html
    else:
        # PPT文件：显示页面图片
        return ''.join([
            f'<img src="{img}" class="slide-img" alt="第{i+1}页" onclick="openModal(this.src)">'
            for i, img in enumerate(page_images)
        ])


def _render_generic_template(filename: str, total_pages: int, analysis_time: str,
                             model_name: str, overall: dict, page_images: list,
                             md_html: str, file_type: str) -> str:
    """渲染通用分析HTML模板"""

    # 使用传入的filename作为显示文件名
    display_filename = filename

    # 生成左侧内容
    left_content_html = _render_left_content(file_type, page_images, md_html)

    # 提取关键数据
    executive_summary = overall.get("executive_summary", {})
    data_quality = overall.get("data_quality_check", {})
    critical_issues = overall.get("critical_business_issues", [])
    root_causes = overall.get("root_cause_synthesis", {})
    logic_review = overall.get("logic_chain_review", {})
    strategy = overall.get("strategy_effectiveness", {})
    highlights = overall.get("replicable_highlights", [])
    recommendations = overall.get("recommendations", {})
    info_gaps = overall.get("information_gaps", {})
    final = overall.get("final_assessment", {})

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{display_filename} - 通用商业分析报告</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
    background: #f5f5f5;
    color: #333;
    line-height: 1.6;
}}
.container {{
    display: flex;
    height: 100vh;
}}
.left-panel {{
    width: 45%;
    background: #fff;
    overflow-y: auto;
    border-right: 1px solid #e0e0e0;
    display: flex;
    flex-direction: column;
}}
.right-panel {{
    width: 55%;
    background: #fafafa;
    overflow-y: auto;
    padding: 20px;
}}
.header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    text-align: center;
}}
.header h1 {{ font-size: 22px; margin-bottom: 10px; }}
.header .meta {{ font-size: 13px; opacity: 0.9; }}
.slides-container {{
    padding: 20px;
    flex: 1;
}}
.slide-img {{
    width: 100%;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 20px;
    cursor: pointer;
    transition: transform 0.2s;
}}
.slide-img:hover {{ transform: scale(1.02); }}
.chapter-card {{
    background: white;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    cursor: pointer;
    transition: box-shadow 0.3s, transform 0.2s;
    border-left: 4px solid #667eea;
}}
.chapter-card:hover {{
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    transform: translateX(4px);
}}
.chapter-level-2 {{
    margin-left: 20px;
    border-left-color: #a78bfa;
    background: #faf9ff;
}}
.chapter-title {{
    font-weight: 600;
    color: #667eea;
    font-size: 16px;
    line-height: 1.6;
}}
.chapter-level-2 .chapter-title {{
    font-size: 14px;
    color: #7c3aed;
}}
.chapter-preview {{
    color: #666;
    font-size: 14px;
    line-height: 1.6;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}}
.modal {{
    display: none;
    position: fixed;
    z-index: 9999;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.9);
}}
.modal-content {{
    margin: auto;
    display: block;
    max-width: 90%;
    max-height: 90%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}}
.close-modal {{
    position: absolute;
    top: 20px;
    right: 40px;
    color: #fff;
    font-size: 40px;
    font-weight: bold;
    cursor: pointer;
}}
.close-modal:hover {{ color: #ccc; }}
.section {{
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}
.section-title {{
    font-size: 18px;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #667eea;
}}
.subsection-title {{
    font-size: 16px;
    font-weight: 600;
    color: #555;
    margin: 15px 0 10px 0;
}}
.field-label {{
    font-weight: 600;
    color: #666;
    margin-top: 12px;
    margin-bottom: 6px;
}}
.field-value {{
    background: #f8f9fa;
    padding: 12px;
    border-radius: 4px;
    border-left: 3px solid #667eea;
}}
.list-item {{
    background: #f8f9fa;
    padding: 10px 15px;
    margin: 8px 0;
    border-radius: 4px;
    border-left: 3px solid #764ba2;
}}
.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 8px;
}}
.badge-high {{ background: #fee; color: #c00; }}
.badge-medium {{ background: #ffeaa7; color: #d63031; }}
.badge-low {{ background: #dfe6e9; color: #2d3436; }}
.issue-card {{
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 15px;
    margin: 12px 0;
}}
.issue-title {{
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
}}
.issue-field {{
    margin: 6px 0;
    font-size: 14px;
}}
.issue-field strong {{
    color: #666;
    min-width: 80px;
    display: inline-block;
}}
.recommendation-card {{
    background: #f0f9ff;
    border-left: 4px solid #667eea;
    padding: 12px;
    margin: 10px 0;
}}
.highlight-card {{
    background: #f0fdf4;
    border-left: 4px solid #10b981;
    padding: 12px;
    margin: 10px 0;
}}
.status-good {{ color: #10b981; font-weight: 600; }}
.status-warning {{ color: #f59e0b; font-weight: 600; }}
.status-bad {{ color: #ef4444; font-weight: 600; }}
.page-link {{
    color: #667eea;
    text-decoration: underline;
    cursor: pointer;
    font-weight: 600;
}}
.page-link:hover {{
    color: #764ba2;
    text-decoration: underline;
}}
/* 表格全屏查看模态框 */
.table-modal {{
    display: none;
    position: fixed;
    inset: 0;
    z-index: 10000;
    background: rgba(0,0,0,0.9);
    align-items: center;
    justify-content: center;
    padding: 20px;
}}
.table-modal.open {{
    display: flex;
}}
.table-modal-content {{
    background: white;
    border-radius: 12px;
    max-width: 95vw;
    max-height: 95vh;
    overflow: auto;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    position: relative;
    padding: 20px;
}}
.table-modal-content table {{
    font-size: 14px;
    min-width: 100%;
    margin: 0;
}}
.table-modal-content th {{
    padding: 12px 16px;
    position: sticky;
    top: 0;
    background: #f8fafc;
    z-index: 10;
}}
.table-modal-content td {{
    padding: 12px 16px;
}}
.table-modal .close-btn {{
    position: fixed;
    top: 20px;
    right: 30px;
    color: white;
    font-size: 40px;
    font-weight: bold;
    cursor: pointer;
    z-index: 10001;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    transition: background 0.3s;
}}
.table-modal .close-btn:hover {{
    background: rgba(255,255,255,0.3);
}}

/* 表格容器添加点击提示 */
.table-wrap {{
    position: relative;
    cursor: pointer;
}}
.table-wrap::after {{
    content: "🔍 点击表格放大查看";
    position: absolute;
    bottom: 8px;
    right: 8px;
    background: rgba(102, 126, 234, 0.9);
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
}}
.table-wrap:hover::after {{
    opacity: 1;
}}

/* 图片放大模态框 */
.image-modal {{
    display: none;
    position: fixed;
    inset: 0;
    z-index: 10000;
    background: rgba(0,0,0,0.95);
    align-items: center;
    justify-content: center;
    padding: 20px;
}}
.image-modal.open {{
    display: flex;
}}
.image-modal img {{
    max-width: 95vw;
    max-height: 95vh;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}}
.image-modal .close-btn {{
    position: fixed;
    top: 20px;
    right: 30px;
    color: white;
    font-size: 40px;
    font-weight: bold;
    cursor: pointer;
    z-index: 10001;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    transition: background 0.3s;
}}
.image-modal .close-btn:hover {{
    background: rgba(255,255,255,0.3);
}}

</style>
</head>
<body>
<div class="container">
    <div class="left-panel">
        <div class="header">
            <h1>📊 {display_filename}</h1>
            <div class="meta">{total_pages} {'页' if file_type == 'ppt' else '章节'} · {analysis_time} · {model_name}</div>
        </div>
        <div class="slides-container">
            {left_content_html}
        </div>
    </div>

    <div class="right-panel">
        <!-- 执行摘要 -->
        <div class="section">
            <div class="section-title">📋 执行摘要</div>
            <div class="field-label">整体结论</div>
            <div class="field-value">{executive_summary.get('overall_conclusion', '无数据')}</div>

            <div class="field-label">业绩表现</div>
            <div class="field-value">{executive_summary.get('business_performance', '无数据')}</div>

            <div class="field-label">报告质量</div>
            <div class="field-value">{executive_summary.get('report_quality', '无数据')}</div>
        </div>

        <!-- 核心经营问题 -->
        <div class="section">
            <div class="section-title">⚠️ 核心经营问题（按重要性排序）</div>
            {_render_critical_issues(critical_issues)}
        </div>

        <!-- 根因综合分析 -->
        <div class="section">
            <div class="section-title">🎯 根因综合分析</div>
            {_render_root_causes(root_causes)}
        </div>

        <!-- 策略有效性评估 -->
        <div class="section">
            <div class="section-title">📈 策略有效性评估</div>
            {_render_strategy(strategy)}
        </div>

        <!-- 可复制亮点 -->
        {_render_highlights(highlights)}

        <!-- 改进建议 -->
        <div class="section">
            <div class="section-title">💡 改进建议</div>
            {_render_recommendations(recommendations)}
        </div>

        <!-- 数据质量检查 -->
        <div class="section">
            <div class="section-title">🔍 数据质量检查</div>
            {_render_data_quality(data_quality)}
        </div>

        <!-- 逻辑链审查 -->
        <div class="section">
            <div class="section-title">🔗 逻辑链审查</div>
            {_render_logic_review(logic_review)}
        </div>

        <!-- 信息缺口 -->
        {_render_info_gaps(info_gaps)}

        <!-- 最终评估 -->
        <div class="section">
            <div class="section-title">✅ 最终评估</div>
            {_render_final_assessment(final)}
        </div>
    </div>
</div>

<!-- 图片放大模态框 -->
<div id="imageModal" class="modal" onclick="closeModal()">
    <span class="close-modal">&times;</span>
    <img class="modal-content" id="modalImage">
</div>

<script>
function openModal(src) {{
    document.getElementById('imageModal').style.display = 'block';
    document.getElementById('modalImage').src = src;
}}

function closeModal() {{
    document.getElementById('imageModal').style.display = 'none';
}}

// 跳转到指定页面并居中显示
function scrollToPage(pageNum) {{
    const slides = document.querySelectorAll('.slide-img');
    if (pageNum > 0 && pageNum <= slides.length) {{
        const targetSlide = slides[pageNum - 1];
        const leftPanel = document.querySelector('.left-panel');
        const slidesContainer = document.querySelector('.slides-container');

        // 计算目标位置：让该图片在可视区域居中
        const slideOffsetTop = targetSlide.offsetTop - slidesContainer.offsetTop;
        const leftPanelHeight = leftPanel.clientHeight;
        const slideHeight = targetSlide.clientHeight;
        const headerHeight = document.querySelector('.header').clientHeight;

        // 居中滚动位置 = 图片顶部 - (视口高度 - 图片高度) / 2 - header高度
        const scrollPosition = slideOffsetTop - (leftPanelHeight - slideHeight) / 2 + headerHeight;

        leftPanel.scrollTo({{
            top: Math.max(0, scrollPosition),
            behavior: 'smooth'
        }});

        // 高亮效果
        targetSlide.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.8)';
        setTimeout(() => {{
            targetSlide.style.boxShadow = '';
        }}, 2000);
    }}
}}

// ESC键关闭
document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeModal();
}});

// 页面加载完成后，自动将分析内容中的"第X页"转换为可点击链接
document.addEventListener('DOMContentLoaded', function() {{
    const rightPanel = document.querySelector('.right-panel');
    if (rightPanel) {{
        // 匹配"第X页"、"第X-Y页"等模式
        rightPanel.innerHTML = rightPanel.innerHTML.replace(/第(\\d+)页/g, function(match, pageNum) {{
            return '<span class="page-link" onclick="scrollToPage(' + pageNum + ')">' + match + '</span>';
        }});
    }}
}});
</script>
<!-- 表格放大模态框 -->
<div class="table-modal" id="tableModal" onclick="closeTableModal()">
  <span class="close-btn" onclick="closeTableModal()">&times;</span>
  <div class="table-modal-content" id="tableModalContent" onclick="event.stopPropagation()">
  </div>
</div>

<!-- 图片放大模态框(MD左侧图片专用，独立id避免与PPT模态框冲突) -->
<div class="image-modal" id="imageModalMd" onclick="closeImageModal()">
  <span class="close-btn" onclick="closeImageModal()">&times;</span>
  <img id="imageModalImg" src="" alt="" onclick="event.stopPropagation()">
</div>

<script>
// 表格放大功能
function openTableModal(tableWrap) {{
  const table = tableWrap.querySelector('table');
  if (!table) return;

  const modal = document.getElementById('tableModal');
  const modalContent = document.getElementById('tableModalContent');

  // 克隆表格到模态框
  modalContent.innerHTML = '';
  const tableClone = table.cloneNode(true);
  modalContent.appendChild(tableClone);

  // 显示模态框
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeTableModal() {{
  const modal = document.getElementById('tableModal');
  modal.classList.remove('open');
  document.body.style.overflow = 'auto';
}}

// 图片放大功能
function openImageModal(imgSrc) {{
  const modal = document.getElementById('imageModalMd');
  const modalImg = document.getElementById('imageModalImg');

  modalImg.src = imgSrc;
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeImageModal() {{
  const modal = document.getElementById('imageModalMd');
  modal.classList.remove('open');
  document.body.style.overflow = 'auto';
}}

// ESC键关闭模态框
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') {{
    closeTableModal();
    closeImageModal();
  }}
}});
</script>

</body>
</html>"""


def _render_data_quality(data: dict) -> str:
    """渲染数据质量检查"""
    consistency = data.get("data_consistency", {})
    completeness = data.get("data_completeness", {})
    reasonableness = data.get("data_reasonableness", {})

    html = []

    # 数据一致性
    status = consistency.get("status", "")
    status_class = "status-good" if "一致" in status else ("status-warning" if "矛盾" in status else "status-bad")
    html.append(f'<div class="subsection-title">数据一致性: <span class="{status_class}">{status}</span></div>')
    conflicts = consistency.get("major_conflicts", [])
    if conflicts:
        for c in conflicts:
            html.append(f'<div class="list-item">⚠️ {c}</div>')

    # 数据完整性
    status = completeness.get("status", "")
    status_class = "status-good" if "完整" in status else ("status-warning" if "部分" in status else "status-bad")
    html.append(f'<div class="subsection-title">数据完整性: <span class="{status_class}">{status}</span></div>')
    missing = completeness.get("critical_missing", [])
    if missing:
        for m in missing:
            html.append(f'<div class="list-item">❌ {m}</div>')

    # 数据合理性
    status = reasonableness.get("status", "")
    status_class = "status-good" if "合理" in status else ("status-warning" if "存在" in status else "status-bad")
    html.append(f'<div class="subsection-title">数据合理性: <span class="{status_class}">{status}</span></div>')
    anomalies = reasonableness.get("anomalies", [])
    if anomalies:
        for a in anomalies:
            html.append(f'<div class="list-item">⚠️ {a}</div>')

    return '\n'.join(html)


def _render_critical_issues(issues: list) -> str:
    """渲染核心经营问题"""
    if not issues:
        return '<div class="field-value">未识别到关键问题</div>'

    html = []
    for issue in issues:
        issue_id = issue.get("issue_id", "")
        title = issue.get("issue_title", "")
        desc = issue.get("issue_description", "")
        evidence = issue.get("evidence", "")
        nature = issue.get("nature", "")
        root_cause = issue.get("root_cause", "")
        impact = issue.get("impact", "低")
        urgency = issue.get("urgency", "低")

        # 修复badge显示：分别判断影响度和紧急度
        impact_class = "badge-high" if impact == "高" else ("badge-medium" if impact == "中" else "badge-low")
        urgency_class = "badge-high" if urgency == "高" else ("badge-medium" if urgency == "中" else "badge-low")

        impact_badge = f'<span class="badge {impact_class}">影响:{impact}</span>'
        urgency_badge = f'<span class="badge {urgency_class}">紧急:{urgency}</span>'

        html.append(f'''
        <div class="issue-card">
            <div class="issue-title">问题 {issue_id}: {title} {impact_badge} {urgency_badge}</div>
            <div class="issue-field"><strong>问题描述:</strong> {desc}</div>
            <div class="issue-field"><strong>事实依据:</strong> {evidence}</div>
            <div class="issue-field"><strong>问题性质:</strong> {nature}</div>
            <div class="issue-field"><strong>根本原因:</strong> {root_cause}</div>
        </div>
        ''')

    return '\n'.join(html)


def _render_root_causes(data: dict) -> str:
    """渲染根因综合分析"""
    common_causes = data.get("common_root_causes", [])
    internal_external = data.get("internal_vs_external", {})

    html = []

    if common_causes:
        html.append('<div class="subsection-title">共性根因</div>')
        for cause in common_causes:
            rc = cause.get("root_cause", "")
            level = cause.get("level", "")
            explanation = cause.get("explanation", "")
            html.append(f'''
            <div class="list-item">
                <strong>{level}:</strong> {rc}<br>
                <span style="color: #666; font-size: 14px;">{explanation}</span>
            </div>
            ''')

    if internal_external:
        html.append('<div class="subsection-title">内外部因素分离</div>')
        external = internal_external.get("external_factors", [])
        internal = internal_external.get("internal_factors", [])
        bias = internal_external.get("attribution_bias", "")

        if external:
            html.append('<div class="field-label">外部不可控因素:</div>')
            for e in external:
                html.append(f'<div class="list-item">🌐 {e}</div>')

        if internal:
            html.append('<div class="field-label">内部可控因素:</div>')
            for i in internal:
                html.append(f'<div class="list-item">🏢 {i}</div>')

        if bias:
            html.append(f'<div class="field-label">归因偏差:</div><div class="field-value">{bias}</div>')

    return '\n'.join(html)


def _render_logic_review(data: dict) -> str:
    """渲染逻辑链审查"""
    html = []

    review_to_plan = data.get("review_to_plan_coherence", {})
    status = review_to_plan.get("status", "")
    status_class = "status-good" if "贯通" in status else ("status-warning" if "部分" in status else "status-bad")
    html.append(f'<div class="subsection-title">复盘→规划逻辑: <span class="{status_class}">{status}</span></div>')
    disconnects = review_to_plan.get("disconnects", [])
    if disconnects:
        for d in disconnects:
            html.append(f'<div class="list-item">⚠️ {d}</div>')

    goal_strategy = data.get("goal_strategy_action_alignment", {})
    status = goal_strategy.get("status", "")
    status_class = "status-good" if "对齐" in status else ("status-warning" if "部分" in status else "status-bad")
    html.append(f'<div class="subsection-title">目标→策略→行动对齐: <span class="{status_class}">{status}</span></div>')
    gaps = goal_strategy.get("gaps", [])
    if gaps:
        for g in gaps:
            html.append(f'<div class="list-item">⚠️ {g}</div>')

    opportunity = data.get("opportunity_strategy_match", {})
    status = opportunity.get("status", "")
    status_class = "status-good" if "匹配" in status else ("status-warning" if "部分" in status else "status-bad")
    html.append(f'<div class="subsection-title">机会→策略匹配: <span class="{status_class}">{status}</span></div>')
    mismatches = opportunity.get("mismatches", [])
    if mismatches:
        for m in mismatches:
            html.append(f'<div class="list-item">⚠️ {m}</div>')

    return '\n'.join(html)


def _render_strategy(data: dict) -> str:
    """渲染策略有效性"""
    html = []

    current = data.get("current_strategy_review", [])
    if current:
        html.append('<div class="subsection-title">现有策略复盘</div>')
        for s in current:
            strategy = s.get("strategy", "")
            effectiveness = s.get("effectiveness", "")
            reason = s.get("reason", "")
            html.append(f'''
            <div class="list-item">
                <strong>{strategy}</strong> - {effectiveness}<br>
                <span style="color: #666; font-size: 14px;">{reason}</span>
            </div>
            ''')

    planned = data.get("planned_strategy_assessment", [])
    if planned:
        html.append('<div class="subsection-title">规划策略评估</div>')
        for s in planned:
            strategy = s.get("strategy", "")
            feasibility = s.get("feasibility", "")
            target = s.get("target_problem", "")
            match = s.get("match_degree", "")
            risks = s.get("risks", [])
            html.append(f'''
            <div class="list-item">
                <strong>{strategy}</strong> - {feasibility}<br>
                <span style="color: #666; font-size: 14px;">
                针对问题: {target}<br>
                匹配度: {match}
                {f"<br>风险: {', '.join(risks)}" if risks else ""}
                </span>
            </div>
            ''')

    system_eval = data.get("strategy_system_evaluation", "")
    if system_eval:
        html.append(f'<div class="subsection-title">策略体系评价</div><div class="field-value">{system_eval}</div>')

    return '\n'.join(html)


def _render_highlights(highlights: list) -> str:
    """渲染可复制亮点"""
    if not highlights:
        return ''

    html = ['<div class="section"><div class="section-title">✨ 可复制亮点</div>']

    for h in highlights:
        highlight = h.get("highlight", "")
        why_good = h.get("why_good", "")
        methodology = h.get("methodology", "")
        conditions = h.get("replication_conditions", "")
        value = h.get("value", "")

        html.append(f'''
        <div class="highlight-card">
            <div style="font-weight: 600; margin-bottom: 8px;">{highlight}</div>
            <div style="font-size: 14px; color: #666;">
                <div><strong>为什么好:</strong> {why_good}</div>
                <div><strong>方法论:</strong> {methodology}</div>
                <div><strong>复制条件:</strong> {conditions}</div>
                <div><strong>复制价值:</strong> {value}</div>
            </div>
        </div>
        ''')

    html.append('</div>')
    return '\n'.join(html)


def _render_recommendations(data: dict) -> str:
    """渲染改进建议"""
    html = []

    short_term = data.get("short_term_actions", [])
    if short_term:
        html.append('<div class="subsection-title">短期措施（30-90天）</div>')
        for action in short_term:
            priority = action.get("priority", "")
            target = action.get("target_issue", "")
            act = action.get("action", "")
            objective = action.get("objective", "")
            owner = action.get("owner", "")
            timeline = action.get("timeline", "")
            impact = action.get("expected_impact", "")

            html.append(f'''
            <div class="recommendation-card">
                <div style="font-weight: 600; margin-bottom: 6px;">优先级 {priority}: {target}</div>
                <div style="font-size: 14px;">
                    <div><strong>措施:</strong> {act}</div>
                    <div><strong>目标:</strong> {objective}</div>
                    <div><strong>责任主体:</strong> {owner}</div>
                    <div><strong>时间:</strong> {timeline}</div>
                    <div><strong>预期效果:</strong> {impact}</div>
                </div>
            </div>
            ''')

    long_term = data.get("long_term_mechanisms", [])
    if long_term:
        html.append('<div class="subsection-title">长期机制建设</div>')
        for mech in long_term:
            mechanism = mech.get("mechanism", "")
            purpose = mech.get("purpose", "")
            path = mech.get("implementation_path", "")
            criteria = mech.get("success_criteria", "")

            html.append(f'''
            <div class="recommendation-card">
                <div style="font-weight: 600; margin-bottom: 6px;">{mechanism}</div>
                <div style="font-size: 14px;">
                    <div><strong>目的:</strong> {purpose}</div>
                    <div><strong>实施路径:</strong> {path}</div>
                    <div><strong>成功标准:</strong> {criteria}</div>
                </div>
            </div>
            ''')

    return '\n'.join(html)


def _render_info_gaps(data: dict) -> str:
    """渲染信息缺口"""
    missing = data.get("critical_missing_info", [])
    verification = data.get("verification_needed", [])

    if not missing and not verification:
        return ''

    html = ['<div class="section"><div class="section-title">❓ 信息缺口</div>']

    if missing:
        html.append('<div class="subsection-title">关键缺失信息</div>')
        for m in missing:
            html.append(f'<div class="list-item">❌ {m}</div>')

    if verification:
        html.append('<div class="subsection-title">需补充验证</div>')
        for v in verification:
            html.append(f'<div class="list-item">⚠️ {v}</div>')

    html.append('</div>')
    return '\n'.join(html)


def _render_final_assessment(data: dict) -> str:
    """渲染最终评估"""
    html = []

    strengths = data.get("key_strengths", [])
    if strengths:
        html.append('<div class="subsection-title">核心亮点</div>')
        for s in strengths:
            html.append(f'<div class="list-item">✅ {s}</div>')

    weaknesses = data.get("key_weaknesses", [])
    if weaknesses:
        html.append('<div class="subsection-title">关键问题</div>')
        for w in weaknesses:
            html.append(f'<div class="list-item">❌ {w}</div>')

    verdict = data.get("one_sentence_verdict", "")
    if verdict:
        html.append(f'<div class="subsection-title">一句话总评</div><div class="field-value">{verdict}</div>')

    return '\n'.join(html)
