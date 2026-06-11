# Changelog

All notable changes to globalhighlevel.com's static-site build are documented here.

## [0.1.0.11] - 2026-06-11
### Added
- **New "GoHighLevel vs alternativas en LATAM" section on the pricing pillar.** Added a grounded, honest comparison H2 (id=alternativas, with a Table-of-Contents entry) so the pillar finally answers "what should I use instead / alongside GHL." Frames GHL's real edge (all-in-one breadth + SaaS-mode white-label resell + unlimited sub-accounts) against where rivals genuinely win (price, WhatsApp-first UX, native local payments/invoicing, Spanish-native support), then a comparison table — Clientify (€39/mes anual), Kommo ($15/usuario/mes), Leadsales ($97/mes, 3 usuarios), Zoho Bigin ($7/usuario/mes anual), Whaticket ($49/mes, complemento) — each with a straight "cuándo gana sobre GHL" reason, plus a HubSpot note (5–50x pricier, rarely a head-to-head). Competitors are deliberately NOT hyperlinked (this is an affiliate page; don't pass authority/traffic to rivals); internal link to the LATAM payments page. Built via the /research-product-wedge protocol: drafted from the Step-5 competitor vault source with a provenance ledger (every published price `supported`; unverified-price tools — Treble, Zenvia, Cliengo, DataCRM — deliberately excluded rather than guessed). Two-model review (the human-editor replacement): Codex price-verified every figure against the source and caught the missing "anual" qualifiers on Clientify/Zoho plus an unsupported "Starter" phrasing; a Claude adversarial native-Spanish pass caught 2 blocking issues ("e facturación"→"y facturación" grammar, "inflar a GoHighLevel" calque). All fixes applied. Verified: build + `verify.py` (0 dead links). Block 2 of 2 (block 1 was the currency grounding, v0.1.0.10).

## [0.1.0.10] - 2026-06-11
### Changed
- **Grounded the pricing pillar's "Precios en moneda local" table with dated, sourced rates.** The section had stale, ungrounded estimates — the Argentine peso row especially (≈AR$97,000 at an old ~1,000 USD rate, vs the real ~1,450 today, so it was ~45% too low). Replaced MXN/COP/ARS/EUR with grounded 2026-06-11 conversions ($97 ≈ MX$1,686 / COP$340,947 / AR$140,650 oficial / €84; $297 and $497 likewise), added a dated stamp, three honest caveats (rates are a one-day snapshot and fluctuate; Argentina's oficial-vs-blue/MEP split with the blue figure shown; the card/processor spread means the real charge runs a bit higher than mid-market), an external `nofollow` link to xe.com so readers can check the live rate, and an internal link to the LATAM payments page. Upgraded the existing section in place (no duplicate). Built via the /research-product-wedge protocol: drafted from the Step-4 currency vault source with provenance tags (every figure `supported`), Codex number-verified every peso figure against the source (all match, math clean, caveats faithful), and a Claude adversarial native-Spanish register pass returned CLEAN (0 blocking) — the two-model review that now stands in for a human editor. Content-only; no invented numbers. Verified: build + `verify.py` (0 dead links). Block 1 of 2 (competitor comparison ships separately).

## [0.1.0.9] - 2026-06-11
### Fixed
- **Corrected payment-integration claims on the Spanish `que-es` page.** Two sentences listed MercadoPago, Conekta, PayU and Transbank together as if all were native GoHighLevel payment integrations. Verified against GHL help docs + payment-app roundups: GHL natively supports Stripe, PayPal, Authorize.net, NMI, Square, plus MercadoPago for LATAM client collection (7 countries) — Conekta, PayU and Transbank require a custom API integration, not native support. Reframed both mentions to say so (MercadoPago native; the others "vía integración personalizada"), bringing `que-es` in line with the researched `gohighlevel-latam-pagos-agencias` page and removing a claim that could mislead LATAM agencies about out-of-the-box gateway support. Content-only; no invented numbers. Verified: build + `verify.py` (0 dead links). Closes the Conekta/PayU follow-up flagged in 0.1.0.8.

