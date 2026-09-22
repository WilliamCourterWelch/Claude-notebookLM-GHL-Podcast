# LATAM hub `/es/gohighlevel-latam/` — ship plan (taste hold)

**Status: AWAITING WILLIAM TASTE. Do not land, merge, or canary.**

Review label: plan only. Outside adversarial review was not run. No Codex CLI. Not `CODEX_PASS`. Dual-Cursor is the next wave after taste GO.

## URL, title, H1

| | |
|---|---|
| URL | `https://globalhighlevel.com/es/gohighlevel-latam/` |
| File | `globalhighlevel-site/posts/hub-es-gohighlevel-latam.json` |
| `url_path` | `/es/gohighlevel-latam/` |
| `language` | `es` |
| `topic` | `Payments & Pricing` |
| Title / H1 | `GoHighLevel en Latinoamérica: pagos` (35 characters) |
| Rendered `<title>` | brand suffix fits: `GoHighLevel en Latinoamérica: pagos \| Global High Level` |
| Description | 150 characters. Names MercadoPago, the two flows, and the ~$1 card check. |

The June publish draft's H1 is `GoHighLevel en Latinoamérica: la guía honesta de pagos para agencias (2026)`. That string is already the live H1 of `/blog/gohighlevel-latam-pagos-agencias/`. Reusing it here would be a second page with the same headline, and it is over the 60-character title ratchet (`verify.py` Check 7 fails if the over-long count grows). The short H1 is the draft. William can lengthen it only if he also lowers some other title or accepts a ratchet bump.

## What this page is

The official outline (`hub-es-gohighlevel-latam-outline`, 2026-05-11) assigns this URL the LATAM payment map: Flujo A (SaaS Mode, agency bills its clients) versus Flujo B (the sub-account bills the end customer), MercadoPago in 7 countries, a country table, and routing onward.

The body is the 2026-06-03 publish draft, not a new 8,000-word article. The outline's 8,000-word tally assumed country spokes, a Stripe Atlas spoke, screenshots, and an FAQ expansion this repo does not have. Those URLs 404. They are not linked.

Measured draft: about 2,500 words. The publish draft itself was about 1,800 words and is already the live pagos page. This draft adds the July 2026 changelog correction, drops the unsourced PagBank claim, and softens Stripe Atlas.

## Live URLs this page links

All checked 200 on 2026-09-22 except the SaaS Mode help article, which 404s and is not linked.

| Role | URL |
|---|---|
| Precios | `/blog/gohighlevel-precios-planes-2026-guia-completa/` |
| Pagos agencias (same topic, already live) | `/blog/gohighlevel-latam-pagos-agencias/` |
| MercadoPago hub | `/es/mercadopago-gohighlevel/` |
| México | `/blog/gohighlevel-mercadopago-mexico/` |
| Qué es | `/blog/que-es-gohighlevel-mejor-alternativa-herramientas-locales-latinoamerica/` |
| `/es/` entry | cluster "Pagos y Precios" links this hub (`build.py`) |

Qué es is topic `Agency, White-Label & SaaS`. A followed link from this Payments page is cross-silo. Build on 2026-09-22 confirmed the unwrap: the words stay in `public/es/gohighlevel-latam/index.html`, the href does not. Precios survives because it is a funnel sink. Pagos, the MercadoPago hub, and México stay linked (same silo).

Not linked, because they are not built: `/es-mx/`, `/es-ar/`, `/es-co/`, `/pt-br/`, `/es/saas-mode-stripe-atlas/`.

## CTA

One canonical trial block, href `https://globalhighlevel.com/trial`. Render routes Spanish to `highlevel-bootcamp-es` with `fp_ref=amplifi-technologies12`. Prose next to it: 30 days, card required, ~$1 verification hold, subscription not charged during the trial, SMS and calls can cost extra. No "sin tarjeta" trial claim.

## Hreflang

The outline's `es-419` / `es-MX` / `es-AR` / `es-CO` / `pt-BR` block points at pages that do not exist. This post has no `translations` map, so the builder emits no hreflang alternates. That is the site rule: do not advertise 404s.

`/es/` page 1 is a hand-authored hub. The new page is a post, so it shows up in `/es/page/N/` cards and the payments category the same way `/es/mercadopago-gohighlevel/` does. Page 1 of `/es/` now also links the hub from the Pagos cluster.

## Critique gate (2026-06-03, NEEDS-CLEANUP) — what this draft does

- Stripe Atlas is "un camino práctico", not the required path, and not an official HighLevel or Stripe recommendation. No $500 fee (that number is not in the publish draft).
- PagBank / PIX / Boleto as a native GoHighLevel integration is removed. The July 2026 changelog does not name them.
- Chile Stripe is "vista previa", not a hard no, per the Stripe-in-LATAM topic.
- Vote count is "más de 300", linked to the ideas thread. The June draft said 303. The June changelog on this site moved to "más de 300" because the count had already moved. The live pagos JSON still says 303. This new page uses the durable wording.
- Sandoval and Latorre stay as named forum quotes with the ideas thread. They are not a Caso Real.
- No screenshots. None of the outline's captures are attested in this repo.
- The SaaS Mode help URL in the June draft (`155000003670`) returns 404. It is not linked. The four-processor list is carried by the Spanish banner quote.
- July 28 canonical source says Mercado Pago is compatible with channels including "SaaS mode". The June draft says MercadoPago does not do Flujo A. The page states both and leaves the reading explicit: Flujo B is MercadoPago; Flujo A is still the four-processor list. That sentence is the main taste item.

## Not in this PR

- No rewrite of the 28 Spanish posts.
- No new country spokes.
- No 301 from `/blog/gohighlevel-latam-pagos-agencias/` to this URL. That is a taste call. Landing both without a canonical decision leaves two pages on the same topic.
- No English, Desktop, or India edits.
- No VERSION bump, no CHANGELOG, no `seo-cooldown.json`. Those are land steps.
- Frozen English paths were not touched.

## Acceptance checks before any land

From `globalhighlevel-site/`:

1. `python3 -m pytest scripts/ -q`
2. `python3 build.py`
3. `python3 verify.py`
4. Built file `public/es/gohighlevel-latam/index.html` exists.
5. Built HTML contains `fp_ref=amplifi-technologies12` and `highlevel-bootcamp-es`.
6. Built HTML does not contain `sin tarjeta` as a trial claim.
7. Grep the built HTML for `/blog/que-es-gohighlevel-mejor-alternativa-herramientas-locales-latinoamerica/` and record whether the silo pass unwrapped it.
8. Confirm `/es/` page 1 links `/es/gohighlevel-latam/`.

## GSTACK REVIEW REPORT

Primary pass only. Outside voice: not run (deferred Dual-Cursor, no Codex).

Taste held for William:

1. Overlap with the live pagos page. Same research, new URL, no 301.
2. Short H1 versus the June headline.
3. The "SaaS mode" changelog sentence versus "MercadoPago is not Flujo A".
4. "más de 300" versus the June draft's 303.
