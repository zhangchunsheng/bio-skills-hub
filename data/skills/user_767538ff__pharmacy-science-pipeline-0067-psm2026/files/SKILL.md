---
name: pharmacy-science-pipeline-0067-psm2026
description: 药学科普内容生产全流程 skill。覆盖「素材挖掘（权威指南/药品说明书）→ 选题表与五篇提纲（Word）→ 科普文章撰写（Word）→ 短视频脚本（Markdown）→ 竖屏 MP4 渲染（Python 兜底）」五阶段，一键把一次科普需求变成可直接发布的多形态成品。当用户提出「做个药学科普」「痛风/尿酸科普文章」「出个选题表」「写篇用药科普」「科普转短视频」「渲染科普视频」等需求时触发。内置高尿酸/痛风领域知识库（指南清单、关键阈值、药物要点、合规红线）与 Remotion 不可用时改用 Pillow+opencv 的渲染兜底方案。
agent_created: true
version: 1.0.0
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# 药学科普内容生产全流程（pharmacy-science-pipeline）

## 用途
把一次药学科普需求，按统一规范连续产出 **5 种形态**的成品：
1. **选题表 + 五篇提纲**（Word，.docx）
2. **科普文章**（Word，.docx，1500–2500 字/篇）
3. **短视频脚本**（Markdown，分镜/字幕/配音/BGM/互动）
4. **竖屏 MP4**（无声画面版，字幕已内嵌，9:16）
5. （可选）**长图/讲座要点卡**（由提纲的 B 段直接派生）

适用：药师/药剂科做公众号长文、门诊讲座、视频号/抖音短视频、患者教育物料。

## 何时使用
- 用户说「做个 XX 用药科普」「出个痛风科普选题」「把这篇文转短视频」「渲染个科普视频 MP4」。
- 关键词：药学科普、用药科普、痛风、尿酸、高血压、糖尿病、选题表、科普文章、短视频脚本、科普视频。
- 触发即走下面五阶段；用户可只走其中某阶段（如已有文章，只做脚本+视频）。

## 环境与关键约束（必读）
- **本沙箱 npm registry 被严重限速**（单个元数据请求约 89 秒），Remotion 依赖树数百包，实际无法 `npm install` → **渲染默认走 Python 路线**。
- 渲染依赖（managed python 3.13.12）：`...python.exe -m pip install pillow numpy opencv-python-headless`
- 文章/提纲依赖：`python-docx`（在 venv `C:/Users/Yen/.workbuddy/binaries/python/envs/default/Scripts/python.exe` 已验证可用）。
- 中文字体：Windows `C:/Windows/Fonts/msyh.ttc`（index 1 粗体）；Linux 回退 NotoSansCJK。
- **沙箱文件操作坑**：Python 内 `os.remove`/`mv` 会被拦截；重命名/覆盖用 Bash `cp`+`rm`，且先删占用文件再复制。
- opencv VideoWriter 用 `mp4v` fourcc + FFMPEG 后端写 H.264 MP4；中文输出路径可用。

## 领域知识库（references/domain_constants.md）
内置高尿酸/痛风可复用素材，换主题时按同结构替换为新领域的指南/阈值/药物。包含：
- 权威来源清单（指南/共识/食养指南/说明书）
- 关键数值阈值（诊断/启动/达标/停药/pH）
- 药物要点（别嘌醇/非布司他/苯溴马隆/多替诺雷/秋水仙碱，含基因筛查、黑框警告、最大剂量、国药准字）
- 升尿酸药 vs 一箭双雕药对照、果糖危害
- 合规红线（禁用词、个体化、免责声明）

## 五阶段工作流

### 阶段 1：素材挖掘 + 选题
- 从 `domain_constants.md` 的指南/说明书清单中挖「权威有新意」的切入点。
- 结合流行趋势 + 公众误区 + 门诊高频问题，生成 **5 个选题**，每个含「选题名称 + 选题理由（科普价值/针对性）」。
- 输出表格：序号 / 选题标题 / 选题理由。

