# Mining Star ERP

> 🇺🇸 **English overview** · 🇨🇴 Documentación en español más abajo.

## English overview

**Mining Star ERP** is a full-stack management system for a marble and limestone quarry in Tolima, Colombia. It is the MVP of my Software Analysis and Development technology program (SENA), built with AI-assisted development (Claude).

**Modules:** daily mine production, inventory, customers, sales, CRM, online store with cart and Stripe payments, mining and environmental regulations repository, continuous improvement (PDCA), dashboard with charts, role-based access control and database backups.

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 6, Django REST Framework, JWT authentication (SimpleJWT) |
| API docs | OpenAPI 3 with drf-spectacular (Swagger at `/api/docs/`) |
| Frontend | React 19, React Router 7, Recharts, Vite |
| Data | SQLite (PostgreSQL-ready), Excel and PDF exports (openpyxl, ReportLab) |
| Payments | Stripe Checkout with signed webhooks (simulated mode without keys) |
| Quality | 112 backend tests (Django unittest) and 16 frontend tests (Vitest), Ruff and Oxlint |
| Workflow | Git feature branches and pull requests |

**Quick start:** `pip install -r requirements.txt` → `python manage.py migrate` → `python manage.py cargar_demo --clave "Demo*Mina2026"` → `python manage.py runserver`; then `cd frontend && npm install && npm run dev`.

Screenshots: [`docs/capturas/`](docs/capturas/) · Full documentation (Spanish): [`docs/`](docs/README.md)

---


Sistema de gestión de **Mining Star Services and Products** (Ortega Espinosa y
Cía. S.A.S.), cantera de mármol y caliza en Payandé, San Luis (Tolima).
Producto mínimo viable del Tecnólogo en Análisis y Desarrollo de Software — SENA.

Módulos: producción de la mina, inventario, clientes, ventas, **CRM**, **tienda con
carrito y pagos Stripe**, **repositorio normativo minero y ambiental**, **mejora
continua (PHVA)**, **dashboard con gráficas**, **seguridad por cargo con token de
acceso** y **respaldos**.

Construido con **Django 6 + Django REST Framework** (API) y **React 19 + Vite** (interfaz).

📘 **Documentación completa en [`docs/`](docs/README.md)** · 🎤 **[Guía de presentación](docs/00-guia-presentacion.md)**

---

## Requisitos

- Python 3.12 o superior
- pip

## Instalación

```bash
# 1. Clonar o abrir la carpeta del proyecto
cd "Mining Star"

# 2. Crear el entorno virtual
python -m venv .venv

# 3. Activarlo
.venv\Scripts\activate        # Windows (PowerShell o CMD)
source .venv/bin/activate     # Linux / macOS / WSL

# 4. Instalar las dependencias
pip install -r requirements.txt        # solo ejecucion
pip install -r requirements-dev.txt    # ejecucion + herramientas de calidad (ruff)

# 5. Crear el archivo de configuración local
copy .env.example .env        # Windows
cp .env.example .env          # Linux / macOS

# 6. Generar una clave secreta y pegarla en .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 7. Aplicar las migraciones
python manage.py migrate

# 8. Crear el usuario administrador
python manage.py createsuperuser

# 9. Levantar el servidor
python manage.py runserver
```

La aplicación queda en <http://127.0.0.1:8000/>
y el panel de administración en <http://127.0.0.1:8000/admin/>

---

## Datos de demostración y front-end

```bash
python manage.py cargar_demo --clave "Demo*Mina2026"   # 7 usuarios, uno por cargo
cd frontend && npm install && npm run dev               # http://localhost:5173
```

En Windows también: `scripts\preparar_demo.bat`, `scripts\iniciar_backend.bat` y `scripts\iniciar_frontend.bat`.

---

## Variables de entorno

Se definen en `.env`, que **no se sube a Git**. Ver `.env.example`.

| Variable | Para qué sirve |
|---|---|
| `DJANGO_SECRET_KEY` | Clave criptográfica de firmas y sesiones. Única por instalación. |
| `DJANGO_DEBUG` | `True` en desarrollo, `False` siempre en producción. |
| `DJANGO_ALLOWED_HOSTS` | Dominios autorizados, separados por coma. |
| `JWT_ACCESS_MINUTOS` / `JWT_REFRESH_HORAS` | Vida de los tokens de acceso (30 min) y refresco (8 h). |
| `LOGIN_INTENTOS_MAXIMOS` | Intentos fallidos antes del bloqueo (5). |
| `STRIPE_SECRET_KEY` | Llave de prueba `sk_test_…`. Vacía = pago simulado. |
| `STRIPE_WEBHOOK_SECRET` | Firma del webhook de Stripe (opcional). |

---

## Estructura

```
Mining Star/
├── config/                 Configuración del proyecto Django
│   ├── settings.py         Lee los secretos desde .env
│   └── urls.py
├── core/                   Aplicación principal
│   ├── models.py           Cliente, Proveedor, Producto, Empleado, Venta, DetalleVenta
│   ├── forms.py            Validación de todos los datos de entrada
│   ├── admin.py            Los 6 modelos registrados en /admin/
│   ├── exportadores.py     Generadores de Excel y PDF reutilizables
│   ├── tests*.py           112 pruebas automatizadas
│   └── views/              Un módulo por dominio
│       ├── autenticacion.py
│       ├── panel.py
│       ├── clientes.py
│       ├── proveedores.py
│       ├── productos.py
│       ├── empleados.py
│       └── ventas.py
├── templates/
│   ├── base.html           Plantilla madre; las demás heredan de ella
│   └── _mensajes.html      Bloque de mensajes reutilizable
└── static/                 CSS, JavaScript e imágenes
```

---

## Comandos útiles

```bash
python manage.py test core             # Ejecutar las 112 pruebas del backend
python manage.py respaldar_bd          # Copia de seguridad de la base de datos
python manage.py check                 # Revisión de configuración
python manage.py check --deploy        # Revisión previa a producción
python manage.py makemigrations        # Generar migraciones tras cambiar modelos
python manage.py migrate               # Aplicarlas

ruff check .                           # Detectar problemas de estilo y errores
ruff format .                          # Formatear el código
```

---

## Antes de desplegar a producción

1. `DJANGO_DEBUG=False` en el `.env` del servidor.
2. `DJANGO_SECRET_KEY` **distinta** a la de desarrollo.
3. `DJANGO_ALLOWED_HOSTS` con el dominio real.
4. `python manage.py collectstatic`.
5. Cambiar SQLite por PostgreSQL si va a haber varios usuarios simultáneos.
6. Servir siempre por HTTPS.
