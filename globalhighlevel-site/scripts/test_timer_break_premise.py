#!/usr/bin/env python3
"""Regression gate: the retired "copying breaks the timer" claim stays retired.

The 2026-07-31 research rebuild of copiar-templates-temporizadores-gohighlevel
removed a premise no HighLevel documentation supports: that cloning or copying
an email template breaks, desyncs or resets its countdown timer. The pre-rebuild
body asserted it five times ("¿Por Qué Se Rompen los Temporizadores Cuando
Copias Templates?", "El temporizador se reinicia ... o directamente no
funciona", "temporizadores que no funcionan o que muestran tiempos
incorrectos"). The documented behavior is different and benign: email timers are
typically GIFs that recount up to 60s per open, recurrent timers restart at zero
by design, and Apple Mail caches the GIF. A future import, translation pass, or
"restore the old intro" edit must not reintroduce the retired class.

WHY THIS MATCHES PHRASES AND NOT MEANING (design history — read before "improving" it):

The first cut of this gate tried to infer the CLAIM: timer noun + copy verb +
breakage verb co-occurring in a 500-char window, minus a hedge list. Three
independent review passes each found fresh defects in that approach:
  - the hedge list was a window-global kill switch, so one incidental ordinary
    word ("puedes arreglarlo") disarmed it from 250 chars away;
  - tightening the hedge made benign prose fire instead — including this post's
    own Paso 2, one word from blocking every deploy of a ~900-post site;
  - the copy/break distance was bounded but the distance to the TIMER never
    was, so a sentence about an unrelated subsystem near any timer mention
    tripped it.
Each fix moved the failure to the other side. Fuzzy-matching a semantic claim in
free prose is not a thing a regex does safely when the cost of a false positive
is "no one can deploy".

So this gate matches the RETIRED PHRASINGS themselves. Every pattern below names
the timer as the thing that fails, which is the assertion — no window, no hedge
list, no exemption logic, nothing to bypass by adding a word. It has low recall
by construction: a genuinely novel phrasing passes, and that is the reviewer's
job, not this file's. What it buys is a hard floor — the specific text that was
live for months cannot come back silently, and it cannot block a deploy over
ordinary prose.

SCOPE: Spanish posts only (language starts with "es"). The vocabulary is
Spanish. KNOWN GAP, tracked in #53/#54: the English and en-IN siblings
(copy-templates-countdown-timers-gohighlevel,
gohighlevel-countdown-timer-templates-india) assert this same retired class
today and are NOT covered here — they need their own grounded rebuild first.
Coverage honesty: only 1 of ~249 es posts contains timer vocabulary at all, so
in practice this pins that one post plus anything new that adopts the phrasing.

Run: python3 -m pytest scripts/test_timer_break_premise.py
"""
from __future__ import annotations

import html as htmlmod
import json
import re
import unicodedata
from pathlib import Path

POSTS = Path(__file__).resolve().parents[1] / "posts"

TAG = re.compile(r"<[^>]+>")

# Zero-width / bidi / soft-hyphen characters can split a stem ("re<ZWSP>inicia")
# and hide it from every pattern here. Written as escapes on purpose so the set
# is reviewable in a diff.
INVISIBLE = re.compile(r"[­​-‏⁠﻿]")

# Direct assertions that the TIMER is what fails. Each names the timer as the
# subject of the breakage, so no surrounding context is needed to read it as the
# retired claim.
RETIRED = [
    re.compile(r"se\s+rompen\s+los\s+temporizador", re.I),
    re.compile(r"temporizador(?:es)?\s+se\s+romp\w+", re.I),
    re.compile(r"romp\w+\s+(?:el|los)\s+temporizador", re.I),
    re.compile(r"temporizador(?:es)?\s+que\s+no\s+funciona\w*", re.I),
    re.compile(r"temporizador(?:es)?\s+se\s+desincroniz\w+", re.I),
    re.compile(r"(?:cuenta\s+regresiva|temporizador(?:es)?)\s+qued\w+\s+"
               r"(?:rot[oa]s?|inutilizable)", re.I),
    re.compile(r"temporizador(?:es)?\s+se\s+estropea\w*", re.I),
    # "…copiar plantillas con temporizadores en GoHighLevel SIN QUE SE ROMPAN"
    # (the pre-rebuild meta description). The negative framing presupposes the
    # retired claim — it only makes sense if copying otherwise breaks them —
    # and words sit between the timer noun and the verb, so the adjacency
    # patterns above miss it. Same sentence only.
    # "El temporizador se reinicia, los plazos se desincronizán, o
    # directamente no funciona." A bare "el temporizador se reinicia" is the
    # DOCUMENTED recurrent behavior and must stay legal, so this only fires
    # when the restart is chained to a second failure in the same sentence —
    # which is the retired compound assertion, not the documented one.
    re.compile(r"temporizador(?:es)?\s+se\s+reinicia[^.!?]{0,80}"
               r"(?:desincroniz\w+|no\s+funciona)", re.I),
]

