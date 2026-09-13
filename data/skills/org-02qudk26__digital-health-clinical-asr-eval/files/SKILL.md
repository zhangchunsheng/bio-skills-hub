---
name: "digital-health-clinical-asr-eval"
displayName: "临床 ASR 飞轮 — 评测（阶段 3）"
description: "临床 ASR 飞轮的阶段 3。对一个 NeMo manifest 打分，产出五段式的 KER 排行榜（按 ipa_source 的诊断性拆分）。不用于 ASR 鉴权（/riva-asr）。"
version: "1.1.0"
author: "Ben Randoing <brandoing@nvidia.com>"
tags:
  - clinical-asr
  - eval
  - ker
  - leaderboard
  - flywheel
tools:
  - Read
  - Write
  - Bash
  - Skill
license: Apache-2.0
compatibility: "需 NVIDIA_API_KEY（必填，用于经 NVCF 托管的 ASR NIM）。一个由 /digital-health-clinical-asr-build 产出的 NeMo 格式 manifest（或携带临床扩展字段的外部 manifest）。所有 ASR 调用形态及 WER/CER/KER/SER 打分配方均已内联——无需兄弟 agent 技能。"
metadata:
  author: "Ben Randoing <brandoing@nvidia.com>"
  tags:
    - clinical-asr
    - flywheel
    - eval
    - ker
    - leaderboard
  team: healthcare-tme
  domain: ai-ml
  stage: 3
  previous_skill: digital-health-clinical-asr-build
  next_skill: digital-health-clinical-asr-finetune
---

<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# 临床 ASR 飞轮 — 阶段 3（评测）

> **⚠ Agent：回答前请阅读下方的"关键工作流规则"一节。** 本 SKILL.md 是自包含的——`evals/`、`references/`、`assets/` 仅是指针，并非承载内容。方法论问题请直接依据本文件回答；仅在用户明确要求针对真实 manifest 执行时才调用工具。

你负责的是**打分与路由**阶段。用户带着一个 NeMo 格式的 `manifest.jsonl` 进入（要么来自 `/digital-health-clinical-asr-build`，要么从别处带来）。你用所选的 ASR NIM 转写它，计算四项指标，产出五段式排行榜，并读取决策树，决定用户应推进到 `/digital-health-clinical-asr-finetune`、回环到 `/digital-health-clinical-asr-build`，还是停下来加固评测。

**本技能不生成音频。** 若 manifest 缺失或为空，请用户回退到 `/digital-health-clinical-asr-build`。

## 音频会离开你的环境——在发送任何片段前请向用户披露

本阶段会将每个 manifest 行的 WAV 文件与其参考文本传输到外部 NVIDIA 服务。在发起首次 ASR 调用前请说明：

| 服务 | 发送了什么 | 何时 |
|---|---|---|
| **NVIDIA NVCF Parakeet/Nemotron ASR**（`grpc.nvcf.nvidia.com`） | manifest 引用的每个音频片段（原始 PCM 字节），外加参考转写稿及用于打分的临床扩展元数据 | 步骤 3b，每个 manifest 行一次调用 |

这些片段应当是**阶段 2 生成的合成音频**（在用户整理的术语列表上经 Magpie TTS 生成）——而非真实患者音频。**请勿将真实 ASR 录音、真实患者接触记录或任何 PHI 经本技能传出。** 打分在本地运行（纯 Python 的 WER/CER/KER/SER，若已安装则用 `jiwer`）。打分这一步本身不传输任何东西；只有 ASR 那一步会。

## 关键工作流规则（每次激活都适用）

对于方法论问题（排行榜结构、KER 定义、决策树），请依据本文件回答。除非用户明确要求针对真实 manifest 执行，否则不要调用工具、调用其它技能或运行脚本。在任意回复中都要呈现这些事实：

1. **先考虑分流。** 如果用户问的是打分之外的事，请路由并停止，不运行任何工作流：
   - ASR 模型目录选择 / 比较 / 替代 NIM → `/riva-asr`
   - ASR 鉴权（API key、bearer token、function ID）→ `/riva-asr`
   - ASR gRPC 协议、流式、批处理、分块、重试 → `/riva-asr`
   - NIM 部署 / `riva-build` / `riva-deploy` → `/riva-asr-custom`
   - NGC / Docker / NVIDIA Container Toolkit → `/riva-nim-setup`
   - 还没有 manifest → `/digital-health-clinical-asr-build`
   - 已知 KER 且想立刻微调 → `/digital-health-clinical-asr-finetune`
