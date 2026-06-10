# Podcast Pipeline — GlobalHighLevel.com

## Architecture
- **VPS:** IONOS at 74.208.190.10, SSH user `root`, key `~/.ssh/ionos_ghl`, scripts at `/opt/ghl-pipeline/`
- **Site:** globalhighlevel.com on Cloudflare Pages, static build via `build.py`
- **Repo:** RecoveryBiometrics/Claude-notebookLM-GHL-Podcast
- **Posts:** Canonical post store is `globalhighlevel-site/posts/` — generators (`5-blog.py`, `6-india-blog.py`, `7-spanish-blog.py`, `9-arabic-blog.py`) write there, `build.py` reads there, Cloudflare builds from `globalhighlevel-site/`. The old repo-root `posts/` dir was removed 2026-06-10 (vestigial pre-restructure duplicate, read by nothing; its scheduler "sync" was dead code pointing at a nonexistent nested path). Do NOT recreate a repo-root `posts/`.

## Pipeline Cycle (25 hours, VPS systemd)
```
0a. analytics.py        — Transistor downloads + GSC data (with country/language breakdown)
0b. gsc-topics.py       — Flag low-CTR pages, generate improvement suggestions
0c. 8-seo-optimizer.py  — Weekly: rewrite titles/descriptions (10 pages/week, 28-day cooldown)
1.  retry-failed.py     — Retry failed episodes
2.  run-pipeline.py     — 20 episodes (help.gohighlevel.com → NotebookLM → Transistor → blog)
3.  6-india-blog.py     — 5 India blogs (3 from GHL docs + GSC gaps + market topics)
4.  7-spanish-blog.py   — 5 Spanish blogs (same 3-tier sourcing)
4.5 9-arabic-blog.py    — 5 Arabic blogs (same 3-tier sourcing)
5.  deploy_site()       — git push → Cloudflare Pages
```

## Output Per Cycle: 35 posts
- 20 English (podcast episodes + blogs from GHL help docs)
- 5 India + 5 Spanish + 5 Arabic (3-tier: GHL docs, GSC gaps, market verticals)

## Weekly Pipelines (GitHub Actions)
- **Monday:** `weekly-analytics.yml` — GA4 + traffic data
- **Tuesday:** `weekly-seo-report.yml` — GSC gaps → language-tagged TODOs to Sheet
- **Wednesday:** `weekly-content-builder.yml` — reads Sheet, builds gap pages in correct language

## Site Structure
- 4 languages: English (default), Español (`/es/`), India (`/in/`), Arabic (`/ar/`, RTL)
- 8 topic categories (separate from language — no mixing)
- Nav: Topics dropdown + language picker (`English ▼`)
- hreflang tags on every page
- `categories.json`: `{languages: [...], topics: [...]}`

## Topic Sourcing (3 tiers)
1. **GHL Docs** — adapt help.gohighlevel.com articles for each language (trust layer, tracks `articleId`)
2. **GSC Gaps** — queries with impressions, no matching page (`analytics.py` filters by country)
3. **Market Verticals** — industry-specific topics per region (Claude-generated)

## ICM Skills (agent-command-center)
- `/report` — weekly reports, error alerts, CEO digests (silent on success)
- `/localize` — classify language + topic, localize CTAs/pricing/currency
- `/topics` — 3-tier topic sourcing for any language

## Slack Routing
- **#ops-log** (C0AQG0DP222): failure alerts only (silent on success)
- **#ceo** (C0AQAHSQK38): errors/warnings only (silent on clean days)
- **#globalhighlevel** (C0AQ95LG97F): weekly report only

## Key Gotchas
- **NotebookLM auth expires ~every 2 weeks.** Re-login locally, `scp` to VPS
- **GSC token expires periodically.** Re-auth locally: `venv/bin/python3 scripts/analytics.py`, then `scp token-gsc.json` to VPS
- **VPS scripts sync via `scp`, not git pull.** Deploy: `scp -i ~/.ssh/ionos_ghl <file> root@74.208.190.10:/opt/ghl-pipeline/scripts/`
- **public/ is gitignored.** Build output never tracked.
- **28-day cooldown** on SEO optimizer and GSC topic flagging
- **`/trial/`, `/coupon/`, `/start/` are ATTRIBUTION URLs, not SEO landings.** Full content pages (~1,900 words) that pitch both GHL + Extendly affiliates, GA4-tracked CTAs, intentionally `Disallow`'d in `robots.txt` so they don't cannibalize organic SERPs. Parallel SEO-indexable blog posts exist (`/blog/gohighlevel-free-trial-30-days-extended/` etc.). Do NOT unblock, thin out, or migrate their content. Full rules in `globalhighlevel-site/CLAUDE.md`.

