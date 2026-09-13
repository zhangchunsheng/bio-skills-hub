# 临床试验中心实验室分装账单核对台 Team Templates

## Case Header

| Field | Value |
|---|---|
| Case ID | |
| Objective and scope | |
| Accountable owner | |
| Participating teams | |
| Deadline / review cadence | |
| Confidentiality | |
| Source cutoff time | |
| Success criteria | |

## Evidence Register

| Evidence ID | Source and location | Version/date | Owner | Supports | Freshness | Access class | Notes |
|---|---|---|---|---|---|---|---|

Use `E-001`, `E-002`, and stable increments. Never rename an evidence ID after it has been cited.

## Core Register

`差异ID | 研究/实验室 | 中心/匿名样本 | 原管条码 | 接收条件 | 离心/分装规则 | 子管条码/数量/体积 | 冻存/托管 | 检测/外送 | 失败/重分装 | 费率/发票/差异金额 | 证据 | 状态`

## Action Register

| Action ID | Related item | Action | Accountable owner | Contributors | Due date | Completion evidence | Status | Blocker/escalation |
|---|---|---|---|---|---|---|---|---|

Use `A-001`, `A-002`, and stable increments. A task is closed only when completion evidence and acceptance are recorded.

## Decision Log

| Decision ID | Decision required | Options | Recommendation | Decision owner | Due date | Decision | Rationale | Source/evidence | Supersedes |
|---|---|---|---|---|---|---|---|---|---|

## Approval Gate

| Gate | Reviewer | Entry criteria | Result | Conditions | Date | Evidence |
|---|---|---|---|---|---|---|
| Content accuracy | Domain owner | Sources and unresolved questions visible | | | | |
| Risk review | Risk/compliance owner | Risks and exceptions assigned | | | | |
| External release | Authorized approver | Final wording and attachments frozen | | | | |

## Quality Checklist

- Every high-impact statement has a source or is explicitly marked unknown.
- Every open action has one accountable owner and a date or trigger.
- Conflicting sources remain visible with a named resolver.
- Approvals identify person, role, date, scope, and conditions.
- Sensitive material is minimized and stored only in approved locations.
- Closed items include completion evidence and acceptance criteria.

## Handoff Message

```text
Case: [ID and title]
Current state: [one sentence]
Decisions needed: [IDs, owners, due dates]
Actions due next: [IDs, owners, due dates]
Blockers: [IDs and escalation owner]
New evidence: [evidence IDs]
Approval required before: [external action or milestone]
Next review: [date/time]
```

