# BrandCrowd Platform Guide

Full reference for BrandCrowd (`brandcrowd.com`). Read the section you need — don't dump the whole file.

Research date: **2026-07-29**. Pricing, plan names and template counts move; the licence clauses below are quoted
from the live legal documents on that date. Treat commercial figures as best-effort and confirm on the site.

---

## 1. What BrandCrowd actually is (and the family map)

BrandCrowd is a **designer-supplied logo template marketplace with a customization editor on top** — not an
AI-first generator. Real designers submit finished logo designs; BrandCrowd curates and buys them; you browse
the resulting library, customize a template, and license the result.

**Lineage.** Founded as **Incspring** (2008, San Antonio), renamed **Brandstack** (2009), **acquired by
DesignCrowd in December 2011** and relaunched as BrandCrowd. A logo *maker* (editor) was added in 2018 on top
of the marketplace. Headquartered in Sydney, Australia.

**The three-site family — one legal entity, one account.** The Terms of Use name
**DesignCrowd Pty Ltd ACN 127 272 315**, Level 2/44A Foveaux Street, Surry Hills NSW 2010, Australia, and
govern `design.com` and `brandcrowd.com` together. Critically:

> "By registering Your Account on this website, you may be automatically registered on our affiliated websites
> located at: https://www.designcrowd.com.au/ and https://www.design.com/ or https://www.brandcrowd.com/."

<!-- Source: https://www.brandcrowd.com/maker/legals/termsofuse (Last Updated: 11 September 2025) -->

| Site | Model | Skill |
|---|---|---|
| **brandcrowd.com** | Designer-made **template marketplace** + editor, four-tier licence ladder | this skill |
| **design.com** | **AI-first** generation + brand kit, subscription | `/sales-design-com` |
| **designcrowd.com** | **Human contest** marketplace, brief → 25–100+ designers → full copyright | `/sales-designcrowd` |

So "same company, three supply models": bought-from-designers templates, AI generation, and live human contests.
A user who says "the DesignCrowd template site" means BrandCrowd; "the DesignCrowd AI tool" means Design.com.

---

## 2. Modules and automation surface

Every module below is **UI-only**. There is **no public API, no webhooks, no Zapier/Make listing, no MCP server**.
`robots.txt` disallows `/api/` and `/maker/api` — those are internal AJAX endpoints for the site's own front end,
not a documented developer surface, and they are not authenticated developer APIs.

| Module | What it does | Automation |
|---|---|---|
| Logo Maker / Logo Templates | Browse + customize 100K+ designer templates (site claims 380K+ logos in places) | UI-only |
| AI Logo Generator | Prompt-based generation layered onto the marketplace | UI-only |
| Business Name Generator | Name ideas | UI-only |
| Business Cards | Templates + print fulfillment | UI-only |
| Social Media | Posts, stories, covers, banners, profile pics for FB/IG/LI/X/TikTok/YouTube/Twitch/Pinterest/Snapchat/Tumblr/SoundCloud | UI-only |
| Print | Flyers, posters, letterheads, menus, invoices, postcards, invitations, gift certificates, t-shirts | UI-only |
| Video / Animation | Animated logos, TikTok videos, Reels, Shorts | UI-only |
| Website Builder | Hosted site | UI-only |
| Link in Bio / Digital Business Card | Micro-sites | UI-only |
| Domain Names | Register/manage via **GoDaddy + ICANN** as third-party providers | UI-only |
| QR Code Generator, Background Remover, Email Signatures | Utilities | UI-only |
| Sell Logos | Designer supply side (see §6) | UI-only |
| Affiliate program | `/maker/affiliate` — referral revenue, **not** an automation or reseller API | UI-only |

**File formats** (best-effort, per third-party reviews): PNG, JPG, SVG, PDF, EPS, plus GIF/MP4 for animated
designs. Free downloads are **low-resolution and/or watermarked**; high-resolution and vector require a paid plan.

**Embedded third-party assets.** Templates may include **Getty Images** and **Unsplash** content. The Service
Terms require compliance with those vendors' own licences, forbid using such assets standalone, and warn:

> "you acknowledge that your right to use any third party image, video or other content is subject to the
> discretion of the relevant third parties and may be revoked at any time and the relevant content removed
> from your New Work(s)."

<!-- Source: https://www.brandcrowd.com/maker/legals/servicetermsandconditions -->

That means a component of a purchased logo can be pulled later. Prefer marks whose distinctive elements are
native template artwork rather than embedded stock photography.

---

## 3. The licence ladder — the single most important section

