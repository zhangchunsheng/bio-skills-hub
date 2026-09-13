---
name: juhuang-tuijian
description: 剧荒推荐 · 通过观影 DNA 分析把用户匹配到 12 种观影人格之一，从约 2482 部动画库（TV 番 + 动画电影，已做中文名治理与争议作品屏蔽）中生成「五档推荐」片单（作品名+标签+简介+推荐理由四要素），并可渲染含统一卡通形象的可分享图文（人格卡 + 片单长图）。当用户说"测测我的观影人格""剧荒了推荐点动漫""根据我的口味出片单/做分享图""番剧推荐""补番清单""追番推荐""最近看什么好""动漫推荐""anime recommend"时使用。
agent_created: true
argument-hint: "[--persona <人格名>] [--out-dir <输出目录>] [--skip-demo]"
allowed-tools: "Read, Bash(python:*), Write"
---

# 剧荒推荐（Anime Recommender）

把"剧荒"变成一次好玩的人格测试 + 精准动漫推荐。核心交付物是**个性化动漫片单**（纯文字四要素），并可渲染**带统一卡通形象的可分享图**。逻辑由本 skill 的 pipeline 在对话中驱动，Python 脚本（`scripts/`）负责确定性检索与图片渲染。

## 产品边界（铁律）

- **只推动画**（TV 番 + 动画电影），绝不推荐任何真人电视剧 / 电影。作品池（`scripts/anime_pool_merged.py`，约 2482 部）已限定 `direction ∈ {动漫, 动画电影}`，`pool_query(..., domain="动漫")` 强制该护栏。
- **争议作品屏蔽（零容忍）**：`scripts/curation.py` 黑名单拦截国内有明确争议/已下架的作品（当前含「我的英雄学院」全系列/全语言标题，**含剧场版与衍生作**）。三重护栏，缺一不可：
  - ① `pool_query` 候选收集阶段调用 `is_blocked()` 拦截（主路径，覆盖默认片单 / 反馈重推 / 补位）。
  - ② `build_share.build_list()` 与 `regenerate()` 渲染前二次过滤（兜底，防上游绕过），命中时打印 `[curation] 已拦截争议作品 N 部：…`。
  - ③ **LLM 侧铁律（最关键）**：片单作品必须且只能来自 `pool_query` 的返回值——**禁止**执行引擎用自己的知识补充、替换或改名任何作品。热门争议作（如「我的英雄学院 THE MOVIE 英雄崛起」）极易被 LLM「凭印象」补进名单，而这类作品从未经过黑名单；渲染层虽有兜底，但**文字片单没有这道保护**。
  - 扩展：只需在 `DENY_TOKENS` 追加一个专属 token（子串匹配，自动覆盖该作品的全语言标题与衍生作）。
- 输出**纯文字片单**（作品名 + `cat` 标签 + `synopsis` 简介 + `reason` 推荐理由），**不含作品封面图**。
- 12 个人格各有**固定的卡通 mascot**（`assets/stickers/` 静态 PNG，或 `scripts/stickers_data.py` 的 base64 内嵌副本——后者用于禁止上传二进制的分发平台如 SkillHub；二者渲染效果一致，跨用户、跨运行一致）。

## Pipeline（执行步骤）

### Workflow checklist（务必按顺序勾选，⚠️ 为必做）

- [ ] Step 1：收集观影 DNA，产出六维 `user_vec`
- [ ] Step 2：argmax 匹配 12 人格，向用户展示人格档案
- [ ] Step 3：⚠️ REQUIRED 调 `pool_query` 且**务必传入 `user_vec`**，产出五档齐全的片单
- [ ] Step 4：反馈循环（optional，由用户对话触发）
- [ ] Step 5：渲染分享图（optional，渲染前若同名图已存在需 ⚠️ REQUIRED 确认）

### Step 1 — 收集观影 DNA（对话态）
在对话中引导用户说出：最喜欢的 8–12 部动漫 / 不感冒的类型 / 看过的作品。参考 `references/观影DNA分析框架.md` 的六维模型（沉浸/情感/智识/暗度/群像/冒险）为这些作品打 6 维分（0–100），取均值得到用户的 **`user_vec`**（六维 DNA 向量）。
- 六维打分可让用户自评，或由 LLM 依据作品特征直接判定（维度定义见框架 §4.1）。
- 也可直接让用户描述偏好，由 LLM 归纳成 `user_vec`。

