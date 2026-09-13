# Medical Search Strategy Builder

A structured medical literature search strategy builder that converts natural language research questions into database-specific search strings using PICO/PEO frameworks.

## Features

- **PICO/PEO Framework Support**: Automatically suggests the appropriate framework based on research question analysis
- **Multi-Database Coverage**: Generates search strategies for PubMed, Embase, Cochrane Library, Web of Science, and arXiv
- **Bilingual Support**: Handles both Chinese and English research questions
- **MeSH Term Lookup**: Built-in common MeSH terms quick reference table
- **Validation**: Concept validation and search strategy optimization tips

## Supported Databases

| Database | MeSH Support | Field Tags | Wildcard |
|---|---|---|---|
| PubMed | ✅ MeSH | `[MeSH]`, `[Title/Abstract]` | `*` |
| Embase | ✅ Emtree | `/exp`, `:ti,ab` | `*` |
| Cochrane Library | ✅ MeSH | `explode all trees`, `:ti,ab,kw` | `*` |
| Web of Science | ❌ | `TS=`, `TI=`, `AU=` | `*` |
| arXiv | ❌ | `ti:`, `abs:`, `all:` | `*` |

## Installation

This skill follows the [Agent Skills open standard](https://agentskills.io/).

### Via SkillHub (China mirror, recommended for users in China)

```bash
skillhub install medical-search-strategy-builder
```

### Via ClawHub (international)

```bash
npx clawhub install medical-search-strategy-builder
```

## Directory Structure

```
medical-search-strategy-builder/
├── SKILL.md                              # Core skill definition (metadata + instructions)
├── README.md                             # This file
├── references/
│   ├── database-syntax.md                # Detailed syntax guide for each database
│   ├── common-mesh-terms.md              # MeSH terms quick reference table
│   └── validation-checklist.md           # Search strategy validation checklist
└── scripts/                              # (Reserved for future automation scripts)
```

## Usage

Once installed, this skill is automatically activated when you ask to build search strategies for medical literature. Example prompts:

- "帮我构建一个关于二甲双胍治疗2型糖尿病的PubMed检索式"
- "Build a PICO search strategy for: GLP-1 agonists vs metformin for type 2 diabetes"
- "Convert this research question into Embase and Cochrane search strings"
- "我需要一个系统评价的检索策略，研究问题是..."

## PICO/PEO Frameworks

### PICO (Interventional Research)

| Dimension | Description |
|---|---|
| **P** (Population) | Target patient group or disease |
| **I** (Intervention) | Treatment, drug, or procedure |
| **C** (Comparison) | Control or comparator |
| **O** (Outcome) | Result or endpoint |

### PEO (Observational Research)

| Dimension | Description |
|---|---|
| **P** (Population) | Target population |
| **E** (Exposure) | Risk factor or exposure |
| **O** (Outcome) | Result or endpoint |

## License

MIT

## Author

MedPaperHunter Team
