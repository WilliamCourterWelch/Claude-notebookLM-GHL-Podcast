# Changelog

All notable changes to globalhighlevel.com's static-site build are documented here.

## [0.3.1.0] - 2026-07-27
### Fixed
- **RTL logo**: the brand's two spans reordered to "HighLevelGlobal" on every Arabic page — the logo anchor now pins `dir="ltr"` (canary catch).
- **Post chrome localized for Spanish and Arabic**: breadcrumb Home → Inicio / الرئيسية, byline, and read-time ("min de lectura" / "دقائق قراءة"); the Spanish vertical template's stray English "Home" is now "Inicio". India English stays English by design.
- **Arabic bodies' in-body /trial CTAs now point at /ar/trial/** (`localize_trial_hrefs()` render pass, JSON untouched) — 3 posts were sending Arabic readers to the English podcast-attribution landing. The larger es (75) / en (17) /trial cohort is a pending policy call, tracked in TODOS.
- Dropped dead `translations.en` pointers from 2 coupon posts (target is a twin 301; pointing at its canonical would have created a non-reciprocal hreflang cluster).
- 2 new tests: logo LTR pin on RTL pages, trial-href localization scope.

## [0.3.0.0] - 2026-07-27
### Added
- **THE 931 RESTORE IS COMPLETE.** Batch 3 (final): 619 pages live again at their original slugs — the long tail plus every previously-held Arabic page. All 931 pruned URLs now resolve: 877 as live pages, 54 as 301s into their clone canonicals. 1,126 affiliate links normalized in this batch alone (2,900+ across the sprint), zero errors, zero collisions across all three batches.
- **Arabic section launched (Bill-approved).** New `/ar/` hub with full right-to-left rendering, Arabic category pages, and a native-Arabic trial landing at `/ar/trial/` — the ~15 Arabic CTAs baked into restored bodies now land on a real conversion page instead of a 404. Copy reviewed native-reader-grade (5 MSA corrections applied); Arabic slug markers added to the language gate so a future mistagged Arabic post fails the build instead of leaking into English hubs.
- **32 more clone twins consolidated as 301s**, including the pair held since batch 1 for its Arabic canonical.
### Fixed (pre-landing review — 5 specialists + Claude/Codex adversarial + red team)
- **False "no credit card" claims corrected at render time** across ~873 restored bodies + meta descriptions (en/es/ar) — rendered pages now state the ~$1 card-verification truth; post JSON stays byte-faithful (D3).
- **5 twin 301s flipped to clean canonicals** (3 EN→India, 1 EN→Arabic, 1 ES→"-1" suffix were inverted vs batch-2 policy); 54/54 twins verified pointing at canonicals.
- **Nav language picker now renders** — every page links all other live languages (was a hardcoded EN/ES toggle; /ar and /in were unreachable from the nav); Guides/CTA labels localized for Arabic.
- **Arabic hreflang made reciprocal** (6 sibling posts in the pricing/trial clusters) and the 2 Arabic money pages got native Arabic titles/meta.
- **hreflang correctness**: root /category/ pages self-reference (was homepage set), trial landings and 404 emit none (noindex surfaces).
- **Gates hardened**: Check 0b (body script must agree with language field, both directions), Check 5d (no redirect chains), Check 5e (no silently shadow-pruned source rules — 304 stale lines cleaned); corrupt post JSON now fails the build loudly.
- llms.txt grouped into labeled per-language sections (Arabic was nearly absent); /ar/trial attribution corrected to `ar-blog` (no Arabic podcast exists).

### Changed
- Site grows 285 → 904 posts; sitemap 923 URLs, all gates green at full scale (language, silo, canon-link, redirect, sitemap-parity, paid-link checks).

## [0.2.13.0] - 2026-07-27
### Added
- **RESTORE BATCH 2 — 136 pages live again at their original slugs.** The tier A/B remainder of the 931, including the two email-deliverability pages that AI assistants kept visiting twice a day while dead (promoted from batch 3 on GA4 evidence). Same doctrine as batch 1: byte-faithful from git history, Bill-approved topics via the override sheet (20 corrections consumed), 396 affiliate links normalized to the fp_ref tag, updatedAt stamped.
- **13 more clone twins consolidated as 301s** to their canonical pages. Running total: 258 of the 931 URLs resolving (258 = 122 + 136 pages) plus 28 twin redirects.
### Fixed
- **The four missing old-taxonomy hub redirects** (analytics-reporting, email-deliverability, sms-messaging, phone-voice) now 301 to their mapped new hubs — closes the GA4-flagged 404s on old category URLs; and the pre-existing agency-platform rule now points at the correct hub per the approved topic mapping (was sites-funnels-reputation).

## [0.2.12.0] - 2026-07-23
### Added
- **RESTORE BATCH 1 — 122 pages live again at their original slugs.** The revenue core of the 931 pruned pages: the AI-cited landings ChatGPT/Copilot link to, the Bing top-5 rankers, and the top-clicked cluster (desktop app, MCP, voice agents, Agent Studio). Restored byte-faithful from git history except: topic stamped per the Bill-approved assignment sheet (147 title-audit corrections applied via per-slug overrides), `updatedAt` set to the deploy date, and every affiliate link normalized to the current `fp_ref` tag — 322 links across 111 posts, including former `app.gohighlevel.com` signup links that paid nobody (Bill-approved rewrite).
- **15 clone twins consolidated as 301s** to their canonical pages (one pair held with the 5 Arabic pages pending the /ar decision). Pre-existing rules that would have shadowed the new redirects (Cloudflare is first-match-wins) were removed.
- **Two new build gates**: verify.py Check 5 now also fails on duplicate redirect sources and on any `/blog/` 301 that lands on a 404; Check 6 requires every sitemap URL to be a built page and never a redirect source.
### Fixed
- **Every affiliate anchor now renders `rel="nofollow sponsored"`** — firehose-era bodies carried followed paid links (Google paid-link policy risk). Render-time pass; stored JSON untouched. Site-wide count of followed affiliate anchors: 0.
- **The sitemap advertised 5 pillar `/blog/` URLs that 301 to their hubs** — excluded now, so IndexNow submissions only carry real pages.
- **The en/en-IN voice-AI dashboard pair shared an identical title with no hreflang** — reciprocal translations maps added so search engines see them as locale variants, not duplicates.
- IndexNow submitter sends a real User-Agent on the POST as well as the preflight; restore report counts how many sheet overrides were consumed.

