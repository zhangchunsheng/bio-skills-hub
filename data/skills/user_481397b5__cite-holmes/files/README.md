# Cite Holmes 🔍

![icon](assets/icon-512.png)

**Deep research that interrogates its own sources.**

Every AI research report you've ever read had a dirty secret: some of those polished references were probably fabricated. [A Nature news analysis suggests tens of thousands of 2025 publications might include invalid AI-generated references](https://www.nature.com/articles/d41586-026-00969-z). [GPTZero scanned 4,841 NeurIPS 2025 submissions; as independently reported, at least 100 hallucinated citations were found across 51 accepted papers](https://medium.com/@ljingshan6/100-fake-citations-just-slipped-through-neurips-2025-peer-review-5f34f4436560).

Cite Holmes is a deep-research skill with a badge and a magnifying glass: it researches like any deep-research agent — then **arrests its own citations before you can cite them**.

![demo](assets/demo.gif)

*(Demo is real output: 8 references, 3 deliberately planted fabrications — a fake DOI, a dead URL, and a no-URL citation. All 3 were caught and excluded; the 5 real ones passed. Measured: **7.7 s for all 8** — 4.2 s of pure network checks, the rest is deliberate throttling.)*

Reproduce it yourself — the planted-fakes file ships with the repo:

```bash
python scripts/verify_refs.py --refs examples/demo_refs.json
```

## How it works

Five phases, two modes:

| Phase | What happens |
|---|---|
| **CALIBRATE** | Asks you 3–5 sharp questions first (scope, timeframe, audience) — prevents researching the wrong question |
| **PLAN** | Breaks your question into 3–7 sub-questions with a search budget |
| **SEARCH** | Diamond-shaped iterative search: broad → narrow → gap-filling, Chinese + English, source-tier pyramid |
| **VERIFY** | Two layers: semantic check (does the source actually support the claim?) + mechanical check (reachability, domain authority, field completeness, dedup) |
| **SYNTHESIZE** | Report where every conclusion carries a confidence grade — 🟢 two independent sources / 🟡 single authority / 🔴 contested |

Modes: **QUICK** (single fact-check, ≤6 searches, no interrogation) vs **FULL** (open-ended research, ≤15 searches, calibration mandatory).

## The five citation verdicts

| Verdict | Meaning |
|---|---|
| `verified` | Reachable + authoritative tier (official/journal/preprint/major media) + complete fields — may support conclusions |
| `partial` | Reachable but community/blog tier or missing fields — downgraded use |
| `unreachable` | 404/timeout (≠ nonexistent — flagged for human review) |
| `invalid` | Malformed or missing URL/DOI — never enters the report |
| `unverified` | Not checked — never masquerades as verified |

## v1.2: medical evidence mode + bibliography export

```bash
# medical profile: journal-tier sources extend to Cochrane/BMJ/ClinicalTrials/
# NMPA/CDC/NICE/万方/ChiCTR; community-tier sources get an explicit
# "unfit for medical conclusions" warning
python scripts/verify_refs.py --refs refs.json --profile medical

# PMID-only references work out of the box — and every PubMed URL gets its
# PMID existence-checked via NCBI E-utilities. A fabricated PMID is caught
# even though PubMed's own page happily returns 2xx for it.

# export: verified-only BibTeX (straight into your paper) + full audit CSV
python scripts/verify_refs.py --refs refs.json --export bibtex,csv
```

Try the medical demo — real tocilizumab/sJIA references from PubMed, plus one
planted fake PMID and one planted duplicate (both caught):

```bash
python scripts/verify_refs.py --refs examples/medical_refs.json --profile medical --export bibtex,csv
```

## Install

**OpenClaw users (ClawHub — versioned, auto-updatable):**

```bash
clawhub search cite-holmes        # find it on the registry
clawhub install @docsor1212/cite-holmes
```

**Any Agent Skills-compatible agent** (Claude Code, Codex, Cursor, Gemini CLI, ZCode):

```bash
git clone https://github.com/docsor1212/cite-holmes.git ~/.claude/skills/cite-holmes
```

**China mirror (SkillHub 腾讯)**: <https://skillhub.cn/skills/cite-holmes> — fast downloads inside China, 中文说明.

## Usage

Just talk to your agent — it triggers automatically:

```
> deep research: what changed in the agent-skills ecosystem this year?
> is it true that NeurIPS 2025 papers contained 100+ hallucinated citations?
```

Or use the verifier standalone on any reference list:

```bash
python scripts/verify_refs.py --refs research_refs.json --out report.md
# offline structural check / strict CI mode
python scripts/verify_refs.py --refs refs.json --offline
python scripts/verify_refs.py --refs refs.json --strict
```

## What it won't catch (honest limits)

- A fabricated citation that points to a **real, live, plausible page** passes the mechanical check. The semantic layer (the model judging whether the source actually supports the claim) may catch it — it is model judgment, not a guarantee.
- `unreachable` ≠ fake: pages behind login walls or bot-blocking are flagged for human review, not condemned.
- The planted fakes in our demo are exactly the catchable types (dead URL / fake DOI / missing URL). We are not claiming it catches everything.

## Why not just use deep research / a citation checker?

- Deep-research skills **research more** but trust their own citations.
- Standalone citation checkers verify but don't research.
- Cite Holmes does both in one flow: **every reference in every report is machine-checked before it reaches you.**

Zero dependencies (pure Python stdlib), cross-platform (Windows/Linux/macOS), MIT license.

## CiteScore — every report carries a grade

Each verification report opens with a **CiteScore**: a 0-100 confidence score
(verified +10 / partial +4 / unreachable 0 / unverified −2 / invalid −8,
normalized by reference count) with an A–D grade. Screenshot it, quote it,
or gate your CI on it (`--strict`).

## What's new

- **v1.3.0** — CiteScore scorecard in every report (Markdown + JSON), official
  icon, `tests/` regression suite (offline golden + medical profile + exports).
- **v1.2.0** — medical evidence mode (`--profile medical`), PMID verification
  via NCBI E-utilities, BibTeX/CSV bibliography export, 3-key dedup
  (URL/DOI/PMID).

## License

MIT © DoctorQ Lab
