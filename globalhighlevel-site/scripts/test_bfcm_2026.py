"""Black Friday / Cyber Monday 2026 phase helper.

The promo href, hero, and ended state come from one clock. cyber-week-2026
stays out of rendered HTML while CYBER_WEEK_LIVE is false (the URL 404'd on
2026-11-25). These tests render through apply_bfcm.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402

PT = ZoneInfo("America/Los_Angeles")

_SAMPLE = """
<img data-bfcm="hero" src="/images/hero-bfcm-50-off-landscape.jpg" alt="placeholder">
<a data-bfcm="new" data-bfcm-slot="hero" data-bfcm-lang="{lang}" href="https://www.gohighlevel.com/black-friday-2026?fp_ref=amplifi-technologies12&utm_source=globalhighlevel&utm_medium=content&utm_campaign=bfcm2026&utm_content=hero" target="_blank" rel="nofollow noopener">Get 50% off your first 3 months</a>
<span data-bfcm="callout" data-bfcm-lang="{lang}">50% off the first 3 months <a href="/blog/gohighlevel-black-friday-cyber-monday-2026/">offer</a></span>
""".strip()


def _at(y, mo, d, h, mi, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=PT)


def _render(now, lang="en", banner=True):
    return build.apply_bfcm(_SAMPLE.format(lang=lang), lang, now, banner=banner)


def _href(html):
    start = html.find('data-bfcm="new"')
    assert start >= 0
    chunk = html[start:html.find("</a>", start)]
    return chunk


def test_affiliate_constants_unchanged():
    assert "highlevel-bootcamp?" in build.AFFILIATE
    assert "fp_ref=amplifi-technologies12" in build.AFFILIATE
    assert "utm_campaign=" not in build.AFFILIATE
    assert "utm_content=" not in build.AFFILIATE
    assert "/highlevel-bootcamp-es?" in build.AFFILIATE_ES
    assert build.CYBER_WEEK_LIVE is False


def test_black_friday_week_uses_the_live_url_and_landscape_hero():
    for now in (_at(2026, 11, 25, 15, 0), _at(2026, 11, 29, 23, 59, 59)):
        assert build.bfcm_phase(now) == "bf"
        html = _render(now)
        href = _href(html)
        assert "black-friday-2026" in href
        assert "fp_ref=amplifi-technologies12" in href
        assert "utm_content=hero" in href
        assert "gohighlevel.com/cyber-week-2026" not in html
        assert "fp_ref=ghl-main" not in html
        assert 'src="/images/hero-bfcm-50-off-landscape.jpg"' in html
        assert "Ends Nov. 29." in html
        assert "50% off the first 3 months" in html


def test_cyber_week_keeps_black_friday_url_until_the_page_exists():
    for now in (_at(2026, 11, 30, 0, 0), _at(2026, 12, 6, 23, 59, 59)):
        assert build.bfcm_phase(now) == "cm"
        html = _render(now)
        href = _href(html)
        assert "black-friday-2026" in href
        assert "gohighlevel.com/cyber-week-2026" not in html
        assert 'src="/images/highlevel-cyber-week-2026-post-1.png"' in html
        assert "Offer ends Dec 6, 2026." in html
        assert "hero-bfcm-50-off-landscape.jpg" not in html


def test_after_dec_6_the_page_stops_selling_the_promo():
    now = _at(2026, 12, 7, 0, 0)
    assert build.bfcm_phase(now) == "ended"
    for lang, bootcamp in (("en", "highlevel-bootcamp?"), ("es", "highlevel-bootcamp-es?")):
        html = _render(now, lang=lang)
        assert "gohighlevel.com/cyber-week-2026" not in html
        assert "bfcm-ended" in html
        assert "data-bfcm=\"hero\"" not in html
        href = _href(html)
        assert bootcamp in href
        assert "fp_ref=amplifi-technologies12" in href
        assert "utm_content=hero" in href
        anchor = href.split(">", 1)[-1]
        assert "50%" not in anchor
        callout = html.split('data-bfcm="callout"', 1)[1]
        assert "50%" not in callout
        assert "30" in callout
        assert 'rel="nofollow"' in callout


def test_callout_keeps_the_live_offer_during_black_friday_week():
    html = _render(_at(2026, 11, 25, 15, 0), banner=False)
    callout = html.split('data-bfcm="callout"', 1)[1]
    assert "50% off the first 3 months" in callout
    assert "bfcm-ended" not in html
