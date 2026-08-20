#!/usr/bin/env python3
"""Residual gate for UNDISCLOSED zero-cost trial claims.

test_trial_claims_residual.py catches the explicit phrasing ("no credit
card", "sin tarjeta"). It does not catch the implicit variant: a bare
"$0 to start" / "$0 al empezar" with no mention of the ~$1 card-verification
hold reads to a buyer as "no card required" while never using the words the
other gate matches. Same false promise, different sentence, zero coverage.

Found 2026-08-20 while adding in-body CTAs to the two pricing pages: four
newly drafted CTAs carried a bare "$0 upfront" / "$0 por adelantado". The
existing gate passed on all four. They were corrected by hand; this gate
makes the next one fail loudly instead.

The rule: a zero-cost claim is fine, but the same neighbourhood must carry a
disclosure — the ~$1 verification hold, or the truthful cancel line
("cancela cuando quieras" / "cancel any time").

Run: python3 -m pytest scripts/test_zero_cost_claims_disclosed.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

POSTS = Path(__file__).resolve().parents[1] / "posts"

# A claim that the trial costs nothing to begin.
ZERO_COST = re.compile(
    r"\$0\s+(?:to start|upfront|down|al empezar|por adelantado)",
    re.I,
)

# Any of these in the surrounding text makes the claim honest.
DISCLOSURE = re.compile(
    r"card-verification"
    r"|verificaci[oó]n de tarjeta"
    r"|~?\$1"
    r"|cancela cuando quieras"
    r"|cancel any time",
    re.I,
)

# How far either side of the claim we accept a disclosure. Wide enough to
# span the sentence and its neighbour, tight enough that a disclosure three
# paragraphs away does not launder an isolated claim.
WINDOW = 200

# (filename, substring) pairs where the phrase is NOT a claim about our trial
# — a competitor's pricing quoted for comparison, or the phrase cited as
# copy to avoid. Mirrors the ALLOWLIST in test_trial_claims_residual.py;
# without it an honest quotation has no way past the gate.
ALLOWLIST: list[tuple[str, str]] = []


def _walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _walk_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_strings(item)


def _post_files():
    files = sorted(POSTS.glob("*.json"))
    assert len(files) > 100, f"suspiciously few posts under {POSTS} ({len(files)})"
    return files


def test_zero_cost_claims_carry_a_disclosure():
    """Every '$0 to start'-style claim in the corpus must sit within WINDOW
    characters of the ~$1 hold or the truthful cancel line."""
    offenders = []
    for path in _post_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        for field, value in data.items():
            for s in _walk_strings(value):
                for m in ZERO_COST.finditer(s):
                    window = s[max(0, m.start() - WINDOW): m.end() + WINDOW]
                    if DISCLOSURE.search(window):
                        continue
                    ctx = s[max(0, m.start() - 60): m.end() + 60]
                    if any(path.name == fn and marker in ctx
                           for fn, marker in ALLOWLIST):
                        continue
                    offenders.append(f"{path.name}:{field}: ...{ctx!r}")
    assert not offenders, (
        "Undisclosed zero-cost trial claims (add the ~$1 card-verification "
        "hold or the cancel line near the claim):\n" + "\n".join(offenders)
    )


def test_gate_would_catch_a_bare_claim():
    """Guard the guard: the pattern must fire on the exact phrasing that
    slipped through on 2026-08-20, and stay quiet once disclosed."""
    bare = "Start your 30-day free trial — double the standard 14 days, $0 upfront."
    assert ZERO_COST.search(bare), "pattern no longer matches the regressed phrasing"
    assert not DISCLOSURE.search(bare), "bare claim should read as undisclosed"

    fixed = ("Start your 30-day free trial — double the standard 14 days, "
             "and you can cancel any time.")
    assert not ZERO_COST.search(fixed), "corrected copy should carry no zero-cost claim"

    disclosed = ("Try the full platform free for 30 days — full access, $0 to start, "
                 "just a ~$1 card-verification hold.")
    assert ZERO_COST.search(disclosed), "disclosed claim still contains the phrase"
    assert DISCLOSURE.search(disclosed), "disclosure not recognised"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
