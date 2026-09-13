<!-- Source: https://api.na1.insightly.com/v3.1/ (Insightly API v3.1 Help) ; https://support.insight.ly/en-us/Knowledge/article/1447/Working_with_the_Insightly_Web_API/ ; https://support.insight.ly/en-us/Knowledge/article/1420/What_are_webhooks_in_the_workflow_automation -->

# Insightly Web API v3.1 Reference

Captured from live sources 2026-06. Endpoint paths follow Insightly's documented RESTful convention; representative JSON bodies are marked where constructed from documented field lists. Re-verify specifics against `https://api.{pod}.insightly.com/v3.1/Help#!` before relying on them.

## Base URL

```
https://api.{pod}.insightly.com/v3.1/
```

Your instance's **pod** is shown in the web app under **User Settings → API** (right beneath your API key). Example: if your pod is `na1`, the base URL is `https://api.na1.insightly.com/v3.1/`. Common pods include `na1` (North America) and `eu1` (Europe). Using the wrong pod presents as an auth/DNS failure.

## Authentication

Insightly uses **HTTP Basic authentication**. Each user has an **API key** (User Settings → API).

- The **API key is the username**; the **password is blank**.
- The key must be **Base64-encoded** in the `Authorization` header. If you don't Base64-encode it, you get a **401** authentication error.
- You do **not** need to manually Base64-encode the key when using the interactive Sandbox on the Help page (it encodes for you) — which is why code that fails often "works" in the sandbox.

```
Authorization: Basic {base64( "APIKEY:" )}
```

### Auth quick-start (cURL)

```bash
ENC=$(printf '%s:' "$INSIGHTLY_API_KEY" | base64)   # trailing colon = empty password
curl -sS "https://api.na1.insightly.com/v3.1/Contacts?top=1" \
  -H "Authorization: Basic $ENC"
```

```python
import base64, requests
enc = base64.b64encode(f"{API_KEY}:".encode()).decode()
r = requests.get("https://api.na1.insightly.com/v3.1/Contacts",
                 headers={"Authorization": f"Basic {enc}"}, params={"top": 1})
```

## HTTP methods

