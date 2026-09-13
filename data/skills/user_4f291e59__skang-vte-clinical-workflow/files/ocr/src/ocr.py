import json
import os
import subprocess
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageOps
from rapidocr_onnxruntime import RapidOCR
from statistics import median


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def pdf_to_images(pdf_path: str, dpi: int = 300) -> list[Image.Image]:
    """Convert each PDF page to a PIL image."""
    doc = fitz.open(pdf_path)
    images = []
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    try:
        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
    finally:
        doc.close()
    return images


def image_file_to_image(image_path: str) -> Image.Image:
    """Read an image file, normalize EXIF orientation, and convert to RGB."""
    with Image.open(image_path) as img:
        return ImageOps.exif_transpose(img).convert("RGB")


def init_ocr_engine():
    """Initialize the local OCR engine."""
    return init_ocr_backend("rapidocr")


def init_ocr_backend(engine_name: str = "rapidocr"):
    """Initialize the selected local OCR backend."""
    normalized = (engine_name or "rapidocr").lower()
    if normalized == "auto":
        try:
            return _init_paddleocr_backend()
        except Exception:
            try:
                return _init_easyocr_backend()
            except Exception:
                return {"name": "rapidocr", "engine": RapidOCR()}
    if normalized == "paddleocr":
        return _init_paddleocr_backend()
    if normalized == "easyocr":
        return _init_easyocr_backend()
    if normalized == "rapidocr":
        return {"name": "rapidocr", "engine": RapidOCR()}
    raise ValueError(f"Unsupported OCR engine: {engine_name}")


def _init_paddleocr_backend():
    return {"name": "paddleocr", "engine": PaddleOCRBackend()}


class PaddleOCRBackend:
    """Keep the isolated PP-OCRv5 process alive across a batch."""

    def __init__(self):
        skill_root = Path(__file__).resolve().parent.parent
        python_exe = skill_root / ".venv-paddleocr" / "Scripts" / "python.exe"
        worker = skill_root / "scripts" / "paddleocr_worker.py"
        if not python_exe.exists():
            raise RuntimeError(
                "PaddleOCR 隔离环境未安装。请按 SKILL.md 的 PaddleOCR 安装命令初始化。"
            )
        if not worker.exists():
            raise RuntimeError(f"PaddleOCR worker 不存在：{worker}")

        env = os.environ.copy()
        env.setdefault("PADDLE_PDX_MODEL_SOURCE", "BOS")
        env.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        self.process = subprocess.Popen(
            [str(python_exe), str(worker)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=env,
            creationflags=creationflags,
        )
        ready_line = self.process.stdout.readline() if self.process.stdout else ""
        try:
            ready = json.loads(ready_line)
        except json.JSONDecodeError as exc:
            self.close()
            raise RuntimeError("PaddleOCR worker 启动失败，未返回就绪信息。") from exc
        if not ready.get("ready"):
            self.close()
            raise RuntimeError("PaddleOCR worker 未能初始化 PP-OCRv5。")

    def recognize(self, image: Image.Image):
        temp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_path = temp_file.name
            image.save(temp_path, format="PNG")
            request = json.dumps({"image_path": temp_path}, ensure_ascii=False)
            if not self.process.stdin or not self.process.stdout:
                raise RuntimeError("PaddleOCR worker 通信管道不可用。")
            self.process.stdin.write(request + "\n")
            self.process.stdin.flush()
            response_line = self.process.stdout.readline()
            if not response_line:
                raise RuntimeError("PaddleOCR worker 意外退出。")
            response = json.loads(response_line)
            if not response.get("ok"):
                raise RuntimeError(response.get("error", "PaddleOCR 识别失败"))
            return response.get("result", [])
        finally:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)

    def close(self):
        process = getattr(self, "process", None)
        if not process or process.poll() is not None:
            return
        try:
            if process.stdin:
                process.stdin.write('{"command":"shutdown"}\n')
                process.stdin.flush()
            process.wait(timeout=5)
        except Exception:
            process.terminate()

    def __del__(self):
        self.close()


def _init_easyocr_backend():
    try:
        import easyocr
    except ImportError as exc:
        raise RuntimeError("EasyOCR is not installed. Run: python -m pip install easyocr") from exc

    use_gpu = str(__import__("os").environ.get("MEDICAL_OCR_GPU", "")).lower() in {"1", "true", "yes"}
    reader = easyocr.Reader(["ch_sim", "en"], gpu=use_gpu, verbose=False)
    return {"name": "easyocr", "engine": reader}


