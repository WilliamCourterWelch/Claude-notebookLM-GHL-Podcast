#!/usr/bin/env python3
"""migrate_lang_topic.py — backfill `language` + assign a real `topic` on every post.

Restructure decisions:
  D1 (additive): keep `category` untouched for back-compat; ADD a `topic` field.
  D2 (reviewable + idempotent): PROPOSAL-first. Default run modifies NOTHING — it
      writes migration-proposal.csv for human review. Only --apply writes fields,
      and only where a value is missing or changed (re-running is safe).

How values are derived:
  language: explicit post['language'] if present AND valid; else build.post_lang()
            slug inference. If an explicit field DISAGREES with slug inference
            (the ~123 English-tagged-but-Espanol-category posts, "whatsapp"
            false-positives, etc.) -> flag LANG_MISMATCH for the review queue.
  topic:    if post['category'] is one of the 8 REAL topics -> keep it (method=kept).
            else (a language bucket / unknown) -> classify the title against the 8
            real topics by keyword (method=classified). English/India use the
            categories.json keyword arrays (identical to 5-blog.py's classify_post);
            es/ar use their generators' keyword dispatch. A catch-all
            "Agency & Platform" fallback -> flag LOW_CONFIDENCE for the review queue.

Usage:
  cd globalhighlevel-site
  python3 migrate_lang_topic.py            # PROPOSAL -> migration-proposal.csv
  python3 migrate_lang_topic.py --apply    # write language+topic AFTER you review

NOTE (DRY / T7): the es/ar keyword maps below are transcribed from
ghl-podcast-pipeline/scripts/7-spanish-blog.py and 9-arabic-blog.py. A later
cleanup should unify all three into categories.json so there's one source.
"""
import csv
import json
import sys
from pathlib import Path

import build  # same dir; import-safe (main is guarded)

BASE = build.BASE_DIR
VALID_LANGS = {"en", "es", "en-IN", "ar"}
BUCKET_NAMES = {"GoHighLevel India", "GoHighLevel en Español", "GoHighLevel en Espanol"}
CATCH_ALL = "Agency & Platform"

cats = json.loads((BASE / "categories.json").read_text())
# 8 real topics = topics[] minus the language buckets
REAL_TOPICS = [t for t in cats["topics"] if t["name"] not in BUCKET_NAMES]
REAL_TOPIC_NAMES = {t["name"] for t in REAL_TOPICS}

# es/ar keyword dispatch (source: 7-spanish-blog.py:603, 9-arabic-blog.py:367)
ES_KW = [
    ("SMS & Messaging", ["whatsapp", "sms", "mensaje", "comunicación"]),
    ("Payments & Commerce", ["pago", "mercadopago", "precio", "factura", "cobrar"]),
    ("AI & Automation", ["ai", "ia", "inteligencia", "automatización", "automatizacion", "automatizaciones", "flujos de trabajo", "flujo", "workflows", "automations", "bot"]),
    ("CRM & Contacts", ["crm", "contacto", "cliente", "pipeline"]),
    ("Email & Deliverability", ["email", "correo", "deliverability"]),
    ("Agency & Platform", ["embudo", "funnel", "landing", "página", "agencia", "saas", "revend", "white label"]),
]
AR_KW = [
    ("SMS & Messaging", ["واتساب", "whatsapp", "sms", "رسائل", "رسالة"]),
    ("Payments & Commerce", ["دفع", "أسعار", "سعر", "تجارة", "payment", "paytabs", "stripe", "دولار", "درهم"]),
    ("AI & Automation", ["ai", "ذكاء", "أتمتة", "automation", "بوت", "متابعة"]),
    ("CRM & Contacts", ["crm", "عملاء", "عميل", "contacts", "pipeline"]),
    ("Email & Deliverability", ["email", "بريد", "إلكتروني", "deliverability"]),
    ("Analytics & Reporting", ["تحليل", "analytics", "تقرير", "reporting"]),
    ("Phone & Voice", ["هاتف", "phone", "صوت", "voice", "مكالمات"]),
    ("Agency & Platform", ["وكالة", "وكالات", "saas", "agency", "white label", "صفحات هبوط", "landing"]),
]


