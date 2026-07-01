"""
build.py — Static site generator for globalhighlevel.com

Reads:
  - posts/*.json         (blog post HTML + metadata, saved by 5-blog.py)
  - data/published.json  (podcast episode metadata; relocated from the retired pipeline)

Generates:
  - public/index.html                      homepage
  - public/blog/{slug}/index.html          individual posts
  - public/category/{slug}/index.html      category pages
  - public/sitemap.xml                     sitemap
  - public/404.html                        404 page
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from lang_check import validate_meta

BASE_DIR       = Path(__file__).parent
POSTS_DIR      = BASE_DIR / "posts"
PUBLIC_DIR     = BASE_DIR / "public"
PUBLISHED_JSON = BASE_DIR / "data" / "published.json"
CATEGORIES_JSON = BASE_DIR / "categories.json"

SITE_URL     = os.getenv("SITE_URL", "https://globalhighlevel.com")
SITE_NAME    = os.getenv("SITE_NAME", "Global High Level")
SITE_TAGLINE = os.getenv("SITE_TAGLINE", "GoHighLevel Tutorials, Guides & Strategies for Agencies Worldwide")
AFFILIATE    = os.getenv("GHL_AFFILIATE_LINK", "https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12&utm_source=globalhighlevel&utm_medium=website")
# Spanish funnel lands on the localized bootcamp (same fp_ref / FirstPromoter
# attribution, Spanish landing page). fp_ref tracks by param, not by slug, so
# attribution is unchanged — only the language of the destination changes.
AFFILIATE_ES = AFFILIATE.replace("/highlevel-bootcamp?", "/highlevel-bootcamp-es?")

def affiliate_for(lang: str) -> str:
    """Language-aware affiliate base URL. Spanish -> -es bootcamp; others -> default."""
    return AFFILIATE_ES if lang == "es" else AFFILIATE

GA_ID        = "G-HYT0YKNGX2"
CLARITY_ID   = "wkeq0t21ww"
ACCENT       = "#f59e0b"   # amber
ACCENT_DARK  = "#d97706"

# Module-level categories — loaded in main()
CATEGORIES = []   # topic categories (list of dicts)
LANGUAGES  = []   # language definitions (list of dicts)
# EN category slugs that actually have a built page after the 2026-06-03 prune.
# Gates nav/footer category links so they never point at an emptied (404) category.
LIVE_CATEGORY_SLUGS = set()
# P0.3 (2026-06-22): site-wide cap on identical crawlable anchor->URL pairs. Even
# title-only related anchors + injected body links can repeat the same anchor text at
# the same URL across many posts, the manipulative-anchor signal Google demotes. Keyed
# on (anchor_text_lower, url); injected/hub links beyond ANCHOR_URL_CAP are dropped so
# the footprint stays varied. Cleared at the start of each build().
ANCHOR_URL_CAP = 3
# P1.1: a category gets a built hub page only with >= this many posts (mirrors the
# language-topic-page rule). audit_links.py mirrors this value (card_count < 2).
MIN_HUB_POSTS = 2
_ANCHOR_URL_COUNTS: dict = {}


def _cat_link_html(cat: str, css_class: str, extra_style: str = "") -> str:
    """Category label: a real link only when its hub is built (LIVE_CATEGORY_SLUGS),
    else plain text. Centralizes the P1.1 gating shared by every card type so the
    rule lives in one place (was duplicated 4x)."""
    if not cat:
        return ""
    style = f' style="{extra_style}"' if extra_style else ""
    cs = slugify(cat)
    if cs in LIVE_CATEGORY_SLUGS:
        return f'<a href="/category/{cs}/" class="{css_class}"{style}>{cat}</a>'
    return f'<span class="{css_class}"{style}>{cat}</span>'

def _anchor_under_cap(anchor: str, url: str) -> bool:
    """True if (anchor,url) is still under the site-wide cap; registers the use on True."""
    key = (" ".join(anchor.lower().split()), url)
    if _ANCHOR_URL_COUNTS.get(key, 0) >= ANCHOR_URL_CAP:
        return False
    _ANCHOR_URL_COUNTS[key] = _ANCHOR_URL_COUNTS.get(key, 0) + 1
    return True

# Language codes that actually have a built hub (build_language_hub skips empty
# langs). Gates the language picker so it never links a 404 hub (e.g. /ar/).
LIVE_LANG_CODES = set()
# Relative paths of every category/language page that actually gets built. Gates
# hreflang alternates so they never point at an unbuilt (404) page post-prune.
BUILT_PAGE_PATHS = set()
# Slugs of blog posts that survived the prune. Gates post hreflang translation
# maps so they don't advertise pruned sibling-language posts (404) to Google.
LIVE_POST_SLUGS = set()

# ── Helpers ───────────────────────────────────────────────────────────────────

# Categories that bleed through from CMS and mean nothing to readers
_BAD_CATS = {"home", "uncategorized", "blog", "general", ""}

def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9-]", "", text.lower().replace(" ", "-"))
    return re.sub(r"-{2,}", "-", slug).strip("-")


def post_url(post: dict) -> str:
    """Canonical URL path for a post. Uses post['url_path'] if set, else /blog/{slug}/."""
    path = post.get("url_path")
    if path:
        if not path.startswith("/"):
            path = "/" + path
        if not path.endswith("/"):
            path = path + "/"
        return path
    return f"/blog/{post.get('slug', '')}/"


def post_output_rel(post: dict) -> str:
    """Output directory relative to PUBLIC_DIR (no leading slash, no index.html)."""
    return post_url(post).strip("/")

def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso[:19]).strftime("%B %d, %Y")
    except Exception:
        return ""

def truncate(text: str, n: int = 160) -> str:
    return text[:n].rsplit(" ", 1)[0] + "…" if len(text) > n else text

def display_cat(cat: str) -> str:
    """Return category label for display, or empty string if it's a CMS artifact."""
    if not cat or cat.strip().lower() in _BAD_CATS:
        return ""
    return cat.strip()

def read_time(html: str) -> str:
    """Estimate read time from HTML content word count."""
    words = len(re.sub(r"<[^>]+>", " ", html).split())
    mins = max(1, round(words / 200))
    return f"{mins} min read"

def extract_toc(html: str) -> list:
    """Extract (anchor_id, label) from H2 tags for table of contents."""
    items = []
    for m in re.finditer(r'<h2[^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</h2>', html, re.DOTALL):
        anchor = m.group(1)
        label  = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if label:
            items.append((anchor, label))
    if not items:
        for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL):
            label  = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            anchor = slugify(label)
            if label:
                items.append((anchor, label))
    return items[:8]

