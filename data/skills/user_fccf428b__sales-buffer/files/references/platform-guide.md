# Buffer Platform Reference

## Overview

Buffer (buffer.com) is a **simple, transparent social media publishing/scheduling workspace** for
creators, solopreneurs, and small teams — its edge is ease of use and **value pricing**, not depth. Best
for queue-based scheduling across the major networks with light analytics and engagement. Watch-outs:
**per-channel pricing** that scales expensively for agencies, **no social listening**, and approval/
collaboration features gated to the Team plan.

## Capabilities & automation surface

| Module | What it does | Automation surface |
|---|---|---|
| Publish | Queue/schedule posts across 11 networks, drafts | **API** (GraphQL `createPost`; legacy `/updates/create`) |
| Create (Ideas) | Capture/organize content ideas → posts | **API** (ideas) + UI |
| Community | Reply to comments across channels | **UI-only** (no documented engagement API) |
| Analyze | Per-post + account metrics, reports | **API** (post metrics / reports) |
| Collaborate | Team approval workflows (**Team plan**) | **UI-only** |
| AI Assistant | Brainstorm/rewrite/platform-tailor posts | **UI-only** |
| Start Page | Customizable link-in-bio page | **UI-only** |
| Channels | Connect/manage social accounts | **API** (list channels/orgs) |

**Networks (11):** Bluesky, Facebook, Google Business Profile, Instagram, LinkedIn, Mastodon, Pinterest,
Threads, TikTok, X (Twitter), YouTube.

**Programmatic interfaces:** **GraphQL API** (`developers.buffer.com`, Bearer key from
`publish.buffer.com/settings/api`, plan-based rate limits — beta/free) + **legacy REST v1**
(`api.bufferapp.com/1/`, OAuth, 60/min, being deprecated). **No webhooks** (poll). No MCP. See
`references/buffer-api-reference.md`.

## Pricing, limits & plan gates

*Best-effort from research (2026-06) — verify on the live pricing page; Buffer prices **per channel**.*

| Plan | Price | Key limits |
|---|---|---|
| Free | $0 | **3 channels**, 10 queued posts/channel, **lifetime cap of 8 unique channel connections** |
| Essentials | **$5/channel/mo** (annual) / $6 monthly | unlimited queue, analytics, engagement, 1 user |
| Team | **$10/channel/mo** (annual) / $12 monthly | **approval workflows**, unlimited users, drafts |

- **Per-channel pricing compounds:** 10 channels on Essentials ≈ $600/yr; agencies feel this fast.
- **Team-gated:** approval workflows, advanced collaboration; **first-comment scheduling / hashtag manager**
  are also paid-tier features.
- **No social listening at all** — pair with a listening tool (`/sales-social-listening`) if you need it.
- **Free plan's 8-connection lifetime cap** counts every channel you've *ever* connected, even after
  disconnecting — a sneaky gotcha.

## Integrations

- **Direction:** API **writes** posts/drafts and **reads** channels + post metrics; there are **no
  webhooks**, so any "did it publish / what's the engagement" flow must **poll** within rate limits.
- **Auth:** GraphQL = Bearer API key (from publish.buffer.com/settings/api); legacy v1 = OAuth 2.0.
- **Native:** Canva, Google Drive, Dropbox, OneDrive, Unsplash, IFTTT, Zapier.

## Data model

Identity is the **channel** (a connected social account) under an **organization**.

**Channel** <!-- Constructed — verify -->
```json
{ "id": "ch_123", "service": "instagram", "serviceUsername": "@brand", "organizationId": "org_1" }
```

**Post** <!-- Constructed — verify -->
```json
{ "id": "post_456", "channelIds": ["ch_123"], "text": "New launch 🚀", "status": "scheduled",
  "scheduledAt": "2026-07-01T15:00:00Z", "metrics": { "impressions": 0, "likes": 0, "comments": 0 } }
```

## Quick-start recipes

### Recipe 1 — Auto-schedule a post from your app (GraphQL)

**Trigger:** new blog/product → schedule a Buffer post.
```bash
curl -s "https://graph.buffer.com/" -H "Authorization header uses an OAuth access token from the approved secret store -H "Content-Type: application/json" \
  -d '{"query":"mutation($i:CreatePostInput!){createPost(input:$i){id status scheduledAt}}",
       "variables":{"i":{"channelIds":["ch_123"],"text":"New post 🚀","scheduledAt":"2026-07-01T15:00:00Z","status":"scheduled"}}}'
```
```python
import requests
def schedule(channel_id, text, when, key):
    q = "mutation($i:CreatePostInput!){createPost(input:$i){id status}}"
    v = {"i": {"channelIds":[channel_id], "text": text, "scheduledAt": when, "status":"scheduled"}}
    r = requests.post("https://graph.buffer.com/", headers={"Authorization": f"Bearer {key}"},
                      json={"query": q, "variables": v}, timeout=30)
    r.raise_for_status(); return r.json()
```
**Gotchas:** get the key from **publish.buffer.com/settings/api**; media uses the **new Assets Input**
format (legacy format fails as of 2026-05-25); confirm the GraphQL host/schema in the live docs.

### Recipe 2 — Pull post performance into a dashboard (poll, no webhooks)

**Trigger:** scheduled job → query `posts(channelId, first, after)` for metrics, page via `pageInfo`, load
to your warehouse. Because Buffer has **no webhooks**, poll on a schedule that respects the **15-min/24-hr/
30-day** rate windows (e.g. once/hour, not every minute).

### Recipe 3 — Migrate a legacy v1 integration to GraphQL

**Trigger:** old `/updates/create.json` calls → swap to the GraphQL `createPost` mutation, replace the
OAuth `access_token` query param with a **Bearer API key**, and update media to the new Assets Input. Keep
the v1 path only until the migration guide says it's retired.

## Integration patterns

- **Poll, don't wait.** No webhooks means you poll for publish status and metrics — budget calls against
  the per-window limits and cache results; don't tight-loop.
- **Build on GraphQL, not v1.** The REST v1 surface is being deprecated; new work should target the
  GraphQL API and the new Assets Input.
- **Cost-model per channel.** Each connected account is billed; for many accounts/clients, compare against
  flat-rate tools before committing (strategy: `/sales-social-media-management`).
- **Listening lives elsewhere.** Buffer doesn't do social listening — route that to `/sales-social-listening`
  and a dedicated tool.
- **Expect network breakage.** Auto-publishing Stories, first comments, or Reels depends on each network's
  API; features can break when Instagram/TikTok/X change theirs — not a Buffer bug per se.
