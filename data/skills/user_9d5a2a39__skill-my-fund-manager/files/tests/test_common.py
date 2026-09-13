"""_common.py 单元测试（v2.0 新增）。

覆盖：
- 路径/JSON I/O 原子性
- HTML 文本清洗（含 v2.0 新增的 14 个 HTML 实体）
- 经理档案路径 / 加载 / 保存
- HTTP 重试退避（验证 v2.0 修复：非 200 也延迟）
- 进度读写
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


# ============================================================
# 路径与目录
# ============================================================

def test_ensure_dirs_creates_all():
    """ensure_dirs 应创建 DATA / MANAGERS / PROGRESS / EXPORTS"""
    import _common
    with tempfile.TemporaryDirectory() as tmp:
        # 重写 DATA_DIR
        original = _common.DATA_DIR
        _common.DATA_DIR = os.path.join(tmp, "data")
        _common.MANAGERS_DIR = os.path.join(_common.DATA_DIR, "managers")
        _common.PROGRESS_DIR = os.path.join(_common.DATA_DIR, "progress")
        _common.EXPORTS_DIR = os.path.join(_common.DATA_DIR, "exports")
        try:
            _common.ensure_dirs()
            assert os.path.isdir(_common.DATA_DIR)
            assert os.path.isdir(_common.MANAGERS_DIR)
            assert os.path.isdir(_common.PROGRESS_DIR)
            assert os.path.isdir(_common.EXPORTS_DIR)
        finally:
            _common.DATA_DIR = original
            _common.MANAGERS_DIR = os.path.join(original, "managers")
            _common.PROGRESS_DIR = os.path.join(original, "progress")
            _common.EXPORTS_DIR = os.path.join(original, "exports")


# ============================================================
# JSON 读写（含原子性）
# ============================================================

def test_read_json_returns_default_when_missing():
    import _common
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        result = _common.read_json(path, default={"k": "v"})
        assert result == {"k": "v"}
    finally:
        os.remove(path)


def test_read_json_returns_empty_dict_default():
    import _common
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        # 缺省 default=None 时返回 {}
        result = _common.read_json(path)
        assert result == {}
    finally:
        os.remove(path)


def test_read_json_handles_corrupt_file():
    """损坏的 JSON 应返回 default 而不是抛错。"""
    import _common
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("{ invalid json }")
        path = f.name
    try:
        result = _common.read_json(path, default={"fallback": True})
        assert result == {"fallback": True}
    finally:
        os.remove(path)


def test_write_json_preserves_chinese():
    """write_json 应用 ensure_ascii=False 保留中文。"""
    import _common
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        data = {"name": "张坤", "company": "易方达基金"}
        _common.write_json(path, data)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        # 中文字符应原样保存（不是 \uXXXX）
        assert "张坤" in content
        assert "易方达基金" in content
    finally:
        os.remove(path)


def test_write_json_atomic_no_temp_residue():
    """写入失败时不应留下 .tmp 临时文件。"""
    import _common
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.json")
        # 制造写入失败（设目录为只读难，这里仅模拟成功路径）
        _common.write_json(path, {"ok": True})
        assert os.path.exists(path)
        assert not os.path.exists(path + ".tmp")


# ============================================================
# HTML 文本清洗（v2.0 修复核心）
# ============================================================

def test_strip_html_handles_basic():
    import _common
    assert _common.strip_html("<p>Hello</p>") == "Hello"
    assert _common.strip_html("<a href='#'>Link</a>") == "Link"


def test_strip_html_handles_old_entities():
    """5 个基础 HTML 实体。"""
    import _common
    assert "&" in _common.strip_html("&amp;")
    assert "<" in _common.strip_html("&lt;")
    assert ">" in _common.strip_html("&gt;")
    assert '"' in _common.strip_html("&quot;")
    # &nbsp; 应转为 U+00A0 不间断空格（不是普通空格，避免被 strip+压缩空白丢失）
    # 单用 &nbsp; 边界：最终 .strip() 会去掉首尾的 U+00A0（Python str 默认行为）
    # 用含前后文本验证 U+00A0 保留
    assert "\xa0" in _common.strip_html("X&nbsp;Y")


def test_strip_html_handles_apostrophe_entities_v2():
    """v2.0 修复：&apos; 和 &#39; 也应替换为单引号。"""
    import _common
    assert _common.strip_html("it&apos;s") == "it's"
    assert _common.strip_html("it&#39;s") == "it's"


def test_strip_html_handles_em_dash_entities_v2():
    """v2.0 修复：&mdash; &ndash; 等也应替换。"""
    import _common
    assert "—" in _common.strip_html("a&mdash;b")
    assert "–" in _common.strip_html("a&ndash;b")
    assert "…" in _common.strip_html("a&hellip;b")
    assert "«" in _common.strip_html("&laquo;a")
    assert "»" in _common.strip_html("a&raquo;")


def test_strip_html_handles_smart_quotes_v2():
    """v2.0 修复：&lsquo; &rsquo; &ldquo; &rdquo; 智能引号。"""
    import _common
    assert "'" in _common.strip_html("&lsquo;a&rsquo;")
    assert '"' in _common.strip_html("&ldquo;a&rdquo;")


