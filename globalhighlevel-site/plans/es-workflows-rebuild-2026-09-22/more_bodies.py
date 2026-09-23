"""Remaining Spanish rebuild bodies. Imported by apply_rebuild.py."""

MORE: dict[str, tuple[str, str]] = {}

def _src(url: str, label: str, modified: str) -> str:
    if modified.startswith("consultado"):
        note = modified
    else:
        note = f"artículo modificado {modified}. Consultado el 22 de septiembre de 2026"
    return (
        f'<li><a href="{url}" rel="nofollow noopener" target="_blank">{label}</a> '
        f'— {note}.</li>'
    )

# CTA is passed in by the caller via format? We'll embed the same CTA string
# by importing from apply would cycle. Duplicate the short CTA marker and
# let apply_rebuild replace __CTA__.
C = "__CTA__"

MORE["gohighlevel-workflows-practicos-casos-de-uso-reales-agencias-digitales"] = (
    "Cuatro usos que documenta HighLevel: cita por WhatsApp, pago en Success, formulario que crea la oportunidad y una plantilla de workflow que puedes editar.",
    f"""<h2>Respuesta rápida</h2>
<p>Esta página no trae un caso de una agencia con nombre, ciudad y cifra de cierre. Esos relatos se retiraron porque no se podían verificar. Lo que sí está en la documentación de HighLevel, consultada el 22 de septiembre de 2026, son cuatro usos que puedes armar hoy: un recordatorio de cita por WhatsApp, un aviso cuando un pago queda en Success, un formulario que crea una oportunidad, y una plantilla de flujo que cargas y editas.</p>
<p>El plan de la plataforma empieza en 97 USD al mes. No hay en estas guías una suma de "siete suscripciones" ni un margen promedio de agencia que valga la pena repetir.</p>
<h2>Uso 1: Recordatorio de cita por WhatsApp</h2>
<p>La guía de la acción WhatsApp (8 de abril de 2025) da este ejemplo, no un cliente nuestro:</p>
<ul>
<li>Disparador: Appointment Reminder.</li>
<li>Acción: WhatsApp, con una plantilla de recordatorio.</li>
<li>El texto de ejemplo de la guía es: Hi {{{{contact.first_name}}}}, this is a reminder for your appointment scheduled on {{{{appointment.date}}}}.</li>
</ul>
<p>Fuera de la ventana de 24 horas el envío es una plantilla aprobada, no texto libre. Si la persona responde, la guía llama Free Entry Point a la conversación en la que puedes escribir libre o con plantilla hasta por 72 horas sin costo adicional de esa conversación.</p>
<h2>Uso 2: Aviso cuando el pago entra</h2>
<p>La guía de Payment Received (15 de abril de 2026) dice que el disparador corre cuando un pago se procesa en la cuenta: funnel, factura, calendario, membresía, formulario o un pago manual. Para que no corra en un fallo, filtra <strong>Payment Status = Success</strong>. El origen se filtra aparte: Calendar, External, Form, Funnel, Invoice, Manual Payment, Memberships o Website.</p>
<p>El artículo dice que el mecanismo es agnóstico de pasarela para cualquier gateway conectado. Mercado Pago se conecta en Payments como proveedor. El alta de credenciales y el webhook no se repiten aquí.</p>
<p>Conekta, PayU y Transbank no salen en la guía de Mercado Pago como conectores nativos. No los sumes a esta lista.</p>
<h2>Uso 3: Un formulario crea la oportunidad</h2>
<p>La guía de pipelines (Getting Started) documenta este flujo, con etapas de ejemplo New Lead, Booked Call o Closed. Esos nombres son del artículo, no un pipeline inmobiliario cerrado:</p>
<ol>
<li>Crea el pipeline en Opportunities &gt; Pipelines &gt; Create New Pipeline, con las etapas que correspondan a tu proceso, y guarda.</li>
<li>En Automation &gt; Workflows, crea un flujo desde cero.</li>
<li>Disparador: Form Submitted, y elige el formulario.</li>
<li>Acción: Opportunity &gt; Create/Update Opportunity. Elige pipeline y etapa, estado Open, un valor si lo conoces, y Allow Opportunity to Move si quieres que una reentrada actualice la ficha.</li>
<li>Publica. La guía dice que cada envío futuro cae en esa etapa.</li>
</ol>
<p>Cómo se ve esa ficha en el tablero está en <a href="/blog/vista-kanban-gohighlevel-gestionar-deals/">la guía de la vista Kanban</a>.</p>
<h2>Uso 4: Empezar por una plantilla, no desde cero</h2>
<p>La guía de Template Library (13 de agosto de 2025) abre el modal así: Automation, pestaña Workflows, Create Workflow, <strong>Select from Template</strong>. Filtras por categoría, lees About this Template y los requisitos, miras el lienzo y pulsas Continue. Después editas disparadores, acciones y tiempos. La guía pide probar en borrador antes de activar. También dice que hoy no puedes guardar tus propios flujos como plantillas de esa biblioteca, y que cargar una plantilla no toca los flujos que ya tenías.</p>
<p>El paso a paso de esa biblioteca está en <a href="/blog/workflows-gohighlevel-plantillas-agencias-5-minutos/">la guía de plantillas de workflows</a>. La documentación habla de minutos, no de un cronómetro de cinco minutos.</p>
<h2>Qué quedó fuera a propósito</h2>
<ul>
<li>Ningún porcentaje de apertura de WhatsApp. La guía de la acción no lo publica.</li>
<li>Ningún ahorro mensual contra un stack de siete herramientas. No hay una factura así en las fuentes de esta página.</li>
<li>Ningún "caso real" con dueño, ciudad y resultado. Si más adelante hay una captura atestada o un hilo público con nombre, se cita. Hasta entonces, no.</li>
</ul>
<h2>Preguntas frecuentes</h2>
<h3>¿Estos cuatro usos son clientes de esta web?</h3>
<p>No. Son ejemplos y pasos de los artículos de HighLevel citados abajo.</p>
<h3>¿Puedo mezclar el formulario y el pago en el mismo flujo?</h3>
<p>La guía de Payment Received dice que puedes tener varios disparadores en un flujo o partir la lógica con If/Else. No dice que un solo disparador cubra el formulario y el pago a la vez: son eventos distintos.</p>
<h2>Fuentes</h2>
<ul>
{_src("https://help.gohighlevel.com/support/solutions/articles/155000003531-workflow-action-whatsapp", "Workflow Action - WhatsApp", "el 8 de abril de 2025")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000003534-workflow-trigger-payment-received", "Workflow Trigger - Payment Received", "el 15 de abril de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000005062-getting-started-setup-pipelines-and-opportunities", "Getting Started - Setup Pipelines and Opportunities", "consultado el 22 de septiembre de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000005613-template-library-for-workflows", "Template Library for Workflows", "el 13 de agosto de 2025")}
</ul>
{C}
""",
)

