# Guía para presentar Mining Star ERP al instructor

Duración sugerida: **20 minutos** (15 de demostración + 5 de preguntas).
Se presenta desde **el navegador** (la aplicación) y **Visual Studio Code** (el código, la terminal y las pruebas).

---

## 1. Qué se va a presentar

Producto mínimo viable (MVP) de **Mining Star ERP**, el sistema de gestión de *Mining Star Services and Products* (razón social *Ortega Espinosa y Compañía S.A.S.*), cantera de mármol y caliza en Payandé, San Luis (Tolima).

| Bloque | Qué mostrar | Dónde |
|---|---|---|
| Seguridad | Login con token, cargos, bitácora, bloqueo por intentos | Navegador + `core/permisos.py` |
| Dashboard | Indicadores y gráficas que cambian según el cargo | `/` |
| Operación | Producción por turno (HU-001), inventario | `/produccion`, `/inventario` |
| Comercial | CRM, tienda/brochure, carrito, pago con Stripe | `/crm`, `/tienda` |
| Gestión | Normativa minera y ambiental, mejora continua PHVA | `/normativa`, `/mejora` |
| Empresa | Misión, visión, valores, cultura, organigrama, Porter, valor, stakeholders, Canvas, EDT | `/empresa` |
| Calidad | 128 pruebas automatizadas, respaldo, pull request | Terminal de VS Code y GitHub |

## 2. Stack que debe saber nombrar

**Backend:** Python 3.12 · Django 6 · Django REST Framework · JWT (simplejwt) · PostgreSQL · Stripe SDK · drf-spectacular (Swagger).
**Frontend:** React 19 · React Router 7 · Recharts · Vite 8.
**Calidad y versiones:** pruebas de Django y Vitest · Ruff y Oxlint · Git y GitHub con ramas y pull requests.
Detalle en [01-stack-y-arquitectura.md](01-stack-y-arquitectura.md).

---

## 3. Preparación (el día anterior, una sola vez)

Abra la carpeta `Mining Star` en VS Code (**Archivo → Abrir carpeta**) y una terminal (**Terminal → Nueva terminal**, PowerShell).

```powershell
# 1. Traer la rama con todas las mejoras (si aún no está en ella)
git status

# 2. Instalar dependencias, crear respaldo y cargar los datos de demostración.
#    Elija una clave segura: será la de los 7 usuarios de prueba.
scripts\preparar_demo.bat "Demo*Mina2026"

# 3. Instalar el front-end
cd frontend
npm install
cd ..

# 4. Verificar que todo está en verde
python manage.py test core
cd frontend; npm test; cd ..
```

Usuarios creados (todos con la clave que eligió):

| Usuario | Cargo | Para mostrar |
|---|---|---|
| `admin.ms` | Administrador | Todo, incluida Seguridad y respaldos |
| `gerente` | Gerente | Visión completa en modo consulta |
| `comercial` | Comercial | CRM, tienda y carrito |
| `supervisor` | Supervisor | Producción, normativa y mejora |
| `contador` | Contador | Ventas (solo anular) y proveedores |
| `operario` | Operario | Solo producción y mejora: el mejor ejemplo de acceso restringido |
| `auxiliar` | Auxiliar | Inventario |

> Si quiere mostrar el pago real de Stripe en modo prueba, siga [04-pagos-stripe.md](04-pagos-stripe.md). Si no, el carrito funciona en **modo simulado** sin configurar nada.

## 4. Antes de entrar a la sesión (5 minutos antes)

Abra **dos terminales** en VS Code (botón **+** de la terminal) y deje cada una corriendo:

```powershell
# Terminal 1 — API Django
scripts\iniciar_backend.bat
```
```powershell
# Terminal 2 — React
scripts\iniciar_frontend.bat
```

En el navegador deje abiertas tres pestañas:
1. <http://localhost:5173> — la aplicación
2. <http://127.0.0.1:8000/api/docs/> — documentación Swagger de la API
3. <https://github.com/jfor26/mining-star> — el repositorio

Organice la pantalla: **VS Code a la izquierda, navegador a la derecha** (tecla Windows + flechas).

---

## 5. Guion de la demostración

