#!/usr/bin/env python3
"""migrate_lang_topic.py — backfill `language` + assign a real `topic` per post.

D1 (additive): keep `category` for back-compat; ADD `language` + `topic`.
D2 (reviewable + idempotent):
  - PROPOSAL (default): writes migration-proposal.csv. Modifies NOTHING.
  - APPLY (--apply): reads the REVIEWED migration-proposal.csv and writes the
    new_language / new_topic columns from it — so your hand-edits to the CSV are
    what land. Idempotent: only writes a file when a value actually changes.

LANGUAGE
  new_language = explicit post['language'] (if valid) else slug inference.
  Slug inference is computed INDEPENDENTLY via build._LANG_SLUG_MARKERS (NOT
  build.post_lang(), which short-circuits on the explicit field). So an explicit
  field that disagrees with the slug is a REAL signal -> flag LANG_MISMATCH.
  We DEFAULT to the explicit field (never auto-flip es/ar, whose slugs often
  lack markers); the `inferred_language` column shows the alternative so you can
  accept it by editing new_language in the CSV.

TOPIC
  Classify EVERY post with WORD-BOUNDARY keyword matching (no "ach" in "Coaching",
  no Spanish "ia" in "guia"). English/India use categories.json keywords; es/ar
  use their generators' maps.
  - category already a real topic -> keep it (method=kept). If the classifier
    disagrees, flag CATEGORY_MISMATCH and show classified_topic (catches stale
    bad categories like an invoice post filed Phone & Voice).
  - category is a language bucket / unknown -> use the classifier (method=classified);
    a catch-all 'Agency & Platform' fallback -> flag LOW_CONFIDENCE.

CSV columns:
  slug, old_language, inferred_language, old_category, classified_topic,
  new_language, new_topic, method, flags, title

Usage:
  cd globalhighlevel-site
  python3 migrate_lang_topic.py            # PROPOSAL -> migration-proposal.csv
  # ...review/edit the CSV...
  python3 migrate_lang_topic.py --apply    # writes new_language/new_topic FROM the CSV

NOTE (DRY / T7): es/ar keyword maps are transcribed from 7-spanish-blog.py /
9-arabic-blog.py; a later cleanup should unify all three into categories.json.
"""
import csv
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime

import build  # same dir; import-safe (main is guarded)

BASE = build.BASE_DIR
VALID_LANGS = {"en", "es", "en-IN", "ar"}
# Reuse build's set so the bucket list can't drift across modules (if build.py
# renames/adds a bucket, this follows automatically instead of going stale).
BUCKET_NAMES = build.LANG_BUCKET_CATEGORIES
CATCH_ALL = "Agency & Platform"
CSV_PATH = BASE / "migration-proposal.csv"

cats = json.loads((BASE / "categories.json").read_text())
REAL_TOPICS = [t for t in cats["topics"] if t["name"] not in BUCKET_NAMES]
REAL_TOPIC_NAMES = {t["name"] for t in REAL_TOPICS}

# es/ar keyword dispatch (source: 7-spanish-blog.py:603, 9-arabic-blog.py:367).
# "ia" is kept — word-boundary matching makes it safe (matches standalone "ia",
# not "guia"/"agencia").
ES_KW = [
    ("SMS & Messaging", ["whatsapp", "sms", "mensaje", "comunicación"]),
    ("Payments & Commerce", ["pago", "mercadopago", "precio", "factura", "cobrar"]),
    ("AI & Automation", ["ai", "ia", "inteligencia", "automatización", "automatizacion",
                          "automatizaciones", "flujos de trabajo", "flujo", "workflows",
                          "automations", "bot"]),
    ("CRM & Contacts", ["crm", "contacto", "cliente", "pipeline"]),
    ("Email & Deliverability", ["email", "correo", "deliverability"]),
    ("Agency & Platform", ["embudo", "funnel", "landing", "página", "agencia", "saas",
                           "revend", "white label"]),
]
AR_KW = [
    ("SMS & Messaging", ["واتساب", "whatsapp", "sms", "رسائل", "رسالة"]),
    ("Payments & Commerce", ["دفع", "أسعار", "سعر", "تجارة", "payment", "paytabs",
                             "stripe", "دولار", "درهم"]),
    ("AI & Automation", ["ai", "ذكاء", "أتمتة", "automation", "بوت", "متابعة"]),
    ("CRM & Contacts", ["crm", "عملاء", "عميل", "contacts", "pipeline"]),
    ("Email & Deliverability", ["email", "بريد", "إلكتروني", "deliverability"]),
    ("Analytics & Reporting", ["تحليل", "analytics", "تقرير", "reporting"]),
    ("Phone & Voice", ["هاتف", "phone", "صوت", "voice", "مكالمات"]),
    ("Agency & Platform", ["وكالة", "وكالات", "saas", "agency", "white label",
                           "صفحات هبوط", "landing"]),
]


