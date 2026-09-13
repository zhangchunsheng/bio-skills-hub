# 导出 docx 工作流

> v2.0.0 新增。提供三种方案，用户按需选择。

## 方案选择

| 方案 | 适用 | 优点 | 缺点 |
|---|---|---|---|
| tencent-docx（推荐） | 用户在 本技能生态 生态内 | 中文排版规范、原生 .docx、可二次编辑 | 需腾讯文档账号 |
| pandoc | 跨平台脚本化 | 命令简单、支持 LaTeX 数学公式 | 中文排版需自定义 |
| python-docx | 完全本地化、可定制 | 灵活、可批处理 | 需安装 python-docx 包 |

## 方案 1：tencent-docx（推荐）

通过 本技能生态 的 tencent-docx 技能：

```text
用户："导出第 8 章到 /Users/.../第8章-XXX.docx，使用中文出版排版规范"

技能：
  1. 读取 chapter-008.md
  2. 应用排版（宋体正文、黑体标题、首行缩进、1.5 倍行距）
  3. 调用 tencent-docx 技能
  4. 上传到腾讯文档
  5. 下载为 .docx
  6. 移动到用户指定路径
```

排版规范：

- 字体：宋体（中文）/ Times New Roman（英文）
- 一级标题：黑体 22pt 居中
- 二级标题：黑体 16pt
- 正文：宋体 12pt
- 首行缩进：2 字符
- 行距：1.5 倍
- 段间距：段前 0.5 行 / 段后 0.5 行

## 方案 2：pandoc

```bash
# 安装 pandoc
brew install pandoc  # macOS
# 或
sudo apt install pandoc  # Linux

# 安装中文字体（确保中文正常显示）
# macOS：系统自带 PingFang/Heiti
# Linux：安装 wqy-microhei 或 wqy-zenhei

# 转换命令
pandoc chapter-008.md \
  -f markdown \
  -t docx \
  --reference-doc=template.docx \
  -o 第8章-XXX.docx

# 应用中文出版排版（需自定义 reference-doc）
```

template.docx 自定义字段：

- 字体（宋体/黑体）
- 标题样式（一级/二级）
- 行距
- 首行缩进
- 段落间距

详见 [pandoc 参考文档](https://pandoc.org/MANUAL.html)。

## 方案 3：python-docx

```bash
# 安装
pip install python-docx
```

封装脚本：

```python
# scripts/export-to-docx.py
"""
将 chapter-NNN.md 导出为符合中文出版排版规范的 .docx

使用：
  python3 scripts/export-to-docx.py \
    --chapter chapter-008.md \
    --output 第8章-XXX.docx
"""
```

排版要点：

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

doc = Document()

# 设置默认字体
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(12)

# 一级标题：黑体 22pt 居中
h1 = doc.styles['Heading 1']
h1.font.name = '黑体'
h1.font.size = Pt(22)
h1.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

# 行距 1.5 倍
style.paragraph_format.line_spacing = 1.5

# 首行缩进 2 字符
style.paragraph_format.first_line_indent = Cm(0.74)  # 约 2 字符
```

详见 `scripts/export-to-docx.py` 完整实现。

## 输出命名

按用户偏好使用中文出版排版命名：

```
第N章-标题.docx
```

章节标题从 `.md` 的首个 `# 第 N 章` 提取。

如需转换命名（`chapter-001.md` ↔ `第1章-标题.docx`），使用 `scripts/chapter-rename.py`。

## 与写作马拉松工作流的对接

默认输出到：

```
{project-root}/novels/{slug}/docx/
```

或用户指定的：

- `02 本技能生态 工作区/写作马拉松/作品/`
- `20 OPC 项目/10 写作马拉松/`

详见 `references/chapter-rename.md`。

## 导出后处理

- 自动备份原 .md
- 自动更新 meta.json 中的 `last_export_at`
- 自动写入 `CHANGELOG.md`（如项目内有）
- 提示用户手动校验排版效果

## 批量导出

```bash
# 批量导出所有章节
python3 scripts/export-to-docx.py \
  --chapter-dir novels/{slug}/chapters/ \
  --output-dir novels/{slug}/docx/

# 或

for f in novels/{slug}/chapters/chapter-*.md; do
  python3 scripts/export-to-docx.py \
    --chapter "$f" \
    --output-dir novels/{slug}/docx/
done
```

## 排版差异处理

不同流派/平台的排版差异：

| 流派 | 段间距 | 行距 | 字号 |
|---|---|---|---|
| 起点中文网爽文 | 紧 | 1.5 | 12pt |
| 微信公众号 | 松 | 1.75 | 14pt |
| 出版书 | 标准 | 单倍 | 11pt（实际） |
| 晋江文学城言情 | 紧 | 1.5 | 12pt |

详见 `references/style-control.md` 的平台调性卡。

## 常见问题

### Q1：中文字体在 .docx 中显示异常？

A：检查 .docx 的字体嵌入设置，或在 Word 中手动指定字体。

### Q2：行距不生效？

A：检查 style 设置，或在导出脚本中强制应用。

### Q3：首行缩进过大？

A：调整 first_line_indent 数值。中文 2 字符 ≈ 0.74cm，但不同字体有差异。

详见 `references/style-control.md`。
