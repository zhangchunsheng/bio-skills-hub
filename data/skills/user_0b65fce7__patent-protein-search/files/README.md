# patent-sequence-selfhosted

## 作用

在本地对**公开的蛋白质序列**做专利相似性检索：纯 Python 标准库 CLI，无需后端服务或网页。计划在本地生成（零联网），执行时把序列提交到 **EMBL-EBI** 的 6 个专利序列库（EPO / JPO / KIPO / USPTO / nrpl1 / nrpl2），命中结果归一化后本地留存（默认 `~/.cache/patent-sequence-local`）并生成独立 HTML 报告。零费用，原始查询序列不落盘。

> 仅支持蛋白序列；核苷酸、化学结构不适用。相似度只是候选召回证据，不构成权利要求范围 / 有效性 / FTO / 侵权结论。

## 使用方法（6 步）

```bash
cd ~/.workbuddy/skills/patseek-sequence-search

# 1. 自检（不联网）
python3 scripts/client.py doctor

# 2. 本地计划（默认全 6 库，零提交；--database 可收窄）
python3 scripts/client.py plan --sequence-file query.fasta

# 3. 外发需明示确认；执行（仅提交缓存未命中部分）
python3 scripts/client.py execute \
  --plan-id plp_... --sequence-file query.fasta \
  --idempotency-key case-2026-001 --confirm-external-submission

# 4. 轮询至终态（queued/running = 未完成，勿重提）
python3 scripts/client.py watch pls_... --summary --top 5

# 5. 生成静态报告（--top 默认 20，可按需调整）
python3 scripts/client.py render-html pls_... \
  --output report.html --top 10 --title "公开专利蛋白序列对比"
```

可选第 6 步——**PatSeek 专利详情增强**（需要申请人 / 法律状态 / 同族时才用，走 `scripts/patseek_enrichment.py` 的 check → plan → execute，消耗积分并需二次确认）。详见 `references/patseek-enrichment.md`。

## 关键机制

- **联系邮箱全自动**：优先 `EBI_CONTACT_EMAIL`（用户自设）→ 本机持久化复用（状态目录 `contact-email.json`）→ 自动生成（EBI 校验域名 MX 记录，默认 `patent-seq-<hex>@github.com`；可用 `PATENT_SEQUENCE_AUTO_EMAIL_DOMAIN` 换成自己的域名）。仅当报 `error_code: INVALID_CONTACT_EMAIL` 时才需用户提供真实邮箱，并换**新的 idempotency key** 重试。
- **幂等续跑**：execute 中断后用**同一 idempotency key** 重跑不会重复提交；换 key = 全新检索。
- **结果分级**：QX（100% 一致）/ QH（≥90% 高相似）/ QS（其它命中）× P1（解析出公开号，可做详情增强）/ P0（仅 accession，勿臆造公开号）× C0（权利要求未核实前恒为此）。详见 `references/reporting.md`。
- **单序列限制**：多序列 FASTA 不支持，一次一条。
- **报告默认不含查询序列**；公开序列可加 `--include-query-sequence`（配合 `--sequence-file`）升级为带位置标尺、差异芯片和对称一致性矩阵的逐残基比对视图。

更多细节见 `SKILL.md` 与 `references/`（local-runtime / reporting / patseek-enrichment）。
