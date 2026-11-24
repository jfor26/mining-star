# Seguridad

## 1. Acceso por cargo (accesibilidad de cada empleado)

Cada usuario pertenece a un grupo con el nombre de su cargo. Lo que cada cargo puede hacer está en **una sola matriz**, `core/permisos.py`, que aplican la API, las vistas web y el menú de React.

| Módulo | Administrador | Gerente | Supervisor | Comercial | Contador | Operario | Auxiliar |
|---|---|---|---|---|---|---|---|
| Panel | VCEX | V | V | V | V | V | V |
| Clientes | VCEX | V | — | VCE | V | — | V |
| CRM | VCEX | VCEX | — | VCEX | — | — | — |
| Proveedores | VCEX | V | — | — | VCE | — | V |
| Productos e inventario | VCEX | V | V | V | V | — | VCE |
| Empleados | VCEX | V | V | — | — | — | — |
| Ventas | VCEX | V | — | VC | VE | — | — |
| Tienda y pagos | VCEX | V | — | VC | V | — | V |
| Producción | VCEX | V | VCE | — | — | VC | — |
| Normativa | VCEX | VCE | VCE | — | V | — | — |
| Mejora continua | VCEX | VCE | VCE | VC | VC | VC | VC |
| Seguridad | VCEX | V | — | — | — | — | — |
| Atención al cliente (PQRS) (v1.1) | VCEX | VE | — | VE | — | — | — |

V = ver, C = crear, E = editar, X = eliminar. Se consulta también en el aplicativo: *Seguridad → Accesibilidad por cargo*.

- Un usuario **sin cargo** no puede usar ningún módulo.
- El **registro de usuarios ya no es público**: antes cualquiera podía crearse una cuenta y leer datos personales. Ahora solo el Administrador crea usuarios y les asigna cargo.
- Nadie puede cambiar su propio cargo ni desactivar su propia cuenta.
- El menú oculta lo que el cargo no puede usar, pero **la protección real está en el servidor**: aunque alguien escriba la URL o llame a la API, recibe 403.

### Rol Cliente y portal (versión 1.1)

- Los clientes con acceso al portal pertenecen al grupo **Cliente**, que no está en la matriz: no ven ningún módulo interno (la API responde 403) y solo usan `/api/v1/portal/`.
- El portal filtra todo por el cliente vinculado al usuario de la sesión, **nunca por un id que llegue en la petición**. Un cliente que cambie el número de una compra en la URL recibe 404 (prueba `test_no_puede_descargar_el_comprobante_de_otro_cliente`).
- El acceso al portal lo dan o quitan los cargos que pueden editar clientes (`POST/DELETE /clientes/{id}/acceso-portal/`); la clave debe cumplir las reglas de contraseñas seguras.
- La interfaz separa los dos mundos: un cliente que escribe una ruta interna es enviado al portal, y un empleado que abre `/portal` vuelve al sistema interno.

### Formularios públicos (versión 1.1)

- `POST /api/v1/publico/pqrs/` y `/publico/contacto/` no piden sesión, pero están **limitados por IP** (`LIMITE_FORMULARIOS_PUBLICOS`, por defecto 20 por hora) para frenar el spam; al pasarse responden 429.
- Radicar una PQRS exige la **autorización de tratamiento de datos** (Ley 1581 de 2012).
- La consulta de un radicado exige también el **documento** con que se radicó, para que nadie lea la respuesta de otra persona.

## 2. Token de acceso por ingreso

```mermaid
sequenceDiagram
  participant E as Empleado (React)
  participant A as API Django
  E->>A: POST /auth/login/ (usuario, clave)
  A->>A: ¿bloqueado por intentos? ¿clave correcta?
  A-->>E: access (30 min) + refresh (8 h) + cargo y permisos
  A->>A: RegistroAcceso: ingreso, IP, navegador, jti del token
  E->>A: GET /clientes/  Authorization: Bearer access
  A-->>E: 200 o 403 según el cargo
  E->>A: POST /auth/refrescar/ (cuando vence el access)
  A-->>E: access nuevo + refresh nuevo (el anterior queda en lista negra)
  E->>A: POST /auth/logout/ (refresh)
  A->>A: refresh a la lista negra + RegistroAcceso: salida
```

- Cada ingreso emite un **JWT nuevo**; su identificador `jti` queda en la bitácora (*Seguridad → Bitácora de accesos*). Nunca se guarda el token completo.
- **Rotación**: cada renovación entrega un refresh nuevo y bloquea el anterior. Un token robado deja de servir.
- **Cierre de sesión real**: el refresh pasa a la lista negra del servidor.
- El token se guarda en `sessionStorage`, que se borra al cerrar la pestaña.
- La barra superior muestra hasta qué hora es válido el token actual.

## 3. Bloqueo por fuerza bruta

Tras **5 intentos fallidos** para un usuario (o 20 desde una IP) en 15 minutos, el login responde **429** aunque la clave sea correcta. Configurable en `.env` (`LOGIN_INTENTOS_MAXIMOS`). El mensaje de error es igual si el usuario no existe o si la clave está mal, para no revelar qué usuarios existen.

## 4. Otras medidas

| Medida | Dónde |
|---|---|
| Secretos fuera del código (`.env`, excluido de Git) | `config/settings.py` |
| Validación de contraseñas de Django (longitud, comunes, numéricas) | Registro y `cargar_demo` |
| HTTPS, HSTS, cookies seguras cuando `DEBUG=False` | `settings.py` |
| `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy` | `settings.py` |
| Bitácora de accesos de solo lectura en el admin | `core/admin.py` |
| Webhook de Stripe con verificación de firma | `core/pagos.py` |
| Los datos de tarjeta nunca pasan por el servidor (Stripe Checkout) | `core/pagos.py` |
| Ley 1581 de 2012: datos personales solo para cargos autorizados | Matriz de acceso |
| Respaldos excluidos de Git (contienen datos personales) | `.gitignore` |

## 5. Pendientes antes de producción

- Pasar a PostgreSQL y servir por HTTPS (Gunicorn + Nginx o un PaaS).
- Doble factor de autenticación para Administrador y Gerente.
- Registro de auditoría de cambios en datos (quién editó qué), por ejemplo con `django-simple-history`.
- Política de tratamiento de datos publicada y firmada por los titulares.