def inject_inline_ctas(html: str, cta_mid: str) -> str:
    """Inject one inline CTA at roughly the 50% H2 boundary."""
    h2_positions = [m.start() for m in re.finditer(r'<h2', html)]
    n = len(h2_positions)
    if n < 2:
        return html
    mid = h2_positions[n // 2]
    return html[:mid] + cta_mid + html[mid:]

# Slug-pattern markers for language inference. 470 of 946 posts have no
# explicit `language` field; these markers catch ~160 of those by slug stem.
# Conservative list — only unambiguous markers. T2.1 (body-text langdetect)
# will catch the remaining ~310.
_LANG_SLUG_MARKERS = (
    # 2026-05-23: dropped "whatsapp" — it is a product feature, not a geo signal,
    # and misclassified genuine English posts (e.g. how-to-manage-whatsapp-settings)
    # as India. Added high-precision India payment markers + Arabic "mena".
    ("en-IN", ("india", "indian", "rupee", "upi", "razorpay")),
    ("es",    ("espanol", "agencia", "plataforma", "latino", "mexico")),
)

# Category names that are really LANGUAGE buckets, not topics. They must never
# generate a root (English) /category/ page; their posts surface via the
# language hubs (/es/, /in/) and their own /blog/ URLs. 2026-05-23 cliff fix.
LANG_BUCKET_CATEGORIES = {
    "GoHighLevel en Español",
    "GoHighLevel en Espanol",
    "GoHighLevel India",
}


def post_lang(post: dict) -> str:
    """Return the post's language code, with slug-pattern fallback.

    Reads `post['language']` when set. When missing, infers from slug
    markers (e.g. india → en-IN, espanol → es). Falls back to 'en'.

    Treat 'en' and 'en-IN' as DIFFERENT base languages — India-targeted
    English posts must not appear as related cards on US-English posts.
    """
    lang = post.get("language")
    if lang:
        return lang
    slug = post.get("slug", "").lower()
    for code, markers in _LANG_SLUG_MARKERS:
        if any(m in slug for m in markers):
            return code
    return "en"


def post_topic(post: dict) -> str:
    """Return the post's TOPIC (subject axis), independent of language.

    Strangler-fig (T3): reads post['topic'] (backfilled by the T2 migration). For
    any post not yet migrated it falls back to a non-bucket `category`, then to the
    catch-all. Language buckets ('GoHighLevel India' / 'en Español') are NOT topics,
    so they never leak in through the fallback — they resolve to the catch-all.
    """
    topic = post.get("topic")
    if topic:
        return topic
    cat = post.get("category", "")
    if cat and cat not in LANG_BUCKET_CATEGORIES:
        return cat
    return "Agency & Platform"


def _hub_link_block(category: str, cat_slug: str, slug: str) -> str:
    """P1.2 (2026-06-22): one editorial in-body link UP to the category hub, with a
    VARIED anchor (Caleb: vary anchor text, never repeat) chosen deterministically per
    post slug and capped site-wide (P0.3). Returns '' when every variant is over cap so
    we never emit a uniform repeated hub anchor (Codex: that would be a fresh anchor cliff)."""
    cat_l = category.lower()
    url = f"/category/{cat_slug}/"
    variants = [
        f"more {cat_l} tutorials for GoHighLevel",
        f"our {cat_l} guides",
        f"the full {cat_l} guide library",
        f"all {cat_l} how-tos",
    ]
    pick = variants[int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(variants)]
    if not _anchor_under_cap(pick, url):
        for v in variants:
            if _anchor_under_cap(v, url):
                pick = v
                break
        else:
            return ""
    return f'\n<p class="hub-link">Keep learning: <a href="{url}">{pick}</a>.</p>'


def get_related(post: dict, all_posts: list, n: int = 3) -> list:
    """Return n related posts — same language, same topic first, then most recent.

    Language filter (added 2026-05-07) prevents the cross-language related-cards
    bug where English pages pulled Spanish / India / Arabic posts as 'Keep Reading'
    candidates. See post_lang() for slug-pattern inference logic.
    """
    slug = post.get("slug", "")
    topic = post_topic(post)
    target_lang = post_lang(post)
    same_lang = [p for p in all_posts if post_lang(p) == target_lang]
    same = [p for p in same_lang if p.get("slug") != slug and post_topic(p) == topic]
    other = [p for p in same_lang if p.get("slug") != slug and post_topic(p) != topic]
    return (same + other)[:n]


def _build_link_index(all_posts: list, target_lang=None) -> list[tuple[str, str, str, list[str]]]:
    """Build an index of (slug, title, category, keywords) for internal linking.
    Keywords are extracted from the title — split into meaningful phrases.

    When target_lang is provided, only posts matching that language are indexed.
    Filter-by-construction: any caller of this index automatically gets
    language-correct candidates without needing to filter results.
    """
    index = []
    stop = {"in", "the", "a", "an", "to", "for", "of", "and", "or", "how",
            "is", "it", "on", "at", "by", "with", "your", "you", "this",
            "that", "from", "its", "are", "be", "do", "was", "has", "can",
            "my", "our", "all", "no", "not", "what", "why", "when", "use",
            "set", "up", "get", "go", "new", "vs", "best", "top", "way"}
    for p in all_posts:
        if target_lang and post_lang(p) != target_lang:
            continue
        title = p.get("title", p.get("seoTitle", ""))
        slug = p.get("slug", "")
        cat = post_topic(p)
        if not title or not slug:
            continue
        # Extract 2-4 word phrases from title as linkable keywords
        words = re.sub(r"[^a-z0-9\s]", " ", title.lower()).split()
        meaningful = [w for w in words if w not in stop and len(w) > 2]
        phrases = []
        # P0.2 (2026-06-22): MULTI-WORD anchors only. Single-word phrases (any word
        # >=5 chars) were the bare-brand ("gohighlevel") AND generic single-token
        # ("pricing", "payments", "razorpay") anchor source. Caleb non-local: describe
        # the destination, never a bare word or brand name. Bigrams + trigrams only.
        for i in range(len(meaningful) - 1):
            phrases.append(f"{meaningful[i]} {meaningful[i+1]}")
        for i in range(len(meaningful) - 2):
            phrases.append(f"{meaningful[i]} {meaningful[i+1]} {meaningful[i+2]}")
        index.append((slug, title, cat, phrases, post_url(p)))
    return index


def inject_internal_links(html: str, post: dict, all_posts: list, max_links: int = 5) -> str:
    """Inject contextual internal links into post body.

    Scans paragraphs for keyword matches against other posts.
    Links are added as natural in-text hyperlinks, max one link per paragraph,
    max max_links total per post. Same-category posts preferred. Same-language
    only — language filter (added 2026-05-07) prevents cross-language body link
    pollution. See post_lang() for slug-pattern inference logic.
    """
    if not all_posts:
        return html

    slug = post.get("slug", "")
    cat = post_topic(post)
    target_lang = post_lang(post)
    link_index = _build_link_index(all_posts, target_lang=target_lang)

    # Score candidates: same category gets a boost
    candidates = []
    for s, title, c, phrases, url in link_index:
        if s == slug:
            continue
        score = 2 if c == cat else 1
        candidates.append((s, title, c, phrases, score, url))

    # Shuffle within score tiers so we don't always link the same posts
    import random
    rng = random.Random(slug)  # deterministic per post
    rng.shuffle(candidates)
    candidates.sort(key=lambda x: x[4], reverse=True)

    # Find paragraphs and inject links
    linked_slugs = set()
    links_added = 0
    parts = re.split(r'(<p[^>]*>.*?</p>)', html, flags=re.DOTALL)

    for i, part in enumerate(parts):
        if links_added >= max_links:
            break
        if not part.startswith('<p'):
            continue
        # Skip short paragraphs and paragraphs that already have links
        text_only = re.sub(r'<[^>]+>', '', part)
        if len(text_only) < 80 or '<a ' in part:
            continue

        text_lower = text_only.lower()
        for c_slug, c_title, c_cat, c_phrases, c_score, c_url in candidates:
            if c_slug in linked_slugs:
                continue
            # Find the best matching phrase in this paragraph
            best_match = None
            best_len = 0
            for phrase in c_phrases:
                if phrase in text_lower and len(phrase) > best_len:
                    # Find the actual-case version in the text
                    idx = text_lower.find(phrase)
                    if idx >= 0:
                        best_match = phrase
                        best_len = len(phrase)

            if best_match and best_len >= 5:
                # Find the match position in the original HTML paragraph
                idx = part.lower().find(best_match)
                if idx < 0:
                    continue
                # Make sure we're not inside an HTML tag
                before = part[:idx]
                if before.count('<') > before.count('>'):
                    continue
                original_text = part[idx:idx + len(best_match)]
                if not _anchor_under_cap(original_text, c_url):
                    continue  # P0.3: this exact anchor->URL pair already hit the site-wide cap
                link = f'<a href="{c_url}">{original_text}</a>'
                parts[i] = part[:idx] + link + part[idx + len(best_match):]
                linked_slugs.add(c_slug)
                links_added += 1
                break  # one link per paragraph

    return "".join(parts)

def load_categories() -> tuple[list[dict], list[dict]]:
    """Load category definitions from categories.json (new: languages + topics)."""
    if CATEGORIES_JSON.exists():
        data = json.loads(CATEGORIES_JSON.read_text())
        if isinstance(data, dict) and "topics" in data:
            return data.get("topics", []), data.get("languages", [])
        # Backward compat: old flat array format
        return data, []
    return [], []

def write(path: Path, html: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    print(f"  ✓ {path.relative_to(PUBLIC_DIR)}")

def sanitize_content(html: str) -> str:
    """Strip problematic inline elements from blog HTML before rendering.

    Removes:
    - In-content TOC blocks (divs with lists of #section-N anchor links)
    - In-content CTA boxes (blue-themed centered divs with affiliate links)
    """
    # Remove in-content TOC blocks: divs with light background containing
    # a heading/label + a list of #section-N anchor links
    html = re.sub(
        r'<div[^>]*style="[^"]*background:#f0f4ff[^"]*"[^>]*>.*?</div>',
        '',
        html,
        flags=re.DOTALL
    )

    # Remove in-content CTA boxes: solid blue background divs
    html = re.sub(
        r'<div[^>]*style="[^"]*background:#1a73e8[^"]*"[^>]*>.*?</div>',
        '',
        html,
        flags=re.DOTALL
    )

    # Remove bottom CTA boxes: light border/background with centered trial links
    html = re.sub(
        r'<div[^>]*style="[^"]*background:#f0f4ff[^"]*text-align:center[^"]*"[^>]*>.*?</div>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<div[^>]*style="[^"]*text-align:center[^"]*background:#f0f4ff[^"]*"[^>]*>.*?</div>',
        '',
        html,
        flags=re.DOTALL
    )

    # Remove the in-content "What's in This Guide" box (duplicate of the template TOC).
    # MUST require an in-page #anchor (the TOC signature) so we don't delete substantive
    # orange-left-border callouts ("30-Day Game Plan") or affiliate-CTA boxes that share
    # the border style. (review 2026-06-25: the broad version nuked real content + 2 ES CTAs.)
    html = re.sub(
        r'<div[^>]*style="[^"]*border-left:4px solid #f59e0b[^"]*"[^>]*>'
        r'(?:(?!</div>).)*?href="#(?:(?!</div>).)*?</div>',
        '',
        html,
        flags=re.DOTALL
    )

    # Let the template control heading typography — strip inline styles on h2/h3
    # (firehose-era inline font-sizes fought the template and made hierarchy inconsistent)
    html = re.sub(r'(<h[23]\b[^>]*?)\s+style="[^"]*"([^>]*>)', r'\1\2', html)

    return html

# ── CSS — TechCrunch-style editorial layout ──────────────────────────────────

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;0,9..40,800;1,9..40,400&display=swap');

:root{{
  --bg:#07080a;
  --bg2:#0c0e14;
  --surface:#111520;
  --amber:#f59e0b;
  --amber-light:#fbbf24;
  --amber-dim:rgba(245,158,11,0.12);
  --amber-border:rgba(245,158,11,0.22);
  --text:#eef2ff;
  --text2:#a0aec8;
  --text3:#6b7ea8;
  --border:rgba(255,255,255,0.06);
  --max:1120px;
  --content:820px;
  --accent:var(--amber);
  --sans:'DM Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:var(--sans);font-size:16px;line-height:1.7;color:var(--text);background:var(--bg);overflow-x:hidden;-webkit-font-smoothing:antialiased}}
a{{color:var(--amber);text-decoration:none}}
a:hover{{text-decoration:underline}}
img{{max-width:100%;height:auto}}

/* ANIMATIONS */
@keyframes fadeUp{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
.fade-1{{animation:fadeUp .6s ease both}}
.fade-2{{animation:fadeUp .6s .15s ease both}}
.fade-3{{animation:fadeUp .6s .3s ease both}}

/* ── NAV — fixed, backdrop blur, animated underlines ──────────────────────── */
nav{{position:fixed;top:0;inset-x:0;z-index:200;background:rgba(7,8,10,0.85);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}}
.nav-inner{{max-width:var(--max);margin:0 auto;padding:0 24px;height:56px;display:flex;align-items:center;justify-content:space-between;gap:32px}}
.logo{{flex-shrink:0}}
.logo{{font-family:var(--sans);font-size:1.15rem;font-weight:800;letter-spacing:-.3px;display:flex;align-items:center;gap:0;color:var(--text)}}
.logo-amber{{color:var(--amber)}}
.nav-links{{display:flex;align-items:center;gap:24px}}
.nav-link{{font-size:.82rem;font-weight:500;color:var(--text2);letter-spacing:.1px;transition:color .15s;position:relative;padding:4px 0}}
.nav-link::after{{content:'';position:absolute;bottom:0;left:0;width:0;height:2px;background:var(--amber);transition:width .2s ease-in-out}}
.nav-link:hover{{color:var(--text);text-decoration:none}}
.nav-link:hover::after{{width:100%}}
.nav-cta{{font-size:.8rem;font-weight:700;color:#000;background:var(--amber);padding:8px 18px;border-radius:8px;transition:background .15s}}
.nav-cta:hover{{background:var(--amber-light);text-decoration:none}}

/* ── HAMBURGER MENU ──────────────────────────────────────────────────────── */
.hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:8px;margin-left:auto;z-index:301}}
.hamburger span{{display:block;width:22px;height:2px;background:var(--text);border-radius:2px;transition:all .3s ease}}
.mobile-menu{{display:none;position:fixed;top:56px;inset-x:0;background:var(--bg);border-bottom:1px solid var(--border);padding:16px 24px 24px;z-index:199;flex-direction:column;gap:0}}
.mobile-menu a{{display:block;padding:12px 0;font-size:.95rem;font-weight:500;color:var(--text2);border-bottom:1px solid var(--border);transition:color .15s}}
.mobile-menu a:last-child{{border-bottom:none}}
.mobile-menu a:hover{{color:var(--text);text-decoration:none}}
.mobile-menu .nav-cta{{display:block;text-align:center;margin-top:16px;padding:12px;border-radius:8px;border-bottom:none;color:#000}}
#mobile-toggle{{display:none}}
#mobile-toggle:checked ~ .mobile-menu{{display:flex}}
#mobile-toggle:checked ~ .hamburger span:nth-child(1){{transform:rotate(45deg) translate(5px,5px)}}
#mobile-toggle:checked ~ .hamburger span:nth-child(2){{opacity:0}}
#mobile-toggle:checked ~ .hamburger span:nth-child(3){{transform:rotate(-45deg) translate(5px,-5px)}}

.nav-dropdown{{position:relative}}
.nav-dropdown-menu{{display:none;position:absolute;top:100%;left:-12px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:8px 0;min-width:220px;z-index:300;box-shadow:0 8px 24px rgba(0,0,0,.5);padding-top:16px}}
.nav-dropdown-menu::before{{content:'';position:absolute;top:-8px;left:0;right:0;height:16px}}
.nav-dropdown:hover .nav-dropdown-menu{{display:block}}
.nav-dropdown-menu a{{display:block;padding:8px 20px;font-size:.82rem;color:var(--text2);transition:color .15s,background .15s}}
.nav-dropdown-menu a:hover{{color:var(--text);background:rgba(255,255,255,.05);text-decoration:none}}

/* ── CONTAINER ────────────────────────────────────────────────────────────── */
.container{{max-width:var(--max);margin:0 auto;padding:0 24px}}

/* ── SECTION LABELS ───────────────────────────────────────────────────────── */
.section-label{{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid var(--amber);display:inline-block}}

/* ── HOMEPAGE — Featured + stack ──────────────────────────────────────────── */
.hp-featured{{display:grid;grid-template-columns:1.5fr 1fr;gap:32px;padding:88px 0 48px;border-bottom:1px solid var(--border)}}
.hp-lead{{display:flex;flex-direction:column;justify-content:center}}
.hp-lead-cat{{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:12px}}
.hp-lead-title{{font-family:var(--sans);font-size:clamp(2rem,4vw,3.5rem);font-weight:800;line-height:1.15;color:var(--text);margin-bottom:14px;letter-spacing:-.5px}}
.hp-lead-title a{{color:var(--text);transition:color .2s}}
.hp-lead-title a:hover{{color:var(--amber);text-decoration:none}}
.hp-lead-desc{{font-size:1rem;color:var(--text2);line-height:1.65;margin-bottom:16px}}
.hp-lead-meta{{font-size:13px;color:var(--text3);letter-spacing:.2px}}
.hp-stack{{display:flex;flex-direction:column;gap:0}}
.hp-stack-item{{padding:20px 0;border-bottom:1px solid var(--border)}}
.hp-stack-item:first-child{{padding-top:0}}
.hp-stack-item:last-child{{border-bottom:none}}
.hp-stack-cat{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:6px}}
.hp-stack-title{{font-family:var(--sans);font-size:1rem;font-weight:700;line-height:1.35;margin-bottom:6px}}
.hp-stack-title a{{color:var(--text);transition:color .15s}}
.hp-stack-title a:hover{{color:var(--amber);text-decoration:none}}
.hp-stack-meta{{font-size:12px;color:var(--text3)}}

/* ── HOMEPAGE — Main grid + sidebar ───────────────────────────────────────── */
.hp-body{{display:grid;grid-template-columns:1fr 320px;gap:48px;padding:48px 0 80px}}
.hp-articles{{display:flex;flex-direction:column;gap:0}}

/* ── FLAT EDITORIAL CARDS (article list items) ────────────────────────────── */
.card{{padding:24px 0;border-bottom:1px solid var(--border);display:flex;flex-direction:column}}
.card-cat{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:8px;text-decoration:none;display:inline-block}}
a.card-cat:hover{{color:var(--amber-light);text-decoration:none}}
.card-title{{font-family:var(--sans);font-size:1.1rem;font-weight:700;line-height:1.35;margin-bottom:8px}}
.card-title a{{color:var(--text);transition:color .15s}}
.card-title a:hover{{color:var(--amber);text-decoration:none}}
.card-excerpt{{font-size:.9rem;color:var(--text2);line-height:1.55;margin-bottom:12px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.card-meta{{font-size:12px;color:var(--text3);display:flex;align-items:center;gap:6px;flex-wrap:wrap}}
.meta-sep{{color:var(--text3)}}
.podcast-badge{{display:inline-flex;align-items:center;gap:4px;background:var(--amber-dim);color:var(--amber);font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:auto}}

/* ── HOMEPAGE SIDEBAR ─────────────────────────────────────────────────────── */
.hp-sidebar{{position:sticky;top:72px;align-self:start}}
.sidebar-section{{margin-bottom:36px}}
.sidebar-section .section-label{{font-size:11px;margin-bottom:12px;padding-bottom:8px}}
.sidebar-trending{{display:flex;flex-direction:column;gap:0}}
.trending-item{{padding:12px 0;border-bottom:1px solid var(--border);display:flex;gap:10px;align-items:flex-start}}
.trending-item:last-child{{border-bottom:none}}
.trending-num{{font-family:var(--sans);font-size:1.3rem;font-weight:800;color:rgba(245,158,11,.3);line-height:1;min-width:24px}}
.trending-title{{font-size:.85rem;font-weight:600;line-height:1.35}}
.trending-title a{{color:var(--text2);transition:color .15s}}
.trending-title a:hover{{color:var(--text);text-decoration:none}}
.sidebar-podcast{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px;margin-bottom:24px}}
.sidebar-podcast p{{font-size:.85rem;color:var(--text2);margin-bottom:12px;line-height:1.5}}
.btn-spotify{{display:inline-flex;align-items:center;gap:6px;background:#1DB954;color:#000;font-size:.8rem;font-weight:700;padding:8px 16px;border-radius:6px;transition:opacity .15s}}
.btn-spotify:hover{{opacity:.88;text-decoration:none}}
.sidebar-cta{{background:var(--surface);border:1px solid var(--amber-border);border-radius:8px;padding:20px;text-align:center}}
.sidebar-cta .s-headline{{font-size:.9rem;font-weight:700;color:var(--text);margin-bottom:6px}}
.sidebar-cta .s-sub{{font-size:.8rem;color:var(--text2);margin-bottom:14px;line-height:1.5}}
.sidebar-cta .s-fine{{font-size:.7rem;color:var(--text3);margin-top:10px}}
.sidebar-cat-link{{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border);font-size:.85rem;color:var(--text2);transition:color .15s}}
.sidebar-cat-link:last-child{{border-bottom:none}}
.sidebar-cat-link:hover{{color:var(--text);text-decoration:none}}
.sidebar-cat-count{{font-size:.75rem;color:var(--text3);background:rgba(255,255,255,.04);padding:2px 8px;border-radius:12px}}

/* ── Cards grid (for category pages) ──────────────────────────────────────── */
.cards-grid{{display:flex;flex-direction:column;gap:0}}

/* ── HOMEPAGE brand-hub (hero guide-card -> money page, 6 topic clusters) ── */
.hh{{padding:88px 0 64px;text-align:center;background:radial-gradient(820px 420px at 50% -12%,rgba(245,158,11,.13),transparent 64%)}}
.hh h1{{font-family:var(--sans);font-size:clamp(2.4rem,5.4vw,4.2rem);font-weight:800;line-height:1.04;letter-spacing:-1.6px;color:var(--text);margin:0 auto;max-width:900px}}
.hh h1 em{{font-style:normal;color:var(--amber)}}
.hh .sub{{font-size:1.22rem;color:var(--text2);max-width:640px;margin:22px auto 0;line-height:1.55}}
.hh .sub b{{color:var(--text);font-weight:600}}
.guidecard{{display:flex;align-items:center;gap:18px;margin:34px auto 0;max-width:720px;background:linear-gradient(180deg,var(--surface),#0c0f16);border:1px solid var(--amber-border);border-radius:12px;padding:20px 24px;text-align:left;transition:transform .12s,border-color .15s}}
.guidecard:hover{{border-color:var(--amber);transform:translateY(-1px);text-decoration:none}}
.gc-ic{{flex:0 0 46px;height:46px;border-radius:11px;background:var(--amber-dim);display:flex;align-items:center;justify-content:center;color:var(--amber);font-size:22px;font-weight:800}}
.gc-k{{font-size:.72rem;text-transform:uppercase;letter-spacing:1.2px;color:var(--amber);font-weight:700}}
.gc-t{{color:var(--text);font-weight:800;font-size:1.12rem;margin:2px 0 3px;line-height:1.2}}
.gc-d{{color:var(--text2);font-size:.9rem;line-height:1.4}}
.gc-arrow{{color:var(--amber);font-weight:800;white-space:nowrap;margin-left:auto}}
.hubsec{{padding:8px 0 72px}}
.hubsec .eyebrow{{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:var(--amber);font-weight:700}}
.hubsec h2{{font-family:var(--sans);font-size:clamp(1.7rem,3vw,2.3rem);font-weight:800;letter-spacing:-.7px;margin:8px 0 6px;color:var(--text)}}
.hubsec .lead{{color:var(--text2);font-size:1.08rem;margin:0 0 36px}}
.clusters{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.cluster{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:22px;display:flex;flex-direction:column;transition:border-color .15s}}
.cluster:hover{{border-color:var(--amber)}}
.cluster h3{{font-size:1.08rem;font-weight:800;color:var(--text);margin:0 0 6px}}
.cluster p{{font-size:.92rem;color:var(--text2);margin:0 0 16px;flex:1;line-height:1.5}}
.cluster .cl{{color:var(--amber);font-weight:700;font-size:.92rem;margin-top:auto}}
.cluster .cl:hover{{text-decoration:none;opacity:.85}}
.es-banner{{margin-top:20px;background:linear-gradient(90deg,var(--amber-dim),transparent);border:1px solid var(--amber-border);border-radius:14px;padding:18px 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
@media(max-width:820px){{.clusters{{grid-template-columns:1fr}}.hh{{padding:54px 0 40px}}}}

/* ── Reading progress bar ─────────────────────────────────────────────────── */
#reading-progress{{position:fixed;top:0;left:0;height:3px;width:0;background:var(--amber);z-index:9999;transition:width .1s linear}}

/* ── POST PAGE — single clean column (Caleb: no side-rail; in-content links only) ── */
.post-container{{max-width:var(--content);margin:0 auto;padding:96px 24px 56px}}

/* Breadcrumb */
.post-breadcrumb{{font-size:.8rem;color:var(--text3);margin-bottom:24px}}
.post-breadcrumb a{{color:var(--text2);transition:color .15s}}
.post-breadcrumb a:hover{{color:var(--text);text-decoration:none}}
.post-breadcrumb .bc-sep{{margin:0 8px;color:var(--text3);opacity:.5}}

/* Post header */
.post-eyebrow{{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:12px}}
.post-title{{font-family:var(--sans);font-size:clamp(2rem,4vw,3.5rem);font-weight:800;line-height:1.15;color:var(--text);letter-spacing:-.5px;margin-bottom:20px}}
.post-byline{{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--text3);padding-bottom:16px;border-bottom:1px solid var(--border);margin-bottom:8px;flex-wrap:wrap}}
.post-byline .sep{{color:var(--text3);opacity:.4}}

/* Share row */
.share-row{{display:flex;align-items:center;gap:12px;padding:18px 0 0;border-top:1px solid var(--border);margin:24px 0 36px;font-size:13px;color:var(--text3);opacity:.8}}
.share-btn{{display:inline-flex;align-items:center;gap:5px;min-height:36px;padding:7px 13px;border:1px solid var(--border);border-radius:8px;font-size:12px;font-weight:600;color:var(--text2);background:transparent;cursor:pointer;transition:border-color .15s,color .15s}}
.share-btn:hover{{border-color:var(--amber);color:var(--text);text-decoration:none}}

/* CTA — below byline (compact one-liner) */
.cta-byline{{font-size:.9rem;color:var(--text2);margin:0 0 32px;padding:12px 0}}
.cta-byline a{{color:var(--amber);font-weight:600}}
.cta-byline a:hover{{color:var(--amber-light)}}

/* CTA — mid-article inline */
.cta-inline{{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:14px 18px;margin:28px 0;font-size:.9rem;color:var(--text2);display:block}}
.cta-inline a{{color:var(--amber);font-weight:600;text-decoration:none}}
.cta-inline a:hover{{color:var(--amber-light)}}

/* CTA — end of article box */
.cta-end{{background:var(--surface);border:1px solid var(--amber-border);border-radius:8px;padding:32px;text-align:center;margin:48px 0}}
.cta-end h3{{font-family:var(--sans);font-size:1.25rem;font-weight:800;color:var(--text);margin-bottom:10px}}
.cta-end p{{font-size:.9rem;color:var(--text2);margin:0 0 20px;max-width:440px;margin-left:auto;margin-right:auto}}
.cta-end .fine{{font-size:.75rem;color:var(--text3);margin-top:12px}}
.btn-amber{{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--amber);color:#000;font-size:.85rem;font-weight:700;padding:11px 22px;border-radius:8px;min-height:42px;transition:all .2s;text-decoration:none}}

/* ── Bootcamp section — subtle framed panel (it's a real perk, give it weight) ── */
.bootcamp-section{{margin:52px 0;padding:26px 28px;background:rgba(255,255,255,.035);border:1px solid var(--amber-border);border-radius:8px}}
.bootcamp-section h2{{margin-top:0}}
.bootcamp-section h3{{margin-top:24px}}
.bootcamp-section ul{{margin-bottom:0}}
.bootcamp-section li::marker{{color:var(--amber)}}
.btn-amber:hover{{background:var(--amber-light);transform:translateY(-1px);text-decoration:none}}

/* ── TL;DR answer box (answer-first, above the article — no scrolling to find the point) ── */
.tldr{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:22px 26px;margin:0 0 32px}}
.tldr-label{{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:var(--amber);margin-bottom:8px}}
.tldr p{{font-size:1.02rem;line-height:1.6;color:var(--text2);margin:0 0 10px}}
.tldr p:last-child{{margin-bottom:0}}
.tldr strong{{color:var(--text);font-weight:700}}
.tldr a:not(.btn-amber){{color:var(--amber);font-weight:600}}
.tldr-cta{{margin-top:18px;font-size:.92rem;padding:12px 24px;color:#000}}

/* Post body typography */
.post-body{{font-size:19px;line-height:1.75;color:#e5e7eb}}
.post-body h2{{font-family:var(--sans);font-size:1.75rem;line-height:1.3;font-weight:800;color:var(--text);margin:56px 0 16px}}
.post-body h3{{font-size:1.3rem;line-height:1.35;font-weight:700;color:#f3f4f6;margin:36px 0 10px}}
.post-body p{{margin-bottom:20px}}
.post-body ul,.post-body ol{{margin:0 0 20px 24px}}
.post-body li{{margin-bottom:8px}}
.post-body strong{{color:#fff}}
.post-body a{{color:var(--amber);text-decoration:underline;text-underline-offset:3px}}
.post-body a:hover{{color:var(--amber-light)}}

/* ── LIGHT-MODE INLINE STYLE OVERRIDES ────────────────────────────────────── */
.post-body a[style*="color:#1a73e8"],
.post-body a[style*="color: #1a73e8"]{{
  color:var(--amber)!important;
}}
.post-body a[style*="color:#1a73e8"]:hover,
.post-body a[style*="color: #1a73e8"]:hover{{
  color:var(--amber-light)!important;
}}
.post-body div[style*="background:#f0f4ff"],
.post-body div[style*="background: #f0f4ff"]{{
  background:var(--surface)!important;
  border-color:var(--amber-border)!important;
}}
.post-body div[style*="background:#f8f9fa"],
.post-body div[style*="background: #f8f9fa"]{{
  background:var(--surface)!important;
  border-color:var(--border)!important;
}}
.post-body div[style*="background:#fff8e1"],
.post-body div[style*="background: #fff8e1"]{{
  background:rgba(245,158,11,.06)!important;
  border-color:var(--amber-border)!important;
}}
.post-body div[style*="background:#fff"],
.post-body div[style*="background: #fff"],
.post-body div[style*="background:#ffffff"],
.post-body div[style*="background: #ffffff"]{{
  background:var(--surface)!important;
}}
.post-body div[style*="background:#1a73e8"],
.post-body div[style*="background: #1a73e8"]{{
  background:var(--surface)!important;
  border:1px solid var(--amber-border)!important;
}}
.post-body div[style*="background:#1a73e8"] *,
.post-body div[style*="background: #1a73e8"] *{{
  color:var(--text)!important;
}}
.post-body div[style*="background:#1a73e8"] a,
.post-body div[style*="background: #1a73e8"] a{{
  background:var(--amber)!important;
  color:#000!important;
  border-radius:6px;
  padding:12px 24px;
}}
.post-body a[style*="background:#ffffff"],
.post-body a[style*="background: #ffffff"],
.post-body a[style*="background:#fff"],
.post-body a[style*="background: #fff"]{{
  background:var(--amber)!important;
  color:#000!important;
}}
.post-body div[style*="border-left:4px solid #1a73e8"],
.post-body div[style*="border-left: 4px solid #1a73e8"]{{
  border-left-color:var(--amber)!important;
}}
.post-body div[style*="border:2px solid #1a73e8"],
.post-body div[style*="border: 2px solid #1a73e8"]{{
  border-color:var(--amber-border)!important;
}}
.post-body div[style*="border-left:4px solid #ffc107"]{{
  border-left-color:var(--amber)!important;
}}
.post-body div[style*="background:#f8f9fa"] h3,
.post-body div[style*="background: #f8f9fa"] h3{{
  color:var(--amber)!important;
  margin-top:0;
}}
.post-body div[style*="background:#f8f9fa"] h3[style*="color:#1a73e8"],
.post-body div[style*="background: #f8f9fa"] h3[style*="color:#1a73e8"]{{
  color:var(--amber)!important;
}}
.post-body div[style*="background:#f8f9fa"] p,
.post-body div[style*="background: #f8f9fa"] p{{
  color:var(--text2)!important;
}}
.post-body div[style*="background:#f8f9fa"] strong,
.post-body div[style*="background: #f8f9fa"] strong{{
  color:var(--text)!important;
}}
.post-body h2[style*="color:#1a73e8"],
.post-body h3[style*="color:#1a73e8"],
.post-body h4[style*="color:#1a73e8"]{{
  color:var(--amber)!important;
}}
.post-body p[style*="color:#1a73e8"],
.post-body span[style*="color:#1a73e8"],
.post-body p[style*="color:#333"],
.post-body span[style*="color:#333"],
.post-body p[style*="color:#000"],
.post-body span[style*="color:#000"]{{
  color:var(--text2)!important;
}}
.post-body a[style*="background:#1a73e8"],
.post-body a[style*="background: #1a73e8"]{{
  background:var(--amber)!important;
  color:#000!important;
}}
.post-body p[style*="background:#f0fdf4"],
.post-body p[style*="background: #f0fdf4"]{{
  background:var(--surface)!important;
  border-color:var(--amber-border)!important;
  color:var(--text)!important;
}}
.post-body p[style*="background:#f0fdf4"] a,
.post-body p[style*="background: #f0fdf4"] a{{
  color:var(--amber)!important;
}}
.post-body div[style*="border-radius"]{{
  color:var(--text2);
}}

/* TOC */
.toc{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px 24px;margin:0 0 32px}}
.toc-label{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--text3);margin-bottom:12px}}
.toc ol{{margin:0;padding-left:18px}}
.toc li{{font-size:.9rem;line-height:1.9}}
.toc a{{color:var(--text2);text-decoration:none}}
.toc a:hover{{color:var(--amber);text-decoration:none}}

/* Podcast embed */
.podcast-embed{{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--amber);border-radius:8px;padding:20px;margin:36px 0}}
.podcast-embed p{{font-size:.8rem;font-weight:600;color:var(--text2);margin-bottom:12px}}
.podcast-embed iframe{{border-radius:6px}}
.podcast-link{{display:inline-flex;align-items:center;gap:8px;color:var(--amber);font-size:.875rem;font-weight:600;text-decoration:none;margin-top:8px}}
.podcast-link:hover{{color:var(--amber-light);text-decoration:none}}

/* Author box */
.author-box{{display:flex;gap:16px;align-items:flex-start;padding:24px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border);margin:40px 0}}
.author-box .author-name{{font-weight:700;color:var(--accent);font-size:.95rem;margin-bottom:2px;text-decoration:none}}
.author-box .author-name:hover{{text-decoration:underline}}
.author-box .author-role{{font-size:.8rem;color:var(--text2);margin-bottom:6px;font-weight:500}}
.author-box .author-bio{{font-size:.825rem;color:var(--text2);line-height:1.6}}
.author-box .author-bio a{{color:var(--accent);text-decoration:none}}
.author-box .author-bio a:hover{{text-decoration:underline}}

/* Related posts */
.related-posts{{margin:48px 0 0}}
.related-label{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--text3);margin-bottom:18px}}
.related-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.related-card{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px;display:block;transition:border-color .2s}}
.related-card:hover{{border-color:var(--amber)}}
.related-card .r-tag{{display:block;font-size:11px;font-weight:700;color:var(--amber);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}}
.related-card .r-title{{display:-webkit-box;font-size:.85rem;font-weight:600;color:#e5e7eb;line-height:1.4;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;text-decoration:none}}
.related-card:hover .r-title{{color:#fff;text-decoration:none}}
.hub-link{{margin:36px 0 0;padding-top:20px;border-top:1px solid var(--border);font-size:.95rem;color:var(--text2)}}
.hub-link a{{color:var(--amber);font-weight:600}}

/* Pagination */
.pagination{{display:flex;gap:8px;justify-content:center;margin-top:48px;flex-wrap:wrap}}
.page-btn{{padding:8px 16px;border:1px solid var(--border);border-radius:6px;font-size:.875rem;color:var(--text2);background:var(--surface)}}
.page-btn.active{{background:var(--amber);color:#07080a;border-color:var(--amber);font-weight:700}}
.page-btn:hover{{border-color:var(--amber);color:var(--text);text-decoration:none}}

/* Category header */
.cat-header{{background:var(--bg2);border-bottom:1px solid var(--border);padding:100px 24px 40px}}
.cat-header h1{{font-family:var(--sans);font-size:1.8rem;font-weight:800;margin-bottom:8px;color:var(--text)}}
.cat-header p{{color:var(--text2);font-size:.9rem}}

/* Footer */
footer{{border-top:1px solid var(--border);padding:56px 24px 36px;margin-top:80px}}
.footer-inner{{max-width:var(--max);margin:0 auto}}
.footer-top{{display:grid;grid-template-columns:2fr 1fr 1fr;gap:48px;margin-bottom:48px}}
.footer-logo{{font-family:var(--sans);font-size:1.1rem;font-weight:800;margin-bottom:12px;color:var(--text)}}
.footer-logo span{{color:var(--amber)}}
.footer-desc{{font-size:.82rem;color:var(--text3);line-height:1.7;margin-bottom:14px}}
.footer-disclaimer{{font-size:.74rem;color:var(--text3);line-height:1.6;opacity:.7}}
.footer-col h4{{font-size:.76rem;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--text2);margin-bottom:16px}}
.footer-col a{{display:block;font-size:.85rem;color:var(--text2);margin-bottom:10px;transition:color .15s}}
.footer-col a:hover{{color:var(--text);text-decoration:none}}
.footer-bottom{{border-top:1px solid var(--border);padding-top:24px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;font-size:.76rem;color:var(--text3)}}

/* ── RESPONSIVE ───────────────────────────────────────────────────────────── */
@media(max-width:1024px){{
  .hp-featured{{grid-template-columns:1fr}}
  .hp-body{{grid-template-columns:1fr}}
  .hp-sidebar{{position:static;display:grid;grid-template-columns:1fr 1fr;gap:24px}}
  .related-grid{{grid-template-columns:repeat(2,1fr)}}
}}
@media(max-width:640px){{
  .hp-sidebar{{grid-template-columns:1fr}}
  .nav-links{{display:none}}
  .hamburger{{display:flex}}
  .post-title{{font-size:1.8rem}}
  .hp-lead-title{{font-size:1.8rem}}
  .cta-end{{padding:24px 20px}}
  .related-grid{{grid-template-columns:1fr}}
  .cat-header{{padding:90px 20px 36px}}
  .footer-top{{grid-template-columns:1fr;gap:32px}}
  .footer-bottom{{flex-direction:column}}
  .share-row{{flex-wrap:wrap}}
  .trial-grid{{grid-template-columns:1fr!important}}
  .coupon-compare{{grid-template-columns:1fr!important}}
  .coupon-features{{grid-template-columns:1fr!important}}
  .services-grid{{grid-template-columns:1fr!important}}
  .services-steps{{grid-template-columns:1fr!important}}
  .services-pricing{{grid-template-columns:1fr!important}}
  .form-row{{grid-template-columns:1fr!important}}
}}
.chip{{display:inline-block;padding:6px 14px;border-radius:20px;font-size:.8rem;color:var(--text2);border:1px solid var(--surface);text-decoration:none;transition:all .2s}}
.chip:hover{{border-color:var(--amber);color:var(--amber)}}
.chip-active{{background:var(--amber);color:var(--bg);border-color:var(--amber);font-weight:600}}
.chip-active:hover{{color:var(--bg)}}
"""

# ── Base template ─────────────────────────────────────────────────────────────

def _ga_snippet() -> str:
    """Return GA4 + conversion tracking script, or empty string if no GA_ID."""
    if not GA_ID:
        return ""
    return (
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
        f"<script>\n"
        f"window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}\n"
        f'gtag("js",new Date());gtag("config","{GA_ID}");\n'
        f'document.addEventListener("click",function(e){{\n'
        f'  var a=e.target.closest("a[href]");\n'
        f'  if(!a)return;\n'
        f'  var h=a.href||"";\n'
        f'  var isAffiliate=h.indexOf("fp_ref=")>-1;\n'
        f'  var isTrial=h.indexOf("/trial")>-1||h.indexOf("/start")>-1||h.indexOf("/free-trial")>-1||a.classList.contains("nav-cta")||a.classList.contains("btn-amber");\n'
        f'  var isGHL=h.indexOf("gohighlevel.com")>-1;\n'
        f'  if(isAffiliate){{\n'
        f'    gtag("event","ghl_click",{{\n'
        f"      link_url:h,\n"
        f"      link_text:a.textContent.trim().slice(0,50),\n"
        f"      page_path:location.pathname,\n"
        f'      page_lang:document.documentElement.lang||"en"\n'
        f"    }});\n"
        f"  }}else if(isTrial||isGHL){{\n"
        f'    gtag("event","cta_click",{{\n'
        f"      link_url:h,\n"
        f"      link_text:a.textContent.trim().slice(0,50),\n"
        f"      page_path:location.pathname,\n"
        f'      page_lang:document.documentElement.lang||"en"\n'
        f"    }});\n"
        f"  }}\n"
        f"}});\n"
        f"</script>"
    )


def _clarity_snippet() -> str:
    if not CLARITY_ID:
        return ""
    return (
        f"<script>\n"
        f"(function(c,l,a,r,i,t,y){{\n"
        f"  c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};\n"
        f"  t=l.createElement(r);t.async=1;t.src=\"https://www.clarity.ms/tag/\"+i;\n"
        f"  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);\n"
        f'}})(window, document, "clarity", "script", "{CLARITY_ID}");\n'
        f"</script>"
    )


def _build_hreflang_tags(page_path: str = "") -> str:
    """Build hreflang link tags for a page. page_path is relative (e.g., '/category/ai-automation/').

    Only emits an alternate for a language whose version of this page was actually
    built (tracked in BUILT_PAGE_PATHS). Post-prune many language/category pages
    don't exist; advertising them via hreflang pointed Google at 404s.
    """
    tags = []
    for lang in LANGUAGES:
        prefix = lang.get("prefix", "")
        rel = f'{prefix}{page_path}' if page_path else f'{prefix}/'
        if rel not in BUILT_PAGE_PATHS:
            continue
        tags.append(f'<link rel="alternate" hreflang="{lang["code"]}" href="{SITE_URL}{rel}">')
    default_rel = page_path or "/"
    if default_rel in BUILT_PAGE_PATHS:
        tags.append(f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{default_rel}">')
    return "\n".join(tags)


def _build_post_hreflang_tags(translations: dict) -> str:
    """Build hreflang tags for a blog post from an explicit slug-per-language map.

    translations: {"en": "en-slug", "es": "es-slug", "en-IN": "in-slug", "ar": "ar-slug"}
    Emits <link rel="alternate" hreflang="{code}" href="/blog/{slug}/"> for each,
    plus x-default pointing at the English variant (or first entry if no English).
    """
    if not translations or not isinstance(translations, dict):
        return ""
    tags = []
    for code, slug in translations.items():
        if not slug or slug not in LIVE_POST_SLUGS:
            continue  # sibling-language post was pruned; don't advertise a 404
        tags.append(f'<link rel="alternate" hreflang="{code}" href="{SITE_URL}/blog/{slug}/">')
    default_slug = translations.get("en") if translations.get("en") in LIVE_POST_SLUGS else ""
    if not default_slug:
        default_slug = next((s for s in translations.values() if s in LIVE_POST_SLUGS), "")
    if default_slug:
        tags.append(f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/blog/{default_slug}/">')
    return "\n".join(tags)


LANG_META_VIOLATIONS = []

def base_html(title: str, description: str, canonical: str, body: str, og_image: str = "", lang: str = "en", text_dir: str = "ltr", hreflang_path: str = "", hreflang_override: str = "", noindex: bool = False, disable_hreflang_fallback: bool = False) -> str:
    ok, msg = validate_meta(canonical, title, description)
    if not ok:
        LANG_META_VIOLATIONS.append(msg)
    og_img = og_image or os.getenv("OG_IMAGE_URL", f"{SITE_URL}/images/og-default.png")
    cats = CATEGORIES
    aff = affiliate_for(lang)

    # Determine current language for language picker
    current_lang = next((l for l in LANGUAGES if l["code"] == lang), None)
    current_lang_native = current_lang["native"] if current_lang else "English"

    # Nav dropdown links (topics only — no languages mixed in)
    dropdown_links = ""
    for c in cats:
        if c["slug"] not in LIVE_CATEGORY_SLUGS:
            continue
        dropdown_links += f'    <a href="/category/{c["slug"]}/">{c["name"]}</a>\n'

    # Language picker dropdown
    lang_links = ""
    for l in LANGUAGES:
        if l["code"] not in LIVE_LANG_CODES:
            continue  # skip languages with no built hub (e.g. /ar/ post-prune)
        active = ' style="color:var(--amber);font-weight:700"' if l["code"] == lang else ""
        href = l["prefix"] + "/" if l["prefix"] else "/"
        lang_links += f'    <a href="{href}"{active}>{l["native"]}</a>\n'

    # Mobile language row
    mobile_lang_links = ""
    for l in LANGUAGES:
        if l["code"] == lang or l["code"] not in LIVE_LANG_CODES:
            continue
        href = l["prefix"] + "/" if l["prefix"] else "/"
        mobile_lang_links += f'<a href="{href}" style="display:inline-block;margin-right:16px;font-size:.9rem">{l["native"]}</a>'

    # Footer Topics = the 6 homepage clusters (links-safe to existing pages until hubs build)
    _footer_clusters = [
        ("AI Receptionist &amp; Lead Capture", "/category/agency-platform/"),
        ("AI Agents &amp; Automation", "/blog/gohighlevel-ai-agents-automation-complete-guide/"),
        ("CRM &amp; Communication", "/category/crm-communication/"),
        ("Sites, Funnels &amp; Reputation", "/blog/how-to-launch-a-website-in-gohighlevel-pro-templates/"),
        ("Agency, White-Label &amp; SaaS", "/category/agency-platform/"),
        ("Payments &amp; Pricing", "/blog/gohighlevel-payments-complete-guide/"),
    ]
    footer_cat_links = "".join(f'        <a href="{u}">{n}</a>\n' for n, u in _footer_clusters)

    # Footer language links
    footer_lang_links = ""
    for l in LANGUAGES:
        if l["code"] not in LIVE_LANG_CODES:
            continue  # skip languages with no built hub (e.g. /ar/ post-prune)
        href = l["prefix"] + "/" if l["prefix"] else "/"
        footer_lang_links += f'        <a href="{href}">{l["native"]}</a>\n'

    # hreflang tags — override wins (per-post translations map), then optional prefix fallback.
    # disable_hreflang_fallback=True is used for blog posts: if a post has no real
    # translations dict, emit NO hreflang. The old fallback declared every page as a
    # translation of /es/ /in/ /ar/ language hubs — false claim that hurt the cluster.
    # Hubs and category pages still use the fallback (their hreflangs ARE valid).
    if hreflang_override:
        hreflang_html = hreflang_override
    elif disable_hreflang_fallback:
        hreflang_html = ""
    elif LANGUAGES:
        hreflang_html = _build_hreflang_tags(hreflang_path)
    else:
        hreflang_html = ""

    # RTL style override
    rtl_attr = ' dir="rtl"' if text_dir == "rtl" else ""

    return f"""<!DOCTYPE html>
<html lang="{lang}"{rtl_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{'<meta name="robots" content="noindex, follow">' if noindex else ''}
<link rel="canonical" href="{canonical}">
{hreflang_html}
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"WebSite","name":"{SITE_NAME}","url":"{SITE_URL}"}}
</script>
<style>{CSS}
{"html[dir=rtl] .nav-links{flex-direction:row-reverse}html[dir=rtl] .nav-dropdown-menu{left:auto;right:-12px}html[dir=rtl] .cards-grid{direction:rtl}html[dir=rtl] .post-body{direction:rtl;text-align:right}html[dir=rtl] .sidebar-section{direction:rtl}html[dir=rtl] .footer-inner{direction:rtl}" if text_dir == "rtl" else ""}
</style>
{_ga_snippet()}
{_clarity_snippet()}
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/" class="logo">Global<span class="logo-amber">HighLevel</span></a>
    <div class="nav-links">
      <a href="{'/es/#guides' if lang == 'es' else '/#guides'}" class="nav-link">{'Guías' if lang == 'es' else 'Guides'}</a>
      <a href="https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV" class="nav-link" target="_blank" rel="noopener">Podcast</a>
      <a href="{'/' if lang == 'es' else '/es/'}" class="nav-link">{'English' if lang == 'es' else 'Español'}</a>
      <a href="{aff}" class="nav-cta" target="_blank" rel="nofollow noopener">{'Prueba 30 días gratis' if lang == 'es' else 'Start 30 Days Free'}</a>
    </div>
    <input type="checkbox" id="mobile-toggle">
    <label for="mobile-toggle" class="hamburger" aria-label="Menu">
      <span></span><span></span><span></span>
    </label>
    <div class="mobile-menu">
      <a href="{'/es/#guides' if lang == 'es' else '/#guides'}">{'Guías' if lang == 'es' else 'Guides'}</a>
      <a href="https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV" target="_blank" rel="noopener">Podcast</a>
      <a href="{'/' if lang == 'es' else '/es/'}">{'English' if lang == 'es' else 'Español'}</a>
      <a href="{aff}" class="nav-cta" target="_blank" rel="nofollow noopener">{'Prueba 30 días gratis' if lang == 'es' else 'Start 30 Days Free'}</a>
    </div>
  </div>
</nav>
{body}
<footer>
  <div class="footer-inner">
    <div class="footer-top">
      <div>
        <div class="footer-logo">Global<span>HighLevel</span></div>
        <p class="footer-desc">Free GoHighLevel tutorials, guides, and strategies for digital marketing agencies and businesses worldwide.</p>
        <p class="footer-disclaimer">Affiliate disclosure: Some links on this site are affiliate links. If you sign up through our link, we may earn a commission at no extra cost to you. Not affiliated with GoHighLevel LLC.</p>
      </div>
      <div class="footer-col">
        <h4>Topics</h4>
{footer_cat_links}      </div>
      <div class="footer-col">
        <h4>Languages</h4>
{footer_lang_links}      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {datetime.now().year} GlobalHighLevel.com</span>
      <span>Not affiliated with GoHighLevel LLC</span>
    </div>
  </div>
</footer>
</body>
</html>"""

# ── Load data ─────────────────────────────────────────────────────────────────

def load_posts() -> list[dict]:
    """Load all post JSON files from posts/ directory."""
    posts = []
    if not POSTS_DIR.exists():
        return posts
    for f in sorted(POSTS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            if data.get("slug") and data.get("html_content"):
                posts.append(data)
        except Exception:
            pass
    return posts

def load_published() -> list[dict]:
    """Load published.json for episode metadata."""
    if not PUBLISHED_JSON.exists():
        return []
    try:
        return json.loads(PUBLISHED_JSON.read_text())
    except Exception:
        return []

def merge_data(posts: list[dict], published: list[dict]) -> list[dict]:
    """Merge blog post data with episode metadata."""
    ep_by_id = {str(p.get("articleId", p.get("id", ""))): p for p in published}
    merged = []
    for post in posts:
        article_id = str(post.get("articleId", ""))
        ep = ep_by_id.get(article_id, {})
        merged.append({**ep, **post})
    # Sort newest first
    merged.sort(key=lambda x: x.get("publishedAt", x.get("uploadedAt", "")), reverse=True)
    return merged

# ── Page generators ───────────────────────────────────────────────────────────

# 9-part series outline per vertical (ES). Used by authority template to show
# all parts in the sidebar/footer — future parts rendered as "próximamente".
SERIES_PARTS_ES = {
    "agencias-de-marketing": [
        (1, "Por qué las agencias de marketing necesitan un CRM en 2026"),
        (2, "El mejor CRM para agencias de marketing este año"),
        (3, "GoHighLevel vs Clientify para agencias de marketing: comparación honesta"),
        (4, "Cómo configurar GoHighLevel para una agencia de marketing"),
        (5, "Los workflows de GoHighLevel que agencias de marketing usan de verdad"),
        (6, "Precios de GoHighLevel para una agencia: los números reales"),
        (7, "Qué cambia en el mes 1 cuando una agencia de marketing adopta GoHighLevel"),
        (8, "¿Vale la pena GoHighLevel para una agencia de marketing solo?"),
        (9, "Errores comunes que agencias de marketing cometen al configurar GoHighLevel"),
    ],
}


def _authority_css() -> str:
    """Minimal Attia-style CSS. Embedded per-page to avoid template dependencies."""
    return """
<style>
  :root { --ink: #1a1a1a; --ink-soft: #3a3a3a; --link: #1a3a7a; --rule: #e5e5e5; --muted: #6b6b6b; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: #fdfcf9; color: var(--ink); -webkit-font-smoothing: antialiased; }
  body { font-family: Georgia, "Merriweather", "Times New Roman", serif; font-size: 19px; line-height: 1.75; }
  .auth-header { border-bottom: 1px solid var(--rule); background: #fff; padding: 14px 24px; }
  .auth-header-inner { max-width: 1100px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif; font-size: 14px; }
  .auth-header a { color: var(--ink); text-decoration: none; font-weight: 600; letter-spacing: -0.01em; }
  .auth-header a:hover { color: var(--link); }
  .auth-header nav a { margin-left: 24px; font-weight: 400; color: var(--muted); }
  .auth-main { max-width: 760px; margin: 0 auto; padding: 56px 32px 80px; }
  @media (min-width: 900px) { .auth-main { padding: 64px 0 96px; } }
  .auth-series-label { font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 8px; }
  .auth-series-label a { color: var(--muted); text-decoration: none; border-bottom: 1px dotted var(--muted); }
  .auth-series-label a:hover { color: var(--link); border-bottom-color: var(--link); }
  h1.auth-title { font-size: 38px; line-height: 1.22; margin: 8px 0 20px; font-weight: 700; letter-spacing: -0.01em; }
  .auth-byline { color: var(--muted); font-size: 14px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin-bottom: 40px; padding-bottom: 24px; border-bottom: 1px solid var(--rule); }
  .auth-body { font-size: 19px; }
  .auth-body h2 { font-size: 28px; line-height: 1.3; margin: 56px 0 16px; font-weight: 700; letter-spacing: -0.005em; }
  .auth-body h3 { font-size: 21px; line-height: 1.4; margin: 36px 0 12px; font-weight: 700; }
  .auth-body p { margin: 0 0 20px; color: var(--ink); }
  .auth-body ul, .auth-body ol { margin: 0 0 24px; padding-left: 24px; }
  .auth-body ul li, .auth-body ol li { padding-left: 4px; }
  .auth-body li { margin-bottom: 8px; }
  .auth-body a { color: var(--link); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 2px; }
  .auth-body a:hover { text-decoration-thickness: 2px; }
  .auth-body strong { font-weight: 700; color: var(--ink); }
  .auth-body em { font-style: italic; }
  .auth-body blockquote { margin: 24px 0; padding: 0 0 0 20px; border-left: 3px solid var(--rule); color: var(--ink-soft); font-style: italic; }
  .auth-body hr { border: none; border-top: 1px solid var(--rule); margin: 48px 0; }
  /* Strip the writer's inline CTA banners — we render clean prose only */
  .auth-body p[style*="background:#111520"], .auth-body p[style*="background:#fefbf0"], .auth-body p[style*="background:#f5f5f0"] { background: transparent !important; border: none !important; border-left: 3px solid var(--rule) !important; padding: 16px 0 16px 20px !important; color: var(--ink-soft) !important; border-radius: 0 !important; font-style: italic; }
  .auth-body p[style*="background:#111520"] a, .auth-body p[style*="background:#fefbf0"] a, .auth-body p[style*="background:#f5f5f0"] a { color: var(--link) !important; font-weight: 500 !important; }
  .auth-series-nav { margin: 80px 0 40px; padding: 32px 0; border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }
  .auth-series-nav h3 { font-size: 14px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 600; margin: 0 0 18px; }
  .auth-series-nav ol { list-style: none; padding: 0; margin: 0; counter-reset: series; }
  .auth-series-nav li { counter-increment: series; padding: 10px 0; border-bottom: 1px dotted var(--rule); font-size: 16px; display: flex; align-items: baseline; }
  .auth-series-nav li:last-child { border-bottom: none; }
  .auth-series-nav li::before { content: counter(series); font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 700; color: var(--muted); width: 28px; flex-shrink: 0; }
  .auth-series-nav li.current { font-weight: 600; }
  .auth-series-nav li.current::before { color: var(--link); }
  .auth-series-nav li.pending { color: var(--muted); }
  .auth-series-nav li.pending .pending-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin-left: 8px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
  .auth-series-nav a { color: var(--ink); text-decoration: none; border-bottom: 1px solid transparent; }
  .auth-series-nav a:hover { border-bottom-color: var(--link); color: var(--link); }
  .auth-footer { border-top: 1px solid var(--rule); padding: 32px 24px; margin-top: 40px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 13px; color: var(--muted); }
  .auth-footer-inner { max-width: 1100px; margin: 0 auto; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
  .auth-footer a { color: var(--muted); text-decoration: underline; text-decoration-thickness: 1px; }
  .auth-footer a:hover { color: var(--link); }
  @media (max-width: 640px) {
    body { font-size: 17px; }
    h1.auth-title { font-size: 30px; }
    .auth-body { font-size: 17px; }
    .auth-body h2 { font-size: 24px; }
    .auth-main { padding: 32px 20px 60px; }
  }
</style>
"""


def _series_nav_html(post: dict, all_posts: list) -> str:
    """Render the sibling-parts list for the authority series nav."""
    vertical = post.get("vertical", "")
    if not vertical or vertical not in SERIES_PARTS_ES:
        return ""

    # Map shipped pillars (series_part -> url_path) by scanning all_posts
    shipped = {}
    for p in (all_posts or []):
        if p.get("vertical") == vertical and p.get("series_part"):
            shipped[p["series_part"]] = post_url(p)

    current_part = post.get("series_part", 0)
    is_hub = post.get("is_series_hub", False)

    parts = SERIES_PARTS_ES[vertical]
    items = []
    for n, title in parts:
        is_current = (n == current_part) and not is_hub
        is_shipped = n in shipped
        if is_current:
            items.append(f'<li class="current">{title}</li>')
        elif is_shipped:
            items.append(f'<li><a href="{shipped[n]}">{title}</a></li>')
        else:
            items.append(f'<li class="pending">{title} <span class="pending-label">Próximamente</span></li>')

    return f"""
<nav class="auth-series-nav" aria-label="Partes de la serie">
  <h3>Todas las partes de esta serie</h3>
  <ol>
    {chr(10).join(items)}
  </ol>
</nav>
"""


def build_authority_page(post: dict, all_posts: list = None):
    """Minimal Attia-style authority template for series hub + pillar pages.

    No nav dropdown, no amber CTAs, no reading-progress bar, no related-posts grid.
    Just: logo header, series label, title, byline, prose body, series nav, minimal footer.
    """
    slug = post["slug"]
    title = post.get("title", "")
    description = post.get("description", post.get("meta_description", ""))
    html_content = post.get("html_content", "")
    date_str = fmt_date(post.get("publishedAt", ""))
    rtime = read_time(html_content)
    canonical = f"{SITE_URL}{post_url(post)}"

    is_hub = post.get("is_series_hub", False)
    vertical = post.get("vertical", "")
    series_part = post.get("series_part", 0)

    # Sanitize + inject internal links (same as blog template)
    html_content = sanitize_content(html_content)
    if all_posts:
        html_content = inject_internal_links(html_content, post, all_posts, max_links=4)

    # Series label: for hub it's "Serie" + vertical name; for pillar it's "Parte N de 9 · [Hub Title]"
    hub_url_for_label = post.get("hub_url") or f"/es/para/{vertical}/"
    hub_title_for_label = post.get("hub_title", "la serie")
    if is_hub:
        series_label = f'Serie de 9 partes'
    elif series_part:
        series_label = f'Parte {series_part} de 9 · <a href="{hub_url_for_label}">Ver la serie completa</a>'
    else:
        series_label = ""

    series_nav = _series_nav_html(post, all_posts or [])

    # Schema (simplified — Article + BreadcrumbList)
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "author": {"@type": "Person", "name": "William Welch"},
        "datePublished": post.get("publishedAt", ""),
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "url": canonical,
        "publisher": {"@type": "Organization", "name": SITE_NAME},
    }
    if not is_hub and vertical:
        schema["isPartOf"] = {"@type": "Series", "url": f"{SITE_URL}/es/para/{vertical}/"}

    html = f"""<!DOCTYPE html>
<html lang="es" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {SITE_NAME}</title>
<meta name="description" content="{truncate(description, 160)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{truncate(description, 160)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<meta name="robots" content="index, follow, max-image-preview:large">
{_authority_css()}
{_clarity_snippet()}
</head>
<body>
<header class="auth-header">
  <div class="auth-header-inner">
    <a href="/">GlobalHighLevel</a>
    <nav>
      <a href="/es/">Blog</a>
      <a href="{hub_url_for_label}">La serie</a>
    </nav>
  </div>
</header>

<main class="auth-main">
  {f'<div class="auth-series-label">{series_label}</div>' if series_label else ''}
  <h1 class="auth-title">{title}</h1>
  <div class="auth-byline">Por William Welch{' · ' + date_str if date_str else ''} · {rtime}</div>
  <article class="auth-body">
    {html_content}
  </article>
  {series_nav}
</main>

<footer class="auth-footer">
  <div class="auth-footer-inner">
    <span>© 2026 GlobalHighLevel. Este sitio participa en el programa de afiliados de GoHighLevel.</span>
    <span><a href="/about/">Acerca</a> · <a href="/">Home</a></span>
  </div>
</footer>

<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
{faq_schema(html_content)}
</body>
</html>"""

    write(PUBLIC_DIR / post_output_rel(post) / "index.html", html)


def faq_schema(html_content: str) -> str:
    """Build FAQPage JSON-LD from the post's 'Preguntas frecuentes'/FAQ section only.
    Scopes to the FAQ <h2> so non-FAQ <h3> headings elsewhere aren't captured."""
    if not html_content or "FAQPage" in html_content:
        return ""  # content already embeds FAQ schema — do not add a duplicate
    m = re.search(r'<h2[^>]*>\s*(?:Preguntas\s+frecuentes|Frequently Asked Questions|FAQ)[^<]*</h2>(.*?)(?:<h2[^>]*>|<section class="author-bio"|$)',
                  html_content, re.S | re.I)
    if not m:
        return ""
    sec = m.group(1)
    pairs = re.findall(r'<h3[^>]*>(.*?)</h3>(.*?)(?=<h3[^>]*>|$)', sec, re.S)
    pairs += re.findall(r'<p><strong>([^<]*[?¿][^<]*)</strong>(.*?)</p>', sec, re.S)  # bold-paragraph FAQs (hub)
    entities = []
    for q, a in pairs:
        qt = re.sub(r'<[^>]+>', '', q).strip()
        at = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', a)).strip()
        if ('?' in qt or '¿' in qt) and at:
            entities.append({"@type": "Question", "name": qt,
                             "acceptedAnswer": {"@type": "Answer", "text": at}})
    if not entities:
        return ""
    return ('<script type="application/ld+json">'
            + json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                          "mainEntity": entities}, ensure_ascii=False) + '</script>')


def build_post_page(post: dict, all_posts: list = None):
    slug        = post["slug"]
    title       = post.get("title", post.get("seoTitle", ""))
    description = post.get("description", post.get("seoDescription", post.get("meta_description", "")))
    category    = display_cat(post_topic(post)) or "GoHighLevel Tutorials"
    cat_slug    = slugify(category)
    # Only link the category if its page was actually built. Post-prune some topics
    # are empty (404); a non-English post whose topic has no built EN category page
    # (e.g. a lone Spanish AI-Automation post) shows the label as plain text instead.
    _cat_built  = cat_slug in LIVE_CATEGORY_SLUGS
    cat_bc      = f'<a href="/category/{cat_slug}/">{category}</a>' if _cat_built else f'<span>{category}</span>'
    cat_eyebrow = f'<a href="/category/{cat_slug}/" style="color:var(--amber);text-decoration:none">{category}</a>' if _cat_built else f'<span style="color:var(--amber)">{category}</span>'
    date_str    = fmt_date(post.get("publishedAt", post.get("uploadedAt", "")))
    html_content = post.get("html_content", "")
    aff         = affiliate_for(post.get("language", "en"))
    episode_id  = post.get("transistorEpisodeId", "")
    rtime       = read_time(html_content)
    canonical   = f"{SITE_URL}{post_url(post)}"

    # ── Sanitize content: strip in-content TOC and CTA boxes ──────────────────
    html_content = sanitize_content(html_content)

    # ── Internal links: cross-link to related posts for SEO ──────────────────
    # mvp_minimal_links: money/landing pages concentrate juice — no outbound internal
    # SEO links until a real cluster exists to link to (set on the post JSON).
    _mvp_minimal = post.get("mvp_minimal_links")
    if all_posts and not _mvp_minimal:
        html_content = inject_internal_links(html_content, post, all_posts)
    # P1.2: editorial in-body link up to the category hub (only when the hub is built).
    if _cat_built and not _mvp_minimal:
        html_content += _hub_link_block(category, cat_slug, slug)
    if _mvp_minimal:
        # strip hard-coded internal /blog/ and /category/ anchors (keep the visible text)
        html_content = re.sub(r'<a\b[^>]*\bhref="(?:/blog/|/category/)[^"]*"[^>]*>(.*?)</a>',
                              r'\1', html_content, flags=re.S)

    # ── Podcast section ───────────────────────────────────────────────────────
    if episode_id:
        podcast_html = f"""
<div class="podcast-embed">
  <p>Listen to this episode</p>
  <iframe width="100%" height="180" frameborder="no" scrolling="no" seamless
    src="https://share.transistor.fm/e/{episode_id}" loading="lazy"></iframe>
  <a class="podcast-link" href="https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV" target="_blank" rel="noopener">
    Follow the podcast on Spotify
  </a>
</div>"""
    else:
        podcast_html = f"""
<div class="podcast-embed">
  <p>This tutorial also has a podcast episode</p>
  <a class="podcast-link" href="https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV" target="_blank" rel="noopener">
    Listen on Spotify — "Go High Level" podcast
  </a>
</div>"""

    # ── Table of contents ──────────────────────────────────────────────────────
    toc_items = extract_toc(html_content)
    if toc_items:
        toc_rows = "".join(f'<li><a href="#{a}">{label}</a></li>' for a, label in toc_items)
        toc_html = f"""
<div class="toc">
  <div class="toc-label">In This Guide</div>
  <ol>{toc_rows}</ol>
</div>"""
    else:
        toc_html = ""

    # ── TL;DR answer box (answer-first) — only when post defines tldr ──────────
    _tldr = post.get("tldr")
    tldr_html = ""
    if _tldr:
        _paras = _tldr if isinstance(_tldr, list) else [_tldr]
        _body = "".join(f"<p>{para}</p>" for para in _paras)
        _tcta = post.get("tldr_cta")
        _tctahtml = ""
        if _tcta:
            _tctahtml = (f'<a class="btn-amber tldr-cta" href="{aff}&utm_campaign={slug}_tldr" '
                         f'target="_blank" rel="nofollow noopener">{_tcta} &rarr;</a>')
        tldr_html = f'<div class="tldr"><div class="tldr-label">The short version</div>{_body}{_tctahtml}</div>'

    # ── CTA #1 — Below byline (compact one-liner) ─────────────────────────────
    cta1 = f"""
<p class="cta-byline">Follow along &mdash; <a href="/start/" rel="nofollow">get 30 days free &rarr;</a></p>"""
    if _tldr:
        cta1 = ""  # the TL;DR already gives the answer up top; drop the redundant one-liner

    # ── CTA #2 — Mid-article inline ───────────────────────────────────────────
    cta_mid = f"""
<p class="cta-inline">This is built into GoHighLevel.
<a href="/start/" rel="nofollow">Try it free for 30 days &rarr;</a></p>"""
    body_with_ctas = inject_inline_ctas(html_content, cta_mid)

    # ── CTA #3 — End of article box ───────────────────────────────────────────
    cta3 = f"""
<div class="cta-end">
  <h3>Ready to try this?</h3>
  <p>$0 for 30 days — just a ~$1 card-verification hold (no subscription charge). Set up everything in this guide inside your trial.</p>
  <a href="{aff}&utm_campaign={slug}" class="btn-amber" target="_blank" rel="nofollow noopener">Start Free 30-Day Trial</a>
  <div class="fine">Cancel anytime &mdash; $0 for the first 30 days</div>
</div>"""

    # ── Share buttons ─────────────────────────────────────────────────────────
    encoded_url = canonical.replace(":", "%3A").replace("/", "%2F")
    encoded_title = title.replace(" ", "%20").replace("&", "%26")
    share_html = f"""
<div class="share-row">
  <span>Share</span>
  <a href="https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}" target="_blank" rel="noopener" class="share-btn">X</a>
  <a href="https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}" target="_blank" rel="noopener" class="share-btn">LinkedIn</a>
  <button class="share-btn" onclick="navigator.clipboard.writeText('{canonical}');this.textContent='Copied!'">Copy Link</button>
</div>"""

    # ── Author box ─────────────────────────────────────────────────────────────
    author_html = f"""
<div class="author-box">
  <div>
    <a href="/about/" class="author-name">William Welch</a>
    <div class="author-role">GoHighLevel Consultant &amp; Agency Automation Specialist</div>
    <div class="author-bio">I help agencies replace 5-10 disconnected tools with one platform. I've built and managed GoHighLevel automations across CRM, email, SMS, WhatsApp, and AI — and I publish everything I learn here. <a href="/about/">More about me &rarr;</a></div>
  </div>
</div>"""

    # ── Related posts ──────────────────────────────────────────────────────────
    related_html = ""
    if all_posts:
        related = get_related(post, all_posts)
        if related:
            cards = ""
            for r in related:
                r_slug  = r.get("slug", "")
                r_title = r.get("title", r.get("seoTitle", ""))
                r_cat   = display_cat(post_topic(r)) or "GoHighLevel"
                r_url   = post_url(r)
                # P0.1 (2026-06-22): anchor = TITLE ONLY. Previously the whole card
                # was one <a> wrapping the category tag + title, so the crawlable anchor
                # was "{category} {title}" repeated across every same-topic post — the
                # 8x identical mega-anchor that is the April-cliff fingerprint. The tag
                # is now non-link text; the title is the only crawlable link.
                cards += f"""
<div class="related-card">
  <span class="r-tag">{r_cat}</span>
  <a href="{r_url}" class="r-title">{r_title}</a>
</div>"""
            related_html = f"""
<div class="related-posts">
  <div class="related-label">Keep Reading</div>
  <div class="related-grid">{cards}</div>
</div>"""

    # ── Schema ─────────────────────────────────────────────────────────────────
    _art_img = (post.get("image") or f"{SITE_URL}/images/og-default.png")
    article_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "image": [_art_img],
        "inLanguage": post.get("language", "en"),
        "datePublished": post.get("publishedAt", post.get("uploadedAt", "")),
        "dateModified": post.get("publishedAt", post.get("uploadedAt", "")),
        "author": {
            "@type": "Person",
            "name": "William Welch",
            "url": f"{SITE_URL}/about/",
            "jobTitle": "GoHighLevel Consultant & Agency Automation Specialist",
            "sameAs": [
                "https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV"
            ]
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": SITE_URL,
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE_URL}/images/logo.png",
                "width": 512,
                "height": 512
            }
        },
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": [".post-title", ".tldr"]
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "url": canonical
    })
    # BreadcrumbList — Home > Category > Title (the visible breadcrumb, now machine-readable).
    # Only emit the category crumb when that hub page is actually built; otherwise the
    # breadcrumb would link a 404 category URL (review 2026-06-25). Mirrors the visible
    # breadcrumb, which already degrades to a <span> when _cat_built is false.
    _crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"}]
    if _cat_built:
        _crumbs.append({"@type": "ListItem", "position": 2, "name": category,
                        "item": f"{SITE_URL}/category/{cat_slug}/"})
    _crumbs.append({"@type": "ListItem", "position": len(_crumbs) + 1,
                    "name": title, "item": canonical})
    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": _crumbs,
    })
    faq_ld = faq_schema(html_content)

    # ── Progress bar JS ────────────────────────────────────────────────────────
    progress_js = """
<script>
(function(){
  var bar=document.getElementById('reading-progress');
  if(!bar)return;
  window.addEventListener('scroll',function(){
    var body=document.querySelector('.post-body');
    if(!body)return;
    var top=body.getBoundingClientRect().top+window.scrollY;
    var h=body.offsetHeight-window.innerHeight;
    var pct=h>0?Math.min(100,Math.max(0,(window.scrollY-top+window.innerHeight*0.1)/h*100)):100;
    bar.style.width=pct+'%';
  },{passive:true});
})();
</script>"""

    body = f"""
<div id="reading-progress"></div>
<div class="post-container">
  <div class="post-breadcrumb fade-1">
    <a href="/">Home</a><span class="bc-sep">&rsaquo;</span>{cat_bc}<span class="bc-sep">&rsaquo;</span><span>{truncate(title, 50)}</span>
  </div>
  <div class="post-eyebrow fade-1">{cat_eyebrow}</div>
  <h1 class="post-title fade-2">{title}</h1>
  <div class="post-byline fade-3">
    <span>By William Welch</span>
    {"<span class='sep'>&middot;</span><span>" + date_str + "</span>" if date_str else ""}
    <span class="sep">&middot;</span><span>{rtime}</span>
  </div>
  {tldr_html}
  {cta1}
  {toc_html}
  {podcast_html}
  <div class="post-body">{body_with_ctas}</div>
  {cta3}
  {share_html}
  {author_html}
  {related_html}
</div>
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{breadcrumb_schema}</script>
{faq_ld}
{progress_js}"""

    post_lang = post.get("language", "en")
    post_lang_config = next((l for l in LANGUAGES if l["code"] == post_lang), None)
    post_dir = post_lang_config.get("dir", "ltr") if post_lang_config else "ltr"

    hreflang_override = _build_post_hreflang_tags(post.get("translations") or {})

    html = base_html(
        title=f"{title} | {SITE_NAME}",
        description=truncate(description, 160),
        canonical=canonical,
        body=body,
        lang=post_lang,
        text_dir=post_dir,
        hreflang_override=hreflang_override,
        disable_hreflang_fallback=True,
    )
    write(PUBLIC_DIR / post_output_rel(post) / "index.html", html)


def build_index(posts: list[dict], page: int = 1, per_page: int = 18):
    total_pages = max(1, -(-len(posts) // per_page))
    start = (page - 1) * per_page
    page_posts = posts[start:start + per_page]

    # ── Build card HTML for all page posts ────────────────────────────────────
    def make_card(p):
        slug     = p.get("slug", "")
        title    = p.get("title", p.get("seoTitle", "Untitled"))
        desc     = truncate(p.get("description", p.get("seoDescription", p.get("meta_description", ""))), 130)
        cat      = display_cat(post_topic(p))
        date_str = fmt_date(p.get("publishedAt", p.get("uploadedAt", "")))
        ep_id    = p.get("transistorEpisodeId", "")
        rtime    = read_time(p.get("html_content", desc))
        cat_html = _cat_link_html(cat, "card-cat")
        podcast  = '<span class="podcast-badge">Podcast</span>' if ep_id else ""
        return f"""
<article class="card">
  {cat_html}
  <h2 class="card-title"><a href="{post_url(p)}">{title}</a></h2>
  <p class="card-excerpt">{desc}</p>
  <div class="card-meta">
    <span>{date_str}</span>
    {"<span class='meta-sep'>&middot;</span><span>" + rtime + "</span>" if date_str else ""}
    {podcast}
  </div>
</article>"""

    # Pagination
    pages_html = ""
    if total_pages > 1:
        for i in range(1, total_pages + 1):
            href = "/" if i == 1 else f"/page/{i}/"
            active = "active" if i == page else ""
            pages_html += f'<a href="{href}" class="page-btn {active}">{i}</a>'
        pages_html = f'<div class="pagination">{pages_html}</div>'

    canonical = SITE_URL + ("/" if page == 1 else f"/page/{page}/")

    # ── PAGE 1: Editorial homepage ────────────────────────────────────────────
    if page == 1 and len(page_posts) > 0:
        lead = page_posts[0]
        stack_posts = page_posts[1:4]
        rest_posts = page_posts[4:]
        # Trending = top 5 posts for sidebar
        trending = posts[:5]

        # Featured section: lead + stack
        lead_slug = lead.get("slug", "")
        lead_title = lead.get("title", lead.get("seoTitle", ""))
        lead_desc = truncate(lead.get("description", lead.get("seoDescription", lead.get("meta_description", ""))), 200)
        lead_cat = display_cat(post_topic(lead))
        lead_date = fmt_date(lead.get("publishedAt", lead.get("uploadedAt", "")))
        lead_rtime = read_time(lead.get("html_content", lead_desc))
        lead_cat_html = _cat_link_html(lead_cat, "hp-lead-cat", "text-decoration:none;display:inline-block")

        stack_html = ""
        for sp in stack_posts:
            sp_slug = sp.get("slug", "")
            sp_title = sp.get("title", sp.get("seoTitle", ""))
            sp_cat = display_cat(post_topic(sp))
            sp_date = fmt_date(sp.get("publishedAt", sp.get("uploadedAt", "")))
            sp_cat_html = _cat_link_html(sp_cat, "hp-stack-cat", "text-decoration:none;display:inline-block")
            stack_html += f"""
<div class="hp-stack-item">
  {sp_cat_html}
  <div class="hp-stack-title"><a href="{post_url(sp)}">{sp_title}</a></div>
  <div class="hp-stack-meta">{sp_date}</div>
</div>"""

        # Article list (rest of posts)
        articles_html = ""
        for p in rest_posts:
            articles_html += make_card(p)

        # Trending sidebar
        trending_html = ""
        for i, tp in enumerate(trending, 1):
            tp_slug = tp.get("slug", "")
            tp_title = tp.get("title", tp.get("seoTitle", ""))
            trending_html += f"""
<div class="trending-item">
  <span class="trending-num">{i:02d}</span>
  <div class="trending-title"><a href="{post_url(tp)}">{tp_title}</a></div>
</div>"""

        # Topics sidebar
        topics_html = ""
        for c in CATEGORIES:
            if c["slug"] not in LIVE_CATEGORY_SLUGS:
                continue  # skip emptied categories — their page 404s post-prune
            c_count = len([p for p in posts if slugify(post_topic(p)) == c["slug"]])
            topics_html += f"""
<a href="/category/{c['slug']}/" class="sidebar-cat-link">
  <span>{c['name']}</span>
  <span class="sidebar-cat-count">{c_count}</span>
</a>"""

        money_url = "/blog/gohighlevel-free-trial-30-days-extended/"
        body = f"""
<header class="hh"><div class="container">
  <h1>Everything <em>GoHighLevel</em> &mdash; free guides and the 30-day trial.</h1>
  <p class="sub">GlobalHighLevel is the free library for setting GoHighLevel up right &mdash; real tutorials from people who actually use it, plus the <b>extended 30-day trial</b> (double the standard 14). Start with the complete trial guide.</p>
  <a class="guidecard" href="{money_url}">
    <div class="gc-ic">&#9733;</div>
    <div>
      <div class="gc-k">Our most-read guide</div>
      <div class="gc-t">The complete 30-day free trial guide</div>
      <div class="gc-d">Eligibility, the exact steps, the promo-code truth, and the free setup bootcamp &mdash; the full walkthrough.</div>
    </div>
    <span class="gc-arrow">Read &rarr;</span>
  </a>
</div></header>
<section class="hubsec" id="guides"><div class="container">
  <span class="eyebrow">Every GoHighLevel topic</span>
  <h2>Set GoHighLevel up right &mdash; by topic</h2>
  <p class="lead">The full library, organized. Pick the area you're working on.</p>
  <div class="clusters">
    <div class="cluster"><h3>AI Receptionist &amp; Lead Capture</h3><p>Never miss a call or a lead &mdash; AI receptionist, missed-call text-back, and automatic review requests.</p><a class="cl" href="/category/agency-platform/">Explore guides &rarr;</a></div>
    <div class="cluster"><h3>AI Agents &amp; Automation</h3><p>Put the platform on autopilot &mdash; AI agents, workflows, and Conversation AI.</p><a class="cl" href="/blog/gohighlevel-ai-agents-automation-complete-guide/">Explore guides &rarr;</a></div>
    <div class="cluster"><h3>CRM &amp; Communication</h3><p>Run the whole customer relationship in one place &mdash; CRM, email &amp; SMS, the phone system, and the calendar.</p><a class="cl" href="/category/crm-communication/">Explore guides &rarr;</a></div>
    <div class="cluster"><h3>Sites, Funnels &amp; Reputation</h3><p>Capture leads and look credible &mdash; websites &amp; funnels, forms, reviews, and listings.</p><a class="cl" href="/blog/how-to-launch-a-website-in-gohighlevel-pro-templates/">Explore guides &rarr;</a></div>
    <div class="cluster"><h3>Agency, White-Label &amp; SaaS</h3><p>Resell GoHighLevel as your own &mdash; white-label, SaaS mode, sub-accounts, and snapshots.</p><a class="cl" href="/category/agency-platform/">Explore guides &rarr;</a></div>
    <div class="cluster"><h3>Payments &amp; Pricing</h3><p>Get paid inside GoHighLevel and know exactly what it costs &mdash; payments and the full pricing breakdown.</p><a class="cl" href="/blog/gohighlevel-payments-complete-guide/">Explore guides &rarr;</a></div>
  </div>
  <div class="es-banner">
    <div><b style="color:var(--text)">&iquest;Hablas espa&ntilde;ol?</b> <span style="color:var(--text2)">La biblioteca de gu&iacute;as de GoHighLevel y la prueba de 30 d&iacute;as, en espa&ntilde;ol.</span></div>
    <a class="btn-amber" href="/es/" style="font-size:.85rem;padding:10px 18px">Ir a la versi&oacute;n en espa&ntilde;ol &rarr;</a>
  </div>
</div></section>"""
    else:
        # Non-first pages or empty: simple list
        cards_html = ""
        for p in page_posts:
            cards_html += make_card(p)

        body = f"""
<div class="container" style="padding-top:100px">
  <div class="section-label">{"Tutorials" if page == 1 else f"Page {page}"}</div>
  <div class="cards-grid">{cards_html}</div>
  {pages_html}
</div>"""

    # Homepage-only Organization JSON-LD (entity/logo recognition; other pages
    # carry publisher Organization inside their Article schema).
    if page == 1:
        org_schema = json.dumps({
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": SITE_NAME,
            "url": SITE_URL,
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE_URL}/images/logo.png",
                "width": 512,
                "height": 512,
            },
            "sameAs": [
                "https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV",
            ],
        })
        body += f'\n<script type="application/ld+json">{org_schema}</script>'

    html = base_html(
        title=f"{SITE_NAME} — {SITE_TAGLINE}" if page == 1 else f"Page {page} | {SITE_NAME}",
        description="Free GoHighLevel tutorials, guides, and strategies for digital marketing agencies worldwide. Learn GHL step by step.",
        canonical=canonical,
        body=body
    )
    if page == 1:
        write(PUBLIC_DIR / "index.html", html)
    else:
        write(PUBLIC_DIR / "page" / str(page) / "index.html", html)


def build_category_pages(posts: list[dict]):
    # Root /category/ pages are ENGLISH ONLY. 2026-05-23 cliff fix: previously
    # this bucketed ALL languages together (build_category_pages(merged)), so
    # /category/agency-platform/ etc. listed Spanish/India/Arabic posts on an
    # English page. Classify via post_lang() (slug-aware) so the 469 posts with
    # no `language` field land correctly instead of defaulting to "en".
    by_cat: dict[str, list] = {}
    for p in posts:
        if post_lang(p) != "en":
            continue
        # Bucket on TOPIC (T3), not the back-compat `category`. post_topic() never
        # returns a language bucket, so the old bucket-skip is no longer needed: the
        # 123 English posts formerly mis-filed under "en Español" now surface here
        # under their real topic.
        topic = post_topic(p)
        cat = topic if display_cat(topic) else "GoHighLevel Tutorials"
        by_cat.setdefault(cat, []).append(p)

    for cat, cat_posts in by_cat.items():
        cat_slug = slugify(cat)
        if len(cat_posts) < MIN_HUB_POSTS:
            continue  # P1.1: don't build thin 1-post hubs (2026-06-22)
        cards_html = ""
        for p in cat_posts:
            slug     = p.get("slug", "")
            title    = p.get("title", p.get("seoTitle", "Untitled"))
            desc     = truncate(p.get("description", p.get("seoDescription", p.get("meta_description", ""))), 130)
            date_str = fmt_date(p.get("publishedAt", p.get("uploadedAt", "")))
            ep_id    = p.get("transistorEpisodeId", "")
            rtime    = read_time(p.get("html_content", desc))
            cat_label = display_cat(cat)
            cat_html  = _cat_link_html(cat_label, "card-cat")
            podcast   = '<span class="podcast-badge">Podcast</span>' if ep_id else ""
            cards_html += f"""
<article class="card">
  {cat_html}
  <h2 class="card-title"><a href="{post_url(p)}">{title}</a></h2>
  <p class="card-excerpt">{desc}</p>
  <div class="card-meta">
    <span>{date_str}</span>
    {"<span class='meta-sep'>&middot;</span><span>" + rtime + "</span>" if date_str else ""}
    {podcast}
  </div>
</article>"""

        cat_config = next((c for c in CATEGORIES if c["slug"] == cat_slug), None)
        cat_desc = cat_config["description"] if cat_config else f"Free GoHighLevel {cat.lower()} guides and tutorials."

        body = f"""
<div class="cat-header">
  <div class="container">
    <div class="section-label fade-1" style="border-bottom:none;padding-bottom:0;margin-bottom:8px">Category</div>
    <h1 class="fade-2">{cat}</h1>
    <p class="fade-3">{cat_desc}</p>
    <p class="fade-3" style="font-size:.8rem;color:var(--text3);margin-top:6px">{len(cat_posts)} guides</p>
  </div>
</div>
<div class="container">
  <div class="cards-grid" style="padding:32px 0 80px">{cards_html}</div>
</div>"""

        canonical = f"{SITE_URL}/category/{cat_slug}/"
        html = base_html(
            title=f"{cat} | {SITE_NAME}",
            description=f"Free GoHighLevel {cat.lower()} guides and tutorials. Step-by-step help for agencies and businesses.",
            canonical=canonical,
            body=body
        )
        write(PUBLIC_DIR / "category" / cat_slug / "index.html", html)


def _xml_attr(s: str) -> str:
    """Escape a string for safe use inside a double-quoted XML attribute value."""
    return _xml_escape(s, {'"': "&quot;"})


def _sitemap_loc(url: str) -> str:
    """Escape a URL for safe use as XML element text (<loc>/<lastmod>)."""
    return _xml_escape(url)


def _sitemap_alts(page_path: str) -> str:
    """xhtml:link hreflang alternates for an index/category page, in sitemap form.
    Mirrors _build_hreflang_tags (only emits variants that were actually built, via
    BUILT_PAGE_PATHS) but returns <xhtml:link.../> nodes for inclusion inside <url>.
    Returns "" unless there are >=2 real language variants (a single-variant page
    has no alternates to declare). All href values are XML-attribute-escaped."""
    out = []
    for lang in LANGUAGES:
        prefix = lang.get("prefix", "")
        rel = f'{prefix}{page_path}' if page_path else f'{prefix}/'
        if rel not in BUILT_PAGE_PATHS:
            continue
        out.append(f'<xhtml:link rel="alternate" hreflang="{_xml_attr(lang["code"])}" href="{_xml_attr(SITE_URL + rel)}"/>')
    if len(out) < 2:
        return ""
    default_rel = page_path or "/"
    if default_rel in BUILT_PAGE_PATHS:
        out.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{_xml_attr(SITE_URL + default_rel)}"/>')
    return "".join(out)


def _sitemap_post_alts(translations: dict) -> str:
    """xhtml:link hreflang alternates for a blog post, from its slug-per-language map.
    Mirrors _build_post_hreflang_tags; skips pruned siblings (not in LIVE_POST_SLUGS).
    Returns "" unless >=2 live language variants exist."""
    if not translations or not isinstance(translations, dict):
        return ""
    out = []
    for code, slug in translations.items():
        if not slug or slug not in LIVE_POST_SLUGS:
            continue
        out.append(f'<xhtml:link rel="alternate" hreflang="{_xml_attr(code)}" href="{_xml_attr(f"{SITE_URL}/blog/{slug}/")}"/>')
    if len(out) < 2:
        return ""
    default_slug = translations.get("en") if translations.get("en") in LIVE_POST_SLUGS else ""
    if not default_slug:
        default_slug = next((s for s in translations.values() if s in LIVE_POST_SLUGS), "")
    if default_slug:
        out.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{_xml_attr(f"{SITE_URL}/blog/{default_slug}/")}"/>')
    return "".join(out)


def build_sitemap(posts: list[dict]):
    # Build/deploy date stamps the derived index + hub pages (/, /es/, categories):
    # they legitimately change whenever the site is rebuilt with new content/structure,
    # so a fresh lastmod is the correct re-crawl signal post-deploy. Posts carry their
    # own updatedAt/publishedAt date (real content freshness).
    build_date = datetime.now().strftime("%Y-%m-%d")
    home_alts = _sitemap_alts("")
    urls = [f"  <url><loc>{_sitemap_loc(f'{SITE_URL}/')}</loc><lastmod>{build_date}</lastmod><changefreq>daily</changefreq><priority>1.0</priority>{home_alts}</url>"]
    # /trial/, /start/, /coupon/ are excluded from sitemap:
    # - /trial/ and /start/ are noindex conversion surfaces (podcast/blog CTAs)
    # - /coupon/ 301 redirects to /blog/gohighlevel-free-trial-30-days-extended/ (discount-consolidation 2026-04-21)
    urls.append(f"  <url><loc>{_sitemap_loc(f'{SITE_URL}/services/')}</loc><lastmod>{build_date}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>")
    urls.append(f"  <url><loc>{_sitemap_loc(f'{SITE_URL}/about/')}</loc><lastmod>{build_date}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>")
    # Only list pages that were actually built. The 2026-06-03 prune emptied many
    # categories/languages; build_sitemap runs after the category and language
    # page builders, so the index.html on disk is ground truth for these entries
    # — never advertise a 404 to Google.
    for c in CATEGORIES:
        if (PUBLIC_DIR / "category" / c["slug"] / "index.html").exists():
            alts = _sitemap_alts(f'/category/{c["slug"]}/')
            urls.append(f'  <url><loc>{_sitemap_loc(SITE_URL + "/category/" + c["slug"] + "/")}</loc><lastmod>{build_date}</lastmod><changefreq>weekly</changefreq><priority>0.6</priority>{alts}</url>')
    # Language hubs + language-specific topic pages
    for lang in LANGUAGES:
        prefix = lang["prefix"]
        if prefix and (PUBLIC_DIR / prefix.lstrip("/") / "index.html").exists():
            urls.append(f'  <url><loc>{_sitemap_loc(f"{SITE_URL}{prefix}/")}</loc><lastmod>{build_date}</lastmod><changefreq>daily</changefreq><priority>0.9</priority>{home_alts}</url>')
            for c in CATEGORIES:
                if (PUBLIC_DIR / prefix.lstrip("/") / "category" / c["slug"] / "index.html").exists():
                    alts = _sitemap_alts(f'/category/{c["slug"]}/')
                    urls.append(f'  <url><loc>{_sitemap_loc(SITE_URL + prefix + "/category/" + c["slug"] + "/")}</loc><lastmod>{build_date}</lastmod><changefreq>weekly</changefreq><priority>0.6</priority>{alts}</url>')
    for p in posts:
        # Prefer an explicit updatedAt (real content edit) over publishedAt so a
        # rebuilt post signals freshness instead of its original publish date.
        date = (p.get("updatedAt") or p.get("publishedAt") or p.get("uploadedAt") or "")[:10]
        lastmod = f'<lastmod>{date}</lastmod>' if date else ''
        palts = _sitemap_post_alts(p.get("translations") or {})
        urls.append(f'  <url><loc>{_sitemap_loc(f"{SITE_URL}{post_url(p)}")}</loc>{lastmod}<changefreq>monthly</changefreq><priority>0.8</priority>{palts}</url>')

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n  xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    xml += "\n".join(urls)
    xml += "\n</urlset>"
    write(PUBLIC_DIR / "sitemap.xml", xml)


def build_llms_txt(posts: list[dict]):
    """
    Generate llms.txt — tells AI models (ChatGPT, Claude, Perplexity, Gemini)
    what this site is about and lists all available content.
    Standard: https://llmstxt.org
    """
    post_lines = ""
    for p in posts[:200]:  # cap at 200 most recent
        title = p.get("title", p.get("seoTitle", ""))
        slug  = p.get("slug", "")
        desc  = truncate(p.get("description", p.get("seoDescription", p.get("meta_description", ""))), 120)
        if title and slug:
            post_lines += f"- [{title}]({SITE_URL}/blog/{slug}/): {desc}\n"

    content = f"""# GlobalHighLevel.com

> Free GoHighLevel tutorials, guides, and strategies for digital marketing agencies and businesses worldwide.

GlobalHighLevel.com is a free resource covering GoHighLevel (GHL) — an all-in-one CRM, marketing automation, and funnel platform used by digital marketing agencies globally. Every tutorial on this site also has a corresponding podcast episode on Spotify ("Go High Level", {SITE_URL}).

## About

- **Author:** William Welch — GoHighLevel user and affiliate
- **Audience:** Digital marketing agency owners, freelancers, business owners
- **Content:** {len(posts)} step-by-step tutorials and guides covering GoHighLevel features
- **Podcast:** "Go High Level" on Spotify — https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV
- **Free Trial:** 30-day GoHighLevel free trial (double the standard 14 days) — https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12

## Content

All tutorials are free. Topics include GoHighLevel automations, AI conversation bots, funnel building, pipeline management, SMS/email marketing, reputation management, calendar booking, white-label SaaS setup, and sub-account management.

## Tutorials

{post_lines if post_lines else "- New tutorials published daily. See full list at " + SITE_URL}

## Optional

- Sitemap: {SITE_URL}/sitemap.xml
- Podcast: https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV
"""
    write(PUBLIC_DIR / "llms.txt", content)


def build_trial_page():
    """Build affiliate landing pages in all supported languages.
    English: /trial/, /start/ — full SEO-optimized page (282 lines).
    ES/IN/AR: /{lang}/trial/, /{lang}/start/ — minimal native-language landing."""
    _build_affiliate_landing("trial", "podcast")
    _build_affiliate_landing("start", "blog")
    for lang_cfg in LOCALIZED_LANDING_LANGS:
        _build_localized_affiliate_landing(lang_cfg, "trial", "podcast")
        _build_localized_affiliate_landing(lang_cfg, "start", "blog")


LOCALIZED_LANDING_LANGS = [
    {
        "code": "es",
        "prefix": "/es",
        "dir": "ltr",
        "title": "Prueba GoHighLevel Gratis 30 Días — Empieza con $0",
        "desc": "Comienza tu prueba gratis de 30 días de GoHighLevel. Solo se requiere una tarjeta para verificación (una retención temporal de ~$1 que tu banco libera, sin cargo de suscripción). Acceso completo a todas las funciones. Cancela cuando quieras.",
        "h1": "Prueba GoHighLevel Gratis por 30 Días",
        "subh": "$0 por 30 días — solo una verificación de tarjeta de ~$1. Acceso completo. Cancela cuando quieras.",
        "cta": "Empezar mi prueba gratis",
        "value_props": [
            ("CRM todo-en-uno", "Reemplaza 10+ herramientas: CRM, embudos, email, SMS, WhatsApp, calendarios, pagos."),
            ("WhatsApp Business integrado", "El canal real en Latinoamérica. Automatiza seguimientos sin saltar entre apps."),
            ("Desde $97 USD/mes", "Después de los 30 días. Cancelas cuando quieras, sin compromiso."),
        ],
        "faq_h": "Preguntas frecuentes",
        "faq": [
            ("¿Necesito tarjeta de crédito?", "Sí. Para activar la prueba de 30 días se requiere una tarjeta — es una verificación de ~$1 que tu banco libera, no un cargo de suscripción. No pagas nada durante los 30 días y cancelas cuando quieras."),
            ("¿Cuánto cuesta después de la prueba?", "Desde $97 USD al mes. Puedes cancelar en cualquier momento durante los 30 días sin cargo."),
            ("¿Qué pasa si cancelo?", "Tu cuenta se cierra sin cargo. Mantienes lo que construiste pero no puedes acceder después de la cancelación."),
        ],
        "footer_cta": "Empieza tu prueba de 30 días ahora",
    },
    {
        "code": "in",
        "prefix": "/in",
        "dir": "ltr",
        "title": "GoHighLevel Free Trial India — 30 Days, $0 to Start",
        "desc": "Start your 30-day GoHighLevel free trial in India. A card is required to verify (a temporary ~$1 hold, no subscription charge; 3DS/OTP for Indian cards). Full access to all features, $97/mo (~₹8,000) after trial. Cancel anytime.",
        "h1": "Start Your 30-Day GoHighLevel Free Trial",
        "subh": "$0 for 30 days — just a ~$1 card-verification hold. Full access. Built for Indian agencies with Razorpay, WhatsApp, and UPI integration.",
        "cta": "Start my free trial",
        "value_props": [
            ("All-in-one CRM for Indian agencies", "Replace 10+ tools. CRM, funnels, email, WhatsApp, UPI-ready payments."),
            ("WhatsApp + Razorpay native", "Built for how Indian agencies actually operate. No US-centric SMS/Stripe bottlenecks."),
            ("Starts at $97 USD/mo (~₹8,000)", "After your free 30 days. Cancel anytime, no commitment."),
        ],
        "faq_h": "Frequently asked questions",
        "faq": [
            ("Do I need a credit card?", "Yes. Activating the 30-day trial requires a card — it's a ~$1 verification hold your bank releases, not a subscription charge. You pay nothing for 30 days and can cancel anytime. (Indian cards use 3DS/OTP.)"),
            ("What does it cost after the trial?", "Starts at $97 USD/month (~₹8,000/month). Agency plan ~₹24,700/month. Cancel anytime during the 30-day trial with no charge."),
            ("Does it work with Razorpay and WhatsApp Business API?", "Yes. GoHighLevel supports Razorpay and WhatsApp Business API natively — no third-party integration headaches."),
        ],
        "footer_cta": "Start your 30-day trial",
    },
]


def _build_localized_affiliate_landing(lang_cfg: dict, slug: str, campaign: str):
    """Build a localized affiliate landing page at /{lang}/{slug}/.
    Minimal native-language version — full SEO optimization lives in English /trial/ + /start/.
    Focus: reassure the non-EN reader they're in the right place, click through to affiliate."""
    lang = lang_cfg["code"]
    prefix = lang_cfg["prefix"]
    direction = lang_cfg["dir"]
    canonical = f"{SITE_URL}{prefix}/{slug}/"
    affiliate_url = f"{affiliate_for(lang)}&utm_campaign={lang}-{campaign}"

    value_props_html = "\n".join(
        f'  <div class="vp-item">\n    <strong>{name}</strong>\n    <p>{desc}</p>\n  </div>'
        for name, desc in lang_cfg["value_props"]
    )
    faq_html = "\n".join(
        f'  <div class="faq-item">\n    <h3>{q}</h3>\n    <p>{a}</p>\n  </div>'
        for q, a in lang_cfg["faq"]
    )

    body = f"""
<div class="trial-wrap" dir="{direction}">
  <header class="trial-header">
    <h1>{lang_cfg["h1"]}</h1>
    <p class="trial-sub">{lang_cfg["subh"]}</p>
    <a class="trial-cta-primary" href="{affiliate_url}" target="_blank" rel="nofollow noopener">{lang_cfg["cta"]} →</a>
  </header>

  <section class="trial-value-props">
{value_props_html}
  </section>

  <section class="trial-faq">
    <h2>{lang_cfg["faq_h"]}</h2>
{faq_html}
  </section>

  <footer class="trial-footer-cta">
    <a class="trial-cta-primary" href="{affiliate_url}" target="_blank" rel="nofollow noopener">{lang_cfg["footer_cta"]} →</a>
  </footer>
</div>

<style>
  .trial-wrap {{ max-width: 760px; margin: 0 auto; padding: 48px 24px; font-family: Georgia, serif; line-height: 1.7; color: #1a1a1a; }}
  .trial-header {{ text-align: center; padding: 32px 0 48px; border-bottom: 1px solid #e5e5e5; margin-bottom: 48px; }}
  .trial-header h1 {{ font-size: 36px; line-height: 1.2; margin: 0 0 16px; }}
  .trial-sub {{ font-size: 18px; color: #555; margin: 0 0 32px; }}
  .trial-cta-primary {{ display: inline-block; background: #f59e0b; color: #111520; padding: 16px 32px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 17px; font-family: -apple-system, sans-serif; }}
  .trial-cta-primary:hover {{ background: #d97706; color: #fff; }}
  .trial-value-props {{ display: grid; gap: 24px; margin-bottom: 56px; }}
  .vp-item strong {{ display: block; font-size: 18px; margin-bottom: 6px; }}
  .vp-item p {{ margin: 0; color: #444; }}
  .trial-faq h2 {{ font-size: 26px; margin: 0 0 24px; }}
  .faq-item {{ margin-bottom: 28px; }}
  .faq-item h3 {{ font-size: 18px; margin: 0 0 8px; }}
  .faq-item p {{ margin: 0; color: #333; }}
  .trial-footer-cta {{ text-align: center; padding: 48px 0 24px; border-top: 1px solid #e5e5e5; margin-top: 48px; }}
</style>
"""
    html = base_html(
        title=f"{lang_cfg['title']} | {SITE_NAME}",
        description=lang_cfg["desc"],
        canonical=canonical,
        body=body,
        lang=lang,
        text_dir=direction,
        noindex=True,  # localized /{lang}/trial/ and /{lang}/start/ are conversion surfaces too
    )
    write(PUBLIC_DIR / lang / slug / "index.html", html)


def _build_affiliate_landing(slug: str, campaign: str):
    """Build an SEO-optimized affiliate landing page at /{slug}/ with utm_campaign={campaign}.

    Both /trial/ (podcast traffic) and /start/ (blog traffic) are identical in content —
    separate URLs allow GA4 to attribute traffic source via page_path.
    """
    canonical = f"{SITE_URL}/{slug}/"
    title = "GoHighLevel Free Trial 2026: 30 Days, $0 to Start"
    description = "Start your 30-day GoHighLevel free trial — $0 to start (just a ~$1 card-verification hold, no subscription charge). Full access to every feature, cancel anytime. Zero risk, real results."

    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "How long is the GoHighLevel free trial?",
                "acceptedAnswer": {"@type": "Answer", "text": "The standard GoHighLevel free trial is 14 days. Through GlobalHighLevel.com, you get an extended 30-day free trial \u2014 double the time to explore every feature."}
            },
            {
                "@type": "Question",
                "name": "Do I need a credit card for the GoHighLevel free trial?",
                "acceptedAnswer": {"@type": "Answer", "text": "Yes, a card is required to start the trial: a ~$1 verification hold your bank releases, not a subscription charge. You pay nothing for 30 days and can cancel anytime."}
            },
            {
                "@type": "Question",
                "name": "What do I get with the GoHighLevel free trial?",
                "acceptedAnswer": {"@type": "Answer", "text": "Full access to GoHighLevel's CRM, funnel builder, email & SMS marketing, workflow automations, AI conversation bots, calendar booking, reputation management, and more. Nothing is locked during the trial."}
            },
            {
                "@type": "Question",
                "name": "How much does GoHighLevel cost after the free trial?",
                "acceptedAnswer": {"@type": "Answer", "text": "GoHighLevel starts at $97/month after the trial ends. You can cancel anytime during your 30-day free trial if it's not the right fit."}
            },
            {
                "@type": "Question",
                "name": "Is this GoHighLevel free trial legitimate?",
                "acceptedAnswer": {"@type": "Answer", "text": "Yes. This is an official GoHighLevel extended trial offered through their affiliate program. You sign up directly on GoHighLevel's website with full access to all features."}
            },
            {
                "@type": "Question",
                "name": "GoHighLevel 14-day trial vs 30-day trial \u2014 what's the difference?",
                "acceptedAnswer": {"@type": "Answer", "text": "The features are identical. The only difference is time. The standard trial from gohighlevel.com gives you 14 days. Through this page, you get 30 days \u2014 enough time to set up funnels, migrate contacts, and see real results before deciding."}
            },
            {
                "@type": "Question",
                "name": "Can I extend beyond 30 days?",
                "acceptedAnswer": {"@type": "Answer", "text": "No. 30 days is the full trial window. If you're close to a decision, contact support to discuss your specific use case. Plan accordingly."}
            },
            {
                "@type": "Question",
                "name": "GHL vs HubSpot free\u2014which for agencies?",
                "acceptedAnswer": {"@type": "Answer", "text": "HubSpot is CRM-heavy and free forever but capped. GHL is built for agencies: funnel builder, SMS, sub-accounts, and automation without limits. If you're reselling or scaling a team, GHL may be a better fit. If you want just a CRM, HubSpot is an option."}
            },
            {
                "@type": "Question",
                "name": "What if I cancel during the trial?",
                "acceptedAnswer": {"@type": "Answer", "text": "You cancel. Your account closes. No charge. No follow-up emails pushing you back. You keep any work you built (funnels, landing pages, contacts) but can't access them after the trial ends unless you restart."}
            },
            {
                "@type": "Question",
                "name": "Do I get workflow automation features in the trial?",
                "acceptedAnswer": {"@type": "Answer", "text": "Yes. Full access to workflow automation, conditional logic, SMS sequences, and AI-powered features on your plan tier. You can build automated lead qualification workflows immediately."}
            },
            {
                "@type": "Question",
                "name": "Can I migrate contacts and funnels in during the trial?",
                "acceptedAnswer": {"@type": "Answer", "text": "Yes. Import CSV contacts, migrate landing pages from other builders, or connect your Stripe/payment processor. The trial is a full sandbox. Refer to the help center for migration documentation."}
            }
        ]
    })

    offer_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Offer",
        "name": "GoHighLevel 30-Day Free Trial",
        "description": "Extended 30-day free trial for GoHighLevel — CRM, funnels, automations, and AI tools for agencies.",
        "price": "0",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock",
        "url": canonical,
        "seller": {"@type": "Organization", "name": "GoHighLevel"}
    })

    body = f"""
<div class="post-container" style="max-width:740px;padding-top:100px">

  <div class="fade-1" style="text-align:center;margin-bottom:48px">
    <p style="font-size:.82rem;color:var(--text3);margin-bottom:24px">Already know you want in? <a href="{AFFILIATE}&utm_campaign={campaign}-skip" target="_blank" rel="nofollow noopener" style="color:var(--amber)">Go straight to GoHighLevel &rarr;</a></p>
    <p style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:16px">Extended 30-Day Offer · $0 to Start</p>
    <h1 style="font-family:var(--sans);font-size:clamp(2rem,4vw,3.2rem);font-weight:800;line-height:1.15;color:var(--text);letter-spacing:-.5px;margin-bottom:20px">30 Days to Test GoHighLevel. $0 to Start. No BS.</h1>
    <p style="font-size:1.15rem;color:var(--text2);line-height:1.7;max-width:580px;margin:0 auto 28px">Most trials give you 14 days and hope you figure it out. We give you 30—enough time to actually build, test, and decide if GHL scales your business.</p>
    <a href="{AFFILIATE}&utm_campaign={campaign}-hero" class="btn-amber" style="font-size:1rem;padding:14px 36px" target="_blank" rel="nofollow noopener">Start Your 30-Day Free Trial &rarr;</a>
    <p style="font-size:.8rem;color:var(--text3);margin-top:12px">$0 for 30 days &middot; ~$1 card-verification hold &middot; Cancel anytime</p>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px" class="fade-2">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">Why Get a 30-Day GHL Free Trial Instead of 14?</h2>
<p style="font-size:1.05rem;color:var(--text2);line-height:1.75;margin-bottom:20px">Fourteen days is a speed bump, not a runway. Agencies and home service owners we work with need 30 days minimum to build a working funnel, run a test campaign, and see real data. The extra 16 days isn't padding—it's the difference between 'maybe' and 'proven ROI.'</p>
    <p style="font-size:1.05rem;color:var(--text2);line-height:1.75;margin-bottom:20px">You won't hit a paywall mid-build. Full access to CRM, funnel builder, email, SMS, workflow automation, sub-accounts (if you're scaling a team), and landing pages. No restrictions. No 'upgrade to see this.' Trial on your chosen plan level.</p>
    <p style="font-size:1.05rem;color:var(--text2);line-height:1.75;margin-bottom:20px">No subscription charge upfront — just a ~$1 card-verification hold your bank releases. No surprise charges on day 15. Cancel anytime before 30 days pass and pay nothing. If you stay, it's $97/mo (Starter) or $297/mo (Agency). That's it. Many agencies and service businesses have already proven it works; now you test it risk-free.</p>
  </div>


  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">Standard 14-Day Trial vs Our 30-Day Trial</h2>
    <div style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--border);border-radius:8px;overflow:hidden">
      <thead><tr style="background:var(--bg2)">
        <th style="padding:14px 16px;text-align:left;font-size:.85rem;font-weight:700;color:var(--text)">What you get</th>
        <th style="padding:14px 16px;text-align:left;font-size:.85rem;font-weight:700;color:var(--text2)">Standard 14-day</th>
        <th style="padding:14px 16px;text-align:left;font-size:.85rem;font-weight:700;color:var(--amber)">Our 30-day</th>
      </tr></thead>
      <tbody>
        <tr><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">Trial length</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">14 days</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text);font-weight:600">30 days</td></tr>
        <tr><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">Credit card to start</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">Yes (charged)</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text);font-weight:600">~$1 hold only</td></tr>
        <tr><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">Full feature access</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">Limited/restricted</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text);font-weight:600">100% unrestricted</td></tr>
        <tr><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">Time to build & test</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">Rushed</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text);font-weight:600">Real-world validation</td></tr>
        <tr><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">Cost if you cancel</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)">Risk of charges</td><td style="padding:12px 16px;border-top:1px solid var(--border);color:var(--text);font-weight:600">$0 guaranteed</td></tr>
      </tbody>
    </table>
    </div>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">Who This 30-Day Trial Is Built For</h2>
    <div style="display:grid;grid-template-columns:1fr;gap:16px">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:24px"><div style="font-size:.95rem;font-weight:700;color:var(--text);margin-bottom:10px">Marketing agencies (1-50 clients)</div><p style="font-size:.88rem;color:var(--text2);line-height:1.7;margin:0">You need to know if GHL's sub-account structure and automation engine will actually replace your current stack before pitching it to clients. 30 days lets you build a real client funnel, test workflows, and measure results—not just kick the tires.</p></div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:24px"><div style="font-size:.95rem;font-weight:700;color:var(--text);margin-bottom:10px">Home services (plumbing, HVAC, electrical)</div><p style="font-size:.88rem;color:var(--text2);line-height:1.7;margin:0">Your calendar, SMS reminders, and lead follow-up are costing you time and leads. The trial gives you 30 days to connect GHL to your phone, set up automated appointment reminders, and see if it streamlines your admin work.</p></div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:24px"><div style="font-size:.95rem;font-weight:700;color:var(--text);margin-bottom:10px">Solo consultants and coaches</div><p style="font-size:.88rem;color:var(--text2);line-height:1.7;margin:0">You're running everything yourself. 30 days is enough to build your email funnel, landing page, and automated nurture sequence without feeling rushed. By day 25, you'll know if the platform fits your workflow.</p></div>
    </div>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">What Happens When You Start the Free Trial</h2>
    <div style="display:grid;grid-template-columns:1fr;gap:16px">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px"><div style="font-size:.85rem;font-weight:700;color:var(--amber);margin-bottom:6px">Step 1: Click to start</div><p style="font-size:.88rem;color:var(--text2);line-height:1.65;margin:0">One click to start. You verify a card (a ~$1 hold, not a subscription charge) and choose your plan level—full features on all of them during the trial.</p></div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px"><div style="font-size:.85rem;font-weight:700;color:var(--amber);margin-bottom:6px">Step 2: Set up in ~20 min</div><p style="font-size:.88rem;color:var(--text2);line-height:1.65;margin:0">Connect your domain, import contacts if you have them, and pick a template. GHL's funnel builder is drag-and-drop. You'll have a live landing page or lead form before your coffee gets cold.</p></div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px"><div style="font-size:.85rem;font-weight:700;color:var(--amber);margin-bottom:6px">Step 3: Build, test, decide</div><p style="font-size:.88rem;color:var(--text2);line-height:1.65;margin:0">Spend days 2–25 running a real campaign. Drive traffic. Capture leads. Watch the automations work. By day 28, you'll have actual numbers to decide on.</p></div>
    </div>
    <p style="font-size:.9rem;color:var(--text2);line-height:1.7;margin-top:20px">Every feature is unlocked during the 30-day window. No upgrade pushes, no locked tools. Build a full client campaign and see the numbers yourself before deciding.</p>
  </div>
  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px" class="fade-2">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">What's Included in Your GHL Free Trial</h2>
    <div class="trial-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:6px">CRM &amp; Pipeline Management</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">Contacts, deals, tags, smart lists, and custom pipelines to manage every lead.</p>
      </div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:6px">Funnel &amp; Website Builder</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">Drag-and-drop pages, forms, surveys, and full websites — no code needed.</p>
      </div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:6px">Email &amp; SMS Marketing</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">Bulk campaigns, drip sequences, and two-way conversations in one inbox.</p>
      </div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:6px">Workflow Automations</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">If/else logic, triggers, wait steps, webhooks — automate your entire client journey.</p>
      </div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:6px">AI Conversation Bots</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">Agent Studio, brand voice AI, and automated chat/SMS bots that book appointments.</p>
      </div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:6px">Calendar &amp; Booking</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">Booking widgets, round-robin scheduling, Google/Outlook sync, and reminders.</p>
      </div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:6px">Reputation Management</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">Automated review requests, Google review widget, and review response tools.</p>
      </div>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:6px">White-Label SaaS Mode</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">Rebrand GHL as your own platform and resell to clients at your own price.</p>
      </div>
    </div>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <div style="background:var(--surface);border:1px solid var(--amber-border);border-radius:8px;padding:32px">
      <p style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:12px">Prefer done-for-you setup?</p>
      <h2 style="font-family:var(--sans);font-size:1.4rem;font-weight:800;color:var(--text);margin-bottom:16px;margin-top:0">Extendly handles GoHighLevel onboarding for you</h2>
      <p style="font-size:1.02rem;color:var(--text2);line-height:1.7;margin-bottom:18px">If you want the 30-day trial, but do not want to spend the 30 days doing the setup yourself, Extendly does it for you. They handle GoHighLevel onboarding, 24/7 white-label support for your clients, and pre-built snapshots you can import and run. We use them ourselves.</p>
      <a href="https://getextendly.com?deal=vqzoli&amp;fp_sid={slug}-landing"
         onclick="gtag('event','extendly_click',{{page_path:'/{slug}/',source:'{campaign}'}})"
         class="btn-amber"
         style="display:inline-block;font-size:.95rem;padding:12px 28px"
         target="_blank" rel="nofollow noopener">Check out Extendly &rarr;</a>
      <p style="font-size:.75rem;color:var(--text3);margin-top:14px;margin-bottom:0">Affiliate disclosure: if you sign up through this link, globalhighlevel.com may earn a commission at no extra cost to you.</p>
    </div>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">GoHighLevel Free Trial — Frequently Asked Questions</h2>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">How long is the GoHighLevel free trial?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">The standard GoHighLevel free trial is 14 days. Through GlobalHighLevel.com, you get an extended 30-day free trial — double the time to explore every feature.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Do I need a credit card for the GoHighLevel free trial?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">Yes, a card is required to start the trial: a ~$1 verification hold your bank releases, not a subscription charge. You pay nothing for 30 days and can cancel anytime.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">What do I get with the GoHighLevel free trial?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">Full access to GoHighLevel's CRM, funnel builder, email & SMS marketing, workflow automations, AI conversation bots, calendar booking, reputation management, and more. Nothing is locked during the trial.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">How much does GoHighLevel cost after the free trial?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">GoHighLevel starts at $97/month after the trial ends. You can cancel anytime during your 30-day free trial if it's not the right fit.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Is this GoHighLevel free trial legitimate?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">Yes. This is an official GoHighLevel extended trial offered through their affiliate program. You sign up directly on GoHighLevel's website with full access to all features.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">GoHighLevel 14-day trial vs 30-day trial — what's the difference?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">The features are identical. The only difference is time. The standard trial from gohighlevel.com gives you 14 days. Through this page, you get 30 days — enough time to set up funnels, migrate contacts, and see real results before deciding.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Can I extend beyond 30 days?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">No. 30 days is the full trial window. If you're close to a decision, contact support to discuss your specific use case. Plan accordingly.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">GHL vs HubSpot free—which for agencies?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">HubSpot is CRM-heavy and free forever but capped. GHL is built for agencies: funnel builder, SMS, sub-accounts, and automation without limits. If you're reselling or scaling a team, GHL may be a better fit. If you want just a CRM, HubSpot is an option.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">What if I cancel during the trial?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">You cancel. Your account closes. No charge. No follow-up emails pushing you back. You keep any work you built (funnels, landing pages, contacts) but can't access them after the trial ends unless you restart.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Do I get workflow automation features in the trial?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">Yes. Full access to workflow automation, conditional logic, SMS sequences, and AI-powered features on your plan tier. You can build automated lead qualification workflows immediately.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Can I migrate contacts and funnels in during the trial?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">Yes. Import CSV contacts, migrate landing pages from other builders, or connect your Stripe/payment processor. The trial is a full sandbox. Refer to the help center for migration documentation.</p>
    </div>
  </div>

  <div class="cta-end" style="margin-bottom:48px">
    <h3>Start Your GoHighLevel Free Trial</h3>
    <p>30 days full access. Cancel anytime. Set up your funnels, automations, and AI bots — and follow along with our <a href="/" style="color:var(--amber)">free tutorials</a>.</p>
    <a href="{AFFILIATE}&utm_campaign={campaign}-bottom" class="btn-amber" target="_blank" rel="nofollow noopener">Start Free 30-Day Trial &rarr;</a>
    <div class="fine">$0 for the first 30 days &middot; then $97/mo &middot; cancel anytime</div>
  </div>

  <div style="text-align:center;margin-bottom:32px">
    <p style="font-size:.85rem;color:var(--text2)">Looking for a discount? <a href="/blog/gohighlevel-free-trial-30-days-extended/" style="color:var(--amber)">See our GoHighLevel coupon code page</a> or <a href="/" style="color:var(--amber)">browse all GoHighLevel guides</a>.</p>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:32px">
    <p style="font-size:.8rem;color:var(--text3);line-height:1.7;text-align:center">Affiliate disclosure: If you sign up through the links on this page, GlobalHighLevel.com may earn a commission at no extra cost to you. We only recommend tools we use ourselves. Not affiliated with GoHighLevel LLC.</p>
  </div>

</div>
<script type="application/ld+json">{faq_schema}</script>
<script type="application/ld+json">{offer_schema}</script>"""

    html = base_html(
        title=f"{title} | {SITE_NAME}",
        description=description,
        canonical=canonical,
        body=body,
        noindex=True,  # /trial/ and /start/ are conversion surfaces, not search pages
    )
    write(PUBLIC_DIR / slug / "index.html", html)


def build_coupon_page():
    """Build SEO-optimized /coupon/ landing page targeting promo/discount keywords."""
    canonical = f"{SITE_URL}/coupon/"
    title = "GoHighLevel Coupon Code 2026 — 30 Days Free"
    description = "Looking for a GoHighLevel coupon code or promo code? Get a 30-day free trial instead of the standard 14 days. No discount code needed."

    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "Is there a GoHighLevel coupon code?",
                "acceptedAnswer": {"@type": "Answer", "text": "GoHighLevel doesn't offer traditional coupon codes or promo codes. Instead, you can get an extended 30-day free trial through affiliate partners like GlobalHighLevel.com — double the standard 14-day trial. No code needed."}
            },
            {
                "@type": "Question",
                "name": "How do I get a GoHighLevel discount?",
                "acceptedAnswer": {"@type": "Answer", "text": "The best GoHighLevel discount is the extended 30-day free trial. That's 16 extra free days compared to signing up directly. After the trial, plans start at $97/month. There are no publicly available coupon codes or promo codes."}
            },
            {
                "@type": "Question",
                "name": "Does GoHighLevel have a promo code for 2026?",
                "acceptedAnswer": {"@type": "Answer", "text": "There is no GoHighLevel promo code for 2026. GoHighLevel runs its discounts through extended trial offers via affiliate partners. Through this page, you get 30 days free instead of 14 — the best deal currently available."}
            },
            {
                "@type": "Question",
                "name": "Can I get GoHighLevel cheaper than $97/month?",
                "acceptedAnswer": {"@type": "Answer", "text": "GoHighLevel starts at $97/month and there are no publicly available coupon codes to reduce that. The best way to save is by starting with the extended 30-day free trial to make sure it's the right fit before paying anything."}
            },
            {
                "@type": "Question",
                "name": "What is the best GoHighLevel deal right now?",
                "acceptedAnswer": {"@type": "Answer", "text": "The best deal is the extended 30-day free trial — double the standard 14 days. Full access to every feature, cancel anytime, and you pay $0 for a full month (a card is required to start, just a ~$1 verification hold, not a subscription charge). This is better than any coupon code."}
            }
        ]
    })

    body = f"""
<div class="post-container" style="max-width:740px;padding-top:100px">

  <div class="fade-1" style="text-align:center;margin-bottom:48px">
    <p style="font-size:.82rem;color:var(--text3);margin-bottom:24px">Already know you want in? <a href="{AFFILIATE}&utm_campaign=coupon-page-skip" target="_blank" rel="nofollow noopener" style="color:var(--amber)">Go straight to GoHighLevel &rarr;</a></p>
    <p style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:16px">Better Than a Coupon</p>
    <h1 style="font-family:var(--sans);font-size:clamp(2rem,4vw,3.2rem);font-weight:800;line-height:1.15;color:var(--text);letter-spacing:-.5px;margin-bottom:20px">GoHighLevel Coupon Code 2026</h1>
    <p style="font-size:1.15rem;color:var(--text2);line-height:1.7;max-width:580px;margin:0 auto 12px">There's no GoHighLevel coupon code or promo code. But there's something better:</p>
    <p style="font-size:1.3rem;font-weight:800;color:var(--text);margin-bottom:28px">30 days free instead of 14 &mdash; no code needed.</p>
    <a href="{AFFILIATE}&utm_campaign=coupon-page-hero" class="btn-amber" style="font-size:1rem;padding:14px 36px" target="_blank" rel="nofollow noopener">Start Your 30-Day Free Trial &rarr;</a>
    <p style="font-size:.8rem;color:var(--text3);margin-top:12px">$0 for 30 days &middot; No coupon code needed &middot; Cancel anytime</p>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px" class="fade-2">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">Why There's No GoHighLevel Coupon Code</h2>
    <p style="font-size:1.05rem;color:var(--text2);line-height:1.75;margin-bottom:20px">GoHighLevel doesn't typically offer coupon codes, promo codes, or discount codes. Instead, they run promotions through extended trial offers.</p>
    <p style="font-size:1.05rem;color:var(--text2);line-height:1.75;margin-bottom:20px">Instead, GoHighLevel offers <strong style="color:var(--text)">extended free trials</strong> through affiliate partners. The standard trial on gohighlevel.com is 14 days. Through this page, you get <strong style="color:var(--text)">30 days free</strong> — that's 16 extra days at no cost.</p>
    <p style="font-size:1.05rem;color:var(--text2);line-height:1.75">No code to enter. No checkout trick. Just click the link and your 30-day trial starts automatically.</p>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px" class="fade-2">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">30-Day Free Trial vs Coupon Code — The Math</h2>
    <div class="coupon-compare" style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:24px;text-align:center">
        <div style="font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text3);margin-bottom:12px">Typical Coupon Code</div>
        <div style="font-size:2rem;font-weight:800;color:var(--text3);margin-bottom:8px;text-decoration:line-through">10-20% off</div>
        <p style="font-size:.85rem;color:var(--text3);line-height:1.6;margin:0">Saves $10-19 on first month. Still pay $78-87 immediately. 14-day trial only.</p>
      </div>
      <div style="background:var(--surface);border:1px solid var(--amber-border);border-radius:8px;padding:24px;text-align:center">
        <div style="font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:12px">Extended Free Trial</div>
        <div style="font-size:2rem;font-weight:800;color:var(--amber);margin-bottom:8px">$0 for 30 days</div>
        <p style="font-size:.85rem;color:var(--text2);line-height:1.6;margin:0">Pay nothing for a full month. Full access to every feature. Cancel anytime.</p>
      </div>
    </div>
    <p style="font-size:.95rem;color:var(--text2);line-height:1.7;margin-top:20px;text-align:center">Even a 20% coupon code only saves ~$19. The extended trial gives you <strong style="color:var(--text)">16 extra free days</strong> — more time to build before you pay anything.</p>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">What You Get During the GHL Free Trial</h2>
    <div class="coupon-features" style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div style="padding:14px 18px;border:1px solid var(--border);border-radius:6px">
        <span style="font-size:.85rem;color:var(--text)">CRM &amp; Pipeline Management</span>
      </div>
      <div style="padding:14px 18px;border:1px solid var(--border);border-radius:6px">
        <span style="font-size:.85rem;color:var(--text)">Funnel &amp; Website Builder</span>
      </div>
      <div style="padding:14px 18px;border:1px solid var(--border);border-radius:6px">
        <span style="font-size:.85rem;color:var(--text)">Email &amp; SMS Marketing</span>
      </div>
      <div style="padding:14px 18px;border:1px solid var(--border);border-radius:6px">
        <span style="font-size:.85rem;color:var(--text)">Workflow Automations</span>
      </div>
      <div style="padding:14px 18px;border:1px solid var(--border);border-radius:6px">
        <span style="font-size:.85rem;color:var(--text)">AI Conversation Bots</span>
      </div>
      <div style="padding:14px 18px;border:1px solid var(--border);border-radius:6px">
        <span style="font-size:.85rem;color:var(--text)">Calendar &amp; Booking</span>
      </div>
      <div style="padding:14px 18px;border:1px solid var(--border);border-radius:6px">
        <span style="font-size:.85rem;color:var(--text)">Reputation Management</span>
      </div>
      <div style="padding:14px 18px;border:1px solid var(--border);border-radius:6px">
        <span style="font-size:.85rem;color:var(--text)">White-Label SaaS Mode</span>
      </div>
    </div>
    <p style="font-size:.85rem;color:var(--text3);margin-top:14px;text-align:center">Explore all of these during your 30-day GHL free trial.</p>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">GoHighLevel Pricing After the Trial</h2>
    <div style="background:var(--surface);border:1px solid var(--amber-border);border-radius:8px;padding:28px;text-align:center">
      <p style="font-size:.85rem;color:var(--text2);margin-bottom:8px">GoHighLevel plans start at</p>
      <div style="font-size:2.5rem;font-weight:800;color:var(--text);margin-bottom:8px">$97<span style="font-size:1rem;color:var(--text3)">/month</span></div>
      <p style="font-size:.9rem;color:var(--text2);margin:0">But you pay <strong style="color:var(--amber)">$0 for the first 30 days</strong> with the extended trial. No coupon code or promo code will beat that.</p>
    </div>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">GoHighLevel Coupon Code FAQ</h2>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Is there a GoHighLevel coupon code?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">GoHighLevel doesn't offer traditional coupon codes or promo codes. Instead, you can get an extended <strong style="color:var(--text)">30-day free trial</strong> through affiliate partners like GlobalHighLevel.com — double the standard 14-day trial. No code needed.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">How do I get a GoHighLevel discount?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">The best GoHighLevel discount is the extended 30-day free trial. That's 16 extra free days compared to signing up directly. After the trial, plans start at $97/month. There are no publicly available coupon codes or promo codes.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Does GoHighLevel have a promo code for 2026?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">There is no GoHighLevel promo code for 2026. GoHighLevel runs its discounts through extended trial offers via affiliate partners. Through this page, you get 30 days free instead of 14 — the best deal currently available.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Can I get GoHighLevel cheaper than $97/month?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">GoHighLevel starts at $97/month and there are no publicly available coupon codes to reduce that. The best way to save is by starting with the extended 30-day free trial to make sure it's the right fit before paying anything.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">What is the best GoHighLevel deal right now?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">The best deal is the extended 30-day free trial — double the standard 14 days. Full access to every feature, cancel anytime, and you pay <strong style="color:var(--text)">$0 for a full month</strong> (a card is required to start — just a ~$1 verification hold, not a subscription charge). Better than any coupon code.</p>
    </div>
  </div>

  <div class="cta-end" style="margin-bottom:48px">
    <h3>Skip the Coupon Code &mdash; Get 30 Days Free</h3>
    <p>No promo code, no discount code, no checkout tricks. Just a full month of GoHighLevel at $0. Follow along with our <a href="/" style="color:var(--amber)">free tutorials</a> while you build.</p>
    <a href="{AFFILIATE}&utm_campaign=coupon-page-bottom" class="btn-amber" target="_blank" rel="nofollow noopener">Start Free 30-Day Trial &rarr;</a>
    <div class="fine">$0 for the first 30 days &middot; then $97/mo &middot; cancel anytime</div>
  </div>

  <div style="text-align:center;margin-bottom:32px">
    <p style="font-size:.85rem;color:var(--text2)">Looking for tutorials instead? <a href="/blog/gohighlevel-free-trial-30-days-extended/" style="color:var(--amber)">Learn more about the free trial</a> or <a href="/" style="color:var(--amber)">browse all GoHighLevel guides</a>.</p>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:32px">
    <p style="font-size:.8rem;color:var(--text3);line-height:1.7;text-align:center">Affiliate disclosure: If you sign up through the links on this page, GlobalHighLevel.com may earn a commission at no extra cost to you. We only recommend tools we use ourselves. Not affiliated with GoHighLevel LLC.</p>
  </div>

</div>
<script type="application/ld+json">{faq_schema}</script>"""

    html = base_html(
        title=f"{title} | {SITE_NAME}",
        description=description,
        canonical=canonical,
        body=body
    )
    write(PUBLIC_DIR / "coupon" / "index.html", html)


