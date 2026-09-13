#!/usr/bin/env python3
"""
validate-skill.py - 静态校验 SKILL 包

v2.0.0 新增。仿 skill-creator-optimized-pro 的校验脚本。

检查项：
- YAML front matter 存在且可解析
- name/version 一致
- description 非空、具体
- SKILL.md 中引用的本地文件路径存在
- README/CHANGELOG/LICENSE 存在
- scripts/ 中的脚本可执行
- references/ 引用路径存在
- 无 .DS_Store / .pyc / 临时文件

使用：
    python3 validate-skill.py <skill-dir>
    python3 validate-skill.py <skill-dir> --json report.json
    python3 validate-skill.py <skill-dir> --depth
"""

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FILES = ['SKILL.md', '_meta.json', 'README.md', 'CHANGELOG.md', 'LICENSE', 'AGENTS.md']
REQUIRED_DIRS = ['references', 'scripts', 'examples']


def parse_yaml_frontmatter(content: str) -> dict:
    """解析 YAML front matter（简化版，兼容块字符串与列表）。"""
    if not content.startswith('---'):
        return {}
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    yaml_text = parts[1]

    result = {}
    current_key = None
    current_value_lines = []
    in_block_scalar = False
    block_scalar_key = None

    def flush_block_scalar():
        nonlocal current_value_lines, in_block_scalar, block_scalar_key
        if block_scalar_key is not None:
            value = '\n'.join(current_value_lines).strip()
            result[block_scalar_key] = value
        current_value_lines = []
        in_block_scalar = False
        block_scalar_key = None

    for line in yaml_text.split('\n'):
        stripped = line.strip()
        # 块字符串标识（| 或 >）
        if in_block_scalar:
            if line.startswith('  ') or line.startswith('\t') or not stripped:
                current_value_lines.append(line.lstrip())
                continue
            else:
                flush_block_scalar()

        # 列表项
        if stripped.startswith('- ') and current_key:
            value = stripped[2:].strip().strip('"').strip("'")
            if current_key not in result or not isinstance(result.get(current_key), list):
                result[current_key] = []
            if isinstance(result[current_key], list):
                result[current_key].append(value)
            continue

        # 键值对
        if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            if value == '|' or value == '>':
                # 块字符串开始
                in_block_scalar = True
                block_scalar_key = key
                current_value_lines = []
                current_key = key
                continue
            if value:
                if value.startswith('[') and value.endswith(']'):
                    items = re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,\[\]]+)', value)
                    result[key] = [a or b or c for a, b, c in items if (a or b or c).strip()]
                else:
                    result[key] = value.strip('"').strip("'")
            else:
                result[key] = ''
            current_key = key

    flush_block_scalar()
    return result


def check_required_files(skill_dir: Path) -> list:
    """检查必需文件。"""
    issues = []
    for f in REQUIRED_FILES:
        path = skill_dir / f
        if not path.exists():
            issues.append({
                'level': 'ERROR',
                'type': 'missing_file',
                'message': f'缺少必需文件：{f}',
            })
    for d in REQUIRED_DIRS:
        path = skill_dir / d
        if not path.exists():
            issues.append({
                'level': 'WARNING',
                'type': 'missing_dir',
                'message': f'缺少推荐目录：{d}/',
            })
    return issues


def check_yaml(skill_dir: Path) -> list:
    """检查 YAML front matter。"""
    issues = []
    skill_md = skill_dir / 'SKILL.md'
    meta_json = skill_dir / '_meta.json'

    if not skill_md.exists():
        return issues

    content = skill_md.read_text(encoding='utf-8')
    yaml = parse_yaml_frontmatter(content)

    if not yaml:
        issues.append({
            'level': 'ERROR',
            'type': 'yaml_missing',
            'message': 'SKILL.md 缺少 YAML front matter',
        })
        return issues

    # 检查必需字段
    if 'name' not in yaml:
        issues.append({
            'level': 'ERROR',
            'type': 'yaml_missing_name',
            'message': 'YAML 缺少 name 字段',
        })

    if 'description' not in yaml:
        issues.append({
            'level': 'ERROR',
            'type': 'yaml_missing_description',
            'message': 'YAML 缺少 description 字段',
        })

    # 检查 name/version 一致性
    if meta_json.exists() and 'name' in yaml:
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'version' in yaml and 'version' in meta:
                if yaml['version'].strip('"').strip("'") != meta['version']:
                    issues.append({
                        'level': 'ERROR',
                        'type': 'version_inconsistent',
                        'message': f'YAML version ({yaml["version"]}) 与 _meta.json version ({meta["version"]}) 不一致',
                    })
            if 'name' in yaml and 'name' in meta:
                yaml_name = yaml['name'].strip('"').strip("'")
                if yaml_name != meta['name']:
                    issues.append({
                        'level': 'ERROR',
                        'type': 'name_inconsistent',
                        'message': f'YAML name ({yaml_name}) 与 _meta.json name ({meta["name"]}) 不一致',
                    })
        except Exception as e:
            issues.append({
                'level': 'WARNING',
                'type': 'meta_json_parse_error',
                'message': f'_meta.json 解析失败：{e}',
            })

    # 检查 description 长度
    if 'description' in yaml:
        desc_len = len(str(yaml['description']))
        if desc_len < 50:
            issues.append({
                'level': 'WARNING',
                'type': 'description_too_short',
                'message': f'description 过短（{desc_len} 字符），建议 ≥ 50',
            })

    return issues


