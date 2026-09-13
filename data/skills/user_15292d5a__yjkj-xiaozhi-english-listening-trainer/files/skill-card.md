## Description: <br>
Personalizes English listening practice by generating level-appropriate materials from learner vocabulary, interests, and listening blockers. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[qizhitang](https://clawhub.ai/user/qizhitang) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Learners and tutoring agents use this skill to generate personalized English listening passages, guide a listen-summarize-compare-review workflow, diagnose comprehension blockers, and update vocabulary practice records. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill can use and update learner vocabulary, interests, progress reports, and reminders through companion skills. <br>
Mitigation: Review the companion DNA and reminder skills before use so learners and operators understand how those records are stored, updated, deleted, and opted out of. <br>
Risk: Generated listening material may be too easy, too difficult, or mismatched to a learner's current profile if the underlying vocabulary or interest records are stale. <br>
Mitigation: Confirm the learner profile before practice and adjust grade level, topic, speed, and new-word density when the student reports poor fit. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/qizhitang/xiaozhi-english-listening-trainer) <br>
- [Listening topic templates](references/listening-topic-templates.md) <br>
- [Listening material prompts](references/listening-topics.md) <br>
- [General listening topic library](references/topics.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, guidance] <br>
**Output Format:** [Markdown and conversational tutoring text with generated listening passages, vocabulary notes, comprehension questions, and progress summaries.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May depend on companion learner profile, vocabulary DNA, grammar coach, and reminder skills for personalization and follow-up.] <br>

## Skill Version(s): <br>
1.0.1 (source: server release metadata and skill frontmatter) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
