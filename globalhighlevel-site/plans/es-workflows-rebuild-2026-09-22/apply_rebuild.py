#!/usr/bin/env python3
"""Apply the 2026-09-22 Spanish workflow rebuild onto existing post JSON.

Updates html_content, description, and updatedAt only. Titles, slugs, and
topics stay. The timer post is intentionally absent: it was rebuilt in v0.3.9.0.
"""
from __future__ import annotations

import json
from pathlib import Path

POSTS = Path(__file__).resolve().parents[2] / "posts"
UPDATED = "2026-09-22T23:45:00.000000"

CTA = (
    '<p>La prueba de 30 días pide una tarjeta solo para una verificación de ~$1 '
    '(retención temporal que el banco libera, sin cargo de suscripción).</p>\n'
    '<p style="background:#fef3c7;border-left:4px solid #f59e0b;padding:12px 16px;'
    'border-radius:4px;margin-top:20px;"><strong>👉 Empieza ahora:</strong> '
    'Prueba GoHighLevel <strong>GRATIS por 30 días</strong> — acceso completo, '
    'cancela cuando quieras. <a href="https://globalhighlevel.com/trial" '
    'target="_blank">Acceder a prueba gratis →</a></p>'
)

FIG_WA = (
    '<figure class="post-figure"><img src="/images/es-mx/ghl-whatsapp-settings-es-20260728.png" '
    'alt="La opción de WhatsApp tal como aparece en una subcuenta de GoHighLevel, con sincronización de la app, Conversation AI y plantillas" '
    'loading="lazy"><figcaption>La pantalla de WhatsApp en una subcuenta (captura del 28 de julio de 2026, datos de cuenta cubiertos).</figcaption></figure>'
)
FIG_MP_CARD = (
    '<figure class="post-figure"><img src="/images/es-mx/ghl-mercadopago-card-es.png" '
    'alt="La tarjeta de Mercado Pago en Pagos, Integraciones de GoHighLevel, con botón Conectar" '
    'loading="lazy"><figcaption>Mercado Pago en Pagos, Integraciones (captura del 28 de julio de 2026).</figcaption></figure>'
)
FIG_MP_COUNTRY = (
    '<figure class="post-figure"><img src="/images/es-mx/ghl-mp-config-paises-es-20260728.png" '
    'alt="Selector de país de Mercado Pago en GoHighLevel: Argentina, Brasil, Chile, Colombia, México, Perú y Uruguay" '
    'loading="lazy"><figcaption>El selector de país en la configuración de Mercado Pago (captura del 28 de julio de 2026).</figcaption></figure>'
)
FIG_WA_ACTIONS = (
    '<figure class="post-figure"><img src="/images/es-mx/ghl-workflow-action-whatsapp-es-20260728.png" '
    'alt="Acciones de WhatsApp en el creador de flujos: WhatsApp, media, interactive messages, send flows y customer service window check" '
    'loading="lazy"><figcaption>Acciones de WhatsApp en el creador de flujos (captura del 28 de julio de 2026).</figcaption></figure>'
)
FIG_AI_HOME = (
    '<figure class="post-figure"><img src="/images/es-mx/ghl-workflows-home-ai-es-20260728.png" '
    'alt="Página de flujos de trabajo con el botón de asistente de IA y la opción de plantillas" '
    'loading="lazy"><figcaption>Listado de flujos con el asistente de IA y las plantillas (captura del 28 de julio de 2026).</figcaption></figure>'
)


def src(url: str, label: str, modified: str) -> str:
    return (
        f'<li><a href="{url}" rel="nofollow noopener" target="_blank">{label}</a> '
        f'— artículo modificado {modified}. Consultado el 22 de septiembre de 2026.</li>'
    )


BODIES: dict[str, tuple[str, str]] = {}

