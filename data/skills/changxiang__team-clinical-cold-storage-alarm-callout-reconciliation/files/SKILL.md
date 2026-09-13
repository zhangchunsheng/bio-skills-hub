---
name: team-clinical-cold-storage-alarm-callout-reconciliation
description: "Reconcile clinical cold-storage alarm callout billing across studies, laboratories, refrigerators, freezers and deidentified assets, alarm events and configured limits, notification, acknowledgement and escalation timestamps, remote diagnosis, onsite arrival, failure causes, repairs and parts, temperature recovery and continuous monitoring, repeat attendance, warranties, rates, invoices, credits, payments, and trial ledgers without accessing specimens, changing alarms or records, deciding product or sample disposition, certifying equipment, or moving funds. This Pay Skill provides free scope validation, then requires verified payment before releasing the full deliverable."
tags: [临床试验冷存储, 温度报警, 上门服务, 供应商账单]
version: 2.0.2
capability: clinical_cold_storage_alarm_callout_reconciliation
pricing:
  model: per_call
  amount_fen: 599
---

# 临床冷存储报警上门服务账单核对台

## Objective

Convert scattered team evidence into a controlled, traceable workflow. Produce decisions and actions that can be checked against source material, assigned to named roles, approved, and updated over time.

## Team Roles

Use the user's real role names when available. Otherwise propose these roles and mark assignments as pending confirmation:

- 临床样本与药品冷链运营
- 实验室设施设备
- 质量和温控
- 试验财务审计
- 账单审批人

Never silently assign a person, approval, deadline, or commitment.

## Required Inputs

- 研究实验室、冷存储设备和去标识资产、报警事件阈值与时标
- 通知确认升级、远程诊断、上门到场、故障维修换件和温度恢复
- 连续监测、重复出勤、质保、费率发票和试验总账

Start with available material. Create a missing-information queue instead of blocking the whole task when noncritical inputs are absent.

## Pay Skill Contract

Price: `CNY 5.99` per paid invocation. Skill version: `2.0.2`. Product ID: `SP2608160426`.

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
3. 按设备与报警事件重建通知、远程诊断、出勤、维修和恢复链
4. 核对到场资格、重复出勤原因、换件质保、时长和合同费率
5. 分类幽灵上门、重复出勤、质保内收费、无恢复证据和账簿差异
6. Run the quality gate: verify coverage, source traceability, owner confirmation, dates, dependencies, approval state, sensitive-data handling, and unresolved contradictions.
7. Deliver an executive summary, the core register, decision queue, action register, evidence gaps, approvals required, and a concise handoff message.

## Core Register

Use this minimum schema:

`差异ID | 研究/实验室 | 冷存储设备 | 报警事件/阈值 | 通知/确认/升级 | 远程诊断 | 上门到场 | 故障原因 | 维修/换件 | 温度恢复/连续监测 | 重复出勤/质保 | 费率/差异金额 | 证据 | 状态`

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

- 不得接触样本药品、改变报警或实验室记录
- 不得作样本药品处置决定、认证设备或划款
- 温度持续失控、报警未送达、恢复证据缺失或系统性幽灵上门必须升级冷链、实验室质量、临床运营与管理层

## Example Requests

- "核对冷存储报警上门服务账单"
- "识别幽灵上门和重复出勤"
- "生成供应商补证、质保复核与贷项台账"

