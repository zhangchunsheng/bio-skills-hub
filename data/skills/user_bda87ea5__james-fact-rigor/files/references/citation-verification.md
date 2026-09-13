# Citation and Source Verification Rules

## Core Principle

A citation you cannot verify is not a citation — it is a hallucination risk. Every paper, report, law, standard, or dataset referenced in output must be located and confirmed before it appears in the final text.

## What Must Be Verified

Every citation must have:

1. **Title** — exact, not paraphrased from memory
2. **Authors** — at least the first author; full author list preferred
3. **Year** — publication year; for preprints, the submission year
4. **Venue** — journal name, conference name, publisher, or repository
5. **Identifier** — DOI, arXiv ID, PMID, ISBN, or URL
6. **Relevance** — the cited source actually supports the specific claim it is attached to

If any of items 1-5 cannot be confirmed, the citation does not go into the output.

## Verification Process

### For academic papers:

1. Search for the paper by title on Google Scholar, Semantic Scholar, or arXiv.
2. Confirm title, authors, year, and venue match what you intend to cite.
3. Obtain a DOI or arXiv ID. Do not construct these from memory — always copy from the source page.
4. If possible, read the relevant section to confirm it supports the claim you are attaching it to.
5. Record the access date.

### For books:

1. Confirm title, author(s), edition, publisher, year, and ISBN.
2. If citing a specific page or chapter, verify the reference.
3. Edition matters. Page numbers differ across editions.

### For laws, regulations, and standards:

1. Use official sources: government websites, official gazettes, standards body databases.
2. Record the full citation: law name, section/article number, effective date, jurisdiction.
3. Note whether the law has been amended or superseded.

### For web sources:

1. Use the full URL.
2. Record the access date (web pages change or disappear).
3. Prefer primary sources over secondary reporting.
4. If a source is paywalled, note this and seek an open-access version or secondary confirmation.

### For datasets:

1. Record dataset name, version, publisher/provider, and access date.
2. If the data has been updated, specify which version or download date you used.
3. Note the license if relevant.

## Source Hierarchy

Use the most authoritative source available:

| Rank | Source type | Examples |
|---|---|---|
| 1 | Primary research | Original papers, official reports, raw data, official filings, laws/regulations text |
| 2 | Peer-reviewed secondary | Review articles, meta-analyses, textbooks |
| 3 | Reputable institutions | WHO, CDC, IMF, World Bank, central banks, national statistics agencies |
| 4 | Established journalism | Reuters, AP, Bloomberg, FT, WSJ, Nature/Science news |
| 5 | Domain-specific publications | Industry reports, trade press (with named author and editorial process) |
| 6 | General commentary | Blogs, newsletters, social media (require cross-verification) |
| 7 | Unattributed content | Wiki-style sites without citation, content farms, AI-generated content pages |

Rules:
- Specific numerical claims require at least one Tier 1-3 source.
- Tier 4 sources are acceptable for factual reporting if the claim is not a specific number or technical detail.
- Tier 6 sources require cross-verification with Tier 1-4.
- Tier 7 sources are never acceptable as the sole source for a factual claim.
- Wikipedia is a starting point for finding primary sources, not a citable source. Follow the citations to the original.

## Common Citation Errors

### 1. Fabricated citations

The most serious error. AI systems may generate plausible-looking citations with real author names and journal titles but fabricated DOIs and paper titles. **Always search for the citation. If you cannot find it, do not use it.**

Common patterns of fabricated citations:
- DOI that does not resolve
- Author names that do not match the venue
- Paper titles that sound plausible but return no search results
- Volume/issue/page numbers that do not exist

### 2. Correct paper, wrong claim

The paper exists and is real, but it does not say what you claim it says. This happens when:
- You cite a paper you have not read based on its title
- You conflate the paper's findings with a later interpretation
- You cite a preprint version but the published version changed the result

**Prevention:** Read the relevant section. If you cannot access the full text, cite only what the abstract says, and say so.

### 3. Wrong version

- Citing an arXiv preprint when a peer-reviewed version with updated results exists
- Citing a working paper that was later retracted or significantly revised
- Citing a conference paper when the journal version has different numbers

**Prevention:** Check for the latest version. Note which version you cite.

### 4. Misattribution

- Attributing a concept to the wrong person ("Godwin's law" is not from Godwin's paper — actually, it is, but verify rather than assume)
- Citing a secondary source that popularized an idea rather than the primary source that originated it
- Confusing authors with similar names

**Prevention:** Trace the claim to its origin. If you cannot identify the primary source, say "as reported in [secondary source]" rather than attributing directly.

### 5. Year errors

- Using the arXiv submission year instead of the publication year
- Using the conference year instead of the proceedings publication year
- Off-by-one errors from papers published online in one year and in print the next

**Prevention:** Record both the online publication date and the formal publication date if they differ.

## Format

Use a consistent citation format. For most professional output:

**Academic papers:**
> Author(s). "Title." *Journal/Conference*, vol. X, no. Y, pp. ZZ-ZZ, Year. DOI/arXiv.

**Web sources:**
> Author/Publisher. "Title." Site Name, Date. URL (accessed Date).

**Financial/company sources:**
> Company Name. "Title of filing/report." Filing type, Date. URL.

**Laws/regulations:**
> Jurisdiction. "Law name," Section/Article, Year. URL.

## In-Text Attribution

When stating a fact based on a source, distinguish clearly between:

- **What the source says:** "Smith et al. (2024) report a 23% improvement in accuracy."
- **What you infer from the source:** "Smith et al.'s results suggest the method generalizes to other domains [our interpretation]."
- **What multiple sources establish:** "Three independent studies (Smith 2024, Lee 2024, Wang 2025) report consistent improvements."

Do not use citations to decorate claims. If a claim is common knowledge in the field, a citation is not required. If it is a specific finding, number, or controversial claim, cite the source.
