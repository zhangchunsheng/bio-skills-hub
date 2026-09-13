# BrandCrowd — Learnings

Accumulated platform knowledge. Append new findings with the date you learned them.

**2026-07-29**: Research baseline established. Key findings from the live site and its legal documents:

- **Supply model is the differentiator.** BrandCrowd is a *bought-from-designers template marketplace*
  (Incspring 2008 → Brandstack 2009 → acquired by DesignCrowd Dec 2011), not an AI generator. A logo *maker*
  editor was layered on in 2018. This is why its licence structure has no analogue in the AI logo cluster.
- **One entity, three sites, one account.** Terms of Use (last updated 11 Sep 2025) name **DesignCrowd Pty Ltd
  ACN 127 272 315**, Surry Hills NSW, and govern design.com and brandcrowd.com jointly; registering on one "may"
  auto-register you on designcrowd.com.au, design.com and brandcrowd.com. Explains "account I never created"
  reports.
- **The four-tier licence ladder (Service Terms clause 6) is the spine of the skill**: Free / Standard / Buyout /
  Exclusive, each purchasable **under a subscription** OR for a **one-time fee**. Subscription-bound Buyout and
  Exclusive last only "the duration of your Subscription"; at expiry the template returns to the library and the
  licence "will automatically change to a Standard License." Only the one-time fee grants perpetuity. This
  rented-exclusivity mechanic is the single most valuable thing in the skill and is not disclosed at checkout.
- **Exclusivity is not retroactive** — prior licensees "retain an ongoing right to license and use" their
  versions; some elements (shapes, fonts) are never removed; BrandCrowd and the original designer may keep
  displaying the template in marketing/portfolio.
- **Resale bans**: a New Work "cannot be sold more than once" and "cannot be sold on any other design platforms."
  Sublicensing IS granted under Buyout/Exclusive, so client work is fine but a resale product is not.
- **No pricing page exists** — `/pricing` and `/maker/pricing` 404, and `sitemap-main-pages-sitemap.xml` contains
  no pricing URL at all. Price appears only at checkout (`/checkout` is disallowed in robots.txt). Third-party
  quotes span ~$3–$29/mo for nominally the same ladder (Tekpon: 15/24/29; InBound Blogging: 9/14/19; aggregators:
  3/4/5 annual). Never quote a figure as fact — this is a *published-nowhere* case, not a stale-data case.
- **Refunds are technical-impediment-only**, expressly excluding "change of mind" and "design related reasons,"
  all at BrandCrowd's discretion. The Australian Consumer Law backstop is preserved in the text and is the real
  escalation lever. Liability capped at greater of $100 or fees paid.
- **AI training clause (3.4)** covers prompts, written content, **business names**, search terms, personal info,
  photos and edited designs — a concrete pre-launch confidentiality risk for an unfiled brand name.
- **Getty Images / Unsplash content is embedded in templates**, must not be used standalone, and the right to use
  it "may be revoked at any time."
- **Designer side** (`/maker/sell-logos`): BrandCrowd **buys** logos (PayPal/Payoneer), publishes **no rate
  card**, refuses wordmarks/text-only logos, reviews over "a few days to a few weeks," and bars resale elsewhere.
- **No API.** robots.txt disallows `/api/` and `/maker/api` (internal front-end AJAX; `/maker/api` returns 200
  with a zero-byte body). No webhooks, Zapier/Make, MCP, or self-serve white-label. Affiliate programme at
  `/maker/affiliate` is referral revenue only.

**Fetch notes**: the homepage fetches fine, but real page paths live under `/maker/` (`/maker/about`,
`/maker/legals/termsofuse`, `/maker/legals/servicetermsandconditions`, `/maker/sell-logos`) — `/about` and
`/pricing` 404. Legal pages are server-rendered inside a huge nav shell; strip tags and seek from the document
title rather than trusting a summarizer. Trustpilot returns 403 to WebFetch; use search snippets for complaint
signal instead (~458 Trustpilot reviews, PissedConsumer ~1.9★).
