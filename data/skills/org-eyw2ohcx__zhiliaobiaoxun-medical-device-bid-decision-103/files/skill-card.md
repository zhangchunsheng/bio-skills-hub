## Description: <br>
Helps users evaluate medical-device, consumables, reagent, and hospital IT procurement opportunities by using historical bid data to assess whether to bid, expected competitors, buyer preferences, pricing references, and rejection risk. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[zhiliaobiaoxun](https://clawhub.ai/user/zhiliaobiaoxun) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and commercial teams use this skill when they have a concrete hospital or health-system procurement opportunity and need a bid/no-bid recommendation, competitor analysis, buyer history, and pricing guidance. It can produce a full decision report or a lighter quick assessment based on the user's requested depth. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The vendor receives query terms such as project names, company names, and procurement keywords during analysis. <br>
Mitigation: Use the skill only when those query terms are appropriate to send to the vendor service, and avoid including unnecessary sensitive context in searches. <br>
Risk: Free-trial registration can send a consent-gated device hash and stores an API key in the user's home directory. <br>
Mitigation: Prefer a manually configured API key when available, confirm user consent before any automatic registration, and protect or remove the local API-key file according to local policy. <br>
Risk: Generated HTML reports are saved locally and may preserve signed access links returned by the API. <br>
Mitigation: Review reports before sharing or exporting them, and share files containing signed links only with recipients who should be able to access those linked records. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/zhiliaobiaoxun/skills/medical-device-bid-decision) <br>
- [API quick reference](references/api-quick.md) <br>
- [Decision workflow](references/workflow.md) <br>
- [Report template](references/report-template.md) <br>
- [Automatic registration flow](references/auto-register.md) <br>
- [ZLBX API base endpoint](https://mcp-server.zhiliaobiaoxun.com/api_v2/{工具名}) <br>
- [知了商机大师](https://agent.zhiliaobiaoxun.com) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, html, guidance, configuration] <br>
**Output Format:** [Markdown decision report in the conversation, with an optional self-contained HTML report file and citation appendix.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Uses ZLBX_API_KEY or a consent-gated registration flow; complete reports typically consume 12-25 data queries, while quick assessments use about 5-8 queries.] <br>

## Skill Version(s): <br>
1.0.3 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