## [0.2.11.0] - 2026-07-23
### Added
- **Link circle (Caleb canon)** — every blog post now carries a prev/next nav within its language+topic silo, wrapping at the ends so each silo forms one closed loop. Pillars, sink pages, and series/authority pages stay out of circles by construction. This is the canon link structure the 931-post restore lands into.
- **Restore tooling for the 931 pruned posts** (`scripts/restore_posts.py` + tests): checks each post out of git history at its original slug; never overwrites an existing newer page (collision rule); maps the old 8-topic taxonomy onto the current 5 hubs, aborting loudly (with a partial report) on anything unmappable; stamps `updatedAt` to the deploy date while leaving `publishedAt` untouched; writes atomically; exits nonzero if any slug errored so a broken restore can never chain into a deploy. Every affiliate href is normalized to the current `fp_ref` tag — HTML-escaped `&amp;` URLs handled, `utm_campaign` preserved, unrecognized patterns flagged to a report and never guessed.
- **IndexNow recrawl channel** — hosted key file at `/<key>.txt` (spec-validated at build time) plus `scripts/submit_indexnow.py` to push URL batches to Bing per deploy. It verifies the key file is live before submitting and any non-2xx fails loudly.
- **verify.py Check 4 (canon invariants)** on built output: every spoke links up to its hub, circles close exactly as computed, template links never cross language or topic silos, sink pages emit zero outbound internal links. **Check 5:** no `_redirects` rule may shadow a built page.
- 20+ new test functions across five suites (circle edges, series exclusion, anchor-cap edges, nofollow parsing, restore error paths, IndexNow URL handling).
### Changed
- **In-post CTAs point at the money page directly** (`/blog/gohighlevel-free-trial-30-days-extended/`) instead of routing through the retired `/start/` 301 — one less hop, still `rel=nofollow` (TODOS T5 in its D2-superseded form).
- **Contextual link injection is same-silo only** — the cross-topic fallback is gone; in-silo or not at all.
- **Related cards rotate deterministically per post** instead of always picking the first three silo siblings — at 958 posts the old behavior would have concentrated hundreds of card links on three arbitrary pages.
- **3 zero-click snippet rewrites** (payment-providers, sub-accounts, sms-compliance): titles and descriptions rebuilt on the reduce-spam-calls model — concrete benefit up front, a reason to click preserved.
- **Trial-path conversion CTAs get `rel=nofollow` stamped at render time** — localized trial pages are crawlable and firehose bodies repeat one CTA anchor 160×; a followed identical-anchor footprint is the April-cliff fingerprint. The links (and the Spanish funnel) keep working.
- **Anchor caps now apply to anchors baked inside stored post bodies** (`enforce_anchor_caps`, render-time, JSON untouched): beyond 3 identical anchor→URL pairs sitewide the link unwraps to plain text. Covers absolute same-site URLs, authority-page bodies, and counts against post-rewrite pillar hub URLs.
### Fixed
- **158 restore-target URLs were shadowed by prune-era `_redirects` rules** — on Cloudflare Pages a redirect always beats a static file, so restored pages would have been live-unreachable while being submitted to Bing. The build now prunes any rule whose source is a built page or deployed file (318 rules at full scale, sources printed) and Check 5 gates it. The two inverted precedence comments (TODOS T8) are corrected.
- **The money page (sink) was still growing outbound links** — related cards and the followed category-eyebrow link are now suppressed on sink pages.
- **Dead-link gates were blind to absolute same-site URLs** (`https://globalhighlevel.com/...`) — verify.py and audit_links.py now normalize and check them (this immediately surfaced the dead `/ar/trial/` CTAs in the Arabic restore set).
- **audit_links doctrine** (TODOS T6): retired `/start`+`/coupon` no longer exempt; nofollow links exempt from anchor doctrine by rel attribute; exemption prefixes imported from build.py (single source of truth) and matched on path-segment boundaries so `/trial-anything` can't hide behind `/trial`.

## [0.2.10.1] - 2026-07-22
### Fixed
- **Search engines can finally see the money-page redirects.** Removed `Disallow: /start/` and `Disallow: /coupon/` from robots.txt — both URLs were retired in April and 301 to the trial money page, but the robots block meant crawlers could never fetch them to discover the redirect. This recovers **external** backlink equity pointing at those URLs (podcast/social-era links) and makes the 301s visible; the 33 internal `/start/` CTA links are all `rel=nofollow` and pass nothing either way — their equity is recovered by the Ship 2 anchor repoint (TODOS T5, stays P0). Only `/trial/` (a real attribution page) stays blocked. `/coupon/` inclusion was Bill's call 2026-07-22.
- **Blog-post structured data now reports real modification dates.** Article JSON-LD `dateModified` prefers `updatedAt` (falling back to `publishedAt`), matching what category pillars already did — previously every blog post claimed it was never modified since publish.
### Changed
- **Money-page title + meta description rewritten** — title field 50 chars ("GoHighLevel 30-Day Free Trial & Promo Codes (2026)", was 78; renders 70 with the " | Global High Level" suffix, so the keyword payload now fits the ~60-char visible budget and only the brand suffix truncates — was losing keywords at 98 rendered), description 152 chars (was 214 and truncating mid-word). Body untouched. `updatedAt` bumped so sitemap lastmod signals the edit.
- **CLAUDE.md attribution-URL doctrine updated**: `/start/` and `/coupon/` marked RETIRED with do-not-reblock notes; unblock prohibition now covers only `/trial/`.

