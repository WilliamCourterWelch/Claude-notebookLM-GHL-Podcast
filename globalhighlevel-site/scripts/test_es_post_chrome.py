#!/usr/bin/env python3
"""ES blog pages use LATAM Spanish template chrome. EN and en-IN stay English.

Asserts RENDERED HTML. Href, fp_ref, utm_content=cta3, the money-page CTA,
the Spotify URL, and the ghl_click listener must match across languages —
only the visible words change.

Run: python3 -m pytest scripts/test_es_post_chrome.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402


_BODY = (
    "<p>This fixture walks through the setup with enough words to count as an "
    "opening paragraph for the chrome test.</p>"
    '<h2 id="one">First step</h2>'
    "<p>Do the first step in the product and save before you move on to the "
    "next part of the setup.</p>"
    '<h2 id="two">Second step</h2>'
    "<p>Do the second step and check the result before you call the setup finished.</p>"
)

# English template strings that must not survive on an es page.
_EN_GONE = (
    "In This Guide",
    "Follow along",
    "get 30 days free",
    "This is built into GoHighLevel.",
    "Try it free for 30 days",
    "Ready to try this?",
    "Start Free 30-Day Trial",
    "Cancel anytime",
    "This tutorial also has a podcast episode",
    'Listen on Spotify — "Go High Level" podcast',
    "Listen to this episode",
    "Follow the podcast on Spotify",
    "The short version",
    "Copy Link",
    "Copied!",
    "More about me",
    "GoHighLevel Consultant",
    "Keep Reading",
    "Keep learning",
    "Affiliate disclosure:",
    "Free GoHighLevel tutorials, guides, and strategies",
    ">Topics<",
    ">Languages<",
    "Not affiliated with GoHighLevel LLC",
    "AI Receptionist &amp; Lead Capture",
)

_ES_GONE_ON_EN = (
    "En esta guía",
    "Sigue la guía",
    "30 días gratis",
    "Esto ya está en GoHighLevel.",
    "Pruébalo 30 días gratis",
    "¿Listo para probarlo?",
    "Empieza tu prueba de 30 días",
    "Cancela cuando quieras",
    "Este tutorial también está en podcast",
    "Escúchalo en Spotify",
    "Escucha este episodio",
    "Sigue el podcast en Spotify",
    "En corto",
    "Copiar enlace",
    "¡Copiado!",
    "Más sobre mí",
    "Consultor de GoHighLevel",
    "Sigue leyendo",
    "Sigue aprendiendo",
    "Aviso de afiliados",
    ">Temas<",
    ">Idiomas<",
    "No afiliado a GoHighLevel LLC",
    "Recepción con IA y captura de leads",
    "Pagos y precios",
)


def _post(lang: str, *, episode: str = "", tldr=None) -> dict:
    post = {
        "slug": f"chrome-fixture-{lang}",
        "title": "Chrome fixture guide",
        "description": "Fixture page used to pin template chrome language.",
        "html_content": _BODY,
        "language": lang,
        "topic": "Payments & Pricing",
        "publishedAt": "2026-10-22T00:00:00",
    }
    if episode:
        post["transistorEpisodeId"] = episode
    if tldr is not None:
        post["tldr"] = tldr
    return post


def _render(tmp_path, monkeypatch, post: dict, siblings: list[dict] | None = None) -> str:
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    monkeypatch.setattr(build, "LIVE_CATEGORY_SLUGS", {"payments-pricing"})
    build._ANCHOR_URL_COUNTS.clear()
    posts = siblings or [post]
    build.build_post_page(post, all_posts=posts)
    out = tmp_path / build.post_output_rel(post) / "index.html"
    return out.read_text(encoding="utf-8")


def _listener(html: str) -> str:
    m = re.search(r"document.addEventListener\(\"click\".*?</script>", html, re.S)
    assert m, "ghl_click listener missing"
    return m.group(0)


def _cta3_href(html: str) -> str:
    m = re.search(r'<div class="cta-end"[^>]*>[\s\S]*?<a href="([^"]+)" class="btn-amber"', html)
    assert m, "template cta-end button missing"
    return m.group(1)


def test_es_chrome_is_spanish_and_links_stay(tmp_path, monkeypatch):
    es = _post("es")
    en = _post("en")
    inn = _post("en-IN")
    # Siblings so related cards and the circle render. Same topic, same language
    # per page — get_related filters on language, so each render gets its own set.
    def siblings(lang):
        base = _post(lang)
        return [base, _post_sib(lang, 2), _post_sib(lang, 3)]

    es_html = _render(tmp_path / "es", monkeypatch, es, siblings("es"))
    en_html = _render(tmp_path / "en", monkeypatch, en, siblings("en"))
    in_html = _render(tmp_path / "in", monkeypatch, inn, siblings("en-IN"))

    for phrase in (
        "En esta guía",
        "Sigue la guía",
        "30 días gratis",
        "Esto ya está en GoHighLevel.",
        "Pruébalo 30 días gratis",
        "¿Listo para probarlo?",
        "$0 por 30 días",
        "~$1 para verificar la tarjeta",
        "sin cargo de suscripción",
        "Empieza tu prueba de 30 días",
        "Cancela cuando quieras",
        "$0 los primeros 30 días",
        "Este tutorial también está en podcast",
        'Escúchalo en Spotify — podcast "Go High Level"',
        "Compartir",
        "Copiar enlace",
        "¡Copiado!",
        "Consultor de GoHighLevel y automatización para agencias",
        "Más sobre mí",
        "Sigue leyendo",
        "Sigue aprendiendo:",
        "Aviso de afiliados:",
        "Tutoriales, guías y estrategias gratis de GoHighLevel",
        ">Temas<",
        ">Idiomas<",
        "No afiliado a GoHighLevel LLC",
        "Recepción con IA y captura de leads",
        "CRM y comunicación",
        "Sitios, embudos y reputación",
        "Pagos y precios",
        'aria-label="Menú"',
        'aria-label="Más en Payments & Pricing"',
    ):
        assert phrase in es_html, phrase

    for phrase in _EN_GONE:
        assert phrase not in es_html, phrase

    for phrase in (
        "In This Guide",
        "Follow along",
        "get 30 days free",
        "Ready to try this?",
        "Start Free 30-Day Trial",
        "This tutorial also has a podcast episode",
        "Keep Reading",
        "Keep learning:",
        "Affiliate disclosure:",
        ">Topics<",
        ">Languages<",
        "AI Receptionist &amp; Lead Capture",
        'aria-label="Menu"',
        'aria-label="More in Payments & Pricing"',
    ):
        assert phrase in en_html, phrase
        assert phrase in in_html, phrase

    for phrase in _ES_GONE_ON_EN:
        assert phrase not in en_html, phrase
        assert phrase not in in_html, phrase

    money = build.MONEY_PAGE_URL
    for html in (es_html, en_html, in_html):
        assert f'href="{money}" rel="nofollow">', html
        assert html.count(f'href="{money}"') >= 2  # byline + mid-article
        assert 'href="https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV"' in html
        assert 'href="/about/"' in html
        # Footer category URLs are the English hubs in every language.
        for path in (
            "/category/ai-receptionist-lead-capture/",
            "/category/crm-communication/",
            "/category/sites-funnels-reputation/",
            "/category/payments-pricing/",
        ):
            assert f'href="{path}"' in html

    assert _cta3_href(es_html) == build.affiliate_href("es", campaign="chrome-fixture-es", content="cta3")
    assert _cta3_href(en_html) == build.affiliate_href("en", campaign="chrome-fixture-en", content="cta3")
    assert _cta3_href(in_html) == build.affiliate_href("en-IN", campaign="chrome-fixture-en-IN", content="cta3")
    assert "highlevel-bootcamp-es?" in _cta3_href(es_html)
    assert "highlevel-bootcamp-es" not in _cta3_href(en_html)
    assert "highlevel-bootcamp-es" not in _cta3_href(in_html)
    for href in (_cta3_href(es_html), _cta3_href(en_html), _cta3_href(in_html)):
        assert "fp_ref=amplifi-technologies12" in href
        assert "utm_content=cta3" in href
        assert "cta_slot=" not in href

    # The click listener is language-blind. link_text is read from the DOM.
    assert "ghl_click" in es_html
    assert _listener(es_html) == _listener(en_html) == _listener(in_html)
    assert 'cta_slot:String(slot)' in _listener(es_html)
    assert 'qs.get("utm_content")' in _listener(es_html)


def test_es_episode_and_tldr_labels(tmp_path, monkeypatch):
    ep = _post("es", episode="abc123")
    html = _render(tmp_path / "ep", monkeypatch, ep)
    assert "Escucha este episodio" in html
    assert "Sigue el podcast en Spotify" in html
    assert "Este tutorial también está en podcast" not in html
    assert 'src="https://share.transistor.fm/e/abc123"' in html
    assert "Listen to this episode" not in html

    en_ep = _post("en", episode="abc123")
    en_html = _render(tmp_path / "enep", monkeypatch, en_ep)
    assert "Listen to this episode" in en_html
    assert "Follow the podcast on Spotify" in en_html
    assert "Escucha este episodio" not in en_html
    assert 'src="https://share.transistor.fm/e/abc123"' in en_html

    tldr = _post("es", tldr=["La versión corta del fixture."])
    tldr_html = _render(tmp_path / "tldr", monkeypatch, tldr)
    assert "En corto" in tldr_html
    assert "The short version" not in tldr_html
    assert "Sigue la guía" not in tldr_html  # byline CTA drops when tldr is set
    assert "Follow along" not in tldr_html

    en_tldr = _post("en", tldr=["The short answer for the fixture."])
    en_tldr_html = _render(tmp_path / "entldr", monkeypatch, en_tldr)
    assert "The short version" in en_tldr_html
    assert "En corto" not in en_tldr_html
    assert "Follow along" not in en_tldr_html


def _post_sib(lang: str, n: int) -> dict:
    post = _post(lang)
    post["slug"] = f"chrome-fixture-{lang}-{n}"
    post["title"] = f"Sibling guide {n}"
    return post
