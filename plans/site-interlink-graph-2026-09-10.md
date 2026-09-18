# Internal link graph — globalhighlevel.com

Date: 2026-09-10
Method: source-body graph from 909 post JSON files (href extraction, redirects resolved against `globalhighlevel-site/_redirects`) plus the **render-time canon** in `build.py` / `verify.py` Check 4. Live sitemap used to confirm which URLs exist. No headed crawl.

Two graphs exist. Mixing them produces fake orphans.

1. **Stored body graph** — links authors actually wrote into `html_content`.
2. **Rendered graph** — body after unwrap/inject + template chrome (eyebrow, hub-link block, circle prev/next, related cards, CTAs, nav, footer).

Caleb silo rule (canon since v0.2.11.0): followed editorial links stay **same language + same topic**. Conversion links to `FUNNEL_SINK_SLUGS` are exempt. Series parent/child is exempt.

---

## Rendered graph (what Google/Bing actually crawl)

`verify.py` Check 4 is the source of truth for this layer. It requires:

- Every spoke follows up to its hub (eyebrow + `_hub_link_block`, unless sink / EN pillar-blog copy).
- Link circles close inside each language+topic silo with 2+ members (prev/next wrap).
- Template links never cross language or topic.
- The EN money page emits **zero** outbound followed `/blog/` or `/category/` links.

So on the rendered site:

- **True orphans of the crawlable graph are rare.** A post in a 2+ silo sits on a circle, a category hub, language pagination (except the ES page-1 hole), and usually related cards.
- **The money page is a designed dead-end** for internal equity (sink). Outbound is affiliate + `/about/` in the author box.
- Homepage, language hubs, and category hubs are the inlink engines.

Do not "fix" body-level orphans by hand-wiring cross-silo links. The unwrap pass will drop them, `verify.py` will stay green, and the link will vanish (`unwrap_cross_silo_links` / `enforce_anchor_caps` do not name what they stripped).

---

## Source-body graph (what is actually written)

| Metric | Count |
|---|---:|
| Posts with ≥1 internal body outlink | 839 |
| Posts with **zero** internal body outlink (dead ends in JSON) | 70 |
| Posts with **zero** internal body inlink (body orphans) | 846 |
| Distinct source posts that body-link the EN money page | 515 |
| Cross-silo body links (before unwrap; excluding funnel sinks) | 41 |
| Dead internal targets after redirect resolve | **0** |
| `fp_ref=` outbound GHL hrefs in bodies | 1920 |
| `gohighlevel.com` hrefs **without** `fp_ref` in bodies | 74 (help-doc citations are the allowed class) |

Body orphans by language: EN 484 / ES 209 / IN **145 (all of them)** / AR 8.

Body dead-ends by language: **IN 63** / EN 3 / ES 2 / AR 2. India firehose pages mostly do not interlink in JSON; the template has to do all the work.

Interpretation: the restored firehose is a pile of how-tos that almost never name each other. Interlinking is a **build feature**, not a corpus feature. That is fine for silo hygiene. It is weak for hub↔spoke *editorial* context (the injected pillar link is one multi-word keyword match, capped, and easy for `enforce_anchor_caps` to unwrap).

---

## Hub ↔ spoke gaps

EN hubs (template guarantees spoke→hub except the sink):

| Hub | EN spokes | Body links **to** that hub |
|---|---:|---:|
| `/category/agency-white-label-saas/` | 178 | near-zero in stored JSON (hub-link is injected) |
| `/category/crm-communication/` | 130 | same |
| `/category/ai-receptionist-lead-capture/` | 111 | same |
| `/category/payments-pricing/` | 58 | same |
| `/category/sites-funnels-reputation/` | 30 | same |

Gaps that survive render:

1. **Footer omits the largest hub.** Agency White-Label & SaaS is 341 posts and is on the homepage cluster grid, but `_footer_clusters` lists only four topics. Every page's footer under-links the biggest silo.
2. **Topics dropdown is unused.** `dropdown_links` is computed in `base_html` and never rendered. Nav has no Topics control. Guides jumps to `/#guides` (EN/ES) or the language hub (IN/AR).
3. **`/es/` page 1 does not list the 18 newest Spanish posts** (slice consumed, cards discarded). Those 18 are not orphans (category + sitemap) but they lose the language-hub inlink the other 231 get via `/es/page/N/`.
4. **Pagination is not sitemapped.** EN `/page/2..29/`, `/es/page/2..14/`, `/in/page/2..9/` exist and have internal links from the hub strip, but no sitemap entry. Policy, not a bug. They are weak equity pages.
5. **AR AI and AR Payments** (1 post each) have no language-topic hub. The posts still appear on `/ar/` cards.

Hub → spoke: EN category pages list spokes. Language category pages list that language's spokes. Related cards rotate inside the silo. Circle nav wraps. That is a closed loop, not a pyramid with a strong editorial pillar paragraph linking out to named children — except the 5 EN pillar bodies sitting on the category URL.

---

## Thin clusters

