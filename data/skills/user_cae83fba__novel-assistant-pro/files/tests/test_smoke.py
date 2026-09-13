#!/usr/bin/env python3
"""
test_smoke.py - smoke test 自动化用例

> 用于安装或升级后的基础验收。运行 `python3 -m pytest tests/test_smoke.py` 验证。

每个测试用例都对应 smoke-test-prompts.md 中的一条。
"""

import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / 'scripts'

REQUIRED_FILES = [
    'SKILL.md',
    '_meta.json',
    'README.md',
    'AGENTS.md',
    'CHANGELOG.md',
    'LICENSE',
]

REQUIRED_DIRS = ['references', 'scripts', 'examples']


class TestRequiredFiles(unittest.TestCase):
    """测试必需文件。"""

    def test_required_files_exist(self):
        for f in REQUIRED_FILES:
            path = SKILL_DIR / f
            self.assertTrue(path.exists(), f"缺少必需文件：{f}")


class TestRequiredDirs(unittest.TestCase):
    """测试必需目录。"""

    def test_required_dirs_exist(self):
        for d in REQUIRED_DIRS:
            path = SKILL_DIR / d
            self.assertTrue(path.exists(), f"缺少必需目录：{d}")


class TestSkillMetadata(unittest.TestCase):
    """测试 SKILL.md 元数据。"""

    def test_yaml_frontmatter_present(self):
        skill_md = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(skill_md.startswith('---'), 'YAML front matter 缺失')

    def test_meta_json_valid(self):
        import json
        meta_path = SKILL_DIR / '_meta.json'
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            self.assertIn('name', meta)
            self.assertIn('version', meta)
            self.assertIn('license', meta)


class TestReferencesCompleteness(unittest.TestCase):
    """测试 references/ 文件完整性。"""

    def test_genres_present(self):
        genres_dir = SKILL_DIR / 'references' / 'genres'
        if genres_dir.exists():
            genres = list(genres_dir.glob('*.md'))
            self.assertGreaterEqual(len(genres), 6, f"流派模板不足 6 个：{len(genres)}")

    def test_platforms_present(self):
        platforms_dir = SKILL_DIR / 'references' / 'platforms'
        if platforms_dir.exists():
            platforms = list(platforms_dir.glob('*.md'))
            self.assertGreaterEqual(len(platforms), 5, f"平台调性卡不足 5 个：{len(platforms)}")

    def test_anti_ai_present(self):
        anti_ai_dir = SKILL_DIR / 'references' / 'anti-ai'
        if anti_ai_dir.exists():
            files = list(anti_ai_dir.glob('*.md'))
            self.assertGreaterEqual(len(files), 3, f"去 AI 腔模块不足 3 个文件：{len(files)}")


class TestScriptsExecutable(unittest.TestCase):
    """测试脚本可执行。"""

    def test_all_scripts_have_shebang(self):
        scripts_dir = SKILL_DIR / 'scripts'
        if not scripts_dir.exists():
            self.skipTest('scripts/ 不存在')

        for script in scripts_dir.glob('*.py'):
            if script.name == '__init__.py':
                continue
            with open(script, 'r', encoding='utf-8') as f:
                first_line = f.readline()
            self.assertTrue(
                first_line.startswith('#!'),
                f"脚本缺少 shebang：{script.name}"
            )


class TestAntiAIScore(unittest.TestCase):
    """测试 AI 痕迹扫描脚本。"""

    def test_clean_text_scores_high(self):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "anti_ai_scan",
                SCRIPTS_DIR / "anti-ai-scan.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            self.skipTest(f"无法加载 anti_ai_scan: {e}")

        clean_text = """林澈接手案件。她打开档案，发现一个陈年的秘密。

证据不会消失，只会被人放错地方。这是她一直相信的话。

顾闻从门外走进来。她抬起头，看着他。

「你来了。」她说。

「我来了。」他说。"""
        results = []
        for trace_id in range(1, 11):
            result = module.scan_trace(clean_text, trace_id)
            results.append(result)
        total_penalty = sum(r['penalty'] for r in results)
        final_score = max(0, 10 - total_penalty)
        # 干净文本应得高分（> 6）
        self.assertGreaterEqual(final_score, 6)


if __name__ == '__main__':
    unittest.main()
