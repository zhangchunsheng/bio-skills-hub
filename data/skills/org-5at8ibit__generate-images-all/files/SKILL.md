---
name: 全能绘图大师
description: 全能 AI 绘图技能——**无需写提示词，说人话就能出图**。把一句话想法、一篇文章、一段产品介绍或参考图+要求直接交给它，自动完成意图理解与提示词工程(JSON 结构化/身份锁/相机参数/负面词)，经网关生成高清图片，统一文生图(t2i)/图生图(i2i)。三模型任选——gpt-image-2(默认，3算力/张，多元素/文字/信息图/电商主图最强)、nano-banana-pro(7算力/张，人像/产品保真，**支持 2K/4K**)、nano-banana-2(3算力/张，最快最省，批量)。典型用例：①给一篇文章自动配封面/题图(贴文章或链接，自动提炼主视觉+标题排版)；②「画张竖版封面，标题是XXX」自动选比例套版式；③给产品图走 i2i 出电商主图；④「我想要一张XX感觉的图」模糊意图自动扩写成结构化提示词；⑤「参考这张图的画风画XXX」i2i 风格迁移。首次使用需 API Key：访问 https://quakowork.com/console/api-key?source=workbuddy 注册并订阅/充值点数后获取，把 key 贴回对话即可。结果落盘 generate_images 目录（Windows `D:\generate_images`；macOS/Linux `~/generate_images`，脚本自动适配）。奎可智能体出品：https://quakowork.com/。触发词：全能绘图大师、绘图大师workbuddy版、workbuddy出图、workbuddy绘图、AI绘图、配图、生成封面、文生图、图生图。
version: 1.0.0
---

# 全能绘图大师 workbuddy 版（无需提示词 · 经网关出图）

**经网关**（`http://cwapi.xiemoai.com/v1/gateway/proxy`）调用服务器，统一 t2i/i2i。提交走 `/model/t2i-pro` 等 6 条路由，轮询走 `/app/ai/query`，本地图上传走 `/app/upload`。

## 首次使用 / 密钥（每次启动必查）

API Key 保存在**本技能根目录的 `key.txt`**（单行纯文本，按点数计费）。

**启动时（本技能被调用）第一步**：先检查 `key.txt`——

1. **有 key**（文件里有一个非空行）→ 直接继续出图任务；**不要在对话中回显完整 key**。
2. **无 key / 文件为空或缺失** → 停止出图，向用户输出指引：
   > 本技能需要 API Key（按点数计费）。请访问 **https://quakowork.com/console/api-key?source=workbuddy** 注册账号并订阅/充值点数，创建 API Key 后把它粘贴到对话里，我帮你保存后马上开始出图。
3. 用户把 key 贴回来后：去掉首尾引号/空白，`Write` 单行到本技能根 `key.txt`，然后跑 `python scripts/rh_image_api.py check` 验证（输出只显示 key 前 8 位），通过后继续原出图任务。
4. **key 无效 / 点数不足**（网关返回鉴权类错误）→ 引导用户回到同一链接检查 key 或充值，更新 `key.txt` 后重试。

## 无需提示词 · 自动出图（核心能力）

用户**不需要会写提示词**。以下输入都能直接出图：

| 用户给什么 | 技能做什么 |
|---|---|
| 一句话意图（「我想要一张XX感觉的图」） | 自动扩写为结构化提示词（按模型路由 JSON 结构化 / 身份锁）再出图 |
| 一篇文章 / 一段文案（正文或链接） | 读懂内容 → 提炼主视觉与要出现的文字 → 配图 / 封面 |
| 标题 + 用途（「画张竖版封面，标题是XXX」） | 自动选比例与版式，标题文字逐字锁进 `labels` |
| 参考图 + 要求（「参考这张画风」「把产品放进去」） | i2i，画风 / 产品保真 |
| 已是精修结构化提示词 | 直接出图，不再改写 |

出图前向用户**一句话简述**「我准备怎么画」（构图 / 文字 / 选了哪个模型），然后调用脚本。

