---
name: "使用 Swag 从源代码注释生成 Go API 文档"
slug: "generate-go-api-docs-from-source-annotations-with-swag"
version: "1.0.0"
displayName: "使用 Swag 从源码注释生成 Go API 文档"
summary: "在代理需要将 Go 处理程序注解转换为可审查的 Swagger 2.0 文档之前，如果 API 文档、客户端或发布检查依赖于它，则使用 Swag。"
license: "MIT"
description: "在代理需要将 Go 处理程序注解转换为可审查的 Swagger 2.0 文档之前，如果 API 文档、客户端或发布检查依赖于此，则使用 Swag。"
github_stars: 12867
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "Library & API Reference"
framework: "Multi-Framework"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 12867
---

# 使用 Swag 从源码注释生成 Go API 文档

Use Swag when an agent needs to turn Go handler annotations into reviewable Swagger 2.0 documentation before API docs, clients, or release checks depend on it.

## Prerequisites

Go 1.19 or newer; Swag CLI or Docker image; Go API source tree with handler annotations

## Installation

Use the upstream install or setup path that matches your environment:
- go install github.com/swaggo/swag/cmd/swag@latest
- docker run --rm -v $(pwd):/code ghcr.io/swaggo/swag:latest
- Make sure to import the generated docs/docs.go so that your specific configuration gets init'ed. If your General API annotations do not live in main.go, you can let swag know with -g flag.
- Make it OR condition

Requirements and caveats from upstream:
- Alternatively you can run the docker image:
- --dir value, -d value Directories you want to parse,comma separated and general-info file must be in the first one (default: "./")
- | x-name | The extension key, must be start by x- and take only json value | // @x-example-key {"key": "value"} |

Basic usage or getting-started notes:
- [Getting started](#getting-started)
- [Example value of struct](#example-value-of-struct)
- Add comments to your API source code, See [Declarative Comments Format](#declarative-comments-format).

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/swaggo/swag/HEAD/README.md

## Documentation

- https://github.com/1991513ccie-png/skills
