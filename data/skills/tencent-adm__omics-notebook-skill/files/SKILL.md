---
name: omics-notebook-skill
description: 腾讯健康组学平台（Tencent Genomics）Notebook 实例管理技能。基于 omics-platform-cli 完成：登录与配置、在当前环境下创建 Notebook 实例、列出实例。触发场景：用户需要在组学平台上创建/列出 Notebook 实例、管理 Jupyter 实例。触发词：Omics, omics, 组学平台, 健康组学, 腾讯健康组学, omics cli, omics-platform-cli, notebook, Notebook, 创建 notebook, 新建实例, 列 notebook, 列实例, jupyter, Jupyter 实例。
---

# Omics Notebook Skill (v6)

> 通过 `omics-platform-cli` 管理腾讯健康组学平台（genomics.qq.com）的 Notebook 实例。
> 所有命令拼接走 `scripts/omics_cli.py`，统一参数与输出格式。
> **SKILL 的能力范围严格等于 CLI 4 条白名单命令；任何越界都视为越权。**

---

## 能力边界（不可违反 · 最高优先级）

本 SKILL 只能调用以下 **4 条** CLI 一级命令：

```
login   whoami   config   notebook
```

其中 `notebook` 共有 4 个子命令：`create` / `list` / `start` / `stop`。

### 🚫 严令禁止

1. **严禁编造其他命令**——例如 `run` / `list`（顶层）/ `status` / `debug` / `app *` / `project *` / `import` 等都不存在，调用必失败。
2. **严禁直接调用 omics 后端 HTTP API**（CreateNotebook / DescribeEnvironments 等）、SQL、文件系统写入等任何旁路通道。
3. **严禁通过组合现有命令"模拟"出白名单外的语义**。
4. **严禁替用户猜/编造** `--cos-mounts` 的 Bucket、`--volume-mounts` 的 VolumeId、`--name` 等归属用户治理空间的字段。

### ✅ notebook create 前置确认（必经）

SKILL 触发 `omics notebook create ...`（写操作）前必须：

1. 拼出完整命令字符串（含所有 flag）
2. 输出参数摘要表（名称 / 镜像 / 工作目录 / 资源规格 / COS 挂载等关键项）
3. 询问用户："以上命令是否执行？(y / 确认 / 继续)"
4. 仅当收到明确肯定答复（y / yes / 确认 / 继续 / 是 / 执行 / OK）才调用
5. 用户拒绝（n / no / 取消）→ 终止；模糊回复（嗯 / 好 / 可以）→ 再次明确询问
6. 用户追加修改 → 回到 1 重拼

### ✅ 各命令的确认要求

| 命令 | 是否需要确认 |
| --- | --- |
| `whoami` / `config show` / `config clear` / `notebook list` | 免确认（只读 / 本地操作） |
| `notebook start` / `notebook stop` | 免确认（启停有天然安全边界，需指定 NotebookId） |
| `notebook create` | **必须**（写操作） |
| `login` | 主动触发（Step 1），自动打开浏览器授权；无需额外确认 |
| `config set` | Step 2 中通过 AskUserQuestion 收集参数后执行（非交互式四参数模式） |

---

## 退出码 & 鉴权失败处理

| 退出码 | 含义 | SKILL 处理 |
| --- | --- | --- |
| `0` | 成功 | 解析 stdout |
| `1` | 业务错误 | 把 stderr 转述给用户。如果是"未配置"错误，按下文 Step 2 通过 AskUserQuestion 交互式引导完成配置 |
| `2` | 鉴权失败 | 按下文 Step 1，SKILL 主动触发 `omics login`，不要循环重试 |

stderr 中以 `❌` 开头的行为可读错误描述，可直接转述。

> 另外：`scripts/omics_cli.py` 启动时若在 `PATH` 与 `OMICS_CLI_PATH` 都找不到 `omics` 可执行文件，
> 会以退出码 2 报错（含下载页链接），SKILL 必须按下文 **Step −1** 引导用户安装 CLI，
> 提供官网链接 https://cnb.cool/tencenthealthcareomics/omics-platform-cli，**不要**自动尝试下载或安装。

---

## Step −1：CLI 存在性检查（**最先执行**）

> 任何业务命令之前执行。

```bash
python3 scripts/omics_cli.py version
```

| 结果 | 行动 |
|------|------|
| exit 0，打印版本号 | CLI 已安装，进入 Step 0 |
| `FileNotFoundError` / `command not found` | 给出安装链接，等待用户安装（见下） |
| exit 非 0，其他错误 | 提示安装可能损坏，给出安装链接，建议重装 |

**CLI 未安装时**，给出以下提示，等待用户回复「已安装」：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检测到本机尚未安装 omics-platform-cli，无法继续。

请前往官网，按页面 README 中的安装指引完成安装：
👉 https://cnb.cool/tencenthealthcareomics/omics-platform-cli

完成后，请回复「已安装」，我将继续引导您登录和配置。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

用户回复「已安装」后，重新运行 `python3 scripts/omics_cli.py version` 验证，通过后继续 Step 0。

---

## Step 0：鉴权与配置双重检查（每次启动必做）

两步顺序不可颠倒。

### Step 0.1 — 鉴权预检

```bash
python3 scripts/omics_cli.py whoami
```

| 退出码 | 行动 |
|--------|------|
| `0` | 解析用户类型（B端/C端）→ 继续 Step 0.2 |
| `2` | 跳到 Step 1（登录） |

**用户类型识别**（exit 0 后）：

