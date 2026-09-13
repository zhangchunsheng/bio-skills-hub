---
name: "在审查漂移设置之前，使用 terraform-docs 生成 Terraform 模块输入和输出文档"
slug: "generate-terraform-module-inputs-and-outputs-docs-with-terraform-docs-before-review-drift-sets-in"
version: "1.0.0"
displayName: "在审查漂移设置之前，使用 terraform-docs 生成 Terraform 模块输入和输出文档"
summary: "从源代码刷新 Terraform 模块文档，以便在审查或发布之前，变量、输出和提供者与代码保持同步。"
license: "MIT"
description: "从源代码刷新 Terraform 模块文档，以便在审查或发布之前，变量、输出和提供者与代码保持同步。"
github_stars: 4753
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "CI/CD Integrations"
framework: "Multi-Framework"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 4753
---

# 在审查漂移设置之前，使用 terraform-docs 生成 Terraform 模块输入和输出文档

Refresh Terraform module documentation from source so variables, outputs, and providers stay aligned with the code before review or release.

## Prerequisites

Terraform module directory, terraform-docs CLI, optional README template or CI step

## Installation

Use the upstream install or setup path that matches your environment:
- brew install terraform-docs
- brew install terraform-docs/tap/terraform-docs
- go install github.com/terraform-docs/terraform-docs@v0.24.0
- the repo and run make build from the repository which will put terraform-docs in:

Requirements and caveats from upstream:
- ### Using docker
- **NOTE:** Docker tag latest refers to _latest_ stable released version and edge

Basic usage or getting-started notes:
- macOS users can install using [Homebrew]:
- bash
- or

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/terraform-docs/terraform-docs/HEAD/README.md

## Documentation

- https://terraform-docs.io
