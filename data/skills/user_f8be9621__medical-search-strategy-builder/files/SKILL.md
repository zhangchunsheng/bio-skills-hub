---
name: medical-search-strategy-builder
description: >
  Build structured medical literature search strategies from natural language research questions
  using PICO/PEO frameworks. Supports PubMed, Embase, Cochrane Library, Web of Science, and arXiv.
  Use when: the user asks to construct search strings, build search strategies for systematic reviews,
  convert research questions to database queries, mentions PICO/PEO, or needs PubMed/Embase/Cochrane
  search syntax. Supports both Chinese and English input.
  NOT for: performing actual database searches, downloading papers, or full systematic review execution.
metadata:
  openclaw:
    emoji: "🔍"
    version: "1.0.0"
    author: "MedPaperHunter"
    license: "MIT"
    requires:
      bins: ["python3"]
    tags:
      - medical
      - systematic-review
      - search-strategy
      - pico
      - pubmed
      - evidence-based-medicine
---

# Medical Search Strategy Builder

Build structured medical literature search strategies from natural language research questions using PICO/PEO frameworks. Generates database-specific search strings for PubMed, Embase, Cochrane Library, Web of Science, and arXiv.

## When to Use

- User asks to **construct search strings** or **build search strategies**
- User mentions **PICO**, **PEO**, **systematic review**, or **literature search**
- User needs **PubMed**, **Embase**, **Cochrane**, **Web of Science**, or **arXiv** search syntax
- User wants to convert a **research question** into **database queries**
- User mentions **MeSH terms**, **search strategy**, or **search string construction**
- Input can be in **Chinese or English**

## Workflow

### Step 1: Analyze the Research Question

1. Identify the research question from the user's input
2. Detect the language (Chinese or English)
3. Determine the appropriate framework:
   - **PICO** (Population, Intervention, Comparison, Outcome) → for interventional/therapeutic research
   - **PEO** (Population, Exposure, Outcome) → for observational/etiological research

**Framework selection keywords:**

| PICO (Interventional) | PEO (Observational) |
|---|---|
| efficacy, effectiveness, treatment, therapy, intervention, randomized, trial, drug, surgery, comparison, vs, placebo | risk, association, incidence, prevalence, cause, etiology, cohort, case-control, prognostic, mortality, exposure, observational |

### Step 2: Extract PICO/PEO Concepts

For each dimension, identify:

| Dimension | Description | Example |
|---|---|---|
| **P** (Population) | Target patient group or disease | "Type 2 Diabetes" |
| **I** (Intervention) | Treatment, drug, or procedure | "GLP-1 Receptor Agonists" |
| **C** (Comparison) | Control or comparator | "Metformin" |
| **O** (Outcome) | Result or endpoint | "HbA1c reduction" |
| **E** (Exposure) | Risk factor or exposure (PEO only) | "smoking" |

For each concept, collect three types of search terms:

1. **MeSH/Subject Headings** — standardized controlled vocabulary (highest precision)
2. **Free-text terms** — natural language synonyms (highest recall)
3. **Truncated variants** — wildcard forms using `*` (e.g., `diabet*`)

### Step 3: Validate Concepts

Each concept MUST have:
- A non-empty name
- At least one search term (MeSH, free-text, or truncated)
- Ideally 3+ search terms total for adequate recall

### Step 4: Generate Database-Specific Strategies

Use the syntax rules for each target database. See [references/database-syntax.md](references/database-syntax.md) for detailed syntax guides.

**Quick reference:**

| Database | MeSH Field | Free-text Field | Boolean | Wildcard |
|---|---|---|---|---|
| PubMed | `"term"[MeSH]` | `term[Title/Abstract]` | AND, OR, NOT | `*` |
| Embase | `'term'/exp` | `'term':ti,ab` | AND, OR, NOT | `*` |
| Cochrane | `MeSH descriptor: [term] explode all trees` | `"term":ti,ab,kw` | AND, OR, NOT | `*` |
| Web of Science | `TS=("term")` | `TS=("term")` | AND, OR, NOT | `*` |
| arXiv | `ti:"term"` / `abs:"term"` | `ti:"term"` / `abs:"term"` | AND, OR, ANDNOT | `*` |

### Step 5: Format Output

Generate a structured Markdown report containing:
1. Research question analysis (original question, framework, research type)
2. PICO/PEO concept breakdown table
3. Search term table (MeSH, free-text, truncated terms per concept)
4. Database-specific search strategies (in code blocks)
5. Validation and optimization tips

## Output Format

```markdown
## Research Question Analysis
**Original question**: [user's question]
**Research type**: [interventional/observational]
**Framework**: [PICO/PEO]

### PICO/PEO Breakdown
| Dimension | Content |
|-----------|---------|
| P (Population) | [concept name]: [key terms] |
| I (Intervention) | [concept name]: [key terms] |
| C (Comparison) | [concept name]: [key terms] |
| O (Outcome) | [concept name]: [key terms] |

## Search Strategies

### PubMed
\```pubmed
("Diabetes Mellitus, Type 2"[MeSH] OR "type 2 diabetes"[Title/Abstract])
AND
("Metformin"[MeSH] OR metformin[Title/Abstract])
\```

### Embase
\```embase
#1 P: ('diabetes mellitus, type 2'/exp OR 'type 2 diabetes':ti,ab)
#2 I: ('metformin'/exp OR 'metformin':ti,ab)
#Final: #1 AND #2
\```
```

## Common MeSH Terms Quick Reference

See [references/common-mesh-terms.md](references/common-mesh-terms.md) for the full lookup table.

| Chinese Term | MeSH Term |
|---|---|
| 2型糖尿病 | Diabetes Mellitus, Type 2 |
| 高血压 | Hypertension |
| 心力衰竭 | Heart Failure |
| 心肌梗死 | Myocardial Infarction |
| 肿瘤/癌症 | Neoplasms |
| 随机对照试验 | Randomized Controlled Trial as Topic |
| 系统评价 | Systematic Review as Topic |
| 荟萃分析 | Meta-Analysis as Topic |
| 肥胖 | Obesity |
| 哮喘 | Asthma |
| 抑郁症 | Depressive Disorder |
| 冠心病 | Coronary Disease |
| 脑卒中 | Stroke |
| 慢性肾病 | Chronic Kidney Disease |
| COVID-19 | COVID-19 |
| 心房颤动 | Atrial Fibrillation |

## Important Notes

- **MeSH terms improve precision**; free-text terms improve recall. Always use both.
- **Phrase searching**: Multi-word terms should be quoted (e.g., `"type 2 diabetes"`)
- **Truncation**: Use `*` to capture word variants (e.g., `diabet*` matches diabetes, diabetic, diabetology)
- **Boolean operators** must be UPPERCASE in all databases
- **arXiv** does not support MeSH — all terms are treated as free-text
- **Embase** uses Emtree (not MeSH) — terms may differ from PubMed
- For systematic reviews, consider adding methodology filters (e.g., `"Randomized Controlled Trial as Topic"[MeSH]`)
- Always validate search strategies by checking result counts and relevance in the target database
