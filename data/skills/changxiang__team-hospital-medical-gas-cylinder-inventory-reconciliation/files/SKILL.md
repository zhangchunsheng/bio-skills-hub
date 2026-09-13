---
name: team-hospital-medical-gas-cylinder-inventory-reconciliation
description: "Reconcile hospital medical-gas cylinder inventory across gases, cylinders, serial numbers, sizes, ownership, inspections, fills, receipts, storage, wards, patients or equipment, issues, returns, empties, losses, rentals, supplier invoices, credits, and ledgers. Use to identify evidence-backed identity, gas, inspection, fill, location, custody, issue, return, rental, invoice, credit, or balance differences without handling cylinders, making clinical decisions, releasing gas, changing safety records, or moving funds. This Pay Skill provides free scope validation, then requires verified payment before releasing the full deliverable."
tags: [医用气瓶, 氧气库存, 钢瓶租金, 病区追溯]
version: 2.0.2
capability: hospital_medical_gas_cylinder_inventory_reconciliation
pricing:
  model: per_call
  amount_fen: 499
---

# 医院医用气瓶库存核对台

## Objective

Convert scattered team evidence into a controlled, traceable workflow. Produce decisions and actions that can be checked against source material, assigned to named roles, approved, and updated over time.

## Team Roles

Use the user's real role names when available. Otherwise propose these roles and mark assignments as pending confirmation:

- 医院设施运营
- 医用气体管理
- 临床工程
- 供应链
- 库存审批人

Never silently assign a person, approval, deadline, or commitment.

## Required Inputs

- 气体类型气瓶序列号规格所有权检验和充装
- 收货仓储病区发放使用空瓶退回和盘点
- 租赁费率、供应商发票贷项和总账

Start with available material. Create a missing-information queue instead of blocking the whole task when noncritical inputs are absent.

## Pay Skill Contract

Price: `CNY 4.99` per paid invocation. Skill version: `2.0.2`. Product ID: `SP2608160194`.

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
3. 按气瓶序列号建立供应商到病区再到退回的托管链
4. 核对检验充装状态、位置、收发空瓶和理论实物余额
5. 分类失联错气、过检、重复租金、漏退贷项和账簿差异
6. Run the quality gate: verify coverage, source traceability, owner confirmation, dates, dependencies, approval state, sensitive-data handling, and unresolved contradictions.
7. Deliver an executive summary, the core register, decision queue, action register, evidence gaps, approvals required, and a concise handoff message.

## Core Register

Use this minimum schema:

`风险ID | 气体/气瓶序列号 | 规格/所有权 | 检验/充装 | 收货 | 位置/保管 | 发放/使用 | 空瓶/退回 | 理论余额 | 实物余额 | 租金/发票 | 风险金额 | 证据 | 责任人 | 状态`

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

- 不得虚构气体身份、检验、充装、位置、使用或供应商确认
- 不得搬运气瓶、作临床判断、释放气体、改安全记录或划款
- 错气、过检在用、泄漏安全、关键区域缺货和批量失联必须升级临床安全、设施、质量和管理层

## Example Requests

- "核对医用氧气瓶月度盘点与供应商账单"
- "识别失联、过检和重复租金"
- "生成病区确认、隔离建议、退瓶贷项与采购台账"

