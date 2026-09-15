#!/usr/bin/env python3
"""Gate: agency sub-account cousins 301 into the snapshots guide.

Manager GO 2026-09-15. Two firehose cousins consolidate into
`/blog/gohighlevel-sub-accounts-snapshots-agency-guide/`. Title and H1 on
that page stay locked. Cousin JSON is gone so Cloudflare's redirect-beats-
file rule cannot shadow a built page.

Run: python3 -m pytest scripts/test_agency_subaccounts_consolidate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402

SITE = Path(__file__).resolve().parents[1]
POSTS = SITE / "posts"
REDIRECTS = SITE / "_redirects"
PILLAR_SLUG = "gohighlevel-sub-accounts-snapshots-agency-guide"
PILLAR_PATH = f"/blog/{PILLAR_SLUG}/"
LOCKED_TITLE = "GoHighLevel Sub-Accounts: How Many You Really Get"
COUSINS = (
    "manage-sub-accounts-gohighlevel-advanced-filtering",
    "how-to-create-sub-accounts-gohighlevel-snapshots",
)
FOLDED = (
    'id="filters"',
    'id="bulk"',
    "stacked-filter",
    "Bulk Actions",
    "does not auto-update",
    'id="reconnect"',
    'id="make-snapshot"',
    'id="types"',
    "fp_ref=amplifi-technologies12",
)
DO_NOT_TOUCH = {
    "gohighlevel-white-label-setup-agency-guide": (
        "How to White-Label GoHighLevel: The Complete Agency Setup Guide"
    ),
    "gohighlevel-saas-mode-white-label-agency-guide": (
        "GoHighLevel White-Label & SaaS Mode: The Complete Agency Guide"
    ),
    "gohighlevel-free-trial-30-days-extended": (
        "GoHighLevel 30-Day Free Trial (2026): Get Extended Access"
    ),
    "gohighlevel-reselling-rebilling-agency-guide": (
        "GoHighLevel Reselling vs Rebilling: Which Plan Adds Markup"
    ),
}


def _pillar() -> dict:
    return json.loads((POSTS / f"{PILLAR_SLUG}.json").read_text(encoding="utf-8"))


def _redirect_rules() -> list[tuple[str, str, str]]:
    rows = []
    for line in REDIRECTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 3:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def test_pillar_title_and_h1_source_stay_locked():
    raw = (POSTS / f"{PILLAR_SLUG}.json").read_text(encoding="utf-8")
    assert f'"title": "{LOCKED_TITLE}"' in raw
    post = _pillar()
    assert post["title"] == LOCKED_TITLE
    assert post.get("isPillar") is False


def test_cousin_post_json_removed():
    for slug in COUSINS:
        assert not (POSTS / f"{slug}.json").exists(), slug


def test_redirects_are_permanent_into_pillar():
    rules = _redirect_rules()
    wanted = []
    for slug in COUSINS:
        wanted.append(f"/blog/{slug}")
        wanted.append(f"/blog/{slug}/")
    by_src = {src: (dest, code) for src, dest, code in rules}
    for src in wanted:
        assert src in by_src, src
        dest, code = by_src[src]
        assert code == "301", (src, code)
        assert dest == PILLAR_PATH, (src, dest)


def test_no_in_site_links_point_at_cousins():
    leftovers = []
    for path in sorted(POSTS.glob("*.json")):
        html = json.loads(path.read_text(encoding="utf-8")).get("html_content") or ""
        for slug in COUSINS:
            if slug in html:
                leftovers.append(f"{path.stem} -> {slug}")
    assert leftovers == []


def test_folded_subsections_and_affiliate_in_source():
    html = _pillar()["html_content"]
    missing = [n for n in FOLDED if n not in html]
    assert not missing, missing
    assert "no credit card" not in html.lower()
    assert "credit card required" not in html.lower()


def test_rendered_toc_includes_create_within_the_eight_item_cap():
    """create-cousin 301s land here; extract_toc hard-caps at 8 H2s."""
    toc = build.extract_toc(_pillar()["html_content"])
    ids = [anchor for anchor, _ in toc]
    assert "create" in ids
    assert "manage" in ids
    assert "faq" in ids
    assert len(toc) <= 8


def test_do_not_touch_neighbors_keep_their_titles():
    for slug, title in DO_NOT_TOUCH.items():
        post = json.loads((POSTS / f"{slug}.json").read_text(encoding="utf-8"))
        if title is None:
            assert post.get("title"), slug
        else:
            assert post["title"] == title, slug


def test_rendered_pillar_keeps_title_canonical_fp_ref_and_folds(tmp_path, monkeypatch):
    post = _pillar()
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build._ANCHOR_URL_COUNTS.clear()
    build.build_post_page(post, all_posts=[post])
    html = (tmp_path / build.post_output_rel(post) / "index.html").read_text(
        encoding="utf-8"
    )
    assert f"<title>{LOCKED_TITLE}</title>" in html
    assert f'<h1 class="post-title fade-2">{LOCKED_TITLE}</h1>' in html
    canonical = f'{build.SITE_URL}{PILLAR_PATH}'
    assert f'<link rel="canonical" href="{canonical}">' in html
    assert "fp_ref=amplifi-technologies12" in html
    for needle in (
        'id="filters"',
        'id="bulk"',
        "stacked-filter",
        "does not auto-update",
        'id="reconnect"',
        'id="make-snapshot"',
    ):
        assert needle in html, needle
    assert 'content="noindex' not in html


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
