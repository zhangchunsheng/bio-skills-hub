---
slug: pet-medical-local-activity-content-engine-jyc
displayName: "宠物医疗｜本地门店活动内容与转化引擎"
version: 1.0.0
license: "LicenseRef-Proprietary"
summary: "中文宠物医疗与本地生活活动内容引擎，支持可变活动对象、五平台联动、预约到复诊闭环和人工合规审核。"
tags: [宠物医疗, 本地生活, 活动策划, 内容营销]
name: local-business-content-engine
description: "中文本地生活运营与宠物医疗活动内容引擎：根据可变活动对象生成多平台内容、活动方案、预约到复诊转化流程和复盘表。支持疫苗、体检、驱虫、绝育评估、老年宠等服务场景，联动抖音本地推、美团、高德、朋友圈和私域，并强制执行医疗表达、病例隐私、价格、服务承诺和真实性审核。"
metadata:
  category: "宠物医疗 / 本地生活运营 / 活动策划 / 内容营销"
  language: "zh-CN"
  invocation: "$local-business-content-engine"
---

# 宠物医疗｜本地门店活动内容与转化引擎

## 中文命令与分类

- 中文名称：宠物医疗｜本地门店活动内容与转化引擎
- 调用命令：`$local-business-content-engine`
- 分类：宠物医疗 / 本地生活运营 / 活动策划 / 内容营销
- 适用：宠物医院、动物医院及需要本地获客与活动转化的门店

Use this skill to help a local merchant turn a simple shop profile into a one-week customer acquisition package that can be posted, tested, reviewed, and sold as a service.

The user may be:

- A local business owner who needs content to attract nearby customers.
- A content operator selling AI-assisted content packages to merchants.
- A Skill contest participant who needs a practical, non-code workflow with visible business value.

## Output Goal

Produce a complete, reviewable delivery package:

- Shop diagnosis and buyer angle.
- 7-day multi-platform calendar.
- Short-video scripts for Douyin / WeChat Channels.
- Xiaohongshu note drafts.
- WeChat Moments and community posts.
- Private-chat closing SOP.
- Offer / coupon / membership design.
- KPI review table.
- Client-facing delivery note.

Do not promise guaranteed traffic, revenue, ranking, or conversion. Position outputs as testable content and sales assets.

## Variable activity object (required)

The activity object is a variable input, not a fixed product or a hard-coded campaign. Read it from the brief on every run and allow the merchant to change it between campaigns. At minimum, keep these fields together:

- `activity_object`: the current campaign/service object; it may be a string or a structured object.
- `service_scene`: the service being promoted this time.
- `target_segment`: species, age, lifecycle, location, or other audience slice.
- `goal`: the next measurable action, such as inquiry, appointment, arrival, verification, review, or revisit.
- `offer`, `price`, `capacity`, `time_window`: only when the merchant has confirmed them.

For a pet hospital, the selectable service scenes include vaccines, health exams, deworming, spay/neuter assessment, and senior-pet care. The list is extensible; do not assume one of these is always the current activity.

## Pet-medical mode and channel journey

When the brief describes a pet hospital or veterinary service, connect the same activity object across these channels:

- Douyin local push: local content reach, POI/团购 entry, and qualified inquiry.
- Meituan: search/nearby decision, store page, offer, appointment, and verification.
- Gaode: map search, POI accuracy, route and arrival intent.
- Moments: owner/doctor trust, real service scenes, and reminder content.
- Private domain: consultation, appointment confirmation, arrival reminder, review request, and revisit follow-up.

Use this journey as the operating spine: `触达 → 咨询 → 预约 → 到店 → 服务/核销 → 真实评价 → 复诊`. Every stage needs an owner, a user-facing message, a record field, and a next action; external publishing and medical decisions remain human-confirmed.

## Medical expression and safety gates

Before publishing, require human review of medical wording, 病例隐私/脱敏, price and inventory, service scope, appointment terms, and any service promise. Describe process,适用范围,准备事项, and observable service details; do not diagnose, prescribe, set dosage, or infer an outcome from a photo or case snippet.

Never generate or suggest fake reviews, fake scarcity or slots, fabricated cases/metrics, efficacy or cure promises, misleading prices, platform-rule evasion, or coercive selling. Ask the merchant to confirm real availability and policy before an offer, reminder, or “limited” message is posted.

## Workflow

1. Read the merchant profile and the current variable activity object.
2. Clarify the target customer, service scene, purchase trigger, nearby scenario, and next measurable action.
3. Design one weekly campaign theme.
4. Build a platform-specific content matrix:
   - Douyin / WeChat Channels: story-driven short video.
   - Xiaohongshu: search-friendly notes and local decision keywords.
   - Douyin local push / Meituan / Gaode: local reach, search, POI, offer, and arrival intent.
   - WeChat Moments: trust, real scenes, and confirmed offer information.
   - Community/private chat: consultation, appointment, arrival, verification, review, and revisit follow-up.
5. Add medical-expression, privacy, price, service-promise, and brand-safety checks.
6. Generate a review sheet that follows inquiries through appointments, arrivals, verifications, reviews, and revisits.
7. Package the result as a paid deliverable with next-step upsell, without implying guaranteed medical or commercial results.

## Fast Path

When a JSON brief exists, run:

```powershell
python .\local-business-content-engine\scripts\generate_local_business_pack.py --brief .\local-business-content-engine\assets\demo-brief.json --out .\demo-output\local-business-content-pack
```

If no brief exists, ask for only these fields, then proceed:

- Business type and city.
- Current activity object and service scene (replaceable on the next run).
- Target segment and next measurable goal.
- Core offer or best-selling product.
- Confirmed price, capacity, and time window, or mark each as pending merchant review.
- Target customer.
- Main customer pain.
- Unique advantage.
- Call-to-action channel.

## Quality Bar

The package should feel like work a small merchant would actually pay for:

- Specific to the city, customer, product, and nearby consumption context.
- Written in ready-to-post language, not abstract advice.
- Includes private-domain conversion, not only public-platform content.
- Has measurable review fields: views, saves, inquiries, visits, orders, notes.
- Includes safe boundaries: no fake reviews, fake scarcity, medical/legal claims, or platform rule evasion.
- If pet-medical mode is active, includes vaccines, exams, deworming, spay/neuter assessment, senior-pet scenarios, and the full appointment-to-revisit workflow.

## Paid-Service Packaging

Default pricing for the user to sell:

- Starter: 699 CNY, one 7-day content pack for one shop.
- Pro: 2999 CNY, 4 weekly packs plus review and iteration.
- Monthly operator: 5000-12000 CNY/month, weekly content packs plus private-domain scripts and KPI review.

Suggested upsell:

- Turn the best-performing weekly pack into a repeatable shop SOP.
- Add staff shooting checklist and 30-minute training.
- Add monthly review dashboard.

## Contest Submission Angle

For a Skill contest, emphasize:

- Real scenario: local merchants need daily customer acquisition content.
- Practicality: one brief produces a complete weekly operating package.
- Completion: includes script, sample input, sample output, templates, and review tables.
- Innovation: combines public content, private chat, offer design, and KPI review in one Skill.
- Community impact: non-technical users can build useful Skills for real local businesses.
