# uBrand API Reference

<!-- Source: https://ubrand.com (probed 2026-07-29); https://www.logoai.com/logo-api (fetched 2026-07-29) -->

## Summary: uBrand has no API

**There is no uBrand API.** No REST endpoints, no webhooks, no Zapier app, no Make connector, no MCP
server, no SDK, no OpenAPI/Swagger spec, and no developer documentation of any kind. Every module in the
product is UI-only.

This file records the evidence, because **multiple third-party directories claim otherwise** and that claim
is fabricated (see "Fabricated third-party claims" below). Do not reconstruct or invent endpoints.

## Probe evidence (2026-07-29)

### DNS — every API-ish subdomain is NXDOMAIN

```
api.ubrand.com        -> NXDOMAIN
docs.ubrand.com       -> NXDOMAIN
help.ubrand.com       -> NXDOMAIN
app.ubrand.com        -> NXDOMAIN
developer.ubrand.com  -> NXDOMAIN
```

There is no host that could serve an API or its documentation.

### HTTP paths

uBrand's 404 page returns a consistent **32,456-byte** body, so a real page is identifiable by size.

```
/api          -> 200, 299,743 b   Title: "API - uBrand"  -- but renders the APP DASHBOARD SHELL
/api-docs     -> 404,  32,456 b   (404 baseline)
/docs         -> 404,  32,456 b   (404 baseline)
/developers   -> 404,  32,456 b   (404 baseline)
```

**The `/api` page is the trap.** It returns HTTP 200 and its `<title>` is literally `API - uBrand`, which
is enough to make an automated scan (or an LLM summarising search results) conclude an API exists. Its
actual rendered text is the logged-out application shell:

> API - uBrand Home DNA Assets Tools Brand Essentials Business Cards ... Open Branding Mockups ... Brand
> Studio Generate and publish your brand content in seconds ...

No authentication section, no base URL, no endpoint list, no request/response examples, no rate limits.
It is a navigation shell, not documentation.

### iPaaS

- **Zapier**: `zapier.com/apps/ubrand/integrations` returns **HTTP 404** — no uBrand Zapier app exists.
- **Make / n8n**: no connector found.
- **MCP**: no server published under uBrand or TingPing.co.

## Fabricated third-party claims — do not repeat

Several AI-generated tool directories and "knowledge base" pages assert that uBrand offers:

- "API integration"
- "automation platforms like Zapier and Make.com"
- "plugins available for Figma, Sketch, GIMP, and CLI tools requiring no coding"

**All of this is false.** A branding SaaS shipping a GIMP plugin and a CLI is an obvious tell for generated
filler copy, and every element of the claim fails the probes above. Treat aggregator "features" tables for
this platform as unreliable, and cite the DNS/HTTP evidence instead.

## The adjacent real programme: LogoAI's iframe "Logo API"

The only programmatic-sounding offering in this family belongs to the **sibling product**, LogoAI (same
operator, TingPing.co — see `platform-guide.md`). It is a **white-label reseller integration, not a
self-serve automation API**, and it **cannot drive uBrand**.

Notably, **LogoAI's Logo API page uses uBrand Logo Maker as its live demo** — which is how we know uBrand's
logo maker is that iframe.

Verbatim from `logoai.com/logo-api`:

**What it is**
- **Logo API**: "implemented using IFRAME where you can directly open our page from your website." Lets
  your users generate logos, customise designs, and access a download centre for brand assets.
- **Logo API Lite**: generates PNG logos from user inputs, without customisation.

**Access requirements**
- An existing website or app is required.
- You must first become an Affiliate/Partner.
- Gate: "Once you've reached 50 customers via your partner link, we will be more than happy to help you set
  up our logo API."
- Application submission required via their portal.

**Fees**
- Logo API: **$2,000 USD one-time setup**, plus **40% of our official price for each logo sold via your
  API** (revenue share).
- Logo API Lite: pricing not specified.

**Why it is not an automation API**

It embeds *LogoAI's own logo-making UI* into *your* site so that *your* users make logos, and it monetises
by revenue share. There are **no documented REST endpoints, no authentication scheme, no webhooks, and no
batch generation**. A solo user cannot use it to script logo output, and it has no relationship to a uBrand
subscription. See `/sales-logoai` for the full white-label reference.

## What to do instead

If the goal is **programmatic brand-asset or logo generation at volume**, use an image-generation service
with genuine published API documentation rather than either product. Within this catalogue,
`/sales-ideogram` is the logo-cluster platform that actually ships a self-serve programmatic surface
(published OpenAPI spec, API-key auth, official MCP server, signed webhooks) — note it has no SVG/vector
export, which matters for logo work.

If the goal is **managing many client brands in uBrand specifically**, there is no automation path: it is
the Agency plan's UI, at $149/month plus $10/brand/month, done by hand — and see the multi-brand pricing
contradiction in `platform-guide.md` before budgeting.
