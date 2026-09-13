---
name: caf-curfew-cn
description: Estimate caffeine remaining at bedtime and give a brief, conservative drinking decision. Use when a user asks in Chinese or English whether they can still drink coffee, tea, milk tea, cola, cold brew, or an energy drink today; whether an afternoon drink may affect sleep; what time to stop caffeine; or how much caffeine may remain by bedtime. Apply the safety gate before any calculation. Do not use for diagnosis, treatment, emergencies, or a personalized medical dose.
license: LicenseRef-All-Rights-Reserved
metadata:
  version: "1.0.0"
  slug: "caf-curfew-cn"
  displayName: "咖了吗｜今晚还能喝吗"
  summary: "根据饮用时间、咖啡因含量和就寝时间，估算睡前残留并给出保守建议。"
  tags: ["咖啡因", "睡眠", "咖啡", "生活方式"]
  homepage: "https://github.com/daijx66-crypto/caf-skills"
  skillhub:
    category: "life-service"
---

# 咖了吗｜今晚还能喝吗

Estimate bedtime caffeine residue, then give one conservative action. Treat every number as an estimate, not a measurement of the user's body.

## Safety gate

Run this gate before asking routine intake questions or calculating.

1. If the user reports chest pain, fainting, severe palpitations, confusion, seizure-like symptoms, or severe breathing difficulty, stop. Advise urgent medical help or local emergency services. Do not discuss an allowable caffeine amount.
2. If the user is pregnant or breastfeeding, a minor, taking medication, or has heart rhythm problems, liver disease, epilepsy, severe anxiety, or an insomnia disorder, do not calculate a personalized "safe dose." Give a conservative caffeine-free suggestion and recommend asking a qualified clinician.
3. If the user mentions pure caffeine powder or liquid, or mixing energy drinks with alcohol, strongly discourage it. Do not help optimize a dose.

Read `references/evidence-and-safety.md` when a safety signal appears or the user asks for evidence.

## Minimum inputs

Collect only what is missing:

1. Expected bedtime tonight.
2. Caffeine already consumed today: drink, approximate time, and amount or cup size.
3. If evaluating another drink, its type or labeled caffeine amount.

Ask like a personal assistant, not a form. Resolve relative times into absolute ISO 8601 timestamps with an explicit `Z` or `+/-HH:MM` offset before calculation. If the user's timezone is unknown and affects the result, ask once.

## Estimate drink caffeine

Prefer, in order:

1. The user's package label or explicit milligrams.
2. Current official information for the exact brand and cup size.
3. The generic estimates in `references/drink-estimates.md`.

Always mark category values as approximate. Never imply that cafe preparation is exact.

## Calculate

From this skill directory, pass JSON through stdin:

```bash
node scripts/calculate-caffeine.mjs <<'EOF'
{
  "nowIso": "2026-07-19T15:00:00+08:00",
  "bedtimeIso": "2026-07-19T23:30:00+08:00",
  "halfLifeHours": 5,
  "intakes": [
    { "label": "morning latte", "drankAt": "2026-07-19T10:00:00+08:00", "caffeineMg": 120 }
  ],
  "candidate": {
    "label": "small coffee now",
    "drankAt": "2026-07-19T15:00:00+08:00",
    "caffeineMg": 80
  }
}
EOF
```

Use a 5-hour half-life by default. Use 7 hours only as a conservative scenario when the user describes sensitivity or asks for a cautious estimate. Do not claim either value is the user's true metabolism.

The script reports current residue, the candidate drink's projected bedtime residue, projected total residue, and a product heuristic:

- `low`: projected residue below 30 mg.
- `medium`: 30–80 mg.
- `high`: above 80 mg.

These bands are communication aids, not clinical thresholds. Also consider dose, timing, uncertainty, and the user's own sleep response.

## Answer contract

Default to three short parts:

```text
One decision.

One reason. One action.
```

Use decisions such as:

- 可以喝一点
- 悠着点
- 今天不建议再喝咖啡因了

Prefer one actionable alternative: half a serving, decaf, caffeine-free, or moving the drink earlier. Say "可能影响睡眠" or "睡眠风险偏高". Never say "今晚一定失眠", "精准代谢", "安全剂量", or "医学诊断".

Only expand when asked. Then show the input estimate, time to bedtime, projected bedtime residue, half-life assumption, and uncertainty.

## Failure behavior

- Bedtime unknown: ask for it; do not calculate.
- Timestamp lacks an explicit offset: resolve it before running the script.
- Drink amount unknown: give a range or ask for cup size; do not invent precision.
- Script error or unavailable Node.js: explain what is missing and give only a qualitative, conservative suggestion.
- Conflicting information: use the more conservative interpretation and name the uncertainty.

## Boundaries

- Do not diagnose caffeine sensitivity, insomnia, anxiety, or a heart condition.
- Do not create medication-interaction guidance.
- Do not promise sleep outcomes.
- Do not silently store intake history, schedule reminders, or write to external systems.
