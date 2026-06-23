# GlobalHighLevel Recovery & Redesign — June 2026

Strategy work for recovering globalhighlevel.com after the April 24 2026 traffic cliff.
These are **planning artifacts** (not deployed — `build.py` only reads `posts/*.json` and `public/*.html`).

## The diagnosis
- **April 24, 2026:** search impressions fell ~97% overnight (1,569 → 43/day) and never recovered. ~4 Google clicks in the last 28 days.
- **Cause:** content-quality demotion, not a technical glitch. Homepage is indexed fine; the flagship pricing page is "crawled, currently not indexed" since April 23. The ~946-post auto-pipeline content was the problem; it's since been pruned to 15 posts / 26 URLs.
- **Reframe:** Google is the *smallest* channel now. Last 90 days: Direct ~703, Bing+Yahoo+DDG ~360 (not demoted), AI assistants ~118, Google ~122.

## The strategy
- **Service-led, Spanish-first.** Agency/white-label keyword demand is tiny (~1,110/mo). Service-business + the Spanish lane is where the volume is.
- **Spanish is the #1 lane:** "gohighlevel" ≈ 32,000/mo across MX (9,900) + ES (9,900) + CO (8,100) + AR (4,400), all KD 5–9. Confirmed CRM intent (not GHL Hoteles) via SERP. Monetizable slice = research intent (opiniones / precios / qué es) + the 30-day trial.
- **English homepage** targets "gohighlevel 30 day free trial" for the Direct audience.

## Files here
- `globalhighlevel-recovery-plan.html` — the full diagnosis + plan (visual).
- `globalhighlevel-keyword-map.html` — volume × difficulty opportunity map.
- `globalhighlevel-content-plan.html` — 12-move, 4-band page-by-page content plan.
- `globalhighlevel-homepage-draft.html` — English trial-homepage draft (v1).
- `keyword-data/` — raw DataForSEO pulls behind all of the above (GSC/GA4 numbers, universe + ranked + SERP). ~$1.30 total spend.

## P0 next steps
Spanish `/es/` trial homepage → Opiniones pillar (resume) → strengthen Precios → "¿Qué es?" explainer.
SERP-confirmed PAA to answer: ¿Qué es y para qué sirve? · ¿Cuánto cobra? · ¿Es gratuito o de pago? · ¿Es confiable? · ¿Quién está detrás?
