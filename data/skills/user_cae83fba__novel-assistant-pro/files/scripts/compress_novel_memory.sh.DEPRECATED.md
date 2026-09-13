# 旧版 shell 脚本已弃用

macOS 的 BSD sed 与 GNU sed 行为不一致，且 shell 脚本备份策略过于简化、缺少 dry-run。

`compress_novel_memory.py`（v2.0.0）已包含原 shell 脚本全部能力，并新增：

- 兼容章节命名（`## 章节概要` / `## 剧情概要` / `## 章节大纲`）
- 兼容人物关系（`## 人物关系` / `## 人物关系图`）
- 时间戳备份（保留 N 个版本，可通过 `--keep-backups` 控制）
- dry-run 模式（`--dry-run`）
- JSON 报告输出（`--report`）
- 详细错误处理与回滚机制
- macOS / Linux / Windows 三平台兼容

迁移指南：

```bash
# 旧命令
./compress_novel_memory.sh memory/novels/my-novel.md

# 新命令
python3 scripts/compress_novel_memory.py memory/novels/my-novel.md
```
