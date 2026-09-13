# IMA Output Format

Assemble the full deliverable as a single Markdown document using the structure below. This is
the dossier intended for the IMA medical knowledge base / notes. Keep one `#` title (becomes the
IMA note title), use `##` for each section, and fill from verified content only.

```
# <Disease> Academic Teaching Rounds

## Level
Level 1 / Level 2 / Level 3

## Recommended Videos
中文（国内直连优先）：
- <title> | <source> | <link> | <teaching level> | 评分(医疗/教学/科研/英语) | 可访问性

英文 / 外网（需科学上网，无国内镜像时方列）：
- <English title> | <source> | <link> | 可访问性

## Teaching Lesson Plan
<from references/teaching_plan.md — unified 7 sections; Level 3 adds Academic Discussion>

## Clinical Reasoning
<differential → reasoning → key discriminating features>

## Evidence Summary
<key studies/guidelines as Evidence-Summary blocks (see references/evidence_format.md §5):
 each entry = Label + citation + Evidence type + Grade + Finding + Relevance + Limitation(≥L2).
 These entries form the ANCHOR POOL that Teaching Questions cite.>

## Guideline Analysis
<domestic vs AAP/NICE/ESPGHAN/ATS/IDSA/SSC as the comparison table (references/evidence_format.md §4):
 GRADE badges on each recommendation; a "Consensus gaps" bullet for unresolved dimensions.>

## Research Update (Level 3)
<mechanistic, translational, future directions>

## Future Directions
<scientific questions, proposed studies, publication potential>

## Teaching Questions (evidence-anchored)
<from references/teaching_questions.md: each Q carries an Anchor (citation+GRADE), model answer/
 appraisal, pitfall, follow-up; end with the Question → Source map table proving traceability.>

## Medical English Notes
<phrase tables from references/medical_english.md>

## Image Resources
<per-image metadata from references/image_resources.md>
```

## Rules
- State evidence level everywhere a claim depends on literature; use the inline citation and GRADE
  format from `references/evidence_format.md` §1–§3 consistently across Evidence Summary,
  Guideline Analysis, and Teaching Questions.
- **Traceability is mandatory:** every Teaching Question must anchor to an entry already present in
  Evidence Summary or Guideline Analysis; no orphan citations (see evidence_format.md §6).
- If a section lacks sufficient evidence, write: "Current evidence remains insufficient."
- Do not fabricate videos, papers, RCTs, or image sources.
- For IMA sync, keep images as network URLs only (see references/image_resources.md).
