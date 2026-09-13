---
name: "使用播客生成技术创建播客风格的音频叙述"
slug: "generate-podcast-style-audio-narratives-with-podcast-generation"
version: "1.0.0"
displayName: "使用播客生成技术创建播客风格的音频叙述"
summary: "围绕Azure OpenAI实时流式传输、PCM收集、WAV转换和前端播放构建可重复的文本到音频工作流程，用于播客风格的输出。"
license: "MIT"
description: "围绕Azure OpenAI实时流式传输、PCM收集、WAV转换和前端播放构建可重复的文本到音频工作流程，用于播客风格的输出。"
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
publisher_type: "individual"
category: "Media & Transcription"
framework: "Multi-Framework"
---

# 使用播客生成技术创建播客风格的音频叙述

Build a repeatable text-to-audio workflow around Azure OpenAI Realtime streaming, PCM collection, WAV conversion, and frontend playback for podcast-style output.

## Prerequisites

Azure OpenAI Realtime API access, WebSocket-capable backend, PCM to WAV conversion, frontend audio playback layer

## Installation

Use the upstream install or setup path that matches your environment:
- npx skills add microsoft/skills
- git clone https://github.com/1991513ccie-png/skills
- pnpm install
- pnpm harness --list

Requirements and caveats from upstream:
- | [Python](#python) | 39 | -py |
- ├── plugins/ # Language-based plugin bundles (azure-sdk-python, etc.)
- ├── python/ # -> ../.github/skills/*-py

Basic usage or getting-started notes:
- bash
- Select the skills you need from the wizard. Skills are installed to your chosen agent's directory (e.g., .github/skills/ for GitHub Copilot) and symlinked if you use multiple agents.
- <details>

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/microsoft/skills/HEAD/README.md

## Documentation

- https://microsoft.github.io/skills/