### Step 2 — 匹配观影人格
用 `user_vec` 在 12 个人格（`references/persona-spec.md` 的目标向量）上做 `argmax` 匹配；必要时按余弦相邻补位。向用户展示其人格名 + tagline + 六维 DNA 档案（讲清楚"为什么是你"）。
- 多元观影者兜底规则见 `persona-spec.md` §二（§4.4）。

### Step 3 — 生成五档片单
调用 `scripts/works_pool.py` 的 `pool_query`。⚠️ REQUIRED **务必传入 `user_vec`**：同一人格、不同 DNA 画像的用户会因此拿到不同作品，实现个性化；不传则退化为按人格标签取固定列表。
- **同人格 ≠ 同片单**：`pool_query` 会结合 `user_vec`（六维 DNA 相似度）和 `region_priority`（用户作品名单推断的地区偏好）在同一人格池内重排。因此两个用户即使都被判定为「热忱群像派」，只要他们给出的片单 DNA 或地区偏好不同，最终 20 部推荐就会不同。
- **地区优先级由用户作品名单推断，绝不写死日本**：`region_priority = infer_region_priority(<用户提到的作品名列表>)`——在作品池按名字反查区域，按频次降序推导。这样喜欢国漫/欧美番的用户会优先拿到对应地区推荐。
  - **部分信号也要用（重要）**：命中数低于 `min_signal`（默认 3）时**不再整体回退**到冷启动顺序，而是把**已命中的 region 提到最前**，其余仍按冷启动顺序 `[日本, 中国, 欧美]` 补齐。
  - 旧行为（已修正）：命中不足就整体回退成「日本第一」，导致只报 2–3 部国漫却被推 20 部日漫。这条是推荐内容与用户口味南辕北辙的头号原因，改动时务必保留新行为。

可运行配方（让 LLM 在对话中执行，路径按需替换）：

**⚠️ 主路径：直接跑脚本文件（推荐，仅标准库，无需 Pillow / opencc，且不存在 sys.path 问题）**
把 `<SKILL>/scripts/works_pool.py` 当作命令行入口即可，模型解析其 JSON / 文本输出：

```bash
# 个性化片单（传入用户六维 DNA，实现"同人格不同人看到不同作品"）
python <SKILL>/scripts/works_pool.py --persona "热忱群像派" \
       --region 中国 --user-vec "60,70,55,40,75,55" --json

# 未算 DNA 时：退化为按人格标签的固定列表（仍五档齐全）
python <SKILL>/scripts/works_pool.py --persona "热忱群像派" --region 中国

# 排查：打印作品池统计 / 未知人格会给出清晰报错而非静默空列表
python <SKILL>/scripts/works_pool.py --stats
python <SKILL>/scripts/works_pool.py --persona "热忱群像派 "   # 引号/空格错 → 明确报错
```

> 依赖边界（重要，避免"名单为空"）：**文字片单 = `works_pool.py` 纯标准库，任何 Python 都能跑**，
> 不需要 Pillow，opencc 缺失也仅影响极少数日文异体字标题归一化（已 try/except 兜底、不崩溃）。
> 只有 **Step 5 的分享图渲染**（`build_share.py`）需要 `Pillow`。
> 因此即使用户机器没装 Pillow，片单也照常出；渲染图才需要装 `pip install -r requirements.txt`。

**备选（已算好 user_vec 想直接调函数时）**：先 `import` 再调 `pool_query`——注意必须先把 `scripts` 目录加入 `sys.path`，否则 `from works_pool import` 会因找不到模块而失败（历史上"名单为空"多半源于此）：

```python
import sys
sys.path.insert(0, "<SKILL>/scripts")
from works_pool import PERSONA_VECS, pool_query, infer_region_priority

user_vec = (60, 70, 55, 40, 75, 55)
user_works = ["排球少年!!", "灌篮高手", "蜂蜜与四叶草"]
region_priority = infer_region_priority(user_works)
recs = pool_query("热忱群像派", user_vec=user_vec, domain="动漫", n=20, region_priority=region_priority)
```

