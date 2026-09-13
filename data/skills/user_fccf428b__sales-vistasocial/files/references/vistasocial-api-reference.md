<!-- Source: https://apidocs.vistasocial.com/ (Postman documenter; collection description re-verified 2026-06-13) -->
<!-- Source: https://support.vistasocial.com/hc/en-us/articles/32993061787035-Vista-Social-API -->
<!-- Source: https://support.vistasocial.com/hc/en-us/articles/44656690553371-OAuth-2-0 -->

# Vista Social API Reference

## Status

Re-verified 2026-06-13 against the official Postman-hosted docs at apidocs.vistasocial.com (collection description) plus the Vista Social support center API/OAuth articles. The collection description (authentication, OAuth flow, provisioning) was retrieved verbatim. Individual request items (exact endpoint paths and response schemas) are rendered client-side in the Postman documenter and could NOT be extracted — those specifics remain unverified below.

## Overview

Vista Social API provides external access to your **owned social profile data** for powering dashboards and automating reporting, plus **write** operations (create posts, ideas, notes, and upload media). Per the official docs: "Before accessing the API, **your account must be provisioned for API use by your Vista Social account representative.**" It is offered as a paid **API add-on** (public pricing not listed). Note: Zapier and Make do **not** require the API add-on as long as you are on Advanced/Scale/Enterprise (unless making custom API calls); **n8n always requires the API add-on** because it uses direct API calls.

## Authentication

Vista Social API supports **2 forms of authentication**:

### 1. API Key
- **Generated from**: Settings → Integrations in the Vista Social dashboard
- **Header**: Pass an **`api-key`** header on every request (this is the documented header name — it is NOT `Authorization: Bearer`)

```bash
# API key auth — pass the api-key header
curl -H "api-key: YOUR_API_KEY" \
  https://apidocs.vistasocial.com/  # see live docs for exact base URL + endpoint paths
```

### 2. OAuth 2.0 (Authorization Code flow with PKCE S256)
Contact support to set up your OAuth 2.0 client. Endpoints:
- **Authorize**: `https://vistasocial.com/api/oauth/authorize`
- **Token**: `https://vistasocial.com/api/oauth/token`
- **Who am I (debug)**: `https://vistasocial.com/api/oauth/me`

Authorization Code + PKCE flow:
1. Redirect user to `GET /api/oauth/authorize` with query params: `response_type=code`, `client_id`, `redirect_uri` (must match a registered URI), `scope` (space-delimited, optional), `state` (recommended, returned unchanged for CSRF protection), `code_challenge` (PKCE), `code_challenge_method=S256`, `resource` (optional resource indicator, e.g. your MCP server URL).
2. Vista Social redirects back to `redirect_uri` with `code` (and `state`).
3. Exchange code: `POST /api/oauth/token` with `Content-Type: application/x-www-form-urlencoded`, client auth via Basic Auth or `client_id`/`client_secret` in body, and body fields `grant_type=authorization_code`, `code`, `redirect_uri`, `code_verifier`, optional `resource`.
4. Refresh: `POST /api/oauth/token` with `grant_type=refresh_token`, `refresh_token`.

**Token notes**: tokens are opaque strings (not JWTs) — access tokens are prefixed `tk_`, refresh tokens `rt_`. PKCE S256 is enforced when `code_challenge` is used. The OAuth server also supports the client-credentials grant (server-to-server) and a legacy password grant for controlled scenarios.

## Known endpoints

Capabilities confirmed from the official API docs and support articles (exact paths still client-side-rendered — see Gaps):

| Category | Capability | Source |
|---|---|---|
| **Profile data** | Get owned social profile metrics (matches Social Media Performance report) | API |
| **Post data** | Get published post metrics (matches Post Performance Report) | API |
| **Comment data** | Get comment details and metadata | API |
| **Schedule posts** | Create/schedule posts to connected profiles | API + Zapier/Make |
| **Ideas** | Create ideas | API + Zapier/Make |
| **Notes** | Create notes | API + Zapier/Make |
| **Media** | Upload media (image/video/GIF) to the media library | API |
| **Profile groups** | Create/edit profile groups | Zapier/Make (PREMIUM) |
| **Team** | Invite team members, edit team members | Zapier/Make |
| **Inbox** | Get inbox items (comments, messages) | Zapier (PREMIUM) |
| **Metrics** | Get daily profile metrics | Zapier (PREMIUM) |
| **Post metrics** | Get published post metrics | Zapier (PREMIUM) |
| **Reply** | Reply to comments, messages, reviews, mentions | Zapier (PREMIUM) |

