---
name: novel-assistant-pro
version: "2.0.0"
description: 面向长篇小说与多作品创作的项目管理型助手。典型表达：创建小说、写大纲、续写第N章、检查冲突、压缩记忆、提取风格DNA、去AI腔、导出docx、节拍诊断、开篇留存诊断。不适合：一次性短文、营销文案、出版法律审校、敏感题材（成人/政治/宗教等）。触发后可维护人物、世界观、伏笔、时间线、对话风格的一致性，并支持自动续写上下文补全、风格漂移检测、剧情冲突自动预警与本地原稿安全写入。
triggers:
  # 核心创作
  - 小说
  - 章节
  - 续写
  - 写小说
  - 长篇
  - 连载
  - 章节大纲
  - 节拍
  - 开篇
  - 第一章
  # 设定与人设
  - 人物设定
  - 人设
  - 人物卡
  - 世界观
  - 势力
  - 组织
  - 地点
  - 主角
  - 配角
  - 反派
  # 记忆管理
  - 记忆文件
  - 记忆压缩
  - 剧情概要
  - 伏笔
  - 时间线
  - 备份
  # 风格与诊断
  - 风格
  - 文风
  - 去 AI 腔
  - 节拍诊断
  - 开篇留存
  - 风格 DNA
  - 风格漂移
  # 导出与协作
  - 导出 docx
  - 润色
  - 改写
  - 扩写
  - 缩写
  - 协作
  - 灵感
  # 冲突与质量
  - 冲突
  - 剧情冲突
  - 自检
  - 一致性
capabilities:
  - create_novel_project
  - continue_chapter
  - auto_complete_continuation_context
  - manage_character_profiles
  - manage_worldbuilding
  - track_foreshadowing
  - track_timeline
  - preserve_dialogue_style
  - detect_plot_conflicts
  - compress_novel_memory
  - backup_chapters
  - manage_multiple_works
  - first3_retention_diagnosis
  - chapter_pacing_planning
  - style_dna_extract
  - style_drift_detect
  - anti_ai_prose
  - platform_tone_adapter
  - init_novel_project
  - validate_novel_memory
  - export_to_docx
  - chapter_rename
author: 小浣熊肖恩
license: MIT-0
tags:
  - writing
  - fiction
  - novel
  - longform
  - continuity
  - worldbuilding
  - memory-management
  - style-control
  - pacing
  - multi-work
---

# novel-assistant-pro · 小说创作助手

## 一句话定位

帮助用户把长篇小说从「临时续写」升级为「可持续管理的创作项目」：在生成章节前先校准设定，在创作过程中维护人物声音、世界观规则、伏笔和时间线，在写入本地文件时保护原稿安全。

## 适合谁

- 正在写连载小说、长篇小说或系列短篇的创作者。
- 同时管理多部作品、多个主角或复杂世界观的用户。
- 希望 AI 不只是代写，而是帮助维护设定、章节连贯性和伏笔回收的用户。
- 多人协作写作团队，需要统一人物、世界观和剧情口径。
- 参加写作马拉松等限时创作比赛、需要快速建立项目并稳定产出的用户。

## 不适合谁

- 只想要一次性生成短文、作文或营销文案的用户。
- 不希望建立任何本地项目文件或长期记忆文件的用户。
- 需要出版级法律审校、版权审查或敏感内容判断的场景。
- 成人内容、暴力血腥、政治宗教敏感题材、政治不正确叙事。

## 5 分钟上手

```text
Step 1：告诉我你想写什么
  「我想写一部{类型}长篇，主角是{身份}，核心看点是{爽点/反转/悬念}」

Step 2：我会问你 5 个问题（首次创建时）
  - 目标读者
  - 平台风格（番茄小说/起点中文网/晋江文学城/微信公众号/小红书连载/其他）
  - 叙事人称
  - 预期篇幅
  - 保存目录

Step 3：我生成基础设定
  - 主题与核心冲突
  - 主要人物卡（含对话风格样本）
  - 世界观硬规则
  - 前三章大纲（含节拍卡）

Step 4：你确认后我落盘
  - 创建项目目录
  - 写入记忆文件
  - 生成 meta.json

Step 5：进入续写循环
  每次续写只需说"续写第N章"，其他上下文我自动读。
```

