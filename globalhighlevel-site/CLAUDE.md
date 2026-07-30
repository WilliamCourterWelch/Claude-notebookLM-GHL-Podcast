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
text. Markdown support: simple pipe tables, GFM-style (scroll-wrapped;
escaped pipes unsupported — pinned in the tests), numbered lists with nested
bullets, and blockquotes (one containing `fp_ref=` becomes the CTA box;
others render as plain `<blockquote>`). URL hardening: unknown-scheme links
(`javascript:`, protocol-relative) are dropped to plain text and reported
(`dropped_links=` counter), hrefs are attribute-escaped. Gated by
`scripts/test_assemble_spoke.py`. **Provenance pattern:** each silo build
commits its draft sources + manifests under `plans/<silo>-<date>/` plus a fact
ledger (`plans/*-fact-ledger-*.md`) so every published dollar figure traces to
a dated source — keep doing this for future silos.

## Tests — pre-deploy gate suite

Run before any deploy (all must pass): `python3 -m pytest scripts/ -q` — covers
link audits (`test_audit_links`, `test_build_links`), capture pipeline
(`test_ghl_capture`), IndexNow submitter (`test_submit_indexnow`), restore
tooling (`test_restore_posts`), the spoke assembler (`test_assemble_spoke`,
37 tests, added v0.3.7.0), the **trial-claim residual gate**
(`test_trial_claims_residual`, v0.3.4.0), and the **editorial-debt gate**
(`test_no_editorial_markers`: no bracketed editor notes in any post string
field — nested strings included, e.g. `tldr`/`translations` — no
empty/trailing heading sections — added v0.3.4.0 after the 2026-07-28 strip of
27 firehose-era es posts). Then `python3 build.py` and `python3 verify.py`.

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
