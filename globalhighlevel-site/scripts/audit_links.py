#!/usr/bin/env python3
"""Link-hygiene audit gate for globalhighlevel.com (added 2026-06-22).

Parses the BUILT public/ tree and enforces the Caleb non-local internal-link rules
that verify.py does not cover. Run AFTER build.py, BEFORE deploy.

Scope of the EDITORIAL checks (1,2,5): only links inside the article prose
(`<div class="post-body">`), excluding (a) conversion CTAs to the robots-disallowed
attribution path (/trial) and (b) any rel=nofollow link — nofollow CTAs pass no
equity, so they can't form a manipulative-anchor footprint; the cliff rule shapes
FOLLOWED equity only. (Doctrine updated 2026-07-23: /start and /coupon are RETIRED
crawlable 301s as of v0.2.10.1 — no longer exempt paths. The in-post CTAs now point
at the money page directly with rel=nofollow, which exemption (b) covers.) That is
exactly the set Caleb's authority doctrine cares about — breadcrumb, author box,
related/listing cards, nav and footer are navigational chrome (siblings of
.post-body), not editorial links.

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

ORPHAN_TARGET = 3
PUBLIC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "public"
# Conversion/attribution paths: /trial is the robots-disallowed attribution page;
# the language variants are the localized conversion landings hardcoded in
# firehose-era bodies. Imported from build.py so builder exemptions and audit
# exemptions can never desynchronize. /start + /coupon were retired to crawlable
# 301s (v0.2.10.1) — no longer exempt; if they break, the audit must SEE it.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build import ATTRIBUTION_PREFIXES as EXEMPT_PREFIXES  # noqa: E402
from build import is_attribution_path  # noqa: E402  (segment-boundary matcher)
# Single source of truth: builder drops >CAP, gate fails on >CAP; a built hub has
# >= MIN_HUB_CARDS cards. Importing (not mirroring) means they can't desynchronize.
from build import ANCHOR_URL_CAP as CAP, MIN_HUB_POSTS as MIN_HUB_CARDS  # noqa: E402
from build import SITE_URL  # noqa: E402
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
        self.links = []                 # (href, anchor, in_body: bool, nofollow: bool)
        self._href = None
        self._buf = ""
        self._link_in_body = False
        self._link_nofollow = False
        self.card_count = 0
        self.has_body = False           # True if page has a post-body (a pillar-backed hub)

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
            self._link_nofollow = "nofollow" in (a.get("rel") or "").split()
            self._buf = ""
        if tag not in VOID:
            is_body = self._is_body_wrapper(attrs)
            self.stack.append((tag, is_body))
            if is_body:
                self.body_count += 1
                self.has_body = True

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._buf.split()),
                               self._link_in_body, self._link_nofollow))
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
    # Absolute same-site URLs are internal too — normalize before checking, so a
    # restored body's https://globalhighlevel.com/blog/dead/ link can't bypass
    # the 404 gate (codex 2026-07-23).
    p = href.replace(SITE_URL, "").split("#")[0].split("?")[0] or "/"
    if not p.startswith("/"):
        return True
    if is_attribution_path(p):
        return True
    rel = p.strip("/")
    return bool((PUBLIC / rel / "index.html").exists() or (PUBLIC / rel).is_file() or p == "/")


def is_attribution(url: str) -> bool:
    return is_attribution_path(url)


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

        # A pillar-backed hub renders the full pillar article (has a post-body), so it
        # is content-rich even with <2 spoke cards — only flag list-only hubs as thin.
        if "/category/" in page and p.card_count < MIN_HUB_CARDS and not p.has_body:
            thin_hubs.append((page, p.card_count))

        for href, anchor, in_body, nofollow in p.links:
            if href.startswith(("#", "mailto:", "tel:")):
                continue
            # internal 404 — ANY zone, followed or not (a broken nofollow CTA still
            # 404s). Absolute same-site hrefs count as internal (codex 2026-07-23).
            if (href.startswith("/") or href.startswith(SITE_URL)) \
                    and not page_path_exists(href):
                internal_404.append((href, page))
            # editorial checks — post-body only, internal, non-attribution, FOLLOWED
            # (nofollow conversion CTAs pass no equity — exempt from anchor doctrine)
            is_internal = href.startswith("/") or href.startswith(SITE_URL)
            if not (in_body and is_internal) or nofollow:
                continue
            url = href.replace(SITE_URL, "").split("#")[0].split("?")[0]
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