| 类型 | 识别条件 | 后续流程 |
|------|---------|---------|
| 🔵 C端体验用户 | `Role == "trial_user"` 且 `Capabilities` 含 `"misc:trial"` | Step 0.2 → Step 2-C（简化配置） |
| 🟢 B端正式用户 | 其他情况 | Step 0.2 → Step 2-B（完整引导配置） |

### Step 0.2 — 配置完整性检查

```bash
python3 scripts/omics_cli.py config show -o json
```

| 结果 | 行动 |
|------|------|
| exit 0 + 四字段非空（Region / ProjectId / EnvironmentId / CosBucketName） | 配置就绪，复述给用户，进入业务流程 |
| exit 1 或任一字段为空 | 跳到 Step 2（配置引导） |

配置就绪时复述：

```
✅ 当前配置：
   地域：{Region}
   项目：{ProjectName}（{ProjectId}）
   环境：{EnvironmentName}（{EnvironmentId}）
   COS 桶：{CosBucketName}
```

---

## Step 1：登录授权

**SKILL 主动触发**（不是引导用户手动执行）：

```bash
python3 scripts/omics_cli.py login
```

CLI 在本机启动 `localhost:18000` 监听，**自动打开浏览器**到 OAuth 授权确认页。

提示用户：
```
🔐 已为您打开浏览器登录授权页，请在浏览器中点击「确认授权」完成登录。
   授权完成后系统将自动继续。（等待中...最长 120 秒）
```

登录后轮询验证（最多 3 次，间隔 2s）：
- 成功（exit 0）→ 解析用户类型 → 继续 Step 0.2（配置检查）
- 仍失败（exit 2）→ 提示：「授权似乎未完成，请确认浏览器中已点击「确认授权」。如需重新发起授权，请回复「重试」。」

> ⚠️ `omics login` 仅适用于用户本机有浏览器的场景（OAuth 回调落在 `localhost:18000`）。纯远程无桌面环境不适用，遇此情况告知用户。

---

## Step 2：配置引导

### 🟢 B端正式用户（Step 2-B）

SKILL 通过 `AskUserQuestion` 交互式选项卡引导，**禁止让用户在终端手动输入编号或命令**。

**Step 2-B-1：选择地域**

```bash
python3 scripts/omics_cli.py list region -o json
```

解析结果 → `AskUserQuestion`：`question: "请选择要使用的地域"` · `header: "地域选择"`

→ 记录 `<selectedRegion>`

**Step 2-B-2：并行查询项目和环境，先展示项目选择**

```bash
python3 scripts/omics_cli.py list project -o json         # 并行
python3 scripts/omics_cli.py list env --region <selectedRegion> -o json  # 并行
```

过滤 `Region == selectedRegion` 的项目 → `AskUserQuestion`

若无项目 → 提示并等待用户就绪：
```
⚠️ 账号下无可用项目，请先前往组学平台创建：
👉 https://omics.qq.com/platform/project/list
完成后回复「已就绪」。
```

→ 记录 `<selectedProjectId>`、`<selectedProjectName>`

**Step 2-B-3：展示环境选择**

复用 Step 2-B-2 缓存的 `list env` 结果，过滤 `Available=true` → `AskUserQuestion`

若无可用环境 → 提示：
```
⚠️ 无可用环境，请先前往控制台创建：
👉 https://console.cloud.tencent.com/omics/env/env-list
完成后回复「已就绪」。
```

→ 记录 `<selectedEnvId>`、`<selectedEnvName>`

**Step 2-B-4：临时写入 config（后台静默）**

```bash
python3 scripts/omics_cli.py config set \
  -r <selectedRegion> -p <selectedProjectId> \
  -e <selectedEnvId> -b PLACEHOLDER
```

**Step 2-B-5：选择 COS 存储桶**

```bash
python3 scripts/omics_cli.py list cos-bucket -o json
```

过滤 `Associated=true` → `AskUserQuestion`

若无可用桶 → 提示：
```
⚠️ 选定环境（{selectedEnvName}）未绑定 COS 桶，请先绑定：
👉 https://console.cloud.tencent.com/omics/env/env-list
完成后回复「已绑定」。
```

→ 记录 `<selectedBucket>`

**Step 2-B-6：正式写入配置**

```bash
python3 scripts/omics_cli.py config set \
  -r <selectedRegion> \
  -p <selectedProjectId> \
  -e <selectedEnvId> \
  -b <selectedBucket>
```

输出确认摘要：
```
✅ 配置已完成：
   地域：{selectedRegion}
   项目：{selectedProjectName}（{selectedProjectId}）
   环境：{selectedEnvName}（{selectedEnvId}）
   COS 桶：{selectedBucket}
```

---

### 🔵 C端体验用户（Step 2-C）

全程无需用户选择，SKILL 静默完成配置：

```bash
# 查询项目（取第一条）
python3 scripts/omics_cli.py list project -o json

# 若列表为空，停止并提示：
# ⚠️ 账号下暂无可用项目，请联系 omics@tencent.com

# 写入固定配置
python3 scripts/omics_cli.py config set \
  -r ap-guangzhou \
  -p <firstProjectId> \
  -e env-b65ys9kj \
  -b trial-user-1323714374

# 验证（config show 四字段均非空才通过）
python3 scripts/omics_cli.py config show -o json
```

验证通过后输出：
```
✅ 配置已就绪，您可以开始使用了！
   地域：ap-guangzhou（广州）
   项目：{selectedProjectName}
   运行环境：共享计算资源池（env-b65ys9kj）
   存储桶：trial-user-1323714374
```

验证失败时立即停止：
```
❌ 配置验证失败，无法继续使用。
请联系我们获取帮助：📧 omics@tencent.com
```

<!-- 流程来源：omics-common-app-skill/references/omics-cli-setup.md v1.2 §Step-1 / §A / §B / §C / §D -->