## [0.2.10.0] - 2026-07-16
### Changed
- **HIPAA spoke affiliate section** now states commissionability as confirmed — HighLevel runs a dedicated HIPAA campaign in the affiliate portal (verified first-hand in the owner's affiliate dashboard). Adds the insider caveat from the campaign's own instructions: it's a pop-up promotion active only a few times per year; confirm it's live in the HighLevel Affiliate Community and use the approved campaign link. The $118.80/mo figure is pinned to its source ("under the agreement's 40% add-on rate").

## [0.2.9.0] - 2026-07-16
### Added
- **HIPAA compliance add-on spoke** under the Payments & Pricing silo. `gohighlevel-hipaa-compliance` answers the branded PAA cluster (is GHL HIPAA compliant / how much does it cost / how to enable): the $297/mo ($2,970/yr) add-on and what it includes (BAA, ePHI encryption, audit logging, enforced MFA — all vendor-attributed), the non-cancellation catch, per-plan combined cost table, who actually needs it (with the covered-entity caveat), the community price debate (51-vote ideas-board thread, linked + hedged), a BAA-before-real-patient-data warning at every CTA (dummy-data phrasing at the first), and an honestly-hedged affiliate-commission section (HIPAA is not named in the affiliate agreement — readers told to confirm in writing). Research vault + codex/claude third-voice passes in the globalhighlevel-system repo.
### Changed
- **Pricing guide** gains a hub-down link to the HIPAA spoke at the end of Hidden Costs, plus an `updatedAt` (2026-07-16) so sitemap lastmod reflects the edit (blog-post Article dateModified still derives from publishedAt in build.py — only category-pillar pages read updatedAt).

## [0.2.8.0] - 2026-07-07
### Added
- **SaaS-mode setup spoke** under the agency pillar. `gohighlevel-saas-mode-setup-agency-guide` is a focused first-hand how-to: the plan tier that exposes SaaS Mode (Agency Pro + Enterprise, hedged/attributed), where the SaaS Configurator lives, building a plan on the Plans & pricing tab (monthly/annual price, feature toggles, trial + complimentary credits, Copy sale link), connecting Stripe, switching SaaS on per sub-account (incl. bulk activation + payment-method caveat), and the Cancellation/Downgrade/Security/Automatic Tax tabs worth configuring early. A real screenshot of the SaaS Configurator → Plans & pricing tab (`saas-configurator.png`). Targets the "how to set up saas mode in ghl" PAA long-tail — deliberately not the pillar's "saas mode / white-label" head terms.
### For contributors
- Caleb silo: first in-body link points UP to the pillar (`/category/agency-white-label-saas/`), with sibling links to the reselling, sub-accounts/snapshots, and white-label-setup spokes plus the pricing blog. 1 first-hand screenshot (`saas-configurator.png`, owner-attested 2026-07-07). Codex fact-check applied: 8 findings, hedged 6 P1/P2s (SaaS gated to Agency Pro AND Enterprise not Pro-only; Stripe requirement softened to in-account observation; Automatic Tax + cancellation-behavior wording softened to what the screenshot/sources support). build.py link-hygiene + verify.py gates green (0 orphans, 0 dead links). Deploy-gate: gbrain `globalhighlevel-seo-changelog` timeline logged.

## [0.2.7.0] - 2026-07-07
### Added
- **Reselling & rebilling spoke** under the agency pillar. `gohighlevel-reselling-rebilling-agency-guide` is a focused first-hand guide: the reselling-vs-rebilling distinction, which plan unlocks markup (Unlimited rebills at cost, Agency Pro rebills with markup + full SaaS reselling), a real screenshot of the Reselling → Core Services screen (markup slider + Your Price/HighLevel Price/Your Profit margin builder), reselling usage-based marketplace apps (percentage vs fixed markup), letting clients self-cancel add-ons, and an "is reselling GoHighLevel legit?" answer. Targets the reselling/rebilling long-tail + reseller PAA — deliberately not the pillar's white-label/saas-mode head terms.
### For contributors
- Caleb silo: first in-body link points UP to the pillar (`/category/agency-white-label-saas/`), with sibling links to the sub-accounts/snapshots and white-label-setup spokes plus the pricing blog. 1 first-hand screenshot (`reselling.png`, owner-attested 2026-07-06). Codex fact-check applied: fixed 2 P1s (a core-services resale panel mislabeled as "rebilling"; imprecise screenshot numbers) plus pricing/definition hedges. build.py link-hygiene + Clarity gates green. Deploy-gate: gbrain `globalhighlevel-seo-changelog` timeline logged.

## [0.2.6.0] - 2026-07-07
### Added
- **White-label setup spoke** under the agency pillar. `gohighlevel-white-label-setup-agency-guide` is a focused how-to: the logo, the custom login domain (CNAME-before-domain, the step people get stuck on), branded system emails + shared templates, controlling GoHighLevel's in-app banners, and the white-label mobile app (hedged as a higher-tier/paid add-on). First-hand with 1 real screenshot from a live Agency Pro account.
### For contributors
- Caleb silo: the spoke's first in-body link points UP to the pillar (`/category/agency-white-label-saas/`), plus a sibling link to the sub-accounts/snapshots spoke. Codex fact-check clean (hedged absolute "never sees GoHighLevel" claims). Builds green. Deploy-gate: gbrain `globalhighlevel-seo-changelog` logged.

## [0.2.5.0] - 2026-07-07
### Added
- **First-hand screenshots on the Agency, White-Label & SaaS silo.** The pillar (`/category/agency-white-label-saas/`) now carries **5 real, PII-redacted screenshots** from a live GoHighLevel Agency Pro account — the SaaS Configurator, Sub-Accounts, Account Snapshots, Reselling, and Whitelabel settings — plus first-hand operator notes (e.g. the CNAME-must-resolve-first white-label gotcha). The sub-accounts/snapshots spoke gains 2 of those screenshots. This adds the real-usage / EEAT signal (screenshots + first-person experience) the pages lacked — the documented recovery lever for the site's thin-content demotion. Redaction is solid-bar (unrecoverable) and owner-attested; no client names, domains, or IDs published.
### Changed
- **Hub-pillar category pages now emit Article + FAQPage structured data.** The category-as-pillar rendering previously carried only `WebSite` schema; it now emits an `Article` (author, published/modified dates) and a `FAQPage` that mirrors the visible body Q&A, matching the blog-post template. Applies to every content-rich hub, so all pillars gain rich-result eligibility. build.py `build_category_pages` (isPillar branch only; non-pillar categories unchanged).
### For contributors
- Screenshots captured via /ghl-capture using in-app click navigation (GHL's SPA logs out on cold `goto`); solid-bar PII redaction verified image-by-image. Content fact-checked (Codex DONE + Claude adversarial, all pricing/tier/gating confirmed); the build.py schema change codex-reviewed (empty-date omission fix applied). Pre-existing `test_ghl_capture.py` `root`-fixture errors are unrelated to this branch. Deploy-gate: gbrain `globalhighlevel-seo-changelog` timeline logged.

## [0.2.4.0] - 2026-07-03
### Added
- **CRM & Communication hub pillar + spoke rewire.** `gohighlevel-crm-communication-complete-guide` (~1,480w) covers the CRM, unified inbox, two-way SMS (with A2P 10DLC), email deliverability, LC Phone, and calendars. Built via /research-product-wedge from the 148-page killed CRM corpus, fact-checked (Codex DONE + Claude adversarial SHIP). The two existing CRM spokes (spam-calls, unsolicited-SMS) rewired so their first in-body link points up to the pillar. 4 of 5 EN hubs now have a pillar (Sites remaining).
- **Agency, White-Label & SaaS hub — pillar + first spoke** (the hub was English-empty; v0.2.3.0 had dropped its homepage card for that reason). `gohighlevel-saas-mode-white-label-agency-guide` (~1,580w pillar) explains SaaS Mode, the Agency Pro $497 plan that unlocks it, sub-accounts, snapshots, rebilling, reselling, and white-labeling. `gohighlevel-sub-accounts-snapshots-agency-guide` (~965w spoke) covers sub-accounts + snapshots. Built via `/research-product-wedge` from the killed firehose corpus (67 EN agency pages) and fact-checked (Codex 3-pass DONE + Claude adversarial). Corrects the source drafts' fabricated per-seat fee model; states the real cost (flat $497 + usage, unlimited sub-accounts), billing rails (Stripe/NMI/Authorize.net/Square), no-certification reselling, white-label app as a separate ~$497 add-on, and the 30-day trial as a promo (14-day standard). Caleb linking: pillar<->spoke reciprocal, first in-body link is the trial CTA (not Spotify), in-silo only.
### Changed
### Added
- **Sites, Funnels & Reputation hub pillar (the 5th and final hub).** `gohighlevel-sites-funnels-reputation-complete-guide` (~1,270w) covers the website/funnel builder + e-commerce, forms vs surveys, reputation management (Google+Facebook, Reviews AI usage add-on), and business listings (Yext OR Uberall, a paid ~$30/mo add-on). Built from the 86-page killed Sites corpus, fact-checked (Claude adversarial; codex was unavailable mid-session — binary removed by a concurrent brew op). Corrects the outdated "Listings = Yext" claim (now Yext-or-Uberall, agency choice) and flags Listings + Reviews AI as paid add-ons. The 2 Sites spokes rewired to the hub. **All 5 hubs now content-rich.**
### Changed
- **Hub pages now render the pillar content itself.** `/category/{topic}/` shows the full pillar article + the spoke list below it (was a thin card-list). Each pillar now has ONE URL (its hub); the old `/blog/{pillar}/` URL is **not built** and **301-redirects** to the hub, and every internal link is auto-repointed to it (no duplicate content). build.py `build_category_pages` + post canonical; audit_links.py thin-hub gate now treats a pillar-backed hub as content-rich.
- **Restored the Agency homepage hub card** (build.py) now that `/category/agency-white-label-saas/` has >= 2 EN posts and builds. Homepage now shows all 5 hubs.
### For contributors
- Step 0 DataForSEO + Step 0.5 GSC (anti-cannibalization: TARGET, no incumbent) run; claim-ledger gated; /review clean (Codex adversarial: approve). 66 more agency drafts remain in the reuse corpus for slow drip. Prior deploy-gate: gbrain `globalhighlevel-seo-changelog` timeline logged.

## [0.2.3.0] - 2026-07-02
### Changed
- **Reconciled the taxonomy: 8 category topics -> 5 hubs, aligned to the homepage.** The homepage hub cards and `categories.json` topics were two different taxonomies that didn't line up (cards pointed at colliding/placeholder categories). Collapsed to one 5-topic set: **AI Receptionist & Lead Capture** (was AI & Automation + Phone & Voice - AI agents/automation are now spokes under the searched "receptionist/lead capture" head term), **CRM & Communication** (+ Email + SMS), **Sites, Funnels & Reputation** (new), **Agency, White-Label & SaaS** (+ Analytics), **Payments & Pricing**. Re-filed 9 posts. Homepage cards 6 -> 4 (merged the two AI cards; dropped the empty-EN Agency card), each now points at its own distinct category page (no more shared/placeholder targets). ES homepage cards trimmed to the 3 with real ES content and repointed off the dead slug.
- **Fixed the mis-filed Sites posts** (`launch-website`, `uberall`) - moved out of Agency into the new Sites/Funnels/Reputation hub.
### Fixed
- 301 redirects for the renamed category slugs (`/category/ai-automation/` -> `ai-receptionist-lead-capture`, `/category/agency-platform/` -> `sites-funnels-reputation`, ES equivalent) so old URLs don't 404.
### For contributors
- Known follow-up: the hub/category landing pages are auto-generated LISTS, not pillar articles. Next: write real pillar content for CRM, Sites, and AI Receptionist hubs (see TODOs). build.py + verify.py + tests green; /review (Codex) run.

## [0.2.2.0] - 2026-07-02
### Added
- **Two hub pillar pages** (the site had zero real pillars before). `gohighlevel-ai-agents-automation-complete-guide` explains the three automation layers (Workflows / Conversation AI / Agent Studio); `gohighlevel-payments-complete-guide` covers accepting payments in GHL (Stripe/PayPal/NMI/Authorize.net/Square native, MercadoPago regional) and is aimed to NOT cannibalize the ranking pricing page. Homepage + footer cluster cards repointed to both. Both PAA-grounded (DataForSEO) and fact-checked by Codex + a Claude adversarial pass (18 factual fixes, incl. Conversation AI is metered not free on Starter).
- **Homepage Organization JSON-LD** (logo + sameAs Spotify) on `/` only; **favicon** `<link>` site-wide.
### Changed
- **Caleb-canon internal linking.** Silo integrity (re-filed the two automation posts into the AI & Automation topic; `get_related` no longer pads thin silos with other-topic posts — kills cross-silo related cards); spoke link-circles added; each spoke's FIRST in-content link now points up to its pillar; breadcrumb Home/category crumbs de-followed site-wide (BreadcrumbList JSON-LD kept); the 6 homepage hub cards now use unique descriptive anchors instead of 6× "Explore guides".
- **Money-page FAQ 17 -> 12** (dropped the discount keyword-variant doorway cluster).
- **Homepage title 85 -> 55 chars, meta description 116 -> 158 chars** (Caleb on-page limits).
### Fixed
- **verify.py** now resolves internal hrefs that map to a real file on disk (static assets like the favicon), with a `..`-traversal guard + public/-containment check (caught by Codex/Claude review). Fixed one mislabeled post category. Removed 4 dead pipeline scripts (classify-posts, migrate_lang_topic, design-homepage, design-log).
### For contributors
- Build stays `python3 build.py`; `verify.py` + `test_audit_links` + `test_build_links` + `test_ghl_capture` all green. Ran `/review` (Codex + Claude adversarial, 1 finding fixed) before ship. gbrain SEO changelog is the deploy-gate log of record (seo-cooldown.json retired).

## [0.2.1.0] - 2026-06-26
### Fixed
- **Sitemap `lastmod` now stamped on every URL (was 17/27).** The relaunched homepages and category hubs (`/`, `/es/`, `/in/`, all categories) had no `lastmod` at all, and the money page reported its April publish date despite being rebuilt today — so the sitemap was telling Google the relaunch never happened. Derived index/hub pages now stamp the build date; posts prefer an explicit `updatedAt` over `publishedAt`. The money page gained `updatedAt: 2026-06-26`. This is the freshness signal that gets the relaunch re-crawled.
- **robots.txt now `Disallow`s the attribution paths** (`/trial/`, `/coupon/`, `/start/`) for normal crawlers, per the long-standing attribution-clean policy in `globalhighlevel-site/CLAUDE.md`. The AI-crawler groups (GPTBot/ClaudeBot/Google-Extended/PerplexityBot/anthropic-ai) keep `Allow: /` and can still crawl them.
- **llms.txt tutorial count is now dynamic** (`{len(posts)}` = the real built count) instead of a stale hardcoded "80+".
### Added
- **Sitemap-level hreflang alternates** (`<xhtml:link rel="alternate">`) via new `_sitemap_alts`/`_sitemap_post_alts` helpers — the `xhtml` namespace was declared but unused. Now the `/` ↔ `/es/` ↔ `/in/` cluster, both EN↔ES category pairs, and the EN↔ES pricing-post pair carry reciprocal alternates + `x-default`. Page-level hreflang was already correct; this is the recommended sitemap-level complement for international/GEO. Pruned siblings and single-variant pages are correctly excluded.
- **XML-attribute/element escaping** on all sitemap `<loc>` and `href` values (`_xml_attr`/`_sitemap_loc`) so a future `SITE_URL`/slug containing `&`/`"`/`<` can't invalidate the sitemap (defensive; caught by Codex adversarial review).
### For contributors
- Build stays `python3 build.py`; sitemap output validated with `xml.etree` (27/27 lastmod, 30 reciprocal hreflang nodes, well-formed). `verify.py` + the link-audit test suites all green.

## [0.2.0.0] - 2026-06-25
### Added
- **English brand-hub homepage.** The `/` homepage is now an "Everything GoHighLevel" brand hub: a single primary guide card to the 30-day free-trial money page, 6 topic-cluster cards (links-safe — one descriptive anchor per cluster URL), and a Spanish banner to `/es/`. Replaces the old post-firehose index that diluted authority across every URL.
- **Spanish brand-hub homepage at `/es/`.** Mirror build for `lang=='es'` ("Todo sobre GoHighLevel"): primary card to the precios money page, 6 Spanish cluster cards, English banner back to `/`.
- **Complete structured data for SEO + LLM citation.** Article schema gains `image`, `inLanguage`, and `speakable` (`.post-title`, `.tldr`); `BreadcrumbList`, `WebSite`, and a fixed `logo` (512x512). Added `og-default.png` (1200x630) and a branded `logo.png`. Money-page TL;DR answer box + bootcamp CTA panel.
### Changed
- **Relabeled the taxonomy into cluster categories** (Payments & Pricing, CRM & Communication, Agency & Platform) so every live topic forms a 2+ post hub that lists and links its spokes — 0 orphans (`verify.py`: 17/17 listed). Renamed category slugs 301-redirect from the old paths.
- **Consolidated the money-page discount FAQ cluster (10 -> 5).** Merged the promo/discount/coupon-code synonym trio into one Q&A and dropped near-duplicate "best deal"/"how do I get a discount"/"summer promo" variants, keeping the genuinely distinct intents (annual billing, student/nonprofit, Black Friday, affiliate). Removes the keyword-variant doorway pattern that matches the April quality-demotion fingerprint; FAQPage schema drops to 17 honest Q&As. Summer-of-AI affiliate link preserved inside the Black Friday answer.
- **Adopted the homepage nav site-wide, language-aware.** `Guías` -> `/es/#guides` on Spanish pages, `Guides` -> `/#guides` on English. Money pages strip unqualified outbound links (`mvp_minimal_links`) and `nofollow` the robots-blocked `/start/` CTA so no editorial juice leaks to it.
### Fixed
- **5 critical pre-ship fixes** (caught by `/review` — Claude adversarial subagent + Codex structured review): (1) narrowed the duplicate-TOC sanitizer regex to require a `#anchor` so it stops deleting real callout content ("30-Day Game Plan", "Timing Tip") and the ES affiliate CTAs; (2) Spanish nav `Guías` was pointing at the English `/#guides` — now `/es/#guides`; (3) `BreadcrumbList` JSON-LD was emitting category URLs that 404 for single-post topics — gated to built hubs; (4) `razorpay-india` left on a stale category label; (5) renamed category slugs had no 301.
### For contributors
- Build stays a single `python3 build.py` (Cloudflare Pages on push to main); `verify.py` is the structural gate (language/slug agreement, English-only root categories, 0 orphans, 0 dead links). Both green on this release.

## [0.1.0.28] - 2026-06-22
### Fixed
- **Killed the internal-anchor spam pattern that matches the April quality-demotion fingerprint.** The "Keep Reading" related cards wrapped the category tag and the post title in one link, so Google saw the same ~60-character anchor ("Agency & Platform GoHighLevel Pricing 2026...") repeated 8x sitewide pointing at the money pages. Related cards now link the title only (category is plain text), the in-article link injector emits multi-word descriptive anchors only (no bare "GoHighLevel"/"pricing"/"payments" single-word anchors), and a sitewide cap stops any one anchor->URL pair from repeating more than 3x.

### Changed
- **Stopped building thin 1-post category pages.** Category hubs now require 2+ posts (the rule the language hubs already used), so a single-post "category" no longer renders as a near-empty page with one card and a wall of blank space. Those posts fall back to a plain-text breadcrumb; nav, footer, sidebar, and cards drop the now-dead links automatically. Each post also gains one editorial in-body link up to its category hub (varied anchor, capped).

### For contributors
- New **`scripts/audit_links.py`** link-hygiene gate, wired into `build.py` as a blocking build step (Cloudflare runs build.py, so a violation aborts the deploy). It fails the build on anchor cliffs, single-word/bare-brand editorial anchors, thin hubs, and internal 404s, and reports per-post editorial inbound counts (near-orphan curation signal). The HTML parser uses an element stack so unbalanced post markup can't desync it (fail-closed, not fail-open). Stdlib tests: `scripts/test_audit_links.py` + `scripts/test_build_links.py` (`python3 scripts/test_*.py`). Anchor/hub changes went through `/plan-eng-review` + Codex outside voice + a 3-pass `/review` (caught the dead-wired gate and a fail-open parser before merge).

## [0.1.0.27] - 2026-06-22
### Added
- **First real product screenshot on the LATAM agencies hub.** `/blog/gohighlevel-latam-pagos-agencias/` now shows a genuine capture of GoHighLevel's **Integraciones de pagos** screen (Spanish interface, native providers like Stripe/PayPal/Authorize.net) right where the page explains the Flujo B payment stack — first-hand visual proof instead of a text-only claim. This is the first page taken to the real-screenshot EEAT bar the site needs to climb out of the April-2026 quality demotion. Also removed a stale duplicate image (`ghl-payment-integrations-es.png`) that was sitting unused.

### For contributors
- New **`/ghl-capture`** tooling (`globalhighlevel-site/scripts/ghl_capture*.py` + `.claude/skills/ghl-capture/`): captures real GHL sandbox screenshots through the GStack Browser, records a provenance manifest with **human PII attestation** (never auto-claimed), Pillow-optimizes, wires `<figure>` markup into a post's `html_content`, and gates on a per-language orphan check. Designed via `/office-hours` (Codex cold-read + 2-round adversarial spec review) and hardened against path-traversal and fail-open gates per a 3-model `/review`. 9 test groups, all green.

## [0.1.0.26] - 2026-06-22
### Fixed
- **4 post-review quality fixes** (caught by a `/codex` review of the prior unreviewed ships): (1) un-escaped the LATAM hub's "Guías por país" spoke links — they were rendering as literal `&lt;a href&gt;` text instead of clickable links; (2) converted leaked Markdown pipe-tables + a code fence in the Mexico spoke into real `<table>`/`<code>` HTML; (3) replaced a forbidden `gohighlevel.com/pricing` link (no `fp_ref`) with the internal precios page; (4) removed a "clientes en Latinoamérica" bio overclaim on Mexico/Opiniones to match the honest "does not operate in LATAM" framing used on the hub. Also: codified a citation-exception to the affiliate-link rule (doc/forum/blog citations are exempt from `fp_ref`) and fixed the assembler's bio template. Re-reviewed via `/codex` (PASS, no findings).

## [0.1.0.25] - 2026-06-22
### Added
- **FAQPage JSON-LD schema, site-wide and automatic.** `build.py` now auto-generates `FAQPage` structured data from any post's "Preguntas frecuentes"/FAQ section (handles both `<h3>` and bold-paragraph question formats; scopes to the FAQ section so non-FAQ headings aren't captured; skips if a post already embeds its own FAQ schema, to avoid duplicates). This is the structured data that makes FAQs eligible for search rich-results and that LLMs (ChatGPT/Perplexity) cite — the pages had visible FAQs but zero schema before. Now live on Opiniones (4 Q), Mexico (5), the LATAM hub (6), qué-es (5), and precios (9).
- **Pricing-PAA FAQs on the precios page.** Added the top pricing People-Also-Ask questions as explicit Q&As — ¿Cuánto cuesta GoHighLevel al mes? / ¿GoHighLevel tiene prueba gratis? / ¿Cuál es el plan más barato? — grounded in the page's own plan data ($97/$297/$497 + 30-day trial). Replaced the stale embedded FAQ schema so the regenerated FAQPage includes them. (The qué-es page's FAQs were already PAA-aligned — they just gained schema.)