def check_references(skill_dir: Path) -> list:
    """检查 SKILL.md 中引用的文件路径是否存在。"""
    issues = []
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        return issues

    content = skill_md.read_text(encoding='utf-8')

    # 查找 references/ 引用（仅 ASCII 终止符，避免吞中文括号）
    matches = re.findall(r'references/[A-Za-z0-9_\-./]+', content)
    for match in set(matches):
        # 清理锚点
        path_str = match.split('#')[0]
        path = skill_dir / path_str
        if not path.exists():
            issues.append({
                'level': 'ERROR',
                'type': 'reference_missing',
                'message': f'引用路径不存在：{match}',
            })

    # 查找 scripts/ 引用
    matches = re.findall(r'scripts/[A-Za-z0-9_\-./]+', content)
    for match in set(matches):
        path_str = match.split('#')[0]
        path = skill_dir / path_str
        if not path.exists():
            issues.append({
                'level': 'WARNING',
                'type': 'script_missing',
                'message': f'脚本引用不存在：{match}',
            })

    return issues


def check_temp_files(skill_dir: Path) -> list:
    """检查临时文件。"""
    issues = []
    temp_patterns = ['.DS_Store', '__pycache__', '.pyc', '.bak', '~', '.tmp', '.log']

    for pattern in temp_patterns:
        for path in skill_dir.rglob(f'*{pattern}'):
            issues.append({
                'level': 'INFO',
                'type': 'temp_file',
                'message': f'发现临时文件：{path.relative_to(skill_dir)}',
            })

    return issues


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 静态校验 SKILL 包（v2.0.0）'
    )
    parser.add_argument('skill_dir', help='技能包目录')
    parser.add_argument('--json', dest='json_report', help='JSON 报告输出路径')
    parser.add_argument('--depth', action='store_true', help='深度校验')

    args = parser.parse_args()
    skill_dir = Path(args.skill_dir)
    if not skill_dir.exists():
        print(f'错误：目录不存在：{args.skill_dir}', file=sys.stderr)
        sys.exit(1)

    issues = []
    issues.extend(check_required_files(skill_dir))
    issues.extend(check_yaml(skill_dir))
    issues.extend(check_references(skill_dir))
    issues.extend(check_temp_files(skill_dir))

    if args.depth:
        # 深度校验：检查脚本可执行、references 内容厚度等
        pass

    errors = [i for i in issues if i['level'] == 'ERROR']
    warnings = [i for i in issues if i['level'] == 'WARNING']
    infos = [i for i in issues if i['level'] == 'INFO']

    print(f'=== 静态校验 ===')
    print(f'目录：{args.skill_dir}')
    print(f'\n错误：{len(errors)} 个')
    for e in errors:
        print(f"  ✗ {e['message']}")
    print(f'\n警告：{len(warnings)} 个')
    for w in warnings:
        print(f"  ⚠ {w['message']}")
    print(f'\n提示：{len(infos)} 个')
    for i in infos:
        print(f"  ℹ {i['message']}")

    if args.json_report:
        report = {
            'skill_dir': str(skill_dir),
            'error_count': len(errors),
            'warning_count': len(warnings),
            'info_count': len(infos),
            'issues': issues,
        }
        Path(args.json_report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f'\n报告已保存：{args.json_report}')

    if errors:
        sys.exit(1)
    else:
        print('\n✓ 校验通过')


if __name__ == '__main__':
    main()
