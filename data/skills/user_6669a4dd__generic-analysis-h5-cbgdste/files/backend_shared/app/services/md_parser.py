"""
云文档(Markdown) 解析服务
支持: 单个MD文件 / ZIP包(MD + 图片)
"""
import os
import re
import zipfile
from pathlib import Path
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class MDParseResult:
    """MD 解析结果"""
    def __init__(self):
        self.total_pages: int = 1  # MD文档统一为1页(整体)
        self.markdown_content: str = ""  # 完整MD内容
        self.images: List[dict] = []  # 提取的图片 [{path, relative_path}]
        self.outline: List[dict] = []  # 大纲 [{index, title, level}]
        self.raw_text: str = ""  # 纯文本(去除MD语法)


def extract_markdown_images(md_content: str) -> List[str]:
    """提取MD中的图片引用路径 ![...](...) """
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(pattern, md_content)
    return [match[1] for match in matches]


def extract_outline(md_content: str) -> List[dict]:
    """提取MD标题生成大纲"""
    outline = []
    lines = md_content.split('\n')
    for idx, line in enumerate(lines, 1):
        # 匹配 # 标题
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            outline.append({
                'index': idx,
                'title': title,
                'level': level
            })
    return outline


def markdown_to_plain_text(md_content: str) -> str:
    """将MD转换为纯文本(简单处理,去除常见语法)"""
    text = md_content
    # 去除图片
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', '', text)
    # 去除链接
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', text)
    # 去除标题#
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 去除粗体/斜体
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    # 去除代码块
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return text.strip()


async def parse_md_file(file_path: str, analysis_id: int, output_dir: str) -> MDParseResult:
    """解析单个MD文件(无图片)"""
    result = MDParseResult()

    with open(file_path, 'r', encoding='utf-8') as f:
        result.markdown_content = f.read()

    result.outline = extract_outline(result.markdown_content)
    result.raw_text = markdown_to_plain_text(result.markdown_content)

    logger.info(f"MD文件解析完成: {file_path}, 标题数: {len(result.outline)}")
    return result


async def parse_md_zip(zip_path: str, analysis_id: int, output_dir: str) -> MDParseResult:
    """解析ZIP包(MD + 图片)"""
    result = MDParseResult()

    # 解压ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    # 查找MD文件
    md_files = list(Path(output_dir).rglob('*.md'))
    if not md_files:
        raise ValueError("ZIP包中未找到MD文件")

    md_file = md_files[0]  # 取第一个MD文件
    logger.info(f"从ZIP中找到MD文件: {md_file}")

    with open(md_file, 'r', encoding='utf-8') as f:
        result.markdown_content = f.read()

    # 提取大纲
    result.outline = extract_outline(result.markdown_content)
    result.raw_text = markdown_to_plain_text(result.markdown_content)

    # 提取图片引用
    image_refs = extract_markdown_images(result.markdown_content)

    # 查找实际的图片文件（支持多种目录名）
    possible_image_dirs = [
        Path(output_dir) / "images",
        Path(output_dir) / "图片和附件",
        Path(output_dir) / "assets",
        Path(output_dir) / "media",
    ]

    images_dir = None
    for img_dir in possible_image_dirs:
        if img_dir.exists():
            images_dir = img_dir
            logger.info(f"找到图片目录: {img_dir}")
            break

    if images_dir:
        for img_ref in image_refs:
            # 解析相对路径，提取文件名
            img_name = Path(img_ref).name
            # URL解码（处理%20等）
            from urllib.parse import unquote
            img_name_decoded = unquote(img_name)

            # 查找对应的图片文件（模糊匹配）
            found = False
            for img_file in images_dir.glob("*"):
                if img_file.is_file() and (
                    img_file.name == img_name or
                    img_file.name == img_name_decoded or
                    img_name_decoded in img_file.name or
                    img_file.stem == Path(img_name_decoded).stem
                ):
                    result.images.append({
                        'relative_path': img_ref,
                        'actual_path': str(img_file),
                        'filename': img_file.name
                    })
                    logger.info(f"匹配图片: {img_ref} -> {img_file.name}")
                    found = True
                    break

            if not found:
                logger.warning(f"未找到图片: {img_ref}")

    logger.info(f"MD ZIP解析完成: 标题数={len(result.outline)}, 图片数={len(result.images)}")
    return result


async def parse_markdown(file_path: str, analysis_id: int) -> MDParseResult:
    """统一MD解析入口"""
    output_dir = os.path.join(os.path.dirname(file_path), str(analysis_id))
    os.makedirs(output_dir, exist_ok=True)

    if file_path.lower().endswith('.zip'):
        return await parse_md_zip(file_path, analysis_id, output_dir)
    elif file_path.lower().endswith('.md'):
        return await parse_md_file(file_path, analysis_id, output_dir)
    else:
        raise ValueError(f"不支持的文件格式: {file_path}")