## [0.1.0.24] - 2026-06-22
### Fixed
- **Redirect-rescue of high-impression deleted qué-es pages.** Four deleted pages that still had GSC impressions (`guia-completa-…-que-es-ghl-esencial-agencia` ~411 impr, `…que-es-como-usar` ~312, `que-es-gohighlevel-guia-completa-agencias-2026` ~174, `…ghl-plataforma-automatizacion…` ~71) were hard 404s — now 301 to the live qué-es canonical, recovering their ranking value instead of dropping it.
- **Fixed an intent-mismatch redirect.** `que-es-gohighlevel-plataforma-automatizacion-agencias-latinoamerica` (a "what is" page, ~224 impr) was 301'ing to an automation *tutorial*; repointed to the qué-es canonical.
### Changed
- **Normalized the author field to William Welch on all 14 remaining posts** (were "Global High Level" placeholder or empty). The visible author box already rendered William Welch site-wide; this makes the post metadata consistent.

## [0.1.0.23] - 2026-06-22
### Changed
- **Upgraded the LATAM payments page into a proper hub, in place.** `/blog/gohighlevel-latam-pagos-agencias/` went from 907 words (placeholder "Global High Level" author) to ~1,830 words with: the real **William Welch** byline, a **country-comparison table** (Stripe-for-SaaS vs MercadoPago-for-Flujo-B per country), an honest Flujo A / Flujo B framing, the real Mercado Pago Spanish-UI screenshot, a sourced citations list, FAQ, and hub-and-spoke internal links down to the Mexico spoke + Opiniones + precios + qué-es. Done as an in-place upgrade (no new URL, no 301) so it absorbs the topic without cannibalization and keeps existing inbound links valid. Content assembled from the codex-vetted LATAM hub draft in the research vault. Logged to SEO Changelog Tracker.

