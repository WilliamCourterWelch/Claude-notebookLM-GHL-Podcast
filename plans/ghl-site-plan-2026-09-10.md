<!-- /autoplan restore point: /home/ubuntu/.gstack/projects/WilliamCourterWelch-Claude-notebookLM-GHL-Podcast/cursor-ghl-site-plan-2026-09-10-1124-autoplan-restore-20260910-114730.md -->
# Global HighLevel site plan — 2026-09-10

Status: planning/docs only. No production ship, no mass deletes, no merge, no deploy in this PR.

Site: globalhighlevel.com (this repo). Affiliate: `fp_ref=amplifi-technologies12`. Owner context: ~$700–900/mo, never broke $1k on clicks; catalog stagnant since the firehose died; Google weak, Bing/AI stronger.

Companion docs in this PR:

- `plans/site-crawl-inventory-2026-09-10.md`
- `plans/site-interlink-graph-2026-09-10.md`
- `plans/have-vs-need-2026-09-10.md`

gstack: v1.84.1.0. `/autoplan` run against **this file**.

---

## Sibling EN IA autoplan

Tried: `gh pr view 3 --repo WilliamCourterWelch/globalhighlevel-pillar-system` and `plans/en-ia-autoplan-2026-09-10.md` via API.

Result: **repository 404**. Cannot reconcile bullet-by-bullet.

**Alignment assumed from *this* repo's already-shipped EN IA** (treat as the live EN plan unless the sibling PR says otherwise when someone can open it):

- 5 hubs on `/category/{topic}/` with EN pillars canonical there.
- Language ≠ topic. Silo isolation. Money page is a sink. Pricing is a sibling funnel URL, not a second trial page.
- Bing-first CTR over Google-first title panic.
- No mass spoke deletes after the restore.

**If the sibling autoplan later disagrees**, log the divergence here; do not silently rebuild hubs. This sprint does not implement IA.

---

## Goal

Raise affiliate **trial starts** from existing EN traffic without a redesign and without reviving the dead content pipeline.

First post-approve ship = **smallest CTA/measurement win**. Human taste on the live money page and nav **before** that ship.

Spanish/LATAM = **phase 2**. No ES spoke builds, no qué-es 301s, no `/es/` hub redesign in the sequenced ships below.

---

## Premises (challenge these)

1. Clicks, not rankings, are the constraint. Bing already shows the money page (historical: 1,091 impressions, 0.37% CTR — v0.3.16.1; **not re-measured today**).
2. Nav + CTA #3 already carry `fp_ref`. The hole is **instrumentation and first-screen bootcamp clarity**, not "add affiliate links."
3. The internal hop (byline/mid-CTA → money page) is a sales letter, not a bug. Do not retarget every CTA at bootcamp until Bill looks at the letter.
4. 909 URLs are inventory, not a machine. Deleting them is how we already lost a summer. Do not purge.
5. ES can wait. Historical ES pricing CTR was healthier than EN money CTR; that is an argument for a later ES sprint, not for mixing it into P0.

If 1 is wrong (money page CTR already recovered post-snippet), P0 shrinks to measurement-only.

---

## Human taste first (before any code)

Owner opens, desktop + phone:

1. `https://globalhighlevel.com/` — guidecard vs nav CTA. Does "30 days + bootcamp" read in 3 seconds?
2. `https://globalhighlevel.com/blog/gohighlevel-free-trial-30-days-extended/` — first amber box vs mid-page `.bootcamp-section`. Is bootcamp a surprise?
3. `https://globalhighlevel.com/services/` — does this page deserve a nav/footer link, or should it stay a quiet URL so it doesn't compete with the trial?

Write the answers in the PR comment or a follow-up. The P0 ship below does **not** require copy changes if taste is "bootcamp is fine; just measure."

---

## Ship sequence

### Ship 0 — this PR (docs)

The four `plans/*.md` files. No `build.py` change. No post JSON change.

### Ship 1-pre — read instruments we already shipped (same week, no code required)

Before writing new events: pull existing GA4 `ghl_click` (`link_url`, `page_path`, `page_lang` already fire) and pricing `utm_content=tier_*` (v0.3.11.0). If nav vs CTA #3 is already distinguishable from `link_url` + `utm_campaign={slug}`, Ship 1 **shrinks to CLAUDE.md event-name fix + optional `cta_slot` parse**. Do not invent a third event because the docs were stale.

