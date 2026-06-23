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


def main():
    print("test_build_links.py")
    for t in (test_anchor_cap, test_build_link_index_multiword_only, test_hub_link_block):
        t()
    print(f"\n{'PASS' if not FAILED else 'FAIL'} — {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