## 触发方式

**应当触发**：

- 「创建小说」「写一部长篇」「帮我建立设定」
- 「续写第 N 章」「接着写」「补写章节结尾」
- 「检查冲突」「有没有人物设定矛盾」「伏笔漏了哪些」
- 「压缩记忆」「记忆文件太长了」
- 「风格 DNA」「文风漂移了」「去 AI 腔」
- 「导出 docx」「润色」「改写」「扩写」
- 「节拍诊断」「开篇留存诊断」

**不应当触发**：

- 「帮我写辞职信/小红书连载文案/营销文案」
- 「写一首古诗/词」
- 「分析判决书/合同」
- 「给这段代码加注释」
- 「讲个笑话/脑筋急转弯」
- 任何不属于长篇小说创作的项目管理任务。

## 核心 SOP

### 1. 创建新小说项目

```text
识别用户输入 → 进入[构思期]
  ├─ 追问基本信息（≤ 5 项）
  ├─ 输出设定草案（主题/冲突/人物/世界观/前三章大纲）
  ├─ 用户确认
  ├─ 调用 scripts/init-novel-project.py 创建项目
  └─ 进入[草稿期]
```

首轮必收集：作品名、类型/题材、目标读者、平台风格、叙事人称、主角、核心爽点/看点、禁写内容或雷区、保存目录。详见 `references/project-layout.md` 与 `references/novel-memory-template.md`。

### 2. 续写章节（自动上下文补全）

```text
用户："续写第 N 章" 或 "接着写"
  ↓
技能自动执行：
  1. locate project → 读 meta.json 确认当前作品
  2. read memory → 读记忆文件
  3. read prev chapter → 读 chapter-(N-1).md 末段
  4. analyze → 列未解决 P1 伏笔 / 涉及人物 / 硬规则 / 平台调性
  5. ask user ≤ 3 项缺失 → 仅问用户没提供的（一般是"本章目标"或"特殊要求"）
  6. generate chapter → 生成正文
  7. self-check → 自检卡 + AI 痕迹分 + 节拍分
  8. write safe → 文件存在则询问覆盖/另存/取消（write-safety.md 契约）
  9. backup → chapter-N.backup.md 自动生成
  10. update memory → 自动追加本章概要到记忆文件
```

详见 `references/write-safety.md`、`references/style-control.md`、`references/anti-ai/checklist.md`。

### 3. 检查与诊断

```text
触发："检查冲突 / 节拍诊断 / 开篇留存 / 风格漂移"
  ↓
自动调用对应模块：
  - 剧情冲突：references/conflict-detection.md + scripts/conflict-detect.py
  - 节拍诊断：references/pacing/chapter-pacing.md + scripts/chapter-pacing-report.py
  - 开篇留存：references/first3-retention/checklist.md
  - 风格漂移：references/style-dna.md + scripts/style-drift-detect.py
  - 对白风格：references/character-card.md + scripts/dialogue-style-check.py
  ↓
输出报告 → 用户选择改写/接受/搁置
```

### 4. 记忆压缩与导出

```text
触发："压缩记忆 / 导出 docx"
  ↓
压缩：scripts/compress_novel_memory.py [--dry-run] [--report report.json]
  - 自动按章节概要/剧情概要/章节大纲别名识别
  - 时间戳备份，保留 N 个版本
  - JSON 报告输出

导出：references/export-to-docx.md（三方案：tencent-docx / pandoc / python-docx）
```

## 输出契约

