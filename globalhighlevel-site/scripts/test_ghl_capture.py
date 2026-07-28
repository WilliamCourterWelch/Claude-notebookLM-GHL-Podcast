#!/usr/bin/env python3
"""Tests for the ghl-capture pipeline (pure-Python, no browser, no network).

Run: python3 scripts/test_ghl_capture.py
Exits 0 if all pass, 1 otherwise. Uses temp dirs; never touches real posts/images.
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
import types
from pathlib import Path

import ghl_capture_lib as lib
import ghl_optimize_wire as ow

FAILED = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        FAILED.append(name)
        # Under pytest a silent append would leave the test green (vacuous
        # gate); raise so pytest reports the real failure.
        if os.environ.get("PYTEST_CURRENT_TEST"):
            raise AssertionError(name)


@contextlib.contextmanager
def _temp_site():
    """Point lib's SITE/POSTS/IMAGES/CAPTURES at a temp tree; restore on exit.
    Single implementation shared by the standalone runner and the pytest
    fixture so the two entry points can never drift."""
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
            yield root
        finally:
            lib.SITE, lib.POSTS, lib.IMAGES, lib.CAPTURES = orig


def with_temp_site(fn):
    with _temp_site() as root:
        fn(root)


try:  # pytest collects the test_* functions; give it the same temp-site `root`
    import pytest

    @pytest.fixture
    def root():
        with _temp_site() as r:
            yield r
except ImportError:  # standalone `python3 scripts/test_ghl_capture.py` path
    pass


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


def test_safe_component(root):
    print("test_safe_component")
    for bad in ["../evil", "/etc/passwd", "a/b", "..", "", "x;rm", "foo bar"]:
        try:
            lib.safe_component(bad, "x"); check(f"rejects {bad!r}", False)
        except ValueError:
            check(f"rejects {bad!r}", True)
    for ok in ["foo", "ghl-integraciones-pagos-es", "es-mx", "a.b_c-1"]:
        check(f"accepts {ok!r}", lib.safe_component(ok, "x") == ok)


def _make_raw(lang, name):
    from PIL import Image
    (lib.CAPTURES / lang).mkdir(parents=True, exist_ok=True)
    p = lib.CAPTURES / lang / f"{name}.png"
    Image.new("RGB", (40, 30), (10, 20, 30)).save(p)
    return f"captures/{lang}/{name}.png"


def test_optimize_attested_gate(root):
    print("test_optimize_attested_gate")
    raw = _make_raw("es-mx", "r")
    m = {"slug": "s", "lang": "es-mx",
         "images": [{"name": "r", "raw": raw, "attested": False, "published": None}]}
    lib.save_manifest("s", "es-mx", m)
    args = types.SimpleNamespace(slug="s", lang="es-mx", max_width=1200)
    ow.cmd_optimize(args)
    check("unattested NOT published", lib.load_manifest("s", "es-mx")["images"][0]["published"] is None)
    m2 = lib.load_manifest("s", "es-mx"); m2["images"][0]["attested"] = True
    lib.save_manifest("s", "es-mx", m2)
    ow.cmd_optimize(args)
    pub = lib.load_manifest("s", "es-mx")["images"][0]["published"]
    check("attested gets published", bool(pub) and (lib.IMAGES / pub.split('/images/')[1]).exists())


def test_wire_attested_gate(root):
    print("test_wire_attested_gate")
    raw = _make_raw("es-mx", "w")
    (lib.IMAGES / "es-mx").mkdir(parents=True, exist_ok=True)
    from PIL import Image
    Image.new("RGB", (10, 10)).save(lib.IMAGES / "es-mx" / "s-1.png")
    m = {"slug": "s", "lang": "es-mx", "images": [{"name": "w", "raw": raw,
         "attested": False, "published": "/images/es-mx/s-1.png"}]}
    lib.save_manifest("s", "es-mx", m)
    write_post("s", "<h2>x</h2><p>body</p>")
    a = types.SimpleNamespace(post="s", image="/images/es-mx/s-1.png", alt="a",
                              caption="c", after="</p>")
    try:
        ow.cmd_wire(a); check("refuses un-attested wire", False)
    except SystemExit:
        check("refuses un-attested wire", True)
    m2 = lib.load_manifest("s", "es-mx"); m2["images"][0]["attested"] = True
    lib.save_manifest("s", "es-mx", m2)
    ow.cmd_wire(a)
    check("attested wire lands", "/images/es-mx/s-1.png" in lib.load_post("s")["html_content"])
    # path traversal in --image is refused
    bad = types.SimpleNamespace(post="s", image="/images/../../etc/x.png", alt="a",
                                caption="c", after="</p>")
    try:
        ow.cmd_wire(bad); check("refuses traversal --image", False)
    except SystemExit:
        check("refuses traversal --image", True)


def test_orphan_check_failclosed(root):
    print("test_orphan_check_failclosed")
    (lib.POSTS / "broken.json").write_text("{ not json", encoding="utf-8")
    res = lib.orphan_check()
    check("corrupt post surfaced", "broken.json" in res.get("unreadable_posts", []))


def test_pii_checklist_in_skill(root):
    print("test_pii_checklist_in_skill")
    skill = Path(__file__).resolve().parents[2] / ".claude/skills/ghl-capture/SKILL.md"
    if not skill.exists():
        check("SKILL.md present", False); return
    text = skill.read_text(encoding="utf-8")
    for item in lib.PII_CHECKLIST:
        check(f"checklist in skill: {item[:24]}...", item in text)


def main():
    for t in (test_next_index, test_orphan_check, test_figure_and_wire, test_save_post_roundtrip,
              test_safe_component, test_optimize_attested_gate, test_wire_attested_gate,
              test_orphan_check_failclosed, test_pii_checklist_in_skill):
        with_temp_site(t)
    print()
    if FAILED:
        print(f"FAILED: {len(FAILED)} -> {FAILED}")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