---

## 命令意图映射表

| 用户说 | CLI 命令 | 场景 |
| --- | --- | --- |
| 「我没装 CLI / 提示 command not found」 | SKILL 进入 Step −1，提供官网链接 https://cnb.cool/tencenthealthcareomics/omics-platform-cli，等待用户安装后验证 | Step −1 |
| 「我登录了吗 / 当前账号是谁」 | `omics whoami` | Step 0.1 |
| 「我没登录 / session 过期了」 | SKILL 主动调用 `omics login`，自动打开浏览器授权页 | Step 1 |
| 「现在用的是哪个环境和项目」 | `omics config show -o json` | Step 0.2 |
| 「配下默认项目 / 切到 xx 环境」 | SKILL 通过 `AskUserQuestion` 交互式引导完成（B端），或静默写入（C端） | Step 2 |
| 「清掉本地配置」 | `omics config clear` | — |
| 「创建一个 Notebook / 新建实例」 | `omics notebook create ...`（**必须先二次确认**） | §1 |
| 「我有哪些 Notebook 实例 / 列一下实例」 | `omics notebook list -o json` | §2 |
| 「启动 nb-xxxx / 把这个 notebook 开起来」 | `omics notebook start --id <NotebookId>` | §3 |
| 「停止 nb-xxxx / 关掉这个 notebook」 | `omics notebook stop --id <NotebookId>` | §3 |
| 「把实例上的文件下载/获取到本地」 | `python3 scripts/remote_get.py <notebook_id> [本地路径]` | §4 |
| 「在实例上执行代码 / 跑一下这个 notebook」 | `python3 scripts/remote_exec.py <notebook_id> <本地.ipynb>` | §5 |

---

## 功能一：创建 Notebook 实例（`omics notebook create`）

在当前 config 环境下创建一个 Notebook 实例。**写操作，必须先二次确认。**

SKILL 通过**逐步交互式收集**用户所有参数。首先询问用户：

> ① **快速启动**（使用 Python 镜像，1 核 1G，名称/notebook 文件名自动生成时间戳）
> ② **自定义配置**（逐步选择所有参数）

---

### 1.1 整体交互流程

```
Step 1.1.1  第一轮提问：快速启动 还是 自定义配置？
      │
      ├─ 快速启动 ─────────────────────────────────────┐
      │   直接使用预设入参（Python / 1核1G / 时间戳名）    │
      │   跳到 Step 1.1.3（COS 挂载）→ 跳过缓存卷         │
      │   跳到 Step 1.1.5（二次确认）                     │
      │                                                 │
      └─ 自定义配置 ───────────────────────────────────┐│
          Step 1.1.2  基础参数（名称、描述、镜像、       ││
                       notebook 文件名、CPU/GPU、       ││
                       存储、自动关闭）                  ││
                │                                       ││
                ▼                                       ││
          Step 1.1.3  资源参数（CPU 核数/内存 或 GPU）   ││
                │                                       ││
                ▼                                       ││
          Step 1.1.4  COS 挂载 → work_dir + cos_mounts  ││
                │                                       ││
                ▼                                       ││
          Step 1.1.5  缓存卷列表 → volume_mounts        ││
                │                                       ││
                ▼                                       ││
          Step 1.1.6  汇总 → 二次确认                    ││
                │                                       ││
                ▼                                       ◄┘
          python3 scripts/omics_cli.py notebook create ...
```

---

### 1.2 快速启动模式

用户选择"快速启动"后，直接使用以下预设入参，无需逐项询问：

| 参数 | 预设值 |
| --- | --- |
| `--name` | `notebook-cli` |
| `--image` | Python（`jupyter-base-notebook:2025-12-08`） |
| `--notebook-file` | `notebook-cli-{时间戳}`（如 `notebook-cli-20260724-143052`） |
| `--cpu` / `--memory` | CPU 模式，1 核 / 1 GiB（不询问 GPU） |
| `--description` | 空 |
| `--boot-disk` | 默认 20 GiB |
| `--auto-close` / `--auto-close-min` | 默认 true / 2880 |
| `--cos-mounts` | 空（仅用户新增时才传） |
| `--volume-mounts` | 跳过（不调用 `volume list`，不询问缓存卷） |

> 时间戳格式：`YYYYMMDD-HHmmss`（当前本地时间）。

使用预设值后，直接进入 §1.5（COS 挂载 → work_dir），然后跳过 §1.6（缓存卷），进入 §1.7（二次确认）。
二次确认模板同 §1.7（汇总时注明"快速启动"）。

---

### 1.3 自定义配置 — Step 1.1.2：基础参数

向用户一次性列出以下选项，让用户逐项答复（可一次回复多项）：

| # | 参数 | 说明 | 默认值 |
| --- | --- | --- | --- |
| ① | `--name` | Notebook 名称（≤20 字符，中英文/数字/`_`/`-`/`/`，不含 `//`） | 无（必填） |
| ② | `--description` | 描述（≤100 字符） | 无 |
| ③ | `--image` | 二选一：**Python** 或 **R** | 无（必填） |
| ④ | `--notebook-file` | Notebook 文件名（不含 `.ipynb` 扩展名） | 在 §1.5 (d) 确定 |
| ⑤ | 计算模式 | **CPU** 或 **GPU** | 无（必填） |
| ⑥ | `--boot-disk` | 存储 GiB（最小 20） | 20 |
| ⑦ | `--auto-close` | 是否开启自动关闭 | 是 |
| ⑧ | `--auto-close-min` | 自动关闭分钟数（60~43200） | 2880 |

**镜像说明**（③ 二选一）：

