---
name: "使用SQLCoder生成经过验证的分析SQL"
slug: "generate-validated-analytics-sql-with-sqlcoder"
version: "1.0.0"
displayName: "使用 SQLCoder 生成经过验证的分析 SQL"
summary: "当分析代理需要将自然语言问题和模式上下文转化为SQL草稿以便在受控数据工作流中进行审查、验证和运行时，请使用SQLCoder。"
license: "MIT"
description: "当分析代理需要将自然语言问题和模式上下文转化为SQL草稿以便在受控数据工作流中进行审查、验证和运行时，请使用SQLCoder。"
github_stars: 4035
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "Data Extraction & Transformation"
framework: "Custom Agents"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 4035
---

# 使用SQLCoder生成经过验证的分析SQL

Use SQLCoder when an analytics agent needs to turn natural-language questions plus schema context into SQL drafts that can be reviewed, validated, and run inside a controlled data workflow.

## Prerequisites

Python environment, SQLCoder package or Hugging Face model weights, schema metadata for the target database, and a controlled database execution or review path.

## Installation

Use the upstream install or setup path that matches your environment:
- pip install "sqlcoder[transformers]"
- pip install "sqlcoder[llama-cpp]"

Requirements and caveats from upstream:
- python inference.py -q "Question about the sample database goes here"

Basic usage or getting-started notes:
- If running on a non-apple silicon computer without GPU access, please run this on Linux/Intel Mac
- And run this on Windows
- In your terminal, run

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/defog-ai/sqlcoder/HEAD/README.md

## Documentation

- https://github.com/1991513ccie-png/skills
