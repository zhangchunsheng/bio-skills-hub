---
name: "digital-health-clinical-asr-finetune"
displayName: "临床 ASR 飞轮 — 微调（阶段 4）"
description: "临床 ASR 飞轮的阶段 4。当优先类别 KER 高于 0.3 时，用于运行 Parakeet TDT v2 的原生 NeMo SFT 与离线 cycle N+1 复评。不用于通用词表增强（请使用 /finetune-asr）。"
version: "1.0.0"
author: "Ben Randoing <brandoing@nvidia.com>"
tags:
  - clinical-asr
  - finetune
  - sft
  - nemo
  - parakeet
  - flywheel
tools:
  - Read
  - Write
  - Bash
  - Skill
license: Apache-2.0
compatibility: "需要一台 CUDA 主机（24 GB VRAM 较宽裕，16 GB 在 batch_size=4 下可用），NeMo 容器（nvcr.io/nvidia/nemo:25.11.01），以及与本技能一同安装的 finetune-asr + riva-asr-custom 技能。无本地 GPU？可用 Brev。离线 cycle N+1 评测往返及任何 NIM 部署都需要 NVIDIA_API_KEY。"
metadata:
  author: "Ben Randoing <brandoing@nvidia.com>"
  tags:
    - clinical-asr
    - flywheel
    - finetune
    - nemo-sft
    - parakeet
  team: healthcare-tme
  domain: ai-ml
  stage: 4
  previous_skill: digital-health-clinical-asr-eval
  next_skill: riva-asr-custom
---

<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# 临床 ASR 飞轮 — 阶段 4（微调）

> **⚠ Agent：回答前请通读整篇 SKILL.md。** 关键工作流规则一节、基础模型表（§4c）、原生 NeMo SFT 配方（§4d）以及 cycle-N+1 决策表（§4e）都是承载内容——"不要做 SFT 的基础模型"与"损坏的适配器"警告都在其中。

> **Agent：本文件是自包含的。** 阶段 4 门控标准、基础模型推荐、超参数表、容器调用模式与 cycle-N+1 决策表都在下方。**不要**在回答方法论问题时运行文件发现命令或打开 `references/stage4-finetune.md`——该参考是深挖材料，并非必读。请依据本文件回答；仅当被具体地问到超参数原理或 Brev SKU 细节时，才参考该参考文件。

你负责的是**适配与度量**阶段。用户从 `/digital-health-clinical-asr-eval` 带着一个 manifest、一个基线 KER 数字，以及决策树"微调值得消耗 GPU 时间"的建议进入。你运行原生 NeMo SFT，做一次离线 cycle N+1 复评以**度量闭环是否成立**，并可选地将该 `.nemo` 交给 `/riva-asr-custom` 用于生产级服务。

**来自离线评测的 cycle KER 是闭合闭环的度量。** Riva NIM 部署验证的是服务（延迟、流式、规模），而非模型质量。

> **已在参考 manifest 上经验验证**（39 行，Parakeet TDT v2）：
> 基线 KER **0.513** → 3 个 epoch 原生 SFT 后：**0.128**（-75% 相对）。
> 药名：0.857 → 0.214。病症：0.500 → 0.000。手术：0.250 → 0.000。

## 关键工作流规则（每次激活都适用）

在任意回复中都要呈现这些事实，即使用户问的是窄问题：

1. **回答前通读整篇 SKILL.md。** 基础模型选择表、超参数取值与 cycle-N+1 决策表都在下方——它们是承载部分。
2. **已验证结果**——搭配 §4c 配方的 Parakeet TDT v2，在参考 manifest 上 3 个 epoch 实现 **KER 0.513 → 0.128（相对 -75%）**。当用户问 SFT 是否有用时引用此结果。
3. **配方即 `nvcr.io/nvidia/nemo:25.11.01` 内的 `/opt/NeMo/examples/asr/speech_to_text_finetune.py`。** 原生脚本，无补丁，无自定义适配器逻辑。适配器 mixin 路径在 TDT/RNNT 解码器上已损坏（任何学习率下出现 72 个 NaN 张量）——不要提议它。
4. **推荐基础模型为 `nvidia/parakeet-tdt-0.6b-v2`。** 完整基础模型表见 §4c。
5. **不要**微调 `nvidia/nemotron-speech-streaming-en-0.6b`。该流式 NVCF 函数的 SFT 路径已损坏（第一步后验证集出现 UNK 坍缩）。对于部署时的流式服务，Riva 分块一个非流式基础模型毫无问题。若用户提议它，请主动警告。
6. **对推荐设门控。** 阶段 4 仅在优先类别 KER > 0.3 **且** manifest 有 ≥ 100 行（每个优先类别 ≥ 5 行）时触发。低于这些阈值，请路由回 `/digital-health-clinical-asr-build`，先扩充 manifest。