- **Python** → `ccr.ccs.tencentyun.com/omics-public/jupyter-base-notebook:2025-12-08`（Jupyterlab 4.0.0 + Python 3.10）
- **R** → `ccr.ccs.tencentyun.com/omics-public/jupyter-r-notebook:2026-03-03`（Jupyterlab 4.0.7 + R 4.5.2）

> ⑥⑦⑧ 有默认值，用户不回复则直接用默认值。其余为必填。

---

### 1.4 自定义配置 — Step 1.1.3：资源参数（按 CPU / GPU 分叉）

#### CPU 模式

**先问 CPU 核数**：可选值 `1 / 2 / 4 / 8 / 12 / 16 / 32 / 64`（默认 1）。

用户选定核数后，**按以下规格表列出该核数对应的可选内存值**，让用户从其中选一个。不要列出整张表，只列出该核数对应的那行：

| CPU 核数 | 可选内存（GiB） |
| --- | --- |
| 1 | 1, 2, 3, 4, 5, 6, 7, 8 |
| 2 | 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 4 | 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32 |
| 8 | 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32 |
| 12 | 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48 |
| 16 | 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64 |
| 32 | 64, 128, 256 |
| 64 | 128, 192, 256, 512 |

> **关键规则**：用户选的内存值必须在其所选 CPU 核数对应的可选列表中。如果用户输入了不合法的值，提示"`{cpu}核` 对应的可选内存值为 `{...}`"，让其重选。

**完成后得到 `--cpu` 和 `--memory`。**

#### GPU 模式

**先问 GPU 型号**：`T4` 或 `V100`。

用户选定型号后，**列出该型号的可选规格**（从下表中只选匹配该型号的行），让用户选一条（例如："T4 × 1 卡 (8 核 / 32 GiB)"）：

**NVIDIA T4**：

| GPU | cpuCount | memory(GiB) |
| --- | --- | --- |
| T4 × 1 | 8 | 32 |
| T4 × 1 | 20 | 80 |
| T4 × 1 | 32 | 128 |
| T4 × 2 | 40 | 160 |
| T4 × 4 | 80 | 320 |

**NVIDIA V100**：

| GPU | cpuCount | memory(GiB) |
| --- | --- | --- |
| V100 × 1 | 8 | 40 |
| V100 × 2 | 18 | 80 |
| V100 × 4 | 36 | 160 |
| V100 × 8 | 72 | 320 |

> **关键规则**：GPU 模式下 CPU 和内存由规格自动确定，**不要**再单独传 `--cpu` / `--memory`，只传 `--gpu-type` 和 `--gpu-count`。

**完成后得到 `--gpu-type`、`--gpu-count`以及对应的 CPU/内存（仅用于向用户展示）。**

---

### 1.5 自定义配置 — Step 1.1.4：COS 挂载 → work_dir + cos_mounts

> **快速启动模式也会进入此步骤**（共享 COS 挂载流程）。

#### (a) 拉取当前环境的 COS 挂载列表

```bash
python3 scripts/omics_cli.py cos list-mount -o json
```

将返回的挂载列表呈现给用户（表格形式，列为 # / Bucket / SubPath / MountPath / ReadOnly）。这些是环境已有的挂载点，**不需要**作为 `--cos-mounts` 传入（API 端已知）。

> 如果列表为空，提示用户"当前环境尚无 COS 挂载点"，直接进入 (b) 让用户手动新增。

#### (b) 确认是否要新增 COS 挂载

- **列表非空时**：`当前环境已有 N 个 COS 挂载点。是否需要新增？（y/N）`→ 不需要则跳过；需要则按表格格式告知新增信息（Bucket / SubPath / MountPath / ReadOnly），可追加多条。

- **列表为空时**：`当前环境尚无 COS 挂载点，请手动提供至少一条，格式：Bucket / SubPath / MountPath / ReadOnly。`

> **关键规则**：只有用户新增的挂载点才通过 `--cos-mounts` 参数传入。环境中已有的挂载点无需传。

最终：

- `cos_mounts` = 用户新增项组成的 JSON 数组（未新增则为空或不传）
- 候选列表 = 已有列表 + 新增项（至少 1 条），用于下一步选 work_dir

#### (c) 从候选列表中选一个作为 work_dir

> 请从下列挂载列表中选一个作为工作目录 work_dir（输入 #）：

用户选择后按以下规则确定：

- `work_dir` = `cos://{选中行的 Bucket}{选中行的 SubPath}`（SubPath 为空则只取 `cos://{Bucket}/`，不为空则 `cos://{Bucket}{SubPath}`）

#### (d) 列出 work_dir 下已有 .ipynb → 询问是否复用

确定 work_dir 后，用选中行的 Bucket / SubPath 调用 `list-ipynb`，列出该目录下已有的 .ipynb 文件：

```bash
python3 scripts/omics_cli.py notebook list-ipynb --bucket <选中行 Bucket> --prefix <选中行 SubPath 去掉前导斜杠> -o json
```

> 说明：`--prefix` 取选中行的 SubPath 并去掉前导 `/`（SubPath 为空则传空前缀 / 桶根目录）。

然后按结果处理，确定 `--notebook-file`：

- **列表非空**：以表格（列为 # / 文件名）呈现，并询问：
  > 该目录下已有 N 个 .ipynb 文件。是否使用其中某个现存文件？（输入 # 选择；回复 `N`/`否` 表示新建）
  >
  > - 用户选了某个 # → `notebook_file` = 该文件名**去掉 `.ipynb` 扩展名**，直接采用，不再询问文件名；
  > - 用户回复新建 → 询问用户输入新的 `notebook_file`（不含 `.ipynb` 扩展名）。
