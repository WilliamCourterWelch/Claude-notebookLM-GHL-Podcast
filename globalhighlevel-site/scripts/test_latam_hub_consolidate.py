#!/usr/bin/env python3
"""Gate: the LATAM pagos cousin 301s into the Spanish hub.

Manager GO 2026-09-22, three locked calls:
A) 301 /blog/gohighlevel-latam-pagos-agencias/ → /es/gohighlevel-latam/
B) Hub title and H1 are exactly the 43-character string below.
C) Flujo A stays the four-processor list. MercadoPago is Flujo B only.

Cousin JSON is gone so Cloudflare's redirect-beats-file rule cannot shadow
a built page. In-site hrefs that named the cousin slug are gone.

Run: python3 -m pytest scripts/test_latam_hub_consolidate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402

SITE = Path(__file__).resolve().parents[1]
POSTS = SITE / "posts"
REDIRECTS = SITE / "_redirects"
HUB_SLUG = "hub-es-gohighlevel-latam"
HUB_PATH = "/es/gohighlevel-latam/"
LOCKED_TITLE = "GoHighLevel en Latinoamérica: guía de pagos"
COUSIN = "gohighlevel-latam-pagos-agencias"
DUAL_STATEMENT = (
    "Cobrarles la suscripción a tus propios clientes de agencia (Flujo A) "
    "sigue descrito con Stripe, NMI, Authorize.net y Square."
)
FLUJO_B = "MercadoPago cobra a los clientes finales (Flujo B)"
RETARGETED = {
    "gohighlevel-precios-planes-2026-guia-completa": (
        "GoHighLevel Precios 2026: Planes, Costos y Guía Completa"
    ),
    "gohighlevel-mercadopago-mexico": (
        "GoHighLevel + Mercado Pago en México: la guía completa para agencias (2026)"
    ),
    "gohighlevel-opiniones-es-confiable-vale-la-pena": (
        "GoHighLevel Opiniones 2026: ¿Es Confiable y Vale la Pena? Reseña Honesta"
    ),
    "que-es-gohighlevel-mejor-alternativa-herramientas-locales-latinoamerica": (
        "Qué es GoHighLevel vs Herramientas Locales en LATAM"
    ),
}
DO_NOT_TOUCH = {
    "gohighlevel-free-trial-30-days-extended": (
        "GoHighLevel 30-Day Free Trial (2026): Get Extended Access"
    ),
    "gohighlevel-sub-accounts-snapshots-agency-guide": (
        "GoHighLevel Sub-Accounts: How Many You Really Get"
    ),
}


def _hub() -> dict:
    return json.loads((POSTS / f"{HUB_SLUG}.json").read_text(encoding="utf-8"))


def _redirect_rules() -> list[tuple[str, str, str]]:
    rows = []
    for line in REDIRECTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 3:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def test_hub_title_is_the_locked_43_char_string():
    assert len(LOCKED_TITLE) == 43
    raw = (POSTS / f"{HUB_SLUG}.json").read_text(encoding="utf-8")
    assert f'"title": "{LOCKED_TITLE}"' in raw
    post = _hub()
    assert post["title"] == LOCKED_TITLE
    assert post.get("url_path") == HUB_PATH
    # 43 > 40, so compose_title must not append the brand suffix (that would be 63).
    assert build.compose_title(LOCKED_TITLE) == LOCKED_TITLE


def test_cousin_post_json_removed():
    assert not (POSTS / f"{COUSIN}.json").exists()


def test_redirects_are_permanent_into_hub():
    by_src = {src: (dest, code) for src, dest, code in _redirect_rules()}
    for src in (f"/blog/{COUSIN}", f"/blog/{COUSIN}/"):
        assert src in by_src, src
        dest, code = by_src[src]
        assert code == "301", (src, code)
        assert dest == HUB_PATH, (src, dest)


def test_no_post_html_names_the_cousin_slug():
    leftovers = []
    for path in sorted(POSTS.glob("*.json")):
        html = json.loads(path.read_text(encoding="utf-8")).get("html_content") or ""
        if COUSIN in html:
            leftovers.append(path.stem)
    assert leftovers == []


def test_retargeted_posts_link_the_hub_and_keep_their_titles():
    for slug, title in RETARGETED.items():
        post = json.loads((POSTS / f"{slug}.json").read_text(encoding="utf-8"))
        assert post["title"] == title, slug
        assert HUB_PATH in post["html_content"], slug


def test_dual_statement_keeps_mercadopago_off_flujo_a():
    html = _hub()["html_content"]
    assert DUAL_STATEMENT in html
    assert FLUJO_B in html
    assert "sin tarjeta" not in html.lower()
    assert "fp_ref=amplifi-technologies12" in html or "globalhighlevel.com/trial" in html
    # Decision C: do not claim MercadoPago as the Flujo A processor.
    lowered = html.lower()
    for banned in (
        "mercadopago para el flujo a",
        "flujo a es mercadopago",
        "flujo a con mercadopago",
        "mercadopago procesa el flujo a",
    ):
        assert banned not in lowered, banned


def test_do_not_touch_neighbors_keep_their_titles():
    for slug, title in DO_NOT_TOUCH.items():
        post = json.loads((POSTS / f"{slug}.json").read_text(encoding="utf-8"))
        assert post["title"] == title, slug


def test_rendered_hub_keeps_title_canonical_cta(tmp_path, monkeypatch):
    post = _hub()
    monkeypatch.setattr(build, "PUBLIC_DIR", tmp_path)
    build._ANCHOR_URL_COUNTS.clear()
    build.build_post_page(post, all_posts=[post])
    html = (tmp_path / build.post_output_rel(post) / "index.html").read_text(
        encoding="utf-8"
    )
    assert f"<title>{LOCKED_TITLE}</title>" in html
    assert f'<h1 class="post-title fade-2">{LOCKED_TITLE}</h1>' in html
    canonical = f"{build.SITE_URL}{HUB_PATH}"
    assert f'<link rel="canonical" href="{canonical}">' in html
    assert "fp_ref=amplifi-technologies12" in html
    assert "highlevel-bootcamp-es" in html
    assert "sin tarjeta" not in html.lower()
    assert COUSIN not in html
    assert DUAL_STATEMENT in html
    assert 'content="noindex' not in html


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