BODIES["configurar-workflows-gohighlevel-whatsapp-mercadopago"] = (
    "Conecta WhatsApp y Mercado Pago en GoHighLevel con credenciales de producción, el webhook de pagos y un flujo. La prueba pide verificación de tarjeta de ~$1.",
    f"""<h2>Respuesta rápida</h2>
<p>Según las guías de HighLevel consultadas el 22 de septiembre de 2026, el camino documentado es este: conectas WhatsApp en la subcuenta, conectas Mercado Pago en Pagos &gt; Integraciones con credenciales de producción, configuras el webhook de pagos y recién ahí armas el flujo. Mercado Pago, en esa guía, está disponible en Colombia, Argentina, Chile, México, Uruguay, Perú y Brasil. Ecuador y El Salvador figuran como países por venir, no como países ya activos.</p>
<p>El detalle de filtros del disparador Payment Received está en <a href="/blog/workflows-gohighlevel-mercadopago-whatsapp-automaticamente/">el flujo de pago recibido y WhatsApp</a>. Esta página es el alta de los dos canales.</p>
<h2>Lo que tiene que estar listo</h2>
<ul>
<li>Una subcuenta de GoHighLevel donde vas a cobrar y a escribir.</li>
<li>Una cuenta de Mercado Pago con acceso al panel de desarrolladores, y la web del negocio por si Mercado Pago la pide al activar credenciales de producción.</li>
<li>Soporte de pagos sin CVV habilitado en Mercado Pago. La guía dice que, sin eso, suscripciones, cobros off-session y los flujos de facturación tipo SaaS pueden fallar.</li>
<li>Clave pública, access token, país de la cuenta y un secreto de webhook. Las credenciales de prueba no procesan pagos reales.</li>
</ul>
<h2>Paso 1: WhatsApp en la subcuenta</h2>
<p>La guía de alta de WhatsApp (modificada el 16 de septiembre de 2026) abre en <strong>Settings &gt; WhatsApp</strong> y ofrece tres caminos.</p>
<h3>App de WhatsApp Business que ya usas</h3>
<p>Eliges conectar la app existente. La guía llama a esto coexistencia: sigues usando la app y la plataforma a la vez. No está disponible para números de Nigeria ni de Sudáfrica. Importa contactos y hasta seis meses de historial, y solo admite un número. Las plantillas no se envían desde la app de WhatsApp Business: solo desde el CRM. El perfil de WhatsApp se sigue editando en la app, no en el CRM.</p>
<h3>Número nuevo</h3>
<p>Eliges crear una cuenta nueva, continúas con Facebook, cargas un número nuevo o uno elegible del desplegable, confirmas el código por SMS o llamada y seleccionas o creas el portafolio de Meta y la cuenta de WhatsApp Business.</p>
<h3>Migrar desde otro proveedor</h3>
<p>Eliges migrar desde un BSP, seleccionas la cuenta de WhatsApp Business correcta, cargas el número activo y confirmas el código.</p>
{FIG_WA}
<h2>Paso 2: Mercado Pago con credenciales de producción</h2>
<ol>
<li>En HighLevel, abre <strong>Payments</strong> y la pestaña <strong>Integrations</strong>.</li>
<li>Busca Mercado Pago y pulsa <strong>Connect</strong>.</li>
<li>En Mercado Pago, entra a Your integrations, abre o crea una aplicación y copia la Public Key y el Access Token de <strong>Production credentials</strong>. Si aún no están activas, completa industria y sitio web.</li>
<li>Pega ambas claves en HighLevel, elige el país de la cuenta, genera o escribe el secreto de webhook y guarda.</li>
</ol>
<p>La captura del 28 de julio de 2026 muestra el secreto del webhook marcado como opcional en pantalla. La guía modificada el 10 de septiembre de 2026 pide igual configurar las notificaciones para que los eventos de pago vuelvan a HighLevel. Sigue la guía, no solo la etiqueta opcional de esa captura.</p>
{FIG_MP_CARD}
{FIG_MP_COUNTRY}
<h2>Paso 3: Webhook en Mercado Pago</h2>
<ol>
<li>En la aplicación de Mercado Pago, abre Webhooks y configura las notificaciones.</li>
<li>Pega en la URL de modo producción: <code>https://backend.leadconnectorhq.com/payments/mercado-pago/webhook</code>. La guía escribe el host con esa ruta; usa la cadena que muestra el artículo el día que conectes, porque el mismo texto también aparece con otra mayúscula en LeadConnector.</li>
<li>El secreto tiene que ser el mismo en HighLevel y en Mercado Pago.</li>
<li>Selecciona el evento Payment y guarda.</li>
</ol>
<h2>Paso 4: Asignar Mercado Pago por canal</h2>
<p>Después de conectar, abre Manage Provider Configurations. Ahí alternas Live y Test y asignas Mercado Pago a los canales donde quieras usarlo. La guía de países y montos, en la pregunta frecuente, cita límites de tarjetas en Argentina (mínimo de referencia 100 y máximo 15.000.000, en la moneda de esa ayuda de Mercado Pago Argentina), no un mínimo universal en dólares para toda Latinoamérica.</p>
<p>Dos límites que la misma guía escribe sin ambigüedad:</p>
<ul>
<li>Mercado Pago no convierte la moneda de forma dinámica en este setup. Si la cuenta es de Argentina, el precio del producto va en pesos argentinos. Lo mismo vale para la moneda local de tu cuenta.</li>
<li>No puedes tener dos checkouts de Mercado Pago activos en la misma página. Dos order forms con captura de tarjeta en un mismo funnel no cargan.</li>
</ul>
<h2>Qué es Flujo B y qué no es</h2>
<p>Esta conexión es para cobrarle al cliente final desde formularios, funnels, facturas, calendarios u otros canales que asignes. La tarjeta de Mercado Pago en la captura de julio lista varios canales, incluido SaaS mode. La guía del 10 de septiembre dice que, sin pagos sin CVV, los flujos de facturación tipo SaaS pueden no funcionar.</p>
<p>En este sitio, el cobro de la agencia a sus propias subcuentas (Flujo A) sigue siendo Stripe, NMI, Authorize.net o Square. Mercado Pago no reemplaza esa lista. Esa frase es la misma que mantiene la guía de pagos en Latinoamérica.</p>
<h2>Paso 5: El mensaje de WhatsApp sale del flujo</h2>
<p>En Automation &gt; Workflows creas el flujo. La acción documentada se llama WhatsApp. Dentro de la ventana de 24 horas puedes enviar texto libre. Fuera de esa ventana hace falta una plantilla aprobada. La guía también describe una Free Entry Point: si el cliente responde, puedes enviar texto libre o plantilla hasta por 72 horas sin costo adicional de esa conversación, según el texto de la acción.</p>
<p>Un pago que acaba de entrar es un mensaje que inicia el negocio, no una respuesta a un chat abierto. Por eso el aviso de pago usa plantilla, no texto libre, salvo que el contacto esté dentro de la ventana. Los filtros del disparador están en la otra guía de este mismo tema.</p>
<p>La captura del 28 de julio muestra, en el buscador de acciones, WhatsApp, WhatsApp media, WhatsApp interactive messages, WhatsApp send flows y WhatsApp customer service window check. Esos cinco nombres son lo que se veía en esa pantalla. La guía de la acción, modificada el 8 de abril de 2025, documenta el envío de plantilla o de texto dentro de la ventana, más variables del contacto y la opción de no molestar (DND) para WhatsApp.</p>
{FIG_WA_ACTIONS}
{FIG_AI_HOME}
<p>En esa misma captura de julio, el listado ofrece crear con IA y dice en pantalla que puedes crear flujos chateando con la IA. La guía de Workflow AI Builder del 3 de agosto de 2026 no publica una tarifa de ese asistente. No uses la palabra de la captura como precio vigente.</p>
<h2>WhatsApp se cobra en Meta, aparte del plan</h2>
<p>La guía de precios de este sitio, revisada contra la documentación de HighLevel en agosto de 2026, lista la integración de WhatsApp en 10 USD al mes. Aparte, el error 131042 de la API de WhatsApp bloquea los envíos cuando Meta no tiene un método de pago válido en la cuenta de WhatsApp Business. El artículo, modificado el 30 de junio de 2026, dice que la suscripción del CRM no cubre esas tarifas de conversación. También dice que WhatsApp incluye 1.000 conversaciones de servicio gratis al mes y que, pasado ese cupo, sin método de pago en Meta los mensajes nuevos se bloquean.</p>
<p>El hilo público de ideas de Mercado Pago es la demanda verificable: más de 300 votos. No hay en esta página un caso de una agencia con nombre, ciudad y cifra de ventas.</p>
<h2>Preguntas frecuentes</h2>
<h3>¿Mercado Pago cobra en dólares si mi cuenta es local?</h3>
<p>No de forma dinámica, según la guía del 10 de septiembre de 2026. El precio del producto tiene que estar en la moneda de tu cuenta de Mercado Pago.</p>
<h3>¿Puedo poner dos botones de pago de Mercado Pago en la misma página?</h3>
<p>No. La guía dice que Mercado Pago no permite dos elementos de checkout en una sola página.</p>
<h3>¿El plan de GoHighLevel paga las conversaciones de WhatsApp?</h3>
<p>No. El error 131042 es un problema de pago en Meta, aunque el CRM esté al día.</p>
<h2>Fuentes</h2>
<ul>
{src("https://help.gohighlevel.com/support/solutions/articles/155000001980-how-to-set-up-whatsapp-for-a-sub-account", "How to Set Up WhatsApp for a Sub-Account", "el 16 de septiembre de 2026")}
{src("https://help.gohighlevel.com/support/solutions/articles/155000007562-how-to-integrate-with-mercado-pago-for-accepting-payments-", "How to integrate with Mercado Pago", "el 10 de septiembre de 2026")}
{src("https://help.gohighlevel.com/support/solutions/articles/155000003531-workflow-action-whatsapp", "Workflow Action - WhatsApp", "el 8 de abril de 2025")}
{src("https://help.gohighlevel.com/support/solutions/articles/155000007938-error-131042-business-eligibility-payment-issue", "Error 131042 — Business Eligibility Payment Issue", "el 30 de junio de 2026")}
<li><a href="https://ideas.gohighlevel.com/payment-links/p/integrate-mercado-pago" rel="nofollow noopener" target="_blank">Hilo de ideas: integrar Mercado Pago</a> — demanda pública, más de 300 votos. No es un caso de cliente.</li>
</ul>
{CTA}
""",
)

