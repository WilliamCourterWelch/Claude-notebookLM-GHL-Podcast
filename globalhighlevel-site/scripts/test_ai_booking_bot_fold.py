#!/usr/bin/env python3
"""Gate: AI Booking Bots episode is folded onto the Flow Builder page.

Decision (2026-09-24): expand
`master-conversation-ai-flow-builder-gohighlevel-complete-setup`.
No new URL. Agent Studio title/H1 stays locked. Free-trial and agency
titles are not in this diff.

Run: python3 -m pytest scripts/test_ai_booking_bot_fold.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"
HOST = "master-conversation-ai-flow-builder-gohighlevel-complete-setup"
HOST_HREF = f"/blog/{HOST}/#booking-bot"
LOCKED_AGENT = "GoHighLevel Agent Studio: Build AI Agents Step by Step"
HOST_TITLE = "GoHighLevel Conversation AI Flow Builder, No Code"
AI_TOPIC = "AI Receptionist & Lead Capture"
BOOT_STEPS = (
    "https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12"
    "&utm_source=globalhighlevel&utm_medium=blog"
    "&utm_campaign=conversation-ai-booking-bot&utm_content=ai-booking-bots"
)
BOOT_EPISODE = BOOT_STEPS.replace("utm_content=ai-booking-bots", "utm_content=ai-booking-episode")
STEPS = [
    "Open the workflow",
    "Set the trigger",
    "Add Appointment Booking Conversation AI Bot",
    "Save and use the three branches",
    "Test, save, and publish",
]
SPOKES = {
    "how-to-build-ai-agents-in-gohighlevel-agent-studio-guide":
        "Conversation AI booking bot workflow action",
    "build-ai-bots-without-code-gohighlevel-guided-form-setup":
        "Appointment Booking Conversation AI workflow action",
    "how-to-use-service-booking-triggers-gohighlevel-automate-appointments":
        "Conversation AI bot that books the appointment",
    "gohighlevel-ai-agents-automation-complete-guide":
        "Conversation AI booking bot steps",
}
CLUSTER = [
    "/blog/how-to-build-ai-agents-in-gohighlevel-agent-studio-guide/",
    "/blog/build-ai-bots-without-code-gohighlevel-guided-form-setup/",
    "/blog/how-to-use-service-booking-triggers-gohighlevel-automate-appointments/",
]


def _post(slug: str) -> dict:
    return json.loads((POSTS / f"{slug}.json").read_text(encoding="utf-8"))


def _render(post: dict, tmp_path, monkeypatch) -> str:
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build._ANCHOR_URL_COUNTS.clear()
    build.build_post_page(post, all_posts=[post])
    return (tmp_path / build.post_output_rel(post) / "index.html").read_text(encoding="utf-8")


def test_host_keeps_title_and_gains_episode(tmp_path, monkeypatch):
    post = _post(HOST)
    assert post["title"] == HOST_TITLE
    assert post["transistorEpisodeId"] == "1480182e"
    assert "3 suggested times" not in post["html_content"]
    html = post["html_content"]
    steps = html.find('id="extractable-steps"')
    section = html.find('id="section-1"')
    booking = html.find('id="booking-bot"')
    episode = html.find('id="ai-booking-bots-episode"')
    assert 0 < steps < section < booking < episode
    for label in STEPS:
        assert f"<strong>{label}</strong>" in html
    assert html.count(BOOT_STEPS) == 1
    assert html.count(BOOT_EPISODE) == 1
    assert "fp_ref=amplifi-technologies12" in html
    assert 'src="https://share.transistor.fm/e/968aa4ab"' in html
    assert 'href="https://share.transistor.fm/s/968aa4ab"' in html
    assert 'width="100%" height="315" src="https://www.youtube-nocookie.com/embed/y_eFDPg1wrE"' in html
    assert "AI Agents</strong>, then <strong>Conversation AI</strong>" in html
    assert "SMS, Facebook, Instagram, WhatsApp, and Live Chat" in html
    assert "email, or web chat" not in html
    assert 'href="https://www.youtube.com/watch?v=y_eFDPg1wrE"' in html
    assert "155000003467" in html
    assert "155000006515" in html
    assert "master-multi-calendar-appointment-booking-gohighlevel" not in html
    assert "fbq(" not in html
    assert "connect.facebook.net" not in html
    # New blocks do not add a no-card claim. The two legacy sentences stay.
    assert html.lower().count("no credit card") == 2

    rendered = _render(post, tmp_path, monkeypatch)
    assert f"<title>{HOST_TITLE}</title>" in rendered
    assert f'<h1 class="post-title fade-2">{HOST_TITLE}</h1>' in rendered
    assert 'src="https://share.transistor.fm/e/968aa4ab"' in rendered
    assert 'src="https://www.youtube-nocookie.com/embed/y_eFDPg1wrE"' in rendered
    assert BOOT_STEPS in rendered
    assert BOOT_EPISODE in rendered
    assert 'id="booking-bot"' in rendered
    assert 'id="extractable-steps"' in rendered
    for href in CLUSTER:
        assert f'href="{href}"' in rendered
    assert "master-multi-calendar-appointment-booking-gohighlevel" not in rendered
    assert "fbq(" not in rendered


def test_same_silo_spokes_link_back_and_agent_studio_title_stays():
    agent = _post("how-to-build-ai-agents-in-gohighlevel-agent-studio-guide")
    assert agent["title"] == LOCKED_AGENT
    for slug, anchor in SPOKES.items():
        html = _post(slug)["html_content"]
        assert html.count(HOST_HREF) == 1, slug
        assert f">{anchor}</a>" in html


def test_cross_silo_calendar_link_would_unwrap():
    """CRM multi-calendar is a different topic. A followed href is removed
    at render. The fold names the constraint and does not emit the href."""
    host = _post(HOST)
    silo = {
        HOST: ("en", AI_TOPIC),
        "master-multi-calendar-appointment-booking-gohighlevel": ("en", "CRM & Communication"),
        "gohighlevel-ai-agents-automation-complete-guide": ("en", AI_TOPIC),
    }
    sample = (
        '<p>See <a href="/blog/master-multi-calendar-appointment-booking-gohighlevel/">'
        "multi calendar</a>.</p>"
    )
    out = build.unwrap_cross_silo_links(sample, host, silo_map=silo, url_map={})
    assert "<a " not in out
    assert "multi calendar" in out
    pillar = _post("gohighlevel-ai-agents-automation-complete-guide")
    kept = build.unwrap_cross_silo_links(
        pillar["html_content"], pillar, silo_map=silo, url_map={}
    )
    assert HOST_HREF in kept


def test_rendered_spoke_keeps_backlink(tmp_path, monkeypatch):
    slug = "build-ai-bots-without-code-gohighlevel-guided-form-setup"
    rendered = _render(_post(slug), tmp_path, monkeypatch)
    assert HOST_HREF in rendered
    assert "fbq(" not in rendered
