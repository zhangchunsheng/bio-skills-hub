# Trigify Platform Reference

## Overview

Trigify.io is an AI agent-powered signal intelligence platform for B2B GTM teams. It monitors social engagement across LinkedIn, X/Twitter, Reddit, YouTube, Podcasts, and Substack, then routes signals through custom AI workflows to CRM, outreach, and productivity tools. Primary differentiator: LinkedIn-first signal detection with a visual workflow builder and AI agents, not just raw alerts.

## Capabilities & automation surface

### Social Listening & Monitoring (API-accessible via GET leads endpoint; UI for search management)

- **Keyword Listening**: Boolean queries across platforms — supports AND, OR, NOT operators
- **Profile Monitoring**: Track engagement on specific LinkedIn profiles or company pages
- **Podcast Monitoring**: Track mentions in podcast transcripts
- **YouTube Monitoring**: Track mentions in video transcripts and comments
- **Supported platforms**: LinkedIn (primary), X/Twitter, Reddit, YouTube, Podcasts, Substack

### Workflows & Automation (UI + webhook-accessible)

**Triggers:**
- New Post Trigger — fires when a matching post is detected
- Multi Post Trigger — batches multiple posts before firing
- Scheduled Trigger — fires on a time schedule
- Signal Created Trigger — fires when a signal is configured
- Webhook Trigger — fires on incoming webhook

**AI Agents:**
- Sentiment Agent — classifies sentiment of signals
- CopyWriter Agent — generates outreach copy from signal context
- General Agent — custom AI processing with user-defined prompts

**Enrichment nodes:**
- Person Enrichment — enrich contact data from LinkedIn profile
- Company Enrichment — enrich company data
- Prospeo Email Enrichment — find verified email addresses

**Business Network Engagement (Max+ plan):**
- Get Post Likes — retrieve who liked a post
- Get Post Comments — retrieve who commented on a post

**Utilities:**
- HTTP Request — call any external API from workflows
- If Condition — conditional branching
- Loop — iterate over lists
- Delay — wait between steps
- Save to Agent Memory — persist data across workflow runs
- Get Podcast Transcript — fetch full transcript

**Orchestration:**
- Configure Signal — define output signal shape
- Fetch Search Results — pull in listening data
- Create Social Listening Search / Create Profile Monitoring Search — programmatically create searches from workflows
- Exit Node — terminate workflow

### Jarvis AI (UI-only)
Natural language workflow builder. Describe what you want in plain English and Jarvis generates a workflow. Best for quick prototyping — review and customize before production use.

### Social Actions (Max+ plan, UI + workflow-accessible)
- X/Twitter post engagement from workflows (like, reply, repost)

## Pricing, limits & plan gates

| Feature | Starter ($40/mo) | Max ($199/mo) | Enterprise (custom) |
|---|---|---|---|
| Listening Searches | 25 | Unlimited | Unlimited |
| Workflows | Unlimited | Unlimited | Unlimited |
| Credits | 4,000 ($0.012/overage) | 40,000 ($0.012/overage) | Unlimited |
| Search History | 7 days | 12 months | All-time |
| Workspaces | 1 | 3 | Unlimited + RBAC |
| Tables (data storage) | 30 days | 90 days | Custom |
| Social Engagement | No | Yes | Yes |
| Social Actions | No | Yes | Yes |
| BYOK | No | No | Yes |
| SSO/SAML | No | No | Yes |
| Support | Standard | Priority + Slack | Dedicated CSM + SLA |
| API Access | Yes | Yes | Yes |
| Reporting | Yes | Yes | Yes |

**Credit consumption**: Every workflow step consumes credits. Enrichment nodes (Person, Company, Prospeo) cost more than routing nodes. Monitor in Account Settings → Credit Usage.

**Overage**: $0.012 per credit beyond plan limit. No hard cutoff — workflows keep running but you'll be billed.

## Integrations

### CRM (bidirectional — reads contacts, writes leads/signals)
- **HubSpot** — native connector, push contacts/deals, pull pipeline data
- **Attio** — native connector, push enriched leads
- **Apollo** — native connector, push contacts

### Outreach & Sequencing (write — push leads into sequences)
- **Instantly** — add to cold email sequences
- **HeyReach** — add to LinkedIn outreach sequences
- **La Growth Machine** — add to multi-channel sequences
- **Smartlead** — add to email sequences

### Productivity & Notifications (write — push data/alerts)
- **Slack** — send alerts and signal summaries to channels
- **Notion** — create database entries from workflow outputs
- **Linear** — create issues from signals
- **Airtable** — write to bases
- **Google Sheets** — append rows
- **Gmail** — send emails from workflows

### Data & Enrichment (read — pull data into workflows)
- **Surfe** — enrich LinkedIn contacts
- **Clay** — via HTTP Request node
- **Prospeo** — email enrichment (native node)

### Custom (bidirectional via HTTP Request node)
- Any REST API via the HTTP Request workflow node

## Data model

### Listening Search
```json
{
  "id": "search_abc123",
  "name": "AI SaaS competitor tracking",
  "keywords": "\"AI sales\" OR \"sales intelligence\" NOT hiring",
  "platforms": ["linkedin", "twitter", "reddit"],
  "frequency": "hourly",
  "status": "active",
  "created_at": "2026-05-01T10:00:00Z"
}
```
<!-- Constructed from docs — verify against live API -->

