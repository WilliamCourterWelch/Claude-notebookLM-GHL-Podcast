#!/usr/bin/env python3
"""Gate for the /in/ page-1 upgrade (2026-09-22).

/in/ was a card grid with a bare H1. The upgrade prepends a curated intro
and keeps the cards. Dropping the cards to copy /es/ would make the
interpolated "N Guides" title a lie.

Both edges are pinned on rendered HTML:
  - the intro FIRES on /in/ page 1, with the Razorpay SaaS-Mode limit, the
    bootcamp CTA, and links into the live India clusters;
  - it stays OFF /es/, /ar/, and /in/page/2/.

Run: python3 -m pytest scripts/test_in_hub.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

IN_CONFIG = {"prefix": "/in", "code": "en-IN", "native": "India", "dir": "ltr"}
ES_CONFIG = {"prefix": "/es", "code": "es", "native": "Español", "dir": "ltr"}
AR_CONFIG = {"prefix": "/ar", "code": "ar", "native": "العربية", "dir": "rtl"}

IN_DESC = (
    "WhatsApp, Razorpay, and white-label for Indian agencies. "
    "Razorpay does not bill SaaS Mode. "
    "UPI is Razorpay checkout, not its own HighLevel row. Card required."
)


def _posts(n: int, language: str) -> list[dict]:
    return [
        {
            "slug": f"guide-{language}-{i:03d}",
            "title": f"Guide {i:03d}",
            "language": language,
            "description": "A test description for the hub.",
            "html_content": "<p>Test body.</p>",
            "publishedAt": f"2026-01-{(i % 28) + 1:02d}",
        }
        for i in range(n)
    ]


def _render(tmp_path, monkeypatch, config: dict, n: int = 40) -> str:
    import build

    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build.build_language_hub(config, _posts(n, config["code"]))
    prefix = config["prefix"].strip("/")
    return (tmp_path / prefix / "index.html").read_text(encoding="utf-8")


def _visible(html: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


def test_in_page_one_renders_the_intro_and_keeps_the_cards(tmp_path, monkeypatch):
    html = _render(tmp_path, monkeypatch, IN_CONFIG, 40)

    assert html.count("<h1") == 1, "page 1 should have exactly one h1"
    assert "GoHighLevel for <em>Indian agencies</em>" in html
    assert "does not bill SaaS Mode" in html
    assert "UPI is not its own row" in html
    assert "PayU is not in the provider table" in html
    assert "About a $1 verification hold" in html
    assert "40 guides in India" in html
    assert 'class="cards-grid"' in html
    assert 'href="/in/page/2/"' in html
    assert "GoHighLevel India: 40 Guides, UPI and WhatsApp" in html

    for href in (
        "/blog/gohighlevel-pricing-india-2026-rupees-complete-guide/",
        "/blog/how-to-accept-razorpay-upi-payments-in-gohighlevel-india/",
        "/blog/gohighlevel-whatsapp-business-api-setup-india/",
        "/blog/how-indian-saas-companies-white-label-gohighlevel/",
        "/in/category/crm-communication/",
        "/in/category/payments-pricing/",
        "/in/category/agency-white-label-saas/",
        "155000002559-how-to-integrate-razorpay-within-the-crm",
        "155000006075-supported-payment-providers-methods-by-product-area",
        "155000001980-how-to-set-up-whatsapp-for-a-sub-account",
    ):
        assert href in html, href

    assert "fp_ref=amplifi-technologies12" in html
    assert "utm_content=hub_cta" in html
    assert "utm_campaign=in-hub" in html
    assert "highlevel-bootcamp?" in html or "highlevel-bootcamp&" in html
    assert "highlevel-bootcamp-es" not in html
    assert 'rel="nofollow noopener"' in html
    assert "no credit card" not in html.lower()
    assert "$0" not in html
    assert len(IN_DESC) in range(150, 161), len(IN_DESC)
    assert IN_DESC in html


def test_intro_does_not_leak_onto_later_pages_or_other_hubs(tmp_path, monkeypatch):
    """The quiet edge. A copy-paste of the intro onto /es/ or /in/page/2/
    would either ship English payment law onto Spanish, or repeat a page-1
    essay on a catalog page."""
    import build

    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build.build_language_hub(IN_CONFIG, _posts(40, "en-IN"))
    build.build_language_hub(ES_CONFIG, _posts(40, "es"))
    build.build_language_hub(AR_CONFIG, _posts(4, "ar"))

    page2 = (tmp_path / "in" / "page" / "2" / "index.html").read_text(encoding="utf-8")
    es = (tmp_path / "es" / "index.html").read_text(encoding="utf-8")
    ar = (tmp_path / "ar" / "index.html").read_text(encoding="utf-8")

    # The shared /in/ meta description names the SaaS-Mode limit on every
    # paginated URL. The intro body (hero, clusters, hub CTA) must not.
    assert "GoHighLevel for <em>Indian agencies</em>" not in page2
    assert "What actually works in India" not in page2
    assert "utm_content=hub_cta" not in page2
    assert "Razorpay does not bill SaaS Mode" in page2  # meta description

    for label, html in (("es", es), ("ar", ar)):
        assert "does not bill SaaS Mode" not in html, label
        assert "utm_content=hub_cta" not in html, label
        assert "Indian agencies" not in html, label

    assert "40 guides in India" in page2
    assert "<h1" in page2


def test_intro_helper_is_what_the_page_renders(tmp_path, monkeypatch):
    """A helper that is correct and never called is not a fix. The rendered
    page must contain the helper's own string, not a rewritten cousin."""
    import build

    html = _render(tmp_path, monkeypatch, IN_CONFIG, 20)
    intro = build.india_hub_intro()
    assert "does not bill SaaS Mode" in intro
    assert intro.strip() in html
