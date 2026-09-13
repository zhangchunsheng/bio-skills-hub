#!/usr/bin/env python3
"""
test_skill_static.py - 静态校验测试

运行 validate-skill.py 的核心检查项。
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / 'scripts'


class TestValidateSkill(unittest.TestCase):
    """测试 validate-skill.py 的运行结果。"""

    def test_validate_skill_passes(self):
        """运行 validate-skill.py，预期 0 错误。"""
        script = SCRIPTS_DIR / 'validate-skill.py'
        if not script.exists():
            self.skipTest('validate-skill.py 不存在')

        result = subprocess.run(
            [sys.executable, str(script), str(SKILL_DIR)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        # 输出应包含"校验通过"
        self.assertIn('校验通过', result.stdout, f"validate-skill.py 校验失败：\n{result.stdout}\n{result.stderr}")

    def test_validate_skill_json_report(self):
        """验证 JSON 报告可生成。"""
        script = SCRIPTS_DIR / 'validate-skill.py'
        if not script.exists():
            self.skipTest('validate-skill.py 不存在')

        report_path = Path('/tmp/test_validate_report.json')
        result = subprocess.run(
            [sys.executable, str(script), str(SKILL_DIR), '--json', str(report_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if report_path.exists():
            report = json.loads(report_path.read_text(encoding='utf-8'))
            self.assertIn('error_count', report)
            self.assertIn('warning_count', report)


class TestNamingConsistency(unittest.TestCase):
    """测试 SKILL.md 与 _meta.json 的命名一致性。"""

    def test_name_consistent(self):
        import re
        skill_md = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
        meta = json.loads((SKILL_DIR / '_meta.json').read_text(encoding='utf-8'))

        # 提取 YAML 中的 name
        yaml_match = re.search(r'^name:\s*(.+)$', skill_md, re.MULTILINE)
        if yaml_match:
            yaml_name = yaml_match.group(1).strip().strip('"').strip("'")
            self.assertEqual(yaml_name, meta['name'], f"YAML name ({yaml_name}) 与 _meta.json name ({meta['name']}) 不一致")

    def test_version_consistent(self):
        import re
        skill_md = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
        meta = json.loads((SKILL_DIR / '_meta.json').read_text(encoding='utf-8'))

        yaml_match = re.search(r'^version:\s*"?(v?[0-9.]+)"?', skill_md, re.MULTILINE)
        if yaml_match:
            yaml_version = yaml_match.group(1).strip().strip('"')
            # YAML 可能有 "v" 前缀
            yaml_version_clean = yaml_version.lstrip('v')
            self.assertEqual(yaml_version_clean, meta['version'].lstrip('v'),
                             f"YAML version ({yaml_version}) 与 _meta.json version ({meta['version']}) 不一致")


if __name__ == '__main__':
    unittest.main()