## [0.1.0.8] - 2026-06-11
### Changed
- **Deepened the thin Spanish "qué es" page + added FAQPage schema across the LATAM cluster.** `que-es-gohighlevel-...-latinoamerica` was the weakest page in the Spanish cluster (3 H2s, ~600 words, no FAQ). It now runs ~8 H2s / ~1,720 words: adds *¿para qué sirve?* (real LATAM agency use cases), a grounded cost answer that links the pricing pillar, an honest *¿es gratis?* (paid from $97/mo; 30-day trial via affiliate, card + ~$1 verification hold, communication-surcharge caveat), and a *para quién es / para quién NO* section, plus a 5-question **FAQPage** JSON-LD block. Also added FAQPage schema to `gohighlevel-latam-pagos-agencias` (wrapping its existing 3 Q&As) and `como-configurar-primera-automatizacion-...` (new 3-question FAQ section) — so all four Spanish cluster pages now carry FAQPage schema (only the pricing pillar did before), the direct lever for AI-engine citation. Every claim grounded in the LATAM pricing research vault + verified site facts (no invented numbers); reviewed by codex (Spanish quality + grounding + FTC) which flagged REVISE → revised (removed unsourced Conekta/PayU native-payment claims from the new copy, added the comms-surcharge caveat, softened one overpromise). Verified: build + `verify.py` (0 dead links), all 3 FAQPage JSON-LD valid and rendering in built HTML. Deploy gate: SEO Changelog Sheet rows 976-978. Known follow-up (pre-existing, not this change): `que-es` original copy still has 4 Conekta/PayU mentions that may contradict the researched payments page.

## [0.1.0.7] - 2026-06-10
### Fixed
- **Spanish affiliate links now route to the localized `-es` bootcamp.** Every Spanish surface (the `/es/trial` + `/es/start` landings, `base_html` nav/footer CTAs on `es` pages, the in-post end CTA, and the 4 in-content links in `gohighlevel-precios-planes-2026-guia-completa`) pointed at the English `gohighlevel.com/highlevel-bootcamp`. They now use `gohighlevel.com/highlevel-bootcamp-es` (Spanish landing: "BOOTCAMP GRATIS + PRUEBA DE 30 DÍAS"). `build.py` gains a language-aware `affiliate_for(lang)` helper; EN/IN/AR are unchanged (verified by control). `fp_ref=amplifi-technologies12` (FirstPromoter) attributes by parameter, not landing slug, so attribution is unchanged — confirmed via headless load: the `-es` page set `_fprom_code=_r_amplifi-technologies12` and fired `POST t.firstpromoter.com/track/new → 200`. Verified: build + `verify.py` (0 dead links). Deploy gate: SEO Changelog Sheet rows 974-975.

