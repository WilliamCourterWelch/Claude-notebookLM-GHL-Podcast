# TODOS

Backlog for globalhighlevel.com (static site + build pipeline). Source of truth
for the Bing-first recovery ship queue (eng review 2026-07-21, run
`20260721T205056Z-57180`) plus follow-ups. Priorities: P0 (now) → P4 (someday).

## NEXT UP — CTR, not rankings (Bing data 2026-08-03)

### Rewrite titles + meta descriptions on pages ranking 2-6 with ~0% CTR
**Priority:** P0
**This is the highest-value lane on the site right now, and it is not a rankings
problem.** Bing already shows the site for the queries we want; almost nobody
clicks.

Evidence (Bing Webmaster, rolling window ending 2026-08-01):
- Sitewide CTR fell 2.72% (June) → 1.24% (July) while average position stayed
  good, mostly 2-6.
- Impressions are RECOVERING hard: the 7-day block bottomed at 242
  (07-01→07-07) and reached 891 (07-22→07-28), a 3.7x climb. Clicks did not
  follow. More eyeballs, same non-clicks.
- The AI cluster is the sharpest case: **~125 impressions, 0 clicks** across
  `get insights on go high level ai agent` (23), `...ai studio` (21),
  `...ai agent app` (15), `...ai studio pricing` (15),
  `discover more information about go high level ai studio pricing` (14),
  `...ai studio` (13), `...ai agent software` (12), `...ai agent` (12).
  AI queries are 14% of all impressions (189/1329).

