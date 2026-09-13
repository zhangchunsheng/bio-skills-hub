---
name: team-clinical-trial-site-payment
description: "Reconcile clinical-trial site payments across clinical trial agreements, budgets, subjects, visits, procedures, milestones, screen failures, pass-through costs, laboratories, imaging, amendments, invoices, taxes, holdbacks, payments, and closeout. Use to identify evidence-backed missing, duplicate, premature, unsupported, wrong-rate, overbudget, and closeout-payment exceptions without accessing unnecessary patient data, approving invoices, or releasing payments. This Pay Skill provides free scope validation, then requires verified payment before releasing the full deliverable."
tags: [临床试验, 研究中心付款, 访视对账, 研究预算]
version: 2.0.2
capability: clinical_trial_site_payment
pricing:
  model: per_call
  amount_fen: 599
---

# 临床试验中心付款核对台

## Objective

Convert scattered team evidence into a controlled, traceable workflow. Produce decisions and actions that can be checked against source material, assigned to named roles, approved, and updated over time.

## Team Roles

Use the user's real role names when available. Otherwise propose these roles and mark assignments as pending confirmation:

- 临床运营
- 研究中心管理
- 临床财务
- 数据管理或项目管理
- 付款审批人

Never silently assign a person, approval, deadline, or commitment.

## Required Inputs

- 临床试验协议、中心合同预算、修订、付款里程碑、税费和保留款
- 去标识化受试者访视、操作、筛败、实验室影像和EDC状态
- 中心发票、直通费用、付款、查询、预算消耗和关中心材料

Start with available material. Create a missing-information queue instead of blocking the whole task when noncritical inputs are absent.

## Pay Skill Contract

Price: `CNY 5.99` per paid invocation. Skill version: `2.0.2`. Product ID: `SP2608160080`.

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
3. 最小化并去标识化数据，统一研究、中心、受试者令牌、访视事件、合同版本和币种
4. 逐项连接已完成可付事件、合同费率、直通费用、发票、保留款和已付款
5. 分类漏付、重复、过早、无支持、错费率、超预算和关中心缺口并分派调查
6. Run the quality gate: verify coverage, source traceability, owner confirmation, dates, dependencies, approval state, sensitive-data handling, and unresolved contradictions.
7. Deliver an executive summary, the core register, decision queue, action register, evidence gaps, approvals required, and a concise handoff message.

## Core Register

Use this minimum schema:

`差异ID | 研究/中心 | 受试者令牌 | 访视/里程碑 | 完成状态 | 合同版本/费率 | 直通费用 | 应付 | 发票 | 已付/保留 | 预算影响 | 差异类型 | 证据 | 负责人 | 状态`

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

- 不得收集不必要的直接身份信息、虚构访视完成、合同费率、发票或中心确认
- 不得修改EDC、批准发票、释放付款、联系受试者或作出医学判断
- 受试者安全、方案偏离、隐私泄露、制裁命中、研究舞弊和重大超预算必须升级医学、合规、法务和财务授权人

## Example Requests

- "核对多中心试验本月访视和里程碑付款"
- "找出漏付、重复、错费率、无支持费用和超预算"
- "生成中心查询、补票、付款、保留款与关中心台账"

