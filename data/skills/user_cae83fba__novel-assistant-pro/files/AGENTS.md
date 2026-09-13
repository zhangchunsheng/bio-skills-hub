# AGENTS.md · 维护与贡献规范

## 适用范围

本文件约束 `novel-assistant-pro` 的维护者、贡献者以及下游再分发者的协作流程。

## 文件职责边界

| 文件 | 职责 | 不应做的事 |
|---|---|---|
| `SKILL.md` | 主入口：定位、SOP、契约、门禁、资源索引 | 写长篇模板、详细规则、剧本示例 |
| `references/` | 长内容、模板、规则、范例 | 直接定义 SOP |
| `scripts/` | 可独立运行的自动化 | 业务逻辑散落在主流程中 |
| `examples/` | 演示、smoke test、端到端 demo | 成为正式文档 |
| `tests/` | 单元测试与回归 | 业务规则本身 |
| `_meta.json` | 包元数据（版本/作者/许可） | 业务规则、文档 |

## 修改流程

1. **小修**：直接 PR → review → 合并。
2. **中修**：在 PR 中附带：
   - 改动清单（影响哪些 capability、references、scripts）
   - 验证报告（smoke test 全过）
   - CHANGELOG 更新
3. **大修（结构性升级）**：必须走完整流程：
   - 撰写升级方案 → 用户审阅 → 分阶段实施 → 验证 → 文档同步
   - 涉及版本号变更（v1.x → v2.x）

## 版本号规范

- 遵循 SemVer：`MAJOR.MINOR.PATCH`
- MAJOR：结构性升级（如 v1.x → v2.0）
- MINOR：新增 capability（如 v2.0 → v2.1）
- PATCH：bug 修复、文档调整

## CHANGELOG 规范

遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)：

```markdown
## [2.0.0] - 2026-09-09

### Added
- 开篇留存诊断模块
- 章节节拍规划工具
- 风格 DNA 提取与漂移检测
- 去 AI 腔模块
- 12 个自动化脚本
- 6 个流派模板
- 6 个平台调性卡

### Changed
- 主入口精简到 ≤ 200 行
- 续写流程用户输入从 8 项降至 ≤ 3 项
- shell 脚本弃用，仅保留 Python 版
- 章节命名支持 docx 工作流

### Deprecated
- compress_novel_memory.sh（迁移至 compress_novel_memory.py）

### Fixed
- 修复 YAML name/slug/version 三处不一致
- 修复 compress 脚本章节命名错位
- 修复 shell 脚本 macOS 兼容性

### Security
- 写入安全契约文档化（write-safety.md）
- 敏感内容边界明确（sensitive-content.md）
```

## 验证门禁

任何修改必须通过：

```bash
# 1. 主入口行数检查（≤ 200 行）
wc -l SKILL.md

# 2. 静态校验
python3 scripts/validate-skill.py .

# 3. 单元测试
python3 -m pytest tests/

# 4. Smoke test
# 人工运行 examples/smoke-test-prompts.md 全 10+ 条用例

# 5. 与基线包对比
diff -r ../novel-assistant-pro-1.0.0/ .  # 仅参考
```

## 自动化脚本规范

- 使用 `argparse` 而非手动解析 argv
- 错误信息必须含定位（文件、行号、字段）
- 必须支持 `--dry-run` 或 `--report`
- 必须 UTF-8 编码兼容
- 必须 macOS / Linux / Windows 三平台兼容
- 必须有对应的单元测试

## 文档规范

- 中文文案遵循用户偏好：
  - 避免过多破折号「——」
  - 避免「不是 X，是 Y」对比结构
  - 避免拟人化用词
  - 避免过度雕琢比喻
- 表格优先于段落
- 修订痕迹显示（before / after）
- 中文出版排版：宋体正文、黑体标题、首行缩进、1.5 倍行距（仅 .docx 强制）

## 提交规范

```
[type]: [subject]

[body]

[type] ∈ {feat, fix, docs, refactor, test, chore}
[subject] 中文一句话（≤ 30 字）
```

## 红线

- 不得把用户作品写入技能包自身目录
- 不得静默覆盖已有本地文件
- 不得绕过 validate-skill 与 unit test
- 不得破坏 MIT-0 许可证的合规性
- 不得引入成人、暴力、政治宗教敏感内容的默认行为

## 联系人

- 维护者：小浣熊肖恩
