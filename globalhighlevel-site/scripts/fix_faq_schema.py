#!/usr/bin/env python3
"""Rebuild inline FAQPage JSON-LD from each post's own visible FAQ copy.

Why this exists (v0.3.9.2)
--------------------------
FAQ answers live TWICE inside a post's `html_content`: once as visible HTML and
once inside an inline `FAQPage` JSON-LD block. Nothing keeps the two in sync, so
three defects accumulated across the 159 posts that embed schema:

  1. duplicate FAQPage blocks (8 posts) -- engines honor one, the other is waste
  2. ORPHAN questions (16 across 9 posts) -- schema asserts a Q&A that appears
     nowhere on the page. This is the real problem: Google requires FAQ
     structured data to match visible content, and orphans are the class that
     gets rich results suppressed.
  3. answer drift (53 across 29 posts) -- schema wording no longer matches the
     visible answer it claims to mirror.

The fix is deterministic: visible copy is the source of truth. For each post we
re-derive the Q&A pairs from the rendered FAQ sections and emit exactly ONE
FAQPage block containing only questions that are actually visible, with answer
text taken verbatim from the visible answer.

What this deliberately does NOT do
----------------------------------
* It does not touch the 750 posts with no inline schema. `build.py`'s
  `faq_schema()` already generates theirs at render time.
* It does not "fix" trivial drift (whitespace, entity encoding, or a schema
  answer that is a clean truncation of the visible one). Those are faithful and
  rewriting them would churn 218 entries for no gain.
* It does not restructure visible HTML. 36 posts head their FAQ with `<h3>`
  rather than `<h2>`; that is a corpus inconsistency, not a schema defect, and
  changing heading levels is an editorial call, not a migration.

Usage:
    python3 scripts/fix_faq_schema.py --dry-run     # report, write nothing
    python3 scripts/fix_faq_schema.py               # apply
"""
from __future__ import annotations

import argparse
import glob
import html as html_mod
import io
import json
import os
import re
import sys

POSTS_GLOB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "posts", "*.json")

# FAQ section headings, any level. Enumerated from the corpus (9 distinct
# variants across the 159 schema-carrying posts), not guessed:
#   157x "Frequently Asked Questions"   4x "Preguntas frecuentes" (any case)
#     4x "Common Questions About/During ..."   2x "الأسئلة الشائعة"
# The Arabic pattern is deliberately specific: one post has "أخطاء شائعة"
# ("common mistakes"), which is NOT an FAQ section and must not match.
_FAQ_HEADING = (
    r"<h([23])[^>]*>\s*(?:Preguntas\s+frecuentes|Frequently\s+Asked\s+Questions"
    r"|Common\s+Questions|FAQ|الأسئلة\s+الشائعة)[^<]*</h\1>"
)
_LDJSON = r'<script type="application/ld\+json">(.*?)</script>'