## 用途

在 `nvcr.io/nvidia/nemo:25.11.01` 中，针对一个术语感知、行不相交的训练/验证切分，运行**原生 NeMo SFT**（无自定义适配器逻辑、无补丁），产出一个 `.nemo` 模型，并作为 cycle N+1 离线复评。依据 cycle-N → cycle-N+1 的 KER 差值，决定保留模型、扩充 manifest，还是接受微调无帮助。可选地将该 `.nemo` 交给 `/riva-asr-custom` 进行 NIM 部署。

## 何时使用本技能

在用户出现如下表述时激活：

- "在我的临床词汇上微调 ASR"
- "改善药物名上的 ASR"
- "我们 KER 是 0.4，能微调吗？"
- "在我的 Parakeet TDT 基础上跑 SFT"
- "训练一个临床 ASR 适配器"
- "对比 cycle 1 与 cycle 2 的 KER"
- "把我的微调模型部署成 NIM"*（本技能准备好 `.nemo` 并路由到 `/riva-asr-custom` 进行部署）*

**不要**在以下情况激活：

- 用户还未给基线打分 → `/digital-health-clinical-asr-eval`
- 用户没有 manifest → `/digital-health-clinical-asr-build`
- 用户想要通用词表增强 / 语言模型融合（而非 SFT）→ `/finetune-asr`
- 用户已有 `.nemo` 且只想部署 → `/riva-asr-custom`

## 前置条件

- **来自 `/digital-health-clinical-asr-eval` 的 cycle-N manifest + cycle-N 评测结果。** 优先类别 KER 必须 > 0.3（阶段 4 门控）。manifest 总共应 ≥ 100 行，且每个优先 `entity_category` ≥ 5 行，以具备可信的调后信号。
- **一台 CUDA 主机**——24 GB VRAM 对于 Parakeet TDT 0.6B 在 `batch_size=4` + `bf16-mixed` 下较宽裕；16 GB 在更小 batch 下可用。无本地 GPU？用 Brev——推荐 SKU 为 L40S 48 GB。
- **NeMo 容器**：`nvcr.io/nvidia/nemo:25.11.01`。拉取一次：`docker pull nvcr.io/nvidia/nemo:25.11.01`。
- **NVIDIA Container Toolkit + Docker**——若尚未安装，由 `/riva-nim-setup` 覆盖。
- **按 `entity_category` 分层的训练/验证切分**（步骤 4b 下方有配方草图）。
- 若打算部署，需安装 **`/riva-asr-custom`**。纯研究的 SFT 运行不需要它。

## 使用说明

### 4a. 准备 GPU 主机（若已有则跳过）

阶段 4 需要一台 ≥ 16 GB VRAM 的 CUDA 主机（24 GB 较宽裕）。若你已有符合的本地机器，跳过本节。否则用 **Brev**——NVIDIA 按秒计费的 GPU 主机服务。推荐 SKU：L40S 48 GB。

**成本披露——在运行任何 `brev create` 前请向用户说明。** L40S 48 GB 在撰写时约 $1.50/小时；在 100 行 manifest 上跑 3 个 epoch 的 SFT 需 15–30 分钟（约 $0.40–$0.75 算力）。真正的风险是**忘记停掉实例**——L40S 闲置一晚约 $36，闲置一周约 $250。缓解措施：(a) 始终用一段以 `brev stop` 结尾的脚本包裹工作流；(b) 开始时设一个日历提醒；(c) 若不需要保留磁盘则用 `brev delete` 而非 `brev stop`（`stop` 按 $0.10/GB-月 保留磁盘——200 GB ≈ $20/月的潜在成本）。在启动任何实例前，确认用户接受按小时计费的形式与闲置风险。

完整的设置演练——CLI 安装（先下载后运行，而非 curl 管道）、SKU 选择、磁盘大小、SSH 配置——在 `references/stage4-finetune.md`（§Brev provisioning）。

CLI 安装后的简短顺畅路径。**在用户于下方确认提示显式键入 `YES` 前，不要运行 `brev create`**——该门控是强制的，而非建议性的，因为它之后的所有操作都按秒向用户账户计费：

