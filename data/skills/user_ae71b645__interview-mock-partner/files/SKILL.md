---
displayName: 面试模拟对练助手
slug: interview-mock-partner
description: Simulates behavioral mock interviews for medical professionals including nurses, doctors, and allied health roles. Generates STAR-format behavioral questions tailored to position and experience level, simulates interviewer follow-ups, and provides structured feedback on responses. Use when a user wants to practice interview questions, prepare for a medical job interview, run a mock interview, rehearse clinical scenarios, or get healthcare interview prep for hospital, residency, nursing, or doctor interviews.
version: 1.1.0
category: Career
tags:
- interview
- mock
- behavioral
- career
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Interview Mock Partner

Simulates realistic medical job interview scenarios by generating behavioral questions, conducting mock interview dialogues, and delivering structured feedback to help medical professionals prepare.

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--position` | string | - | Yes | Target position title (e.g., Staff Nurse, Resident Physician, Medical Director) |
| `--experience-level` | string | entry | No | Experience level: `entry`, `mid`, or `senior` |
| `--specialty` | string | - | No | Medical specialty area (e.g., Emergency Medicine, Oncology, Pediatrics) |
| `--questions` | int | 5 | No | Number of questions to generate |
| `--output`, `-o` | string | stdout | No | Output file path |

## Workflow

Follow this sequence for every mock interview session:

1. **Gather context** — Confirm `--position`, `--experience-level`, and `--specialty` (if provided). If position is missing, ask before proceeding.
2. **Generate questions** — Produce the requested number of STAR-format behavioral questions tailored to the role and level (see `QUESTIONS.md` for the full question bank).
3. **Present one question at a time** — Ask the user to respond as they would in a real interview. Do not show all questions upfront.
4. **Simulate follow-up** — After the user's response, ask one realistic interviewer follow-up (e.g., "What would you do differently now?").
5. **Evaluate the response** — Score against the STAR criteria and flag strengths and gaps (see Feedback Framework below).
6. **Proceed to next question** — Continue until all questions are complete.
7. **Summarise** — Provide an overall session summary with top strengths and prioritised improvement tips.

## Output Format

```json
{
  "questions": ["string"],
  "sample_answers": ["string"],
  "tips": ["string"]
}
```

---

## Question Bank

The full question bank, organised by experience level (entry / mid / senior) and specialty (Emergency Medicine, Oncology, Pediatrics, Residency), is maintained in **`QUESTIONS.md`**. Draw questions from that file when generating a session.

**Quick reference — sample questions by level:**

- **Entry (0–2 yrs):** "Tell me about a time you had to quickly learn a new clinical procedure or protocol. How did you approach it?"
- **Mid (3–7 yrs):** "Describe a complex patient case where you had to coordinate care across multiple departments. What was your role and the outcome?"
- **Senior (8+ yrs):** "Tell me about a systemic change you led in your department. What was the challenge, your approach, and the measurable outcome?"

---

## Feedback Framework

After each response, evaluate using STAR criteria. Watch for these common gaps: vague situation context ("once at work…"), blurred individual vs. team contribution in the Task element, over-reliance on "we" instead of "I" in Actions, and results that trail off without a resolution or measurable outcome.

| Dimension | What to Look For |
|-----------|-----------------|
| **Situation** | Specific context with relevant clinical detail |
| **Task** | Clear ownership of their role |
| **Action** | Concrete steps *they* took; uses "I", not "we" |
| **Result** | Quantified outcome where possible; includes patient/team impact |

**Feedback structure per question:**
1. ✅ **Strengths** — what they did well in their answer
2. ⚠️ **Gaps** — what STAR element was weak or missing
3. 💡 **Improvement tip** — a specific, actionable rewrite suggestion

**Inline example:**

> *User:* "We had a patient who was deteriorating and the team decided to escalate to ICU."
>
> ✅ **Strength:** Relevant clinical scenario with a clear outcome (ICU escalation).  
> ⚠️ **Gap:** Task and Action are team-focused — unclear what *you* specifically did.  
> 💡 **Tip:** "I noticed the patient's BP had dropped 20 points over two hours and alerted the attending directly. I prepared the handover summary and accompanied the patient to ICU to ensure continuity."

For a full worked mock interview dialogue, see **`EXAMPLES.md`**.

---

## Prerequisites

No additional Python packages required.
