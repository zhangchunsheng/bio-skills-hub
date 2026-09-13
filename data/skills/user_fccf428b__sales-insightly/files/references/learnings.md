# Insightly Learnings

Accumulated tips, gotchas, and corrections discovered during use. Claude reads this at the start of each invocation and appends new learnings as they're discovered.

<!-- Add entries below in format: **YYYY-MM-DD**: Learning description -->

**2026-06-28**: Research baseline — platform docs, REST API v3.1 surface (pod-specific base URL, Base64 Basic auth, top/skip/count_total pagination, plan-gated daily quota 1k–100k + 10 req/s, ETag/If-Match, CUSTOMFIELDS array), workflow-automation webhooks (Professional+, 2 retries), pricing (CRM Plus $29 / Professional $49 / Enterprise $99; Marketing/Service/AppConnect separate), and known pain points (Base64 auth 401, pod base URL, limited reporting, no email sequencing, custom objects Enterprise-only) captured from live sources on this date. Re-verify specifics against current docs before relying on them.

**2026-06-28**: The #1 developer footgun is forgetting to Base64-encode the API key — the in-browser Help sandbox encodes for you, so code that 401s often "works" in the sandbox, masking the real cause.

**2026-06-28**: Webhooks are NOT a subscription API — they're a "Webhook" action inside a Workflow Automation rule, so they require a plan with workflow automation (Professional+) and retry only twice before dropping the event. Always pair with a reconciliation pull on DATE_UPDATED_UTC.

**2026-06-28**: API paths use British spelling `Organisations` (not `Organizations`) — a common cause of 404s when porting code written against other CRMs.
