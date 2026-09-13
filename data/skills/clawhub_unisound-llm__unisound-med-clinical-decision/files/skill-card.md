## Description: <br>
Provides structured clinical-decision and health-management assistance across diagnosis, primary care, outcome analysis, condition analysis, and chronic disease management task modes. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[unisound-llm](https://clawhub.ai/user/unisound-llm) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External developers and clinical application integrators use this skill to route user-supplied clinical questions to a medical model and receive structured assistance for triage, treatment planning, primary care support, outcome analysis, condition analysis, or chronic disease management. The output is model-assisted information and should not be treated as a formal clinical decision. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Clinical question text is sent to the configured medical-model API and may contain sensitive patient information. <br>
Mitigation: De-identify patient data before use and follow the organization's privacy and data-handling rules. <br>
Risk: Generated medical content may be incomplete, inaccurate, or unsuitable for direct patient-care decisions. <br>
Mitigation: Require qualified clinical review and treat outputs as assistance rather than formal diagnosis or treatment direction. <br>
Risk: API keys passed through command arguments can appear in command histories, process listings, or shared job logs. <br>
Mitigation: Use secure secret handling where possible and avoid exposing real API keys in reusable commands or logs. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/unisound-llm/skills/unisound-med-clinical-decision) <br>
- [Hivoice chat completions API endpoint](https://maas-api.hivoice.cn/v1/chat/completions) <br>


## Skill Output: <br>
**Output Type(s):** [Text, JSON, Guidance, Configuration] <br>
**Output Format:** [JSON by default, NDJSON for batch output, or plain text when text-only output is requested] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Can write full results to a UTF-8 output file; dry-run emits parsed question metadata without calling the API.] <br>

## Skill Version(s): <br>
1.0.2 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
