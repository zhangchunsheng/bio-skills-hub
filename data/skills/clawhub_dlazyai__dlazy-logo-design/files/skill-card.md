## Description: <br>
Dlazy Logo Design helps agents create, refine, or evaluate logo and brand identity work through the dLazy hosted logo-design template. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[dlazyai](https://clawhub.ai/user/dlazyai) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users, designers, and developers use this skill to create, upgrade, or evaluate logos and brand identity concepts through the dLazy hosted logo-design template. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Prompts and any files attached with --files are sent to dLazy services. <br>
Mitigation: Avoid confidential brand assets unless dLazy's terms and data handling are acceptable; attach only the files needed for the task. <br>
Risk: The dLazy CLI can save an API key in the local user configuration. <br>
Mitigation: Use OS-user protected configuration or the DLAZY_API_KEY environment variable, and rotate or revoke keys from the dLazy dashboard when needed. <br>
Risk: A global npm installation persists the pinned dLazy CLI on the host. <br>
Mitigation: Use the pinned npx invocation when a persistent global CLI is not desired. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/dlazyai/skills/dlazy-logo-design) <br>
- [dLazy CLI source](https://github.com/dlazyai/cli) <br>
- [@dlazy/cli npm package](https://www.npmjs.com/package/@dlazy/cli) <br>
- [dLazy homepage](https://dlazy.com) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Files, Guidance] <br>
**Output Format:** [Markdown or terminal text from the dLazy CLI, with generated logo assets or preview links when the service returns them] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires a dLazy API key; optional local attachments are uploaded via the dLazy CLI when --files is used.] <br>

## Skill Version(s): <br>
1.3.4 (source: frontmatter, server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