- **列表为空**：不列表也不问「是否复用」，直接询问用户输入新的 `notebook_file`（不含 `.ipynb` 扩展名）。

> **关键规则**：复用现存文件时，`--notebook-file` 传的是**不含 `.ipynb` 扩展名**的文件名，且必须是列表中真实存在的文件，不要替用户编造。

### 1.6 自定义配置 — Step 1.1.5：获取缓存卷列表 → 确定 volume_mounts

执行：

```bash
python3 scripts/omics_cli.py volume list -o json
```

将返回的缓存卷列表呈现给用户（表格形式，列为 # / VolumeId / Name / Status / MountPath），然后询问：

> 当前环境有 N 个缓存卷。是否要挂载缓存卷？（y/N）
>
> - 不需要 → `--volume-mounts` 留空（CLI 默认 `[]`）
> - 需要 → 请告诉我你想挂载哪些（按表格中的 # 选择，多个用逗号分隔，如 `1,3`；`*` 全选）

用户选择后，按以下规则确定 `--volume-mounts`：

- `volume_mounts` = `[{"VolumeId":"<VolumeId1>","MountPath":"/vol-<VolumeId1>"}, {"VolumeId":"<VolumeId2>",...}, ...]`（所有选中项）

> 如果列表为空，直接跳过此步骤（CLI 默认 `[]`），不询问用户。

---

### 1.7 Step 1.1.6：二次确认（**必经**）

将所有收集到的参数汇总，按快速启动 / CPU / GPU 模式输出确认模板。用户确认后执行 `notebook create`。用户回复识别规则同 §1.8。

#### 快速启动模式确认模板

```
即将创建 Notebook 实例，请确认：
  ┌──────────────────────────────────────────────────┐
  │ 模式        : ⚡ 快速启动                          │
  │ 名称        : notebook-cli                         │
  │ 镜像        : Python (jupyter-base-notebook)      │
  │ Notebook 文件: notebook-cli-20260724-143052 (.ipynb)│
  │ 资源        : 1 核 / 1 GiB / 磁盘 20 GiB            │
  │ 工作目录    : cos://my-bucket/notebooks            │
  │ COS 已有挂载 (3):                                  │
  │  ① my-bucket:/notebooks → /mnt/data               │
  │  ② my-bucket:/data    → /mnt/data2               │
  │  ③ other-bucket:/    → /mnt/other                │
  │ 新增挂载    : 无                                   │
  │ 缓存卷      : 无（快速启动跳过）                    │
  │ 自动关闭    : 是（2880 min）                        │
  └──────────────────────────────────────────────────┘
完整命令:
  python3 scripts/omics_cli.py notebook create \
    --name notebook-cli \
    --image ccr.ccs.tencentyun.com/omics-public/jupyter-base-notebook:2025-12-08 \
    --work-dir cos://my-bucket/notebooks \
    --notebook-file notebook-cli-20260724-143052 \
    --cpu 1 --memory 1 -o json

确认无误请回复「确认 / 继续 / y」；如需修改请告诉我改什么。
```

#### CPU 模式确认模板

```
即将创建 Notebook 实例，请确认：
  ┌──────────────────────────────────────────────────┐
  │ 名称        : my-notebook                         │
  │ 描述        : （用户填的值，没填则"无"）           │
  │ 镜像        : Python (jupyter-base-notebook)      │
  │ 模式        : CPU                                  │
  │ Notebook 文件: demo (.ipynb)                       │
  │ 资源        : 4 核 / 16 GiB / 磁盘 20 GiB          │
  │ 工作目录    : cos://my-bucket/notebooks            │
  │ COS 已有挂载 (3):                                  │
  │  ① my-bucket:/notebooks → /mnt/data               │
  │  ② my-bucket:/data    → /mnt/data2               │
  │  ③ other-bucket:/    → /mnt/other                │
  │ 新增挂载 (1):                                     │
  │  ① new-bucket:/result → /mnt/result               │
  │ 缓存卷 (1):                                       │
  │  ① vol-xxx → /vol-vol-xxx                         │
  │ 自动关闭    : 是（2880 min）                        │
  └──────────────────────────────────────────────────┘
完整命令:
  python3 scripts/omics_cli.py notebook create \
    --name my-notebook \
    --image ccr.ccs.tencentyun.com/omics-public/jupyter-base-notebook:2025-12-08 \
    --work-dir cos://my-bucket/notebooks \
    --notebook-file demo \
    --cos-mounts '[{"Bucket":"new-bucket","SubPath":"/result","MountPath":"/mnt/result"}]' \
    --volume-mounts '[{"VolumeId":"vol-xxx","MountPath":"/vol-vol-xxx"}]' \
    --cpu 4 --memory 16 --boot-disk 20 -o json

确认无误请回复「确认 / 继续 / y」；如需修改请告诉我改什么。
```

#### GPU 模式确认模板

```
即将创建 Notebook 实例，请确认：
  ┌──────────────────────────────────────────────────┐
  │ 名称        : gpu-nb                              │
  │ 描述        : （用户填的值，没填则"无"）           │
  │ 镜像        : R (jupyter-r-notebook)              │
  │ 模式        : GPU (T4 x 1, 8 核 / 32 GiB)         │
  │ Notebook 文件: demo (.ipynb)                       │
  │ 磁盘        : 20 GiB                               │
  │ 工作目录    : cos://my-bucket/notebooks            │
  │ COS 已有挂载 (1):                                  │
  │  ① my-bucket:/notebooks → /mnt/data               │
  │ 新增挂载    : 无                                   │
  │ 缓存卷      : 无                                   │
  │ 自动关闭    : 是（2880 min）                        │
  └──────────────────────────────────────────────────┘
完整命令:
  python3 scripts/omics_cli.py notebook create \
    --name gpu-nb \
    --image ccr.ccs.tencentyun.com/omics-public/jupyter-r-notebook:2026-03-03 \
    --work-dir cos://my-bucket/notebooks \
    --notebook-file demo \
    --gpu-type T4 --gpu-count 1 -o json

确认无误请回复「确认 / 继续 / y」；如需修改请告诉我改什么。
```

