---
type: data
topic: agency-white-label-saas
status: populated
source: gohighlevel.com/pricing (vendor-controlled) + owner account corroboration
pull_date: 2026-07-06
---

# GoHighLevel agency plan tiers + feature gating

Vendor-controlled pricing page → tagged `[vendor-claimed]`. Owner (Bill) is on Agency Pro $497 and his account exposes SaaS Configurator + Reselling + Whitelabel (corroborates SaaS Mode = Pro tier). Publish pricing with attribution ("As of 2026, GoHighLevel lists…"), never as timeless fact, and hedge exact numbers ("at the time of writing").

| Plan | Price | Sub-accounts | Reselling / rebilling | SaaS Mode | Notes |
|---|---|---|---|---|---|
| **Starter** | $97/mo ($970/yr) | 3 | basic only | ❌ | unlimited contacts/users, core features `[vendor-claimed — ghl pricing 2026-07-06]` |
| **Unlimited** | $297/mo ($2,970/yr) | unlimited | rebill phone & email **without markup**, basic API | ❌ | `[vendor-claimed — ghl pricing 2026-07-06]` |
| **Agency Pro** | $497/mo ($4,970/yr) | unlimited | rebill **with markup**, automated sub-account creation, user/agent reporting, advanced API | ✅ | "Transforms HighLevel into your own sellable software product" `[vendor-claimed — ghl pricing 2026-07-06]`. Owner is on this tier `[verbatim — owner account 2026-07-06]` |
| **Enterprise** | custom | unlimited | full | ✅ | white-label mobile app, HIPAA, dedicated success, custom dev `[vendor-claimed — ghl pricing 2026-07-06]` |

## Feature gating (verify each in draft; codex fact-check target)
- **SaaS Mode** → Agency Pro ($497)+ `[vendor-claimed]` — corroborated by owner account.
- **Rebilling with markup** → Agency Pro; **without markup** → Unlimited `[vendor-claimed]`.
- **White-label custom domain** (app.yourbrand.com) → available across plans ("connect custom domains") `[vendor-claimed]` — corroborated: owner's Whitelabel tab shows app./link.reiamplifi.com.
- **White-label MOBILE app** → Enterprise (or paid add-on) — ⚠️ AMBIGUOUS in source (said "$497/month add-on" AND "Enterprise"). DO NOT state definitively; hedge or verify against help.gohighlevel.com before publishing. `[interpreted]`
- **SSO (OIDC)** → Enterprise-tier per owned post `how-to-set-up-sso` `[summary — owned prior post]` — verify.
- **Snapshots** → all plans `[interpreted]` — verify.

## Anti-cannibalization note
Existing ranking page `/blog/gohighlevel-pricing-plans-2026-complete-guide/` owns the "pricing" query cluster. This pillar covers pricing only as a section and LINKS to that page for full pricing — does NOT target the pricing keyword (per data/agency-gsc-cluster.md).
