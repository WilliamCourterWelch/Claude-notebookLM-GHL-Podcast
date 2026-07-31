# DRAFT v2 — copiar-templates-temporizadores-gohighlevel (rebuild, 2026-07-30)

v1 + BOTH third-voice passes applied: codex (6 BLOCKING + WARN/style) and Claude
adversarial (4 BLOCKING + 7 WARN + style). Fix map at the bottom. v1 kept for audit.

Slug: copiar-templates-temporizadores-gohighlevel (existing — keep)
Topic: Agency, White-Label & SaaS

---

## Título propuesto

Cómo Copiar Templates con Temporizadores en GoHighLevel (y Por Qué Parece que Se Reinician)

## Meta description propuesta (≤155)

Según HighLevel, los temporizadores en emails suelen ser GIFs que cuentan hasta
60 segundos por apertura. Aprende a crearlos, clonarlos y verificarlos.

---

## Respuesta rápida

Según la documentación de HighLevel, los temporizadores de cuenta regresiva se
crean en **Marketing > Countdown Timer** y hay tres tipos: fijo (cuenta hacia una
fecha concreta), recurrente (se reinicia al llegar a cero) y dinámico
(personalizado por acción de cada usuario, como la apertura de un email). En los
emails, el temporizador **típicamente se implementa como un GIF que cuenta desde
el momento en que el lector abre el mensaje, hasta por 60 segundos**, y se
refresca si el email se vuelve a abrir. Ese comportamiento documentado es lo
primero a descartar cuando un temporizador de email parece reiniciarse — conviene
conocerlo antes de copiar o clonar templates.

## Lo que necesitas antes de empezar

- Una cuenta de GoHighLevel con acceso al Email Marketing y al Template Library.
- Saber dónde se crean los temporizadores: Marketing > Countdown Timer (lo harás
  en el Paso 1).
- Claridad sobre qué tipo de temporizador usa tu campaña: fijo, recurrente o
  dinámico. La documentación de HighLevel define el recurrente como uno que se
  reinicia al llegar a cero — si tu campaña usa ese tipo, el reinicio es el
  comportamiento esperado, no un error.

## Paso 1: Configura tu temporizador

Según la guía oficial, ve a **Marketing > Countdown Timer** y configura el tipo
que corresponda a tu campaña:

- **Fijo** — cuenta regresiva hacia una fecha y hora concretas; la documentación
  lo recomienda para eventos tipo Black Friday o lanzamientos.
- **Recurrente** — se reinicia después de llegar a cero; pensado para
  promociones continuas.
- **Dinámico** — personalizado para cada usuario según sus acciones (por
  ejemplo, la apertura del email).

Según la misma documentación, al expirar el temporizador muestra una imagen de
expiración que redirige a la página de expiración que definas; en funnels, esa
página se muestra automáticamente al terminar el tiempo.

[CTA-MID-1: prueba gratis 30 días]

## Paso 2: Inserta el temporizador en tu template de email

El flujo documentado por HighLevel:

1. Crea o abre tu template de campaña en **Email Marketing**.
2. Inserta el elemento de countdown timer en el email.
3. Elige el diseño del temporizador.
4. En ajustes, alinéalo dentro del email y ajusta el color de fondo y el
   espaciado interno (padding).
5. Copia el enlace de redirección del temporizador y úsalo en los botones del
   email.

## Paso 3: Clona el template — y verifica

Según la documentación, la función de clonado del Template Library existe para
mantener la simetría de tu marca y reducir el tiempo de construir un canal
nuevo partiendo de un template existente (traducción propia). Lo que la
documentación **no** describe es ningún comportamiento especial de los
temporizadores al clonar un template — ni a favor ni en contra. Por eso, la
práctica sensata para una agencia es verificar, no asumir:

**Checklist de verificación después de clonar un template con temporizador:**

1. Abre el template clonado y confirma que el elemento del temporizador sigue
   presente y apunta al temporizador correcto (no a uno de otra campaña).
2. Revisa el tipo: si es recurrente, reiniciarse al llegar a cero es su
   comportamiento documentado.
