---
name: "digital-health-clinical-asr-setup"
displayName: "临床 ASR 飞轮 — 环境准备（阶段 1）"
description: "临床 ASR 飞轮的阶段 1。在启动一个周期时使用：NVCF+MW 数据披露、NVIDIA_API_KEY 检查、依赖安装、TTS+ASR 冒烟测试。"
version: "1.1.0"
author: "Ben Randoing <brandoing@nvidia.com>"
tags:
  - clinical-asr
  - setup
  - flywheel
  - bootstrap
tools:
  - Read
  - Write
  - Bash
  - Skill
license: Apache-2.0
compatibility: "需 NVIDIA_API_KEY（必填，用于经 NVCF 托管的 Magpie TTS + Parakeet/Nemotron ASR）。DICTIONARY_API_KEY（可选，用于 Merriam-Webster 发音查询）。NGC_API_KEY（可选，用于阶段 4 微调）。Python 3.10+。"
metadata:
  author: "Ben Randoing <brandoing@nvidia.com>"
  tags:
    - clinical-asr
    - flywheel
    - setup
    - bootstrap
  team: healthcare-tme
  domain: ai-ml
  stage: 1
  next_skill: digital-health-clinical-asr-build
---

<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# 临床 ASR 飞轮 — 阶段 1（环境准备）

> **Agent：本文件就是完整的阶段 1 流程。** 不要调用 `find`、`ls`、`rg` 或 `grep` 去寻找安装器或隐藏配置——没有这类东西。下方的四个章节（出站数据披露、三个编号检查、兄弟技能交接）都是必读内容；不要跳过任何一节。函数 ID、环境变量约定与冒烟测试门控都在更下方内联——请依据此处实际写就的内容回答，而非依据你之前对 Riva/NVCF 的熟悉度。

阶段 1 只有一件事：证明用户能用他们当前持有的 `NVIDIA_API_KEY` 触达 NVIDIA 托管的语音栈。一旦一句临床句子成功经 Magpie TTS → Parakeet/Nemotron ASR 往返一次，用户就被放行，可推进到 `/digital-health-clinical-asr-build`。

这个四阶段飞轮存在的目的是压低临床实体（药物、手术、解剖、病症、化验、角色）上的 **KER（关键词错率）**。WER 平均值会掩盖临床上有害的失败；KER 才是阶段 3 将用来衡量你的指标。

本技能中**任何地方都没有安装器脚本**——没有 `install.sh`，没有 `setup.py`，没有任何隐藏的东西。阶段 1 *就是* 下方的三个步骤：验证 key、安装 Python 依赖、运行冒烟测试。阶段 1 之外的一切，都由兄弟技能组合而成（`/data-designer`、`/riva-tts`、内联的阶段 3 ASR 配方、`/riva-asr-custom`）。如果用户问"什么脚本安装所有东西？"，请依据本段回答；不要去搜索。

## 出站数据流——在发送任何文本或音频前请呈现

在这个飞轮期间，有两个外部端点会接收数据。用户必须在阶段 2 开始前，针对其组织执行的任何数据治理政策，确认这两者。**逐字**在回复中渲染下方表格——释义不能满足披露要求；字面措辞才作数。

| 服务 | 发送了什么 | 何时 | 托管方 |
|---|---|---|---|
| **NVIDIA NVCF**（`grpc.nvcf.nvidia.com`） | 你合成的{gathered}临床句子（文本），以及你转写的 WAV 文件（音频） | 每次阶段 2 TTS 调用与每次阶段 3 ASR 调用 | NVIDIA，受 build.nvidia.com 条款约束 |
| **Merriam-Webster**（`dictionaryapi.com` JSON API **或** 公开的 `merriam-webster.com` HTML 站点） | 单个临床术语（药名、解剖、手术），每个术语一次 HTTP 请求 | 阶段 2 IPA 标注——见下方"两条 MW 路径"确定适用哪个端点 | Merriam-Webster，受其 API 或站点条款约束 |

