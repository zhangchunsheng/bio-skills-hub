## Description: <br>
医疗设备商机雷达 helps agents find early hospital and public-health procurement opportunities by scanning proposed projects, purchase intentions, and expiring service contracts, then ranking leads by budget, urgency, and fit. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[dragonzu](https://clawhub.ai/user/dragonzu) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Sales and business development users use this skill to identify and prioritize early medical equipment, consumables, reagent, maintenance, and hospital IT opportunities. It is intended for China-focused hospital and health-system procurement lead discovery from public bidding and project data. <br>

### Deployment Geography for Use: <br>
China-focused; usable globally by users monitoring Chinese hospital procurement data. <br>

## Known Risks and Mitigations: <br>
Risk: The skill persists account credentials and generated reports may contain signed links that bypass login for anyone who receives the report. <br>
Mitigation: Use a manually configured API key when possible, store credentials securely, and remove signed links before sharing reports unless recipients are intended to have access. <br>
Risk: Scans consume vendor credits, and consent-based auto-registration sends platform, CPU architecture, and a hashed MAC-derived identifier to the vendor. <br>
Mitigation: Review the estimated query cost before running scans and use a preconfigured API key to skip auto-registration when device-derived registration is not acceptable. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/dragonzu/skills/medical-equipment-opportunity-radar) <br>
- [API Quick Reference](references/api-quick.md) <br>
- [Workflow Guide](references/workflow.md) <br>
- [Report Template](references/report-template.md) <br>
- [Auto-Registration Flow](references/auto-register.md) <br>
- [知了商机大师](https://agent.zhiliaobiaoxun.com) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, files, configuration, guidance] <br>
**Output Format:** [Markdown opportunity lists with optional self-contained HTML report files.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires ZLBX_API_KEY or consent-based auto-registration; scans consume vendor credits and generated reports may include signed links.] <br>

## Skill Version(s): <br>
1.0.2 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
