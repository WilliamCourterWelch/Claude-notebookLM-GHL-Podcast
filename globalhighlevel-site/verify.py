#!/usr/bin/env python3
"""verify.py — phase gate for the language x topic restructure.

Runs against the built public/ output and asserts seven invariants (Checks 0-6).
Each later phase of the restructure must keep these green before /seo-deploy-gate.

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
  Check 5  Redirect shadow : no _redirects rule may shadow a built page, no
                           duplicate sources, no /blog/ 301 into a 404.
  Check 6  Sitemap parity : every sitemap <loc> is a built page and never a
                           redirect source.

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
    """Root-relative hrefs PLUS absolute same-site hrefs (normalized to relative)
    — an absolute same-site dead link is just as dead (codex 2026-07-23)."""
    rel = set(re.findall(r'href="(/[^"#?]*)"', html))
    abs_ = set(re.findall(r'href="' + re.escape(build.SITE_URL) + r'(/[^"#?]*)"', html))
    return rel | abs_


def norm(h: str) -> str:
    return unquote(h.split("#")[0].split("?")[0])


def main() -> int:
    if not PUBLIC.exists():
        print(f"ERROR: {PUBLIC} not found — run `python3 build.py` first.")
        return 1

    # Verify against the SAME dicts the build rendered from — merge_data can add
    # episode fields (publishedAt fallbacks etc.) that change circle ordering, so
    # raw load_posts() could compute different neighbors than the build did
    # (red-team 2026-07-23).
    posts = build.merge_data(build.load_posts(), build.load_published())
    # Check 4 reads build's module globals, which only build.main() populates.
    # Load them here or the spoke->pillar check silently never fires (the
    # `cat_slug in LIVE_CATEGORY_SLUGS` gate would test against an empty set —
    # review finding 2026-07-23). Live hubs come from the BUILT output, which is
    # what this gate verifies anyway.
    build.CATEGORIES, build.LANGUAGES = build.load_categories()
    build.LIVE_CATEGORY_SLUGS = {p.parent.name for p in (PUBLIC / "category").glob("*/index.html")}
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

    # --- Check 0b: body script must agree with the language field ----------
    # Slug markers only see slugs, so an Arabic post with an unmarked slug (or
    # an Arabic body stamped `en`) sails through Check 0 — the exact leak the
    # gate exists to prevent. Arabic is trivially detectable from script
    # (U+0600–U+06FF), so check both directions on the body, and require the
    # ar posts' title+description to be Arabic too (the SERP surface)
    # (adversarial + codex + red-team consensus, 2026-07-27).
    print("\n=== Check 0b: body script agrees with language field ===")
    import re as _re
    _AR_RE = _re.compile(r"[\u0600-\u06FF]")
    script_fails = []
    for post in posts:
        slug = post.get("slug", "")
        lang = build.post_lang(post)
        body = post.get("html_content", "")
        ar_chars = len(_AR_RE.findall(body))
        ratio = ar_chars / max(1, len(body))
        if lang == "ar":
            if ratio < 0.05:
                script_fails.append(f"{slug}: language=ar but body is only {ratio:.1%} Arabic script")
            if not _AR_RE.search(post.get("title", "")):
                script_fails.append(f"{slug}: language=ar but title has no Arabic script")
            if not _AR_RE.search(post.get("description", post.get("seoDescription", ""))):
                script_fails.append(f"{slug}: language=ar but description has no Arabic script")
        elif ratio > 0.05:
            script_fails.append(f"{slug}: language={lang!r} but body is {ratio:.1%} Arabic script")
    for msg in script_fails[:10]:
        print(f"    {msg}")
    print("  ->", "PASS" if not script_fails else f"FAIL ({len(script_fails)} script/language mismatches)")
    if script_fails:
        fails.append(f"Check 0b: {len(script_fails)} body-script/language mismatches")

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
        if f.name == "404.html":
            continue  # error page: its self-referential canonical is /404 by design
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
    #   e. body silo scan : followed internal post links in the BODY prose are
    #                      same-silo, funnel-sink, or series-nav — the unwrap
    #                      pass is fail-open, this is the alarm (D13)
    print("\n=== Check 4: canon link invariants (spoke->pillar, circles, silo, sink) ===")
    slug_meta = {p["slug"]: (build.post_lang(p), build.post_topic(p))
                 for p in posts if p.get("slug")}
    # e. body-zone silo scan needs URL-keyed metadata: custom-url_path posts
    #    (/es/para/..., /es/mercadopago-gohighlevel/) are invisible to slug
    #    lookups — the bypass that hid 15 cross-silo links (D13, 2026-07-27).
    url_meta = {build.post_url(p): (p["slug"], (build.post_lang(p), build.post_topic(p)))
                for p in posts if p.get("slug")}
    c4_fails: list[str] = []
    _c4e_scanned = [0]  # zones actually scanned — 0 at the end means the alarm is dead

    def _c4e_scan(label: str, page_html: str, lang: str, topic: str, src_url: str,
                  end_marker: str, body_class: str = 'class="post-body'):
        """Check 4e body-zone scanner. Tolerant of class-token variants
        ('class="post-body fade-3"'), loud when the zone is missing or
        unterminated (codex P2: the alarm must not silently empty itself)."""
        b_start = page_html.find(body_class)
        if b_start < 0:
            c4_fails.append(f"{label}: 4e body zone MISSING ({body_class} not found)")
            return
        b_end = page_html.find(end_marker, b_start)
        if b_end < 0:
            b_end = page_html.find('<script type="application/ld+json">', b_start)
        if b_end < 0:
            c4_fails.append(f"{label}: 4e body zone UNTERMINATED (no {end_marker} / JSON-LD after post-body)")
            return
        body = page_html[b_start:b_end]
        _c4e_scanned[0] += 1
        for m in re.finditer(r'<a\b([^>]*)>', body):
            attrs = m.group(1)
            href_m = re.search(
                r'href="(?:' + re.escape(build.SITE_URL) + r')?(/[^"]+?)"', attrs)
            if not href_m:
                continue
            rel_m = re.search(r'rel="([^"]*)"', attrs)
            if rel_m and "nofollow" in rel_m.group(1).split():
                continue
            tgt_url = unquote(href_m.group(1)).split("?")[0].split("#")[0]
            if not tgt_url.endswith("/"):
                tgt_url += "/"
            t_meta = url_meta.get(tgt_url)
            if t_meta is None:
                continue  # not a post page (hub, landing, asset)
            t_slug, t_silo = t_meta
            if t_slug in build.FUNNEL_SINK_SLUGS or t_silo == (lang, topic):
                continue
            if build._series_nav_exempt(src_url, tgt_url, url_meta):
                continue
            c4_fails.append(f"{label}: cross-silo BODY link -> {tgt_url} {t_silo} != {(lang, topic)}")
    for p in posts:
        slug = p.get("slug")
        if not slug:
            continue
        if build.is_series_post(p):
            # authority template: series nav is its cluster structure, not the
            # circle — skip circle checks, but its body STILL goes through the
            # unwrap pass, so the 4e alarm must cover it (codex P2 re-review).
            auth_page = PUBLIC / build.post_output_rel(p) / "index.html"
            if auth_page.exists():
                _c4e_scan(f"authority {slug}", read(auth_page),
                          build.post_lang(p), build.post_topic(p), build.post_url(p),
                          end_marker='<script type="application/ld+json">',
                          body_class='class="auth-body')
            continue
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
            # the category eyebrow must be plain text on a sink (it was the last
            # followed outbound leak — red-team 2026-07-23)
            eb = re.search(r'class="post-eyebrow[^"]*">(.*?)</div>', html, re.S)
            if eb and "<a " in eb.group(1):
                c4_fails.append(f"sink {slug}: followed eyebrow link present")
            # slice body -> cta-end (nested divs make a </div> match under-scan)
            b_start = html.find('class="post-body"')
            b_end = html.find('class="cta-end"', b_start)
            body = html[b_start:b_end] if b_start >= 0 and b_end > b_start else html
            for m in re.finditer(r'<a\b([^>]*)>', body):
                attrs = m.group(1)
                href_m = re.search(
                    r'href="(?:' + re.escape(build.SITE_URL) + r')?(/(?:blog|category)/[^"]*)"', attrs)
                rel_m = re.search(r'rel="([^"]*)"', attrs)
                followed = not (rel_m and "nofollow" in rel_m.group(1).split())
                if href_m and followed:
                    c4_fails.append(f"sink {slug}: followed internal link {href_m.group(1)} in body")
            continue

        # a. spoke->pillar (EN posts whose hub is built; eyebrow/hub-link carries it).
        # Scope to the post's own template zones — the header/footer nav links every
        # hub on every page, so a whole-document search passes vacuously even if the
        # eyebrow/hub-link disappeared (codex P2, 2026-07-23).
        cat_slug = build.slugify(build.display_cat(topic) or "GoHighLevel Tutorials")
        if lang == "en" and not is_pillar_blog and cat_slug in build.LIVE_CATEGORY_SLUGS:
            eb_m = re.search(r'class="post-eyebrow[^"]*">(.*?)</div>', html, re.S)
            hub_m = re.search(r'class="hub-link".*?</p>', html, re.S)
            zones = (eb_m.group(1) if eb_m else "") + (hub_m.group(0) if hub_m else "")
            if f'href="/category/{cat_slug}/"' not in zones:
                c4_fails.append(f"{slug}: no eyebrow/hub-link to its hub /category/{cat_slug}/")

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
            # search for the JSON-LD terminator AFTER the block start — the head
            # carries a WebSite schema that would otherwise end the slice before
            # it begins, silently emptying this check (codex P2, 2026-07-23)
            zone_end = html.find('<script type="application/ld+json">', min(starts))
            zone = html[min(starts):zone_end if zone_end > 0 else len(html)]
            for tgt in re.findall(r'href="[^"]*?/blog/([^"/]+)/?"', zone):
                meta = slug_meta.get(unquote(tgt))
                if meta and meta != (lang, topic):
                    c4_fails.append(f"{slug}: cross-silo template link -> {tgt} {meta} != {(lang, topic)}")

        # e. body-zone silo scan (D13, 2026-07-27): the unwrap pass is fail-open
        # (empty map -> silent no-op), so the BUILT body prose is the ground
        # truth. Any followed internal post link in the body must be same-silo,
        # a funnel sink, or series navigation. This catches both a silently
        # disabled unwrap AND link shapes the unwrap regex can't see.
        # Fail-loud (codex P2): a missing/unterminated body zone is itself a
        # failure — an emptied slice must never silently pass the alarm.
        _c4e_scan(slug, html, lang, topic, build.post_url(p),
                  end_marker='class="cta-end"')
    # e (continued): EN hub pillars render their body on the /category/ page,
    # NOT at /blog/ — the per-post loop never sees them. This was the exact
    # render site the unwrap pass itself missed (codex P1, 2026-07-27), so the
    # alarm must cover it too.
    for p in posts:
        if not (p.get("isPillar") and p.get("language", "en") == "en" and p.get("slug")):
            continue
        _cat = build.display_cat(build.post_topic(p))
        _cs = build.slugify(_cat or "")
        hub_page = PUBLIC / "category" / _cs / "index.html"
        if not _cs or not hub_page.exists():
            continue
        _c4e_scan(f"hub-pillar {p['slug']} (/category/{_cs}/)", read(hub_page),
                  build.post_lang(p), build.post_topic(p), build.post_url(p),
                  end_marker='class="cards-grid"')
    if _c4e_scanned[0] == 0:
        c4_fails.append("Check 4e scanned ZERO body zones — the silo alarm is dead (template class drift?)")
    for msg in c4_fails[:20]:
        print(f"    {msg}")
    print("  ->", "PASS" if not c4_fails else f"FAIL ({len(c4_fails)} canon violations)")
    print(f"    (4e: {_c4e_scanned[0]} body zones scanned)")
    if c4_fails:
        fails.append(f"Check 4: {len(c4_fails)} canon link invariant violations")

    # --- Check 5: no _redirects rule shadows a built page ------------------
    # Cloudflare Pages follows _redirects BEFORE serving static files, so a rule
    # whose source is a built page makes that page live-unreachable. 158 of the
    # 931 restore slugs had prune-era 301 rules — build.py prunes them from the
    # deployed copy; this gate proves the prune worked (red-team 2026-07-23).
    # (`redirects` and `pages` are the locals built in Check 3's section.)
    print("\n=== Check 5: no _redirects rule shadows a built page ===")
    # every source variant that resolves to a built page OR deployed root file —
    # including "/" itself (a root rule would shadow the homepage)
    shadowed = sorted(h for h in redirects if h in pages)
    for h in shadowed[:10]:
        print(f"    shadowed: {h}")
    # 5b: duplicate sources — Cloudflare is first-match-wins, so a second rule
    # with the same source silently never fires (batch-1 review, 2026-07-23)
    rf_lines = [ln.strip() for ln in read(rf).splitlines()
                if ln.strip() and not ln.strip().startswith("#")] if rf.exists() else []
    srcs = [ln.split()[0] for ln in rf_lines]
    dupes = sorted({x for x in srcs if srcs.count(x) > 1})
    for d in dupes[:10]:
        print(f"    duplicate source (first-match shadows the rest): {d}")
    # 5c: every /blog/-targeted rule must land on a built page or another rule —
    # a permanent 301 into a 404 is worse than the 404 (batch-1 review, 2026-07-23)
    dead_targets = []
    for ln in rf_lines:
        parts = ln.split()
        if len(parts) >= 2 and parts[1].startswith("/blog/"):
            tgt = parts[1]
            variants = {tgt, tgt.rstrip("/"), tgt.rstrip("/") + "/"}
            if not (variants & pages) and not (variants & set(srcs)):
                dead_targets.append(f"{parts[0]} -> {tgt}")
    for d in dead_targets[:10]:
        print(f"    301 into 404: {d}")
    # 5d: no redirect chains — Cloudflare is single-pass, so a rule whose
    # target is itself a rule source costs a real second 301 (adversarial
    # review 2026-07-27). Checked on the DEPLOYED rule set.
    chains = []
    _src_set = set(srcs)
    for ln in rf_lines:
        parts = ln.split()
        if len(parts) >= 2:
            tgt = parts[1]
            for v in {tgt, tgt.rstrip("/"), tgt.rstrip("/") + "/"}:
                if v in _src_set:
                    chains.append(f"{parts[0]} -> {tgt} (target is itself a rule source)")
                    break
    for c in chains[:10]:
        print(f"    chain: {c}")
    # 5e: source-file hygiene — a rule in the SOURCE _redirects whose source is
    # a built page gets silently shadow-pruned at deploy; that dormant rule
    # resurrects (possibly as a chain) the moment the page is removed again.
    # The source file must describe production: no silently-pruned rules
    # (adversarial review 2026-07-27; 304 stale lines cleaned same day).
    _src_file = PUBLIC.parent / "_redirects"
    stale_src = []
    if _src_file.exists():
        for ln in read(_src_file).splitlines():
            t = ln.strip()
            if t and not t.startswith("#") and len(t.split()) >= 2:
                h = t.split()[0]
                if h in pages:
                    stale_src.append(h)
    for h in stale_src[:10]:
        print(f"    stale source rule (shadow-pruned at deploy): {h}")
    _c5_bad = len(shadowed) + len(dupes) + len(dead_targets) + len(chains) + len(stale_src)
    print("  ->", "PASS" if not _c5_bad else
          f"FAIL ({len(shadowed)} shadowed, {len(dupes)} duplicate sources, {len(dead_targets)} dead 301 targets, {len(chains)} chains, {len(stale_src)} stale source rules)")
    if _c5_bad:
        fails.append(f"Check 5: {_c5_bad} redirect defects (shadowed/duplicate/dead-target/chain/stale-source)")

    # --- Check 6: sitemap <-> built parity ---------------------------------
    # Every sitemap <loc> must be a built page (or deployed root file) and must
    # NOT be a _redirects source — the hole that let 5 pillar 301-URLs ship to
    # IndexNow (red-team 2026-07-23).
    print("\n=== Check 6: sitemap advertises only built, non-redirected pages ===")
    sm = PUBLIC / "sitemap.xml"
    sm_bad = []
    if sm.exists():
        locs = re.findall(r"<loc>(.*?)</loc>", read(sm))
        src_set = set(srcs)
        for loc in locs:
            path = loc.replace(build.SITE_URL, "") or "/"
            variants = {path, path.rstrip("/"), path.rstrip("/") + "/"}
            if not (variants & pages):
                sm_bad.append(f"not built: {path}")
            elif variants & src_set:
                sm_bad.append(f"redirect source in sitemap: {path}")
        print(f"  sitemap locs: {len(locs)} | defects: {len(sm_bad)}")
        for b in sm_bad[:10]:
            print(f"    {b}")
    else:
        sm_bad.append("sitemap.xml missing from build output")
        print("  sitemap.xml MISSING")
    # 6b reverse direction: every built non-pillar post must be IN the sitemap
    # (the exists()-skip in build_sitemap must only ever drop pillar 301-URLs —
    # a silent build failure must not silently shrink the sitemap)
    if sm.exists():
        loc_paths = {l.replace(build.SITE_URL, "").rstrip("/") + "/" for l in locs}
        for p_ in posts:
            if p_.get("isPillar") and p_.get("language", "en") == "en":
                continue
            u = build.post_url(p_)
            if (PUBLIC / build.post_output_rel(p_) / "index.html").exists() and u not in loc_paths:
                sm_bad.append(f"built post missing from sitemap: {u}")
    # 6c: ZERO followed paid links sitewide — catches every rel-bug variant
    # (single-quoted rel, duplicate rel attr, uppercase <A) that the render
    # pass could miss (adversarial 2026-07-23)
    followed_paid = []
    from html.parser import HTMLParser

    class _PaidLinkScan(HTMLParser):
        def __init__(self):
            super().__init__()
            self.hit = False
        def handle_starttag(self, tag, attrs):
            if tag != "a" or self.hit:
                return
            d = dict(attrs)
            href = d.get("href") or ""
            if "fp_ref=" in href:
                rel = (d.get("rel") or "").split()
                if "nofollow" not in rel:
                    self.hit = True

    for f_ in PUBLIC.rglob("index.html"):
        sc = _PaidLinkScan()
        sc.feed(read(f_))
        if sc.hit:
            followed_paid.append(str(f_.relative_to(PUBLIC)))
    for fp_ in followed_paid[:10]:
        print(f"    followed paid link on: {fp_}")
    if followed_paid:
        sm_bad.extend(f"followed fp_ref anchor: {x}" for x in followed_paid)
    print("  ->", "PASS" if not sm_bad else f"FAIL ({len(sm_bad)} sitemap/paid-link defects)")
    if sm_bad:
        fails.append(f"Check 6: {len(sm_bad)} sitemap/paid-link defects")

    # ---- Check 7: SERP title-length ratchet -------------------------------
    # Caleb Ulku's non-local canon puts title tags at 50-60 characters, which is
    # about where Google truncates. On 2026-08-25 the whole built tree was
    # measured: median 83c and 95% over 60, because " | Global High Level" was
    # appended unconditionally to 973 of 980 pages. compose_title() (build.py)
    # now drops the brand when it does not fit, taking the median to 63c and the
    # over-60 count to TITLE_OVERLONG_BASELINE.
    #
    # This is a RATCHET, not a clean gate. 590 pages are still too long on their
    # own words and need real title rewrites, which change the visible <h1> too
    # (a post's `title` drives both). Failing outright would block every build
    # until that work is done, so instead the count may shrink but never grow.
    # LOWER THE BASELINE as you rewrite titles — that is the point of it.
    print("\n=== Check 7: SERP title length (Caleb canon: 50-60 chars) ===")
    # Import the budget rather than restating it. A second `TITLE_MAX = 60` here
    # would be free to drift from build.py's, and the gate would then be checking
    # a different rule than the composer enforces.
    TITLE_MAX = build.TITLE_MAX
    # Ratchet history — lower this as titles land, never raise it:
    #   590  v0.3.15.0  conditional brand suffix (mechanical, sitewide)
    #   580  v0.3.16.0  10 hand-rewritten titles, picked by BING impressions
    TITLE_OVERLONG_BASELINE = 580
    _t_re = re.compile(r"<title>(.*?)</title>", re.S)
    _noindex_re = re.compile(r'name="robots"[^>]*noindex')

    # Scan EVERY .html, not just index.html. 404.html is a standalone file and
    # was invisible to an index.html-only scan, which is how its hardcoded brand
    # suffix survived the conversion. (Codex adversarial, 2026-08-25.)
    #
    # Skip noindex pages. A page excluded from search has no SERP title to
    # budget, so neither the length ceiling nor the branding rule means anything
    # for it — and without this a future short noindex page (a /thanks/ titled
    # "Thanks") would trip the mirror invariant below for no reason. Today this
    # exempts 5 pages (404 + the four /trial/ landings) and changes no count:
    # 0 of them are overlong and 0 have room for the brand.
    _titled = []
    for f_ in sorted(PUBLIC.rglob("*.html")):
        h_ = read(f_)
        m_ = _t_re.search(h_)
        if not m_ or _noindex_re.search(h_):
            continue
        _titled.append((m_.group(1), str(f_.relative_to(PUBLIC))))

    overlong = [(len(t_), p_) for t_, p_ in _titled if len(t_) > TITLE_MAX]
    n_over = len(overlong)
    print(f"  titles over {TITLE_MAX} chars: {n_over} (baseline {TITLE_OVERLONG_BASELINE})")

    # HARD invariant, not a ratchet: no page may keep the brand suffix while
    # over the limit. That combination means a title was composed somewhere
    # that does not route through compose_title(). It caught exactly that on
    # 2026-08-25 — build.py has a SECOND, separate page template for the
    # /es/para/<vertical>/ pages (build.py:1935) that still hardcoded
    # "{title} | {SITE_NAME}", so 2 pages kept a 20-char suffix at 85 chars
    # while every other call site had been converted.
    _brand_suffix = f" | {build.SITE_NAME}"
    branded_overlong = [p_ for t_, p_ in _titled
                        if len(t_) > TITLE_MAX and t_.endswith(_brand_suffix)]
    if branded_overlong:
        for p_ in branded_overlong[:5]:
            print(f"    keeps brand while overlong: {p_}")
        print(f"  -> FAIL ({len(branded_overlong)} pages bypass compose_title)")
        fails.append(
            f"Check 7: {len(branded_overlong)} overlong titles still carry the brand "
            f"suffix (a title is being composed outside compose_title)"
        )

    # MIRROR invariant. The check above only catches a caller that keeps the
    # brand when it should not. This catches the opposite bypass: a title with
    # room for the brand that does not carry it. compose_title ALWAYS appends
    # when it fits, so a short unbranded title proves the page was composed
    # somewhere else. Without this, a caller could regress from
    # compose_title("Page 2") to a bare "Page 2" and every gate would still
    # pass. Verified 0 false positives across the built tree on 2026-08-25.
    # (Codex adversarial, 2026-08-25.)
    short_unbranded = [(len(t_), p_) for t_, p_ in _titled
                       if not t_.endswith(_brand_suffix)
                       and len(t_) + len(_brand_suffix) <= TITLE_MAX]
    if short_unbranded:
        for L_, p_ in sorted(short_unbranded)[:5]:
            print(f"    room for brand but missing it ({L_}c): {p_}")
        print(f"  -> FAIL ({len(short_unbranded)} pages bypass compose_title)")
        fails.append(
            f"Check 7: {len(short_unbranded)} titles have room for the brand but "
            f"lack it (a title is being composed outside compose_title)"
        )
    if n_over > TITLE_OVERLONG_BASELINE:
        for L_, p_ in sorted(overlong, reverse=True)[:5]:
            print(f"    {L_}c  {p_}")
        print("  -> FAIL (regression: more overlong titles than the baseline)")
        fails.append(
            f"Check 7: {n_over} overlong titles > baseline {TITLE_OVERLONG_BASELINE}"
        )
    else:
        if n_over < TITLE_OVERLONG_BASELINE:
            print(
                f"  -> PASS (improved by {TITLE_OVERLONG_BASELINE - n_over} — "
                f"lower TITLE_OVERLONG_BASELINE to {n_over} in verify.py)"
            )
        else:
            print("  -> PASS (holding at baseline)")

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