MORE["maestro-ai-flow-builder-gohighlevel-setup-completo"] = (
    "Abre Conversation AI Flow Builder, deja el bot en Auto Pilot y arma captura, cita y fin de chat. Ese lienzo no es el generador de workflows por prompt.",
    f"""<h2>Respuesta rápida</h2>
<p>El AI Flow Builder de esta página es el <strong>Conversation AI Flow Builder</strong> de la guía de HighLevel modificada el 1 de junio de 2026. No es el Workflow AI Builder, que genera un flujo de automatización a partir de un prompt. Ese otro producto está en <a href="/blog/ai-help-gohighlevel-workflows-construccion-rapida/">la guía de construcción de workflows con IA</a>.</p>
<p>La propia guía avisa que el lienzo se parece al de automatizaciones y no se comporta igual. Lo abres cuando quieres que el bot siga un camino de conversación dentro de Conversation AI. Si quieres que un workflow pregunte, espere respuesta y siga, la guía manda usar la acción de Conversation AI en el Workflow Builder, no este lienzo.</p>
<h2>Paso 1: Crear el bot</h2>
<p>Ve a <strong>AI Agents &gt; Conversation AI &gt; Create Bot &gt; Create New Bot (Flow Based Builder)</strong>.</p>
<p>En Bot Settings:</p>
<ul>
<li>Nombra el bot.</li>
<li>Pon el estado en <strong>Auto Pilot</strong>.</li>
<li>Marca o desmarca canales: SMS, Facebook, Instagram, WhatsApp y Live Chat, solo los que el bot tenga habilitados.</li>
<li>Sube el máximo de mensajes. La guía pone como ejemplo algo como 100, porque el flujo puede ser largo.</li>
<li>Guarda.</li>
</ul>
<h2>Paso 2: Objetivos del bot</h2>
<p>La guía dice que los Bot Goals (personalidad, intención y el resto) son un prompt global que entra en cada acción del flujo.</p>
<ul>
<li>Elige el tono con una o más palabras. El ejemplo del artículo es friendly y confident.</li>
<li>Describe personalidad y estilo con frases y campos, por ejemplo que el bot es de {{{{ai.business_name}}}}.</li>
<li>Describe la intención, por ejemplo ayudar a elegir un objetivo y agendar.</li>
<li>Agrega contexto y ejemplos de cómo sí hablar y cómo no hablar.</li>
</ul>
<p>Condiciones que la guía nombra:</p>
<ul>
<li><strong>Stop Bot</strong>: si la persona insulta o dice stop, el flujo se detiene.</li>
<li><strong>Human Handover</strong>: si el bot no sabe o piden una persona, se detiene y avisa a un humano.</li>
<li><strong>Auto Followup</strong>: la guía lo marca como coming soon. No lo des por activo.</li>
</ul>
<p>En citas puedes permitir cancelar y reprogramar. Guarda los objetivos.</p>
<h2>Paso 3: Abrir el lienzo</h2>
<p>En la pestaña de objetivos, pulsa <strong>Launch Flow Builder</strong>. Sabes que estás en el lienzo de Conversation AI, y no en automatizaciones, porque dice Back to Conversation AI y Test Bot, no Workflow.</p>
<p>El disparador por defecto es <strong>Chat Initiated</strong>. La guía dice que es la única forma de empezar el flujo. Los custom triggers no lo inician.</p>
<p>Un nodo [END] cierra el objetivo, no el chat. La conversación sigue sin un objetivo hasta que la cortes con el máximo de mensajes, un timeout o la acción End Conversation.</p>
<h2>Paso 4: Acciones de IA</h2>
<p>El botón + abre acciones. La guía lista estas, además de las acciones normales del workflow:</p>
<ul>
<li><strong>Capture Information / Qualify.</strong> Describes el objetivo (máximo 500 caracteres), puedes escribir un campo del contacto, instrucciones extra, un formato de respuesta, saltar el objetivo si el campo ya viene lleno, un máximo de intentos, cortar si no se cumple el criterio y poner una etiqueta al final. Esta acción y Book Appointment insisten hasta cumplir el objetivo o hasta una salida, por ejemplo el máximo de intentos.</li>
<li><strong>Book Appointment.</strong> Prompt de reserva, calendario, rama de cita creada y rama de cita no creada. Sigue intentando hasta reservar o hasta una salida clara, por ejemplo que la persona diga que no quiere agendar.</li>
<li><strong>End Conversation.</strong> Mensaje literal, sin que la IA lo reescriba. Puedes reactivar el bot después de un número de horas u otra unidad.</li>
<li><strong>AI Splitter.</strong> No envía mensajes. Solo clasifica lo ya recogido. Tiene una rama por defecto si ninguna condición cuadra, más las ramas que definas.</li>
<li><strong>AI Message.</strong> Se ejecuta una vez. El prompt describe el mensaje y puedes esperar la respuesta.</li>
<li><strong>Custom Message.</strong> Se envía el texto exacto que escribes, una vez.</li>
<li><strong>Transfer Bot.</strong> Pasa el contacto a otro bot y sale de este flujo. No vuelve salvo que otro transfer lo regrese.</li>
<li><strong>Continue Conversation.</strong> Instrucciones para seguir charlando cuando ya no queda un objetivo.</li>
</ul>
<h2>Custom triggers</h2>
<p>Puedes tener hasta tres. Cada uno tiene una descripción de la condición, una prioridad del 1 al 10 y una sensibilidad Low, Medium o High. La guía dice que, hoy, disparan cuando el contacto ya llegó a un nodo [END], no a mitad del flujo. La sensibilidad a mitad del flujo está descrita como un comportamiento próximo, no como el actual. Un If/Else puede enrutar Chat Initiated y cada custom trigger por una rama distinta.</p>
<h2>Lo que este builder no documenta</h2>
<p>La guía no menciona Mercado Pago, Conekta ni ningún cobro dentro del bot. Conectar un pago es la integración de Payments, no un paso de este lienzo. Tampoco publica un multiplicador de velocidad.</p>
<h2>Preguntas frecuentes</h2>
<h3>¿El bot puede arrancar con otro disparador que no sea Chat Initiated?</h3>
<p>No, según la pregunta frecuente de la guía. Los custom triggers redirigen después, no encienden el flujo.</p>
<h3>¿AI Message y Custom Message son lo mismo?</h3>
<p>No. AI Message redacta a partir del prompt y del contexto. Custom Message envía el texto tal cual.</p>
<h2>Fuentes</h2>
<ul>
{_src("https://help.gohighlevel.com/support/solutions/articles/155000006515-conversation-ai-flow-builder", "Conversation AI Flow Builder", "el 1 de junio de 2026")}
</ul>
{C}
""",
)