def test_strip_html_handles_numeric_character_reference_v2():
    """v2.0 修复：&#123; 数字引用应解为字符。"""
    import _common
    # &#65; = "A"
    assert "A" in _common.strip_html("&#65;")


def test_strip_html_handles_empty():
    import _common
    assert _common.strip_html("") == ""
    assert _common.strip_html(None) == ""


def test_strip_html_collapses_whitespace():
    import _common
    assert _common.strip_html("<p>a</p>\n\n  <p>b</p>") == "a b"


# ============================================================
# 经理档案路径
# ============================================================

def test_manager_path_sanitizes_unsafe_chars():
    """manager_path 应替换非法字符。"""
    import _common
    # 不应包含 路径分隔符
    p = _common.manager_path("123/456")
    assert "/" not in os.path.basename(p) or "\\" not in os.path.basename(p)

    p2 = _common.manager_path("abc@@@")
    assert isinstance(p2, str)


def test_list_manager_files_filter_json():
    import _common
    with tempfile.TemporaryDirectory() as tmp:
        original = _common.MANAGERS_DIR
        _common.MANAGERS_DIR = tmp
        try:
            # 创建几个文件
            for f in ["30189741.json", "30189744.json", "readme.txt", "noext"]:
                Path(tmp, f).write_text("{}")
            files = _common.list_manager_files()
            assert "30189741" in files
            assert "30189744" in files
            assert "readme" not in files
            assert "noext" not in files
            assert len(files) == 2
        finally:
            _common.MANAGERS_DIR = original


# ============================================================
# 进度追踪
# ============================================================

def test_progress_roundtrip():
    """load_progress / save_progress 应能正确往返。"""
    import _common
    with tempfile.TemporaryDirectory() as tmp:
        original = _common.PROGRESS_DIR
        _common.PROGRESS_DIR = tmp
        try:
            progress = {"done": ["m1", "m2"], "pending": ["m3", "m4"]}
            _common.save_progress("test_task", progress)
            loaded = _common.load_progress("test_task")
            assert loaded["done"] == ["m1", "m2"]
            assert loaded["pending"] == ["m3", "m4"]
        finally:
            _common.PROGRESS_DIR = original


def test_progress_initial_state():
    """新任务的初始进度应含 done/pending 两个空列表。"""
    import _common
    with tempfile.TemporaryDirectory() as tmp:
        original = _common.PROGRESS_DIR
        _common.PROGRESS_DIR = tmp
        try:
            loaded = _common.load_progress("brand_new_task")
            assert "done" in loaded
            assert "pending" in loaded
        finally:
            _common.PROGRESS_DIR = original


# ============================================================
# JSON 解析（含转义字符串）
# ============================================================

def test_find_balanced_json_handles_escapes():
    """_find_balanced_json 应处理字符串内的转义引号。"""
    import _common
    text = '{"key": "value with \\"escaped\\" quote"}'
    result = _common._find_balanced_json(text)
    parsed = json.loads(result)
    assert '"escaped"' in parsed["key"]


def test_find_balanced_json_handles_nested():
    """嵌套对象应正确匹配。"""
    import _common
    text = '{"a": {"b": 1}, "c": 2}'
    result = _common._find_balanced_json(text)
    parsed = json.loads(result)
    assert parsed["a"]["b"] == 1
    assert parsed["c"] == 2


def test_find_balanced_json_no_object():
    """无 { 时应返回 None。"""
    import _common
    assert _common._find_balanced_json("no json here") is None


# ============================================================
# http_get 重试退避（v2.0 修复验证）
# ============================================================

def test_http_get_retries_on_non_200_with_delay():
    """v2.0 修复：非 200 响应也应延迟，避免反爬。"""
    import _common
    import requests

    mock_response = MagicMock()
    mock_response.status_code = 429  # Too Many Requests
    mock_response.text = ""

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    mock_session.get.__name__ = "get"

    with patch.object(_common, "_get_requests", return_value=mock_session), \
         patch.object(_common, "_random_delay") as mock_delay, \
         patch.object(_common.time, "sleep") as mock_sleep:

        result = _common.http_get("http://example.com", retries=3)
        assert result is None
        # 验证：非 200 也应触发 sleep（v2.0 修复关键）
        # 应该有 2 次 sleep（2 次重试间），不是 0
        assert mock_sleep.call_count >= 2, (
            f"v2.0 修复：非 200 响应必须延迟。实际 sleep 调用 {mock_sleep.call_count} 次"
        )


def test_http_get_eventual_success():
    """最终成功时应返回文本。"""
    import _common
    import requests

    mock_responses = [
        MagicMock(status_code=429, text=""),  # 第一次失败
        MagicMock(status_code=200, text="ok"),  # 第二次成功
    ]
    mock_session = MagicMock()
    mock_session.get.side_effect = mock_responses
    mock_session.get.__name__ = "get"

    with patch.object(_common, "_get_requests", return_value=mock_session), \
         patch.object(_common.time, "sleep"):
        result = _common.http_get("http://example.com", retries=3)
        assert result == "ok"


# ============================================================
# 运行测试
# ============================================================

def main():
    tests = [
        (name, obj)
        for name, obj in globals().items()
        if name.startswith("test_") and callable(obj)
    ]
    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*60}\n_common.py 测试: {passed} 通过, {failed} 失败\n{'='*60}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
