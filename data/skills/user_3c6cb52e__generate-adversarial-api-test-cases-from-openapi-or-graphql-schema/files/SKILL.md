---
name: "从 OpenAPI 或 GraphQL 模式生成对抗性 API 测试用例"
slug: "generate-adversarial-api-test-cases-from-openapi-or-graphql-schema"
version: "1.0.0"
displayName: "从 OpenAPI 或 GraphQL 模式生成对抗性 API 测试用例"
summary: "当代理需要将API模式转换为广泛的负面和边界情况覆盖而不是手写示例时，请使用Schemathesis。该技能练习实时端点或应用钩子，探索意外组合，并报告普通正常路径测试遗漏的失败情况。"
license: "MIT"
description: "当代理需要将API模式转换为广泛的负面和边界情况覆盖而不是手动编写示例时，请使用Schemathesis。该技能练习实时端点或应用钩子，探索意外组合，并报告普通正常路径测试遗漏的失败情况。"
github_stars: 3214
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
category: "Security & Verification"
framework: "Multi-Framework"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 3214
---

# 从 OpenAPI 或 GraphQL 模式生成对抗性 API 测试用例

Use Schemathesis when an agent needs to turn an API schema into broad negative and edge-case coverage instead of hand-writing examples. The skill exercises live endpoints or app hooks, explores unexpected combinations, and reports failures that ordinary happy-path tests miss.

## Installation

Use the upstream install or setup path that matches your environment:
- uv pip install schemathesis

Requirements and caveats from upstream:
- <img src="https://img.shields.io/pypi/pyversions/schemathesis.svg" alt="Python versions">
- **Python Tests:**
- python

Basic usage or getting-started notes:
- uvx schemathesis run https://example.schemathesis.io/openapi.json
- uvx schemathesis run https://your-api.com/openapi.json
- **Command Line:**

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/schemathesis/schemathesis/HEAD/README.md
