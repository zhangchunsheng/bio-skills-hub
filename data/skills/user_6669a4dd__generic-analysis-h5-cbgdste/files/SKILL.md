---
name: 通用分析H5报告
description: >-
  对单份述职/复盘/经营报告(.ppt/.pptx/.md/.zip/飞书云文档链接)做 McKinsey 风格的穿透式通用商业分析，
  快速模式只做整体分析(跳过逐页/逐章)，产出一个左原文右10维度分析的离线单文件 H5(图片base64内嵌，可直接分享)。
  当用户提到"通用分析/通用分析系统/快速模式/只要整体分析/generic模式/穿透式分析/报告分析H5/
  h5_export_generic/run_overall_only_pipeline"，或给出一份 PPT/云文档报告要一份可分享的分析 H5 时使用。
  用户只给飞书 wiki/docx 云文档链接时也能全自动跑通（cloud_doc_run.py），无需用户手动导出 zip。
  默认用 WorkBuddy 当前会话模型做分析（--no-ai 模式，不花外部 API 钱）；
  一份报告一个 H5；若要把一批报告汇总成给总经理看的驾驶舱，请改用 gm-cockpit 或 oms-cockpit。
version: 1.0.0
category: 办公效率
platforms:
  - WorkBuddy
license: MIT
author: 尘易顺
---

# 通用分析H5报告 (generic-analysis-h5)

对**单份**经营/述职/复盘报告做通用商业分析（非模板合规检查），输出一个**离线单文件 H5**：左侧原文（PPT 页图 / Markdown 正文），右侧 10 个维度的分析。

**快速模式**是本 skill 的默认且唯一模式：只跑**整体分析**，跳过逐页/逐章分析——一次多模态调用把「全部页面图片 + 文本」一起喂给 AI，既快（3-5 分钟）又能消除只传文本时的数据幻觉。

## 何时使用本 skill

- 用户给出**一份** `.ppt/.pptx/.md/.zip` 报告，想要一份能直接发出去的分析 H5。
- 用户给出**飞书云文档链接**（`/wiki/` 或 `/docx/`），想要分析 H5 —— 走 **cloud_doc_run.py 全自动**（见下）。
- 用户说「通用分析系统」「快速模式」「只要整体分析」「输出H5到根目录」。
- **不适用**：一批报告汇总成驾驶舱（用 `gm-cockpit` / `oms-cockpit`）；述职规范合规打分（把 `prompt_config.json` 的 `active_mode` 改成 `review`）。

## ★★ 强制前置：多模态模型检测（每次分析前必须先做）

**为什么是硬性要求**：本 skill 的分析证据等级是「图片里的表格/图表 > 文本」——PPT 页图、
文档内嵌图里的关键数字只有**多模态模型**才看得见（提示词原文：图片中的数据表格和图表是最准确的，
如果文本与图片不一致，以图片为准）。纯文本模型看不到图：轻则漏掉核心数据、重则根据上下文**瞎编数字**，
产出的 H5 "看起来完整、实则虚构"。所以**在调用 AI 分析之前，必须先确认所用模型支持图像输入**；
确认不了或确认不支持 → **立即停下，让用户切换到多模态模型，绝不硬跑**。

两条路径各自怎么检测：

### 路径A：WorkBuddy 会话模型（默认路径 / --no-ai）— 会话内 Read 自检

1. ①步备料完成后（`cloud_doc_run.py --no-ai` 输出分析ID），**先用 Read 工具读一张
   `backend/uploads/<id>/<id>/图片和附件/` 里的图**（读第一张即可）。
2. 能正常描述出图片内容（颜色/布局/表格文字）→ 当前会话模型是多模态，继续做 10 维度分析。
3. Read 报错、提示"无法读取图像/不支持图像输入"、或只能看到文件名看不到画面 → **立即停下**，
   **不要继续分析**，用 AskUserQuestion 让用户选择/切换到多模态模型，选项示例：
   - Claude Sonnet 4 / GPT-4o / Qwen2.5-VL / 其他（按 WorkBuddy 当前实际可选的视觉模型给出）
   用户切换后，**重读那张图确认能看图**，再继续分析。
4. 整份报告**没有任何图片**（纯文字 md）→ 会话模型多模态非必需，跳过自检直接分析，
   但在分析里注明"未检测到图片，结论仅基于文本"。

### 路径B：外部模型（backend/.env 的 DEFAULT_MODEL / 一条命令全自动）— 脚本自动检测

