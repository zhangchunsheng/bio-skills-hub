---
name: medical-aesthetics-compliance-advisor
description: "Medical aesthetics compliance advisor for the Chinese medical aesthetics industry. This skill should be used when users need to check institutional compliance, generate platform-compliant marketing content, or produce policy interpretation briefs for medical aesthetics regulations. Covers compliance self-checks across licenses, personnel qualifications, advertising rules, product traceability, and tax regulations; content generation with automatic sensitive-word filtering for 10 mainstream platforms (Douyin, WeChat, Xiaohongshu, Kuaishou, Shipinhao, Bilibili, Weibo, Zhihu, Toutiao, Baijiahao); and structured policy brief generation for new regulations. Also covers reputation & compliance monitoring of self-media accounts, project-based education content libraries, and violation ruling against advertising laws. Triggers on requests involving medical aesthetics compliance, content review, regulatory interpretation, institution audits, marketing content safety checks, reputation monitoring, education content, or violation ruling."
agent_created: true
---

# Medical Aesthetics Compliance Advisor

## Overview

Provide compliance advisory capabilities for the Chinese medical aesthetics (医疗美容) industry. Six core modules: compliance self-check engine, marketing content generator with sensitive-word filtering, policy interpretation brief generator, reputation & compliance monitor, project education library, and violation ruling. Designed for medical aesthetics institutions, self-media creators, and compliance consultants who need rapid, accurate regulatory guidance.

## 付费能力（X402 微信 Agent Pay）

本 Skill 的正式付费交付物——合规自查报告、政策解读简报、违规裁定结论、深度科普内容库——需通过微信 Agent Pay（X402 协议）完成支付后获取。免费能力（敏感词预检、合规要点口头答疑、法规条款引用）不走支付流程，可直接返回。

> 后端服务须由商户自行部署并对公网可访问，对未支付请求返回 HTTP 402。本 Skill 描述 Agent 侧的调用与支付流程；签名、下单、查单等由后端处理。

### 付费前置检查
调用本 Skill 的付费能力前，检查当前 Agent 是否已安装 `weixinpay` 插件：
- 已安装：可继续提供付费服务。
- 未安装：提示"当前 Agent 暂不支持微信支付付费能力"，终止付费流程，改为提供免费能力或建议用户安装插件。

### 工作流程

#### 第一步：请求资源
向商户服务发起首次请求（注意：不要携带 `X-Out-Trade-No` 头）。
```
POST {SKILL_INVOKE_URL}
Content-Type: application/json
Body: {"query": "用户的查询内容"}
```
将 `{SKILL_INVOKE_URL}` 替换为实际部署的后端地址（示例：`https://your-domain.com/skill/medical-aesthetics-compliance/invoke`）。

#### 第二步：处理 402 响应
若返回 **HTTP 402**，从响应中提取以下两项并妥善保存（二者缺一不可）：
- 响应头 `WeixinPay-Required`：支付码（payment_code）。
- 响应头 `X-Out-Trade-No`：商户订单号。
响应体示例：
```json
{
  "code": "PAYMENT_REQUIRED",
  "message": "需要支付后才能获取内容",
  "WeixinPay": {
    "WeixinPay-Required": "payment_code_xxx",
    "prompt": "本次使用微信支付，请将 WeixinPay-Required 的值作为 paymentCode 交给 weixinpay_pay，以向用户申请支付授权。"
  },
  "out_trade_no": "WX402_20260630120000abcdef123456",
  "amount": "0.01",
  "currency": "CNY"
}
```

#### 第三步：发起支付
将第二步保存的 `WeixinPay-Required` 值作为 `paymentCode`，调用 `weixinpay_pay` 工具向用户申请支付授权：
```
weixinpay_pay(paymentCode = "<WeixinPay-Required 的值>")
```
等待用户确认并完成支付。