> **模板规则**（CPU / GPU 通用）：
> - **COS 已有挂载**：从 `cos list-mount` 返回的环境已有列表，**不需要**通过命令参数传入，仅展示给用户确认。
> - **新增挂载**：用户手动新增的项，才通过 `--cos-mounts` 传入；没有新增则命令中不出现 `--cos-mounts`。
> - 缓存卷同理：有值则 `--volume-mounts`，无则不传。

---

### 1.8 用户回复识别

| 用户回复 | SKILL 行为 |
| --- | --- |
| `y` / `yes` / `确认` / `继续` / `OK` / `是` / `执行` | 调用 `cli.execute(...)` |
| `n` / `no` / `取消` / `等等` / `先别` | 终止流程，等待用户进一步指示 |
| 含修改意图的句子（"改下 X" / "把 Y 换成 Z"） | 解析修改意图 → 重拼命令 → 重走确认 |
| 模糊回复（"嗯" / "好" / "可以" / "试试"） | ⚠️ 不算肯定 → 再次明确询问"是否执行 y/N？" |

---

### 1.9 Step 1.1.7：执行创建

用户确认后执行：

```bash
# CPU 模式
python3 scripts/omics_cli.py notebook create \
  --name <name> \
  --image <image> \
  --work-dir <work_dir> \
  --notebook-file <notebook_file> \
  [--cos-mounts '<cos_mounts_json>'] \
  [--volume-mounts '<volume_mounts_json>'] \
  --cpu <cpu> --memory <memory> [--boot-disk <boot_disk>] \
  [--auto-close / --no-auto-close] [--auto-close-min <min>] -o json

# GPU 模式（CPU/内存自动确定，只传 --gpu-type/--gpu-count，不传 --cpu/--memory）
python3 scripts/omics_cli.py notebook create \
  --name <name> \
  --image <image> \
  --work-dir <work_dir> \
  --notebook-file <notebook_file> \
  [--cos-mounts '<cos_mounts_json>'] \
  [--volume-mounts '<volume_mounts_json>'] \
  --gpu-type <T4|V100> --gpu-count <n> [--boot-disk <boot_disk>] \
  [--auto-close / --no-auto-close] [--auto-close-min <min>] -o json
```

**成功输出**：CLI 回显 `NotebookId` / Name / WorkDir / NotebookUri / CPU·Memory / Image / AutoClose。把 `NotebookId` 转述给用户。

---

### 1.10 常见失败处理

| CLI 报错 | 处置 |
| --- | --- |
| `--cpu/--memory 不匹配` + 列出可选内存值 | 把可选值转述给用户，让其重选 memory 后重跑 |
| `不支持的 GPU 规格组合` | 转述可选 GPU 规格，让用户重选 |
| `--name` 格式错误（超长 / 非法字符 / 连续斜杠） | 转述规则，请用户改名 |
| `--work-dir 格式错误` | 提示须为 `cos://{bucket}/{prefix}` |
| `--cos-mounts` JSON 解析失败 / 字段缺失 | 转述报错，协助用户修正 JSON |
| 环境不是 MANAGED_KUBERNETES / 非 RUNNING | 提示用户去控制台检查环境，或 `omics config set` 切到可用环境 |
| 退出码 2（鉴权失败） | 走 Step 1 引导 `omics login` |

---

## 功能二：列出 Notebook 实例（`omics notebook list`）

列当前 config 环境下的全部 Notebook 实例。**只读，免确认。**

```bash
python3 scripts/omics_cli.py notebook list -o json
```

**输出关键字段**：`NotebookId` / `Name` / `Status` / `CreateTime`，以及 `TotalCount`。

紧凑总结建议：`当前环境共 N 个 Notebook：✅ 运行中 X / ⏸ 已停止 Y`。

> 固定走 config 环境，不支持跨环境查询。如需查别的环境，先让用户 `omics config set` 切换。

---

## 功能三：启动/停止 Notebook 实例

启动或停止当前 config 环境下指定 ID 的 Notebook 实例。**写操作，免确认（有天然安全边界的启停）。**

### 启动实例

```bash
python3 scripts/omics_cli.py notebook start --id <NotebookId>
```

**示例**：`python3 scripts/omics_cli.py notebook start --id nb-xxxx`

**退出码**：0 成功，1 业务错误（如实例不存在或状态不允许启动），2 鉴权失败。

> 启动后可通过 `notebook list` 查看状态变化。

### 停止实例

```bash
python3 scripts/omics_cli.py notebook stop --id <NotebookId>
```

**示例**：`python3 scripts/omics_cli.py notebook stop --id nb-xxxx`

**退出码**：0 成功，1 业务错误（如实例不存在或状态不允许停止），2 鉴权失败。

> **注意**：`notebook start/stop` 是写操作但无需二次确认——启停属于有天然安全边界的操作（停止可重启、启动不会覆盖数据），且需要 `NotebookId` 精确指定目标。如果用户选了错误的实例，应该通过 `notebook list` 确认后再操作。

---

## 功能四：获取 Notebook 实例指定文件内容

使用 `remote_get.py` 下载指定 Notebook 实例 `NotebookCosUri` 所指向的 .ipynb 文件到本地。