MORE["configurar-facebook-instagram-messaging-gohighlevel"] = (
    "Conecta Facebook e Instagram Messenger con la bandeja de HighLevel, prueba el mensaje desde otra cuenta y respeta las 24 horas del DM de Instagram en el flujo.",
    f"""<h2>Respuesta rápida</h2>
<p>La guía de HighLevel modificada el 18 de agosto de 2026 conecta Facebook e Instagram Messenger para que los mensajes lleguen a Conversations. No es un reemplazo de Clientify, HubSpot o Zoho con una tabla de precios inventada: es el alta del canal y la prueba de que el mensaje entra y la respuesta sale.</p>
<h2>Paso 1: Conectar la página</h2>
<ol>
<li>Ve a <strong>Settings &gt; Integrations</strong>.</li>
<li>Pulsa <strong>Connect</strong> en Facebook &amp; Instagram.</li>
<li>Entra a Facebook y elige la página que está ligada a Instagram.</li>
<li>Pulsa Connect Facebook &amp; Instagram.</li>
<li>Pulsa <strong>Sync Leads</strong>.</li>
</ol>
<h2>Paso 2: Ligar Instagram a la página de Facebook</h2>
<p>En Facebook, entra a la página, luego Account &gt; Settings, busca Linked Accounts, elige Instagram y conecta. Deja activo el interruptor para que los mensajes de Instagram aparezcan en la bandeja y autentica Instagram.</p>
<h2>Paso 3: Probar con otra cuenta</h2>
<p>La guía pide probar desde una cuenta distinta a la del negocio.</p>
<h3>Facebook</h3>
<ol>
<li>Desde otra cuenta de Facebook, abre la página conectada.</li>
<li>Pulsa Message y envía un texto de prueba.</li>
<li>En la subcuenta, abre Conversations y confirma que el mensaje está en el historial.</li>
</ol>
<h3>Instagram</h3>
<ol>
<li>Desde otra cuenta de Instagram, abre el perfil del negocio.</li>
<li>Envía un DM.</li>
<li>En Conversations, abre esa conversación y confirma el texto.</li>
</ol>
<p>La conexión está bien cuando el mensaje aparece en Conversations, bajo el contacto correcto, y cuando respondes desde HighLevel y la respuesta llega a la cuenta de prueba.</p>
<h2>Si el mensaje no aparece</h2>
<ol>
<li>En Settings &gt; Integrations, confirma que la página y la cuenta de Instagram son las correctas.</li>
<li>Confirma que el acceso a mensajes está habilitado.</li>
<li>Revisa los permisos de Facebook e Instagram.</li>
<li>Confirma que Instagram está ligado a esa página.</li>
<li>Envía otro mensaje de prueba.</li>
</ol>
<p>La guía corta de troubleshooting (20 de agosto de 2025) agrega tres chequeos: que LeadConnector pueda enviar y leer mensajes de la página, que el usuario tenga acceso completo a la página y a los mensajes, y que Messenger esté activo en Settings &gt; Integration &gt; la tarjeta de Facebook &gt; Settings. En Instagram, la cuenta tiene que figurar en los activos conectados de la página.</p>
<h2>Qué hace HighLevel con el contacto</h2>
<p>El primer mensaje de Facebook o Instagram crea o actualiza un contacto según tus preferencias de deduplicación. Si después comparten un email o teléfono que ya existe y Allow Duplicate Contact está apagado, HighLevel fusiona el contacto del messenger con el registro existente. Si Allow Duplicate Contact está encendido, no fusiona y pueden quedar dos fichas.</p>
<h2>Responder por un flujo, no solo a mano</h2>
<p>La acción Instagram DM (4 de septiembre de 2024) envía un DM solo si el contacto escribió a la página conectada en las últimas 24 horas. La guía recomienda usar Instagram Interactive Messenger:</p>
<ul>
<li>Si respondes un comentario, Reply Type = Reply to Comment via DM.</li>
<li>Si respondes un DM, Reply Type = Reply to DM.</li>
</ul>
<p>Hasta el 31 de agosto de 2024 un fallo de Meta dejaba enviar un DM a quien comentaba aunque no hubiera escrito en 24 horas. La guía dice que ese fallo ya se corrigió. No armes el flujo como si ese atajo siguiera vivo.</p>
<p>La receta Facebook comments + Workflow AI (8 de abril de 2025) es un ejemplo documentado, no un cliente: el disparador es un comentario de primer nivel, una acción manda el comentario a OpenAI para redactar la respuesta, otra responde en comentarios, otra pide un análisis de sentimiento y parte el flujo, y si el sentimiento es positivo envía un DM interactivo.</p>
<p>Para mover ese contacto a un tablero, la acción Create/Update Opportunity existe en la lista de acciones. El uso del tablero está en <a href="/blog/vista-kanban-gohighlevel-gestionar-deals/">la vista Kanban</a>.</p>
<h2>Preguntas frecuentes</h2>
<h3>¿Puedo probar el mensaje desde la misma cuenta del negocio?</h3>
<p>La guía pide otra cuenta. Probar desde la cuenta conectada no reproduce lo que hace un cliente.</p>
<h3>¿Un comentario de Instagram autoriza un DM directo sin ventana de 24 horas?</h3>
<p>No, según la nota del 4 de septiembre de 2024. Si usas el disparador de comentarios, el DM sale como respuesta al comentario cuando hay un comentario reciente, o como DM directo solo si además hubo un DM en las últimas 24 horas.</p>
<h2>Fuentes</h2>
<ul>
{_src("https://help.gohighlevel.com/support/solutions/articles/155000005068-getting-started-setup-facebook-and-instagram-messenger", "Getting Started - Setup Facebook and Instagram Messenger", "el 18 de agosto de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000006069-messaging-setup-troubleshoot", "Messaging setup and troubleshoot", "el 20 de agosto de 2025")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000003298-instagram-dm-workflow-action", "Instagram DM - Workflow Action", "el 4 de septiembre de 2024")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000004659-workflow-recipes-facebook-comments-workflow-ai", "Workflow Recipes - Facebook comments + Workflow AI", "el 8 de abril de 2025")}
</ul>
{C}
""",
)

