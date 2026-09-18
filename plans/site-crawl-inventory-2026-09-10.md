# Site crawl inventory — globalhighlevel.com

Date: 2026-09-10
Repo: WilliamCourterWelch/Claude-notebookLM-GHL-Podcast @ `0.3.17.0` (`81e987cf`)
Method: source inventory (909 `globalhighlevel-site/posts/*.json` + `build.py` helpers), live `curl` of `sitemap.xml` and key HTML. No headed browser, no Playwright crawl.
Sibling pillar-system PR: **inaccessible** (`WilliamCourterWelch/globalhighlevel-pillar-system` 404 via `gh`). Inventory is this site repo only.

Live checks (2026-09-10):

| URL | HTTP | Notes |
|---|---|---|
| `https://globalhighlevel.com/sitemap.xml` | 200 | 927 `<loc>`s, 200,698 bytes |
| `/` `/es/` `/in/` `/ar/` | 200 | language hubs |
| `/trial/` | 200 | `noindex, follow` |
| `/about/` `/services/` | 200 | |
| money page + EN pricing | 200 | |
| `/start/` `/coupon/` `/free-trial/` | 301 | → money page |
| `/es/start/` | 301 | → ES pricing guide (not the ES trial blog) |

---

## What the site is

Static affiliate tutorial site. Cloudflare Pages builds from `globalhighlevel-site/` via `python3 build.py`. The 25-hour NotebookLM → Transistor → blog pipeline is **retired** (2026-06-11). Canonical post store is `globalhighlevel-site/posts/`. Podcast catalog is `globalhighlevel-site/data/published.json` (158 episodes). Affiliate conversion URL:

`https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12`

Spanish lands on `/highlevel-bootcamp-es?` with the same `fp_ref`.

---

## How pages are generated

Single generator: `globalhighlevel-site/build.py`. `main()`:

1. Wipes `public/` (gitignored), copies `robots.txt`, `_redirects`, `images/`, IndexNow key.
2. Loads `posts/*.json` + `data/published.json` (podcast metadata merged onto matching posts).
3. EN hub pillars (`isPillar` + `language=en`) are **not** built at `/blog/{slug}/`. Their `/blog/` URL is 301'd onto `/category/{topic}/`.
4. Remaining posts: `build_authority_page` if series (`is_series_hub` or `url_path` starts `/es/para/` or `/for/`), else `build_post_page`.
5. EN homepage `build_index` at `/` + `/page/{N}/` (18 per page).
6. EN category hubs `build_category_pages` (min 2 EN posts).
7. Language hubs + language-topic pages (`min_posts=2`).
8. `/trial/` + localized `/es|in|ar/trial/`. `/start/` and `/coupon/` are **not** built.
9. `/services/`, `/about/`, `llms.txt`, `sitemap.xml`, `404.html`.
10. Shadow-prune: any `_redirects` source that matches a built page is dropped from the **deployed** copy (Cloudflare redirects beat static files).
11. Blocking: tracking-tag assert + `scripts/audit_links.py`.

Post JSON is treated as byte-faithful. Render passes mutate HTML only: trial-claim correction, `localize_trial_hrefs`, `nofollow_affiliate_links`, cross-silo unwrap, table wrap, pillar-link inject, in-silo inject, hub-link block, circle nav, related cards, template CTAs.

Authoring path for new spokes: `assemble_spoke.py <manifest.json>` (es + en since v0.3.7.0). Provenance lives under `globalhighlevel-site/plans/`.

---

## Counts that match live sitemap

| Source | Count |
|---|---|
| Post JSON files | 909 |
| EN hub pillars (blog URL 301 → category hub, not a built `/blog/` page) | 5 |
| Built post pages | 904 |
| Sitemap `<loc>` | **927** |

Sitemap identity (live):

```
904 post pages
+ 1 home + 1 /about/ + 1 /services/
+ 5 EN category hubs
+ 3 language hubs (/es/ /in/ /ar/)
+ 5 ES category + 5 IN category + 2 AR category
= 927
```

