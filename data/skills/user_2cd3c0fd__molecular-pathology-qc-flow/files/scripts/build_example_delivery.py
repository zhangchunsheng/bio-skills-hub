#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性生成 Skill 内置的四套分子病理质控交付包。

说明：交付根目录必须不存在；原始示例和用户文件均不会被覆盖。
Author: WangYunL
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from build_qc_bundle import BundleBuildError, build_bundle, file_digest
from qc_flow_model import configure_console_encoding
from query_knowledge import DEFAULT_INDEX


SKILL_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = (
    ("BRAF-V600E", SKILL_ROOT / "assets" / "BRAF-V600E下机质控.json"),
    ("NGS", SKILL_ROOT / "assets" / "NGS通用质控.json"),
    ("FISH-ALK", SKILL_ROOT / "assets" / "FISH-ALK通用质控.json"),
    ("Sanger", SKILL_ROOT / "assets" / "Sanger通用质控.json"),
)


def build_example_delivery(
    output_root: Path, preview: str = "both", index_path: Path = DEFAULT_INDEX
) -> list[Path]:
    """在临时目录生成四套交付物，全部成功后再复制到新目录。"""
    if output_root.exists():
        raise BundleBuildError(f"交付根目录已存在，已停止以避免覆盖：{output_root}")
    if not output_root.parent.exists():
        raise BundleBuildError(f"交付根目录的父目录不存在：{output_root.parent}")

    with TemporaryDirectory(prefix="molecular-qc-examples-") as temporary:
        staging = Path(temporary) / "delivery"
        staging.mkdir()
        generated: list[tuple[str, Path]] = []
        for folder_name, input_path in EXAMPLES:
            bundle_dir = staging / folder_name
            files = build_bundle(input_path, bundle_dir, None, preview, index_path)
            generated.extend((folder_name, path) for path in files)

        readme_path = staging / f"{date.today().isoformat()}-分子病理质控流程图交付说明.md"
        readme_path.write_text(
            "\n".join(
                [
                    "# 分子病理质控流程图交付说明",
                    "",
                    "作者：WangYunL  ",
                    f"生成日期：{date.today().isoformat()}  ",
                    "",
                    "## 一、交付内容",
                    "",
                    "| 目录 | 技术或项目 | 内容 |",
                    "| --- | --- | --- |",
                    "| BRAF-V600E | PCR / BRAF V600E 下机质控 | JSON、Draw.io、质控说明、结构预览、清单 |",
                    "| NGS | NGS 通用质控 | JSON、Draw.io、质控说明、结构预览、清单 |",
                    "| FISH-ALK | FISH / ALK 通用质控 | JSON、Draw.io、质控说明、结构预览、清单 |",
                    "| Sanger | Sanger 通用质控 | JSON、Draw.io、质控说明、结构预览、清单 |",
                    "",
                    "## 二、使用边界",
                    "",
                    "- BRAF 数值只复现用户提供的原流程，不外推为其他试剂或平台标准。",
                    "- NGS、FISH/ALK、Sanger 中待确认规则必须结合当前 SOP、IFU 和验证报告。",
                    "- PNG/SVG 是结构预览，不等同于 diagrams.net 桌面端真实渲染验收。",
                    "- 所有子目录均包含 SHA-256 交付清单，可用于检查文件是否变化。",
                    "",
                    "## 三、原文件保护",
                    "",
                    "本交付目录为新建目录，未修改或覆盖用户原始 BRAF Draw.io。",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        manifest_path = staging / "总交付清单.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "delivery_version": "1.2",
                    "generated_on": date.today().isoformat(),
                    "author": "WangYunL",
                    "bundles": [folder for folder, _ in EXAMPLES],
                    "files": [
                        {
                            "bundle": folder,
                            "path": str(path.relative_to(staging)).replace("\\", "/"),
                            "size": path.stat().st_size,
                            "sha256": file_digest(path),
                        }
                        for folder, path in generated
                    ]
                    + [
                        {
                            "bundle": "root",
                            "path": readme_path.name,
                            "size": readme_path.stat().st_size,
                            "sha256": file_digest(readme_path),
                        }
                    ],
                    "boundary": "结构预览不等同于 diagrams.net 桌面端真实渲染。",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        shutil.copytree(staging, output_root)
    return sorted(output_root.iterdir(), key=lambda path: path.name)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="一次性生成 BRAF、NGS、FISH/ALK、Sanger 四套交付包。")
    parser.add_argument("--output-root", required=True, type=Path, help="必须不存在的新交付根目录")
    parser.add_argument(
        "--preview",
        choices=("none", "svg", "png", "both"),
        default="both",
        help="每套交付包的结构预览格式，默认同时生成 SVG 和 PNG",
    )
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="技术项目知识索引")
    return parser.parse_args()


def main() -> int:
    """执行四套示例交付。"""
    args = parse_args()
    try:
        entries = build_example_delivery(args.output_root, args.preview, args.index)
    except (OSError, BundleBuildError, ValueError) as exc:
        print(f"示例交付生成失败：{exc}", file=sys.stderr)
        return 1
    print(f"四套交付包生成成功：{args.output_root}")
    for path in entries:
        print(f"- {path.name}")
    return 0


if __name__ == "__main__":
    configure_console_encoding()
    raise SystemExit(main())

