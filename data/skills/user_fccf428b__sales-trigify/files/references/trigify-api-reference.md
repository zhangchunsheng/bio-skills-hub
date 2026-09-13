<!-- Source: https://help.trigify.io/en/articles/27-making-api-calls -->
<!-- Source: https://help.trigify.io/en/articles/9504542-http-request -->

# Trigify API Reference

## Overview

Trigify has a minimal REST API with one documented endpoint. The primary automation surface is the **workflow system** (triggers, AI agents, enrichment nodes, integrations) — not traditional CRUD API endpoints.

## Authentication

- **Method**: API key via `x-api-key` header
- **Where to find**: Log in → Integrations page → API Key
- **Format**: Custom header (not Bearer token)

```bash
curl -X GET "https://app.trigify.io/api/sdr/YOUR_SDR_CODE/leads" \
  -H "x-api-key: YOUR_API_KEY"
```

## Endpoints

### GET /api/sdr/{sdrCode}/leads

Retrieve leads captured by a specific SDR workflow.

**Parameters:**
- `sdrCode` (path, required) — unique SDR identifier found in your Trigify dashboard

**Request:**
```bash
curl -X GET "https://app.trigify.io/api/sdr/abc123/leads" \
  -H "x-api-key: sk_live_..."
```

**Response:**
```json
[
  {
    "id": "lead_xyz789",
    "first_name": "Jane",
    "last_name": "Smith",
    "linkedin_url": "https://linkedin.com/in/janesmith",
    "company": "Acme Corp",
    "title": "VP of Sales",
    "email": "jane@acme.com",
    "signal_type": "competitor_engagement",
    "signal_details": {
      "post_url": "https://linkedin.com/posts/...",
      "engagement_type": "comment",
      "engagement_count": 5,
      "sentiment": "positive"
    },
    "created_at": "2026-05-07T14:30:00Z"
  }
]
```
<!-- Constructed from docs — verify against live API -->

## HTTP Request Node (outbound API calls from workflows)

The HTTP Request node is a workflow node that lets you call any external API from within a Trigify workflow. It is not a Trigify API endpoint — it's how Trigify calls *your* APIs.

**Configuration:**
| Setting | Details |
|---|---|
| Method | GET, POST, PUT, PATCH, DELETE |
| URL | Full API endpoint URL |
| Headers | Key-value pairs (Authorization, Content-Type, etc.) |
| Query Parameters | Key-value pairs appended as URL query strings |
| Body | JSON for POST, PUT, PATCH requests |

**Output variables:**
- `result` — API response body
- `statusCode` — HTTP status code (200, 400, etc.)
- `success` — boolean

**Example:**
```
Method: POST
URL: https://hooks.slack.com/services/T.../B.../xxx
Headers:
  Content-Type: application/json
Body:
{
  "text": "New signal: {{firstName}} {{lastName}} engaged with {{postUrl}}"
}
```

**Security**: Never hardcode API keys in HTTP Request nodes. Keys are visible to all workspace members who can view the workflow.

## Webhook Trigger (inbound)

Trigify workflows can be triggered by incoming webhooks. The Webhook Trigger node generates a unique URL that accepts POST requests.

**Payload schema**: Not publicly documented. The webhook body is available as workflow variables.

## Pagination

Not documented. The GET leads endpoint appears to return all leads without pagination parameters.

## Rate Limits

Not documented. No published rate cap for the API endpoint. Workflow execution is credit-gated (4K on Starter, 40K on Max).

## Gaps

- Only 1 documented API endpoint (GET leads). No endpoints for managing searches, workflows, contacts, or signals.
- No webhook payload schema documentation.
- No pagination, filtering, or sorting parameters documented for the leads endpoint.
- No rate limit headers or retry guidance.
- No OpenAPI/Swagger spec found.
- No Postman collection found.
- No MCP server.
