---
name: "digital-health-clinical-asr-build"
displayName: "临床 ASR 飞轮 — 构建基准（阶段 2）"
description: "临床 ASR 飞轮的阶段 2。用于整理临床术语、标注 IPA 并合成 NeMo manifest。不用于打分（请使用 /digital-health-clinical-asr-eval）。"
version: "1.1.0"
author: "Ben Randoing <brandoing@nvidia.com>"
tags:
  - clinical-asr
  - dataset
  - ipa
  - magpie
  - nemo-manifest
  - flywheel
tools:
  - Read
  - Write
  - Bash
  - Skill
license: Apache-2.0
compatibility: "需 NVIDIA_API_KEY（必填，用于经 NVCF 托管的 Magpie TTS）。DICTIONARY_API_KEY（可选，用于 Merriam-Webster 医学词典查询）。必须先完成阶段 1（/digital-health-clinical-asr-setup）。所有 TTS、IPA 及合成配方均已内联——无需兄弟 agent 技能。"
metadata:
  author: "Ben Randoing <brandoing@nvidia.com>"
  tags:
    - clinical-asr
    - flywheel
    - dataset
    - ipa
    - magpie
  team: healthcare-tme
  domain: ai-ml
  stage: 2
  previous_skill: digital-health-clinical-asr-setup
  next_skill: digital-health-clinical-asr-eval
---

<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# 临床 ASR 飞轮 — 阶段 2（构建基准）

> **⚠ Agent：回答前请通读整篇 SKILL.md。** 本阶段是交互式且有门控的。具体来说：在提出术语（步骤 2a）**之前**，先向用户提出 1–2 个感知专科的澄清问题；在步骤 2c 中带用户走完两级 IPA 流水线（override → merriam-webster → magpie_g2p）；在完整笛卡尔积合成之前，命中步骤 2d 中明确的 QA 试听门控；并告知用户他们在阶段 3 将看到的核心指标 **KER**。跳过其中任何一步都会破坏方法论。

你负责的是**整理与合成**阶段。用户从 `/digital-health-clinical-asr-setup` 进入，离开时携带 NeMo 格式的 `manifest.jsonl` 及其引用的音频——两者都准备好在 `/digital-health-clinical-asr-eval` 进行打分。

保持对话式。这是飞轮中最温暖、最具领域感知的一步：你在询问临床医生（或与他们共事的人）哪些术语如今会造成困扰，并围绕他们的实际情况塑造一个基准。问简短、聚焦的问题。向用户展示正在被加入的内容。不要说教。

## 数据会离开你的环境——在发送任何术语前请向用户披露

本阶段会将用户整理的内容传输到两个外部服务。在调用任一接口前，请向用户说明：

| 服务 | 发送了什么 | 何时 |
|---|---|---|
| **Merriam-Webster**（`dictionaryapi.com` API 或 `merriam-webster.com` 公开站点） | 种子列表中的每个术语发起一次 HTTP 请求——术语出现在 URL 路径中 | 步骤 2c —— 见下方 MW 路径要点 |
| **NVIDIA NVCF Magpie TTS**（``grpc.nvcf.nvidia.com``） | 每个生成的临床句子（文本，以及任何 SSML IPA 包装） | 步骤 2d 与 2e，每次合成调用 |

两个端点都期望**非 PHI 的合成内容**——你整理的术语列表、由 `/data-designer`（或你的回退模板）据此生成的句子。**请勿将真实患者记录、真实 ASR 转写稿或任何 PHI 经本技能传出。** 如果术语列表本身敏感（专有药物代号、未发布产品名、客户保密的适应症），在继续前请与用户确认：在其组织的数据治理政策下，对外传输 API 是可接受的。

如果完全不接受 MW 传输：采用下方的路径 C（跳过 MW；流水线回退到 Magpie G2P，对长尾术语的覆盖率降低）。

## 用途

整理一份临床专科术语列表，通过 Magpie TTS 以两级 IPA 流水线为其生成评测音频，并写出带有临床扩展字段（`term`、`entity_category`、`ipa_source`、`voice_id`、`noise_level`、`context_type`）的 NeMo 格式 manifest。其输出即为阶段 3 的输入。

最终用户将得到：

