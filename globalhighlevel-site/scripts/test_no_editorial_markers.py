#!/usr/bin/env python3
"""Regression gate: no editorial-debt markers in any post field.

The 2026-07-28 strip removed ~35 bracketed editor notes / fabricated-case
stubs from 27 firehose-era es posts ([NOTA EDITORIAL: ...], [SECCIÓN A
COMPLETAR...], [INCOMPLETO — AÑADIR AQUÍ], etc.). Future imports or the
research-wedge rebuild must never reintroduce the class.

Policy notes (intentional scope):
- ANY bracketed "[Nota ...:" / "[NOTA ...:" is banned in published content,
  even a reader-facing footnote — use unbracketed prose for disclaimers. A
  trip here is deliberate, not a false positive; do not loosen the regex.
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
# The Nota-opener is tolerant: any bracketed Nota-word with a colon within
# 50 chars ([NOTA DEL EDITOR: ...], [Nota importante: ...]) trips it.
MARKER = re.compile(
    r"\[(?:"
    r"(?:NOTA|Nota|nota)\b[^\]\n]{0,50}:"
    r"|(?i:SECCIÓN (?:A COMPLETAR|INCOMPLETA|PENDIENTE))"
    r"|CONTENIDO TRUNCADO"
    r"|CONTINUAR CON"
    r"|Continuará con"
    r"|Continúa con el contenido"
    r"|Continuar con detalles"
    r"|Aquí iría"
    r"|Esta sección (?:también )?(?:requiere|debe contener)"
    r"|Sección (?:pendiente|continúa|incompleta)"
    r"|(?i:INCOMPLETO)"
    r"|AÑADIR AQUÍ"
    r"|POR COMPLETAR"
    r"|PENDIENTE DE"
    r"|FALTA(?:N)?[ :]"
    r"|COMPLETAR"
    r"|EXPANDIR"
    r")"
)

# Structural strip residue, level-aware:
# - a same-level heading immediately following a heading = empty section
# - an h3 section closed immediately by an h2 = empty h3 section
# - a heading as the very last thing in the body
# Scope: bare headings and id=-anchored headings are CONTENT headings; a
# heading carrying style= (or other attributes) is box/chrome markup by
# corpus convention (FAQ boxes title with <h3 style=...> then h3 questions)
# and is exempt — flagging those false-positives on ~500 posts.
# (an h2 immediately followed by an h3 is a legitimate section-with-
#  subsection opener and is NOT flagged)
_H = r'(?:\s+id="[^"]*")?'
# tempered dot: heading content may contain inline tags but never a closing
# </hN>, so a lazy match can't backtrack across section boundaries
EMPTY_H2 = re.compile(r"<h2" + _H + r">(?:(?!</h2>).)*</h2>\s*(?=<h2[\s>]|$)", re.DOTALL)
EMPTY_H3 = re.compile(r"<h3" + _H + r">(?:(?!</h3>).)*</h3>\s*(?=<h[23][\s>]|$)", re.DOTALL)


def _walk_strings(value):
    """Yield every string nested anywhere in a post's JSON value
    (covers tldr lists, translations dicts, future nested fields)."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _walk_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_strings(item)


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
            for s in _walk_strings(value):
                m = MARKER.search(s)
                if m:
                    offenders.append(f"{path.name}:{field}: {s[m.start():m.start()+70]!r}")
    assert not offenders, (
        "Editorial-debt markers found in published post content "
        "(strip them or complete the section):\n" + "\n".join(offenders)
    )


def test_no_empty_or_trailing_heading_sections():
    offenders = []
    for path in _post_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        body = data.get("html_content") or ""
        for pat in (EMPTY_H2, EMPTY_H3):
            for m in pat.finditer(body):
                # a heading whose content is a link is a self-contained CTA
                # (e.g. <h3><a href=...>Start your free trial</a></h3>), not
                # an empty section promising content that never comes
                if "<a" in m.group(0):
                    continue
                offenders.append(f"{path.name}: {m.group(0)[:70]!r}")
                break
    assert not offenders, (
        "Empty heading sections / trailing headings found (structural strip "
        "residue):\n" + "\n".join(offenders)
    )


def test_marker_regex_fires_on_known_phrasings():
    """The gate must trip on every observed phrasing class (fire-check)."""
    samples = [
        "[NOTA EDITORIAL: falta el caso]", "[NOTA PARA EDITOR: incompleto]",
        "[NOTA DEL EDITOR: revisar]", "[Nota importante: completar]",
        "[nota: pendiente]", "[SECCIÓN A COMPLETAR: pasos]",
        "[Sección incompleta - requiere]", "[sección pendiente de datos]",
        "[CONTENIDO TRUNCADO EN FUENTE]", "[CONTINUAR CON STEPS TÉCNICOS...]",
        "[Continuará con pasos específicos...]", "[Continuar con detalles del caso...]",
        "[Continúa con el contenido original]", "[Aquí iría un video]",
        "[Esta sección requiere datos]", "[Esta sección también requiere pasos]",
        "[INCOMPLETO — AÑADIR AQUÍ]", "[Incompleto]", "[POR COMPLETAR]",
        "[PENDIENTE DE REVISIÓN]", "[FALTA: contexto]", "[FALTAN datos]",
    ]
    missed = [s for s in samples if not MARKER.search(s)]
    assert not missed, f"MARKER misses known phrasings: {missed}"
    legit = [
        "Hola [Client Name], tu cita es [Fecha]", "[TIMER] Black Friday",
        "usa [DECISION], [WAITING] para notas", "[Enlace a encuesta]",
        "[NOMBRE CLIENTE]. Responde", "[MERCADOPAGO LINK]. ¿En qué ayudamos?",
        "[DEADLINE: DATE]",
    ]
    false_pos = [s for s in legit if MARKER.search(s)]
    assert not false_pos, f"MARKER false-positives on merge fields: {false_pos}"


if __name__ == "__main__":
    test_no_editorial_markers_in_posts()
    test_no_empty_or_trailing_heading_sections()
    test_marker_regex_fires_on_known_phrasings()
    print("ALL TESTS PASSED")