- `generic_run.py` 在调 AI 前**自动做多模态前置检测**（模型名启发式 → 必要时发一张 64x64 测试图
  探测，几乎不花钱）；不通过会**直接退出、不调 AI**，并打印三种处理办法。
- 想单独检测：`python <skill目录>/scripts/check_multimodal.py`（`--model gpt-4o` 可指定模型，
  `--json` 机器可读，退出码 0=可用 1=不可用 2=配置缺失）。
- 检测不通过时按提示任选其一：
  1. **本次覆盖**：`python generic_run.py "<报告>" --model "<多模态模型名>"`
  2. **永久生效**：修改 `backend/.env` 的 `DEFAULT_MODEL` 为多模态模型
  3. 确知支持但检测误报：`--skip-multimodal-check` 强制继续（不推荐）
- `--upload-only` / `--h5-only` 不调 AI、不做检测；`--upload-only` 会打印会话模型自检提醒。

## ★ 默认路径：用 WorkBuddy 会话模型分析（不花外部 API 钱）

**这是默认执行方式**。用户没有特别指定时，一律走这条。原理：1-4 步（导出/补表/提图/打包）
不涉及 AI，只有第 5 步分析要调模型——把第 5 步换成「当前会话模型直接分析」，
即可完全绕开 `backend/.env` 里的外部 key，费用走 WorkBuddy 自身。

```bash
# ① 准备数据（导出→补表→提图→打包→建记录），不调用任何外部 AI
python <skill目录>/scripts/cloud_doc_run.py "<飞书链接>" --no-ai
#    输出末尾会打印 分析ID，例如 [✓] 分析记录 id=101

# ② 先做多模态自检（Read 一张 图片和附件/ 的图，能描述内容→继续；不能→停下让用户切换多模态模型，见上文）
#    然后在会话内读取素材并亲自完成 10 维度分析
#    正文：backend/uploads/<id>/<id>/*.md      （Read 工具直接读，含全部数据表）
#    图片：backend/uploads/<id>/<id>/图片和附件/*.png  （多模态模型可直接 Read 看图）
#    schema：backend_shared/app/services/prompts/generic_overall_analysis_prompt.txt
#    把分析结果写成 analysis.json（10 个顶层 key，见下）

# ③ 写库（--model 必带：H5 头部要显示真实分析模型）
python <skill目录>/scripts/write_session_analysis.py --id <id> --json analysis.json \
       --model "WorkBuddy 会话模型"

# ④ 出 H5（纯渲染，不调 AI）
cd <backend目录> && python generic_run.py --id <id> --h5-only --out "<输出名>.html"
```

**analysis.json 的 10 个顶层 key（缺一个 H5 就空一块，写库脚本会拦截）**：
`executive_summary` · `data_quality_check` · `critical_business_issues` · `root_cause_analysis` ·
`logic_chain_review` · `strategy_effectiveness` · `replicable_highlights` · `recommendations` ·
`information_gaps` · `final_assessment`

助手做分析时的要求（与 `generic_overall_analysis_prompt.txt` 一致）：
- **必须引用具体数字和数据表编号**作为证据，不能泛泛而谈
- 穿透表象找结构性矛盾（如「增收不增利」），敢指出报告自身的逻辑矛盾与归因回避
- 多模态模型务必把 `图片和附件/` 里的图逐张 Read 看过再下结论；纯文本模型则依赖 md 里的 alt 描述
- 嵌套结构严格照 schema，**不要自创字段名**（实测踩过：`critical_business_issues` 条目必须是
  `issue_id/issue_title/issue_description/evidence/nature/root_cause/impact/urgency` 八字段，
  写成 `issue/severity/business_impact` 会渲染空白）

**这条路径踩过的三个坑（已在脚本里修掉，换电脑复制新版即可）：**
1. **第 4 个维度叫 `root_cause_synthesis` 不是 `root_cause_analysis`** —— 写错 H5 少一块。
   写库脚本已内置 10 个 key 校验，缺失会直接报错拦截。
2. **`--upload-only` 必须顺带跑 `run_parse_only`** —— 只建记录不解析会导致
   `outline/raw_texts/total_pages` 为空，**H5 左侧原文全空、图片 0 张、体积只有 0.05MB**
   （正常含图应是 MB 级）。`generic_run.py` 已修复为建记录后自动解析。
3. **解析会把 status 改回 `parsed`** —— 若手动补跑过解析，出 H5 前需把 status 改回 `completed`
  （写库脚本会自动置为 completed，正常顺序 `--no-ai` → 写库 → `--h5-only` 不会遇到）。

