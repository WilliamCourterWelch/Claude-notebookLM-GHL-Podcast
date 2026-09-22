#!/usr/bin/env python3
"""Pins the 2026-09-22 rebuild of nine existing Spanish workflow posts.

The tenth slug in the thin-list, copiar-templates-temporizadores-gohighlevel,
was already rebuilt in v0.3.9.0 and is guarded by test_timer_break_premise.
This gate does not reopen it.
"""
from __future__ import annotations

import json
from pathlib import Path

POSTS = Path(__file__).resolve().parents[1] / "posts"

REBUILT = {
    "configurar-workflows-gohighlevel-whatsapp-mercadopago":
        "Cómo Configurar Workflows de GoHighLevel para Negocios Locales: WhatsApp + MercadoPago",
    "workflows-gohighlevel-mercadopago-whatsapp-automaticamente":
        "Workflows en GoHighLevel: Integra MercadoPago y WhatsApp Automáticamente",
    "gohighlevel-workflows-practicos-casos-de-uso-reales-agencias-digitales":
        "GoHighLevel Workflows Prácticos para Agencias Digitales",
    "maestro-ai-flow-builder-gohighlevel-setup-completo":
        "Domina el AI Flow Builder de GoHighLevel: Guía Completa de Setup para Agencias",
    "configurar-facebook-instagram-messaging-gohighlevel":
        "Cómo Configurar Mensajes de Facebook e Instagram en GoHighLevel: Guía Completa para Agencias",
    "vista-kanban-gohighlevel-gestionar-deals":
        "Vista Kanban en GoHighLevel: Cómo Gestionar Deals Mejor (Guía 2026)",
    "workflows-gohighlevel-plantillas-agencias-5-minutos":
        "Workflows de GoHighLevel para Agencias: Plantillas Listas que Puedes Implementar en 5 Minutos",
    "gohighlevel-inmobiliarias-automatiza-consultas-ventas":
        "GoHighLevel para Inmobiliarias: Automatiza Consultas y Cierra Más Ventas con GHL",
    "ai-help-gohighlevel-workflows-construccion-rapida":
        "AI Help en GoHighLevel: Construye Workflows 3x Más Rápido (Guía para Agencias Latinas)",
}

DUAL = (
    "configurar-workflows-gohighlevel-whatsapp-mercadopago",
    "workflows-gohighlevel-mercadopago-whatsapp-automaticamente",
)


def _load(slug: str) -> dict:
    return json.loads((POSTS / f"{slug}.json").read_text(encoding="utf-8"))


def test_rebuilt_posts_keep_titles_and_cite_help():
    for slug, title in REBUILT.items():
        data = _load(slug)
        assert data["title"] == title
        assert data["slug"] == slug
        assert data["language"] == "es"
        body = data["html_content"]
        desc = data["description"]
        assert "help.gohighlevel.com" in body, slug
        assert "https://globalhighlevel.com/trial" in body, slug
        assert "~$1" in body, slug
        assert "sin tarjeta" not in body.lower(), slug
        assert "sin tarjeta" not in desc.lower(), slug
        assert 150 <= len(desc) <= 160, (slug, len(desc), desc)
        assert "25-35%" not in body
        assert "90%+" not in body


def test_mercadopago_posts_keep_flujo_a_on_the_four_processors():
    for slug in DUAL:
        body = _load(slug)["html_content"]
        assert "Stripe, NMI, Authorize.net o Square" in body, slug
        assert "no reemplaza" in body.lower() or "no son el conector" in body.lower() or "sigue siendo" in body


def test_ai_help_does_not_treat_3x_as_a_documented_rate():
    body = _load("ai-help-gohighlevel-workflows-construccion-rapida")["html_content"]
    assert "no publica ese multiplicador" in body
    assert "30 segundos" in body