def recognize_image(engine, image) -> list[tuple[str, float]]:
    """Recognize a single image and return text lines with confidence scores."""
    if isinstance(image, Image.Image):
        original_image = image
    else:
        original_image = Image.fromarray(image)

    result = _run_ocr(engine, original_image)
    if not result:
        return []

    original_lines = rebuild_reading_order(result)
    if not _looks_sideways(result):
        return original_lines

    candidates = [original_lines]

    rotated_90 = original_image.rotate(90, expand=True)
    rotated_90_result = _run_ocr(engine, rotated_90)
    if rotated_90_result:
        candidates.append(rebuild_reading_order(rotated_90_result))

    if _score_reading_order(candidates[-1]) <= _score_reading_order(original_lines):
        for degrees in (-90, 180):
            rotated = original_image.rotate(degrees, expand=True)
            rotated_result = _run_ocr(engine, rotated)
            if rotated_result:
                candidates.append(rebuild_reading_order(rotated_result))

    return max(candidates, key=_score_reading_order)


def _run_ocr(engine, image: Image.Image):
    if isinstance(engine, dict) and engine.get("name") == "easyocr":
        return _run_easyocr(engine["engine"], image)
    if isinstance(engine, dict) and engine.get("name") == "paddleocr":
        return engine["engine"].recognize(image)

    rapidocr_engine = engine["engine"] if isinstance(engine, dict) else engine
    result, _ = rapidocr_engine(np.array(image))
    return result or []


def _run_easyocr(reader, image: Image.Image):
    result = reader.readtext(np.array(image), detail=1, paragraph=False)
    normalized = []
    for box, text, confidence in result or []:
        normalized.append((box, text, confidence))
    return normalized


def _looks_sideways(raw_result) -> bool:
    """Detect pages photographed sideways by OCR box geometry."""
    ratios = []
    for item in raw_result:
        box = item[0]
        xs = [float(point[0]) for point in box]
        ys = [float(point[1]) for point in box]
        width = max(1.0, max(xs) - min(xs))
        height = max(1.0, max(ys) - min(ys))
        ratios.append(height / width)
    if not ratios:
        return False
    return median(ratios) > 2.0


def rebuild_reading_order(raw_result) -> list[tuple[str, float]]:
    """Rebuild natural reading order and merge fragments from the same line.

    RapidOCR coordinates are usually useful, but some outpatient photos return
    skewed or perspective-transformed boxes. In those cases a single column-first
    ordering can start from footer/lab fragments and drop the apparent first page.
    Build several plausible orders and choose the one that best resembles a
    complete outpatient record.
    """
    entries = []
    for item in raw_result:
        box, text, confidence = item[0], str(item[1]).strip(), float(item[2])
        if not text:
            continue
        xs = [float(point[0]) for point in box]
        ys = [float(point[1]) for point in box]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        height = max(1.0, y_max - y_min)
        entries.append(
            {
                "text": text,
                "confidence": confidence,
                "x_min": x_min,
                "x_max": x_max,
                "x_center": (x_min + x_max) / 2,
                "y_min": y_min,
                "y_max": y_max,
                "y_center": (y_min + y_max) / 2,
                "height": height,
                "index": len(entries),
            }
        )

    if not entries:
        return []

    candidates = [
        _page_block_order(entries),
        _raw_order(entries),
        _row_major_order(entries),
        _column_major_order(entries),
    ]
    return max(candidates, key=_score_reading_order)


def _raw_order(entries: list[dict]) -> list[tuple[str, float]]:
    return [(entry["text"], entry["confidence"]) for entry in sorted(entries, key=lambda e: e["index"])]


def _page_block_order(entries: list[dict]) -> list[tuple[str, float]]:
    """Read multiple paper sheets in one photo as page blocks, then concatenate.

    The user often photographs one patient's 1-5 paper pages together. OCR engines
    may interleave lines with the same vertical position across adjacent sheets.
    Splitting by page-like x-center clusters first keeps each sheet intact.
    """
    blocks = _group_page_blocks(entries)
    if len(blocks) < 2:
        return []

    rebuilt = []
    for block in _sort_page_blocks(blocks):
        for entry in sorted(block, key=lambda e: e["index"]):
            rebuilt.append((entry["text"], entry["confidence"]))
    return rebuilt


