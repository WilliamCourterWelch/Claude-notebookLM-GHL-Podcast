#!/usr/bin/env python3
"""verify.py — phase gate for the language x topic restructure.

Runs against the built public/ output and asserts three invariants. Each later
phase of the restructure must keep these green before /seo-deploy-gate.

  Check 0  Lang vs slug  : a post's `language` field must not contradict a specific
                           slug marker (catches a migration that wrote the wrong
                           language; the other checks trust the field and can't).
  Check 1  English-root  : every root /category/<topic>/ page lists ONLY English posts.
  Check 2  No orphans    : every post with a live /blog/ page appears in >=1 listing.
  Check 3  No dead links : every internal href resolves to a generated page or a
                           _redirects rule (minus KNOWN_DANGLING, which T6 clears).
  Check 4  Canon links   : Caleb-canon template invariants on built output —
                           spoke->pillar link present, link circles close, no
                           cross-silo/cross-language template links, and sink
                           pages (mvp_minimal_links) emit ZERO outbound internal
                           links (D3/D9, full-restore sprint 2026-07-23).

Usage:
    cd globalhighlevel-site
    python3 build.py        # produce public/
    python3 verify.py       # gate it

Exit 0 = clean, 1 = one or more checks failed. Reuses build.post_lang() so the
language classification is identical to what the build uses for listings.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import build  # same directory; main() is guarded so importing is side-effect-free

PUBLIC = build.PUBLIC_DIR

# T6 (2026-05-27): all pre-existing dead links cleared, so this allowlist is now
# empty — the gate flags EVERY dangling internal link with no exceptions.
#   - the bucket-category link (/es/category/gohighlevel-espanol/) vanished when T3
#     removed language buckets from the topic axis;
#   - the 3 LATAM hub/spoke links + the bare /blog/ nav link were resolved by routing
#     listing cards through post_url() (so they point at the real /es/para/ URLs) and
#     pointing the Spanish hub nav at /es/.
KNOWN_DANGLING: set[str] = set()


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def blog_slugs(html: str) -> set[str]:
    """All /blog/<slug>/ targets in a page, unicode-safe and percent-decoded."""
    return {unquote(m) for m in re.findall(r'href="/blog/([^"]+?)/?"', html)}


def internal_hrefs(html: str) -> set[str]:
    return set(re.findall(r'href="(/[^"#?]*)"', html))


def norm(h: str) -> str:
    return unquote(h.split("#")[0].split("?")[0])


def main() -> int:
    if not PUBLIC.exists():
        print(f"ERROR: {PUBLIC} not found — run `python3 build.py` first.")
        return 1

    posts = build.load_posts()
    lang_by_slug = {p["slug"]: build.post_lang(p) for p in posts if p.get("slug")}
    all_slugs = set(lang_by_slug)
    fails: list[str] = []

    # --- Check 0: language field must not contradict a specific slug marker -
    # Every other check resolves language via build.post_lang(), which just
    # echoes the explicit `language` field. So those checks CANNOT detect a
    # migration that wrote the WRONG language — they'd validate the bad field
    # against itself. This check is the independent cross-reference: if a slug
    # carries a SPECIFIC marker (es / en-IN / ar) but the resolved language
    # disagrees, that's a mislabel. Pre-migration this flags the known India
    # posts the T2 migration is built to fix; post-apply it must be 0, and it
    # will FAIL on any NEW bad write (e.g. a Spanish post stamped `en`).
    print("=== Check 0: language field agrees with slug markers ===")

    def infer_lang_from_slug(slug: str) -> str:
        s = (slug or "").lower()
        for code, markers in build._LANG_SLUG_MARKERS:
            if any(m in s for m in markers):
                return code
        return "en"

    contradictions = []
    for slug, resolved in sorted(lang_by_slug.items()):
        marker = infer_lang_from_slug(slug)
        if marker != "en" and marker != resolved:
            contradictions.append((slug, resolved, marker))
    print(f"  slug-marked posts whose language field disagrees: {len(contradictions)}"
          " (pre-migration: these are the T2 targets; post-apply must be 0)")
    for slug, resolved, marker in contradictions[:10]:
        print(f"    - {slug}: language={resolved!r} but slug marker says {marker!r}")
    print("  ->", "PASS" if not contradictions else f"FAIL ({len(contradictions)} mislabeled)")
    if contradictions:
        fails.append(f"Check 0: {len(contradictions)} posts whose language field contradicts their slug marker")

    # --- Check 1: root /category/ pages English-only -----------------------
    print("=== Check 1: root /category/ pages are English-only ===")
    contam = 0
    for idx in sorted((PUBLIC / "category").glob("*/index.html")):
        slug = idx.parent.name
        links = blog_slugs(read(idx))
        bad = sorted(s for s in links if lang_by_slug.get(s, "en") != "en")
        contam += len(bad)
        flag = "  <-- CONTAMINATED" if bad else ""
        print(f"  /category/{slug}/: {len(links)} posts, {len(bad)} non-English{flag}")
        if bad:
            print("      e.g.", bad[:6])
    print("  ->", "PASS" if not contam else f"FAIL ({contam} cross-language links)")
    if contam:
        fails.append(f"Check 1: {contam} cross-language links on root category pages")

    # --- Check 2: no orphaned posts ----------------------------------------
    print("\n=== Check 2: no orphaned posts (each live post in >=1 listing) ===")
    listing_globs = [
        "index.html", "page/*/index.html", "category/*/index.html",
        "es/index.html", "es/page/*/index.html", "es/category/*/index.html",
        "in/index.html", "in/page/*/index.html", "in/category/*/index.html",
        "ar/index.html", "ar/page/*/index.html", "ar/category/*/index.html",
    ]
    listed: set[str] = set()
    for g in listing_globs:
        for f in PUBLIC.glob(g):
            listed |= blog_slugs(read(f))
    orphans = [s for s in sorted(all_slugs - listed)
               if (PUBLIC / "blog" / s / "index.html").exists()]
    print(f"  listed: {len(all_slugs & listed)}/{len(all_slugs)} | orphans with a live /blog/ page: {len(orphans)}")
    for s in orphans[:10]:
        print(f"    - {s} (lang={lang_by_slug.get(s)})")
    print("  ->", "PASS" if not orphans else f"FAIL ({len(orphans)} orphans)")
    if orphans:
        fails.append(f"Check 2: {len(orphans)} orphaned posts")

    # --- Check 3: no dangling internal links -------------------------------
    print("\n=== Check 3: no dangling internal links ===")
    pages: set[str] = set()
    for f in PUBLIC.rglob("index.html"):
        rel = f.parent.relative_to(PUBLIC)
        pages.add("/" if str(rel) == "." else f"/{rel}/")
    for f in PUBLIC.iterdir():
        if f.is_file():
            pages.add("/" + f.name)
    redirects: set[str] = set()
    rf = PUBLIC / "_redirects"
    if rf.exists():
        for ln in read(rf).splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                src = ln.split()[0]
                redirects |= {src, src.rstrip("/") + "/", src.rstrip("/")}

    def resolves(h: str) -> bool:
        h = norm(h)
        if (h in pages or h in redirects
                or h.rstrip("/") + "/" in pages
                or h.rstrip("/") in redirects or h.rstrip("/") + "/" in redirects):
            return True
        # Static assets (e.g. the /images/logo.png favicon) live in subdirs, not in the
        # page set. An href that maps to a real file INSIDE public/ resolves — but reject
        # any ".." traversal so a link can't escape public/ and match a repo file (which
        # would never be deployed as a live asset). Confirm the resolved path stays under public/.
        rel = h.lstrip("/")
        if not rel or ".." in rel.split("/"):
            return False
        target = (PUBLIC / rel).resolve()
        pub = PUBLIC.resolve()
        return (target == pub or pub in target.parents) and target.is_file()

    dangling: dict[str, int] = {}
    for f in PUBLIC.rglob("*.html"):
        for h in internal_hrefs(read(f)):
            if not resolves(h):
                dangling[norm(h)] = dangling.get(norm(h), 0) + 1
    new_dangling = {h: n for h, n in dangling.items() if h not in KNOWN_DANGLING}
    known_hit = {h: n for h, n in dangling.items() if h in KNOWN_DANGLING}
    print(f"  NEW dangling targets: {len(new_dangling)} | known-pending (T6): {len(known_hit)}")
    for h, n in sorted(new_dangling.items(), key=lambda x: -x[1])[:15]:
        print(f"    {n:5d}x  {h}")
    print("  ->", "PASS" if not new_dangling else f"FAIL ({len(new_dangling)} new dead links)")
    if new_dangling:
        fails.append(f"Check 3: {len(new_dangling)} new dangling internal links")

    # --- Check 4: canon link invariants (D3, 2026-07-23) -------------------
    # The Caleb-canon template structure must hold on the BUILT output:
    #   a. spoke->pillar : every non-sink EN post with a built hub links UP to it
    #   b. circle closes : each post's rendered circle-nav matches the computed
    #                      prev/next; wraparound means the silo forms one cycle
    #   c. no cross-silo : circle + related-card targets stay same-lang+same-topic
    #   d. sink exclusion: mvp_minimal_links pages gain ZERO outbound internal
    #                      links (no circle, no related cards, no hub link, no
    #                      /blog|/category anchors in the post body)
    print("\n=== Check 4: canon link invariants (spoke->pillar, circles, silo, sink) ===")
    slug_meta = {p["slug"]: (build.post_lang(p), build.post_topic(p))
                 for p in posts if p.get("slug")}
    c4_fails: list[str] = []
    for p in posts:
        slug = p.get("slug")
        if not slug:
            continue
        if build.is_series_post(p):
            continue  # authority template: series nav is its cluster structure, not the circle
        page = PUBLIC / build.post_output_rel(p) / "index.html"
        if not page.exists():
            continue
        html = read(page)
        is_sink = bool(p.get("mvp_minimal_links"))
        is_pillar_blog = bool(p.get("isPillar")) and p.get("language", "en") == "en"
        lang, topic = build.post_lang(p), build.post_topic(p)

        if is_sink:
            # d. sink exclusion — zero outbound internal links, in any template slot
            if 'class="circle-nav"' in html or 'class="related-posts"' in html or 'class="hub-link"' in html:
                c4_fails.append(f"sink {slug}: template block (circle/related/hub) present")
            # slice body -> cta-end (nested divs make a </div> match under-scan)
            b_start = html.find('class="post-body"')
            b_end = html.find('class="cta-end"', b_start)
            body = html[b_start:b_end] if b_start >= 0 and b_end > b_start else html
            for m in re.finditer(r'<a\b([^>]*)>', body):
                attrs = m.group(1)
                href_m = re.search(r'href="(/(?:blog|category)/[^"]*)"', attrs)
                if href_m and "nofollow" not in attrs:
                    c4_fails.append(f"sink {slug}: followed internal link {href_m.group(1)} in body")
            continue

        # a. spoke->pillar (EN posts whose hub is built; eyebrow/hub-link carries it)
        cat_slug = build.slugify(build.display_cat(topic) or "GoHighLevel Tutorials")
        if lang == "en" and not is_pillar_blog and cat_slug in build.LIVE_CATEGORY_SLUGS:
            if f'href="/category/{cat_slug}/"' not in html:
                c4_fails.append(f"{slug}: no link to its hub /category/{cat_slug}/")

        # b. circle closes — rendered nav matches the computed neighbors
        prev_p, next_p = (None, None) if is_pillar_blog else build.circle_neighbors(p, posts)
        if next_p is not None:
            want_next = f'class="circle-next" href="{build.post_url(next_p)}"'
            if want_next not in html:
                c4_fails.append(f"{slug}: circle-next missing/wrong (want {build.post_url(next_p)})")
            if prev_p is not next_p:
                want_prev = f'class="circle-prev" href="{build.post_url(prev_p)}"'
                if want_prev not in html:
                    c4_fails.append(f"{slug}: circle-prev missing/wrong (want {build.post_url(prev_p)})")
        elif 'class="circle-nav"' in html:
            c4_fails.append(f"{slug}: unexpected circle-nav (singleton silo or excluded page)")

        # c. no cross-silo/cross-language in template blocks (related cards + circle
        # both render between the author box and the JSON-LD scripts — scan that zone)
        starts = [i for i in (html.find('class="related-posts"'), html.find('class="circle-nav"')) if i >= 0]
        if starts:
            zone = html[min(starts):html.find('<script type="application/ld+json">')]
            for tgt in re.findall(r'href="[^"]*?/blog/([^"/]+)/?"', zone):
                meta = slug_meta.get(unquote(tgt))
                if meta and meta != (lang, topic):
                    c4_fails.append(f"{slug}: cross-silo template link -> {tgt} {meta} != {(lang, topic)}")
    for msg in c4_fails[:20]:
        print(f"    {msg}")
    print("  ->", "PASS" if not c4_fails else f"FAIL ({len(c4_fails)} canon violations)")
    if c4_fails:
        fails.append(f"Check 4: {len(c4_fails)} canon link invariant violations")

    print("\n" + "=" * 52)
    if fails:
        print("VERIFY: FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("VERIFY: PASS — 0 lang/slug mismatches, 0 contamination, 0 orphans, 0 new dead links, canon invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
