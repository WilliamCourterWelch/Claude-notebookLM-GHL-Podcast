#!/usr/bin/env python3
"""Residual gate for false trial claims (the ~$1 card-verification truth).

correct_trial_claims() is an ordered exact-phrase table — by design it fails
open: a phrase variant the table doesn't cover renders a false "no credit
card" claim with no error. This gate makes that failure loud and automatic
(it was a manual, casing-blind scan before 2026-07-28, which let Title-Case
variants and the trial post's own <title> ship false claims).

Three checks:
1. Ordering invariant — the table is specific-before-generic; a sentence
   entry appended after a bare catch-all would silently never match.
2. Entry behavior — the sentence-level Spanish entries fire and are
   idempotent (f(f(x)) == f(x)).
3. Corpus residual — apply the table to every nested string of every post
   (plus titles, which the post renderer does NOT route through the table)
   and assert a case-insensitive no-card pattern finds nothing outside the
   explicit allowlist.

Run: python3 -m pytest scripts/test_trial_claims_residual.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import _TRIAL_CLAIM_FIXES, correct_trial_claims  # noqa: E402

POSTS = Path(__file__).resolve().parents[1] / "posts"

RESIDUAL = re.compile(
    r"(?:sin (?:solicitar )?tarjeta(?: de crédito)?"
    r"|no (?:necesitas|se requiere|requiere|hace falta) (?:una )?tarjeta"
    r"|no credit card"
    r"|without (?:a )?credit card)",
    re.I,
)

# (filename, substring) pairs that legitimately contain the phrase.
ALLOWLIST = [
    # spam-trigger vocabulary example — the phrase is quoted as a word to
    # AVOID, not a claim about the trial; a blanket swap would corrupt it
    ("fix-spam-filter-blocks-gohighlevel-boost-deliverability.json",
     "Act Now, Guarantee, No Credit Card, Risk-Free"),
]


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


def test_table_ordering_invariant():
    """No earlier (more specific) old-phrase may be a substring of a later
    old-phrase — the earlier replacement would mangle the later match and
    the later entry would silently never fire."""
    olds = [old for old, _ in _TRIAL_CLAIM_FIXES]
    bad = [
        (i, j)
        for i in range(len(olds))
        for j in range(i + 1, len(olds))
        if olds[i] in olds[j]
    ]
    assert not bad, (
        "Mis-ordered _TRIAL_CLAIM_FIXES entries (specific must come before "
        "generic): " + ", ".join(f"#{i} {olds[i]!r} inside #{j} {olds[j]!r}" for i, j in bad)
    )


def test_new_spanish_entries_fire_and_are_idempotent():
    cases = [
        ("No. La prueba de 30 días no requiere tarjeta de crédito. Solo "
         "necesitas un email válido para crear tu cuenta.", "Casi:"),
        ("La prueba es completamente gratuita y no requiere tarjeta de crédito.", "~$1"),
        ("No necesitas tarjeta de crédito. Solo tu email.", "~$1"),
        ("No necesitas tarjeta de crédito. Configura en 5 minutos.", "~$1"),
        ("(Sin Tarjeta de Crédito)", "~$1"),
        ("(No Credit Card)", "~$1"),
        ("No Credit Card Needed", "~$1"),
        ("prueba GRATIS de 30 días sin solicitar tarjeta de crédito", "~$1"),
    ]
    for src, must_contain in cases:
        out = correct_trial_claims(src)
        assert must_contain in out, f"entry did not fire on {src!r} -> {out!r}"
        assert not RESIDUAL.search(out), f"residual survives correction: {src!r} -> {out!r}"
        assert correct_trial_claims(out) == out, f"not idempotent: {src!r}"


def test_no_rendered_residual_claims_in_corpus():
    """Approximate the render: run every nested string of every post (and the
    title, which build.py never routes through the table) through
    correct_trial_claims, then scan case-insensitively."""
    offenders = []
    for path in _post_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        for field, value in data.items():
            for s in _walk_strings(value):
                corrected = correct_trial_claims(s)
                for m in RESIDUAL.finditer(corrected):
                    ctx = corrected[max(0, m.start() - 40):m.end() + 40]
                    if any(path.name == fn and marker in ctx for fn, marker in ALLOWLIST):
                        continue
                    # question-forms are intentionally untouched — the paired
                    # answers carry the correction (table design note)
                    tail = corrected[m.end():m.end() + 3]
                    if "?" in tail or "؟" in tail:
                        continue
                    offenders.append(f"{path.name}:{field}: ...{ctx!r}")
    assert not offenders, (
        "False trial claims survive correct_trial_claims (extend "
        "_TRIAL_CLAIM_FIXES or fix the stored text):\n" + "\n".join(offenders)
    )


if __name__ == "__main__":
    test_table_ordering_invariant()
    test_new_spanish_entries_fire_and_are_idempotent()
    test_no_rendered_residual_claims_in_corpus()
    print("ALL TESTS PASSED")