def _group_page_blocks(entries: list[dict]) -> list[list[dict]]:
    if len(entries) < 12:
        return [entries]

    page_width = max(e["x_max"] for e in entries) - min(e["x_min"] for e in entries)
    x_gap_threshold = max(110.0, page_width * 0.06)

    blocks = []
    current = []
    for entry in sorted(entries, key=lambda e: e["x_center"]):
        if current and entry["x_center"] - current[-1]["x_center"] > x_gap_threshold:
            blocks.append(current)
            current = []
        current.append(entry)
    if current:
        blocks.append(current)

    meaningful = [block for block in blocks if len(block) >= 6]
    if len(meaningful) < 2:
        return [entries]

    return _merge_small_page_block_fragments(blocks)


def _merge_small_page_block_fragments(blocks: list[list[dict]]) -> list[list[dict]]:
    merged = []
    for block in blocks:
        if not merged:
            merged.append(block)
        elif len(block) < 8 or _blocks_overlap_x(merged[-1], block):
            merged[-1].extend(block)
        else:
            merged.append(block)
    return merged


def _sort_page_blocks(blocks: list[list[dict]]) -> list[list[dict]]:
    decorated = []
    for block in blocks:
        y_min = min(entry["y_min"] for entry in block)
        y_max = max(entry["y_max"] for entry in block)
        decorated.append(
            {
                "block": block,
                "x_min": min(entry["x_min"] for entry in block),
                "y_min": y_min,
                "height": y_max - y_min,
            }
        )

    if not decorated:
        return []

    row_tolerance = max(80.0, median(item["height"] for item in decorated) * 0.25)
    rows = []
    for item in sorted(decorated, key=lambda i: i["y_min"]):
        if rows and abs(item["y_min"] - rows[-1]["y_min"]) <= row_tolerance:
            row = rows[-1]
            row["items"].append(item)
            row["y_min"] = sum(i["y_min"] for i in row["items"]) / len(row["items"])
        else:
            rows.append({"y_min": item["y_min"], "items": [item]})

    sorted_blocks = []
    for row in rows:
        sorted_blocks.extend(item["block"] for item in sorted(row["items"], key=lambda i: i["x_min"]))
    return sorted_blocks


def _blocks_overlap_x(left: list[dict], right: list[dict]) -> bool:
    left_min = min(entry["x_min"] for entry in left)
    left_max = max(entry["x_max"] for entry in left)
    right_min = min(entry["x_min"] for entry in right)
    right_max = max(entry["x_max"] for entry in right)
    overlap = min(left_max, right_max) - max(left_min, right_min)
    if overlap <= 0:
        return False
    smaller_width = min(left_max - left_min, right_max - right_min)
    return overlap / max(1.0, smaller_width) > 0.25


def _row_major_order(entries: list[dict]) -> list[tuple[str, float]]:
    rebuilt = []
    median_height = median(entry["height"] for entry in entries)
    for row in _group_rows(entries):
        items = sorted(row["items"], key=lambda e: e["x_min"])
        text = _join_row_items(items, median_height)
        confidence = sum(item["confidence"] for item in items) / len(items)
        if text:
            rebuilt.append((text, confidence))
    return rebuilt


def _column_major_order(entries: list[dict]) -> list[tuple[str, float]]:
    rebuilt = []
    for column in _group_columns(entries):
        column_height = median(entry["height"] for entry in column)
        for row in _group_rows(column):
            items = sorted(row["items"], key=lambda e: e["x_min"])
            text = _join_row_items(items, column_height)
            confidence = sum(item["confidence"] for item in items) / len(items)
            if text:
                rebuilt.append((text, confidence))
    return rebuilt


READING_ORDER_KEYWORDS = [
    "定点医疗机构",
    "姓名",
    "性别",
    "年龄",
    "身份",
    "就诊时间",
    "科别",
    "主诉",
    "现病史",
    "既往史",
    "过敏史",
    "个人史",
    "家族史",
    "体格检查",
    "辅助检查",
    "诊断",
    "处理",
    "处置意见",
]

BAD_START_PREFIXES = (
    "mg/L",
    "mmol",
    "管腔",
    "最大宽度",
    "累及长度",
    "征象",
    "内未见",
    "屏气后",
    "*D-",
    "D-二聚体",
    "1.",
    "2.",
    "3.",
)

EARLY_ANCHORS = ("姓名", "性别", "年龄", "主诉", "现病史")