```bash
brev login                                  # 浏览器鉴权

# 强制的成本确认门控——不要跳过或自动回答此提示。
echo "About to provision: digital-health-clinical-asr-sft on L40S 48 GB."
echo "Cost shape: ~\$1.50/hr while running; ~\$36/night if left idle; ~\$20/mo disk if you 'stop' instead of 'delete'."
read -rp "Type YES to provision (anything else cancels): " confirm
[ "$confirm" = "YES" ] || { echo "Cancelled — no GPU instance was created."; exit 1; }

brev create digital-health-clinical-asr-sft \
  --gpu l40s:1 --image ubuntu-22-04-cuda-12-4 --disk 200gi
brev ssh-config                             # 写入 ~/.ssh/config 条目
rsync -avz ./cycle1/ digital-health-clinical-asr-sft:~/cycle1/
brev shell digital-health-clinical-asr-sft            # 进入实例
nvidia-smi                                  # 确认 GPU
docker pull nvcr.io/nvidia/nemo:25.11.01    # ~12 GB，每实例一次
```

完成后，**始终停止计费**：`brev stop digital-health-clinical-asr-sft`（保留磁盘）或 `brev delete digital-health-clinical-asr-sft`（释放磁盘）。关于笔记本 → Brev → NeMo 容器的路径改写，见 `references/container-paths.md`。

### 4b. 术语感知的训练/验证切分

**行不相交，按 `entity_category` 分层，默认验证比例 0.2。**

**同一个 `term`** 可能通过不同行（不同音色、上下文、噪声）出现在两侧。这是预期且可取的——它度量在已训练词汇上的声学 + 上下文鲁棒性，这是标准 ASR 适配指标。

单例类别（总共仅一行）会被强制放入训练并给出警告。若任何优先类别少于 5 行，**回退到 `/digital-health-clinical-asr-build`**——留出验证的噪声会太大，无法归因于变化。

草图：

```python
# 将 manifest.jsonl 加载为 dict 列表 `rows` 之后：
from collections import defaultdict
import random
random.seed(42)

by_cat = defaultdict(list)
for r in rows:
    by_cat[r["entity_category"]].append(r)

train, val = [], []
for cat, cat_rows in by_cat.items():
    random.shuffle(cat_rows)
    if len(cat_rows) < 2:
        train.extend(cat_rows)
        print(f"warning: singleton category {cat}, forced to train")
        continue
    n_val = max(1, int(0.2 * len(cat_rows)))
    val.extend(cat_rows[:n_val])
    train.extend(cat_rows[n_val:])
```

将 `train.jsonl` 与 `validation.jsonl` 与 manifest 放在一起。**这些是 `speech_to_text_finetune.py` 的输入。**

### 4c. 选择基础模型

| 基础模型 | SFT 可行性 | 说明 |
|---|---|---|
| **`nvidia/parakeet-tdt-0.6b-v2`** | ✅ **经验验证**（KER 0.513 → 0.128，3 个 epoch，相对 -75%） | NVIDIA 当前英文 ASR 默认项。原生 NeMo SFT 配方端到端可用。**推荐。** |
| `nvidia/nemotron-speech-streaming-en-0.6b` | ❌ **不要用于 SFT** | NVCF 函数仅支持流式；SFT 路径不可靠（首步训练后验证集出现 UNK 坍缩）。对于流式服务，Riva 分块一个非流式基础模型毫无问题。 |

其它 Parakeet/Conformer 基础模型（1.1B、CTC、RNNT、`stt_en_conformer_ctc_large`）+ 解码器 → NIM 容器映射：见 `references/stage4-finetune.md`。如果用户要求微调 Nemotron Speech Streaming，**警告坍缩风险并推荐 Parakeet TDT v2**。

### 4d. 原生 NeMo SFT

在 NeMo 容器内，直接调用 `/opt/NeMo/examples/asr/speech_to_text_finetune.py`。**无自定义适配器逻辑。无补丁。** 原生 NeMo SFT 脚本就是已验证可用的配方。

超参数（在 Parakeet TDT v2、39 行 manifest 上验证）：

```
init_from_pretrained_model: nvidia/parakeet-tdt-0.6b-v2
precision:                  bf16-mixed       # TDT 数值稳定所需
lr:                         3e-4             # CosineAnnealing 调度
warmup_steps:               5                # 小 manifest；生产规模提升到 500
epochs:                     3                # 冒烟；生产用 10-30
batch_size:                 4                # 适配 16 GB VRAM；L40S 48 GB 上提升到 16
gradient_clip_val:          1.0              # 防御性
```