def build_services_page():
    """Build /services/ page — a la carte AI automation services."""
    canonical = f"{SITE_URL}/services/"
    title = "GoHighLevel Automation Services — $497/mo"
    description = "AI automation systems built inside GoHighLevel. Content pipelines, lead follow-up, appointment setting, SEO engines, and more. A la carte, no contracts."

    WEBHOOK_URL = "https://services.leadconnectorhq.com/hooks/VL5PlkLBYG4mKk3N6PGw/webhook-trigger/98cc6f29-7cee-4b59-845f-8908cdbe9575"

    services = [
        {
            "name": "AI Content Pipeline",
            "desc": "Automated blog posts and podcast episodes generated from your existing content, published on autopilot.",
            "includes": "Source scraping, AI audio generation, transcription, SEO blog posts, podcast distribution",
        },
        {
            "name": "SEO Engine",
            "desc": "Google Search Console monitoring with auto-generated topics, landing pages, and content gap analysis.",
            "includes": "GSC integration, keyword tracking, auto-generated pages, 28-day optimization cycles",
        },
        {
            "name": "AI Lead Follow-Up",
            "desc": "Claude-powered SMS and email sequences that respond intelligently to inbound leads. Opt-in only.",
            "includes": "AI conversation flows, smart nurture sequences, re-engagement campaigns, CRM tagging",
        },
        {
            "name": "AI Appointment Setter",
            "desc": "Conversation bot that qualifies leads and books calls on your calendar — no human needed.",
            "includes": "GHL Agent Studio setup, calendar integration, qualification logic, handoff workflows",
        },
        {
            "name": "Direct Mail Campaigns",
            "desc": "AI-written postcards and letters with multi-touch sequences that drive inbound responses.",
            "includes": "6-touch campaign copywriting, QR tracking, CRM integration, follow-up automation",
        },
        {
            "name": "CRM Setup &amp; Workflow Automation",
            "desc": "Pipelines, triggers, and workflows configured to automate your entire client journey.",
            "includes": "Pipeline design, workflow automation, tagging logic, reporting dashboards",
        },
        {
            "name": "Multi-Location SEO Pages",
            "desc": "Hundreds of geo-targeted landing pages generated at scale for local service businesses.",
            "includes": "Dynamic page generation, local schema markup, city/county targeting, sitemap automation",
        },
        {
            "name": "Reputation Management",
            "desc": "Automated review requests after jobs, AI-written responses, and Google review monitoring.",
            "includes": "Review request workflows, AI response drafting, sentiment tracking, review widgets",
        },
    ]

    services_html = ""
    for s in services:
        services_html += f"""
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:24px;transition:border-color .2s">
        <div style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">{s['name']}</div>
        <p style="font-size:.9rem;color:var(--text2);line-height:1.65;margin-bottom:12px">{s['desc']}</p>
        <p style="font-size:.78rem;color:var(--text3);line-height:1.6;margin:0"><strong style="color:var(--text2)">Includes:</strong> {s['includes']}</p>
      </div>"""

    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "How much do GoHighLevel automation services cost?",
                "acceptedAnswer": {"@type": "Answer", "text": "Each automation system is $497/month plus API usage at 6x cost. Pick only the systems you need — no bundles, no contracts. API usage covers Claude, Gemini, and other AI services powering your automations."}
            },
            {
                "@type": "Question",
                "name": "Do you do unsolicited outbound SMS?",
                "acceptedAnswer": {"@type": "Answer", "text": "No. All SMS and email automation is opt-in only. We don't support cold outreach, skip-traced lists, or unsolicited messaging. This protects your numbers from being banned and keeps you compliant with TCPA and A2P 10DLC regulations. Read more at globalhighlevel.com/blog/unsolicited-sms-gohighlevel-compliance-risk/"}
            },
            {
                "@type": "Question",
                "name": "What AI tools do you use for GoHighLevel automation?",
                "acceptedAnswer": {"@type": "Answer", "text": "We use Claude (Anthropic) for intelligent conversations, copywriting, and decision-making. Gemini for transcription and content processing. NotebookLM for podcast generation. All integrated directly into your GoHighLevel account."}
            },
            {
                "@type": "Question",
                "name": "How long does setup take?",
                "acceptedAnswer": {"@type": "Answer", "text": "Most systems are live within 3-5 business days. Complex multi-system setups may take 1-2 weeks. We use AI to accelerate the build process so you are not waiting months for delivery."}
            },
            {
                "@type": "Question",
                "name": "Do I need a GoHighLevel account?",
                "acceptedAnswer": {"@type": "Answer", "text": "Yes. We build inside your GHL account so you own everything. Don't have one yet? Start a 30-day free trial at globalhighlevel.com/trial and we'll set up your first system during the trial period."}
            }
        ]
    })

    service_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Service",
        "name": "GoHighLevel AI Automation Services",
        "description": "Done-for-you AI automation systems built inside GoHighLevel. Content pipelines, lead follow-up, appointment setting, SEO engines, and more.",
        "provider": {"@type": "Organization", "name": "GlobalHighLevel", "url": SITE_URL},
        "url": canonical,
        "offers": {
            "@type": "Offer",
            "price": "497",
            "priceCurrency": "USD",
            "description": "Per automation system per month, plus API usage"
        }
    })

    body = f"""
<div class="post-container" style="max-width:780px;padding-top:100px">

  <div class="fade-1" style="text-align:center;margin-bottom:48px">
    <p style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--amber);margin-bottom:16px">AI Automation Services</p>
    <h1 style="font-family:var(--sans);font-size:clamp(2rem,4vw,3rem);font-weight:800;line-height:1.15;color:var(--text);letter-spacing:-.5px;margin-bottom:20px">GoHighLevel Automation Services — AI Systems That Run Your Business</h1>
    <p style="font-size:1.1rem;color:var(--text2);line-height:1.7;max-width:600px;margin:0 auto 16px">Pick the automations you need. We build them inside your GHL account. They run 24/7. You pay monthly.</p>
    <p style="font-size:1.3rem;font-weight:800;color:var(--text);margin-bottom:8px">$497/mo per system + API usage</p>
    <p style="font-size:.85rem;color:var(--text3)">API usage billed at 6x cost &middot; No contracts &middot; Cancel anytime</p>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px" class="fade-2">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:8px">GHL Automation Services — Pick What You Need</h2>
    <p style="font-size:.9rem;color:var(--text3);margin-bottom:24px">Each system is $497/mo. Pick one, pick all eight. No bundles, no upsells.</p>
    <div class="services-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
{services_html}
    </div>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">How It Works</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px" class="services-steps">
      <div style="text-align:center">
        <div style="font-size:2rem;font-weight:800;color:var(--amber);margin-bottom:8px">1</div>
        <div style="font-size:.9rem;font-weight:700;color:var(--text);margin-bottom:6px">You Pick</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">Choose the automations you need from the menu above.</p>
      </div>
      <div style="text-align:center">
        <div style="font-size:2rem;font-weight:800;color:var(--amber);margin-bottom:8px">2</div>
        <div style="font-size:.9rem;font-weight:700;color:var(--text);margin-bottom:6px">We Build</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">We set everything up inside your GoHighLevel account. Live in 3-5 days.</p>
      </div>
      <div style="text-align:center">
        <div style="font-size:2rem;font-weight:800;color:var(--amber);margin-bottom:8px">3</div>
        <div style="font-size:.9rem;font-weight:700;color:var(--text);margin-bottom:6px">It Runs</div>
        <p style="font-size:.82rem;color:var(--text2);line-height:1.6;margin:0">Your systems run 24/7. You pay monthly. Cancel anytime.</p>
      </div>
    </div>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">GoHighLevel Consulting &amp; Setup Pricing</h2>
    <div style="background:var(--surface);border:1px solid var(--amber-border);border-radius:8px;padding:32px;text-align:center;margin-bottom:20px">
      <div style="font-size:2.5rem;font-weight:800;color:var(--text)">$497<span style="font-size:1rem;color:var(--text3)">/mo per system</span></div>
      <p style="font-size:.95rem;color:var(--text2);margin:12px 0 0">+ API usage at 6x cost (typically $30-150/mo depending on volume)</p>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px" class="services-pricing">
      <div style="padding:16px;border:1px solid var(--border);border-radius:6px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:4px">1 system</div>
        <div style="font-size:.82rem;color:var(--text2)">$497/mo + API</div>
      </div>
      <div style="padding:16px;border:1px solid var(--border);border-radius:6px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:4px">3 systems</div>
        <div style="font-size:.82rem;color:var(--text2)">$1,491/mo + API</div>
      </div>
      <div style="padding:16px;border:1px solid var(--border);border-radius:6px">
        <div style="font-size:.85rem;font-weight:700;color:var(--text);margin-bottom:4px">5 systems</div>
        <div style="font-size:.82rem;color:var(--text2)">$2,485/mo + API</div>
      </div>
      <div style="padding:16px;border:1px solid var(--border);border-radius:8px;border-color:var(--amber-border)">
        <div style="font-size:.85rem;font-weight:700;color:var(--amber);margin-bottom:4px">All 8 systems</div>
        <div style="font-size:.82rem;color:var(--text2)">$3,976/mo + API</div>
      </div>
    </div>
    <p style="font-size:.8rem;color:var(--text3);text-align:center;margin-top:14px">No setup fees &middot; No contracts &middot; Cancel any system anytime</p>
  </div>

  <div style="background:var(--surface);border:1px solid var(--amber-border);border-radius:8px;padding:24px;margin-bottom:48px">
    <div style="display:flex;align-items:flex-start;gap:12px">
      <div style="font-size:1.2rem;line-height:1">&#9888;</div>
      <div>
        <div style="font-size:.9rem;font-weight:700;color:var(--text);margin-bottom:6px">Opt-In Only — No Unsolicited SMS</div>
        <p style="font-size:.85rem;color:var(--text2);line-height:1.65;margin:0">All SMS and email automation we build is <strong style="color:var(--text)">opt-in only</strong>. We do not support cold outreach, skip-traced lists, or unsolicited messaging. This protects your phone numbers from being banned and keeps you compliant with TCPA and A2P 10DLC regulations. <a href="/blog/unsolicited-sms-gohighlevel-compliance-risk/" style="color:var(--amber)">Read why this matters &rarr;</a></p>
      </div>
    </div>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:24px">GoHighLevel Setup Service FAQ</h2>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">How much do GoHighLevel automation services cost?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">Each automation system is $497/month plus API usage at 6x cost. Pick only the systems you need — no bundles, no contracts. API usage covers Claude, Gemini, and other AI services powering your automations.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Do you do unsolicited outbound SMS?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">No. All SMS and email automation is opt-in only. We don't support cold outreach, skip-traced lists, or unsolicited messaging. This protects your numbers from being banned and keeps you compliant with TCPA and A2P 10DLC regulations. <a href="/blog/unsolicited-sms-gohighlevel-compliance-risk/" style="color:var(--amber)">Read why this matters</a>.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">What AI tools do you use?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">We use Claude (Anthropic) for intelligent conversations, copywriting, and decision-making. Gemini for transcription and content processing. NotebookLM for podcast generation. All integrated directly into your GoHighLevel account.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">How long does setup take?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">Most systems are live within 3-5 business days. Complex multi-system setups may take 1-2 weeks. We use AI to accelerate the build process so you're not waiting months for delivery.</p>
    </div>

    <div style="margin-bottom:24px">
      <h3 style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px">Do I need a GoHighLevel account?</h3>
      <p style="font-size:.95rem;color:var(--text2);line-height:1.7">Yes. We build inside your GHL account so you own everything. Don't have one yet? <a href="/blog/gohighlevel-free-trial-30-days-extended/" style="color:var(--amber)">Start a 30-day free trial</a> and we'll set up your first system during the trial period.</p>
    </div>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:48px;margin-bottom:48px" id="contact">
    <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:8px">Get Started</h2>
    <p style="font-size:.9rem;color:var(--text2);margin-bottom:24px">Tell us what you need. We'll get back to you within 24 hours.</p>
    <form id="services-form" style="display:flex;flex-direction:column;gap:16px">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px" class="form-row">
        <div>
          <label style="font-size:.78rem;font-weight:600;color:var(--text2);display:block;margin-bottom:6px">First Name</label>
          <input type="text" name="firstName" required style="width:100%;padding:10px 14px;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.9rem;font-family:var(--sans)">
        </div>
        <div>
          <label style="font-size:.78rem;font-weight:600;color:var(--text2);display:block;margin-bottom:6px">Last Name</label>
          <input type="text" name="lastName" required style="width:100%;padding:10px 14px;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.9rem;font-family:var(--sans)">
        </div>
      </div>
      <div>
        <label style="font-size:.78rem;font-weight:600;color:var(--text2);display:block;margin-bottom:6px">Email</label>
        <input type="email" name="email" required style="width:100%;padding:10px 14px;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.9rem;font-family:var(--sans)">
      </div>
      <div>
        <label style="font-size:.78rem;font-weight:600;color:var(--text2);display:block;margin-bottom:6px">Phone</label>
        <input type="tel" name="phone" style="width:100%;padding:10px 14px;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.9rem;font-family:var(--sans)">
      </div>
      <div>
        <label style="font-size:.78rem;font-weight:600;color:var(--text2);display:block;margin-bottom:6px">Which systems are you interested in?</label>
        <textarea name="services" rows="3" placeholder="e.g. AI Content Pipeline, AI Lead Follow-Up, CRM Setup" style="width:100%;padding:10px 14px;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.9rem;font-family:var(--sans);resize:vertical"></textarea>
      </div>
      <div>
        <label style="font-size:.78rem;font-weight:600;color:var(--text2);display:block;margin-bottom:6px">Tell us about your business</label>
        <textarea name="message" rows="3" placeholder="What industry, how many leads/mo, what are you trying to automate?" style="width:100%;padding:10px 14px;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.9rem;font-family:var(--sans);resize:vertical"></textarea>
      </div>
      <button type="submit" class="btn-amber" style="width:100%;text-align:center;padding:14px;font-size:.95rem;border:none;cursor:pointer">Send Inquiry &rarr;</button>
      <div id="form-status" style="font-size:.85rem;text-align:center;display:none"></div>
    </form>
  </div>

  <div style="text-align:center;margin-bottom:32px">
    <p style="font-size:.85rem;color:var(--text2)">Not ready for services? <a href="/blog/gohighlevel-free-trial-30-days-extended/" style="color:var(--amber)">Start a free 30-day GHL trial</a>, check our <a href="/blog/gohighlevel-free-trial-30-days-extended/" style="color:var(--amber)">coupon page</a>, or explore our <a href="/" style="color:var(--amber)">free tutorials</a>.</p>
  </div>

  <div style="border-top:1px solid var(--border);padding-top:32px">
    <p style="font-size:.8rem;color:var(--text3);line-height:1.7;text-align:center">GlobalHighLevel.com is an independent automation consultancy. We are not affiliated with GoHighLevel LLC or Anthropic. GoHighLevel is a registered trademark of HighLevel Inc.</p>
  </div>

</div>
<script type="application/ld+json">{faq_schema}</script>
<script type="application/ld+json">{service_schema}</script>
<script>
(function(){{
  var form=document.getElementById('services-form');
  var status=document.getElementById('form-status');
  if(!form)return;
  form.addEventListener('submit',function(e){{
    e.preventDefault();
    var data={{}};
    new FormData(form).forEach(function(v,k){{data[k]=v}});
    status.style.display='block';
    status.style.color='var(--text2)';
    status.textContent='Sending...';
    fetch('{WEBHOOK_URL}',{{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify(data)
    }}).then(function(r){{
      if(r.ok){{
        status.style.color='var(--amber)';
        status.textContent='Sent! We\\'ll be in touch within 24 hours.';
        form.reset();
      }}else{{
        status.style.color='#ef4444';
        status.textContent='Something went wrong. Email us instead.';
      }}
    }}).catch(function(){{
      status.style.color='#ef4444';
      status.textContent='Something went wrong. Email us instead.';
    }});
  }});
}})();
</script>"""

    html = base_html(
        title=f"{title} | {SITE_NAME}",
        description=description,
        canonical=canonical,
        body=body
    )
    write(PUBLIC_DIR / "services" / "index.html", html)


