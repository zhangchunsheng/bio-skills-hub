# Insightly Platform Reference

## Overview

Insightly (insightly.com) is a unified CRM that bundles sales pipeline, **project management**, marketing automation, and customer service on one record graph. Its defining feature: a won **Opportunity** can be converted into a **Project**, so the same account record carries both the sale and the post-sale delivery — a strong fit for agencies, consultancies, and professional-services teams that sell *and* deliver work. Sold as four separately-licensed modules (CRM, Marketing, Service, AppConnect) for SMB/mid-market.

## Capabilities & automation surface

| Capability | What it does | Automation surface |
|---|---|---|
| **CRM (Contacts, Organisations, Leads, Opportunities)** | Pipeline + lead/contact management, opportunity→project handoff | **API-accessible** (REST v3.1 read/write) |
| **Projects, Tasks, Events, Notes** | Post-sale delivery tracking, activities, calendar, notes | **API-accessible** |
| **Pipelines & Pipeline Stages** | Opportunity and project stage definitions | **API-accessible** (read) |
| **Custom fields** | Per-object custom fields (`CUSTOMFIELDS` array) | **API-accessible**; available below Enterprise |
| **Custom objects** | User-defined object types | **API-accessible** but **Enterprise-only** |
| **Products / Pricebooks / Quotes** | CPQ-style objects (added in v3.1) | **API-accessible** but **Enterprise-only** |
| **Workflow automation** | "When record added/updated, then…" rules incl. a **Webhook** action | **Webhook-accessible**; rules are **Professional+** |
| **Marketing (email, scoring, A/B, journeys)** | Separately-licensed Marketing product | Mostly **UI-only**; some sync via AppConnect |
| **Service / Support (tickets, portals, KB)** | Separately-licensed Service product | Mostly **UI-only**; some sync via AppConnect |
| **AppConnect** | Built-in no-code iPaaS, 2,000+ app connectors | **UI-built**, runs server-side (task-metered) |
| **AI Copilot** | In-app CRM assistant | UI-only; Professional+ |

## Pricing, limits & plan gates

Best-effort, captured 2026-06; pricing changes frequently. **No permanent free tier** — 14-day trial. (A legacy "Free/Gratis" tier persists only as an API rate-limit bucket.)

**CRM** (per user/mo, billed annually):
- **Plus $29** — leads/contacts, projects, advanced reports, dashboards. Record cap 100,000, 10 GB files, mass email 2,500/day. **No** lead assignment/routing, workflow automation, AI Copilot, custom objects, products/quotes.
- **Professional $49** (recommended) — adds **lead assignment/routing, workflow automation (→ webhooks), AI Copilot**. Record cap 250,000, 100 GB, mass email 5,000/day.
- **Enterprise $99** (contact sales) — adds **custom objects, products/pricebooks/quotes, sandboxes, comprehensive audit logging**. Record cap 500,000, 250 GB, mass email 10,000/day.

**Marketing**: $99 (2k prospects) / $499 (10k) / $999 (20k) per account/mo. **Service**: $29 / $49 / $99 per user/mo. **AppConnect**: $249–$1,899/mo by monthly task volume (25K–250K tasks). **All-in-One bundle**: from $349 / $899 / $2,599 per month (up to ~30% combined savings).

**API daily request quota (per day, by plan)** — exceeding returns `429`:
- Free/Gratis (legacy): 1,000 · Legacy: 20,000 · Plus: 40,000 · Professional: 60,000 · Enterprise: 100,000
- Plus a **10 requests/second** ceiling across all plans.
- Headers: `X-RateLimit-Limit` (daily quota), `X-RateLimit-Remaining`.

**Integration gotcha:** the API works on Plus, but **workflow automation (and therefore webhooks) starts at Professional**, and **custom objects/products/quotes need Enterprise**. Confirm your tier before designing an integration around webhooks or custom objects.

## Integrations

