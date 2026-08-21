#!/usr/bin/env python3
"""Gate for the per-language hub <title> override (v0.3.11.1).

The language hubs (/es/, /in/, /ar/) rendered a bare label — "GoHighLevel
India" — which tells a searcher nothing. /in/ drew 131 Bing impressions at
position 4.2 and ZERO clicks over the 75-day window ending 2026-08-18.

Both edges are pinned, per the gate doctrine in CLAUDE.md ("a gate tested on
only one edge is half-tested"):
  - the override FIRES for en-IN, or the change is decorative;
  - it stays QUIET for every other language, or it silently rewrites hubs it
    was never meant to touch.

The count is asserted to be interpolated rather than literal, because a
hardcoded "145" rots the moment a post publishes.

Run: python3 -m pytest scripts/test_hub_titles.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import hub_title_for  # noqa: E402


SUFFIX = " | Global High Level"  # base_html appends this; 20 chars


def test_india_override_fires():
    t = hub_title_for("en-IN", "India", 145)
    assert t == "GoHighLevel India: 145 Guides, UPI and WhatsApp", t
    # Assert on the RENDERED length, suffix included — asserting on the bare
    # helper output would pass while the real SERP title overflowed.
    # (Codex adversarial review, 2026-08-20.)
    assert len(t + SUFFIX) <= 70, f"rendered title too long: {len(t + SUFFIX)}"
    # The payoff itself must clear truncation even when the suffix is cut.
    assert len(t) <= 55, f"payoff does not fit before truncation: {len(t)}"


def test_no_bare_ampersand_in_titles():
    """base_html interpolates titles with no HTML escaping (build.py:1610), so a
    bare `&` ships unescaped into <title>/og:title. Don't add new instances."""
    for code, name in (("en-IN", "India"), ("es", "Español"), ("ar", "العربية")):
        for page in (1, 3):
            t = hub_title_for(code, name, 145, page)
            assert "&" not in t, f"{code} p{page} emits a bare ampersand: {t!r}"


def test_count_is_interpolated_not_hardcoded():
    """A literal would make the title lie as soon as a post publishes."""
    a = hub_title_for("en-IN", "India", 145)
    b = hub_title_for("en-IN", "India", 146)
    assert a != b, "post count is not interpolated into the India hub title"
    assert "146" in b, b


def test_other_languages_keep_the_default():
    """The quiet edge. Without this, an override typo silently renames every
    other hub."""
    cases = [
        ("es", "Español", "GoHighLevel Español"),
        ("ar", "العربية", "GoHighLevel العربية"),
        ("en", "English", "GoHighLevel English"),
        ("fr", "Français", "GoHighLevel Français"),
    ]
    for code, native, expected in cases:
        got = hub_title_for(code, native, 42)
        assert got == expected, f"{code}: expected {expected!r}, got {got!r}"
        assert str(42) not in got, f"{code} leaked a post count into a default title"


def test_unknown_language_does_not_crash():
    assert hub_title_for("zz", "Klingon", 0) == "GoHighLevel Klingon"


def test_paginated_pages_do_not_claim_the_full_inventory():
    """/in/page/9/ renders a single card. Repeating "145 Guides" there would
    overstate that page AND give nine pages one identical indexable title.
    (Codex adversarial review, 2026-08-20.)"""
    p1 = hub_title_for("en-IN", "India", 145, 1)
    p9 = hub_title_for("en-IN", "India", 145, 9)

    assert "145" in p1, p1
    assert "145" not in p9, f"page 9 still claims the full inventory: {p9!r}"
    assert "Guides" not in p9, f"page 9 still implies a count: {p9!r}"
    assert p9.endswith("Page 9"), p9
    assert p1 != p9, "paginated pages share a title"

    # Every page must be distinct, or they compete as duplicates.
    titles = [hub_title_for("en-IN", "India", 145, n) for n in range(1, 10)]
    assert len(set(titles)) == 9, "duplicate hub titles across pagination"


def test_default_languages_also_paginate_uniquely():
    """The quiet edge still has to paginate — es/ar had the same duplicate-title
    problem before this change and must not keep it."""
    es = [hub_title_for("es", "Español", 40, n) for n in range(1, 5)]
    assert len(set(es)) == 4, "Spanish hub pages share a title"
    assert es[0] == "GoHighLevel Español", es[0]
    assert es[2].endswith("Page 3"), es[2]
    assert "Guides" not in es[2], "default path leaked the India wording"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
