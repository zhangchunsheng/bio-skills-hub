# Vista Social Platform Reference

## Overview

Vista Social is an all-in-one social media management platform supporting 15+ networks (Instagram, Facebook, LinkedIn, X/Twitter, TikTok, YouTube, Pinterest, Reddit, Threads, Tumblr, Snapchat, Bluesky). Differentiated by bundled pricing (not per-seat), built-in review management, and DM automations with lead collection. G2 rating: 4.8/5 (1,071 reviews). Target audience: growing brands, agencies, and small marketing teams.

## Capabilities & automation surface

| Capability | Description | Access |
|---|---|---|
| **Publishing & scheduling** | Schedule posts to 15+ social networks, bulk scheduling, content calendar, AI-generated captions/hashtags, Canva integration, optimal timing | API + Zapier/Make |
| **Unified inbox** | Comments, DMs, reviews, mentions across all connected profiles in one view, assignment, tagging | Zapier (Get Inbox — PREMIUM) |
| **Analytics & reporting** | Performance reports per profile/post, custom date ranges, white-label (Scale+), Looker Studio connector | API (profile/post metrics) + Zapier (Get Daily Metrics — PREMIUM) |
| **Social listening** | Keyword monitoring across social, web, news. Sentiment filtering. $75/mo add-on per listener | UI-only (no API for listening data) |
| **Review management** | Monitor and reply to reviews on Google, Facebook, Yelp, TripAdvisor, OpenTable, Trustpilot | Zapier (Reply — PREMIUM) |
| **DM automations** | Automated DM flows with lead collection, keyword triggers, auto-replies. Advanced+ only. Up to 100K contacts on Scale | UI-only |
| **Employee advocacy** | Curated content for employees to share. $199/mo add-on (3 advocates free) | UI-only |
| **Vista Page** | Link-in-bio landing page builder | UI-only |
| **AI Assistant** | ChatGPT-powered content generation, hashtag suggestions, caption writing. Unlimited on Scale+ | UI-only |
| **AI Training & Knowledge** | Train AI on your brand voice for automated responses. Advanced+ only | UI-only |
| **Content ideas** | Idea capture and collaboration with labels and profile group assignment | API + Zapier/Make |
| **Notes** | Internal notes per profile group with dates and visibility | API + Zapier/Make |
| **Team management** | Roles, permissions, approval workflows. Custom fields on Advanced+ | Zapier (Invite Team Member) |
| **Profile groups** | Organize social profiles into groups (useful for agencies managing clients) | Zapier/Make (PREMIUM) |

## Pricing, limits & plan gates

| Feature | Professional $79/mo | Advanced $149/mo | Scale $349/mo | Enterprise (custom) |
|---|---|---|---|---|
| Social profiles | 15 | 30 | 70 | Unlimited |
| Team members | 3 | 6 | 10 | Unlimited |
| Zapier/Make/n8n | No | Yes | Yes | Yes |
| API add-on | Available (extra) | Available (extra) | Available (extra) | Included |
| DM automations | No | Yes (10K contacts) | Yes (100K contacts) | Yes (unlimited) |
| AI Training & Knowledge | No | Yes | Yes | Yes |
| Custom fields | No | Yes | Yes | Yes |
| White-label reports | No | No | Yes | Yes |
| Approval workflows | Basic | Advanced | Advanced | Advanced |
| Sentiment on inbox | No | No | No | Yes |
| SAML SSO | No | No | No | Yes |
| Dedicated account manager | No | No | No | Yes |

**Add-ons (all plans):**
- Social listening: $75/mo for broader social/web/news monitoring (own-profile listening is free)
- Employee advocacy: $199/mo for 25 employees (3 advocates free)
- X (Twitter) integration: $29/mo (due to X API pricing)
- API: paid add-on (public pricing not listed). Required for direct API + n8n; NOT required for Zapier/Make on Advanced+ unless making custom API calls.

**AI credits (monthly):** Professional 2,500 · Advanced 10,000 · Scale & Enterprise unlimited.

**Annual billing**: 20% discount on all plans.

## Integrations

| Integration | Direction | Plan required |
|---|---|---|
| Zapier | Bidirectional (7 triggers, 11 actions) | Advanced+ (no API add-on needed unless custom API calls) |
| Make | Bidirectional (1 trigger, 11 actions) | Advanced+ (no API add-on needed unless custom API calls) |
| n8n | Bidirectional (direct API calls) | Advanced+ **and** API add-on (always required) |
| MCP Server | AI assistants (Claude/ChatGPT) act on your account via 47 tools | API add-on / MCP-enabled account |
| Canva | Import designs into posts | All |
| Google Business | Publishing + review management | All |
| Looker Studio | Export analytics data | All (via connector) |
| Vista Social API | Read profiles/posts/comments + write (schedule posts, create ideas/notes, upload media) | API add-on; provisioned by account rep |

**No native CRM connectors.** CRM sync requires Zapier/Make middleware.

**MCP Server**: official remote MCP server exposes 47 tools (publishing & scheduling, reports & analytics, inbox & community, tasks & workflows, accounts/profiles/teams, Vista Pages, help, utilities). Copy the Remote MCP Server URL from integrations settings and add it as a connector in Claude/ChatGPT with "No authentication" (the API key is embedded in the URL). 60 req/min limit. See `vistasocial-api-reference.md`.

**Auth (direct API)**: pass an **`api-key`** header (not `Authorization: Bearer`), or use OAuth 2.0 (Authorization Code + PKCE S256) via `vistasocial.com/api/oauth/{authorize,token,me}`. Opaque tokens prefixed `tk_`/`rt_`. Direct-API rate limit 60/min with `x-vs-rate-limit-remaining` header.

