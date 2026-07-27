#!/usr/bin/env python3
"""Tests for the internal-link logic in build.py (anchor cap, multi-word anchors, hub link).

Run: python3 scripts/test_build_links.py
Exits 0 if all pass, 1 otherwise. Imports build.py (import-safe: main() is __main__-guarded).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # globalhighlevel-site/
import build

FAILED = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        FAILED.append(name)


def test_anchor_cap():
    build._ANCHOR_URL_COUNTS.clear()
    cap = build.ANCHOR_URL_CAP
    seq = [build._anchor_under_cap("Our Guides", "/c/") for _ in range(cap + 1)]
    check(f"first {cap} under cap True, then False", seq == [True] * cap + [False])
    # case + whitespace normalized -> shares the same counter (already at cap)
    check("normalized variant shares counter (over cap)", build._anchor_under_cap("our   guides", "/c/") is False)
    # same anchor, different URL is an independent counter
    check("same anchor different url is independent", build._anchor_under_cap("our guides", "/other/") is True)


def test_build_link_index_multiword_only():
    build._ANCHOR_URL_COUNTS.clear()
    idx = build._build_link_index([{"slug": "s", "title": "GoHighLevel Pricing Guide", "html_content": "x"}])
    check("index produced one entry", len(idx) == 1)
    phrases = idx[0][3]
    check("every anchor phrase is multi-word (no single tokens)", all(" " in p for p in phrases))
    check("no bare-brand single-word anchor 'gohighlevel'", "gohighlevel" not in phrases)
    check("no generic single-word anchor 'pricing'", "pricing" not in phrases)
    check("a real bigram from the title is present", "gohighlevel pricing" in phrases)


def test_hub_link_block():
    build._ANCHOR_URL_COUNTS.clear()
    out = build._hub_link_block("Sales", "sales", "post-1")
    check("hub link emits a <p class=hub-link>", 'class="hub-link"' in out)
    check("hub link points at the category hub", 'href="/category/sales/"' in out)
    # deterministic per slug
    build._ANCHOR_URL_COUNTS.clear()
    a = build._hub_link_block("Sales", "sales", "post-1")
    build._ANCHOR_URL_COUNTS.clear()
    b = build._hub_link_block("Sales", "sales", "post-1")
    check("same slug -> same anchor (deterministic)", a == b)
    # all variants over cap -> returns '' (no uniform repeated/empty-anchor cliff)
    build._ANCHOR_URL_COUNTS.clear()
    url = "/category/sales/"
    for v in ["more sales tutorials for gohighlevel", "our sales guides",
              "the full sales guide library", "all sales how-tos"]:
        build._ANCHOR_URL_COUNTS[(" ".join(v.lower().split()), url)] = build.ANCHOR_URL_CAP
    check("all variants capped -> returns '' (no fresh cliff)", build._hub_link_block("Sales", "sales", "p2") == "")


def test_date_modified():
    dm = build._date_modified
    check("prefers updatedAt", dm({"updatedAt": "2026-07-22T00:00:00", "publishedAt": "2026-04-10T06:00:00"}) == "2026-07-22T00:00:00")
    check("falls back to publishedAt when missing", dm({"publishedAt": "2026-04-10T06:00:00"}) == "2026-04-10T06:00:00")
    check("empty updatedAt falls back", dm({"updatedAt": "", "publishedAt": "2026-04-10T06:00:00"}) == "2026-04-10T06:00:00")
    check("uploadedAt last resort", dm({"uploadedAt": "2026-04-01T00:00:00"}) == "2026-04-01T00:00:00")


def _silo(topic, lang, n, pub_start=1):
    """n synthetic circle-member posts in one lang+topic silo."""
    return [{"slug": f"{topic}-{lang}-{i}", "title": f"{topic.title()} Guide {i}",
             "language": lang, "topic": topic,
             "publishedAt": f"2026-01-{pub_start + i:02d}T00:00:00"} for i in range(n)]


def test_circle_neighbors():
    posts = _silo("crm", "en", 4)
    # walk the successor chain: must visit every member exactly once and wrap (closes)
    seen, cur = [], posts[0]
    for _ in range(4):
        _, nxt = build.circle_neighbors(cur, posts)
        seen.append(nxt["slug"])
        cur = nxt
    check("circle closes: successor chain is one full cycle", sorted(seen) == sorted(p["slug"] for p in posts))
    check("chain returns to start", cur["slug"] == posts[0]["slug"])
    prev, nxt = build.circle_neighbors(posts[0], posts)
    check("prev of first wraps to last", prev["slug"] == posts[-1]["slug"])
    check("deterministic", build.circle_neighbors(posts[2], posts) == build.circle_neighbors(posts[2], posts))


def test_circle_edge_cases():
    one = _silo("crm", "en", 1)
    check("singleton silo -> no circle", build.circle_neighbors(one[0], one) == (None, None))
    two = _silo("crm", "en", 2)
    p, n = build.circle_neighbors(two[0], two)
    check("2-post silo: prev is next (same neighbor)", p is n and n["slug"] == two[1]["slug"])
    # sink + pillar are never circle members
    posts = _silo("crm", "en", 3)
    posts[1]["mvp_minimal_links"] = True
    check("sink post excluded from membership", build.circle_neighbors(posts[1], posts) == (None, None))
    _, nxt = build.circle_neighbors(posts[0], posts)
    check("circle skips over the sink", nxt["slug"] == posts[2]["slug"])
    posts2 = _silo("agency", "en", 3)
    posts2[0]["isPillar"] = True
    check("pillar excluded from membership", build.circle_neighbors(posts2[0], posts2) == (None, None))


def test_circle_never_crosses_silo():
    posts = _silo("crm", "en", 2) + _silo("payments", "en", 2) + _silo("crm", "es", 2)
    ok = True
    for p in posts:
        prev, nxt = build.circle_neighbors(p, posts)
        ok = ok and all(x is None or (x["topic"] == p["topic"] and x["language"] == p["language"])
                        for x in (prev, nxt))
    check("every neighbor stays same lang+topic across mixed silos", ok)


def test_related_rotation_distributes():
    posts = _silo("crm", "en", 10)
    # with same[:n] every post picked the same 3; rotation must yield >3 distinct targets
    targets = set()
    for p in posts:
        targets |= {r["slug"] for r in build.get_related(p, posts)}
    check("related-card targets spread beyond the first 3 posts", len(targets) > 3)


def test_inject_internal_links_same_silo_only():
    build._ANCHOR_URL_COUNTS.clear()
    html = ('<p>This is a long paragraph about payment providers setup that easily '
            'clears the eighty character minimum for link injection to happen here.</p>')
    me = {"slug": "me", "title": "Me", "language": "en", "topic": "crm"}
    other_silo = {"slug": "other", "title": "Payment Providers Setup Guide",
                  "language": "en", "topic": "payments", "html_content": "x"}
    out = build.inject_internal_links(html, me, [me, other_silo])
    check("cross-silo candidate never linked", "/blog/other/" not in out)
    same_silo = dict(other_silo, topic="crm", slug="same")
    build._ANCHOR_URL_COUNTS.clear()
    out2 = build.inject_internal_links(html, me, [me, same_silo])
    check("same-silo candidate IS linked", "/blog/same/" in out2)


def test_is_series_post():
    check("is_series_hub flag -> series", build.is_series_post({"is_series_hub": True}) is True)
    check("/es/para/ url_path -> series", build.is_series_post({"url_path": "/es/para/agencias/"}) is True)
    check("/for/ url_path -> series", build.is_series_post({"url_path": "/for/coaches/"}) is True)
    check("plain post -> not series", build.is_series_post({"slug": "x"}) is False)
    check("/blog/ url_path -> not series", build.is_series_post({"url_path": "/blog/x/"}) is False)


def test_circle_excludes_series():
    posts = _silo("crm", "en", 3)
    posts[1]["url_path"] = "/for/agencies/"  # series/authority page
    check("series post excluded from membership", build.circle_neighbors(posts[1], posts) == (None, None))
    _, nxt = build.circle_neighbors(posts[0], posts)
    check("circle skips over the series post", nxt["slug"] == posts[2]["slug"])
    posts2 = _silo("agency", "en", 3)
    posts2[1]["is_series_hub"] = True
    check("is_series_hub post excluded from membership",
          build.circle_neighbors(posts2[1], posts2) == (None, None))


def test_get_related_edges():
    # silo of exactly n+1: rotation path not taken, every sibling returned
    three = _silo("crm", "en", 3)
    rel = build.get_related(three[0], three)
    check("small silo (<=n siblings): all siblings returned",
          {r["slug"] for r in rel} == {three[1]["slug"], three[2]["slug"]})
    # deterministic per slug
    ten = _silo("crm", "en", 10)
    check("get_related deterministic per slug",
          build.get_related(ten[4], ten) == build.get_related(ten[4], ten))
    # rotation never leaves the silo (lang + topic)
    mixed = _silo("crm", "en", 6) + _silo("crm", "es", 4) + _silo("payments", "en", 4)
    ok = all(r["language"] == "en" and r["topic"] == "crm"
             for p in mixed[:6] for r in build.get_related(p, mixed))
    check("rotated related cards stay same lang+topic", ok)


def test_enforce_anchor_caps_edges():
    # query/fragment strip: variants share the cap counter with the clean URL
    build._ANCHOR_URL_COUNTS.clear()
    plain = '<p><a href="/blog/t/">same anchor here</a></p>'
    for _ in range(build.ANCHOR_URL_CAP):
        build.enforce_anchor_caps(plain)
    q = build.enforce_anchor_caps('<p><a href="/blog/t/?utm=1">same anchor here</a></p>')
    f = build.enforce_anchor_caps('<p><a href="/blog/t/#frag">same anchor here</a></p>')
    check("?query variant shares counter (unwrapped over cap)", q == "<p>same anchor here</p>")
    check("#fragment variant shares counter (unwrapped over cap)", f == "<p>same anchor here</p>")
    # empty visible anchor (image-only link): kept, never counted
    build._ANCHOR_URL_COUNTS.clear()
    img = '<p><a href="/blog/e/"><img src="x.png"></a></p>'
    check("image-only (empty-text) anchor never unwrapped",
          all(build.enforce_anchor_caps(img) == img for _ in range(build.ANCHOR_URL_CAP + 2)))
    # anchor tag without href: untouched
    build._ANCHOR_URL_COUNTS.clear()
    noh = '<p><a name="jump">in-page target</a></p>'
    check("href-less <a> untouched", build.enforce_anchor_caps(noh) == noh)


def test_enforce_anchor_caps_absolute():
    # absolute own-site hrefs count as internal — same cap as root-relative
    build._ANCHOR_URL_COUNTS.clear()
    absl = f'<p><a href="{build.SITE_URL}/blog/t/">same anchor here</a></p>'
    outs = [build.enforce_anchor_caps(absl) for _ in range(build.ANCHOR_URL_CAP + 1)]
    kept = sum("/blog/t/" in o for o in outs)
    check(f"absolute own-site anchor kept exactly CAP({build.ANCHOR_URL_CAP})x",
          kept == build.ANCHOR_URL_CAP)
    check("absolute own-site anchor over cap unwrapped to plain text",
          outs[-1] == "<p>same anchor here</p>")
    # mixed absolute + relative forms share ONE ledger counter
    build._ANCHOR_URL_COUNTS.clear()
    rel = '<p><a href="/blog/t/">same anchor here</a></p>'
    mixed = [build.enforce_anchor_caps(absl),
             build.enforce_anchor_caps(absl),
             build.enforce_anchor_caps(rel),
             build.enforce_anchor_caps(rel)]
    check("mixed forms: 2 absolute + 1 relative kept (shared counter)",
          all("/blog/t/" in o for o in mixed[:3]))
    check("mixed forms: 4th occurrence unwrapped (shared counter over cap)",
          mixed[3] == "<p>same anchor here</p>")


def test_cta_money_page():
    check("MONEY_PAGE_URL is the trial post", build.MONEY_PAGE_URL == "/blog/gohighlevel-free-trial-30-days-extended/")


def test_enforce_anchor_caps():
    link = '<a href="/blog/target/">gohighlevel starter plan</a>'
    build._ANCHOR_URL_COUNTS.clear()
    outs = [build.enforce_anchor_caps(f"<p>{link}</p>") for _ in range(build.ANCHOR_URL_CAP + 2)]
    kept = sum('href="/blog/target/"' in o for o in outs)
    check(f"baked anchor kept exactly CAP({build.ANCHOR_URL_CAP})x sitewide", kept == build.ANCHOR_URL_CAP)
    check("over-cap keeps visible text, drops link",
          outs[-1] == "<p>gohighlevel starter plan</p>")
    build._ANCHOR_URL_COUNTS.clear()
    nf = '<p><a href="/blog/x/" rel="nofollow">try it free</a></p>'
    check("nofollow CTA never unwrapped",
          all(build.enforce_anchor_caps(nf) == nf for _ in range(5)))
    build._ANCHOR_URL_COUNTS.clear()
    es = '<p><a href="/es/trial/">empieza tu prueba gratis aquí →</a></p>'
    es_out = build.enforce_anchor_caps(es)
    check("attribution/conversion path never unwrapped (Spanish funnel intact)",
          all('href="/es/trial/"' in build.enforce_anchor_caps(es) for _ in range(5)))
    check("attribution CTA gains rel=nofollow (no followed 160x-anchor footprint)",
          'rel="nofollow"' in es_out)
    build._ANCHOR_URL_COUNTS.clear()
    es_rel = '<p><a href="/es/trial/" rel="noopener">cta</a></p>'
    check("attribution CTA with existing rel gets nofollow appended",
          'rel="noopener nofollow"' in build.enforce_anchor_caps(es_rel))
    build._ANCHOR_URL_COUNTS.clear()
    ext = '<p><a href="https://example.com/">external</a></p>'
    check("external link untouched", build.enforce_anchor_caps(ext) == ext)


def test_nofollow_affiliate_links():
    f = build.nofollow_affiliate_links
    bare = '<p><a href="https://www.gohighlevel.com/x?fp_ref=amplifi-technologies12">go</a></p>'
    check("bare affiliate anchor gains nofollow sponsored", 'rel="nofollow sponsored"' in f(bare))
    has = '<p><a href="https://x.com/?fp_ref=a" rel="noopener">go</a></p>'
    check("existing rel gets nofollow appended", 'rel="noopener nofollow sponsored"' in f(has))
    ok = '<p><a href="https://x.com/?fp_ref=a" rel="nofollow noopener">go</a></p>'
    check("already-nofollow untouched", f(ok) == ok)
    plain = '<p><a href="/blog/x/">internal</a></p>'
    check("non-affiliate anchor untouched", f(plain) == plain)


def test_post_lang_markers():
    f = build.post_lang
    check("explicit language field wins over slug markers",
          f({"language": "en", "slug": "gohighlevel-arabic-guide"}) == "en")
    check("slug marker 'arabic' infers ar", f({"slug": "gohighlevel-crm-arabic-guide"}) == "ar")
    check("slug marker 'mena' infers ar", f({"slug": "gohighlevel-mena-agencies"}) == "ar")
    check("slug marker 'india' infers en-IN", f({"slug": "gohighlevel-india-payments"}) == "en-IN")
    check("slug marker 'espanol' infers es", f({"slug": "gohighlevel-espanol-tutorial"}) == "es")
    check("unmarked slug falls back to en", f({"slug": "gohighlevel-pricing-guide"}) == "en")
    # documents current substring semantics: no live slug may contain a marker
    # as an accidental substring ('mena' in 'phenomena') without tripping this
    check("no live post slug accidentally matches a marker for the wrong language",
          all(f(post) == (post.get("language") or "en")
              for post in build.load_posts() if post.get("language")))


def test_localized_landing_configs():
    import json
    cats = json.loads((Path(__file__).resolve().parent.parent / "categories.json").read_text())
    langs = {l["prefix"]: l for l in cats["languages"] if l.get("prefix")}
    required = ("code", "prefix", "dir", "title", "desc", "h1", "subh", "cta",
                "value_props", "faq_h", "faq", "footer_cta")
    for cfg in build.LOCALIZED_LANDING_LANGS:
        missing = [k for k in required if k not in cfg]
        check(f"landing config {cfg.get('code')} has all required keys", not missing)
        lang = langs.get(cfg["prefix"])
        check(f"landing prefix {cfg['prefix']} exists in categories.json languages", lang is not None)
        if lang:
            check(f"landing dir matches categories.json for {cfg['prefix']}",
                  cfg["dir"] == lang.get("dir", "ltr"))


def test_rtl_rendering():
    out = build.base_html(title="t", description="d", canonical=f"{build.SITE_URL}/x/",
                          body="<p>x</p>", lang="ar", text_dir="rtl")
    check("ar page renders <html lang=\"ar\" dir=\"rtl\">", '<html lang="ar" dir="rtl">' in out)
    out_es = build.base_html(title="t", description="d", canonical=f"{build.SITE_URL}/x/",
                             body="<p>x</p>", lang="es", text_dir="ltr")
    check("es page has no dir=rtl attribute", 'dir="rtl"' not in out_es)


def test_attribution_prefixes_protected():
    for prefix in build.ATTRIBUTION_PREFIXES:
        path = prefix + "/"
        check(f"{path} is an attribution path", build.is_attribution_path(path))
        build._ANCHOR_URL_COUNTS.clear()
        html = "".join(f'<p><a href="{path}">start trial</a></p>' for _ in range(build.ANCHOR_URL_CAP + 2))
        out = build.enforce_anchor_caps(html)
        check(f"{path} anchors never unwrapped by anchor cap", out.count(f'href="{path}"') == build.ANCHOR_URL_CAP + 2)


def test_correct_trial_claims():
    f = build.correct_trial_claims
    en = "<p>Try it — No credit card required. Cancel anytime.</p>"
    check("en 'No credit card required' rewritten to card-verification truth",
          "~$1 card verification" in f(en) and "No credit card required" not in f(en))
    en2 = "<p>No credit card. No commitment.</p>"
    check("en staccato FAQ answer rewritten", f(en2) == "<p>Just a ~$1 card verification. No commitment.</p>")
    es = "<p>Empieza gratis — Sin tarjeta de crédito requerida.</p>"
    check("es claim rewritten", "verificación de tarjeta" in f(es) and "Sin tarjeta" not in f(es))
    ar = "<p>جرّب مجاناً — بدون بطاقة ائتمان.</p>"
    check("ar claim rewritten", "تحقق رمزي" in f(ar) and "بدون بطاقة" not in f(ar))
    ar_faq = "<p>لا. GoHighLevel توفر 30 يوماً مجاناً بدون بطاقة ائتمان.</p>"
    out = f(ar_faq)
    check("ar FAQ opener flipped to truthful yes", out.startswith("<p>نعم،") and "بدون بطاقة" not in out)
    clean = "<p>The card on file is charged $97/month after the trial.</p>"
    check("truthful copy untouched", f(clean) == clean)
    check("pass is idempotent", f(f(en)) == f(en))


def test_logo_ltr_on_rtl_pages():
    out = build.base_html(title="t", description="d", canonical=f"{build.SITE_URL}/x/",
                          body="<p>x</p>", lang="ar", text_dir="rtl")
    check("logo anchor pins dir=ltr (RTL must not reorder brand spans)",
          'class="logo" dir="ltr"' in out)


def test_localize_trial_hrefs():
    f = build.localize_trial_hrefs
    ar = '<p><a href="https://globalhighlevel.com/trial/">جرب</a> <a href="/trial/">x</a></p>'
    out = f(ar, "ar")
    check("ar bodies: /trial CTAs rewritten to /ar/trial/",
          out.count('href="/ar/trial/"') == 2 and "globalhighlevel.com/trial" not in out)
    check("es bodies untouched (pending policy call)", f(ar, "es") == ar)
    check("en bodies untouched", f(ar, "en") == ar)


def main():
    print("test_build_links.py")
    for t in (test_anchor_cap, test_build_link_index_multiword_only, test_hub_link_block,
              test_date_modified, test_circle_neighbors, test_circle_edge_cases,
              test_circle_never_crosses_silo, test_related_rotation_distributes,
              test_inject_internal_links_same_silo_only, test_is_series_post,
              test_circle_excludes_series, test_get_related_edges,
              test_enforce_anchor_caps_edges, test_enforce_anchor_caps_absolute,
              test_cta_money_page, test_enforce_anchor_caps,
              test_nofollow_affiliate_links, test_post_lang_markers,
              test_localized_landing_configs, test_rtl_rendering,
              test_attribution_prefixes_protected, test_correct_trial_claims,
              test_logo_ltr_on_rtl_pages, test_localize_trial_hrefs):
        t()
    print(f"\n{'PASS' if not FAILED else 'FAIL'} — {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
