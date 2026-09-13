## Description: <br>
Iaiops Clinical helps agents guide clinical-facility operations work across BACnet/IP, Modbus, and OPC-UA, with patient-safety checks for isolation rooms, operating rooms, and medical gas systems. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[zw008](https://clawhub.ai/user/zw008) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Facility engineers and clinical operations teams use this skill to guide read-first inspection, diagnostics, and safety-oriented review of hospital building-control, medical-gas, and SCADA data. It is intended to support, not replace, authorized site procedures and clinical-facility safety controls. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The release is described as read-only, but the artifact documents BACnet write capability for hospital building-control systems. <br>
Mitigation: Use only where BACnet writes are blocked or governed by site authorization, dry-run review, rollback planning, and named approval. <br>
Risk: Clinical-facility pressure, ventilation, and medical-gas analysis can be mistaken for authoritative safety or compliance decisions. <br>
Mitigation: Treat outputs as support for authorized personnel; verify findings against site instruments, alarm panels, and applicable facility procedures before acting. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/zw008/skills/iaiops-clinical) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown with inline shell commands and operational guidance] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May include read-first diagnostic workflows, protocol-specific tool guidance, and safety review notes.] <br>

## Skill Version(s): <br>
0.12.0 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