## Pagination

Not documented in fetchable sources. Based on typical REST API patterns, likely offset-based or cursor-based pagination.

## Rate limits

- **Direct API / MCP**: 60 requests/minute (3,600/hour). Each response includes an **`x-vs-rate-limit-remaining`** header showing the remaining calls allowed in the current minute. On a rate-limit error, pause for a minute. **If you violate the rate limit more than 10 times per hour, your key is deactivated.**
- **Zapier/Make**: 60 requests/minute (3,600/hour)

## Data not available via API

- Paid/Ad Account data — not exposed
- X/Twitter data — excluded from API
- Social listening data — not exposed via API
- DM automation data — UI-only
- Employee advocacy data — UI-only

## MCP Server (AI assistant integration)

Vista Social ships an official **remote MCP server** so AI assistants (Claude, ChatGPT, etc.) can act on your account.
- **Setup**: copy the **Remote MCP Server URL** ("MCP link") from your Vista Social integrations settings, then add it as a connector in your AI tool. In Claude: Search & tools → Add connectors → paste the Remote MCP Server URL → select **"No authentication"** (your API key is already embedded in the server URL).
- **Requirements**: a Vista Social account with MCP enabled and a paid AI account.
- **Tools**: **47 MCP tools** across 9 categories — publishing & scheduling, reports & analytics, inbox & community management, tasks & workflows, accounts, profiles & teams, Vista Pages, help & documentation, and utilities. Examples: "Create or update a post" (draft/schedule/edit across one or more connected profiles), "Add internal team comment to post", "Create media" (upload image/video/GIF to the media library).
- **Rate limit**: 60 requests/minute, same `x-vs-rate-limit-remaining` header as the REST API.
- Source: https://support.vistasocial.com/hc/en-us/articles/40393513382043-MCP-Server , https://support.vistasocial.com/hc/en-us/articles/46525029430299-Vista-Social-s-Available-MCP-Tools

## iPaaS surface (alternative programmatic interface)

For users without the API add-on, **Zapier and Make** (included on Advanced+) are the primary programmatic interface. **n8n** uses direct API calls and therefore **always requires the API add-on**, regardless of plan.

### Zapier (7 triggers, 11 actions)

**Triggers:**
1. `post_failed` — Post Failed to Publish
2. `draft_created` — New Draft Is Created
3. `internal_comment` — New Internal Post Comment
4. `post_scheduled` — New Post Is Scheduled
5. `post_published` — New Post Is Published
6. `post_rejected` — Post Has Been Rejected
7. `post_review` — Post Needs to Be Reviewed

**Actions:**
1. `create_idea` — Create a new idea
2. `create_note` — Create a new note
3. `schedule_post` — Schedule a new post
4. `create_internal_comment` — Create internal post comment
5. `create_profile_group` — Create profile group (PREMIUM)
6. `edit_profile_group` — Edit profile group (PREMIUM)
7. `invite_team_member` — Invite team member
8. `reply` — Reply to comment/message/review/mention (PREMIUM)
9. `get_daily_metrics` — Get daily profile metrics (PREMIUM)
10. `get_inbox` — Get inbox items (PREMIUM)
11. `get_post_metrics` — Get post metrics (PREMIUM)

### Make (12 modules)

**Actions:**
1. Create a New Idea
2. Create a New Internal Post Comment
3. Create a New Note
4. Create a New Profile Group (PREMIUM)
5. Delete Scheduled Post
6. Edit Profile Group (PREMIUM)
7. Edit Team Member
8. Get Profile Groups
9. Schedule a New Post
10. Update Scheduled Post

**Trigger:**
11. Watch Scheduled Posts

**Utility:**
12. Make an API Call (custom endpoint access)

## Gaps (still unverified as of 2026-06-13)

- Full REST endpoint paths + response schemas — the Postman documenter renders request items client-side; only the collection description (auth/OAuth/provisioning) was extractable. The official base URL for REST calls is not stated in the extractable text.
- Pagination pattern — not documented in extractable sources
- Error response format — not documented in extractable sources
- Webhook support — no outbound webhooks documented (confirmed absent in current docs)
- API add-on pricing — not public

**Resolved since prior version**: auth header is `api-key` (confirmed); OAuth 2.0 is supported (confirmed, full flow above); direct-API rate limit is 60/min with `x-vs-rate-limit-remaining` header (confirmed); API supports writes (create posts/ideas/notes, upload media); account must be provisioned by a Vista Social account representative.