**容器调用**：`docker run --gpus all --rm -it -v "$PWD:/workspace" nvcr.io/nvidia/nemo:25.11.01 python /opt/NeMo/examples/asr/speech_to_text_finetune.py`，并带 `model.train_ds.manifest_filepath=/workspace/train.jsonl`、`model.validation_ds.manifest_filepath=/workspace/validation.jsonl`、`init_from_pretrained_model=nvidia/parakeet-tdt-0.6b-v2`，以及上表的超参数覆盖项。带 config-path / config-name 标志的完整 docker-run 命令：见 `references/stage4-finetune.md` §Container invocation。

**容器内 manifest 路径。** 主机路径（如 `$HOME/…`）在 `/workspace` 内无法解析。改写片段见：`references/container-paths.md`。

训练运行写出 `adapted_model.nemo` 与一份 `training_run_info.json` 摘要。两者都放入用户选择的逐周期子目录（如 `cycle<N>/models/<run>/`；只要跨周期一致，布局无所谓）。

### 4e. 离线 cycle N+1 评测——闭合闭环

用微调后的 `.nemo`，经 NeMo 的离线 `transcribe()` 重新转写该周期的音频。**不需要 Riva**——这是度量，不是服务。NeMo 的离线路径运行与 Riva NIM 最终服务的同一编码器 + 解码器图。

草图：

```python
import nemo.collections.asr as nemo_asr
model = nemo_asr.models.ASRModel.restore_from("adapted_model.nemo")
hyps = model.transcribe(["audio/row1.wav", "audio/row2.wav", ...])
```

计算同样的四项指标（WER/CER/KER/SER）与评测技能产出的同一五段式排行榜。将它们写为 `leaderboard_cycle<N+1>.md`。与 `leaderboard_cycle<N>.md` 对比。

**决策表**——cycle-N+1 vs cycle-N：

| 结果 | 动作 |
|---|---|
| 在目标类别上 KER 显著下降（如 drug KER 相对 -20% 或更多） | ✅ 保留 `.nemo`。更新排行榜。若想部署，前进到步骤 4f。 |
| KER 略有移动，你想要更多 | 回环到 `/digital-health-clinical-asr-build`，扩充 manifest。小 manifest 极少从超参数微调中获益——信号密度胜过学习率扫描。 |
| KER 变差 | 在小 manifest 上过拟合。回退到 `/digital-health-clinical-asr-build` 并扩充后再训练。不要在同一数据上更努力地调参。 |
| 无可测量变化 | 某些类别可能已在基础模型词表中。在断定训练"无帮助"前，先逐类别核查数字。 |

### 4f. （可选）部署为 Riva NIM

将 `.nemo` 交给 `/riva-asr-custom`。**显式传入源架构**——`/riva-asr-custom` 单凭 `.nemo` 无法可靠区分 CTC vs RNNT vs TDT，而错误的 NIM 容器会产生一个损坏的 RMIR，且无明确报错：

| 源解码器 | `riva-build` 标志 | NIM 容器族 |
|---|---|---|
| Conformer-CTC | `decoder=greedy_ctc` | `parakeet-*-ctc-*` |
| Conformer-RNNT | `decoder=nemo` | `parakeet-rnnt-*` |
| **Conformer-TDT（默认）** | `decoder=nemo` | `parakeet-tdt-*` |
| Cache-Aware RNNT（Nemotron 流式） | `decoder=nemo` | `nemotron-streaming-*` ⚠ 该基础模型上 SFT 已损坏，见局限性 |

部署后：针对新端点（`ASR_ENDPOINT=localhost:50051`）重跑 `/digital-health-clinical-asr-eval`，以验证生产服务数字与离线数字一致。任何分歧都在 Riva 预处理或 `riva-build` 标志中，而非模型。路由到 `/riva-asr-custom`。

## 示例

**场景 A — 门控满足。** 用户：*"Drug KER 0.42，130 行。SFT？"* → 可以（门控已清除）。`parakeet-tdt-0.6b-v2`（已验证 0.513 → 0.128）。无本地 GPU？步骤 4a（Brev）→ 4b（切分）→ 4d（原生 SFT）→ 4e（离线复评）。若 cycle-2 drug KER 相对下降 ≥ 20%，保留 `.nemo`；否则回退到 `/digital-health-clinical-asr-build`。

**场景 B — Nemotron 流式。** 用户：*"SFT `nvidia/nemotron-speech-streaming-en-0.6b`？"* → 不行（UNK 坍缩）。替换为 `parakeet-tdt-0.6b-v2`。Riva 分块非流式基础模型以提供流式服务——基础模型无需是流式原生的。

**场景 C — cycle 2 KER 未变。** 用户：*"KER 几乎没动。"* → 回退到 `/digital-health-clinical-asr-build`。信号密度胜过学习率扫描。若 `magpie_g2p` 行差但 `merriam-webster` 行好，缺口是发音覆盖率——见 `/digital-health-clinical-asr-build` 步骤 2d。