If GA4/FirstPromoter credentials are not in this cloud environment, that pull happens on the owner's machine. It still gates the code ship.

Kill criterion: if existing Explores already split nav (no `utm_campaign`) vs cta3 (`utm_campaign={slug}`), do not add `utm_content=nav` just for symmetry. Still add the `utm_content=` assert so nobody bakes it into `AFFILIATE`.

### Ship 1 — P0 CTA/measurement (first post-approve **code**)

**Files:** `globalhighlevel-site/build.py` only at template call sites + `_ga_snippet`; `globalhighlevel-site/CLAUDE.md`; new pytest that asserts **rendered HTML**.

**Architecture (eng review — do not ignore):**

1. Do **not** put `utm_content` on `AFFILIATE` or inside `affiliate_for()`. That function is language-only. Add `affiliate_href(lang, *, campaign=None, content=...)` that appends with `&`.
2. New assert: `"utm_content=" not in AFFILIATE` (sibling of the `utm_campaign` assert). Baking content into the constant contaminates `AFFILIATE_ES` replace, `localize_trial_hrefs`, and every template href with the same slot.
3. Wire: nav (desktop + mobile), cta3, tldr, `_build_affiliate_landing`, `_build_localized_affiliate_landing`. Optionally about-page CTA (`utm_content=about`). Do not call dead `build_trial_page()` (it still builds `/start/`).
4. `/trial/` already uses `utm_campaign=podcast-hero|skip|bottom`. **Append** `utm_content`; never collapse those campaigns into one `trial_landing`. Prefer `trial_hero` / `trial_skip` / `trial_bottom`. Keep `ar` → campaign `blog`.
5. Listener: parse `utm_content` from the clicked URL via `URLSearchParams` into `cta_slot`. Keep existing `ghl_click` fields (`link_url`, `link_text`, `page_path`, `page_lang`) exactly once. Do not add a second `page_lang`. Do not allowlist slots (pricing already uses `tier_starter` etc.; an allowlist would drop them). Empty `cta_slot` = untagged body href — document that, do not "fix" by rewriting 1,920 JSON files.
6. GA4 admin: register `cta_slot` as a custom dimension or Explores die after ~30 days. That step is not code.
7. CLAUDE.md: there is no `affiliate_click` event today.

**Tests:** rendered HTML, not source greps (v0.3.14.0 anti-pattern). Nav both langs; cta3 + tldr; trial landing campaigns preserved; `AFFILIATE` still has zero `utm_content`; pricing bodies still have exactly one `utm_content=` per tier href; `test_localize_trial_hrefs` still exact-matches; nofollow still on fp_ref; mutation: removing `utm_content=nav` from nav must fail. Then full `pytest scripts/ -q`, `build.py`, `verify.py` (Check 4, 5, 6c).

**Do not:** money-page JSON, mid-CTA retarget, `_redirects`, robots, widget, Topics dropdown, `json.dumps` of posts, revive `/start/`.

**Success:** nav click and CTA #3 click distinguishable in GA4 **and** in rendered hrefs. `fp_ref=amplifi-technologies12` unchanged. FirstPromoter still attributes.

### Ship 2 — P1 Bing money-page re-pull (before any chrome)

Autoplan reorder: chrome does not teach. Close the v0.3.16.1 snippet bet first.

- Restore or rewrite `pull-bing.py` into `globalhighlevel-site/scripts/`.
- `GetPageQueryStats` on the money page + EN pricing (250-row `GetPageStats` cap is a trap).
- Compare money-page CTR to the **0.37% documented baseline**.
- Read-only weekly Bing dump Action is allowed later. No content-builder Action.

### Ship 3 — P1 graph one-liners (still not a redesign)

Only after Ship 1 is live. Prefer after Ship 2 so we are not editing footer during a CTR read.

1. Footer: add Agency White-Label & SaaS (5th cluster). Mirror homepage. First visible UI in this plan; keep amber, DM Sans, existing footer CSS. Do not invent a new component.
2. Nav: default **footer only**. Delete unused `dropdown_links` or leave it; do not add a Topics menu unless Bill asks.
3. Optional money-page bootcamp sentence in the first amber box, only if the pre-ship taste pass asked. Sync FAQ JSON-LD. Byte-faithful JSON.