⚠️ **名单来源铁律（最高优先级，先于一切其它要求）**：片单里的每一部作品**必须且只能**来自 `pool_query` 的返回值。**严禁**执行引擎：
- 用自己的动漫知识往名单里**补充**作品（哪怕觉得"这部很合适"）；
- **替换** `pool_query` 给出的作品，或给它**改名**；
- 手写 `works=[{...}, {...}]` 直接传给 `build_list()` / `regenerate()`；
- **把某部作品的 `aliases` 当成独立作品输出**——`aliases` 是同一部作品的其它语言 / 季数标题（例如「排球少年!!」的 aliases 含「ハイキュー!! 乌野高校 VS 白鸟沢学园高校」），**只用于反查，不是可推荐条目**。片单里只输出 `name` 字段。

这不是风格建议，而是合规与体验要求。两个真实事故都源于破坏此铁律：
- 「我的英雄学院 THE MOVIE 英雄崛起」被凭印象补入 → 绕过 `curation.is_blocked()` 争议作品黑名单；
- 「排球少年!! 第二季」与「排球少年!! 乌野高中 VS 白鸟泽学园高中」同时出现 → 绕过同系列限流，且后者根本不是作品库里的 `name`（它是别名，也是模型的知识），纯属凭空补入。

⚠️ **同系列只留 1 部**：`pool_query` 内部已按 `series_key` 限流——同一 IP 的不同季 / 剧场版 / 带副标题的续作视为同一系列，默认每系列只留 1 部。执行引擎**不得**手动把同系列的第二部加回名单。渲染层 `build_list()` / `regenerate()` 也会再兜底去重一次（命中时打印 `[series] 已剔除同系列重复 N 部：…`）。

若发现 `pool_query` 结果不足 20 部或五档不齐，正确处理是**调 `pool_query` 参数重跑**（换 region_priority / 放宽 direction），**不是自己补作品**。

输出含 `synopsis` 与 `reason` 字段，按 tier 分五档：你的本命(like) / 上头预警(expand) / 开个盲盒(try) / 宝藏冷门(niche) / 意外惊喜(neighbor)。

**每档必须列出全部作品，禁止省略**。若使用表格呈现，「代表作」列必须写出该档所有作品的 `name`（如 7 部就列 7 个名字），**不得**使用 `...`、`…`、`等`、`等 N 部` 或任何截断形式。这是真实片单，不是摘要；脚本已返回完整 20 部，执行引擎必须全部呈现，不得替用户「折叠」。

**五档结构是硬要求**，片单必须五档齐全（配额 `like6 / expand5 / try4 / niche3 / neighbor2 = 20`）。`pool_query` 内部三条关键规则保证了这一点，改动引擎时不要破坏：

- **跨区降级只作用于 `try`**：同人格但非偏好地区的作品，只有 `try` 会降级进 `neighbor`（充当「跨区惊喜」）；`like` / `expand` / `niche` **保留原 tier**，让偏好地区的标杆作仍能进入主档。旧行为是「跨区一律降级」，会把整个非偏好地区作品池塞进 `neighbor`，主档则被其他地区占满。
  - 注意：`niche` 曾与 `try` 一并降级，结果偏好地区非日本时冷门档候选被抽干到 0、整档消失（48 组场景里 5 组）。现已改回不降级——`niche` 仅 3 部且属「挖宝」性质，保留它不影响主档贴合偏好地区。
- **五档配额保底**：先按每档配额取候选（`quota` 合计正好 20），保证五档都有席位；因近名/同系列去重导致不足 20 部时，再从各档 `OVERFLOW` 余量按档优先补齐。旧行为是把各档 `quota×OVERFLOW` 串成一条长候选，`finalize_reco` 一旦在前两档凑满 20 就 `break`，结果片单永远只有「你的本命 + 上头预警」两档。
- **档位保底（下限 1 部）**：候选按**轮转交织**排列（先各档第 1 部、再各档第 2 部…），使去重时优先保住每档第一个席位；末尾再做一次保底——若某档因去重被剔空、且该档还有候选，就从该档补 1 部，同时挤掉一部「所属档位数量已大于 1」的作品。因此即使数据分布变化也不会整档消失；但某档若确实一部候选都没有，则跳过——**不凭空凑数，也不把别的作品改档冒名顶替**。

自检方法：拿一份片单统计 `Counter(w["tier"] for w in recs)`，若只有 2 个 key 说明五档保底被破坏了。

### Step 4 — 反馈循环（可选，对话触发）
用户的话语驱动迭代，**状态在对话上下文传递，不落盘、不写文件**：
- 用户说"这几部不喜欢" → 剔除 + 避开相关标签（`reject_tags`）+ 从作品池补足到 20 部。
- 用户说"这几部看过了" → 排除 + 补足未看过的（换一批，而非变少）。
- 连续 2 轮"都不喜欢"且否定集中在主档时，再回溯重估人格（框架 §9.4）。