#### 第四步：支付成功后获取资源（⚠️ 必须执行）
支付成功后，**必须**重新向同一接口发起请求，并在请求头携带第二步保存的两个值；请求体（Body）与第一步完全一致：
```
POST {SKILL_INVOKE_URL}
Content-Type: application/json
Headers:
  WeixinPay-Required: <第二步保存的支付码>
  X-Out-Trade-No: <第二步保存的订单号>
Body: {"query": "原始查询内容"}
```
成功后返回 **HTTP 200** 及付费内容：
```json
{
  "code": "SUCCESS",
  "message": "付费内容",
  "out_trade_no": "WX402_20260630120000abcdef123456",
  "transaction_id": "4200001234202306300000000001",
  "content": "【付费内容】...",
  "already_fulfilled": false
}
```
> ⚠️ 第四步是最易被遗漏的一步：不携带 `X-Out-Trade-No` 头重试，将永远拿不到付费内容。Body 必须与首次请求一致，仅通过请求头传递订单号与支付凭证。

## Core Capabilities

### 1. Compliance Self-Check Engine

Perform institutional compliance audits by checking license validity, personnel qualifications, advertising compliance, and product traceability against current regulations.

**Workflow:**

1. Collect institution information (JSON input with fields: institution_name, license_number, business_scope, staff_list, advertising_channels, product_inventory).
2. Run `scripts/compliance_check.py` with the institution data to generate a risk score and remediation checklist.
3. Cross-reference findings against `references/compliance_rules.md` for regulatory citations.
4. Check advertising materials against `references/advertising_restrictions.md` for prohibited content.
5. Verify product traceability against `references/product_traceability.md`.
6. Generate a structured compliance report with risk level (low/medium/high/critical), specific violations, regulatory citations, and actionable remediation steps.

**Input format for compliance_check.py:**

```json
{
  "institution_name": "XX医疗美容门诊部",
  "license_number": "PDYXXXXXX",
  "business_scope": ["美容外科", "美容皮肤科", "美容牙科"],
  "staff": [
    {"name": "张医生", "title": "主诊医师", "category": "美容外科", "cert_number": "..."}
  ],
  "advertising_channels": ["douyin", "wechat", "xiaohongshu"],
  "advertising_content": "原广告文案...",
  "products": [
    {"name": "玻尿酸注射液", "batch": "20240101", "registration_number": "..."}
  ]
}
```

### 2. Marketing Content Generator

Generate platform-compliant marketing content for 10 mainstream self-media platforms (Douyin, WeChat Official Accounts, Xiaohongshu, Kuaishou, Shipinhao, Bilibili, Weibo, Zhihu, Toutiao, Baijiahao) with automatic sensitive-word detection and replacement suggestions.

**Workflow:**

1. Determine target platform (douyin / wechat / xiaohongshu / kuaishou / shipinhao / bilibili / weibo / zhihu / toutiao / baijiahao), content topic, and target audience.
2. Load platform-specific rules from `references/platform_guidelines.md`.
3. Generate content draft following platform style guidelines.
4. Run `scripts/content_generator.py` to scan for sensitive words and prohibited expressions.
5. Replace flagged terms with compliant alternatives from the suggestion list.
6. Output final content with a compliance confidence score (0-100).

**Sensitive word categories covered:**
- Absolute superlatives (最, 第一, 唯一)
- Medical efficacy guarantees (包治, 根治, 100%有效)
- Pre/post comparison photos without proper labeling
- Unverified celebrity endorsements
- Off-label use implications
- Price manipulation language (最低价, 破价)

**Platform-specific prohibited words (auto-detected per platform, sourced from PLATFORM_SPECIFIC in content_generator.py):**
- douyin / kuaishou: 加微信, 私聊, 免费做, 9.9元体验, 秒杀, 限时福利 (快手另含: 加快手号, 左下角小黄车, 点击购物车)
- wechat: 点击购买, 立即下单, 扫码购买
- xiaohongshu: 种草, 测评, 体验报告, 对比照, 术前术后
- shipinhao: 加微信, 加微, 私聊, 点击下方链接, 立即预约, 阅读原文
- bilibili: 点击购买, 购买链接, 私聊, 商务合作, 推广, 广告
- weibo: 加微信, 私聊, 代购, 微商, 点击购买, 限时特价
- zhihu: 加微信, 私聊, 点击下方, 购买链接, 推广, 软广
- toutiao / baijiahao: 加微信, 私聊, 点击链接, 立即购买, 免费领取, 扫码