> **用途**：当用户希望"执行某个 Notebook 实例上已有的文件"时，**先执行本功能**把远端文件拉到本地，再把得到的本地文件交给**功能五**在实例上执行。即功能四是功能五的前置准备步骤。

### 4.1 整体流程

```
1. omics notebook list -o json → 列出运行中实例，让用户选择一个
2. python3 scripts/remote_get.py <notebook_id> [本地保存路径]
       ↓
   remote_get.py 内部自动：
      ① 从 notebook list 解析 InstanceUrl + NotebookCosUri + CosBucketMounts
      ② 从 cos list-mount 拉环境挂载列表 → 合并 → 匹配 remote_notebook_path
      ③ GET /api/contents/{path} 读取内容 → 保存到本地
3. 得到本地 .ipynb 文件（供功能五使用）
```

### 4.2 Step 1：选择目标实例

```bash
python3 scripts/omics_cli.py notebook list -o json
```

过滤出 `Status == "RUNNING"` 的实例，呈现给用户（# / NotebookId / Name / CreateTime），让用户选一个。

> 如果没有 RUNNING 实例，提示用户先通过功能三启动一个。

### 4.3 Step 2：执行 remote_get.py

```bash
python3 scripts/remote_get.py <notebook_id> [本地保存路径]
```

**参数**：

| 参数 | 说明 |
| --- | --- |
| `notebook_id` | 用户在 Step 1 中选择的实例 ID（如 `notebook-xxx`） |
| 本地保存路径（可选） | 不传则用远程文件名保存到当前目录 |

**依赖**：`pip install requests`

**说明**：脚本固定下载该实例 `NotebookCosUri` 指向的 .ipynb 文件，不接受自定义远程路径。

**示例**：

```bash
python3 scripts/remote_get.py notebook-xxx
python3 scripts/remote_get.py notebook-xxx ./demo.ipynb
```

### 4.4 后续

拿到本地 .ipynb 后，若用户需要在实例上执行，转入**功能五**（把该本地文件传给 `remote_exec.py`）。

---

## 功能五：在 Notebook 实例上执行本地代码

使用 `remote_exec.py` 将本地 .ipynb 文件上传到远端实例执行，并自动回写结果。

### 5.1 整体流程

```
1. omics notebook list -o json → 列出运行中实例，让用户选择一个
2. 用户提供本地 .ipynb 文件路径
3. python3 scripts/remote_exec.py <notebook_id> <本地.ipynb> [kernelId]
       ↓
   remote_exec.py 内部自动：
      ① 从 notebook list 解析 InstanceUrl + NotebookCosUri + CosBucketMounts
      ② 从 cos list-mount 拉环境挂载列表 → 合并 → 匹配 remote_notebook_path
      ③ 上传 notebook → 创建/复用 kernel → 逐 cell 执行 → 回写结果
      ④ 输出 set-session 链接
4. 在编辑器中打开返回的 URL
```

### 5.2 Step 1：选择目标实例

```bash
python3 scripts/omics_cli.py notebook list -o json
```

过滤出 `Status == "RUNNING"` 的实例，呈现给用户（# / NotebookId / Name / CreateTime），让用户选一个。

> 如果没有 RUNNING 实例，提示用户先通过功能三启动一个。

### 5.3 Step 2：获取本地 notebook 文件

让用户提供本地 .ipynb 文件路径（绝对路径或相对于工作目录的相对路径）。

> 如果用户只提供了代码片段而非 .ipynb 文件，SKILL 应先参照 demo.ipynb 格式生成 `.ipynb` 文件到本地，再将文件路径传给 remote_exec.py。

### 5.4 Step 3：执行 remote_exec.py

```bash
python3 scripts/remote_exec.py <notebook_id> <本地.ipynb文件> [kernel_id]
```

**参数**：

| 参数 | 说明 |
| --- | --- |
| `notebook_id` | 用户在 Step 1 中选择的实例 ID（如 `notebook-xxx`） |
| 本地 .ipynb 文件 | 用户在 Step 2 中提供的文件路径 |
| `kernel_id`（可选） | 复用已有 kernel，不传则自动创建新 kernel |

**依赖**：`pip install requests websocket-client`

**示例**：

```bash
python3 scripts/remote_exec.py notebook-xxx demo.ipynb
```

### 5.5 Step 4：打开结果

`remote_exec.py` 执行成功后会输出**两个独立的 URL**：

```
[STEP 3] 🔗 先设置 session: https://genomics.qq.com/platform/cli/set-session?session=...
[STEP 3] 🔗 再打开 notebook: https://<instance>/lab/tree/<path>.ipynb
```

SKILL 按顺序打开：

1. 先用 `preview_url` 打开**第一个 URL**（set-session 链接），用于在浏览器建立会话；
2. **等待第一个 URL 打开完成后**，再用 `preview_url` 打开**第二个 URL**（notebook 地址），任务完成。

> 注意：必须先打开 session URL 并等其加载完成，再打开 notebook URL，否则会话未建立会导致 notebook 打不开。

### 5.6 典型对话示例

```
用户：帮我在 notebook-xxx 上跑一下 demo.ipynb
SKILL：
  1. (内部) omics notebook list -o json 确认实例状态
  2. 确认 demo.ipynb 文件存在
  3. python3 scripts/remote_exec.py notebook-xxx demo.ipynb
  4. 输出执行进度（上传/创建kernel/逐cell执行/回写）
  5. 🔗 先打开 session URL，等加载完成后再打开 notebook URL
```

---

## 典型会话场景

### 场景 A0：用户没装 CLI

