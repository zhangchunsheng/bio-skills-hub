# 多作品管理

## 每部作品必须独立维护

- 独立记忆文件：`memory/novels/{slug-A}.md` / `memory/novels/{slug-B}.md`
- 独立章节目录：`novels/{slug-A}/chapters/` / `novels/{slug-B}/chapters/`
- 独立备份目录：`novels/{slug-A}/backups/` / `novels/{slug-B}/backups/`
- 独立人物档案：`novels/{slug-A}/characters/` / `novels/{slug-B}/characters/`
- 独立风格约束（每部作品风格 DNA 不同）
- 独立流派/平台调性参考

## 切换作品的 SOP

```text
用户："我现在开始写新作品《YYY》"

技能执行：
  1. 确认当前作品名（防止误切）
     "您正在写的是《XXX》，要切换到《YYY》吗？"
  2. 读取当前作品的 meta.json，确认完成度
     "《XXX》当前进度：第 23 章 / 50 章（46%）"
  3. 清空会话记忆摘要中上一作品的关键设定
     （避免 A 作品设定串到 B 作品）
  4. 询问《YYY》的基本信息
  5. 调用 init-novel-project.py 创建新项目
  6. 切换完成
```

## 反模式（必须避免）

- 把 A 作品的人物写到 B 作品里
- 把 A 作品的硬规则应用到 B 作品
- 把 A 作品的伏笔状态写到 B 作品的章节概要里
- 把 A 作品的风格 DNA 作为 B 作品的基线

## 并行创作的注意事项

```text
场景：用户同时管理《XXX》和《YYY》两部作品

每次操作前必须：
  1. 明确当前作品名（用户或技能主动确认）
  2. 读取对应作品的记忆文件（不是另一个的）
  3. 写入对应作品的目录（不是另一个的）
  4. 备份到对应作品的 backup 目录（不是另一个的）
```

## 自动校验

```bash
# 列出所有作品
python3 scripts/init-novel-project.py --list

# 输出：
# 《XXX》star-port-end    第 23 章 / 50 章  46%
# 《YYY》another-world    第 8 章 / 30 章   27%

# 切换作品
python3 scripts/init-novel-project.py --switch YYY
```

## 多作品的元数据汇总

建议在用户工作区根目录维护一个 `novels-index.md`：

```markdown
# 我的小说项目索引

| 作品 | Slug | 类型 | 平台 | 当前章节 | 总章节 | 进度 | 状态 |
|---|---|---|---|---:|---:|---:|---|
| 星港尽头 | star-port-end | 科幻悬疑 | 起点中文网 | 23 | 50 | 46% | 连载中 |
| 凡人之上 | mortal-ascending | 玄幻 | 番茄小说 | 45 | 100 | 45% | 连载中 |
| 古镇秘事 | ancient-town | 历史悬疑 | 微信公众号 | 12 | 20 | 60% | 完结 |
```

## 跨作品知识迁移（v3.x 预留）

P3-02 跨作品知识迁移：用户授权下，新作品可继承已完结作品的人物原型/势力原型。

当前版本：手动复制（参考 `references/collab-workflow.md` 中的人物迁移流程）。

详见 P3-02。