def classify_en(title: str):
    """English/India: match the 8 real topics' categories.json keywords (longest first)."""
    t = title.lower()
    for cat in REAL_TOPICS:
        for kw in sorted(cat["keywords"], key=len, reverse=True):
            if kw in t:
                return cat["name"], False
    return CATCH_ALL, True  # catch-all -> low confidence


def classify_kw(title: str, table):
    t = title.lower()
    for name, kws in table:
        if any(w in t for w in kws):
            return name, False
    return CATCH_ALL, True


def classify(title: str, lang: str):
    if lang == "es":
        return classify_kw(title, ES_KW)
    if lang == "ar":
        return classify_kw(title, AR_KW)
    return classify_en(title)  # en, en-IN


def main() -> int:
    apply = "--apply" in sys.argv
    posts = build.load_posts()
    rows = []
    n_kept = n_reclassified = n_lang_mismatch = n_low_conf = n_lang_backfill = 0

    for p in posts:
        slug = p.get("slug")
        if not slug:
            continue
        title = p.get("title") or p.get("seoTitle") or ""
        explicit = p.get("language")
        inferred = build.post_lang(p)
        new_lang = explicit if explicit in VALID_LANGS else inferred
        lang_mismatch = bool(explicit) and explicit in VALID_LANGS and explicit != inferred
        if not explicit:
            n_lang_backfill += 1
        if lang_mismatch:
            n_lang_mismatch += 1

        cat = p.get("category", "")
        if cat in REAL_TOPIC_NAMES:
            new_topic, low_conf, method = cat, False, "kept"
            n_kept += 1
        else:
            new_topic, low_conf = classify(title, new_lang)
            method = "classified"
            n_reclassified += 1
            if low_conf:
                n_low_conf += 1

        flags = []
        if lang_mismatch:
            flags.append("LANG_MISMATCH")
        if low_conf:
            flags.append("LOW_CONFIDENCE")
        rows.append({
            "slug": slug,
            "old_language": explicit or "",
            "old_category": cat,
            "new_language": new_lang,
            "new_topic": new_topic,
            "method": method,
            "flags": "|".join(flags),
            "title": title[:80],
        })

    out = BASE / "migration-proposal.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # topic distribution
    dist = {}
    for r in rows:
        dist[r["new_topic"]] = dist.get(r["new_topic"], 0) + 1

    print(f"=== migration proposal ({len(rows)} posts) ===")
    print(f"  language: {n_lang_backfill} backfilled (no explicit field), {n_lang_mismatch} MISMATCH (review)")
    print(f"  topic:    {n_kept} kept (already a real topic), {n_reclassified} reclassified from a bucket")
    print(f"            {n_low_conf} LOW_CONFIDENCE (catch-all fallback -> review)")
    print(f"  review queue total: {len({r['slug'] for r in rows if r['flags']})} posts flagged")
    print("\n  proposed topic distribution:")
    for name, c in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"    {c:4d}  {name}")
    print(f"\n  proposal written: {out}")
    print("  review it, then re-run with --apply to write language+topic.")

    if apply:
        print("\n  --apply: writing language+topic to posts (idempotent)...")
        changed = 0
        by_slug = {r["slug"]: r for r in rows}
        for p in posts:
            r = by_slug.get(p.get("slug"))
            if not r:
                continue
            dirty = False
            if p.get("language") != r["new_language"]:
                p["language"] = r["new_language"]; dirty = True
            if p.get("topic") != r["new_topic"]:
                p["topic"] = r["new_topic"]; dirty = True
            if dirty:
                fp = build.POSTS_DIR / f"{p['slug']}.json"
                fp.write_text(json.dumps(p, indent=2, ensure_ascii=True) + "\n")
                changed += 1
        print(f"  wrote {changed} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
