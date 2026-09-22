#!/usr/bin/env python3
"""Gate: Agent Studio cluster depth stays on the locked build guide.

Taste lifted 2026-09-22. Manager locked A, B, and C as drafted. This pins
the structure: naming section, setup anchor, cluster hrefs, spoke backlinks,
the two new 301s, the locked title, and no new outbound from the money page.

Run: python3 -m pytest scripts/test_agent_studio_cluster.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"
REDIRECTS = ROOT / "_redirects"
PILLAR = "how-to-build-ai-agents-in-gohighlevel-agent-studio-guide"
PILLAR_HREF = f"/blog/{PILLAR}/"
LOCKED = "GoHighLevel Agent Studio: Build AI Agents Step by Step"
MONEY = "gohighlevel-free-trial-30-days-extended"

# Same-silo spokes that must link back. The money page is intentionally absent.
SPOKE_BACKLINKS = [
    "clone-ai-agents-gohighlevel-scale-sub-accounts",
    "gohighlevel-ai-agent-pricing",
    "gohighlevel-ai-studio-pricing",
    "gohighlevel-voice-ai-pricing",
    "how-to-use-agent-studio-router-in-gohighlevel-smarter-ai-flows",
    "how-to-use-brand-voice-in-gohighlevel-agent-studio-guide",
    "how-to-use-variables-in-gohighlevel-agent-studio-save-time",
    "automate-client-support-ask-ai-agent-studio-gohighlevel",
    "how-to-setup-agent-logs-metrics-in-gohighlevel-monitor-ai-performance",
    "how-to-monitor-ai-agents-in-gohighlevel-agent-logs-guide",
    "gohighlevel-ai-employee-ai-receptionist-review",
    "gohighlevel-ai-employee-pricing",
    "how-to-create-pages-faster-gohighlevel-ai-studio",
]

CLUSTER_HREFS = [
    "/blog/clone-ai-agents-gohighlevel-scale-sub-accounts/",
    "/blog/how-to-use-agent-studio-router-in-gohighlevel-smarter-ai-flows/",
    "/blog/how-to-use-brand-voice-in-gohighlevel-agent-studio-guide/",
    "/blog/how-to-use-variables-in-gohighlevel-agent-studio-save-time/",
    "/blog/automate-client-support-ask-ai-agent-studio-gohighlevel/",
    "/blog/how-to-setup-agent-logs-metrics-in-gohighlevel-monitor-ai-performance/",
    "/blog/how-to-monitor-ai-agents-in-gohighlevel-agent-logs-guide/",
    "/blog/gohighlevel-voice-ai-pricing/",
    "/blog/gohighlevel-ai-employee-pricing/",
    "/blog/gohighlevel-ai-employee-ai-receptionist-review/",
    "/blog/gohighlevel-ai-studio-pricing/",
    "/blog/gohighlevel-ai-agent-pricing/",
    "/blog/how-to-create-pages-faster-gohighlevel-ai-studio/",
]

REDIRECT_SOURCES = [
    "/blog/how-to-setup-ai-agents-in-gohighlevel",
    "/blog/how-to-setup-ai-agents-in-gohighlevel/",
    "/blog/gohighlevel-ai-studio-vs-agent-studio",
    "/blog/gohighlevel-ai-studio-vs-agent-studio/",
    "/blog/how-to-build-ai-agents-gohighlevel-agent-studio-setup",
    "/blog/how-to-build-ai-agents-gohighlevel-agent-studio-setup/",
    "/blog/build-smarter-ai-agents-gohighlevel-agent-studio-setup",
    "/blog/build-smarter-ai-agents-gohighlevel-agent-studio-setup/",
]


def _post(slug: str) -> dict:
    return json.loads((POSTS / f"{slug}.json").read_text(encoding="utf-8"))


def test_pillar_keeps_locked_title_and_gains_sections():
    post = _post(PILLAR)
    assert post["title"] == LOCKED
    html = post["html_content"]
    assert 'id="ai-studio-is-not-agent-studio"' in html
    assert '<a id="setup"></a>\n<h2 id="section-2">' in html
    assert html.find('id="ai-studio-is-not-agent-studio"') < html.find('id="setup"')
    assert 'id="agent-studio-cluster"' in html
    assert "AI Studio Is Not Agent Studio" in html
    assert "not included in any subscription plan" in html
    for href in CLUSTER_HREFS:
        assert f'href="{href}"' in html
    assert "sin tarjeta" not in html.lower()
    # The pre-existing no-card sentence is rewritten at render. New copy must
    # not add another one. Count stays at the one legacy CTA line.
    assert html.lower().count("no credit card") == 1


def test_spokes_link_back_and_money_page_does_not():
    for slug in SPOKE_BACKLINKS:
        html = _post(slug)["html_content"]
        assert html.count(PILLAR_HREF) == 1, slug
    money = _post(MONEY)
    assert PILLAR not in money["html_content"]
    assert money["title"].startswith("GoHighLevel 30-Day Free Trial")


def test_setup_and_naming_404s_redirect_to_the_pillar():
    rules = {}
    for line in REDIRECTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        assert len(parts) >= 3, line
        rules[parts[0]] = parts[1]
    for src in REDIRECT_SOURCES:
        assert rules.get(src) == PILLAR_HREF, src
    assert (POSTS / "gohighlevel-ai-studio-vs-agent-studio.json").exists() is False
    assert (POSTS / "how-to-setup-ai-agents-in-gohighlevel.json").exists() is False


def test_rendered_pillar_keeps_sections_title_and_affiliate(tmp_path, monkeypatch):
    post = _post(PILLAR)
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build._ANCHOR_URL_COUNTS.clear()
    build.build_post_page(post, all_posts=[post])
    html = (tmp_path / build.post_output_rel(post) / "index.html").read_text(
        encoding="utf-8"
    )
    assert f"<title>{LOCKED}</title>" in html
    assert f'<h1 class="post-title fade-2">{LOCKED}</h1>' in html
    assert 'id="ai-studio-is-not-agent-studio"' in html
    assert 'id="setup"' in html
    assert 'id="agent-studio-cluster"' in html
    assert "fp_ref=amplifi-technologies12" in html
    for href in CLUSTER_HREFS:
        assert f'href="{href}"' in html


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
