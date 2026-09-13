---
name: general-skill-publisher
description: >
  通用技能发布器。将 ~/your-agent/skills/<target> 技能打包为可跨平台分发、自包含的 zip 压缩包。
  支持两级路由：默认最简模式（源文件直接 zip），以及全流程发布模式（含依赖分析、去品牌化、代码审查等 8 步管线）。
version: v1.0
triggers:
  - keyword: 打包
    description: 触发最简模式（🟢），源文件直接 zip，零处理。
  - keyword: 发布
    description: 触发全流程发布模式（🔴），执行完整的 8 步管线。
  - keyword: 迁移
    description: 触发全流程发布模式（🔴），执行完整的 8 步管线。
---

# general-skill-publisher

通用技能发布器 —— 将本地技能打包为可跨平台分发、自包含的 zip 压缩包。

## 两级路由（触发规则）

| 路由 | 触发条件 | 行为 |
|------|----------|------|
| 🟢 最简模式 | 用户说「把 xx 打包给我」——**不含**「发布」或「迁移」关键词 | 源文件直接 zip，零处理 |
| 🔴 发布模式 | 用户说「调用 general-skill-publisher 将 xx 打包给我，我要发布/迁移」——**必须含**「发布」或「迁移」关键词 | 执行完整 8 步管线 |

> **误触发防护：默认走最简模式。** 只有用户明确说出「发布」或「迁移」时才进入全流程管线。

---

## 🔴 全流程管线（发布模式）

当用户明确要求「发布」或「迁移」时，按顺序执行以下 8 个步骤：

### Step 1: 源文件盘点

扫描 `~/your-agent/skills/<target>/` 的完整文件树，记录所有文件及其路径结构。

```
操作：
  1. 列出目标技能目录下的所有文件（递归）
  2. 记录文件类型（脚本、配置、文档、二进制等）
  3. 生成完整的文件清单
```

### Step 2: 依赖分析

分析目标技能的依赖项：

- **Python 依赖**：扫描 `requirements.txt`、`pyproject.toml`、`setup.py` 等
- **系统命令依赖**：检查代码中对系统命令的调用（如 `curl`、`jq`、`ffmpeg` 等）
- **环境变量依赖**：扫描对特定环境变量的引用
- **外部引用**：记录对外部脚本、URL 或其他非自包含资源的引用

### Step 3: 副本构建到 `/tmp/`

将源文件完整复制到 `/tmp/skill-publish-<name>/` 工作目录，作为可修改的副本。

```
操作：
  1. 创建 /tmp/skill-publish-<name>/ 目录
  2. 完整复制 ~/your-agent/skills/<target>/ 的所有文件到工作目录
  3. 后续所有修改操作均在 /tmp/ 副本上进行
```

### Step 4: 二进制判断与安装块处理

**判断规则**（发布平台约束：只接受 `.md` 格式）：
- 扫描副本中所有非 `.md` 文件（`.sh`/`.py`/`.js`/真二进制等）
- **无非 `.md` 文件** → 跳过此步骤，保持文件原样
- **有非 `.md` 文件** → 使用 `install` 安装块法处理

**安装块格式**（仅当存在二进制时写入 SKILL.md 末尾）：

````markdown
## 安装

```bash
cat > scripts/install.sh << 'SCRIPT_EOF'
#!/bin/bash
# 安装脚本内容
# ...
SCRIPT_EOF
chmod +x scripts/install.sh
```
````

> 安装块使用 **heredoc** 方式写入，确保跨平台兼容性。

### Step 5: 去品牌化

将所有特定 Agent 品牌名称替换为通用术语，确保技能可在任何 Agent 环境下使用。

**品牌替换对照表：**

| 原品牌名 | 替换为 |
|----------|--------|
| Claude Code | Agent CLI |
| claude code | agent cli |
| CLAUDE.md | AGENTS.md |
| `~/.claude/skills/` | `~/your-agent/skills/` |
| Claude | Agent |
| claude | agent |
| Hermes | Agent |
| hermes | agent |
| Codex | Agent |
| codex | agent |
| OpenClaw | Agent |
| openclaw | agent |

**保留不动的内容：**
- 第三方文档引用（如链接到外部项目的 README）
- 技术命令和包名（如 `claude-code` npm 包名）
- 任何非品牌性质的专有名词

同时将所有版本号重置为 `v1.0`。

### Step 6: README 生成

生成跨平台 README 文件，**必须在标题后插入综合功能摘要**，然后才是安装说明，且安装部分**必须同时包含 bash 和 PowerShell 命令**：

