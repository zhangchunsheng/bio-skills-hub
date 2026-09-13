## Description: <br>
Iaiops Process guides agents through process-plant monitoring and diagnostics across HART-IP, OPC-UA, Modbus, and optional MQTT/Sparkplug B, emphasizing read-first workflows and MOC-gated writes. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[zw008](https://clawhub.ai/user/zw008) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and OT engineers use this skill to guide safe process-plant data collection, diagnostics, downtime triage, data-quality checks, and OEE analysis across HART-IP, OPC-UA, Modbus, and optional UNS/Sparkplug workflows. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Use in production OT or plant environments may expose sensitive export and publish capabilities. <br>
Mitigation: Review before production installation, require explicit operator approval, and restrict destinations with allowlists. <br>
Risk: Historian push, export, stream publish, and stream publish event tools can behave as write or export paths despite the skill's read-first posture. <br>
Mitigation: Verify the underlying iaiops MCP server enforces dry-run behavior, audit logging, and MOC controls before enabling these capabilities. <br>


## Reference(s): <br>
- [Iaiops Process ClawHub release](https://clawhub.ai/zw008/skills/iaiops-process) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown guidance with inline commands and tool names] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Read-first operational guidance with approval requirements for write/export actions] <br>

## Skill Version(s): <br>
0.12.0 (source: server release evidence, created 2026-07-13) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
