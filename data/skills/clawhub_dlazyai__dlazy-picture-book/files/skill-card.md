## Description: <br>
Creates a complete picture book from a theme by drafting a paged story, generating style-consistent illustrations and background music with dLazy services, and assembling a portable HTML book. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[dlazyai](https://clawhub.ai/user/dlazyai) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and developers use this skill to have an agent create children's picture books or bedtime storybooks with coordinated story text, generated illustrations, background music, and an offline HTML reading experience. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Prompts and reference images may be sent to dLazy services during generation. <br>
Mitigation: Avoid sensitive images or private story details unless the user is comfortable uploading them to the service. <br>
Risk: Generated media is downloaded and written into the local project folder. <br>
Mitigation: Use a dedicated output directory and review generated files before sharing the finished book. <br>
Risk: Authentication may store a dLazy API key in the local CLI configuration. <br>
Mitigation: Use the documented dLazy authentication flow, keep the config file private, and rotate or revoke the key from the dLazy dashboard when needed. <br>
Risk: Media generation can consume paid credits or fail when credits are insufficient. <br>
Mitigation: Use the skill's low-quality image setting for draft books and confirm credit availability before generating many pages. <br>


## Reference(s): <br>
- [ClawHub skill listing](https://clawhub.ai/dlazyai/skills/dlazy-picture-book) <br>
- [dLazy CLI source](https://github.com/dlazyai/cli) <br>
- [dLazy CLI npm package](https://www.npmjs.com/package/@dlazy/cli) <br>
- [dLazy homepage](https://dlazy.com) <br>


## Skill Output: <br>
**Output Type(s):** [text, code, shell commands, configuration, guidance, files] <br>
**Output Format:** [Markdown guidance with shell commands, JSON book manifest, generated media files, and self-contained HTML] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Outputs typically include book.json, index.html, generated image files, and a background music file with relative paths for offline sharing.] <br>

## Skill Version(s): <br>
1.3.5 (source: frontmatter and release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
