# TODOS

Backlog for globalhighlevel.com (static site + build pipeline). Source of truth
for the Bing-first recovery ship queue (eng review 2026-07-21, run
`20260721T205056Z-57180`) plus follow-ups. Priorities: P0 (now) → P4 (someday).

## Gates (Ship 2)

### Add verify.py Check 4: robots-aware crawlability gate
**Priority:** P0
Scoped-correct robots.txt parser that fails loudly on unknown directives; no gate
currently knows robots.txt exists — that is how the `/start/` leak passed green for
3 weeks. (Eng review T3)

### Regression test pinning the /start/ false-green case
**Priority:** P0
`scripts/test_verify_robots.py`: a link that resolves via `_redirects` while the
target is robots-blocked must FAIL verify. Protects Check 4 from being silently
weakened. (Eng review T4)

### Vary CTA anchor text per article
**Priority:** P0
The ~33 sitewide `/start/` CTA links must become varied-anchor editorial links to
the money page; identical anchors collide with `audit_links.py` CAP=3 and
`build.py` ANCHOR_URL_CAP silently drops extras. (Eng review T5)

### Update audit_links.py doctrine for retired /start (+ /coupon)
**Priority:** P0
Drop `/start` from `EXEMPT_PREFIXES` and fix comments still calling it
"robots-disallowed" — as of v0.2.10.1 `/start/` and `/coupon/` are crawlable 301s,
and the audit would still pass if `/start` broke. (Eng review T6 + Codex 2026-07-22)

### Delete dead build_trial_page()
**Priority:** P1
`build.py:2156` still calls `_build_affiliate_landing("start", "blog")`; one future
call resurrects a static `/start/` page that shadows the 301 (static files win over
`_redirects` per Cloudflare docs). (Eng review T7)

### Fix inverted Cloudflare precedence comments
**Priority:** P1
`build.py:3474-3477` and `:3368` claim redirects lose to static assets; Cloudflare
docs say redirects are ALWAYS followed. Both comments assert the opposite of
reality. (Eng review T8)

### Delete vestigial repo-root _redirects
**Priority:** P1
Root `_redirects` still claims `/start` is a live landing page; the deployed file is
`globalhighlevel-site/_redirects` (build.py:3347). Also confirm the Cloudflare Pages
output dir in the dashboard. (Eng review T9)

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

### Submit rebuilt URLs via submit-bing.py / IndexNow after deploy
**Priority:** P1
(Eng review T14)

## Infra (Ship 4)

### Pages Function for real 410s on the ~70 thin-AI URLs
**Priority:** P2
`_redirects` supports only 301/302/303/307/308; real 410s need
`functions/_middleware.js`. Lowest value — only if slack. (Eng review T13)

## Content hygiene

### Prune or restore dead translation pointers in money-page JSON
**Priority:** P2
`translations` maps es/en-IN to two posts that don't exist in `posts/`; build fails
soft (drops hreflang). Also confirm `/es/start` 301 target (pricing guide, not a
Spanish trial post) is intentional. (Adversarial review 2026-07-22)

### Discount-intent coverage check on money page
**Priority:** P3
`/discount`, `/coupon-code`, and the old promo-discount blog URL all 301 into the
money page, whose new title dropped "Discounts"; description still carries it.
Watch discount-query impressions post-recrawl; revisit title if they sag.
(Codex 2026-07-22)

## Completed
