# Frontend Design Standards — GlobalHighLevel.com

## Brand & Audience
- Site: GlobalHighLevel.com — free GoHighLevel tutorials and affiliate site
- Audience: Digital marketing agency owners, freelancers, business owners
- Tone: Confident expert talking to a peer. Not a salesperson. Not a blogger.
- Goal: Affiliate signups for GHL 30-day free trial

## Design Rules — Non-Negotiable

### NO generic AI aesthetics:
- No purple/violet gradients
- No Inter or Roboto as the primary display font
- No "glassmorphism" cards with blur effects
- No generic blue (#3b82f6) as the accent
- No grid-of-3-feature-cards with emoji icons as the only layout idea

### DO use distinctive choices:
- Pick ONE unexpected accent color (amber, coral, lime, copper — not blue, not purple)
- Use DM Sans 800 for headlines (loaded via Google Fonts)
- DM Sans for body copy — clean and readable
- Asymmetric layouts, pull-quotes, editorial treatments
- CSS animations: entrance fades, scroll reveals (CSS only, no JS deps)
- Generous whitespace — let the content breathe

### Typography hierarchy:
- Headlines: DM Sans 800, clamp(2rem, 4vw, 3.5rem), line-height 1.15, letter-spacing -.5px
- Section headlines: DM Sans 800, 1.5rem
- Body: 19px, DM Sans 400, line-height 1.75
- Labels/eyebrows: 13px, uppercase, letter-spacing .5px

### Color palette:
- Background: Near-black (#07080a)
- Surface cards: #111520
- Accent: Amber (#f59e0b) or another non-generic choice — decide before building
- Text: #eef2ff (primary), #7c8aab (secondary), #3d4a63 (muted)
- Do NOT use blue as the primary accent

## Affiliate Link Rules — NEVER Break These

- **Every single link to GoHighLevel.com MUST use the affiliate link** — no exceptions
- Affiliate link: `https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12`
- Always append UTM params: `&utm_source=globalhighlevel&utm_medium={location}&utm_campaign={context}`
- This includes: pricing pages, feature pages, sign-up pages, help links — ANYTHING on gohighlevel.com
- NEVER link to `gohighlevel.com/pricing` or any GHL URL without `fp_ref=amplifi-technologies12`
- All affiliate links: `target="_blank" rel="nofollow noopener"`
- **Render-time backstop (v0.2.12.0):** `build.py` (`nofollow_affiliate_links`) runs over stored post bodies and stamps `rel="nofollow sponsored"` on any `fp_ref=` anchor that lacks `nofollow` (anchors already carrying `nofollow` are left as-is; template CTAs render their own `nofollow noopener`). Stored JSON untouched. Firehose-era bodies carried followed paid links (Google paid-link policy risk); the guaranteed invariant is **zero followed affiliate anchors sitewide**. Author-written rel attributes are still expected — the pass is the backstop, not the norm.
- **No placeholder `#` links** — if the real URL isn't known, link to `/category/gohighlevel-tutorials/` or `/`
- **Citation exception (added 2026-06-22):** *reference* links to `help.gohighlevel.com`, `ideas.gohighlevel.com`, `help.leadconnectorhq.com`, or `gohighlevel.com/post/...` (docs, the ideas/feature forum, changelog, blog posts) used as **sources/citations** are EXEMPT from `fp_ref` — they are evidence/EEAT references, not conversion CTAs, and `fp_ref` on a help-doc makes no sense. The rule applies to **conversion-intent** links (signup, pricing, trial, feature/sales pages). Every conversion link still MUST carry the affiliate link + `fp_ref`.
- Spotify podcast link: `https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV`

## /trial/ — Attribution URL (NOT an SEO landing) · /start/ + /coupon/ — RETIRED 301s

**Purpose:** These three paths were dedicated attribution/conversion pages for people who arrive from our owned media (podcast descriptions, blog CTAs, social), intentionally separated from organic SEO pages. As of 2026-07-22 only `/trial/` is still a live page — `/start/` and `/coupon/` are retired 301s (see below).

**What they are:**
- **`/trial/`** — podcast-description destination. Every episode description on Spotify/Apple points here.
- **`/coupon/`** — RETIRED. Was the promo-code / discount-hunter destination (podcast + social use). No longer built; `_redirects` 301s it to `/blog/gohighlevel-free-trial-30-days-extended/`. Unblocked in robots.txt 2026-07-22 (Bill's call, same rationale as `/start/`) — do not re-add `Disallow: /coupon/`.
- **`/start/`** — RETIRED. Was the blog-article-embedded CTA destination (split from `/trial/` on 2026-04-15). The page is no longer built (`build.py` skips it) and `_redirects` 301s it to `/blog/gohighlevel-free-trial-30-days-extended/`. Unblocked in robots.txt 2026-07-22 so crawlers can see the 301 — do not re-add `Disallow: /start/`.

**Format (describes `/trial/` today; historical for the retired `/start/` + `/coupon/`):**
- Full content pages, ~1,500–2,000 words each
- Pitch BOTH GHL primary affiliate AND Extendly secondary affiliate (education + trust before the click)
- 7+ outbound affiliate links with `fp_ref=amplifi-technologies12` + UTM params
- GA4 fires `cta_click` / `affiliate_click` event on every CTA press (before the outbound redirect)
- Peter Attia voice: teach the "why 30 days not 14", who it's for, what's included, then affiliate

**Why `/trial/` is `Disallow`'d in `robots.txt`** (applied to all three until 2026-07-22; now `/trial/` only):
- Normal Googlebot is explicitly blocked from crawling the path
- AI crawlers (GPTBot, ClaudeBot, Google-Extended, PerplexityBot, anthropic-ai) ARE allowed
- Reason: keep attribution clean — these URLs must NOT compete in SERPs with our organic blog pages, otherwise podcast-click data is polluted with organic-search clicks

**Locked for 8 weeks** (historical: was enforced via `locked_until` in the retired pipeline's `seo-cooldown.json`; the SEO optimizer that read it is gone as of 2026-06-11, so this lock is no longer auto-enforced — keep the paths out of SERP competition manually).

**Parallel SEO-indexable pages exist** for trial + pricing (these rank for organic money keywords):
- `/trial/` ↔ `/blog/gohighlevel-free-trial-30-days-extended/`
- `/blog/gohighlevel-pricing-plans-2026-complete-guide/` for the pricing query cluster

`/coupon/` does NOT have a parallel SEO blog. Per Apr 21 redesign (commit `3788bf1`): the old `/blog/gohighlevel-promo-code-discount-2026-real-ways-to-save/` was deleted and `_redirects:18` 301s any inbound traffic to `/blog/gohighlevel-free-trial-30-days-extended/` (the trial blog is the canonical SEO destination for both trial and discount intent — they consolidated). Auto-deploy `aa23952` accidentally re-added the promo blog on the cliff day; cleaned up again 2026-05-07 in commit `3f8588e`.

The live attribution URL (`/trial/` — historically also `/coupon/` and `/start/`) and the SEO blog are allowed to have overlapping content — different audiences, different funnels, different attribution. Edit them independently.

**Do NOT:**
- Unblock `/trial/` in `robots.txt` — it breaks attribution. (`/start/` and `/coupon/` are the exceptions: both retired + 301'd, deliberately unblocked 2026-07-22 so their link equity flows to the money page.)
- Migrate their content to the blog pages — kills podcast-listener UX and the Extendly pitch
- Thin them out to a fast redirect — loses the "teach before you sell" voice and Extendly conversion
- Point internal cross-links to these paths for SEO reasons — always link to the `/blog/...` SEO page for content context, reserve attribution paths for owned-media CTAs only

**When editing:** if you rewrite one, consider whether the parallel SEO blog post needs the same update (e.g., new FAQ entry, updated pricing). They're independent artifacts serving different audiences, but fact drift between them is confusing.

## Internal Link Doctrine & Build Gates (canon since v0.2.11.0)

The canon link structure is enforced at render time by `build.py` and gated by
`verify.py` — do not hand-wire internal links that fight it.

**Link template (per blog post):**
- **Link circle:** every post in a silo with 2+ members carries a prev/next nav
  within its language+topic silo, wrapping at the ends so each silo is one
  closed loop (singleton silos get no circle). Pillars, sink pages, and
  series/authority pages are excluded by construction.
- **Contextual injection is same-silo only** — no cross-language, no
  cross-topic. In-silo or not at all.
- **Related cards rotate deterministically per post** (not first-three) and are
  suppressed entirely on sink pages.
- **Sink airtightness:** the money page (`/blog/gohighlevel-free-trial-30-days-extended/`)
  suppresses related cards, circle nav, and the followed category-eyebrow link,
  and strips followed `/blog|/category` anchors from the body — so it emits no
  outbound internal blog/category links. (The author box still links `/about/`;
  generalizing the scan is an open TODO.) Do not add outbound links to it.
- **Internal trial-path CTAs (formerly `/start/`) point at the money page
  directly**, `rel=nofollow`. Direct-affiliate CTAs (cta3, TLDR) still go
  straight to the affiliate URL. Trial-path conversion CTAs get `rel=nofollow`
  stamped at render time.
- **Anchor caps:** beyond 3 identical anchor→URL pairs sitewide (including
  anchors baked in stored post bodies and absolute same-site URLs), the link
  unwraps to plain text at render time — post JSON is never mutated.
- **Neither stripping pass names the link it dropped, and no gate fails on it
  (learned v0.3.9.1).** `unwrap_cross_silo_links()` (build.py:775) and
  `enforce_anchor_caps()` (build.py:362) both remove an author-added body link
  by dropping the anchor and keeping the words. The cross-silo pass at least
  increments `_RENDER_PASS_COUNTS["unwrapped"]`, and `main()` prints an
  aggregate count (build.py:4131); `enforce_anchor_caps()` records nothing at
  all. Neither reports WHICH intended link was lost, and `verify.py` still
  reports clean either way, so the post reads fine and the build is green while
  the link is gone. After adding any body link by hand, grep the BUILT html
  under `public/` for the target href to confirm it survived. A proposed verify
  gate is tracked in TODOS.
- **On the 159 posts that embed FAQ schema, the answer text exists TWICE inside
  the same `html_content` field (learned v0.3.9.1):** once as visible HTML
  (`<h3>` + `<p>`) and once inside an inline `FAQPage` JSON-LD `<script>` block.
  Editing only the visible copy desyncs the rich-result surface, and neither
  `verify.py` nor `audit_links.py` checks parity. When you touch an FAQ answer,
  check whether the post embeds `FAQPage` and change both copies if so (a
  `.replace()` over the field should match `count == 2`). Posts WITHOUT an
  inline block are safe: `faq_schema()` (build.py:1948) generates the schema
  from the visible FAQ at render time and returns early when `"FAQPage"` is
  already present, so it never double-writes. Gate still tracked in TODOS (P1).
- **The data is clean as of v0.3.10.0, and `scripts/fix_faq_schema.py` keeps it
  that way.** That migration rebuilt 39 posts from their own visible copy
  (8 duplicate `FAQPage` blocks, 19 orphan questions asserting a Q&A absent from
  the page, 26 drifted answers). Re-run it any time: `--dry-run` audits, a bare
  run fixes, and a second run is a clean no-op. It refuses rather than guesses —
  it will not strip a post's only schema, and it aborts on any post where it
  recovers under half the existing questions.
- **HAZARD when writing ANY FAQ extractor: the trial CTA is a SIBLING `<div>`
  immediately after the FAQ container.** Bound an answer on the next heading and
  the last answer on the page swallows the CTA. That put "Ready to Get Started…
  Claim Your Free Trial" inside 38 posts' `acceptedAnswer` during v0.3.10.0
  development — advertising copy in structured data, which Google's
  structured-data policies prohibit. Bound answers on `</div>`/`<div`/`<section`
  as well as headings. **Every local gate stayed green while this was wrong**
  (pytest, `build.py`, `verify.py`) because no gate reads schema content; codex
  adversarial review is what caught it.
- **FAQ markup is not uniform across the corpus.** 8 distinct FAQ section
  heading variants (157x "Frequently Asked Questions", 4x "Preguntas
  frecuentes", 4x "Common Questions About/During X", 2x "الأسئلة الشائعة"), and
  **37 posts head their FAQ with `<h3>` rather than `<h2>`** — so an extractor
  that ends the section at the next `<h3>` sees those as empty, because the
  questions themselves are `<h3>`. Beware the Arabic near-miss: "أخطاء شائعة"
  is "common *mistakes*", not an FAQ heading, and must not match.

**Gates (all must pass before deploy):**
- `verify.py` Check 4 — canon invariants on built output: every spoke links up
  to its hub, circles close exactly as computed, template links never cross
  language or topic silos, sinks emit zero outbound internal links.
- `verify.py` Check 5 — redirect defects: no `_redirects` rule may shadow a
  built page (on Cloudflare Pages a redirect ALWAYS beats a static file — the
  build prunes shadowing rules and prints the pruned sources); no duplicate
  redirect sources (first-match-wins means a dupe silently shadows the later
  rule — 5b, v0.2.12.0); no `/blog/` 301 may land on a non-built page (dead
  target — 5c, v0.2.12.0).
- `verify.py` Check 6 (v0.2.12.0) — sitemap parity: every sitemap `<loc>` must
  be a built page and never a redirect source. The build excludes pillar
  `/blog/` URLs that 301 to their hubs from the sitemap, so IndexNow
  submissions only carry real pages.
- `verify.py` Check 7 (v0.3.15.0) — SERP title length. **A ratchet plus two hard
  invariants; read the title rule below before changing any of it.** The ratchet
  counts titles over 60 characters and fails only if the number grows past
  `TITLE_OVERLONG_BASELINE` (580 as of v0.3.16.0; the constant carries its own
  history, so read it rather than trusting this line). The invariants fail
  outright: no page
  may keep the brand suffix while over the limit, and no page may have room for
  the brand and lack it — either proves a title was composed outside
  `compose_title()`. Scans every `*.html` (404.html is standalone and was
  invisible to an `index.html`-only scan) and skips `noindex` pages.
- `scripts/audit_links.py` — `/start` + `/coupon` are no longer audit-exempt;
  nofollow links are exempt from anchor doctrine by `rel` attribute; exemption
  prefixes are imported from `build.py` (single source of truth) and matched on
  path-segment boundaries.

**Restore + recrawl tooling (full-restore sprint, v0.2.11.0+):**
- `scripts/restore_posts.py --slugs FILE|--all --deploy-date YYYY-MM-DD
  [--dry-run] [--report PATH] [--topic-overrides FILE]` — restores pruned
  posts from git history at their original slugs; never overwrites a newer
  page; maps old 8-topic taxonomy onto the current 5 hubs; normalizes
  affiliate hrefs to the current `fp_ref`; writes atomically; exits nonzero on
  any slug error. `--topic-overrides` takes a `{slug: topic}` JSON (the
  Bill-approved assignment sheet) that wins over the taxonomy mapping —
  unknown topics are fatal, and the report counts how many overrides were
  consumed (`overrides_applied`).
- `scripts/submit_indexnow.py --urls FILE|--sitemap [--dry-run]` — pushes URL
  batches to Bing via IndexNow. The key lives in `indexnow-key.txt` and is
  hosted at `/<key>.txt`; the script verifies the key file is live before
  submitting and fails loudly on any non-2xx.

## Languages & the /ar Section (v0.3.0.0)

- **`/es/` page 1 renders ZERO post cards, and that is not a bug.** Read this
  before "fixing" it. `build_language_hub()` has an explicit
  `if page == 1 and lang_code == "es":` branch that replaces the standard
  card-grid body with a hand-authored brand hub: hero, a featured pricing-guide
  card, three topic clusters, and the English-site banner. Deliberate since
  v0.2.0.0 (commit `6a83e63`, "MVP relaunch — EN+ES brand-hub homepages") and
  reconfirmed by Bill on 2026-08-24. Every other language, and every `/es/page/N/`,
  takes the `else` branch and renders cards normally. A 2026-08-24 session spent
  a full investigation rediscovering this from scratch — the symptom looks
  exactly like a broken hub.
  - **Consequence worth knowing:** that branch still consumes its slice
    (`lang_posts[0:18]`) and then throws the cards away, so the 18 newest Spanish
    posts are absent from the hub's numbered path, which reaches 231 of 249. They
    are not orphaned (all sit on `/es/category/` pages and in the sitemap). Open
    P2 in `TODOS.md` with both closure options.
  - **Because of that hole, no `/es/` surface may state a corpus count** — not
    the `<title>`, not the paginated subtitle, not the all-topics chip (which
    reads `Todas`, not `All (N)`). v0.3.14.0 removed all three after Codex
    caught the title claiming 249. `/in/` and `/ar/` keep their counts: their
    page 1 renders cards and links every page, so theirs are honest.
  - Until v0.3.14.0 that branch also emitted **no pagination at all**, so
    `/es/page/2..14/` had zero inbound links and no sitemap entry (no `/page/`
    URL is sitemapped, by policy). `es_library_block()` now carries the strip
    into the curated body. If you edit this branch, keep `{es_all_guides}` in it.
- **4 languages in `categories.json`:** en (default, no prefix), es (`/es`),
  en-IN (`/in`), and ar (`/ar`, `dir: rtl`). Arabic is the only RTL language —
  templates read `dir` from the language config; never hardcode `ltr`. The ONE
  deliberate exception: the logo anchor pins `dir="ltr"` so bidi reordering
  doesn't flip the brand's two spans into "HighLevelGlobal" (v0.3.1.0).
- **Post chrome is localized per language** (v0.3.1.0): breadcrumb Home,
  byline, and read-time render via lookup dicts in the post builder — es gets
  Inicio / Por / "min de lectura", ar gets الرئيسية / بقلم / "دقائق قراءة",
  en-IN stays English by design. Add a dict entry when adding a language.
- **Render passes on post bodies** (JSON stays byte-faithful, D3):
  `correct_trial_claims()` rewrites false no-card boilerplate to the ~$1
  card-verification truth; `localize_trial_hrefs()` routes in-body /trial
  CTAs direct to the language-matched affiliate page (Bill-decided
  v0.3.2.0): en/en-IN → `highlevel-bootcamp`, es → `highlevel-bootcamp-es`
  (FirstPromoter tracker verified identical to EN), ar → `/ar/trial/` (GHL
  has no Arabic page), tags `utm_campaign=blog-trial-{en|es|in}`, downstream
  paid-link pass stamps `rel="nofollow sponsored"`;
  `unwrap_cross_silo_links()` enforces the Caleb Critical Rule strictly
  (Bill-decided v0.3.3.0) — any body link crossing a topic/language silo is
  unwrapped (words stay, link goes), matching BOTH `/blog/` links and
  custom-URL posts via `_SILO_BY_URL` (D13 — 14 links hid behind
  `/es/para/...`-style paths). EXCEPT: `FUNNEL_SINK_SLUGS` (money +
  pricing — conversion links, not topical ones) and series navigation
  (`_series_nav_exempt` — a hub and its parts link each other by canon);
  `inject_pillar_link()` weaves ONE in-prose link per post to the
  language-correct silo hub where a MULTI-WORD topic keyword naturally
  occurs as a WHOLE word (the word-boundary guard extends over simple
  plurals and never splits a word; single-word anchors are banned by the
  audit gate; no natural phrase → no link — the eyebrow covers structure
  regardless; non-EN hubs guarded by the MIN_LANG_TOPIC_POSTS bucket rule
  so no dead links). verify.py Check 4e scans rendered BODY prose for
  cross-silo links — the unwrap is fail-open, 4e is the alarm.
  `wrap_tables()` (v0.3.8.0) is the mobile-table backstop: any bare
  `<table>` in a rendered body gets a `.table-wrap` scroll container so wide
  tables scroll instead of clipping; tables already inside an overflow
  wrapper (assemble_spoke output) are left alone. Runs on post, authority,
  and category-pillar bodies. Gated by `scripts/test_wrap_tables.py`.
- **Localized trial landings:** `build.py`'s `LOCALIZED_LANDING_LANGS` builds
  `/{lang}/trial/` for es, in, and ar (Arabic copy native-reader reviewed,
  5 MSA corrections, v0.3.0.0). Only the `/trial/` variants are built —
  `/es/start` and `/in/start` stay retired 301s in `_redirects`; `/ar/start`
  never existed publicly and has no rule (don't add one).
- **Language hubs + category pages build themselves:** `/ar/` and
  `/ar/category/<topic>/` come from the standard language-hub loop
  (`build_language_topic_pages`, `min_posts=2`) — any language-topic bucket
  with 2+ posts gets a category page, singleton buckets get none. No
  Arabic-specific page code exists; growing a bucket past 1 post creates its
  category page automatically.
- **Language gate:** `_LANG_SLUG_MARKERS` in `build.py` carries Arabic markers
  (`arabic`, `mena`) so a future mistagged Arabic post fails the build instead
  of leaking into English hubs.

## Verified Facts (use ONLY these — invent nothing)
- Site: GlobalHighLevel.com — free GHL tutorials
- Podcast: "Go High Level" on Spotify
- Podcast stats: 380+ followers
- Top episode: "GoHighLevel Conversation AI Bot"
- Content: 909 published blog posts (English, India, Spanish, Arabic; was 27 post-prune 2026-06 — the full-restore sprint completed 2026-07-27 across v0.2.12.0–v0.3.0.0, with all 931 pruned URLs accounted for: 877 live pages + 54 twin 301s; +5 English AI-silo pages in v0.3.7.0) + 158 podcast episodes. NOTE: re-verify this count (`ls posts/*.json | wc -l`) before citing it — it moves as new posts publish.
- Offer: GoHighLevel 30-day FREE trial (double the standard 14-day trial)
- GHL starts at $97/month
- Affiliate link: https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12
- Spanish affiliate link: https://www.gohighlevel.com/highlevel-bootcamp-es?fp_ref=amplifi-technologies12 (the ONLY localized GHL affiliate page — 26-variant sweep 2026-07-27, all others 404; tracker verified identical to EN)
- Do NOT hardcode stream counts or follower numbers — they change. Check analytics if needed.

## DO NOT invent:
- Testimonials or reviews
- Income claims or revenue numbers
- Student counts or community sizes
- Awards, press mentions, certifications

## Screenshots — capture → redact → attest → publish (HARD RULE, v0.3.5.0)

No product screenshot reaches `images/` (and therefore the live site) without ALL of:
1. Raw capture in `captures/<lang>/` (gitignored, local-only) + an entry in the
   slug's `*.manifest.json` with `claim_supported` and `forbidden_overclaims`.
2. Solid-bar redaction (NOT blur) of: brand logo, sub-account name box, avatar,
   and any client/owner PII. Redacted file verified visually.
3. Bill's attestation recorded in the manifest (`attested: true`, `attested_by`,
   `attested_at`) BEFORE the image is copied into `images/`.
4. The published `<img>` alt/caption must match what the image actually shows
   (adversarial review caught a caption claiming a card not visible in frame).

Why written down: on 2026-07-28 two June captures were found LIVE un-redacted
(brand + sandbox identity visible) — published by a session that skipped this
flow because it existed only as convention, not doc. Fixed in v0.3.5.0.

## assemble_spoke.py — manifest-driven post authoring (es + en, v0.3.7.0)

`python3 assemble_spoke.py <manifest.json>` turns approved markdown drafts into
a post JSON. Originally es-only (LATAM spokes); since v0.3.7.0 it authors
English pages too: the manifest's `language` field keys the author bio, CTA
fallback label, and hub-link label, and `hub_title` overrides the hub anchor
text. Since v0.3.8.0 the EN author bio (`BIO_EN`) carries the full affiliate
disclosure (~40% recurring commission, plan-based not usage-based) — page-top
disclosure blockquotes were removed from the AI-silo drafts so pages open
with the answer; don't re-add them. Markdown support: simple pipe tables, GFM-style (scroll-wrapped;
escaped pipes unsupported — pinned in the tests), numbered lists with nested
bullets, and blockquotes (one containing `fp_ref=` becomes the CTA box;
others render as plain `<blockquote>`). URL hardening: unknown-scheme links
(`javascript:`, protocol-relative) are dropped to plain text and reported
(`dropped_links=` counter), hrefs are attribute-escaped. Gated by
`scripts/test_assemble_spoke.py`. **Provenance pattern:** each silo build
commits its draft sources + manifests under `plans/<silo>-<date>/` plus a fact
ledger (`plans/*-fact-ledger-*.md`) so every published dollar figure traces to
a dated source — keep doing this for future silos. Extended v0.3.9.0 to
single-post research rebuilds (`plans/es-timer-rebuild-2026-07-31/`) and to
non-numeric claims: any sentence attributed to "la documentación" needs a
ledger row naming the help article and the date it was fetched. A retired
claim also records the search that retired it, so the next session does not
re-litigate it from memory.

## Tests — pre-deploy gate suite

Run before any deploy (all must pass): `python3 -m pytest scripts/ -q` — covers
link audits (`test_audit_links`, `test_build_links`), capture pipeline
(`test_ghl_capture`), IndexNow submitter (`test_submit_indexnow`), restore
tooling (`test_restore_posts`), the spoke assembler (`test_assemble_spoke`,
39 tests, added v0.3.7.0), the table-wrap render pass (`test_wrap_tables`,
6 tests, added v0.3.8.0), the **trial-claim residual gate**
(`test_trial_claims_residual`, v0.3.4.0), and the **editorial-debt gate**
(`test_no_editorial_markers`: no bracketed editor notes in any post string
field — nested strings included, e.g. `tldr`/`translations` — no
empty/trailing heading sections — added v0.3.4.0 after the 2026-07-28 strip of
27 firehose-era es posts), the **retired-timer-premise gate**
(`test_timer_break_premise`: Spanish posts may not reassert that copying/cloning
a template breaks its countdown timer — an ungrounded claim removed in the
2026-07-31 rebuild), and the **FAQ schema migration**
(`test_fix_faq_schema`, 21 tests, added v0.3.10.0 — pins the CTA-swallow
boundary, the h3-headed FAQ sections, the 9 heading variants, the prefix-vs-
substring triviality guard, and the refuse-rather-than-guess paths), and the
**undisclosed zero-cost claim gate** (`test_zero_cost_claims_disclosed`,
4 tests, added v0.3.11.0 — the implicit sibling of the trial-claim residual
gate: a bare "$0 to start" with no `~$1` card-verification hold within 200
chars makes the same promise as "no credit card" without using any word that
gate matches. Reads `$` as literal, `&#36;`, or `&dollar;`, and whitespace as
`&nbsp;`. A cancellation promise is deliberately NOT accepted as a cost
disclosure. Carries an `ALLOWLIST` for honest quotation), and the
**hub-title gate** (`test_hub_titles`, 11 tests, added v0.3.12.0, Spanish added
v0.3.13.0 — covers `hub_title_for()`, which gives a language hub a `<title>`
worth clicking and keeps paginated hub titles distinct. Pins both edges: the
overrides fire for `en-IN` and `es`, and stay quiet for `ar`/`en`/`fr`/`pt`.
For `en-IN` it pins that the post count is interpolated rather than literal and
that pages 2+ drop the count instead of claiming the whole inventory. It also
pins that no hub title emits a bare `&`, and that a Spanish hub paginates in
Spanish (`Página N`, not `Page N`). **Length is asserted at the PRODUCTION count
and in UTF-8 BYTES** — accented characters cost two bytes each, so a
character-length check passes while the real SERP title overflows.
Paginated titles are deliberately exempt from the page-1 byte budget: hub
pagination is not a ranking target, so the requirement there is distinct and
honest, not short.

**The Spanish title carries NO count on any page, and that is deliberate — do
not "helpfully" restore it** (`test_spanish_title_carries_no_count_at_all`,
v0.3.14.0). `/es/` page 1 is a curated hub that renders no cards, and
`build_language_hub` still slices `lang_posts[0:18]` for it and then discards
those cards, so the numbered path reaches **231 of 249** and the 18 newest
Spanish posts sit outside it. Any number on that page promises a listing the
page cannot deliver. v0.3.13.0 shipped "249 Guías Paso a Paso"; a v0.3.14.0
draft restored "249 Guías y Precios" arguing the new pagination made it honest,
and Codex refuted it — *"249 is not defensible unless page 1 actually links a
complete 249-item path."* Restore the count only after closing the 18-post hole
(filed as a P2 in `TODOS.md`, with both closure options costed). `/in/` and
`/ar/` keep their counts: their page 1 renders cards and links every page, so
theirs are honest).

Also run the **/es/ hub pagination gate** (`test_es_hub_pagination`, 10 tests,
added v0.3.14.0). `/es/` page 1 is hand-authored and had emitted no pagination
at all since v0.2.0.0, leaving `/es/page/2..14/` with zero inbound links and no
sitemap entry — 13 indexable pages reachable only by typing the URL. The gate
pins that `es_library_block()` fires when there are pages, stays empty when
there are none, embeds the caller's `pag_html` verbatim rather than rebuilding
it, and states no count or completeness wording (`todas`, `completa`).

**These tests assert against RENDERED HTML, not helper output** — a technique
new to this repo in v0.3.14.0 and worth reusing. `build.py` exposes `PUBLIC_DIR`
as a module-level constant that `build_language_hub()` and `write()` read at
call time, so a test can `monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)`,
call the real builder with synthetic posts (`post_lang()` reads `post["language"]`
directly, so `{"language": "es"}` is enough), and read the pages it produces.
Costs about 0.2s per test. The first draft pinned the wiring with a
source-string assertion instead; Codex flagged that it would pass on a comment,
a non-f-string body, or an assigned-then-overwritten variable. **If a gate can
only fail when a helper's text changes, it is not guarding the page.**
Also run the **title-length gate** (`scripts/test_title_length.py`, 6 tests,
added v0.3.15.0) — see the title rule immediately below, which it enforces.
Then `python3 build.py` and `python3 verify.py`.

## SERP titles — 60 characters, and the brand is conditional (v0.3.15.0)

**Every `<title>` must go through `compose_title()` (`build.py`). Never write
`f"{title} | {SITE_NAME}"` at a call site.** That was the old pattern at ten
call sites plus a separate page template, and it put the 20-character publisher
name on 973 of 980 pages — pushing the median title to 83 characters when Caleb
Ulku's non-local canon (and roughly Google's truncation point) is **50-60
characters**. 95% of the site rendered a title too long to display in full.

`compose_title()` appends `" | Global High Level"` only when the result still
fits 60 characters — i.e. on any base title of **40 characters or fewer**
(60 minus the 20-character suffix). That is **44 indexable pages**: blog
pagination (`Page 2` says nothing on its own), category pages, two short posts,
and the `/es/` and `/ar/` hubs. Plus `404.html`, which is `noindex` and so sits
outside the gate — 45 branded titles in the built tree, 44 of them indexable.
Everywhere else the page keeps its own words.

**Do not restate that cohort from memory.** An earlier draft of the docstring
called it "all `/page/N/` pagination", drawn from the shortest few entries of a
sorted list; it was wrong for 16 of the 44. A later draft said 44 across the
whole tree, having counted only `index.html`. Both were caught in review. Count
it when you need it.

Three things to know before touching this:

- **A green build does NOT mean titles are compliant.** 580 pages still exceed
  60 characters on their own words (median 68). Check 7 is a **ratchet**: the
  count may shrink, never grow. Failing outright would block every build until
  hundreds of pages of copy work landed, and the gate would get deleted instead.
  Lower `TITLE_OVERLONG_BASELINE` in `verify.py` as titles land; the check prints
  the new number to use and the constant carries its own history. Tracked as a
  P2 in `TODOS.md`.
- **Shortening a title changes the visible page.** A post's `title` drives BOTH
  `<title>` and the `<h1 class="post-title">` (`seoTitle` is only a fallback, not
  an override). Title rewrites are copy work, not a mechanical pass.
- **`noindex` pages are exempt, deliberately.** A page excluded from search has
  no SERP title to budget, and without the exemption a future short `noindex`
  page (a `/thanks/` titled "Thanks") would trip the invariant for nothing. The
  consequence: `404.html`'s title is composed correctly but is **not**
  gate-protected — re-hardcoding its suffix would not fail the build. That is
  consistency hygiene, not an enforced invariant. It is not a hole to "fix".

### Rewriting a title? Three rules, learned the hard way (v0.3.16.0)

**1. PRIORITISE BY BING, NOT GOOGLE.** This decides whether the work is worth
doing at all, and the two engines give opposite answers for this site. Measured
2026-08-25:

| | Google (90d) | Bing (~75d feed) |
|---|---|---|
| impressions | 1,524 | **10,356** |
| clicks | **5** | **152** |
| URLs known | 203 of 927 | — |
| the overlong pages | 499 impr, **0 clicks** | 1,278 impr, **45 clicks** at pos 3-6 |

Ranked by Google, rewriting titles looks worthless and the honest advice is
don't bother. Ranked by Bing, the top 10 were worth roughly +35 clicks per
window, about 23% of all site Bing clicks. **A percentage of pages is not a
percentage of traffic, and neither means anything until you name the engine.**
Method: `python3 scripts/pull-bing.py --property ghl --top 200`, join
`top_pages` against built `<title>` lengths, rank by
`impressions * (target_ctr - current_ctr)`. Note `pull-bing.py`'s
`live_payload()` sums the whole feed with no date filter, so its totals are
~75 days, not 28.

**2. Check `_redirects` before dropping ANY term from a title.** The LATAM page
has **14 URLs 301'ing into it** from `vs alternativas` / `vs herramientas
locales` sources — it is the consolidation target for a whole cluster. A first
draft dropped "Herramientas Locales" from its title and would have discarded the
topical match those 14 redirects are pointing at. Adversarial review caught it.
A title is not just a snippet; on a consolidation target it is the thing that
tells the engine the redirected pages' topic still lives here.

**3. Edit post titles BYTE-FAITHFULLY.** Do NOT `json.load` a post and
`json.dumps` it back — that re-escapes the entire file, and on one post it
rewrote the whole `html_content` blob (semantically identical, but a ten-line
title change became an unreviewable diff). Read the raw text, detect whether the
file uses `\u` escapes, encode just the title value the same way, and do a
single string replacement. This repo's doctrine is that post JSON stays
byte-faithful; a title PR should be exactly one changed line per file.

**Two budgets in two units, on purpose-ish.** This gate measures CHARACTERS
(<= 60). `scripts/test_hub_titles.py` measures UTF-8 BYTES (<= 75), because
accented characters cost two bytes — `/es/` is 59 characters but 61 bytes. They
do not disagree on any current page. Both are proxies; the real constraint is
pixel width, which neither models. Filed as a P3 in `TODOS.md` rather than
reconciled, so don't assume one of them is a bug.

**Writing a content gate? Match phrases, not meaning — and pin BOTH edges.**
`test_timer_break_premise` first tried to infer the *claim* (timer noun + copy
verb + breakage verb co-occurring in a window, minus a hedge list). Three review
passes each found a fresh hole, alternating sides: a window-global hedge list let
one ordinary word disarm it; tightening the hedge made benign prose fire,
including that post's own Paso 2, one word from blocking every deploy; the
copy/break distance was bounded while the distance to the timer noun never was.
It now matches the retired phrasings themselves — each names the timer as the
thing that fails, so there is no window and nothing to bypass by adding a word.
Low recall by construction; novel phrasing is the reviewer's job. Its test keeps
a `retired` group (fires, or the gate is decorative) AND a `grounded` group
(never fires, or the gate blocks every deploy) — a gate tested on only one edge
is half-tested. Cost of a false positive here is "nobody can deploy", so bias to
precision.

## Canonical in-body trial CTA block (added v0.3.4.0)

When a post needs a closing trial CTA in stored JSON, copy this block VERBATIM
(do not mint a new variant — the corpus already has ~18 divergent one-off
callouts; this is the canonical one). The href stays `globalhighlevel.com/trial`:
`localize_trial_hrefs()` routes it per language and `nofollow_affiliate_links()`
stamps rel at render. NEVER write a "no credit card" claim — the truthful line
is "acceso completo, cancela cuando quieras":

```html
<p style="background:#fef3c7;border-left:4px solid #f59e0b;padding:12px 16px;border-radius:4px;margin-top:20px;"><strong>👉 Empieza ahora:</strong> Prueba GoHighLevel <strong>GRATIS por 30 días</strong> — acceso completo, cancela cuando quieras. <a href="https://globalhighlevel.com/trial" target="_blank">Acceder a prueba gratis →</a></p>
```
