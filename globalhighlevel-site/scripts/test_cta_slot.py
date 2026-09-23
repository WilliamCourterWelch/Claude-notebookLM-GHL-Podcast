#!/usr/bin/env python3
"""Gate: affiliate CTAs stamp a short utm_content slot for GA4 ghl_click.

GA4 truncates Link URL around 100 characters, which hides utm_campaign on the
bootcamp URL. Slot lives on utm_content (and optionally cta_slot); the click
listener copies it into the event param cta_slot.

Page-level pins assert RENDERED HTML (nav, cta3, tldr, landings, listener).
Helper, AFFILIATE-constant, and corpus JSON checks are separate.

Run: python3 -m pytest scripts/test_cta_slot.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402


PRICING_SLOTS = ("tier_starter", "tier_unlimited", "tier_saaspro", "after_comparison")


def _hrefs(html: str, needle: str) -> list[str]:
    return re.findall(r'href="([^"]*' + re.escape(needle) + r'[^"]*)"', html)


def _fixture_post(**kwargs) -> dict:
    post = {
        "slug": "cta-slot-fixture",
        "title": "CTA Slot Fixture Guide",
        "description": "Fixture page used to pin affiliate CTA slot params.",
        "html_content": (
            "<p>Body copy for the fixture. "
            '<a href="https://www.gohighlevel.com/highlevel-bootcamp'
            "?fp_ref=amplifi-technologies12&amp;utm_source=globalhighlevel"
            '&amp;utm_medium=website&amp;utm_content=tier_starter">'
            "Starter</a> "
            '<a href="https://www.gohighlevel.com/highlevel-bootcamp'
            "?fp_ref=amplifi-technologies12&utm_source=globalhighlevel"
            '&utm_medium=website&utm_content=tier_unlimited">Unlimited</a> '
            '<a href="https://www.gohighlevel.com/highlevel-bootcamp'
            "?fp_ref=amplifi-technologies12&utm_source=globalhighlevel"
            '&utm_medium=website&utm_content=tier_saaspro">SaaS Pro</a> '
            '<a href="https://www.gohighlevel.com/highlevel-bootcamp'
            "?fp_ref=amplifi-technologies12&utm_source=globalhighlevel"
            '&utm_medium=website&utm_content=after_comparison">Compare</a>'
            "</p>"
        ),
        "language": "en",
        "topic": "gohighlevel-tutorials",
        "publishedAt": "2026-09-11T00:00:00",
        "tldr": ["The short answer for the fixture."],
        "tldr_cta": "Start the 30-day trial",
    }
    post.update(kwargs)
    return post


def _render_post(tmp_path, monkeypatch, post: dict) -> str:
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build._ANCHOR_URL_COUNTS.clear()
    build.build_post_page(post, all_posts=[post])
    out = tmp_path / build.post_output_rel(post) / "index.html"
    return out.read_text(encoding="utf-8")


def test_affiliate_constant_has_no_slot():
    assert "utm_content=" not in build.AFFILIATE
    assert "cta_slot=" not in build.AFFILIATE
    assert "utm_content=" not in build.AFFILIATE_ES
    assert "utm_content=" not in build.affiliate_for("en")
    assert "utm_content=" not in build.affiliate_for("es")
    assert build.affiliate_for("es") != build.affiliate_for("en")
    assert "highlevel-bootcamp-es?" in build.affiliate_for("es")


def test_affiliate_href_appends_content_and_keeps_campaign():
    url = build.affiliate_href("en", campaign="podcast-hero", content="trial_hero")
    assert url.startswith(build.AFFILIATE)
    assert "utm_campaign=podcast-hero" in url
    assert "utm_content=trial_hero" in url
    assert url.count("?") == 1
    assert "fp_ref=amplifi-technologies12" in url
    # Constant stays language-only after the call.
    assert "utm_content=" not in build.AFFILIATE
    es = build.affiliate_href("es", content="nav")
    assert "highlevel-bootcamp-es?" in es
    assert "utm_content=nav" in es
    assert "utm_campaign=" not in es
    # No allowlist on content — pricing tier_* must pass through the helper too.
    tier = build.affiliate_href("en", content="tier_starter")
    assert "utm_content=tier_starter" in tier


def test_affiliate_href_optional_campaign_and_content_branches():
    """affiliate_href combinations: neither, campaign only, content only, both, falsy extras."""
    bare = build.affiliate_href("en")
    assert bare == build.affiliate_for("en")
    assert "utm_campaign=" not in bare
    assert "utm_content=" not in bare
    camp_only = build.affiliate_href("en", campaign="only-camp")
    assert camp_only == build.affiliate_for("en") + "&utm_campaign=only-camp"
    assert "utm_content=" not in camp_only
    content_only = build.affiliate_href("en", content="only-slot")
    assert content_only == build.affiliate_for("en") + "&utm_content=only-slot"
    assert "utm_campaign=" not in content_only
    # Falsy extras must not append empty params (if campaign: / if content:).
    empty = build.affiliate_href("es", campaign="", content="")
    assert empty == build.affiliate_for("es")
    assert "utm_campaign=" not in empty
    assert "utm_content=" not in empty
    both_es = build.affiliate_href("es", campaign="x", content="y")
    assert "highlevel-bootcamp-es?" in both_es
    assert "utm_campaign=x" in both_es
    assert "utm_content=y" in both_es
    # Non-es langs share the English bootcamp (affiliate_for else branch).
    for lang in ("ar", "en-IN", "in"):
        assert build.affiliate_for(lang) == build.AFFILIATE
        assert "utm_content=" not in build.affiliate_for(lang)


def test_affiliate_href_quotes_spaces_and_ampersands():
    spaced = build.affiliate_href("en", content="a b")
    assert "utm_content=a%20b" in spaced
    assert "utm_content=a b" not in spaced
    amped = build.affiliate_href("en", campaign="x&y")
    assert "utm_campaign=x%26y" in amped
    assert "utm_campaign=x&y" not in amped


def test_rendered_nav_desktop_and_mobile_carry_nav_slot():
    html = build.base_html(
        title="t",
        description="d",
        canonical=f"{build.SITE_URL}/x/",
        body="<p>x</p>",
        lang="en",
    )
    nav_ctas = re.findall(
        r'<a href="([^"]+)" class="nav-cta"', html
    )
    assert len(nav_ctas) == 2, f"expected desktop+mobile nav CTAs, got {nav_ctas!r}"
    for href in nav_ctas:
        assert "utm_content=nav" in href, href
        assert "fp_ref=amplifi-technologies12" in href
        assert "utm_campaign=" not in href
    es = build.base_html(
        title="t",
        description="d",
        canonical=f"{build.SITE_URL}/es/x/",
        body="<p>x</p>",
        lang="es",
    )
    es_nav = re.findall(r'<a href="([^"]+)" class="nav-cta"', es)
    assert es_nav and all("highlevel-bootcamp-es?" in h and "utm_content=nav" in h for h in es_nav)
    ar = build.base_html(
        title="t",
        description="d",
        canonical=f"{build.SITE_URL}/ar/x/",
        body="<p>x</p>",
        lang="ar",
    )
    ar_nav = re.findall(r'<a href="([^"]+)" class="nav-cta"', ar)
    assert len(ar_nav) == 2
    assert all("utm_content=nav" in h and "bootcamp-es" not in h for h in ar_nav)


def test_rendered_ghl_click_listener_copies_slot_from_url():
    html = build.base_html(
        title="t",
        description="d",
        canonical=f"{build.SITE_URL}/x/",
        body="<p>x</p>",
    )
    # Snippet is in the rendered page, not merely in build.py.
    assert 'gtag("event","ghl_click"' in html
    assert "link_url:h" in html
    assert "link_text:a.textContent.trim().slice(0,50)" in html
    assert "page_path:location.pathname" in html
    assert 'page_lang:document.documentElement.lang||"en"' in html
    assert 'qs.get("cta_slot")' in html
    assert 'qs.get("utm_content")' in html
    assert 'qs.get("cta_slot")||qs.get("utm_content")||"unstamped"' in html
    assert "cta_slot:String(slot).slice(0,64)" in html
    assert "try{" in html
    assert "catch(err){}" in html
    assert 'var slot=""' in html
    assert "new URL(h,location.href)" in html
    assert "u.searchParams" in html
    assert 'host==="gohighlevel.com"' in html
    assert 'host.slice(-16)===".gohighlevel.com"' in html
    # No allowlist — pricing tier_* and any new slot must pass through.
    assert "tier_starter" not in html.split("ghl_click")[1].split("cta_click")[0]
    assert '["nav"' not in html
    assert "ALLOWED" not in html
    # cta_click (non-affiliate) must not grow a cta_slot event param.
    cta_click_block = html.split('gtag("event","cta_click"')[1].split("});")[0]
    assert "cta_slot" not in cta_click_block


def test_rendered_post_cta3_and_tldr_slots(tmp_path, monkeypatch):
    html = _render_post(tmp_path, monkeypatch, _fixture_post())
    cta3 = [h for h in _hrefs(html, "utm_content=cta3") if "fp_ref=" in h]
    assert cta3, "cta3 slot missing from rendered post"
    assert all("utm_campaign=cta-slot-fixture" in h for h in cta3)
    assert all("utm_content=cta3" in h for h in cta3)
    tldr_hrefs = re.findall(r'<a class="btn-amber tldr-cta" href="([^"]+)"', html)
    assert tldr_hrefs, "tldr CTA missing from rendered post"
    assert all("utm_content=tldr" in h for h in tldr_hrefs)
    assert all("utm_campaign=cta-slot-fixture_tldr" in h for h in tldr_hrefs)
    # Nav still nav on the same page (slot-level split vs cta3).
    nav = re.findall(r'<a href="([^"]+)" class="nav-cta"', html)
    assert nav and all("utm_content=nav" in h for h in nav)
    assert not any("utm_content=cta3" in h for h in nav)


def test_rendered_pricing_tier_utm_content_preserved(tmp_path, monkeypatch):
    html = _render_post(tmp_path, monkeypatch, _fixture_post())
    for slot in PRICING_SLOTS:
        assert f"utm_content={slot}" in html, f"pricing slot {slot} stripped from rendered HTML"


def test_rendered_es_post_cta3_uses_spanish_bootcamp(tmp_path, monkeypatch):
    html = _render_post(
        tmp_path,
        monkeypatch,
        _fixture_post(language="es", slug="cta-slot-fixture-es", tldr=None, tldr_cta=None),
    )
    cta3 = [h for h in _hrefs(html, "utm_content=cta3") if "fp_ref=" in h]
    assert cta3, "es cta3 missing"
    assert all("highlevel-bootcamp-es?" in h for h in cta3)
    assert all("utm_content=cta3" in h for h in cta3)


def test_rendered_es_tldr_uses_spanish_bootcamp(tmp_path, monkeypatch):
    html = _render_post(
        tmp_path,
        monkeypatch,
        _fixture_post(
            language="es",
            slug="cta-slot-fixture-es",
            tldr=["Resumen corto."],
            tldr_cta="Empieza la prueba",
        ),
    )
    tldr_hrefs = re.findall(r'<a class="btn-amber tldr-cta" href="([^"]+)"', html)
    assert tldr_hrefs, "es tldr CTA missing"
    assert all("highlevel-bootcamp-es?" in h for h in tldr_hrefs)
    assert all("utm_content=tldr" in h for h in tldr_hrefs)
    assert all("utm_campaign=cta-slot-fixture-es_tldr" in h for h in tldr_hrefs)


def test_rendered_tldr_omitted_when_cta_label_missing(tmp_path, monkeypatch):
    html = _render_post(
        tmp_path,
        monkeypatch,
        _fixture_post(tldr=["The short answer for the fixture."], tldr_cta=None),
    )
    assert 'class="btn-amber tldr-cta"' not in html
    assert "utm_content=tldr" not in html
    assert "utm_content=cta3" in html


def test_rendered_localized_landing_keeps_campaign_and_slots(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    es = next(c for c in build.LOCALIZED_LANDING_LANGS if c["code"] == "es")
    build._build_localized_affiliate_landing(es, "trial", "podcast")
    html = (tmp_path / "es" / "trial" / "index.html").read_text(encoding="utf-8")
    hero = re.findall(r'<a class="trial-cta-primary" href="([^"]+)"', html)
    assert len(hero) == 2, hero
    assert "utm_campaign=es-podcast" in hero[0]
    assert "utm_content=trial_hero" in hero[0]
    assert "utm_campaign=es-podcast" in hero[1]
    assert "utm_content=trial_bottom" in hero[1]
    assert all("highlevel-bootcamp-es?" in h for h in hero)
    nav = re.findall(r'<a href="([^"]+)" class="nav-cta"', html)
    assert nav and all("utm_content=nav" in h for h in nav)


def test_rendered_in_landing_uses_en_bootcamp_and_slots(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    inn = next(c for c in build.LOCALIZED_LANDING_LANGS if c["code"] == "in")
    build._build_localized_affiliate_landing(inn, "trial", "podcast")
    html = (tmp_path / "in" / "trial" / "index.html").read_text(encoding="utf-8")
    hero = re.findall(r'<a class="trial-cta-primary" href="([^"]+)"', html)
    assert len(hero) == 2, hero
    assert "utm_campaign=in-podcast" in hero[0]
    assert "utm_content=trial_hero" in hero[0]
    assert "utm_campaign=in-podcast" in hero[1]
    assert "utm_content=trial_bottom" in hero[1]
    assert all("highlevel-bootcamp?" in h and "bootcamp-es" not in h for h in hero)


def test_rendered_en_trial_keeps_podcast_campaign_names(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build._build_affiliate_landing("trial", "podcast")
    html = (tmp_path / "trial" / "index.html").read_text(encoding="utf-8")
    skip = re.search(
        r'href="([^"]+)"[^>]*>Go straight to GoHighLevel', html
    )
    hero = re.search(
        r'<a href="([^"]+)" class="btn-amber"[^>]*>Start Your 30-Day Free Trial', html
    )
    bottom = re.search(
        r'<div class="cta-end"[^>]*>[\s\S]*?<a href="([^"]+)" class="btn-amber"', html
    )
    assert skip, "trial skip CTA missing"
    assert hero, "trial hero CTA missing"
    assert bottom, "trial bottom CTA missing"
    assert "utm_campaign=podcast-skip" in skip.group(1)
    assert "utm_content=trial_skip" in skip.group(1)
    assert "utm_campaign=podcast-hero" in hero.group(1)
    assert "utm_content=trial_hero" in hero.group(1)
    assert "utm_campaign=podcast-bottom" in bottom.group(1)
    assert "utm_content=trial_bottom" in bottom.group(1)
    # Campaign names were not collapsed into the slot.
    assert "utm_campaign=trial_hero" not in html


def test_localize_trial_hrefs_appends_blog_trial_slot():
    out = build.localize_trial_hrefs('<a href="/trial/">x</a>', "en")
    href = out.split('href="')[1].split('"')[0]
    assert "utm_campaign=blog-trial-en" in href
    assert "utm_content=blog_trial" in href
    es = build.localize_trial_hrefs('<a href="/trial/">x</a>', "es")
    es_href = es.split('href="')[1].split('"')[0]
    assert "utm_campaign=blog-trial-es" in es_href
    assert "utm_content=blog_trial" in es_href
    assert "highlevel-bootcamp-es?" in es_href


def test_localize_trial_hrefs_en_in_prefixed_and_typo_keep_blog_trial_slot():
    inn = build.localize_trial_hrefs('<a href="/trial/">x</a>', "en-IN")
    in_href = inn.split('href="')[1].split('"')[0]
    assert "utm_campaign=blog-trial-in" in in_href
    assert "utm_content=blog_trial" in in_href
    assert "bootcamp-es" not in in_href
    es_pref = build.localize_trial_hrefs('<a href="/es/trial/">x</a>', "en")
    es_href = es_pref.split('href="')[1].split('"')[0]
    assert "utm_campaign=blog-trial-es" in es_href
    assert "utm_content=blog_trial" in es_href
    assert "highlevel-bootcamp-es?" in es_href
    in_pref = build.localize_trial_hrefs('<a href="/in/trial/">x</a>', "es")
    in_pref_href = in_pref.split('href="')[1].split('"')[0]
    assert "utm_campaign=blog-trial-in" in in_pref_href
    assert "utm_content=blog_trial" in in_pref_href
    typo = build.localize_trial_hrefs(
        '<a href="https://goingHighLevel.com/free-trial">x</a>', "en"
    )
    typo_href = typo.split('href="')[1].split('"')[0]
    assert "utm_content=blog_trial" in typo_href
    assert "highlevel-bootcamp-es?" in typo_href
    assert "utm_campaign=blog-trial-es" in typo_href


def test_localize_trial_hrefs_ar_does_not_stamp_blog_trial():
    out = build.localize_trial_hrefs('<a href="/trial/">x</a>', "ar")
    href = out.split('href="')[1].split('"')[0]
    assert href == "/ar/trial/"
    assert "utm_content=" not in out
    assert "utm_campaign=" not in out


def _bootcamp_hrefs(html: str) -> list[str]:
    return re.findall(r'href="([^"]*highlevel-bootcamp[^"]*)"', html, re.I)


def _slot_of(href: str) -> str:
    raw = href.replace("&amp;", "&").replace("&#38;", "&")
    query = raw.split("#", 1)[0].split("?", 1)[-1]
    for part in query.split("&"):
        key, _, value = part.partition("=")
        if key in ("utm_content", "cta_slot") and value:
            return value
    return ""


def test_stamp_appends_in_article_without_copying_campaign():
    src = (
        '<a href="https://www.gohighlevel.com/highlevel-bootcamp'
        '?fp_ref=amplifi-technologies12&utm_source=blog&utm_medium=article'
        '&utm_campaign=how-to-install-gohighlevel-desktop-app--complete-setup-guide">'
        'Install</a>'
    )
    out = build.stamp_missing_bootcamp_slots(src)
    assert "utm_content=in_article" in out
    assert "utm_campaign=how-to-install-gohighlevel-desktop-app--complete-setup-guide&utm_content=in_article" in out
    assert "utm_content=how-to-install" not in out
    assert out.count("utm_content=") == 1
    assert build.stamp_missing_bootcamp_slots(out) == out


def test_stamp_leaves_existing_slots_and_non_bootcamp_hrefs():
    kept = (
        '<a href="https://www.gohighlevel.com/highlevel-bootcamp'
        '?fp_ref=amplifi-technologies12&amp;utm_content=tier_starter">S</a>'
        '<a href="https://www.gohighlevel.com/highlevel-bootcamp'
        '?fp_ref=amplifi-technologies12&utm_content=extractable-steps">T</a>'
        '<a href="https://www.gohighlevel.com/highlevel-bootcamp'
        '?fp_ref=amplifi-technologies12&cta_slot=nav">N</a>'
        '<a href="https://www.gohighlevel.com/ai'
        '?fp_ref=amplifi-technologies12&utm_campaign=summer_ai">AI</a>'
        '<a href="https://help.gohighlevel.com/highlevel-bootcamp">docs</a>'
    )
    out = build.stamp_missing_bootcamp_slots(kept)
    assert out == kept
    bare = (
        '<a href="https://www.gohighlevel.com/highlevel-bootcamp-es'
        '?fp_ref=amplifi-technologies12">ES</a>'
    )
    es = build.stamp_missing_bootcamp_slots(bare)
    assert "highlevel-bootcamp-es?" in es
    assert "utm_content=in_article" in es
    assert "utm_campaign=" not in es


def test_rendered_gap_pages_stamp_every_bootcamp_href(tmp_path, monkeypatch):
    """Desktop install guide, money page, white-label guide, ES precios guía.

    Titles/H1 stay on the stored strings. Body hrefs gain utm_content=in_article.
    Template slots (nav, cta3) and stored slots (tier_*, extractable-steps) stay.
    """
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    root = Path(__file__).resolve().parents[1] / "posts"
    pages = {
        "how-to-install-gohighlevel-desktop-app-complete-setup-guide.json": (
            "utm_campaign=how-to-install-gohighlevel-desktop-app--complete-setup-guide&utm_content=in_article"
        ),
        "gohighlevel-free-trial-30-days-extended.json": (
            "utm_campaign=gohighlevel-free-trial-30-days-extended&utm_content=in_article"
        ),
        "gohighlevel-white-label-setup-agency-guide.json": (
            "utm_campaign=white-label-spoke&utm_content=in_article"
        ),
        "gohighlevel-precios-planes-2026-guia-completa.json": (
            "utm_campaign=gohighlevel-precios-planes-2026-guia-completa&utm_content=in_article"
        ),
    }
    locked_trial = "GoHighLevel 30-Day Free Trial (2026): Get Extended Access"
    for name, needle in pages.items():
        post = json.loads((root / name).read_text(encoding="utf-8"))
        build._ANCHOR_URL_COUNTS.clear()
        build.build_post_page(post, all_posts=[post])
        html = (tmp_path / build.post_output_rel(post) / "index.html").read_text(encoding="utf-8")
        assert f'<h1 class="post-title fade-2">{post["title"]}</h1>' in html
        hrefs = _bootcamp_hrefs(html)
        assert hrefs, name
        for href in hrefs:
            slot = _slot_of(href)
            assert slot, href
            assert len(slot) <= 64, slot
            assert "utm_campaign" not in slot
            assert len(slot) < 40, slot
        assert needle in html, name
        assert "utm_content=nav" in html
        assert "utm_content=cta3" in html
        assert "utm_content=unstamped" not in html
    trial = json.loads((root / "gohighlevel-free-trial-30-days-extended.json").read_text(encoding="utf-8"))
    trial_html = (tmp_path / build.post_output_rel(trial) / "index.html").read_text(encoding="utf-8")
    assert f"<title>{locked_trial}</title>" in trial_html
    assert "utm_campaign=master-discount-guide&utm_content=in_article" in trial_html
    ai_hrefs = [
        h for h in re.findall(r'href="([^"]+)"', trial_html) if "gohighlevel.com/ai?" in h
    ]
    assert ai_hrefs and all("utm_content=" not in h and "cta_slot=" not in h for h in ai_hrefs)
    assert all("utm_campaign=summer_ai" in h for h in ai_hrefs)
    precios = json.loads((root / "gohighlevel-precios-planes-2026-guia-completa.json").read_text(encoding="utf-8"))
    precios_html = (tmp_path / build.post_output_rel(precios) / "index.html").read_text(encoding="utf-8")
    for slot in PRICING_SLOTS:
        assert f"utm_content={slot}" in precios_html
    agency = (root / "gohighlevel-sub-accounts-snapshots-agency-guide.json").read_text(encoding="utf-8")
    assert '"title": "GoHighLevel Sub-Accounts: How Many You Really Get"' in agency


def test_live_pricing_post_json_still_has_tier_slots():
    """Corpus pin: pricing guides' stored CTAs keep tier_* utm_content.
    Render pass must not be the only copy of those values."""
    root = Path(__file__).resolve().parents[1] / "posts"
    for name in (
        "gohighlevel-pricing-plans-2026-complete-guide.json",
        "gohighlevel-precios-planes-2026-guia-completa.json",
    ):
        raw = (root / name).read_text(encoding="utf-8")
        for slot in PRICING_SLOTS:
            assert f"utm_content={slot}" in raw, f"{name}: {slot}"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
