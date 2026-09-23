#!/usr/bin/env python3
"""en-IN posts must not call PayU native or say Razorpay bills SaaS Mode.

HighLevel's provider table (help 155000006075, fetched 2026-09-22) has no PayU
row and marks Razorpay No for SaaS Mode. v0.3.20.0 fixed `/in/` and the India
pricing guide. This gate covers the rest of the India corpus, including the
guide, so a later edit cannot put the old claim back.

Run: python3 -m pytest scripts/test_india_payment_truth.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"

# A PayU mention is allowed only inside a denial. Match the phrase, not the
# intent: "not natively" / "custom integration" are the sentences that already
# told the truth before this pass (WhatsApp Business API setup).
DENIAL = re.compile(
    r"PayU is not a native"
    r"|PayU is not native"
    r"|PayU is not in the provider table"
    r"|PayU is not in HighLevel's provider table"
    r"|not natively"
    r"|via a custom integration"
    r"|custom build"
    r"|नेटिव इंटीग्रेशन नहीं",
    re.I,
)
SAAS_DENIAL = re.compile(
    r"does not bill SaaS Mode|SaaS Mode का बिल नहीं करता"
)
FORBIDDEN = (
    "Razorpay/PayU",
    "Razorpay or PayU",
    "Razorpay and PayU",
    "Razorpay, PayU",
    "PayU integration is also available",
    "integrates directly with Razorpay, PayU",
    "SaaS mode with Stripe/Razorpay",
    "SaaS-style services",
    # Leftover "use both / every Indian gateway" after PayU was deleted from the sentence.
    "Set up both",
    "Both are GST-compliant",
    "all major Indian",
    "other Indian payment",
    "Instamojo",
    "UPI Direct",
    "are all supported",
    "integrations with both",
    "integrates with both",
    "all supported natively",
    "any major payment gateway",
    "सभी payment gateways",
    "तीनों major",
    "native UPI",
    "Native UPI",
    "All three payment methods",
    "All three are integrated",
    "all gateways",
    "other payment gateways",
    "integrates with all three",
    "UPI native support",
    "Native Razorpay + UPI",
)
TAG = re.compile(r"<[^>]+>")


def _plain(value: str) -> str:
    return re.sub(r"\s+", " ", TAG.sub(" ", value))


def _strings(obj):
    if isinstance(obj, dict):
        for child in obj.values():
            yield from _strings(child)
    elif isinstance(obj, list):
        for child in obj:
            yield from _strings(child)
    elif isinstance(obj, str):
        yield obj


def _india_posts():
    for path in sorted(POSTS.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("language") == "en-IN":
            yield path.stem, data


def payu_mentions_are_denied(blob: str) -> list[str]:
    """Return PayU windows that do not sit next to a denial."""
    bad = []
    for match in re.finditer(r"PayU", blob):
        window = blob[max(0, match.start() - 180) : match.end() + 180]
        if not DENIAL.search(window):
            bad.append(re.sub(r"\s+", " ", window)[:160])
    return bad


def test_gate_fires_on_a_native_claim_and_passes_a_denial():
    """Both edges. A gate tested on only one side is half-tested."""
    assert payu_mentions_are_denied("GoHighLevel integrates with Razorpay and PayU.")
    assert payu_mentions_are_denied("Select Razorpay or PayU in Payment Gateways.")
    assert payu_mentions_are_denied(
        "Custom integrations (Razorpay, PayU, UPI, TMS systems)"
    )
    assert not payu_mentions_are_denied(
        "PayU is not a native HighLevel integration."
    )
    assert not payu_mentions_are_denied(
        "PayU is not in the provider table, so it is not a native integration."
    )
    assert not payu_mentions_are_denied(
        "local gateways like PayU connect via a custom integration, not natively."
    )


def test_india_corpus_has_no_payu_native_or_razorpay_saas_claim():
    offenders = []
    for slug, data in _india_posts():
        blob = "\n".join(_strings(data))
        for phrase in FORBIDDEN:
            if phrase in blob:
                offenders.append(f"{slug}: forbidden {phrase!r}")
        offenders.extend(f"{slug}: {snip}" for snip in payu_mentions_are_denied(blob))
        plain = _plain(blob)
        for sentence in re.split(r"(?<=[.?!।])\s+", plain):
            if (
                re.search(r"Razorpay", sentence)
                and "SaaS Mode" in sentence
                and not SAAS_DENIAL.search(sentence)
            ):
                offenders.append(f"{slug}: SaaS Mode without denial: {sentence[:160]}")
    assert offenders == [], offenders[:12]


def test_pricing_guide_and_razorpay_setup_still_deny_the_claims():
    guide = json.loads(
        (POSTS / "gohighlevel-pricing-india-2026-rupees-complete-guide.json").read_text(
            encoding="utf-8"
        )
    )
    setup = json.loads(
        (POSTS / "how-to-accept-razorpay-upi-payments-in-gohighlevel-india.json").read_text(
            encoding="utf-8"
        )
    )
    assert "Razorpay does not bill SaaS Mode" in guide["html_content"]
    assert "PayU is not native" in guide["html_content"]
    assert "Razorpay does not bill SaaS Mode" in setup["html_content"]
    assert "SaaS-style services" not in setup["html_content"]
    assert guide["title"] == "GoHighLevel Pricing India 2026: Plans from Rs 8,000/Month"
