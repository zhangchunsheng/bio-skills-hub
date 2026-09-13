import argparse
import os
import re
import sys
from pathlib import Path

os.environ["FLAGS_use_mkldnn"] = "0"

from desensitizer import desensitize_lines
from grouper import group_pages_by_patient
from ocr import (
    SUPPORTED_IMAGE_EXTENSIONS,
    image_file_to_image,
    init_ocr_backend,
    pdf_to_images,
    recognize_image,
)
from output import write_docx, write_markdown
from postprocess import mark_low_confidence_lines, postprocess_patient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="纸质病历批量OCR识别与脱敏工具")
    parser.add_argument("input_path", nargs="?", help="输入路径：PDF、图片或图片文件夹")
    parser.add_argument("--input", dest="input_option", help="输入路径：PDF、图片或图片文件夹")
    parser.add_argument("--output", default="./output", help="输出目录（默认：./output）")
    parser.add_argument(
        "--format",
        default="md",
        choices=["md", "docx"],
        help="输出格式：md 或 docx（默认：md）",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="输入为文件夹时递归处理子文件夹中的图片",
    )
    parser.add_argument(
        "--ocr-engine",
        default="rapidocr",
        choices=["rapidocr", "easyocr", "paddleocr", "auto"],
        help="OCR引擎：rapidocr、easyocr、paddleocr 或 auto（默认：rapidocr；auto优先PP-OCRv5）",
    )
    return parser.parse_args()


def resolve_input(args: argparse.Namespace) -> Path:
    input_value = args.input_option or args.input_path
    if not input_value:
        raise ValueError("请通过 --input 或位置参数提供 PDF、图片或图片文件夹路径")

    input_path = Path(input_value).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"输入路径不存在：{input_path}")
    return input_path


def get_writer(output_format: str):
    return (".md", write_markdown) if output_format == "md" else (".docx", write_docx)


def collect_images(input_dir: Path, recursive: bool) -> list[Path]:
    pattern_iter = input_dir.rglob("*") if recursive else input_dir.glob("*")
    images = [
        path
        for path in pattern_iter
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]
    return sorted(images, key=lambda p: p.name.lower())


def recognize_pages(engine, images: list) -> list[dict]:
    pages = []
    for i, image in enumerate(images):
        print(f"正在识别第 {i + 1}/{len(images)} 页...")
        lines_with_conf = recognize_image(engine, image)
        lines = mark_low_confidence_lines(lines_with_conf)
        pages.append({"pdf_page": i, "lines": lines})
    return pages


def write_patient_record(filepath: Path, pages_lines: list[list[str]], write_fn) -> None:
    paragraphs = postprocess_patient(pages_lines)
    desensitized = desensitize_lines(paragraphs)
    write_fn(str(filepath), desensitized)


def split_lines_by_patient(lines: list[str]) -> list[list[str]]:
    """Split one photographed image when it accidentally contains multiple patients."""
    split_points: list[int] = []
    current_name: str | None = None

    for index, line in enumerate(lines):
        patient_name = _extract_patient_name(line)
        if not patient_name:
            continue

        if current_name is None:
            current_name = patient_name
            continue

        if not _looks_like_same_patient_name(patient_name, current_name):
            split_at = _include_patient_header(lines, index)
            if split_at > 0 and split_at not in split_points:
                split_points.append(split_at)
            current_name = patient_name

    if not split_points:
        return [lines]

    starts = [0] + split_points
    ends = split_points + [len(lines)]
    return [
        lines[start:end]
        for start, end in zip(starts, ends)
        if any(line.strip() for line in lines[start:end])
    ]


def _extract_patient_name(line: str) -> str | None:
    match = re.search(r"姓名[：:\s]*([\u4e00-\u9fff]{1,6})", line)
    if not match:
        return None

    value = match.group(1).strip()
    if value in {"姓名", "性别", "年龄", "身份", "科别"}:
        return None
    return value


def _include_patient_header(lines: list[str], index: int) -> int:
    start = index
    while start > 0 and _is_patient_header_line(lines[start - 1]):
        start -= 1
    return start