### Ship 4 — P1 money-page section (copy, not a new URL)

Plan-by-plan trial table (Starter / Unlimited / Agency Pro): does the 30-day extension apply, what changes after day 30. Queries already listed in TODOS (~130 impressions, 0 clicks). Same sink page. No new slug.

### Ship 5 — P1 thin content machine (EN only)

- Cadence: handful of EN spokes/month via `assemble_spoke.py` + fact ledger.
- Sources: Bing gaps on money/pricing/AI hubs + official GHL changelog. Not NotebookLM firehose.
- Support existing hubs. No new topic.
- ES/AR/IN pages: maintenance only (gates, factual breaks).

### Explicitly later (phase 2 / P2)

- All `/es/` work: 18-post hole, qué-es consolidation, promo-page fate, `/es/start/` asymmetry.
- Conversation widget (cost model still open).
- Arabic expansion or deletion.
- 580 title rewrites beyond Bing-picked batches.
- Mass 301 of "thin" firehose.

---

## NOT in scope (this plan)

- Production deploy from this branch.
- Headed crawl of the live site.
- Recreating `ghl-podcast-pipeline/` generators, VPS systemd content loop, claude.ai `/schedule` jobs.
- Unblocking `/trial/`.
- New CTAs to `/start/` or `/coupon/`.
- Repo-root `posts/` directory.
- Inventing revenue forecasts.

---

## What already exists (leverage, don't rebuild)

| Need | Existing |
|---|---|
| Affiliate URL + ES variant | `AFFILIATE` / `AFFILIATE_ES` / `affiliate_for()` |
| Click listener | `_ga_snippet()` |
| Money page sink | `mvp_minimal_links` + Check 4 |
| CTA #3 / nav | `build_post_page` / `base_html` |
| Trial landings | `_build_affiliate_landing` + `LOCALIZED_LANDING_LANGS` |
| New honest pages | `assemble_spoke.py`, `plans/ai-silo-*` fact ledger pattern |
| Bing method (docs) | CLAUDE.md § titles; script missing in-repo |
| Deploy gates | `pytest scripts/`, `build.py`, `verify.py` |
| Footer clusters | `_footer_clusters` in `base_html` (edit the list) |

---

## Implementation alternatives (Ship 1)

| Approach | Effort | Risk | Verdict |
|---|---|---|---|
| A. Add `utm_content` + fields on existing `ghl_click` | small | GA4 explores break if someone filtered on old params only | **Recommended** — no third event name |
| B. New `affiliate_outbound` event, keep `ghl_click` duplicate | small | two events per click | Only if GA4 already has dashboards on `ghl_click` that must stay byte-identical |
| C. Mid-CTA retarget to bootcamp sitewide | small code, large product | skips the sales letter; taste | Reject until Ship-taste says hop is waste |

---

## Dream state delta

```
NOW: 909 URLs, working bootcamp CTAs, slot-blind analytics, dead pipeline,
     EN IA already 5 hubs, ES catalog idle, ~$700-900/mo clicks

THIS PLAN: know which CTA slot pays; footer matches IA; money page answers
           plan-named trial queries; tiny EN editorial cadence

12-MONTH: Bing/AI citation still the acquisition channel; EN hubs maintained;
          ES phase 2 if cash justifies; still no firehose
```

---

## Error & rescue

| Error | Rescue |
|---|---|
| `utm_content` added onto stored JSON bodies | Don't. Template only. Restore from git (byte-faithful). |
| `AFFILIATE` gains a pre-baked `utm_campaign` | Build assert already fails. Keep it. |
| Ship 1 breaks Check 4 / paid-link gate | Revert snippet; never loosen `nofollow` on fp_ref. |
| Someone "cleans" 846 body orphans | Stop. Circles exist. Point at the graph doc. |
| ES work sneaks into Ship 1–5 | Cut. Phase 2. |
| Widget added on money page | Violates sink + unbounded AI cost. Separate plan. |

---

## Failure modes