Clause 6 of the Service Terms defines **four** licence types. Each can be bought **under a Subscription** or as a
**one-time licence Fee**, and that choice changes how long the rights last.

| Licence | Exclusive? | Template removed from library? | Duration |
|---|---|---|---|
| **Free** | No | No | "the term specified in the license" |
| **Standard** | No | **No — stays on sale to everyone, during your term and beyond** | Subscription duration, **or** perpetuity if one-time fee |
| **Buyout** | Non-exclusive, but **sublicensable** | Yes, for the licence duration | Subscription duration, **or** perpetuity if one-time fee |
| **Exclusive** | **Yes**, sublicensable | Yes, for the licence duration | Subscription duration, **or** perpetuity if one-time fee |

### 3a. Rented exclusivity — the trap

For both Buyout and Exclusive, the term is:

> "(when purchased under a Buyout License Subscription) the duration of your Subscription; or (when purchased
> under a one-time license Fee) perpetuity."

and at expiry:

> "At the expiry of the Buyout License, the Logo Template will again become available for customisation and
> license (as a New Work) to other users of The Sites. **Your license will automatically change to a Standard
> License**, so that you can continue to use the New Work(s) that you created from that Logo Template."

The Exclusive Licence carries the identical downgrade clause. So **if exclusivity was bought on a subscription
and the subscription lapses, the mark goes back on sale and the buyer silently drops to a non-exclusive Standard
licence.** Only the **one-time licence fee** buys perpetual exclusivity. This is the difference between owning
and renting a brand, and nothing in the checkout flow says it out loud.

### 3b. Exclusivity is not retroactive

> "You acknowledge that the underlying Logo Template may have been previously licensed to other persons as a New
> Work(s) prior to your purchase of the Buyout License. Such third-party licensees will retain an ongoing right
> to license and use the New Work(s) they previously created using the underlying Logo Template."

Buying Exclusive stops **future** licences. Everyone who already licensed that template keeps using it forever.
Before paying for exclusivity, reverse-image-search the template — if it is already in market, exclusivity buys
much less than it appears to.

### 3c. Elements are never exclusive, and the template keeps being shown

> "Some elements within the Logo Template may not be removed from The Sites for any period of time, such as
> certain shapes or fonts used in the Logo Template."

And under every licence tier, the template may still be displayed for promotion by **BrandCrowd** (marketing,
press, its other sites) and by **the original designer** as portfolio work, on or off the platform.

### 3d. Resale restrictions kill the agency/reseller model

> "New Work(s) created under any license in this clause 6 cannot be sold more than once."
> "New Work(s) created under any license in this clause 6 cannot be sold on any other design platforms other
> than those offered by The Sites or The Sites Services."

A design agency cannot build a logo-resale product on BrandCrowd output, and cannot list the results on Fiverr,
Etsy, Creative Market or a rival marketplace. Buyout/Exclusive do grant a **right to sublicense**, which is what
lets you hand the mark to a client — but the "sold more than once" cap still applies per New Work.

### 3e. Licence ≠ trademark

None of the four licences is a trademark. A Standard-licensed mark is by construction **non-distinctive** —
the same template is on sale to the whole market — which is exactly the weakness that sinks a trademark
application. The clearance sequence before committing: reverse-image search the template → USPTO/EUIPO (or local
registry) search → only then decide between a one-time Exclusive licence and commissioning original work.

---

## 4. Pricing — and why no figure here is authoritative

**BrandCrowd publishes no pricing page.** `/pricing` and `/maker/pricing` both 404, and the sitemap index
(`sitemap-index.xml` → `sitemap-main-pages-sitemap.xml`) contains **no pricing URL at all** among its main pages.
Price is disclosed inside the checkout flow, after design work is done — and `robots.txt` disallows `/checkout`.

Consequently third-party figures disagree badly (all monthly, as of mid-2026):

| Source | Tiers quoted |
|---|---|
| Tekpon | Starter $15, Value $24, Premium $29; separate business-card plans at $9 and $14 |
| InBound Blogging | Saver $9, Value $14, Premium $19 |
| Aggregator listings | "from $3/mo billed annually", Value $4, Premium $5 |

The spread ($3 → $29 for nominally the same ladder) reflects annual-vs-monthly framing, geo/currency, and
promotional A/B variants. **Quote a range, name tiers by what they unlock, and send the user to the live
checkout to see their actual price.** Never state a BrandCrowd price as fact.

Shape of the ladder, which is stable across sources: entry tier = high-resolution + vector logo files, unlimited
edits, business cards, social templates, design tools; mid tier adds the **website builder**; top tier adds
**link-in-bio + digital business card**. Annual billing is a **year committed upfront** at a much lower effective
monthly rate. A free tier exists and downloads **low-resolution / watermarked** files.

