---
name: patent-sequence-selfhosted
description: 在用户本机直接运行专利蛋白序列检索（Codex 或其他 agent 均可），使用自带的标准库 CLI、本地状态/缓存和 EMBL-EBI，外发前需显式确认。无需后端服务、网页或 PatSeek API。PatSeek 仅用于可选地增强已解析的专利公开号详情。用户要求 PatSeek 托管的序列检索时请使用受管的 patseek-sequence-search skill。不适用于核苷酸或化学结构检索。
---

# 本机专利蛋白序列检索（Agent-local）

在 agent 宿主机上直接使用 `scripts/client.py`。仅依赖 Python 标准库；
不要启动 FastAPI、后台服务或网页。计划、任务元数据、归一化公开结果和缓存
条目存储在 `PATENT_SEQUENCE_STATE_DIR`（默认 `~/.cache/patent-sequence-local`）。
原始查询序列永不落盘。

安装与状态行为见 [references/local-runtime.md](references/local-runtime.md)。
首次检索前先跑 `doctor`。`PATSEEK_API_KEY`、`PATSEQ_BACKEND_URL`、
`PATSEQ_BACKEND_API_KEY` 均非必需，序列客户端也不会读取。

## 隐私与授权

本 skill 仅支持蛋白质序列。优先用 `--sequence-file`；不要打印、记录或在报告中
包含原始序列。计划阶段完全本地、零网络请求。执行时，每个缓存未命中的库会把
蛋白序列和配置的联系邮箱直接发送到 EMBL-EBI。

联系地址自动解析，优先级如下：(1) 用户自设的 `EBI_CONTACT_EMAIL`；
(2) 每台安装持久化的自动地址（`patent-seq-<hex>@<domain>`，存于状态目录的
`contact-email.json`）；(3) 首次外发时新生成的地址。EMBL-EBI 拒绝无 MX 记录
域名的地址（如 `users.noreply.github.com`、`test.com` 会被拒；`github.com`
可用）。可用 `PATENT_SEQUENCE_AUTO_EMAIL_DOMAIN` 覆盖兜底域名（尽量用自己
可控的域名）。若执行返回 `error_code: "INVALID_CONTACT_EMAIL"`，停下并向用户
索取真实 `EBI_CONTACT_EMAIL`，然后用**新的 idempotency key** 重试。不要把该
地址写进报告，也不要持久化到 plan/search/cache 文件。

制定计划前，先确认序列已公开。若为未公开、专有、患者来源、受出口管制或其他
敏感序列，除非用户明确接受发往 EMBL-EBI，否则停止。不得从一般性的检索请求
推断用户已同意外发。

## 成本安全工作流

1. 零网络诊断本地运行时：

   ```bash
   python3 scripts/client.py doctor
   ```

2. 创建本地计划。仅记录序列长度和摘要，并报告哪些库需要外发。默认检索全部
   6 个专利库（epo/jpo/kipo/uspto/nrpl1/nrpl2）；用 `--database` 收窄：

   ```bash
   python3 scripts/client.py plan \
     --sequence-file /path/to/query.fasta
   ```

3. 向用户报告：plan ID、查询摘要与长度、库、阈值、缓存命中、预计外发次数、
   目的地、零费用、有效期和本地留存情况。

4. 若预计有外发，指明涉及哪些库和 EMBL-EBI 目的地，并在执行前获得显式确认。
   计划不构成外发授权。无需用户预先提供邮箱：联系地址自动解析（见「隐私与
   授权」）；仅 `INVALID_CONTACT_EMAIL` 失败时才升级询问用户。

5. 用同一序列和稳定的按案 idempotency key 执行：

   ```bash
   python3 scripts/client.py execute \
     --plan-id plp_... \
     --sequence-file /path/to/query.fasta \
     --idempotency-key case-2026-0001 \
     --confirm-external-submission
   ```

6. 轮询返回的 search ID；不要因某个库慢就重新提交：

   ```bash
   python3 scripts/client.py watch pls_... --summary --top 5
   ```

   注意：若 EBI 的 status 端点已返回 FINISHED 但本地长期显示 running 且
   报 `Cannot parse EMBL-EBI result types`，说明 poll 进程用的是旧版代码，
   应停掉旧 watch 进程后用修复版重新 poll（不要重发提交）。

7. 任务完成后生成独立静态报告。只写一个 HTML 文件，不启服务、不加载外部脚本：

   ```bash
   python3 scripts/client.py render-html pls_... \
     --output /path/to/sequence-report.html \
     --title "公开专利蛋白序列对比" \
     --top 10
   ```

   `--top` 默认 20。默认报告展示指标、专利
   映射、目标残基和比对坐标，不嵌入查询残基。对已公开序列，确认生成的
   HTML 可以包含完整查询序列后，才连同匹配的 FASTA 加 `--include-query-sequence`。
   包含查询残基时，比对视图会加每 10 残基一个的共享位置标尺、每 5 残基的
   视觉分组和带编号的差异芯片，便于逐残基核对；并渲染由所示比对计算的对称
   一致性矩阵（精确匹配 / 替换 / 缺口列计数）。

`queued` 和 `running` 视为未完成。超时和失败的库按「失败」处理，不是零命中。
execute 响应不确定时，复用完全相同的 idempotency key。若进程中断后本地某库
记录停留在 `submitting`，不要盲目重发，因为外部结果可能未知。

## 结果解读与可选的 PatSeek 交互

解读结果前先读 [references/reporting.md](references/reporting.md)。把序列
相似性、专利号映射、权利要求关联作为三个独立的证据维度。

序列工作流本身无需 PatSeek 即告完成。若用户另行要求专利详情、同族、权利
要求或法律状态，读 [references/patseek-enrichment.md](references/patseek-enrichment.md)。
用隔离的可选助手做能力检测并创建零调用计划：

```bash
python3 scripts/patseek_enrichment.py check
python3 scripts/patseek_enrichment.py plan pls_... --top 5
```

若返回状态为 `skill_missing`、`api_key_missing`、`api_invalid`、
`api_disabled` 或 `credits_insufficient`，停止并把返回的 `user_action` 告知
用户。未经用户操作，不得安装 Skill、创建/复用 Key 或充值。已配置的 Key 不
代表有效；可用 `check --validate-api-key` 在不请求专利详情的前提下校验。

向用户展示：计划涉及的公开号去重清单、详情调用次数、直到响应前未知的积分
成本、有效期和确认要求。仅在显式确认后执行：

```bash
python3 scripts/patseek_enrichment.py execute \
  --plan-id pep_... \
  --confirm-patseek-use
```

若标准库 HTTPS 传输在拿到确定响应前失败、且已安装的 PatSeek Skill 运行时
可用，须待用户确认没有任何详情调用成功后创建新计划，再加
`--transport skill-client`。该传输使用 PatSeek Skill 的 `requests` 依赖，
但每个付费详情请求只尝试一次。

助手会在详情调用前校验 Key、增量写入进度、不重试不确定的调用，并把归一化
公开结果存于 `enrichments/`。之后的 `render-html` 会自动补充专利身份、申请
人/发明人、日期、聚合法律状态、同族数量、权利要求-序列信号、增强覆盖率及
实际返回积分。失败与未尝试的公开号要分开披露。绝不向 PatSeek 发送蛋白序列
或本地检索状态，也绝不回退到 PatSeek 托管的序列检索。

相似性只是候选召回证据，不构成权利要求范围、有效性、FTO 或侵权结论。