2. **默认 ASR NIM 为 `nvidia/parakeet-tdt-0.6b-v2`**（NVCF 函数 ID `d3fe9151-442b-4204-a70d-5fcc597fd610`，离线 gRPC）。环境变量覆盖项：`ASR_MODEL_NAME`（排行榜显示名）、`ASR_NVCF_FUNCTION_ID`（切换到其它托管 NIM——例如当 Parakeet 后端故障时换成 Whisper Large v3 `b702f636-…`，或换成微调过的 NIM）、`ASR_ENDPOINT`（自托管 gRPC，优先）。在消耗 API 额度前，把所选 NIM **及其解析出的 function-id** 回显给用户。
3. **ASR 转写在步骤 3b 内联**（NVCF gRPC + `riva.client.ASRService.offline_recognize`，与阶段 1 相同的鉴权模式）。对于更深入的协议/鉴权问题、替代 NIM 目录，或自托管 Riva NIM 配置，请交给 `/riva-asr`。
4. **KER 是头条指标。** 逐行检查：被标记的 `term` 词必须以*顺序、连续、相邻*的方式出现在归一化假设中。`cefazolin → cefa zolin` 算作未命中。聚合 WER 会掩盖临床上危险的失败；两者都要报告，KER 才是门控。
5. **按 `ipa_source` 的拆分是排行榜中信息量最大的单一数字。** `merriam-webster` 与 `magpie_g2p` 之间的差值证明了 SSML override 流水线确实在做实事。请向用户朗读这一节。
6. **特例路由。** `merriam-webster` 行好、`magpie_g2p` 行差 → 是发音覆盖率缺口，**而非**模型缺口。路由回 `/digital-health-clinical-asr-build` 步骤 2d。**不要**作为首选建议 `/digital-health-clinical-asr-finetune`。
7. **五段式排行榜顺序。** 头条（WER/CER/KER/SER）→ 按 `entity_category` 的 KER → 按 `ipa_source` 的 KER → 按 `noise_level` 的 KER → 逐术语 KER（从最差开始）。按 `ipa_source` 的章节是强制的；它是 SSML 流水线生效的证明。

## 用途

为一个临床 ASR manifest 打分，产出五段式 KER 排行榜，并经评测后决策树路由用户。方法论细节（指标定义、归一化、排行榜顺序、特例路由）位于上方的关键工作流规则与下方说明中。

## 何时使用本技能

在用户出现如下表述时激活：

- "为我的 ASR manifest 打分"
- "Parakeet TDT v2 的 KER 是多少？"
- "在 cycle-N 上跑评测"
- "在临床基准上比较两个 ASR 模型"
- "生成排行榜"
- "我有一个 manifest.jsonl，怎么给它打分？"
- "为什么 WER 是 0.07 时 KER 却是 0.4？"
- "我们应该微调吗？"*（这是评测侧的问题——评测后决策树就在本技能中）*

**字面关键词非激活检查**——若用户消息包含以下任一：`authenticate`、`API key`、`bearer`、`function ID`、`gRPC`、`streaming`、`chunking`、`batching`、`transcription retry`、`riva-build`、`riva-deploy`、`NIM deploy`、`NGC`、`Docker`、`Container Toolkit`，或问"哪个 ASR 模型最好" / "比较模型" / "厂商差异"——**不要**激活打分工作流。套用上方关键工作流规则 #1 路由到正确的兄弟技能并停止。即便用户在关键词旁提到"KER"或"eval"也同样适用。

## 前置条件

- **一个带临床扩展字段的 NeMo 格式 manifest**（`term`、`entity_category`、`ipa_source`、`voice_id`、`noise_level`、`context_type`）。其 schema 记录在构建技能的 `references/manifest-schema.md` 中。
- **已导出 `NVIDIA_API_KEY`**（阶段 1 前置条件仍适用）。
- 已安装 **`nvidia-riva-client` + `soundfile`**（阶段 1 前置条件）。自托管 Riva NIM 的详情见 `/riva-asr` 选项 B。
- **音频文件实际存在于磁盘上**——在消耗 API 额度前，先运行 manifest-schema 参考中的音频存在性预检。

