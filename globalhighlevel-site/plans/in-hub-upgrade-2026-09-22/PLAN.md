# `/in/` India hub upgrade — draft plan

**Status: AWAITING WILLIAM TASTE. Do not land.**

Client: Global HighLevel only. URL stays `https://globalhighlevel.com/in/`. This is an upgrade. It is not a 410, not a 301, and not a new URL.

William's queue lock: LATAM done (v0.3.19.0) → Desktop quiet → this hub → AI cluster depth next. This PR stops at taste. Dual-Cursor land waits for a manager reply of GO.

## How `/in/` is authored

`/in/` is not a post. `build_language_hub()` in `globalhighlevel-site/build.py` builds it from every post whose language is `en-IN`.

| Piece | Where |
|---|---|
| Page | `build_language_hub()`, language code `en-IN`, prefix `/in` |
| SERP title | `hub_title_for("en-IN", ...)` |
| Meta description | `hub_descriptions["en-IN"]` |
| Page-1 pitch | `india_hub_intro()`, prepended on page 1 only |
| Cards, chips, pagination | the shared catalog branch, still used on page 1 |
| Posts | `globalhighlevel-site/posts/*.json` with `"language": "en-IN"` |

`/es/` page 1 throws its first 18 cards away and renders a hand-written hub. `/in/` must not copy that. The India title interpolates the post count, and the count is honest only while page 1 lists the cards and links `/in/page/2/` onward. The intro is additive. The cards stay.

## What is live today

Fetched as the current production page before this draft:

| | Live |
|---|---|
| Title | `GoHighLevel India: 145 Guides, UPI and WhatsApp` (47 characters at 145 posts) |
| H1 | `GoHighLevel — India` |
| Body | Label, that H1, the count line, topic chips, a card grid, pagination |
| CTA | No bootcamp button on the hub itself |
| Bing | Historically about 133 impressions and 0 clicks (the brief). The title was rewritten on 2026-08-20 (v0.3.12.0) for that zero-click result. It has not had a long measurement window. |

145 posts, all `en-IN`, counted 2026-09-22:

| Topic | Posts |
|---|---|
| Agency, White-Label & SaaS | 54 |
| CRM & Communication | 35 |
| AI Receptionist & Lead Capture | 29 |
| Payments & Pricing | 19 |
| Sites, Funnels & Reputation | 8 |

No new posts in this draft. The library is already large. The hub was thin because the page never said what the library is for.

## Proposed title and H1

| | Proposed | Characters |
|---|---|---|
| `<title>` | `GoHighLevel India: 145 Guides, UPI and WhatsApp` | 47 at the current count. The `{count}` stays interpolated. |
| Rendered title | the same string. No brand suffix. 47 is over 40, so `compose_title()` does not append ` \| Global High Level`. | under 60, so Check 7 does not grow |
| H1 | `GoHighLevel for Indian agencies` | visible page only |
| Meta description | `WhatsApp, Razorpay, and white-label for Indian agencies. Razorpay does not bill SaaS Mode. UPI is Razorpay checkout, not its own HighLevel row. Card required.` | 158 |

The SERP title is unchanged on purpose. It already names UPI and WhatsApp, the count is real, and growing the over-60 title count is forbidden unless another over-long title is retired. Changing this title is a taste question, not a requirement of the upgrade.

Paginated titles stay `GoHighLevel India: UPI and WhatsApp — Page N`. They do not repeat "145 Guides".

## What the draft page says

Page 1, above the existing card grid:

1. H1 and a three-sentence stack: WhatsApp, Razorpay, white-label.
2. A featured card to `/blog/gohighlevel-pricing-india-2026-rupees-complete-guide/`. The card says that guide still claims Razorpay can bill SaaS Mode, and that HighLevel's table says no.
3. Three clusters, each with one category link:
   - WhatsApp → `/in/category/crm-communication/` and the WhatsApp setup post
   - Razorpay and UPI → `/in/category/payments-pricing/` and the Razorpay setup post
   - White-label and SaaS Mode → `/in/category/agency-white-label-saas/` and the white-label post
