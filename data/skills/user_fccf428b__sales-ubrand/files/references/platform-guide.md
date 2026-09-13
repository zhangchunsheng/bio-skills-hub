# uBrand Platform Guide

<!-- Source: https://ubrand.com, https://ubrand.com/pricing, https://ubrand.com/term (fetched 2026-07-29) -->

Best-effort reference from research on **2026-07-29**. Pricing, tiers, and terms move — verify on-site.

## What uBrand is

uBrand (ubrand.com) is a **subscription AI brand-identity platform** aimed at entrepreneurs, solopreneurs,
and small teams. Its pitch is the full brand system rather than a single logo file: you start from a name,
generate a logo, and the platform builds out the surrounding identity (colours, type, guidelines, mockups)
plus ongoing content creation and social publishing.

Positioning from its own pricing page comparison table:

| | Freelance designer | Agency | uBrand |
|---|---|---|---|
| Price | $200 ~ $2,000 USD | $2,000 ~ $10,000 USD | $29 USD/month |
| Time | 1 ~ 2 weeks | 1 ~ 2 months | 30 minutes |
| Good | Flexible | Professional | Easy to use |
| Bad | Unpredictable | Expensive | DIY required |

## Operator and the LogoAI relationship

**uBrand and LogoAI (`/sales-logoai`) are operated by the same company.** Both sites' Terms of Use open
with the identical sentence: *"This website is operated by TingPing.co."*

**uBrand's logo maker is LogoAI's iframe "Logo API".** LogoAI's own Logo API page presents **uBrand Logo
Maker as the live demonstration** of that iframe integration. Practical consequences:

- The **logo generation engine is the same** in both products. Choosing between them is a choice of
  **wrapper and billing model**, not of logo quality.
- **LogoAI sells the logo one-time** (pay-to-download packages). **uBrand rents the whole brand system
  monthly.** If a user only needs a logo file, LogoAI is the cheaper path — see `/sales-logoai`.
- uBrand's extra value over LogoAI is everything *around* the logo: Brand DNA, guidelines, asset
  management, AI image/video generation, social publishing, team/agency multi-brand management.

## Modules and automation surface

Every module is **UI-only**. There is no API, webhook, iPaaS connector, or MCP server (see
`ubrand-api-reference.md` for the probe evidence).

| Module | What it does | Automation |
|---|---|---|
| AI Logo Maker | Name/industry → AI logo concepts (LogoAI iframe engine) | UI-only |
| Brand DNA | Brand strategy/positioning attributes that seed the visual identity | UI-only |
| Brand Logo Kit | Logo variants and file formats packaged together | UI-only |
| Brand Guideline | Generated brand guidelines document (colour, type, usage) | UI-only |
| Brand Mockups | Logo/brand applied to product and environment mockups | UI-only |
| Brand Inspiration | Reference/ideation gallery | UI-only |
| Image Generator | AI brand image generation (consumes AI credits) | UI-only |
| Video Generator | AI brand video generation (consumes AI credits) | UI-only |
| Brand Tools | Business cards, email signatures, themes, PPTs | UI-only |
| Brand Social | AI-powered social media design **and publishing** | UI-only |
| Brand Asset Management | Store/share brand assets in "Brand Space" | UI-only |

Brand Social advertises publishing to Facebook, Instagram, LinkedIn, X, YouTube, and TikTok. That is
uBrand posting *on your behalf from its own UI* — it is not an integration you can drive programmatically.

## Pricing

Verbatim from ubrand.com/pricing (2026-07-29). A **Monthly / Yearly** toggle exists, but annual figures
render dynamically (the markup carries an unfilled `"yearly":"$<num>{{price` placeholder) and could **not
be verified** — confirm annual rates at checkout.

