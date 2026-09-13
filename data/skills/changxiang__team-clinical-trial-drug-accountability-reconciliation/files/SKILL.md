---
name: team-clinical-trial-drug-accountability-reconciliation
description: "Reconcile clinical-trial investigational-product accountability across protocols, countries, sites, depots, products, kits, lots, expiries, randomization systems, shipments, receipts, temperatures, storage, dispensing, subjects, returns, reconciliation, quarantine, destruction, certificates, deviations, approvals, and inventory balances. Use to identify evidence-backed missing, duplicate, misassigned, expired, temperature-affected, unreturned, or unexplained units without randomizing subjects, dispensing product, changing trial data, releasing stock, or destroying product. This Pay Skill provides free scope validation, then requires verified payment before releasing the full deliverable."
tags: [试验药品, IP账物, IWRS, 中心库存]
version: 2.0.2
capability: clinical_trial_drug_accountability_reconciliation
pricing:
  model: per_call
  amount_fen: 599
---

# 临床试验药品账物核对台

## Objective

Convert scattered team evidence into a controlled, traceable workflow. Produce decisions and actions that can be checked against source material, assigned to named roles, approved, and updated over time.

## Team Roles

Use the user's real role names when available. Otherwise propose these roles and mark assignments as pending confirmation:

- 临床供应
- 中心药房
- 临床运营
- 质量保证
- 药品差异审批人

Never silently assign a person, approval, deadline, or commitment.

## Required Inputs

- 方案国家中心、药品套件批号效期、随机与分配规则
- 仓库发运收货温控、中心储存、受试者发放使用退回记录
- IWRS导出、库存盘点、隔离销毁、证书、偏差和审批

Start with available material. Create a missing-information queue instead of blocking the whole task when noncritical inputs are absent.

## Pay Skill Contract

Price: `CNY 5.99` per paid invocation. Skill version: `2.0.2`. Product ID: `SP2608160164`.

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
3. 按产品套件批号中心受试者建立不可变事件链
4. 滚动核对期初收发放退隔离销毁与期末实物余额
5. 分类错发、漏收发、未退、温控影响、效期、盲态和销毁证据缺口
6. Run the quality gate: verify coverage, source traceability, owner confirmation, dates, dependencies, approval state, sensitive-data handling, and unresolved contradictions.
7. Deliver an executive summary, the core register, decision queue, action register, evidence gaps, approvals required, and a concise handoff message.

## Core Register

Use this minimum schema:

`差异ID | 试验/中心 | 产品/套件/批号 | 效期 | IWRS状态 | 物流状态 | 中心库存 | 受试者发放/退回 | 隔离/销毁 | 温控 | 理论余额 | 实物余额 | 差异类型 | 受试者影响 | 证据 | 状态`

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

- 不得暴露不必要的受试者身份或虚构随机、发药、退回、销毁和温控记录
- 不得随机、发药、改临床数据、释放隔离品或销毁药品
- 错发药、破盲、受试者安全、批量账物不符和可疑伪造必须升级医学、药物警戒、质量、法规与试验负责人

## Example Requests

- "核对中心药房盘点与IWRS库存"
- "追踪套件从仓库到受试者再到销毁的事件链"
- "生成隔离、偏差、补证与检查准备台账"

