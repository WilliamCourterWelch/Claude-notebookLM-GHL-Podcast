#!/usr/bin/env python3
"""Gate for the /es/ hub's pagination strip (v0.3.14.0).

/es/ page 1 is a curated hub: build_language_hub swaps in a hand-authored hero
and three topic clusters for `page == 1 and lang_code == "es"`, with no card
grid. Deliberate since v0.2.0.0 (commit 6a83e63, "MVP relaunch — EN+ES brand-hub
homepages") — but that branch also emitted no pagination, so /es/page/2..14/ had
ZERO inbound links AND no sitemap entry (no /page/ URL is sitemapped, by policy).
13 indexable pages, and the 231 Spanish posts they list, were reachable only by
guessing URLs. /in/ never had this: its page 1 takes the else branch, which
already emits pag_html, and it links /in/page/2..5/.

Both edges are pinned, per the gate doctrine in CLAUDE.md ("a gate tested on only
one edge is half-tested"):
  - the strip FIRES when there are pages to link, or the fix is decorative;
  - it stays EMPTY when there is nothing to paginate, or the heading renders
    above an empty strip.

The WIRING is pinned too. A helper that is correct, tested, and never called is
the exact shape of a fix that does not ship, so one test asserts that
build_language_hub really interpolates it into the Spanish page-1 body.

And the strip is pinned to make NO completeness claim. Page 1 consumes
lang_posts[0:18] and then discards those cards, so paging reaches 231 of the 249
Spanish posts. The first draft read "Las 249 guías en español / Explora todas las
guías" above a strip that delivers 231 — the same count-over-collection overclaim
that got caught three separate times on 2026-08-24 ("249 Guías para Agencias",
"145 Guides" on a one-card page, "Without Errors"). The count lives in the
<title>, where it describes the library; it must not reappear here.

Run: python3 -m pytest scripts/test_es_hub_pagination.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1] / "build.py"
sys.path.insert(0, str(BUILD.parent))
from build import es_library_block  # noqa: E402


# Shaped exactly like build_language_hub's pag_html.
PAG = (
    '<div class="pagination">'
    ' <a href="/es/" class="active">1</a>'
    ' <a href="/es/page/2/">2</a>'
    "</div>"
)


def test_strip_fires_when_there_are_pages():
    got = es_library_block(PAG)
    assert got, "strip is empty even though there are pages to link"
    assert "Explora la biblioteca" in got, got


def test_pagination_is_embedded_verbatim():
    """The strip must EMBED the caller's pag_html rather than rebuild its own.
    A second implementation would drift from the else-branch pagination it
    mirrors, and drift is how /es/ and /in/ diverged in the first place."""
    got = es_library_block(PAG)
    assert PAG in got, "pag_html was not embedded verbatim"
    assert "/es/page/2/" in got, "the orphaned page is still not linked"


def test_strip_is_empty_without_pagination():
    """The quiet edge. total_pages <= 1 leaves pag_html empty; rendering the
    heading anyway would put a library heading above an empty strip."""
    assert es_library_block("") == ""


def test_strip_makes_no_count_or_completeness_claim():
    """THE REGRESSION GUARD. Paging reaches 231 of 249 Spanish posts because
    page 1 slices off 18 and drops them. Any number, or any "todas/completa"
    phrasing, promises coverage this strip does not deliver. Three overclaims of
    exactly this shape shipped-and-were-caught on 2026-08-24; this pins the
    fourth from happening."""
    chrome = es_library_block(PAG).replace(PAG, "")  # drop caller-supplied markup
    # Only the VISIBLE copy makes claims. Strip tags so CSS values like
    # margin-top:56px don't read as a count.
    text = re.sub(r"<[^>]+>", " ", chrome)

    digits = re.findall(r"\d", text)
    assert not digits, f"strip reintroduced a count: {text!r}"

    lowered = text.lower()
    for claim in ("todas", "todos", "completa", "completo", "entera"):
        assert claim not in lowered, (
            f"strip claims completeness ({claim!r}) but reaches 231 of 249: {chrome!r}"
        )


def test_no_bare_ampersand():
    """base_html interpolates the body with no HTML escaping (build.py:1610),
    so a bare `&` would ship unescaped. Entities are fine; loose `&` is not."""
    got = es_library_block(PAG)
    bare = re.findall(r"&(?!#?\w+;)", got)
    assert not bare, f"bare ampersand in the strip: {got!r}"


ES_LANG_CONFIG = {"prefix": "/es", "code": "es", "native": "Español", "dir": "ltr"}


def _es_posts(n: int) -> list[dict]:
    """Minimal Spanish posts. `language` is set explicitly so post_lang() does
    not have to infer from the slug."""
    return [
        {
            "slug": f"guia-es-{i:03d}",
            "title": f"Guía de GoHighLevel {i:03d}",
            "language": "es",
            "description": "Descripción de prueba para el hub en español.",
            "html_content": "<p>Contenido de prueba.</p>",
            "publishedAt": f"2026-01-{(i % 28) + 1:02d}",
        }
        for i in range(n)
    ]


def _render_es_hub(tmp_path, monkeypatch, n_posts: int) -> str:
    """Render the real /es/ page 1 into a temp tree and return its HTML.

    build_language_hub reads PUBLIC_DIR as a module global at call time, so
    patching it redirects every write (and write()'s relative_to() print).
    """
    import build

    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build.build_language_hub(ES_LANG_CONFIG, _es_posts(n_posts))
    return (tmp_path / "es" / "index.html").read_text(encoding="utf-8")


def test_rendered_es_hub_links_every_paginated_page(tmp_path, monkeypatch):
    """THE PRODUCTION GATE. The helper being correct proves nothing if the hub
    never renders it — and a source-string assertion would pass on a comment, a
    non-f-string body, or an assigned-then-overwritten variable. So assert on
    the actual rendered page. (Codex adversarial review, 2026-08-24.)"""
    html = _render_es_hub(tmp_path, monkeypatch, 40)  # 40 posts @ 18/page -> 3 pages

    for page in (2, 3):
        assert f'href="/es/page/{page}/"' in html, (
            f"/es/ does not link /es/page/{page}/ — the orphaned-page defect is back"
        )
    # And the pages it links must actually exist on disk.
    for page in (2, 3):
        assert (tmp_path / "es" / "page" / str(page) / "index.html").exists()


def test_rendered_es_hub_keeps_the_curated_design(tmp_path, monkeypatch):
    """The quiet edge. Bill decided the brand-hub design stays; the pagination
    strip is additive. If a future edit swaps the body wholesale, catch it."""
    html = _render_es_hub(tmp_path, monkeypatch, 40)
    for marker in ("guidecard", "clusters", "es-banner", "hubsec"):
        assert marker in html, f"curated /es/ design lost its {marker!r} block"


def test_rendered_es_hub_makes_no_false_count_or_completeness_claim(
    tmp_path, monkeypatch
):
    """Page 1 slices off 18 posts and drops them, so the numbered path reaches
    n-18 of n. Nothing on the rendered page may claim otherwise — not the
    <title>, not the hero, not the strip. This is the gate that would have
    caught "249 Guías y Precios"."""
    n = 40
    html = _render_es_hub(tmp_path, monkeypatch, n)

    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)

    assert str(n) not in text, (
        f"rendered /es/ claims {n} guides but the numbered path reaches {n - 18}"
    )
    lowered = text.lower()
    for claim in ("todas las gu", "biblioteca completa", "biblioteca entera"):
        assert claim not in lowered, f"rendered /es/ claims completeness: {claim!r}"


def test_rendered_es_paginated_pages_make_no_false_count_claim(tmp_path, monkeypatch):
    """/es/page/2/ rendered "249 guides in Español" — wrong twice: a count the
    numbered path cannot deliver (page 1 discards the first 18), and English UI
    copy on a Spanish page, the defect v0.3.13.0 fixed in the <title>. The
    page-1 gate above misses this because it only reads /es/.
    (Codex adversarial re-review, 2026-08-24.)"""
    n = 40
    _render_es_hub(tmp_path, monkeypatch, n)
    html = (tmp_path / "es" / "page" / "2" / "index.html").read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", html)

    # The two CORPUS-level claims. Per-category chip counts are deliberately NOT
    # banned here — those are honest, because /es/category/<x>/ really does list
    # every post it counts. Only claims about the whole Spanish corpus are false,
    # since the numbered path drops the first 18.
    assert "guides in" not in text, "English UI copy on a Spanish hub page"
    assert f"All ({n})" not in text, (
        f"/es/page/2/ chip claims {n} guides; the numbered path reaches {n - 18}"
    )
    assert "Todas" in text, "Spanish hub lost its localized all-topics chip"


def test_rendered_english_hubs_keep_their_honest_count(tmp_path, monkeypatch):
    """The quiet edge for the es-only subtitle. /in/ page 1 takes the else
    branch: it renders cards AND links every paginated page, so its count is
    honest and must survive. Without this, the Spanish carve-out silently
    strips the count from every language."""
    import build

    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    posts = [dict(p, language="en-IN") for p in _es_posts(40)]
    build.build_language_hub(
        {"prefix": "/in", "code": "en-IN", "native": "India", "dir": "ltr"}, posts
    )
    html = (tmp_path / "in" / "index.html").read_text(encoding="utf-8")

    assert "40 guides in India" in html, "English hub lost its honest count"
    assert 'href="/in/page/2/"' in html, "English hub lost its pagination"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