### 3. Policy Brief Generator

Produce structured policy interpretation briefs for new medical aesthetics regulations within 48 hours of publication.

**Workflow:**

1. Input the regulation text, title, or source URL.
2. Run `scripts/policy_brief.py` to extract key provisions and generate a structured brief.
3. Cross-reference with `references/tax_regulations_2026.md` for tax-related regulations.
4. Generate impact analysis covering: affected entities, compliance deadlines, operational changes required, financial impact estimates.
5. Output a policy brief with sections: regulation overview, key changes, impact analysis, compliance checklist, recommended actions.

### 4. Reputation & Compliance Monitor

Monitor self-media accounts (own or competitors) for compliance risks by batch-scanning published content against platform rules and sensitive-word libraries.

**Workflow:**

1. Collect content list (JSON/CSV with fields: platform, post_id, content_text, publish_date).
2. For each item, run `scripts/content_generator.py` with its platform to scan sensitive words and prohibited expressions.
3. Aggregate results: count of violations per platform, severity tier (A/B/C/platform-specific), and repeat offenders.
4. Cross-reference against `references/reputation_rules.md` for account-level risk patterns (e.g., high-frequency导流词, repeated疗效保证).
5. Output a monitor report with per-post findings, account risk score, and prioritized remediation actions.

**Input format:**

```json
{
  "account": "机构官方抖音号",
  "posts": [
    {"platform": "douyin", "post_id": "p001", "content_text": "原文案...", "publish_date": "2026-07-01"}
  ]
}
```

> Note: `scripts/reputation_monitor.py` and `references/reputation_rules.md` are planned modules — implement them to enable batch automation; manual execution via content_generator.py is supported now.

### 5. Project Education Library

Generate compliant science-popularization (科普) content and FAQ for specific medical aesthetics procedures, avoiding efficacy guarantees and before/after comparisons.

**Workflow:**

1. Identify target procedure (e.g., 玻尿酸, 热玛吉, 双眼皮).
2. Load the procedure template from `references/project_kb.md` (principle, suitable candidates, risks, aftercare).
3. Draft education content following the template, explicitly avoiding level-A/B sensitive words.
4. Run `scripts/content_generator.py` to verify compliance of the draft.
5. Output a structured 科普 article + FAQ block with a compliance confidence score (0-100).

> Note: `scripts/edu_content.py` and `references/project_kb.md` are planned modules — implement them to enable one-click generation; manual drafting + content_generator.py check works now.

### 6. Violation Ruling

Rule on which regulation/article a penalized case violated, given the case description or penalty decision text.

**Workflow:**

1. Input the violation description or penalty decision text.
2. Extract key facts (claimed efficacy, compared results, unqualified endorsement, price inducement, etc.).
3. Match facts against `references/violation_laws.md` (广告法, 医疗广告管理办法, 反不正当竞争法 clause library).
4. Output the specific violated articles, penalty basis, and remediation advice.
5. (Optional) Cross-check with `references/advertising_restrictions.md` for prohibited-content mapping.

> Note: `scripts/violation_judge.py` and `references/violation_laws.md` are planned modules — implement them to enable auto-ruling; manual citation via the references works now.

## Reference Files

Load the following reference files from `references/` as needed:

| File | When to Load |
|------|-------------|
| `compliance_rules.md` | Performing compliance self-checks; need regulatory citations |
| `platform_guidelines.md` | Generating marketing content; checking platform-specific rules |
| `tax_regulations_2026.md` | Interpreting tax-related regulations; 2026 VAT changes |
| `advertising_restrictions.md` | Reviewing advertising materials; checking prohibited content |
| `product_traceability.md` | Auditing product inventory; checking traceability compliance |
| `reputation_rules.md` | Reputation monitoring; account-level risk patterns (planned) |
| `project_kb.md` | Procedure education templates; 科普 content library (planned) |
| `violation_laws.md` | Violation ruling; advertising-law clause library (planned) |

