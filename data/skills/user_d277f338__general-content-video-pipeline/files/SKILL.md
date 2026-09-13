---
name: general-content-video-pipeline
description: >
  通用「内容主题 → 成片视频」自动化管线。当用户需要把某类内容（故事、讲解、剧情）自动化为完整视频（AI文本→TTS语音→配图→视频合成→拼接intro/outro→存盘/发布）时使用。
  主入口脚本承载运行，支持每日定时从主题索引读取选题并生成完整视频。题材、路径、品牌均可通过配置化输入调整。
agent_created: true
---

# 通用内容视频自动化管线

## 概述

从「选题/主题」到「最终视频」的完整自动化管线。适合把周期性内容创作（每日/每周）自动化为视频产出。约定每日固定时刻由定时任务触发，生成当日内容视频。

## 配置化输入（必填，先确定）

| 配置 | 说明 | 示例 |
|------|------|------|
| `project_root` | 项目根目录 | `{project}/` |
| `out_root` | 成片输出目录（盘符/云端） | `{out}/{系列名}/{日期}_{标题}/` |
| `content_src` | 选题/主题来源 | `content_tagging.md` 或其它索引文件 |
| `main_script` | 主入口脚本 | `content_pipeline.py` |
| `tts_script` | TTS 引擎（含文本清理） | `unified_tts.py` |
| `video_assembler` | 视频合成引擎 | `video_assembler.py` |
| `concat_script` | intro/正文/outro 拼接 | `concat_video.py` |
| `pub_script` | 发布素材生成器（可选） | `publish_assets.py` |
| `font_zh / font_emoji` | 中文字体 / emoji 字体路径 | `C\:/Windows/Fonts/msyhbd.ttc` / `seguiemj.ttf` |
| `video_spec` | 分辨率、字幕安全区 | `1080×1920 竖屏` |
| `bgm_pattern` | 背景音乐按日循环 | 周一=mon ~ 周日=sun |

> 原技能耦合点（具体项目名、"睡前故事"题材、U盘路径、固定字体）统一由上述配置承载，任意周期性内容视频均可复用本管线骨架。

## 管线流程

```
主题/选题 → AI内容文本 → TTS语音(分句) → 场景配图生成 → 视频合成 → 拼接 intro/outro → 存入输出目录
```

## 工作规范

### TTS 文本清理
使用 TTS 引擎中的统一清理函数，不要直接传原始 markdown 给 TTS。
清理项：Markdown 标题(`#`)、粗体(`**`)、斜体(`*`)、列表标记(`- `、`1. `)、引用(`>`)、分隔线(`---`)、特殊符号（箭头/emoji 等颜文字）。

### emoji 渲染（横切复用）
FFmpeg drawtext 只支持单一字体，含 emoji 的文本必须拆成两条 drawtext：
- emoji → emoji 字体（如 seguiemj.ttf）
- 中文 → 中文字体（如 msyhbd.ttc）

使用 `ffmpeg-emoji-ass-subtitle` 技能的 `drawtext_util.py` 中 `build_emoji_text_drawtext()` 统一处理。

### 视频规格
- 分辨率、字幕位置：按 `video_spec` 配置（默认竖屏、底部安全区）
- intro/outro：`output/intro.mp4` / `output/outro.mp4`
- 背景音乐：`output/bgm_*.mp3`（按日循环）
- 尺寸不统一时统一处理：`scale=W:H:force_original_aspect_ratio=increase,crop=W:H`

### 日期验证（工程安全）
**永远不要硬编码日期而不验证星期！**
```python
# 每次硬编码日期时验证：
from datetime import date
assert date.fromisoformat("2026-06-29").weekday() == 0, "必须是周一！"
```

## 手动运行

```bash
cd {project_root}
python {main_script} --story-title "标题" --theme 主题 --character 角色
```

## 每日自动化
每日定时任务执行完整管线：
1. 从 `content_src` 读取今日选题
2. 生成内容文本（AI 生成）
3. 生成 TTS 语音
4. 生成配图
5. 合成视频
6. 拼接 intro/outro
7. 发布素材生成（可选）

## 相邻技能
- 配图/封面：`content-illustration-packager`
- 多平台发布包：`multi-platform-publish-assets`
- 素材入库：`filesystem-scan-to-db`
- 构建站点：`sqlite-static-site-build-deploy`