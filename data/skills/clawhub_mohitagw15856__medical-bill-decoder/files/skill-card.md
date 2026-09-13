## Description: <br>
Decode an itemized medical bill or EOB into plain English and find the charges worth disputing. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[mohitagw15856](https://clawhub.ai/user/mohitagw15856) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users can use this skill to interpret itemized medical bills or EOBs, identify likely duplicate, unbundled, balance-billing, or mismatch issues, and prepare scripts for billing, financial-assistance, or negotiation calls. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Medical bills and EOBs may contain sensitive personal, medical, and financial information. <br>
Mitigation: Share only the minimum bill details needed, remove identifiers when practical, and avoid including unrelated personal information. <br>
Risk: Billing guidance can be mistaken for legal, financial, or medical advice. <br>
Mitigation: Treat the output as plain-language billing help and confirm jurisdiction-dependent or load-bearing decisions with a qualified professional. <br>
Risk: The agent could overstate code meanings, prices, protections, or negotiation outcomes. <br>
Mitigation: Require uncertain codes to be marked for confirmation, avoid invented prices or diagnoses, and frame scripts as requests rather than promised outcomes. <br>


## Reference(s): <br>
- [Medical Bill Decoder Skill Page](https://clawhub.ai/mohitagw15856/skills/medical-bill-decoder) <br>
- [Medical Bill Decoder Homepage](https://mohitagw15856.github.io/pm-claude-skills/skill/medical-bill-decoder.html) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, guidance] <br>
**Output Format:** [Markdown with a verdict, line-by-line table, ranked red flags, scripts, action steps, and disclaimer] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Uses only user-provided bill or EOB details and instructs the agent not to invent codes, charges, prices, diagnoses, or outcomes.] <br>

## Skill Version(s): <br>
50.0.0 (source: ClawHub release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
