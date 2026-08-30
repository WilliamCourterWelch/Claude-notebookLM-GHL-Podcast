#!/usr/bin/env python3
"""FAQPage JSON-LD must say exactly what the visible FAQ says.

A post can carry hand-written FAQPage structured data in its body. Search
engines read that JSON-LD, not the prose, so if someone adds a visible Q&A and
forgets the JSON-LD (or the reverse) the page ships structured data that
contradicts itself. Nothing renders wrong, no other gate fires, and the drift
stays invisible until a SERP surfaces an answer the page no longer contains.

Found 2026-08-30 while adding four FAQs to the pricing guide: that edit had to
touch two places by hand and the only thing keeping them together was
remembering to.

SCOPE. Only posts carrying their OWN FAQPage in the body can drift. When a post
has none, `faq_schema()` in build.py generates one FROM the visible questions at
render time, so those pages are in sync by construction (the money page works
this way). This gate covers every post with hand-written schema: 159 as of
2026-08-30, all currently in sync, no exceptions list.

EXTRACTION IS BORROWED ON PURPOSE. The heading pattern and section scoping come
from `fix_faq_schema.py`, whose `_FAQ_HEADING` was enumerated from the corpus
(157 "Frequently Asked Questions", 4 "Preguntas frecuentes", 4 "Common
Questions", 2 Arabic) rather than guessed, and whose `visible_pairs()` bounds a
section at the next heading of the same or higher level. A first draft of this
file used a hand-rolled English-only `<h2>` regex; it silently skipped 42 posts
and reported 3 false drifts caused by grabbing `<h3>`s from outside the FAQ.
Codex adversarial review caught it. Do not re-hand-roll the extractor: import it.

Run: python3 -m pytest scripts/test_faq_schema_sync.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_faq_schema import visible_pairs  # noqa: E402  (corpus-verified extractor)

POSTS = Path(__file__).resolve().parents[1] / "posts"
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

# Every post carrying hand-written FAQ schema was in sync when this gate landed.
# There is deliberately NO allowlist: an exceptions list that only checks its
# entries are still broken is not a ratchet, it is a mute button (anyone can add
# a newly drifted slug and the suite goes green). If a post drifts, fix the post.
EXPECTED_MIN_SCOPE = 150


def schema_questions(html: str) -> list[str] | None:
    """The Q&A the search engine is told about. None when the body carries no
    FAQPage, which means build.py generates it from the visible questions."""
    found = None
    for m in LD.finditer(html):
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if obj.get("@type") == "FAQPage":
            found = [q.get("name", "") for q in obj.get("mainEntity", [])]
    return found


def visible_questions(html: str) -> list[str]:
    """The Q&A a human sees, in page order."""
    return [q for q, _ in visible_pairs(html)]


def _in_scope():
    """(slug, visible, schema) for every post carrying hand-written FAQ schema."""
    out = []
    files = sorted(POSTS.glob("*.json"))
    assert len(files) > 100, f"suspiciously few posts under {POSTS} ({len(files)})"
    for path in files:
        html = json.loads(path.read_text(encoding="utf-8")).get("html_content") or ""
        sch = schema_questions(html)
        if sch is None:
            continue
        out.append((path.stem, visible_questions(html), sch))
    return out


def test_gate_has_something_to_check():
    """Guard the guard. If a refactor moves FAQ JSON-LD out of post bodies, or
    the borrowed heading pattern stops matching, this file would pass while
    checking nothing."""
    scope = _in_scope()
    assert len(scope) >= EXPECTED_MIN_SCOPE, (
        f"only {len(scope)} posts carry FAQPage schema (expected >= "
        f"{EXPECTED_MIN_SCOPE}) — the detector has probably stopped matching. "
        f"Check fix_faq_schema._FAQ_HEADING before trusting a pass."
    )
    empty = [s for s, vis, _ in scope if not vis]
    assert not empty, (
        f"these posts have FAQ schema but no visible questions the extractor can "
        f"find — a silent skip is how the first version of this gate hid 42 "
        f"posts: {empty[:10]}"
    )


def test_visible_faq_matches_schema():
    """Structured data must list exactly the visible questions, in order."""
    problems = []
    for slug, vis, sch in _in_scope():
        if vis == sch:
            continue
        only_vis = [q for q in vis if q not in sch]
        only_sch = [q for q in sch if q not in vis]
        problems.append(
            f"{slug}: visible={len(vis)} schema={len(sch)}"
            + (f"\n    visible only: {only_vis}" if only_vis else "")
            + (f"\n    schema only:  {only_sch}" if only_sch else "")
            + ("\n    same questions, different order" if not only_vis and not only_sch else "")
        )
    assert not problems, (
        "FAQ structured data disagrees with the visible FAQ. Edit BOTH sides:\n"
        + "\n".join(problems)
    )


def _replace_faq_block(html: str, new_questions: list[str]) -> str:
    """Rewrite the FAQPage script block to carry exactly `new_questions`.
    Done through json, not string surgery, so the fixture cannot break on
    whitespace or escaping."""
    for m in LD.finditer(html):
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if obj.get("@type") != "FAQPage":
            continue
        entities = obj["mainEntity"]
        by_name = {q.get("name", ""): q for q in entities}
        obj["mainEntity"] = [by_name[n] for n in new_questions]
        block = '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"
        return html[: m.start()] + block + html[m.end():]
    raise AssertionError("no FAQPage block found to mutate")


def test_detector_catches_drift_in_real_html():
    """Mutate a real post's HTML and run it back through the PARSERS. Comparing
    two lists proves Python works; this proves the extraction does."""
    scope = [s for s in _in_scope() if len(s[1]) > 2]
    assert scope, "no multi-question post available as a fixture"
    slug, _, _ = scope[0]
    html = json.loads((POSTS / f"{slug}.json").read_text(encoding="utf-8"))["html_content"]
    sch = schema_questions(html)
    assert visible_questions(html) == sch, "fixture must start in sync"

    # 1. Schema loses a question the page still shows.
    dropped = _replace_faq_block(html, sch[:-1])
    assert len(schema_questions(dropped)) == len(sch) - 1, "mutation should remove one question"
    assert visible_questions(dropped) != schema_questions(dropped), (
        "parsers did not notice a question missing from the schema"
    )

    # 2. Same questions, wrong order. Order matters: the JSON-LD is what the
    #    engine reads back, and a reordered list is a different answer set.
    reordered = _replace_faq_block(html, list(reversed(sch)))
    assert sorted(schema_questions(reordered)) == sorted(sch), "reorder must keep the same set"
    assert visible_questions(reordered) != schema_questions(reordered), (
        "parsers did not notice reordered schema questions"
    )

    # 3. Page changes a visible question the schema still claims.
    renamed = html.replace(">" + visible_questions(html)[-1] + "</h3>", ">Something Else Entirely</h3>", 1)
    if renamed != html:
        assert visible_questions(renamed) != schema_questions(renamed), (
            "parsers did not notice a changed visible question"
        )
