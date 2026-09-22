#!/usr/bin/env python3
"""Gate: Agent Studio guide title/H1/og:title stay on the locked rewrite.

William GO locked 2026-09-22. URL path stays
`/blog/how-to-build-ai-agents-in-gohighlevel-agent-studio-guide/`.
Bing ~pos 4.1, CTR 0.88%, 455 impressions (seo-ops 2026-W39).

The post `title` drives <title>, <h1 class="post-title">, og:title, and
JSON-LD headline. There is no twitter:title meta — do not invent one.

Run: python3 -m pytest scripts/test_agent_studio_title.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402

LOCKED = "GoHighLevel Agent Studio: Build AI Agents Step by Step"
OLD = "Build AI Agents in GoHighLevel: Complete Agent Studio Guide"
POST = (
    Path(__file__).resolve().parents[1]
    / "posts"
    / "how-to-build-ai-agents-in-gohighlevel-agent-studio-guide.json"
)


def test_source_title_is_byte_faithful_locked_string():
    raw = POST.read_text(encoding="utf-8")
    front, _, _body = raw.partition('"html_content"')
    assert f'"title": "{LOCKED}"' in front
    assert OLD not in front
    data = json.loads(raw)
    assert data["title"] == LOCKED
    assert data["slug"] == "how-to-build-ai-agents-in-gohighlevel-agent-studio-guide"


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
    head, sep, _rest = html.partition("<body")
    assert sep == "<body"
    assert f"<title>{LOCKED}</title>" in head
    assert f'<meta property="og:title" content="{LOCKED}">' in head
    assert f"<title>{LOCKED}</title>" in html
    assert f'<h1 class="post-title fade-2">{LOCKED}</h1>' in html
    assert f'<meta property="og:title" content="{LOCKED}">' in html
    assert f'"headline": "{LOCKED}"' in html
    assert "twitter:title" not in html
    assert "fp_ref=amplifi-technologies12" in html
    assert OLD not in html


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
