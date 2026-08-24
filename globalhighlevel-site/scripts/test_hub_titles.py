#!/usr/bin/env python3
"""Gate for the per-language hub <title> override (v0.3.12.0, es added v0.3.13.0).

The language hubs (/es/, /in/, /ar/) rendered a bare label — "GoHighLevel
India" — which tells a searcher nothing. /in/ drew 131 Bing impressions at
position 4.2 and ZERO clicks over the 75-day window ending 2026-08-18; /es/
drew 25 at position 6.9, also zero, in the 2026-08-24 pull.

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
ES_POST_COUNT = 249  # production Spanish corpus size as of v0.3.13.0


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
        ("ar", "العربية", "GoHighLevel العربية"),
        ("en", "English", "GoHighLevel English"),
        ("fr", "Français", "GoHighLevel Français"),
        ("pt", "Português", "GoHighLevel Português"),
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
    """The quiet edge still has to paginate — the default path had the same
    duplicate-title problem before v0.3.12.0 and must not regain it. Uses `ar`
    because `es` became an override in v0.3.13.0."""
    ar = [hub_title_for("ar", "العربية", 40, n) for n in range(1, 5)]
    assert len(set(ar)) == 4, "Arabic hub pages share a title"
    assert ar[0] == "GoHighLevel العربية", ar[0]
    assert ar[2].endswith("Page 3"), ar[2]
    assert "Guides" not in ar[2], "default path leaked the India wording"
    assert "Guías" not in ar[2], "default path leaked the Spanish wording"


def test_spanish_override_fires():
    """/es/ drew 25 Bing impressions at position 6.9 with ZERO clicks against a
    bare "GoHighLevel Español" (2026-08-24 pull) — the same defect /in/ had."""
    p1 = hub_title_for("es", "Español", ES_POST_COUNT)
    assert p1 == f"GoHighLevel en Español: {ES_POST_COUNT} Guías Paso a Paso", p1

    # Assert at the PRODUCTION count, and in BYTES: accented characters cost two
    # bytes each, so a character-length check passes while the real title
    # overflows. (Codex adversarial review, 2026-08-24.)
    rendered = p1 + SUFFIX
    assert len(rendered.encode("utf-8")) <= 75, (
        f"rendered title {len(rendered.encode('utf-8'))} bytes "
        f"({len(rendered)} chars) — too long for the SERP"
    )

    # Same pagination rule as en-IN: page 1 carries the count, later pages do not.
    p4 = hub_title_for("es", "Español", ES_POST_COUNT, 4)
    assert str(ES_POST_COUNT) not in p4, f"page 4 claims the full inventory: {p4!r}"
    assert "Guías" in p4, p4
    titles = [hub_title_for("es", "Español", ES_POST_COUNT, n) for n in range(1, 6)]
    assert len(set(titles)) == 5, "duplicate Spanish hub titles across pagination"

    # Count interpolated, not literal.
    assert hub_title_for("es", "Español", ES_POST_COUNT + 1) != p1


def test_spanish_pagination_is_not_english():
    """A Spanish hub reading "— Page 2" ships English UI copy to a Spanish
    audience. (Codex adversarial review, 2026-08-24.)"""
    p2 = hub_title_for("es", "Español", ES_POST_COUNT, 2)
    assert p2.endswith("Página 2"), p2
    assert "Page" not in p2, f"English pagination word on a Spanish hub: {p2!r}"
    # en-IN is an English-language hub, so it correctly keeps "Page".
    assert hub_title_for("en-IN", "India", 145, 2).endswith("Page 2")

    # DELIBERATE: paginated titles are allowed past the page-1 byte budget
    # (/es/page/2/ renders 77 bytes). Hub pagination is not a ranking target —
    # page 1 is. The requirement here is that each page is DISTINCT and HONEST,
    # not that it fits a SERP. Asserted loosely so a runaway template still
    # fails, without pretending page 2 needs page 1's discipline.
    assert len((p2 + SUFFIX).encode("utf-8")) <= 100, p2


def test_spanish_title_does_not_overclaim_the_corpus():
    """lang_posts is EVERY Spanish post. 30 of the 249 are not agency-framed
    (restaurantes, belleza/salud, e-commerce, inmobiliarias, cupones, checkout),
    so the hub title must not call them all agency guides."""
    for page in (1, 3):
        t = hub_title_for("es", "Español", ES_POST_COUNT, page)
        assert "Agencias" not in t, f"title overclaims the corpus: {t!r}"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