| Plan | Price | Brands | Credits | Brand Space | Adds |
|---|---|---|---|---|---|
| **Solo** | US $29/month | "For solopreneurs building 1 brand" | 500 AI Credits | 1GB | Brand Tools (business cards, signatures, themes, PPTs), Brand Social, Brand Asset Management |
| **Pro** | US $49/month | "For managing up to 5 brands" | 1000 AI Credits | 5GB | Everything in Solo + Team collaboration (invite team members) |
| **Agency** | US $149/month | "For managing multiple brands" | — | — | Everything in Pro + additional brands at **$10/each/month**, one dashboard for multiple brands, per-brand account access control |

### The multi-brand contradiction

The pricing page **contradicts itself** on the same screen. The Pro tier is sold as *"For managing up to 5
brands"*, but the FAQ directly below states:

> **Is the PRO subscription associated with brands or users?**
> The PRO subscription is applied to individual brands. If you manage multiple brands that require a PRO
> subscription, you must separately purchase a subscription for each brand.

And the Agency tier separately charges *"$10/each/month"* for additional brands. These three statements
cannot all be true. **Anyone budgeting for more than one brand must get written confirmation of what $49
covers before paying** — the difference between "5 brands for $49" and "$49 per brand" is 5×.

### The free tier is undefined

The pricing page headline says *"It's 100% free to get started."* But there is **no free column in the tier
table, no stated credit allowance, no feature list, and no published limit** anywhere on the site. Combined
with the Terms (below), which bar use of any generated logo "until payment has been made", treat free as
**preview-only**: you can look, you cannot legitimately use the output.

### What a lapsed subscription does (from uBrand's own FAQ)

> **What if my brand library is more than 1GB when my PRO membership expires?**
> Don't worry, your files will still be saved in your brand library, you just won't be able to add new
> files. You can either renew your PRO membership or delete some files to free up more space.

> **Can I still use design templates saved after my PRO membership expires?**
> If your PRO membership has expired, you will still be able to download your saved design files, but you
> won't be able to open them for further editing.

So on lapse: **downloads yes, editing no, new files no.** uBrand is rent, not purchase. The operational
advice is to **export every asset you might ever need to edit before cancelling** — logo files, guidelines,
templates, source assets — because no clause entitles you to re-open the workspace later.

Note the FAQ still says "PRO membership" throughout even though the tiers are Solo/Pro/Agency; the
behaviour is described as applying to the paid product generally.

## Terms of Use — the borrowed contract

**uBrand's Terms of Use at `ubrand.com/term` are LogoAI's Terms of Use with the product name swapped.**
Verified 2026-07-29 by fetching both and comparing: distinctive clauses appear word-for-word in both.

That matters because LogoAI's Terms were written for a **one-time logo purchase** business, and uBrand
sells a **monthly subscription**. The result is a contract that never addresses the product it governs.

### What the Terms actually say (verbatim extracts)

**Operator:**
> This website is operated by TingPing.co. Throughout the site, the terms "we", "us" and "our" refer to
> uBrand and TingPing.co.

**Copyright and Intellectual Property:**
> All generated logos are protected by copyright laws. You may not use any of the logos without obtaining a
> licence from us. A license can be obtained by purchasing the logo. We make backups of all generated logos
> and regularly check whether they appear anywhere on the internet. The user acknowledges that no
> trademark, copyright or service marks are being conveyed under this license agreement. Furthermore the
> user acknowledges that we have no obligation or duty to perform trademark, copyright or service marks
> searches to validate that the logo is not infringing... We encourage the user to perform their own
> independent searches.

**Satisfaction Guarantee:**
> If you have purchased a logo from us and created another logo on our website afterwards which you like
> better, you can ask for replacement within 30 days of purchase. You can take advantage of this
> replacement only once (per purchase). The acquired license is automatically transferred to the second
> logo. You are not allowed to use the first logo after it has been replaced.

**Refund:**
> After the logo has been purchased and the user has access to the files, they are not eligible for a
> refund. In order to treat everyone equally, no exceptions will be made.

