#!/usr/bin/env python3
"""The India pricing guide must match the provider table (William lock, 2026-09-22).

`gohighlevel-pricing-india-2026-rupees-complete-guide` used to say SaaS Mode
bills through Razorpay and that PayU is a native integration. HighLevel's
provider table (help 155000006075, fetched 2026-09-22) marks Razorpay No for
SaaS Mode and does not list PayU. The visible FAQ and the inline FAQPage
answer are the same string, so a one-sided edit would ship a rich result
that still tells the old lie.

Run: python3 -m pytest scripts/test_india_pricing_honesty.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from build import india_hub_intro  # noqa: E402
from fix_faq_schema import visible_pairs  # noqa: E402

POST = ROOT / "posts" / "gohighlevel-pricing-india-2026-rupees-complete-guide.json"
TITLE = "GoHighLevel Pricing India 2026: Plans from Rs 8,000/Month"
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

FORBIDDEN = (
    "PayU integration is also available",
    "Stripe/Razorpay",
    "PayU, and UPI",
    "PayU, UPI native",
    "UPI native",
    "UPI included",
    "integrates directly with Razorpay, PayU",
    "SaaS mode with Stripe/Razorpay",
)


def _post() -> dict:
    return json.loads(POST.read_text(encoding="utf-8"))


def test_title_unchanged_and_under_the_ratchet():
    title = _post()["title"]
    assert title == TITLE, title
    assert len(title) <= 60, len(title)


def test_guide_denies_razorpay_saas_mode_and_native_payu():
    post = _post()
    html = post["html_content"]
    blob = html + "\n" + post["description"]
    for bad in FORBIDDEN:
        assert bad not in blob, bad
    assert html.count("Razorpay does not bill SaaS Mode") == 1
    desc = post["description"]
    assert "Razorpay does not bill SaaS Mode" in desc
    # build.truncate cuts at 160 and drops the last word. A cut inside
    # "does not bill SaaS Mode" would tell a searcher Razorpay does not bill.
    from build import truncate
    shown = truncate(desc, 160)
    assert len(desc) <= 160, len(desc)
    assert shown == desc
    assert shown.endswith("SaaS Mode.")
    assert "PayU is not in the provider table" in html
    assert "PayU is not native" in html
    assert "not a native integration" in html


def test_faq_answer_matches_schema():
    html = _post()["html_content"]
    visible = dict(visible_pairs(html))
    q = "What payment methods can my clients use through GHL?"
    assert q in visible, list(visible)
    assert "PayU is not in HighLevel's provider table" in visible[q]
    schema_answer = None
    for m in LD.finditer(html):
        obj = json.loads(m.group(1))
        if obj.get("@type") != "FAQPage":
            continue
        for item in obj["mainEntity"]:
            if item.get("name") == q:
                schema_answer = item["acceptedAnswer"]["text"]
    assert schema_answer == visible[q]


def test_hub_card_routes_without_calling_the_guide_wrong():
    """Lock 3: once the guide is accurate, the card must not contradict it.
    Lock 4: the hub still says older India posts are wrong about PayU."""
    intro = india_hub_intro()
    assert "That guide still says" not in intro
    assert "The pricing guide says the same thing." in intro
    assert "Razorpay does not bill SaaS Mode" in intro
    assert "Where an older India post says PayU is built in, that sentence is wrong." in intro
