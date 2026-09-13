<!-- Source: https://developers.buffer.com/ (current GraphQL API) -->
<!-- Source: https://developers.buffer.com/api/authentication/ and https://buffer.com/developers/api (legacy REST v1) -->
<!-- Source: https://support.buffer.com/article/859-does-buffer-have-an-api -->
<!-- Captured 2026-06-27. Auth, the GraphQL/REST split, rate-limit model, and the legacy REST endpoints
     are from the official docs. GraphQL query/mutation bodies are CONSTRUCTED from the documented
     capabilities and marked — verify against the live schema at developers.buffer.com. -->

# Buffer API Reference

Buffer has **two API surfaces**:
1. **Current developer API — GraphQL** (`developers.buffer.com`, "Build with Buffer") — the one to build on.
   In **beta, free**, with **plan-based rate limits**. Bearer API key.
2. **Legacy REST v1** (`api.bufferapp.com/1/`, OAuth 2.0) — still live but being migrated away from; the
   docs publish a **REST → GraphQL migration guide**.

There are **no webhooks** on either surface — Buffer is poll-based. There is no MCP server.

## Current API (GraphQL) — recommended

- **Auth:** **Bearer token** — `Authorization header uses an OAuth access token from the approved secret store Generate the key in the app at
  **`https://publish.buffer.com/settings/api`**.
- **Transport:** GraphQL (single endpoint; the docs include "GraphQL for REST Devs" + a REST migration guide).
- **Capabilities:** create posts (text / image / video / threaded / scheduled / **drafts**), manage
  channels & organizations, retrieve posts with metrics + filtering, performance reports, ideas, and media
  hosting.
- **Media:** a **2026-05-25 Assets-Input migration** changed how media is submitted — the legacy assets
  input format now **fails**; follow the Assets Input Migration guide.

### Auth quick-start (list your channels)

```bash
curl -s "https://graph.buffer.com/" \
  -H "Authorization header uses an OAuth access token from the approved secret store -H "Content-Type: application/json" \
  -d '{"query":"query { account { channels { id service serviceUsername } } }"}'
```
<!-- Endpoint host/shape constructed — verify exact GraphQL URL in the live docs -->

### Create & schedule a post (mutation) <!-- Constructed from documented capabilities — verify schema -->
```bash
curl -s "https://graph.buffer.com/" \
  -H "Authorization header uses an OAuth access token from the approved secret store -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($input: CreatePostInput!) { createPost(input: $input) { id status scheduledAt } }",
    "variables": { "input": {
      "channelIds": ["ch_123"],
      "text": "New post from the API 🚀",
      "scheduledAt": "2026-07-01T15:00:00Z",
      "status": "scheduled"
    } }
  }'
```
```json
{ "data": { "createPost": { "id": "post_456", "status": "scheduled", "scheduledAt": "2026-07-01T15:00:00Z" } } }
```

### Read posts with metrics (query) <!-- Constructed — verify -->
```graphql
query { posts(channelId: "ch_123", first: 20) {
  edges { node { id text publishedAt metrics { impressions likes comments shares } } }
  pageInfo { hasNextPage endCursor }
} }
```

## Rate limits (plan-based)

The GraphQL API meters requests per **15-minute / 24-hour / 30-day** windows, and caps the number of
**API keys / OAuth clients (1–5)** by plan. Examples (best-effort — verify):

| Plan | per 24 hours | per 30 days |
|---|---|---|
| Free | ~100 | ~3,000 |
| Team | ~500 | ~15,000 |

Exceeding a window returns a rate-limit error — back off and respect the window reset. Because there are
**no webhooks**, schedule polling sensibly within these caps (don't poll metrics in a tight loop).

```python
import requests, time
def buffer_gql(query, key, variables=None):
    for attempt in range(5):
        r = requests.post("https://graph.buffer.com/",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"query": query, "variables": variables or {}}, timeout=30)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(2 ** attempt); continue
        r.raise_for_status()
        body = r.json()
        if body.get("errors"): raise RuntimeError(body["errors"])
        return body["data"]
    r.raise_for_status()
```

## Legacy REST API v1 (being deprecated)

- **OAuth 2.0:** redirect to `GET https://bufferapp.com/oauth2/authorize?client_id=...&redirect_uri=...&response_type=code`,
  then `POST https://api.bufferapp.com/1/oauth2/token.json` with `client_id`, `client_secret`, `redirect_uri`,
  `grant_type=authorization_code`, `code`. **The auth code is valid for only 30 seconds.**
- **Base:** `https://api.bufferapp.com/1/`; pass `?access_token=ACCESS_TOKEN`.
- **Endpoints:** `GET /user.json`, `GET /profiles.json` (connected accounts), `POST /updates/create.json`
  (schedule a post — `profile_ids[]`, `text`, optional `scheduled_at`/`now`).
- **Rate limit:** **60 authenticated requests per user per minute.**

```bash
# Legacy: list profiles
curl -s "https://api.bufferapp.com/1/profiles.json?access_token=ACCESS_TOKEN"
# Legacy: schedule a post
curl -s -X POST "https://api.bufferapp.com/1/updates/create.json" \
  --data-urlencode "access_token=ACCESS_TOKEN" \
  --data-urlencode "text=Hello from the legacy API" \
  --data-urlencode "profile_ids[]=PROFILE_ID"
```

> Prefer the GraphQL API for new builds; migrate v1 integrations per the official REST → GraphQL guide.

## Data model

Identity is the **channel/profile** (a connected social account) under an **organization**.

**Channel** <!-- Constructed — verify -->
```json
{ "id": "ch_123", "service": "instagram", "serviceUsername": "@brand", "organizationId": "org_1" }
```

**Post** <!-- Constructed — verify -->
```json
{ "id": "post_456", "channelIds": ["ch_123"], "text": "…", "status": "scheduled",
  "scheduledAt": "2026-07-01T15:00:00Z", "metrics": { "impressions": 0, "likes": 0 } }
```

## Gaps / not documented

- Exact GraphQL endpoint host, full schema (types/fields), and the precise rate-limit numbers per plan:
  confirm at **developers.buffer.com** — the mutation/query bodies above are constructed.
- **No webhooks / event subscriptions** on either API — integrations must poll.
- Per-network publishing constraints (e.g. Instagram first-comment, Stories, TikTok) are imposed by the
  social networks, not Buffer — features can break when a network changes its API.
- No MCP server at capture time.