def kw_match(kw: str, text: str) -> bool:
    """Keyword present with ASCII word boundaries — 'ach' won't match 'coaching',
    'ia' won't match 'guia'. Arabic-script keywords are flanked by non-ASCII so
    the boundary still resolves cleanly."""
    return re.search(r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])", text) is not None


def infer_from_slug(slug: str) -> str:
    """Independent slug inference (does NOT short-circuit on an explicit field)."""
    s = (slug or "").lower()
    for code, markers in build._LANG_SLUG_MARKERS:
        if any(m in s for m in markers):
            return code
    return "en"


def classify_en(title: str):
    t = title.lower()
    for cat in REAL_TOPICS:
        for kw in sorted(cat["keywords"], key=len, reverse=True):
            if kw_match(kw, t):
                return cat["name"], False
    return CATCH_ALL, True


def classify_kw(title: str, table):
    t = title.lower()
    for name, kws in table:
        if any(kw_match(w, t) for w in kws):
            return name, False
    return CATCH_ALL, True


def classify(title: str, lang: str):
    if lang == "es":
        return classify_kw(title, ES_KW)
    if lang == "ar":
        return classify_kw(title, AR_KW)
    return classify_en(title)


def build_rows():
    rows = []
    for p in build.load_posts():
        slug = p.get("slug")
        if not slug:
            continue
        title = str(p.get("title") or p.get("seoTitle") or "")  # coerce: a non-str title must not crash the whole run
        raw = p.get("language")
        explicit = raw if raw in VALID_LANGS else None
        inferred = infer_from_slug(slug)
        flags = []
        # Actionable language mismatch = the slug carries a SPECIFIC marker
        # (es/en-IN/ar) that contradicts the field. We propose the slug's value
        # (the safe direction: en default -> specific). We do NOT flag/flip when
        # the slug merely infers "en" against an es/ar field — that's an English
        # transliterated slug, and the explicit field is the trustworthy signal.
        if explicit and inferred != "en" and inferred != explicit:
            new_lang = inferred
            flags.append("LANG_MISMATCH")
        elif explicit:
            new_lang = explicit
        else:
            new_lang = inferred
            if raw and raw not in VALID_LANGS:
                flags.append("LANG_INVALID")

        cat = p.get("category", "")
        classified_topic, low_conf = classify(title, new_lang)

        if cat in REAL_TOPIC_NAMES:
            new_topic, method = cat, "kept"
            # Only flag when the classifier CONFIDENTLY disagrees (not a weak
            # catch-all) — surfaces stale bad categories (invoice -> Phone & Voice).
            if classified_topic != cat and classified_topic != CATCH_ALL:
                flags.append("CATEGORY_MISMATCH")
        else:
            new_topic, method = classified_topic, "classified"
            if low_conf:
                flags.append("LOW_CONFIDENCE")

        rows.append({
            "slug": slug,
            "old_language": raw or "",
            "inferred_language": inferred,
            "old_category": cat,
            "classified_topic": classified_topic,
            "new_language": new_lang,
            "new_topic": new_topic,
            "method": method,
            "flags": "|".join(flags),
            "title": title[:80],
        })
    return rows


def propose() -> int:
    rows = build_rows()
    if not rows:
        print("No posts found (need slug + html_content) — nothing to propose.")
        return 1
    # Never silently destroy a reviewed CSV. If one exists, back it up first so a
    # re-run can't erase hand-edits (the CSV is the human review/decision record).
    if CSV_PATH.exists():
        bak = CSV_PATH.with_name(f"{CSV_PATH.stem}.{datetime.now():%Y%m%d-%H%M%S}.bak.csv")
        shutil.copy2(CSV_PATH, bak)
        print(f"  (existing proposal backed up -> {bak.name})")
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def count(flag):
        return sum(1 for r in rows if flag in r["flags"].split("|"))

    dist = {}
    for r in rows:
        dist[r["new_topic"]] = dist.get(r["new_topic"], 0) + 1

    print(f"=== migration PROPOSAL ({len(rows)} posts) — nothing applied ===")
    print(f"  language: {sum(1 for r in rows if not r['old_language'])} backfilled | "
          f"{count('LANG_MISMATCH')} LANG_MISMATCH (review) | {count('LANG_INVALID')} invalid")
    print(f"  topic:    {sum(1 for r in rows if r['method']=='kept')} kept | "
          f"{sum(1 for r in rows if r['method']=='classified')} classified")
    print(f"            {count('CATEGORY_MISMATCH')} CATEGORY_MISMATCH (stale kept cat) | "
          f"{count('LOW_CONFIDENCE')} LOW_CONFIDENCE")
    flagged = sum(1 for r in rows if r["flags"])
    print(f"  review queue: {flagged} posts flagged")
    print("\n  proposed topic distribution:")
    for name, c in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"    {c:4d}  {name}")
    print(f"\n  proposal: {CSV_PATH}")
    print("  edit new_language/new_topic in the CSV as needed, then: python3 migrate_lang_topic.py --apply")
    return 0


