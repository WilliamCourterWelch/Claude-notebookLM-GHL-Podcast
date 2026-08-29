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

The rule: a zero-cost claim is fine, but the same neighbourhood must carry
the ~$1 card-verification disclosure. A cancellation promise ("cancel any
time" / "cancela cuando quieras") does NOT satisfy it — see the note on
DISCLOSURE below.

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
#
# `_D` matches a dollar sign however the HTML spells it (literal, numeric
# entity, named entity); `_SP` matches whitespace including &nbsp;. Without
# those the gate reads only the prettiest spelling and misses the rest.
_D = r"(?:\$|&#0*36;|&dollar;)"
_SP = r"(?:\s|&nbsp;|&#0*160;)+"
ZERO_COST = re.compile(
    # "$0 to start" / "$0 today" / "$0 al empezar" ...
    rf"{_D}0{_SP}(?:to start|today|due today|due|upfront|up front|down"
    rf"|al empezar|por adelantado|hoy)"
    # "starts at $0" / "pay nothing to start" / "free to start"
    rf"|starts?{_SP}at{_SP}{_D}0"
    rf"|pay{_SP}nothing{_SP}(?:to start|today|upfront)"
    rf"|free{_SP}to{_SP}start"
    rf"|gratis{_SP}para{_SP}empezar",
    re.I,
)

# What counts as an honest disclosure: the ~$1 card-verification hold, in
# either language. NOTE: a cancellation promise ("cancel any time" /
# "cancela cuando quieras") is deliberately NOT accepted here. It speaks to
# the cancellation policy, not to what the card is charged at signup, so
# "$0 upfront, cancel any time" would otherwise sail through while still
# implying no card is required. (Codex adversarial review, 2026-08-20.)
DISCLOSURE = re.compile(
    r"card-verification"
    r"|card verification"
    r"|verificaci[oó]n de tarjeta"
    rf"|~?{_D}1",
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
    characters of the ~$1 card-verification hold."""
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


def test_cancellation_promise_is_not_a_cost_disclosure():
    """A cancellation promise says nothing about what the card is charged at
    signup. Accepting it would let '$0 upfront, cancel any time' ship while
    still implying no card is needed. (Codex adversarial review, 2026-08-20.)"""
    for laundered in (
        "$0 upfront, cancel any time.",
        "Empieza con $0 por adelantado, cancela cuando quieras.",
    ):
        assert ZERO_COST.search(laundered), f"claim not detected: {laundered!r}"
        assert not DISCLOSURE.search(laundered), (
            f"cancellation promise wrongly accepted as a cost disclosure: {laundered!r}"
        )


def test_gate_catches_spelling_variants():
    """The corpus is HTML written by several hands. A gate that only reads
    one spelling of the claim is a gate in name only."""
    for variant in (
        "$0 today",
        "$0 due today",
        "starts at $0",
        "pay nothing to start",
        "free to start",
        "gratis para empezar",
        "&#36;0 to start",
        "$0&nbsp;to start",
    ):
        assert ZERO_COST.search(variant), f"variant not detected: {variant!r}"

    # And it must not fire on unrelated money copy.
    for innocent in (
        "SaaS Pro is $497/month.",
        "Annual billing knocks roughly 17% off.",
        "The platform replaces $0-to-$500 worth of niche tools.",
    ):
        assert not ZERO_COST.search(innocent), f"false positive on {innocent!r}"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