MORE["vista-kanban-gohighlevel-gestionar-deals"] = (
    "Vista Kanban de Opportunities en HighLevel: contrae etapas, cambia el ancho de columna, ordena por fecha o valor y el diseño queda en tu navegador. Es tuyo.",
    f"""<h2>Respuesta rápida</h2>
<p>La vista Kanban de HighLevel, en la guía modificada el 2 de abril de 2026, muestra las oportunidades por etapa del pipeline. Puedes contraer etapas, cambiar el ancho de las columnas, ordenar y pasar a la vista de lista. El diseño se guarda en el navegador y no cambia la vista de tus compañeros.</p>
<p>La guía no dice que una agencia en Latinoamérica pierda un porcentaje de deals por no usar el tablero. Esa cifra no está aquí.</p>
<h2>Paso 1: Abrir el tablero</h2>
<ol>
<li>Abre <strong>Opportunities</strong>.</li>
<li>Quédate en la vista Kanban, no en List View. La de lista es la que sirve cuando necesitas filas y columnas.</li>
</ol>
<h2>Paso 2: Contraer o expandir una etapa</h2>
<ol>
<li>Localiza la columna.</li>
<li>Pulsa el control del encabezado de la etapa para contraerla o expandirla.</li>
</ol>
<p>La guía de personalización de tarjetas describe el mismo gesto como pulsar el encabezado (&gt; o &lt;). Sirve para esconder etapas que casi no usas.</p>
<h2>Paso 3: Cambiar el ancho</h2>
<ol>
<li>En Kanban, pasa el cursor por el borde de la columna.</li>
<li>Arrastra el divisor.</li>
<li>Doble clic en el divisor devuelve el ancho por defecto.</li>
</ol>
<h2>Paso 4: Ordenar</h2>
<ol>
<li>Pulsa <strong>Sort</strong> arriba.</li>
<li>Elige el campo. La guía incluye campos por defecto, como Created On y Last Updated, y campos personalizados de estos tipos: Single Line, Multi Line Text, Dropdown, Radio Select, Number, Monetary, Phone y Date.</li>
<li>Elige ascendente o descendente. Las tarjetas se reordenan solas.</li>
</ol>
<h2>Qué se guarda y qué no</h2>
<ul>
<li>Etapas contraídas y anchos se guardan solos.</li>
<li>Eso vive en el almacenamiento local del navegador.</li>
<li>Es solo tu vista. Otro usuario no la hereda.</li>
<li>Otro navegador u otro dispositivo puede no traer ese diseño.</li>
</ul>
<p>La guía de tarjetas agrega que los campos visibles de la tarjeta se editan con Manage Fields, que el ajuste es por pipeline y puede aplicarse a todos los pipelines de la location, y que sigue siendo específico del usuario.</p>
<h2>Crear el pipeline que el tablero muestra</h2>
<p>La guía de pipelines define cuatro palabras: Pipeline es el proceso, Stage es un paso, Opportunity es el trato, Contact es la persona. Un ejemplo de etapas del artículo es New Lead, Booked Call o Closed. Pon las etapas que tu equipo realmente usa. La guía de edición dice que las etapas deben ser claras y orientadas a una acción.</p>
<ol>
<li>Opportunities &gt; Pipelines &gt; Create New Pipeline.</li>
<li>Nombre, etapas y guardar.</li>
</ol>
<p>El artículo de pipelines dice que la página usa el sistema HighRise y que esa actualización se enciende en Sub-account &gt; Labs. Si tu listado de pipelines no se ve como el artículo, revisa Labs antes de concluir que la función no está. La guía de Kanban del 2 de abril no pide Labs para contraer, ensanchar y ordenar.</p>
<p>Si borras una etapa, la guía de edición dice que puedes mover las oportunidades existentes a otra etapa antes de confirmar.</p>
<h2>Llenar el tablero con un formulario</h2>
<p>La guía Getting Started documenta la automatización, y dice que también puedes crear oportunidades a mano o importarlas. No hace falta un flujo para tener fichas.</p>
<ol>
<li>Automation &gt; Workflows, flujo nuevo desde cero o desde una plantilla.</li>
<li>Disparador Form Submitted, el formulario concreto, guardar.</li>
<li>Acción Create/Update Opportunity: pipeline, etapa, estado Open, valor si lo tienes, y Allow Opportunity to Move si una reentrada debe actualizar la ficha.</li>
<li>Publica.</li>
</ol>
<p>Para una inmobiliaria que arma sus propias etapas, el contexto está en <a href="/blog/gohighlevel-inmobiliarias-automatiza-consultas-ventas/">la guía de consultas inmobiliarias</a>. No es un módulo inmobiliario aparte: es este mismo pipeline.</p>
<h2>Preguntas frecuentes</h2>
<h3>¿El orden y el ancho los ven todos en la cuenta?</h3>
<p>No. La guía dice que el diseño es tuyo y queda en ese navegador.</p>
<h3>¿Qué campos puedo usar para ordenar?</h3>
<p>Created On, Last Updated y los tipos de campo personalizado que lista la guía: texto de una línea, texto multilínea, desplegable, radio, número, monetario, teléfono y fecha.</p>
<h2>Fuentes</h2>
<ul>
{_src("https://help.gohighlevel.com/support/solutions/articles/155000007528-use-kanban-view-in-opportunities", "Use Kanban View in Opportunities", "el 2 de abril de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000003910-customize-opportunity-cards-in-board-view", "Customize Opportunity Cards in Board View", "consultado el 22 de septiembre de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000005062-getting-started-setup-pipelines-and-opportunities", "Getting Started - Setup Pipelines and Opportunities", "consultado el 22 de septiembre de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000001982-understanding-pipelines", "Understanding Pipelines", "consultado el 22 de septiembre de 2026")}
</ul>
{C}
""",
)

