---
name: "使用 AGENTS.md 生成器安全地生成和修补 AGENTS.md 和 RUNBOOK.md"
slug: "generate-and-safely-patch-agents-md-and-runbook-md-with-agents-md-generator"
version: "1.0.0"
displayName: "使用 AGENTS.md 生成器安全地生成和修补 AGENTS.md 和 RUNBOOK.md"
summary: "引导并安全地更新 AGENTS.md 和 RUNBOOK.md，而不会覆盖手动编辑的文档，从而使编码代理仓库保持干净的机器可读契约。"
license: "MIT"
description: "引导并安全地更新 AGENTS.md 和 RUNBOOK.md，而不会覆盖手动编辑的文档，从而使编码代理仓库保持干净的机器可读契约。"
github_stars: 2
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "Templates & Workflows"
framework: "Multi-Framework"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 2
---

# 使用 AGENTS.md 生成器安全地生成和补丁 AGENTS.md 和 RUNBOOK.md

Bootstrap and safely update AGENTS.md and RUNBOOK.md without clobbering hand-edited docs, so coding-agent repos keep a clean machine-readable contract.

## Prerequisites

Python 3.11+, pipx or pip, Git repository

## Installation

Use the upstream install or setup path that matches your environment:
- pip install -e ".[dev]"
- pipx install git+https://github.com/1991513ccie-png/skills
- pipx uninstall agentsgen
- python -m pip install -e ".[dev]"

Requirements and caveats from upstream:
- [![Python](https://img.shields.io/badge/python-%3E%3D3.11-blue)](pyproject.toml)
- agentsgen init . --preset cli-python
- **Python library (Poetry + pytest):** [recipes/python-lib/](recipes/python-lib/)

Basic usage or getting-started notes:
- RUNBOOK.md (human-friendly command/run cheatsheet)
- sh
- python3 -m venv .venv

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/markoblogo/AGENTS.md_generator/HEAD/README.md

## Documentation

- https://github.com/1991513ccie-png/skills