def _score_reading_order(lines: list[tuple[str, float]]) -> int:
    texts = [text.strip() for text, _ in lines if text and text.strip()]
    if not texts:
        return -10_000

    joined = "\n".join(texts)
    score = 0
    score += sum(10 for keyword in READING_ORDER_KEYWORDS if keyword in joined)

    for text in texts:
        if any(text.startswith(f"{keyword}：") or text.startswith(f"{keyword}:") for keyword in READING_ORDER_KEYWORDS):
            score += 4

    first_non_metadata = _first_non_metadata_line(texts)
    if first_non_metadata.startswith(BAD_START_PREFIXES):
        score -= 60

    first_twelve = "\n".join(texts[:12])
    if any(anchor in first_twelve for anchor in EARLY_ANCHORS):
        score += 30
    if "主诉" in first_twelve:
        score += 15
    if "现病史" in first_twelve:
        score += 10

    positions = {keyword: joined.find(keyword) for keyword in READING_ORDER_KEYWORDS}
    if positions.get("主诉", -1) != -1 and positions.get("辅助检查", -1) != -1:
        if positions["辅助检查"] < positions["主诉"]:
            score -= 45
    if positions.get("姓名", -1) != -1 and positions.get("主诉", -1) != -1:
        if positions["姓名"] > positions["主诉"]:
            score -= 20
    if positions.get("现病史", -1) != -1 and positions.get("主诉", -1) != -1:
        if positions["现病史"] < positions["主诉"]:
            score -= 10

    return score


def _first_non_metadata_line(texts: list[str]) -> str:
    metadata_prefixes = (
        "打印时间",
        "就诊医师",
        "诊断",
        "第",
        "北京大学",
    )
    for text in texts:
        if text.startswith(metadata_prefixes):
            continue
        return text
    return texts[0]


def _group_columns(entries: list[dict]) -> list[list[dict]]:
    """Group text blocks by rough column to avoid horizontal cross-line joins."""
    x_min = min(entry["x_min"] for entry in entries)
    x_max = max(entry["x_max"] for entry in entries)
    page_width = max(1.0, x_max - x_min)
    column_gap_threshold = max(250.0, page_width * 0.18)

    columns = []
    for entry in sorted(entries, key=lambda e: e["x_min"]):
        if not columns:
            columns.append([entry])
            continue

        current = columns[-1]
        current_anchor = median(item["x_min"] for item in current)
        if entry["x_min"] - current_anchor > column_gap_threshold:
            columns.append([entry])
        else:
            current.append(entry)

    return [sorted(column, key=lambda e: (e["y_center"], e["x_min"])) for column in columns]


def _group_rows(entries: list[dict]) -> list[dict]:
    median_height = median(entry["height"] for entry in entries)
    row_tolerance = max(8.0, median_height * 0.7)

    rows = []
    for entry in sorted(entries, key=lambda e: (e["y_center"], e["x_min"])):
        if rows and abs(entry["y_center"] - rows[-1]["y_center"]) <= row_tolerance:
            row = rows[-1]
            row["items"].append(entry)
            item_count = len(row["items"])
            row["y_center"] = (row["y_center"] * (item_count - 1) + entry["y_center"]) / item_count
            row["height"] = max(row["height"], entry["height"])
        else:
            rows.append(
                {
                    "y_center": entry["y_center"],
                    "height": entry["height"],
                    "items": [entry],
                }
            )
    return rows


def _join_row_items(items: list[dict], median_height: float) -> str:
    """Merge OCR fragments that belong to the same physical text line."""
    pieces = []
    previous = None
    for item in items:
        text = item["text"]
        if previous is not None:
            gap = item["x_min"] - previous["x_max"]
            if gap > median_height * 0.8 and _needs_space(pieces[-1], text):
                pieces.append(" ")
        pieces.append(text)
        previous = item
    return "".join(pieces).strip()


def _needs_space(left: str, right: str) -> bool:
    """Return whether adjacent fragments need an inserted space."""
    if not left or not right:
        return False
    if left[-1] in "（([《“‘:：、" or right[0] in "），。、；;：:）]》”’":
        return False
    if re_match_chinese(left[-1]) and re_match_chinese(right[0]):
        return False
    return True


def re_match_chinese(char: str) -> bool:
    return "\u4e00" <= char <= "\u9fff"


def parse_ocr_result(raw_result, confidence_threshold: float = 0.5) -> list[str]:
    """Parse raw OCR result and keep lines above confidence threshold."""
    if not raw_result:
        return []

    lines = []
    for item in raw_result:
        text = item[1]
        confidence = item[2]
        if confidence >= confidence_threshold:
            lines.append(text)
    return lines