```
$EVAL_DIR/cycle<N>/
├── audio/<slug>.wav        合成的音频片段
├── manifest.jsonl          NeMo 格式 + 临床扩展
├── term_seed.csv           整理得到的输入
└── pronunciation_overrides.csv   可在各周期间追加
```

（`$EVAL_DIR` 由用户自行选择——本技能不强制布局。上方结构仅为建议，并非要求。）

## 何时使用本技能

在用户出现如下表述时激活：

- "构建临床 ASR 基准"
- "为 ASR 评测整理药物名 / 手术名"
- "为医学术语生成评测音频"
- "从临床术语创建 NeMo manifest"
- "把肿瘤 / 心脏 / 骨科术语加入我的基准"
- "试听这些药名的 TTS 发音"
- "给我做一个 cycle-N manifest"

**不要**在以下情况激活（另：若消息提及 `auth`、`API key`、`gRPC`、`streaming`、`riva-build`、`NIM deploy`、`NGC` 或 `Docker`，请按下述要点路由并停止）：

- 用户已有 manifest 且想为其打分 → `/digital-health-clinical-asr-eval`
- 用户想在已有 manifest 上微调 → `/digital-health-clinical-asr-finetune`
- 用户询问通用 TTS / SSML / 声音克隆 / 音色目录问题 → `/read-aloud`（或 `/riva-tts`）
- TTS/ASR 的 **auth / API key / gRPC / streaming** → `/riva-tts` 或 `/riva-asr`
- **NIM 部署** 或 `riva-build` / `riva-deploy` 标志 → `/riva-asr-custom` 或 `/riva-tts-custom`
- **NGC / Docker / NVIDIA Container Toolkit** → `/riva-nim-setup`
- 用户询问通用合成数据问题 → `/data-designer`

## 前置条件

- **已完成 `/digital-health-clinical-asr-setup`**——已导出 `NVIDIA_API_KEY`，已安装 Python 依赖，六个上游技能已确认可用。
- **`/read-aloud`**（或 `/riva-tts`）可达。默认使用经 NVCF 托管的 Magpie。自托管的 Magpie NIM 也可用，但会在前置条件链中加入 `/riva-nim-setup`。
- **`/data-designer`** 可达。若 `/data-designer` 不可用，首个周期允许使用模板回退，但需标记这些行，以便未来周期可重新生成。
- **用户拥有的工作目录**。本技能建议 `$EVAL_DIR/cycle<N>/`，但不强制。

## 使用说明

### 2a. 专科访谈 → `term_seed.csv`

**一次只问一个问题**。目标是浮现 4–10 个带正确 `entity_category` 的候选术语，而非写一本教科书。

按顺序提问：

1. *这是针对哪个专科 / 工作流？*（肿瘤口述、ICU 交接、心理接诊、骨科术后……）
2. *你见过哪些 ASR 失败模式？*——药名、多词手术名、缩写、复合病症。
3. *哪些是每天都会出现的词，哪些是最难的？*——日常常见词成为健全性基线；日常难词成为信号。

提出 4–10 个带 `entity_category` 的候选术语。写入前请用户确认。然后写出 `term_seed.csv`：

```csv
term,entity_category
cefazolin,drug
acetabular reamer,procedure
tibial plateau,anatomy
femoroacetabular impingement,condition
hemoglobin a1c,lab
respiratory therapist,role
```

**类别词表是固定的。** KER 依赖它。允许的取值：

```
drug | procedure | anatomy | condition | lab | role
```

若用户提出新类别，请驳回：要么它映射到六个之一，要么方法论需要一次有意的扩展（那是未来周期的工作，而非一次性临时的添加）。

### 2b. 经 `/data-designer` 生成句子

向 `/data-designer` 下达如下简报：

> 对 `term_seed.csv` 中的每一行，生成一条或多条自然英文句子，以符合该行 `entity_category` 的方式嵌入 `term`。输出 schema：`{term, entity_category, sentence, context_type}`。每个术语生成 3–5 个 `context_type` 变体。初始 `context_type` 词表：`dictation`、`handoff`、`chart_note`、`history`。句子长度 10–30 词。

本步骤的输出是一个逐术语的句子变体文件。文件名任意——选定一个并在整个周期目录中一致使用。