| 输出类型 | 格式 | 文件命名 | 写入策略 |
|---|---|---|---|
| 章节正文 | Markdown | `chapter-NNN.md` 或 `第N章-标题.docx` | 文件存在 → 三选一：覆盖/另存/取消 |
| 记忆文件 | Markdown | `memory/novels/{novel-slug}.md` | 同上 |
| 人物卡 | Markdown | 记忆文件内嵌 或 `characters/{name}.md` | 同上 |
| 备份 | Markdown | `*.backup-YYYYMMDD-HHMMSS.md` | 自动生成 |
| 诊断报告 | Markdown / JSON | `reports/{type}-{date}.md` 或 `.json` | 增量追加 |
| 导出 docx | 二进制 | `第N章-标题.docx` | 用户指定路径 |

## 质量门禁（自检 checklist）

完成小说任务前自检以下项目：

- [ ] 是否确认了作品名和当前章节？
- [ ] 是否调用 `scripts/validate-novel-memory.py` 校验过记忆文件？
- [ ] 是否读取了记忆文件中的硬规则、伏笔、人物对话风格？
- [ ] 是否避免了人物设定漂移（声音指纹偏离 < 20%）？
- [ ] 是否检查了世界观硬规则？
- [ ] 是否追踪了 P1/P2 伏笔？
- [ ] 是否输出了节拍卡（目标/阻力/变化/反馈/钩子）？
- [ ] 是否输出了 AI 痕迹分（< 3 为合格）？
- [ ] 是否说明了可能的剧情冲突？
- [ ] 是否保护了已有本地文件（覆盖前询问）？
- [ ] 是否生成了时间戳备份？
- [ ] 是否更新了记忆文件中的章节概要与伏笔状态？

## 异常处理（failover 契约）

| 异常类型 | 检测方式 | 处理方案 |
|---|---|---|
| 记忆文件格式不符 | `validate-novel-memory.py` | 输出错误位置 + 修复建议，不写入 |
| 章节编号冲突 | `validate-novel-memory.py` | 列出冲突章节 + 询问用户 |
| 伏笔 ID 重复 | `validate-novel-memory.py` | 自动重命名 + 提示用户 |
| 文件已存在 | `write-safety.md` 契约 | 三选一：覆盖/另存/取消 |
| 写入失败 | try-except | 保留完整正文在对话 + 提示手动复制 |
| 备份失败 | try-except | 警告但不阻塞 |
| 压缩后字数异常 | 比对前后 | 自动回滚 + 提示 |
| 风格 DNA 漂移 > 阈值 | `style-drift-detect.py` | 标注段落 + 给出改写建议 |
| 剧情冲突严重 | `conflict-detect.py` | 必须用户确认才能继续 |
| 敏感内容触发 | 关键词扫描（见 `references/sensitive-content.md`） | 拒答 + 转人工 |
| 多作品切换未确认 | 上下文检测 | 强制询问当前作品名 |
| 项目目录不存在 | locate project | 询问用户是否新建 |