def _text(fragment: str) -> str:
    """Strip tags, unescape entities, collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html_mod.unescape(fragment))).strip()


def strip_ldjson(html: str) -> str:
    return re.sub(_LDJSON, "", html, flags=re.S)


def visible_pairs(html: str) -> list[tuple[str, str]]:
    """Extract (question, answer) from every visible FAQ section, in page order.

    Scoped to FAQ sections so unrelated <h3> headings elsewhere are not captured.
    A section runs from its heading until the next heading of the SAME OR HIGHER
    level, the author bio, or end of content.
    """
    visible = strip_ldjson(html)
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()

    for m in re.finditer(_FAQ_HEADING, visible, re.I):
        rest = visible[m.end():]
        # A FAQ section always ends at the next <h1>/<h2> (or the author bio),
        # NEVER at an <h3> -- the questions themselves are <h3>. 36 posts head
        # their FAQ with <h3> rather than <h2>; stopping at the next <h3> made
        # those sections read as empty and silently skipped every one of them.
        stop = re.search(r"<h[12][^>]*>|<section class=\"author-bio\"", rest, re.I)
        section = rest[: stop.start()] if stop else rest

        # An answer ends at the next question OR at the close of the FAQ
        # container. Running to the next <h2> made the LAST answer swallow the
        # sibling CTA block that follows it ("Ready to Get Started... Claim Your
        # Free Trial"), which put advertising copy into 38 posts' structured
        # data -- a Google structured-data policy violation, caught by codex
        # adversarial review before this shipped.
        found = re.findall(
            r"<h3[^>]*>(.*?)</h3>(.*?)(?=<h3[^>]*>|</div>|<div|<section|<h2|<h1|$)",
            section, re.S,
        )
        # Hub pages use bold paragraphs instead of h3, in two shapes:
        # answer inside the same <p>, and answer in the following <p>.
        found += re.findall(r"<p><strong>([^<]*[?¿؟][^<]*)</strong>(.*?)</p>", section, re.S)
        found += re.findall(
            r"<p><strong>([^<]*[?¿؟][^<]*)</strong>\s*</p>\s*<p[^>]*>(.*?)</p>", section, re.S
        )

        for raw_q, raw_a in found:
            q, a = _text(raw_q), _text(raw_a)
            if not q or not a:
                continue
            if not any(ch in q for ch in "?¿؟"):
                continue  # the section heading itself, not a question
            if q in seen:
                continue
            seen.add(q)
            pairs.append((q, a))
    return pairs


def build_block(pairs: list[tuple[str, str]]) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    }
    return ('<script type="application/ld+json">'
            + json.dumps(payload, ensure_ascii=False)
            + "</script>")


def current_questions(html: str) -> list[str]:
    out: list[str] = []
    for block in re.findall(_LDJSON, html, re.S):
        if "FAQPage" not in block:
            continue
        try:
            data = json.loads(block.strip())
        except ValueError:
            continue
        for q in data.get("mainEntity", []):
            name = _text(q.get("name", ""))
            if name:
                out.append(name)
    return out


def _norm(s: str) -> str:
    """Aggressive normalization for the triviality test only."""
    return re.sub(r"[^\w]", "", s.lower())


def current_pairs(html: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for block in re.findall(_LDJSON, html, re.S):
        if "FAQPage" not in block:
            continue
        try:
            data = json.loads(block.strip())
        except ValueError:
            continue
        for q in data.get("mainEntity", []):
            out.append((_text(q.get("name", "")),
                        _text(q.get("acceptedAnswer", {}).get("text", ""))))
    return out


def has_real_defect(html: str, pairs: list[tuple[str, str]]) -> bool:
    """True only when rewriting fixes something that actually matters.

    A schema answer that differs from the visible one purely by whitespace,
    entity encoding, or clean truncation is FAITHFUL. Rewriting those would
    churn ~110 posts for zero SEO gain, so they are left alone.
    """
    blocks = [b for b in re.findall(_LDJSON, html, re.S) if "FAQPage" in b]
    if len(blocks) > 1:
        return True  # duplicate FAQPage blocks

    visible = {q: a for q, a in pairs}
    for q, a in current_pairs(html):
        if q not in visible:
            return True  # orphan: schema asserts a Q&A not on the page
        v = visible[q]
        if _norm(v) == _norm(a):
            continue  # whitespace / entity only
        # A clean truncation means the schema answer is a TRUE PREFIX of the
        # visible one. Two weaker tests were tried and both were wrong:
        #   * comparing only the first 80 chars -- missed 5 posts that diverged
        #     later ("other users or accounts" vs "other users/accounts")
        #   * substring containment (`_norm(a) in _norm(v)`) -- that is not
        #     truncation at all, it silently masks drift whenever the stale
        #     schema text happens to appear anywhere inside the visible answer.
        if a and _norm(v).startswith(_norm(a)):
            continue  # schema answer is a clean prefix of the visible answer
        return True  # genuine wording drift
    return False


def rewrite(html: str):
    """Replace all inline FAQPage blocks with one rebuilt from visible copy.

    Returns:
        (new_html, pairs) when a rewrite is warranted, otherwise
        (None, reason) where reason is one of:
          "no-schema"        -- post has no inline FAQPage block
          "no-visible-pairs" -- refuse to strip: nothing visible to rebuild from
          "no-defect"        -- schema is already faithful, leave it alone
    """
    faq_blocks = [b for b in re.findall(_LDJSON, html, re.S) if "FAQPage" in b]
    if not faq_blocks:
        return None, "no-schema"

    pairs = visible_pairs(html)
    if not pairs:
        # Refuse to strip a post's only schema. Better a stale block than none.
        return None, "no-visible-pairs"

    # Extraction shortfall guard. Refusing only on ZERO pairs is not enough: if
    # the extractor finds one pair and misses four, it would emit a one-entry
    # FAQPage and silently discard the rest as "orphans". Any post where we
    # recover fewer than half the existing questions is a parser failure, not a
    # content defect -- leave it untouched and report it.
    existing = len({q for q, _ in current_pairs(html)})
    if existing and len(pairs) * 2 < existing:
        return None, "extraction-shortfall"

    if not has_real_defect(html, pairs):
        return None, "no-defect"

    replaced = False
    out_parts: list[str] = []
    pos = 0
    for m in re.finditer(_LDJSON, html, re.S):
        if "FAQPage" not in m.group(1):
            continue
        out_parts.append(html[pos:m.start()])
        if not replaced:
            out_parts.append(build_block(pairs))
            replaced = True
        # subsequent FAQPage blocks are dropped
        pos = m.end()
    out_parts.append(html[pos:])
    return "".join(out_parts), pairs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    changed = skipped_no_visible = no_defect = shortfall = 0
    dropped_orphans: list[tuple[str, str]] = []
    merged_dupes: list[str] = []
    resynced: list[str] = []

    for path in sorted(glob.glob(POSTS_GLOB)):
        try:
            with io.open(path, encoding="utf-8") as fh:
                post = json.load(fh)
        except ValueError:
            print("  SKIP unparseable: %s" % os.path.basename(path), file=sys.stderr)
            continue

        html = post.get("html_content") or ""
        blocks = [b for b in re.findall(_LDJSON, html, re.S) if "FAQPage" in b]
        if not blocks:
            continue

        before = current_questions(html)
        new_html, pairs = rewrite(html)
        name = os.path.basename(path)

        if new_html is None:
            if pairs == "no-visible-pairs":
                skipped_no_visible += 1
                print("  KEEP (no visible Q&A found, refusing to strip schema): %s" % name)
            elif pairs == "extraction-shortfall":
                shortfall += 1
                print("  KEEP (extractor recovered <half the questions -- parser gap): %s" % name)
            else:
                no_defect += 1
            continue
        if new_html == html:
            no_defect += 1
            continue

        after = [q for q, _ in pairs]
        for q in before:
            if q not in after:
                dropped_orphans.append((name, q))
        if len(blocks) > 1:
            merged_dupes.append(name)
        if len(before) == len(after) and set(before) == set(after):
            resynced.append(name)

        changed += 1
        if not args.dry_run:
            post["html_content"] = new_html
            # Atomic write, same pattern as restore_posts.py:292. A truncating
            # in-place write that dies mid-flight leaves invalid JSON, and
            # build.load_posts() swallows unparseable posts silently -- the post
            # would vanish from the site with no error (adversarial 2026-07-23).
            text = json.dumps(post, ensure_ascii=False, indent=2) + "\n"
            tmp = path + ".tmp"
            with io.open(tmp, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.replace(tmp, path)

    verb = "would change" if args.dry_run else "changed"
    print("\n%s: %d posts" % (verb, changed))
    print("  duplicate FAQPage blocks merged : %d" % len(merged_dupes))
    print("  orphan questions dropped        : %d (across %d posts)"
          % (len(dropped_orphans), len({n for n, _ in dropped_orphans})))
    print("  answer text re-synced only      : %d" % len(resynced))
    print("  no real defect (left alone)     : %d" % no_defect)
    print("  no visible Q&A (refused to strip): %d" % skipped_no_visible)
    print("  extraction shortfall (refused)  : %d" % shortfall)
    if dropped_orphans:
        print("\norphan questions dropped (not present in visible copy):")
        for n, q in dropped_orphans:
            print("  %s\n      %s" % (n, q[:90]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
