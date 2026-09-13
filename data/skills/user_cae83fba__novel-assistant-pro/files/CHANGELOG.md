# Changelog

所有版本变更遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范。
版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [2.0.0] - 2026-09-09

### Added
- **开篇留存诊断模块**：first3-retention（钩子强度 / 主角处境 / 欲望与异常 / 信息密度 4 维评分卡）
- **章节节拍规划工具**：chapter-pacing（目标 / 阻力 / 变化 / 反馈 / 钩子 5 要素检查表与打分脚本）
- **风格 DNA 提取与漂移检测**：style-dna-extract.py + style-drift-detect.py
- **去 AI 腔模块**：references/anti-ai/（10 条典型痕迹清单 + 改写示范 + 评分卡）
- **自动续写上下文补全流程**：用户输入从 8 项降至 ≤ 3 项
- **对话状态机**：构思期 / 草稿期 / 修订期 / 完稿期 四态
- **平台调性卡**：番茄小说 / 起点中文网 / 晋江文学城 / 七猫小说 / 微信公众号 / 小红书连载
- **流派模板**：玄幻 / 都市 / 言情 / 悬疑 / 历史 / 科幻
- **新增 12 个自动化脚本**：init-novel-project / validate-novel-memory / chapter-pacing-report / style-dna-extract / style-drift-detect / dialogue-style-check / conflict-detect / export-to-docx / world-rules-lint / relationship-graph / chapter-rename / validate-skill
- **导出 docx 工作流指引**：tencent-docx / pandoc / python-docx 三方案
- **章节命名互转**：chapter-001.md ↔ 第N章-标题.docx
- **多作品切换上下文清理机制**
- **灵感素材库机制**：idea-vault.md
- **协作冲突解决具体流程**：collab-workflow.md
- **敏感内容边界**：sensitive-content.md（≥ 5 条红线）
- **README / AGENTS / CHANGELOG / LICENSE** 4 文档齐备
- **章节节奏自动诊断**：chapter-pacing-report.py
- **静态校验与单元测试**：validate-skill.py + tests/

### Changed
- 主入口 SKILL.md 从 ~500 行精简到 ≤ 200 行
- description 三段式重写（能力 + 典型表达 + 不该触发）
- 触发词从 13 个扩充到 40+ 个
- compress_novel_memory.py 兼容 3 种章节命名别名、2 种伏笔格式
- compress_novel_memory.py 支持 dry-run / report / 时间戳备份
- 续写流程用户输入从 8 项降至 ≤ 3 项
- 记忆文件模板兼容多种章节标题与人物关系图命名

### Deprecated
- compress_novel_memory.sh（迁移至 compress_novel_memory.py）
  - 原因：macOS BSD sed 兼容性差、备份策略简化
  - 迁移：直接使用 `python3 compress_novel_memory.py`

### Fixed
- 修复 YAML `name=novel-assistant` 与 `_meta.json` slug=`novel-assistant-pro` 不一致
- 修复 YAML `version=1.1.0` 与 `_meta.json` `version=1.0.0` 不一致
- 修复 compress 脚本找「剧情概要」但模板写「章节概要」的命名错位
- 修复 shell 脚本在 macOS BSD sed 下的行为差异
- 修复人物关系图 / 章节大纲 / 人物关系命名不一致
- 修复章节数提取误判（「### 早期章节」被算入）
- 修复备份覆盖式策略（无多版本）

### Security
- 写入安全契约文档化（references/write-safety.md 7 条规则）
- 敏感内容边界明确（references/sensitive-content.md ≥ 5 条红线 + 拒答模板）
- 不静默覆盖已有本地文件（覆盖前询问）
- 不写入系统隐藏目录（除非用户明确指定）
- 不把用户作品写入技能包自身目录

## [1.1.0] - 2025-xx-xx（旧版，源包）

### Added
- 多作品并行管理
- 人物对话风格样本库
- 伏笔优先级标记
- 章节备份和记忆压缩建议

## [1.0.3] - 2025-xx-xx（旧版，源包）

### Added
- 基础项目管理能力
- 人物卡、伏笔追踪、时间线管理
- 风格控制模板

## [1.0.0] - 2025-xx-xx（旧版，源包）

### Added
- 初始发布
- 基础 SOP：创建 / 续写 / 检查 / 压缩
