---
name: mindmap
description: 生成基于认知科学方法论的交互式思维导图。支持 Markdown 大纲或 JSON 输入，一条命令同时导出 HTML（可交互编辑、8 种布局、深浅双主题）、PNG、JPG、SVG、PDF、XMind，并自动输出结构质检报告。Generate cognitive-science-grounded interactive mind maps from Markdown outlines or JSON; one command exports HTML/PNG/JPG/SVG/PDF/XMind with dark & light themes and a built-in structure quality report. 当用户提到"思维导图 / 脑图 / mind map"、要求把文章、笔记、会议纪要、学习内容"梳理成结构 / 可视化"、或要求导出 XMind/PNG/PDF 结构图时，务必使用本技能 —— 即使用户没有明确说出"思维导图"三个字。
user-invocable: true
metadata: {"openclaw": {"requires": {"bins": ["python3"], "pip": ["pillow"]}}}
---

# Mind Map Generator — 思维导图生成器

把内容提炼成放射状知识结构，一条命令导出多种格式。核心特色：

- **Markdown 大纲直接输入** —— 不必手写 JSON，也没有 shell 引号转义问题
- **一次生成多格式** —— `--format html,png,xmind` 一条命令搞定
- **深空 / 纸墨双主题** —— `--theme midnight|paper`，HTML 内还有 🌓 一键切换
- **结构质检报告** —— 自动按认知负荷·双重编码·渐进分化·MECE·概念图关系等原则检查，输出改进建议
- **交互式 HTML** —— 双击编辑、Enter 加兄弟 / Tab 加子节点、拖到另一节点上改挂父子关系、拖到空白处按位置重排兄弟顺序（拖动后始终自动整齐布局，不会拉乱连线）、拖根平移全图、8 种布局、右键菜单；节点标签超过 20 字符自动省略（…）保持版面整洁，双击节点在编辑框中查看并修改完整内容；点「HTML」按钮绑定文件后，之后每次改动自动写回该 HTML 文件（Chrome/Edge），不支持时回退为下载含全部编辑的自包含文件

## 快速开始（推荐工作流）

