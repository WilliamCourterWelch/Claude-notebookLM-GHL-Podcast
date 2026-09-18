# HAVE vs NEED — Global HighLevel affiliate site

Date: 2026-09-10
Scope: English-first cash this sprint. Spanish/LATAM is phase 2, not a build target here.
Affiliate context (owner, not invented analytics): ~$700–900/mo, never broke $1k on clicks; `fp_ref=amplifi-technologies12`; content stagnant ~3–4 months; Google weak, Bing/AI stronger.

Sibling `WilliamCourterWelch/globalhighlevel-pillar-system` PR #3 (`plans/en-ia-autoplan-2026-09-10.md`): **404 / inaccessible**. This file does not pretend to have read it.

Do not invent new traffic or revenue numbers. Where a figure appears, it is from this repo's changelog/TODOS (already measured in-session on those dates) or from the owner.

---

## HAVE — what exists and is actually strong

### Conversion plumbing
- One canonical affiliate URL, asserted at build time (`fp_ref` required, `utm_campaign` must not be pre-baked, ES bootcamp derived by string replace and asserted unequal).
- Nav CTA on every page is already a **direct bootcamp** click (`nofollow noopener`), language-aware.
- Post template CTA #3 is already a **direct bootcamp** click with `utm_campaign={slug}`.
- EN money page is a real sales page: 30 vs 14, setup walkthrough, bootcamp section, coupon-truth, annual ~17%, seasonal, Extendly, FAQ. Sink so it does not leak equity. Snippet rewritten 2026-08-29 so it stops turning discount searchers away.
- `/trial/` is a clean podcast attribution URL (`noindex` + `Disallow`). Do not unblock it.
- Paid-link backstop: zero followed `fp_ref` anchors sitewide (`nofollow_affiliate_links`).
- Trial-claim residual gate + zero-cost disclosure gate + FAQ sync gate. The site has been burned by false "no credit card" copy and will fail deploy if it returns.

### IA that already shipped (EN)
- 5 topic hubs, language as a separate axis, Caleb silo isolation, EN pillars living **on** `/category/{topic}/`.
- Homepage is a brand hub with a money-page guidecard and five cluster links, not a firehose dump.
- 927 sitemap URLs match built indexable pages. Redirect/sitemap parity is gated (`verify.py` 5–6).
- Restore sprint accounted for the prune: 909 live posts, twin 301s, old taxonomy redirected.

### Quality / ops
- Adversarial review culture (changelog is full of Codex catching overclaims). Pre-deploy: `pytest scripts/`, `build.py`, `verify.py`.
- Bing-first title work already landed the 10 highest-value overlong titles (v0.3.16.0). Ratchet at 580 remaining.
- GA4 + Clarity on every page. IndexNow key live.
- `assemble_spoke.py` + fact ledgers for honest new pages (AI silo, ES timer rebuild).

### Distribution that is not Google
- `llms.txt`, AI crawlers allowed including `/trial/`. Changelog already treats Copilot-shaped queries as citation surface, not title-rewrite surface.
- 158-episode podcast still points at `/trial/`.

---

## HAVE — real, but not the cash bottleneck

- 909 URLs. Most are firehose how-tos. EN median ~1,450 words. They exist; they are not a content machine.
- 249 Spanish pages. Some convert (ES pricing 3.02% CTR on 298 Bing impressions per TODOS 2026-08-29 — **that figure is historical, not re-pulled today**). ES is still phase 2.
- 145 India pages. Body-dead-end heavy. Hub exists.
- 8 Arabic stubs. RTL hub exists so the language picker is not a 404. Not a market.

---

## NEED — gaps that move affiliate cash

Priorities: **P0** this sprint after human taste pass · **P1** next · **P2** later / needs a Bill one-way door. No mass deletes.

### P0 — smallest CTA + measurement win

The money is clicks on `fp_ref=amplifi-technologies12` that become trials. The site already emits those clicks. It does not tell us **which slot** earned them, and docs disagree with the code.