MORE["workflows-gohighlevel-plantillas-agencias-5-minutos"] = (
    "Carga un workflow desde la Template Library de HighLevel, filtra, lee requisitos y edítalo. La guía habla de minutos, no de un tope de cinco. Prueba en Draft.",
    f"""<h2>Respuesta rápida</h2>
<p>La Template Library de workflows, en la guía modificada el 13 de agosto de 2025, sirve para cargar un flujo prediseñado, leer sus requisitos y editarlo. La guía dice que así lanzas automatizaciones en minutos. No publica un límite de cinco minutos. El título histórico de esta página dice "5 minutos"; el cuerpo sigue lo que el artículo sí escribe.</p>
<p>No reemplaza la revisión. La misma guía pide probar en borrador antes de activar.</p>
<h2>Paso 1: Abrir la biblioteca</h2>
<ol>
<li>En el menú izquierdo, pulsa <strong>Automation</strong>.</li>
<li>Entra a la pestaña <strong>Workflows</strong>.</li>
<li>Pulsa <strong>Create Workflow</strong>.</li>
<li>Elige <strong>Select from Template</strong>.</li>
</ol>
<h2>Paso 2: Filtrar</h2>
<p>El panel de filtros acota por categoría. El ejemplo del artículo es Lead Nurture u Onboarding. También puedes buscar por palabra u ordenar por popularidad. Al pasar el cursor por una tarjeta ves una descripción corta.</p>
<h2>Paso 3: Previsualizar y cargar</h2>
<ol>
<li>Pulsa el icono del ojo o la tarjeta.</li>
<li>Lee About this Template y los Prerequisites.</li>
<li>Revisa el lienzo completo de disparadores y acciones.</li>
<li>Pulsa <strong>Continue</strong> para cargarlo en el editor.</li>
</ol>
<p>Después cambias disparadores, acciones, esperas y condiciones. Prueba con un contacto o una etiqueta de muestra, guarda y activa solo cuando el resultado sea el que esperabas.</p>
<h2>Límites que la guía escribe</h2>
<ul>
<li>No puedes crear tus propias plantillas en esa biblioteca. La pregunta frecuente dice que, por ahora, la función no está disponible.</li>
<li>Todo lo cargado se puede editar.</li>
<li>Seguirán agregando plantillas. No hay una lista cerrada en el artículo.</li>
<li>Cargar una plantilla no modifica los flujos que ya tenías publicados.</li>
<li>Para volver al original, vuelve a seleccionar la misma plantilla. Eso no deshace un flujo ya activado por arte de magia: te da otra copia desde el original.</li>
</ul>
<h2>Qué revisar antes de publicar</h2>
<p>La guía de buenas prácticas pide tres cosas: mirar si la biblioteca tiene una versión más nueva, adaptar textos y tiempos a tu proceso, y dejar el flujo en Draft con un subconjunto pequeño antes de encenderlo para todos. Compartir el enlace de una plantilla con el equipo es el método que el artículo describe para estandarizar. No es un caso de una agencia con resultados medidos.</p>
<p>Cuatro usos concretos, armados con otras guías y no con una plantilla sin nombre, están en <a href="/blog/gohighlevel-workflows-practicos-casos-de-uso-reales-agencias-digitales/">workflows prácticos para agencias</a>.</p>
<h2>Preguntas frecuentes</h2>
<h3>¿Puedo guardar mi flujo como plantilla de la biblioteca?</h3>
<p>No, según la pregunta frecuente del 13 de agosto de 2025.</p>
<h3>¿Cargar una plantilla pisa mis automatizaciones actuales?</h3>
<p>No. El artículo dice que tus automatizaciones actuales quedan intactas.</p>
<h2>Fuentes</h2>
<ul>
{_src("https://help.gohighlevel.com/support/solutions/articles/155000005613-template-library-for-workflows", "Template Library for Workflows", "el 13 de agosto de 2025")}
</ul>
{C}
""",
)

