---
name: team-medical-device-udi-label-change-control
description: "Control medical-device UDI and label changes across device families, models, packaging levels, UDI-DIs, production identifiers, issuing agencies, regulatory registrations, label artwork, symbols, languages, barcodes, master data, manufacturing sites, bills of material, validation, inventories, distribution, UDI database submissions, acknowledgements, change orders, approvals, and effective dates. Use to identify evidence-backed identifier, artwork, barcode, master-data, inventory, market, submission, or cutover gaps without designing labels, validating medical claims, releasing product, or submitting regulatory records. This Pay Skill provides free scope validation, then requires verified payment before releasing the full deliverable."
tags: [医疗器械, UDI, 标签变更, 产品追溯]
version: 2.0.2
capability: medical_device_udi_label_change_control
pricing:
  model: per_call
  amount_fen: 599
---

# 医疗器械UDI标签变更控制台

## Objective

Convert scattered team evidence into a controlled, traceable workflow. Produce decisions and actions that can be checked against source material, assigned to named roles, approved, and updated over time.

## Team Roles

Use the user's real role names when available. Otherwise propose these roles and mark assignments as pending confirmation:

- 器械法规
- 质量体系
- 标签与主数据
- 生产供应链
- 变更审批人

Never silently assign a person, approval, deadline, or commitment.

## Required Inputs

- 器械族型号包装层级、UDI-DI/PI、发码机构和适用市场注册
- 标签图稿符号语言条码、BOM包材、主数据、验证和变更单
- 工厂库存批次、分销切换、UDI数据库提交回执、生效日和审批

Start with available material. Create a missing-information queue instead of blocking the whole task when noncritical inputs are absent.

## Pay Skill Contract

Price: `CNY 5.99` per paid invocation. Skill version: `2.0.2`. Product ID: `SP2608160147`.

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
3. 统一器械型号包装层级市场和UDI主键及版本
4. 映射注册变更到图稿条码主数据BOM验证库存和数据库提交
5. 分类错码、版本冲突、未验证、旧标库存、提交无回执和切换缺口
6. Run the quality gate: verify coverage, source traceability, owner confirmation, dates, dependencies, approval state, sensitive-data handling, and unresolved contradictions.
7. Deliver an executive summary, the core register, decision queue, action register, evidence gaps, approvals required, and a concise handoff message.

## Core Register

Use this minimum schema:

`风险ID | 器械/型号/包装层级 | 市场/注册版本 | UDI-DI/PI规则 | 标签图稿/条码 | 主数据/BOM | 验证 | 旧标库存 | 数据库提交/回执 | 生效/切换日 | 风险类型 | 证据 | 责任人 | 审批 | 状态`

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

- 不得虚构器械注册、UDI、验证、医学声明、数据库提交、回执或产品状态
- 不得设计批准标签、验证临床或医学声明、释放产品、报送监管数据库
- 可能影响患者安全、错标错码、无效条码、大量旧标库存和市场中断必须升级质量、法规、医学安全、法务与管理层

## Example Requests

- "建立器械型号包装层级与UDI标签版本矩阵"
- "找出条码主数据、BOM、库存和数据库提交不一致"
- "生成验证、旧标隔离、切换、提交准备与审批台账"