| Gap | Evidence | Need |
|---|---|---|
| Event name drift | `CLAUDE.md` says `cta_click` / `affiliate_click`. Listener fires `ghl_click` (fp_ref) and `cta_click` (everything else). | One outbound event, e.g. `affiliate_outbound`, with `cta_slot` = `nav` \| `cta3` \| `tldr` \| `body` \| `trial_landing` \| `money_page`. Keep old events for a window or map them. |
| Slot-blind UTMs | Nav CTA uses the base affiliate URL (no `utm_campaign` beyond what's in `AFFILIATE`). CTA #3 uses `utm_campaign={slug}`. Pricing body CTAs already have `utm_content=tier_*` (v0.3.11.0). | First **read** existing GA4. If still blind: `affiliate_href()` helper (not `affiliate_for()`) stamps `utm_content` on template hrefs only. Never bake `utm_content` into `AFFILIATE`. Listener copies it to `cta_slot` via `URLSearchParams`. |
| Internal hop tax unmeasured | Byline + mid CTAs send people to the money page `rel=nofollow` instead of bootcamp. If they bounce, that is a lost click we currently file as `cta_click` on `/blog/...` not as a failed outbound. | Report hop vs outbound. Do **not** blindly retarget every mid-CTA at bootcamp without a taste pass on the money page (the hop is the sales letter). |
| `pull-bing.py` missing from this repo | Cited as the method in CLAUDE.md / TODOS. Glob finds zero files. | Either restore the script into `globalhighlevel-site/scripts/` or document the off-repo path. Cannot run a measurement loop from this checkout. |
| No GitHub Actions | `.github/` absent; weekly-analytics / weekly-seo-report / weekly-content-builder were deleted with the pipeline. | A **read-only** measurement workflow is a later P1. P0 is "we can see slot-level clicks in GA4 after one ship." |
| Docs vs code on `affiliate_click` | Contributors will add the wrong event name. | Patch CLAUDE.md in the same PR as the listener. |

Out of P0: redesign, new hubs, ES builds, widget, deleting thin AR pages, rewriting 580 titles.

### P0-adjacent (human taste, then maybe ship)

Bill looks at these in a browser **before** we change copy:

1. EN homepage guidecard + nav CTA + money page above-the-fold. Is the bootcamp promise visible without scrolling? (Money page has a bootcamp `<div class="bootcamp-section">` mid-page, not in the first amber box.)
2. `/services/` vs trial. Should the footer/nav mention services at all? It is the only indexable competing offer.

If taste says "bootcamp is buried," the smallest copy win is a **one-line bootcamp mention in the first money-page CTA box**, not a new page. That is still a content edit on a sink; run the SEO deploy gate if it ships.

### P1 — measurement loop + EN cluster hygiene (no deletes)

| Gap | Need |
|---|---|
| Bing recrawl loop | Restore or rewrite `pull-bing.py`. Re-pull ~30 days after the v0.3.16.1 snippet change and compare money-page CTR to the 0.37% baseline **as documented**, not as a new claim. |
| Footer missing Agency hub | Add the fifth cluster link. One `base_html` list. Graph fix, not a redesign. |
| Dead Topics dropdown | Either render it or delete `dropdown_links`. Current nav cannot reach hubs without homepage/footer. |
| Plan-by-plan trial section on the money page | TODOS already specified: 130 Bing impressions, 0 clicks, queries that name Agency Pro / Unlimited / SaaS Mode trial. A **section**, not a new URL. |
| AI-pricing 2025 leftovers vs 2026 AI silo | Internally link 2025 posts to the 2026 silo pages (same-silo only) or 301 after a human look. Do not auto-delete. |
| Widget (Conversation AI vs Agent Studio) | TODOS P1, Bill-open questions (calendar, sitewide vs money/AI only, cost cap). Dogfood, second conversion path. Not the first ship. |
| `tldr` on 1/909 posts | Answer-first is a money-page feature only. Rolling TL;DR sitewide is a content program, not a P0. |

### P1 — content machine (restart, don't revive the corpse)

The retired pipeline must stay dead. Need a **thin** machine:

- Topic source: Bing gaps (`GetPageQueryStats` on the money + pricing URLs) + GHL changelog, not 20 NotebookLM episodes/night.
- Authoring: `assemble_spoke.py` + fact ledger (already the pattern).
- Cadence: few EN spokes/month that support the money/pricing/AI hubs, not 35 posts/cycle.
- Trigger: GitHub Actions only (`memory/project_automation_surface.md` still applies). No new claude.ai `/schedule`, no VPS cron for content.

Without this, the catalog ages in place (last new publish 2026-07-29). Stagnation is real. Volume is not the fix; the firehose is what created the fat Agency cluster.

### P2 — later / one-way doors / ES phase

| Gap | Why P2 |
|---|---|
| Spanish/LATAM hub, qué-es consolidation (9 URLs), ES promo page, `/es/` 18-post hole | Owner: phase 2. Consolidation 301s live URLs. ES pricing already outperforms EN money CTR historically — don't idle-hand it, don't build it this sprint. |
| `/es/start/` → pricing vs EN `/start/` → trial | Asymmetric. Human call. |
| Arabic stubs (~75 word median) | Don't delete without a 404 plan. Don't expand. |
| 580 overlong titles | Ratchet exists. Bing-pick the next 10 if a pull shows leftover CTR. |
| Title `&` escaping (63 titles) | P2 in TODOS. Not cash. |
| GHL conversation widget cost model | Unbounded public traffic vs 1,000-response Growth cap. |
| Zero-cost gate only in pytest, not `verify.py` | Fail-open if someone skips pytest. Fold in when touching gates. |
| Mass page deletes / "thin content purge" | Explicitly out. Restore sprint just put 877 URLs back. |

---

## Mapping HAVE → NEED (affiliate cash)

```
HAVE: nav + CTA#3 already hit bootcamp with fp_ref
NEED: know which slot, on which language, produced the click  → P0 measurement

HAVE: money page is the SEO trial/discount URL and a sink
NEED: bootcamp visible in first CTA (taste) + plan-by-plan section (P1 copy)

HAVE: 5 EN hubs + silo gates
NEED: footer/nav actually expose all 5; don't rebuild IA  → P1 one-liners

HAVE: Bing-first culture, no pull script in repo, no Actions
NEED: restore the measurement tool; later a read-only Action  → P0/P1

HAVE: assemble_spoke + fact ledgers
NEED: a tiny editorial cadence, not pipeline revival  → P1

HAVE: 249 ES pages
NEED: leave them alone this sprint  → P2 / phase 2
```

---

## What we are not calling a NEED

- A sixth topic hub.
- Unblocking `/trial/`.
- Pointing new in-post CTAs at `/start/` or `/coupon/`.
- Recreating repo-root `posts/` or the NotebookLM pipeline.
- Using headed Playwright as the IA method.
- Inventing "if we add N pages we will hit $X."
