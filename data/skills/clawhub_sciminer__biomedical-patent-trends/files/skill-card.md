## Description: <br>
Download, search, and analyze Patent-Mol-Wiki biomedical-patent packages for recent-period trend reviews, portfolio statistics, entity lookup, charting, and molecular-structure analysis. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[sciminer](https://clawhub.ai/user/sciminer) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Patent analysts, biomedical researchers, portfolio teams, and developers use this skill to download Patent-Mol-Wiki packages, search local wiki indexes, summarize patent trends, generate reproducible charts, and analyze selected molecular-structure files. It emphasizes coverage disclosure, credential safety, and evidence-backed conclusions. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The downloader can send the SciMiner API key to any URL returned by the provider response. <br>
Mitigation: Review before installing with a real SciMiner key; restrict credentialed requests to SciMiner or approved download hosts, avoid HTTP URLs, and avoid attaching the API key to arbitrary response URLs. <br>


## Reference(s): <br>
- [Biomedical Patent Trends on ClawHub](https://clawhub.ai/sciminer/skills/biomedical-patent-trends) <br>
- [Patent-Mol-Wiki download API](references/patent-mol-wiki-api.md) <br>
- [Structure-analysis rules](references/structure-analysis.md) <br>
- [SciMiner API key utility](https://sciminer.tech/utility) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance] <br>
**Output Format:** [Markdown guidance with inline shell commands and generated JSON, CSV, and SVG analysis artifacts.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires a local SciMiner credential for downloads; molecular-structure analysis requires RDKit in the analysis environment.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
