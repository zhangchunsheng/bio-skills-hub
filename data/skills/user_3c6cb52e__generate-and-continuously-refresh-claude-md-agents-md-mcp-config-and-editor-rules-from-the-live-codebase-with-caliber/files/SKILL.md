---
name: "从实时代码库中生成并持续刷新 CLAUDE.md、AGENTS.md、MCP 配置和编辑器规则，使用 Caliber"
slug: "generate-and-continuously-refresh-claude-md-agents-md-mcp-config-and-editor-rules-from-the-live-codebase-with-caliber"
version: "1.0.0"
displayName: "从实时代码库中生成并持续刷新 CLAUDE.md、AGENTS.md、MCP 配置和编辑器规则，使用 Caliber"
summary: "在代理面向仓库的指令开始偏离实际代码库，并且你希望使用一个工作流程来审计、生成、审查并在多个编码代理之间保持这些文件更新时，请使用 Caliber。"
license: "MIT"
description: "当面向代理的仓库指令开始偏离实际代码库，而你希望使用一个工作流程来审计、生成、审查并在多个编码代理之间保持这些文件更新时，请使用 Caliber。"
github_stars: 717
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "Developer Tools"
framework: "Multi-Framework"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 717
  npm_package: "@rely-ai/caliber"
  npm_weekly_downloads: 6541
---

# 从实时代码库中生成并持续刷新 CLAUDE.md、AGENTS.md、MCP 配置和编辑器规则，使用 Caliber

Use Caliber when agent-facing repo instructions have started drifting from the actual codebase and you want one workflow to audit, generate, review, and keep those files fresh across multiple coding agents.

## Prerequisites

Node.js 20+, terminal access, and either Claude Code or Cursor CLI for /setup-caliber, or the Caliber CLI workflow for other supported agents.

## Installation

Use the upstream install or setup path that matches your environment:
- npx @rely-ai/caliber bootstrap
- **Run from your terminal** (PowerShell, CMD, or Git Bash) — not from inside an IDE chat window. Open a terminal, cd into your project folder, then run npx @rely-ai/caliber bootstrap.
- npx @rely-ai/caliber bootstrap ← one-time, 2 seconds
- git clone https://github.com/1991513ccie-png/skills

Requirements and caveats from upstream:
- <a href="https://nodejs.org"><img src="https://img.shields.io/node/v/@rely-ai/caliber" alt="node"></a>
- Requires **Node.js >= 20**.
- TypeScript, Python, Go, Rust, Java, Ruby, Terraform, and more. Language and framework detection is fully LLM-driven — no hardcoded mappings. Caliber works on any project.

Basic usage or getting-started notes:
- **Don't use Claude Code or Cursor?** Run caliber init instead — it's the same setup as a CLI wizard. Works with any LLM provider: bring your own Anthropic, OpenAI, or Vertex AI key.
- Pre-commit hooks run the refresh loop automatically. New team members get nudged to bootstrap on their first session.
- Caliber watches your AI coding sessions and learns from them. Hooks capture tool usage, failures, and your corrections — then an LLM distills operational patterns into CALIBER_LEARNINGS.md.

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/caliber-ai-org/ai-setup/HEAD/README.md

## Documentation

- https://caliber-ai.dev