---

## 5. Refunds, renewals and cancellation

The Service Terms are unusually narrow. Refunds are available:

> "if there is a technical impediment with such New Work or The Site Service that renders you unable to utilise
> the New Work or The Site Service in accordance with the relevant license or service description."

and expressly **not**:

> "for a 'change of mind'; for design related reasons; or where there is no technical impediment to use of that
> particular Template or New Work."
> "All refunds are at Our discretion…"

**"I don't like how it looks" and "I didn't mean to subscribe" are both outside the written policy.** The one
real backstop is statutory: the terms repeatedly preserve the **Australian Consumer Law** guarantees
("Nothing in this clause 4 shall operate to exclude or restrict any guarantee in the Australian Consumer Law"),
and liability is otherwise capped at "the greater of $100 or the amount of fees paid by you."

**Subscription reality.** Subscription periods may be "monthly, annual, two-year or three-year," and:

> "you will not be guaranteed access to the New Work(s) or any Subscription Services beyond the expiration of
> the Subscription"

Reported user experience (Trustpilot ~458 reviews; PissedConsumer ~1.9★) clusters on: a purchase that read as
one-time turning out to be an annual subscription in fine print; **no advance renewal notice and no receipt
email**, so the charge is discovered on a card statement after the refund window closed; and repeat billing
after an attempted cancellation. Cancellation is self-serve from the account dashboard.

**Practical sequence:** cancel from the dashboard immediately → screenshot the plan/renewal screen and keep every
receipt → contact `brandcrowd.com/maker/contact` inside the window citing the specific clause → if unresolved,
invoke Australian Consumer Law guarantees explicitly → then dispute with the card issuer.

---

## 6. Your content trains their AI

Clause 3.4 grants a broad training right over user input:

> "We may use aspects of Your Content to train our AI Processes (including those developed with third party
> providers). Such aspects of Your Content may include (without limitation) any: prompts; written content
> (including website copy); business names; search terms; personal information provided in conjunction with The
> Sites Services; photos; and edited designs."

For a pre-launch founder this matters concretely: **an unannounced product name or positioning typed into the
name generator or search box is training data.** If the name is confidential until launch, don't type it in
before filing the trademark application.

They also reserve the right to "continue to expand and change the use of AI Processes… without notice to you."

---

## 7. Selling logos as a designer

`brandcrowd.com/maker/sell-logos` — the supply side. Three steps: apply to join → submit logos for review →
get paid via **PayPal or Payoneer**.

- BrandCrowd **buys** logos rather than paying an ongoing royalty; the page publishes **no rate card**, so
  compensation is only visible after applying.
- **Exclusivity runs the other way too**: "Any logos we buy from you must not be sold in any third parties or
  platforms."
- **Wordmarks and text-only logos are not bought** — icon/symbol marks only.
- Curation is selective ("We don't pay for any logos that fail to meet our quality standards") and review takes
  "a few days to a few weeks."
- The designer retains the right to show the design in their portfolio (mirrored in the buyer-side clauses).

Advise designers to get the per-logo figure in writing before submitting a batch, since the sale is exclusive
and irreversible for that artwork.

---

## 8. No API — what to do instead

There is no documented REST API, no webhook system, no Zapier/Make connectors, and no MCP server. The affiliate
programme is referral revenue, not automation, and there is no self-serve white-label/reseller tier. Logo
generation on BrandCrowd **cannot be scripted**.

For programmatic brand-asset generation at volume, use an image-generation service with a documented API and
vectorize downstream (e.g. raster generation → an auto-trace step → SVG), and run trademark clearance per mark.
Note that the resale restrictions in §3d would in any case block a "generate and sell logos" product built on
BrandCrowd output.

---

## 9. Sources

- `https://www.brandcrowd.com/` — homepage, JSON-LD (`"Over 100K templates"`)
- `https://www.brandcrowd.com/maker/legals/termsofuse` — Terms of Use, last updated 11 September 2025
- `https://www.brandcrowd.com/maker/legals/servicetermsandconditions` — Service Terms (licences, refunds, AI)
- `https://www.brandcrowd.com/maker/about`, `/maker/sell-logos`, `/maker/affiliate`
- `https://www.brandcrowd.com/robots.txt`, `sitemap-index.xml`, `sitemap-main-pages-sitemap.xml`
- `https://en.wikipedia.org/wiki/BrandCrowd` — Incspring → Brandstack → DesignCrowd acquisition history
- Tekpon, InBound Blogging, Trustpilot, PissedConsumer — third-party pricing and complaint signal
