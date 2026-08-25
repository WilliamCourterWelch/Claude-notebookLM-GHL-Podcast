#!/usr/bin/env python3
"""Gate for SERP title composition (v0.3.15.0).

Caleb Ulku's non-local SEO canon puts title tags at 50-60 characters — see
`lessons/12-non-local-seo/click-through-rate-ctr-analysis.md` in the AI SEO
Mastery Pro corpus — which is also roughly where Google truncates. Every title
call site in build.py used to append " | Global High Level" unconditionally.

Measured across the whole built tree on 2026-08-25, before the fix:

    median title      83 chars
    in the 50-60 band  1% (10 of 980)
    over 60 chars     95% (936 of 980)

20 of those characters were the brand suffix, on 973 of 980 pages. `compose_title`
now appends it only when the result still fits, which takes the median to 63c and
moves 33% into the band.

The brand survives on any base of 40 characters or fewer — 44 pages as built on
2026-08-25: 28 blog-pagination pages, 12 category pages, 2 short blog posts, and
the /es/ and /ar/ hubs. An earlier draft of this file said "all /page/N/
pagination", which was drawn from the shortest few of a sorted list and was wrong
for 16 of the 44.

Both edges are pinned, per the gate doctrine in CLAUDE.md:
  - the brand is KEPT when it fits, or the fix silently strips brand from every
    page including the ones with room for it;
  - the brand is DROPPED when it does not, or the fix does nothing at all.

The corpus-wide count is ratcheted separately, in verify.py Check 7, because it
reads built output. 590 pages are still over 60 on their own words.

Run: python3 -m pytest scripts/test_title_length.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import SITE_NAME, TITLE_MAX, compose_title  # noqa: E402


SUFFIX = f" | {SITE_NAME}"


def test_brand_is_kept_when_it_fits():
    """The firing edge. /page/N/ is the real case: its own title is the bare
    string "Page 2", which says nothing without the brand."""
    got = compose_title("Page 2")
    assert got == f"Page 2{SUFFIX}", got
    assert len(got) <= TITLE_MAX


def test_brand_is_dropped_when_it_does_not_fit():
    """The quiet edge. This title plus the 20-char suffix runs past the line, so
    the suffix goes and the page keeps its own words.

    Deliberately no hardcoded character counts in this docstring. An earlier
    draft said "46 chars ... is 66" when the string is 47 and composes to 67 —
    the third unverified number stated in a comment on 2026-08-25, after the
    survivor-cohort claim and a test-count claim. The assertion below computes
    it instead, so the fixture cannot silently stop exercising the drop path.
    """
    base = "GoHighLevel India: 145 Guides, UPI and WhatsApp"
    assert len(base) + len(SUFFIX) > TITLE_MAX, "fixture no longer exercises the drop"
    assert compose_title(base) == base


def test_boundary_is_exactly_title_max():
    """Off-by-one guard: a composed title of exactly TITLE_MAX is allowed,
    TITLE_MAX + 1 is not."""
    fits = "x" * (TITLE_MAX - len(SUFFIX))
    assert compose_title(fits) == fits + SUFFIX
    assert len(compose_title(fits)) == TITLE_MAX

    one_over = "x" * (TITLE_MAX - len(SUFFIX) + 1)
    assert compose_title(one_over) == one_over


def test_never_makes_a_title_longer_than_it_had_to_be():
    """The helper may return something over TITLE_MAX only when the caller's own
    words already exceed it. It must never push a title over the line itself."""
    for base in ("Short", "Page 12", "x" * 40, "x" * 59, "x" * 61, "x" * 120):
        got = compose_title(base)
        if len(got) > TITLE_MAX:
            assert got == base, f"composer pushed {base!r} over the limit: {got!r}"


def test_does_not_double_append_an_existing_suffix():
    """A caller that already composed its own branded title must not get the
    brand twice.

    The fixture is deliberately SHORT. A long pre-branded title masks this bug
    entirely — the second suffix would be dropped for length anyway — so a test
    written with a long fixture passes while the defect is live. That is exactly
    how it shipped for one commit on 2026-08-25: `compose_title("Home | Global
    High Level")` returned "Home | Global High Level | Global High Level".
    """
    short_already_branded = f"Home{SUFFIX}"
    assert len(short_already_branded) + len(SUFFIX) <= TITLE_MAX, (
        "fixture is too long to exercise the double-append path"
    )
    got = compose_title(short_already_branded)
    assert got.count(SITE_NAME) == 1, f"brand appears twice: {got!r}"
    assert got == short_already_branded


def test_title_max_matches_caleb_canon():
    """If someone widens the budget, make them do it deliberately. Caleb's
    lesson says 50-60 characters; 60 is the ceiling."""
    assert TITLE_MAX == 60, f"TITLE_MAX drifted from Caleb's 60: {TITLE_MAX}"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
