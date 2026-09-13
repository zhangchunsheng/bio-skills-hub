## Description: <br>
Verify or normalize biomedical and life-science reference lists when the task is about AI-caused reference errors, making bibliographies more reliable and convincing. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[emp-tca](https://clawhub.ai/user/emp-tca) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Researchers, manuscript authors, editors, and developers use this skill to verify biomedical reference lists for fabricated or corrupted citations, normalize citation formats, and produce audit reports plus auto-fixed bibliography files. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Verification can send citation identifiers and sometimes short reference titles to public citation services such as Crossref, PubMed/NCBI, and OpenAlex. <br>
Mitigation: Use format-only mode for private documents, or disable verification channels that should not receive citation metadata. <br>
Risk: Optional API keys or email settings may be sent to external services during authenticated or polite metadata lookups. <br>
Mitigation: Avoid setting NCBI_API_KEY, OPENALEX_API_KEY, or USER_EMAIL unless higher rate limits or authenticated lookups are needed. <br>
Risk: Audit classifications and auto-fixed bibliographies can still contain mistakes or unresolved severe citation issues. <br>
Mitigation: Review generated reports before using the fixed bibliography, and keep severe or unresolved items for manual confirmation. <br>


## Reference(s): <br>
- [Verification Policy](references/verification_policy.md) <br>
- [Biomedical Reference Verifier on ClawHub](https://clawhub.ai/emp-tca/skills/biomedical-reference-verifier) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown reports, JSON or JSONL records, fixed bibliography files, and shell command guidance] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Writes reference-audit-summary.md, reference-audit-detail.md, references.auto-fixed.md or document.auto-fixed.md, and optional process JSON/index artifacts without overwriting the source.] <br>

## Skill Version(s): <br>
1.1.3 (source: frontmatter and server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
