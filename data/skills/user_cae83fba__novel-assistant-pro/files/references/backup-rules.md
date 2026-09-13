# 本地备份规则

## 备份目录

```text
novels/{novel-slug}/backups/
```

或

```text
memory/novels/backups/{novel-slug}/
```

## 备份命名

| 类型 | 命名 | 示例 |
|---|---|---|
| 章节备份 | `chapter-NNN.backup-YYYYMMDD-HHMMSS.md` | `chapter-008.backup-20260909-180000.md` |
| 记忆文件备份 | `{novel-slug}.backup-YYYYMMDD-HHMMSS.md` | `star-port-end.backup-20260909-180000.md` |
| 草稿备份 | `chapter-NNN.draft-N.backup-YYYYMMDD-HHMMSS.md` | `chapter-008.draft-1.backup-20260909-180000.md` |

## 自动备份时机

| 时机 | 是否备份 |
|---|---|
| 覆盖已有文件前 | ✓ |
| 每次章节写完后 | ✓ |
| 记忆文件每次修改前 | ✓ |
| 每次压缩前 | ✓（时间戳备份） |
| 用户主动 `Ctrl+Z` 类操作 | ✓ |

## 备份保留策略

```bash
# 默认保留 5 个备份（可通过参数调整）
python3 scripts/compress_novel_memory.py memory/novels/{slug}.md \
  --keep-backups 5

# 不保留任何备份（仅在确认有外部备份时使用）
python3 scripts/compress_novel_memory.py memory/novels/{slug}.md \
  --keep-backups 0

# 保留 20 个备份（长篇项目）
python3 scripts/compress_novel_memory.py memory/novels/{slug}.md \
  --keep-backups 20
```

## 备份恢复

```bash
# 列出所有备份
ls -la novels/{slug}/backups/

# 恢复最新备份
cp novels/{slug}/backups/chapter-008.backup-20260909-180000.md \
   novels/{slug}/chapters/chapter-008.md

# 恢复到指定时间点
# （手动复制对应时间戳的备份）
```

## 跨设备备份

建议同步到云端：

- Baidu 网盘（用户已有账号）
- iCloud Drive（macOS）
- OneDrive（Windows）
- Git 私有仓库（推荐用于版本管理）

详见 `references/idea-vault.md` 与 `references/export-to-docx.md`。

## 打包交付时

打包技能包或导出项目时：

- 必须排除 `backups/` 目录（避免冗余）
- 必须排除 `.DS_Store`、`__pycache__`、`.pytest_cache`
- 仅打包：记忆文件、章节正文、人物档案、项目元数据

详见 `AGENTS.md`。

## 多人协作下的备份

多人协作时，建议：

- 每位协作者本地保留完整 backups/
- 主仓库使用 Git 做版本管理（commit + push）
- 关键节点打 tag（如完成一卷时）
- 冲突解决后立即打 backup

详见 `references/collab-workflow.md`。