| Mode | Severity | Mitigation |
|---|---|---|
| Measuring clicks, still ~$700/mo | expected | Measurement doesn't mint conversions. Next lever is money-page taste + Ship 4 section. |
| FirstPromoter ignores `utm_content` | low | UTM is for GA4. `fp_ref` is the commission. |
| Nav CTA vs money-page CTA conflict (user clicks both) | low | `utm_content` tells you. Don't remove one. |
| Clarity + GA4 double-count anxiety | none | Different products. Don't "dedupe" by removing Clarity. |

---

## Temporal (Ship 1 once approved)

- Hour 0: Ship 1-pre pull of existing GA4 (or note credentials missing).
- Hour 1: `affiliate_href()` + `utm_content` assert; wire nav/cta3/tldr/trial builders; listener parses `cta_slot`. CLAUDE.md.
- Hour 2: rendered-HTML tests; full pytest; `build.py` + `verify.py`; do not push `main`.
- Later: bootcamp sentence only if taste asked (Ship 3 copy, not Ship 1).

---

## Cross-links for implementers

- Affiliate rules: `globalhighlevel-site/CLAUDE.md`
- Sink / silo: same file, Internal Link Doctrine
- Backlog already agreeing with Ship 4: `TODOS.md` "Plan-by-plan trial section"
- Do not run retired pipeline: repo-root `CLAUDE.md` banner

---

## GSTACK REVIEW REPORT

gstack 1.84.1.0 `/autoplan`. Session `1511-1789040500-c718c681`.
Codex: **unavailable** (binary not found) — `[subagent-only]` for dual voices.
Office-hours: skipped (user already specified four deliverables; background agent).
UI scope: **yes** (nav, footer, CTA) — Design ran, scoped to future ships not this docs PR.
DX scope: **yes** (build.py, GA events, scripts) — DX ran light.
Mode: SELECTIVE EXPANSION (autoplan default for iteration).
Final gate: background/cloud agent, AskUserQuestion unavailable. **User Challenges stand as owner's original direction.** Taste auto-chose recommended. Human gate = this PR.

### Phase 0 intake

Plan: EN-first affiliate cash; first *code* ship is CTA/measurement; no redesign; no mass deletes; ES phase 2.
UI scope: yes. DX scope: yes.
Loaded: plan-ceo-review, plan-design-review, plan-eng-review, plan-devex-review.

### Phase 1 — CEO

#### 0A Premise challenge

| Premise | Assessment |
|---|---|
| Clicks not rankings | **Partly true for Bing money page** (1,091 impr / 0.37% CTR, v0.3.16.1). False as a whole-site diagnosis: Google ~5 clicks/90d; pricing head terms at pos 7.4/7.7 are ranking. |
| Slot-blind analytics is the hole | **Overstated.** `ghl_click` already has `link_url` + `page_lang`; CTA #3 has `utm_campaign={slug}`; pricing already has `utm_content=tier_*` (v0.3.11.0). Real hole may be **unread instruments**. |
| Internal hop is a sales letter | Reasonable; Clarity 38.7% avg scroll (changelog) means many never see mid-page CTAs. Do not retarget sitewide without hop-completion data. |
| Do not purge 909 | Accept as owner constraint this sprint. Historical: prune kept 15 click-earners of 946 (CHANGELOG heavy-prune). Restore-trauma ≠ forever policy. **Not a delete sprint.** |
| ES can wait | **Owner constraint.** Evidence cuts the other way (ES CTR 9.43% vs EN 2.14%, changelog v0.3.13.0). Queued as User Challenge. Direction stands. |

Doing nothing: catalog keeps aging (last new publish 2026-07-29); money-page snippet bet stays unclosed; still ~$700–900/mo.

#### 0B / What already exists

Mapped in plan body. Extra: pricing `utm_content` already live; do not duplicate.

#### 0C Dream state

Unchanged. This plan is a delta on an already-hubbed EN site, not a 12-month strategy.

#### 0C-bis Alternatives

A. Minimal: CLAUDE.md + assert only if GA4 already splits slots. Completeness 5/10.
B. Recommended: `affiliate_href` + listener parse + rendered tests. Completeness 8/10.
C. Ideal: B + FirstPromoter×GA4 weekly readout + ES strategy scored, no ES build. Completeness 10/10, out of this sprint except 1-pre pull.