## Scripts

### scripts/compliance_check.py

Run institutional compliance audits. Accepts JSON input (file path or stdin) and outputs a risk assessment report with scored findings.

```bash
python scripts/compliance_check.py --input institution_data.json --output report.json
```

### scripts/content_generator.py

Generate platform-compliant content and scan for sensitive words. Accepts platform, topic, and content draft as input.

Supported platforms (--platform): douyin, wechat, xiaohongshu, kuaishou, shipinhao, bilibili, weibo, zhihu, toutiao, baijiahao

```bash
python scripts/content_generator.py --platform douyin --topic "玻尿酸注射注意事项" --draft "draft.txt"
```

### scripts/policy_brief.py

Generate structured policy interpretation briefs from regulation text.

```bash
python scripts/policy_brief.py --input regulation.txt --output brief.md
```

### scripts/reputation_monitor.py

Batch-scan self-media posts for compliance risks and output a monitor report. (Planned module — implement to enable batch automation.)

```bash
python scripts/reputation_monitor.py --input posts.json --output monitor.json
```

### scripts/edu_content.py

Generate compliant 科普 content and FAQ for a given procedure. (Planned module.)

```bash
python scripts/edu_content.py --project "玻尿酸" --output edu.md
```

### scripts/violation_judge.py

Rule which regulation/article a penalized case violated. (Planned module.)

```bash
python scripts/violation_judge.py --input case.txt --output ruling.md
```

## Usage Examples

**Example 1: Compliance Audit**
> "帮我们机构做一次合规自查，这是我们的基本信息和广告文案"

Load `references/compliance_rules.md` and `references/advertising_restrictions.md`, collect institution data, run `compliance_check.py`, generate report.

**Example 2: Content Generation**
> "帮我写一条抖音短视频脚本，主题是热玛吉术后护理"

Load `references/platform_guidelines.md`, run `content_generator.py` with platform=douyin, review output for compliance.

**Example 3: Policy Interpretation**
> "2026年医美机构增值税新规出来了，帮我出一份解读报告"

Load `references/tax_regulations_2026.md`, run `policy_brief.py` with the regulation text, generate structured brief.

**Example 4: Reputation Monitoring**
> "帮我扫一遍我们抖音号和竞品最近发的20条内容，看哪些踩线了"

Load `references/reputation_rules.md` (planned), collect post list, run content_generator.py per post, aggregate into monitor report.

**Example 5: Education Content**
> "给我写一版玻尿酸的科普文案和常见问答，要合规"

Load `references/project_kb.md` (planned), draft per template, run content_generator.py to verify.

**Example 6: Violation Ruling**
> "这家机构被罚了，说违反广告法，帮我判定到底踩了哪条"

Load `references/violation_laws.md` (planned), extract facts, match clauses, output violated articles + penalty basis.

## Important Notes

- All regulatory citations include the specific law/regulation name, article number, and effective date.
- Compliance risk scores use a 4-tier system: low (0-30), medium (31-60), high (61-80), critical (81-100).
- Content compliance scores below 80 require manual review before publishing.
- Policy briefs should be reviewed by a licensed legal professional before formal distribution.
- Product traceability checks require valid registration numbers from NMPA (国家药品监督管理局).
- 付费交付物（合规自查报告、政策解读简报、违规裁定结论、深度科普内容库）必须走「付费能力（X402 微信 Agent Pay）」章节的 402 流程：处理 402 → 调用 `weixinpay_pay` → 带 `X-Out-Trade-No` 头重试。**第四步重试不可省略**，否则无法取回付费内容。后端服务须真实部署并返回合规 402（参考 mch-demo）。