**用途 → 模型速查**（用户没点名模型时自动选）：
- 文章配图 / 封面 / 信息图 / 电商主图（有文字、多元素）→ `gpt-image-2`（默认）
- 人像写真 / 换装 / 换背景 / 产品保真 → `nano-banana-pro`
- 最高清 4K → `nano-banana-pro` + `--resolution 4K`
- 批量 / 要快 / 要省 → `nano-banana-2`

## 默认值

| 项 | 默认 |
|---|---|
| 模型 `--model` | **gpt-image-2** |
| 分辨率 `--resolution` | **2K**（香蕉 PRO 可 `4K`；V2/GPT-image-2 固定 2K，传 4K 会报错） |
| 比例 `--aspect` | **1:1**（按用途自动选：竖版封面 3:4、横版题图 16:9 等） |

## 三模型（--model 可切换）

| `--model` | 中文名 | t2i 路由 | i2i 路由 | 分辨率 | 算力/张 | 实测耗时(2K) | 适用 |
|---|---|---|---|---|---|---|---|
| `nano-banana-pro` | 香蕉 PRO | `/model/t2i-pro` | `/model/i2i-pro` | **2K/4K** | **7** | ~30s（4K~55s） | 人像/产品保真、最高清 4K |
| `nano-banana-2` | 香蕉 V2 | `/model/t2i-v2` | `/model/i2i-v2` | 固定 2K | **3** | ~25s | 最便宜最快、批量 |
| `gpt-image-2`（**默认**） | GPT-image-2 | `/model/t2i-g2` | `/model/i2i-g2` | 固定 2K | **3** | **~50-165s（波动大）** | 多元素/文字/信息图/电商主图（JSON 结构化） |

> 三模型 t2i 与 i2i 同算力；轮询统一走 `/app/ai/query`。
> gpt-image-2 额外必填 `quality`（脚本内部固定 `high`）；**三模型均传 `aspectRatio`**。

## 提示词优化（出图前，agent 层自动完成）

用户的输入若是**草稿 / 口语化 / 只有模糊风格词 / 多元素构图 / i2i 带参考图**，**先按 [`references/prompt-optimization.md`](references/prompt-optimization.md) 优化**，再把优化后的提示词传给 `rh_image_api.py`。已是精修结构化提示词则直接出图。

**按 `--model` 路由**：
- `gpt-image-2`（默认）→ 多元素/有布局/有文字/参考表/信息图/电商主图 → **JSON 结构化**（`count`+`labels[]`）+ `REFERENCE_0` 锚定
- `nano-banana-pro` / `nano-banana-2` → 人像写真/换装/换背景/产品保真 → **身份锁**（`identity_lock_strength` / `modification_permission: NONE`）+ `Image 1` + raw 美学 + 详尽负面词

优化后向用户简述改了什么（一行），再调用命令。决策树、骨架与示例见参考文档。

## 个人风格库（保存 / 复用）

`~/.claude/styles/` 是用户个人的风格库（在技能目录外，技能更新不会覆盖）。完整格式规范见 [`~/.claude/styles/_风格库说明.md`](../../styles/_风格库说明.md)。

- **启动时**：先 `Glob ~/.claude/styles/*.md`（**跳过 `_*` 前缀**），若有风格则向用户列出（名 + description + model/aspect），问「套用某个已有风格 / 新建不套风格」；没有则跳过。
- **套用已有风格**：`Read` 选中文件 → 问占位符的值 → 「固定调性串」整段照搬 + 填好的「提示词骨架」拼成最终提示词 → 按 frontmatter 的 `model` / `aspect` 出图。
- **出图后（用户对画风满意时）**：主动问「要把这次风格存成模板吗？」→ 随图变化的部分抽成 `<...>` 占位符、固定不变的部分锁为调性串 → 按规范 `Write` 新文件到 `~/.claude/styles/<中性名>.md`。
- **列出 / 查看 / 删除风格**：直接 `Glob` / `Read` / `rm`。

## 密钥（脚本层）