验收标准：H5 体积 MB 级、`data:image` 数量 = 图片数、`<table>` 数量 > 0、10 个维度标题都在。

> 💡 会话模型 vs 外部模型：会话模型（走 WorkBuddy 计费）质量取决于当前所选模型，
> 且分析写在会话里可随时追问/修订；外部模型（`backend/.env` 的 qwen3.7-plus）是一条命令全自动、
> 但要自备 key。**默认走会话模型**，用户明确要"全自动一条命令"时才走下面的外部模型路径。

## 云文档链接 → 全自动分析（走 backend/.env 的外部模型，需自备 key）

```bash
cd <报告分析系统项目根目录>
python <skill目录>/scripts/cloud_doc_run.py "<飞书wiki/docx链接>" [--out "输出名.html"]
```

内部 5 步全自动（已验证跑通，广州战区文档 ID=99 全绿）：

```
1  drive +export --file-extension markdown   → 官方正文 md（含 <sheet> 占位 + 图片外链）
2  sheets +csv-get 逐个展开内嵌电子表格     → markdown 表格插回原文（18 个表数据不丢）
3  drive +export --file-extension pdf        → 导出 PDF，PyMuPDF 提取文档原图
   （按图片引用前的最近标题定位页面，排除页宽渲染图/头像小图）
4  图片写入 图片和附件/，md 引用改本地路径   → 打包 ZIP（md + 图片和附件/ 同级）
5  调 backend/generic_run.py 跑通用分析      → 输出 H5
```

**为什么不能只用 `drive +export` 的 markdown 直接分析（踩过的坑）：**
- 飞书导出 markdown **不携带内嵌电子表格**：原生前端导出直接跳过（数据全丢），OpenAPI 导出留空 `<sheet>` 占位标签。必须用 `sheets +csv-get` 按 token 逐个补回，否则 AI 拿不到收入/利润等核心数字。
- 图片：API 导出的 md 里图片是 `internal-api-drive-stream` authcode 外链，`docs +media-download` / 直连下载均被权限拦截（1063001/404/连接重置）。**可靠来源 = 导出 PDF 提取**（PDF 是标准导出，图片必然渲染进去）。
- 判断「内嵌表 vs 原生表格」：内嵌 sheet 有独立 spreadsheet token（如 `P7QxsLQjAhBwontEqiMc7Vfen6g`），原生表格没有。原生表格导出 markdown 会保留，内嵌表不会。

Windows 环境注意：`cloud_doc_run.py` 内部直接调用 node 入口，不要依赖 `lark-cli` 命令本身
（Python subprocess 无法直接执行 sh/cmd 包装）。路径已做跨机器自动探测，换电脑无需改代码，
也可用环境变量覆盖：`WB_NODE` / `WB_LARK_RUN_JS` / `WB_PYTHON`（需装有 fastapi 等依赖的
python3.12）/ `WB_BACKEND`（报告分析系统 backend 目录），或 `--backend` 参数。

**换电脑部署清单（让 skill 在别人电脑跑通）**：
1. 复制 skill 目录（无密钥，安全）到对方 `~/.workbuddy/skills/`
2. 对方电脑装好「报告分析系统 backend」：Python 3.12 + `pip install -r requirements.txt`，
   `generic_run.py` 落位 `backend/` 根目录，`backend/.env` 填**对方自己的** BASE_URL/API_KEY/DEFAULT_MODEL（**必须多模态模型**；
   generic_run 会在分析前自动检测，非多模态直接拦截停下），
   `app/services/prompt_config.json` 的 `active_mode=generic`（数据库自动建）
3. 对方电脑的 WorkBuddy 需已登录飞书 connector（lark-cli 可用，对目标文档有导出权限）
4. 路径探测失败时设置 4 个 WB_* 环境变量；跑 PPT 才需要 LibreOffice

## 标准执行流程（一条命令）

```bash
cd backend
python generic_run.py "<报告文件完整路径>"
```

脚本按序完成 4 步，全程无需启动 uvicorn 服务：

```
0 前置       自动检测模型是否多模态(模型名→必要时测试图探测)；非多模态立即停下提示换模型
1 建分析记录 + 落盘 uploads/{id}/     (等价于 POST /api/analyses/upload)
2 run_overall_only_pipeline(id)       解析 → 仅整体分析(多模态传图+文本)
3 体检                                 拦截空JSON / raw-error 截断
4 generate_generic_h5 → 复制到项目根目录/<原名>-通用分析.html
```

