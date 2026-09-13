# Generate Comic Drama Video

一个面向 Codex 智能体的横屏漫剧视频生产 Skill。它把故事创作、完整脚本审核、统一视觉生成、配音、字幕对齐、可选背景音乐、HyperFrames 合成和最终 MP4 校验串成一套可恢复、可审核的工作流。

仓库地址：<https://github.com/niuhuoshan/generate-comic-drama-video>

## 作品展示

### AI 图文漫剧《不存在的 13 楼》

[![AI 图文漫剧《不存在的 13 楼》](assets/showcase/bv1zvnh6aeji-cover.jpg)](https://www.bilibili.com/video/BV1ZVNh6aEji)

使用本 Skill 制作的成品漫剧，时长 4 分 36 秒。点击封面前往 Bilibili 观看。

[在 Bilibili 观看](https://www.bilibili.com/video/BV1ZVNh6aEji) | `BV1ZVNh6aEji`

## 主要能力

- 根据主题或一句话设定创作完整故事，自动决定合理的分镜数量。
- 在生成任何付费媒体前，要求用户审核完整脚本。
- 脚本审核会逐个分镜展示完整画面内容和全部口播原文，不会只给大纲或摘要。
- 使用固定风格锚点和角色设定图保持跨分镜的一致性。
- 支持 OpenAI 兼容图片接口，图像模型固定为 `gpt-image-2`。
- 支持 Xiaomi MiMo 预设音色和声音设计，也支持本地 Kokoro 回退方案。
- 按视觉分镜生成连续口播，再把短字幕对齐到自然停顿，减少短句 TTS 的机械感。
- 可选使用本地 MusicGen 生成背景音乐，默认不生成 BGM 和音效。
- 使用 HyperFrames 构建 1920x1080、30 fps 的横屏视频。
- 最终通过 FFprobe 验证视频流、音频流、分辨率、帧率和时长。
- 图片与音频任务带有清单和断点恢复能力，避免重复执行已经完成的付费请求。

单个项目最多支持 600 个分镜，最终时长不能超过 900 秒。

## 工作流程

1. 环境预检和用户需求收集。
2. 生成并校验 `story.json`。
3. 向用户展示完整脚本，包括每个分镜的画面内容和全部口播，等待明确确认。
4. 生成风格锚点、角色设定图和所有分镜图，统一等待一次视觉确认。
5. 根据需要试听并确认音色，生成分镜级连续口播和字幕时间轴。
6. 可选生成背景音乐。
7. 构建并检查 HyperFrames 项目。
8. 渲染画面轨道，混入已校验的口播和可选 BGM。
9. 使用 FFprobe 校验最终 MP4 后交付。

Skill 不会从用户沉默中推断审批。脚本和视觉内容都必须获得明确确认后才能进入下一阶段。

## 安装

### 方法一：让智能体自动安装

在 Codex 中新建一个任务，直接发送下面的指令：

```text
请使用 $skill-installer 安装下面的 Codex Skill：

仓库：https://github.com/niuhuoshan/generate-comic-drama-video
分支：main
仓库内路径：.
安装名称：generate-comic-drama-video

安装完成后检查 SKILL.md 是否存在，并告诉我安装结果。
```

也可以让智能体直接执行安装脚本：

```text
请运行 Codex 自带的 skill-installer，将 niuhuoshan/generate-comic-drama-video 仓库 main 分支的根目录安装为 generate-comic-drama-video。安装后不要运行媒体生成，只验证 Skill 是否安装成功。
```

安装完成后，在下一个 Codex 任务中即可使用该 Skill。

### 方法二：使用安装脚本

Windows PowerShell：

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$Installer = Join-Path $CodexHome "skills\.system\skill-installer\scripts\install-skill-from-github.py"

python $Installer `
  --repo niuhuoshan/generate-comic-drama-video `
  --path . `
  --ref main `
  --name generate-comic-drama-video
```

macOS 或 Linux：

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

python3 "$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo niuhuoshan/generate-comic-drama-video \
  --path . \
  --ref main \
  --name generate-comic-drama-video
```

安装器会把 Skill 放到：

```text
$CODEX_HOME/skills/generate-comic-drama-video
```

如果未设置 `CODEX_HOME`，默认位置为：

- Windows：`%USERPROFILE%\.codex\skills\generate-comic-drama-video`
- macOS/Linux：`~/.codex/skills/generate-comic-drama-video`

如果目标目录已经存在，安装器会停止以保护现有文件。请先备份已有版本，或者使用下面的 Git 安装方式维护更新。

### 方法三：使用 Git 手动安装

Windows PowerShell：

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$Destination = Join-Path $CodexHome "skills\generate-comic-drama-video"

git clone git@github.com:niuhuoshan/generate-comic-drama-video.git $Destination
```

macOS 或 Linux：

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
git clone git@github.com:niuhuoshan/generate-comic-drama-video.git \
  "$CODEX_HOME/skills/generate-comic-drama-video"
```

通过 Git 安装后，可以这样更新：

```bash
git -C "$CODEX_HOME/skills/generate-comic-drama-video" pull --ff-only
```

Windows PowerShell 更新命令：

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
git -C (Join-Path $CodexHome "skills\generate-comic-drama-video") pull --ff-only
```

## 安装验证

Windows PowerShell：

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
Test-Path (Join-Path $CodexHome "skills\generate-comic-drama-video\SKILL.md")
```

macOS 或 Linux：

```bash
test -f "${CODEX_HOME:-$HOME/.codex}/skills/generate-comic-drama-video/SKILL.md" && echo "Skill installed"
```

验证成功后，请新建一个 Codex 任务，或者在下一轮对话中显式调用：

```text
$generate-comic-drama-video 帮我制作一部横屏漫剧，主题是：一名深夜代驾意外发现乘客来自十年后。
```

## 环境要求

基础环境：

- Python 3
- Node.js 22 或更高版本
- `npx`
- Chrome 或 Chromium
- FFmpeg 和 FFprobe
- HyperFrames
- Codex 的 `imagegen` CLI

默认推荐使用外部图片服务和 Xiaomi MiMo TTS。只有启用本地回退能力时，才需要安装对应的额外依赖：

- 本地 Kokoro：`kokoro-onnx`、`soundfile`，非英语音素可能还需要 `espeak-ng`
- 本地 MusicGen：`transformers`、`torch`、`soundfile`、`numpy`

首次使用前运行预检。

Windows PowerShell：

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$ComicSkill = Join-Path $CodexHome "skills\generate-comic-drama-video"

python (Join-Path $ComicSkill "scripts\preflight.py") `
  --image-provider external `
  --tts-provider xiaomi_mimo `
  --json
```

macOS 或 Linux：

```bash
COMIC_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/generate-comic-drama-video"

python3 "$COMIC_SKILL/scripts/preflight.py" \
  --image-provider external \
  --tts-provider xiaomi_mimo \
  --json
```

只有明确需要本地背景音乐时，才在预检命令中添加 `--bgm`。

## 服务配置

### 图片服务

图片服务需要兼容 OpenAI Images API，并支持 `gpt-image-2`、图片生成、图片编辑、多张参考图输入和 Base64 图片返回。

Windows PowerShell：

```powershell
$env:COMIC_IMAGE_BASE_URL = "https://provider.example/v1"
$env:COMIC_IMAGE_API_KEY = "your-api-key"
$env:COMIC_IMAGE_MODEL = "gpt-image-2"
```

macOS 或 Linux：

```bash
export COMIC_IMAGE_BASE_URL="https://provider.example/v1"
export COMIC_IMAGE_API_KEY="your-api-key"
export COMIC_IMAGE_MODEL="gpt-image-2"
```

### Xiaomi MiMo TTS

Windows PowerShell：

```powershell
$env:COMIC_TTS_BASE_URL = "https://api.xiaomimimo.com/v1"
$env:COMIC_TTS_API_KEY = "your-api-key"
```

macOS 或 Linux：

```bash
export COMIC_TTS_BASE_URL="https://api.xiaomimimo.com/v1"
export COMIC_TTS_API_KEY="your-api-key"
```

API Key 只能通过环境变量配置。不要把密钥写入提示词、`story.json`、源码、日志或清单文件。

## 使用示例

基础请求：

```text
$generate-comic-drama-video 制作一部横屏悬疑漫剧：一个独居老人每天都会收到已故妻子寄来的明信片。使用中文男声，不要背景音乐。
```

带视觉参考：

```text
$generate-comic-drama-video 根据我提供的参考图制作一部都市情感漫剧。保持角色服装和发型一致，旁白使用第三人称，字幕每条不超过 22 个汉字。
```

试听声音：

```text
$generate-comic-drama-video 在正式生成配音前，为同一段口播生成几个 Xiaomi MiMo 男声音色样本，让我确认后再继续。
```

智能体会先询问仍然缺失的必要信息，然后执行环境预检。主题以外的可选项未指定时，将使用 Skill 中定义的默认值。

## 目录结构

```text
generate-comic-drama-video/
├── SKILL.md
├── Readme.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── example-story.json
│   ├── showcase/
│   └── vendor/
├── references/
│   ├── workflow.md
│   ├── runtime.md
│   ├── production-lessons.md
│   └── story.schema.json
├── scripts/
│   ├── preflight.py
│   ├── validate_story.py
│   ├── generate_visuals.py
│   ├── generate_scene_audio.py
│   ├── generate_voice_previews.py
│   ├── generate_bgm.py
│   ├── build_hyperframes.py
│   └── finalize_video.py
└── tests/
```

`SKILL.md` 是智能体执行工作流的入口，`references/` 保存运行规范和数据契约，`scripts/` 提供可恢复的确定性媒体处理工具。

## 常见问题

### 为什么安装后当前对话没有触发 Skill？

新安装的 Skill 通常在下一轮或新任务中可用。新建任务并显式输入 `$generate-comic-drama-video` 即可。

### 为什么不能直接开始生成图片？

Skill 会先完成环境预检和完整脚本审核。这样可以在付费生成前修正故事、分镜和口播，减少返工成本。

### 为什么脚本预览很长？

用户需要确认最终进入配音的完整内容，因此预览必须包含每个分镜的画面和全部口播。长脚本可以分批展示，但不能只提供大纲。

### 是否必须生成背景音乐？

不必须。默认不生成 BGM，也不生成音效。只有用户明确要求时才启用本地 MusicGen。

### 中途失败会从头开始吗？

不会。图片和音频阶段会保存清单及已完成文件。恢复运行时会跳过已经验证完成的任务。

## 许可证

许可证内容见仓库根目录的 [LICENSE](LICENSE)。
