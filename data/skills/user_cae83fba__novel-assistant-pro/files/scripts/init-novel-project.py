#!/usr/bin/env python3
"""
init-novel-project.py - 初始化小说项目

v2.0.0 新增。命令式创建项目目录、初始化记忆文件、生成 meta.json。

使用：
    python3 init-novel-project.py \\
      --slug star-port-end \\
      --title "星港尽头" \\
      --type "科幻悬疑" \\
      --platform "起点中文网" \\
      --pov "第三人称有限视角" \\
      --output-dir "/Users/.../novels/"
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_STRUCTURE = """
{root}/{slug}/
├── memory/
│   └── novels/
│       └── {slug}.md
├── novels/
│   └── {slug}/
│       ├── chapters/
│       ├── backups/
│       ├── characters/
│       └── meta.json
└── README.md
"""


MEMORY_TEMPLATE = """# 《{title}》记忆文件

> 创建时间：{created_at}
> 最后更新：{created_at}

## 基本信息

- 小说名：{title}
- 类型/题材：{type}
- 目标平台：{platform}
- 叙事人称：{pov}
- 当前章节：未开始
- 当前状态：构思中

## 风格规则

- 语言风格：（待设定）
- 节奏偏好：（待设定）
- 对话比例：（待设定）
- 禁用表达：（待设定）
- 标志性写法：（待设定）
- 平台调性：{platform}

## 世界观规则

### 硬规则（不可违反）

1. （待设定）

### 软规则（可扩展）

1. （待设定）

### 待定规则（未确认）

1. （待设定）

## 主要人物

### 主角：（待设定）

- 身份：
- 年龄/阶段：
- 外显目标：
- 隐性需求：
- 核心矛盾：
- 能力/限制：
- 与主线关系：
- 对话风格：
- 典型台词：
- 不会说的话：

#### 对话风格样本

- 语气关键词：
- 常用表达：
- 典型台词：
- 不会说的话：

#### 声音指纹

- 平均句长：
- 句式偏好：
- 修辞偏好：
- 口头禅：
- 词汇偏好：

## 人物关系

- （待设定）

## 主线与阶段目标

- 总主线：（待设定）
- 当前阶段目标：（待设定）
- 下一阶段目标：（待设定）

## 章节概要

| 章节 | 标题 | 核心事件 | 结尾钩子 | 影响 |
|---|---|---|---|---|
| （待设定） |  |  |  |  |

## 未解决伏笔

| 编号 | 等级 | 埋设章节 | 内容 | 计划回收 | 当前状态 |
|---|---|---|---|---|---|
| （待设定） |  |  |  |  |  |

## 已回收伏笔

| 编号 | 回收章节 | 回收方式 | 是否闭环 |
|---|---|---|---|

## 时间线

| 顺序 | 章节 | 故事时间 | 事件 | 涉及人物 | 影响 |
|---:|---|---|---|---|---|
| （待设定） |  |  |  |  |  |

## 上一章结尾

（暂无）

## 下一章写作目标

（暂无）

## 待确认问题

- （待设定）

## 版本记录

- v2.0.0 初始化：{created_at}
"""


META_JSON_TEMPLATE = {
    "title": None,
    "slug": None,
    "type": None,
    "platform": None,
    "narrative_pov": None,
    "target_word_count": 0,
    "current_chapter": 0,
    "created_at": None,
    "updated_at": None,
    "memory_file": None,
    "chapter_dir": None,
    "backup_dir": None,
    "language": "zh-CN",
    "tags": [],
    "version": "2.0.0",
    "novel_assistant_pro_version": "2.0.0"
}


README_TEMPLATE = """# {title}

> Slug：{slug}
> 类型：{type}
> 平台：{platform}
> 叙事人称：{pov}
> 创建时间：{created_at}

## 项目状态

- 当前章节：未开始
- 当前状态：构思中
- 进度：0%

## 目录结构

```
{slug}/
├── memory/novels/{slug}.md       # 记忆文件
├── novels/{slug}/
│   ├── chapters/                  # 章节正文
│   ├── backups/                   # 章节备份
│   ├── characters/                # 人物档案
│   └── meta.json                  # 项目元数据
└── README.md                      # 本文件
```

## 写作工作流

1. **创建后第一次写**：补充记忆文件中的风格规则、人物设定、世界观硬规则
2. **续写章节**：「续写第 N 章」
3. **检查冲突**：「帮我检查第 N 章有没有冲突」
4. **导出 docx**：「导出第 N 章到 /path/to/第N章-标题.docx」

## 工具栈

- 自动化校验：`novel-assistant-pro/scripts/validate-novel-memory.py`
- 风格 DNA 提取：`novel-assistant-pro/scripts/style-dna-extract.py`
- 导出 docx：`novel-assistant-pro/scripts/export-to-docx.py`

## 维护者