可运行配方（`scripts/build_share.py` 的 `regenerate`，会同时渲染反馈后片单图）：

```python
from build_share import regenerate
# 场景 A：不喜欢 + 避开属性
works = regenerate({"mode":"dislike","items":["排球少年!!","灌篮高手"],"reject_tags":["运动"]},
                   "<out>/share_list_feedback.png", persona=persona, user_vec=user_vec,
                   region_priority=region_priority)
# 场景 B：看过了 → 换一批没看过的
works = regenerate({"mode":"seen","items":["排球少年!!","强风吹拂"]},
                   "<out>/share_list_seen.png", persona=persona, user_vec=user_vec,
                   region_priority=region_priority)
```

### Step 5 — 渲染分享图（optional）

调用渲染脚本生成**两张图**：用户人格卡（`share_persona.png`，含卡通形象 + 六维 DNA 档案）+ 片单长图（`share_list.png`）。脚本只输出这两张，**不要**自行调用已弃用的 `build_one_page`（会产生多余的第三张图）。

⚠️ REQUIRED **覆盖确认（条件触发）**：渲染前先检查 `<out>` 下是否已存在同名 `share_persona.png` / `share_list.png`。若存在，用结构化选项让用户三选一：**① 渲染到带时间戳的新文件名（推荐，零风险）** / **② 确认覆盖** / **③ 跳过渲染**。首次生成（无同名文件）不打断，直接渲染。

```bash
python <SKILL>/scripts/build_share.py --persona "热忱群像派" --out-dir <out>
# 可选：--skip-demo 跳过 dislike/seen 演示图
```

- 路径与字体**全部相对脚本**，移动到任何机器开箱即用（脚本内置系统 CJK 字体回退）。
- 卡通形象：每个被匹配到的人格渲染其固定 mascot，所有用户一致。
- **片单长图不要传 `status_text`**：`build_list(works=recs, out_path=...)` 不传该参数时，顶部不会渲染那条「你喜欢的：…」状态条。用户明确要求片单图只呈现推荐结果本身，不回显其输入清单。
  - 例外：`regenerate()` 内部会传反馈文案（如「已剔除 2 部不喜欢的作品…」），那是**反馈轮**的产物，属于有效信息，保留。

## 命令行参数（Options）

渲染脚本 `build_share.py` 支持的 flag（对话态调用时由 LLM 决定是否需要）：

| Flag | 说明 | 默认值 |
| --- | --- | --- |
| `--persona <人格名>` | 指定要渲染的人格（如「热忱群像派」），不传则由对话中匹配的 persona 决定 | 当前匹配人格 |
| `--out-dir <路径>` | 图片输出目录 | 脚本同级 `out/` |
| `--skip-demo` | 跳过 dislike/seen 演示图，只渲染人格卡 + 片单长图 | 否（默认渲染演示图） |

## 安全约束（执行引擎必读）

- 渲染脚本会**直接覆盖**同名 PNG（`share_persona.png` / `share_list.png`），无需也不应手动清理目录。
- **禁止**在运行本 skill 时执行任何删除 / 清空命令（`rm -rf`、`rm -r`、`shutil.rmtree` 等）。所有产物由脚本自身管理，执行引擎不得自行删除文件。
- 反馈循环是纯对话态流程，不写数据库、不持久化用户数据。

## 资产与依赖

