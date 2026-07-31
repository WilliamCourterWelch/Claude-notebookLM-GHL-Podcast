"""Tests for scripts/fix_faq_schema.py (v0.3.9.2).

The migration rewrites inline FAQPage JSON-LD from a post's own visible copy.
The dangerous failure modes are (a) stripping a post's only schema, and
(b) churning posts whose schema was already faithful. Both are pinned here.
"""
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fix_faq_schema as F  # noqa: E402


def _block(pairs):
    return ('<script type="application/ld+json">'
            + json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                          "mainEntity": [
                              {"@type": "Question", "name": q,
                               "acceptedAnswer": {"@type": "Answer", "text": a}}
                              for q, a in pairs]}, ensure_ascii=False)
            + "</script>")


def _faq_blocks(html):
    return [b for b in re.findall(F._LDJSON, html, re.S) if "FAQPage" in b]


def _questions(html):
    out = []
    for b in _faq_blocks(html):
        out += [q["name"] for q in json.loads(b.strip())["mainEntity"]]
    return out


VISIBLE = (
    "<h2>Frequently Asked Questions</h2>"
    "<h3>Does it work?</h3><p>Yes it works fine.</p>"
    "<h3>Is it free?</h3><p>No, it costs money.</p>"
)


def test_visible_pairs_extracts_h2_section():
    pairs = F.visible_pairs(VISIBLE)
    assert pairs == [("Does it work?", "Yes it works fine."),
                     ("Is it free?", "No, it costs money.")]


def test_visible_pairs_handles_h3_section_heading():
    """36 posts head their FAQ with <h3>, not <h2>. They must not be missed."""
    html = ("<h3>Frequently Asked Questions</h3>"
            "<h3>Does it work?</h3><p>Yes it works fine.</p>")
    assert F.visible_pairs(html) == [("Does it work?", "Yes it works fine.")]


def test_visible_pairs_handles_arabic_heading():
    html = ("<h2>الأسئلة الشائعة</h2>"
            "<h3>هل يعمل هذا؟</h3><p>نعم يعمل بشكل جيد.</p>")
    assert F.visible_pairs(html) == [("هل يعمل هذا؟", "نعم يعمل بشكل جيد.")]


def test_section_heading_itself_is_not_a_question():
    """The FAQ heading has no '?' so it must never become a schema entity."""
    for q, _ in F.visible_pairs(VISIBLE):
        assert "Frequently Asked" not in q


def test_ignores_h3_outside_faq_section():
    html = ("<h2>Setup steps</h2><h3>Step one?</h3><p>Do this.</p>"
            "<h2>Frequently Asked Questions</h2>"
            "<h3>Does it work?</h3><p>Yes it works fine.</p>")
    assert F.visible_pairs(html) == [("Does it work?", "Yes it works fine.")]


def test_duplicate_blocks_are_merged_to_one():
    html = VISIBLE + _block([("Does it work?", "Yes it works fine.")]) \
                   + _block([("Is it free?", "No, it costs money.")])
    assert len(_faq_blocks(html)) == 2
    new, _ = F.rewrite(html)
    assert new is not None
    assert len(_faq_blocks(new)) == 1
    assert set(_questions(new)) == {"Does it work?", "Is it free?"}


def test_orphan_question_is_dropped():
    """Schema asserting a Q&A absent from the page is the Google violation."""
    html = VISIBLE + _block([("Does it work?", "Yes it works fine."),
                             ("Ghost question?", "Never shown on the page.")])
    new, _ = F.rewrite(html)
    assert new is not None
    assert "Ghost question?" not in _questions(new)
    assert "Does it work?" in _questions(new)


def test_real_drift_is_resynced_to_visible():
    html = VISIBLE + _block([("Does it work?", "Actually it is broken and unusable."),
                             ("Is it free?", "No, it costs money.")])
    new, _ = F.rewrite(html)
    assert new is not None
    answers = {q["name"]: q["acceptedAnswer"]["text"]
               for q in json.loads(_faq_blocks(new)[0].strip())["mainEntity"]}
    assert answers["Does it work?"] == "Yes it works fine."


def test_trivial_whitespace_drift_is_left_alone():
    html = VISIBLE + _block([("Does it work?", "Yes it works   fine."),
                             ("Is it free?", "No, it costs money.")])
    new, reason = F.rewrite(html)
    assert new is None and reason == "no-defect"


def test_truncated_schema_answer_is_left_alone():
    """A schema answer that is a clean prefix of the visible one is faithful."""
    long_vis = ("<h2>Frequently Asked Questions</h2><h3>Does it work?</h3>"
                "<p>" + ("Yes it works fine and here is a great deal more detail. " * 4) + "</p>")
    full = F.visible_pairs(long_vis)[0][1]
    html = long_vis + _block([("Does it work?", full[:100])])
    new, reason = F.rewrite(html)
    assert new is None and reason == "no-defect"


def test_refuses_to_strip_when_no_visible_pairs():
    """Better a stale block than a post with no schema at all."""
    html = "<p>No FAQ section here at all.</p>" + _block([("Q?", "A.")])
    new, reason = F.rewrite(html)
    assert new is None and reason == "no-visible-pairs"
    assert len(_faq_blocks(html)) == 1


