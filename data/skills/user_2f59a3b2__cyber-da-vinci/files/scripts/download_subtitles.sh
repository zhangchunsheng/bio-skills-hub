#!/bin/bash
# download_subtitles.sh - 从YouTube/B站下载视频字幕
# 用法: bash download_subtitles.sh <视频URL> [输出目录]
# 优先级: 人工字幕(中文) > 人工字幕(英文) > 自动生成字幕(中文) > 自动生成字幕(英文)

set -e

VIDEO_URL="$1"
OUTPUT_DIR="${2:-.}"

if [ -z "$VIDEO_URL" ]; then
  echo "用法: bash download_subtitles.sh <视频URL> [输出目录]"
  echo "示例: bash download_subtitles.sh https://www.youtube.com/watch?v=xxxxx ./sources/transcripts/"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "========================================="
echo "字幕下载工具 - 赛博达芬奇·Skill"
echo "目标URL: $VIDEO_URL"
echo "输出目录: $OUTPUT_DIR"
echo "========================================="

# 检查 yt-dlp 是否可用
if ! command -v yt-dlp &> /dev/null; then
  echo "[INFO] yt-dlp 未安装，尝试使用 pip 安装..."
  pip install yt-dlp -q
fi

echo "[STEP 1] 检查可用字幕..."
yt-dlp --list-subs "$VIDEO_URL" 2>/dev/null | head -50 || true

echo ""
echo "[STEP 2] 尝试下载人工字幕（中文优先）..."
DOWNLOADED=false

# 尝试1：人工中文字幕
if yt-dlp \
  --skip-download \
  --write-subs \
  --sub-lang "zh-Hans,zh-Hant,zh,cmn" \
  --sub-format "srt/vtt/best" \
  --no-warnings \
  -o "$OUTPUT_DIR/%(title)s.%(ext)s" \
  "$VIDEO_URL" 2>/dev/null; then
  
  # 检查是否真的下载了字幕文件
  if ls "$OUTPUT_DIR"/*.srt 2>/dev/null || ls "$OUTPUT_DIR"/*.vtt 2>/dev/null; then
    echo "[✓] 成功下载中文字幕"
    DOWNLOADED=true
  fi
fi

# 尝试2：人工英文字幕
if [ "$DOWNLOADED" = false ]; then
  echo "[STEP 3] 尝试下载人工字幕（英文）..."
  if yt-dlp \
    --skip-download \
    --write-subs \
    --sub-lang "en,en-US,en-GB" \
    --sub-format "srt/vtt/best" \
    --no-warnings \
    -o "$OUTPUT_DIR/%(title)s.%(ext)s" \
    "$VIDEO_URL" 2>/dev/null; then
    
    if ls "$OUTPUT_DIR"/*.srt 2>/dev/null || ls "$OUTPUT_DIR"/*.vtt 2>/dev/null; then
      echo "[✓] 成功下载英文字幕"
      DOWNLOADED=true
    fi
  fi
fi

# 尝试3：自动生成中文字幕
if [ "$DOWNLOADED" = false ]; then
  echo "[STEP 4] 尝试下载自动生成字幕（中文）..."
  if yt-dlp \
    --skip-download \
    --write-auto-subs \
    --sub-lang "zh-Hans,zh-Hant,zh" \
    --sub-format "srt/vtt/best" \
    --no-warnings \
    -o "$OUTPUT_DIR/%(title)s.%(ext)s" \
    "$VIDEO_URL" 2>/dev/null; then
    
    if ls "$OUTPUT_DIR"/*.srt 2>/dev/null || ls "$OUTPUT_DIR"/*.vtt 2>/dev/null; then
      echo "[✓] 成功下载中文自动字幕（注意：质量可能较低）"
      DOWNLOADED=true
    fi
  fi
fi

# 尝试4：自动生成英文字幕
if [ "$DOWNLOADED" = false ]; then
  echo "[STEP 5] 尝试下载自动生成字幕（英文）..."
  if yt-dlp \
    --skip-download \
    --write-auto-subs \
    --sub-lang "en" \
    --sub-format "srt/vtt/best" \
    --no-warnings \
    -o "$OUTPUT_DIR/%(title)s.%(ext)s" \
    "$VIDEO_URL" 2>/dev/null; then
    
    if ls "$OUTPUT_DIR"/*.srt 2>/dev/null || ls "$OUTPUT_DIR"/*.vtt 2>/dev/null; then
      echo "[✓] 成功下载英文自动字幕（注意：质量可能较低）"
      DOWNLOADED=true
    fi
  fi
fi

if [ "$DOWNLOADED" = false ]; then
  echo "[✗] 未能下载任何字幕"
  echo "可能原因："
  echo "  1. 该视频没有字幕"
  echo "  2. URL 格式有误"
  echo "  3. 视频有地区限制"
  echo "  4. yt-dlp 版本过旧，请运行: pip install -U yt-dlp"
  exit 1
fi

echo ""
echo "========================================="
echo "下载完成！字幕文件："
ls -la "$OUTPUT_DIR"/*.srt "$OUTPUT_DIR"/*.vtt 2>/dev/null || true
echo ""
echo "下一步：运行字幕清洗脚本"
echo "  python3 srt_to_transcript.py <字幕文件路径> [输出txt路径]"
echo "========================================="
