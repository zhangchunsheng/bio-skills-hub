# Evidence-Anchored Teaching Questions (循证教学问题设计)

## Principle

Teaching Questions are **not generic prompts** — each one is pinned to a specific guideline
recommendation or landmark study already presented in the dossier. This makes bedside questioning
reproducible, defensible, and citable, and directly exercises the literature/guideline content the
learner just reviewed. Follow `references/evidence_format.md` for citations and GRADE badges.

## Question item schema

For every question, output this structure (omit Follow-up for Level 1):

```
- **Q:** <question phrased for the learner's level>
- **Anchor:** <guideline/study it tests, with citation + GRADE>
  e.g. "SSC 2021, 1B — initial 30 mL/kg fluid resuscitation in septic shock"
- **Model answer (L1/L2):** <concise, cites the anchor; L3 gives appraisal instead>
- **Pitfall:** <common mistake / misconception learners make>
- **Follow-up (L2/L3):** <deeper probe — comparison, limitation, or gap>
```

## Level-specific design

### Level 1 — competence, guideline-first (domestic)
- Anchor to **domestic guideline first-line** recommendations.
- Question types: diagnostic steps, first-line choice, routine monitoring, red-flag recognition.
- Each answer cites the domestic guideline; mention an international guideline only if it agrees.
- Always provide a model answer; 3–4 questions.

### Level 2 — judgment, comparison (guideline + RCT)
- Anchor to **guideline comparisons** (AAP vs NICE vs domestic vs SSC/ATS/IDSA/ESPGHAN) and **key
  RCTs**.
- Question types: "why X over Y" backed by a trial; risk stratification; when to escalate care.
- Require the learner to justify with **evidence grade**.
- 4–5 questions, each with a Follow-up.

### Level 3 — critical appraisal, research frontier
- Anchor to **specific recent RCT/paper** (last 5 years) already in Evidence Summary.
- Question types: study limitations, generalizability, contradictions across studies,
  translational gap, "what remains unclear".
- No single right answer — assessed by reasoning quality and citation accuracy.
- 4–6 questions; model "answer" is an appraisal, not a fact.

## Reusable question templates (fill per disease)

1. **Diagnosis anchor** — "According to <guideline 202x>, what are the diagnostic criteria for
   <disease>, and which finding is most discriminatory?"
2. **First-line anchor** — "What is the first-line treatment per <domestic guideline 202x>, and
   what is the GRADE-backed evidence supporting it?"
3. **Comparison anchor (L2)** — "Guideline A recommends X (1B) while Guideline B recommends Y
   (2C) for <scenario>. How do you reconcile this for the current patient?"
4. **RCT anchor (L3)** — "The <NAME> trial (Lancet 2023; RCT, High) found ..., but reported
   limitation L. How should that change (or not change) your practice?"
5. **Guideline gap** — "Which aspect of <disease> lacks consensus across guidelines, and what
   evidence would be needed to resolve it?"
6. **Safety/monitoring anchor** — "Per <guideline>, what monitoring is mandatory after starting
   <drug>, and what is the evidence behind each monitored parameter?"
7. **Translational anchor (L3)** — "Biomarker <X> is prognostic in <paper>; at what translational
   stage is it, and what blocks clinical application?"

## Question → Source map (mandatory, end of Teaching Questions)

Close the section with a traceability table proving every question is literature-anchored:

```
| # | 问题主题 | 锚定来源 (指南/研究) | 证据等级 |
| --- | --- | --- | --- |
| 1 | 诊断标准 | 中国指南 202x / SSC 2021 1B | Guideline 1B |
| 2 | 一线治疗 | <NAME> trial, NEJM 2014 | RCT, High |
| 3 | 指南差异 | AAP 2019 vs NICE 2022 | Guideline 1B / 2C |
```

All anchors MUST already appear in Evidence Summary or Guideline Analysis. See
`references/evidence_format.md` §6 for the full traceability rule.
