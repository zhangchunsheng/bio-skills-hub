---
name: "从策划的文件夹中快速生成静态照片相册网站，使用 DD Photos"
slug: "generate-fast-static-photo-album-sites-from-curated-folders-with-dd-photos"
version: "1.0.0"
displayName: "从策划的文件夹中快速生成静态照片相册网站，使用 DD Photos"
summary: "将导出的照片文件夹转换为移动友好的静态相册网站，而无需搭建基于数据库的图库系统。"
license: "MIT"
description: "将导出的照片文件夹转换为移动友好的静态相册网站，而无需搭建基于数据库的图库系统。"
github_stars: 155
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "Image & Creative Automation"
framework: "Multi-Framework"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 155
---

# 从策划的文件夹中快速生成静态照片相册网站，使用 DD Photos

Turn exported photo folders into a mobile-friendly static album site without standing up a database-backed gallery system.

## Prerequisites

Go toolchain or built binaries, source photo folders, DD Photos config files, optional static hosting target such as S3 or a web server

## Installation

Use the upstream install or setup path that matches your environment:
- docker run --rm -v ~/my-ddphotos:/ddphotos dougdonohoe/ddphotos init

Requirements and caveats from upstream:
- [![Docker Image Version](https://img.shields.io/docker/v/dougdonohoe/ddphotos?logo=docker&label=Docker%20Hub)](https://hub.docker.com/r/dougdonohoe/ddphotos)
- [![Docker Pulls](https://img.shields.io/docker/pulls/dougdonohoe/ddphotos?logo=docker&label=Docker%20Pulls)](https://hub.docker.com/r/dougdonohoe/ddphotos)
- ## Docker Quick Start

Basic usage or getting-started notes:
- ./ddphotos run # run dev server at http://localhost:5173
- Once you have defined where your photos live, you run the photogen tool,
- Dry-run mode by default (use -doit to write files).

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/dougdonohoe/ddphotos/HEAD/README.md

## Documentation

- https://ddphotos.donohoe.info
