# 审查脚本已知误判

`review.py` 在对含 heredoc 安装块的 SKILL.md 进行审查时，会将安装块内的代码当作普通 markdown 正文解析，产生以下误报：

## 常见误报类型

| 误报检查项 | 触发原因 | 示例 |
|-----------|---------|------|
| Dead links | Python 正则表达式中的 `[...](...)` 被误解析为 markdown 链接 | `r"subprocess\.(?:run|call)\s*\(\s*\[['\"]([\w-]+)"` → `([\w-]+)` 被当作 `[label](url)` |
| Install block syntax | heredoc 内容中的文本被误判为定界符 | 代码内出现 `EOF` 字符串被当作未闭合的 heredoc |
| Brand names | 安装块内嵌 HTML/CSS 中的类名 | `id="agent-content"` / `.agent-sidebar` |

## 处理原则

**凡因 heredoc 安装块内嵌代码内容触发的审查失败，一律直接忽略。** 这是审查脚本的架构局限——它无法区分"markdown 正文"和"heredoc 内的代码"。

## 排除方法

审查时关注失败项的来源文件和行号：
- 若行号落在 `## 安装` 章节之后 → 大概率是误报
- 若错误内容看起来像代码（正则、变量名等）→ 确认是安装块内容 → 忽略

## 记录

首次发现：2026-07-04，打包 `general-skill-publisher` 自举时。
