<!-- Source: https://docs.sendr.io/ (OpenAPI 3.1.0 spec at https://api.sendr.io/openapi) — re-verified 2026-06-13 -->

# Sendr API Reference

**Base URL:** `https://api.sendr.io`
**Spec version:** OpenAPI 3.1.0 (`info.version`: 1.0.0)

## Authentication

Three methods supported (re-verified 2026-06-13 against live `api.sendr.io/openapi`):

1. **API Key** (recommended) — `X-API-Key` header. Generate from Sendr API Key settings.
2. **Bearer Token (JWT)** — `Authorization header uses an OAuth access token from the approved secret store header
3. **Session Cookie** — `sb-auth-auth-token.0` cookie

**Note on plan-gating:** Earlier docs gated API/webhooks to a "Pro" tier. As of 2026-06-13 the official pricing page (sendr.ai/pricing) shows a restructured Free Trial / Monthly ($119/mo) / Annual ($1,499/yr) lineup and no longer lists a separate "Pro" plan or an explicit API tier gate. Confirm current API access in your workspace settings — the OpenAPI spec itself declares no plan-based restriction.

## Endpoints

### Auth

#### GET `/seat/me`
Verify API key validity. Returns user info.

**Response fields:** workspace ID, seat ID, role, email, name, workspace name.

---

### Sheets

#### GET `/api/v1/sheet`
List sheets with pagination.

**Query params:**
- `offset` — pagination offset
- `limit` — 20-1000
- Filter by user, date, name, campaign

#### GET `/api/v1/sheet/{id}`
Retrieve a specific sheet.

#### GET `/api/v1/sheet/{id}/column`
Get sheet columns with metadata.

**Response fields:** name, dataType, format, display order, pinning, sorting, enrichment status.

#### POST `/api/v1/sheet/{sheetId}/row`
Add a row to a sheet.

**Body:** key-value pairs (string, number, boolean, null).

---

### Campaigns

#### GET `/api/v1/campaigns`
List campaigns with pagination, sorting, search, status filtering.

**Status values:** `DRAFT`, `ACTIVE`, `PAUSED`

#### GET `/api/v1/campaigns/{campaignId}`
Get campaign details.

---

### Sendr Page (Personalized Landing Pages)

#### GET `/api/v1/page-template/list`
List all page templates.

#### GET `/api/v1/page-template/{id}/variables`
Get template variables.

**Response fields:** tag, example, label, fallback.

#### POST `/api/v1/enrichment/sendr-page`
Generate a personalized page.

**Body (verbatim from live OpenAPI, 2026-06-13):**
- `templateId` (number, required) — page template to use
- `variablesValues` (object) — key-value pairs matching template variables
- `videoBackgroundUrl` (string, nullable) — prospect website / video background source
- `videoBackgroundType` (enum: `static` | `cursor` | `scroll`) — how the background renders
- `gifSource` (enum: `landing-page` | `video-thumbnail` | `dynamic-website`) — what the GIF preview is generated from
- `gifHyperlinkText` (string, nullable)
- `gifWebsiteUrl` (string, nullable)
- `attributes` (object, nullable) — additional metadata
- `webhookUrl` (string, nullable) — URL to receive completion notification

**Returns:** `pageId` (number), `pageUrl` (URI), `pagePreviewUrl` (URI), `availableTemplateKeys` (string[]), `variablesUsed` (object), `warnings` (string[]).

#### POST `/api/v1/enrichment/sendr-page-webhook`
Webhook endpoint Sendr calls to report page generation / engagement events.

**Event types (from OpenAPI):** `page_render:created`, `page_render:updated`, `contact_page_engagement:created`, `contact_page_engagement:updated`.
**Payload fields:** `attributes` (object), `eventStatus` (enum: `pending` | `done`).

---

### Dynamic Audio

#### POST `/api/v1/enrichment/dynamic-audio`
Queue audio generation with word replacement.

**Body (verbatim from live OpenAPI, 2026-06-13):**
- `audioUrl` (URI, required) — base audio to splice
- `elevenlabsId` (string, nullable) — optional ElevenLabs voice ID
- `targetWord` (string, required) — word to replace
- `replacementWord` (string, required) — personalized value
- `languageCode` (string, nullable)
- `webhookUrl` (URI, nullable) — completion notification

---

### Video

#### POST `/api/v1/enrichment/generate-video`
Queue video generation.

**Body (verbatim from live OpenAPI, 2026-06-13):**
- `audioUrl` (URI, required)
- `videoUrl` (URI, required)
- `muxAssetId` (string)
- `elevenlabsId` (string, nullable)
- `targetWord` (string, required) / `replacementWord` (string, required)
- `languageCode` (string, nullable)
- `pageSlug` (string, nullable)
- `mode` (enum: `merge` audio overlay | `lipsync` full generation | `video_only`)
- `webhookUrl` (URI, nullable)

---

### Webhooks

#### GET `/api/v1/webhook`
List workspace webhooks.

#### POST `/api/v1/webhook`
Create a webhook subscription.

**Body:** `name`, `url`, `events` (string array, nullable — no fixed enum in the spec), `attributes`.

**Signing:** Sendr signs deliveries with an `X-Webhook-Secret` header, generated when you register a webhook in Sendr Webhook settings. Validate inbound webhooks against this secret.

#### PATCH `/api/v1/webhook`
Update an existing webhook.

#### DELETE `/api/v1/webhook`
Delete a webhook.

#### POST `/api/v1/webhook/reveal-secret`
Retrieve the webhook signing secret. **Returns:** `{ "secret": "<string>" }` — the value sent in the `X-Webhook-Secret` header on deliveries.

#### POST `/api/v1/webhook/enabling`
Toggle webhook active/inactive status.

---

## Rate limits

Not publicly documented. Contact hello@sendr.io for rate limit details.

## SDKs

No official SDKs. Use the OpenAPI spec at `https://api.sendr.io/openapi` to generate clients.

## Support

- Email: hello@sendr.io
- Community: community.sendr.io
- Help center: help.sendr.io
