#!/usr/bin/env python3
"""Tests for the ghl-capture pipeline (pure-Python, no browser, no network).

Run: python3 scripts/test_ghl_capture.py
Exits 0 if all pass, 1 otherwise. Uses temp dirs; never touches real posts/images.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import ghl_capture_lib as lib

FAILED = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        FAILED.append(name)


def with_temp_site(fn):
    """Point lib's SITE/POSTS/IMAGES/CAPTURES at a temp tree, run fn, restore."""
    orig = (lib.SITE, lib.POSTS, lib.IMAGES, lib.CAPTURES)
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        lib.SITE = root
        lib.POSTS = root / "posts"
        lib.IMAGES = root / "images"
        lib.CAPTURES = root / "captures"
        for p in (lib.POSTS, lib.IMAGES, lib.CAPTURES):
            p.mkdir(parents=True)
        try:
            fn(root)
        finally:
            lib.SITE, lib.POSTS, lib.IMAGES, lib.CAPTURES = orig


def write_post(slug, html_content, language="es"):
    lib.POSTS.joinpath(f"{slug}.json").write_text(
        json.dumps({"slug": slug, "language": language, "html_content": html_content},
                   ensure_ascii=False, indent=2),
        encoding="utf-8")


def touch_image(rel):  # rel like es-mx/foo.png
    p = lib.IMAGES / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\x89PNG\r\n")  # not a real PNG; orphan-check only stats names


def test_next_index(root):
    print("test_next_index")
    touch_image("es-mx/mypost-1.png")
    touch_image("es-mx/mypost-3.png")
    touch_image("es-mx/other-9.png")
    check("max+1 ignoring other slugs", lib.next_index("mypost", "es-mx") == 4)
    check("fresh slug starts at 1", lib.next_index("brandnew", "es-mx") == 1)


def test_orphan_check(root):
    print("test_orphan_check")
    touch_image("es-mx/used-1.png")
    touch_image("es-mx/shared-1.png")
    touch_image("es-mx/orphan-1.png")          # referenced by nobody -> orphan
    write_post("a", 'x <img src="/images/es-mx/used-1.png"> y '
                    '<img src="/images/es-mx/shared-1.png">')
    write_post("b", 'q <img src="/images/es-mx/shared-1.png"> '   # reuse: fine
                    '<img src="/images/es-mx/missing-1.png"> r')  # broken
    res = lib.orphan_check()
    check("orphan detected", res["orphans"] == ["/images/es-mx/orphan-1.png"])
    check("broken detected", res["broken"] == ["/images/es-mx/missing-1.png"])
    check("shared image is NOT an orphan", "/images/es-mx/shared-1.png" not in res["orphans"])
    check("reuse across 2 posts allowed",
          set(res["referenced"]["/images/es-mx/shared-1.png"]) == {"a", "b"})


def test_figure_and_wire(root):
    print("test_figure_and_wire")
    frag = lib.figure_html("/images/es-mx/p-1.png", 'Tom & "Jerry" <ok>', "Caption <b> & co")
    check("figure uses post-figure class", 'class="post-figure"' in frag)
    check("alt attribute escaped", '&amp;' in frag and '&quot;' in frag and '&lt;ok&gt;' in frag)
    check("caption text escaped", "Caption &lt;b&gt; &amp; co" in frag)
    check("loading lazy present", 'loading="lazy"' in frag)

    body = "<h2>Pagos</h2><p>Texto del párrafo.</p><h2>Siguiente</h2>"
    out = lib.insert_after_marker(body, "</p>", frag)
    check("inserted right after </p>", out.startswith("<h2>Pagos</h2><p>Texto del párrafo.</p>" + frag))
    try:
        lib.insert_after_marker(body, "<nope>", frag)
        check("missing marker raises", False)
    except ValueError:
        check("missing marker raises", True)


def test_save_post_roundtrip(root):
    print("test_save_post_roundtrip")
    write_post("rt", "<p>café</p>")
    d = lib.load_post("rt")
    d["html_content"] += "<p>añadido</p>"
    lib.save_post("rt", d)
    raw = lib.post_path("rt").read_text(encoding="utf-8")
    check("non-ascii kept literal (ensure_ascii=False)", "café" in raw and "añadido" in raw)
    check("indent=2 preserved", '\n  "slug"' in raw)
    check("trailing newline", raw.endswith("\n"))


def main():
    for t in (test_next_index, test_orphan_check, test_figure_and_wire, test_save_post_roundtrip):
        with_temp_site(t)
    print()
    if FAILED:
        print(f"FAILED: {len(FAILED)} -> {FAILED}")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
