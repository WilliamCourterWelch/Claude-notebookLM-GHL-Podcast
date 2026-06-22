"""Shared helpers for the /ghl-capture EEAT evidence pipeline.

Design doc: ~/.gstack/projects/WilliamCourterWelch-Claude-notebookLM-GHL-Podcast/
kerapassante-main-design-20260622-151441.md

Judgment (which screens prove a claim, honesty sign-off) lives in the
/ghl-capture SKILL.md. This module + the two scripts beside it are pure
EXECUTION: capture orchestration, Pillow optimize, figure wiring, orphan check.
Nothing here auto-detects PII or certifies truth; honesty is human-attested and
recorded in the manifest (see PII_CHECKLIST + the `attested` manifest field).
"""
from __future__ import annotations

import glob
import html
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# globalhighlevel-site/ (this file lives in globalhighlevel-site/scripts/)
SITE = Path(__file__).resolve().parent.parent
POSTS = SITE / "posts"
IMAGES = SITE / "images"
CAPTURES = SITE / "captures"

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")

# Canonical PII / data-leak checklist. SINGLE runtime source of truth so the
# attestation can't drift between runs (spec-review finding N1). SKILL.md quotes
# this list verbatim; if it changes, change it HERE.
PII_CHECKLIST = [
    "Account / agency name in the top bar or profile menu",
    "Contacts, conversations, or any client list / client PII (name, email, phone)",
    "Notification bell contents and recent-activity feeds",
    "Billing, card, or payment-method details",
    "Autofill / browser dropdowns exposing saved data",
    "Any sub-account or location name that is not the throwaway sandbox",
]


def utc_now() -> str:
    """ISO-8601 UTC timestamp. Machine-captured (never hand-entered) per N1."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------- path safety

_SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def safe_component(value: str, what: str) -> str:
    """Reject any path component that could escape its directory. Plan `name`,
    `slug`, and `lang` all become filesystem paths; an unvalidated `../` or
    absolute value writes screenshots/manifests outside the tree (all three
    reviewers flagged this as the merge blocker). Returns the value or raises."""
    if not isinstance(value, str) or not _SAFE.match(value) or ".." in value:
        raise ValueError(
            f"unsafe {what}: {value!r} (allowed: letters/digits/._- , no '..', no '/')"
        )
    return value


def assert_under(path: Path, base: Path) -> Path:
    """Resolve `path` and confirm it stays inside `base`. Defense in depth even
    after component validation. Raises ValueError on escape."""
    rp, rb = path.resolve(), base.resolve()
    if rp != rb and rb not in rp.parents:
        raise ValueError(f"path escapes {rb}: {rp}")
    return path


def _atomic_write(path: Path, text: str) -> None:
    """Write via temp file + os.replace so a crash never leaves a truncated
    post/manifest (reviewers flagged non-atomic JSON writes)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


# ---------------------------------------------------------------- posts / json

def post_path(slug: str) -> Path:
    return POSTS / f"{slug}.json"


def load_post(slug: str) -> dict:
    return json.loads(post_path(slug).read_text(encoding="utf-8"))


