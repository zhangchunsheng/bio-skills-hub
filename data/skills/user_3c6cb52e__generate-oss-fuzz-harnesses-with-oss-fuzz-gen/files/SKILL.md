---
name: "使用 oss-fuzz-gen 生成 OSS-Fuzz 混合器"
slug: "generate-oss-fuzz-harnesses-with-oss-fuzz-gen"
version: "1.0.0"
displayName: "使用 oss-fuzz-gen 生成 OSS-Fuzz 混合器"
summary: "使用LLM辅助的测试夹具生成来扩展真实项目在手动模糊测试工作开始前的覆盖率。"
license: "MIT"
description: "使用LLM辅助的测试夹具生成来扩展真实项目在手动模糊测试工作开始前的覆盖率。"
github_stars: 1384
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "Security & Verification"
framework: "Multi-Framework"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 1384
---

# 使用 oss-fuzz-gen 生成 OSS-Fuzz 混合器

oss-fuzz-gen 是一个用于为开源项目生成 Fuzz 测试混合器的工具。它可以帮助开发者快速创建针对特定项目的模糊测试框架，从而提高软件的安全性和稳定性。

该工具支持多种编程语言和框架，包括 C/C++、Go、Python 等。通过分析源代码并自动生成相应的 fuzzing 混合器，oss-fuzz-gen 能够显著减少手动编写测试用例的工作量。

使用方法：
1. 安装 oss-fuzz-gen 工具
2. 准备目标项目的源代码
3. 运行命令：`oss-fuzz-gen --project <project_name> --language <language>`
4. 查看生成的混合器文件并进行必要的调整

更多详情请访问：https://github.com/google/oss-fuzz-gen

示例命令：
```
oss-fuzz-gen --project myproject --language c++
```

该工具与 Google 的 OSS-Fuzz 项目紧密集成，可以无缝对接到现有的 fuzzing 工作流中。

Use LLM-assisted harness generation to expand fuzz coverage for real projects before manual fuzzing work begins.

## Prerequisites

oss-fuzz-gen, compiler toolchain, fuzzing runtime

## Installation

Requirements and caveats from upstream:
- This framework generates fuzz targets for real-world C/C++/Java/Python projects with

Basic usage or getting-started notes:
- Check our detailed [usage guide](./USAGE.md) for instructions on how to run this framework and generate reports based on the results.
- ## Independent Agent Execution and Evaluation
- You can also execute or evaluate individual agents without running full experiments, using the integrated agent execution framework.

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/google/oss-fuzz-gen/HEAD/README.md

## Documentation

- https://github.com/1991513ccie-png/skills