`scripts/rh_image_api.py` 与 `scripts/fetch_task.py` 从**本技能根目录的 `key.txt`** 读 key（首个非空行，自动去引号/空白）。无 key 时脚本报错信息自带注册链接。网关双头鉴权（`jh-api-key` 头 + 占位 Authorization）不变。

## 命令（入口 `scripts/rh_image_api.py`）

```bash
# 零成本自检：验证 key + 列路由表
python rh_image_api.py check

# 打印路由表 + 探测每条路由必填字段（排错）
python rh_image_api.py discover

# 文生图（默认 gpt-image-2/2K）
python rh_image_api.py t2i "提示词" [--model gpt-image-2] [--resolution 2K] [--aspect 1:1] [-n 1]

# 图生图 / 编辑（参考图 | 分隔，最多 10；本地图自动上传拿 download_url，URL 透传）
python rh_image_api.py i2i "提示词" --images "<图片路径1>|<图片路径2>" [--model nano-banana-pro] [--resolution 2K] [--aspect 1:1]

# 自动判断（给图走 i2i，否则 t2i）
python rh_image_api.py auto "提示词" [--images "..."] [--model ...]
```

参考图支持 jpg/png/webp/bmp，单张 ≤ 10 MB（服务器限制）；本地图脚本自动经网关 `/app/upload` 上传拿 `download_url`，URL 透传。

## 运行模式：前台 / 后台 + 轮询 + 中止取回

`rh_image_api.py` 一次调用 = 上传(i2i) + 提交 + 轮询 + 下载。**慢图必须后台跑**，否则会被前台 Bash 工具 2 分钟超时杀掉。

- **快图（预计 <90s）**：香蕉 2K（~25-35s）、香蕉 4K（~55s）→ 可前台。
- **慢图（预计 ≥90s）**：**gpt-image-2（实测 50-165s 波动）**、批量 `-n>1` → **必须后台**（Bash `run_in_background: true`）+ `TaskOutput` 主动轮询（`block=true`，30-60s 一轮）。脚本持续报进度：`[SUBMITTED] task_id=…`、`[poll Xs] 状态/心搏`，**不会静默**。
- **中止 / 报错必取回（铁律）**：任何运行被中断 → `tail <输出目录>/_tasklog_pro.jsonl`（Windows `D:\generate_images\_tasklog_pro.jsonl`；macOS/Linux `~/generate_images/_tasklog_pro.jsonl`）取最近 `task_id` → `python scripts/fetch_task.py <task_id>` 把服务端已生成的图取回。

## 铁律

- **绝不 Read 生成结果图**：只轮询 + 下载 + 保存；验证只看落盘成功数与 PIL 量尺寸（`from PIL import Image; Image.open(f).size`）。文字/画风核对交用户。
- **密钥安全**：完整 key **绝不回显到对话**、不写进日志；日志只打前 8 位 + 长度。
- **优化只在 agent 层**：提示词优化由调用者（Claude）读 `references/prompt-optimization.md` 后完成；`rh_image_api.py` 永远原样透传，**不引入任何 LLM 调用**。
- **风格库在技能目录外**：个人风格一律存 `~/.claude/styles/`，**绝不**写入本技能目录（技能更新会整体覆盖）。`key.txt` 是唯一放技能根的用户数据（丢了重新贴一次 key 即可）。

## 常见坑

- **gpt-image-2 比 banana 慢 5-6 倍**（~165s vs ~30s）：慢图走后台 + TaskOutput，别前台硬等。
- **V2 / GPT-image-2 传 `--resolution 4K` 会报错**：脚本按模型校验，仅香蕉 PRO 支持 4K。
- **gpt-image-2 耗时波动大**（实测 50-165s）：慢图走后台 + TaskOutput，别前台硬等。`--aspect` 三模型均生效（脚本已传 `aspectRatio`）。
- **鉴权失败 / 点数不足**：引导用户到 https://quakowork.com/console/api-key?source=workbuddy 检查 key 或订阅/充值，更新 `key.txt` 后重试。
- 实际算力消耗以控制台为准（表中所列 7/3/3 为技能报告口径）。

---

© **奎可智能体出品** · https://quakowork.com/