**Not in sitemap (by design):** `/trial/` and localized trial landings (`noindex` / attribution); all `/page/N/` pagination; `/404.html`; `llms.txt`; IndexNow key file.

**Expected built tree (including non-sitemapped pages):** 984 paths (adds EN `/page/2..29/`, `/es/page/2..14/`, `/in/page/2..9/`, four trial landings, 404, robots, sitemap, llms.txt).

---

## Languages

| Code | Prefix | Posts | Hub | Hub page 1 | Paginated | Topic category pages |
|---|---|---|---|---|---|---|
| `en` | *(none)* | 507 | `/` | Editorial homepage (hero + money-page guidecard + 5 topic clusters + ES banner) | `/page/2..29/` (29 pages) | 5 EN hubs |
| `es` | `/es` | 249 | `/es/` | **Curated brand hub, zero post cards** (deliberate since v0.2.0.0) | `/es/page/2..14/` (14 pages; strip added v0.3.14.0) | 5 |
| `en-IN` | `/in` | 145 | `/in/` | Card grid, honest count in title | `/in/page/2..9/` | 5 |
| `ar` | `/ar` | 8 | `/ar/` | Card grid, RTL (`dir=rtl`) | 1 page | 2 (CRM, Agency) |

`/es/` page 1 still slices `lang_posts[0:18]` and throws the cards away, so the numbered path lists **231 of 249**. The 18 newest Spanish posts are on `/es/category/` and in the sitemap, not on the numbered hub path. No `/es/` surface may state a corpus count.

---

## Topics (5 hubs, not mixed with language)

From `globalhighlevel-site/categories.json` (the live 5-hub taxonomy; repo-root `categories.json` is the old 10-topic leftover and is **not** what `build.py` reads).

| Topic | EN | ES | IN | AR | Total | EN hub URL |
|---|---:|---:|---:|---:|---:|---|
| Agency, White-Label & SaaS | 178 | 105 | 54 | 4 | 341 | `/category/agency-white-label-saas/` |
| CRM & Communication | 130 | 60 | 35 | 2 | 227 | `/category/crm-communication/` |
| AI Receptionist & Lead Capture | 111 | 62 | 29 | 1 | 203 | `/category/ai-receptionist-lead-capture/` |
| Payments & Pricing | 58 | 20 | 19 | 1 | 98 | `/category/payments-pricing/` |
| Sites, Funnels & Reputation | 30 | 2 | 8 | 0 | 40 | `/category/sites-funnels-reputation/` |
| **Total** | **507** | **249** | **145** | **8** | **909** | |

AR AI and AR Payments buckets have 1 post each → **no** `/ar/category/` page (`MIN_LANG_TOPIC_POSTS=2`). ES Sites is exactly 2 → a thin category page exists.

Repo-root `categories.json` still lists 10 topics including language-as-topic (`gohighlevel-india`, `gohighlevel-espanol`). Dead file. Do not use it.

---

## Route types / templates

| Template | Builder | Typical URL | Who gets it |
|---|---|---|---|
| `base_html` | wrap | every HTML page | nav + footer + GA4 `G-HYT0YKNGX2` + Clarity `wkeq0t21ww` + hreflang + inline CSS |
| Editorial homepage | `build_index` page 1 | `/` | EN only |
| Paginated index | `build_index` page 2+ | `/page/N/` | EN; **not sitemapped** |
| Blog post | `build_post_page` | `/blog/{slug}/` (or `url_path`) | default |
| Authority / series | `build_authority_page` | `/es/para/...`, future `/for/` | 2 live pages, both Spanish |
| EN category hub | `build_category_pages` | `/category/{topic}/` | 5 live; pillar body injected for EN pillars |
| Language hub | `build_language_hub` | `/es/` `/in/` `/ar/` | |
| Language topic | `build_language_topic_pages` | `/{lang}/category/{topic}/` | min 2 posts |
| Trial landing | `_build_affiliate_landing` | `/trial/` | `noindex`; podcast attribution |
| Localized trial | `_build_localized_affiliate_landing` | `/es/trial/` `/in/trial/` `/ar/trial/` | es/in campaign `podcast`; ar campaign `blog` |
| Services | `build_services_page` | `/services/` | Bill's $497/mo a-la-carte offer + GHL webhook form |
| About | `build_about_page` | `/about/` | E-E-A-T |
| 404 | `build_404` | `/404.html` | standalone, `noindex` |
| AI index | `build_llms_txt` | `/llms.txt` | capped lists per language |