def _is_patient_header_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    return any(
        token in stripped
        for token in (
            "病历记录",
            "门诊病历",
            "北京大学",
            "医疗机构",
            "定点医疗机构编码",
            "就诊卡",
            "打印时间",
        )
    )


def _patient_file_suffix(patient_index: int) -> str:
    if 1 <= patient_index <= 26:
        return chr(ord("A") + patient_index - 1)
    return f"-{patient_index}"


def _looks_like_same_patient_name(left: str, right: str | None) -> bool:
    if right is None:
        return False
    if left == right:
        return True
    if len(left) != len(right) or len(left) > 4:
        return False
    return sum(1 for a, b in zip(left, right) if a != b) <= 1


def process_pdf(input_path: Path, output_dir: Path, output_format: str, ocr_engine: str) -> tuple[int, int]:
    ext, write_fn = get_writer(output_format)

    print("正在将PDF转为图片...")
    images = pdf_to_images(str(input_path))
    print(f"共 {len(images)} 页")

    print("正在初始化OCR引擎...")
    engine = init_ocr_backend(ocr_engine)
    pages = recognize_pages(engine, images)

    print("正在按患者分组...")
    groups, unclassified = group_pages_by_patient(pages)

    print("正在处理、脱敏并输出文件...")
    for idx, group in enumerate(groups, start=1):
        pages_lines = [page["lines"] for page in group["pages"]]
        filepath = output_dir / f"病历_{idx:03d}{ext}"
        write_patient_record(filepath, pages_lines, write_fn)

    for idx, page in enumerate(unclassified, start=1):
        filepath = output_dir / "unclassified" / f"未分类_{idx:03d}{ext}"
        write_patient_record(filepath, [page["lines"]], write_fn)

    return len(groups), len(unclassified)


def process_images(image_paths: list[Path], output_dir: Path, output_format: str, ocr_engine: str) -> int:
    ext, write_fn = get_writer(output_format)

    print("正在初始化OCR引擎...")
    engine = init_ocr_backend(ocr_engine)

    record_count = 0
    for idx, image_path in enumerate(image_paths, start=1):
        print(f"正在处理图片 {idx}/{len(image_paths)}：{image_path.name}")
        image = image_file_to_image(str(image_path))
        lines_with_conf = recognize_image(engine, image)
        lines = mark_low_confidence_lines(lines_with_conf)
        patient_groups = split_lines_by_patient(lines)
        for patient_index, patient_lines in enumerate(patient_groups, start=1):
            if len(patient_groups) == 1:
                filepath = output_dir / f"病历_{idx:03d}_{image_path.stem}{ext}"
            else:
                suffix = _patient_file_suffix(patient_index)
                filepath = output_dir / f"病历_{idx:03d}{suffix}_{image_path.stem}{ext}"
            write_patient_record(filepath, [patient_lines], write_fn)
            record_count += 1

    return record_count


def main() -> int:
    args = parse_args()

    try:
        input_path = resolve_input(args)
        output_dir = Path(args.output).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"正在处理：{input_path}")

        if input_path.is_dir():
            image_paths = collect_images(input_path, args.recursive)
            if not image_paths:
                raise ValueError(f"文件夹中未找到支持的图片文件：{input_path}")
            count = process_images(image_paths, output_dir, args.format, args.ocr_engine)
            print("\n处理完成！")
            print(f"共输出 {count} 份病历")
        elif input_path.suffix.lower() == ".pdf":
            group_count, unclassified_count = process_pdf(input_path, output_dir, args.format, args.ocr_engine)
            print("\n处理完成！")
            print(f"共识别 {group_count} 名患者")
            print(f"共 {unclassified_count} 页未分类")
        elif input_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            count = process_images([input_path], output_dir, args.format, args.ocr_engine)
            print("\n处理完成！")
            print(f"共输出 {count} 份病历")
        else:
            supported = ", ".join(sorted(SUPPORTED_IMAGE_EXTENSIONS | {".pdf"}))
            raise ValueError(f"不支持的输入类型：{input_path.suffix}。支持：{supported}")

        print(f"输出目录：{output_dir}")
        return 0
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