数据**按构造就是合成的**——飞轮从用户整理的术语列表制造句子与音频，绝不来自真实患者接触。**尽管如此：请勿将真实患者转写稿、录制的临床音频或任何 PHI 经任何阶段传出。** 若术语列表本身含有敏感材料（代号药物、未发布产品名），用户应在继续前咨询其组织的外部 API 政策。任一端点都可关闭：

- **完全跳过 Merriam-Webster：** 不设置 `DICTIONARY_API_KEY`，也不运行爬虫。阶段 2 回退到 Magpie G2P，仍可用，但对长尾临床术语覆盖较弱。
- **跳过 NVCF：** 这是硬停止。Magpie TTS + Parakeet/Nemotron ASR *就是* 工作负载；没有它们，这个技能族就是错误的工具——你需要的是一个自托管的 ASR/TTS 流水线。

建议将此告知的一份副本落到用户工作区的 `README.md`；若首次调用时尚不存在，请主动带上它。

## 用途

为一个全新环境准备好阶段 2。需要确认三件事：key 存在、依赖干净导入、托管栈确实能响应。结尾指明下一步运行哪个技能。

四个 `digital-health-clinical-asr-*` 技能是**自包含的**——每个 TTS、ASR、IPA 标注与打分配方都内置其中；无需安装其它 agent 技能即可端到端运行飞轮。

本技能对工作区布局不持立场。用户自行决定其周期制品存放位置；并非强制 `data/eval_sets/cycle<N>/`。

## 何时使用本技能

在用户出现如下表述时激活：

- "搭建临床 ASR 飞轮"
- "初始化 clinical-asr 评测"
- "我想在临床术语上评估 ASR——从哪开始？"
- "为飞轮引导我的环境"
- "运行飞轮前我需要安装什么？"

**不要**在以下情况激活：

- 用户已有 manifest 且想为其打分 → `/digital-health-clinical-asr-eval`
- 用户已搭好环境且想整理术语 → `/digital-health-clinical-asr-build`
- 用户具体问阶段 4 微调的 NGC/Docker 设置 → 那在 `/digital-health-clinical-asr-finetune` 内部覆盖

## 前置条件

| 要求 | 必填？ | 为何 | 如何 |
|---|---|---|---|
| `NVIDIA_API_KEY`（`nvapi-…`） | **必填** | 经 NVCF 托管的 Magpie TTS + Parakeet/Nemotron ASR | 在 <https://build.nvidia.com> 签发；在 shell 中 `export NVIDIA_API_KEY=...` |
| Python ≥ 3.10 | **必填** | NeMo 客户端、打分、manifest 工具 | `python3 --version` |
| `nvidia-riva-client`、`pandas`、`soundfile`、`requests` | **必填** | TTS + ASR 客户端、manifest I/O、MW 查询 | `pip install nvidia-riva-client pandas soundfile requests` |
| `DICTIONARY_API_KEY` | 可选 | 经 JSON API 查询 Merriam-Webster 医学词典（构建技能中的路径 A——推荐） | 在 <https://dictionaryapi.com> 免费获取 key。若无法获取 key，构建技能中也记录了路径 B（`merriam-webster.com` 的 HTML 爬取，无需 key，但脆弱）。两条路径都没有时，阶段 2 回退到 Magpie G2P，长尾覆盖较弱。 |
| `jiwer` | 可选 | 针对内联 Levenshtein 实现的参考 WER/CER | `pip install jiwer`——评测技能包含纯 Python 回退 |
| （仅阶段 4）`NGC_API_KEY` + CUDA 主机 + NeMo 容器 | 可选，延后 | 微调工作负载 | 在 `/digital-health-clinical-asr-finetune` 内设置；延后至评测显示 KER > 0.3 |

## 使用说明