### Added
- **Spanish pricing silo (Caleb internal-link structure).** Wired the 4 existing Spanish pages into a hub-and-spoke silo with no new/duplicate pages: `gohighlevel-precios-planes-2026-guia-completa` (pillar) links down to its three variations (`que-es-...latinoamerica`, `gohighlevel-latam-pagos-agencias`, `como-configurar-primera-automatizacion...`); each variation links back up to the pillar; the variations form a link circle (que-es → pagos → automatizacion → que-es). 9 editorial body links, unique keyword-rich Spanish anchors that describe the destination, no brand-name anchors, pointing at `/blog/` pages (not the robots-blocked `/es/trial`). The pricing pillar previously had zero internal links. Verified: `verify.py` PASS (0 dead links). Deploy gate: SEO Changelog Sheet rows 970-973. (Landed on `main` as #8 without a version bump; documented here.)

### Removed
- **Vestigial repo-root `posts/` directory.** A pre-restructure leftover (13 post JSONs all duplicated in `globalhighlevel-site/posts/`, the canonical store `build.py` reads and Cloudflare builds from). It was read by nothing — `scheduler.py`'s "sync root posts" loop pointed at a nonexistent nested path. 9 of its files still carried the false "no credit card" claim, so it was both a regression trap and an FTC-risk string sitting in tracked files. Removed the dir and corrected the misleading CLAUDE.md "sync both posts/ dirs" rule. Live site unchanged. Deploy gate: SEO Changelog Sheet row 969. (Landed on `main` as `700a725` without a version bump; documented here.)

## [0.1.0.6] - 2026-06-09
### Fixed
- **Removed the false "no credit card required" trial claim site-wide.** Every trial surface — the English/Spanish/India/Arabic `/trial` and `/start` pages, the FAQPage structured data, and 13 blog posts (including the top converter `gohighlevel-free-trial-30-days-extended` and the pricing guide) — claimed the GoHighLevel 30-day trial needs no credit card. Per GoHighLevel's own help doc (3DS card support on the affiliate signup page) and two support agents, that is false: a card IS required to start — a ~$1 verification hold the bank releases, not a subscription charge. All 32 instances are reframed to the honest, still-compelling "$0 for 30 days, just a ~$1 card-verification hold, no subscription charge, cancel anytime" (with matching Spanish/India/Arabic copy). Fixes an accuracy problem, removes an affiliate-trust/conversion leak (prospects promised "no card" then hitting the card screen), and corrects the FAQ structured data that Google and AI engines quote verbatim. Verified: build + `verify.py` (0 dead links) + 0 "no credit card" claims in the built HTML. Deploy gate: SEO Changelog Sheet row 968.

## [0.1.0.5] - 2026-06-09
### Fixed
- **Post-prune cleanup: the sitemap, navigation, and breadcrumbs no longer point at the category and language pages the prune emptied.** The 2026-06-03 prune (931 posts) left `build.py` emitting all 8 topic categories and all 4 language hubs into `sitemap.xml` and the nav regardless of whether any posts remained, so Google and visitors hit 27 dead category/language URLs (e.g. `/category/ai-automation/`, the entire `/ar/` Arabic tree) plus a dead `/blog/` and one Spanish post breadcrumb. `build.py` now gates every category link, language-hub link, and post breadcrumb to pages that actually got built: `sitemap.xml` drops from 53 to 26 live URLs (0 dead), the homepage Topics menu / sidebar / footer link only the 5 live categories, the language picker drops the empty Arabic hub, and a post whose category page wasn't built renders the category as plain text instead of a dead link. It also gates `hreflang` alternate links (both the page-level alternates and per-post translation maps) so they no longer advertise pruned language/category pages: this cleared ~20 pages of dead `hreflang="ar"` plus stale per-post translation alternates that still pointed at deleted sibling-language posts. The gates read live post counts on every build, so categories and languages reappear on their own as the nightly pipeline adds posts back. Verified with `build.py` + `verify.py` (Check 3: 0 dangling links) plus a full crawl of every built page checking both `<a href>` anchors and `<link rel="alternate" hreflang>` targets — all resolve to built pages. Deploy gate: SEO Changelog Sheet row 967.

## [0.1.0.4] - 2026-06-03
### Removed
- **Heavy prune: 931 zero-affiliate-click posts deleted (98.4% of the catalog).** Of 946 posts, only 15 produced any affiliate-link click in the last 90 days (GA4 `ghl_click` / `cta_click` / `affiliate_click` / `extendly_click`). Removed the 931 that produced zero — all 30-90 days old, the 35-posts/night firehose output that Google treats as scaled-content abuse. Kept the 14 click-earners + the LATAM pillar (`gohighlevel-latam-pagos-agencias`); structural/attribution pages (`/`, `/trial/`, `/start/`, language hubs) untouched. Sitemap shrinks 946 → 15 quality URLs. Mechanism: delete JSON → 404 (Google-canonical scaled-content removal). Per-page audit in `prune-plan/KILL.txt` + SEO Changelog Sheet rows 36-966. Fully reversible via `git revert`. Traffic context: Bing index (Bing+Yahoo+DuckDuckGo) drives ~2.7× Google; AI referrals (ChatGPT/Perplexity/Claude) ≈ Google — affiliate-click criterion already counts all of them.

## [0.1.0.3] - 2026-06-03
### Fixed
- LATAM hub: affiliate CTA now points to the Spanish funnel landing /es/trial (was linking directly to the English gohighlevel.com bootcamp). Matches the es-post pattern.

## [0.1.0.2] - 2026-06-03
### Added
- **New Spanish pillar: "GoHighLevel en Latinoamérica — guía honesta de pagos para agencias"** (`/blog/gohighlevel-latam-pagos-agencias/`, `topic: Payments & Commerce`, `language: es`). Buyer-intent hub for LATAM marketing agencies: MercadoPago Flow B across 7 countries (AR/BR/CL/CO/MX/PE/UY); the SaaS Mode (Flow A) constraint (only Stripe/NMI/Authorize.net/Square, card-only checkout); Stripe Atlas workaround by country; honest "where GoHighLevel does NOT work" framing; country comparison table; FAQ; `dofollow` source citations + 30-day affiliate CTA marked `rel="sponsored"`. Grounded in the existing MercadoPago research vault; Codex drift-gated + native-Spanish third-voice reviewed + claim-ledgered. Surfaces under the Payments topic and the /es Español hub. (Earlier mistakenly published to the GHL blog CMS — wrong system; this repo is the canonical publish path.)

## [0.1.0.1] - 2026-06-01
### Changed
- **Upgraded the GoHighLevel pricing page (`/blog/gohighlevel-pricing-plans-2026-complete-guide/`) from 1,540 to ~2,650 words.** Rebuilt to the buyer-intent "ChatGPT-citation" recipe that the trial page already wins with: a one-line price answer up top (Starter $97 / Unlimited $297 / SaaS Pro $497, annual ~17% off), a "what GoHighLevel replaces" comparison table, a promo-code/discount section (links the canonical `/blog/gohighlevel-free-trial-30-days-extended/` — no duplicate page), an India-pricing answer, and 11 FAQ entries built from real GSC pricing queries plus FAQPage schema. Targets the pricing query cluster (~150 impressions/quarter, previously ranking page 7-9 with zero clicks). A codex fact-check pass fixed a usage-cost contradiction and trimmed unverifiable claims. Deploy gate: logged to the SEO Changelog Sheet (row 35) and `seo-cooldown.json`.

## [0.1.0.0] - 2026-05-27
### Added
- **`topic` as the real category axis, separate from language (language × topic restructure).**
  Every post now carries a `topic` field (one of 8 canonical topics) independent of its
  `language`. `build.py` organizes the site by `topic` (via a new `post_topic()` helper with
  a `category` fallback), so the two axes are no longer tangled. 373 posts that were trapped
  under language-bucket "categories" (`GoHighLevel en Español` / `GoHighLevel India`) now
  surface under their real topic.
- **`verify.py` phase-gate harness.** Re-runnable audit with 4 checks: Check 0 (a post's
  `language` field must not contradict its slug markers — catches a bad migration write that
  the other checks, which trust the field, cannot), Check 1 (root `/category/` English-only),
  Check 2 (no orphaned posts), Check 3 (no dangling internal links, allowlist now empty).
- **`migrate_lang_topic.py` reviewable migration tool.** Proposal-first (writes a CSV for
  human review), idempotent `--apply` that reads the reviewed CSV, fail-loud validation
  (rejects bad language/topic, aborts on duplicate slugs), and a writer that preserves each
  file's existing encoding + newline so a 2-field change is a 2-line diff, not a reformat.

### Changed
- **945 posts re-tagged** with a clean `language` + `topic` (4 India posts corrected `en`→`en-IN`,
  469 posts backfilled `language`). `category` kept for back-compat. Migration was AI-classified
  with the uncertain calls reviewed by hand.
- **Daily generators (5-blog, 6-india, 7-spanish, 9-arabic) stamp `topic` + `language`** on every
  new post, so the nightly pipeline no longer re-creates the language/topic tangle.
- **`categories.json` is topics-only** — the 2 language buckets are removed; old bucket category
  URLs 301-redirect to the `/es/` and `/in/` hubs. The 8 topic-page URLs are unchanged.
- **Language-hub category links respect a `min_posts` fallback** — the hub no longer links a
  per-language category page that isn't generated (single-post topics fall back to the `/lang/` hub).

### Fixed
- **`5-blog.py` classifier crash.** It iterated the `{topics, languages}` config dict by its
  string keys and raised `TypeError`, so English/podcast posts classified to the fallback. Now
  reads `categories.json["topics"]` and returns one of the 8 canonical topics.
- **Listing cards now link to each post's real URL** via `post_url()` instead of a hardcoded
  `/blog/{slug}/`. The LATAM pillar/spoke posts (rendered at `/es/para/...`) no longer 404 from
  category and hub listings. All known dead links cleared.

## [0.0.0.1] - 2026-05-23
### Fixed
- **Cross-language internal linking (GSC cliff fix).** English root `/category/` pages
  no longer list Spanish / India / Arabic posts. The May-7 fix only covered in-post
  links (`get_related`, `inject_internal_links`); `build_category_pages` still bucketed
  all 4 languages together. All listing builders (homepage, category pages, language
  hubs, language topic pages) now classify language consistently via `post_lang()`, so
  the 469 posts with no `language` field route correctly instead of defaulting to English.
  Verified by local build: 0 cross-language links across all 8 English category pages
  (was ~140+), 0 orphaned posts.
- **Language-bucket "categories" removed from the English root.** "GoHighLevel en Español"
  and "GoHighLevel India" no longer generate root `/category/` pages; their old URLs
  301-redirect to `/es/` and `/in/`.
- **Tightened language slug inference.** Dropped the `whatsapp` marker (a feature, not a
  geo signal — it misclassified genuine English posts as India); added `upi` / `razorpay`
  / `mena`.
