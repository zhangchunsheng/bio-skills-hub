#!/usr/bin/env python3
"""
test_validate_memory.py - validate_novel_memory.py 的单元测试
"""

import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from validate_novel_memory import (
        check_required_sections, check_foreshadowing_ids,
        check_chapter_continuity, check_p1_stale, get_unresolved_by_priority
    )
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    IMPORT_ERROR = str(e)


class TestRequiredSections(unittest.TestCase):
    """测试必填章节检查。"""

    def setUp(self):
        if not IMPORT_OK:
            self.skipTest(f"无法导入 validate_novel_memory：{IMPORT_ERROR}")

    def test_missing_section_detected(self):
        content = "# 测试\n\n## 基本信息\n- 小说名：测试\n"
        issues = check_required_sections(content)
        self.assertTrue(len(issues) > 0)

    def test_all_sections_present(self):
        content = """# 测试

## 基本信息
- 小说名：测试

## 风格规则
- 语言风格：克制

## 世界观规则
### 硬规则
1. 测试

## 主要人物
### 林澈
- 身份

## 人物关系
- A 与 B

## 主线与阶段目标
- 总主线

## 章节概要
### 第1章
测试

## 未解决伏笔
| F001 | P1 | 1 | 测试 | 第2章 | 未回收 |

## 已回收伏笔
| F001 | 2 | 反转 | 是 |

## 时间线
| 1 | 001 | 第一天 | 事件 | 林澈 | 影响 |
"""
        issues = check_required_sections(content)
        self.assertEqual(len(issues), 0)


class TestForeshadowingIDs(unittest.TestCase):
    """测试伏笔 ID 唯一性。"""

    def setUp(self):
        if not IMPORT_OK:
            self.skipTest(f"无法导入 validate_novel_memory：{IMPORT_ERROR}")

    def test_unique_ids(self):
        content = "| F001 | P1 | 1 | 内容1 | 第3章 | 未回收 |\n| F002 | P2 | 2 | 内容2 | 第5章 | 未回收 |"
        issues = check_foreshadowing_ids(content)
        self.assertEqual(len(issues), 0)

    def test_duplicate_ids(self):
        content = "| F001 | P1 | 1 | 内容1 | 第3章 | 未回收 |\n| F001 | P2 | 2 | 内容2 | 第5章 | 未回收 |"
        issues = check_foreshadowing_ids(content)
        self.assertEqual(len(issues), 1)
        self.assertIn('F001', issues[0]['message'])


class TestChapterContinuity(unittest.TestCase):
    """测试章节编号连续性。"""

    def setUp(self):
        if not IMPORT_OK:
            self.skipTest(f"无法导入 validate_novel_memory：{IMPORT_ERROR}")

    def test_continuity(self):
        content = """### 第1章
内容

### 第2章
内容

### 第3章
内容
"""
        issues = check_chapter_continuity(content)
        self.assertEqual(len(issues), 0)

    def test_gap(self):
        content = """### 第1章
内容

### 第3章
内容
"""
        issues = check_chapter_continuity(content)
        self.assertEqual(len(issues), 1)


class TestP1Stale(unittest.TestCase):
    """测试 P1 伏笔长期未推进。"""

    def setUp(self):
        if not IMPORT_OK:
            self.skipTest(f"无法导入 validate_novel_memory：{IMPORT_ERROR}")

    def test_fresh_p1(self):
        content = """## 章节概要

### 第1章
内容

### 第2章
内容

### 第3章
内容

## 未解决伏笔

| F001 | P1 | 1 | 内容 | 第10章 | 未回收 |
"""
        issues = check_p1_stale(content, threshold=10)
        self.assertEqual(len(issues), 0)

    def test_stale_p1(self):
        # 创建 15 章 + 一个埋在第 1 章的 P1
        chapter_section = '\n\n'.join(f'### 第{i}章\n内容' for i in range(1, 16))
        content = f"""## 章节概要

{chapter_section}

## 未解决伏笔

| F001 | P1 | 1 | 内容 | 第20章 | 未回收 |
"""
        issues = check_p1_stale(content, threshold=10)
        self.assertEqual(len(issues), 1)


class TestUnresolvedByPriority(unittest.TestCase):
    """测试未解决伏笔按优先级分组。"""

    def setUp(self):
        if not IMPORT_OK:
            self.skipTest(f"无法导入 validate_novel_memory：{IMPORT_ERROR}")

    def test_grouping(self):
        content = """## 未解决伏笔

| F001 | P1 | 1 | 主线关键 | 第5章 | 未回收 |
| F002 | P2 | 2 | 支线 | 第6章 | 未回收 |
| F003 | P3 | 3 | 氛围 | - | 未回收 |
"""
        result = get_unresolved_by_priority(content)
        self.assertEqual(len(result['P1']), 1)
        self.assertEqual(len(result['P2']), 1)
        self.assertEqual(len(result['P3']), 1)


if __name__ == '__main__':
    unittest.main()