# Active-voice claims ("Copiar el template resetea la cuenta regresiva"). These
# need a copy/clone verb in the same sentence, because the bare phrase is also
# ordinary instruction ("si falla, reinicia el temporizador").
RETIRED_IF_COPY = [
    re.compile(r"(?:resetea|reinicia)\s+(?:el\s+temporizador|la\s+cuenta\s+regresiva)", re.I),
    # "…copiar plantillas con temporizadores en GoHighLevel SIN QUE SE ROMPAN"
    # (the pre-rebuild meta description). Negative framing presupposes the
    # retired claim — it only means something if copying otherwise breaks them.
    # Copy context is required: "prueba los temporizadores en móvil para que no
    # se rompan" is ordinary QA advice and must not block a deploy.
    re.compile(r"temporizador(?:es)?\b[^.!?]{0,40}?"
               r"(?:sin\s+que\s+se\s+romp\w+|para\s+que\s+no\s+se\s+romp\w+)", re.I),
    re.compile(r"(?:sin\s+que\s+se\s+romp\w+|para\s+que\s+no\s+se\s+romp\w+)"
               r"[^.!?]{0,20}?\btemporizador(?:es)?\b", re.I),
    # The pre-rebuild MECHANISM for the retired premise: copying leaves the
    # timer's placeholders pointing at the original account. Retired with the
    # claim it explained, and pinned separately so it can't return piecemeal
    # without the failure sentence that used to follow it.
    re.compile(r"placeholders?\b[^.!?]{0,60}?apuntan\s+a\s+la\s+cuenta\s+original", re.I),
]

COPY = re.compile(r"(?:copia\w*|clona\w*|duplica\w*|replica\w*)", re.I)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Chars of context shown per offender in the failure message.
EXCERPT_CHARS = 160


def _plain_variants(s: str) -> tuple[str, str]:
    """Plain-text renderings of a post string, with tags removed two ways.

    Order matters: unescape BEFORE stripping tags, twice, so double-encoded
    markup can't survive as literal text. NFC folds combining diacritics.

    Two variants are returned because tag removal is a trade-off: replacing a
    tag with a SPACE keeps words apart across block tags but lets an inline tag
    split a stem (`se ro<span>mpe`); replacing it with NOTHING closes the split
    but glues words across block boundaries. A hit in either counts, so neither
    trick works.
    """
    t = unicodedata.normalize("NFC", s)
    t = INVISIBLE.sub("", t)
    spaced = t
    glued = t
    for _ in range(2):
        spaced = TAG.sub(" ", htmlmod.unescape(spaced))
        glued = TAG.sub("", htmlmod.unescape(glued))
    return spaced, glued


def _premise_hits(text: str) -> list[str]:
    """Excerpts asserting the retired break-on-copy premise."""
    hits = []
    for variant in _plain_variants(text):
        for pat in RETIRED:
            m = pat.search(variant)
            if m:
                hits.append(_excerpt(variant, m))
        for sentence in SENTENCE_SPLIT.split(variant):
            if not COPY.search(sentence):
                continue
            for pat in RETIRED_IF_COPY:
                m = pat.search(sentence)
                if m:
                    hits.append(_excerpt(sentence, m))
    # de-dupe across the two variants
    seen, out = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def _excerpt(text: str, m: re.Match) -> str:
    half = EXCERPT_CHARS // 2
    chunk = text[max(0, m.start() - half):m.end() + half]
    return f"...{' '.join(chunk.split())}... [matched {m.group(0)!r}]"


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


def _load(path: Path) -> dict:
    """Read a post, naming the file on any failure. A bare json.loads here
    would block every deploy with a stack trace that doesn't say which post."""
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AssertionError(f"{path.name}: unreadable post JSON ({exc})") from exc
    assert isinstance(data, dict), f"{path.name}: post JSON is not an object"
    return data


def test_no_retired_timer_premise_in_spanish_posts():
    offenders = []
    scanned = 0
    for path in _post_files():
        data = _load(path)
        # startswith so a future es-MX / es-ES locale split can't silently
        # switch the gate off.
        if not str(data.get("language", "")).lower().startswith("es"):
            continue
        scanned += 1
        for field, value in data.items():
            for s in _walk_strings(value):
                hits = _premise_hits(s)
                if hits:
                    offenders.append(f"{path.name}:{field}: {hits[0]}")
    assert scanned > 50, f"suspiciously few es posts scanned ({scanned})"
    assert not offenders, (
        "A retired 'copying/cloning breaks the timer' phrasing is back in "
        "published content. HighLevel documents no such behavior — state the "
        "documented mechanism instead (email timers are typically GIFs that "
        "recount up to 60s per open, recurrent timers restart at zero by "
        "design, Apple Mail caches the GIF):\n" + "\n".join(offenders)
    )