- **GET** — retrieve information
- **POST** — add new records
- **PUT** — update records (send the full object; use `If-Match` with the record's `ETag` for optimistic concurrency)
- **DELETE** — remove records

## Content & encoding

- **Content-Type:** `application/json` (default). XML is also accepted on some endpoints by sending `Content-Type: text/xml`, but JSON is standard.
- **Compression:** supports GZIP/DEFLATE via the `Accept-Encoding` header.
- **Dates:** URL parameters use ISO 8601 (`yyyy-mm-ddThh:mm:ssZ`); object data fields use `yyyy-MM-dd HH:mm:ss`. Sync on `DATE_UPDATED_UTC`.

## Pagination

| Param | Meaning |
|---|---|
| `top` | Number of records to return. **Default 100, max 500.** |
| `skip` | Skip the first N records (offset paging). |
| `count_total=true` | Returns the total record count in the **`X-Total-Count`** response header. Adds cost — request it once, not on every page. |

Page by incrementing `skip` by `top` until a page returns fewer than `top` records.

## Rate limiting

- **Per-second ceiling:** maximum **10 requests/second** (all plans).
- **Daily quota (per day, by plan):**

| Plan | Requests/day |
|---|---|
| Free / Gratis (legacy) | 1,000 |
| Legacy | 20,000 |
| Plus | 40,000 |
| Professional | 60,000 |
| Enterprise | 100,000 |

- Exceeding either limit returns **HTTP 429**.
- **Response headers:** `X-RateLimit-Limit` (daily quota), `X-RateLimit-Remaining` (requests left in the rolling 24h period).

## Concurrency (ETag / If-Match)

`GET` responses include an `ETag`. On `PUT`, send `If-Match: {etag}` so a stale update is rejected (HTTP 412) instead of silently overwriting newer data.

## Resources / endpoints

Standard RESTful pattern per object: `GET /{Resource}`, `GET /{Resource}/{id}`, `POST /{Resource}`, `PUT /{Resource}`, `DELETE /{Resource}/{id}`, plus filtered search `GET /{Resource}/Search?field_name={field}&field_value={value}`.

| Resource | Notes |
|---|---|
| `/Contacts` | People. Sub-resources for links, tags, notes, tasks, events, emails, dates, image. |
| `/Organisations` | Companies (**British spelling**). Same sub-resource pattern as Contacts. |
| `/Leads` | Pre-conversion leads; `POST /Leads/{id}/Convert` converts to Contact/Org/Opportunity. |
| `/Opportunities` | Deals; `OPPORTUNITY_STATE` = OPEN/WON/LOST/ABANDONED/SUSPENDED; links to `PIPELINE_ID`/`STAGE_ID`. |
| `/Projects` | Post-sale delivery records; created from a won opportunity. |
| `/Tasks` | Activities/to-dos with `STATUS`, `PRIORITY`, `DUE_DATE`. |
| `/Events` | Calendar events. |
| `/Notes` | Notes attachable to any record. |
| `/Pipelines` | Pipeline definitions (read). |
| `/PipelineStages` | Stage definitions within a pipeline (read). |
| `/Tags` | Tag list and bulk tag operations (v3.1 bulk tag updates). |
| `/CustomFields/{objectName}` | Custom-field metadata for an object type (field names + types). |
| `/Products`, `/Pricebooks`, `/PricebookEntries`, `/Quotes`, `/QuoteLineItems` | CPQ objects — **added in v3.1; Enterprise-only**. |
| `/Users` | Insightly users. |
| `/TeamMembers`, `/Teams` | Team membership. |
| `/Relationships` | Relationship type definitions. |
| `/Currencies`, `/CustomObjects`, `/CustomObjectRecords` | Reference data + custom objects (**Enterprise-only**). |

v3.1 additions over v3.0: **Products, Price Books, Quotes** endpoints and **bulk tag / date / domain** update operations.

### Example: list contacts (GET)

```
GET /v3.1/Contacts?top=2&skip=0&count_total=true
Authorization: Basic {base64("APIKEY:")}
```
Response (200) — array of contact objects; `X-Total-Count` header carries the total:
```json
[
  {
    "CONTACT_ID": 123456789,
    "FIRST_NAME": "Ada",
    "LAST_NAME": "Lovelace",
    "EMAIL_ADDRESS": "ada@example.com",
    "ORGANISATION_ID": 987654321,
    "DATE_CREATED_UTC": "2026-06-01 14:03:22",
    "DATE_UPDATED_UTC": "2026-06-20 09:11:40",
    "TAGS": [{ "TAG_NAME": "newsletter" }],
    "CUSTOMFIELDS": [
      { "FIELD_NAME": "CONTACT_FIELD_1", "FIELD_VALUE": "Inbound" }
    ]
  }
]
```
<!-- Constructed from documented Insightly field lists — verify against live API -->

### Example: create a contact (POST)

```
POST /v3.1/Contacts
Content-Type: application/json
Authorization: Basic {base64("APIKEY:")}

{ "FIRST_NAME": "Grace", "LAST_NAME": "Hopper", "EMAIL_ADDRESS": "grace@example.com" }
```
Returns `201` with the created object including `CONTACT_ID`.

### Example: update with concurrency (PUT)

```
PUT /v3.1/Contacts
If-Match: "{etag-from-prior-GET}"
Content-Type: application/json

{ "CONTACT_ID": 123456789, "FIRST_NAME": "Ada", "LAST_NAME": "Lovelace", "TITLE": "CTO" }
```
Send the complete object. A stale `If-Match` returns `412 Precondition Failed`.

### Example: create an opportunity (POST)

```json
{
  "OPPORTUNITY_NAME": "Website rebuild",
  "OPPORTUNITY_STATE": "OPEN",
  "OPPORTUNITY_VALUE": 24000,
  "BID_CURRENCY": "USD",
  "PIPELINE_ID": 555,
  "STAGE_ID": 5551,
  "FORECAST_CLOSE_DATE": "2026-07-15 00:00:00"
}
```
<!-- Constructed from documented Insightly field lists — verify against live API -->

### Custom fields

Custom fields are a **`CUSTOMFIELDS` array** of `{ "FIELD_NAME", "FIELD_VALUE" }` pairs on the parent record (not top-level keys). Discover field names + types via `GET /CustomFields/{objectName}` (e.g. `Contact`, `Organisation`, `Opportunity`). Include the array on `POST`/`PUT` to set values.

## Error responses

| Status | Meaning |
|---|---|
| 400 | Bad request (malformed body / invalid field). |
| 401 | Unauthorized — almost always the API key wasn't Base64-encoded, or wrong pod. |
| 402 | Payment required / plan limit. |
| 404 | Resource or record not found. |
| 412 | Precondition failed (stale `If-Match` ETag). |
| 429 | Rate limit exceeded (10 req/s ceiling or the daily quota). |

### Rate-limit retry snippet

```python
import time, requests

def get(url, headers, params=None, tries=5):
    for i in range(tries):
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 429:
            return r
        # daily quota or per-second ceiling. Check remaining; back off.
        remaining = r.headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            raise RuntimeError("Daily quota exhausted — stop until reset")
        time.sleep(2 ** i)   # exponential backoff for the per-second ceiling
    return r
```

## Webhooks (workflow automation)

Insightly has **no webhook-subscription API**. Webhooks are created as an **action inside a Workflow Automation rule** (workflow automation is **Professional+**).

- **Setup:** Workflow Automation → create a rule → set the **Trigger** (record **added or updated**) → add a **Webhook** action with a descriptive name and the **URI** to POST to.
- **Trigger:** fires when a record is added or updated and the rule conditions match.
- **Payload:** an HTTP `POST` containing a collection of the record's **Field IDs paired with their values**. Example fields for a Task webhook: `TASK_ID`, `TITLE`, `CATEGORY_ID`, `DUE_DATE`, `STATUS`, `PRIORITY`, plus timestamps.
- **Auth on the callback:** Insightly's webhooks support **HTTP Basic authentication** — you can configure a Base64-encoded username/password that Insightly will send to your endpoint. (Some third-party integration guides also reference an `x-insightly-signature` HMAC-SHA256 header for verification; confirm against current docs before relying on it.)
- **Retries:** if there is **no positive acknowledgement**, Insightly **tries two more times and then stops** attempting to send that event. A brief outage drops events — pair webhooks with a periodic reconciliation pull on `DATE_UPDATED_UTC`.

Example receiver:
```python
from flask import Flask, request
app = Flask(__name__)

@app.post("/insightly-webhook")
def hook():
    payload = request.json          # { "TASK_ID": ..., "STATUS": ..., ... }
    enqueue(payload)                # ACK fast, process async (only 2 retries)
    return "", 200
```

## Gaps

- The live Help page renders the per-endpoint schemas (request/response field tables) interactively; full per-field schemas for every resource were not captured verbatim and should be confirmed at `https://api.{pod}.insightly.com/v3.1/Help#!`.
- The exact set of available pods beyond `na1`/`eu1` is account-specific (read it from User Settings).
