#!/usr/bin/env python3
"""Gate: money-page title/H1/og:title stay on the locked head-term rewrite.

William GO via COS 2026-09-15. Bing W37 cluster is
`gohighlevel 30 day free trial*` (4 clicks / 1,267 impressions / 0.32% CTR /
pos ~5). The old title led with clever "Not 14" instead of the head term.

The post `title` drives <title>, <h1 class="post-title">, og:title, and
JSON-LD headline. There is no twitter:title meta — do not invent one.

Run: python3 -m pytest scripts/test_trial_title.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402

LOCKED = "GoHighLevel 30-Day Free Trial (2026): Get Extended Access"
POST = (
    Path(__file__).resolve().parents[1]
    / "posts"
    / "gohighlevel-free-trial-30-days-extended.json"
)


def test_source_title_is_byte_faithful_locked_string():
    raw = POST.read_text(encoding="utf-8")
    assert f'"title": "{LOCKED}"' in raw
    assert "Get 30 Days Free, Not 14" not in raw.split("html_content", 1)[0]


def test_locked_title_fits_serp_budget_without_brand():
    assert len(LOCKED) <= build.TITLE_MAX
    assert build.compose_title(LOCKED) == LOCKED


def test_rendered_title_h1_og_and_headline_match(tmp_path, monkeypatch):
    post = json.loads(POST.read_text(encoding="utf-8"))
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build._ANCHOR_URL_COUNTS.clear()
    build.build_post_page(post, all_posts=[post])
    html = (tmp_path / build.post_output_rel(post) / "index.html").read_text(
        encoding="utf-8"
    )
    assert f"<title>{LOCKED}</title>" in html
    assert f'<h1 class="post-title fade-2">{LOCKED}</h1>' in html
    assert f'<meta property="og:title" content="{LOCKED}">' in html
    assert f'"headline": "{LOCKED}"' in html
    assert "twitter:title" not in html
    assert "fp_ref=amplifi-technologies12" in html
    assert "Get 30 Days Free, Not 14 — GoHighLevel Trial 2026" not in html


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