**模板回退。** 若 `/data-designer` 不可用，使用 4 模板回退（每个 `context_type` 一个）并机械地替换 `term`。在 manifest 中标记这些行（`context_type` 已设置，只是句子不那么自然），以便未来周期可重新生成。

### 2c. 两级 IPA 标注（承载质量的关键杠杆）

每个术语按顺序通过三级流水线：

1. **Override**——`pronunciation_overrides.csv` 携带团队已审核的已验证 IPA。若 `term` 在此命中某行，则 override 优先。
2. **Merriam-Webster**——对未 override 的术语，获取 MW 拼读，转换为 IPA，对照 Magpie 的 en-US 音素集做校验。若两者都成功，该术语标记为 `merriam-webster`。
3. **Magpie G2P（回退）**——若 override 与 MW 都无法产出有效 IPA，则在合成时将纯文本传给 Magpie 的神经 G2P。该行标记为 `magpie_g2p`。

每个 manifest 行都携带 `ipa_source` 标签（`override | merriam-webster | magpie_g2p`）。阶段 3 排行榜中 `merriam-webster` 与 `magpie_g2p` 行之间的差异**正是发音策略生效的证明**——在产出排行榜时请明确指出来。

**三种 MW 查询选择**——都标记为 `merriam-webster`。**A**：`dictionaryapi.com` JSON API + `DICTIONARY_API_KEY`（在 dictionaryapi.com 免费获取）——推荐独立使用。**B**：爬取 `merriam-webster.com` 的 HTML——无需 key，但易受站点 HTML 变动影响；配方内联于 `references/pronunciation-pipeline.md`。**C**：跳过 MW，回退到 Magpie G2P，但长尾覆盖率更弱。两种配方 + 完整的 respelling→IPA 表均位于 `references/pronunciation-pipeline.md`。路径 A 的函数以 `api_key` 作为参数（绝不读取 `os.environ`）；传入 `None` 以跳过 MW。

`pronunciation_overrides.csv` 的 schema：

```csv
term,ipa,verified_by,verified_at,notes
cefazolin,sɛfəˈzoʊlɪn,brandoing,2026-05-13,confirmed against MW respelling + ear test
```

跨周期仅追加。后续重新运行构建会自动拾取新条目。

### 2d. QA 模式合成（**不要**跳过此门控）

在运行完整笛卡尔积之前，为每个术语合成**一个 wav**：使用首个音色、干净噪声、默认上下文。与用户一同试听每个片段。

对每个标记为 `magpie_g2p` 的术语，使用临床后缀模式提出一个 IPA 候选，并在建议前对照 Magpie 的 en-US 音素集做校验：

| 后缀 | 重音模式（示例） |
|---|---|
| `-mycin` | …ˈmaɪsɪn（vancomycin、gentamicin） |
| `-prazole` | …ˈpreɪzoʊl（esomeprazole、omeprazole） |
| `-statin` | …ˈstætɪn（atorvastatin、rosuvastatin） |
| `-sartan` | …ˈsɑːrtən（losartan、valsartan） |
| `-azole` | …ˈeɪzoʊl（fluconazole、ketoconazole） |
| `-cillin` | …ˈsɪlɪn（amoxicillin、piperacillin） |
| `-parin` | …ˈpɛərɪn（enoxaparin、heparin） |

**音素校验模式**——用候选 IPA 实时探测 Magpie 的 en-US 神经 G2P。若 Magpie 接受该 SSML，则该 IPA 在其音素库中。将上方后缀模式作为*预过滤*（廉价启发式），并用实时探测来确认，再提交为 override。`magpie_validates_ipa(ipa, api_key, voice_id)` 配方——一个最小化的 NVCF gRPC 合成调用，以 fail-closed（失败即关闭）方式返回 `True`/`False`——位于 `references/pronunciation-pipeline.md`。

在向用户展示前，对每个候选 IPA 调用一次。在用户批准后，将已验证的 IPA 追加到 `pronunciation_overrides.csv`。在下次 manifest 生成时，该行的 `ipa_source` 会从 `magpie_g2p` 翻转为 `override`。

**进入步骤 2e 前的人审（HITL）试听门控——fail-closed。** 在**对话中明确发生以下任一情况之前**，不得合成完整笛卡尔积、不得将任何暂存 IPA 候选提升进 `pronunciation_overrides.csv`、也不得推进到阶段 3：

