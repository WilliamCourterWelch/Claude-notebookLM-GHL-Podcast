#!/usr/bin/env python3
"""Tests for assemble_spoke.py: markdown tables (flush_tbl), ordered/nested
lists, language-keyed bios/CTA/hub labels (BIOS et al.), URL hardening
(scheme allowlist, attribute escaping, host-based rel), and main() end-to-end.

Run: python3 scripts/test_assemble_spoke.py   (or via pytest: python3 -m pytest scripts/ -q)
Exits 0 if all pass, 1 otherwise. No network, no real posts/: main() end-to-end
runs write manifests + section drafts to a temp dir and point man["out"] there.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # globalhighlevel-site/
import assemble_spoke as asp  # import-safe: main() is __main__-guarded

FAILED = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        FAILED.append(name)
    assert cond, name  # make failures visible to pytest too


AFF = asp.AFFILIATE_DEFAULT


# --- table parsing: flush_tbl -------------------------------------------------

def test_basic_table():
    md = ("Intro paragraph.\n"
          "\n"
          "| Plan | Price |\n"
          "| --- | --- |\n"
          "| Starter | $97 |\n"
          "| Pro | $297 |\n"
          "\n"
          "Closing.")
    html = asp.md_to_html(md, AFF)
    check("basic: separator row dropped", '---' not in html)
    check("basic: thead from first row",
          '<thead><tr><th>Plan</th><th>Price</th></tr></thead>' in html)
    check("basic: tbody rows in order",
          '<tbody><tr><td>Starter</td><td>$97</td></tr>'
          '<tr><td>Pro</td><td>$297</td></tr></tbody>' in html)
    check("basic: one table only", html.count('<table>') == 1)
    check("basic: para before table flushed first",
          html.index('<p>Intro paragraph.</p>') < html.index('<table>'))
    check("basic: para after table", '<p>Closing.</p>' in html)


def test_alignment_separators_dropped():
    md = ("| A | B | C |\n"
          "|:---|:---:|---:|\n"
          "| 1 | 2 | 3 |")
    html = asp.md_to_html(md, AFF)
    check("align: colon separators dropped", ':-' not in html and '-:' not in html)
    check("align: header kept", '<th>A</th><th>B</th><th>C</th>' in html)
    check("align: body kept", '<td>1</td><td>2</td><td>3</td>' in html)


def test_table_without_separator():
    # no |---| row: first row is still promoted to thead
    html = asp.md_to_html("| H1 | H2 |\n| a | b |", AFF)
    check("nosep: first row is thead", '<thead><tr><th>H1</th><th>H2</th></tr></thead>' in html)
    check("nosep: second row is tbody", '<tbody><tr><td>a</td><td>b</td></tr></tbody>' in html)


def test_separator_only_and_empty_tables():
    check("only separators: no table emitted",
          '<table>' not in asp.md_to_html("|---|---|\n| :--- | ---: |", AFF))
    check("lone empty pipe row: no table emitted",
          '<table>' not in asp.md_to_html("|", AFF))
    check("empty input: empty output", asp.md_to_html("", AFF) == '')


def test_ragged_rows_do_not_crash():
    # malformed: body rows with fewer/more cells than the header
    html = asp.md_to_html("| A | B |\n| --- | --- |\n| only |\n| 1 | 2 | 3 |", AFF)
    check("ragged: short row renders its one cell", '<tr><td>only</td></tr>' in html)
    check("ragged: long row renders all three cells",
          '<tr><td>1</td><td>2</td><td>3</td></tr>' in html)
    check("ragged: header unaffected", '<th>A</th><th>B</th>' in html)


def test_inline_markdown_and_escaping_in_cells():
    md = ("| Feature | Verdict |\n"
          "| --- | --- |\n"
          "| **Voice AI** | [pricing](https://www.gohighlevel.com/pricing?fp_ref=x) |\n"
          "| *italic* & a < b | [hub](/blog/some-hub/) |")
    html = asp.md_to_html(md, AFF)
    check("cells: bold converted", '<td><strong>Voice AI</strong></td>' in html)
    check("cells: italic converted", '<em>italic</em>' in html)
    check("cells: < escaped", 'a &lt; b' in html)
    check("cells: external link gets nofollow rel",
          '<a href="https://www.gohighlevel.com/pricing?fp_ref=x" target="_blank" '
          'rel="nofollow noopener">pricing</a>' in html)
    check("cells: internal link stays followed",
          '<a href="/blog/some-hub/">hub</a>' in html)


def test_table_terminated_by_text_line():
    # a non-blank, non-pipe line ends the table (no blank line needed)
    html = asp.md_to_html("| A |\n| 1 |\nAfter text.", AFF)
    check("terminate: table closed before text",
          html.index('</table>') < html.index('<p>After text.</p>'))


def test_table_at_end_of_document_flushes():
    html = asp.md_to_html("Para.\n\n| A | B |\n| --- | --- |\n| 1 | 2 |", AFF)
    check("eof: trailing table emitted", '<td>1</td><td>2</td>' in html)
    check("eof: table is last element", html.rstrip().endswith('</table></div>'))


def test_two_tables_split_by_blank_line():
    html = asp.md_to_html("| A |\n| 1 |\n\n| B |\n| 2 |", AFF)
    check("split: blank line yields two tables", html.count('<table>') == 2)


def test_table_adjacent_to_list():
    html = asp.md_to_html("- item one\n- item two\n| A |\n| 1 |", AFF)
    check("list: ul flushed before table",
          html.index('</ul>') < html.index('<table>'))
    check("list: items intact", '<li>item one</li><li>item two</li>' in html)


def test_table_then_blockquote():
    html = asp.md_to_html("| A |\n| 1 |\n> a quote", AFF)
    check("tbl->bq: table flushed before blockquote",
          html.index('</table>') < html.index('<blockquote>'))
    check("tbl->bq: quote text intact", '<blockquote><p>a quote</p></blockquote>' in html)


def test_blockquote_then_table():
    html = asp.md_to_html("> a quote\n| A |\n| 1 |", AFF)
    check("bq->tbl: blockquote flushed before table",
          html.index('</blockquote>') < html.index('<table>'))
    check("bq->tbl: table intact", '<th>A</th>' in html)


def test_table_between_headings():
    html = asp.md_to_html("## Pricing\n| A |\n| 1 |\n### Next", AFF)
    check("headings: h2 before table", html.index('<h2>Pricing</h2>') < html.index('<table>'))
    check("headings: table closed before next heading",
          html.index('</table>') < html.index('<h2>Next</h2>'))


def test_affiliate_cta_blockquote_still_works_next_to_table():
    md = ("| Plan | Price |\n"
          "| --- | --- |\n"
          "| Starter | $97 |\n"
          "\n"
          f"> ## **Try it free**\n"
          f"> [Start your 30-day trial]({AFF})\n"
          "> No long-term contract.")
    html = asp.md_to_html(md, AFF)
    check("cta: table rendered", '<td>$97</td>' in html)
    check("cta: cta-box rendered after table",
          html.index('</table>') < html.index('cta-box'))
    check("cta: affiliate button link kept", 'cta-btn' in html and 'fp_ref=' in html)


# --- BIOS: language-aware author bio -----------------------------------------

def test_bios_dict_shape():
    check("BIOS: exactly es+en keys", set(asp.BIOS) == {'es', 'en'})
    check("BIOS: es is the Spanish bio",
          asp.BIOS['es'] is asp.BIO_ES and 'Sobre el autor' in asp.BIO_ES)
    check("BIOS: en is the English bio",
          asp.BIOS['en'] is asp.BIO_EN and 'About the author' in asp.BIO_EN)
    check("BIOS: both bios carry the contact mailto",
          all('mailto:bill@reiamplifi.com' in b for b in asp.BIOS.values()))
    check("BIOS: both bios disclose the affiliate relationship",
          'afiliado de HighLevel' in asp.BIO_ES and 'HighLevel affiliate' in asp.BIO_EN)


def _run_main(tmp, language=None, hub_slug=None, hub_title=None):
    """Drive main() end-to-end with a minimal manifest + one section draft."""
    sec = Path(tmp) / "section.md"
    sec.write_text("# S\n## Draft\nHello world.\n\n| Plan | Price |\n| --- | --- |\n"
                   "| Starter | $97 |\n", encoding='utf-8')
    out = Path(tmp) / "out.json"
    man = {"slug": "s", "title": "T", "description": "d", "category": "Guides",
           "tags": ["a"], "publishedAt": "2026-07-29T00:00:00", "topic": "AI & Automation",
           "sections": [str(sec)], "out": str(out)}
    if language is not None:
        man["language"] = language
    if hub_slug is not None:
        man["hub_slug"] = hub_slug
    if hub_title is not None:
        man["hub_title"] = hub_title
    manp = Path(tmp) / "man.json"
    manp.write_text(json.dumps(man), encoding='utf-8')
    saved = sys.argv
    try:
        sys.argv = ["assemble_spoke.py", str(manp)]
        asp.main()
    finally:
        sys.argv = saved
    return json.loads(out.read_text(encoding='utf-8'))


def test_bio_selection_en():
    with tempfile.TemporaryDirectory() as tmp:
        post = _run_main(tmp, language="en")
    check("bio en: English bio appended", post["html_content"].endswith(asp.BIO_EN))
    check("bio en: Spanish bio absent", 'Sobre el autor' not in post["html_content"])
    check("bio en: section table made it into the post",
          '<th>Plan</th><th>Price</th>' in post["html_content"])


def test_bio_selection_es():
    with tempfile.TemporaryDirectory() as tmp:
        post = _run_main(tmp, language="es")
    check("bio es: Spanish bio appended", post["html_content"].endswith(asp.BIO_ES))
    check("bio es: English bio absent", 'About the author' not in post["html_content"])


def test_bio_selection_en_in():
    # regional variant truncates to 'en' via language[:2]
    with tempfile.TemporaryDirectory() as tmp:
        post = _run_main(tmp, language="en-IN")
    check("bio en-IN: maps to English bio", post["html_content"].endswith(asp.BIO_EN))
    check("bio en-IN: language field preserved verbatim", post["language"] == "en-IN")


def test_bio_selection_unknown_language_falls_back_en():
    with tempfile.TemporaryDirectory() as tmp:
        post = _run_main(tmp, language="ar")
    check("bio ar: unknown language falls back to English bio",
          post["html_content"].endswith(asp.BIO_EN))


def test_missing_language_key_raises():
    # language is a required manifest key: main() must fail loudly (KeyError)
    # before writing any output, not silently default a language.
    with tempfile.TemporaryDirectory() as tmp:
        try:
            _run_main(tmp, language=None)
            check("missing language: KeyError raised", False)
        except KeyError:
            check("missing language: KeyError raised", True)
        check("missing language: no output file written",
              not (Path(tmp) / "out.json").exists())


def test_hub_link_prepended():
    with tempfile.TemporaryDirectory() as tmp:
        post = _run_main(tmp, language="es", hub_slug="hub-x")
    check("hub: link paragraph prepended",
          post["html_content"].startswith('<p class="hub-link">'))
    check("hub: href targets the hub slug", '/blog/hub-x/' in post["html_content"])
    check("hub es: Spanish label", 'Parte de la guía' in post["html_content"])


def test_hub_link_english_label():
    with tempfile.TemporaryDirectory() as tmp:
        post = _run_main(tmp, language="en", hub_slug="hub-y", hub_title="Hub Y")
    check("hub en: English label", 'Part of the guide' in post["html_content"])
    check("hub en: no Spanish label leak", 'Parte de la guía' not in post["html_content"])


def test_all_dash_data_row_is_kept():
    # '| - | - |' below the separator is a legitimate "not included" data row
    html = asp.md_to_html("| Feature | Free |\n| --- | --- |\n| - | - |", AFF)
    check("dash row: kept as data", '<tr><td>-</td><td>-</td></tr>' in html)


def test_escaped_pipe_limitation_pinned():
    # documented limitation: \| is split like a normal pipe (no GFM escape support)
    html = asp.md_to_html("| A | B |\n| --- | --- |\n| use \\| pipe | x |", AFF)
    check("escaped pipe: split on literal | (known limitation)",
          '<td>use \\</td><td>pipe</td><td>x</td>' in html)


def test_unsafe_link_scheme_dropped():
    html = asp.md_to_html("[click](javascript:alert(1))", AFF)
    check("scheme: javascript link stripped to text",
          '<a' not in html and 'click' in html)
    html2 = asp.md_to_html('[q](https://x.com/a"b)', AFF)
    check("scheme: quote in URL escaped in attribute", 'href="https://x.com/a&quot;b"' in html2)


def test_numbered_list_renders_as_ol():
    html = asp.md_to_html("1. first\n2. second\n3. third", AFF)
    check("ol: single ordered list", html.count('<ol>') == 1)
    check("ol: items in order", '<li>first</li><li>second</li><li>third</li>' in html)


def test_numbered_list_with_nested_bullets():
    md = "1. top one\n2. top two\n   - sub a\n   - sub b\n3. top three"
    html = asp.md_to_html(md, AFF)
    check("nested: one ol, numbering not restarted", html.count('<ol>') == 1)
    check("nested: bullets nest inside item two",
          '<li>top two<ul><li>sub a</li><li>sub b</li></ul></li>' in html)
    check("nested: item three still in the same ol",
          html.index('<li>top three</li>') < html.index('</ol>'))


def test_unindented_bullet_after_ol_is_top_level():
    # an UNINDENTED bullet after a numbered list starts a new top-level ul,
    # it does not get swallowed as a nested item of the last ol entry
    html = asp.md_to_html("1. one\n2. two\n- top bullet", AFF)
    check("unindented: ol closed before ul", html.index('</ol>') < html.index('<ul>'))
    check("unindented: bullet is top-level", '<ul><li>top bullet</li></ul>' in html)
    check("unindented: not nested in item two", '<li>two</li>' in html)


def test_table_wrapped_for_mobile_overflow():
    html = asp.md_to_html("| A | B |\n| --- | --- |\n| 1 | 2 |", AFF)
    check("overflow: table wrapped in scroll container",
          '<div style="overflow-x:auto"><table>' in html and '</table></div>' in html)


def test_query_string_url_not_double_escaped():
    # regression: inline() html-escapes text first (& -> &amp;), so the link
    # regex sees &amp; inside the URL — the href must un-escape before its own
    # single attribute-escape, or UTM params ship as amp;utm_source=... garbage
    md = "[trial](https://x.com/go?fp_ref=a&utm_source=b&utm_medium=c)"
    html = asp.md_to_html(md, AFF)
    check("utm: single-escaped ampersands in href",
          'href="https://x.com/go?fp_ref=a&amp;utm_source=b&amp;utm_medium=c"' in html)
    check("utm: no double-escape artifact", 'amp;amp;' not in html and 'amp;utm' not in
          html.replace('&amp;utm', ''))


def test_protocol_relative_url_dropped():
    html = asp.md_to_html("[x](//evil.example/path)", AFF)
    check("protocol-relative: link stripped to text", '<a' not in html and 'x' in html)


def test_cta_box_url_attribute_escaped():
    md = ('> ## **Go**\n'
          '> [Start](https://www.gohighlevel.com/x?fp_ref=amplifi-technologies12&utm_source=g)\n')
    html = asp.md_to_html(md, AFF)
    check("cta href: ampersand escaped once in attribute",
          'href="https://www.gohighlevel.com/x?fp_ref=amplifi-technologies12&amp;utm_source=g"' in html)


def test_valid_schemes_pass_through():
    check("mailto: link survives",
          '<a href="mailto:a@b.com">m</a>' in asp.md_to_html("[m](mailto:a@b.com)", AFF))
    check("uppercase HTTPS survives (case-insensitive allowlist)",
          '<a href="HTTPS://x.com/p"' in asp.md_to_html("[c](HTTPS://x.com/p)", AFF))


def test_host_based_rel_not_substring():
    # lookalike hosts are EXTERNAL (nofollow); internal paths containing
    # 'http' stay followed — rel is decided by parsed hostname, not substrings
    h1 = asp.md_to_html("[evil](https://globalhighlevel.com.evil.com/x)", AFF)
    check("lookalike host gets nofollow", 'rel="nofollow noopener"' in h1)
    h2 = asp.md_to_html("[real](https://www.globalhighlevel.com/blog/x/)", AFF)
    check("own subdomain stays followed", 'rel=' not in h2)
    h3 = asp.md_to_html("[guide](/blog/gohighlevel-http-guide/)", AFF)
    check("internal path containing 'http' stays followed", 'rel=' not in h3)


def test_hub_title_from_manifest_and_non_es_requirement():
    with tempfile.TemporaryDirectory() as tmp:
        post = _run_main(tmp, language="en", hub_slug="hub-z", hub_title="The AI Guide")
    check("hub_title: manifest value rendered", '>The AI Guide</a>' in post["html_content"])
    with tempfile.TemporaryDirectory() as tmp:
        try:
            _run_main(tmp, language="en", hub_slug="hub-z")
            check("hub_title: non-es without title raises", False)
        except SystemExit:
            check("hub_title: non-es without title raises", True)


def test_text_after_list_preserves_document_order():
    # a text line directly after a list (no blank) closes the list first,
    # so the rendered order matches the draft order
    h1 = asp.md_to_html("1. first\nNext paragraph", AFF)
    check("ol->text: list emitted before paragraph",
          h1.index('</ol>') < h1.index('<p>Next paragraph</p>'))
    h2 = asp.md_to_html("- item\nNext paragraph", AFF)
    check("ul->text: list emitted before paragraph",
          h2.index('</ul>') < h2.index('<p>Next paragraph</p>'))


def test_hub_title_and_slug_escaped():
    with tempfile.TemporaryDirectory() as tmp:
        post = _run_main(tmp, language="en", hub_slug='hub"x', hub_title="A <b>& Title")
    h = post["html_content"]
    check("hub: title html-escaped", 'A &lt;b&gt;&amp; Title' in h)
    check("hub: slug quote-escaped in href", 'href="/blog/hub&quot;x/"' in h)


def test_loose_numbered_list_limitation_pinned():
    # documented limitation: a blank line between numbered items splits the
    # list into separate <ol>s (numbering restarts) — keep lists tight
    html = asp.md_to_html("1. first\n\n2. second", AFF)
    check("loose list: splits into two ols (known limitation)",
          html.count('<ol>') == 2)


def test_cta_fallback_labels():
    check("cta fallback: es+en labels exist", set(asp.CTA_FALLBACK) == {'es', 'en'})
    # a CTA blockquote mentioning fp_ref with no parseable [label](url) link
    md = "> ## **Go**\n> sign up now fp_ref=amplifi"
    html_en = asp.md_to_html(md, AFF, lang='en')
    html_es = asp.md_to_html(md, AFF, lang='es')
    check("cta fallback: en label on en pages", asp.CTA_FALLBACK['en'] in html_en)
    check("cta fallback: es label on es pages", asp.CTA_FALLBACK['es'] in html_es)


def main():
    # discovery-based: direct-run always executes the same set pytest collects
    tests = [v for k, v in sorted(globals().items())
             if k.startswith('test_') and callable(v)]
    for t in tests:
        print(t.__name__)
        try:
            t()
        except AssertionError:
            pass  # already recorded in FAILED; keep running the rest
    print(f"\n{'PASS' if not FAILED else 'FAIL'} — {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
