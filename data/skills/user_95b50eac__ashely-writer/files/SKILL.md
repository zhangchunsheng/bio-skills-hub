---
name: wechat-suite
description: 一键安装公众号写作全家桶：wechat 系列（选题大纲、初稿、文风画像、标题、全流程构建）与 xiaohu 系列（微信排版、封面生成），共 7 个 skill。当用户说"安装公众号套装""部署 wechat 系列""把写公众号的 skill 都装上""下载公众号全家桶"时使用。This skill deploys the full WeChat-article-writing skill suite (wechat-* + xiaohu-*) into the user's skills directory in one step.
license: MIT
allowed-tools:
disable: false
---

# wechat-suite — 公众号写作全家桶一键安装

本 skill 是一个安装器。它把内置的 7 个公众号写作 skill（wechat 系列 + xiaohu 系列）一次性部署到用户的 skills 目录，用户无需逐个下载。

## 包含的 skill（7 个）

- wechat-topic-outline-planner — 公众号选题与大纲策划
- wechat-draft-writer — 公众号初稿写作
- wechat-style-profiler — 文风 DNA 梳理
- wechat-title-generator — 公众号标题生成与评估
- wechat-article-builder — 公众号文章全流程自动生成与发布
- xiaohu-wechat-format — 微信排版（结构化预处理 + 封面生成）
- xiaohu-wechat-cover — 公众号封面图生成器（嵌套于 xiaohu-wechat-format）

## 安装方式

运行部署脚本，把内置的全部 skill 复制到用户的 skills 目录：

```bash
python3 scripts/deploy.py
```

脚本会：
1. 自动定位用户的 skills 目录（默认 `~/.workbuddy/skills/`，若不存在则回退 `~/.codebuddy/skills/`）。
2. 递归找出所有含 `SKILL.md` 的目录，按每个 skill 自身 frontmatter 里的 `name` 作为落盘目录名（避免嵌套 skill 名称冲突）。
3. 逐个复制；若已存在则跳过（不覆盖用户已有修改）。
4. 打印每个 skill 的安装结果。

## 使用方式

安装完成后，7 个 skill 会出现在用户的 skill 列表里，按需触发即可（例如"基于这篇参考文章写篇公众号文章并推送"会触发 wechat-article-builder）。本安装器 skill 本身可保留或删除，不影响已部署的 7 个 skill。