**生成逻辑：**
1. 从目标 SKILL.md 的 frontmatter `description` 字段提取一句话定位
2. 从 SKILL.md 正文的首个引用块（`> xxx`）提取补充描述
3. 结合目录结构和脚本列表，拼接核心能力清单

**README 模板：**

```markdown
# <skill-name>

> **📦 技能摘要**
>
> <从 SKILL.md frontmatter description 提取的一句话定位>
>
> **核心能力：**
> - <能力1> — <简要说明>
> - <能力2> — <简要说明>
> - <能力3> — <简要说明>
>
> **适用场景：** <从 SKILL.md 正文提取的典型使用场景>
>
> **亮点：** <从 SKILL.md 中提取的核心优势，如零依赖/自动回退/跨平台等>

## 安装与使用

### Linux / macOS (bash)

```bash
# 解压
unzip <skill-name>-v1.0.zip -d <skill-name>
cd <skill-name>

# 安装依赖（如有）
pip install -r requirements.txt

# 使用
python main.py
```

### Windows (PowerShell)

```powershell
# 解压
Expand-Archive -Path <skill-name>-v1.0.zip -DestinationPath <skill-name>
cd <skill-name>

# 安装依赖（如有）
pip install -r requirements.txt

# 使用
python main.py
```
```

> **摘要质量要求**：不是机械填空——必须阅读目标技能 SKILL.md 全文，理解该技能实际做什么、解决什么问题、有什么亮点，然后用人类可读的简洁中文写出 3-5 条核心能力和 1-2 句适用场景。避免凑数和模板感。

### Step 7: 代码审查（7 项检查清单）

对最终副本进行以下 7 项检查，确保全部通过：

| # | 检查项 | 要求 |
|---|--------|------|
| 1 | **Frontmatter** | SKILL.md 的 YAML frontmatter 格式正确且字段完整 |
| 2 | **死链接** | 无指向不存在文件或外部死链的引用 |
| 3 | **安装块语法** | 如存在安装块，heredoc 语法正确，`chmod +x` 无误 |
| 4 | **README 跨平台** | README 同时包含 bash 和 PowerShell 命令 |
| 5 | **零品牌名** | 全文无 Claude、Hermes、Codex 等品牌残留（第三方引用除外） |
| 6 | **零非 .md 文件** | 确认无非 `.md` 文件残留（平台分发约束） |
| 7 | **版本 v1.0** | 所有版本号均为 v1.0 |

### Step 8: 打包为 zip

将审查通过的副本打包为 `<skill-name>-v1.0.zip`：

```bash
cd /tmp/skill-publish-<name>
zip -r ../<skill-name>-v1.0.zip .
```

生成的 zip 文件位于 `/tmp/<skill-name>-v1.0.zip`，交付给用户。

---

## 红线（绝对不可违反）

1. **全程 `/tmp/` 操作**：所有修改、构建、打包操作在 `/tmp/` 进行，**绝不触碰 `~/your-agent/skills/` 中的原始文件**
2. **二进制处理**：有二进制才用 `install` 块，无二进制原样保留，不无中生有
3. **自包含**：打包产物解压即用，不依赖外部资源（明确声明的依赖除外）
4. **品牌替换**：严格按替换表执行，但保留第三方引用和技术命令/包名

---

## 关键坑（从实战测试沉淀）

⚠️ **"二进制"在这里是分发约束，不是技术定义**：发布平台（Skillhub）只接受 `.md` 格式。因此 `.sh`/`.py`/`.js` 等文本脚本也必须从 zip 移除，转为 heredoc 安装块。使用 `is_publish_binary()`（非 `.md` 即需转换），不用 `is_text_file()`。

⚠️ **安装块：文本脚本用 heredoc 原文，真二进制用 base64**：`.sh`/`.py` 脚本用 `cat > file << 'EOF' ... EOF` 嵌原文，Agent 直接看懂。只有无法 UTF-8 解码的真正二进制才降级用 base64。

⚠️ **审查脚本会对安装块产生误报**：`review.py` 将 heredoc 内的代码当 markdown 正文解析，会误报 Dead links（正则表达式）、Install block syntax（代码内 EOF 字符串）等。凡因安装块内容触发的审查失败，直接忽略。详见 [references/review-false-positives.md](references/review-false-positives.md)。

⚠️ **品牌替换大小写双覆盖**：`Hermes`+`hermes`、`Claude`+`claude`、`OpenClaw`+`openclaw` 都要替换。全局替换必须先长后短（`Claude Code`→`Agent CLI` 先于 `Claude`→`Agent`）。

⚠️ **版本号审查正则必须要求 `v` 前缀**：`VERSION_PATTERN` 若用 `\bv?(\d+\.\d+)\b` 会把章节编号（`### 1.1`）和 IP 地址（`114.114.114`）误判为版本号。正确正则是 `\bv(\d+\.\d+)\b`，只匹配带 `v` 前缀的版本。

