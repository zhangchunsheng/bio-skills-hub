#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析 Windows 默认下载目录并生成安全路径片段。

说明：路径解析职责独立于知识查询和文件生成，便于测试与复用。
Author: WangYunL
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


DOWNLOADS_KNOWN_FOLDER_ID = "{374DE290-123F-4565-9164-39C4925E467B}"
INVALID_SEGMENT_PATTERN = re.compile(r"[<>:\"/\\|?*\x00-\x1f]")
RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


class DownloadsPathError(ValueError):
    """表示默认下载目录或路径片段无法安全解析。"""


def safe_path_segment(value: str, field_name: str) -> str:
    """把技术或项目名称转换为 Windows 安全目录名。"""
    segment = INVALID_SEGMENT_PATTERN.sub("_", str(value or "")).strip().rstrip(". ")
    segment = re.sub(r"\s+", " ", segment)
    if not segment or segment in {".", ".."}:
        raise DownloadsPathError(f"{field_name} 无法生成有效目录名。")
    if segment.upper() in RESERVED_WINDOWS_NAMES:
        segment = f"_{segment}"
    return segment[:120].rstrip(". ")


def _registry_downloads_dir() -> Path | None:
    """从 Windows Known Folder 注册表项读取用户下载目录。"""
    if sys.platform != "win32":
        return None
    try:
        import winreg

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            raw_value, _ = winreg.QueryValueEx(key, DOWNLOADS_KNOWN_FOLDER_ID)
    except (ImportError, OSError):
        return None
    expanded = os.path.expandvars(str(raw_value))
    return Path(expanded).expanduser()


def resolve_downloads_dir(override: Path | None = None) -> Path:
    """优先使用显式测试路径，否则自动识别 Windows 默认下载目录。"""
    candidate = override or _registry_downloads_dir() or (Path.home() / "Downloads")
    resolved = candidate.expanduser().resolve()
    if not resolved.exists():
        raise DownloadsPathError(f"下载目录不存在：{resolved}")
    if not resolved.is_dir():
        raise DownloadsPathError(f"下载路径不是目录：{resolved}")
    return resolved

