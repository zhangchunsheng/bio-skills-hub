---
name: team-pharma-rebate-chargeback-reconciliation
description: "Reconcile pharmaceutical rebates and distributor chargebacks across contracts, products, NDCs, price eligibility, customers, classes of trade, sales, resales, inventories, returns, claims, chargebacks, rebates, fees, credits, disputes, and payments. Use to identify evidence-backed ineligible claims, wrong price deltas, duplicate units, quantity mismatches, short credits, and deadline risks without adjudicating or paying claims. This Pay Skill provides free scope validation, then requires verified payment before releasing the full deliverable."
tags: [医药返利, 分销扣款, 合同价格, 药品结算]
version: 2.0.2
capability: pharma_rebate_chargeback_reconciliation
pricing:
  model: per_call
  amount_fen: 599
---

# 医药返利扣款核对台

## Objective

Convert scattered team evidence into a controlled, traceable workflow. Produce decisions and actions that can be checked against source material, assigned to named roles, approved, and updated over time.

## Team Roles

Use the user's real role names when available. Otherwise propose these roles and mark assignments as pending confirmation:

- 医药合同与定价
- 渠道分销运营
- 收入与返利会计
- 合规
- 索赔审批人

Never silently assign a person, approval, deadline, or commitment.

## Required Inputs

- 合同、产品编码、价格版本、合格客户、交易类别、返利扣款规则和期限
- 出厂销售、分销转售、库存、退货、单位换算和客户层级
- 索赔扣款、贷项、付款、拒绝争议、应计和历史调整

Start with available material. Create a missing-information queue instead of blocking the whole task when noncritical inputs are absent.

## Pay Skill Contract

Price: `CNY 5.99` per paid invocation. Skill version: `2.0.2`. Product ID: `SP2608160086`.

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
3. 统一产品编码、客户层级、交易类别、合同价格、单位和服务期间
4. 逐行连接销售转售、资格、合同价差、索赔扣款、贷项和付款
5. 分类无资格、错价差、重复单位、数量错配、少贷项和截止风险并路由复核
6. Run the quality gate: verify coverage, source traceability, owner confirmation, dates, dependencies, approval state, sensitive-data handling, and unresolved contradictions.
7. Deliver an executive summary, the core register, decision queue, action register, evidence gaps, approvals required, and a concise handoff message.

## Core Register

Use this minimum schema:

`差异ID | 合同/客户 | 产品编码 | 交易类别 | 销售/转售 | 服务期 | 合同价/成交价 | 合格单位 | 应返/应扣 | 已申/已贷 | 差异类型 | 截止日 | 证据 | 负责人 | 状态`

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

- 不得虚构合同价格、客户资格、转售单位、索赔或贷项
- 不得审批拒绝索赔、开具贷项、付款、单方扣款或修改主数据
- 政府价格、反回扣、340B或类似监管、制裁和重大异常必须升级合规、法务、定价负责人和审计

## Example Requests

- "核对分销商月度药品扣款和返利"
- "找出错客户资格、错价差、重复单位和少贷项"
- "生成争议、补证、贷项调整与应计复核台账"

