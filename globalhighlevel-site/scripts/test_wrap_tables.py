#!/usr/bin/env python3
"""Tests for build.py's wrap_tables render pass (v0.3.8.0): bare <table>
elements get a .table-wrap scroll container; tables already inside an
overflow container (assemble_spoke output) are left alone.

Run: python3 scripts/test_wrap_tables.py  (or via pytest)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build

FAILED = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        FAILED.append(name)
    assert cond, name


def test_bare_table_gets_wrapped():
    h = build.wrap_tables('<p>a</p><table><tr><td>x</td></tr></table><p>b</p>')
    check("bare: wrapped in .table-wrap",
          '<div class="table-wrap"><table><tr><td>x</td></tr></table></div>' in h)
    check("bare: surrounding content intact", h.startswith('<p>a</p>') and h.endswith('<p>b</p>'))


def test_prewrapped_table_left_alone():
    src = '<div style="overflow-x:auto"><table><tr><td>x</td></tr></table></div>'
    h = build.wrap_tables(src)
    check("prewrapped: unchanged", h == src)
    src2 = '<div class="table-wrap"><table><tr><td>y</td></tr></table></div>'
    check("table-wrap: unchanged", build.wrap_tables(src2) == src2)


def test_multiple_tables_mixed():
    src = ('<table><tr><td>1</td></tr></table>'
           '<div style="overflow-x:auto"><table><tr><td>2</td></tr></table></div>'
           '<table><tr><td>3</td></tr></table>')
    h = build.wrap_tables(src)
    check("mixed: two bare tables wrapped", h.count('class="table-wrap"') == 2)
    check("mixed: prewrapped not double-wrapped",
          '<div style="overflow-x:auto"><table><tr><td>2</td></tr></table></div>' in h)


def test_wrapper_variants_recognized():
    # spaced overflow style and multi-class wrappers also count as pre-wrapped
    s1 = '<div style="overflow-x: auto"><table><tr><td>a</td></tr></table></div>'
    check("variant: spaced overflow-x untouched", build.wrap_tables(s1) == s1)
    s2 = '<div class="foo table-wrap bar"><table><tr><td>b</td></tr></table></div>'
    check("variant: multi-class table-wrap untouched", build.wrap_tables(s2) == s2)
    # the three wrapper styles that actually exist in the posts corpus —
    # pinned so a future regex tightening can't silently double-wrap live posts
    for style in ('overflow-x:auto;', 'overflow-x:auto;margin-bottom:28px;',
                  'overflow-x:auto;margin:20px 0;'):
        s = f'<div style="{style}"><table><tr><td>c</td></tr></table></div>'
        check(f"corpus variant untouched: {style}", build.wrap_tables(s) == s)


def test_known_limitations_pinned():
    # nested tables would be mangled (non-greedy match) — none exist in the
    # corpus; this pins the CURRENT behavior so a corpus change surfaces it
    nested = '<table><tr><td><table><tr><td>x</td></tr></table></td></tr></table>'
    h = build.wrap_tables(nested)
    check("limitation: nested tables close wrapper early (documented)",
          h.startswith('<div class="table-wrap"><table>'))
    # lowercase-only contract: uppercase <TABLE> is not wrapped
    up = '<TABLE><TR><TD>x</TD></TR></TABLE>'
    check("limitation: uppercase tables skipped (documented)",
          build.wrap_tables(up) == up)


def test_no_table_passthrough():
    check("no table: identity", build.wrap_tables('<p>plain</p>') == '<p>plain</p>')
    check("empty: identity", build.wrap_tables('') == '')


def test_table_with_attributes_wrapped():
    h = build.wrap_tables('<table class="x" style="width:50%"><tr><td>z</td></tr></table>')
    check("attrs: wrapped despite attributes",
          h.startswith('<div class="table-wrap"><table class="x"'))


def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith('test_') and callable(v)]
    for t in tests:
        print(t.__name__)
        try:
            t()
        except AssertionError:
            pass
    print(f"\n{'PASS' if not FAILED else 'FAIL'} — {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