1. 任意命令报 `command not found: omics` / 退出码 2（找不到二进制）→
   进入 Step −1，提供官网链接 https://cnb.cool/tencenthealthcareomics/omics-platform-cli，等待用户安装；
2. 等用户回执「已安装」→ 跑 `omics version` 验证 → 通过后进入场景 A。

### 场景 A：用户首次使用

1. `whoami` → 退出 2 → SKILL 主动触发 `omics login`，自动打开浏览器授权页，等用户完成授权
2. 重新 `whoami` ✓ → 跑 `config show` → 退出 1 → SKILL 通过 `AskUserQuestion` 交互式引导完成配置（B端 Step 2-B）或静默写入（C端 Step 2-C）
3. 重新 `config show` ✓ → 进入业务流程

### 场景 B：创建 Notebook 实例

1. `whoami` ✓ + `config show` ✓ → 复述当前配置
2. 用户："帮我建一个 4 核 16G 的 python notebook，叫 my-nb"
3. 收集必填项：镜像（Python → base-notebook 镜像）、工作目录 `--work-dir`、`--notebook-file`、`--cos-mounts`
   - 缺任何必填项 → 向用户询问，**不要替用户编造** Bucket / 路径
4. **二次确认**（按 §1.7 模板，展示完整命令 + 参数摘要）
5. 用户确认 → `notebook create ...`
6. 解析 `NotebookId` → 转述给用户；如需列出可用 `notebook list` 复核

### 场景 C：列实例

1. 用户："我有哪些 notebook" → `notebook list -o json` → 按 Status 分组总结

### 场景 D：用户想切环境

1. 用户："换到 env-yyy 环境" → SKILL 通过 `AskUserQuestion` 交互式引导重新选择地域/项目/环境/桶（B端 Step 2-B），或静默写入（C端 Step 2-C）
2. `config show -o json` 复述新配置后继续业务

### 场景 E：业务命令报鉴权失败

1. 任何业务命令 exit 2 → SKILL 主动触发 `omics login`，自动打开浏览器授权页
2. 等用户完成浏览器授权（最长 120 秒）
3. 重新跑原命令一次

### 场景 F：启动/停止 Notebook 实例

1. `whoami` ✓ + `config show` ✓
2. 用户："启动 nb-xxxx" / "把 nb-xxxx 关掉"
3. 执行 `notebook start --id nb-xxxx` 或 `notebook stop --id nb-xxxx`
4. 输出结果，可选 `notebook list` 复核状态
5. 如果用户不确定 NotebookId，先走场景 C 列实例让用户挑

### 场景 G：获取 Notebook 实例上的文件到本地（功能四）

1. `whoami` ✓ + `config show` ✓
2. `notebook list -o json` → 列出 RUNNING 实例，让用户选一个
3. `python3 scripts/remote_get.py <notebook_id> [本地保存路径]`
4. 输出下载进度 → 得到本地 .ipynb 文件
5. 若用户接着要执行该文件，转入场景 H（功能五）

### 场景 H：在 Notebook 实例上执行代码（功能五）

1. `whoami` ✓ + `config show` ✓
2. `notebook list -o json` → 列出 RUNNING 实例，让用户选一个
3. 用户提供本地 .ipynb 文件路径（或代码片段，SKILL 先生成 .ipynb；也可能来自场景 G 下载的文件）
4. `python3 scripts/remote_exec.py <notebook_id> <本地.ipynb>`
5. 输出执行进度 → 🔗 返回链接 → 在编辑器中打开

---

## 脚本 API 参考

`scripts/omics_cli.py` 也可作为 Python 模块导入：

```python
from scripts.omics_cli import OmicsCLI

cli = OmicsCLI()

# ✅ 检查类命令；whoami 失败走 Step 1（SKILL 主动触发 login）；config show 失败走 Step 2（AskUserQuestion 引导）
cli.execute(cli.build_whoami())
cli.execute(cli.build_config_show(output="json"))
cli.execute(cli.build_config_clear())                  # 仅在用户明确要求清配置时

# Step 1: SKILL 主动调用 login（omics login 在 WorkBuddy 本机运行时可自动打开浏览器）
# Step 2: config set 以非交互式四参数模式调用 (-r -p -e -b)，在 AskUserQuestion 收集参数后执行

# 创建 Notebook（写操作，调用前必须完成二次确认！）
cli.execute(cli.build_notebook_create(
    name="my-notebook",
    image=OmicsCLI.IMAGE_JUPYTER_PYTHON,
    work_dir="cos://my-bucket/notebooks",
    notebook_file="demo",
    cos_mounts='[{"Bucket":"my-bucket","MountPath":"/mnt/data"}]',
    cpu=4, memory=16, boot_disk=20,
    output="json",
))

# GPU 模式：CPU/内存由规格自动确定
cli.execute(cli.build_notebook_create(
    name="gpu-nb",
    image=OmicsCLI.IMAGE_JUPYTER_R,
    work_dir="cos://my-bucket/notebooks",
    notebook_file="demo",
    cos_mounts='[{"Bucket":"my-bucket","MountPath":"/mnt/data"}]',
    gpu_type="T4", gpu_count=1,
    output="json",
))

# 列 Notebook 实例
cli.execute(cli.build_notebook_list(output="json"))

# 启动 / 停止 Notebook 实例
cli.execute(cli.build_notebook_start(notebook_id="nb-xxxx"))
cli.execute(cli.build_notebook_stop(notebook_id="nb-xxxx"))
```

环境变量 `OMICS_CLI_PATH` 可覆盖 CLI 可执行文件路径。

---

## 关联文档

- 边界契约：[CONTRACT.md](CONTRACT.md)
- 命令 wrapper：[scripts/omics_cli.py](scripts/omics_cli.py)