Auto-chose **B** (user asked for measurement win). A is the kill-switch if 1-pre shows data already exists.

#### 0D–0F

SELECTIVE EXPANSION. In-blast: reorder Bing re-pull before footer; add 1-pre; eng helper/assert/tests. Out: ES builds, widget, purge, services as primary offer (owner call already in taste list).

#### CEO dual voices

CODEX SAYS (CEO): `[codex-unavailable]`

CLAUDE SUBAGENT (CEO — strategic independence): P0 does not touch cash; no economics; EN-first contradicts measured ES CTR; "do not purge" unexamined; `/services/` is a second company; sequence put chrome before the snippet bet; Ship 5 cadence without a winner thesis. Verdict: careful implementation memo, not a growth plan.

Primary (this session): agree measurement is a **commit**, not a company theory. Did **not** flip ES to this sprint (User Challenge). Did **not** authorize deletes. Did swap Bing re-pull before footer (mechanical).

```
CEO DUAL VOICES — CONSENSUS TABLE:
═══════════════════════════════════════════════════════════════
  Dimension                           Claude  Codex  Consensus
  ──────────────────────────────────── ─────── ─────── ─────────
  1. Premises valid?                   mixed   N/A    N/A
  2. Right problem to solve?           no*     N/A    N/A
  3. Scope calibration correct?        yes**   N/A    N/A
  4. Alternatives sufficiently explored? no    N/A    N/A
  5. Competitive/market risks covered? no      N/A    N/A
  6. 6-month trajectory sound?         if cash not the KPI  N/A  N/A
═══════════════════════════════════════════════════════════════
* Subagent: P0 is tooling. User: first ship is measurement. USER CHALLENGE.
** For a docs+first-commit plan, yes. For 10x cash, no.
CONFIRMED = 0/6 (Codex missing). Single-voice critical: P0 vs cash (surfaced).
```

#### CEO sections 1–10 (examined)

1. Strategy: affiliate trial starts. Proxy risk named (GA4 debug ≠ trials).
2. Error/rescue: table in plan body.
3. Scope: four docs this PR; code later. No silent expansion into ES.
4. Users: agency owners hunting trial/pricing; Bill as operator.
5. Metrics: ghl_click + FirstPromoter; kill criterion added.
6. Sequencing: human taste → 1-pre → Ship 1 → Bing pull → footer.
7. Dependencies: GA4 access, IndexNow, fp_ref invariant.
8. Competitive: coupon aggregators, official docs, AI citations — named by subagent; not a P0 build.
9. 6-month regret: instrumented a known funnel; ES idle; Google still dead — logged.
10. Completeness vs chore: Ship 1 is a chore unless 1-pre is done.

Design (section 11): see Phase 2.

**Phase 1 complete.** Codex: unavailable. Claude subagent: 14 findings (3 critical). Consensus: 0/6 CONFIRMED (missing voice). User Challenges queued. Passing to Phase 2.

### Phase 2 — Design

Ship 1 is invisible (query params + JS). First visible UI is Ship 3 footer link.

| Dimension | Score | Note |
|---|---|---|
| Hierarchy | 8 | Footer already lists 4 hubs; adding the largest is consistency, not a new pattern. |
| Spacing/type | 9 | Reuse existing footer `<a>` style. Amber already in brand. |
| Nav | 7 | Dead `dropdown_links`; plan says do not add Topics chrome. |
| Contrast | 9 | Existing tokens. |
| Motion | n/a | No animation. |
| Voice | 8 | Cluster names already on homepage. |
| Distinctiveness | 8 | No purple/Inter/generic cards. |

Issues auto-decided: no new dropdown (P5 explicit). No `/services/` in footer unless Bill asks (competing offer).

```
Design Voices: Codex N/A, Claude (primary) — footer-only. Consensus 6/7 informal.
```

**Phase 2 complete.**

### Phase 2.5 — DX

Developer journey for Ship 1: read this plan → `affiliate_href` → rendered tests → pytest/build/verify.