def build_about_page(total_posts: int = 0):
    """Build /about/ page — E-E-A-T authority page for author."""
    canonical = f"{SITE_URL}/about/"
    title = "About William Welch — GoHighLevel Consultant | GlobalHighLevel"
    description = "William Welch helps agencies automate with GoHighLevel. 300+ tutorials, a top GHL podcast, and hands-on experience building automations for agencies worldwide."

    person_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "mainEntity": {
            "@type": "Person",
            "name": "William Welch",
            "jobTitle": "GoHighLevel Consultant & Agency Automation Specialist",
            "url": canonical,
            "sameAs": [
                "https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV"
            ],
            "worksFor": {
                "@type": "Organization",
                "name": "REI Amplifi",
                "url": "https://reiamplifi.com"
            },
            "knowsAbout": [
                "GoHighLevel", "CRM automation", "agency operations",
                "WhatsApp marketing", "AI agents", "workflow automation",
                "email deliverability", "SaaS platforms"
            ]
        }
    })

    body = f"""
<article class="post-content" style="padding-top:140px;max-width:720px;margin:0 auto">
  <div class="post-eyebrow"><a href="/">Home</a> &rsaquo; About</div>
  <h1 style="font-family:var(--sans);font-size:clamp(2rem,4vw,3rem);font-weight:800;line-height:1.15;letter-spacing:-.5px;margin-bottom:16px">About William Welch</h1>
  <div class="author-role" style="font-size:1rem;color:var(--amber);margin-bottom:32px;font-weight:600">GoHighLevel Consultant &amp; Agency Automation Specialist</div>

  <h2>What I Do</h2>
  <p>I help digital marketing agencies stop paying for 5-10 disconnected tools and move everything into GoHighLevel. CRM, email, SMS, WhatsApp, funnels, calendars, AI agents, payments — one platform, fully automated.</p>
  <p>I've built GoHighLevel systems for agencies across the US, India, and Latin America — from solo operators to teams managing 50+ sub-accounts. If it can be automated in GHL, I've probably built it.</p>

  <h2>Why I Built This Site</h2>
  <p>GoHighLevel is powerful but the learning curve is real. The official docs cover features — they don't show you how to actually set things up for your specific business.</p>
  <p>GlobalHighLevel.com is where I publish everything I learn. Every tutorial comes from real implementation work, not theory. When I figure out how to solve a problem in GHL, I write it up so you don't have to waste the same hours I did.</p>

  <h2>By the Numbers</h2>
  <ul>
    <li><strong>{total_posts}+ published tutorials</strong> covering every major GHL feature</li>
    <li><strong>Go High Level podcast</strong> — <a href="https://open.spotify.com/show/28LLaXVbmnHUMNBFGdgdlV" target="_blank" rel="noopener">380+ followers on Spotify</a>, 6,400+ total streams</li>
    <li><strong>10 content categories</strong> — from AI &amp; Automation to international markets (India, Latin America)</li>
    <li><strong>Built from real work</strong> — tutorials, podcast episodes, and guides from hands-on GoHighLevel implementation, not theory</li>
  </ul>

  <h2>My Approach</h2>
  <p>Every piece of content on this site follows three rules:</p>
  <ol>
    <li><strong>Based on real usage</strong> — I only write about features I've actually configured and tested</li>
    <li><strong>Fact-checked</strong> — every tutorial runs through an automated fact-checking agent before publishing</li>
    <li><strong>Actionable</strong> — step-by-step instructions you can follow inside your GHL account right now</li>
  </ol>

  <h2>Work With Me</h2>
  <p>If you need hands-on help setting up GoHighLevel for your agency, I offer consulting and implementation services through <a href="https://reiamplifi.com" target="_blank" rel="noopener">REI Amplifi</a>.</p>

  <div class="cta-end" style="margin-top:48px">
    <h3>Try GoHighLevel Free</h3>
    <p>30 days free — double the standard 14-day trial. $0 to start (just a ~$1 card-verification hold).</p>
    <a href="{AFFILIATE}&utm_campaign=about" class="btn-amber" target="_blank" rel="nofollow noopener">Start Free 30-Day Trial</a>
  </div>
</article>
<script type="application/ld+json">{person_schema}</script>"""

    html = base_html(title, description, canonical, body)
    write(PUBLIC_DIR / "about" / "index.html", html)