def test_gate_fires_on_retired_phrasings_and_not_on_grounded_prose():
    """Both edges. `retired` must trip (or the gate is decorative); `grounded`
    must not (or the gate blocks every deploy over ordinary prose)."""
    retired = [
        # --- verbatim pre-rebuild ---
        "¿Por Qué Se Rompen los Temporizadores Cuando Copias Templates?",
        "El temporizador se reinicia, los plazos se desincronizán, o "
        "directamente no funciona.",
        "el resultado: temporizadores que no funcionan o que muestran tiempos "
        "incorrectos.",
        # --- phrasings a rewrite could reach for ---
        "al clonar el template el temporizador se rompe",
        "si duplicas la plantilla, la cuenta regresiva queda rota",
        "<p>Copiar el template <strong>rompe el temporizador</strong>.</p>",
        "Duplicar un template en otra subcuenta hace que el temporizador se "
        "rompa.",
        "La copia del template en la subcuenta destino rompe el temporizador.",
        "El temporizador se rompe al ser copiado el template.",
        "Copiar el template resetea la cuenta regresiva.",
        "Duplicar el template reinicia el temporizador.",
        "Tras copiar la plantilla el temporizador queda inutilizable.",
        # the pre-rebuild META DESCRIPTION — negative framing, and the verb is
        # not adjacent to the timer noun
        "Aprende a copiar plantillas de email con temporizadores en "
        "GoHighLevel sin que se rompan.",
        "Copia tus plantillas para que no se rompan los temporizadores.",
        # the pre-rebuild MECHANISM sentence, restorable on its own
        "Cuando copias un template de una cuenta a una subcuenta sin los "
        "pasos correctos, esos placeholders apuntan a la cuenta original, no "
        "a la nueva.",
        # --- evasion attempts ---
        "Al copiar el template, el temporizador se &lt;span&gt;rompe&lt;/span&gt;.",
        "Al copiar el template, el temporizador se ro<span>mpe</span>.",
        "Al co​piar el template, el temporizador se romp​e.",
    ]
    missed = [s for s in retired if not _premise_hits(s)]
    assert not missed, f"gate misses retired phrasings: {missed}"

    grounded = [
        # the rebuilt post's own framing
        "Ese comportamiento documentado es lo primero a descartar cuando un "
        "temporizador de email parece reiniciarse, y conviene conocerlo antes "
        "de copiar o clonar templates.",
        "Es decir: si un temporizador de email vuelve a arrancar al abrir el "
        "mensaje, eso puede coincidir con el comportamiento documentado, y no "
        "basta para concluir que el template se rompió.",
        "Lo que la documentación no describe es ningún comportamiento especial "
        "de los temporizadores al clonar un template, ni a favor ni en contra.",
        "Revisa el tipo: si es recurrente, reiniciarse al llegar a cero es su "
        "comportamiento documentado.",
        "Cómo Copiar Templates con Temporizadores en GoHighLevel (y Por Qué "
        "Parece que Se Reinician)",
        # ordinary verification advice — a fuzzy matcher fired on these
        "Al clonar la plantilla, revisa si el temporizador se reinicia.",
        "Cuando copias el template, comprueba que el temporizador no se "
        "reinicia antes de tiempo.",
        "Recurrente — se reinicia después de llegar a cero; pensado para "
        "promociones continuas.",
        # failures belonging to some OTHER subsystem near a timer mention
        "Copia el enlace de redirección del temporizador y úsalo en los "
        "botones del email. Si el botón no funciona, vuelve a pegar el enlace.",
        "Inserta el temporizador en el email. Al copiar una snapshot de "
        "agencia, la integración de pagos deja de funcionar.",
        "Configura el temporizador. Si duplicas un workflow, el webhook de "
        "Zapier se rompe.",
        # English duty "rota" — why the corpus scan is es-only
        "Duplicate the countdown timer block for each rota you manage.",
        # ordinary QA advice: negative framing with NO copy context
        "Prueba los temporizadores en móvil para que no se rompan.",
        "Revisa la zona horaria de los temporizadores sin que se rompan las "
        "campañas programadas.",
    ]
    false_pos = [s for s in grounded if _premise_hits(s)]
    assert not false_pos, (
        f"gate false-positives on grounded prose (would block deploys): "
        f"{false_pos}"
    )


def test_rebuilt_timer_post_is_clean():
    """Pin the post the rebuild fixed — a targeted revert must fail here."""
    path = POSTS / "copiar-templates-temporizadores-gohighlevel.json"
    assert path.exists(), f"rebuilt timer post missing: {path}"
    data = _load(path)
    hits = [h for v in data.values() for s in _walk_strings(v) for h in _premise_hits(s)]
    assert not hits, f"timer post reasserts the retired premise: {hits}"


if __name__ == "__main__":
    test_no_retired_timer_premise_in_spanish_posts()
    test_gate_fires_on_retired_phrasings_and_not_on_grounded_prose()
    test_rebuilt_timer_post_is_clean()
    print("ALL TESTS PASSED")