- `scripts/anime_pool_merged.py`：约 2482 部动画作品库（仅含已做 persona 标注的作品；已治理：日文/罗马音标题→通行中文名并保留原名于 `aliases`，跨语言同名合并，争议作品由 `curation.py` 屏蔽）。**该库是生成产物，不要手工编辑**。
- `scripts/anime_pool.py`：作品池加载层。**在此统一做繁简/日文异体字归一化**（OpenCC `t2s` + 兜底映射表），对 `name` / `cat` / `synopsis` / `reason` / `aliases` 生效，保证对外输出的文案一律简体。
- `scripts/works_pool.py`：检索引擎（`PERSONA_VECS` / `pool_query` / `infer_region_priority` / `neighbor_personas` / `work_vec`）。
- `scripts/build_share.py`：分享图渲染（`build_persona` / `build_list` / `regenerate`）。
- `scripts/apply_feedback.py`：反馈重推 CLI（`--dislike` / `--seen` / `--tags`）。
- `scripts/dna_analyzer.py`：DNA 分析器（`compute_dna` / `match_personas` / `resolve_persona` / `recommend` / `run`）。
- `references/观影DNA分析框架.md`：完整人格定义、六维模型、匹配与档位、反馈循环（§9）逻辑。
- `references/persona-spec.md`：12 人格目标向量 + tier/cat 规范速查。
- `references/扩库提示词.md`：需扩充作品库时，用 LLM 批量扩库的提示词模板（未来迭代用）。
- `assets/stickers/`：12 个人格卡通 mascot（静态 PNG，完整包随包分发）。
- `scripts/stickers_data.py`：**卡通贴图的 base64 内嵌副本**（纯文本，448×448 / 256 色）。`build_share._mascot_image` 优先用它——因此即使分发平台禁止上传 PNG（如 SkillHub），下载到的包**仍能渲染出卡通形象**，无需任何二进制文件。
- 依赖（见 `requirements.txt`）：
  - `Pillow>=10.0` —— **只有渲染图片才需要**，纯检索/出文字片单无需安装。
  - `opencc-python-reimplemented>=0.1.7` —— 繁简归一化用。已做 `try/except` 兜底：缺失时**不崩溃**，但日文异体字标题（如 `崩壊`/`帰`）会保持原样，因此新环境请照常安装。
- 兜底映射表 `_EXTRA_SIMPLIFY`（在 `anime_pool.py`）用于补 OpenCC 覆盖不到的日文新字体，发现新的异体字标题时往这里追加即可。

## 字体说明（重要）

本 skill **不打包专有商业字体**（如 Apple Hiragino）以避免再分发授权问题。`build_share.py` 的 `find_font()` 已内置回退顺序：包内 `assets/fonts/` → macOS `PingFang` / `Hiragino` → Windows `微软雅黑` → Linux `Noto Sans CJK` / `文泉驿`。若目标机器无可用 CJK 字体，把任意开源字体（如 `NotoSansCJK-Regular.ttc`）放入 `assets/fonts/` 即可。

## 注意

- 新手用户请先读包内 `README.md`：含安装、对话口令模板与常见问题，无需技术背景即可上手。
- 分享版仅含已做 persona 标注的作品（persona 非空，`pool_query` 按 persona 精确召回）；冷门日漫（约 5200 部，`persona` 为空）不在本版作品库中，如需扩充请用内部版（含全量 7675 部）或见 `references/扩库提示词.md` 继续标注接入。

## Pre-delivery self-check（交付前自检）

交付文字片单和/或图片前，逐项核对：

1. ⚠️ **无争议作品（合规红线）**：逐部核对名单里没有 `curation.is_blocked(name) == True` 的作品（当前重点：「我的英雄学院」全系列 / 剧场版 / 衍生作，含「我的英雄学院 THE MOVIE 英雄崛起」）。一旦出现，说明名单混入了**非 `pool_query` 来源**的作品——回 Step 3 重跑，**不要手工删补**。
2. ⚠️ **无同系列重复**：`Counter(series_key(w["name"]) for w in recs)` 每个 key 的计数都应为 1。同一 IP 的不同季 / 剧场版 / 副标题续作（如「排球少年!! 第二季」与「…乌野高中 VS 白鸟泽学园高中」）不得同时出现；若出现即说明混入了非 `pool_query` 来源的条目，回 Step 3 重跑。
3. ⚠️ **片单恰好 20 部**（`len(recs) == 20`）。
4. ⚠️ **五档齐全**：`Counter(w["tier"] for w in recs)` 应有 5 个 key（like/expand/try/niche/neighbor）；若只有 2 个即异常，说明五档保底被破坏，回 Step 3 重跑。
5. **地区分布符合用户口味**：`region_priority` 由用户作品名单推断（喜国漫则该地区在前），不要写死日本。
6. 若渲染了图：确认 `<out>` 下未误覆盖用户已有文件（见 Step 5 覆盖确认）。
7. 片单长图**未回显**「你喜欢的：…」状态条（未传 `status_text`）；纯文字片单已含 name/cat/synopsis/reason 四要素。
8. **无省略号截断**：检查文字片单/表格中，每一档的作品列表都是完整的，没有出现 `...`、`…`、`等`、`等 N 部` 等截断。脚本已返回完整 20 部，输出端不得折叠。
