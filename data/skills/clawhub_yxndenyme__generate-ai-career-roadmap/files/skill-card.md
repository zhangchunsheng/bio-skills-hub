## Description: <br>
根据使用者的简历或引导式问答，生成基于最新证据的 AI 与泛 AI 职业机会报告和个性化学习路线。适用于分析近期 AI 赛道、公司、新兴职位、可迁移能力、岗位匹配、技能差距、作品集方向，或制定由使用者自定义周期并区分通识、职位专项和行业专项的职业转型学习计划。 <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[yxndenyme](https://clawhub.ai/user/yxndenyme) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and career changers use this skill to turn a resume or guided intake into an evidence-based AI career opportunity report, role fit analysis, and personalized learning roadmap. It supports current market research, skill-gap analysis, portfolio planning, and report updates. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill processes resumes, career goals, constraints, and other personal background information. <br>
Mitigation: Provide only information needed for the career analysis, avoid unnecessary sensitive details, and review generated reports before sharing. <br>
Risk: Career recommendations and market conclusions may become stale or misleading if sources are not current. <br>
Mitigation: Require current web research for full reports, keep evidence dates near time-sensitive claims, and verify important recommendations against authoritative sources. <br>
Risk: Generated reports may overstate achievements, qualifications, hiring certainty, or completed portfolio work. <br>
Mitigation: Keep resume facts, user-stated preferences, assumptions, and predictions separate; do not invent accomplishments, credentials, jobs, salaries, or employment guarantees. <br>


## Reference(s): <br>
- [个人画像采集与简历提取](artifact/references/intake-profile.md) <br>
- [最新 AI 与泛 AI 市场研究规则](artifact/references/research-policy.md) <br>
- [职位分类与匹配评分](artifact/references/role-taxonomy.md) <br>
- [个性化学习计划框架](artifact/references/learning-plan-framework.md) <br>
- [最终报告规范](artifact/references/report-contract.md) <br>
- [AI 职业规划资料采集表](artifact/assets/profile-intake-template.md) <br>
- [AI 与泛 AI 职业机会及个人学习路线报告](artifact/assets/report-template.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, files, shell commands, guidance] <br>
**Output Format:** [Markdown career report, with optional local Markdown/DOCX/PDF files when requested and validation output from a Python report checker] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Reports include dated sources, role-fit scoring, gap analysis, learning plans, portfolio recommendations, privacy checks, and validation findings.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
