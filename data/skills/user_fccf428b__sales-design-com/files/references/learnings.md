# Design.com Learnings

Accumulated tips, gotchas, and corrections discovered during use. Claude reads this at the start of each
invocation and appends new learnings as they're discovered.

<!-- Add entries below in format: **YYYY-MM-DD**: Learning description -->

**2026-07-26**: Research baseline — platform capabilities, the two-library free/premium split, pricing ladder, file
formats, licensing/IP-review terms, billing complaints, and the no-API reality captured from live design.com pages
(homepage, /logo-maker, /maker/free-logos, /blog) plus third-party sources (appscribed review, DesignCrowd blog's own
Design.com review, usefulai + superside listicles, PissedConsumer/Trustpilot/Reddit complaint themes). Re-verify
against live pages before relying on specifics.

**2026-07-26**: **Corporate lineage** — Design.com is **DesignCrowd's own AI subsidiary/successor** (launched 2024),
sister to **BrandCrowd**; same parent, three different models. Design.com = AI/DIY subscription brand kit;
DesignCrowd (`/sales-designcrowd`) = human contest marketplace with full copyright transfer; BrandCrowd = sister
template/AI maker (backlogged, not yet a skill). "DesignCrowd's AI tool" = Design.com. This is the highest-value
disambiguation in the skill — the four "design*" logo brands (Design.com / DesignCrowd / Designs.ai / Designhill /
DesignEvo / DesignBro / DesignMantic) are heavily confusable.

**2026-07-26**: **THE key structural fact — two separate logo libraries.** A curated **"Free Logos" collection**
(design.com/maker/free-logos) is genuinely 100% free: full **PNG/JPG + vector SVG/EPS/PDF**, **no watermark**,
worldwide irrevocable commercial license, free editing. The **much larger premium library** (bulk of 435k+ templates)
needs a **paid plan** to download. This resolves a direct contradiction in the sources: Design.com's own blog claims
"a genuine free plan requiring no upgrade to download logos … vector exports at every pricing level, even the free
tier," while appscribed reports "Free tier: browse and customize templates; **no export access**." Both are right —
they describe different libraries. Always ask which library the user's mark came from before discussing price.

**2026-07-26**: **Pricing is genuinely unsettled across sources — do not quote a fixed ladder.** Variants found:
(a) Starter ~$15/mo (~$5/mo annual) / Value ~$24/mo (~$6/mo) / Premium ~$29/mo (~$7/mo) [appscribed + DesignCrowd
blog]; (b) a **"Brand" plan** ~$72/yr or ~$12/mo with vector files, 1,200+ templates, website, domain registration,
brand guidelines [cybernews]; (c) Design.com's own blog: paid plans "from **$3/month billed annually**"; (d)
cybernews also cites Starter at $15/mo **or $60/yr**. Name plans by what they unlock, quote a range, send users to
checkout.

**2026-07-26**: **Vector is NOT the gate — the library is.** SVG/EPS/PDF ship with free-collection logos and at every
paid tier, so the "which tier do I need for vector?" trap that bites Turbologo/Logobean does **not** apply here.
Higher tiers add **scope** (website builder → digital business card → link-in-bio), not file quality. Animated marks
also yield GIF/MP4.

**2026-07-26**: **Licensing is unusually strong for the budget cluster but still non-exclusive by default.** Every
logo gets a **manual IP review** + copyright check (a real differentiator), and the license is "worldwide,
irrevocable … any commercial and non-commercial purpose." BUT the underlying icon stays in the library unless the user
buys an **exclusive or buyout license** on a **select** logo, which **removes the icon from the library**. That's the
genuine exclusivity path — most peers offer nothing equivalent. A license is still not a registered trademark.

**2026-07-26**: **The complaint cluster has ONE root cause: subscription vs one-time expectation.** PissedConsumer
~1.8★ (unexpected/recurring charges, unauthorized charges, unresolved refunds); Trustpilot ~189+ reviews and an
r/SmallBusinessOwners thread ("Is Design.com a ripoff for logos?") echo it. Design.com bills a **recurring
auto-renewing plan** while most of the budget cluster is pay-once-per-logo. Cancellation IS self-serve from the
dashboard; **refund eligibility depends on whether paid assets were downloaded** + the published window. Surface the
word "subscription" before the user pays. Support: design.com/maker/contact.

**2026-07-26**: **No developer surface at all.** No public API (no `api.design.com`, no developer docs, no OpenAPI
spec, no Postman collection), no webhooks, no Zapier/Make app, no MCP, and **no self-serve white-label/reseller
program**. Also **no affiliate program found** — unusual for this cluster (Looka, LOGO.com, DesignEvo, Designhill,
LogoAI, FreeLogoDesign all run one), so re-check on the next sweep in case it exists but is unindexed.

**2026-07-26**: **Differentiator worth leading with** — the **AI chat editor** (plain-language edit requests on a
generated mark) plus prompt-based generation. Most of the budget cluster is template-fill or one-shot AI with a
manual editor; conversational editing is the fastest way to push a shared template away from looking generic, which
is the direct answer to the "my logo looks like everyone else's" complaint.

**2026-07-26**: Live-site fetch notes — design.com homepage, `/logo-maker`, `/maker/free-logos` and `/blog/*` all
fetch cleanly. **`/pricing`, `/plans` and `/maker/pricing` all 404** (the live pricing route wasn't located), and
**trustpilot.com + cybernews 403 to WebFetch**. Use the blog + third-party reviews for pricing, and treat every figure
as best-effort.