- 由 novel-assistant-pro v2.0.0 自动生成
"""


def create_project(slug: str, title: str, type_: str, platform: str,
                   pov: str, output_dir: str, dry_run: bool = False) -> dict:
    """创建小说项目目录结构。"""
    now = datetime.now(timezone.utc).isoformat()
    root = Path(output_dir).expanduser().resolve()

    report = {
        'success': False,
        'dry_run': dry_run,
        'project_root': None,
        'files_created': [],
        'errors': [],
    }

    project_root = root / slug
    if project_root.exists() and not dry_run:
        report['errors'].append(f'项目目录已存在：{project_root}')
        return report

    paths = {
        'memory': root / 'memory' / 'novels' / f'{slug}.md',
        'novels_chapters': project_root / 'chapters',
        'novels_backups': project_root / 'backups',
        'novels_characters': project_root / 'characters',
        'novels_meta': project_root / 'meta.json',
        'project_readme': project_root / 'README.md',
    }

    if dry_run:
        report['success'] = True
        report['project_root'] = str(project_root)
        report['note'] = 'dry-run 模式，未实际创建'
        return report

    try:
        project_root.mkdir(parents=True, exist_ok=True)
        paths['novels_chapters'].mkdir(parents=True, exist_ok=True)
        paths['novels_backups'].mkdir(parents=True, exist_ok=True)
        paths['novels_characters'].mkdir(parents=True, exist_ok=True)

        meta = META_JSON_TEMPLATE.copy()
        meta.update({
            'title': title,
            'slug': slug,
            'type': type_,
            'platform': platform,
            'narrative_pov': pov,
            'created_at': now,
            'updated_at': now,
            'memory_file': str(paths['memory']),
            'chapter_dir': str(paths['novels_chapters']),
            'backup_dir': str(paths['novels_backups']),
        })
        paths['novels_meta'].write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        report['files_created'].append(str(paths['novels_meta']))

        # 记忆文件
        memory_content = MEMORY_TEMPLATE.format(
            title=title, type=type_, platform=platform, pov=pov, created_at=now
        )
        paths['memory'].parent.mkdir(parents=True, exist_ok=True)
        paths['memory'].write_text(memory_content, encoding='utf-8')
        report['files_created'].append(str(paths['memory']))

        # README
        readme_content = README_TEMPLATE.format(
            title=title, slug=slug, type=type_, platform=platform,
            pov=pov, created_at=now
        )
        paths['project_readme'].write_text(readme_content, encoding='utf-8')
        report['files_created'].append(str(paths['project_readme']))

        report['success'] = True
        report['project_root'] = str(project_root)
    except Exception as e:
        report['errors'].append(f'创建失败：{e}')

    return report


def list_projects(output_dir: str) -> list:
    """列出所有已创建的项目。"""
    root = Path(output_dir).expanduser().resolve()
    projects = []
    for meta_path in root.glob('*/meta.json'):
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            projects.append({
                'title': meta.get('title', '未知'),
                'slug': meta.get('slug', '未知'),
                'current_chapter': meta.get('current_chapter', 0),
                'updated_at': meta.get('updated_at', '未知'),
            })
        except Exception:
            continue
    return projects


def main():
    parser = argparse.ArgumentParser(
        description='novel-assistant-pro · 初始化小说项目（v2.0.0）'
    )
    parser.add_argument('--slug', help='项目 slug（英文、小写、短横线）')
    parser.add_argument('--title', help='小说名')
    parser.add_argument('--type', help='类型/题材')
    parser.add_argument('--platform', help='目标平台')
    parser.add_argument('--pov', help='叙事人称')
    parser.add_argument('--output-dir', required=True, help='项目根目录')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际创建')
    parser.add_argument('--list', action='store_true', help='列出所有项目')
    parser.add_argument('--report', type=str, default=None, help='JSON 报告输出路径')

    args = parser.parse_args()

    if args.list:
        projects = list_projects(args.output_dir)
        print(f"=== 项目列表（共 {len(projects)} 个）===")
        for p in projects:
            print(f"  《{p['title']}》（{p['slug']}）- 第 {p['current_chapter']} 章 - {p['updated_at']}")
        return

    if not all([args.slug, args.title, args.type, args.platform, args.pov]):
        print('错误：创建项目需要 --slug / --title / --type / --platform / --pov', file=sys.stderr)
        sys.exit(1)

    report = create_project(
        slug=args.slug,
        title=args.title,
        type_=args.type,
        platform=args.platform,
        pov=args.pov,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
    )

    if report['success']:
        print(f"✓ 项目创建成功：{report['project_root']}")
        for f in report['files_created']:
            print(f"  - {f}")
        if report.get('note'):
            print(f"  [{report['note']}]")
    else:
        print(f"✗ 创建失败：{report['errors']}", file=sys.stderr)
        sys.exit(1)

    if args.report:
        Path(args.report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f"  报告已保存：{args.report}")


if __name__ == '__main__':
    main()