## [0.1.0.22] - 2026-06-22
### Fixed
- **Broken internal link on the Mexico spoke.** The "Parte de la guía" link pointed at `/blog/gohighlevel-latam-guia-pagos-agencias/` (a planned hub slug that isn't built) → 404. Repointed to the existing `/blog/gohighlevel-latam-pagos-agencias/`. Caught by the internal-linking eval.

## [0.1.0.21] - 2026-06-22
### Added
- **New Spanish review pillar: `/blog/gohighlevel-opiniones-es-confiable-vale-la-pena/` — "GoHighLevel Opiniones 2026: ¿Es Confiable y Vale la Pena? Reseña Honesta."** Honest-review angle targeting the validated trust/comparison PAA cluster (¿es confiable? / ¿vale la pena? / alternativas), which GSC confirmed no existing page ranks for (no cannibalization). ~1,600 words with genuine material cons (learning curve, module depth, A2P/SMS setup friction, English UI corners, per-country payment gaps), a "para quién NO vale la pena" section, first-hand observations from configuring MercadoPago in a sandbox, three translated quotes from real LATAM agency owners (linked to GoHighLevel's ideas forum), and honest "when I'd choose the competitor instead" comparisons (HubSpot/Clientify/Kartra). Real byline (William Welch), prominent affiliate disclosure (top + at CTA), reuses the Spanish payments-UI screenshot. Hub-and-spoke: internal-links to qué-es, precios, pagos, and the Mexico spoke. Passed cross-model review (Codex) on the blocking items; residual citation-strictness flags judged beyond a consumer-review-page standard. Logged to SEO Changelog Tracker.

## [0.1.0.20] - 2026-06-22
### Added
- **New Spanish pillar: `/blog/gohighlevel-mercadopago-mexico/` — "GoHighLevel + Mercado Pago en México: la guía completa para agencias (2026)."** First page built to the post-demotion quality bar: real author byline (William Welch), honest "limitations" section, 5-question FAQ, affiliate CTA with `fp_ref`, and **two first-hand screenshots of the actual GoHighLevel Spanish UI** (the Mercado Pago provider card showing native LATAM availability, and the Mercado Pago configuration screen — clave pública / token / país / webhook) captured live from a sandbox sub-account. ~6,000 words, assembled from the LATAM research vault (38 sources + 8 prior Codex critiques). Logged to the SEO Changelog Tracker sheet. Shipped as a single pilot (not a batch) per cross-model review, since the domain is under an April-2026 algorithmic quality demotion and new content only helps if it changes the quality profile.
- **Image pipeline in `build.py`.** Added `shutil.copytree(images/ → public/images/)` after the `public/` clean, so tracked source images in `images/` are served. The site previously had **no image-serving mechanism** — every page was text-only, which is one reason it read as thin affiliate content. Images referenced as `/images/...`.
- **`assemble_spoke.py`** — reusable assembler that converts research-vault section drafts (markdown + editorial commentary) into a clean post JSON: strips frontmatter/commentary/image-refs, converts markdown→HTML, wires the affiliate CTA, appends a sourced EEAT author bio. Reusable for the LATAM hub + future spokes.

## [0.1.0.19] - 2026-06-14
### Removed
- **Deleted the `/12-month-plan/` page (stale dead-pipeline operating plan that also exposed internal business strategy).** The page was a public "12-month operating plan" that (a) described the now-deleted 25-hour pipeline as live and present-tense ("Trades Pipeline **Live**… **producing 20 episodes per day**… trades pipeline **shipping** a 9-part series across three languages… Derivative blog posts published in all three languages") — all false after the pipeline's retirement (0.1.0.15) — and (b) published REI Amplifi internal financials/strategy on a GoHighLevel affiliate site: the $7,500/mo client floor, ice-machine unit economics (93% gross margin, ~$1,500 net/machine/mo, 150-machine → ~$2.7M EBITDA target across TX/FL/CA), and licensing-deal plans. It was an orphan (not in the sitemap, robots, nav, or any internal link — reachable only via a direct/Facebook link, which GA4 showed getting a trickle). Removed `build_12_month_plan_page()` and its call from `build.py`, and added `/12-month-plan` + `/12-month-plan/` → `/` 301s in `_redirects` (Cloudflare serves the redirect now that no static file is generated). Verified: the page no longer builds, and zero "EBITDA / bass fishing / 93 percent gross" text remains anywhere in the build output.
### Fixed
- **Corrected one stale cadence claim on `/about/`.** The bio's content bullet said *"New content daily — tutorials, podcast episodes, and guides published every cycle"* — false now that the daily pipeline is dead. Reframed to *"Built from real work — tutorials, podcast episodes, and guides from hands-on GoHighLevel implementation, not theory"* (evergreen, accurate, and on-brand with the page's existing "real implementation work, not theory" framing). The rest of `/about/` (consultant bio, "15+ published tutorials") is accurate and unchanged. Verified: build + `verify.py` (0 dead links), stale line gone / new line present in built `/about/`.

## [0.1.0.18] - 2026-06-14
### Fixed
- **Corrected the false "PayU is native" claim on the `/in/trial/` page.** The India trial attribution page (hardcoded in `build.py`) had an FAQ — *"Does it work with Razorpay and WhatsApp Business API?"* — answered *"Yes. GoHighLevel supports Razorpay, PayU, and WhatsApp Business API natively…"* PayU is **not** a native GoHighLevel integration (it needs a custom build); Razorpay and the WhatsApp Business API **are** native. Same inaccuracy we already fixed in the India blog post (0.1.0.14) and the ES `que-es` page (0.1.0.9), but it persisted on the parallel trial page. The question only asks about Razorpay + WhatsApp (both genuinely native), so dropped the false PayU mention: now *"Yes. GoHighLevel supports Razorpay and WhatsApp Business API natively — no third-party integration headaches."* The other Razorpay/WhatsApp/UPI "native" mentions on the page (subheadline, value props) are accurate and unchanged. Verified the corrected framing already lives in both posts (`que-es`: "Conekta o PayU se conectan vía integración personalizada… no de forma nativa"; India blog: "PayU is not a native integration… custom build"). Verified: build + `verify.py` (0 dead links), 0 PayU in built `/in/trial/`.

## [0.1.0.17] - 2026-06-14
### Removed
- **Killed Arabic (`/ar/`) as a supported language, for good.** The Arabic content stream never had live posts (the `/ar/` hub already 404'd, and the Arabic blog generator died with the pipeline in 0.1.0.15), but vestigial Arabic config was still shipping one live page and dead metadata. Removed it everywhere: the `ar` entry in `categories.json` `languages` (which drives the language picker, `hreflang` alternates, sitemap hubs, and `dir="rtl"`); the hardcoded Arabic trial-page dict in `build.py` (this was still building a live `/ar/trial/` — now 404); the `("ar", …)` slug-language detection markers; the Arabic `hub_descriptions` entry; and the dead `translations.ar` keys in the 3 posts that carried them (free-trial, ES pricing, EN pricing — all pointed at a non-existent `…-arabic-…` slug that `build.py` already gated out of `hreflang`). Removed the `/ar/start` redirect lines from `_redirects`. Corrected the live `/about/` + `/12-month-plan/` operating-plan prose that claimed the site publishes in "four languages (Spanish, Arabic, Indian English, English)" / "ranking in four languages" — now **three languages (Spanish, Indian English, English)**, and dropped the "Spanish and Arabic ranked fastest" line to "Spanish ranked fastest." **No live content lost** (zero Arabic posts, zero Arabic podcast episodes). The other three languages are untouched: rebuild produces the es + in hubs, their trial pages, and all 15 blog posts; the language picker now lists only English / Español / India; `verify.py` PASS (0 dead links, 0 orphans); sitemap carries no `/ar/` URLs. Generic RTL CSS plumbing is left in `build.py` (inert — no `dir="rtl"` language remains — and harmless). Note for a separate cleanup: `/about/` + `/12-month-plan/` still describe the now-deleted 25-hour pipeline in the present tense ("shipping… producing 20 episodes per day").

## [0.1.0.16] - 2026-06-12
### Added
- **301-redirect map for the dead pipeline-era blog URLs (codex + Bill reviewed).** GSC + GA4 show 233 deleted `/blog/` URLs (the auto-pipeline's culled posts, logged `prune_404` on 2026-06-03) still pulling organic + AI-assistant clicks into 404s during the post-cliff recovery. Mapped each to the closest live page by topic + language and added **155 topical 301s** to `_redirects` (the remaining 78 are English feature how-tos with no live equivalent — intentionally **left to 404** rather than dumped on the homepage, per codex's soft-404 guidance and Bill's call; a 404 reaches the same de-index end-state as a 410 with zero code, and Cloudflare's `_redirects` can't emit a 410 anyway). Destinations (all verified HTTP 200): ES automation pillar (70), ES LATAM payments (17), ES `qué-es`/alternatives pillar (8), ES pricing (1), `/es/` hub (17), `/in/` hub (26), India WhatsApp (3), India Razorpay/UPI (2), EN master-payment-providers (5), EN unsolicited-SMS compliance (3), EN reduce-spam-calls IVR (2), EN free-trial (1 ES discount slug).
### Fixed
- **Repointed broken existing redirects that 301'd to now-deleted (404) targets.** Found while building the map: the live `_redirects` had redirect→404 chains. `/es/start`, `/in/start`, `/ar/start` pointed at three deleted trial-blog slugs (`gohighlevel-prueba-gratis-…`, `…free-trial-india-…`, `…free-trial-arabic-…`, all 404); repointed to the ES pricing pillar, the `/in/` hub, and `/` respectively (note: the whole `/ar/` hub is itself 404 — Arabic content is gone). All 14 `gohighlevel-vs-*` lines pointed at `gohighlevel-vs-competidores-locales-domina-espana-america-latina` (404); repointed to the live ES alternatives pillar (`que-es-…-mejor-alternativa-…`). Also `/es/mercadopago-gohighlevel/` (404, had real clicks) → ES LATAM payments. codex review (gpt-5.5, high reasoning): no blockers; structural checks pass (no duplicate sources, no loops/chains, every destination 200). Verified: `build.py` copies `_redirects` → `public/` (byte-match), `verify.py` PASS (0 dead links, 0 orphans, 15/15 posts listed). Deploy gate: SEO Changelog Sheet row 986. (The 15 live posts keep static files, which take precedence over `_redirects`, so none of them can be shadowed by a redirect.)

## [0.1.0.15] - 2026-06-11
### Removed
- **Retired and deleted the dead 25-hour blog-generation pipeline (directory + all CI), preserving every byte of live-site content.** The content-generation product (`ghl-podcast-pipeline/`: blog generators 1-9, the VPS systemd service, the scheduler, NotebookLM/Transistor scrapers, the dashboard, and all its data) was killed and will never run again. Deleted the whole directory plus its entire trigger surface: the 6 scheduled GitHub Actions workflows that orchestrated it (`daily-pipeline-health`, `measure-t1-recovery` — already broken, it `cd`'d into the deleted dir — `weekly-analytics`, `weekly-content-builder`, `weekly-measure-seo-change`, `weekly-seo-report`) and the `Claude_notebookLM_GHL_Podcast.md` "Project Brain" doc (~34k lines removed total). **No live content lost:** the only thing the static build read from the pipeline was the podcast-episode catalog (`published.json`, 158 episodes), which was relocated to `globalhighlevel-site/data/published.json` and `build.py` repointed at it; `design-homepage.py`'s pipeline `.env`/venv reference was made local. Verified the live site is exactly these 15 blog posts + 158 podcast episodes (sitemap confirmed — not "hundreds"). After deletion: build OK, 158 episodes + 15 blogs render, `verify.py` PASS (0 dead links), zero dangling `ghl-podcast-pipeline` references repo-wide. Cloudflare auto-deploys the live site on push, independent of the removed workflows.

## [0.1.0.14] - 2026-06-11
### Fixed
- **De-fabricated the India WhatsApp post's case study and corrected its PayU payment claims (3 spots).** The systemic fabrication audit (started for the Spanish automatizacion post) found the same pattern in `gohighlevel-whatsapp-business-api-setup-india`: a section headed *"Real Case: A Mumbai Digital Agency's Transformation — Case Study: Digital Momentum (Mumbai)"* with an invented 8-person agency and invented results (saved ₹18,000/mo, reduced onboarding 40%, closed 3 high-ticket clients in Q1, paid for itself in 3 weeks), no source. Reframed to an explicit illustrative example ("Picture a typical… typically runs… tends to pay for itself"), removed every invented specific. The two-model review (Codex + Claude adversarial) then caught that the **same post claimed native PayU in three places** — the reframed bullet, the comparison table row, and an FAQ ("integrates with both PayU and Razorpay"). Corrected all three: PayU is NOT a native GoHighLevel integration (it would need a custom build); Razorpay IS native (verified via HighLevel's support docs + the "Razorpay integration is now live" changelog — installed per sub-account from the App Marketplace, with agency-level support flagged as still incomplete by some Indian users). Table label PayU→Razorpay (keeps the ✅ accurate); FAQ rewritten to state Razorpay-native / PayU-custom. Verified: build + `verify.py` (0 dead links). Root cause is the blog generators producing fabricated "Real Case" studies + repeating the PayU-native error across languages — a pipeline-level fix is the next step.

## [0.1.0.13] - 2026-06-11
### Fixed
- **Replaced a fabricated "Caso Real" case study with an honest illustrative example.** The automatizacion post had a section headed *"Caso Real: Una Agencia de Diseño Web en Medellín"* featuring an invented company ("Digital Studio") with invented results — *recuperaron el 85% de los leads*, *4 horas → 30 minutos*, an exact *$553/mes* savings — all presented as a real case with no source. That is the fabricated-content / EEAT-penalty risk the project rules forbid. Found during the site-wide source-link audit. Reframed to an explicit illustrative example (*"Ejemplo: cómo se ve esto en una agencia pequeña… Imagina… suele… el resultado típico"*), removed every invented specific and the fake company, grounded the follow-up-gap point with a real, cited statistic (*44% de los vendedores se rinde tras un solo intento y solo el 8% hace más de cinco seguimientos*) linked to IRC Sales Solutions — a sales-training firm, NOT a CRM competitor, `rel="nofollow"` — and framed the ~$600–700-vs-$97 tool-cost comparison as illustrative. Two-model review (the human-editor replacement): Codex confirmed no fabrication remains and the cited stat is faithful to the source; a Claude adversarial Spanish pass returned CLEAN/0-blocking. Verified: build + `verify.py` (0 dead links). (Separate follow-up noted by the review: surrounding sections of this same post mix *voseo* with *tú* — a register-normalization pass for another PR.)

## [0.1.0.12] - 2026-06-11
### Fixed
- **Source-linked the Alexander Sandoval quote + made the vote count durable on the payments page.** `gohighlevel-latam-pagos-agencias` quoted a named real person (Sandoval, Chile agency) verbatim and cited "303 personas votaron" with no link — an unverifiable quote and a brittle live number (the GoHighLevel Ideas board showed 304 the very next day). Linked the quote and the vote stat to the GHL Ideas board MercadoPago feature-request thread (`ideas.gohighlevel.com`, `rel="nofollow noopener"`) — GHL's own property, so linking it is safe (no authority/traffic to a competitor) and *adds* EEAT by making the demand signal verifiable. Changed "303 personas" to the durable "más de 300 personas" so a drifting count can't make us look wrong, and tightened attribution to "la agencia chilena que abrió la solicitud" (verified via the board: Sandoval is the original requester; status Complete, April 2026; current count 304). No new claims — strictly adds a citation and de-brittles a number. Verified: build + `verify.py` (0 dead links). The durable lesson (published named quotes + community stats must link their source; don't link competitor sources on an affiliate page) was baked into the `/research-product-wedge` skill (claude-config 147e319).

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