### 阶段 2：选题表 + 五篇提纲（Word）
- 用 `references/docx_builder.py` 的样式辅助生成。
- 每篇提纲统一四段式：**A 公众号长文骨架 / B 门诊讲座要点卡 / C 短视频脚本要素 / D 建议配图**。
- 结构：封面信息块 → 使用说明 + 写作红线 notebox → 选题总表（斑马纹）→ 逐篇提纲 → 附录循证依据 + 统一免责声明。

### 阶段 3：科普文章（Word）
- 结构：**问题切入（痛点引言）+ 通俗解读（生活化比喻）+ 实操建议（要点卡/红线）+ 案例对比 + 结论**。
- 多用短句短段；术语给白话；关键数字保留并可回溯。
- 用 docx_builder 的 `notebox` 放「用药安全红线」，文末统一免责声明。
- 自检：禁用词 grep（根治/治愈/神药/百分百/保证有效）；数值可回溯;剂量一律「个体化决定」。

### 阶段 4：短视频脚本（Markdown）
- 用 `references/script_template.md` 模板填充：概述表 / 知识点拆解 / 分镜表 / AI 提示词 / 配音 / BGM 音效 / 互动 / 自检。
- 时长默认 60s，9:16，语速 4–4.5 字/秒（约 240–270 字）。
- 叙事：钩子(0–4s) → 痛点 → 原理比喻 → 要点卡×N → 安全红线 → 互动 CTA。

### 阶段 5：短视频渲染（Python 兜底）
- 用 `references/render_template.py` 骨架：1080×1920 / 30fps / 改 `DURATION` 与 `SCENES` 即换内容。
- 统一视觉：医疗深蓝底 + 白底圆角卡 + 橙红/蓝强调 + 顶部进度条 + 底部字幕条。
- 渲染后用 cv2 回读校验：总帧数 == DURATION×30 且可读。
- 该渲染为**无声画面版**（字幕已内嵌）；BGM/音效按脚本用剪映或 Remotion `<Audio>` 叠加。

## 视觉风格默认（可改 COLORS / docx 主题）
- 视频：9:16 1080×1920，30fps；深蓝 `#0E2A47`、橙红 `#E8541E`、蓝 `#2A6FDB`、绿 `#22A06E`。
- 文档：微软雅黑；标题深蓝、正文深灰、提醒灰底橙框；A4 页边距 2.2–2.3cm。

## 合规红线（科普内容，必须遵守）
- 禁用「根治/治愈/神药/百分百/保证有效/包好」等绝对化疗效词。
- 剂量/停药/换药一律落到「由医生/药师个体化决定」。
- 文末统一免责声明：不替代面诊，用药请遵医嘱。
- 关键数值须可回溯到指南/药品说明书。

## 复用与定制
- **换疾病主题**：改 `domain_constants.md`（指南/阈值/药物/红线）即可，工作流不变。
- **改文案/时长**：编辑 `render_template.py` 的 `SCENES` / `DURATION`。
- **改配色**：改 `render_template.py` 的 `COLORS` 或 docx_builder 的颜色常量。
- **严格用 Remotion**：仅当环境能正常访问 npm（或挂代理镜像）时再切回 React 技术栈。

## 常见问题
- **VideoWriter 打不开**：装 `opencv-python-headless`（自带 ffmpeg）；fourcc 用 `mp4v`。
- **中文乱码**：msyh.ttc 粗体用 `index=1`；Linux 用 NotoSansCJK-Bold.ttc。
- **渲染崩在清理步**：把 `os.remove`/`os.rename` 移出 Python，用 Bash `cp`+`rm`。
- **npm 装 Remotion 卡死**：直接走 Python 兜底，不要等。
- **docx 中文样式不生效**：用 `docx_builder.set_run` 同时设 `w:eastAsia` 字体。
