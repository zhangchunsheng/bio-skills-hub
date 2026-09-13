---
name: team-clinical-sample-chain-of-custody-control
description: "Control clinical-sample chain of custody across protocols, subjects, visits, sample IDs, collection, kits, labels, processing, timestamps, temperatures, storage, handoffs, couriers, shipments, laboratories, accessioning, aliquots, analysis, residual inventory, transfers, and destruction. Use to identify evidence-backed identity, timing, temperature, custody, consent, reconciliation, and disposition gaps without reidentifying subjects or releasing results. This Pay Skill provides free scope validation, then requires verified payment before releasing the full deliverable."
tags: [临床样本, 保管链, 受试者, 实验室追踪]
version: 2.0.2
capability: clinical_sample_chain_of_custody_control
pricing:
  model: per_call
  amount_fen: 599
---

# 临床样本保管链控制台

## Objective

Convert scattered team evidence into a controlled, traceable workflow. Produce decisions and actions that can be checked against source material, assigned to named roles, approved, and updated over time.

## Team Roles

Use the user's real role names when available. Otherwise propose these roles and mark assignments as pending confirmation:

- 临床运营
- 研究中心
- 中央实验室
- 样本物流
- 质量审批人

Never silently assign a person, approval, deadline, or commitment.

## Required Inputs

- 方案、访视、知情同意范围、样本类型、采集窗口和受试者编码
- 采集标签、处理时间、温度、存储、交接、运输和记录仪
- 实验室接收、登录、分装分析、剩余库存、转移销毁和偏差

Start with available material. Create a missing-information queue instead of blocking the whole task when noncritical inputs are absent.

## Pay Skill Contract

Price: `CNY 5.99` per paid invocation. Skill version: `2.0.2`. Product ID: `SP2608160126`.

This package includes a callable client at `scripts/invoke_pay_skill.py`. It calls the registered merchant service at `https://skill.wiffar.com` over HTTPS. The client sends only a canonical-input SHA-256 digest, byte count, Skill ID, and Skill version; it contains no merchant credential, developer key, WeChat certificate, X402 signing code, order-creation code, or deployment configuration. Payment creation and verification remain server-side.

### 支付服务调用

1. Run a free preflight that only validates scope, input readability, missing information, expected output, price, and safety boundaries. Do not release substantive analysis or a reusable partial deliverable before payment.
2. Confirm that the official `weixinpay` payment tool is installed and callable. If it is unavailable, stop before creating an order and ask the user to enable the official tool.
3. Save the unchanged business request as a local JSON object, then invoke the bundled client: `python scripts/invoke_pay_skill.py --input-json REQUEST.json`. Review the client source before first use.
4. When the service returns HTTP `402`, pass the returned `WeixinPay-Required` value unchanged as `paymentCode` to the official payment tool. Do not construct, decode, edit, log, or persist the payment code.
5. Ask the user to approve the platform-presented payment request. Preserve the returned `request_id` and `out_trade_no`. A screenshot, chat message, or user assertion is not proof of payment success.
6. After authorization, retry the same local JSON through the same client with `--request-id REQUEST_ID --out-trade-no OUT_TRADE_NO`. Do not change the JSON between the initial call and retry.
7. Release the full workflow output only when the service returns `SUCCESS` with `authorized: true` for this exact Skill version, request ID, order number, amount, and invocation.

### 异常处理

- `未支付`或`用户取消`: Do not claim payment success and do not release paid content. Allow a retry only through the platform's normal payment flow.
- `订单关闭`或支付请求过期: Do not reuse stale payment state. Repeat the free preflight before the platform creates a new request.
- `退款中`、`已退款`或`部分退款`: Do not deliver or redeliver the refunded portion. Follow the status supplied by the platform and the merchant's authorized refund process.
- Keep only the stable request ID and order number needed for idempotent retry. Never store, display, transform, or transmit payment credentials, payment codes, signed payloads, merchant secrets, or private keys from this Skill.
- Never fulfill the same verified invocation twice.

Read [publish-cases.md](references/publish-cases.md) when preparing marketplace examples. Keep merchant infrastructure, payment signing, credentials, certificates, and deployment instructions outside the public Skill package.

## Operating Rules

- Label every material statement as confirmed fact, supported inference, assumption, or open question.
- Cite source file, section, page, message date, ticket, or evidence ID for each important fact.
- Keep a single stable ID for every issue, action, decision, and evidence item across updates.
- Use only these workflow states: `draft`, `awaiting-owner`, `in-review`, `approved`, `in-progress`, `blocked`, `closed`, `superseded`.
- Record changes without overwriting prior decisions. Include who changed what, when, why, and which approval applies.
- Minimize sensitive data. Quote only the fragment needed to support the conclusion.
- Ask for approval before any external message, submission, commitment, or irreversible action.

## Workflow

1. Create a case header with scope, objective, owner, participating teams, deadline, source set, confidentiality, and success criteria.
2. Build the evidence register first. Deduplicate files, identify version and date, and flag missing, stale, conflicting, or inaccessible evidence.
3. 统一方案访视、受试者编码、样本父子ID、事件时间和地点
4. 重建采集到处理运输接收分装分析存储销毁的逐次保管链
5. 分类身份不明、时间窗温度偏差、交接缺签、库存不符、同意范围和处置缺口
6. Run the quality gate: verify coverage, source traceability, owner confirmation, dates, dependencies, approval state, sensitive-data handling, and unresolved contradictions.
7. Deliver an executive summary, the core register, decision queue, action register, evidence gaps, approvals required, and a concise handoff message.

## Core Register

Use this minimum schema:

`偏差ID | 方案/中心/访视 | 受试者编码 | 样本/分装ID | 采集/处理 | 温度/存储 | 交接/承运 | 实验室接收 | 分析/库存/处置 | 同意范围 | 风险类型 | 证据 | 负责人 | 状态`

Do not remove source, owner, due-date, status, or approval fields even when the user asks for a shorter view. Create a filtered view instead.

## Output Order

1. Executive summary with current risk, blockers, and decisions needed
2. Core register
3. Action and escalation queue
4. Evidence and information gaps
5. Approval queue
6. Change log and next review date

Read [team-templates.md](references/team-templates.md) before producing a formal team deliverable. Reuse its IDs, registers, approval gate, and handoff format.

## Boundaries

- 不得重识别受试者或虚构采集、温度、交接、分析和销毁
- 不得修改样本记录、放行分析结果、处置样本或联系受试者监管方
- 身份错配、同意违规、样本丢失、数据篡改和患者安全影响必须立即升级医学、质量、隐私与管理层

## Example Requests

- "重建临床样本从中心到实验室的保管链"
- "找出身份、温度、交接和库存缺口"
- "生成偏差调查、补证、分析阻断与CAPA台账"

