# 7 种输入格式处理

> **步骤 2（读取）按输入格式分支处理**。每种格式对应不同的工具链。

---

## 1. PDF 文件（.pdf）

**工具**：pdfplumber / PyPDF2 / OCR 兜底

**流程**：
```python
import pdfplumber
with pdfplumber.open(path) as pdf:
    text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)
```

**失败兜底**：纯扫描件 → tesseract OCR 兜底；OCR 失败 → 提示用户"换格式"

**输出**：
```python
{
  "title": pdf.metadata.get("Title", path.stem),
  "content": text,
  "source_type": "pdf",
  "raw_path": path,
  "chars": len(text)
}
```

## 2. Word 文档（.docx）

**工具**：python-docx

**流程**：
```python
from docx import Document
doc = Document(path)
text = "\n\n".join(p.text for p in doc.paragraphs)
```

**图片处理**：可选项（是否提取 docx 内图片作为配图）

**输出**：
```python
{
  "title": doc.core_properties.title or path.stem,
  "content": text,
  "source_type": "docx",
  "raw_path": path,
  "chars": len(text)
}
```

## 3. Markdown（.md 或文件夹）

**工具**：直读

**单文件**：
```python
text = Path(path).read_text(encoding="utf-8")
```

**文件夹**（GitHub 仓库等）：
```python
files = glob("**/*.zh-Hans.md", recursive=True)  # 优先 .zh-Hans.md
text = "\n\n---\n\n".join(f"## {f}\n\n{Path(f).read_text()}" for f in files)
```

**输出**：
```python
{
  "title": path.stem,
  "content": text,
  "source_type": "markdown",
  "raw_path": path,
  "chars": len(text)
}
```

## 4. URL（网页文章）

**工具**：requests + readability + html2text

**流程**：调 `links-pipeline/scripts/extract_article.py`

**输出**：
```python
{
  "title": "文章标题",
  "content": "Markdown 化正文",
  "source_type": "url",
  "raw_path": url,
  "chars": len(content)
}
```

## 5. GitHub 本地仓库路径（文件夹）

**工具**：glob + read

**流程**：
```python
# 优先读 README.zh-Hans.md
readme = Path(repo_path) / "README.zh-Hans.md"
if readme.exists():
    main_content = readme.read_text()
# 附加各章节
stages = glob("stages/*.zh-Hans.md")
resources = glob("resources/*.zh-Hans.md")
all_text = main_content + "\n\n" + "\n\n---\n\n".join(...)
```

**用户可指定子集**："只解读 stages/" 或 "只读 resources/agent-paradigms.zh-Hans.md"

**输出**：
```python
{
  "title": repo_path.stem,
  "content": all_text,
  "source_type": "github_repo",
  "raw_path": repo_path,
  "chars": len(text)
}
```

## 6. 视频链接（B 站/YouTube）

**工具**：yt-dlp + ffmpeg + Whisper

**流程**：调 `links-pipeline/scripts/download.py`
1. yt-dlp 下载视频
2. ffmpeg 提取音频（16kHz wav）
3. Whisper 转录（base 模型，language=zh）
4. 字幕交叉验证（如果平台有独立字幕流）
5. 大模型清洗（DeepSeek）

**输出**：
```python
{
  "title": "视频标题",
  "content": "转录文本（含时间戳）",
  "source_type": "video",
  "raw_path": video_url,
  "chars": len(transcript)
}
```

## 7. 抖音/小红书/公众号链接

**工具**：Playwright 移动端 UA 模拟

**流程**：调 `links-pipeline/scripts/douyin_download.py` 或 `extract_article.py`

- **抖音/小红书视频**：Playwright 抓 video src → 无水印地址 → 下载 → 转音频 → Whisper
- **小红书图文**：Playwright 抓正文 + 图片
- **公众号文章**：requests + readability（公众号限制少，requests 直接抓）

**输出**：
```python
{
  "title": "分享内容标题",
  "content": "正文 / 转录文本",
  "source_type": "douyin|xiaohongshu|wechat",
  "raw_path": share_url,
  "chars": len(content)
}
```

---

## 统一输出格式

**所有 7 种输入最后都输出 `SourceText`**：
```python
class SourceText:
    title: str          # 内容标题
    content: str        # 主体文本（Markdown 格式）
    source_type: str    # "pdf" | "docx" | "markdown" | "url" | "github_repo" | "video" | "douyin" | "xiaohongshu" | "wechat"
    raw_path: str       # 原始路径 / URL
    metadata: dict      # 额外元信息（作者、日期等）
    chars: int          # 字符数
```

## 失败兜底总则

| 失败场景 | 兜底策略 |
|---|---|
| PDF 纯扫描件 | tesseract OCR |
| URL 403/反爬 | Playwright 模拟 |
| 视频下载失败 | 提示用户"换源/换格式" |
| 抖音/小红书反爬升级 | 提示用户"换源" |
| 内容空 / 字符数 < 100 | 提示用户"内容太短" |
| 超时（5 分钟） | 提示用户重试或换源 |

**任一兜底失败 → 步骤 1 报错，不进入步骤 2**。