4. One bootcamp CTA: `affiliate_href("en-IN", campaign="in-hub", content="hub_cta")`, which is `highlevel-bootcamp` with `fp_ref=amplifi-technologies12`, `utm_campaign=in-hub`, `utm_content=hub_cta`, `rel="nofollow noopener"`. The line next to it: a card is required, about a $1 verification hold, the subscription is not charged during the trial.
5. Then the existing chips, all 18 page-1 cards, and pagination. The subtitle `{N} guides in India` stays.

Pages 2+ stay a catalog. They share the new meta description. They do not repeat the hero.

## Payment facts (do not invent past these)

Checked 2026-09-22. Detail is in `fact-ledger.md` in this folder.

- Razorpay is a documented HighLevel marketplace app (help `155000002559`, modified 2025-12-12). It is not invented.
- The provider table (help `155000006075`, modified 2026-02-17) marks Razorpay **Yes** for order forms, forms, surveys, email checkout, the store, invoices including recurring, payment links, courses, communities, and calendars.
- The same row marks Razorpay **No** for charging a card on the contact page, **SaaS Mode**, the service menu, and POS.
- The Razorpay FAQ says the official app does not do SaaS Mode or wallet recharges, because it cannot charge a saved card off-session.
- The table has a Razorpay row and **no UPI row**. UPI is a method inside a Razorpay checkout, not a separate HighLevel gateway.
- **PayU is not in the table.** Several India posts call PayU native. The hub says that sentence is wrong. Those posts are not rewritten here.
- WhatsApp connects per sub-account (help `155000001980`). Meta bills conversation fees separately (error 131042, help `155000007938`).
- SaaS Mode is Yes for Stripe, Authorize.net, NMI, and Square. Not for Razorpay.

The India pricing guide (`gohighlevel-pricing-india-2026-rupees-complete-guide`) still says SaaS Mode can bill with Razorpay, and it names PayU. This draft does not edit that post. The hub card warns the reader. Editing it is taste question 3. It is a live page with FAQ schema stored twice in `html_content`.

## What already exists

- `hub_title_for()` and `scripts/test_hub_titles.py` already pin the India title, the interpolated count, and distinct paginated titles. This draft does not change that function.
- `/es/` page 1 is the visual pattern (`.hh`, `.guidecard`, `.clusters`, `.es-banner`). Reused. No new CSS.
- `affiliate_href()` already stamps `utm_content` for GA4 `ghl_click`. The hub CTA uses it. No analytics code change.
- Category pages already exist for the three clusters (54, 35, and 19 posts). No new spokes.
- LATAM (`/es/gohighlevel-latam/`, v0.3.19.0) is the honesty pattern: say which flow a processor actually serves. This hub does the same for Razorpay vs SaaS Mode.

## NOT in scope

- Killing or 301ing `/in/`.
- New India posts, new Spanish posts, homepage redesign.
- Retitling the frozen English money paths (free-trial post, agency guide) through 2026-10-13. Linking to them is allowed. This draft does not link the frozen English trial post. The CTA goes to the bootcamp.
- AI Agent Studio cluster depth.
- Rewriting the 145 India posts that say "no credit card", call PayU native, or say Razorpay bills SaaS Mode.
- VERSION bump, CHANGELOG, `seo-cooldown.json`, gbrain timeline. Those are land steps, after GO.
- Desktop work. It was marked quiet.

## Failure modes

| Failure | What the reader sees | Guard |
|---|---|---|
| Cards dropped to copy `/es/` | Title says 145 guides, page 1 cannot list them | `test_in_hub.py` requires the card grid, `40 guides in India`, and `/in/page/2/` |
| Razorpay described as the SaaS Mode processor | Agencies plan client billing on an app HighLevel marks No | Pinned phrase `does not bill SaaS Mode` on page 1 and in the meta description |
| UPI described as its own HighLevel product | A searcher expects a UPI row that the provider table does not have | Pinned phrase `UPI is not its own row` |
| PayU called native | Same class of miss as the LATAM PagBank claim | Pinned phrase `PayU is not in the provider table` |
| CTA loses `fp_ref` or uses the Spanish bootcamp | Measurement and commission break | Test requires `fp_ref=amplifi-technologies12`, `utm_content=hub_cta`, and rejects `highlevel-bootcamp-es` |
| Intro copied onto `/es/` or `/ar/` | Wrong language, wrong payment law | Quiet-edge test |
| Title grows past 60 | Check 7 ratchet fails | Title string unchanged |
| "$0" or "no credit card" on the hub | Trial-claim gates, and a false promise | Copy says card required and about a $1 hold. Test rejects both phrases |

