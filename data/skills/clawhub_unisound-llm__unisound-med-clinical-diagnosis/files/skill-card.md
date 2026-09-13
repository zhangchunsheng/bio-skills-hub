## Description: <br>
Runs clinical case analysis, differential diagnosis, and primary-care diagnosis prompts against a configured medical-model API. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[unisound-llm](https://clawhub.ai/user/unisound-llm) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and clinical workflow integrators use this skill to pass medical case text to a configured medical-model API for structured diagnosis reasoning, differential diagnosis, or dry-run input inspection. It is intended as model-assisted information and not as a formal diagnosis decision system. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Clinical case text is sent to the configured medical-model API during normal execution. <br>
Mitigation: Do not include patient identifiers or protected health information unless the endpoint and data flow are approved by the organization; use --dry-run to inspect parsed input before making a network call. <br>
Risk: The model response may be incomplete or uncertain for medical decision-making. <br>
Mitigation: Treat outputs as model-assisted information only and require qualified clinical review before use in care decisions. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/unisound-llm/skills/unisound-med-clinical-diagnosis) <br>
- [ClawHub publisher profile](https://clawhub.ai/user/unisound-llm) <br>


## Skill Output: <br>
**Output Type(s):** [JSON, Text, Shell commands, Guidance] <br>
**Output Format:** [JSON on stdout by default, optional text-only answer output, and optional JSON or NDJSON file output] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Supports dry-run parsing without network calls; batch JSONL output is newline-delimited JSON.] <br>

## Skill Version(s): <br>
1.0.2 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