EN pillars (blog URL 301 → hub):

| Pillar slug | Hub |
|---|---|
| `gohighlevel-ai-agents-automation-complete-guide` | `/category/ai-receptionist-lead-capture/` |
| `gohighlevel-crm-communication-complete-guide` | `/category/crm-communication/` |
| `gohighlevel-sites-funnels-reputation-complete-guide` | `/category/sites-funnels-reputation/` |
| `gohighlevel-payments-complete-guide` | `/category/payments-pricing/` |
| `gohighlevel-saas-mode-white-label-agency-guide` | `/category/agency-white-label-saas/` |

Custom `url_path` posts (3):

| URL | Role |
|---|---|
| `/es/mercadopago-gohighlevel/` | MercadoPago spoke |
| `/es/para/agencias-de-marketing/` | series hub |
| `/es/para/agencias-de-marketing/por-que-agencias-marketing-necesitan-crm-2026-parte-1/` | series part 1 |

Sink flag: `mvp_minimal_links: true` on **one** post, the EN money page `/blog/gohighlevel-free-trial-30-days-extended/`. `FUNNEL_SINK_SLUGS` is a wider set (trial + pricing in all 4 languages) used only to **allow inbound** cross-silo links, not to airtight the page.

Podcast: 490 of 909 posts carry `transistorEpisodeId` and embed Transistor. 158 episodes in the catalog. Spotify show: `https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV`.

---

## Conversion / money routes