| Dimension | Score |
|---|---|
| TTHW (time-to-hello-world) | Target: one local build showing `utm_content=nav` in `public/index.html` |
| Docs | CLAUDE.md event names must match code (the whole point) |
| Errors | Asserts fail the build if AFFILIATE is polluted |
| Examples | Copy nav/cta3 call sites, not `build_trial_page()` |
| Consistency | Same `&` concat as existing `utm_campaign` |
| Debugging | GA4 DebugView + view-source on nav href |
| Integration | Custom dimension admin is a human step |
| Onboarding | Test plan artifact at `~/.gstack/projects/.../cursor-ghl-site-plan-2026-09-10-1124-test-plan-20260910.md` |

```
DX Voices: Codex N/A. Consensus N/A (5/8 informal primary).
```

**Phase 2.5 complete.**

### Phase 3 — Eng

#### Scope challenge (read actual code)

`affiliate_for()` is language-only. `_ga_snippet` already sends `page_lang`. `build_trial_page()` is dead. Pricing JSON already has `utm_content`. `AFFILIATE` forbids pre-baked `utm_campaign`. Plan amended to match.

#### Architecture

```
AFFILIATE (const, fp_ref, NO utm_campaign, NO utm_content)
    │
    ├─ affiliate_for(lang) → EN or ES base
    │         │
    │         └─ affiliate_href(lang, campaign, content)
    │                    │
    │                    ├─ nav (content=nav, no campaign)
    │                    ├─ cta3 (campaign=slug, content=cta3)
    │                    ├─ tldr (campaign=slug_tldr, content=tldr)
    │                    └─ trial builders (keep podcast-hero|skip|bottom)
    │
    └─ localize_trial_hrefs (unchanged; body /trial rewrite)
                │
_ga_snippet: click → if fp_ref → ghl_click { existing fields + cta_slot from URLSearchParams }
```

Coupling: one helper. Security: slot literals only; parse with URLSearchParams; try/catch on `new URL`.

#### Eng dual voices

CODEX SAYS (eng): `[codex-unavailable]`

CLAUDE SUBAGENT (eng): 10 findings. High: don't stamp via `affiliate_for`; add `utm_content` assert; don't duplicate pricing tiers; parse `cta_slot` from URL (GA4 100-char cap); don't revive `build_trial_page`; rendered tests not string greps.

Primary: accepted all high findings into Ship 1.

```
ENG DUAL VOICES — CONSENSUS TABLE:
═══════════════════════════════════════════════════════════════
  Dimension                           Claude  Codex  Consensus
  ──────────────────────────────────── ─────── ─────── ─────────
  1. Architecture sound?               yes*    N/A    N/A
  2. Test coverage sufficient?         after amendment yes  N/A  N/A
  3. Performance risks addressed?      n/a     N/A    N/A
  4. Security threats covered?         yes     N/A    N/A
  5. Error paths handled?              asserts yes N/A N/A
  6. Deployment risk manageable?       docs PR has none; Ship 1 gated  N/A  N/A
═══════════════════════════════════════════════════════════════
* After helper/assert amendment. Original sketch was unsound.
```

#### Test diagram

See `~/.gstack/projects/WilliamCourterWelch-Claude-notebookLM-GHL-Podcast/cursor-ghl-site-plan-2026-09-10-1124-test-plan-20260910.md`.

#### Failure modes (eng)

Duplicate `utm_content` on pricing; two `?` in href; GA4 truncating long `link_url` so slot never appears unless parsed separately; Friday-green source grep.

**Phase 3 complete.**

### Cross-phase themes

**Theme: unread existing instrumentation** — CEO (pricing UTMs, ghl_click fields) and Eng (same). High-confidence. Ship 1-pre.

**Theme: do not bake slot into AFFILIATE** — Eng critical; CEO "more events unused." Helper + assert.

No other multi-phase theme. ES-as-strategy is CEO-only (User Challenge).

### User Challenges (direction stands unless Bill changes it)

1. **ES is phase 2, not this sprint's build.** Subagent: ES is the live CTR advantage. Cost if we're wrong: competitors consolidate qué-es; we keep optimizing the weaker language. **Default: owner's ES-later stands.** Strategy note stays in have-vs-need; no ES code.

2. **First ship is measurement, not a cash bet.** Subagent: P0 doesn't touch cash. Cost if we're wrong: another quarter under $1k with a nicer GA4 schema. **Default: measurement-first stands**, with 1-pre so we don't stamp redundant params, and Bing re-pull moved ahead of footer.