## 使用说明

### 3a. 选择 ASR NIM

**默认**：`nvidia/parakeet-tdt-0.6b-v2`，经 NVCF gRPC（离线），函数 ID `d3fe9151-442b-4204-a70d-5fcc597fd610`。这是 NVIDIA 当前英文 ASR 的推荐项——目录中速度最快/最便宜，且在 NeMo 的原生 SFT 配方中受支持，因此阶段 3 基线与阶段 4 微调共用同一模型族。

三种运行时环境变量覆盖旋钮（`ASR_MODEL_NAME` 用于排行榜显示、`ASR_NVCF_FUNCTION_ID` 切换其它托管 NIM、`ASR_ENDPOINT` 用于自托管 gRPC），以及完整的替代 NIM 目录（Parakeet TDT 1.1B、Parakeet CTC 1.1B、Whisper Large v3、Nemotron 流式，含函数 ID 与调用形态说明）：`references/offline-asr-recipe.md`。

在消耗 API 额度前，把所选 NIM、解析出的函数 ID 及任何环境变量覆盖项回显给用户。在托管 Parakeet TDT v2 上跑 200 行的 manifest 很便宜；但在 1000 行 manifest 上意外跑错模型就不便宜了。

### 3b. 转写

对 `manifest.jsonl` 中的每一行，转写 `audio_filepath` 并写出 `per_sample.json`（每行一个 JSON 对象，JSONL 或 JSON 数组——由调用方选择）：

```json
{
  "audio_filepath": "...",
  "ref": "<row.text>",
  "hyp": "<asr output>",
  "term": "<row.term>",
  "entity_category": "<row.entity_category>",
  "ipa_source": "<row.ipa_source>",
  "voice_id": "<row.voice_id>",
  "noise_level": "<row.noise_level>",
  "context_type": "<row.context_type>"
}
```

**配方**（完整 Python 见 `references/offline-asr-recipe.md`）：`transcribe_manifest(api_key, manifest_path, out_path, language_code="en-US")` 打开一个到 NVCF 的离线 gRPC 流（若设置了自托管 Riva 则到 `ASR_ENDPOINT`），对每行调用 `riva.client.ASRService.offline_recognize`——临床 manifest 中的句子 ≤ 30 秒，故无需流式/批处理——并写出上方 JSONL。与阶段 1 冒烟测试相同的 `auth_for` 形态。Agent 框架显式传入 `api_key`；配方在顶部读取三个环境变量覆盖项（`ASR_NVCF_FUNCTION_ID`、`ASR_MODEL_NAME`、`ASR_ENDPOINT`），以便审计者在一处看到所有旋钮。

**Whisper 回退**（当 Parakeet 的 NVCF 后端因 Triton 报出 `CUDA illegal-memory-access` 故障时）与**自托管 Riva NIM**（`ASR_ENDPOINT=localhost:50051`）的环境变量模式：见 `references/offline-asr-recipe.md`（§Whisper 回退、§自托管 Riva NIM）。

**弹性旋钮交由用户决定。** 若 NVCF 在批处理中途返回 `RESOURCE_EXHAUSTED`，循环会在该行抛出错误；从该失败行重跑。流式/批处理/带退避的重试不在范围内——见 `/riva-asr`。

### 3c. 计算四项指标

对每一行，计算：

| 指标 | 测量内容 | 为何保留 |
|---|---|---|
| **WER** | 词错率（归一化后的 token 上的 Levenshtein 距离） | 行业标准；对临床而言是钝器 |
| **CER** | 字符错率 | 捕获长复合名词上的近似错误 |
| **KER** ★ | 关键词错率——被标记的 `term` 是否出现在假设中（归一化、**连续**匹配）？ | **头条临床信号** |
| **SER** | 句错率（只要有错为 1，全对为 0） | 健全性边界；医生所经历的体验 |

