# general-skill-publisher

> **📦 技能摘要**
>
> 通用技能发布器——将本地技能一键打包为可跨平台分发、自包含的 zip 压缩包。解决 Agent 技能从开发环境迁移到 Skillhub 等发布平台的最后一公里问题。
>
> **核心能力：**
> - 🟢 **最简打包** — 源文件直接 zip，零处理，秒级交付
> - 🔴 **全流程发布管线** — 8 步自动化：源文件盘点 → 依赖分析 → 副本构建 → 二进制转换（heredoc 安装块/base64）→ 去品牌化（5 大品牌 → 通用术语）→ README 生成（bash + PowerShell 双平台）→ 7 项代码审查 → zip 打包
> - 🛡️ **原生文件零风险** — 所有操作在 `/tmp/` 隔离区执行，绝不触碰 `~/your-agent/skills/` 原始文件
> - 🔍 **7 项审查清单** — Frontmatter 格式、死链接、安装块语法、跨平台 README、零品牌残留、零非 .md 文件、版本号 v1.0
>
> **适用场景：** 本地开发完成的 Agent 技能需要发布到 Skillhub 或迁移到其他 Agent 平台时，自动完成格式转换、品牌清理、依赖声明、跨平台适配等全流程处理。
>
> **亮点：** 误触发防护（默认最简模式）；非 `.md` 文件智能处理（文本脚本 heredoc，真二进制 base64）；品牌替换先长后短防误伤；审查失败先穷尽修复再标记可忽略。

## 安装与使用

### 依赖要求

```bash
pip install pyyaml
```

### Linux / macOS (bash)

```bash
# 解压
unzip general-skill-publisher-v1.0.zip -d general-skill-publisher
cd general-skill-publisher

# 安装脚本（详见 SKILL.md 安装章节）
mkdir -p scripts
# 从 SKILL.md 复制安装命令执行

# 使用
python3 scripts/publish.py <skill-name> --mode release
```

### Windows (PowerShell)

```powershell
# 解压
Expand-Archive -Path general-skill-publisher-v1.0.zip -DestinationPath general-skill-publisher
cd general-skill-publisher

# 安装脚本
New-Item -ItemType Directory -Force -Path scripts
# 从 SKILL.md 复制安装命令执行
```
