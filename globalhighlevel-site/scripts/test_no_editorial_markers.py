#!/usr/bin/env python3
"""Regression gate: no editorial-debt markers in any post field.

The 2026-07-28 strip removed ~32 bracketed editor notes / fabricated-case
stubs from 26 firehose-era es posts ([NOTA EDITORIAL: ...], [SECCIÓN A
COMPLETAR...], [INCOMPLETO — AÑADIR AQUÍ], etc.). Future imports or the
research-wedge rebuild must never reintroduce the class.

Policy notes (intentional scope):
- ANY bracketed "[Nota:" / "[NOTA" is banned in published content, even a
  reader-facing footnote — use unbracketed prose for disclaimers. A trip
  here is deliberate, not a false positive; do not loosen the regex.
- Merge-field examples ([Client Name], [Fecha], [MERCADOPAGO LINK]) stay
  allowed: single short tokens, not editor-note phrasings.
- Known limitation: unbracketed meta-editorial prose (e.g. a heading like
  "Refrescar antes de publicar") can't be caught by pattern alone — that
  class is on the reviewer, not this gate.

Run: python3 -m pytest scripts/test_no_editorial_markers.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

POSTS = Path(__file__).resolve().parents[1] / "posts"

# Each alternative matches the *opening* of a known editor-note phrasing.
MARKER = re.compile(
    r"\[(?:"
    r"(?:NOTA|Nota|nota)(?: (?:EDITORIAL|editorial|PARA EDITOR|para editor))?\s*:"
    r"|SECCIÓN (?:A COMPLETAR|INCOMPLETA|PENDIENTE)"
    r"|CONTENIDO TRUNCADO"
    r"|CONTINUAR CON"
    r"|Continuará con"
    r"|Continúa con el contenido"
    r"|Continuar con detalles"
    r"|Aquí iría"
    r"|Esta sección (?:también )?(?:requiere|debe contener)"
    r"|Sección (?:pendiente|continúa|incompleta)"
    r"|INCOMPLETO"
    r"|AÑADIR AQUÍ"
    r"|POR COMPLETAR"
    r"|PENDIENTE DE"
    r"|FALTA(?:N)? "
    r"|COMPLETAR"
    r"|EXPANDIR"
    r")"
)

# Same-level heading immediately followed by another same-level heading (an
# empty section), or a heading as the very last thing in the body — the
# structural residue a bad strip leaves behind.
EMPTY_SECTION = re.compile(r"<h([23])>[^<]*</h\1>\s*(?=<h\1>|$)")


def _post_files():
    files = sorted(POSTS.glob("*.json"))
    # Vacuous-green guard: an empty/missing posts dir must fail loudly, not
    # pass by scanning nothing (corpus is ~900 posts).
    assert len(files) > 100, f"suspiciously few posts under {POSTS} ({len(files)})"
    return files


def test_no_editorial_markers_in_posts():
    offenders = []
    for path in _post_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        for field, value in data.items():
            if not isinstance(value, str):
                continue
            m = MARKER.search(value)
            if m:
                offenders.append(f"{path.name}:{field}: {value[m.start():m.start()+70]!r}")
    assert not offenders, (
        "Editorial-debt markers found in published post content "
        "(strip them or complete the section):\n" + "\n".join(offenders)
    )


def test_no_empty_or_trailing_heading_sections():
    offenders = []
    for path in _post_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        body = data.get("html_content") or ""
        m = EMPTY_SECTION.search(body)
        if m:
            offenders.append(f"{path.name}: {m.group(0)[:70]!r}")
    assert not offenders, (
        "Empty heading sections / trailing headings found (structural strip "
        "residue):\n" + "\n".join(offenders)
    )


if __name__ == "__main__":
    test_no_editorial_markers_in_posts()
    test_no_empty_or_trailing_heading_sections()
    print("ALL TESTS PASSED")