### Paso 1 — Presentación del problema (1 min) · *Navegador: pantalla de login*
> "Mining Star es una cantera de mármol y caliza en Payandé, Tolima. Antes llevaba la producción y las ventas en papel y Excel, sin control de quién accede a qué ni de los vencimientos ante la ANM y CORTOLIMA. El MVP integra operación, ventas, pagos en línea y cumplimiento en una sola plataforma web."

Señale el logo de Mining Star y el sello del SENA.

### Paso 2 — Login y token de acceso (2 min) · *Navegador + VS Code*
1. Ingrese con `operario`.
2. Muestre la barra superior: **"Token activo · vence HH:MM"** y la insignia **Operario**.
3. Muestre que el menú solo tiene Dashboard, La empresa, Producción y Mejora continua.
4. Escriba en la barra de direcciones `localhost:5173/clientes` → aparece **Acceso restringido**.
> "Cada vez que un empleado entra se emite un token JWT nuevo de 30 minutos. El menú se arma con los permisos de su cargo, pero la protección real está en el servidor: aunque escriba la URL, la API responde 403."

En **VS Code** abra `core/permisos.py` y muestre `MATRIZ_DE_ACCESO`:
> "Esta es la matriz cargo × módulo. La misma regla la aplican la API, las vistas web y el menú de React."

### Paso 3 — Dashboard según el cargo (2 min)
1. Con `operario`, el dashboard solo muestra producción y mejora continua.
2. Cierre sesión y entre con `gerente`: aparecen ventas por mes, productos más vendidos, embudo CRM, inventario valorizado, normativa y PHVA.
3. Pulse **Ver tabla** en una gráfica.
> "El servidor solo envía los datos que el cargo puede ver. Cada gráfica tiene vista de tabla para accesibilidad; los colores se eligieron para que los distingan personas con daltonismo."

### Paso 4 — Producción de la mina, HU-001 (1 min)
Con `supervisor` (o `operario`): **Producción** → registre un turno (Caliza, 35 t) → aparece en la tabla y en el stock de materia prima.
> "Es la historia de usuario HU-001. No se permite registrar dos veces el mismo material en el mismo turno ni fechas futuras."

### Paso 5 — CRM (1,5 min)
Con `comercial`: **CRM** → embudo por etapas → mueva una oportunidad con **→** → pestaña **Interacciones** → registre una llamada.
> "El CRM calcula el valor ponderado según la probabilidad de cada etapa."

### Paso 6 — Tienda, brochure, carrito y pago con Stripe (3 min) · *el momento más visual*
1. **Tienda y brochure** → filtre por categoría → **Imprimir brochure** (muestre la vista previa de impresión y cierre).
2. **Agregar al carrito** dos productos → **🛒** → elija el cliente → **Confirmar pedido** → **Pagar**.
3. En modo simulado: **Aprobar pago** → "Pago aprobado, se registró la venta V-00xx".
4. Vaya a **Ventas**: la venta está en el historial; en **Inventario** el stock bajó.
> "Crear el pedido no descuenta inventario; el descuento ocurre al confirmarse el pago, dentro de una transacción. Si Stripe avisa dos veces, la venta se crea una sola vez. Con llaves de prueba de Stripe, el cliente paga en la página segura de Stripe con la tarjeta 4242 4242 4242 4242; los datos de la tarjeta nunca pasan por nuestro servidor."

En **VS Code** abra `core/servicios.py` → función `confirmar_pago`.

### Paso 7 — Normativa minera y ambiental y mejora continua (2 min)
1. **Normativa**: filtre por *Ambiental*; muestre el ICA **vencido** y la declaración de regalías que vence en días. Cambie un estado a *Cumplido*.
> "Es el repositorio de lo que exigen la ANM, CORTOLIMA, MinTrabajo, la DIAN y la SIC, con alertas de vencimiento."
2. **Mejora continua**: muestre el ciclo PHVA y pase una acción a la siguiente fase.
> "Cualquier empleado puede proponer una mejora. No se puede cerrar una acción sin registrar cómo se verificó su eficacia."

