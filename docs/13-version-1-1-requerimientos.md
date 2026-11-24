# Versión 1.1 — Requerimientos, casos de uso y cambios

Versión construida después de la guía 10, a partir de las sugerencias del instructor en la presentación del 8 de octubre de 2026 y de las decisiones del equipo (23 de noviembre de 2026). Rama de trabajo: `mejoras`. La versión entregada en la guía 10 quedó congelada en la rama `version-guia10`.

**Equipo:** Diego Navarro, Juan Fernando Ortega Rojas, Juan Pablo Camargo Aricapa y Kaleth Fabián Poveda Aza.

## 1. Origen de cada cambio

| Sugerencia o decisión | Dónde se atendió |
|---|---|
| Botones para volver atrás | RF-21 |
| Eliminar personal, buscar, ordenar alfabéticamente y por tiempo laborado, filtrar por cargo | RF-22 a RF-24 |
| Tema claro, oscuro y automático | RF-25 |
| Recordatorio del tiempo restante de la sesión | Ya existía (barra superior: «Token activo · vence …») |
| Experiencia distinta para usuario y administrador; interfaz limitada para clientes | RF-27 a RF-30 (portal de clientes) y matriz de permisos |
| Chatbot | RF-36 |
| Ícono de notificaciones | RF-26 |
| Base de datos en PostgreSQL | RNF-10 |
| CRM, redes sociales, contacto y PQRS | RF-31 a RF-35 |
| Nombre comercial sin datos personales | RNF-14 |
| Pruebas en vivo en la presentación | `docs/15-guion-pruebas-en-vivo.md` |

## 2. Requerimientos funcionales nuevos

| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-21 | El sistema muestra un botón «Volver» en todas las pantallas internas excepto el inicio; si no hay pantalla anterior, lleva al inicio. | Media |
| RF-22 | El usuario con permiso puede registrar, editar y eliminar empleados; antes de eliminar, el sistema pide confirmación. | Alta |
| RF-23 | El listado de empleados permite buscar por documento, nombre o correo, y ordenar por nombre (A–Z, Z–A) o por tiempo laborado. | Alta |
| RF-24 | El listado de empleados permite filtrar por cargo y muestra cuántos empleados hay en cada uno. | Media |
| RF-25 | El usuario puede elegir tema claro, oscuro o automático (según el dispositivo); la elección se recuerda. | Baja |
| RF-26 | La campana de notificaciones avisa de productos en stock mínimo, requisitos normativos vencidos o por vencer (30 días), pedidos pagados, oportunidades con 7 días o más sin contacto, PQRS sin responder y mensajes de contacto sin atender. Cada cargo ve solo los de sus módulos; los avisos se marcan como leídos. | Alta |
| RF-27 | El inicio de sesión ofrece dos accesos: «Personal de la empresa» y «Soy cliente»; cada rol llega a su propia interfaz. | Alta |
| RF-28 | Un usuario con permiso de editar clientes puede dar, cambiar o quitar el acceso al portal de un cliente (usuario = NIT). | Alta |
| RF-29 | En el portal, el cliente consulta sus compras y descarga el comprobante en PDF de cada una. | Alta |
| RF-30 | En el portal, el cliente solicita cotizaciones de uno o varios productos; el sistema crea una oportunidad en el CRM (etapa Prospecto, origen Portal) con el valor estimado y una interacción, y el cliente ve el estado de sus solicitudes. | Alta |
| RF-31 | La ficha del cliente reúne sus datos, compras, oportunidades, días desde el último contacto y la línea de tiempo de interacciones. | Alta |
| RF-32 | El sitio público presenta productos, misión, visión, valores, cumplimiento, contacto, preguntas frecuentes y redes sociales. | Media |
| RF-33 | Cualquier persona puede radicar una PQRS (tipo, nombre, documento, correo, detalle y autorización de datos) y recibe un radicado PQRS-AAAA-NNNN. | Alta |
| RF-34 | Con el radicado y el documento, la persona consulta el estado y la respuesta de su PQRS. | Alta |
| RF-35 | El personal autorizado lista, responde y cierra las PQRS y atiende los mensajes de contacto. | Alta |
| RF-36 | El asistente responde preguntas sobre stock, stock mínimo, vencimientos, ventas, producción, clientes, CRM y PQRS con datos del sistema, indica la fuente y respeta los permisos del cargo. | Media |
| RF-37 | La calculadora del sitio estima los m³ de recebo para una vía a partir de largo, ancho y espesor. | Baja |

## 3. Requerimientos no funcionales nuevos o modificados