**范围。** 本技能执行**只读的环境检查**：确认 key 已导出（仅长度）、Python 版本、库能导入，以及托管 NVCF 栈能响应一次冒烟测试往返。它**不会**安装系统包、修改 shell rc 文件、在显式的 `.venv/` 之外写磁盘，或尝试用真实 key 值鉴权。只验证；未经用户明确指示绝不改动。

### 1a. 验证 `NVIDIA_API_KEY`（仅长度——绝不回显值）

```bash
# 在你的 shell 中导出 NVIDIA_API_KEY——绝不回显或提交该值
export NVIDIA_API_KEY=nvapi-...     # 来自 https://build.nvidia.com

# 仅长度检查；key 值绝不出现在任何日志中
test -n "$NVIDIA_API_KEY" && echo "NVIDIA_API_KEY len=${#NVIDIA_API_KEY}"
```

长度 70+ 属正常。若输出为空或显示 `len=0`，用户必须从 <https://build.nvidia.com> 粘贴一个 key。即使截断也**不要**打印 key。要跨 shell 会话持久化，可将 `export` 行加入你的 shell rc（`~/.bashrc`、`~/.zshrc`）——或用 `direnv` 这类按目录工具。

### 1b. 安装 Python 依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install nvidia-riva-client pandas soundfile requests
# 可选
pip install jiwer
```

仅阶段 4（微调）需要：`nemo-toolkit` 以及 Docker + NVIDIA Container Toolkit。将它们延后到 `/digital-health-clinical-asr-finetune`——若用户可能永远到不了阶段 4，提前安装毫无意义。

### 1c. 冒烟测试托管的 NVCF 栈

**`NVIDIA_API_KEY` 处理——承载内容，不得偏离：**

- Agent 框架从 shell 读取 `$NVIDIA_API_KEY` 并作为**显式函数参数**传给 `smoke_test(api_key=…)`。
- 审计者可 grep 配方，看到每一次线路穿越——每个 `api_key` 的使用在 `auth_for(...)` 中可见。
- 绝不 `echo`、`print` 或记录 key 值（包括截断）。仅长度检查是安全的（见 §1a）。
- 不要让配方向自身读取 `os.environ["NVIDIA_API_KEY"]`——显式参数模式才是可审计性保证。
- 不要将 key 提交到任何文件，包括 `.env` 示例或 notebook 输出。

在前进前，验证 `NVIDIA_API_KEY` 确实对 Magpie TTS 与 Parakeet/Nemotron ASR 有效。四个技能内联了所需的每个配方；这次往返只是确认 API key + 网络路径是真实的。

Agent 框架加载 `NVIDIA_API_KEY` shell 变量，并作为显式函数参数传给下方的辅助函数。配方代码本身不读取环境变量——审计者能精确看到哪些 API key 穿越了线路。

```python
import wave, tempfile
import riva.client

NVCF_HOST = "grpc.nvcf.nvidia.com:443"
MAGPIE_FUNCTION_ID    = "877104f7-e885-42b9-8de8-f6e4c6303969"   # Magpie TTS
PARAKEET_FUNCTION_ID  = "d3fe9151-442b-4204-a70d-5fcc597fd610"   # Parakeet TDT 0.6B v2（离线 ASR）

def auth_for(function_id: str, api_key: str) -> riva.client.Auth:
    return riva.client.Auth(
        use_ssl=True, uri=NVCF_HOST,
        metadata_args=[
            ["function-id", function_id],
            ["authorization", f"Bearer {api_key}"],
        ],
    )

