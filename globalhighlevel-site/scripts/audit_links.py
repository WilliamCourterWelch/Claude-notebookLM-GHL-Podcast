#!/usr/bin/env python3
"""Link-hygiene audit gate for globalhighlevel.com (added 2026-06-22).

Parses the BUILT public/ tree and enforces the Caleb non-local internal-link rules
that verify.py does not cover. Run AFTER build.py, BEFORE deploy.

Scope of the EDITORIAL checks (1,2,5): only links inside the article prose
(`<div class="post-body">`), excluding conversion CTAs to the robots-disallowed
attribution paths (/trial,/coupon,/start). That is exactly the set Caleb's authority
doctrine cares about — breadcrumb, author box, related/listing cards, nav and footer
are navigational chrome (siblings of .post-body), not editorial links.

FAILS (exit 1):
  1. anchor cliff   — same editorial anchor->URL pair repeated > CAP times
  2. single-word    — an editorial link whose anchor is a bare single token (>=5 chars)
  3. thin hub       — a built /category/ page with fewer than 2 post cards
  4. internal 404   — ANY same-site link pointing at a path with no built page
REPORTS (never fails):
  5. near-orphans   — blog posts with < TARGET editorial inbound links (T6 curation signal)
"""
import sys, re
from pathlib import Path
from html.parser import HTMLParser

CAP = 3              # MUST track build.py ANCHOR_URL_CAP (builder drops >CAP; gate fails on >CAP)
ORPHAN_TARGET = 3
MIN_HUB_CARDS = 2    # MUST track build.py MIN_HUB_POSTS (a built hub has >= this many cards)
PUBLIC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "public"
EXEMPT_PREFIXES = ("/trial", "/coupon", "/start")  # robots-disallowed attribution / conversion CTAs
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}
BODY_WRAPPERS = ("post-body", "post-content")  # article-prose containers


class LinkParser(HTMLParser):
    """Tracks whether each <a> sits inside the article prose (.post-body/.post-content).

    Uses an explicit element STACK, not a numeric depth threshold, so a single
    unbalanced/stray closing tag in machine-generated post HTML cannot desync the
    parser and silently drop the rest of the article from the editorial checks
    (the fail-open vector the review flagged). Stray closers with no matching open
    are ignored; body membership is keyed on the specific wrapper element and only
    cleared when that element actually closes.
    """
    def __init__(self):
        super().__init__()
        self.stack = []                 # list of (tagname, is_body_wrapper)
        self.body_count = 0             # open .post-body/.post-content ancestors
        self.links = []                 # (href, anchor, in_body: bool)
        self._href = None
        self._buf = ""
        self._link_in_body = False
        self.card_count = 0

    def _is_body_wrapper(self, attrs):
        tokens = (dict(attrs).get("class") or "").split()
        return any(w in tokens for w in BODY_WRAPPERS)  # exact class token, not substring

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "article" and "card" in (a.get("class") or "").split():
            self.card_count += 1
        if tag == "a" and a.get("href"):
            self._href = a["href"]
            self._link_in_body = self.body_count > 0
            self._buf = ""
        if tag not in VOID:
            is_body = self._is_body_wrapper(attrs)
            self.stack.append((tag, is_body))
            if is_body:
                self.body_count += 1

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._buf.split()), self._link_in_body))
            self._href = None
        if tag in VOID:
            return
        # Pop back to the nearest matching open tag. A stray closer with no match is
        # ignored (no desync), so unbalanced HTML cannot fail the gate open.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                while len(self.stack) > i:
                    _, was_body = self.stack.pop()
                    if was_body:
                        self.body_count -= 1
                break

    def handle_data(self, data):
        if self._href is not None:
            self._buf += data


def page_path_exists(href: str) -> bool:
    p = href.split("#")[0].split("?")[0]
    if not p.startswith("/"):
        return True
    if any(p.rstrip("/").startswith(e) for e in EXEMPT_PREFIXES):
        return True
    rel = p.strip("/")
    return bool((PUBLIC / rel / "index.html").exists() or (PUBLIC / rel).is_file() or p == "/")


