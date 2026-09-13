---
name: "从自定义帧序列生成适用于Slack的动画GIF"
slug: "generate-slack-ready-animated-gifs-from-custom-frame-sequences"
version: "1.0.0"
displayName: "从自定义帧序列生成适用于Slack的动画GIF"
summary: "使用 Anthropic 的 slack-gif-creator 技能来创建符合 Slack 实用尺寸、时长和维度限制的动画 GIF。它为代理提供了一个有界限的 GIF 生产工作流程，而不是通用的图像库或聊天贴图列表。"
license: "MIT"
description: "使用 Anthropic 的 slack-gif-creator 技能来创建符合 Slack 实用尺寸、时长和维度限制的动画 GIF。它为代理提供了一个有界限的 GIF 生产工作流程，而不是通用的图像库或聊天贴图列表。"
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "Image & Creative Automation"
framework: "Claude Agents"
---

# 从自定义帧序列生成适用于Slack的动画GIF

Use Anthropic's slack-gif-creator skill to build animated GIFs that stay inside Slack's practical size, duration, and dimension constraints. It gives an agent a bounded GIF-production workflow, not a generic image library or chat sticker listing.

## Prerequisites

Python, Pillow, imageio, imageio-ffmpeg, numpy, and optional uploaded source images

## Installation

Requirements and caveats from upstream:
- The frontmatter requires only two fields:

Basic usage or getting-started notes:
- Select document-skills or example-skills
- /plugin install example-skills@anthropic-agent-skills
- These example skills are all already available to paid plans in Claude.ai.

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/anthropics/skills/HEAD/README.md

## Documentation

- https://raw.githubusercontent.com/anthropics/skills/main/skills/slack-gif-creator/SKILL.md