## Test plan

From `globalhighlevel-site/`:

1. `python3 -m pytest scripts/ -q`
2. `python3 build.py`
3. `python3 verify.py`

`scripts/test_in_hub.py` renders the real builder into a temp directory. It does not assert on the helper alone.

## Architecture

```
en-IN posts (145)
        |
        v
build_language_hub()
        |
        +-- page == 1 --> india_hub_intro()  +  chips + cards + pagination
        |
        +-- page >= 2 --> catalog only (shared meta description)
```

`unwrap_cross_silo_links()` does not run on hub HTML. These links are in the template, so they are not stripped. Help-doc links are citations, not affiliate CTAs, and do not carry `fp_ref`.

## Decision audit trail

| # | Decision | Class | Why |
|---|---|---|---|
| 1 | Upgrade the existing `/in/` URL | Locked by William | Not a kill |
| 2 | Keep the card grid under the intro | Mechanical | The count in the title is only true if page 1 lists the posts |
| 3 | Keep the SERP title | Taste, recommended | Already specific, under 60, count is real. A new title needs a retired over-long title if it exceeds 60 |
| 4 | Change the H1 | Taste, recommended | The live H1 is the thin part |
| 5 | No new posts | Mechanical | 145 posts already cover the three clusters. The gap is the hub, not a missing spoke |
| 6 | State Razorpay's SaaS Mode limit on the hub, do not rewrite the pricing guide in this PR | Taste, recommended | The guide is a live page with duplicated FAQ schema. The hub warns. A rewrite is a separate GO |
| 7 | One bootcamp CTA with `utm_content=hub_cta` | Mechanical | Measurement stays intact, `fp_ref` required |
| 8 | No version bump until land | Mechanical | Taste hold. v0.3.19.0 is LATAM and stays the shipped version |

## Taste questions for William

1. **H1.** Recommended: `GoHighLevel for Indian agencies`. Live is `GoHighLevel — India`. The SERP title does not change.
2. **SERP title.** Recommended: keep `GoHighLevel India: {count} Guides, UPI and WhatsApp`. It is 47 characters at 145 posts. A replacement that drops the count, or that runs past 60, is a different call.
3. **Pricing guide.** The featured card links the India rupee pricing guide and says its Razorpay-for-SaaS-Mode sentence is wrong. Recommended: leave the guide for a follow-up. Say if this PR should correct that post (and the PayU sentences) before land.
4. **Tone of the correction.** The hub tells the reader the older posts are wrong about PayU and about SaaS Mode. Recommended: keep that on the page. The alternative is a softer cluster that only states the limit and does not mention the older posts.

## Land checklist (after GO only)

- Dual-Cursor review, then VERSION and CHANGELOG.
- gbrain timeline on `globalhighlevel-seo-changelog` before any push to `main`.
- `seo-cooldown.json` mirror for `/in/`.
- Re-run pytest, build, verify on the land commit.

## GSTACK REVIEW REPORT

Draft only. Not approved. Not landed.

- gstack preflight: bun 1.4.2, `~/.claude/skills/gstack/ship/SKILL.md` and `review/SKILL.md` present after `./setup`.
- Codex outside voice: not installed (`CODEX_NOT_INSTALLED`). Missing coverage. Dual-Cursor is the land reviewer William already requires. Do not treat this draft as that pass.
- CEO: upgrade, do not kill, do not add spokes. The thin page is the product bug. Completeness here is an honest hub over 145 existing posts, not 145 rewrites.
- Design: reused the `/es/` hub classes. No new visual system. UI scope is the page-1 intro only.
- DX: skipped. This is a reader page, not a developer tool.
- Eng: one function, one branch inside the existing hub builder, one rendered-HTML test. Title ratchet untouched.

**AWAITING WILLIAM TASTE. Do not land.**
