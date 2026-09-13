---
name: team-clinical-central-lab-aliquot-billing-reconciliation
description: "Reconcile clinical-trial central-laboratory aliquot billing across studies, sites, pseudonymized specimens and parent tubes, visits and collection, receipt conditions, centrifugation and aliquoting rules, child-tube barcodes, volumes and counts, frozen custody, testing and send-outs, failed processing and realiquoting, rates, invoices, credits, payments, and trial ledgers without reidentifying participants, handling specimens, deciding sample validity, changing laboratory records, or moving funds. This Pay Skill provides free scope validation, then requires verified payment before releasing the full deliverable."
tags: [临床试验, 中心实验室, 样本分装, 实验室账单]
version: 2.0.2
capability: clinical_central_lab_aliquot_billing_reconciliation
pricing:
  model: per_call
  amount_fen: 599
---

# 临床试验中心实验室分装账单核对台

## Objective

Convert scattered team evidence into a controlled, traceable workflow. Produce decisions and actions that can be checked against source material, assigned to named roles, approved, and updated over time.

## Team Roles

Use the user's real role names when available. Otherwise propose these roles and mark assignments as pending confirmation:

- 临床样本运营
- 中心实验室
- 数据管理和质量
- 试验财务
- 账单审批人

Never silently assign a person, approval, deadline, or commitment.

## Required Inputs

- 研究中心、去标识样本原管、访视采样和接收条件
- 离心分装规则、子管条码体积数量、冻存托管、检测外送和失败重做
- 费率、发票贷项付款和试验总账

Start with available material. Create a missing-information queue instead of blocking the whole task when noncritical inputs are absent.

## Pay Skill Contract

Price: `CNY 5.99` per paid invocation. Skill version: `2.0.2`. Product ID: `SP2608160396`.

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
3. 按原管和子管条码重建接收、处理、分装、冻存及外送链
4. 核对方案规则、数量体积、失败重做、托管和费率
5. 分类幽灵子管、重复分装、体积不可能、无托管记录和账簿差异
6. Run the quality gate: verify coverage, source traceability, owner confirmation, dates, dependencies, approval state, sensitive-data handling, and unresolved contradictions.
7. Deliver an executive summary, the core register, decision queue, action register, evidence gaps, approvals required, and a concise handoff message.

## Core Register

Use this minimum schema:

`差异ID | 研究/实验室 | 中心/匿名样本 | 原管条码 | 接收条件 | 离心/分装规则 | 子管条码/数量/体积 | 冻存/托管 | 检测/外送 | 失败/重分装 | 费率/发票/差异金额 | 证据 | 状态`

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

- 不得重识别受试者、接触样本或改变实验室记录
- 不得判断样本有效性、作临床决定或划款
- 身份断链、体积冲突、温控异常或系统性幽灵子管必须升级实验室质量、临床运营、数据管理与管理层

## Example Requests

- "核对中心实验室分装账单"
- "识别幽灵子管和重复处理费"
- "生成实验室补证、数据复核与贷项台账"

