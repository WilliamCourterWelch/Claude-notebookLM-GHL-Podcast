# Fact ledger — copiar-templates-temporizadores-gohighlevel rebuild (2026-07-31)

Every claim the rebuilt post attributes to HighLevel documentation, with the
article it came from and the date that article was fetched. Sources were
enumerated by help-center FOLDER first (Step 0a), not by search-hit sampling.

Research vault (full chain: fetch-budget logs, critiques, third-voice passes):
`globalhighlevel-system/` → `source/ghl-countdown-timer-canonical-2026-07-30.md`,
`source/ghl-payments-whatsapp-docs-corpus-2026-07-30.md`,
`research-vault/critiques/copiar-templates-thirdvoice-{codex,claude-adversarial,verify}-2026-07-30.md`.

Corpus enumerated: portal search "countdown timer" → 10-article product folder
(getting started, fixed, recurring, editing, emails, funnels, email-funnel sync,
timezone adaptation, WhatsApp templates, placeholder).

| # | Claim in the post | Source | Fetched | Tag |
|---|---|---|---|---|
| 1 | Timers are created at Marketing > Countdown Timer | help article 155000003100 (mod. 2024-09-19) | 2026-07-30 | vendor-claimed |
| 2 | Three types: fijo / recurrente / dinámico, with the Black Friday + "resets after reaching zero" + "personalized per user" definitions | 155000003100 | 2026-07-30 | verbatim (translated) |
| 3 | On expiry an expiry image redirects to the expired page; in funnels it shows automatically | 155000003100 | 2026-07-30 | verbatim (translated) |
| 4 | Email insert flow (Marketing > Countdown Timer → Email Marketing template → insert element → design → align/background/padding → copy redirection link for buttons) | 155000003101 (mod. 2024-09-19) | 2026-07-30 | verbatim (translated) |
| 5 | Email timers are "typically implemented as GIFs", count from each open "for up to 60 seconds", refresh on reopen | 155000003101 | 2026-07-30 | verbatim (translated, hedge preserved) |
| 6 | "Apple Mail caches GIFs" so the timer "may appear to stop ticking after the first open" | 155000003101 | 2026-07-30 | verbatim (translated, hedge preserved) |
| 7 | Clone purpose: brand symmetry + reduce time to build a new channel by starting from an existing template | 155000001458 (mod. 2024-01-11) | 2026-07-30 | verbatim (translated) |
| 8 | Clone steps (hover → three dots → "Clone Template" → confirm; second path from inside the template; title editable after) | 155000001458 | 2026-07-31 | verbatim (translated) |
| 9 | "Agency admins have the access to clone templates" | 155000001458 | 2026-07-31 | verbatim |
| 10 | The documentation describes NO special timer behavior on clone (absence claim) | 155000001458 + Wait-action article 155000002470, both read in full | 2026-07-30 | summary (verified absence) |

## The removed premise (why this rebuild exists)

The pre-rebuild body asserted 5x that copying/cloning a template breaks,
desyncs or resets its countdown timer. The full 5-class fetch budget was run
and returned ZERO corroboration:

| Source class | Result |
|---|---|
| Official canonical (Wait action 155000002470) | silent on copy/clone |
| Vendor docs (clone-templates 155000001458) | no timer statement |
| Site-specific (portal search "clone templates") | nothing on breakage |
| General web | only Adobe Campaign / Marketo threads, zero GHL |
| Forum/community (reddit-scoped) | zero GHL reports |

Verdict: `[out-of-scope]` — unpublishable in any form. The rebuild explains the
documented GIF mechanism instead, and `scripts/test_timer_break_premise.py`
blocks reintroduction in Spanish posts.

## Known gaps carried out of this release

- The English and en-IN siblings still assert the removed premise (filed as a
  follow-up; the Spanish gate does not cover them by design).
- `hide-countdown-timers-gohighlevel-apple-mail-fix` states a contradictory
  mechanism ("JavaScript or CSS-based animations", "renders as a static
  image") — also filed.
- No provenance/citation gate exists: removing a false claim is now gated,
  asserting a NEW false one is still reviewer-only.
