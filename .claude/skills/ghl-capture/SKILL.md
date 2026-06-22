---
name: ghl-capture
description: Capture real GoHighLevel product screenshots from the owner's sandbox and wire them into globalhighlevel.com posts as honest, attested first-hand EEAT evidence.
allowed-tools:
  - Bash
  - Read
  - Edit
  - AskUserQuestion
---

# /ghl-capture — EEAT evidence capture for globalhighlevel.com

This skill holds the JUDGMENT. Execution is delegated to the canon `browse`
binary (GStack Browser) and three Python scripts in `globalhighlevel-site/scripts/`.
Design doc: `~/.gstack/projects/WilliamCourterWelch-Claude-notebookLM-GHL-Podcast/kerapassante-main-design-20260622-151441.md`.

## Why this exists
globalhighlevel.com is under an April-2026 Google quality demotion. The
2026-06-22 survivor audit: 15/15 posts have zero screenshots, 14/15 zero
first-person, 0/15 a real author. The recovery lever is genuine EEAT, which
needs the owner's real GHL account, not more AI text. This skill turns real GHL
usage into auditable page evidence without faking anything.

## Hard rules (read every run)
1. **Real captures only.** No mockups, no AI-generated images, no invented
   metrics or results. The skill REFUSES to invent; it does not certify truth.
2. **Honesty is human-attested, not automated.** A skill cannot OCR a dashboard
   for client PII. Bill confirms each capture is clean against the checklist
   below; the scripts record `attested: true` and refuse to optimize/wire
   anything not attested.
3. **Pilot one page, then watch.** First run does ONE page. Do not bulk-apply.
   Re-check GSC indexing (backlog #5); 4-week time-box, then decide on EEAT
   merits if indexing is inconclusive (the sitewide demotion confounds it).
4. **No publish bypass.** This skill stages images + edits `html_content`; the
   site ships only through `/ship`.
5. **Worktree + `git pull` first** (multi-session git safety; local main runs
   behind origin).

## PII / data-leak checklist (the attestation gate)
Bill confirms EACH capture shows NONE of these before it can be used. This list
is the runtime source of truth in `scripts/ghl_capture_lib.py` (`PII_CHECKLIST`)
— it is reproduced here, do not paraphrase per run:
- Account / agency name in the top bar or profile menu
- Contacts, conversations, or any client list / client PII (name, email, phone)
- Notification bell contents and recent-activity feeds
- Billing, card, or payment-method details
- Autofill / browser dropdowns exposing saved data
- Any sub-account or location name that is not the throwaway sandbox

If any appears: re-frame/crop the screen and re-capture, or drop that image.

## Workflow

### Step 0 — Setup
- Confirm the GStack Browser is open and **Bill is logged into the GHL sandbox**
  (`app.reiamplifi.com`, location `t7MZYIDv56SJjcyTkdfd`; he logs in himself —
  localStorage tokens, headless login fails). Run `/connect-chrome` if needed.
- Work in a worktree off `origin/main`; `git pull` first.

### Step 1 — Pick the target + extract claims (JUDGMENT)
- Choose ONE post (`posts/<slug>.json`, note its `language`). Pilot recommendation:
  `gohighlevel-latam-pagos-agencias` (crawled today, fastest indexing signal).
- Read its `html_content`. List the factual/product claims a screenshot would
  substantiate (e.g. "MercadoPago is a native GHL payment provider" → Payments →
  Integrations screen). Decoration that proves no claim is NOT allowed.

### Step 2 — Write the capture plan (the skill→script handoff)
Produce a JSON array; show it to Bill as a table and get a yes before capturing:
```json
[
  {"name": "ghl-pagos-integraciones",
   "url_or_app_area": "https://app.reiamplifi.com/.../payments/integrations",
   "claim_supported": "MercadoPago appears as a native payment provider",
   "forbidden_overclaims": "Do not claim zero fees or instant settlement"}
]
```
`name` becomes the raw filename. Use a real URL when there is one; otherwise an
app-area label (the manifest stores `app-area:<label>` per spec finding N2).

### Step 3 — Capture (delegated)
```bash
cd globalhighlevel-site
python3 scripts/ghl_capture.py capture --plan /tmp/plan.json --slug <slug> --lang <lang>
```
Writes raws to `captures/<lang>/` and a manifest with machine-captured `url` +
`captured_at`. Does NOT log in, does NOT detect PII. **GHL is a heavy SPA** — the
script waits for `document.readyState=complete` then a paint delay before shooting
(`--settle` / `--settle-after`, defaults 8s/3s) so it captures the screen, not the
loading spinner. **Always Read the captured PNG before attesting** — a too-short
settle yields a spinner, and only your eyes catch it.

### Step 4 — Attest (Bill, at the keyboard)
Interactive: `python3 scripts/ghl_capture.py attest --slug <slug> --lang <lang>`
(walks each image against the PII checklist; y/N per image).
Non-interactive (when the decision was made elsewhere, e.g. a UI sign-off):
`python3 scripts/ghl_capture.py attest --slug <slug> --lang <lang> --name <img> --decision yes|no --by <who>`.
Either way sets `attested` + `attested_at` (+ `attested_by`). The decision MUST
originate from the human; the script only records it. Unattested images are
refused by optimize/wire.

### Step 5 — Optimize (delegated, Pillow)
```bash
python3 scripts/ghl_optimize_wire.py optimize --slug <slug> --lang <lang>
```
Attested raws → `images/<lang>/<slug>-<n>.png` (n = max+1, never overwrite).
Refuses anything not attested.

### Step 6 — Wire into the post (JUDGMENT picks the spot)
Choose a `--after` marker: a unique substring in `html_content` right where the
claim is made (usually the closing `</p>` of the claim's paragraph, or a unique
heading). Caption states only what the image shows.
```bash
python3 scripts/ghl_optimize_wire.py wire \
  --post <slug> --image /images/<lang>/<slug>-1.png \
  --alt "<honest alt>" --caption "<honest caption>" --after "</p>"
```
Inserts the site-standard `<figure class="post-figure">`. Refuses unless the
image is optimized AND attested. Cross-language reuse: pass the same image path
when wiring into another language's post.

### Step 7 — Orphan check (leak gate)
```bash
python3 scripts/ghl_optimize_wire.py orphan-check
```
Exit 1 if any published image is referenced by zero posts, or any post
references a missing file. Fix before shipping. (This currently flags the
pre-existing leak `ghl-payment-integrations-es.png` — resolve it as the first
real test by wiring it into a relevant post or deleting it.)

### Step 8 — Ship + watch
- Commit (raws + manifest in `captures/` are the committed audit trail). The
  manifest records the live sandbox URL as provenance; this is **repo-internal**
  — `build.py` copies only `images/`, never `captures/`, so provenance URLs never
  reach the live site. Keep `captures/` out of any published build.
- Ship the pilot page via **`/ship`** (never hand-rolled).
- Record the pilot page's GSC index status as the watch baseline; set a 4-week
  reminder. Hold bulk application until the indexing signal is read.

## Validation
`python3 scripts/test_ghl_capture.py` (pure-Python, no browser) covers naming,
the orphan check, attestation refusal, figure escaping, and the JSON round-trip.