MORE["gohighlevel-inmobiliarias-automatiza-consultas-ventas"] = (
    "Para una inmobiliaria en HighLevel: pipeline propio, formulario que crea la oportunidad y WhatsApp con plantilla. No hay una tasa de cierre oficial de la guía.",
    f"""<h2>Respuesta rápida</h2>
<p>HighLevel no publica, en las guías usadas aquí, un módulo inmobiliario con tasa de cierre. Lo que sí puedes configurar para una consulta de propiedad es un pipeline con tus etapas, un formulario que crea la oportunidad y un WhatsApp que responde con plantilla cuando la persona no acaba de escribir. Esta página no trae una inmobiliaria con nombre ni un porcentaje de ventas.</p>
<p>El tablero donde se ven esas oportunidades está en <a href="/blog/vista-kanban-gohighlevel-gestionar-deals/">la vista Kanban</a>.</p>
<h2>Paso 1: Etapas que sí usas</h2>
<p>La guía de pipelines dice que una etapa es un paso del proceso y que conviene que sea una acción, no una etiqueta vaga. El ejemplo del artículo es New Lead, Booked Call o Closed. Una inmobiliaria puede nombrar las suyas —consulta nueva, visita agendada, oferta, cerrada— siempre que el equipo sepa cuándo mover la ficha. Esos nombres en español son una adaptación del ejemplo, no una plantilla oficial de HighLevel.</p>
<ol>
<li>Abre <strong>Opportunities &gt; Pipelines</strong>.</li>
<li>Pulsa <strong>Create New Pipeline</strong>.</li>
<li>Escribe el nombre y las etapas. Guarda.</li>
</ol>
<p>Si más adelante borras una etapa, la guía de edición dice que puedes mover las oportunidades existentes a otra etapa antes de confirmar el borrado.</p>
<h2>Paso 2: La consulta crea la oportunidad</h2>
<p>La guía Getting Started documenta este automatismo. También dice que puedes crear la oportunidad a mano o importarla. El flujo no es obligatorio.</p>
<ol>
<li>Automation &gt; Workflows &gt; Create Workflow &gt; Start from Scratch.</li>
<li>Disparador <strong>Form Submitted</strong>. Elige el formulario de la consulta. Guarda el disparador.</li>
<li>Acción <strong>Create/Update Opportunity</strong>. Pipeline, etapa inicial, estado Open. Si conoces un valor, cárgalo. Activa Allow Opportunity to Move si una segunda consulta de la misma persona debe actualizar la ficha en lugar de ignorarla.</li>
<li>Pasa de borrador a publicado cuando lo hayas probado.</li>
</ol>
<h2>Paso 3: El mensaje de WhatsApp</h2>
<p>La acción WhatsApp (8 de abril de 2025) envía texto libre dentro de la ventana de 24 horas y plantilla aprobada fuera de ella. Una consulta que llega por formulario, y no por un chat recién abierto, cae fuera de esa ventana: el primer aviso sale con plantilla. El ejemplo literal de la guía es un recordatorio de cita con {{{{contact.first_name}}}} y {{{{appointment.date}}}}. Sirve de formato. El texto comercial de tu plantilla lo aprueba Meta; no lo inventes aquí y lo des por aprobado.</p>
<p>Si la persona responde, la guía describe una Free Entry Point de hasta 72 horas para texto libre o plantilla, sin costo adicional de esa conversación. Puedes respetar quien pidió silencio con DND de WhatsApp.</p>
<p>WhatsApp en la subcuenta se da de alta en Settings &gt; WhatsApp: app existente, número nuevo o migración desde otro proveedor. El error 131042 bloquea envíos si Meta no tiene un método de pago en la cuenta de WhatsApp Business, aunque el CRM esté pagado. El artículo de ese error dice que hay 1.000 conversaciones de servicio al mes sin cargo y que, superado el cupo, hace falta el método de pago en Meta.</p>
<h2>Paso 4: Mirar el tablero, no una hoja suelta</h2>
<p>En Opportunities, vista Kanban, cada etapa es una columna. Puedes contraer las que no estás trabajando, ensanchar las activas y ordenar por Created On, Last Updated o por campos personalizados de los tipos que lista la guía (texto, desplegable, número, monetario, teléfono, fecha). Ese diseño queda en tu navegador. No es un cambio para todo el equipo.</p>
<h2>Lo que esta página no afirma</h2>
<ul>
<li>No afirma cuántas consultas se pierden sin un CRM.</li>
<li>No afirma que Mercado Pago cierre la venta de un inmueble dentro de este flujo. Cobrar es otra guía y otro tema.</li>
<li>No hay un caso real. Si no hay nombre verificable, no hay caso.</li>
</ul>
<h2>Preguntas frecuentes</h2>
<h3>¿HighLevel trae etapas inmobiliarias ya traducidas?</h3>
<p>No en las guías citadas. El ejemplo en inglés es New Lead, Booked Call o Closed. Las etapas en español las escribes tú.</p>
<h3>¿El primer WhatsApp de una consulta de formulario puede ser texto libre?</h3>
<p>Solo si el contacto ya está dentro de la ventana de 24 horas. Si no, la guía pide plantilla aprobada.</p>
<h2>Fuentes</h2>
<ul>
{_src("https://help.gohighlevel.com/support/solutions/articles/155000005062-getting-started-setup-pipelines-and-opportunities", "Getting Started - Setup Pipelines and Opportunities", "consultado el 22 de septiembre de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000001982-understanding-pipelines", "Understanding Pipelines", "consultado el 22 de septiembre de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000007528-use-kanban-view-in-opportunities", "Use Kanban View in Opportunities", "el 2 de abril de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000003531-workflow-action-whatsapp", "Workflow Action - WhatsApp", "el 8 de abril de 2025")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000007938-error-131042-business-eligibility-payment-issue", "Error 131042", "el 30 de junio de 2026")}
{_src("https://help.gohighlevel.com/support/solutions/articles/155000001980-how-to-set-up-whatsapp-for-a-sub-account", "How to Set Up WhatsApp for a Sub-Account", "el 16 de septiembre de 2026")}
</ul>
{C}
""",
)

