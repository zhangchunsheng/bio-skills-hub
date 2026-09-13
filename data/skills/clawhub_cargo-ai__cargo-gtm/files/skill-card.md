## Description: <br>
Front door for any GTM task on Cargo: sourcing, waterfall enrichment, email, phone, and LinkedIn lookup, email verification, scoring, qualification, sequencing, CRM sync, and signal monitoring for prospects, leads, accounts, contacts, ICP lists, and campaign activation. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[cargo-ai](https://clawhub.ai/user/cargo-ai) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
GTM operators, sales teams, and agents use this skill to plan and execute prospecting, account research, contact enrichment, verification, personalization, sequencing, CRM handoff, and signal-monitoring workflows in Cargo. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill can enrich and move personal sales data across many external providers and destinations. <br>
Mitigation: Require explicit approval before contact reveal, phone lookup, visitor de-anonymization, CRM or sequencer push, Slack or webhook post, scheduled play, or signed-output download; confirm lawful basis, vendor approval, minimization, retention, and suppression handling. <br>
Risk: Paid or cost-unknown GTM actions can spend credits or scale beyond the user's intended scope. <br>
Mitigation: Use the artifact's pilot, approval, and receipt gate before every paid batch, including a 1-3 row pilot, observed per-row cost, balance check, scope cap, and post-run spend receipt. <br>
Risk: Contact lists can contain wrong people, stale roles, unsafe emails, duplicates, or rows that should not be sent. <br>
Mitigation: Run the bundled deterministic QA scripts for email validation, current-role selection, LinkedIn name matching, and final contact accuracy auditing before sequencer or CRM handoff. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/cargo-ai/skills/cargo-gtm) <br>
- [Cargo skills homepage](https://github.com/getcargohq/cargo-skills) <br>
- [Cost discipline](references/cost-discipline.md) <br>
- [Contact accuracy](references/contact-accuracy.md) <br>
- [Output retrieval](references/output-retrieval.md) <br>
- [Stage action map](references/stage-action-map.md) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Markdown, Shell commands, Configuration, Code] <br>
**Output Format:** [Markdown guidance with inline shell commands, JSON configuration examples, and TypeScript QA script usage] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Routes agents to phase guides, recipes, provider playbooks, cost gates, output retrieval commands, and deterministic contact QA scripts.] <br>

## Skill Version(s): <br>
1.7.0 (source: frontmatter and server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
