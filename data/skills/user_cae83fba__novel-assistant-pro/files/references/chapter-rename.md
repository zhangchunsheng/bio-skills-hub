# 章节命名互转（chapter-rename.md）

> v2.0.0 新增。在 `chapter-NNN.md` 与 `第N章-标题.docx` 之间互转。

## 命名风格对比

| 风格 | 适用场景 | 优点 | 缺点 |
|---|---|---|---|
| `chapter-001.md` | 工程化、技能自动化、版本管理 | 易排序、跨平台、易脚本处理 | 不直观、与中文出版习惯不符 |
| `第1章-标题.docx` | 中文出版、写作马拉松工作流、交付 | 直观、符合用户偏好 | 难排序、特殊字符处理复杂 |

## 互转规则

### `chapter-NNN.md` → `第N章-标题.docx`

```text
chapter-001.md       →   第1章-{标题}.docx
chapter-002.md       →   第2章-{标题}.docx
chapter-099.md       →   第99章-{标题}.docx
chapter-100.md       →   第100章-{标题}.docx
```

**标题来源**：从 `.md` 文件的第一个 `# 第 N 章 xxx` 标题提取 xxx 部分。

### `第N章-标题.docx` → `chapter-NNN.md`

```text
第1章-港口爆炸.docx     →   chapter-001.md
第10章-真相浮现.docx    →   chapter-010.md
第100章-最终对决.docx   →   chapter-100.md
```

**编号补零**：3 位补零。

## 转换脚本

```bash
# 单个文件转换
python3 scripts/chapter-rename.py \
  --input chapter-001.md \
  --output "第1章-港口爆炸.docx" \
  --title "港口爆炸"

# 批量转换（整个目录）
python3 scripts/chapter-rename.py \
  --batch novels/{slug}/chapters/ \
  --direction md-to-docx \
  --output-dir novels/{slug}/docx/

# 反向转换
python3 scripts/chapter-rename.py \
  --batch novels/{slug}/docx/ \
  --direction docx-to-md \
  --output-dir novels/{slug}/chapters/

# 自动检测方向
python3 scripts/chapter-rename.py \
  --auto novels/{slug}/chapters/ novels/{slug}/docx/
```

## 与写作马拉松工作流的对接

用户的写作马拉松默认目录：

```
02 本技能生态 工作区/写作马拉松/作品/{slug}/
```

写作马拉松 Word 归档目录：

```
20 OPC 项目/10 写作马拉松/{slug}/
```

章节文件命名：

```
第N章-标题.docx
```

转换示例：

```bash
# 把 chapter 文件转换到写作马拉松目录
python3 scripts/chapter-rename.py \
  --batch novels/{slug}/chapters/ \
  --direction md-to-docx \
  --output-dir "02 本技能生态 工作区/写作马拉松/作品/{slug}/"

# 或使用 export-to-docx 直接生成 docx
python3 scripts/export-to-docx.py \
  --chapter-dir novels/{slug}/chapters/ \
  --output-dir "20 OPC 项目/10 写作马拉松/{slug}/"
```

## 标题提取规则

从 `.md` 文件提取章节标题：

```python
import re

def extract_title(content: str, chapter_num: int) -> str:
    # 匹配 # 第 N 章 标题
    patterns = [
        rf'^# 第\s*{chapter_num}\s*章\s*[：:\s]*(.+)$',
        rf'^# Chapter\s*{chapter_num}\s*[：:\s]*(.+)$',
        rf'^# {chapter_num}\s*[：:\s]*(.+)$',
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            # 清理非法文件名字符
            title = re.sub(r'[\\/:*?"<>|]', '', title)
            return title
    return f'第{chapter_num}章'  # 默认标题
```

## 特殊字符处理

docx 文件名不能包含：

```
\ / : * ? " < > |
```

转换时自动替换：

| 原文 | 替换 |
|---|---|
| `?` | `_` |
| `:` | `_` |
| `*` | `_` |
| `"` | `''` |
| `<` `>` | `(` `)` |
| `\` `/` | `_` |
| `|` | `_` |

## 文件名长度限制

- Windows：255 字符（含路径）
- macOS：255 字符
- Linux：255 字符（但建议 < 100）

建议章节标题 ≤ 30 字符，避免文件名过长。

## 与Baidu 网盘同步

章节文件命名使用 `第N章-标题.docx` 后，可直接同步到Baidu 网盘：

```
20 OPC 项目/10 写作马拉松/{slug}/
├── 第1章-港口爆炸.docx
├── 第2章-残片追踪.docx
└── ...
```

Baidu 网盘自动按文件名排序，章节顺序保持。

详见 `AGENTS.md` 中的跨设备备份部分。