### Paso 8 — Seguridad y respaldo (1,5 min) · con `admin.ms`
1. **Seguridad → Bitácora de accesos**: ingresos, intentos fallidos e identificador del token.
2. **Accesibilidad por cargo**: la matriz completa.
3. **Usuarios y cargos**: cambie el cargo de un usuario.
4. **Respaldos (backup) → Crear respaldo ahora**.
> "Tras 5 intentos fallidos el usuario queda bloqueado 15 minutos. Al cerrar sesión, el token de refresco pasa a una lista negra en el servidor."

Demostración opcional del bloqueo: cierre sesión e intente 5 veces con clave errada; en el sexto intento aparece "Demasiados intentos fallidos".

### Paso 9 — La empresa (1,5 min)
**La empresa** → recorra rápido las pestañas: misión y visión, cultura, **estructura** (organigrama con el cargo de cada uno en el sistema), **5 fuerzas de Porter**, valor y diferencial, stakeholders, **modelo de negocio (Canvas)** y **EDT**.
> "El riesgo principal es el poder de los compradores; la ventaja principal es tener un título vigente cerca del consumo."

### Paso 10 — Calidad: pruebas, API y pull request (2 min) · *VS Code y GitHub*
En la terminal (con los servidores corriendo en las otras dos):
```powershell
python manage.py test core.tests_mvp
```
> "Son 112 pruebas del backend y 16 del frontend. Prueban sobre todo lo que el sistema debe rechazar."

Pestaña de **Swagger** (`/api/docs/`): muestre los grupos Autenticación, CRM, Tienda y pagos, Seguridad.
Pestaña de **GitHub**: la rama `feature/mvp-presentacion`, sus commits y el **pull request** hacia `main`.

### Cierre (30 s)
> "El MVP cubre operación, ventas, pagos, CRM, cumplimiento y mejora continua con seguridad por cargo. Lo siguiente sería desplegarlo con PostgreSQL y HTTPS, agregar doble factor para gerencia y conectar la app móvil a la misma API."

---

## 6. Preguntas probables y cómo responderlas

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué JWT y no sesión? | La API la consumen React y a futuro la app móvil, donde no hay cookie de sesión. |
| ¿Qué pasa si roban el token? | El de acceso dura 30 min; el de refresco rota en cada uso y se invalida al cerrar sesión. |
| ¿Cómo se sincroniza el frontend con el backend? | React solo habla con la API REST (`/api/v1`); en desarrollo Vite reenvía `/api` a Django. Toda escritura queda en la base de datos y las pantallas leen de ella. |
| ¿Por qué PostgreSQL? | Es el mismo motor en desarrollo, pruebas y producción (Railway), soporta varios usuarios a la vez y evita errores que solo aparecen al publicar. Empezamos con SQLite en el MVP y migramos (docs/12-postgresql.md). |
| ¿Cómo evitan vender lo que no hay? | Descuento condicional en una sola instrucción SQL dentro de una transacción. |
| ¿Stripe cobra de verdad? | No. Se usa modo prueba o modo simulado; nunca llaves reales en desarrollo. |
| ¿De dónde salen Porter, Canvas y EDT? | Del estudio de mercado y del plan de reactivación del título 15834, resumidos sin datos confidenciales. |
| ¿Las normas son exactas? | Son una referencia para el proyecto formativo; las fechas son de demostración y la lista debe validarla el asesor jurídico minero. |
| ¿Qué metodología usaron? | Desarrollo incremental por historias de usuario, con ramas por funcionalidad y pull requests. |

## 7. Plan B

| Si falla… | Hacer |
|---|---|
| `npm run dev` | Mostrar la interfaz Django en <http://127.0.0.1:8000> (también aplica los permisos por cargo). |
| La base de datos | `python manage.py restaurar_bd respaldos\<último archivo>.json` |
| Olvidó la clave demo | `python manage.py cargar_demo --clave "OtraClave*2026"` (no duplica datos). |
| Un usuario quedó bloqueado | Esperar 15 minutos o entrar con otro usuario. |
| No hay internet | Todo funciona en local; solo Stripe real y GitHub necesitan conexión. |
| Todo | Mostrar las capturas de `docs/capturas/`. |
