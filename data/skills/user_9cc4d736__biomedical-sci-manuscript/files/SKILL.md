---
slug: biomedical-sci-manuscript
version: 1.0.0
displayName: Biomedical SCI Manuscript
name: biomedical-sci-manuscript
description: "Draft, revise, or restructure a biomedical SCI manuscript while preserving all source data, figures, tables, captions, citations, and formatting. Use for \"SCI论文写作\", manuscript drafting, section revision, report analysis, or tracked manuscript improvement."
---

# Biomedical SCI Manuscript

## Language Contract

Keep the manuscript body, citations, headings, and scientific terminology in the source manuscript's language and format unless the user requests translation. Write all auxiliary reports, analyses, modification rationales, risk notes, and suggestions in Chinese, except Skill names, standard English technical terms, and direct source quotations.

## Non-lossy Source Inventory

Before writing, create an inventory of every section, reference marker, equation, figure, embedded image, table, caption, footnote, cross-reference, supplementary callout, and placement anchor. Treat the source file as immutable and create a new output file.

For DOCX, edit the existing document structure or a full copy. Do not rebuild the document from extracted plain text because that drops media relationships, captions, fields, and layout.

Create a `原稿版式快照` before editing: document sections, page size, margins, header/footer, page numbering, styles, fonts, font sizes, line spacing, paragraph spacing, alignment, indents, heading hierarchy, table styles, figure placement, caption styles, and reference layout.

## Drafting and Revision

1. Establish the central claim and evidence map from validated source material.
2. Preserve the original article type, heading hierarchy, citation convention, figures, tables, captions, callout order, and all source formatting unless the user explicitly requests a format change.
3. Draft or revise Methods and Results from supplied facts; never invent data, P values, confidence intervals, ethics statements, sample sizes, citations, or figure content.
4. Separate observation, interpretation, limitation, and future work. Calibrate causal language to the design.
5. Keep every figure/table and its caption verbatim unless the user explicitly requests a caption revision. If moved, update the callout and anchor without deleting the object.

## Deliverables

Return:

- a revised manuscript matching the source language and format;
- a Chinese `修改说明` with actual edits and reasons;
- a Chinese `风险与待作者确认事项`;
- a before/after preservation inventory for sections, figures, tables, captions, references, and supplementary callouts.
- a Chinese `版式一致性报告` comparing the source and output snapshots, with every intentional format change and its user-approved reason.

## Zero-loss Quality Gate

Compare source and output inventories and formatting snapshots. Block delivery on any unexplained difference in figure count, table count, caption count, reference count, embedded media count, numeric result, unit, identifier, page geometry, style hierarchy, or paragraph/table formatting. Report `DATA LOSS DETECTED` or `FORMAT DRIFT DETECTED` and restore from the source before continuing.