**Violation:**
> You may not use any of the generated logos for any purpose until payment has been made.

**Prices:**
> Prices for our products are subject to change without notice. Prices include VAT. We reserve the right at
> any time to modify or discontinue the Service (or any part or content thereof) without notice.

### The gaps this creates

1. **The subscription-to-licence mapping is absent.** Rights attach to "purchasing the logo" — a
   transaction uBrand does not offer. Nothing states that a Solo/Pro/Agency plan conveys the logo licence,
   or whether that licence survives cancellation. A user relying on a uBrand logo commercially should get
   **written confirmation from support** and keep it with the receipt.
2. **No subscription terms at all.** No cancellation clause, no auto-renewal disclosure, no pro-rata rule,
   no notice period.
3. **No credit rules.** AI Credits are sold on every tier, but the Terms never define expiry, rollover,
   refundability, or what happens to unspent credits at cancellation.
4. **The refund clause can't apply as written.** It contemplates one-time file purchases and says "no
   exceptions" — it does not address monthly billing.
5. **The "Satisfaction Guarantee" has no subscription analogue.** One logo replacement per purchase, within
   30 days of purchase — undefined when there is no purchase, only a plan.
6. **Rights are actively policed.** "We make backups of all generated logos and regularly check whether
   they appear anywhere on the internet" means unpaid use carries real enforcement risk.
7. **No trademark clearance duty.** Explicitly disclaimed — run your own USPTO/EUIPO search. An
   AI-generated mark can also be hard to register, and the shared LogoAI engine means visually similar
   marks may exist from either product's user base.

### Practical billing advice

Prefer **monthly over annual** billing. Because the published policy doesn't address subscriptions, the
realistic remedies for a disputed charge are a **card-issuer chargeback** or **statutory distance-selling
rights** (14 days in the EU/UK) — not the site's own policy. Screenshot the checkout screen and the plan
description at purchase; the Terms reserve the right to change prices and discontinue the service without
notice, and the pricing page is the only place the tier contents are stated.

## Dead links and site gaps (verified 2026-07-29)

The 404 page returns a consistent 32,456-byte body, which makes real pages easy to distinguish.

| Path | Status | Note |
|---|---|---|
| `/term` | 200 | The real (borrowed) Terms of Use |
| `/privacy` | 200 | Privacy policy |
| `/refund` | **404** | **Linked from the site footer as "Refund Policy" — the target does not exist** |
| `/help` | **404** | No help centre at the obvious path |
| `/about`, `/contact` | 404 | No about or contact page |
| `/api`, `/api-docs`, `/developers` | 404 / app shell | See `ubrand-api-reference.md` |

The footer advertising a **Refund Policy that 404s** is worth surfacing to any user weighing a purchase:
the only refund language that exists anywhere is the inherited logo-purchase clause inside `/term`.

## Known user complaints

From third-party review aggregation (Trustpilot/SourceForge/Slashdot listings, 2026-07):

- **Support unresponsiveness** — repeated reports of support requests going unanswered after signup.
- **Editing lockout after expiry** — matches uBrand's own documented FAQ behaviour above.
- **Logos not editable after creation** in some flows.
- **Storage ceilings** — 1GB (Solo) / 5GB (Pro) Brand Space fills up; on expiry the library freezes.

Because support responsiveness is a recurring complaint, advise users to resolve licence and multi-brand
billing questions **before** paying, not after.

## Where uBrand fits

A logo is downstream of a locked name, which is downstream of a validated idea. Route accordingly:

- Validate the idea first — `/sales-idea-validation`
- Generate the name — `/sales-namelix`
- Just need the logo file, one-time — `/sales-logoai` (same engine, one-time pricing) or `/sales-brandmark`
- Subscription brand-kit alternative — `/sales-looka`
- Wider marketing creative after the brand exists — `/sales-canva`
- Landing page / smoke test under the new brand — `/sales-funnel`