| URL | Indexable | Role |
|---|---|---|
| `/blog/gohighlevel-free-trial-30-days-extended/` | yes | **EN money page.** Sink. 30-day trial + bootcamp + discount truth. Parallel of `/trial/`. |
| `/blog/gohighlevel-pricing-plans-2026-complete-guide/` | yes | EN pricing. Funnel-sink slug (inbound allowed). Not airtight. |
| `/blog/gohighlevel-prueba-gratis-30-dias-como-empezar/` | yes | ES trial blog |
| `/blog/gohighlevel-precios-planes-2026-guia-completa/` | yes | ES pricing. `/es/start/` 301s here. |
| `/blog/codigo-promocional-gohighlevel-2026-descuentos-reales/` | yes | ES standalone promo page (EN equivalent was 301'd into the money page) |
| `/blog/gohighlevel-free-trial-india-30-days-setup-guide/` | yes | IN trial |
| `/blog/gohighlevel-pricing-india-2026-rupees-complete-guide/` | yes | IN pricing |
| `/blog/gohighlevel-free-trial-arabic-30-days-guide/` | yes | AR trial (~297 words) |
| `/blog/gohighlevel-pricing-arabic-2026-complete-guide/` | yes | AR pricing (~299 words) |
| `/trial/` | **noindex** | Podcast / owned-media attribution. Disallow in `robots.txt`. Pitches GHL + Extendly. |
| `/es/trial/` `/in/trial/` `/ar/trial/` | built | Localized landings. `/ar/trial/` exists because GHL has no Arabic bootcamp page. |
| `/start/` `/coupon/` `/promo/` `/free-trial/` | 301 | → EN money page. Unblocked in robots so crawlers see the 301. |
| `/es/start/` | 301 | → ES **pricing**, not ES trial |
| `/in/start/` | 301 | → `/in/` |
| `/services/` | yes | Competing conversion: Bill's paid automation services, not the affiliate trial |

Nav CTA (every page): direct affiliate bootcamp URL, `rel=nofollow noopener`, language-aware (`-es` for Spanish). Label: "Start 30 Days Free" / "Prueba 30 días gratis" / "ابدأ 30 يوماً مجاناً".

Post template CTAs:

- CTA #1 byline: `rel=nofollow` to EN money page (skipped if `tldr` present). **Only 1 post has `tldr`** (the money page itself).
- Mid-article CTA: same, money page, `rel=nofollow`.
- CTA #3 end box: **direct affiliate** + `utm_campaign={slug}`.
- TL;DR CTA: direct affiliate + `utm_campaign={slug}_tldr` (money page only).

In-body `/trial` hrefs are rewritten at render by `localize_trial_hrefs` to the language bootcamp URL (ar → `/ar/trial/`).

---

## Nav / footer patterns

Desktop nav (`base_html`): logo (`/` always, `dir=ltr`) · Guides (`/#guides`, `/es/#guides`, `/in/`, `/ar/`) · Podcast (Spotify, new tab) · other live language hubs · amber nav-CTA (affiliate).

Mobile: hamburger checkbox + same set.

**Topics dropdown is dead code.** `dropdown_links` is built from live EN categories and never interpolated into the nav HTML. Topics are reachable from homepage clusters and the footer (and from post eyebrows / hub-link blocks).

Footer Topics (hardcoded 4 of 5 hubs):

- AI Receptionist & Lead Capture
- CRM & Communication
- Sites, Funnels & Reputation
- Payments & Pricing

**Missing from footer:** Agency, White-Label & SaaS (`/category/agency-white-label-saas/`) — the largest cluster (341 posts). Homepage clusters include all five.

Footer also: language hubs, affiliate disclosure, "Not affiliated with GoHighLevel LLC".

---

## Redirects and robots

- Source `_redirects`: 168 rules (slash and non-slash twins, old taxonomy, clone-pair consolidations, ES vs-alternativas cluster → `que-es-gohighlevel-mejor-alternativa-herramientas-locales-latinoamerica`).
- Build appends EN pillar `/blog/` → `/category/` 301s, then drops any rule whose source is a built page.
- `robots.txt`: `Disallow: /trial/` only. `/start/` and `/coupon/` deliberately allowed. AI crawlers (`GPTBot`, `ClaudeBot`, `Google-Extended`, `PerplexityBot`, `anthropic-ai`) `Allow: /`. Sitemap advertised.

---

## Content age (stagnation)

Publish dates on the 909 posts:

| Month | New posts |
|---|---:|
| 2026-03 | 441 |
| 2026-04 | 450 |
| 2026-06 | 3 |
| 2026-07 | 15 |

Newest `publishedAt`: **2026-07-29** (EN AI-silo pricing/review set). Newest `updatedAt`: **2026-08-20** (5 posts; money page + pricing copy). Pipeline retirement 2026-06-11 explains the cliff. July work is restore + hand-authored hubs/AI silo, not a restarted firehose.

Word-count shape (source HTML, tags stripped):

| Lang | n | p50 | mean | min | max |
|---|---:|---:|---:|---:|---:|
| en | 507 | 1455 | 1551 | 852 | 4539 |
| en-IN | 145 | 1296 | 1325 | 428 | 2115 |
| es | 249 | 639 | 753 | 312 | 5886 |
| ar | 8 | 75 | 135 | 51 | 299 |

Arabic pages are stubs. Spanish median is about half of English.

---

## Measurement already on the page

Every HTML page: GA4 config + click listener. `fp_ref=` → event `ghl_click`. `/trial`, `/start`, `/free-trial`, `.nav-cta`, `.btn-amber`, or `gohighlevel.com` without `fp_ref` → event `cta_click`. Microsoft Clarity on every page. IndexNow key hosted for Bing recrawl. `scripts/pull-bing.py` is **cited in CLAUDE.md / TODOS.md and is not in this repo**. No `.github/` workflows remain (deleted with the pipeline).

---

## What this inventory is not

- Not a traffic report. Bing/Google numbers cited elsewhere are from prior changelog/TODOS measurements, not re-pulled today.
- Not a rendered-HTML link audit. `verify.py` Check 4 is the live gate on built output; this file inventories routes from source + live sitemap.
- Not a recommendation to delete pages. Mass deletes are out of scope for this planning pass.