def is_attribution(url: str) -> bool:
    return any(url.rstrip("/").startswith(e) for e in EXEMPT_PREFIXES)


def main():
    if not PUBLIC.exists():
        print(f"AUDIT ERROR: public dir not found: {PUBLIC}", file=sys.stderr)
        return 2

    anchor_pairs, single_word, internal_404, thin_hubs, inbound = {}, [], [], [], {}
    html_files = list(PUBLIC.rglob("index.html"))
    blog_paths = {f"/{f.parent.relative_to(PUBLIC).as_posix()}/"
                  for f in html_files if "blog" in f.parent.parts}

    for f in html_files:
        page = "/" + f.parent.relative_to(PUBLIC).as_posix() + "/"
        if page == "/./": page = "/"
        p = LinkParser()
        p.feed(f.read_text(encoding="utf-8", errors="replace"))

        if "/category/" in page and p.card_count < MIN_HUB_CARDS:
            thin_hubs.append((page, p.card_count))

        for href, anchor, in_body in p.links:
            if href.startswith(("#", "mailto:", "tel:")):
                continue
            # internal 404 — ANY zone
            if href.startswith("/") and not page_path_exists(href):
                internal_404.append((href, page))
            # editorial checks — post-body only, internal, non-attribution
            is_internal = href.startswith("/") or href.startswith("https://globalhighlevel.com")
            if not (in_body and is_internal):
                continue
            url = href.replace("https://globalhighlevel.com", "").split("#")[0].split("?")[0]
            if is_attribution(url):
                continue
            if not anchor:
                continue
            anchor_pairs[(anchor.lower(), url)] = anchor_pairs.get((anchor.lower(), url), 0) + 1
            if " " not in anchor and len(anchor) >= 5 and re.fullmatch(r"[A-Za-z][A-Za-z']+", anchor):
                single_word.append((anchor, url, page))
            tgt = url.rstrip("/") + "/"
            if tgt in blog_paths:
                inbound[tgt] = inbound.get(tgt, 0) + 1

    cliffs = {k: v for k, v in anchor_pairs.items() if v > CAP}
    fails = 0
    print(f"=== Link audit on {PUBLIC} ({len(html_files)} pages) ===")

    if cliffs:
        fails += 1
        print(f"\nFAIL (1) anchor cliff — {len(cliffs)} editorial anchor->URL pairs repeated > {CAP}:")
        for (anc, url), n in sorted(cliffs.items(), key=lambda x: -x[1])[:20]:
            print(f"   {n:>3}x  '{anc[:60]}' -> {url}")
    else:
        print(f"OK   (1) no editorial anchor->URL pair repeats more than {CAP}x")

    if single_word:
        fails += 1
        uniq = sorted(set(single_word))
        print(f"\nFAIL (2) single-word editorial anchors — {len(uniq)} found:")
        for anc, url, page in uniq[:20]:
            print(f"   '{anc}' -> {url}   (on {page})")
    else:
        print("OK   (2) no single-word / bare-brand editorial anchors")

    if thin_hubs:
        fails += 1
        print(f"\nFAIL (3) thin hubs (<2 cards) that should not have been built:")
        for url, n in thin_hubs:
            print(f"   {url}  ({n} cards)")
    else:
        print("OK   (3) no thin (<2 post) category pages built")

    if internal_404:
        fails += 1
        uniq = sorted(set(internal_404))
        print(f"\nFAIL (4) internal links to unbuilt pages — {len(uniq)}:")
        for href, page in uniq[:20]:
            print(f"   {href}   (on {page})")
    else:
        print("OK   (4) no internal links to unbuilt (404) pages")

    orphans = sorted(((inbound.get(b, 0), b) for b in blog_paths))
    print(f"\n(5) Editorial inbound per blog post (target >={ORPHAN_TARGET}, report-only — T6 curation):")
    for n, b in orphans:
        flag = "  <-- near-orphan" if n < ORPHAN_TARGET else ""
        print(f"   {n:>3}  {b}{flag}")

    print(f"\n=== {'PASS' if fails == 0 else 'FAIL'} ({fails} gate(s) failed) ===")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