1. **用户确认已试听 QA 片段**，并针对每个片段（或每个分桶，如"MW 那组听起来没问题"、"修复 `pembrolizumab`"等）给出判定。提供 `afplay`（macOS）或 `paplay`/`aplay`（Linux）命令供用户播放——然后**停下，等待其听后回复**。仅通过 AskUserQuestion 提示进行纸面批准——点击"全部提升"或"锁定"而未试听——**不满足此门控**。Magpie 校验某 IPA 只能证明它在音素库中；它无法证明它匹配*预期*的发音。只有用户的耳朵能证明这一点。
2. **用户明确选择跳过本周期的试听**，措辞需刻意（例如*"跳过试听，接受错发音可能稀释阶段 3 KER 信号的风险——将其记为 cycle-N 的注意事项"*），而非单次点击透传的副作用。将跳过记录于周期级备注（如 `eval/cycle<N>/cycle_notes.md`），以便未来操作员能看到试听被推迟。

Magpie NVCF 对超过 100 行的任务会激进限流，重做既耗 API 额度又耗时钟时间——但更大的风险是发布一个带有错发音参考音频的 manifest，它会悄悄污染阶段 3 的 KER 信号。花在试听上的时间比重跑周期更省。

### 2e. 完整基准生成

发音锁定后，生成完整笛卡尔积 `|terms| × |voices| × |noise_levels| × |context_types|`。默认：2–4 个 Magpie en-US 音色（Mia/Jason/Ray），`[clean, snr_15db, snr_5db]`，`[dictation, handoff, chart_note, history]`。

自包含合成——无需 `/read-aloud`。`synthesize_row(row, all_overrides, out_dir, api_key)` 配方——打开 NVCF gRPC 流，经 `render_sentence_with_overrides` 将 override 包装进 SSML，将 16-bit 单声道 PCM 写入 `<out_dir>/audio/<slug>.wav`——位于 `references/pronunciation-pipeline.md`（§Synthesis call）。关键不变量：`all_overrides` 携带 `pronunciation_overrides.csv` 中的*每一个*条目（包括像 `intravenously` 这样的上下文词 override），以便渲染器能包裹任何其逐字文本出现在 `row['text']` 中的 override。只包裹 `row['term']` 会静默丢弃上下文词的 override。

噪声注入（clean → `snr_15db` → `snr_5db`）与 manifest schema（NeMo 规范字段 + 临床扩展，外加预检 schema 与音频存在性检查）均位于 `references/manifest-schema.md`。

**当乘积 > 100 行时发出警告。** Magpie NVCF 限流会在大任务上产生约 5–10% 的 `RESOURCE_EXHAUSTED` 丢弃。请重跑被丢弃的行。

### 阶段 2 完成清单

在五个子步骤全部跑完前，不要认为阶段 2 已完成。Agent 常在 2a 或 2b 后就停止；目标是得到一个合成的 manifest 加一次交接：

- **2a**——`term_seed.csv`，4–10 个术语，`entity_category ∈ {drug, procedure, anatomy, condition, lab, role}`
- **2b**——每个术语 3–5 个 `context_type` 句子变体
- **2c**——每个术语标记为 `ipa_source ∈ {override, merriam-webster, magpie_g2p}`
- **2d**——QA wav 已试听，IPA override 经用户明确批准锁定
- **2e**——`manifest.jsonl` + 笛卡尔积的逐行音频
- **交接**——指明 `/digital-health-clinical-asr-eval` 为下一技能，并指明 **KER** 为其核心指标

写入仅限用户选定的 `$EVAL_DIR/cycle<N>/`。不要写其它地方、不要修改环境变量、不要安装包——这些属于 `/digital-health-clinical-asr-setup`。

## 示例

