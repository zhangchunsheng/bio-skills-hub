---
name: school-absence-note-kit
description: Draft truthful school absence, late arrival, early pickup, appointment, illness recovery, and make-up work messages with documentation checklist, follow-up tracker, and tone variants for email, portal, or printed notes. Use when a parent, guardian, caregiver, or older student needs school attendance communication without fabricated excuses, signatures, medical details, or school-policy advice.
---

# School Absence Note Kit

## Overview

Use this skill when a parent, guardian, caregiver, homeschool coordinator, or older student needs a clear school attendance message. Focus on truthful, concise communication, make-up work follow-up, documentation readiness, and practical tracking.

This is a prompt-only administrative writing skill. It does not fabricate excuses, medical details, documentation, signatures, or permissions. It does not interpret school law or override local attendance policy.

## Trigger

Use this skill when the user needs to:

- Notify a school about an absence.
- Explain a late arrival or early pickup.
- Send an illness recovery or appointment note.
- Request make-up work after missed class.
- Prepare a printed note, email, or school portal message.
- Track whether the school responded and whether assignments were received.

Do not use this skill to create false excuses, forge documentation, impersonate a parent or school official, evade attendance rules, or hide safety concerns.

## Intake

Ask for only the details needed to draft the note:

- School level or grade band.
- Recipient, such as teacher, attendance office, advisor, coach, or school nurse.
- Student name or initials, if the user wants them included.
- Date or date range of absence, late arrival, or early pickup.
- Communication channel: email, portal message, printed note, text, or call script.
- Truthful reason category: illness, appointment, family emergency, transportation issue, religious observance, bereavement, weather or closure issue, late arrival, early pickup, or other user-stated reason.
- Expected return date or time if known.
- Requested action, such as excuse absence, send make-up work, confirm receipt, notify teachers, or coordinate pickup.
- Parent, guardian, or caregiver contact information if the user wants it included.
- Known documentation requirement, such as doctor note, appointment slip, or school form.

Do not ask for private medical details unless the user says the school requires a general health-related note. Prefer broad wording such as "illness" or "medical appointment" unless the user asks for more detail.

## Workflow

1. **Clarify the attendance event.** Identify whether this is an absence, late arrival, early pickup, appointment, illness recovery, make-up work request, or follow-up.
2. **Confirm truth and scope.** Use only user-provided truthful facts and avoid invented details, signatures, or documents.
3. **Select the channel and tone.** Choose short portal message, formal email, printed note, or phone-call script.
4. **Draft the core note.** Include student, date or time, reason category, expected return, requested action, and contact information if provided.
5. **Add make-up work language.** Request assignments, deadlines, missed handouts, tests, projects, or online materials when relevant.
6. **Build a documentation checklist.** List possible items to verify against school rules, clearly labeling unknown requirements.
7. **Create tone variants.** Provide concise, formal, and warm versions when useful.
8. **Create a follow-up tracker.** Track sent date, recipient, channel, response, assignments received, documentation submitted, and unresolved items.
9. **Add policy reminder.** Encourage the user to confirm school-specific attendance rules for extended, repeated, or uncertain absences.

## Output Format

Return these sections:

1. **Situation Snapshot**: student, school level, dates or times, reason category, recipient, channel, and requested action.
2. **Ready-to-Send Note**: the primary message in the selected format.
3. **Short Portal Version**: a compact version for limited text fields.
4. **Formal Email Version**: subject line, greeting, body, closing, and contact line.
5. **Printed Note Version**: date line, recipient line, message, parent or guardian name line, and contact line.
6. **Make-Up Work Request**: assignments, deadlines, materials, tests, and preferred reply channel.
7. **Documentation Checklist**: what the user may need to verify or attach.
8. **Follow-Up Tracker**: sent date, recipient, response, assignments received, documentation submitted, and next action.
9. **Scope and Policy Notes**: no fabrication, no signatures, no medical details unless required, and confirm local attendance rules.

If the user only needs one format, provide that format first and keep alternatives brief.

## Message Rules

- Keep the note truthful, concise, respectful, and specific enough for school administration.
- Use neutral absence categories instead of unnecessary personal detail.
- Ask for make-up work clearly without blaming the school or teacher.
- Include dates and times in an unambiguous format.
- Do not invent appointment details, illnesses, emergencies, transportation problems, signatures, forms, or school responses.
- Do not claim a school must excuse the absence unless the user provides that policy.
- Do not provide legal advice about truancy, disability accommodations, custody, guardianship, or attendance disputes.

## Special Cases

### Illness Absence
Use general language such as "due to illness" unless the user says the school requires more detail. Include expected return if known and a make-up work request if needed.

### Medical or Dental Appointment
State that the student has an appointment and include pickup or return time. Mention documentation only if the user has it or the school requires it.

### Late Arrival
Include expected arrival time, whether the student should report to the office, and any class or assignment follow-up needed.

### Early Pickup
Include pickup time, pickup person if the user wants it included, and where the school should send the student if known. Do not create authorization language beyond the user's facts.

### Family Emergency or Sensitive Reason
Keep details minimal. Offer a respectful note that protects privacy while still notifying the school.

### Extended or Repeated Absences
Encourage the user to check school attendance policy, documentation rules, and counselor or administrator support. Do not imply the note alone will resolve compliance issues.

## Safety Boundaries

- No fabricated excuses, medical details, appointment records, signatures, parent identity, school forms, or documentation.
- No impersonation of a parent, guardian, clinician, school official, or student if the user is not authorized.
- No advice to violate attendance policy, hide safety issues, or mislead the school.
- No legal advice about truancy, custody, disability accommodations, or education rights.
- For extended, repeated, disputed, or sensitive absences, encourage checking school rules and contacting appropriate school staff.

## Acceptance Criteria

1. Produces a ready-to-send school absence, late arrival, early pickup, appointment, illness recovery, or make-up work message.
2. Includes channel-appropriate variants for email, portal, and printed note when useful.
3. Includes make-up work checklist, documentation checklist, and follow-up tracker.
4. Uses truthful user-provided facts and avoids fabricated excuses, medical details, signatures, or documents.
5. Encourages confirmation of local school attendance rules for extended, repeated, or uncertain cases.
6. Requires no code execution, credentials, API access, or network dependency.

## Example Prompts

- "Write a school absence note for my child who was sick yesterday."
- "Draft an email for an early pickup for a dental appointment."
- "I need a short portal message for a late arrival this morning."
- "Help me ask my child's teacher for make-up work after two missed days."
- "Create a printed absence note and follow-up tracker."