MORE["ai-help-gohighlevel-workflows-construccion-rapida"] = (
    "Workflow AI Builder de HighLevel arma el flujo desde un prompt. El promedio publicado es bajo 30 segundos. La guía no publica un factor de 3x. Revísalo antes.",
    f"""<h2>Respuesta rápida</h2>
<p>La función que esta página llamaba AI Help es el <strong>Workflow AI Builder</strong> de la guía modificada el 28 de agosto de 2026. Escribes qué quieres automatizar y el builder arma disparadores y acciones para que los revises. No es el Conversation AI Flow Builder, que diseña la conversación de un bot. Ese otro lienzo está en <a href="/blog/maestro-ai-flow-builder-gohighlevel-setup-completo/">la guía del AI Flow Builder</a>.</p>
<p>El título histórico dice "3x más rápido". La guía no publica ese multiplicador. Lo que sí publica es un promedio de generación por debajo de 30 segundos, frente a unos 60 segundos antes, sin presentar eso como un cambio de calidad.</p>
<h2>Dónde se abre</h2>
<ol>
<li><strong>Listado de flujos.</strong> Automation &gt; Workflows y el botón <strong>Build using AI</strong>. Se abre un cuadro para el prompt.</li>
<li><strong>Dentro de un flujo nuevo.</strong> Create Workflow &gt; Start from Scratch. Hay una caja de prompt y puedes dictar por voz.</li>
<li><strong>El chatbot del builder.</strong> Dentro del editor, el asistente también construye el flujo.</li>
</ol>
<h2>Paso 1: Escribir el prompt</h2>
<p>Puedes redactar el tuyo o usar una plantilla de prompt de la interfaz. Ejemplos literales de la guía, en inglés:</p>
<ul>
<li>Send a welcome email series when someone fills out my contact form.</li>
<li>Create a birthday reminder workflow that sends SMS greetings.</li>
<li>Notify my team on Slack when a high-value opportunity is created.</li>
<li>Follow up with webinar attendees 24 hours after the event.</li>
</ul>
<p>Puedes pedir en el mismo texto el nombre del flujo y ajustes: permitir reentrada, varias oportunidades, parar al responder, zona horaria y horario, remitente, marcar conversaciones como leídas. Un ejemplo de la guía combina varios: renombrar, cambiar el email remitente, limitar los mensajes a lunes a viernes de 9 a 18 y dejar la reentrada apagada.</p>
<h2>Paso 2: Generar y leer la lista de pendientes</h2>
<p>Pulsa Build Workflow o Send, según desde dónde entraste. La guía dice que la generación suele terminar en menos de 30 segundos de promedio. Si tarda más, recomienda simplificar el prompt. Si el autosave está activo, el flujo se guarda al crearse y en cada edición hecha por la IA.</p>
<p>Antes de publicar, abre la lista To-Do. La guía dice que ahí faltan decisiones humanas: credenciales, cuenta, pipeline, campos obligatorios. Elegir un ítem te lleva a la acción. Un flujo generado no está siempre listo para publicarse.</p>
<h2>Paso 3: Corregir con alcance</h2>
<p>En el chat describes el cambio y el alcance: todos los pasos que coincidan, un número de pasos, o acciones y disparadores concretos. La guía dice que el builder toca solo ese alcance.</p>
<p>La versión 3, en el mismo artículo, agrega progreso en vivo, varios cambios en un solo pedido, memoria de la sesión ("hazlo de 48 horas"), confirmación antes de empezar de cero si el lienzo ya tiene un flujo, y edición masiva de textos, etapas de pipeline o remitente.</p>
<p><strong>Point and Edit</strong> selecciona acciones en el lienzo: una, varias, o un rango con Shift. El cambio se aplica solo a lo seleccionado. La guía lo recomienda cuando hay más de 10 acciones o varias ramas.</p>
<p><strong>Chat Mode</strong> planea sin construir. Lo activas, acuerdas disparadores y tiempos, lo desactivas y recién ahí pides que lo arme.</p>
<p>Si faltan datos, el Clarifying Agent hace hasta tres preguntas (disparador, canal, tiempo, o un canal no soportado). Puedes elegir una opción, escribir la tuya o saltar la pregunta.</p>
<h2>Lo que la IA no hace</h2>
<p>La sección Beta Limitations dice tres cosas: hay que revisar disparadores y acciones a mano, algunas configuraciones complejas se ajustan a mano, y la IA no prueba el flujo. La prueba la haces tú antes de publicar.</p>
<p>Para apagarlo: en la agencia, Settings &gt; Labs, desactiva Workflow AI Builder. En la subcuenta, Automations &gt; Global Workflow Settings &gt; Workflow AI, apaga AI Builder.</p>
<h2>Preguntas frecuentes</h2>
<h3>¿El flujo generado se puede publicar tal cual?</h3>
<p>No siempre. La guía manda revisar la lista de pendientes y completar campos antes de publicar.</p>
<h3>¿Dónde está el 3x del título?</h3>
<p>No está en la guía del 28 de agosto de 2026. El dato de velocidad que el artículo sí da es el promedio de generación, por debajo de 30 segundos.</p>
<h2>Fuentes</h2>
<ul>
{_src("https://help.gohighlevel.com/support/solutions/articles/155000006100-workflow-ai-builder", "Workflow AI Builder", "el 28 de agosto de 2026")}
</ul>
{C}
""",
)
