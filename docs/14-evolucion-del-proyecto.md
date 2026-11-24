# Cómo llegamos al resultado: evolución de Mining Star

Línea de tiempo construida con el historial de Git del repositorio `jfor26/mining-star` (`git log --reverse`). Cada fila es un hito que se puede mostrar en GitHub.

| Fecha | Hito | Qué cambió y por qué |
|---|---|---|
| 28/08/2026 | **Punto de partida** | Primer estado del proyecto en Django con plantillas. Se hizo una auditoría completa de seguridad y se corrigieron errores antes de crecer. |
| 20–21/09/2026 | **API REST** | Se expuso el sistema en `/api/v1/` para separar el servidor de la interfaz. Se corrigió que una venta no descontara inventario y que borrar registros con dependencias rompiera datos (ahora responde 409). |
| 21/09/2026 | **Producción de la mina (HU-001)** | Registro de la extracción por turno y material; el stock de materia prima se calcula desde los registros. |
| 25/09/2026 | **Panel con cifras reales** | El tablero dejó de mostrar valores fijos y pasó a calcularlos de la base de datos. |
| 05/10/2026 | **Interfaz en React** | Nueva interfaz (React 19 + Vite) que consume la API con tokens JWT. |
| 06/10/2026 | **MVP completo** | CRM, tienda con carrito y pagos Stripe (modo simulado), normativa minera y ambiental, mejora continua (PHVA), permisos por cargo, token por ingreso con bitácora, bloqueo por fuerza bruta, respaldos, dashboard con gráficas y 38 pruebas nuevas. |
| 08/10/2026 | **Presentación al instructor** | Sugerencias: volver atrás, gestionar empleados (eliminar, buscar, ordenar, filtrar por cargo), tema claro/oscuro, interfaz distinta para clientes, revisar lo del «blockchain». |
| 16/11/2026 | **Guías 7, 8 y 9** | Evidencias de construcción, API y pruebas (plan, casos y reporte de pruebas ejecutadas). |
| 23/11/2026 | **Despliegue en Railway (guía 10)** | Gunicorn, WhiteNoise, PostgreSQL administrado y CORS. Sistema publicado y probado con 13 casos funcionales. La versión entregada quedó congelada en la rama `version-guia10`. |
| 23/11/2026 | **Versión 1.1 (rama `mejoras`)** | Atención de las sugerencias: módulo Empleados y cargos, botón Volver, tema claro/oscuro/automático, PostgreSQL como única base de datos, nombre comercial nuevo, campana de notificaciones, portal de clientes con cotizaciones conectadas al CRM, ficha del cliente, sitio público con contacto y PQRS, y asistente. 148 pruebas de backend y 37 de interfaz. |

## Decisiones que vale la pena explicar

| Decisión | Alternativa descartada | Razón |
|---|---|---|
| API REST + React | Seguir solo con plantillas de Django | Separa responsabilidades y permite el portal y futuras apps móviles. |
| Matriz de permisos por cargo en un solo archivo | Permisos por modelo de Django | Más fácil de leer, auditar y explicar: una fila por cargo, una columna por módulo. |
| PostgreSQL en todos los ambientes | SQLite en desarrollo y PostgreSQL en producción | Evita errores que solo aparecen al publicar y soporta varios usuarios a la vez. |
| Railway para la demostración | Microsoft Azure | Despliegue directo desde GitHub en minutos; Azure queda como opción para producción. |
| Avisos calculados, no guardados | Guardar cada notificación en una tabla | Nunca quedan desactualizados; solo se guarda qué leyó cada usuario. |
| Asistente por reglas | Conectar un modelo de IA de pago | Sin costo y con datos exactos; el motor está aislado para cambiarlo después. |
| «Token JWT con bitácora» | Llamarlo «blockchain» | Es una credencial firmada que vence; blockchain es un registro distribuido, otra tecnología. |

## Cómo mostrarlo en la presentación

1. En GitHub, abrir **Insights → Network** o la lista de commits de la rama `mejoras` para ver el avance en el tiempo.
2. Comparar las ramas `version-guia10` y `mejoras` (**Compare**) para mostrar exactamente qué cambió en la versión 1.1.
3. Mostrar el lienzo de diseño (propuesta v1.1) y luego la pantalla real: así se ve que el diseño se aprobó antes de programar.
4. Ejecutar en vivo el guion de `docs/15-guion-pruebas-en-vivo.md`.