## Deploy Checklist — BLOCKING (do not skip)
Before ANY `git push origin main` that touches SEO content (posts, redirects, build.py, meta rewrites):
1. **Log to Google Sheet FIRST** — "SEO Changelog Tracker" (ID: `1rK5UjtCeuzwwqIRE7GxC39_b3-10dSogUyxfe_Ycc0o`), Changelog tab. One row per change: Date, Business, Slug, Action, Attempt, Position, Impressions, CTR, Old Title, New Title.
2. **Update `seo-cooldown.json`** — add entries for every page touched. scp to VPS.
3. **THEN push.** If Sheet write fails, fix auth. Do not push undocumented changes.
This is Rule 7 of `seo-deploy-gate`. Sheet is source of truth. JSON is fallback.

## Affiliate Link
All GHL links must include `fp_ref=amplifi-technologies12`. Full rules in `globalhighlevel-site/CLAUDE.md`.

## Trigger Surface — BLOCKING (do not skip)

**GitHub Actions is the canonical trigger surface for cloud automation.** All NEW recurring automation goes there. Do not create:
- New `/schedule` (claude.ai routines) — surface is FROZEN. Existing 3 active routines remain (Verticals Measurement Daily, CEO Daily Narrative, Weekly SEO Report). Everything else is zombie or migrating.
- VPS cron jobs — VPS systemd is for content generation only (`ghl-podcast.service`, NotebookLM, scp deploys).
- Mac local cron — Mac may be off; cloud-only.

**Before proposing ANY new trigger:** read `memory/project_automation_surface.md`. It lists what already exists and where. The Apr 27 session burned ~2 hours rebuilding things that already existed because no one diarized first.

**Skill source of truth:** `RecoveryBiometrics/agent-command-center` (24 skills). `~/.claude/skills/` on the Mac is a working copy that drifts; sync it back via `cp -R` + commit before any production workflow reads it.

## GBrain Search Guidance (configured by /sync-gbrain)
<!-- gstack-gbrain-search-guidance:start -->

GBrain is set up and synced on this machine. The agent should prefer gbrain
over Grep when the question is semantic or when you don't know the exact
identifier yet.

**This worktree is pinned to a worktree-scoped code source** via the
`.gbrain-source` file in the repo root (kubectl-style context). Any
`gbrain code-def`, `code-refs`, `code-callers`, `code-callees`, or `query`
call from anywhere under this worktree routes to that source by default —
no `--source` flag needed. Conductor sibling worktrees of the same repo
each have their own pin and their own indexed pages, so semantic results
match the actual code on disk in this worktree.

Two indexed corpora available via the `gbrain` CLI:
- This worktree's code (auto-pinned via `.gbrain-source`).
- `~/.gstack/` curated memory (registered as `gstack-brain-<user>` source via
  the existing federation pipeline).

Prefer gbrain when:
- "Where is X handled?" / semantic intent, no exact string yet:
    `gbrain search "<terms>"` or `gbrain query "<question>"`
- "Where is symbol Y defined?" / symbol-based code questions:
    `gbrain code-def <symbol>` or `gbrain code-refs <symbol>`
- "What calls Y?" / "What does Y depend on?":
    `gbrain code-callers <symbol>` / `gbrain code-callees <symbol>`
- "What did we decide last time?" / past plans, retros, learnings:
    `gbrain search "<terms>" --source gstack-brain-<user>`

Grep is still right for known exact strings, regex, multiline patterns, and
file globs. Run `/sync-gbrain` after meaningful code changes; for ongoing
auto-sync across all worktrees, run `gbrain autopilot --install` once per
machine — gbrain's daemon handles incremental refresh on a schedule.

<!-- gstack-gbrain-search-guidance:end -->
