# uBrand — Accumulated Learnings

Append new findings with today's date. Newest entries at the bottom of each section.

## Research baseline

**2026-07-29**: Research baseline established for uBrand (ubrand.com). Live site, actively maintained
(2026 copyright, recent blog posts on GPT-image-2 branding and social content calendars). Subscription AI
brand-identity platform: Solo $29/mo, Pro $49/mo, Agency $149/mo (+$10/brand/month). Modules: AI Logo
Maker, Brand DNA, Brand Logo Kit, Brand Guideline, Brand Mockups, Brand Inspiration, Image Generator, Video
Generator, Brand Tools, Brand Social (design + publishing), Brand Asset Management. Claims "2,000+ Brands".
All research from live-site fetches plus third-party review aggregation.

## Verified facts

**2026-07-29 — Same operator as LogoAI.** Both `ubrand.com/term` and `logoai.com/term` open with the
identical sentence "This website is operated by TingPing.co." Confirmed by fetching both and diffing.

**2026-07-29 — uBrand's logo maker is LogoAI's iframe.** `logoai.com/logo-api` presents **uBrand Logo Maker
as the live demo** of its iframe Logo API integration. Same logo engine in both products; the difference is
the wrapper and the billing model (LogoAI = one-time pay-to-download; uBrand = monthly subscription).

**2026-07-29 — The Terms are LogoAI's Terms, name-swapped.** Distinctive clauses appear word-for-word in
both documents, including "We make backups of all generated logos and regularly check whether they appear
anywhere on the internet", the "Satisfaction Guarantee" one-time-replacement clause, and "After the logo has
been purchased and the user has access to the files, they are not eligible for a refund... no exceptions
will be made." Consequence: a **one-time-logo-purchase contract governs a monthly subscription** — the
licence trigger is "purchasing the logo" (which uBrand never sells), and there is **no subscription,
cancellation, pro-rata, auto-renewal, or credit-expiry clause anywhere**.

**2026-07-29 — Pricing page contradicts itself on multi-brand billing.** Pro is sold "For managing up to 5
brands" while the FAQ on the same page says "The PRO subscription is applied to individual brands. If you
manage multiple brands that require a PRO subscription, you must separately purchase a subscription for
each brand." Agency separately charges $10/brand/month. The three statements are mutually inconsistent —
a 5× budget difference for anyone branding more than one thing.

**2026-07-29 — Lapse behaviour is documented by uBrand itself.** FAQ: expired membership → saved design
files "will still be able to download... but you won't be able to open them for further editing"; brand
library keeps existing files but "you won't be able to add new files." uBrand is rent, not purchase —
export everything editable before cancelling.

**2026-07-29 — No free tier is defined.** The pricing page says "It's 100% free to get started" but
publishes no free column, credit allowance, feature list, or limit. Combined with the Terms' bar on using
any logo "until payment has been made", free is preview-only.

**2026-07-29 — Footer links a Refund Policy that 404s.** `ubrand.com/refund` is linked from the site footer
(`href="/refund"` present in the homepage HTML) and returns the 404 baseline body. `/help` also 404s. The
only refund language anywhere is the inherited logo-purchase clause inside `/term`.

**2026-07-29 — No API, and third-party claims of one are fabricated.** `api./docs./developer./app.`
ubrand.com are all NXDOMAIN; `zapier.com/apps/ubrand/integrations` returns 404; no Make connector, no
webhooks, no MCP. Aggregator pages claiming "API integration", "Zapier and Make.com", and "plugins for
Figma, Sketch, GIMP, and CLI tools" are AI-generated filler — every element fails the probes.

## Gotchas discovered

**2026-07-29 — `/api` is a 200-response trap.** `ubrand.com/api` returns HTTP 200 (299,743 b) with
`<title>API - uBrand</title>`, but renders the app dashboard shell, not documentation. Title-only or
status-code-only checks will wrongly conclude an API exists. The 404 baseline body is a consistent
**32,456 bytes**, which makes real pages easy to separate from misses.

**2026-07-29 — Annual pricing is unverifiable from markup.** A Monthly/Yearly toggle exists but the page
ships an unfilled placeholder (`"yearly":"$<num>{{price`); annual rates render dynamically.
Quote monthly prices only and tell users to confirm annual at checkout.

**2026-07-29 — Support unresponsiveness is the top third-party complaint.** Repeated reports of support
requests going unanswered after signup, alongside the editing lockout and storage-ceiling complaints.
Because support is unreliable, licence and multi-brand billing questions should be settled **before**
payment, not after.

## Open questions

- What exactly the free tier includes (nothing published; would need an account to determine).
- Annual pricing for each tier.
- Whether a Solo/Pro/Agency subscription is treated by support as conveying the logo licence, and whether
  that licence survives cancellation — the Terms are silent and this is the single most important gap.
- What happens to unspent AI Credits at renewal or cancellation (no rollover/expiry rule published).
- Whether the Agency plan's per-brand $10/month is additive to, or replaces, the FAQ's per-brand
  subscription rule.