3. **No mass deletes / noindex purge.** Subagent: 15/946 earners historically. Cost if we're wrong: Google stays dead because restored firehose still looks scaled. **Default: no deletes this sprint.**

### Taste decisions (auto-chose recommended)

1. Footer vs Topics nav — footer only (P5).
2. Approach A vs B for events — B (`cta_slot` on `ghl_click`) unless 1-pre kills it (A).
3. Bing re-pull before footer — yes (completeness).

### Decision audit trail

| # | Phase | Decision | Class | Principle | Rationale | Rejected |
|---|---|---|---|---|---|---|
| 1 | 0 | Skip office-hours | mechanical | P6 | User specified deliverables | Run office-hours |
| 2 | 0 | SELECTIVE EXPANSION | mechanical | autoplan default | Iteration on existing site | HOLD / REDUCE |
| 3 | 1 | ES stays phase 2 | User Challenge | owner | Explicit constraint | Build ES now |
| 4 | 1 | No mass deletes | User Challenge | owner | Explicit constraint | Noindex firehose |
| 5 | 1 | Keep measurement as first *code* ship | User Challenge | owner | Explicit constraint | Jump to copy/distribution |
| 6 | 1 | Add Ship 1-pre read-existing | mechanical | P4 DRY | UTMs already exist | Stamp blindly |
| 7 | 1 | Bing pull before footer | taste | P1 | Chrome doesn't learn | Footer first |
| 8 | 2 | No Topics dropdown | mechanical | P5 | Dead code; don't add chrome | Render dropdown |
| 9 | 3 | `affiliate_href` not `affiliate_for` | mechanical | P5 | Eng: same slot on every CTA | Bake into AFFILIATE |
| 10 | 3 | Parse cta_slot from URL | mechanical | P1 | GA4 100-char cap on link_url | Href-only |
| 11 | 3 | Rendered HTML tests | mechanical | P1 | Repo anti-pattern | Source grep |
| 12 | 4 | Auto-approve A for PR delivery | mechanical | spawned/cloud | AUQ unavailable; PR is the gate | Stop and wait |

### Pre-gate checklist

- [x] CEO premises named
- [x] Sections examined
- [x] Error & rescue table
- [x] Failure modes
- [x] NOT in scope
- [x] What already exists
- [x] Dream state delta
- [x] Dual voices (subagent-only)
- [x] CEO consensus table
- [x] Design 7 dimensions
- [x] DX TTHW + checklist
- [x] Eng scope vs actual code
- [x] Architecture ASCII
- [x] Test plan on disk
- [x] Eng consensus table
- [x] Cross-phase themes
- [x] Audit trail nonempty

### Implementation tasks (no JSONL this session; inlined)

- [ ] **T1 (P1)** — Ship 1-pre: pull GA4 `ghl_click` + pricing `utm_content` before coding
- [ ] **T2 (P1)** — `affiliate_href` + `utm_content` assert + listener parse + rendered tests
- [ ] **T3 (P2)** — Restore `pull-bing.py`; money-page GetPageQueryStats vs 0.37%
- [ ] **T4 (P2)** — Footer fifth hub
- [ ] **T5 (P2)** — Plan-by-plan trial section on money page (TODOS already)
- [ ] **T6 (P3)** — GA4 register `cta_slot` custom dimension (human)

### Completion summaries

- CEO: DONE_WITH_CONCERNS — strategy vs chore named; owner constraints held.
- Design: skipped-as-UI-for-later; footer-only scores.
- DX: TTHW = view-source nav href after local build.
- Eng: DONE — Ship 1 sketch was unsound; amended.

STATUS: DONE_WITH_CONCERNS
REASON: Codex missing; User Challenges need Bill on the PR; no live GA4 pull in this environment.
ATTEMPTED: full source inventory, live sitemap curl, CEO+eng subagents, plan amendments.
RECOMMENDATION: Approve docs PR. Do not `/ship` the site. Next: Ship 1-pre on a machine with GA4, then Ship 1 code on a new branch.

<!-- AUTONOMOUS DECISION LOG -->
## Decision Audit Trail

See table above. 12 rows.
