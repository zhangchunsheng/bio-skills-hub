# novel-assistant-pro

[![version](https://img.shields.io/badge/version-2.0.0-blue.svg)](./CHANGELOG.md)
[![license](https://img.shields.io/badge/license-MIT--0-green.svg)](./LICENSE)
![status](https://img.shields.io/badge/status-stable-brightgreen.svg)

面向长篇小说与多作品创作的 **项目管理型 AI 助手**。核心定位是「可持续管理的创作项目」，而不是「一次性代写」。

## 核心能力

- 项目生命周期：创建 → 续写 → 修订 → 压缩 → 导出
- 一致性维护：人物声音、世界观硬规则、伏笔链路、时间线
- 自动化诊断：剧情冲突、节拍五要素、开篇留存、风格漂移、AI 痕迹
- 工程化交付：本地写入安全、章节备份、记忆压缩、docx 导出
- 多作品协作：独立记忆 + 独立目录 + 切换清理

## 快速开始

```text
"我想写一部玄幻长篇，主角是退婚少年，核心看点是废材逆袭。
 请帮我建立人物、世界观和前三章大纲。"
```

详见 [SKILL.md](./SKILL.md) 与 [references/quickstart.md](./references/quickstart.md)。

## 目录结构

```text
novel-assistant-pro-2.0.0/
├── SKILL.md                              # 主入口（≤ 200 行）
├── README.md                             # 本文件
├── AGENTS.md                             # 维护与贡献规范
├── CHANGELOG.md                          # 版本变更记录
├── LICENSE                               # MIT-0 许可证
├── _meta.json                            # 包元数据
├── examples/                             # 示例记忆文件、smoke test、端到端 demo
├── references/                           # 详细规则与模板（按需读取）
│   ├── genres/                           # 流派模板（6 个）
│   ├── platforms/                        # 平台调性卡（6 个）
│   ├── anti-ai/                          # 去 AI 腔模块
│   ├── first3-retention/                 # 开篇留存诊断
│   └── pacing/                           # 章节节拍规划
├── scripts/                              # 自动化脚本（12+ 个）
└── tests/                                # 单元测试与 smoke test
```

## 安装

### SkillHub 安装

1. 在商汤小浣熊中打开 Skills 面板。
2. 搜索 `novel-assistant-pro`。
3. 点击安装。


```

## 触发示例

| 想做什么 | 该怎么说 |
|---|---|
| 创建新书 | 「我想写一部{类型}长篇，主角是{身份}，核心看点是{爽点}」 |
| 续写章节 | 「续写第 8 章」或「接着写」 |
| 检查冲突 | 「帮我检查第 12 章有没有人物设定冲突、时间线问题和伏笔遗漏」 |
| 压缩记忆 | 「这部小说的记忆文件太长了，帮我压缩，但不要丢失 P1 伏笔」 |
| 提取风格 | 「分析开篇 1000 字，提取风格 DNA」 |
| 去 AI 腔 | 「把第 8 章改成更人味的版本」 |
| 导出 docx | 「导出第 8 章到 `/path/to/第8章-XXX.docx`」 |
| 章节命名转换 | 「把所有 `chapter-001.md` 改成 `第1章-标题.docx`」 |
| 切换作品 | 「我现在开始写新作品 {新作品名}」 |
| 加入灵感 | 「把这条灵感记到《XXX》的素材库：{灵感内容}」 |

## 不会做的事

- 写辞职信、营销文案、古诗词、笑话
- 出版法律审校、版权审查
- 成人内容、暴力血腥、政治宗教敏感题材
- 把用户作品写入技能包自身目录
- 静默覆盖已有本地文件

## 文档导航

- 主入口：[SKILL.md](./SKILL.md)
- 完整规则：[references/](./references/)
- 自动化脚本：[scripts/](./scripts/)
- 单元测试：[tests/](./tests/)
- 变更记录：[CHANGELOG.md](./CHANGELOG.md)
- 贡献指南：[AGENTS.md](./AGENTS.md)

## 维护者

- 肖恩小浣熊

## 许可证

MIT-0（详见 [LICENSE](./LICENSE)）。