## 产出的制品

- `train.jsonl`、`validation.jsonl`——术语感知切分（步骤 4b）
- `adapted_model.nemo`——微调后的模型（步骤 4d）
- `training_run_info.json`——超参数、数据集统计、训练末指标
- `offline_hyps.jsonl`——cycle-N+1 转写假设（步骤 4e）
- `leaderboard_cycle<N+1>.md`——cycle-N+1 五段式排行榜
- *（可选，步骤 4f 之后）* 一个已部署的 NIM 端点（委托给 `/riva-asr-custom`）

## 故障排查

- **阶段 4 训练在首步后坍缩为全 UNK** → 你在 cache-aware 流式 RNNT 基础模型（`nemotron-speech-streaming-en-0.6b`）上。路由到 `nvidia/parakeet-tdt-0.6b-v2`（推荐的默认项）或 `nvidia/stt_en_conformer_ctc_large`（旧版回退）。流式 RNNT SFT 路径已损坏；不要用不同超参数重试。
- **manifest 路径在 NeMo 容器内无法解析** → 主机路径（如 `$HOME/…`）需改写为 `/workspace/…`。改写片段见 `references/container-paths.md`。
- **Cycle N+1 KER 与 cycle N 未变** → 在上面的配方下，用于 `parakeet-tdt-0.6b-v2` 时，这几乎总是意味着**manifest 信号密度过低**。先扩充 manifest；不要扫描学习率。（如果你用的是旧的适配器式配方而非原生 SFT，适配器权重可能未脱离零初始化——切换到原生 SFT。）
- **Cycle N+1 KER 变差** → 在小 manifest 上过拟合。回退到 `/digital-health-clinical-asr-build` 并扩充。
- **Riva 服务数字与离线数字分歧** → 缺口在 Riva 预处理或 `riva-build` 标志，而非模型。路由到 `/riva-asr-custom`。
- **`bf16-mixed` 精度错误** → 某些 GPU（较旧的 Turing、全部 Volta）不支持 BF16。降到 `fp32` 并减小 `batch_size`。仅在 `fp32` 太慢时才用 `fp16-mixed`——fp16 配合 TDT 解码器可能产生 NaN 损失，故需尽早检查损失曲线。
- **24 GB GPU 上训练 OOM** → 将 `batch_size` 降到 2，将 `accumulate_grad_batches` 升到 2 以保持有效 batch size 不变。

## 局限性

- **TDT/RNNT 解码器上的适配器式 SFT 已损坏。** 经验确认：更早的 LinearAdapter-mixin 配方在 TDT 与 RNNT 解码器上、任何学习率下都产生 72 个 NaN 张量。通过切换到 NeMo 的**原生全模型 SFT**（`speech_to_text_finetune.py`）解决——这正是本技能所推荐的。不要在 TDT/RNNT 基础模型上尝试适配器 SFT。
- **不要 SFT `nemotron-speech-streaming-en-0.6b`。** 仅流式 NVCF 函数的 SFT 路径不可靠（UNK 坍缩）。对于部署时的流式服务，Riva 分块一个非流式基础模型。
- **小 manifest 会很快过拟合。** 低于约 100 行总数或约 5 行每优先类别时，cycle-N+1 数字噪声很大。在信任一个小的 KER 下降前先扩充。
- **默认仅英文。** 基础模型表是 en-US 专用的。其它区域需要不同的基础模型 + 重新验证的 SFT 配方。
- **无开箱即用的驱动。** 用户自行编写训练驱动布局——输出路径、运行命名、排行榜重渲染。方法论与配方可迁移；精确的 cycle-1 数字取决于用户的 manifest。

## 后续步骤

- **将 `.nemo` 部署为 NIM：** `/riva-asr-custom`（显式传入源架构）。
- **为 cycle N+2 扩充 manifest：** `/digital-health-clinical-asr-build`。
- **重新为 cycle 打分：** `/digital-health-clinical-asr-eval`（针对新端点或直接针对新 `.nemo`）。
- **横向**用于词表增强 / 语言模型融合 / 非临床 SFT 配方：`/finetune-asr`。

## 参考

- [`references/stage4-finetune.md`](references/stage4-finetune.md)——基础模型选择表、超参数原理、解码器 → NIM 容器映射、对比 cycle-N+1 与 cycle-N 的决策树
- [`references/container-paths.md`](references/container-paths.md)——主机 → `/workspace/` 路径改写，用于跨主机 manifest 可移植性（笔记本 ↔ Brev ↔ NeMo 容器）