**第一步**：按 [内容设计方法](#内容设计四步法) 提炼结构，写入一个 Markdown 大纲文件（避免把内容塞进 shell 参数——引号和特殊字符会出问题）：

```bash
cat > /tmp/mindmap_outline.md << 'EOF'
# 中心洞见（一句话，不是话题标签）

## 🔬 维度一 [#4A90D9]
- 具体证据 A
- 量化数据 B
  - 更具体的事实

## 💰 维度二 [#27AE60]
- 证据 C
- 证据 D
EOF
```

语法规则：`#` 一级标题 = 中心节点；`##` = 主分支（可在行尾用 `[#十六进制]` 指定颜色）；`-` 列表按缩进（2 空格一层）嵌套为子节点。也可以省略 `#` 标题，此时 `--title` 会作为中心节点。

**第二步**：一条命令生成全部格式：

```bash
python3 {baseDir}/generate_mindmap.py \
  --title "主题名" \
  --format html,png,xmind \
  --data-file /tmp/mindmap_outline.md \
  --output "主题名.html"
```

`--output` 只需给一个路径，其余格式自动换扩展名。省略 `--output` 时自动选择输出目录：`$MINDMAP_OUTPUT_DIR` → `/mnt/user-data/outputs`（Claude 沙箱）→ `~/.openclaw/workspace`（OpenClaw）→ 当前目录。

**第三步**：查看 stderr 中的质检报告（`📋` 一行摘要 + `⚠` 警告）。如出现警告（分支超过 6 个、总节点超 40、标签过长、单子节点分支等），先修改大纲再重新生成，不要把警告丢给用户。

**第四步**：向用户汇报，必须包含脚本 stdout 中 `✅ ... → 路径` 的完整绝对路径，并说明各格式用途：HTML 浏览器打开可交互编辑（双击改文字、Enter 加兄弟节点、Tab 加子节点、把一个节点拖到另一个节点上可改变其父子归属、拖动中心节点平移整图、右上角切主题；点「HTML」按钮绑定文件后，在 Chrome/Edge 中之后的改动会自动保存回该文件，其它浏览器则每次点按钮另存为含全部改动的新文件）、PNG 直接嵌入文档分享、XMind 可在 XMind 软件继续编辑。

## 输入格式

**Markdown 大纲**（首选，见上）。**JSON**（需要精确控制时）：

```json
{
  "central": "核心洞见",
  "branches": [
    {"label": "🔬 维度一", "color": "#4A90D9",
     "children": ["证据A", {"label": "证据B", "children": ["事实1", "事实2"]}]}
  ]
}
```

JSON 也通过 `--data-file` 传入（自动识别 JSON / Markdown）；`--data-file -` 读 stdin；`--data '...'` 仅限极短内容。主分支若缺 emoji，脚本会按语义关键词自动补充。

## 命令参考

| 参数 | 说明 |
|------|------|
| `--title` | 必填。导图标题（大纲无 `#` 标题时兼作中心节点） |
| `--data-file` | 数据文件路径（JSON 或 Markdown），`-` 为 stdin |
| `--data` | 内联数据字符串（仅限短内容） |
| `--format` | 逗号分隔多格式：`html,svg,png,jpg,pdf,xmind`（默认 html） |
| `--theme` | `midnight` 深空（默认）/ `paper` 纸墨（适合打印、白底文档） |
| `--output` | 输出路径；多格式时自动换扩展名；省略则用自适应工作目录 |
| `--scale` | PNG/JPG/PDF 像素密度，默认 2.0 |
| `--quality` | JPG 质量 1–100，默认 92 |
| `--no-lint` | 关闭质检报告 |
| `--no-auto-install` | 禁止自动安装 Pillow，仅打印安装指引 |

## 内容设计四步法

完整的认知科学依据（Buzan 放射性思考、Paivio 双重编码、Miller/Sweller 认知负荷、语义网络、Ausubel 渐进分化、MECE 完全穷尽、Novak 概念图关系）与详细规范见 `{baseDir}/references/methodology.md`——生成前先读它。执行时的硬约束：

1. **中心节点 = 核心洞见**，不是话题标签。✅ "AI 正从工具变为协作者"；❌ "AI 发展趋势"。
2. **主分支 3–6 个 = 理解维度**，不是原文章节。同级抽象层次一致，每个分支带一个不重复的 emoji，颜色与语义一致（蓝=机制、绿=成果、橙=问题、紫=背景、黄=资源、青=流程、红=警告）。定稿前做 **MECE 自检**：这些维度是否**完全穷尽**了主题、有无遗漏或重叠（总结类任务尤其关键）。
3. **子节点 = 具体证据**（机制、数据、案例、对比、行动、限制），每分支 2–5 个，优先可想象的具体词。**渐进分化**：从中心到叶子概括度逐层递减，不出现"子节点比父节点更宽泛"的倒挂。
4. **节点 4–12 字**、全图 ≤ 40 节点、≤ 4 层。主题内在复杂度过高时**拆成多张图**而非硬压缩。生成后核对质检报告（会提示 MECE、渐进分化、关系型表述等）。

**关系表达（概念图）**：内容里若是因果/时序/对比/条件等**非从属**关系，别硬塞进父子层级——因果优先鱼骨图、时序优先时间线，或在措辞里保留关系词（"导致""优于""若…则"），避免把关系信息压扁丢失。

按内容类型选维度框架与布局：分析类"是什么·为什么·怎么做·结果"（左右均衡）；问题解决"根因·影响·方案·评估"（鱼骨图）；学习类"概念·机制·场景·误区"；项目类"目标·策略·执行·风险"（树形）；时间/流程类按顺序（时间线）；头脑风暴自由发散（辐射/力导向）。布局在 HTML 中随时可切换。

## 依赖与故障排除

- **零系统级 C 库依赖。** HTML/SVG/XMind 纯 Python；PNG/JPG/PDF 需 Pillow（`pip install pillow`）。若检测到 Playwright 则优先用它渲染 PNG/JPG（质量更高、保留 emoji）。
- Pillow 缺失时脚本会尝试 `pip install pillow`（先普通安装、再 `--user`，**绝不**使用 `--break-system-packages`）；在受管环境失败会打印指引。共享或锁定环境请加 `--no-auto-install` 并让用户自行安装。
- Pillow 后备渲染会去掉 emoji（系统字体不含彩色 emoji）；若用户在意 emoji 的图片效果，安装 Playwright 或让用户在 HTML 中用浏览器导出。
- 中文乱码/方块：Pillow 渲染依赖系统 CJK 字体（微软雅黑 / PingFang / Noto CJK），Linux 无 CJK 字体时建议 `apt install fonts-noto-cjk`。

## 内置示例

`{baseDir}/examples/`：`ai_trends.html`、`product_launch.html`、`python_learning.html`（可直接用浏览器打开体验交互与主题切换），以及对应 `.json` 数据和 `outline_example.md` 大纲示例。