Below 8 posts, language+topic:

| Lang | Topic | n | Category page? |
|---|---|---:|---|
| ar | AI Receptionist & Lead Capture | 1 | no |
| ar | Payments & Pricing | 1 | no |
| ar | CRM & Communication | 2 | yes |
| es | Sites, Funnels & Reputation | 2 | yes (barely) |
| ar | Agency, White-Label & SaaS | 4 | yes |

Arabic mean word count is 135. Those "pages" are not clusters; they are leftover restore stubs.

The **fat** cluster is the problem on the other side: Agency White-Label & SaaS is 178 EN + 105 ES how-tos, many of them generic firehose. That is a thin-meaning cluster: lots of URLs, little differentiation, competing titles.

Sites/Funnels is the only small *English* hub (30). It has a real pillar on the category URL.

---

## Designed dead ends vs accidental dead ends

| Page | Kind | Why |
|---|---|---|
| `/blog/gohighlevel-free-trial-30-days-extended/` | designed sink | `mvp_minimal_links`. No related cards, no circle, no followed category eyebrow, body `/blog|/category` anchors stripped. Author box still → `/about/`. |
| Template CTA #3 / nav CTA | designed outbound | affiliate bootcamp, `nofollow`. Equity is not supposed to leave with them. |
| `/trial/` | attribution dead-end for Googlebot | `Disallow` + `noindex`. AI crawlers allowed. |
| 70 JSON dead-ends | accidental in source | mostly IN. Render still adds hub + circle + related (if silo ≥2) + CTAs. |

Pricing pages are **not** sinks. They accept cross-silo inbound (`FUNNEL_SINK_SLUGS`) and still emit related/circle/hub links. Only the EN trial blog is airtight.

---

## Duplicate / competing money pages

Canon (this repo): one SEO money page per intent, plus a parallel noindex attribution URL.

**Keep (do not merge this sprint):**

| Intent | EN SEO | Attribution | Notes |
|---|---|---|---|
| 30-day trial / coupon / discount | money page | `/trial/` | EN promo blog was 301'd into the money page on purpose. |
| Pricing / plans / hidden costs | EN pricing guide | — | Distinct query cluster. |

**Compete with the EN money page today:**

1. **`/services/`** — indexable, $497/mo Bill services, GHL webhook. Same audience, different offer. Nav does not feature it. Sitemap priority 0.9. If someone lands from "GoHighLevel automation" this can steal the trial click.
2. **ES `codigo-promocional-gohighlevel-2026-descuentos-reales`** — standalone discount page. EN ran the opposite experiment (killed the promo blog). Unproven on Bing's 250-page cap (absence ≠ zero). Phase 2 / ES, not this sprint.
3. **Nine Spanish "qué es GoHighLevel" URLs** splitting ~130 Bing impressions (TODOS, 2026-08-29). Consolidation target already named: `que-es-gohighlevel-mejor-alternativa-herramientas-locales-latinoamerica` (14 inbound 301s). **Needs a human call to 301 live pages. Out of this sprint.**
4. **Language trial/pricing siblings** — correct (translations map on the money page). AR versions are ~300 words and should not rank; they should not be deleted blindly either.
5. **AI pricing splinters** (2026-07-29): Voice AI / AI Studio / AI Employee / AI Agent pricing + the AI hub pillar. Intentional silo, but they compete with EN pricing for "ghl ai pricing" style queries.
6. **Older EN "AI pricing 2025" posts** (`how-to-maximize-ai-pricing-in-gohighlevel-2025-update`, `leverage-ai-pricing-updates-gohighlevel-save-more`) still live next to the 2026 AI-silo pages.

**Redirect oddity:** `/es/start/` → ES **pricing**, while `/start/` → EN **trial**. Asymmetric. Do not "fix" without Bill; it may be intentional (ES commercial intent).

---

## Inlink concentration

Template + 515 body links already point at the EN money page. Mid-article and byline CTAs on **every** non-tldr post add more `rel=nofollow` hops to it. Direct affiliate (nav + CTA #3) skips it.

Consequence for cash: a lot of internal "trial" traffic is a **second pageview** on the money page, not an affiliate click. If the money page snippet/CTR is weak (documented 0.37% Bing CTR vs 2.70% ranked-page average, changelog v0.3.16.1), the hop taxes conversion. Measurement must split:

- `ghl_click` (fp_ref outbound)
- `cta_click` (internal trial hop, `.btn-amber`, nav without fp_ref — nav **has** fp_ref so it is `ghl_click`)

Docs in `CLAUDE.md` still mention `affiliate_click`. The listener never fires that name.

---

## Graph risks this plan will not "fix" by deleting

- 846 body orphans: expected. Circles exist. Do not mass-delete.
- 580 overlong titles: copy work, Bing-prioritized, already a ratchet. Not a graph problem.
- ES qué-es cluster: consolidation is a human one-way door.
- Cross-silo 41 in JSON: unwrap at render. Adding more body links without checking built HTML is how links disappear while tests stay green.