**场景 A — 全新肿瘤基准。** 用户：*"我们看到化疗药名被错转录。我从哪开始？"* → 步骤 2a：确认专科为肿瘤，询问哪些药（免疫疗法生物制剂、铂类、紫杉烷类）。提出约 10 个候选：`cisplatin`、`paclitaxel`、`pembrolizumab`、`nivolumab`、`carboplatin`、`docetaxel`、`bevacizumab`、`trastuzumab`、`cetuximab`、`pemetrexed`。写出 `term_seed.csv`，全部 `entity_category=drug`。步骤 2b：为 `/data-designer` 下达简报，每个术语 4 个上下文变体 = 40 个句子。步骤 2c：对每个做 MW 查询——像 `pembrolizumab` 这样的生物制剂很可能落到 `magpie_g2p`；铂类很可能命中 MW。步骤 2d：每个术语合成一个 QA wav，带用户走查 `pembrolizumab` 等片段，用 `-mab` 后缀重音模式提出 IPA 候选。步骤 2e：批准后，运行 10 术语 × 2 音色 × 2 噪声级别 × 3 上下文 = 120 行。

**场景 B — 追加到已有周期。** 用户：*"我有一个 cycle-1 manifest，想再加 5 个手术名。"* → 仅重跑步骤 2a（仅针对新术语的专科访谈）、2b（新术语的句子生成）、2c（新术语的 IPA 流水线）、2d（试听新术语）和 2e（仅合成新术语行）。追加到已有 `manifest.jsonl`。**不要为已有术语重新生成音频**——周期隔离是有意为之，以便排行榜能干净地对比 cycle N 与 cycle N+1。

## 产出的制品

- `term_seed.csv`——带 `entity_category` 的整理术语
- `pronunciation_overrides.csv`——已验证 IPA，**跨周期可追加**
- `manifest.jsonl`——带临床扩展字段的 NeMo 格式（每行一个 JSON 对象）
- `audio/<slug>.wav`——合成的音频片段，manifest 每行一个

## 故障排查

- **TTS 限流丢弃（`RESOURCE_EXHAUSTED`）** 在 >100 行生成时出现 → 在 Magpie NVCF 上属预期。确认 `/read-aloud` 中启用了指数退避；大任务上预期约 5–10% 丢弃，并对缺口重跑。
- **所有 `ipa_source` 行都标记为 `magpie_g2p`** → MW 查询全面失败，或候选 IPA 未通过音素校验。重新验证你配置的 MW 路径（A 用 `DICTIONARY_API_KEY`；B 用 HTTPS 可达性 + 解析器），然后将候选与 Magpie 的 en-US 音素库比对。
- **即使有 IPA override，Magpie 仍读错某术语** → 先验证该 IPA 在 Magpie en-US 音素库中，且 SSML 包装语法有效。若两者都通过，底层 TTS bug 归 `/read-aloud`（`/riva-tts`）所有——路由到那里诊断。本技能提供 override 机制，但不拥有神经 G2P 或 SSML 解析器。
- **来自 `/data-designer` 的句子变体平淡 / 模板化** → 检查简报；仅含 schema 的提示偶尔会产生刻板输出。向简报加入 1–2 个上下文示例并重跑。
- **音频文件存在但 `manifest.jsonl` 偏短** → manifest 写入器跳过了合成返回 NVCF 错误的行。仅用缺失的行重跑构建。

对于本列表之外的任何问题，识别涉及的哪个上游技能并路由过去。`digital-health-clinical-asr-build` 技能拥有方法论，而非 TTS 或 DataDesigner 的内部实现。

## 局限性

- **默认仅英文。** 两级 IPA 流水线对照的是 Magpie 的 en-US 音素库。其它区域需要不同的上游音素集 + override CSV 格式。
- **六个固定实体类别。** 扩展 `entity_category` 是一次有意的方法论变更，而非一次性微调——KER 拆解、排行榜分区和下游微调脚本都依赖该词表。
- **首个周期规模很小。** 低于约 20 个术语时，按 `ipa_source` 拆分的排行榜各桶内行数不足以产生统计意义。即使耗费一次会话，也要构建一个有意义的周期。
- **Magpie NVCF 限流。** 大任务约 5–10% 丢弃；预留一次重跑。

## 后续步骤

- **前向：** `/digital-health-clinical-asr-eval`——转写 manifest，给 WER/CER/KER/SER 打分，产出五段式排行榜。
- **回退到 setup**（若环境中任何东西损坏）：`/digital-health-clinical-asr-setup`。
- **横向**用于 TTS 专项调试：`/read-aloud` 或 `/riva-tts`。

## 参考

- [`references/manifest-schema.md`](references/manifest-schema.md)——NeMo 规范字段 + 临床扩展；预检 schema 与音频存在性检查；跨周期稳定性规则