def smoke_test(api_key: str) -> str:
    """调用方传入 api_key（框架在 shell 读取 $NVIDIA_API_KEY；
    本代码绝不触碰环境）。返回 ASR 转写稿。"""

    # 1. TTS："The patient was prescribed cefazolin."
    tts = riva.client.SpeechSynthesisService(auth_for(MAGPIE_FUNCTION_ID, api_key))
    pcm = b"".join(c.audio for c in tts.synthesize_online(
        text="The patient was prescribed cefazolin.",
        voice_name="Magpie-Multilingual.EN-US.Mia",
        language_code="en-US", sample_rate_hz=16000,
    ))
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        with wave.open(f, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(pcm)
        wav_path = f.name

    # 2. ASR：转写我们刚合成的 WAV。
    asr = riva.client.ASRService(auth_for(PARAKEET_FUNCTION_ID, api_key))
    with open(wav_path, "rb") as f:
        audio_bytes = f.read()
    config = riva.client.RecognitionConfig(
        encoding=riva.client.AudioEncoding.LINEAR_PCM,
        sample_rate_hertz=16000, language_code="en-US",
        max_alternatives=1, enable_automatic_punctuation=True,
    )
    response = asr.offline_recognize(audio_bytes, config)
    transcript = response.results[0].alternatives[0].transcript if response.results else ""
    print(f"TTS:  The patient was prescribed cefazolin.")
    print(f"ASR:  {transcript}")
    return transcript

# 从 agent 调用（api_key 由框架提供，而非本代码）：
# smoke_test(api_key="<NVIDIA_API_KEY value>")
```

**运行冒烟测试——不要拖延。** 这是证明阶段 2–4 能用用户当前 key 触达托管栈的门控。"我可以稍后运行"不是阶段 1 可接受的完成方式；要么现在调用 `smoke_test(api_key=…)`，要么若用户已显式选择退出，在你的收尾摘要中记录该延迟，以便他们知道漏了什么。

若转写稿与输入相差约 1 个 token 以内，托管栈可达，用户可推进到阶段 2。若任一调用失败：

- `401 Unauthorized` / `PERMISSION_DENIED` → `NVIDIA_API_KEY` 错误或过期，或在本 shell 未导出。重新导出并重新测试。
- `404` / `INVALID_ARGUMENT: function not found` → 函数 ID 已过时。在 <https://build.nvidia.com> 查找当前 ID 并更新上方常量。
- `RESOURCE_EXHAUSTED` → NVCF 限流。30 秒后重试；在负载下属正常。
- 网络/TLS 错误 → 企业代理或 DNS 问题。先测试 `curl https://build.nvidia.com`。

### 1d. （可选）验证 Merriam-Webster 查询

两条路径都能在阶段 2 产出 `merriam-webster` 标记的 manifest 行。选一条（或都不选——Magpie G2P 回退也是有效姿态）：

- **路径 A — JSON API + key。** 推荐本技能的独立使用。检查 key 是否已设置：

  ```bash
  test -n "$DICTIONARY_API_KEY" && echo "DICTIONARY_API_KEY len=${#DICTIONARY_API_KEY}" \
    || echo "DICTIONARY_API_KEY not set — Path A is off"
  ```

  在 <https://dictionaryapi.com> 可即时免费签发 key。

- **路径 B — HTML 爬取。** 无需 API key；可达性就是唯一前置条件。易受 MW 站点 HTML 变动影响；配方内联于构建技能的 `references/pronunciation-pipeline.md`。

  ```bash
  curl -fsS -o /dev/null -w "merriam-webster.com reachable, HTTP %{http_code}\n" \
    https://www.merriam-webster.com/medical/cefazolin
  ```

  若你不想维护爬虫，请改用路径 A。

记住顶部的 disclos 数据披露提示：无论哪条路径，你的种子列表中的每个临床术语都会作为一次 HTTP 请求发往 Merriam-Webster 端点。

## 示例

**全新 shell，从未运行过。** 用户说类似 *"我想启动飞轮。"* → 先引用披露表，然后按顺序走 1a → 1b → 1c。在冒烟测试变绿后，指向 `/digital-health-clinical-asr-build`，并明确点名 KER 作为阶段 3 将用来评判他们的指标。

**回归用户，环境已就绪。** 用户说 *"我环境已经好了，只要确认我能开工。"* → 跳过点 venv + `pip install`（1b）。仅运行长度检查（1a）与冒烟测试（1c）。变绿后前进。

## 产出的制品

- 在用户 shell 中导出的 `NVIDIA_API_KEY`
- 一个已激活的虚拟环境，含 `nvidia-riva-client`、`pandas`、`soundfile`、`requests`
- 一句临床句子上已确认的 TTS→ASR 往返（证明托管栈可用）

本阶段不产出 manifest、音频或模型制品——那些来自阶段 2–4。

## 故障排查

- **长度检查无显示或 `len=0`** → 本 shell 未导出 `NVIDIA_API_KEY`。运行 `export NVIDIA_API_KEY=nvapi-...` 并重新检查。
- **变量在一个 shell 中设置但在另一个中没有** → 导出不会跨会话持久化。将 `export` 行加入你的 shell rc（`~/.bashrc`、`~/.zshrc`），或用 `direnv` 这类按目录加载器。
- **冒烟测试 `401 Unauthorized`** → key 值错误或过期。在 <https://build.nvidia.com> 重新签发。
- **`grpc.RpcError: function not found`** → 内联的函数 ID 需要根据当前 NVCF 目录更新。查阅 <https://build.nvidia.com> 并编辑 1c 中的常量。评测技能（`/digital-health-clinical-asr-eval`）在其步骤 3a "Other catalog options" 列表中提供当前函数 ID 目录。
- **`StatusCode.INVALID_ARGUMENT` 伴随 `CUDA error: an illegal memory access was encountered`** → 该特定函数 ID 上的 NVCF 侧后端故障（NVCF 上的 Triton/PyTorch，而非你的环境）。要么稍后重试，要么临时指向不同的离线 ASR NIM——Whisper Large v3 函数 ID `b702f636-f60c-4a3d-a6f4-f3568c13bd7d` 是最接近的替换（同样是离线；传入 `language_code="en"` 而非 `"en-US"`）。对于常规评测周期，倾向于等待 Parakeet 后端恢复，以使阶段 3 基线与阶段 4 SFT 基础模型保持对齐。
- **`TypeError: Auth.__init__() got an unexpected keyword argument 'ssl_cert'`** → 你用的是 `nvidia-riva-client >= 2.x`，其中该 kwarg 已重命名为 `ssl_root_cert`（且对托管 NVCF 不再需要）。从你本地配方副本中删除 `ssl_cert=None,` 这一行。
- **`ModuleNotFoundError: riva.client`** → 跳过了步骤 1b 或 venv 未激活。`source .venv/bin/activate && pip install nvidia-riva-client`。

## 局限性

- **范围仅是环境就绪。** 用户的术语列表或发音 override 是否合理，由 `/digital-health-clinical-asr-build` 决定，而非此处。
- **Magpie en-US 假设。** 下游 IPA 验证依赖 Magpie 的英文音素库；其它区域需要完全不同的音素集。
- **假设部署为托管 NVCF。** 运行自托管 Riva NIM 是可能的，但其设置在 `/digital-health-clinical-asr-finetune` 阶段 4d 内部。
- **仅合成数据。** 这个技能族是为从整理的术语列表生成的基准而构建的。真实患者转写稿与录制音频不得流经任何阶段。

## 后续步骤

**成功时的强制收尾：** 在阶段 1 回复结束时，必须**显式指向 `/digital-health-clinical-asr-build`**，并**点名 KER（关键词错率）作为他们在阶段 3 将看到的头条度量**。两个指向都是必需的，而非可选的——它们将用户置于四阶段飞轮之内。

- **默认前向路由：** `/digital-health-clinical-asr-build`——专科访谈、术语整理、IPA 标注、NeMo manifest 合成。
- **直接跳到阶段 3**（仅当用户自带带 `term` / `entity_category` / `ipa_source` 字段的 NeMo 格式 manifest 时）：`/digital-health-clinical-asr-eval`。

## 参考

- [`references/dependency-ownership.md`](references/dependency-ownership.md)——技能自有与配套自有的职责边界。