BODIES["workflows-gohighlevel-mercadopago-whatsapp-automaticamente"] = (
    "Configura Payment Received en GoHighLevel, filtra el estado Success y envía WhatsApp con plantilla si el pago no abrió la ventana de 24 horas. Revisa el origen.",
    f"""<h2>Respuesta rápida</h2>
<p>Cuando Mercado Pago ya está conectado, la guía de HighLevel del disparador Payment Received (modificada el 15 de abril de 2026) es el camino para reaccionar a un pago. El artículo lo describe como agnóstico de pasarela: funciona con Stripe, PayPal y cualquier otro gateway conectado. Mercado Pago es un proveedor que se conecta en Payments. Esta página no vuelve a explicar las credenciales: eso está en <a href="/blog/configurar-workflows-gohighlevel-whatsapp-mercadopago/">la guía de alta de WhatsApp y Mercado Pago</a>.</p>
<h2>Antes de armar el flujo</h2>
<ul>
<li>Mercado Pago en modo producción, con el webhook de pagos guardado y el proveedor asignado al canal donde cobras.</li>
<li>WhatsApp activo en la subcuenta y, para avisos que salen de un pago, una plantilla aprobada. Un pago no abre por sí solo la ventana de 24 horas.</li>
<li>El flujo en borrador hasta que lo pruebes. La guía dice probar con un entorno sandbox o con un producto de prueba, y publicar antes de esperar que el disparador corra.</li>
</ul>
<h2>Paso 1: Crear el flujo y elegir Payment Received</h2>
<ol>
<li>Ve a <strong>Automation &gt; Workflows</strong>.</li>
<li>Pulsa <strong>+ Create Workflow</strong> y elige <strong>Start from Scratch</strong>.</li>
<li>Pulsa <strong>+ Add New Trigger</strong>, baja a la sección Payments y elige <strong>Payment Received</strong>.</li>
<li>Ponle un nombre que diga qué pago es, por ejemplo el producto o la factura, no solo "pago".</li>
</ol>
<h2>Paso 2: Filtrar para no disparar cualquier cobro</h2>
<p>Pulsa <strong>+ Add filters</strong>. La guía lista estas fuentes:</p>
<ul>
<li>Calendar: pago de una cita.</li>
<li>External: pago de terceros como Stripe, PayPal o una API externa.</li>
<li>Form: formulario con elemento de pago.</li>
<li>Funnel: order form de un funnel.</li>
<li>Invoice: factura enviada desde HighLevel.</li>
<li>Manual Payment: pago cargado a mano en el CRM.</li>
<li>Memberships: acceso a un producto o curso.</li>
<li>Website: tienda, producto o suscripción.</li>
</ul>
<p>Para un aviso solo cuando el dinero entró, agrega el filtro <strong>Payment Status = Success</strong>. Puedes acotar también por Global Product y, si el origen es un calendario, por el calendario concreto. Guarda el disparador.</p>
<h2>Paso 3: Elegir la acción de WhatsApp correcta</h2>
<p>Agrega la acción WhatsApp. La guía de esa acción (8 de abril de 2025) distingue dos envíos:</p>
<ul>
<li>Texto libre, solo dentro de la ventana de 24 horas de una conversación que el cliente ya abrió.</li>
<li>Plantilla aprobada, para iniciar conversación fuera de esa ventana. Un recibo de pago cae aquí, salvo que sepas que el contacto escribió en las últimas 24 horas.</li>
</ul>
<p>Puedes usar variables. La guía del disparador nombra, entre otras, {{{{Payment Amount}}}} y {{{{Transaction ID}}}}. El ejemplo de plantilla que da la acción de WhatsApp es de recordatorio de cita, no de pago: "Hi {{{{contact.first_name}}}}, this is a reminder for your appointment scheduled on {{{{appointment.date}}}}." Sirve para ver el formato. El texto de tu plantilla de pago lo aprueba Meta; esta página no inventa un texto aprobado.</p>
<p>Si el cliente responde a ese mensaje, la misma guía llama Free Entry Point a la conversación que permite texto libre o plantilla hasta por 72 horas sin costo adicional. También puedes activar DND de WhatsApp para quien pidió no recibir mensajes.</p>
<h2>Pagos fallidos y suscripciones</h2>
<p>La misma guía dice que Payment Status = Failed sirve para un seguimiento de cobro fallido. No es una segunda pasarela: es un filtro del mismo disparador.</p>
<p>Para cargos recurrentes, el artículo compara tres disparadores y dice que no hay un disparador exclusivo de Stripe:</p>
<ul>
<li><strong>Payment Received</strong> corre en cada cargo recurrente si filtras por transacción de suscripción con el cliente ausente, e incluye fallos vía Payment Status.</li>
<li><strong>Order Submitted</strong> corre en cargos recurrentes exitosos y exige funnels V2. En V1, usa Payment Received.</li>
<li><strong>Subscription</strong> reacciona al alta, la pausa, la reanudación o la cancelación, no a cada cobro.</li>
</ul>
<p>Esos tres, dice el artículo, normalizan eventos de cualquier gateway conectado. No hay en la guía una frase que nombre a Mercado Pago dentro de esa tabla. La lectura que sí sostiene el texto es: conectas el proveedor y el disparador de pagos es el mismo mecanismo.</p>
<h2>Lo que no debes afirmar</h2>
<ul>
<li>Conekta, PayU y Transbank no son el conector que describe la guía de Mercado Pago. No los presentes como integración nativa en este flujo.</li>
<li>Flujo A, la agencia cobrando a sus subcuentas, sigue en Stripe, NMI, Authorize.net o Square. Mercado Pago aquí es el cobro al cliente final.</li>
<li>No hay un caso real con nombre de agencia y porcentaje de cierre. El ejemplo de la documentación es el recordatorio de cita citado arriba.</li>
</ul>
<h2>Preguntas frecuentes</h2>
<h3>¿El disparador distingue un pago de funnel de un pago de factura?</h3>
<p>Sí. El filtro Source separa Calendar, External, Form, Funnel, Invoice, Manual Payment, Memberships y Website.</p>
<h3>¿Puedo usar el monto del pago dentro del mensaje?</h3>
<p>La guía dice que sí puedes usar campos como {{{{Payment Amount}}}} y {{{{Transaction ID}}}} en emails o avisos internos. En WhatsApp, fuera de la ventana de 24 horas, ese texto tiene que vivir en una plantilla aprobada.</p>
<h3>¿Hace falta Zapier para que Mercado Pago dispare el flujo?</h3>
<p>No para el pago que ya entra por el proveedor conectado. El webhook que configura la guía de Mercado Pago apunta a la URL de pagos de LeadConnector. El disparador Inbound Webhook es otro mecanismo, para aplicaciones externas que tú conectas.</p>
<h2>Fuentes</h2>
<ul>
{src("https://help.gohighlevel.com/support/solutions/articles/155000003534-workflow-trigger-payment-received", "Workflow Trigger - Payment Received", "el 15 de abril de 2026")}
{src("https://help.gohighlevel.com/support/solutions/articles/155000003531-workflow-action-whatsapp", "Workflow Action - WhatsApp", "el 8 de abril de 2025")}
{src("https://help.gohighlevel.com/support/solutions/articles/155000007562-how-to-integrate-with-mercado-pago-for-accepting-payments-", "How to integrate with Mercado Pago", "el 10 de septiembre de 2026")}
</ul>
{CTA}
""",
)


def main() -> None:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from more_bodies import MORE

    BODIES.update({slug: (desc, html.replace("__CTA__", CTA)) for slug, (desc, html) in MORE.items()})
    assert len(BODIES) == 9, len(BODIES)
    for slug, (desc, html) in BODIES.items():
        path = POSTS / f"{slug}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["description"] = desc
        data["html_content"] = html
        data["updatedAt"] = UPDATED
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        words = len(__import__("re").sub(r"<[^>]+>", " ", html).split())
        print(f"{slug}\tdesc={len(desc)}\twords={words}")


if __name__ == "__main__":
    main()
