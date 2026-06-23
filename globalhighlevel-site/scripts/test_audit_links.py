#!/usr/bin/env python3
"""Tests for the link-hygiene gate (scripts/audit_links.py). Pure-Python, no network.

Run: python3 scripts/test_audit_links.py
Exits 0 if all pass, 1 otherwise. Uses temp dirs; never touches the real public/ tree.

Priority: the gate's own correctness. A fail-OPEN gate (silently passing while letting a
violation through) is worse than no gate, so the parser fail-closed behavior and the
end-to-end exit codes are the load-bearing cases here.
"""
import sys
import tempfile
from pathlib import Path

import audit_links as al
from audit_links import LinkParser

FAILED = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        FAILED.append(name)


def inbody_map(html):
    p = LinkParser()
    p.feed(html)
    return {h: ib for h, _, ib in p.links}


def test_body_vs_chrome():
    m = inbody_map('<nav><a href="/x/">nav</a></nav>'
                   '<div class="post-body"><p><a href="/y/">deep editorial anchor</a></p></div>')
    check("nav link classified as chrome (not body)", m.get("/x/") is False)
    check("post-body link classified as editorial", m.get("/y/") is True)


def test_fail_closed_stray_close():
    # A single stray </p> must NOT desync the parser and drop the rest of the article.
    m = inbody_map('<div class="post-body"><p>x</p></p>'
                   '<p><a href="/y/">deep editorial anchor</a></p></div>'
                   '<footer><a href="/z/">foot</a></footer>')
    check("stray </p>: later post-body link still editorial (fail-closed)", m.get("/y/") is True)
    check("stray </p>: footer link still chrome", m.get("/z/") is False)


def test_void_and_nested():
    m = inbody_map('<div class="post-body"><figure><img src="a.png">'
                   '<a href="/in/">inner anchor</a></figure></div>'
                   '<footer><a href="/out/">out</a></footer>')
    check("img (void) inside post-body does not break nesting", m.get("/in/") is True)
    check("link after post-body close is chrome", m.get("/out/") is False)


def test_wrapper_exact_token():
    # 'post-content-wrapper' must NOT count as the editorial body (exact token, not substring).
    m = inbody_map('<div class="post-content-wrapper"><a href="/w/">x anchor</a></div>')
    check("post-content-wrapper is NOT treated as editorial body", m.get("/w/") is False)
    m2 = inbody_map('<article class="post-content"><a href="/c/">x anchor</a></article>')
    check("exact post-content token IS editorial body", m2.get("/c/") is True)


def test_page_path_exists():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "blog" / "real").mkdir(parents=True)
        (root / "blog" / "real" / "index.html").write_text("x")
        orig = al.PUBLIC
        al.PUBLIC = root
        try:
            check("existing built page -> True", al.page_path_exists("/blog/real/") is True)
            check("missing page -> False (so 404 check can fire)", al.page_path_exists("/blog/missing/") is False)
            check("exempt attribution path -> True even if unbuilt", al.page_path_exists("/trial/") is True)
            check("root -> True", al.page_path_exists("/") is True)
        finally:
            al.PUBLIC = orig


def _page(public, rel, body):
    p = public / rel
    p.mkdir(parents=True, exist_ok=True)
    (p / "index.html").write_text(body, encoding="utf-8")


def run_main_on(tree_builder):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        tree_builder(root)
        orig = al.PUBLIC
        al.PUBLIC = root
        try:
            return al.main()
        finally:
            al.PUBLIC = orig


def test_main_clean_passes():
    def build(root):
        _page(root, "blog/a", '<div class="post-body"><p>hi</p></div>')
        _page(root, "blog/b", '<div class="post-body"><p>hi</p></div>')
    check("clean tree -> main() == 0", run_main_on(build) == 0)


def test_main_thin_hub_fails():
    def build(root):
        _page(root, "blog/a", '<div class="post-body"><p>hi</p></div>')
        _page(root, "category/thin", '<article class="card">one</article>')  # 1 card < MIN_HUB_CARDS
    check("thin hub (1 card) -> main() == 1", run_main_on(build) == 1)


def test_main_anchor_cliff_boundary():
    anchor = '<a href="/blog/t/">deep editorial anchor phrase</a>'
    def build_ok(root):   # exactly CAP occurrences -> OK (v > CAP is the fail rule)
        _page(root, "blog/t", '<div class="post-body"><p>target</p></div>')
        for i in range(al.CAP):
            _page(root, f"blog/p{i}", f'<div class="post-body"><p>{anchor}</p></div>')
    def build_fail(root):  # CAP+1 occurrences -> FAIL
        _page(root, "blog/t", '<div class="post-body"><p>target</p></div>')
        for i in range(al.CAP + 1):
            _page(root, f"blog/p{i}", f'<div class="post-body"><p>{anchor}</p></div>')
    check(f"anchor repeated exactly CAP({al.CAP})x -> main() == 0", run_main_on(build_ok) == 0)
    check(f"anchor repeated CAP+1({al.CAP+1})x -> main() == 1", run_main_on(build_fail) == 1)


def test_main_internal_404_fails():
    def build(root):
        _page(root, "blog/a", '<div class="post-body"><p>'
                              '<a href="/blog/ghost/">a missing internal target link</a></p></div>')
    check("internal link to unbuilt page -> main() == 1", run_main_on(build) == 1)


def main():
    print("test_audit_links.py")
    for t in (test_body_vs_chrome, test_fail_closed_stray_close, test_void_and_nested,
              test_wrapper_exact_token, test_page_path_exists, test_main_clean_passes,
              test_main_thin_hub_fails, test_main_anchor_cliff_boundary,
              test_main_internal_404_fails):
        t()
    print(f"\n{'PASS' if not FAILED else 'FAIL'} — {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