def _write_post(slug: str, p: dict) -> None:
    """Write the post back PRESERVING its existing serialization convention so a
    2-field change shows a 2-line diff, not a whole-file reformat (the corpus is
    mixed: ~662 files \\u-escape non-ASCII, ~283 store it literally; none have a
    trailing newline). Match this file's escape style + trailing newline so the
    git diff stays a faithful, reviewable audit trail of what actually changed."""
    path = build.POSTS_DIR / f"{slug}.json"
    try:
        orig = path.read_text(encoding="utf-8")
    except Exception:
        orig = ""
    ensure_ascii = "\\u" in orig          # keep this file's existing escape style
    trailing = "\n" if orig.endswith("\n") else ""
    path.write_text(json.dumps(p, indent=2, ensure_ascii=ensure_ascii) + trailing,
                    encoding="utf-8")


def apply_csv() -> int:
    if not CSV_PATH.exists():
        print("ERROR: migration-proposal.csv not found — run the proposal first.")
        return 1
    # utf-8-sig tolerates a BOM a spreadsheet may add (else the first column key
    # becomes '﻿slug' and every lookup misses).
    raw_rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8-sig")))
    # A hand-edit that duplicates a slug row would silently win-last (the dict
    # comprehension keeps the last). Catch it BEFORE collapsing — fail loud.
    dup = {s: c for s, c in Counter(r["slug"] for r in raw_rows).items() if c > 1}
    if dup:
        print(f"ABORT: {len(dup)} duplicate slug(s) in the CSV (a hand-edit duplicated a row) — nothing written.")
        for s, c in list(dup.items())[:20]:
            print(f"   {s} appears {c}x")
        return 1
    reviewed = {r["slug"]: r for r in raw_rows}
    # Validate hand-editable fields before writing ANYTHING (codex P2): a CSV typo
    # in new_language orphans the post (excluded from every hub); a bad new_topic
    # makes a junk category page. Fail loud, write nothing, let the user fix + re-run.
    bad = [(s, r["new_language"], r["new_topic"]) for s, r in reviewed.items()
           if r["new_language"] not in VALID_LANGS or r["new_topic"] not in REAL_TOPIC_NAMES]
    if bad:
        print(f"ABORT: {len(bad)} CSV row(s) have an invalid new_language or new_topic — nothing written.")
        print(f"  valid languages: {sorted(VALID_LANGS)}")
        for s, lang, topic in bad[:20]:
            print(f"   {s}: language={lang!r} topic={topic!r}")
        return 1
    posts = build.load_posts()
    post_slugs = {p.get("slug") for p in posts}
    changed = 0
    skipped: list[str] = []
    for p in posts:
        slug = p.get("slug")
        r = reviewed.get(slug)
        if not r:
            skipped.append(slug)   # post on disk but no CSV row -> left unmigrated
            continue
        dirty = False
        if r["new_language"] and p.get("language") != r["new_language"]:
            p["language"] = r["new_language"]; dirty = True
        if r["new_topic"] and p.get("topic") != r["new_topic"]:
            p["topic"] = r["new_topic"]; dirty = True
        if dirty:
            _write_post(slug, p)
            changed += 1
    # Stale = CSV rows whose slug matches no current post (post renamed/deleted or
    # a typo'd hand-edit). These no-op silently otherwise; surface them loudly so a
    # half-applied / mismatched CSV is caught, not shipped.
    stale = sorted(s for s in reviewed if s not in post_slugs)
    print(f"APPLIED from migration-proposal.csv: {changed} files written")
    if skipped:
        print(f"  WARNING: {len(skipped)} post(s) on disk had NO CSV row (left unmigrated):")
        for s in sorted(skipped)[:20]:
            print(f"   - {s}")
    if stale:
        print(f"  WARNING: {len(stale)} CSV row(s) matched no post on disk (stale/typo'd slug):")
        for s in stale[:20]:
            print(f"   - {s}")
    return 0


def main() -> int:
    return apply_csv() if "--apply" in sys.argv else propose()


if __name__ == "__main__":
    sys.exit(main())