def build_404():
    body = f"""
<div style="text-align:center;padding:160px 24px 100px">
  <h1 style="font-family:var(--sans);font-size:5rem;font-weight:800;color:var(--amber);margin-bottom:8px">404</h1>
  <h2 style="font-family:var(--sans);font-size:1.5rem;font-weight:700;margin-bottom:16px;color:var(--text)">Page Not Found</h2>
  <p style="color:var(--text3);margin-bottom:32px">The page you're looking for doesn't exist.</p>
  <a href="/" class="btn-amber">Go Home</a>
</div>"""
    html = base_html("404 — Page Not Found | Global High Level", "Page not found.", f"{SITE_URL}/404", body)
    write(PUBLIC_DIR / "404.html", html)


# ── Language hub + topic pages ────────────────────────────────────────────────

def build_language_hub(lang_config: dict, posts: list[dict], per_page: int = 18):
    """Build a language hub page (e.g., /es/, /in/, /ar/) with paginated posts."""
    prefix = lang_config["prefix"]
    lang_code = lang_config["code"]
    lang_name = lang_config["native"]
    text_dir = lang_config.get("dir", "ltr")

    # Filter posts for this language — post_lang() (slug-aware), not the raw
    # field, so the 469 unlabeled posts are routed to the right hub instead of
    # defaulting to English and getting orphaned. 2026-05-23 cliff fix.
    lang_posts = [p for p in posts if post_lang(p) == lang_code]
    if not lang_posts:
        print(f"  Skipping {lang_name} hub — no posts")
        return

    lang_posts.sort(key=lambda x: x.get("publishedAt", x.get("uploadedAt", "")), reverse=True)

    # Build topic filter chips (keyed on TOPIC, T3 — not back-compat category)
    topic_counts = {}
    for p in lang_posts:
        cat = post_topic(p)
        topic_counts[cat] = topic_counts.get(cat, 0) + 1

    chips_html = f'<a href="{prefix}/" class="chip chip-active">All ({len(lang_posts)})</a>'
    for c in CATEGORIES:
        count = topic_counts.get(c["name"], 0)
        # Only link categories that ACTUALLY get a page. build_language_topic_pages
        # skips any category with < min_posts (2) in this language, so linking a
        # single-post topic here is a guaranteed 404 (T5 / codex P2). The post still
        # surfaces in the hub's "All" list, so it's not orphaned.
        if count >= 2:
            chips_html += f' <a href="{prefix}/category/{c["slug"]}/" class="chip">{c["name"]} ({count})</a>'

    total_pages = max(1, -(-len(lang_posts) // per_page))
    for page in range(1, total_pages + 1):
        start = (page - 1) * per_page
        page_posts = lang_posts[start:start + per_page]

        cards_html = ""
        for p in page_posts:
            slug = p.get("slug", "")
            title = p.get("title", p.get("seoTitle", "Untitled"))
            desc = truncate(p.get("description", p.get("seoDescription", p.get("meta_description", ""))), 130)
            date_str = fmt_date(p.get("publishedAt", p.get("uploadedAt", "")))
            rtime = read_time(p.get("html_content", desc))
            cat_raw = post_topic(p)
            cat_label = display_cat(cat_raw)
            if not cat_label:
                cat_html = ""
            elif topic_counts.get(cat_raw, 0) >= 2:
                cat_html = f'<a href="{prefix}/category/{slugify(cat_label)}/" class="card-cat">{cat_label}</a>'
            else:
                # Single-post topic in this language has no category page (min_posts=2);
                # fall back to the language hub so the badge isn't a 404 (T5 / codex P2).
                cat_html = f'<a href="{prefix}/" class="card-cat">{cat_label}</a>'
            cards_html += f"""
<article class="card">
  {cat_html}
  <h2 class="card-title"><a href="{post_url(p)}">{title}</a></h2>
  <p class="card-excerpt">{desc}</p>
  <div class="card-meta"><span>{date_str}</span>{"<span class='meta-sep'>&middot;</span><span>" + rtime + "</span>" if date_str else ""}</div>
</article>"""

        # Pagination
        pag_html = ""
        if total_pages > 1:
            pag_html = '<div class="pagination">'
            for pg in range(1, total_pages + 1):
                href = f"{prefix}/" if pg == 1 else f"{prefix}/page/{pg}/"
                cls = ' class="active"' if pg == page else ""
                pag_html += f' <a href="{href}"{cls}>{pg}</a>'
            pag_html += "</div>"

        if page == 1 and lang_code == "es":
            money_url = "/blog/gohighlevel-precios-planes-2026-guia-completa/"
            body = f"""
<header class="hh"><div class="container">
  <h1>Todo sobre <em>GoHighLevel</em> &mdash; gu&iacute;as en espa&ntilde;ol y precios claros.</h1>
  <p class="sub">GlobalHighLevel es la biblioteca gratuita para configurar GoHighLevel correctamente &mdash; tutoriales reales de gente que lo usa de verdad, los <b>precios sin letra chica</b> y la prueba extendida de 30 d&iacute;as. Empieza por la gu&iacute;a completa de precios.</p>
  <a class="guidecard" href="{money_url}">
    <div class="gc-ic">&#9733;</div>
    <div>
      <div class="gc-k">Nuestra gu&iacute;a m&aacute;s le&iacute;da</div>
      <div class="gc-t">Precios de GoHighLevel 2026: cu&aacute;nto cuesta y si es gratis</div>
      <div class="gc-d">Planes, el precio real desde $97, la prueba de 30 d&iacute;as y c&oacute;mo pagar menos.</div>
    </div>
    <span class="gc-arrow">Leer &rarr;</span>
  </a>
</div></header>
<section class="hubsec" id="guides"><div class="container">
  <span class="eyebrow">Cada tema de GoHighLevel</span>
  <h2>Configura GoHighLevel bien &mdash; por tema</h2>
  <p class="lead">La biblioteca completa, organizada. Elige el &aacute;rea en la que est&aacute;s trabajando.</p>
  <div class="clusters">
    <div class="cluster"><h3>WhatsApp y Captaci&oacute;n de Leads</h3><p>El canal #1 en espa&ntilde;ol &mdash; API de WhatsApp Business, conectar GHL con WhatsApp y respuesta autom&aacute;tica a cada lead.</p><a class="cl" href="/es/category/agency-platform/">Explorar gu&iacute;as &rarr;</a></div>
    <div class="cluster"><h3>Automatizaci&oacute;n y Agentes IA</h3><p>Pon la plataforma en piloto autom&aacute;tico &mdash; workflows, seguimiento de leads y agentes con IA.</p><a class="cl" href="/blog/como-configurar-primera-automatizacion-gohighlevel-paso-a-paso/">Explorar gu&iacute;as &rarr;</a></div>
    <div class="cluster"><h3>CRM y Comunicaci&oacute;n</h3><p>Maneja toda la relaci&oacute;n con el cliente en un solo lugar &mdash; CRM, email y SMS, tel&eacute;fono y calendario.</p><a class="cl" href="/es/category/agency-platform/">Explorar gu&iacute;as &rarr;</a></div>
    <div class="cluster"><h3>Sitios, Embudos y Reputaci&oacute;n</h3><p>Captura leads y proyecta confianza &mdash; sitios y embudos, formularios, rese&ntilde;as y reputaci&oacute;n.</p><a class="cl" href="/es/category/agency-platform/">Explorar gu&iacute;as &rarr;</a></div>
    <div class="cluster"><h3>Agencia, Marca Blanca y SaaS</h3><p>Revende GoHighLevel como tuyo &mdash; marca blanca, modo SaaS, sub-cuentas y reportes.</p><a class="cl" href="/blog/gohighlevel-latam-pagos-agencias/">Explorar gu&iacute;as &rarr;</a></div>
    <div class="cluster"><h3>Pagos y Precios</h3><p>Cobra dentro de GoHighLevel y conoce el costo real &mdash; MercadoPago y pasarelas para LATAM, m&aacute;s el desglose de precios.</p><a class="cl" href="/es/category/payments-pricing/">Explorar gu&iacute;as &rarr;</a></div>
  </div>
  <div class="es-banner">
    <div><b style="color:var(--text)">Prefer English?</b> <span style="color:var(--text2)">The full GoHighLevel guide library and the 30-day trial.</span></div>
    <a class="btn-amber" href="/" style="font-size:.85rem;padding:10px 18px">Go to the English site &rarr;</a>
  </div>
</div></section>"""
        else:
            body = f"""
<div class="cat-header">
  <div class="container">
    <div class="section-label fade-1" style="border-bottom:none;padding-bottom:0;margin-bottom:8px">{lang_name}</div>
    <h1 class="fade-2">GoHighLevel — {lang_name}</h1>
    <p class="fade-3">{len(lang_posts)} guides in {lang_name}</p>
    <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">{chips_html}</div>
  </div>
</div>
<div class="container">
  <div class="cards-grid" style="padding:32px 0 40px">{cards_html}</div>
  {pag_html}
</div>"""

        hub_descriptions = {
            "en": "Free GoHighLevel tutorials, guides, and strategies for digital marketing agencies and businesses worldwide. Step-by-step help.",
            "es": "Tutoriales y guías gratuitas de GoHighLevel en español. Aprende a configurar, automatizar y escalar tu agencia paso a paso.",
            "en-IN": "Free GoHighLevel tutorials and guides for Indian agencies. UPI payments, WhatsApp automation, and agency growth — step by step.",
        }
        hub_desc = hub_descriptions.get(lang_code, f"Free GoHighLevel tutorials and guides in {lang_name}.")
        canonical = f"{SITE_URL}{prefix}/" if page == 1 else f"{SITE_URL}{prefix}/page/{page}/"
        html = base_html(
            title=f"GoHighLevel {lang_name} | {SITE_NAME}",
            description=hub_desc,
            canonical=canonical,
            body=body,
            lang=lang_code,
            text_dir=text_dir,
            hreflang_path="",
        )
        if page == 1:
            write(PUBLIC_DIR / prefix.lstrip("/") / "index.html", html)
        else:
            write(PUBLIC_DIR / prefix.lstrip("/") / "page" / str(page) / "index.html", html)


def build_language_topic_pages(lang_config: dict, posts: list[dict], min_posts: int = 2):
    """Build topic pages within a language (e.g., /es/category/ai-automation/)."""
    prefix = lang_config["prefix"]
    lang_code = lang_config["code"]
    text_dir = lang_config.get("dir", "ltr")

    lang_posts = [p for p in posts if post_lang(p) == lang_code]

    by_topic = {}
    for p in lang_posts:
        # T3: key on TOPIC, not the back-compat `category`. post_topic() never
        # returns a language bucket, so the old "GoHighLevel en Español" bucket
        # pages are no longer generated — those URLs 301 to the /es/ /in/ hubs
        # (cliff-fix redirects). Topic pages here use the real 8 topics only.
        cat = post_topic(p)
        by_topic.setdefault(cat, []).append(p)

    for cat_name, cat_posts in by_topic.items():
        if len(cat_posts) < min_posts:
            continue

        cat_slug = slugify(cat_name)
        cat_config = next((c for c in CATEGORIES if c["slug"] == cat_slug), None)
        cat_desc = cat_config["description"] if cat_config else f"GoHighLevel {cat_name.lower()} guides."

        cat_posts.sort(key=lambda x: x.get("publishedAt", x.get("uploadedAt", "")), reverse=True)

        cards_html = ""
        for p in cat_posts:
            slug = p.get("slug", "")
            title = p.get("title", p.get("seoTitle", "Untitled"))
            desc = truncate(p.get("description", p.get("seoDescription", p.get("meta_description", ""))), 130)
            date_str = fmt_date(p.get("publishedAt", p.get("uploadedAt", "")))
            rtime = read_time(p.get("html_content", desc))
            cards_html += f"""
<article class="card">
  <h2 class="card-title"><a href="{post_url(p)}">{title}</a></h2>
  <p class="card-excerpt">{desc}</p>
  <div class="card-meta"><span>{date_str}</span>{"<span class='meta-sep'>&middot;</span><span>" + rtime + "</span>" if date_str else ""}</div>
</article>"""

        body = f"""
<div class="cat-header">
  <div class="container">
    <div class="section-label fade-1" style="border-bottom:none;padding-bottom:0;margin-bottom:8px">{lang_config['native']}</div>
    <h1 class="fade-2">{cat_name}</h1>
    <p class="fade-3">{cat_desc}</p>
    <p class="fade-3" style="font-size:.8rem;color:var(--text3);margin-top:6px">{len(cat_posts)} guides</p>
  </div>
</div>
<div class="container">
  <div class="cards-grid" style="padding:32px 0 80px">{cards_html}</div>
</div>"""

        canonical = f"{SITE_URL}{prefix}/category/{cat_slug}/"
        html = base_html(
            title=f"{cat_name} — {lang_config['native']} | {SITE_NAME}",
            description=f"GoHighLevel {cat_name.lower()} guides in {lang_config['native']}.",
            canonical=canonical,
            body=body,
            lang=lang_code,
            text_dir=text_dir,
            hreflang_path=f"/category/{cat_slug}/",
        )
        write(PUBLIC_DIR / prefix.lstrip("/") / "category" / cat_slug / "index.html", html)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n🔨 Building globalhighlevel.com...\n")

    # Clean public dir, then copy robots.txt from source (not from public/ which is gitignored)
    ROBOTS_SRC = BASE_DIR / "robots.txt"
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir(parents=True)
    if ROBOTS_SRC.exists():
        shutil.copy(ROBOTS_SRC, PUBLIC_DIR / "robots.txt")
    REDIRECTS_SRC = BASE_DIR / "_redirects"
    if REDIRECTS_SRC.exists():
        shutil.copy(REDIRECTS_SRC, PUBLIC_DIR / "_redirects")
    # Static images (tracked in source images/; public/ is gitignored + cleaned each build)
    IMAGES_SRC = BASE_DIR / "images"
    if IMAGES_SRC.exists():
        shutil.copytree(IMAGES_SRC, PUBLIC_DIR / "images")

    global CATEGORIES, LANGUAGES, LIVE_CATEGORY_SLUGS, LIVE_LANG_CODES, BUILT_PAGE_PATHS, LIVE_POST_SLUGS
    CATEGORIES, LANGUAGES = load_categories()

    posts     = load_posts()
    published = load_published()
    merged    = merge_data(posts, published)

    print(f"  Posts found: {len(posts)}")
    print(f"  Episodes in published.json: {len(published)}")
    print(f"  Categories: {len(CATEGORIES)}")
    print(f"  Merged: {len(merged)}\n")

    # Which English categories still have posts (mirrors build_category_pages
    # bucketing). base_html links category pages while pages are mid-build, so it
    # can't disk-check — it reads this precomputed set instead. Recomputed every
    # build, so it self-heals as the pipeline adds posts back.
    # P1.1 (2026-06-22): min_posts=2 for English hubs (mirrors language topic pages
    # + build_category_pages). A 1-post category renders as an empty-void "junk" page
    # and is a thin doorway under the quality demotion, so it is NOT built. Its post
    # falls back to a plain-text breadcrumb (build_post_page _cat_built keys off this set).
    _en_cat_counts = {}
    for _p in merged:
        if post_lang(_p) != "en":
            continue
        _topic = post_topic(_p)
        _cat = _topic if display_cat(_topic) else "GoHighLevel Tutorials"
        _en_cat_counts[slugify(_cat)] = _en_cat_counts.get(slugify(_cat), 0) + 1
    LIVE_CATEGORY_SLUGS = {_s for _s, _n in _en_cat_counts.items() if _n >= MIN_HUB_POSTS}
    _ANCHOR_URL_COUNTS.clear()  # P0.3: fresh anchor-cap ledger per build
    # Languages with at least one post get a built hub (mirrors build_language_hub's
    # `if not lang_posts: return`). English ("en") is always present.
    LIVE_LANG_CODES = {post_lang(_p) for _p in merged} | {"en"}
    # Slugs of surviving blog posts; gates post hreflang maps (see _build_post_hreflang_tags).
    LIVE_POST_SLUGS = {_p.get("slug") for _p in merged if _p.get("slug")}

    # Relative paths of every category/language page that will actually be built,
    # so _build_hreflang_tags() never advertises an unbuilt (404) alternate to
    # Google. Mirrors build_category_pages (EN), build_language_hub (>=1 post),
    # and build_language_topic_pages (>=2 posts per language-topic).
    BUILT_PAGE_PATHS = {"/", "/services/", "/about/"}
    BUILT_PAGE_PATHS |= {f"/category/{_s}/" for _s in LIVE_CATEGORY_SLUGS}
    for _lang in LANGUAGES:
        _prefix = _lang["prefix"]
        if not _prefix or _lang["code"] not in LIVE_LANG_CODES:
            continue  # English root handled above; skip languages with no built hub
        BUILT_PAGE_PATHS.add(f"{_prefix}/")
        _counts = {}
        for _p in merged:
            if post_lang(_p) == _lang["code"]:
                _t = post_topic(_p)
                _counts[_t] = _counts.get(_t, 0) + 1
        for _t, _n in _counts.items():
            if _n >= 2:
                BUILT_PAGE_PATHS.add(f"{_prefix}/category/{slugify(_t)}/")

    # Individual post pages — authority template for series content, blog template for rest
    print("Building post pages...")
    authority_count = 0
    blog_count = 0
    for p in merged:
        is_series = p.get("is_series_hub") or p.get("url_path", "").startswith("/es/para/") or p.get("url_path", "").startswith("/for/")
        if is_series:
            build_authority_page(p, all_posts=merged)
            authority_count += 1
        else:
            build_post_page(p, all_posts=merged)
            blog_count += 1
    print(f"  authority: {authority_count}, blog: {blog_count}")

    # Homepage (paginated) — English only
    print("\nBuilding homepage...")
    homepage_posts = [
        p for p in merged
        if post_lang(p) == "en"
    ]
    print(f"  Homepage posts (English only): {len(homepage_posts)} of {len(merged)} total")
    per_page = 18
    total_pages = max(1, -(-len(homepage_posts) // per_page))
    for page in range(1, total_pages + 1):
        build_index(homepage_posts, page=page, per_page=per_page)

    # Category pages
    print("\nBuilding category pages...")
    build_category_pages(merged)

    # Language hubs and language-specific topic pages
    print("\nBuilding language hubs...")
    for lang in LANGUAGES:
        if lang["prefix"]:  # skip English — it's the main site
            print(f"  Building {lang['native']} hub ({lang['prefix']})...")
            build_language_hub(lang, merged)
            build_language_topic_pages(lang, merged)

    # Sitemap
    print("\nBuilding sitemap...")
    build_sitemap(merged)

    # Landing pages
    # /trial/ stays as podcast conversion page (noindex). /start/ and /coupon/ are
    # NOT built — they 301 redirect to the master blog post via _redirects (discount
    # consolidation 2026-04-21). Static files would take precedence over _redirects
    # on Cloudflare Pages, so we skip building them entirely.
    print("\nBuilding trial page...")
    _build_affiliate_landing("trial", "podcast")
    for lang_cfg in LOCALIZED_LANDING_LANGS:
        _build_localized_affiliate_landing(lang_cfg, "trial", "podcast")
    # Deliberately NOT building /start/ or /coupon/ — see _redirects file
    print("Building services page...")
    build_services_page()

    # About page (E-E-A-T)
    print("Building about page...")
    build_about_page(total_posts=len(merged))

    # 12-month plan page (public commitment document)
    print("Building 12-month plan page...")

    # llms.txt (AI discoverability)
    build_llms_txt(merged)

    # 404
    build_404()

    if LANG_META_VIOLATIONS:
        print(f"\n❌ Build FAILED — {len(LANG_META_VIOLATIONS)} meta/language mismatch(es):")
        for v in LANG_META_VIOLATIONS[:20]:
            print(f"   • {v}")
        if len(LANG_META_VIOLATIONS) > 20:
            print(f"   … and {len(LANG_META_VIOLATIONS) - 20} more")
        sys.exit(1)

    print(f"\n✅ Build complete — {len(merged)} posts, {total_pages} index pages\n")

    _assert_tracking_tags_on_every_page()
    _assert_link_hygiene()


def _assert_link_hygiene():
    """Fail the build if the link-hygiene gate (scripts/audit_links.py) finds a
    violation: anchor cliff, single-word/bare-brand anchor, thin hub, or internal 404.
    Blocking — Cloudflare runs build.py, so a non-zero exit here stops the deploy.
    Same structural-guarantee pattern as _assert_tracking_tags_on_every_page."""
    audit = BASE_DIR / "scripts" / "audit_links.py"
    if not audit.exists():
        return
    sys.stdout.flush()  # keep build + subprocess output in order in CI/Cloudflare logs
    result = subprocess.run([sys.executable, str(audit), str(PUBLIC_DIR)])
    if result.returncode != 0:
        print("\n❌ Link-hygiene gate failed (scripts/audit_links.py) — build aborted.")
        sys.exit(1)


def _assert_tracking_tags_on_every_page():
    """Fail the build if any rendered HTML page is missing the Clarity tag.
    Structural guarantee: no page ships without Clarity. Adding a new HTML template
    that bypasses base_html will surface here at build time, not in production."""
    if not CLARITY_ID:
        return
    public = BASE_DIR / "public"
    pages = list(public.rglob("*.html"))
    missing = [html.relative_to(public) for html in pages
               if CLARITY_ID not in html.read_text(encoding="utf-8", errors="ignore")]
    if missing:
        print(f"\n❌ Clarity tag ({CLARITY_ID}) missing on {len(missing)} page(s):")
        for p in missing[:10]:
            print(f"     • {p}")
        if len(missing) > 10:
            print(f"     … and {len(missing) - 10} more")
        sys.exit(1)
    print(f"✅ Clarity tag verified on all {len(pages)} pages\n")


if __name__ == "__main__":
    main()