### Zapier triggers
1. Post Failed to Publish
2. New Draft Is Created
3. New Internal Post Comment
4. New Post Is Scheduled
5. New Post Is Published
6. Post Has Been Rejected
7. Post Needs to Be Reviewed

### Zapier actions
1. Create Idea
2. Create Note
3. Schedule Post
4. Create Internal Post Comment
5. Create a Profile Group (PREMIUM)
6. Edit a Profile Group (PREMIUM)
7. Invite Team Member
8. Reply (PREMIUM)
9. Get Daily Metrics (PREMIUM)
10. Get Inbox (PREMIUM)
11. Get Post Metrics (PREMIUM)

### Make modules
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
11. Watch Scheduled Posts (trigger)
12. Make an API Call (utility)

**Rate limit**: 60 requests/minute (3,600/hour) on Zapier/Make.

## Data model

### Post object
<!-- Constructed from docs — verify against live API -->
```json
{
  "id": "post_abc123",
  "message": "Check out our new feature! #launch",
  "profiles": ["profile_001", "profile_002"],
  "media": [
    {
      "type": "image",
      "url": "https://example.com/image.jpg"
    }
  ],
  "scheduled_at": "2026-05-10T14:00:00Z",
  "status": "scheduled",
  "published_at": null,
  "metrics": {
    "impressions": 0,
    "engagements": 0,
    "clicks": 0
  }
}
```

### Profile object
<!-- Constructed from docs — verify against live API -->
```json
{
  "id": "profile_001",
  "name": "Acme Corp",
  "platform": "instagram",
  "username": "@acmecorp",
  "profile_group_id": "group_abc",
  "connected": true,
  "metrics": {
    "followers": 12500,
    "posts": 340
  }
}
```

### Inbox item object
<!-- Constructed from docs — verify against live API -->
```json
{
  "id": "inbox_xyz",
  "type": "comment",
  "platform": "facebook",
  "profile_id": "profile_002",
  "author": "Jane Doe",
  "message": "Love this product!",
  "sentiment": "positive",
  "created_at": "2026-05-04T09:30:00Z",
  "replied": false
}
```

## Quick-start recipes

### Recipe 1: Schedule a post via Zapier when a blog is published

**Trigger**: RSS feed (new blog post) or CMS webhook
**Steps**:
1. Connect Vista Social to Zapier (requires Advanced+ plan)
2. Set trigger: RSS → New Item
3. Set action: Vista Social → Schedule Post
4. Map fields: blog title → caption, blog URL → link, featured image → media

**Zapier configuration:**
```
Trigger: RSS by Zapier → New Item in Feed
  Feed URL: https://yourblog.com/feed

Action: Vista Social → Schedule Post
  Profiles: [select target profiles]
  Message: "New blog: {{title}} — {{link}}"
  Media URL: {{enclosure_url}}
  Schedule: "next_available"  # or specific time
```

**Gotchas**: Video posts may fail if the video doesn't meet platform specs. Test with images first.

### Recipe 2: Alert Slack when a post fails to publish

**Trigger**: Vista Social → Post Failed to Publish (Zapier trigger)
**Steps**:
1. Create Zapier zap with Vista Social trigger
2. Add Slack action: Send Channel Message
3. Include post details and profile name in the message

**Zapier configuration:**
```
Trigger: Vista Social → Post Failed to Publish

Action: Slack → Send Channel Message
  Channel: #social-alerts
  Message: "Failed post on {{profile_name}}: {{message}}"
```

### Recipe 3: Export daily metrics to Google Sheets

**Trigger**: Schedule (daily at 8 AM)
**Steps**:
1. Create Zapier zap with Schedule trigger
2. Add Vista Social action: Get Daily Metrics (PREMIUM)
3. Add Google Sheets action: Create Spreadsheet Row

**Zapier configuration:**
```
Trigger: Schedule by Zapier → Every Day at 8:00 AM

Action: Vista Social → Get Daily Metrics (PREMIUM)
  Profile: [select profile]
  Date Range: yesterday

Action: Google Sheets → Create Spreadsheet Row
  Spreadsheet: "Social Metrics 2026"
  Worksheet: "Daily"
  Columns: Date, Impressions, Engagements, Followers, Clicks
```

**Gotchas**: Get Daily Metrics is a premium Zapier action — it costs extra per task on Zapier's side.

## Integration patterns

### CRM sync pattern
Vista Social has no native CRM connectors. Use Zapier/Make as middleware:

1. **Lead capture from DM automations** → Vista Social DM collects lead info → Manual export or use Get Inbox (PREMIUM Zapier) → Push to HubSpot/Salesforce
2. **Social engagement → CRM activity** → "New Internal Post Comment" trigger → Create CRM activity/note
3. **Blog → Social post** → CRM workflow publishes blog → RSS/webhook → Vista Social Schedule Post

**Limitation**: No real-time webhook from Vista Social to your systems. Polling via Zapier is the primary pattern.

### Multi-client agency pattern
1. Create profile groups per client
2. Set up team members with role-based permissions per group
3. Use approval workflows (Advanced+) for client review
4. White-label reports on Scale+ for client delivery
5. Use Looker Studio connector for custom client dashboards

### Content calendar automation
1. Store content ideas in Vista Social Ideas (or external tool)
2. Batch-create posts weekly
3. Use AI Assistant for first drafts, then human review
4. Queue posts with optimal timing per network
5. Monitor via "Post Failed to Publish" Zapier trigger