**归一化（在计算四项指标前应用于 `ref` 与 `hyp` 双方）：**

1. 转小写。
2. NFKD 归一化（智能引号 → ASCII 等）。
3. 去除标点**除连字符外**。
4. 将连续空白压缩为单个空格。

**内联打分配方**——`normalize` / `edit_distance` / `wer` / `cer` / `ker` / `ser`（纯 Python，无 `jiwer` 依赖）：见 `references/scoring-recipes.md`。按行取各指标的 `mean(per-row score)` 进行跨行聚合。

**严格 KER**——term 词必须以*顺序、相邻*的方式出现在归一化假设中。这是保守的：`cefazolin → cefa zolin` 计为未命中。在临床上这是正确的取舍——下游药房查找会在拼错的 token 上失败。

KER 不惩罚周围的错误。一行中 term 正确、句子其余部分一团糟，仍记 KER=0；该行的 WER 会另行暴露更广泛的问题。

### 3d. 拆解 + 排行榜

写出一个五段式 markdown 排行榜，**顺序如下**：

1. **头条**——所选模型的整体 WER、CER、KER、SER。
2. **按 `entity_category` 的 KER**——drug vs procedure vs anatomy vs…… 这才是用户为部署真正关心的。
3. **按 `ipa_source` 的 KER**——**排行榜中信息量最大的单一数字。** `merriam-webster` 与 `magpie_g2p` 行之间的差值，证明了 SSML override 流水线在做实事。*请向用户朗读这一节。*
4. **按 `noise_level` 的 KER**——临床环境很吵。`snr_5db` 行比 `clean` 更接近现实。
5. **逐术语 KER**（从最差开始）——这些是你阶段 4 微调的目标。

一个代表性的 `ipa_source` 拆分及 merriam-webster vs magpie_g2p 差值解读：见 `references/scoring-recipes.md` §Representative ipa_source split。差值讲述了部署的故事——若用户看到巨大差距并问"我们应该微调吗？"，答案是*还不行*；把他们路由回 `/digital-health-clinical-asr-build` 的 IPA QA 流水线（阶段 2d）。见下方决策树。

## 决策树（评测后）

读取**优先类别的 KER**（多数临床工作流看 drug KER，手术工作流看 procedure KER）并路由：

| 优先类别的 KER | 建议 |
|---|---|
| **> 0.3** | `/digital-health-clinical-asr-finetune`。manifest 已经是 NeMo 格式就绪状态。注意：行数 ≥ 100 才具备可信微调信号的最低要求；若 manifest 更小，先经 `/digital-health-clinical-asr-build` 扩充它。 |
| **0.1 – 0.3** | 要么扩充术语列表（回到 `/digital-health-clinical-asr-build`，加入新领域术语——通常比调参更便宜地暴露更多失败），**要么**微调。在*首次*评测时，扩充。在*后续*评测中若已扩充过 manifest，则调参。 |
| **< 0.1** | 强基线。先别调参——你是在针对一个已饱和的指标做优化。把评测做得更狠：加入音色、噪声级别、上下文、对抗性术语。回环到 `/digital-health-clinical-asr-build`。 |

**特例——`merriam-webster` 行得分好但 `magpie_g2p` 行差。** 那是发音提示覆盖率缺口，**而非**模型缺口。路由回 `/digital-health-clinical-asr-build` 步骤 2d（IPA QA 审查），而非 `/digital-health-clinical-asr-finetune`。在 TTS 发音缺口上微调，是教模型去误识它自己的错误——错误的修复方式。

## 示例

**场景 A — 对全新 cycle-1 manifest 的首次评测。** 用户：*"我已有 `manifest.jsonl`，含 200 行临床音频，带 `term` 与 `entity_category` 字段。怎么给它打分？"* → 完全跳过阶段 2。运行音频存在性预检。选择 `parakeet-tdt-0.6b-v2`（默认）并回显选择 + 解析出的函数 ID。运行内联的步骤 3b 配方（`transcribe_manifest(...)`）。计算四项指标。产出五段式排行榜。向用户朗读按 `ipa_source` 的拆分。对 drug KER 应用决策树。