⚠️ **版本重写时机**：版本号统一放在 Step 6（去品牌化）中一并处理，不要单开步骤。排除 URL 行（`https?://`）、技术工具版本行（`python 3.11`、`node 18`）、frontmatter 的 `version:` 字段。

- **绝不修改原生文件** —— `/tmp/` 是唯一的工作区
- **误触发防护** —— 默认走最简模式，只有「发布」「迁移」关键词才触发全流程
- **跨平台** —— README 必须同时有 bash 和 PowerShell 命令
- **安装块格式规范** —— 使用 heredoc 嵌原文（文本脚本）或 base64（真二进制）：
  ```bash
  cat > scripts/xxx.sh << 'SCRIPT_EOF'
  #!/usr/bin/env bash
  ...
  SCRIPT_EOF
  chmod +x scripts/xxx.sh
  ```
- **版本号重写时机** —— 统一在 Step 6（去品牌化）中处理，排除 URL 行和技术工具版本行

⚠️ **去品牌化必须三改（2026-07-04 BOSS纠正）**：目录名 + 文件名 + 内容全部清除品牌名。不能只改 SKILL.md 的 name 字段而保留 `hermes-xxx` 目录名。改名顺序：目录名 → 文件名 → 内容（长字符串先于短字符串）→ 交叉引用更新。

⚠️ **改名冲突检查**：批量改名前先扫描所有目标名，避免两个源文件碰撞到同一目标名导致覆盖丢失。碰撞时用不同名（如 `codex-tools.md`→`agent-tools-codex.md`、`hermes-tools.md`→`agent-tools-hermes.md`）。

⚠️ **审查失败先穷尽修复，再判断可忽略**：审查脚本报出的失败项，先修到不能再修为止。不能提前标记为"可忽略"而跳过。只有第三方引用文档（如 Anthropic 官方原文）的失败才能标记为预期可接受。

⚠️ **多skill组合包发布**：当用户要求打包多个 skill 为一个套件时，需手动组装目录结构→对每个子 skill 逐一去品牌化→生成统一主 SKILL.md→审查→打包。流程同单 skill 但需注意跨 skill 引用路径更新。

⚠️ **审查脚本安装块误报（已知局限）**：review.py 会将 heredoc 安装块内嵌的代码当作 markdown 正文解析，从而导致误报——(1)代码内正则表达式被当作 dead links；(2)代码内字符串被当作未闭合的 heredoc 定界符。凡因安装块内容引发的 Dead links / Install block syntax 审查失败，**一律直接忽略**，非包质量问题。

⚠️ **打包格式默认 .zip**：BOSS 要求打包产物为 `.zip` 格式。仅在 `.zip` 不可用时才考虑 `.tar` 或 `.gz`。

⚠️ **触发词歧义（2026-07-04 BOSS纠正）**：BOSS 说「技能发布技能」「优化升级技能发布技能」→ 指 `general-skill-publisher` **本身**，不是被发布的目标技能。不要说「优化升级技能发布技能」= 修改目标技能的 SKILL.md。正确理解：「技能发布技能」= the skill-publishing skill = `general-skill-publisher`。

⚠️ **「技能顶层 readme」的所指（2026-07-04 BOSS纠正）**：在 publisher 上下文中，BOSS 说「在技能顶层的 readme.md 文档技能标题后开始处加一段…」指的是**被发布产物的 README.md**（Step 6 生成的），不是 publisher 自己的 SKILL.md。

⚠️ **安装块内硬编码路径修正**：去品牌化时，安装块内脚本的 `$HOME/.hermes/skills/<name>/` 等硬编码 Agent 路径，应改为 `$(dirname "$0")/` 相对路径，确保解压后脚本能自引用。典型修正：`local_file="$HOME/.hermes/skills/xxx/scripts/config.sh"` → `local_file="$(dirname "$0")/config.sh"`。

---

## 使用示例

### 🟢 最简打包

```
用户：把我的 my-skill 打包给我
助手：[直接 zip ~/your-agent/skills/my-skill/ → 交付 my-skill.zip]
```

### 🔴 全流程发布

```
用户：调用 general-skill-publisher 将 my-skill 打包给我，我要发布
助手：[执行 8 步管线 → 交付 my-skill-v1.0.zip]
```

---

## 输出交付物

| 产物 | 位置 | 说明 |
|------|------|------|
| 工作副本 | `/tmp/skill-publish-<name>/` | 去品牌化、审查后的完整副本 |
| 最终 zip | `/tmp/<name>-v1.0.zip` | 自包含、跨平台兼容的发布包 |

