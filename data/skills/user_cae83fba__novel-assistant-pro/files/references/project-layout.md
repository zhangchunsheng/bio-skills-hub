# 项目目录结构

> 用户首次创建小说项目时使用。如用户已有目录结构，以用户为准，不强行重构。

## 默认项目结构

```text
{project-root}/
├── memory/
│   └── novels/
│       └── {novel-slug}.md          # 记忆文件（每部作品独立）
├── novels/
│   └── {novel-slug}/
│       ├── chapters/
│       │   ├── chapter-001.md
│       │   └── chapter-002.md
│       ├── drafts/                   # 草稿
│       ├── backups/                  # 章节备份
│       │   └── chapter-001.backup-20260909-120000.md
│       ├── characters/               # 人物档案（可选）
│       ├── meta.json                 # 项目元数据
│       └── README.md                 # 项目说明
└── references/
    └── {novel-slug}/                 # 流派/平台调性引用（可选）
```

## 命名规范

| 类别 | 命名规则 | 示例 |
|---|---|---|
| 项目目录 | 英文、小写、短横线 | `city-hunter`、`star-port-end` |
| 章节文件 | `chapter-NNN.md`（3 位补零） | `chapter-001.md` |
| 章节备份 | `chapter-NNN.backup-YYYYMMDD-HHMMSS.md` | `chapter-001.backup-20260909-120000.md` |
| 记忆文件 | `{novel-slug}.md` | `star-port-end.md` |
| 人物档案 | `{character-name}.md` | `lin-che.md`、`gu-wen.md` |
| 草稿 | `chapter-NNN.draft-N.md` | `chapter-001.draft-1.md` |

## docx 工作流命名（与中文出版排版对齐）

如需对接 `02 本技能生态 工作区/写作马拉松/作品/` 或 `20 OPC 项目/10 写作马拉松/`，章节文件可使用：

```
第N章-标题.docx
```

详见 `references/chapter-rename.md`。

## meta.json 结构

```json
{
  "title": "星港尽头",
  "slug": "star-port-end",
  "type": "科幻悬疑",
  "platform": "起点中文网",
  "narrative_pov": "第三人称有限视角",
  "target_word_count": 200000,
  "current_chapter": 8,
  "created_at": "2026-09-01T10:00:00Z",
  "updated_at": "2026-09-09T18:00:00Z",
  "memory_file": "memory/novels/star-port-end.md",
  "chapter_dir": "novels/star-port-end/chapters/",
  "backup_dir": "novels/star-port-end/backups/",
  "language": "zh-CN",
  "tags": ["科幻", "悬疑", "无限轮回"]
}
```

## 与中文出版排版的对接

章节文件最终交付为 docx 时，应满足：

- 宋体正文（中文）
- 黑体标题（一级 / 二级）
- 首行缩进 2 字符
- 1.5 倍行距
- 章节标题居中或加粗
- 段落之间不空行

详见 `references/export-to-docx.md`。
