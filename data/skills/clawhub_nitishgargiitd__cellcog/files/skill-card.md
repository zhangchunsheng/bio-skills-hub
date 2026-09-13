## Description: <br>
Cellcog helps agents send multimodal tasks to CellCog for research, analysis, content generation, code, documents, dashboards, and other deliverables. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[nitishgargiitd](https://clawhub.ai/user/nitishgargiitd) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and agent users use this skill to configure CellCog, send prompts and tagged local files to the CellCog service, wait for or receive completion notifications, continue tasks, and retrieve generated outputs. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Prompts and files inside SHOW_FILE tags are uploaded to the third-party CellCog service. <br>
Mitigation: Only tag files intended for CellCog processing, and do not include secrets, credentials, private customer data, or regulated information unless approved. <br>
Risk: Generated files may be downloaded or written to local paths. <br>
Mitigation: Review requested output paths and inspect generated files before relying on them or using them in downstream workflows. <br>
Risk: The skill depends on a CellCog API key for service access. <br>
Mitigation: Provide CELLCOG_API_KEY through the environment and avoid hard-coding or sharing the key in prompts, files, or generated artifacts. <br>


## Reference(s): <br>
- [Cellcog on ClawHub](https://clawhub.ai/nitishgargiitd/skills/cellcog) <br>
- [CellCog homepage](https://cellcog.ai) <br>
- [CellCog Python SDK](https://github.com/CellCog/cellcog_python) <br>
- [cellcog on PyPI](https://pypi.org/project/cellcog/) <br>
- [DeepResearch Bench Leaderboard](https://huggingface.co/spaces/muset-ai/DeepResearch-Bench-Leaderboard) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, files, guidance] <br>
**Output Format:** [Markdown guidance with Python and shell snippets; CellCog responses may include text, status fields, generated file paths, and downloaded artifacts.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires python3 and CELLCOG_API_KEY. SHOW_FILE tags upload referenced files to CellCog; GENERATE_FILE tags can direct downloaded outputs to local paths.] <br>

## Skill Version(s): <br>
2.0.16 (source: release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
