# AI agents cluster depth — ship plan

**Status: TASTE LIFTED 2026-09-22. Manager locked A, B, and C as drafted. Dual-Cursor approved. Landing.**

No new URL. No new title. No new H1.

The locked pillar stays:

| | |
|---|---|
| URL | `https://globalhighlevel.com/blog/how-to-build-ai-agents-in-gohighlevel-agent-studio-guide/` |
| File | `globalhighlevel-site/posts/how-to-build-ai-agents-in-gohighlevel-agent-studio-guide.json` |
| Title / H1 | `GoHighLevel Agent Studio: Build AI Agents Step by Step` (54 characters, PR #69, frozen) |

Review label: Dual-Cursor approved at `e39a36e7`. Claude (`claude-opus-5-5-high`, `bc-e5c80f0b-d691-54e8-8c4a-154b5f55699d`) and secondary high (`gpt-5.6-terra-high`, `bc-b8b4a2df-bac0-54b6-808b-46b2abd17fb2`) both APPROVE. Codex CLI is not installed (`CODEX_MODE: not_installed`). Dual-Cursor is the authorized outside voice.

## Decision

Setup intent already lives on the pillar. Naming does not, except as one sentence buried in the metrics section plus the AI Studio pricing page. This ship does three things:

1. **Naming.** A short section on the pillar, `AI Studio Is Not Agent Studio`, with a TOC entry. No compare post.
2. **Setup.** Keep `How to Set Up Your First AI Agent` (`#section-2`). Add `<a id="setup"></a>` immediately above that heading so `#setup` and `#section-2` both land on it. The two existing setup 301s stay. No setup sibling post.
3. **Links.** A stable in-body cluster list on the pillar, plus one backlink from each live spoke in the set below. Two confirmed 404s that were never posts get 301s onto the pillar.

## What was checked (2026-09-22)

Live HTTP, no redirect follow:

| URL | Result |
|---|---|
| Pillar | 200. Title and H1 are the locked string. |
| `/blog/how-to-build-ai-agents-gohighlevel-agent-studio-setup/` | 301 to the pillar |
| `/blog/build-smarter-ai-agents-gohighlevel-agent-studio-setup/` | 301 to the pillar |
| `/blog/gohighlevel-ai-studio-vs-agent-studio/` | 404 |
| `/blog/how-to-setup-ai-agents-in-gohighlevel/` | 404 |
| `/blog/how-to-set-up-ai-agents-in-gohighlevel/` | 404 |
| Named spokes (clone, both Studio prices, voice price, router, brand voice, variables, Ask AI, both log pages, both AI Employee pages, free-trial, AI Studio pages how-to) | 200 |

`git log -S` for both 404 slugs is empty. Nothing in `posts/` or `_redirects` linked them. The pillar's live hrefs all returned 200. There was no dead href on the pillar to repair.

The pillar body already linked the four pricing pages, the AI Employee review, the base pricing guide, and the money page. Clone, router, brand voice, and the contest page showed up only as related cards or circle nav. Circle nav's other neighbor is `how-to-add-inbound-messages-gohighlevel-reduce-api-calls` (200). That page is not part of this cluster.

`inject_internal_links` splits words. Confirmed live on 2026-09-22, before this branch: the pillar anchors the variables page on `GoHighLevel agent` inside `GoHighLevel agents`, and the AI Studio pages guide anchors this pillar on `Studio build` inside `Studio builds`. Both come from title bigrams with no word boundary. This plan does not change `build.py`.

## Fact ledger (fetched 2026-09-22)

Do not quote a figure in the new section unless it is in this table. The July 2026 ledger (`plans/ai-silo-fact-ledger-2026-07-29.md`) still matches the rows below. Token tables are left on the pricing pages. This section does not restate model rates.

| Claim in the new section | Source | Fetched |
|---|---|---|
| AI Studio is a prompt builder for websites, landing pages, and other front-end experiences (surveys, forms, booking flows) | [AI Studio in HighLevel](https://help.gohighlevel.com/support/solutions/articles/155000007587-ai-studio-in-highlevel), modified Tue, 22 Sep 2026, 10:10 AM | 2026-09-22 |
| AI Studio on the plan table: pay-per-use at token cost; Growth "usage included"; Unlimited "3× usage included" | [AI Product Pricing](https://help.gohighlevel.com/support/solutions/articles/155000006652-ai-product-pricing), modified Tue, 22 Sep 2026, 5:08 AM | 2026-09-22 |
| Growth is $50/month. Unlimited is $97/month. Both are per enabled location. | Same pricing article. The Agent Studio note names "AI Employee Growth ($50/mo)" and "AI Employee Unlimited ($97/mo)". The plans intro says monthly per enabled location. Unlimited's own block says "$97/month per enabled location". | 2026-09-22 |
| Agent Studio is not included in any subscription plan. It stays pay-per-use on pay-per-use, Growth, and Unlimited. Table row is "at token cost" in all three columns. | Same pricing article, including the FAQ "Is Agent Studio included in any plan?" Answer: "No." | 2026-09-22 |

Not used in new copy, on purpose:

- Ask AI "free through Summer 2026" from the July ledger. The 22 Sep article prices Ask AI as token cost / usage included / 3×. Summer is over. The new section does not mention Ask AI's price.
- Per-model token rates, Voice AI per-minute rates, and the worked call example. Those stay on the existing pricing pages, which still say "July 2026". The structural claims on those pages ($50, $97, 3×, Agent Studio excluded) still match the 22 Sep article. This ship does not redate those pages.

Help links are citations. They do not get `fp_ref`.

## Pages touched

Pillar, plus one backlink paragraph each. All of these are `language: en` and `topic: AI Receptionist & Lead Capture`, so the silo pass keeps the href.

| Slug | Job of the new sentence |
|---|---|
| `how-to-build-ai-agents-in-gohighlevel-agent-studio-guide` | Naming section, `#setup` anchor, cluster list |
| `gohighlevel-ai-studio-pricing` | Points at the agent build. This page already separates the two Studios. |
| `gohighlevel-ai-agent-pricing` | Points at the build. This page already says Agent Studio is excluded from $97. |
| `gohighlevel-voice-ai-pricing` | Voice is the phone meter. The build guide is the other product. |
| `gohighlevel-ai-employee-pricing` | Tiers are the bundle. Agent Studio sits outside them. |
| `gohighlevel-ai-employee-ai-receptionist-review` | The review is the bundle. Custom agents are the build guide. |
| `how-to-create-pages-faster-gohighlevel-ai-studio` | This page is the page builder. |
| `clone-ai-agents-gohighlevel-scale-sub-accounts` | Clone comes after the build. |
| `how-to-use-agent-studio-router-in-gohighlevel-smarter-ai-flows` | Router comes after the build. |
| `how-to-use-brand-voice-in-gohighlevel-agent-studio-guide` | Brand voice comes after the build. |
| `how-to-use-variables-in-gohighlevel-agent-studio-save-time` | Variables come after the build. |
| `automate-client-support-ask-ai-agent-studio-gohighlevel` | Support flow points at the build. |
| `how-to-setup-agent-logs-metrics-in-gohighlevel-monitor-ai-performance` | Metrics measure a built agent. |
| `how-to-monitor-ai-agents-in-gohighlevel-agent-logs-guide` | Logs trace a built agent. |

Anchor text on every backlink is unique. The sitewide cap is 3 identical anchor-to-URL pairs. The money page is not in this list.

## Redirects added

Both forms, slash and non-slash, 301 to the pillar. Existing setup 301s are unchanged.

- `/blog/how-to-setup-ai-agents-in-gohighlevel`
- `/blog/gohighlevel-ai-studio-vs-agent-studio`

`/blog/how-to-set-up-ai-agents-in-gohighlevel/` (set-up, with a hyphen) also 404s. It is not redirected. It was a second guess, not the slug in the queue. Adding it is a one-line follow-up if William wants it.

## Not in this PR

- No new post. No title edit. The over-60 title count does not grow. Router (64) and logs-metrics (71) stay over 60.
- No retitle of the free-trial money page or the agency snapshots guide. Frozen through 2026-10-13.
- No edit to the money page body. No new outbound link from it.
- No Spanish, India, Arabic, Desktop, or LATAM edit.
- No restoration of the retired Agent Studio 404 set.
- `build.py` injector is unchanged.
- Pricing pages are not redated from July 2026. See the ledger.
- `seo-cooldown.json` stays retired.

## Taste holds (William)

Locked 2026-09-22 as drafted. The new sentences ship.

- **A.** No compare post. The naming section on the pillar is the page. The 301 from `/blog/gohighlevel-ai-studio-vs-agent-studio/` stays.
- **B.** No setup sibling. `#section-2` remains the setup section. `#setup` is an alias. The existing setup 301s stay. The new 301 from `/blog/how-to-setup-ai-agents-in-gohighlevel/` stays.
- **C.** The cluster list and the thirteen backlink sentences ship as written. Anchors stay unique.

Copy he is approving is the naming section, the cluster list, and one short paragraph on each spoke. Titles do not change.

## Acceptance checks

From `globalhighlevel-site/`:

1. `python3 -m pytest scripts/ -q`
2. `python3 build.py`
3. `python3 verify.py`
4. Built pillar HTML contains `id="ai-studio-is-not-agent-studio"`, `id="setup"`, `id="agent-studio-cluster"`, and `fp_ref=amplifi-technologies12`.
5. Built pillar HTML contains each cluster href in the list above.
6. Built money page does not contain `how-to-build-ai-agents-in-gohighlevel-agent-studio-guide`.
7. Title and H1 on the pillar are still the locked string.
8. New copy does not contain `sin tarjeta` or a no-card trial claim.

## GSTACK REVIEW REPORT

Phase 0: GitHub, base branch `main`. UI scope: no (no new chrome, no template change). DX scope: no (readers are agency owners, not developers integrating an API). Design phase skipped. DX phase skipped.

Phase 1 (CEO): The queue asked for setup, naming, and links without a thin second post. The pillar already has a setup H2 in the TOC, and the only setup URLs we ever published already 301 here. A setup sibling would cannibalize `#section-2`. A compare post would cannibalize `gohighlevel-ai-studio-pricing`, which already says the two Studios bill differently. Completeness here is the section plus the links, not another URL. Premises checked against live HTTP and the 22 Sep help articles. No premise queued as wrong.

Phase 3 (eng): Edits are string splices of `html_content` inside post JSON (`json.dumps(..., ensure_ascii=False)` round-trips the existing value). FAQ blocks are not edited, so the hand-written FAQPage stays aligned with the visible questions. New paragraphs each contain one `<a>`, so `inject_internal_links` skips them. Same-silo hrefs are not unwrapped. The money page is untouched. No title passes through `compose_title` differently, so Check 7 stays at 579.

Outside voice: Codex CLI absent (`CODEX_MODE: not_installed`). Dual-Cursor is the authorized outside voice. Both reviewers APPROVE at `e39a36e7`: Claude opus (`bc-e5c80f0b-d691-54e8-8c4a-154b5f55699d`) and GPT terra (`bc-b8b4a2df-bac0-54b6-808b-46b2abd17fb2`). No blockers.

Taste gate: **LIFTED 2026-09-22.** Manager locked A, B, and C as drafted.

<!-- autoplan-accepted:ceo -->
- Naming is a section on the locked pillar, not a new compare URL.
- Setup stays on `#section-2`. No second setup post.
- Only same-silo English Agent Studio, AI pricing, and Voice AI pages get a backlink. The money page gets none.
<!-- /autoplan-accepted:ceo -->

<!-- autoplan-accepted:eng -->
- Byte-faithful JSON splice. FAQ schema untouched. Titles untouched.
- New 301 sources must not be built pages. Target is the live pillar.
- `scripts/test_agent_studio_cluster.py` pins the section ids, the 301s, the backlinks, the locked title, and the money-page absence.
<!-- /autoplan-accepted:eng -->