Note those query shapes ("get insights on…", "discover more information
about…") look machine-generated, likely Copilot/assistant-mediated rather than
human typed. Worth deciding whether they are worth optimizing a title FOR, or
whether they are grounding impressions that will never click. **Answer that
question first** — it changes whether this is a title-rewrite job or a
structured-answer job.

**ANSWERED 2026-08-20 (v0.3.12.0):** grounding impressions, not click surface.
The cluster is 16 queries / 171 impressions at avg position 4.8 with **exactly
zero clicks** — no human reads a SERP title for "discover more information
about". This corroborates the 07-22 AI Search Queries export
(`concepts/globalhighlevel-bing-404-audit-2026-07-22`), where the site already
holds 17-50% citation share on the trial/pricing cluster, and GA4 confirms the
downstream traffic is real but small (28d: chatgpt.com 4 sessions, copilot.com
2, both with a key event). **Do not spend title rewrites here** — it is a
structured-answer / citation job. Full analysis:
`client-globalhighlevel:concepts/globalhighlevel-query-targets-2026-08-20`.

Start with the pages that have impressions and no clicks:
`gohighlevel-pricing-plans-2026-complete-guide` (325 impr / 2 clicks),
`how-to-install-gohighlevel-desktop-app-complete-setup-guide` (63 / 0),
`master-payment-providers-gohighlevel-complete-setup-guide` (52 / 0),
`gohighlevel-sub-accounts-snapshots-agency-guide` (37 / 0),
`how-to-maximize-ai-pricing-in-gohighlevel-2025-update` (33 / 0).

**Round 1 shipped in v0.3.12.0** against a fresh 2026-08-20 pull: free-trial
(610 impr / 0.7%), EN pricing (488 / 0.4%), sub-accounts (329 / 0.9%), `/in/`
(131 / 0.0%) and WhatsApp settings (55 / 0.0%). Still open from the list above:
`how-to-install-gohighlevel-desktop-app-complete-setup-guide` (now 308 impr but
already converting at 2.6%, so lower priority) and
`master-payment-providers-gohighlevel-complete-setup-guide` (112 / 0.9%), plus
`how-to-maximize-ai-pricing-in-gohighlevel-2025-update` (41 / 0.0%).

Do NOT start this before re-reading Bing on/after **Wed 2026-08-05** — the
current window predates the v0.3.9.1 + v0.3.10.0 recrawls and the 39-URL
IndexNow submit, so the baseline will move. (Satisfied: re-read 2026-08-20.)

## Site capabilities

### Embed a GHL conversation widget on the site: ask questions -> book a call
**Priority:** P1
**Scope confirmed by Bill 2026-08-03:** build it IN GoHighLevel and embed it on
globalhighlevel.com. A visitor lands, asks the widget questions, and if they want
to, books a call with Bill. Knowledge base sourced from the site's own content.

This is the first real **lead-capture** surface on the site. Today the only
conversion path is an affiliate click; this adds "booked call with Bill" as a
second, higher-value outcome from the same organic traffic. It is also
dogfooding — an affiliate site for GoHighLevel that visibly RUNS GoHighLevel is
proof rather than a claim, and the widget itself becomes a screenshot-able
demo for the AI silo pages.

**Pick the right GHL product before building — they are not interchangeable and
the cost model differs sharply** (all verified against GHL docs 2026-07-29, see
`plans/ai-silo-fact-ledger-2026-07-29.md`):
- **Conversation AI** — chat, bundled into AI Employee plans. Growth $50/mo caps
  at **1,000 chat responses/month**; Unlimited $97/mo is genuinely unlimited
  under fair use.
- **Agent Studio** — custom agents, **pay-per-use on EVERY plan, token cost per
  response, never bundled — not even in the $97 tier**.
- **Voice AI** — metered per minute; only relevant if the widget should talk.
- **AI Studio** — the prompt-based site/funnel builder. NOT this. Easy to confuse
  by name; the site has a whole page untangling it.

**Cost is the load-bearing decision here.** This widget sits on a public SEO site
whose impressions are climbing (7-day block went 242 -> 891 through late July), so
inbound volume is unbounded and grows with the CTR work above. A capped plan plus
a traffic spike equals a widget that silently stops answering. Model expected
conversations/month against the 1,000-response Growth cap BEFORE choosing a tier.

Knowledge base: the site has ~900 posts already written, which is the corpus. See
`add-tables-to-knowledge-base-gohighlevel-ai-employee-setup` and
`auto-refresh-knowledge-base-gohighlevel-keep-ai-accurate` — auto-refresh matters
because the corpus changes on every ship, and a stale KB will confidently answer
with retired facts (this session alone corrected pricing claims on 40+ posts).

**Existing constraints that must not be broken:**
- **Attribution.** `/trial/` is the podcast/owned-media destination and is
  `Disallow`'d in robots.txt on purpose so organic clicks do not pollute
  podcast-attribution data. Decide up front where a widget-booked call is
  attributed, and do not let the widget become a second uncontrolled path into
  the affiliate funnel.
- **The money page is a SINK.** `/blog/gohighlevel-free-trial-30-days-extended/`
  emits zero outbound internal blog/category links by design, and `verify.py`
  Check 4 enforces it. Do not hang the widget there without re-reading the sink
  doctrine in `globalhighlevel-site/CLAUDE.md`.
- **Static-output assumption.** `build.py` renders static HTML and `verify.py`
  gates it; a third-party embed script is a new runtime dependency neither gate
  knows about. Current perf is good (TTFB ~145ms, DOM ready ~773ms) and worth
  protecting — measure with `/benchmark` before and after.
- **Affiliate rules still apply** to every gohighlevel.com URL the widget emits:
  `fp_ref=amplifi-technologies12` + UTM, `rel="nofollow sponsored"`.

**Open questions for Bill (do not guess):** which calendar the booking lands on,
whether the widget should appear sitewide or only on money/AI-silo pages, and
whether it should be text-only or voice-capable.

## Gates (Ship 2)

### Add robots-aware crawlability gate to verify.py (next free check number)
**Priority:** P0
Scoped-correct robots.txt parser that fails loudly on unknown directives; no gate
currently knows robots.txt exists — that is how the `/start/` leak passed green for
3 weeks. NOTE: "Check 4" was taken by the canon-invariants gate in v0.2.11.0,
Check 5 by redirect-shadowing, and Check 6 by sitemap parity in v0.2.12.0 —
this lands as Check 7+. (Eng review T3)

### Regression test pinning the /start/ false-green case
**Priority:** P0
`scripts/test_verify_robots.py`: a link that resolves via `_redirects` while the
target is robots-blocked must FAIL verify. Protects the robots gate (T3 above)
from being silently weakened. (Eng review T4)


### Wire the zero-cost claim gate into the build backstop
**Priority:** P2
`scripts/test_zero_cost_claims_disclosed.py` (v0.3.11.0) scans the corpus for a
`$0 to start`-style claim with no `~$1` card-verification disclosure nearby. It
runs under pytest only. `build.py` and `verify.py` do not call it, so a deploy
path that skips pytest ships an undisclosed claim green — the same fail-open
shape as the FAQ-parity gap. Fold the scan into `verify.py` as a check, or call
it from `build.py` alongside `audit_links.py`. (Codex adversarial review,
2026-08-20)


### Escape titles/descriptions before interpolating into head tags
**Priority:** P2
`base_html()` (`build.py:1610`) writes `title` and `description` straight into
`<title>`, `<meta name="description">`, `og:title` and `og:description` with no
HTML escaping. **63 of 909 post titles contain `&`, and 58 built pages already
emit a bare `&` in `<title>`** — invalid HTML today, and head corruption or
attribute injection the first time a title carries `"`, `<`, or entity-looking
text from JSON. Fix is `html.escape(..., quote=True)` at the interpolation site,
but it must not double-escape titles that already carry deliberate entities, so
audit those 63 first. v0.3.12.0 sidesteps it (hub titles say "and", not "&")
rather than adding a 59th instance. (Codex adversarial review, 2026-08-20)


### Paginated hubs pair a self-canonical with root-level hreflang
**Priority:** P2
`build_language_hub` gives `/es/page/N/` a self-canonical but passes
`hreflang_path=""`, so `_build_hreflang_tags()` (`build.py:1486`) emits root
alternates (`/`, `/es/`, `/in/`, `/ar/`). Pages 2+ therefore carry unique titles
paired with alternates that describe different pages. Pre-existing, but sharper
now that paginated titles are distinct. Either pass the paginated path through
to the hreflang builder, or drop alternates on pages 2+. (Codex adversarial
review, 2026-08-24)


### Delete dead build_trial_page()
**Priority:** P1
`build.py` `build_trial_page()` (~line 2358) still calls `_build_affiliate_landing("start", "blog")` and its
docstring calls `/start/` a "full SEO-optimized page". Dead code with a misleading
docstring — one innocent future call rebuilds a retired page. Blast radius grew in
v0.3.0.0: the function also loops `LOCALIZED_LANDING_LANGS` (now es/in/ar), so an
accidental call would rebuild retired `/{lang}/start/` pages in all four languages.
(Note: per current Cloudflare docs the 301 would still win over a static file — see
T8 — so the risk is confusion + a stale crawlable artifact, not redirect shadowing.)
(Eng review T7)


### Delete vestigial repo-root _redirects
**Priority:** P1
Root `_redirects` still claims `/start` is a live landing page; the deployed file is
`globalhighlevel-site/_redirects` (build.py deploy copy, ~line 3543). Also confirm the Cloudflare Pages
output dir in the dashboard. (Eng review T9)

## Full-restore sprint follow-ups (from Day-1 reviews, 2026-07-23)


### Precompute silo map for circle/related/inject (perf at 2k+ posts)
**Priority:** P2
circle_members/get_related rescan all_posts per post (O(n^2 log n), ~2.5s combined
at ~950-post scale — site landed at 904 in v0.3.0.0 — fine today, ~2min at 10k) and _build_link_index is rebuilt per post. One
{(lang,topic): sorted members} map per build fixes all three. (Perf specialist 2026-07-23)

### Batch git reads in restore_posts.py
**Priority:** P3
931 sequential `git show` spawns ~10-30s; `git cat-file --batch` would do one.
One-off migration cost, acceptable. (Perf specialist 2026-07-23)

### verify.py Check 4 fail-detection self-tests
**Priority:** P2
Check 4 passes on real output but nothing proves it FIRES on violations (the 4a
vacuous-gate bug shipped exactly because of this). Synthetic-violation harness:
build a page missing its hub link / wrong circle / cross-silo card, assert FAIL.
(Testing specialist 2026-07-23)

### build.load_posts swallows unparseable JSON silently
**Priority:** P2
`except Exception: pass` drops a corrupt post from the site with no trace; the
restore now writes atomically so the main vector is closed, but the swallow
remains. Make it print loudly or fail. (Adversarial 2026-07-23)

### Sink strip + Check 4d cover only /blog|/category hrefs
**Priority:** P3
A baked followed link to /, /about/ or /es/... in a sink body would escape both.
Money page body has none today. Generalize both scans. (Adversarial 2026-07-23)

### In-prose contextual links for top spokes (eng review D12)
**Priority:** P2
Caleb canon: "links should be contextual, placed within relevant sections of text."
Circle + hub links are template-placed; weave contextual in-body links into the
~30 highest-value restored spokes (desktop-app, MCP, Agent Studio cluster) 2-3
weeks post-sprint, choosing pages from pull-bing.py recrawl data (only spokes
that reattached). Mirrors globalhighlevel-system/TODOS.md. Depends on: sprint
complete + recrawl data.

### Cross-silo body-link audit (eng review D11)
**Priority:** P2
Scan restored html_content for internal links crossing topic silos; retarget
within-silo or unlink. Firehose bodies predate the no-cross-link rule; render-time
anchor caps bound the worst repetition but don't fix silo leakage. Mirrors
globalhighlevel-system/TODOS.md. Depends on: sprint complete, topics final.

## Content rebuild (Ship 3)

### Fresh Bing pull + commit URL lists
**Priority:** P1
Re-run `pull-bing.py`; commit derived URL lists + raw export + command + date range.
On-disk pull is from Jun 30. (Eng review T10)

### Quality-gate the 15 dead URLs against git history
**Priority:** P1
`git show ea68058^:posts/<slug>.json` — judge each individually; they came from the
same firehose batch that caused the April demotion. (Eng review T11)

### Rebuild 12-15 Bing-ranked dead URLs at original slugs
**Priority:** P1
Start with `how-to-connect-airtable-in-gohighlevel` (Bing pos 1.0). No redirects for
these; external links SKIPPED per Bill 2026-07-21 (accepted known risk). (Eng review T12)

### Submit rebuilt URLs via scripts/submit_indexnow.py after deploy
**Priority:** P1
The submitter shipped in v0.2.11.0 (`scripts/submit_indexnow.py --urls FILE` or
`--sitemap`); this item is now just "run it after the rebuild deploy". (Eng review T14)

## Infra (Ship 4)

### Pages Function for real 410s on the ~70 thin-AI URLs
**Priority:** P2
`_redirects` supports only 301/302/303/307/308; real 410s need
`functions/_middleware.js`. Lowest value — only if slack. (Eng review T13)

### verify.py gate: FAQPage JSON-LD must match the visible FAQ copy
**Priority:** P1
FAQ answers exist twice inside the same `html_content` field — visible HTML and
an inline FAQPage JSON-LD block. Editing one silently desyncs the other, and
neither `verify.py` nor `audit_links.py` checks parity, so schema drift ships
clean. Hit for real in v0.3.9.1 (caught by codex adversarial, not by a gate).
Add a check that every `<h3>`/`<p>` FAQ pair has a matching `acceptedAnswer`
text, allowing for stripped markup.

**Status after v0.3.10.0:** the DATA is now clean (all 822 schema questions
across 159 posts: 0 duplicates, 0 orphans, 0 drift, 0 invalid JSON) and
`scripts/fix_faq_schema.py` can re-audit on demand. The GATE is still missing,
so nothing stops the next hand-edit from desyncing again. Raised to P1: during
this very migration a bad extractor wrote CTA/advertising text into 38 posts'
`acceptedAnswer` fields and every local gate stayed green — pytest, build.py and
verify.py all passed, because no gate reads schema content. Codex adversarial
caught it; a gate would have. Cheapest version: lift `has_real_defect()` +
`visible_pairs()` out of the migration script and assert zero defects over
`posts/*.json`, plus assert no answer contains CTA copy.

### verify.py gate: intended body links must survive render-time unwrapping
**Priority:** P2
`enforce_anchor_caps` unwraps an anchor→URL pair past 3 identical uses sitewide,
and `unwrap_cross_silo_links` drops cross-silo body links — both silently, with
no gate reporting that an author-added link vanished from built output. Codex
measured three v0.3.9.1 silo anchors sitting at 2/3 of the cap, so one more
matching anchor earlier in sorted build order would strip them. Add a check
comparing body links in post JSON against anchors in the built HTML, reporting
any that were unwrapped.

## AI silo follow-ups (Bill review, 2026-07-30)

### Pricing-table screenshots (sandbox GHL or official pricing page)
**Priority:** P2
Bill asked whether the tier tables can be augmented with real screenshots
(his sandboxed GHL account or gohighlevel.com's pricing page). Parked after
v0.3.8.0 shipped styled HTML tables — screenshots are now an EEAT addition,
not a fix. MUST follow the capture → solid-bar redact → Bill attestation →
publish HARD RULE (site CLAUDE.md, v0.3.5.0) on either source.

### Next AI-product spokes: Conversation AI / Reviews AI / Agent Studio — sequencing discussion with Bill
**Priority:** P2
The help-center folder 155000001368 (Agent Studio) alone has 21 articles;
Conversation AI and Reviews AI have their own corpora. Candidate spokes
feeding the AI pillar, to be sequenced against the Arabic-expansion queue
(session state 2026-07-30). Per the updated /research-product-wedge Step 0a
(and learning wedge-research-skips-vendor-doc-corpus): each spoke's research
STARTS by enumerating that product's help.gohighlevel.com doc folder and
building the capability model from it — demand data layers on top.
Discussion with Bill pending; do not start without his sequencing call.

## Content hygiene

### Rebuild stripped es sections via /research-product-wedge (Bill-directed)
**Priority:** P1
**PROGRESS v0.3.5.0 (2026-07-28):** Post 1 of 10 rebuilt and shipped (configurar-workflows-
gohighlevel-whatsapp-mercadopago, 301→1554 words, wedge vault + attested screenshots +
in-silo links).
**PROGRESS v0.3.9.0 (2026-07-31):** Post 2 of 10 rebuilt and shipped (copiar-templates-
temporizadores-gohighlevel, 423→975 words). Its premise was ungrounded, not merely thin:
the full 5-class fetch budget found zero support for "copying breaks the timer", so the
post was rebuilt on the documented GIF mechanism, the documented clone steps were added,
and a regression gate (`scripts/test_timer_break_premise.py`) now blocks the retired
phrasings in es posts. Provenance committed at `plans/es-timer-rebuild-2026-07-31/`.
The 4 fetch-resolvable ungroundeds and Step 5 competitor research both completed in the
wedge vault (2026-07-30) and feed the remaining rebuilds.
Remaining: 8 posts, 121-post Caso Real batch decision (the 7 highest-exposure posts got
the Ejemplo-hipotético treatment in v0.3.6.0), and the EN/en-IN timer siblings that still
assert the retired premise (#53) plus the contradicting Apple Mail mechanism post (#54).
v0.3.4.0 stripped editor notes + fabricated "Caso Real" cases from 27 es posts;
the honest gaps now need real content (Bill 2026-07-28: "strip and then use the
research wedge to fix them"). Highest-value gaps: configurar-workflows-gohighlevel-
whatsapp-mercadopago (how-to shell — title promises configuration, body has none),
gohighlevel-workflows-practicos-… (slug still says "casos-de-uso-reales", zero cases),
maestro-ai-flow-builder (setup guide missing steps 2-5), configurar-facebook-
instagram-messaging (paso-a-paso section removed), copiar-templates-temporizadores
(steps 2+ missing), vista-kanban (sections 3-8 never existed), workflows-gohighlevel-
mercadopago-whatsapp-automaticamente + plantillas-agencias-5-minutos + inmobiliarias
(case + how-to sections). (ai-help-gohighlevel-workflows-construccion-rapida's
"Casos reales" intro bullet was removed same day — deliver real cases there
during the rebuild if the wedge produces them.) Any new "Caso Real" must be real and verifiable — the
sitewide inventory shows ~137 es posts carry "Caso Real" headings from the same
firehose batch; audit that wider set during the wedge (fabrication risk beyond the
27 already handled). Gate: test_no_editorial_markers.py bans editor notes re-entering.
Watch notes from the 0.3.4.0 adversarial review: (a) all 28 stripped posts got
updatedAt=2026-07-28, so crawlers are invited to recrawl them at their thinnest
state until the rebuild lands — prioritize the wedge accordingly; (b)
gohighlevel-mercadopago-mexico body contains bill@reiamplifi.com in prose —
confirm intended; (c) workflows-gohighlevel-mercadopago-whatsapp-automaticamente
still has one pre-existing unclosed <p> (browsers auto-close; cosmetic).

### Editorial-debt gate is pytest-only — consider a verify.py hook
**Priority:** P3
test_no_editorial_markers.py runs in the documented pre-deploy pytest suite
(CLAUDE.md), but verify.py/build.py don't invoke pytest, so a deploy path that
skips pytest skips the gate. If that ever bites, add a verify.py check that
shells the two test functions. (Red team 2026-07-28)

### Refine trial-claim render pass long tail
**Priority:** P3
v0.3.0.0 pre-landing review shipped `correct_trial_claims()` — a render-time
exact-phrase pass that rewrites the known no-card boilerplate (en/es/ar, bodies
+ meta descriptions) to the ~$1 card-verification truth; rendered residual was 0
across 904 pages. RESOLVED 2026-07-28 in two rounds. Round 1: 9 escaped
lowercase variants in 7 es posts added as sentence-level exact entries.
Round 2 (standalone /review caught the round-1 scan was casing-blind):
Title-Case escapes ("(Sin Tarjeta de Crédito)", "(No Credit Card)"), the
Spanish trial page's own stored TITLE (title/h1/JSON-LD fan-out), and a
render-path gap — category-page card excerpts never ran the correction
pass (now correct-then-truncate at all 6 card sites). The manual scan is
retired: scripts/test_trial_claims_residual.py now gates this automatically
(ordering invariant + entry behavior + case-insensitive corpus residual,
titles included). Remaining: consider a Devanagari (Hindi) variant if one
ever appears. (Codex review 2026-07-27; resolved + gated 2026-07-28)

### About-page copy in build.py is stale post-restore
**Priority:** P2
`build.py` about-page body (~line 3267, 3311) still says "300+ tutorials", "10
content categories", and "India, Latin America" — site is now 909 posts, 5 topics,
and 4 languages including Arabic. Copy lives in code, so it was out of scope for
the docs pass. (Codex doc review 2026-07-27)

### Confirm /es/start 301 target (pricing guide vs restored Spanish trial post)
**Priority:** P3
The dead-pointer half of this item resolved itself in v0.3.0.0: both money-page
`translations` targets (es + en-IN) were restored in Batch 3, so hreflang emits
again. Remaining: `/es/start` 301s to the pricing guide while the restored Spanish
trial post (`gohighlevel-prueba-gratis-30-dias-como-empezar`) now exists — confirm
that target is still intentional or repoint. (Adversarial review 2026-07-22;
updated 2026-07-27)

### Discount-intent coverage check on money page
**Priority:** P3
`/discount`, `/coupon-code`, and the old promo-discount blog URL all 301 into the
money page, whose new title dropped "Discounts"; description still carries it.
Watch discount-query impressions post-recrawl; revisit title if they sag.
(Codex 2026-07-22)

### Money-page rendered title is 70 chars with brand suffix
**Priority:** P3
`build.py` appends " | Global High Level" (20 chars) to every post title, so the
50-char money-page title renders at 70 — keyword payload fits the ~60-char visible
budget, brand suffix truncates in SERPs. If Google starts rewriting the title,
consider suppressing the suffix for the money page (template change, pairs with T5).
(Claude + Codex 2026-07-22)

### /trial/ noindex is invisible behind its robots block
**Priority:** P3
`build.py` sets noindex on `/trial/` (`_build_affiliate_landing`, ~line 2756) but robots.txt blocks crawlers from ever
reading it, so external podcast links can get `/trial/` indexed as "URL indexed
without content" — polluting the attribution cleanliness the block protects. Check
GSC coverage for `/trial/`; if indexed-without-content appears, decide between
unblock+keep-noindex vs status quo. (Adversarial review 2026-07-22, pre-existing)

### Review backlog (v0.3.0.0 pre-landing, all P3)
**Priority:** P3
- Language config duplicated: `LOCALIZED_LANDING_LANGS` repeats prefix/dir that
  categories.json declares (guarded by test_localized_landing_configs; resolve
  by lookup or keep the test). (maintainability 2026-07-27)
- site CLAUDE.md says "never hardcode ltr" but build.py:1512's bespoke ES
  vertical template hardcodes dir="ltr" (harmless, es is LTR). (maintainability)
- Arabic pages still carry minor English chrome: "Home" breadcrumb, byline,
  "min read". Nav/CTA/guides ARE localized as of v0.3.0.0. (adversarial)
- 2 posts hold dead translations.en pointers to a nonexistent promo-code slug
  (gohighlevel-coupons-hindi-india-guide, codigo-promocional-gohighlevel-2026-
  descuentos-reales) — gated out of output, cosmetic. (adversarial)

### Arabic/i18n polish backlog (v0.3.1.0 review, all P3)
**Priority:** P3
- English chrome blocks on ar pages (CTAs "Ready to try this?", trailing arrows,
  podcast/share/author boxes) render in RTL bidi context — wrap intentionally-
  English blocks in dir="ltr" containers or extend label dicts. (adversarial)
- Breadcrumb JSON-LD still hardcodes "Home" on es/ar posts (visual breadcrumb
  is localized; the schema.org name is not). (codex)
- Consolidate chrome labels into one CHROME_LABELS map — labels now live in
  the post-renderer dicts + localize_date/localize_rtime + authority footer.
  (maintainability)
- localize_trial_hrefs() is exact-match by design (single-quote/query-string
  variants unhandled; zero exist in corpus — verified). Revisit if the es/en
  cohort rewrite ships. (codex)
- Confirm the es↔en-IN coupon hreflang pair (codigo-promocional ↔
  coupons-hindi) are genuine content equivalents — codex flags the cluster as
  possibly false; both about promo codes, symmetric, pre-existing. (codex)

### Spanish topic keywords for better es pillar-link coverage
**Priority:** P3
inject_pillar_link() wove only 7 es links (vs 138 en) because categories.json
keywords are mostly English words. Adding Spanish multi-word keyword lists per
topic would lift es contextual coverage. Confirmed by codex adversarial
(0.3.3.0 review): 7/249 es, 0/8 ar eligible posts injected. (Pack B 2026-07-27)

### Caleb canon as a FAT SKILL, not more build.py code (Bill-directed)
**Priority:** P2 — next architecture step after v0.3.3.0 lands
Bill (D13 gate, 2026-07-27): the plan was restore-then "create fat skills thin
harnesses out of caleb canon to apply to the whole site" — not accrete canon
judgment into build.py. build.py render passes should stay deterministic
EXECUTION of already-made calls; the JUDGMENT layer (what counts as a silo
violation, exemption doctrine, when to add/remove links, how to audit a new
content batch against canon) belongs in a markdown skill Claude reads at
runtime. Ground in Tan canon first (/office-hours or /plan-eng-review) before
building — do not freestyle a skill design.

### Shared _render_body_passes() helper (review 0.3.3.0)
**Priority:** P3
The body-pass chain (localize_trial_hrefs → correct_trial_claims →
nofollow_affiliate_links → wrap_tables → unwrap_cross_silo_links →
enforce_anchor_caps) is hand-repeated at 3 render sites (build_post_page,
build_authority_page, hub pillar in build_category_pages) — the hub site
missed the unwrap wire until the 0.3.3.0 review caught it, and v0.3.8.0's
wrap_tables had to be hand-wired at all 3 sites again. Extract one helper so a new pass cannot miss a
call site. Same class: inject_pillar_link and inject_internal_links duplicate
the paragraph-eligibility/splice machinery — and inject_internal_links still
carries the lowercased-copy indexing + bare '<p' split that 0.3.3.0 fixed in
inject_pillar_link (adversarial: identical latent bugs). Fix both when
extracting. Also derive FUNNEL_SINK_SLUGS' money slug from a shared constant
(one more silent-drift site today). Codex advisory residuals (0.3.3.0, both
0-instance in corpus): a shared tolerant href extractor (single-quote/uppercase/
protocol-relative links invisible to unwrap + Check 4e), and explicit series
metadata instead of _series_nav_exempt's common-directory inference.

### Pillar-link build-order churn + anchor diversity (adversarial, watch)
**Priority:** P3 — watch-mode, revisit with real SERP data
Cap slots are consumed in merged-list order, so adding/reordering posts
reshuffles which pages carry pillar links next build (link-graph churn class).
Payments & Pricing has 1 usable multi-word keyword → identical exact-match
anchor on all its pillar links. Also note: EN posts can carry up to 3 hub
references (eyebrow + in-prose + P1.2 footer block) — intended stacking,
documented here so nobody "fixes" it blind.

## Completed

### Give /es/ hub a real title (round 2 of the snippet rewrite)
**Priority:** P2
`/es/` rendered a bare "GoHighLevel Español" and drew 25 Bing impressions at
position 6.9 with ZERO clicks (2026-08-24 pull). Now reads "GoHighLevel en
Español: 249 Guías Paso a Paso", with per-language pagination wording so
`/es/page/N/` says "Página N". First draft said "Guías para Agencias" and was
corrected in review: 30 of the 249 Spanish posts are not agency-framed.
**Completed:** v0.3.13.0 (2026-08-24)


### Pack B: Caleb-canon linking (D11 strict + D12 contextual) — DECIDED & SHIPPED
**Completed:** v0.3.3.0 (2026-07-27)
D11: cross-silo body links unwrapped render-time — 38 total after the review
extended coverage to custom-URL posts and the hub pillar render (D13); funnel
+ series-nav exempt; 0 remain rendered in any link shape, verify Check 4e now
guards it. D12: 102 clean in-prose pillar links woven (word-boundary guard
replaced the first cut's 168, ~55 of which split words mid-plural). Bill's
calls: strict unwrap + mechanical render pass + D13 extend-and-gate.


### Trial CTAs direct-to-affiliate per language — DECIDED & SHIPPED
**Completed:** v0.3.2.0 (2026-07-27)
Bill's call: in-body trial links route direct to the language-matched GHL
affiliate page (en/en-IN -> bootcamp, es -> bootcamp-es tracker-verified,
ar -> /ar/trial/ since GHL has no Arabic page). utm_campaign=blog-trial-{lang}
splits portal clicks. /trial stays live for the podcast spoken URL.


### Restore Batch 3 (FINAL) + /ar section — SPRINT COMPLETE
**Completed:** v0.3.0.0 (2026-07-27)
619 pages restored; /ar hub + RTL + Arabic trial landing (Bill: build the AR
section); all 931 accounted: 877 live + 54 twin 301s. Arabic disposition
resolved (option a). 904 posts live.


### Restore Batch 2
**Completed:** v0.2.13.0 (2026-07-27)
136 tier-A/B pages restored (incl. GA4-promoted RFC-5322 pair — canonical as
page, india twin as 301 per clone policy), 13 twin 301s, all 8 old-taxonomy hub
redirects now correct (4 added, 1 target fixed). 285 posts live.


### Restore Batch 1 (Day 2 of full-restore sprint)
**Completed:** v0.2.12.0 (2026-07-23)
122 pages restored at original slugs (Bill-approved topics via 147-slug override
file), 15 clone-twin 301s (1 held with Arabic), signup links rewritten to
affiliate, zero followed fp_ref anchors sitewide (nofollow-sponsored stamped at
render where missing), sitemap parity gate
(Check 6) + redirect dupe/dead-target gates (Check 5b/5c) added.


### Ship 2 (Day-1 restore sprint) — CTA repoint, audit doctrine, Cloudflare comments (T5, T6, T8)
**Completed:** v0.2.11.0 (2026-07-23)
T5 shipped in its D2-superseded form: in-post CTAs repoint to the money page
DIRECTLY, staying rel=nofollow (sprint eng review D2 overrode the varied-anchor
editorial plan; internal equity flows via the canon link structure instead), with
render-time anchor caps (`enforce_anchor_caps`) killing identical-anchor cliffs
from firehose bodies. T6: `/start`+`/coupon` no longer audit-exempt; nofollow links
exempt by rel; prefixes imported from build.py with segment-boundary matching.
T8: both inverted Cloudflare-precedence comments corrected; the build now PRUNES
_redirects rules that shadow built pages (158 restore slugs were shadowed) and
verify.py Check 5 gates it.

### Ship 1 — Bing recovery cheap wins (eng review T1 + T2)
**Completed:** v0.2.10.1 (2026-07-22)
Removed `Disallow: /start/` + `/coupon/` (Bill-approved extension) from robots.txt;
money-page title/meta rewrite with `updatedAt` bump; blog Article JSON-LD
`dateModified` now prefers `updatedAt` (+ regression test in test_build_links.py);
doctrine updated in both CLAUDE.md files.
