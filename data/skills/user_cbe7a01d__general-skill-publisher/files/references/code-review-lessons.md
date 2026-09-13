# 代码审查实战教训

> 本文件记录 `general-skill-publisher` 开发和审查过程中发现的关键问题及解决方案。

## VERSION_PATTERN 误判

**问题**：正则 `\bv?(\d+\.\d+)\b` 会把章节编号（`### 1.1`）和 IP 地址（`114.114.114`）误判为版本号。

**修复**：改为 `\bv(\d+\.\d+)\b`，强制要求 `v` 前缀。只匹配 `v1.0`、`v2.1` 等真正版本字符串。

```python
# ❌ 错误
VERSION_PATTERN = re.compile(r"\bv?(\d+\.\d+(?:\.\d+)?)\b")

# ✅ 正确
VERSION_PATTERN = re.compile(r"\bv(\d+\.\d+(?:\.\d+)?)\b")
```

## 品牌替换顺序

**问题**：先替换短字符串 `Agent → Agent`，再替换长字符串 `Agent CLI → Agent CLI` 时，`Agent CLI` 已变成 `Agent Code`。

**修复**：长字符串优先替换。

```python
BRAND_REPLACEMENTS = [
    ("Agent CLI", "Agent CLI"),   # 先长
    ("AGENTS.md", "AGENTS.md"),
    ("~/your-agent/skills/", "~/your-agent/skills/"),
    ("Agent", "Agent"),            # 后短
    ("Agent", "Agent"),
    ("agent", "agent"),            # 大小写双覆盖
]
```

## 死链接检测

**问题**：SKILL.md 引用 `references/testing-lessons.md` 但文件不存在，审查才暴露。

**教训**：打包前必须运行 `review.py` 的 check 2（死链接），不能依赖人工检查。

## 步骤编号对齐

**问题**：SKILL.md 将"二进制检测+安装块生成"合并为 Step 4，publish.py 拆分为 Step 4+5。文档与代码不一致。

**教训**：修改 pipeline 步骤后必须同步更新 SKILL.md，确保编号一致。

## 版本号重写时机

**问题**：版本号重写放在 Step 6（去品牌化）中，但 Step 5 生成的安装块内容也需要版本号统一。

**现状**：安装块内容为源文件原文，不单独重写其中的版本号。版本重写仅覆盖 .md 文件。如需统一安装块中的版本号，需在 Step 5 之后额外处理。

## 分发约束 vs 技术定义

**核心区分**：
- **技术定义**：`.sh`/`.py`/`.js` 是文本文件（`is_text_file()` 返回 True）
- **分发约束**：发布平台只接受 `.md`，因此所有非 `.md` 需转为安装块（`is_publish_binary()` 返回 True）

处理时使用 `is_publish_binary()` 判断是否需要转换，但生成安装块时仍区分文本（heredoc）和真二进制（base64）。