### Lead (from GET /api/sdr/{sdrCode}/leads)
```json
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
  "enrichment": {
    "company_size": "51-200",
    "industry": "SaaS",
    "location": "San Francisco, CA"
  },
  "created_at": "2026-05-07T14:30:00Z"
}
```
<!-- Constructed from docs — verify against live API -->

### Workflow
```json
{
  "id": "wf_def456",
  "name": "Competitor engagement → HubSpot",
  "trigger": "new_post",
  "nodes": [
    {"type": "sentiment_agent", "config": {"threshold": "positive"}},
    {"type": "person_enrichment"},
    {"type": "if_condition", "config": {"field": "title", "contains": "VP|Director|Head"}},
    {"type": "hubspot_push", "config": {"pipeline": "Sales", "stage": "Lead"}}
  ],
  "status": "active",
  "credits_used_30d": 1250
}
```
<!-- Constructed from docs — verify against live API -->

## Quick-start recipes

### Recipe 1: Track competitor LinkedIn engagement and push to CRM

**Use case**: Identify people engaging with a competitor's LinkedIn content and add them to your CRM as warm leads.

**Steps**:
1. Create a Profile Monitoring search on the competitor's LinkedIn page
2. Build a workflow: New Post Trigger → Get Post Likes → Person Enrichment → If Condition (title match) → HubSpot push

**cURL — fetch leads from SDR endpoint**:
```bash
curl -X GET "https://app.trigify.io/api/sdr/YOUR_SDR_CODE/leads" \
  -H "x-api-key: YOUR_API_KEY"
```

**Python — fetch and filter leads**:
```python
import requests

url = "https://app.trigify.io/api/sdr/YOUR_SDR_CODE/leads"
headers = {"x-api-key": "YOUR_API_KEY"}
response = requests.get(url, headers=headers)
leads = response.json()

# Filter for VP+ titles
vp_leads = [
    lead for lead in leads
    if any(t in lead.get("title", "").lower() for t in ["vp", "director", "head of", "chief"])
]
for lead in vp_leads:
    print(f"{lead['first_name']} {lead['last_name']} — {lead['title']} at {lead['company']}")
```

**Gotcha**: Get Post Likes and Get Post Comments require Max plan ($199/mo). On Starter, you can only detect the post — not who engaged.

### Recipe 2: Signal-to-outreach automation (keyword → enrich → Instantly)

**Use case**: Auto-enroll people posting about your problem space into a cold email sequence.

**Steps**:
1. Create a keyword listening search: `"looking for" AND ("sales tool" OR "CRM" OR "outbound")`
2. Build a workflow: New Post Trigger → Sentiment Agent (positive/neutral only) → Person Enrichment → Prospeo Email Enrichment → Instantly (add to campaign)

**Gotcha**: Prospeo enrichment consumes credits per lookup. Use the Sentiment Agent and If Condition nodes *before* enrichment to avoid wasting credits on irrelevant signals.

### Recipe 3: Inbound webhook → custom processing

**Use case**: Receive data from an external tool and process it through Trigify's AI agents.

**Workflow**: Webhook Trigger → General Agent (custom prompt) → Slack notification

**HTTP Request node example — push to external API**:
```bash
# Inside a Trigify workflow HTTP Request node:
Method: POST
URL: https://your-app.com/api/leads
Headers:
  Authorization header uses an OAuth access token from the approved secret store
  Content-Type: application/json
Body:
{
  "name": "{{firstName}} {{lastName}}",
  "email": "{{email}}",
  "signal": "{{signalType}}",
  "source": "trigify"
}
```

**Gotcha**: Never hardcode API keys in HTTP Request nodes. If sharing workflows with team members, keys will be exposed.

## Integration patterns

### CRM sync architecture
- **Direction**: Trigify → CRM (one-way push). Trigify does not pull CRM data back.
- **Field mapping**: Done in the CRM integration node within workflows. Map Trigify lead fields to CRM contact/deal properties.
- **Conflict resolution**: Trigify creates new records by default. Dedup logic must be configured in the CRM integration settings or handled by CRM-side automation.
- **Sync frequency**: Real-time per workflow execution. No batch sync option.

### Webhook patterns
- **Inbound**: Webhook Trigger node accepts POST requests to a Trigify-generated URL. Use for external tools pushing data into Trigify workflows.
- **Outbound**: HTTP Request node sends data to any external endpoint. Configure method, headers, body with Trigify variables.
- **Retry behavior**: Not documented. Implement idempotency on your receiving endpoint.
- **Payload schema**: Not publicly documented. Use the workflow Output node to inspect payload shapes during testing.

### Rate limits and error handling
- API rate limits not documented. The single GET endpoint appears to have no published rate cap.
- Workflow execution is credit-gated, not rate-gated. If you have credits, workflows run.
- For HTTP Request nodes calling external APIs, handle rate limits in the external API's terms. Trigify does not auto-retry failed HTTP requests — use a Delay + Loop pattern for manual retry logic.
