# Guion de pruebas en vivo para la presentación

El instructor pidió hacer pruebas en vivo. Este guion dura unos 15 minutos y se ejecuta sobre el sistema publicado (o en local con `cargar_demo`). Cada prueba dice qué hacer, qué debe pasar y quién del equipo la presenta (ajústenlo entre ustedes).

**Antes de empezar**
- Datos de demostración cargados (`python manage.py cargar_demo --clave "<clave demo>"`).
- Dos ventanas del navegador: una normal (personal) y una de incógnito (cliente o visitante). La sesión se guarda por pestaña.
- La clave demo la escribe el presentador; no se muestra en pantalla.

| N.º | Prueba | Pasos | Resultado esperado | Presenta |
|---|---|---|---|---|
| PV-01 | Sitio público | Abrir la dirección del sistema sin iniciar sesión. | Se ve el sitio de la empresa (productos, nosotros, contacto, PQRS). | Integrante 1 |
| PV-02 | Calculadora | En «Cumplimiento y calculadora», subir el espesor a 25 cm. | El resultado cambia de ≈ 120 m³ a ≈ 150 m³. | Integrante 1 |
| PV-03 | Radicar PQRS | Radicar una petición con documento `900500001` sin marcar la autorización; luego marcarla y radicar. | Primero rechaza por la autorización de datos; después muestra un radicado `PQRS-AAAA-NNNN`. Anotarlo. | Integrante 1 |
| PV-04 | Credenciales incorrectas | «Acceso personal» → usuario `gerente` con una clave equivocada. | «Usuario o contraseña incorrectos» (no dice cuál de los dos falló). | Integrante 2 |
| PV-05 | Ingreso y token | Ingresar como `gerente`. | Dashboard del Gerente; arriba «Token activo · vence …». | Integrante 2 |
| PV-06 | Campana | Abrir la campana y filtrar por «Normativa»; hacer clic en un aviso. | Lista solo los avisos del cargo; al hacer clic abre Normativa y el contador baja. | Integrante 2 |
| PV-07 | Asistente | Preguntar «¿Qué productos están en stock mínimo?». Luego ingresar como `operario` y preguntar «¿Cuál fue la última venta?». | El gerente recibe la lista con la fuente «Inventario»; el operario recibe «Su cargo no tiene acceso a esa información». | Integrante 2 |
| PV-08 | Empleados | Ingresar como `admin.ms` → Empleados y cargos → ordenar por «Más tiempo laborado» y filtrar «Operario». | Orden por antigüedad y solo operarios. | Integrante 3 |
| PV-09 | Eliminar con historial | Intentar eliminar a Carlos Molina (supervisor con producción). | Pide confirmación y luego explica que tiene registros asociados y sugiere marcarlo Inactivo (409). | Integrante 3 |
| PV-10 | Tema oscuro y Volver | Elegir el tema oscuro, abrir Clientes y pulsar «Volver». | Cambia el tema y regresa a la pantalla anterior. | Integrante 3 |
| PV-11 | Portal del cliente | En incógnito: «Soy cliente» → NIT `900500001` y la clave demo. | Portal con «Mis compras»; no aparece el menú interno. | Integrante 4 |
| PV-12 | Aislamiento | En el portal, escribir en la barra de direcciones `/ventas`. | El sistema devuelve al portal: el cliente no entra al sistema interno. | Integrante 4 |
| PV-13 | Cotización → CRM | En el catálogo pulsar «Cotizar» en Recebo para vías, cantidad 15, enviar. Luego, como `comercial`, abrir Clientes → Constructora Vías del Centro. | En el portal aparece «Recibida»; en la ficha del cliente aparece la oportunidad «desde el portal» y la interacción en la línea de tiempo. | Integrante 4 |
| PV-14 | Responder PQRS | Como `comercial` → Atención al cliente → abrir la PQRS de PV-03 → responder y marcar «Respondida». En el sitio, consultar el radicado con el documento. | El ciudadano ve el estado «Respondida» y el texto de la respuesta. | Integrante 1 |
| PV-15 | API protegida | Abrir `/api/v1/clientes/` sin sesión. | HTTP 401: «Las credenciales de autenticación no se proveyeron». | Integrante 2 |
| PV-16 | Pruebas automáticas | En la terminal: `python manage.py test` y `npm test`. | 148 y 37 pruebas en verde. | Integrante 3 |

**Si algo falla en vivo:** decirlo con tranquilidad, mostrar la prueba automática que cubre ese caso y explicar cómo se corregiría. Un error bien explicado también demuestra dominio del sistema.
