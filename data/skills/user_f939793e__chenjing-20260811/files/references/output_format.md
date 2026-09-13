# Output Format Template

For every recommended video, emit the block below, exactly once per video. Fill each field from the actual video — never leave a field blank with invented content.

---

## Video Title

视频名称：<verbatim title of the video>

## Source

来源：<channel / institution / platform>

## Link

视频链接：<verified URL>

## Language

语言：English / Mixed

## Clinical Specialty

专业：<e.g., Pediatrics / ICU / Cardiology>

## Teaching Level

教学等级：Level 1 / Level 2 / Level 3

## Accessibility (国内可访问性)

国内可访问性：国内直连 / 需科学上网
（默认国内直连；外网源须显式标注"需科学上网"，无国内镜像时方才列入）

## Teaching Type

类型：<one of: Bedside teaching rounds / Case discussion / Grand rounds / Residency teaching>

## Duration

时长：<e.g., 18:42>  (or "Unknown" only if truly unobtainable)

## Target Learners

适合：
- Medical students
- Residents
- Fellows
- Attending physicians

# Clinical Teaching Analysis

## 1. Case Content

病例介绍：<what disease / scenario / patient is shown>

## 2. Teaching Points

主要教学内容：<key clinical facts, signs, management taught>

## 3. Clinical Reasoning Value

临床推理价值：<differential, decision making, evidence basis>

## 4. English Learning Value

医学英语学习重点：
- Common clinical phrases: <list phrases observed>
- Presentation expressions: <how the case is presented>
- Doctor–patient communication: <dialogue examples>

## 5. Recommendation Score

评分：
- Medical quality: <n>/10
- Educational value: <n>/10
- Research value: <n>/10
- English learning value: <n>/10
- Teaching Level: Level 1 / 2 / 3

---

## When no fully-qualifying video exists

Open with: "目前未找到完全符合标准的英文医学教学查房视频，以下推荐为最接近资源，并说明差距。"

Then still use the template for the closest candidates, but add a "## Gap Analysis" note under each explaining specifically which criterion is not met (e.g., "Authenticity = category 4 only; no real bedside examination shown").

## Advanced-function outputs (on request)

When the user asks for deeper work, append or produce separately:

1. **Extract medical English expressions** — a table: phrase | context | Chinese meaning.
2. **Bedside English learning notes** — structured notes from the video (vocab + phrases + sample dialogue).
3. **Case discussion logic summary** — the reasoning chain: findings → differential → investigation → diagnosis → management.
4. **Western vs Chinese bedside teaching comparison** — compare workflow, roles, documentation, learner participation.
5. **English case presentation template** — use the asset `assets/case_presentation_template.md` as the base.
