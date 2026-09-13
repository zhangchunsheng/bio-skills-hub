# Evidence & Citation Format (文献与指南板块规范)

This reference standardizes how literature and guidelines are presented across the dossier so
that every claim is traceable, every recommendation carries a grade, and Teaching Questions can
cite a concrete anchor. Use it in **Evidence Summary**, **Guideline Analysis**, and **Teaching
Questions** (and anywhere a claim depends on literature).

## 1. Inline citation style

Use a compact inline citation wherever a statement depends on a source. Format:
`(Issuer/Author Year; Evidence type, Grade)`.

Examples:
- Guideline: `(SSC 2021; Guideline, GRADE 1B)`
- RCT: `(ARISE trial, N Engl J Med 2014; RCT, High)`
- Meta-analysis: `(XXX meta-analysis, JAMA 2022; Meta, Moderate)`
- Real-world study: `(YYY cohort, Chest 2021; Observational, Low)`
- Mechanistic / preclinical: `(ZZZ mouse model, Cell 2023; Preclinical)`
- Expert consensus: `(AAP 2019; Consensus)`

If a claim is well-established physiology (not a contested recommendation), no citation is needed,
but contested or guideline-driven statements MUST be cited.

## 2. Evidence-level vocabulary

Always label the evidence type:
- `RCT` — randomized controlled trial
- `Meta` / `Systematic review` — pooled evidence
- `Guideline` — issued by a named body with year
- `RWS` / `Observational` — cohort / case-control / registry
- `Preclinical` — animal / in vitro / mechanistic
- `Consensus` / `Expert opinion` — lowest tier

## 3. GRADE badge (for guideline recommendations)

When quoting a guideline recommendation, append its GRADE strength + quality:
- `1` = strong recommendation; `2` = weak / discretionary
- `A`/`B`/`C`/`D` = evidence quality High / Moderate / Low / Very low
- Examples: `1B` (strong, moderate-quality evidence), `2C` (weak, low-quality evidence).

State the badge exactly as the guideline issued it; if the guideline uses a different system
(e.g., AAP strength-of-recommendation), translate to GRADE-equivalent and note the original.

## 4. Guideline comparison table

Use this table in **Guideline Analysis** so differences are explicit and citable:

```
| 维度 | 中国指南 202x | AAP 202x | NICE 202x | ESPGHAN/ATS/IDSA/SSC | 是否共识 |
| --- | --- | --- | --- | --- | --- |
| 一线治疗 | ... | ... | ... | ... | ✅/⚠️ |
| 关键差异 | ... | ... | ... | ... | 说明 |
```

- Fill ONLY from verified guideline text. Mark `未检索到` where no guideline addresses the row.
- For each divergent row, add a one-line explanation citing the relevant recommendation (with GRADE).
- End the section with a "Consensus gaps" bullet: which dimensions lack agreement and why.

## 5. Evidence-Summary entry format

Each key study/guideline in **Evidence Summary** should be a short block:

```
- **[Label]** <Study/Guideline name> (<cite>; <Evidence type>, <Grade>)
  - Question/Population: ...
  - Finding: ...
  - Relevance to this case/teaching point: ...
  - Limitation (Level 2+): ...
```

This block becomes the **anchor pool** that Teaching Questions draw from.

## 6. Traceability rule (critical — links literature to questions)

- Every Teaching Question MUST reference at least one anchor that already appears in **Evidence
  Summary** or **Guideline Analysis** (no orphan citations).
- The anchor's label/citation must match exactly what was written earlier in the dossier.
- If a question has no literature support, either drop it or explicitly tag it
  `（概念核查，无外部文献支撑）`.
- The dossier MUST end Teaching Questions with a **Question → Source map** (see
  `references/teaching_questions.md`) so a reviewer can verify every question's basis.
