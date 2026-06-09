# Changelog

All notable changes to globalhighlevel.com's static-site build are documented here.

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
