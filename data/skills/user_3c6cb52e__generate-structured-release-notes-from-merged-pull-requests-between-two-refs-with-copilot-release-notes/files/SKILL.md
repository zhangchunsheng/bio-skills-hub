---
name: "通过 Copilot Release Notes 从两个引用之间的合并拉取请求生成结构化发布说明"
slug: "generate-structured-release-notes-from-merged-pull-requests-between-two-refs-with-copilot-release-notes"
version: "1.0.0"
displayName: "通过 Copilot Release Notes 从两个引用之间的合并拉取请求生成结构化发布说明"
summary: "比较两个标签、分支或SHA，并将已合并的拉取请求转换为可审查的markdown和JSON发布说明，用于发布工作流。"
license: "MIT"
description: "比较两个标签、分支或SHA，并将已合并的拉取请求转换为可审查的markdown和JSON发布说明，用于发布工作流。"
github_stars: 2
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "CI/CD Integrations"
framework: "Multi-Framework"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 2
---

# 使用 Copilot Release Notes 从两个引用之间的合并拉取请求中生成结构化发布说明

Compare two tags, branches, or SHAs and turn merged pull requests into reviewable markdown and JSON release notes for a release workflow.

## Prerequisites

GitHub Actions runner, checked-out git history for the compared refs, GitHub Copilot license, fine-grained PAT with Copilot Requests read permission

## Installation

Use the upstream install or setup path that matches your environment:
- npm install
- npm test # run 42 unit tests
- npx ncc build src/index.ts -o dist # rebuild dist/

Requirements and caveats from upstream:
- This action requires a COPILOT_GITHUB_TOKEN — a GitHub fine-grained personal access token with the **"Copilot Requests: Read"** permission. The token owner must have an active GitHub Copilot license.
- Uses the GitHub API to find PRs associated with commits. Catches more PR types but requires API access and is slower for large ranges.

Basic usage or getting-started notes:
- A **GitHub Actions** runner (Ubuntu, macOS, or Windows)
- An active **GitHub Copilot license**
- A **fine-grained PAT** with the Copilot Requests: Read permission (see [Authentication](#authentication))

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/github/copilot-release-notes/HEAD/README.md

## Documentation

- https://github.com/1991513ccie-png/skills