常用变体：

```bash
python generic_run.py "报告.zip" --out "华东大区-通用分析.html"   # 指定输出名
python generic_run.py "报告.zip" --model "gpt-4o"                # 指定多模态模型(覆盖 .env)
python generic_run.py --check-multimodal                         # 只检测当前模型是否多模态
python generic_run.py --id 92 --h5-only                          # 复用已跑结果，只重出H5(不花AI)
python generic_run.py --id 92 --check                            # 只体检
python generic_run.py --id 92 --title "正确标题.pptx" --h5-only    # 修标题后重出
```

> ⚠️ **MD 必须传 ZIP 包**（MD + `图片和附件/` 同级），不要单独传 `.md`，否则 H5 无图。

## 输出的 10 个维度

📋 执行摘要 · 🔍 数据质量检查 · ⚠️ 核心经营问题 · 🎯 根因综合分析 · 🔗 逻辑链审查 · 📈 策略有效性评估 · ✨ 可复制亮点 · 💡 改进建议 · ❓ 信息缺口 · ✅ 最终评估

H5 交互：PPT 页图 / MD 图片点击全屏放大（ESC 关闭）；MD 表格点击放大。

## 关键文件

| 文件 | 作用 |
|---|---|
| `scripts/check_multimodal.py` | ★ 多模态模型检测脚本（模型名启发式+64x64测试图运行时探测；退出码 0=可用 1=不可用 2=配置缺失） |
| `scripts/generic_run.py` | ★ 一条命令驱动（**内置多模态前置检测**→建记录→分析→体检→出H5→复制），落位 `backend/generic_run.py` |
| `scripts/cloud_doc_run.py` | ★ 云文档链接全自动管线（导出md→补内嵌表→PDF提图→打包→调generic_run）；`--no-ai` 只备料不调外部AI |
| `scripts/write_session_analysis.py` | ★ 把会话模型产出的 10 维度 JSON 写入分析库（配合 `--no-ai` + `--h5-only`） |
| `backend_shared/app/services/task_runner.py` | `run_overall_only_pipeline` — 快速模式管线 |
| `backend_shared/app/services/ai_service.py` | `analyze_overall_with_images`(PPT) / `analyze_document`(MD)，均 `max_tokens=16384` |
| `backend_shared/app/services/h5_export_generic.py` | ★ 唯一正确的 H5 生成器 |
| `backend_shared/app/services/prompts/generic_overall_analysis_prompt.txt` | 整体分析提示词（10 维度 schema） |
| `backend_shared/app/services/prompt_config.json` | `active_mode` 必须是 `generic` |

## 铁律与已内置的坑

- **生成器只用 `h5_export_generic.py`**。`h5_export.py`（旧版述职规范格式）和 `h5_export_adapter.py`（适配器）格式都不对。
- **`active_mode` 必须为 `generic`**，否则加载的是述职规范提示词，输出 schema 对不上，H5 会整片空白。
- **体检拦截截断**：AI 返回非法 JSON 时 `ai_service` 会存成 `{"raw":..., "error":...}`——长度看着上万，但 H5 全空。脚本在导出前拦下并提示重跑（真实踩过：id=93 存了 16823 字符却 0/10 维度）。
- **ZIP 多包一层文件夹 → 图片全丢**：解析器和 H5 都只在 `uploads/{id}/{id}/{图片和附件|images|assets|media}` 这一层找图。脚本在分析前预解压并把图片目录**自动上移一层**。
- **标题乱码**：H5 标题取自 `ppt_path` 的文件名；旧流程用 `curl -F` 上传会把中文名压成 `26ÄêCBG...`。脚本改为**直接落盘复制**，从根上避免；历史记录可用 `--title` 修。
- **纯文本模型硬跑 → 数据幻觉**：图片里的表格/图表是最高优先级证据，纯文本模型看不到图就会编数字。`generic_run.py` 已在调 AI 前内置多模态检测并拦截（出路：`--model` 覆盖 / 改 .env / `--skip-multimodal-check`）；会话路径靠助手 Read 自检，不通过先让用户切模型。
- **PPT 需要 LibreOffice**（`soffice` 转页图）；纯 MD/ZIP 不需要。

## 运行前置

见同目录 `依赖与运行说明.md`；接入 Codex / workbuddy 等非 Claude Code 工具见 `接入其他工具指南.md`；完整逐步手册见 `reference/操作文档-通用分析H5.md`。