## 资源索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `references/project-layout.md` | 项目目录结构 | 创建/迁移项目时 |
| `references/write-safety.md` | 写入安全契约 | 任何文件写入前 |
| `references/novel-memory-template.md` | 记忆文件模板 | 创建/校验记忆时 |
| `references/character-card.md` | 人物卡模板 | 创建/更新人物时 |
| `references/worldbuilding.md` | 世界观管理 | 涉及硬规则时 |
| `references/foreshadowing.md` | 伏笔追踪 | 涉及伏笔时 |
| `references/timeline.md` | 时间线管理 | 涉及时间时 |
| `references/conflict-detection.md` | 剧情冲突检测 | 检查冲突时 |
| `references/style-control.md` | 风格控制模板 | 建立/校验风格时 |
| `references/style-dna.md` | 风格 DNA 提取与校验 | 跨章一致性时 |
| `references/memory-compression.md` | 记忆压缩规则 | 压缩记忆时 |
| `references/backup-rules.md` | 本地备份规则 | 备份前 |
| `references/multi-work-management.md` | 多作品管理 | 切换作品时 |
| `references/collab-workflow.md` | 多人协作流程 | 协作场景 |
| `references/quickstart.md` | 5 分钟上手 | 首次使用 |
| `references/export-to-docx.md` | 导出 docx 三方案 | 导出时 |
| `references/idea-vault.md` | 灵感素材库 | 临时灵感落盘 |
| `references/sensitive-content.md` | 敏感内容边界 | 触发红线判断时 |
| `references/chapter-rename.md` | 章节命名互转 | `chapter-001.md` ↔ `第1章-标题.docx` |
| `references/first3-retention/checklist.md` | 开篇留存诊断 | 新书首章检查 |
| `references/pacing/chapter-pacing.md` | 章节节拍规划 | 每章写前/写后 |
| `references/anti-ai/traces.md` | AI 痕迹清单 | 每章 AI 痕迹检测 |
| `references/anti-ai/rewrites.md` | 改写示范 | 去除 AI 痕迹 |
| `references/anti-ai/checklist.md` | AI 痕迹评分 | 每章出分 |
| `references/genres/xianxia.md` | 玄幻流派模板 | 首次创建玄幻作品 |
| `references/genres/urban.md` | 都市流派模板 | 首次创建都市作品 |
| `references/genres/romance.md` | 言情流派模板 | 首次创建言情作品 |
| `references/genres/mystery.md` | 悬疑流派模板 | 首次创建悬疑作品 |
| `references/genres/historical.md` | 历史流派模板 | 首次创建历史作品 |
| `references/genres/scifi.md` | 科幻流派模板 | 首次创建科幻作品 |
| `references/platforms/tomato.md` | 番茄小说平台调性卡 | 番茄小说连载 |
| `references/platforms/qidian.md` | 起点中文网平台调性卡 | 起点中文网连载 |
| `references/platforms/jinjiang.md` | 晋江文学城平台调性卡 | 晋江文学城连载 |
| `references/platforms/qimao.md` | 七猫小说平台调性卡 | 七猫小说连载 |
| `references/platforms/wechat.md` | 微信公众号调性卡 | 微信公众号连载 |
| `references/platforms/xhs.md` | 小红书连载调性卡 | 小红书连载 |

## 脚本索引

| 脚本 | 用途 | 何时调用 |
|---|---|---|
| `scripts/compress_novel_memory.py` | 记忆文件压缩 | 章节 > 30 或用户主动触发 |
| `scripts/init-novel-project.py` | 命令式创建项目 | 用户给出保存目录时 |
| `scripts/validate-novel-memory.py` | 记忆文件校验 | 每次读写前 |
| `scripts/chapter-pacing-report.py` | 节拍五要素打分 | 每章写后 |
| `scripts/style-dna-extract.py` | 风格指纹提取 | 新书首章写完后 |
| `scripts/style-drift-detect.py` | 风格漂移检测 | 每章写后 |
| `scripts/dialogue-style-check.py` | 对白风格校验 | 每章写后 |
| `scripts/conflict-detect.py` | 剧情冲突自动检测 | 检查冲突时 |
| `scripts/export-to-docx.py` | 导出 docx 封装 | 导出时 |
| `scripts/world-rules-lint.py` | 世界观硬规则自洽校验 | 涉及硬规则时 |
| `scripts/relationship-graph.py` | 人物关系 mermaid 图 | 关系梳理时 |
| `scripts/chapter-rename.py` | 章节命名互转 | 与 docx 工作流衔接时 |

## CHANGELOG

参见 [`CHANGELOG.md`](./CHANGELOG.md)。

## 维护与贡献

参见 [`AGENTS.md`](./AGENTS.md)。

## 许可证

MIT-0（无限制免费使用，详见 [`LICENSE`](./LICENSE)）。
