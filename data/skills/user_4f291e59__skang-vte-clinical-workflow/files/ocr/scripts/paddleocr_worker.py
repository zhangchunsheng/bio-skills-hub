"""Persistent local PP-OCRv5 worker for the medical-ocr skill."""

from __future__ import annotations

import contextlib
import json
import os
import sys


def _normalize_result(results) -> list[list]:
    normalized: list[list] = []
    for result in results:
        payload = result.json
        data = payload.get("res", payload)
        polygons = data.get("rec_polys") or data.get("dt_polys") or []
        texts = data.get("rec_texts") or []
        scores = data.get("rec_scores") or []
        for polygon, text, score in zip(polygons, texts, scores):
            normalized.append([polygon, str(text), float(score)])
    return normalized


def main() -> int:
    os.environ.setdefault("PADDLE_PDX_MODEL_SOURCE", "BOS")
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

    from paddleocr import PaddleOCR

    # Keep Paddle/PaddleX logs away from the line-oriented JSON protocol.
    with contextlib.redirect_stdout(sys.stderr):
        engine = PaddleOCR(
            lang="ch",
            ocr_version="PP-OCRv5",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device="cpu",
        )

    print(json.dumps({"ready": True}), flush=True)
    for raw_line in sys.stdin:
        try:
            request = json.loads(raw_line)
            if request.get("command") == "shutdown":
                return 0
            image_path = request["image_path"]
            with contextlib.redirect_stdout(sys.stderr):
                results = list(engine.predict(image_path))
            response = {"ok": True, "result": _normalize_result(results)}
        except Exception as exc:  # return a structured error to the parent
            response = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