| ID | Requerimiento |
|---|---|
| RNF-10 | PostgreSQL 16 en desarrollo, pruebas y producción; las pruebas automáticas corren sobre PostgreSQL. |
| RNF-11 | El portal solo entrega datos del cliente de la sesión (aislamiento por usuario, verificado con pruebas). |
| RNF-12 | Los formularios públicos se limitan a 20 envíos por hora por IP (respuesta 429). |
| RNF-13 | Radicar una PQRS exige la autorización de tratamiento de datos personales (Ley 1581 de 2012). |
| RNF-14 | Nombre comercial «Mining Star Services and Products ERP» y razón social «Industrias Mineras S.A.S.»; los datos de ejemplo no usan nombres reales del equipo. |
| RNF-15 | Interfaz usable en celular (pantallas que se reorganizan) y con contraste suficiente en los temas claro y oscuro. |
| RNF-16 | El asistente funciona sin servicios externos ni costo; su motor está aislado para reemplazarlo por un modelo de IA. |
| RNF-17 | Los respaldos se generan en JSON (portable) y, si hay `pg_dump`, en formato nativo de PostgreSQL; la restauración es transaccional. |

## 4. Casos de uso nuevos

### CU-10 Solicitar cotización desde el portal
- **Actor:** Cliente con acceso al portal.
- **Precondición:** el cliente inició sesión con su NIT.
- **Flujo principal:** 1) el cliente elige productos y cantidades (o pulsa «Cotizar» en el catálogo); 2) opcionalmente indica fecha de entrega y observaciones; 3) envía; 4) el sistema valida, calcula el valor estimado a precios vigentes, crea la oportunidad (Prospecto, origen Portal) y la interacción; 5) muestra «Solicitud enviada» y la solicitud en «Mis solicitudes» con estado «Recibida».
- **Flujos alternos:** sin productos o cantidad cero → mensaje y no se envía; fecha pasada → error en el campo.
- **Postcondición:** el comercial ve la oportunidad en el CRM y en la ficha del cliente.

### CU-11 Radicar y consultar una PQRS
- **Actor:** ciudadano o cliente (sin sesión).
- **Flujo principal:** 1) elige el tipo; 2) diligencia nombre, documento, correo y detalle; 3) autoriza el tratamiento de datos; 4) radica; 5) el sistema asigna el radicado y lo muestra; 6) luego consulta con radicado y documento y ve estado y respuesta.
- **Flujos alternos:** sin autorización → no se radica; documento distinto al consultar → «No encontramos una PQRS…»; más de 20 envíos por hora → 429.

### CU-12 Responder una PQRS
- **Actor:** Administrador, Gerente o Comercial.
- **Flujo principal:** 1) abre «Atención al cliente»; 2) elige una PQRS pendiente; 3) escribe la respuesta y cambia el estado a «Respondida»; 4) guarda.
- **Flujo alterno:** marcar «Respondida» sin texto → error «Escriba la respuesta…».

### CU-13 Consultar al asistente
- **Actor:** cualquier cargo interno.
- **Flujo principal:** 1) abre el asistente; 2) escribe o elige una pregunta sugerida; 3) el sistema identifica la intención, verifica el permiso del cargo y responde con datos y fuente.
- **Flujos alternos:** cargo sin permiso → «Su cargo no tiene acceso a esa información»; pregunta no reconocida → explica qué temas maneja.

### CU-14 Atender avisos de la campana
- **Actor:** cualquier cargo interno.
- **Flujo principal:** 1) la campana muestra el número de avisos sin leer; 2) el usuario la abre y filtra por tipo; 3) al hacer clic en un aviso, el sistema lo marca como leído y abre el módulo correspondiente.

## 5. API nueva

| Método y ruta | Uso |
|---|---|
| `GET/POST /api/v1/notificaciones/` | Avisos de la campana y marcar como leídos |
| `POST/DELETE /api/v1/clientes/{id}/acceso-portal/` | Dar o quitar el acceso al portal |
| `GET /api/v1/clientes/{id}/ficha/` | Ficha del cliente |
| `GET /api/v1/portal/resumen/`, `/portal/catalogo/` | Datos del cliente y catálogo |
| `POST /api/v1/portal/cotizaciones/` | Solicitud de cotización → CRM |
| `GET /api/v1/portal/compras/{id}/comprobante/` | Comprobante PDF |
| `POST /api/v1/publico/pqrs/`, `GET /publico/pqrs/{radicado}/?documento=` | Radicar y consultar PQRS |
| `POST /api/v1/publico/contacto/` | Mensaje de contacto |
| `GET/PATCH /api/v1/pqrs/`, `/api/v1/contactos/` | Gestión interna |
| `POST /api/v1/asistente/` | Pregunta al asistente |

La documentación interactiva completa está en `/api/docs/`.

## 6. Pruebas

| Conjunto | Cantidad |
|---|---|
| Backend (Django, sobre PostgreSQL) | 148 pruebas |
| Interfaz (Vitest + Testing Library) | 37 pruebas |

Archivos nuevos: `core/tests_notificaciones.py`, `core/tests_portal.py`, `core/tests_publico.py`, `core/tests_asistente.py` y, en el frontend, `Empleados`, `Barra`, `Campana`, `Portal`, `Sitio` y `Asistente`.

## 7. Datos pendientes de la empresa

Se completan en `frontend/src/datos/sitio.js` sin tocar el código: dirección, teléfono, correo, horario, número de WhatsApp Business, enlace del mapa, redes sociales, número de la licencia ambiental, respuestas de las preguntas frecuentes y enlace a la política de tratamiento de datos.