- **Direction:** the v3.1 REST API is **bidirectional** (read + write) on CRM objects. **Webhooks push outbound only** (Insightly → your URL) and are created as workflow-rule actions.
- **AppConnect** (built-in iPaaS): 2,000+ connectors (Slack, Gmail, QuickBooks, Shopify, Salesforce, Xero, Jira, Workday, ZoomInfo, Unbounce…), drag-and-drop, task-metered pricing.
- **iPaaS:** Zapier, Make, Pipedream, and integration platforms wrap the REST API for no-code flows.
- **Native:** Google Workspace / Gmail, Microsoft 365 / Outlook, QuickBooks, Mailchimp, Xero, and more.

## Data model

Resources are British-spelled where applicable (**`Organisations`**, not `Organizations`). Field names are UPPER_SNAKE_CASE. Every record has `DATE_CREATED_UTC` and `DATE_UPDATED_UTC` (use the latter for incremental sync).

**Contact** (`GET /Contacts/{id}`):
```json
{
  "CONTACT_ID": 123456789,
  "FIRST_NAME": "Ada",
  "LAST_NAME": "Lovelace",
  "EMAIL_ADDRESS": "ada@example.com",
  "ORGANISATION_ID": 987654321,
  "TITLE": "Founder",
  "DATE_CREATED_UTC": "2026-06-01 14:03:22",
  "DATE_UPDATED_UTC": "2026-06-20 09:11:40",
  "TAGS": [{ "TAG_NAME": "newsletter" }],
  "CUSTOMFIELDS": [
    { "FIELD_NAME": "CONTACT_FIELD_1", "FIELD_VALUE": "Inbound" }
  ]
}
```
<!-- Constructed from documented Insightly field lists — verify against live API -->

**Opportunity** (`GET /Opportunities/{id}`):
```json
{
  "OPPORTUNITY_ID": 222333444,
  "OPPORTUNITY_NAME": "Website rebuild",
  "OPPORTUNITY_STATE": "OPEN",
  "OPPORTUNITY_VALUE": 24000,
  "BID_CURRENCY": "USD",
  "PROBABILITY": 60,
  "PIPELINE_ID": 555,
  "STAGE_ID": 5551,
  "FORECAST_CLOSE_DATE": "2026-07-15 00:00:00",
  "RESPONSIBLE_USER_ID": 11,
  "DATE_UPDATED_UTC": "2026-06-21 18:00:00",
  "CUSTOMFIELDS": []
}
```
<!-- Constructed from documented Insightly field lists — verify against live API -->

**Custom fields** are always an array of `{ "FIELD_NAME", "FIELD_VALUE" }` objects on the parent record. To set one, include it in the `CUSTOMFIELDS` array on a `POST`/`PUT`. Field names (e.g. `CONTACT_FIELD_1`) come from `GET /CustomFields/{objectName}`.

**Opportunity → Project**: converting a won opportunity creates a `Project` linked back via the opportunity; projects carry their own pipeline/stage, tasks, and (Enterprise) budgets. Project budgets do **not** roll up cleanly into the parent opportunity — a documented reporting limitation.

## Quick-start recipes

### Recipe 1 — Create a contact and an opportunity (cURL + Python)

Auth is HTTP Basic with the **API key as the username, Base64-encoded, blank password**. Find your **pod** (e.g. `na1`) under the API key in User Settings.

```bash
# Base64-encode "APIKEY:" (note the trailing colon = empty password)
ENC=$(printf '%s:' "$INSIGHTLY_API_KEY" | base64)

curl -sS -X POST "https://api.na1.insightly.com/v3.1/Contacts" \
  -H "Authorization: Basic $ENC" \
  -H "Content-Type: application/json" \
  -d '{ "FIRST_NAME": "Ada", "LAST_NAME": "Lovelace", "EMAIL_ADDRESS": "ada@example.com" }'
```