3. Confirma que los botones del email usan el enlace de redirección del
   temporizador de ESTA campaña.
4. Envíate un email de prueba y ábrelo dos veces: según la documentación,
   normalmente el GIF cuenta de nuevo desde cada apertura, hasta por 60
   segundos. Haz la prueba fuera de Apple Mail, que cachea los GIFs (ver
   Límites).
5. Confirma la página de expiración configurada para el temporizador.

[CTA-MID-2: ¿Quieres armarlo con tu propia cuenta? Empieza tu prueba gratis de
30 días aquí →]

## ¿Por qué parece que los temporizadores "se reinician"?

La explicación, tal como la documenta HighLevel (traducción propia): los
countdown timers en emails se implementan típicamente como GIFs. El temporizador
cuenta desde el momento en que el usuario abre el email, hasta por 60 segundos,
y si el lector vuelve a abrir el mensaje, el GIF se refresca y cuenta de nuevo.

Es decir: si un temporizador de email vuelve a arrancar al abrir el mensaje, eso
puede coincidir con el comportamiento documentado — no basta para concluir que
el template se rompió. Antes de asumir un error tras clonar un template, el
primer punto a revisar es este mecanismo documentado; y si tu temporizador es
recurrente, su reinicio al llegar a cero también es comportamiento esperado.

Un matiz más, también documentado: **Apple Mail cachea los GIFs**, así que en
ese cliente de correo el temporizador puede parecer que deja de avanzar después
de la primera apertura. Si un cliente de tu agencia reporta un temporizador
congelado en iPhone, Apple Mail es una causa documentada que conviene revisar
primero.

## Límites que debes conocer

- Máximo 60 segundos de conteo visible por apertura en emails (por el enfoque
  GIF, según la documentación).
- Apple Mail: GIF cacheado — el temporizador puede verse congelado tras la
  primera apertura.
- En funnels el comportamiento es distinto al email: la página de expiración se
  muestra automáticamente al llegar a cero.

[CTA-BOTTOM-BOX: ¿Listo para probarlo? $0 por 30 días]

---

## Notas de ensamblaje (no publicar)

- Up-link al hub del silo Agency + link circle (assembly manifest).
- Sin sección FAQ separada; sin lista de países; disclosure nivel bio + footer.
- Todas las citas de documentación son traducción propia del inglés (marcado una
  vez en la sección de explicación).
- NO se asevera rotura al copiar en ninguna parte; NO se menciona copiado entre
  subcuentas/cuentas (fuera del alcance de las fuentes).

## Fix map (v1 → v2)

- Codex B: "GIF que cuenta" → "típicamente… hasta por 60 segundos" (answer box,
  checklist 4, sección explicación). "la mayoría de las sorpresas" → "lo primero
  a descartar". "verás el GIF" → "según la documentación, normalmente…" + nota
  Apple Mail. "no está roto — exactamente" → "puede coincidir… no basta para
  concluir". "Si copiaste… lo más probable" → eliminado (sin diagnóstico, sin
  subcuentas). "esa es la causa" → "una causa documentada que conviene revisar
  primero".
- Claude B1: cita fabricada "partir de un template existente" → paráfrasis sin
  comillas. B2: diagnóstico + subcuentas → eliminado. B3: "típicamente" añadido
  también en meta description (≤155). B4: cuantificador eliminado.
- Claude W1: checklist 3 → verificación pura (sin mecanismo de fallo). W2:
  "(traducción propia)" añadido; comillas internas retiradas. W3: absencia
  limitada a clonar; heading sin "comparte". W4: prueba fuera de Apple Mail.
  W5: "cliente de correo" / "cliente de tu agencia". W6: prerequisito circular
  reformulado. W7: "entre cuentas" eliminado del answer box.
- Style (ambos): "Configura tu temporizador"; "espaciado interno (padding)";
  "sin mitos" eliminado; "página de expiración" consistente; "hay tres tipos";
  "conteo visible"; terminología "temporizador" dominante, "countdown timer"
  solo como nombre de la función; meta ≤155.