def save_post(slug: str, data: dict) -> None:
    """Write a post back matching repo convention: indent=2, ensure_ascii=False,
    trailing newline. Targeted html_content edits keep the diff small."""
    _atomic_write(post_path(slug), json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def iter_posts():
    """Yield (path, data) for every readable post. Unreadable posts are NOT
    silently skipped here — callers that gate on completeness must consult
    unreadable_posts() too, or the gate is fail-open."""
    for p in sorted(POSTS.glob("*.json")):
        try:
            yield p, json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue


def unreadable_posts() -> list[str]:
    """Posts that exist but fail to parse — a corrupt post hides its image
    references, so orphan_check must report these rather than report OK."""
    bad = []
    for p in sorted(POSTS.glob("*.json")):
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            bad.append(p.name)
    return bad


# ------------------------------------------------------------------- images

def referenced_image_paths() -> dict[str, list[str]]:
    """Map every /images/... path referenced in any post's html_content to the
    list of post slugs that reference it. Same image in several posts is fine
    (intentional reuse, e.g. ghl-mercadopago-card-es.png in 2 ES posts)."""
    refs: dict[str, list[str]] = {}
    pat = re.compile(r'/images/[^"\\\s)]+')
    for path, data in iter_posts():
        slug = data.get("slug", path.stem)
        for m in pat.findall(data.get("html_content", "") or ""):
            refs.setdefault(m, []).append(slug)
    return refs


def published_images() -> list[str]:
    """Every committed image under images/, as a site-absolute /images/... path."""
    out = []
    for ext in IMAGE_EXTS:
        for f in IMAGES.rglob(f"*{ext}"):
            if f.is_file() and not f.is_symlink():
                out.append("/images/" + f.relative_to(IMAGES).as_posix())
    return sorted(out)


def orphan_check() -> dict:
    """Leak gate. Returns:
      orphans: published images referenced by ZERO posts (the leak class, e.g.
               ghl-payment-integrations-es.png captured+optimized but never wired)
      broken:  /images/ paths a post references but no file exists on disk
    Reuse across multiple posts is allowed, so this is "referenced by >=1", NOT
    "exactly one" (real data has shared screenshots in 2 posts)."""
    refs = referenced_image_paths()
    published = set(published_images())
    referenced = set(refs)
    return {
        "orphans": sorted(published - referenced),
        "broken": sorted(referenced - published),
        "referenced": refs,
        "unreadable_posts": unreadable_posts(),  # fail-closed: surface corrupt posts
    }


def next_index(slug: str, lang: str) -> int:
    """Next <n> for images/<lang>/<slug>-<n>.png. max existing +1, never reuse."""
    d = IMAGES / lang
    n = 0
    if d.exists():
        pat = re.compile(re.escape(slug) + r"-(\d+)\.")
        for f in d.iterdir():
            m = pat.match(f.name)
            if m:
                n = max(n, int(m.group(1)))
    return n + 1


# ---------------------------------------------------------------- manifest

def manifest_path(slug: str, lang: str) -> Path:
    return CAPTURES / lang / f"{slug}.manifest.json"


def load_manifest(slug: str, lang: str) -> dict:
    p = manifest_path(slug, lang)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"slug": slug, "lang": lang, "images": []}


def save_manifest(slug: str, lang: str, manifest: dict) -> None:
    _atomic_write(manifest_path(slug, lang),
                  json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def manifest_entry(manifest: dict, name: str) -> dict | None:
    for e in manifest.get("images", []):
        if e.get("name") == name:
            return e
    return None


# ---------------------------------------------------------------- wiring

def figure_html(src: str, alt: str, caption: str) -> str:
    """Build the figure markup matching the existing site convention exactly:
    <figure class="post-figure"><img ... loading="lazy"><figcaption>...</figcaption></figure>
    alt is an attribute, caption is text -> both HTML-escaped."""
    return (
        '<figure class="post-figure">'
        f'<img src="{html.escape(src, quote=True)}" '
        f'alt="{html.escape(alt, quote=True)}" loading="lazy">'
        f"<figcaption>{html.escape(caption)}</figcaption></figure>"
    )


def insert_after_marker(html_content: str, marker: str, fragment: str) -> str:
    """Insert fragment immediately after the first occurrence of marker.
    Raises ValueError if marker is absent or ambiguous-empty. The SKILL picks a
    marker (usually a closing tag like </p> of the claim's paragraph, or a
    unique heading) so placement is deterministic and reviewable in the diff."""
    if not marker:
        raise ValueError("empty marker")
    idx = html_content.find(marker)
    if idx == -1:
        raise ValueError(f"marker not found in html_content: {marker!r}")
    cut = idx + len(marker)
    return html_content[:cut] + fragment + html_content[cut:]
