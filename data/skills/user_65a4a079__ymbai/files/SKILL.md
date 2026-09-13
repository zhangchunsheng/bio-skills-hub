---
name: medical-aesthetics-compliance-advisor
description: "Medical aesthetics compliance advisor for the Chinese medical aesthetics industry. This skill should be used when users need to check institutional compliance, generate platform-compliant marketing content, or produce policy interpretation briefs for medical aesthetics regulations. Covers compliance self-checks across licenses, personnel qualifications, advertising rules, product traceability, and tax regulations; content generation with automatic sensitive-word filtering for Douyin/WeChat/Xiaohongshu; and structured policy brief generation for new regulations. Triggers on requests involving medical aesthetics compliance, content review, regulatory interpretation, institution audits, or marketing content safety checks."
agent_created: true
---

# Medical Aesthetics Compliance Advisor

## Overview

Provide compliance advisory capabilities for the Chinese medical aesthetics (医疗美容) industry. Three core modules: compliance self-check engine, marketing content generator with sensitive-word filtering, and policy interpretation brief generator. Designed for medical aesthetics institutions, self-media creators, and compliance consultants who need rapid, accurate regulatory guidance.

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

Generate platform-compliant marketing content for Douyin, WeChat Official Accounts, and Xiaohongshu with automatic sensitive-word detection and replacement suggestions.

**Workflow:**

1. Determine target platform (douyin / wechat / xiaohongshu), content topic, and target audience.
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

### 3. Policy Brief Generator

Produce structured policy interpretation briefs for new medical aesthetics regulations within 48 hours of publication.

**Workflow:**

1. Input the regulation text, title, or source URL.
2. Run `scripts/policy_brief.py` to extract key provisions and generate a structured brief.
3. Cross-reference with `references/tax_regulations_2026.md` for tax-related regulations.
4. Generate impact analysis covering: affected entities, compliance deadlines, operational changes required, financial impact estimates.
5. Output a policy brief with sections: regulation overview, key changes, impact analysis, compliance checklist, recommended actions.

## Reference Files

Load the following reference files from `references/` as needed:

| File | When to Load |
|------|-------------|
| `compliance_rules.md` | Performing compliance self-checks; need regulatory citations |
| `platform_guidelines.md` | Generating marketing content; checking platform-specific rules |
| `tax_regulations_2026.md` | Interpreting tax-related regulations; 2026 VAT changes |
| `advertising_restrictions.md` | Reviewing advertising materials; checking prohibited content |
| `product_traceability.md` | Auditing product inventory; checking traceability compliance |

## Scripts

### scripts/compliance_check.py

Run institutional compliance audits. Accepts JSON input (file path or stdin) and outputs a risk assessment report with scored findings.

```bash
python scripts/compliance_check.py --input institution_data.json --output report.json
```

### scripts/content_generator.py

Generate platform-compliant content and scan for sensitive words. Accepts platform, topic, and content draft as input.

```bash
python scripts/content_generator.py --platform douyin --topic "玻尿酸注射注意事项" --draft "draft.txt"
```

### scripts/policy_brief.py

Generate structured policy interpretation briefs from regulation text.

```bash
python scripts/policy_brief.py --input regulation.txt --output brief.md
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

## Important Notes

- All regulatory citations include the specific law/regulation name, article number, and effective date.
- Compliance risk scores use a 4-tier system: low (0-30), medium (31-60), high (61-80), critical (81-100).
- Content compliance scores below 80 require manual review before publishing.
- Policy briefs should be reviewed by a licensed legal professional before formal distribution.
- Product traceability checks require valid registration numbers from NMPA (国家药品监督管理局).