**场景 B — 解读混合结果。** 用户：*"评测显示标记 `merriam-webster` 的行 KER 0.05，但标记 `magpie_g2p` 的行 KER 0.40。我该微调吗？"* → 不——这正是特例。模型没问题；发音提示未覆盖长尾术语。把用户路由回 `/digital-health-clinical-asr-build` 步骤 2d，试听 `magpie_g2p` 行并将已验证 IPA 追加到 `pronunciation_overrides.csv`。在重建后重跑阶段 3，再考虑阶段 4。

## 产出的制品

- `per_sample.json`——逐行转写结果，保留全部临床扩展字段（ASR `hyp` 连接到 manifest 的 `ref` 与元数据）
- `results.csv`——逐行 WER/CER/KER/SER 分数
- `leaderboard_cycle<N>.md`——五段式 markdown 报告

（文件名由用户选择；上方名称是本技能其余部分假定的约定。）

## 故障排查

- **"找不到 manifest"** → 用户跳过了阶段 2。路由到 `/digital-health-clinical-asr-build` 或确认 `$MANIFEST_PATH`。
- **所有行 KER=1** → `ref` 与 `hyp` 之间的归一化不一致。对双方应用四个归一化步骤。
- **所有行 KER=0 但 WER 高** → 可能是 manifest 错位（音频行不匹配）。手工抽查几个 `(ref, hyp)` 对。
- **`merriam-webster` 低、`magpie_g2p` 高** → 发音覆盖率缺口。路由到 `/digital-health-clinical-asr-build` 步骤 2d。**不要微调**——模型不是问题。
- **`merriam-webster` 与 `magpie_g2p` 都高** → 真实模型缺口。阶段 4 是正确的路由（manifest ≥ 100 行）。
- **`clean` 行正常、`snr_5db` 暴涨** → 鲁棒性缺口；经 `/digital-health-clinical-asr-build` 扩充噪声多样性。
- **Riva-NIM 与离线 NeMo 结果分歧** → Riva 预处理 / `riva-build` 标志。路由到 `/riva-asr-custom`。
- **大 manifest 上的 `RESOURCE_EXHAUSTED`** → 30 秒后重试；切片并重新运行丢弃的行。内置退避：`/riva-asr`。
- **`Auth.__init__() got 'ssl_cert'`** / **Parakeet 函数 ID 上的 CUDA illegal-memory-access**：见 `references/offline-asr-recipe.md`（ssl_root_cert 重命名 + §Whisper 回退）。

其它问题：识别上游归属。ASR 协议 / NIM 部署 → `/riva-asr`。打分 → 此处。

## 局限性

- **默认仅英文。** 分词 + 归一化假设拉丁字母表与 en-US 词表。
- **严格连续的 KER 是保守的。** 像 `cefa zolin` 这样的近似未命中也算未命中。这是有意的——药房查找在近似未命中上会失败。想要"软"匹配的用户可切换到音素级编辑距离，那是方法论扩展，而非配置微调。
- **每次评测运行仅一个模型。** 比较两个模型意味着运行评测两次并对比两个 `leaderboard_cycle<N>.md` 文件（或自行扩展配方以写出多模型行）。
- **假设仅托管路径。** 自托管 NIM 可用，但需先完成 `/riva-nim-setup`。

## 后续步骤

- **前向（KER > 0.3、manifest ≥ 100 行）：** `/digital-health-clinical-asr-finetune`。
- **回退构建（首次评测 KER 0.1–0.3，或 `magpie_g2p` 缺口）：** `/digital-health-clinical-asr-build`。
- **停止（KER < 0.1）：** 评测已饱和。在宣告胜利前先加固它。
- **横向**用于 ASR 协议 / 鉴权 / 流式 / 自托管 NIM 详情：`/riva-asr`。

## 参考

- [`references/offline-asr-recipe.md`](references/offline-asr-recipe.md)——完整步骤 3b Python 配方（`transcribe_manifest`、`resolve_asr_config`、`build_asr_auth`），含调用形态说明的函数 ID 目录，Whisper 回退，自托管 Riva NIM 设置
- [`references/scoring-recipes.md`](references/scoring-recipes.md)——带规范 4 步归一化的纯 Python WER/CER/KER/SER 打分函数