def test_post_without_schema_is_untouched():
    new, reason = F.rewrite(VISIBLE)
    assert new is None and reason == "no-schema"


def test_rebuilt_block_is_valid_json_and_wellformed():
    html = VISIBLE + _block([("Does it work?", "stale")])
    new, _ = F.rewrite(html)
    data = json.loads(_faq_blocks(new)[0].strip())
    assert data["@context"] == "https://schema.org"
    assert data["@type"] == "FAQPage"
    assert all(q["@type"] == "Question" for q in data["mainEntity"])
    assert all(q["acceptedAnswer"]["@type"] == "Answer" for q in data["mainEntity"])


def test_non_ascii_survives_rebuild_unescaped():
    html = ("<h2>Preguntas frecuentes</h2><h3>¿Funciona?</h3><p>Sí, funciona bien.</p>"
            + _block([("¿Funciona?", "obsoleto")]))
    new, _ = F.rewrite(html)
    assert "¿Funciona?" in new and "Sí, funciona bien." in new
    assert "\\u" not in _faq_blocks(new)[0]


def test_common_questions_heading_is_recognized():
    """4 posts head their FAQ 'Common Questions About X' rather than 'FAQ'."""
    html = ("<h3>Common Questions About Email Templates</h3>"
            "<h3>Can I edit templates later?</h3><p>Yes, any time.</p>")
    assert F.visible_pairs(html) == [("Can I edit templates later?", "Yes, any time.")]


def test_arabic_common_mistakes_heading_is_not_treated_as_faq():
    """'أخطاء شائعة' means 'common mistakes' -- not an FAQ section."""
    html = ("<h2>أخطاء شائعة يجب تجنبها</h2>"
            "<h3>هل يعمل هذا؟</h3><p>نعم.</p>")
    assert F.visible_pairs(html) == []


def test_drift_past_the_first_80_chars_is_not_treated_as_truncation():
    """Regression: comparing only a prefix let 5 real mismatches through."""
    head = "A" * 90
    vis = ("<h2>Frequently Asked Questions</h2><h3>Does it work?</h3>"
           "<p>" + head + " used by other users/accounts.</p>")
    html = vis + _block([("Does it work?", head + " used by other users or accounts.")])
    new, reason = F.rewrite(html)
    assert new is not None, "divergence past char 80 must count as real drift"
    answers = {q["name"]: q["acceptedAnswer"]["text"]
               for q in json.loads(_faq_blocks(new)[0].strip())["mainEntity"]}
    assert answers["Does it work?"].endswith("used by other users/accounts.")


def test_cta_block_after_faq_is_not_swallowed_into_last_answer():
    """Regression: the sibling CTA div leaked into 38 posts' schema answers.

    Google's structured-data policy forbids misleading/advertising content in
    structured data, so this is a policy violation, not just noise.
    """
    html = ('<h2>Frequently Asked Questions</h2>'
            '<h3>Does it work?</h3><p>Yes it works fine.</p>'
            '</div>'
            '<div style="text-align:center;">'
            '<p>Ready to Get Started with GoHighLevel?</p>'
            '<p>Claim Your Free Trial &rarr;</p></div>'
            + _block([("Does it work?", "stale")]))
    new, _ = F.rewrite(html)
    answers = {q["name"]: q["acceptedAnswer"]["text"]
               for q in json.loads(_faq_blocks(new)[0].strip())["mainEntity"]}
    assert answers["Does it work?"] == "Yes it works fine."
    for a in answers.values():
        assert "Ready to Get Started" not in a
        assert "Claim Your Free Trial" not in a
    # The CTA must survive in the visible HTML. We bound the answer; we never
    # delete page content.
    assert "Claim Your Free Trial" in new


def test_extraction_shortfall_refuses_rather_than_dropping_questions():
    """One recovered pair must not justify discarding four existing ones."""
    html = ("<h2>Frequently Asked Questions</h2>"
            "<h3>Only parseable one?</h3><p>Yes.</p>"
            + _block([("Only parseable one?", "Yes."), ("Q2?", "A2"), ("Q3?", "A3"),
                      ("Q4?", "A4"), ("Q5?", "A5")]))
    new, reason = F.rewrite(html)
    assert new is None and reason == "extraction-shortfall"
    assert len(_questions(html)) == 5, "original schema must be left intact"


def test_substring_containment_is_not_mistaken_for_truncation():
    """`_norm(a) in _norm(v)` masked drift; only a true PREFIX is faithful."""
    vis = ("<h2>Frequently Asked Questions</h2><h3>Does it work?</h3>"
           "<p>Actually no. Yes it works fine. But only sometimes.</p>")
    html = vis + _block([("Does it work?", "Yes it works fine.")])
    new, reason = F.rewrite(html)
    assert new is not None, "mid-string containment is drift, not truncation"


def test_split_bold_question_and_answer_paragraphs():
    """4 posts use <p><strong>Q?</strong></p><p>A</p>."""
    html = ("<h2>Frequently Asked Questions</h2>"
            "<p><strong>Is it free?</strong></p><p>No, it costs money.</p>")
    assert ("Is it free?", "No, it costs money.") in F.visible_pairs(html)