```python
import base64, requests

POD = "na1"                      # from User Settings, under your API key
BASE = f"https://api.{POD}.insightly.com/v3.1"
api_key = "YOUR_API_KEY"
enc = base64.b64encode(f"{api_key}:".encode()).decode()   # key as username, blank password
H = {"Authorization": f"Basic {enc}", "Content-Type": "application/json"}

contact = requests.post(f"{BASE}/Contacts", headers=H, json={
    "FIRST_NAME": "Ada", "LAST_NAME": "Lovelace",
    "EMAIL_ADDRESS": "ada@example.com",
}).json()

opp = requests.post(f"{BASE}/Opportunities", headers=H, json={
    "OPPORTUNITY_NAME": "Website rebuild",
    "OPPORTUNITY_STATE": "OPEN",
    "OPPORTUNITY_VALUE": 24000,
    "PIPELINE_ID": 555, "STAGE_ID": 5551,
}).json()
print(contact["CONTACT_ID"], opp["OPPORTUNITY_ID"])
```
**Gotchas:** un-encoded key → `401`; wrong pod → DNS/auth failure; custom fields go in the `CUSTOMFIELDS` array, not as top-level keys.

### Recipe 2 — Nightly incremental export within the daily quota

Pull only records changed since the last run, page with `top`/`skip`, and size the job with `count_total` on the first page only.

```python
import base64, requests, datetime

BASE = "https://api.na1.insightly.com/v3.1"
enc = base64.b64encode(f"{API_KEY}:".encode()).decode()
H = {"Authorization": f"Basic {enc}"}
since = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

skip, top, rows = 0, 500, []
params = {"updated_after_utc": since, "top": top, "skip": skip, "count_total": "true"}
while True:
    r = requests.get(f"{BASE}/Opportunities/Search", headers=H, params=params)
    if r.status_code == 429:
        # daily quota or 10 req/s ceiling hit — back off / stop for the day
        break
    batch = r.json()
    rows += batch
    if len(batch) < top:
        break
    skip += top
    params = {"updated_after_utc": since, "top": top, "skip": skip}  # drop count_total after page 1
print(len(rows), "opportunities; remaining:", r.headers.get("X-RateLimit-Remaining"))
```
**Gotchas:** `count_total=true` is extra cost — send it once; watch `X-RateLimit-Remaining`; `top` max is 500.

### Recipe 3 — Fire a webhook from a workflow rule (Professional+)

There is **no webhook-subscription API**. Build it in the UI: **Workflow Automation → new rule → Trigger** (record added/updated) **→ Action: Webhook**, set the target URI. On trigger Insightly POSTs the record's fields (Field IDs paired with values) to your URL. Make your receiver:
```python
from flask import Flask, request
app = Flask(__name__)

@app.post("/insightly-webhook")
def hook():
    payload = request.json          # { "TASK_ID": ..., "TITLE": ..., "STATUS": ..., ... }
    # ACK immediately, process async — Insightly retries only twice then gives up
    enqueue(payload)
    return "", 200
```
**Gotchas:** retries are **2 attempts** after the first failure, then the event is dropped; a downstream outage loses events — reconcile periodically on `DATE_UPDATED_UTC`. Webhooks require a plan that includes workflow automation (Professional+).

## Integration patterns

- **CRM sync architecture:** treat `DATE_UPDATED_UTC` as the watermark; upsert on the natural key (email for Contacts, name+domain for Organisations) since the API doesn't dedupe for you. Cache the pipeline/stage IDs and custom-field metadata (they rarely change) to avoid spending quota on lookups.
- **Webhook listener pattern:** ACK `2xx` in <2s and queue the work; because retries are minimal, pair webhooks with a nightly reconciliation pull so a missed delivery self-heals. Use the workflow rule's conditions to scope which records fire (avoid a firehose).
- **Batch/pagination pattern:** page with `top` (≤500) + `skip`; use the `*/Search?field_name=&field_value=` endpoints for filtered pulls; throttle to <10 req/s and stop on `429` until the daily quota resets. For large backfills, run during off-hours and checkpoint `skip` so a `429` mid-run is resumable.
- **Concurrency on updates:** Insightly returns an `ETag`; send it back as `If-Match` on `PUT` to avoid lost-update overwrites. Pre-v3.0 you had to send the whole object graph on update; v3.1 is more forgiving but still prefers complete objects.
