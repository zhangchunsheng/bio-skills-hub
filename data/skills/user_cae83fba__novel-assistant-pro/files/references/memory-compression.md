# 记忆压缩规则

## 三级压缩

| 等级 | 参考条件 | 压缩策略 |
|---|---|---|
| 轻压缩 | 3000-6000 字 | 合并早期章节概要，保留全部人物、世界观和伏笔 |
| 中压缩 | 6000-12000 字 | 精简已解决伏笔、合并支线概要，保留 P1/P2 伏笔 |
| 强压缩 | 12000 字以上 | 只保留主线、核心人物、硬规则、未解决伏笔和关键时间点 |

## 压缩脚本

```bash
# 默认压缩（保留最近 15 章）
python3 scripts/compress_novel_memory.py memory/novels/{slug}.md

# 自定义保留章节数
python3 scripts/compress_novel_memory.py memory/novels/{slug}.md \
  --keep-chapters 20

# 预览压缩效果（不实际写入）
python3 scripts/compress_novel_memory.py memory/novels/{slug}.md \
  --dry-run

# 输出 JSON 报告
python3 scripts/compress_novel_memory.py memory/novels/{slug}.md \
  --report reports/compression-report.json

# 自定义备份保留数
python3 scripts/compress_novel_memory.py memory/novels/{slug}.md \
  --keep-backups 10
```

## 压缩前后必须输出：压缩报告

```markdown
### 压缩报告

- 原始长度：{N} 字
- 压缩后长度：{M} 字
- 压缩率：{百分比}%
- 保留内容：核心人物、世界观硬规则、P1/P2 伏笔、关键时间点
- 合并内容：早期章节概要
- 删除内容：已回收伏笔的详细回收方式
- 风险提示：合并概要可能导致人物细节丢失
```

## 兼容的章节命名

`compress_novel_memory.py` 自动识别以下别名：

- 章节概要：`## 章节概要` / `## 剧情概要` / `## 章节大纲`
- 人物关系：`## 人物关系` / `## 人物关系图`
- 伏笔追踪：`## 伏笔追踪` / `## 未解决伏笔`

## 备份策略

- 默认创建时间戳备份：`memory/novels/{slug}.md.backup-YYYYMMDD-HHMMSS.md`
- 默认保留最近 5 个备份（可通过 `--keep-backups N` 调整）
- `--keep-backups 0` 表示不保留备份（仅在确认当前环境有外部备份时使用）

## 不删除的内容

压缩时，以下内容**绝不删除**：

1. 硬规则（世界观不可违反的规则）
2. P1 伏笔（主线关键伏笔）
3. 核心人物的对话风格样本
4. 关键时间点（影响后续章节的事件）
5. 跨作品引用（如有）

## 何时不压缩

- 记忆文件 < 3000 字
- 用户明确禁止压缩
- 当前正在进行大规模修订（压缩会丢失修订细节）

## 与续写的衔接

压缩后，下一次续写：

1. 自动读取压缩后的记忆文件
2. 必要时询问用户是否需要回看原始备份
3. 续写流程不变

## 跨章节合并策略

```markdown
## 合并早期章节概要

### 早期章节概要（第 1-15 章）

- 第 1 章：林澈接手港口爆炸事故
- 第 2 章：她追查残片来源
- 第 3 章：找到黑匣子碎片，出现顾闻旧识别码
- 第 4 章：内务局警告
- ……共 15 章早期内容已合并

### 第 16 章

林澈首次直接质疑顾闻。

### 第 17 章

顾闻透露部分真相，但保留关键信息。

（保留最近 15 章的完整概要）
```

详见 `scripts/compress_novel_memory.py` 源码。
